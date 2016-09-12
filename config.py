# -*- coding: utf-8 -*-

import os, pytz
from datetime import datetime

# Statement for enabling the development environment
DEBUG = True

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
INIT_DB = True
DEFAULT_USER_SCORE = 800

SQLALCHEMY_TRACK_MODIFICATIONS = True
