import copy
import datetime
import json
import os
import re
import subprocess
import sys
import time
import traceback
from urllib.parse import quote
import httplib2
import iso8601
import oauth2client.client
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig, hostname
from docassemble.base.error import DAError
from docassemble.webapp.files import SavedFile
from docassemble.webapp.worker_common import worker_controller, workerapp, process_error, error_object


USING_SUPERVISOR = bool(os.environ.get('SUPERVISOR_SERVER_URL', None))

WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
CONTAINER_ROLE = ':' + os.environ.get('CONTAINERROLE', '') + ':'

ONEDRIVE_CHUNK_SIZE = 2000000

SUPERVISORCTL = [daconfig.get('supervisorctl', 'supervisorctl')]
if daconfig['supervisor'].get('username', None):
    SUPERVISORCTL.extend(['--username', daconfig['supervisor']['username'], '--password', daconfig['supervisor']['password']])


class RedisCredStorage(oauth2client.client.Storage):

    def __init__(self, r, user_id, oauth_app='googledrive'):
        self.r = r
        self.key = 'da:' + oauth_app + ':userid:' + str(user_id)
        self.lockkey = 'da:' + oauth_app + ':lock:userid:' + str(user_id)
        super().__init__()

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
                logmessage("RedisCredStorage: could not read credentials from " + str(json_creds))
        return creds

    def locked_put(self, credentials):
        self.r.set(self.key, credentials.to_json())

    def locked_delete(self):
        self.r.delete(self.key)


def ensure_directories(the_path):
    the_dir = os.path.dirname(the_path)
    os.makedirs(the_dir, exist_ok=True)


