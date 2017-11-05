# -*- coding: utf-8 -*-
from api import *
from test.shared import TPTestCase
from tp import app, db
from tp.auth.models import User
from test.auth.http.api import login, register

class RankHTTPTestCase(TPTestCase):
    token = None
    number_of_results = None
    number_of_users = None
    user_id = None

    def setUp(self):
        super(RankHTTPTestCase, self).setUp()
        #numero di risultati che la classifica ritorna di default
        self.number_of_results = app.config["RESULTS_LIMIT_RANK_ITALY"]
        #numero di utenti da generare per la classifica
        self.number_of_users = self.number_of_results * 3
        for i in range (0, self.number_of_users):
            response = register(self, "user%s" % i, "user%s@gmail.com" % i, "user%s" % i)
            id = response.json.get("user").get("id")
            user = User.query.filter(User.id == id).first()
            #l'utente i-esimo avrà punteggio i
            user.score = i
            db.session.commit()

        userNumber = self.number_of_users - 1
        loginResponse = login(self, "user%s" % userNumber, "user%s" % userNumber)
        self.token = loginResponse.json.get("token")
        self.user_id = loginResponse.json.get("user").get("id")

    def test_global_rank(self):
        print "#1: Classifica ricevuta correttamente"
        response = global_rank(self)
        assert response.status_code == 200
        assert response.json.get("rank")
        assert response.json.get("my_position")

        rank = response.json.get("rank")
        print "#2: Classifica di %s elementi come predefinito" % self.number_of_results
        assert len(rank) == self.number_of_results

        print "#3: Position di ogni elemento ricevuta"
        for user in rank:
            assert user.get("position")

        print "#4: Sono nei primi n, mi ritorna i primi n"
        #sono già primo, sono stato generato con lo score più alto
        last_index = len(rank) - 1
        assert rank[last_index].get("position") == self.number_of_results

        print "#5: Sono dopo i primi n, mi ritorna i (n/2)-1 prima e n/2 dopo"
        #aggiorno il mio punteggio
        user = User.query.filter(User.id == self.user_id).first()
        lastScore = user.score
        newPosition = self.number_of_results + 3
        newScore = self.number_of_users - newPosition
        user.score = newScore
        #aggiorno il punteggio dell'utente che ha il mio nuovo punteggio, per non generare inconsistenze
        other = User.query.filter(User.score == user.score).first()
        other.score = lastScore
        db.session.commit()
        #ottengo la nuova classifica
        response = global_rank(self)
        rank = response.json.get("rank")

        assert rank[0].get("position") == newPosition - self.number_of_results / 2 + 1

        print "#6: Paginazione: up corretta"
        thresold = newScore
        response = global_rank(self, thresold, "up")
        rank = response.json.get("rank")
        
        assert rank[0].get("score") == newScore + self.number_of_results

        print "#7: Paginazione: down corretta"
        response = global_rank(self, thresold, "down")
        rank = response.json.get("rank")
        print rank[len(rank) - 1].get("score")
        print newScore - self.number_of_results
        assert rank[len(rank) - 1].get("score") == newScore - self.number_of_results

        print "#8: Paginazione: direction sbagliata"
        response = global_rank(self, 3400, "efeervev")
        assert response.status_code == 400

        print "#9: Parametri mancanti"
        print "#9.1: thresold quando direction è settata"
        response = global_rank(self, None, "up")
        assert response.status_code == 400

        print "#9.2: direction quando thresold è settato"
        response = global_rank(self, 3400, None)
        assert response.status_code == 400

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
