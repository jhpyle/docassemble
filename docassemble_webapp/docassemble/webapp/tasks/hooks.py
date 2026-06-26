from celery import chord as celery_chord
from celery.result import result_from_tuple
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.tasks.app import celery_app

@hookimpl
def get_celery_app():
    return celery_app

@hookimpl
def get_task(obj):
    return result_from_tuple(obj.as_tuple(), app=celery_app)

@hookimpl
def chord(arg):
    return celery_chord(arg)
