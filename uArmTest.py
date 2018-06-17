#!/usr/bin/env python3

import random
import os
from fireant import FireAnt
import uf.wrapper.swift_api as sapi

# Examples of user defined functions

swift = sapi.SwiftAPI()

def move_x(xcoord):
    (x, y, z) = swift.get_position()
    swift.set_position(x+xcoord, y, z, speed=200, wait=True)
def move_y(ycoord):
    (x, y, z) = swift.get_position()
    swift.set_position(x, y+ycoord, z, speed=200, wait=True)
def move_z(zcoord):
    (x, y, z) = swift.get_position()
    swift.set_position(x, y, z+zcoord, speed=200, wait=True)

def stretch(scoord):
    (s1,r1,h1) = swift.get_polar()
    swift.set_polar(s=s1+scoord ,speed=200, wait=True)
def rotation(rcoord):
    swift.set_polar(r=r1+rcoord ,speed=200, wait=True)
def height(hcoord):
    swift.set_polar(h=h1+hcoord ,speed=200, wait=True)


if __name__ == '__main__':
    try:
        authfile = open('uArm.json', 'r')
        path = os.path.dirname(os.path.realpath(__file__))
        myAnt = FireAnt(authfile, path, 'stream.sh', 'stream_stop.sh')

        print(myAnt.get_name())
        print(myAnt.get_description())

        # myAnt.add_sensor(name, callback_function)
        
        # myAnt.add_command(name, callback, argument, key, behavior)
        myAnt.add_command("move_x", move_x, 'W', "additive")
        myAnt.add_command("move_x", move_x, 'S', "regressive")
        myAnt.add_command("move_y", move_y, 'A', "additive")
        myAnt.add_command("move_y", move_y, 'D', "regressive")
        myAnt.add_command("move_z", move_z, 'Q', "additive")
        myAnt.add_command("move_z", move_z, 'E', "regressive")
        myAnt.add_command("buzz", swift.set_buzzer, 'H', 'hold')
        myAnt.add_command("pump", swift.set_pump, 'F', 'tap')
        myAnt.add_command("grip", swift.set_gripper, 'G', 'tap')
        # myAnt.remove_command(name)

    except KeyboardInterrupt:
        print("Interrupted by owner")
