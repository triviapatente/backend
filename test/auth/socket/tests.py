
from test.shared import TPAuthTestCase
from api import *
from test.game.socket.utils import dumb_crawler
from tp.game.models import Category

class AuthSocketTestCase(TPAuthTestCase):
    def test_login(self):
        # run dumb crawler
        dumb_crawler()

        print "#1: Successful login"
        response = login(self)
        assert response.json.get("global_rank_position") is not None
        #assert response.json.get("preferences") is not None
        #assert response.json.get("fb") is not None
        #TODO: assert response.json.get("friends_rank_position") is not None
        #stats = response.json.get("stats")
        #assert stats is not None
        #first = stats[0]
        #assert first
        #assert first.get("id") is None
        #assert first.get("hint") == "Complessivo"

        #print "#2: Le statistiche sono su tutte le categorie"
        #stats = response.json.get("stats")
        #count = Category.query.count()
        #il +1 sta ad indicare 'complessivo'
        #assert len(stats) == count + 1

    def test_logout(self):
        response = login(self)

        print "#1: Successful logout"
        response = logout(self.socket)
        assert response.json.get("success") == True
