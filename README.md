# Auto-RC-Car

This is my MSc Artificial Intelligence project. A paper associated with this project will be available here on project completion.

This readme file is to be updated and refined at the end of the project.


## To do next
- [x] Make camera connection extra robust/reliable and just amazingly fast.
- [x] Add and use multithreading for the sensor server.
- [x] Make a testing file for the camera connection for analysis, plots of e.g. FPS, delay, img bytes, etc.
    - [ ] I need to get more details about the frames lost in every second (how many lost frames in the 30 frames
    sent in the second), if that is substantial.
    - [ ] A way to see/find out when and how many frames are lost, is it usually 1 or are they lost consecutively.
- [x] Add testing folder to this readme file.
- [x] Close sensor server and thread more neatly and properly.
- [x] Look into multithreading options.
- [x] Add the controller server.
    - [x] Use multithreading for it.
- [x] Make main loop in main.py into a class, and clean up main.py
    - Maybe make a CamHandler class to take care of it, and have instance var of frame that I can access
    in main.py
- [x] Close threads properly when program is finished.
- [ ] Make another window for all stats/details, e.g. fps, num of bytes, delay, distance, etc.
- [ ] Make a GUI specific class to handle all GUI related stuff.
- [ ] Find an alternative to pygame......... I don't like it at all. I need a better way to get keyboard input without interfering with cv2.
- [ ] I might want to make a data collection class to handle all of that to keep seperate from the controller handler.
- [ ] RC Car steering
    - [x] Add ability to collect training data
    - [x] Collect data 
    - [x] Create and train Auto steering module.
    - [x] Extract road features
        - [x] Mask of the road using only edges of the road.
        - [x] Centre of lane
    - [x] Train a CNN on only the masks to find optimal CNN for masks, then combine with full frame CNN.
    - [x] Add centre of lane to fully connected layer (FCL) at the end to create 1 big network to combine all features.
        - So network will consists of 2 image inputs, frame and mask, and 1 integer at the final fully connected layer.
    - [x] Once the forward model is trained and works well, train the left and right models.
- [ ] Create and train sign detector.
    - [ ] Apply it to the RC Car.
- [ ] Create and train a CNN to detect traffic signs, where the prediction is [x, y, w, h] of the bounding box.
- [ ] Try to make the car map the road.
    - [ ] Ability to map the road into a 2D canvas as the car moves around the road in real-time.
    - [ ] Ability to select any position on the road on the 2D canvas and the car to navigate to that position.
- [ ] Real-time graph of the FPS, to track when/if things go wrong.
- [ ] Add docstrings and document everything.


## Files and directories notes
`main.py` is the executable for this project. It combines everything together.

`cam_handler.py` handles anything related to the camera.

`sensor_handler.py` handles anything related to the infrared sensor.

`controller_handler.py` handles anything related to the controller/motors of the car.


`/servers`, contains the server files for the camera, sensor, and controller connections between the computer and the Pi.

`/on_raspberrypi`, contains the files that are on the raspberry pi.

`/testing`, contains sub-directories to test and analyse different components of the project.

`/steering`, contains anything related to the autonomous steering/driving.

## To run

TODO:
- Add hardware configuration here.
- Somewhere I need to explain all the keyboard inputs to use, but if I do a GUI, I might not need to.
- Add exact steps to re-produce everything. Also show how to run for specific tasks, e.g. to train model, collect data, etc.


## Keyboard shortcuts

TODO: I need to make this section better and put it somewhere more appropriate.

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