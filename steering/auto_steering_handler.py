import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)
from tensorflow.keras.models import load_model

import numpy as np

from steering.data_sequence import DataSequence  # steering. is needed since this class is used from main.py.

class AutoSteeringHandler:

    def __init__(self, obstacle_distance, tl_stop_distance):
        self.obstacle_distance = obstacle_distance
        self.tl_stop_distance = tl_stop_distance
        self.is_green_light = True  # Keeps track of the last detected traffic light colour, 1(red), 2(green).

        self.data_seq = DataSequence()


    def load_models(self, f_model_name, l_model_name, r_model_name):
        self.f_model = load_model(f"steering/saved_models/model_f_{f_model_name}.h5")
        self.l_model = load_model(f"steering/saved_models/model_l_{l_model_name}.h5")
        self.r_model = load_model(f"steering/saved_models/model_r_{r_model_name}.h5")

    

    def predict_steering(self, frame, auto_direction, sensor_distance, detected_light, tl_dist_to_edge):

        # If an obstacle is in front of the car, ignore everything else and stop the car.
        if sensor_distance <= self.obstacle_distance:
            return -1

        # If a red light is detected and is close to the edge, then also stop the car.
        if detected_light == 1 and tl_dist_to_edge <= self.tl_stop_distance:
            self.is_green_light = False

        # Checking if green light is detected, the +20 is to allow for larger green light detection area.
        elif detected_light == 2 and tl_dist_to_edge <= self.tl_stop_distance + 20:
            self.is_green_light = True

        if not self.is_green_light:
            return -1
            

        # I arbitrary chose the forward model for the pre-processing checks because all three models will have the same input.
        processed_input = self.data_seq.pre_process_input(frame, self.f_model.inputs)

        steering_pred = -2  # Just in case auto_direction is set to something unexpected.

        if auto_direction == 1:    # forward
            prediction = self.f_model.predict(processed_input)
            steering_pred = np.argmax(prediction[0])
        elif auto_direction == 2:  # left
            prediction = self.l_model.predict(processed_input)
            steering_pred = np.argmax(prediction[0])
        elif auto_direction == 3:  # right
            prediction = self.r_model.predict(processed_input)
            steering_pred = np.argmax(prediction[0])

        return steering_pred + 1  # +1 needed since the prediction is 0,1,2 for forward,left,right respectively, but 1,2,3 required.

