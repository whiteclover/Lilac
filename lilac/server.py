#!/usr/bin/env python



import re
import logging
import os.path

from solo.web.app import App
from solo.web.server import WebServer
from solo.util import json_encode

LOGGER = logging.getLogger('lilac.server')



class LilacWebServer(object):

    def __init__(self, host='127.0.0.1', port=8080, mako_cache_dir=None, 
        cookie_secret='7oGwHH8NQDKn9hL12Gak9G/MEjZZYk4PsAxqKU4cJoY=', debug=False):
        if not mako_cache_dir:
            raise TypeError('You must set cache directory for mako')
        self.cookie_secret = cookie_secret
        self.mako_cache_dir = mako_cache_dir

        self.host = host
        self.port = port
        self.debug = debug
        self.app = app = App('lilac', debug=debug)

        self.bootstrap()

    def bootstrap(self):
        self.bootstrap_app()
        self.bootstrap_template()
        self.bootstrap_db()
        self.bootstrap_hooks()

        from lilac import tool 
        tool.COOKIE_SECRET = self.cookie_secret

    def bootstrap_app(self):
        m = self.app.route()
        m.mapper.explicit = False

        from lilac.controller.home import HomeController
        from lilac.controller.user import user_menu
        from lilac.controller.task import task_menu

        home = HomeController()

        m.connect('index', '/', controller=home, action='index', conditions=dict(method=["GET"]))
        m.connect('index1', '/index', controller=home, action='index', conditions=dict(method=["GET"]))
        
        # Custom 404 Page
        self.app.error_page(404, home._404_page)

        user_menu(m)
        task_menu(m)



    def bootstrap_template(self):
        from solo.template import setup_template, template_vars

        template_vars['json_encode'] = json_encode

        path = os.path.dirname(__file__)
        setup_template([
            os.path.join(path, 'views/'),
            os.path.join(path, 'views/layouts/')],
            module_cache_dir=self.mako_cache_dir)

        # Mount static files
        self.app.asset('asset', '/assets', os.path.join(os.path.dirname(__file__), 'assets'))

    def bootstrap_db(self):
        pass

    def bootstrap_hooks(self):
        # Enable user session tool hooks
        from lilac.tool import  init_user, clear_user
        self.app.attach('before_handler', init_user)
        self.app.attach('on_end_request', clear_user)

    def serve_forever(self):
        self.httpd = WebServer((self.host, self.port ), self.app, log=self.debug)
        try:
            self.httpd.start()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.httpd.stop()


