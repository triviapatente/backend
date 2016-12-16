# -*- coding: utf-8 -*-
import time
from datetime import datetime
def getList(self, game_id, datetime = datetime.now(), token = None):
    if not token:
        token = self.token
    timestamp = time.mktime(datetime.timetuple()) + datetime.microsecond / 1000
    url = "/message/list/%d?timestamp=%s" % (game_id, timestamp)
    return self.app.get(url, token = token)
