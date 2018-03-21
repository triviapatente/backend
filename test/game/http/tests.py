# -*- coding: utf-8 -*-

from api import *
from test.shared import TPAuthTestCase, get_socket_client
from tp.game.models import Game, Partecipation
from test.auth.http.api import register
from test.game.http.utils import dumb_training
from test.base.socket.api import join_room
from test.game.socket.api import *
from test.game.socket.utils import dumb_crawler
from test.base.socket.api import global_infos
from tp import db, app
class GameHTTPTestCase(TPAuthTestCase):
    first_opponent = None
    second_opponent = None
    third_opponent = None

    first_opponent_socket = None
    def setUp(self):
        super(GameHTTPTestCase, self).setUp(socket = True)
        self.first_opponent = register(self, "test1", "test1@gmail.com", "sdfsdfsdfds").json
        self.first_opponent_socket = get_socket_client()
        #il primo utente deve allacciarsi al socket per ricevere gli eventi, con una chiamata qualsiasi
        global_infos(self.first_opponent_socket, self.first_opponent.get("token"))
        self.second_opponent = register(self, "test2", "test2@gmail.com", "sdfsdfsdfds").json
        self.third_opponent = register(self, "test3", "test3@gmail.com", "sdfsdfsdfds").json

    def test_new_game(self):
        opponent_id = self.first_opponent.get("user").get("id")

        print "#1: Creazione game"
        response = new_game(self, opponent_id)
        assert response.json.get("success") == True
        game = response.json.get("game")
        assert game
        assert game.get("started") == False
        assert response.json.get("user")

        print "#1.1: Due partecipation sono state create:"
        game_id = game.get("id")
        partecipations = Partecipation.query.filter(Partecipation.game_id == game_id).all()
        assert len(partecipations) == 2

        print "#2 Event Test: l'avversario ha ricevuto l'evento"
        response = self.first_opponent_socket.get_received()
        assert response.json.get("action") == "create"
        assert response.json.get("user")
        assert response.json.get("name") == "game"

        print "#3: Creazione game con utente inesistente"
        response = new_game(self, 32)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4: Parametri mancanti: utente"
        response = new_game(self, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_leave_score_decrement(self):
        opponent_id = self.first_opponent.get("user").get("id")
        opponent_token = self.first_opponent.get("token")
        other_opponent_token = self.second_opponent.get("token")

        game_id = new_game(self, opponent_id).json.get("game").get("id")
        #per intercettare e rendere 'innocuo' l'evento di creazione del game
        self.first_opponent_socket.get_received()

        print "#1: Il game non esiste"
        response = leave_score_decrement(self, 200)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#2: Non appartengo al game"
        other_game_id = new_game(self, opponent_id, token = other_opponent_token).json.get("game").get("id")
        #per intercettare e rendere 'innocuo' l'evento di creazione del game
        self.first_opponent_socket.get_received()

        response = leave_score_decrement(self, other_game_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: Parametri mancanti"
        print "#3: game_id"
        response = leave_score_decrement(self, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4: Ottengo correttamente il mio score decrement"
        response = leave_score_decrement(self, game_id)
        assert response.json.get("success") == True
        assert response.json.get("decrement") is not None

    def test_leave_game(self):
        opponent_id = self.first_opponent.get("user").get("id")
        opponent_token = self.first_opponent.get("token")
        other_opponent_token = self.second_opponent.get("token")

        game_id = new_game(self, opponent_id).json.get("game").get("id")
        #per intercettare e rendere 'innocuo' l'evento di creazione del game
        self.first_opponent_socket.get_received()

        print "#1: Il game non esiste"
        response = leave_game(self, 200)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#2: Non appartengo al game"
        other_game_id = new_game(self, opponent_id, token = other_opponent_token).json.get("game").get("id")
        #per intercettare e rendere 'innocuo' l'evento di creazione del game
        self.first_opponent_socket.get_received()

        response = leave_game(self, other_game_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: Parametri mancanti"
        print "#3: game_id"
        response = leave_game(self, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4: Mi tolgo dal gioco correttamente"
        response = leave_game(self, game_id)
        assert response.json.get("success") == True
        assert response.json.get("partecipations")
        assert response.json.get("game")
        assert response.json.get("ended") == True
        assert response.json.get("winner")

        print "#5 Event Test: l'avversario ha ricevuto l'evento"
        response = self.first_opponent_socket.get_received()
        assert response.json.get("action") == "game_left"
        assert response.json.get("partecipations")
        assert response.json.get("user_id")
        assert response.json.get("winner_id")

        print "#6: Mi ritolgo dallo stesso gioco"
        response = leave_game(self, game_id)
        assert response.json.get("status_code") == 403
        assert response.json.get("success") == False

        print "#7: Una volta uscito, ogni azione mi considera fuori room"
        response = init_round(self.socket, game_id, self.token)
        assert response.json.get("status_code") == 403
        assert response.json.get("success") == False

    def test_random_search(self):

        print "#1: Creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user1 = response.json.get("user")
        assert user1

        #azzero i database se no l'utente scelto è sempre lo stesso (l'unico con game attivi)
        Partecipation.query.delete()
        db.session.commit()

        print "#2: Creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user2 = response.json.get("user")
        assert user2

        #azzero i database se no l'utente scelto è sempre lo stesso (l'unico con game attivi)
        Partecipation.query.delete()
        db.session.commit()

        print "#3: Creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user3 = response.json.get("user")
        assert user3

        print "Opponents: ", user1.get("username"), user2.get("username"), user3.get("username")

    def prepare_round(self, socket, game, token):
        print "preparing round for game", game
        round_id = init_round(socket, game, token).json.get("round").get("id")
        category = get_categories(socket, game, round_id, token).json.get("categories")[0].get("id")
        choose_category(socket, category, game, round_id, token)
        return round_id
    def process_round(self, socket, game, token, round_id = None):
        if not round_id:
            round_id = self.prepare_round(socket, game, token)
        print "processing round for game", game, "id:", round_id
        questions = get_questions(socket, game, round_id, token).json.get("questions")
        for question in questions:
            answer(socket, True, game, round_id, question.get("id"), token)
        return round_id
    def create_bulk_game(self):
        opponent_id = self.first_opponent.get("user").get("id")
        opponent_token = self.first_opponent.get("token")
        id = new_game(self, opponent_id).json.get("game").get("id")
        join_room(self.socket, id, "game", self.token)
        join_room(self.first_opponent_socket, id, "game", self.first_opponent.get("token"))
        self.socket.get_received()
        return id

    def test_recent_games(self):

        dumb_crawler()

        #il primo game lo creo, inizializzo il round e non rispondo: è il mio turno
        #Risultato sperato : my_turn = true, started = false
        first_game = self.create_bulk_game()
        init_round(self.socket, first_game, self.token)
        #il secondo game lo creo e faccio scorrere 1 turno fino ad arrivare al secondo turno dell'avversario
        #Risultato sperato : my_turn = true, started = false (il prossimo turno il dealer sarò io!)
        second_game = self.create_bulk_game()
        round_id = self.process_round(self.socket, second_game, self.token)
        self.first_opponent_socket.get_received()
        self.process_round(self.first_opponent_socket, second_game, self.first_opponent.get("token"), round_id)
        self.socket.get_received()
        round_id = self.prepare_round(self.first_opponent_socket, second_game, self.first_opponent.get("token"))
        self.socket.get_received()
        self.process_round(self.socket, second_game, self.token, round_id)
        self.first_opponent_socket.get_received()
        init_round(self.socket, second_game, self.token)
        #il terzo game lo creo, rispondo al primo round con l'avversario e ritorno al mio turno, scegliendo la categoria
        #Risultato sperato : my_turn = true, started = false (categoria settata, posso agire!)
        third_game = self.create_bulk_game()
        round_id = self.process_round(self.socket, third_game, self.token)
        self.first_opponent_socket.get_received()
        self.process_round(self.first_opponent_socket, third_game, self.first_opponent.get("token"), round_id)
        self.socket.get_received()
        self.prepare_round(self.first_opponent_socket, third_game, self.first_opponent.get("token"))
        self.socket.get_received()
        #il quarto game lo creo, rispondo al primo round con l'avversario e ritorno al mio turno
        #Risultato sperato : my_turn = false, started = true (devo aspettare che l'avversario setti la categoria)
        fourth_game = self.create_bulk_game()
        round_id = self.process_round(self.socket, fourth_game, self.token)
        self.first_opponent_socket.get_received()
        self.process_round(self.first_opponent_socket, fourth_game, self.first_opponent.get("token"), round_id)
        init_round(self.first_opponent_socket, fourth_game, self.first_opponent.get("token"))
        #il quinto game lo creo e rispondo a tutte le domande fino ad arrivare al turno dell'avversario
        #Risultato sperato : my_turn = false, started = false (il prossimo turno è dell'avversario!)
        fifth_game = self.create_bulk_game()
        round_id = self.process_round(self.socket, fifth_game, self.token)
        self.first_opponent_socket.get_received()
        #il sesto game lo creo e mi tolgo subito, quindi viene settato ended = true
        sixth_game = self.create_bulk_game()
        leave_game(self, sixth_game)

        print "#1: Risposta successful"
        response = recent_games(self)
        assert response.json.get("success") == True

        games = response.json.get("recent_games")
        assert games is not None
        assert len(games) == 6

        print "#2.1: Il primo game è quello con il mio turno"
        assert games[0].get("id") == third_game
        assert games[0].get("my_turn") == True
        assert games[0].get("started") == True

        print "#2.2: Il secondo game è il secondo con il mio turno"
        assert games[1].get("id") == second_game
        assert games[1].get("my_turn") == True
        assert games[1].get("started") == True

        print "#2.3: Il terzo game è il secondo con il turno dell'avversario"
        assert games[2].get("id") == first_game
        assert games[2].get("my_turn") == True
        assert games[2].get("started") == False

        print "#2.4: Il quarto game è quello con il turno dell'avversario"
        assert games[3].get("id") == fifth_game
        assert games[3].get("my_turn") == False
        assert games[3].get("started") == False

        print "#2.5: Il quinto game è il terzo con il mio turno"
        assert games[4].get("id") == fourth_game
        assert games[4].get("my_turn") == False
        assert games[4].get("started") == True

        print "#2.6: Il sesto game è quello finito"
        assert games[5].get("id") == sixth_game
        assert games[5].get("ended") == True

    def test_suggested_users(self):
        user_id = self.user.get("id")
        first_opponent_id = self.first_opponent.get("user").get("id")

        #Aggiunta di un game già finito con vincitore me stesso per testare last won
        game = Game(creator_id = user_id, ended = True, winner_id = user_id)
        db.session.add(game)
        db.session.commit()

        part_1 = Partecipation(user_id = user_id, game_id = game.id)
        part_2 = Partecipation(user_id = first_opponent_id, game_id = game.id)
        db.session.add_all([part_1, part_2])
        db.session.commit()

        print "#1. Chiamata successful"
        response = suggested_users(self)
        assert response.json.get("success") == True
        users = response.json.get("users")
        assert users is not None

        print "#1.1 Controllo che sia indicato che l'ultima partita con a la ho vinta io"
        for user in users:
            last_game_won = user.get("last_game_won")
            if user.get("id") == first_opponent_id:
                assert last_game_won == True
            else:
                assert last_game_won is None or last_game_won == False

        print "#2.1 Controllo che sia indicato che l'ultima partita con a la ho persa io"
        #cambio il vincitore dell'ultimo game con a, e lo setto ad a stesso
        game.winner_id = first_opponent_id
        db.session.add(game)
        db.session.commit()

        response = suggested_users(self)
        assert response.json.get("success") == True
        users = response.json.get("users")

        for user in users:
            last_game_won = user.get("last_game_won")
            print last_game_won
            if user.get("id") == first_opponent_id:
                assert last_game_won == False
            else:
                assert last_game_won is None or last_game_won == False

        print "#3. Lunghezza output = 10"
        assert len(users) == 3

        print "#4. Non ci sono io nell'output"
        for user in users:
            assert user.get("id") != user_id


    def test_search_user(self):
        print "#1: Risposta successful"
        response = search_user(self, "a")
        assert response.status_code == 200
        users = response.json.get("users")
        assert users is not None

        print "#3: Parametri mancanti"
        print "#3.1: query"
        response = search_user(self, None)
        assert response.status_code == 400

    def test_training_answer(self):
        dumb_crawler()
        questions = get_training_questions(self, True).json.get("questions")
        input = {}
        for question in questions:
            input[question.get("id")] = question.get("answer")
        print "#1.1: Risposta successfull"
        response = answer_training(self, input)
        assert response.status_code == 200

        print "#1.2: Ritorno il training creato"
        assert response.json.get("training") is not None
        assert response.json.get("training").get("id") is not None

        print "#1.3: Nelle stats viene registrato un nuovo training completo e senza errori"
        response = get_trainings(self)
        assert response.json.get("stats").get(app.config["TRAINING_STATS_NO_ERRORS"]) == 1
        assert response.json.get("stats").get(app.config["TRAINING_STATS_TOTAL"]) == 1
        assert len(response.json.get("trainings")) == 1

        print "#2 Parametro invalido"
        print "#2.1 Numero sbagliato di answer"
        response = answer_training(self, {1: True})
        assert response.status_code == 400

        print "#2.2 Alcuni quiz non esistono"
        newInput = input
        del newInput["%s" % questions[0].get("id")]
        newInput["%s" % -1] = True
        response = answer_training(self, newInput)
        assert response.status_code == 400

        print "#3: Parametri mancanti"
        print "#3: answers"
        response = answer_training(self, None)
        assert response.status_code == 400

    def test_get_training(self):
        dumb_crawler()
        id = dumb_training(self.user.get("id"), 0)

        print "#1.1: Risposta successfull"
        response = get_training(self, id)
        assert response.status_code == 200

        print "#1.2: Numero di domande corrette"
        assert len(response.json.get("questions")) == app.config["NUMBER_OF_QUESTIONS_FOR_TRAINING"]

        print "#1.3: Utente non autorizzato"
        response = get_training(self, id, self.first_opponent.get("token"))
        assert response.status_code == 403

        print "#2. Training inesistente"
        response = get_training(self, 234)
        assert response.status_code == 403

        print "#3: Parametri mancanti"
        print "#3: training"
        response = get_training(self, None)
        assert response.status_code == 404

    def test_get_trainings_and_stats(self):
        dumb_crawler()
        user_id = self.user.get("id")
        dumb_training(user_id, 0)
        dumb_training(user_id, 0)
        dumb_training(user_id, 1)
        dumb_training(user_id, 4)
        dumb_training(user_id, 3)
        dumb_training(user_id, 5)
        dumb_training(user_id, 6)
        dumb_training(user_id, 7)

        print "#1.1: Risposta successfull"
        response = get_trainings(self)
        assert response.status_code == 200

        print "#2.1: Lunghezza lista di training corretta"
        assert len(response.json.get("trainings")) == 8

        print "#2.2: Stats"
        stats = response.json.get("stats")

        print "#2.2.1: Stats: count training corretto"
        assert stats.get(app.config["TRAINING_STATS_TOTAL"]) == 8

        print "#2.2.2: Stats: no_errors corretto"
        assert stats.get(app.config["TRAINING_STATS_NO_ERRORS"]) == 2

        print "#2.2.3: Stats: 12_errors corretto"
        assert stats.get(app.config["TRAINING_STATS_1_2_ERRORS"]) == 1

        print "#2.2.4: Stats: 34_errors corretto"
        assert stats.get(app.config["TRAINING_STATS_3_4_ERRORS"]) == 2

        print "#2.2.4: Stats: more_errors corretto"
        assert stats.get(app.config["TRAINING_STATS_MORE_ERRORS"]) == 3


    def test_get_training_questions(self):
        dumb_crawler()

        print "#1.1: Risposta successfull, random = True"
        response = get_training_questions(self, True)
        assert response.status_code == 200

        print "#1.1: Risposta successfull, random = False"
        response = get_training_questions(self, False)
        assert response.status_code == 200

        print "#2: 40 domande"
        assert len(response.json.get("questions")) == app.config["NUMBER_OF_QUESTIONS_FOR_TRAINING"]

        print "#3: Parametri mancanti"
        print "#3: random"
        response = get_training_questions(self, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400
