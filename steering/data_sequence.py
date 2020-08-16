import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

import cv2
import numpy as np
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import random




# Data sequence class for data loading, processing, and to manage custom batches.
class DataSequence(tf.keras.utils.Sequence):

    def __init__(self, batch_size=32, num_classes=3, use_data_aug=0, seed_num=0, use_custom_batches=0):
        self.batch_size = batch_size
        self.num_classes = num_classes
        self.use_data_aug = use_data_aug
        self.seed_num = seed_num
        self.use_custom_batches = use_custom_batches

        tf.random.set_seed(seed_num)
        np.random.seed(seed_num)
        random.seed(seed_num)


    def load_data(self, path_to_data_dir, model_to_load):
        print("Loading data...")
        with open(f"{path_to_data_dir}/steering_frames_{model_to_load}.npy", "rb") as file:
            self.all_x_data = np.load(file).astype(np.float32)
        with open(f"{path_to_data_dir}/steering_labels_{model_to_load}.npy", "rb") as file:
            self.all_y_data = np.load(file)

        print("Labels:", self.all_y_data)
            
        self.n_samples = self.all_y_data.shape[0]   
        print("Loaded data shape:", self.all_x_data.shape)



    # For pre-processing training data. x_data and y_data are passed in so this method can be used for predictions
    # as well or anywhere where pre-processing is needed.
    def pre_process_data(self, crop_height=1, height_to_crop=95, resize_img=1, img_shape=(200, 100), use_yuv=1, blur_img=1, x_data=None, y_data=None):

        if x_data is None: x_data = self.all_x_data
        if y_data is None: y_data = self.all_y_data

        if crop_height:
            x_data = x_data[:, height_to_crop:, :, :]

        x_data /= 255

        processed_imgs = []
        for i in range(x_data.shape[0]):
            img = x_data[i]

            if resize_img: img = cv2.resize(img, dsize=img_shape)
            if use_yuv: img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
            if blur_img: img = cv2.GaussianBlur(img, (3, 3), 0)

            processed_imgs.append(img)

        processed_imgs = np.array(processed_imgs)
        x_data = processed_imgs
        del processed_imgs


        y_data -= 1  # This is needed because the collected data is using classes 1,2,3, but needs to be 0,1,2.
        y_data = tf.one_hot(y_data, self.num_classes).numpy()

        self.all_x_data = x_data
        self.all_y_data = y_data

        return x_data, y_data


    # Split dataset into seperate arrays, one for each class, to get full control over the data, hence each batch.
    def split_into_classes(self, remove_f_samples, f_samples_to_remove):
        # These three variables will hold all samples for each of the classes (forward, left and right).
        self.forward_x = []
        self.left_x = []
        self.right_x = []
        
        for i, img in enumerate(self.all_x_data):
            label = self.all_y_data[i]
            
            if (label==np.array([1, 0, 0])).all(): self.forward_x.append(img)
            elif (label==np.array([0, 1, 0])).all(): self.left_x.append(img)
            elif (label==np.array([0, 0, 1])).all(): self.right_x.append(img)
                
        # del self.all_x_data  # No longer needed, delete from memory.
        
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


        # Remove some forward samples, to balance data.
        if remove_f_samples:
            self.forward_x = self.forward_x[f_samples_to_remove:, :, :, :]
            print("Forward samples after removal", self.forward_x.shape)

            self.all_x_data = np.vstack((self.forward_x, self.left_x, self.right_x))

            self.all_y_data = np.array([0]*self.forward_x.shape[0] + [1]*self.left_x.shape[0] + [2]*self.right_x.shape[0])
            self.all_y_data = tf.one_hot(self.all_y_data, self.num_classes).numpy()

            self.n_samples = self.all_x_data.shape[0]

            self.all_x_data, self.all_y_data = shuffle(self.all_x_data, self.all_y_data)

            print("\nForward samples:", self.forward_x.shape, "with a ratio of", 
                  round(self.forward_x.shape[0]/self.n_samples, 2), "in the dataset")
            print("Left samples:   ", self.left_x.shape, " with a ratio of",
                  round(self.left_x.shape[0]/self.n_samples, 2), "in the dataset")
            print("Right samples:  ", self.right_x.shape, "with a ratio of",
                  round(self.right_x.shape[0]/self.n_samples, 2), "in the dataset", "\n")

            print("\nAll samples:", self.all_x_data.shape, self.all_y_data.shape)

            
    # For splitting dataset into train and validation sets, and when using custom batches possibly a test set.
    # For testing, I simply test it on the road physically for a more accurate test.
    def split_val_test(self, val_ratio, test_ratio, f_ratio, l_ratio, r_ratio):
        if not self.use_custom_batches:
            self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(self.all_x_data,
                                                                                  self.all_y_data,
                                                                                  test_size=val_ratio,
                                                                                  random_state=self.seed_num)

            # Deleting from memory as they are not needed anymore.
            del self.all_x_data
            del self.all_y_data

            self.train_n_samples = self.y_train.shape[0]

            print("Training data:   ", self.x_train.shape, self.y_train.shape)
            print("Validation data: ", self.x_val.shape, self.y_val.shape)

        else:  # Splits the whole data set into val and test sets with the same ratios for each class as set above.
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

    # For excracting the road mask to be used as an additional input to the model.
    # The x_data and x_data_val parameters are needed so I can use the same method to excract the road masks for prediction.
    def excract_road_masks(self, x_data=None, x_data_val=None):

        if x_data is None: x_data = self.x_train
        if x_data_val is None: x_data_val = self.x_val

        # These numbers were found by experimenting with different values on specifically challenging frames.
        lowerYUV = np.array([51, 81, 40]) / 255
        upperYUV = np.array([255, 164, 117]) / 255
        
        x_train_masks = []
        x_val_masks = []

        # Excracting the road mask for all frames in both the training and validation sets.
        for i in range(x_data.shape[0]):
            x_train_img = x_data[i]
            x_train_mask = cv2.inRange(x_train_img, lowerYUV, upperYUV)
            x_train_masks.append(x_train_mask)


            if i < x_data_val.shape[0]:
                x_val_img = x_data_val[i]
                x_val_mask = cv2.inRange(x_val_img, lowerYUV, upperYUV)
                x_val_masks.append(x_val_mask)

        self.x_train_masks = np.array(x_train_masks) / 255
        self.x_train_masks = np.expand_dims(self.x_train_masks, axis=3)
        del x_train_masks

        self.x_val_masks = np.array(x_val_masks) / 255
        self.x_val_masks = np.expand_dims(self.x_val_masks, axis=3)
        del x_val_masks

        return self.x_train_masks, self.x_val_masks
    
    # Excracting the road central vertical distance to be use as an additional input to the model.
    def excract_centre_distance(self, x_data=None, x_data_val=None):
        # Excracting the central distance to the end of road for all frames in both the training and validation sets.

        if x_data is None: x_data = self.x_train_masks
        if x_data_val is None: x_data_val = self.x_val_masks

        # Will hold all the distances for all the frames, which are excracted using the masks. Please refer to the paper for
        # exactly what distance this is.
        x_train_dist = []
        x_val_dist = []
        for i in range(x_data.shape[0]):
            x_train_mask = x_data[i]

            mid_x = x_train_mask.shape[1] // 2

            # Vertical slice of the middle column of the mask/frame.
            v_slice = x_train_mask[:, mid_x]

            # Finding the first non-zero value (one) which will be the middle top point of the road.
            road_top_mid = (v_slice!=0).argmax(axis=0)[0]

            # Getting the distance by reversing the distance, to get the distance of the road (height of the road).
            centre_dist = x_train_mask.shape[0] - road_top_mid
            centre_dist = centre_dist / x_train_mask.shape[0]  # Normalising.

            x_train_dist.append(centre_dist)

            # Same for the validation set.
            if i < x_data_val.shape[0]:
                x_val_mask = x_data_val[i]

                mid_x = x_val_mask.shape[1] // 2
                v_slice = x_val_mask[:, mid_x]

                road_top_mid = (v_slice!=0).argmax(axis=0)

                centre_dist = x_val_mask.shape[0] - road_top_mid
                centre_dist = centre_dist / x_val_mask.shape[0]  # Normalising.

                x_val_dist.append(centre_dist)

        
        self.x_train_dist = np.array(x_train_dist)
        del x_train_dist
        
        self.x_val_dist = np.array(x_val_dist)
        del x_val_dist

        return self.x_train_dist, self.x_val_dist
    
    # To process input data for prediction.
    def pre_process_input(self, frame, model_inputs, convert_to_rgb=True):

        frame = np.float32(frame)

        if convert_to_rgb:
            frame = frame[:, :, ::-1]  # Converting to RGB since the frame is coming from opencv which uses BGR.

        frame = np.array([frame])  # Needed to get batch size of 1.
        
        processed_frame, _ = self.pre_process_data(x_data=frame, y_data=np.array([0]))  # Passing in dummy y_data.

        # Checking what type of model it is by checking the number of inputs and constructing the required input.
        # Could be a model with just the frame as input, or frame/mask, or frame/dist, or all three.
        num_inputs = len(model_inputs)

        if num_inputs == 1:  # When only the frame is the input.
            return processed_frame

        elif num_inputs == 2:  # For when there are two inputs.
            # Since the mask has a shape of an image, I can simply check if the length of the shape is 4 or not (None, h, w, channels).
            # Where if the input was a distance, the shape will just be (None, 1), 2 values.
            input2_shape_size = len(model_inputs[1].shape)

            if input2_shape_size == 4:  # When the second input is a mask.
                # Getting the mask for the frame. Same val data is used as it does not matter, not needed for prediction.
                frame_mask, _ = self.excract_road_masks(x_data=processed_frame, x_data_val=processed_frame)
                processed_input = [processed_frame, frame_mask]
                return processed_input

            elif input2_shape_size == 2:  # When the second input is a distance.
                # The mask is needed to excract the distance.
                frame_mask, _ = self.excract_road_masks(x_data=processed_frame, x_data_val=processed_frame)
                frame_dist, _ = self.excract_centre_distance(x_data=frame_mask, x_data_val=frame_mask)

                processed_input = [processed_frame, frame_dist]
                return processed_input

        elif num_inputs == 3:
            frame_mask, _ = self.excract_road_masks(x_data=processed_frame, x_data_val=processed_frame)
            frame_dist, _ = self.excract_centre_distance(x_data=frame_mask, x_data_val=frame_mask)

            processed_input = [processed_frame, frame_mask, frame_dist]

            return processed_input
    

    # This is mainly used when custom batches are used.
    def get_batch(self, batch_size):

        if not self.use_custom_batches:
            return (self.x_train[0:batch_size], self.y_train[0:batch_size])

        else:
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
        self.datagen = tf.keras.preprocessing.image.ImageDataGenerator(
            rescale=1./255,
            fill_mode="constant",
            rotation_range=rot_range,
            brightness_range=(bright_min, bright_max)
            # horizontal_flip=hori_flip
            # zoom_range=0.3,
            # width_shift_range=0.1,
            # height_shift_range=0.1,   
        )

        # self.datagen.fit(self.x_train)  # Double check if I need this or not.
        
    def __len__(self):
        return self.train_n_samples // self.batch_size
    
    # This will be used if custom batches are used, please refer to auto_steering_handler.py for custom batches.
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