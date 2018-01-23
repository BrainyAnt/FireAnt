#!/usr/bin/env python

import os
import sys
import sched
from multiprocessing import Process
import time
import json
import urllib2
import pyrebase

# Exception class definition
class TokenRequestError(Exception):
    """Could not retreive token exception."""
    pass
class InvalidTokenException(Exception):
    """Received invalid authentication token exception."""
    pass

class FireAnt:
    #members
    #database
    #idToken
    #userID
    #ownerID
    #robotID
    #userOn
    #userEntry

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
            #DIR = os.path.dirname(os.path.realpath(__file__))
            AUTH_DATA = json.load(open(os.path.dirname(os.path.realpath(__file__)) + '/' + authfile))
        except IOError:
            print("Config file not found!")
            sys.exit()

        try:
            REQUEST = urllib2.Request('https://robots.brainyant.com:8080/robotLogin')
            REQUEST.add_header('Content-Type', 'application/json')
            #========================NO ANSWER======================================
            RESPONSE = urllib2.urlopen(REQUEST, json.dumps(AUTH_DATA))
            #==============================================================
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
        self.ownerID = AUTH_DATA["owner_ID"]
        self.robotID = AUTH_DATA["robot_ID"]
        #p1 = Process(target = self.start_still_alive_every_n_secs, args = [1])
        #p1.start()

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
        return self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('users').child(self.userID).child("ControlData").order_by_key().get(token=self.idToken)
    
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
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queueArchive').update(log_data, token=self.idToken)
        self.database.child('users').child(self.ownerID).child('robots').child(self.robotID).child('queue').child(self.userEntry).remove(token=self.idToken)
        self.userID = None
        self.userEntry = None
        self.userOn = None

    def start_still_alive_every_n_secs(self, n_seconds):
        """Start a recurring function that signals the robot is online every n seconds"""
        try:
            scheduler = sched.scheduler(time.time, time.sleep)
            scheduler.enter(n_seconds, 1, self.still_alive, (self, scheduler, n_seconds))
            scheduler.run()
        except KeyboardInterrupt:
            sys.exit(1)

    def still_alive(self, scheduler, n_seconds):
        """Send a signal to the server every n seconds"""
        iamalive = urllib2.Request('https://robots.brainyant.com:8080/iAmAlive')
        iamalive.add_header('Content-Type', 'application/json')
        urllib2.urlopen(iamalive, json.dumps({'robotID': self.robotID}))
        try:
            if self.is_robot_online():
                scheduler.enter(n_seconds, 1, self.still_alive, (self, scheduler, n_seconds))
        except KeyboardInterrupt:
            sys.exit(1)

#    def wait_for_users():
#        """Wait for user to show up in queue"""
#        # Get UID
#        try:
#            u_entry = None
#            userid = None
#            uon = None
#            while userid is None:
#                (userid, uon, u_entry) = get_first_user()
#            wait_for_user_on(u_entry, userid, uon)
#        except KeyboardInterrupt:
#            print("INTERRUPT!")
#            sys.exit(0)
#
#    def wait_for_user_on(u_entry, userid, uon):
#        """Wait for current user to be online"""
#        try:
#            while not uon:
#                uon = get_useron()
#            set_robotOn(u_entry)
#            set_startControl(u_entry)
#            listen_for_commands(u_entry, userid, uon)
#        except KeyboardInterrupt:
#            print("INTERRUPT!")
#            exit(0)