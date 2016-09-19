# -*- coding: utf-8 -*-

# crawler built based on:
seed = 'http://m.patentati.it/quiz-patente-b/lista-domande.php'
baseUrl = 'http://m.patentati.it/'
# path where images are saved
from app import app
imgPath = app.config["QUIZ_IMAGE_FOLDER"]

print imgPath
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# from crawler import crawler
# from app import db
#
# # Create directory if it doesn't exist
# import os
#
# if not os.path.exists(imgPath):
#     os.makedirs(imgPath)
#
# ### Extraction ###
# print 'Start crawling ' + seed + '..'
# crawler.getCategories(db.session, seed, baseUrl, imgPath)
#
# ### Saving Data ###
# print 'Saving data..'
# db.session.commit()
# print 'Done'
