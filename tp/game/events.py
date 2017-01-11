# -*- coding: utf-8 -*-
from tp.events.utils import EventActions
from tp.events.decorators import event
from flask import g
from tp.game.utils import isRoundEnded, get_round_infos, getOpponentFrom

@event("user_answered", action = EventActions.create, needs_push = False)
def user_answered(room, question, quiz):
    question.correct = (question.answer == quiz.answer)
    questionJSON = question.json
    del questionJSON["answer"]
    data = {"user": g.user.json, "answer": questionJSON}
    return (room, data)

@event("round_ended", action = EventActions.destroy, needs_push = False)
def round_ended(room, round):
    data = {"round": round.json, "user": g.user.json}
    return (room, data)

@event("category_chosen", action = EventActions.create, needs_push = False)
def category_chosen(room, category):
    data = {"category": category.json, "user": g.user.json}
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

class RecentGameEvents:
    #Eventi Recent games
    @staticmethod
    @event("recent_game", action = EventActions.create)
    def created(game, users = None):
        if users is None:
            users = [getOpponentFrom(game)]
        data = {"game": game}
        return (users, data)

    @staticmethod
    @event("recent_game", action = EventActions.update)
    def ended(game, users = None):
        if users is None:
            users = [getOpponentFrom(game)]
        data = {"game": game}
        return (users, data)

    @staticmethod
    @event("recent_game", action = EventActions.update)
    def turn_changed(game, my_turn, users = None):
        if users is None:
            users = [getOpponentFrom(game)]
        game.my_turn = my_turn
        data = {"game": game}
        return (users, data)
