import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

from tensorflow.keras import layers

import numpy as np
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
import random
import shutil

from data_sequence import DataSequence


# Some parameters
MODELS = ["forward", "left", "right"]  # Also represents the class names.
MODEL_I = 0  # Model index, determines which module to train, hence which data to use, (chosen from MODELS).

# The folder where the data is stored. This is here to easily switch between local and Google Colab env.
PATH_TO_DATA_DIR = "data"
# PATH_TO_DATA_DIR = "drive/My Drive/Auto_RC_Car/data"  # For when using Google Colab.


VALIDATION_SPLIT = 0.1
TEST_SPLIT = 0  # Zero for no test set.

USE_DATA_AUG = True

HEIGHT_CROP = 95  # How many pixels to crop from the top.
USE_SQUARE_IMG = True  # Whether to re-size the image to a square image.
IMGS_SHAPE = (240-HEIGHT_CROP, 320, 3)  # Image dims to use for training.

if USE_SQUARE_IMG:
    IMGS_SHAPE = (IMGS_SHAPE[0], IMGS_SHAPE[0], 3)

BATCH_SIZE = 256  # Needs to be even, because half will be original data, half augmented data.

NUM_CLASSES = 3

# Ratios of classes in each batch. I do this because there are significantly more forward samples (stayin in lane).
FORWARD_RATIO = 0.5
LEFT_RATIO    = 0.25
RIGHT_RATIO   = 0.25

# Data augmentation parameters
ROT_RANGE = 2
BRIGHT_MIN = 0.2
BRIGHT_MAX = 1.5
HORI_FLIP = True

SEED_NUM = 2

# General setup
tf.random.set_seed(SEED_NUM)
np.random.seed(SEED_NUM)
random.seed(SEED_NUM)




data_seq = DataSequence(IMGS_SHAPE, BATCH_SIZE, NUM_CLASSES, USE_DATA_AUG, SEED_NUM)

data_seq.load_data(path_to_data_dir=PATH_TO_DATA_DIR, model_to_load=MODELS[MODEL_I])
data_seq.pre_process_data(HEIGHT_CROP, USE_SQUARE_IMG)
data_seq.split_into_classes()
data_seq.split_val_test(VALIDATION_SPLIT, TEST_SPLIT, FORWARD_RATIO, LEFT_RATIO, RIGHT_RATIO)
data_seq.create_aug_gen(ROT_RANGE, BRIGHT_MIN, BRIGHT_MAX, HORI_FLIP)




# Creating the model

inputs = tf.keras.Input(shape=IMGS_SHAPE)

x = layers.Conv2D(24, 5, strides=2, activation="elu")(inputs)
x = layers.MaxPooling2D(2)(x)

x = layers.Conv2D(36, 5, activation="elu")(x)
x = layers.MaxPooling2D(2, padding="same")(x)

x = layers.Conv2D(48, 5, padding="same", activation="elu")(x)
x = layers.MaxPooling2D(2)(x)

x = layers.Conv2D(64, 3, padding="same", activation="elu")(x)
# x = layers.Conv2D(64, 3, activation="elu")(x)

x = layers.Flatten()(x)

x = layers.Dense(1024, activation="elu")(x)
# x = layers.Dense(1024, activation="elu")(x)

outputs = layers.Dense(3, activation="softmax")(x)


optimizer = tf.keras.optimizers.Adam(lr=1e-3)

model = tf.keras.Model(inputs=inputs, outputs=outputs)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=["accuracy"])
model.summary()


# Training the model.
EPOCHS = 30
MODEL_NAME = "br_org_paddingSame_resized_cropped_largeFNN"
SAVE_MODEL = True

try:
    shutil.rmtree("logs")
except FileNotFoundError as err:
    pass

callbacks = [
    tf.keras.callbacks.TensorBoard(log_dir='./logs')
]
# command to view -> tensorboard --logdir=./logs  


history = model.fit(data_seq,
                    steps_per_epoch = data_seq.train_n_samples // BATCH_SIZE,
                    validation_data = (data_seq.x_val, data_seq.y_val),
                    validation_steps = data_seq.x_val.shape[0] // BATCH_SIZE,
                    epochs = EPOCHS,
                    callbacks=callbacks,
                    shuffle=False)



# Saving the trained model and its history.
if SAVE_MODEL:
    model.save(f"saved_models/model_{MODELS[MODEL_I]}_{MODEL_NAME}.h5")
    
    history_array = np.array([history.history["loss"],
                              history.history["accuracy"],
                              history.history["val_loss"],
                              history.history["val_accuracy"]])
    with open(f"saved_models/history_{MODELS[MODEL_I]}_{MODEL_NAME}.npy", "wb") as file:
        np.save(file, history_array)