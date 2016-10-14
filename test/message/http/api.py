# -*- coding: utf-8 -*-

#Utility methods
def getList(self, game_id, datetime):
    url = "/message/list/%d?datetime=%s" % (game_id, datetime)
    return self.app.get(url, token = self.token)
