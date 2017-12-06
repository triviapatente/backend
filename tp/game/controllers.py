# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g, send_file
from tp import app, db
from tp.auth.models import User
from tp.game.models import *
from tp.utils import doTransaction
from sqlalchemy.orm import aliased
from tp.decorators import auth_required, fetch_models, needs_values, check_game_not_ended
from tp.ws_decorators import check_in_room
from tp.exceptions import ChangeFailed, NotAllowed
from sqlalchemy import or_, func
from tp.rank.queries import getLastGameResultJoin
from tp.game.utils import sanitizeSuggestedUsers, getSuggestedUsers, updateScore, searchInRange, createGame, getUsersFromGame, getPartecipationFromGame, getRecentGames, getScoreDecrementForLosing
from tp.base.utils import RoomType
import events
from events import RecentGameEvents

game = Blueprint("game", __name__, url_prefix = "/game")
quiz = Blueprint("quiz", __name__, url_prefix = "/quiz")
category = Blueprint("category", __name__, url_prefix = "/category")

@game.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#creazione della partita
@game.route("/new", methods = ["POST"])
@auth_required
# @needs_values("POST", "number_of_players")
@fetch_models(opponent = User)
def newGame():
    opponent = g.models["opponent"]
    game = doTransaction(createGame, **({"opponents": [opponent]}))
    if game:
        print "Game %d created." % game.id
        events.new_game(game)
        RecentGameEvents.created(game)
        return jsonify(success = True, game = game, user = opponent)
    else:
        raise ChangeFailed()
@game.route("/leave/decrement", methods = ["GET"])
@auth_required
@needs_values("GET", "game_id")
@fetch_models(game_id = Game)
@check_game_not_ended("game_id")
def get_leave_score_decrement():
    game = g.models["game_id"]
    user_ids = [u.id for u in getUsersFromGame(game)]
    #se non appartengo al gioco
    if g.user.id not in user_ids:
        raise NotAllowed()
    decrement = 0
    if game.started:
        decrement = getScoreDecrementForLosing(game)
    return jsonify(success = True, decrement = decrement)

@game.route("/leave", methods = ["POST"])
@auth_required
@fetch_models(game_id = Game)
@check_game_not_ended("game_id")
def leave_game():
    game = g.models["game_id"]
    users = getUsersFromGame(game)
    user_ids = [u.id for u in users]
    #se non appartengo al gioco
    if g.user.id not in user_ids:
        raise NotAllowed()
    #se ci sono più di due giocatori
    if len(users) > 2:
        #TODO: gestire la multiutenza nel gioco (versione 2.0)
        #il game non finisce, e si flagga la partecipation dell'utente, in modo che si capisce che non gioca più
        return jsonify(success = False, reason = "Version 2.0")
    #se il numero di giocatori è corretto
    elif len(users) == 2:
        opponent = [u for u in users if u.id != g.user.id][0]
        #modifico il game settandogli tra l'altro lo winner
        game.ended = True
        game.winner_id = opponent.id
        db.session.add(game)
        db.session.commit()
        #modifico i punteggi degli utenti
        updateScore(game)
        #ritorno le varie risposte
        partecipations = [p.json for p in getPartecipationFromGame(game)]
        events.game_left(users, game, partecipations)
        RecentGameEvents.ended(game = game)
        return jsonify(success = True, ended = True, game = game, winner = opponent, partecipations = partecipations)
    #nessun avversario.. solo io nel gioco
    #NOTE: non dovrebbe succedere mai, in new_game l'opponent è obbligatorio
    return jsonify(success = False, message = "Nessun avversario in questo match!")

# ricerca aleatoria di un avversario
@game.route("/new/random", methods = ["POST"])
@auth_required
def randomSearch():
    # definisco il numero di cicli massimo di ricerca
    firstUser = User.query.order_by(User.score.desc()).first()
    lastUser = User.query.order_by(User.score).first()
    # massimo range in cui andare a cercare
    maxRangeToCover = max(firstUser.score - g.user.score, g.user.score - firstUser.score)
    #incremento del range, range di partenza
    rangeIncrement, initialRange = app.config["RANGE_INCREMENT"], app.config["INITIAL_RANGE"]
    #utente candidato
    opponent = None
    #il +1 serve nel caso in cui esistono tutti utenti con lo stesso punteggio (maxRangeToCover sarebbe 0)
    scoreRange, prevRange = range(initialRange, maxRangeToCover + initialRange + 1, rangeIncrement), 0
    #per ogni punteggio nello score
    for entry in scoreRange:
        #ottengo l'utente candidato nel sottorange
        user = searchInRange(prevRange, entry, g.user)
        #se lo trovo, lo prendo
        if user:
            opponent = user
            break
        prevRange = entry
    #controllo se non ho trovato nessun utente
    if opponent is None:
        print "No opponent found."
        return jsonify(success = False)
    #eseguo la transazione con l'utente trovato
    game = doTransaction(createGame, opponents = [opponent])
    #gestisco l'output
    if game:
        print "Game %d created." % game.id
        events.new_game(game)
        RecentGameEvents.created(game)
        return jsonify(success = True, game = game, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/recents", methods = ["GET"])
@auth_required
def recent_games():
    #timestamp = g.query.get("timestamp")
    #if timestamp:
    #    date = datetime.fromtimestamp(float(timestamp))
    recent_games = getRecentGames(g.user)
    return jsonify(success = True, recent_games = recent_games)

@quiz.route("/image/<int:id>", methods = ["GET"])
def getQuizImage(id):
    image = Image.query.filter(Image.id == id).first()
    if image:
        return send_file(image.imagePath)
    raise NotAllowed()

@category.route("/image/<int:id>", methods = ["GET"])
def getCategoryImage(id):
    category = Category.query.filter(Category.id == id).first()
    if category:
        return send_file(category.imagePath)
    raise NotAllowed()

@game.route("/users/suggested", methods = ["GET"])
@auth_required
def get_suggested_users():
    users = getSuggestedUsers(g.user)
    return jsonify(success = True, users = users)


@game.route("/users/search", methods = ["GET"])
@needs_values("GET", "query")
@auth_required
def search_user():
    query = "%" + g.query.get("query") + "%"
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    criteria = or_(User.username.ilike(query), func.concat(User.name, " ", User.surname).ilike(query))
    matches = User.query.with_entities(User, getLastGameResultJoin(User)).filter(User.id != g.user.id).filter(criteria).limit(limit).all()
    output = sanitizeSuggestedUsers(matches)
    return jsonify(success = True, users = output)
