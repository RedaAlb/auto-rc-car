# The on_raspberrypi directory

This directory contains all the files that should be on the raspberry pi.

All these files should be ran on the pi.

- `cam_client.py`
    - Used to send a real-time stream of frames to the computer(host) using a UDP socket "connection".
    - Since it is a UDP socket, it does not matter which one you run first, the 'cam_server.py' or the 'cam_client.py'.