@workerapp.task
def sync_with_google_drive(user_id):
    logmessage("sync_with_google_drive: starting")
    worker_controller.initialize()
    logmessage("sync_with_google_drive: continuing")
    storage = RedisCredStorage(worker_controller.r, user_id, oauth_app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage("sync_with_google_drive: credentials failed")
        return worker_controller.functions.ReturnValue(ok=False, error="credentials expired", restart=False)
    try:
        with worker_controller.flaskapp.app_context():
            http = credentials.authorize(httplib2.Http())
            service = worker_controller.apiclient.discovery.build('drive', 'v3', http=http)
            key = 'da:googledrive:mapping:userid:' + str(user_id)
            the_folder = worker_controller.r.get(key)
            if the_folder is None:
                raise DAError("Please go to your profile and set up Google Drive synchronization again.")
            the_folder = the_folder.decode()
            response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()
            the_mime_type = response.get('mimeType', None)
            trashed = response.get('trashed', False)
            if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
                return worker_controller.functions.ReturnValue(ok=False, error="error accessing Google Drive", restart=False)
            local_files = {}
            local_modtimes = {}
            gd_files = {}
            gd_dirlist = {}
            gd_ids = {}
            gd_modtimes = {}
            gd_deleted = {}
            gd_zero = {}
            sections_modified = set()
            commentary = ''
            for section in ['static', 'templates', 'questions', 'modules', 'sources', 'packages']:
                local_files[section] = set()
                local_modtimes[section] = {}
                if section == 'questions':
                    the_section = 'playground'
                elif section == 'templates':
                    the_section = 'playgroundtemplate'
                else:
                    the_section = 'playground' + section
                area = SavedFile(user_id, fix=True, section=the_section)
                for f in area.list_of_files():
                    local_files[section].add(f)
                    local_modtimes[section][f] = os.path.getmtime(os.path.join(area.directory, f))
                subdirs = []
                page_token = None
                while True:
                    param = {'spaces': 'drive', 'fields': 'nextPageToken, files(id, name)', 'q': "mimeType: 'application/vnd.google-apps.folder' and trashed=false and name='" + section + "' and '" + str(the_folder) + "' in parents"}
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
                    file_metadata = {
                        'name': section,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [the_folder]
                    }
                    new_dir = service.files().create(body=file_metadata,
                                                     fields='id').execute()
                    new_id = new_dir.get('id', None)
                    if new_id is None:
                        return worker_controller.functions.ReturnValue(ok=False, error="error accessing " + section + " in Google Drive", restart=False)
                    subdirs.append(new_id)
                if len(subdirs) == 0:
                    return worker_controller.functions.ReturnValue(ok=False, error="error accessing " + section + " in Google Drive", restart=False)
                subdir = subdirs[0]
                gd_files[section] = set()
                gd_dirlist[section] = {}
                gd_ids[section] = {}
                gd_modtimes[section] = {}
                gd_deleted[section] = set()
                gd_zero[section] = set()
                page_token = None
                while True:
                    param = {'spaces': "drive", 'fields': "nextPageToken, files(id, mimeType, name, modifiedTime, trashed, size)", 'q': "'" + str(subdir) + "' in parents"}
                    if page_token is not None:
                        param['pageToken'] = page_token
                    response = service.files().list(**param).execute()
                    for the_file in response.get('files', []):
                        logmessage("GD found " + the_file['name'])
                        if the_file['mimeType'] == 'application/vnd.google-apps.folder':
                            # logmessage("sync_with_google_drive: found a folder " + repr(the_file))
                            gd_dirlist[section][the_file['name']] = the_file['id']
                            continue
                        if re.search(r'(\.tmp|\.gdoc|\#)$', the_file['name']):
                            continue
                        if re.search(r'^(\~)', the_file['name']):
                            continue
                        if 'size' not in the_file:
                            continue
                        gd_ids[section][the_file['name']] = the_file['id']
                        gd_modtimes[section][the_file['name']] = epoch_from_iso(the_file['modifiedTime'])
                        if int(the_file['size']) == 0:
                            gd_zero[section].add(the_file['name'])
                        logmessage("Google says modtime on " + str(the_file['name']) + " is " + str(the_file['modifiedTime']) + ", which is " + str(gd_modtimes[section][the_file['name']]))
                        if the_file['trashed']:
                            gd_deleted[section].add(the_file['name'])
                            continue
                        gd_files[section].add(the_file['name'])
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                for subdir_name, subdir_id in gd_dirlist[section].items():
                    page_token = None
                    while True:
                        param = {'spaces': "drive", 'fields': "nextPageToken, files(id, name, modifiedTime, trashed, size)", 'q': "mimeType!='application/vnd.google-apps.folder' and '" + str(subdir_id) + "' in parents"}
                        if page_token is not None:
                            param['pageToken'] = page_token
                        response = service.files().list(**param).execute()
                        for the_file in response.get('files', []):
                            logmessage("GD found " + the_file['name'] + " in subdir " + subdir_name)
                            if re.search(r'(\.tmp|\.gdoc|\#)$', the_file['name']):
                                continue
                            if re.search(r'^(\~)', the_file['name']):
                                continue
                            if 'size' not in the_file:
                                continue
                            path_name = os.path.join(subdir_name, the_file['name'])
                            gd_ids[section][path_name] = the_file['id']
                            gd_modtimes[section][path_name] = epoch_from_iso(the_file['modifiedTime'])
                            if int(the_file['size']) == 0:
                                gd_zero[section].add(path_name)
                            logmessage("Google says modtime on " + str(path_name) + " is " + str(the_file['modifiedTime']) + ", which is " + str(gd_modtimes[section][path_name]))
                            if the_file['trashed']:
                                gd_deleted[section].add(path_name)
                                continue
                            gd_files[section].add(path_name)
                        page_token = response.get('nextPageToken', None)
                        if page_token is None:
                            break
                gd_deleted[section] = gd_deleted[section] - gd_files[section]
                for f in gd_files[section]:
                    logmessage("Considering " + str(f) + " on GD")
                    if f in local_files[section]:
                        logmessage("Local timestamp was " + str(local_modtimes[section][f]) + " while timestamp on Google Drive was " + str(gd_modtimes[section][f]))
                    if f not in local_files[section] or gd_modtimes[section][f] - local_modtimes[section][f] > 3:
                        logmessage("Going to copy " + str(f) + " from Google Drive to local")
                        sections_modified.add(section)
                        commentary += "Copied " + str(f) + " from Google Drive.\n"
                        the_path = os.path.join(area.directory, f)
                        ensure_directories(the_path)
                        if f in gd_zero[section]:
                            with open(the_path, 'a', encoding='utf-8'):
                                os.utime(the_path, (gd_modtimes[section][f], gd_modtimes[section][f]))
                        else:
                            with open(the_path, 'wb') as fh:
                                response = service.files().get_media(fileId=gd_ids[section][f])
                                downloader = worker_controller.apiclient.http.MediaIoBaseDownload(fh, response)
                                done = False
                                while done is False:
                                    status, done = downloader.next_chunk()  # pylint: disable=unused-variable
                                    # logmessage("Download %d%%." % int(status.progress() * 100))
                            os.utime(the_path, (gd_modtimes[section][f], gd_modtimes[section][f]))
                for f in local_files[section]:
                    logmessage("Considering " + str(f) + ", which is a local file")
                    if f in gd_files[section]:
                        logmessage("Local timestamp was " + str(local_modtimes[section][f]) + " while timestamp on Google Drive was " + str(gd_modtimes[section][f]))
                    if f not in gd_deleted[section]:
                        logmessage("Considering " + str(f) + " is not in Google Drive deleted")
                        if f not in gd_files[section]:
                            logmessage("Considering " + str(f) + " is not in Google Drive")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0 and not the_path.endswith('.placeholder'):
                                logmessage("Found zero byte file: " + str(the_path))
                                continue
                            logmessage("Copying " + str(f) + " to Google Drive.")
                            if not the_path.endswith('.placeholder'):
                                commentary += "Copied " + str(f) + " to Google Drive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)  # pylint: disable=unused-variable
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            logmessage("Setting GD modtime on new file " + str(f) + " to " + str(the_modtime))
                            dir_part, file_part = os.path.split(f)
                            if dir_part != '':
                                if dir_part not in gd_dirlist[section]:
                                    file_metadata = {
                                        'name': dir_part,
                                        'mimeType': 'application/vnd.google-apps.folder',
                                        'parents': [subdir]
                                    }
                                    new_file = service.files().create(body=file_metadata,
                                                                      fields='id').execute()
                                    gd_dirlist[section][dir_part] = new_file.get('id', None)
                                parent_to_use = gd_dirlist[section][dir_part]
                            else:
                                parent_to_use = subdir
                            file_metadata = {'name': file_part, 'parents': [parent_to_use], 'modifiedTime': the_modtime, 'createdTime': the_modtime}
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            the_new_file = service.files().create(body=file_metadata,
                                                                  media_body=media,
                                                                  fields='id').execute()
                            the_new_file.get('id')
                        elif local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                            logmessage("Considering " + str(f) + " is in Google Drive but local is more recent")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0 and not the_path.endswith('.placeholder'):
                                logmessage("Found zero byte file during update: " + str(the_path))
                                continue
                            commentary += "Updated " + str(f) + " on Google Drive.\n"
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            logmessage("Updating on Google Drive and setting GD modtime on modified " + str(f) + " to " + str(the_modtime))
                            file_metadata = {'modifiedTime': the_modtime}
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            updated_file = service.files().update(fileId=gd_ids[section][f],
                                                                  body=file_metadata,
                                                                  media_body=media,
                                                                  fields='modifiedTime').execute()
                            gd_modtimes[section][f] = epoch_from_iso(updated_file['modifiedTime'])
                            logmessage("After update, timestamp on Google Drive is " + str(gd_modtimes[section][f]))
                            logmessage("After update, timestamp on local system is " + str(os.path.getmtime(the_path)))
                for f in gd_deleted[section]:
                    logmessage("Considering " + str(f) + " is deleted on Google Drive")
                    if f in local_files[section]:
                        logmessage("Considering " + str(f) + " is deleted on Google Drive but exists locally")
                        logmessage("Local timestamp was " + str(local_modtimes[section][f]) + " while timestamp on Google Drive was " + str(gd_modtimes[section][f]))
                        if local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                            logmessage("Considering " + str(f) + " is deleted on Google Drive but exists locally and needs to be undeleted on GD")
                            commentary += "Undeleted and updated " + str(f) + " on Google Drive.\n"
                            the_path = os.path.join(area.directory, f)
                            extension, mimetype = worker_controller.get_ext_and_mimetype(the_path)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            logmessage("Setting GD modtime on undeleted file " + str(f) + " to " + str(the_modtime))
                            file_metadata = {'modifiedTime': the_modtime, 'trashed': False}
                            media = worker_controller.apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                            updated_file = service.files().update(fileId=gd_ids[section][f],
                                                                  body=file_metadata,
                                                                  media_body=media,
                                                                  fields='modifiedTime').execute()
                            gd_modtimes[section][f] = epoch_from_iso(updated_file['modifiedTime'])
                        else:
                            logmessage("Considering " + str(f) + " is deleted on Google Drive but exists locally and needs to deleted locally")
                            sections_modified.add(section)
                            commentary += "Deleted " + str(f) + " from Playground.\n"
                            the_path = os.path.join(area.directory, f)
                            if os.path.isfile(the_path):
                                area.delete_file(f)
                for f in os.listdir(area.directory):
                    the_path = os.path.join(area.directory, f)
                    logmessage("Before finalizing, " + str(f) + " has a modtime of " + str(os.path.getmtime(the_path)))
                area.finalize()
                for f in os.listdir(area.directory):
                    if f not in gd_files[section]:
                        continue
                    local_files[section].add(f)
                    the_path = os.path.join(area.directory, f)
                    local_modtimes[section][f] = os.path.getmtime(the_path)
                    logmessage("After finalizing, " + str(f) + " has a modtime of " + str(local_modtimes[section][f]))
                    if abs(local_modtimes[section][f] - gd_modtimes[section][f]) > 3:
                        the_modtime = iso_from_epoch(local_modtimes[section][f])
                        logmessage("post-finalize: updating GD modtime on file " + str(f) + " to " + str(the_modtime))
                        file_metadata = {'modifiedTime': the_modtime}
                        updated_file = service.files().update(fileId=gd_ids[section][f],
                                                              body=file_metadata,
                                                              fields='modifiedTime').execute()
                        gd_modtimes[section][f] = epoch_from_iso(updated_file['modifiedTime'])
            for key in worker_controller.r.keys('da:interviewsource:docassemble.playground' + str(user_id) + ':*'):
                worker_controller.r.incr(key)
            if commentary != '':
                logmessage(commentary)
        do_restart = bool('modules' in sections_modified)
        return worker_controller.functions.ReturnValue(ok=True, summary=commentary, restart=do_restart)
    except DAError as e:
        return worker_controller.functions.ReturnValue(ok=False, error=str(e), restart=False)
    except BaseException as e:
        return worker_controller.functions.ReturnValue(ok=False, error="Error syncing with Google Drive: " + worker_controller.noquote(str(e)), restart=False)


def try_request(*pargs, **kwargs):
    start_time = time.time()
    args = list(pargs)
    http = args.pop(0)
    tries = 1
    while tries < 5:
        r, content = http.request(*args, **kwargs)
        if int(r['status']) != 504:
            break
        logmessage("Got a 504 after try " + str(tries))
        time.sleep(2*tries)
        tries += 1
    logmessage("try_request: duration was %.2f seconds" % (time.time() - start_time, ))
    return r, content


def epoch_from_iso(datestring):
    return (iso8601.parse_date(datestring) - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()


def iso_from_epoch(seconds):
    return datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc).isoformat().replace('+00:00', 'Z')


@workerapp.task
def sync_with_onedrive(user_id):
    logmessage("sync_with_onedrive: starting")
    worker_controller.initialize()
    logmessage("sync_with_onedrive: continuing")
    storage = RedisCredStorage(worker_controller.r, user_id, oauth_app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage("sync_with_onedrive: credentials failed")
        return worker_controller.functions.ReturnValue(ok=False, error="credentials expired", restart=False)
    try:
        with worker_controller.flaskapp.app_context():
            http = credentials.authorize(httplib2.Http())
            # r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive", "GET")
            # drive_id = json.loads(content)['id']
            # r, content = try_request(http, "https://graph.microsoft.com/v1.0/drive/special/approot")
            # if int(r['status']) != 200:
            #     return worker_controller.functions.ReturnValue(ok=False, error="Could not verify application root", restart=False)
            key = 'da:onedrive:mapping:userid:' + str(user_id)
            the_folder = worker_controller.r.get(key)
            if the_folder is None:
                raise DAError("Please go to your profile and set up OneDrive synchronization again.")
            the_folder = the_folder.decode()
            r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(the_folder), "GET")
            if int(r['status']) != 200:
                trashed = True
            else:
                info = json.loads(content.decode())
                trashed = bool('deleted' in info)
            if trashed is True:
                logmessage('trash_gd_file: folder did not exist')
                return False
            if trashed is True or 'folder' not in info:
                return worker_controller.functions.ReturnValue(ok=False, error="error accessing OneDrive", restart=False)
            local_files = {}
            local_modtimes = {}
            od_files = {}
            od_dirlist = {}
            od_ids = {}
            od_modtimes = {}
            od_createtimes = {}
            od_deleted = {}
            od_zero = {}
            sections_modified = set()
            commentary = ''
            subdirs = {}
            subdir_count = {}
            r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
            while True:
                if int(r['status']) != 200:
                    return worker_controller.functions.ReturnValue(ok=False, error="error accessing OneDrive subfolders", restart=False)
                info = json.loads(content.decode())
                for item in info['value']:
                    if 'deleted' in item or 'folder' not in item:
                        continue
                    if item['name'] in ('static', 'templates', 'questions', 'modules', 'sources', 'packages'):
                        subdirs[item['name']] = item['id']
                        subdir_count[item['name']] = item['folder']['childCount']
                if "@odata.nextLink" not in info:
                    break
                r, content = try_request(http, info["@odata.nextLink"], "GET")
            for section in ['static', 'templates', 'questions', 'modules', 'sources', 'packages']:
                logmessage("sync_with_onedrive: processing " + section)
                if section not in subdirs:
                    headers = {'Content-Type': 'application/json'}
                    data = {}
                    data['name'] = section
                    data['folder'] = {}
                    data["@microsoft.graph.conflictBehavior"] = "rename"
                    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(the_folder) + "/children", "POST", headers=headers, body=json.dumps(data))
                    if int(resp['status']) != 201:
                        worker_controller.functions.ReturnValue(ok=False, error="error accessing " + section + " in OneDrive", restart=False)
                    new_item = json.loads(content.decode())
                    subdirs[section] = new_item['id']
                    subdir_count[section] = 0
                if section not in subdirs:
                    worker_controller.functions.ReturnValue(ok=False, error="error accessing " + section + " in OneDrive", restart=False)
                local_files[section] = set()
                local_modtimes[section] = {}
                if section == 'questions':
                    the_section = 'playground'
                elif section == 'templates':
                    the_section = 'playgroundtemplate'
                else:
                    the_section = 'playground' + section
                area = SavedFile(user_id, fix=True, section=the_section)
                for f in area.list_of_files():
                    local_files[section].add(f)
                    local_modtimes[section][f] = os.path.getmtime(os.path.join(area.directory, f))
                od_files[section] = set()
                od_ids[section] = {}
                od_modtimes[section] = {}
                od_createtimes[section] = {}
                od_deleted[section] = set()
                od_zero[section] = set()
                od_dirlist[section] = {}
                if subdir_count[section] == 0:
                    logmessage("sync_with_onedrive: skipping " + section + " because empty on remote")
                else:
                    r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(subdirs[section]) + "/children?$select=id,name,deleted,fileSystemInfo,folder,size", "GET")
                    logmessage("sync_with_onedrive: processing " + section + ", which is " + str(subdirs[section]))
                    while True:
                        if int(r['status']) != 200:
                            return worker_controller.functions.ReturnValue(ok=False, error="error accessing OneDrive subfolder " + section + " " + str(r['status']) + ": " + content.decode() + " looking for " + str(subdirs[section]), restart=False)
                        info = json.loads(content.decode())
                        # logmessage("sync_with_onedrive: result was " + repr(info))
                        for the_file in info['value']:
                            if 'folder' in the_file:
                                # logmessage("sync_with_onedrive: found a folder " + repr(the_file))
                                od_dirlist[section][the_file['name']] = the_file['id']
                                continue
                            # logmessage("sync_with_onedrive: found a file " + repr(the_file))
                            if re.search(r'^(\~)', the_file['name']):
                                continue
                            od_ids[section][the_file['name']] = the_file['id']
                            od_modtimes[section][the_file['name']] = epoch_from_iso(the_file['fileSystemInfo']['lastModifiedDateTime'])
                            od_createtimes[section][the_file['name']] = epoch_from_iso(the_file['fileSystemInfo']['createdDateTime'])
                            if the_file['size'] == 0:
                                od_zero[section].add(the_file['name'])
                            logmessage("OneDrive says modtime on " + str(the_file['name']) + " in " + section + " is " + str(the_file['fileSystemInfo']['lastModifiedDateTime']) + ", which is " + str(od_modtimes[section][the_file['name']]))
                            if the_file.get('deleted', None):
                                od_deleted[section].add(the_file['name'])
                                continue
                            od_files[section].add(the_file['name'])
                        if "@odata.nextLink" not in info:
                            break
                        r, content = try_request(http, info["@odata.nextLink"], "GET")
                    for subdir_name, subdir_id in od_dirlist[section].items():
                        r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(subdir_id) + "/children?$select=id,name,deleted,fileSystemInfo,folder,size", "GET")
                        logmessage("sync_with_onedrive: processing " + section + " subdir " + subdir_name + ", which is " + str(subdir_id))
                        while True:
                            if int(r['status']) != 200:
                                return worker_controller.functions.ReturnValue(ok=False, error="error accessing OneDrive subfolder " + section + " subdir " + subdir_name + " " + str(r['status']) + ": " + content.decode() + " looking for " + str(subdir_id), restart=False)
                            info = json.loads(content.decode())
                            for the_file in info['value']:
                                if 'folder' in the_file:
                                    continue
                                # logmessage("sync_with_onedrive: found a file " + repr(the_file))
                                if re.search(r'^(\~)', the_file['name']):
                                    continue
                                path_name = os.path.join(subdir_name, the_file['name'])
                                od_ids[section][path_name] = the_file['id']
                                od_modtimes[section][path_name] = epoch_from_iso(the_file['fileSystemInfo']['lastModifiedDateTime'])
                                od_createtimes[section][path_name] = epoch_from_iso(the_file['fileSystemInfo']['createdDateTime'])
                                if the_file['size'] == 0:
                                    od_zero[section].add(path_name)
                                logmessage("OneDrive says modtime on " + str(path_name) + " in " + section + " is " + str(the_file['fileSystemInfo']['lastModifiedDateTime']) + ", which is " + str(od_modtimes[section][path_name]))
                                if the_file.get('deleted', None):
                                    od_deleted[section].add(path_name)
                                    continue
                                od_files[section].add(path_name)
                            if "@odata.nextLink" not in info:
                                break
                            r, content = try_request(http, info["@odata.nextLink"], "GET")
                od_deleted[section] = od_deleted[section] - od_files[section]
                for f in od_files[section]:
                    logmessage("Considering " + str(f) + " on OD")
                    if f in local_files[section]:
                        logmessage("Local timestamp was " + str(local_modtimes[section][f]) + " while timestamp on OneDrive was " + str(od_modtimes[section][f]))
                    if f not in local_files[section] or od_modtimes[section][f] - local_modtimes[section][f] > 3:
                        logmessage("Going to copy " + str(f) + " from OneDrive to local")
                        sections_modified.add(section)
                        commentary += "Copied " + str(f) + " from OneDrive.\n"
                        the_path = os.path.join(area.directory, f)
                        ensure_directories(the_path)
                        if f in od_zero[section]:
                            with open(the_path, 'a', encoding='utf-8'):
                                os.utime(the_path, (od_modtimes[section][f], od_modtimes[section][f]))
                        else:
                            r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(od_ids[section][f]) + "/content", "GET")
                            with open(the_path, 'wb') as fh:
                                fh.write(content)
                            os.utime(the_path, (od_modtimes[section][f], od_modtimes[section][f]))
                for f in local_files[section]:
                    logmessage("Considering " + str(f) + ", which is a local file")
                    if f in od_files[section]:
                        logmessage("Local timestamp was " + str(local_modtimes[section][f]) + " while timestamp on OneDrive was " + str(od_modtimes[section][f]))
                    if f not in od_deleted[section]:
                        logmessage("Considering " + str(f) + " is not in OneDrive deleted")
                        if f not in od_files[section]:
                            logmessage("Considering " + str(f) + " is not in OneDrive")
                            the_path = os.path.join(area.directory, f)
                            dir_name = os.path.dirname(f)
                            base_name = os.path.basename(f)
                            if os.path.getsize(the_path) == 0 and not the_path.endswith('.placeholder'):
                                logmessage("Found zero byte file: " + str(the_path))
                                continue
                            logmessage("Copying " + str(f) + " to OneDrive.")
                            if not the_path.endswith('.placeholder'):
                                commentary += "Copied " + str(f) + " to OneDrive.\n"
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            logmessage("Setting OD modtime on new file " + str(f) + " to " + str(the_modtime) + " which is " + str(local_modtimes[section][f]))
                            data = {}
                            data['name'] = base_name
                            data['description'] = ''
                            data["fileSystemInfo"] = {"createdDateTime": the_modtime, "lastModifiedDateTime": the_modtime}
                            # data["fileSystemInfo"] = { "createdDateTime": the_modtime, "lastAccessedDateTime": the_modtime, "lastModifiedDateTime": the_modtime }
                            # data["@microsoft.graph.conflictBehavior"] = "replace"
                            if dir_name != '':
                                if dir_name not in od_dirlist[section]:
                                    headers = {'Content-Type': 'application/json'}
                                    dirdata = {}
                                    dirdata['name'] = dir_name
                                    dirdata['folder'] = {}
                                    dirdata["@microsoft.graph.conflictBehavior"] = "rename"
                                    r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(subdirs[section]) + "/children", "POST", headers=headers, body=json.dumps(dirdata))
                                    if int(r['status']) != 201:
                                        raise DAError("sync_with_onedrive: could not create subfolder " + dir_name + ' in ' + str(subdirs[section]) + '.  ' + content.decode() + ' status: ' + str(r['status']))
                                    new_item = json.loads(content.decode())
                                    od_dirlist[section][dir_name] = new_item['id']
                                result = onedrive_upload(http, od_dirlist[section][dir_name], dir_name, data, the_path)
                            else:
                                result = onedrive_upload(http, subdirs[section], section, data, the_path)
                            if isinstance(result, worker_controller.functions.ReturnValue):
                                return result
                            od_files[section].add(f)
                            od_ids[section][f] = result
                            od_modtimes[section][f] = local_modtimes[section][f]
                            od_createtimes[section][f] = local_modtimes[section][f]
                        elif local_modtimes[section][f] - od_modtimes[section][f] > 3:
                            logmessage("Considering " + str(f) + " is in OneDrive but local is more recent")
                            the_path = os.path.join(area.directory, f)
                            if os.path.getsize(the_path) == 0 and not the_path.endswith('.placeholder'):
                                logmessage("Found zero byte file during update: " + str(the_path))
                                continue
                            commentary += "Updated " + str(f) + " on OneDrive.\n"
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            logmessage("Updating on OneDrive and setting OD modtime on modified " + str(f) + " to " + str(the_modtime))
                            data = {}
                            data['name'] = f
                            data['description'] = ''
                            data["fileSystemInfo"] = {"createdDateTime": iso_from_epoch(od_createtimes[section][f]), "lastModifiedDateTime": the_modtime}
                            # data["fileSystemInfo"] = {"createdDateTime": od_createtimes[section][f], "lastAccessedDateTime": the_modtime, "lastModifiedDateTime": the_modtime}
                            # data["@microsoft.graph.conflictBehavior"] = "replace"
                            result = onedrive_upload(http, subdirs[section], section, data, the_path, new_item_id=od_ids[section][f])
                            if isinstance(result, worker_controller.functions.ReturnValue):
                                return result
                            od_modtimes[section][f] = local_modtimes[section][f]
                            logmessage("After update, timestamp on OneDrive is " + str(od_modtimes[section][f]))
                            logmessage("After update, timestamp on local system is " + str(os.path.getmtime(the_path)))
                for f in od_deleted[section]:
                    logmessage("Considering " + str(f) + " is deleted on OneDrive")
                    if f in local_files[section]:
                        logmessage("Considering " + str(f) + " is deleted on OneDrive but exists locally")
                        logmessage("Local timestamp was " + str(local_modtimes[section][f]) + " while timestamp on OneDrive was " + str(od_modtimes[section][f]))
                        if local_modtimes[section][f] - od_modtimes[section][f] > 3:
                            logmessage("Considering " + str(f) + " is deleted on OneDrive but exists locally and needs to be undeleted on OD")
                            commentary += "Undeleted and updated " + str(f) + " on OneDrive.\n"
                            the_path = os.path.join(area.directory, f)
                            the_modtime = iso_from_epoch(local_modtimes[section][f])
                            logmessage("Setting OD modtime on undeleted file " + str(f) + " to " + str(the_modtime))
                            data = {}
                            data['name'] = f
                            data['description'] = ''
                            # data["fileSystemInfo"] = {"createdDateTime": od_createtimes[section][f], "lastAccessedDateTime": the_modtime, "lastModifiedDateTime": the_modtime}
                            data["fileSystemInfo"] = {"createdDateTime": iso_from_epoch(od_createtimes[section][f]), "lastModifiedDateTime": the_modtime}
                            # data["@microsoft.graph.conflictBehavior"] = "replace"
                            result = onedrive_upload(http, subdirs[section], section, data, the_path, new_item_id=od_ids[section][f])
                            if isinstance(result, worker_controller.functions.ReturnValue):
                                return result
                            od_modtimes[section][f] = local_modtimes[section][f]
                        else:
                            logmessage("Considering " + str(f) + " is deleted on OneDrive but exists locally and needs to deleted locally")
                            sections_modified.add(section)
                            commentary += "Deleted " + str(f) + " from Playground.\n"
                            the_path = os.path.join(area.directory, f)
                            if os.path.isfile(the_path):
                                area.delete_file(f)
                for f in os.listdir(area.directory):
                    the_path = os.path.join(area.directory, f)
                    logmessage("Before finalizing, " + str(f) + " has a modtime of " + str(os.path.getmtime(the_path)))
                area.finalize()
                for f in os.listdir(area.directory):
                    if f not in od_files[section]:
                        continue
                    local_files[section].add(f)
                    the_path = os.path.join(area.directory, f)
                    local_modtimes[section][f] = os.path.getmtime(the_path)
                    logmessage("After finalizing, " + str(f) + " has a modtime of " + str(local_modtimes[section][f]))
                    if abs(local_modtimes[section][f] - od_modtimes[section][f]) > 3:
                        the_modtime = iso_from_epoch(local_modtimes[section][f])
                        logmessage("post-finalize: updating OD modtime on file " + str(f) + " to " + str(the_modtime))
                        headers = {'Content-Type': 'application/json'}
                        r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(od_ids[section][f]), "PATCH", headers=headers, body=json.dumps({'fileSystemInfo': {"createdDateTime": iso_from_epoch(od_createtimes[section][f]), "lastModifiedDateTime": the_modtime}}, sort_keys=True))
                        if int(r['status']) != 200:
                            return worker_controller.functions.ReturnValue(ok=False, error="error updating OneDrive file in subfolder " + section + " " + str(r['status']) + ": " + content.decode(), restart=False)
                        od_modtimes[section][f] = local_modtimes[section][f]
            for key in worker_controller.r.keys('da:interviewsource:docassemble.playground' + str(user_id) + ':*'):
                worker_controller.r.incr(key)
            if commentary != '':
                logmessage(commentary)
        do_restart = bool('modules' in sections_modified)
        return worker_controller.functions.ReturnValue(ok=True, summary=commentary, restart=do_restart)
    except DAError as e:
        return worker_controller.functions.ReturnValue(ok=False, error=str(e), restart=False)
    except BaseException as e:
        return worker_controller.functions.ReturnValue(ok=False, error="Error syncing with OneDrive: " + str(e) + str(traceback.format_tb(e.__traceback__)), restart=False)


