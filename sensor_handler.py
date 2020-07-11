import threading
import cv2

from servers import sensor_server

class SensorHandler:

    def __init__(self, host_ip, port_sensor, run_sensor_server):
        self.run_sensor_server = run_sensor_server

        # Creates and starts a TCP sensor server(socket) to receive the distances from the IR sensor attached
        # to the pi. The server is ran on a thread to keep the connections seperated.
        self.server_sensor = sensor_server.SensorServer(host_ip, port_sensor)

        if run_sensor_server:
            self.sensor_thread = threading.Thread(target=self.server_sensor.start_server, name="sensor_thread", args=())
            self.sensor_thread.start()
    

    def get_distance(self):  # Infrared sensor distance
        return self.server_sensor.distance

    def display_distance(self, frame):

        dist = self.get_distance()

        if dist == 0 or not self.run_sensor_server:
            return frame
        else:
            dist = round(dist, 2)
            frame = cv2.putText(frame, str(dist) + " cm", (10, 34), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), thickness=2)
            return frame