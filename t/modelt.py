

from lilac.model import _CrontabPattern, _ParsedSpec, Task, User
from datetime import datetime, timedelta
import unittest

class TaskTest(unittest.TestCase):

    def test_new(self):
        task = Task(1, 'task_id', 'name', 'job.test', {'args':(), 'kw':{}}, 'every 5')
        self.assertEquals((task.name, task.event), ('name', 'every 5'))
        self.assertEquals(task.pattern, ['every', '5'])

        self.assertRaises(TypeError, lambda: task(1, 'task_id', 'name', 'every'))
        self.assertRaises(TypeError, lambda: task(1, 'task_id', 'name', 'every x'))
        self.assertRaises(TypeError, lambda: task(1, 'task_id', 'name', 'at xx'))

    def test_gen_next_run(self):
        task = Task(1, 'task_id', 'name', 'job.test',  {'args':(), 'kw':{}}, 'every 5', datetime.strptime("8/8/2014 16:35", "%d/%m/%Y %H:%M"), 
            datetime.strptime("8/8/2014 16:30", "%d/%m/%Y %H:%M"))
        self.assertEqual(task.next_run, datetime.strptime("8/8/2014 16:35", "%d/%m/%Y %H:%M"))
        self.assertTrue(task.gen_next_run() > datetime.strptime("8/8/2014 16:35", "%d/%m/%Y %H:%M"))

    def test_is_running(self):
        task = Task(1, 'task_id', 'name', 'job.test',  {'args':(), 'kw':{}}, 'every 5', datetime.strptime("8/8/2014 16:35", "%d/%m/%Y %H:%M"), 
            datetime.strptime("8/8/2014 16:30", "%d/%m/%Y %H:%M")) 
        self.assertEqual(task.is_running(), False)


    def test_fresh(self):
        task = Task(1, 'task_id', 'name', 'job.test', {'args':(), 'kw':{}}, 'every 5')
        res = task.fresh()
        assert res == True
        assert task.task_id is None
        assert task.status == Task.SCHEDULED
        assert task.run_times == 1

        task = Task(1, 'task_id', 'name', 'job.test', {'args':(), 'kw':{}}, 'every 5')
        task.event = 'at 20141111 1212'
        res = task.fresh()
        assert res == False

    def test_retry(self):
        task = Task(1, 'task_id', 'name', 'job.test', {'args':(), 'kw':{}}, 'every 5')
        res = task.retry()
        assert res == True
        assert task.attempts == 1
        assert task.status == Task.RETRY

        task = Task(1, 'task_id', 'name', 'job.test', {'args':(), 'kw':{}}, 'every 5')
        task.attempts = 4
        res = task.retry()
        assert res == False
        assert task.status == Task.ABORTED
        assert task.run_times == 1

    def test_event_type(self):
        t = datetime.now() + timedelta(minutes=5)
        task = Task(1, 'task_id', 'name', 'job.test',  {'args':(), 'kw':{}}, 'at ' + t.strftime('%Y%m%d%H%M'))
        self.assertEqual(task.event_type, 'at')
        task.event = 'every 5'
        self.assertEqual(task.event_type, 'every')


class _CrontabPatternTest(unittest.TestCase):

    def setUp(self):
        self.pat = _CrontabPattern()

    def test_validate(self):
        self.assertTrue(self.pat.validate('7 0-23 1-32 1-12 0-7'))
        self.assertTrue(self.pat.validate('0-59/2 0-23 1-32 1-12 0-7'))
        self.assertFalse(self.pat.validate('0-23 1-32 1-12 0-7'))
        self.assertFalse(self.pat.validate('*7xx 0-23 1-32 1-12 0-7'))

    def test_parse(self):
        self.assertEqual(self.pat.parse('0-59/2 0-23 1-32 1-12 0-7'), _ParsedSpec(minute=set([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58]), hour=set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]), dom=set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]), month=set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]), dow=set([0, 1, 2, 3, 4, 5, 6, 7])))
        self.assertEqual(self.pat.parse('7 0-23 1-32 1-12 0-7'), _ParsedSpec(minute=set([7]), hour=set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]), dom=set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]), month=set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]), dow=set([0, 1, 2, 3, 4, 5, 6, 7])))
     
    def test_gen_next_run(self):
        gens =  [datetime(2012, 4, 29),
             datetime(2012, 4, 29, 0, 0), 
             datetime(2012, 4, 29, 0, 7),
             datetime(2012, 4, 29, 0, 14),
             datetime(2012, 4, 29, 0, 21), 
             datetime(2012, 4, 29, 0, 28), 
             datetime(2012, 4, 29, 0, 35),
             datetime(2012, 4, 29, 0, 42), 
             datetime(2012, 4, 29, 0, 49),
             datetime(2012, 4, 29, 0, 56), 
             datetime(2012, 4, 29, 1, 0)
        ]
        for i, gen in enumerate(gens[0:10]):
            self.assertEqual(self.pat.gen_next_run('*/7 * * * *', gen), gens[i])


class UserTest(unittest.TestCase):

    def setUp(self):
        self.new_user = User('username', 'email', 'real_name', 'password', 'status')
        self.db_user = User('username', 'email', 'real_name',
                                  'd63dc919e201d7bc4c825630d2cf25fdc93d4b2f0d46706d29038d01', 'status', uid=1)

    def test_secure_passwod(self):
        self.assertEqual(self.new_user.secure_password('password'),
                         'd63dc919e201d7bc4c825630d2cf25fdc93d4b2f0d46706d29038d01')

    def test_check(self):
        self.assertTrue(self.new_user.check('password'))
        self.assertTrue(self.db_user.check('password'))

if __name__ == '__main__':
    unittest.main()