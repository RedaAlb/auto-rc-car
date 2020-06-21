import socket
import struct

import cv2
import numpy as np


class CameraServer:

    UDP_BYTE_LIMIT = 65507

    bytes_offset = 5

    def __init__(self, host_ip, port_car):
        self.host_ip = host_ip
        self.port_car = port_car

        self.cam_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def start_server(self):
        self.cam_socket.bind((self.host_ip, self.port_car))
        print(f"Server (camera) - UDP connection opened on {self.host_ip}:{self.port_car}...")


    def get_frame(self):

        frame = None

        img_num_bytes = 0

        # While not receiving from the Pi, keep trying until data is receieved.
        while img_num_bytes == 0:
            try:
                # Getting the size(number of bytes) of the image to be received, (which is an int32, 4 bytes).
                img_num_bytes = struct.unpack("<L", self.cam_socket.recvfrom(4)[0])[0]
            except OSError as err1:
                print("1  OSError " + str(err1))

        img_bytes = b''  # This will hold the actual frame/image in bytes.

        # Checking if the image exceeds the UDP byte limit, if it is, then receive 2 packets (splitted frame).
        if(img_num_bytes >= self.UDP_BYTE_LIMIT):
            #print("This frame was split in half.")
            
            half1_num_bytes = int(img_num_bytes / 2)

            if(img_num_bytes % 2 == 0):
                half2_num_bytes = img_num_bytes - half1_num_bytes
            else:
                half2_num_bytes = img_num_bytes - half1_num_bytes - 1

            try:
                half1 = self.cam_socket.recvfrom(half1_num_bytes)[0]
            except OSError as err2:
                print("2  OS Error, from half 1 " + str(err2))

            try:
                half2 = self.cam_socket.recvfrom(half2_num_bytes + self.bytes_offset)[0]
            except OSError as err3:
                print("3  OS Error, from half 2 " + str(err3))

            # Combine both halves to make the full frame.
            img_bytes = half1 + half2

        else:
            # Size less than UDP_BYTE_LIMIT(65507), avoid unnecessary splitting.
            if img_num_bytes is not 0:
                try:
                    img_bytes = self.cam_socket.recvfrom(img_num_bytes)[0]
                except OSError as err4:
                    print("4  OS Error, from full frame " + str(err4))

            # else:
            # 	print("5  Full frame error.")

        if img_num_bytes is not 0:
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        return frame

    def close_server(self):
        self.cam_socket.close()
        print("Server (camera) - connection closed")
