from flask import request, jsonify, Blueprint
from app import app, db

base = Blueprint("base", __name__, url_prefix = "/base")

@app.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)
