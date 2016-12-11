# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# crawler built based on:
seed = 'http://m.patentati.it/quiz-patente-b/lista-domande.php'
baseUrl = 'http://m.patentati.it/'
# path where images are saved
import tp
tp.init()
from tp import app
imgPath = app.config["QUIZ_IMAGE_FOLDER"]

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DropTable

from crawler import crawler
from tp import db
from tp.game.models import Quiz, Category

# Create directory if it doesn't exist
import os

if not os.path.exists(imgPath):
    os.makedirs(imgPath)

### Extraction ###
print 'Start crawling ' + seed + '..'

db.engine.execute(DropTable(Quiz.__table__))
db.engine.execute(DropTable(Category.__table__))
db.create_all()
crawler.getCategories(db.session, seed, baseUrl, imgPath)

### Saving Data ###
print 'Saving data..'
db.session.commit()
print 'Done'
