import zoneinfo
import json
import datetime
from io import TextIOWrapper
from pathlib import Path
import tempfile
import filecmp
import zipfile
import subprocess
import re
import os
import uuid
import tarfile
import importlib
import shutil
import stat
import time
import codecs
import xml.etree.ElementTree as ET
from urllib.parse import quote as urllibquote
from urllib.request import urlretrieve
import unicodedata
import xlsxwriter
import tomli
import tomli_w
import httplib2
import oauth2client
import yaml as standardyaml
from flask import (
    request,
    g,
    redirect,
    jsonify,
    Response,
    make_response,
    render_template,
    flash,
    current_app,
    session,
)
from flask_cors import cross_origin
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
from markupsafe import Markup
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import YamlLexer  # pylint: disable=no-name-in-module
from sqlalchemy import select, or_, and_
import werkzeug
from docassemble_flask_user import login_required, roles_required
from docassemble.base.error import DAError, DAException
from docassemble.base.functions import bytesyaml, altyamlstring, serializable_dict
from docassemble.base.hooks import write_ml_source, fix_ml_files
from docassemble.base.generate_key import random_string
from docassemble.base.interview_cache import get_interview, clear_cache
from docassemble.base.language.control import set_language, get_language
from docassemble.base.language.words import word, word_collection
from docassemble.base.pandoc import (
    convertible_extensions,
    word_to_markdown,
    convertible_mimetypes,
)
from docassemble.base.parse import InterviewStatus, Interview
from docassemble.base.interview_source import (
    interview_source_from_string,
    InterviewSourceString,
)
from docassemble.base.thread_context import this_thread
from docassemble.webapp.config import (
    final_default_yaml_filename,
    DEBUG,
    NOTIFICATION_CONTAINER,
    NOTIFICATION_MESSAGE,
    keymap,
    DEFER,
    DEFAULT_LANGUAGE,
    ga_configured,
    GITHUB_BRANCH,
    google_config,
    da_version,
    daconfig,
    START_TIME,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.files.file_access import get_info_from_file_number
from docassemble.webapp.files.file_number import get_new_file_number
from docassemble.webapp.files.helpers import file_set_attributes
from docassemble.webapp.files.savedfile import SavedFile, DEFAULT_GITIGNORE
from docassemble.webapp.files.savedfile import (
    make_package_dir,
    publish_package,
    make_package_zip,
)
from docassemble.webapp.interview.helpers import read_fields
from docassemble.webapp.interview.user_dict import fetch_user_dict
from docassemble.webapp.mail.da_flask_mail import Message
from docassemble.webapp.mail.hooks import da_send_mail
from docassemble.webapp.main.hooks import get_default_timezone
from docassemble.webapp.packages.models import Package, PackageAuth
from docassemble.webapp.sessions import get_session
from docassemble.webapp.tasks.app import celery_app
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.users.helpers import needs_to_change_password
from docassemble.webapp.users.models import UserRoles, UserModel, Role
from docassemble.webapp.utils.filenames import (
    get_ext_and_mimetype,
    secure_filename_spaces_ok,
    directory_for,
)
from docassemble.webapp.utils.helpers import (
    get_vars_in_use,
    standard_scripts,
    noquote,
    default_playground_yaml,
    install_zip_package,
    flash_as_html,
    indent_by,
    name_of_user,
    current_info,
    formatted_current_time,
    get_base_url,
    get_next_link,
    get_package_info,
    redis_script,
    should_run_create,
    formatted_current_date,
    additional_scripts,
    pg_code_cache,
    standard_html_start,
    additional_css,
    ok_mimetypes,
    uid_or_random,
    true_or_false,
    ok_extensions,
    CAN_CONVERT_WORD,
    version_warning,
    custom_send_file,
)
from docassemble.webapp.interview.dictionary import fresh_dictionary
from docassemble.webapp.packages.helpers import pypi_status
from docassemble.webapp.utils.filenames import sanitize_arguments, secure_filename
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.utils.path import splitall
from docassemble.webapp.utils.redis_cred_storage import RedisCredStorage
from .blueprint import develop_bp
from .common import project_name, get_playground_user
from .forms import (
    AddinUploadForm,
    CreatePackageForm,
    CreatePlaygroundPackageForm,
    DeleteProject,
    FunctionFileForm,
    GitHubForm,
    GoogleDriveForm,
    NewProject,
    OneDriveForm,
    PlaygroundFilesEditForm,
    PlaygroundFilesForm,
    PlaygroundForm,
    PlaygroundPackagesForm,
    PlaygroundUploadForm,
    PullPlaygroundPackage,
    RenameProject,
    RequestDeveloperForm,
    Utilities,
)
from .helpers import (
    add_project,
    base_words,
    define_examples,
    delete_ssh_keys,
    get_github_flow,
    get_ssh_keys,
    pg_ex,
    set_playground_user,
)


@develop_bp.route('/playground_poll', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def playground_poll():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    script = f"""
    <script{DEFER}>
      function daPollCallback(data){{
        if (data.success){{
          window.location.replace(data.url);
        }}
      }}
      function daPoll(){{
        $.ajax({{
          type: 'GET',
          url: {json.dumps(url_for('develop.playground_redirect_poll'))},
          success: daPollCallback,
          dataType: 'json'
        }});
        return true;
      }}
      document.addEventListener("DOMContentLoaded", function () {{
        $( document ).ready(function() {{
          //console.log("polling");
          setInterval(daPoll, 4000);
        }});
      }});
    </script>"""
    response = make_response(render_template('develop/playground_poll.html', version_warning=None, bodyclass='daadminbody', extra_js=Markup(script), tab_title=word('Waiting'), page_title=word('Waiting')), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def get_gd_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('googledrive', {})
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('Google Drive is not configured.')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='https://www.googleapis.com/auth/drive',
        redirect_uri=url_for('develop.google_drive_callback', _external=True),
        access_type='offline',
        prompt='consent')
    return flow


def get_gd_folder():
    key = 'da:googledrive:mapping:userid:' + str(current_user.id)
    folder = r.get(key)
    if folder is not None:
        return folder.decode()
    return folder


def set_gd_folder(folder):
    key = 'da:googledrive:mapping:userid:' + str(current_user.id)
    if folder is None:
        r.delete(key)
    else:
        set_od_folder(None)
        r.set(key, folder)


def get_od_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('onedrive', {})
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('OneDrive is not configured.')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='files.readwrite.all user.read offline_access',
        redirect_uri=url_for('develop.onedrive_callback', _external=True),
        response_type='code',
        auth_uri='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        token_uri='https://login.microsoftonline.com/common/oauth2/v2.0/token')
    return flow


def get_od_folder():
    key = 'da:onedrive:mapping:userid:' + str(current_user.id)
    folder = r.get(key)
    if folder is not None:
        return folder.decode()
    return folder


def set_od_folder(folder):
    key = 'da:onedrive:mapping:userid:' + str(current_user.id)
    if folder is None:
        r.delete(key)
    else:
        set_gd_folder(None)
        r.set(key, folder)


@develop_bp.route('/google_drive_callback', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def google_drive_callback():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    for key in request.args:
        logmessage("google_drive_callback: argument " + str(key) + ": " + str(request.args[key]))
    if 'code' in request.args:
        flow = get_gd_flow()
        credentials = flow.step2_exchange(request.args['code'])
        storage = RedisCredStorage(oauth_app='googledrive')
        storage.put(credentials)
        error = None
    elif 'error' in request.args:
        error = request.args['error']
    else:
        error = word("could not connect to Google Drive")
    if error:
        flash(word('There was a Google Drive error: ' + error), 'error')
        return redirect(url_for('user.profile'))
    flash(word('Connected to Google Drive'), 'success')
    return redirect(url_for('develop.google_drive_page'))


def rename_gd_project(old_project, new_project):
    the_folder = get_gd_folder()
    if the_folder is None:
        logmessage('rename_gd_project: folder not configured')
        return False
    storage = RedisCredStorage(oauth_app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('rename_gd_project: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    import apiclient  # pylint: disable=import-outside-toplevel
    service = apiclient.discovery.build('drive', 'v3', http=http)
    response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()  # pylint: disable=no-member
    trashed = response.get('trashed', False)
    the_mime_type = response.get('mimeType', None)
    if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
        logmessage('rename_gd_project: folder did not exist')
        return False
    for section in ['static', 'templates', 'questions', 'modules', 'sources', 'packages']:
        logmessage("rename_gd_project: section is " + section)
        subdir = None
        page_token = None
        while True:
            response = service.files().list(spaces="drive", pageToken=page_token, fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(section) + "' and '" + str(the_folder) + "' in parents").execute()  # pylint: disable=no-member
            for the_file in response.get('files', []):
                if 'id' in the_file:
                    subdir = the_file['id']
                    break
            page_token = response.get('nextPageToken', None)
            if subdir is not None or page_token is None:
                break
        if subdir is None:
            logmessage('rename_gd_project: section ' + str(section) + ' could not be found')
            continue
        subsubdir = None
        page_token = None
        while True:
            response = service.files().list(spaces="drive", pageToken=page_token, fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(old_project) + "' and '" + str(subdir) + "' in parents").execute()  # pylint: disable=no-member
            for the_file in response.get('files', []):
                if 'id' in the_file:
                    subsubdir = the_file['id']
                    break
            page_token = response.get('nextPageToken', None)
            if subsubdir is not None or page_token is None:
                break
        if subsubdir is None:
            logmessage('rename_gd_project: project ' + str(old_project) + ' could not be found in ' + str(section))
            continue
        metadata = {'name': new_project}
        service.files().update(fileId=subsubdir, body=metadata, fields='name').execute()  # pylint: disable=no-member
        logmessage('rename_gd_project: folder ' + str(old_project) + ' renamed in section ' + str(section))
    return True


def trash_gd_project(old_project):
    the_folder = get_gd_folder()
    if the_folder is None:
        logmessage('trash_gd_project: folder not configured')
        return False
    storage = RedisCredStorage(oauth_app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('trash_gd_project: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    import apiclient  # pylint: disable=import-outside-toplevel
    service = apiclient.discovery.build('drive', 'v3', http=http)
    response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()  # pylint: disable=no-member
    trashed = response.get('trashed', False)
    the_mime_type = response.get('mimeType', None)
    if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
        logmessage('trash_gd_project: folder did not exist')
        return False
    for section in ['static', 'templates', 'questions', 'modules', 'sources', 'packages']:
        subdir = None
        page_token = None
        while True:
            response = service.files().list(spaces="drive", pageToken=page_token, fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(section) + "' and '" + str(the_folder) + "' in parents").execute()  # pylint: disable=no-member
            for the_file in response.get('files', []):
                if 'id' in the_file:
                    subdir = the_file['id']
                    break
            page_token = response.get('nextPageToken', None)
            if subdir is not None or page_token is None:
                break
        if subdir is None:
            logmessage('trash_gd_project: section ' + str(section) + ' could not be found')
            continue
        subsubdir = None
        page_token = None
        while True:
            response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(old_project) + "' and '" + str(subdir) + "' in parents").execute()  # pylint: disable=no-member
            for the_file in response.get('files', []):
                if 'id' in the_file:
                    subsubdir = the_file['id']
                    break
            page_token = response.get('nextPageToken', None)
            if subsubdir is not None or page_token is None:
                break
        if subsubdir is None:
            logmessage('trash_gd_project: project ' + str(old_project) + ' could not be found in ' + str(section))
            continue
        service.files().delete(fileId=subsubdir).execute()  # pylint: disable=no-member
        logmessage('trash_gd_project: project ' + str(old_project) + ' deleted in section ' + str(section))
    return True


def trash_gd_file(section, filename, current_project):
    if section == 'template':
        section = 'templates'
    the_folder = get_gd_folder()
    if the_folder is None:
        logmessage('trash_gd_file: folder not configured')
        return False
    storage = RedisCredStorage(oauth_app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('trash_gd_file: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    import apiclient  # pylint: disable=import-outside-toplevel
    service = apiclient.discovery.build('drive', 'v3', http=http)
    response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()  # pylint: disable=no-member
    trashed = response.get('trashed', False)
    the_mime_type = response.get('mimeType', None)
    if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
        logmessage('trash_gd_file: folder did not exist')
        return False
    subdir = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(section) + "' and '" + str(the_folder) + "' in parents").execute()  # pylint: disable=no-member
    for the_file in response.get('files', []):
        if 'id' in the_file:
            subdir = the_file['id']
            break
    if subdir is None:
        logmessage('trash_gd_file: section ' + str(section) + ' could not be found')
        return False
    if current_project != 'default':
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(current_project) + "' and '" + str(subdir) + "' in parents").execute()  # pylint: disable=no-member
        subdir = None
        for the_file in response.get('files', []):
            if 'id' in the_file:
                subdir = the_file['id']
                break
        if subdir is None:
            logmessage('trash_gd_file: project ' + str(current_project) + ' could not be found')
            return False
    id_of_filename = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType!='application/vnd.google-apps.folder' and name='" + str(filename) + "' and '" + str(subdir) + "' in parents").execute()  # pylint: disable=no-member
    for the_file in response.get('files', []):
        if 'id' in the_file:
            id_of_filename = the_file['id']
            break
    if id_of_filename is None:
        logmessage('trash_gd_file: file ' + str(filename) + ' could not be found in ' + str(section))
        return False
    service.files().delete(fileId=id_of_filename).execute()  # pylint: disable=no-member
    logmessage('trash_gd_file: file ' + str(filename) + ' permanently deleted from ' + str(section))
    return True


@develop_bp.route('/sync_with_google_drive', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def sync_with_google_drive():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    current_project = get_current_project()
    the_next = current_app.user_manager.make_safe_url_function(request.args.get('next', url_for('develop.playground_page', project=current_project)))
    auto_next = request.args.get('auto_next', None)
    if current_app.config['USE_GOOGLE_DRIVE'] is False:
        flash(word("Google Drive is not configured"), "error")
        return redirect(the_next)
    storage = RedisCredStorage(oauth_app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        return redirect(uri)
    task = celery_app.signature('tasks.sync_with_google_drive', args=[current_user.id]).delay()
    session['taskwait'] = task.id
    if auto_next:
        return redirect(url_for('develop.gd_sync_wait', auto_next=auto_next))
    return redirect(url_for('develop.gd_sync_wait', next=the_next))


@develop_bp.route('/gdsyncing', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def gd_sync_wait():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    current_project = get_current_project()
    next_url = current_app.user_manager.make_safe_url_function(request.args.get('next', url_for('develop.playground_page', project=current_project)))
    auto_next_url = request.args.get('auto_next', None)
    my_csrf = generate_csrf()
    script = f"""
    <script{DEFER}>
      var daCheckinInterval = null;
      var autoNext = {json.dumps(auto_next_url)};
      var resultsAreIn = false;
      var pollInterval = null;
      var taskId = null;
      function daRestartCallback(data){{
        taskId = data.task_id;
        pollInterval = setInterval(daPoll, 4000);
      }}
      function daPoll(){{
        $.ajax({{
          type: 'GET',
          url: {json.dumps(url_for('main.check_restart_status'))} + '?' + $.param({{"task_id": taskId}}),
          success: daCheckStatus,
          error: daIgnoreStatus,
          dataType: 'json',
          timeout: 3500
        }});
      }}
      function daCheckStatus(data){{
        if (data.status == "completed"){{
          clearInterval(pollInterval);
          $("#returnButton").show();
          $("#restartButton").hide();
        }}
        else{{
          console.log("Status of restart was: " + data.status + ".");
        }}
      }}
      function daIgnoreStatus(data){{
        console.log("Unable to check status of restart. Perhaps the server will respond again.")
      }}
      function daRestart(){{
        $.ajax({{
          type: 'POST',
          url: {json.dumps(url_for('main.restart_ajax'))},
          data: 'csrf_token={my_csrf}&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        }});
        return true;
      }}
      function daSyncCallback(data){{
        if (data.success){{
          if (data.status == 'finished'){{
            resultsAreIn = true;
            if (data.ok){{
              if (autoNext != null){{
                window.location.replace(autoNext);
              }}
              $("#notification").html({json.dumps(word("The synchronization was successful."))});
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-danger");
              $("#notification").addClass("alert-success");
            }}
            else{{
              $("#notification").html({json.dumps(word("The synchronization was not successful."))});
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-success");
              $("#notification").addClass("alert-danger");
            }}
            $("#resultsContainer").show();
            $("#resultsArea").html(data.summary);
            if (daCheckinInterval != null){{
              clearInterval(daCheckinInterval);
            }}
            if (data.restart){{
              $("#returnButton").hide();
              $("#restartButton").show();
              daRestart();
            }}
          }}
          else if (data.status == 'failed' && !resultsAreIn){{
            resultsAreIn = true;
            $("#notification").html({json.dumps(word("There was an error with the synchronization."))});
            $("#notification").removeClass("alert-info");
            $("#notification").removeClass("alert-success");
            $("#notification").addClass("alert-danger");
            $("#resultsContainer").show();
            if (data.error_message){{
              $("#resultsArea").html(data.error_message);
            }}
            else if (data.summary){{
              $("#resultsArea").html(data.summary);
            }}
            if (daCheckinInterval != null){{
              clearInterval(daCheckinInterval);
            }}
          }}
        }}
        else if (!resultsAreIn){{
          $("#notification").html({json.dumps(word("There was an error."))});
          $("#notification").removeClass("alert-info");
          $("#notification").removeClass("alert-success");
          $("#notification").addClass("alert-danger");
          if (daCheckinInterval != null){{
            clearInterval(daCheckinInterval);
          }}
        }}
      }}
      function daSync(){{
        if (resultsAreIn){{
          return;
        }}
        $.ajax({{
          type: 'POST',
          url: {json.dumps(url_for('develop.checkin_sync_with_google_drive'))},
          data: 'csrf_token={my_csrf}',
          success: daSyncCallback,
          dataType: 'json'
        }});
        return true;
      }}
      document.addEventListener("DOMContentLoaded", function () {{
        $( document ).ready(function() {{
          //console.log("page loaded");
          daCheckinInterval = setInterval(daSync, 2000);
        }});
      }});
    </script>"""
    response = make_response(render_template('develop/gd_sync_wait.html', version_warning=None, bodyclass='daadminbody', extra_js=Markup(script), tab_title=word('Synchronizing'), page_title=word('Synchronizing'), next_page=next_url), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/onedrive_callback', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def onedrive_callback():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    for key in request.args:
        logmessage("onedrive_callback: argument " + str(key) + ": " + str(request.args[key]))
    if 'code' in request.args:
        flow = get_od_flow()
        credentials = flow.step2_exchange(request.args['code'])
        storage = RedisCredStorage(oauth_app='onedrive')
        storage.put(credentials)
        error = None
    elif 'error' in request.args:
        error = request.args['error']
        if 'error_description' in request.args:
            error += '; ' + str(request.args['error_description'])
    else:
        error = word("could not connect to OneDrive")
    if error:
        flash(word('There was a OneDrive error: ' + error), 'error')
        return redirect(url_for('user.profile'))
    flash(word('Connected to OneDrive'), 'success')
    return redirect(url_for('develope.onedrive_page'))


def rename_od_project(old_project, new_project):
    the_folder = get_od_folder()
    if the_folder is None:
        logmessage('rename_od_project: folder not configured')
        return False
    storage = RedisCredStorage(oauth_app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('rename_od_project: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllibquote(the_folder), "GET")
    if int(resp['status']) != 200:
        trashed = True
    else:
        info = json.loads(content.decode())
        # logmessage("Found " + repr(info))
        trashed = bool(info.get('deleted', None))
    if trashed is True or 'folder' not in info:
        logmessage('rename_od_project: folder did not exist')
        return False
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllibquote(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
    subdir = {}
    for section in ['static', 'templates', 'questions', 'modules', 'sources', 'packages']:
        subdir[section] = None
    while True:
        if int(resp['status']) != 200:
            logmessage('rename_od_project: could not obtain subfolders')
            return False
        info = json.loads(content.decode())
        for item in info.get('value', []):
            if item.get('deleted', None) or 'folder' not in item:
                continue
            if item['name'] in subdir:
                subdir[item['name']] = item['id']
        if "@odata.nextLink" not in info:
            break
        resp, content = http.request(info["@odata.nextLink"], "GET")
    for section, the_subdir in subdir.items():
        if the_subdir is None:
            logmessage('rename_od_project: could not obtain subfolder for ' + str(section))
            continue
        subsubdir = None
        resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(the_subdir) + "/children?$select=id,name,deleted,folder", "GET")
        while True:
            if int(resp['status']) != 200:
                logmessage('rename_od_project: could not obtain contents of subfolder for ' + str(section))
                break
            info = json.loads(content.decode())
            for item in info.get('value', []):
                if item.get('deleted', None) or 'folder' not in item:
                    continue
                if item['name'] == old_project:
                    subsubdir = item['id']
                    break
            if subsubdir is not None or "@odata.nextLink" not in info:
                break
            resp, content = http.request(info["@odata.nextLink"], "GET")
        if subsubdir is None:
            logmessage("rename_od_project: subdirectory " + str(old_project) + " not found")
        else:
            headers = {'Content-Type': 'application/json'}
            resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(subsubdir), "PATCH", headers=headers, body=json.dumps({'name': new_project}))
            if int(resp['status']) != 200:
                logmessage('rename_od_project: could not rename folder ' + str(old_project) + " in " + str(section) + " because " + repr(content))
                continue
        logmessage('rename_od_project: project ' + str(old_project) + ' rename in section ' + str(section))
    return True


def trash_od_project(old_project):
    the_folder = get_od_folder()
    if the_folder is None:
        logmessage('trash_od_project: folder not configured')
        return False
    storage = RedisCredStorage(oauth_app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('trash_od_project: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllibquote(the_folder), "GET")
    if int(resp['status']) != 200:
        trashed = True
    else:
        info = json.loads(content.decode())
        # logmessage("Found " + repr(info))
        trashed = bool(info.get('deleted', None))
    if trashed is True or 'folder' not in info:
        logmessage('trash_od_project: folder did not exist')
        return False
    subdir = {}
    for section in ['static', 'templates', 'questions', 'modules', 'sources', 'packages']:
        subdir[section] = None
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllibquote(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
    while True:
        if int(resp['status']) != 200:
            logmessage('trash_od_project: could not obtain subfolders')
            return False
        info = json.loads(content.decode())
        for item in info['value']:
            if item.get('deleted', None) or 'folder' not in item:
                continue
            if item['name'] in subdir:
                subdir[item['name']] = item['id']
        if "@odata.nextLink" not in info:
            break
        resp, content = http.request(info["@odata.nextLink"], "GET")
    for section, the_subdir in subdir.items():
        if the_subdir is None:
            logmessage('trash_od_project: could not obtain subfolder for ' + str(section))
            continue
        subsubdir = None
        resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(the_subdir) + "/children?$select=id,name,deleted,folder", "GET")
        while True:
            if int(resp['status']) != 200:
                logmessage('trash_od_project: could not obtain contents of subfolder for ' + str(section))
                break
            info = json.loads(content.decode())
            for item in info['value']:
                if item.get('deleted', None) or 'folder' not in item:
                    continue
                if item['name'] == old_project:
                    subsubdir = item['id']
                    break
            if subsubdir is not None or "@odata.nextLink" not in info:
                break
            resp, content = http.request(info["@odata.nextLink"], "GET")
        if subsubdir is None:
            logmessage("Could not find subdirectory " + old_project + " in section " + str(section))
        else:
            resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllibquote(subsubdir) + "/children?$select=id", "GET")
            to_delete = []
            while True:
                if int(resp['status']) != 200:
                    logmessage('trash_od_project: could not obtain contents of project folder')
                    return False
                info = json.loads(content.decode())
                for item in info.get('value', []):
                    if 'id' in item:
                        to_delete.append(item['id'])
                if "@odata.nextLink" not in info:
                    break
                resp, content = http.request(info["@odata.nextLink"], "GET")
            for item_id in to_delete:
                resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(item_id), "DELETE")
                if int(resp['status']) != 204:
                    logmessage('trash_od_project: could not delete file ' + str(item_id) + ".  Result: " + repr(content))
                    return False
            resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(subsubdir), "DELETE")
            if int(resp['status']) != 204:
                logmessage('trash_od_project: could not delete project ' + str(old_project) + ".  Result: " + repr(content))
                return False
            logmessage('trash_od_project: project ' + str(old_project) + ' trashed in section ' + str(section))
    return True


def trash_od_file(section, filename, current_project):
    if section == 'template':
        section = 'templates'
    the_folder = get_od_folder()
    if the_folder is None:
        logmessage('trash_od_file: folder not configured')
        return False
    storage = RedisCredStorage(oauth_app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('trash_od_file: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllibquote(the_folder), "GET")
    if int(resp['status']) != 200:
        trashed = True
    else:
        info = json.loads(content.decode())
        # logmessage("Found " + repr(info))
        trashed = bool(info.get('deleted', None))
    if trashed is True or 'folder' not in info:
        logmessage('trash_od_file: folder did not exist')
        return False
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllibquote(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
    subdir = None
    while True:
        if int(resp['status']) != 200:
            logmessage('trash_od_file: could not obtain subfolders')
            return False
        info = json.loads(content.decode())
        # logmessage("Found " + repr(info))
        for item in info['value']:
            if item.get('deleted', None) or 'folder' not in item:
                continue
            if item['name'] == section:
                subdir = item['id']
                break
        if subdir is not None or "@odata.nextLink" not in info:
            break
        resp, content = http.request(info["@odata.nextLink"], "GET")
    if subdir is None:
        logmessage('trash_od_file: could not obtain subfolder')
        return False
    if current_project != 'default':
        resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(subdir) + "/children?$select=id,name,deleted,folder", "GET")
        subdir = None
        while True:
            if int(resp['status']) != 200:
                logmessage('trash_od_file: could not obtain subfolders to find project')
                return False
            info = json.loads(content.decode())
            for item in info['value']:
                if item.get('deleted', None) or 'folder' not in item:
                    continue
                if item['name'] == current_project:
                    subdir = item['id']
                    break
            if subdir is not None or "@odata.nextLink" not in info:
                break
            resp, content = http.request(info["@odata.nextLink"], "GET")
        if subdir is None:
            logmessage('trash_od_file: could not obtain subfolder')
            return False
    id_of_filename = None
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(subdir) + "/children?$select=id,name,deleted,folder", "GET")
    while True:
        if int(resp['status']) != 200:
            logmessage('trash_od_file: could not obtain contents of subfolder')
            return False
        info = json.loads(content.decode())
        # logmessage("Found " + repr(info))
        for item in info['value']:
            if item.get('deleted', None) or 'folder' in item:
                continue
            if 'folder' in item:
                continue
            if item['name'] == filename:
                id_of_filename = item['id']
                break
        if id_of_filename is not None or "@odata.nextLink" not in info:
            break
        resp, content = http.request(info["@odata.nextLink"], "GET")
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(id_of_filename), "DELETE")
    if int(resp['status']) != 204:
        logmessage('trash_od_file: could not delete ')
        return False
    logmessage('trash_od_file: file ' + str(filename) + ' trashed from ' + str(section))
    return True


@develop_bp.route('/sync_with_onedrive', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def sync_with_onedrive():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    # current_project = get_current_project()
    the_next = current_app.user_manager.make_safe_url_function(request.args.get('next', url_for('develop.playground_page', project=get_current_project())))
    auto_next = request.args.get('auto_next', None)
    if current_app.config['USE_ONEDRIVE'] is False:
        flash(word("OneDrive is not configured"), "error")
        return redirect(the_next)
    storage = RedisCredStorage(oauth_app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        return redirect(uri)
    task = celery_app.signature('tasks.sync_with_onedrive', args=[current_user.id]).delay()
    session['taskwait'] = task.id
    if auto_next:
        return redirect(url_for('develop.od_sync_wait', auto_next=auto_next))
    return redirect(url_for('develop.od_sync_wait', next=the_next))


@develop_bp.route('/odsyncing', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def od_sync_wait():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    current_project = get_current_project()
    next_url = current_app.user_manager.make_safe_url_function(request.args.get('next', url_for('develop.playground_page', project=current_project)))
    auto_next_url = request.args.get('auto_next', None)
    if auto_next_url is not None:
        auto_next_url = current_app.user_manager.make_safe_url_function(auto_next_url)
    my_csrf = generate_csrf()
    script = f"""
    <script{DEFER}>
      var daCheckinInterval = null;
      var autoNext = {json.dumps(auto_next_url)};
      var resultsAreIn = false;
      var pollInterval = null;
      var taskId = null;
      function daRestartCallback(data){{
        taskId = data.task_id;
        pollInterval = setInterval(daPoll, 4000);
      }}
      function daPoll(){{
        $.ajax({{
          type: 'GET',
          url: {json.dumps(url_for('main.check_restart_status'))} + '?' + $.param({{"task_id": taskId}}),
          success: daCheckStatus,
          error: daIgnoreStatus,
          dataType: 'json',
          timeout: 3500
        }});
      }}
      function daCheckStatus(data){{
        if (data.status == "completed"){{
          clearInterval(pollInterval);
          $("#returnButton").show();
          $("#restartButton").hide();
        }}
        else{{
          console.log("Status of restart was: " + data.status + ".");
        }}
      }}
      function daIgnoreStatus(data){{
        console.log("Unable to check status of restart. Perhaps the server will respond again.")
      }}
      function daRestart(){{
        $.ajax({{
          type: 'POST',
          url: {json.dumps(url_for('main.restart_ajax'))},
          data: 'csrf_token={my_csrf}&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        }});
        return true;
      }}
      function daSyncCallback(data){{
        if (data.success){{
          if (data.status == 'finished'){{
            resultsAreIn = true;
            if (data.ok){{
              $("#notification").html({json.dumps(word("The synchronization was successful."))});
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-danger");
              $("#notification").addClass("alert-success");
            }}
            else{{
              $("#notification").html({json.dumps(word("The synchronization was not successful."))});
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-success");
              $("#notification").addClass("alert-danger");
            }}
            $("#resultsContainer").show();
            $("#resultsArea").html(data.summary);
            if (daCheckinInterval != null){{
              clearInterval(daCheckinInterval);
            }}
            if (data.restart){{
              $("#returnButton").hide();
              $("#restartButton").show();
              daRestart();
            }}
            else{{
              if (autoNext != null){{
                window.location.replace(autoNext);
              }}
            }}
          }}
          else if (data.status == 'failed' && !resultsAreIn){{
            resultsAreIn = true;
            $("#notification").html({json.dumps(word("There was an error with the synchronization."))});
            $("#notification").removeClass("alert-info");
            $("#notification").removeClass("alert-success");
            $("#notification").addClass("alert-danger");
            $("#resultsContainer").show();
            if (data.error_message){{
              $("#resultsArea").html(data.error_message);
            }}
            else if (data.summary){{
              $("#resultsArea").html(data.summary);
            }}
            if (daCheckinInterval != null){{
              clearInterval(daCheckinInterval);
            }}
          }}
        }}
        else if (!resultsAreIn){{
          $("#notification").html({json.dumps(word("There was an error."))});
          $("#notification").removeClass("alert-info");
          $("#notification").removeClass("alert-success");
          $("#notification").addClass("alert-danger");
          if (daCheckinInterval != null){{
            clearInterval(daCheckinInterval);
          }}
        }}
      }}
      function daSync(){{
        if (resultsAreIn){{
          return;
        }}
        $.ajax({{
          type: 'POST',
          url: {json.dumps(url_for('develop.checkin_sync_with_onedrive'))},
          data: 'csrf_token={my_csrf}',
          success: daSyncCallback,
          dataType: 'json'
        }});
        return true;
      }}
      document.addEventListener("DOMContentLoaded", function () {{
        $( document ).ready(function() {{
          //console.log("page loaded");
          daCheckinInterval = setInterval(daSync, 2000);
        }});
      }});
    </script>"""
    response = make_response(render_template('develop/od_sync_wait.html', version_warning=None, bodyclass='daadminbody', extra_js=Markup(script), tab_title=word('Synchronizing'), page_title=word('Synchronizing'), next_page=next_url), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response

# @develop_bp.route('/old_sync_with_google_drive', methods=['GET', 'POST'])
# @login_required
# @roles_required(['admin', 'developer'])
# def old_sync_with_google_drive():
#     next = request.args.get('next', url_for('develop.playground_page'))
#     extra_meta = """\n    <meta http-equiv="refresh" content="1; url='""" + url_for('develop.do_sync_with_google_drive', next=next) + """'">"""
#     return render_template('develop/google_sync.html', version_warning=None, bodyclass='daadminbody', extra_meta=Markup(extra_meta), tab_title=word('Synchronizing'), page_title=word('Synchronizing'))


def add_br(text):
    return re.sub(r'[\n\r]+', "<br>", text)


@develop_bp.route('/checkin_sync_with_google_drive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def checkin_sync_with_google_drive():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    if 'taskwait' not in session:
        return jsonify(success=False)
    result = celery_app.AsyncResult(id=session['taskwait'])
    if result.ready():
        if 'taskwait' in session:
            del session['taskwait']
        the_result = result.get()
        if the_result.__class__.__name__ == 'ReturnValue':
            if the_result.ok:
                logmessage("checkin_sync_with_google_drive: success")
                return jsonify(success=True, status='finished', ok=the_result.ok, summary=add_br(the_result.summary), restart=the_result.restart)
            if hasattr(the_result, 'error'):
                logmessage("checkin_sync_with_google_drive: failed return value is " + str(the_result.error))
                return jsonify(success=True, status='failed', error_message=str(the_result.error), restart=False)
            if hasattr(the_result, 'summary'):
                return jsonify(success=True, status='failed', summary=add_br(the_result.summary), restart=False)
            return jsonify(success=True, status='failed', error_message=str("No error message.  Result is " + str(the_result)), restart=False)
        logmessage("checkin_sync_with_google_drive: failed return value is a " + str(type(the_result)))
        logmessage("checkin_sync_with_google_drive: failed return value is " + str(the_result))
        return jsonify(success=True, status='failed', error_message=noquote(str(the_result)), restart=False)
    return jsonify(success=True, status='waiting', restart=False)


@develop_bp.route('/checkin_sync_with_onedrive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def checkin_sync_with_onedrive():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    if 'taskwait' not in session:
        return jsonify(success=False)
    result = celery_app.AsyncResult(id=session['taskwait'])
    if result.ready():
        if 'taskwait' in session:
            del session['taskwait']
        the_result = result.get()
        if the_result.__class__.__name__ == 'ReturnValue':
            if the_result.ok:
                logmessage("checkin_sync_with_onedrive: success")
                return jsonify(success=True, status='finished', ok=the_result.ok, summary=add_br(the_result.summary), restart=the_result.restart)
            if hasattr(the_result, 'error'):
                logmessage("checkin_sync_with_onedrive: failed return value is " + str(the_result.error))
                return jsonify(success=True, status='failed', error_message=str(the_result.error), restart=False)
            if hasattr(the_result, 'summary'):
                return jsonify(success=True, status='failed', summary=add_br(the_result.summary), restart=False)
            return jsonify(success=True, status='failed', error_message=str("No error message.  Result is " + str(the_result)), restart=False)
        logmessage("checkin_sync_with_onedrive: failed return value is a " + str(type(the_result)))
        logmessage("checkin_sync_with_onedrive: failed return value is " + str(the_result))
        return jsonify(success=True, status='failed', error_message=str(the_result), restart=False)
    return jsonify(success=True, status='waiting', restart=False)


@develop_bp.route('/google_drive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def google_drive_page():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if current_app.config['USE_GOOGLE_DRIVE'] is False:
        flash(word("Google Drive is not configured"), "error")
        return redirect(url_for('user.profile'))
    form = GoogleDriveForm(request.form)
    if request.method == 'POST' and form.cancel.data:
        return redirect(url_for('user.profile'))
    storage = RedisCredStorage(oauth_app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        # logmessage("google_drive_page: uri is " + str(uri))
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    import apiclient  # pylint: disable=import-outside-toplevel
    try:
        service = apiclient.discovery.build('drive', 'v3', http=http)
    except:
        set_gd_folder(None)
        storage.release_lock()
        storage.locked_delete()
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        return redirect(uri)
    items = [{'id': '', 'name': word('-- Do not link --')}]
    # items = []
    page_token = None
    while True:
        try:
            response = service.files().list(spaces="drive", pageToken=page_token, fields="nextPageToken, files(id, name, mimeType, shortcutDetails)", q="trashed=false and 'root' in parents and (mimeType = 'application/vnd.google-apps.folder' or (mimeType = 'application/vnd.google-apps.shortcut' and shortcutDetails.targetMimeType = 'application/vnd.google-apps.folder'))").execute()  # pylint: disable=no-member
        except BaseException as err:
            logmessage("google_drive_page: " + err.__class__.__name__ + ": " + str(err))
            set_gd_folder(None)
            storage.release_lock()
            storage.locked_delete()
            flash(word('There was a Google Drive error: ' + err.__class__.__name__ + ": " + str(err)), 'error')
            return redirect(url_for('develop.google_drive_page'))
        for the_file in response.get('files', []):
            if the_file['mimeType'] == 'application/vnd.google-apps.shortcut':
                the_file['id'] = the_file['shortcutDetails']['targetId']
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    item_ids = [x['id'] for x in items if x['id'] != '']
    if request.method == 'POST' and form.submit.data:
        if form.folder.data == '':
            set_gd_folder(None)
            storage.locked_delete()
            flash(word("Google Drive is not linked."), 'success')
        elif form.folder.data in (-1, '-1'):
            file_metadata = {
                'name': 'docassemble',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            new_file = service.files().create(body=file_metadata,  # pylint: disable=no-member
                                              fields='id').execute()
            new_folder = new_file.get('id', None)
            set_gd_folder(new_folder)
            gd_fix_subdirs(service, new_folder)
            if new_folder is not None:
                active_folder = {'id': new_folder, 'name': 'docassemble'}
                items.append(active_folder)
                item_ids.append(new_folder)
            flash(word("Your Playground is connected to your Google Drive."), 'success')
        elif form.folder.data in item_ids:
            flash(word("Your Playground is connected to your Google Drive."), 'success')
            set_gd_folder(form.folder.data)
            gd_fix_subdirs(service, form.folder.data)
        else:
            flash(word("The supplied folder " + str(form.folder.data) + "could not be found."), 'error')
            set_gd_folder(None)
        return redirect(url_for('user.profile'))
    the_folder = get_gd_folder()
    active_folder = None
    if the_folder is not None:
        try:
            response = service.files().get(fileId=the_folder, fields="mimeType, trashed").execute()  # pylint: disable=no-member
        except:
            set_gd_folder(None)
            return redirect(url_for('develop.google_drive_page'))
        the_mime_type = response.get('mimeType', None)
        trashed = response.get('trashed', False)
        if trashed is False and the_mime_type == "application/vnd.google-apps.folder":
            active_folder = {'id': the_folder, 'name': response.get('name', 'no name')}
            if the_folder not in item_ids:
                items.append(active_folder)
        else:
            set_gd_folder(None)
            the_folder = None
            flash(word("The mapping was reset because the folder does not appear to exist anymore."), 'error')
    if the_folder is None:
        for item in items:
            if item['name'].lower() == 'docassemble':
                active_folder = item
                break
    if active_folder is None:
        active_folder = {'id': -1, 'name': 'docassemble'}
        items.append(active_folder)
        item_ids.append(-1)
    if the_folder is not None:
        gd_fix_subdirs(service, the_folder)
    if the_folder is None:
        the_folder = ''
    description = 'Select the folder from your Google Drive that you want to be synchronized with the Playground.'
    if current_app.config['USE_ONEDRIVE'] is True and get_od_folder() is not None:
        description += '  ' + word('Note that if you connect to a Google Drive folder, you will disable your connection to OneDrive.')

    response = make_response(render_template('develop/googledrive.html', version_warning=version_warning, description=description, bodyclass='daadminbody', header=word('Google Drive'), tab_title=word('Google Drive'), items=items, the_folder=the_folder, page_title=word('Google Drive'), form=form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def gd_fix_subdirs(service, the_folder):
    subdirs = []
    page_token = None
    while True:
        response = service.files().list(spaces="drive", pageToken=page_token, fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and '" + str(the_folder) + "' in parents").execute()
        for the_file in response.get('files', []):
            subdirs.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    todo = set(['questions', 'static', 'sources', 'templates', 'modules', 'packages'])
    done = set(x['name'] for x in subdirs if x['name'] in todo)
    for key in todo - done:
        file_metadata = {
            'name': key,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [the_folder]
        }
        service.files().create(body=file_metadata,
                               fields='id').execute()


@develop_bp.route('/onedrive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def onedrive_page():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if current_app.config['USE_ONEDRIVE'] is False:
        flash(word("OneDrive is not configured"), "error")
        return redirect(url_for('user.profile'))
    form = OneDriveForm(request.form)
    if request.method == 'POST' and form.cancel.data:
        return redirect(url_for('user.profile'))
    storage = RedisCredStorage(oauth_app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_od_flow()
        uri = flow.step1_get_authorize_url()
        logmessage("one_drive_page: uri is " + str(uri))
        return redirect(uri)
    items = [{'id': '', 'name': word('-- Do not link --')}]
    http = credentials.authorize(httplib2.Http())
    try:
        resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/root/children?$select=id,name,deleted,folder", "GET")
    except:
        set_od_folder(None)
        storage.release_lock()
        storage.locked_delete()
        flow = get_od_flow()
        uri = flow.step1_get_authorize_url()
        logmessage("one_drive_page: uri is " + str(uri))
        return redirect(uri)
    while True:
        if int(resp['status']) != 200:
            flash("Error: could not connect to OneDrive; response code was " + str(resp['status']) + ".   " + content.decode(), 'danger')
            return redirect(url_for('user.profile'))
        info = json.loads(content.decode())
        for item in info['value']:
            if 'folder' not in item:
                continue
            items.append({'id': item['id'], 'name': item['name']})
        if "@odata.nextLink" not in info:
            break
        resp, content = http.request(info["@odata.nextLink"], "GET")
    item_ids = [x['id'] for x in items if x['id'] != '']
    if request.method == 'POST' and form.submit.data:
        if form.folder.data == '':
            set_od_folder(None)
            storage.locked_delete()
            flash(word("OneDrive is not linked."), 'success')
        elif form.folder.data in (-1, '-1'):
            headers = {'Content-Type': 'application/json'}
            info = {}
            info['name'] = 'docassemble'
            info['folder'] = {}
            info["@microsoft.graph.conflictBehavior"] = "fail"
            resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/root/children", "POST", headers=headers, body=json.dumps(info))
            if int(resp['status']) == 201:
                new_item = json.loads(content.decode())
                set_od_folder(new_item['id'])
                od_fix_subdirs(http, new_item['id'])
                flash(word("Your Playground is connected to your OneDrive."), 'success')
            else:
                flash(word("Could not create folder.  " + content.decode()), 'danger')
        elif form.folder.data in item_ids:
            set_od_folder(form.folder.data)
            od_fix_subdirs(http, form.folder.data)
            flash(word("Your Playground is connected to your OneDrive."), 'success')
        else:
            flash(word("The supplied folder " + str(form.folder.data) + "could not be found."), 'danger')
            set_od_folder(None)
        return redirect(url_for('user.profile'))
    the_folder = get_od_folder()
    active_folder = None
    if the_folder is not None:
        resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(the_folder), "GET")
        if int(resp['status']) != 200:
            set_od_folder(None)
            flash(word("The previously selected OneDrive folder does not exist.") + "  " + str(the_folder) + " " + str(content) + " status: " + repr(resp['status']), "info")
            return redirect(url_for('develop.onedrive_page'))
        info = json.loads(content.decode())
        logmessage("Found " + repr(info))
        if info.get('deleted', None):
            set_od_folder(None)
            flash(word("The previously selected OneDrive folder was deleted."), "info")
            return redirect(url_for('develop.onedrive_page'))
        active_folder = {'id': the_folder, 'name': info.get('name', 'no name')}
        if the_folder not in item_ids:
            items.append(active_folder)
            item_ids.append(the_folder)
    if the_folder is None:
        for item in items:
            if item['name'].lower() == 'docassemble':
                active_folder = item
                break
    if active_folder is None:
        active_folder = {'id': -1, 'name': 'docassemble'}
        items.append(active_folder)
        item_ids.append(-1)
    if the_folder is not None:
        od_fix_subdirs(http, the_folder)
    if the_folder is None:
        the_folder = ''
    description = word('Select the folder from your OneDrive that you want to be synchronized with the Playground.')
    if current_app.config['USE_GOOGLE_DRIVE'] is True and get_gd_folder() is not None:
        description += '  ' + word('Note that if you connect to a OneDrive folder, you will disable your connection to Google Drive.')
    response = make_response(render_template('develop/onedrive.html', version_warning=version_warning, bodyclass='daadminbody', header=word('OneDrive'), tab_title=word('OneDrive'), items=items, the_folder=the_folder, page_title=word('OneDrive'), form=form, description=Markup(description)), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def od_fix_subdirs(http, the_folder):
    subdirs = set()
    resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
    while True:
        if int(resp['status']) != 200:
            raise DAError("od_fix_subdirs: could not get contents of folder")
        info = json.loads(content.decode())
        logmessage("Found " + repr(info))
        for item in info['value']:
            if 'folder' in item:
                subdirs.add(item['name'])
        if "@odata.nextLink" not in info:
            break
        resp, content = http.request(info["@odata.nextLink"], "GET")
    todo = set(['questions', 'static', 'sources', 'templates', 'modules', 'packages'])
    for folder_name in (todo - subdirs):
        headers = {'Content-Type': 'application/json'}
        data = {}
        data['name'] = folder_name
        data['folder'] = {}
        data["@microsoft.graph.conflictBehavior"] = "rename"
        resp, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + str(the_folder) + "/children", "POST", headers=headers, body=json.dumps(data))
        if int(resp['status']) != 201:
            raise DAError("od_fix_subdirs: could not create subfolder " + folder_name + ' in ' + str(the_folder) + '.  ' + content.decode() + ' status: ' + str(resp['status']))


@develop_bp.route('/view_source', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def view_source():
    setup_translation()
    source_path = request.args.get('i', None)
    playground_user = get_playground_user()
    current_project = get_current_project()
    if source_path is None:
        logmessage("view_source: no source path")
        return ('File not found', 404)
    try:
        if re.search(r':', source_path):
            source = interview_source_from_string(source_path)
        else:
            try:
                source = interview_source_from_string('docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + source_path)
            except:
                source = interview_source_from_string(source_path)
    except BaseException as errmess:
        logmessage("view_source: no source: " + str(errmess))
        return ('File not found', 404)
    header = source_path
    response = make_response(render_template('develop/view_source.html', version_warning=None, bodyclass='daadminbody', tab_title="Source", page_title="Source", extra_css=Markup('\n    <link href="' + url_for('static', filename='app/pygments.min.css') + '" rel="stylesheet">'), header=header, contents=Markup(highlight(source.content, YamlLexer(), HtmlFormatter(cssclass="highlight dahighlight dafullheight")))), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/playgroundstatic/<current_project>/<userid>/<path:filename>', methods=['GET'])
def playground_static(current_project, userid, filename):
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    # filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    try:
        attach = int(request.args.get('attach', 0))
    except:
        attach = 0
    area = SavedFile(userid, fix=True, section='playgroundstatic')
    the_directory = directory_for(area, current_project)
    filename = filename.replace('/', os.path.sep)
    path = os.path.join(the_directory, filename)
    if os.path.join('..', '') in path:
        return ('File not found', 404)
    if os.path.isfile(path):
        filename = os.path.basename(filename)
        extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
        response = custom_send_file(path, mimetype=str(mimetype), download_name=filename)
        if attach:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename))
        return response
    return ('File not found', 404)


@develop_bp.route('/playgroundmodules/<current_project>/<userid>/<path:filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_modules(current_project, userid, filename):
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    # filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    try:
        attach = int(request.args.get('attach', 0))
    except:
        attach = 0
    area = SavedFile(userid, fix=True, section='playgroundmodules')
    the_directory = directory_for(area, current_project)
    filename = filename.replace('/', os.path.sep)
    path = os.path.join(the_directory, filename)
    if os.path.join('..', '') in path:
        return ('File not found', 404)
    if os.path.isfile(path):
        filename = os.path.basename(filename)
        extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
        response = custom_send_file(path, mimetype=str(mimetype), download_name=filename)
        if attach:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    return ('File not found', 404)


@develop_bp.route('/playgroundsources/<current_project>/<userid>/<path:filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_sources(current_project, userid, filename):
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    try:
        attach = int(request.args.get('attach', 0))
    except:
        attach = 0
    # filename = re.sub(r'[^A-Za-z0-9\-\_\(\)\. ]', '', filename)
    filename = filename.replace('/', os.path.sep)
    area = SavedFile(userid, fix=True, section='playgroundsources')
    write_ml_source(area, userid, current_project, filename)
    the_directory = directory_for(area, current_project)
    path = os.path.join(the_directory, filename)
    if os.path.join('..', '') in path:
        return ('File not found', 404)
    if os.path.isfile(path):
        filename = os.path.basename(filename)
        extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
        response = custom_send_file(path, mimetype=str(mimetype), download_name=filename)
        if attach:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    return ('File not found', 404)


@develop_bp.route('/playgroundtemplate/<current_project>/<userid>/<path:filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_template(current_project, userid, filename):
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    # filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    setup_translation()
    try:
        attach = int(request.args.get('attach', 0))
    except:
        attach = 0
    area = SavedFile(userid, fix=True, section='playgroundtemplate')
    the_directory = directory_for(area, current_project)
    filename = filename.replace('/', os.path.sep)
    path = os.path.join(the_directory, filename)
    if os.path.join('..', '') in path:
        return ('File not found', 404)
    if os.path.isfile(path):
        filename = os.path.basename(filename)
        extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
        response = custom_send_file(path, mimetype=str(mimetype), download_name=filename)
        if attach:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    return ('File not found', 404)


@develop_bp.route('/playgrounddownload/<current_project>/<userid>/<path:filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_download(current_project, userid, filename):
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    # filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    area = SavedFile(userid, fix=True, section='playground')
    the_directory = directory_for(area, current_project)
    filename = filename.replace('/', os.path.sep)
    path = os.path.join(the_directory, filename)
    if os.path.join('..', '') in path:
        return ('File not found', 404)
    if os.path.isfile(path):
        filename = os.path.basename(filename)
        extension, mimetype = get_ext_and_mimetype(path)  # pylint: disable=unused-variable
        response = custom_send_file(path, mimetype=str(mimetype))
        response.headers['Content-type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    return ('File not found', 404)


@develop_bp.route('/officefunctionfile', methods=['GET', 'POST'])
@cross_origin(origins='*', methods=['GET', 'POST', 'HEAD'], automatic_options=True)
def playground_office_functionfile():
    g.embed = True
    set_language(DEFAULT_LANGUAGE)
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    functionform = FunctionFileForm(request.form)
    response = make_response(render_template('develop/officefunctionfile.html', current_project=get_current_project(), page_title=word("Docassemble Playground"), tab_title=word("Playground"), parent_origin=daconfig.get('office addin url', daconfig.get('url root', get_base_url())), form=functionform), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/officetaskpane', methods=['GET', 'POST'])
@cross_origin(origins='*', methods=['GET', 'POST', 'HEAD'], automatic_options=True)
def playground_office_taskpane():
    g.embed = True
    set_language(DEFAULT_LANGUAGE)
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    default_da_server = url_for('interview.rootindex', _external=True)
    response = make_response(render_template('develop/officeouter.html', page_title=word("Docassemble Playground"), tab_title=word("Playground"), default_da_server=default_da_server, extra_js=Markup(f"\n        <script{DEFER}>{indent_by(variables_js(office_mode=True), 9)}        </script>")), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/officeaddin', methods=['GET', 'POST'])
@cross_origin(origins='*', methods=['GET', 'POST', 'HEAD'], automatic_options=True)
@login_required
@roles_required(['developer', 'admin'])
def playground_office_addin():
    g.embed = True
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    playground_user = get_playground_user()
    project_to_use = werkzeug.utils.secure_filename(request.args.get('project', get_current_project()))
    if request.args.get('fetchfiles', None):
        playground = SavedFile(playground_user.id, fix=True, section='playground')
        the_directory = directory_for(playground, project_to_use)
        if not os.path.isdir(the_directory):
            return ('File not found', 404)
        files = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        return jsonify(success=True, files=files, projects=get_list_of_projects(playground_user.id))
    pg_var_file = request.args.get('pgvars', None)
    # logmessage("playground_office_addin: YAML file is " + str(pg_var_file))
    use_html = request.args.get('html', False)
    uploadform = AddinUploadForm(request.form)
    if request.method == 'POST':
        area = SavedFile(playground_user.id, fix=True, section='playgroundtemplate')
        filename = secure_filename(uploadform.filename.data)
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', filename)
        if filename == '':
            return jsonify({'success': False})
        content = str(uploadform.content.data)
        start_index = 0
        char_index = 0
        for char in content:
            char_index += 1
            if char == ',':
                start_index = char_index
                break
        area.write_content(codecs.decode(bytearray(content[start_index:], encoding='utf-8'), 'base64'), filename=filename, binary=True, project=project_to_use)
        area.finalize()
        if use_html:
            if pg_var_file is None:
                pg_var_file = ''
        else:
            if pg_var_file is None or pg_var_file == '':
                return jsonify({'success': True, 'variables_json': [], 'vocab_list': []})
    if pg_var_file is not None:
        playground = SavedFile(playground_user.id, fix=True, section='playground')
        the_directory = directory_for(playground, project_to_use)
        files = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        if pg_var_file in files:
            # logmessage("playground_office_addin: file " + str(pg_var_file) + " was found")
            interview_source = interview_source_from_string('docassemble.playground' + str(playground_user.id) + project_name(project_to_use) + ':' + pg_var_file, raise_jinja_errors=False)
            interview_source.set_testing(True)
        else:
            # logmessage("playground_office_addin: file " + str(pg_var_file) + " was not found")
            if pg_var_file == '' and project_to_use == 'default':
                pg_var_file = 'test.yml'
            content = "modules:\n  - docassemble.base.util\n---\nmandatory: True\nquestion: hi"
            interview_source = InterviewSourceString(content=content, directory=the_directory, package="docassemble.playground" + str(playground_user.id) + project_name(project_to_use), path="docassemble.playground" + str(playground_user.id) + project_name(project_to_use) + ":" + pg_var_file, testing=True)
        interview = Interview(source=interview_source)
        ensure_ml_file_exists(interview, pg_var_file, project_to_use)
        the_current_info = current_info(yaml='docassemble.playground' + str(playground_user.id) + project_name(project_to_use) + ':' + pg_var_file, req=request, action=None, device_id=request.cookies.get('ds', None))
        this_thread.current_info = the_current_info
        interview_status = InterviewStatus(current_info=the_current_info)
        if use_html:
            variables_html, vocab_list, vocab_dict, ac_list = get_vars_in_use(interview, interview_status, debug_mode=False, show_messages=False, show_jinja_help=True, current_project=project_to_use)  # pylint: disable=unused-variable
            return jsonify({'success': True, 'current_project': project_to_use, 'variables_html': variables_html, 'vocab_list': list(vocab_list), 'vocab_dict': vocab_dict})
        variables_json, vocab_list, vocab_dict, ac_list = get_vars_in_use(interview, interview_status, debug_mode=False, return_json=True, current_project=project_to_use)
        return jsonify({'success': True, 'variables_json': variables_json, 'vocab_list': list(vocab_list)})
    parent_origin = re.sub(r'^(https?://[^/]+)/.*', r'\1', daconfig.get('office addin url', get_base_url()))
    response = make_response(render_template('develop/officeaddin.html', current_project=project_to_use, page_title=word("Docassemble Office Add-in"), tab_title=word("Office Add-in"), parent_origin=parent_origin, form=uploadform), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def cloud_trash(use_gd, use_od, section, the_file, current_project):
    if use_gd:
        try:
            trash_gd_file(section, the_file, current_project)
        except BaseException as the_err:
            logmessage("cloud_trash: unable to delete file on Google Drive.  " + str(the_err))
    elif use_od:
        try:
            trash_od_file(section, the_file, current_project)
        except BaseException as the_err:
            try:
                logmessage("cloud_trash: unable to delete file on OneDrive.  " + str(the_err))
            except:
                logmessage("cloud_trash: unable to delete file on OneDrive.")


@develop_bp.route('/playgroundfiles', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_files():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    playground_user = get_playground_user()
    current_project = get_current_project()
    use_gd = bool(current_app.config['USE_GOOGLE_DRIVE'] is True and get_gd_folder() is not None)
    use_od = bool(use_gd is False and current_app.config['USE_ONEDRIVE'] is True and get_od_folder() is not None)
    form = PlaygroundFilesForm(request.form)
    formtwo = PlaygroundFilesEditForm(request.form)
    is_ajax = bool('ajax' in request.form and int(request.form['ajax']))
    section = werkzeug.utils.secure_filename(request.args.get('section', 'template'))
    the_file = secure_filename_spaces_ok(request.args.get('file', ''))
    scroll = False
    if the_file != '':
        scroll = True
    if request.method == 'GET':
        is_new = true_or_false(request.args.get('new', False))
    else:
        is_new = False
    if is_new:
        scroll = True
        the_file = ''
    if request.method == 'POST':
        form_validated = bool((form.purpose.data == 'upload' and form.validate()) or (formtwo.purpose.data == 'edit' and formtwo.validate()))
        if form_validated:
            if form.section.data:
                section = form.section.data
            if formtwo.file_name.data:
                the_file = formtwo.file_name.data
                the_file = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', the_file)
    else:
        form_validated = None
    if section not in ("template", "static", "sources", "modules", "packages"):
        section = "template"
    pgarea = SavedFile(playground_user.id, fix=True, section='playground')
    the_directory = directory_for(pgarea, current_project)
    if current_project != 'default' and not os.path.isdir(the_directory):
        current_project = set_current_project('default')
        the_directory = directory_for(pgarea, current_project)
    dropdown_files = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    current_variable_file = get_variable_file(current_project)
    if current_variable_file is not None:
        if current_variable_file in dropdown_files:
            active_file = current_variable_file
        else:
            delete_variable_file(current_project)
            active_file = None
    else:
        active_file = None
    if active_file is None:
        current_file = get_current_file(current_project, 'questions')
        if current_file in dropdown_files:
            active_file = current_file
        elif len(dropdown_files) > 0:
            delete_current_file(current_project, 'questions')
            active_file = dropdown_files[0]
        else:
            delete_current_file(current_project, 'questions')
    area = SavedFile(playground_user.id, fix=True, section='playground' + section)
    the_directory = directory_for(area, current_project)
    if request.args.get('delete', False):
        # argument = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', request.args.get('delete'))
        argument = request.args.get('delete')
        if argument:
            the_directory = directory_for(area, current_project)
            the_file = add_project(argument, current_project)
            filename = os.path.join(the_directory, argument)
            if os.path.exists(filename):
                os.remove(filename)
                area.finalize()
                for key in r.keys('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':*'):
                    r.incr(key.decode())
                cloud_trash(use_gd, use_od, section, argument, current_project)
                flash(word("Deleted file: ") + the_file, "success")
                for key in r.keys('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':*'):
                    r.incr(key.decode())
                return redirect(url_for('develop.playground_files', section=section, project=current_project))
            flash(word("File not found: ") + argument, "error")
    if request.args.get('convert', False):
        # argument = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', request.args.get('convert'))
        argument = request.args.get('convert')
        if argument:
            filename = os.path.join(the_directory, argument)
            if os.path.exists(filename):
                to_file = os.path.splitext(argument)[0] + '.md'
                to_path = os.path.join(the_directory, to_file)
                if not os.path.exists(to_path):
                    extension, mimetype = get_ext_and_mimetype(argument)
                    if mimetype and mimetype in convertible_mimetypes:
                        the_format = convertible_mimetypes[mimetype]
                    elif extension and extension in convertible_extensions:
                        the_format = convertible_extensions[extension]
                    else:
                        flash(word("File format not understood: ") + argument, "error")
                        return redirect(url_for('develop.playground_files', section=section, project=current_project))
                    if CAN_CONVERT_WORD:
                        result = word_to_markdown(filename, the_format)
                    else:
                        result = None
                    if result is None:
                        flash(word("File could not be converted: ") + argument, "error")
                        return redirect(url_for('develop.playground_files', section=section, project=current_project))
                    shutil.copyfile(result.name, to_path)
                    flash(word("Created new Markdown file called ") + to_file + word("."), "success")
                    area.finalize()
                    return redirect(url_for('develop.playground_files', section=section, file=to_file, project=current_project))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.method == 'POST' and form_validated:
        if 'uploadfile' in request.files:
            the_files = request.files.getlist('uploadfile')
            if the_files:
                need_to_restart = False
                for up_file in the_files:
                    try:
                        filename = werkzeug.utils.secure_filename(up_file.filename)
                        extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
                        if section == 'modules' and extension != 'py':
                            flash(word("Sorry, only .py files can be uploaded here.  To upload other types of files, use other Folders."), 'error')
                            return redirect(url_for('develop.playground_files', section=section, project=current_project))
                        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', filename)
                        the_file = filename
                        filename = os.path.join(the_directory, filename)
                        up_file.save(filename)
                        for key in r.keys('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':*'):
                            r.incr(key.decode())
                        area.finalize()
                        if section == 'modules':
                            need_to_restart = True
                    except BaseException as err_mess:
                        flash("Error of type " + str(type(err_mess)) + " processing upload: " + str(err_mess), "error")
                if need_to_restart:
                    flash(word('Since you uploaded a Python module, the server needs to restart in order to load your module.'), 'info')
                    return redirect(url_for('main.restart_page', next=url_for('develop.playground_files', section=section, file=the_file, project=current_project)))
                flash(word("Upload successful"), "success")
        if formtwo.delete.data:
            if the_file != '':
                filename = os.path.join(the_directory, the_file)
                if os.path.exists(filename):
                    os.remove(filename)
                    for key in r.keys('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':*'):
                        r.incr(key.decode())
                    area.finalize()
                    flash(word("Deleted file: ") + the_file, "success")
                    return redirect(url_for('develop.playground_files', section=section, project=current_project))
                flash(word("File not found: ") + the_file, "error")
        if formtwo.submit.data and formtwo.file_content.data:
            if the_file != '':
                if section == 'modules' and not re.search(r'\.py$', the_file):
                    the_file = re.sub(r'\..*', '', the_file) + '.py'
                if formtwo.original_file_name.data and formtwo.original_file_name.data != the_file:
                    old_filename = os.path.join(the_directory, formtwo.original_file_name.data)
                    cloud_trash(use_gd, use_od, section, formtwo.original_file_name.data, current_project)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                filename = os.path.join(the_directory, the_file)
                with open(filename, 'w', encoding='utf-8') as fp:
                    fp.write(re.sub(r'\r\n', r'\n', formtwo.file_content.data))
                the_time = formatted_current_time()
                for key in r.keys('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':*'):
                    r.incr(key.decode())
                area.finalize()
                if formtwo.active_file.data and formtwo.active_file.data != the_file:
                    # interview_file = os.path.join(pgarea.directory, formtwo.active_file.data)
                    r.incr('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + formtwo.active_file.data)
                    # if os.path.isfile(interview_file):
                    #     with open(interview_file, 'a'):
                    #         os.utime(interview_file, None)
                    #     pgarea.finalize()
                flash_message = flash_as_html(str(the_file) + ' ' + word('was saved at') + ' ' + the_time + '.', message_type='success', is_ajax=is_ajax)
                if section == 'modules':
                    # restart_all()
                    flash(word('Since you changed a Python module, the server needs to restart in order to load your module.'), 'info')
                    return redirect(url_for('main.restart_page', next=url_for('develop.playground_files', section=section, file=the_file, project=current_project)))
                if is_ajax:
                    return jsonify(success=True, flash_message=flash_message)
                return redirect(url_for('develop.playground_files', section=section, file=the_file, project=current_project))
            flash(word('You need to type in a name for the file'), 'error')
    if is_ajax and not form_validated:
        errors = []
        for field_name, error_messages in formtwo.errors.items():
            for err in error_messages:
                errors.append({'fieldName': field_name, 'err': err})
        return jsonify(success=False, errors=errors)
    files = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])

    editable_files = []
    convertible_files = []
    trainable_files = {}
    mode = "yml"
    for a_file in files:
        extension, mimetype = get_ext_and_mimetype(a_file)
        if (mimetype and mimetype in ok_mimetypes) or (extension and extension in ok_extensions) or (mimetype and mimetype.startswith('text')):
            if section == 'sources' and re.match(r'ml-.*\.json$', a_file):
                trainable_files[a_file] = re.sub(r'^ml-|\.json$', '', a_file)
            else:
                editable_files.append({'name': a_file, 'modtime': os.path.getmtime(os.path.join(the_directory, a_file))})
    assign_opacity(editable_files)
    editable_file_listing = [x['name'] for x in editable_files]
    if CAN_CONVERT_WORD:
        for a_file in files:
            extension, mimetype = get_ext_and_mimetype(a_file)
            b_file = os.path.splitext(a_file)[0] + '.md'
            if b_file not in editable_file_listing and ((mimetype and mimetype in convertible_mimetypes) or (extension and extension in convertible_extensions)):
                convertible_files.append(a_file)
    if the_file and not is_new and the_file not in editable_file_listing:
        the_file = ''
    if not the_file and not is_new:
        current_file = get_current_file(current_project, section)
        if current_file in editable_file_listing:
            the_file = current_file
        else:
            delete_current_file(current_project, section)
            if len(editable_files) > 0:
                the_file = sorted(editable_files, key=lambda x: x['modtime'])[-1]['name']
            else:
                if section == 'modules':
                    the_file = 'test.py'
                elif section == 'sources':
                    the_file = 'test.json'
                else:
                    the_file = 'test.md'
    if the_file in editable_file_listing:
        set_current_file(current_project, section, the_file)
    if the_file != '':
        mode, mimetype = get_ext_and_mimetype(the_file)
    if mode != 'md':
        active_file = None
    if section == 'modules':
        mode = 'py'
    formtwo.original_file_name.data = the_file
    formtwo.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(the_directory, the_file)):
        filename = os.path.join(the_directory, the_file)
    else:
        filename = None
    if filename is not None:
        area.finalize()
        with open(filename, 'r', encoding='utf-8') as fp:
            try:
                content = fp.read()
            except:
                filename = None
                content = ''
    elif formtwo.file_content.data:
        content = re.sub(r'\r\n', r'\n', formtwo.file_content.data)
    else:
        content = ''
    lowerdescription = None
    description = None
    if section == "template":
        header = word("Templates")
        description = 'Add files here that you want want to include in your interviews using <a target="_blank" href="https://docassemble.org/docs/documents.html#docx template file"><code>docx template file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#pdf template file"><code>pdf template file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#content file"><code>content file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#initial yaml"><code>initial yaml</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#additional yaml"><code>additional yaml</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#template file"><code>template file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#rtf template file"><code>rtf template file</code></a>, or <a target="_blank" href="https://docassemble.org/docs/documents.html#docx reference file"><code>docx reference file</code></a>.'
        upload_header = word("Upload a template file")
        list_header = word("Existing template files")
        edit_header = word('Edit text files')
        after_text = None
    elif section == "static":
        header = word("Static Files")
        description = 'Add files here that you want to include in your interviews with <a target="_blank" href="https://docassemble.org/docs/initial.html#images"><code>images</code></a>, <a target="_blank" href="https://docassemble.org/docs/initial.html#image sets"><code>image sets</code></a>, <a target="_blank" href="https://docassemble.org/docs/markup.html#inserting%20images"><code>[FILE]</code></a> or <a target="_blank" href="https://docassemble.org/docs/functions.html#url_of"><code>url_of()</code></a>.'
        upload_header = word("Upload a static file")
        list_header = word("Existing static files")
        edit_header = word('Edit text files')
        after_text = None
    elif section == "sources":
        header = word("Source Files")
        description = 'Add files here that you want to use as a data source in your interview code, such as word translation files and training data for machine learning.  For Python source code, see the Modules folder.'
        upload_header = word("Upload a source file")
        list_header = word("Existing source files")
        edit_header = word('Edit source files')
        after_text = None
    else:  # section == "modules":
        header = word("Modules")
        upload_header = word("Upload a Python module")
        list_header = word("Existing module files")
        edit_header = word('Edit module files')
        description = 'You can use this page to add Python module files (.py files) that you want to include in your interviews using <a target="_blank" href="https://docassemble.org/docs/initial.html#modules"><code>modules</code></a> or <a target="_blank" href="https://docassemble.org/docs/initial.html#imports"><code>imports</code></a>.'
        lowerdescription = Markup("""<p>To use this in an interview, write a <a target="_blank" href="https://docassemble.org/docs/initial.html#modules"><code>modules</code></a> block that refers to this module using Python's syntax for specifying a "relative import" of a module (i.e., prefix the module name with a period).</p>""" + highlight('---\nmodules:\n  - .' + re.sub(r'\.py$', '', the_file) + '\n---', YamlLexer(), HtmlFormatter(cssclass='highlight dahighlight')) + """<p>If you wish to refer to this module from another package, you can use a fully qualified reference.</p>""" + highlight('---\nmodules:\n  - ' + "docassemble.playground" + str(playground_user.id) + project_name(current_project) + "." + re.sub(r'\.py$', '', the_file) + '\n---', YamlLexer(), HtmlFormatter(cssclass='highlight dahighlight')))
        after_text = None
    initial_values = playground_values(current_project, the_file, playground_user)
    initial_values.update({
        "daPage": 'files',
        "daScroll": bool(scroll),
        "isNew": bool(is_new),
        "existingFiles": files,
        "daSection": section,
        "daUrlPlaygroundFiles": url_for('develop.playground_files', project=current_project),
        "daContent": content,
        "daMode": mode
    })
    extra_js = f"""
    <script{DEFER} src="{url_for('static', filename="app/playgroundbundle.min.js", v=da_version)}"></script>
    {redis_script(initial_values)}
"""
    any_files = bool(len(editable_files) > 0)
    back_button = Markup('<span class="navbar-brand navbar-nav dabackicon me-3"><a href="' + url_for('develop.playground_page', project=current_project) + '" class="dabackbuttoncolor nav-link" title=' + json.dumps(word("Go back to the main Playground page")) + '><i class="fa-solid fa-chevron-left"></i><span class="daback">' + word('Back') + '</span></a></span>')
    if current_user.id != playground_user.id:
        header += " / " + playground_user.email
    if current_project != 'default':
        header += " / " + current_project
    response = make_response(render_template('develop/playgroundfiles.html', current_project=current_project, version_warning=None, bodyclass='daadminbody', use_gd=use_gd, use_od=use_od, back_button=back_button, tab_title=header, page_title=header, extra_css=Markup('\n    <link href="' + url_for('static', filename='app/playgroundbundle.css', v=da_version) + '" rel="stylesheet">'), extra_js=Markup(extra_js), header=header, upload_header=upload_header, list_header=list_header, edit_header=edit_header, description=Markup(description), lowerdescription=lowerdescription, form=form, files=sorted(files, key=lambda y: y.lower()), section=section, userid=playground_user.id, editable_files=sorted(editable_files, key=lambda y: y['name'].lower()), editable_file_listing=editable_file_listing, trainable_files=trainable_files, convertible_files=convertible_files, formtwo=formtwo, current_file=the_file, content=content, after_text=after_text, is_new=str(is_new), any_files=any_files, dropdown_files=sorted(dropdown_files, key=lambda y: y.lower()), active_file=active_file, playground_package='docassemble.playground' + str(playground_user.id) + project_name(current_project), own_playground=bool(playground_user.id == current_user.id)), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/pullplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def pull_playground_package():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    current_project = get_current_project()
    form = PullPlaygroundPackage(request.form)
    if request.method == 'POST':
        if form.pull.data:
            if form.github_url.data and form.pypi.data:
                flash(word("You cannot pull from GitHub and PyPI at the same time.  Please fill in one and leave the other blank."), 'error')
            elif form.github_url.data:
                return redirect(url_for('develop.playground_packages', project=current_project, pull='1', github_url=re.sub(r'/*$', '', str(form.github_url.data).strip()), branch=form.github_branch.data))
            elif form.pypi.data:
                return redirect(url_for('develop.playground_packages', project=current_project, pull='1', pypi=form.pypi.data))
        if form.cancel.data:
            return redirect(url_for('develop.playground_packages', project=current_project))
    elif 'github' in request.args:
        form.github_url.data = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['github'])
    elif 'pypi' in request.args:
        form.pypi.data = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['pypi'])
    form.github_branch.choices = []
    description = word("Enter a URL of a GitHub repository containing an extension package.  When you press Pull, the contents of that repository will be copied into the Playground, overwriting any files with the same names.  Or, put in the name of a PyPI package and it will do the same with the package on PyPI.")
    branch = request.args.get('branch')
    initial_values = {
        "daDefaultBranch": branch if branch else GITHUB_BRANCH,
        "daGetGitBranches": url_for('packages.get_git_branches'),
        "daGithubBranch": GITHUB_BRANCH
    }
    extra_js = f"""
    <script{DEFER} src="{url_for('static', filename='app/pullplaygroundpackage.min.js')}"></script>
    <script{DEFER}>Object.assign(window, {json.dumps(initial_values)})</script>
"""
    response = make_response(render_template('develop/pull_playground_package.html',
                                             current_project=current_project,
                                             form=form,
                                             description=description,
                                             version_warning=version_warning,
                                             bodyclass='daadminbody',
                                             title=word("Pull GitHub or PyPI Package"),
                                             tab_title=word("Pull"),
                                             page_title=word("Pull"),
                                             extra_js=Markup(extra_js)), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def get_user_repositories(http):
    repositories = []
    resp, content = http.request("https://api.github.com/user/repos", "GET")
    if int(resp['status']) == 200:
        repositories.extend(json.loads(content.decode()))
        while True:
            next_link = get_next_link(resp)
            if next_link:
                resp, content = http.request(next_link, "GET")
                if int(resp['status']) != 200:
                    raise DAError("get_user_repositories: could not get information from next URL")
                repositories.extend(json.loads(content.decode()))
            else:
                break
    else:
        raise DAError("playground_packages: could not get information about repositories")
    return repositories


def get_orgs_info(http):
    orgs_info = []
    resp, content = http.request("https://api.github.com/user/orgs", "GET")
    if int(resp['status']) == 200:
        orgs_info.extend(json.loads(content.decode()))
        while True:
            next_link = get_next_link(resp)
            if next_link:
                resp, content = http.request(next_link, "GET")
                if int(resp['status']) != 200:
                    raise DAError("get_orgs_info: could not get additional information about organizations")
                orgs_info.extend(json.loads(content.decode()))
            else:
                break
    else:
        raise DAError("get_orgs_info: failed to get orgs using https://api.github.com/user/orgs")
    return orgs_info


def get_branch_info(http, full_name):
    branch_info = []
    resp, content = http.request("https://api.github.com/repos/" + str(full_name) + '/branches', "GET")
    if int(resp['status']) == 200:
        branch_info.extend(json.loads(content.decode()))
        while True:
            next_link = get_next_link(resp)
            if next_link:
                resp, content = http.request(next_link, "GET")
                if int(resp['status']) != 200:
                    raise DAError("get_branch_info: could not get additional information from next URL")
                branch_info.extend(json.loads(content))
            else:
                break
    else:
        logmessage("get_branch_info: could not get info from https://api.github.com/repos/" + str(full_name) + '/branches')
    return branch_info


def fix_package_folder():
    playground_user = get_playground_user()
    use_gd = bool(current_app.config['USE_GOOGLE_DRIVE'] is True and get_gd_folder() is not None)
    use_od = bool(use_gd is False and current_app.config['USE_ONEDRIVE'] is True and get_od_folder() is not None)
    problem_exists = False
    area = SavedFile(playground_user.id, fix=True, section='playgroundpackages')
    for f in os.listdir(area.directory):
        path = os.path.join(area.directory, f)
        if os.path.isfile(path) and not f.startswith('docassemble.') and not f.startswith('.'):
            os.rename(path, os.path.join(area.directory, 'docassemble.' + f))
            cloud_trash(use_gd, use_od, 'packages', f, 'default')
            problem_exists = True
        if os.path.isdir(path) and not f.startswith('.'):
            for e in os.listdir(path):
                if os.path.isfile(os.path.join(path, e)) and not e.startswith('docassemble.') and not e.startswith('.'):
                    os.rename(os.path.join(path, e), os.path.join(path, 'docassemble.' + e))
                    cloud_trash(use_gd, use_od, 'packages', e, f)
                    problem_exists = True
    if problem_exists:
        area.finalize()


def secure_git_branchname(branch):
    """Makes an input branch name a valid git branch name, and also strips out
  things that would interpolated in bash."""
    # The rules of what's allowed in a git branch name are: https://git-scm.com/docs/git-check-ref-format
    branch = unicodedata.normalize("NFKD", branch)
    branch = branch.encode("ascii", "ignore").decode("ascii")
    branch = re.compile(r"[\u0000-\u0020]|(\")|(@{)|(\.\.)|[\u0170~ ^:?*$`[\\]|(//+)").sub("", branch)
    branch = branch.strip("/")
    # Can include a slash, but no slash-separated component can begin with a dot `.` or end with `.lock`
    branch = "/".join([re.compile(r"\.lock$").sub("", component.lstrip('.')) for component in branch.split("/")])
    branch = branch.rstrip(".")
    if branch == "@":
        branch = "_"
    return branch


def do_playground_pull(area, current_project, github_url=None, branch=None, pypi_package=None, can_publish_to_github=False, github_email=None, pull_only=False):
    playground_user = get_playground_user()
    area_sec = {'templates': 'playgroundtemplate', 'static': 'playgroundstatic', 'sources': 'playgroundsources', 'questions': 'playground'}
    readme_text = ''
    gitignore_text = ''
    setup_py = ''
    pyproject_toml = ''
    if branch in ('', 'None'):
        branch = None
    if branch:
        branch = secure_git_branchname(branch)
        branch_option = ['-b', branch]
    else:
        branch_option = []
    need_to_restart = False
    extracted = {}
    data_files = {'templates': [], 'static': [], 'sources': [], 'interviews': [], 'modules': [], 'questions': []}
    directory = tempfile.mkdtemp(prefix='SavedFile')
    output = ''
    pypi_url = daconfig.get('pypi url', 'https://pypi.org/pypi')
    expected_name = 'unknown'
    if github_url:
        github_url = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\#\[\]\@\$\+\,\=]', '', github_url)
        repo_name = re.sub(r'/*$', '', github_url)
        repo_name = re.sub(r'^http.*github.com/', '', repo_name)
        repo_name = re.sub(r'.*@github.com:', '', repo_name)
        repo_name = re.sub(r'.git$', '', repo_name)
        if 'x-oauth-basic@github.com' not in github_url and can_publish_to_github and github_email:
            github_url = f'git@github.com:{repo_name}.git'
            expected_name = re.sub(r'.*/', '', github_url)
            expected_name = re.sub(r'\.git', '', expected_name)
            expected_name = re.sub(r'docassemble-', '', expected_name)
            (private_key_file, public_key_file) = get_ssh_keys(github_email)
            os.chmod(private_key_file, stat.S_IRUSR | stat.S_IWUSR)
            os.chmod(public_key_file, stat.S_IRUSR | stat.S_IWUSR)
            ssh_script = tempfile.NamedTemporaryFile(mode='w', prefix="datemp", suffix='.sh', delete=False, encoding='utf-8')
            ssh_script.write('# /bin/bash\n\nssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i "' + str(private_key_file) + '" $1 $2 $3 $4 $5 $6')
            ssh_script.close()
            os.chmod(ssh_script.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            # git_prefix = "GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i \"" + str(private_key_file) + "\"' "
            git_prefix = "GIT_SSH=" + ssh_script.name + " "
            git_env = dict(os.environ, GIT_SSH=ssh_script.name)
            output += "Doing " + git_prefix + "git clone " + " ".join(branch_option) + github_url + "\n"
            try:
                output += subprocess.check_output(["git", "clone"] + branch_option + [github_url], cwd=directory, stderr=subprocess.STDOUT, env=git_env).decode()
            except subprocess.CalledProcessError as err:
                output += err.output.decode()
                return {'action': "error", 'message': "error running git clone.  " + output}
        else:
            if not github_url.startswith('http'):
                github_url = f'https://github.com/{repo_name}'
            expected_name = re.sub(r'.*/', '', github_url)
            expected_name = re.sub(r'\.git', '', expected_name)
            expected_name = re.sub(r'docassemble-', '', expected_name)
            try:
                if branch is not None:
                    logmessage("Doing git clone -b " + branch + " " + github_url)
                    output += subprocess.check_output(['git', 'clone', '-b', branch, github_url], cwd=directory, stderr=subprocess.STDOUT).decode()
                else:
                    logmessage("Doing git clone " + github_url)
                    output += subprocess.check_output(['git', 'clone', github_url], cwd=directory, stderr=subprocess.STDOUT).decode()
            except subprocess.CalledProcessError as err:
                output += err.output.decode()
                return {'action': "error", 'message': "error running git clone.  " + output}
        logmessage(output)
        dirs_inside = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f)) and re.search(r'^[A-Za-z0-9]', f)]
        if len(dirs_inside) == 1:
            commit_file = os.path.join(directory_for(area['playgroundpackages'], current_project), '.' + dirs_inside[0])
            packagedir = os.path.join(directory, dirs_inside[0])
            try:
                current_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=packagedir, stderr=subprocess.STDOUT).decode()
            except subprocess.CalledProcessError as err:
                output = err.output.decode()
                return {'action': "error", 'message': "error running git rev-parse.  " + output}
            with open(commit_file, 'w', encoding='utf-8') as fp:
                fp.write(current_commit.strip())
            logmessage("Wrote " + current_commit.strip() + " to " + commit_file)
        else:
            logmessage("Did not find a single directory inside repo")
        if pull_only:
            return {'action': 'pull_only'}
    elif pypi_package:
        pypi_package = re.sub(r'[^A-Za-z0-9\-\.\_\:\/\@\+\=]', '', pypi_package)
        pypi_package = 'docassemble.' + re.sub(r'^docassemble\.', '', pypi_package)
        package_file = tempfile.NamedTemporaryFile(suffix='.tar.gz')
        try:
            http = httplib2.Http()
            resp, content = http.request(pypi_url + "/" + str(pypi_package) + "/json", "GET")
            the_pypi_url = None
            if int(resp['status']) == 200:
                pypi_response = json.loads(content.decode())
                for file_option in pypi_response['releases'][pypi_response['info']['version']]:
                    if file_option['packagetype'] == 'sdist':
                        the_pypi_url = file_option['url']
                        break
            else:
                return {'action': 'fail', 'message': word("The package you specified could not be downloaded from PyPI.")}
            if the_pypi_url is None:
                return {'action': 'fail', 'message': word("The package you specified could not be downloaded from PyPI as a tar.gz file.")}
        except BaseException as err:
            return {'action': 'error', 'message': "error getting information about PyPI package.  " + str(err)}
        try:
            urlretrieve(the_pypi_url, package_file.name)
        except BaseException as err:
            return {'action': 'error', 'message': "error downloading PyPI package.  " + str(err)}
        try:
            tar = tarfile.open(package_file.name)
            tar.extractall(path=directory)
            tar.close()
        except BaseException as err:
            return {'action': 'error', 'message': "error unpacking PyPI package.  " + str(err)}
        package_file.close()
    initial_directories = len(splitall(directory)) + 1
    for root, dirs, files in os.walk(directory):
        at_top_level = bool(('setup.py' in files or 'pyproject.toml' in files or 'setup.cfg' in files) and 'docassemble' in dirs)
        for a_file in files:
            orig_file = os.path.join(root, a_file)
            # output += "Original file is " + orig_file + "\n"
            thefilename = os.path.join(*splitall(orig_file)[initial_directories:])  # pylint: disable=no-value-for-parameter
            (the_directory, filename) = os.path.split(thefilename)
            if filename.startswith('#') or filename.endswith('~'):
                continue
            dirparts = splitall(the_directory)
            if '.git' in dirparts:
                continue
            levels = re.findall(r'/', the_directory)
            for sec in ('templates', 'static', 'sources', 'questions'):
                if the_directory.endswith('data/' + sec) and filename != 'README.md':
                    data_files[sec].append(filename)
                    target_filename = os.path.join(directory_for(area[area_sec[sec]], current_project), filename)
                    # output += "Copying " + orig_file + "\n"
                    copy_if_different(orig_file, target_filename)
            if filename == 'README.md' and at_top_level:
                with open(orig_file, 'r', encoding='utf-8') as fp:
                    readme_text = fp.read()
            if filename == '.gitignore' and at_top_level:
                with open(orig_file, 'r', encoding='utf-8') as fp:
                    gitignore_text = fp.read()
            if filename == 'setup.py' and at_top_level:
                with open(orig_file, 'r', encoding='utf-8') as fp:
                    setup_py = fp.read()
            if filename == 'pyproject.toml' and at_top_level:
                with open(orig_file, 'r', encoding='utf-8') as fp:
                    pyproject_toml = fp.read()
            elif len(levels) >= 1 and not at_top_level and filename.endswith('.py') and filename != '__init__.py' and 'tests' not in dirparts and 'data' not in dirparts:
                data_files['modules'].append(filename)
                target_filename = os.path.join(directory_for(area['playgroundmodules'], current_project), filename)
                # output += "Copying " + orig_file + "\n"
                if (not os.path.isfile(target_filename)) or filecmp.cmp(orig_file, target_filename) is False:
                    need_to_restart = True
                copy_if_different(orig_file, target_filename)
    # output += "setup.py is " + str(len(setup_py)) + " characters long\n"
    if setup_py:
        setup_py = re.sub(r'.*setup\(', '', setup_py, flags=re.DOTALL)
        for line in setup_py.splitlines():
            m = re.search(r"^ *([a-z_]+) *= *\(?'(.*)'", line)
            if m:
                extracted[m.group(1)] = m.group(2)
            m = re.search(r'^ *([a-z_]+) *= *\(?"(.*)"', line)
            if m:
                extracted[m.group(1)] = m.group(2)
            m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
            if m:
                the_list = []
                for item in re.split(r', *', m.group(2)):
                    inner_item = re.sub(r"'$", '', item)
                    inner_item = re.sub(r"^'", '', inner_item)
                    inner_item = re.sub(r'"+$', '', inner_item)
                    inner_item = re.sub(r'^"+', '', inner_item)
                    the_list.append(inner_item)
                extracted[m.group(1)] = the_list
    if pyproject_toml:
        data = tomli.loads(pyproject_toml)
        if 'project' in data and isinstance(data['project'], dict):
            extracted['description'] = data['project'].get('description', '')
            extracted['name'] = data['project'].get('name', '')
            extracted['version'] = data['project'].get('version', '')
            extracted['license'] = data['project'].get('license', '')
            if 'authors' in data['project'] and isinstance(data['project']['authors'], list) and len(data['project']['authors']) > 0 and isinstance(data['project']['authors'][0], dict):
                extracted['author'] = data['project']['authors'][0].get('name', '')
                extracted['author_email'] = data['project']['authors'][0].get('email', '')
            if 'dependencies' in data['project'] and isinstance(data['project']['dependencies'], list):
                extracted['install_requires'] = data['project']['dependencies']
            if 'urls' in data['project'] and isinstance(data['project']['urls'], dict):
                extracted['url'] = data['project']['urls'].get('Homepage', '')
    if not extracted.get('name', None):
        return {'action': 'error', 'message': "could not find name of PyPI package."}
    info_dict = {'readme': readme_text, 'gitignore': gitignore_text, 'interview_files': data_files['questions'], 'sources_files': data_files['sources'], 'static_files': data_files['static'], 'module_files': data_files['modules'], 'template_files': data_files['templates'], 'dependencies': extracted.get('install_requires', []), 'description': extracted.get('description', ''), 'author_name': extracted.get('author', ''), 'author_email': extracted.get('author_email', ''), 'license': extracted.get('license', ''), 'url': extracted.get('url', ''), 'version': extracted.get('version', ''), 'github_url': github_url, 'github_branch': branch, 'pypi_package_name': pypi_package}
    info_dict['dependencies'] = [x.strip() for x in map(lambda y: re.sub(r'[\>\<\=@].*', '', y), info_dict['dependencies']) if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp')]
    # output += "info_dict is set\n"
    package_name = re.sub(r'^docassemble\.', '', extracted.get('name', expected_name))
    # if not user_can_edit_package(pkgname='docassemble.' + package_name):
    #     index = 1
    #     orig_package_name = package_name
    #     while index < 100 and not user_can_edit_package(pkgname='docassemble.' + package_name):
    #         index += 1
    #         package_name = orig_package_name + str(index)
    with open(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + package_name), 'w', encoding='utf-8') as fp:
        the_yaml = standardyaml.safe_dump(info_dict, default_flow_style=False, default_style='|')
        fp.write(str(the_yaml))
    for sec in area:
        area[sec].finalize()
    for key in r.keys('da:interviewsource:docassemble.playground' + str(playground_user.id) + ':*'):
        r.incr(key.decode())
    return {'action': 'finished', 'need_to_restart': need_to_restart, 'package_name': package_name}


def get_github_username_and_email():
    storage = RedisCredStorage(oauth_app='github')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        raise DAException('GitHub integration expired.')
    http = credentials.authorize(httplib2.Http())
    try:
        resp, content = http.request("https://api.github.com/user", "GET")
    except:
        return None, None, None
    if int(resp['status']) == 200:
        info = json.loads(content.decode('utf-8', 'ignore'))
        github_user_name = info.get('login', None)
        github_author_name = info.get('name', None)
        github_email = info.get('email', None)
    else:
        raise DAError("playground_packages: could not get information about GitHub User")
    if github_email is None:
        resp, content = http.request("https://api.github.com/user/emails", "GET")
        if int(resp['status']) == 200:
            info = json.loads(content.decode('utf-8', 'ignore'))
            for item in info:
                if item.get('email', None) and item.get('visibility', None) != 'private':
                    github_email = item['email']
    if github_user_name is None or github_email is None:
        raise DAError("playground_packages: login not present in user info from GitHub")
    return github_user_name, github_email, github_author_name


@develop_bp.route('/playgroundpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_packages():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    fix_package_folder()
    playground_user = get_playground_user()
    current_project = get_current_project()
    form = PlaygroundPackagesForm(request.form)
    fileform = PlaygroundUploadForm(request.form)
    the_file = secure_filename_spaces_ok(request.args.get('file', ''))
    # no_file_specified = bool(the_file == '')
    scroll = False
    allow_pypi = daconfig.get('pypi', False)
    pypi_username = current_user.pypi_username
    pypi_password = current_user.pypi_password
    pypi_url = daconfig.get('pypi url', 'https://pypi.org/pypi')
    can_publish_to_pypi = bool(allow_pypi is True and pypi_username is not None and pypi_password is not None and pypi_username != '' and pypi_password != '')
    github_auth_info = {}
    if current_app.config['USE_GITHUB']:
        github_auth = r.get('da:using_github:userid:' + str(current_user.id))
        if github_auth is not None:
            github_auth = github_auth.decode()
            if github_auth == '1':
                github_auth_info = {'shared': True, 'orgs': True}
            else:
                github_auth_info = json.loads(github_auth)
            can_publish_to_github = True
        else:
            can_publish_to_github = False
    else:
        can_publish_to_github = None
    if can_publish_to_github and request.method == 'GET':
        storage = RedisCredStorage(oauth_app='github')
        credentials = storage.get()
        if not credentials or credentials.invalid:
            state_string = random_string(16)
            session['github_next'] = json.dumps({'state': state_string, 'path': 'playground_packages', 'arguments': request.args})
            flow = get_github_flow()
            uri = flow.step1_get_authorize_url(state=state_string)
            return redirect(uri)
    show_message = true_or_false(request.args.get('show_message', True))
    github_message = None
    pypi_message = None
    pypi_version = None
    package_list, package_auth = get_package_info()  # pylint: disable=unused-variable
    package_names = sorted([package.package.name for package in package_list])
    for default_package in ('docassemble', 'docassemble.base', 'docassemble.webapp'):
        if default_package in package_names:
            package_names.remove(default_package)
    # if the_file:
    #     scroll = True
    if request.method == 'GET':
        is_new = true_or_false(request.args.get('new', False))
    else:
        is_new = False
    if is_new:
        # scroll = True
        the_file = ''
    area = {}
    file_list = {}
    section_name = {'playground': 'Interview files', 'playgroundpackages': 'Packages', 'playgroundtemplate': 'Template files', 'playgroundstatic': 'Static files', 'playgroundsources': 'Source files', 'playgroundmodules': 'Modules'}
    section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
    section_field = {'playground': form.interview_files, 'playgroundtemplate': form.template_files, 'playgroundstatic': form.static_files, 'playgroundsources': form.sources_files, 'playgroundmodules': form.module_files}
    for sec in ('playground', 'playgroundpackages', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules'):
        area[sec] = SavedFile(playground_user.id, fix=True, section=sec)
        the_directory = directory_for(area[sec], current_project)
        if sec == 'playground' and current_project != 'default' and not os.path.isdir(the_directory):
            current_project = set_current_project('default')
            the_directory = directory_for(area[sec], current_project)
        if os.path.isdir(the_directory):
            file_list[sec] = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        else:
            file_list[sec] = []
    for sec, field in section_field.items():
        the_list = []
        for item in file_list[sec]:
            the_list.append((item, item))
        field.choices = the_list
    the_list = []
    for item in package_names:
        the_list.append((item, item))
    form.dependencies.choices = the_list
    validated = False
    form.github_branch.choices = []
    if form.github_branch.data:
        form.github_branch.choices.append((form.github_branch.data, form.github_branch.data))
    else:
        form.github_branch.choices.append(('', ''))
    if request.method == 'POST' and not (current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin')):
        form.install_also.data = 'n'
        form.install.data = ''
    if request.method == 'POST' and 'uploadfile' not in request.files:
        the_file = form.file_name.data
    the_file = re.sub(r'[^A-Za-z0-9\-\_\.]+', '-', the_file)
    the_file = re.sub(r'^docassemble-', r'', the_file)
    form.files_to_add.choices = [('.gitignore', '.gitignore'), ('LICENSE', 'LICENSE'), ('MANIFEST.in', 'MANIFEST.in'), ('README.md', 'README.md'), ('pyproject.toml', 'pyproject.toml'), ('setup.cfg', 'setup.cfg'), ('setup.py', 'setup.py'), ('docassemble/' + the_file + '/__init__.py', 'docassemble/' + the_file + '/__init__.py')]
    for sec, prefix in (('playground', 'data/questions/'), ('playgroundtemplate', 'data/templates/'), ('playgroundstatic', 'data/static/'), ('playgroundsources', 'data/sources/'), ('playgroundmodules', '')):
        if sec not in ('playground', 'playgroundmodules'):
            form.files_to_add.choices.append(('docassemble/' + the_file + '/' + prefix + 'README.md', 'docassemble/' + the_file + '/' + prefix + 'README.md'))
        for item in file_list[sec]:
            path = 'docassemble/' + the_file + '/' + prefix + item
            form.files_to_add.choices.append((path, path))
    if request.method == 'POST' and 'uploadfile' not in request.files and form.validate():
        validated = True
    the_directory = directory_for(area['playgroundpackages'], current_project)
    files = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    editable_files = []
    for a_file in files:
        editable_files.append({'name': re.sub(r'^docassemble\.', r'', a_file), 'modtime': os.path.getmtime(os.path.join(the_directory, a_file))})
    assign_opacity(editable_files)
    editable_file_listing = [x['name'] for x in editable_files]
    if request.method == 'GET' and not the_file and not is_new:
        current_file = get_current_file(current_project, 'packages')
        if not current_file.startswith('docassemble.'):
            current_file = 'docassemble.' + current_file
            set_current_file(current_project, 'packages', current_file)
        if re.sub(r'^docassemble\.', r'', current_file) in editable_file_listing:
            the_file = re.sub(r'^docassemble\.', r'', current_file)
        else:
            delete_current_file(current_project, 'packages')
            if len(editable_files) > 0:
                the_file = sorted(editable_files, key=lambda x: x['modtime'])[-1]['name']
            else:
                the_file = ''
    # if the_file != '' and not user_can_edit_package(pkgname='docassemble.' + the_file):
    #     flash(word('Sorry, that package name,') + ' ' + the_file + word(', is already in use by someone else'), 'error')
    #     validated = False
    if request.method == 'GET' and the_file in editable_file_listing:
        set_current_file(current_project, 'packages', 'docassemble.' + the_file)
    if the_file == '' and len(file_list['playgroundpackages']) and not is_new:
        the_file = file_list['playgroundpackages'][0]
        the_file = re.sub(r'^docassemble\.', r'', the_file)
    old_info = {}
    branch_info = []
    github_http = None
    github_ssh = None
    github_use_ssh = False
    github_user_name = None
    github_email = None
    github_author_name = None
    github_url_from_file = None
    pypi_package_from_file = None
    expected_name = 'unknown'
    if request.method == 'GET' and the_file != '':
        if the_file != '' and os.path.isfile(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + the_file)):
            filename = os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + the_file)
            with open(filename, 'r', encoding='utf-8') as fp:
                content = fp.read()
                old_info = standardyaml.load(content, Loader=standardyaml.FullLoader)
                if isinstance(old_info, dict):
                    if 'license' in old_info and isinstance(old_info['license'], str) and 'MIT License' in old_info['license']:
                        old_info['license'] = 'MIT'
                    github_url_from_file = old_info.get('github_url', None)
                    pypi_package_from_file = old_info.get('pypi_package_name', None)
                    for field in ('license', 'description', 'author_name', 'author_email', 'version', 'url', 'readme'):
                        if field in old_info:
                            form[field].data = old_info[field]
                        else:
                            form[field].data = ''
                    if 'dependencies' in old_info and isinstance(old_info['dependencies'], list) and len(old_info['dependencies']):
                        old_info['dependencies'] = list(map(lambda y: re.sub(r'[\>\<\=].*', '', y), old_info['dependencies']))
                        for item in ('docassemble', 'docassemble.base', 'docassemble.webapp'):
                            if item in old_info['dependencies']:
                                del old_info['dependencies'][item]
                    for field in ('dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files'):
                        if field in old_info and isinstance(old_info[field], list) and len(old_info[field]):
                            form[field].data = old_info[field]
                else:
                    raise DAException("YAML yielded " + repr(old_info) + " from " + repr(content))
        else:
            filename = None
    if the_file != '' and can_publish_to_github and not is_new:
        github_package_name = 'docassemble-' + the_file
        try:
            storage = RedisCredStorage(oauth_app='github')
            credentials = storage.get()
            if not credentials or credentials.invalid:
                if form.github.data:
                    state_string = random_string(16)
                    session['github_next'] = json.dumps({'state': state_string, 'path': 'playground_packages', 'arguments': request.args})
                    flow = get_github_flow()
                    uri = flow.step1_get_authorize_url(state=state_string)
                    return redirect(uri)
                raise DAException('GitHub integration expired.')
            http = credentials.authorize(httplib2.Http())
            resp, content = http.request("https://api.github.com/user", "GET")
            if int(resp['status']) == 200:
                info = json.loads(content.decode('utf-8', 'ignore'))
                github_user_name = info.get('login', None)
                github_author_name = info.get('name', None)
                github_email = info.get('email', None)
            else:
                raise DAError("playground_packages: could not get information about GitHub User")
            if github_email is None:
                resp, content = http.request("https://api.github.com/user/emails", "GET")
                if int(resp['status']) == 200:
                    info = json.loads(content.decode('utf-8', 'ignore'))
                    for item in info:
                        if item.get('email', None) and item.get('visibility', None) != 'private':
                            github_email = item['email']
            if github_user_name is None or github_email is None:
                raise DAError("playground_packages: login not present in user info from GitHub")
            found = False
            found_strong = False
            resp, content = http.request("https://api.github.com/repos/" + str(github_user_name) + "/" + github_package_name, "GET")
            if int(resp['status']) == 200:
                repo_info = json.loads(content.decode('utf-8', 'ignore'))
                github_http = repo_info['html_url']
                github_ssh = repo_info['ssh_url']
                if repo_info['private']:
                    github_use_ssh = True
                github_message = word('This package is') + ' <a target="_blank" href="' + repo_info.get('html_url', 'about:blank') + '">' + word("published on GitHub") + '</a>.'
                if github_author_name:
                    github_message += "  " + word("The author is") + " " + github_author_name + "."
                branch_info = get_branch_info(http, repo_info['full_name'])
                found = True
                if github_url_from_file is None or github_url_from_file in [github_ssh, github_http]:
                    found_strong = True
            if found_strong is False and github_auth_info.get('shared'):
                repositories = get_user_repositories(http)
                for repo_info in repositories:
                    if repo_info['name'] != github_package_name or (github_http is not None and github_http == repo_info['html_url']) or (github_ssh is not None and github_ssh == repo_info['ssh_url']):
                        continue
                    if found and github_url_from_file is not None and github_url_from_file not in [repo_info['html_url'], repo_info['ssh_url']]:
                        break
                    github_http = repo_info['html_url']
                    github_ssh = repo_info['ssh_url']
                    if repo_info['private']:
                        github_use_ssh = True
                    github_message = word('This package is') + ' <a target="_blank" href="' + repo_info.get('html_url', 'about:blank') + '">' + word("published on GitHub") + '</a>.'
                    branch_info = get_branch_info(http, repo_info['full_name'])
                    found = True
                    if github_url_from_file is None or github_url_from_file in [github_ssh, github_http]:
                        found_strong = True
                    break
            if found_strong is False and github_auth_info['orgs']:
                orgs_info = get_orgs_info(http)
                for org_info in orgs_info:
                    resp, content = http.request("https://api.github.com/repos/" + str(org_info['login']) + "/" + github_package_name, "GET")
                    if int(resp['status']) == 200:
                        repo_info = json.loads(content.decode('utf-8', 'ignore'))
                        if found and github_url_from_file is not None and github_url_from_file not in [repo_info['html_url'], repo_info['ssh_url']]:
                            break
                        github_http = repo_info['html_url']
                        github_ssh = repo_info['ssh_url']
                        if repo_info['private']:
                            github_use_ssh = True
                        github_message = word('This package is') + ' <a target="_blank" href="' + repo_info.get('html_url', 'about:blank') + '">' + word("published on GitHub") + '</a>.'
                        branch_info = get_branch_info(http, repo_info['full_name'])
                        found = True
                        if github_url_from_file is None or github_url_from_file in [github_ssh, github_http]:
                            found_strong = True
                        break
            if found is False:
                github_message = word('This package is not yet published on your GitHub account.')
        except BaseException as e:
            logmessage('playground_packages: GitHub error.  ' + str(e))
            github_message = word('Unable to determine if the package is published on your GitHub account.')
    if request.method == 'POST' and 'uploadfile' in request.files:
        the_files = request.files.getlist('uploadfile')
        need_to_restart = False
        if current_user.timezone:
            the_timezone = zoneinfo.ZoneInfo(current_user.timezone)
        else:
            the_timezone = zoneinfo.ZoneInfo(get_default_timezone())
        if the_files:
            for up_file in the_files:
                # zip_filename = werkzeug.utils.secure_filename(up_file.filename)
                zippath = tempfile.NamedTemporaryFile(mode="wb", suffix=".zip", prefix="datemp", delete=False)
                up_file.save(zippath.name)
                area_sec = {'templates': 'playgroundtemplate', 'static': 'playgroundstatic', 'sources': 'playgroundsources', 'questions': 'playground'}
                zippath.close()
                with zipfile.ZipFile(zippath.name, mode='r') as zf:
                    readme_text = ''
                    gitignore_text = ''
                    setup_py = ''
                    pyproject_toml = ''
                    extracted = {}
                    data_files = {'templates': [], 'static': [], 'sources': [], 'interviews': [], 'modules': [], 'questions': []}
                    has_docassemble_dir = set()
                    has_setup_file = set()
                    for zinfo in zf.infolist():
                        if zinfo.is_dir():
                            if zinfo.filename.endswith('/docassemble/'):
                                has_docassemble_dir.add(re.sub(r'/docassemble/$', '', zinfo.filename))
                            if zinfo.filename == 'docassemble/':
                                has_docassemble_dir.add('')
                        elif zinfo.filename.endswith('/setup.py') or zinfo.filename.endswith('/pyproject.toml') or zinfo.filename.endswith('/setup.cfg'):
                            (directory, filename) = os.path.split(zinfo.filename)
                            has_setup_file.add(directory)
                        elif zinfo.filename in ('setup.py', 'pyproject.toml', 'setup.cfg'):
                            has_setup_file.add('')
                    root_dir = None
                    for directory in has_docassemble_dir.union(has_setup_file):
                        if root_dir is None or len(directory) < len(root_dir):
                            root_dir = directory
                    if root_dir is None:
                        flash(word("The zip file did not contain a docassemble add-on package."), 'error')
                        return redirect(url_for('develop.playground_packages', project=current_project, file=the_file))
                    for zinfo in zf.infolist():
                        # logmessage("Found a " + zinfo.filename)
                        if zinfo.filename.endswith('/'):
                            continue
                        (directory, filename) = os.path.split(zinfo.filename)
                        if filename.startswith('#') or filename.endswith('~'):
                            continue
                        dirparts = splitall(directory)
                        if '.git' in dirparts:
                            continue
                        levels = re.findall(r'/', directory)
                        time_tuple = zinfo.date_time
                        the_time = time.mktime(datetime.datetime(*time_tuple).timetuple())
                        for sec in ('templates', 'static', 'sources', 'questions'):
                            if directory.endswith('data/' + sec) and filename != 'README.md':
                                data_files[sec].append(filename)
                                target_filename = os.path.join(directory_for(area[area_sec[sec]], current_project), filename)
                                with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                    shutil.copyfileobj(source_fp, target_fp)
                                os.utime(target_filename, (the_time, the_time))
                        if filename == 'README.md' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                readme_text = the_file_obj.read()
                        if filename == '.gitignore' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                gitignore_text = the_file_obj.read()
                        if filename == 'setup.py' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                setup_py = the_file_obj.read()
                        if filename == 'pyproject.toml' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                pyproject_toml = the_file_obj.read()
                        elif len(levels) >= 1 and directory != root_dir and filename.endswith('.py') and filename != '__init__.py' and 'tests' not in dirparts and 'data' not in dirparts:
                            need_to_restart = True
                            data_files['modules'].append(filename)
                            target_filename = os.path.join(directory_for(area['playgroundmodules'], current_project), filename)
                            with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                shutil.copyfileobj(source_fp, target_fp)
                                os.utime(target_filename, (the_time, the_time))
                    if setup_py:
                        setup_py = re.sub(r'.*setup\(', '', setup_py, flags=re.DOTALL)
                        for line in setup_py.splitlines():
                            m = re.search(r"^ *([a-z_]+) *= *\(?'(.*)'", line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\(?"(.*)"', line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
                            if m:
                                the_list = []
                                for item in re.split(r', *', m.group(2)):
                                    inner_item = re.sub(r"'$", '', item)
                                    inner_item = re.sub(r"^'", '', inner_item)
                                    inner_item = re.sub(r'"+$', '', inner_item)
                                    inner_item = re.sub(r'^"+', '', inner_item)
                                    the_list.append(inner_item)
                                extracted[m.group(1)] = the_list
                    if pyproject_toml:
                        data = tomli.loads(pyproject_toml)
                        if 'project' in data and isinstance(data['project'], dict):
                            extracted['description'] = data['project'].get('description', '')
                            extracted['name'] = data['project'].get('name', '')
                            extracted['version'] = data['project'].get('version', '')
                            extracted['license'] = data['project'].get('license', '')
                            if 'authors' in data['project'] and isinstance(data['project']['authors'], list) and len(data['project']['authors']) > 0 and isinstance(data['project']['authors'][0], dict):
                                extracted['author'] = data['project']['authors'][0].get('name', '')
                                extracted['author_email'] = data['project']['authors'][0].get('email', '')
                            if 'dependencies' in data['project'] and isinstance(data['project']['dependencies'], list):
                                extracted['install_requires'] = data['project']['dependencies']
                            if 'urls' in data['project'] and isinstance(data['project']['urls'], dict):
                                extracted['url'] = data['project']['urls'].get('Homepage', '')
                    info_dict = {'readme': readme_text, 'gitignore': gitignore_text, 'interview_files': data_files['questions'], 'sources_files': data_files['sources'], 'static_files': data_files['static'], 'module_files': data_files['modules'], 'template_files': data_files['templates'], 'dependencies': list(map(lambda y: re.sub(r'[\>\<\=].*', '', y), extracted.get('install_requires', []))), 'description': extracted.get('description', ''), 'author_name': extracted.get('author', ''), 'author_email': extracted.get('author_email', ''), 'license': extracted.get('license', ''), 'url': extracted.get('url', ''), 'version': extracted.get('version', '')}

                    info_dict['dependencies'] = [x.strip() for x in map(lambda y: re.sub(r'[\>\<\=@].*', '', y), info_dict['dependencies']) if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp')]
                    package_name = re.sub(r'^docassemble\.', '', extracted.get('name', expected_name))
                    with open(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + package_name), 'w', encoding='utf-8') as fp:
                        the_yaml = standardyaml.safe_dump(info_dict, default_flow_style=False, default_style='|')
                        fp.write(str(the_yaml))
                    for key in r.keys('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':*'):
                        r.incr(key.decode())
                    for the_area in area.values():
                        the_area.finalize()
                    the_file = package_name
                zippath.close()
        if show_message:
            flash(word("The package was unpacked into the Playground."), 'success')
        if need_to_restart:
            return redirect(url_for('main.restart_page', next=url_for('develop.playground_packages', project=current_project, file=the_file)))
        return redirect(url_for('develop.playground_packages', project=current_project, file=the_file))
    if request.method == 'GET' and 'pull' in request.args and int(request.args['pull']) == 1 and ('github_url' in request.args or 'pypi' in request.args):
        if can_publish_to_github and (github_user_name is None or github_email is None):
            (github_user_name, github_email, github_author_name) = get_github_username_and_email()
        github_url = request.args.get('github_url', None)
        pypi_package = request.args.get('pypi', None)
        branch = request.args.get('branch', None)
        do_pypi_also = true_or_false(request.args.get('pypi_also', False))
        if current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin'):
            do_install_also = true_or_false(request.args.get('install_also', False))
        else:
            do_install_also = False
        result = do_playground_pull(area, current_project, github_url=github_url, branch=branch, pypi_package=pypi_package, can_publish_to_github=can_publish_to_github, github_email=github_email, pull_only=(do_pypi_also or do_install_also))
        if result['action'] == 'error':
            raise DAError("playground_packages: " + result['message'])
        if result['action'] == 'fail':
            flash(result['message'], 'error')
            return redirect(url_for('develop.playground_packages', project=current_project))
        if result['action'] == 'pull_only':
            the_args = {'package': the_file, 'project': current_project}
            if do_pypi_also:
                the_args['pypi'] = '1'
            if do_install_also:
                the_args['install'] = '1'
            area['playgroundpackages'].finalize()
            return redirect(url_for('develop.create_playground_package', **the_args))
        if result['action'] == 'finished':
            the_file = result['package_name']
            if show_message:
                flash(word("The package was unpacked into the Playground."), 'success')
            # shutil.rmtree(directory)
            if result['need_to_restart']:
                return redirect(url_for('main.restart_page', next=url_for('develop.playground_packages', file=the_file, project=current_project)))
            return redirect(url_for('develop.playground_packages', project=current_project, file=the_file))
    if request.method == 'POST' and validated and form.delete.data and the_file != '' and the_file == form.file_name.data and os.path.isfile(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + the_file)):
        os.remove(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + the_file))
        dotfile = os.path.join(directory_for(area['playgroundpackages'], current_project), '.docassemble-' + the_file)
        if os.path.exists(dotfile):
            os.remove(dotfile)
        area['playgroundpackages'].finalize()
        flash(word("Deleted package"), "success")
        return redirect(url_for('develop.playground_packages', project=current_project))
    if not is_new:
        pkgname = 'docassemble.' + the_file
        if can_publish_to_pypi:
            pypi_info = pypi_status(pkgname)
            if pypi_info['error']:
                pypi_message = word("Unable to determine if the package is published on PyPI.")
            else:
                if pypi_info['exists'] and 'info' in pypi_info['info']:
                    pypi_version = pypi_info['info']['info'].get('version', None)
                    pypi_message = word('This package is') + ' <a target="_blank" href="' + pypi_url + '/' + pkgname + '/' + pypi_version + '">' + word("published on PyPI") + '</a>.'
                    pypi_author = pypi_info['info']['info'].get('author', None)
                    if pypi_author:
                        pypi_message += "  " + word("The author is") + " " + pypi_author + "."
                    if pypi_version != form['version'].data:
                        pypi_message += "  " + word("The version on PyPI is") + " " + str(pypi_version) + ".  " + word("Your version is") + " " + str(form['version'].data) + "."
                else:
                    pypi_message = word('This package is not yet published on PyPI.')
    if request.method == 'POST' and validated:
        new_info = {}
        for field in ('license', 'description', 'author_name', 'author_email', 'version', 'url', 'readme', 'dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files'):
            new_info[field] = form[field].data
        # logmessage("found " + str(new_info))
        if form.submit.data or form.download.data or form.install.data or form.pypi.data or form.github.data:
            if the_file != '':
                area['playgroundpackages'].finalize()
                if form.original_file_name.data and form.original_file_name.data != the_file:
                    old_filename = os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + form.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                if can_publish_to_pypi and form.pypi.data and pypi_version is not None:
                    if not new_info['version']:
                        new_info['version'] = pypi_version
                    while 'releases' in pypi_info['info'] and new_info['version'] in pypi_info['info']['releases'].keys():
                        versions = new_info['version'].split(".")
                        versions[-1] = str(int(versions[-1]) + 1)
                        new_info['version'] = ".".join(versions)
                filename = os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + the_file)
                if os.path.isfile(filename):
                    with open(filename, 'r', encoding='utf-8') as fp:
                        content = fp.read()
                        old_info = standardyaml.load(content, Loader=standardyaml.FullLoader)
                    for name in ('github_url', 'github_branch', 'pypi_package_name', 'gitignore'):
                        if old_info.get(name, None):
                            new_info[name] = old_info[name]
                with open(filename, 'w', encoding='utf-8') as fp:
                    the_yaml = standardyaml.safe_dump(new_info, default_flow_style=False, default_style='|')
                    fp.write(str(the_yaml))
                area['playgroundpackages'].finalize()
                if form.download.data:
                    return redirect(url_for('develop.create_playground_package', package=the_file, project=current_project))
                if form.install.data:
                    return redirect(url_for('develop.create_playground_package', package=the_file, project=current_project, install='1'))
                if form.pypi.data:
                    if form.install_also.data:
                        return redirect(url_for('develop.create_playground_package', package=the_file, project=current_project, pypi='1', install='1'))
                    return redirect(url_for('develop.create_playground_package', package=the_file, project=current_project, pypi='1'))
                if form.github.data:
                    session['github_to_add'] = form.files_to_add.data
                    the_branch = form.github_branch.data
                    if the_branch == "<new>":
                        the_branch = re.sub(r'[^A-Za-z0-9\_\-]', r'', str(form.github_branch_new.data))
                        return redirect(url_for('develop.create_playground_package', project=current_project, package=the_file, github='1', commit_message=form.commit_message.data, new_branch=str(the_branch), pypi_also=('1' if form.pypi_also.data else '0'), install_also=('1' if form.install_also.data else '0')))
                    return redirect(url_for('develop.create_playground_package', project=current_project, package=the_file, github='1', commit_message=form.commit_message.data, branch=str(the_branch), pypi_also=('1' if form.pypi_also.data else '0'), install_also=('1' if form.install_also.data else '0')))
                the_time = formatted_current_time()
                if show_message:
                    flash(word('The package information was saved.'), 'success')
    form.original_file_name.data = the_file
    form.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + the_file)):
        filename = os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + the_file)
    else:
        filename = None
    header = word("Packages")
    upload_header = None
    edit_header = None
    description = Markup("""Describe your package and choose the files from your Playground that will go into it.""")
    after_text = None
    initial_values = playground_values(current_project, the_file)
    initial_values.update({
        "daPage": 'package',
        "daScroll": bool(scroll),
        "isNew": is_new,
        "existingFiles": files,
        "existingPypiVersion": pypi_version,
        "currentFile": the_file,
        "daContent": form.readme.data,
    })
    initial_values['daTranslations'].update({
            "needToIncrement": word("You need to increment the version before publishing to PyPI."),
            "commit": word("Commit"),
            "publish": word("Publish"),
            "github": word("GitHub"),
            "pypi": word("PyPI"),
            "unsavedChangesWarning": word("There are unsaved changes.  Are you sure you wish to leave this page?"),
            "sureDeletePackage": word("Are you sure that you want to delete this package?"),
            "packageExistsWarning": word("Warning: a package definition by that name already exists.  If you save, you will overwrite it."),
        })
    any_files = len(editable_files) > 0
    back_button = Markup('<span class="navbar-brand navbar-nav dabackicon me-3"><a href="' + url_for('develop.playground_page', project=current_project) + '" class="dabackbuttoncolor nav-link" title=' + json.dumps(word("Go back to the main Playground page")) + '><i class="fa-solid fa-chevron-left"></i><span class="daback">' + word('Back') + '</span></a></span>')
    if can_publish_to_pypi:
        if pypi_message is not None:
            pypi_message = Markup(pypi_message)
    else:
        pypi_message = None
    extra_js = f"""
    <script{DEFER} src="{url_for('static', filename="app/playgroundbundle.min.js", v=da_version)}"></script>
    {redis_script(initial_values)}
"""
    if github_use_ssh:
        the_github_url = github_ssh
    else:
        the_github_url = github_http
    if the_github_url is None and github_url_from_file is not None:
        the_github_url = github_url_from_file
    if the_github_url is None:
        the_pypi_package_name = pypi_package_from_file
    else:
        the_pypi_package_name = None
    if github_message is not None and github_url_from_file is not None and github_url_from_file != github_http and github_url_from_file != github_ssh:
        github_message += '  ' + word("This package was originally pulled from") + ' <a target="_blank" href="' + github_as_http(github_url_from_file) + '">' + word('a GitHub repository') + '</a>.'
    if github_message is not None and old_info.get('github_branch', None) and (github_http or github_url_from_file):
        html_url = github_http or github_url_from_file
        commit_code = None
        current_commit_file = os.path.join(directory_for(area['playgroundpackages'], current_project), '.' + github_package_name)
        if os.path.isfile(current_commit_file):
            with open(current_commit_file, 'r', encoding='utf-8') as fp:
                commit_code = fp.read().strip()
            if current_user.timezone:
                the_timezone = zoneinfo.ZoneInfo(current_user.timezone)
            else:
                the_timezone = zoneinfo.ZoneInfo(get_default_timezone())
            commit_code_date = datetime.datetime.fromtimestamp(os.path.getmtime(current_commit_file), datetime.timezone.utc).astimezone(the_timezone).strftime("%Y-%m-%d %H:%M:%S %Z")
        else:
            commit_code_date = ''
        if commit_code:
            github_message += '  ' + word('The current branch is %s and the current commit is %s.') % ('<a target="_blank" href="' + html_url + '/tree/' + old_info['github_branch'] + '">' + old_info['github_branch'] + '</a>', '<a target="_blank" href="' + html_url + '/commit/' + commit_code + '"><code>' + commit_code[0:7] + '</code></a>') + '  ' + word('The commit was saved locally at %s.') % commit_code_date
        else:
            github_message += '  ' + word('The current branch is %s.') % ('<a target="_blank" href="' + html_url + '/tree/' + old_info['github_branch'] + '">' + old_info['github_branch'] + '</a>',)
    if github_message is not None:
        github_message = Markup(github_message)
    branch = old_info.get('github_branch', None)
    if branch is not None:
        branch = branch.strip()
    branch_choices = []
    if len(branch_info) > 0:
        branch_choices.append(("<new>", word("(New branch)")))
    branch_names = set()
    for br in branch_info:
        branch_names.add(br['name'])
        branch_choices.append((br['name'], br['name']))
    if branch and branch in branch_names:
        form.github_branch.data = branch
        default_branch = branch
    elif 'master' in branch_names:
        form.github_branch.data = 'master'
        default_branch = 'master'
    elif 'main' in branch_names:
        form.github_branch.data = 'main'
        default_branch = 'main'
    else:
        default_branch = GITHUB_BRANCH
    form.github_branch.choices = branch_choices
    if form.author_name.data in ('', None) and current_user.first_name and current_user.last_name:
        form.author_name.data = current_user.first_name + " " + current_user.last_name
    if form.author_email.data in ('', None) and current_user.email:
        form.author_email.data = current_user.email
    if current_user.id != playground_user.id:
        header += " / " + playground_user.email
    if current_project != 'default':
        header += " / " + current_project
    response = make_response(render_template('develop/playgroundpackages.html', current_project=current_project, branch=default_branch, version_warning=None, bodyclass='daadminbody', can_publish_to_pypi=can_publish_to_pypi, pypi_message=pypi_message, can_publish_to_github=can_publish_to_github, github_message=github_message, github_url=the_github_url, pypi_package_name=the_pypi_package_name, back_button=back_button, tab_title=header, page_title=header, extra_css=Markup('\n    <link href="' + url_for('static', filename='app/playgroundbundle.css', v=da_version) + '" rel="stylesheet">'), extra_js=Markup(extra_js), header=header, upload_header=upload_header, edit_header=edit_header, description=description, form=form, fileform=fileform, files=files, file_list=file_list, userid=playground_user.id, editable_files=sorted(editable_files, key=lambda y: y['name'].lower()), current_file=the_file, after_text=after_text, section_name=section_name, section_sec=section_sec, section_field=section_field, package_names=sorted(package_names, key=lambda y: y.lower()), any_files=any_files), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def github_as_http(url):
    if url.startswith('http'):
        return url
    return re.sub(r'^[^@]+@([^:]+):(.*)\.git$', r'https://\1/\2', url)


def copy_if_different(source, destination):
    if (not os.path.isfile(destination)) or filecmp.cmp(source, destination) is False:
        shutil.copyfile(source, destination)


@develop_bp.route('/playground_redirect_poll', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_redirect_poll():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    playground_user = get_playground_user()
    key = 'da:runplayground:' + str(playground_user.id)
    the_url = r.get(key)
    # logmessage("playground_redirect: key " + str(key) + " is " + str(the_url))
    if the_url is not None:
        the_url = the_url.decode()
        r.delete(key)
        return jsonify({'success': True, 'url': the_url})
    return jsonify({'success': False, 'url': the_url})


@develop_bp.route('/playground_redirect', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_redirect():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    playground_user = get_playground_user()
    key = 'da:runplayground:' + str(playground_user.id)
    counter = 0
    while counter < 15:
        the_url = r.get(key)
        # logmessage("playground_redirect: key " + str(key) + " is " + str(the_url))
        if the_url is not None:
            the_url = the_url.decode()
            r.delete(key)
            return redirect(the_url)
        time.sleep(1)
        counter += 1
    return ('File not found', 404)


def upload_js():
    return """
      $("#uploadlink").on('click', function(event){
        $("#uploadlabel").click();
        event.preventDefault();
        return false;
      });
      $("#uploadlabel").on('click', function(event){
        event.stopPropagation();
        event.preventDefault();
        $("#uploadfile").click();
        return false;
      });
      $("#uploadfile").on('click', function(event){
        event.stopPropagation();
      });
      $("#uploadfile").on('change', function(event){
        $("#fileform").submit();
      });"""


def variables_js(form=None, office_mode=False, current_project=None):
    if current_project is None:
        current_project = 'default'
    playground_user = get_playground_user()
    output = """
function activatePopovers(){
  var daPopoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  var daPopoverList = daPopoverTriggerList.map(function (daPopoverTriggerEl) {
    return new bootstrap.Popover(daPopoverTriggerEl, {trigger: "click", html: true});
  });
}

function activateVariables(){
  $(".daparenthetical").on("click", function(event){
    var reference = $(this).data("ref");
    //console.log("reference is " + reference);
    var target = $('[data-name="' + reference + '"]').first();
    if (target.length > 0){
      //console.log("target is " + target);
      //console.log("scrolltop is now " + $('#daplaygroundcard').scrollTop());
      //console.log("Scrolling to " + target.parent().parent().position().top);
      $('#daplaygroundcard').animate({
          scrollTop: target.parent().parent().position().top
      }, 1000);
    }
    event.preventDefault();
  });

  $(".dashowmethods").on("click", function(event){
    var target_id = $(this).data("showhide");
    $("#" + target_id).slideToggle();
  });

  $(".dashowattributes").each(function(){
    var basename = $(this).data('name');
    if (attrs_showing.hasOwnProperty(basename)){
      if (attrs_showing[basename]){
        $('tr[data-parent="' + basename + '"]').show();
      }
    }
    else{
      attrs_showing[basename] = false;
    }
  });

  $(".dashowattributes").on("click", function(event){
    var basename = $(this).data('name');
    attrs_showing[basename] = !attrs_showing[basename];
    $('tr[data-parent="' + basename + '"]').each(function(){
      $(this).toggle();
    });
  });"""
    if office_mode:
        return output + "\n}"
    if form is None:
        form = 'form'
    output += """
  $(".playground-variable").on("click", function(event){
    daCm.ev.dispatch(daCm.ev.state.replaceSelection($(this).data("insert"), "around"));
    daCm.ev.focus();
  });

  $(".dasearchicon").on("click", function(event){
    var query = $(this).data('name');
    if (query == null || query.length == 0){
      daCm.ev.dispatch({selection: {anchor: daCm.ev.state.selection.main.head}})
      return;
    }
    daStartNewSearch(daCm.ev, query);
    event.preventDefault();
    return false;
  });
}

var interviewBaseUrl = '""" + url_for('interview.index', reset='1', cache='0', i='docassemble.playground' + str(playground_user.id) + ':.yml') + """';
var shareBaseUrl = '""" + url_for('interview.index', i='docassemble.playground' + str(playground_user.id) + ':.yml', _external=True) + """';

function updateRunLink(){
  if (currentProject == 'default'){
    $("#daRunButton").attr("href", interviewBaseUrl.replace(':.yml', ':' + $("#daVariables").val()));
    $("a.da-example-share").attr("href", shareBaseUrl.replace(':.yml', ':' + $("#daVariables").val()));
  }
  else{
    $("#daRunButton").attr("href", interviewBaseUrl.replace(':.yml', currentProject + ':' + $("#daVariables").val()));
    $("a.da-example-share").attr("href", shareBaseUrl.replace(':.yml', currentProject + ':' + $("#daVariables").val()));
  }
}

function fetchVars(changed){
  $("#playground_content").val(daCm.ev.state.doc.toString());
  updateRunLink();
  $.ajax({
    type: "POST",
    url: """ + '"' + url_for('develop.playground_variables') + '"' + """ + '?project=' + currentProject,
    data: 'csrf_token=' + $("#""" + form + """ input[name='csrf_token']").val() + '&variablefile=' + $("#daVariables").val() + '&ajax=1&changed=' + (changed ? 1 : 0),
    success: function(data){
      if (data.action && data.action == 'reload'){
        location.reload(true);
      }
      if (data.vocab_list != null){
        vocab = data.vocab_list;
      }
      if (data.current_project != null){
        currentProject = data.current_project;
      }
      if (data.ac_list != null){
        daAutoComp.length = 0;
        let n = data.ac_list.length;
        for(let i = 0; i < n; i++){
          daAutoComp.push(data.ac_list[i]);
        }
      }
      if (data.variables_html != null){
        $("#daplaygroundtable").html(data.variables_html);
        var daPopoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var daPopoverList = daPopoverTriggerList.map(function (daPopoverTriggerEl) {
          return new bootstrap.Popover(daPopoverTriggerEl, {trigger: "focus", html: true});
        });
        activateVariables();
      }
    },
    dataType: 'json'
  });
  $("#daVariables").blur();
}

function variablesReady(){
  $("#daVariables").change(function(event){
    fetchVars(true);
  });
}

function daFetchVariableReportCallback(data){
  var translations = """ + json.dumps({'in mako': word("in mako"), 'mentioned in': word("mentioned in"), 'defined by': word("defined by")}) + """;
  var modal = $("#daVariablesReport .modal-body");
  if (modal.length == 0){
    console.log("No modal body on page");
    return;
  }
  if (!data.success){
    $(modal).html('<p>""" + word("Failed to load report") + """</p>');
    return;
  }
  var yaml_file = data.yaml_file;
  modal.empty();
  var accordion = $('<div>');
  accordion.addClass("accordion");
  accordion.attr("id", "varsreport");
  var n = data.items.length;
  for (var i = 0; i < n; ++i){
    var item = data.items[i];
    if (item.questions.length){
      var accordionItem = $('<div>');
      accordionItem.addClass("accordion-item");
      var accordionItemHeader = $('<h2>');
      accordionItemHeader.addClass("accordion-header");
      accordionItemHeader.attr("id", "accordionItemheader" + i);
      accordionItemHeader.html('<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse' + i + '" aria-expanded="false" aria-controls="collapse' + i + '">' + item.name + '</button>');
      accordionItem.append(accordionItemHeader);
      var collapse = $("<div>");
      collapse.attr("id", "collapse" + i);
      collapse.attr("aria-labelledby", "accordionItemheader" + i);
      collapse.data("bs-parent", "#varsreport");
      collapse.addClass("accordion-collapse");
      collapse.addClass("collapse");
      var accordionItemBody = $("<div>");
      accordionItemBody.addClass("accordion-body");
      var m = item.questions.length;
      for (var j = 0; j < m; j++){
        var h5 = $("<h5>");
        h5.html(item.questions[j].usage.map(x => translations[x]).join(','));
        var pre = $("<pre>");
        pre.html(item.questions[j].source_code);
        accordionItemBody.append(h5);
        accordionItemBody.append(pre);
        if (item.questions[j].yaml_file != yaml_file){
          var p = $("<p>");
          p.html(""" + json.dumps(word("from")) + """ + ' ' + item.questions[j].yaml_file);
          accordionItemBody.append(p);
        }
      }
      collapse.append(accordionItemBody);
      accordionItem.append(collapse);
      accordion.append(accordionItem);
    }
  }
  modal.append(accordion);
}

function daFetchVariableReport(theFile=currentFile){
  url = """ + json.dumps(url_for('develop.variables_report', project=current_project)) + """ + "&file=" + theFile;
  $("#daVariablesReport .modal-body").html('<p>""" + word("Loading . . .") + """</p>');
  $.ajax({
    type: "GET",
    url: url,
    success: daFetchVariableReportCallback,
    xhrFields: {
      withCredentials: true
    },
    error: function(xhr, status, error){
      $("#daVariablesReport .modal-body").html('<p>""" + word("Failed to load report") + """</p>');
    }
  });
}

$( document ).ready(function() {
  $(document).on('keydown', function(e){
    if (e.which == 13){
      var tag = $( document.activeElement ).prop("tagName");
      if (tag == "INPUT"){
        e.preventDefault();
        e.stopPropagation();
        daCm.ev.focus();
        return false;
      }
    }
  });
});
"""
    return output


@develop_bp.route("/varsreport", methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def variables_report():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    playground_user = get_playground_user()
    playground = SavedFile(playground_user.id, fix=True, section='playground')
    the_file = request.args.get('file', None)
    if the_file is not None:
        the_file = secure_filename_spaces_ok(the_file)
    current_project = werkzeug.utils.secure_filename(request.args.get('project', 'default'))
    the_directory = directory_for(playground, current_project)
    files = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    if len(files) == 0:
        return jsonify(success=False, reason=1)
    if the_file is None or the_file not in files:
        return jsonify(success=False, reason=2)
    interview_source = interview_source_from_string('docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + the_file, raise_jinja_errors=False)
    interview_source.set_testing(True)
    interview = Interview(source=interview_source)
    ensure_ml_file_exists(interview, the_file, current_project)
    yaml_file = 'docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + the_file
    the_current_info = current_info(yaml=yaml_file, req=request, action=None, device_id=request.cookies.get('ds', None))
    this_thread.current_info = the_current_info
    interview_status = InterviewStatus(current_info=the_current_info)
    variables_html, vocab_list, vocab_dict, ac_list = get_vars_in_use(interview, interview_status, debug_mode=False, current_project=current_project)  # pylint: disable=unused-variable
    results = []
    result_dict = {}
    for name in vocab_list:
        if name in ('x', 'row_item', 'i', 'j', 'k', 'l', 'm', 'n') or name.startswith('x.') or name.startswith('x[') or name.startswith('row_item.'):
            continue
        result = {'name': name, 'questions': []}
        results.append(result)
        result_dict[name] = result
    for question in interview.questions_list:
        names_seen = {}
        for the_type, the_set in (('in mako', question.mako_names), ('mentioned in', question.names_used), ('defined by', question.fields_used)):
            for name in the_set:
                the_name = name
                subnames = [the_name]
                while True:
                    if re.search(r'\[[^\]]\]$', the_name):
                        the_name = re.sub(r'\[[^\]]\]$', '', the_name)
                    elif '.' in the_name:
                        the_name = re.sub(r'\.[^\.]*$', '', the_name)
                    else:
                        break
                    subnames.append(the_name)
                on_first = True
                for subname in subnames:
                    if the_type == 'defined by' and not on_first:
                        the_type = 'mentioned in'
                    on_first = False
                    if subname not in result_dict:
                        continue
                    if subname not in names_seen:
                        names_seen[subname] = {'yaml_file': question.from_source.path, 'source_code': question.source_code.strip(), 'usage': []}
                        result_dict[subname]['questions'].append(names_seen[subname])
                    if the_type not in names_seen[subname]['usage']:
                        names_seen[subname]['usage'].append(the_type)
    return jsonify(success=True, yaml_file=yaml_file, items=results)


@develop_bp.route('/playgroundvariables', methods=['POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_variables():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    playground_user = get_playground_user()
    current_project = get_current_project()
    playground = SavedFile(playground_user.id, fix=True, section='playground')
    the_directory = directory_for(playground, current_project)
    files = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    if len(files) == 0:
        return jsonify(success=False, reason=1)
    post_data = request.form.copy()
    if request.method == 'POST' and 'variablefile' in post_data:
        active_file = post_data['variablefile']
        if post_data['variablefile'] in files:
            if 'changed' in post_data and int(post_data['changed']):
                set_variable_file(current_project, active_file)
            interview_source = interview_source_from_string('docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file, raise_jinja_errors=False)
            interview_source.set_testing(True)
        else:
            if active_file == '' and current_project == 'default':
                active_file = 'test.yml'
            content = ''
            if 'playground_content' in post_data:
                content = re.sub(r'\r\n', r'\n', post_data['playground_content'])
            interview_source = InterviewSourceString(content=content, directory=the_directory, package="docassemble.playground" + str(playground_user.id) + project_name(current_project), path="docassemble.playground" + str(playground_user.id) + project_name(current_project) + ":" + active_file, testing=True)
        interview = Interview(source=interview_source)
        ensure_ml_file_exists(interview, active_file, current_project)
        the_current_info = current_info(yaml='docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file, req=request, action=None, device_id=request.cookies.get('ds', None))
        this_thread.current_info = the_current_info
        interview_status = InterviewStatus(current_info=the_current_info)
        variables_html, vocab_list, vocab_dict, ac_list = get_vars_in_use(interview, interview_status, debug_mode=False, current_project=current_project)  # pylint: disable=unused-variable
        return jsonify(success=True, variables_html=variables_html, vocab_list=vocab_list, current_project=current_project, ac_list=ac_list)
    return jsonify(success=False, reason=2)


def ensure_ml_file_exists(interview, yaml_file, current_project):
    playground_user = get_playground_user()
    if len(interview.mlfields) > 0:
        if hasattr(interview, 'ml_store'):
            parts = interview.ml_store.split(':')
            if parts[0] != 'docassemble.playground' + str(playground_user.id) + current_project:
                return
            source_filename = re.sub(r'.*/', '', parts[1])
        else:
            source_filename = 'ml-' + re.sub(r'\.ya?ml$', '', yaml_file) + '.json'
        # logmessage("Source filename is " + source_filename)
        source_dir = SavedFile(playground_user.id, fix=False, section='playgroundsources')
        source_directory = directory_for(source_dir, current_project)
        if current_project != 'default':
            source_filename = os.path.join(current_project, source_filename)
        if source_filename not in source_dir.list_of_files():
            # logmessage("Source filename does not exist yet")
            source_dir.fix()
            source_path = os.path.join(source_directory, source_filename)
            with open(source_path, 'a', encoding='utf-8'):
                os.utime(source_path, None)
            source_dir.finalize()


def assign_opacity(files):
    if len(files) == 1:
        files[0]['opacity'] = 1.0
    else:
        indexno = 0.0
        max_indexno = float(len(files) - 1)
        for file_dict in sorted(files, key=lambda x: x['modtime']):
            file_dict['opacity'] = round(0.2 + 0.8*(indexno/max_indexno), 2)
            indexno += 1.0


@develop_bp.route('/playground_run', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_page_run():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    playground_user = get_playground_user()
    current_project = get_current_project()
    the_file = secure_filename_spaces_ok(request.args.get('file'))
    if the_file:
        active_interview_string = 'docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + the_file
        the_url = url_for('interview.index', reset=1, i=active_interview_string)
        key = 'da:runplayground:' + str(playground_user.id)
        # logmessage("Setting key " + str(key) + " to " + str(the_url))
        pipe = r.pipeline()
        pipe.set(key, the_url)
        pipe.expire(key, 25)
        pipe.execute()
        return redirect(url_for('develop.playground_page', file=the_file, project=current_project))
    return redirect(url_for('develop.playground_page', project=current_project))


def get_list_of_projects(user_id):
    playground = SavedFile(user_id, fix=False, section='playground')
    return playground.list_of_dirs()


def rename_project(user_id, old_name, new_name):
    fix_package_folder()
    for sec in ('', 'sources', 'static', 'template', 'modules', 'packages'):
        area = SavedFile(user_id, fix=True, section='playground' + sec)
        if os.path.isdir(os.path.join(area.directory, old_name)):
            os.rename(os.path.join(area.directory, old_name), os.path.join(area.directory, new_name))
            area.finalize()


def create_project(user_id, new_name):
    fix_package_folder()
    for sec in ('', 'sources', 'static', 'template', 'modules', 'packages'):
        area = SavedFile(user_id, fix=True, section='playground' + sec)
        new_dir = os.path.join(area.directory, new_name)
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir, exist_ok=True)
        path = os.path.join(new_dir, '.placeholder')
        with open(path, 'a', encoding='utf-8'):
            os.utime(path, None)
        area.finalize()


def delete_project(user_id, the_project_name):
    fix_package_folder()
    for sec in ('', 'sources', 'static', 'template', 'modules', 'packages'):
        area = SavedFile(user_id, fix=True, section='playground' + sec)
        area.delete_directory(the_project_name)
        area.finalize()


@develop_bp.route('/playgroundproject', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_project():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    use_gd = bool(current_app.config['USE_GOOGLE_DRIVE'] is True and get_gd_folder() is not None)
    use_od = bool(use_gd is False and current_app.config['USE_ONEDRIVE'] is True and get_od_folder() is not None)
    playground_user = get_playground_user()
    current_project = get_current_project()
    if request.args.get('rename'):
        form = RenameProject(request.form)
        mode = 'rename'
        description = word("You are renaming the project called %s.") % (current_project, )
        page_title = word("Rename project")
        if request.method == 'POST' and form.validate():
            if current_project == 'default':
                flash(word("You cannot rename the default Playground project"), 'error')
            else:
                rename_project(playground_user.id, current_project, form.name.data)
                if use_gd:
                    try:
                        rename_gd_project(current_project, form.name.data)
                    except BaseException as the_err:
                        logmessage("playground_project: unable to rename project on Google Drive.  " + str(the_err))
                elif use_od:
                    try:
                        rename_od_project(current_project, form.name.data)
                    except BaseException as the_err:
                        try:
                            logmessage("playground_project: unable to rename project on OneDrive.  " + str(the_err))
                        except:
                            logmessage("playground_project: unable to rename project on OneDrive.")
                current_project = set_current_project(form.name.data)
                flash(word('Since you renamed a project, the server needs to restart in order to reload any modules.'), 'info')
                return redirect(url_for('main.restart_page', next=url_for('develop.playground_project', project=current_project)))
    elif request.args.get('new'):
        form = NewProject(request.form)
        mode = 'new'
        description = word("Enter the name of the new project you want to create.")
        page_title = word("New project")
        if request.method == 'POST' and form.validate():
            if form.name.data == 'default' or form.name.data in get_list_of_projects(playground_user.id):
                flash(word("The project name %s is not available.") % (form.name.data, ), "error")
            else:
                create_project(playground_user.id, form.name.data)
                current_project = set_current_project(form.name.data)
                mode = 'standard'
                return redirect(url_for('develop.playground_page', project=current_project))
    elif request.args.get('delete'):
        form = DeleteProject(request.form)
        mode = 'delete'
        description = word("WARNING!  If you press Delete, the contents of the %s project will be permanently deleted.") % (current_project, )
        page_title = word("Delete project")
        if request.method == 'POST' and form.validate():
            if current_project == 'default':
                flash(word("The default project cannot be deleted."), "error")
            else:
                if use_gd:
                    try:
                        trash_gd_project(current_project)
                    except BaseException as the_err:
                        logmessage("playground_project: unable to delete project on Google Drive.  " + str(the_err))
                elif use_od:
                    try:
                        trash_od_project(current_project)
                    except BaseException as the_err:
                        try:
                            logmessage("playground_project: unable to delete project on OneDrive.  " + str(the_err))
                        except:
                            logmessage("playground_project: unable to delete project on OneDrive.")
                delete_project(playground_user.id, current_project)
                flash(word("The project %s was deleted.") % (current_project,), "success")
                current_project = set_current_project('default')
                return redirect(url_for('develop.playground_project', project=current_project))
    else:
        form = None
        mode = 'standard'
        page_title = word("Projects")
        description = word("You can divide up your Playground into multiple separate areas, apart from your default Playground area.  Each Project has its own question files and Folders.")
    back_button = Markup('<span class="navbar-brand navbar-nav dabackicon me-3"><a href="' + url_for('develop.playground_page', project=current_project) + '" class="dabackbuttoncolor nav-link" title=' + json.dumps(word("Go back to the main Playground page")) + '><i class="fa-solid fa-chevron-left"></i><span class="daback">' + word('Back') + '</span></a></span>')
    response = make_response(render_template('develop/manage_projects.html', version_warning=None, bodyclass='daadminbody', back_button=back_button, tab_title=word("Projects"), description=description, page_title=page_title, projects=get_list_of_projects(playground_user.id), current_project=current_project, mode=mode, form=form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def set_current_project(new_name):
    key = 'da:playground:project:' + str(current_user.id)
    pipe = r.pipeline()
    pipe.set(key, new_name)
    pipe.expire(key, 2592000)
    pipe.execute()
    return new_name


def get_current_project():
    current_project = request.args.get('project', None)
    if current_project is not None:
        current_project = werkzeug.utils.secure_filename(current_project)
    key = 'da:playground:project:' + str(current_user.id)
    if current_project is None:
        current_project = r.get(key)
        if current_project is not None:
            current_project = current_project.decode()
    else:
        pipe = r.pipeline()
        pipe.set(key, current_project)
        pipe.expire(key, 2592000)
        pipe.execute()
    if current_project is None:
        return 'default'
    return current_project


def set_current_file(current_project, section, new_name):
    key = 'da:playground:project:' + str(current_user.id) + ':playground' + section + ':' + current_project
    pipe = r.pipeline()
    pipe.set(key, new_name)
    pipe.expire(key, 2592000)
    pipe.execute()
    return new_name


def get_current_file(current_project, section):
    key = 'da:playground:project:' + str(current_user.id) + ':playground' + section + ':' + current_project
    current_file = r.get(key)
    if current_file is None:
        return ''
    return current_file.decode()


def delete_current_file(current_project, section):
    key = 'da:playground:project:' + str(current_user.id) + ':playground' + section + ':' + current_project
    r.delete(key)


def clear_current_playground_info():
    r.delete('da:playground:project:' + str(current_user.id))
    to_delete = []
    for key in r.keys('da:playground:project:' + str(current_user.id) + ':playground*'):
        to_delete.append(key)
    for key in to_delete:
        r.delete(key)


def set_variable_file(current_project, variable_file):
    key = 'da:playground:project:' + str(current_user.id) + ':' + current_project + ':variablefile'
    pipe = r.pipeline()
    pipe.set(key, variable_file)
    pipe.expire(key, 2592000)
    pipe.execute()
    return variable_file


def get_variable_file(current_project):
    key = 'da:playground:project:' + str(current_user.id) + ':' + current_project + ':variablefile'
    variable_file = r.get(key)
    if variable_file is not None:
        variable_file = variable_file.decode()
    return variable_file


def delete_variable_file(current_project):
    key = 'da:playground:project:' + str(current_user.id) + ':' + current_project + ':variablefile'
    r.delete(key)


def get_list_of_playgrounds():
    user_list = []
    for user in db.session.execute(select(UserModel.id, UserModel.social_id, UserModel.email, UserModel.first_name, UserModel.last_name).join(UserRoles, UserModel.id == UserRoles.user_id).join(Role, UserRoles.role_id == Role.id).where(and_(UserModel.active == True, or_(Role.name == 'admin', Role.name == 'developer'))).distinct().order_by(UserModel.id)):  # noqa: E712 # pylint: disable=singleton-comparison
        if user.social_id.startswith('disabled$'):
            continue
        user_info = {}
        for attrib in ('id', 'email'):
            user_info[attrib] = getattr(user, attrib)
        name_string = ''
        if user.first_name:
            name_string += str(user.first_name) + " "
        if user.last_name:
            name_string += str(user.last_name)
        user_info['name'] = name_string
        user_list.append(user_info)
    return user_list


@develop_bp.route('/playgroundselect', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_select():
    setup_translation()
    if not (current_app.config['ENABLE_PLAYGROUND'] and current_app.config['ENABLE_SHARING_PLAYGROUNDS']):
        return ('File not found', 404)
    current_project = get_current_project()
    if request.args.get('select'):
        clear_current_playground_info()
        set_playground_user(int(request.args['select']))
        return redirect(url_for('develop.playground_page', project='default'))
    form = None
    mode = 'standard'
    page_title = word("All Playgrounds")
    description = word("You can use the Playground of another user who has admin or developer privileges.")
    back_button = Markup('<span class="navbar-brand navbar-nav dabackicon me-3"><a href="' + url_for('develop.playground_page', project=current_project) + '" class="dabackbuttoncolor nav-link" title=' + json.dumps(word("Go back to the main Playground page")) + '><i class="fa-solid fa-chevron-left"></i><span class="daback">' + word('Back') + '</span></a></span>')
    response = make_response(render_template('develop/manage_playgrounds.html', version_warning=None, bodyclass='daadminbody', back_button=back_button, tab_title=word("All Playgrounds"), description=description, page_title=page_title, playgrounds=get_list_of_playgrounds(), current_project=current_project, mode=mode, form=form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route("/pgcodecache", methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def get_pg_var_cache():
    response = make_response(bytesyaml.dump_to_bytes(pg_code_cache), 200)
    response.headers['Content-Disposition'] = 'attachment; filename=pgcodecache.yml'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


def playground_values(current_project, the_file, playground_user=None):
    values = {
        "currentProject": current_project,
        "currentFile": the_file,
        "daNotificationContainer": NOTIFICATION_CONTAINER,
        "daNotificationMessage": NOTIFICATION_MESSAGE,
        "daSessionLifetimeSeconds": 999 * int(daconfig.get('session lifetime seconds', 43200)),
        "daUrlPlaygroundPage": url_for('develop.playground_page'),
        "daUrlPlaygroundPageWithProject": url_for('develop.playground_page', project=current_project),
        "daGoogleDriveSyncUrl": url_for('develop.sync_with_google_drive', project=current_project, auto_next=url_for('develop.playground_page_run', file=the_file, project=current_project)),
        "daOneDriveSyncUrl": url_for('develop.sync_with_onedrive', project=current_project, auto_next=url_for('develop.playground_page_run', file=the_file, project=current_project)),
        "daWrapLines": bool(daconfig.get('wrap lines in playground', True)),
        "daKeymap": keymap,
        "daTranslations": {"in mako": word("in mako"),
                           "mentioned in": word("mentioned in"),
                           "defined by": word("defined by"),
                           "from": word("from"),
                           "loading": word("Loading . . ."),
                           "failedToLoad": word("Failed to load report"),
                           "sessionHasExpired": word("Your browser session has expired and you have been signed out.  You will not be able to save your work.  Please log in again."),
                           "fileExistWarning": word("Warning: a file by that name already exists.  If you save, you will overwrite it."),
                           "linkCopiedClipboard": word('Link copied to clipboard.'),
                           "unsavedChangesWarning": word("There are unsaved changes.  Are you sure you wish to leave this page?"),
                           "sureYouWantToDelete": word("Are you sure that you want to delete this playground file?"),
                           "sureYouWantToDeleteFile": word("Are you sure that you want to delete this file?"),
                           },
    }
    if playground_user:
        values.update({
            "interviewBaseUrl": url_for('interview.index', reset='1', cache='0', i='docassemble.playground' + str(playground_user.id) + ':.yml'),
            "shareBaseUrl": url_for('interview.index', i='docassemble.playground' + str(playground_user.id) + ':.yml', _external=True),
            "daVariablesReportUrl": url_for('develop.variables_report', project=current_project),
            "daUrlPlaygroundVariables": url_for('develop.playground_variables')
        })
    return values


@develop_bp.route('/playground', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_page():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    playground_user = get_playground_user()
    current_project = get_current_project()
    if 'ajax' in request.form and int(request.form['ajax']):
        is_ajax = True
        use_gd = False
        use_od = False
    else:
        is_ajax = False
        use_gd = bool(current_app.config['USE_GOOGLE_DRIVE'] is True and get_gd_folder() is not None)
        use_od = bool(use_gd is False and current_app.config['USE_ONEDRIVE'] is True and get_od_folder() is not None)
        if request.method == 'GET' and needs_to_change_password():
            return redirect(url_for('user.change_password', next=url_for('develop.playground_page', project=current_project)))
    fileform = PlaygroundUploadForm(request.form)
    form = PlaygroundForm(request.form)
    interview = None
    the_file = secure_filename_spaces_ok(request.args.get('file', get_current_file(current_project, 'questions')))
    valid_form = None
    if request.method == 'POST':
        valid_form = form.validate()
    if request.method == 'GET':
        is_new = true_or_false(request.args.get('new', False))
        debug_mode = true_or_false(request.args.get('debug', False))
    else:
        debug_mode = False
        is_new = bool(not valid_form and form.status.data == 'new')
    if is_new:
        the_file = ''
    playground = SavedFile(playground_user.id, fix=True, section='playground')
    the_directory = directory_for(playground, current_project)
    if current_project != 'default' and not os.path.isdir(the_directory):
        current_project = set_current_project('default')
        the_directory = directory_for(playground, current_project)
    if request.method == 'POST' and 'uploadfile' in request.files:
        the_files = request.files.getlist('uploadfile')
        if the_files:
            for up_file in the_files:
                try:
                    filename = secure_filename(up_file.filename)
                    extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
                    if extension not in ('yml', 'yaml'):
                        flash(word("Sorry, only YAML files can be uploaded here.  To upload other types of files, use the Folders."), 'error')
                        return redirect(url_for('develop.playground_page', project=current_project))
                    filename = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', filename)
                    new_file = filename
                    filename = os.path.join(the_directory, filename)
                    up_file.save(filename)
                    try:
                        with open(filename, 'r', encoding='utf-8') as fp:
                            fp.read()
                    except:
                        os.remove(filename)
                        flash(word("There was a problem reading the YAML file you uploaded.  Are you sure it is a YAML file?  File was not saved."), 'error')
                        return redirect(url_for('develop.playground_page', project=current_project))
                    playground.finalize()
                    r.incr('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + new_file)
                    flash(word("Uploaded %s to the Playground.") % (os.path.basename(filename),), 'success')
                    return redirect(url_for('develop.playground_page', project=current_project, file=os.path.basename(filename)))
                except BaseException as err_mess:
                    flash("Error of type " + str(type(err_mess)) + " processing upload: " + str(err_mess), "error")
        return redirect(url_for('develop.playground_page', project=current_project))
    if request.method == 'POST' and (form.submit.data or form.run.data or form.delete.data):
        if valid_form and form.playground_name.data:
            the_file = secure_filename_spaces_ok(form.playground_name.data)
            # the_file = re.sub(r'[^A-Za-z0-9\_\-\. ]', '', the_file)
            if the_file != '':
                if not re.search(r'\.ya?ml$', the_file):
                    the_file = re.sub(r'\..*', '', the_file) + '.yml'
                filename = os.path.join(the_directory, the_file)
                if not os.path.isfile(filename):
                    with open(filename, 'a', encoding='utf-8'):
                        os.utime(filename, None)
            else:
                # flash(word('You need to type in a name for the interview'), 'error')
                is_new = True
        else:
            # flash(word('You need to type in a name for the interview'), 'error')
            is_new = True
    # the_file = re.sub(r'[^A-Za-z0-9\_\-\. ]', '', the_file)
    files = sorted([{'name': f, 'modtime': os.path.getmtime(os.path.join(the_directory, f))} for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9].*[A-Za-z]$', f)], key=lambda x: x['name'])
    file_listing = [x['name'] for x in files]
    assign_opacity(files)
    if valid_form is False:
        content = form.playground_content.data
    else:
        content = ''
    if the_file and not is_new and the_file not in file_listing:
        if request.method == 'GET':
            delete_current_file(current_project, 'questions')
            return redirect(url_for('develop.playground_page', project=current_project))
        the_file = ''
    is_default = False
    if request.method == 'GET' and not the_file and not is_new:
        current_file = get_current_file(current_project, 'questions')
        if current_file in files:
            the_file = current_file
        else:
            delete_current_file(current_project, 'questions')
            if len(files) > 0:
                the_file = sorted(files, key=lambda x: x['modtime'])[-1]['name']
            elif current_project == 'default':
                the_file = 'test.yml'
                is_default = True
                content = default_playground_yaml
            else:
                the_file = ''
                is_default = False
                content = ''
                is_new = True
    if the_file in file_listing:
        set_current_file(current_project, 'questions', the_file)
    active_file = the_file
    current_variable_file = get_variable_file(current_project)
    if current_variable_file is not None:
        if current_variable_file in file_listing:
            active_file = current_variable_file
        else:
            delete_variable_file(current_project)
    if the_file != '':
        filename = os.path.join(the_directory, the_file)
        if (valid_form or is_default) and not os.path.isfile(filename):
            with open(filename, 'w', encoding='utf-8') as fp:
                fp.write(content)
            playground.finalize()
            files = sorted([{'name': f, 'modtime': os.path.getmtime(os.path.join(the_directory, f))} for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9].*[A-Za-z]$', f)], key=lambda x: x['name'])
    console_messages = []
    if request.method == 'POST' and the_file != '' and valid_form:
        if form.delete.data:
            filename_to_del = os.path.join(the_directory, form.playground_name.data)
            if os.path.isfile(filename_to_del):
                os.remove(filename_to_del)
                flash(word('File deleted.'), 'info')
                r.delete('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + the_file)
                if active_file != the_file:
                    r.incr('da:interviewsource:docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file)
                cloud_trash(use_gd, use_od, 'questions', form.playground_name.data, current_project)
                playground.finalize()
                current_variable_file = get_variable_file(current_project)
                if current_variable_file in (the_file, form.playground_name.data):
                    delete_variable_file(current_project)
                delete_current_file(current_project, 'questions')
                return redirect(url_for('develop.playground_page', project=current_project))
            flash(word('File not deleted.  There was an error.'), 'error')
        if (form.submit.data or form.run.data):
            if form.original_playground_name.data and form.original_playground_name.data != the_file:
                old_filename = os.path.join(the_directory, form.original_playground_name.data)
                if not is_ajax:
                    flash(word("Changed name of interview"), 'success')
                cloud_trash(use_gd, use_od, 'questions', form.original_playground_name.data, current_project)
                if os.path.isfile(old_filename):
                    os.remove(old_filename)
                    files = sorted([{'name': f, 'modtime': os.path.getmtime(os.path.join(the_directory, f))} for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9].*[A-Za-z]$', f)], key=lambda x: x['name'])
                    file_listing = [x['name'] for x in files]
                    assign_opacity(files)
                if active_file == form.original_playground_name.data:
                    active_file = the_file
                    set_variable_file(current_project, active_file)
            the_time = formatted_current_time()
            should_save = True
            the_content = re.sub(r'\r\n', r'\n', form.playground_content.data)
            if os.path.isfile(filename):
                with open(filename, 'r', encoding='utf-8') as fp:
                    orig_content = fp.read()
                    if orig_content == the_content:
                        # logmessage("No need to save")
                        should_save = False
            if should_save:
                with open(filename, 'w', encoding='utf-8') as fp:
                    fp.write(the_content)
            if not form.submit.data and active_file != the_file:
                active_file = the_file
                set_variable_file(current_project, active_file)
            this_interview_string = 'docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + the_file
            active_interview_string = 'docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file
            r.incr('da:interviewsource:' + this_interview_string)
            if the_file != active_file:
                r.incr('da:interviewsource:' + active_interview_string)
            playground.finalize()
            clear_cache(this_interview_string)
            if active_interview_string != this_interview_string:
                clear_cache(active_interview_string)
            if not form.submit.data:
                the_url = url_for('interview.index', reset=1, i=this_interview_string)
                key = 'da:runplayground:' + str(playground_user.id)
                # logmessage("Setting key " + str(key) + " to " + str(the_url))
                pipe = r.pipeline()
                pipe.set(key, the_url)
                pipe.expire(key, 12)
                pipe.execute()
            try:
                interview_source = interview_source_from_string(active_interview_string, raise_jinja_errors=False)
                interview_source.set_testing(True)
                interview = Interview(source=interview_source)
                ensure_ml_file_exists(interview, active_file, current_project)
                yaml = 'docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file
                session_id_to_use = uid_or_random(yaml)
                the_current_info = current_info(yaml=yaml, req=request, action=None, device_id=request.cookies.get('ds', None), session_uid=session_id_to_use)
                the_current_info['session'] = session_id_to_use
                this_thread.current_info = the_current_info
                interview_status = InterviewStatus(current_info=the_current_info)
                variables_html, vocab_list, vocab_dict, ac_list = get_vars_in_use(interview, interview_status, debug_mode=debug_mode, current_project=current_project)  # pylint: disable=unused-variable
                if form.submit.data:
                    flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.', 'success', is_ajax=is_ajax)
                else:
                    flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Running in other tab.'), message_type='success', is_ajax=is_ajax)
                if interview.issue.get('mandatory_id', False):
                    console_messages.append(word("Note: it is a best practice to tag every mandatory block with an id."))
                if interview.issue.get('id_collision', False):
                    console_messages.append(word("Note: more than one block uses id") + " " + interview.issue['id_collision'])
            except DAError:
                variables_html = None
                flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Problem detected.'), message_type='error', is_ajax=is_ajax)
            if is_ajax:
                return jsonify(variables_html=variables_html, vocab_list=vocab_list, ac_list=ac_list, flash_message=flash_message, current_project=current_project, console_messages=console_messages, active_file=active_file, active_interview_url=url_for('interview.index', i=active_interview_string, _external=True))
        else:
            flash(word('Playground not saved.  There was an error.'), 'error')
    interview_path = None
    if valid_form is not False and the_file != '':
        with open(filename, 'r', encoding='utf-8') as fp:
            form.original_playground_name.data = the_file
            form.playground_name.data = the_file
            content = fp.read()
            # if not form.playground_content.data:
            #     form.playground_content.data = content
    if active_file != '':
        is_fictitious = False
        interview_path = 'docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file
        if is_default:
            interview_source = InterviewSourceString(content=content, directory=the_directory, package="docassemble.playground" + str(playground_user.id) + project_name(current_project), path="docassemble.playground" + str(playground_user.id) + project_name(current_project) + ":" + active_file, testing=True)
        else:
            interview_source = interview_source_from_string(interview_path, raise_jinja_errors=False)
            interview_source.set_testing(True)
    else:
        is_fictitious = True
        if current_project == 'default':
            active_file = 'test.yml'
        else:
            is_new = True
        if form.playground_content.data:
            content = re.sub(r'\r', '', form.playground_content.data)
            interview_source = InterviewSourceString(content=content, directory=the_directory, package="docassemble.playground" + str(playground_user.id) + project_name(current_project), path="docassemble.playground" + str(playground_user.id) + project_name(current_project) + ":" + active_file, testing=True)
        else:
            interview_source = InterviewSourceString(content='', directory=the_directory, package="docassemble.playground" + str(playground_user.id) + project_name(current_project), path="docassemble.playground" + str(playground_user.id) + project_name(current_project) + ":" + active_file, testing=True)
    interview = Interview(source=interview_source)
    if hasattr(interview, 'mandatory_id_issue') and interview.mandatory_id_issue:  # pylint: disable=no-member
        console_messages.append(word("Note: it is a best practice to tag every mandatory block with an id."))
    yaml = 'docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file
    session_id_to_use = uid_or_random(yaml)
    the_current_info = current_info(yaml='docassemble.playground' + str(playground_user.id) + project_name(current_project) + ':' + active_file, req=request, action=None, device_id=request.cookies.get('ds', None), session_uid=session_id_to_use)
    the_current_info['session'] = session_id_to_use
    this_thread.current_info = the_current_info
    interview_status = InterviewStatus(current_info=the_current_info)
    variables_html, vocab_list, vocab_dict, ac_list = get_vars_in_use(interview, interview_status, debug_mode=debug_mode, current_project=current_project)
    dropdown_files = [x['name'] for x in files]
    define_examples()
    if is_fictitious or is_new:
        new_active_file = word('(New file)')
        if new_active_file not in dropdown_files:
            dropdown_files.insert(0, new_active_file)
        if is_fictitious:
            active_file = new_active_file
    initial_values = playground_values(current_project, the_file, playground_user)
    initial_values.update({
        "daPage": 'questions',
        "isNew": is_new,
        "existingFiles": file_listing,
        "daConsoleMessages": console_messages,
        "daAutoComp": ac_list,
        "daContent": content,
        "validForm": valid_form,
        "vocab": vocab_list,
        "originalFileName": the_file,
        "daEncodedExampleData": [pg_ex['encoded_data_dict'], pg_ex['pg_first_id'][0]] if pg_ex['encoded_data_dict'] is not None else None
    })
    any_files = len(files) > 0
    page_title = word("Playground")
    if current_user.id != playground_user.id:
        page_title += " / " + playground_user.email
    if current_project != 'default':
        page_title += " / " + current_project
    extra_js = f"""
    <script{DEFER} src="{url_for('static', filename="app/playgroundbundle.min.js", v=da_version)}"></script>
    {redis_script(initial_values)}"""
    response = make_response(render_template('develop/playground.html', projects=get_list_of_projects(playground_user.id), current_project=current_project, version_warning=None, bodyclass='daadminbody', use_gd=use_gd, use_od=use_od, userid=playground_user.id, page_title=Markup(page_title), tab_title=word("Playground"), extra_css=Markup('\n    <link href="' + url_for('static', filename='app/playgroundbundle.css', v=da_version) + '" rel="stylesheet">'), extra_js=Markup(extra_js), form=form, fileform=fileform, files=sorted(files, key=lambda y: y['name'].lower()), any_files=any_files, dropdown_files=sorted(dropdown_files, key=lambda y: y.lower()), current_file=the_file, active_file=active_file, content=content, variables_html=Markup(variables_html), example_html=pg_ex['encoded_example_html'], interview_path=interview_path, is_new=str(is_new), valid_form=str(valid_form), own_playground=bool(playground_user.id == current_user.id), action=url_for('develop.playground_page', project=current_project)), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/playgroundbundle.css', methods=['GET'])
def playground_css_bundle():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = ''
    for parts in [['app', 'pygments.css'], ['bootstrap', 'css', 'bootstrap-icons.css'], ['bootstrap-fileinput', 'css', 'fileinput.css']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    return Response(output, mimetype='text/css')

@develop_bp.route('/github_menu', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_menu():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if not current_app.config['USE_GITHUB']:
        return ('File not found', 404)
    setup_translation()
    form = GitHubForm(request.form)
    if request.method == 'POST':
        if form.configure.data:
            r.delete('da:github:userid:' + str(current_user.id))
            return redirect(url_for('develop.github_configure'))
        if form.unconfigure.data:
            return redirect(url_for('develop.github_unconfigure'))
        if form.cancel.data:
            return redirect(url_for('users.user_profile_page'))
        if form.save.data:
            info = {}
            info['shared'] = bool(form.shared.data)
            info['orgs'] = bool(form.orgs.data)
            r.set('da:using_github:userid:' + str(current_user.id), json.dumps(info))
            flash(word("Your GitHub settings were saved."), 'info')
    uses_github = r.get('da:using_github:userid:' + str(current_user.id))
    if uses_github is not None:
        uses_github = uses_github.decode()
        if uses_github == '1':
            form.shared.data = True
            form.orgs.data = True
        else:
            info = json.loads(uses_github)
            form.shared.data = info['shared']
            form.orgs.data = info['orgs']
        description = word("Your GitHub integration is currently turned on.  Below, you can change which repositories docassemble can access.  You can disable GitHub integration if you no longer wish to use it.")
    else:
        description = word("If you have a GitHub account, you can turn on GitHub integration.  This will allow you to use GitHub as a version control system for packages from inside the Playground.")
    return render_template('develop/github.html', form=form, version_warning=None, title=word("GitHub Integration"), tab_title=word("GitHub"), page_title=word("GitHub"), description=description, uses_github=uses_github, bodyclass='daadminbody')


@develop_bp.route('/github_configure', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_configure():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if not current_app.config['USE_GITHUB']:
        return ('File not found', 404)
    setup_translation()
    storage = RedisCredStorage(oauth_app='github')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        state_string = random_string(16)
        session['github_next'] = json.dumps({'state': state_string, 'path': 'github_configure', 'arguments': request.args})
        flow = get_github_flow()
        uri = flow.step1_get_authorize_url(state=state_string)
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    found = False
    try:
        resp, content = http.request("https://api.github.com/user/emails", "GET")
        assert int(resp['status']) == 200
    except:
        r.delete('da:github:userid:' + str(current_user.id))
        r.delete('da:using_github:userid:' + str(current_user.id))
        flash(word("There was a problem connecting to GitHub. Please check your GitHub configuration and try again."), 'danger')
        return redirect(url_for('develop.github_menu'))
    user_info_list = json.loads(content.decode())
    user_info = None
    for item in user_info_list:
        if item.get('email', None) and item.get('visibility', None) != 'private':
            user_info = item
    if user_info is None:
        logmessage("github_configure: could not get information about user")
        r.delete('da:github:userid:' + str(current_user.id))
        r.delete('da:using_github:userid:' + str(current_user.id))
        flash(word("There was a problem connecting to GitHub. Please check your GitHub configuration and try again."), 'danger')
        return redirect(url_for('develop.github_menu'))
    try:
        resp, content = http.request("https://api.github.com/user/keys", "GET")
        assert int(resp['status']) == 200
        for key in json.loads(content.decode()):
            if key['title'] == current_app.config['APP_NAME'] or key['title'] == current_app.config['APP_NAME'] + '_user_' + str(current_user.id):
                found = True
    except:
        logmessage("github_configure: could not get information about ssh keys")
        r.delete('da:github:userid:' + str(current_user.id))
        r.delete('da:using_github:userid:' + str(current_user.id))
        flash(word("There was a problem connecting to GitHub. Please check your GitHub configuration and try again."), 'danger')
        return redirect(url_for('develop.github_menu'))
    while found is False:
        next_link = get_next_link(resp)
        if next_link:
            resp, content = http.request(next_link, "GET")
            if int(resp['status']) == 200:
                for key in json.loads(content.decode()):
                    if key['title'] == current_app.config['APP_NAME'] or key['title'] == current_app.config['APP_NAME'] + '_user_' + str(current_user.id):
                        found = True
            else:
                r.delete('da:github:userid:' + str(current_user.id))
                r.delete('da:using_github:userid:' + str(current_user.id))
                flash(word("There was a problem connecting to GitHub. Please check your GitHub configuration and try again."), 'danger')
                return redirect(url_for('develop.github_menu'))
        else:
            break
    if found:
        flash(word("An SSH key is already installed on your GitHub account. The existing SSH key will not be replaced. Note that if you are connecting to GitHub from multiple docassemble servers, each server needs to have a different appname in the Configuration. If you have problems using GitHub, disable the integration and configure it again."), 'info')
    if not found:
        (private_key_file, public_key_file) = get_ssh_keys(user_info['email'])  # pylint: disable=unused-variable
        with open(public_key_file, 'r', encoding='utf-8') as fp:
            public_key = fp.read()
        headers = {'Content-Type': 'application/json'}
        body = json.dumps({'title': current_app.config['APP_NAME'] + '_user_' + str(current_user.id), 'key': public_key})
        resp, content = http.request("https://api.github.com/user/keys", "POST", headers=headers, body=body)
        if int(resp['status']) == 201:
            flash(word("GitHub integration was successfully configured."), 'info')
        else:
            logmessage("github_configure: error setting public key")
            r.delete('da:github:userid:' + str(current_user.id))
            r.delete('da:using_github:userid:' + str(current_user.id))
            flash(word("There was a problem connecting to GitHub. Please check your GitHub configuration and try again."), 'danger')
            return redirect(url_for('develop.github_menu'))
    r.set('da:using_github:userid:' + str(current_user.id), json.dumps({'shared': True, 'orgs': True}))
    return redirect(url_for('develop.github_menu'))


@develop_bp.route('/github_unconfigure', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_unconfigure():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if not current_app.config['USE_GITHUB']:
        return ('File not found', 404)
    setup_translation()
    storage = RedisCredStorage(oauth_app='github')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        state_string = random_string(16)
        session['github_next'] = json.dumps({'state': state_string, 'path': 'github_unconfigure', 'arguments': request.args})
        flow = get_github_flow()
        uri = flow.step1_get_authorize_url(state=state_string)
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    ids_to_remove = []
    try:
        resp, content = http.request("https://api.github.com/user/keys", "GET")
        if int(resp['status']) == 200:
            for key in json.loads(content.decode()):
                if key['title'] == current_app.config['APP_NAME'] or key['title'] == current_app.config['APP_NAME'] + '_user_' + str(current_user.id):
                    ids_to_remove.append(key['id'])
        else:
            raise DAError("github_configure: could not get information about ssh keys")
        while True:
            next_link = get_next_link(resp)
            if next_link:
                resp, content = http.request(next_link, "GET")
                if int(resp['status']) == 200:
                    for key in json.loads(content.decode()):
                        if key['title'] == current_app.config['APP_NAME'] or key['title'] == current_app.config['APP_NAME'] + '_user_' + str(current_user.id):
                            ids_to_remove.append(key['id'])
                else:
                    raise DAError("github_unconfigure: could not get additional information about ssh keys")
            else:
                break
        for id_to_remove in ids_to_remove:
            resp, content = http.request("https://api.github.com/user/keys/" + str(id_to_remove), "DELETE")
            if int(resp['status']) != 204:
                raise DAError("github_unconfigure: error deleting public key " + str(id_to_remove) + ": " + str(resp['status']) + " content: " + content.decode())
    except:
        logmessage("Error deleting SSH keys on GitHub")
    delete_ssh_keys()
    r.delete('da:github:userid:' + str(current_user.id))
    r.delete('da:using_github:userid:' + str(current_user.id))
    flash(word("GitHub integration was successfully disconnected."), 'info')
    return redirect(url_for('users.user_profile_page'))


@develop_bp.route('/github_oauth_callback', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_oauth_callback():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    setup_translation()
    failed = False
    do_a_redirect = False
    if not current_app.config['USE_GITHUB']:
        logmessage('github_oauth_callback: server does not use github')
        failed = True
    elif 'github_next' not in session:
        logmessage('github_oauth_callback: next not in session')
        failed = True
    if failed is False:
        github_next = json.loads(session['github_next'])
        del session['github_next']
        if 'code' not in request.args or 'state' not in request.args:
            logmessage('github_oauth_callback: code and state not in args')
            failed = True
            do_a_redirect = True
        elif request.args['state'] != github_next['state']:
            logmessage('github_oauth_callback: state did not match')
            failed = True
    if failed:
        r.delete('da:github:userid:' + str(current_user.id))
        r.delete('da:using_github:userid:' + str(current_user.id))
        if do_a_redirect:
            flash(word("There was a problem connecting to GitHub. Please check your GitHub configuration and try again."), 'danger')
            return redirect(url_for('develop.github_menu'))
        return ('File not found', 404)
    flow = get_github_flow()
    credentials = flow.step2_exchange(request.args['code'])
    storage = RedisCredStorage(oauth_app='github')
    storage.put(credentials)
    return redirect(github_next['path'], **github_next['arguments'])


@develop_bp.route("/vars", methods=['POST', 'GET'])
def get_variables():
    yaml_filename = request.args.get('i', None)
    if yaml_filename is None:
        return ("Invalid request", 400)
    session_info = get_session(yaml_filename)
    if session_info is None:
        return ("Invalid request", 400)
    session_id = session_info['uid']
    if 'visitor_secret' in request.cookies:
        secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    # session_cookie_id = request.cookies.get('session', None)
    if session_id is None or yaml_filename is None:
        return jsonify(success=False)
    # logmessage("get_variables: fetch_user_dict")
    this_thread.current_info = current_info(yaml=yaml_filename, req=request, interface='vars', device_id=request.cookies.get('ds', None))
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        assert user_dict is not None
    except:
        return jsonify(success=False)
    if (not DEBUG) and '_internal' in user_dict and 'misc' in user_dict['_internal'] and 'variable_access' in user_dict['_internal']['misc'] and user_dict['_internal']['misc']['variable_access'] is False:
        return jsonify(success=False)
    variables = serializable_dict(user_dict, include_internal=True)
    # variables['_internal'] = serializable_dict(user_dict['_internal'])
    return jsonify(success=True, variables=variables, steps=steps, encrypted=is_encrypted, uid=session_id, i=yaml_filename)


@develop_bp.route("/test_embed", methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def test_embed():
    setup_translation()
    yaml_filename = request.args.get('i', final_default_yaml_filename)
    user_dict = fresh_dictionary()
    interview = get_interview(yaml_filename)
    the_current_info = current_info(yaml=yaml_filename, req=request, action=None, location=None, interface='web', device_id=request.cookies.get('ds', None))
    this_thread.current_info = the_current_info
    interview_status = InterviewStatus(current_info=the_current_info)
    try:
        interview.assemble(user_dict, interview_status)
    except:
        pass
    current_language = get_language()
    page_title = word("Embed test")
    if interview.options.get('analytics on', True):
        if ga_configured:
            ga_ids = google_config.get('analytics id')
        else:
            ga_ids = None
    else:
        ga_ids = None
    start_part = standard_html_start(interview_language=current_language, debug=False, bootstrap_theme=interview_status.question.interview.get_bootstrap_theme(), external=True, page_title=page_title, social=daconfig['social'], yaml_filename=yaml_filename) + current_app.config['GLOBAL_CSS'] + additional_css(interview_status)
    scripts = standard_scripts(interview_language=current_language, external=True) + additional_scripts(ga_ids) + current_app.config['GLOBAL_JS']
    response = make_response(render_template('develop/test_embed.html', scripts=scripts, start_part=start_part, interview_url=url_for('interview.index', i=yaml_filename, js_target='dablock', _external=True), page_title=page_title), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/packagezip', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def download_zip_package():
    package_name = request.args.get('package', None)
    if not package_name:
        return ('File not found', 404)
    package_name = werkzeug.utils.secure_filename(package_name)
    package = db.session.execute(select(Package).filter_by(active=True, name=package_name, type='zip')).scalar()
    if package is None:
        return ('File not found', 404)
    if not current_user.has_role('admin'):
        auth = db.session.execute(select(PackageAuth).filter_by(package_id=package.id, user_id=current_user.id)).scalar()
        if auth is None:
            return ('File not found', 404)
    try:
        file_info = get_info_from_file_number(package.upload, privileged=True)
    except:
        return ('File not found', 404)
    filename = re.sub(r'\.', '-', package_name) + '.zip'
    response = custom_send_file(file_info['path'] + '.zip', mimetype='application/zip', download_name=filename)
    response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/createplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_playground_package():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    fix_package_folder()
    playground_user = get_playground_user()
    current_project = get_current_project()
    form = CreatePlaygroundPackageForm(request.form)
    current_package = request.args.get('package', None)
    if current_package is not None:
        current_package = werkzeug.utils.secure_filename(current_package)
    do_pypi = request.args.get('pypi', False)
    do_github = request.args.get('github', False)
    if current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin'):
        do_install = request.args.get('install', False)
    else:
        do_install = False
    branch = request.args.get('branch', None)
    if branch is not None:
        branch = branch.strip()
    if branch in ('', 'None'):
        branch = None
    new_branch = request.args.get('new_branch', None)
    if new_branch is not None and new_branch not in ('', 'None'):
        branch = new_branch
    sanitize_arguments(do_pypi, do_github, do_install, branch, new_branch)
    if current_app.config['USE_GITHUB']:
        github_auth = r.get('da:using_github:userid:' + str(current_user.id))
    else:
        github_auth = None
    area = {}
    area['playgroundpackages'] = SavedFile(playground_user.id, fix=True, section='playgroundpackages')
    if os.path.isfile(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + current_package)):
        filename = os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + current_package)
        info = {}
        with open(filename, 'r', encoding='utf-8') as fp:
            content = fp.read()
            info = standardyaml.load(content, Loader=standardyaml.FullLoader)
    else:
        info = {}
    if do_github:
        if not current_app.config['USE_GITHUB']:
            return ('File not found', 404)
        if current_package is None:
            logmessage('create_playground_package: package not specified')
            return ('File not found', 404)
        if not github_auth:
            logmessage('create_playground_package: github button called when github auth not enabled.')
            return ('File not found', 404)
        github_auth = github_auth.decode()
        if github_auth == '1':
            github_auth_info = {'shared': True, 'orgs': True}
        else:
            github_auth_info = json.loads(github_auth)
        github_package_name = 'docassemble-' + re.sub(r'^docassemble-', r'', current_package)
        # github_package_name = re.sub(r'[^A-Za-z\_\-]', '', github_package_name)
        if 'github_to_add' in session:
            files_to_add = session['github_to_add']
            del session['github_to_add']
        else:
            files_to_add = None
        if github_package_name in ('docassemble-base', 'docassemble-webapp', 'docassemble-demo'):
            return ('File not found', 404)
        commit_message = request.args.get('commit_message', 'a commit')
        storage = RedisCredStorage(oauth_app='github')
        credentials = storage.get()
        if not credentials or credentials.invalid:
            state_string = random_string(16)
            session['github_next'] = json.dumps({'state': state_string, 'path': 'create_playground_package', 'arguments': request.args})
            flow = get_github_flow()
            uri = flow.step1_get_authorize_url(state=state_string)
            return redirect(uri)
        http = credentials.authorize(httplib2.Http())
        resp, content = http.request("https://api.github.com/user", "GET")
        if int(resp['status']) == 200:
            user_info = json.loads(content.decode())
            github_user_name = user_info.get('login', None)
            github_email = user_info.get('email', None)
        else:
            raise DAError("create_playground_package: could not get information about GitHub User")
        if github_email is None:
            resp, content = http.request("https://api.github.com/user/emails", "GET")
            if int(resp['status']) == 200:
                email_info = json.loads(content.decode())
                for item in email_info:
                    if item.get('email', None) and item.get('visibility', None) != 'private':
                        github_email = item['email']
        if github_user_name is None or github_email is None:
            raise DAError("create_playground_package: login and/or email not present in user info from GitHub")
        github_url_from_file = info.get('github_url', None)
        found = False
        found_strong = False
        commit_repository = None
        resp, content = http.request("https://api.github.com/repos/" + str(github_user_name) + "/" + github_package_name, "GET")
        if int(resp['status']) == 200:
            repo_info = json.loads(content.decode('utf-8', 'ignore'))
            commit_repository = repo_info
            found = True
            if github_url_from_file is None or github_url_from_file in [repo_info['html_url'], repo_info['ssh_url']]:
                found_strong = True
        if found_strong is False and github_auth_info['shared']:
            repositories = get_user_repositories(http)
            for repo_info in repositories:
                if repo_info['name'] != github_package_name or (commit_repository is not None and commit_repository.get('html_url', None) is not None and commit_repository['html_url'] == repo_info['html_url']) or (commit_repository is not None and commit_repository.get('ssh_url', None) is not None and commit_repository['ssh_url'] == repo_info['ssh_url']):
                    continue
                if found and github_url_from_file is not None and github_url_from_file not in [repo_info['html_url'], repo_info['ssh_url']]:
                    break
                commit_repository = repo_info
                found = True
                if github_url_from_file is None or github_url_from_file in [repo_info['html_url'], repo_info['ssh_url']]:
                    found_strong = True
                break
        if found_strong is False and github_auth_info['orgs']:
            orgs_info = get_orgs_info(http)
            for org_info in orgs_info:
                resp, content = http.request("https://api.github.com/repos/" + str(org_info['login']) + "/" + github_package_name, "GET")
                if int(resp['status']) == 200:
                    repo_info = json.loads(content.decode('utf-8', 'ignore'))
                    if found and github_url_from_file is not None and github_url_from_file not in [repo_info['html_url'], repo_info['ssh_url']]:
                        break
                    commit_repository = repo_info
                    break
    file_list = {}
    the_directory = directory_for(area['playgroundpackages'], current_project)
    file_list['playgroundpackages'] = sorted([re.sub(r'^docassemble\.', r'', f) for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    the_choices = []
    for file_option in file_list['playgroundpackages']:
        the_choices.append((file_option, file_option))
    form.name.choices = the_choices
    if request.method == 'POST':
        if form.validate():
            current_package = form.name.data
            # flash("form validated", 'success')
        else:
            the_error = ''
            for error in form.name.errors:
                the_error += str(error)
            flash("form did not validate with " + str(form.name.data) + " " + str(the_error) + " among " + str(form.name.choices), 'error')
    if current_package is not None:
        pkgname = re.sub(r'^docassemble-', r'', current_package)
        # if not user_can_edit_package(pkgname='docassemble.' + pkgname):
        #    flash(word('That package name is already in use by someone else.  Please change the name.'), 'error')
        #    current_package = None
    if current_package is not None and current_package not in file_list['playgroundpackages']:
        flash(word('Sorry, that package name does not exist in the playground'), 'error')
        current_package = None
    if current_package is not None:
        # section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
        for sec in ('playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules'):
            area[sec] = SavedFile(playground_user.id, fix=True, section=sec)
            the_directory = directory_for(area[sec], current_project)
            if os.path.isdir(the_directory):
                file_list[sec] = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
            else:
                file_list[sec] = []
        if os.path.isfile(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + current_package)):
            filename = os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + current_package)
            info = {}
            with open(filename, 'r', encoding='utf-8') as fp:
                content = fp.read()
                info = standardyaml.load(content, Loader=standardyaml.FullLoader)
            for field in ('dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files'):
                if field not in info:
                    info[field] = []
            info['dependencies'] = list(x for x in map(lambda y: re.sub(r'[\>\<\=].*', '', y), info['dependencies']) if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp'))
            info['modtime'] = os.path.getmtime(filename)
            author_info = {}
            author_info['author name and email'] = name_of_user(playground_user, include_email=True)
            author_info['author name'] = name_of_user(playground_user)
            author_info['author email'] = playground_user.email
            author_info['first name'] = playground_user.first_name
            author_info['last name'] = playground_user.last_name
            author_info['id'] = playground_user.id
            if do_pypi:
                if current_user.pypi_username is None or current_user.pypi_password is None or current_user.pypi_username == '' or current_user.pypi_password == '':
                    flash("Could not publish to PyPI because username and password were not defined")
                    return redirect(url_for('develop.playground_packages', project=current_project, file=current_package))
                if playground_user.timezone:
                    the_timezone = playground_user.timezone
                else:
                    the_timezone = get_default_timezone()
                fix_ml_files(author_info['id'], current_project)
                had_error, logmessages = publish_package(pkgname, info, author_info, current_project=current_project)
                flash(logmessages, 'danger' if had_error else 'info')
                if not do_install:
                    time.sleep(3.0)
                    return redirect(url_for('develop.playground_packages', project=current_project, file=current_package))
            if do_github:
                if commit_repository is not None:
                    resp, content = http.request("https://api.github.com/repos/" + commit_repository['full_name'] + "/commits?per_page=1", "GET")
                    if int(resp['status']) == 200:
                        commit_list = json.loads(content.decode('utf-8', 'ignore'))
                        if len(commit_list) == 0:
                            first_time = True
                            is_empty = True
                        else:
                            first_time = False
                            is_empty = False
                    else:
                        first_time = True
                        is_empty = True
                else:
                    first_time = True
                    is_empty = False
                    headers = {'Content-Type': 'application/json'}
                    the_license = 'mit' if re.search(r'MIT', info.get('license', '')) else None
                    body = json.dumps({'name': github_package_name, 'description': info.get('description', None), 'homepage': info.get('url', None), 'license_template': the_license})
                    resp, content = http.request("https://api.github.com/user/repos", "POST", headers=headers, body=body)
                    if int(resp['status']) != 201:
                        raise DAError("create_playground_package: unable to create GitHub repository: status " + str(resp['status']) + " " + str(content))
                    resp, content = http.request("https://api.github.com/repos/" + str(github_user_name) + "/" + github_package_name, "GET")
                    if int(resp['status']) == 200:
                        commit_repository = json.loads(content.decode('utf-8', 'ignore'))
                    else:
                        raise DAError("create_playground_package: GitHub repository could not be found after creating it.")
                if first_time:
                    logmessage("Not checking for stored commit code because no target repository exists")
                    pulled_already = False
                else:
                    current_commit_file = os.path.join(directory_for(area['playgroundpackages'], current_project), '.' + github_package_name)
                    if os.path.isfile(current_commit_file):
                        with open(current_commit_file, 'r', encoding='utf-8') as fp:
                            commit_code = fp.read()
                        commit_code = commit_code.strip()
                        resp, content = http.request("https://api.github.com/repos/" + commit_repository['full_name'] + "/commits/" + commit_code, "GET")
                        if int(resp['status']) == 200:
                            logmessage("Stored commit code is valid")
                            pulled_already = True
                        else:
                            logmessage("Stored commit code is invalid")
                            pulled_already = False
                    else:
                        logmessage("Commit file not found")
                        pulled_already = False
                directory = tempfile.mkdtemp(prefix='SavedFile')
                (private_key_file, public_key_file) = get_ssh_keys(github_email)
                os.chmod(private_key_file, stat.S_IRUSR | stat.S_IWUSR)
                os.chmod(public_key_file, stat.S_IRUSR | stat.S_IWUSR)
                ssh_script = tempfile.NamedTemporaryFile(mode='w', prefix="datemp", suffix='.sh', delete=False, encoding='utf-8')
                ssh_script.write('# /bin/bash\n\nssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i "' + str(private_key_file) + '" $1 $2 $3 $4 $5 $6')
                ssh_script.close()
                os.chmod(ssh_script.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                # git_prefix = "GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i \"" + str(private_key_file) + "\"' "
                git_prefix = "GIT_SSH=" + ssh_script.name + " "
                git_env = dict(os.environ, GIT_SSH=ssh_script.name)
                ssh_url = commit_repository.get('ssh_url', None)
                # github_url = commit_repository.get('html_url', None)
                commit_branch = commit_repository.get('default_branch', GITHUB_BRANCH)
                if ssh_url is None:
                    raise DAError("create_playground_package: could not obtain ssh_url for package")
                output = ''
                # if branch:
                #     branch_option = '-b ' + str(branch) + ' '
                # else:
                #     branch_option = '-b ' + commit_branch + ' '
                tempbranch = 'playground' + random_string(5)
                packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
                the_user_name = str(playground_user.first_name) + " " + str(playground_user.last_name)
                if the_user_name == ' ':
                    the_user_name = 'Anonymous User'
                if is_empty:
                    os.makedirs(packagedir)
                    output += "Doing git init\n"
                    try:
                        output += subprocess.check_output(["git", "init"], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output
                        raise DAError("create_playground_package: error running git init.  " + output) from err
                    with open(os.path.join(packagedir, 'README.md'), 'w', encoding='utf-8') as the_file:
                        the_file.write("")
                    if files_to_add is not None and '.gitignore' in files_to_add:
                        with open(os.path.join(packagedir, '.gitignore'), 'w', encoding='utf-8') as the_file:
                            the_file.write(DEFAULT_GITIGNORE)
                    output += "Doing git config user.email " + json.dumps(github_email) + "\n"
                    try:
                        output += subprocess.check_output(["git", "config", "user.email", json.dumps(github_email)], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git config user.email.  " + output) from err
                    output += "Doing git config user.name " + json.dumps(the_user_name) + "\n"
                    try:
                        output += subprocess.check_output(["git", "config", "user.name", json.dumps(the_user_name)], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git config user.name.  " + output) from err
                    output += "Doing git add README.md\n"
                    try:
                        output += subprocess.check_output(["git", "add", "README.md"], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git add README.md.  " + output) from err
                    if files_to_add is not None and '.gitignore' in files_to_add:
                        output += "Doing git add .gitignore\n"
                        try:
                            output += subprocess.check_output(["git", "add", ".gitignore"], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                        except subprocess.CalledProcessError as err:
                            output += err.output.decode()
                            raise DAError("create_playground_package: error running git add .gitignore.  " + output) from err
                    output += "Doing git commit -m \"first commit\"\n"
                    try:
                        output += subprocess.check_output(["git", "commit", "-m", "first commit"], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git commit -m \"first commit\".  " + output) from err
                    output += "Doing git branch -M " + commit_branch + "\n"
                    try:
                        output += subprocess.check_output(["git", "branch", "-M", commit_branch], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git branch -M " + commit_branch + ".  " + output) from err
                    output += "Doing git remote add origin " + ssh_url + "\n"
                    try:
                        output += subprocess.check_output(["git", "remote", "add", "origin", ssh_url], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git remote add origin.  " + output) from err
                    output += "Doing " + git_prefix + "git push -u origin " + '"' + commit_branch + '"' + "\n"
                    try:
                        output += subprocess.check_output(["git", "push", "-u", "origin ", commit_branch], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running first git push.  " + output) from err
                else:
                    output += "Doing " + git_prefix + "git clone " + ssh_url + "\n"
                    try:
                        output += subprocess.check_output(["git", "clone", ssh_url], cwd=directory, stderr=subprocess.STDOUT, env=git_env).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git clone.  " + output) from err
                if not os.path.isdir(packagedir):
                    raise DAError("create_playground_package: package directory did not exist.  " + output)
                if pulled_already:
                    output += "Doing git checkout " + commit_code + "\n"
                    try:
                        output += subprocess.check_output(["git", "checkout", commit_code], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        # raise DAError("create_playground_package: error running git checkout.  " + output)
                if playground_user.timezone:
                    the_timezone = playground_user.timezone
                else:
                    the_timezone = get_default_timezone()
                fix_ml_files(author_info['id'], current_project)
                if branch:
                    the_branch = branch
                else:
                    the_branch = commit_branch
                output += "Going to use " + the_branch + " as the branch.\n"
                if not is_empty:
                    output += "Doing git config user.email " + json.dumps(github_email) + "\n"
                    try:
                        output += subprocess.check_output(["git", "config", "user.email", json.dumps(github_email)], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git config user.email.  " + output) from err
                    output += "Doing git config user.name " + json.dumps(the_user_name) + "\n"
                    try:
                        output += subprocess.check_output(["git", "config", "user.name", json.dumps(the_user_name)], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git config user.email.  " + output) from err
                    output += "Trying git checkout " + the_branch + "\n"
                    try:
                        output += subprocess.check_output(["git", "checkout", the_branch], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError:
                        output += the_branch + " is a new branch\n"
                        # force_branch_creation = True
                        branch = the_branch
                output += "Doing git checkout -b " + tempbranch + "\n"
                try:
                    output += subprocess.check_output(["git", "checkout", "-b", tempbranch], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                except subprocess.CalledProcessError as err:
                    output += err.output.decode()
                    raise DAError("create_playground_package: error running git checkout.  " + output) from err
                output += "Writing files.\n"
                make_package_dir(pkgname, info, author_info, directory=directory, current_project=current_project)
                try:
                    if files_to_add is None:
                        output += "Doing git add .\n"
                        output += subprocess.check_output(["git", "add", "."], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    else:
                        output += "Doing git add " + (' '.join(files_to_add)) + "\n"
                        output += subprocess.check_output(["git", "add"] + files_to_add, cwd=packagedir, stderr=subprocess.STDOUT).decode()
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git add.  " + output) from err
                output += "Doing git status\n"
                try:
                    output += subprocess.check_output(["git", "status"], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                except subprocess.CalledProcessError as err:
                    output += err.output.decode()
                    raise DAError("create_playground_package: error running git status.  " + output) from err
                output += "Doing git commit -m " + json.dumps(str(commit_message)) + "\n"
                try:
                    output += subprocess.check_output(["git", "commit", "-am", str(commit_message)], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                except subprocess.CalledProcessError as err:
                    output += err.output.decode()
                    raise DAError("create_playground_package: error running git commit.  " + output) from err
                output += "Trying git checkout " + the_branch + "\n"
                try:
                    output += subprocess.check_output(["git", "checkout", the_branch], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                    branch_exists = True
                except subprocess.CalledProcessError:
                    branch_exists = False
                if not branch_exists:
                    output += "Doing git checkout -b " + the_branch + "\n"
                    try:
                        output += subprocess.check_output(["git", "checkout", "-b", the_branch], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git checkout -b " + the_branch + ".  " + output) from err
                else:
                    output += "Doing git merge --squash " + tempbranch + "\n"
                    try:
                        output += subprocess.check_output(["git", "merge", "--squash", tempbranch], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git merge --squash " + tempbranch + ".  " + output) from err
                    output += "Doing git commit\n"
                    try:
                        output += subprocess.check_output(["git", "commit", "-am", str(commit_message)], cwd=packagedir, stderr=subprocess.STDOUT).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git commit -am " + str(commit_message) + ".  " + output) from err
                if branch:
                    output += "Doing " + git_prefix + "git push --set-upstream origin " + str(branch) + "\n"
                    try:
                        output += subprocess.check_output(["git", "push", "--set-upstream", "origin", str(branch)], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git push.  " + output) from err
                else:
                    output += "Doing " + git_prefix + "git push\n"
                    try:
                        output += subprocess.check_output(["git", "push"], cwd=packagedir, stderr=subprocess.STDOUT, env=git_env).decode()
                    except subprocess.CalledProcessError as err:
                        output += err.output.decode()
                        raise DAError("create_playground_package: error running git push.  " + output) from err
                logmessage(output)
                flash(word("Pushed commit to GitHub.") + "<br>" + re.sub(r'[\n\r]+', '<br>', output), 'info')
                time.sleep(3.0)
                shutil.rmtree(directory)
                the_args = {'project': current_project, 'pull': '1', 'github_url': ssh_url, 'show_message': '0'}
                do_pypi_also = true_or_false(request.args.get('pypi_also', False))
                if current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin'):
                    do_install_also = true_or_false(request.args.get('install_also', False))
                else:
                    do_install_also = False
                if do_pypi_also or do_install_also:
                    the_args['file'] = current_package
                    if do_pypi_also:
                        the_args['pypi_also'] = '1'
                    if do_install_also:
                        the_args['install_also'] = '1'
                if branch:
                    the_args['branch'] = branch
                return redirect(url_for('develop.playground_packages', **the_args))
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(None, nice_name, None)
            file_set_attributes(file_number, private=True, persistent=True, session=None, filename=None)
            saved_file = SavedFile(file_number, extension='zip', fix=True, should_not_exist=True)
            if playground_user.timezone:
                the_timezone = playground_user.timezone
            else:
                the_timezone = get_default_timezone()
            fix_ml_files(author_info['id'], current_project)
            zip_file = make_package_zip(pkgname, info, author_info, the_timezone, current_project=current_project)
            saved_file.copy_from(zip_file.name)
            saved_file.finalize()
            if do_install:
                install_zip_package('docassemble.' + pkgname, file_number)
                result = celery_app.signature('tasks.update_packages').apply_async(link=celery_app.signature('tasks.reset_server', kwargs={'run_create': should_run_create('docassemble.' + pkgname)}))
                session['taskwait'] = result.id
                session['serverstarttime'] = START_TIME
                return redirect(url_for('packages.update_package_wait', next=url_for('develop.playground_packages', project=current_project, file=current_package)))
                # return redirect(url_for('develop.playground_packages', file=current_package))
            response = custom_send_file(saved_file.path, mimetype='application/zip', as_attachment=True, download_name=nice_name)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return response
    response = make_response(render_template('develop/create_playground_package.html', current_project=current_project, version_warning=version_warning, bodyclass='daadminbody', form=form, current_package=current_package, package_names=file_list['playgroundpackages'], tab_title=word('Playground Packages'), page_title=word('Playground Packages')), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/createpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_package():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    form = CreatePackageForm(request.form)
    if request.method == 'POST' and form.validate():
        pkgname = re.sub(r'^docassemble-', r'', form.name.data)
        licensetext = """\
The MIT License (MIT)

"""
        licensetext += 'Copyright (c) ' + str(datetime.datetime.now().year) + ' ' + str(name_of_user(current_user)) + """

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        gitignore = daconfig.get('default gitignore', DEFAULT_GITIGNORE)
        readme = '# docassemble.' + str(pkgname) + "\n\nA docassemble extension.\n\n## Author\n\n" + name_of_user(current_user, include_email=True) + "\n"
        pyprojecttoml = tomli_w.dumps({'build-system': {'requires': ['setuptools>=80.9.0'], 'build-backend': 'setuptools.build_meta'}, 'project': {'name': f'docassemble.{pkgname}', 'version': '0.0.1', 'description': 'A docassemble extension.', 'readme': 'README.md', 'authors': [{'name': str(name_of_user(current_user)), 'email': str(current_user.email)}], 'license': 'MIT', 'license-files': ['LICENSE'], 'urls': {'Homepage': 'https://docassemble.org'}}, 'tool': {'setuptools': {'packages': {'find': {'where': ['.']}}}}})
        manifestin = f"""\
include README.md
graft docassemble/{pkgname}/data
recursive-exclude * *.egg-info
recursive-exclude .git *
recursive-exclude venv *
recursive-exclude .github *
recursive-exclude .pytest_cache *
recursive-exclude .vscode *
recursive-exclude build *
recursive-exclude dist *
recursive-exclude * __pycache__
recursive-exclude * *.pyc
recursive-exclude * *.pyo
recursive-exclude * *.orig
recursive-exclude * *~
recursive-exclude * *.bak
recursive-exclude * *.swp
"""
        setupcfg = """\
[metadata]
long_description = file: README.md
"""
        setuppy = """\
import os
import sys
from setuptools import setup, find_namespace_packages
from fnmatch import fnmatchcase
from distutils2.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', os.path.join('.', 'build'), os.path.join('.', 'dist'), 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + os.path.sep, package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

"""
        setuppy += "setup(name='docassemble." + str(pkgname) + "',\n" + """\
      version='0.0.1',
      description=('A docassemble extension.'),
      long_description=""" + repr(readme) + """,
      long_description_content_type='text/markdown',
      author=""" + repr(str(name_of_user(current_user))) + """,
      author_email=""" + repr(str(current_user.email)) + """,
      license='MIT',
      url='https://docassemble.org',
      packages=find_namespace_packages(),
      zip_safe = False,
      package_data=find_package_data(where=os.path.join('docassemble', '""" + str(pkgname) + """', ''), package='docassemble.""" + str(pkgname) + """'),
     )

"""
        questionfiletext = """\
---
metadata:
  title: I am the title of the application
  short title: Mobile title
  description: |
    Insert description of question file here.
  authors:
    - name: """ + str(current_user.first_name) + " " + str(current_user.last_name) + """
      organization: """ + str(current_user.organization) + """
  revision_date: """ + formatted_current_date() + """
---
mandatory: True
code: |
  user_done
---
question: |
  % if user_doing_well:
  Good to hear it!
  % else:
  Sorry to hear that!
  % endif
sets: user_done
buttons:
  - Exit: exit
  - Restart: restart
---
question: Are you doing well today?
yesno: user_doing_well
...
"""
        templatereadme = """\
# Template directory

If you want to use templates for document assembly, put them in this directory.
"""
        staticreadme = """\
# Static file directory

If you want to make files available in the web app, put them in
this directory.
"""
        sourcesreadme = """\
# Sources directory

This directory is used to store word translation files,
machine learning training files, and other sources of data.
"""
        objectfile = """\
# This is a Python module in which you can write your own Python code,
# if you want to.
#
# Include this module in a docassemble interview by writing:
# ---
# modules:
#   - docassemble.""" + pkgname + """.objects
# ---
#
# Then you can do things like:
# ---
# objects:
#   - favorite_fruit: Fruit
# ---
# mandatory: True
# question: |
#   When I eat some ${ favorite_fruit.name },
#   I think, "${ favorite_fruit.eat() }"
# ---
# question: What is the best fruit?
# fields:
#   - Fruit Name: favorite_fruit.name
# ---
from docassemble.base.util import DAObject


class Fruit(DAObject):

    def eat(self):
        return "Yum, that " + self.name + " was good!"
"""
        directory = tempfile.mkdtemp(prefix='SavedFile')
        packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
        questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
        templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
        staticdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'static')
        sourcesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'sources')
        os.makedirs(questionsdir, exist_ok=True)
        os.makedirs(templatesdir, exist_ok=True)
        os.makedirs(staticdir, exist_ok=True)
        os.makedirs(sourcesdir, exist_ok=True)
        with open(os.path.join(packagedir, '.gitignore'), 'w', encoding='utf-8') as the_file:
            the_file.write(gitignore)
        with open(os.path.join(packagedir, 'README.md'), 'w', encoding='utf-8') as the_file:
            the_file.write(readme)
        with open(os.path.join(packagedir, 'LICENSE'), 'w', encoding='utf-8') as the_file:
            the_file.write(licensetext)
        with open(os.path.join(packagedir, 'setup.py'), 'w', encoding='utf-8') as the_file:
            the_file.write(setuppy)
        with open(os.path.join(packagedir, 'setup.cfg'), 'w', encoding='utf-8') as the_file:
            the_file.write(setupcfg)
        with open(os.path.join(packagedir, 'MANIFEST.in'), 'w', encoding='utf-8') as the_file:
            the_file.write(manifestin)
        with open(os.path.join(packagedir, 'pyproject.toml'), 'w', encoding='utf-8') as the_file:
            the_file.write(pyprojecttoml)
        with open(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), 'w', encoding='utf-8') as the_file:
            the_file.write('__version__ = "0.0.1"')
        with open(os.path.join(packagedir, 'docassemble', pkgname, 'objects.py'), 'w', encoding='utf-8') as the_file:
            the_file.write(objectfile)
        with open(os.path.join(templatesdir, 'README.md'), 'w', encoding='utf-8') as the_file:
            the_file.write(templatereadme)
        with open(os.path.join(staticdir, 'README.md'), 'w', encoding='utf-8') as the_file:
            the_file.write(staticreadme)
        with open(os.path.join(sourcesdir, 'README.md'), 'w', encoding='utf-8') as the_file:
            the_file.write(sourcesreadme)
        with open(os.path.join(questionsdir, 'questions.yml'), 'w', encoding='utf-8') as the_file:
            the_file.write(questionfiletext)
        nice_name = 'docassemble-' + str(pkgname) + '.zip'
        file_number = get_new_file_number(None, nice_name, None)
        file_set_attributes(file_number, private=True, persistent=True, session=None, filename=None)
        saved_file = SavedFile(file_number, extension='zip', fix=True, should_not_exist=True)
        zf = zipfile.ZipFile(saved_file.path, compression=zipfile.ZIP_DEFLATED, mode='w')
        trimlength = len(directory) + 1
        if current_user.timezone:
            the_timezone = zoneinfo.ZoneInfo(current_user.timezone)
        else:
            the_timezone = zoneinfo.ZoneInfo(get_default_timezone())
        for root, dirs, files in os.walk(packagedir):  # pylint: disable=unused-variable
            for the_file in files:
                thefilename = os.path.join(root, the_file)
                info = zipfile.ZipInfo(thefilename[trimlength:])
                info.date_time = datetime.datetime.fromtimestamp(os.path.getmtime(thefilename), datetime.timezone.utc).astimezone(the_timezone).timetuple()
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                with open(thefilename, 'rb') as fp:
                    zf.writestr(info, fp.read())
                # zf.write(thefilename, thefilename[trimlength:])
        zf.close()
        saved_file.save()
        saved_file.finalize()
        shutil.rmtree(directory)
        response = custom_send_file(saved_file.path, mimetype='application/zip', as_attachment=True, download_name=nice_name)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        flash(word("Package created"), 'success')
        return response
    response = make_response(render_template('develop/create_package.html', version_warning=version_warning, bodyclass='daadminbody', form=form, tab_title=word('Create Package'), page_title=word('Create Package')), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@develop_bp.route('/playgroundbundle.js', methods=['GET'])
def playground_js_bundle():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = ''
    for parts in [['areyousure', 'jquery.are-you-sure.js'], ['bootstrap-fileinput', 'js', 'plugins', 'buffer.js'], ['bootstrap-fileinput', 'js', 'plugins', 'filetype.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.js'], ['bootstrap-fileinput', 'js', 'plugins', 'sortable.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['app', 'cm6.js'], ['app', 'playground.js']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    return Response(output, mimetype='application/javascript')


@develop_bp.route('/reqdev', methods=['GET', 'POST'])
@login_required
def request_developer():
    setup_translation()
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    form = RequestDeveloperForm(request.form)
    recipients = []
    if request.method == 'POST':
        for user in db.session.execute(select(UserModel.id, UserModel.email).join(UserRoles, UserModel.id == UserRoles.user_id).join(Role, UserRoles.role_id == Role.id).where(and_(UserModel.active == True, Role.name == 'admin'))):  # noqa: E712 # pylint: disable=singleton-comparison
            if user.email not in recipients:
                recipients.append(user.email)
        body = "User " + str(current_user.email) + " (" + str(current_user.id) + ") has requested developer privileges.\n\n"
        if form.reason.data:
            body += "Reason given: " + str(form.reason.data) + "\n\n"
        body += "Go to " + url_for('users.edit_user_profile_page', user_id=current_user.id, _external=True) + " to change the user's privileges."
        msg = Message("Request for developer account from " + str(current_user.email), recipients=recipients, body=body)
        if len(recipients) == 0:
            flash(word('No administrators could be found.'), 'error')
        else:
            try:
                da_send_mail(msg, None)
                flash(word('Your request was submitted.'), 'success')
            except:
                flash(word('We were unable to submit your request.'), 'error')
        return redirect(url_for('user.profile'))
    return render_template('users/request_developer.html', version_warning=None, bodyclass='daadminbody', tab_title=word("Developer Access"), page_title=word("Developer Access"), form=form)


@develop_bp.route('/utilities', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def utilities():
    setup_translation()
    form = Utilities(request.form)
    fields_output = None
    word_box = None
    uses_null = False
    file_type = None
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('utilities')))
    if request.method == 'POST':
        if 'language' in request.form:
            language = request.form['language']
            result = {}
            result[language] = {}
            existing = word_collection.get(language, {})
            if 'api key' in daconfig['google'] and daconfig['google']['api key']:
                import googleapiclient.discovery  # pylint: disable=import-outside-toplevel
                try:
                    service = googleapiclient.discovery.build('translate', 'v2',
                                                              developerKey=daconfig['google']['api key'])
                    use_google_translate = True
                except:
                    logmessage("utilities: attempt to call Google Translate failed")
                    use_google_translate = False
            else:
                use_google_translate = False
                service = None
            words_to_translate = []
            for the_word in base_words:
                if the_word in existing and existing[the_word] is not None:
                    result[language][the_word] = existing[the_word]
                    continue
                words_to_translate.append(the_word)
            if language == 'en':
                for the_word in words_to_translate:
                    if not bool(result[language].get(the_word)):
                        result[language][the_word] = the_word
            else:
                chunk_limit = daconfig.get('google translate words at a time', 20)
                chunks = []
                interim_list = []
                while len(words_to_translate) > 0:
                    the_word = words_to_translate.pop(0)
                    interim_list.append(the_word)
                    if len(interim_list) >= chunk_limit:
                        chunks.append(interim_list)
                        interim_list = []
                if len(interim_list) > 0:
                    chunks.append(interim_list)
                for chunk in chunks:
                    if use_google_translate:
                        try:
                            resp = service.translations().list(  # pylint: disable=no-member
                                source='en',
                                target=language,
                                q=chunk
                            ).execute()
                        except BaseException as errstr:
                            logmessage("utilities: translation failed: " + str(errstr))
                            resp = None
                        if isinstance(resp, dict) and 'translations' in resp and isinstance(resp['translations'], list) and len(resp['translations']) == len(chunk):
                            for the_index, the_chunk in enumerate(chunk):
                                if isinstance(resp['translations'][the_index], dict) and 'translatedText' in resp['translations'][the_index]:
                                    result[language][the_chunk] = re.sub(r'&#39;', r"'", str(resp['translations'][the_index]['translatedText']))
                                else:
                                    result[language][the_chunk] = 'XYZNULLXYZ'
                                    uses_null = True
                        else:
                            for the_word in chunk:
                                result[language][the_word] = 'XYZNULLXYZ'
                            uses_null = True
                    else:
                        for the_word in chunk:
                            result[language][the_word] = 'XYZNULLXYZ'
                        uses_null = True
            if form.systemfiletype.data == 'YAML':
                word_box = altyamlstring.dump_to_string(result)
                word_box = re.sub(r'"XYZNULLXYZ"', r'null', word_box)
            elif form.systemfiletype.data == 'XLSX':
                temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
                xlsx_filename = language + "-words.xlsx"
                workbook = xlsxwriter.Workbook(temp_file.name)
                worksheet = workbook.add_worksheet()
                bold = workbook.add_format({'bold': 1, 'num_format': '@'})
                text = workbook.add_format({'num_format': '@'})
                text.set_align('top')
                wrapping = workbook.add_format({'num_format': '@'})
                wrapping.set_align('top')
                wrapping.set_text_wrap()
                # wrapping.set_locked(False)
                numb = workbook.add_format()
                numb.set_align('top')
                worksheet.write('A1', 'orig_lang', bold)
                worksheet.write('B1', 'tr_lang', bold)
                worksheet.write('C1', 'orig_text', bold)
                worksheet.write('D1', 'tr_text', bold)
                worksheet.set_column(0, 0, 10)
                worksheet.set_column(1, 1, 10)
                worksheet.set_column(2, 2, 55)
                worksheet.set_column(3, 3, 55)
                row = 1
                for key, val in result[language].items():
                    worksheet.write_string(row, 0, 'en', text)
                    worksheet.write_string(row, 1, language, text)
                    worksheet.write_string(row, 2, key, wrapping)
                    worksheet.write_string(row, 3, val, wrapping)
                    row += 1
                workbook.close()
                response = custom_send_file(temp_file.name, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=xlsx_filename)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return response
            elif form.systemfiletype.data == 'XLIFF 1.2':
                temp_file = tempfile.NamedTemporaryFile(suffix='.xlf', delete=False)
                xliff_filename = language + "-words.xlf"
                xliff = ET.Element('xliff')
                xliff.set('xmlns', 'urn:oasis:names:tc:xliff:document:1.2')
                xliff.set('version', '1.2')
                the_file = ET.SubElement(xliff, 'file')
                the_file.set('source-language', 'en')
                the_file.set('target-language', language)
                the_file.set('datatype', 'plaintext')
                the_file.set('original', 'self')
                the_file.set('id', 'f1')
                the_file.set('xml:space', 'preserve')
                body = ET.SubElement(the_file, 'body')
                indexno = 1
                for key, val in result[language].items():
                    trans_unit = ET.SubElement(body, 'trans-unit')
                    trans_unit.set('id', str(indexno))
                    trans_unit.set('xml:space', 'preserve')
                    source = ET.SubElement(trans_unit, 'source')
                    source.set('xml:space', 'preserve')
                    target = ET.SubElement(trans_unit, 'target')
                    target.set('xml:space', 'preserve')
                    source.text = key
                    target.text = val
                    indexno += 1
                temp_file.write(ET.tostring(xliff))
                temp_file.close()
                response = custom_send_file(temp_file.name, mimetype='application/xml', as_attachment=True, download_name=xliff_filename)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return response
            elif form.systemfiletype.data == 'XLIFF 2.0':
                temp_file = tempfile.NamedTemporaryFile(suffix='.xlf', delete=False)
                xliff_filename = language + "-words.xlf"
                xliff = ET.Element('xliff')
                xliff.set('xmlns', 'urn:oasis:names:tc:xliff:document:2.0')
                xliff.set('version', '2.0')
                xliff.set('srcLang', 'en')
                xliff.set('trgLang', language)
                the_file = ET.SubElement(xliff, 'file')
                the_file.set('id', 'f1')
                the_file.set('original', 'self')
                the_file.set('xml:space', 'preserve')
                unit = ET.SubElement(the_file, 'unit')
                unit.set('id', "docassemble_phrases")
                indexno = 1
                for key, val in result[language].items():
                    segment = ET.SubElement(unit, 'segment')
                    segment.set('id', str(indexno))
                    segment.set('xml:space', 'preserve')
                    source = ET.SubElement(segment, 'source')
                    source.set('xml:space', 'preserve')
                    target = ET.SubElement(segment, 'target')
                    target.set('xml:space', 'preserve')
                    source.text = key
                    target.text = val
                    indexno += 1
                temp_file.write(ET.tostring(xliff))
                temp_file.close()
                response = custom_send_file(temp_file.name, mimetype='application/xml', as_attachment=True, download_name=xliff_filename)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return response
        if 'pdfdocxfile' in request.files and request.files['pdfdocxfile'].filename:
            filename = secure_filename(request.files['pdfdocxfile'].filename)
            extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
            if mimetype == 'application/pdf':
                file_type = 'pdf'
                pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=True)
                the_file = request.files['pdfdocxfile']
                the_file.save(pdf_file.name)
                try:
                    fields_output = read_fields(pdf_file.name, the_file.filename, 'pdf', 'yaml')
                except BaseException as err:
                    fields_output = str(err)
                pdf_file.close()
            elif mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                file_type = 'docx'
                docx_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".docx", delete=True)
                the_file = request.files['pdfdocxfile']
                the_file.save(docx_file.name)
                try:
                    fields_output = read_fields(docx_file.name, the_file.filename, 'docx', 'yaml')
                except BaseException as err:
                    fields_output = str(err)
                docx_file.close()
        if form.officeaddin_submit.data:
            resp = make_response(render_template('develop/officemanifest.xml', office_app_version=form.officeaddin_version.data, guid=str(uuid.uuid4())))
            resp.headers['Content-type'] = 'text/xml; charset=utf-8'
            resp.headers['Content-Disposition'] = 'attachment; filename="manifest.xml"'
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return resp
    form.systemfiletype.choices = [('YAML', 'YAML'), ('XLSX', 'XLSX'), ('XLIFF 1.2', 'XLIFF 1.2'), ('XLIFF 2.0', 'XLIFF 2.0')]
    form.systemfiletype.data = 'YAML'
    form.filetype.choices = [('XLSX', 'XLSX'), ('XLIFF 1.2', 'XLIFF 1.2'), ('XLIFF 2.0', 'XLIFF 2.0')]
    form.filetype.data = 'XLSX'
    response = make_response(render_template('develop/utilities.html', version_warning=version_warning, bodyclass='daadminbody', tab_title=word("Utilities"), page_title=word("Utilities"), form=form, fields=fields_output, word_box=word_box, uses_null=uses_null, file_type=file_type, interview_placeholder=word("E.g., docassemble.demo:data/questions/questions.yml"), language_placeholder=word("E.g., es, fr, it")), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response
