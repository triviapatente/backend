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

@event("game", action = EventActions.destroy)
def game_ended(room, game, partecipations):
    data = {"game": game.json, "winner_id": game.winner_id, "partecipations": partecipations}
    return (room, data)

@event("user_left", action = EventActions.game_left)
def game_left(room, game, partecipations):
    data = {"game": game.json, "user_id": g.user.id, "winner_id": game.winner_id, "partecipations": partecipations}
    return (room, data)

@event("game", action = EventActions.create)
def new_game(game):
    opponent = getOpponentFrom(game)
    data = {"game": game.json, "user": g.user.json}
    return ([opponent], data)

class RecentGameEvents:
    #Eventi Recent games
    @staticmethod
    @event("recent_game", action = EventActions.create, needs_push = False)
    def created(game):
        opponent = getOpponentFrom(game)
        game.setOpponent(opponent)
        game.my_turn = True
        data = {"game": game.json}
        return ([opponent], data)

    @staticmethod
    @event("recent_game", action = EventActions.update, needs_push = False)
    def ended(game):
        opponent = getOpponentFrom(game)
        game.setOpponent(opponent)
        data = {"game": game.json}
        return ([opponent], data)

    @staticmethod
    @event("recent_game", action = EventActions.update, needs_push = False)
    def turn_changed(game, my_turn):
        opponent = getOpponentFrom(game)
        game.setOpponent(opponent)
        game.my_turn = my_turn
        data = {"game": game.json}
        return ([opponent], data)
