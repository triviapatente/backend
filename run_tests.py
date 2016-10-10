import sys

reload(sys)
sys.setdefaultencoding('utf8')

import unittest

#importo i test
from test.pipeline import *

#creiamo le tabelle necessarie al testing
from subprocess import call
call(["sudo", "sh", "scripts/init_test.sh"])


if __name__ == '__main__':
    from app import app
    app.config['TESTING'] = True
    #sostituisco il normale db con quello fittizio
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config["SQLALCHEMY_TEST_DATABASE_URI"]
    unittest.main()
    app.config['TESTING'] = False
