# from twilio.util import TwilioCapability
import socket
import copy
import threading
import urllib
import urllib2
import os
import tailer
import sys
import datetime
from dateutil import tz
import time
import pip.utils.logging
import pip
import shutil
import codecs
import weakref
import types
import pkg_resources
import docassemble.base.parse
import docassemble.base.pdftk
import docassemble.base.interview_cache
import docassemble.webapp.update
from docassemble.base.standardformatter import as_html, signature_html
import xml.etree.ElementTree as ET
import docassemble.webapp.database
import tempfile
import zipfile
import traceback
from docassemble.base.pandoc import word_to_markdown, convertible_mimetypes, convertible_extensions
from docassemble.webapp.screenreader import to_text
from docassemble.base.error import DAError, DAErrorNoEndpoint, DAErrorMissingVariable
from docassemble.base.util import pickleable_objects, word, comma_and_list
from docassemble.base.logger import logmessage
from Crypto.Cipher import AES
from Crypto.Hash import MD5
import mimetypes
import logging
import pickle
import string
import random
import cgi
import Cookie
import re
import urlparse
import json
import base64
import requests
from flask import make_response, abort, render_template, request, session, send_file, redirect, url_for, current_app, get_flashed_messages, flash, Markup, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_user import login_required, roles_required, UserManager, SQLAlchemyAdapter
from flask_user.forms import LoginForm
from flask_user import signals, user_logged_in, user_changed_password, user_registered, user_registered, user_reset_password
from docassemble.webapp.develop import CreatePackageForm, CreatePlaygroundPackageForm, UpdatePackageForm, ConfigForm, PlaygroundForm, LogForm, Utilities, PlaygroundFilesForm, PlaygroundFilesEditForm, PlaygroundPackagesForm
from flask_mail import Mail, Message
import flask_user.signals
import httplib2
from werkzeug import secure_filename, FileStorage
from rauth import OAuth1Service, OAuth2Service
from flask_kvsession import KVSessionExtension
from simplekv.db.sql import SQLAlchemyStore
from sqlalchemy import create_engine, MetaData, Sequence, or_, and_
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.core.models import Attachments, Uploads, SpeakList, Messages, Supervisors
from docassemble.webapp.users.models import UserAuth, User, Role, UserDict, UserDictKeys, UserRoles, UserDictLock
from docassemble.webapp.packages.models import Package, PackageAuth, Install
from docassemble.webapp.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED, dbtableprefix, hostname
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype, make_package_zip
from PIL import Image
import pyPdf
import yaml
import inspect
from subprocess import call, Popen, PIPE
DEBUG = daconfig.get('debug', False)
docassemble.base.parse.debug = DEBUG
import docassemble.base.util
docassemble.base.util.set_debug_status(DEBUG)
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter

default_playground_yaml = """metadata:
  title: Default playground interview
  short title: Test
  comment: This is a learning tool.  Feel free to write over it.
---
include:
  - basic-questions.yml
---
mandatory: true
code: |
  need(all_done)
---
sets: all_done
question: |
  Here is your document, ${ client }.
subquestion: |
  In order ${ quest }, you will need this.
attachments:
  - name: Information Sheet
    filename: info_sheet
    content: |
      Your name is ${ client }.
      
      % if user.age_in_years() > 60:
      You are a senior.
      % endif
      Your quest is ${ quest }.  You
      are eligible for ${ benefits }.
---
question: |
  What is your quest?
fields:
  - Your quest: quest
    hint: to find the Loch Ness Monster
---
code: |
  if user.age_in_years() < 18:
    benefits = "CHIP"
  else:
    benefits = "Medicaid"
"""

app.debug = False

ok_mimetypes = {"application/javascript": "javascript", "text/x-python": "python"}
ok_extensions = {"yml": "yaml", "yaml": "yaml", "md": "markdown", "markdown": "markdown", 'py': "python"}
default_yaml_filename = daconfig.get('default_interview', 'docassemble.demo:data/questions/questions.yml')

document_match = re.compile(r'^--- *$', flags=re.MULTILINE)
fix_tabs = re.compile(r'\t')
fix_initial = re.compile(r'^---\n')
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
extraneous_var = re.compile(r'^x\.|^x\[')

if 'mail' not in daconfig:
    daconfig['mail'] = dict()
default_title = daconfig.get('default_title', daconfig.get('brandname', 'docassemble'))
default_short_title = daconfig.get('default_short_title', default_title)
os.environ['PYTHON_EGG_CACHE'] = tempfile.mkdtemp()
app.config['APP_NAME'] = daconfig.get('appname', 'docassemble')
app.config['BRAND_NAME'] = daconfig.get('brandname', daconfig.get('appname', 'docassemble'))
app.config['MAIL_USERNAME'] = daconfig['mail'].get('username', None)
app.config['MAIL_PASSWORD'] = daconfig['mail'].get('password', None)
app.config['MAIL_DEFAULT_SENDER'] = daconfig['mail'].get('default_sender', None)
app.config['MAIL_SERVER'] = daconfig['mail'].get('server', 'localhost')
app.config['MAIL_PORT'] = daconfig['mail'].get('port', 25)
app.config['MAIL_USE_SSL'] = daconfig['mail'].get('use_ssl', False)
app.config['MAIL_USE_TLS'] = daconfig['mail'].get('use_tls', True)
#app.config['ADMINS'] = [daconfig.get('admin_address', None)]
app.config['APP_SYSTEM_ERROR_SUBJECT_LINE'] = app.config['APP_NAME'] + " system error"
app.config['APPLICATION_ROOT'] = daconfig.get('root', '/')
app.config['CSRF_ENABLED'] = False
app.config['USER_APP_NAME'] = app.config['APP_NAME']
app.config['USER_SEND_PASSWORD_CHANGED_EMAIL'] = False
app.config['USER_SEND_REGISTERED_EMAIL'] = False
app.config['USER_SEND_USERNAME_CHANGED_EMAIL'] = False
app.config['USER_ENABLE_EMAIL'] = True
app.config['USER_ENABLE_USERNAME'] = False
app.config['USER_ENABLE_REGISTRATION'] = True
app.config['USER_ENABLE_CHANGE_USERNAME'] = False
app.config['USER_ENABLE_CONFIRM_EMAIL'] = False
app.config['USER_AUTO_LOGIN_AFTER_REGISTER'] = True
app.config['USER_AUTO_LOGIN_AFTER_RESET_PASSWORD'] = False
app.config['USER_AFTER_FORGOT_PASSWORD_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_CHANGE_PASSWORD_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_CHANGE_USERNAME_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_CONFIRM_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_FORGOT_PASSWORD_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_LOGIN_ENDPOINT'] = 'interview_list'
app.config['USER_AFTER_LOGOUT_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'interview_list'
app.config['USER_AFTER_RESEND_CONFIRM_EMAIL_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_RESET_PASSWORD_ENDPOINT'] = 'user.login' 
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['USE_X_SENDFILE'] = daconfig.get('xsendfile', True)
PNG_RESOLUTION = daconfig.get('png_resolution', 300)
PNG_SCREEN_RESOLUTION = daconfig.get('png_screen_resolution', 72)
PDFTOPPM_COMMAND = daconfig.get('pdftoppm', 'pdftoppm')
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
LOGSERVER = daconfig.get('log server', None)
docassemble.base.util.set_default_language(DEFAULT_LANGUAGE)
docassemble.base.util.set_default_locale(DEFAULT_LOCALE)
docassemble.base.util.set_default_dialect(DEFAULT_DIALECT)
docassemble.base.util.set_language(DEFAULT_LANGUAGE, dialect=DEFAULT_DIALECT)
docassemble.base.util.set_locale(DEFAULT_LOCALE)
docassemble.base.util.set_da_config(daconfig)
docassemble.base.util.update_locale()
message_sequence = dbtableprefix + 'message_id_seq'

audio_mimetype_table = {'mp3': 'audio/mpeg', 'ogg': 'audio/ogg'}

valid_voicerss_languages = {
    'ca': ['es'],
    'zh': ['cn', 'hk', 'tw'],
    'da': ['dk'],
    'nl': ['nl'],
    'en': ['au', 'ca', 'gb', 'in', 'us'],
    'fi': ['fi'],
    'fr': ['ca, fr'],
    'de': ['de'],
    'it': ['it'],
    'ja': ['jp'],
    'ko': ['kr'],
    'nb': ['no'],
    'pl': ['pl'],
    'pt': ['br', 'pt'],
    'ru': ['ru'],
    'es': ['mx', 'es'],
    'sv': ['se']
    }

voicerss_config = daconfig.get('voicerss', None)
if not voicerss_config or ('enable' in voicerss_config and not voicerss_config['enable']) or not ('key' in voicerss_config and voicerss_config['key']):
    VOICERSS_ENABLED = False
else:
    VOICERSS_ENABLED = True
ROOT = daconfig.get('root', '/')
if 'currency symbol' in daconfig:
    docassemble.base.util.update_language_function('*', 'currency_symbol', lambda: daconfig['currency symbol'])
#app.logger.warning("default sender is " + app.config['MAIL_DEFAULT_SENDER'] + "\n")
exit_page = daconfig.get('exitpage', '/')

if S3_ENABLED:
    import docassemble.webapp.amazon
    s3 = docassemble.webapp.amazon.s3object(s3_config)

SUPERVISORCTL = daconfig.get('supervisorctl', 'supervisorctl')
PACKAGE_CACHE = daconfig.get('packagecache', '/var/www/.cache')
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local')
UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')
FULL_PACKAGE_DIRECTORY = os.path.join(PACKAGE_DIRECTORY, 'lib', 'python2.7', 'site-packages')
LOG_DIRECTORY = daconfig.get('log', '/usr/share/docassemble/log')
#PLAYGROUND_MODULES_DIRECTORY = daconfig.get('playground_modules', )

for path in [FULL_PACKAGE_DIRECTORY, PACKAGE_CACHE, UPLOAD_DIRECTORY, LOG_DIRECTORY]: #, os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble')
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            print "Could not create path: " + path
            sys.exit(1)
    if not os.access(path, os.W_OK):
        print "Unable to create files in directory: " + path
        sys.exit(1)
if not os.access(WEBAPP_PATH, os.W_OK):
    print "Unable to modify the timestamp of the WSGI file: " + WEBAPP_PATH
    sys.exit(1)

init_py_file = """try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)
"""
    
#if not os.path.isfile(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py')):
#    with open(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py'), 'a') as the_file:
#        the_file.write(init_py_file)

#USE_PROGRESS_BAR = daconfig.get('use_progress_bar', True)
SHOW_LOGIN = daconfig.get('show_login', True)
#USER_PACKAGES = daconfig.get('user_packages', '/var/lib/docassemble/dist-packages')
#sys.path.append(USER_PACKAGES)
#if USE_PROGRESS_BAR:
initial_dict = dict(_internal=dict(progress=0, tracker=0, steps_offset=0, secret=None, answered=set(), answers=dict(), objselections=dict(), starttime=None, modtime=None), url_args=dict())
#else:
#    initial_dict = dict(_internal=dict(tracker=0, steps_offset=0, answered=set(), answers=dict(), objselections=dict()), url_args=dict())
if 'initial_dict' in daconfig:
    initial_dict.update(daconfig['initial_dict'])
docassemble.base.parse.set_initial_dict(initial_dict)
LOGFILE = daconfig.get('flask_log', '/tmp/flask.log')
#APACHE_LOGFILE = daconfig.get('apache_log', '/var/log/apache2/error.log')

connect_string = docassemble.webapp.database.connection_string()
alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()

mail = Mail(app)

def my_default_url(error, endpoint, values):
    return url_for('index')

app.handle_url_build_error = my_default_url

engine = create_engine(alchemy_connect_string, convert_unicode=True)
metadata = MetaData(bind=engine)
store = SQLAlchemyStore(engine, metadata, 'kvstore')

kv_session = KVSessionExtension(store, app)

error_file_handler = logging.FileHandler(filename=LOGFILE)
error_file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(error_file_handler)

#sys.stderr.write("__name__ is " + str(__name__) + " and __package__ is " + str(__package__) + "\n")

def flask_logger(message):
    #app.logger.warning(message)
    sys.stderr.write(unicode(message) + "\n")
    return

def get_url_from_file_reference(file_reference, **kwargs):
    file_reference = str(file_reference)
    if re.search(r'^http', file_reference):
        return(file_reference)
    if file_reference in ['login', 'signin']:
        return(url_for('user.login', **kwargs))
    elif file_reference == 'interviews':
        return(url_for('interview_list', **kwargs))
    elif file_reference == 'playground':
        return(url_for('playground_page', **kwargs))
    elif file_reference == 'playgroundtemplate':
        return(url_for('playground_files', section='template'))
    elif file_reference == 'playgroundstatic':
        return(url_for('playground_files', section='static'))
    elif file_reference == 'playgroundmodules':
        return(url_for('playground_files', section='modules'))
    elif file_reference == 'playgroundstatic':
        return(url_for('playground_packages', **kwargs))
    elif file_reference == 'playgroundfiles':
        return(url_for('playground_files', **kwargs))
    elif file_reference == 'create_playground_package':
        return(url_for('create_playground_package', **kwargs))
    if re.match('[0-9]+', file_reference):
        file_number = file_reference
        if can_access_file_number(file_number):
            the_file = SavedFile(file_number)
            url = the_file.url_for(**kwargs)
        else:
            url = 'about:blank'
    else:
        question = kwargs.get('question', None)
        root = daconfig.get('root', '/')
        fileroot = daconfig.get('fileserver', root)
        if 'ext' in kwargs:
            extn = kwargs['ext']
            extn = re.sub(r'^\.', '', extn)
            extn = '.' + extn
        else:
            extn = ''
        parts = file_reference.split(':')
        if len(parts) < 2:
            file_reference = re.sub(r'^data/static/', '', file_reference)
            the_package = None
            if question is not None:
                the_package = question.from_source.package
            if the_package is None:
                the_package = 'docassemble.base'
            parts = [the_package, file_reference]
            #the_file = None
            #try:
            #the_file = pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1])
            #except:
            #    if current_user.is_authenticated and not current_user.is_anonymous:
            #        return(fileroot + "playgroundstatic/" + file_reference)
            #if not os.path.isfile(the_file) and current_user.is_authenticated and not current_user.is_anonymous:
            #    return(fileroot + "playgroundstatic/" + file_reference)
        parts[1] = re.sub(r'^data/static/', '', parts[1])
        url = fileroot + 'packagestatic/' + parts[0] + '/' + parts[1] + extn
    return(url)

docassemble.base.parse.set_url_finder(get_url_from_file_reference)

def absolute_filename(the_file):
    match = re.match(r'^docassemble.playground([0-9]+):(.*)', the_file)
    #logmessage("absolute_filename call: " + the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', match.group(2))
        #logmessage("absolute_filename: filename is " + filename)
        playground = SavedFile(match.group(1), section='playground', fix=True, filename=filename)
        return playground
    match = re.match(r'^/playgroundtemplate/([0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', match.group(2))
        playground = SavedFile(match.group(1), section='playgroundtemplate', fix=True, filename=filename)
        return playground
    match = re.match(r'^/playgroundstatic/([0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', match.group(2))
        playground = SavedFile(match.group(1), section='playgroundstatic', fix=True, filename=filename)
        return playground
    return(None)

# def absolute_validator(the_file):
#     #logmessage("Running my validator")
#     if the_file.startswith(os.path.join(UPLOAD_DIRECTORY, 'playground')) and current_user.is_authenticated and not current_user.is_anonymous and current_user.has_role('admin', 'developer') and os.path.dirname(the_file) == os.path.join(UPLOAD_DIRECTORY, 'playground', str(current_user.id)):
#         return True
#     return False

docassemble.base.parse.set_absolute_filename(absolute_filename)
#logmessage("Server started")

def can_access_file_number(file_number):
    upload = Uploads.query.filter_by(indexno=file_number, key=session['uid']).first()
    if upload:
        return True
    return False

def get_info_from_file_number(file_number):
    result = dict()
    upload = Uploads.query.filter_by(indexno=file_number, key=session['uid']).first()
    if upload:
        result['filename'] = upload.filename
        result['extension'], result['mimetype'] = get_ext_and_mimetype(result['filename'])
        result['savedfile'] = SavedFile(file_number, extension=result['extension'], fix=True)
        result['path'] = result['savedfile'].path
        result['fullpath'] = result['path'] + '.' + result['extension']
    # cur = conn.cursor()
    # cur.execute("SELECT filename FROM uploads where indexno=%s and key=%s", [file_number, session['uid']])
    # for d in cur:
    #     result['path'] = get_path_from_file_number(file_number)
    #     result['filename'] = d[0]
    #     result['extension'], result['mimetype'] = get_ext_and_mimetype(result['filename'])
    #     result['fullpath'] = result['path'] + '.' + result['extension']
    #     break
    # conn.commit()
    if 'path' not in result:
        logmessage("path is not in result for " + str(file_number))
        return result
    filename = result['path'] + '.' + result['extension']
    if os.path.isfile(filename):
        add_info_about_file(filename, result)
    else:
        logmessage("Filename DID NOT EXIST.")
    return(result)

def add_info_about_file(filename, result):
    if result['extension'] == 'pdf':
        reader = pyPdf.PdfFileReader(open(filename))
        result['pages'] = reader.getNumPages()
    elif result['extension'] in ['png', 'jpg', 'gif']:
        im = Image.open(filename)
        result['width'], result['height'] = im.size
    elif result['extension'] == 'svg':
        tree = ET.parse(filename)
        root = tree.getroot()
        viewBox = root.attrib.get('viewBox', None)
        if viewBox is not None:
            dimen = viewBox.split(' ')
            if len(dimen) == 4:
                result['width'] = float(dimen[2]) - float(dimen[0])
                result['height'] = float(dimen[3]) - float(dimen[1])
    return

def get_info_from_file_reference(file_reference, **kwargs):
    #sys.stderr.write('file reference is ' + str(file_reference) + "\n")
    #logmessage('file reference is ' + str(file_reference))
    if 'convert' in kwargs:
        convert = kwargs['convert']
    else:
        convert = None
    if re.match('[0-9]+', str(file_reference)):
        result = get_info_from_file_number(int(file_reference))
    else:
        result = dict()
        question = kwargs.get('question', None)
        the_package = None
        parts = file_reference.split(':')
        if len(parts) == 1:
            the_package = None
            if question is not None:
                the_package = question.from_source.package
            if the_package is not None:
                file_reference = the_package + ':' + file_reference
            else:
                file_reference = 'docassemble.base:' + file_reference
        result['fullpath'] = docassemble.base.util.static_filename_path(file_reference)
    #logmessage("path is " + str(result['fullpath']))
    if result['fullpath'] is not None and os.path.isfile(result['fullpath']):
        result['filename'] = os.path.basename(result['fullpath'])
        ext_type, result['mimetype'] = get_ext_and_mimetype(result['fullpath'])
        path_parts = os.path.splitext(result['fullpath'])
        result['path'] = path_parts[0]
        result['extension'] = path_parts[1].lower()
        result['extension'] = re.sub(r'\.', '', result['extension'])
        #logmessage("Extension is " + result['extension'])
        if convert is not None and result['extension'] in convert:
            #logmessage("Converting...")
            if os.path.isfile(result['path'] + '.' + convert[result['extension']]):
                #logmessage("Found conversion file ")
                result['extension'] = convert[result['extension']]
                result['fullpath'] = result['path'] + '.' + result['extension']
                ext_type, result['mimetype'] = get_ext_and_mimetype(result['fullpath'])
            else:
                logmessage("Did not find file " + result['path'] + '.' + convert[result['extension']])
                return dict()
        #logmessage("Full path is " + result['fullpath'])
        if os.path.isfile(result['fullpath']):
            add_info_about_file(result['fullpath'], result)
    else:
        logmessage("File reference " + str(file_reference) + " DID NOT EXIST.")
    return(result)

#sys.stderr.write("server.py: setting file_finder" + "\n")
docassemble.base.parse.set_file_finder(get_info_from_file_reference)

def get_documentation_dict():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/documentation.yml')
    if 'fullpath' in documentation:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(yaml.load(content))
    return(None)

def get_name_info():
    docstring = get_info_from_file_reference('docassemble.base:data/questions/docstring.yml')
    if 'fullpath' in docstring:
        with open(docstring['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(yaml.load(content))
    return(None)

def get_title_documentation():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/title_documentation.yml')
    if 'fullpath' in documentation:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(yaml.load(content))
    return(None)

title_documentation = get_title_documentation()
documentation_dict = get_documentation_dict()
base_name_info = get_name_info()
for val in base_name_info:
    base_name_info[val]['name'] = val
    base_name_info[val]['insert'] = val
    if 'show' not in base_name_info[val]:
        base_name_info[val]['show'] = False

def get_mail_variable(*args, **kwargs):
    return mail

def save_numbered_file(filename, orig_path, yaml_file_name=None):
    file_number = get_new_file_number(session['uid'], filename, yaml_file_name=yaml_file_name)
    extension, mimetype = get_ext_and_mimetype(filename)
    new_file = SavedFile(file_number, extension=extension, fix=True)
    new_file.copy_from(orig_path)
    new_file.save(finalize=True)
    return(file_number, extension, mimetype)

def async_mail(the_message):
    mail.send(the_message)

docassemble.base.parse.set_mail_variable(get_mail_variable)
docassemble.base.parse.set_async_mail(async_mail)
docassemble.base.parse.set_save_numbered_file(save_numbered_file)

key_requires_preassembly = re.compile('^(x\.|x\[|_multiple_choice)')
match_invalid = re.compile('[^A-Za-z0-9_\[\].\'\%\-=]')
match_invalid_key = re.compile('[^A-Za-z0-9_\[\].\'\%\- =]')
match_brackets = re.compile('\[\'.*\'\]$')
match_inside_and_outside_brackets = re.compile('(.*)(\[\'[^\]]+\'\])$')
match_inside_brackets = re.compile('\[\'([^\]]+)\'\]')

APPLICATION_NAME = 'docassemble'
app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
app.config['USE_GOOGLE_LOGIN'] = False
app.config['USE_FACEBOOK_LOGIN'] = False
if 'oauth' in daconfig:
    app.config['OAUTH_CREDENTIALS'] = daconfig['oauth']
    if 'google' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['google'] and daconfig['oauth']['google']['enable'] is False):
        app.config['USE_GOOGLE_LOGIN'] = True
    if 'facebook' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['facebook'] and daconfig['oauth']['facebook']['enable'] is False):
        app.config['USE_FACEBOOK_LOGIN'] = True

app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
password_secret_key = daconfig.get('password_secretkey', app.secret_key)
#app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                         for x in xrange(32))

word_file_list = daconfig.get('words', list())
if type(word_file_list) is not list:
    word_file_list = [word_file_list]
for word_file in word_file_list:
    logmessage("Reading from " + str(word_file))
    file_info = get_info_from_file_reference(word_file)
    if 'fullpath' in file_info:
        with open(file_info['fullpath'], 'rU') as stream:
            for document in yaml.load_all(stream):
                if document and type(document) is dict:
                    for lang, words in document.iteritems():
                        if type(words) is dict:
                            docassemble.base.util.update_word_collection(lang, words)
                        else:
                            logmessage("Error reading " + str(word_file) + ": words not in dictionary form.")
                else:
                    logmessage("Error reading " + str(word_file) + ": yaml file not in dictionary form.")
    else:
        logmessage("Error reading " + str(word_file) + ": yaml file not found.")
        
def logout():
    secret = request.cookies.get('secret', None)
    if secret is None:
        secret = ''.join(random.choice(string.ascii_letters) for i in range(16))
        set_cookie = True
    else:
        set_cookie = False
    user_manager = current_app.user_manager
    flask_user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
    logout_user()
    delete_session()
    flash(word('You have signed out successfully.'), 'success')
    next = request.args.get('next', _endpoint_url(user_manager.after_logout_endpoint))
    response = redirect(next)
    if set_cookie:
        response.set_cookie('secret', secret)
    return response

def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property

def pad_to_16(the_string):
    if len(the_string) >= 16:
        return the_string[:16]
    return str(the_string) + (16 - len(the_string)) * '0'

def decrypt_session(secret):
    user_code = session.get('uid', None)
    filename = session.get('i', None)
    if user_code == None or filename == None or secret is None:
        return
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        phrase = decrypt_phrase(record.phrase, secret)
        record.phrase = pack_phrase(the_dict)
        record.encrypted = False
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        if record.dictionary:
            the_dict = decrypt_dictionary(record.dictionary, secret)
            record.dictionary = pack_dictionary(the_dict)
            record.encrypted = False
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).all():
        the_dict = decrypt_dictionary(record.dictionary, secret)
        record.dictionary = pack_dictionary(the_dict)
        record.encrypted = False
        changed = True
    if changed:
        db.session.commit()
    return

