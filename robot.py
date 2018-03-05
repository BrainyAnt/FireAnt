#!/usr/bin/env python3

import random
from fireant import FireAnt
import furnicaControl as UC

# User defined functions

def light_on():
    pass


def light_off():
    pass


def light_switch():
    pass


def light_sensor():
    return random.randint(1, 501)


def user_sensor_function1():
    return random.randint(1, 501)


def user_sensor_function2():
    return random.randint(1, 501)


def user_control_handler(message):
    print(message['data'])
    # Example: message["data"] = {"fwd": 24}
    fwd, back, left, right = (message['data']['fwd'], message['data']['back'], message['data']['left'], message['data']['right'])
    UC.runMotors(fwd, back, left, right)


if __name__ == '__main__':
    try:
        UC.init()
        UC.start()
        myAnt = FireAnt('auth.json', user_control_handler)
        print(myAnt.get_name())
        print(myAnt.get_description())

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor("light", light_sensor)
        myAnt.add_sensor("sensor1", user_sensor_function1)
        myAnt.add_sensor("sensor2", user_sensor_function2)
        # myAnt.remove_sensor(name)

    except KeyboardInterrupt:
        print("Interrupted by owner")
        pass
    UC.stop()
    UC.clear()