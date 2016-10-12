# -*- coding: utf-8 -*-

import os
import unittest
import tempfile
from unittest import TestCase
from tp import app, db, socketio

class TPTestCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.socket = socketio.test_client(app)
        #il db è inizializzato a ogni test
        db.drop_all()
        db.create_all()

class TPAuthTestCase(TPTestCase):
    def setUp(self):
        super.setUp()
        #TODO: aggiungere autenticazione
