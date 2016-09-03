from celery import Celery
import docassemble.base.config
from docassemble.base.config import daconfig
if not docassemble.base.config.loaded:
    docassemble.base.config.load()
backend = daconfig.get('redis', None)
if backend is None:
    backend = 'redis://localhost'
broker = daconfig.get('rabbitmq', None)
if broker is None:
    broker = 'amqp://guest@localhost//'
    
workerapp = Celery('worker', backend=backend, broker=broker)
workerapp.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE=daconfig.get('timezone', 'America/New_York'),
    CELERY_ENABLE_UTC=True
)

@workerapp.task
def add(x, y):
    time.sleep(5)
    return x + y
