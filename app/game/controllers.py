# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from app import app, db
from app.game.models import *
from app.decorators import auth_required

game = Blueprint("game", __name__, url_prefix = "/game")

@game.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#creazione della partita
@game.route("/new_game")
@auth_required
# @needs_post_values("number_of_players")
@fetch_models({"opponent":"user"})
def createGame():
    new_game = Game()
    new_game.users.append(g.models["opponent"].id)
    new_game.users.append(g.user.id)
    db.session.add(new_game)
    db.session.commit()
    return jsonify(game = new_game)
