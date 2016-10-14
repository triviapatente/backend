# -*- coding: utf-8 -*-

def new_game(self, token, opponent_id):
    return self.app.post("/game/new_game", token = token, data = {"opponent":opponent_id})
