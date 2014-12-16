#!/usr/bin/env python
from lilac import db
from lilac.model import Task, User
from lilac.util import json_decode, json_encode
from lilac.paginator import Paginator

from datetime import datetime
import uuid


def gen_task_id():
    return str(uuid.uuid4())

class TaskMapper(object):

    def claim(self, limit, age=None):
        age= age or datetime.now()
        task_id = gen_task_id()
        db.execute('UPDATE cron SET task_id=%s, status=%s WHERE task_id IS NULL and next_run<=%s and status<%s LIMIT %s', 
            (task_id, Task.RUNNING, age, Task.RUNNING, limit))
        tasks = db.query('SELECT * FROM cron WHERE  task_id=%s', (task_id,))
        return [self._load(task) for task in tasks]

    def clear_timeout_task(self, when):
        db.execute('UPDATE cron set task_id=NULL, status=%s WHERE task_id IS NOT NULL AND next_run<%s', (Task.SCHEDULED, when))

    def take(self, name, status=0, page=1, perpage=10):
        select  = 'SELECT * FROM cron'
        where = []
        args = []
        if status:
            args.append(status)
            where.append('status=%s')
        if name:
            args.append(name)
            where.append(' name like %s')

        if where:
            where = ' WHERE ' + ' AND '.join(where)
        else:
            where = ''

        args.extend([perpage, (page - 1) * perpage])
        results = db.query(select + where + ' LIMIT %s OFFSET %s', args)
        return [self._load(task) for task in results]
        
    def count(self, name, status):
        select  = 'SELECT COUNT(cron_id) FROM cron'
        where = []
        args = []
        if status:
            args.append(status)
            where.append('status=%s')
        if name:
            args.append(name)
            where.append(' name like %s')

        if where:
            where = ' WHERE ' + ' AND '.join(where)
        else:
            where = ''
        return db.query(select + where , args)[0][0]

    def find_by_cron_id(self, cron_id):
        res = db.query_one('SELECT * FROM cron WHERE cron_id=%s', (cron_id,))
        if res:
            return self._load(res)

    def find(self, name):
        res = db.query_one('SELECT * FROM cron WHERE name=%s', (name,))
        if res:
            return self._load(res)

    def find_by_task_id(self, task_id):
        results = db.query('SELECT * FROM cron WHERE task_id=%s', (task_id,))
        return [self._load(data) for data in results]

    def _load(self, data):
        data = list(data)
        if data[4] is not None:
            data[4] = json_decode(data[4])
        if data[12] is not None:
            data[12] = json_decode(data[12])

        return Task(*data)

    def save(self, task):
        if task.data is not None:
            data = json_encode(task.data)
        else:
            data = None
        last_five_logs = json_encode(task.last_five_logs)
        if task.cron_id is None:
            return db.execute('INSERT INTO cron(task_id, name, action, data, event, next_run, last_run, run_times, attempts, status, created, last_five_logs) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                              (task.task_id, task.name, task.action, data, task.event, task.next_run, task.last_run, task.run_times, task.attempts, task.status, task.created, last_five_logs))

        return 	db.execute('INSERT INTO cron(task_id, name, action, data, event, next_run, last_run, run_times, attempts, status, created, last_five_logs) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
		 		ON DUPLICATE KEY UPDATE cron_id=VALUES(cron_id), task_id=VALUES(task_id), event=VALUES(event), next_run=VALUES(next_run), \
		 		last_run=VALUES(last_run), action=VALUES(action), data=VALUES(data),run_times=VALUES(run_times), attempts=VALUES(attempts), status=VALUES(status), last_five_logs=VALUES(last_five_logs)',
                           (task.task_id, task.name, task.action, data, task.event, task.next_run, task.last_run, task.run_times, task.attempts, task.status, task.created, last_five_logs))

    def delete(self, task):
        return db.execute('DELETE FROM cron WHERE cron_id=%s', (task.cron_id,))

    def delete_by_name(self, name):
        return db.execute('DELETE FROM cron WHERE name=%s', (name,))

    def delete_by_task_id(self, task_id):
        return db.execute('DELETE FROM cron WHERE task_id=%s', (task_id,))



class UserMapper(object):

    model = User
    SELECT = 'SELECT username, email, real_name, password, status, role, uid, created FROM users '

    def find(self, uid):
        """Find and load the user from database by uid(user id)"""
        data = db.query(self.SELECT + 'WHERE uid=%s', (uid,))
        if data:
            return self._load(data[0])

    def find_by_email(self, email):
        """Return user by email if find in database otherwise None"""
        data = db.query(self.SELECT + 'WHERE email=%s', (email,))
        if data:
            return self._load(data[0])

    def find_by_username(self, username):
        """Return user by username if find in database otherwise None"""
        data = db.query(self.SELECT + 'WHERE username=%s', (username,))
        if data:
            return self._load(data[0])

    def paginate(self, page=1, perpage=10):
        count = self.count()
        results = db.query(self.SELECT + ' ORDER BY created DESC LIMIT %s OFFSET %s', (perpage, (page - 1) * perpage))
        users = [self._load(user) for user in results]
        return Paginator(users, count, page, perpage, '/user')

    def _load(self, data):
        return self.model(*data)

    def save(self, user):
        return db.execute("INSERT INTO users(uid, username, email, real_name, password, status, role, created) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE \
            email=VALUES(email), password=VALUES(password), status=VALUES(status), role=VALUES(role), real_name=VALUES(real_name)",
            (user.uid, user.username, user.email, user.real_name, user.password, user.status, user.role, user.created))

    def count(self):
        return db.query('SELECT COUNT(uid) FROM users')[0][0]

    def delete(self, user):
        return db.execute('DELETE FROM users WHERE uid=%s', (user.uid,))


__backends = {}
__backends['task'] = TaskMapper()
__backends['user'] = UserMapper()

def Backend(name):
    return __backends.get(name)