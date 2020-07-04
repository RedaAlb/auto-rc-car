import socket
import time

import numpy as np
import cv2

import matplotlib.pyplot as plt

import os
import sys
sys.path.insert(1, os.getcwd())  # So I can import the cam_server.py

from servers import cam_server

# Getting computer IP address.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

port_cam = 5000

# Creates and starts a UDP camera server(socket) to receive from the Raspberry Pi.
server_cam = cam_server.CameraServer(host_ip, port_cam)
server_cam.start_server()


start_time = time.time()

# Variables needed to calculate the FPS achieved on the computer.
temp_start_time = time.time()
frame_counter = 0
fps = 0


frame_number = 0  # Used to track frames throughout the whole connection.

SAVE_CAM_DATA = False  # Whether to save the data in the lists below for each frame.
TIME_TO_PROCESS = 5  # How long to keep saving data, in seconds.

# These lists will keep track of some cam connection details for plotting later.
all_fps = []
all_delays = []
all_img_bytes = []
frames_lost = []  # Keeps track of which frames were lost (frame numbers).


try:
    while(True):
        ss_time = time.time()  # Used to calculate the delay in the connection.

        # Requesting the image bytes from the RC Car (PiCamera)
        img_bytes = server_cam.get_img_bytes()

        delay = time.time() - ss_time

        frame_number += 1   # Running number throughout the whole connection.
        frame_counter += 1  # Only used to calculate the fps.

        # Calculating the fps when 1 second has passed.
        elapsed_time = time.time() - temp_start_time
        if(elapsed_time >= 1):
            fps = round(frame_counter / elapsed_time, 2)
            frame_counter = 0
            temp_start_time = time.time()

        # If frame data was not successfully received or something went wrong, skip this frame.
        if img_bytes is None or img_bytes == b'' or len(img_bytes) <= 4:
            print(img_bytes)
            print("No frame received")
            frames_lost.append(frame_number)
            continue


        all_fps.append(fps)
        all_delays.append(delay)
        all_img_bytes.append(len(img_bytes))

        # Converting image bytes to an actual image/frame.
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:  # Ensuring the decoding was successfull as well (no corruption in image data).
            continue


        frame = cv2.putText(frame, str(fps) + " FPS", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), thickness=1)
        frame = cv2.putText(frame, str(len(img_bytes)) + " bytes", (10, 35), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), thickness=1)
        cv2.imshow("RC Car raw frame", frame)

        if SAVE_CAM_DATA and ((time.time() - start_time) >= TIME_TO_PROCESS):
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    
    if SAVE_CAM_DATA:
        # To keep all lists/arrays the same dimensions.
        filler_amount = len(all_fps) - len(frames_lost)
        frames_lost = frames_lost + [-1 for i in range(filler_amount)]  # Fill rest of list with zeros to match length of others.

        all_cam_data = np.array([all_fps, all_delays, all_img_bytes, frames_lost])

        with open("testing\\cam_connection\\cam_data_640x480_60fps.npy", "wb") as file:
            np.save(file, all_cam_data)


    server_cam.close_server()

    cv2.destroyAllWindows()