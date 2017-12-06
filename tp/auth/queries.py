# -*- coding: utf-8 -*-

from tp.auth.models import *
from sqlalchemy import or_, func, distinct
from sqlalchemy.orm import aliased
from tp import db

# ritorna l'utente a partire dallo username o dalla email (##user_identifier)
def getUserFromIdentifier(user_identifier):
    return User.query.filter(or_(func.lower(User.email) == func.lower(user_identifier), func.lower(User.username) == func.lower(user_identifier))).first()

# ritorna il keychain dell'utente a partire dall'##id
def getKeychain(id):
    return Keychain.query.filter(Keychain.user_id == id).first()

# ritorna l'utente a partire dallo ##username o dalla ##email
def getUserFromUsernameOrEmail(username, email):
    return User.query.filter(or_(func.lower(User.username) == func.lower(username), func.lower(User.email) == func.lower(email))).first()
