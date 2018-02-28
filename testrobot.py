#!/usr/bin/env python3

import random
import time
from fireant import FireAnt


def userControlHandler(message):

    # ControlData   [PROPOSED]
    # motor:
    #   cw    [0-100]
    #   ccw   [0-100]
    # dual motor:
    #   fwd   [0-100]
    #   back  [0-100]
    #   left  [0-100]
    #   right [0-100]
    # led:
    #   ON/OFF[0/1]
    # servo:
    #   angle [0-360]

    if type(message["data"]).__name__ == 'dict':
        if "fwd" in message["data"]:
            if message["data"]["fwd"]>0:
                print("ON")
            else:
                print("OFF")
    elif type(message["data"]).__name__ == 'int':
        if message["path"] == "fwd":
            if message["data"] > 1:
                print("ON")
            else:
                print("OFF")


def lightSensor():
    return random.randint(1,501)


def userSensorFunction1():
    return random.randint(1,501)


def userSensorFunction2():
    return random.randint(1,501)


if __name__ == '__main__':
    try:
        # FLOW:
        # connect to robot
        # setup add/remove sensors/actuators. set key bindings.
        # wait for user
        # start video stream
        # start control stream
        # start sensor stream
        # log session
        # go to "wait for user"

        myAnt = FireAnt('auth.json')
        print(myAnt.get_name())
        print(myAnt.get_description())

        # sensor registered in 'output'
        # sensor
        #   value

        # myAnt.add_sensor(name, callback_function)
        myAnt.add_sensor("light", lightSensor)
        myAnt.add_sensor("sensor1", userSensorFunction1)
        myAnt.add_sensor("sensor2", userSensorFunction2)
        # myAnt.remove_sensor(name)

        # actuators registered in 'input'   [PROPOSED]
        #   actuator:
        #       type  [press, tap, hold]
        #       key   [W, A, S, D, etc.]

        # myAnt.add_actuator(name, pin, function, key)
        # myAnt.remove_actuator(name)
        # myAnt.modify_actuator(name, pin, function, key)

        loop = 0
        while True: # possibly myAnt.is_robot_online
            loop = loop + 1
            print("Loop: {}".format(loop))

            myAnt.start_user_wait()

            myAnt.stream_control_data(userControlHandler)
            myAnt.stream_sensor_data()

            while myAnt.user_online():
                time.sleep(1)
                pass
            
            myAnt.log_session()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by master")
