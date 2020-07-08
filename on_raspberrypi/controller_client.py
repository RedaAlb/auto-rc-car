import socket
import explorerhat as eh
import time
import struct


class ControllerClient:

    SPEED = 60  # Speed of the car.

    def __init__(self, host):
        self.host = host

    def start_client(self):
        # The number of bytes to receive for the direction to move in.
        # Could be -1, 1, 2, or 3 -> do nothing, forward, left, right, signals respectively.
        dir_num_bytes = struct.calcsize('i')

        # Keeping track of the previous direction received so I don't spam the motors everytime when the same direction received.
        prev_dir = -1

        client_socket = socket.socket()

        print(f"Client (controller) - Waiting to connect to {self.host}...")
        client_socket.connect(self.host)
        print(f"Client (controller) - Connection made with {self.host}...")

        try:
            while True:

                try:
                    data = client_socket.recv(dir_num_bytes)
                except KeyboardInterrupt:
                    pass
                
                if(data == b''):  # If no data was received.
                    break

                direction = struct.unpack('i', data)[0]

                if direction == 0:  # If the direction received is zero, then close down the connection.
                    break
                
                # print("Direction received", direction)
                
                if direction is not prev_dir:
                    # print("Direction changed", direction)
                    prev_dir = direction

                    # TODO: Possibly make this into switch statement.

                    if (direction == -1):  # do nothing
                        eh.motor.one.stop()
                        eh.motor.two.stop()

                    elif (direction == 1):  # forward
                        eh.motor.one.forward(self.SPEED)
                        eh.motor.two.forward(self.SPEED)

                    elif (direction == 2):  # left
                        eh.motor.one.stop()
                        eh.motor.two.forward(self.SPEED)

                    elif (direction == 3):  # right
                        eh.motor.one.forward(self.SPEED)
                        eh.motor.two.stop()

                    else:  # if anything else was sent.
                        eh.motor.one.stop()
                        eh.motor.two.stop()
                
                #time.sleep(0.01)

        finally:
            eh.motor.one.stop()
            eh.motor.two.stop()
            
            client_socket.close()
            print("Client (controller) - connection closed")