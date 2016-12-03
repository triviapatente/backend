# -*- coding: utf-8 -*-

from tp.game.models import Category, Quiz
from tp import db
from api import init_round, get_categories, choose_category, get_questions, answer
#metodo che genera un set fittizio di categorie e quiz per non evocare il vero e proprio crawler a ogni test
def dumb_crawler():
    for i in range(0, 10):
        c = Category(name= "category_%d" % i)
        db.session.add(c)
        db.session.commit()
        for n in range(0, 40):
            # risposta corretta è sempre quella vera per semplificare il test delle vittorie
            q = Quiz(category_id = c.id, question = "Quiz %d della categoria %d" % (n, i), answer = True)
            db.session.add(q)
        db.session.commit()

#funzione che genera una categoria
def generate_random_category():
    c = Category(name= "category_100")
    db.session.add(c)
    db.session.commit()
    return c

#funzione che genera una domanda
def generate_random_question(category_id):
    q = Quiz(question= "question x", answer = True, category_id = category_id)
    db.session.add(q)
    db.session.commit()
    return q

#funzione che svolge un turno. I sockets devono essere forniti con quest'ordine: dealer, altri
#i sockets sono una coppia: socket, socket_answer
def generateRound(game_id, *sockets):
    dealer_socket = sockets[0][0]
    opponent_socket = sockets[1][0]
    round_id = init_round(dealer_socket, game_id).json.get("round").get("id")
    chosen_category_id = get_categories(dealer_socket, game_id, round_id).json.get("categories")[0].get("id")
    choose_category(dealer_socket, chosen_category_id, game_id, round_id)
    questions = get_questions(dealer_socket, round_id, game_id).json.get("questions")

    dealer_answer = sockets[0][1]
    opponent_answer = sockets[1][1]
    for question in questions:
        question_id = question.get("id")
        for (socket, socket_answer) in sockets:
            answer(socket, socket_answer, game_id, round_id, question_id)
            for (opponent, _) in sockets:
                if opponent != socket:
                    opponent.get_received() #consumo l'evento question_answered
