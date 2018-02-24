#!/usr/bin/env python3

import time
import random
import sys
from fireant import FireAnt

def userControlHandler(message):
    if type(message["data"]).__name__ == 'dict':
        if "fwd" in message["data"]:
            if message["data"]["fwd"]>0:
                print("ON")
            else:
                print("OFF")
    elif type(message["data"]).__name__ == 'int':
        if message["path"] == "fwd":
            if message["data"] > 1:
                print("ON")
            else:
                print("OFF")

def lightSensor():
    return random.randint(1,501)

def userSensorFunction1():
    return random.randint(1,501)

def userSensorFunction2():
    return random.randint(1,501)

if __name__ == '__main__':
    try:
        # FLOW:
        # connect to robot
        # setup add/remove sensors/actuators. set key bindings.
        # wait for user
        # start video stream
        # start control stream
        # start sensor stream
        # log session
        # go to "wait ..." 

        myAnt = FireAnt('auth.json')
        print(myAnt.get_name())
        print(myAnt.get_description())

        myAnt.add_sensor("light", lightSensor)
        myAnt.add_sensor("sensor1", userSensorFunction1)
        myAnt.add_sensor("sensor2", userSensorFunction2)

        #myAnt.add_sensor(name, callback_function)
        #myAnt.remove_sensor(name)
        #myAnt.update_sensor(name, value)
        
        #myAnt.add_actuator(name, pin, function, key)
        #myAnt.remove_actuator(name)
        #myAnt.modify_actuator(name, pin, function, key)

        while True: #possibly myAnt.is_robot_online
            print('Waiting for users ...')
            myAnt.wait_for_users()
            print('Got user!')

            myAnt.stream_control_data(userControlHandler)
            myAnt.stream_sensor_data()

            while myAnt.user_online():
                pass
            
            myAnt.log_session()

    except KeyboardInterrupt:
        myAnt.log_session()
        print("Interrupted by master")
