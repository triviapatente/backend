# -*- coding: utf-8 -*-

from flask_socketio import emit
from flask import g
from functools import wraps
from pyfcm import FCMNotification

from tp.events.models import *
from tp.base.utils import getUsersFromRoomID
from tp import socketio, app
from tp.preferences.models import Preferences

pushService = FCMNotification(api_key = app.config["FIREBASE_API_KEY"])

def event(name, action, preferences_key = None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            (users, data, push_infos) = f(*args, **kwargs)
            if not users:
                return None
            if data is not None: #necessito di dati socket?
                data["action"] = action.value
                data["name"] = name
            #users è una stanza
            if isinstance(users, str):
                users = getUsersFromRoomID(users)
            if not users:
                return (users, data, preferences_key)
            #elimino il currentuser
            users = [u for u in users if u.id != g.user.id]
            if data is not None:
                for user in users:
                    send_socket_message(name, user, data)
            if push_infos:
                send_push_message(users, push_infos)
            return (users, data, preferences_key)
        return decorated_function
    return decorator

def send_socket_message(name, user, data):
    sockets = Socket.query.filter(Socket.user_id == user.id).all()
    for socket in sockets:
        print(f"[SOCKET EVENT, name = {name}, user = {user.username}, sid = {socket.socket_id}]")
        try:
            socketio.emit(name, data, room = socket.socket_id)
        except Exception as e:
            print("Exception on emit", str(e))

def send_push_message(users, params):
    user_ids = [u.id for u in users]
    installations = Installation.query.filter(Installation.user_id.in_(user_ids)).all()
    device_tokens = [i.token for i in installations]
    if len(device_tokens) != 0:
        print("Sending push to...", device_tokens)
        title = "TriviaPatente"
        body = params["message"]
        result = pushService.notify_multiple_devices(registration_ids = device_tokens, message_title = title, message_body = body, data_message = params)
        print("[PUSH EVENT, result:]", result)
