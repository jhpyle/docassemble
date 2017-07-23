min_system_version = '0.1.22'
import re
import os
import sys
import tempfile
import ruamel.yaml
import tarfile
from textstat.textstat import textstat
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load()
import docassemble.base.functions
from urllib import unquote
from docassemble.base.config import daconfig, hostname, in_celery

DEBUG = daconfig.get('debug', False)
HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)
request_active = True

word_file_list = daconfig.get('words', list())
if type(word_file_list) is not list:
    word_file_list = [word_file_list]
for word_file in word_file_list:
    #sys.stderr.write("Reading from " + str(word_file) + "\n")
    filename = docassemble.base.functions.static_filename_path(word_file)
    if os.path.isfile(filename):
        with open(filename, 'rU') as stream:
            for document in ruamel.yaml.safe_load_all(stream):
                if document and type(document) is dict:
                    for lang, words in document.iteritems():
                        if type(words) is dict:
                            docassemble.base.functions.update_word_collection(lang, words)
                        else:
                            sys.stderr.write("Error reading " + str(word_file) + ": words not in dictionary form.\n")
                else:
                    sys.stderr.write("Error reading " + str(word_file) + ": yaml file not in dictionary form.\n")

default_playground_yaml = """metadata:
  title: Default playground interview
  short title: Test
  comment: This is a learning tool.  Feel free to write over it.
---
include:
  - basic-questions.yml
---
mandatory: True
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

ok_mimetypes = {"application/javascript": "javascript", "text/x-python": "python", "application/json": "json", "text/css": "css"}
ok_extensions = {"yml": "yaml", "yaml": "yaml", "md": "markdown", "markdown": "markdown", 'py': "python", "json": "json", "css": "css"}

default_yaml_filename = daconfig.get('default interview', None)
final_default_yaml_filename = daconfig.get('default interview', 'docassemble.demo:data/questions/questions.yml')
keymap = daconfig.get('keymap', None)

detect_mobile = re.compile('Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|NetFront|Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|Dolfin|Dolphin|Skyfire|Zune')
alphanumeric_only = re.compile('[\W_]+')
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")
document_match = re.compile(r'^--- *$', flags=re.MULTILINE)
fix_tabs = re.compile(r'\t')
fix_initial = re.compile(r'^---\n')
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
extraneous_var = re.compile(r'^x\.|^x\[')
key_requires_preassembly = re.compile('^(x\.|x\[|_multiple_choice|.*\[[ijklmn]\])')
match_invalid = re.compile('[^A-Za-z0-9_\[\].\'\%\-=]')
match_invalid_key = re.compile('[^A-Za-z0-9_\[\].\'\%\- =]')
match_brackets = re.compile('\[\'.*\'\]$')
match_inside_and_outside_brackets = re.compile('(.*)(\[\'[^\]]+\'\])$')
match_inside_brackets = re.compile('\[\'([^\]]+)\'\]')

if 'mail' not in daconfig:
    daconfig['mail'] = dict()
if 'dispatch' not in daconfig:
    daconfig['dispatch'] = dict()
default_title = daconfig.get('default title', daconfig.get('brandname', 'docassemble'))
default_short_title = daconfig.get('default short title', default_title)
os.environ['PYTHON_EGG_CACHE'] = tempfile.gettempdir()
PNG_RESOLUTION = daconfig.get('png resolution', 300)
PNG_SCREEN_RESOLUTION = daconfig.get('png screen resolution', 72)
PDFTOPPM_COMMAND = daconfig.get('pdftoppm', 'pdftoppm')
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'en_US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
LOGSERVER = daconfig.get('log server', None)
CHECKIN_INTERVAL = daconfig.get('checkin interval', 6000)
#message_sequence = dbtableprefix + 'message_id_seq'

if os.environ.get('SUPERVISOR_SERVER_URL', None):
    USING_SUPERVISOR = True
    #sys.stderr.write("Using supervisor and hostname is " + str(hostname) + "\n")
else:
    USING_SUPERVISOR = False
    #sys.stderr.write("Not using supervisor and hostname is " + str(hostname) + "\n")

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
#app.logger.warning("default sender is " + current_app.config['MAIL_DEFAULT_SENDER'] + "\n")
exit_page = daconfig.get('exitpage', 'https://docassemble.org')

SUPERVISORCTL = daconfig.get('supervisorctl', 'supervisorctl')
#PACKAGE_CACHE = daconfig.get('packagecache', '/var/www/.cache')
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local')
UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')
FULL_PACKAGE_DIRECTORY = os.path.join(PACKAGE_DIRECTORY, 'lib', 'python2.7', 'site-packages')
LOG_DIRECTORY = daconfig.get('log', '/usr/share/docassemble/log')
#PLAYGROUND_MODULES_DIRECTORY = daconfig.get('playground_modules', )

init_py_file = """try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)
"""
    
#if not os.path.isfile(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py')):
#    with open(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py'), 'a') as the_file:
#        the_file.write(init_py_file)

#USE_PROGRESS_BAR = daconfig.get('use_progress_bar', True)
SHOW_LOGIN = daconfig.get('show login', True)
ALLOW_REGISTRATION = daconfig.get('allow registration', True)
#USER_PACKAGES = daconfig.get('user_packages', '/var/lib/docassemble/dist-packages')
#sys.path.append(USER_PACKAGES)
#if USE_PROGRESS_BAR:

if in_celery:
    LOGFILE = daconfig.get('celery flask log', '/tmp/celery-flask.log')
else:
    LOGFILE = daconfig.get('flask log', '/tmp/flask.log')
#APACHE_LOGFILE = daconfig.get('apache_log', '/var/log/apache2/error.log')

#connect_string = docassemble.webapp.database.connection_string()
#alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()

def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property

def _endpoint_url(endpoint):
    url = '/'
    if endpoint:
        url = url_for(endpoint)
    return url

def _get_safe_next_param(param_name, default_endpoint):
    if param_name in request.args:
        safe_next = current_app.user_manager.make_safe_url_function(unquote(request.args[param_name]))
    else:
        safe_next = _endpoint_url(default_endpoint)
    return safe_next

# def _do_login_user(user, safe_next, remember_me=False):
#     if not user: return unauthenticated()

#     if not _call_or_get(user.is_active):
#         flash(word('Your account has not been enabled.'), 'error')
#         return redirect(url_for('user.login'))

#     user_manager = current_app.user_manager
#     if user_manager.enable_email and user_manager.enable_confirm_email \
#             and not current_app.user_manager.enable_login_without_confirm_email \
#             and not user.has_confirmed_email():
#         url = url_for('user.resend_confirm_email')
#         flash(flask_user.translations.gettext('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="%(url)s">Re-send confirmation email</a>.', url=url), 'error')
#         return redirect(url_for('user.login'))

#     login_user(user, remember=remember_me)

#     signals.user_logged_in.send(current_app._get_current_object(), user=user)

#     flash(word('You have signed in successfully.'), 'success')

#     return redirect(safe_next)

def custom_resend_confirm_email():
    user_manager =  current_app.user_manager
    db_adapter = user_manager.db_adapter
    form = user_manager.resend_confirm_email_form(request.form)
    if request.method=='GET' and 'email' in request.args:
        form.email.data = request.args['email']
    if request.method=='POST' and form.validate():
        email = form.email.data
        user, user_email = user_manager.find_user_by_email(email)
        if user:
            flask_user.views._send_confirm_email(user, user_email)
        return redirect(flask_user.views._endpoint_url(user_manager.after_resend_confirm_email_endpoint))
    return user_manager.render_function(user_manager.resend_confirm_email_template, form=form)

def custom_login():
    """ Prompt for username/email and password and sign the user in."""
    user_manager =  current_app.user_manager
    db_adapter = user_manager.db_adapter

    safe_next = _get_safe_next_param('next', user_manager.after_login_endpoint)
    safe_reg_next = _get_safe_next_param('reg_next', user_manager.after_register_endpoint)

    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        return redirect(safe_next)

    login_form = user_manager.login_form(request.form)
    register_form = user_manager.register_form()
    if request.method != 'POST':
        login_form.next.data     = register_form.next.data     = safe_next
        login_form.reg_next.data = register_form.reg_next.data = safe_reg_next

    if request.method=='POST' and login_form.validate():
        user = None
        user_email = None
        if user_manager.enable_username:
            user = user_manager.find_user_by_username(login_form.username.data)
            user_email = None
            if user and db_adapter.UserEmailClass:
                user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
                        user_id=int(user.get_id()),
                        is_primary=True,
                        )
            if not user and user_manager.enable_email:
                user, user_email = user_manager.find_user_by_email(login_form.username.data)
        else:
            user, user_email = user_manager.find_user_by_email(login_form.email.data)

        if user:
            safe_next = user_manager.make_safe_url_function(login_form.next.data)
            if daconfig.get('two factor authentication', False) is True and user.otp_secret is not None:
                session['validated_user'] = user.id
                if user.otp_secret.startswith(':phone:'):
                    phone_number = re.sub(r'^:phone:', '', user.otp_secret)
                    verification_code = random_digits(daconfig['verification code digits'])
                    message = word("Your verification code is") + " " + str(verification_code) + "."
                    key = 'da:mfa:phone:' + str(phone_number) + ':code'
                    pipe = r.pipeline()
                    pipe.set(key, verification_code)
                    pipe.expire(key, daconfig['verification code timeout'])
                    pipe.execute()
                    success = docassemble.base.util.send_sms(to=phone_number, body=message)
                    if not success:
                        flash(word("Unable to send verification code."), 'error')
                        return redirect(url_for('user.login'))
                return redirect(url_for('mfa_login', next=safe_next))
            if user_manager.enable_email and user_manager.enable_confirm_email \
               and len(daconfig['email confirmation privileges']) \
               and user.has_role(*daconfig['email confirmation privileges']) \
               and not user.has_confirmed_email():
                url = url_for('user.resend_confirm_email', email=user.email)
                flash(word('You cannot log in until your e-mail address has been confirmed.') + '<br><a href="' + url + '">' + word('Click here to confirm your e-mail') + '</a>.', 'error')
                return redirect(url_for('user.login'))
            return flask_user.views._do_login_user(user, safe_next, login_form.remember_me.data)

    return user_manager.render_function(user_manager.login_template,
            form=login_form,
            login_form=login_form,
            register_form=register_form)

def logout():
    secret = request.cookies.get('secret', None)
    if secret is None:
        secret = random_string(16)
        set_cookie = True
    else:
        secret = str(secret)
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

# def custom_login():
#     logmessage("custom_login")
#     user_manager = current_app.user_manager
#     db_adapter = user_manager.db_adapter
#     secret = request.cookies.get('secret', None)
#     if secret is not None:
#         secret = str(secret)
#     next = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
#     reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))

#     if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
#         return redirect(next)

#     login_form = user_manager.login_form(request.form)
#     register_form = user_manager.register_form()
#     if request.method != 'POST':
#         login_form.next.data     = register_form.next.data = next
#         login_form.reg_next.data = register_form.reg_next.data = reg_next

#     if request.method == 'POST':
#         try:
#             login_form.validate()
#         except:
#             logmessage("custom_login: got an error when validating login")
#             pass
#     if request.method == 'POST' and login_form.validate():
#         user = None
#         user_email = None
#         if user_manager.enable_username:
#             user = user_manager.find_user_by_username(login_form.username.data)
#             user_email = None
#             if user and db_adapter.UserEmailClass:
#                 user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
#                         user_id=int(user.get_id()),
#                         is_primary=True,
#                         )
#             if not user and user_manager.enable_email:
#                 user, user_email = user_manager.find_user_by_email(login_form.username.data)
#         else:
#             user, user_email = user_manager.find_user_by_email(login_form.email.data)

#         if user:
#             return _do_login_user(user, login_form.password.data, secret, login_form.next.data, login_form.remember_me.data)

#     return render_template(user_manager.login_template, page_title=word('Sign In'), tab_title=word('Sign In'), form=login_form, login_form=login_form, register_form=register_form)

def unauthenticated():
    flash(word("You need to log in before you can access") + " " + word(request.path), 'error')
    the_url = url_for('user.login', next=fix_http(request.url))
    return redirect(the_url)

def unauthorized():
    flash(word("You are not authorized to access") + " " + word(request.path), 'error')
    return redirect(url_for('interview_list', next=fix_http(request.url)))

def my_default_url(error, endpoint, values):
    return url_for('index')

def make_safe_url(url):
    parts = urlparse.urlsplit(url)
    safe_url = parts.path
    if parts.query != '':
        safe_url += '?' + parts.query
    if parts.fragment != '':
        safe_url += '#' + parts.fragment
    return safe_url

import docassemble.webapp.setup
from docassemble.webapp.app_object import app, csrf, flaskbabel
from docassemble.webapp.db_object import db
from docassemble.webapp.users.forms import MyRegisterForm, MyInviteForm, MySignInForm, PhoneLoginForm, PhoneLoginVerifyForm, MFASetupForm, MFAReconfigureForm, MFALoginForm, MFAChooseForm, MFASMSSetupForm, MFAVerifySMSSetupForm, MyResendConfirmEmailForm
from docassemble.webapp.users.models import UserModel, UserAuthModel, MyUserInvitation
from flask_user import UserManager, SQLAlchemyAdapter
db_adapter = SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel, UserInvitationClass=MyUserInvitation)
from docassemble.webapp.users.views import user_profile_page
user_manager = UserManager()
user_manager.init_app(app, db_adapter=db_adapter, login_form=MySignInForm, register_form=MyRegisterForm, user_profile_view_function=user_profile_page, logout_view_function=logout, unauthorized_view_function=unauthorized, unauthenticated_view_function=unauthenticated, make_safe_url_function=make_safe_url, login_view_function=custom_login, resend_confirm_email_view_function=custom_resend_confirm_email, resend_confirm_email_form=MyResendConfirmEmailForm)
from flask_login import LoginManager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'custom_login'

#from twilio.rest import Capability as TwilioCapability
from twilio.rest import Client as TwilioRestClient
import twilio.twiml
from PIL import Image
import socket
import copy
import threading
import urllib
import urllib2
import tailer
import datetime
from dateutil import tz
import time
import pip.utils.logging
import pip
import shutil
import filecmp
import codecs
import weakref
import types
import stat
import pkg_resources
import babel.dates
import pytz
import httplib2
import zipfile
import traceback
from Crypto.Hash import MD5
import mimetypes
import logging
import cPickle as pickle
#import string
#import random
import cgi
import Cookie
import urlparse
import json
import base64
import requests
import redis
import yaml
import inspect
import pyotp
import qrcode
import qrcode.image.svg
import StringIO
from distutils.version import LooseVersion
from subprocess import call, Popen, PIPE
import subprocess
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import HtmlFormatter
from flask import make_response, abort, render_template, request, session, send_file, redirect, current_app, get_flashed_messages, flash, Markup, jsonify, Response, g
from flask import url_for
from flask_login import login_user, logout_user, current_user
from flask_user import login_required, roles_required
from flask_user import signals, user_logged_in, user_changed_password, user_registered, user_reset_password
#from flask_wtf.csrf import generate_csrf
from docassemble.webapp.develop import CreatePackageForm, CreatePlaygroundPackageForm, UpdatePackageForm, ConfigForm, PlaygroundForm, PlaygroundUploadForm, LogForm, Utilities, PlaygroundFilesForm, PlaygroundFilesEditForm, PlaygroundPackagesForm, GoogleDriveForm, GitHubForm, PullPlaygroundPackage
from flask_mail import Mail, Message
import flask_user.signals
import flask_user.translations
import flask_user.views
from werkzeug import secure_filename, FileStorage
from rauth import OAuth2Service
import apiclient
import oauth2client
import strict_rfc3339
import io
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from sqlalchemy import or_, and_
import docassemble.base.parse
import docassemble.base.pdftk
import docassemble.base.interview_cache
import docassemble.webapp.update
from docassemble.base.standardformatter import as_html, as_sms, get_choices, get_choices_with_abb
from docassemble.base.pandoc import word_to_markdown, convertible_mimetypes, convertible_extensions
from docassemble.webapp.screenreader import to_text
from docassemble.base.error import DAError, DAErrorNoEndpoint, DAErrorMissingVariable
from docassemble.base.functions import pickleable_objects, word, comma_and_list, get_default_timezone, ReturnValue
from docassemble.base.logger import logmessage
from docassemble.webapp.backend import cloud, initial_dict, can_access_file_number, get_info_from_file_number, da_send_mail, get_new_file_number, pad, unpad, encrypt_phrase, pack_phrase, decrypt_phrase, unpack_phrase, encrypt_dictionary, pack_dictionary, decrypt_dictionary, unpack_dictionary, nice_date_from_utc, fetch_user_dict, fetch_previous_user_dict, advance_progress, reset_user_dict, get_chat_log, savedfile_numbered_file, generate_csrf, get_info_from_file_reference, reference_exists
from docassemble.webapp.core.models import Attachments, Uploads, SpeakList, Supervisors, Shortener, Email, EmailAttachment
from docassemble.webapp.packages.models import Package, PackageAuth, Install
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype, make_package_zip
from docassemble.base.generate_key import random_string, random_lower_string, random_alphanumeric, random_digits
import docassemble.webapp.backend
import docassemble.base.util
from docassemble.base.util import DAEmail, DAEmailRecipientList, DAEmailRecipient, DAFileList, DAFile, DAObject

mimetypes.add_type('application/x-yaml', '.yml')
mimetypes.add_type('application/x-yaml', '.yaml')

redis_host = daconfig.get('redis', None)
if redis_host is None:
    redis_host = 'redis://localhost'

docassemble.base.util.set_redis_server(redis_host)

store = RedisStore(redis.StrictRedis(host=docassemble.base.util.redis_server, db=1))

kv_session = KVSessionExtension(store, app)

if 'twilio' in daconfig:
    twilio_config = dict()
    twilio_config['account sid'] = dict()
    twilio_config['number'] = dict()
    twilio_config['name'] = dict()
    if type(daconfig['twilio']) is not list:
        config_list = [daconfig['twilio']]
    else:
        config_list = daconfig['twilio']
    for tconfig in config_list:
        if type(tconfig) is dict and 'account sid' in tconfig and 'number' in tconfig:
            twilio_config['account sid'][unicode(tconfig['account sid'])] = 1
            twilio_config['number'][unicode(tconfig['number'])] = tconfig
            if 'default' not in twilio_config['name']:
                twilio_config['name']['default'] = tconfig
            if 'name' in tconfig:
                twilio_config['name'][tconfig['name']] = tconfig
        else:
            logmessage("do_sms: improper setup in twilio configuration")    
    if 'default' not in twilio_config['name']:
        twilio_config = None
else:
    twilio_config = None

app.debug = False
app.handle_url_build_error = my_default_url
app.config['USE_GOOGLE_LOGIN'] = False
app.config['USE_FACEBOOK_LOGIN'] = False
app.config['USE_AZURE_LOGIN'] = False
app.config['USE_GOOGLE_DRIVE'] = False
app.config['USE_PHONE_LOGIN'] = False
app.config['USE_GITHUB'] = False
if twilio_config is not None and daconfig.get('phone login', False) is True:
    app.config['USE_PHONE_LOGIN'] = True
if 'oauth' in daconfig:
    app.config['OAUTH_CREDENTIALS'] = daconfig['oauth']
    if 'google' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['google'] and daconfig['oauth']['google']['enable'] is False):
        app.config['USE_GOOGLE_LOGIN'] = True
    else:
        app.config['USE_GOOGLE_LOGIN'] = False
    if 'facebook' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['facebook'] and daconfig['oauth']['facebook']['enable'] is False):
        app.config['USE_FACEBOOK_LOGIN'] = True
    else:
        app.config['USE_FACEBOOK_LOGIN'] = False
    if 'azure' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['azure'] and daconfig['oauth']['azure']['enable'] is False):
        app.config['USE_AZURE_LOGIN'] = True
    else:
        app.config['USE_AZURE_LOGIN'] = False
    if 'googledrive' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['googledrive'] and daconfig['oauth']['googledrive']['enable'] is False):
        app.config['USE_GOOGLE_DRIVE'] = True
    else:
        app.config['USE_GOOGLE_DRIVE'] = False
    if 'github' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['github'] and daconfig['oauth']['github']['enable'] is False):
        app.config['USE_GITHUB'] = True
    else:
        app.config['USE_GITHUB'] = False
else:
    app.config['OAUTH_CREDENTIALS'] = dict()

def get_sms_session(phone_number, config='default'):
    sess_info = None
    if twilio_config is None:
        raise DAError("get_sms_session: Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
    if phone_number is None:
        raise DAError("terminate_sms_session: phone_number " + str(phone_number) + " is invalid")
    sess_contents = r.get('da:sms:client:' + phone_number + ':server:' + tconfig['number'])
    if sess_contents is not None:
        try:        
            sess_info = pickle.loads(sess_contents)
        except:
            logmessage("get_sms_session: unable to decode session information")
    sess_info['email'] = None
    if 'user_id' in sess_info and sess_info['user_id'] is not None:
        user = load_user(sess_info['user_id'])
        if user is not None:
            sess_info['email'] = user.email
    return sess_info

def initiate_sms_session(phone_number, yaml_filename=None, uid=None, secret=None, encrypted=None, user_id=None, email=None, new=False, config='default'):
    phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
    if phone_number is None:
        raise DAError("initiate_sms_session: phone_number " + str(phone_number) + " is invalid")
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    current_info = docassemble.base.functions.get_info('current_info')
    if yaml_filename is None:
        yaml_filename = current_info.get('yaml_filename', None)
        if yaml_filename is None:
            yaml_filename = default_yaml_filename
    temp_user_id = None
    if user_id is None and email is not None:
        user = UserModel.query.filter_by(email=email, active=True).first()
        if user is not None:
            user_id = user.id
    if user_id is None:
        if not new:
            if 'user' in current_info:
                if 'theid' in current_info['user']:
                    if current_info['user'].get('is_authenticated', False):
                        user_id = current_info['user']['theid']
                    else:
                        temp_user_id = current_info['user']['theid']
        if user_id is None and temp_user_id is None:
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            temp_user_id = new_temp_user.id
    if secret is None:
        if not new:
            secret = current_info['secret']
        if secret is None:
            secret = random_string(16)
    if uid is None:
        if new:
            uid = get_unique_name(yaml_filename, secret)
        else:
            uid = current_info.get('session', None)
            if uid is None:
                uid = get_unique_name(yaml_filename, secret)
    if encrypted is None:
        if new:
            encrypted = True
        else:
            encrypted = current_info['encrypted']
    sess_info = dict(yaml_filename=yaml_filename, uid=uid, secret=secret, number=phone_number, encrypted=encrypted, tempuser=temp_user_id, user_id=user_id)
    #logmessage("initiate_sms_session: setting da:sms:client:" + phone_number + ':server:' + tconfig['number'] + " to " + str(sess_info))
    r.set('da:sms:client:' + phone_number + ':server:' + tconfig['number'], pickle.dumps(sess_info))
    return True
        
def terminate_sms_session(phone_number, config='default'):
    sess_info = None
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
    r.delete('da:sms:client:' + phone_number + ':server:' + tconfig['number'])

def fix_http(url):
    if HTTP_TO_HTTPS:
        return re.sub(r'^http:', 'https:', url)
    else:
        return url

def remove_question_package(args):
    if '_question' in args:
        del args['_question']
    if '_package' in args:
        del args['_package']
    
def get_url_from_file_reference(file_reference, **kwargs):
    if isinstance(file_reference, DAFile) and hasattr(file_reference, 'number'):
        file_number = file_reference.number
        if can_access_file_number(file_number):
            url_properties = dict()
            if hasattr(file_reference, 'filename'):
                url_properties['filename'] = file_reference.filename
            if hasattr(file_reference, 'extension'):
                url_properties['ext'] = file_reference.extension
            for key, val in kwargs.iteritems():
                url_properties[key] = val
            the_file = SavedFile(file_number)
            return(the_file.url_for(**url_properties))
    file_reference = str(file_reference)
    if re.search(r'^http', file_reference):
        return(file_reference)
    if file_reference in ['login', 'signin']:
        remove_question_package(kwargs)
        return(url_for('user.login', **kwargs))
    elif file_reference in ['register']:
        remove_question_package(kwargs)
        return(url_for('user.register', **kwargs))
    elif file_reference == 'help':
        return('javascript:show_help_tab()');
    elif file_reference == 'interviews':
        remove_question_package(kwargs)
        return(url_for('interview_list', **kwargs))
    elif file_reference == 'interview_list':
        remove_question_package(kwargs)
        return(url_for('interview_list', **kwargs))
    elif file_reference == 'playground':
        remove_question_package(kwargs)
        return(url_for('playground_page', **kwargs))
    elif file_reference == 'playgroundtemplate':
        return(url_for('playground_files', section='template'))
    elif file_reference == 'playgroundstatic':
        return(url_for('playground_files', section='static'))
    elif file_reference == 'playgroundsources':
        return(url_for('playground_files', section='sources'))
    elif file_reference == 'playgroundmodules':
        return(url_for('playground_files', section='modules'))
    elif file_reference == 'playgroundpackages':
        remove_question_package(kwargs)
        return(url_for('playground_packages', **kwargs))
    elif file_reference == 'playgroundfiles':
        remove_question_package(kwargs)
        return(url_for('playground_files', **kwargs))
    elif file_reference == 'create_playground_package':
        remove_question_package(kwargs)
        return(url_for('create_playground_package', **kwargs))
    if re.match('[0-9]+', file_reference):
        remove_question_package(kwargs)
        file_number = file_reference
        if can_access_file_number(file_number):
            the_file = SavedFile(file_number)
            url = the_file.url_for(**kwargs)
        else:
            url = 'about:blank'
    else:
        question = kwargs.get('_question', None)
        package_arg = kwargs.get('_package', None)
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
            if question is not None and question.from_source is not None and hasattr(question.from_source, 'package'):
                the_package = question.from_source.package
            if the_package is None and package_arg is not None:
                the_package = package_arg
            if the_package is None:
                the_package = 'docassemble.base'
            parts = [the_package, file_reference]
        parts[1] = re.sub(r'^data/[^/]+/', '', parts[1])
        if reference_exists(parts[0] + ':data/static/' + parts[1]):
            url = fileroot + 'packagestatic/' + parts[0] + '/' + parts[1] + extn
        else:
            url = None
    return(url)

def user_id_dict():
    output = dict()
    for user in UserModel.query.all():
        output[user.id] = user
    anon = FakeUser()
    anon_role = FakeRole()
    anon_role.name = word('anonymous')
    anon.roles = [anon_role]
    anon.id = -1
    anon.firstname = 'Anonymous'
    anon.lastname = 'User'
    output[-1] = anon
    return output

def get_base_words():
    documentation = get_info_from_file_reference('docassemble.base:data/sources/base-words.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def get_documentation_dict():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def get_name_info():
    docstring = get_info_from_file_reference('docassemble.base:data/questions/docstring.yml')
    if 'fullpath' in docstring and docstring['fullpath'] is not None:
        with open(docstring['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def get_title_documentation():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/title_documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property

def pad_to_16(the_string):
    if len(the_string) >= 16:
        return the_string[:16]
    return str(the_string) + (16 - len(the_string)) * '0'

def decrypt_session(secret, user_code=None, filename=None):
    #logmessage("decrypt_session: user_code is " + str(user_code) + " and filename is " + str(filename))
    nowtime = datetime.datetime.utcnow()
    if user_code == None or filename == None or secret is None:
        return
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        phrase = decrypt_phrase(record.phrase, secret)
        record.phrase = pack_phrase(phrase)
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
            record.modtime = nowtime
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).all():
        the_dict = decrypt_dictionary(record.dictionary, secret)
        record.dictionary = pack_dictionary(the_dict)
        record.encrypted = False
        record.modtime = nowtime
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        phrase = decrypt_phrase(record.message, secret)
        record.message = pack_phrase(phrase)
        record.encrypted = False
        changed = True
    if changed:
        db.session.commit()
    return

def encrypt_session(secret, user_code=None, filename=None):
    #logmessage("encrypt_session: user_code is " + str(user_code) + " and filename is " + str(filename))
    nowtime = datetime.datetime.utcnow()
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
            record.modtime = nowtime
            changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=False).order_by(UserDict.indexno).all():
        the_dict = unpack_dictionary(record.dictionary)
        record.dictionary = encrypt_dictionary(the_dict, secret)
        record.encrypted = True
        record.modtime = nowtime
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        phrase = unpack_phrase(record.message)
        record.message = encrypt_phrase(phrase, secret)
        record.encrypted = True
        changed = True
    if changed:
        db.session.commit()
    return

def substitute_secret(oldsecret, newsecret):
    #logmessage("substitute_secret: " + repr(oldsecret) + " and " + repr(newsecret))
    if oldsecret == None or oldsecret == newsecret:
        return newsecret
    user_code = session.get('uid', None)
    if user_code == None or 'i' not in session:
        return newsecret
    filenames = set([session['i']])
    for the_record in db.session.query(UserDict.filename).filter_by(key=user_code).group_by(UserDict.filename).all():
        filenames.add(the_record.filename)
    for filename in filenames:
        #logmessage("substitute_secret: filename is " + str(filename) + " and key is " + str(user_code))
        changed = False
        for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
            phrase = decrypt_phrase(record.phrase, oldsecret)
            record.phrase = encrypt_phrase(phrase, newsecret)
            changed = True
        if changed:
            db.session.commit()
        changed = False
        for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
            if record.dictionary:
                the_dict = decrypt_dictionary(record.dictionary, oldsecret)
                record.dictionary = encrypt_dictionary(the_dict, newsecret)
                changed = True
        if changed:
            db.session.commit()
        changed = False
        for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).all():
            #logmessage("substitute_secret: record was encrypted")
            the_dict = decrypt_dictionary(record.dictionary, oldsecret)
            record.dictionary = encrypt_dictionary(the_dict, newsecret)
            changed = True
        if changed:
            db.session.commit()
        changed = False
        for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
            phrase = decrypt_phrase(record.message, oldsecret)
            record.message = encrypt_phrase(phrase, newsecret)
            changed = True
        if changed:
            db.session.commit()
    return newsecret

def MD5Hash(data=None):
    if data is None:
        data = ''
    h = MD5.new()
    h.update(data)
    return h

# def _do_login_user(user, password, secret, next, remember_me=False):
#     logmessage("_do_login_user")
#     if not user:
#         return unauthenticated()

#     if not _call_or_get(user.is_active):
#         flash(word('Your account has not been enabled.'), 'error')
#         return redirect(url_for('user.login'))

#     user_manager = current_app.user_manager
#     if user_manager.enable_email and user_manager.enable_confirm_email \
#             and not current_app.user_manager.enable_login_without_confirm_email \
#             and not user.has_confirmed_email():
#         url = url_for('user.resend_confirm_email')
#         flash('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="' + str(url) + '">Re-send confirmation email</a>.', 'error')
#         return redirect(url_for('user.login'))

#     login_user(user, remember=remember_me)

#     if 'i' in session and 'uid' in session:
#         save_user_dict_key(session['uid'], session['i'])
#         session['key_logged'] = True 

#     signals.user_logged_in.send(current_app._get_current_object(), user=user)

#     if 'tempuser' in session:
#         changed = False
#         for chat_entry in ChatLog.query.filter_by(temp_user_id=int(session['tempuser'])).all():
#             chat_entry.user_id = user.id
#             chat_entry.temp_user_id = None
#             changed = True
#         if changed:
#             db.session.commit()
#         changed = False
#         for chat_entry in ChatLog.query.filter_by(temp_owner_id=int(session['tempuser'])).all():
#             chat_entry.owner_id = user.id
#             chat_entry.temp_owner_id = None
#             changed = True
#         if changed:
#             db.session.commit()
#         del session['tempuser']
#     session['user_id'] = user.id
#     flash(word('You have signed in successfully.'), 'success')

#     newsecret = substitute_secret(secret, pad_to_16(MD5Hash(data=password).hexdigest()))
#     response = redirect(next)
#     response.set_cookie('secret', newsecret)
#     return response

def set_request_active(value):
    global request_active
    request_active = value

def syslog_message(message):
    message = re.sub(r'\n', ' ', message)
    if current_user and current_user.is_authenticated and not current_user.is_anonymous:
        the_user = current_user.email
    else:
        the_user = "anonymous"
    if request_active:
        sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': request.remote_addr, 'yamlfile': session.get('i', 'na'), 'user': the_user, 'session': session.get('uid', 'na')})
    else:
        sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': 'localhost', 'yamlfile': 'na', 'user': 'na', 'session': 'na'})

def syslog_message_with_timestamp(message):
    syslog_message(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message)
    
def copy_playground_modules():
    devs = list()
    for user in UserModel.query.filter_by(active=True).all():
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
        with open(os.path.join(local_dir, '__init__.py'), 'w') as the_file:
            the_file.write(init_py_file)

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
        result['interview'] = url_for('index', reset=1, i="docassemble.base:data/questions/examples/" + example + ".yml")
        example_file = 'docassemble.base:data/questions/examples/' + example + '.yml'
        result['image'] = url_for('static', filename='examples/' + example + ".png")
        file_info = get_info_from_file_reference(example_file)
        start_block = 1
        end_block = 2
        if 'fullpath' not in file_info or file_info['fullpath'] is None:
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
                has_context = False
                if re.search(r'metadata:', blocks[0]) and start_block > 0:
                    initial_block = 1
                else:
                    initial_block = 0
                if start_block > initial_block:
                    result['before_html'] = highlight("\n---\n".join(blocks[initial_block:start_block]) + "\n---", YamlLexer(), HtmlFormatter())
                    has_context = True
                else:
                    result['before_html'] = ''
                if len(blocks) > end_block:
                    result['after_html'] = highlight("---\n" + "\n---\n".join(blocks[end_block:len(blocks)]), YamlLexer(), HtmlFormatter())
                    has_context = True
                else:
                    result['after_html'] = ''
                result['source'] = "\n---\n".join(blocks[start_block:end_block])
                result['html'] = highlight(result['source'], YamlLexer(), HtmlFormatter())
                result['has_context'] = has_context
        examples.append(result)
    
def get_examples():
    examples = list()
    example_list_file = get_info_from_file_reference('docassemble.base:data/questions/example-list.yml')
    if 'fullpath' in example_list_file and example_list_file['fullpath'] is not None:
        example_list = list()
        with open(example_list_file['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            proc_example_list(ruamel.yaml.safe_load(content), examples)
    #logmessage("Examples: " + str(examples))
    return(examples)

def add_timestamps(the_dict, manual_user_id=None):
    nowtime = datetime.datetime.utcnow()
    the_dict['_internal']['starttime'] = nowtime 
    the_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated and not current_user.is_anonymous):
        if manual_user_id is not None:
            the_user_id = manual_user_id
        else:
            the_user_id = current_user.id
        the_dict['_internal']['accesstime'][the_user_id] = nowtime
    else:
        the_dict['_internal']['accesstime'][-1] = nowtime
    return

def fresh_dictionary():
    the_dict = copy.deepcopy(initial_dict)
    add_timestamps(the_dict)
    return the_dict    

def manual_checkout(manual_session_id=None, manual_filename=None):
    if manual_session_id is not None:
        session_id = manual_session_id
    else:
        session_id = session.get('uid', None)
    if manual_filename is not None:
        yaml_filename = manual_filename
    else:
        yaml_filename = session.get('i', None)
    if session_id is None or yaml_filename is None:
        return
    if current_user.is_anonymous:
        the_user_id = 't' + str(session.get('tempuser', None))
    else:
        the_user_id = current_user.id
    endpart = ':uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    pipe = r.pipeline()
    pipe.expire('da:session' + endpart, 12)
    pipe.expire('da:html' + endpart, 12)
    pipe.expire('da:interviewsession' + endpart, 12)
    pipe.expire('da:ready' + endpart, 12)
    pipe.expire('da:block' + endpart, 12)
    pipe.execute()
    #r.publish('da:monitor', json.dumps(dict(messagetype='refreshsessions')))
    #logmessage("Done checking out from " + endpart)
    return

def chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles):
    key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    if mode in ['peer', 'peerhelp']:
        peer_ok = True
    else:
        peer_ok = False
    if mode in ['help', 'peerhelp']:
        help_ok = True
    else:
        help_ok = False
    potential_partners = set()
    if help_ok and len(partner_roles) and not r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
        chat_session_key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        for role in partner_roles:
            for the_key in r.keys('da:monitor:role:' + role + ':userid:*'):
                user_id = re.sub(r'^.*:userid:', '', the_key)
                potential_partners.add(user_id)
        for the_key in r.keys('da:monitor:chatpartners:*'):
            user_id = re.sub(r'^.*chatpartners:', '', the_key)
            if user_id not in potential_partners:
                for chat_key in r.hgetall(the_key):
                    if chat_key == chat_session_key:
                        potential_partners.add(user_id)
    num_peer = 0
    if peer_ok:
        for sess_key in r.keys('da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
            if sess_key != key:
                num_peer += 1
    result = ChatPartners()
    result.peer = num_peer
    result.help = len(potential_partners)
    #return (dict(peer=num_peer, help=len(potential_partners)))
    return result
    
def do_redirect(url, is_ajax):
    if is_ajax:
        return jsonify(action='redirect', url=url, csrf_token=generate_csrf())
    else:
        return redirect(url)

def do_refresh(is_ajax, yaml_filename):
    if is_ajax:
        return jsonify(action='refresh', csrf_token=generate_csrf())
    else:
        return redirect(url_for('index', i=yaml_filename))

def standard_scripts():
    return '\n    <script src="' + url_for('static', filename='app/jquery.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/jquery.validate.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap/js/bootstrap.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/jasny-bootstrap.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-slider/dist/bootstrap-slider.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/signature.js') + '"></script>\n    <script src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>\n    <script src="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.js') + '"></script>\n'
    
def standard_html_start(interview_language=DEFAULT_LANGUAGE, debug=False):
    output = '<!DOCTYPE html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <link rel="shortcut icon" href="' + url_for('favicon') + '">\n    <link rel="apple-touch-icon" sizes="180x180" href="' + url_for('apple_touch_icon') + '">\n    <link rel="icon" type="image/png" href="' + url_for('favicon_md') + '" sizes="32x32">\n    <link rel="icon" type="image/png" href="' + url_for('favicon_sm') + '" sizes="16x16">\n    <link rel="manifest" href="' + url_for('favicon_manifest_json') + '">\n    <link rel="mask-icon" href="' + url_for('favicon_safari_pinned_tab') + '" color="' + daconfig.get('favicon mask color', '#698aa7') + '">\n    <meta name="theme-color" content="' + daconfig.get('favicon theme color', '#83b3dd') + '">\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap-theme.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/jasny-bootstrap.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />\n    <link href="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-slider/dist/css/bootstrap-slider.min.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/app.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/interview.css') + '" rel="stylesheet">'
    if debug:
        output += '\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'
    return output

def process_file(saved_file, orig_file, mimetype, extension, initial=True):
    if extension == "jpg" and daconfig.get('imagemagick', 'convert') is not None:
        unrotated = tempfile.NamedTemporaryFile(suffix=".jpg")
        rotated = tempfile.NamedTemporaryFile(suffix=".jpg")
        shutil.move(orig_file, unrotated.name)
        call_array = [daconfig.get('imagemagick', 'convert'), str(unrotated.name), '-auto-orient', '-density', '300', 'jpeg:' + rotated.name]
        result = call(call_array)
        if result == 0:
            saved_file.copy_from(rotated.name)
        else:
            saved_file.copy_from(unrotated.name)
    elif initial:
        shutil.move(orig_file, saved_file.path)
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
    #if extension == "pdf":
    #    make_image_files(saved_file.path)
    saved_file.finalize()
    
def save_user_dict_key(user_code, filename, priors=False):
    #logmessage("save_user_dict_key: called")
    interview_list = set([filename])
    found = set()
    if priors:
        for the_record in db.session.query(UserDict.filename).filter_by(key=user_code).group_by(UserDict.filename).all():
            # if the_record.filename not in interview_list:
            #     logmessage("Other interview found: " + the_record.filename)
            interview_list.add(the_record.filename)
    for filename_to_search in interview_list:
        the_record = UserDictKeys.query.filter_by(key=user_code, filename=filename_to_search, user_id=current_user.id).first()
        if the_record:
            found.add(filename_to_search)
    for filename_to_save in (interview_list - found):
        new_record = UserDictKeys(key=user_code, filename=filename_to_save, user_id=current_user.id)
        db.session.add(new_record)
        db.session.commit()
    return

def save_user_dict(user_code, user_dict, filename, secret=None, changed=False, encrypt=True, manual_user_id=None):
    #logmessage("save_user_dict: called with encrypt " + str(encrypt))
    nowtime = datetime.datetime.utcnow()
    user_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated and not current_user.is_anonymous):
        if manual_user_id is not None:
            the_user_id = manual_user_id
        else:
            the_user_id = current_user.id
        user_dict['_internal']['accesstime'][the_user_id] = nowtime
    else:
        user_dict['_internal']['accesstime'][-1] = nowtime
        the_user_id = None
    if changed is True:
        if encrypt:
            new_record = UserDict(modtime=nowtime, key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
        else:
            new_record = UserDict(modtime=nowtime, key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
        db.session.add(new_record)
        db.session.commit()
    else:
        max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(and_(UserDict.key == user_code, UserDict.filename == filename)).scalar()
        if max_indexno is None:
            if encrypt:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
            else:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
            db.session.add(new_record)
            db.session.commit()
        else:
            for record in UserDict.query.filter_by(key=user_code, filename=filename, indexno=max_indexno).all():
                if encrypt:
                    record.dictionary = encrypt_dictionary(user_dict, secret)
                    record.modtime = nowtime
                    record.encrypted = True
                else:
                    record.dictionary = pack_dictionary(user_dict)
                    record.modtime = nowtime
                    record.encrypted = False                   
            db.session.commit()
    return

def process_bracket_expression(match):
    try:
        inner = codecs.decode(match.group(1), 'base64').decode('utf8')
    except:
        inner = match.group(1)
    return("[" + repr(inner) + "]")

def myb64unquote(the_string):
    return(codecs.decode(the_string, 'base64').decode('utf8'))

def safeid(text):
    return codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '')

def from_safeid(text):
    return(codecs.decode(text, 'base64').decode('utf8'))

def progress_bar(progress):
    if progress == 0:
        return('');
    return('<div class="row"><div class="col-lg-6 col-md-8 col-sm-10"><div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="' + str(progress) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(progress) + '%;"></div></div></div></div>\n')

def get_unique_name(filename, secret):
    nowtime = datetime.datetime.utcnow()
    while True:
        newname = random_string(32)
        obtain_lock(newname, filename)
        existing_key = UserDict.query.filter_by(key=newname).first()
        if existing_key:
            release_lock(newname, filename)
            continue
        new_user_dict = UserDict(modtime=nowtime, key=newname, filename=filename, dictionary=encrypt_dictionary(fresh_dictionary(), secret))
        db.session.add(new_user_dict)
        db.session.commit()
        return newname

def get_attachment_info(the_user_code, question_number, filename, secret):
    the_user_dict = None
    existing_entry = Attachments.query.filter_by(key=the_user_code, question=question_number, filename=filename).first()
    if existing_entry and existing_entry.dictionary:
        if existing_entry.encrypted:
            the_user_dict = decrypt_dictionary(existing_entry.dictionary, secret)
        else:
            the_user_dict = unpack_dictionary(existing_entry.dictionary)
    return the_user_dict, existing_entry.encrypted

def update_attachment_info(the_user_code, the_user_dict, the_interview_status, secret, encrypt=True):
    Attachments.query.filter_by(key=the_user_code, question=the_interview_status.question.number, filename=the_interview_status.question.interview.source.path).delete()
    db.session.commit()
    if encrypt:
        new_attachment = Attachments(key=the_user_code, dictionary=encrypt_dictionary(the_user_dict, secret), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=True)
    else:
        new_attachment = Attachments(key=the_user_code, dictionary=pack_dictionary(the_user_dict), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=False)
    db.session.add(new_attachment)
    db.session.commit()
    return

def obtain_lock(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    found = False
    count = 4
    while count > 0:
        record = r.get(key)
        if record:
            time.sleep(1.0)
        else:
            found = False
            break
        found = True
        count -= 1
    if found:
        release_lock(user_code, filename)
    pipe = r.pipeline()
    pipe.set(key, 1)
    pipe.expire(key, 4)
    
def release_lock(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    r.delete(key)

def make_navbar(status, page_title, page_short_title, steps, show_login, chat_info, debug_mode):
    navbar = """\
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
"""
    navbar += """\
          <button id="mobile-toggler" type="button" class="navbar-toggle collapsed mynavbar-toggle" data-toggle="collapse" data-target="#navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
"""
    if status.question.can_go_back and steps > 1:
        navbar += """\
          <span class="navbar-brand"><form style="inline-block" id="backbutton" method="POST"><input type="hidden" name="csrf_token" value=""" + '"' + generate_csrf() + '"' + """/><input type="hidden" name="_back_one" value="1"><button class="dabackicon" type="submit"><i class="glyphicon glyphicon-chevron-left dalarge"></i></button></form></span>
"""
    navbar += """\
          <a href="#question" data-toggle="tab" class="navbar-brand"><span class="hidden-xs">""" + status.question.interview.get_title().get('full', page_title) + """</span><span class="visible-xs-block">""" + status.question.interview.get_title().get('short', page_short_title) + """</span></a>
          <a class="invisible" id="questionlabel" href="#question" data-toggle="tab">""" + word('Question') + """</a>
"""
    help_message = word("Help is available")
    extra_help_message = word("Help is available for this question")
    phone_message = word("Phone help is available")
    chat_message = word("Live chat is available")
    source_message = word("How this question came to be asked")
    if len(status.helpText):
        if status.question.helptext is None:
            navbar += '          <a title="' + help_message + '" class="mynavbar-text" href="#help" id="helptoggle" data-toggle="tab">' + word('Help') + '</a> <a title="' + phone_message + '" id="daPhoneAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-earphone chat-active"></i></a> <a title="' + chat_message + '" id="daChatAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-comment"></i></a>'
        else:
            navbar += '          <a title="' + extra_help_message + '" class="mynavbar-text daactivetext" href="#help" id="helptoggle" data-toggle="tab">' + word('Help') + ' <i class="glyphicon glyphicon-star"></i></a> <a title="' + phone_message + '" id="daPhoneAvailable" class="mynavbar-icon daactivetext invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-earphone chat-active"></i></a> <a title="' + chat_message + '" id="daChatAvailable" class="mynavbar-icon daactivetext invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-comment"></i></a>'
    elif chat_info['availability'] == 'available':
        navbar += '          <a title="' + phone_message + '" id="daPhoneAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-earphone chat-active"></i></a> <a title="' + chat_message + '" id="daChatAvailable" class="mynavbar-icon invisible" href="#help" data-toggle="tab"><i class="glyphicon glyphicon-comment"></i></a>'
    navbar += """
        </div>
        <div class="collapse navbar-collapse" id="navbar-collapse">
          <ul class="nav navbar-nav navbar-left hidden-xs">
"""
    if debug_mode:
        navbar += """\
            <li><a class="no-outline" title=""" + repr(str(source_message)) + """ id="sourcetoggle" href="#source" data-toggle="collapse" aria-expanded="false" aria-controls="source">""" + word('Source') + """</a></li>
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
    if ALLOW_REGISTRATION:
        sign_in_text = word('Sign in or sign up to save answers')
    else:
        sign_in_text = word('Sign in to save answers')
    if show_login:
        if current_user.is_anonymous:
            if custom_menu:
                navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '<span class="caret"></span></a><ul class="dropdown-menu">' + custom_menu + '<li><a href="' + url_for('user.login') + '">' + sign_in_text + '</a></li></ul></li>' + "\n"
            else:
                navbar += '            <li><a href="' + url_for('user.login') + '">' + sign_in_text + '</a></li>' + "\n"
        else:
            navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle hidden-xs" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + (current_user.email if current_user.email else re.sub(r'.*\$', '', current_user.social_id)) + '<span class="caret"></span></a><ul class="dropdown-menu">'
            if custom_menu:
                navbar += custom_menu
            if current_user.has_role('admin', 'developer', 'advocate'):
                navbar +='<li><a href="' + url_for('monitor') + '">' + word('Monitor') + '</a></li>'
            if current_user.has_role('admin', 'developer'):
                navbar +='<li><a href="' + url_for('package_page') + '">' + word('Package Management') + '</a></li>'
                navbar +='<li><a href="' + url_for('logs') + '">' + word('Logs') + '</a></li>'
                navbar +='<li><a href="' + url_for('playground_page') + '">' + word('Playground') + '</a></li>'
                navbar +='<li><a href="' + url_for('utilities') + '">' + word('Utilities') + '</a></li>'
                if current_user.has_role('admin'):
                    navbar +='<li><a href="' + url_for('user_list') + '">' + word('User List') + '</a></li>'
                    #navbar +='<li><a href="' + url_for('privilege_list') + '">' + word('Privileges List') + '</a></li>'
                    navbar +='<li><a href="' + url_for('config_page') + '">' + word('Configuration') + '</a></li>'
            navbar += '<li><a href="' + url_for('interview_list') + '">' + word('My Interviews') + '</a></li><li><a href="' + url_for('user_profile_page') + '">' + word('Profile') + '</a></li><li><a href="' + url_for('user.logout') + '">' + word('Sign Out') + '</a></li></ul></li>'
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

def delete_session():
    for key in ['i', 'uid', 'key_logged', 'action', 'tempuser', 'user_id', 'encrypted', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'playgroundfile', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules', 'playgroundpackages', 'update', 'phone_number', 'otp_secret', 'validated_user', 'github_state', 'github_next']:
        if key in session:
            del session[key]
    return

def backup_session():
    backup = dict()
    for key in ['i', 'uid', 'key_logged', 'action', 'tempuser', 'user_id', 'encrypted', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'playgroundfile', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules', 'playgroundpackages', 'update', 'phone_number', 'otp_secret', 'validated_user', 'github_state', 'github_next']:
        if key in session:
            backup[key] = session[key]
    return backup

def restore_session(backup):
    for key in ['i', 'uid', 'key_logged', 'action', 'tempuser', 'user_id', 'encrypted', 'google_id', 'google_email', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'playgroundfile', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules', 'playgroundpackages', 'update', 'phone_number', 'otp_secret', 'validated_user', 'github_state', 'github_next']:
        if key in backup:
            session[key] = backup[key]

def reset_session(yaml_filename, secret, retain_code=False):
    #logmessage("reset_session: retain_code is " + str(retain_code))
    session['i'] = yaml_filename
    if retain_code is False or 'uid' not in session:
        session['uid'] = get_unique_name(yaml_filename, secret)
    if 'key_logged' in session:
        del session['key_logged']
    if 'action' in session:
        del session['action']
    user_code = session['uid']
    #logmessage("reset_session: user_code is " + str(user_code))
    user_dict = fresh_dictionary()
    return(user_code, user_dict)

def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url

def user_can_edit_package(pkgname=None, giturl=None):
    if pkgname is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(and_(Package.name == pkgname, Package.active == True))
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    if giturl is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(and_(Package.giturl == giturl, Package.active == True))
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    return(False)

def uninstall_package(packagename):
    #logmessage("server uninstall_package: " + packagename)
    existing_package = Package.query.filter_by(name=packagename, active=True).order_by(Package.id.desc()).first()
    if existing_package is None:
        flash(word("Package did not exist"), 'error')
        return
    for package in Package.query.filter_by(name=packagename, active=True).all():
        package.active = False
    db.session.commit()
    return

def summarize_results(results, logmessages):
    output = '<br>'.join([x + ':&nbsp;' + results[x] for x in sorted(results.keys())])
    if len(logmessages):
        if len(output):
            output += '<br><br><strong>'+ word("pip log") + ':</strong><br>'
        else:
            output = ''
        output += re.sub(r'\n', r'<br>', logmessages)
    return Markup(output)

def install_zip_package(packagename, file_number):
    #logmessage("install_zip_package: " + packagename + " " + str(file_number))
    existing_package = Package.query.filter_by(name=packagename).order_by(Package.id.desc()).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, upload=file_number, active=True, type='zip', version=1)
        db.session.add(package_auth)
        db.session.add(package_entry)
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None and existing_package.upload != file_number:
            SavedFile(existing_package.upload).delete()
        existing_package.package_auth.user_id = current_user.id
        existing_package.package_auth.authtype = 'owner'
        existing_package.upload = file_number
        existing_package.active = True
        existing_package.limitation = None
        existing_package.giturl = None
        existing_package.type = 'zip'
        existing_package.version += 1
    db.session.commit()
    return

def install_git_package(packagename, giturl):
    #logmessage("install_git_package: " + packagename + " " + str(giturl))
    if Package.query.filter_by(name=packagename).first() is None and Package.query.filter_by(giturl=giturl).first() is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, giturl=giturl, package_auth=package_auth, version=1, active=True, type='git', upload=None, limitation=None)
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        existing_package = Package.query.filter_by(name=packagename).order_by(Package.id.desc()).first()
        if existing_package is None:
            existing_package = Package.query.filter_by(giturl=giturl).order_by(Package.id.desc()).first()
        if existing_package is not None:
            if existing_package.type == 'zip' and existing_package.upload is not None:
                SavedFile(existing_package.upload).delete()
            existing_package.package_auth.user_id = current_user.id
            existing_package.package_auth.authtype = 'owner'
            existing_package.name = packagename
            existing_package.giturl = giturl
            existing_package.upload = None
            existing_package.version += 1
            existing_package.limitation = None
            existing_package.active = True
            existing_package.type = 'git'
            db.session.commit()
        else:
            logmessage("install_git_package: package " + str(giturl) + " appeared to exist but could not be found")
    return

def install_pip_package(packagename, limitation):
    existing_package = Package.query.filter_by(name=packagename).order_by(Package.id.desc()).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, limitation=limitation, version=1, active=True, type='pip')
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None:
            SavedFile(existing_package.upload).delete()
        existing_package.package_auth.user_id = current_user.id
        existing_package.package_auth.authtype = 'owner'
        existing_package.version += 1
        existing_package.type = 'pip'
        existing_package.limitation = limitation
        existing_package.giturl = None
        existing_package.upload = None
        existing_package.active = True
        db.session.commit()
    return

def get_package_info():
    if current_user.has_role('admin'):
        is_admin = True
    else:
        is_admin = False
    package_list = list()
    package_auth = dict()
    seen = dict()
    for auth in PackageAuth.query.all():
        if auth.package_id not in package_auth:
            package_auth[auth.package_id] = dict()
        package_auth[auth.package_id][auth.user_id] = auth.authtype
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        if package.name in seen:
            continue
        seen[package.name] = 1
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

def name_of_user(user, include_email=False):
    output = ''
    if user.first_name:
        output += user.first_name
        if user.last_name:
            output += ' '
    if user.last_name:
        output += user.last_name
    if include_email and user.email:
        if output:
            output += ', '
        output += user.email
    return output

def flash_as_html(message, message_type="info", is_ajax=True):
    if message_type == 'error':
        message_type = 'danger'
    output = """
        <div class="alert alert-""" + str(message_type) + """"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>""" + str(message) + """</div>
"""
    if not is_ajax:
        flash(message, message_type)
    return output

def make_example_html(examples, first_id, example_html, data_dict):
    example_html.append('          <ul class="nav nav-pills nav-stacked example-list example-hidden">\n')
    for example in examples:
        if 'list' in example:
            example_html.append('          <li><a class="example-heading">' + example['title'] + '</a>')
            make_example_html(example['list'], first_id, example_html, data_dict)
            example_html.append('          </li>')
            continue
        if len(first_id) == 0:
            first_id.append(example['id'])
        example_html.append('            <li><a class="example-link" data-example="' + example['id'] + '">' + example['title'] + '</a></li>')
        data_dict[example['id']] = example
    example_html.append('          </ul>')

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

def infobutton(title):
    docstring = ''
    if 'doc' in title_documentation[title]:
        docstring += noquote(title_documentation[title]['doc']) + "<br>"
    if 'url' in title_documentation[title]:
        docstring += "<a target='_blank' href='" + title_documentation[title]['url'] + "'>" + word("View documentation") + "</a>"
    return '&nbsp;<a class="daquestionsign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + docstring + '" title="' + word("Help") + '" data-selector="true" data-title="' + noquote(title_documentation[title].get('title', title)) + '"><i class="glyphicon glyphicon-question-sign"></i></a>'

def search_button(var, field_origins, name_origins, interview_source, all_sources):
    in_this_file = False
    usage = dict()
    if var in field_origins:
        for x in sorted(field_origins[var]):
            if x is interview_source:
                in_this_file = True
            else:
                if x.path not in usage:
                    usage[x.path] = set()
                usage[x.path].add('defined')
                all_sources.add(x)
    if var in name_origins:
        for x in sorted(name_origins[var]):
            if x is interview_source:
                in_this_file = True
            else:
                if x.path not in usage:
                    usage[x.path] = set()
                usage[x.path].add('used')
                all_sources.add(x)
    usage_type = [set(), set(), set()]
    for path, the_set in usage.iteritems():
        if 'defined' in the_set and 'used' in the_set:
            usage_type[2].add(path)
        elif 'used' in the_set:
            usage_type[1].add(path)
        elif 'defined' in the_set:
            usage_type[0].add(path)
        else:
            continue
    messages = list()
    if len(usage_type[2]):
        messages.append(word("Defined and used in " + docassemble.base.functions.comma_and_list(sorted(usage_type[2]))))
    elif len(usage_type[0]):
        messages.append(word("Defined in") + ' ' + docassemble.base.functions.comma_and_list(sorted(usage_type[0])))
    elif len(usage_type[2]):
        messages.append(word("Used in") + ' ' + docassemble.base.functions.comma_and_list(sorted(usage_type[0])))
    if len(messages):
        title = 'title="' + '; '.join(messages) + '" '
    else:
        title = ''
    if in_this_file:
        classname = 'dasearchthis'
    else:
        classname = 'dasearchother'
    return '<a class="dasearchicon ' + classname + '" ' + title + 'data-name="' + noquote(var) + '"><i class="glyphicon glyphicon-search"></i></a>'

search_key = """
                  <tr><td><h4>""" + word("Note") + """</h4></td></tr>
                  <tr><td><a class="dasearchicon dasearchthis"><i class="glyphicon glyphicon-search"></i></a> """ + word("means the name is located in this file") + """</td></tr>
                  <tr><td><a class="dasearchicon dasearchother"><i class="glyphicon glyphicon-search"></i></a> """ + word("means the name may be located in a file included by reference, such as:") + """</td></tr>"""

def find_needed_names(interview, needed_names, the_name=None, the_question=None):
    if the_name is not None:
        needed_names.add(the_name)
        if the_name in interview.questions:
            for lang in interview.questions[the_name]:
                for question in interview.questions[the_name][lang]:
                    find_needed_names(interview, needed_names, the_question=question)
    elif the_question is not None:
        for the_set in (the_question.mako_names, the_question.names_used):
            for name in the_set:
                if name in needed_names:
                    continue
                find_needed_names(interview, needed_names, the_name=name)
    else:
        for question in interview.questions_list:
            if not (question.is_mandatory or question.is_initial or question.question_type == "objects"):
                continue
            find_needed_names(interview, needed_names, the_question=question)

def get_vars_in_use(interview, interview_status, debug_mode=False):
    user_dict = fresh_dictionary()
    has_no_endpoint = False
    if 'uid' not in session:
        session['uid'] = random_string(32)
    if debug_mode:
        has_error = True
        error_message = "Not checking variables because in debug mode."
        error_type = Exception
    else:
        try:
            interview.assemble(user_dict, interview_status)
            has_error = False
        except Exception as errmess:
            has_error = True
            error_message = str(errmess)
            error_type = type(errmess)
            logmessage("get_vars_in_use: failed assembly with error type " + str(error_type) + " and message: " + error_message)
    fields_used = set()
    names_used = set()
    field_origins = dict()
    name_origins = dict()
    all_sources = set()
    names_used.update(interview.names_used)
    for question in interview.questions_list:
        for the_set in (question.mako_names, question.names_used, question.fields_used):
            names_used.update(the_set)
            for key in the_set:
                if key not in name_origins:
                    name_origins[key] = set()
                name_origins[key].add(question.from_source)
        fields_used.update(question.fields_used)
        for key in question.fields_used:
            if key not in field_origins:
                field_origins[key] = set()
            field_origins[key].add(question.from_source)
            # if key == 'advocate':
            #     try:
            #         logmessage("Found advocate in " + question.content.original_text)
            #     except:
            #         logmessage("Found advocate")
    for val in interview.questions:
        names_used.add(val)
        if val not in name_origins:
            name_origins[val] = set()
        for lang in interview.questions[val]:
            for q in interview.questions[val][lang]:
                name_origins[val].add(q.from_source)
        fields_used.add(val)
        if val not in field_origins:
            field_origins[val] = set()
        for lang in interview.questions[val]:
            for q in interview.questions[val][lang]:
                field_origins[val].add(q.from_source)
    needed_names = set()
    find_needed_names(interview, needed_names)
    functions = set()
    modules = set()
    classes = set()
    name_info = copy.deepcopy(base_name_info)
    area = SavedFile(current_user.id, fix=True, section='playgroundtemplate')
    templates = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundstatic')
    static = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundsources')
    sources = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    area = SavedFile(current_user.id, fix=True, section='playgroundmodules')
    avail_modules = sorted([re.sub(r'.py$', '', f) for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f))])
    for val in user_dict:
        if type(user_dict[val]) is types.FunctionType:
            functions.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val) + '()', 'tag': str(val) + str(inspect.formatargspec(*inspect.getargspec(user_dict[val])))}
        elif type(user_dict[val]) is types.ModuleType:
            modules.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val)}
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
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val), 'bases': bases, 'methods': method_list}
    for val in docassemble.base.functions.pickleable_objects(user_dict):
        names_used.add(val)
        if val not in name_info:
            name_info[val] = dict()
        name_info[val]['type'] = user_dict[val].__class__.__name__
    for var in base_name_info:
        if base_name_info[var]['show']:
            names_used.add(var)
    names_used = set([i for i in names_used if not extraneous_var.search(i)])
    for var in ['_internal']:
        names_used.discard(var)
    view_doc_text = word("View documentation")
    word_documentation = word("Documentation")
    attr_documentation = word("Show attributes")
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
    vocab_set = (names_used | functions | classes | modules | fields_used | set([key for key in base_name_info if not re.search(r'\.', key)]) | set([key for key in name_info if not re.search(r'\.', key)]) | set(templates) | set(static) | set(sources) | set(avail_modules) | set(interview.images.keys()))
    vocab_set = set([i for i in vocab_set if not extraneous_var.search(i)])
    names_used = names_used.difference( functions | classes | modules | set(avail_modules) )
    undefined_names = names_used.difference(fields_used | set(base_name_info.keys()) )
    for var in ['_internal']:
        undefined_names.discard(var)
        vocab_set.discard(var)
    names_used = names_used.difference( undefined_names )
    if len(undefined_names):
        content += '\n                  <tr><td><h4>' + word('Undefined names') + infobutton('undefined') + '</h4></td></tr>'
        for var in sorted(undefined_names):
            content += '\n                  <tr><td>' + search_button(var, field_origins, name_origins, interview.source, all_sources) + '<a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-danger playground-variable">' + var + '</a></td></tr>'
    if len(names_used):
        content += '\n                  <tr><td><h4>' + word('Variables') + infobutton('variables') + '</h4></td></tr>'
        has_parent = dict()
        has_children = set()
        for var in names_used:
            parent = re.sub(r'\..*', '', var)
            if parent != var:
                has_parent[var] = parent
                has_children.add(parent)
        in_nest = False
        for var in sorted(names_used):
            if var in has_parent:
                hide_it = ' style="display: none" data-parent="' + noquote(has_parent[var]) + '"'
            else:
                hide_it = ''
            if var in base_name_info:
                if not base_name_info[var]['show']:
                    continue
            if var in documentation_dict or var in base_name_info:
                class_type = 'info'
                title = 'title="' + word("Special variable") + '" '
            elif var not in needed_names:
                class_type = 'warning'
                title = 'title="' + word("Possibly not used") + '" '
            else:
                class_type = 'primary'
                title = ''
            content += '\n                  <tr' + hide_it + '><td>' + search_button(var, field_origins, name_origins, interview.source, all_sources) + '<a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" ' + title + 'class="label label-' + class_type + ' playground-variable">' + var + '</a>'
            if var in has_children:
                content += '&nbsp;<a class="dashowattributes" role="button" data-name="' + noquote(var) + '" title="' + attr_documentation + '"><i class="glyphicon glyphicon-option-horizontal"></i></a>'
            if var in name_info and 'type' in name_info[var] and name_info[var]['type']:
                content +='&nbsp;<span data-ref="' + noquote(name_info[var]['type']) + '" class="daparenthetical">(' + name_info[var]['type'] + ')</span>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
        if len(all_sources):
            content += search_key
            content += '\n                <tr><td>'
            content += '\n                  <ul>'
            for path in sorted([x.path for x in all_sources]):
                content += '\n                    <li><a target="_blank" href="' + url_for('view_source', i=path)+ '">' + path + '<a></li>'
            content += '\n                  </ul>'
            content += '\n                </td></tr>'
    if len(functions):
        content += '\n                  <tr><td><h4>' + word('Functions') + infobutton('functions') + '</h4></td></tr>'
        for var in sorted(functions):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-warning playground-variable">' + name_info[var]['tag'] + '</a>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(classes):
        content += '\n                  <tr><td><h4>' + word('Classes') + infobutton('classes') + '</h4></td></tr>'
        for var in sorted(classes):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-info playground-variable">' + name_info[var]['name'] + '</a>'
            if name_info[var]['bases']:
                content += '&nbsp;<span data-ref="' + noquote(name_info[var]['bases'][0]) + '" class="daparenthetical">(' + name_info[var]['bases'][0] + ')</span>'
            if name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + var + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            if len(name_info[var]['methods']):
                content += '&nbsp;<a class="dashowmethods" role="button" data-showhide="XMETHODX' + var + '" title="' + word('Methods') + '"><i class="glyphicon glyphicon-cog"></i></a>'
                content += '<div style="display: none;" id="XMETHODX' + var + '"><table><tbody>'
                for method_info in name_info[var]['methods']:
                    content += '<tr><td><a data-name="' + noquote(method_info['name']) + '" data-insert="' + noquote(method_info['insert']) + '" class="label label-warning playground-variable">' + method_info['tag'] + '</a>'
                    if method_info['doc']:
                        content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + method_info['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + noquote(method_info['name']) + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
                    content += '</td></tr>'
                content += '</tbody></table></div>'
            content += '</td></tr>'
    if len(modules):
        content += '\n                  <tr><td><h4>' + word('Modules defined') + infobutton('modules') + '</h4></td></tr>'
        for var in sorted(modules):
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="label label-success playground-variable">' + name_info[var]['name'] + '</a>'
            if name_info[var]['doc']:
                content += '&nbsp;<a class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title="' + word_documentation + '" data-selector="true" data-title="' + noquote(var) + '"><i class="glyphicon glyphicon-info-sign"></i></a>'
            content += '</td></tr>'
    if len(avail_modules):
        content += '\n                  <tr><td><h4>' + word('Modules available in Playground') + infobutton('playground_modules') + '</h4></td></tr>'
        for var in avail_modules:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert=".' + noquote(var) + '" class="label label-success playground-variable">.' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(templates):
        content += '\n                  <tr><td><h4>' + word('Templates') + infobutton('templates') + '</h4></td></tr>'
        for var in templates:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(static):
        content += '\n                  <tr><td><h4>' + word('Static files') + infobutton('static') + '</h4></td></tr>'
        for var in static:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(sources):
        content += '\n                  <tr><td><h4>' + word('Source files') + infobutton('sources') + '</h4></td></tr>'
        for var in sources:
            content += '\n                  <tr><td><a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-default playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    if len(interview.images):
        content += '\n                  <tr><td><h4>' + word('Decorations') + infobutton('decorations') + '</h4></td></tr>'
        for var in sorted(interview.images):
            content += '\n                  <tr><td>'
            the_ref = get_url_from_file_reference(interview.images[var].get_reference())
            if the_ref is None:
                content += '<a title="' + word("This image file does not exist") + '" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-danger playground-variable">' + noquote(var) + '</a>'
            else:
                content += '<img class="daimageicon" src="' + get_url_from_file_reference(interview.images[var].get_reference()) + '">&nbsp;<a data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="label label-primary playground-variable">' + noquote(var) + '</a>'
            content += '</td></tr>'
    content += "\n                  <tr><td><br><em>" + word("Type Ctrl-space to autocomplete.") + "</em></td><tr>"
    return content, sorted(vocab_set)

def make_png_for_pdf(doc, prefix):
    if prefix == 'page':
        resolution = PNG_RESOLUTION
    else:
        resolution = PNG_SCREEN_RESOLUTION
    task = docassemble.webapp.worker.make_png_for_pdf.delay(doc, prefix, resolution, session['uid'], PDFTOPPM_COMMAND)
    return task.id

def wait_for_task(task_id):
    logmessage("wait_for_task: starting")
    try:
        result = docassemble.webapp.worker.workerapp.AsyncResult(id=task_id)
        if result.ready():
            logmessage("wait_for_task: was ready")
            return True
        logmessage("wait_for_task: waiting for task to complete")
        result.get(timeout=60)
        logmessage("wait_for_task: returning true")
        return True
    except Exception as the_error:
        logmessage("wait_for_task: got error: " + str(the_error))
        return False

# def make_image_files(path):
#     if PDFTOPPM_COMMAND is not None:
#         args = [PDFTOPPM_COMMAND, '-r', str(PNG_RESOLUTION), '-png', path, path + 'page']
#         result = call(args)
#         if result > 0:
#             raise DAError("Call to pdftoppm failed")
#         args = [PDFTOPPM_COMMAND, '-r', str(PNG_SCREEN_RESOLUTION), '-png', path, path + 'screen']
#         result = call(args)
#         if result > 0:
#             raise DAError("Call to pdftoppm failed")
#     return

def trigger_update(except_for=None):
    logmessage("trigger_update: except_for is " + str(except_for))
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url and not (except_for and host.hostname == except_for):
                if host.hostname == hostname:
                    the_url = 'http://localhost:9001'
                else:
                    the_url = host.url
                args = [SUPERVISORCTL, '-s', the_url, 'start update']
                result = call(args)
                if result == 0:
                    logmessage("trigger_update: sent reset to " + str(host.hostname))
                else:
                    logmessage("trigger_update: call to supervisorctl on " + str(host.hostname) + " was not successful")
    return

def restart_on(host):
    logmessage("restart_on: " + str(host.hostname))
    if host.hostname == hostname:
        the_url = 'http://localhost:9001'
    else:
        the_url = host.url
    if re.search(r':(web|all):', host.role):
        args = [SUPERVISORCTL, '-s', the_url, 'start reset']
        result = call(args)
        if result == 0:
            logmessage("restart_on: sent reset to " + str(host.hostname))
        else:
            logmessage("restart_on: call to supervisorctl with reset on " + str(host.hostname) + " was not successful")
    return

def restart_all():
    restart_others()
    restart_this()
    return

def restart_this():
    logmessage("restart_this: hostname is " + str(hostname))
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url:
                logmessage("restart_this: considering " + str(host.hostname) + " against " + str(hostname))
                if host.hostname == hostname:
                    restart_on(host)
            #else:
            #    logmessage("restart_this: unable to get host url")
    else:
        logmessage("restart_this: touching wsgi file")
        wsgi_file = WEBAPP_PATH
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a'):
                os.utime(wsgi_file, None)
    return

def restart_others():
    logmessage("restart_others: starting")
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url:
                if host.hostname != hostname:
                    restart_on(host)
            #else:
            #    logmessage("restart_others: unable to get host url")
    return

def current_info(yaml=None, req=None, action=None, location=None, interface='web'):
    if current_user.is_authenticated and not current_user.is_anonymous:
        ext = dict(email=current_user.email, roles=[role.name for role in current_user.roles], the_user_id=current_user.id, theid=current_user.id, firstname=current_user.first_name, lastname=current_user.last_name, nickname=current_user.nickname, country=current_user.country, subdivisionfirst=current_user.subdivisionfirst, subdivisionsecond=current_user.subdivisionsecond, subdivisionthird=current_user.subdivisionthird, organization=current_user.organization, timezone=current_user.timezone)
    else:
        ext = dict(email=None, the_user_id='t' + str(session.get('tempuser', None)), theid=session.get('tempuser', None), roles=list())
    headers = dict()
    if req is None:
        url = 'http://localhost'
        url_root = 'http://localhost'
        secret = None
        clientip = None
    else:
        url = req.base_url
        url_root = req.url_root
        secret = req.cookies.get('secret', None)
        for key, value in req.headers.iteritems():
            headers[key] = value
        clientip = req.remote_addr
    if secret is not None:
        secret = str(secret)
    return_val = {'session': session.get('uid', None), 'secret': secret, 'yaml_filename': yaml, 'interface': interface, 'url': url, 'url_root': url_root, 'encrypted': session.get('encrypted', True), 'user': {'is_anonymous': current_user.is_anonymous, 'is_authenticated': current_user.is_authenticated}, 'headers': headers, 'clientip': clientip}
    if action is not None:
        return_val.update(action)
        # return_val['orig_action'] = action['action']
        # return_val['orig_arguments'] = action['arguments']
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
    
def call_sync():
    if not USING_SUPERVISOR:
        return
    args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'start', 'sync']
    result = call(args)
    if result == 0:
        logmessage("call_sync: sent message to " + hostname)
    else:
        logmessage("call_sync: call to supervisorctl on " + hostname + " was not successful")
        abort(404)
    in_process = 1
    counter = 10
    check_args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'status', 'sync']
    while in_process == 1 and counter > 0:
        output, err = Popen(check_args, stdout=PIPE, stderr=PIPE).communicate()
        if not re.search(r'RUNNING', output):
            in_process = 0
        else:
            time.sleep(1)
        counter -= 1
    return

def formatted_current_time():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime('%H:%M:%S %Z')

def formatted_current_date():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime("%Y-%m-%d")

class Object(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    pass

class FakeUser(object):
    pass

class FakeRole(object):
    pass

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'].get(provider_name, dict())
        self.consumer_id = credentials.get('id', None)
        self.consumer_secret = credentials.get('secret', None)

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
        #logmessage("GoogleSignIn, args: " + str([str(arg) + ": " + str(request.args[arg]) for arg in request.args]))
        #logmessage("GoogleSignIn, request: " + str(request.data))
        session['google_id'] = result.get('id', [None])[0]
        session['google_email'] = result.get('email', [None])[0]
        response = make_response(json.dumps('Successfully connected user.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # oauth_session = self.service.get_auth_session(
        #     data={'code': request.args['code'],
        #           'grant_type': 'authorization_code',
        #           'redirect_uri': self.get_callback_url()}
        # )
        return response
    
    def callback(self):
        #logmessage("GoogleCallback, args: " + str([str(arg) + ": " + str(request.args[arg]) for arg in request.args]))
        #logmessage("GoogleCallback, request: " + str(request.data))
        email = session.get('google_email', None)
        google_id = session.get('google_id', None)
        if 'google_id' in session:
            del session['google_id']
        if 'google_email' in session:
            del session['google_email']
        if email is not None and google_id is not None:
            return (
                'google$' + str(google_id),
                email.split('@')[0],
                email
            )
        else:
            raise Exception("Could not get Google authorization information")

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/v2.9/oauth/authorize',           
            access_token_url='https://graph.facebook.com/v2.9/oauth/access_token',
            base_url='https://graph.facebook.com/v2.9/'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='public_profile,email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            decoder=json.loads,
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me', params={'fields': 'id,name,email'}).json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],
            me.get('email')
        )

class AzureSignIn(OAuthSignIn):
    def __init__(self):
        super(AzureSignIn, self).__init__('azure')
        self.service = OAuth2Service(
            name='azure',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://login.microsoftonline.com/common/oauth2/authorize',
            access_token_url='https://login.microsoftonline.com/common/oauth2/token',
            base_url='https://graph.microsoft.com/v1.0/'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            client_id=self.consumer_id,
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            decoder=json.loads,
            data={'code': request.args['code'],
                  'client_id': self.consumer_id,
                  'client_secret': self.consumer_secret,
                  'resource': 'https://graph.microsoft.com/',
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        return (
            'azure$' + me['id'],
            me.get('mail').split('@')[0],
            me.get('mail')
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

@flaskbabel.localeselector
def get_locale():
    translations = [str(translation) for translation in flaskbabel.list_translations()]
    return request.accept_languages.best_match(translations)

@lm.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

@app.route('/headers', methods=['POST', 'GET'])
@csrf.exempt
def show_headers():
    return jsonify(headers=dict(request.headers), ipaddress=request.remote_addr)

@app.route('/authorize/<provider>', methods=['POST', 'GET'])
@csrf.exempt
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
@csrf.exempt
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    # for argument in request.args:
    #     logmessage("argument " + str(argument) + " is " + str(request.args[argument]))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash(word('Authentication failed.'), 'error')
        return redirect(url_for('interview_list'))
    user = UserModel.query.filter_by(social_id=social_id).first()
    if not user:
        user = UserModel.query.filter_by(email=email).first()
    if user and user.social_id is not None and user.social_id.startswith('local'):
        flash(word('There is already a username and password on this system with the e-mail address') + " " + str(email) + ".  " + word("Please log in."), 'error')
        return redirect(url_for('user.login'))
    if not user:
        user = UserModel(social_id=social_id, nickname=username, email=email, active=True)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=False)
    if 'i' in session and 'uid' in session:
        save_user_dict_key(session['uid'], session['i'], priors=True)
        session['key_logged'] = True
    #logmessage("oauth_callback: calling substitute_secret")
    secret = substitute_secret(str(request.cookies.get('secret', None)), pad_to_16(MD5Hash(data=social_id).hexdigest()))
    response = redirect(url_for('interview_list'))
    response.set_cookie('secret', secret)
    return response

@app.route('/phone_login', methods=['POST', 'GET'])
def phone_login():
    if not app.config['USE_PHONE_LOGIN']:
        abort(404)
    form = PhoneLoginForm(request.form)
    #next = request.args.get('next', url_for('interview_list'))
    if request.method == 'POST' and form.submit.data:
        ok = True
        if form.validate():
            phone_number = form.phone_number.data
            if docassemble.base.functions.phone_number_is_valid(phone_number):
                phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
            else:
                ok = False
        else:
            ok = False
        if ok:
            verification_code = random_digits(daconfig['verification code digits'])
            message = word("Your verification code is") + " " + str(verification_code) + "."
            user_agent = request.headers.get('User-Agent', '')
            if detect_mobile.search(user_agent):
                message += '  ' + word("You can also follow this link: ") + url_for('phone_login_verify', _external=True, p=phone_number, c=verification_code)
            tracker_prefix = 'da:phonelogin:ip:' + str(request.remote_addr) + ':phone:'
            tracker_key = tracker_prefix + str(phone_number)
            pipe = r.pipeline()
            pipe.incr(tracker_key)
            pipe.expire(tracker_key, daconfig['ban period'])
            pipe.execute()
            total_attempts = 0
            for key in r.keys(tracker_prefix + '*'):
                val = r.get(key)
                total_attempts += int(val)
            if total_attempts > daconfig['attempt limit']:
                logmessage("IP address " + str(request.remote_addr) + " attempted to log in too many times.")
                flash(word("You have made too many login attempts."), 'error')
                return redirect(url_for('user.login'))
            total_attempts = 0
            for key in r.keys('da:phonelogin:ip:*:phone:' + phone_number):
                val = r.get(key)
                total_attempts += int(val)
            if total_attempts > daconfig['attempt limit']:
                logmessage("Too many attempts were made to log in to phone number " + str(phone_number))
                flash(word("You have made too many login attempts."), 'error')
                return redirect(url_for('user.login'))
            key = 'da:phonelogin:' + str(phone_number) + ':code'
            pipe = r.pipeline()
            pipe.set(key, verification_code)
            pipe.expire(key, daconfig['verification code timeout'])
            pipe.execute()
            #logmessage("Writing code " + str(verification_code) + " to " + key)
            docassemble.base.functions.this_thread.current_info = current_info(req=request)
            success = docassemble.base.util.send_sms(to=phone_number, body=message)
            if success:
                session['phone_number'] = phone_number
                return redirect(url_for('phone_login_verify'))
            else:
                flash(word("There was a problem sending you a text message.  Please log in another way."), 'error')
                return redirect(url_for('user.login'))
        else:
            flash(word("Please enter a valid phone number"), 'error')
    return render_template('flask_user/phone_login.html', form=form, version_warning=None, title=word("Sign in with your mobile phone"), tab_title=word("Sign In"), page_title=word("Sign in"))

@app.route('/pv', methods=['POST', 'GET'])
def phone_login_verify():
    if not app.config['USE_PHONE_LOGIN']:
        abort(404)
    phone_number = session.get('phone_number', request.args.get('p', None))
    if phone_number is None:
        abort(404)
    form = PhoneLoginVerifyForm(request.form)
    form.phone_number.data = phone_number
    if 'c' in request.args and 'p' in request.args:
        submitted = True
        form.verification_code.data = request.args.get('c', None)
    else:
        submitted = False
    if submitted or (request.method == 'POST' and form.submit.data):
        if form.validate():
            social_id = 'phone$' + str(phone_number)
            user = UserModel.query.filter_by(social_id=social_id).first()
            if user and user.active is False:
                flash(word("Your account has been disabled."), 'error')
                return redirect(url_for('user.login'))
            if not user:
                user = UserModel(social_id=social_id, nickname=phone_number, active=True)
                db.session.add(user)
                db.session.commit()
            login_user(user, remember=False)
            r.delete('da:phonelogin:ip:' + str(request.remote_addr) + ':phone:' + phone_number)
            if 'i' in session and 'uid' in session:
                save_user_dict_key(session['uid'], session['i'], priors=True)
                session['key_logged'] = True
            secret = substitute_secret(str(request.cookies.get('secret', None)), pad_to_16(MD5Hash(data=social_id).hexdigest()))
            response = redirect(url_for('interview_list'))
            response.set_cookie('secret', secret)
            return response
        else:
            logmessage("IP address " + str(request.remote_addr) + " made a failed login attempt using phone number " + str(phone_number) + ".")
            flash(word("Your verification code is invalid or expired.  Please try again."), 'error')
            return redirect(url_for('user.login'))
    return render_template('flask_user/phone_login_verify.html', form=form, version_warning=None, title=word("Verify your phone"), tab_title=word("Enter code"), page_title=word("Enter code"), description=word("We just sent you a text message with a verification code.  Enter the verification code to proceed."))

@login_required
@app.route('/mfa_setup', methods=['POST', 'GET'])
def mfa_setup():
    if daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    form = MFASetupForm(request.form)
    if request.method == 'POST' and form.submit.data:
        if 'otp_secret' not in session:
            abort(404)
        otp_secret = session['otp_secret']
        del session['otp_secret']
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        totp = pyotp.TOTP(otp_secret)
        if not totp.verify(supplied_verification_code):
            flash(word("Your verification code was invalid."), 'error')
            return redirect(url_for('user_profile_page'))
        user = load_user(current_user.id)
        user.otp_secret = otp_secret
        db.session.commit()
        flash(word("You are now set up with two factor authentication."), 'success')
        return redirect(url_for('user_profile_page'))
    otp_secret = pyotp.random_base32()
    if current_user.email:
        the_name = current_user.email
    else:
        the_name = re.sub(r'.*\$', '', current_user.social_id)
    the_url = pyotp.totp.TOTP(otp_secret).provisioning_uri(the_name, issuer_name=app.config['APP_NAME'])
    im = qrcode.make(the_url, image_factory=qrcode.image.svg.SvgPathImage)
    output = StringIO.StringIO()
    im.save(output)
    the_qrcode = output.getvalue()
    the_qrcode = re.sub("<\?xml version='1.0' encoding='UTF-8'\?>\n", '', the_qrcode)
    the_qrcode = re.sub(r'height="[0-9]+mm" ', '', the_qrcode)
    the_qrcode = re.sub(r'width="[0-9]+mm" ', '', the_qrcode)
    m = re.search(r'(viewBox="[^"]+")', the_qrcode)
    if m:
        viewbox = ' ' + m.group(1)
    else:
        viewbox = ''
    the_qrcode = '<svg class="mfasvg"' + viewbox + '><g transform="scale(1.0)">' + the_qrcode + '</g></svg>'
    session['otp_secret'] = otp_secret
    return render_template('flask_user/mfa_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("Scan the barcode with your phone's authenticator app and enter the verification code."), the_qrcode=Markup(the_qrcode))

@login_required
@app.route('/mfa_reconfigure', methods=['POST', 'GET'])
def mfa_reconfigure():
    if daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    user = load_user(current_user.id)
    if user.otp_secret is None:
        if twilio_config is None:
            return redirect(url_for('mfa_setup'))
        return redirect(url_for('mfa_choose'))
    form = MFAReconfigureForm(request.form)
    if request.method == 'POST':
        if form.reconfigure.data:
            if twilio_config is None:
                return redirect(url_for('mfa_setup'))
            return redirect(url_for('mfa_choose'))
        elif form.disable.data:
            user.otp_secret = None
            db.session.commit()
            flash(word("Your account no longer uses two-factor authentication."), 'success')
            return redirect(url_for('user_profile_page'))
        elif form.cancel.data:
            return redirect(url_for('user_profile_page'))
    return render_template('flask_user/mfa_reconfigure.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("Your account already has two-factor authentication enabled.  Would you like to reconfigure or disable two-factor authentication?"))

@login_required
@app.route('/mfa_choose', methods=['POST', 'GET'])
def mfa_choose():
    if daconfig.get('two factor authentication', False) is not True or current_user.is_anonymous or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    if twilio_config is None:
        return redirect(url_for('mfa_setup'))
    user = load_user(current_user.id)
    form = MFAChooseForm(request.form)
    if request.method == 'POST':
        if form.sms.data:
            return redirect(url_for('mfa_sms_setup'))
        elif form.auth.data:
            return redirect(url_for('mfa_setup'))
        else:
            return redirect(url_for('user_profile_page'))
    return render_template('flask_user/mfa_choose.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=Markup(word("""Which type of two-factor authentication would you like to use?  The first option is to use an authentication app like <a target="_blank" href="https://en.wikipedia.org/wiki/Google_Authenticator">Google Authenticator</a> or <a target="_blank" href="https://authy.com/">Authy</a>.  The second option is to receive a text (SMS) message containing a verification code.""")))

@login_required
@app.route('/mfa_sms_setup', methods=['POST', 'GET'])
def mfa_sms_setup():
    if twilio_config is None or daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    form = MFASMSSetupForm(request.form)
    user = load_user(current_user.id)
    if request.method == 'GET' and user.otp_secret is not None and user.otp_secret.startswith(':phone:'):
        form.phone_number.data = re.sub(r'^:phone:', '', user.otp_secret)
    if request.method == 'POST' and form.submit.data:
        phone_number = form.phone_number.data
        if docassemble.base.functions.phone_number_is_valid(phone_number):
            phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
            verification_code = random_digits(daconfig['verification code digits'])
            message = word("Your verification code is") + " " + str(verification_code) + "."
            success = docassemble.base.util.send_sms(to=phone_number, body=message)
            if success:
                session['phone_number'] = phone_number
                key = 'da:mfa:phone:' + str(phone_number) + ':code'
                pipe = r.pipeline()
                pipe.set(key, verification_code)
                pipe.expire(key, daconfig['verification code timeout'])
                pipe.execute()
                return redirect(url_for('mfa_verify_sms_setup'))
            else:
                flash(word("There was a problem sending the text message."), 'error')
                return redirect(url_for('user_profile_page'))
        else:
            flash(word("Invalid phone number."), 'error')            
    return render_template('flask_user/mfa_sms_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("""Enter your phone number.  A confirmation code will be sent to you."""))

@login_required
@app.route('/mfa_verify_sms_setup', methods=['POST', 'GET'])
def mfa_verify_sms_setup():
    if 'phone_number' not in session or twilio_config is None or daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    form = MFAVerifySMSSetupForm(request.form)
    if request.method == 'POST' and form.submit.data:
        phone_number = session['phone_number']
        del session['phone_number']
        key = 'da:mfa:phone:' + str(phone_number) + ':code'
        verification_code = r.get(key)
        r.delete(key)
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        if verification_code is None:
            flash(word('Your verification code was missing or expired'), 'error')
            return redirect(url_for('user_profile_page'))
        if verification_code == supplied_verification_code:
            user = load_user(current_user.id)
            user.otp_secret = ':phone:' + phone_number
            db.session.commit()
            flash(word("You are now set up with two factor authentication."), 'success')
            return redirect(url_for('user_profile_page'))
    return render_template('flask_user/mfa_verify_sms_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word('We just sent you a text message with a verification code.  Enter the verification code to proceed.'))

@app.route('/mfa_login', methods=['POST', 'GET'])
def mfa_login():
    if daconfig.get('two factor authentication', False) is not True:
        logmessage("mfa_login: two factor authentication not configured")
        abort(404)
    if 'validated_user' not in session:
        logmessage("mfa_login: validated_user not in session")
        abort(404)
    user = load_user(session['validated_user'])
    if user is None or user.otp_secret is None or not user.social_id.startswith('local'):
        logmessage("mfa_login: user not setup for MFA where validated_user was " + str(session['validated_user']))
        abort(404)
    form = MFALoginForm(request.form)
    if not form.next.data:
        form.next.data = _get_safe_next_param('next', url_for('interview_list'))
    if request.method == 'POST' and form.submit.data:
        del session['validated_user']
        fail_key = 'da:failedlogin:ip:' + str(request.remote_addr)
        failed_attempts = r.get(fail_key)
        if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
            abort(404)
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        if user.otp_secret.startswith(':phone:'):
            phone_number = re.sub(r'^:phone:', '', user.otp_secret)
            key = 'da:mfa:phone:' + str(phone_number) + ':code'
            verification_code = r.get(key)
            r.delete(key)
            if verification_code is None or supplied_verification_code != verification_code:
                r.incr(fail_key)
                r.expire(fail_key, 86400)
                flash(word("Your verification code was invalid or expired."), 'error')
                return redirect(url_for('user.login'))
            elif failed_attempts is not None:
                r.delete(fail_key)
        else:
            totp = pyotp.TOTP(user.otp_secret)
            if not totp.verify(supplied_verification_code):
                r.incr(fail_key)
                r.expire(fail_key, 86400)
                flash(word("Your verification code was invalid."), 'error')
                return redirect(url_for('user.login'))
            elif failed_attempts is not None:
                r.delete(fail_key)
        safe_next = user_manager.make_safe_url_function(form.next.data)
        return flask_user.views._do_login_user(user, safe_next, False)
    description = word("This account uses two-factor authentication.")
    if user.otp_secret.startswith(':phone:'):
        description += "  " + word("Please enter the verification code from the text message we just sent you.")
    else:
        description += "  " + word("Please enter the verification code from your authentication app.")
    return render_template('flask_user/mfa_login.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=description)

def get_github_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('github', dict())
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('GitHub integration is not configured')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='repo admin:public_key',
        redirect_uri=url_for('github_oauth_callback', _external=True),
        auth_uri='http://github.com/login/oauth/authorize',
        token_uri='https://github.com/login/oauth/access_token',
        access_type='offline',
        prompt='consent')
    return flow

def delete_ssh_keys():
    area = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    area.delete_file('.ssh-private')
    area.delete_file('.ssh-public')
    area.delete_file('.ssh_command.sh')
    area.finalize()

def get_ssh_keys(email):
    area = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    private_key_file = os.path.join(area.directory, '.ssh-private')
    public_key_file = os.path.join(area.directory, '.ssh-public')
    if not (os.path.isfile(private_key_file) and os.path.isfile(private_key_file)):
        from Crypto.PublicKey import RSA
        key = RSA.generate(4096)
        pubkey = key.publickey()
        area.write_content(key.exportKey('PEM'), filename=private_key_file, save=False)
        area.write_content(pubkey.exportKey('OpenSSH') + " " + str(email) + "\n", filename=public_key_file, save=False)
        area.finalize()
    return (private_key_file, public_key_file)

def get_next_link(resp):
    if 'link' in resp and resp['link']:
        link_info = links_from_header.extract(resp['link'])
        if 'next' in link_info:
            return link_info['next']
    return None

@app.route('/github_menu', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_menu():
    if not app.config['USE_GITHUB']:
        abort(404)
    form = GitHubForm(request.form)
    if request.method == 'POST':
        if form.configure.data:
            return redirect(url_for('github_configure'))
        elif form.unconfigure.data:
            return redirect(url_for('github_unconfigure'))
        elif form.cancel.data:
            return redirect(url_for('user_profile_page'))
    uses_github = r.get('da:using_github:userid:' + str(current_user.id))
    if uses_github:
        description = "Your GitHub integration is currently turned on.  You can disconnect GitHub integration if you no longer wish to use it."
    else:
        description = "If you have a GitHub account, you can turn on GitHub integration.  This will allow you to use GitHub as a version control system for packages from inside the Playground."
    return render_template('pages/github.html', form=form, version_warning=None, title=word("GitHub Integration"), tab_title=word("GitHub"), page_title=word("GitHub"), description=description, uses_github=uses_github, bodyclass='adminbody')

@app.route('/github_configure', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_configure():
    if not app.config['USE_GITHUB']:
        abort(404)
    storage = RedisCredStorage(app='github')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        session['github_state'] = random_string(16)
        session['github_next'] = 'configure'
        flow = get_github_flow()
        uri = flow.step1_get_authorize_url(state=session['github_state'])
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    found = False
    resp, content = http.request("https://api.github.com/user", "GET")
    if int(resp['status']) == 200:
        user_info = json.loads(content)
        if 'email' not in user_info:
            raise DAError("github_configure: could not get e-mail address of user")
    else:
        raise DAError("github_configure: could not get information about user")
    resp, content = http.request("https://api.github.com/user/keys", "GET")
    if int(resp['status']) == 200:
        for key in json.loads(content):
            if key['title'] == app.config['APP_NAME']:
                found = True
    else:
        raise DAError("github_configure: could not get information about ssh keys")
    while found is False:
        next_link = get_next_link(resp)
        if next_link:
            resp, content = http.request(next_link, "GET")
            if int(resp['status']) == 200:
                for key in json.loads(content):
                    if key['title'] == app.config['APP_NAME']:
                        found = True
            else:
                raise DAError("github_configure: could not get additional information about ssh keys")
        else:
            break
    if found:
        flash(word("Your GitHub integration has already been configured."), 'info')
    if not found:
        (private_key_file, public_key_file) = get_ssh_keys(user_info['email'])
        with open(public_key_file, 'rb') as fp:
            public_key = fp.read()
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(dict(title=app.config['APP_NAME'], key=public_key))
        resp, content = http.request("https://api.github.com/user/keys", "POST", headers=headers, body=body)
        if int(resp['status']) == 201:
            flash(word("GitHub integration was successfully configured."), 'info')
        else:
            raise DAError("github_configure: error setting public key")
    r.set('da:using_github:userid:' + str(current_user.id), 1)
    return redirect(url_for('user_profile_page'))

@app.route('/github_unconfigure', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_unconfigure():
    if not app.config['USE_GITHUB']:
        abort(404)
    storage = RedisCredStorage(app='github')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        session['github_state'] = random_string(16)
        session['github_next'] = 'unconfigure'
        flow = get_github_flow()
        uri = flow.step1_get_authorize_url(state=session['github_state'])
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    found = False
    resp, content = http.request("https://api.github.com/user/keys", "GET")
    if int(resp['status']) == 200:
        for key in json.loads(content):
            if key['title'] == app.config['APP_NAME']:
                found = True
                id_to_remove = key['id']
    else:
        raise DAError("github_configure: could not get information about ssh keys")
    while found is False:
        next_link = get_next_link(resp)
        if next_link:
            resp, content = http.request(next_link, "GET")
            if int(resp['status']) == 200:
                for key in json.loads(content):
                    if key['title'] == app.config['APP_NAME']:
                        found = True
                        id_to_remove = key['id']
            else:
                raise DAError("github_configure: could not get additional information about ssh keys")
        else:
            break
    if found:
        resp, content = http.request("https://api.github.com/user/keys/" + str(id_to_remove), "DELETE")
        if int(resp['status']) != 204:
            raise DAError("github_configure: error deleting public key " + str(id_to_remove) + ": " + str(resp['status']) + " content: " + str(content))
    delete_ssh_keys()
    r.delete('da:github:userid:' + str(current_user.id))
    r.delete('da:using_github:userid:' + str(current_user.id))
    flash(word("GitHub integration was successfully disconnected."), 'info')
    return redirect(url_for('user_profile_page'))

@app.route('/github_oauth_callback', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_oauth_callback():
    failed = False
    if not app.config['USE_GITHUB']:
        logmessage('start_github_oauth: server does not use github')
        failed = True
    elif 'github_state' not in session or 'github_next' not in session:
        logmessage('start_github_oauth: github_state or github_next not in session')
        failed = True
    elif 'code' not in request.args or 'state' not in request.args:
        logmessage('start_github_oauth: code and state not in args')
        failed = True
    elif request.args['state'] != session['github_state']:
        logmessage('start_github_oauth: state did not match')
        failed = True
    if failed:
        r.delete('da:github:userid:' + str(current_user.id))
        r.delete('da:using_github:userid:' + str(current_user.id))
        abort(404)
    flow = get_github_flow()
    credentials = flow.step2_exchange(request.args['code'])
    storage = RedisCredStorage(app='github')
    storage.put(credentials)
    next_page = session['github_next']
    del session['github_state']
    del session['github_next']
    if next_page == 'configure':
        return redirect(url_for('github_configure'))
    elif next_page == 'unconfigure':
        return redirect(url_for('github_unconfigure'))
    elif next_page.startswith('package:'):
        return redirect(url_for('create_playground_package', package=re.sub(r'^package:', '', next_page), github='1', commit_message=re.sub(r'^package:[^:]*:', '', next_page)))
    elif next_page.startswith('playgroundpackages:'):
        return redirect(url_for('playground_packages', file=re.sub(r'^playgroundpackages:', '', next_page)))
    logmessage('start_github_oauth: unknown next page ' + str(next_page))
    r.delete('da:github:userid:' + str(current_user.id))
    r.delete('da:using_github:userid:' + str(current_user.id))
    abort(404)

    # resp, content = http.request("https://api.github.com/user", "GET")
    # if int(resp['status']) >= 200 and int(resp['status']) < 300:
    #     user_info = json.loads(content)
    # else:
    #     raise DAError("Could not get information about the GitHub user")
    # github_user_name = user_info.get('login', None)
    # if github_user_name is None:
    #     raise DAError("Could not get the GitHub user name")
    # logmessage("GitHub user name is " + str(github_user_name))
    #headers = {'Content-Type': 'application/json'}
    #body = json.dumps(dict())
    # resp, content = http.request("https://api.github.com/user/repos", "GET")
    # if int(resp['status']) >= 200 and int(resp['status']) < 300:
    #     repositories = json.loads(content)
    #     for repository in repositories:
            #name
            #full_name
            #html_url
            #ssh_url
            
#    else:
#        raise DAError("Could not get information about the GitHub user's repositories: " + str(resp['status']) + " content: " + str(content))

@app.route('/user/google-sign-in')
def google_page():
    return render_template('flask_user/google_login.html', version_warning=None, title=word("Sign In"), tab_title=word("Sign In"), page_title=word("Sign in"))

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
        manual_checkout()
        obtain_lock(session_id, yaml_filename)
        reset_user_dict(session_id, yaml_filename)
        release_lock(session_id, yaml_filename)
    return redirect(exit_page)

@app.route("/cleanup_sessions", methods=['GET'])
def cleanup_sessions():
    kv_session.cleanup_sessions()
    return render_template('base_templates/blank.html')

@app.route("/health_check", methods=['GET'])
def health_check():
    return render_template('pages/health_check.html', version_warning=None, content="OK")

@app.route("/checkout", methods=['POST', 'GET'])
def checkout():
    try:
        manual_checkout()
    except:
        return jsonify(success=False)
    return jsonify(success=True)

@app.route("/restart_ajax", methods=['POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_ajax():
    #logmessage("restart_ajax: action is " + str(request.form.get('action', None)))
    #if current_user.has_role('admin', 'developer'):
    #    logmessage("restart_ajax: user has permission")
    #else:
    #    logmessage("restart_ajax: user has no permission")
    if request.form.get('action', None) == 'restart' and current_user.has_role('admin', 'developer'):
        logmessage("restart_ajax: restarting")
        restart_all()
        return jsonify(success=True)

class ChatPartners(object):
    pass
    
@app.route("/checkin", methods=['POST', 'GET'])
def checkin():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if 'visitor_secret' in request.cookies:
        secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    #session_cookie_id = request.cookies.get('session', None)
    if session_id is None or yaml_filename is None:
        return jsonify(success=False)
    if current_user.is_anonymous:
        the_user_id = 't' + str(session['tempuser'])
        auth_user_id = None
        temp_user_id = int(session['tempuser'])
    else:
        auth_user_id = current_user.id
        the_user_id = current_user.id
        temp_user_id = None
    if request.form.get('action', None) == 'chat_log':
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        if user_dict['_internal']['livehelp']['availability'] != 'available':
            return jsonify(success=False)
        messages = get_chat_log(user_dict['_internal']['livehelp']['mode'], yaml_filename, session_id, auth_user_id, temp_user_id, secret, auth_user_id, temp_user_id)
        return jsonify(success=True, messages=messages)
    if request.form.get('action', None) == 'checkin':
        commands = list()
        checkin_code = request.form.get('checkinCode', None)
        do_action = request.form.get('do_action', None)
        #logmessage("in checkin")
        if do_action is not None:
            parameters = dict()
            form_parameters = request.form.get('parameters', None)
            if form_parameters is not None:
                form_parameters = json.loads(form_parameters)
                for param in form_parameters:
                    if param['name'] in ['_checkboxes', '_empties', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location', '_varnames', 'ajax', 'informed', 'csrf_token']:
                        continue
                    try:
                        parameters[from_safeid(param['name'])] = param['value']
                    except:
                        logmessage("checkin: failed to unpack " + str(param['name']))
            #logmessage("Action was " + str(do_action) + " and parameters were " + str(parameters))
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
            interview = docassemble.base.interview_cache.get_interview(yaml_filename)
            interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=dict(action=do_action, arguments=parameters)))
            interview.assemble(user_dict, interview_status)
            if interview_status.question.question_type == "backgroundresponse":
                the_response = interview_status.question.backgroundresponse
                commands.append(dict(action=do_action, value=docassemble.base.functions.safe_json(the_response), extra='backgroundresponse'))
            elif interview_status.question.question_type == "template" and interview_status.question.target is not None:
                commands.append(dict(action=do_action, value=dict(target=interview_status.question.target, content=docassemble.base.util.markdown_to_html(interview_status.questionText, trim=True)), extra='backgroundresponse'))
            save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted)
        peer_ok = False
        help_ok = False
        num_peers = 0
        help_available = 0
        old_chatstatus = session.get('chatstatus', None)
        chatstatus = request.form.get('chatstatus', 'off')
        if old_chatstatus != chatstatus:
            session['chatstatus'] = chatstatus
        obj = dict(chatstatus=chatstatus, i=yaml_filename, uid=session_id, userid=the_user_id)
        key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        call_forwarding_on = False
        forwarding_phone_number = None
        if twilio_config is not None:
            forwarding_phone_number = twilio_config['name']['default'].get('number', None)
            if forwarding_phone_number is not None:
                call_forwarding_on = True
        call_forwarding_code = None
        call_forwarding_message = None
        if call_forwarding_on:
            for call_key in r.keys(re.sub(r'^da:session:uid:', 'da:phonecode:monitor:*:uid:', key)):
                call_forwarding_code = r.get(call_key)
                if call_forwarding_code is not None:
                    other_value = r.get('da:callforward:' + str(call_forwarding_code))
                    if other_value is None:
                        r.delete(call_key)
                        continue
                    remaining_seconds = r.ttl(call_key)
                    if remaining_seconds > 30:
                        call_forwarding_message = '<span class="phone-message"><i class="glyphicon glyphicon-earphone"></i> ' + word('To reach an advocate who can assist you, call') + ' <a class="phone-number" href="tel:' + str(forwarding_phone_number) + '">' + str(forwarding_phone_number) + '</a> ' + word("and enter the code") + ' <span class="phone-code">' + str(call_forwarding_code) + '</span>.</span>'
                        break
        chat_session_key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        potential_partners = list()
        if str(chatstatus) != 'off': #in ['waiting', 'standby', 'ringing', 'ready', 'on', 'hangup', 'observeonly']:
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
            obj['chatstatus'] = chatstatus
            obj['secret'] = secret
            obj['encrypted'] = is_encrypted
            obj['mode'] = user_dict['_internal']['livehelp']['mode']
            if obj['mode'] in ['peer', 'peerhelp']:
                peer_ok = True
            if obj['mode'] in ['help', 'peerhelp']:
                help_ok = True
            obj['partner_roles'] = user_dict['_internal']['livehelp']['partner_roles']
            if current_user.is_authenticated:
                for attribute in ['email', 'confirmed_at', 'first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone']:
                    obj[attribute] = getattr(current_user, attribute, None)
            else:
                obj['temp_user_id'] = temp_user_id
            if help_ok and len(obj['partner_roles']) and not r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
                pipe = r.pipeline()
                for role in obj['partner_roles']:
                    role_key = 'da:chat:roletype:' + str(role)
                    pipe.set(role_key, 1)
                    pipe.expire(role_key, 2592000)
                pipe.execute()
                for role in obj['partner_roles']:
                    for the_key in r.keys('da:monitor:role:' + role + ':userid:*'):
                        user_id = re.sub(r'^.*:userid:', '', the_key)
                        if user_id not in potential_partners:
                            potential_partners.append(user_id)
                for the_key in r.keys('da:monitor:chatpartners:*'):
                    user_id = re.sub(r'^.*chatpartners:', '', the_key)
                    if user_id not in potential_partners:
                        for chat_key in r.hgetall(the_key):
                            if chat_key == chat_session_key:
                                potential_partners.append(user_id)
            if len(potential_partners) > 0:
                if chatstatus == 'ringing':
                    lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
                    #logmessage("Writing to " + str(lkey))
                    pipe = r.pipeline()
                    failure = True
                    for user_id in potential_partners:
                        for the_key in r.keys('da:monitor:available:' + str(user_id)):
                            pipe.rpush(lkey, the_key)
                            failure = False
                    if peer_ok:
                        for the_key in r.keys('da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                            if the_key != chat_session_key:
                                pipe.rpush(lkey, the_key)
                                failure = False
                    if failure:
                        if peer_ok:
                            chatstatus = 'ready'
                        else:
                            chatstatus = 'waiting'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                    else:
                        pipe.expire(lkey, 60)
                        pipe.execute()
                        chatstatus = 'ready'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                elif chatstatus in ['on']:
                    if len(potential_partners) > 0:
                        already_connected_to_help = False
                        current_helper = None
                        for user_id in potential_partners:
                            for the_key in r.hgetall('da:monitor:chatpartners:' + str(user_id)):
                                if the_key == chat_session_key:
                                    already_connected_to_help = True
                                    current_helper = user_id
                        if not already_connected_to_help:
                            for user_id in potential_partners:
                                mon_sid = r.get('da:monitor:available:' + str(user_id))
                                if mon_sid is None:
                                    continue
                                int_sid = r.get('da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id))
                                if int_sid is None:
                                    continue
                                r.publish(mon_sid, json.dumps(dict(messagetype='chatready', uid=session_id, i=yaml_filename, userid=the_user_id, secret=secret, sid=int_sid)))
                                r.publish(int_sid, json.dumps(dict(messagetype='chatpartner', sid=mon_sid)))
                                break
                if chatstatus in ['waiting', 'hangup']:
                    chatstatus = 'standby'
                    session['chatstatus'] = chatstatus
                    obj['chatstatus'] = chatstatus
            else:
                if peer_ok:
                    if chatstatus == 'ringing':
                        lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
                        pipe = r.pipeline()
                        failure = True
                        for the_key in r.keys('da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                            if the_key != chat_session_key:
                                pipe.rpush(lkey, the_key)
                                failure = False
                        if not failure:
                            pipe.expire(lkey, 6000)
                            pipe.execute()
                        chatstatus = 'ready'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                    elif chatstatus in ['waiting', 'hangup']:
                        chatstatus = 'standby'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                else:
                    if chatstatus in ['standby', 'ready', 'ringing', 'hangup']:
                        chatstatus = 'waiting'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
            if peer_ok:
                for sess_key in r.keys('da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                    if sess_key != key:
                        num_peers += 1
        help_available = len(potential_partners)
        html_key = 'da:html:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        if old_chatstatus != chatstatus:
            html = r.get(html_key)
            if html is not None:
                html_obj = json.loads(html)
                if 'browser_title' in html_obj:
                    obj['browser_title'] = html_obj['browser_title']
                if r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
                    obj['blocked'] = True
                else:
                    obj['blocked'] = False
                r.publish('da:monitor', json.dumps(dict(messagetype='sessionupdate', key=key, session=obj)))
            else:
                logmessage("checkin: the html was not found at " + str(html_key))
        pipe = r.pipeline()
        pipe.set(key, pickle.dumps(obj))
        pipe.expire(key, 60)
        pipe.expire(html_key, 60)
        pipe.execute()
        ocontrol_key = 'da:control:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        ocontrol = r.get(ocontrol_key)
        if ocontrol is None:
            observer_control = False
        else:
            observer_control = True
        parameters = request.form.get('parameters', None)
        if parameters is not None:
            key = 'da:input:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
            r.publish(key, parameters)
        worker_key = 'da:worker:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        worker_len = r.llen(worker_key)
        if worker_len > 0:
            workers_inspected = 0
            while workers_inspected <= worker_len:
                worker_id = r.lpop(worker_key)
                if worker_id is not None:
                    try:
                        result = docassemble.webapp.worker.workerapp.AsyncResult(id=worker_id)
                        if result.ready():
                            if type(result.result) == ReturnValue:
                                commands.append(dict(value=result.result.value, extra=result.result.extra))
                        else:
                            r.rpush(worker_key, worker_id)
                    except Exception as errstr:
                        logmessage("checkin: got error " + str(errstr))
                        r.rpush(worker_key, worker_id)
                workers_inspected += 1
        if peer_ok or help_ok:
            return jsonify(success=True, chat_status=chatstatus, num_peers=num_peers, help_available=help_available, phone=call_forwarding_message, observerControl=observer_control, commands=commands, checkin_code=checkin_code)
        else:
            return jsonify(success=True, chat_status=chatstatus, phone=call_forwarding_message, observerControl=observer_control, commands=commands, checkin_code=checkin_code)
    return jsonify(success=False)

@app.before_request
def setup_celery():
    docassemble.webapp.worker.workerapp.set_current()

# @app.before_request
# def before_request():
#     g.request_start_time = time.time()
#     g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

@app.route("/vars", methods=['POST', 'GET'])
def get_variables():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if 'visitor_secret' in request.cookies:
        secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    #session_cookie_id = request.cookies.get('session', None)
    if session_id is None or yaml_filename is None:
        return jsonify(success=False)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        return jsonify(success=False)
    return jsonify(success=True, variables=docassemble.base.functions.serializable_dict(user_dict), steps=steps, encrypted=is_encrypted, uid=session_id, i=yaml_filename)

@app.route("/", methods=['POST', 'GET'])
def index():
    if 'ajax' in request.form:
        is_ajax = True
    else:
        is_ajax = False
        # if 'newsecret' in session:
        #     logmessage("interview_list: fixing cookie")
        #     response = redirect(url_for('index'))
        #     response.set_cookie('secret', session['newsecret'])
        #     del session['newsecret']
        #     return response
    chatstatus = session.get('chatstatus', 'off')
    session_id = session.get('uid', None)
    #logmessage("index: session uid is " + str(session_id))
    if current_user.is_anonymous:
        #logmessage("index: is anonymous")
        if 'tempuser' not in session:
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            session['tempuser'] = new_temp_user.id
    else:
        #logmessage("index: is not anonymous")
        if 'user_id' not in session:
            session['user_id'] = current_user.id
    expire_visitor_secret = False
    if 'visitor_secret' in request.cookies:
        #logmessage("index: there is a visitor secret")
        if 'session' in request.args:
            secret = request.cookies.get('secret', None)
            expire_visitor_secret = True
        else:
            secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    use_cache = int(request.args.get('cache', 1))
    reset_interview = int(request.args.get('reset', 0))
    encrypted = session.get('encrypted', True)
    #logmessage("index: session says encrypted is " + str(encrypted))
    if secret is None:
        #logmessage("index: setting set_cookie to True")
        secret = random_string(16)
        set_cookie = True
    else:
        #logmessage("index: setting set_cookie to False")
        secret = str(secret)
        set_cookie = False
    yaml_filename = session.get('i', default_yaml_filename)
    #logmessage("index: yaml_filename from session/default is " + str(yaml_filename))
    steps = 0
    need_to_reset = False
    yaml_parameter = request.args.get('i', None)
    if yaml_filename is None and yaml_parameter is None:
        if len(daconfig['dispatch']):
            return redirect(url_for('interview_start'))
        else:
            yaml_filename = final_default_yaml_filename
    session_parameter = request.args.get('session', None)
    #logmessage("index: session_parameter is " + str(session_parameter))
    if yaml_parameter is not None:
        #logmessage("index: yaml_parameter is not None: " + str(yaml_parameter))
        yaml_filename = yaml_parameter
        old_yaml_filename = session.get('i', None)
        #logmessage("index: old_yaml_filename is " + str(old_yaml_filename))
        if old_yaml_filename != yaml_filename or reset_interview:
            #logmessage("index: change in yaml filename detected")
            show_flash = False
            session['i'] = yaml_filename
            if old_yaml_filename is not None and request.args.get('from_list', None) is None and not yaml_filename.startswith("docassemble.playground") and not yaml_filename.startswith("docassemble.base"):
                show_flash = True
            if session_parameter is None:
                #logmessage("index: change in yaml filename detected and session_parameter is None")
                if show_flash:
                    if current_user.is_authenticated:
                        message = "Starting a new interview.  To go back to your previous interview, go to My Interviews on the menu."
                    else:
                        message = "Starting a new interview.  To go back to your previous interview, log in to see a list of your interviews."
                #logmessage("index: calling reset_session with retain_code")
                user_code, user_dict = reset_session(yaml_filename, secret, retain_code=True)
                reset_user_dict(user_code, yaml_filename)
                save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
                release_lock(user_code, yaml_filename)
                session_id = session.get('uid', None)
                if 'key_logged' in session:
                    del session['key_logged']
                need_to_reset = True
            else:
                #logmessage("index: both i and session provided")
                if show_flash:
                    if current_user.is_authenticated:
                        message = "Entering a different interview.  To go back to your previous interview, go to My Interviews on the menu."
                    else:
                        message = "Entering a different interview.  To go back to your previous interview, log in to see a list of your interviews."
            if show_flash:
                flash(word(message), 'info')
    elif not is_ajax:
        #logmessage("index: need_to_reset is True")
        need_to_reset = True
    if session_parameter is not None:
        #logmessage("index: session parameter is not None: " + str(session_parameter))
        session_id = session_parameter
        session['uid'] = session_id
        if yaml_parameter is not None:
            #logmessage("index: yaml_parameter is not None: " + str(yaml_filename))
            session['i'] = yaml_filename
        if 'key_logged' in session:
            del session['key_logged']
        need_to_reset = True
    if session_id:
        #logmessage("index: session_id is defined")
        user_code = session_id
        obtain_lock(user_code, yaml_filename)
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(user_code, yaml_filename, secret=secret)
        except:
            #logmessage("index: there was an exception after fetch_user_dict")
            #sys.stderr.write(str(the_err) + "\n")
            release_lock(user_code, yaml_filename)
            logmessage("index: dictionary fetch failed, resetting without retain_code")
            user_code, user_dict = reset_session(yaml_filename, secret)
            encrypted = False
            session['encrypted'] = encrypted
            is_encrypted = encrypted
            if 'key_logged' in session:
                del session['key_logged']
            need_to_reset = True
        if encrypted != is_encrypted:
            #logmessage("index: change in encryption; encrypted is " + str(encrypted) + " but is_encrypted is " + str(is_encrypted))
            encrypted = is_encrypted
            session['encrypted'] = encrypted
        if user_dict is None:
            #logmessage("index: user_dict is None")
            try:
                release_lock(user_code, yaml_filename)
            except:
                pass
            del user_code
            del user_dict
    try:
        user_dict
        user_code
    except:
        #logmessage("index: 02 Calling without retain_code")
        user_code, user_dict = reset_session(yaml_filename, secret)
        encrypted = False
        session['encrypted'] = encrypted
        if 'key_logged' in session:
            del session['key_logged']
        steps = 0
    action = None
    if user_dict.get('multi_user', False) is True and encrypted is True:
        #logmessage("index: encryption mismatch, should be False")
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
    # else:
    #     logmessage("index: no encryption mismatch for should be False")        
    if user_dict.get('multi_user', False) is False and encrypted is False:
        #logmessage("index: encryption mismatch, should be True")
        encrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
        encrypted = True
        session['encrypted'] = encrypted
    # else:
    #     logmessage("index: no encryption mismatch for should be True")        
    if current_user.is_authenticated and 'key_logged' not in session:
        #logmessage("index: need to save user dict key")
        save_user_dict_key(user_code, yaml_filename)
        session['key_logged'] = True
    if 'action' in session:
        #logmessage("index: action in session")
        action = json.loads(myb64unquote(session['action']))
        del session['action']
    if len(request.args):
        #logmessage("index: there were args")
        if 'action' in request.args:
            session['action'] = request.args['action']
            response = do_redirect(url_for('index', i=yaml_filename), is_ajax)
            if set_cookie:
                response.set_cookie('secret', secret)
            if expire_visitor_secret:
                response.set_cookie('visitor_secret', '', expires=0)
            release_lock(user_code, yaml_filename)
            #logmessage("index: returning action response")
            return response
        for argname in request.args:
            if argname in ['filename', 'question', 'format', 'index', 'i', 'action', 'from_list', 'session', 'cache', 'reset']:
                continue
            if re.match('[A-Za-z_]+', argname):
                exec("url_args['" + argname + "'] = " + repr(request.args.get(argname).encode('unicode_escape')), user_dict)
                #logmessage("index: there were args and we need to reset")
            need_to_reset = True
    if need_to_reset:
        #logmessage("index: needed to reset, so redirecting; encrypted is " + str(encrypted))
        if use_cache == 0:
            docassemble.base.parse.interview_source_from_string(yaml_filename).reset_modtime()
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret, encrypt=encrypted)
        response = do_redirect(url_for('index', i=yaml_filename), is_ajax)
        if set_cookie:
            response.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
        release_lock(user_code, yaml_filename)
        return response
    #logmessage("index: made it through")
    post_data = request.form.copy()
    if current_user.is_anonymous:
        the_user_id = 't' + str(session['tempuser'])
    else:
        the_user_id = current_user.id
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
        ci = current_info(yaml=yaml_filename, req=request)
        worker_key = 'da:worker:uid:' + str(user_code) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        for email_address in re.split(r' *[,;] *', attachment_email_address.strip()):
            try:
                result = docassemble.webapp.worker.email_attachments.delay(yaml_filename, ci['user'], user_code, secret, ci['url'], ci['url_root'], email_address, question_number, include_editable)
                r.rpush(worker_key, result.id)
                success = True
            except Exception as errmess:
                success = False
                logmessage("index: failed with " + str(errmess))
                break
        if success:
            flash(word("Your documents will be e-mailed to") + " " + str(attachment_email_address) + ".", 'success')
        else:
            flash(word("Unable to e-mail your documents to") + " " + str(attachment_email_address) + ".", 'error')
    if '_back_one' in post_data and steps > 1:
        steps, user_dict, is_encrypted = fetch_previous_user_dict(user_code, yaml_filename, secret)
        if encrypted != is_encrypted:
            encrypted = is_encrypted
            session['encrypted'] = encrypted
    elif 'filename' in request.args:
        the_user_dict, attachment_encrypted = get_attachment_info(user_code, request.args.get('question'), request.args.get('i'), secret)
        if the_user_dict is not None:
            interview = docassemble.base.interview_cache.get_interview(request.args.get('i'))
            interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=request.args.get('i'), req=request, action=action))
            interview.assemble(the_user_dict, interview_status)
            if len(interview_status.attachments) > 0:
                the_attachment = interview_status.attachments[int(request.args.get('index'))]
                the_filename = the_attachment['file'][request.args.get('format')]
                the_format = request.args.get('format')
                if the_format == "pdf":
                    mime_type = 'application/pdf'
                elif the_format == "tex":
                    mime_type = 'application/x-latex'
                elif the_format == "rtf":
                    mime_type = 'application/rtf'
                elif the_format == "docx":
                    mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                response = send_file(the_filename, mimetype=str(mime_type), as_attachment=True, attachment_filename=str(the_attachment['filename']) + '.' + str(the_format))
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                release_lock(user_code, yaml_filename)
                return(response)
    if '_checkboxes' in post_data:
        checkbox_fields = json.loads(myb64unquote(post_data['_checkboxes'])) #post_data['_checkboxes'].split(",")
        for checkbox_field in checkbox_fields:
            if checkbox_field not in post_data:
                post_data.add(checkbox_field, 'False')
    if '_empties' in post_data:
        empty_fields = json.loads(myb64unquote(post_data['_empties']))
        for empty_field in empty_fields:
            if empty_field not in post_data:
                post_data.add(empty_field, 'None')
    else:
        empty_fields = dict()
    something_changed = False
    if '_tracker' in post_data and user_dict['_internal']['tracker'] != int(post_data['_tracker']):
        if user_dict['_internal']['tracker'] > int(post_data['_tracker']):
            logmessage("index: the assemble function has been run since the question was posed.")
        else:
            logmessage("index: the tracker in the dictionary is behind the tracker in the question.")
        something_changed = True
        user_dict['_internal']['tracker'] = max(int(post_data['_tracker']), user_dict['_internal']['tracker'])
    if '_track_location' in post_data and post_data['_track_location']:
        logmessage("index: found track location of " + post_data['_track_location'])
        the_location = json.loads(post_data['_track_location'])
    else:
        the_location = None
    should_assemble = False
    for key in post_data:
        if key.startswith('_') or key in ['csrf_token', 'ajax']:
            continue
        try:
            if key_requires_preassembly.search(from_safeid(key)):
                should_assemble = True
                #logmessage("index: pre-assembly necessary")
                break
        except:
            logmessage("index: bad key was " + str(key))
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    debug_mode = DEBUG or yaml_filename.startswith('docassemble.playground')
    # if should_assemble and '_action_context' in post_data:
    #     action = json.loads(myb64unquote(post_data['_action_context']))
    interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action, location=the_location), tracker=user_dict['_internal']['tracker'])
    if should_assemble or something_changed:
        interview.assemble(user_dict, interview_status)
        if '_question_name' in post_data and post_data['_question_name'] != interview_status.question.name:
            logmessage("index: not the same question name: " + post_data['_question_name'] + " versus " + interview_status.question.name)
    changed = False
    error_messages = list()
    if '_the_image' in post_data:
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
                filename = secure_filename('canvas.png')
                file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                extension, mimetype = get_ext_and_mimetype(filename)
                new_file = SavedFile(file_number, extension=extension, fix=True)
                new_file.write_content(theImage)
                new_file.finalize()
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ", filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', make_pngs=True, extension='" + str(extension) + "')"
            else:
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ")"
            #logmessage("Doing " + the_string)
            try:
                exec(the_string, user_dict)
                changed = True
                steps += 1
            except Exception as errMess:
                error_messages.append(("error", "Error: " + str(errMess)))
    known_datatypes = dict()
    if '_datatypes' in post_data:
        known_datatypes = json.loads(myb64unquote(post_data['_datatypes']))
    known_varnames = dict()
    if '_varnames' in post_data:
        known_varnames = json.loads(myb64unquote(post_data['_varnames']))
    if '_files' in post_data:
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
            for orig_file_field_raw in file_fields:
                orig_file_field = orig_file_field_raw
                var_to_store = orig_file_field_raw
                if orig_file_field not in request.files and len(known_varnames):
                    for key, val in known_varnames.iteritems():
                        if val == orig_file_field_raw:
                            orig_file_field = key
                            var_to_store = val
                            break
                if orig_file_field in request.files:
                    the_files = request.files.getlist(orig_file_field)
                    if the_files:
                        files_to_process = list()
                        for the_file in the_files:
                            filename = secure_filename(the_file.filename)
                            file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                            extension, mimetype = get_ext_and_mimetype(filename)
                            saved_file = SavedFile(file_number, extension=extension, fix=True)
                            temp_file = tempfile.NamedTemporaryFile(suffix='.' + extension)
                            the_file.save(temp_file.name)
                            process_file(saved_file, temp_file.name, mimetype, extension)
                            #sys.stderr.write("Upload was processed\n")
                            files_to_process.append((filename, file_number, mimetype, extension))
                        try:
                            file_field = from_safeid(var_to_store)
                        except:
                            error_messages.append(("error", "Error: Invalid file_field: " + var_to_store))
                            break
                        if match_invalid.search(file_field):
                            error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                            break
                        if len(files_to_process) > 0:
                            elements = list()
                            indexno = 0
                            for (filename, file_number, mimetype, extension) in files_to_process:
                                elements.append("docassemble.base.core.DAFile('" + file_field + "[" + str(indexno) + "]', filename='" + str(filename) + "', number=" + str(file_number) + ", make_pngs=True, mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')")
                                indexno += 1
                            the_string = file_field + " = docassemble.base.core.DAFileList('" + file_field + "', elements=[" + ", ".join(elements) + "])"
                        else:
                            the_string = file_field + " = None"
                        #logmessage("Doing " + the_string)
                        try:
                            exec(the_string, user_dict)
                            changed = True
                            steps += 1
                        except Exception as errMess:
                            sys.stderr.write("Error: " + str(errMess) + "\n")
                            error_messages.append(("error", "Error: " + str(errMess)))
    known_variables = dict()
    for orig_key in copy.deepcopy(post_data):
        if orig_key in ['_checkboxes', '_empties', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location', '_varnames', 'ajax', 'informed', 'csrf_token']:
            continue
        try:
            key = myb64unquote(orig_key)
        except:
            continue
        if key.startswith('_field_') and orig_key in known_varnames:
            if not (known_varnames[orig_key] in post_data and post_data[known_varnames[orig_key]] != '' and post_data[orig_key] == ''):
                post_data[known_varnames[orig_key]] = post_data[orig_key]
    for orig_key in post_data:
        if orig_key in ['_checkboxes', '_empties', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location', '_varnames', 'ajax', 'informed', 'csrf_token']:
            continue
        #logmessage("Got a key: " + key)
        data = post_data[orig_key]
        try:
            key = myb64unquote(orig_key)
        except:
            raise DAError("invalid name " + str(orig_key))
        if key.startswith('_field_'):
            continue
        bracket_expression = None
        if orig_key in empty_fields:
            #logmessage("orig_key " + str(orig_key) + " is set to empty: " + str(empty_fields[orig_key]))
            set_to_empty = empty_fields[orig_key]
        else:
            #logmessage("orig_key " + str(orig_key) + " is not set to empty")
            set_to_empty = False
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
                    use_initialize = False
                    m = re.search(r'(.*)\.([^.]+)', key)
                    if re.search(r'\.', key):
                        core_key_name = re.sub(r'\..*', '', key)
                        attribute_name = re.sub(r'\..*', '', key)
                        #logmessage("Core key is " + str(core_key_name))
                        try:
                            core_key = eval(core_key, user_dict)
                            if isinstance(core_key, DAObject):
                                use_initialize = True
                        except:
                            pass
                    if use_initialize:
                        the_string = core_key_name + ".initializeAttributecore\n" + key + ' = docassemble.base.core.DADict(' + repr(key) +')'
                    else:
                        the_string = "import docassemble.base.core\n" + key + ' = docassemble.base.core.DADict(' + repr(key) +')'
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
            elif known_datatypes[real_key] == 'date':
                if type(data) in [str, unicode]:
                    data = data.strip()
                data = repr(data)
            elif known_datatypes[real_key] == 'integer':
                if data == '':
                    data = 0
                data = "int(" + repr(data) + ")"
            elif known_datatypes[real_key] in ['number', 'float', 'currency', 'range']:
                if data == '':
                    data = 0
                data = "float(" + repr(data) + ")"
            elif known_datatypes[real_key] in ['object', 'object_radio']:
                if data == '' or set_to_empty:
                    continue
                data = "_internal['objselections'][" + repr(key) + "][" + repr(data) + "]"
            elif known_datatypes[real_key] in ['object_checkboxes'] and bracket_expression is not None:
                if data not in ['True', 'False', 'None'] or set_to_empty:
                    continue
                do_append = True
                if data == 'False':
                    do_opposite = True
                data = "_internal['objselections'][" + repr(from_safeid(real_key)) + "][" + repr(bracket_expression) + "]"
            elif set_to_empty == 'object_checkboxes':
                continue    
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
            #logmessage("key is not in datatypes where datatypes is " + str(known_datatypes))
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
        if set_to_empty:
            if set_to_empty == 'checkboxes':
                try:
                    exec("import docassemble.base.core", user_dict)
                except Exception as errMess:
                    error_messages.append(("error", "Error: " + str(errMess)))
                data = 'docassemble.base.core.DADict(' + repr(key) + ')'
            else:
                data = 'None'
        if do_append and not set_to_empty:
            key_to_use = from_safeid(real_key)
            if do_opposite:
                the_string = 'if ' + data + ' in ' + key_to_use + '.elements:\n    ' + key_to_use + '.remove(' + data + ')'
            else:
                the_string = 'if ' + data + ' not in ' + key_to_use + '.elements:\n    ' + key_to_use + '.append(' + data + ')'
        else:
            the_string = key + ' = ' + data
        #logmessage("Doing " + str(the_string))
        try:
            exec(the_string, user_dict)
            changed = True
            steps += 1
        except Exception as errMess:
            error_messages.append(("error", "Error: " + str(errMess)))
            # logmessage("Error: " + str(errMess))
    for orig_key in empty_fields:
        key = myb64unquote(orig_key)
        #logmessage("Doing key " + str(key))
        if empty_fields[orig_key] == 'object_checkboxes':
            exec(key + '.clear()' , user_dict)
            exec(key + '.gathered = True' , user_dict)
        elif empty_fields[orig_key] in ['object', 'object_radio']:
            try:
                eval(key, user_dict)
            except:
                exec(key + ' = None' , user_dict)
    if 'informed' in request.form:
        user_dict['_internal']['informed'][the_user_id] = dict()
        for key in request.form['informed'].split(','):
            user_dict['_internal']['informed'][the_user_id][key] = 1
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
    # if '_multiple_choice' in post_data and '_question_name' in post_data and post_data['_question_name'] in interview.questions_by_name and not interview.questions_by_name[post_data['_question_name']].is_generic:
    #     interview_status.populate(interview.questions_by_name[post_data['_question_name']].ask(user_dict, 'None', 'None'))
    # else:
    interview.assemble(user_dict, interview_status)
    current_language = docassemble.base.functions.get_language()
    if current_language != DEFAULT_LANGUAGE:
        session['language'] = current_language
    if not interview_status.can_go_back:
        user_dict['_internal']['steps_offset'] = steps
    if len(interview_status.attachments) > 0:
        #logmessage("Updating attachment info")
        update_attachment_info(user_code, user_dict, interview_status, secret)
    if interview_status.question.question_type == "restart":
        manual_checkout()
        url_args = user_dict['url_args']
        user_dict = fresh_dictionary()
        user_dict['url_args'] = url_args
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request))
        reset_user_dict(user_code, yaml_filename)
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
        if current_user.is_authenticated and 'visitor_secret' not in request.cookies:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        steps = 0
        changed = False
        interview.assemble(user_dict, interview_status)
    will_save = True
    if interview_status.question.question_type == "refresh":
        release_lock(user_code, yaml_filename)
        return do_refresh(is_ajax, yaml_filename)
    if interview_status.question.question_type == "signin":
        release_lock(user_code, yaml_filename)
        return do_redirect(url_for('user.login', next=url_for('index', i=yaml_filename, session=user_code)), is_ajax)
    if interview_status.question.question_type == "register":
        release_lock(user_code, yaml_filename)
        return do_redirect(url_for('user.register', next=url_for('index', i=yaml_filename, session=user_code)), is_ajax)
    if interview_status.question.question_type == "leave":
        release_lock(user_code, yaml_filename)
        if interview_status.questionText != '':
            return do_redirect(interview_status.questionText, is_ajax)
        else:
            return do_redirect(exit_page, is_ajax)
    if interview_status.question.interview.use_progress_bar and interview_status.question.progress is not None and interview_status.question.progress > user_dict['_internal']['progress']:
        user_dict['_internal']['progress'] = interview_status.question.progress
    if interview_status.question.question_type == "exit":
        manual_checkout()
        user_dict = fresh_dictionary()
        reset_user_dict(user_code, yaml_filename)
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
        if current_user.is_authenticated and 'visitor_secret' not in request.cookies:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        release_lock(user_code, yaml_filename)
        if interview_status.questionText != '':
            return do_redirect(interview_status.questionText, is_ajax)
        else:
            return do_redirect(exit_page, is_ajax)
    if interview_status.question.question_type == "response":
        if is_ajax:
            # Duplicative to save here?
            #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
            release_lock(user_code, yaml_filename)
            return jsonify(action='resubmit', csrf_token=generate_csrf())
        else:
            if hasattr(interview_status.question, 'all_variables'):
                response_to_send = make_response(docassemble.base.functions.dict_as_json(user_dict).encode('utf8'), '200 OK')
            elif hasattr(interview_status.question, 'binaryresponse'):
                response_to_send = make_response(interview_status.question.binaryresponse, '200 OK')
            else:
                response_to_send = make_response(interview_status.questionText.encode('utf8'), '200 OK')
            response_to_send.headers['Content-type'] = interview_status.extras['content_type']
        if set_cookie:
            response_to_send.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
    elif interview_status.question.question_type == "sendfile":
        if is_ajax:
            #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
            release_lock(user_code, yaml_filename)
            return jsonify(action='resubmit', csrf_token=generate_csrf())
        else:
            # Duplicative to save here?  Just for the 404?
            #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
            if interview_status.question.response_file is not None:
                the_path = interview_status.question.response_file.path()
            else:
                logmessage("index: could not send file because the response was None")
                abort(404)                
            if not os.path.isfile(the_path):
                logmessage("index: could not send file because file (" + the_path + ") not found")
                abort(404)
            response_to_send = send_file(the_path, mimetype=interview_status.extras['content_type'])
            response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        if set_cookie:
            response_to_send.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
    elif interview_status.question.question_type == "redirect":
        # Duplicative to save here?
        #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        response_to_send = do_redirect(interview_status.questionText, is_ajax)
    else:
        response_to_send = None
    # Why do this?  To prevent loops of redirects?
    user_dict['_internal']['answers'] = dict()
    if interview_status.question.name and interview_status.question.name in user_dict['_internal']['answers']:
        del user_dict['_internal']['answers'][interview_status.question.name]
    if action and not changed:
        changed = True
        logmessage("Incrementing steps because action")
        steps += 1
    if changed and interview_status.question.interview.use_progress_bar:
        advance_progress(user_dict)
    #logmessage("index: saving user dict where encrypted is " + str(encrypted))
    save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
    if user_dict.get('multi_user', False) is True and encrypted is True:
        #logmessage("index: post interview, encryption should be False")
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
    # else:
    #     logmessage("index: post interview, no detection of encryption should be False")
    if user_dict.get('multi_user', False) is False and encrypted is False:
        #logmessage("index: post interview, encryption should be True")
        encrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
        encrypted = True
        session['encrypted'] = encrypted
    # else:
    #     logmessage("index: post interview, no detection of encryption should be True")
    if response_to_send is not None:
        release_lock(user_code, yaml_filename)
        return response_to_send
    flash_content = ""
    messages = get_flashed_messages(with_categories=True) + error_messages
    if messages and len(messages):
        flash_content += '<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">'
        for classname, message in messages:
            if classname == 'error':
                classname = 'danger'
            flash_content += '<div class="alert alert-' + classname + '"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>'
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
    if 'reload_after' in interview_status.extras:
        reload_after = 1000 * int(interview_status.extras['reload_after'])
    else:
        reload_after = 0
    if interview_status.question.can_go_back and (steps - user_dict['_internal']['steps_offset']) > 1:
        allow_going_back = True
    else:
        allow_going_back = False
    if not is_ajax:
        scripts = standard_scripts()
        if interview_status.question.checkin is not None:
            do_action = repr(str(interview_status.question.checkin))
        else:
            do_action = 'null'
        if 'javascript' in interview_status.question.interview.external_files:
            for fileref in interview_status.question.interview.external_files['javascript']:
                scripts += '    <script src="' + get_url_from_file_reference(fileref, question=interview_status.question) + '"></script>\n';
        chat_available = user_dict['_internal']['livehelp']['availability']
        chat_mode = user_dict['_internal']['livehelp']['mode']
        #logmessage("index: chat_available is " + str(chat_available))
        if chat_available == 'unavailable':
            chat_status = 'off'
            session['chatstatus'] = 'off'
        elif chat_available == 'observeonly':
            chat_status = 'observeonly'
            session['chatstatus'] = 'observeonly'
        else:
            chat_status = chatstatus
        if chat_status in ['ready', 'on']:
            chat_status = 'ringing'
            session['chatstatus'] = 'ringing'
        if chat_status != 'off':
            send_changes = 'true'
        else:
            if do_action != 'null':
                send_changes = 'true'
            else:
                send_changes = 'false'
        if current_user.is_authenticated:
            user_id_string = str(current_user.id)
            if current_user.has_role('admin', 'developer', 'advocate'):
                is_user = 'false'
            else:
                is_user = 'true'
        else:
            user_id_string = 't' + str(session['tempuser'])
            is_user = 'true'
        if 'uid' in session and 'i' in session:
            if r.get('da:control:uid:' + str(session['uid']) + ':i:' + str(session['i']) + ':userid:' + str(the_user_id)) is not None:
                being_controlled = 'true'
            else:
                being_controlled = 'false'
        else:
            being_controlled = 'false'
        if debug_mode:
            debug_readability_help = """
            $("#readability-help").show();
            $("#readability-question").hide();
"""
            debug_readability_question = """
            $("#readability-help").hide();
            $("#readability-question").show();
"""
        else:
            debug_readability_help = ''
            debug_readability_question = ''
        scripts += """    <script type="text/javascript" charset="utf-8">
      var map_info = null;
      var whichButton = null;
      var socket = null;
      var foobar = null;
      var chatHistory = [];
      var daCheckinCode = null;
      var daCheckingIn = 0;
      var daShowingHelp = 0;
      var daAllowGoingBack = """ + ('true' if allow_going_back else 'false') + """;
      var daSteps = """ + str(steps) + """;
      var daIsUser = """ + is_user + """;
      var daChatStatus = """ + repr(str(chat_status)) + """;
      var daChatAvailable = """ + repr(str(chat_available)) + """;
      var daChatPartnersAvailable = 0;
      var daPhoneAvailable = false;
      var daChatMode = """ + repr(str(chat_mode)) + """;
      var daSendChanges = """ + send_changes + """;
      var daInitialized = false;
      var notYetScrolled = true;
      var daBeingControlled = """ + being_controlled + """;
      var daInformedChanged = false;
      var daInformed = """ + json.dumps(user_dict['_internal']['informed'].get(user_id_string, dict())) + """;
      var daShowingSpinner = false;
      var daSpinnerTimeout = null;
      var daSubmitter = null;
      var daDoAction = """ + do_action + """;
      var daCsrf = """ + repr(str(generate_csrf())) + """;
      function preloadImage(url){
        var img = new Image();
        img.src = url;
      }
      preloadImage('""" + str(url_for('static', filename='app/loader.gif')) + """');
      preloadImage('""" + str(url_for('static', filename='app/chat.ico')) + """');
      preloadImage('""" + str(url_for('static', filename='jquery-labelauty/source/images/checkbox-unchecked.png')) + """');
      preloadImage('""" + str(url_for('static', filename='jquery-labelauty/source/images/input-unchecked.png')) + """');
      preloadImage('""" + str(url_for('static', filename='jquery-labelauty/source/images/checkbox-checked.png')) + """');
      preloadImage('""" + str(url_for('static', filename='jquery-labelauty/source/images/input-checked.png')) + """');
      preloadImage('""" + str(url_for('static', filename='jquery-labelauty/source/images/radio-unchecked.png')) + """');
      preloadImage('""" + str(url_for('static', filename='jquery-labelauty/source/images/radio-checked.png')) + """');
      preloadImage('""" + str(url_for('static', filename='bootstrap-fileinput/img/loading-sm.gif')) + """');
      preloadImage('""" + str(url_for('static', filename='bootstrap-fileinput/img/loading.gif')) + """');
      function url_action(action, args){
          if (args == null){
              args = {};
          }
          data = {action: action, arguments: args};
          return '?action=' + encodeURIComponent(btoa(JSON.stringify(data)));
      }
      function show_help_tab(){
          $('#helptoggle').trigger('click');
      }
      function url_action_call(action, args, callback){
          if (args == null){
              args = {};
          }
          if (callback == null){
              callback = function(){};
          }
          var data = {action: action, arguments: args};
          $.ajax({
            type: "GET",
            url: "?action=" + encodeURIComponent(btoa(JSON.stringify(data))),
            success: callback,
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
      }
      function get_interview_variables(callback){
          if (callback == null){
              callback = function(){};
          }
          $.ajax({
            type: "GET",
            url: """ + '"' + url_for('get_variables') + '"' + """,
            success: callback,
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
      }
      function userNameString(data){
          if (data.hasOwnProperty('temp_user_id')){
              return """ + repr(str(word("anonymous visitor"))) + """ + ' ' + data.temp_user_id;
          }
          else{
              if (data.first_name != '' && data.first_name != ''){
                  return data.first_name + ' ' + data.last_name;
              }
              else{
                  return data.email;
              }
          }
      }
      function inform_about(subject){
        if (subject in daInformed || (subject != 'chatmessage' && !daIsUser)){
          return;
        }
        if (daShowingHelp && subject != 'chatmessage'){
          daInformed[subject] = 1;
          daInformedChanged = true;
          return;
        }
        if (daShowingHelp && subject == 'chatmessage'){
          return;
        }
        var target;
        var message;
        var waitPeriod = 3000;
        if (subject == 'chat'){
          target = "#daChatAvailable i";
          message = """ + repr(str(word("Get help through live chat by clicking here."))) + """;
        }
        else if (subject == 'chatmessage'){
          target = "#daChatAvailable i";
          message = """ + repr(str(word("A chat message has arrived."))) + """;
        }
        else if (subject == 'phone'){
          target = "#daPhoneAvailable i";
          message = """ + repr(str(word("Click here to get help over the phone."))) + """;
        }
        else{
          return;
        }
        if (subject != 'chatmessage'){
          daInformed[subject] = 1;
          daInformedChanged = true;
        }
        $(target).popover({"content": message, "placement": "bottom", "trigger": "manual", "container": "body"});
        $(target).popover('show');
        setTimeout(function(){
          $(target).popover('destroy');
          $(target).removeAttr('title');
        }, waitPeriod);
      }
      // function daCloseSocket(){
      //   if (typeof socket !== 'undefined' && socket.connected){
      //     //socket.emit('terminate');
      //     //io.unwatch();
      //   }
      // }
      function publishMessage(data){
        var newDiv = document.createElement('li');
        $(newDiv).addClass("list-group-item");
        if (data.is_self){
          $(newDiv).addClass("list-group-item-warning dalistright");
        }
        else{
          $(newDiv).addClass("list-group-item-info");
        }
        //var newSpan = document.createElement('span');
        //$(newSpan).html(data.message);
        //$(newSpan).appendTo($(newDiv));
        //var newName = document.createElement('span');
        //$(newName).html(userNameString(data));
        //$(newName).appendTo($(newDiv));
        $(newDiv).html(data.message);
        $("#daCorrespondence").append(newDiv);
      }
      function scrollChat(){
        var chatScroller = $("#daCorrespondence");
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
          //console.log("Slow scrolling to " + height);
          if (height == 0){
            notYetScrolled = true;
            return;
          }
          chatScroller.animate({scrollTop: height}, 800);
        }
        else{
          console.log("scrollChat: error");
        }
      }
      function scrollChatFast(){
        var chatScroller = $("#daCorrespondence");
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
          if (height == 0){
            notYetScrolled = true;
            return;
          }
          //console.log("Scrolling to " + height + " where there are " + chatScroller[0].childElementCount + " children");
          chatScroller.scrollTop(height);
        }
        else{
          console.log("scrollChatFast: error");
        }
      }
      function daSender(){
        //console.log("daSender");
        if ($("#daMessage").val().length){
          socket.emit('chatmessage', {data: $("#daMessage").val()});
          $("#daMessage").val("");
          $("#daMessage").focus();
        }
        return false;
      }
      function show_control(mode){
        //console.log("You are now being controlled");
        if ($("body").hasClass("dacontrolled")){
          return;
        }
        $('input[type="submit"], button[type="submit"]').prop("disabled", true);
        $("body").addClass("dacontrolled");
        var newDiv = document.createElement('div');
        $(newDiv).addClass("top-alert col-xs-10 col-sm-7 col-md-6 col-lg-5 col-centered");
        $(newDiv).html(""" + repr(str(word("Your screen is being controlled by an operator."))) + """)
        $(newDiv).attr('id', "controlAlert");
        $(newDiv).css("display", "none");
        $(newDiv).appendTo($("body"));
        if (mode == 'animated'){
          $(newDiv).slideDown();
        }
        else{
          $(newDiv).show();
        }
      }
      function hide_control(){
        //console.log("You are no longer being controlled");
        if (! $("body").hasClass("dacontrolled")){
          return;
        }
        $('input[type="submit"], button[type="submit"]').prop("disabled", false);
        $("body").removeClass("dacontrolled");
        $("#controlAlert").html(""" + repr(str(word("The operator is no longer controlling your screen."))) + """);
        setTimeout(function(){
          $("#controlAlert").slideUp(300, function(){
            $("#controlAlert").remove();
          });
        }, 2000);
      }
      function daInitializeSocket(){
        if (socket != null){
            if (socket.connected){
                //console.log("Calling connectagain");
                if (daChatStatus == 'ready'){
                  socket.emit('connectagain', {data: 1});
                }
                if (daBeingControlled){
                    show_control('animated');
                    socket.emit('start_being_controlled', {data: 1});
                }
            }
            else{
                //console.log('daInitializeSocket: socket.connect()');
                socket.connect();
            }
            return;
        }
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/interview", {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/interview" + location.port, {path: '/ws/socket.io'});
        }
        //console.log("daInitializeSocket: socket is " + socket);
        if (socket != null){
            socket.on('connect', function() {
                if (socket == null){
                    console.log("Error: socket is null");
                    return;
                }
                //console.log("Connected socket with sid " + socket.id);
                if (daChatStatus == 'ready'){
                    daChatStatus = 'on';
                    display_chat();
                    pushChanges();
                    //daTurnOnChat();
                    //console.log("Emitting chat_log from on connect");
                    socket.emit('chat_log', {data: 1});
                }
                if (daBeingControlled){
                    show_control('animated')
                    socket.emit('start_being_controlled', {data: 1});
                }
            });
            socket.on('chat_log', function(arg) {
                //console.log("Got chat_log");
                $("#daCorrespondence").html('');
                chatHistory = []; 
                var messages = arg.data;
                for (var i = 0; i < messages.length; ++i){
                    chatHistory.push(messages[i]);
                    publishMessage(messages[i]);
                }
                scrollChatFast();
            });
            socket.on('chatready', function(data) {
                //var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                //console.log('chatready');
            });
            socket.on('terminate', function() {
                //console.log("interview: terminating socket");
                socket.disconnect();
            });
            socket.on('controllerstart', function(){
              daBeingControlled = true;
              show_control('animated');
            });
            socket.on('controllerexit', function(){
              daBeingControlled = false;
              hide_control();
              if (daChatStatus != 'on'){
                if (socket != null && socket.connected){
                  //console.log('Terminating interview socket because control over');
                  socket.emit('terminate');
                }
              }
            });
            socket.on('disconnect', function() {
                //console.log("Disconnected socket");
                //socket = null;
            });
            socket.on('reconnected', function() {
                //console.log("Reconnected");
                daChatStatus = 'on';
                display_chat();
                pushChanges();
                daTurnOnChat();
                //console.log("Emitting chat_log from reconnected");
                socket.emit('chat_log', {data: 1});
            });
            socket.on('mymessage', function(arg) {
                //console.log("Received " + arg.data);
                $("#daPushResult").html(arg.data);
            });
            socket.on('departure', function(arg) {
                //console.log("Departure " + arg.numpartners);
                if (arg.numpartners == 0){
                    daCloseChat();
                }
            });
            socket.on('chatmessage', function(arg) {
                //console.log("Received chat message " + arg.data);
                chatHistory.push(arg.data);
                publishMessage(arg.data);
                scrollChat();
                inform_about('chatmessage');
            });
            socket.on('newpage', function(incoming) {
                //console.log("newpage received");
                var data = incoming.obj;
                daProcessAjax(data, $("#daform"));
            });
            socket.on('controllerchanges', function(data) {
                //console.log("controllerchanges: " + data.parameters);
                var valArray = Object();
                var values = JSON.parse(data.parameters);
                for (var i = 0; i < values.length; i++) {
                    valArray[values[i].name] = values[i].value;
                }
                //console.log("valArray is " + JSON.stringify(valArray));
                $("#daform").each(function(){
                    $(this).find(':input').each(function(){
                        var type = $(this).attr('type');
                        var id = $(this).attr('id');
                        var name = $(this).attr('name');
                        if (type == 'checkbox'){
                            if (name in valArray){
                                if (valArray[name] == 'True'){
                                    $(this).prop('checked', true);
                                }
                                else{
                                    $(this).prop('checked', false);
                                }
                            }
                            else{
                                $(this).prop('checked', false);
                            }
                        }
                        else if (type == 'radio'){
                            if (name in valArray){
                                if (valArray[name] == $(this).val()){
                                    $(this).prop('checked', true);
                                }
                                else{
                                    $(this).prop('checked', false);
                                }
                            }
                        }
                        else if ($(this).data().hasOwnProperty('sliderMax')){
                            $(this).slider('setValue', parseInt(valArray[name]));
                        }
                        else{
                            if (name in valArray){
                                $(this).val(valArray[name]);
                            }
                        }
                    });
                });
                if (data.clicked){
                    //console.log("Need to click " + data.clicked);
                    $(data.clicked).prop("disabled", false);
                    $(data.clicked).addClass("click-selected");
                    setTimeout(function(){
                      $(data.clicked).click();
                    }, 200);
                }
            });
        }
      }
      var checkinInterval = null;
      var daReloader = null;
      var dadisable = null;
      var daChatRoles = """ + json.dumps(user_dict['_internal']['livehelp']['roles']) + """;
      var daChatPartnerRoles = """ + json.dumps(user_dict['_internal']['livehelp']['partner_roles']) + """;
      function daValidationHandler(form){
        //form.submit();
        $("#daform").each(function(){
          $(this).find(':input').off('change', pushChanges);
        });
        $("meta[name=viewport]").attr('content', "width=device-width, minimum-scale=1.0, maximum-scale=1.0, initial-scale=1.0");
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
        dadisable = setTimeout(function(){
          $(form).find('input[type="submit"]').prop("disabled", true);
          $(form).find('button[type="submit"]').prop("disabled", true);
        }, 1);
        if (whichButton != null){
          $(".btn-lg").each(function(){
            if (this != whichButton){
              $(this).removeClass("btn-primary btn-info btn-warning btn-error");
              $(this).addClass("btn-default");
            }
          });
          if ($(whichButton).hasClass("btn-success")){
            $(whichButton).removeClass("btn-success");
            $(whichButton).addClass("btn-primary");
          }
          else{
            $(whichButton).removeClass("btn-primary btn-info btn-warning btn-error btn-default");
            $(whichButton).addClass("btn-success");
          }
        }
        whichButton = null;
        if ($('input[name="_files"]').length){
          $("#uploadiframe").remove();
          var iframe = $('<iframe name="uploadiframe" id="uploadiframe" style="display: none"></iframe>');
          $("body").append(iframe);
          $(form).attr("target", "uploadiframe");
          $('<input>').attr({
              type: 'hidden',
              name: 'ajax',
              value: '1'
          }).appendTo($(form));
          iframe.bind('load', function(){
            setTimeout(function(){
              daProcessAjax($.parseJSON($("#uploadiframe").contents().text()), form);
            }, 0);
          });
          form.submit();
        }
        else{
          if (daSubmitter != null){
            var input = $("<input>")
              .attr("type", "hidden")
              .attr("name", daSubmitter.name).val(daSubmitter.value);
            $(form).append($(input));
          }
          var informed = '';
          if (daInformedChanged){
            informed = '&informed=' + Object.keys(daInformed).join(',');
          }
          $.ajax({
            type: "POST",
            url: $(form).attr('action'),
            data: $(form).serialize() + '&ajax=1' + informed, 
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, form);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
        }
        daSpinnerTimeout = setTimeout(showSpinner, 1000);
        return(false);
      }
      function pushChanges(){
        //console.log("pushChanges");
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
        daCheckin();
        checkinInterval = setInterval(daCheckin, """ + str(CHECKIN_INTERVAL) + """);
      }
      function daProcessAjaxError(xhr, status, error){
        //console.log("Got error: " + error);
        //console.log("Status was: " + status);
        $("body").html(xhr.responseText);
      }
      function addScriptToHead(src){
        var head = document.getElementsByTagName("head")[0];
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = src;
        script.async = true;
        script.defer = true;
        head.appendChild(script);
        //console.log("All done");
      }
      function daProcessAjax(data, form){
        daInformedChanged = false;
        if (dadisable != null){
          clearTimeout(dadisable);
        }
        daCsrf = data.csrf_token;
        if (data.action == 'body'){
          $("body").html(data.body);
          $("body").removeClass();
          $("body").addClass(data.bodyclass);
          $("meta[name=viewport]").attr('content', "width=device-width, initial-scale=1");
          daDoAction = data.do_action;
          daChatAvailable = data.livehelp.availability;
          daChatMode = data.livehelp.mode;
          daChatRoles = data.livehelp.roles;
          daChatPartnerRoles = data.livehelp.partner_roles;
          daSteps = data.steps;
          daAllowGoingBack = data.allow_going_back;
          history.pushState({steps: daSteps}, data.browser_title + " - page " + daSteps, "#page" + daSteps);
          daInitialize();
          var tempDiv = document.createElement('div');
          tempDiv.innerHTML = data.extra_scripts;
          var scripts = tempDiv.getElementsByTagName('script');
          for (var i = 0; i < scripts.length; i++){
            //console.log("Found one script");
            if (scripts[i].src != ""){
              //console.log("Added script to head");
              addScriptToHead(scripts[i].src);
            }
            else{
              eval(scripts[i].innerHTML);
            }
          }
          for (var i = 0; i < data.extra_css.length; i++){
            $("head").append(data.extra_css[i]);
          }
          document.title = data.browser_title;
          if ($("html").attr("lang") != data.lang){
            $("html").attr("lang", data.lang);
          }
          if (daReloader != null){
            clearTimeout(daReloader);
          }
          if (data.reload_after != null && data.reload_after > 0){
            //daReloader = setTimeout(function(){location.reload();}, data.reload_after);
            daReloader = setTimeout(function(){daRefreshSubmit();}, data.reload_after);
          }
          daUpdateHeight();
        }
        else if (data.action == 'redirect'){
          window.location = data.url;
        }
        else if (data.action == 'refresh'){
          daRefreshSubmit();
        }
        else if (data.action == 'resubmit'){
          if (daSubmitter != null){
            var input = $("<input>")
              .attr("type", "hidden")
              .attr("name", daSubmitter.name).val(daSubmitter.value);
            $(form).append($(input));
          }
          form.submit();
        }
      }
      function daRingChat(){
        daChatStatus = 'ringing';
        pushChanges();
      }
      function daTurnOnChat(){
        //console.log("Publishing from daTurnOnChat");
        $("#daChatOnButton").addClass("invisible");
        $("#daChatBox").removeClass("invisible");
        $("#daCorrespondence").html('');
        for(var i = 0; i < chatHistory.length; i++){
          publishMessage(chatHistory[i]);
        }
        scrollChatFast();
        $("#daMessage").prop('disabled', false);
        if (daShowingHelp){
          $("#daMessage").focus();
        }
      }
      function daCloseChat(){
        //console.log('daCloseChat');
        daChatStatus = 'hangup';
        pushChanges();
        if (socket != null && socket.connected){
          socket.disconnect();
        }
      }
      // function daTurnOffChat(){
      //   $("#daChatOnButton").removeClass("invisible");
      //   $("#daChatBox").addClass("invisible");
      //   //daCloseSocket();
      //   $("#daMessage").prop('disabled', true);
      //   $("#daSend").unbind();
      //   //daStartCheckingIn();
      // }
      function display_chat(){
        if (daChatStatus == 'off' || daChatStatus == 'observeonly'){
          $("#daChatBox").addClass("invisible");
          $("#daChatAvailable").addClass("invisible");
          $("#daChatOnButton").addClass("invisible");
        }
        else{
          if (daChatStatus == 'waiting'){
            if (daChatPartnersAvailable > 0){
              $("#daChatBox").removeClass("invisible");
            }
          }
          else {
            $("#daChatBox").removeClass("invisible");
          }
        }
        if (daChatStatus == 'waiting'){
          //console.log("I see waiting")
          if (chatHistory.length > 0){
            $("#daChatAvailable i").removeClass("chat-active");
            $("#daChatAvailable i").addClass("chat-inactive");
            $("#daChatAvailable").removeClass("invisible");
          }
          else{
            $("#daChatAvailable i").removeClass("chat-active");
            $("#daChatAvailable i").removeClass("chat-inactive");
            $("#daChatAvailable").addClass("invisible");
          }
          $("#daChatOnButton").addClass("invisible");
          $("#daChatOffButton").addClass("invisible");
          $("#daMessage").prop('disabled', true);
          $("#daSend").prop('disabled', true);
        }
        if (daChatStatus == 'standby' || daChatStatus == 'ready'){
          //console.log("I see standby")
          $("#daChatAvailable").removeClass("invisible");
          $("#daChatAvailable i").removeClass("chat-inactive");
          $("#daChatAvailable i").addClass("chat-active");
          $("#daChatOnButton").removeClass("invisible");
          $("#daChatOffButton").addClass("invisible");
          $("#daMessage").prop('disabled', true);
          $("#daSend").prop('disabled', true);
          inform_about('chat');
        }
        if (daChatStatus == 'on'){
          $("#daChatAvailable").removeClass("invisible");
          $("#daChatAvailable i").removeClass("chat-inactive");
          $("#daChatAvailable i").addClass("chat-active");
          $("#daChatOnButton").addClass("invisible");
          $("#daChatOffButton").removeClass("invisible");
          $("#daMessage").prop('disabled', false);
          if (daShowingHelp){
            $("#daMessage").focus();
          }
          $("#daSend").prop('disabled', false);
          inform_about('chat');
        }
      }
      function daChatLogCallback(data){
        //console.log("daChatLogCallback: success is " + data.success);
        if (data.success){
          $("#daCorrespondence").html('');
          chatHistory = []; 
          var messages = data.messages;
          for (var i = 0; i < messages.length; ++i){
            chatHistory.push(messages[i]);
            publishMessage(messages[i]);
          }
          display_chat();
          scrollChatFast();
        }
      }
      function daRefreshSubmit(){
        $.ajax({
          type: "POST",
          url: $('#daform').attr('action'),
          data: 'csrf_token=' + daCsrf + '&ajax=1',
          success: function(data){
            setTimeout(function(){
              daProcessAjax(data, $("#daform"));
            }, 0);
          },
          error: function(xhr, status, error){
            setTimeout(function(){
              daProcessAjaxError(xhr, status, error);
            }, 0);
          }
        });
      }
      function daResetCheckinCode(){
        daCheckinCode = Math.random();
      }
      function daCheckinCallback(data){
        daCheckingIn = 0;
        //console.log("daCheckinCallback: success is " + data.success);
        if (data.checkin_code != daCheckinCode){
          //console.log("Ignoring checkincallback because code is wrong");
          return;
        }
        if (data.success){
          if (data.commands.length > 0){
            for (var i = 0; i < data.commands.length; ++i){
              var command = data.commands[i];
              if (command.extra == 'flash'){
                if (!$("#flash").length){
                  $("body").append('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash"></div>');
                }
                $("#flash").append('<div class="alert alert-info alert-interlocutory"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + command.value + '</div>');
                //console.log("command is " + command.value);
              }
              else if (command.extra == 'refresh'){
                daRefreshSubmit();
              }
              else if (command.extra == 'javascript'){
                eval(command.value);
              }
              else if (command.extra == 'backgroundresponse'){
                var assignments = Array();
                if (command.value.hasOwnProperty('target') && command.value.hasOwnProperty('content')){
                  assignments.push({target: command.value.target, content: command.value.content});
                }
                if (Array.isArray(command.value)){
                  for (i = 0; i < command.value.length; ++i){
                    var possible_assignment = command.value[i];
                    if (possible_assignment.hasOwnProperty('target') && possible_assignment.hasOwnProperty('content')){
                      assignments.push({target: possible_assignment.target, content: possible_assignment.content});
                    }
                  }
                }
                for (i = 0; i < assignments.length; ++i){
                  var assignment = assignments[i];
                  $('#datarget' + assignment.target.replace(/[^A-Za-z0-9\_]/g)).html(assignment.content);
                }
                $(document).trigger('daCheckIn', [command.action, command.value]);
              }
            }
            // setTimeout(function(){
            //   $("#flash .alert-interlocutory").hide(300, function(){
            //     $(self).remove();
            //   });
            // }, 5000);
          }
          oldDaChatStatus = daChatStatus;
          //console.log("daCheckinCallback: from " + daChatStatus + " to " + data.chat_status);
          if (data.phone == null){
            $("#daPhoneMessage").addClass("invisible");
            $("#daPhoneMessage p").html('');
            $("#daPhoneAvailable").addClass("invisible");
            daPhoneAvailable = false;
          }
          else{
            $("#daPhoneMessage").removeClass("invisible");
            $("#daPhoneMessage p").html(data.phone);
            $("#daPhoneAvailable").removeClass("invisible");
            daPhoneAvailable = true;
            inform_about('phone');
          }
          var statusChanged;
          if (daChatStatus == data.chat_status){
            statusChanged = false;
          }
          else{
            statusChanged = true;
          }
          if (statusChanged){
            daChatStatus = data.chat_status;
            display_chat();
            if (daChatStatus == 'ready'){
              //console.log("calling initialize socket because ready");
              daInitializeSocket();
            }
          }
          daChatPartnersAvailable = 0;
          if (daChatMode == 'peer' || daChatMode == 'peerhelp'){
            daChatPartnersAvailable += data.num_peers;
            if (data.num_peers == 1){
              $("#peerMessage").html('<span class="badge btn-info">' + data.num_peers + ' """ + word("other user") + """</span>');
            }
            else{
              $("#peerMessage").html('<span class="badge btn-info">' + data.num_peers + ' """ + word("other users") + """</span>');
            }
            $("#peerMessage").removeClass("invisible");
          }
          else{
            $("#peerMessage").addClass("invisible");
          }
          if (daChatMode == 'peerhelp' || daChatMode == 'help'){
            if (data.help_available == 1){
              $("#peerHelpMessage").html('<span class="badge btn-primary">' + data.help_available + ' """ + word("operator") + """</span>');
            }
            else{
              $("#peerHelpMessage").html('<span class="badge btn-primary">' + data.help_available + ' """ + word("operators") + """</span>');
            }
            $("#peerHelpMessage").removeClass("invisible");
          }
          else{
            $("#peerHelpMessage").addClass("invisible");
          }
          if (daBeingControlled){
            if (!data.observerControl){
              daBeingControlled = false;
              hide_control();
              if (daChatStatus != 'on'){
                if (socket != null && socket.connected){
                  //console.log('Terminating interview socket because control is over');
                  socket.emit('terminate');
                }
              }
            }
          }
          else{
            if (data.observerControl){
              daBeingControlled = true;
              daInitializeSocket();
            }
          }
        }
      }
      function daCheckoutCallback(data){
      }
      function daCheckin(){
        //console.log("daCheckin");
        daCheckingIn += 1;
        if (daCheckingIn > 1 && !(daCheckingIn % 3)){
          //console.log("daCheckin: request already pending, not re-sending");
          return;
        }
        var datastring;
        if ((daChatStatus != 'off') && $("#daform").length > 0 && !daBeingControlled){ // daChatStatus == 'waiting' || daChatStatus == 'standby' || daChatStatus == 'ringing' || daChatStatus == 'ready' || daChatStatus == 'on' || daChatStatus == 'observeonly'
          if (daDoAction != null){
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode, parameters: JSON.stringify($("#daform").serializeArray()), do_action: daDoAction});
          }
          else{
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode, parameters: JSON.stringify($("#daform").serializeArray())});
          }
        }
        else{
          if (daDoAction != null){
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode, do_action: daDoAction, parameters: JSON.stringify($("#daform").serializeArray())});
          }
          else{
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode});
          }
        }
        //console.log("Doing checkin with " + daChatStatus);
        $.ajax({
          type: 'POST',
          url: """ + "'" + url_for('checkin') + "'" + """,
          data: datastring,
          success: daCheckinCallback,
          dataType: 'json'
        });
        return true;
      }
      function daCheckout(){
        $.ajax({
          type: 'POST',
          url: """ + "'" + url_for('checkout') + "'" + """,
          data: 'csrf_token=' + daCsrf + '&action=checkout',
          success: daCheckoutCallback,
          dataType: 'json'
        });
        return true;
      }
      function daStopCheckingIn(){
        daCheckout();
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
      }
      //function daStartCheckingIn(){
      //  daStopCheckingIn();
      //  checkinInterval = setInterval(daCheckin, """ + str(CHECKIN_INTERVAL) + """);
      //}
      function showSpinner(){
        if ($("#question").length > 0){
          $('<div id="daSpinner" class="spinner-container"><div class="container"><div class="row"><div class="col-lg-6 col-md-8 col-sm-10"><img class="da-spinner" src=""" + '"' + str(url_for('static', filename='app/loader.gif')) + '"' + """></div></div></div></div>').appendTo("body");
        }
        else{
          var newImg = document.createElement('img');
          $(newImg).attr("src", """ + repr(str(url_for('static', filename='app/loader.gif'))) + """);
          $(newImg).attr("id", "daSpinner");
          $(newImg).addClass("da-sig-spinner");
          $(newImg).appendTo("#sigtoppart");
        }
        daShowingSpinner = true;
      }
      function hideSpinner(){
        $("#daSpinner").remove();
        daShowingSpinner = false;
        daSpinnerTimeout = null;
      }
      function adjustInputWidth(e){
        var contents = $(this).val();
        contents = contents.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/ /g, '&nbsp;');
        $('<span class="input-embedded" id="dawidth">').html( contents ).appendTo('body');
        $(this).width($('#dawidth').width() + 16);
        $('#dawidth').remove();
      }
      function daInitialize(){
        daResetCheckinCode();
        if (daSpinnerTimeout != null){
          clearTimeout(daSpinnerTimeout);
          daSpinnerTimeout = null;
        }
        if (daShowingSpinner){
          hideSpinner();
        }
        notYetScrolled = true;
        $('#source').on('hide.bs.collapse', function (e) {
          $("#readability").slideUp();
        });
        $('#source').on('show.bs.collapse', function (e) {
          if (daShowingHelp){
            $("#readability-question").hide();
            $("#readability-help").show();
          }
          else{
            $("#readability-help").hide();
            $("#readability-question").show();
          }
          $("#readability").slideDown();
        });
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
          if ($(e.target).attr("href") == '#help'){
            daShowingHelp = 1;
            if (notYetScrolled){
              scrollChatFast();
              notYetScrolled = false;
            }""" + debug_readability_help + """
          }
          else if ($(e.target).attr("href") == '#question'){
            daShowingHelp = 0;""" + debug_readability_question + """
          }
        });
        $("input.input-embedded").on('keyup', adjustInputWidth);
        $("input.input-embedded").each(adjustInputWidth);
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'click focus', html: true})
        });
        if (daPhoneAvailable){
          $("#daPhoneAvailable").removeClass("invisible");
        }
        $("#daChatOnButton").click(daRingChat);
        $("#daChatOffButton").click(daCloseChat);
        $('#daMessage').bind('keypress keydown keyup', function(e){
          if(e.keyCode == 13) { daSender(); e.preventDefault(); }
        });
        $('#daform button[type="submit"]').click(function(){
          daSubmitter = this;
          return true;
        });
        $('#daform input[type="submit"]').click(function(){
          daSubmitter = this;
          return true;
        });
        $('#emailform button[type="submit"]').click(function(){
          daSubmitter = this;
          return true;
        });
        $("body").focus();
        $("#daform input, #daform textarea, #daform select").first().each(function(){
          $(this).focus();
          var inputType = $(this).attr('type');
          if ($(this).prop('tagName') != 'SELECT' && inputType != "checkbox" && inputType != "radio" && inputType != "hidden" && inputType != "submit" && inputType != "file" && inputType != "range" && inputType != "number" && inputType != "date"){
            var strLength = $(this).val().length * 2;
            $(this)[0].setSelectionRange(strLength, strLength);
          }
        });
        $(".to-labelauty").labelauty({ class: "labelauty fullwidth" });
        $(".to-labelauty-icon").labelauty({ label: false });
        $(function(){ 
          var navMain = $("#navbar-collapse");
          navMain.on("click", "a", null, function () {
            if (!($(this).hasClass("dropdown-toggle"))){
              navMain.collapse('hide');
            }
          });
          $("#helptoggle").on("click", function(){
            //console.log("Got to helptoggle");
            window.scrollTo(0, 1);
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
          var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
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
        $("#daSend").click(daSender);
        if (daChatAvailable == 'unavailable'){
          daChatStatus = 'off';
        }
        if (daChatAvailable == 'observeonly'){
          daChatStatus = 'observeonly';
        }
        if ((daChatStatus == 'off' || daChatStatus == 'observeonly') && daChatAvailable == 'available'){
          daChatStatus = 'waiting';
        }
        display_chat();
        if (daBeingControlled){
          show_control('fast');
        }
        if (daChatStatus == 'ready' || daBeingControlled){
          daInitializeSocket();
        }
        if (true || daInitialized == false){
          setTimeout(function(){
            //console.log("daInitialize call to chat_log in checkin");
            $.ajax({
              type: 'POST',
              url: """ + "'" + url_for('checkin') + "'" + """,
              data: $.param({action: 'chat_log', csrf_token: daCsrf}),
              success: daChatLogCallback,
              dataType: 'json'
            });
          }, 200);
        }
        if (daInitialized == true){
          //console.log("Publishing from memory");
          $("#daCorrespondence").html('');
          for(var i = 0; i < chatHistory.length; i++){
            publishMessage(chatHistory[i]);
          }
        }
        if (daChatStatus != 'off'){
          daSendChanges = true;
        }
        else{
          if (daDoAction == null){
            daSendChanges = false;
          }
          else{
            daSendChanges = true;
          }
        }
        if (daSendChanges){
          $("#daform").each(function(){
            $(this).find(':input').change(pushChanges);
          });
        }
        daInitialized = true;
        daShowingHelp = 0;
        daSubmitter = null;
        setTimeout(function(){
          $("#flash .alert-success").hide(300, function(){
            $(self).remove();
          });
        }, 3000);
        setTimeout(function () {
          window.scrollTo(0, 1);
        }, 10);
        if (daShowingSpinner){
          hideSpinner();
        }
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
        setTimeout(daCheckin, 100);
        checkinInterval = setInterval(daCheckin, """ + str(CHECKIN_INTERVAL) + """);
        $(document).trigger('daPageLoad');
      }
      $(document).ready(function(){
        daInitialize();
        history.replaceState({steps: daSteps}, "", "#page" + daSteps);
        var daReloadAfter = """ + str(int(reload_after)) + """;
        if (daReloadAfter > 0){
          daReloader = setTimeout(function(){daRefreshSubmit();}, daReloadAfter);
        }
        // setTimeout(daCheckin, 100);
        // checkinInterval = setInterval(daCheckin, """ + str(CHECKIN_INTERVAL) + """);
        window.onpopstate = function(event) {
          if (event.state.steps < daSteps && daAllowGoingBack){
            $("#backbutton").submit();
          }
        };
        $( window ).bind('unload', function() {
          daStopCheckingIn();
          if (socket != null && socket.connected){
            //console.log('Terminating interview socket because window unloaded');
            socket.emit('terminate');
          }
        });
      });
      $(window).ready(daUpdateHeight);
      $(window).resize(daUpdateHeight);
      function daUpdateHeight(){
        $(".googleMap").each(function(){
          var size = $( this ).width();
          $( this ).css('height', size);
        });
      }
      function daAddMap(map_num, center_lat, center_lon){
        var map = new google.maps.Map(document.getElementById("map" + map_num), {
          zoom: 11,
          center: new google.maps.LatLng(center_lat, center_lon),
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });
        var infowindow = new google.maps.InfoWindow();
        return({map: map, infowindow: infowindow});
      }
      function daAddMarker(map, marker_info, show_marker){
        var marker;
        if (marker_info.icon){
          if (marker_info.icon.path){
            marker_info.icon.path = google.maps.SymbolPath[marker_info.icon.path];
          }
        }
        else{
          marker_info.icon = null;
        }
        marker = new google.maps.Marker({
          position: new google.maps.LatLng(marker_info.latitude, marker_info.longitude),
          map: map.map,
          icon: marker_info.icon
        });
        if(marker_info.info){
          google.maps.event.addListener(marker, 'click', (function(marker, info) {
            return function() {
              map.infowindow.setContent(info);
              map.infowindow.open(map.map, marker);
            }
          })(marker, marker_info.info));
        }
        if(show_marker){
          map.infowindow.setContent(marker_info.info);
          map.infowindow.open(map.map, marker);
        }
        return marker;
      }
      function daInitMap(){
        maps = [];
        map_info_length = map_info.length;
        for (var i = 0; i < map_info_length; i++){
          the_map = map_info[i];
          var bounds = new google.maps.LatLngBounds();
          maps[i] = daAddMap(i, the_map.center.latitude, the_map.center.longitude);
          marker_length = the_map.markers.length;
          if (marker_length == 1){
            show_marker = true
          }
          else{
            show_marker = false
          }
          for (var j = 0; j < marker_length; j++){
            var new_marker = daAddMarker(maps[i], the_map.markers[j], show_marker);
            bounds.extend(new_marker.getPosition());
          }
          if (marker_length > 1){
            maps[i].map.fitBounds(bounds);
          }
        }
      }
    </script>"""
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    interview_status.extra_scripts = list()
    interview_status.extra_css = list()
    validation_rules = {'rules': {}, 'messages': {}, 'errorClass': 'help-inline'}
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    # if 'reload_after' in interview_status.extras:
    #     reload_after = '\n    <meta http-equiv="refresh" content="' + str(interview_status.extras['reload_after']) + '">'
    # else:
    #     reload_after = ''
    browser_title = interview_status.question.interview.get_title().get('full', default_title)
    if not is_ajax:
        standard_header_start = standard_html_start(interview_language=interview_language, debug=debug_mode)
    if interview_status.question.question_type == "signature":
        interview_status.extra_scripts.append('<script>$( document ).ready(function() {daInitializeSignature();});</script>')
        bodyclass="dasignature"
    else:
        bodyclass="dabody"
        # if not is_ajax:
        #     start_output = standard_header_start + '\n    <title>' + browser_title + '</title>\n  </head>\n  <body class="dasignature">\n'
        # output = make_navbar(interview_status, default_title, default_short_title, (steps - user_dict['_internal']['steps_offset']), SHOW_LOGIN, user_dict['_internal']['livehelp'], debug_mode)
        # output += signature_html(interview_status, debug_mode, url_for('index', i=yaml_filename), validation_rules)
        # if not is_ajax:
        #     end_output = scripts + "\n    " + "\n    ".join(interview_status.extra_scripts) + """\n  </body>\n</html>"""
    if debug_mode:
        interview_status.screen_reader_text = dict()
    if 'speak_text' in interview_status.extras and interview_status.extras['speak_text']:
        interview_status.initialize_screen_reader()
        util_language = docassemble.base.functions.get_language()
        util_dialect = docassemble.base.functions.get_dialect()
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
            logmessage("index: unable to determine dialect; reverting to default")
            the_language = DEFAULT_LANGUAGE
            the_dialect = DEFAULT_DIALECT
        for question_type in ['question', 'help']:
            for audio_format in ['mp3', 'ogg']:
                interview_status.screen_reader_links[question_type].append([url_for('speak_file', question=interview_status.question.number, digest='XXXTHEXXX' + question_type + 'XXXHASHXXX', type=question_type, format=audio_format, language=the_language, dialect=the_dialect), audio_mimetype_table[audio_format]])
    # else:
    #     logmessage("speak_text was not here")
    # if interview_status.question.question_type == "signature":
    #     content = signature_html(interview_status, debug_mode, url_for('index', i=yaml_filename), validation_rules)
    # else:
    content = as_html(interview_status, url_for, debug_mode, url_for('index', i=yaml_filename), validation_rules)
    #sms_content = as_sms(interview_status)
    if debug_mode:
        readability = dict()
        for question_type in ['question', 'help']:
            if question_type not in interview_status.screen_reader_text:
                continue
            phrase = to_text(interview_status.screen_reader_text[question_type]).encode('utf8')
            if not phrase:
                phrase = "The sky is blue."
            readability[question_type] = [('Flesch Reading Ease', textstat.flesch_reading_ease(phrase)),
                                          ('Flesch-Kincaid Grade Level', textstat.flesch_kincaid_grade(phrase)),
                                          ('Gunning FOG Scale', textstat.gunning_fog(phrase)),
                                          ('SMOG Index', textstat.smog_index(phrase)),
                                          ('Automated Readability Index', textstat.automated_readability_index(phrase)),
                                          ('Coleman-Liau Index', textstat.coleman_liau_index(phrase)),
                                          ('Linsear Write Formula', textstat.linsear_write_formula(phrase)),
                                          ('Dale-Chall Readability Score', textstat.dale_chall_readability_score(phrase)),
                                          ('Readability Consensus', textstat.text_standard(phrase))]
        readability_report = ''
        for question_type in ['question', 'help']:
            if question_type in readability:
                readability_report += '          <table style="display: none;" class="table" id="readability-' + question_type +'">' + "\n"
                readability_report += '            <tr><th>Formula</th><th>Score</th></tr>' + "\n"
                for read_type, value in readability[question_type]:
                    readability_report += '            <tr><td>' + read_type +'</td><td>' + str(value) + "</td></tr>\n"
                readability_report += '          </table>' + "\n"
    if interview_status.using_screen_reader:
        for question_type in ['question', 'help']:
            #phrase = codecs.encode(to_text(interview_status.screen_reader_text[question_type]).encode('utf8'), 'base64').decode().replace('\n', '')
            if question_type not in interview_status.screen_reader_text:
                continue
            phrase = to_text(interview_status.screen_reader_text[question_type]).encode('utf8')
            #logmessage("Phrase is " + repr(phrase))
            if encrypted:
                the_phrase = encrypt_phrase(phrase, secret)
            else:
                the_phrase = pack_phrase(phrase)
            the_hash = MD5Hash(data=phrase).hexdigest()
            content = re.sub(r'XXXTHEXXX' + question_type + 'XXXHASHXXX', the_hash, content)
            existing_entry = SpeakList.query.filter_by(filename=yaml_filename, key=user_code, question=interview_status.question.number, digest=the_hash, type=question_type, language=the_language, dialect=the_dialect).first()
            if existing_entry:
                if existing_entry.encrypted:
                    existing_phrase = decrypt_phrase(existing_entry.phrase, secret)
                else:
                    existing_phrase = unpack_phrase(existing_entry.phrase)
                if phrase != existing_phrase:
                    logmessage("index: the phrase changed; updating it")
                    existing_entry.phrase = the_phrase
                    existing_entry.upload = None
                    existing_entry.encrypted = encrypted
                    db.session.commit()
            else:
                new_entry = SpeakList(filename=yaml_filename, key=user_code, phrase=the_phrase, question=interview_status.question.number, digest=the_hash, type=question_type, language=the_language, dialect=the_dialect, encrypted=encrypted)
                db.session.add(new_entry)
                db.session.commit()
    # output = '<!DOCTYPE html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet">\n    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css" rel="stylesheet">\n    <link href="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />\n    <link href="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/app.css') + '" rel="stylesheet">'
    if not is_ajax:
        start_output = standard_header_start
        if 'css' in interview_status.question.interview.external_files:
            for fileref in interview_status.question.interview.external_files['css']:
                start_output += '\n    <link href="' + get_url_from_file_reference(fileref, question=interview_status.question) + '" rel="stylesheet">'
        start_output += '\n' + indent_by("".join(interview_status.extra_css).strip(), 4).rstrip()
        start_output += '\n    <title>' + browser_title + '</title>\n  </head>\n  <body class="' + bodyclass + '">\n'
    output = make_navbar(interview_status, default_title, default_short_title, (steps - user_dict['_internal']['steps_offset']), SHOW_LOGIN, user_dict['_internal']['livehelp'], debug_mode) + flash_content + '    <div class="container">' + "\n      " + '<div class="row">\n        <div class="tab-content">\n'
    if interview_status.question.interview.use_progress_bar:
        output += progress_bar(user_dict['_internal']['progress'])
    output += content + "        </div>"
    if debug_mode:
        output += '\n        <div class="col-md-4" style="display: none" id="readability">' + readability_report + '</div>'
    output += "\n      </div>\n"
    if debug_mode:
        output += '      <div class="row">' + "\n"
        output += '        <div id="source" class="col-md-12 collapse">' + "\n"
        #output += '          <h3>' + word('SMS version') + '</h3>' + "\n"
        #output += '            <pre style="white-space: pre-wrap;">' + sms_content + '</pre>\n'
        if interview_status.using_screen_reader:
            output += '          <h3>' + word('Plain text of sections') + '</h3>' + "\n"
            for question_type in ['question', 'help']:
                if question_type in interview_status.screen_reader_text:
                    output += '<pre style="white-space: pre-wrap;">' + to_text(interview_status.screen_reader_text[question_type]) + '</pre>\n'
        output += '          <h3>' + word('Source code for question') + '</h3>' + "\n"
        if interview_status.question.source_code is None:
            output += word('unavailable')
        else:
            output += highlight(interview_status.question.source_code, YamlLexer(), HtmlFormatter())
        # if len(interview_status.question.fields_used):
        #     output += "<p>Variables set: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.fields_used)]) + "</p>"
        # if len(interview_status.question.names_used):
        #     output += "<p>Variables in code: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.names_used)]) + "</p>"
        # if len(interview_status.question.mako_names):
        #     output += "<p>Variables in templates: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.mako_names)]) + "</p>"
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
                    # if len(stage['question'].fields_used):
                    #     output += "<p>Variables set: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].fields_used)]) + "</p>"
                    # if len(stage['question'].names_used):
                    #     output += "<p>Variables in code: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].names_used)]) + "</p>"
                    # if len(stage['question'].mako_names):
                    #     output += "<p>Variables in templates: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(stage['question'].mako_names)]) + "</p>"
                elif 'variable' in stage:
                    output += "          <h5>" + word('Needed definition of') + " <code>" + str(stage['variable']) + "</code></h5>\n"
#                output += '          <h4>' + word('Variables defined') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(docassemble.base.functions.pickleable_objects(user_dict))]) + '</p>' + "\n"
            output += '          <h4>' + word('Variables defined') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(user_dict)]) + '</p>' + "\n"
            # output += '          <h4>' + word('Variables as JSON') + '</h4>' + "\n        <pre>" + docassemble.base.functions.dict_as_json(user_dict) + '</pre>' + "\n"
        output += '        </div>' + "\n"
        output += '      </div>' + "\n"
    output += '    </div>'
    if not is_ajax:
        end_output = scripts + "\n" + "".join(interview_status.extra_scripts) + """\n  </body>\n</html>"""
    #logmessage(output.encode('utf8'))
    #logmessage("Request time interim: " + str(g.request_time()))
    if 'uid' in session and 'i' in session:
        key = 'da:html:uid:' + str(session['uid']) + ':i:' + str(session['i']) + ':userid:' + str(the_user_id)
        #logmessage("Setting html key " + key)
        pipe = r.pipeline()
        pipe.set(key, json.dumps(dict(body=output, extra_scripts=interview_status.extra_scripts, extra_css=interview_status.extra_css, browser_title=browser_title, lang=interview_language, bodyclass=bodyclass)))
        pipe.expire(key, 60)
        pipe.execute()
        #sys.stderr.write("10\n")
        #logmessage("Done setting html key " + key)
        #if session.get('chatstatus', 'off') in ['waiting', 'standby', 'ringing', 'ready', 'on']:
        if user_dict['_internal']['livehelp']['availability'] != 'unavailable':
            inputkey = 'da:input:uid:' + str(session['uid']) + ':i:' + str(session['i']) + ':userid:' + str(the_user_id)
            r.publish(inputkey, json.dumps(dict(message='newpage', key=key)))
    if is_ajax:
        if interview_status.question.checkin is not None:
            do_action = interview_status.question.checkin
        else:
            do_action = None
        response = jsonify(action='body', body=output, extra_scripts=interview_status.extra_scripts, extra_css=interview_status.extra_css, browser_title=browser_title, lang=interview_language, bodyclass=bodyclass, reload_after=reload_after, livehelp=user_dict['_internal']['livehelp'], csrf_token=generate_csrf(), do_action=do_action, steps=steps, allow_going_back=allow_going_back)
    else:
        output = start_output + output + end_output
        response = make_response(output.encode('utf8'), '200 OK')
        response.headers['Content-type'] = 'text/html; charset=utf-8'
    if set_cookie:
        response.set_cookie('secret', secret)
    if expire_visitor_secret:
        response.set_cookie('visitor_secret', '', expires=0)
    release_lock(user_code, yaml_filename)
    #logmessage("Request time final: " + str(g.request_time()))
    #sys.stderr.write("11\n")
    return response

@app.template_filter('word')
def word_filter(text):
    return docassemble.base.functions.word(unicode(text))

@app.context_processor
def utility_processor():
    def user_designator(the_user):
        if the_user.email:
            return the_user.email
        else:
            return re.sub(r'.*\$', '', the_user.social_id)
    def word(text):
        return docassemble.base.functions.word(text)
    def random_social():
        return 'local$' + random_alphanumeric(32)
    if 'language' in session:
        docassemble.base.functions.set_language(session['language'])
    def in_debug():
        return DEBUG
    return dict(random_social=random_social, word=word, in_debug=in_debug, user_designator=user_designator)

@app.route('/speakfile', methods=['GET'])
def speak_file():
    audio_file = None
    filename = session.get('i', None)
    key = session.get('uid', None)
    encrypted = session.get('encrypted', False)
    question = request.args.get('question', None)
    question_type = request.args.get('type', None)
    file_format = request.args.get('format', None)
    the_language = request.args.get('language', None)
    the_dialect = request.args.get('dialect', None)
    the_hash = request.args.get('digest', None)
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if file_format not in ['mp3', 'ogg'] or not (filename and key and question and question_type and file_format and the_language and the_dialect):
        logmessage("speak_file: could not serve speak file because invalid or missing data was provided: filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    entry = SpeakList.query.filter_by(filename=filename, key=key, question=question, digest=the_hash, type=question_type, language=the_language, dialect=the_dialect).first()
    if not entry:
        logmessage("speak_file: could not serve speak file because no entry could be found in speaklist for filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    if not entry.upload:
        existing_entry = SpeakList.query.filter(and_(SpeakList.phrase == entry.phrase, SpeakList.language == entry.language, SpeakList.dialect == entry.dialect, SpeakList.upload != None, SpeakList.encrypted == entry.encrypted)).first()
        if existing_entry:
            logmessage("speak_file: found existing entry: " + str(existing_entry.id) + ".  Setting to " + str(existing_entry.upload))
            entry.upload = existing_entry.upload
            db.session.commit()
        else:
            if not VOICERSS_ENABLED:
                logmessage("speak_file: could not serve speak file because voicerss not enabled")
                abort(404)
            new_file_number = get_new_file_number(key, 'speak.mp3', yaml_file_name=filename)
            #phrase = codecs.decode(entry.phrase, 'base64')
            if entry.encrypted:
                phrase = decrypt_phrase(entry.phrase, secret)
            else:
                phrase = unpack_phrase(entry.phrase)
            url = voicerss_config.get('url', "https://api.voicerss.org/")
            #logmessage("Retrieving " + url)
            audio_file = SavedFile(new_file_number, extension='mp3', fix=True)
            audio_file.fetch_url_post(url, dict(f=voicerss_config.get('format', '16khz_16bit_stereo'), key=voicerss_config['key'], src=phrase, hl=str(entry.language) + '-' + str(entry.dialect)))
            if audio_file.size_in_bytes() > 100:
                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', audio_file.path + '.mp3']
                logmessage("speak_file: calling " + " ".join(call_array))
                result = call(call_array)
                if result != 0:
                    logmessage("speak_file: failed to convert downloaded mp3 (" + audio_file.path + '.mp3' + ") to ogg")
                    abort(404)
                entry.upload = new_file_number
                audio_file.finalize()
                db.session.commit()
            else:
                logmessage("speak_file: download from voicerss (" + url + ") failed")
                abort(404)
    if not entry.upload:
        logmessage("speak_file: upload file number was not set")
        abort(404)
    if not audio_file:
        audio_file = SavedFile(entry.upload, extension='mp3', fix=True)
    the_path = audio_file.path + '.' + file_format
    if not os.path.isfile(the_path):
        logmessage("speak_file: could not serve speak file because file (" + the_path + ") not found")
        abort(404)
    response = send_file(the_path, mimetype=audio_mimetype_table[file_format])
    return(response)

@app.route('/list', methods=['GET'])
def interview_start():
    interview_info = list()
    if len(daconfig['dispatch']) == 0:
        return redirect(url_for('index', reset=1, i=final_default_yaml_filename))
    for key, yaml_filename in sorted(daconfig['dispatch'].iteritems()):
        try:
            interview = docassemble.base.interview_cache.get_interview(yaml_filename)
            if len(interview.metadata):
                metadata = interview.metadata[0]
                interview_title = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
            else:
                interview_title = word('Untitled')
        except:
            logmessage("interview_dispatch: unable to load interview file " + yaml_filename)
            continue
        interview_info.append(dict(link=url_for('index', i=yaml_filename), display=interview_title))
    return render_template('pages/start.html', version_warning=None, interview_info=interview_info, title=daconfig.get('start page title', word('Available interviews')))

@app.route('/start/<dispatch>', methods=['GET'])
def redirect_to_interview(dispatch):
    logmessage("The dispatch is " + str(dispatch))
    yaml_filename = daconfig['dispatch'].get(dispatch, None)
    if yaml_filename is None:
        abort(404)
    arguments = dict()
    for arg in request.args:
        arguments[arg] = request.args[arg]
    arguments['i'] = yaml_filename
    return redirect(url_for('index', **arguments))

@app.route('/storedfile/<uid>/<number>/<filename>.<extension>', methods=['GET'])
def serve_stored_file(uid, number, filename, extension):
    number = re.sub(r'[^0-9]', '', str(number))
    if not can_access_file_number(number, uid=uid):
        abort(404)
    file_info = get_info_from_file_number(number, privileged=True)
    if 'path' not in file_info:
        abort(404)
    else:
        response = send_file(file_info['path'], mimetype=file_info['mimetype'])
        return(response)

@app.route('/uploadedfile/<number>/<filename>.<extension>', methods=['GET'])
def serve_uploaded_file_with_filename_and_extension(number, filename, extension):
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    number = re.sub(r'[^0-9]', '', str(number))
    if cloud is not None:
        if not can_access_file_number(number):
            abort(404)
        the_file = SavedFile(number)
    else:
        file_info = get_info_from_file_number(number, privileged=privileged)
        if 'path' not in file_info:
            abort(404)
        else:
            if os.path.isfile(file_info['path'] + '.' + extension):
                extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
                response = send_file(file_info['path'] + '.' + extension, mimetype=mimetype)
                return(response)
            else:
                abort(404)

@app.route('/uploadedfile/<number>.<extension>', methods=['GET'])
def serve_uploaded_file_with_extension(number, extension):
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    number = re.sub(r'[^0-9]', '', str(number))
    if cloud is not None:
        if not can_access_file_number(number):
            abort(404)
        the_file = SavedFile(number)
    else:
        file_info = get_info_from_file_number(number, privileged=privileged)
        if 'path' not in file_info:
            abort(404)
        else:
            if os.path.isfile(file_info['path'] + '.' + extension):
                extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
                response = send_file(file_info['path'] + '.' + extension, mimetype=mimetype)
                return(response)
            else:
                abort(404)

@app.route('/uploadedfile/<number>', methods=['GET'])
def serve_uploaded_file(number):
    number = re.sub(r'[^0-9]', '', str(number))
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    file_info = get_info_from_file_number(number, privileged=privileged)
    #file_info = get_info_from_file_reference(number)
    if 'path' not in file_info:
        abort(404)
    else:
        #block_size = 4096
        #status = '200 OK'
        response = send_file(file_info['path'], mimetype=file_info['mimetype'])
        return(response)

@app.route('/uploadedpage/<number>/<page>', methods=['GET'])
def serve_uploaded_page(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    file_info = get_info_from_file_number(number, privileged=privileged)
    if 'path' not in file_info:
        abort(404)
    else:
        max_pages = 1 + int(file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        filename = file_info['path'] + 'page-' + (formatter % int(page)) + '.png'
        if os.path.isfile(filename):
            response = send_file(filename, mimetype='image/png')
            return(response)
        else:
            abort(404)

@app.route('/uploadedpagescreen/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    file_info = get_info_from_file_number(number, privileged=privileged)
    if 'path' not in file_info:
        logmessage('serve_uploaded_pagescreen: no access to file number ' + str(number))
        abort(404)
    else:
        max_pages = 1 + int(file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        filename = file_info['path'] + 'screen-' + (formatter % int(page)) + '.png'
        if os.path.isfile(filename):
            response = send_file(filename, mimetype='image/png')
            return(response)
        else:
            logmessage('serve_uploaded_pagescreen: path ' + filename + ' is not a file')
            abort(404)

@app.route('/visit_interview', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'advocate'])
def visit_interview():
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    key = 'da:session:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    try:
        obj = pickle.loads(r.get(key))
    except:
        abort(404)
    if 'secret' not in obj or 'encrypted' not in obj:
        abort(404)
    session['i'] = i
    session['uid'] = uid
    session['encrypted'] = obj['encrypted']
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    session['key_logged'] = True
    if 'tempuser' in session:
        del session['tempuser']
    response = redirect(url_for('index', reset=1, i=i))
    response.set_cookie('visitor_secret', obj['secret'])
    return response

@app.route('/observer', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'advocate'])
def observer():
    session['observer'] = 1
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    observation_script = """
    <script>
      var daSendChanges = false;
      var daNoConnectionCount = 0;
      var daConnected = false;
      var daConfirmed = false;
      var observerChangesInterval = null;
      var daInitialized = false;
      var daShowingHelp = false;
      var daInformedChanged = false;
      var dadisable = null;
      var daCsrf = """ + repr(str(generate_csrf())) + """;
      window.turnOnControl = function(){
        //console.log("Turning on control");
        daSendChanges = true;
        daNoConnectionCount = 0;
        resetPushChanges();
        socket.emit('observerStartControl', {uid: """ + repr(str(uid)) + """, i: """ + repr(str(i)) + """, userid: """ + repr(str(userid)) + """});
      }
      window.turnOffControl = function(){
        //console.log("Turning off control");
        if (!daSendChanges){
          //console.log("Already turned off");
          return;
        }
        daSendChanges = false;
        daConfirmed = false;
        stopPushChanges();
        socket.emit('observerStopControl', {uid: """ + repr(str(uid)) + """, i: """ + repr(str(i)) + """, userid: """ + repr(str(userid)) + """});
        return;
      }
      function stopPushChanges(){
        if (observerChangesInterval != null){
          clearInterval(observerChangesInterval);
        }
      }
      function resetPushChanges(){
        if (observerChangesInterval != null){
          clearInterval(observerChangesInterval);
        }
        observerChangesInterval = setInterval(pushChanges, """ + str(CHECKIN_INTERVAL) + """);
      }
      function daValidationHandler(form){
        //form.submit();
        dadisable = setTimeout(function(){
          $(form).find('input[type="submit"]').prop("disabled", true);
          $(form).find('button[type="submit"]').prop("disabled", true);
        }, 1);
        if ($('input[name="_files"]').length){
          $("#uploadiframe").remove();
          var iframe = $('<iframe name="uploadiframe" id="uploadiframe" style="display: none"></iframe>');
          $("body").append(iframe);
          $(form).attr("target", "uploadiframe");
          $('<input>').attr({
              type: 'hidden',
              name: 'ajax',
              value: '1'
          }).appendTo($(form));
          iframe.bind('load', function(){
            setTimeout(function(){
              daProcessAjax($.parseJSON($("#uploadiframe").contents().text()), form);
            }, 0);
          });
          form.submit();
        }
        else{
          if (daSubmitter != null){
            var input = $("<input>")
              .attr("type", "hidden")
              .attr("name", daSubmitter.name).val(daSubmitter.value);
            $(form).append($(input));
          }
          var informed = '';
          if (daInformedChanged){
            informed = '&informed=' + Object.keys(daInformed).join(',');
          }
          $.ajax({
            type: "POST",
            url: $(form).attr('action'),
            data: $(form).serialize() + '&ajax=1' + informed, 
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, form);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
        }
        daSpinnerTimeout = setTimeout(showSpinner, 1000);
        return(false);
      }
      function pushChanges(){
        //console.log("Pushing changes");
        if (observerChangesInterval != null){
          clearInterval(observerChangesInterval);
        }
        if (!daSendChanges || !daConnected){
          return;
        }
        observerChangesInterval = setInterval(pushChanges, """ + str(CHECKIN_INTERVAL) + """);
        socket.emit('observerChanges', {uid: """ + repr(str(uid)) + """, i: """ + repr(str(i)) + """, userid: """ + repr(str(userid)) + """, parameters: JSON.stringify($("#daform").serializeArray())});
      }
      function daProcessAjaxError(xhr, status, error){
        $("body").html(xhr.responseText);
      }
      function daSubmitter(event){
        event.preventDefault();
        if (!daSendChanges || !daConnected){
          return false;
        }
        var theId = $(this).attr('id');
        var theName = $(this).attr('name');
        var theValue = $(this).val();
        var skey;
        if (theId){
          skey = '#' + theId.replace(/(:|\.|\[|\]|,|=|\/|\")/g, '\\\\$1');
        }
        else if (theName){
          skey = '#' + $(this).parents("form").attr('id') + ' ' + $(this).prop('tagName').toLowerCase() + '[name="' + theName.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1') + '"]';
          if (typeof theValue !== 'undefined'){
            skey += '[value="' + theValue + '"]'
          }
        }
        else{
          skey = '#' + $(this).parents("form").attr('id') + ' ' + $(this).prop('tagName').toLowerCase() + '[type="submit"]';
        }
        //console.log("Need to click on " + skey);
        if (observerChangesInterval != null){
          clearInterval(observerChangesInterval);
        }
        socket.emit('observerChanges', {uid: """ + repr(str(uid)) + """, i: """ + repr(str(i)) + """, userid: """ + repr(str(userid)) + """, clicked: skey, parameters: JSON.stringify($("#daform").serializeArray())});
        return false;
      }
      function daInitialize(){
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'click focus', html: true})
        });
        $('button[type="submit"]').click(daSubmitter);
        $('input[type="submit"]').click(daSubmitter);
        $(".to-labelauty").labelauty({ width: "100%" });
        $(".to-labelauty-icon").labelauty({ label: false });
        var navMain = $("#navbar-collapse");
        navMain.on("click", "a", null, function () {
          if (!($(this).hasClass("dropdown-toggle"))){
            navMain.collapse('hide');
          }
        });
        $("#helptoggle").on("click", function(){
          //console.log("Got to helptoggle");
          window.scrollTo(0, 0);
          $(this).removeClass('daactivetext')
          return true;
        });
        $("#sourcetoggle").on("click", function(){
          $(this).toggleClass("sourceactive");
        });
        $('#backToQuestion').click(function(event){
          event.preventDefault();
          $('#questionlabel').trigger('click');
        });
        $(".showif").each(function(){
          var showIfSign = $(this).data('showif-sign');
          var showIfVar = $(this).data('showif-var');
          var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
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
        // dadisable = setTimeout(function(){
        //   $("#daform").find('button[type="submit"]').prop("disabled", true);
        //   //$("#daform").find(':input').prop("disabled", true);
        // }, 1);
        $("#daform").each(function(){
          $(this).find(':input').on('change', pushChanges);
        });
        daInitialized = true;
        daShowingHelp = 0;
      }
      $( document ).ready(function(){
        daInitialize();
        $( window ).bind('unload', function() {
          if (socket != null && socket.connected){
            socket.emit('terminate');
          }
        });
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/observer" + location.port, {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/observer" + location.port, {path: '/ws/socket.io'});
        }
        if (typeof socket !== 'undefined') {
            socket.on('connect', function() {
                //console.log("Connected!");
                socket.emit('observe', {uid: """ + repr(str(uid)) + """, i: """ + repr(str(i)) + """, userid: """ + repr(str(userid)) + """});
                daConnected = true;
            });
            socket.on('terminate', function() {
                //console.log("Terminating socket");
                socket.disconnect();
            });
            socket.on('disconnect', function() {
                //console.log("Disconnected socket");
                //socket = null;
            });
            socket.on('stopcontrolling', function(data) {
                window.parent.stopControlling(data.key);
            });
            socket.on('start_being_controlled', function(data) {
                //console.log("Got start_being_controlled");
                daConfirmed = true;
                pushChanges();
                window.parent.gotConfirmation(data.key);
            });
            socket.on('abortcontrolling', function(data) {
                //console.log("Got abortcontrolling");
                //daSendChanges = false;
                //daConfirmed = false;
                //stopPushChanges();
                window.parent.abortControlling(data.key);
            });
            socket.on('noconnection', function(data) {
                //console.log("warning: no connection");
                if (daNoConnectionCount++ > 2){
                    //console.log("error: no connection");
                    window.parent.stopControlling(data.key);
                }
            });
            socket.on('newpage', function(incoming) {
                var data = incoming.obj;
                $("body").html(data.body);
                $("body").removeClass();
                $("body").addClass(data.bodyclass);
                daInitialize();
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.extra_scripts;
                var scripts = tempDiv.getElementsByTagName('script');
                for (var i = 0; i < scripts.length; i++){
                  eval(scripts[i].innerHTML);
                }
                for (var i = 0; i < data.extra_css.length; i++){
                  $("head").append(data.extra_css[i]);
                }
                document.title = data.browser_title;
                if ($("html").attr("lang") != data.lang){
                  $("html").attr("lang", data.lang);
                }
                pushChanges();
            });
            socket.on('pushchanges', function(data) {
                var valArray = Object();
                var values = data.parameters;
                for (var i = 0; i < values.length; i++) {
                    valArray[values[i].name] = values[i].value;
                }
                $("#daform").each(function(){
                    $(this).find(':input').each(function(){
                        var type = $(this).attr('type');
                        var id = $(this).attr('id');
                        var name = $(this).attr('name');
                        if (type == 'checkbox'){
                            if (name in valArray){
                                if (valArray[name] == 'True'){
                                    $(this).prop('checked', true);
                                }
                                else{
                                    $(this).prop('checked', false);
                                }
                            }
                            else{
                                $(this).prop('checked', false);
                            }
                        }
                        else if (type == 'radio'){
                            if (name in valArray){
                                if (valArray[name] == $(this).val()){
                                    $(this).prop('checked', true);
                                }
                                else{
                                    $(this).prop('checked', false);
                                }
                            }
                        }
                        else if ($(this).data().hasOwnProperty('sliderMax')){
                            $(this).slider('setValue', parseInt(valArray[name]));
                        }
                        else{
                            if (name in valArray){
                                $(this).val(valArray[name]);
                            }
                        }
                    });
                });
            });
        }
        observerChangesInterval = setInterval(pushChanges, """ + str(CHECKIN_INTERVAL) + """);
    });
    </script>
"""
    the_key = 'da:html:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    html = r.get(the_key)
    if html is not None:
        obj = json.loads(html)
    else:
        logmessage("observer: failed to load JSON from key " + the_key)
        obj = dict()
    output = standard_html_start(interview_language=obj.get('lang', 'en'), debug=DEBUG)
    output += indent_by("".join(obj.get('extra_css', list())), 4)
    output += '\n    <title>' + word('Observation') + '</title>\n  </head>\n  <body class="' + obj.get('bodyclass', 'dabody') + '">\n'
    output += obj.get('body', '')
    output += standard_scripts() + observation_script + "\n    " + "".join(obj.get('extra_scripts', list())) + "\n  </body>\n</html>"
    response = make_response(output.encode('utf8'), '200 OK')
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    return response

@app.route('/monitor', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'advocate'])
def monitor():
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('interview_list')))
    session['monitor'] = 1
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    phone_number_key = 'da:monitor:phonenumber:' + str(session['user_id'])
    default_phone_number = r.get(phone_number_key)
    if default_phone_number is None:
        default_phone_number = ''
    sub_role_key = 'da:monitor:userrole:' + str(session['user_id'])
    if r.exists(sub_role_key):
        subscribed_roles = r.hgetall(sub_role_key)
        r.expire(sub_role_key, 2592000)
    else:
        subscribed_roles = dict()
    key = 'da:monitor:available:' + str(current_user.id)
    if r.exists(key):
        daAvailableForChat = 'true'
    else:
        daAvailableForChat = 'false'
    call_forwarding_on = 'false'
    if twilio_config is not None:
        forwarding_phone_number = twilio_config['name']['default'].get('number', None)
        if forwarding_phone_number is not None:
            call_forwarding_on = 'true'
    script = '<script type="text/javascript" src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>\n' + """<script type="text/javascript" charset="utf-8">
    var daAudioContext = null;
    var socket;
    var soundBuffer = Object();
    var daShowingNotif = false;
    var daUpdatedSessions = Object();
    var daUserid = """ + str(current_user.id) + """;
    var daPhoneOnMessage = """ + repr(str("The user can call you.  Click to cancel.")) + """;
    var daPhoneOffMessage = """ + repr(str("Click if you want the user to be able to call you.")) + """;
    var daSessions = Object();
    var daAvailRoles = Object();
    var daChatPartners = Object();
    var daPhonePartners = Object();
    var daNewPhonePartners = Object();
    var daTermPhonePartners = Object();
    var daUsePhone = """ + call_forwarding_on + """;
    var daSubscribedRoles = """ + json.dumps(subscribed_roles) + """;
    var daAvailableForChat = """ + daAvailableForChat + """;
    var daPhoneNumber = """ + repr(str(default_phone_number)) + """;
    var daFirstTime = 1;
    var updateMonitorInterval = null;
    var daNotificationsEnabled = false;
    var daControlling = Object();
    var daBrowserTitle = """ + repr(str(word('Monitor'))) + """;
    window.gotConfirmation = function(key){
        //console.log("Got confirmation in parent for key " + key);
        // daControlling[key] = 2;
        // var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        // $("#listelement" + skey).find("a").each(function(){
        //     if ($(this).data('name') == "stopControlling"){
        //         $(this).removeClass('invisible');
        //         console.log("Found it");
        //     }
        // });
    }
    function faviconRegular(){
      var link = document.querySelector("link[rel*='shortcut icon'") || document.createElement('link');
      link.type = 'image/x-icon';
      link.rel = 'shortcut icon';
      link.href = '""" + url_for('favicon', nocache="1") + """';
      document.getElementsByTagName('head')[0].appendChild(link);
    }
    function faviconAlert(){
      var link = document.querySelector("link[rel*='shortcut icon'") || document.createElement('link');
      link.type = 'image/x-icon';
      link.rel = 'shortcut icon';
      link.href = '""" + url_for('static', filename='app/chat.ico') + """?nocache=1';
      document.getElementsByTagName('head')[0].appendChild(link);
    }
    function topMessage(message){
        var newDiv = document.createElement('div');
        $(newDiv).addClass("top-alert col-xs-10 col-sm-7 col-md-6 col-lg-5 col-centered");
        $(newDiv).html(message)
        $(newDiv).css("display", "none");
        $(newDiv).appendTo($("body"));
        $(newDiv).slideDown();
        setTimeout(function(){
          $(newDiv).slideUp(300, function(){
            $(newDiv).remove();
          });
        }, 2000);
    }
    window.abortControlling = function(key){
        topMessage(""" + repr(str(word("That screen is already being controlled by another operator"))) + """);
        stopControlling(key);
    }
    window.stopControlling = function(key){
        //console.log("Got stopControlling in parent for key " + key);
        // if (daControlling.hasOwnProperty(key)){
        //   delete daControlling[key];
        // }
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        $("#listelement" + skey).find("a").each(function(){
            if ($(this).data('name') == "stopControlling"){
                $(this).click();
                //console.log("Found it");
            }
        });
    }
    function daOnError(){
        console.log('daOnError');
    }
    function loadSoundBuffer(key, url_a, url_b){
        //console.log("loadSoundBuffer");
        var pos = 0;
        if (daAudioContext == null){
            return;
        }
        var request = new XMLHttpRequest();
        request.open('GET', url_a, true);
        request.responseType = 'arraybuffer';
        request.onload = function(){
            daAudioContext.decodeAudioData(request.response, function(buffer){
                if (!buffer){
                    if (pos == 1){
                        console.error('loadSoundBuffer: error decoding file data');
                        return;
                    }
                    else {
                        pos = 1;
                        console.info('loadSoundBuffer: error decoding file data, trying next source');
                        request.open("GET", url_b, true);
                        return request.send();
                    }
                }
                soundBuffer[key] = buffer;
            },
            function(error){
                if (pos == 1){
                    console.error('loadSoundBuffer: decodeAudioData error');
                    return;
                }
                else{
                    pos = 1;
                    console.info('loadSoundBuffer: decodeAudioData error, trying next source');
                    request.open("GET", url_b, true);
                    return request.send();
                }
            });
        }
        request.send();
    }
    function playSound(key) {
        //console.log("playSound");
        var buffer = soundBuffer[key];
        if (!daAudioContext || !buffer){
            return;
        }
        var source = daAudioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(daAudioContext.destination);
        source.start(0);
    }
    function checkNotifications(){
        //console.log("checkNotifications");
        if (daNotificationsEnabled){
            return;
        }
        if (!("Notification" in window)) {
            daNotificationsEnabled = false;
            return;
        }
        if (Notification.permission === "granted") {
            daNotificationsEnabled = true;
            return;
        }
        if (Notification.permission !== 'denied') {
            Notification.requestPermission(function (permission) {
                if (permission === "granted") {
                    daNotificationsEnabled = true;
                }
            });
        }
    }
    function notifyOperator(key, mode, message) {
        //console.log("notifyOperator: " + key + " " + mode + " " + message);
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        if (mode == "chat"){
          playSound('newmessage');
        }
        else{
          playSound('newconversation');
        }
        if ($("#listelement" + skey).offset().top > $(window).scrollTop() + $(window).height()){
          if (mode == "chat"){
            $("#chat-message-below").html(""" + repr(str(word("New message below"))) + """);
          }
          else{
            $("#chat-message-below").html(""" + repr(str(word("New conversation below"))) + """);
          }
          //$("#chat-message-below").data('key', key);
          $("#chat-message-below").slideDown();
          daShowingNotif = true;
          markAsUpdated(key);
        }
        else if ($("#listelement" + skey).offset().top + $("#listelement" + skey).height() < $(window).scrollTop() + 32){
          if (mode == "chat"){
            $("#chat-message-above").html(""" + repr(str(word("New message above"))) + """);
          }
          else{
            $("#chat-message-above").html(""" + repr(str(word("New conversation above"))) + """);
          }
          //$("#chat-message-above").data('key', key);
          $("#chat-message-above").slideDown();
          daShowingNotif = true;
          markAsUpdated(key);
        }
        else{
          //console.log("It is visible");
        }
        if (!daNotificationsEnabled){
            //console.log("Browser will not enable notifications")
            return;
        }
        if (!("Notification" in window)) {
            return;
        }
        if (Notification.permission === "granted") {
            var notification = new Notification(message);
        }
        else if (Notification.permission !== 'denied') {
            Notification.requestPermission(function (permission) {
                if (permission === "granted") {
                    var notification = new Notification(message);
                    daNotificationsEnabled = true;
                }
            });
        }
    }
    function phoneNumberOk(){
        //console.log("phoneNumberOk");
        var phoneNumber = $("#daPhoneNumber").val();
        if (phoneNumber == '' || phoneNumber.match(/^\+?[1-9]\d{1,14}$/)){
            return true;
        }
        else{
            return false;
        }
    }
    function checkPhone(){
        //console.log("checkPhone");
        $("#daPhoneNumber").val($("#daPhoneNumber").val().replace(/[^0-9\+]/g, ''));
        var the_number = $("#daPhoneNumber").val();
        if (the_number[0] != '+'){
            $("#daPhoneNumber").val('+' + the_number);
        }
        if (phoneNumberOk()){
            $("#daPhoneNumber").parent().removeClass("has-error");
            $("#daPhoneError").addClass("invisible");
            daPhoneNumber = $("#daPhoneNumber").val();
            if (daPhoneNumber == ''){
                daPhoneNumber = null;
            }
            else{
                $(".phone").removeClass("invisible");
            }
        }
        else{
            $("#daPhoneNumber").parent().addClass("has-error");
            $("#daPhoneError").removeClass("invisible");
            daPhoneNumber = null;
            $(".phone").addClass("invisible");
        }
        $("#daPhoneSaved").removeClass("invisible");
        setTimeout(function(){
            $("#daPhoneSaved").addClass("invisible");
        }, 2000);
    }
    function allSessions(uid, yaml_filename){
        //console.log("allSessions");
        var prefix = 'da:session:uid:' + uid + ':i:' + yaml_filename + ':userid:';
        var output = Array();
        for (var key in daSessions){
            if (daSessions.hasOwnProperty(key) && key.indexOf(prefix) == 0){
                output.push(key);
            }
        }
        return(output);
    }
    function scrollChat(key){
        var chatScroller = $(key).find('ul').first();
        if (chatScroller.length){
            var height = chatScroller[0].scrollHeight;
            chatScroller.animate({scrollTop: height}, 800);
        }
        else{
            console.log("scrollChat: error")
        }
    }
    function scrollChatFast(key){
        var chatScroller = $(key).find('ul').first();
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
            //console.log("Scrolling to " + height + " where there are " + chatScroller[0].childElementCount + " children");
            chatScroller.scrollTop(height);
          }
        else{
            console.log("scrollChatFast: error")
        }
    }
    function do_update_monitor(){
        //console.log("do_update_monitor with " + daAvailableForChat);
        if (phoneNumberOk()){
          daPhoneNumber = $("#daPhoneNumber").val();
          if (daPhoneNumber == ''){
            daPhoneNumber = null;
          }
        }
        else{
          daPhoneNumber = null;
        }
        socket.emit('updatemonitor', {available_for_chat: daAvailableForChat, phone_number: daPhoneNumber, subscribed_roles: daSubscribedRoles, phone_partners_to_add: daNewPhonePartners, phone_partners_to_terminate: daTermPhonePartners});
    }
    function update_monitor(){
        //console.log("update_monitor with " + daAvailableForChat);
        if (updateMonitorInterval != null){
            clearInterval(updateMonitorInterval);
        }
        do_update_monitor();
        updateMonitorInterval = setInterval(do_update_monitor, """ + str(CHECKIN_INTERVAL) + """);
        //console.log("update_monitor");
    }
    function isHidden(ref){
        if ($(ref).length){
            if (($(ref).offset().top + $(ref).height() < $(window).scrollTop() + 32)){
                return -1;
            }
            else if ($(ref).offset().top > $(window).scrollTop() + $(window).height()){
                return 1;
            }
            else{
                return 0;
            }
        }
        else{
            return 0;
        }
    }
    function markAsUpdated(key){
        //console.log("markAsUpdated with " + key);
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        if (isHidden("#listelement" + skey)){
            daUpdatedSessions["#listelement" + skey] = 1;
        }
    }
    function activateChatArea(key){
        //console.log("activateChatArea with " + key);
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        if (!$("#chatarea" + skey).find('input').first().is(':focus')){
          $("#listelement" + skey).addClass("new-message");
          if (daBrowserTitle == document.title){
            document.title = '* ' + daBrowserTitle;
            faviconAlert();
          }
        }
        markAsUpdated(key);
        $("#chatarea" + skey).removeClass('invisible');
        $("#chatarea" + skey).find('input, button').prop("disabled", false);
        $("#chatarea" + skey).find('ul').html('');
        socket.emit('chat_log', {key: key});
    }
    function deActivateChatArea(key){
        //console.log("daActivateChatArea with " + key);
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        $("#chatarea" + skey).find('input, button').prop("disabled", true);
        $("#listelement" + skey).removeClass("new-message");
        if (document.title != daBrowserTitle){
            document.title = daBrowserTitle;
            faviconRegular();
        }
    }
    function undraw_session(key){
        //console.log("Undrawing...");
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        var xButton = document.createElement('a');
        var xButtonIcon = document.createElement('i');
        $(xButton).addClass("corner-remove");
        $(xButtonIcon).addClass("glyphicon glyphicon-remove-circle");
        $(xButtonIcon).appendTo($(xButton));
        $("#listelement" + skey).addClass("list-group-item-danger");
        $("#session" + skey).find("a").remove();
        $("#session" + skey).find("span").first().html('""" + word("offline") + """');
        $("#session" + skey).find("span").first().removeClass('label-info');
        $("#session" + skey).find("span").first().addClass('label-danger');
        $(xButton).click(function(){
            $("#listelement" + skey).slideUp(300, function(){
                $("#listelement" + skey).remove();
                check_if_empty();
            });
        });
        $(xButton).appendTo($("#session" + skey));
        $("#chatarea" + skey).find('input, button').prop("disabled", true);
        var theIframe = $("#iframe" + skey).find('iframe')[0];
        if (theIframe){
            $(theIframe).contents().find('body').addClass("dainactive");
            if (theIframe.contentWindow && theIframe.contentWindow.turnOffControl){
                theIframe.contentWindow.turnOffControl();
            }
        }
        if (daControlling.hasOwnProperty(key)){
            delete daControlling[key];
        }
        delete daSessions[key];
    }
    function publish_chat_log(uid, yaml_filename, userid, mode, messages){
        //console.log("publish_chat_log with " + uid + " " + yaml_filename + " " + userid + " " + mode + " " + messages);
        var keys; 
        //if (mode == 'peer' || mode == 'peerhelp'){
        //    keys = allSessions(uid, yaml_filename);
        //}
        //else{
            keys = ['da:session:uid:' + uid + ':i:' + yaml_filename + ':userid:' + userid];
        //}
        for (var i = 0; i < keys.length; ++i){
            key = keys[i];
            var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
            var chatArea = $("#chatarea" + skey).find('ul').first();
            for (var i = 0; i < messages.length; ++i){
                var message = messages[i];
                var newLi = document.createElement('li');
                $(newLi).addClass("list-group-item");
                if (message.is_self){
                    $(newLi).addClass("list-group-item-warning dalistright");
                }
                else{
                    $(newLi).addClass("list-group-item-info");
                }
                $(newLi).html(message.message);
                $(newLi).appendTo(chatArea);
            }
            scrollChatFast("#chatarea" + skey);
        }
    }
    function check_if_empty(){
        if ($("#monitorsessions").find("li").length > 0){
            $("#emptylist").addClass("invisible");
        }
        else{
            $("#emptylist").removeClass("invisible");
        }
    }
    function draw_session(key, obj){
        //console.log("draw_session with " + key);
        var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
        var the_html;
        var wants_to_chat;
        if (obj.chatstatus != 'off'){ //obj.chatstatus == 'waiting' || obj.chatstatus == 'standby' || obj.chatstatus == 'ringing' || obj.chatstatus == 'ready' || obj.chatstatus == 'on' || obj.chatstatus == 'observeonly'
            wants_to_chat = true;
        }
        if (wants_to_chat){
            the_html = obj.browser_title + ' &mdash; '
            if (obj.hasOwnProperty('first_name')){
              the_html += obj.first_name + ' ' + obj.last_name;
            }
            else{
              the_html += '""" + word("anonymous visitor") + """ ' + obj.temp_user_id;
            }
        }
        var theListElement;
        var sessionDiv;
        var theIframeContainer;
        var theChatArea;
        if ($("#session" + skey).length && !(key in daSessions)){
            $("#listelement" + skey).removeClass("list-group-item-danger");
            $("#iframe" + skey).find('iframe').first().contents().find('body').removeClass("dainactive");
        }
        daSessions[key] = 1;
        if ($("#session" + skey).length){
            theListElement = $("#listelement" + skey).first();
            sessionDiv = $("#session" + skey).first();
            //controlDiv = $("#control" + skey).first();
            theIframeContainer = $("#iframe" + skey).first();
            theChatArea = $("#chatarea" + skey).first();
            $(sessionDiv).empty();
            if (obj.chatstatus == 'on' && key in daChatPartners && $("#chatarea" + skey).find('button').first().prop("disabled") == true){
                activateChatArea(key);
            }
        }
        else{
            var theListElement = document.createElement('li');
            $(theListElement).addClass('list-group-item');
            $(theListElement).attr('id', "listelement" + key);
            var sessionDiv = document.createElement('div');
            $(sessionDiv).attr('id', "session" + key);
            $(sessionDiv).addClass('chat-session');
            $(sessionDiv).appendTo($(theListElement));
            $(theListElement).appendTo("#monitorsessions");
            // controlDiv = document.createElement('div');
            // $(controlDiv).attr('id', "control" + key);
            // $(controlDiv).addClass("chatcontrol invisible chat-session");
            // $(controlDiv).appendTo($(theListElement));
            theIframeContainer = document.createElement('div');
            $(theIframeContainer).addClass("observer-container invisible");
            $(theIframeContainer).attr('id', 'iframe' + key);
            var theIframe = document.createElement('iframe');
            $(theIframe).addClass("observer");
            $(theIframe).attr('name', 'iframe' + key);
            $(theIframe).appendTo($(theIframeContainer));
            $(theIframeContainer).appendTo($(theListElement));
            var theChatArea = document.createElement('div');
            $(theChatArea).addClass('monitor-chat-area invisible');
            $(theChatArea).html('<div class="row"><div class="col-md-12"><ul class="list-group dachatbox" id="daCorrespondence"></ul></div></div><form autocomplete="off"><div class="row"><div class="col-md-12"><div class="input-group"><input type="text" class="form-control" disabled><span class="input-group-btn"><button class="btn btn-default" type="button" disabled>""" + word("Send") + """</button></span></div></div></div></form>');
            $(theChatArea).attr('id', 'chatarea' + key);
            var submitter = function(){
                //console.log("I am the submitter and I am submitting " + key);
                var input = $(theChatArea).find("input").first();
                var message = input.val().trim();
                if (message == null || message == ""){
                    //console.log("Message was blank");
                    return false;
                }
                socket.emit('chatmessage', {key: key, data: input.val()});
                input.val('');
                return false;
            };
            $(theChatArea).find("button").click(submitter);
            $(theChatArea).find("input").bind('keypress keydown keyup', function(e){
                if(e.keyCode == 13) { submitter(); e.preventDefault(); }
            });
            $(theChatArea).find("input").focus(function(){
                $(theListElement).removeClass("new-message");
                if (document.title != daBrowserTitle){
                    document.title = daBrowserTitle;
                    faviconRegular();
                }
            });
            $(theChatArea).appendTo($(theListElement));
            if (obj.chatstatus == 'on' && key in daChatPartners){
                activateChatArea(key);
            }
        }
        var theText = document.createElement('span');
        $(theText).addClass('chat-title-label');
        theText.innerHTML = the_html;
        var statusLabel = document.createElement('span');
        $(statusLabel).addClass("label label-info chat-status-label");
        $(statusLabel).html(obj.chatstatus == 'observeonly' ? 'off' : obj.chatstatus);
        $(statusLabel).appendTo($(sessionDiv));
        if (daUsePhone){
          var phoneButton = document.createElement('a');
          var phoneIcon = document.createElement('i');
          $(phoneIcon).addClass("glyphicon glyphicon-earphone");
          $(phoneIcon).appendTo($(phoneButton));
          $(phoneButton).addClass("label phone");
          $(phoneButton).data('name', 'phone');
          if (key in daPhonePartners){
            $(phoneButton).addClass("phone-on label-success");
            $(phoneButton).attr('title', daPhoneOnMessage);
          }
          else{
            $(phoneButton).addClass("phone-off label-default");
            $(phoneButton).attr('title', daPhoneOffMessage);
          }
          $(phoneButton).addClass('observebutton')
          $(phoneButton).appendTo($(sessionDiv));
          $(phoneButton).attr('href', '#');
          if (daPhoneNumber == null){
            $(phoneButton).addClass("invisible");
          }
          $(phoneButton).click(function(e){
            if ($(this).hasClass("phone-off") && daPhoneNumber != null){
              $(this).removeClass("phone-off");
              $(this).removeClass("label-default");
              $(this).addClass("phone-on");
              $(this).addClass("label-success");
              $(this).attr('title', daPhoneOnMessage);
              daPhonePartners[key] = 1;
              daNewPhonePartners[key] = 1;
              if (key in daTermPhonePartners){
                delete daTermPhonePartners[key];
              }
              update_monitor();
            }
            else{
              $(this).removeClass("phone-on");
              $(this).removeClass("label-success");
              $(this).addClass("phone-off");
              $(this).addClass("label-default");
              $(this).attr('title', daPhoneOffMessage);
              if (key in daPhonePartners){
                delete daPhonePartners[key];
              }
              if (key in daNewPhonePartners){
                delete daNewPhonePartners[key];
              }
              daTermPhonePartners[key] = 1;
              update_monitor();
            }
            e.preventDefault();
            return false;
          });
        }
        var unblockButton = document.createElement('a');
        $(unblockButton).addClass("label label-info observebutton");
        $(unblockButton).data('name', 'unblock');
        if (!obj.blocked){
            $(unblockButton).addClass("invisible");
        }
        $(unblockButton).html('""" + word("Unblock") + """');
        $(unblockButton).attr('href', '#');
        $(unblockButton).appendTo($(sessionDiv));
        var blockButton = document.createElement('a');
        $(blockButton).addClass("label label-danger observebutton");
        if (obj.blocked){
            $(blockButton).addClass("invisible");
        }
        $(blockButton).html('""" + word("Block") + """');
        $(blockButton).attr('href', '#');
        $(blockButton).data('name', 'block');
        $(blockButton).appendTo($(sessionDiv));
        $(blockButton).click(function(e){
            $(unblockButton).removeClass("invisible");
            $(this).addClass("invisible");
            deActivateChatArea(key);
            socket.emit('block', {key: key});
            e.preventDefault();
            return false;
        });
        $(unblockButton).click(function(e){
            $(blockButton).removeClass("invisible");
            $(this).addClass("invisible");
            socket.emit('unblock', {key: key});
            e.preventDefault();
            return false;
        });
        var joinButton = document.createElement('a');
        $(joinButton).addClass("label label-warning observebutton");
        $(joinButton).html('""" + word("Join") + """');
        $(joinButton).attr('href', '""" + url_for('visit_interview') + """?' + $.param({i: obj.i, uid: obj.uid, userid: obj.userid}));
        $(joinButton).data('name', 'join');
        $(joinButton).attr('target', '_blank');
        $(joinButton).appendTo($(sessionDiv));
        if (wants_to_chat){
            var openButton = document.createElement('a');
            $(openButton).addClass("label label-primary observebutton");
            $(openButton).attr('href', '""" + url_for('observer') + """?' + $.param({i: obj.i, uid: obj.uid, userid: obj.userid}));
            //$(openButton).attr('href', 'about:blank');
            $(openButton).attr('id', 'observe' + key);
            $(openButton).attr('target', 'iframe' + key);
            $(openButton).html('""" + word("Observe") + """');
            $(openButton).data('name', 'open');
            $(openButton).appendTo($(sessionDiv));
            var stopObservingButton = document.createElement('a');
            $(stopObservingButton).addClass("label label-default observebutton invisible");
            $(stopObservingButton).html('""" + word("Stop Observing") + """');
            $(stopObservingButton).attr('href', '#');
            $(stopObservingButton).data('name', 'stopObserving');
            $(stopObservingButton).appendTo($(sessionDiv));
            var controlButton = document.createElement('a');
            $(controlButton).addClass("label label-info observebutton");
            $(controlButton).html('""" + word("Control") + """');
            $(controlButton).attr('href', '#');
            $(controlButton).data('name', 'control');
            $(controlButton).appendTo($(sessionDiv));
            var stopControllingButton = document.createElement('a');
            $(stopControllingButton).addClass("label label-default observebutton invisible");
            $(stopControllingButton).html('""" + word("Stop Controlling") + """');
            $(stopControllingButton).attr('href', '#');
            $(stopControllingButton).data('name', 'stopControlling');
            $(stopControllingButton).appendTo($(sessionDiv));
            $(controlButton).click(function(event){
                event.preventDefault();
                //console.log("Controlling...");
                $(this).addClass("invisible");
                $(stopControllingButton).removeClass("invisible");
                $(stopObservingButton).addClass("invisible");
                var theIframe = $("#iframe" + skey).find('iframe')[0];
                if (theIframe != null && theIframe.contentWindow){
                    theIframe.contentWindow.turnOnControl();
                }
                else{
                    console.log("Cannot turn on control");
                }
                daControlling[key] = 1;
                return false;
            });
            $(stopControllingButton).click(function(event){
                //console.log("Got click on stopControllingButton");
                event.preventDefault();
                var theIframe = $("#iframe" + skey).find('iframe')[0];
                if (theIframe != null && theIframe.contentWindow && theIframe.contentWindow.turnOffControl){
                    theIframe.contentWindow.turnOffControl();
                }
                else{
                    console.log("Cannot turn off control");
                    return false;
                }
                //console.log("Stop controlling...");
                $(this).addClass("invisible");
                $(controlButton).removeClass("invisible");
                $(stopObservingButton).removeClass("invisible");
                if (daControlling.hasOwnProperty(key)){
                    delete daControlling[key];
                }
                return false;
            });
            $(openButton).click(function(){
                //console.log("Observing..");
                $(this).addClass("invisible");
                $(stopObservingButton).removeClass("invisible");
                $("#iframe" + skey).removeClass("invisible");
                $(controlButton).removeClass("invisible");
                return true;
            });
            $(stopObservingButton).click(function(e){
                //console.log("Unobserving...");
                $(this).addClass("invisible");
                $(openButton).removeClass("invisible");
                $(controlButton).addClass("invisible");
                $(stopObservingButton).addClass("invisible");
                $(stopControllingButton).addClass("invisible");
                var theIframe = $("#iframe" + skey).find('iframe')[0];
                if (daControlling.hasOwnProperty(key)){
                    delete daControlling[key];
                    if (theIframe != null && theIframe.contentWindow && theIframe.contentWindow.turnOffControl){
                        //console.log("Calling turnOffControl in iframe");
                        theIframe.contentWindow.turnOffControl();
                    }
                }
                if (theIframe != null && theIframe.contentWindow){
                    //console.log("Deleting the iframe");
                    theIframe.contentWindow.document.open();
                    theIframe.contentWindow.document.write("");
                    theIframe.contentWindow.document.close();
                }
                $("#iframe" + skey).slideUp(400, function(){
                    $(this).css("display", "").addClass("invisible");
                });
                e.preventDefault();
                return false;
            });
            if ($(theIframeContainer).hasClass("invisible")){
                $(openButton).removeClass("invisible");
                $(stopObservingButton).addClass("invisible");
                $(controlButton).addClass("invisible");
                $(stopControllingButton).addClass("invisible");
                if (daControlling.hasOwnProperty(key)){
                    delete daControlling[key];
                }
            }
            else{
                $(openButton).addClass("invisible");
                if (daControlling.hasOwnProperty(key)){
                    $(stopObservingButton).addClass("invisible");
                    $(controlButton).addClass("invisible");
                    $(stopControllingButton).removeClass("invisible");
                }
                else{
                    $(stopObservingButton).removeClass("invisible");
                    $(controlButton).removeClass("invisible");
                    $(stopControllingButton).addClass("invisible");
                }
            }
        }
        $(theText).appendTo($(sessionDiv));
        if (obj.chatstatus == 'on' && key in daChatPartners && $("#chatarea" + skey).hasClass('invisible')){
            activateChatArea(key);
        }
        if ((obj.chatstatus != 'on' || !(key in daChatPartners)) && $("#chatarea" + skey).find('button').first().prop("disabled") == false){
            deActivateChatArea(key);
        }
        else if (obj.blocked){
            deActivateChatArea(key);
        }
    }
    function onScrollResize(){
        if (document.title != daBrowserTitle){
            document.title = daBrowserTitle;
            faviconRegular();
        }
        if (!daShowingNotif){
            return true;
        }
        var obj = Array();
        for (var key in daUpdatedSessions){
            if (daUpdatedSessions.hasOwnProperty(key)){
                obj.push(key);
            }
        }
        var somethingAbove = false;
        var somethingBelow = false;
        var firstElement = -1;
        var lastElement = -1;
        for (var i = 0; i < obj.length; ++i){
            var result = isHidden(obj[i]);
            if (result == 0){
                delete daUpdatedSessions[obj[i]];
            }
            else if (result < 0){
                var top = $(obj[i]).offset().top;
                somethingAbove = true;
                if (firstElement == -1 || top < firstElement){
                    firstElement = top;
                }
            }
            else if (result > 0){
                var top = $(obj[i]).offset().top;
                somethingBelow = true;
                if (lastElement == -1 || top > lastElement){
                    lastElement = top;
                }
            }
        }
        if (($("#chat-message-above").is(":visible")) && !somethingAbove){
            $("#chat-message-above").hide();
        }
        if (($("#chat-message-below").is(":visible")) && !somethingBelow){
            $("#chat-message-below").hide();
        }
        if (!(somethingAbove || somethingBelow)){
            daShowingNotif = false;
        }
        return true;
    }
    $(document).ready(function(){
        //console.log("document ready");
        try {
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            daAudioContext = new AudioContext();
        }
        catch(e) {
            console.log('Web Audio API is not supported in this browser');
        }
        loadSoundBuffer('newmessage', '""" + url_for('static', filename='sounds/notification-click-on.mp3') + """', '""" + url_for('static', filename='sounds/notification-click-on.ogg') + """');
        loadSoundBuffer('newconversation', '""" + url_for('static', filename='sounds/notification-stapler.mp3') + """', '""" + url_for('static', filename='sounds/notification-stapler.ogg') + """');
        loadSoundBuffer('signinout', '""" + url_for('static', filename='sounds/notification-snap.mp3') + """', '""" + url_for('static', filename='sounds/notification-snap.ogg') + """');
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/monitor" + location.port, {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/monitor" + location.port, {path: '/ws/socket.io'});
        }
        //console.log("socket is " + socket)
        if (typeof socket !== 'undefined') {
            socket.on('connect', function() {
                //console.log("Connected!");
                update_monitor();
            });
            socket.on('terminate', function() {
                //console.log("monitor: terminating socket");
                socket.disconnect();
            });
            socket.on('disconnect', function() {
                //console.log("monitor: disconnected socket");
                //socket = null;
            });
            socket.on('refreshsessions', function(data) {
                update_monitor();
            });
            // socket.on('abortcontroller', function(data) {
            //     console.log("Got abortcontroller message for " + data.key);
            // });
            socket.on('chatready', function(data) {
                var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                //console.log('chatready: ' + key);
                activateChatArea(key);
                notifyOperator(key, "chatready", """ + repr(str(word("New chat connection from"))) + """ + ' ' + data.name)
            });
            socket.on('chatstop', function(data) {
                var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                //console.log('chatstop: ' + key);
                if (key in daChatPartners){
                    delete daChatPartners[key];
                }
                deActivateChatArea(key);
            });
            socket.on('chat_log', function(arg) {
                //console.log('chat_log: ' + arg.userid);
                publish_chat_log(arg.uid, arg.i, arg.userid, arg.mode, arg.data);
            });            
            socket.on('block', function(arg) {
                //console.log("back from blocking " + arg.key);
                update_monitor();
            });            
            socket.on('unblock', function(arg) {
                //console.log("back from unblocking " + arg.key);
                update_monitor();
            });            
            socket.on('chatmessage', function(data) {
                //console.log("chatmessage");
                var keys; 
                if (data.data.mode == 'peer' || data.data.mode == 'peerhelp'){
                  keys = allSessions(data.uid, data.i);
                }
                else{
                  keys = ['da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid];
                }
                for (var i = 0; i < keys.length; ++i){
                  key = keys[i];
                  var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
                  //console.log("Received chat message for #chatarea" + skey);
                  var chatArea = $("#chatarea" + skey).find('ul').first();
                  var newLi = document.createElement('li');
                  $(newLi).addClass("list-group-item");
                  if (data.data.is_self){
                    $(newLi).addClass("list-group-item-warning dalistright");
                  }
                  else{
                    $(newLi).addClass("list-group-item-info");
                  }
                  $(newLi).html(data.data.message);
                  $(newLi).appendTo(chatArea);
                  scrollChat("#chatarea" + skey);
                  if (data.data.is_self){
                    $("#listelement" + skey).removeClass("new-message");
                    if (document.title != daBrowserTitle){
                      document.title = daBrowserTitle;
                      faviconRegular();
                    }
                  }
                  else{
                    if (!$("#chatarea" + skey).find('input').first().is(':focus')){
                      $("#listelement" + skey).addClass("new-message");
                      if (daBrowserTitle == document.title){
                        document.title = '* ' + daBrowserTitle;
                        faviconAlert();
                      }
                    }
                    if (data.data.hasOwnProperty('temp_user_id')){
                      notifyOperator(key, "chat", """ + repr(str(word("anonymous visitor"))) + """ + ' ' + data.data.temp_user_id + ': ' + data.data.message);
                    }
                    else{
                      if (data.data.first_name && data.data.first_name != ''){
                        notifyOperator(key, "chat", data.data.first_name + ' ' + data.data.last_name + ': ' + data.data.message);
                      }
                      else{
                        notifyOperator(key, "chat", data.data.email + ': ' + data.data.message);
                      }
                    }
                  }
                }
            });
            socket.on('sessionupdate', function(data) {
                //console.log("Got session update: " + data.session.chatstatus);
                draw_session(data.key, data.session);
                check_if_empty();
            });
            socket.on('updatemonitor', function(data) {
                //console.log("Got update monitor response");
                //console.log("updatemonitor: chat partners are: " + data.chatPartners);
                daChatPartners = data.chatPartners;
                daNewPhonePartners = Object();
                daTermPhonePartners = Object();
                daPhonePartners = data.phonePartners;
                var newSubscribedRoles = Object();
                for (var key in data.subscribedRoles){
                    if (data.subscribedRoles.hasOwnProperty(key)){
                        newSubscribedRoles[key] = 1;
                    }
                }
                for (var i = 0; i < data.availRoles.length; ++i){
                    var key = data.availRoles[i];
                    var skey = key.replace(/(:|\.|\[|\]|,|=|\/| )/g, '\\\\$1');
                    if ($("#role" + skey).length == 0){
                        var label = document.createElement('label');
                        $(label).addClass('checkbox-inline');
                        var input = document.createElement('input');
                        var text = document.createTextNode(key);
                        $(input).attr('type', 'checkbox');
                        $(input).attr('id', "role" + key);
                        if (key in newSubscribedRoles){
                            $(input).prop('checked', true);
                        }
                        else{
                            $(input).prop('checked', false);
                        }
                        $(input).val(key);
                        $(input).appendTo($(label));
                        $(text).appendTo($(label));
                        $(label).appendTo($("#monitorroles"));
                        $(input).change(function(){
                            var key = $(this).val();
                            //console.log("change to " + key);
                            if ($(this).is(":checked")) {
                                //console.log("it is checked");
                                daSubscribedRoles[key] = 1;
                            }
                            else{
                                //console.log("it is not checked");
                                if (key in daSubscribedRoles){
                                    delete daSubscribedRoles[key];
                                }
                            }
                            update_monitor();
                        });
                    }
                    else{
                        var input = $("#role" + skey).first();
                        if (key in newSubscribedRoles){
                            $(input).prop('checked', true);
                        }
                        else{
                            $(input).prop('checked', false);
                        }
                    }
                }
                daSubscribedRoles = newSubscribedRoles;
                newDaSessions = Object();
                for (var key in data.sessions){
                    if (data.sessions.hasOwnProperty(key)){
                        var user_id = key.replace(/^.*:userid:/, '');
                        if (true || user_id != daUserid){
                            var obj = data.sessions[key];
                            newDaSessions[key] = obj;
                            draw_session(key, obj);
                        }
                    }
                }
                var toDelete = Array();
                var numSessions = 0;
                for (var key in daSessions){
                    if (daSessions.hasOwnProperty(key)){
                        numSessions++;
                        if (!(key in newDaSessions)){
                            toDelete.push(key);
                        }
                    }
                }
                for (var i = 0; i < toDelete.length; ++i){
                    var key = toDelete[i];
                    undraw_session(key);
                }
                if ($("#monitorsessions").find("li").length > 0){
                    $("#emptylist").addClass("invisible");
                }
                else{
                    $("#emptylist").removeClass("invisible");
                }
            });
        }
        if (daAvailableForChat){
            $("#daNotAvailable").addClass("invisible");
            checkNotifications();
        }
        else{
            $("#daAvailable").addClass("invisible");
        }
        $("#daAvailable").click(function(){
            $("#daAvailable").addClass("invisible");
            $("#daNotAvailable").removeClass("invisible");
            daAvailableForChat = false;
            //console.log("daAvailableForChat: " + daAvailableForChat);
            update_monitor();
            playSound('signinout');
        });
        $("#daNotAvailable").click(function(){
            checkNotifications();
            $("#daNotAvailable").addClass("invisible");
            $("#daAvailable").removeClass("invisible");
            daAvailableForChat = true;
            //console.log("daAvailableForChat: " + daAvailableForChat);
            update_monitor();
            playSound('signinout');
        });
        $( window ).bind('unload', function() {
          if (typeof socket !== 'undefined'){
            socket.emit('terminate');
          }
        });
        if (daUsePhone){
          $("#daPhoneInfo").removeClass("invisible");
          $("#daPhoneNumber").val(daPhoneNumber);
          $("#daPhoneNumber").change(checkPhone);
          $("#daPhoneNumber").bind('keypress keydown keyup', function(e){
            if(e.keyCode == 13) { $(this).blur(); e.preventDefault(); }
          });
        }
        $(window).on('scroll', onScrollResize);
        $(window).on('resize', onScrollResize);
        $(".chat-notifier").click(function(e){
            //var key = $(this).data('key');
            var direction = 0;
            if ($(this).attr('id') == "chat-message-above"){
                direction = -1;
            }
            else{
                direction = 1;
            }
            var target = -1;
            var targetElement = null;
            for (var key in daUpdatedSessions){
                if (daUpdatedSessions.hasOwnProperty(key)){
                    var top = $(key).offset().top;
                    if (direction == -1){
                        if (target == -1 || top < target){
                            target = top;
                            targetElement = key;
                        }
                    }
                    else{
                        if (target == -1 || top > target){
                            target = top;
                            targetElement = key;
                        }
                    }
                }
            }
            if (target >= 0){
                $("html, body").animate({scrollTop: target - 60}, 500, function(){
                    $(targetElement).find("input").first().focus();
                });
            }
            e.preventDefault();
            return false;
        })
    });
</script>"""
    return render_template('pages/monitor.html', version_warning=None, bodyclass='adminbody', extra_js=Markup(script), tab_title=word('Monitor'), page_title=word('Monitor')), 200

@app.route('/updatingpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package_wait():
    next_url = request.args.get('next', url_for('update_package'))
    my_csrf = generate_csrf()
    script = """<script>
      var checkinInterval = null;
      var resultsAreIn = false;
      function daRestartCallback(data){
        //console.log("Restart result: " + data.success);
      }
      function daRestart(){
        $.ajax({
          type: 'POST',
          url: """ + repr(str(url_for('restart_ajax'))) + """,
          data: 'csrf_token=""" + my_csrf + """&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        });
        return true;
      }
      function daUpdateCallback(data){
        if (data.success){
          if (data.status == 'finished'){
            resultsAreIn = true;
            if (data.ok){
              $("#notification").html('""" + word("The package update was successful.  The logs are below.") + """');
              $("#notification").removeClass("alert-info");
              $("#notification").addClass("alert-success");
            }
            else{
              $("#notification").html('""" + word("The package update was not fully successful.  The logs are below.") + """');
              $("#notification").removeClass("alert-info");
              $("#notification").addClass("alert-danger");
            }
            $("#resultsContainer").show();
            $("#resultsArea").html(data.summary);
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
            daRestart();
          }
          else if (data.status == 'failed' && !resultsAreIn){
            resultsAreIn = true;
            $("#notification").html('""" + word("There was an error updating the packages.") + """');
            $("#notification").removeClass("alert-info");
            $("#notification").addClass("alert-danger");
            $("#resultsContainer").show();
            $("#resultsArea").html(data.error_message);
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
          }
        }
        else if (!resultsAreIn){
          $("#notification").html('""" + word("There was an error.") + """');
          $("#notification").removeClass("alert-info");
          $("#notification").addClass("alert-danger");
          if (checkinInterval != null){
            clearInterval(checkinInterval);
          }
        }
      }
      function daUpdate(){
        if (resultsAreIn){
          return;
        }
        $.ajax({
          type: 'POST',
          url: """ + repr(str(url_for('update_package_ajax'))) + """,
          data: 'csrf_token=""" + my_csrf + """',
          success: daUpdateCallback,
          dataType: 'json'
        });
        return true;
      }
      $( document ).ready(function() {
        //console.log("page loaded");
        checkinInterval = setInterval(daUpdate, 2000);
      });
    </script>
"""
    return render_template('pages/update_package_wait.html', version_warning=None, bodyclass='adminbody', extra_js=Markup(script), tab_title=word('Updating'), page_title=word('Updating'), next_page=next_url)

@app.route('/update_package_ajax', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package_ajax():
    if 'update' not in session:
        return jsonify(success=False)
    result = docassemble.webapp.worker.workerapp.AsyncResult(id=session['update'])
    if result.ready():
        if 'update' in session:
            del session['update']
        the_result = result.get()
        if type(the_result) is ReturnValue:
            if the_result.ok:
                #logmessage("update_package_ajax: success")
                return jsonify(success=True, status='finished', ok=the_result.ok, summary=summarize_results(the_result.results, the_result.logmessages))
            elif hasattr(the_result, 'error_message'):
                logmessage("update_package_ajax: failed return value is " + str(the_result.error_message))
                return jsonify(success=True, status='failed', error_message=str(the_result.error_message))
            else:
                return jsonify(success=True, status='failed', error_message=str("No error message.  Result is " + str(the_result)))
        else:
            logmessage("update_package_ajax: failed return value is a " + str(type(the_result)))
            logmessage("update_package_ajax: failed return value is " + str(the_result))
            return jsonify(success=True, status='failed', error_message=str(the_result))
    else:
        return jsonify(success=True, status='waiting')

@app.route('/updatepackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package():
    if 'update' in session:
        del session['update']
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    form = UpdatePackageForm(request.form)
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
                existing_package = Package.query.filter_by(name=target, active=True).order_by(Package.id.desc()).first()
                if existing_package is not None:
                    if existing_package.type == 'git' and existing_package.giturl is not None:
                        install_git_package(target, existing_package.giturl)
                    elif existing_package.type == 'pip':
                        install_pip_package(existing_package.name, existing_package.limitation)
        result = docassemble.webapp.worker.update_packages.delay()
        session['update'] = result.id
        return redirect(url_for('update_package_wait'))
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
                    result = docassemble.webapp.worker.update_packages.delay()
                    session['update'] = result.id
                    return redirect(url_for('update_package_wait'))
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            except Exception as errMess:
                flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        else:
            if form.giturl.data:
                giturl = form.giturl.data.strip()
                packagename = re.sub(r'/*$', '', giturl)
                packagename = re.sub(r'^git+', '', packagename)
                packagename = re.sub(r'#.*', '', packagename)
                packagename = re.sub(r'\.git$', '', packagename)
                packagename = re.sub(r'.*/', '', packagename)
                if user_can_edit_package(giturl=giturl) and user_can_edit_package(pkgname=packagename):
                    #commands = ['install', '--egg', '--src=' + temp_directory, '--log-file=' + pip_log.name, '--upgrade', "--install-option=--user", 'git+' + giturl + '.git#egg=' + packagename]
                    install_git_package(packagename, giturl)
                    result = docassemble.webapp.worker.update_packages.delay()
                    session['update'] = result.id
                    return redirect(url_for('update_package_wait'))
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            elif form.pippackage.data:
                m = re.match(r'([^>=<]+)([>=<]+.+)', form.pippackage.data)
                if m:
                    packagename = m.group(1)
                    limitation = m.group(2)
                else:
                    packagename = form.pippackage.data
                    limitation = None
                packagename = re.sub(r'[^A-Za-z0-9\_\-\.]', '', packagename)
                if user_can_edit_package(pkgname=packagename):
                    install_pip_package(packagename, limitation)
                    result = docassemble.webapp.worker.update_packages.delay()
                    session['update'] = result.id
                    return redirect(url_for('update_package_wait'))
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            else:
                flash(word('You need to supply a Git URL, upload a file, or supply the name of a package on PyPI.'), 'error')
    package_list, package_auth = get_package_info()
    form.pippackage.data = None
    form.giturl.data = None
    return render_template('pages/update_package.html', version_warning=version_warning, bodyclass='adminbody', form=form, package_list=package_list, tab_title=word('Update Package'), page_title=word('Update Package')), 200

# @app.route('/testws', methods=['GET', 'POST'])
# def test_websocket():
#     script = '<script type="text/javascript" src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>' + """<script type="text/javascript" charset="utf-8">
#     var socket;
#     $(document).ready(function(){
#         if (location.protocol === 'http:' || document.location.protocol === 'http:'){
#             socket = io.connect("http://" + document.domain + "/interview", {path: '/ws/socket.io'});
#         }
#         if (location.protocol === 'https:' || document.location.protocol === 'https:'){
#             socket = io.connect("https://" + document.domain + "/interview" + location.port, {path: '/ws/socket.io'});
#         }
#         if (typeof socket !== 'undefined') {
#             socket.on('connect', function() {
#                 //console.log("Connected!");
#                 socket.emit('chat_log', {data: 1});
#             });
#             socket.on('mymessage', function(arg) {
#                 //console.log("Received " + arg.data);
#                 $("#daPushResult").html(arg.data);
#             });
#             socket.on('chatmessage', function(arg) {
#                 console.log("Received chat message " + arg.data);
#                 var newDiv = document.createElement('div');
#                 $(newDiv).html(arg.data.message);
#                 $("#daCorrespondence").append(newDiv);
#             });
#         }
#         $("#daSend").click(daSender);
#     });
# </script>"""
#     return render_template('pages/socketserver.html', extra_js=Markup(script)), 200

@app.route('/createplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_playground_package():
    form = CreatePlaygroundPackageForm(request.form)
    current_package = request.args.get('package', None)
    do_pypi = request.args.get('pypi', False)
    do_github = request.args.get('github', False)
    do_install = request.args.get('install', False)
    if do_github:
        if not app.config['USE_GITHUB']:
            abort(404)
        if current_package is None:
            logmessage('create_playground_package: package not specified')
            abort(404)
    if app.config['USE_GITHUB']:
        github_package_name = 'docassemble-' + re.sub(r'^docassemble-', r'', current_package)
        #github_package_name = re.sub(r'[^A-Za-z\_\-]', '', github_package_name)
        if github_package_name in ['docassemble-base', 'docassemble-webapp', 'docassemble-demo']:
            abort(404)
        commit_message = request.args.get('commit_message', 'a commit')
        storage = RedisCredStorage(app='github')
        credentials = storage.get()
        if not credentials or credentials.invalid:
            session['github_state'] = random_string(16)
            session['github_next'] = 'package:' + str(current_package) + ':' + str(commit_message)
            flow = get_github_flow()
            uri = flow.step1_get_authorize_url(state=session['github_state'])
            return redirect(uri)
        http = credentials.authorize(httplib2.Http())
        resp, content = http.request("https://api.github.com/user", "GET")
        if int(resp['status']) == 200:
            user_info = json.loads(content)
            github_user_name = user_info.get('login', None)
            github_email = user_info.get('email', None)
        else:
            raise DAError("create_playground_package: could not get information about GitHub User")
        if github_user_name is None or github_email is None:
            raise DAError("create_playground_package: login and/or email not present in user info from GitHub")
        all_repositories = dict()
        resp, content = http.request("https://api.github.com/user/repos", "GET")
        if int(resp['status']) != 200:
            raise DAError("create_playground_package: could not get information about repositories")
        else:
            repositories = json.loads(content)
            for repository in repositories:
                all_repositories[repository['name']] = repository
            while True:
                next_link = get_next_link(resp)
                if next_link:
                    resp, content = http.request(next_link, "GET")
                    if int(resp['status']) != 200:
                        raise DAError("create_playground_package: could not get additional information about repositories")
                    else:
                        repositories = json.loads(content)
                        for repository in repositories:
                            all_repositories[repository['name']] = repository
                else:
                    break
    area = dict()
    area['playgroundpackages'] = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    file_list = dict()
    file_list['playgroundpackages'] = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f)) and not f.startswith('.')])
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
            flash(word('That package name is already in use by someone else.  Please change the name.'), 'error')
            current_package = None
    if current_package is not None and current_package not in file_list['playgroundpackages']:
        flash(word('Sorry, that package name does not exist in the playground'), 'error')
        current_package = None
    if current_package is not None:
        section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
        for sec in ['playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules']:
            area[sec] = SavedFile(current_user.id, fix=True, section=sec)
            file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f))])
        if os.path.isfile(os.path.join(area['playgroundpackages'].directory, current_package)):
            filename = os.path.join(area['playgroundpackages'].directory, current_package)
            info = dict()
            with open(filename, 'rU') as fp:
                content = fp.read().decode('utf8')
                info = yaml.load(content)
            for field in ['dependencies', 'dependency_links', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files']:
                if field not in info:
                    info[field] = list()
            for package in ['docassemble', 'docassemble.base']:
                if package not in info['dependencies']:
                    info['dependencies'].append(package)
            for package in info['dependencies']:
                logmessage("Considering " + str(package))
                existing_package = Package.query.filter_by(name=package, active=True).first()
                if existing_package is not None:
                    logmessage("Package " + str(package) + " exists")
                    if existing_package.giturl is None or existing_package.giturl == 'https://github.com/jhpyle/docassemble':
                        logmessage("Package " + str(package) + " exists but I will skip it; name is " + str(existing_package.name) + " and giturl is " + str(existing_package.giturl))
                        continue
                    # https://github.com/jhpyle/docassemble-helloworld
                    # git+https://github.com/fact-project/smart_fact_crawler.git@master#egg=smart_fact_crawler-0
                    #the_package_name = re.sub(r'.*/', '', existing_package.giturl)
                    #the_package_name = re.sub(r'-', '_', the_package_name)
                    #new_url = existing_package.giturl + '/archive/master.zip'
                    new_url = 'git+' + existing_package.giturl + '#egg=' + existing_package.name + '-' + existing_package.packageversion
                    if new_url not in info['dependency_links']:
                        info['dependency_links'].append(str(new_url))
                else:
                    logmessage("Package " + str(package) + " does not exist")
            info['modtime'] = os.path.getmtime(filename)
            author_info = dict()
            author_info['author name and email'] = name_of_user(current_user, include_email=True)
            author_info['author name'] = name_of_user(current_user)
            author_info['author email'] = current_user.email
            author_info['first name'] = current_user.first_name
            author_info['last name'] = current_user.last_name
            author_info['id'] = current_user.id
            if do_pypi:
                if current_user.pypi_username is None or current_user.pypi_password is None:
                    flash("Could not publish to PyPI because username and password were not defined")
                    return redirect(url_for('playground_packages', file=current_package))
                if current_user.timezone:
                    the_timezone = current_user.timezone
                else:
                    the_timezone = get_default_timezone()
                logmessages = docassemble.webapp.files.publish_package(pkgname, info, author_info, the_timezone)
                flash(logmessages, 'info')
                time.sleep(3.0)
                return redirect(url_for('playground_packages', file=current_package))
            if do_github:
                if github_package_name in all_repositories:
                    first_time = False
                else:
                    first_time = True
                    headers = {'Content-Type': 'application/json'}
                    the_license = 'mit' if re.search(r'MIT License', info.get('license', '')) else None
                    body = json.dumps(dict(name=github_package_name, description=info.get('description', None), homepage=info.get('url', None), license_template=the_license))
                    resp, content = http.request("https://api.github.com/user/repos", "POST", headers=headers, body=body)
                    if int(resp['status']) != 201:
                        raise DAError("create_playground_package: unable to create GitHub repository: status " + str(resp['status']) + " " + str(content))
                    all_repositories[github_package_name] = json.loads(content)
                directory = tempfile.mkdtemp()
                (private_key_file, public_key_file) = get_ssh_keys(github_email)
                os.chmod(private_key_file, stat.S_IRUSR | stat.S_IWUSR)
                os.chmod(public_key_file, stat.S_IRUSR | stat.S_IWUSR)
                git_prefix = "GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i \"" + str(private_key_file) + "\"' "
                ssh_url = all_repositories[github_package_name].get('ssh_url', None)
                if ssh_url is None:
                    raise DAError("create_playground_package: could not obtain ssh_url for package")
                output = ''
                output += "Doing " + git_prefix + "git clone " + ssh_url + "\n"
                try:
                    output += subprocess.check_output(git_prefix + "git clone " + ssh_url, cwd=directory, stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git clone.  " + output)
                if current_user.timezone:
                    the_timezone = current_user.timezone
                else:
                    the_timezone = get_default_timezone()
                docassemble.webapp.files.make_package_dir(pkgname, info, author_info, the_timezone, directory=directory)
                packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
                if not os.path.isdir(packagedir):
                    raise DAError("create_playground_package: package directory did not exist")
                # try:
                #     output += subprocess.check_output(["git", "init"], cwd=packagedir, stderr=subprocess.STDOUT)
                # except subprocess.CalledProcessError as err:
                #     output += err.output
                #     raise DAError("create_playground_package: error running git init.  " + output)
                try:
                    output += subprocess.check_output(["git", "config", "user.email", repr(str(github_email))], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git config user.email.  " + output)
                try:
                    output += subprocess.check_output(["git", "config", "user.name", repr(str(current_user.first_name) + " " + str(current_user.last_name))], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git config user.email.  " + output)
                try:
                    output += subprocess.check_output(["git", "add", "."], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git add.  " + output)
                try:
                    output += subprocess.check_output(["git", "commit", "-m", str(commit_message)], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git commit.  " + output)
                if False:
                    try:
                        output += subprocess.check_output(["git", "remote", "add", "origin", ssh_url], cwd=packagedir, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        output += err.output
                        raise DAError("create_playground_package: error running git remote add origin.  " + output)
                    output += git_prefix + "git push -u origin master\n"
                    try:
                        output += subprocess.check_output(git_prefix + "git push -u origin master", cwd=packagedir, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError as err:
                        output += err.output
                        raise DAError("create_playground_package: error running first git push.  " + output)
                else:
                    output += git_prefix + "git push\n"
                    try:
                        output += subprocess.check_output(git_prefix + "git push", cwd=packagedir, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError as err:
                        output += err.output
                        raise DAError("create_playground_package: error running git push.  " + output)
                flash(word("Pushed commit to GitHub.") + "  " + output, 'info')
                time.sleep(3.0)
                shutil.rmtree(directory)
                return redirect(url_for('playground_packages', file=current_package))
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            if current_user.timezone:
                the_timezone = current_user.timezone
            else:
                the_timezone = get_default_timezone()
            zip_file = docassemble.webapp.files.make_package_zip(pkgname, info, author_info, the_timezone)
            saved_file.copy_from(zip_file.name)
            saved_file.finalize()
            # # Why do this here?  To reserve the name?  It is all done by install_zip_package
            # # and otherwise why mess up the package listing?
            # existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).first()
            # if existing_package is None:
            #     package_auth = PackageAuth(user_id=current_user.id)
            #     package_entry = Package(name='docassemble.' + pkgname, package_auth=package_auth, upload=file_number, type='zip')
            #     db.session.add(package_auth)
            #     db.session.add(package_entry)
            #     #sys.stderr.write("Ok, did the commit\n")
            # else:
            #     existing_package.upload = file_number
            #     existing_package.active = True
            #     existing_package.version += 1
            # db.session.commit()
            if do_install:
                install_zip_package('docassemble.' + pkgname, file_number)
                result = docassemble.webapp.worker.update_packages.delay()
                session['update'] = result.id
                return redirect(url_for('update_package_wait', next=url_for('playground_packages', file=current_package)))
                #return redirect(url_for('playground_packages', file=current_package))
            else:
                response = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return(response)
    return render_template('pages/create_playground_package.html', version_warning=version_warning, bodyclass='adminbody', form=form, current_package=current_package, package_names=file_list['playgroundpackages'], tab_title=word('Playground Packages'), page_title=word('Playground Packages')), 200

@app.route('/createpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_package():
    form = CreatePackageForm(request.form)
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
            manifestin = """\
include README.md
"""
            setupcfg = """\
[metadata]
description-file = README
"""
            setuppy = """\
#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils2.util import convert_path

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info', '.git', '.gitignore')
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
      version='0.0.1',
      description=('A docassemble extension.'),
      author=""" + repr(str(name_of_user(current_user))) + """,
      author_email=""" + repr(str(current_user.email)) + """,
      license='MIT',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      zip_safe = False,
      package_data=find_package_data(where='docassemble/""" + str(pkgname) + """/', package='docassemble.""" + str(pkgname) + """'),
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
    - name: """ + unicode(current_user.first_name) + " " + unicode(current_user.last_name) + """
      organization: """ + unicode(current_user.organization) + """
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

If you want to use non-standard document templates with pandoc,
put template files in this directory.
"""
            staticreadme = """\
# Static file directory

If you want to make files available in the web app, put them in
this directory.
"""
            sourcesreadme = """\
# Sources directory

This directory is used to store word translation files, 
machine learning training files, and other source files.
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
            sourcesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'sources')
            if not os.path.isdir(questionsdir):
                os.makedirs(questionsdir)
            if not os.path.isdir(templatesdir):
                os.makedirs(templatesdir)
            if not os.path.isdir(staticdir):
                os.makedirs(staticdir)
            if not os.path.isdir(sourcesdir):
                os.makedirs(sourcesdir)
            with open(os.path.join(packagedir, 'README.md'), 'w') as the_file:
                the_file.write(readme)
            with open(os.path.join(packagedir, 'LICENSE'), 'w') as the_file:
                the_file.write(licensetext)
            with open(os.path.join(packagedir, 'setup.py'), 'w') as the_file:
                the_file.write(setuppy)
            with open(os.path.join(packagedir, 'setup.cfg'), 'w') as the_file:
                the_file.write(setupcfg)
            with open(os.path.join(packagedir, 'MANIFEST.in'), 'w') as the_file:
                the_file.write(manifestin)
            with open(os.path.join(packagedir, 'docassemble', '__init__.py'), 'w') as the_file:
                the_file.write(initpy)
            with open(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), 'w') as the_file:
                the_file.write('')
            with open(os.path.join(packagedir, 'docassemble', pkgname, 'objects.py'), 'w') as the_file:
                the_file.write(objectfile)
            with open(os.path.join(templatesdir, 'README.md'), 'w') as the_file:
                the_file.write(templatereadme)
            with open(os.path.join(staticdir, 'README.md'), 'w') as the_file:
                the_file.write(staticreadme)
            with open(os.path.join(sourcesdir, 'README.md'), 'w') as the_file:
                the_file.write(sourcesreadme)
            with open(os.path.join(questionsdir, 'questions.yml'), 'w') as the_file:
                the_file.write(questionfiletext)
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            zf = zipfile.ZipFile(saved_file.path, mode='w')
            trimlength = len(directory) + 1
            if current_user.timezone:
                the_timezone = pytz.timezone(current_user.timezone)
            else:
                the_timezone = pytz.timezone(get_default_timezone())
            for root, dirs, files in os.walk(packagedir):
                for file in files:
                    thefilename = os.path.join(root, file)
                    info = zipfile.ZipInfo(thefilename[trimlength:])
                    info.date_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(thefilename)).replace(tzinfo=pytz.utc).astimezone(the_timezone).timetuple()
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0644 << 16L
                    with open(thefilename, 'rb') as fp:
                        zf.writestr(info, fp.read())
                    #zf.write(thefilename, thefilename[trimlength:])
            zf.close()
            saved_file.save()
            saved_file.finalize()
            shutil.rmtree(directory)
            existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).order_by(Package.id.desc()).first()
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
            response = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return response
    return render_template('pages/create_package.html', version_warning=version_warning, bodyclass='adminbody', form=form, tab_title=word('Create Package'), page_title=word('Create Package')), 200

@app.route('/restart', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_page():
    script = """<script>
      function daRestartCallback(data){
        //console.log("Restart result: " + data.success);
      }
      function daRestart(){
        $.ajax({
          type: 'POST',
          url: """ + repr(str(url_for('restart_ajax'))) + """,
          data: 'csrf_token=""" + generate_csrf() + """&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        });
        return true;
      }
      $( document ).ready(function() {
        //console.log("restarting");
        setTimeout(daRestart, 500);
      });
    </script>
"""
    next_url = request.args.get('next', url_for('interview_list'))
    extra_meta = """\n    <meta http-equiv="refresh" content="5;URL='""" + next_url + """'">"""
    return render_template('pages/restart.html', version_warning=None, bodyclass='adminbody', extra_meta=Markup(extra_meta), extra_js=Markup(script), tab_title=word('Restarting'), page_title=word('Restarting'))

def get_gd_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('googledrive', dict())
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('Google Drive is not configured.')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='https://www.googleapis.com/auth/drive',
        redirect_uri=url_for('google_drive_callback', _external=True),
        access_type='offline',
        approval_prompt='force')
    return flow

def get_gd_folder():
    key = 'da:googledrive:mapping:userid:' + str(current_user.id)
    return r.get(key)

def set_gd_folder(folder):
    key = 'da:googledrive:mapping:userid:' + str(current_user.id)
    if folder is None:
        r.delete(key)
    else:
        r.set(key, folder)

class RedisCredStorage(oauth2client.client.Storage):
    def __init__(self, app='googledrive'):
        self.key = 'da:' + app + ':userid:' + str(current_user.id)
        self.lockkey = 'da:' + app + ':lock:userid:' + str(current_user.id)        
    def acquire_lock(self):
        pipe = r.pipeline()
        pipe.set(self.lockkey, 1)
        pipe.expire(self.lockkey, 5)
        pipe.execute()
    def release_lock(self):
        r.delete(self.lockkey)
    def locked_get(self):
        json_creds = r.get(self.key)
        creds = None
        if json_creds is not None:
            try:
                creds = oauth2client.client.Credentials.new_from_json(json_creds)
            except:
                logmessage("Could not read credentials from " + str(json_creds))
        return creds
    def locked_put(self, credentials):
        r.set(self.key, credentials.to_json())
    def locked_delete(self):
        r.delete(self.key)

@app.route('/google_drive_callback', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def google_drive_callback():
    for key in request.args:
        logmessage("Argument " + str(key) + ": " + str(request.args[key]))
    if 'code' in request.args:
        flow = get_gd_flow()
        credentials = flow.step2_exchange(request.args['code'])
        storage = RedisCredStorage(app='googledrive')
        storage.put(credentials)
        error = None
    elif 'error' in request.args:
        error = request.args['error']
    else:
        error = word("could not connect to Google Drive")
    if error:
        flash(word('There was a Google Drive error: ' + error), 'error')
        return redirect(url_for('interview_list'))
    else:
        flash(word('Connected to Google Drive'), 'success')
    return redirect(url_for('google_drive_page'))

def trash_gd_file(section, filename):
    if section == 'template':
        section == 'templates'
    the_folder = get_gd_folder()
    if the_folder is None:
        logmessage('trash_gd_file: folder not configured')
        return False
    storage = RedisCredStorage(app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('trash_gd_file: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)
    response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()
    trashed = response.get('trashed', False)
    the_mime_type = response.get('mimeType', None)
    if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
        logmessage('trash_gd_file: folder did not exist')
        return False
    subdir = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(section) + "' and '" + str(the_folder) + "' in parents").execute()
    for the_file in response.get('files', []):
        if 'id' in the_file:
            subdir = the_file['id']
            break
    if subdir is None:
        logmessage('trash_gd_file: section ' + str(section) + ' could not be found')
        return False
    id_of_filename = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType!='application/vnd.google-apps.folder' and trashed=false and name='" + str(filename) + "' and '" + str(subdir) + "' in parents").execute()
    for the_file in response.get('files', []):
        if 'id' in the_file:
            id_of_filename = the_file['id']
            break
    if id_of_filename is None:
        logmessage('trash_gd_file: file ' + str(filename) + ' could not be found in ' + str(section))
        return False
    file_metadata = { 'trashed': True }
    service.files().update(fileId=id_of_filename,
                           body=file_metadata).execute()
    return True

@app.route('/sync_with_google_drive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def sync_with_google_drive():
    if app.config['USE_GOOGLE_DRIVE'] is False:
        flash(word("Google Drive is not configured"), "error")
        return redirect(url_for('interview_list'))
    storage = RedisCredStorage(app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)
    the_folder = get_gd_folder()
    response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()
    the_mime_type = response.get('mimeType', None)
    trashed = response.get('trashed', False)
    if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
        flash(word("Error accessing Google Drive"), 'error')
        return redirect(url_for('google_drive'))
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
        area = SavedFile(current_user.id, fix=True, section=the_section)
        for f in os.listdir(area.directory):
            local_files[section].add(f)
            local_modtimes[section][f] = os.path.getmtime(os.path.join(area.directory, f))
        subdirs = list()
        page_token = None
        while True:
            response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + section + "' and '" + str(the_folder) + "' in parents").execute()
            for the_file in response.get('files', []):
                if 'id' in the_file:
                    subdirs.append(the_file['id'])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        if len(subdirs) == 0:
            flash(word("Error accessing " + section + " in Google Drive"), 'error')
            return redirect(url_for('google_drive'))
        subdir = subdirs[0]
        gd_files[section] = set()
        gd_ids[section] = dict()
        gd_modtimes[section] = dict()
        gd_deleted[section] = set()
        page_token = None
        while True:
            response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name, modifiedTime, trashed)", q="mimeType!='application/vnd.google-apps.folder' and '" + str(subdir) + "' in parents").execute()
            for the_file in response.get('files', []):
                gd_ids[section][the_file['name']] = the_file['id']
                gd_modtimes[section][the_file['name']] = strict_rfc3339.rfc3339_to_timestamp(the_file['modifiedTime'])
                if the_file['trashed']:
                    gd_deleted[section].add(the_file['name'])
                    continue
                gd_files[section].add(the_file['name'])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        for f in gd_files[section]:
            if f not in local_files[section] or gd_modtimes[section][f] - local_modtimes[section][f] > 3:
                sections_modified.add(section)
                commentary += "Copied " + f + " from Google Drive.  "
                the_path = os.path.join(area.directory, f)
                with open(the_path, 'wb') as fh:
                    response = service.files().get_media(fileId=gd_ids[section][f])
                    downloader = apiclient.http.MediaIoBaseDownload(fh, response)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        #logmessage("Download %d%%." % int(status.progress() * 100))
                os.utime(the_path, (gd_modtimes[section][f], gd_modtimes[section][f]))
        for f in local_files[section]:
            if f not in gd_deleted[section]:
                if f not in gd_files[section]:
                    commentary += "Copied " + f + " to Google Drive.  "
                    the_path = os.path.join(area.directory, f)
                    extension, mimetype = get_ext_and_mimetype(the_path)
                    the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
                    file_metadata = { 'name' : f, 'parents': [subdir], 'modifiedTime': the_modtime, 'createdTime': the_modtime }
                    media = apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                    the_new_file = service.files().create(body=file_metadata,
                                                          media_body=media,
                                                          fields='id').execute()
                    new_id = the_new_file.get('id')
                elif local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                    commentary += "Updated " + f + " on Google Drive.  "
                    the_path = os.path.join(area.directory, f)
                    extension, mimetype = get_ext_and_mimetype(the_path)
                    the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
                    file_metadata = { 'modifiedTime': the_modtime }
                    media = apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                    service.files().update(fileId=gd_ids[section][f],
                                           body=file_metadata,
                                           media_body=media).execute()
        for f in gd_deleted[section]:
            if f in local_files[section]:
                if local_modtimes[section][f] - gd_modtimes[section][f] > 3:
                    commentary += "Undeleted and updated " + f + " on Google Drive.  "
                    the_path = os.path.join(area.directory, f)
                    extension, mimetype = get_ext_and_mimetype(the_path)
                    the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
                    file_metadata = { 'modifiedTime': the_modtime, 'trashed': False }
                    media = apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
                    service.files().update(fileId=gd_ids[section][f],
                                           body=file_metadata,
                                           media_body=media).execute()
                else:
                    sections_modified.add(section)
                    commentary += "Deleted " + f + " from Playground.  "
                    the_path = os.path.join(area.directory, f)
                    if os.path.isfile(the_path):
                        area.delete_file(f)
        area.finalize()
    if commentary != '':
        flash(commentary, 'success')
    next = request.args.get('next', url_for('playground_page'))
    if 'modules' in sections_modified:
        return redirect(url_for('restart_page', next=next))
    return redirect(next)
    #return render_template('pages/testgoogledrive.html', tab_title=word('Google Drive Test'), page_title=word('Google Drive Test'), commentary=commentary)

@app.route('/google_drive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def google_drive_page():
    if app.config['USE_GOOGLE_DRIVE'] is False:
        flash(word("Google Drive is not configured"), "error")
        return redirect(url_for('interview_list'))
    form = GoogleDriveForm(request.form)
    storage = RedisCredStorage(app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        logmessage("uri is " + str(uri))
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)
    items = [dict(id='', name=word('-- Do not link --'))]
    #items = []
    page_token = None
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents").execute()
        for the_file in response.get('files', []):
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    item_ids = [x['id'] for x in items if x['id'] != '']
    if request.method == 'POST' and form.submit.data:
        if form.folder.data == '':
            set_gd_folder(None)
        elif form.folder.data == -1:
            file_metadata = {
                'name' : 'docassemble',
                'mimeType' : 'application/vnd.google-apps.folder'
            }
            new_file = service.files().create(body=file_metadata,
                                              fields='id').execute()
            new_folder = new_file.get('id', None)
            set_gd_folder(new_folder)
            if new_folder is not None:
                active_folder = dict(id=new_folder, name='docassemble')
                items.append(active_folder)
                item_ids.append(new_folder)
        elif form.folder.data in item_ids:
            set_gd_folder(form.folder.data)
        else:
            flash(word("The supplied folder could not be found."), 'error')
            set_gd_folder(None)
    the_folder = get_gd_folder()
    active_folder = None
    if the_folder is not None:
        response = service.files().get(fileId=the_folder, fields="mimeType, trashed").execute()
        the_mime_type = response.get('mimeType', None)
        trashed = response.get('trashed', False)
        if trashed is False and the_mime_type == "application/vnd.google-apps.folder":
            active_folder = dict(id=the_folder, name=response.get('name', 'no name'))
            if the_folder not in item_ids:
                items.append(active_folder)
        else:
            set_gd_folder(None)
            the_folder = None
            flash(word("The mapping was reset because the folder does not appear to exist anymore."), 'error')
    if the_folder is None:
        for item in items:
            if (item['name'].lower() == 'docassemble'):
                active_folder = item
                break
    if active_folder is None:
        active_folder = dict(id=-1, name='docassemble')
        items.append(active_folder)
        item_ids.append(-1)
    if the_folder is not None:
        subdirs = list()
        page_token = None
        while True:
            response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and '" + str(the_folder) + "' in parents").execute()
            for the_file in response.get('files', []):
                subdirs.append(the_file)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        todo = set(['questions', 'static', 'sources', 'templates', 'modules'])
        done = set([x['name'] for x in subdirs if x['name'] in todo])
        for key in todo - done:
            file_metadata = {
                'name' : key,
                'mimeType' : 'application/vnd.google-apps.folder',
                'parents': [the_folder]
            }
            new_file = service.files().create(body=file_metadata,
                                              fields='id').execute()
    if the_folder is None:
        the_folder = ''
    description = 'Select the folder from your Google Drive that you want to be synchronized with the Playground.'
    return render_template('pages/googledrive.html', version_warning=version_warning, bodyclass='adminbody', header=word('Google Drive'), tab_title=word('Google Drive'), items=items, the_folder=the_folder, page_title=word('Google Drive'), form=form)

@app.route('/config', methods=['GET', 'POST'])
@login_required
@roles_required(['admin'])
def config_page():
    form = ConfigForm(request.form)
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
                logmessage('config_page: ' + str(errMess))
            if ok:
                if cloud is not None:
                    key = cloud.get_key('config.yml')
                    key.set_contents_from_string(form.config_content.data)
                with open(daconfig['config file'], 'w') as fp:
                    fp.write(form.config_content.data.encode('utf8'))
                    flash(word('The configuration file was saved.'), 'success')
                #session['restart'] = 1
                return redirect(url_for('restart_page'))
        elif form.cancel.data:
            flash(word('Configuration not updated.'), 'info')
            return redirect(url_for('interview_list'))
        else:
            flash(word('Configuration not updated.  There was an error.'), 'error')
            return redirect(url_for('interview_list'))
    if ok:
        with open(daconfig['config file'], 'rU') as fp:
            content = fp.read().decode('utf8')
    if content is None:
        abort(404)
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    python_version = daconfig.get('python version', word('Unknown'))
    system_version = daconfig.get('system version', word('Unknown'))
    if python_version == system_version:
        version = word("Version ") + unicode(python_version)
    else:
        version = word("Version ") + unicode(python_version) + ' (Python); ' + unicode(system_version) + ' (' + word('system') + ')'
    return render_template('pages/config.html', version_warning=version_warning, version=version, bodyclass='adminbody', tab_title=word('Configuration'), page_title=word('Configuration'), extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    ' + kbLoad + '<script>\n      daTextArea=document.getElementById("config_content");\n      daTextArea.value = ' + json.dumps(content) + ';\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", ' + kbOpt + 'tabSize: 2, tabindex: 70, autofocus: true, lineNumbers: true, matchBrackets: true});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n      daCodeMirror.setOption("coverGutterNextToScrollbar", true);\n    </script>'), form=form), 200

@app.route('/view_source', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def view_source():
    source_path = request.args.get('i', None)
    if source_path is None:
        logmessage("No source path")
        abort(404)
    try:
        if re.search(r':', source_path):
            source = docassemble.base.parse.interview_source_from_string(source_path)
        else:
            try:
                source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + source_path)
            except:
                source = docassemble.base.parse.interview_source_from_string(source_path)
    except Exception as errmess:
        logmessage("No source: " + str(errmess))
        abort(404)
    header = source_path
    return render_template('pages/view_source.html', version_warning=None, bodyclass='adminbody', tab_title="Source", page_title="Source", extra_css=Markup('\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), header=header, contents=Markup(highlight(source.content, YamlLexer(), HtmlFormatter(cssclass="highlight fullheight")))), 200

@app.route('/playgroundstatic/<userid>/<filename>', methods=['GET'])
def playground_static(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundstatic')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        return(response)
    abort(404)

@app.route('/playgroundsources/<userid>/<filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_sources(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundsources')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/playgroundtemplate/<userid>/<filename>', methods=['GET'])
def playground_template(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundtemplate')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/playgrounddownload/<userid>/<filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_download(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', filename)
    area = SavedFile(userid, fix=True, section='playground')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/playgroundfiles', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_files():
    if app.config['USE_GOOGLE_DRIVE'] is False or get_gd_folder() is None:
        use_gd = False
    else:
        use_gd = True
    form = PlaygroundFilesForm(request.form)
    formtwo = PlaygroundFilesEditForm(request.form)
    if 'ajax' in request.form:
        is_ajax = True
    else:
        is_ajax = False
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
    if section not in ["template", "static", "sources", "modules", "packages"]:
        section = "template"
    pgarea = SavedFile(current_user.id, fix=True, section='playground')
    pulldown_files = sorted([f for f in os.listdir(pgarea.directory) if os.path.isfile(os.path.join(pgarea.directory, f))])
    if 'variablefile' in session:
        if session['variablefile'] in pulldown_files:
            active_file = session['variablefile']
        else:
            del session['variablefile']
            active_file = None
    else:
        active_file = None
    if active_file is None:
        if 'playgroundfile' in session and session['playgroundfile'] in pulldown_files:
            active_file = session['playgroundfile']
        elif len(pulldown_files):
            active_file = pulldown_files[0]
    area = SavedFile(current_user.id, fix=True, section='playground' + section)
    if request.args.get('delete', False):
        argument = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', request.args.get('delete'))
        if argument:
            filename = os.path.join(area.directory, argument)
            if os.path.exists(filename):
                os.remove(filename)
                area.finalize()
                if use_gd:
                    try:
                        trash_gd_file(section, argument)
                    except Exception as the_err:
                        logmessage("playground_files: unable to delete file on Google Drive.  " + str(the_err))
                flash(word("Deleted file: ") + argument, "success")
                return redirect(url_for('playground_files', section=section))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.args.get('convert', False):
        argument = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', request.args.get('convert'))
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
        if 'uploadfile' in request.files:
            the_files = request.files.getlist('uploadfile')
            if the_files:
                for up_file in the_files:
                    try:
                        filename = secure_filename(up_file.filename)
                        filename = re.sub(r'[^A-Za-z0-9\-\_\.]+', '_', filename)
                        the_file = filename
                        filename = os.path.join(area.directory, filename)
                        up_file.save(filename)
                        area.finalize()
                        if section == 'modules':
                            return redirect(url_for('restart_page', next=url_for('playground_files', section=section, file=the_file)))
                    except Exception as errMess:
                        flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
                flash(word("Upload successful"), "success")
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
                the_time = formatted_current_time()
                area.finalize()
                if formtwo.active_file.data:
                    interview_file = os.path.join(pgarea.directory, formtwo.active_file.data)
                    if os.path.isfile(interview_file):
                        with open(interview_file, 'a'):
                            os.utime(interview_file, None)
                        pgarea.finalize()
                flash_message = flash_as_html(str(the_file) + ' ' + word('was saved at') + ' ' + the_time + '.', message_type='success', is_ajax=is_ajax)
                if section == 'modules':
                    #restart_all()
                    return redirect(url_for('restart_page', next=url_for('playground_files', section=section, file=the_file)))
                if is_ajax:
                    return jsonify(success=True, flash_message=flash_message)
                else:
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
    if the_file and not is_new and the_file not in editable_files:
        the_file = ''
    if not the_file and not is_new:
        if 'playground' + section in session and session['playground' + section] in editable_files:
            the_file = session['playground' + section]
        else:
            if 'playground' + section in session:
                del session['playground' + section]
            if len(editable_files):
                the_file = editable_files[0]
            else:
                if section == 'modules':
                    the_file = 'test.py'
                elif section == 'sources':
                    the_file = 'test.json'
                else:
                    the_file = 'test.md'
    if the_file in editable_files:
        session['playground' + section] = the_file
    if the_file != '':
        extension, mimetype = get_ext_and_mimetype(the_file)
        if (mimetype and mimetype in ok_mimetypes):
            mode = ok_mimetypes[mimetype]
        elif (extension and extension in ok_extensions):
            mode = ok_extensions[extension]
    if mode != 'markdown':
        active_file = None
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
    lowerdescription = None
    description = None
    if (section == "template"):
        header = word("Templates")
        description = 'Add files here that you want want to include in your interviews using "docx template file," "pdf template file," "content file," "initial yaml," "additional yaml," "template file," "rtf template file," or "docx reference file."'
        upload_header = word("Upload a template file")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "static"):
        header = word("Static Files")
        description = 'Add files here that you want to include in your interviews with "images," "image sets," "[FILE]" or "url_of()."'
        upload_header = word("Upload a static file")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "sources"):
        header = word("Source Files")
        description = 'Add files here that you want to make available to your interview code, such as word translation files and training data for machine learning.'
        upload_header = word("Upload a source file")
        edit_header = word('Edit source files')
        after_text = None
    elif (section == "modules"):
        header = word("Modules")
        upload_header = word("Upload a Python module")
        edit_header = word('Edit module files')
        lowerdescription = Markup("""<p>To use this in an interview, write a <code>modules</code> block that refers to this module using Python's syntax for specifying a "relative import" of a module (i.e., prefix the module name with a period).</p>""" + highlight('---\nmodules:\n  - .' + re.sub(r'\.py$', '', the_file) + '\n---', YamlLexer(), HtmlFormatter()))
        after_text = None
    if scroll:
        extra_command = """
        if ($("#file_name").val().length > 0){
          daCodeMirror.focus();
        }
        else{
          $("#file_name").focus()
        }
        scrollBottom();"""
    else:
        extra_command = ""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    extra_js = """
    <script>
      var daCodeMirror;
      var daTextArea;
      var vocab = [];
      var daIsNew = """ + ('true' if is_new else 'false') + """;
      var daSection = """ + '"' + section + '";' + """

""" + variables_js(form='formtwo') + """

""" + search_js(form='formtwo') + """

      function saveCallback(data){
        fetchVars(true);
        if ($("#flash").length){
          $("#flash").html(data.flash_message);
        }
        else{
          $("#main").prepend('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">' + data.flash_message + '</div>');
        }
      }

      function scrollBottom(){
        $("html, body").animate({
          scrollTop: $("#editnav").offset().top - 53
        }, "slow");
      }
      $( document ).ready(function() {
        $("#uploadbutton").click(function(event){
          if ($("#uploadfile").val() == ""){
            event.preventDefault();
            return false;
          }
        });
        daTextArea = document.getElementById("file_content");
        daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: """ + ('{name: "markdown", underscoresBreakWords: false}' if mode == 'markdown' else repr(str(mode))) + """, """ + kbOpt + """tabSize: 2, tabindex: 580, autofocus: false, lineNumbers: true, matchBrackets: true});
        $(window).bind("beforeunload", function(){
          daCodeMirror.save();
          $("#formtwo").trigger("checkform.areYouSure");
        });
        $("#daDelete").click(function(event){
          if (!confirm(""" + repr(str(word("Are you sure that you want to delete this file?"))) + """)){
            event.preventDefault();
          }
        });
        $("#formtwo").areYouSure(""" + repr(str(json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}))) + """);
        $("#formtwo").bind("submit", function(e){
          daCodeMirror.save();
          $("#formtwo").trigger("reinitialize.areYouSure");
          if (daSection != 'modules' && !daIsNew){
            var extraVariable = ''
            if ($("#daVariables").length){
              extraVariable = '&active_file=' + encodeURIComponent($("#daVariables").val());
            }
            $.ajax({
              type: "POST",
              url: """ + '"' + url_for('playground_files') + '"' + """,
              data: $("#formtwo").serialize() + extraVariable + '&submit=Save&ajax=1',
              success: function(data){
                saveCallback(data);
                setTimeout(function(){
                  $("#flash .alert-success").hide(300, function(){
                    $(self).remove();
                  });
                }, 3000);
              },
              dataType: 'json'
            });
            e.preventDefault();
            return false;
          }
          return true;
        });
        daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});
        daCodeMirror.setOption("coverGutterNextToScrollbar", true);
        $("#uploadfile").fileinput();
        searchReady();
        variablesReady();
        fetchVars(false);""" + extra_command + """
      });
      searchReady();
    </script>"""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    if len(editable_files):
        any_files = True
    else:
        any_files = False
    back_button = Markup('<a href="' + url_for('playground_page') + '" class="btn btn-sm navbar-btn nav-but"><i class="glyphicon glyphicon-arrow-left"></i> ' + word("Back") + '</a>')
    return render_template('pages/playgroundfiles.html', version_warning=None, bodyclass='adminbody', use_gd=use_gd, back_button=back_button, tab_title=header, page_title=header, extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    ' + kbLoad + '<script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/" + mode + "/" + ('damarkdown' if mode == 'markdown' else mode) + ".js") + '"></script>' + extra_js), header=header, upload_header=upload_header, edit_header=edit_header, description=description, lowerdescription=lowerdescription, form=form, files=files, section=section, userid=current_user.id, editable_files=editable_files, convertible_files=convertible_files, formtwo=formtwo, current_file=the_file, content=content, after_text=after_text, is_new=str(is_new), any_files=any_files, pulldown_files=pulldown_files, active_file=active_file), 200

@app.route('/pullplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def pull_playground_package():
    form = PullPlaygroundPackage(request.form)
    if request.method == 'POST':
        if form.pull.data:
            if form.github_url.data and form.pypi.data:
                flash(word("You cannot pull from GitHub and PyPI at the same time.  Please fill in one and leave the other blank."), 'error')
            elif form.github_url.data:
                return redirect(url_for('playground_packages', pull='1', github_url=form.github_url.data))
            elif form.pypi.data:
                return redirect(url_for('playground_packages', pull='1', pypi=form.pypi.data))
        if form.cancel.data:
            return redirect(url_for('playground_packages'))
    elif 'file' in request.args:
        form.github_url.data = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['file'])
    description = word("Enter a URL of a GitHub repository containing an extension package.  When you press Pull, the contents of that repository will be copied into the Playground, overwriting any files with the same names.")
    return render_template('pages/pull_playground_package.html', form=form, description=description, version_warning=version_warning, bodyclass='adminbody', title=word("Pull GitHub or PyPI Package"), tab_title=word("Pull"), page_title=word("Pull")), 200

@app.route('/playgroundpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_packages():
    form = PlaygroundPackagesForm(request.form)
    fileform = PlaygroundUploadForm(request.form)
    the_file = request.args.get('file', '')
    if the_file == '':
        no_file_specified = True
    else:
        no_file_specified = False
    scroll = False
    allow_pypi = daconfig.get('pypi', False)
    pypi_username = current_user.pypi_username
    pypi_password = current_user.pypi_password
    pypi_url = daconfig.get('pypi url', 'https://pypi.python.org/pypi')
    if allow_pypi is True and pypi_username is not None and pypi_password is not None:
        can_publish_to_pypi = True
    else:
        can_publish_to_pypi = False
    if app.config['USE_GITHUB']:
        can_publish_to_github = r.get('da:using_github:userid:' + str(current_user.id))
    else:
        can_publish_to_github = None
    github_message = None
    pypi_message = None
    pypi_version = None        
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
    section_name = {'playground': 'Interview files', 'playgroundpackages': 'Packages', 'playgroundtemplate': 'Template files', 'playgroundstatic': 'Static files', 'playgroundsources': 'Source files', 'playgroundmodules': 'Modules'}
    section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
    section_field = {'playground': form.interview_files, 'playgroundtemplate': form.template_files, 'playgroundstatic': form.static_files, 'playgroundsources': form.sources_files, 'playgroundmodules': form.module_files}
    for sec in ['playground', 'playgroundpackages', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules']:
        area[sec] = SavedFile(current_user.id, fix=True, section=sec)
        file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f)) and not f.startswith('.')])
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
    files = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f)) and not f.startswith('.')])
    editable_files = list()
    mode = "yaml"
    for a_file in files:
        editable_files.append(a_file)
    if request.method == 'GET' and not the_file and not is_new:
        if 'playgroundpackages' in session and session['playgroundpackages'] in editable_files:
            the_file = session['playgroundpackages']
        else:
            if 'playgroundpackages' in session:
                del session['playgroundpackages']
            if len(editable_files):
                the_file = editable_files[0]
            else:
                the_file = ''
    if the_file != '' and not user_can_edit_package(pkgname='docassemble.' + the_file):
        flash(word('Sorry, that package name,') + ' ' + the_file + word(', is already in use by someone else'), 'error')
        the_file = ''
    if request.method == 'GET' and the_file in editable_files:
        session['playgroundpackages'] = the_file
    if the_file == '' and len(file_list['playgroundpackages']) and not is_new:
        the_file = file_list['playgroundpackages'][0]
    old_info = dict()
    on_github = False
    github_http = None
    if the_file != '' and can_publish_to_github and not is_new:
        github_package_name = 'docassemble-' + the_file
        try:
            storage = RedisCredStorage(app='github')
            credentials = storage.get()
            if not credentials or credentials.invalid:
                session['github_state'] = random_string(16)
                session['github_next'] = 'playgroundpackages:' + the_file
                flow = get_github_flow()
                uri = flow.step1_get_authorize_url(state=session['github_state'])
                return redirect(uri)
            http = credentials.authorize(httplib2.Http())
            resp, content = http.request("https://api.github.com/user", "GET")
            if int(resp['status']) == 200:
                info = json.loads(content)
                github_user_name = info.get('login', None)
                github_author_name = info.get('name', None)
                github_email = info.get('email', None)
            else:
                raise DAError("create_playground_package: could not get information about GitHub User")
            if github_user_name is None:
                raise DAError("playground_packages: login not present in user info from GitHub")
            resp, content = http.request("https://api.github.com/repos/" + str(github_user_name) + "/" + github_package_name, "GET")
            if int(resp['status']) == 200:
                repo_info = json.loads(content)
                github_http = repo_info['html_url']
                github_message = word('This package is') + ' <a target="_blank" href="' + repo_info.get('html_url', 'about:blank') + '">' + word("published on GitHub") + '</a>.'
                if github_author_name:
                    github_message += "  " + word("The author is") + " " + github_author_name + "."
                on_github = True
            else:
                github_message = word('This package is not yet published on GitHub.')
        except Exception as e:
            logmessage('playground_packages: GitHub error.  ' + str(e))
            github_message = word('Unable to determine if the package is published on GitHub.')
            github_user_name = None
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
                    if 'dependencies' in old_info and type(old_info['dependencies']) is list and len(old_info['dependencies']):
                        for item in old_info['dependencies']:
                            pass#PPP
                    for field in ['dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files']:
                        if field in old_info and type(old_info[field]) is list and len(old_info[field]):
                            form[field].data = old_info[field]
        else:
            filename = None
    if request.method == 'POST' and 'uploadfile' in request.files:
        the_files = request.files.getlist('uploadfile')
        need_to_restart = False
        if current_user.timezone:
            the_timezone = pytz.timezone(current_user.timezone)
        else:
            the_timezone = pytz.timezone(get_default_timezone())
        epoch_date = datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.utc)
        if the_files:
            for up_file in the_files:
                #try:
                    zip_filename = secure_filename(up_file.filename)
                    zippath = tempfile.NamedTemporaryFile(mode="wb", suffix=".zip", delete=True)
                    up_file.save(zippath.name)
                    area_sec = dict(templates='playgroundtemplate', static='playgroundstatic', sources='playgroundsources', questions='playground')
                    with zipfile.ZipFile(zippath.name, mode='r') as zf:
                        readme_text = ''
                        setup_py = ''
                        extracted = dict()
                        data_files = dict(templates=list(), static=list(), sources=list(), interviews=list(), modules=list(), questions=list())
                        for zinfo in zf.infolist():
                            #logmessage("Found a " + zinfo.filename)
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
                            for sec in ['templates', 'static', 'sources', 'questions']:
                                if directory.endswith('data/' + sec) and filename != 'README.md':
                                    data_files[sec].append(filename)
                                    target_filename = os.path.join(area[area_sec[sec]].directory, filename)
                                    with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                        shutil.copyfileobj(source_fp, target_fp)
                                    os.utime(target_filename, (the_time, the_time))
                            if filename == 'README.md' and len(levels) == 0:
                                readme_text = zf.read(zinfo)
                            if filename == 'setup.py' and len(levels) == 0:
                                setup_py = zf.read(zinfo)
                            elif len(levels) >= 2 and filename.endswith('.py') and filename != '__init__.py':
                                need_to_restart = True
                                data_files['modules'].append(filename)
                                target_filename = os.path.join(area['playgroundmodules'].directory, filename)
                                with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                    shutil.copyfileobj(source_fp, target_fp)
                                    os.utime(target_filename, (the_time, the_time))
                        setup_py = re.sub(r'.*setup\(', '', setup_py, flags=re.DOTALL)
                        for line in setup_py.splitlines():
                            m = re.search(r"^ *([a-z_]+) *= *\(?u?'(.*)'", line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\(?u?"(.*)"', line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
                            if m:
                                the_list = list()
                                for item in re.split(r', *', m.group(2)):
                                    inner_item = re.sub(r"'$", '', item)
                                    inner_item = re.sub(r"^u?'", '', inner_item)
                                    inner_item = re.sub(r'"+$', '', item)
                                    inner_item = re.sub(r'^u?"+', '', inner_item)
                                    the_list.append(inner_item)
                                extracted[m.group(1)] = the_list
                        info_dict = dict(readme=readme_text, interview_files=data_files['questions'], sources_files=data_files['sources'], static_files=data_files['static'], module_files=data_files['modules'], template_files=data_files['templates'], dependencies=extracted.get('install_requires', list()), dependency_links=extracted.get('dependency_links', list()), description=extracted.get('description', ''), license=extracted.get('license', ''), url=extracted.get('url', ''), version=extracted.get('version', ''))
                        package_name = re.sub(r'^docassemble\.', '', extracted.get('name', 'unknown'))
                        with open(os.path.join(area['playgroundpackages'].directory, package_name), 'w') as fp:
                            the_yaml = yaml.safe_dump(info_dict, default_flow_style=False, default_style='|')
                            fp.write(the_yaml.encode('utf8'))
                        for sec in area:
                            area[sec].finalize()
                        the_file = package_name
                #except Exception as errMess:
                    #flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        if need_to_restart:
            return redirect(url_for('restart_page', next=url_for('playground_packages', file=the_file)))
        return redirect(url_for('playground_packages', file=the_file))
    if request.method == 'GET' and 'pull' in request.args and int(request.args['pull']) == 1 and ('github_url' in request.args or 'pypi' in request.args):
        area_sec = dict(templates='playgroundtemplate', static='playgroundstatic', sources='playgroundsources', questions='playground')
        readme_text = ''
        setup_py = ''
        need_to_restart = False
        extracted = dict()
        data_files = dict(templates=list(), static=list(), sources=list(), interviews=list(), modules=list(), questions=list())
        directory = tempfile.mkdtemp()
        output = ''
        if 'github_url' in request.args:
            github_url = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['github_url'])
            output += "Doing git clone " + str(github_url) + "\n"
            try:
                output += subprocess.check_output(['git', 'clone', github_url], cwd=directory, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err:
                output += err.output
                raise DAError("playground_packages: error running git clone.  " + output)
        elif 'pypi' in request.args:
            pypi_package = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['pypi'])
            pypi_package = 'docassemble.' + re.sub(r'^docassemble\.', '', pypi_package)
            package_file = tempfile.NamedTemporaryFile(suffix='.tar.gz')
            try:
                http = httplib2.Http()
                resp, content = http.request("https://pypi.python.org/pypi/" + str(pypi_package) + "/json", "GET")
                pypi_url = None
                if int(resp['status']) == 200:
                    pypi_response = json.loads(content)
                    for file_option in pypi_response['releases'][pypi_response['info']['version']]:
                        if file_option['packagetype'] == 'sdist':
                            pypi_url = file_option['url']
                            break
                else:
                    flash(word("The package you specified could not be downloaded from PyPI."), 'error')
                    return redirect(url_for('playground_packages'))
                if pypi_url is None:
                    flash(word("The package you specified could not be downloaded from PyPI as a tar.gz file."), 'error')
                    return redirect(url_for('playground_packages'))
            except Exception as err:
                raise DAError("playground_packages: error getting information about PyPI package.  " + str(err))
            try:
                urllib.urlretrieve(pypi_url, package_file.name)
            except Exception as err:
                raise DAError("playground_packages: error downloading PyPI package.  " + str(err))
            try:
                tar = tarfile.open(package_file.name)
                tar.extractall(path=directory)
                tar.close()
            except Exception as err:
                raise DAError("playground_packages: error unpacking PyPI package.  " + str(err))
        initial_directories = len(splitall(directory)) + 1
        for root, dirs, files in os.walk(directory):
            for file in files:
                orig_file = os.path.join(root, file)
                #output += "Original file is " + orig_file + "\n"
                thefilename = os.path.join(*splitall(orig_file)[initial_directories:])
                (the_directory, filename) = os.path.split(thefilename)
                if filename.startswith('#') or filename.endswith('~'):
                    continue
                dirparts = splitall(the_directory)
                if '.git' in dirparts:
                    continue
                levels = re.findall(r'/', the_directory)
                for sec in ['templates', 'static', 'sources', 'questions']:
                    if the_directory.endswith('data/' + sec) and filename != 'README.md':
                        data_files[sec].append(filename)
                        target_filename = os.path.join(area[area_sec[sec]].directory, filename)
                        #output += "Copying " + orig_file + "\n"
                        copy_if_different(orig_file, target_filename)
                if filename == 'README.md' and len(levels) == 0:
                    with open(orig_file, 'rU') as fp:
                        readme_text = fp.read().decode('utf8')
                if filename == 'setup.py' and len(levels) == 0:
                    with open(orig_file, 'rU') as fp:
                        setup_py = fp.read().decode('utf8')
                elif len(levels) >= 1 and filename.endswith('.py') and filename != '__init__.py':
                    need_to_restart = True
                    data_files['modules'].append(filename)
                    target_filename = os.path.join(area['playgroundmodules'].directory, filename)
                    #output += "Copying " + orig_file + "\n"
                    copy_if_different(orig_file, target_filename)
        #output += "setup.py is " + str(len(setup_py)) + " characters long\n"
        setup_py = re.sub(r'.*setup\(', '', setup_py, flags=re.DOTALL)
        for line in setup_py.splitlines():
            m = re.search(r"^ *([a-z_]+) *= *\(?u?'(.*)'", line)
            if m:
                extracted[m.group(1)] = m.group(2)
            m = re.search(r'^ *([a-z_]+) *= *\(?u?"(.*)"', line)
            if m:
                extracted[m.group(1)] = m.group(2)
            m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
            if m:
                the_list = list()
                for item in re.split(r', *', m.group(2)):
                    inner_item = re.sub(r"'$", '', item)
                    inner_item = re.sub(r"^u?'", '', inner_item)
                    inner_item = re.sub(r'"+$', '', item)
                    inner_item = re.sub(r'^u?"+', '', inner_item)
                    the_list.append(inner_item)
                extracted[m.group(1)] = the_list
        info_dict = dict(readme=readme_text, interview_files=data_files['questions'], sources_files=data_files['sources'], static_files=data_files['static'], module_files=data_files['modules'], template_files=data_files['templates'], dependencies=extracted.get('install_requires', list()), dependency_links=extracted.get('dependency_links', list()), description=extracted.get('description', ''), license=extracted.get('license', ''), url=extracted.get('url', ''), version=extracted.get('version', ''))
        #output += "info_dict is set\n"
        package_name = re.sub(r'^docassemble\.', '', extracted.get('name', 'unknown'))
        if not user_can_edit_package(pkgname='docassemble.' + package_name):
            index = 1
            orig_package_name = package_name
            while index < 100 and not user_can_edit_package(pkgname='docassemble.' + package_name):
                index += 1
                package_name = orig_package_name + str(index)
        with open(os.path.join(area['playgroundpackages'].directory, package_name), 'w') as fp:
            the_yaml = yaml.safe_dump(info_dict, default_flow_style=False, default_style='|')
            fp.write(the_yaml.encode('utf8'))
        area['playgroundpackages'].finalize()
        for sec in area:
            area[sec].finalize()
        the_file = package_name
        flash(word("The package was unpacked into the Playground."), 'success')
        shutil.rmtree(directory)
        if need_to_restart:
            return redirect(url_for('restart_page', next=url_for('playground_packages', file=the_file)))
        return redirect(url_for('playground_packages', file=the_file))
    if request.method == 'POST' and form.delete.data and the_file != '' and the_file == form.file_name.data and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
        os.remove(os.path.join(area['playgroundpackages'].directory, the_file))
        area['playgroundpackages'].finalize()
        flash(word("Deleted package"), "success")
        return redirect(url_for('playground_packages'))
    if not is_new:
        pkgname = 'docassemble.' + the_file
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
        new_info = dict()
        for field in ['license', 'description', 'version', 'url', 'readme', 'dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files']:
            new_info[field] = form[field].data
        #logmessage("found " + str(new_info))
        if form.submit.data or form.download.data or form.install.data or form.pypi.data or form.github.data:
            if the_file != '':
                area['playgroundpackages'].finalize()
                if form.original_file_name.data and form.original_file_name.data != the_file:
                    old_filename = os.path.join(area['playgroundpackages'].directory, form.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                if form.pypi.data and pypi_version is not None:
                    versions = pypi_version.split(".")
                    while True:
                        versions[-1] = str(int(versions[-1]) + 1)
                        new_info['version'] = ".".join(versions)
                        if 'releases' not in pypi_info['info'] or new_info['version'] not in pypi_info['info']['releases'].keys():
                            break
                        versions = new_info['version'].split(".")
                filename = os.path.join(area['playgroundpackages'].directory, the_file)
                with open(filename, 'w') as fp:
                    the_yaml = yaml.safe_dump(new_info, default_flow_style=False, default_style = '|')
                    fp.write(the_yaml.encode('utf8'))
                area['playgroundpackages'].finalize()
                if form.download.data:
                    return redirect(url_for('create_playground_package', package=the_file))
                if form.install.data:
                    return redirect(url_for('create_playground_package', package=the_file, install='1'))
                if form.pypi.data:
                    return redirect(url_for('create_playground_package', package=the_file, pypi='1'))
                if form.github.data:
                    return redirect(url_for('create_playground_package', package=the_file, github='1', commit_message=form.commit_message.data))
                the_time = formatted_current_time()
                flash(word('The package information was saved.'), 'success')
                
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
    extra_command += upload_js() + "\n";
    extra_command += """\
      $("#daCancel").click(function(event){
        var whichButton = this;
        $("#commit_message_div").hide();
        $(".btn-lg").each(function(){
          if (this != whichButton && $(this).is(":hidden")){
            $(this).show();
          }
        });
        $("#daGitHub").html('""" + word("GitHub") + """');
        $(this).hide();
        event.preventDefault();
        return false;
      });
      $("#daGitHub").click(function(event){
        var whichButton = this;
        if ($("#commit_message").val().length == 0 || $("#commit_message_div").is(":hidden")){
          if ($("#commit_message_div").is(":visible")){
            $("#commit_message").parent().addClass("has-error");
          }
          else{
            $("#commit_message_div").show();
            $(".btn-lg").each(function(){
              if (this != whichButton && $(this).is(":visible")){
                $(this).hide();
              }
            });
            $(this).html('""" + word("Commit") + """');
            $("#daCancel").show();
          }
          $("#commit_message").focus();
          event.preventDefault();
          return false;
        }
      });
"""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    if len(editable_files):
        any_files = True
    else:
        any_files = False
    back_button = Markup('<a href="' + url_for('playground_page') + '" class="btn btn-sm navbar-btn nav-but"><i class="glyphicon glyphicon-arrow-left"></i> ' + word("Back") + '</a>')
    if pypi_message is not None:
        pypi_message = Markup(pypi_message)
    if github_message is not None:
        github_message = Markup(github_message)
    return render_template('pages/playgroundpackages.html', version_warning=None, bodyclass='adminbody', can_publish_to_pypi=can_publish_to_pypi, pypi_message=pypi_message, can_publish_to_github=can_publish_to_github, github_message=github_message, github_http=github_http, back_button=back_button, tab_title=header, page_title=header, extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/markdown/markdown.js") + '"></script>\n    ' + kbLoad + '<script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this package?") + '")){event.preventDefault();}});\n      $("#daPyPI").click(function(event){if(!confirm("' + word("Are you sure that you want to publish this package to PyPI?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("readme");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "markdown", ' + kbOpt + 'tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true, matchBrackets: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#form").trigger("checkform.areYouSure");});\n      $("#form").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#form").bind("submit", function(){daCodeMirror.save(); $("#form").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n      daCodeMirror.setOption("coverGutterNextToScrollbar", true);\n      function scrollBottom(){$("html, body").animate({ scrollTop: $(document).height() }, "slow");}\n' + extra_command + '    </script>'), header=header, upload_header=upload_header, edit_header=edit_header, description=description, form=form, fileform=fileform, files=files, file_list=file_list, userid=current_user.id, editable_files=editable_files, current_file=the_file, after_text=after_text, section_name=section_name, section_sec=section_sec, section_field=section_field, package_names=package_names, any_files=any_files), 200

def copy_if_different(source, destination):
    if (not os.path.isfile(destination)) or filecmp.cmp(source, destination) is False:
        shutil.copyfile(source, destination)

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

@app.route('/playground_redirect', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_redirect():
    key = 'da:runplayground:' + str(current_user.id)
    counter = 0
    while counter < 15:
        the_url = r.get(key)
        #logmessage("playground_redirect: key " + str(key) + " is " + str(the_url))
        if the_url is not None:
            r.delete(key)
            return redirect(the_url)
        time.sleep(1)
        counter += 1
    abort(404)

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
    
def search_js(form=None):
    if form is None:
        form = 'form'
    return """
var origPosition = null;
var searchMatches = null;

function searchReady(){
  $("#""" + form + """ input[name='search_term']").on("focus", function(event){
    origPosition = daCodeMirror.getCursor('from');
  });
  $("#""" + form + """ input[name='search_term']").change(update_search);
  $("#""" + form + """ input[name='search_term']").on("keydown", enter_search);
  $("#""" + form + """ input[name='search_term']").on("keyup", update_search);
  $("#daSearchPrevious").click(function(event){
    var query = $("#""" + form + """ input[name='search_term']").val();
    if (query.length == 0){
      clear_matches();
      daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      return;
    }
    origPosition = daCodeMirror.getCursor('from');
    var sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findPrevious();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
    }
    else{
      var lastLine = daCodeMirror.lastLine()
      var lastChar = daCodeMirror.lineInfo(lastLine).text.length
      origPosition = { line: lastLine, ch: lastChar, xRel: 1 }
      sc = daCodeMirror.getSearchCursor(query, origPosition);
      show_matches(query);
      var found = sc.findPrevious();
      if (found){
        daCodeMirror.setSelection(sc.from(), sc.to());
        scroll_to_selection();
        $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      }
      else{
        $("#""" + form + """ input[name='search_term']").addClass("search-error");
      }
    }
    event.preventDefault();
    return false;
  });
  $("#daSearchNext").click(function(event){
    var query = $("#""" + form + """ input[name='search_term']").val();
    if (query.length == 0){
      clear_matches();
      daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      return;
    }
    origPosition = daCodeMirror.getCursor('to');
    var sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findNext();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
    }
    else{
      origPosition = { line: 0, ch: 0, xRel: 1 }
      sc = daCodeMirror.getSearchCursor(query, origPosition);
      show_matches(query);
      var found = sc.findNext();
      if (found){
        daCodeMirror.setSelection(sc.from(), sc.to());
        scroll_to_selection();
        $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      }
      else{
        $("#""" + form + """ input[name='search_term']").addClass("search-error");
      }
    }
    event.preventDefault();
    return false;
  });
}

function show_matches(query){
  clear_matches();
  if (query.length == 0){
    daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
    $("#""" + form + """ input[name='search_term']").removeClass("search-error");
    return;
  }
  searchMatches = daCodeMirror.showMatchesOnScrollbar(query);
}

function clear_matches(){
  if (searchMatches != null){
    try{
      searchMatches.clear();
    }
    catch(err){}
  }
}

function scroll_to_selection(){
  daCodeMirror.scrollIntoView(daCodeMirror.getCursor('from'))
  var t = daCodeMirror.charCoords(daCodeMirror.getCursor('from'), "local").top;
  daCodeMirror.scrollTo(null, t);
}

function enter_search(event){
  if(event.keyCode == 13) {
    event.preventDefault();
    $("#daSearchNext").click();
    return false;
  }
}

function update_search(event){
  var query = $(this).val();
  if (query.length == 0){
    clear_matches();
    daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
    $(this).removeClass("search-error");
    return;
  }
  if(event.keyCode == 13) {
    event.preventDefault();
    return false;
  }
  var sc = daCodeMirror.getSearchCursor(query, origPosition);
  show_matches(query);

  var found = sc.findNext();
  if (found){
    daCodeMirror.setSelection(sc.from(), sc.to());
    scroll_to_selection();
    $(this).removeClass("search-error");
  }
  else{
    origPosition = { line: 0, ch: 0, xRel: 1 }
    sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findNext();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $(this).removeClass("search-error");
    }
    else{
      $(this).addClass("search-error");
    }
  }
}

"""
    
def variables_js(form=None):
    if form is None:
        form = 'form'
    return """
function activateVariables(){
  $(".playground-variable").on("click", function(event){
    daCodeMirror.replaceSelection($(this).data("insert"), "around");
    daCodeMirror.focus();
  });

  $(".daparenthetical").on("click", function(event){
    var reference = $(this).data("ref");
    //console.log("reference is " + reference);
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
    $("#" + target_id).slideToggle();
  });

  $(".dashowattributes").on("click", function(event){
    var basename = $(this).data('name');
    $('tr[data-parent="' + basename + '"]').each(function(){
      $(this).toggle();
    });
  });
  $(".dasearchicon").on("click", function(event){
    var query = $(this).data('name');
    if (query == null || query.length == 0){
      clear_matches();
      daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
      return;
    }
    origPosition = daCodeMirror.getCursor('to');
    $("#""" + form + """ input[name='search_term']").val(query);
    var sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findNext();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $("#form input[name='search_term']").removeClass('search-error');
    }
    else{
      origPosition = { line: 0, ch: 0, xRel: 1 }
      sc = daCodeMirror.getSearchCursor(query, origPosition);
      show_matches(query);
      var found = sc.findNext();
      if (found){
        daCodeMirror.setSelection(sc.from(), sc.to());
        scroll_to_selection();
        $("#""" + form + """ input[name='search_term']").removeClass('search-error');
      }
      else{
        $("#""" + form + """ input[name='search_term']").addClass('search-error');
      }
    }
    event.preventDefault();
    return false;
  });
}

var interviewBaseUrl = '""" + url_for('index', reset='1', cache='0', i='docassemble.playground' + str(current_user.id) + ':.yml') + """';

function updateRunLink(){
  $("#daRunButton").attr("href", interviewBaseUrl.replace('.yml', $("#daVariables").val()));
}

function fetchVars(changed){
  daCodeMirror.save();
  updateRunLink();
  $.ajax({
    type: "POST",
    url: """ + '"' + url_for('playground_variables') + '"' + """,
    data: 'csrf_token=' + $("#""" + form + """ input[name='csrf_token']").val() + '&variablefile=' + $("#daVariables").val() + '&changed=' + (changed ? 1 : 0),
    success: function(data){
      if (data.vocab_list != null){
        vocab = data.vocab_list;
      }
      if (data.variables_html != null){
        $("#daplaygroundtable").html(data.variables_html);
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'click', html: true})
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

function activatePopovers(){
  $(function () {
    $('[data-toggle="popover"]').popover({trigger: 'click', html: true})
  });
}

"""

@app.route('/playgroundvariables', methods=['POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_variables():
    playground = SavedFile(current_user.id, fix=True, section='playground')
    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f))])
    if len(files) == 0:
        return jsonify(success=False, reason=1)
    post_data = request.form.copy()
    if request.method == 'POST' and 'variablefile' in post_data:
        active_file = post_data['variablefile']
        if post_data['variablefile'] in files:
            if 'changed' in post_data and int(post_data['changed']):
                session['variablefile'] = active_file
            interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + active_file)
            interview_source.set_testing(True)
        else:
            if active_file == '':
                active_file = 'test.yml'
            content = ''
            if 'playground_content' in post_data:
                content = post_data['playground_content']
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        interview = interview_source.get_interview()
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
        variables_html, vocab_list = get_vars_in_use(interview, interview_status, debug_mode=False)
        return jsonify(success=True, variables_html=variables_html, vocab_list=vocab_list)
    return jsonify(success=False, reason=2)
    
@app.route('/playground', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_page():
    if 'ajax' in request.form:
        is_ajax = True
        use_gd = False
    else:
        is_ajax = False
        if app.config['USE_GOOGLE_DRIVE'] is False or get_gd_folder() is None:
            use_gd = False
        else:
            use_gd = True
        if request.method == 'GET' and needs_to_change_password():
            return redirect(url_for('user.change_password', next=url_for('playground_page')))
    fileform = PlaygroundUploadForm(request.form)
    form = PlaygroundForm(request.form)
    interview = None
    the_file = request.args.get('file', '')
    if request.method == 'GET':
        is_new = request.args.get('new', False)
        debug_mode = request.args.get('debug', False)
    else:
        debug_mode = False
        is_new = False
    if is_new:
        the_file = ''
    playground = SavedFile(current_user.id, fix=True, section='playground')
    #path = os.path.join(UPLOAD_DIRECTORY, 'playground', str(current_user.id))
    #if not os.path.exists(path):
    #    os.makedirs(path)
    if request.method == 'POST' and 'uploadfile' in request.files:
        the_files = request.files.getlist('uploadfile')
        if the_files:
            for up_file in the_files:
                try:
                    filename = secure_filename(up_file.filename)
                    extension, mimetype = get_ext_and_mimetype(filename)
                    if extension not in ['yml', 'yaml']:
                        flash(word("Sorry, only YAML files can be uploaded here.  To upload other types of files, use the Folders."), 'error')
                        return redirect(url_for('playground_page'))
                    filename = re.sub(r'[^A-Za-z0-9\-\_\.]+', '_', filename)
                    filename = os.path.join(playground.directory, filename)
                    up_file.save(filename)
                    try:
                        with open(filename, 'rU') as fp:
                            fp.read().decode('utf8')
                    except:
                        os.remove(filename)
                        flash(word("There was a problem reading the YAML file you uploaded.  Are you sure it is a YAML file?  File was not saved."), 'error')
                        return redirect(url_for('playground_page'))
                    playground.finalize()
                    return redirect(url_for('playground_page', file=os.path.basename(filename)))
                except Exception as errMess:
                    flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        return redirect(url_for('playground_page'))
    if request.method == 'POST' and (form.submit.data or form.run.data or form.delete.data):
        if (form.playground_name.data):
            the_file = form.playground_name.data
            the_file = re.sub(r'[^A-Za-z0-9\_\-\.]', '', the_file)
            if the_file != '':
                if not re.search(r'\.ya?ml$', the_file):
                    the_file = re.sub(r'\..*', '', the_file) + '.yml'
                filename = os.path.join(playground.directory, the_file)
                if not os.path.isfile(filename):
                    with open(filename, 'a'):
                        os.utime(filename, None)
            else:
                flash(word('You need to type in a name for the interview'), 'error')
                is_new = True
        else:
            flash(word('You need to type in a name for the interview'), 'error')
            is_new = True
    the_file = re.sub(r'[^A-Za-z0-9\_\-\.]', '', the_file)
    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f))])
    content = ''
    if the_file and not is_new and the_file not in files:
        the_file = ''
    is_default = False
    if request.method == 'GET' and not the_file and not is_new:
        if 'playgroundfile' in session and session['playgroundfile'] in files:
            the_file = session['playgroundfile']
        else:
            if 'playgroundfile' in session:
                del session['playgroundfile']
            if len(files):
                the_file = files[0]
            else:
                the_file = 'test.yml'
                is_default = True
                content = default_playground_yaml
    if the_file in files:
        session['playgroundfile'] = the_file
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
    # if request.method == 'POST' and 'variablefile' in post_data:
    #     active_file = post_data['variablefile']
    #     if post_data['variablefile'] in files:
    #         session['variablefile'] = active_file
    #         interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + active_file)
    #         interview_source.set_testing(True)
    #     else:
    #         if active_file == '':
    #             active_file = 'test.yml'
    #         content = ''
    #         if form.playground_content.data:
    #             content = form.playground_content.data
    #         interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
    #     interview = interview_source.get_interview()
    #     interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
    #     variables_html, vocab_list = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
    #     if is_ajax:
    #         return jsonify(variables_html=variables_html, vocab_list=vocab_list)
    if request.method == 'POST' and the_file != '' and form.validate():
        if form.delete.data:
            if os.path.isfile(filename):
                os.remove(filename)
                flash(word('File deleted.'), 'info')
                playground.finalize()
                if use_gd:
                    try:
                        trash_gd_file('questions', the_file)
                    except Exception as the_err:
                        logmessage("playground_page: unable to delete file on Google Drive.  " + str(the_err))
                if 'variablefile' in session and session['variablefile'] == the_file:
                    del session['variablefile']
                return redirect(url_for('playground_page'))
            else:
                flash(word('File not deleted.  There was an error.'), 'error')
        if (form.submit.data or form.run.data) and form.playground_content.data:
            if form.original_playground_name.data and form.original_playground_name.data != the_file:
                old_filename = os.path.join(playground.directory, form.original_playground_name.data)
                if not is_ajax:
                    flash(word("Changed name of interview"), 'success')
                if os.path.isfile(old_filename):
                    os.remove(old_filename)
                    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f))])
            the_time = formatted_current_time()
            with open(filename, 'w') as fp:
                fp.write(form.playground_content.data.encode('utf8'))
            # for a_file in files:
            #     docassemble.base.interview_cache.clear_cache('docassemble.playground' + str(current_user.id) + ':' + a_file)
            #     a_filename = os.path.join(playground.directory, a_file)
            #     if a_filename != filename and os.path.isfile(a_filename):
            #         with open(a_filename, 'a'):
            #             os.utime(a_filename, None)
            this_interview_string = 'docassemble.playground' + str(current_user.id) + ':' + the_file
            active_interview_string = 'docassemble.playground' + str(current_user.id) + ':' + active_file
            a_filename = os.path.join(playground.directory, active_file)
            if a_filename != filename and os.path.isfile(a_filename):
                with open(a_filename, 'a'):
                    os.utime(a_filename, None)
            playground.finalize()
            docassemble.base.interview_cache.clear_cache(this_interview_string)
            if active_interview_string != this_interview_string:
                docassemble.base.interview_cache.clear_cache(active_interview_string)
            if not form.submit.data:
                the_url = url_for('index', reset=1, i=this_interview_string)
                key = 'da:runplayground:' + str(current_user.id)
                #logmessage("Setting key " + str(key) + " to " + str(the_url))
                pipe = r.pipeline()
                pipe.set(key, the_url)
                pipe.expire(key, 12)
                pipe.execute()
            try:
                interview_source = docassemble.base.parse.interview_source_from_string(active_interview_string)
                interview_source.set_testing(True)
                interview = interview_source.get_interview()
                interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
                variables_html, vocab_list = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
                if form.submit.data:
                    flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.', 'success', is_ajax=is_ajax)
                else:
                    flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Running in other tab.'), message_type='success', is_ajax=is_ajax)
            except:
                variables_html = None
                flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Problem detected.'), message_type='error', is_ajax=is_ajax)
            if is_ajax:
                return jsonify(variables_html=variables_html, vocab_list=vocab_list, flash_message=flash_message)
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
    variables_html, vocab_list = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
    pulldown_files = list(files)
    define_examples()
    if is_fictitious or is_new or is_default:
        new_active_file = word('(New file)')
        if new_active_file not in pulldown_files:
            pulldown_files.insert(0, new_active_file)
        if is_fictitious:
            active_file = new_active_file
    ajax = """
var exampleData;
var originalFileName = """ + repr(str(the_file)) + """;
var isNew = """ + repr(str(is_new)) + """;
var vocab = """ + json.dumps(vocab_list) + """;

""" + variables_js() + """

""" + search_js() + """

function activateExample(id, scroll){
  var info = exampleData[id];
  $("#example-source").html(info['html']);
  $("#example-source-before").html(info['before_html']);
  $("#example-source-after").html(info['after_html']);
  $("#example-image-link").attr("href", info['interview']);
  $("#example-image").attr("src", info['image']);
  if (info['documentation'] != null){
    $("#example-documentation-link").attr("href", info['documentation']);
    $("#example-documentation-link").removeClass("example-hidden");
    //$("#example-documentation-link").slideUp();
  }
  else{
    $("#example-documentation-link").addClass("example-hidden");
    //$("#example-documentation-link").slideDown();
  }
  $(".example-list").addClass("example-hidden");
  $(".example-link").removeClass("example-active");
  $(".example-link").parent().removeClass("active");
  $(".example-link").each(function(){
    if ($(this).data("example") == id){
      $(this).addClass("example-active");
      $(this).parent().addClass("active");
      $(this).parents(".example-list").removeClass("example-hidden");
      if (scroll){
        setTimeout(function(){
          //console.log($(this).parents("li").last()[0].offsetTop);
          //console.log($(this).parents("li").last().parent()[0].offsetTop);
          $(".example-active").parents("ul").last().scrollTop($(".example-active").parents("li").last()[0].offsetTop);
        }, 0);
      }
      //$(this).parents(".example-list").slideDown();
    }
  });
  $("#hide-full-example").addClass("invisible");
  if (info['has_context']){
    $("#show-full-example").removeClass("invisible");
  }
  else{
    $("#show-full-example").addClass("invisible");
  }
  $("#example-source-before").addClass("invisible");
  $("#example-source-after").addClass("invisible");
}

function saveCallback(data){
  if ($("#flash").length){
    $("#flash").html(data.flash_message);
  }
  else{
    $("#main").prepend('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">' + data.flash_message + '</div>');
  }
  if (data.vocab_list != null){
    vocab = data.vocab_list;
  }
  if (data.variables_html != null){
    $("#daplaygroundtable").html(data.variables_html);
    activateVariables();
    $("#form").trigger("reinitialize.areYouSure");
    $(function () {
      $('[data-toggle="popover"]').popover({trigger: 'click', html: true});
    });
  }
}

$( document ).ready(function() {
  variablesReady();
  searchReady();
  $("#daRun").click(function(event){
    if (originalFileName != $("#playground_name").val()){
      $("#form button[name='submit']").click();
      event.preventDefault();
      return false;
    }
    daCodeMirror.save();
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&run=Save+and+Run&ajax=1',
      success: function(data){
        saveCallback(data);
      },
      dataType: 'json'
    });
    //event.preventDefault();
    return true;
  });
  $("#form button[name='submit']").click(function(event){
    daCodeMirror.save();
    if (isNew == "True" || originalFileName != $("#playground_name").val() || $("#playground_name").val().trim() == ""){
      return true;
    }
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&submit=Save&ajax=1',
      success: function(data){
        saveCallback(data);
        setTimeout(function(){
          $("#flash .alert-success").hide(300, function(){
            $(self).remove();
          });
        }, 3000);
      },
      dataType: 'json'
    });
    event.preventDefault();
    return false;
  });

  $(".example-link").on("click", function(){
    var id = $(this).data("example");
    activateExample(id, false);
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
      //$(".example-list").slideUp();
      var new_link = $(this).parent().find("a.example-link").first();
      if (new_link.length){
        var id = new_link.data("example");
        activateExample(id, true);
      }
    }
  });

  activatePopovers();

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
  activateVariables();
  updateRunLink();
  origPosition = daCodeMirror.getCursor();
});
"""
    if len(files):
        any_files = True
    else:
        any_files = False
    cm_setup = """
    <script>
      var word_re = /[\w$]+/
      CodeMirror.registerHelper("hint", "yaml", function(editor, options){
        var cur = editor.getCursor(), curLine = editor.getLine(cur.line);
        var end = cur.ch, start = end;
        while (start && word_re.test(curLine.charAt(start - 1))) --start;
        var curWord = start != end && curLine.slice(start, end);
        var list = [];
        if (curWord){
          var n = vocab.length;
          for (var i = 0; i < n; ++i){
            if (vocab[i].indexOf(curWord) == 0){
              list.push(vocab[i]);
            }
          }
        }
        return {list: list, from: CodeMirror.Pos(cur.line, start), to: CodeMirror.Pos(cur.line, end)};
      });""" + upload_js() + """
    </script>"""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    return render_template('pages/playground.html', version_warning=None, bodyclass='adminbody', use_gd=use_gd, userid=current_user.id, page_title=word("Playground"), tab_title=word("Playground"), extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/hint/show-hint.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/hint/show-hint.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    ' + kbLoad + '<script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>' + cm_setup + '\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this playground file?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("playground_content");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", ' + kbOpt + 'tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true, matchBrackets: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#form").trigger("checkform.areYouSure");});\n      $("#form").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#form").bind("submit", function(){daCodeMirror.save(); $("#form").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setSize(null, "400px");\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }, "Ctrl-Space": "autocomplete" });\n      daCodeMirror.setOption("coverGutterNextToScrollbar", true);\n' + indent_by(ajax, 6) + '\n      exampleData = JSON.parse(atob("' + pg_ex['encoded_data_dict'] + '"));\n      activateExample("' + str(pg_ex['pg_first_id'][0]) + '", false);\n    </script>'), form=form, fileform=fileform, files=files, any_files=any_files, pulldown_files=pulldown_files, current_file=the_file, active_file=active_file, content=content, variables_html=Markup(variables_html), example_html=pg_ex['encoded_example_html'], interview_path=interview_path, is_new=str(is_new)), 200

# nameInfo = ' + str(json.dumps(vars_in_use['name_info'])) + ';

# def mydump(data_dict):
#     output = ""
#     for key, val in data_dict.iteritems():
#         output += "      exampleData[" + str(repr(key)) + "] = " + str(json.dumps(val)) + "\n"
#     return output

@app.route('/packages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def package_page():
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('interview_list')))
    return render_template('pages/packages.html', version_warning=version_warning, bodyclass='adminbody', tab_title=word("Package Management"), page_title=word("Package Management")), 200

@app.errorhandler(Exception)
def server_error(the_error):
    errmess = unicode(type(the_error).__name__) + ": " + unicode(the_error)
    if isinstance(the_error, DAError):
        the_trace = None
        logmessage(errmess)
    else:
        the_trace = traceback.format_exc()
        logmessage(the_trace)
    if isinstance(the_error, DAError):
        error_code = the_error.error_code
    else:
        error_code = 501
    flask_logtext = []
    if os.path.exists(LOGFILE):
        with open(LOGFILE) as the_file:
            for line in the_file:
                if re.match('Exception', line):
                    flask_logtext = []
                flask_logtext.append(line)
    if re.search(r'\n', errmess):
        errmess = '<pre>' + errmess + '</pre>'
    else:
        errmess = '<blockquote>' + errmess + '</blockquote>'
    return render_template('pages/501.html', version_warning=None, tab_title=word("Error"), page_title=word("Error"), error=errmess, logtext=str(the_trace)), error_code

# @app.route('/testpost', methods=['GET', 'POST'])
# def test_post():
#     errmess = "Hello, " + str(request.method) + "!"
#     is_redir = request.args.get('redir', None)
#     if is_redir or request.method == 'GET':
#         return render_template('pages/testpost.html', error=errmess), 200
#     newargs = dict(request.args)
#     newargs['redir'] = '1'
#     logtext = url_for('test_post', **newargs)
#     #return render_template('pages/testpost.html', error=errmess, logtext=logtext), 200
#     return redirect(logtext, code=307)

@app.route('/packagestatic/<package>/<filename>', methods=['GET'])
def package_static(package, filename):
    the_file = docassemble.base.functions.package_data_filename(str(package) + ':data/static/' + str(filename))
    if the_file is None:
        abort(404)
    extension, mimetype = get_ext_and_mimetype(the_file)
    response = send_file(the_file, mimetype=str(mimetype))
    return(response)

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
    response = send_file(the_file, as_attachment=True, mimetype='text/plain', attachment_filename=filename, cache_timeout=0)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return(response)

@app.route('/logs', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def logs():
    form = LogForm(request.form)
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
            files = [f for f in content.split("\n") if f != '' and f is not None]
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
    return render_template('pages/logs.html', version_warning=version_warning, bodyclass='adminbody', tab_title=word("Logs"), page_title=word("Logs"), form=form, files=files, current_file=the_file, content=content, default_filter_string=default_filter_string), 200

@app.route('/reqdev', methods=['GET', 'POST'])
@login_required
def request_developer():
    from docassemble.webapp.users.forms import RequestDeveloperForm
    form = RequestDeveloperForm(request.form)
    recipients = list()
    if request.method == 'POST':
        for user in UserModel.query.filter_by(active=True).all():
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
                da_send_mail(msg)
                flash(word('Your request was submitted.'), 'success')
            except:
                flash(word('We were unable to submit your request.'), 'error')
        return redirect(url_for('interview_list'))
    return render_template('users/request_developer.html', version_warning=None, bodyclass='adminbody', tab_title=word("Developer Access"), page_title=word("Developer Access"), form=form)

def docx_variable_fix(variable):
    variable = re.sub(r'\\', '', variable)
    variable = re.sub(r'^([A-Za-z\_][A-Za-z\_0-9]*).*', r'\1', variable)
    return variable

@app.route('/utilities', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def utilities():
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
            result = dict()
            result[language] = dict()
            existing = docassemble.base.functions.word_collection.get(language, dict())
            if 'google' in daconfig and 'api key' in daconfig['google'] and daconfig['google']['api key']:
                from googleapiclient.discovery import build
                try:
                    service = build('translate', 'v2',
                                    developerKey=daconfig['google']['api key'])
                    use_google_translate = True
                except:
                    logmessage("Attempt to call Google Translate failed")
                    use_google_translate = False
            else:
                use_google_translate = False
            for the_word in base_words:
                if the_word in existing and existing[the_word] is not None:
                    result[language][the_word] = existing[the_word]
                    continue
                if use_google_translate:
                    try:
                        resp = service.translations().list(
                            source='en',
                            target=language,
                            q=[the_word]
                        ).execute()
                    except Exception as errstr:
                        logmessage("Translation failed: " + str(errstr))
                        resp = None
                    if type(resp) is dict and u'translations' in resp and type(resp[u'translations']) is list and len(resp[u'translations']) and type(resp[u'translations'][0]) is dict and 'translatedText' in resp[u'translations'][0]:
                        result[language][the_word] = re.sub(r'&#39;', r"'", resp['translations'][0]['translatedText'])
                    else:
                        result[language][the_word] = 'XYZNULLXYZ'
                else:
                    result[language][the_word] = 'XYZNULLXYZ'
                    uses_null = True
            word_box = ruamel.yaml.safe_dump(result, default_flow_style=False, default_style = '"', allow_unicode=True, width=1000).decode('utf8')
            word_box = re.sub(r'"XYZNULLXYZ"', r'Null', word_box)
        if 'pdfdocxfile' in request.files and request.files['pdfdocxfile'].filename:
            filename = secure_filename(request.files['pdfdocxfile'].filename)
            extension, mimetype = get_ext_and_mimetype(filename)
            if mimetype == 'application/pdf':
                file_type = 'pdf'
                pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=True)
                the_file = request.files['pdfdocxfile']
                the_file.save(pdf_file.name)
                fields = docassemble.base.pdftk.read_fields(pdf_file.name)
                if fields is None:
                    fields_output = word("Error: no fields could be found in the file")
                else:
                    fields_output = "---\nquestion: " + word("Here is your document.") + "\nevent: " + 'some_event' + "\nattachment:" + "\n  - name: " + os.path.splitext(the_file.filename)[0] + "\n    filename: " + os.path.splitext(the_file.filename)[0] + "\n    pdf template file: " + the_file.filename + "\n    fields:\n"
                    for field, default, pageno, rect, field_type in fields:
                        fields_output += '      "' + field + '": ' + default + "\n"
                    fields_output += "---"
            elif mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                file_type = 'docx'
                docx_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".docx", delete=True)
                the_file = request.files['pdfdocxfile']
                the_file.save(docx_file.name)
                result_file = word_to_markdown(docx_file.name, 'docx')
                if result_file is None:
                    fields_output = word("Error: no fields could be found in the file")
                else:
                    with open(result_file.name, 'rU') as fp:
                        result = fp.read()
                    fields = set()
                    for variable in re.findall(r'{{ *([^\} ]+) *}}', result):
                        fields.add(docx_variable_fix(variable))
                    for variable in re.findall(r'{%[a-z]* for [A-Za-z\_][A-Za-z0-9\_]* in *([^\} ]+) *%}', result):
                        fields.add(docx_variable_fix(variable))
                    if len(fields):
                        fields_output = "---\nquestion: " + word("Here is your document.") + "\nevent: " + 'some_event' + "\nattachment:" + "\n  - name: " + os.path.splitext(the_file.filename)[0] + "\n    filename: " + os.path.splitext(the_file.filename)[0] + "\n    docx template file: " + the_file.filename + "\n    fields:\n"
                        for field in fields:
                            fields_output += '      "' + field + '": ' + "Something\n"
                        fields_output += "---"
                    else:
                        fields_output = word("Error: no fields could be found in the file")
    return render_template('pages/utilities.html', version_warning=version_warning, bodyclass='adminbody', extra_css=Markup('\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>\n    <script>$("#pdfdocxfile").fileinput();</script>'), tab_title=word("Utilities"), page_title=word("Utilities"), form=form, fields=fields_output, word_box=word_box, uses_null=uses_null, file_type=file_type)

# @app.route('/save', methods=['GET', 'POST'])
# def save_for_later():
#     if current_user.is_authenticated and not current_user.is_anonymous:
#         return render_template('pages/save_for_later.html', interview=sdf)
#     secret = request.cookies.get('secret', None)

@app.route('/after_reset', methods=['GET', 'POST'])
def after_reset():
    #logmessage("after_reset")
    response = redirect(url_for('user.login'))
    if 'newsecret' in session:
        #logmessage("after_reset: fixing cookie")
        response.set_cookie('secret', session['newsecret'])
        del session['newsecret']
    return response

# @app.before_request
# def reset_thread_local():
#     docassemble.base.functions.reset_thread_local()

# @app.after_request
# def remove_temporary_files(response):
#     docassemble.base.functions.close_files()
#     return response

def needs_to_change_password():
    if not current_user.has_role('admin'):
        return False
    #logmessage("needs_to_change_password: starting")
    if app.user_manager.verify_password('password', current_user):
        flash(word("Your password is insecure and needs to be changed"), "warning")
        return True
    #logmessage("needs_to_change_password: ending")
    return False

@app.route('/interviews', methods=['GET', 'POST'])
@login_required
def interview_list():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    if 'newsecret' in session:
        #logmessage("interview_list: fixing cookie")
        response = redirect(url_for('interview_list'))
        response.set_cookie('secret', session['newsecret'])
        del session['newsecret']
        return response
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('interview_list')))
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    #logmessage("interview_list: secret is " + str(secret))
    if 'action' in request.args and request.args.get('action') == 'deleteall':
        subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), UserDict.filename, UserDict.key).group_by(UserDict.filename, UserDict.key).subquery()
        interview_query = db.session.query(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted).filter(UserDictKeys.user_id == current_user.id).join(subq, and_(subq.c.filename == UserDictKeys.filename, subq.c.key == UserDictKeys.key)).join(UserDict, and_(UserDict.indexno == subq.c.indexno, UserDict.key == UserDictKeys.key, UserDict.filename == UserDictKeys.filename)).group_by(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted)
        sessions_to_delete = list()
        for interview_info in interview_query:
            sessions_to_delete.append((interview_info.key, interview_info.filename))
        if len(sessions_to_delete):
            for session_id, yaml_filename in sessions_to_delete:
                manual_checkout(manual_session_id=session_id, manual_filename=yaml_filename)
                obtain_lock(session_id, yaml_filename)
                reset_user_dict(session_id, yaml_filename)
                release_lock(session_id, yaml_filename)
            flash(word("Deleted interviews"), 'success')
        return redirect(url_for('interview_list'))
    elif 'action' in request.args and request.args.get('action') == 'delete':
        yaml_file = request.args.get('filename', None)
        session_id = request.args.get('session', None)
        if yaml_file is not None and session_id is not None:
            manual_checkout(manual_session_id=session_id, manual_filename=yaml_file)
            obtain_lock(session_id, yaml_file)
            reset_user_dict(session_id, yaml_file)
            release_lock(session_id, yaml_file)
            flash(word("Deleted interview"), 'success')
            return redirect(url_for('interview_list'))
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), UserDict.filename, UserDict.key).group_by(UserDict.filename, UserDict.key).subquery()
    interview_query = db.session.query(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted).filter(UserDictKeys.user_id == current_user.id).join(subq, and_(subq.c.filename == UserDictKeys.filename, subq.c.key == UserDictKeys.key)).join(UserDict, and_(UserDict.indexno == subq.c.indexno, UserDict.key == UserDictKeys.key, UserDict.filename == UserDictKeys.filename)).group_by(UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted)
    #logmessage(str(interview_query))
    interviews = list()
    for interview_info in interview_query:
        is_valid = True
        try:
            interview = docassemble.base.interview_cache.get_interview(interview_info.filename)
            if len(interview.metadata):
                metadata = interview.metadata[0]
                interview_title = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
            else:
                interview_title = word('Untitled')
        except:
            logmessage("interview_list: unable to load interview file " + interview_info.filename)
            metadata = dict()
            metadata['title'] = word('Error: interview not found')
            interview_title = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
            is_valid = False
        #logmessage("Found old interview with title " + interview_title)
        if interview_info.encrypted:
            try:
                dictionary = decrypt_dictionary(interview_info.dictionary, secret)
            except:
                logmessage("interview_list: unable to decrypt dictionary with secret " + str(secret))
                dictionary = fresh_dictionary()
                metadata = dict()
                metadata['title'] = word('Error: interview cannot be decrypted')
                interview_title = metadata.get('title', metadata.get('short title', word('Untitled'))).rstrip()
                is_valid = False
        else:
            dictionary = unpack_dictionary(interview_info.dictionary)
        starttime = nice_date_from_utc(dictionary['_internal']['starttime'], timezone=the_timezone)
        modtime = nice_date_from_utc(dictionary['_internal']['modtime'], timezone=the_timezone)
        interviews.append({'interview_info': interview_info, 'dict': dictionary, 'modtime': modtime, 'starttime': starttime, 'title': interview_title, 'valid': is_valid})
    script = """<script>
      $("#deleteall").on('click', function(event){
        if (confirm('""" + word("Are you sure you want to delete all saved interviews?") + """')){
          return true;
        }
        event.preventDefault();
        return false;
      });
    </script>
"""
    return render_template('pages/interviews.html', version_warning=version_warning, extra_js=Markup(script), tab_title=word("Interviews"), page_title=word("Interviews"), numinterviews=len(interviews), interviews=sorted(interviews, key=lambda x: x['dict']['_internal']['starttime']))

def fix_secret():
    password = request.form.get('password', request.form.get('new_password', None))
    if password is not None:
        secret = str(request.cookies.get('secret', None))
        newsecret = pad_to_16(MD5Hash(data=password).hexdigest())
        if secret is None or secret != newsecret:
            #logmessage("fix_secret: calling substitute_secret")
            session['newsecret'] = substitute_secret(secret, newsecret)
    else:
        logmessage("fix_secret: password not in request")

def login_or_register(sender, user, **extra):
    fix_secret()
    if 'i' in session and 'uid' in session:
        save_user_dict_key(session['uid'], session['i'], priors=True)
        session['key_logged'] = True
    if 'tempuser' in session:
        changed = False
        for chat_entry in ChatLog.query.filter_by(temp_user_id=int(session['tempuser'])).all():
            chat_entry.user_id = user.id
            chat_entry.temp_user_id = None
            changed = True
        if changed:
            db.session.commit()
        changed = False
        for chat_entry in ChatLog.query.filter_by(temp_owner_id=int(session['tempuser'])).all():
            chat_entry.owner_id = user.id
            chat_entry.temp_owner_id = None
            changed = True
        if changed:
            db.session.commit()
        del session['tempuser']
    session['user_id'] = user.id
    if user.language and user.language != DEFAULT_LANGUAGE:
        session['language'] = user.language

@user_logged_in.connect_via(app)
def _on_user_login(sender, user, **extra):
    #logmessage("on user login")
    login_or_register(sender, user, **extra)
    #flash(word('You have signed in successfully.'), 'success')

@user_changed_password.connect_via(app)
def _on_password_change(sender, user, **extra):
    #logmessage("on password change")
    fix_secret()
    
@user_reset_password.connect_via(app)
def _on_password_reset(sender, user, **extra):
    #logmessage("on password reset")
    fix_secret()

@user_registered.connect_via(app)
def on_register_hook(sender, user, **extra):
    from docassemble.webapp.users.models import Role
    user_invite = extra.get('user_invite', None)
    if user_invite is None:
        return
    this_user_role = Role.query.filter_by(id=user_invite.role_id).first()
    if this_user_role is None:
        this_user_role = Role.query.filter_by(name='user').first()
    roles_to_remove = list()
    for role in user.roles:
        roles_to_remove.append(role)
    for role in roles_to_remove:
        user.roles.remove(role)
    user.roles.append(this_user_role)
    db.session.commit()
    login_or_register(sender, user, **extra)
    #flash(word('You have registered successfully.'), 'success')

# @user_logged_in.connect_via(app)
# def _after_login_hook(sender, user, **extra):
#     if 'i' in session and 'uid' in session:
#         save_user_dict_key(session['uid'], session['i'])
#         session['key_logged'] = True 
#     newsecret = substitute_secret(secret, pad_to_16(MD5Hash(data=password).hexdigest()))
#     # Redirect to 'next' URL
#     response = redirect(next)
#     response.set_cookie('secret', newsecret)
#     return response

# @app.teardown_appcontext
# def close_db(error):
#     if hasattr(db, 'engine'):
#         db.engine.dispose()

# @app.route('/webrtc')
# def webrtc():
#     return render_template('pages/webrtc.html', tab_title=word("WebRTC"), page_title=word("WebRTC"))

# @app.route('/webrtc_token', methods=['GET'])
# @csrf.exempt
# def webrtc_token():
#     if twilio_config is None:
#         logmessage("webrtc_token: could not get twilio configuration")
#         return
#     account_sid = twilio_config['name']['default'].get('account sid', None)
#     auth_token = twilio_config['name']['default'].get('auth token', None)
#     application_sid = twilio_config['name']['default'].get('app sid', None)

#     logmessage("webrtc_token: account sid is " + str(account_sid) + "; auth_token is " + str(auth_token) + "; application_sid is " + str(application_sid))

#     identity = 'testuser2'

#     capability = TwilioCapability(account_sid, auth_token)
#     capability.allow_client_outgoing(application_sid)
#     capability.allow_client_incoming(identity)
#     token = capability.generate()

#     return jsonify(identity=identity, token=token)

@app.route("/voice", methods=['POST', 'GET'])
@csrf.exempt
def voice():
    resp = twilio.twiml.Response()
    if twilio_config is None:
        logmessage("voice: ignoring call to voice because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if 'voice' not in twilio_config['name']['default'] or twilio_config['name']['default']['voice'] in [False, None]:
        logmessage("voice: ignoring call to voice because voice feature not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("voice: request to voice did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    for item in request.form:
        logmessage("voice: item " + str(item) + " is " + str(request.form[item]))
    with resp.gather(action=daconfig.get('root', '/') + "digits", finishOnKey='#', method="POST", timeout=10, numDigits=5) as g:
        g.say(word("Please enter the four digit code, followed by the pound sign."))

    # twilio_config = daconfig.get('twilio', None)
    # if twilio_config is None:
    #     logmessage("Could not get twilio configuration")
    #     return
    # twilio_caller_id = twilio_config.get('number', None)
    # if "To" in request.form and request.form["To"] != '':
    #     dial = resp.dial(callerId=twilio_caller_id)
    #     if phone_pattern.match(request.form["To"]):
    #         dial.number(request.form["To"])
    #     else:
    #         dial.client(request.form["To"])
    # else:
    #     resp.say("Thanks for calling!")

    return Response(str(resp), mimetype='text/xml')

@app.route("/digits", methods=['POST', 'GET'])
@csrf.exempt
def digits():
    resp = twilio.twiml.Response()
    if twilio_config is None:
        logmessage("digits: ignoring call to digits because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("digits: request to digits did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    if "Digits" in request.form:
        the_digits = re.sub(r'[^0-9]', '', request.form["Digits"])
        logmessage("digits: got " + str(the_digits))
        phone_number = r.get('da:callforward:' + str(the_digits))
        if phone_number is None:
            resp.say(word("I am sorry.  The code you entered is invalid or expired.  Goodbye."))
            resp.hangup()
        else:
            dial = resp.dial(number=phone_number)
            r.delete('da:callforward:' + str(the_digits))
    else:
        logmessage("digits: no digits received")
        resp.say(word("No access code was entered."))
        resp.hangup()
    return Response(str(resp), mimetype='text/xml')

def sms_body(phone_number, body='question', config='default'):
    if twilio_config is None:
        raise DAError("sms_body: Twilio not enabled")
    if config not in twilio_config['name']:
        raise DAError("sms_body: specified config value, " + str(config) + ", not in Twilio configuration")
    tconfig = twilio_config['name'][config]
    if 'sms' not in tconfig or tconfig['sms'] in [False, None, 0]:
        raise DAError("sms_body: sms feature is not enabled in Twilio configuration")
    if 'account sid' not in tconfig:
        raise DAError("sms_body: account sid not in Twilio configuration")
    if 'number' not in tconfig:
        raise DAError("sms_body: phone number not in Twilio configuration")
    if 'doing_sms' in session:
        raise DAError("Cannot call sms_body from within sms_body")
    form = dict(To=tconfig['number'], From=phone_number, Body=body, AccountSid=tconfig['account sid'])
    base_url = request.base_url
    url_root = request.url_root
    tbackup = docassemble.base.functions.backup_thread_variables()
    sbackup = backup_session()
    session['doing_sms'] = True
    resp = do_sms(form, base_url, url_root, save=False)
    restore_session(sbackup)
    docassemble.base.functions.restore_thread_variables(tbackup)
    if resp is None or len(resp.verbs) == 0 or len(resp.verbs[0].verbs) == 0:
        return None
    #return 'snooobar'
    return resp.verbs[0].verbs[0].body

def favicon_file(filename):
    the_dir = docassemble.base.functions.package_data_filename(daconfig.get('favicon', 'docassemble.webapp:data/static/favicon'))
    if the_dir is None or not os.path.isdir(the_dir):
        logmessage("Could not find favicon directory")
        abort(404)
    the_file = os.path.join(the_dir, filename)
    if not os.path.isfile(the_file):
        abort(404)
    extension, mimetype = get_ext_and_mimetype(the_file)
    response = send_file(the_file, mimetype=mimetype)
    return(response)

@app.route("/favicon.ico", methods=['GET'])
def favicon():
    return(favicon_file('favicon.ico'))
@app.route("/apple-touch-icon.png", methods=['GET'])
def apple_touch_icon():
    return(favicon_file('apple-touch-icon.png'))
@app.route("/favicon-32x32.png", methods=['GET'])
def favicon_md():
    return(favicon_file('favicon-32x32.png'))
@app.route("/favicon-16x16.png", methods=['GET'])
def favicon_sm():
    return(favicon_file('favicon-16x16.png'))
@app.route("/manifest.json", methods=['GET'])
def favicon_manifest_json():
    return(favicon_file('manifest.json'))
@app.route("/safari-pinned-tab.svg", methods=['GET'])
def favicon_safari_pinned_tab():
    return(favicon_file('safari-pinned-tab.svg'))
@app.route("/android-chrome-192x192.png", methods=['GET'])
def favicon_android_md():
    return(favicon_file('android-chrome-192x192.png'))
@app.route("/android-chrome-512x512.png", methods=['GET'])
def favicon_android_lg():
    return(favicon_file('android-chrome-512x512.png'))
@app.route("/mstile-150x150.png", methods=['GET'])
def favicon_mstile():
    return(favicon_file('mstile-150x150.png'))
@app.route("/browserconfig.xml", methods=['GET'])
def favicon_browserconfig():
    return(favicon_file('browserconfig.xml'))

@app.route("/robots.txt", methods=['GET'])
def robots():
    the_file = docassemble.base.functions.package_data_filename(daconfig.get('robots', 'docassemble.webapp:data/static/robots.txt'))
    if the_file is None:
        abort(404)
    response = send_file(the_file, mimetype='text/plain')
    return(response)

@app.route("/sms", methods=['POST'])
@csrf.exempt
def sms():
    #logmessage("Received: " + str(request.form))
    form = request.form
    base_url = request.base_url
    url_root = request.url_root
    resp = do_sms(form, base_url, url_root)
    return Response(str(resp), mimetype='text/xml')

def do_sms(form, base_url, url_root, config='default', save=True):
    resp = twilio.twiml.Response()
    special_messages = list()
    if twilio_config is None:
        logmessage("do_sms: ignoring message to sms because Twilio not enabled")
        return resp
    if "AccountSid" not in form or form["AccountSid"] not in twilio_config['account sid']:
        logmessage("do_sms: request to sms did not authenticate")
        return resp
    if "To" not in form or form["To"] not in twilio_config['number']:
        logmessage("do_sms: request to sms ignored because recipient number " + str(form.get('To', None)) + " not in configuration, " + str(twilio_config))
        return resp
    tconfig = twilio_config['number'][form["To"]]
    if 'sms' not in tconfig or tconfig['sms'] in [False, None, 0]:
        logmessage("do_sms: ignoring message to sms because SMS not enabled")
        return resp
    if "From" not in form or not re.search(r'[0-9]', form["From"]):
        logmessage("do_sms: request to sms ignored because unable to determine caller ID")
        return resp
    if "Body" not in form:
        logmessage("do_sms: request to sms ignored because message had no content")
        return resp
    inp = form['Body'].strip()
    #logmessage("Received >" + inp + "<")
    key = 'da:sms:client:' + form["From"] + ':server:' + tconfig['number']
    #logmessage("Searching for " + key)
    sess_contents = r.get(key)
    if sess_contents is None:
        logmessage("Nothing found")
        yaml_filename = tconfig.get('default interview', default_yaml_filename)
        if 'dispatch' in tconfig and type(tconfig['dispatch']) is dict:
            if inp.lower() in tconfig['dispatch']:
                yaml_filename = tconfig['dispatch'][inp.lower()]
                #logmessage("do_sms: using interview from dispatch: " + str(yaml_filename))
        if yaml_filename is None:
            logmessage("do_sms: request to sms ignored because no interview could be determined")
            return resp
        secret = random_string(16)
        uid = get_unique_name(yaml_filename, secret)
        new_temp_user = TempUser()
        db.session.add(new_temp_user)
        db.session.commit()
        sess_info = dict(yaml_filename=yaml_filename, uid=uid, secret=secret, number=form["From"], encrypted=True, tempuser=new_temp_user.id, user_id=None)
        r.set(key, pickle.dumps(sess_info))
        accepting_input = False
    else:
        try:        
            sess_info = pickle.loads(sess_contents)
            #logmessage("Unpickled contents: " + str(sess_info))
        except:
            #logmessage("do_sms: unable to decode session information")
            return resp
        accepting_input = True
    if inp.lower() in [word('exit'), word('quit')]:
        logmessage("do_sms: exiting")
        if save:
            reset_user_dict(sess_info['uid'], sess_info['yaml_filename'])
        r.delete(key)
        return resp
    session['uid'] = sess_info['uid']
    obtain_lock(sess_info['uid'], sess_info['yaml_filename'])
    steps, user_dict, is_encrypted = fetch_user_dict(sess_info['uid'], sess_info['yaml_filename'], secret=sess_info['secret'])
    encrypted = sess_info['encrypted']
    action = None
    action_performed = False
    while True:
        if user_dict.get('multi_user', False) is True and encrypted is True:
            encrypted = False
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                decrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if user_dict.get('multi_user', False) is False and encrypted is False:
            encrypted = True
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                encrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        interview = docassemble.base.interview_cache.get_interview(sess_info['yaml_filename'])
        if 'skip' not in user_dict['_internal']:
            user_dict['_internal']['skip'] = dict()
        if 'smsgather' in user_dict['_internal']:
            #logmessage("do_sms: need to gather " + user_dict['_internal']['smsgather'])
            sms_variable = user_dict['_internal']['smsgather']
        else:
            sms_variable = None
        # if action is not None:
        #     action_manual = True
        # else:
        #     action_manual = False
        user = None
        if sess_info['user_id'] is not None:
            user = load_user(sess_info['user_id'])
        if user is None:
            ci = dict(user=dict(is_anonymous=True, is_authenticated=False, email=None, theid=sess_info['tempuser'], the_user_id='t' + sess_info['tempuser'], roles=['user'], firstname='SMS', lastname='User', nickname=None, country=None, subdivisionfirst=None, subdivisionsecond=None, subdivisionthird=None, organization=None, timezone=None, location=None), session=sess_info['uid'], secret=sess_info['secret'], yaml_filename=sess_info['yaml_filename'], interface='sms', url=base_url, url_root=url_root, encrypted=encrypted, headers=dict(), clientip=None, sms_variable=sms_variable, skip=user_dict['_internal']['skip'], sms_sender=form["From"])
        else:
            ci = dict(user=dict(is_anonymous=False, is_authenticated=True, email=user.email, theid=user.id, the_user_id=user.id, roles=user.roles, firstname=user.first_name, lastname=user.last_name, nickname=user.nickname, country=user.country, subdivisionfirst=user.subdivisionfirst, subdivisionsecond=user.subdivisionsecond, subdivisionthird=user.subdivisionthird, organization=user.organization, timezone=user.timezone, location=None), session=sess_info['uid'], secret=sess_info['secret'], yaml_filename=sess_info['yaml_filename'], interface='sms', url=base_url, url_root=url_root, encrypted=encrypted, headers=dict(), clientip=None, sms_variable=sms_variable, skip=user_dict['_internal']['skip'])
        if action is not None:
            #logmessage("Setting action to " + str(action))
            ci.update(action)
        interview_status = docassemble.base.parse.InterviewStatus(current_info=ci)
        interview.assemble(user_dict, interview_status)
        if action is not None:
            sess_info['question'] = interview_status.question.name
            r.set(key, pickle.dumps(sess_info))
        elif 'question' in sess_info and sess_info['question'] != interview_status.question.name:
            logmessage("do_sms: blanking the input because question changed")
            if inp not in [word('?'), word('back'), word('question'), word('exit')]:
                inp = 'question'

        #logmessage("do_sms: inp is " + inp.lower() + " and steps is " + str(steps) + " and can go back is " + str(interview_status.can_go_back))
        m = re.search(r'^(' + word('menu') + '|' + word('link') + ')([0-9]+)', inp.lower())
        if m:
            #logmessage("Got " + inp)
            arguments = dict()
            selection_type = m.group(1)
            selection_number = int(m.group(2)) - 1
            links = list()
            menu_items = list()
            sms_info = as_sms(interview_status, links=links, menu_items=menu_items)
            target_url = None
            if selection_type == word('menu') and selection_number < len(menu_items):
                (target_url, label) = menu_items[selection_number]
            if selection_type == word('link') and selection_number < len(links):
                (target_url, label) = links[selection_number]
            if target_url is not None:
                uri_params = re.sub(r'^[\?]*\?', r'', target_url)
                for statement in re.split(r'&', uri_params):
                    parts = re.split(r'=', statement)
                    arguments[parts[0]] = parts[1]
            if 'action' in arguments:
                #logmessage(myb64unquote(urllib.unquote(arguments['action'])))
                action = json.loads(myb64unquote(urllib.unquote(arguments['action'])))
                #logmessage("Action is " + str(action))
                action_performed = True
                accepting_input = False
                inp = ''
                continue
            break
        if inp.lower() in [word('back')] and steps > 1 and interview_status.can_go_back:
            steps, user_dict, is_encrypted = fetch_previous_user_dict(sess_info['uid'], sess_info['yaml_filename'], secret=sess_info['secret'])
            if 'question' in sess_info:
                del sess_info['question']
                r.set(key, pickle.dumps(sess_info))
            accepting_input = False
            inp = ''
            continue
        else:
            break
    false_list = [word('no'), word('n'), word('false'), word('f')]
    true_list = [word('yes'), word('y'), word('true'), word('t')]
    inp_lower = inp.lower()
    skip_it = False
    changed = False
    if accepting_input:
        if inp_lower in [word('?')]:
            sms_info = as_sms(interview_status)
            message = ''
            if sms_info['help'] is None:
                message += word('Sorry, no help is available for this question.')
            else:
                message += sms_info['help']
            message += "\n" + word("To read the question again, type question.")
            resp.message(message)
            release_lock(sess_info['uid'], sess_info['yaml_filename'])
            if 'uid' in session:
                del session['uid']
            return resp
        if inp_lower in [word('question')]:
            accepting_input = False
    if accepting_input:
        saveas = None
        if len(interview_status.question.fields):
            question = interview_status.question
            if question.question_type == "fields":
                field = None
                next_field = None
                for the_field in interview_status.question.fields:
                    if hasattr(the_field, 'datatype') and the_field.datatype in ['html', 'note', 'script', 'css']:
                        continue
                    if the_field.number in user_dict['_internal']['skip']:
                        continue
                    if field is None:
                        field = the_field
                    elif next_field is None:
                        next_field = the_field
                    else:
                        break
                if field is None:
                    logmessage("do_sms: unclear what field is necessary!")
                    if 'smsgather' in user_dict['_internal']:
                        del user_dict['_internal']['smsgather']
                    field = interview_status.question.fields[0]
                    next_field = None
                saveas = myb64unquote(field.saveas)
            else:
                if hasattr(interview_status.question.fields[0], 'saveas'):
                    saveas = myb64unquote(interview_status.question.fields[0].saveas)
                    #logmessage("do_sms: variable to set is " + str(saveas))
                else:
                    saveas = None
                field = interview_status.question.fields[0]
                next_field = None
            if question.question_type == "settrue":
                if inp_lower in [word('ok')]:
                    data = 'True'
                else:
                    data = None
            elif question.question_type == 'signature':
                filename = 'canvas.png'
                extension = 'png'
                mimetype = 'image/png'
                temp_image_file = tempfile.NamedTemporaryFile(suffix='.' + extension)
                image = Image.new("RGBA", (200, 50))
                image.save(temp_image_file.name, 'PNG')
                saved_file = savedfile_numbered_file(filename, temp_image_file.name, yaml_file_name=sess_info['yaml_filename'], uid=sess_info['uid'])
                if inp_lower in [word('x')]:
                    the_string = saveas + " = docassemble.base.core.DAFile('" + saveas + "', filename='" + str(filename) + "', number=" + str(saved_file.file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')"
                    #logmessage("do_sms: doing " + the_string)
                    try:
                        exec('import docassemble.base.core', user_dict)
                        exec(the_string, user_dict)
                        changed = True
                        steps += 1
                    except Exception as errMess:
                        logmessage("do_sms: error: " + str(errMess))
                        special_messages.append(word("Error") + ": " + str(errMess))
                    skip_it = True
                    data = repr('')
                else:
                    data = None
            elif hasattr(field, 'datatype') and field.datatype in ["file", "files", "camera", "camcorder", "microphone"]:
                if inp_lower == word('skip') and not interview_status.extras['required'][field.number]:
                    skip_it = True
                    data = repr('')
                else:
                    files_to_process = list()
                    num_media = int(form.get('NumMedia', '0'))
                    fileindex = 0
                    while True:
                        if field.datatype == "file" and fileindex > 0:
                            break
                        if fileindex >= num_media or 'MediaUrl' + str(fileindex) not in form:
                            break
                        #logmessage("mime type is" + form.get('MediaContentType' + str(fileindex), 'Unknown'))
                        mimetype = form.get('MediaContentType' + str(fileindex), 'image/jpeg')
                        extension = re.sub(r'\.', r'', mimetypes.guess_extension(mimetype))
                        if extension == 'jpe':
                            extension = 'jpg'
                        filename = 'file' + '.' + extension
                        file_number = get_new_file_number(sess_info['uid'], filename, yaml_file_name=sess_info['yaml_filename'])
                        saved_file = SavedFile(file_number, extension=extension, fix=True)
                        the_url = form['MediaUrl' + str(fileindex)]
                        #logmessage("Fetching from >" + the_url + "<")
                        saved_file.fetch_url(the_url)
                        process_file(saved_file, saved_file.path, mimetype, extension)
                        files_to_process.append((filename, file_number, mimetype, extension))
                        fileindex += 1
                    if len(files_to_process) > 0:
                        elements = list()
                        indexno = 0
                        for (filename, file_number, mimetype, extension) in files_to_process:
                            elements.append("docassemble.base.core.DAFile('" + saveas + "[" + str(indexno) + "]', filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')")
                            indexno += 1
                        the_string = saveas + " = docassemble.base.core.DAFileList('" + saveas + "', elements=[" + ", ".join(elements) + "])"
                        logmessage("do_sms: doing " + the_string)
                        try:
                            exec('import docassemble.base.core', user_dict)
                            exec(the_string, user_dict)
                            changed = True
                            steps += 1
                        except Exception as errMess:
                            logmessage("do_sms: error: " + str(errMess))
                            special_messages.append(word("Error") + ": " + str(errMess))
                        skip_it = True
                        data = repr('')
                    else:
                        data = None
                        if interview_status.extras['required'][field.number]:
                            special_messages.append(word("You must attach a file."))
            elif question.question_type in ["yesno"] or (hasattr(field, 'datatype') and (field.datatype in ['yesno', 'yesnowide'] or (hasattr(field, 'datatype') and field.datatype == 'boolean' and (hasattr(field, 'sign') and field.sign > 0)))):
                if inp_lower in true_list:
                    data = 'True'
                elif inp_lower in false_list:
                    data = 'False'
                else:
                    data = None
            elif question.question_type in ["yesnomaybe"] or (hasattr(field, 'datatype') and (field.datatype in ['yesnomaybe', 'yesnowidemaybe'] or (field.datatype == 'threestate' and (hasattr(field, 'sign') and field.sign > 0)))):
                if inp_lower in true_list:
                    data = 'True'
                elif inp_lower in false_list:
                    data = 'False'
                else:
                    data = 'None'
            elif question.question_type in ["noyes"] or (hasattr(field, 'datatype') and (field.datatype in ['noyes', 'noyeswide'] or (field.datatype == 'boolean' and (hasattr(field, 'sign') and field.sign < 0)))):
                if inp_lower in true_list:
                    data = 'False'
                elif inp_lower in false_list:
                    data = 'True'
                else:
                    data = None
            elif question.question_type in ['noyesmaybe', 'noyesmaybe', 'noyeswidemaybe'] or (hasattr(field, 'datatype') and field.datatype == 'threestate' and (hasattr(field, 'sign') and field.sign < 0)):
                if inp_lower in true_list:
                    data = 'False'
                elif inp_lower in false_list:
                    data = 'True'
                else:
                    data = 'None'
            elif question.question_type == 'multiple_choice' or hasattr(field, 'choicetype') or (hasattr(field, 'datatype') and field.datatype in ['object', 'object_radio', 'radio', 'checkboxes', 'object_checkboxes']):
                cdata, choice_list = get_choices_with_abb(interview_status, field)
                data = None
                if hasattr(field, 'datatype') and field.datatype in ['checkboxes', 'object_checkboxes'] and saveas is not None:
                    try:
                        eval(saveas, user_dict)
                    except:
                        the_string = "import docassemble.base.core\n" + saveas + ' = docassemble.base.core.DADict(' + repr(saveas) + ')'
                        #logmessage("do_sms: doing " + the_string)
                        try:
                            exec(the_string, user_dict)
                            changed = True
                        except:
                            logmessage("do_sms: failed to create checkbox dict")
                if (inp_lower == word('skip') or (inp_lower == word('none') and hasattr(field, 'datatype') and field.datatype in ['checkboxes', 'object_checkboxes'])) and ((hasattr(field, 'disableothers') and field.disableothers) or (hasattr(field, 'datatype') and field.datatype in ['checkboxes', 'object_checkboxes']) or not (interview_status.extras['required'][field.number] or (question.question_type == 'multiple_choice' and hasattr(field, 'saveas')))):
                    if hasattr(field, 'datatype'):
                        if field.datatype in ['object', 'object_radio']:
                            skip_it = True
                            data = repr('')
                        if field.datatype in ['checkboxes', 'object_checkboxes']:
                            skip_it = True
                            data = repr('')
                            for choice in choice_list:
                                the_string = choice[1] + ' = False'
                                #logmessage("do_sms: doing " + str(the_string) + " for skipping checkboxes")
                                try:
                                    exec(the_string, user_dict)
                                    changed = True
                                except:
                                    logmessage("do_sms: failure to set checkbox with " + the_string)
                        elif field.datatype in ['integer']:
                            data = '0'
                        elif field.datatype in ['number', 'float', 'currency', 'range']:
                            data = '0.0'
                        else:
                            data = repr('')
                    else:
                        data = repr('')
                else:
                    if hasattr(field, 'datatype') and field.datatype in ['object_checkboxes']:
                        skip_it = True
                        data = repr('')
                        true_values = set()
                        for selection in re.split(r' *[,;] *', inp_lower):
                            for potential_abb, value in cdata['abblower'].iteritems():
                                if selection and selection.startswith(potential_abb):
                                    for choice in choice_list:
                                        if value == choice[0]:
                                            true_values.add(choice[1])
                        for choice in choice_list:
                            if choice[1] in true_values:
                                the_string = 'if ' + choice[2] + ' not in ' + saveas + ':\n    ' + saveas + '.append(' + choice[2] + ')'
                            else:
                                the_string = 'if ' + choice[2] + ' in ' + saveas + ':\n    ' + saveas + '.remove(' + choice[2] + ')'
                            #logmessage("do_sms: doing " + str(the_string) + " for object_checkboxes")
                            try:
                                exec(the_string, user_dict)
                                changed = True
                            except:
                                logmessage("do_sms: failure to set checkbox with " + the_string)
                    elif hasattr(field, 'datatype') and field.datatype in ['checkboxes']:
                        skip_it = True
                        data = repr('')
                        true_values = set()
                        for selection in re.split(r' *[,;] *', inp_lower):
                            for potential_abb, value in cdata['abblower'].iteritems():
                                if selection and selection.startswith(potential_abb):
                                    for choice in choice_list:
                                        if value == choice[0]:
                                            true_values.add(choice[1])
                        for choice in choice_list:
                            if choice[1] in true_values:
                                the_string = choice[1] + ' = True'
                            else:
                                the_string = choice[1] + ' = False'
                            #logmessage("do_sms: doing " + str(the_string) + " for checkboxes")
                            try:
                                exec(the_string, user_dict)
                                changed = True
                            except:
                                logmessage("do_sms: failure to set checkbox with " + the_string)
                    else:
                        #logmessage("do_sms: user selected " + inp_lower + " and data is " + str(cdata))
                        for potential_abb, value in cdata['abblower'].iteritems():
                            if inp_lower.startswith(potential_abb):
                                #logmessage("do_sms: user selected " + value)
                                for choice in choice_list:
                                    #logmessage("do_sms: considering " + choice[0])
                                    if value == choice[0]:
                                        #logmessage("do_sms: found a match")
                                        saveas = choice[1]
                                        if hasattr(field, 'datatype') and field.datatype in ['object', 'object_radio']:
                                            data = choice[2]
                                        else:
                                            data = repr(choice[2])
                                        break
                                break
            elif hasattr(field, 'datatype') and field.datatype in ['integer']:
                if inp_lower == word('skip') and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\-\.]', '', inp)
                    if data == '':
                        data = '0'
                    try:
                        the_value = eval("int(" + repr(data) + ")")
                        data = "int(" + repr(data) + ")"
                    except:
                        data = None
            elif hasattr(field, 'datatype') and field.datatype in ['range']:
                if inp_lower == word('skip') and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\-\.]', '', inp)
                    try:
                        the_value = eval("float(" + repr(data) + ")", user_dict)
                        if the_value > int(interview_status.extras['max'][field.number]) or the_value < int(interview_status.extras['min'][field.number]):
                            data = None
                    except:
                        data = None
            elif hasattr(field, 'datatype') and field.datatype in ['number', 'float', 'currency']:
                if inp_lower == word('skip') and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\-\.]', '', inp)
                    if data == '':
                        data = '0.0'
                    try:
                        the_value = eval("float(" + repr(data) + ")", user_dict)
                        data = "float(" + repr(str(data)) + ")"
                    except:
                        data = None
            else:
                if inp_lower == word('skip'):
                    if interview_status.extras['required'][field.number]:
                        data = repr(inp)
                    else:
                        data = repr('')
                        skip_it = True
                else:
                    data = repr(inp)
        else:
            data = None
        if data is None:
            logmessage("do_sms: could not process input: " + inp)
            special_messages.append(word("I do not understand what you mean by") + ' "' + inp + '"')
        else:
            the_string = saveas + ' = ' + data
            #logmessage("do_sms: doing " + str(the_string))
            #release_lock(sess_info['uid'], sess_info['yaml_filename'])
            #return resp
            try:
                if not skip_it:
                    exec(the_string, user_dict)
                    changed = True
                    if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                        #logmessage("do_sms: disabling others")
                        if 'sms_variable' in interview_status.current_info:
                            del interview_status.current_info['sms_variable']
                        if 'smsgather' in user_dict['_internal'] and user_dict['_internal']['smsgather'] == saveas:
                            #logmessage("do_sms: deleting " + user_dict['_internal']['smsgather'] + "because disable others")
                            del user_dict['_internal']['smsgather']
                if next_field is None:
                    if 'skip' in user_dict['_internal']:
                        del user_dict['_internal']['skip']
                    if 'sms_variable' in interview_status.current_info:
                        del interview_status.current_info['sms_variable']
                else:
                    user_dict['_internal']['skip'][field.number] = True
                if 'smsgather' in user_dict['_internal'] and user_dict['_internal']['smsgather'] == saveas:
                    #logmessage("do_sms: deleting " + user_dict['_internal']['smsgather'])
                    del user_dict['_internal']['smsgather']
            except:
                logmessage("do_sms: failure to set variable with " + the_string)
                release_lock(sess_info['uid'], sess_info['yaml_filename'])
                if 'uid' in session:
                    del session['uid']
                return resp
        if changed and next_field is None and question.name not in user_dict['_internal']['answers']:
            user_dict['_internal']['answered'].add(question.name)
        interview.assemble(user_dict, interview_status)
        sess_info['question'] = interview_status.question.name
        r.set(key, pickle.dumps(sess_info))
    if interview_status.question.question_type in ["restart", "exit"]:
        logmessage("do_sms: exiting because of restart or exit")
        if save:
            reset_user_dict(sess_info['uid'], sess_info['yaml_filename'])
        r.delete(key)
    else:
        if not interview_status.can_go_back:
            user_dict['_internal']['steps_offset'] = steps
        #user_dict['_internal']['answers'] = dict()
        if interview_status.question.name and interview_status.question.name in user_dict['_internal']['answers']:
            del user_dict['_internal']['answers'][interview_status.question.name]
        #logmessage("do_sms: " + as_sms(interview_status))
        #twilio_client = TwilioRestClient(tconfig['account sid'], tconfig['auth token'])
        #message = twilio_client.messages.create(to=form["From"], from_=form["To"], body=as_sms(interview_status))
        #logmessage("calling as_sms")
        sms_info = as_sms(interview_status)
        qoutput = sms_info['question']
        if sms_info['next'] is not None:
            #logmessage("do_sms: next variable is " + sms_info['next'])
            user_dict['_internal']['smsgather'] = sms_info['next']
        if (accepting_input or changed or action_performed or sms_info['next'] is not None) and save:
            save_user_dict(sess_info['uid'], user_dict, sess_info['yaml_filename'], secret=sess_info['secret'], encrypt=encrypted, changed=changed)
        for special_message in special_messages:
            qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + special_message + 'XXXXMESSAGE_AREAXXXX', qoutput)
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', '', qoutput)
        if user_dict.get('multi_user', False) is True and encrypted is True:
            encrypted = False
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                decrypt_session(secret, user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if user_dict.get('multi_user', False) is False and encrypted is False:
            encrypted = True
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                encrypt_session(secret, user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if len(interview_status.attachments) > 0:
            with resp.message(qoutput) as m:
                media_count = 0
                for attachment in interview_status.attachments:
                    if media_count >= 9:
                        break
                    for doc_format in attachment['formats_to_use']:
                        if media_count >= 9:
                            break
                        if doc_format not in ['pdf', 'rtf']:
                            continue
                        filename = attachment['filename'] + '.' + doc_format
                        saved_file = savedfile_numbered_file(filename, attachment['file'][doc_format], yaml_file_name=sess_info['yaml_filename'], uid=sess_info['uid'])
                        url = re.sub(r'/$', r'', url_root) + url_for('serve_stored_file', uid=sess_info['uid'], number=saved_file.file_number, filename=attachment['filename'], extension=doc_format)
                        #logmessage('sms: url is ' + str(url))
                        m.media(url)
                        media_count += 1
        else:
            resp.message(qoutput)
    release_lock(sess_info['uid'], sess_info['yaml_filename'])
    #logmessage(str(form))
    if 'uid' in session:
        del session['uid']
    return resp

def retrieve_email(email_id):
    email = Email.query.filter_by(id=email_id).first()
    if email is None:
        raise DAError("E-mail did not exist")
    short_record = Shortener.query.filter_by(short=email.short).first()
    if short_record.user_id is not None:
        user = UserModel.query.filter_by(id=short_record.user_id, active=True).first()
    else:
        user = None
    if short_record is None:
        raise DAError("Short code did not exist")
    return get_email_obj(email, short_record, user)

class AddressEmail(object):
    def __str__(self):
        return str(self.address)
    def __unicode__(self):
        return unicode(self.address)

def retrieve_emails(**pargs):
    key = pargs.get('key', None)
    index = pargs.get('index', None)
    if key is None and index is not None:
        raise DAError("retrieve_emails: if you provide an index you must provide a key")
    if 'i' in pargs:
        yaml_filename = pargs['i']
    else:
        yaml_filename = session.get('i', None)
    if 'uid' in pargs:
        uid = pargs['uid']
    else:
        uid = session.get('uid', None)
    if 'user_id' in pargs:
        user_id = pargs['user_id']
        temp_user_id = None
    elif 'temp_user_id' in pargs:
        user_id = None
        temp_user_id = pargs['temp_user_id']
    elif current_user.is_anonymous:
        user_id = None
        temp_user_id = session.get('tempuser', None)
    else:
        user_id = current_user.id
        temp_user_id = None
    user_cache = user_id_dict()
    results = list()
    if key is None:
        the_query = Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id).order_by(Shortener.modtime)
    else:
        if index is None:
            the_query = Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key).order_by(Shortener.modtime)
        else:
            the_query = Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key, index=index).order_by(Shortener.modtime)
    for record in the_query:
        result_for_short = AddressEmail()
        result_for_short.address = record.short
        result_for_short.key = record.key
        result_for_short.index = record.index
        result_for_short.emails = list()
        if record.user_id is not None:
            user = user_cache[record.user_id]
            result_for_short.owner = user.email
        else:
            user = None
            result_for_short.owner = None
        for email in Email.query.filter_by(short=record.short).order_by(Email.datetime_received):
            result_for_short.emails.append(get_email_obj(email, record, user))
        results.append(result_for_short)
    return results

def get_email_obj(email, short_record, user):
    email_obj = DAEmail(short=email.short)
    email_obj.key = short_record.key
    email_obj.index = short_record.index
    email_obj.initializeAttribute('to_address', DAEmailRecipientList, json.loads(email.to_addr), gathered=True)
    email_obj.initializeAttribute('cc_address', DAEmailRecipientList, json.loads(email.cc_addr), gathered=True)
    email_obj.initializeAttribute('from_address', DAEmailRecipient, **json.loads(email.from_addr))
    email_obj.initializeAttribute('reply_to', DAEmailRecipient, **json.loads(email.reply_to_addr))
    email_obj.initializeAttribute('return_path', DAEmailRecipient, **json.loads(email.return_path_addr))
    email_obj.subject = email.subject
    email_obj.datetime_message = email.datetime_message
    email_obj.datetime_received = email.datetime_received
    email_obj.initializeAttribute('attachment', DAFileList, gathered=True)
    if user is None:
        email_obj.address_owner = None
    else:
        email_obj.address_owner = user.email
    for attachment_record in EmailAttachment.query.filter_by(email_id=email.id).order_by(EmailAttachment.index):
        #sys.stderr.write("Attachment record is " + str(attachment_record.id) + "\n")
        upload = Uploads.query.filter_by(indexno=attachment_record.upload).first()
        if upload is None:
            continue
        #sys.stderr.write("Filename is " + upload.filename + "\n")
        saved_file_att = SavedFile(attachment_record.upload, extension=attachment_record.extension, fix=True)
        process_file(saved_file_att, saved_file_att.path, attachment_record.content_type, attachment_record.extension, initial=False)
        if upload.filename == 'headers.json':
            #sys.stderr.write("Processing headers\n")
            email_obj.initializeAttribute('headers', DAFile, mimetype=attachment_record.content_type, extension=attachment_record.extension, number=attachment_record.upload)
        elif upload.filename == 'attachment.txt' and attachment_record.index < 3:
            #sys.stderr.write("Processing body text\n")
            email_obj.initializeAttribute('body_text', DAFile, mimetype=attachment_record.content_type, extension=attachment_record.extension, number=attachment_record.upload)
        elif upload.filename == 'attachment.html' and attachment_record.index < 3:
            email_obj.initializeAttribute('body_html', DAFile, mimetype=attachment_record.content_type, extension=attachment_record.extension, number=attachment_record.upload)
        else:
            email_obj.attachment.appendObject(DAFile, mimetype=attachment_record.content_type, extension=attachment_record.extension, number=attachment_record.upload)
    if not hasattr(email_obj, 'headers'):
        email_obj.headers = None
    if not hasattr(email_obj, 'body_text'):
        email_obj.body_text = None
    if not hasattr(email_obj, 'body_html'):
        email_obj.body_html = None
    return email_obj

def write_pypirc():
    pypirc_file = daconfig.get('pypirc path', '/var/www/.pypirc')
    #pypi_username = daconfig.get('pypi username', None)
    #pypi_password = daconfig.get('pypi password', None)
    pypi_url = daconfig.get('pypi url', 'https://pypi.python.org/pypi')
    # if pypi_username is None or pypi_password is None:
    #     return
    if os.path.isfile(pypirc_file):
        with open(pypirc_file, 'rU') as fp:
            existing_content = fp.read()
    else:
        existing_content = None
    content = """\
[distutils]
index-servers =
  pypi

[pypi]
repository: """ + pypi_url + "\n"
#     """
# username: """ + pypi_username + """
# password: """ + pypi_password + "\n"
    if existing_content != content:
        with open(pypirc_file, 'w') as fp:
            fp.write(content)
        os.chmod(pypirc_file, stat.S_IRUSR | stat.S_IWUSR)
    
def pypi_status(packagename):
    result = dict()
    pypi_url = daconfig.get('pypi url', 'https://pypi.python.org/pypi')
    try:
        handle = urllib2.urlopen(pypi_url + '/' + str(packagename) + '/json')
    except urllib2.HTTPError, e:
        if e.code == 404:
            result['error'] = False
            result['exists'] = False
        else:
            result['error'] = e.code
    except Exception, e:
        result['error'] = str(e)
    else:
        try:
            result['info'] = json.load(handle)
        except:
            result['error'] = 'json'
        else:
            result['error'] = False
            result['exists'] = True
    return result

def get_short_code(**pargs):
    key = pargs.get('key', None)
    index = pargs.get('index', None)
    if key is None and index is not None:
        raise DAError("get_short_code: if you provide an index you must provide a key")
    if 'i' in pargs:
        yaml_filename = pargs['i']
    else:
        yaml_filename = session.get('i', None)
    if 'uid' in pargs:
        uid = pargs['uid']
    else:
        uid = session.get('uid', None)
    if 'user_id' in pargs:
        user_id = pargs['user_id']
        temp_user_id = None
    elif 'temp_user_id' in pargs:
        user_id = None
        temp_user_id = pargs['temp_user_id']
    elif current_user.is_anonymous:
        user_id = None
        temp_user_id = session.get('tempuser', None)
    else:
        user_id = current_user.id
        temp_user_id = None
    short_code = None
    for record in Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key, index=index):
        short_code = record.short
    if short_code is not None:
        return short_code
    counter = 0
    new_record = None
    while counter < 20:
        existing_id = None
        new_short = random_lower_string(6)
        for record in Shortener.query.filter_by(short=new_short):
            existing_id = record.id
        if existing_id is None:
            new_record = Shortener(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, short=new_short, key=key, index=index)
            db.session.add(new_record)
            db.session.commit()
            break
        counter += 1
    if new_record is None:
        raise SystemError("Failed to generate unique short code")
    return new_short
        
for path in [FULL_PACKAGE_DIRECTORY, UPLOAD_DIRECTORY, LOG_DIRECTORY]: #PACKAGE_CACHE
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            sys.exit("Could not create path: " + path)
    if not os.access(path, os.W_OK):
        sys.exit("Unable to create files in directory: " + path)
if not os.access(WEBAPP_PATH, os.W_OK):
    sys.exit("Unable to modify the timestamp of the WSGI file: " + WEBAPP_PATH)

r = redis.StrictRedis(host=docassemble.base.util.redis_server, db=0)
#docassemble.base.functions.set_server_redis(r)

#docassemble.base.util.set_twilio_config(twilio_config)
docassemble.base.functions.update_server(url_finder=get_url_from_file_reference,
                                         chat_partners_available=chat_partners_available,
                                         sms_body=sms_body,
                                         get_sms_session=get_sms_session,
                                         initiate_sms_session=initiate_sms_session,
                                         terminate_sms_session=terminate_sms_session,
                                         twilio_config=twilio_config,
                                         server_redis=r,
                                         user_id_dict=user_id_dict,
                                         retrieve_emails=retrieve_emails,
                                         get_short_code=get_short_code,
                                         make_png_for_pdf=make_png_for_pdf,
                                         wait_for_task=wait_for_task)
#docassemble.base.util.set_user_id_function(user_id_dict)
#docassemble.base.functions.set_generate_csrf(generate_csrf)
#docassemble.base.parse.set_url_finder(get_url_from_file_reference)
#docassemble.base.parse.set_url_for(url_for)
#APPLICATION_NAME = 'docassemble'

base_words = get_base_words()
title_documentation = get_title_documentation()
documentation_dict = get_documentation_dict()
base_name_info = get_name_info()
for val in base_name_info:
    base_name_info[val]['name'] = val
    base_name_info[val]['insert'] = val
    if 'show' not in base_name_info[val]:
        base_name_info[val]['show'] = False

#docassemble.base.functions.set_chat_partners_available(chat_partners_available)

password_secret_key = daconfig.get('password secretkey', app.secret_key)

sys_logger = logging.getLogger('docassemble')
sys_logger.setLevel(logging.DEBUG)

LOGFORMAT = 'docassemble: ip=%(clientip)s i=%(yamlfile)s uid=%(session)s user=%(user)s %(message)s'

if LOGSERVER is None:
    docassemble_log_handler = logging.FileHandler(filename=os.path.join(LOG_DIRECTORY, 'docassemble.log'))
    sys_logger.addHandler(docassemble_log_handler)
else:
    import logging.handlers
    handler = logging.handlers.SysLogHandler(address=(LOGSERVER, 514), socktype=socket.SOCK_STREAM)
    sys_logger.addHandler(handler)

if not in_celery:
    if LOGSERVER is None:
        docassemble.base.logger.set_logmessage(syslog_message_with_timestamp)
    else:
        docassemble.base.logger.set_logmessage(syslog_message)

def null_func(*pargs, **kwargs):
    logmessage("Null function called")
    return None

if in_celery:
    docassemble.base.functions.update_server(bg_action=null_func,
                                             #async_ocr=null_func,
                                             ocr_page=null_func,
                                             ocr_finalize=null_func,
                                             worker_convert=null_func)
else:
    import docassemble.webapp.worker
    #sys.stderr.write("calling set worker now\n")
    docassemble.base.functions.update_server(bg_action=docassemble.webapp.worker.background_action,
                                             #async_ocr=docassemble.webapp.worker.async_ocr,
                                             ocr_page=docassemble.webapp.worker.ocr_page,
                                             ocr_finalize=docassemble.webapp.worker.ocr_finalize,
                                             worker_convert=docassemble.webapp.worker.convert)

pg_ex = dict()

def define_examples():
    if 'encoded_example_html' in pg_ex:
        return
    example_html = list()
    example_html.append('        <div class="col-md-2">\n          <h4>Example blocks</h4>')
    pg_ex['pg_first_id'] = list()
    data_dict = dict()
    make_example_html(get_examples(), pg_ex['pg_first_id'], example_html, data_dict)
    example_html.append('        </div>')
    example_html.append('        <div class="col-md-4 example-source-col"><h4>Source<a class="label label-success example-copy">Insert</a></h4><div id="example-source-before" class="invisible"></div><div id="example-source"></div><div id="example-source-after" class="invisible"></div><div><a class="example-hider" id="show-full-example">Show context of example</a><a class="example-hider invisible" id="hide-full-example">Hide context of example</a></div></div>')
    example_html.append('        <div class="col-md-6"><h4>Preview<a target="_blank" class="label label-primary example-documentation example-hidden" id="example-documentation-link">View documentation</a></h4><a href="#" target="_blank" id="example-image-link"><img title="Click to try this interview" class="example_screenshot" id="example-image"></a></div>')
    pg_ex['encoded_data_dict'] = safeid(json.dumps(data_dict))
    pg_ex['encoded_example_html'] = Markup("\n".join(example_html))


if LooseVersion(min_system_version) > LooseVersion(daconfig['system version']):
    version_warning = word("Your docassemble system needs to be upgraded.")
else:
    version_warning = None
    
import docassemble.webapp.machinelearning
docassemble.base.util.set_knn_machine_learner(docassemble.webapp.machinelearning.SimpleTextMachineLearner)
docassemble.base.util.set_svm_machine_learner(docassemble.webapp.machinelearning.SVMMachineLearner)
docassemble.base.util.set_machine_learning_entry(docassemble.webapp.machinelearning.MachineLearningEntry)

from docassemble.webapp.users.models import UserAuthModel, UserModel, UserDict, UserDictKeys, TempUser, ChatLog
with app.app_context():
    copy_playground_modules()
    write_pypirc()

if __name__ == "__main__":
    app.run()
