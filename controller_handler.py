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

        self.collect_data = False

        # Used to store the training data if collecting data.
        self.frames = []
        self.labels = []  # Steering for the frame, either 1, 2, 3 -> forward, left, or right, respectively.


        # TODO: Take care of all GUI stuff in a GUI class. But do this when I find something to replace pygame with.
        pg.init()
        display = pg.display.set_mode((400, 400))
        display.fill((255, 255, 255))

        font = pg.font.Font(None, 32)
        text = font.render("Focus this window to control car", 1, (100, 100, 100))
        display.blit(text, (20, 20))



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


                # On key release so it does not save twice accidentally.
                if event.key == pg.K_s:  # Save all collected training data.
                    self.save_collected_data()
                    print("Data collection - Training data SAVED")

                if event.key == pg.K_p:  # Pause/unpause data collection
                    if self.collect_data:
                        self.collect_data = False
                        print("Data collection - Collection PAUSED")
                    else:
                        self.collect_data = True
                        print("Data collection - Collection STARTED")
                
                if event.key == pg.K_c:
                    self.controller.put(0)  # close connection

                if event.key == pg.K_r:
                    self.frames = []
                    self.labels = []
                    print("Data collection - Collected data RESET")

        pg.display.update()



    def add_data_sample(self, frame, steering_dir):
        if self.collect_data and frame is not None:
            self.frames.append(frame)
            self.labels.append(steering_dir)

            print(len(self.labels))


    def save_collected_data(self):
        self.collect_data = False
        print("Data collection - Collection STOPPED")

        frames_array = np.array(self.frames)
        labels_array = np.array(self.labels)

        with open("steering/data/steering_frames.npy", "wb") as file:
            np.save(file, frames_array)
        
        with open("steering/data/steering_labels.npy", "wb") as file:
            np.save(file, labels_array)

    def display_recording(self, frame):
        img_w = frame.shape[1]
        frame = cv2.putText(frame, "R", (img_w - 30, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), thickness=3)
        return frame