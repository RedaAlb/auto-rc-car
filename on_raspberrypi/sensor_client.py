import socket
import explorerhat as eh
import time
import struct


class SensorClient:

    DISTANCE_DELAY = 0.2  # In seconds, how long to wait to send another distance reading.
    VOLT_AVG_VALUES = 10  # How many voltage values to use to get an average reading.


    def __init__(self, host):
        self.host = host

    def get_distance(self):

        # Getting 10 voltage readings and then getting the average to reduce noisy data.
        voltage_values = []
        for i in range (self.VOLT_AVG_VALUES):
            voltage_values.append(eh.analog.four.read())

        avg_voltage = sum(voltage_values) / self.VOLT_AVG_VALUES

        # To prevent division by zero errors, in case the voltage readings were corrupted.
        if (avg_voltage <= 0):
            avg_voltage = 0.001

        # Calculating the distance, 13 because for 1V, the distance is 13cm for this sensor.
        distance = round(13 / avg_voltage, 2)

        return distance

    def start_client(self):

        client_socket = socket.socket()

        print(f"Client (sensor) - Waiting to connect to {self.host}...")

        try:
            client_socket.connect(self.host)
            print(f"Client (sensor) - Connection made with {self.host}...")
        except TimeoutError as err:  # For when only controller server is ran.
            print("Client (sensor) - Connection timed out")

        try:
            while True:
                distance = self.get_distance()
                dist_bytes = struct.pack("f", distance)  # Converting to bytes, "f" -> 4 bytes for float32.

                try:
                    client_socket.send(dist_bytes)
                except (BrokenPipeError, ConnectionResetError) as err:
                    break  # For when the server (computer) closes the connection.

                time.sleep(self.DISTANCE_DELAY)  # Adding a small delay as the distance doesn't need to be updated every moment.

        finally:
            client_socket.close()
            print("Client (sensor) - Connection closed")
