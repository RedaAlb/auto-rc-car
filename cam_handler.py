import time

import numpy as np
import cv2

from servers import cam_server


class CamHandler:

    def __init__(self, host_ip, port_cam, cam_print_logs):

        self.cam_print_logs = cam_print_logs

        # Creates and starts a UDP camera server(socket) to receive from the Raspberry Pi.
        self.server_cam = cam_server.CameraServer(host_ip, port_cam, cam_print_logs)
        self.server_cam.start_server()

        # Variables needed to calculate the FPS achieved on the computer.
        self.start_time = time.time()
        self.frame_counter = 0
        self.fps = 0


    def get_frame(self):
        # Requesting the image bytes from the RC Car (PiCamera)
        img_bytes = self.server_cam.get_img_bytes()
        self.frame_counter += 1

        # Calculating the fps when 1 second has passed.
        elapsed_time = time.time() - self.start_time
        if(elapsed_time >= 1):
            self.fps = round(self.frame_counter / elapsed_time, 2)
            self.frame_counter = 0
            self.start_time = time.time()

        # If frame data was not successfully received or something went wrong, skip this frame.
        if img_bytes is None or img_bytes == b'' or len(img_bytes) <= 4:
            if self.cam_print_logs: print("No frame received")
            return None

        # Converting image bytes to an actual image/frame.
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:  # Ensuring the decoding was successfull as well (no corruption in image data).
            return None
        
        return frame

    def display_fps(self, frame):
        frame = cv2.putText(frame, str(self.fps) + " FPS", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), thickness=2)
        return frame
