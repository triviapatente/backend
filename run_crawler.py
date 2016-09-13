# -*- coding: utf-8 -*-

# crawler built based on:
seed = 'http://m.patentati.it/quiz-patente-b/lista-domande.php'
path = 'images/'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crawler import crawler
from app.base.models import Base

engine = create_engine('postgresql://ted:ted@localhost:5432/triviapatente')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

### Extraction ###
print 'Start crawling ' + seed + '..'
crawler.getCategories(session, seed, path)

### Saving Data ###
print 'Saving data..'
session.commit()
print 'Done'
