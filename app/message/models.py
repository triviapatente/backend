# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.base.models import Base, CommonPK

class Message(Base, CommonPK):

  content = Column(String, nullable = False)
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
  user = relationship("User")
