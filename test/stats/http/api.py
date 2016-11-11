# -*- coding: utf-8 -*-
def get_info(self, category, token = None):
    if not token:
        token = self.token
    return self.app.get("/stats/detail/%s" % category, token = token)

def get_categories(self, token = None):
    return self.app.get("/stats/categories")
