# Auto-RC-Car

This is my MSc Artificial Intelligence project. A paper associated with this project will be available here on project completion.


## Files and directories notes
`main.py` is the executable for this project. It combines everything together.

`cam_handler.py` handles anything related to the camera.

`sensor_handler.py` handles anything related to the infrared sensor.

`controller_handler.py` handles anything related to the controller/motors of the car.


`/servers`, contains the server files for the camera, sensor, and controller connections between the computer and the Pi.

`/on_raspberrypi`, contains the files that are on the raspberry pi.

`/testing`, contains sub-directories to test and analyse different components of the project.

`/steering`, contains anything related to the autonomous steering/driving.

`/sign_detection`, contains anything related to the signs detection and recognition.

`/traffic_light_detection`, contains anything related to the traffic light detection.

`/gui`, contains all the files related to creating the gui, including the road mapping.

## To run

TODO:
- Add hardware configuration here.
- Somewhere I need to explain all the keyboard inputs to use, but if I do a GUI, I might not need to.
- Add exact steps to re-produce everything. Also show how to run for specific tasks, e.g. to train model, collect data, etc.


## Keyboard shortcuts

`[q]` Quit program.<br>
`[p]` Pause/unpause data collection.<br>
`[s]` Save data collected.<br>
`[r]` Reset/delete currently collected data.<br>
`[i]` Information regarding current data collection state<br>
`[1]`, `[2]`, `[3]` To choose which steering direction mode to collect data for (forward, left, right). Note that if not in data collection mode, `[1]`, `[2]`, `[3]` will be used to change which model to use for autonomous driving.<br>
`[0]` Add one lap, used to track what lap you are in when collecting data for convenience.<br>
`[-]` Reset the laps done to zero.<br>
`[Arrow keys]` Control car.<br>
`[a]` Toggle between autonomous mode and manual driving.<br>
`[#]` Stop the car.<br>
`[c]` Capture and save current frame/image.<br>
