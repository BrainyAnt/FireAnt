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
2. Python 3
3. pip3
4. RPi.GPIO

## Installation

1. Install Raspbian [Stretch](https://www.raspberrypi.org/downloads/raspbian/) OS on a microSD card
2. Connect Raspberry Pi to WiFi network ( [how to guide](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md "SETTING UP WIFI VIA THE COMMAND LINE") )
3. Enable Raspicam: `sudo raspi-config`
    - Navigate to "Interfacing Options"
    - Select "Camera"
    - Reboot
4. Check Python version: `python3 -V`
    - If python is not installed, install it via: `sudo apt-get install python3`
5. Get Pyrebase: `python3 -m pip install Pyrebase`
6. If RPi.GPIO is not installed, install it via: `pip3 install RPi.GPIO`
6. Install ffmpeg: `sudo apt-get install ffmpeg`
7. Install brainyant FireAnt package: `git clone https://github.com/BrainyAnt/FireAnt.git`

## Usage

1. Sign in or register on [BrainyAnt](http://www.brainyant.com "Robots.Unite")
2. Create a new robot entry for your Raspberry Pi
3. Download the __auth.json__ file from the platform
4. Copy __auth.json__ to FireAnt folder
5. Edit __robot.py__
6. Run __robot.py__: `python robot.py` or simply `./robot.py`

## Feedback

Give us feedback, inform us of any issues or troubleshooting. [Contact](http://www.brainyant.com/contact) us or send us an email at *contact@brainyant.com*
