def null_function(*pargs, **kwargs):
    return
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(in_celery=True)
from docassemble.base.config import daconfig
import docassemble.base.interview_cache
from docassemble.base.functions import word, comma_and_list, ReturnValue
import docassemble.base.functions
from celery import Celery
from celery.result import result_from_tuple, AsyncResult
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
    from docassemble.webapp.server import set_request_active, fetch_user_dict, save_user_dict, obtain_lock, release_lock, get_attachment_info, Message, reset_user_dict, da_send_mail
    from docassemble.webapp.server import app as flaskapp
    worker_controller.flaskapp = flaskapp
    worker_controller.set_request_active = set_request_active
    worker_controller.fetch_user_dict = fetch_user_dict
    worker_controller.save_user_dict = save_user_dict
    worker_controller.obtain_lock = obtain_lock
    worker_controller.release_lock = release_lock
    worker_controller.get_attachment_info = get_attachment_info
    worker_controller.Message = Message
    worker_controller.reset_user_dict = reset_user_dict
    worker_controller.da_send_mail = da_send_mail

def convert(obj):
    return result_from_tuple(obj.as_tuple(), app=workerapp)

@workerapp.task
def email_attachments(yaml_filename, user_info, user_code, secret, url, url_root, email_address, question_number, include_editable):
    success = False
    if worker_controller is None:
        initialize_db()
    docassemble.base.functions.set_uid(user_code)
    with worker_controller.flaskapp.app_context():
        worker_controller.set_request_active(False)
        the_user_dict = worker_controller.get_attachment_info(user_code, question_number, yaml_filename, secret)
        if the_user_dict is not None:
            interview = docassemble.base.interview_cache.get_interview(yaml_filename)
            interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=user_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, interface='worker', arguments=dict()))
            interview.assemble(the_user_dict, interview_status)
            if len(interview_status.attachments) > 0:
                attached_file_count = 0
                attachment_info = list()
                for the_attachment in interview_status.attachments:
                    file_formats = list()
                    if 'pdf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                        file_formats.append('pdf')
                    if include_editable or 'pdf' not in file_formats:
                        if 'rtf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                            file_formats.append('rtf')
                        if 'docx' in the_attachment['valid_formats']:
                            file_formats.append('docx')
                    for the_format in file_formats:
                        the_filename = the_attachment['file'][the_format]
                        if the_format == "pdf":
                            mime_type = 'application/pdf'
                        elif the_format == "rtf":
                            mime_type = 'application/rtf'
                        elif the_format == "docx":
                            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        attachment_info.append({'filename': str(the_attachment['filename']) + '.' + str(the_format), 'path': str(the_filename), 'mimetype': str(mime_type), 'attachment': the_attachment})
                        sys.stderr.write("Need to attach to the e-mail a file called " + str(the_attachment['filename']) + '.' + str(the_format) + ", which is located on the server at " + str(the_filename) + ", with mime type " + str(mime_type) + "\n")
                        attached_file_count += 1
                if attached_file_count > 0:
                    doc_names = list()
                    for attach_info in attachment_info:
                        if attach_info['attachment']['name'] not in doc_names:
                            doc_names.append(attach_info['attachment']['name'])
                    subject = comma_and_list(doc_names)
                    if len(doc_names) > 1:
                        body = word("Your documents, ") + " " + subject + " " + word(", are attached") + "."
                    else:
                        body = word("Your document, ") + " " + subject + " " + word(", is attached") + "."
                    html = "<p>" + body + "</p>"
                    sys.stderr.write("Need to send an e-mail with subject " + subject + " to " + str(email_address) + " with " + str(attached_file_count) + " attachment(s)\n")
                    msg = worker_controller.Message(subject, recipients=[email_address], body=body, html=html)
                    for attach_info in attachment_info:
                        with open(attach_info['path'], 'rb') as fp:
                            msg.attach(attach_info['filename'], attach_info['mimetype'], fp.read())
                    try:
                        sys.stderr.write("Starting to send\n")
                        worker_controller.da_send_mail(msg)
                        sys.stderr.write("Finished sending\n")
                        success = True
                    except Exception as errmess:
                        sys.stderr.write(str(errmess) + "\n")
                        success = False
    
    if success:
        return ReturnValue(value=word("E-mail was sent to") + " " + email_address, extra='flash')
    else:
        return ReturnValue(value=word("Unable to send e-mail to") + " " + email_address, extra='flash')

@workerapp.task
def background_action(yaml_filename, user_info, session_code, secret, url, url_root, action, extra=None):
    if worker_controller is None:
        initialize_db()
    docassemble.base.functions.set_uid(user_code)
    with worker_controller.flaskapp.app_context():
        sys.stderr.write("background_action: yaml_filename is " + str(yaml_filename) + " and session code is " + str(session_code) + "\n")
        worker_controller.set_request_active(False)
        interview = docassemble.base.interview_cache.get_interview(yaml_filename)
        interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, action=action['action'], interface='worker', arguments=action['arguments']))
        steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
        try:
            interview.assemble(user_dict, interview_status)
        except:
            pass
        if interview_status.question.question_type in ["restart", "exit"]:
            worker_controller.reset_user_dict(session_code, yaml_filename)
            worker_controller.release_lock(session_code, yaml_filename)
        if interview_status.question.question_type == "response":
            if not hasattr(interview_status.question, 'binaryresponse'):
                sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
        if interview_status.question.question_type == "backgroundresponse":
            return ReturnValue(value=interview_status.question.backgroundresponse, extra=extra)
        if interview_status.question.question_type == "backgroundresponseaction":
            new_action = interview_status.question.action
            interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, interface='worker', action=new_action['action'], arguments=new_action['arguments']))
            worker_controller.obtain_lock(session_code, yaml_filename)
            steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
            try:
                interview.assemble(user_dict, interview_status)
            except:
                pass
            # is this right?
            if str(user_info.get('the_user_id', None)).startswith('t'):
                worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted)
            else:
                worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, manual_user_id=user_info['theid'])
            worker_controller.release_lock(session_code, yaml_filename)
            if hasattr(interview_status, 'question') and interview_status.question.question_type == "backgroundresponse":
                return ReturnValue(value=interview_status.question.backgroundresponse, extra=extra)
            return ReturnValue(value=new_action, extra=extra)
        return(ReturnValue(extra=extra))
