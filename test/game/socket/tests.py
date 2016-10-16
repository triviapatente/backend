# -*- coding: utf-8 -*-

from test.auth.http.api import register
from test.auth.socket.api import login
from test.game.http.api import new_game
from test.shared import get_socket_client, TPAuthTestCase
from test.base.socket.api import join_room, leave_room
from api import *
from tp.game.models import Round, Question, ProposedCategory, ProposedQuestion
from tp import db
from tp.base.utils import RoomType
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
        #creo un avversario
        response = register(self, "opponent", "opponent@gmail.com", "opponent")
        self.opponent_id = response.json.get("user").get("id")
        self.opponent_token = response.json.get("token")
        self.opponent_socket = get_socket_client()
        #effettuo il login
        login(self, self.opponent_socket, self.opponent_token)
        #creo la partita
        self.game = new_game(self, self.opponent_id).json.get("game")
        self.game_id = self.game.get("id")
        #entrambi i giocatori entrano nella room
        join_room(self.socket, self.game_id, RoomType.game.value)
        join_room(self.opponent_socket, self.game_id, RoomType.game.value)
        #faccio partire il dumb crawler, per generare categorie e domande casualmente
        dumb_crawler()

    def test_init_round(self):
        print "#1: Creo due round con number uguale e game uguale"
        r = Round(game_id = self.game_id, number = 1, dealer_id = self.opponent_id)
        db.session.add(r)
        r = Round(game_id = self.game_id, number = 1, dealer_id = self.opponent_id)
        db.session.add(r)
        try:
            db.session.commit()
            #se non crea un'eccezione è un problema
            assert False, "Duplicate key-value not called"
        except IntegrityError:
            #annullo la transazione
            db.session.rollback()

        print "#2: Accedo al primo round ma il dealer è il creatore della partita"
        #pulisco i round della partita (come se fosse ricominciata)
        Round.query.delete()
        db.session.commit()
        #l'avversario entra nel round e gli viene indicato come procedere nella response
        response = init_round(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("round")
        #essendo il primo round, il dealer dev'essere chi ha creato la partita
        assert response.json.get("round").get("dealer_id") == self.game.get("creator_id")

        print "#3: Accedo al round ma colui che dovrebbe essere il nuovo dealer sta ancora giocando il precedente"
        #svolgo il primo turno ma opponent non gioca
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        chosen_category_id = get_categories(self.socket, self.game_id, round_id).json.get("categories")[0].get("id")
        choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        questions = get_questions(self.socket, round_id, self.game_id).json.get("questions")
        for question in questions:
            question_id = question.get("id")
            #risponde solo self.socket perchè self.opponent_socket è il dealer del round successivo e quindi sta ancora giocando
            answer(self.socket, True, self.game_id, round_id, question_id)
        #quando ri-accedo alla room per continuare con il round successivo mi viene comunicato che l'altro sta ancora giocando
        response = init_round(self.socket, self.game_id, 2)
        assert response.json.get("success") == True
        assert response.json.get("waiting") == "game"

        print "#4: Accedo a un round senza aver risposto alle domande del precedente"
        #opponent accede senza completare il primo turno al secondo turno
        response = init_round(self.opponent_socket, self.game_id, 2)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#5: Accedo al round ma il dealer ne sta scegliendo la categoria"
        #rispondo alle domande anche con opponent, finendo lo svolgimento del turno
        for question in questions:
            question_id = question.get("id")
            answer(self.opponent_socket, True, self.game_id, round_id, question_id)
        #accedo nuovamente al round con lo stesso giocatore, ma ora è opponent a dover scegliere la categoria
        response = init_round(self.socket, self.game_id, 2)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("waiting") == "category"

        print "#6: Accedo ad un round diverso dal primo e ricevo le precedenti risposte"
        assert response.json.get("previous_answers")

        print "#7: game_id inesistente"
        response = init_round(self.socket, 234, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8: round_id casuale"
        response = init_round(self.socket, self.game_id, 2341)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#9: Parametri mancanti"
        print "#9.1: game_id"
        response = init_round(self.socket, None, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#9.2: number"
        response = init_round(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#10: Accedo a un round senza essere iscritto alla room"
        leave_room(self.socket, self.game_id, "game")
        response = init_round(self.socket, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_get_categories(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")

        print "#1: Sono dealer del round e richiedo le categorie"
        response = get_categories(self.socket, self.game_id, round_id)
        assert response.json.get("success") == True
        categories = response.json.get("categories")
        assert categories

        print "#2: Le richiedo e sono le stesse"
        n_categories = len(categories)
        response = get_categories(self.socket, self.game_id, round_id)
        assert response.json.get("success") == True
        assert n_categories == len(response.json.get("categories"))
        #controllo se le categorie sono uguali (l'ordine dovrebbe anche lui essere uguale)
        for i in range(0, n_categories):
            a = categories[i]
            b = response.json.get("categories")[i]
            assert a.get("id") == b.get("id")

        print "#3: Non sono dealer e le richiedo"
        response = get_categories(self.opponent_socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4: game inesistente"
        response = get_categories(self.socket, 2342, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5: round inesistente"
        response = get_categories(self.socket, self.game_id, 441)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6: Parametri mancanti"
        print "#6.1: game_id"
        response = get_categories(self.socket, None, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2: number"
        response = get_categories(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: non appartengo alla room"
        leave_room(self.socket, self.game_id, RoomType.game.value)
        response = get_categories(self.socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_choose_category(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id).json.get("categories")
        chosen_category_id = categories[0].get("id")

        print "#1: La categoria non è tra le proposte"
        #creo una categoria nuova, che non era tra le proposte
        not_proposed_category = generate_random_category()
        response = choose_category(self.socket, not_proposed_category.id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#2: Non sono dealer"
        response = choose_category(self.opponent_socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: Scelgo la categoria correttamente, sono dealer del turno"
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == True
        assert response.json.get("category")

        print "#4: La categoria è già stata scelta"
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#5: Parametri inesistenti"
        print "#5.1: category"
        response = choose_category(self.socket, 324324, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.2: game_id"
        response = choose_category(self.socket, chosen_category_id, 3242, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.3: number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, 3234)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6: Parametri mancanti"
        print "#6.1: category"
        response = choose_category(self.socket, None, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2: game_id"
        response = choose_category(self.socket, chosen_category_id, None, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.3: number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: Non appartengo alla room"
        leave_room(self.socket, self.game_id, RoomType.game.value)
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_get_questions(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id).json.get("categories")
        chosen_category_id = categories[0].get("id")

        print "#1: Non ho ancora scelto la categoria"
        response = get_questions(self.socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        choose_category(self.socket, chosen_category_id, self.game_id, round_id)

        print "#2: Ottengo correttamente le domande come primo utente"
        response = get_questions(self.socket, self.game_id, round_id)
        assert response.json.get("success") == True
        questions_a = response.json.get("questions")
        assert questions_a

        print "#3: Ottengo correttamente le domande come secondo utente"
        response = get_questions(self.opponent_socket, self.game_id, round_id)
        assert response.json.get("success") == True
        questions_b = response.json.get("questions")
        assert questions_b

        print "#4: Le richiedo e sono le stesse"
        n_questions = len(questions_a)
        assert n_questions == len(questions_b)
        #controllo anche il contenuto e l'ordine
        for i in range(0, n_questions):
            a = questions_a[i]
            b = questions_b[i]
            assert a.get("id") == b.get("id")

        print "#5: Parametri inesistenti"
        print "#5.1: round_id"
        response = get_questions(self.socket, self.game_id, 234234)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.2: game"
        response = get_questions(self.socket, 4543, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6: Parametri mancanti"
        print "#6.1: round_id"
        response = get_questions(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2: game"
        response = get_questions(self.socket, None, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: Non appartengo alla room"
        leave_room(self.socket, self.game_id, RoomType.game.value)
        response = get_questions(self.socket, self.game_id, round_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_answer(self):
        round_id = init_round(self.socket, self.game_id, 1).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id).json.get("categories")
        chosen_category_id = categories[0].get("id")
        choose_category(self.socket, chosen_category_id, self.game_id, round_id)
        question_id = get_questions(self.opponent_socket, self.game_id, round_id).json.get("questions")[0].get("id")

        print "#1: Rispondo a una domanda che non mi è stata posta"
        not_proposed_question = generate_random_question(chosen_category_id)
        response = answer(self.socket, False, self.game_id, round_id, not_proposed_question.id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#2: rispondo a una domanda di un'altra categoria che non mi è stata posta"
        not_proposed_question = generate_random_question(categories[1].get("id"))
        response = answer(self.socket, False, self.game_id, round_id, not_proposed_question.id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: rispondo alla domanda senza nessun errore del server"
        response = answer(self.socket, True, self.game_id, round_id, question_id)
        assert response.json.get("success") == True
        assert response.json.get("correct_answer") is not None

        print "#4: Rispondo a una domanda a cui ho già risposto"
        response = answer(self.socket, False, self.game_id, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#5 Parametri mancanti"
        print "#5.1: answer"
        response = answer(self.socket, None, self.game_id, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.2: game"
        response = answer(self.socket, True, None, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.3: round"
        response = answer(self.socket, False, self.game_id, None, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.4: quiz"
        response = answer(self.socket, True, self.game_id, round_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6: Parametri inesistenti"
        print "#6.1: game"
        response = answer(self.socket, True, 234234, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2: round"
        response = answer(self.socket, False, self.game_id, 3434, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.3: quiz"
        response = answer(self.socket, True, self.game_id, round_id, 45454)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: Non sono iscritto alla room"
        leave_room(self.socket, self.game_id, RoomType.game.value)
        response = answer(self.socket, True, self.game_id, round_id, question_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
