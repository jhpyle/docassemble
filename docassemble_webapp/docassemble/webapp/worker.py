import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(in_celery=True)
from docassemble.base.config import daconfig, hostname
from celery import Celery, chord
from celery.result import result_from_tuple, AsyncResult
import celery
import sys
import socket
import importlib
import os
import re
import httplib2
import strict_rfc3339
import oauth2client.client
import time
from docassemble.webapp.files import SavedFile

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
    from docassemble.webapp.server import set_request_active, fetch_user_dict, save_user_dict, obtain_lock, release_lock, Message, reset_user_dict, da_send_mail, get_info_from_file_number, retrieve_email, trigger_update, r, apiclient, get_ext_and_mimetype, get_user_object, login_user, error_notification
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
    worker_controller.r = r
    worker_controller.apiclient = apiclient
    worker_controller.get_ext_and_mimetype = get_ext_and_mimetype
    worker_controller.loaded = True
    worker_controller.get_user_object = get_user_object
    worker_controller.login_user = login_user
    worker_controller.error_notification = error_notification

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

class RedisCredStorage(oauth2client.client.Storage):
    def __init__(self, r, user_id, app='googledrive'):
        self.r = r
        self.key = 'da:' + app + ':userid:' + str(user_id)
        self.lockkey = 'da:' + app + ':lock:userid:' + str(user_id)        
    def acquire_lock(self):
        pipe = self.r.pipeline()
        pipe.set(self.lockkey, 1)
        pipe.expire(self.lockkey, 5)
        pipe.execute()
    def release_lock(self):
        self.r.delete(self.lockkey)
    def locked_get(self):
        json_creds = self.r.get(self.key)
        creds = None
        if json_creds is not None:
            try:
                creds = oauth2client.client.Credentials.new_from_json(json_creds)
            except:
                sys.stderr.write("RedisCredStorage: could not read credentials from " + str(json_creds) + "\n")
        return creds
    def locked_put(self, credentials):
        self.r.set(self.key, credentials.to_json())
    def locked_delete(self):
        self.r.delete(self.key)

