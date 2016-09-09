# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.base.models import Base, CommonPK
from app.auth.models import User



class Installation(Base, CommonPK):

  os = Column(Enum("iOS", "Android", name = "os_type_enum"), nullable = False)
  token = Column(String, nullable = False) #token che rappresenta l'installazione in uno specifico device dell'app
  device_id = Column(String, nullable = False) #id che rappresenta univocamente un device
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
  user = relationship(User)
