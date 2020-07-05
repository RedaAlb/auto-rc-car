import socket
import threading
import time

import numpy as np
import cv2

from servers import cam_server
from servers import sensor_server

RUN_SENSOR_SERVER = False


# Getting computer IP address.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

port_cam = 5000
port_sensor = 5001

# Creates and starts a UDP camera server(socket) to receive from the Raspberry Pi.
server_cam = cam_server.CameraServer(host_ip, port_cam)
server_cam.start_server()

# Creates and starts a TCP sensor server(socket) to receive the distances from the IR sensor attached to the pi.
# The server is ran on a thread to keep the connections seperated.
server_sensor = sensor_server.SensorServer(host_ip, port_sensor)

if RUN_SENSOR_SERVER:
    sensor_thread = threading.Thread(target=server_sensor.start_server, name="sensor_thread", args=())
    sensor_thread.start()

# Variables needed to calculate the FPS achieved on the computer.
start_time = time.time()
frame_counter = 0
fps = 0

try:
    while(True):
        # Requesting the image bytes from the RC Car (PiCamera)
        img_bytes = server_cam.get_img_bytes()
        frame_counter += 1

        # Calculating the fps when 1 second has passed.
        elapsed_time = time.time() - start_time
        if(elapsed_time >= 1):
            fps = round(frame_counter / elapsed_time, 2)
            frame_counter = 0
            start_time = time.time()

        # If frame data was not successfully received or something went wrong, skip this frame.
        if img_bytes is None or img_bytes == b'' or len(img_bytes) <= 4:
            print("No frame received")
            continue

        # Converting image bytes to an actual image/frame.
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:  # Ensuring the decoding was successfull as well (no corruption in image data).
            continue


        if server_sensor.distance is not 0 and RUN_SENSOR_SERVER:
            print(f"{server_sensor.distance:.2f} cm")


        frame = cv2.putText(frame, str(fps) + " FPS", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), thickness=1)
        cv2.imshow("RC Car raw frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    server_cam.close_server()

    if RUN_SENSOR_SERVER:
        server_sensor.close_server()

    cv2.destroyAllWindows()
    
