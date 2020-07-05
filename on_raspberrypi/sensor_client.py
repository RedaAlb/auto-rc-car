import socket
import explorerhat as eh
import time
import struct

# host_ip = "192.168.0.17"  #  desktop
host_ip = "192.168.0.15"    #  laptop
host_port = 5001

host = (host_ip, host_port)

client_socket = socket.socket()

print(f"Client (sensor) - Waiting to connect to {host}...")
client_socket.connect(host)
print(f"Client (sensor) - Connection made with {host}...")


DISTANCE_DELAY = 0.2  # In seconds, how long to wait to send another distance reading.
VOLT_AVG_VALUES = 10  # How many voltage values to use to get an average reading.

def get_distance():

    # Getting 10 voltage readings and then getting the average to reduce noisy data.
    voltage_values = []
    for i in range (VOLT_AVG_VALUES):
        voltage_values.append(eh.analog.four.read())

    avg_voltage = sum(voltage_values) / VOLT_AVG_VALUES

    # To prevent division by zero errors, in case the voltage readings were corrupted.
    if (avg_voltage <= 0):
        avg_voltage = 0.001

    # Calculating the distance, 13 because for 1V, the distance is 13cm for this sensor.
    distance = round(13 / avg_voltage, 2)

    return distance

try:
    while True:
        distance = get_distance()
        dist_bytes = struct.pack("f", distance)  # Converting to bytes, "f" -> 4 bytes for float32.

        try:
            client_socket.send(dist_bytes)
        except (BrokenPipeError, ConnectionResetError) as err:
            break  # For when the server (computer) closes the connection.

        time.sleep(DISTANCE_DELAY)  # Adding a small delay as the distance is not needed at every moment.

finally:
    client_socket.close()
    print("Client (sensor) - connection closed")
