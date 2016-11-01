# -*- coding: utf-8 -*-

def get_wrong_answers(self, category, token = None):
    if not token:
        token = self.token
    return self.app.get("/stats/wrong_answers/%s" % category, token = token)

def get_progresses(self, category, token = None):
    if not token:
        token = self.token
    return self.app.get("/stats/progresses/%s" % category, token = token)

def get_categories(self, token = None):
    return self.app.get("/stats/categories")
