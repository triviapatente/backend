from flask import request, jsonify
from app import app
from blueprints import base

@base.route("/welcome", methods = ["GET"])
def welcome():
    output = {
        "name": __name__,
        "version": SERVER_VERSION
    }
    return jsonify(output)
