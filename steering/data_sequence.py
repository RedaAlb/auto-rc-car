import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

import cv2
import numpy as np
from sklearn.utils import shuffle
import shutil
import random




# Data sequence class for data loading, processing, and to manage custom batches.
class DataSequence(tf.keras.utils.Sequence):

    def __init__(self, img_shape, batch_size, num_classes, use_data_aug, seed_num):
        self.img_shape = img_shape
        self.batch_size = batch_size
        self.num_classes = num_classes
        self.use_data_aug = use_data_aug
        self.seed_num = seed_num

        tf.random.set_seed(seed_num)
        np.random.seed(seed_num)
        random.seed(seed_num)
        
    def load_data(self, path_to_data_dir, model_to_load):
        with open(f"{path_to_data_dir}/steering_frames_{model_to_load}.npy", "rb") as file:
            self.all_x_data = np.load(file).astype(np.float32)
        with open(f"{path_to_data_dir}/steering_labels_{model_to_load}.npy", "rb") as file:
            self.all_y_data = np.load(file)
            
        self.n_samples = self.all_y_data.shape[0]
        print("Loaded data shape:", self.all_x_data.shape)
        
    def pre_process_data(self, height_crop, use_square_img):

        self.all_x_data = self.all_x_data[:, height_crop:, :, :]

        if use_square_img:
            resized_imgs = []
            for i in range(self.all_x_data.shape[0]):
                img = self.all_x_data[i]
                resized_img = cv2.resize(img, dsize=(img.shape[0], img.shape[0]))
                resized_imgs.append(resized_img)

            resized_imgs = np.array(resized_imgs)
            self.all_x_data = resized_imgs
            del resized_imgs
        
        self.all_x_data /= 255
        
        self.all_y_data -= 1  # This is needed because the collected data is using classes 1,2,3, but needs to be 0,1,2.
        self.all_y_data = tf.one_hot(self.all_y_data, self.num_classes).numpy()
    
    # Split dataset into seperate arrays, one for each class, to get full control over the data, hence each batch.
    def split_into_classes(self):
        # These three variables will hold all samples for each of the classes (forward, left and right).
        self.forward_x = []
        self.left_x = []
        self.right_x = []
        
        for i, img in enumerate(self.all_x_data):
            label = self.all_y_data[i]
            
            if (label==np.array([1, 0, 0])).all(): self.forward_x.append(img)
            elif (label==np.array([0, 1, 0])).all(): self.left_x.append(img)
            elif (label==np.array([0, 0, 1])).all(): self.right_x.append(img)
                
        del self.all_x_data  # No longer needed, delete from memory.
        
        self.forward_x = np.array(self.forward_x)
        self.left_x = np.array(self.left_x)
        self.right_x = np.array(self.right_x)
        
        np.random.shuffle(self.forward_x)
        np.random.shuffle(self.left_x)
        np.random.shuffle(self.right_x)
        
        print("\nForward samples:", self.forward_x.shape, "with a ratio of",
              round(self.forward_x.shape[0]/self.n_samples, 2), "in the dataset")
        print("Left samples:   ", self.left_x.shape, " with a ratio of",
              round(self.left_x.shape[0]/self.n_samples, 2), "in the dataset")
        print("Right samples:  ", self.right_x.shape, "with a ratio of",
              round(self.right_x.shape[0]/self.n_samples, 2), "in the dataset", "\n")
        
    
    # Splits the whole data set into val and test sets with the same ratios for each class as set above.
    def split_val_test(self, val_ratio, test_ratio, f_ratio, l_ratio, r_ratio):
        val_n = int(self.n_samples * val_ratio)
        test_n = int(self.n_samples * test_ratio)

        self.f_ratio = f_ratio
        self.l_ratio = l_ratio
        self.r_ratio = r_ratio
        
        # Validation set
        val_f_n_samples = int(val_n * self.f_ratio)  # Validation forward class number of samples.
        val_l_n_samples = int(val_n * self.l_ratio)
        val_r_n_samples = int(val_n * self.r_ratio)
        
        self.x_val = self.forward_x[:val_f_n_samples]  # Slicing works because the arrays have already been shuffled.
        # Deleting them so they don't remain for training or test set.
        self.forward_x = np.delete(self.forward_x, slice(val_f_n_samples), axis=0)

        self.x_val = np.vstack((self.x_val, self.left_x[:val_l_n_samples]))
        self.left_x = np.delete(self.left_x, slice(val_l_n_samples), axis=0)
        
        self.x_val = np.vstack((self.x_val, self.right_x[:val_r_n_samples]))
        self.right_x = np.delete(self.right_x, slice(val_r_n_samples), axis=0)
        
        # Creating the labels for the validatin set.
        self.y_val = np.array([0]*val_f_n_samples + [1]*val_l_n_samples + [2]*val_r_n_samples)
        self.y_val = tf.one_hot(self.y_val, self.num_classes).numpy()
        
        self.x_val, self.y_val = shuffle(self.x_val, self.y_val)
        print("Validation set:", self.x_val.shape, self.y_val.shape)
        
        
        # Test set
        test_f_n_samples = int(test_n * self.f_ratio)
        test_l_n_samples = int(test_n * self.l_ratio)
        test_r_n_samples = int(test_n * self.r_ratio)

        self.x_test = self.forward_x[:test_f_n_samples]
        self.forward_x = np.delete(self.forward_x, slice(test_f_n_samples), axis=0)

        self.x_test = np.vstack((self.x_test, self.left_x[:test_l_n_samples]))
        self.left_x = np.delete(self.left_x, slice(test_l_n_samples), axis=0)

        self.x_test = np.vstack((self.x_test, self.right_x[:test_r_n_samples]))
        self.right_x = np.delete(self.right_x, slice(test_r_n_samples), axis=0)

        self.y_test = np.array([0]*test_f_n_samples + [1]*test_l_n_samples + [2]*test_r_n_samples)
        self.y_test = tf.one_hot(self.y_test, self.num_classes).numpy()

        self.x_test, self.y_test = shuffle(self.x_test, self.y_test)
        print("Test set:", self.x_test.shape, self.y_test.shape)
        
        print("\nTraining set (what is left):")
        print("Forward samples:", self.forward_x.shape)
        print("Left samples:   ", self.left_x.shape)
        print("Right samples:  ", self.right_x.shape)
        
        self.train_n_samples = self.forward_x.shape[0] + self.left_x.shape[0] + self.right_x.shape[0]
        print("Total training samples:", self.train_n_samples)
        
    def get_batch(self, batch_size):
        # Returns (x_batch, y_batch) where x_batch is made up of samples with same ratios as set above.
        
        f_n_samples = int(batch_size * self.f_ratio)  # Number of samples for the forward class in the batch.
        l_n_samples = int(batch_size * self.l_ratio)
        r_n_samples = int(batch_size * self.r_ratio)
        
        # Getting random indicies for each class and adding the samples to the batch.
        rand_indices = np.random.choice(self.forward_x.shape[0], f_n_samples, replace=False)
        x_batch = self.forward_x[rand_indices]
        
        rand_indices = np.random.choice(self.left_x.shape[0], l_n_samples, replace=False)
        x_batch = np.vstack((x_batch, self.left_x[rand_indices]))
        
        rand_indices = np.random.choice(self.right_x.shape[0], r_n_samples, replace=False)
        x_batch = np.vstack((x_batch, self.right_x[rand_indices]))
        
        # This is to ensure that a full batch is returned (because using ratios might not give full numbers).
        # Remaining samples to fill/complete a batch, forward samples are used for fillers.
        rem_samples = batch_size - (f_n_samples + l_n_samples + r_n_samples)
        if rem_samples != 0:  # If filling is needed to complete the batch.
            rand_indices = np.random.choice(self.forward_x.shape[0], rem_samples, replace=False)
            x_batch = np.vstack((x_batch, self.forward_x[rand_indices]))
        
        # Creating the labels for the batch
        y_batch = np.array([0]*f_n_samples + [1]*l_n_samples + [2]*r_n_samples + [0]*rem_samples)
        y_batch = tf.one_hot(y_batch, self.num_classes).numpy()
        
        x_batch, y_batch = shuffle(x_batch, y_batch)
        
        return (x_batch, y_batch)
    
    
    # Creating the generator for data augmentation.
    def create_aug_gen(self, rot_range, bright_min, bright_max, hori_flip):
        # Note that I am using the original data and data augmented data, because this works best for this
        # behavioral cloning task.
        self.datagen = tf.keras.preprocessing.image.ImageDataGenerator(
            rescale=1./255,
            rotation_range=rot_range,
            brightness_range=(bright_min, bright_max),
            horizontal_flip=hori_flip
        )

        # self.datagen.fit(self.x_train)  # Double check if I need this or not.
        
    def __len__(self):
        return self.train_n_samples // self.batch_size
    
    def __getitem__(self, idx):
        
        # Orginal data batch half.
        first_batch_half = self.get_batch(self.batch_size // 2)  # Half batch size because half org and half augmented.
        
        # Getting the other half from the augmentation generator.
        second_batch_half = self.get_batch(self.batch_size // 2)
        if self.use_data_aug:
            datagen_flow = self.datagen.flow(second_batch_half[0], second_batch_half[1], batch_size=self.batch_size // 2)
            second_batch_half = datagen_flow.next()
            
        x_batch = np.vstack((first_batch_half[0], second_batch_half[0]))
        y_batch = np.vstack((first_batch_half[1], second_batch_half[1]))
        
        # print(x_batch, y_batch)
        return (x_batch, y_batch)