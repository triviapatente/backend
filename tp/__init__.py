# -*- coding: utf-8 -*-


app = None
socketio = None
db = None

def init(testing = False, ci = False):
    print "app initialization"
    global app
    global socketio
    global db

    # Import flask and template operators
    from flask import Flask, render_template, jsonify, json

    # Import SQLAlchemy
    from flask.ext.sqlalchemy import SQLAlchemy

    from tp.base.utils import TPJSONEncoder

    # Import SocketIO
    from flask_socketio import SocketIO

    # Define the WSGI application object
    app = Flask(__name__)

    #aggiungo il json encoder custom
    app.json_encoder = TPJSONEncoder

    # Configurations
    # This line imports contents of config.py in app.config
    app.config.from_object('config')


    if testing:
        print "enabling testing mode.."
        if ci:
            print "enabling ci mode..."
            app.config["SQLALCHEMY_TEST_DATABASE_URI"] = app.config["SQLALCHEMY_TEST_DATABASE_URI"].replace("localhost", "postgres")
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_TEST_DATABASE_URI"]


    # Define the database object which is imported
    # by modules and controllers
    db = SQLAlchemy(app)
    socketio = SocketIO(app, json = json)

    from tp.exceptions import TPException
    #registro la generica exception TPException creata. D'ora in poi quando in una richiesta lancerò un exception che deriva da questa verrà spedito all'utente l'output di questa funzione
    @app.errorhandler(TPException)
    def handleTPException(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        print "API Error %d: %s" % (error.status_code, error.message)
        return response
    @socketio.on_error_default
    def handle_socket_error(error):
        response = None
        if issubclass(error.__class__, TPException):
            response = json.dumps(error.to_dict())
            print "Socket Error %d: %s" % (error.status_code, error.message)
        else:
            response = str(error)
            print "Socket Error %s" % response
        emit("error", response)


    from tp.auth.controllers import auth, account, info
    from tp.base.controllers import base
    from tp.game.controllers import game
    from tp.message.controllers import message
    from tp.push.controllers import push
    from tp.preferences.controllers import preferences
    from tp.purchases.controllers import shop


    # Register blueprint(s)
    app.register_blueprint(auth)
    app.register_blueprint(base)
    app.register_blueprint(game)
    app.register_blueprint(message)
    app.register_blueprint(push)
    app.register_blueprint(preferences)
    app.register_blueprint(account)
    app.register_blueprint(info)
    app.register_blueprint(shop)


    # Add websockets
    import tp.auth.web_sockets
    import tp.base.web_sockets
    import tp.message.web_sockets
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
    from tp.game.models import Round, Question, Game, Invite, partecipation

    from sqlalchemy.ext.compiler import compiles
    #this line make droptable to be in cascade mode for postgresql
    @compiles(DropTable, "postgresql")
    def _compile_drop_table(element, compiler, **kwargs):
        return compiler.visit_drop_table(element) + " CASCADE"

    #db.engine.execute(DropTable(Round.__table__))
    #db.engine.execute(CreateTable(Round.__table__))
    #db.engine.execute(DropTable(Game.__table__))
    #db.engine.execute(CreateTable(Game.__table__))
    #db.engine.execute(DropTable(Question.__table__))
    #db.engine.execute(CreateTable(Question.__table__))
    #db.engine.execute(DropTable(Invite.__table__))
    #db.engine.execute(CreateTable(Invite.__table__))
    #db.engine.execute(DropTable(partecipation))
    #db.engine.execute(CreateTable(partecipation))
    #end migration

    # This will create the database file using SQLAlchemy
    db.create_all()
