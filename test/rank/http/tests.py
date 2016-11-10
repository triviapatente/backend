# -*- coding: utf-8 -*-
from api import *
from test.shared import TPTestCase
from tp import app
from test.auth.http.api import login, register

class RankHTTPTestCase(TPTestCase):
    token = None
    number_of_results = None

    def setUp(self):
        super(RankHTTPTestCase, self).setUp()
        self.number_of_results = app.config["RESULTS_LIMIT_RANK_ITALY"]
        MAX = self.number_of_results + 3
        for i in range (0, MAX):
            register(self, "user%s" % i, "user%s@gmail.com" % i, "user%s" % i)
        self.token = login(self, "user%s" % (MAX-1), "user%s" % (MAX-1)).json.get("token")
    def test_global_rank(self):
        print "#1: Classifica ricevuta correttamente"
        response = global_rank(self)
        assert response.status_code == 200
        assert response.json.get("rank")
        assert response.json.get("my_position")

        rank = response.json.get("rank")
        print "#2: Classifica di %s elementi come predefinito" % self.number_of_results
        assert len(rank) == self.number_of_results

    def test_search(self):
        print "#1: Risposta successful"
        response = search(self, "us")
        assert response.status_code == 200
        matches = response.json.get("matches")
        assert matches is not None
        for match in matches:
            assert match.get("position")

        print "#3: Parametri mancanti"
        print "#3.1: query"
        response = search(self, None)
        assert response.status_code == 400
