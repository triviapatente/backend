# -*- coding: utf-8 -*-

from datetime import datetime

def getList(self, game_id, datetime = datetime.now(), token = None):
    if not token:
        token = self.token
    url = "/message/list/%d?datetime=%s" % (game_id, datetime)
    return self.app.get(url, token = token)
