from tensorflow.keras.models import load_model
import pandas as pd
import cv2
import numpy as np

import threading
from queue import Queue

from sign_detection.circle_detector import CircleDetector


class SignDetector:

    model = load_model("sign_detection/trained_sign_recognition_model.h5")
    labels = pd.read_csv("sign_detection/sign_names.csv")


    def __init__(self, detect_signs, display_sign_detected, display_trackbars):
        self.detect_signs = detect_signs
        self.display_sign_detected = display_sign_detected
        self.display_trackbars = display_trackbars

        # These variables will hold the information for the most current detected sign, to be accessed by the main thread in main.py.
        self.class_index = -1
        self.sign_name = ""
        self.sign_dist = -1

        # This will store the previously detected sign name, since a sign needs to be detected twice in two consecutive frames.
        self.prev_sign_name = ""

        # This queue is used to communicate between the main thread (main.py) and the sign detection thread below.
        self.frame_queue = Queue(maxsize=1)  # maxsize=1 to ensure only one frame and is the latest frame is in the queue.

        # Keeping the sign detector in a seperate thread to not make it a bottleneck in the camera network connection.
        if detect_signs:
            self.sign_detector_thread = threading.Thread(target=self.sign_detector_thread, name="sign_detector_thread", args=((self.frame_queue,)))
            self.sign_detector_thread.start()

    def sign_detector_thread(self, frame_queue):

        circle_detector = CircleDetector(self.display_trackbars)

        while self.detect_signs:
            frame = frame_queue.get(-1)

            try:
                if frame == 0: break  # Signal to shutdown the thread.
            except ValueError as err:  # For when an actual frame is received which you cannot compare to zero.
                pass

            if frame is not None and self.detect_signs:
                all_circles = circle_detector.find_circles(frame)
                self.class_index, self.sign_name, self.sign_dist = self.make_prediction(frame, all_circles, self.display_sign_detected)


    # Preprocessing for the input to the model.
    def preprocessing(self, img):
        img = np.asarray(img)
        img = cv2.resize(img, (32, 32))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.equalizeHist(img)
        
        img = img / 255

        img = img.reshape(1, 32, 32, 1)
        
        return img

    # Getting all circle patches detected and passing them into the model for classification.
    def make_prediction(self, frame, all_circles, display_sign_info):

        if all_circles is not None:  # If circle(s) were detected.
            for circle in all_circles:
                # Getting the top left corner and bottom right corner coordinates of the rectangle that the circle is in (sign patch/bounding box).
                top_l_corner, bottom_r_corner = circle.get_rect_coords()

                # Cutting/cropping out the sign as a rectangle/patch to feed into the model for classification.
                sign_patch = frame[top_l_corner[1]:bottom_r_corner[1], top_l_corner[0]:bottom_r_corner[0]]

                try:  # For when one of the corner coordinates is out of bound of the frame (when sign is at the very edge).
                    sign_patch = self.preprocessing(sign_patch)
                except:
                    break

                # Making a prediction using the trained sign detection model.
                class_index = self.model.predict_classes(sign_patch)[0]
                sign_name = self.labels.iloc[class_index][1]
                sign_dist = circle.get_dist_to_edge(frame.shape[1])

                if sign_name != self.prev_sign_name:
                    self.prev_sign_name = sign_name
                    break

                if display_sign_info:
                    # Displaying the sign bounding box, distance to edge, and the sign name on the frame.
                    frame = circle.draw_sign_info(frame, top_l_corner, bottom_r_corner, sign_dist, sign_name)

                cv2.imshow("RC Car camera feed", frame)
                cv2.waitKey(1)

                # Here I am simply returning the first detected circle to not slow down, since making multiple predictions would require significantly more time.
                # Only one sign is required to be detected at once. However, this can be easily expanded later if multiple signs needs to be detected at once.
                return class_index, sign_name, sign_dist
        else:
            self.prev_sign_name = ""   # Resetting the previously detected sign to no sign.

        # The waitKey(1) is so if the trackbars window were to be displayed, it does crash, and you are still able
        # to use the trackbars even if no circles were detected to "fine-tune" the values.
        cv2.waitKey(1)
        return -1, "", -1
    
    def get_sign_direction(self):
        if   self.sign_name == "Ahead only": return 1         # Forward
        elif self.sign_name == "Turn left ahead": return 2    # Left
        elif self.sign_name == "Turn right ahead": return 3   # Right




