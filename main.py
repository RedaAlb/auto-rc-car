import socket
import cv2
import numpy as np

import cam_handler
import sensor_handler
import controller_handler

from steering import auto_steering_handler

from sign_detection.sign_detector import SignDetector
from sign_detection.circle_detector import CircleDetector



RUN_SENSOR_SERVER = 0
RUN_CONTROLLER_SERVER = 1


DISPLAY_FPS = 1
DISPLAY_DISTANCE = 1  # Whether to display the distance received from the infrared sensor on the pi.
CAM_PRINT_LOGS = 0    # Whether to print camera connection logs.


# Which trained models to use for autonomous driving for each direction.
F_MODEL_TO_LOAD = "3_0_16_oldM_baseL_Ddata_dAug_MEpochs"
L_MODEL_TO_LOAD = "6_4_bestModel_Lmodel_dataAug"
R_MODEL_TO_LOAD = "7_1_bestModel_Rmodel_firstTime_dAug_1000Epochs"


DETECT_SIGNS = True  # Whether to detect signs or not.
DISPLAY_TRACKBARS = False  # Display trackbars to change argument values for the hough circles detector.
DISPLAY_SIGN_DETECTED = True  # Whether to display the sign detected in the frame.


# Getting computer/host IP address.
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


# Creates a sign detector instance and starts the sign detector on a new thread.
sign_detector = SignDetector(DETECT_SIGNS, DISPLAY_SIGN_DETECTED, DISPLAY_TRACKBARS)



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


        # When auto mode is on, predict the steering and communicate that to the motors.
        if handler_controller.autonomous_mode:
            predicted_steering = handler_auto.predict_steering(raw_frame, handler_controller.auto_direction)
            handler_controller.controller.put(predicted_steering)


        # Putting the current frame in the queue to communicate it with the sign detector thread.
        sign_detector.frame_queue.put(raw_frame)
        # This method will check what type of sign it is and return the corresponding direction integer for which model to use.
        detected_sign_direction = sign_detector.get_sign_direction()
        if detected_sign_direction is not None: handler_controller.auto_direction = detected_sign_direction
        # print(detected_sign_direction, handler_controller.auto_direction)

        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        # To control the car using the keyboard, to collect training data when/if needed, and general keyboard input.
        if handler_controller.is_collecting_data:
            handler_controller.process_key_pressed(raw_frame)
            frame = handler_controller.display_recording(frame)  # To display whether currently in data collection(recording) mode or not.
        else:
            handler_controller.process_key_pressed()

        cv2.imshow("RC Car camera feed", frame)
        

finally:

    handler_cam.server_cam.close_server()

    if RUN_SENSOR_SERVER:
        handler_sensor.server_sensor.close_server()
    if RUN_CONTROLLER_SERVER:
        handler_controller.server_controller.close_server()
        handler_controller.controller.put(0)  # To exit the controller thread/connection.

    sign_detector.frame_queue.put(0)
    sign_detector.detect_signs = False

    cv2.destroyAllWindows()

