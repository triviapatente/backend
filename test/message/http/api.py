# -*- coding: utf-8 -*-

from datetime import datetime

#Utility methods
def getList(self, game_id, datetime = datetime.now()):
    url = "/message/list/%d?datetime=%s" % (game_id, datetime)
    return self.app.get(url, token = self.token)
