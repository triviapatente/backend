# -*- coding: utf-8 -*-
from commonpk import CommonPK
from category import Category
from base import Base
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship


class Quiz(Base, CommonPK):

  question = Column(String(250), nullable = False)
  answer = Column(Boolean, nullable = False)
  image = Column(String) #path dell'immagine oppure blob, da decidere
  category_id = Column(Integer, ForeignKey("category.id"), nullable = False)
  category = relationship(Category)
