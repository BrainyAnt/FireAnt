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

def userSensorHandler(message):
    print("SENSOR CHANGE")
    switcher = {
        "sensor1": userSensorFunction1,
        "sensor2": userSensorFunction2,
    }
    func = switcher.get(message["path"],"nothing")
    return func(message["data"])

def userSensorFunction1():
    # read sensor
    # publish sensor
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

        #myAnt.addsensor(name, pin, function, key)
        #myAnt.removesensor(name)
        #myAnt.modfifysensor(name, pin, function, key)
        #myAnt.addactuator(name, pin, function, key)
        #myAnt.removeactuator(name)
        #myAnt.modfifyactuator(name, pin, function, key)

        while True: #possibly myAnt.is_robot_online
            print('Waiting for users ...')
            myAnt.wait_for_available_user()
            
            print('Got user!')
            myAnt.stream_control_data(userControlHandler)
            myAnt.stream_sensor_data(userSensorHandler)
            #myAnt.register_sensor(name, pin, function)
            #myAnt.stream_sensor_requests()
            while myAnt.get_useron():
                pass
            myAnt.log_session()

    except KeyboardInterrupt:
        myAnt.log_session()
        print("Interrupted by master")
