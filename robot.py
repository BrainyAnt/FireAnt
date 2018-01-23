#!/usr/bin/env python

#import sys
#mport os
#import RPi.GPIO as GPIO
import random
from fireant import FireAnt

#GPIO setup
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

def readSensor1():
    return {"sensor1": {"value": 100, 'request': False}}

def readSensor2():
    return {"sensor_2": {"value": random.randint(1, 101), 'request': True}}

if __name__ == '__main__':
    try:
        myAnt = FireAnt('auth.json')
        while myAnt.is_robot_online():
            myAnt.wait_for_available_user()
            while myAnt.get_useron():
                #get control data
                controldata = myAnt.get_control_data()
                
                #use control data
                for item in controldata['sensors']:
                    print('{}: {}'.format(item, controldata['sensors'][item]))
                print()
                
                #get sensor reading
                readSensor1()
                
                #send sensor reading
                request1 = controldata['sensors']['sensor1']['request']
                if request1:
                    myAnt.publish_data(readSensor1())
            
                request2 = controldata['sensors']['sensor_2']['request']
                if request2:
                    myAnt.publish_data(readSensor2())
                #end control
            #log session
            myAnt.log_session()
    except KeyboardInterrupt:
        print("Interrupted by owner")