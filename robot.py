#!/usr/bin/env python

# Import modules.
import random
from fireant import FireAnt

# GPIO setup

# User implemented functions
def userFunction(args):
    #do stuff
    value = args
    return value

def readSensor1():
    #get sensor data
    return 100

def readSensor2():
    #another user defined sensor reading function
    return random.randint(1,501)

# main part
if __name__ == '__main__':
    try:
        # STEP1 create a FireAnt object. This registers with the platform and sets the robot online.
        myAnt = FireAnt('auth.json')

        # STEP2 (optional) get information about your robot
        print(myAnt.is_robot_online())
        print(myAnt.get_name())
        print(myAnt.get_description())

        while myAnt.is_robot_online():

            # STEP4 wait for a user to request control
            print('Waiting for users ...')
            myAnt.wait_for_available_user()
            print('Got user!')

            # as long as the user is online and in control:
            while myAnt.get_useron():
                # STEP5 get control data
                controldata = myAnt.get_control_data()

                # STEP6 do stuff with control data
                userFunction(controldata)

                # STEP7 handle sensors
                # check if sensor reading is requested
                request1 = myAnt.get_sensor_request('sensor1')
                request2 = myAnt.get_sensor_request('sensor_2')

                # send sensor reading to database
                if request1:
                    reading = readSensor1()
                    myAnt.publish_data(("sensor1", reading, False))
                    #myAnt.publish_data( (SENSOR_NAME, READING, REQUEST) )
                if request2:
                    myAnt.publish_data(("sensor_2", readSensor2(), True))

            # STEP8 log session
            myAnt.log_session()
    except KeyboardInterrupt:
        myAnt.log_session()
        print("Interrupted by master")
