from celery import Celery
import docassemble.base.config
from docassemble.base.config import daconfig
if not docassemble.base.config.loaded:
    docassemble.base.config.load()

workerapp = Celery('worker', backend=daconfig.get('redis', 'redis://localhost'), broker=daconfig.get('rabbitmq', 'amqp://guest@localhost//'))

@workerapp.task
def add(x, y):
    time.sleep(5)
    return x + y