def encrypt_session(secret):
    user_code = session.get('uid', None)
    filename = session.get('i', None)
    if user_code == None or filename == None or secret is None:
        return
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        phrase = unpack_phrase(record.phrase)
        record.phrase = encrypt_phrase(phrase, secret)
        record.encrypted = True
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        if record.dictionary:
            the_dict = unpack_dictionary(record.dictionary)
            record.dictionary = encrypt_dictionary(the_dict, secret)
            record.encrypted = True
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=False).order_by(UserDict.indexno).all():
        the_dict = unpack_dictionary(record.dictionary)
        record.dictionary = encrypt_dictionary(the_dict, secret)
        record.encrypted = True
        changed = True
    if changed:
        db.session.commit()
    return

def substitute_secret(oldsecret, newsecret):
    if oldsecret == None or oldsecret == newsecret:
        return newsecret
    user_code = session.get('uid', None)
    filename = session.get('i', None)
    if user_code == None or filename == None:
        return newsecret
    # currentsecret = None
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename).all():
        if record.encrypted:
            phrase = decrypt_phrase(record.phrase, oldsecret)
        else:
            phrase = unpack_phrase(record.phrase)
            record.encrypted = True
        record.phrase = encrypt_phrase(phrase, newsecret)
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in Attachments.query.filter_by(key=user_code, filename=filename).all():
        if record.dictionary:
            #logmessage("Found old dictionary in attachments")
            if record.encrypted:
                the_dict = decrypt_dictionary(record.dictionary, oldsecret)
                #logmessage("Decrypted it with old secret " + oldsecret)
            else:
                the_dict = unpack_dictionary(record.dictionary)
                record.encrypted = True
            #logmessage("re-encrypted with secret " + newsecret)
            record.dictionary = encrypt_dictionary(the_dict, newsecret)
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename).order_by(UserDict.indexno).all():
        #logmessage("Found old dictionary in userdict")
        if record.encrypted:
            the_dict = decrypt_dictionary(record.dictionary, oldsecret)
            #logmessage("Decrypted it with old secret " + oldsecret)
        else:
            the_dict = unpack_dictionary(record.dictionary)
            record.encrypted = True
        record.dictionary = encrypt_dictionary(the_dict, newsecret)
        #logmessage("re-encrypted with secret " + newsecret)
        changed = True
    if changed:
        #logmessage("committed changes")
        db.session.commit()
    return newsecret

def _do_login_user(user, password, secret, next, remember_me=False):
    # User must have been authenticated
    if not user: return unauthenticated()

    # Check if user account has been disabled
    if not _call_or_get(user.is_active):
        flash(word('Your account has not been enabled.'), 'error')
        return redirect(url_for('user.login'))

    # Check if user has a confirmed email address
    user_manager = current_app.user_manager
    if user_manager.enable_email and user_manager.enable_confirm_email \
            and not current_app.user_manager.enable_login_without_confirm_email \
            and not user.has_confirmed_email():
        url = url_for('user.resend_confirm_email')
        flash('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="' + str(url) + '">Re-send confirmation email</a>.', 'error')
        return redirect(url_for('user.login'))

    # Use Flask-Login to sign in user
    #print('login_user: remember_me=', remember_me)
    login_user(user, remember=remember_me)

    if 'i' in session and 'uid' in session:
        save_user_dict_key(session['uid'], session['i'])
        session['key_logged'] = True 

    # Send user_logged_in signal
    signals.user_logged_in.send(current_app._get_current_object(), user=user)

    # Prepare one-time system message
    flash(word('You have signed in successfully.'), 'success')

    newsecret = substitute_secret(secret, pad_to_16(MD5.MD5Hash(data=password).hexdigest()))
    # Redirect to 'next' URL
    response = redirect(next)
    response.set_cookie('secret', newsecret)
    return response

def _endpoint_url(endpoint):
    url = '/'
    if endpoint:
        url = url_for(endpoint)
    return url

def custom_login():
    #logmessage("Got to login page")
    user_manager =  current_app.user_manager
    db_adapter = user_manager.db_adapter
    secret = request.cookies.get('secret', None)
    #logmessage("custom_login: secret is " + str(secret))
    next = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
    reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))

    # Immediately redirect already logged in users
    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        return redirect(next)

    # Initialize form
    login_form = user_manager.login_form(request.form)          # for login.html
    register_form = user_manager.register_form()                # for login_or_register.html
    if request.method != 'POST':
        login_form.next.data     = register_form.next.data = next
        login_form.reg_next.data = register_form.reg_next.data = reg_next

    # Process valid POST
    if request.method == 'POST':
        try:
            login_form.validate()
        except:
            logmessage("Got an error when validating login")
            pass
    if request.method == 'POST' and login_form.validate():
        # Retrieve User
        user = None
        user_email = None
        if user_manager.enable_username:
            # Find user record by username
            user = user_manager.find_user_by_username(login_form.username.data)
            user_email = None
            # Find primary user_email record
            if user and db_adapter.UserEmailClass:
                user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
                        user_id=int(user.get_id()),
                        is_primary=True,
                        )
            # Find user record by email (with form.username)
            if not user and user_manager.enable_email:
                user, user_email = user_manager.find_user_by_email(login_form.username.data)
        else:
            # Find user by email (with form.email)
            user, user_email = user_manager.find_user_by_email(login_form.email.data)

        if user:
            # Log user in
            return _do_login_user(user, login_form.password.data, secret, login_form.next.data, login_form.remember_me.data)

    # Process GET or invalid POST
    return render_template(user_manager.login_template,
            form=login_form,
            login_form=login_form,
            register_form=register_form)

def setup_app(app, db):
    from docassemble.webapp.users.forms import MyRegisterForm
    from docassemble.webapp.users.views import user_profile_page
    #from docassemble.webapp.users import models
    #from docassemble.webapp.pages import views
    #from docassemble.webapp.users import views
    db_adapter = SQLAlchemyAdapter(db, User, UserAuthClass=UserAuth)
    user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm, user_profile_view_function=user_profile_page, logout_view_function=logout, login_view_function=custom_login)
    return(app)

setup_app(app, db)
lm = LoginManager(app)
lm.login_view = 'user.login'

supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
if supervisor_url:
    USING_SUPERVISOR = True
    Supervisors.query.filter_by(hostname=hostname).delete()
    db.session.commit()
    new_entry = Supervisors(hostname=hostname, url="http://" + hostname + ":9001")
    db.session.add(new_entry)
    db.session.commit()
else:
    USING_SUPERVISOR = False

sys_logger = logging.getLogger('docassemble')
sys_logger.setLevel(logging.DEBUG)

if LOGSERVER is None:
    docassemble_log_handler = logging.FileHandler(filename=os.path.join(LOG_DIRECTORY, 'docassemble.log'))
    sys_logger.addHandler(docassemble_log_handler)
else:
    import logging.handlers
    handler = logging.handlers.SysLogHandler(address=(LOGSERVER, 514), socktype=socket.SOCK_STREAM)
    sys_logger.addHandler(handler)
    
LOGFORMAT = 'docassemble: ip=%(clientip)s i=%(yamlfile)s uid=%(session)s user=%(user)s %(message)s'
def syslog_message(message):
    message = re.sub(r'\n', ' ', message)
    if current_user and current_user.is_authenticated and not current_user.is_anonymous:
        the_user = current_user.email
    else:
        the_user = "anonymous"
    sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': request.remote_addr, 'yamlfile': session.get('i', 'na'), 'user': the_user, 'session': session.get('uid', 'na')})

def syslog_message_with_timestamp(message):
    syslog_message(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message)
    
if LOGSERVER is None:
    docassemble.base.logger.set_logmessage(syslog_message_with_timestamp)
else:
    docassemble.base.logger.set_logmessage(syslog_message)

def copy_playground_modules():
    devs = list()
    for user in User.query.filter_by(active=True).all():
        for role in user.roles:
            if role.name == 'admin' or role.name == 'developer':
                devs.append(user.id)
    for user_id in devs:
        mod_dir = SavedFile(user_id, fix=True, section='playgroundmodules')
        local_dir = os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'playground' + str(user_id))
        if os.path.isdir(local_dir):
            shutil.rmtree(local_dir)
        #sys.stderr.write("Copying " + str(mod_dir.directory) + " to " + str(local_dir) + "\n")
        shutil.copytree(mod_dir.directory, local_dir)
        with open(os.path.join(local_dir, '__init__.py'), 'a') as the_file:
            the_file.write(init_py_file)

copy_playground_modules()
#sys.path.append(PLAYGROUND_MODULES_DIRECTORY)

# END OF INITIALIZATION

