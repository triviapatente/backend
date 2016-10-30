# -*- coding: utf-8 -*-
from api import *
from test.shared import TPAuthTestCase
from tp import app
from test.auth.http.api import login, register

class RankHTTPTestCase(TPAuthTestCase):

    def test_global_rank(self):
        number_of_results = app.config["RESULTS_LIMIT_RANK_ITALY"]
        MAX = number_of_results + 3
        for i in range (0, MAX):
            register(self, "user%s" % i, "user%s@gmail.com" % i, "user%s" % i)
        token = login(self, "user%s" % (MAX-1), "user%s" % (MAX-1)).json.get("token")

        print "#1: Classifica ricevuta correttamente"
        response = global_rank(self, token)
        assert response.status_code == 200
        assert response.json.get("rank")
        assert response.json.get("my_position")

        rank = response.json.get("rank")
        print "#2: Classifica di %s elementi come predefinito" % number_of_results
        assert len(rank) == number_of_results
