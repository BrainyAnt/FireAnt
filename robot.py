#!/usr/bin/env python3

import random
import time
from fireant import FireAnt

MOTOR11 = 9
MOTOR12 = 10
MOTOR21 = 22
MOTOR22 = 23
LIGHT = 17


def go_forward(speed):
    pass


def go_backward(speed):
    pass


def go_right(speed):
    pass


def go_left(speed):
    pass


def stop():
    pass


def light_on():
    pass


def light_off():
    pass


def light_switch():
    pass


def user_control_handler(message):
    # message["data"] = {"fwd"}
    if type(message["data"]).__name__ == 'dict':
        if "fwd" in message["data"]:
            if message["data"]["fwd"] > 0:
                print("ON")
            else:
                print("OFF")
    elif type(message["data"]).__name__ == 'int':
        if message["path"] == "fwd":
            if message["data"] > 1:
                print("ON")
            else:
                print("OFF")


def light_sensor():
    return random.randint(1, 501)


def user_sensor_function1():
    return random.randint(1, 501)


def user_sensor_function2():
    return random.randint(1, 501)


if __name__ == '__main__':
    try:

        # FLOW:
        # connect to robot
        # setup add/remove sensors/actuators. set key bindings.
        # wait for user
        # start video stream (automatically)
        # start control stream (listen for control commands)
        # start sensor stream (listen for sensor requests)
        # log session
        # go to "wait for user"

        myAnt = FireAnt('auth.json')
        print(myAnt.get_name())
        print(myAnt.get_description())
        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor("light", light_sensor)
        myAnt.add_sensor("sensor1", user_sensor_function1)
        myAnt.add_sensor("sensor2", user_sensor_function2)
        # myAnt.remove_sensor(name)

        # myAnt.add_actuator(name, pin, function, key)
        # myAnt.remove_actuator(name)
        # myAnt.modify_actuator(name, pin, function, key)

        loop = 0
        while True:  # possibly myAnt.is_robot_online
            loop = loop + 1
            print("Loop: {}".format(loop))
            myAnt.start_user_wait()
            myAnt.stream_control_data(user_control_handler)
            myAnt.stream_sensor_data()
            while myAnt.user_online():
                time.sleep(1)
                pass

            myAnt.log_session()

    except KeyboardInterrupt:
        print("Interrupted by master")
