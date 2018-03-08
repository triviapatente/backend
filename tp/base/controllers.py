# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, render_template
from tp import app, db
from flask import g, redirect, request
from porting import getJSONModels
from tp.exceptions import NotAllowed, BadParameters, Forbidden
from tp.decorators import auth_required, needs_values
from tp.base.models import Feedback
from sqlalchemy import exc
from tp.events.models import Installation
from premailer import transform
import jinja2

base = Blueprint("base", __name__, url_prefix = "/ws")

@base.route("/")
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)
@base.route("/generateTemplates", methods = ["GET"])
def generateTemplates():
    if app.config["DEBUG"] is False:
        raise Forbidden()
    text = transform(render_template("forgot_password/email.html", token = "{{token}}"))
    with open('tp/templates/generated/email.html', 'w') as output_file:
        output_file.write(text)
    return jsonify(success = True)

@base.route("/models", methods = ["GET"])
def obtainModels():
    debug = app.config["DEBUG"]
    if not debug:
        raise NotAllowed()
    output = getJSONModels()
    return jsonify(output)

@base.route("/store_page/ios", methods = ["GET"])
def redirectToAppStore():
    url = app.config["IOS_STORE_URL"]
    return redirect(url)
@base.route("/store_page/android", methods = ["GET"])
def redirectToPlayStore():
    url = app.config["ANDROID_STORE_URL"]
    return redirect(url)
@base.route("/terms", methods = ["GET"])
def redirectToTerms():
    path = app.config["TERMS_PATH"]
    url = request.host_url + path
    return redirect(url)

@base.route("/registerForPush", methods = ["POST"])
@needs_values("POST", "token", "deviceId", "os")
@auth_required
def registerForPush():
    token = g.post.get("token")
    device_id = g.post.get("deviceId")
    os = g.post.get("os")
    Installation.query.filter(Installation.token == token, Installation.os == os).delete()
    db.session.commit()
    installation = Installation.query.filter(Installation.device_id == device_id, Installation.os == os).first()
    if not installation:
        installation = Installation(device_id = device_id, os = os, token = token)
    installation.token = token
    installation.user_id = g.user.id
    db.session.add(installation)
    db.session.commit()
    return jsonify(success = True)

@base.route("/unregisterForPush", methods = ["POST"])
@needs_values("POST", "deviceId", "os")
def unregisterForPush():
    device_id = g.post.get("deviceId")
    os = g.post.get("os")
    Installation.query.filter(Installation.device_id == device_id, Installation.os == os).delete()
    db.session.commit()
    return jsonify(success = True)
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
