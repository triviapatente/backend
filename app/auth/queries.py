# -*- coding: utf-8 -*-

from app.auth.models import *
from sqlalchemy import or_, func, distinct
from sqlalchemy.orm import aliased
from app import db

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
    a = aliased(User, name="a")
    b = aliased(User, name="user")
    ## funziona per magia, non toccare assolutamente, qualunque modifica, anche sensata, potrebbe rovinare tutto ##
    #getPosition è la subquery, da chiamare per ogni record di b per il valore del campo position.
    #conta il numero di distinti valori di punteggio superiori a quelli del record corrente a
    getPosition = db.session.query(func.count(distinct(a.score))).filter(a.score > b.score).subquery()
    #ritorna tutti i campi della tabella user, e aggiunge la colonna position prendendo i valori dalla subquery getPosition
    #ordina i record in modo discendente in base alla
    return db.session.query(b, getPosition.as_scalar().label("position")).order_by("position").limit(app.config["RESULTS_LIMIT_RANK_ITALY"]).all()
