#!/usr/bin/env python3

import random
import os
from fireant import FireAnt
import uf.wrapper.swift_api as sapi

# Examples of user defined functions

swift = sapi.SwiftAPI()

def move_x(xcoord):
    (x, y, z) = swift.get_position()
    swift.set_position(xcoord, y, z, speed=200, wait=True)
def move_y(ycoord):
    swift.set_position(y=ycoord, speed=200, wait=True)
def move_z(zcoord):
    swift.set_position(z=zcoord, speed=200, wait=True)

def stretch(scoord):
    swift.set_polar(s=scoord ,speed=200, wait=True)
def rotation(rcoord):
    swift.set_polar(r=rcoord ,speed=200, wait=True)
def height(hcoord):
    swift.set_polar(h=hcoord ,speed=200, wait=True)


if __name__ == '__main__':
    try:
        authfile = open('uArm.json', 'r')
        path = os.path.dirname(os.path.realpath(__file__))
        myAnt = FireAnt(authfile, path, 'stream.sh', 'stream_stop.sh')

        print(myAnt.get_name())
        print(myAnt.get_description())

        # myAnt.add_sensor(name, callback_function)
        
        # myAnt.add_command(name, callback, argument, key, behavior)
        myAnt.add_command("move_x", move_x, 'x', 'W', "additive")
        myAnt.add_command("move_x", move_x, 'x', 'S', "regressive")
        myAnt.add_command("buzz", swift.set_buzzer, 'on', 'H', 'hold')
        myAnt.add_command("pump", swift.set_pump, 'on', 'G', 'tap')
        # myAnt.remove_command(name)

    except KeyboardInterrupt:
        print("Interrupted by owner")