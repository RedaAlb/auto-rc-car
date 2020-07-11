# The servers directory

There are 3 seperate servers that needs to be handled, the camera server, sensor server, and the controller server.

`cam_server.py` responsible for handling the server connection between the computer and the raspberry pi camera, to be able to get frames to the computer.

`sensor_server.py` responsible for handling the server connection between the computer and the infrared sensor attached to the pi.

`controller_server.py` responsible for handling the server connection between the computer and the motors on the pi. It will send
`-1`, `0`, `1`, `2`, or `3` to the pi, for `do nothing`, `close connection`, `forward`, `left`, `right`, signals respectively. It will determine/control what the motors do.