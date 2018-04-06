# -*- coding: utf-8 -*-

import os
import unittest
import tempfile
from unittest import TestCase
from flask import json
from tp import app, db, socketio
import string
from random import *
from test.base.socket.api import global_infos
from test.auth.http.api import register
class TPTestCase(TestCase):
    def setUp(self):
        self.app = get_test_client()
        self.socket = get_socket_client()
        #il db è inizializzato a ogni test
        db.drop_all()
        db.create_all()
        db.session.close()


class TPAuthTestCase(TPTestCase):
    def setUp(self, socket = False):
        super(TPAuthTestCase, self).setUp()
        response = register(self, "pippo", "pippo@gmail.com", "pisdfsdfppo")
        self.token = response.json.get("token")
        self.user = response.json.get("user")
        assert self.token
        assert self.user

#metodo che ottiene il client per fare il test, un pò modificato
def get_test_client():
    test_client = app.test_client()
    #sostituisco i metodi
    test_client.get = fake_request(test_client, "get")
    test_client.post = fake_request(test_client, "post")
    return test_client

def get_socket_client():
    socket_client = socketio.test_client(app)
    socket_client.deviceId = "".join(choice(string.ascii_letters + string.digits) for x in range(randint(10, 15)))
    socket_client.get_received = fake_socket_request(socket_client)
    socket_client.emit = fake_socket_emit(socket_client)
    return socket_client
#metodo che ritorna uno specifico metodo di app con delle modifiche

#ESEMPIO
#app.test_client().pippo diventa una funzione che accetta tra i suoi argomenti anche token,
#e se esiste chiama il vero test_client().pippo, che è stato recuperato prima di riassegnarlo,
#aggiungendo tp-session-token negli header, e ritornando il json della risposta, che è stata encodata su utf-8
def fake_request(test_client, fn):
    #vado a pescare il vecchio metodo, prima che lo cambiassi
    oldmethod = getattr(test_client, fn)
    def request(url, **args):
        #ottengo gli header, se ci sono
        headers = args.get("headers", {})
        #ottengo il token, se esiste
        token = args.get("token")
        #se esiste, lo inserisco negli header
        if token:
            headers["tp-session-token"] = token
            del args["token"]
        #reinserisco gli header
        args["headers"] = headers
        #chiamo il metodo che si chiamava fn in app, ripassando gli argomenti misti contenuti in args come argomenti della funzione
        response = oldmethod(url, **args)
        assert response.status_code != 500, "Internal server error"
        #faccio l'encode della risposta
        response.data = response.data.encode("utf-8")
        print "Risposta HTTP (url = %s): " % url, response.data
        try:
            #aggiungo il json alla risposta
            response.json = json.loads(response.data)
        except:
            pass
        return response
    return request
def fake_socket_emit(socket):
    oldmethod = socket.emit
    def emit(name, values):
        values["tp-device-id"] = socket.deviceId
        return oldmethod(name, values)
    return emit
def fake_socket_request(socket):
    oldmethod = socket.get_received
    def get_received(index = 0):
        #chiamo il metodo che si chiamava fn in app, ripassando gli argomenti misti contenuti in args come argomenti della funzione
        response = oldmethod()
        assert response, "Null response"
        event = response[index].get("name")
        args = response[index].get("args")
        if isinstance(args, list):
            json = args[0]
        else:
            json = args
        print "Risposta SOCKET (event = %s): " % event, json
        assert json, "No response from server"
        assert json.get("status_code") != 500, "Internal server error"
        output = lambda: None
        output.json = json
        return output
    return get_received
