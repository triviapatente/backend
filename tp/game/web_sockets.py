# -*- coding: utf-8 -*-
from flask import g, request
from tp import socketio, app, db
from tp.ws_decorators import ws_auth_required, filter_input_room, check_in_room
from tp.base.utils import roomName
from tp.game.utils import get_dealer, getUsersFromGame
from tp.auth.models import User
from tp.game.models import Game, Question, Round, Category, Quiz
from tp.decorators import needs_values, fetch_models
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g
from tp.base.utils import RoomType
from tp.exceptions import NotAllowed, ChangeFailed
#TODO: test
@socketio.on("init_round")
@ws_auth_required
@needs_values("SOCKET", "number", "game")
@fetch_models(game = Game)
@check_in_room(RoomType.game, "game")
def init_round(data):
    #ottengo i modelli
    game = g.models["game"]
    number = g.params["number"]
    if number > 2:
        #ottengo gli utenti del match
        users = getUsersFromGame(game, User.id)
        #controllo se ci sono risposte non date dagli utenti nel round precedente a quello in cui ho appena giocato
        answered_count = Round.query.filter(Round.number == number - 2).filter(Round.game_id == game.id).join(Question).filter(Question.answer != None).filter(Question.user_id.in_(users)).count()
        if answered_count != len(users) * app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]:
            raise NotAllowed()
    if number > 1:
        #controllo se ci sono risposte non date da me nel round in cui ho appena giocato
        my_answered_count = Round.query.filter(Round.number == number - 1).filter(Round.game_id == game.id).join(Question).filter(Question.answer != None).filter(Question.user_id == g.user.id).count()
        if my_answered_count != app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]:
            raise NotAllowed()
    #ottengo il round di riferimento
    round = Round.query.filter(Round.game_id == game.id, Round.number == number).first()
    #se è nullo
    if round is None:
        #lo creo
        round = Round(game = game, number = number)
        #genero il dealer
        round.dealer_id = get_dealer(game, number)
        if round.dealer_id is None:
            raise NotAllowed()
        #lo salvo in db
        db.session.add(round)
        db.session.commit()

    #risposta standard
    output = {"round": round.json, "success": True}
    #se questo non è il primo round
    if round.number > 1:
        #vado a prendere le risposte del precedente round degli altri giocatori
        previousAnswers = Question.query.filter(Question.user_id != g.user.id).join(Round).filter(Round.number == number - 1).filter(Round.game_id == game.id).all()
        # le aggiungo alla risposta
        output["previous_answers"] = previousAnswers
    #se il dealer sono io
    if round.dealer_id == g.user.id:
        #invio la risposta
        emit("init_round", output)
    elif round.cat_id is None:
        #invio la risposta standard più l'info che stiamo aspettando per la scelta della category
        output["waiting"] = "category"
        emit("init_round", output)
    else:
        #invio la risposta standard più l'info che stiamo aspettando perchè altri giocatori giocano
        output["waiting"] = "game"
        emit("init_round", output)

#TODO: test
@socketio.on("get_questions")
@ws_auth_required
@needs_values("SOCKET", "round_id", "game", "category")
@fetch_models(round_id = Round, game = Game, category = Category)
@check_in_room(RoomType.game, "game")
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
@ws_auth_required
@needs_values("SOCKET", "round_id", "game")
#round id, non round number!!!
@fetch_models(round_id = Round, game = Game)
@check_in_room(RoomType.game, "game")
def get_random_categories(data):
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
@ws_auth_required
@needs_values("SOCKET", "answer", "game", "question")
@fetch_models(game = Game, question = Question)
@check_in_room(RoomType.game, "game")
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
@ws_auth_required
@needs_values("SOCKET", "category", "game", "round")
@fetch_models(game = Game, round = Round, category = Category)
@check_in_room(RoomType.game, "game")
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
