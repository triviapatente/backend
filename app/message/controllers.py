# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from app import app, db
from app.message.models import *

message = Blueprint("message", __name__, url_prefix = "/message")

@message.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)
