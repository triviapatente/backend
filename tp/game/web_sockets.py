# -*- coding: utf-8 -*-
from flask import g, request
from tp import socketio, app
from tp.ws_decorators import ws_auth_required, filter_input_room, check_in_room
from tp.base.utils import roomName
from tp.game.utils import get_dealer
from tp.game.models import Game, Question, Round, Category, Quiz
from tp.decorators import needs_values, fetch_models
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g

#TODO: test
@socketio.on("round")
@needs_values("SOCKET", "number", "game")
@fetch_models({"game": Game})
@check_in_room("game", "game")
def init_round(data):
    #ottengo i modelli
    game = g.models["game"]
    number = g.models["number"]
    #ottengo il round di riferimento
    round = Round.query.filter(game_id = game.id, number = number).one()
    #se è nullo
    if round is None:
        #lo creo
        round = Round(game_id = game.id, number = number)
        #genero il dealer
        round.dealer = get_dealer(game, number)
        #lo salvo in db
        db.session.add(round)
        db.session.commit()
    #risposta standard
    output = {"round": round, success: True}
    #se il dealer sono io
    if round.dealer_id == g.user.id:
        #se questo non è il primo round
        if round.number > 1:
            #vado a prendere le risposte del precedente round degli altri giocatori
            previousAnswers = Question.query.filter_by(user_id != g.user.id, game_id = game.id, number = round.number - 1).all()
            # le aggiungo alla risposta
            output["previous_answers"] = previous_answers
        #invio la risposta
        emit("round", output)
    elif round.category_id is None:
        #invio la risposta standard più l'info che stiamo aspettando per la scelta della category
        output["waiting"] = "category"
        emit("round", output)
    else:
        #invio la risposta standard più l'info che stiamo aspettando perchè altri giocatori giocano
        output["waiting"] = "game"
        emit("round", output)

#TODO: test
@socketio.on("get_questions")
@needs_values("SOCKET", "round_id", "game", "category")
@fetch_models({"round_id": Round, "game": Game, "category": Category})
@check_in_room("game", "game")
def get_questions(data):
    #ottengo i modelli dalla richiesta
    round = g.models["round_id"]
    game = g.models["game"]
    category = g.models["category"]
    #ottengo le domande proposte precedentemente per lo stesso turno, se ci sono
    proposed = Quiz.query.with_entities(Question).filter(Question.game_id == game.id, Question.user_id == g.user.id, Question.round_id == round.number, Question.category_id == category.id).all()
    #se non ci sono
    if len(proposed) == 0:
        #le genero random, pescando da quelle della categoria richiesta
        proposed = Quiz.query.filter(Quiz.category_id == category.id).order_by(func.random()).limit(app.config["NUMBER_OF_QUESTIONS_PER_ROUND"])
        #e le aggiungo come questions in db
        for candidate in proposed:
            q = Question(game_id = game.id, round_id = round.id, quiz_id = candidate.id, user_id = g.user.id)
            db.session.add(q)
        db.session.commit()
    #dopodichè, rispondo
    emit("get_questions", {"questions": proposed, "success": True})


#TODO: test
@socketio.on("get_categories")
@needs_values("SOCKET", "round_id", "game")
#round id, non round number!!!
@fetch_models({"round_id": Round, "game": Game})
@check_in_room("game", "game")
def get_random_categories():
    #ottengo i modelli dalla richiesta
    round = g.models["round_id"]
    game = g.models["game"]
    #controllo: solo il dealer può ottenere la lista delle categorie disponibili
    if round.dealer_id != g.user.id:
        raise NotAllowed()
    #ottengo le categorie proposte precedentemente per lo stesso turno, se ci sono
    proposed = Category.query.with_entities(Category).join(ProposedCategory).filter(ProposedCategory.round_id == round.id).all()
    #se non ci sono
    if len(proposed) == 0:
        #le genero random
        proposed = Category.query.order_by(func.random()).limit(app.config["NUMBER_OF_CATEGORIES_PROPOSED"])
        #e le aggiungo come proposed in db
        for candidate in proposed:
            c = ProposedCategory(round_id = round.id, category_id = candidate.id)
            db.session.add(c)
        db.session.commit()
    #dopodichè, rispondo
    emit("get_categories", {"categories": proposed, "success": True})


#TODO: test
@socketio.on("answer")
@needs_values("SOCKET", "answer", "game", "question")
@fetch_models({"game": Game, "question": Question})
@check_in_room("game", "game")
def answer(data):
    #ottengo i modelli
    question = g.models["question"]
    answer = g.models["answer"]
    #se sto cercando di rispondere a una question che non mi è stata posta vengo buttato fuori
    if question.user_id != g.user.id:
        raise NotAllowed()
    #se ho già risposto, non posso più farlo
    if question.answer != None:
        raise ChangeFailed()
    #modifico la risposta e la salvo in db
    question.answer = answer
    db.session.add(question)
    db.session.save()
    #ottengo il quiz di riferimento
    quiz = Quiz.query.filter(Quiz.id == question.quiz_id).one()
    #rispondo anche dicendo se ho dato la risposta giusta o sbagliata
    emit("answer", {"success": True, "correct_answer": quiz.answer == question.answer})


#TODO: test
@socketio.on("choose_category")
@needs_values("SOCKET", "category", "game", "round")
@fetch_models({"game": Game, "round": Round, "category": Category})
@check_in_room("game", "game")
def choose_category(data):
    #ottengo i modelli
    round = g.models["round"]
    category = g.models["category"]
    #se non sono il dealer, vengo buttato fuori
    if round.dealer_id != g.user_id:
        raise NotAllowed()
    #se ho già scelto la categoria, non posso più farlo
    if round.category_id != None:
        raise ChangeFailed()
    #aggiorno la categoria e salvo in db
    round.category_id = category.id
    db.session.add(round)
    db.session.commit()
    #rispondo anche con info sulla category scelta
    emit("choose_category", {"success": True, "category": category})