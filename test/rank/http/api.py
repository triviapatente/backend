# -*- coding: utf-8 -*-

def global_rank(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/rank/global", token = token)
