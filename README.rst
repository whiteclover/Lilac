Lilac
########


Currently, Lilac is A Distributed Scheduler Task System.

Supports
===========

#. Distributed scheduler, You can run many schedulers (Yes! it can on diffrent servers) at same time.
#. Multi-threaded task execution (Leader/Follower variant)
#. Scheduled event at a certain time or periodic execution like a crontab
#. Attempting tasks that fail
#. A thread-safe DB Api, and supports master/slave mode 
#. Take advantage of data-mapper pattern
#. A Web Management Tool (Built in MVC pattern writen by mako gevent cherrypy)

.. image:: https://github.com/thomashuang/lilac/blob/master/docs/img/task.png



What will be in future
=======================

#. Add mongodb supports  for scheduler task backend
#. Improve web tool 
#. Add Loop Until event for task
#. Add Queued task supports (Maybe zeromq or rabbitmq backend)


Requirement
===========

The modules are required to run solo as below:

#. `solo <https://github.com/thomashuang/solo>`_
#. `db <https://github.com/thomashuang/dbpy>`_


How to install
==============

Firstly download or fetch it form github then run the command in shell:

.. code-block:: bash

    cd lilac # the path to the project
    python setup.py install


Compatibility
=============

Built and tested under Python 2.7 


Development
===========

Fork or download it, then run:

.. code-block:: bash 

    cd lilac # the path to the project
    python setup.py develop


Setup Database
==============

* create database in mysql:
* then run the mysql schema.sql script in the project directoy schema:

.. code-block:: bash

    mysql -u yourusername -p yourpassword yourdatabase < schema.sql


if your database has not been created yet, log into your mysql first using:

.. code-block:: bash

    mysql -u yourusername -p yourpassword yourdatabase
    mysql>CREATE DATABASE a_new_database_name
    # = you can =
    mysql> USE a_new_database_name
    mysql> source schema.sql


How to use
==========

Set and Run Web Manager
-------------------------

.. code-block:: python 

    import logging
    from lilac.server import LilacWebServer
    import os.path

    import db

    db.setup({ 'host': 'localhost', 'user': 'test', 'passwd': 'test', 'db': 'lilac'})

    def run(host='localhost', port=8080, debug=False):
        setdebug(debug)
        LilacWebServer(host=host,
                    port=port,
                    mako_cache_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache'),
                    debug=debug).serve_forever()


    def setdebug(debug=False):

        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=level,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

    if __name__ == '__main__':
        run(debug=True)


when firstly run the web tool, please use the root account:

:username: lilac 
:password: lilac

then login the web tool and change your root password.

.. note:: 


    if you wanna use gevent, please install ``gevent`` firstly, then set ``use_gevent`` to ``True``

Set up scheduler
-------------------


Here Is A Demo :

.. code-block:: python

    import db
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
        db.setup({ 'host': 'localhost', 'user': 'test', 'passwd': 'test', 'db': 'lilac'})
         
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

Event
=======

When you add job to scheduler, you see a event arugement. it is a specfic when to run task. Current event supports three types:

at
----

this event will only run once, in a future datetime, it should at least 1 minute speed from now: the pattern as below::

    at %Y%m%d%H%M

every
-----

this event will run in loop by minute(s), the pattern is a  unsiged integer::

    every minute(s)

cron
-----

this event pattern is pattern of crontab, current supports::

      field          allowed values
      -----          --------------
      minute         0-59
      hour           0-23
      day of month   1-31
      month          1-12 
      day of week    0-7 

and the every sub pattern only support below regex expression format::

    ^(\d+-\d+/\d+)|(\d+-\d+)|(\d+)$

LICENSE
=======

    Copyright (C) 2014-2015 Thomas Huang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

