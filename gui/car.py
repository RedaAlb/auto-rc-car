import threading
from queue import Queue, Empty

import cv2
import numpy as np

import math
import time


class Car:
    def __init__(self):
        self.steering = Queue()  # Will be used to communicate with the other threads. -1 for idle, 1 forward, 2 left, 3 right.
        self.steering.put(-1)

        self.mapping_thread = threading.Thread(target=self.mapping_thread, name="mapping_thread", args=((self.steering,)))
        self.mapping_thread.start()

    # Used to map the rc car steering virtually and map the road.
    def mapping_thread(self, steering):

        image = cv2.imread("gui/bg.png")
        pos = (100, 100)  # Position of the virtual car (vc).
        angle = 0
        width = 100
        height = 100

        speed = 0.3  # Forward speed of the vc.
        left_turning_speed = 20  # How fast the vc turns.
        right_turning_speed = 20


        # Used to time how long one full revolution(spin) the vc takes. This time needs to match with the real rc car.
        # Use left_turning_speed and right_turning_speed to experiment with different timings.
        GET_REV_TIME = False  # Turn this on when required to get the time for one revolution of the vc.
        revolution_started = False
        revolution_ended = False

        if GET_REV_TIME:
            print("Road/Car Mapping - Press and hold either left or right arrow until one full revolution is completed, the time will be printed when done.")

        while True:

            # Getting the steering direction from the main thread which is changed when a key is pressed in gui.py
            try: steering_dir = steering.get(timeout=0)
            except Empty: pass

            if steering_dir == -2: break  # To close the thread.

            elif steering_dir == 2:  # left
                angle += np.radians(left_turning_speed)
            elif steering_dir == 3:  # right
                angle -= np.radians(right_turning_speed)
            elif steering_dir == 1:  # forward
                new_x = pos[0] + (speed*np.cos(-np.radians(angle)))
                new_y = pos[1] + (speed*np.sin(-np.radians(angle)))
                pos = (new_x, new_y)


            # Drawing a small circle for every position the vc has been to represent the trail of the vc.
            image = cv2.circle(image, (int(pos[0]), int(pos[1])), radius=1, color=(0, 0, 255), thickness=-1)


            image2 = image.copy()  # So previous vc positions are not present in conesutive images/frames, like "clearing the window".

            # Drawing the square to represent the vc.
            # First rotating each point to the correct orientation.
            c, s = np.cos(np.radians(angle)), np.sin(np.radians(angle))
            rot_matrix = np.matrix("{} {}; {} {}".format(c, -s, s, c))

            p1 = [ + width / 2,  + height / 2]
            p2 = [ - width / 2,  + height / 2]
            p3 = [ - width / 2,  - height / 2]
            p4 = [ + width / 2,  - height / 2]
            p1_new = (np.dot(p1, rot_matrix) + pos).astype(int)
            p2_new = (np.dot(p2, rot_matrix) + pos).astype(int)
            p3_new = (np.dot(p3, rot_matrix) + pos).astype(int)
            p4_new = (np.dot(p4, rot_matrix) + pos).astype(int)

            # Drawing the lines to make up the square (vc).
            img = cv2.line(image2, (p1_new[0, 0], p1_new[0, 1]), (p2_new[0, 0], p2_new[0, 1]), (255, 0, 0), 1)
            img = cv2.line(img, (p2_new[0, 0], p2_new[0, 1]), (p3_new[0, 0], p3_new[0, 1]), (255, 0, 0), 1)
            img = cv2.line(img, (p3_new[0, 0], p3_new[0, 1]), (p4_new[0, 0], p4_new[0, 1]), (255, 0, 0), 1)
            img = cv2.line(img, (p4_new[0, 0], p4_new[0, 1]), (p1_new[0, 0], p1_new[0, 1]), (0, 255, 0), 1)
            img = cv2.line(img, (p2_new[0, 0], p2_new[0, 1]), (p4_new[0, 0], p4_new[0, 1]), (255, 0, 0), 1)
            img = cv2.line(img, (p1_new[0, 0], p1_new[0, 1]), (p3_new[0, 0], p3_new[0, 1]), (255, 0, 0), 1)

            if GET_REV_TIME:
                if (angle < 0 or angle > 0) and not revolution_started:
                    start_time = int(time.time() * 1000)
                    revolution_started = True
                if (angle < -360 or angle > 360) and not revolution_ended:
                    end_time = int(time.time() * 1000)
                    print("Time taken:", end_time - start_time)
                    revolution_ended = True
                    break

            cv2.imshow("Car and road mapping", image2)
            cv2.waitKey(1)