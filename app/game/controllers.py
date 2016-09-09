# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from app import app, db
from app.game.models import *

game = Blueprint("game", __name__, url_prefix = "/game")

@game.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)
