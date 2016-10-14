# -*- coding: utf-8 -*-

def new_game(self, opponent_id):
    return self.app.post("/game/new", token = self.token, data = {"opponent":opponent_id})

def new_random_game(self):
    return self.app.post("/game/new/random", token = self.token)

def get_pending_invites(self, token = None):
    if token is None:
        token = self.token
    return self.app.get("/game/invites", token = token)

def get_pending_invites_badge(self, token):
    if token is None:
        token = self.token
    return self.app.get("/game/invites/badge", token = token)

def process_invite(self, game_id, accepted):
    return self.app.post("/game/invites/" + game_id, token = self.token, data = {"accepted": accepted})
