# -*- coding: utf-8 -*-

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from expire_matches import expire_matches
class Config(object):
    JOBS = [
        #{
        #    'id': 'expire_matches_job',
        #    'func': expire_matches,
        #    'replace_existing': True,
        #    'trigger': 'interval',
        #    'seconds': 10
        #}
    ]

    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///flask_context.db')
    }

    SCHEDULER_API_ENABLED = True
