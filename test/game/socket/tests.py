# -*- coding: utf-8 -*-

from test.auth.http.api import register
from test.auth.socket.api import login
from test.game.http.api import new_game
from test.shared import get_socket_client, TPAuthTestCase
from test.base.socket.api import join_room, leave_room
from api import *
from tp.game.models import Round
from tp import db
from sqlalchemy.exc import IntegrityError
from utils import dumb_crawler, create_random_category
class GameSocketTestCase(TPAuthTestCase):

    opponent_id = None
    opponent_token = None
    opponent_socket = None
    game_id = None
    game = None
    def setUp(self):
        super(GameSocketTestCase, self).setUp(socket = True)
        response = register(self, "opponent", "opponent@gmail.com", "opponent")
        self.opponent_id = response.json.get("user").get("id")
        self.opponent_token = response.json.get("token")
        self.opponent_socket = get_socket_client()
        login(self, self.opponent_socket, self.opponent_token)
        self.game = new_game(self, self.opponent_id).json.get("game")
        self.game_id = self.game.get("id")
        join_room(self.socket, self.game_id, "game")
        join_room(self.opponent_socket, self.game_id, "game")

        dumb_crawler()



    def test_init_round(self):
        print "#1 creo due round con number uguale e game uguale"
        r = Round(game_id = self.game_id, number = 1, dealer_id = self.opponent_id)
        db.session.add(r)
        r = Round(game_id = self.game_id, number = 1, dealer_id = self.opponent_id)
        db.session.add(r)
        try:
            db.session.commit()
            assert False, "Duplicate key-value not called"
        except IntegrityError:
            pass

        print "#2 Creo un round senza essere iscritto alla room"
        leave_room(self.socket, self.game_id, "game")
        response = init_round(self.socket, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
        join_room(self.socket, self.game_id, "game")

        print "#3 Creo il primo round e il dealer è il creatore della partita"
        Round.query.delete()
        response = init_round(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("round").get("dealer_id") == self.game.get("creator_id")

        print "#4 Accedo al round ma il dealer ne sta scegliendo la categoria"
        Round.query.delete()
        init_round(self.socket, self.game_id, 1)
        response = init_round(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("waiting") == "category"

        print "#5 Accedo al round ma colui che dovrebbe essere il nuovo dealer sta ancora giocando il precedente"



        print "#6 Accedo a un round senza aver risposto alle domande del precedente"
        Round.query.delete()
        response = init_round(self.socket, self.game_id, 1)
        response = init_round(self.socket, self.game_id, 2)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#7 Creo un round che non è il primo e ricevo le precedenti risposte"

        print "#7 game_id inesistente"
        Round.query.delete()
        response = init_round(self.socket, 234, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400
        print "#8 round_id casuale"
        Round.query.delete()
        response = init_round(self.socket, self.game_id, 2341)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
        print "#8 Parametri mancanti"
        print "#8.1 game_id"
        Round.query.delete()
        response = init_round(self.socket, None, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8.2 number"
        Round.query.delete()
        response = init_round(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_get_categories(self):
        print "#1 Sono dealer del round e richiedo le categorie"
        init_round(self.socket, self.game_id, 1)
        response = get_categories(self.socket, self.game_id, 1)
        assert response.json.get("success") == True
        categories = response.json.get("categories")
        n_categories = len(categories)
        assert categories

        print "#2 Le richiedo e sono le stesse"
        response = get_categories(self.socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert n_categories == len(response.json.get("categories"))
        #controllo se le categorie sono uguali (l'ordine dovrebbe anche lui essere uguale)
        for i in range(0, n_categories):
            a = categories[i]
            b = response.json.get("categories")[i]
            assert a.get("id") == b.get("id")

        print "#3 Non sono dealer e le richiedo"
        response = get_categories(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 game inesistente"
        response = get_categories(self.socket, 2342, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5 round inesistente"
        response = get_categories(self.socket, self.game_id, 441)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8 Parametri mancanti"
        print "#8.1 game_id"
        response = get_categories(self.socket, None, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8.2 number"
        response = get_categories(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#9 non appartengo alla room"
        leave_room(self.socket, self.game_id, "game")
        response = get_categories(self.socket, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_choose_category(self):
        init_round(self.socket, self.game_id, 1)
        categories = get_categories(self.socket, self.game_id, 1).json.get("categories")
        chosen_category_id = categories[0].get("id")

        print "#1 Scelgo la categoria correttamente, sono dealer del turno"
        response = choose_category(self.socket, chosen_category_id, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("category")

        print "#2 La categoria è già stata scelta"
        response = choose_category(self.socket, chosen_category_id, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 Non sono dealer"
        response = choose_category(self.opponent_socket, chosen_category_id, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 La categoria non è tra le proposte"
        #creo una categoria nuova, che non era tra le proposte
        not_proposed_category = create_random_category()
        response = choose_category(self.opponent_socket, not_proposed_category.id, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#5 Parametri inesistenti"
        print "#5.1 category"
        response = choose_category(self.socket, 324324, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.2 game_id"
        response = choose_category(self.socket, chosen_category_id, 3242, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.3 number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, 3)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6 Parametri mancanti"
        print "#6.1 category"
        response = choose_category(self.socket, None, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2 game_id"
        response = choose_category(self.socket, chosen_category_id, None, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.3 number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7 non appartengo alla room"
        leave_room(self.socket, self.game_id, "game")
        response = choose_category(self.socket, chosen_category_id, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
        
    def test_get_questions(self):
        pass
    def test_answer(self):
        pass
