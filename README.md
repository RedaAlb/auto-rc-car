# Auto-RC-Car

This is my MSc Artificial Intelligence project.

This readme file is to be updated and refined as the projects evolves.


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
    - [ ] Create and train Auto steering module.
    - [ ] Extract road features
        - [ ] Mask of the road using only edges of the road.
        - [ ] Centre of lane
    - [ ] Train a CNN on only the masks to find optimal CNN for masks, then combine with full frame CNN.
    - [ ] Add centre of lane to fully connected layer (FCL) at the end to create 1 big network to combine all features.
    - So network will consists of 2 image inputs, frame and mask, and 1 int at the FCL.
- [ ] Train a CNN to detect traffic signs, where the prediction is [x, y, w, h] of the bounding box.
- [ ] Add docstrings and document everything.


## Files and directories notes
`main.py` is the executable for this project. It combines everything together.

`cam_handler.py` handles anything related to the camera.

`sensor_handler.py` handles anything related to the infrared sensor.

`controller_handler.py` handles anything related to the controller/motors of the car.


`/servers`, contains the server files for the camera, sensor, and controller connections between the computer and the Pi.

`/on_raspberrypi`, contains the files that are on the raspberry pi.

`/testing`, contains sub-directories to test and analyse different components of the project.

`/steering`, contains anything related to the autonomous steering.

## To run
- [ ] Add hardware configuration here.
- [ ] I need to check if running from root or sub-directories makes a difference or not.
- [ ] Somewhere I need to explain all the keyboard inputs to use, but if I do a GUI, I might not need to.

1. Run `main.py` on the computer.
1. Run `cam_client.py` on the pi.
1. Run `sensor_control_client.py` on the pi.

## Keyboard shortcuts

I need to make this section better and put it somewhere more appropriate.

`[q]` Quit program.<br />
`[p]` Pause/unpause data collection.<br />
`[s]` Save data collected.<br />
`[r]` Reset/delete currently collected data.<br />
`[i]` Information regarding current data collection state<br />
`[1]`, `[2]`, `[3]` To choose which steering direction mode to collect data for (forward, left, right).<br />
`[Arrows]` Control car.<br />
