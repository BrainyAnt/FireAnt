#!/usr/bin/env python3

import random
import time
from fireant import FireAnt

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

# My setup
# Actuators
#   MOTOR1 = (<PIN>, <PIN>)
#   MOTOR2 = (<PIN>, <PIN>)
#   SERVO1 = <PIN_PWM>
#   LED1 = <PIN>
# Sensors
#   TEMP = <PIN>
#   LIGHT = <PIN>

# My functions
# Actuators
#   run_motor1_function()
#   run_motor2_function()
#   run_servo1_function()
#   switch_LED1_function()
# Sensor
#   read_TEMP_function()
#   read_LIGHT_function()
# Commands/Actions          [COMING SOON]
#   move_forward()          [COMING SOON]
#   switch_light()          [COMING SOON]
#   read_temperature()      [COMING SOON]


def userControlDataHandler(message):
    # get TYPE, NAME, VALUE/S
    # message['data']->type->name->value
    # for devType in message['data']:
    #    devices = message['data'][devType]
    #    for devName in devices:
    #        switcher = {
    #            "motor1": run_motor1
    #            "motor2": run_motor2
    #            "servo1": run_servo1
    #            "led1": switch_LED1
    #        }
    #        func = switcher.get(devName, lambda: "INVALID")
    #        func(devices[devName])

    # if type(message["data"]).__name__ == 'dict':
    if "fwd" in message["data"]:
        if message["data"]["fwd"]>0:
            print("dictON")
        else:
            print("dictOFF")

    # elif type(message["data"]).__name__ == 'int':
    #    if message["path"] == "fwd":
    #        if message["data"] > 1:
    #            print("singleON")
    #        else:
    #            print("singleOFF")


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

        myAnt = FireAnt('private.json', userControlDataHandler)

        print(myAnt.get_name())
        print(myAnt.get_description())

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor("light", lightSensor)
        myAnt.add_sensor("sensor1", userSensorFunction1)
        # myAnt.add_sensor("sensor2", userSensorFunction2)

        # myAnt.remove_sensor(name)

        # actuators registered in 'input'   [PROPOSED]
        #   actuator:
        #       type  [press, tap, hold]
        #       key   [W, A, S, D, etc.]

        # myAnt.add_actuator(name, function, key, type) incremental
        # myAnt.remove_actuator(name)
        # myAnt.modify_actuator(name, pin, function, key)

        # COMMANDS
        # TODO Add handling of new action in back-end.
        # add_command (name, key, type)
        # returns [number, T/F, string]
        myAnt.add_command('fwd', move_forward, 'w', "hold")

    except KeyboardInterrupt:
        print("Interrupted by master")