def onedrive_upload(http, folder_id, folder_name, data, the_path, new_item_id=None):
    headers = {'Content-Type': 'application/json'}
    is_new = bool(new_item_id is None)
    total_bytes = os.path.getsize(the_path)
    if total_bytes == 0:
        r, content = try_request(http, 'https://graph.microsoft.com/v1.0/me/drive/items/' + quote(folder_id) + ':/' + quote(data['name']) + ':/content', 'PUT', headers={'Content-Type': 'text/plain'}, body=bytes())
        if int(r['status']) not in (200, 201):
            logmessage("Error0")
            logmessage(str(r['status']))
            logmessage(content.decode())
            return worker_controller.functions.ReturnValue(ok=False, error="error uploading zero-byte file to OneDrive subfolder " + folder_id + " " + str(r['status']) + ": " + content.decode(), restart=False)
        if new_item_id is None:
            new_item_id = json.loads(content.decode())['id']
    else:
        the_url = 'https://graph.microsoft.com/v1.0/me/drive/items/' + quote(folder_id) + ':/' + quote(data['name']) + ':/createUploadSession'
        body_data = {"item": {"@microsoft.graph.conflictBehavior": "replace"}}
        r, content = try_request(http, the_url, 'POST', headers=headers, body=json.dumps(body_data, sort_keys=True))
        if int(r['status']) != 200:
            return worker_controller.functions.ReturnValue(ok=False, error="error uploading to OneDrive subfolder " + folder_id + " " + str(r['status']) + ": " + content.decode() + " and url was " + the_url + " and folder name was " + folder_name + " and path was " + the_path + " and data was " + json.dumps(body_data, sort_keys=True) + " and is_new is " + repr(is_new), restart=False)
        logmessage("Upload session created.")
        upload_url = json.loads(content.decode())["uploadUrl"]
        logmessage("Upload url obtained.")
        start_byte = 0
        with open(the_path, 'rb') as fh:
            while start_byte < total_bytes:
                num_bytes = min(ONEDRIVE_CHUNK_SIZE, total_bytes - start_byte)
                custom_headers = {'Content-Length': str(num_bytes), 'Content-Range': 'bytes ' + str(start_byte) + '-' + str(start_byte + num_bytes - 1) + '/' + str(total_bytes), 'Content-Type': 'application/octet-stream'}
                # logmessage("url is " + repr(upload_url) + " and headers are " + repr(custom_headers))
                r, content = try_request(http, upload_url, 'PUT', headers=custom_headers, body=bytes(fh.read(num_bytes)))
                logmessage("Sent request")
                start_byte += num_bytes
                if start_byte == total_bytes:
                    logmessage("Reached end")
                    if int(r['status']) not in (200, 201):
                        logmessage("Error1")
                        logmessage(str(r['status']))
                        logmessage(content.decode())
                        return worker_controller.functions.ReturnValue(ok=False, error="error uploading file to OneDrive subfolder " + folder_id + " " + str(r['status']) + ": " + content.decode(), restart=False)
                    if new_item_id is None:
                        new_item_id = json.loads(content.decode())['id']
                else:
                    if int(r['status']) != 202:
                        logmessage("Error2")
                        logmessage(str(r['status']))
                        logmessage(content.decode())
                        return worker_controller.functions.ReturnValue(ok=False, error="error during upload of file to OneDrive subfolder " + folder_id + " " + str(r['status']) + ": " + content.decode(), restart=False)
                    logmessage("Got 202")
    item_data = copy.deepcopy(data)
    if 'fileSystemInfo' in item_data and 'createdDateTime' in item_data['fileSystemInfo']:
        del item_data['fileSystemInfo']['createdDateTime']
    item_data['name'] = re.sub(r'.*/', '', item_data['name'])
    logmessage("Patching with " + repr(item_data) + " to " + "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id) + " and headers " + repr(headers))
    r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id), "PATCH", headers=headers, body=json.dumps(item_data, sort_keys=True))
    logmessage("PATCH request sent")
    if int(r['status']) != 200:
        return worker_controller.functions.ReturnValue(ok=False, error="error during updating of uploaded file to OneDrive subfolder " + folder_id + " " + str(r['status']) + ": " + content.decode(), restart=False)
    # tries = 1
    # start_time = time.time()
    # while tries < 3:
    #     logmessage("Checking in on results " + "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id) + " at " + str(time.time() - start_time))
    #     r, content = try_request(http, "https://graph.microsoft.com/v1.0/me/drive/items/" + quote(new_item_id), "GET")
    #     if int(r['status']) != 200:
    #         return worker_controller.functions.ReturnValue(ok=False, error="error during updating of uploaded file to OneDrive subfolder " + folder_id + " " + str(r['status']) + ": " + str(content), restart=False)
    #     logmessage("Metadata is now " + str(content))
    #     time.sleep(5)
    #     tries += 1
    logmessage("Returning " + str(new_item_id))
    return new_item_id


