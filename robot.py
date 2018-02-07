#!/usr/bin/env python
import time
import random
from fireant import FireAnt
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

headlight = 17
GPIO.setup(headlight, GPIO.OUT)

def userFunction(message):
    print(message["data"])
    try:
        print(message["data"]["fwd"])
    except Exception:
        pass
    if str(type(message["data"])) == "<type 'dict'>":
        if "fwd" in message["data"]:
            if message["data"]["fwd"]>0:
                GPIO.output(headlight, GPIO.HIGH)
            else:
                GPIO.output(headlight, GPIO.LOW)
    elif str(type(message["data"])) == "<type 'int'>":
        if message["path"] == "fwd":
            if message["data"] > 1:
                GPIO.output(headlight, GPIO.HIGH)
            else:
                GPIO.output(headlight, GPIO.LOW)



def readSensor1():
    #get sensor data
    return random.randint(1,501)

if __name__ == '__main__':
    try:
        myAnt = FireAnt('auth.json')
        
        print(myAnt.is_robot_online())
        print(myAnt.get_name())
        print(myAnt.get_description())
        
        while True:
            print('Waiting for users ...')
            myAnt.wait_for_available_user()
            print('Got user!')
            
            myAnt.stream_control_data(userFunction) 
            
            while myAnt.get_useron():
    	        myAnt.publish_data(("sensor", random.randint(1,100), True))
    	        time.sleep(random.randint(1,10))
            
            myAnt.close_stream()
            myAnt.log_session()

    except KeyboardInterrupt:
        myAnt.log_session()
        print("Interrupted by master")
