
def obtainCurrentUserFrom(rank, user_id):
    for user in rank:
        if user.get("id") == user_id:
            return
    assert False
