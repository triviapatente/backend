# -*- coding: utf-8 -*-

from test.auth.http.api import register
from test.game.http.api import new_game, leave_game
from test.shared import get_socket_client, TPAuthTestCase
from test.base.socket.api import join_room, leave_rooms
from api import *
from tp.game.models import Round, Question, ProposedCategory, ProposedQuestion, Game
from tp.auth.models import User
from tp.events.models import Socket
from tp.base.utils import RoomType
from tp import db, app
from sqlalchemy.exc import IntegrityError
from utils import dumb_crawler, generate_random_category, generate_random_question, generateRound
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
        #creo la partita
        self.game = new_game(self, self.opponent_id).json.get("game")
        self.game_id = self.game.get("id")
        #entrambi i giocatori entrano nella room
        join_room(self.opponent_socket, self.game_id, RoomType.game.value, self.opponent_token)
        join_room(self.socket, self.game_id, RoomType.game.value, self.token)
        self.opponent_socket.get_received() #consumo l'evento user_joined provocato dal join room di self.socket
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

        print "#2: Accedo al primo round e il dealer è il creatore della partita"
        #pulisco i round della partita (come se fosse ricominciata)
        Round.query.delete()
        db.session.commit()
        #l'avversario entra nel round e gli viene indicato come procedere nella response
        response = init_round(self.opponent_socket, self.game_id, self.opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("opponent_online")
        #essendo il primo round, il dealer dev'essere chi ha creato la partita
        assert response.json.get("round").get("dealer_id") == self.game.get("creator_id")

        print "#3: Accedo al round ma colui che dovrebbe essere il nuovo dealer sta ancora giocando il precedente"
        #svolgo il primo turno ma opponent non gioca
        round_id = init_round(self.socket, self.game_id, self.token).json.get("round").get("id")
        chosen_category_id = get_categories(self.socket, self.game_id, round_id, self.token).json.get("categories")[0].get("id")
        choose_category(self.socket, chosen_category_id, self.game_id, round_id, self.token)
        self.opponent_socket.get_received() #consumo l'evento category_chosen, innescato dalla precedente chiamata a choose_category
        questions = get_questions(self.socket, self.game_id, round_id, self.token).json.get("questions")
        for question in questions:
            question_id = question.get("id")
            #risponde solo self.socket perchè self.opponent_socket è il dealer del round successivo e quindi sta ancora giocando
            answer(self.socket, True, self.game_id, round_id, question_id, self.token)
        #quando ri-accedo alla room per continuare con il round successivo mi viene comunicato che l'altro sta ancora giocando
        response = init_round(self.socket, self.game_id, self.token)
        assert response.json.get("success") == True
        assert response.json.get("waiting") == "game"

        print "#4: Chiamo init_round senza aver risposto alle domande del precedente (mi ritorna le info del round in cui sto giocando)"
        self.opponent_socket.get_received()
        #opponent accede senza completare il primo turno al secondo turno
        response = init_round(self.opponent_socket, self.game_id, self.opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("round").get("number") == 1

        print "#5: Accedo al round ma il dealer ne sta scegliendo la categoria"
        #rispondo alle domande anche con opponent, finendo lo svolgimento del turno
        for question in questions:
            question_id = question.get("id")
            answer(self.opponent_socket, True, self.game_id, round_id, question_id, self.opponent_token)
        self.socket.get_received() #consumo l'evento round_ended

        #accedo nuovamente al round con lo stesso giocatore, ma ora è opponent a dover scegliere la categoria
        response = init_round(self.socket, self.game_id, self.token)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("waiting") == "category"

        print "#6: game_id inesistente"
        response = init_round(self.socket, 234, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: Parametri mancanti"
        print "#7.1: game_id"
        response = init_round(self.socket, None, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8: Accedo a un round senza essere iscritto alla room"
        leave_rooms(self.socket, RoomType.game.value, self.token)
        response = init_round(self.socket, self.game_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        join_room(self.socket, self.game_id, RoomType.game.value, self.token)
        self.opponent_socket.get_received() #consumo l'evento user_joined provocato dal join room di self.socket
        numberOfRounds = app.config["NUMBER_OF_ROUNDS"]
        print "#9: Dopo %d turni la partita finisce" % numberOfRounds
        #svolgo i turni
        limit = (numberOfRounds / 2) + 1
        for i in range(1, limit):
            #svolgo il turno con dealer opponent
            generateRound(self.game_id, (self.opponent_socket, True, self.opponent_token), (self.socket, True, self.token))
            #svolgo il turno con dealer user
            generateRound(self.game_id, (self.socket, True, self.token), (self.opponent_socket, True, self.opponent_token))

        #adesso provando ad accedere al round successivo dovrei ottenere l'update dei punteggi
        response = init_round(self.opponent_socket, self.game_id, self.token)
        #chiamo due volte per consumare gli eventi
        response = init_round(self.opponent_socket, self.game_id, self.token)
        assert response.json.get("ended")
        partecipations = response.json.get("partecipations")
        assert partecipations
        socket_response = self.socket.get_received()
        assert socket_response.json.get("winner_id") == response.json.get("winner_id")
        # controllo che tutti i giocatori abbiano avuto un cambiamento nel punteggio
        for p in partecipations:
            score_inc = p.get("score_increment")
            print "User %s got score increment: %d" % (p.get("user_id"), score_inc)
            assert score_inc != 0
        print "#9.1 draw: no winner"
        assert response.json.get("winner_id") == None

        print "#9.2 user win"
        #creo una nuova partita
        self.game = new_game(self, self.opponent_id).json.get("game")
        self.game_id = self.game.get("id")
        #entrambi i giocatori entrano nella room
        join_room(self.opponent_socket, self.game_id, RoomType.game.value, self.opponent_token)
        join_room(self.socket, self.game_id, RoomType.game.value, self.token)
        #consumo l'evento user_joined provocato dal join room di self.socket
        self.opponent_socket.get_received()
        #accetto la partita con opponent_socket
        init_round(self.opponent_socket, self.game_id, self.opponent_token)
        #svolgo i turni con risposte diverse per i giocatori
        for i in range(0, limit):
            #svolgo il turno con dealer user
            generateRound(self.game_id, (self.socket, True, self.token), (self.opponent_socket, False, self.opponent_token))
            if i != limit - 1:
                #svolgo il turno con dealer opponent
                generateRound(self.game_id, (self.opponent_socket, False, self.opponent_token), (self.socket, True, self.token))
        #adesso provando ad accedere al round successivo dovrei ottenere l'update dei punteggi
        response = init_round(self.opponent_socket, self.game_id, self.token)
        #doppia chiamata per togliere gli eventi
        response = init_round(self.opponent_socket, self.game_id, self.token)
        assert response.json.get("ended")
        partecipations = response.json.get("partecipations")
        assert partecipations
        # controllo che tutti i giocatori abbiano avuto un cambiamento nel punteggio
        for p in partecipations:
            score_inc = p.get("score_increment")
            print "User %s got score increment: %d" % (p.get("user_id"), score_inc)
            assert score_inc != 0
        # controllo che abbia vinto user
        assert response.json.get("winner_id") == self.user.get("id")

        print "#10: Creo una partita, e accedo al round senza che l'utente abbia accettato l'invito"
        self.game = new_game(self, self.opponent_id).json.get("game")
        join_room(self.socket, self.game.get("id"), RoomType.game.value, self.token)
        response = init_round(self.socket, self.game.get("id"), self.token)
        assert response.json.get("success") == True
        assert response.json.get("waiting") == "category"

    def test_get_categories(self):
        round_id = init_round(self.socket, self.game_id, self.token).json.get("round").get("id")

        print "#1: Sono dealer del round e richiedo le categorie"
        response = get_categories(self.socket, self.game_id, round_id, self.token)
        assert response.json.get("success") == True
        categories = response.json.get("categories")
        assert categories

        print "#2: Le richiedo e sono le stesse"
        n_categories = len(categories)
        response = get_categories(self.socket, self.game_id, round_id, self.token)
        assert response.json.get("success") == True
        assert n_categories == len(response.json.get("categories"))
        #controllo se le categorie sono uguali (l'ordine dovrebbe anche lui essere uguale)
        for i in range(0, n_categories):
            a = categories[i]
            b = response.json.get("categories")[i]
            assert a.get("id") == b.get("id")

        print "#3: Non sono dealer e le richiedo"
        response = get_categories(self.opponent_socket, self.game_id, round_id, self.opponent_token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4: game inesistente"
        response = get_categories(self.socket, 2342, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5: round inesistente"
        response = get_categories(self.socket, self.game_id, 441, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6: Parametri mancanti"
        print "#6.1: game_id"
        response = get_categories(self.socket, None, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2: number"
        response = get_categories(self.socket, self.game_id, None, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: non appartengo alla room"
        leave_rooms(self.socket, RoomType.game.value, self.token)
        response = get_categories(self.socket, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_choose_category(self):
        round_id = init_round(self.socket, self.game_id, self.token).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id, self.token).json.get("categories")
        chosen_category_id = categories[0].get("id")

        print "#1: La categoria non è tra le proposte"
        #creo una categoria nuova, che non era tra le proposte
        not_proposed_category = generate_random_category()
        response = choose_category(self.socket, not_proposed_category.id, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#2: Non sono dealer"
        response = choose_category(self.opponent_socket, chosen_category_id, self.game_id, round_id, self.opponent_token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: Scelgo la categoria correttamente, sono dealer del turno"
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id, self.token)
        assert response.json.get("success") == True
        assert response.json.get("category")

        print "#4: Event Test: controllo che all'avversario sia arrivato l'evento correttamente"
        response = self.opponent_socket.get_received() #consumo l'evento category_chosen, innescato dalla precedente chiamata a chosen_category
        assert response.json.get("action") == "create"
        assert response.json.get("user")
        assert response.json.get("category")

        print "#5: La categoria è già stata scelta"
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#6: Parametri inesistenti"
        print "#6.1: category"
        response = choose_category(self.socket, 324324, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2: game_id"
        response = choose_category(self.socket, chosen_category_id, 3242, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.3: number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, 3234, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: Parametri mancanti"
        print "#7.1: category"
        response = choose_category(self.socket, None, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.2: game_id"
        response = choose_category(self.socket, chosen_category_id, None, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.3: number"
        response = choose_category(self.socket, chosen_category_id, self.game_id, None, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8: Non appartengo alla room"
        leave_rooms(self.socket, RoomType.game.value, self.token)
        response = choose_category(self.socket, chosen_category_id, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_get_questions(self):
        round_id = init_round(self.socket, self.game_id, self.token).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id, self.token).json.get("categories")
        chosen_category_id = categories[0].get("id")

        print "#1: Non ho ancora scelto la categoria"
        response = get_questions(self.socket, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        choose_category(self.socket, chosen_category_id, self.game_id, round_id, self.token)
        self.opponent_socket.get_received() #consumo l'evento category_chosen, innescato dalla precedente chiamata a choose_category

        print "#2: Ottengo correttamente le domande come primo utente"
        response = get_questions(self.socket, self.game_id, round_id, self.token)
        assert response.json.get("success") == True
        questions_a = response.json.get("questions")
        assert questions_a

        print "#2.1: Le domande sono ordinate per id"
        ids = [q.get("id") for q in questions_a]
        assert ids == sorted(ids)

        print "#3: Ottengo correttamente le domande come secondo utente"
        response = get_questions(self.opponent_socket, self.game_id, round_id, self.opponent_token)
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
        response = get_questions(self.socket, self.game_id, 234234, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5.2: game"
        response = get_questions(self.socket, 4543, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6: Parametri mancanti"
        print "#6.1: round_id"
        response = get_questions(self.socket, self.game_id, None, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#6.2: game"
        response = get_questions(self.socket, None, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7: Non appartengo alla room"
        leave_rooms(self.socket, RoomType.game.value, self.token)
        response = get_questions(self.socket, self.game_id, round_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_answer(self):
        round_id = init_round(self.socket, self.game_id, self.token).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id, self.token).json.get("categories")
        chosen_category_id = categories[0].get("id")
        choose_category(self.socket, chosen_category_id, self.game_id, round_id, self.token)
        self.opponent_socket.get_received() #consumo l'evento category_chosen, innescato dalla precedente chiamata a choose_category
        questions = get_questions(self.opponent_socket, self.game_id, round_id, self.opponent_token).json.get("questions")
        question_id = questions[0].get("id")
        print "#1: Rispondo a una domanda che non mi è stata posta"
        not_proposed_question = generate_random_question(chosen_category_id)
        response = answer(self.socket, False, self.game_id, round_id, not_proposed_question.id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#2: rispondo a una domanda di un'altra categoria che non mi è stata posta"
        not_proposed_question = generate_random_question(categories[1].get("id"))
        response = answer(self.socket, False, self.game_id, round_id, not_proposed_question.id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: rispondo alla domanda senza nessun errore del server"
        #rispondo con true per verificare poi la correttezza
        response = answer(self.socket, True, self.game_id, round_id, question_id, self.token)
        assert response.json.get("success") == True
        correct_answer = response.json.get("correct_answer")
        assert correct_answer is not None
        print "#3.1 la risposta è corretta"
        assert correct_answer

        print "#5 Event Test: arriva l'evento round_ended corretto all'avversario, quando rispondo a tutte le domande"
        answer(self.socket, True, self.game_id, round_id, questions[1].get("id"), self.token)
        answer(self.socket, True, self.game_id, round_id, questions[2].get("id"), self.token)
        answer(self.socket, True, self.game_id, round_id, questions[3].get("id"), self.token)
        #consumo l'evento round_ended
        round_ended_response = self.opponent_socket.get_received(3)
        assert round_ended_response.json.get("action") == "destroy"
        assert round_ended_response.json.get("round").get("id") == round_id
        assert round_ended_response.json.get("user").get("id") == self.user.get("id")

        print "#6: Rispondo a una domanda a cui ho già risposto"
        response = answer(self.socket, False, self.game_id, round_id, question_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#7 Parametri mancanti"
        print "#7.1: answer"
        response = answer(self.socket, None, self.game_id, round_id, question_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.2: game"
        response = answer(self.socket, True, None, round_id, question_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.3: round"
        response = answer(self.socket, False, self.game_id, None, question_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#7.4: quiz"
        response = answer(self.socket, True, self.game_id, round_id, None, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8: Parametri inesistenti"
        print "#8.1: game"
        response = answer(self.socket, True, 234234, round_id, question_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8.2: round"
        response = answer(self.socket, False, self.game_id, 3434, question_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8.3: quiz"
        response = answer(self.socket, True, self.game_id, round_id, 45454, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#9: Non sono iscritto alla room"
        leave_rooms(self.socket, RoomType.game.value, self.token)
        response = answer(self.socket, True, self.game_id, round_id, question_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

    def test_round_details(self):
        NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]

        print "#1: Faccio la richiesta senza essermi iscritto alla room"
        leave_rooms(self.socket, RoomType.game.value, self.token)
        response = round_details(self.socket, self.game_id, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
        join_room(self.socket, self.game_id, RoomType.game.value, self.token)

        print "#2: Dopo 2 round in cui entrambi han risposto a tutto, mi vengono ritornate NUMBER_OF_QUESTIONS_PER_ROUND * 2 round * 2 utenti"
        generateRound(self.game_id, (self.socket, True, self.token), (self.opponent_socket, True, self.opponent_token))
        generateRound(self.game_id, (self.opponent_socket, True, self.opponent_token), (self.socket, True, self.token))
        response = round_details(self.socket, self.game_id, self.token)
        users = response.json.get("users")
        quizzes = response.json.get("quizzes")
        answers = response.json.get("answers")
        categories = response.json.get("categories")
        assert len(users) == 2
        assert len(quizzes) == (NUMBER_OF_QUESTIONS_PER_ROUND * 2)
        assert len(answers) == len(quizzes) * len(users)
        assert len(categories) == (len(quizzes) / NUMBER_OF_QUESTIONS_PER_ROUND)

        print "#3: Dopo 3 round in cui io ho risposto a tutto, l'altro ha risposto a n domande su 4 del 3 (con n < 4)"
        print "#3.1: mi vengono ritornate NUMBER_OF_QUESTIONS_PER_ROUND * 3 round * 2 utenti"
        round_id = init_round(self.socket, self.game_id, self.token).json.get("round").get("id")
        categories = get_categories(self.socket, self.game_id, round_id, self.token).json.get("categories")
        chosen_category_id = categories[0].get("id")
        choose_category(self.socket, chosen_category_id, self.game_id, round_id, self.token)
        self.opponent_socket.get_received() #consumo l'evento category_chosen, innescato dalla precedente chiamata a choose_category
        questions = get_questions(self.opponent_socket, self.game_id, round_id, self.opponent_token).json.get("questions")
        #n = numero di risposte date dall'avversario
        n = NUMBER_OF_QUESTIONS_PER_ROUND - 1
        for i in range(0, len(questions)):
            question_id = questions[i].get("id")
            answer(self.socket, True, self.game_id, round_id, question_id, self.token)
            self.opponent_socket.get_received()
            if i != n:
                answer(self.opponent_socket, True, self.game_id, round_id, question_id, self.opponent_token)
                self.socket.get_received()

        response = round_details(self.socket, self.game_id, self.token)
        users = response.json.get("users")
        quizzes = response.json.get("quizzes")
        answers = response.json.get("answers")
        categories = response.json.get("categories")
        assert len(users) == 2
        assert len(quizzes) == (NUMBER_OF_QUESTIONS_PER_ROUND * 3)
        assert len(answers) == len(quizzes) * len(users) - (NUMBER_OF_QUESTIONS_PER_ROUND - n)
        assert len(categories) == (len(quizzes) / NUMBER_OF_QUESTIONS_PER_ROUND)

        print "#3.2: all'avversario vengono ritornate NUMBER_OF_QUESTIONS_PER_ROUND * 3 round * 2 utenti - (NUMBER_OF_QUESTIONS_PER_ROUND - n) * 2"
        response = round_details(self.opponent_socket, self.game_id, self.opponent_token)
        users = response.json.get("users")
        quizzes = response.json.get("quizzes")
        answers = response.json.get("answers")
        categories = response.json.get("categories")
        quizzes_length = len(quizzes)
        assert len(users) == 2
        assert quizzes_length == (NUMBER_OF_QUESTIONS_PER_ROUND * 3)
        assert len(answers) == quizzes_length * len(users) - (NUMBER_OF_QUESTIONS_PER_ROUND - n) * 2
        assert len(categories) == (quizzes_length / NUMBER_OF_QUESTIONS_PER_ROUND)

        print "#3.3: All'avversario non vengono ritornate le soluzioni dei quiz non giocati"
        assert quizzes[quizzes_length - 2].get("answer") is not None
        assert quizzes[quizzes_length - 1].get("answer") is None

        print "#4: Event test: round_ended"
        answer(self.opponent_socket, True, self.game_id, round_id, question_id, self.opponent_token)
        response = self.socket.get_received()
        assert response.json.get("round")

        print "#5: Event test: user_answered"
        round_id = init_round(self.opponent_socket, self.game_id, self.opponent_token).json.get("round").get("id")
        categories = get_categories(self.opponent_socket, self.game_id, round_id, self.opponent_token).json.get("categories")
        chosen_category_id = categories[0].get("id")
        choose_category(self.opponent_socket, chosen_category_id, self.game_id, round_id, self.opponent_token)
        self.socket.get_received() #consumo l'evento category_chosen, innescato dalla precedente chiamata a choose_category
        questions = get_questions(self.opponent_socket, self.game_id, round_id, self.opponent_token).json.get("questions")
        answer(self.opponent_socket, True, self.game_id, round_id, questions[0].get("id"), self.opponent_token)
        #evento user answered
        response = self.socket.get_received()
        user_answer = response.json.get("answer")
        assert user_answer
        assert user_answer.get("answer") is None
        assert user_answer.get("correct") is not None

        print "#6: Abbandono il gioco, ritorna ended = true, winner e partecipations"
        leave_game(self, self.game_id)
        response = round_details(self.socket, self.game_id, self.token)
        users = response.json.get("users")
        quizzes = response.json.get("quizzes")
        answers = response.json.get("answers")
        categories = response.json.get("categories")
        partecipations = response.json.get("partecipations")
        winner_id = response.json.get("winner_id")
        assert len(users) == 2
        assert len(quizzes) == (NUMBER_OF_QUESTIONS_PER_ROUND * 4)
        assert len(answers) == (len(quizzes) - NUMBER_OF_QUESTIONS_PER_ROUND) * len(users)
        assert len(partecipations) == len(users)
        assert len(categories) == (len(quizzes) / NUMBER_OF_QUESTIONS_PER_ROUND)
        assert response.json.get("game").get("ended") == True
        assert response.json.get("game").get("winner_id") == self.opponent_id

        print "#7: Parametri mancanti"
        print "#7.1 game"
        response = round_details(self.socket, None, self.token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_user_online(self):
        user_id = self.user.get("id")
        print "#1: Io sono online"
        assert is_user_online(self.socket, self.game_id, user_id, self.token) == True
        print "#2: Il mio opponent è online"
        assert is_user_online(self.socket, self.game_id, self.opponent_id, self.token) == True
        print "#3: Il mio opponent esce, ed è offline"
        return
        leave_rooms(self.opponent_socket, "game", self.opponent_token)
        self.socket.get_received()
        assert is_user_online(self.socket, self.game_id, self.opponent_id, self.token) == False
        print "#4: Io esco, io sono offline"
        leave_rooms(self.socket, "game", self.token)
        self.opponent_socket.get_received()
        assert is_user_online(self.socket, self.game_id, user_id, self.token) == False
        print "#5: Mi disconnetto, la mia istanza socket viene eliminata"
        self.socket.disconnect()
        assert Socket.query.filter(Socket.user_id == user_id).count() == 0
        print "#6: L'avversario si disconnette, l'istanza socket viene eliminata"
        self.opponent_socket.disconnect()
        assert Socket.query.filter(Socket.user_id == self.opponent_id).count() == 0
        print "#6.1: Ora sono offline"
        assert is_user_online(self.socket, self.game_id, user_id, self.token) == False
        print "#6.2: L'avversario è offline"
        assert is_user_online(self.socket, self.game_id, self.opponent_id, self.token) == False
