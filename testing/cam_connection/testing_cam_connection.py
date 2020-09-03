import socket
import time

import numpy as np
import cv2

import matplotlib.pyplot as plt

import os
import sys
sys.path.insert(1, os.getcwd())  # So I can import the cam_server.py

import cam_handler



CAM_PRINT_LOGS = True  # Whether to print camera connection logs.
DISPLAY_FPS = True

SAVE_CAM_DATA = True  # Whether to save the data in the lists below for each frame.
TIME_TO_PROCESS = 600  # How long to keep saving data, in seconds.

# Please note this is only used for the filename, to change the actual FPS and resolution, change it in /on_raspberrypi/cam_client.py
FPS_RES_TEST = "60fps_1640x922"

# Getting computer IP address.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

port_cam = 5000

# Creates and starts a UDP camera server(socket) to receive from the Raspberry Pi.
handler_cam = cam_handler.CamHandler(host_ip, port_cam, CAM_PRINT_LOGS)


frame_number = 0  # Used to track frames throughout the whole connection.

all_fps = []        # Stores all the FPS achieved throughout the connection.
all_delays = []     # Keeps track of all the delays for each frame.
all_img_bytes = []  # Stores the image number of bytes (size) of each frame received.

frames_lost = []  # Keeps track of which frames were lost (frame numbers). 

start_time = time.time()

try:
    while(True):
        start_d_time = time.time()  # Used to calculate the delay in the connection.

        # Requesting/getting the frame from the pi.
        frame, img_bytes = handler_cam.get_frame()

        all_delays.append(time.time() - start_d_time)  # Storing the delay.
        all_fps.append(handler_cam.fps)
        # if img_bytes is not None: all_img_bytes.append(len(img_bytes))

        # If frame was lost in any way. Please see get_frame() for when None is returned.
        if frame is None:
            print("Frame", frame_number, "was lost.")
            frames_lost.append(frame_number)
            all_img_bytes.append(-1)  # Adding -1 so all the arrays are the same size for easier saving (as one big numpy array).

            frame_number += 1
            continue

        frames_lost.append(-1)
        all_img_bytes.append(len(img_bytes))
        frame_number += 1

        if frame_number % 1000 == 0:
            print(frame_number, "frames done, time passed:", time.time() - start_time)

        if DISPLAY_FPS: frame = handler_cam.display_fps(frame)


        cv2.imshow("RC Car frame", frame)

        if SAVE_CAM_DATA and ((time.time() - start_time) >= TIME_TO_PROCESS):
            print(f"{TIME_TO_PROCESS} seconds finished.")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:

    handler_cam.server_cam.close_server()

    if SAVE_CAM_DATA:

        all_cam_conn_data = np.array([all_fps, all_delays, all_img_bytes, frames_lost])

        with open(f"testing\\cam_connection\\cam_data_{FPS_RES_TEST}.npy", "wb") as file:
            np.save(file, all_cam_conn_data)

    cv2.destroyAllWindows()