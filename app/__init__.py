# -*- coding: utf-8 -*-

# Import flask and template operators
from flask import Flask, render_template, jsonify

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

from app.base.utils import TPJSONEncoder

# Define the WSGI application object
app = Flask(__name__)

#aggiungo il json encoder custom
app.json_encoder = TPJSONEncoder

# Configurations
# This line imports contents of config.py in app.config
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

from app.auth.controllers import auth
from app.base.controllers import base
from app.game.controllers import game
from app.message.controllers import message
from app.push.controllers import push

# Register blueprint(s)
app.register_blueprint(auth)
app.register_blueprint(base)
app.register_blueprint(game)
app.register_blueprint(message)
app.register_blueprint(push)

from app.exceptions import TPException
#registro la generica exception TPException creata. D'ora in poi quando in una richiesta lancerò un exception che deriva da questa verrà spedito all'utente l'output di questa funzione
@app.errorhandler(TPException)
def handleTPException(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    print "API Error %d: %s" % (error.status_code, error.message)
    return response

# Build the database:
# Discard old configurations
# Attenzione! Questa chiamata è distruttiva, distrugge infatti ogni contenuto del db. Usarla con cautela.
if app.config["DEBUG"] and app.config["INIT_DB"]:
    db.drop_all()
# This will create the database file using SQLAlchemy
db.create_all()
