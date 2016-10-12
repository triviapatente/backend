# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from tp import app, db
from tp.auth.models import User
from tp.game.models import *
from tp.utils import doTransaction
from tp.decorators import auth_required, fetch_models, needs_values
from tp.exceptions import ChangeFailed, Forbidden
from tp.game.utils import updateScore, searchInRange

game = Blueprint("game", __name__, url_prefix = "/game")

@game.route("/test", methods = ["POST"])
@needs_values("POST", "game_id", "scoreRange")
def test():
    game = Game.query.filter_by(id = g.post.get("game_id")).first()
    return jsonify(updatedScores = updateScore(game, int(g.post.get("scoreRange"))))

@game.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#creazione della partita
@game.route("/new_game", methods = ["POST"])
@auth_required
# @need_values("POST", "number_of_players")
@fetch_models({"opponent": User})
def newGame():
    output = doTransaction(createGame, **({"opponent":g.models["opponent"]}))
    if output:
        return jsonify(game = output)
    else:
        raise ChangeFailed()

# ricerca aleatoria di un avversario
@game.route("/new_game/random", methods = ["POST"])
@auth_required
def randomSearch():
    # definisco il numero di cicli massimo di ricerca
    users_scores = User.query.order_by(User.score.desc()).all()
    maxRangeToCover = max(users_scores[0].score - g.user.score, g.user.score - users_scores[-1].score)
    rangeIncrement = app.config["RANGE_INCREMENT"]
    prevRange = 0
    opponent = None
    for scoreRange in range(app.config["INITIAL_RANGE"], maxRangeToCover + rangeIncrement, rangeIncrement):
        user = searchInRange(prevRange, scoreRange, g.user)
        if user:
            opponent = user
            break
        prevRange = scoreRange

    output = doTransaction(createGame, **({"opponent":opponent}))
    if output:
        return jsonify(game = output)
    else:
        raise ChangeFailed()

#metodo transazionale per la creazione di una partita
def createGame(**params):
    new_game = Game(creator = g.user)
    opponent = params["opponent"]
    new_game.users.append(opponent)
    new_game.users.append(g.user)
    db.session.add(new_game)
    #TODO: gestire la logica per mandare le notifiche push a chi di dovere
    invite = Invite(sender = g.user, receiver = opponent, game = new_game)
    db.session.add(invite)
    return new_game

@game.route("/invites", methods = ["GET"])
@auth_required
def getPendingInvites():
    invites = Invite.query.filter(Invite.receiver_id == g.user.id, Invite.accepted == None).all()
    return jsonify(invites = invites)

#considerare di dare questa info alla creazione del websocket
@game.route("/invites/badge", methods = ["GET"])
@auth_required
def getPendingInvitesBadge():
    badge = Invite.query.filter(Invite.receiver_id == g.user.id, Invite.accepted == None).count()
    return jsonify(badge = badge)

#considerare di dare questa info alla creazione del websocket
#TODO: controllare che l'invito non sia già stato accettato
@game.route("/invites/<int:game_id>", methods = ["POST"])
@needs_values("POST", "accepted")
@auth_required
def processInvite(game_id):
    invite = Invite.query.filter(Invite.game_id == game_id, Invite.receiver_id == g.user.id).first()
    if not invite:
        raise ChangeFailed()
    #TODO: gestire la logica che a un certo punto blocca gli inviti di gioco
    invite.accepted = g.post["accepted"]
    db.session.add(invite)
    db.session.commit()
    return jsonify(success = True)
