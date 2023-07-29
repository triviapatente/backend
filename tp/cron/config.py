# -*- coding: utf-8 -*-

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from tp.cron.expire_matches import expire_matches
class Config(object):
    JOBS = [
        {
            'id': 'expire_matches_job',
            'func': expire_matches,
            'replace_existing': True,
            'trigger': 'interval',
            'seconds': 60 * 30
        }
    ]

    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///flask_context.db')
    }

    SCHEDULER_API_ENABLED = True
