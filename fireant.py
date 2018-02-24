#!/usr/bin/env python3

import os
import sys
import sched
from threading import Thread
import time
import json
import requests
import signal
import subprocess
import pyrebase

# Exception class definition
class TokenRequestError(Exception):
    """Could not retreive token exception."""
    pass
class InvalidTokenException(Exception):
    """Received invalid authentication token exception."""
    pass

class FireAnt:
    """The BrainyAnt firebase communication class"""
    
    def __init__(self, authfile):    
        """ Register with firebase using authentication data. Return database reference, toke, and userID """
        
        FIREBASE_CONFIG = {
            "apiKey": "AIzaSyDC23ZxJ7YjwVfM0BQ2o6zAtWinFrxCrcI",
            "authDomain": "brainyant-2e30d.firebaseapp.com",
            "databaseURL": "https://brainyant-2e30d.firebaseio.com/",
            "storageBucket": "gs://brainyant-2e30d.appspot.com/"
        }
        
        FIREBASE = pyrebase.initialize_app(FIREBASE_CONFIG)
        AUTH = FIREBASE.auth()
        DB = FIREBASE.database()
        
        try:
            DIR = os.path.dirname(os.path.realpath(__file__))
            AUTH_DATA = json.load(open(DIR + '/' + authfile))
        except IOError:
            print("Config file not found!")
            sys.exit(400)

        try:
            payload = json.dumps(AUTH_DATA)
            headers={'content-type': 'application/json'}
            req = requests.post('https://robots.brainyant.com:8080/robotLogin', data=payload, headers=headers)
            TOKEN = req.json()['customToken']
            if TOKEN is None:
                raise TokenRequestError
        except TokenRequestError:
            print("Can't sign in to firebase. Invalid token.")
        
        try:
            USERID = None
            USER_DATA = AUTH.sign_in_with_custom_token(TOKEN)
            FRESH_DATA = AUTH.refresh(USER_DATA['refreshToken'])
            USERID = FRESH_DATA['userId']
            IDTOKEN = FRESH_DATA['idToken']
            if USERID is None:
                raise InvalidTokenException
        except InvalidTokenException:
            print("Can't sign in to firebase. Invalid token.")

        self._userData = USER_DATA
        self._auth = AUTH
        self._database = DB
        self._idToken = IDTOKEN
        self._ownerID = AUTH_DATA["ownerID"]
        self._robotID = AUTH_DATA["robotID"]
        
        self._userEntry = None
        self._userID = None
        self._userOn = None
        self._streamproc = None
        self._my_control_stream = None
        self._my_sensor_stream = None
        self._sensor_list = {}
        
        #Start a new thread with the "still_alive" recurrent function
        self._parathread = Thread(target = self._start_still_alive_every_n_secs, args = [2])
        self._parathread.daemon = True
        self._parathread.start()

        #self._parathread2 = Thread(target = self._start_half_hour_refresh, args = [1])
        #self._parathread2.daemon = True
        #self._parathread2.start()

    def get_name(self):
        """Return robot name"""
        name = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('profile').child('name').get(token=self._idToken).val()
        return name

    def get_description(self):
        """Return robot description"""
        description = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('profile').child('description').get(token=self._idToken).val()
        return description
        
    def _set_robot_offline(self):
        """Set field value of isOnline to False"""
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('profile').update({'isOnline': False}, token=self._idToken)

    def robot_online(self):
        """Return field value of isOnline"""
        return self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('profile').child('isOnline').get(token=self._idToken).val()

    def _get_first_user(self):
        """Get first user information"""
        (uid, useron, user_entry) = (None, None, None)
        firstuser = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').order_by_key().limit_to_first(1).get(token=self._idToken)
        try:
            for i in firstuser.each():
                uid = i.val()['uid']
                useron = i.val()['userOn']
                user_entry = i.key()
        except TypeError:
            (uid, useron, user_entry) = (None, None, None)
        self._userID = uid
        self._userOn = useron
        self._userEntry = user_entry
        return (user_entry, uid, useron)

    def user_online(self):
        """Get first user status"""
        try:
            aux = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').order_by_key().limit_to_first(1).get(token=self._idToken)
            for i in aux.each():
                useron = i.val()['userOn']
        except TypeError:
	        print("No user in queue")
	        useron = False
        except KeyboardInterrupt:
            sys.exit(2)
        except KeyError:
            print("Missing field: userOn")
            self._delete_entry()
            useron = False
        return useron

    def _delete_entry(self):
        """Delete bad entry in database"""
        print('deleting bad entry ...')
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(self._userEntry).remove(token=self._idToken)

    def get_control_data(self):
        """Return ControlData values from firebase"""
        #user_id = self._get_first_user()[1]
        try:
            return self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("ControlData").order_by_key().get(token=self._idToken).val()
        except TypeError:
            return None

    def get_sensor_data(self):
        """Return ControlData values from firebase"""
        #user_id = self._get_first_user()[1]
        try:
            return self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("SensorData").order_by_key().get(token=self._idToken).val()
        except TypeError:
            return None

    def stream_control_data(self, myControlCallback):
        self._my_control_stream = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("ControlData").stream(myControlCallback, stream_id="control data stream", token=self._idToken)

    def stream_sensor_data(self):
        self._my_sensor_stream = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("SensorData").stream(self._sensor_handler, stream_id="control data stream", token=self._idToken)

    def _close_streams(self):
        try:
            if self._my_control_stream:
                self._my_control_stream.close()
            if self._my_sensor_stream:
                self._my_sensor_stream.close()
        except AttributeError:
            print('There is no stream')
    
    def _set_robotOn(self):
        """Set robotOn flag to True"""
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(self._userEntry).update({"robotOn": True}, token=self._idToken)

    def _set_startControl(self):
        """Record timestamp when control session starts"""
        timestamp = int(round(time.time()*1000))
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(self._userEntry).update({"startControl": timestamp}, token=self._idToken)

    def _get_startControl(self):
        """Return timestamp for start of control session"""
        return self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(self._userEntry).child('startControl').get(token=self._idToken).val()

    def _get_sensor_request(self, sensor):
        """Return sensor request"""
        return self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("SensorData").child(sensor).get(token=self._idToken).val()

    def wait_for_users(self):
        """Wait for user to show up in queue"""
        #log "ActiveUser" user if any
        try:
            u_entry = None
            userid = None
            uon = None
            while userid is None and uon is None:
                (u_entry, userid, uon) = self._get_first_user()
        except KeyboardInterrupt:
            print("INTERRUPT!")
            sys.exit(0)
        #move current user to "ActiveUser" section
        self._start_video_stream()
        self._set_robotOn()
        self._set_startControl()
        return (u_entry, userid, uon)

    def log_session(self):
        """Log a session to archive after it is over"""
        log_timestamp = int(round(time.time()*1000))
        try:
            log_data = {
                log_timestamp: {
                    'uid': self._userID,
                    'useTime': log_timestamp - self._get_startControl(),
                    'waitTime': self._get_startControl() - int(self._userEntry)
                }
            }
        except ValueError:
            log_data = {
                log_timestamp: {
                    'uid': self._userID,
                    'useTime': log_timestamp - self._get_startControl(),
                    'waitTime': None
                }
            }
        except TypeError:
            log_data = {
                log_timestamp: {
                    'uid': self._userID,
                    'useTime': None,
                    'waitTime': None
                }
            }
        self._close_streams()
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queueArchive').update(log_data, token=self._idToken)
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(self._userEntry).remove(token=self._idToken)
        self._stop_video_stream()
        self._userID = None
        self._userEntry = None
        self._userOn = False

    def _start_video_stream(self):
        """Start stream"""
        try:
            camera = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('profile').child('stream').get(token=self._idToken).val()
            secretkey = self._database.child('users').child(self._ownerID).child('cameras').child(camera).child('secretKey').get(token=self._idToken).val()
            streamparam = self._ownerID + '/' + camera + '/' + secretkey
            path = os.path.dirname(os.path.realpath(__file__))
            cmd = path + '/stream.sh' + ' ' + streamparam
            #self._streamproc = subprocess.Popen(cmd, shell=True)
        except IOError:
            print("ERROR: Stream unable to start")
            sys.exit(3)

    def _stop_video_stream(self):
        """Stop stream"""
        path = os.path.dirname(os.path.realpath(__file__))
        cmd = path + '/stream_stop.sh'
        #subprocess.Popen(cmd, shell=True)
    
    def _start_still_alive_every_n_secs(self, n_seconds):
        """Start a recurring function that signals the robot is online every n seconds"""
        try:
            scheduler = sched.scheduler(time.time, time.sleep)
            scheduler.enter(n_seconds, 1, self._still_alive, (scheduler, n_seconds))
            scheduler.run()
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not still alive!!!')

    def _still_alive(self, scheduler, n_seconds):
        """Send a signal to the server every n seconds"""
        try:
            headers = {'content-type': 'application/json'}
            payload = json.dumps({'ownerID': self._ownerID, 'robotID': self._robotID})
            requests.post('https://robots.brainyant.com:8080/iAmAlive', data=payload, headers=headers)
            #if self.robot_online():
            scheduler.enter(n_seconds, 1, self._still_alive, (scheduler, n_seconds))
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not still alive 2!!!')
            sys.exit(10)
    
    def _start_half_hour_refresh(self, scheduler):
        try:
            scheduler = sched.scheduler(time.time, time.sleep)
            scheduler.enter(1800, 1, self._half_hour_refresh, (scheduler))
            scheduler.run()
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not refreshing')

    def _half_hour_refresh(self, scheduler):
        """Refresh auth token every 1800 seconds"""
        try:
            FRESH_TOKEN = self._auth.refresh(self._userData['refreshToken'])
            self._idToken = FRESH_TOKEN['idToken']
            scheduler.enter(1800, 1, self._half_hour_refresh, (scheduler))
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not still refreshing!!!')
            sys.exit(10)

    def add_sensor(self, name, callback):
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('output').update({name: 0}, token=self._idToken)
        self._sensor_list[name]=callback
    
    def remove_sensor(self, name):
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('output').child(name).remove(token=self._idToken)
        del self._sensor_list[name]

    def _update_sensor(self, name, value):
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('output').update({name: value}, token=self._idToken)

    def _continous_update_sensor(self, sensor, reader):
        while self._get_sensor_request(sensor) == "loop":
            self._update_sensor(sensor, reader())
            time.sleep(1)
    
    def _sensor_handler(self, message):
        for s in message["data"]:
            sensor = s
            readType = message["data"][s]
        reader = self._sensor_list[sensor]
        if readType == "once":
            self._update_sensor(sensor, reader())
        if readType == "loop":
            r = Thread(target=self._continous_update_sensor, args=[sensor, reader])
            r.start()

    #COMING SOON
    #
    # add_actuator
    # send to firebase: name, key
    # actuator type in {on/off, progressive, hold}
    # sensor type in {stop, once, loop}
    # path /users/ownerID/robots/robotID/users/userID/SensorData -> {name: type}
    # path /users/ownerID/robots/robotID/profile/Actuators -> {name: {key: ikey, type: itype}}
