# -*- coding: utf-8 -*-
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
    import __builtin__
    
    __builtin__.TESTING = True

    if len(sys.argv) >= 2 and sys.argv[1] == "-ci":
        __builtin__.CI = True
    from app import app
    app.config['TESTING'] = True
    #sostituisco il normale db con quello fittizio
    unittest.main()
    app.config['TESTING'] = False
