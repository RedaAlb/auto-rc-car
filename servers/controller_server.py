import socket
import struct
import time

class ControllerServer:

    CONTROLLER_DELAY = 0  # Delay in seconds on how much to wait until updating the direction of the car.

    def __init__(self, host_ip, port_controller):
        self.host_ip = host_ip
        self.port_controller = port_controller

        # This will hold what signal to send to pi to tell the motors/pi to do.
        self.controller = 2  # Can be -1, 1, 2, or 3 -> do nothing, forward, left, right, signals respectively
        self.stop_controller_server = False

    def start_server(self, queue):
        self.controller_socket = socket.socket()  # Not in constructor so the socket is on the thread completly.
        self.controller_socket.bind((self.host_ip, self.port_controller))

        self.controller_socket.listen(0)
        print(f"Server (controller) - TCP connection opened on {self.host_ip}:{self.port_controller}, waiting for controller connection...")

        self.controller_conn = self.controller_socket.accept()[0]
        print("Server (controller) - Connection made with Pi motors")


        # Sending the currently set control signal to the pi, to tell the motors what to do.
        while(not self.stop_controller_server):

            # controller_in_bytes = struct.pack("i", self.controller)  # Converting to bytes.
            controller_in_bytes = struct.pack("i", queue.get())  # Converting to bytes.

            try:
                data = self.controller_conn.send(controller_in_bytes)
            except (ConnectionAbortedError, ConnectionResetError) as err:
                pass  # For when the connection is interupted from program exit.

            time.sleep(self.CONTROLLER_DELAY)


    def close_server(self):
        self.stop_controller_server = True
        self.controller_socket.close()
        self.controller_conn.close()

        print("Server (controller) - Controller connection closed")