def proc_example_list(example_list, examples):
    for example in example_list:
        if type(example) is dict:
            for key, value in example.iteritems():
                sublist = list()
                proc_example_list(value, sublist)
                examples.append({'title': str(key), 'list': sublist})
                break
            continue
        result = dict()
        result['id'] = example
        result['interview'] = url_for('index', i="docassemble.base:data/questions/examples/" + example + ".yml")
        example_file = 'docassemble.base:data/questions/examples/' + example + '.yml'
        result['image'] = url_for('static', filename='examples/' + example + ".png")
        file_info = get_info_from_file_reference(example_file)
        start_block = 1
        end_block = 2
        if 'fullpath' not in file_info:
            continue
        try:
            interview = docassemble.base.interview_cache.get_interview(example_file)
            if len(interview.metadata):
                metadata = interview.metadata[0]
                result['title'] = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
                result['documentation'] = metadata.get('documentation', None)
                start_block = int(metadata.get('example start', 1))
                end_block = int(metadata.get('example end', start_block)) + 1
            else:
                continue
        except:
            continue
        with open(file_info['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            content = fix_initial.sub('', content)
            blocks = map(lambda x: x.strip(), document_match.split(content))
            if len(blocks):
                if re.search(r'metadata:', blocks[0]) and start_block > 0:
                    initial_block = 1
                else:
                    initial_block = 0
                if start_block > initial_block:
                    result['before_html'] = highlight("\n---\n".join(blocks[initial_block:start_block]) + "\n---", YamlLexer(), HtmlFormatter())
                else:
                    result['before_html'] = ''
                if len(blocks) > end_block:
                    result['after_html'] = highlight("---\n" + "\n---\n".join(blocks[end_block:len(blocks)]), YamlLexer(), HtmlFormatter())
                else:
                    result['after_html'] = ''
                result['source'] = "\n---\n".join(blocks[start_block:end_block])
                result['html'] = highlight(result['source'], YamlLexer(), HtmlFormatter())
        examples.append(result)
    
def get_examples():
    examples = list()
    example_list_file = get_info_from_file_reference('docassemble.base:data/questions/example-list.yml')
    if 'fullpath' in example_list_file:
        example_list = list()
        with open(example_list_file['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            proc_example_list(yaml.load(content), examples)
    #logmessage("Examples: " + str(examples))
    return(examples)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=None,
            access_token_url=None,
            base_url=None
        )
    def authorize(self):
        result = urlparse.parse_qs(request.data)
        session['google_id'] = result.get('id', [None])[0]
        session['google_email'] = result.get('email', [None])[0]
        response = make_response(json.dumps('Successfully connected user.', 200))
        response.headers['Content-Type'] = 'application/json'
        return response
    
    def callback(self):
        email = session.get('google_email')
        return (
            'google$' + str(session.get('google_id')),
            email.split('@')[0],
            email
        )

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',           
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],
            me.get('email')
        )

# class TwitterSignIn(OAuthSignIn):
#     def __init__(self):
#         super(TwitterSignIn, self).__init__('twitter')
#         self.service = OAuth1Service(
#             name='twitter',
#             consumer_key=self.consumer_id,
#             consumer_secret=self.consumer_secret,
#             request_token_url='https://api.twitter.com/oauth/request_token',
#             authorize_url='https://api.twitter.com/oauth/authorize',
#             access_token_url='https://api.twitter.com/oauth/access_token',
#             base_url='https://api.twitter.com/1.1/'
#         )
#     def authorize(self):
#         request_token = self.service.get_request_token(
#             params={'oauth_callback': self.get_callback_url()}
#         )
#         session['request_token'] = request_token
#         return redirect(self.service.get_authorize_url(request_token[0]))
#     def callback(self):
#         request_token = session.pop('request_token')
#         if 'oauth_verifier' not in request.args:
#             return None, None, None
#         oauth_session = self.service.get_auth_session(
#             request_token[0],
#             request_token[1],
#             data={'oauth_verifier': request.args['oauth_verifier']}
#         )
#         me = oauth_session.get('account/verify_credentials.json').json()
#         social_id = 'twitter$' + str(me.get('id'))
#         username = me.get('screen_name')
#         return social_id, username, None   # Twitter does not provide email

@app.route('/authorize/<provider>', methods=['POST', 'GET'])
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash(word('Authentication failed.'), 'error')
        return redirect(url_for('interview_list'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email, active=True)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=False)
    if 'i' in session and 'uid' in session:
        save_user_dict_key(session['uid'], session['i'])
        session['key_logged'] = True 
    secret = request.cookies.get('secret', None)
    newsecret = substitute_secret(secret, pad_to_16(MD5.MD5Hash(data=social_id+password_secret_key).hexdigest()))
    if not current_user.is_anonymous:
        #update_user_id(session['uid'])
        flash(word('Welcome!  You are logged in as ') + email, 'success')
    response = redirect(url_for('interview_list'))
    response.set_cookie('secret', newsecret)
    return response

# @app.route('/login')
# def login():
#     msg = Message("Test message",
#                   sender="Docassemble <no-reply@docassemble.org>",
#                   recipients=["jhpyle@gmail.com"])
#     msg.body = "Testing, testing"
#     msg.html = "<p>Testing, testing.  Someone used the login page.</p>"
#     mail.send(msg)
#     form = LoginForm()
#     return render_template('flask_user/login.html', form=form, login_form=form, title="Sign in")

@app.route('/user/google-sign-in')
def google_page():
    return render_template('flask_user/google_login.html', title="Sign in")

@app.route("/user/post-sign-in", methods=['GET'])
def post_sign_in():
    session_id = session.get('uid', None)
    return redirect(url_for('interview_list'))

@app.route("/exit", methods=['POST', 'GET'])
def exit():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if 'key_logged' in session:
        del session['key_logged']
    if session_id is not None and yaml_filename is not None:
        reset_user_dict(session_id, yaml_filename)
    return redirect(exit_page)

@app.route("/cleanup_sessions", methods=['GET'])
def cleanup_sessions():
    kv_session.cleanup_sessions()
    return render_template('base_templates/blank.html')

def add_timestamps(the_dict):
    the_dict['_internal']['starttime'] = datetime.datetime.utcnow()
    the_dict['_internal']['modtime'] = datetime.datetime.utcnow()
    return

def fresh_dictionary():
    the_dict = copy.deepcopy(initial_dict)
    add_timestamps(the_dict)
    return the_dict    

@app.route("/", methods=['POST', 'GET'])
def index():
    #seq = Sequence(message_sequence)
    #nextid = connection.execute(seq)
    session_id = session.get('uid', None)
    secret = request.cookies.get('secret', None)
    encrypted = session.get('encrypted', True)
    if secret is None:
        secret = ''.join(random.choice(string.ascii_letters) for i in range(16))
        set_cookie = True
    else:
        set_cookie = False
    yaml_filename = session.get('i', default_yaml_filename)
    steps = 0
    need_to_reset = False
    # secret_parameter = request.args.get('sid', None)
    yaml_parameter = request.args.get('i', None)
    session_parameter = request.args.get('session', None)
    # if secret_parameter is not None:
    #     if currentsecret != secret_parameter:
    #         currentsecret = secret_parameter
    #         session['currentsecret'] = currentsecret
    if yaml_parameter is not None:
        show_flash = False
        yaml_filename = yaml_parameter
        # if session.get('nocache', False):
        #     docassemble.base.interview_cache.clear_cache(yaml_filename)
        old_yaml_filename = session.get('i', None)
        # if yaml_filename.startswith("/playground") and not current_user.is_authenticated:
        #     flash(word("You must be logged in as a developer to continue"), 'error')
        #     return redirect(url_for('user.login', next=url_for('index', **request.args)))
        if old_yaml_filename is not None:
            if old_yaml_filename != yaml_filename:
                session['i'] = yaml_filename
                if request.args.get('from_list', None) is None and not yaml_filename.startswith("docassemble.playground") and not yaml_filename.startswith("docassemble.base"):
                    show_flash = True
        if session_parameter is None:
            if show_flash:
                if current_user.is_authenticated:
                    message = "Starting a new interview.  To go back to your previous interview, go to My Interviews on the menu."
                else:
                    message = "Starting a new interview.  To go back to your previous interview, log in to see a list of your interviews."
            #logmessage("session parameter is none")
            user_code, user_dict = reset_session(yaml_filename, secret)
            session_id = session.get('uid', None)
            if 'key_logged' in session:
                del session['key_logged']
            need_to_reset = True
        else:
            logmessage("Both i and session provided")
            if show_flash:
                if current_user.is_authenticated:
                    message = "Entering a different interview.  To go back to your previous interview, go to My Interviews on the menu."
                else:
                    message = "Entering a different interview.  To go back to your previous interview, log in to see a list of your interviews."
        if show_flash:
            flash(word(message), 'info')
    if session_parameter is not None:
        logmessage("session parameter is " + str(session_parameter))
        session_id = session_parameter
        session['uid'] = session_id
        if yaml_parameter is not None:
            session['i'] = yaml_filename
        if 'key_logged' in session:
            del session['key_logged']
        need_to_reset = True
    if session_id:
        user_code = session_id
        #logmessage("session id is " + str(session_id))
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(user_code, yaml_filename, secret)
        except:
            user_code, user_dict = reset_session(yaml_filename, secret)
            encrypted = False
            session['encrypted'] = encrypted
            is_encrypted = encrypted
            if 'key_logged' in session:
                del session['key_logged']
            need_to_reset = True
        if encrypted != is_encrypted:
            encrypted = is_encrypted
            session['encrypted'] = encrypted
        # if currentsecret is not None:
        #     try:
        #         steps, user_dict = fetch_user_dict(user_code, yaml_filename, currentsecret)
        #         secret_to_use = currentsecret
        #     except:
        #         del session['currentsecret']
        #         currentsecret = None
        #         try:
        #             steps, user_dict = fetch_user_dict(user_code, yaml_filename, secret)
        #             secret_to_use = secret
        #         except:
        #             logmessage("Error: could not get user dict")
        # else:
        #     steps, user_dict = fetch_user_dict(user_code, yaml_filename, secret)
        #     secret_to_use = secret
        if user_dict is None:
            logmessage("user_dict was none")
            del user_code
            del user_dict
    try:
        user_dict
        user_code
    except:
        logmessage("resetting session")
        user_code, user_dict = reset_session(yaml_filename, secret)
        encrypted = False
        session['encrypted'] = encrypted
        if 'key_logged' in session:
            del session['key_logged']
        steps = 0
    action = None
    if user_dict.get('multi_user', False) is True and encrypted is True:
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret)
        # user_dict['_internal']['secret'] = ''.join(random.choice(string.ascii_letters) for i in range(16))
        # currentsecret, temptwo = substitute_secret(secret, user_dict['_internal']['secret'])
        # session['currentsecret'] = currentsecret
        # secret_in_use = currentsecret
    if user_dict.get('multi_user', False) is False and encrypted is False:
        encrypt_session(secret)
        encrypted = True
        session['encrypted'] = encrypted
    if current_user.is_authenticated and 'key_logged' not in session:
        #logmessage("save_user_dict_key called with " + user_code + " and " + yaml_filename)
        save_user_dict_key(user_code, yaml_filename)
        session['key_logged'] = True
    if 'action' in session:
        action = json.loads(myb64unquote(session['action']))
        del session['action']
    if len(request.args):
        if 'action' in request.args:
            session['action'] = request.args['action']
            response = redirect(url_for('index'))
            if set_cookie:
                response.set_cookie('secret', secret)
            return response
        for argname in request.args:
            if argname in ('filename', 'question', 'format', 'index', 'i', 'action', 'from_list', 'session'):
                continue
            if re.match('[A-Za-z_]+', argname):
                exec("url_args['" + argname + "'] = " + repr(request.args.get(argname).encode('unicode_escape')), user_dict)
            need_to_reset = True
    if need_to_reset:
        save_user_dict(user_code, user_dict, yaml_filename, secret, encrypt=encrypted)
        # if current_user.is_authenticated:
        #     save_user_dict_key(user_code, yaml_filename)
        #     session['key_logged'] = True
        response = redirect(url_for('index'))
        if set_cookie:
            response.set_cookie('secret', secret)
        return response
    #logmessage("action is " + str(action))
    post_data = request.form.copy()
    if '_email_attachments' in post_data and '_attachment_email_address' in post_data and '_question_number' in post_data:
        success = False
        question_number = post_data['_question_number']
        attachment_email_address = post_data['_attachment_email_address']
        if '_attachment_include_editable' in post_data:
            if post_data['_attachment_include_editable'] == 'True':
                include_editable = True
            else:
                include_editable = False
            del post_data['_attachment_include_editable']
        else:
            include_editable = False
        del post_data['_question_number']
        del post_data['_email_attachments']
        del post_data['_attachment_email_address']
        logmessage("Got e-mail request for " + str(question_number) + " with e-mail " + str(attachment_email_address) + " and rtf inclusion of " + str(include_editable) + " and using yaml file " + yaml_filename)
        the_user_dict = get_attachment_info(user_code, question_number, yaml_filename, secret)
        if the_user_dict is not None:
            #logmessage("the_user_dict is not none!")
            interview = docassemble.base.interview_cache.get_interview(yaml_filename)
            interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action))
            interview.assemble(the_user_dict, interview_status)
            if len(interview_status.attachments) > 0:
                #logmessage("there are attachments!")
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
                        logmessage("Need to attach to the e-mail a file called " + str(the_attachment['filename']) + '.' + str(the_format) + ", which is located on the server at " + str(the_filename) + ", with mime type " + str(mime_type))
                        attached_file_count += 1
                if attached_file_count > 0:
                    doc_names = list()
                    for attach_info in attachment_info:
                        if attach_info['attachment']['name'] not in doc_names:
                            doc_names.append(attach_info['attachment']['name'])
                    subject = comma_and_list(doc_names)
                    if len(doc_names) > 1:
                        body = "Your " + subject + " are attached."
                    else:
                        body = "Your " + subject + " is attached."
                    html = "<p>" + body + "</p>"
                    logmessage("Need to send an e-mail with subject " + subject + " to " + str(attachment_email_address) + " with " + str(attached_file_count) + " attachment(s)")
                    msg = Message(subject, recipients=[attachment_email_address], body=body, html=html)
                    for attach_info in attachment_info:
                        with open(attach_info['path'], 'rb') as fp:
                            msg.attach(attach_info['filename'], attach_info['mimetype'], fp.read())
                    try:
                        # mail.send(msg)
                        logmessage("Starting to send")
                        async_mail(msg)
                        logmessage("Finished sending")
                        success = True
                    except Exception as errmess:
                        logmessage(str(errmess))
                        success = False
        if success:
            flash(word("Your documents were e-mailed to") + " " + str(attachment_email_address) + ".", 'info')
        else:
            flash(word("Unable to e-mail your documents to") + " " + str(attachment_email_address) + ".", 'error')
    if '_back_one' in post_data and steps > 1:
        steps, user_dict, is_encrypted = fetch_previous_user_dict(user_code, yaml_filename, secret)
        if encrypted != is_encrypted:
            encrypted = is_encrypted
            session['encrypted'] = encrypted
        #logmessage("Went back")
    elif 'filename' in request.args:
        #logmessage("Got a GET statement with filename!")
        the_user_dict = get_attachment_info(user_code, request.args.get('question'), request.args.get('filename'), secret)
        if the_user_dict is not None:
            #logmessage("the_user_dict is not none!")
            interview = docassemble.base.interview_cache.get_interview(request.args.get('filename'))
            interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action))
            interview.assemble(the_user_dict, interview_status)
            if len(interview_status.attachments) > 0:
                #logmessage("there are attachments!")
                the_attachment = interview_status.attachments[int(request.args.get('index'))]
                the_filename = the_attachment['file'][request.args.get('format')]
                the_format = request.args.get('format')
                #block_size = 4096
                #status = '200 OK'
                if the_format == "pdf":
                    mime_type = 'application/pdf'
                elif the_format == "tex":
                    mime_type = 'application/x-latex'
                elif the_format == "rtf":
                    mime_type = 'application/rtf'
                elif the_format == "docx":
                    mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                return(send_file(the_filename, mimetype=str(mime_type), as_attachment=True, attachment_filename=str(the_attachment['filename']) + '.' + str(the_format)))
    if '_checkboxes' in post_data:
        checkbox_fields = json.loads(myb64unquote(post_data['_checkboxes'])) #post_data['_checkboxes'].split(",")
        for checkbox_field in checkbox_fields:
            if checkbox_field not in post_data:
                post_data.add(checkbox_field, 'False')
    something_changed = False
    if '_tracker' in post_data and user_dict['_internal']['tracker'] != int(post_data['_tracker']):
        logmessage("Something changed.")
        #logmessage("user dict has " + str(user_dict['_internal']['tracker']) + " and post data has " + post_data['_tracker'])
        something_changed = True
    if '_track_location' in post_data and post_data['_track_location']:
        logmessage("Found track location of " + post_data['_track_location'])
        the_location = json.loads(post_data['_track_location'])
    else:
        the_location = None
    should_assemble = False
    if something_changed:
        for key in post_data:
            try:
                if key_requires_preassembly.search(from_safeid(key)):
                    should_assemble = True
                    break
            except:
                logmessage("Bad key: " + str(key))
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action, location=the_location), tracker=user_dict['_internal']['tracker'])
    if should_assemble:
        logmessage("Reassembling.")
        interview.assemble(user_dict, interview_status)
    #else:
        #logmessage("I am not assembling.")        
    changed = False
    error_messages = list()
    if '_the_image' in post_data:
        #interview.assemble(user_dict, interview_status)
        file_field = from_safeid(post_data['_save_as']);
        if match_invalid.search(file_field):
            error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
        else:
            if something_changed and key_requires_preassembly.search(file_field) and not should_assemble:
                interview.assemble(user_dict, interview_status)
            initial_string = 'import docassemble.base.core'
            try:
                exec(initial_string, user_dict)
            except Exception as errMess:
                error_messages.append(("error", "Error: " + str(errMess)))
            if '_success' in post_data and post_data['_success']:
                theImage = base64.b64decode(re.search(r'base64,(.*)', post_data['_the_image']).group(1) + '==')
                #sys.stderr.write("Got theImage and it is " + str(len(theImage)) + " bytes long\n")
                filename = secure_filename('canvas.png')
                file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                extension, mimetype = get_ext_and_mimetype(filename)
                new_file = SavedFile(file_number, extension=extension, fix=True)
                new_file.write_content(theImage)
                new_file.finalize()
                #sys.stderr.write("Saved theImage\n")
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ", filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')"
            else:
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ")"
            #sys.stderr.write(the_string + "\n")
            try:
                exec(the_string, user_dict)
                changed = True
                steps += 1
            except Exception as errMess:
                #sys.stderr.write("Error: " + str(errMess) + "\n")
                error_messages.append(("error", "Error: " + str(errMess)))
    if '_files' in post_data:
        #logmessage("There are files")
        #interview.assemble(user_dict, interview_status)
        file_fields = json.loads(myb64unquote(post_data['_files'])) #post_data['_files'].split(",")
        has_invalid_fields = False
        should_assemble_now = False
        for orig_file_field in file_fields:
            try:
                file_field = from_safeid(orig_file_field)
            except:
                error_messages.append(("error", "Error: Invalid file_field: " + orig_file_field))
                break
            if match_invalid.search(file_field):
                has_invalid_fields = True
                error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                break
            if key_requires_preassembly.search(file_field):
                should_assemble_now = True
        if not has_invalid_fields:
            initial_string = 'import docassemble.base.core'
            try:
                exec(initial_string, user_dict)
            except Exception as errMess:
                error_messages.append(("error", "Error: " + str(errMess)))
            if something_changed and should_assemble_now and not should_assemble:
                interview.assemble(user_dict, interview_status)
            for orig_file_field in file_fields:
                #logmessage("There is a file_field")
                if orig_file_field in request.files:
                    #logmessage("There is a file_field in request.files")
                    the_files = request.files.getlist(orig_file_field)
                    if the_files:
                        files_to_process = list()
                        for the_file in the_files:
                            #logmessage("There is a file_field in request.files and it has a type of " + str(type(the_file)) + " and its str representation is " + str(the_file))
                            filename = secure_filename(the_file.filename)
                            file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                            extension, mimetype = get_ext_and_mimetype(filename)
                            saved_file = SavedFile(file_number, extension=extension, fix=True)
                            if extension == "jpg" and daconfig.get('imagemagick', 'convert') is not None:
                                unrotated = tempfile.NamedTemporaryFile(suffix=".jpg")
                                rotated = tempfile.NamedTemporaryFile(suffix=".jpg")
                                the_file.save(unrotated.name)
                                call_array = [daconfig.get('imagemagick', 'convert'), str(unrotated.name), '-auto-orient', '-density', '300', 'jpeg:' + rotated.name]
                                result = call(call_array)
                                if result == 0:
                                    saved_file.copy_from(rotated.name)
                                else:
                                    saved_file.copy_from(unrotated.name)
                            else:
                                the_file.save(saved_file.path)
                                saved_file.save()
                            if mimetype == 'video/quicktime' and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
                                result = call(call_array)
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'copy', '-acodec', 'copy', saved_file.path + '.mp4']
                                result = call(call_array)
                            if mimetype == 'video/mp4' and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
                                result = call(call_array)
                            if mimetype == 'video/ogg' and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '22', '-c:a', 'libmp3lame', '-qscale:a', '2', '-ac', '2', '-ar', '44100', saved_file.path + '.mp4']
                                result = call(call_array)
                            if mimetype == 'audio/mpeg' and daconfig.get('pacpl', 'pacpl') is not None:
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
                                result = call(call_array)
                            if mimetype == 'audio/ogg' and daconfig.get('pacpl', 'pacpl') is not None:
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
                                result = call(call_array)
                            if mimetype in ['audio/3gpp'] and daconfig.get('avconv', 'avconv') is not None:
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, saved_file.path + '.ogg']
                                result = call(call_array)
                                call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, saved_file.path + '.mp3']
                                result = call(call_array)
                            if mimetype in ['audio/x-wav', 'audio/wav'] and daconfig.get('pacpl', 'pacpl') is not None:
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
                                result = call(call_array)
                                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
                                result = call(call_array)
                            if extension == "pdf":
                                make_image_files(saved_file.path)
                            saved_file.finalize()
                            files_to_process.append((filename, file_number, mimetype, extension))
                        try:
                            file_field = from_safeid(orig_file_field)
                        except:
                            error_messages.append(("error", "Error: Invalid file_field: " + orig_file_field))
                            break
                        if match_invalid.search(file_field):
                            error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                            break
                        if len(files_to_process) > 0:
                            elements = list()
                            indexno = 0
                            for (filename, file_number, mimetype, extension) in files_to_process:
                                elements.append("docassemble.base.core.DAFile('" + file_field + "[" + str(indexno) + "]', filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')")
                                indexno += 1
                            the_string = file_field + " = docassemble.base.core.DAFileList('" + file_field + "', elements=[" + ", ".join(elements) + "])"
                        else:
                            the_string = file_field + " = None"
                        logmessage("Doing " + the_string)
                        try:
                            exec(the_string, user_dict)
                            changed = True
                            steps += 1
                        except Exception as errMess:
                            sys.stderr.write("Error: " + str(errMess) + "\n")
                            error_messages.append(("error", "Error: " + str(errMess)))
                        #post_data.add(file_field, str(file_number))
    known_datatypes = dict()
    if '_datatypes' in post_data:
        #logmessage(myb64unquote(post_data['_datatypes']))
        known_datatypes = json.loads(myb64unquote(post_data['_datatypes']))
    known_varnames = dict()
    if '_varnames' in post_data:
        known_varnames = json.loads(myb64unquote(post_data['_varnames']))
    known_variables = dict()
    for orig_key in copy.deepcopy(post_data):
        if orig_key in ['_checkboxes', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location', '_varnames']:
            continue
        try:
            key = myb64unquote(orig_key)
        except:
            continue
        if key.startswith('_field_') and orig_key in known_varnames:
            post_data[known_varnames[orig_key]] = post_data[orig_key]
    for orig_key in post_data:
        if orig_key in ['_checkboxes', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location', '_varnames']:
            continue
        #logmessage("Got a key: " + key)
        data = post_data[orig_key]
        try:
            key = myb64unquote(orig_key)
        except:
            raise DAError("invalid name " + str(orig_key))
        #data = re.sub(r'"""', '', data)
        if key.startswith('_field_'):
            continue
        bracket_expression = None
        if match_brackets.search(key):
            #logmessage("Searching key " + str(key))
            match = match_inside_and_outside_brackets.search(key)
            try:
                key = match.group(1)
            except:
                raise DAError("invalid name " + str(match.group(1)))
            real_key = safeid(key)
            if match_invalid.search(key):
                error_messages.append(("error", "Error: Invalid character in key: " + key))
                break
            b_match = match_inside_brackets.search(match.group(2))
            if b_match:
                try:
                    bracket_expression = from_safeid(b_match.group(1))
                except:
                    bracket_expression = b_match.group(1)
            bracket = match_inside_brackets.sub(process_bracket_expression, match.group(2))
            #logmessage("key is " + str(key) + " and bracket is " + str(bracket))
            if key in user_dict:
                known_variables[key] = True
            if key not in known_variables:
                try:
                    eval(key, user_dict)
                except:
                    #logmessage("setting key " + str(key) + " to empty dict")
                    the_string = key + ' = dict()'
                    try:
                        exec(the_string, user_dict)
                        known_variables[key] = True
                    except:
                        raise DAError("cannot initialize " + key)
            key = key + bracket
        else:
            real_key = orig_key
            if match_invalid_key.search(key):
                error_messages.append(("error", "Error: Invalid character in key: " + key))
                break
        #logmessage("Real key is " + real_key + " and key is " + key)
        do_append = False
        do_opposite = False
        if real_key in known_datatypes:
            #logmessage("key " + real_key + "is in datatypes: " + known_datatypes[key])
            if known_datatypes[real_key] in ['boolean', 'checkboxes', 'yesno', 'noyes', 'yesnowide', 'noyeswide']:
                if data == "True":
                    data = "True"
                else:
                    data = "False"
            elif known_datatypes[real_key] in ['threestate', 'yesnomaybe', 'noyesmaybe', 'yesnowidemaybe', 'noyeswidemaybe']:
                if data == "True":
                    data = "True"
                elif data == "None":
                    data = "None"
                else:
                    data = "False"
            elif known_datatypes[real_key] == 'integer':
                if data == '':
                    data = 0
                data = "int(" + repr(data) + ")"
            elif known_datatypes[real_key] in ['number', 'float', 'currency', 'range']:
                if data == '':
                    data = 0
                data = "float(" + repr(data) + ")"
            elif known_datatypes[real_key] in ['object', 'object_radio']:
                if data == '':
                    continue
                #logmessage("Got to here")
                data = "_internal['objselections'][" + repr(key) + "][" + repr(data) + "]"
            elif known_datatypes[real_key] in ['object_checkboxes'] and bracket_expression is not None:
                if data not in ['True', 'False', 'None']:
                    continue
                do_append = True
                if data == 'False':
                    do_opposite = True
                data = "_internal['objselections'][" + repr(from_safeid(real_key)) + "][" + repr(bracket_expression) + "]"
            else:
                if type(data) in [str, unicode]:
                    data = data.strip()
                data = repr(data)
            if known_datatypes[real_key] in ['object_checkboxes']:
                do_append = True
        elif key == "_multiple_choice":
            #logmessage("key is multiple choice")
            data = "int(" + repr(data) + ")"
        else:
            logmessage("key is not in datatypes where datatypes is " + str(known_datatypes))
            data = repr(data)
        if key == "_multiple_choice":
            #interview.assemble(user_dict, interview_status)
            #if interview_status.question.question_type == "multiple_choice" and not hasattr(interview_status.question.fields[0], 'saveas'):
                #key = '_internal["answers"]["' + interview_status.question.name + '"]'
            if '_question_name' in post_data:
                key = '_internal["answers"][' + repr(post_data['_question_name']) + ']'
            #else:
                #continue
                #error_messages.append(("error", "Error: multiple choice values were supplied, but docassemble was not waiting for an answer to a multiple choice question."))
        if do_append:
            key_to_use = from_safeid(real_key)
            if do_opposite:
                the_string = 'if ' + data + ' in ' + key_to_use + ':\n    ' + key_to_use + '.remove(' + data + ')'
            else:
                the_string = 'if ' + data + ' not in ' + key_to_use + ':\n    ' + key_to_use + '.append(' + data + ')'
        else:
            the_string = key + ' = ' + data
        logmessage("Doing " + str(the_string))
        try:
            exec(the_string, user_dict)
            changed = True
            steps += 1
        except Exception as errMess:
            error_messages.append(("error", "Error: " + str(errMess)))
    # if 'x' in user_dict:
    #     del user_dict['x']
    # if 'i' in user_dict:
    #     del user_dict['i']
    # if changed and '_question_name' in post_data:
        # user_dict['_internal']['answered'].add(post_data['_question_name'])
        # logmessage("From server.py, answered name is " + post_data['_question_name'])
        # user_dict['role_event_notification_sent'] = False
    if changed and '_question_name' in post_data and post_data['_question_name'] not in user_dict['_internal']['answers']:
        user_dict['_internal']['answered'].add(post_data['_question_name'])
    interview.assemble(user_dict, interview_status)
    if not interview_status.can_go_back:
        user_dict['_internal']['steps_offset'] = steps
    if len(interview_status.attachments) > 0:
        #logmessage("Updating attachment info")
        update_attachment_info(user_code, user_dict, interview_status, secret)
    if interview_status.question.question_type == "restart":
        url_args = user_dict['url_args']
        user_dict = fresh_dictionary()
        user_dict['url_args'] = url_args
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request))
        reset_user_dict(user_code, yaml_filename)
        save_user_dict(user_code, user_dict, yaml_filename, secret)
        if current_user.is_authenticated:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        steps = 0
        changed = False
        interview.assemble(user_dict, interview_status)
    if interview_status.question.interview.use_progress_bar and interview_status.question.progress is not None and interview_status.question.progress > user_dict['_internal']['progress']:
        user_dict['_internal']['progress'] = interview_status.question.progress
    if interview_status.question.question_type == "exit":
        user_dict = fresh_dictionary()
        reset_user_dict(user_code, yaml_filename)
        save_user_dict(user_code, user_dict, yaml_filename, secret)
        if current_user.is_authenticated:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        if interview_status.questionText != '':
            return redirect(interview_status.questionText)
        else:
            return redirect(exit_page)
    if interview_status.question.question_type == "refresh":
        return redirect(url_for('index'))
    if interview_status.question.question_type == "signin":
        return redirect(url_for('user.login'))
    if interview_status.question.question_type == "leave":
        if interview_status.questionText != '':
            return redirect(interview_status.questionText)
        else:
            return redirect(exit_page)
    user_dict['_internal']['answers'] = dict()
    if changed and interview_status.question.interview.use_progress_bar:
        advance_progress(user_dict)
    save_user_dict(user_code, user_dict, yaml_filename, secret, changed=changed, encrypt=encrypted)
    if user_dict.get('multi_user', False) is True and encrypted is True:
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret)
    if user_dict.get('multi_user', False) is False and encrypted is False:
        encrypt_session(secret)
        encrypted = True
        session['encrypted'] = encrypted
    flash_content = ""
    messages = get_flashed_messages(with_categories=True) + error_messages
    if messages and len(messages):
        flash_content += '<div class="container topcenter" id="flash">'
        for classname, message in messages:
            if classname == 'error':
                classname = 'danger'
            flash_content += '<div class="row"><div class="col-sm-7 col-md-6 col-lg-5 col-centered"><div class="alert alert-' + classname + '"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div></div></div>'
        flash_content += '</div>'
