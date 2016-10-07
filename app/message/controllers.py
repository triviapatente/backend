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


@message.route("/list/<int:game_id>/", methods = ["GET"])
@auth_required
@needs_values("GET", "datetime")
def list(game_id):
    return jsonify(messages = getMessages(game_id, g.query.get("datetime")))
