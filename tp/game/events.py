# -*- coding: utf-8 -*-
from tp.events.utils import EventActions
from tp.events.decorators import event
from flask import g
from tp.base.utils import jsonifyDates
from tp.game.utils import isRoundEnded, get_round_infos, getOpponentFrom

@event("user_answered", action = EventActions.create)
def user_answered(room, question, quiz):
    question.correct = (question.answer == quiz.answer)
    questionJSON = question.json
    del questionJSON["answer"]
    data = {"user": jsonifyDates(g.user.json), "answer": questionJSON}
    return (room, data, None)

@event("round_ended", action = EventActions.destroy)
def round_ended(room, round):
    data = {"round": jsonifyDates(round.json), "user": jsonifyDates(g.user.json)}
    return (room, data, None)
@event("tickle", action = EventActions.notify)
def tickle(game, opponent):
    message = "L'utente %s sta aspettando che tu completi il turno!" % g.user.displayName
    push_infos = {"game": jsonifyDates(game.json), "opponent": jsonifyDates(g.user.json), "message": message}
    return ([opponent], None, push_infos)

@event("category_chosen", action = EventActions.create)
def category_chosen(room, category):
    data = {"category": jsonifyDates(category.json), "user": jsonifyDates(g.user.json)}
    return (room, data, None)

@event("game_ended", action = EventActions.destroy)
def game_ended(room, game, partecipations):
    message = game.getGameResultPushMessage()
    push_infos = {"game": jsonifyDates(game.json), "opponent": jsonifyDates(g.user.json), "message": message}
    data = {"game": game.json, "winner_id": game.winner_id, "partecipations": partecipations}
    return (room, data, push_infos)

@event("your_turn", action = EventActions.update)
def your_turn(game, opponent):
    push_infos = {"game": jsonifyDates(game.json), "opponent": jsonifyDates(g.user.json), "message": "Partita con %s: è il tuo turno!" % g.user.displayName}
    return ([opponent], {}, push_infos)

@event("user_left_game", action = EventActions.game_left)
def game_left(room, game, partecipations):
    message = game.getGameLeftPushMessage()
    push_infos = {"game": jsonifyDates(game.json), "opponent": jsonifyDates(g.user.json), "message": message}
    data = {"game": game.json, "user_id": g.user.id, "winner_id": game.winner_id, "partecipations": partecipations, "annulled": game.isAnnulled()}
    return (room, data, push_infos)

@event("game", action = EventActions.create)
def new_game(game):
    opponent = getOpponentFrom(game.id)
    data = {"game": jsonifyDates(game.json), "user": jsonifyDates(g.user.json)}
    push_infos = {"game": jsonifyDates(game.json), "opponent": jsonifyDates(g.user.json), "message": "%s ti ha sfidato a una partita! Fagli vedere chi è il più in gamba!" % g.user.displayName}
    return ([opponent], data, push_infos)

class RecentGameEvents:
    #Eventi Recent games
    @staticmethod
    @event("recent_game", action = EventActions.notify)
    def change(opponent):
        data = {"recent_game_changed": True}
        return ([opponent], data, None)
