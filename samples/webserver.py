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