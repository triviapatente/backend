# -*- coding: utf-8 -*-
from tp.events.utils import EventActions
from tp.events.decorators import event
from flask import g

@event("round_started", action = EventActions.create, preferences_key = "notification_round")
def round_started(room, round):
    data = {"round": round.json}
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
#TODO: implementare questo evento, e la chiamata http associata
@event("game_left", action = EventActions.game_left)
def game_left(room, game):
    data = {"game": game.json, "user": g.user.json}
    return (room, data)

@event("new_game", action = EventActions.create, preferences_key = "notification_new_game")
def new_game(room, game):
    data = {"game": game.json}
    return (room, data)