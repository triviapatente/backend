# -*- coding: utf-8 -*-

from flask_socketio import emit
from models import Socket
from flask import g
from utils import getUsersFromRoomID
from functools import wraps
from tp import socketio
from tp.preferences.models import Preferences

def event(name, action, preferences_key = None, needs_push = True):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            (users, data) = f(*args, **kwargs)
            if not users:
                return None
            data["action"] = action.value
            data["name"] = name
            #users è una stanza
            if isinstance(users, basestring):
                users = getUsersFromRoomID(users)
            elif isinstance(users, list) and isinstance(users[0], basestring):
                users = [u for u in getUsersFromRoomID(r) for r in users]
            if not users:
                return (users, data, include_self, preferences_key, needs_push)
            #elimino il currentuser
            users = [u for u in users if u.id != g.user.id]
            for user in users:
                send(name, user, data, preferences_key, needs_push)
            return (users, data, preferences_key, needs_push)
        return decorated_function
    return decorator

def send(name, user, data, preferences_key, needs_push):
    sockets = Socket.query.filter(Socket.user_id == user.id).all()
    if sockets:
        for socket in sockets:
            print "[SOCKET EVENT, name = %s, user = %d, sid = %s]" % (name, user.id, socket.socket_id), data
            socketio.emit(name, data, room = socket.socket_id)

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