@workerapp.task
def ocr_dummy(doc, indexno, **kwargs):
    logmessage("ocr_dummy started in worker")
    worker_controller.initialize()
    url_root = kwargs.get('url_root', daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/'))
    url = kwargs.get('url', url_root + 'interview')
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url_root, path=url):
            worker_controller.functions.reset_local_variables()
            worker_controller.functions.set_uid(kwargs['user_code'])
            user_info = kwargs['user']
            if not str(user_info['the_user_id']).startswith('t'):
                user_object = worker_controller.get_user_object(user_info['theid'])
                worker_controller.login_user(user_object, remember=False)
            worker_controller.set_request_active(False)
            if doc._is_pdf():
                return worker_controller.functions.ReturnValue(ok=True, value={'indexno': indexno, 'doc': doc})
            return worker_controller.functions.ReturnValue(ok=True, value={'indexno': indexno, 'doc': worker_controller.util.pdf_concatenate(doc)})


@workerapp.task
def ocr_page(indexno, **kwargs):
    logmessage("ocr_page started in worker")
    worker_controller.initialize()
    url_root = kwargs.get('url_root', daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/'))
    url = kwargs.get('url', url_root + 'interview')
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url_root, path=url):
            worker_controller.functions.reset_local_variables()
            worker_controller.functions.set_uid(kwargs['user_code'])
            user_info = kwargs['user']
            if not str(user_info['the_user_id']).startswith('t'):
                user_object = worker_controller.get_user_object(user_info['theid'])
                worker_controller.login_user(user_object, remember=False)
            worker_controller.set_request_active(False)
            return worker_controller.functions.ReturnValue(ok=True, value=worker_controller.util.ocr_page(indexno, **kwargs))


