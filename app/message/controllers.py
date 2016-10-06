# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from app import app, db
from app.message.models import *
from app.message.utils import *
from app.decorators import *

message = Blueprint("message", __name__, url_prefix = "/message")

@message.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)


@message.route("/scroll", methods = ["GET"])
@auth_required
@needs_values("GET", "game_id", "datetime")
def scroll():
    return jsonify(messages = getMessages(g.get.get("game_id"), g.get.get("datetime")))
