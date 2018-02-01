#!/usr/bin/env python

import os
import sys
import sched
#from multiprocessing import Process
from threading import Thread
import time
import json
import urllib2
import pyrebase
import subprocess, signal
#import requests

# Exception class definition
class TokenRequestError(Exception):
    """Could not retreive token exception."""
    pass
class InvalidTokenException(Exception):
    """Received invalid authentication token exception."""
    pass

class FireAnt:
    """The BrainyAnt firebase communication class"""
    #members
    #database
    #idToken
    #userID
    #ownerID
    #robotID
    #userOn
    #userEntry
    #scheduler
    #event
    #streamproc
    #streamPID

    #methods
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
            sys.exit()
        
        #try:
        #    payload =  json.dumps(AUTH_DATA)
        #    headers = {'Content-Type': 'application/json'}
        #    r = requests.get('https://robots.brainyant.com:8080/robotLogin', params = payload, headers = headers)
        #    TOKEN = r.json()
        #    print(TOKEN)
        #except TokenRequestError:
        #    print('ERROR getting token')
        
        try:
            REQUEST = urllib2.Request('https://robots.brainyant.com:8080/robotLogin')
            REQUEST.add_header('Content-Type', 'application/json')
            RESPONSE = urllib2.urlopen(REQUEST, json.dumps(AUTH_DATA))
            TOKEN = json.loads(RESPONSE.read())['customToken']
            if TOKEN is None:
                raise TokenRequestError
        except TokenRequestError:
            print('Error! Could not retreive signin token from server. Server might be down.')
        
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

        self.database = DB
        self.idToken = IDTOKEN
        self.ownerID = AUTH_DATA["ownerID"]
        self.robotID = AUTH_DATA["robotID"]

        self.start_stream()
        print('Action.')
        print(self.streamPID)
        try:
            self.parathread = Thread(target = self.start_still_alive_every_n_secs, args = [2])
            self.parathread.start()
            #paraproc = Process(target = self.start_still_alive_every_n_secs, args = [2])
            #paraproc.start()
        except KeyboardInterrupt:
            self.parathread.join()
            #paraproc.join()
            print('Killed (not still alive)')

    def start_stream(self):
        """Start stream"""
        try:
            print('Lights')
            camera = self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('profile').child('stream').get(token=self.idToken).val()
            secretkey = self.database.child('users').child(self.ownerID).child('cameras').child(camera).child('secretKey').get(token=self.idToken).val()
            streamparam = self.ownerID + '/' + camera + '/' + secretkey
            print('Camera')
            DIR = os.path.dirname(os.path.realpath(__file__))
            self.streamproc = subprocess.Popen([DIR+'/stream.sh', streamparam])
            self.streamPID = self.streamproc.pid
            #os.spawnl(os.P_NOWAIT, DIR+'/stream.sh', 'stream.sh', streamparam)
        except IOError:
            print("ERROR: Stream unable to start")
            sys.exit(3)

    def stop_stream(self):
        """Stop stream"""
        #self.streamproc.kill()
        subprocess.Popen(['kill -9', self.streamPID])
        #os.kill(self.streamPID, signal.SIGKILL)
        print("KILLED STREAM")
        #DIR = os.path.dirname(os.path.realpath(__file__))
        #os.spawnl(os.P_NOWAIT, DIR+'/stream_stop.sh', 'stream_stop.sh')

    def get_name(self):
        """Return robot name"""
        name = self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('profile').child('name').get(token=self.idToken).val()
        return name

    def get_description(self):
        """Return robot description"""
        description = self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('profile').child('description').get(token=self.idToken).val()
        return description
        
    def set_robot_offline(self):
        """Set field value of isOnline to False"""
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('profile').update({'isOnline': False}, token=self.idToken)

    def is_robot_online(self):
        """Return field value of isOnline"""
        return self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('profile').child('isOnline').get(token=self.idToken).val()

    def get_first_user(self):
        """Get first user information"""
        (uid, useron, user_entry) = (None, None, None)
        firstuser = self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queue').order_by_key().limit_to_first(1).get(token=self.idToken)
        try:
            for i in firstuser.each():
                uid = i.val()['uid']
                useron = i.val()['userOn']
                user_entry = i.key()
        except TypeError:
            self.userID = None
            self.userOn = None
            self.userEntry = None
        self.userID = uid
        self.userOn = useron
        self.userEntry = user_entry
        return (user_entry, uid, useron)

    def get_useron(self):
        """Get first user status"""
        try:
            aux = self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queue').order_by_key().limit_to_first(1).get(token=self.idToken)
            for i in aux.each():
                useron = i.val()['userOn']
        except KeyboardInterrupt:
            sys.exit(2)
        return useron

    def get_control_data(self):
        """Return ControlData values from firebase"""
        user_id = self.get_first_user()[1]
        try:
            return self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('users').child(user_id).child("ControlData").order_by_key().get(token=self.idToken).val()
        except TypeError:
            return None
    
    def set_robotOn(self):
        """Set robotOn flag to True"""
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queue').child(self.userEntry).update({"robotOn": True}, token=self.idToken)

    def set_startControl(self):
        """Record timestamp when control session starts"""
        timestamp = int(round(time.time()*1000)) #calendar.timegm(time.gmtime())
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queue').child(self.userEntry).update({"startControl": timestamp}, token=self.idToken)

    def get_startControl(self):
        """Return timestamp for start of control session"""
        return self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queue').child(self.userEntry).child('startControl').get(token=self.idToken).val()

    def log_session(self):
        """Log a session to archive after it is over"""
        log_timestamp = int(round(time.time()*1000)) #queue_archive entry: timestamp
        try:
            log_data = {
                log_timestamp: {
                    'uid': self.userID,
                    'useTime': log_timestamp - self.get_startControl(),
                    'waitTime': self.get_startControl() - int(self.userEntry)
                }
            }
        except ValueError:
            log_data = {
                log_timestamp: {
                    'uid': self.userID,
                    'useTime': log_timestamp - self.get_startControl(),
                    'waitTime': None
                }
            }
        self.stop_stream()
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queueArchive').update(log_data, token=self.idToken)
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queue').child(self.userEntry).remove(token=self.idToken)
        self.userID = None
        self.userEntry = None
        self.userOn = None

    def start_still_alive_every_n_secs(self, n_seconds):
        """Start a recurring function that signals the robot is online every n seconds"""
        try:
            scheduler = sched.scheduler(time.time, time.sleep)
            scheduler.enter(n_seconds, 1, self.still_alive, (scheduler, n_seconds))
            scheduler.run()
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not still alive!!!')

    def still_alive(self, scheduler, n_seconds):
        """Send a signal to the server every n seconds"""
        try:
            iamalive = urllib2.Request('https://robots.brainyant.com:8080/iAmAlive')
            iamalive.add_header('Content-Type', 'application/json')
            urllib2.urlopen(iamalive, json.dumps({'robotID': self.robotID}))            
            if self.is_robot_online(): #there is a problem here with SSL. 
                scheduler.enter(n_seconds, 1, self.still_alive, (scheduler, n_seconds))
        except KeyboardInterrupt:
            for item in scheduler.queue:
                scheduler.cancel(item)
            sys.stdout.write('Not still alive 2!!!')

    def wait_for_available_user(self):
        """Wait for user to show up in queue"""
        # Get UID
        try:
            u_entry = None
            userid = None
            uon = None
            while self.is_robot_online() and userid is None and uon is None:
                (u_entry, userid, uon) = self.get_first_user()
        except KeyboardInterrupt:
            print("INTERRUPT!")
            self.parathread.join()
            sys.exit(0)
        self.set_robotOn()
        self.set_startControl()
        return (u_entry, userid, uon)

    def publish_data(self, data):
        """Publish data to database"""
        sensor_name = data[0]
        sensor_value = data[1]
        sensor_request = data[2]
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('users').child(self.userID).child("ControlData").child("sensors").child(sensor_name).update({'request': sensor_request}, token=self.idToken)
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('users').child(self.userID).child("ControlData").child("sensors").child(sensor_name).update({'value': sensor_value}, token=self.idToken)

    def get_sensor_request(self, sensor):
        try:
            return self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('users').child(self.userID).child("ControlData").child("sensors").child(sensor).child('request').get(token=self.idToken).val()
        except TypeError:
            self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('users').child(self.userID).child("ControlData").child("sensors").child(sensor).update({'request': False}, token=self.idToken)
            print('Sensor might not be registered')
            return False