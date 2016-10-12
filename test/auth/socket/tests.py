
from test.shared import TPTestCase
from api import *
class AuthSocketTestCase(TPTestCase):

    #Utility methods



    #TEST METHODS

    def test_login(self):
        token = register(self.app, "pippo", "pippo@gmail.com", "pippo")

        response = login(self.socket, token)
        assert response.json.get("success") == True

    def test_logout(self):
        token = register(self.app, "pippo", "pippo@gmail.com", "pippo")
        response = login(self.socket, token)
        assert response.json.get("success") == True
        response = logout(self.socket)
        assert response.json.get("success") == True
