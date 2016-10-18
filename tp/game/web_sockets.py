# -*- coding: utf-8 -*-
from flask import g, request, json
from tp import socketio, app, db
from tp.ws_decorators import ws_auth_required, filter_input_room, check_in_room
from tp.base.utils import roomName
from tp.game.utils import get_dealer, getUsersFromGame, updateScore, gameEnded, getPartecipationFromGame
from tp.auth.models import User
from tp.game.models import Game, Question, Round, Category, Quiz, ProposedCategory, ProposedQuestion
from tp.decorators import needs_values, fetch_models
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g
from tp.base.utils import RoomType
from tp.exceptions import NotAllowed, ChangeFailed
from sqlalchemy import func
import events
@socketio.on("init_round")
@ws_auth_required
@needs_values("SOCKET", "number", "game")
@fetch_models(game = Game)
@check_in_room(RoomType.game, "game")
def init_round(data):
    #ottengo i modelli
    game = g.models["game"]
    number = g.params["number"]
    #controllo che la partita non sia finita
    if number > app.config["NUMBER_OF_ROUNDS"] and gameEnded(game):
        #se è finita
        #evito di fare l'update più volte
        if not game.ended:
            game.ended = True
            db.session.add(game)
            db.session.commit()
            print "Game %d ended. Updating scores.." % game.id
            updatedUsers = updateScore(game)
            print "User's score updated.", updatedUsers
        partecipations = [p.json for p in getPartecipationFromGame(game)]
        return emit("init_round", {"partecipations": partecipations, "ended": True})
    NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    if number > 2:
        #ottengo gli utenti del match
        users = getUsersFromGame(game, User.id)
        #controllo se ci sono risposte non date dagli utenti nel round precedente a quello in cui ho appena giocato
        answered_count = Round.query.filter(Round.number == number - 2).filter(Round.game_id == game.id).join(Question).filter(Question.user_id.in_(users)).count()
        if answered_count != len(users) * NUMBER_OF_QUESTIONS_PER_ROUND:
            raise NotAllowed()
    if number > 1:
        #controllo se ci sono risposte non date da me nel round in cui ho appena giocato
        my_answered_count = Round.query.filter(Round.number == number - 1).filter(Round.game_id == game.id).join(Question).filter(Question.user_id == g.user.id).count()
        if my_answered_count != NUMBER_OF_QUESTIONS_PER_ROUND:
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
    #se il dealer non sono io
    if round.dealer_id != g.user.id:
        if Question.query.filter(Question.user_id == round.dealer_id).join(Round).filter(Round.number == number - 1).count() < NUMBER_OF_QUESTIONS_PER_ROUND:
            #invio la risposta standard più l'info che stiamo aspettando perchè altri giocatori giocano
            output["waiting"] = "game"
        elif round.cat_id is None:
            #invio la risposta standard più l'info che stiamo aspettando per la scelta della category
            output["waiting"] = "category"
    print "User %s in init round got output:" % g.user.username, output
    emit("init_round", output)

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
        proposed = Category.query.order_by(func.random()).limit(app.config["NUMBER_OF_CATEGORIES_PROPOSED"]).all()
        #e le aggiungo come proposed in db
        for candidate in proposed:
            c = ProposedCategory(round_id = round.id, category_id = candidate.id)
            db.session.add(c)
        db.session.commit()
    #dopodichè, rispondo
    proposed = sorted([p.json for p in proposed], key = lambda cat: cat.get("id"))
    print "User %s got proposed categories." % g.user.username, proposed
    emit("get_categories", {"categories": proposed, "success": True})

@socketio.on("choose_category")
@ws_auth_required
@needs_values("SOCKET", "category", "game", "round_id")
@fetch_models(game = Game, round_id = Round, category = Category)
@check_in_room(RoomType.game, "game")
def choose_category(data):
    #ottengo i modelli
    round = g.models["round_id"]
    category = g.models["category"]
    game = g.models["game"]

    proposed = ProposedCategory.query.filter(ProposedCategory.round_id == round.id).filter(ProposedCategory.category_id == category.id).first()
    if not proposed:
        raise NotAllowed()
    #se non sono il dealer, vengo buttato fuori
    if round.dealer_id != g.user.id:
        raise NotAllowed()
    #se ho già scelto la categoria, non posso più farlo
    if round.cat_id != None:
        raise NotAllowed()
    #aggiorno la categoria e salvo in db
    round.cat_id = category.id
    db.session.add(round)
    # genero le domande random, pescando da quelle della categoria richiesta
    proposed = Quiz.query.filter(Quiz.category_id == category.id).order_by(func.random()).limit(app.config["NUMBER_OF_QUESTIONS_PER_ROUND"])
    #e le aggiungo come questions in db
    for candidate in proposed:
        q = ProposedQuestion(round_id = round.id, quiz_id = candidate.id)
        db.session.add(q)
    db.session.commit()
    db.session.commit()
    #rispondo anche con info sulla category scelta
    print "User %s has choosen category." % g.user.username, category
    emit("choose_category", {"success": True, "category": category})
    events.category_chosen(g.roomName, category)

@socketio.on("get_questions")
@ws_auth_required
@needs_values("SOCKET", "round_id", "game")
@fetch_models(round_id = Round, game = Game)
@check_in_room(RoomType.game, "game")
def get_questions(data):
    #ottengo i modelli dalla richiesta
    round = g.models["round_id"]
    if not round.cat_id:
        raise NotAllowed()
    #ottengo le domande proposte precedentemente per lo stesso turno, se ci sono
    proposed = Quiz.query.join(ProposedQuestion).filter(ProposedQuestion.round_id == round.id).all()
    proposed = sorted([p.json for p in proposed], key = lambda q: q.get("id"))
    #dopodichè, rispondo
    print "User %s got questions." % g.user.username, proposed
    emit("get_questions", {"questions": proposed, "success": True})

@socketio.on("answer")
@ws_auth_required
@needs_values("SOCKET", "answer", "game", "round_id", "quiz_id")
@fetch_models(game = Game, round_id = Round, quiz_id = Quiz)
@check_in_room(RoomType.game, "game")
def answer(data):
    #ottengo i modelli
    answer = g.params["answer"]
    round = g.models["round_id"]
    quiz = g.models["quiz_id"]
    question = Question.query.filter(Question.round_id == round.id, Question.user_id == g.user.id, Question.quiz_id == quiz.id).first()
    #se ho già risposto, non posso più farlo
    proposedQuestion = ProposedQuestion.query.filter(ProposedQuestion.round_id == round.id).filter(ProposedQuestion.quiz_id == quiz.id).first()
    if not proposedQuestion:
        raise NotAllowed()
    if question:
        raise NotAllowed()
    question = Question(round_id = round.id, user_id = g.user.id, quiz_id = quiz.id, answer = answer)
    db.session.add(question)
    db.session.commit()
    #rispondo anche dicendo se ho dato la risposta giusta o sbagliata
    print "User %s answered to proposed question." % g.user.username, question, answer
    correct = (quiz.answer == question.answer)
    emit("answer", {"success": True, "correct_answer": correct})
    events.question_answered(g.roomName, quiz, correct)
