#!/usr/bin/env python

import re
from lilac.controller import ADMIN, LOGGER
from lilac.orm  import Backend
from lilac.tool import access, set_secure_cookie
from lilac.model import User

from solo.template import render_template
from solo.web.util import jsonify
from solo.web import ctx
from webob import exc
from lilac.paginator import Paginator

USER_STATUSES = {
    'actived': 'actived',
    'banned': 'banned',
}

USER = 'user'
ROOT = 'root'
ADMIN = 'administrator'
ROLES = {
    # 'root' : 'root',
    'administrator': 'administrator',
    'user': 'user'
}



def user_menu(m):
    
    ctl = UserController()
    
    # User Api

    m.connect('userinfo', '/userinfo', controller=ctl, action='userinfo')
    m.connect('login_page', '/login', controller=ctl, action='login_page', conditions=dict(method=["GET"]))
    m.connect('login', '/login', controller=ctl, action='login', conditions=dict(method=["POST"]))
    m.connect('logout', '/logout', controller=ctl, action='logout')

    m.connect('add_user_page', '/user/add', controller=ctl, action='add_page', conditions=dict(method=["GET"]))
    m.connect('add_user', '/user/add', controller=ctl, action='add', conditions=dict(method=["POST"]))
    m.connect('user_index', '/user', controller=ctl, action='index', conditions=dict(method=["GET"]))
    m.connect('edit_user_page', '/user/:uid/edit', controller=ctl, action='edit_page', conditions=dict(method=["GET"]))
    m.connect('edit_user', '/user/:uid/edit', controller=ctl, action='edit', conditions=dict(method=["POST"]))


class UserController(object):

    @access()
    def index(self, page=1):
        user = ctx.request.user
        if user.role != 'root':
            raise exc.HTTPFound(location='/user/%d/edit' % (user.uid))

        page = int(page)
        users = Backend('user').paginate(page, 10)
        return render_template('user.index.html', users=users)

    @jsonify
    def userinfo(self):
        return ctx.request.user

    def login_page(self):
        if ctx.request.user.uid != 0:
            raise exc.HTTPFound('/task')
        return render_template('login.html')

    def login(self, username='', password=''):
        LOGGER.error('username=%s', username)
        username = username.strip()
        password = password.strip()
        user = Backend('user').find_by_username(username)
        if user and user.check(password):
            set_secure_cookie('auth', str(user.uid))
            LOGGER.info('success')
            raise exc.HTTPFound(location='/task')
        return render_template('login.html')

    def logout(self):
        if ctx.request.user.uid != 0:
            ctx.response.delete_cookie('auth')

        raise exc.HTTPFound(location='/login')

    @access(ROOT)
    def add_page(self):
        return render_template('user.add.html', statuses=USER_STATUSES, roles=ROLES)

    @jsonify
    @access(ROOT)
    def add(self, username, email, real_name, password, status='', role='user'):
        username, real_name = username.strip(), real_name.strip()
        if not re.match(r'^[A-Za-z0-9_]{4,16}$', username):
            return {'status' : 'error', 'msg' : 'user name: %s must be the ^[A-Za-z0-9_]{4,16}$ pattern' %(username)}

        if not re.match(r'^[A-Za-z0-9_ ]{4,16}$', real_name):
            return {'status' : 'error', 'msg' : 'real name: %s must be the [A-Za-z0-9_]{4,16} pattern' %(real_name)}

        if not re.match(r'^[A-Za-z0-9@#$%^&+=]{4,16}$', password):
            return {'status' : 'error', 'msg' : 'password: %s must be the ^[A-Za-z0-9@#$%^&+=]{4,16}$ pattern' %(password)}

        if status not in USER_STATUSES:
            status = 'actived'

        if role not in ROLES:
            role = 'user'

        if len(email) > 7 and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email):
            if Backend('user').find_by_email(email):
                return {'status' : 'error', 'msg' : 'email:%s is used' %(email)}

        if Backend('user').find_by_username(username):
            return {'status' : 'error', 'msg' : 'user name:%s is used' %(username)}

        user = User(username, email, real_name, password, status, role)
        Backend('user').save(user)
        return  {'status' : 'info', 'msg' : 'saved'}

    @access()
    def edit_page(self, uid):
        uid = int(uid)
        user = Backend('user').find(uid)
        if not user:
            raise exc.HTTPNotFound('Not Found')
        return render_template('user.edit.html', statuses=USER_STATUSES, roles=ROLES, user=user)

    @jsonify
    @access()
    def edit(self, uid, email, real_name, password, newpass1, newpass2, status, role='user'):
        real_name, newpass1, newpass2 = real_name.strip(), newpass1.strip(), newpass2.strip()

        uid = int(uid)
        user = Backend('user').find(uid)
        if not user:
            raise exc.HTTPNotFound('user not found')

        me = ctx.request.user
        if me.uid == user.uid:
            if re.match(r'[A-Za-z0-9@#$%^&+=]{4,16}', newpass1):
                if password and newpass1 and newpass1 == newpass2:
                    user.password = newpass1
            elif newpass1:
                return {'status' : 'error', 'msg' : 'password: %s must be the [A-Za-z0-9_]{4,16} pattern' %(newpass1)}

            if len(email) > 7 and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email):
                user_ = Backend('user').find_by_email(email)
                if user_ and user_.uid != user.uid:
                    return {'status' : 'error', 'msg' : 'email:%s is used' %(email)}
                else:
                    user.email = email


        if me.uid == 1 and user.uid != 1:
            if role in (ADMIN, USER):
                user.role = role
            if user.status != status and status in USER_STATUSES:
                user.status = status

        if re.match(r'^[A-Za-z0-9_ ]{4,16}$', real_name):
            if user.real_name != real_name:
                user.real_name = real_name

        Backend('user').save(user)
        return  {'status' : 'info', 'msg' : 'updated'}
        
		
