#!/usr/bin/env python

import cherrypy
import sys
import logging
from cherrypy.process import servers

LOGGER = logging.getLogger('web.server')

class GeventWSGIServer(object):

    """Adapter for a gevent.wsgi.WSGIServer."""

    def __init__(self, *args, **kwargs):
        from lilac.web.patch import patch_cherrypy

        patch_cherrypy()
        self.args = args
        self.kwargs = kwargs
        self.ready = False

    def start(self):
        """Start the GeventWSGIServer."""
        # We have to instantiate the server class here because its __init__
        from gevent.wsgi import WSGIServer

        self.ready = True
        LOGGER.debug('Starting Gevent WSGI Server...')
        self.httpd = WSGIServer(*self.args, **self.kwargs)
        self.httpd.serve_forever()

    def stop(self):
        """Stop the HTTP server."""
        LOGGER.debug('Stoping Gevent WSGI Server...')
        self.ready = False
        self.httpd.stop()


class WebServer(object):

    def __init__(self, server_name='Sola', host='127.0.0.1', port=8080, use_gevent=True, debug=False, encoding='UTF-8'):
        self.server_name = server_name
        self.host = host
        self.port = port
        self.debug = debug
        self.encoding = encoding
        self.use_gevent = use_gevent
        self.config = self.gen_config()
        self.bootstrap()

    def bootstrap(self):
        """You can intialize more configs or settings in here"""
        pass

    def gen_config(self):
        conf = {
            'global':
                {
                    'server.socket_host': self.host,
                    'server.socket_port': self.port,
                    'engine.autoreload.on': self.debug,
                    #'log.screen': self.debug,
                    'log.error_file': '',
                    'log.access_file': '',
                    'request.error_response': self.handle_internal_exception,
                    'tools.decode.on': True,
                    "tools.encode.on": True,
                    'tools.encode.encoding': self.encoding,
                    'tools.gzip.on': True,
                    'tools.log_headers.on': False,
                    'request.show_tracebacks': False,
                }
        }
        if self.use_gevent:
            conf['global']['environment'] = 'embedded'

        return conf

    def set_404_pape(self, not_found_handler):
        """Custom not found page"""
        self.config['global']['error_page.404'] = not_found_handler


    def asset(self, path, asset_path):
        """Set servering Static directory"""
        self.config[path] = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': asset_path
        }

    def handle_internal_exception(self):
        """Handle the unknow exception and also throw 5xx status and push message to frontend"""
        cls, e, tb = sys.exc_info()

        LOGGER.exception('Unhandled Error %s', e)
        resp = cherrypy.response
        resp.status = 500
        resp.content_type = 'text/html; charset=UTF-8'

        if cherrypy.request.method != 'HEAD':
            resp.body = ["""<html>
<head><title>Internal Server Error </title></head>
<body><p>An error occurred: <b>%s</b></p></body>
</html> """ % (str(e))]

    def new_route(self):
        return cherrypy.dispatch.RoutesDispatcher()

    def create_app(self):
        raise NotImplemented('Must implement create_app in Subclass')

    def _bootstrap_app(self):
        ctl, routes = self.create_app()
        cherrypy.config.clear()
        config = {'/': {'request.dispatch': routes}, 'global': self.config}
        config.update(self.config)
        cherrypy.config.update(config)
        return cherrypy.tree.mount(ctl, '/', config)

    def serve_forever(self):
        engine = cherrypy.engine
        if hasattr(engine, "signal_handler"):
            engine.signal_handler.subscribe()
        if hasattr(engine, "console_control_handler"):
            engine.console_control_handler.subscribe()
        app = self._bootstrap_app()
        try:
            if self.use_gevent:
                # Turn off autoreload when using *cgi.
                #cherrypy.config.update({'engine.autoreload_on': False})
                addr = cherrypy.server.bind_addr
                cherrypy.server.unsubscribe()
                f = GeventWSGIServer(addr, app, log=None)
                s = servers.ServerAdapter(engine, httpserver=f, bind_addr=addr)
                s.subscribe()
                engine.start()
            else:
                cherrypy.quickstart(app)
        except KeyboardInterrupt:
            self.stop()
        else:
            engine.block()

    def stop(self):
        cherrypy.engine.stop()
