# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g, send_file
from tp import app, db
from tp.auth.models import User
from tp.game.models import *
from tp.utils import doTransaction
from sqlalchemy.orm import aliased
from tp.decorators import auth_required, fetch_models, needs_values
from tp.ws_decorators import check_in_room
from tp.exceptions import ChangeFailed, NotAllowed
from tp.game.utils import updateScore, last_game_result_query, searchInRange, createGame, handleInvite, getUsersFromGame, getPartecipationFromGame, getRecentGames
from tp.base.utils import RoomType
import events
game = Blueprint("game", __name__, url_prefix = "/game")
quiz = Blueprint("quiz", __name__, url_prefix = "/quiz")
category = Blueprint("category", __name__, url_prefix = "/category")

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
    (game, invite) = doTransaction(createGame, **({"opponents": [opponent]}))
    if invite and game:
        print "Game %d created." % game.id
        events.invite_created([opponent], invite)
        return jsonify(success = True, game = game, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/leave", methods = ["POST"])
@auth_required
@fetch_models(game_id = Game)
def leave_game():
    game = g.models["game_id"]
    users = getUsersFromGame(game)
    user_ids = [u.id for u in users]
    #se non appartengo al gioco
    if g.user.id not in user_ids:
        raise NotAllowed()
    #se ci sono più di due giocatori
    if len(users) > 2:
        #TODO: gestire la multiutenza nel gioco (versione 2.0)
        #il game non finisce, e si flagga la partecipation dell'utente, in modo che si capisce che non gioca più
        return jsonify(success = False, reason = "Version 2.0")
    #se il numero di giocatori è corretto
    elif len(users) == 2:
        opponent = [u for u in users if u.id != g.user.id][0]
        #modifico il game settandogli tra l'altro lo winner
        game.ended = True
        game.winner_id = opponent.id
        db.session.add(game)
        db.session.commit()
        #modifico i punteggi degli utenti
        updateScore(game)
        #ritorno le varie risposte
        partecipations = [p.json for p in getPartecipationFromGame(game)]
        events.game_left(users, game, partecipations)
        return jsonify(success = True, ended = True, game = game, winner = opponent, partecipations = partecipations)
    #nessun avversario.. solo io nel gioco
    #NOTE: non dovrebbe succedere mai, in new_game l'opponent è obbligatorio
    return jsonify(success = False, message = "Nessun avversario in questo match!")

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
    (game, invite) = doTransaction(createGame, opponents = [opponent])
    #gestisco l'output
    if game and invite:
        print "Game %d created." % game.id
        events.invite_created([opponent], invite)
        return jsonify(success = True, game = game, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/invites", methods = ["GET"])
@auth_required
def getPendingInvites():
    invites = Invite.query.with_entities(Invite.game_id, Invite.sender_id, User.name.label("sender_name"), User.surname.label("sender_surname"), User.username.label("sender_username"), User.image.label("sender_image"))
    invites = invites.filter(Invite.receiver_id == g.user.id, Invite.accepted == None).join(User, Invite.sender_id == User.id).all()
    print "User %s got pending invites." % g.user.username
    return jsonify(success = True, invites = invites)

@game.route("/invites/<int:game_id>", methods = ["POST"])
@needs_values("POST", "accepted")
@fetch_models(game_id = Game)
@auth_required
def processInvite(game_id):
    invite = Invite.query.filter(Invite.game_id == game_id, Invite.receiver_id == g.user.id, Invite.accepted == None).first()
    game = g.models["game_id"]
    if not invite:
        print "User %s not allowed to process invite for game %d." % (g.user.username, game_id)
        raise NotAllowed()
    #TODO: gestire la logica che a un certo punto blocca gli inviti di gioco
    invite = doTransaction(handleInvite, invite = invite)
    if invite:
        events.invite_processed([invite.sender], invite)
        print "User %s processed invite for game %d:" % (g.user.username, game_id), invite
        return jsonify(success = True, invite = invite)
    else:
        raise ChangeFailed()

@game.route("/recents", methods = ["GET"])
@auth_required
def recent_games():
    recent_games = getRecentGames(g.user)
    return jsonify(success = True, recent_games = recent_games)

@quiz.route("/image/<int:id>", methods = ["GET"])
def getQuizImage(id):
    image = Image.query.filter(Image.id == id).first()
    print id, image.id, image.imagePath
    if image:
        return send_file(image.imagePath)
    raise NotAllowed()

@category.route("/image/<int:id>", methods = ["GET"])
def getCategoryImage(id):
    folder = app.config["QUIZ_IMAGE_FOLDER"]
    category = Category.query.filter(Category.id == id).first()
    if category:
        return send_file(category.imagePath)
    raise NotAllowed()
@game.route("/users/suggested", methods = ["GET"])
@auth_required
def get_suggested_users():
    a = aliased(Partecipation, "a")
    n = 10
    left_users = User.query.with_entities(User, last_game_result_query(User.id)).filter(User.score >= g.user.score).filter(User.id != g.user.id).order_by(User.score.desc()).limit(n).all()
    right_users = User.query.with_entities(User, last_game_result_query(User.id)).filter(User.score < g.user.score).filter(User.id != g.user.id).order_by(User.score.desc()).limit(n).all()

    left_min = len(left_users) < (n / 2)
    right_min = len(right_users) < (n / 2)
    #entrambi hanno meno di 5 elementi a testa
    if left_min and right_min:
        #ritorno un risultato con lunghezza < 10
        users = left_users + right_users
    #l'array di sinistra ha meno di 5 elementi
    elif left_min:
        #dall'array di destra prendo (10 - gli elementi di sinistra) elementi
        upper_bound = n - len(left_users)
        #prendo tutti quelli da sinistra
        users = left_users + right_users[:upper_bound]
    #l'array di destra ha meno di 5 elementi
    elif right_min:
        #dall'array di sinistra prendo (10 - gli elementi di destra) elementi
        lower_bound = len(left_users) - (n - len(right_users))
        #prendo tutti quelli da destra
        users = left_users[lower_bound:] + right_users
    #entrambi gli array hanno un numero di elementi >= a 5
    else:
        #prendo gli ultimi 5 elementi da quello di sinistra, e i primi 5 da destra
        users = left_users[(n/2):] + right_users[:(n/2)]
    output = sanitize_last_game_result(users)
    return jsonify(success = True, users = output)

def sanitize_last_game_result(users):
    output = []
    for user in users:
        item = user[0]
        last_winner = user[1]
        if last_winner is not None:
            item.last_game_won = (last_winner == g.user.id)
        output.append(item)
    return output

@game.route("/users/search", methods = ["GET"])
@needs_values("GET", "query")
@auth_required
def search_user():
    query = "%" + g.query.get("query") + "%"
    matches = User.query.with_entities(User, last_game_result_query(User.id)).filter(User.id != g.user.id).filter(User.username.ilike(query)).all()
    output = sanitize_last_game_result(matches)
    return jsonify(success = True, users = output)
