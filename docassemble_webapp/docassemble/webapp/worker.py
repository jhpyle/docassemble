import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(in_celery=True)
from docassemble.base.config import daconfig, hostname
from celery import Celery, chord
from celery.result import result_from_tuple, AsyncResult
import sys
import socket
import importlib

class WorkerController(object):
    pass

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

worker_controller = None

def initialize_db():
    global worker_controller
    worker_controller = WorkerController()
    from docassemble.webapp.server import set_request_active, fetch_user_dict, save_user_dict, obtain_lock, release_lock, get_attachment_info, Message, reset_user_dict, da_send_mail, get_info_from_file_number, retrieve_email, trigger_update
    from docassemble.webapp.server import app as flaskapp
    import docassemble.base.functions
    import docassemble.base.interview_cache
    import docassemble.base.parse
    import docassemble.base.ocr
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
    worker_controller.functions = docassemble.base.functions
    worker_controller.interview_cache = docassemble.base.interview_cache
    worker_controller.parse = docassemble.base.parse
    worker_controller.retrieve_email = retrieve_email
    worker_controller.get_info_from_file_number = get_info_from_file_number
    worker_controller.trigger_update = trigger_update
    worker_controller.ocr = docassemble.base.ocr

def convert(obj):
    return result_from_tuple(obj.as_tuple(), app=workerapp)

# def async_ocr(*pargs, **kwargs):
#     sys.stderr.write("async_ocr started in worker\n")
#     if worker_controller is None:
#         initialize_db()
#     collector = ocr_finalize.s()
#     todo = list()
#     for item in worker_controller.ocr.ocr_page_tasks(*pargs, **kwargs):
#         todo.append(ocr_page.s(**item))
#     the_chord = chord(todo)(collector)
#     sys.stderr.write("async_ocr finished in worker\n")
#     return the_chord

@workerapp.task
def ocr_page(**kwargs):
    sys.stderr.write("ocr_page started in worker\n")
    if worker_controller is None:
        initialize_db()
    worker_controller.functions.set_uid(kwargs['user_code'])
    with worker_controller.flaskapp.app_context():
        return worker_controller.functions.ReturnValue(ok=True, value=worker_controller.ocr.ocr_page(**kwargs))

@workerapp.task
def ocr_finalize(*pargs, **kwargs):
    sys.stderr.write("ocr_finalize started in worker\n")
    if worker_controller is None:
        initialize_db()
    #worker_controller.functions.set_uid(kwargs['user_code'])
    if 'message' in kwargs and kwargs['message']:
        message = kwargs['message']
    else:
        message = worker_controller.functions.word("OCR succeeded")
    with worker_controller.flaskapp.app_context():
        try:
            return worker_controller.functions.ReturnValue(ok=True, value=message, content=worker_controller.ocr.ocr_finalize(*pargs), extra=kwargs.get('extra', None))
        except Exception as the_error:
            return worker_controller.functions.ReturnValue(ok=False, value=str(the_error), error_message=str(the_error), extra=kwargs.get('extra', None))

@workerapp.task
def make_png_for_pdf(doc, prefix, resolution, user_code, pdf_to_png):
    sys.stderr.write("make_png_for_pdf started in worker for size " + prefix + "\n")
    if worker_controller is None:
        initialize_db()
    worker_controller.functions.set_uid(user_code)
    with worker_controller.flaskapp.app_context():
        worker_controller.ocr.make_png_for_pdf(doc, prefix, resolution, pdf_to_png)
    return

@workerapp.task
def update_packages():
    sys.stderr.write("update_packages in worker: starting\n")
    if worker_controller is None:
        initialize_db()
    sys.stderr.write("update_packages in worker: continuing\n")
    try:
        with worker_controller.flaskapp.app_context():
            sys.stderr.write("update_packages in worker: importing update\n")
            import docassemble.webapp.update
            sys.stderr.write("update_packages in worker: starting update\n")
            ok, logmessages, results = docassemble.webapp.update.check_for_updates()
            sys.stderr.write("update_packages in worker: update completed\n")
            worker_controller.trigger_update(except_for=hostname)
            sys.stderr.write("update_packages in worker: trigger completed\n")
            return worker_controller.functions.ReturnValue(ok=ok, logmessages=logmessages, results=results)
    except:
        e = sys.exc_info()[0]
        error_mess = sys.exc_info()[1]
        sys.stderr.write("update_packages in worker: error was " + str(e) + " with message " + str(error_mess) + "\n")
        return worker_controller.functions.ReturnValue(ok=False, error_message=str(e))
    sys.stderr.write("update_packages in worker: all done\n")
    return worker_controller.functions.ReturnValue(ok=False, error_message="Reached end")
    
