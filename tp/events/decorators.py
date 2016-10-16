# -*- coding: utf-8 -*-

from flask_socketio import emit
from models import Socket
from flask import g
from utils import getUsersFromRoomID
from functools import wraps

def event(name, action, include_self, preferences_key = None, needs_push = True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            (users, data) = f(*args, **kwargs)
            if not users:
                return None
            data["name"] = name
            data["action"] = action.value
            print "event users", users
            #users è una stanza
            if isinstance(users, basestring):
                users = getUsersFromRoomID(users)
            if isinstance(users, list) and isinstance(users[0], str):
                users = [u for u in getUsersFromRoomID(r) for r in users]
            print "event users", users
            if not users:
                return (users, data, include_self, preferences_key, needs_push)
            if not include_self:
                users = [u for u in users if u.id != g.user.id]
            print "event users", users
            for user in users:
                send(name, user, data, preferences_key, needs_push)
            return (users, data, include_self, preferences_key, needs_push)
        return decorated_function
    return decorator

def send(name, user, data, preferences_key, needs_push):
    socket = Socket.query.filter(Socket.user_id == user.id).first()
    if socket:
        print "[SOCKET EVENT, name = %s, user = %d]" % (name, user.id), data
        emit(name, room = socket.socket_id, data = data)
    elif needs_push:
        if preferences_key:
            preferences = Preferences.query.filter(Preferences.user_id == user.id).first()
            if preferences[preferences_key]:
                print "[PUSH EVENT, name = %s, user = %d]" % (name, user.id), data
                #TODO: send push
                pass
        else:
            print "[PUSH EVENT, name = %s, user = %d]" % (name, user.id), data
            #TODO: send push
            pass
