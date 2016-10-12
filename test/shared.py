# -*- coding: utf-8 -*-

import os
import unittest
import tempfile
from unittest import TestCase
from tp import app, db, socketio
from test.auth.http.api import register
class TPTestCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.socket = socketio.test_client(app)
        #il db è inizializzato a ogni test
        db.drop_all()
        db.create_all()

class TPAuthTestCase(TPTestCase):
    def setUp(self):
        super(TPAuthTestCase, self).setUp()
        response = register(self.app, "pippo", "pippo@gmail.com", "pippo")
        self.token = response.json.get("token")
        self.user = response.json.get("user")