@workerapp.task
def email_attachments(yaml_filename, user_info, user_code, secret, url, url_root, email_address, question_number, include_editable):
    success = False
    if worker_controller is None:
        initialize_db()
    worker_controller.functions.set_uid(user_code)
    with worker_controller.flaskapp.app_context():
        worker_controller.set_request_active(False)
        the_user_dict, encrypted = worker_controller.get_attachment_info(user_code, question_number, yaml_filename, secret)
        if the_user_dict is not None:
            interview = worker_controller.interview_cache.get_interview(yaml_filename)
            interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=user_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=encrypted, interface='worker', arguments=dict()))
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
                        #sys.stderr.write("Need to attach to the e-mail a file called " + str(the_attachment['filename']) + '.' + str(the_format) + ", which is located on the server at " + str(the_filename) + ", with mime type " + str(mime_type) + "\n")
                        attached_file_count += 1
                if attached_file_count > 0:
                    doc_names = list()
                    for attach_info in attachment_info:
                        if attach_info['attachment']['name'] not in doc_names:
                            doc_names.append(attach_info['attachment']['name'])
                    subject = worker_controller.functions.comma_and_list(doc_names)
                    if len(doc_names) > 1:
                        body = worker_controller.functions.word("Your documents, ") + " " + subject + worker_controller.functions.word(", are attached") + "."
                    else:
                        body = worker_controller.functions.word("Your document, ") + " " + subject + worker_controller.functions.word(", is attached") + "."
                    html = "<p>" + body + "</p>"
                    #sys.stderr.write("Need to send an e-mail with subject " + subject + " to " + str(email_address) + " with " + str(attached_file_count) + " attachment(s)\n")
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
        return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("E-mail was sent to") + " " + email_address, extra='flash')
    else:
        return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("Unable to send e-mail to") + " " + email_address, extra='flash')

@workerapp.task
def background_action(yaml_filename, user_info, session_code, secret, url, url_root, action, extra=None):
    if worker_controller is None:
        initialize_db()
    worker_controller.functions.set_uid(session_code)
    with worker_controller.flaskapp.app_context():
        sys.stderr.write("background_action: yaml_filename is " + str(yaml_filename) + " and session code is " + str(session_code) + "\n")
        worker_controller.set_request_active(False)
        if action['action'] == 'incoming_email':
            if 'id' in action['arguments']:
                action['arguments'] = dict(email=worker_controller.retrieve_email(action['arguments']['id']))
        interview = worker_controller.interview_cache.get_interview(yaml_filename)
        try:
            steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
        except:
            sys.stderr.write("background_action: could not decrypt dictionary\n")
            return(worker_controller.functions.ReturnValue(extra=extra))
        if user_dict is None:
            sys.stderr.write("background_action: dictionary could not be found\n")
            return(worker_controller.functions.ReturnValue(extra=extra))
        interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=is_encrypted, action=action['action'], interface='worker', arguments=action['arguments']))
        try:
            interview.assemble(user_dict, interview_status)
        except Exception as e:
            sys.stderr.write("Error in assembly: " + str(e))
        if not hasattr(interview_status, 'question'):
            #sys.stderr.write("background_action: status was question\n")
            return(worker_controller.functions.ReturnValue(extra=extra))
        if interview_status.question.question_type in ["restart", "exit"]:
            #sys.stderr.write("background_action: status was restart or exit\n")
            worker_controller.reset_user_dict(session_code, yaml_filename)
            worker_controller.release_lock(session_code, yaml_filename)
        if interview_status.question.question_type == "response":
            #sys.stderr.write("background_action: status was response\n")
            if hasattr(interview_status.question, 'all_variables'):
                pass
            elif not hasattr(interview_status.question, 'binaryresponse'):
                sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
        if interview_status.question.question_type == "backgroundresponse":
            #sys.stderr.write("background_action: status was backgroundresponse\n")
            return worker_controller.functions.ReturnValue(value=interview_status.question.backgroundresponse, extra=extra)
        if interview_status.question.question_type == "backgroundresponseaction":
            #sys.stderr.write("background_action: status was backgroundresponseaction\n")
            new_action = interview_status.question.action
            worker_controller.obtain_lock(session_code, yaml_filename)
            steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
            interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=is_encrypted, interface='worker', action=new_action['action'], arguments=new_action['arguments']))
            try:
                interview.assemble(user_dict, interview_status)
            except Exception as e:
                sys.stderr.write("Error in assembly: " + str(e))
            # is this right?
            if str(user_info.get('the_user_id', None)).startswith('t'):
                worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted)
            else:
                worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, manual_user_id=user_info['theid'])
            worker_controller.release_lock(session_code, yaml_filename)
            if hasattr(interview_status, 'question'):
                if interview_status.question.question_type == "response":
                    #sys.stderr.write("background_action: status was response\n")
                    if hasattr(interview_status.question, 'all_variables'):
                        pass
                    elif not hasattr(interview_status.question, 'binaryresponse'):
                        sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
                elif interview_status.question.question_type == "backgroundresponse":
                    return worker_controller.functions.ReturnValue(value=interview_status.question.backgroundresponse, extra=extra)
            return worker_controller.functions.ReturnValue(value=new_action, extra=extra)
        sys.stderr.write("background_action: return at end\n")
        return(worker_controller.functions.ReturnValue(extra=extra))
