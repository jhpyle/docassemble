from six import string_types, text_type, PY2
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(in_celery=True)
from docassemble.base.config import daconfig, hostname
from celery import Celery, chord
from celery.result import result_from_tuple, AsyncResult
from celery.backends.redis import RedisBackend
import celery
import copy
import sys
import socket
import importlib
import os
import re
import httplib2
import oauth2client.client
import time
import json
import iso8601
import datetime
import pytz
import traceback
from subprocess import call
from requests.utils import quote
from docassemble.webapp.files import SavedFile
from io import open

if os.environ.get('SUPERVISOR_SERVER_URL', None):
    USING_SUPERVISOR = True
else:
    USING_SUPERVISOR = False

WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
container_role = ':' + os.environ.get('CONTAINERROLE', '') + ':'

ONEDRIVE_CHUNK_SIZE = 2000000

class WorkerController(object):
    pass

backend = daconfig.get('redis', None)
if backend is None:
    backend = 'redis://localhost'
broker = daconfig.get('rabbitmq', None)
if broker is None:
    broker = 'pyamqp://guest@' + socket.gethostname() + '//'

SUPERVISORCTL = daconfig.get('supervisorctl', 'supervisorctl')

workerapp = Celery('docassemble.webapp.worker', backend=backend, broker=broker)
importlib.import_module('docassemble.webapp.config_worker')
workerapp.config_from_object('docassemble.webapp.config_worker')
workerapp.set_current()
workerapp.set_default()

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
            json_creds = json_creds.decode()
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
            if the_folder is not None:
                the_folder = the_folder.decode()
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
                        gd_modtimes[section][the_file['name']] = epoch_from_iso(the_file['modifiedTime'])
                        sys.stderr.write("Google says modtime on " + text_type(the_file['name']) + " is " + text_type(the_file['modifiedTime']) + ", which is " + text_type(gd_modtimes[section][the_file['name']]) + "\n")
                        if the_file['trashed']:
                            gd_deleted[section].add(the_file['name'])
                            continue
                        gd_files[section].add(the_file['name'])
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                gd_deleted[section] = gd_deleted[section] - gd_files[section]
                for f in gd_files[section]:
                    sys.stderr.write("Considering " + text_type(f) + " on GD\n")
                    if f in local_files[section]:
                        sys.stderr.write("Local timestamp was " + text_type(local_modtimes[section][f]) + " while timestamp on Google Drive was " + text_type(gd_modtimes[section][f]) + "\n")
                    if f not in local_files[section] or gd_modtimes[section][f] - local_modtimes[section][f] > 3:
                        sys.stderr.write("Going to copy " + text_type(f) + " from Google Drive to local\n")
                        sections_modified.add(section)
                        commentary += "Copied " + text_type(f) + " from Google Drive.\n"
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
                    sys.stderr.write("Considering " + text_type(f) + ", which is a local file\n")
                    if f in gd_files[section]:
                        sys.stderr.write("Local timestamp was " + text_type(local_modtimes[section][f]) + " while timestamp on Google Drive was " + text_type(gd_modtimes[section][f]) + "\n")
                    if f not in gd_deleted[section]:
                        sys.stderr.write("Considering " + text_type(f) + " is not in Google Drive deleted\n")
                        if f not in gd_files[section]:
                            sys.stderr.write("Considering " + text_type(f) + " is not in Google Drive\n")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0:
                                sys.stderr.write("Found zero byte file: " + text_type(the_path) + "\n")
                                continue
                            sys.stderr.write("Copying " + text_type(f) + " to Google Drive.\n")
                            commentary += "Copied " + text_type(f) + " to Google Drive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            sys.stderr.write("Setting GD modtime on new file " + text_type(f) + " to " + text_type(the_modtime) + "\n")
                            file_metadata = { 'name': f, 'parents': [subdir], 'modifiedTime': the_modtime, 'createdTime': the_modtime }
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            the_new_file = service.files().create(body=file_metadata,
                                                                  media_body=media,
                                                                  fields='id').execute()
                            new_id = the_new_file.get('id')
                        elif local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                            sys.stderr.write("Considering " + text_type(f) + " is in Google Drive but local is more recent\n")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0:
                                sys.stderr.write("Found zero byte file during update: " + text_type(the_path) + "\n")
                                continue
                            commentary += "Updated " + text_type(f) + " on Google Drive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            sys.stderr.write("Updating on Google Drive and setting GD modtime on modified " + text_type(f) + " to " + text_type(the_modtime) + "\n")
                            file_metadata = { 'modifiedTime': the_modtime }
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            updated_file = service.files().update(fileId=gd_ids[section][f],
                                                                  body=file_metadata,
                                                                  media_body=media,
                                                                  fields='modifiedTime').execute()
                            gd_modtimes[section][f] = epoch_from_iso(updated_file['modifiedTime'])
                            sys.stderr.write("After update, timestamp on Google Drive is " + text_type(gd_modtimes[section][f]) + "\n")
                            sys.stderr.write("After update, timestamp on local system is " + text_type(os.path.getmtime(the_path)) + "\n")
                for f in gd_deleted[section]:
                    sys.stderr.write("Considering " + text_type(f) + " is deleted on Google Drive\n")
                    if f in local_files[section]:
                        sys.stderr.write("Considering " + text_type(f) + " is deleted on Google Drive but exists locally\n")
                        sys.stderr.write("Local timestamp was " + text_type(local_modtimes[section][f]) + " while timestamp on Google Drive was " + text_type(gd_modtimes[section][f]) + "\n")
                        if local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                            sys.stderr.write("Considering " + text_type(f) + " is deleted on Google Drive but exists locally and needs to be undeleted on GD\n")
                            commentary += "Undeleted and updated " + text_type(f) + " on Google Drive.\n"
                            the_path = os.path.join(area.directory, f)
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            sys.stderr.write("Setting GD modtime on undeleted file " + text_type(f) + " to " + text_type(the_modtime) + "\n")
                            file_metadata = { 'modifiedTime': the_modtime, 'trashed': False }
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            updated_file = service.files().update(fileId=gd_ids[section][f],
                                                                  body=file_metadata,
                                                                  media_body=media,
                                                                  fields='modifiedTime').execute()
                            gd_modtimes[section][f] = epoch_from_iso(updated_file['modifiedTime'])
                        else:
                            sys.stderr.write("Considering " + text_type(f) + " is deleted on Google Drive but exists locally and needs to deleted locally\n")
                            sections_modified.add(section)
                            commentary += "Deleted " + text_type(f) + " from Playground.\n"
                            the_path = os.path.join(area.directory, f)
                            if os.path.isfile(the_path):
                                area.delete_file(f)
                for f in os.listdir(area.directory):
                    the_path = os.path.join(area.directory, f)
                    sys.stderr.write("Before finalizing, " + text_type(f) + " has a modtime of " + text_type(os.path.getmtime(the_path)) + "\n")
                area.finalize()
                for f in os.listdir(area.directory):
                    if f not in gd_files[section]:
                        continue
                    local_files[section].add(f)
                    the_path = os.path.join(area.directory, f)
                    local_modtimes[section][f] = os.path.getmtime(the_path)
                    sys.stderr.write("After finalizing, " + text_type(f) + " has a modtime of " + text_type(local_modtimes[section][f]) + "\n")
                    if abs(local_modtimes[section][f] - gd_modtimes[section][f]) > 3:
                        the_modtime = iso_from_epoch(local_modtimes[section][f])
                        sys.stderr.write("post-finalize: updating GD modtime on file " + text_type(f) + " to " + text_type(the_modtime) + "\n")
                        file_metadata = { 'modifiedTime': the_modtime }
                        updated_file = service.files().update(fileId=gd_ids[section][f],
                                                              body=file_metadata,
                                                              fields='modifiedTime').execute()
                        gd_modtimes[section][f] = epoch_from_iso(updated_file['modifiedTime'])
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

