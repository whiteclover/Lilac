 #!/usr/bin/env python
 
import logging
 
LOGGER = logging.getLogger('app')
 
 
class App(object):
 
    def __init__(self):
        self.actions = {}
        self.initialize()
 
    def initialize(self):
        pass
 
    def __call__(self, task):
        try:
            LOGGER.info('Task is :%s', task)
            handler = self.actions.get(task.action)
            if handler:
                handler(*task.data.get('args', ()), **task.data.get('kw', {}))
            else:
                raise AppError('task.action:%s not found' %(task.action))
        except Exception as e:
            raise e
 
    def add_task(self, action, func):
        if action in self.actions:
            raise KeyError('Action:%s is in app' %(action))
        self.actions[action] = func
 
 
class AppError(Exception):
    pass