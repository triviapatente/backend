# -*- coding: utf-8 -*-
#!/usr/bin/python

# import sys
# import importlib
# importlib.reload(sys)
# sys.setdefaultencoding('utf8')

import eventlet
eventlet.monkey_patch()

from subprocess import call


import tp
tp.init()

from tp import app, socketio

print('Running the service..')
debug = app.config["DEBUG"]
port = app.config["PORT"]
host = "0.0.0.0"
if debug == False:
    certfile = app.config["SSL_CERT_PATH"]
    keyfile = app.config["SSL_PRIVATE_KEY_PATH"]
    socketio.run(app, host = host, port = port, debug = debug, certfile = certfile, keyfile = keyfile)
else:
    socketio.run(app, host = host, port = port, debug = debug)



call(["fuser", "-k", f"{port}/tcp"])
