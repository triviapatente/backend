# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from subprocess import call

#se lo script non è stato chiamato con la flag che forza l'avvio impedendo l'inizializzazione
if len(sys.argv) >= 2 and sys.argv[1] == "-update":
    #esegui lo script di inizializzazione dell'app (che installa anche le dipendenze)
    call(["sudo", "sh", "scripts/dependencies.sh"])


import tp
tp.init()

from tp import app, socketio

debug = app.config["DEBUG"]
port = app.config["PORT"]
context = None
if debug == False:
    from OpenSSL import SSL
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_privatekey_file('/etc/ssl/tp_certs/www.triviapatente.it_private_key.key')
    context.use_certificate_file('/etc/ssl/tp_certs/www.triviapatente.it_ssl_certificate.cer')

print 'Running the service..'
socketio.run(app, host = '0.0.0.0', port = port, debug = debug, ssl_context=context)

call(["fuser", "-k", "%d/tcp" % port])
