# -*- coding: utf-8 -*-
from datetime import datetime

def timestamp(date):
    return (date - datetime(1970, 1, 1)).total_seconds()
