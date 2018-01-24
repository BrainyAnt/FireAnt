# FireAnt
BrainyAnt python library for interfacing with Brainyant online platform.

## Requirements
### Hardware
  - Raspberry Pi V3.0
  - Raspicam V2.1
### Software
  - Python 2.7
  - Internet connection
## Installation
  - Create an account on [www.brainyant.com]
    Browse to brainyant.com, create an account and add a new robot. Remember to add a video stream for the robot; Connect to your RPi, open a browser and login to your account in brainyant.com. Go to the newly added robot and press the "Download Auth File" button. This will save auth.json that contains your robot credentials. Save it on the disk in the same folder where _robot.py_ will be.
  - Clone this repository
  '''
  git clone 
  '''
  - Install ffmpeg
  '''
  sudo apt-get install ffmpeg
  '''
  - Enable raspicam:
  '''
  sudo raspi-config
  '''
  - Navigate to 'Interface Options'>'Camera' and enable camera. Reboot device.
  
## Useage
  - To start adding functionality to your robot you can edit the _robot.py_ file. Include class implemented in _fireant.py_. Follow the comments.
  - Run _robot.py_
