#!/usr/bin/env python3

import random
from fireant import FireAnt
import userControl as UC        # use a custom control library

# Examples of user defined functions

def light_on():
    print("Light is ON")
    pass


def light_off():
    print("Light is OFF")
    pass


def light_switch():
    print("Light SWITCH")
    pass


def light_reader():
    return random.randint(1, 501)


def temperature_reader():
    return random.randint(-101, 101)


def distance_reader():
    return random.randint(0, 1001)


if __name__ == '__main__':
    try:
        myAnt = FireAnt('auth.json')
        print(myAnt.get_name())
        print(myAnt.get_description())

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor("light", light_reader)
        myAnt.add_sensor("temperature", temperature_reader)
        myAnt.add_sensor("distance", distance_reader)
        # myAnt.remove_sensor(name)

        # myAnt.add_command(name, callback, key, behavior)
        myAnt.add_command('fwd', UC.move_forward, 'W', "hold")
        myAnt.add_command('left', UC.move_left, 'A', "hold")
        myAnt.add_command('right', UC.move_right, 'D', "hold")
        myAnt.add_command('back', UC.move_back, 'S', "hold")
        myAnt.add_command('light', light_switch, 'f', "press")
        # myAnt.remove_command(name)

    except KeyboardInterrupt:
        print("Interrupted by owner")