import importlib
import socket
import time
import sys
from contextlib import contextmanager
from celery import Celery
from celery.result import result_from_tuple
from docassemble.base.config import daconfig
from docassemble.base.logger import logmessage

backend = daconfig.get('redis', None)
if backend is None:
    backend = 'redis://localhost'
broker = daconfig.get('rabbitmq', None)
if broker is None:
    broker = 'pyamqp://guest@' + socket.gethostname() + '//'

workerapp = Celery('docassemble.webapp.worker', backend=backend, broker=broker)
importlib.import_module('docassemble.webapp.config_worker')
workerapp.config_from_object('docassemble.webapp.config_worker')
workerapp.set_current()
workerapp.set_default()


class WorkerController:

    def __init__(self):
        self.loaded = False

    def initialize(self):
        if self.loaded:
            return
        from docassemble.webapp.server import set_request_active, fetch_user_dict, save_user_dict, obtain_lock, obtain_lock_patiently, release_lock, Message, reset_user_dict, da_send_mail, get_info_from_file_number, retrieve_email, trigger_update, r, apiclient, get_ext_and_mimetype, get_user_object, login_user, error_notification, noquote, update_last_login  # pylint: disable=import-outside-toplevel
        from docassemble.webapp.server import app as flaskapp  # pylint: disable=import-outside-toplevel
        import docassemble.webapp.update  # pylint: disable=import-outside-toplevel, redefined-outer-name
        import docassemble.base.functions  # pylint: disable=import-outside-toplevel
        docassemble.base.functions.server_context.context = 'celery'
        import docassemble.base.interview_cache  # pylint: disable=import-outside-toplevel
        import docassemble.base.util  # pylint: disable=import-outside-toplevel
        import docassemble.base.parse  # pylint: disable=import-outside-toplevel
        self.flaskapp = flaskapp
        self.set_request_active = set_request_active
        self.fetch_user_dict = fetch_user_dict
        self.save_user_dict = save_user_dict
        self.obtain_lock = obtain_lock
        self.obtain_lock_patiently = obtain_lock_patiently
        self.release_lock = release_lock
        self.Message = Message
        self.reset_user_dict = reset_user_dict
        self.da_send_mail = da_send_mail
        self.functions = docassemble.base.functions
        self.interview_cache = docassemble.base.interview_cache
        self.parse = docassemble.base.parse
        self.retrieve_email = retrieve_email
        self.get_info_from_file_number = get_info_from_file_number
        self.trigger_update = trigger_update
        self.util = docassemble.base.util
        self.r = r
        self.apiclient = apiclient
        self.get_ext_and_mimetype = get_ext_and_mimetype
        self.get_user_object = get_user_object
        self.login_user = login_user
        self.update_last_login = update_last_login
        self.error_notification = error_notification
        self.noquote = noquote
        self.update = docassemble.webapp.update
        self.loaded = True


worker_controller = WorkerController()


def convert(obj):
    return result_from_tuple(obj.as_tuple(), app=workerapp)


def process_error(interview, session_code, yaml_filename, secret, user_info, url, url_root, is_encrypted, error_type, error_message, error_trace, variables, extra):
    start_time = time.time()
    new_action = worker_controller.functions.this_thread.current_info['on_error']
    new_action['arguments']['error_type'] = error_type
    new_action['arguments']['error_message'] = error_message
    new_action['arguments']['error_trace'] = error_trace
    new_action['arguments']['variables'] = variables
    the_current_info = {'user': user_info, 'session': session_code, 'secret': secret, 'yaml_filename': yaml_filename, 'url': url, 'url_root': url_root, 'encrypted': is_encrypted, 'interface': 'worker', 'action': new_action['action'], 'arguments': new_action['arguments']}
    worker_controller.functions.this_thread.current_info = the_current_info
    worker_controller.obtain_lock(session_code, yaml_filename)
    steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
    interview_status = worker_controller.parse.InterviewStatus(current_info=the_current_info)
    old_language = worker_controller.functions.get_language()
    try:
        interview.assemble(user_dict, interview_status)
    except BaseException as e:
        if hasattr(e, 'traceback'):
            logmessage("Error in assembly during error callback: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
        else:
            logmessage("Error in assembly during error callback: " + str(e.__class__.__name__) + ": " + str(e))
        error_type = e.__class__.__name__
        error_message = str(e)
        if hasattr(e, 'traceback'):
            error_trace = str(e.traceback)
            if hasattr(e, 'da_line_with_error'):
                error_trace += "\nIn line: " + str(e.da_line_with_error)
        else:
            error_trace = None
        worker_controller.error_notification(e, message=error_message, trace=error_trace)
    worker_controller.functions.set_language(old_language)
    # is this right?
    save_status = worker_controller.functions.this_thread.misc.get('save_status', 'new')
    if save_status != 'ignore':
        if str(user_info.get('the_user_id', None)).startswith('t'):
            worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, steps=steps)
        else:
            worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, manual_user_id=user_info['theid'], steps=steps)
    worker_controller.release_lock(session_code, yaml_filename)
    if hasattr(interview_status, 'question'):
        if interview_status.question.question_type == "response":
            logmessage("Time in error callback was " + str(time.time() - start_time))
            # logmessage("background_action: status in error callback was response")
            if hasattr(interview_status.question, 'all_variables'):
                pass
            elif not hasattr(interview_status.question, 'binaryresponse'):
                sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
        elif interview_status.question.question_type == "backgroundresponse":
            logmessage("Time in error callback was " + str(time.time() - start_time))
            return worker_controller.functions.ReturnValue(ok=False, error_type=error_type, error_trace=error_trace, error_message=error_message, variables=variables, value=interview_status.question.backgroundresponse, extra=extra)
    logmessage("Time in error callback was " + str(time.time() - start_time))
    return worker_controller.functions.ReturnValue(ok=False, error_type=error_type, error_trace=error_trace, error_message=error_message, variables=variables, extra=extra)


def error_object(err):
    logmessage("Error: " + str(err.__class__.__name__) + ": " + str(err))
    error_type = err.__class__.__name__
    error_message = str(err)
    error_trace = None
    worker_controller.error_notification(err, message=error_message, trace=error_trace)
    return worker_controller.functions.ReturnValue(ok=False, error_message=error_message, error_type=error_type, error_trace=error_trace, restart=False)


@contextmanager
def bg_context():
    worker_controller.initialize()
    url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    url = url_root + 'interview'
    with worker_controller.flaskapp.app_context() as a, worker_controller.flaskapp.test_request_context(base_url=url_root, path=url) as b:
        worker_controller.functions.reset_local_variables()
        worker_controller.set_request_active(False)
        yield (a, b)
