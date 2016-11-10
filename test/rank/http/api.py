# -*- coding: utf-8 -*-

def global_rank(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/rank/global", token = token)

def search(self, query, token = None):
    if not token:
        token = self.token
    url = "/rank/search"
    if query:
        url += "?query=%s" % query
    return self.app.get(url, token = token)
