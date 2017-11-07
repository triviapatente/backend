
from test.shared import TPAuthTestCase
from api import *
from test.game.socket.utils import dumb_crawler
from tp.game.models import Category

class AuthSocketTestCase(TPAuthTestCase):

    def test_logout(self):
        response = login(self)

        print "#1: Successful logout"
        response = logout(self.socket)
        assert response.json.get("success") == True
