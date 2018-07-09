#!/usr/bin/env python3

import random
import os
from fireant import FireAnt
import userControl as UC        # use a custom control library

def my_function(data):
    x=data
    y=x
    # do something with value
    print('x: {}'.format(x))
    print('y: {}'.format(y))

def foo(a,*,b=2):
    print(a)
    print(b)

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

def inc(data):
    print(data)

def dec(data):
    print(data)

if __name__ == '__main__':
    try:
        authfile = open('private.json', 'r')
        path = os.path.dirname(os.path.realpath(__file__))
        myAnt = FireAnt(authfile, path, 'stream.sh', 'stream_stop.sh')

        print(myAnt.get_name())
        print(myAnt.get_description())

        myAnt.set_control_time(120)

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor('Light', light_reader)
        myAnt.add_sensor('Temperature', temperature_reader)
        myAnt.add_sensor('Distance', distance_reader)
        # myAnt.remove_sensor(name)

        # myAnt.add_command(name, callback, key, behavior)
        # press, hold, tap, additive, regressive
        myAnt.add_command('pos', inc, 'W', "additive")
        myAnt.add_command('pos', inc, 'S', "regressive")
        myAnt.add_command('pos', inc, 'R', "tap")
        myAnt.add_command('pos', inc, 'T', "switch")
        myAnt.add_command('pos', inc, 'H', "press")
        myAnt.add_command('light', light_switch, 'l', 'switch')
        # myAnt.remove_command(name)

    except KeyboardInterrupt:
        print("Interrupted by owner")