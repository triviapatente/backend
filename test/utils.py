import os
import unittest
import tempfile
from unittest import TestCase
from app import app, db

class TPTestCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        #il db è inizializzato a ogni test
        db.drop_all()
        db.create_all()
