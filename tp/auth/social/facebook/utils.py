# -*- coding: utf-8 -*-
from facebook import GraphAPI
class FBManager(GraphAPI):
    APP_ID = 170873569983444
    APP_SECRET = "ae42ef2543f27349564f72c90635a058"
    def getTokenInfos(self):
        return self.debug_access_token(self.access_token, self.APP_ID, self.APP_SECRET)

    def getUserInfos(self):
        return self.get_object("me", fields = "id,name,first_name,last_name,email,birthday")

    @staticmethod
    def profileImage(tokenInfos):
        fb_id = tokenInfos.get("data").get("user_id")
        return "https://graph.facebook.com/%s/picture?type=normal" % fb_id
