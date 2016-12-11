# -*- coding: utf-8 -*-
from tp.events.utils import EventActions
from tp.events.decorators import event
from flask import g
from tp.game.utils import isRoundEnded, get_info_for_single

@event("round_started", action = EventActions.create, preferences_key = "notification_round")
def round_started(room, round):
    data = {"round": round.json, "user": g.user.json}
    return (room, data)

@event("round_ended", action = EventActions.destroy, needs_push = False)
def round_ended(room, round):
    #check if round is ended for everyone
    globally_ended = isRoundEnded(round)
    data = {"round": round.json, "user": g.user.json, "globally": globally_ended}
    if globally_ended:
        (quizzes, answers, category) = get_info_for_single(round.id)
        data["quizzes"] = quizzes
        data["answers"] = answers
        data["category"] = category
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

@event("game_ended", action = EventActions.destroy)
def game_ended(room, game, partecipations):
    data = {"game": game.json, "winner_id": game.winner_id, "partecipations": partecipations}
    return (room, data)

@event("game_left", action = EventActions.game_left)
def game_left(room, game, partecipations):
    data = {"game": game.json, "user_id": g.user.id, "winner_id": game.winner_id, "partecipations": partecipations}
    return (room, data)

@event("invite_created", action = EventActions.create, preferences_key = "notification_new_game")
def invite_created(users, invite):
    data = {"invite": invite.json, "user": g.user}
    return (users, data)

@event("invite_processed", action = EventActions.update)
def invite_processed(users, invite):
    data = {"accepted": invite.accepted}
    return (users, data)
