# Auto-RC-Car

This is my MSc Artificial Intelligence project.

This readme file is to be updated and refined as the projects evolves.


## To do next
- [x] Make camera connection extra robust/reliable and just amazingly fast.
- [x] Add and use multithreading for the sensor server.
- [ ] Close sensor server and thread more neatly and properly.
- [x] Look into multithreading options.
- [ ] Add the controller server.
    - [ ] Use multithreading for it.


## Files and directories notes

`main.py` is the executable for this project. It combines everything together.

`/servers`, contains the server files for the camera, sensor, and controller connections between the computer and the Pi.

`/on_raspberrypi`, contains the files that are on the raspberry pi and that needs to be ran on the pi.


## To run

- [ ] Add hardware configuration here.

1. Run `main.py`
2. Run `cam_client.py` on the pi.