#     scripts = """
#     <script src="//ajax.googleapis.com/ajax/libs/jquery/2.2.0/jquery.min.js"></script>
#     <script src="//ajax.aspnetcdn.com/ajax/jquery.validate/1.14.0/jquery.validate.min.js"></script>
#     <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
#     <script src="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/js/jasny-bootstrap.min.js"></script>
# """
        # $(function () {
        #   $('.tabs a:last').tab('show')
        # })
    scripts = '\n    <script src="' + url_for('static', filename='app/jquery.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/jquery.validate.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap/js/bootstrap.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/jasny-bootstrap.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-slider/bootstrap-slider.min.js') + '"></script>\n'
    #\n    <script src="' + url_for('static', filename='jquery-mobile/jquery.mobile.custom.min.js') + '"></script>
    scripts += '    <script src="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.js') + '"></script>' + """
    <script>
      $( document ).ready(function() {
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'click focus', html: true})
        })
        $("#daform input, #daform textarea, #daform select").first().each(function(){
          $(this).focus();
          var inputType = $(this).attr('type');
          if ($(this).prop('tagName') != 'SELECT' && inputType != "checkbox" && inputType != "radio" && inputType != "hidden" && inputType != "submit" && inputType != "file" && inputType != "range"){
            var strLength = $(this).val().length * 2;
            $(this)[0].setSelectionRange(strLength, strLength);
          }
        });
        $(".to-labelauty").labelauty({ width: "100%" });
        $(".to-labelauty-icon").labelauty({ label: false });
        $(function(){ 
          var navMain = $("#navbar-collapse");
          navMain.on("click", "a", null, function () {
            if (!($(this).hasClass("dropdown-toggle"))){
              navMain.collapse('hide');
            }
          });
          $("#helptoggle").on("click", function(){
            window.scrollTo(0, 0);
            $(this).removeClass('daactivetext')
          });
          $("#sourcetoggle").on("click", function(){
            $(this).toggleClass("sourceactive");
          });
          $('#backToQuestion').click(function(event){
            event.preventDefault();
            $('#questionlabel').trigger('click');
          });
        });
        $(".showif").each(function(){
          var showIfSign = $(this).data('showif-sign');
          var showIfVar = $(this).data('showif-var');
          var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/, "\\\\$1");
          var showIfVal = $(this).data('showif-val');
          var saveAs = $(this).data('saveas');
          var isSame = (saveAs == showIfVar);
          var showIfDiv = this;
          var showHideDiv = function(){
            //console.log("showHideDiv1")
            if($(this).parents(".showif").length !== 0){
              return;
            }
            var theVal;
            if ($(this).attr('type') == "checkbox" || $(this).attr('type') == "radio"){
              theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
            }
            else{
              theVal = $(this).val();
            }
            //console.log("val is " + theVal + " and showIfVal is " + showIfVal)
            if(theVal == showIfVal){
              //console.log("They are the same");
              if (showIfSign){
                $(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
              else{
                $(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
            }
            else{
              //console.log("They are not the same");
              if (showIfSign){
                $(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
              else{
                $(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
            }
          };
          $("#" + showIfVarEscaped).each(showHideDiv);
          $("#" + showIfVarEscaped).change(showHideDiv);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").each(showHideDiv);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").change(showHideDiv);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").each(showHideDiv);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(showHideDiv);
        });
      });
    </script>"""
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    if interview_status.question.question_type == "signature":
        output = '<!doctype html>\n<html lang="' + interview_language + '">\n  <head><meta charset="utf-8"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=0" /><title>' + interview_status.question.interview.get_title().get('full', default_title) + '</title><script src="' + url_for('static', filename='app/jquery.min.js') + '"></script><script src="' + url_for('static', filename='app/signature.js') + '"></script><link href="' + url_for('static', filename='app/signature.css') + '" rel="stylesheet"><title>' + word('Sign Your Name') + '</title></head>\n  <body onresize="resizeCanvas()">'
        output += signature_html(interview_status, DEBUG, ROOT)
        output += """\n  </body>\n</html>"""
    else:
        extra_scripts = list()
        extra_css = list()
        if 'speak_text' in interview_status.extras and interview_status.extras['speak_text']:
            interview_status.initialize_screen_reader()
            util_language = docassemble.base.util.get_language()
            util_dialect = docassemble.base.util.get_dialect()
            question_language = interview_status.question.language
            if question_language != '*':
                the_language = question_language
            else:
                the_language = util_language
            if the_language == util_language and util_dialect is not None:
                the_dialect = util_dialect
            elif voicerss_config and 'languages' in voicerss_config and the_language in voicerss_config['languages']:
                the_dialect = voicerss_config['languages'][the_language]
            elif the_language in valid_voicerss_languages:
                the_dialect = valid_voicerss_languages[the_language][0]
            else:
                logmessage("Unable to determine dialect; reverting to default")
                the_language = DEFAULT_LANGUAGE
                the_dialect = DEFAULT_DIALECT
            for question_type in ['question', 'help']:
                for audio_format in ['mp3', 'ogg']:
                    interview_status.screen_reader_links[question_type].append([url_for('speak_file', question=interview_status.question.number, type=question_type, format=audio_format, language=the_language, dialect=the_dialect), audio_mimetype_table[audio_format]])
        # else:
        #     logmessage("speak_text was not here")
        content = as_html(interview_status, extra_scripts, extra_css, url_for, DEBUG, ROOT)
        if interview_status.using_screen_reader:
            for question_type in ['question', 'help']:
                #phrase = codecs.encode(to_text(interview_status.screen_reader_text[question_type]).encode('utf-8'), 'base64').decode().replace('\n', '')
                phrase = to_text(interview_status.screen_reader_text[question_type])
                if encrypted:
                    the_phrase = encrypt_phrase(phrase, secret)
                else:
                    the_phrase = pack_phrase(phrase, secret)
                existing_entry = SpeakList.query.filter_by(filename=yaml_filename, key=user_code, question=interview_status.question.number, type=question_type, language=the_language, dialect=the_dialect).first()
                if existing_entry:
                    if existing_entry.encrypted:
                        existing_phrase = decrypt_phrase(existing_entry.phrase, secret)
                    else:
                        existing_phrase = unpack_phrase(existing_entry.phrase)
                    if phrase != existing_phrase:
                        logmessage("The phrase changed; updating it")
                        existing_entry.phrase = the_phrase
                        existing_entry.upload = None
                        existing_entry.encrypted = encrypted
                        db.session.commit()
                else:
                    new_entry = SpeakList(filename=yaml_filename, key=user_code, phrase=the_phrase, question=interview_status.question.number, type=question_type, language=the_language, dialect=the_dialect, encrypted=encrypted)
                    db.session.add(new_entry)
                    db.session.commit()
        if interview_status.question.language != '*':
            interview_language = interview_status.question.language
        else:
            interview_language = DEFAULT_LANGUAGE
        # output = '<!DOCTYPE html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet">\n    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css" rel="stylesheet">\n    <link href="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />\n    <link href="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/app.css') + '" rel="stylesheet">'
        output = '<!DOCTYPE html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap-theme.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/jasny-bootstrap.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />\n    <link href="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-slider/css/bootstrap-slider.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/app.css') + '" rel="stylesheet">'
        #    <link href="' + url_for('static', filename='jquery-mobile/jquery.mobile.custom.theme.min.css') + '" rel="stylesheet">\n
        #\n    <link href="' + url_for('static', filename='jquery-mobile/jquery.mobile.custom.structure.css') + '" rel="stylesheet">
        if DEBUG:
            output += '\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'
        output += "".join(extra_css)
        output += '\n    <title>' + interview_status.question.interview.get_title().get('full', default_title) + '</title>\n  </head>\n  <body>\n'
        output += make_navbar(interview_status, default_title, default_short_title, (steps - user_dict['_internal']['steps_offset']), SHOW_LOGIN) + '    <div class="container">' + "\n      " + '<div class="row">\n        <div class="tab-content">\n' + flash_content
        if interview_status.question.interview.use_progress_bar:
            output += progress_bar(user_dict['_internal']['progress'])
        output += content + "        </div>\n      </div>\n"
        if DEBUG:
            output += '      <div class="row">' + "\n"
            output += '        <div id="source" class="col-md-12 collapse">' + "\n"
            if interview_status.using_screen_reader:
                output += '          <h3>' + word('Plain text of sections') + '</h3>' + "\n"
                for question_type in ['question', 'help']:
                    output += '<pre style="white-space: pre-wrap;">' + to_text(interview_status.screen_reader_text[question_type]) + '</pre>\n'
            output += '          <h3>' + word('Source code for question') + '</h3>' + "\n"
            if interview_status.question.source_code is None:
                output += word('unavailable')
            else:
                output += highlight(interview_status.question.source_code, YamlLexer(), HtmlFormatter())
            if len(interview_status.question.fields_used):
                output += "<p>Variables set: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.fields_used)]) + "</p>"
            if len(interview_status.question.names_used):
                output += "<p>Variables in code: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.names_used)]) + "</p>"
            if len(interview_status.question.mako_names):
                output += "<p>Variables in templates: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.mako_names)]) + "</p>"
            if len(interview_status.seeking) > 1:
                output += '          <h4>' + word('How question came to be asked') + '</h4>' + "\n"
                # output += '<ul>\n'
                # for foo in user_dict['_internal']['answered']:
                #     output += "<li>" + str(foo) + "</li>"
                # output += '</ul>\n'
                for stage in interview_status.seeking:
                    if 'question' in stage and 'reason' in stage and stage['question'] is not interview_status.question:
                        if stage['reason'] == 'initial':
                            output += "          <h5>" + word('Ran initial code') + "</h5>\n"
                        elif stage['reason'] == 'mandatory question':
                            output += "          <h5>" + word('Tried to ask mandatory question') + "</h5>\n"
                        elif stage['reason'] == 'mandatory code':
                            output += "          <h5>" + word('Tried to run mandatory code') + "</h5>\n"
                        elif stage['reason'] == 'asking':
                            output += "          <h5>" + word('Tried to ask question') + "</h5>\n"
                        if stage['question'].from_source.path != interview.source.path:
                            output += '          <p style="font-weight: bold;"><small>(' + word('from') + ' ' + stage['question'].from_source.path +")</small></p>\n"
                        if stage['question'].source_code is None:
                            output += word('unavailable')
                        else:
                            output += highlight(stage['question'].source_code, YamlLexer(), HtmlFormatter())
                        if len(stage['question'].fields_used):
                            output += "<p>Variables set: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].fields_used)]) + "</p>"
                        if len(stage['question'].names_used):
                            output += "<p>Variables in code: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].names_used)]) + "</p>"
                        if len(stage['question'].mako_names):
                            output += "<p>Variables in templates: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].mako_names)]) + "</p>"
                    elif 'variable' in stage:
                        output += "          <h5>" + word('Needed definition of') + " <code>" + str(stage['variable']) + "</code></h5>\n"
                output += '          <h4>' + word('Variables defined') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(docassemble.base.util.pickleable_objects(user_dict))]) + '</p>' + "\n"
            output += '        </div>' + "\n"
            output += '      </div>' + "\n"
        output += '    </div>'
        output += scripts + "\n    " + "".join(extra_scripts) + """\n  </body>\n</html>"""
    #logmessage(output.encode('utf8'))
    response = make_response(output.encode('utf8'), '200 OK')
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    if set_cookie:
        response.set_cookie('secret', secret)
    return response

if __name__ == "__main__":
    app.run()

def process_bracket_expression(match):
    #return("[" + repr(urllib.unquote(match.group(1)).encode('unicode_escape')) + "]")
    try:
        inner = codecs.decode(match.group(1), 'base64').decode('utf-8')
    except:
        inner = match.group(1)
    return("[" + repr(inner) + "]")

def myb64unquote(the_string):
    return(codecs.decode(the_string, 'base64').decode('utf-8'))

def safeid(text):
    return codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '')

def from_safeid(text):
    #logmessage("from_safeid: " + str(text))
    return(codecs.decode(text, 'base64').decode('utf-8'))

def progress_bar(progress):
    if progress == 0:
        return('');
    return('<div class="row"><div class="col-lg-6 col-md-8 col-sm-10"><div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="' + str(progress) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(progress) + '%;"></div></div></div></div>\n')

def pad(the_string):
    return the_string + (16 - len(the_string) % 16) * chr(16 - len(the_string) % 16)

def unpad(the_string):
    return the_string[0:-ord(the_string[-1])]

def encrypt_phrase(phrase, secret):
    iv = app.secret_key[:16]
    encrypter = AES.new(secret, AES.MODE_CBC, iv)
    return iv + codecs.encode(encrypter.encrypt(pad(phrase)), 'base64').decode()

def pack_phrase(phrase):
    return codecs.encode(phrase, 'base64').decode()

def decrypt_phrase(phrase_string, secret):
    decrypter = AES.new(secret, AES.MODE_CBC, phrase_string[:16])
    return unpad(decrypter.decrypt(codecs.decode(phrase_string[16:], 'base64')))

def unpack_phrase(phrase_string):
    return codecs.decode(phrase_string, 'base64')

def encrypt_dictionary(the_dict, secret):
    iv = ''.join(random.choice(string.ascii_letters) for i in range(16))
    encrypter = AES.new(secret, AES.MODE_CBC, iv)
    return iv + codecs.encode(encrypter.encrypt(pad(pickle.dumps(pickleable_objects(the_dict)))), 'base64').decode()

def pack_dictionary(the_dict):
    return codecs.encode(pickle.dumps(pickleable_objects(the_dict)), 'base64').decode()

def decrypt_dictionary(dict_string, secret):
    decrypter = AES.new(secret, AES.MODE_CBC, dict_string[:16])
    return pickle.loads(unpad(decrypter.decrypt(codecs.decode(dict_string[16:], 'base64'))))

def unpack_dictionary(dict_string):
    return pickle.loads(codecs.decode(dict_string, 'base64'))

def get_unique_name(filename, secret):
    while True:
        newname = ''.join(random.choice(string.ascii_letters) for i in range(32))
        existing_key = UserDict.query.filter_by(key=newname).first()
        if existing_key:
            continue
        # cur = conn.cursor()
        # cur.execute("SELECT key from userdict where key=%s", [newname])
        # if cur.fetchone():
        #     #logmessage("Key already exists in database")
        #     continue
        new_user_dict = UserDict(key=newname, filename=filename, dictionary=encrypt_dictionary(fresh_dictionary(), secret))
        db.session.add(new_user_dict)
        db.session.commit()
        # cur.execute("INSERT INTO userdict (key, filename, dictionary) values (%s, %s, %s);", [newname, filename, codecs.encode(pickle.dumps(initial_dict.copy()), 'base64').decode()])
        # conn.commit()
        return newname

# def update_user_id(the_user_code):
#     if current_user.id is not None and the_user_code is not None:
#         cur = conn.cursor()
#         cur.execute("UPDATE userdict set user_id=%s where key=%s", [current_user.id, the_user_code])
#         conn.commit()
#     return
    
def get_attachment_info(the_user_code, question_number, filename, secret):
    the_user_dict = None
    existing_entry = Attachments.query.filter_by(key=the_user_code, question=question_number, filename=filename).first()
    if existing_entry and existing_entry.dictionary:
        #the_user_dict = pickle.loads(codecs.decode(existing_entry.dictionary, 'base64'))
        if existing_entry.encrypted:
            the_user_dict = decrypt_dictionary(existing_entry.dictionary, secret)
        else:
            the_user_dict = unpack_dictionary(existing_entry.dictionary)
    # cur = conn.cursor()
    # cur.execute("select dictionary from attachments where key=%s and question=%s and filename=%s", [the_user_code, question_number, filename])
    # for d in cur:
    #     if d[0]:
    #         the_user_dict = pickle.loads(codecs.decode(d[0], 'base64'))
    #     break
    # conn.commit()
    return the_user_dict

def update_attachment_info(the_user_code, the_user_dict, the_interview_status, secret, encrypt=True):
    #logmessage("Got to update_attachment_info")
    Attachments.query.filter_by(key=the_user_code, question=the_interview_status.question.number, filename=the_interview_status.question.interview.source.path).delete()
    db.session.commit()
    if encrypt:
        new_attachment = Attachments(key=the_user_code, dictionary=encrypt_dictionary(the_user_dict, secret), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=True)
    else:
        new_attachment = Attachments(key=the_user_code, dictionary=pack_dictionary(the_user_dict), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=False)
    db.session.add(new_attachment)
    db.session.commit()
    return

