# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from tp import app, db
from tp.auth.models import User
from tp.game.models import *
from tp.utils import doTransaction
from tp.decorators import auth_required, fetch_models, needs_values
from tp.ws_decorators import check_in_room
from tp.exceptions import ChangeFailed, Forbidden, NotAllowed
from tp.game.utils import updateScore, searchInRange, createGame, getUsersFromGame, getPartecipationFromGame
from tp.base.utils import RoomType
from sqlalchemy.orm import aliased
from sqlalchemy import func

import events
game = Blueprint("game", __name__, url_prefix = "/game")

@game.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#creazione della partita
@game.route("/new", methods = ["POST"])
@auth_required
# @need_values("POST", "number_of_players")
@fetch_models(opponent = User)
def newGame():
    opponent = g.models["opponent"]
    output = doTransaction(createGame, **({"opponents": [opponent]}))
    if output:
        print "Game %d created." % output.id
        events.new_game([opponent], output)
        return jsonify(success = True, game = output, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/leave", methods = ["POST"])
@auth_required
@fetch_models(game_id = Game)
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
        events.game_left(users, game, opponent, partecipations)
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
    output = doTransaction(createGame, **({"opponents":[opponent]}))
    #gestisco l'output
    if output:
        print "Game %d created." % output.id, output
        return jsonify(success = True, game = output, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/invites", methods = ["GET"])
@auth_required
def getPendingInvites():
    invites = Invite.query.filter(Invite.receiver_id == g.user.id, Invite.accepted == None).all()
    print "User %s got pending invites." % g.user.username
    return jsonify(success = True, invites = invites)

@game.route("/invites/<int:game_id>", methods = ["POST"])
@needs_values("POST", "accepted")
@fetch_models(game_id = Game)
@auth_required
def processInvite(game_id):
    invite = Invite.query.filter(Invite.game_id == game_id, Invite.receiver_id == g.user.id, Invite.accepted == None).first()
    if not invite:
        print "User %s not allowed to process invite for game %d." % (g.user.username, game_id)
        raise NotAllowed()
    #TODO: gestire la logica che a un certo punto blocca gli inviti di gioco
    invite.accepted = g.post["accepted"]
    db.session.add(invite)
    db.session.commit()
    print "User %s processed invite for game %d:" % (g.user.username, game_id), invite
    return jsonify(success = True, invite = invite)

@game.route("/recents", methods = ["GET"])
@auth_required
def recent_games():
    a = aliased(Round, name = "a")
    questions = Question.query.with_entities(func.count(Question.round_id)).filter(Question.round_id == a.id).filter(Question.user_id == g.user.id).as_scalar()
    my_turn = db.session.query(a).with_entities(func.count(a.id)).filter(a.game_id == Game.id).filter(a.cat_id != None).filter(questions != 0).label("my_turn")
    recent_games = db.session.query(Game).join(Partecipation).filter(Partecipation.user_id == g.user.id).with_entities(Game, my_turn).order_by(my_turn.desc())
    return jsonify(success = True, recent_games = recent_games.all())
