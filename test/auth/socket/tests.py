
from test.shared import TPAuthTestCase
from api import *

class AuthSocketTestCase(TPAuthTestCase):
    #TEST METHODS
    def test_login(self):
        print "#2: Successfull Login"
        response = login(self, self.token)
        assert response.json.get("success") == True

    def test_logout(self):
        response = login(self, self.token)
        print "#1: Successfull logout"
        response = logout(self)
        assert response.json.get("success") == True
