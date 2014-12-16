import logging
from lilac.server import lilacWebServer
import os.path

from lilac import db

db.setup('localhost', 'test', 'test', 'lilac', pool_opt={'minconn': 3, 'maxconn': 10})


def run(host='localhost', port=80, use_gevent=False, debug=False):
    setdebug(debug)
    lilacWebServer(host=host,
                port=port, use_gevent=use_gevent, 
                mako_cache_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache'),
                debug=debug).serve_forever()


def setdebug(debug=False):

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

if __name__ == '__main__':
    run(debug=True)