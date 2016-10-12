# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from tp import app, db
from porting import getJSONModels
from tp.exceptions import NotAllowed
base = Blueprint("base", __name__, url_prefix = "/ws")

@base.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

@base.route("/models", methods = ["GET"])
def obtainModels():
    debug = app.config["DEBUG"]
    if not debug:
        raise NotAllowed()
    output = getJSONModels()
    return jsonify(output)
