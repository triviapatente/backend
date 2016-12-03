# -*- coding: utf-8 -*-
from tp.events.utils import EventActions
from tp.events.decorators import event
from flask import g

@event("round_started", action = EventActions.create, preferences_key = "notification_round")
def round_started(room, round):
    data = {"round": round.json, "user": g.user.json}
    return (room, data)

@event("round_ended", action = EventActions.destroy, needs_push = False)
def round_ended(room, round):
    data = {"round": round.json, "user": g.user.json}
    return (room, data)

@event("category_chosen", action = EventActions.create, needs_push = False)
def category_chosen(room, category):
    data = {"category": category.json, "user": g.user.json}
    return (room, data)

@event("question_answered", action = EventActions.answer, needs_push = False)
def question_answered(room, quiz, correct):
    #non posso inviare la risposta all'utente!
    quiz_json = quiz.json
    del quiz_json["answer"]
    data = {"correct": correct, "quiz": quiz_json, "user": g.user.json}
    return (room, data)

#TODO: implementare questo evento
@event("gamescore_updated", action = EventActions.update, needs_push = False)
def score_updated(room, user, score):
    data = {"user": user.json, "score": score}
    return (room, data)
#TODO: implementare questo evento
@event("game_finished", action = EventActions.destroy)
def game_finished(room, game, winner, partecipations):
    data = {"score": score, "winner": winner.json, "partecipations": partecipations}
    return (room, data)

@event("game_left", action = EventActions.game_left)
def game_left(room, game, winner, partecipations):
    data = {"game": game.json, "user": g.user.json, "winner": winner.json, "partecipations": partecipations}
    return (room, data)

@event("new_game", action = EventActions.create, preferences_key = "notification_new_game")
def new_game(users, game):
    data = {"game": game.json}
    return (users, data)

@event("invite_accepted", action = EventActions.update)
def accept_invite(users, game):
    data = {"game": game.json, "user": g.user}
    return (users, data)

@event("invite_refused", action = EventActions.update)
def refuse_invite(users, game):
    data = {"game": game.json, "user": g.user}
    return (users, data)
