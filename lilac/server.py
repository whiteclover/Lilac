#!/usr/bin/env python
from lilac.web.server import WebServer
from lilac.web.template import render_template
from lilac.model import Task, User
from lilac.data import Backend
from lilac.tool import jsonify, access, set_secure_cookie
from lilac.paginator import Paginator
from lilac.util import json_encode, json_decode

import cherrypy
import re
import logging
import os.path


LOGGER = logging.getLogger('lilac.server')


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

TASK_STATUS_LIST = ('all', 'scheduled',  'runnig', 'new',  'rerty', 'completed', 'stop', 'aborted')

TASK_STATUSES = {
    'all': 0,
    'new': Task.NEW,
    'scheduled': Task.SCHEDULED,
    'rerty': Task.RETRY,
    'runnig': Task.RUNNING,
    'completed': Task.COMPLETED,
    'stop': Task.STOP,
    'aborted': Task.ABORTED
}

TASK_KEY_STATUSES = {}
for k, v in TASK_STATUSES.items():
    TASK_KEY_STATUSES[str(v)] = k


class lilacController(object):

    def index(self):
        return render_template('index.html')

    @jsonify
    def userinfo(self):
        return cherrypy.request.user

    def login_page(self):
        if cherrypy.request.user.uid != 0:
            raise cherrypy.HTTPRedirect('/task')
        return render_template('login.html')

    def login(self, username='', password=''):
        username = username.strip()
        password = password.strip()
        user = Backend('user').find_by_username(username)
        if user and user.check(password):
            set_secure_cookie('auth', str(user.uid))
            raise cherrypy.HTTPRedirect('/task')
        return render_template('login.html')

    def logout(self):
        if cherrypy.request.user.uid != 0:
            req_cookie = cherrypy.request.cookie
            # Response cookie that overwrites the old one and expires
            res_cookie = cherrypy.response.cookie
            for name in req_cookie.keys():
                res_cookie[name] = name
                res_cookie[name]['path'] = '/'
                res_cookie[name]['max-age'] = 0  # or: res_cookie[name]['expires'] = 0

        raise cherrypy.HTTPRedirect('/login')

    @access()
    def user_index(self, page=1):
        user = cherrypy.request.user
        if user.role != 'root':
            raise cherrypy.HTTPRedirect('/user/%d/edit' % (user.uid))

        page = int(page)
        users = Backend('user').paginate(page, 10)
        return render_template('user.index.html', users=users)

    @access(ROOT)
    def add_user_page(self):
        return render_template('user.add.html', statuses=USER_STATUSES, roles=ROLES)

    @jsonify
    @access(ROOT)
    def add_user(self, username, email, real_name, password, status='', role='user'):
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
    def edit_user_page(self, uid):
        uid = int(uid)
        user = Backend('user').find(uid)
        if not user:
            raise cherrypy.HTTPError(404, 'user not found')
        return render_template('user.edit.html', statuses=USER_STATUSES, roles=ROLES, user=user)

    @jsonify
    @access()
    def edit_user(self, uid, email, real_name, password, newpass1, newpass2, status, role='user'):
        real_name, newpass1, newpass2 = real_name.strip(), newpass1.strip(), newpass2.strip()

        uid = int(uid)
        user = Backend('user').find(uid)
        if not user:
            raise cherrypy.HTTPError(404, 'user not found')

        me = cherrypy.request.user
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
        

    @access()
    def task_page(self, status='all', name='', page=1):

        # process page , keep it within range(1, 2000)
        try:
            page = int(page)
        except TypeError:
            page = 1
        if page > 2000:
            page = 2000

        _status = TASK_STATUSES.get(status, 0)
        name = name.strip()
        tasks = Backend('task').take(name, _status, page)
        count = Backend('task').count(name, _status)
        glue = '?page=' if not name else '?name=%s&page=' % (name)
        tasks = Paginator(tasks, count, page, 20, '/task/status/%s' % (status), glue)
        return render_template('task.index.html', name=name, status=status, 
            statuses=TASK_STATUS_LIST, key_statuses=TASK_KEY_STATUSES, tasks=tasks)

    @access(ADMIN)
    def add_task_page(self):
        return render_template('task.add.html')

    @jsonify
    @access(ADMIN)
    def add_task(self, name, action, data, event, status='new'):
        name, action, data, event = name.strip(), action.strip(), data.strip(), event.strip()
        if name and Backend('task').find(name):
            return {'status': 'error', 'msg': 'Exist the task'}
        try:
            action, data, status = self.process_task_args(action, data, status)
            task = Task(None, None, name, action, data, event)
            if Backend('task').save(task):
                return {'status': 'success', 'msg': 'created'}
        except TypeError as e:
            return {'status': 'error', 'msg': str(e)}

    @access(ADMIN)
    def edit_task_page(self, name):
        task = Backend('task').find(name)
        if not task:
            raise cherrypy.HTTPError(404, 'nof found')

        if not task.data:
            task.data = ''
        else:
            task.data = json_encode(task.data)
        return render_template('task.edit.html', task=task, statuses=TASK_STATUSES)

    @jsonify
    @access(ADMIN)
    def edit_task(self,  name, action, data, event, status):
        try:
            action, data, status = self.process_task_args(action, data, status)
        except TypeError as e:
            return {'msg': str(e), 'status': 'error'}

        task = Backend('task').find(name)
        if not task:
            raise cherrypy.HTTPError(404, 'nof found')

        if not task.is_running():
            task.action = action
            task.status = status
            try:
                task.event = event
            except:
                return {'msg': 'event invalid', 'status': 'error'}
            Backend('task').save(task)
            return {'status': 'info', 'msg': 'saved', }
        else:
            return {'status': 'error', 'msg': 'The task is runnig'}

    def process_task_args(self, action, data, status):
        if not re.match(r'[A-Za-z0-9_.]{4,100}', action):
            raise TypeError('action:%s invalid, must be [A-Za-z0-9_.]{4,100}' % (action))
        try:
            data = json_decode(data)
        except:
            raise TypeError('invalid json data')

        if status not in TASK_STATUSES:
            raise TypeError('invalid status')

        status = TASK_STATUSES[status]
        return action, data, status

    @jsonify
    @access(ADMIN)
    def delete_task(self, name):
        task = Backend('task').find(name)
        if not task:
            return {'status': 'error', 'msg': 'Doesn\'t exist  the task'}

        if not task.is_running():
            Backend('task').delete(task)
            return {'status': 'redirect', 'msg': 'deleted, wait to redirect to /task', 'url': '/task'}
        else:
            return {'status': 'error', 'msg': 'The task is runnig'}

    def _404_page(self, *args, **kw):
        return render_template('404.html')


