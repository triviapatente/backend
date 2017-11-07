# -*- coding: utf-8 -*-

def init_round(socket, game, token):
    socket.emit("init_round", {"tp-session-token": token, "body": {"game": game}})
    return socket.get_received()

def get_questions(socket, game, round_id, token):
    socket.emit("get_questions", {"tp-session-token": token, "body": {"round_id": round_id, "game": game}})
    return socket.get_received()

def get_categories(socket, game, round_id, token):
    socket.emit("get_categories", {"tp-session-token": token, "body": {"round_id": round_id, "game": game}})
    return socket.get_received()

def answer(socket, answer, game, round, quiz, token):
    socket.emit("answer", {"tp-session-token": token, "body": {"answer": answer, "game": game, "round_id": round, "quiz_id": quiz}})
    return socket.get_received()

def choose_category(socket, category, game, round, token):
    socket.emit("choose_category", {"tp-session-token": token, "body": {"category": category, "game": game, "round_id": round}})
    return socket.get_received()
def round_details(socket, game, token):
    socket.emit("round_details", {"tp-session-token": token, "body": {"game": game}})
    return socket.get_received()
