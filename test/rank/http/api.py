# -*- coding: utf-8 -*-

def global_rank(self, thresold = None, direction = None, token = None):
    if not token:
        token = self.token
    suffix = ""
    if direction or thresold:
        suffix += "?"
    if direction:
        suffix += "direction=%s&" % direction
    if thresold:
        suffix += "thresold=%s" % thresold
    print suffix
    return self.app.get("/rank/global%s" % suffix, token = token)

def search(self, query, token = None):
    if not token:
        token = self.token
    url = "/rank/search"
    if query:
        url += "?query=%s" % query
    return self.app.get(url, token = token)
