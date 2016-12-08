# -*- coding: utf-8 -*-
from flask import g, request, json
from tp import socketio, app, db
from tp.ws_decorators import ws_auth_required, filter_input_room, check_in_room
from tp.base.utils import roomName
from tp.game.utils import get_closed_round_details, get_dealer, getNextRoundNumber, getUsersFromGame, updateScore, gameEnded, getPartecipationFromGame, setWinner, numberOfAnswersFor, isOpponentOnline
from tp.auth.models import User
from tp.game.models import Game, Question, Round, Category, Quiz, ProposedCategory, ProposedQuestion
from tp.decorators import needs_values, fetch_models
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g
from tp.base.utils import RoomType
from tp.exceptions import NotAllowed, ChangeFailed
from sqlalchemy import func, and_
import events

@socketio.on("init_round")
@ws_auth_required
@needs_values("SOCKET", "game")
@fetch_models(game = Game)
@check_in_room(RoomType.game, "game")
def init_round(data):
    #parametri in input
    game = g.models["game"]
    #costanti
    NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    NUMBER_OF_ROUNDS = app.config["NUMBER_OF_ROUNDS"]
    #round di riferimento in base all'attività precedente dell'utente
    next_number = getNextRoundNumber(game)
    #round precedente a quello di riferimento
    prev_round = Round.query.filter(Round.number == next_number - 1).filter(Round.game_id == game.id).first()
    #controllo che la partita non sia finita
    if game.ended or gameEnded(game):
        #se è finita
        #evito di fare l'update più volte
        if not game.ended:
            game.ended = True
            game.winner = setWinner(game)
            db.session.add(game)
            db.session.commit()
            print "Game %d ended. Updating scores.." % game.id
            updatedUsers = updateScore(game)
            print "User's score updated."
        #preparo l'output
        partecipations = [p.json for p in getPartecipationFromGame(game)]
        winner = None
        if game.winner:
            winner = game.winner.id
        return emit("init_round", {"success": True, "partecipations": partecipations, "ended": True, "winner": winner})
    #controllo il caso in cui si è al round 10, con domande completate, e quindi si fa riferimento all'11, ma la partita non è finita:
    #vuol dire che gli altri utenti devono ancora giocare
    if next_number > NUMBER_OF_ROUNDS:
        return emit("init_round", {"success": True, "waiting": "game"})
    #caso in cui ho completato il secondo round (di cui son sicuramente dealer), ma l'avversario è ancora fermo all'1
    if next_number > 3:
        #ottengo gli utenti del match
        users = getUsersFromGame(game, User.id)
        #controllo se ci sono risposte non date dagli utenti nel round precedente a quello in cui ho appena giocato
        answered_count = Round.query.filter(Round.number == next_number - 3).filter(Round.game_id == game.id).join(Question).count()
        if answered_count != len(users) * NUMBER_OF_QUESTIONS_PER_ROUND:
            return emit("init_round", {"success": True, "waiting": "game"})
    #ottengo il round di riferimento
    round = Round.query.filter(Round.game_id == game.id, Round.number == next_number).first()
    need_new_round = round is None
    #se è nullo
    if need_new_round:
        #lo creo
        round = Round(game = game, number = next_number)
        #genero il dealer
        round.dealer_id = get_dealer(game, next_number)
        #se il dealer non esiste, vuol dire che non ci sono utenti che partecipano al gioco
        if round.dealer_id is None:
            raise NotAllowed()
        #lo salvo in db
        db.session.add(round)
        db.session.commit()
    #risposta standard
    output = {"round": round.json, "success": True, "opponent_online": isOpponentOnline(game)}
    #ottengo il dealer per usarlo successivamente
    dealer = User.query.filter(User.id == round.dealer_id).first()
    #Il dealer del turno a cui mi riferisco deve ancora giocare il precedente turno
    if prev_round and numberOfAnswersFor(round.dealer_id, prev_round.id) < NUMBER_OF_QUESTIONS_PER_ROUND:
        #invio la risposta standard più l'info che stiamo aspettando perchè altri giocatori giocano al round precedente
        output["waiting"] = "game"
        output["waiting_for"] = dealer
    #Il dealer del turno a cui mi riferisco non ha scelto la category
    elif round.cat_id is None:
        #invio la risposta standard più l'info che stiamo aspettando per la scelta della category
        output["waiting"] = "category"
        output["waiting_for"] = dealer
    #Non ho ancora giocato tutte le partite del turno a cui mi riferisco
    elif numberOfAnswersFor(g.user.id, round.id) < NUMBER_OF_QUESTIONS_PER_ROUND:
        #invio la risposta standard più l'info che devo ancora finire il round
        output["waiting"] = "game"
        output["waiting_for"] = g.user
    print "User %s in init round got output:" % g.user.username, output
    #TODO informazione ridondante, rimuoverla quando avremo il db lato client (in tal caso basterà l'id della categoria, che è messo nel round)
    output["category"] = Category.query.filter(Category.id == round.cat_id).first()
    emit("init_round", output)
    #se è stato creato un nuovo round, mando l'evento
    if need_new_round:
        events.round_started(g.roomName, round)


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
        ids = Round.query.filter(Round.game_id == game.id).join(Category).with_entities(Category.id).all()
        #le genero random
        proposed = Category.query.filter(~Category.id.in_(ids)).order_by(func.random()).limit(app.config["NUMBER_OF_CATEGORIES_PROPOSED"]).all()
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
    proposed = Quiz.query.join(ProposedQuestion).outerjoin(Question, and_(Question.quiz_id == Quiz.id, Question.user_id == g.user.id, Question.round_id == round.id)).with_entities(Quiz, Question.answer).filter(ProposedQuestion.round_id == round.id).all()
    output = []
    for item in proposed:
        quiz = item[0]
        quiz.my_answer = item[1]
        quiz.answered_correctly = (quiz.my_answer == quiz.answer)
        del quiz.answer
        output.append(quiz)

    proposed = sorted([p.json for p in output], key = lambda q: q.get("id"))
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
    proposedQuestion = ProposedQuestion.query.filter(ProposedQuestion.round_id == round.id).filter(ProposedQuestion.quiz_id == quiz.id).first()
    if not proposedQuestion:
        raise NotAllowed()
    #se ho già risposto, non posso più farlo
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

    NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    number_of_answers = Question.query.filter(Question.round_id == round.id).filter(Question.user_id == g.user.id).count()
    if number_of_answers == NUMBER_OF_QUESTIONS_PER_ROUND:
        events.round_ended(g.roomName, round)

@socketio.on("round_details")
@ws_auth_required
@needs_values("SOCKET", "game")
@fetch_models(game = Game)
@check_in_room(RoomType.game, "game")
def round_details(data):
    game = g.models["game"]
    (quizzes, answers, categories, users, partecipations) = get_closed_round_details(game)
    output = {"answers": answers, "quizzes": quizzes, "categories": categories, "users": users}
    if game.ended:
        output["partecipations"] = partecipations
    return emit("round_details", output)
