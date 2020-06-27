import socket
import cv2
import threading

from servers import cam_server
from servers import sensor_server

RUN_SENSOR_SERVER = False


# Getting computer IP address.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

port_cam = 5000
port_sensor = 5001

# Creates and starts a UDP camera server(socket) to receive from the Raspberry Pi.
server_cam = cam_server.CameraServer(host_ip, port_cam)
server_cam.start_server()

# Creates and starts a TCP sensor server(socket) to receive the distances from the IR sensor attached to the pi.
# The server is ran on a thread to keep the connections seperated.
server_sensor = sensor_server.SensorServer(host_ip, port_sensor)

if RUN_SENSOR_SERVER:
    sensor_thread = threading.Thread(target=server_sensor.start_server, name="sensor_thread", args=())
    sensor_thread.start()


try:
    while(True):

        # Requesting a frame from RC Car (PiCamera)
        frame = server_cam.get_frame()

        # If no frame data was received or something went wrong, skip this frame.
        if frame is None:
            print("No frame received")
            continue

        
        # frame = cv2.resize(frame, (0, 0), fx=2, fy=2)

        if server_sensor.distance is not 0 and RUN_SENSOR_SERVER:
            print(f"{server_sensor.distance:.2f} cm")

        cv2.imshow("RC Car raw frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    server_cam.close_server()

    if RUN_SENSOR_SERVER:
        server_sensor.close_server()

    cv2.destroyAllWindows()
    
