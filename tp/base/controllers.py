# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, render_template
from tp import app, db
from flask import g, redirect, request, render_template_string, send_file
from porting import getJSONModels
from tp.exceptions import NotAllowed, BadParameters, InstagramProblem, InstagramUnnecessary, ChangeFailed
from tp.decorators import auth_required, needs_values, create_session
from tp.base.models import Feedback
from tp.auth.models import User, Keychain
from tp.base.utils import *
import datetime
from tp.utils import doTransaction
from sqlalchemy import exc
from tp.events.models import Installation
from premailer import transform
import jinja2
import StringIO
import requests

base = Blueprint("base", __name__, url_prefix = "/ws")
gdpr = Blueprint("gdpr", __name__, url_prefix = "/gdpr")
@base.route("/")
@create_session
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

@base.route("/generateTemplates", methods = ["GET"])
@create_session
def generateTemplates():
    if app.config["DEBUG"] is False:
        raise NotAllowed()
    text = transform(render_template("forgot_password/email.html", token = "{{token}}"))
    with open('tp/templates/generated/email.html', 'w') as output_file:
        output_file.write(text)
    return jsonify(success = True)

@base.route("/instagram", methods = ["GET"])
@create_session
def obtainInstagramPhotos():
    BASE_URL = app.config["INSTAGRAM_API_ENDPOINT"]
    NEEDS_INSTAGRAM = app.config["NEEDS_INSTAGRAM_SHOWGALLERY"]
    ACCESS_TOKEN = app.config["INSTAGRAM_ACCESS_TOKEN"]
    if not NEEDS_INSTAGRAM:
        raise InstagramUnnecessary()
    request = requests.get(BASE_URL + "?access_token=" + ACCESS_TOKEN)
    json = request.json()
    meta = json["meta"]
    code = meta["code"]
    if code != 200:
        raise InstagramProblem()
    data = json["data"]
    images = []
    for item in data:
        type = item["type"]
        url = item["images"]["standard_resolution"]["url"]
        link = item["link"]
        images.append({"url": url, "type": type, "link": link})
    import random
    random.shuffle(images)
    return jsonify(success = True, images = images)

@base.route("/models", methods = ["GET"])
@create_session
def obtainModels():
    debug = app.config["DEBUG"]
    if not debug:
        raise NotAllowed()
    output = getJSONModels()
    return jsonify(output)

@base.route("/store_page/ios", methods = ["GET"])
@create_session
def redirectToAppStore():
    url = app.config["IOS_STORE_URL"]
    return redirect(url)
@base.route("/store_page/android", methods = ["GET"])
@create_session
def redirectToPlayStore():
    url = app.config["ANDROID_STORE_URL"]
    return redirect(url)
@base.route("/terms", methods = ["GET"])
@create_session
def redirectToTerms():
    path = app.config["TERMS_PATH"]
    url = request.host_url + path
    return redirect(url)
@base.route("/registerForPush", methods = ["POST"])
@create_session
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
@create_session
@needs_values("POST", "deviceId", "os")
def unregisterForPush():
    device_id = g.post.get("deviceId")
    os = g.post.get("os")
    Installation.query.filter(Installation.device_id == device_id, Installation.os == os).delete()
    db.session.commit()
    return jsonify(success = True)
@base.route("/privacyPolicy", methods = ["GET"])
@create_session
def redirectToPrivacyPolicy():
    url = app.config["PRIVACY_POLICY_URL"]
    return redirect(url)

#API usata per intercettare le richieste di contatto degli utenti
@base.route("/contact", methods = ["POST"])
@create_session
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

@app.template_filter('simpleDate')
def simpleDateFilter(value):
    return value.strftime("%b %d %Y %H:%M:%S")

@base.route("/redirect/drop-user")
def redirectToDropUser():
    url = app.config["DROP_ACCOUNT_URL"]
    return redirect(url)

@base.route("/redirect/get-data")
def redirectToGetData():
    url = app.config["GET_DATA_URL"]
    return redirect(url)

@base.route("/redirect/revoke-permissions")
def redirectToRevoke():
    url = app.config["REVOKE_PERMISSIONS_URL"]
    return redirect(url)

@gdpr.route("/drop-user", methods = ["POST"])
@create_session
@auth_required
def deleteUser():
    output = doTransaction(dropUser, id=g.user.id)
    if output == True:
        return jsonify(success = True)
    else:
        raise ChangeFailed()

@gdpr.route("/get-data", methods = ["POST"])
@create_session
@auth_required
def getData():
    template = app.config["GDPR_DATA_TEMPLATE"]
    installations = Installation.query.filter(Installation.user_id == g.user.id).all()
    output = render_template_string(template, user=g.user, installations=installations, installations_count=len(installations))
    strIO = StringIO.StringIO()
    strIO.write(output)
    strIO.seek(0)
    return send_file(strIO,
                    attachment_filename="your_data.txt",
                    as_attachment=True)
