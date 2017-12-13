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
SQLALCHEMY_TEST_DATABASE_URI = 'postgresql://ted:ted@localhost:5432/triviapatente_test'

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
    "version": 0.9,
    "webservice type": "REST",
    "last_run": datetime.now(pytz.utc)
}
#mail config
#NOTE: temporaneo, quando compriamo il dominio è da cambiare
EMAIL_SENDER = "support@triviapatente.it"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_SSL = True
#MAIL_USE_TLS : default False
#MAIL_DEBUG : default app.debug
MAIL_USERNAME = "triviapatente@gmail.com"
MAIL_PASSWORD = "TriviaPatente1"

INIT_DB = False
TRAP_BAD_REQUEST_ERRORS = DEBUG
DEFAULT_USER_SCORE = 100

SQLALCHEMY_TRACK_MODIFICATIONS = True

MAX_CHARS_FOR_FIELD = 300

#vite iniziali per utente
INITIAL_LIFES = 3

#numero minimo di caratteri username
USERNAME_MIN_CHARS = 3

#numero minimo di caratteri password
PASSWORD_MIN_CHARS = 7

#estensioni ammesse
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#numero di categorie proposte per il gioco
NUMBER_OF_CATEGORIES_PROPOSED = 5
#numero di domande per gioco
NUMBER_OF_QUESTIONS_PER_ROUND = 4
#numero di recent games per pagina
RECENT_GAMES_PER_PAGE = 30
#numero di round per partita
NUMBER_OF_ROUNDS = 5
#percorso dove vengono salvate le immagini dei quiz
QUIZ_IMAGE_FOLDER = "images/"
CATEGORY_IMAGE_FOLDER = "images/categories/"
#percorso delle immagini utenti
UPLOAD_FOLDER = "images/users/"
#numero di risultati mostrati nella classifica italiana
RESULTS_LIMIT_RANK_ITALY = 20
#fattore moltiplicativo massimo e minimo
#MAX_MULTIPLIER_FACTOR = 100
#MIN_MULTIPLIER_FACTOR = 32
#bonus di punteggio per partita giocata
#BONUS_SCORE = 10
#incremento di range ogni tentativo
#RANGE_INCREMENT = 50
#range iniziale
#INITIAL_RANGE = 200
#numero di punti assegnati/tolti in caso di uscita dalla partita
SCORE_ON_LEFT_GAME = 5
#terms and conditions url
TERMS_URL = "http://www.pdf995.com/samples/pdf.pdf"
#terms and conditions last update
TERMS_AND_CONDITIONS_LAST_UPDATE = datetime(2017, 12, 13, 00, 21) #00:21 of 13/12/2017
#privacy policy url
PRIVACY_POLICY_URL = "http://www.pdf995.com/samples/pdf.pdf"
#privacy policy last update
PRIVACY_POLICY_LAST_UPDATE = datetime(2017, 12, 13, 00, 21) #00:21 of 13/12/2017
#url to android store
ANDROID_STORE_URL = "http://www.android.com"
#url to iOS store
IOS_STORE_URL = "http://www.apple.com"
#numero di messaggi nuovi mostrati ad ogni scroll
MESSAGE_PER_SCROLL = 50
#numero di divisioni dati nel chart delle statistiche
NUMBER_OF_CHART_DIVISORS = 15
