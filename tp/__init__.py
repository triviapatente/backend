# -*- coding: utf-8 -*-


app = None
socketio = None
db = None
mail = None
redisDB = None
limiter = None
from flask.json import JSONEncoder
#classe che viene utilizzata internamente da flask per fare il JSON encoding di una classe
class TPJSONEncoder(JSONEncoder):
    def default(self, obj):
        #la classe ha la proprietà json? (Base e le sue derivate la hanno)
        serialized = getattr(obj, "json", None)
        if serialized:
            #se si, ritornala direttamente
            return serialized
        #se no, gestisci con la classe padre (genererà un errore se la classe non è serializable)
        return super(TPJSONEncoder, self).default(obj)

def init(testing = False, ci = False):
    print("app initialization")
    global app
    global socketio
    global db
    global mail
    global redisDB
    global limiter
    # Import flask and template operators
    from flask import Flask, render_template, jsonify, json

    # Import SQLAlchemy
    from flask_sqlalchemy import SQLAlchemy
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from flask_mail import Mail
    from flask_cors import CORS

    # Import SocketIO
    from flask_socketio import SocketIO, emit

    # Define the WSGI application object
    app = Flask(__name__)


    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    #aggiungo il json encoder custom
    app.json_encoder = TPJSONEncoder

    # Configurations
    # This line imports contents of config.py in app.config
    app.config.from_object('config')
    key_func = None
    import uuid
    if testing or ci:
        del app.config["RATELIMIT_STORAGE_URL"]
        key_func = uuid.uuid4
    else:
        key_func = get_remote_address
    limiter = Limiter(
        app,
        key_func=key_func,
        default_limits=app.config["DDOS_LIMITS"]
    )

    if not testing and not ci:
        import redis
        redisDB = redis.StrictRedis(host="localhost", port=6379, db=0)
        #configure ddos limiter

    if testing:
        print("enabling testing mode..")
        if ci:
            print("enabling ci mode..")
            app.config["SQLALCHEMY_TEST_DATABASE_URI"] = app.config["SQLALCHEMY_TEST_DATABASE_URI"].replace("localhost", "postgres")
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_TEST_DATABASE_URI"]

    file = open('tp/templates/gdpr/data.txt')
    app.config["GDPR_DATA_TEMPLATE"] = file.read()
    file.close()

    # Define the database object which is imported
    # by modules and controllers
    db = SQLAlchemy(app)
    socketio = SocketIO(json = json, async_mode='eventlet')
    if app.config["DEBUG"] == True or testing or ci:
        print("Starting SocketIO without Redis..")
        socketio.init_app(app)
    else:
        print("Starting SocketIO with Redis..")
        socketio.init_app(app, message_queue='redis://')
    mail = Mail()
    mail.init_app(app)

    from flask_apscheduler import APScheduler
    from tp.cron.config import Config
    import atexit
    app.config.from_object(Config())
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait= True))
    import logging

    log = logging.getLogger('apscheduler.executors.default')
    log.setLevel(logging.INFO)  # DEBUG

    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)

    from tp.exceptions import TPException
    from flask import request, session
    import traceback, sys

    @app.teardown_request
    def onRequestDown(exc):
        db.session.remove()
    #registro la generica exception TPException creata. D'ora in poi quando in una richiesta lancerò un exception che deriva da questa verrà spedito all'utente l'output di questa funzione
    @app.errorhandler(TPException)
    def handleTPException(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        print(f"API Error {error.status_code}: {error.message}")
        return response
    @socketio.on_error_default
    def handle_socket_error(error):
        response = None
        event = request.event["message"]
        if issubclass(error.__class__, TPException):
            response = error.to_dict()
            print("Socket Error {error.status_code} ({event}): {error.message}")
        else:
            error = str(error)
            #internal server error
            response = {"error": error, "success": False, "status_code": 500}
            print("Socket Error {error} ({event})")
        print("Traceback: {traceback.format_exc(sys.exc_info())}")
        emit(event, response)


    from tp.auth.controllers import auth, account, info, fb
    from tp.base.controllers import base, gdpr
    from tp.game.controllers import game, quiz, category, training
    from tp.message.controllers import message
    from tp.preferences.controllers import preferences
    from tp.purchases.controllers import shop
    from tp.rank.controllers import rank
    from tp.stats.controllers import stats


    # Register blueprint(s)
    app.register_blueprint(auth)
    app.register_blueprint(base)
    app.register_blueprint(game)
    app.register_blueprint(quiz)
    app.register_blueprint(category)
    app.register_blueprint(training)
    app.register_blueprint(gdpr)
    #app.register_blueprint(preferences)
    app.register_blueprint(account)
    #app.register_blueprint(info)
    #app.register_blueprint(fb)
    #app.register_blueprint(shop)
    app.register_blueprint(rank)
    app.register_blueprint(stats)


    # Add websockets
    import tp.base.web_sockets
    #import tp.message.web_sockets
    import tp.game.web_sockets
    # Creazione directory per upload users pictures
    import os

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    # Build the database:
    # Discard old configurations
    # Attenzione! Questa chiamata è distruttiva, distrugge infatti ogni contenuto del db. Usarla con cautela.
    if app.config["DEBUG"] and app.config["INIT_DB"]:
        db.drop_all()


    #The following lines represents migration stuff
    #TODO: use flask-migrate
    from sqlalchemy.schema import CreateTable, DropTable
    from tp.game.models import Round, Question, Game, Partecipation

    from sqlalchemy.ext.compiler import compiles
    #this line make droptable to be in cascade mode for postgresql
    #@compiles(DropTable, "postgresql")
    #def _compile_drop_table(element, compiler, **kwargs):
    #    return compiler.visit_drop_table(element) + " CASCADE"

    # This will create the database file using SQLAlchemy
    db.create_all()

    #from tp.purchases.models import ShopItem
    #ShopItem.init()