def fetch_user_dict(user_code, filename, secret):
    user_dict = None
    steps = 0
    encrypted = True
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('count')).filter(UserDict.key == user_code and UserDict.filename == filename).subquery()
    results = db.session.query(UserDict.dictionary, UserDict.encrypted, subq.c.count).join(subq, subq.c.indexno == UserDict.indexno)
    for d in results:
        if d.dictionary:
            if d.encrypted:
                user_dict = decrypt_dictionary(d.dictionary, secret)
            else:
                user_dict = unpack_dictionary(d.dictionary)
                encrypted = False
        if d.count:
            steps = d.count
        break
    return steps, user_dict, encrypted

def fetch_previous_user_dict(user_code, filename, secret):
    user_dict = None
    max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(UserDict.key == user_code and UserDict.filename == filename).scalar()
    if max_indexno is not None:
        UserDict.query.filter_by(indexno=max_indexno).delete()
        db.session.commit()
    return fetch_user_dict(user_code, filename, secret)

def advance_progress(user_dict):
    user_dict['_internal']['progress'] += 0.05*(100-user_dict['_internal']['progress'])
    return

def save_user_dict_key(user_code, filename):
    the_record = UserDictKeys.query.filter_by(key=user_code, filename=filename, user_id=current_user.id).first()
    if the_record:
        found = True
    else:
        found = False
    if not found:
        new_record = UserDictKeys(key=user_code, filename=filename, user_id=current_user.id)
        db.session.add(new_record)
        db.session.commit()
    return

def save_user_dict(user_code, user_dict, filename, secret, changed=False, encrypt=True):
    user_dict['_internal']['modtime'] = datetime.datetime.utcnow()
    if current_user.is_authenticated and not current_user.is_anonymous:
        the_user_id = current_user.id
    else:
        the_user_id = None
    if changed is True:
        if encrypt:
            new_record = UserDict(key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
        else:
            new_record = UserDict(key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
        db.session.add(new_record)
        db.session.commit()
    else:
        max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(UserDict.key == user_code and UserDict.filename == filename).scalar()
        if max_indexno is None:
            if encrypt:
                new_record = UserDict(key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
            else:
                new_record = UserDict(key=user_code, dictionary=pack_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=False)
            db.session.add(new_record)
            db.session.commit()
        else:
            for record in UserDict.query.filter_by(key=user_code, filename=filename, indexno=max_indexno).all():
                if encrypt:
                    record.dictionary = encrypt_dictionary(user_dict, secret)
                    record.encrypted = True
                else:
                    record.dictionary = pack_dictionary(user_dict)
                    record.encrypted = False                   
            db.session.commit()
    return

def reset_user_dict(user_code, filename):
    UserDict.query.filter_by(key=user_code, filename=filename).delete()
    db.session.commit()
    UserDictKeys.query.filter_by(key=user_code, filename=filename).delete()
    db.session.commit()
    for upload in Uploads.query.filter_by(key=user_code, yamlfile=filename).all():
        old_file = SavedFile(upload.indexno)
        old_file.delete()
    Uploads.query.filter_by(key=user_code, yamlfile=filename).delete()
    db.session.commit()
    Attachments.query.filter_by(key=user_code, filename=filename).delete()
    db.session.commit()
    SpeakList.query.filter_by(key=user_code, filename=filename).delete()
    db.session.commit()
    return

def get_new_file_number(user_code, file_name, yaml_file_name=None):
    new_upload = Uploads(key=user_code, filename=file_name, yamlfile=yaml_file_name)
    db.session.add(new_upload)
    db.session.commit()
    return new_upload.indexno
    # indexno = None
    # cur = conn.cursor()
    # cur.execute("INSERT INTO uploads (key, filename) values (%s, %s) RETURNING indexno", [user_code, file_name])
    # for d in cur:
    #     indexno = d[0]
    # conn.commit()
    # return (indexno)

def make_navbar(status, page_title, page_short_title, steps, show_login):
    navbar = """\
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
"""
    navbar += """\
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
"""
    if status.question.can_go_back and steps > 1:
        navbar += """\
          <span class="navbar-brand"><form style="inline-block" id="backbutton" method="POST"><input type="hidden" name="_back_one" value="1"><button class="dabackicon" type="submit"><i class="glyphicon glyphicon-chevron-left dalarge"></i></button></form></span>
"""
    navbar += """\
          <a href="#question" data-toggle="tab" class="navbar-brand"><span class="hidden-xs">""" + status.question.interview.get_title().get('full', page_title) + """</span><span class="visible-xs-block">""" + status.question.interview.get_title().get('short', page_short_title) + """</span></a>
          <a class="invisible" id="questionlabel" href="#question" data-toggle="tab">""" + word('Question') + """</a>
"""
    if len(status.helpText):
        if status.question.helptext is None:
            navbar += '          <a class="mynavbar-text" href="#help" id="helptoggle" data-toggle="tab">' + word('Help') + '</a>'
        else:
            navbar += '          <a class="mynavbar-text daactivetext" href="#help" id="helptoggle" data-toggle="tab">' + word('Help') + ' <i class="glyphicon glyphicon-star"></i></a>'
    navbar += """
        </div>
        <div class="collapse navbar-collapse" id="navbar-collapse">
          <ul class="nav navbar-nav navbar-left">
"""
    # if status.question.helptext is None:
    #     navbar += '<li><a href="#help" data-toggle="tab">' + word('Help') + "</a></li>\n"
    # else:
    #     navbar += '<li><a class="daactivetext" href="#help" data-toggle="tab">' + word('Help') + ' <i class="glyphicon glyphicon-star"></i>' + "</a></li>\n"
    if DEBUG:
        navbar += """\
            <li><a id="sourcetoggle" href="#source" data-toggle="collapse" aria-expanded="false" aria-controls="source">""" + word('Source') + """</a></li>
"""
    navbar += """\
          </ul>
          <ul class="nav navbar-nav navbar-right">
"""
    if 'menu_items' in status.extras:
        if type(status.extras['menu_items']) is not list:
            custom_menu += '<li>' + word("Error: menu_items is not a Python list") + '</li>'
        elif len(status.extras['menu_items']):
            custom_menu = ""
            for menu_item in status.extras['menu_items']:
                if not (type(menu_item) is dict and 'url' in menu_item and 'label' in menu_item):
                    custom_menu += '<li>' + word("Error: menu item is not a Python dict with keys of url and label") + '</li>'
                else:
                    custom_menu += '<li><a href="' + menu_item['url'] + '">' + menu_item['label'] + '</a></li>'
        else:
            custom_menu = False
    else:
        custom_menu = False
    if show_login:
        if current_user.is_anonymous:
            #logmessage("is_anonymous is " + str(current_user.is_anonymous))
            if custom_menu:
                navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '<span class="caret"></span></a><ul class="dropdown-menu">' + custom_menu + '<li><a href="' + url_for('user.login', next=url_for('interview_list')) + '">' + word('Sign in') + '</a></li></ul></li>' + "\n"
            else:
                navbar += '            <li><a href="' + url_for('user.login', next=url_for('interview_list')) + '">' + word('Sign in') + '</a></li>' + "\n"
        else:
            navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + current_user.email + '<span class="caret"></span></a><ul class="dropdown-menu">'
            if custom_menu:
                navbar += custom_menu
            if current_user.has_role('admin', 'developer'):
                navbar +='<li><a href="' + url_for('package_page') + '">' + word('Package Management') + '</a></li>'
                navbar +='<li><a href="' + url_for('logs') + '">' + word('Logs') + '</a></li>'
                navbar +='<li><a href="' + url_for('playground_page') + '">' + word('Playground') + '</a></li>'
                navbar +='<li><a href="' + url_for('utilities') + '">' + word('Utilities') + '</a></li>'
                if current_user.has_role('admin'):
                    navbar +='<li><a href="' + url_for('user_list') + '">' + word('User List') + '</a></li>'
                    navbar +='<li><a href="' + url_for('privilege_list') + '">' + word('Privileges List') + '</a></li>'
                    navbar +='<li><a href="' + url_for('config_page') + '">' + word('Configuration') + '</a></li>'
            navbar += '<li><a href="' + url_for('interview_list') + '">' + word('My Interviews') + '</a></li><li><a href="' + url_for('user_profile_page') + '">' + word('Profile') + '</a></li><li><a href="' + url_for('user.logout') + '">' + word('Sign out') + '</a></li></ul></li>'
    else:
        if custom_menu:
            navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '<span class="caret"></span></a><ul class="dropdown-menu">' + custom_menu + '<li><a href="' + url_for('exit') + '">' + word('Exit') + '</a></li></ul></li>' + "\n"
        else:
            navbar += '            <li><a href="' + url_for('exit') + '">' + word('Exit') + '</a></li>'
    navbar += """\
          </ul>
        </div>
      </div>
    </div>
"""
    return(navbar)

@app.context_processor
def utility_processor():
    def word(text):
        return docassemble.base.util.word(text)
    def random_social():
        return 'local$' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    return dict(random_social=random_social, word=word)

def delete_session():
    for key in ['i', 'uid', 'key_logged', 'action']:
        if key in session:
            del session[key]
    return

def reset_session(yaml_filename, secret):
    session['i'] = yaml_filename
    session['uid'] = get_unique_name(yaml_filename, secret)
    if 'key_logged' in session:
        del session['key_logged']
    if 'action' in session:
        del session['action']
    user_code = session['uid']
    #logmessage("User code is now " + str(user_code))
    user_dict = fresh_dictionary()
    return(user_code, user_dict)

def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url

@app.route('/speakfile', methods=['GET'])
def speak_file():
    audio_file = None
    filename = session['i']
    key = session['uid']
    encrypted = session.get('encrypted', False)
    question = request.args.get('question', None)
    question_type = request.args.get('type', None)
    file_format = request.args.get('format', None)
    the_language = request.args.get('language', None)
    the_dialect = request.args.get('dialect', None)
    secret = request.cookies.get('secret', None)
    if file_format not in ['mp3', 'ogg'] or not (filename and key and question and question_type and file_format and the_language and the_dialect):
        logmessage("Could not serve speak file because invalid or missing data was provided: filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    entry = SpeakList.query.filter_by(filename=filename, key=key, question=question, type=question_type, language=the_language, dialect=the_dialect).first()
    if not entry:
        logmessage("Could not serve speak file because no entry could be found in speaklist for filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    if not entry.upload:
        existing_entry = SpeakList.query.filter(SpeakList.phrase == entry.phrase, SpeakList.language == entry.language, SpeakList.dialect == entry.dialect, SpeakList.upload != None, SpeakList.encrypted == entry.encrypted).first()
        if existing_entry:
            logmessage("Found existing entry: " + str(existing_entry.id) + ".  Setting to " + str(existing_entry.upload))
            entry.upload = existing_entry.upload
            db.session.commit()
        else:
            if not VOICERSS_ENABLED:
                logmessage("Could not serve speak file because voicerss not enabled")
                abort(404)
            new_file_number = get_new_file_number(key, 'speak.mp3', yaml_file_name=filename)
            #phrase = codecs.decode(entry.phrase, 'base64')
            if entry.encrypted:
                phrase = decrypt_phrase(entry.phrase, secret)
            else:
                phrase = unpack_phrase(entry.phrase)
            url = "https://api.voicerss.org/?" + urllib.urlencode({'key': voicerss_config['key'], 'src': phrase, 'hl': str(entry.language) + '-' + str(entry.dialect)})
            logmessage("Retrieving " + url)
            audio_file = SavedFile(new_file_number, extension='mp3', fix=True)
            audio_file.fetch_url(url)
            if audio_file.size_in_bytes() > 100:
                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', audio_file.path + '.mp3']
                result = call(call_array)
                if result != 0:
                    logmessage("Failed to convert downloaded mp3 (" + path + ") to ogg")
                    abort(404)
                entry.upload = new_file_number
                audio_file.finalize()
                db.session.commit()
            else:
                logmessage("Download from voicerss (" + path + ") failed")
                abort(404)
    if not entry.upload:
        logmessage("Upload file number was not set")
        abort(404)
    if not audio_file:
        audio_file = SavedFile(entry.upload, extension='mp3', fix=True)
    the_path = audio_file.path + '.' + file_format
    if not os.path.isfile(the_path):
        logmessage("Could not serve speak file because file (" + the_path + ") not found")
        abort(404)
    return(send_file(the_path, mimetype=audio_mimetype_table[file_format]))

@app.route('/uploadedfile/<number>.<extension>', methods=['GET'])
def serve_uploaded_file_with_extension(number, extension):
    number = re.sub(r'[^0-9]', '', str(number))
    if S3_ENABLED:
        if not can_access_file_number(number):
            abort(404)
        the_file = SavedFile(number)
    else:
        file_info = get_info_from_file_number(number)
        if 'path' not in file_info:
            abort(404)
        else:
            if os.path.isfile(file_info['path'] + '.' + extension):
                extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
                return(send_file(file_info['path'] + '.' + extension, mimetype=mimetype))
            else:
                abort(404)

@app.route('/uploadedfile/<number>', methods=['GET'])
def serve_uploaded_file(number):
    number = re.sub(r'[^0-9]', '', str(number))
    file_info = get_info_from_file_number(number)
    #file_info = get_info_from_file_reference(number)
    if 'path' not in file_info:
        abort(404)
    else:
        #block_size = 4096
        #status = '200 OK'
        return(send_file(file_info['path'], mimetype=file_info['mimetype']))

@app.route('/uploadedpage/<number>/<page>', methods=['GET'])
def serve_uploaded_page(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    file_info = get_info_from_file_number(number)
    if 'path' not in file_info:
        abort(404)
    else:
        filename = file_info['path'] + 'page-' + str(page) + '.png'
        if os.path.isfile(filename):
            return(send_file(filename, mimetype='image/png'))
        else:
            abort(404)

@app.route('/uploadedpagescreen/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    file_info = get_info_from_file_number(number)
    if 'path' not in file_info:
        logmessage('no access to file number ' + str(number))
        abort(404)
    else:
        filename = file_info['path'] + 'screen-' + str(page) + '.png'
        if os.path.isfile(filename):
            return(send_file(filename, mimetype='image/png'))
        else:
            logmessage('path ' + filename + ' is not a file')
            abort(404)

def user_can_edit_package(pkgname=None, giturl=None):
    if pkgname is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(Package.name == pkgname)
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    if giturl is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(Package.giturl == giturl)
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    return(False)

class Object(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    pass

@app.route('/updatepackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package():
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    form = UpdatePackageForm(request.form, current_user)
    action = request.args.get('action', None)
    target = request.args.get('package', None)
    if action is not None and target is not None:
        package_list, package_auth = get_package_info()
        the_package = None
        for package in package_list:
            if package.package.name == target:
                the_package = package
                break
        if the_package is not None:
            if action == 'uninstall' and the_package.can_uninstall:
                uninstall_package(target)
            elif action == 'update' and the_package.can_update:
                existing_package = Package.query.filter_by(name=target, active=True).first()
                if existing_package is not None:
                    if existing_package.type == 'git' and existing_package.giturl is not None:
                        install_git_package(target, existing_package.giturl)
                    elif existing_package.type == 'pip':
                        install_pip_package(existing_package.name, existing_package.limitation)
    if request.method == 'POST' and form.validate_on_submit():
        if 'zipfile' in request.files and request.files['zipfile'].filename:
            try:
                the_file = request.files['zipfile']
                filename = secure_filename(the_file.filename)
                pkgname = re.sub(r'\.zip$', r'', filename)
                pkgname = re.sub(r'docassemble-', 'docassemble.', pkgname)
                if user_can_edit_package(pkgname=pkgname):
                    file_number = get_new_file_number(session.get('uid', None), filename)
                    saved_file = SavedFile(file_number, extension='zip', fix=True)
                    zippath = saved_file.path
                    the_file.save(zippath)
                    saved_file.save()
                    saved_file.finalize()
                    #zippath += '.zip'
                    #commands = ['install', zippath, '--egg', '--no-index', '--src=' + tempfile.mkdtemp(), '--log-file=' + pip_log.name, '--upgrade', "--install-option=--user"]
                    install_zip_package(pkgname, file_number)
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            except Exception as errMess:
                flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        else:
            if form.giturl.data:
                giturl = form.giturl.data.strip()
                packagename = re.sub(r'.*/', '', giturl)
                if user_can_edit_package(giturl=giturl) and user_can_edit_package(pkgname=packagename):
                    #commands = ['install', '--egg', '--src=' + temp_directory, '--log-file=' + pip_log.name, '--upgrade', "--install-option=--user", 'git+' + giturl + '.git#egg=' + packagename]
                    install_git_package(packagename, giturl)
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            elif form.pippackage.data:
                m =re.match(r'([^>=<]+)([>=<]+.+)', form.pippackage.data)
                if m:
                    packagename = m.group(1)
                    limitation = m.group(2)
                else:
                    packagename = form.pippackage.data
                    limitation = None
                packagename = re.sub(r'[^A-Za-z0-9\_]', '', packagename)
                if user_can_edit_package(pkgname=packagename):
                    install_pip_package(packagename, limitation)
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            else:
                flash(word('You need to either supply a Git URL or upload a file.'), 'error')
    package_list, package_auth = get_package_info()
    form.pippackage.data = None
    form.giturl.data = None
    return render_template('pages/update_package.html', form=form, package_list=package_list), 200

def uninstall_package(packagename):
    logmessage("uninstall_package: " + packagename)
    existing_package = Package.query.filter_by(name=packagename, active=True).first()
    if existing_package is None:
        flash(word("Package did not exist"), 'error')
        return
    the_upload_number = existing_package.upload
    the_package_type = existing_package.type
    for package in Package.query.filter_by(name=packagename, active=True).all():
        package.active = False
    db.session.commit()
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    if ok:
        if the_package_type == 'zip' and the_upload_number is not None:
            SavedFile(the_upload_number).delete()
        trigger_update(except_for=hostname)
        restart_wsgi()
        flash(word("Uninstall successful"), 'success')
    else:
        flash(word("Uninstall not successful"), 'error')
    flash('pip log:  ' + str(logmessages), 'info')
    logmessage(logmessages)
    logmessage("uninstall_package: done")
    return

def install_zip_package(packagename, file_number):
    logmessage("install_zip_package: " + packagename + " " + str(file_number))
    existing_package = Package.query.filter_by(name=packagename, active=True).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, upload=file_number, active=True, type='zip', version=1)
        db.session.add(package_auth)
        db.session.add(package_entry)
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None and existing_package.upload != file_number:
            SavedFile(existing_package.upload).delete()
        existing_package.upload = file_number
        existing_package.active = True
        existing_package.limitation = None
        existing_package.type = 'zip'
        existing_package.version += 1
    db.session.commit()
    #logmessage("Going into check for updates now")
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    #logmessage("Returned from check for updates")
    #logmessage('pip log: ' + str(logmessages), 'info')
    if ok:
        trigger_update(except_for=hostname)
        restart_wsgi()
        flash(word("Install successful"), 'success')
    else:
        flash(word("Install not successful"), 'error')
    flash('pip log: ' + str(logmessages), 'info')
    # pip_log = tempfile.NamedTemporaryFile()
    # commands = ['install', '--quiet', '--egg', '--no-index', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, zippath]
    # returnval = pip.main(commands)
    # if returnval > 0:
    #     with open(pip_log.name) as x:
    #         logfilecontents = x.read()
    #         flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + '</pre>', 'error')
    return

def install_git_package(packagename, giturl):
    logmessage("install_git_package: " + packagename + " " + str(giturl))
    if Package.query.filter_by(name=packagename, active=True).first() is None and Package.query.filter_by(giturl=giturl, active=True).first() is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, giturl=giturl, package_auth=package_auth, version=1, active=True, type='git')
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        package_entry = Package.query.filter_by(name=packagename).first()
        if package_entry is not None:
            if package_entry.type == 'zip' and package_entry.upload is not None:
                SavedFile(package_entry.upload).delete()
            package_entry.version += 1
            package_entry.giturl = giturl
            package_entry.upload = None
            package_entry.limitation = None
            package_entry.type = 'git'
            db.session.commit()
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    if ok:
        trigger_update(except_for=hostname)
        restart_wsgi()
        flash(word("Install successful"), 'success')
    else:
        flash(word("Install not successful"), 'error')
    flash('pip log: ' + str(logmessages), 'info')
    # pip_log = tempfile.NamedTemporaryFile()
    # commands = ['install', '--quiet', '--egg', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + giturl + '.git#egg=' + packagename]
    # returnval = pip.main(commands)
    # if returnval > 0:
    #     with open(pip_log.name) as x: logfilecontents = x.read()
    #     flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + "</pre>", 'error')
    return

def install_pip_package(packagename, limitation):
    existing_package = Package.query.filter_by(name=packagename, active=True).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, limitation=limitation, type='pip')
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None:
            SavedFile(existing_package.upload).delete()
        existing_package.version += 1
        existing_package.type = 'pip'
        existing_package.limitation = limitation
        existing_package.giturl = None
        existing_package.upload = None
        db.session.commit()
    ok, logmessages = docassemble.webapp.update.check_for_updates()
    if ok:
        trigger_update(except_for=hostname)
        restart_wsgi()
        flash(word("Install successful"), 'success')
    else:
        flash(word("Install not successful"), 'error')
    flash('pip log: ' + str(logmessages), 'info')
    # pip_log = tempfile.NamedTemporaryFile()
    # commands = ['install', '--quiet', '--egg', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + giturl + '.git#egg=' + packagename]
    # returnval = pip.main(commands)
    # if returnval > 0:
    #     with open(pip_log.name) as x: logfilecontents = x.read()
    #     flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + "</pre>", 'error')
    return

def get_package_info():
    if current_user.has_role('admin'):
        is_admin = True
    else:
        is_admin = False
    package_list = list()
    package_auth = dict()
    for auth in PackageAuth.query.all():
        if auth.package_id not in package_auth:
            package_auth[auth.package_id] = dict()
        package_auth[auth.package_id][auth.user_id] = auth.authtype
    for package in Package.query.filter_by(active=True).order_by(Package.name).all():
        if package.type is not None:
            if package.type == 'zip':
                can_update = False
            else:
                can_update = True
            if is_admin or (package.id in package_auth and current_user.id in package_auth[package.id]):
                can_uninstall = True
            else:
                can_uninstall = False
            if package.core:
                can_uninstall = False
                can_update = is_admin
            package_list.append(Object(package=package, can_update=can_update, can_uninstall=can_uninstall))
    return package_list, package_auth

@app.route('/createplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_playground_package():
    form = CreatePlaygroundPackageForm(request.form, current_user)
    current_package = request.args.get('package', None)
    do_install = request.args.get('install', False)
    from_playground = request.args.get('from_playground', False)
    area = dict()
    area['playgroundpackages'] = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    file_list = dict()
    file_list['playgroundpackages'] = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f))])
    the_choices = list()
    for file_option in file_list['playgroundpackages']:
        the_choices.append((file_option, file_option))
    form.name.choices = the_choices
    if request.method == 'POST':
        if form.validate():
            current_package = form.name.data
            #flash("form validated", 'success')
        else:
            the_error = ''
            for error in form.name.errors:
                the_error += str(error)
            flash("form did not validate with " + str(form.name.data) + " " + str(the_error) + " among " + str(form.name.choices), 'error')
    if current_package is not None:
        pkgname = re.sub(r'^docassemble-', r'', current_package)
        if not user_can_edit_package(pkgname='docassemble.' + pkgname):
            flash(word('Sorry, that package name is already in use by someone else'), 'error')
            current_package = None
    if current_package is not None and current_package not in file_list['playgroundpackages']:
        flash(word('Sorry, that package name does not exist in the playground'), 'error')
        current_package = None
    if current_package is not None:
        section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundmodules': 'modules'}
        for sec in ['playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundmodules']:
            area[sec] = SavedFile(current_user.id, fix=True, section=sec)
            file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f))])
        if os.path.isfile(os.path.join(area['playgroundpackages'].directory, current_package)):
            filename = os.path.join(area['playgroundpackages'].directory, current_package)
            info = dict()
            with open(filename, 'rU') as fp:
                content = fp.read().decode('utf8')
                info = yaml.load(content)
            for field in ['dependencies', 'interview_files', 'template_files', 'module_files', 'static_files']:
                if field not in info:
                    info[field] = list()
            for package in ['docassemble', 'docassemble.base']:
                if package not in info['dependencies']:
                    info['dependencies'].append(package)
            author_info = dict()
            author_info['author name and email'] = name_of_user(current_user, include_email=True)
            author_info['author name'] = name_of_user(current_user)
            author_info['author email'] = current_user.email
            author_info['first name'] = current_user.first_name
            author_info['last name'] = current_user.last_name
            author_info['id'] = current_user.id
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            zip_file = docassemble.webapp.files.make_package_zip(pkgname, info, author_info)
            saved_file.copy_from(zip_file.name)
            saved_file.finalize()
            existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).first()
            if existing_package is None:
                package_auth = PackageAuth(user_id=current_user.id)
                package_entry = Package(name='docassemble.' + pkgname, package_auth=package_auth, upload=file_number, type='zip')
                db.session.add(package_auth)
                db.session.add(package_entry)
                #sys.stderr.write("Ok, did the commit\n")
            else:
                existing_package.upload = file_number
                existing_package.active = True
                existing_package.version += 1
            db.session.commit()
            if do_install:
                install_zip_package('docassemble.' + pkgname, file_number)
                return redirect(url_for('playground_packages', file=current_package))
            else:
                resp = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
                return resp
    return render_template('pages/create_playground_package.html', form=form, current_package=current_package, package_names=file_list['playgroundpackages']), 200