@workerapp.task
def sync_with_google_drive(user_id):
    sys.stderr.write("sync_with_google_drive: starting\n")
    if not hasattr(worker_controller, 'loaded'):
        initialize_db()
    sys.stderr.write("sync_with_google_drive: continuing\n")
    storage = RedisCredStorage(worker_controller.r, user_id, app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        sys.stderr.write("sync_with_google_drive: credentials failed\n")
        return worker_controller.functions.ReturnValue(ok=False, error="credentials expired", restart=False)
    try:
        with worker_controller.flaskapp.app_context():
            http = credentials.authorize(httplib2.Http())
            service = worker_controller.apiclient.discovery.build('drive', 'v3', http=http)
            key = 'da:googledrive:mapping:userid:' + str(user_id)
            the_folder = worker_controller.r.get(key)
            response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()
            the_mime_type = response.get('mimeType', None)
            trashed = response.get('trashed', False)
            if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
                return worker_controller.functions.ReturnValue(ok=False, error="error accessing Google Drive", restart=False)
            local_files = dict()
            local_modtimes = dict()
            gd_files = dict()
            gd_ids = dict()
            gd_modtimes = dict()
            gd_deleted = dict()
            sections_modified = set()
            commentary = ''
            for section in ['static', 'templates', 'questions', 'modules', 'sources']:
                local_files[section] = set()
                local_modtimes[section] = dict()
                if section == 'questions':
                    the_section = 'playground'
                elif section == 'templates':
                    the_section = 'playgroundtemplate'
                else:
                    the_section = 'playground' + section
                area = SavedFile(user_id, fix=True, section=the_section)
                for f in os.listdir(area.directory):
                    local_files[section].add(f)
                    local_modtimes[section][f] = os.path.getmtime(os.path.join(area.directory, f))
                    #local_modtimes[section][f] = area.get_modtime(filename=f)
                subdirs = list()
                page_token = None
                while True:
                    param = dict(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + section + "' and '" + str(the_folder) + "' in parents")
                    if page_token is not None:
                        param['pageToken'] = page_token
                    response = service.files().list(**param).execute()
                    for the_file in response.get('files', []):
                        if 'id' in the_file:
                            subdirs.append(the_file['id'])
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                if len(subdirs) == 0:
                    return worker_controller.functions.ReturnValue(ok=False, error="error accessing " + section + " in Google Drive", restart=False)
                subdir = subdirs[0]
                gd_files[section] = set()
                gd_ids[section] = dict()
                gd_modtimes[section] = dict()
                gd_deleted[section] = set()
                page_token = None
                while True:
                    param = dict(spaces="drive", fields="nextPageToken, files(id, name, modifiedTime, trashed)", q="mimeType!='application/vnd.google-apps.folder' and '" + str(subdir) + "' in parents")
                    if page_token is not None:
                        param['pageToken'] = page_token
                    response = service.files().list(**param).execute()
                    for the_file in response.get('files', []):
                        if re.search(r'(\.tmp|\.gdoc|\#)$', the_file['name']):
                            continue
                        if re.search(r'^(\~|\.)', the_file['name']):
                            continue
                        gd_ids[section][the_file['name']] = the_file['id']
                        gd_modtimes[section][the_file['name']] = strict_rfc3339.rfc3339_to_timestamp(the_file['modifiedTime'])
                        sys.stderr.write("Google says modtime on " + unicode(the_file['name']) + " is " + unicode(the_file['modifiedTime']) + ", which is " + unicode(gd_modtimes[section][the_file['name']]) + "\n")
                        if the_file['trashed']:
                            gd_deleted[section].add(the_file['name'])
                            continue
                        gd_files[section].add(the_file['name'])
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                gd_deleted[section] = gd_deleted[section] - gd_files[section]
                for f in gd_files[section]:
                    sys.stderr.write("Considering " + unicode(f) + " on GD\n")
                    if f in local_files[section]:
                        sys.stderr.write("Local timestamp was " + unicode(local_modtimes[section][f]) + " while timestamp on Google Drive was " + unicode(gd_modtimes[section][f]) + "\n")
                    if f not in local_files[section] or gd_modtimes[section][f] - local_modtimes[section][f] > 3:
                        sys.stderr.write("Going to copy " + unicode(f) + " from Google Drive to local\n")
                        sections_modified.add(section)
                        commentary += "Copied " + unicode(f) + " from Google Drive.\n"
                        the_path = os.path.join(area.directory, f)
                        with open(the_path, 'wb') as fh:
                            response = service.files().get_media(fileId=gd_ids[section][f])
                            downloader = worker_controller.apiclient.http.MediaIoBaseDownload(fh, response)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                                #sys.stderr.write("Download %d%%." % int(status.progress() * 100) + "\n")
                        os.utime(the_path, (gd_modtimes[section][f], gd_modtimes[section][f]))
                for f in local_files[section]:
                    sys.stderr.write("Considering " + unicode(f) + ", which is a local file\n")
                    if f in gd_files[section]:
                        sys.stderr.write("Local timestamp was " + unicode(local_modtimes[section][f]) + " while timestamp on Google Drive was " + unicode(gd_modtimes[section][f]) + "\n")
                    if f not in gd_deleted[section]:
                        sys.stderr.write("Considering " + unicode(f) + " is not in Google Drive deleted\n")
                        if f not in gd_files[section]:
                            sys.stderr.write("Considering " + unicode(f) + " is not in Google Drive\n")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0:
                                sys.stderr.write("Found zero byte file: " + unicode(the_path) + "\n")
                                continue
                            sys.stderr.write("Copying " + unicode(f) + " to Google Drive.\n")
                            commentary += "Copied " + unicode(f) + " to Google Drive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
                            sys.stderr.write("Setting GD modtime on new file " + unicode(f) + " to " + unicode(the_modtime) + "\n")
                            file_metadata = { 'name': f, 'parents': [subdir], 'modifiedTime': the_modtime, 'createdTime': the_modtime }
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            the_new_file = service.files().create(body=file_metadata,
                                                                  media_body=media,
                                                                  fields='id').execute()
                            new_id = the_new_file.get('id')
                        elif local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                            sys.stderr.write("Considering " + unicode(f) + " is in Google Drive but local is more recent\n")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0:
                                sys.stderr.write("Found zero byte file during update: " + unicode(the_path) + "\n")
                                continue
                            commentary += "Updated " + unicode(f) + " on Google Drive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
                            sys.stderr.write("Updating on Google Drive and setting GD modtime on modified " + unicode(f) + " to " + unicode(the_modtime) + "\n")
                            file_metadata = { 'modifiedTime': the_modtime }
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            updated_file = service.files().update(fileId=gd_ids[section][f],
                                                                  body=file_metadata,
                                                                  media_body=media,
                                                                  fields='modifiedTime').execute()
                            gd_modtimes[section][f] = strict_rfc3339.rfc3339_to_timestamp(updated_file['modifiedTime'])
                            sys.stderr.write("After update, timestamp on Google Drive is " + unicode(gd_modtimes[section][f]) + "\n")
                            sys.stderr.write("After update, timestamp on local system is " + unicode(os.path.getmtime(the_path)) + "\n")
                for f in gd_deleted[section]:
                    sys.stderr.write("Considering " + unicode(f) + " is deleted on Google Drive\n")
                    if f in local_files[section]:
                        sys.stderr.write("Considering " + unicode(f) + " is deleted on Google Drive but exists locally\n")
                        sys.stderr.write("Local timestamp was " + unicode(local_modtimes[section][f]) + " while timestamp on Google Drive was " + unicode(gd_modtimes[section][f]) + "\n")
                        if local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                            sys.stderr.write("Considering " + unicode(f) + " is deleted on Google Drive but exists locally and needs to be undeleted on GD\n")
                            commentary += "Undeleted and updated " + unicode(f) + " on Google Drive.\n"
                            the_path = os.path.join(area.directory, f)
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
                            sys.stderr.write("Setting GD modtime on undeleted file " + unicode(f) + " to " + unicode(the_modtime) + "\n")
                            file_metadata = { 'modifiedTime': the_modtime, 'trashed': False }
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            updated_file = service.files().update(fileId=gd_ids[section][f],
                                                                  body=file_metadata,
                                                                  media_body=media,
                                                                  fields='modifiedTime').execute()
                            gd_modtimes[section][f] = strict_rfc3339.rfc3339_to_timestamp(updated_file['modifiedTime'])
                        else:
                            sys.stderr.write("Considering " + unicode(f) + " is deleted on Google Drive but exists locally and needs to deleted locally\n")
                            sections_modified.add(section)
                            commentary += "Deleted " + unicode(f) + " from Playground.\n"
                            the_path = os.path.join(area.directory, f)
                            if os.path.isfile(the_path):
                                area.delete_file(f)
                for f in os.listdir(area.directory):
                    the_path = os.path.join(area.directory, f)
                    sys.stderr.write("Before finalizing, " + unicode(f) + " has a modtime of " + unicode(os.path.getmtime(the_path)) + "\n")
                area.finalize()
                for f in os.listdir(area.directory):
                    if f not in gd_files[section]:
                        continue
                    local_files[section].add(f)
                    the_path = os.path.join(area.directory, f)
                    local_modtimes[section][f] = os.path.getmtime(the_path)
                    sys.stderr.write("After finalizing, " + unicode(f) + " has a modtime of " + unicode(local_modtimes[section][f]) + "\n")
                    if abs(local_modtimes[section][f] - gd_modtimes[section][f]) > 3:
                        the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
                        sys.stderr.write("post-finalize: updating GD modtime on file " + unicode(f) + " to " + unicode(the_modtime) + "\n")
                        file_metadata = { 'modifiedTime': the_modtime }
                        updated_file = service.files().update(fileId=gd_ids[section][f],
                                                              body=file_metadata,
                                                              fields='modifiedTime').execute()
                        gd_modtimes[section][f] = strict_rfc3339.rfc3339_to_timestamp(updated_file['modifiedTime'])
            for key in worker_controller.r.keys('da:interviewsource:docassemble.playground' + str(user_id) + ':*'):
                worker_controller.r.incr(key)
            if commentary != '':
                sys.stderr.write(commentary + "\n")
        if 'modules' in sections_modified:
            do_restart = True
        else:
            do_restart = False
        return worker_controller.functions.ReturnValue(ok=True, summary=commentary, restart=do_restart)
    except Exception as e:
        return worker_controller.functions.ReturnValue(ok=False, error="Error syncing with Google Drive: " + str(e), restart=False)

@workerapp.task
def ocr_page(**kwargs):
    sys.stderr.write("ocr_page started in worker\n")
    if not hasattr(worker_controller, 'loaded'):
        initialize_db()
    worker_controller.functions.set_uid(kwargs['user_code'])
    worker_controller.functions.reset_local_variables()
    with worker_controller.flaskapp.app_context():
        return worker_controller.functions.ReturnValue(ok=True, value=worker_controller.ocr.ocr_page(**kwargs))

@workerapp.task
def ocr_finalize(*pargs, **kwargs):
    sys.stderr.write("ocr_finalize started in worker\n")
    if not hasattr(worker_controller, 'loaded'):
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
def make_png_for_pdf(doc, prefix, resolution, user_code, pdf_to_png, page=None):
    sys.stderr.write("make_png_for_pdf started in worker for size " + prefix + "\n")
    if not hasattr(worker_controller, 'loaded'):
        initialize_db()
    worker_controller.functions.set_uid(user_code)
    worker_controller.functions.reset_local_variables()
    with worker_controller.flaskapp.app_context():
        worker_controller.ocr.make_png_for_pdf(doc, prefix, resolution, pdf_to_png, page=page)
    return

@workerapp.task
def update_packages():
    sys.stderr.write("update_packages in worker: starting\n")
    if not hasattr(worker_controller, 'loaded'):
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
def email_attachments(user_code, email_address, attachment_info):
    success = False
    if not hasattr(worker_controller, 'loaded'):
        initialize_db()
    worker_controller.functions.set_uid(user_code)
    worker_controller.functions.reset_local_variables()
    with worker_controller.flaskapp.app_context():
        worker_controller.set_request_active(False)
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
        msg = worker_controller.Message(subject, recipients=[email_address], body=body, html=html)
        success_attach = True
        for attach_info in attachment_info:
            file_info = worker_controller.get_info_from_file_number(attach_info['number'])
            if 'fullpath' in file_info:
                with open(file_info['fullpath'], 'rb') as fp:
                    msg.attach(attach_info['filename'], attach_info['mimetype'], fp.read())
            else:
                success_attach = False
        if success_attach:
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

# @workerapp.task
# def old_email_attachments(yaml_filename, user_info, user_code, secret, url, url_root, email_address, question_number, include_editable):
#     success = False
#     if not hasattr(worker_controller, 'loaded'):
#         initialize_db()
#     worker_controller.functions.set_uid(user_code)
#     with worker_controller.flaskapp.app_context():
#         worker_controller.set_request_active(False)
#         #the_user_dict, encrypted = worker_controller.get_attachment_info(user_code, question_number, yaml_filename, secret)
#         steps, the_user_dict, is_encrypted = worker_controller.fetch_user_dict(user_code, yaml_filename, secret=secret)
#         if the_user_dict is not None:
#             interview = worker_controller.interview_cache.get_interview(yaml_filename)
#             interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=user_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=encrypted, interface='worker', arguments=dict()))
#             interview.assemble(the_user_dict, interview_status)
#             if len(interview_status.attachments) > 0:
#                 attached_file_count = 0
#                 attachment_info = list()
#                 for the_attachment in interview_status.attachments:
#                     file_formats = list()
#                     if 'pdf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
#                         file_formats.append('pdf')
#                     if include_editable or 'pdf' not in file_formats:
#                         if 'rtf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
#                             file_formats.append('rtf')
#                         if 'docx' in the_attachment['valid_formats']:
#                             file_formats.append('docx')
#                     for the_format in file_formats:
#                         the_filename = the_attachment['file'][the_format]
#                         if the_format == "pdf":
#                             mime_type = 'application/pdf'
#                         elif the_format == "rtf":
#                             mime_type = 'application/rtf'
#                         elif the_format == "docx":
#                             mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
#                         attachment_info.append({'filename': str(the_attachment['filename']) + '.' + str(the_format), 'path': str(the_filename), 'mimetype': str(mime_type), 'attachment': the_attachment})
#                         #sys.stderr.write("Need to attach to the e-mail a file called " + str(the_attachment['filename']) + '.' + str(the_format) + ", which is located on the server at " + str(the_filename) + ", with mime type " + str(mime_type) + "\n")
#                         attached_file_count += 1
#                 if attached_file_count > 0:
#                     doc_names = list()
#                     for attach_info in attachment_info:
#                         if attach_info['attachment']['name'] not in doc_names:
#                             doc_names.append(attach_info['attachment']['name'])
#                     subject = worker_controller.functions.comma_and_list(doc_names)
#                     if len(doc_names) > 1:
#                         body = worker_controller.functions.word("Your documents, ") + " " + subject + worker_controller.functions.word(", are attached") + "."
#                     else:
#                         body = worker_controller.functions.word("Your document, ") + " " + subject + worker_controller.functions.word(", is attached") + "."
#                     html = "<p>" + body + "</p>"
#                     #sys.stderr.write("Need to send an e-mail with subject " + subject + " to " + str(email_address) + " with " + str(attached_file_count) + " attachment(s)\n")
#                     msg = worker_controller.Message(subject, recipients=[email_address], body=body, html=html)
#                     for attach_info in attachment_info:
#                         with open(attach_info['path'], 'rb') as fp:
#                             msg.attach(attach_info['filename'], attach_info['mimetype'], fp.read())
#                     try:
#                         sys.stderr.write("Starting to send\n")
#                         worker_controller.da_send_mail(msg)
#                         sys.stderr.write("Finished sending\n")
#                         success = True
#                     except Exception as errmess:
#                         sys.stderr.write(str(errmess) + "\n")
#                         success = False
    
#     if success:
#         return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("E-mail was sent to") + " " + email_address, extra='flash')
#     else:
#         return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("Unable to send e-mail to") + " " + email_address, extra='flash')

@workerapp.task
def background_action(yaml_filename, user_info, session_code, secret, url, url_root, action, extra=None):
    if not hasattr(worker_controller, 'loaded'):
        initialize_db()
    worker_controller.functions.set_uid(session_code)
    worker_controller.functions.reset_local_variables()
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url):
            if not str(user_info['the_user_id']).startswith('t'):
                worker_controller.login_user(worker_controller.get_user_object(user_info['theid']), remember=False)
            sys.stderr.write("background_action: yaml_filename is " + str(yaml_filename) + " and session code is " + str(session_code) + " and action is " + repr(action) + "\n")
            worker_controller.set_request_active(False)
            if action['action'] == 'incoming_email':
                if 'id' in action['arguments']:
                    action['arguments'] = dict(email=worker_controller.retrieve_email(action['arguments']['id']))
            interview = worker_controller.interview_cache.get_interview(yaml_filename)
            worker_controller.obtain_lock(session_code, yaml_filename)
            worker_controller.release_lock(session_code, yaml_filename)
            try:
                steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
            except Exception as the_err:
                sys.stderr.write("background_action: could not obtain dictionary because of " + str(the_err.__class__.__name__) + ": " + str(the_err) + "\n")
                return(worker_controller.functions.ReturnValue(extra=extra))
            if user_dict is None:
                sys.stderr.write("background_action: dictionary could not be found\n")
                return(worker_controller.functions.ReturnValue(extra=extra))
            start_time = time.time()
            interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=is_encrypted, action=action['action'], interface='worker', arguments=action['arguments']))
            try:
                interview.assemble(user_dict, interview_status)
            except Exception as e:
                if hasattr(e, 'traceback'):
                    sys.stderr.write("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
                else:
                    sys.stderr.write("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e))
                error_type = e.__class__.__name__
                error_message = unicode(e)
                if hasattr(e, 'traceback'):
                    error_trace = unicode(e.traceback)
                    if hasattr(e, 'da_line_with_error'):
                        error_trace += "\nIn line: " + unicode(e.da_line_with_error)
                else:
                    error_trace = None
                variables = list(reversed([y for y in worker_controller.functions.this_thread.current_variable]))
                worker_controller.error_notification(e, message=error_message, trace=error_trace)
                if 'on_error' not in worker_controller.functions.this_thread.current_info:
                    return(worker_controller.functions.ReturnValue(ok=False, error_message=error_message, error_type=error_type, error_trace=error_trace, variables=variables))
                else:
                    sys.stderr.write("Time in background action before error callback was " + str(time.time() - start_time))
                    return process_error(interview, session_code, yaml_filename, secret, user_info, url, url_root, is_encrypted, error_type, error_message, error_trace, variables, extra)
            sys.stderr.write("Time in background action was " + str(time.time() - start_time))
            if not hasattr(interview_status, 'question'):
                #sys.stderr.write("background_action: status had no question\n")
                return(worker_controller.functions.ReturnValue(extra=extra))
            if interview_status.question.question_type in ["restart", "exit"]:
                #sys.stderr.write("background_action: status was restart or exit\n")
                if str(user_info.get('the_user_id', None)).startswith('t'):
                    worker_controller.reset_user_dict(session_code, yaml_filename, temp_user_id=user_info.get('theid', None))
                else:
                    worker_controller.reset_user_dict(session_code, yaml_filename, user_id=user_info.get('theid', None))
            if interview_status.question.question_type in ["restart", "exit", "logout"]:
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
                start_time = time.time()
                new_action = interview_status.question.action
                #sys.stderr.write("new action is " + repr(new_action) + "\n")
                worker_controller.obtain_lock(session_code, yaml_filename)
                steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
                interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=is_encrypted, interface='worker', action=new_action['action'], arguments=new_action['arguments']))
                try:
                    interview.assemble(user_dict, interview_status)
                    has_error = False
                except Exception as e:
                    if hasattr(e, 'traceback'):
                        sys.stderr.write("Error in assembly during callback: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
                    else:
                        sys.stderr.write("Error in assembly during callback: " + str(e.__class__.__name__) + ": " + str(e))
                    error_type = e.__class__.__name__
                    error_message = unicode(e)
                    if hasattr(e, 'traceback'):
                        error_trace = unicode(e.traceback)
                        if hasattr(e, 'da_line_with_error'):
                            error_trace += "\nIn line: " + unicode(e.da_line_with_error)
                    else:
                        error_trace = None
                    variables = list(reversed([y for y in worker_controller.functions.this_thread.current_variable]))
                    worker_controller.error_notification(e, message=error_message, trace=error_trace)
                    has_error = True
                # is this right?
                if str(user_info.get('the_user_id', None)).startswith('t'):
                    worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, steps=steps)
                else:
                    worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, manual_user_id=user_info['theid'], steps=steps)
                worker_controller.release_lock(session_code, yaml_filename)
                if has_error:
                    return worker_controller.functions.ReturnValue(ok=False, error_type=error_type, error_trace=error_trace, error_message=error_message, variables=variables, extra=extra)
                if hasattr(interview_status, 'question'):
                    if interview_status.question.question_type == "response":
                        #sys.stderr.write("background_action: status was response\n")
                        if hasattr(interview_status.question, 'all_variables'):
                            pass
                        elif not hasattr(interview_status.question, 'binaryresponse'):
                            sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
                    elif interview_status.question.question_type == "backgroundresponse":
                        sys.stderr.write("Time in background response action was " + str(time.time() - start_time))
                        return worker_controller.functions.ReturnValue(value=interview_status.question.backgroundresponse, extra=extra)
                sys.stderr.write("Time in background response action was " + str(time.time() - start_time))
                return worker_controller.functions.ReturnValue(value=new_action, extra=extra)
            if hasattr(interview_status, 'questionText') and interview_status.questionText:
                sys.stderr.write("background_action: The end result of the background action was the asking of this question: " + repr(str(interview_status.questionText).strip()) + "\n")
                sys.stderr.write("background_action: Perhaps your interview did not ask all of the questions needed for the background action to do its work.")
                sys.stderr.write("background_action: Or perhaps your background action did its job, but you did not end it with a call to background_response().")
                error_type = 'QuestionError'
                error_trace = None
                error_message = interview_status.questionText
                variables = list(reversed([y for y in worker_controller.functions.this_thread.current_variable]))
                worker_controller.error_notification(Exception("The end result of the background action was the asking of this question: " + repr(str(interview_status.questionText).strip())))
                if 'on_error' not in worker_controller.functions.this_thread.current_info:
                    return worker_controller.functions.ReturnValue(ok=False, error_type=error_type, error_trace=error_trace, error_message=error_message, variables=variables, extra=extra)
                else:
                    return process_error(interview, session_code, yaml_filename, secret, user_info, url, url_root, is_encrypted, error_type, error_message, error_trace, variables, extra)
            sys.stderr.write("background_action: finished\n")
            return(worker_controller.functions.ReturnValue(extra=extra))