def try_request(*pargs, **kwargs):
    start_time = time.time()
    args = [arg for arg in pargs]
    http = args.pop(0)
    tries = 1
    while tries < 5:
        r, content = http.request(*args, **kwargs)
        if int(r['status']) != 504:
            break
        sys.stderr.write("Got a 504 after try " + text_type(tries) + "\n")
        time.sleep(2*tries)
        tries += 1
    sys.stderr.write("try_request: duration was %.2f seconds\n" % (time.time() - start_time, ))
    return r, content

def epoch_from_iso(datestring):
    return (iso8601.parse_date(datestring) - datetime.datetime(1970,1,1, tzinfo=pytz.utc)).total_seconds()

def iso_from_epoch(seconds):
    return datetime.datetime.utcfromtimestamp(seconds).replace(tzinfo=pytz.utc).isoformat().replace('+00:00', 'Z')

@workerapp.task
def sync_with_onedrive(user_id):
    sys.stderr.write("sync_with_onedrive: starting\n")
    if not hasattr(worker_controller, 'loaded'):
        initialize_db()
    sys.stderr.write("sync_with_onedrive: continuing\n")
    storage = RedisCredStorage(worker_controller.r, user_id, app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        sys.stderr.write("sync_with_onedrive: credentials failed\n")
        return worker_controller.functions.ReturnValue(ok=False, error="credentials expired", restart=False)
    try:
        with worker_controller.flaskapp.app_context():
            http = credentials.authorize(httplib2.Http())
            #r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive", "GET")
            #drive_id = json.loads(content)['id']
            #r, content = try_request(http, "https://graph.microsoft.com/v1.0/drive/special/approot")
            #if int(r['status']) != 200:
            #    return worker_controller.functions.ReturnValue(ok=False, error="Could not verify application root", restart=False)
            key = 'da:onedrive:mapping:userid:' + str(user_id)
            the_folder = worker_controller.r.get(key)
            if the_folder is not None:
                the_folder = the_folder.decode()
            r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(the_folder), "GET")
            if int(r['status']) != 200:
                trashed = True
            else:
                info = json.loads(content.decode())
                if 'deleted' in info:
                    trashed = True
                else:
                    trashed = False
            if trashed is True:
                sys.stderr.write('trash_gd_file: folder did not exist' + "\n")
                return False
            if trashed is True or 'folder' not in info:
                return worker_controller.functions.ReturnValue(ok=False, error="error accessing OneDrive", restart=False)
            local_files = dict()
            local_modtimes = dict()
            od_files = dict()
            od_ids = dict()
            od_modtimes = dict()
            od_createtimes = dict()
            od_deleted = dict()
            sections_modified = set()
            commentary = ''
            subdirs = dict()
            subdir_count = dict()
            r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
            while True:
                if int(r['status']) != 200:
                    return worker_controller.functions.ReturnValue(ok=False, error="error accessing OneDrive subfolders", restart=False)
                info = json.loads(content.decode())
                for item in info['value']:
                    if 'deleted' in item or 'folder' not in item:
                        continue
                    if item['name'] in ('static', 'templates', 'questions', 'modules', 'sources'):
                        subdirs[item['name']] = item['id']
                        subdir_count[item['name']] = item['folder']['childCount']
                if "@odata.nextLink" not in info:
                    break
                r, content = try_request(http, info["@odata.nextLink"], "GET")
            for section in ['static', 'templates', 'questions', 'modules', 'sources']:
                sys.stderr.write("sync_with_onedrive: processing " + section + "\n")
                if section not in subdirs:
                    worker_controller.functions.ReturnValue(ok=False, error="error accessing " + section + " in OneDrive", restart=False)
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
                page_token = None
                od_files[section] = set()
                od_ids[section] = dict()
                od_modtimes[section] = dict()
                od_createtimes[section] = dict()
                od_deleted[section] = set()
                page_token = None
                if subdir_count[section] == 0:
                    sys.stderr.write("sync_with_onedrive: skipping " + section + " because empty on remote\n")
                else:
                    r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(subdirs[section]) + "/children?$select=id,name,deleted,fileSystemInfo", "GET")
                    sys.stderr.write("sync_with_onedrive: processing " + section + ", which is " + text_type(subdirs[section]) + "\n")
                    while True:
                        if int(r['status']) != 200:
                            return worker_controller.functions.ReturnValue(ok=False, error="error accessing OneDrive subfolder " + section + " " + text_type(r['status']) + ": " + content.decode() + " looking for " + text_type(subdirs[section]), restart=False)
                        info = json.loads(content.decode())
                        #sys.stderr.write("sync_with_onedrive: result was " + repr(info) + "\n")
                        for the_file in info['value']:
                            #sys.stderr.write("sync_with_onedrive: found a file " + repr(the_file) + "\n")
                            if 'folder' in the_file:
                                continue
                            if re.search(r'^(\~|\.)', the_file['name']):
                                continue
                            od_ids[section][the_file['name']] = the_file['id']
                            od_modtimes[section][the_file['name']] = epoch_from_iso(the_file['fileSystemInfo']['lastModifiedDateTime'])
                            od_createtimes[section][the_file['name']] = epoch_from_iso(the_file['fileSystemInfo']['createdDateTime'])
                            sys.stderr.write("OneDrive says modtime on " + text_type(the_file['name']) + " in " + section + " is " + text_type(the_file['fileSystemInfo']['lastModifiedDateTime']) + ", which is " + text_type(od_modtimes[section][the_file['name']]) + "\n")
                            if the_file.get('deleted', None):
                                od_deleted[section].add(the_file['name'])
                                continue
                            od_files[section].add(the_file['name'])
                        if "@odata.nextLink" not in info:
                            break
                        r, content = try_request(http, info["@odata.nextLink"], "GET")
                od_deleted[section] = od_deleted[section] - od_files[section]
                for f in od_files[section]:
                    sys.stderr.write("Considering " + text_type(f) + " on OD\n")
                    if f in local_files[section]:
                        sys.stderr.write("Local timestamp was " + text_type(local_modtimes[section][f]) + " while timestamp on OneDrive was " + text_type(od_modtimes[section][f]) + "\n")
                    if f not in local_files[section] or od_modtimes[section][f] - local_modtimes[section][f] > 3:
                        sys.stderr.write("Going to copy " + text_type(f) + " from OneDrive to local\n")
                        sections_modified.add(section)
                        commentary += "Copied " + text_type(f) + " from OneDrive.\n"
                        the_path = os.path.join(area.directory, f)
                        r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(od_ids[section][f]) + "/content", "GET")
                        with open(the_path, 'wb') as fh:
                            fh.write(content)
                        os.utime(the_path, (od_modtimes[section][f], od_modtimes[section][f]))
                for f in local_files[section]:
                    sys.stderr.write("Considering " + text_type(f) + ", which is a local file\n")
                    if f in od_files[section]:
                        sys.stderr.write("Local timestamp was " + text_type(local_modtimes[section][f]) + " while timestamp on OneDrive was " + text_type(od_modtimes[section][f]) + "\n")
                    if f not in od_deleted[section]:
                        sys.stderr.write("Considering " + text_type(f) + " is not in OneDrive deleted\n")
                        if f not in od_files[section]:
                            sys.stderr.write("Considering " + text_type(f) + " is not in OneDrive\n")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0:
                                sys.stderr.write("Found zero byte file: " + text_type(the_path) + "\n")
                                continue
                            sys.stderr.write("Copying " + text_type(f) + " to OneDrive.\n")
                            commentary += "Copied " + text_type(f) + " to OneDrive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            sys.stderr.write("Setting OD modtime on new file " + text_type(f) + " to " + text_type(the_modtime) + " which is " + text_type(local_modtimes[section][f]) + "\n")
                            data = dict()
                            data['name'] = f
                            data['description'] = ''
                            data["fileSystemInfo"] = { "createdDateTime": the_modtime, "lastModifiedDateTime": the_modtime }
                            #data["fileSystemInfo"] = { "createdDateTime": the_modtime, "lastAccessedDateTime": the_modtime, "lastModifiedDateTime": the_modtime }
                            #data["@microsoft.graph.conflictBehavior"] = "replace"
                            result = onedrive_upload(http, subdirs[section], section, data, the_path)
                            if isinstance(result, worker_controller.functions.ReturnValue):
                                return result
                            od_files[section].add(f)
                            od_ids[section][f] = result
                            od_modtimes[section][f] = local_modtimes[section][f]
                            od_createtimes[section][f] = local_modtimes[section][f]
                        elif local_modtimes[section][f] - od_modtimes[section][f] > 3:
                            sys.stderr.write("Considering " + text_type(f) + " is in OneDrive but local is more recent\n")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0:
                                sys.stderr.write("Found zero byte file during update: " + text_type(the_path) + "\n")
                                continue
                            commentary += "Updated " + text_type(f) + " on OneDrive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            sys.stderr.write("Updating on OneDrive and setting OD modtime on modified " + text_type(f) + " to " + text_type(the_modtime) + "\n")
                            data = dict()
                            data['name'] = f
                            data['description'] = ''
                            data["fileSystemInfo"] = { "createdDateTime": iso_from_epoch(od_createtimes[section][f]), "lastModifiedDateTime": the_modtime }
                            #data["fileSystemInfo"] = { "createdDateTime": od_createtimes[section][f], "lastAccessedDateTime": the_modtime, "lastModifiedDateTime": the_modtime }
                            #data["@microsoft.graph.conflictBehavior"] = "replace"
                            result = onedrive_upload(http, subdirs[section], section, data, the_path, new_item_id=od_ids[section][f])
                            if isinstance(result, worker_controller.functions.ReturnValue):
                                return result
                            od_modtimes[section][f] = local_modtimes[section][f]
                            sys.stderr.write("After update, timestamp on OneDrive is " + text_type(od_modtimes[section][f]) + "\n")
                            sys.stderr.write("After update, timestamp on local system is " + text_type(os.path.getmtime(the_path)) + "\n")
                for f in od_deleted[section]:
                    sys.stderr.write("Considering " + text_type(f) + " is deleted on OneDrive\n")
                    if f in local_files[section]:
                        sys.stderr.write("Considering " + text_type(f) + " is deleted on OneDrive but exists locally\n")
                        sys.stderr.write("Local timestamp was " + text_type(local_modtimes[section][f]) + " while timestamp on OneDrive was " + text_type(od_modtimes[section][f]) + "\n")
                        if local_modtimes[section][f] - od_modtimes[section][f] > 3:
                            sys.stderr.write("Considering " + text_type(f) + " is deleted on OneDrive but exists locally and needs to be undeleted on OD\n")
                            commentary += "Undeleted and updated " + text_type(f) + " on OneDrive.\n"
                            the_path = os.path.join(area.directory, f)
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            sys.stderr.write("Setting OD modtime on undeleted file " + text_type(f) + " to " + text_type(the_modtime) + "\n")
                            data = dict()
                            data['name'] = f
                            data['description'] = ''
                            #data["fileSystemInfo"] = { "createdDateTime": od_createtimes[section][f], "lastAccessedDateTime": the_modtime, "lastModifiedDateTime": the_modtime }
                            data["fileSystemInfo"] = { "createdDateTime": iso_from_epoch(od_createtimes[section][f]), "lastModifiedDateTime": the_modtime }
                            #data["@microsoft.graph.conflictBehavior"] = "replace"
                            result = onedrive_upload(http, subdirs[section], section, data, the_path, new_item_id=od_ids[section][f])
                            if isinstance(result, worker_controller.functions.ReturnValue):
                                return result
                            od_modtimes[section][f] = local_modtimes[section][f]
                        else:
                            sys.stderr.write("Considering " + text_type(f) + " is deleted on OneDrive but exists locally and needs to deleted locally\n")
                            sections_modified.add(section)
                            commentary += "Deleted " + text_type(f) + " from Playground.\n"
                            the_path = os.path.join(area.directory, f)
                            if os.path.isfile(the_path):
                                area.delete_file(f)
                for f in os.listdir(area.directory):
                    the_path = os.path.join(area.directory, f)
                    sys.stderr.write("Before finalizing, " + text_type(f) + " has a modtime of " + text_type(os.path.getmtime(the_path)) + "\n")
                area.finalize()
                for f in os.listdir(area.directory):
                    if f not in od_files[section]:
                        continue
                    local_files[section].add(f)
                    the_path = os.path.join(area.directory, f)
                    local_modtimes[section][f] = os.path.getmtime(the_path)
                    sys.stderr.write("After finalizing, " + text_type(f) + " has a modtime of " + text_type(local_modtimes[section][f]) + "\n")
                    if abs(local_modtimes[section][f] - od_modtimes[section][f]) > 3:
                        the_modtime = iso_from_epoch(local_modtimes[section][f])
                        sys.stderr.write("post-finalize: updating OD modtime on file " + text_type(f) + " to " + text_type(the_modtime) + "\n")
                        headers = { 'Content-Type': 'application/json' }
                        r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(od_ids[section][f]), "PATCH", headers=headers, body=json.dumps(dict(fileSystemInfo = { "createdDateTime": iso_from_epoch(od_createtimes[section][f]), "lastModifiedDateTime": the_modtime })))
                        if int(r['status']) != 200:
                            return worker_controller.functions.ReturnValue(ok=False, error="error updating OneDrive file in subfolder " + section + " " + text_type(r['status']) + ": " + content.decode(), restart=False)
                        od_modtimes[section][f] = local_modtimes[section][f]
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
        if PY2:
            return worker_controller.functions.ReturnValue(ok=False, error="Error syncing with OneDrive: " + str(e), restart=False)
        else:
            return worker_controller.functions.ReturnValue(ok=False, error="Error syncing with OneDrive: " + str(e) + str(traceback.format_tb(e.__traceback__)), restart=False)

