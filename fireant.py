#!/usr/bin/env python3

import os
import sys
import sched
from threading import Thread
import time
import json
import requests
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
    
    def __init__(self, authfile, userControlDataHandler):
        """ Register with firebase using authentication data. Return database reference, toke, and userID """
        self._authfile = authfile
        AUTH, AUTH_DATA, DB, USER_DATA, IDTOKEN = self._firebase_sign_in(self._authfile)
        
        self._userData = USER_DATA
        self._auth = AUTH
        self._database = DB
        self._idToken = IDTOKEN
        self._ownerID = AUTH_DATA["ownerID"]
        self._robotID = AUTH_DATA["robotID"]
        
        self._userEntry = None
        self._userID = None
        self._userOn = None
        
        self._video_stream = None
        
        self._my_control_stream = None
        self._my_sensor_stream = None
        self._my_user_stream = None
        
        self._sensor_list = {}
        self._command_list = {}
        
        # Start a new thread with the "still_alive" recurrent function
        self._parathread = Thread(target = self._start_still_alive_every_n_secs, args = [3])
        self._parathread.daemon = True
        self._parathread.start()

        # Start a new thread with the "token refresh" recurrent function
        self._parathread2 = Thread(target = self._start_token_refresh, args = [1800])
        self._parathread2.daemon = True
        self._parathread2.start()

        # Start waiting for users in a new thread
        print('Main loop')
        self._mainloop_thread = Thread(target = self._main_loop, args = [userControlDataHandler])
        self._mainloop_thread.start()
        print('After main loop')

    def _firebase_sign_in(self, authfile):
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
            USER_DATA = AUTH.sign_in_with_custom_token(TOKEN)
            USER_DATA = AUTH.refresh(USER_DATA['refreshToken'])
            USERID = USER_DATA['userId']
            IDTOKEN = USER_DATA['idToken']
            if USERID is None:
                raise InvalidTokenException
        except InvalidTokenException:
            print("Can't sign in to firebase. Invalid token.")
        return (AUTH, AUTH_DATA, DB, USER_DATA, IDTOKEN)
    
    def _refresh_token(self):
        self._userData = self._auth.refresh(self._userData['refreshToken'])
        self._idToken = self._userData["idToken"]

    def _main_loop(self, userControlDataHandler):
        try:
            while True:                                 # maybe replace with myAnt.is_robot_online
                self._start_user_wait()
                self._stream_control_data(userControlDataHandler)
                self._stream_sensor_data()
                #self.stream_commands()
                while self.user_online():
                    pass
                self._log_session()
        except KeyboardInterrupt:
            print("Main loop interrupted by keyboard.")

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
            self._delete_entry(self._userEntry)
            useron = False
        return useron

    def _delete_entry(self, entry):
        """Delete bad entry in database"""
        print('deleting bad entry ...')
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(entry).remove(token=self._idToken)

    def get_control_data(self):
        """Return ControlData values from firebase"""
        # user_id = self._get_first_user()[1]
        try:
            return self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("ControlData").order_by_key().get(token=self._idToken).val()
        except TypeError:
            return None

    def get_sensor_data(self):
        """Return ControlData values from firebase"""
        # user_id = self._get_first_user()[1]
        try:
            return self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("SensorData").order_by_key().get(token=self._idToken).val()
        except TypeError:
            return None

    def _stream_control_data(self, myControlCallback):
        self._my_control_stream = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("ControlData").stream(myControlCallback, stream_id="control data stream", token=self._idToken)

    def _stream_sensor_data(self):
        self._my_sensor_stream = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("SensorData").stream(self._sensor_handler, stream_id="sensor data stream", token=self._idToken)
    
    def _close_streams(self):
        try:
            if self._my_control_stream:
                self._my_control_stream.close()
            if self._my_sensor_stream:
                self._my_sensor_stream.close()
        except AttributeError:
            print('There is no stream')

    def _handle_user(self, message):
        pass
    
    def _get_first_entry(self):
        try:
            firstuser = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').order_by_key().limit_to_first(1).get(token=self._idToken)
            for i in firstuser.each():
                entry = i.key()
            self._userEntry = entry
            return entry
        except TypeError:
            return None
    
    def _get_first_user(self):
        """Get first user information"""
        (uid, useron, user_entry) = (None, None, None)
        firstuser = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').order_by_key().limit_to_first(1).get(token=self._idToken)
        try:
            for i in firstuser.each():
                uid = i.val()['uid']
                useron = i.val()['userOn']
                user_entry = i.key()
        except (TypeError, KeyError):
            (uid, useron, user_entry) = (None, None, None)
        self._userID = uid
        self._userOn = useron
        self._userEntry = user_entry
        return (user_entry, uid, useron)

    def _get_entry_data_ID(self, user_entry):
        try:
            data = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(user_entry).get(token=self._idToken).val()
            return data['uid']
        except KeyError:
            self._delete_entry(user_entry)
            return None
        except TypeError:
            self._delete_entry(user_entry)
            return None

    def _get_entry_data_ON(self, entry):
        data = self._my_user_stream = self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('queue').child(entry).get(token=self._idToken).val()
        return data['userOn']

    def _start_user_wait(self):
        (user_entry, uid, useron) = (None, None, False)
        
        while user_entry is None:
            user_entry = self._get_first_entry()
        uid = self._get_entry_data_ID(user_entry)

        if uid is None:
            print("bad entry ... deleting")
            self._delete_entry(user_entry)
            self.start_user_wait()
        else:
            print("is user online?")
            while useron is False:
                useron = self._get_entry_data_ON(user_entry)
        print("user is online")
        self._userEntry = user_entry
        self._userID = uid

        self._set_robotOn()
        self._set_startControl()

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

    def _log_session(self):
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
            #self._video_stream = subprocess.Popen(cmd, shell=True)
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
    
    def _start_token_refresh(self, timer):
        try:
            scheduler = sched.scheduler(time.time, time.sleep)
            scheduler.enter(timer, 2, self._token_refresh, (scheduler, timer))
            scheduler.run()
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not refreshing')

    def _token_refresh(self, scheduler, timer):
        """Refresh auth token every 1800 seconds"""
        try:
            print("Refreshing...")
            self._refresh_token()
            scheduler.enter(timer, 2, self._token_refresh, (scheduler, timer))
            print("Refreshed.")
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
        while self.user_online() and self._get_sensor_request(sensor) == "loop":
            self._update_sensor(sensor, reader())
            print("I read the {} sensor!".format(sensor))
            time.sleep(1)
        else:
            self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('users').child(self._userID).child("SensorData").update({sensor: "stop"}, token=self._idToken)
    
    def _sensor_handler(self, message):
        try:
            for s in message["data"]:
                sensor = s
                readType = message["data"][s]
        except TypeError:
            return
        reader = self._sensor_list[sensor]
        if readType == "once":
            self._update_sensor(sensor, reader())
        if readType == "loop":
            r = Thread(target=self._continous_update_sensor, args=[sensor, reader])
            r.start()

    def add_command(self, name, callback, key, behavior):
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('input').update({name: {'key': key, 'behavior': behavior}}, token=self._idToken)
        # Add command to ControlData for each user.
        self._command_list[name]=callback

    def remove_command(self, name):
        self._database.child('users').child(self._ownerID).child('robots').child(self._robotID).child('input').child(name).remove(token=self._idToken)
        del self._command_list[name]

    def change_command(self, name, callback, key, behavior):
        self.remove_command(name)
        self.add_command(name, callback, key, behavior)

    def _command_handler(self, message):
        try:
            for com in message["data"]:
                # Control data should have {cmd: value} -> backend should create entries for each user.

                self._command_list[com](message['data'][com])
        except TypeError:
            return

    # COMING SOON
    #
    # add_actuator/command
    # send to firebase: name, key, behavior
    # actuator key binding
    # actuator type in {press, tap, hold}
    # path /users/ownerID/robots/robotID/users/userID/SensorData -> {name: type}
    # path /users/ownerID/robots/robotID/profile/Actuators -> {name: {key: ikey, type: itype}}
