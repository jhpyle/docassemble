import importlib
import socket
from celery import Celery
from docassemble.webapp.config import daconfig

def get_celery_app():
    backend = daconfig.get('redis', None)
    if backend is None:
        backend = 'redis://localhost'
    broker = daconfig.get('rabbitmq', None)
    if broker is None:
        broker = f'pyamqp://guest@{socket.gethostname()}//'

    workerapp = Celery('docassemble.webapp.worker', backend=backend, broker=broker)
    importlib.import_module('docassemble.webapp.config_worker')
    workerapp.config_from_object('docassemble.webapp.config_worker')
    workerapp.set_current()
    workerapp.set_default()
    return workerapp
