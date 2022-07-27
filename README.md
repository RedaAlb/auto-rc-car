# Auto-RC-Car

This is my MSc Artificial Intelligence project. This repo is being replaced by a newer [repo](https://github.com/RedaAlb/auto-rc-car) as I am re-creating the project from scratch.

There is a paper associated with this project, which can be found [here](for_readme/MSc_AI_Auto_RC_Car_paper.pdf).


## Files and directories notes
`main.py` is the executable for this project. It combines everything together.

`cam_handler.py` handles anything related to the camera.

`sensor_handler.py` handles anything related to the infrared sensor.

`controller_handler.py` handles anything related to the controller/motors of the car.


`/servers`, contains the server files for the camera, sensor, and controller connections between the computer and the Pi.

`/on_raspberrypi`, contains the files that are on the raspberry pi.

`/testing_cam_connection`, contains files to test and analyse the camera network connection between the computer and the Pi.

`/steering`, contains anything related to the autonomous steering/driving.

`/sign_detection`, contains anything related to the signs detection and recognition.

`/traffic_light_detection`, contains anything related to the traffic light detection.

`/gui`, contains all the files related to creating the gui, including the road mapping.

`/for_readme`, contains files such as images for the main readme file.

## To run

### Step 0 - Hardware components required

There are two options:

1. Use only the minimum hardware required, which is a Raspberry Pi (any version) and a PiCamera connected to it. This will only allow you to stream the camera frames to the computer at your chosen resolution and FPS.

1. To produce the exact same results and be able run everything, below is all the hardware components you will need:

| Component                        | Purpose                 | Cost (£) |
|----------------------------------|-------------------------|----------|
| Raspberry Pi 4 Model B - 8GB RAM | Microcomputer           | 73.50    |
| Explorer HAT Pro                 | H-Bridge & Analog input | 20.40    |
| Raspberry   Pi Camera v2.1       | Camera                  | 24.21    |
| Sharp IR GP2Y0A41SK0F            | Distance sensor         | 8.99     |
| STS-Pi Roving Robot              | Chassis & Motors        | 27.90    |
| Poweradd EnergyCell 5000mAh      | Power supply            | 12.00    |
| Total cost                       |                         | 167.00   |


Visual view of the hardware setup:

![Visual hardware setup](for_readme/hardware_setup.PNG)



### Step 1 - Setting up the environment

- Python 3.7.7 is required.
- Setup an environment using the `requirements.txt` file (to be added).


### Step 2 - To run

1. Change appropriate parameters (capital variable names) in `main.py` if needed.
1. Run `main.py`, this will display your computer local IP address for convenience.
1. Change the host IP to the one obtained from the previous step in `cam_client.py`, then run `cam_client.py` on the Raspberry Pi.
    - You should now see the live camera feed on the computer.
    - You can specify the resolution and FPS in `cam_client.py`
1. Change the host IP in `sensor_controller_client.py`, then run `sensor_controller_client.py` on the Raspberry Pi to establish the sensor and controller connections.
1. See keyboard shortcuts below.
1. For anything else such as model training, each directory has its own readme file you can [refer to.](#Files-and-directories-notes)

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