@workerapp.task
def ocr_finalize(*pargs, **kwargs):
    logmessage("ocr_finalize started in worker")
    worker_controller.initialize()
    url_root = kwargs.get('url_root', daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/'))
    url = kwargs.get('url', url_root + 'interview')
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url_root, path=url):
            worker_controller.functions.set_uid(kwargs['user_code'])
            user_info = kwargs['user']
            if not str(user_info['the_user_id']).startswith('t'):
                user_object = worker_controller.get_user_object(user_info['theid'])
                worker_controller.login_user(user_object, remember=False)
            worker_controller.set_request_active(False)
            if 'message' in kwargs and kwargs['message']:
                message = kwargs['message']
            else:
                message = worker_controller.functions.word("OCR succeeded")
            try:
                if kwargs.get('pdf', False):
                    try:
                        (target, dafilelist) = worker_controller.util.ocr_finalize(*pargs, **kwargs)
                    except BaseException as e:
                        return error_object(e)
                    user_info = kwargs['user']
                    yaml_filename = kwargs['yaml_filename']
                    session_code = kwargs['user_code']
                    secret = kwargs['secret']
                    if not str(user_info['the_user_id']).startswith('t'):
                        user_object = worker_controller.get_user_object(user_info['theid'])
                        worker_controller.login_user(user_object, remember=False)
                    # logmessage("ocr_finalize: yaml_filename is " + str(yaml_filename) + " and session code is " + str(session_code))
                    the_current_info = {'user': user_info, 'session': session_code, 'secret': secret, 'yaml_filename': yaml_filename, 'url': url, 'url_root': url_root, 'interface': 'worker'}
                    worker_controller.functions.this_thread.current_info = the_current_info
                    worker_controller.set_request_active(False)
                    worker_controller.obtain_lock_patiently(session_code, yaml_filename)
                    try:
                        steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
                    except BaseException as the_err:
                        worker_controller.release_lock(session_code, yaml_filename)
                        error_message = "ocr_finalize: could not obtain dictionary because of " + str(the_err.__class__.__name__) + ": " + str(the_err)
                        logmessage(error_message)
                        return worker_controller.functions.ReturnValue(ok=False, error_message=error_message, error_type=DAError)
                    if user_dict is None:
                        worker_controller.release_lock(session_code, yaml_filename)
                        error_message = "ocr_finalize: dictionary could not be found"
                        logmessage(error_message)
                        return worker_controller.functions.ReturnValue(ok=False, error_message=error_message, error_type=DAError)
                    user_dict['__PDF_OCR_OBJECT'] = target
                    try:
                        assert worker_controller.functions.illegal_variable_name(target.instanceName) is not True
                        for attribute in ('number', 'file_info', 'filename', 'has_specific_filename', 'ok', 'extension', 'mimetype', 'page_task', 'screen_task'):
                            if hasattr(target, attribute):
                                exec(target.instanceName + '.' + attribute + ' = __PDF_OCR_OBJECT.' + attribute, user_dict)
                            else:
                                exec(target.instanceName + '.delattr(' + repr(attribute) + ')', user_dict)
                        if dafilelist:
                            assert worker_controller.functions.illegal_variable_name(dafilelist.instanceName) is not True
                            exec(dafilelist.instanceName + '.elements = [' + dafilelist.instanceName + '.elements[0]]', user_dict)
                    except BaseException as the_err:
                        worker_controller.release_lock(session_code, yaml_filename)
                        error_message = "ocr_pdf: could not save file object: " + str(the_err.__class__.__name__) + ": " + str(the_err)
                        logmessage(error_message)
                        return worker_controller.functions.ReturnValue(ok=False, error_message=error_message, error_type=DAError)
                    del user_dict['__PDF_OCR_OBJECT']
                    if str(user_info.get('the_user_id', None)).startswith('t'):
                        worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, steps=steps)
                    else:
                        worker_controller.save_user_dict(session_code, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, manual_user_id=user_info['theid'], steps=steps)
                    worker_controller.release_lock(session_code, yaml_filename)
                    return worker_controller.functions.ReturnValue(ok=True, value=True)
                return worker_controller.functions.ReturnValue(ok=True, value=message, content=worker_controller.util.ocr_finalize(*pargs, **kwargs), extra=kwargs.get('extra', None))
            except BaseException as the_error:
                logmessage("Error in ocr_finalize: " + the_error.__class__.__name__ + ': ' + str(the_error))
                return worker_controller.functions.ReturnValue(ok=False, value=str(the_error), error_message=str(the_error), extra=kwargs.get('extra', None))


