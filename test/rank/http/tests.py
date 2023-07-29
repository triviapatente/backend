# -*- coding: utf-8 -*-
from api import *
from utils import *
from test.shared import TPTestCase
from tp import app, db
from tp.auth.models import User
from test.auth.http.api import login, register
from tp.rank.utils import extractArrayFrom

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
        self.number_of_users = self.number_of_results + 10
        for i in range (0, self.number_of_users):
            response = register(self, "user%s" % i, "user%s@gmail.com" % i, "userpassword%s" % i)
            id = response.json.get("user").get("id")
            user = User.query.filter(User.id == id).first()
            #l'utente i-esimo avrà punteggio i
            user.score = i
            db.session.add(user)
            db.session.commit()

        userNumber = self.number_of_users - 1
        loginResponse = login(self, "user%s" % userNumber, "userpassword%s" % userNumber)
        self.token = loginResponse.json.get("token")
        self.user_id = loginResponse.json.get("user").get("id")

    def test_array_merge(self):
        limit = 10
        print("#1: Left e right < limit / 2")
        output = extractArrayFrom([], [], limit)
        assert len(output) == 0
        output = extractArrayFrom([1, 2], [3], limit)
        assert len(output) == 3
        output = extractArrayFrom([1], [2, 3], limit)
        assert len(output) == 3
        print("#2: Left < limit / 2, e right no")
        output = extractArrayFrom([], [1, 2, 3, 4, 5], limit)
        assert len(output) == 5
        output = extractArrayFrom([], [1, 2, 3, 4, 5, 6], limit)
        assert len(output) == 6
        output = extractArrayFrom([1], [2, 3, 4, 5, 6], limit)
        assert len(output) == 6
        output = extractArrayFrom([1], [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], limit)
        assert len(output) == limit
        print("#3: Right < limit / 2, e left no")
        output = extractArrayFrom([1, 2, 3, 4, 5], [], limit)
        assert len(output) == 5
        output = extractArrayFrom([1, 2, 3, 4, 5, 6], [], limit)
        assert len(output) == 6
        output = extractArrayFrom([1, 2, 3, 4, 5], [6], limit)
        assert len(output) == 6
        output = extractArrayFrom([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [11], limit)
        assert len(output) == limit
        print("#4: Right e left >= limit / 2")
        output = extractArrayFrom([1, 2, 3, 4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14, 15, 16, 17], limit)
        assert len(output) == limit
        assert output[0] == 5
        assert output[limit - 1] == 14
        output = extractArrayFrom([1, 2, 3, 4, 5], [6, 7, 8, 9, 10], limit)
        assert len(output) == limit

    def test_global_rank(self):
        print("#1: Classifica ricevuta correttamente")
        response = global_rank(self)
        rank = response.json.get("rank")
        assert response.status_code == 200
        assert rank

        print(f"#2: Classifica di {self.number_of_results} elementi come predefinito")
        assert len(rank) == self.number_of_results

        print("#3: Position e internalPosition di ogni elemento ricevuta")
        for user in rank:
            assert user.get("position")
            assert user.get("internalPosition")

        print("#4: Sono nei primi n, mi ritorna i primi n")
        #sono già primo, sono stato generato con lo score più alto
        index = 0
        assert rank[index].get("position") == index + 1
        index = len(rank) - 1
        assert rank[index].get("position") == index + 1

        print("#5: Sono dopo i primi n, ritorna esattamente n risultati con me")
        #aggiorno il mio punteggio
        user = User.query.get(self.user_id)
        lastScore = user.score
        #aggiorno il punteggio dell'utente che ha il mio nuovo punteggio, per non generare inconsistenze
        other = User.query.filter(User.score == lastScore / 2).filter(User.id != user.id).first()
        other.score = lastScore
        user.score = lastScore / 2
        db.session.commit()
        #ottengo la nuova classifica
        response = global_rank(self)
        rank = response.json.get("rank")
        assert len(rank) == self.number_of_results

        print("#6: Ci sono sempre io in classifica")
        obtainCurrentUserFrom(rank, self.user_id)

        #paginazione
        thresold = [u for u in rank if u.get("id") == self.user_id][0].get("internalPosition")
        print("#7: Paginazione: up corretta")
        response = global_rank(self, thresold, "up")
        rank = response.json.get("rank")

        for i in range(0, len(rank)):
            assert rank[i].get("internalPosition") == thresold + i + 1

        print("#8: Paginazione: down corretta")
        response = global_rank(self, thresold, "down")
        rank = response.json.get("rank")

        for i in range(0, len(rank)):
            assert rank[i].get("internalPosition") == thresold - len(rank) + i

        print("#9: Paginazione: direction sbagliata")
        response = global_rank(self, 3400, "efeervev")
        assert response.status_code == 400

        print("#10: Paginazione: top rank")
        response = global_rank(self, 0, "up")
        rank = response.json.get("rank")
        assert len(rank) == self.number_of_results
        for i in range(0, len(rank)):
            assert rank[i].get("internalPosition") == i + 1

        print("#11: Parametri mancanti")
        print("#11.1: thresold quando direction è settata")
        response = global_rank(self, None, "up")
        assert response.status_code == 400

        print("#11.2: direction quando thresold è settato")
        response = global_rank(self, 3400, None)
        assert response.status_code == 400

    def test_position(self):
        user = User.query.filter(User.id == self.user_id).first()
        opponent = User.query.filter(User.id != self.user_id).first()
        opponent.score = user.score
        opponent_id = opponent.id
        db.session.add(opponent)
        db.session.commit()

        response = global_rank(self)
        rank = response.json.get("rank")
        user = [u for u in rank if u.get("id") == self.user_id][0]
        opponent = [u for u in rank if u.get("id") == opponent_id][0]

        print("#1: Punteggi uguali, position uguale")
        assert user.get("position") == opponent.get("position")

        print("#2: Punteggi uguali, internalPosition diversa")
        assert user.get("internalPosition") != opponent.get("internalPosition")

        print("#3: internalPosition per ugual punteggio stabilita alfabeticamente")
        if user.get("username") > opponent.get("username"):
            assert user.get("internalPosition") > opponent.get("internalPosition")
        else:
            assert user.get("internalPosition") < opponent.get("internalPosition")

    def test_search(self):
        print("#1: Risposta successful")
        response = search(self, "us")
        assert response.status_code == 200
        matches = response.json.get("users")
        assert matches is not None
        for match in matches:
            assert match.get("position")

        print("#2: Parametri mancanti")
        print("#2.1: query")
        response = search(self, None)
        assert response.status_code == 400
