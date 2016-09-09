def null_function(*pargs, **kwargs):
    return
import docassemble.base.config
if not docassemble.base.config.loaded:
#     set_request_active = null_function
#     fetch_user_dict = null_function
#     save_user_dict = null_function
#     app = None
#     db = None
# else:
    docassemble.base.config.load(in_celery=True)
from docassemble.base.config import daconfig
import docassemble.base.interview_cache
import docassemble.base.parse
from celery import Celery
import sys

class WorkerController(object):
    pass

backend = daconfig.get('redis', None)
if backend is None:
    backend = 'redis://localhost'
broker = daconfig.get('rabbitmq', None)
if broker is None:
    broker = 'amqp://guest@localhost//'
    
workerapp = Celery('docassemble.webapp.worker', backend=backend, broker=broker)
workerapp.conf.update(
    CELERY_TASK_SERIALIZER='pickle',
    CELERY_ACCEPT_CONTENT=['pickle'],
    CELERY_RESULT_SERIALIZER='pickle',
    CELERY_TIMEZONE=daconfig.get('timezone', 'America/New_York'),
    CELERY_ENABLE_UTC=True
)

w = None

def initialize_db():
    global w
    w = WorkerController()
    from docassemble.webapp.server import set_request_active, fetch_user_dict, save_user_dict, obtain_lock, release_lock
    from docassemble.webapp.server import app as flaskapp
    w.flaskapp = flaskapp
    w.set_request_active = set_request_active
    w.fetch_user_dict = fetch_user_dict
    w.save_user_dict = save_user_dict
    w.obtain_lock = obtain_lock
    w.release_lock = release_lock
    #sys.stderr.write("initialized db")

@workerapp.task
def background_action(yaml_filename, user_info, session_code, secret, url, action):
    if w is None:
        initialize_db()
    with w.flaskapp.app_context():
        #sys.stderr.write("Got to background action in worker where action is " + str(action) + " and yaml_filename is " + str(yaml_filename) + " and session code is " + str(session_code) + "\n")
        w.set_request_active(False)
        interview = docassemble.base.interview_cache.get_interview(yaml_filename)
        interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, action=action['action'], arguments=action['arguments'], location=None))
        #sys.stderr.write("Calling fetch_user_dict with " + str(session_code) + " " + str(yaml_filename) + " " + str(secret) + "\n")
        steps, user_dict, is_encrypted = w.fetch_user_dict(session_code, yaml_filename, secret=secret)
        # if 'answer' in user_dict:
        #     sys.stderr.write("Answer currently is " + str(user_dict['answer']) + "\n")
        # else:
        #     sys.stderr.write("Answer not in user_dict\n")
        try:
            interview.assemble(user_dict, interview_status)
            #sys.stderr.write("Assembled ok\n")
        except:
            #sys.stderr.write("Assemble not ok\n")
            pass
        #sys.stderr.write("Status " + str(interview_status.question.content.original_text) + "\n")
        # if 'answer' in user_dict:
        #     sys.stderr.write("Answer now is " + str(user_dict['answer']) + "\n")
        # else:
        #     sys.stderr.write("Answer still not in user_dict\n")
        if interview_status.question.question_type == "backgroundresponse":
            #sys.stderr.write("Got backgroundresponse in worker\n")
            return(interview_status.question.backgroundresponse)
        if interview_status.question.question_type == "backgroundresponseaction":
            #sys.stderr.write("Got backgroundresponseaction in worker\n")
            new_action = interview_status.question.action
            interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, action=new_action['action'], arguments=new_action['arguments'], location=None))
            w.obtain_lock(session_code, yaml_filename)
            steps, user_dict, is_encrypted = w.fetch_user_dict(session_code, yaml_filename, secret=secret)
            try:
                interview.assemble(user_dict, interview_status)
                #sys.stderr.write("Assembled 2 ok\n")
            except:
                #sys.stderr.write("Assembled 2 not ok\n")
                pass
            w.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted)
            w.release_lock(session_code, yaml_filename)
            return(new_action)
        return(None)