@app.route('/createpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_package():
    form = CreatePackageForm(request.form, current_user)
    if request.method == 'POST' and form.validate():
        pkgname = re.sub(r'^docassemble-', r'', form.name.data)
        if not user_can_edit_package(pkgname='docassemble.' + pkgname):
            flash(word('Sorry, that package name is already in use by someone else'), 'error')
        else:
            #foobar = Package.query.filter_by(name='docassemble_' + pkgname).first()
            #sys.stderr.write("this is it: " + str(foobar) + "\n")
            initpy = """\
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

"""
            licensetext = """\
The MIT License (MIT)

"""
            licensetext += 'Copyright (c) ' + str(datetime.datetime.now().year) + ' ' + unicode(current_user.first_name) + " " + unicode(current_user.last_name) + """

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
            readme = '# docassemble.' + str(pkgname) + "\n\nA docassemble extension.\n\n## Author\n\n" + name_of_user(current_user, include_email=True) + "\n"
            setuppy = """\
#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
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
                    stack.append((fn, prefix + name + '/', package))
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
      version='0.1',
      description=('A docassemble extension.'),
      author=""" + repr(name_of_user(current_user)) + """,
      author_email=""" + repr(current_user.email) + """,
      license='MIT',
      url='http://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      zip_safe = False,
      package_data=find_package_data(where='docassemble/""" + str(pkgname) + """/', package='docassemble.""" + str(pkgname) + """'),
     )

"""
            questionfiletext = """\
---
metadata:
  description: |
    Insert description of question file here.
  authors:
    - name: """ + unicode(current_user.first_name) + " " + unicode(current_user.last_name) + """
      organization: """ + unicode(current_user.organization) + """
  revision_date: """ + time.strftime("%Y-%m-%d") + """
---
mandatory: true
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

If you want to use non-standard document templates with pandoc,
put template files in this directory.
"""
            staticreadme = """\
# Static file directory

If you want to make files available in the web app, put them in
this directory.
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
# mandatory: true
# question: |
#   When I eat some ${ favorite_fruit.name }, 
#   I think, "${ favorite_fruit.eat() }"
# ---
# question: What is the best fruit?
# fields:
#   - Fruit Name: favorite_fruit.name
# ---
from docassemble.base.core import DAObject

class Fruit(DAObject):
    def eat(self):
        return "Yum, that " + self.name + " was good!"
"""
            directory = tempfile.mkdtemp()
            packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
            questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
            templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
            staticdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'static')
            os.makedirs(questionsdir)
            os.makedirs(templatesdir)
            os.makedirs(staticdir)
            with open(os.path.join(packagedir, 'README.md'), 'a') as the_file:
                the_file.write(readme)
            with open(os.path.join(packagedir, 'LICENSE'), 'a') as the_file:
                the_file.write(licensetext)
            with open(os.path.join(packagedir, 'setup.py'), 'a') as the_file:
                the_file.write(setuppy)
            with open(os.path.join(packagedir, 'docassemble', '__init__.py'), 'a') as the_file:
                the_file.write(initpy)
            with open(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), 'a') as the_file:
                the_file.write('')
            with open(os.path.join(packagedir, 'docassemble', pkgname, 'objects.py'), 'a') as the_file:
                the_file.write(objectfile)
            with open(os.path.join(templatesdir, 'README.md'), 'a') as the_file:
                the_file.write(templatereadme)
            with open(os.path.join(staticdir, 'README.md'), 'a') as the_file:
                the_file.write(staticreadme)
            with open(os.path.join(questionsdir, 'questions.yml'), 'a') as the_file:
                the_file.write(questionfiletext)
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            #archive = tempfile.NamedTemporaryFile(delete=False)
            zf = zipfile.ZipFile(saved_file.path, mode='w')
            trimlength = len(directory) + 1
            for root, dirs, files in os.walk(packagedir):
                for file in files:
                    thefilename = os.path.join(root, file)
                    zf.write(thefilename, thefilename[trimlength:])
            zf.close()
            saved_file.save()
            saved_file.finalize()
            existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).first()
            if existing_package is None:
                package_auth = PackageAuth(user_id=current_user.id)
                package_entry = Package(name='docassemble.' + pkgname, package_auth=package_auth, upload=file_number, type='zip')
                db.session.add(package_auth)
                db.session.add(package_entry)
                #sys.stderr.write("Ok, did the commit\n")
            else:
                existing_package.upload = file_number
                existing_package.active = True
                existing_package.version += 1
            db.session.commit()
            resp = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
            return resp
    return render_template('pages/create_package.html', form=form), 200

def name_of_user(user, include_email=False):
    output = ''
    if user.first_name:
        output += ''
        if user.last_name:
            output += ' '
    if user.last_name:
        output += user.last_name
    if include_email and user.email:
        if output:
            output += ', '
        output += user.email
    return output

@app.route('/config', methods=['GET', 'POST'])
@login_required
@roles_required(['admin'])
def config_page():
    form = ConfigForm(request.form, current_user)
    content = None
    ok = True
    if request.method == 'POST':
        if form.submit.data and form.config_content.data:
            try:
                yaml.load(form.config_content.data)
            except Exception as errMess:
                ok = False
                content = form.config_content.data
                errMess = word("Configuration not updated.  There was a syntax error in the configuration YAML.") + '<pre>' + str(errMess) + '</pre>'
                flash(str(errMess), 'error')
                logmessage(str(errMess))
            if ok:
                if S3_ENABLED:
                    key = s3.get_key('config.yml')
                    key.set_contents_from_string(form.config_content.data)
                with open(daconfig['config_file'], 'w') as fp:
                    fp.write(form.config_content.data.encode('utf8'))
                    flash(word('The configuration file was saved.'), 'success')
                restart_wsgi()
                return redirect(url_for('interview_list'))
        elif form.cancel.data:
            flash(word('Configuration not updated.'), 'info')
            return redirect(url_for('index'))
        else:
            flash(word('Configuration not updated.  There was an error.'), 'error')
            return redirect(url_for('index'))
    if ok:
        with open(daconfig['config_file'], 'rU') as fp:
            content = fp.read().decode('utf8')
    if content is None:
        abort(404)
    return render_template('pages/config.html', extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    <script>\n      daTextArea=document.getElementById("config_content");\n      daTextArea.value = ' + json.dumps(content) + ';\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", tabSize: 2, tabindex: 70, autofocus: true, lineNumbers: true});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n    </script>'), form=form), 200

def flash_as_html(message, message_type="info"):
    output = """
        <div class="row">
          <div class="col-sm-7 col-md-6 col-lg-5 col-centered">
            <div class="alert alert-""" + str(message_type) + """"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>""" + str(message) + """</div>
          </div>
        </div>
"""
    return output

def make_example_html(examples, first_id, example_html, data_dict):
    example_html.append('          <ul class="nav nav-pills nav-stacked example-list example-hidden">\n')
    for example in examples:
        if 'list' in example:
            example_html.append('          <li><a class="example-heading">' + example['title'] + '</a>')
            make_example_html(example['list'], first_id, example_html, data_dict)
            example_html.append('          </li>')
            continue
        #logmessage("Doing example with id " + str(example['id']))
        if len(first_id) == 0:
            first_id.append(example['id'])
        example_html.append('            <li><a class="example-link" data-example="' + example['id'] + '">' + example['title'] + '</a></li>')
        data_dict[example['id']] = example
    example_html.append('          </ul>')