class lilacWebServer(WebServer):

    def __init__(self, host='127.0.0.1', port=8080, mako_cache_dir=None, 
        cookie_secret='7oGwHH8NQDKn9hL12Gak9G/MEjZZYk4PsAxqKU4cJoY=',
        use_gevent=True, debug=False, ):
        if not mako_cache_dir:
            raise TypeError('You must set cache directory for mako')
        self.cookie_secret = cookie_secret
        self.mako_cache_dir = mako_cache_dir
        WebServer.__init__(self, 'lilac', host, port, use_gevent, debug)

    def bootstrap(self):
        self.bootstrap_template()
        self.booststrap_db()
        self.bootstrap_tools()

        from lilac import tool 
        tool.COOKIE_SECRET = self.cookie_secret

    def bootstrap_template(self):
        from lilac.web.template import setup_template, template_vars

        template_vars['json_encode'] = json_encode

        path = os.path.dirname(__file__)
        setup_template([
            os.path.join(path, 'views/'),
            os.path.join(path, 'views/layouts/')],
            module_cache_dir=self.mako_cache_dir)

        # Mount static files
        self.asset('/assets', os.path.join(os.path.dirname(__file__), 'assets'))

    def booststrap_db(self):
        pass
        # from lilac import db
        # db.setup('localhost', 'test', 'test', 'lilac', pool_opt={'minconn': 3, 'maxconn': 10})

    def bootstrap_tools(self):

        # Enable user session tool hooks
        self.config['global']['tools.init_user.on'] = True
        self.config['global']['tools.clear_user.on'] = True

    def create_app(self):
        ctl = lilacController()
        m = self.new_route()
        m.mapper.explicit = False

        # Custom 404 Page
        self.set_404_pape(ctl._404_page)

        m.connect('index', '/', controller=ctl, action='index')
        m.connect('userinfo', '/userinfo', controller=ctl, action='userinfo')
        m.connect('login_page', '/login', controller=ctl, action='login_page', conditions=dict(method=["GET"]))
        m.connect('login', '/login', controller=ctl, action='login', conditions=dict(method=["POST"]))
        m.connect('logout', '/logout', controller=ctl, action='logout')

        # User Api
        m.connect('task_page', '/task/status/:status', controller=ctl, action='task_page')
        m.connect('task_all', '/task', controller=ctl, action='task_page')
        m.connect('add_task_page', '/task/add', controller=ctl, action='add_task_page', conditions=dict(method=["GET"]))
        m.connect('add_task', '/task/add', controller=ctl, action='add_task', conditions=dict(method=["POST"]))
        m.connect('edit_task_page', '/task/:name/edit', controller=ctl, action='edit_task_page', conditions=dict(method=["GET"]))
        m.connect('edit_task', '/task/:name/edit', controller=ctl, action='edit_task', conditions=dict(method=["POST"]))
        m.connect('delete_task', '/task/:name/delete', controller=ctl, action='delete_task', conditions=dict(method=["POST"]))

        # Task Api
        m.connect('add_user_page', '/user/add', controller=ctl, action='add_user_page', conditions=dict(method=["GET"]))
        m.connect('add_user', '/user/add', controller=ctl, action='add_user', conditions=dict(method=["POST"]))
        m.connect('user_index', '/user', controller=ctl, action='user_index')
        m.connect('edit_user_page', '/user/:uid/edit', controller=ctl, action='edit_user_page', conditions=dict(method=["GET"]))
        m.connect('edit_user', '/user/:uid/edit', controller=ctl, action='edit_user', conditions=dict(method=["POST"]))
        return ctl, m
