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
    return 100

def readSensor2():
    return random.randint(1, 101)

if __name__ == '__main__':
    try:
        myAnt = FireAnt('auth.json')
        
        while myAnt.is_robot_online():
            
            #wait for a user to request control
            myAnt.wait_for_available_user()
            
            while myAnt.get_useron():
                #get control data
                controldata = myAnt.get_control_data()
                
                #do stuff control data
                
                #get sensor reading
                reading = readSensor1()
                
                #send sensor reading
                request1 = controldata['sensors']['sensor1']['request']
                if request1:
                    myAnt.publish_data( ("sensor1", reading, False) )
            
                request2 = controldata['sensors']['sensor_2']['request']
                if request2:
                    myAnt.publish_data(("sensor_2", readSensor2(), True))
            
            #log session
            myAnt.log_session()
    
    except KeyboardInterrupt:
        print("Interrupted by master")