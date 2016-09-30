# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from app import app, db
from app.auth.models import User
from app.game.models import *
from app.utils import doTransaction
from app.decorators import auth_required, fetch_models, needs_post_values
from app.exceptions import ChangeFailed, Forbidden

game = Blueprint("game", __name__, url_prefix = "/game")

@game.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#creazione della partita
@game.route("/new_game", methods = ["POST"])
@auth_required
# @needs_post_values("number_of_players")
@fetch_models({"opponent": User})
def newGame():
    #metodo transazionale
    def createGame():
        db.session.autoflush = True
        new_game = Game()
        opponent = g.models["opponent"]
        new_game.users.append(opponent)
        print opponent.id
        new_game.users.append(g.user)
        print g.user.id
        db.session.add(new_game)
        db.session.commit()
        #TODO: gestire la logica per mandare le notifiche push a chi di dovere
        invite = Invite(sender = g.user, receiver = opponent, game = new_game)
        db.session.add(invite)
        return jsonify(game = new_game)
    output = doTransaction(createGame)
    if output:
        return output
    else:
        raise ChangeFailed()



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
@game.route("/invites/<int:game_id>", methods = ["POST"])
@needs_post_values("accepted")
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
