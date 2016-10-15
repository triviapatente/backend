# -*- coding: utf-8 -*-

def init_round(socket, game, number):
    socket.emit("init_round", {"number": number, "game": game})
    return socket.get_received()

def get_questions(socket, round_id, game):
    socket.emit("get_questions", {"round_id": round_id, "game": game})
    return socket.get_received()

def get_categories(socket, game, round_id):
    socket.emit("get_categories", {"round_id": round_id, "game": game})
    return socket.get_received()

def answer(socket, answer, game, round, quiz):
    socket.emit("answer", {"answer": answer, "game": game, "round_id": round, "quiz_id": quiz})
    return socket.get_received()

def choose_category(socket, category, game, round):
    socket.emit("choose_category", {"category": category, "game": game, "round_id": round})
    return socket.get_received()
