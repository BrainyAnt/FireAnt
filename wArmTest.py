#!/usr/bin/env python3

import random
import os
import time
from fireant.fireant import FireAnt
import uf.wrapper.swift_api as sapi

# Examples of user defined functions

SPEED = 50000
STEP = 1

swift = sapi.SwiftAPI()

def forward(value):
    swift.set_position(STEP if value else 0, 0, 0, speed=SPEED, relative=True, wait=False)
def back(value):
    swift.set_position(-STEP if value else 0, 0, 0, speed=SPEED, relative=True, wait=False)
def left(value):
    swift.set_position(0, STEP if value else 0, 0, speed=SPEED, relative=True, wait=False)
def right(value):
    swift.set_position(0, -STEP if value else 0, 0, speed=SPEED, relative=True, wait=False)
def up(value):
    swift.set_position(0, 0, STEP if value else 0, speed=SPEED, relative=True, wait=False)
def down(value):
    swift.set_position(0, 0, -STEP if value else 0, speed=SPEED, relative=True, wait=False)

def stretch(scoord):
    swift.set_polar(STEP if scoord else 0, 0, 0, speed=SPEED, relative=True, wait=False)
def retract(scoord):
    swift.set_polar(-STEP if scoord else 0, 0, 0, speed=SPEED, relative=True, wait=False)
def rotate_left(rcoord):
    swift.set_polar(0, STEP if rcoord else 0, 0, speed=SPEED, relative=True, wait=False)
def rotate_right(rcoord):
    swift.set_polar(0, -STEP if rcoord else 0, 0, speed=SPEED, relative=True, wait=False)
def upward(hcoord):
    swift.set_polar(0, 0, STEP if hcoord else 0, speed=SPEED, relative=True, wait=False)
def downward(hcoord):
    swift.set_polar(0, 0, -STEP if hcoord else 0, speed=SPEED, relative=True, wait=False)

def wrist_cw(value):
    swift.set_wrist(value)
def wrist_ccw(value):
    swift.set_wrist(value)

def buzz(data):
    if data:
        print('buzz!')
        swift.set_buzzer(1000, 500)

def reset(data):
    if data:
        print('reset')
        swift.reset()

def grip(data):
    print('grip')
    swift.set_gripper()

def pump(data):
    print('pump')
    swift.set_pump(on=data)

def get_wrist_angle():
    return swift.get_servo_angle(3)

def attach_detach_servo(data, servo_id):
    if data:
        swift.set_servo_attach(servo_id)
        print('attaching '+str(servo_id))
    else:
        swift.set_servo_detach(servo_id)
        print('detaching '+str(servo_id))
def attach_detach_servo0(data):
    attach_detach_servo(data, 0)
def attach_detach_servo1(data):
    attach_detach_servo(data, 1)
def attach_detach_servo2(data):
    attach_detach_servo(data, 2)
def attach_detach_servo3(data):
    attach_detach_servo(data, 3)

def get_attach0():
    return swift.get_servo_attach(0)
def get_attach1():
    return swift.get_servo_attach(1)
def get_attach2():
    return swift.get_servo_attach(2)
def get_attach3():
    return swift.get_servo_attach(3)


if __name__ == '__main__':
    
    try:
        authfile = open('uArm.json', 'r')
        path = os.path.dirname(os.path.realpath(__file__))
        myAnt = FireAnt(authfile, path, 'stream.sh', 'stream_stop.sh')

        print(myAnt.get_name())
        print(myAnt.get_description())
        print(swift.get_device_info())
        # print(swift.get_descriptioN())

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor('Moving', swift.get_is_moving)
        myAnt.add_sensor('Position (carthesian)', swift.get_position)
        myAnt.add_sensor('Position (polar)', swift.get_polar)
        myAnt.add_sensor('Wrist angle', get_wrist_angle)
        myAnt.add_sensor('Servo angles', swift.get_servo_angle)
        myAnt.add_sensor('Wrist angle', get_wrist_angle)
        myAnt.add_sensor('Servo 0', get_attach0)
        myAnt.add_sensor('Servo 1', get_attach1)
        myAnt.add_sensor('Servo 2', get_attach2)
        myAnt.add_sensor('Servo 3', get_attach3)
        # myAnt.remove_sensor(name)

        # myAnt.add_command(name, callback, key, behavior)
        myAnt.add_command('Forward', forward, 'W', 'hold')
        myAnt.add_command('Back', back, 'S', 'hold')
        myAnt.add_command('Left', left, 'A', 'hold')
        myAnt.add_command('Right', right, 'D', 'hold')
        myAnt.add_command('Up', up, 'E', 'hold')
        myAnt.add_command('Down', down, 'Q', 'hold')
        myAnt.add_command('Stretch', stretch, 'I', 'hold')
        myAnt.add_command('Retract', retract, 'K', 'hold')
        myAnt.add_command('Rotate_L', rotate_left, 'J', 'hold')
        myAnt.add_command('Rotate_R', rotate_right, 'L', 'hold')
        myAnt.add_command('Upward', upward, 'O', 'hold')
        myAnt.add_command('Downward', downward, 'U', 'hold')
        myAnt.add_command('Reset', reset, 'R', 'tap')
        myAnt.add_command('Pump', pump, 'F', 'switch')
        myAnt.add_command('Buzz', buzz, 'H', 'switch')
        myAnt.add_command('Wrist', wrist_cw, 'X', 'additive')
        myAnt.add_command('Wrist', wrist_cw, 'Z', 'regressive')
        # myAnt.add_command('Attach_detach_servo_0', attach_detach_servo0, 'U', 'switch')
        # myAnt.add_command('Attach_detach_servo_1', attach_detach_servo1, 'I', 'switch')
        # myAnt.add_command('Attach_detach_servo_2', attach_detach_servo2, 'O', 'switch')
        # myAnt.add_command('Attach_detach_servo_3', attach_detach_servo3, 'P', 'switch')

    except KeyboardInterrupt:
        print("Interrupted by owner")
