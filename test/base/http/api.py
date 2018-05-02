# -*- coding: utf-8 -*-

def contact(self, message, scope, token = None):
    if not token:
        token = self.token
    return self.app.post("/ws/contact", token = token, data = {"message": message, "scope": scope})

def get_instagram_photos(self):
    return self.app.get("/ws/instagram")
