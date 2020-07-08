import socket
import struct

class SensorServer:

    sensor_num_bytes = struct.calcsize('f')  # A 4 bytes float.

    def __init__(self, host_ip, port_sensor):
        self.host_ip = host_ip
        self.port_sensor = port_sensor

        self.distance = 0
        self.stop_sensor_server = False

    def start_server(self):
        self.sensor_socket = socket.socket()  # Not in constructor so the socket is on the thread completely.

        self.sensor_socket.bind((self.host_ip, self.port_sensor))

        self.sensor_socket.listen(0)
        print(f"Server (sensor) - TCP connection opened on {self.host_ip}:{self.port_sensor}, waiting for sensor connection...")

        self.sensor_conn = self.sensor_socket.accept()[0]  # sensor connection.
        print("Server (sensor) - Connection made with IR sensor")

        # Getting the distance from the Pi at a constant rate (rate is set on the client (the Pi))
        while(not self.stop_sensor_server):
            try:
                data = self.sensor_conn.recv(self.sensor_num_bytes)
            except ConnectionAbortedError as err:
                pass  # For when the connection is interupted from program exit.

            if(data == 0 or data == b''):
                break

            self.distance = struct.unpack('f', data)[0]
            # print(f"{self.distance:.2f} cm")


    def close_server(self):
        self.stop_sensor_server = True
        self.sensor_socket.close()
        self.sensor_conn.close()
        print("Server (sensor) - Sensor connection closed")