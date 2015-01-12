import db
from lilac.model import Task, User
from lilac.orm import Backend


import unittest


class TaskMapperTest(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup({ 'host': 'localhost', 'user': 'test', 'passwd': 'test', 'db': 'lilac'})
        self.task = Task(
            None, 'task_id', 'job_test', 'job.test', {'args': (), 'kw': {}}, 'every 5')
        Backend('task').delete_by_name('job_test')
        Backend('task').save(self.task)

    def test_find(self):
        task = Backend('task').find('job_test')
        assert task.name == self.task.name
        assert task.status == self.task.status
        assert task.event == self.task.event
        assert task.attempts == self.task.attempts

        task = Backend('task').find_by_task_id('task_id')[0]
        assert task.name == self.task.name
        assert task.status == self.task.status
        assert task.event == self.task.event
        assert task.attempts == self.task.attempts

        task = Backend('task').find_by_cron_id(task.cron_id)
        assert task.name == self.task.name
        assert task.status == self.task.status
        assert task.event == self.task.event
        assert task.attempts == self.task.attempts

    def test_save(self):
        task = Backend('task').find('job_test')
        task.fresh()
        task.attempts += 1
        task.status = Task.COMPLETED
        Backend('task').save(task)
        task = Backend('task').find('job_test')
        assert task.name == self.task.name
        assert task.event == self.task.event
        assert task.run_times == 1
        assert task.attempts == self.task.attempts + 1
        assert task.status == Task.COMPLETED
        assert task.last_five_logs[0]['status'] == Task.SCHEDULED

    def test_save_after_retry(self):
        task = Backend('task').find('job_test')
        task.retry('msg')
        Backend('task').save(task)
        task = Backend('task').find('job_test')
        assert task.name == self.task.name
        assert task.event == self.task.event
        assert task.run_times == 1
        assert task.attempts == self.task.attempts + 1
        assert task.status == Task.RETRY

    def test_delete(self):
        task = Backend('task').find('job_test')
        ret = Backend('task').delete(task)
        task = Backend('task').find('job_test')
        self.assertEqual(task, None)

    def test_delete_by_name(self):
        task = Backend('task').find('job_test')
        ret = Backend('task').delete_by_name(task.name)
        task = Backend('task').find('job_test')
        self.assertEqual(task, None)

    def test_delete_by_task_id(self):
        task = Backend('task').find('job_test')
        ret = Backend('task').delete_by_task_id(task.task_id)
        task = Backend('task').find('job_test')
        self.assertEqual(task, None)


class UserMapper(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup({ 'host': 'localhost', 'user': 'test', 'passwd': 'test', 'db': 'lilac'})
        self.user = User('username', 'email', 'real_name', 'password', 'actived')
        db.execute('DELETE FROM users WHERE email=%s or email=%s',
                   (self.user.email, 'email2'))
        Backend('user').save(self.user)
        self.uid = db.query('SELECT uid FROM users WHERE email=%s', (self.user.email,))[0][0]

    def test_find(self):
        user = Backend('user').find(self.uid)
        assert user.username == self.user.username
        assert user.status == self.user.status
        assert user.uid == self.uid

        user = Backend('user').find_by_email(self.user.email)
        assert user.username == self.user.username
        assert user.status == self.user.status
        assert user.uid == self.uid

    def test_save(self):
        # on dup
        user = Backend('user').find(self.uid)
        user.status = 'banned'
        Backend('user').save(user)
        user = Backend('user').find(self.uid)
        assert user.status == 'banned'

        # new case
        user = User('username', 'email2', 'real_name', 'password', 'active')
        Backend('user').save(user)
        user = Backend('user').find_by_email(self.user.email)
        assert user is not None

    def test_delete(self):
        self.user.uid = self.uid
        ret = Backend('user').delete(self.user)
        user = Backend('user').find(self.uid)
        self.assertEqual(user, None)


if __name__ == '__main__':

    unittest.main()
