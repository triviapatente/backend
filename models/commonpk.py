# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer

class CommonPK(object):

    id =  Column(Integer, primary_key = True)
