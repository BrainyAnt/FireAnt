#!/usr/bin/env python3

import random
import os
#from fireant import FireAnt
from fireant import FireAnt
import userControl as UC        # use a custom control library

# Examples of user defined functions

def my_function(value):
    # do something with value
    print(value)

def light_on():
    print("Light is ON")


def light_off():
    print("Light is OFF")


def light_switch(value):
    if value:
        light_on()
    else:
        light_off()


def light_reader():
    return random.randint(1, 501)


def temperature_reader():
    return random.randint(-101, 101)


def distance_reader():
    return random.randint(0, 1001)


def hold(value):
    if value:
        print('hold ON')
    else:
        print('hold OFF')


if __name__ == '__main__':
    try:
        authfile = open('auth.json', 'r')
        path = os.path.dirname(os.path.realpath(__file__))
        myAnt = FireAnt(authfile, path, 'stream.sh', 'stream_stop.sh')

        print(myAnt.get_name())
        print(myAnt.get_description())

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor("light", light_reader)
        myAnt.add_sensor("temperature", temperature_reader)
        myAnt.add_sensor("distance", distance_reader)
        # myAnt.remove_sensor(name)

        # myAnt.add_command(name, callback, key, behavior)
        myAnt.add_command('fwd', UC.move_forward, 'W', "press")
        myAnt.add_command('left', UC.move_left, 'A', "press")
        myAnt.add_command('right', UC.move_right, 'D', "press")
        myAnt.add_command('back', UC.move_back, 'S', "press")
        myAnt.add_command('light', light_switch, 'F', "tap")
        myAnt.add_command('hold on', hold, 'h', 'hold')
        # myAnt.remove_command(name)

    except KeyboardInterrupt:
        print("Interrupted by owner")