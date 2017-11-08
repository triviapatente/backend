# -*- coding: utf-8 -*-
from flask import Blueprint, g, jsonify, request
from tp.decorators import auth_required, needs_values
from tp.exceptions import BadParameters
from tp.rank.queries import *
import re

rank = Blueprint("rank", __name__, url_prefix = "/rank")

#api per la richiesta della classifica italiana (globale)
@rank.route("/global", methods = ["GET"])
@auth_required
def getItalianRank():
    #inizializzazione vars
    thresold = None
    direction = None
    #ottengo i parametri, se ci sono
    thresold = request.args.get("thresold")
    direction = request.args.get("direction")
    #se non ci sono informazioni paginazione, ritorno la classifica localizzata attorno alla posizione dell'utente
    if not thresold and not direction:
        rank = getRank()
    #se invece ci sono info di paginazione, ma solo la direction, fallisco
    elif thresold is None:
        raise BadParameters(["thresold"])
    #se invece ci sono info di paginazione, ma solo il thresold oppure la direction è sbagliata, fallisco
    elif direction is None or re.match(r'up|down', direction) is None:
        raise BadParameters(["direction"])
    #se ci sono corrette info di paginazione, avvio una query paginata
    else:
        rank = getPaginatedRank(thresold, direction)
    print "User %s got global rank." % g.user.username
    return jsonify(rank = rank)

@rank.route("/friends", methods = ["GET"])
@auth_required
def getFriendsRank():
    pass

@rank.route("/search", methods = ["GET"])
@auth_required
@needs_values("GET", "query")
def searchInRank():
    query = g.query["query"]
    matches = search("%" + query + "%")
    return jsonify(matches = matches)
