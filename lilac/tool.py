#!/usr/bin/env python

from functools import wraps
from cherrypy import request, response, tools, Tool, HTTPRedirect
from hashlib import sha1
import hmac
import logging
import base64
import time
from lilac.data import Backend
from lilac.model import User
from lilac.web.template import render_template

from lilac.util import json_encode

LOGGER = logging.getLogger('lilac.tool')

COOKIE_SECRET  = 'cookie_secret'


__all__ = ['jsonify', 'set_secure_cookie', 'get_secure_cookie']


# An user instance for guest
_guest = User('guest', 'email', 'Guest', 'password', 'actived', 'guest', uid=0)


def access(role=None):
    def decorator(f):
        @wraps(f)
        def _decorator(*args, **kw):
            if request.user == _guest and request.path_info !='/login':
                raise HTTPRedirect('/login')
            user = request.user
            _role = user.role
            if user.is_banned() and (role and _role != 'root'  and  _role != role):
                raise render_template('403.html', role=role, banned=user.is_banned())
            return f(*args, **kw)
        return _decorator
    return decorator


def init_user():
    """Load user if the auth session validates."""
    uid = get_secure_cookie('auth')
    try:
        uid = int(uid)
        user = Backend('user').find(uid)
        if not user:
            user = _guest
    except TypeError:
        user = _guest
    request.user = user



def clear_user():
    """Clear user in current request session"""
    del request.user


tools.init_user = Tool('before_request_body', init_user)
tools.clear_user = Tool('before_finalize', clear_user)


def jsonify(f):
    @wraps(f)
    def _jsonify(*args, **kw):
        data = f(*args, **kw)
        data = json_encode(data)
        response.headers['Content-Type'] = 'application/json'
        return data
    return _jsonify


def set_secure_cookie(name, value, max_age_days=30, **kwargs):
    cookie = response.cookie
    cookie[name] = create_signed_value(name, value)
    cookie[name]['path'] = '/'
    cookie[name]['max-age'] = max_age_days * 86400
    for key, value in kwargs.iteritems():
        cookie[name][key] = value


def get_secure_cookie(name, value=None, max_age_days=31):
    if value is None:
        value = request.cookie.get(name)
        if value:
            value = value.value
    return decode_signed_value(COOKIE_SECRET, name, value, max_age_days=max_age_days)


def create_signed_value(name, value):
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = _secert_signature(COOKIE_SECRET, name, value, timestamp)
    value = "|".join([value, timestamp, signature])
    return value


def decode_signed_value(secret, name, value, max_age_days=31):
    if not value:
        return None
    parts = value.split("|")
    if len(parts) != 3:
        return None
    signature = _secert_signature(secret, name, parts[0], parts[1])
    if not _time_independent_equals(parts[2], signature):
        LOGGER.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - max_age_days * 86400:
        LOGGER.warning("Expired cookie %r", value)
        return None
    if timestamp > time.time() + 31 * 86400:
        LOGGER.warning("Cookie timestamp in future; possible tampering %r", value)
        return None
    if parts[1].startswith("0"):
        LOGGER.warning("Tampered cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0])
    except Exception:
        return None


def _secert_signature(secret, *parts):
    hash = hmac.new(secret, digestmod=sha1)
    for part in parts:
        hash.update(part)
    return hash.hexdigest()

if hasattr(hmac, 'compare_digest'):  # python 3.3
    _time_independent_equals = hmac.compare_digest
else:
    def _time_independent_equals(a, b):
        if len(a) != len(b):
            return False
        result = 0
        if isinstance(a[0], int):  # python3 byte strings
            for x, y in zip(a, b):
                result |= x ^ y
        else:  # python2
            for x, y in zip(a, b):
                result |= ord(x) ^ ord(y)
        return result == 0