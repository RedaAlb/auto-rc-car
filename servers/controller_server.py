import socket
import struct
import time

class ControllerServer:

    CONTROLLER_DELAY = 0  # Delay in seconds on how much to wait until updating the direction of the car.

    def __init__(self, host_ip, port_controller):
        self.host_ip = host_ip
        self.port_controller = port_controller

        self.stop_controller_server = False

    def start_server(self, controller):
        self.controller_socket = socket.socket()  # Not in constructor so the socket is on the thread completely.
        self.controller_socket.bind((self.host_ip, self.port_controller))

        self.controller_socket.listen(0)
        print(f"Server (controller) - TCP connection opened on {self.host_ip}:{self.port_controller}, waiting for controller connection...")

        self.controller_conn = self.controller_socket.accept()[0]
        print("Server (controller) - Connection made with Pi motors")


        # Sending the currently set control signal to the pi, to tell the motors what to do.
        while(not self.stop_controller_server):

            # This will hold what signal to send to pi to tell the motors/pi to do.
            steering_dir = controller.get()  # Can be -1, 0, 1, 2, or 3 -> do nothing, close connection, forward, left, right, signals respectively.
            
            controller_in_bytes = struct.pack("i", steering_dir)  # Converting to bytes.

            try:
                data = self.controller_conn.send(controller_in_bytes)
            except (ConnectionAbortedError, ConnectionResetError) as err: # For when the connection is interupted from program exit.
                break


            if steering_dir == 0:  # zero signals to close the connection.
                self.close_server()
                break

            time.sleep(self.CONTROLLER_DELAY)


    def close_server(self):
        self.stop_controller_server = True
        self.controller_socket.close()

        try:
            self.controller_conn.close()
        except AttributeError as err:  # When program exits without making a connection to the controller server.
            pass

        print("Server (controller) - Controller connection closed")