def process_error(interview, session_code, yaml_filename, secret, user_info, url, url_root, is_encrypted, error_type, error_message, error_trace, variables, extra):
    start_time = time.time()
    new_action = worker_controller.functions.this_thread.current_info['on_error']
    new_action['arguments']['error_type'] = error_type
    new_action['arguments']['error_message'] = error_message
    new_action['arguments']['error_trace'] = error_trace
    new_action['arguments']['variables'] = variables
    worker_controller.obtain_lock(session_code, yaml_filename)
    steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
    interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=is_encrypted, interface='worker', action=new_action['action'], arguments=new_action['arguments']))
    try:
        interview.assemble(user_dict, interview_status)
    except Exception as e:
        if hasattr(e, 'traceback'):
            sys.stderr.write("Error in assembly during error callback: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
        else:
            sys.stderr.write("Error in assembly during error callback: " + str(e.__class__.__name__) + ": " + str(e))
        error_type = e.__class__.__name__
        error_message = unicode(e)
        if hasattr(e, 'traceback'):
            error_trace = unicode(e.traceback)
            if hasattr(e, 'da_line_with_error'):
                error_trace += "\nIn line: " + unicode(e.da_line_with_error)
        else:
            error_trace = None
        worker_controller.error_notification(e, message=error_message, trace=error_trace)
    # is this right?
    if str(user_info.get('the_user_id', None)).startswith('t'):
        worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, steps=steps)
    else:
        worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, manual_user_id=user_info['theid'], steps=steps)
    worker_controller.release_lock(session_code, yaml_filename)
    if hasattr(interview_status, 'question'):
        if interview_status.question.question_type == "response":
            sys.stderr.write("Time in error callback was " + str(time.time() - start_time))
            #sys.stderr.write("background_action: status in error callback was response\n")
            if hasattr(interview_status.question, 'all_variables'):
                pass
            elif not hasattr(interview_status.question, 'binaryresponse'):
                sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
        elif interview_status.question.question_type == "backgroundresponse":
            sys.stderr.write("Time in error callback was " + str(time.time() - start_time))
            return worker_controller.functions.ReturnValue(ok=False, error_type=error_type, error_trace=error_trace, error_message=error_message, variables=variables, value=interview_status.question.backgroundresponse, extra=extra)
    sys.stderr.write("Time in error callback was " + str(time.time() - start_time))
    return worker_controller.functions.ReturnValue(ok=False, error_type=error_type, error_trace=error_trace, error_message=error_message, variables=variables, extra=extra)
