# -*- coding: utf-8 -*-

from test.auth.http.api import register
from test.auth.socket.api import login
from test.game.http.api import new_game
from test.shared import get_socket_client, TPAuthTestCase
from test.base.socket.api import join_room, leave_room
from api import *
from tp.game.models import Round, Question, ProposedCategory, ProposedQuestion
from tp import db
from sqlalchemy.exc import IntegrityError
from utils import dumb_crawler, generate_random_category, generate_random_question
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
        db.session.commit()
        response = init_round(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("round").get("dealer_id") == self.game.get("creator_id")

        print "#4 Accedo al round ma il dealer ne sta scegliendo la categoria"
        Round.query.delete()
        db.session.commit()
        init_round(self.socket, self.game_id, 1)
        response = init_round(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("waiting") == "category"

        print "#5 Accedo al round ma colui che dovrebbe essere il nuovo dealer sta ancora giocando il precedente"



        print "#6 Accedo a un round senza aver risposto alle domande del precedente"
        Round.query.delete()
        db.session.commit()
        response = init_round(self.socket, self.game_id, 1)
        response = init_round(self.socket, self.game_id, 2)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#7 Creo un round che non è il primo e ricevo le precedenti risposte"
        Round.query.delete()
        db.session.commit()
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        chosen_category_id = get_categories(self.socket, self.game_id, round_id).json.get("categories")[0].get("id")
        choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        questions = get_questions(self.socket, round_id, self.game_id).json.get("questions")
        for question in questions:
            question_id = question.get("id")
            answer(self.socket, True, self.game_id, round_id, question_id)
            answer(self.opponent_socket, False, self.game_id, round_id, question_id)

        response = init_round(self.socket, self.game_id, 2)
        assert response.json.get("success") == True
        assert response.json.get("previous_answers")
        Question.query.delete()
        ProposedCategory.query.delete()
        ProposedQuestion.query.delete()
        Round.query.delete()
        db.session.commit()

        print "#7 game_id inesistente"
        response = init_round(self.socket, 234, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8 round_id casuale"
        response = init_round(self.socket, self.game_id, 2341)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#8 Parametri mancanti"
        print "#8.1 game_id"
        response = init_round(self.socket, None, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8.2 number"
        response = init_round(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_get_categories(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")

        print "#1 Sono dealer del round e richiedo le categorie"
        response = get_categories(self.socket, self.game_id, round_id)
        assert response.json.get("success") == True
        categories = response.json.get("categories")
        n_categories = len(categories)
        assert categories

        print "#2 Le richiedo e sono le stesse"
        response = get_categories(self.socket, self.game_id, round_id)
        assert response.json.get("success") == True
        assert n_categories == len(response.json.get("categories"))
        #controllo se le categorie sono uguali (l'ordine dovrebbe anche lui essere uguale)
        for i in range(0, n_categories):
            a = categories[i]
            b = response.json.get("categories")[i]
            assert a.get("id") == b.get("id")

        print "#3 Non sono dealer e le richiedo"
        response = get_categories(self.opponent_socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 game inesistente"
        response = get_categories(self.socket, 2342, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5 round inesistente"
        response = get_categories(self.socket, self.game_id, 441)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8 Parametri mancanti"
        print "#8.1 game_id"
        response = get_categories(self.socket, None, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8.2 number"
        response = get_categories(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#9 non appartengo alla room"
        leave_room(self.socket, self.game_id, "game")
        response = get_categories(self.socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_choose_category(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id).json.get("categories")
        chosen_category_id = categories[0].get("id")

        print "#1 La categoria non è tra le proposte"
        #creo una categoria nuova, che non era tra le proposte
        not_proposed_category = generate_random_category()
        response = choose_category(self.socket, not_proposed_category.id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#2 Non sono dealer"
        response = choose_category(self.opponent_socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3 Scelgo la categoria correttamente, sono dealer del turno"
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == True
        assert response.json.get("category")

        print "#4 La categoria è già stata scelta"
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#5 Parametri inesistenti"
        print "#5.1 category"
        response = choose_category(self.socket, 324324, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.2 game_id"
        response = choose_category(self.socket, chosen_category_id, 3242, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.3 number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, 3234)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6 Parametri mancanti"
        print "#6.1 category"
        response = choose_category(self.socket, None, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2 game_id"
        response = choose_category(self.socket, chosen_category_id, None, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.3 number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7 non appartengo alla room"
        leave_room(self.socket, self.game_id, "game")
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_get_questions(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id).json.get("categories")
        chosen_category_id = categories[0].get("id")

        print "#1 non ho ancora scelto la categoria"
        response = get_questions(self.socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        choose_category(self.socket, chosen_category_id, self.game_id, round_id)

        print "#2 non appartengo alla room"
        leave_room(self.socket, self.game_id, "game")
        response = get_questions(self.socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
        join_room(self.socket, self.game_id, "game")

        print "#3 ottengo correttamente le domande come primo utente"
        response = get_questions(self.socket, self.game_id, round_id)
        assert response.json.get("success") == True
        questions_a = response.json.get("questions")
        assert questions_a

        print "#4 ottengo correttamente le domande come secondo utente"
        response = get_questions(self.opponent_socket, self.game_id, round_id)
        assert response.json.get("success") == True
        questions_b = response.json.get("questions")
        assert questions_b

        print "#5 Le richiedo e sono le stesse"
        n_questions = len(questions_a)
        assert n_questions == len(questions_b)

        for i in range(0, n_questions):
            a = questions_a[i]
            b = questions_b[i]
            assert a.get("id") == b.get("id")

        print "#6 Parametri inesistenti"
        print "#6.1 round_id"
        response = get_questions(self.socket, self.game_id, 234234)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2 game"
        response = get_questions(self.socket, 4543, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7 Parametri mancanti"
        print "#7.1 round_id"
        response = get_questions(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.2 game"
        response = get_questions(self.socket, None, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_answer(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id).json.get("categories")
        chosen_category_id = categories[0].get("id")
        choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        question_id = get_questions(self.opponent_socket, self.game_id, round_id).json.get("questions")[0].get("id")

        print "#1 non sono iscritto alla room"
        leave_room(self.socket, self.game_id, "game")
        response = answer(self.socket, True, self.game_id, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
        join_room(self.socket, self.game_id, "game")

        print "#2 rispondo a una domanda che non mi è stata posta"
        not_proposed_question = generate_random_question(chosen_category_id)
        response = answer(self.socket, False, self.game_id, round_id, not_proposed_question.id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3 rispondo a una domanda di un'altra categoria che non mi è stata posta"
        not_proposed_question = generate_random_question(categories[1].get("id"))
        response = answer(self.socket, False, self.game_id, round_id, not_proposed_question.id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 rispondo alla domanda senza nessun errore del server"
        response = answer(self.socket, True, self.game_id, round_id, question_id)
        assert response.json.get("success") == True
        assert response.json.get("correct_answer") is not None

        print "#5 rispondo a una domanda a cui ho già risposto"
        response = answer(self.socket, False, self.game_id, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#6 Parametri mancanti"
        print "#6.1 answer"
        response = answer(self.socket, None, self.game_id, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2 game"
        response = answer(self.socket, True, None, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.3 round"
        response = answer(self.socket, False, self.game_id, None, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.4 quiz"
        response = answer(self.socket, True, self.game_id, round_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7 Parametri inesistenti"
        print "#7.1 game"
        response = answer(self.socket, True, 234234, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.2 round"
        response = answer(self.socket, False, self.game_id, 3434, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.3 quiz"
        response = answer(self.socket, True, self.game_id, round_id, 45454)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400
