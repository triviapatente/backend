# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from tp import app, db
from flask import g, redirect
from porting import getJSONModels
from tp.exceptions import NotAllowed, BadParameters
from tp.decorators import auth_required, needs_values
from tp.base.models import Feedback
from sqlalchemy import exc

base = Blueprint("base", __name__, url_prefix = "/ws")

@base.route("/")
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

@base.route("/terms", methods = ["GET"])
def redirectToTerms():
    url = app.config["TERMS_URL"]
    return redirect(url)

@base.route("/privacyPolicy", methods = ["GET"])
def redirectToPrivacyPolicy():
    url = app.config["PRIVACY_POLICY_URL"]
    return redirect(url)

#API usata per intercettare le richieste di contatto degli utenti
@base.route("/contact", methods = ["POST"])
@needs_values("POST", "message", "scope")
@auth_required
def contactUs():
    #ottengo l'input
    message = g.post.get("message")
    scope = g.post.get("scope")
    #inserimento in db
    feedback = Feedback(user = g.user, message = message, scope = scope)
    db.session.add(feedback)
    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        raise BadParameters(["scope"])

    return jsonify(success = True)