@workerapp.task
def make_png_for_pdf(doc, prefix, resolution, user_code, pdf_to_png, page=None):
    logmessage("make_png_for_pdf started in worker for size " + prefix)
    worker_controller.initialize()
    url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    url = url_root + 'interview'
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url_root, path=url):
            worker_controller.functions.reset_local_variables()
            worker_controller.functions.set_uid(user_code)
            worker_controller.util.make_png_for_pdf(doc, prefix, resolution, pdf_to_png, page=page)


@workerapp.task
def reset_server(result, run_create=None):
    logmessage("reset_server in worker: starting with run_create " + repr(run_create))
    if hasattr(result, 'ok') and not result.ok:
        logmessage("reset_server in worker: not resetting because result did not succeed.")
        return result
    if not run_create:
        worker_controller.initialize()
        pipe = worker_controller.r.pipeline()
        pipe.set('da:skip_create_tables', 1)
        pipe.expire('da:skip_create_tables', 10)
        logmessage("reset_server in worker: setting da:skip_create_tables.")
        pipe.execute()
    if USING_SUPERVISOR:
        if re.search(r':(web|celery|all):', CONTAINER_ROLE):
            if result.hostname == hostname:
                hostname_to_use = 'localhost'
            else:
                hostname_to_use = result.hostname
            args = SUPERVISORCTL + ['-s', 'http://' + hostname_to_use + ':9001', 'start', 'reset']
            result = subprocess.run(args, check=False).returncode
            logmessage("reset_server in worker: called " + ' '.join(args))
        else:
            logmessage("reset_server in worker: did not reset due to container role")
    else:
        logmessage("reset_server in worker: supervisor not active, touching WSGI file")
        wsgi_file = WEBAPP_PATH
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a', encoding='utf-8'):
                os.utime(wsgi_file, None)
    logmessage("reset_server in worker: finishing")
    return result