def onedrive_upload(http, folder_id, folder_name, data, the_path, new_item_id=None):
    headers = { 'Content-Type': 'application/json' }
    if new_item_id is None:
        is_new = True
        #item_data = copy.deepcopy(data)
        #item_data['file'] = dict()
        #the_url = 'https://graph.microsoft.com/v1.0/me/drive/items/' + quote(folder_id) + '/children'
        #r, content = try_request(http, the_url, 'POST', headers=headers, body=json.dumps(item_data))
        #if int(r['status']) != 201:
        #    return worker_controller.functions.ReturnValue(ok=False, error="error creating shell file for OneDrive subfolder " + folder_id + " " + text_type(r['status']) + ": " + text_type(content) + " and url was " + the_url + " and body was " + json.dumps(data), restart=False)
        #new_item_id = json.loads(content)['id']
        #sys.stderr.write("Created shell " + quote(new_item_id) + " with " + repr(item_data) + "\n")
        #the_url = 'https://graph.microsoft.com/v1.0/me/drive/items/' + quote(folder_id) + ':/' + quote(data['name']) + ':/createUploadSession'
    else:
        is_new = False
        #the_url = 'https://graph.microsoft.com/v1.0/me/drive/items/' + quote(new_item_id) + '/createUploadSession'
    the_url = 'https://graph.microsoft.com/v1.0/me/drive/items/' + quote(folder_id) + ':/' + quote(data['name']) + ':/createUploadSession'
    body_data = {"item": {"@microsoft.graph.conflictBehavior": "replace", "description": data['description'], "fileSystemInfo": { "@odata.type": "microsoft.graph.fileSystemInfo" }, "name": data['name']}}
    r, content = try_request(http, the_url, 'POST', headers=headers, body=json.dumps(body_data))
    if int(r['status']) != 200:
        return worker_controller.functions.ReturnValue(ok=False, error="error uploading to OneDrive subfolder " + folder_id + " " + text_type(r['status']) + ": " + content.decode() + " and url was " + the_url + " and folder name was " + folder_name + " and path was " + the_path + " and data was " + repr(data) + " and is_new is " + repr(is_new), restart=False)
    sys.stderr.write("Upload session created.\n")
    upload_url = json.loads(content.decode())["uploadUrl"]
    sys.stderr.write("Upload url obtained.\n")
    total_bytes = os.path.getsize(the_path)
    start_byte = 0
    with open(the_path, 'rb') as fh:
        while start_byte < total_bytes:
            num_bytes = min(ONEDRIVE_CHUNK_SIZE, total_bytes - start_byte)
            custom_headers = { 'Content-Length': text_type(num_bytes), 'Content-Range': 'bytes ' + text_type(start_byte) + '-' + text_type(start_byte + num_bytes - 1) + '/' + text_type(total_bytes), 'Content-Type': 'application/octet-stream' }
            #sys.stderr.write("url is " + repr(upload_url) + " and headers are " + repr(custom_headers) + "\n")
            r, content = try_request(http, upload_url, 'PUT', headers=custom_headers, body=bytes(fh.read(num_bytes)))
            sys.stderr.write("Sent request\n")
            start_byte += num_bytes
            if start_byte == total_bytes:
                sys.stderr.write("Reached end\n")
                if int(r['status']) not in (200, 201):
                    sys.stderr.write("Error1\n")
                    sys.stderr.write(text_type(r['status']) + "\n")
                    sys.stderr.write(content.decode())
                    return worker_controller.functions.ReturnValue(ok=False, error="error uploading file to OneDrive subfolder " + folder_id + " " + text_type(r['status']) + ": " + content.decode(), restart=False)
                if new_item_id is None:
                    new_item_id = json.loads(content.decode())['id']
            else:
                if int(r['status']) != 202:
                    sys.stderr.write("Error2\n")
                    sys.stderr.write(text_type(r['status']) + "\n")
                    sys.stderr.write(content.decode())
                    return worker_controller.functions.ReturnValue(ok=False, error="error during upload of file to OneDrive subfolder " + folder_id + " " + text_type(r['status']) + ": " + content.decode(), restart=False)
                sys.stderr.write("Got 202\n")
    item_data = copy.deepcopy(data)
    if 'fileSystemInfo' in item_data and 'createdDateTime' in item_data['fileSystemInfo']:
        del item_data['fileSystemInfo']['createdDateTime']
    sys.stderr.write("Patching with " + repr(item_data) + " to " + "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id) + " and headers " + repr(headers) + "\n")
    r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id), "PATCH", headers=headers, body=json.dumps(item_data))
    sys.stderr.write("PATCH request sent\n")
    if int(r['status']) != 200:
        return worker_controller.functions.ReturnValue(ok=False, error="error during updating of uploaded file to OneDrive subfolder " + folder_id + " " + text_type(r['status']) + ": " + content.decode(), restart=False)
    # tries = 1
    # start_time = time.time()
    # while tries < 3:
    #     sys.stderr.write("Checking in on results " + "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id) + " at " + text_type(time.time() - start_time) + "\n")
    #     r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id), "GET")
    #     if int(r['status']) != 200:
    #         return worker_controller.functions.ReturnValue(ok=False, error="error during updating of uploaded file to OneDrive subfolder " + folder_id + " " + text_type(r['status']) + ": " + text_type(content), restart=False)
    #     sys.stderr.write("Metadata is now " + text_type(content) + "\n")
    #     time.sleep(5)
    #     tries += 1
    sys.stderr.write("Returning " + text_type(new_item_id) + "\n")
    return new_item_id

