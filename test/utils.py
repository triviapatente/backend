import os
import unittest
import tempfile
from unittest import TestCase
from app import app
#TODO: reindirizzare il tutto in un db postgres fittizio
#TODO: muovere la configurazione in pipeline.py, in modo che venga fatta una volta per ogni test
class TPTestCase(TestCase):
    def setUp(self):
        #self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        #with app.app_context():
        #    app.init_db()

    def tearDown(self):
        app.config['TESTING'] = False
        #os.close(self.db_fd)
        #os.unlink(flaskr.app.config['DATABASE'])