@app.route('/playgroundstatic/<userid>/<filename>', methods=['GET'])
def playground_static(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundstatic')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        return(send_file(filename, mimetype=str(mimetype)))
    abort(404)

@app.route('/playgroundtemplate/<userid>/<filename>', methods=['GET'])
def playground_template(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundtemplate')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        return(send_file(filename, mimetype=str(mimetype)))
    abort(404)

@app.route('/playgroundfiles', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_files():
    form = PlaygroundFilesForm(request.form, current_user)
    formtwo = PlaygroundFilesEditForm(request.form, current_user)
    section = request.args.get('section', 'template')
    the_file = request.args.get('file', '')
    scroll = False
    if the_file:
        scroll = True
    if request.method == 'GET':
        is_new = request.args.get('new', False)
    else:
        is_new = False
    if is_new:
        scroll = True
        the_file = ''
    if request.method == 'POST':
        if (form.section.data):
            section = form.section.data
        if (formtwo.file_name.data):
            the_file = formtwo.file_name.data
            the_file = re.sub(r'[^A-Za-z0-9\-\_\.]+', '_', the_file)
    if section not in ("template", "static", "modules", "packages"):
        section = "template"
    area = SavedFile(current_user.id, fix=True, section='playground' + section)
    if request.args.get('delete', False):
        argument = re.sub(r'[^A-Za-z0-9\-\_\.]', '', request.args.get('delete'))
        if argument:
            filename = os.path.join(area.directory, argument)
            if os.path.exists(filename):
                os.remove(filename)
                area.finalize()
                flash(word("Deleted file: ") + argument, "success")
                return redirect(url_for('playground_files', section=section))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.args.get('convert', False):
        argument = re.sub(r'[^A-Za-z0-9\-\_\.]', '', request.args.get('convert'))
        if argument:
            filename = os.path.join(area.directory, argument)
            if os.path.exists(filename):
                to_file = os.path.splitext(argument)[0] + '.md'
                to_path = os.path.join(area.directory, to_file)
                if not os.path.exists(to_path):
                    extension, mimetype = get_ext_and_mimetype(argument)
                    if (mimetype and mimetype in convertible_mimetypes):
                        the_format = convertible_mimetypes[mimetype]
                    elif extension and extension in convertible_extensions:
                        the_format = convertible_extensions[extension]
                    else:
                        flash(word("File format not understood: ") + argument, "error")
                        return redirect(url_for('playground_files', section=section))
                    result = word_to_markdown(filename, the_format)
                    if result is None:
                        flash(word("File could not be converted: ") + argument, "error")
                        return redirect(url_for('playground_files', section=section))
                    shutil.copyfile(result.name, to_path)
                    flash(word("Created new Markdown file called ") + to_file + word("."), "success")
                    area.finalize()
                    return redirect(url_for('playground_files', section=section, file=to_file))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.method == 'POST':
        if 'uploadfile' in request.files and request.files['uploadfile'].filename:
            try:
                up_file = request.files['uploadfile']
                filename = secure_filename(up_file.filename)
                filename = re.sub(r'[^A-Za-z0-9\-\_\.]+', '_', filename)
                filename = os.path.join(area.directory, filename)
                up_file.save(filename)
                area.finalize()
            except Exception as errMess:
                flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        if formtwo.delete.data:
            if the_file != '':
                filename = os.path.join(area.directory, the_file)
                if os.path.exists(filename):
                    os.remove(filename)
                    area.finalize()
                    flash(word("Deleted file: ") + the_file, "success")
                    return redirect(url_for('playground_files', section=section))
                else:
                    flash(word("File not found: ") + the_file, "error")            
        if formtwo.submit.data and formtwo.file_content.data:
            if the_file != '':
                if formtwo.original_file_name.data and formtwo.original_file_name.data != the_file:
                    old_filename = os.path.join(area.directory, formtwo.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                filename = os.path.join(area.directory, the_file)
                with open(filename, 'w') as fp:
                    fp.write(formtwo.file_content.data.encode('utf8'))
                the_time = time.strftime('%H:%M:%S %Z', time.localtime())
                area.finalize()
                flash(str(the_file) + word(' was saved at') + ' ' + the_time + '.', 'success')
                if section == 'modules':
                    restart_wsgi()
                return redirect(url_for('playground_files', section=section, file=the_file))
            else:
                flash(word('You need to type in a name for the file'), 'error')                
    files = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    editable_files = list()
    convertible_files = list()
    mode = "yaml"
    for a_file in files:
        extension, mimetype = get_ext_and_mimetype(a_file)
        if (mimetype and mimetype in ok_mimetypes) or (extension and extension in ok_extensions):
            editable_files.append(a_file)
    for a_file in files:
        extension, mimetype = get_ext_and_mimetype(a_file)
        b_file = os.path.splitext(a_file)[0] + '.md'
        if b_file not in editable_files and ((mimetype and mimetype in convertible_mimetypes) or (extension and extension in convertible_extensions)):
            convertible_files.append(a_file)
    if request.method == 'GET' and not the_file and not is_new:
        if len(editable_files):
            the_file = editable_files[0]
        else:
            if section == 'modules':
                the_file = 'test.py'
            else:
                the_file = 'test.md'
    if the_file != '':
        extension, mimetype = get_ext_and_mimetype(the_file)
        if (mimetype and mimetype in ok_mimetypes):
            mode = ok_mimetypes[mimetype]
        elif (extension and extension in ok_extensions):
            mode = ok_extensions[extension]
    formtwo.original_file_name.data = the_file
    formtwo.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(area.directory, the_file)):
        filename = os.path.join(area.directory, the_file)
    else:
        filename = None
    if filename is not None:
        area.finalize()
        with open(filename, 'rU') as fp:
            content = fp.read().decode('utf8')
    elif formtwo.file_content.data:
        content = formtwo.file_content.data
    else:
        content = ''
    if (section == "template"):
        header = word("Templates")
        description = 'Add files here that you want want to include in your interviews using "content file," "initial yaml," "additional yaml," "template file," "rtf template file," "pdf template file," or "docx reference file."'
        upload_header = word("Upload a template file")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "static"):
        header = word("Static files")
        description = 'Add files here that you want to include in your interviews with "images," "image sets," "[FILE]" or "url_of()."'
        upload_header = word("Upload a static file")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "modules"):
        header = word("Modules")
        upload_header = None
        edit_header = None
        description = Markup("""To use this in an interview, write a <code>modules</code> block that refers to this module using Python's syntax for specifying a "relative import" of a module (i.e., prefix the module name with a period).""" + highlight('---\nmodules:\n  - .' + re.sub(r'\.py$', '', the_file) + '\n---', YamlLexer(), HtmlFormatter()))
        after_text = None
    if scroll:
        extra_command = """\
      if ($("#file_name").val().length > 0){
        daCodeMirror.focus();
      }
      else{
        $("#file_name").focus()
      }
      scrollBottom();\n"""
    else:
        extra_command = ""
    return render_template('pages/playgroundfiles.html', extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/" + mode + "/" + mode + ".js") + '"></script>\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this file?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("file_content");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "' + mode + '", tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#formtwo").trigger("checkform.areYouSure");});\n      $("#formtwo").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#formtwo").bind("submit", function(){daCodeMirror.save(); $("#formtwo").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n      function scrollBottom(){$("html, body").animate({ scrollTop: $(document).height() }, "slow");}\n' + extra_command + '    </script>'), header=header, upload_header=upload_header, edit_header=edit_header, description=description, form=form, files=files, section=section, userid=current_user.id, editable_files=editable_files, convertible_files=convertible_files, formtwo=formtwo, current_file=the_file, content=content, after_text=after_text, is_new=str(is_new)), 200

@app.route('/playgroundpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_packages():
    form = PlaygroundPackagesForm(request.form, current_user)
    the_file = request.args.get('file', '')
    scroll = False
    package_list, package_auth = get_package_info()
    package_names = sorted([package.package.name for package in package_list])
    for default_package in ['docassemble', 'docassemble.base', 'docassemble.webapp']:
        if default_package in package_names:
            package_names.remove(default_package)
    # if the_file:
    #     scroll = True
    if request.method == 'GET':
        is_new = request.args.get('new', False)
    else:
        is_new = False
    if is_new:
        # scroll = True
        the_file = ''
    area = dict()
    file_list = dict()
    section_name = {'playground': 'Interview files', 'playgroundpackages': 'Packages', 'playgroundtemplate': 'Template files', 'playgroundstatic': 'Static files', 'playgroundmodules': 'Modules'}
    section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundmodules': 'modules'}
    section_field = {'playground': form.interview_files, 'playgroundtemplate': form.template_files, 'playgroundstatic': form.static_files, 'playgroundmodules': form.module_files}
    for sec in ['playground', 'playgroundpackages', 'playgroundtemplate', 'playgroundstatic', 'playgroundmodules']:
        area[sec] = SavedFile(current_user.id, fix=True, section=sec)
        file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f))])
    for sec, field in section_field.iteritems():
        the_list = []
        for item in file_list[sec]:
            the_list.append((item, item))
        field.choices = the_list
    the_list = []
    for item in package_names:
        the_list.append((item, item))
    form.dependencies.choices = the_list
    validated = False
    if request.method == 'POST' and form.validate():
        the_file = form.file_name.data
        validated = True
    the_file = re.sub(r'[^A-Za-z0-9\-\_\.]+', '-', the_file)
    the_file = re.sub(r'^docassemble-', r'', the_file)
    if not user_can_edit_package(pkgname='docassemble.' + the_file):
        flash(word('Sorry, that package name,') + the_file + word(', is already in use by someone else'), 'error')
        the_file = ''
    if the_file == '' and len(file_list['playgroundpackages']) and not is_new:
        the_file = file_list['playgroundpackages'][0]
    old_info = dict()
    if request.method == 'GET' and the_file != '':
        if the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
            filename = os.path.join(area['playgroundpackages'].directory, the_file)
            with open(filename, 'rU') as fp:
                content = fp.read().decode('utf8')
                old_info = yaml.load(content)
                if type(old_info) is dict:
                    for field in ['license', 'description', 'version', 'url', 'readme']:
                        if field in old_info:
                            form[field].data = old_info[field]
                        else:
                            form[field].data = ''
                    for field in ['dependencies', 'interview_files', 'template_files', 'module_files', 'static_files']:
                        if field in old_info and type(old_info[field]) is list and len(old_info[field]):
                            form[field].data = old_info[field]
        else:
            filename = None
    if request.method == 'POST' and validated:
        if form.delete.data and the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
            os.remove(os.path.join(area['playgroundpackages'].directory, the_file))
            area['playgroundpackages'].finalize()
            flash(word("Deleted package"), "success")
            return redirect(url_for('playground_packages'))
        new_info = dict()
        for field in ['license', 'description', 'version', 'url', 'readme', 'dependencies', 'interview_files', 'template_files', 'module_files', 'static_files']:
            new_info[field] = form[field].data
        #logmessage("found " + str(new_info))
        if form.submit.data or form.download.data or form.install.data:
            if the_file != '':
                area['playgroundpackages'].finalize()
                if form.original_file_name.data and form.original_file_name.data != the_file:
                    old_filename = os.path.join(area['playgroundpackages'].directory, form.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                filename = os.path.join(area['playgroundpackages'].directory, the_file)
                with open(filename, 'w') as fp:
                    the_yaml = yaml.safe_dump(new_info, default_flow_style=False, default_style = '|')
                    fp.write(the_yaml.encode('utf8'))
                area['playgroundpackages'].finalize()
                if form.download.data:
                    return redirect(url_for('create_playground_package', package=the_file))
                if form.install.data:
                    return redirect(url_for('create_playground_package', package=the_file, install=True))
                the_time = time.strftime('%H:%M:%S %Z', time.localtime())
                flash(word('The package information was saved.'), 'success')
    files = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f))])
    editable_files = list()
    mode = "yaml"
    for a_file in files:
        editable_files.append(a_file)
    if request.method == 'GET' and not the_file and not is_new:
        if len(editable_files):
            the_file = editable_files[0]
        else:
            the_file = ''
    form.original_file_name.data = the_file
    form.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
        filename = os.path.join(area['playgroundpackages'].directory, the_file)
    else:
        filename = None
    header = word("Packages")
    upload_header = None
    edit_header = None
    description = Markup("""Describe your package and choose the files from your Playground that will go into it.""")
    after_text = None
    if scroll:
        extra_command = "      scrollBottom();\n"
    else:
        extra_command = ""
    return render_template('pages/playgroundpackages.html', extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/markdown/markdown.js") + '"></script>\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this package?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("readme");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "markdown", tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#form").trigger("checkform.areYouSure");});\n      $("#form").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#form").bind("submit", function(){daCodeMirror.save(); $("#form").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n      function scrollBottom(){$("html, body").animate({ scrollTop: $(document).height() }, "slow");}\n' + extra_command + '    </script>'), header=header, upload_header=upload_header, edit_header=edit_header, description=description, form=form, files=files, file_list=file_list, userid=current_user.id, editable_files=editable_files, current_file=the_file, after_text=after_text, section_name=section_name, section_sec=section_sec, section_field=section_field, package_names=package_names), 200

def public_method(method, the_class):
    if isinstance(method, types.MethodType) and method.__name__ != 'init' and not method.__name__.startswith('_') and method.__name__ in the_class.__dict__:
        return True
    return False

def noquote(string):
    if string is None:
        return string
    string = noquote_match.sub('&quot;', string)
    string = lt_match.sub('&lt;', string)
    string = gt_match.sub('&gt;', string)
    string = amp_match.sub('&amp;', string)
    return string
    # if string is None:
    #     return None
    # newstring = json.dumps(string.replace('\n', ' ').rstrip())
    # return newstring[1:-1]

def infobutton(title):
    docstring = ''
    if 'doc' in title_documentation[title]:
        docstring += noquote(title_documentation[title]['doc']) + "<br>"
    if 'url' in title_documentation[title]:
        docstring += "<a target='_blank' href='" + title_documentation[title]['url'] + "'>" + word("View documentation") + "</a>"
    return '&nbsp;<a class="daquestionsign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + docstring + '" title="' + word("Help") + '" data-selector="true" data-title="' + noquote(title_documentation[title].get('title', title)) + '"><i class="glyphicon glyphicon-question-sign"></i></a>'
    
def get_vars_in_use(interview, interview_status):
    user_dict = fresh_dictionary()
    has_no_endpoint = False
    try:
        interview.assemble(user_dict, interview_status)
        has_error = False
    except Exception as errmess:
        has_error = True
        error_message = str(errmess)
        error_type = type(errmess)
        logmessage("Failed assembly with error type " + str(error_type) + " and message: " + error_message)
    fields_used = set()
    names_used = set()
    names_used.update(interview.names_used)
    for question in interview.questions_list:
        names_used.update(question.mako_names)
        names_used.update(question.names_used)
        names_used.update(question.fields_used)
        fields_used.update(question.fields_used)
    for val in interview.questions:
        names_used.add(val)
        fields_used.add(val)
    functions = set()
    modules = set()
    classes = set()
    name_info = copy.deepcopy(base_name_info)
    area = SavedFile(current_user.id, fix=True, section='playgroundtemplate')
    templates = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundstatic')
    static = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundmodules')
    avail_modules = sorted([re.sub(r'.py$', '', f) for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    for val in user_dict:
        #logmessage("Found val " + str(val) + " of type " + str(type(user_dict[val])))
        if type(user_dict[val]) is types.FunctionType:
            functions.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val) + '()', 'tag': str(val) + str(inspect.formatargspec(*inspect.getargspec(user_dict[val])))}
        elif type(user_dict[val]) is types.ModuleType:
            modules.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val)}
        # elif type(user_dict[val]) is types.ClassType:
        #     classes.add(val)
        #     name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val)}
        elif type(user_dict[val]) is types.TypeType or type(user_dict[val]) is types.ClassType:
            classes.add(val)
            bases = list()
            for x in list(user_dict[val].__bases__):
                if x.__name__ != 'DAObject':
                    bases.append(x.__name__)
            methods = inspect.getmembers(user_dict[val], predicate=lambda x: public_method(x, user_dict[val]))
            method_list = list()
            for name, value in methods:
                method_list.append({'insert': '.' + str(name) + '()', 'name': str(name), 'doc': noquote(inspect.getdoc(value)), 'tag': '.' + str(name) + str(inspect.formatargspec(*inspect.getargspec(value)))})
            #logmessage("Defining name_info for " + str(val))
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val), 'bases': bases, 'methods': method_list}
    for val in docassemble.base.util.pickleable_objects(user_dict):
        names_used.add(val)
        if val not in name_info:
            name_info[val] = dict()
        #name_info[val]['type'] = type(user_dict[val]).__name__
        name_info[val]['type'] = user_dict[val].__class__.__name__
    for var in base_name_info:
        if base_name_info[var]['show']:
            names_used.add(var)
    names_used = set([i for i in names_used if not extraneous_var.search(i)])
    for var in ['_internal']:
        names_used.discard(var)
    view_doc_text = word("View documentation")
    word_documentation = word("Documentation")
    for var in documentation_dict:
        if var not in name_info:
            name_info[var] = dict()
        if 'doc' in name_info[var] and name_info[var]['doc'] is not None:
            name_info[var]['doc'] += '<br>'
        else:
            name_info[var]['doc'] = ''
        name_info[var]['doc'] += "<a target='_blank' href='" + documentation_dict[var] + "'>" + view_doc_text + "</a>"
    for var in name_info:
        if 'methods' in name_info[var]:
            for method in name_info[var]['methods']:
                if var + '.' + method['name'] in documentation_dict:
                    if method['doc'] is None:
                        method['doc'] = ''
                    else:
                        method['doc'] += '<br>'
                    method['doc'] += "<a target='_blank' href='" + documentation_dict[var + '.' + method['name']] + "'>" + view_doc_text + "</a>"                
    content = ''
    if has_error:
        error_style = 'danger'
        if error_type is DAErrorNoEndpoint:
            error_style = 'warning'
            message_to_use = title_documentation['incomplete']['doc']
        elif error_type is DAErrorMissingVariable:
            message_to_use = error_message
        else:
            message_to_use = title_documentation['generic error']['doc']
        content += '\n                  <tr><td class="playground-warning-box"><div class="alert alert-' + error_style + '">' + message_to_use + '</div></td></tr>'
    # content += '\n                  <tr><td><h4>From</h4></td></tr>'
    # content += '\n                  <tr><td><select>'
    # for the_file in files:
    #     content += '<option '
    #     if the_file == current_file:
    #         content += "selected "
    #     content += 'value="' + the_file + '">' + str(the_file) + '</option>'
    # content += '</select></td></tr>'
    names_used = names_used.difference( functions | classes | modules | set(avail_modules) )
    undefined_names = names_used.difference(fields_used | set(base_name_info.keys()) )
    for var in ['_internal']:
        undefined_names.discard(var)
    names_used = names_used.difference( undefined_names )
    if len(undefined_names):
        content += '\n                  <tr><td><h4>Undefined names' + infobutton('undefined') + '</h4></td></tr>'
        for var in sorted(undefined_names):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-danger playground-variable">' + var + '</a></td></tr>'
    if len(names_used):
        content += '\n                  <tr><td><h4>Variables' + infobutton('variables') + '</h4></td></tr>'
        for var in sorted(names_used):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-primary playground-variable">' + var + '</a>'
            if var in name_info and 'type' in name_info[var] and name_info[var]['type']:
                content +='&nbsp;<span data-ref="' + noquote(name_info[var]['type']) + '" class="daparenthetical">(' + name_info[var]['type'] + ')</span>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(functions):
        content += '\n                  <tr><td><h4>Functions' + infobutton('functions') + '</h4></td></tr>'
        for var in sorted(functions):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-warning playground-variable">' + name_info[var]['tag'] + '</a>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(classes):
        content += '\n                  <tr><td><h4>Classes' + infobutton('classes') + '</h4></td></tr>'
        for var in sorted(classes):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-info playground-variable">' + name_info[var]['name'] + '</a>'
            if name_info[var]['bases']:
                content += '&nbsp;<span data-ref="' + noquote(name_info[var]['bases'][0]) + '" class="daparenthetical">(' + name_info[var]['bases'][0] + ')</span>'
            if name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            if len(name_info[var]['methods']):
                content += '&nbsp;<a class="dashowmethods" role="button" data-showhide="XMETHODX' + var + '" title="' + word('Methods') + '"><i class="glyphicon glyphicon-cog"></i></a>'
                content += '<table class="invisible" id="XMETHODX' + var + '"><tbody>'
                for method_info in name_info[var]['methods']:
                    content += '<tr><td><a data-name="' + noquote(method_info['name']) + '" data-insert="' + noquote(method_info['insert']) + '" class="label label-warning playground-variable">' + method_info['tag'] + '</a>'
                    if method_info['doc']:
                        content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + method_info['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + noquote(method_info['name']) + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
                    content += '</td></tr>'
                content += '</tbody></table>'
            content += '</td></tr>'
    if len(modules):
        content += '\n                  <tr><td><h4>Modules defined' + infobutton('modules') + '</h4></td></tr>'
        for var in sorted(modules):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-success playground-variable">' + name_info[var]['name'] + '</a>'
            if name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + noquote(var) + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(avail_modules):
        content += '\n                  <tr><td><h4>Modules available in Playground' + infobutton('playground_modules') + '</h4></td></tr>'
        for var in avail_modules:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert=".' + noquote(var) + '" class="label label-success playground-variable">.' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(templates):
        content += '\n                  <tr><td><h4>Templates' + infobutton('templates') + '</h4></td></tr>'
        for var in templates:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(static):
        content += '\n                  <tr><td><h4>Static files' + infobutton('static') + '</h4></td></tr>'
        for var in static:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(interview.images):
        content += '\n                  <tr><td><h4>Decorations' + infobutton('decorations') + '</h4></td></tr>'
        for var in sorted(interview.images):
            content += '\n                  <tr><td><img class="daimageicon" src="' + get_url_from_file_reference(interview.images[var].get_reference()) + '">&nbsp;<a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-primary playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    return content

@app.route('/playground', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_page():
    form = PlaygroundForm(request.form, current_user)
    interview = None
    the_file = request.args.get('file', '')
    if request.method == 'GET':
        is_new = request.args.get('new', False)
    else:
        is_new = False
    if is_new:
        the_file = ''
    playground = SavedFile(current_user.id, fix=True, section='playground')
    #path = os.path.join(UPLOAD_DIRECTORY, 'playground', str(current_user.id))
    #if not os.path.exists(path):
    #    os.makedirs(path)
    if request.method == 'POST' and (form.submit.data or form.run.data or form.delete.data):
        if (form.playground_name.data):
            the_file = form.playground_name.data
            the_file = re.sub(r'[^A-Za-z0-9\_\-\.]', '', the_file)
            if not re.search(r'\.ya?ml$', the_file):
                the_file = re.sub(r'\..*', '', the_file) + '.yml'
            if the_file != '':
                filename = os.path.join(playground.directory, the_file)
                if not os.path.isfile(filename):
                    with open(filename, 'a'):
                        os.utime(filename, None)
            else:
                flash(word('You need to type in a name for the interview'), 'error')
        else:
            flash(word('You need to type in a name for the interview'), 'error')
    the_file = re.sub(r'[^A-Za-z0-9\_\-\.]', '', the_file)
    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f))])
    content = ''
    is_default = False
    if request.method == 'GET' and not the_file and not is_new:
        if len(files):
            the_file = files[0]
        else:
            the_file = 'test.yml'
            is_default = True
            content = default_playground_yaml
    active_file = the_file
    if 'variablefile' in session:
        if session['variablefile'] in files:
            active_file = session['variablefile']
        else:
            del session['variablefile']
    if the_file != '':
        filename = os.path.join(playground.directory, the_file)
        if not os.path.isfile(filename):
            with open(filename, 'w') as fp:
                fp.write(content.encode('utf8'))
            playground.finalize()
    post_data = request.form.copy()
    if request.method == 'POST' and 'variablefile' in post_data:
        active_file = post_data['variablefile']
        if post_data['variablefile'] in files:
            session['variablefile'] = active_file
            interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + active_file)
            interview_source.set_testing(True)
        else:
            if active_file == '':
                active_file = 'test.yml'
            content = ''
            if form.playground_content.data:
                content = form.playground_content.data
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        interview = interview_source.get_interview()
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
        variables_html = get_vars_in_use(interview, interview_status)
        return jsonify(variables_html=variables_html)
    if request.method == 'POST' and the_file != '' and form.validate():
        if form.delete.data:
            if os.path.isfile(filename):
                os.remove(filename)
                flash(word('File deleted.'), 'info')
                playground.finalize()
                if 'variablefile' in session and session['variablefile'] == the_file:
                    del session['variablefile']
                return redirect(url_for('playground_page'))
            else:
                flash(word('File not deleted.  There was an error.'), 'error')
        if (form.submit.data or form.run.data) and form.playground_content.data:
            if form.original_playground_name.data and form.original_playground_name.data != the_file:
                old_filename = os.path.join(playground.directory, form.original_playground_name.data)
                if os.path.isfile(old_filename):
                    os.remove(old_filename)
                    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f))])
            the_time = time.strftime('%H:%M:%S %Z', time.localtime())
            with open(filename, 'w') as fp:
                fp.write(form.playground_content.data.encode('utf8'))
            for a_file in files:
                docassemble.base.interview_cache.clear_cache('docassemble.playground' + str(current_user.id) + ':' + a_file)
                a_filename = os.path.join(playground.directory, a_file)
                if a_filename != filename and os.path.isfile(a_filename):
                    with open(a_filename, 'a'):
                        os.utime(a_filename, None)
            playground.finalize()
            if form.submit.data:
                flash(word('Saved at') + ' ' + the_time + '.', 'success')
            else:
                flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Running in other tab.'), message_type='success')
                interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + the_file)
                interview_source.set_testing(True)
                interview = interview_source.get_interview()
                interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
                variables_html = get_vars_in_use(interview, interview_status)
                return jsonify(url=url_for('index', i='docassemble.playground' + str(current_user.id) + ':' + the_file), variables_html=variables_html, flash_message=flash_message)
        else:
            flash(word('Playground not saved.  There was an error.'), 'error')
    interview_path = None
    if the_file != '':
        with open(filename, 'rU') as fp:
            form.original_playground_name.data = the_file
            form.playground_name.data = the_file
            content = fp.read().decode('utf8')
            #if not form.playground_content.data:
                #form.playground_content.data = content
    if active_file != '':
        is_fictitious = False
        interview_path = 'docassemble.playground' + str(current_user.id) + ':' + active_file
        if is_default:
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        else:
            interview_source = docassemble.base.parse.interview_source_from_string(interview_path)
            interview_source.set_testing(True)
    else:
        is_fictitious = True
        active_file = 'test.yml'
        if form.playground_content.data:
            content = re.sub(r'\r', '', form.playground_content.data)
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        else:
            interview_source = docassemble.base.parse.InterviewSourceString(content='', directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
    interview = interview_source.get_interview()
    interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
    variables_html = get_vars_in_use(interview, interview_status)
    pulldown_files = list(files)
    if is_fictitious or is_new or is_default:
        new_active_file = word('(New file)')
        if new_active_file not in pulldown_files:
            pulldown_files.insert(0, new_active_file)
        if is_fictitious:
            active_file = new_active_file
    ajax = """
var exampleData;

function activateExample(id){
  var info = exampleData[id];
  $("#example-source").html(info['html']);
  $("#example-source-before").html(info['before_html']);
  $("#example-source-after").html(info['after_html']);
  $("#example-image-link").attr("href", info['interview']);
  $("#example-image").attr("src", info['image']);
  if (info['documentation'] != null){
    $("#example-documentation-link").attr("href", info['documentation']);
    $("#example-documentation-link").removeClass("example-hidden");
  }
  else{
    $("#example-documentation-link").addClass("example-hidden");
  }
  $(".example-list").addClass("example-hidden");
  $(".example-link").removeClass("example-active");
  $(".example-link").parent().removeClass("active");
  $(".example-link").each(function(){
    if ($(this).data("example") == id){
      $(this).addClass("example-active");
      $(this).parent().addClass("active");
      $(this).parents(".example-list").removeClass("example-hidden");
    }
  });
  $("#hide-full-example").addClass("invisible");
  $("#show-full-example").removeClass("invisible");
  $("#example-source-before").addClass("invisible");
  $("#example-source-after").addClass("invisible");
}

interviewBaseUrl = '""" + url_for('index', i='docassemble.playground' + str(current_user.id) + ':.yml') + """';

function updateRunLink(){
  $("#daRunButton").attr("href", interviewBaseUrl.replace('.yml', $("#daVariables").val()));
}

$( document ).ready(function() {
  $("#daVariables").change(function(event){
    daCodeMirror.save();
    updateRunLink();
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&variablefile=' + $(this).val(),
      success: function(data){
        console.log("foobar1")
        $("#daplaygroundtable").html(data.variables_html)
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'hover', html: true})
        });
        console.log("foobar2")
      },
      dataType: 'json'
    });
    $(this).blur();
  });
  $("#daRun").click(function(event){
    daCodeMirror.save();
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&run=Save+and+Run',
      success: function(data){
        if ($("#flash").length){
          $("#flash").html(data.flash_message)
        }
        else{
          $("#main").prepend('<div class="container topcenter" id="flash">' + data.flash_message + '</div>')
        }
        $("#daplaygroundtable").html(data.variables_html)
        window.open(data.url, '_blank');
        $("#form").trigger("reinitialize.areYouSure")
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'hover', html: true})
        });
      },
      dataType: 'json'
    });
    event.preventDefault();
  });
  $(".playground-variable").on("click", function(){
    daCodeMirror.replaceSelection($(this).data("insert"), "around");
    daCodeMirror.focus();
  });

  $(".daparenthetical").on("click", function(event){
    var reference = $(this).data("ref");
    //console.log("reference is " + reference)
    var target = $('[data-name="' + reference + '"]').first();
    if (target != null){
      //console.log("scrolltop is now " + $('#daplaygroundpanel').scrollTop());
      //console.log("Scrolling to " + target.position().top);
      $('#daplaygroundpanel').animate({
          scrollTop: target.position().top
      }, 1000);
    }
    event.preventDefault();
  });

  $(".dashowmethods").on("click", function(event){
    var target_id = $(this).data("showhide");
    $("#" + target_id).toggleClass("invisible");
  });

  $(".example-link").on("click", function(){
    var id = $(this).data("example");
    activateExample(id);
  });

  $(".example-copy").on("click", function(){
    if (daCodeMirror.somethingSelected()){
      daCodeMirror.replaceSelection("");
    }
    var id = $(".example-active").data("example");
    var curPos = daCodeMirror.getCursor();
    var notFound = 1;
    var insertLine = daCodeMirror.lastLine();
    daCodeMirror.eachLine(curPos.line, insertLine, function(line){
      if (notFound){
        if (line.text.substring(0, 3) == "---" || line.text.substring(0, 3) == "..."){
          insertLine = daCodeMirror.getLineNumber(line)
          //console.log("Found break at line number " + insertLine)
          notFound = 0;
        }
      }
    });
    if (notFound){
      daCodeMirror.setSelection({'line': insertLine, 'ch': null});
      daCodeMirror.replaceSelection("\\n---\\n" + exampleData[id]['source'] + "\\n", "around");
    }
    else{
      daCodeMirror.setSelection({'line': insertLine, 'ch': 0});
      daCodeMirror.replaceSelection("---\\n" + exampleData[id]['source'] + "\\n", "around");
    }
    daCodeMirror.focus();
  });

  $(".example-heading").on("click", function(){
    var list = $(this).parent().children("ul").first();
    if (list != null){
      if (!list.hasClass("example-hidden")){
        return;
      }
      $(".example-list").addClass("example-hidden");
      var new_link = $(this).parent().find("a.example-link").first();
      if (new_link.length){
        var id = new_link.data("example");
        activateExample(id);  
      }
    }
  });

  $(function () {
    $('[data-toggle="popover"]').popover({trigger: 'hover', html: true})
  });

  $("#show-full-example").on("click", function(){
    var id = $(".example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("invisible");
    $("#hide-full-example").removeClass("invisible");
    $("#example-source-before").removeClass("invisible");
    $("#example-source-after").removeClass("invisible");
  });

  $("#hide-full-example").on("click", function(){
    var id = $(".example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("invisible");
    $("#show-full-example").removeClass("invisible");
    $("#example-source-before").addClass("invisible");
    $("#example-source-after").addClass("invisible");
  });
  if ($("#playground_name").val().length > 0){
    daCodeMirror.focus();
  }
  else{
    $("#playground_name").focus()
  }
  updateRunLink();
});
"""
    example_html = list()
    example_html.append('        <div class="col-md-2">\n          <h4>' + word("Example blocks") +'</h4>')
    first_id = list()
    data_dict = dict()
    make_example_html(get_examples(), first_id, example_html, data_dict)
    example_html.append('        </div>')
    example_html.append('        <div class="col-md-6"><h4>' + word("Preview") + '<a target="_blank" class="label label-primary example-documentation example-hidden" id="example-documentation-link">' + word('View documentation') + '</a></h4><a href="#" target="_blank" id="example-image-link"><img title="' + word('Click to try this interview') + '" class="example_screenshot" id="example-image"></a></div>')
    example_html.append('        <div class="col-md-4 example-source-col"><h4>' + word('Source') + ' <a class="label label-success example-copy">' + word('Insert') + '</a></h4><div id="example-source-before" class="invisible"></div><div id="example-source"></div><div id="example-source-after" class="invisible"></div><div><a class="example-hider" id="show-full-example">' + word("Show context of example") + '</a><a class="example-hider invisible" id="hide-full-example">' + word("Hide context of example") + '</a></div></div>')
    return render_template('pages/playground.html', page_title=word("Playground"), extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this playground file?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("playground_content");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#form").trigger("checkform.areYouSure");});\n      $("#form").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#form").bind("submit", function(){daCodeMirror.save(); $("#form").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setSize(null, "400px");\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n' + indent_by(ajax, 6) + '\n      exampleData = ' + str(json.dumps(data_dict)) + ';\n      activateExample("' + str(first_id[0]) + '");\n    </script>'), form=form, files=files, pulldown_files=pulldown_files, current_file=the_file, active_file=active_file, content=content, variables_html=Markup(variables_html), example_html=Markup("\n".join(example_html)), interview_path=interview_path, is_new=str(is_new)), 200

# nameInfo = ' + str(json.dumps(vars_in_use['name_info'])) + ';      

@app.route('/packages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def package_page():
    return render_template('pages/packages.html'), 200

def make_image_files(path):
    #logmessage("make_image_files on " + str(path))
    if PDFTOPPM_COMMAND is not None:
        args = [PDFTOPPM_COMMAND, '-r', str(PNG_RESOLUTION), '-png', path, path + 'page']
        result = call(args)
        if result > 0:
            raise DAError("Call to pdftoppm failed")
        args = [PDFTOPPM_COMMAND, '-r', str(PNG_SCREEN_RESOLUTION), '-png', path, path + 'screen']
        result = call(args)
        if result > 0:
            raise DAError("Call to pdftoppm failed")
    return

@app.errorhandler(Exception)
def server_error(the_error):
    errmess = unicode(the_error)
    if type(the_error) is DAError:
        the_trace = None
        logmessage(errmess)
    else:
        the_trace = traceback.format_exc()
        logmessage(the_trace)
    flask_logtext = []
    with open(LOGFILE) as the_file:
        for line in the_file:
            if re.match('Exception', line):
                flask_logtext = []
            flask_logtext.append(line)
    # apache_logtext = []
    # with open(APACHE_LOGFILE) as the_file:
    #     for line in the_file:
    #         if re.search('configured -- resuming normal operations', line):
    #             apache_logtext = []
    #         apache_logtext.append(line)
    # errmess = re.sub(r'\n', '<br>', errmess)
    if re.search(r'\n', errmess):
        errmess = '<pre>' + errmess + '</pre>'
    else:
        errmess = '<blockquote>' + errmess + '</blockquote>'
    return render_template('pages/501.html', error=errmess, logtext=str(the_trace)), 501

def trigger_update(except_for=None):
    logmessage("trigger_update: except_for is " + str(except_for))
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url and not (except_for and host.hostname == except_for):
                args = [SUPERVISORCTL, '-s', host.url, 'start update']
                result = call(args)
                if result == 0:
                    logmessage("trigger_update: sent reset to " + str(host.hostname))
                else:
                    logmessage("trigger_update: call to supervisorctl on " + str(host.hostname) + " was not successful")
    return

def restart_wsgi():
    logmessage("Got to restart_wsgi")
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url:
                args = [SUPERVISORCTL, '-s', host.url, 'start reset']
                result = call(args)
                if result == 0:
                    logmessage("restart_wsgi: sent reset to " + str(host.hostname))
                else:
                    logmessage("restart_wsgi: call to supervisorctl on " + str(host.hostname) + " was not successful")
            else:
                logmessage("restart_wsgi: unable to get host url")
        time.sleep(1)
    else:
        logmessage("restart_wsgi: touched wsgi file")
        wsgi_file = WEBAPP_PATH
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a'):
                os.utime(wsgi_file, None)
    return

@app.route('/testpost', methods=['GET', 'POST'])
def test_post():
    errmess = "Hello, " + str(request.method) + "!"
    is_redir = request.args.get('redir', None)
    if is_redir or request.method == 'GET':
        return render_template('pages/testpost.html', error=errmess), 200
    newargs = dict(request.args)
    newargs['redir'] = '1'
    logtext = url_for('test_post', **newargs)
    #return render_template('pages/testpost.html', error=errmess, logtext=logtext), 200
    return redirect(logtext, code=307)

@app.route('/packagestatic/<package>/<filename>', methods=['GET'])
def package_static(package, filename):
    the_file = docassemble.base.util.package_data_filename(str(package) + ':data/static/' + str(filename))
    if the_file is None:
        abort(404)
    extension, mimetype = get_ext_and_mimetype(the_file)
    return(send_file(the_file, mimetype=str(mimetype)))

def current_info(yaml=None, req=None, action=None, location=None):
    if current_user.is_authenticated and not current_user.is_anonymous:
        ext = dict(email=current_user.email, roles=[role.name for role in current_user.roles], theid=current_user.id, firstname=current_user.first_name, lastname=current_user.last_name, nickname=current_user.nickname, country=current_user.country, subdivisionfirst=current_user.subdivisionfirst, subdivisionsecond=current_user.subdivisionsecond, subdivisionthird=current_user.subdivisionthird, organization=current_user.organization)
    else:
        ext = dict(email=None, theid=None, roles=list())
    if req is None:
        url = 'http://localhost'
    else:
        url = req.base_url
    return_val = {'session': session.get('uid', None), 'yaml_filename': yaml, 'url': url, 'user': {'is_anonymous': current_user.is_anonymous, 'is_authenticated': current_user.is_authenticated}}
    if action is not None:
        return_val.update(action)
    if location is not None:
        ext['location'] = location
    else:
        ext['location'] = None
    return_val['user'].update(ext)
    return(return_val)

def html_escape(text):
    text = re.sub('&', '&amp;', text)
    text = re.sub('<', '&lt;', text)
    text = re.sub('>', '&gt;', text)
    return text;

def indent_by(text, num):
    if not text:
        return ""
    return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"

# def indent_by(text, num):
#     return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"
    
# @app.route('/twiliotest', methods=['GET', 'POST'])
# def twilio_test():
#     account_sid = "ACfad8e668b5f9e15d499ab823523b9358"
#     auth_token = "86549c9a407b25d32f21c758e7b09546"
#     application_sid = "AP67affb53323193b8e2af0872aad387ad"
#     capability = TwilioCapability(account_sid, auth_token)
#     capability.allow_client_outgoing(application_sid)
#     token = capability.generate()
#     return render_template('pages/twiliotest.html', token=token)

@app.route('/logfile/<filename>', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def logfile(filename):
    if LOGSERVER is None:
        the_file = os.path.join(LOG_DIRECTORY, filename)
        if not os.path.isfile(the_file):
            abort(404)
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8080', "GET")
        the_file, headers = urllib.urlretrieve("http://" + LOGSERVER + ':8080/' + urllib.quote(filename))
    return(send_file(the_file, as_attachment=True, mimetype='text/plain', attachment_filename=filename, cache_timeout=0))

@app.route('/logs', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def logs():
    form = LogForm(request.form, current_user)
    the_file = request.args.get('file', None)
    default_filter_string = ''
    if request.method == 'POST' and form.file_name.data:
        the_file = form.file_name.data
    if LOGSERVER is None:
        call_sync()
        files = sorted([f for f in os.listdir(LOG_DIRECTORY) if os.path.isfile(os.path.join(LOG_DIRECTORY, f))])
        if the_file is None and len(files):
            if 'docassemble.log' in files:
                the_file = 'docassemble.log'
            else:
                the_file = files[0]
        if the_file is not None:
            filename = os.path.join(LOG_DIRECTORY, the_file)
            # if (not os.path.isfile(filename)) and len(files):
            #     the_file = files[0]
            # else:
            #     the_file = None
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8080', "GET")
        if int(resp['status']) >= 200 and int(resp['status']) < 300:
            files = content.split("\n")
        else:
            abort(404)
        if len(files):
            if the_file is None:
                the_file = files[0]
            filename, headers = urllib.urlretrieve("http://" + LOGSERVER + ':8080/' + urllib.quote(the_file))
    if len(files):
        if request.method == 'POST' and form.submit.data and form.filter_string.data:
            default_filter_string = form.filter_string.data
            reg_exp = re.compile(form.filter_string.data)
            temp_file = tempfile.NamedTemporaryFile()
            with open(filename, 'rU') as fp:
                for line in fp:
                    if reg_exp.search(line):
                        temp_file.write(line)
            lines = tailer.tail(temp_file, 30)
        else:
            lines = tailer.tail(open(filename), 30)
        content = "\n".join(lines)
    else:
        content = "No log files available"
    return render_template('pages/logs.html', form=form, files=files, current_file=the_file, content=content, default_filter_string=default_filter_string), 200

def call_sync():
    if not USING_SUPERVISOR:
        return
    args = [SUPERVISORCTL, '-s', 'http://' + hostname + ':9001', 'start', 'sync']
    result = call(args)
    if result == 0:
        logmessage("logs: sent message to " + hostname)
    else:
        logmessage("logs: call to supervisorctl on " + hostname + " was not successful")
        abort(404)
    in_process = 1
    counter = 10
    check_args = [SUPERVISORCTL, '-s', 'http://' + hostname + ':9001', 'status', 'sync']
    while in_process == 1 and counter > 0:
        output, err = Popen(check_args, stdout=PIPE, stderr=PIPE).communicate()
        if not re.search(r'RUNNING', output):
            in_process = 0
        else:
            time.sleep(1)
        counter -= 1
    return


@app.route('/reqdev', methods=['GET', 'POST'])
@login_required
def request_developer():
    from docassemble.webapp.users.forms import RequestDeveloperForm
    form = RequestDeveloperForm(request.form, current_user)
    recipients = list()
    if request.method == 'POST':
        for user in User.query.filter_by(active=True).all():
            for role in user.roles:
                if role.name == 'admin':
                    recipients.append(user.email)
        url = request.base_url
        url = re.sub(r'^(https?://[^/]+)/.*', r'\1', url)
        body = "User " + str(current_user.email) + " (" + str(current_user.id) + ") has requested developer privileges.\n\n"
        if form.reason.data:
            body += "Reason given: " + str(form.reason.data) + "\n\n"
        body += "Go to " + str(url) + url_for('edit_user_profile_page', id=current_user.id) + " to change the user's privileges."
        from flask_mail import Message
        msg = Message("Request for developer account from " + str(current_user.email), recipients=recipients, body=body)
        if not len(recipients):
            flash(word('No administrators could be found.'), 'error')
        else:
            try:
                async_mail(msg)
                flash(word('Your request was submitted.'), 'success')
            except:
                flash(word('We were unable to submit your request.'), 'error')
        return redirect(url_for('index'))
    return render_template('users/request_developer.html', form=form)

@app.route('/utilities', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def utilities():
    form = Utilities(request.form)
    fields_output = None
    if request.method == 'POST':
        if 'pdffile' in request.files and request.files['pdffile'].filename:
            pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=True)
            the_file = request.files['pdffile']
            the_file.save(pdf_file.name)
            fields = docassemble.base.pdftk.read_fields(pdf_file.name)
            if fields is None:
                fields_output = word("Error: no fields could be found in the file")
            else:
                fields_output = "---\nquestion: " + word("something") + "\nsets: " + word('some_variable') + "\nattachment:" + "\n  - name: " + os.path.splitext(the_file.filename)[0] + "\n    filename: " + os.path.splitext(the_file.filename)[0] + "\n    pdf template file: " + the_file.filename + "\n    fields:\n"
                for field, default, pageno, rect, field_type in fields:
                    fields_output += '      "' + field + '": ' + default + "\n"
                fields_output += "---"
    return render_template('pages/utilities.html', form=form, fields=fields_output)

def nice_date_from_utc(timestamp):
    return timestamp.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime('%x %X')

@app.route('/save', methods=['GET', 'POST'])
def save_for_later():
    if current_user.is_authenticated and not current_user.is_anonymous:
        return render_template('pages/save_for_later.html', interview=sdf)
    secret = request.cookies.get('secret', None)

@app.route('/interviews', methods=['GET', 'POST'])
@login_required
def interview_list():
    secret = request.cookies.get('secret', None)
    #logmessage("interview_list: secret is " + str(secret))
    if 'action' in request.args and request.args.get('action') == 'delete':
        yaml_file = request.args.get('filename', None)
        session_id = request.args.get('session', None)
        if yaml_file is not None and session_id is not None:
            reset_user_dict(session_id, yaml_file)
            flash(word("Deleted interview"), 'success')
            return redirect(url_for('interview_list'))
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), UserDict.filename, UserDict.key).group_by(UserDict.filename, UserDict.key).subquery()
    interview_query = db.session.query(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted).filter(UserDictKeys.user_id == current_user.id).join(subq, and_(subq.c.filename == UserDictKeys.filename, subq.c.key == UserDictKeys.key)).join(UserDict, and_(UserDict.indexno == subq.c.indexno, UserDict.key == UserDictKeys.key, UserDict.filename == UserDictKeys.filename)).group_by(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted)
    #logmessage(str(interview_query))
    interviews = list()
    for interview_info in interview_query:
        try:
            interview = docassemble.base.interview_cache.get_interview(interview_info.filename)
        except:
            logmessage("Unable to load interview file " + interview_info.filename)
            continue
        if len(interview.metadata):
            metadata = interview.metadata[0]
            interview_title = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
        else:
            interview_title = word('Untitled')
        #logmessage("Found old interview with title " + interview_title)
        if interview_info.encrypted:
            try:
                dictionary = decrypt_dictionary(interview_info.dictionary, secret)
            except:
                logmessage("Unable to decrypt dictionary with secret " + str(secret))
                continue
        else:
            dictionary = unpack_dictionary(interview_info.dictionary)
        starttime = nice_date_from_utc(dictionary['_internal']['starttime'])
        modtime = nice_date_from_utc(dictionary['_internal']['modtime'])
        interviews.append({'interview_info': interview_info, 'dict': dictionary, 'modtime': modtime, 'starttime': starttime, 'title': interview_title})
    return render_template('pages/interviews.html', interviews=sorted(interviews, key=lambda x: x['dict']['_internal']['starttime']))

# @user_logged_in.connect_via(app)
# def _after_login_hook(sender, user, **extra):
#     if 'i' in session and 'uid' in session:
#         save_user_dict_key(session['uid'], session['i'])
#         session['key_logged'] = True 
#     newsecret = substitute_secret(secret, pad_to_16(MD5.MD5Hash(data=password).hexdigest()))
#     # Redirect to 'next' URL
#     response = redirect(next)
#     response.set_cookie('secret', newsecret)
#     return response
