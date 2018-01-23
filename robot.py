#!/usr/bin/env python

#import sys
#mport os
#import RPi.GPIO as GPIO
from fireant import FireAnt

#GPIO setup
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

if __name__ == '__main__':
    #register with firebase
    myAnt = FireAnt('auth.json')
    name = myAnt.get_name()
    print(name)
    #repeat
    #get control data
    #do things with it
    #send data to firebase