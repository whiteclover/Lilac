#!/usr/bin/env python

import re
from solo.template import render_template
from solo.web.util import jsonify
from solo.util import json_encode, json_decode
from webob import exc 
from lilac.controller import ADMIN, LOGGER
from lilac.orm  import Backend
from lilac.tool import access
from lilac.model import Task
from lilac.paginator import Paginator



TASK_STATUS_LIST = ('all', 'scheduled',  'running', 'new',  'rerty', 'completed', 'stop', 'aborted')

TASK_STATUSES = {
    'all': 0,
    'new': Task.NEW,
    'scheduled': Task.SCHEDULED,
    'rerty': Task.RETRY,
    'running': Task.RUNNING,
    'completed': Task.COMPLETED,
    'stop': Task.STOP,
    'aborted': Task.ABORTED
}

TASK_KEY_STATUSES = {}
for k, v in TASK_STATUSES.items():
    TASK_KEY_STATUSES[str(v)] = k


def task_menu(m):

    ctl = TaskController()
    
    # Task api
    m.connect('task_page', '/task/status/:status', controller=ctl, action='index', conditions=dict(method=["GET"]))
    m.connect('task_all', '/task', controller=ctl, action='index', conditions=dict(method=["GET"]))
    m.connect('add_task_page', '/task/add', controller=ctl, action='add_page', conditions=dict(method=["GET"]))
    m.connect('add_task', '/task/add', controller=ctl, action='add', conditions=dict(method=["POST"]))
    m.connect('edit_task_page', '/task/:name/edit', controller=ctl, action='edit_page', conditions=dict(method=["GET"]))
    m.connect('edit_task', '/task/:name/edit', controller=ctl, action='edit', conditions=dict(method=["POST"]))
    m.connect('delete_task', '/task/:name/delete', controller=ctl, action='delete', conditions=dict(method=["POST"]))



class TaskController(object):

    @access()
    def index(self, status='all', name='', page=1):

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
    def add_page(self):
        return render_template('task.add.html')

    @jsonify
    @access(ADMIN)
    def add(self, name, action, data, event, status='new'):
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
    def edit_page(self, name):
        task = Backend('task').find(name)
        if not task:
            raise exc.HTTPNotFound('Not found')

        if not task.data:
            task.data = ''
        else:
            task.data = json_encode(task.data)
        return render_template('task.edit.html', task=task, statuses=TASK_STATUSES)

    @jsonify
    @access(ADMIN)
    def edit(self,  name, action, data, event, status):
        try:
            action, data, status = self.process_task_args(action, data, status)
        except TypeError as e:
            return {'msg': str(e), 'status': 'error'}

        task = Backend('task').find(name)
        if not task:
            raise  exc.HTTPNotFound('Not found')

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
    def delete(self, name):
        task = Backend('task').find(name)
        if not task:
            return {'status': 'error', 'msg': 'Doesn\'t exist  the task'}

        if not task.is_running():
            Backend('task').delete(task)
            return {'status': 'redirect', 'msg': 'deleted, wait to redirect to /task', 'url': '/task'}
        else:
            return {'status': 'error', 'msg': 'The task is runnig'}