@workerapp.task
def update_packages(restart=True):
    start_time = time.time()
    logmessage("update_packages in worker: starting")
    worker_controller.initialize()
    logmessage("update_packages in worker: continuing after " + str(time.time() - start_time) + " seconds")
    try:
        with worker_controller.flaskapp.app_context():
            worker_controller.set_request_active(False)
            logmessage("update_packages in worker: starting update after " + str(time.time() - start_time) + " seconds")
            ok, logmessages, results = worker_controller.update.check_for_updates(start_time=start_time, full=restart)
            logmessage("update_packages in worker: update completed after " + str(time.time() - start_time) + " seconds")
            if restart and ':all:' not in CONTAINER_ROLE:
                worker_controller.trigger_update(except_for=hostname)
                logmessage("update_packages in worker: trigger completed after " + str(time.time() - start_time) + " seconds")
            return worker_controller.functions.ReturnValue(ok=ok, logmessages=logmessages, results=results, hostname=hostname, restart=restart)
    except:
        e = sys.exc_info()[0]
        error_mess = sys.exc_info()[1]
        logmessage("update_packages in worker: error was " + str(e) + " with message " + str(error_mess))
        return worker_controller.functions.ReturnValue(ok=False, error_message=str(e), restart=False)
    logmessage("update_packages in worker: all done")
    return worker_controller.functions.ReturnValue(ok=False, error_message="Reached end", restart=False)


@workerapp.task
def email_attachments(user_code, email_address, attachment_info, language, subject=None, body=None, html=None, config=None):
    success = False
    worker_controller.initialize()
    url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    url = url_root + 'interview'
    if config is None:
        config = 'default'
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url_root, path=url):
            worker_controller.functions.reset_local_variables()
            worker_controller.functions.set_uid(user_code)
            if language and language != '*':
                worker_controller.functions.set_language(language)
            worker_controller.set_request_active(False)
            doc_names = []
            for attach_info in attachment_info:
                if attach_info['attachment']['name'] not in doc_names:
                    doc_names.append(attach_info['attachment']['name'])
            if subject is None:
                subject = worker_controller.functions.comma_and_list(doc_names)
            if body is None:
                if len(doc_names) > 1:
                    body = worker_controller.functions.word("Your documents, %s, are attached.") % (worker_controller.functions.comma_and_list(doc_names),)
                else:
                    body = worker_controller.functions.word("Your document, %s, is attached.") % (worker_controller.functions.comma_and_list(doc_names),)
            if html is None:
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
                    logmessage("Starting to send")
                    worker_controller.da_send_mail(msg, config=config)
                    logmessage("Finished sending")
                    success = True
                except BaseException as errmess:
                    try:
                        logmessage(str(errmess.__class__.__name__) + ": " + str(errmess))
                    except:
                        logmessage("Error of type" + str(errmess.__class__.__name__) + " that could not be displayed")
                    success = False
            if success:
                return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("E-mail was sent to") + " " + email_address, extra='flash')
            return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("Unable to send e-mail to") + " " + email_address, extra='flash')

# @workerapp.task
# def old_email_attachments(yaml_filename, user_info, user_code, secret, url, url_root, email_address, question_number, include_editable):
#     success = False
#     worker_controller.initialize()
#     worker_controller.functions.set_uid(user_code)
#     with worker_controller.flaskapp.app_context():
#         worker_controller.set_request_active(False)
#         # the_user_dict, encrypted = worker_controller.get_attachment_info(user_code, question_number, yaml_filename, secret)
#         steps, the_user_dict, is_encrypted = worker_controller.fetch_user_dict(user_code, yaml_filename, secret=secret)
#         if the_user_dict is not None:
#             interview = worker_controller.interview_cache.get_interview(yaml_filename)
#             interview_status = worker_controller.parse.InterviewStatus(current_info=dict(user=user_info, session=user_code, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=encrypted, interface='worker', arguments={}))
#             interview.assemble(the_user_dict, interview_status)
#             if len(interview_status.attachments) > 0:
#                 attached_file_count = 0
#                 attachment_info = []
#                 for the_attachment in interview_status.attachments:
#                     file_formats = []
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
#                         # logmessage("Need to attach to the e-mail a file called " + str(the_attachment['filename']) + '.' + str(the_format) + ", which is located on the server at " + str(the_filename) + ", with mime type " + str(mime_type))
#                         attached_file_count += 1
#                 if attached_file_count > 0:
#                     doc_names = []
#                     for attach_info in attachment_info:
#                         if attach_info['attachment']['name'] not in doc_names:
#                             doc_names.append(attach_info['attachment']['name'])
#                     subject = worker_controller.functions.comma_and_list(doc_names)
#                     if len(doc_names) > 1:
#                         body = worker_controller.functions.word("Your documents, ") + " " + subject + worker_controller.functions.word(", are attached") + "."
#                     else:
#                         body = worker_controller.functions.word("Your document, ") + " " + subject + worker_controller.functions.word(", is attached") + "."
#                     html = "<p>" + body + "</p>"
#                     # logmessage("Need to send an e-mail with subject " + subject + " to " + str(email_address) + " with " + str(attached_file_count) + " attachment(s)")
#                     msg = worker_controller.Message(subject, recipients=[email_address], body=body, html=html)
#                     for attach_info in attachment_info:
#                         with open(attach_info['path'], 'rb') as fp:
#                             msg.attach(attach_info['filename'], attach_info['mimetype'], fp.read())
#                     try:
#                         logmessage("Starting to send")
#                         worker_controller.da_send_mail(msg)
#                         logmessage("Finished sending")
#                         success = True
#                     except BaseException as errmess:
#                         logmessage(str(errmess))
#                         success = False

#     if success:
#         return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("E-mail was sent to") + " " + email_address, extra='flash')
#     else:
#         return worker_controller.functions.ReturnValue(value=worker_controller.functions.word("Unable to send e-mail to") + " " + email_address, extra='flash')


