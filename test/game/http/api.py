# -*- coding: utf-8 -*-

def newGame(self, opponent_id):
    return self.app.post("/game/new_game", token = self.token, data = {"opponent":opponent_id})
