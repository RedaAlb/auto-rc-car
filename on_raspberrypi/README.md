# The on_raspberrypi directory

This directory contains all the files that should be on the raspberry pi.

All these files should be ran on the pi.

- `cam_client.py`
    - Used to send a real-time stream of frames to the computer(host) using a UDP socket "connection".
- `sensor_client.py`
    - Used to send the infrared sensor distance data from the pi to the computer using a TCP socket connection.