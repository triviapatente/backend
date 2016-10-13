# -*- coding: utf-8 -*-

from tp.auth.models import *
from sqlalchemy import or_, func, distinct
from sqlalchemy.orm import aliased
from tp import db

# ritorna l'utente a partire dallo username o dalla email (##user_identifier)
def getUserFromIdentifier(user_identifier):
    return User.query.filter(or_(User.email == user_identifier, User.username == user_identifier)).first()

# ritorna il keychain dell'utente a partire dall'##id
def getKeychain(id):
    return Keychain.query.filter(Keychain.user_id == id).first()

# ritorna l'utente a partire dallo ##username o dalla ##email
def getUserFromUsernameOrEmail(username, email):
    return User.query.filter(or_(User.username == username, User.email == email)).first()

# ritorna la classifica
def getRank():
    return User.query.order_by(User.score).limit(app.config["RESULTS_LIMIT_RANK_ITALY"])

def getUserPosition(user):
    return db.session.query(func.count(distinct(User.score))).filter(User.score > user.score).scalar() + 1
