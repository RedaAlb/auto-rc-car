# The on_raspberrypi directory

This directory contains all the files that should be on the raspberry pi.

- `cam_client.py`
    - Used to send a real-time stream of frames to the computer(host) using a UDP socket "connection".
- `sensor_client.py`
    - Used to send the infrared sensor distance data from the pi to the computer using a TCP socket connection.
- `controller_client.py`
    - Used to receive control signals from the computer to tell the motors what to do.
- `sensor_controller_client.py`, used to run `sensor_client.py` and `controller_client.py` at the same time using two threads.