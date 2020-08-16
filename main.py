import socket
import cv2
import numpy as np

import cam_handler
import sensor_handler
import controller_handler

from steering import auto_steering_handler



RUN_SENSOR_SERVER = 0
RUN_CONTROLLER_SERVER = 1


DISPLAY_FPS = 1
DISPLAY_DISTANCE = 1  # Whether to display the distance received from the infrared sensor on the pi.
CAM_PRINT_LOGS = 0    # Whether to print camera connection logs.


F_MODEL_TO_LOAD = "3_0_16_oldM_baseL_Ddata_dAug_MEpochs"  # Which model to use for autonomous driving for the forward model.
L_MODEL_TO_LOAD = "6_4_bestModel_Lmodel_dataAug"
R_MODEL_TO_LOAD = "7_1_bestModel_Rmodel_firstTime_dAug_1000Epochs"



# Getting computer IP address.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

port_cam = 5000
port_sensor = 5001
port_controller = 5002

handler_cam = cam_handler.CamHandler(host_ip, port_cam, CAM_PRINT_LOGS)
handler_sensor = sensor_handler.SensorHandler(host_ip, port_sensor, RUN_SENSOR_SERVER)
handler_controller = controller_handler.ControllerHandler(host_ip, port_controller, RUN_CONTROLLER_SERVER)



handler_auto = auto_steering_handler.AutoSteeringHandler()  # Autonomous driving handler.
handler_auto.load_models(F_MODEL_TO_LOAD, L_MODEL_TO_LOAD, R_MODEL_TO_LOAD)  # Loading trained forward, left, and right models.





try:
    while(True):

        # Requesting/getting the frame from the pi.
        raw_frame = handler_cam.get_frame()

        if raw_frame is None:  # Ensuring a frame was received and processed successfully.
            continue

        frame = raw_frame.copy()  # Creating a copy which I can alter, while still having the raw frame.

        if DISPLAY_FPS: frame = handler_cam.display_fps(frame)


        # Getting the infrared sensor distance from the pi.
        distance = handler_sensor.get_distance()
        if DISPLAY_DISTANCE: frame = handler_sensor.display_distance(frame)



        if handler_controller.autonomous_mode:
            predicted_steering = handler_auto.predict_steering(raw_frame, handler_controller.auto_direction)
            handler_controller.controller.put(predicted_steering)



        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # To control the car using the keyboard and to collect training data when/if needed.
        if handler_controller.is_collecting_data:
            handler_controller.process_key_pressed(raw_frame)
            frame = handler_controller.display_recording(frame)  # To display whether currently in data collection(recording) mode or not.
        else:
            handler_controller.process_key_pressed()

        cv2.imshow("RC Car frames", frame)
        

finally:

    handler_cam.server_cam.close_server()

    if RUN_SENSOR_SERVER:
        handler_sensor.server_sensor.close_server()
    if RUN_CONTROLLER_SERVER:
        handler_controller.server_controller.close_server()
        handler_controller.controller.put(0)  # To exit the controller thread/connection.

    cv2.destroyAllWindows()

