# -*- coding: utf-8 -*-

def new_game(self, opponent_id, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/new", token = token, data = {"opponent":opponent_id})

def new_random_game(self, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/new/random", token = self.token)

def get_pending_invites(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/game/invites", token = token)

def leave_game(self, game_id, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/leave", token = token, data = {"game_id": game_id})

def process_invite(self, game_id, accepted, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/invites/%s" % game_id, token = token, data = {"accepted": accepted})

def recent_games(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/game/recents", token = token)

def suggested_users(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/game/users/suggested", token = token)

def search_user(self, query, token = None):
    if not token:
        token = self.token
    url = "/game/users/search"
    if query:
        url += "?query=%s" % query
    return self.app.get(url, token = token)
