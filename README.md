# FireAnt

Python library interfacing Raspberry Pi with [BrainyAnt](http://www.brainyant.com "Robots.Unite") platform.
Use this to build your own robot and code the funcionality you desire.

## Prerequisites

### Hardware

1. Raspberry Pi v3.0
2. Raspicam v2.1
3. Wifi connection

### Software

1. Raspbian Stretch OS
2. Python3
3. pip3
4. RPi.GPIO package

## Installation

1. Install Raspbian [Stretch](https://www.raspberrypi.org/downloads/raspbian/) OS on a microSD card
2. Connect Raspberry Pi to 
[WiFi](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md "SETTING UP WIFI VIA THE COMMAND LINE") network
3. Connect to Raspberry Pi via [ssh](https://www.raspberrypi.org/documentation/remote-access/ssh/) 
client (ssh, PuTTy, etc.)
4. Enable Raspicam:
    - Run `sudo raspi-config` in the command prompt
    - Navigate to "Interfacing Options"
    - Select "Camera"
    - Enable
    - Reboot
5. Check Python version: 
    - Run `python3 -V`
    - If python is not installed, install it via: `sudo apt-get install python3`
6. Get Pyrebase: `python3 -m pip install Pyrebase`
7. If RPi.GPIO is not installed, install it via: `pip3 install RPi.GPIO`
8. Install ffmpeg: `sudo apt-get install ffmpeg`
9. Get the __FireAnt__ package: `git clone https://github.com/BrainyAnt/FireAnt.git`
    - If _git_ is not installed run: `sudo apt-get install git`

## How to use

1. Sign in or create an account on [BrainyAnt](http://www.brainyant.com "Robots.Unite")
2. Create a new robot entry
3. Download the __auth.json__ file from the platform
4. Copy __auth.json__ to __FireAnt__ folder
5. Edit __robot.py__ to define your robot's behavior using the functions from the package 
and your own functions for controlling your robot
6. Run __robot.py__: `python3 robot.py` or simply `./robot.py`
7. Finally, you can see your robot is online on [brainyant](www.brainyant.com), in the __My Robots__ section

##Functions
###FireAnt (constructor)
This is the constructor that initializes a FireAnt object which allows the communication of commands and sensor data
between your robot and the BrainyAnt platform. 
```python
myRobot = FireAnt(auth.json)
```
It requires you to specify an authentication file (_auth.json_). The one that you've downloaded from the website 
(_How to use: step 3_). It will look for that file in the same directory where _robot.py_ is.
###get_name
Returns the name that you gave your robot as a string.
```python
myRobot.get_name()
```
###get_description
Returns the description of your robot as a string.
```python
myRobot.get_description()
```
###robot_online
Returns _True / False_ if the robot is online/offline (i.e. connected to the platform)
```python
myRobot.robot_online()
```
If the robot shuts down, or is out of WiFi range it will automatically be set to offline.
###add_sensor
Register a new sensor.
```python
myRobot.add_sensor(name, callback)
```
It requires a _name_ and a _callback_ function that is run when a request is received for that 
sensor.
###remove_sensor
Remove a sensor referenced by name.
```python
myRobot.renove_sensor(name)
```
###start_user_wait
Starts looking in the user queue for users who have requested control of your robot.
```python
myRobot.start_user_wait()
```
When a user requests control, an entry is created in the user queue. The first one in the queue will be the first 
to receive control as soon as he/she is online.
Once someone is in control, the function automatically starts the video stream.
###user_online
Returns _True / False_ if a user has requested control of your robot and is online.
```python
myRobot.user_online()
```
###get_control_data
Returns a snapshot of the entries and values found in _ControlData_ as a python _dict_
```python
myRobot.get_control_data()
```
###get_sensor_data
Returns a snapshot of the entries and values found in _SensorData_ as a python _dict_
```python
myRobot.get_sensor_data()
```
###stream_control_data
Starts listening for changes in the _ControlData_ section and runs the specified callback function every time a change
is detected.
```python
myRobot.stream_control_data(control_handler_function)
```
###stream_sensor_data
Starts listening for changes in the _SensorData_ section (i.e. sensor requests) and runs the callback function specified
for each sensor.
```python
myRobot.stream_sensor_data()
``` 
###log_session
Logs the relevant data form the control session to an archive (start of session, user ID, control time). It also removes
the user who was just in control from the queue. 
```python
myRobot.log_session()
```
##Coming soon
###add_actuator
You will have the option of easily adding actuators specific to your custom robot. You will be able to bind a key and
set a behavior for when the key is pressed (on/off, tap, hold).
###remove_actuator
Remove an actuator that you have registered.

## Feedback
Give us feedback. Tell us about any issues or troubleshooting. [Contact](http://www.brainyant.com/contact) us via email 
at *contact@brainyant.com* or message us on [facebook](https://www.facebook.com/brainyantrobots/)
