# Import flask and template operators
from flask import Flask, render_template

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

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (base)

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

# app.register_blueprint(xyz_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()
