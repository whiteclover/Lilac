#!/usr/bin/env python

from lilac import db
from datetime import datetime
import urllib2
from lilac.app import App
from lilac.scheduler import Scheduler
import logging 

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    def get_date(url, session='xxx'):
        date = None
        try:
            r = urllib2.urlopen(url)
            date = r.info().dict['date']
        except:
            LOGGER.info('open failed')
        LOGGER.info('session: %s, date:%s,', session, date)
     
    def setdebug(debug=False):
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=level,
                                format='%(asctime)s %(levelname)-8s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')
    setdebug(False)
    db.setup('localhost', 'test', 'test', 'lilac',
        pool_opt={'minconn': 3, 'maxconn': 10})
     
    app = App()
    app.add_task('task.test', get_date)
    scheduler = Scheduler(app, 20, 20, 100)
     
    db.execute('delete from cron')
    for i in range(100):
        if i % 2 == 0:
            print i
            action = 'task.not_found'
        else:
            action = 'task.test'
        scheduler.add_task('name_%d' %(i), 'every 2', action, datetime.now(), 'http://www.google.com', session=i)
    scheduler.run()