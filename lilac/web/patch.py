#!/usr/bin/env python

import cherrypy
from cherrypy import _cprequest
from cherrypy.lib import httputil
import sys
import logging
from cherrypy.process import servers


LOGGER = logging.getLogger('web.patch')


try:
    from greenlet import getcurrent as get_ident
except ImportError:
    LOGGER.ERROR('You shall install Gevent, if wanna use gevent wsgi server')
    exit(1)


def patch_cherrypy():
    cherrypy.serving = GreenletServing()


class GreenletServing(object):
    __slots__ = ('__local__', )

    def __init__(self):
        object.__setattr__(self, '__local__', {})
        ident = get_ident()
        self.__local__[ident] = {
            'request': _cprequest.Request(httputil.Host("127.0.0.1", 80), httputil.Host("127.0.0.1", 1111)),
            'response': _cprequest.Response()
        }

    def load(self, request, response):
        self.__local__[get_ident()] = {
            'request': request,
            'response': response
        }

    def __getattr__(self, name):
        try:
            return self.__local__[get_ident()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = get_ident()
        local = self.__local__
        try:
            local[ident][name] = value
        except KeyError:
            local[ident] = {name: value}

    def clear(self):
        """Clear all attributes of the current greenlet."""
        del self.__local__[get_ident()]