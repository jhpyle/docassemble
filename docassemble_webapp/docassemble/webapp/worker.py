def null_function(*pargs, **kwargs):
    return
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(in_celery=True)
from docassemble.base.config import daconfig
import docassemble.base.interview_cache
import docassemble.base.parse
from celery import Celery
from celery.result import result_from_tuple
import sys
import socket

class WorkerController(object):
    pass

backend = daconfig.get('redis', None)
if backend is None:
    backend = 'redis://localhost'
broker = daconfig.get('rabbitmq', None)
if broker is None:
    broker = 'pyamqp://guest@' + socket.gethostname() + '//'

workerapp = Celery('docassemble.webapp.worker', backend=backend, broker=broker)
workerapp.conf.update(
    task_serializer='pickle',
    accept_content=['pickle'],
    result_serializer='pickle',
    timezone=daconfig.get('timezone', 'America/New_York'),
    enable_utc=True,
)

worker_controller = None

def initialize_db():
    global worker_controller
    worker_controller = WorkerController()
    from docassemble.webapp.server import set_request_active, fetch_user_dict, save_user_dict, obtain_lock, release_lock
    from docassemble.webapp.server import app as flaskapp
    worker_controller.flaskapp = flaskapp
    worker_controller.set_request_active = set_request_active
    worker_controller.fetch_user_dict = fetch_user_dict
    worker_controller.save_user_dict = save_user_dict
    worker_controller.obtain_lock = obtain_lock
    worker_controller.release_lock = release_lock

def convert(obj):
    return result_from_tuple(obj.as_tuple(), app=workerapp)

@workerapp.task
def background_action(yaml_filename, user_info, session_code, secret, url, url_root, action):
    if worker_controller is None:
        initialize_db()
    with worker_controller.flaskapp.app_context():
        sys.stderr.write("background_action: action is " + str(action) + " and yaml_filename is " + str(yaml_filename) + " and session code is " + str(session_code) + "\n")
        worker_controller.set_request_active(False)
        interview = docassemble.base.interview_cache.get_interview(yaml_filename)
        interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, action=action['action'], interface='worker', arguments=action['arguments']))
        steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
        try:
            interview.assemble(user_dict, interview_status)
        except:
            pass
        if interview_status.question.question_type in ["restart", "exit"]:
            reset_user_dict(session_code, yaml_filename)
            release_lock(session_code, yaml_filename)
        if interview_status.question.question_type == "response":
            if not hasattr(interview_status.question, 'binaryresponse'):
                sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
        if interview_status.question.question_type == "backgroundresponse":
            return(interview_status.question.backgroundresponse)
        if interview_status.question.question_type == "backgroundresponseaction":
            new_action = interview_status.question.action
            interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, interface='worker', action=new_action['action'], arguments=new_action['arguments']))
            worker_controller.obtain_lock(session_code, yaml_filename)
            steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
            try:
                interview.assemble(user_dict, interview_status)
            except:
                pass
            worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, manual_user_id=user_info['theid'])
            worker_controller.release_lock(session_code, yaml_filename)
            return(new_action)
        return(None)
