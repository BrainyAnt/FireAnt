#!/usr/bin/env python3

import random
import time
from fireant import FireAnt
import testControl

    # ControlData   [PROPOSED]      | input     [PROPOSED]                                          |
    #-------------------------------+---------------------------------------------------------------+
    # motor:                        | motor:                                                        |
    #   motor1: [-100,100]          |   motor1: keys:   {cw: Q, ccw: A}                             |
    #                               |           type:   [incremental, tap]                          |
    #-------------------------------+---------------------------------------------------------------+
    # dual motor setup:             | dual motor setup:                                             |
    #   fwd     [0-100]             |   keys:   {fwd: UP, back: DOWN, left: LEFT, right: RIGHT}     |
    #   back    [0-100]             |   type:   [hold, tap]                                         |
    #   left    [0-100]             |                                                               |
    #   right   [0-100]             |                                                               |
    #-------------------------------+---------------------------------------------------------------|
    # led:                          | led:                                                          |
    #   led1    [0/1]               |   led1    key:    [F]                                         |
    #                               |           type:   [press, tap]                                |
    #   led2    [0/1]               |   led2    key:    [L]                                         |
    #                               |           type:   [press, tap]                                |
    #-------------------------------+---------------------------------------------------------------|
    # servo:                        | servo:                                                        |
    #   servo1  [0-360]             |   servo1  key:    {inc: P, dec: O}                            |
    #                               |           type:   [tap]                                       |
    #-------------------------------+---------------------------------------------------------------+

def lightSensor():
    return random.randint(1,501)


def userSensorFunction1():
    return random.randint(1,501)


def userSensorFunction2():
    return random.randint(1,501)


def move_forward():
    print("FORWARD")


if __name__ == '__main__':
    try:
        # FLOW:
        # init object
        #   connect to robot
        #   wait for user
        #   start video stream
        #   start control stream
        #   start sensor stream
        #   log session
        #   go to "wait for user"
        # setup: add/remove sensors/actuators (future: action/commands). set key bindings.

        myAnt = FireAnt('private.json')

        print(myAnt.get_name())
        print(myAnt.get_description())

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor("light", lightSensor)
        myAnt.add_sensor("sensor1", userSensorFunction1)
        # myAnt.remove_sensor(name)

        myAnt.add_command('fwd', move_forward, 'W', "hold")
        myAnt.add_command('init', testControl.init, 'I', "tap")
        myAnt.add_command('stop', testControl.stop, 'S', "tap")

    except KeyboardInterrupt:
        print("Interrupted by master")