@workerapp.task
def ocr_page(**kwargs):
    sys.stderr.write("ocr_page started in worker\n")
    if not hasattr(worker_controller, 'loaded'):
        initialize_db()
    worker_controller.functions.reset_local_variables()
    worker_controller.functions.set_uid(kwargs['user_code'])
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
    worker_controller.functions.reset_local_variables()
    worker_controller.functions.set_uid(user_code)
    with worker_controller.flaskapp.app_context():
        worker_controller.ocr.make_png_for_pdf(doc, prefix, resolution, pdf_to_png, page=page)
    return

@workerapp.task
def reset_server(result):
    sys.stderr.write("reset_server in worker: starting\n")
    if hasattr(result, 'ok') and not result.ok:
        sys.stderr.write("reset_server in worker: not resetting because result did not succeed.\n")
        return result
    if USING_SUPERVISOR:
        if re.search(r':(web|celery|all):', container_role):
            args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'start', 'reset']
            result = call(args)
            sys.stderr.write("reset_server in worker: called " + ' '.join(args) + "\n")
        else:
            sys.stderr.write("reset_server in worker: did not reset due to container role\n")
    else:
        sys.stderr.write("reset_server in worker: supervisor not active, touching WSGI file\n")
        wsgi_file = WEBAPP_PATH
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a'):
                os.utime(wsgi_file, None)
    sys.stderr.write("reset_server in worker: finishing\n")
    return result

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
    worker_controller.functions.reset_local_variables()
    worker_controller.functions.set_uid(user_code)
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
    worker_controller.functions.reset_local_variables()
    worker_controller.functions.set_uid(session_code)
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
            try:
                steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
            except Exception as the_err:
                worker_controller.release_lock(session_code, yaml_filename)
                sys.stderr.write("background_action: could not obtain dictionary because of " + str(the_err.__class__.__name__) + ": " + str(the_err) + "\n")
                return(worker_controller.functions.ReturnValue(extra=extra))
            worker_controller.release_lock(session_code, yaml_filename)
            if user_dict is None:
                sys.stderr.write("background_action: dictionary could not be found\n")
                return(worker_controller.functions.ReturnValue(extra=extra))
            start_time = time.time()
            interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=session_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=is_encrypted, action=action['action'], interface='worker', arguments=action['arguments']))
            old_language = worker_controller.functions.get_language()
            try:
                interview.assemble(user_dict, interview_status)
            except Exception as e:
                if PY2:
                    if hasattr(e, 'traceback'):
                        sys.stderr.write("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
                    else:
                        sys.stderr.write("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e))
                else:
                    if hasattr(e, '__traceback__'):
                        sys.stderr.write("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(traceback.format_tb(e.__traceback__)))
                    else:
                        sys.stderr.write("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e))
                error_type = e.__class__.__name__
                error_message = text_type(e)
                if PY2:
                    if hasattr(e, 'traceback'):
                        error_trace = text_type(e.traceback)
                        if hasattr(e, 'da_line_with_error'):
                            error_trace += "\nIn line: " + text_type(e.da_line_with_error)
                    else:
                        error_trace = None
                else:
                    if hasattr(e, '__traceback__'):
                        error_trace = ''.join(traceback.format_tb(e.__traceback__))
                        if hasattr(e, 'da_line_with_error'):
                            error_trace += "\nIn line: " + text_type(e.da_line_with_error)
                    else:
                        error_trace = None
                variables = list(reversed([y for y in worker_controller.functions.this_thread.current_variable]))
                worker_controller.error_notification(e, message=error_message, trace=error_trace)
                if 'on_error' not in worker_controller.functions.this_thread.current_info:
                    return(worker_controller.functions.ReturnValue(ok=False, error_message=error_message, error_type=error_type, error_trace=error_trace, variables=variables))
                else:
                    sys.stderr.write("Time in background action before error callback was " + str(time.time() - start_time))
                    worker_controller.functions.set_language(old_language)
                    return process_error(interview, session_code, yaml_filename, secret, user_info, url, url_root, is_encrypted, error_type, error_message, error_trace, variables, extra)
            worker_controller.functions.set_language(old_language)
            sys.stderr.write("Time in background action was " + str(time.time() - start_time))
            if not hasattr(interview_status, 'question'):
                #sys.stderr.write("background_action: status had no question\n")
                return(worker_controller.functions.ReturnValue(extra=extra))
            if interview_status.question.question_type in ["restart", "exit", "exit_logout"]:
                #sys.stderr.write("background_action: status was restart or exit\n")
                worker_controller.obtain_lock(session_code, yaml_filename)
                if str(user_info.get('the_user_id', None)).startswith('t'):
                    worker_controller.reset_user_dict(session_code, yaml_filename, temp_user_id=user_info.get('theid', None))
                else:
                    worker_controller.reset_user_dict(session_code, yaml_filename, user_id=user_info.get('theid', None))
                worker_controller.release_lock(session_code, yaml_filename)
            # if interview_status.question.question_type in ["restart", "exit", "logout", "exit_logout", "new_session"]:
            #     #There is no lock to release.  Why is this here?
            #     #worker_controller.release_lock(session_code, yaml_filename)
            #     pass
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
                old_language = worker_controller.functions.get_language()
                try:
                    interview.assemble(user_dict, interview_status)
                    has_error = False
                except Exception as e:
                    if hasattr(e, 'traceback'):
                        sys.stderr.write("Error in assembly during callback: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
                    else:
                        sys.stderr.write("Error in assembly during callback: " + str(e.__class__.__name__) + ": " + str(e))
                    error_type = e.__class__.__name__
                    error_message = text_type(e)
                    if hasattr(e, 'traceback'):
                        error_trace = text_type(e.traceback)
                        if hasattr(e, 'da_line_with_error'):
                            error_trace += "\nIn line: " + text_type(e.da_line_with_error)
                    else:
                        error_trace = None
                    variables = list(reversed([y for y in worker_controller.functions.this_thread.current_variable]))
                    worker_controller.error_notification(e, message=error_message, trace=error_trace)
                    has_error = True
                # is this right?  Save even though there was an error on assembly?
                worker_controller.functions.set_language(old_language)
                save_status = worker_controller.functions.this_thread.misc.get('save_status', 'new')
                if (not has_error) and save_status != 'ignore':
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
                if interview_status.orig_sought != interview_status.sought:
                    sought_message = text_type(interview_status.orig_sought) + " (" + interview_status.sought + ")"
                else:
                    sought_message = text_type(interview_status.orig_sought)
                sys.stderr.write("background_action: The end result of the background action was the seeking of the variable " + sought_message + ", which resulted in asking this question: " + repr(str(interview_status.questionText).strip()) + "\n")
                sys.stderr.write("background_action: Perhaps your interview did not ask all of the questions needed for the background action to do its work.")
                sys.stderr.write("background_action: Or perhaps your background action did its job, but you did not end it with a call to background_response().")
                error_type = 'QuestionError'
                error_trace = None
                error_message = interview_status.questionText
                variables = list(reversed([y for y in worker_controller.functions.this_thread.current_variable]))
                worker_controller.error_notification(Exception("The end result of the background action was the seeking of the variable " + sought_message + ", which resulted in asking this question: " + repr(str(interview_status.questionText).strip())))
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
    old_language = worker_controller.functions.get_language()
    try:
        interview.assemble(user_dict, interview_status)
    except Exception as e:
        if hasattr(e, 'traceback'):
            sys.stderr.write("Error in assembly during error callback: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
        else:
            sys.stderr.write("Error in assembly during error callback: " + str(e.__class__.__name__) + ": " + str(e))
        error_type = e.__class__.__name__
        error_message = text_type(e)
        if hasattr(e, 'traceback'):
            error_trace = text_type(e.traceback)
            if hasattr(e, 'da_line_with_error'):
                error_trace += "\nIn line: " + text_type(e.da_line_with_error)
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
