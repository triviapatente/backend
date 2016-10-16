# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from tp import app, db
from tp.auth.models import User
from tp.game.models import *
from tp.utils import doTransaction
from tp.decorators import auth_required, fetch_models, needs_values
from tp.exceptions import ChangeFailed, Forbidden, NotAllowed
from tp.game.utils import updateScore, searchInRange, createGame

game = Blueprint("game", __name__, url_prefix = "/game")

@game.route("/test", methods = ["POST"])
@needs_values("POST", "game_id", "scoreRange")
def test():
    game = Game.query.filter_by(id = g.post.get("game_id")).first()
    return jsonify(updatedScores = updateScore(game, int(g.post.get("scoreRange"))))

@game.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#creazione della partita
@game.route("/new", methods = ["POST"])
@auth_required
# @need_values("POST", "number_of_players")
@fetch_models(opponent = User)
def newGame():
    opponent = g.models["opponent"]
    output = doTransaction(createGame, **({"opponents": [opponent]}))
    if output:
        print "Game %d created." % output.id
        return jsonify(success = True, game = output, user = opponent)
    else:
        raise ChangeFailed()

# ricerca aleatoria di un avversario
@game.route("/new/random", methods = ["POST"])
@auth_required
def randomSearch():
    # definisco il numero di cicli massimo di ricerca
    firstUser = User.query.order_by(User.score.desc()).first()
    lastUser = User.query.order_by(User.score).first()
    # massimo range in cui andare a cercare
    maxRangeToCover = max(firstUser.score - g.user.score, g.user.score - firstUser.score)
    #incremento del range, range di partenza
    rangeIncrement, initialRange = app.config["RANGE_INCREMENT"], app.config["INITIAL_RANGE"]
    #utente candidato
    opponent = None
    #il +1 serve nel caso in cui esistono tutti utenti con lo stesso punteggio (maxRangeToCover sarebbe 0)
    scoreRange, prevRange = range(initialRange, maxRangeToCover + initialRange + 1, rangeIncrement), 0
    #per ogni punteggio nello score
    for entry in scoreRange:
        #ottengo l'utente candidato nel sottorange
        user = searchInRange(prevRange, entry, g.user)
        #se lo trovo, lo prendo
        if user:
            opponent = user
            break
        prevRange = entry
    #controllo se non ho trovato nessun utente
    if opponent is None:
        print "No opponent found."
        return jsonify(success = False)
    #eseguo la transazione con l'utente trovato
    output = doTransaction(createGame, **({"opponents":[opponent]}))
    #gestisco l'output
    if output:
        print "Game %d created." % output.id, output
        return jsonify(success = True, game = output, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/invites", methods = ["GET"])
@auth_required
def getPendingInvites():
    invites = Invite.query.filter(Invite.receiver_id == g.user.id, Invite.accepted == None).all()
    print "User %s got pending invites." % g.user.username
    return jsonify(success = True, invites = invites)

#considerare di dare questa info alla creazione del websocket
@game.route("/invites/badge", methods = ["GET"])
@auth_required
def getPendingInvitesBadge():
    badge = Invite.query.filter(Invite.receiver_id == g.user.id, Invite.accepted == None).count()
    print "User %s got pending invites badges." % g.user.username
    return jsonify(success = True, badge = badge)

#considerare di dare questa info alla creazione del websocket
#TODO: controllare che l'invito non sia già stato accettato
@game.route("/invites/<int:game_id>", methods = ["POST"])
@needs_values("POST", "accepted")
@fetch_models(game_id = Game)
@auth_required
def processInvite(game_id):
    invite = Invite.query.filter(Invite.game_id == game_id, Invite.receiver_id == g.user.id).first()
    if not invite:
        print "User %s not allowed to process invite for game %d." % (g.user.username, game_id)
        raise NotAllowed()
    #TODO: gestire la logica che a un certo punto blocca gli inviti di gioco
    invite.accepted = g.post["accepted"]
    db.session.add(invite)
    db.session.commit()
    print "User %s processed invite for game %d:" % (g.user.username, game_id), invite
    return jsonify(success = True, invite = invite)
