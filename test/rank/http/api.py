# -*- coding: utf-8 -*-

def global_rank(self, thresold = None, direction = None, token = None):
    if not token:
        token = self.token
    suffix = ""
    if direction  is not None or thresold is not None:
        suffix += "?"
    if direction is not None:
        suffix += "direction=%s&" % direction
    if thresold is not None:
        suffix += "thresold=%s" % thresold

    return self.app.get("/rank/global%s" % suffix, token = token)

def search(self, query, token = None):
    if not token:
        token = self.token
    url = "/rank/search"
    if query:
        url += "?query=%s" % query
    return self.app.get(url, token = token)
