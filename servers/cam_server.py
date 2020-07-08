import socket
import struct

import cv2
import numpy as np


class CameraServer:

    UDP_BYTE_LIMIT = 65507

    def __init__(self, host_ip, port_car, print_logs):
        self.host_ip = host_ip
        self.port_car = port_car
        self.print_logs = print_logs

        self.cam_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def start_server(self):
        self.cam_socket.bind((self.host_ip, self.port_car))
        print(f"Server (camera) - UDP connection opened on {self.host_ip}:{self.port_car}...")


    def get_img_bytes(self):

        img_bytes = b''  # This will hold the actual frame/image in bytes.

        img_num_bytes = 0

        try:
            # Getting the size(number of bytes) of the image to be received, (which is an int32, 4 bytes).
            img_num_bytes = struct.unpack("<L", self.cam_socket.recvfrom(4)[0])[0]
            # print("Frame number of bytes", img_num_bytes)
        except OSError as err1:
            if self.print_logs: print("1  OSError, from img number of bytes:", str(err1))

        # If no data was received, skip this frame.
        if img_num_bytes == 0:
            return None

        # Checking if the image exceeds the UDP byte limit, if it is, then receive 2 packets (splitted frame).
        if(img_num_bytes >= self.UDP_BYTE_LIMIT):
            #print("This frame was split in half.")
            
            half1_num_bytes = img_num_bytes // 2
            half2_num_bytes = img_num_bytes - half1_num_bytes
            
            try:
                half1 = self.cam_socket.recvfrom(half1_num_bytes)[0]
            except OSError as err2:
                if self.print_logs: print("2  OSError, from half 1:", str(err2))
                return None

            try:
                half2 = self.cam_socket.recvfrom(half2_num_bytes)[0]
            except OSError as err3:
                if self.print_logs: print("3  OSError, from half 2:", str(err3))
                return None

            # Combine both halves to make the full frame.
            try:
                img_bytes = half1 + half2
            except NameError as err4:
                if self.print_logs: print("4  NameError from halves combination:", str(err4))
                return None

        # Size less than UDP_BYTE_LIMIT(65507), avoid unnecessary splitting.
        else:
            try:
                img_bytes = self.cam_socket.recvfrom(img_num_bytes)[0]
            except OSError as err5:
                if self.print_logs: print("5  OS Error, from full frame:", str(err5))
                return None

        return img_bytes

    def close_server(self):
        self.cam_socket.close()
        print("Server (camera) - connection closed")
