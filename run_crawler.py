# -*- coding: utf-8 -*-
# import sys
# import importlib
# importlib.reload(sys)
# sys.setdefaultencoding('utf8')

# crawler built based on:
seed = 'http://m.patentati.it/quiz-patente-b/lista-domande.php'
baseUrl = 'http://m.patentati.it/'
# path where images are saved
import tp
tp.init()
print('App initialized')
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
print('Creating images dir')

if not os.path.exists(imgPath):
    os.makedirs(imgPath)
print('Image dir created')

### Extraction ###
print(f"Start crawling {seed}..")

db.create_all()
crawler.getCategories(db.session, seed, baseUrl, imgPath)

### Saving Data ###
print('Saving data..')
db.session.commit()
print('Done')
