# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from app import app, db
from app.auth.models import *

auth = Blueprint("auth", __name__, url_prefix = "/auth")

@auth.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)
