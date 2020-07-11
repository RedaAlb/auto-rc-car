import threading
from queue import Queue
import pygame as pg

import numpy as np
import cv2

from servers import controller_server


class ControllerHandler:

    def __init__(self, host_ip, port_controller, run_controller_server):
        self.run_controller_server = run_controller_server

        # Creates and starts a TCP controller server(socket) to control what the motors do on the pi.
        # The server is ran on a thread to keep the connections seperated.
        self.server_controller = controller_server.ControllerServer(host_ip, port_controller)

        # Used to store/share the controller variable in a queue so the motors can be controlled from the main thread.
        self.controller = Queue()  # Can be -1, 0, 1, 2, or 3 -> do nothing, close connection, forward, left, right, signals respectively.
        self.controller.put(-1)

        if run_controller_server:
            self.controller_thread = threading.Thread(target=self.server_controller.start_server, name="controller_thread", args=((self.controller,)))
            self.controller_thread.start()

        self.is_collecting_data = False  # Whether to collect/capture data for training.

        # Used to store the training data if collecting data. TODO: Combine all these 6 variables into 1 big matrix.
        self.frames_forward = []
        self.labels_forward = []  # Steering for the frame, either 1, 2, 3 -> forward, left, or right, respectively.

        self.frames_left, self.labels_left = [], []
        self.frames_right, self.labels_right = [], []

        self.rec_direction = 1  # What direction to record/collect the frames/labels for 1, 2, 3 -> forward, left, right


        # TODO: Take care of all GUI stuff in a GUI class. But do this when I find something to replace pygame with.
        pg.init()
        display = pg.display.set_mode((400, 400))
        display.fill((255, 255, 255))

        font = pg.font.Font(None, 32)
        text = font.render("Focus this window to control car", 1, (100, 100, 100))
        display.blit(text, (20, 20))
        pg.display.update()

    def process_key_pressed(self, frame=None):
        # For controlling the car manually and to collect training data.

        keys = pg.key.get_pressed()

        # This if statement separation/order is done for smooth steering using the keyboard.
        if keys[pg.K_LEFT]:      # steer left
            self.controller.put(2)
            self.add_data_sample(frame, 2)

        elif keys[pg.K_RIGHT]:   # steer right
            self.controller.put(3)
            self.add_data_sample(frame, 3)
            
        elif keys[pg.K_UP]:      # go forward
            self.controller.put(1)
            self.add_data_sample(frame, 1)

        elif keys[pg.K_DOWN]:
            self.controller.put(-1) # stop, do nothing

        for event in pg.event.get():
            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT: self.controller.put(-1)
                elif event.key == pg.K_RIGHT: self.controller.put(-1)
                elif event.key == pg.K_UP: self.controller.put(-1)


                # On key release/key-up so nothing happens twice accidentally.
                if event.key == pg.K_s:  # Save all collected training data.
                    self.save_collected_data()
                    print("Data collection - Training data SAVED")

                elif event.key == pg.K_p:  # Pause/unpause data collection
                    if self.is_collecting_data:
                        self.is_collecting_data = False
                        print("Data collection - Collection PAUSED")
                    else:
                        self.is_collecting_data = True
                        print("Data collection - Collection STARTED")
                
                elif event.key == pg.K_c: self.controller.put(0)  # close controller connection
    
                elif event.key == pg.K_r:
                    self.reset_collected_data()
                    print("Data collection - Collected data RESET")
                
                elif event.key == pg.K_1:
                    self.rec_direction = 1
                    print("Data collection - Recording for forward(1) steering")
                elif event.key == pg.K_2:
                    self.rec_direction = 2
                    print("Data collection - Recording for left(2) steering")
                elif event.key == pg.K_3:
                    self.rec_direction = 3
                    print("Data collection - Recording for right(3) steering")

                elif event.key == pg.K_i:
                    self.print_collection_info()


    def add_data_sample(self, frame, steering_dir):
        if self.is_collecting_data and frame is not None:
            if self.rec_direction == 1:
                self.frames_forward.append(frame)
                self.labels_forward.append(steering_dir)
                print(f"Data collection - forward(1) mode, added \"{steering_dir}\" sample {len(self.labels_forward)}")
            elif self.rec_direction == 2:
                self.frames_left.append(frame)
                self.labels_left.append(steering_dir)
                print(f"Data collection - left(2) mode, added \"{steering_dir}\" sample {len(self.labels_left)}")
            elif self.rec_direction == 3:
                self.frames_right.append(frame)
                self.labels_right.append(steering_dir)
                print(f"Data collection - right(3) mode, added \"{steering_dir}\" sample {len(self.labels_right)}")

    def save_collected_data(self):
        self.is_collecting_data = False
        print("Data collection - Collection STOPPED")

        # Converting to numpy arrays.
        frames_forward_arr, labels_forward_arr  = np.array(self.frames_forward), np.array(self.labels_forward)
        frames_left_arr, labels_left_arr  = np.array(self.frames_left), np.array(self.labels_left)
        frames_right_arr, labels_right_arr  = np.array(self.frames_right), np.array(self.labels_right)

        # Saving the numpy arrays/data
        with open("steering/data/steering_frames_forward.npy", "wb") as file: np.save(file, frames_forward_arr)
        with open("steering/data/steering_frames_left.npy", "wb") as file: np.save(file, frames_left_arr)
        with open("steering/data/steering_frames_right.npy", "wb") as file: np.save(file, frames_right_arr)

        with open("steering/data/steering_labels_forward.npy", "wb") as file: np.save(file, labels_forward_arr)
        with open("steering/data/steering_labels_left.npy", "wb") as file: np.save(file, labels_left_arr)
        with open("steering/data/steering_labels_right.npy", "wb") as file: np.save(file, labels_right_arr)

        
    def reset_collected_data(self):
        self.frames_forward, self.frames_left, self.frames_right = [], [], []
        self.labels_forward, self.labels_left, self.labels_right = [], [], []


    def display_recording(self, frame):
        img_w = frame.shape[1]
        text = "R" + str(self.rec_direction)
        frame = cv2.putText(frame, text, (img_w - 50, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), thickness=3)
        return frame

    
    def print_collection_info(self):

        n_forward = len(self.frames_forward)
        n_left = len(self.frames_left)
        n_right = len(self.frames_right)

        print("\n--------------Data collection info--------------")
        print("Recording is:", self.is_collecting_data)
        print("Current recording direction/mode:", self.rec_direction)
        print("For forward mode,", n_forward, " samples captured so far.")
        print("For left    mode,", n_left, " samples captured so far.")
        print("For right   mode,", n_right, " samples captured so far.")
        print("Total samples captured:", (n_forward + n_left + n_right))
        print("------------------------------------------------\n")