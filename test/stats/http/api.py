# -*- coding: utf-8 -*-
def get_info(self, category, token = None):
    if not token:
        token = self.token
    url = "/stats/detail/"
    if category:
        url += "%d" % category
    return self.app.get(url, token = token)

def get_categories(self, token = None):
    return self.app.get("/stats/categories")
