import threading
import time

from sensor_client import SensorClient
from controller_client import ControllerClient

host_ip = "192.168.0.17"  #  desktop

port_sensor = 5001
port_controller = 5002

host_sen = (host_ip, port_sensor)
host_con = (host_ip, port_controller)


client_sensor = SensorClient(host_sen)
client_controller = ControllerClient(host_con)


sensor_thread = threading.Thread(target=client_sensor.start_client, name="sensor_client", args=())
control_thread = threading.Thread(target=client_controller.start_client, name="controller_client", args=())

sensor_thread.start()
time.sleep(1)
control_thread.start()