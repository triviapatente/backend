# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from tp import app, db
from tp.message.models import *
from tp.message.utils import *
from tp.decorators import *
from datetime import datetime
from tp.decorators import create_session

message = Blueprint("message", __name__, url_prefix = "/message")

@message.route("/", methods = ["GET"])
@create_session
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

@message.route("/list/<int:game_id>", methods = ["GET"])
@create_session
@auth_required
@needs_values("GET", "timestamp")
def list(game_id):
    timestamp = g.query.get("timestamp")
    date = datetime.fromtimestamp(float(timestamp))
    print "User %s got messages from game %d from %s" % (g.user.username, game_id, date)
    return jsonify(messages = getMessages(game_id, date))
