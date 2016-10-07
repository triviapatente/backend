# -*- coding: utf-8 -*-

import os, pytz
from datetime import datetime

# Statement for enabling the development environment
DEBUG = True

#port used to serve this service
PORT = 8000

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'postgresql://ted:ted@localhost:5432/triviapatente'

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "dssovnjaeknbjkrebnwdvlknfvbkndfbl"

# Secret key for signing cookies
SECRET_KEY = "dvkljmdklvmvdkjVSDLjmvlfsnv.kmvsdvsdlvn"

PUBLIC_INFOS = {
    "name": "TriviaPatente Webservice",
    "version": 0.1,
    "webservice type": "REST",
    "last_run": datetime.now(pytz.utc)
}
INIT_DB = False
TRAP_BAD_REQUEST_ERRORS = DEBUG
DEFAULT_USER_SCORE = 800

SQLALCHEMY_TRACK_MODIFICATIONS = True

#vite iniziali per utente
INITIAL_LIFES = 3

#percorso delle immagini utenti
UPLOAD_FOLDER = "users/images/"
#estensioni ammesse
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#numero di categorie proposte per il gioco
NUMBER_OF_CATEGORIES_PROPOSED = 5
#numero di domande per gioco
NUMBER_OF_QUESTIONS_PER_ROUND = 4
#percorso dove vengono salvate le immagini dei quiz
QUIZ_IMAGE_FOLDER = "images/"
#numero di risultati mostrati nella classifica italiana
RESULTS_LIMIT_RANK_ITALY = 10
#fattore moltiplicativo massimo e minimo
MAX_MULTIPLIER_FACTOR = 100
MIN_MULTIPLIER_FACTOR = 32
#numero di messaggi nuovi mostrati ad ogni scroll
MESSAGE_PER_SCROLL = 50
