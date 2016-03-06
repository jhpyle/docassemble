from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from celery import Celery

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379',
#     CELERY_RESULT_BACKEND='redis://localhost:6379'
# )

db = SQLAlchemy(app)

# def make_celery(app):
#     celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery

# celery = make_celery(app)

# @celery.task()
# def async_mailer(mail, message):
#     mail.send(message)
