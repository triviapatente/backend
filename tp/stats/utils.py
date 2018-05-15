# -*- coding: utf-8 -*-
from datetime import datetime

def timestamp(date, tz):
    unix = datetime(1970, 1, 1, 0, 0, 0)
    return (date - unix).total_seconds()
