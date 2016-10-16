# -*- coding: utf-8 -*-
from tp.event.utils import EventActions
from tp.events.decorators import event

@event("round_started", action = EventActions.create, include_self = False, preferences_key = "notification_round")
def round_started(room, round):
    data = {"round": round.json}
    return (room, data)

@event("category_chosen", action = EventActions.offline, include_self = False, needs_push = False)
def category_chosen(room, category):
    data = {"category": category.json}
    return (room, data)

@event("question_answered", action = EventActions.answer, include_self = False, needs_push = False)
def question_answered(room, quiz, correct):
    #non posso inviare la risposta all'utente!
    del quiz.answer
    data = {"correct": correct, "quiz": quiz.json}
    return (room, data)

@event("gamescore_updated", action = EventActions.update, include_self = True, needs_push = False)
def score_updated(room, user, score):
    data = {"user": user.json, "score": score}
    return (room, data)

@event("game_left", action = EventActions.game_left, include_self = True)
def game_left(room, game, user):
    data = {"game": game.json, "user": user.json}
    return (room, data)

@event("new_game", action = EventActions.create, include_self = True, preferences_key = "notification_new_game")
def new_game(room, game):
    data = {"game": game.json}
    return (room, data)
