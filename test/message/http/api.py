# -*- coding: utf-8 -*-

#Utility methods
def getList(self, game_id):
    return self.app.get("message/list/%s" game_id, token = self.token)
