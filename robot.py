#!/usr/bin/env python
import time
import random
import sys
from fireant import FireAnt

#import RPi.GPIO as GPIO
#headlight = 17
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(headlight, GPIO.OUT)

def userFunction(message):
    if str(type(message["data"])) == "<type 'dict'>":
        if "fwd" in message["data"]:
            if message["data"]["fwd"]>0:
                #GPIO.output(headlight, GPIO.HIGH)
                print("ON")
            else:
                #GPIO.output(headlight, GPIO.LOW)
                print("OFF")
    elif str(type(message["data"])) == "<type 'int'>":
        if message["path"] == "fwd":
            if message["data"] > 1:
                #GPIO.output(headlight, GPIO.HIGH)
                print("ON")
            else:
                #GPIO.output(headlight, GPIO.LOW)
                print("OFF")



def readSensor1():
    #get sensor data
    return random.randint(1,501)

if __name__ == '__main__':
    try:
        myAnt = FireAnt('auth.json')

        print(myAnt.get_name())
        print(myAnt.get_description())
        
        while True:
            print('Waiting for users ...')
            myAnt.wait_for_available_user()
            print('Got user!')
            
            myAnt.stream_control_data(userFunction) 
            
            while myAnt.get_useron():
                sys.stdout.write("ON \r")

            myAnt.log_session()

    except KeyboardInterrupt:
        myAnt.log_session()
        print("Interrupted by master")
