# -*- coding: utf-8 -*-
from flask import json

def new_game(self, opponent_id, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/new", token = token, data = {"opponent":opponent_id})

def new_random_game(self, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/new/random", token = self.token)

def leave_game(self, game_id, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/leave", token = token, data = {"game_id": game_id})

def recent_games(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/game/recents", token = token)

def suggested_users(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/game/users/suggested", token = token)

def leave_score_decrement(self, game_id, token = None):
    if not token:
        token = self.token
    suffix = "?game_id="
    if game_id:
        suffix += "%s" % game_id
    return self.app.get("/game/leave/decrement%s" % suffix, token = token)

def search_user(self, query, token = None):
    if not token:
        token = self.token
    url = "/game/users/search"
    if query:
        url += "?query=%s" % query
    return self.app.get(url, token = token)

def get_training_questions(self, random, token = None):
    if not token:
        token = self.token
    query = ""
    if random is not None:
        query = "?random=%r" % random

    return self.app.get("/training/new%s" % query, token = token)

def get_trainings(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/training/all", token = token)

def get_training(self, id, token = None):
    if not token:
        token = self.token
    path = ""
    if id is not None:
        path = "%d" % id
    return self.app.get("/training/%s" % path, token = token)

def tickle(self, round_id, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/tickle", data = {"round": round_id}, token = token)

def answer_training(self, answers, token = None):
    if not token:
        token = self.token
    if answers is not None:
        for (quiz_id, answer) in answers.items():
            answers["%s" % quiz_id] = answers.pop(quiz_id)
    return self.app.post("/training/new", token = token, data = json.dumps(dict(answers = answers)), content_type='application/json')
