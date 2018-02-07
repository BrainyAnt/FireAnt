# FireAnt

Python library interfacing Raspberry Pi with BrainyAnt platform.
Use this to build your own robot and code the funcionality you desire.

## Prerequisites

### Hardware

1. Raspberry Pi v3.0
2. Raspicam v2.1
3. Wifi connection

### Software

1. Raspbian Stretch OS
2. Python 2.7

## Installation

1. Install [Stretch](https://www.raspberrypi.org/downloads/raspbian/) on an SD card
2. Connect Raspberry Pi to WiFi network ([guide](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md "SETTING WIFI UP VIA THE COMMAND LINE"))
2. Enable Raspicam and ssh: `sudo raspi-config`
3. Check Python version: `python -V`
    If python is not installed, install via `sudo apt-get install python`
4. Install pip: `sudo apt-get install python-pip`
5. Get Pyrebase: `sudo pip install Pyrebase`
6. Apply this python 2.7 - Pyrebase compatibility [fix](https://gist.github.com/codeAshu/f6384203706e989b0d38db6e0a9d11e7 "Pyrebase fix")
    - edit *pyrebase.py* usually found here: */home/pi/.local/lib/python2.7/site-packages/pyrebase/pyrebase.py*
7. Install ffmpeg: `sudo apt-get install ffmpeg`
8. Get brainyant FireAnt package: `git clone https://github.com/BrainyAnt/FireAnt.git`

## Usage

1. Sign in or regster on [BrainyAnt](http://www.brainyant.com "Robots.Unite")
2. Create a new robot entry for your Raspberry Pi
3. Download the __auth.json__ file
4. Copy __auth.json__ to FireAnt folder
5. Edit __robot.py__
6. Run robot.py: `python robot.py` or simply `./robot.py`

## Feedback

Give us feedback, inform us of any issues or troubleshooting. [Contact](http://www.brainyant.com/contact) us or send us an email at *contact@brainyant.com*
