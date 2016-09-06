# -*- coding: utf-8 -*-
from base import Base
from commonpk import CommonPK

from sqlalchemy import Column, String

class Category(Base, CommonPK):

  name = Column(String(250), nullable = False)
