# -*- coding: utf-8 -*-

def new_game(self, opponent_id, token = None):
    if not token:
        token = self.token
    return self.app.post("/game/new", token = token, data = {"opponent":opponent_id})

def new_random_game(self):
    return self.app.post("/game/new/random", token = self.token)

def get_pending_invites(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/game/invites", token = token)

def get_pending_invites_badge(self, token):
    if not token:
        token = self.token
    return self.app.get("/game/invites/badge", token = token)

def process_invite(self, token, game_id, accepted):
    if not token:
        token = self.token
    return self.app.post("/game/invites/%s" % game_id, token = token, data = {"accepted": accepted})
