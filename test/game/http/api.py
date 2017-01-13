# -*- coding: utf-8 -*-

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
