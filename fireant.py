#!/usr/bin/env python

import os
import sys
import sched
from threading import Thread
import time
import json
import urllib2
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
            REQUEST = urllib2.Request('https://robots.brainyant.com:8080/robotLogin')
            REQUEST.add_header('Content-Type', 'application/json')
            RESPONSE = urllib2.urlopen(REQUEST, json.dumps(AUTH_DATA))
            TOKEN = json.loads(RESPONSE.read())['customToken']
            if TOKEN is None:
                raise TokenRequestError
        except TokenRequestError:
            print('Error! Could not retreive signin token from server. Server might be down.')
            sys.exit(222)
        
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

        self.__database = DB
        self.__idToken = IDTOKEN
        self.__ownerID = AUTH_DATA["ownerID"]
        self.__robotID = AUTH_DATA["robotID"]

        try:
            self.__parathread = Thread(target = self.__start_still_alive_every_n_secs, args = [2])
            self.__parathread.daemon = True
            self.__parathread.start()
        except KeyboardInterrupt:
            sys.stdout.write("Killed (not still alive) 111")
            print('Killed (not still alive)')

    def __start_stream(self):
        """Start stream"""
        try:
            camera = self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('profile').child('stream').get(token=self.__idToken).val()
            secretkey = self.__database.child('users').child(self.__ownerID).child('cameras').child(camera).child('secretKey').get(token=self.__idToken).val()
            streamparam = self.__ownerID + '/' + camera + '/' + secretkey
            path = os.path.dirname(os.path.realpath(__file__))
            subprocess.call([path + '/stream.sh', streamparam])
            #subprocess.call(["raspivid -w 800 -h 500 -fps 10 -vf -hf -cd MJPEG -t 0 -o - | ffmpeg -loglevel panic -i - -f mpegts -codec:v mpeg1video -s 800x500 -b:v 750k https://robots.brainyant.eu:8080/$1", streamparam], shell=True)
        except IOError:
            print("ERROR: Stream unable to start")
            sys.exit(3)

    def __stop_stream(self):
        """Stop stream"""
        #path = os.path.dirname(os.path.realpath(__file__))
        #subprocess.call([path + '/stream_stop.sh'])
        subprocess.call(['kill -9 $(pgrep raspivid)'], shell=True)
        print("KILLED STREAM")

    def get_name(self):
        """Return robot name"""
        name = self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('profile').child('name').get(token=self.__idToken).val()
        return name

    def get_description(self):
        """Return robot description"""
        description = self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('profile').child('description').get(token=self.__idToken).val()
        return description
        
    def __set_robot_offline(self):
        """Set field value of isOnline to False"""
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('profile').update({'isOnline': False}, token=self.__idToken)

    def is_robot_online(self):
        """Return field value of isOnline"""
        return self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('profile').child('isOnline').get(token=self.__idToken).val()

    def __get_first_user(self):
        """Get first user information"""
        (uid, useron, user_entry) = (None, None, None)
        firstuser = self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queue').order_by_key().limit_to_first(1).get(token=self.__idToken)
        try:
            for i in firstuser.each():
                uid = i.val()['uid']
                useron = i.val()['userOn']
                user_entry = i.key()
        except TypeError:
            self.__userID = None
            self.__userOn = None
            self.__userEntry = None
        self.__userID = uid
        self.__userOn = useron
        self.__userEntry = user_entry
        return (user_entry, uid, useron)

    def get_useron(self):
        """Get first user status"""
        try:
            aux = self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queue').order_by_key().limit_to_first(1).get(token=self.__idToken)
            for i in aux.each():
                useron = i.val()['userOn']
        except KeyboardInterrupt:
            sys.exit(2)
        except KeyError:
            print("Missing field: userOn")
            self.__delete_entry()
            useron = False
        return useron

    def __delete_entry(self):
        """Delete bad entry in database"""
        print('deleting bad entry ...')
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queue').child(self.__userEntry).remove(token=self.__idToken)

    def get_control_data(self):
        """Return ControlData values from firebase"""
        user_id = self.__get_first_user()[1]
        try:
            return self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('users').child(user_id).child("ControlData").order_by_key().get(token=self.__idToken).val()
        except TypeError:
            return None
    
    def __set_robotOn(self):
        """Set robotOn flag to True"""
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queue').child(self.__userEntry).update({"robotOn": True}, token=self.__idToken)

    def __set_startControl(self):
        """Record timestamp when control session starts"""
        timestamp = int(round(time.time()*1000)) #calendar.timegm(time.gmtime())
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queue').child(self.__userEntry).update({"startControl": timestamp}, token=self.__idToken)

    def __get_startControl(self):
        """Return timestamp for start of control session"""
        return self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queue').child(self.__userEntry).child('startControl').get(token=self.__idToken).val()

    def wait_for_available_user(self):
        """Wait for user to show up in queue"""
        # Get UID
        try:
            u_entry = None
            userid = None
            uon = None
            while self.is_robot_online() and userid is None and uon is None:
                (u_entry, userid, uon) = self.__get_first_user()
        except KeyboardInterrupt:
            print("INTERRUPT!")
            sys.exit(0)

        self.__start_stream()
        self.__set_robotOn()
        self.__set_startControl()
        return (u_entry, userid, uon)

    def log_session(self):
        """Log a session to archive after it is over"""
        log_timestamp = int(round(time.time()*1000)) #queue_archive entry: timestamp
        try:
            log_data = {
                log_timestamp: {
                    'uid': self.__userID,
                    'useTime': log_timestamp - self.__get_startControl(),
                    'waitTime': self.__get_startControl() - int(self.__userEntry)
                }
            }
        except ValueError:
            log_data = {
                log_timestamp: {
                    'uid': self.__userID,
                    'useTime': log_timestamp - self.__get_startControl(),
                    'waitTime': None
                }
            }
        except TypeError:
            log_data = {
                log_timestamp: {
                    'uid': self.__userID,
                    'useTime': None,
                    'waitTime': None
                }
            }
        self.__stop_stream()
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queueArchive').update(log_data, token=self.__idToken)
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('queue').child(self.__userEntry).remove(token=self.__idToken)
        self.__userID = None
        self.__userEntry = None
        self.__userOn = None

    def __start_still_alive_every_n_secs(self, n_seconds):
        """Start a recurring function that signals the robot is online every n seconds"""
        try:
            scheduler = sched.scheduler(time.time, time.sleep)
            scheduler.enter(n_seconds, 1, self.__still_alive, (scheduler, n_seconds))
            scheduler.run()
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            #sys.stdout.write('Not still alive!!!')
            print('Not still alive!!!')

    def __still_alive(self, scheduler, n_seconds):
        """Send a signal to the server every n seconds"""
        try:
            iamalive = urllib2.Request('https://robots.brainyant.com:8080/iAmAlive')
            iamalive.add_header('Content-Type', 'application/json')
            urllib2.urlopen(iamalive, json.dumps({'robotID': self.__robotID}))            
            if self.is_robot_online(): #there is a problem here with SSL. 
                scheduler.enter(n_seconds, 1, self.__still_alive, (scheduler, n_seconds))
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not still alive 2!!!')

    def publish_data(self, data):
        """Publish data to database"""
        sensor_name = data[0]
        sensor_value = data[1]
        sensor_request = data[2]
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('users').child(self.__userID).child("ControlData").child("sensors").child(sensor_name).update({'request': sensor_request}, token=self.__idToken)
        self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('users').child(self.__userID).child("ControlData").child("sensors").child(sensor_name).update({'value': sensor_value}, token=self.__idToken)

    def get_sensor_request(self, sensor):
        """Return sensor request"""
        try:
            return self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('users').child(self.__userID).child("ControlData").child("sensors").child(sensor).child('request').get(token=self.__idToken).val()
        except TypeError:
            self.__database.child('users').child(self.__ownerID).child('robots').child(self.__robotID).child('users').child(self.__userID).child("ControlData").child("sensors").child(sensor).update({'request': False}, token=self.__idToken)
            print('Sensor might not be registered')
            return False