@workerapp.task
def background_action(yaml_filename, user_info, session_code, secret, url, url_root, action, extra=None):
    if url_root is None:
        url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    if url is None:
        url = url_root + 'interview'
    time.sleep(1.0)
    worker_controller.initialize()
    worker_controller.functions.reset_local_variables()
    worker_controller.functions.set_uid(session_code)
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url_root, path=url):
            if not str(user_info['the_user_id']).startswith('t'):
                user_object = worker_controller.get_user_object(user_info['theid'])
                worker_controller.login_user(user_object, remember=False)
                worker_controller.update_last_login(user_object)
            logmessage("background_action: yaml_filename is " + str(yaml_filename) + " and session code is " + str(session_code) + " and action is " + repr(action))
            worker_controller.set_request_active(False)
            if action['action'] == 'incoming_email':
                if 'id' in action['arguments']:
                    action['arguments'] = {'email': worker_controller.retrieve_email(action['arguments']['id'])}
            the_current_info = {'user': user_info, 'session': session_code, 'secret': secret, 'yaml_filename': yaml_filename, 'url': url, 'url_root': url_root, 'encrypted': True, 'action': action['action'], 'interface': 'worker', 'arguments': action['arguments']}
            worker_controller.functions.this_thread.current_info = the_current_info
            interview = worker_controller.interview_cache.get_interview(yaml_filename)
            worker_controller.obtain_lock_patiently(session_code, yaml_filename)
            try:
                steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
            except BaseException as the_err:
                worker_controller.release_lock(session_code, yaml_filename)
                logmessage("background_action: could not obtain dictionary because of " + str(the_err.__class__.__name__) + ": " + str(the_err))
                return worker_controller.functions.ReturnValue(extra=extra)
            the_current_info['encrypted'] = is_encrypted
            worker_controller.release_lock(session_code, yaml_filename)
            if user_dict is None:
                logmessage("background_action: dictionary could not be found")
                return worker_controller.functions.ReturnValue(extra=extra)
            start_time = time.time()
            interview_status = worker_controller.parse.InterviewStatus(current_info=the_current_info)
            old_language = worker_controller.functions.get_language()
            try:
                interview.assemble(user_dict, interview_status)
            except BaseException as e:
                if hasattr(e, '__traceback__'):
                    logmessage("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(traceback.format_tb(e.__traceback__)))
                else:
                    logmessage("Error in assembly: " + str(e.__class__.__name__) + ": " + str(e))
                error_type = e.__class__.__name__
                error_message = str(e)
                if hasattr(e, '__traceback__'):
                    error_trace = ''.join(traceback.format_tb(e.__traceback__))
                    if hasattr(e, 'da_line_with_error'):
                        error_trace += "\nIn line: " + str(e.da_line_with_error)
                else:
                    error_trace = None
                variables = list(reversed(list(worker_controller.functions.this_thread.current_variable)))
                worker_controller.error_notification(e, message=error_message, trace=error_trace)
                if 'on_error' not in worker_controller.functions.this_thread.current_info:
                    return worker_controller.functions.ReturnValue(ok=False, error_message=error_message, error_type=error_type, error_trace=error_trace, variables=variables)
                logmessage("Time in background action before error callback was " + str(time.time() - start_time))
                worker_controller.functions.set_language(old_language)
                return process_error(interview, session_code, yaml_filename, secret, user_info, url, url_root, is_encrypted, error_type, error_message, error_trace, variables, extra)
            worker_controller.functions.set_language(old_language)
            logmessage("Time in background action was " + str(time.time() - start_time))
            if not hasattr(interview_status, 'question'):
                # logmessage("background_action: status had no question")
                return worker_controller.functions.ReturnValue(extra=extra)
            if interview_status.question.question_type in ["restart", "exit", "exit_logout"]:
                # logmessage("background_action: status was restart or exit")
                worker_controller.obtain_lock_patiently(session_code, yaml_filename)
                if str(user_info.get('the_user_id', None)).startswith('t'):
                    worker_controller.reset_user_dict(session_code, yaml_filename, temp_user_id=user_info.get('theid', None))
                else:
                    worker_controller.reset_user_dict(session_code, yaml_filename, user_id=user_info.get('theid', None))
                worker_controller.release_lock(session_code, yaml_filename)
            # if interview_status.question.question_type in ["restart", "exit", "logout", "exit_logout", "new_session"]:
            #     # There is no lock to release.  Why is this here?
            #     # worker_controller.release_lock(session_code, yaml_filename)
            #     pass
            if interview_status.question.question_type == "response":
                # logmessage("background_action: status was response")
                if hasattr(interview_status.question, 'all_variables'):
                    pass
                elif not hasattr(interview_status.question, 'binaryresponse'):
                    sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
            if interview_status.question.question_type == "backgroundresponse":
                # logmessage("background_action: status was backgroundresponse")
                return worker_controller.functions.ReturnValue(value=interview_status.question.backgroundresponse, extra=extra)
            if interview_status.question.question_type == "backgroundresponseaction":
                # logmessage("background_action: status was backgroundresponseaction")
                start_time = time.time()
                new_action = interview_status.question.action
                # logmessage("new action is " + repr(new_action))
                the_current_info = {'user': user_info, 'session': session_code, 'secret': secret, 'yaml_filename': yaml_filename, 'url': url, 'url_root': url_root, 'encrypted': True, 'interface': 'worker', 'action': new_action['action'], 'arguments': new_action['arguments']}
                worker_controller.functions.this_thread.current_info = the_current_info
                worker_controller.obtain_lock_patiently(session_code, yaml_filename)
                steps, user_dict, is_encrypted = worker_controller.fetch_user_dict(session_code, yaml_filename, secret=secret)
                the_current_info['encrypted'] = is_encrypted
                interview_status = worker_controller.parse.InterviewStatus(current_info=the_current_info)
                old_language = worker_controller.functions.get_language()
                try:
                    interview.assemble(user_dict, interview_status)
                    has_error = False
                except BaseException as e:
                    if hasattr(e, 'traceback'):
                        logmessage("Error in assembly during callback: " + str(e.__class__.__name__) + ": " + str(e) + ": " + str(e.traceback))
                    else:
                        logmessage("Error in assembly during callback: " + str(e.__class__.__name__) + ": " + str(e))
                    error_type = e.__class__.__name__
                    error_message = str(e)
                    if hasattr(e, 'traceback'):
                        error_trace = str(e.traceback)
                        if hasattr(e, 'da_line_with_error'):
                            error_trace += "\nIn line: " + str(e.da_line_with_error)
                    else:
                        error_trace = None
                    variables = list(reversed(list(worker_controller.functions.this_thread.current_variable)))
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
                        # logmessage("background_action: status was response")
                        if hasattr(interview_status.question, 'all_variables'):
                            pass
                        elif not hasattr(interview_status.question, 'binaryresponse'):
                            sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
                    elif interview_status.question.question_type == "backgroundresponse":
                        logmessage("Time in background response action was " + str(time.time() - start_time))
                        return worker_controller.functions.ReturnValue(value=interview_status.question.backgroundresponse, extra=extra)
                logmessage("Time in background response action was " + str(time.time() - start_time))
                return worker_controller.functions.ReturnValue(value=new_action, extra=extra)
            if hasattr(interview_status, 'questionText') and interview_status.questionText:
                if interview_status.orig_sought != interview_status.sought:
                    sought_message = str(interview_status.orig_sought) + " (" + interview_status.sought + ")"
                else:
                    sought_message = str(interview_status.orig_sought)
                logmessage("background_action: The end result of the background action was the seeking of the variable " + sought_message + ", which resulted in asking this question: " + repr(str(interview_status.questionText).strip()))
                logmessage("background_action: Perhaps your interview did not ask all of the questions needed for the background action to do its work.")
                logmessage("background_action: Or perhaps your background action did its job, but you did not end it with a call to background_response().")
                error_type = 'QuestionError'
                error_trace = None
                error_message = interview_status.questionText
                variables = list(reversed(list(worker_controller.functions.this_thread.current_variable)))
                worker_controller.error_notification(Exception("The end result of the background action was the seeking of the variable " + sought_message + ", which resulted in asking this question: " + repr(str(interview_status.questionText).strip())))
                if 'on_error' not in worker_controller.functions.this_thread.current_info:
                    return worker_controller.functions.ReturnValue(ok=False, error_type=error_type, error_trace=error_trace, error_message=error_message, variables=variables, extra=extra)
                return process_error(interview, session_code, yaml_filename, secret, user_info, url, url_root, is_encrypted, error_type, error_message, error_trace, variables, extra)
            logmessage("background_action: finished")
            return worker_controller.functions.ReturnValue(extra=extra)


@workerapp.task
def ocr_google(image_file, raw_result, user_code):
    logmessage("ocr_google started in worker")
    worker_controller.initialize()
    url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    url = url_root + 'interview'
    with worker_controller.flaskapp.app_context():
        with worker_controller.flaskapp.test_request_context(base_url=url_root, path=url):
            worker_controller.functions.reset_local_variables()
            worker_controller.functions.set_uid(user_code)
            worker_controller.set_request_active(False)
            return worker_controller.util.google_ocr_file(image_file, raw_result=raw_result)
