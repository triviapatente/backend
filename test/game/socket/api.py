# -*- coding: utf-8 -*-

def init_round(socket, game, number):
    socket.emit("init_round", {"number": number, "game": game})
    return socket.get_received()

def get_questions(self, round_id, game, category):
    self.socket.emit("get_questions", token = token, data = {"round_id": round_id, "game": game, "category": category})
    return self.socket.get_received()

def get_random_categories(self, round_id, game):
    self.socket.emit("get_random_categories", {"round_id": round_id, "game": game})
    return self.socket.get_received()

def answer(self, answer, game, question):
    self.socket.emit("answer", {"answer": answer, "game": game, "question": question})
    return self.socket.get_received()

def choose_category(self, category, game, round):
    self.socket.emit("choose_category", {"category": category, "game": game, "round": round})
    return self.socket.get_received()
