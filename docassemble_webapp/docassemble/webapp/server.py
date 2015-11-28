import os
import sys
import datetime
import time
import pip
import shutil
import codecs
import weakref
import docassemble.base.parse
import docassemble.base.interview_cache
from docassemble.base.standardformatter import as_html, signature_html
import xml.etree.ElementTree as ET
import docassemble.webapp.database
import tempfile
import zipfile
import traceback
from docassemble.base.error import DAError
from docassemble.base.util import pickleable_objects, word, comma_and_list
from docassemble.base.logger import logmessage
import mimetypes
import logging
#import psycopg2
import pickle
import string
import random
import cgi
import Cookie
import re
import urlparse
import json
import base64
from flask import make_response, abort, render_template, request, session, send_file, redirect, url_for, current_app, get_flashed_messages, flash, Markup
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask.ext.user import login_required, roles_required, UserManager, SQLAlchemyAdapter
from flask.ext.user.forms import LoginForm
from docassemble.webapp.develop import CreatePackageForm, UpdatePackageForm, ConfigForm, SandboxForm
from flask_mail import Mail, Message
import flask.ext.user.signals
import httplib2
from werkzeug import secure_filename, FileStorage
from rauth import OAuth1Service, OAuth2Service
from flask_kvsession import KVSessionExtension
from simplekv.db.sql import SQLAlchemyStore
from sqlalchemy import create_engine, MetaData
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.users.models import UserAuth, User, Role, UserDict, UserDictKeys, UserRoles, UserDictLock, Attachments, Uploads
from docassemble.webapp.packages.models import Package, PackageAuth
from docassemble.webapp.config import daconfig
from PIL import Image
import pyPdf
import yaml
from subprocess import call
DEBUG = daconfig.get('debug', False)
docassemble.base.parse.debug = DEBUG
if DEBUG:
    from pygments import highlight
    from pygments.lexers import YamlLexer
    from pygments.formatters import HtmlFormatter

app.debug = False

default_yaml_filename = daconfig.get('default_interview', 'docassemble.demo:data/questions/questions.yml')

if 'mail' not in daconfig:
    daconfig['mail'] = dict()
os.environ['PYTHON_EGG_CACHE'] = tempfile.mkdtemp()
app.config['APP_NAME'] = daconfig.get('appname', 'docassemble')
app.config['BRAND_NAME'] = daconfig.get('brandname', daconfig.get('appname', 'docassemble'))
app.config['MAIL_USERNAME'] = daconfig['mail'].get('username', None)
app.config['MAIL_PASSWORD'] = daconfig['mail'].get('password', None)
app.config['MAIL_DEFAULT_SENDER'] = daconfig['mail'].get('default_sender', None)
app.config['MAIL_SERVER'] = daconfig['mail'].get('server', 'localhost')
app.config['MAIL_PORT'] = daconfig['mail'].get('port', 25)
app.config['MAIL_USE_SSL'] = daconfig['mail'].get('use_ssl', False)
app.config['MAIL_USE_TLS'] = daconfig['mail'].get('use_tls', False)
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
app.config['USER_AFTER_LOGIN_ENDPOINT'] = 'index'
app.config['USER_AFTER_LOGOUT_ENDPOINT'] = 'index'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'index'
app.config['USER_AFTER_RESEND_CONFIRM_EMAIL_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_RESET_PASSWORD_ENDPOINT'] = 'user.login' 
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['USE_X_SENDFILE'] = daconfig.get('xsendfile', True)
PNG_RESOLUTION = daconfig.get('png_resolution', 300)
PNG_SCREEN_RESOLUTION = daconfig.get('png_screen_resolution', 72)
PDFTOPPM_COMMAND = daconfig.get('pdftoppm', None)
docassemble.base.util.set_default_language(daconfig.get('language', 'en'))
docassemble.base.util.set_default_locale(daconfig.get('locale', 'US.utf8'))
docassemble.base.util.set_language(daconfig.get('language', 'en'))
docassemble.base.util.set_locale(daconfig.get('locale', 'US.utf8'))
docassemble.base.util.set_da_config(daconfig)
docassemble.base.util.update_locale()
ROOT = daconfig.get('root', '/')
if 'currency symbol' in daconfig:
    docassemble.base.util.update_language_function('*', 'currency_symbol', lambda: daconfig['currency symbol'])
app.logger.warning("default sender is " + app.config['MAIL_DEFAULT_SENDER'] + "\n")
exit_page = daconfig.get('exitpage', '/')
UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')
USE_PROGRESS_BAR = daconfig.get('use_progress_bar', True)
SHOW_LOGIN = daconfig.get('show_login', True)
#USER_PACKAGES = daconfig.get('user_packages', '/var/lib/docassemble/dist-packages')
#sys.path.append(USER_PACKAGES)
if USE_PROGRESS_BAR:
    initial_dict = dict(_internal=dict(progress=0, tracker=0, answered=set(), answers=dict(), objselections=dict()), url_args=dict())
else:
    initial_dict = dict(_internal=dict(tracker=0, answered=set(), answers=dict(), objselections=dict()), url_args=dict())
if 'initial_dict' in daconfig:
    initial_dict.update(daconfig['initial_dict'])
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

#conn = psycopg2.connect(connect_string)

KVSessionExtension(store, app)

error_file_handler = logging.FileHandler(filename=LOGFILE)
error_file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(error_file_handler)

def flask_logger(message):
    app.logger.warning(message)
    sys.stderr.write(unicode(message) + "\n")
    return

docassemble.base.logger.set_logmessage(flask_logger)

#logmessage("foo bar")

def get_url_from_file_reference(file_reference, **kwargs):
    if re.search(r'^http', file_reference):
        return(file_reference)
    root = daconfig.get('root', '/')
    if 'ext' in kwargs:
        extn = kwargs['ext']
        extn = re.sub(r'^\.', '', extn)
        extn = '.' + extn
    else:
        extn = ''
    if re.match('[0-9]+', file_reference):
        file_number = file_reference
        if 'page' in kwargs:
            page = kwargs['page']
            size = kwargs.get('size', 'page')
            url = root + 'uploadedpage'
            if size == 'screen':
                url += 'screen'
            url += '/' + str(file_number) + '/' + str(page)
        else:
            url = root + 'uploadedfile/' + str(file_number) + extn
    else:
        parts = file_reference.split(':')
        if len(parts) < 2:
            parts = ['docassemble.base', file_reference]
        parts[1] = re.sub(r'^data/static/', '', parts[1])
        url = root + 'packagestatic/' + parts[0] + '/' + parts[1] + extn
    return(url)

docassemble.base.parse.set_url_finder(get_url_from_file_reference)

def absolute_validator(the_file):
    logmessage("Running my validator")
    if the_file.startswith(os.path.join(UPLOAD_DIRECTORY, 'sandbox')) and current_user.is_authenticated and not current_user.is_anonymous and current_user.has_role('admin', 'developer') and the_file == os.path.join(UPLOAD_DIRECTORY, 'sandbox', str(current_user.id)):
        return True
    return False

docassemble.base.parse.set_absolute_validator(absolute_validator)

def get_path_from_file_number(file_number, directory=False):
    parts = re.sub(r'(...)', r'\1/', '{0:012x}'.format(int(file_number))).split('/')
    path = os.path.join(UPLOAD_DIRECTORY, *parts)
    if directory:
        return(path)
    else:
        return (os.path.join(path, 'file'))

def get_ext_and_mimetype(filename):
    mimetype, encoding = mimetypes.guess_type(filename)
    extension = filename.lower()
    extension = re.sub('.*\.', '', extension)
    if extension == "jpeg":
        extension = "jpg"
    if extension == "tiff":
        extension = "tif"
    if extension == '3gpp':
        mimetype = 'audio/3gpp'
    return(extension, mimetype)

def get_info_from_file_number(file_number):
    result = dict()
    upload = Uploads.query.filter_by(indexno=file_number, key=session['uid']).first()
    if upload:
        result['path'] = get_path_from_file_number(file_number)
        result['filename'] = upload.filename
        result['extension'], result['mimetype'] = get_ext_and_mimetype(result['filename'])
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
        return result
    filename = result['path'] + '.' + result['extension']
    add_info_about_file(filename, result)
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
    if re.match('[0-9]+', file_reference):
        return(get_info_from_file_number(file_reference))
    result = dict()
    if 'convert' in kwargs:
        convert = kwargs['convert']
    else:
        convert = None
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
                #logmessage("Did not find file " + result['path'] + '.' + convert[result['extension']])
                return dict()
        #logmessage("Full path is " + result['fullpath'])
        add_info_about_file(result['fullpath'], result)
    else:
        logmessage("File reference " + str(file_reference) + " DID NOT EXIST.")
    return(result)

docassemble.base.parse.set_file_finder(get_info_from_file_reference)

def get_mail_variable(*args, **kwargs):
    return mail

def save_numbered_file(filename, orig_path):
    file_number = get_new_file_number(session['uid'], filename)
    extension, mimetype = get_ext_and_mimetype(filename)
    path = get_file_path(file_number)
    shutil.copyfile(orig_path, path)
    os.symlink(path, path + '.' + extension)
    return(file_number, extension, mimetype)

docassemble.base.parse.set_mail_variable(get_mail_variable)
docassemble.base.parse.set_save_numbered_file(save_numbered_file)

key_requires_preassembly = re.compile('^(x\.|x\[|_multiple_choice)')
match_invalid = re.compile('[^A-Za-z0-9_\[\].\'\%\-=]')
match_brackets = re.compile('\[\'.*\'\]$')
match_inside_and_outside_brackets = re.compile('(.*)(\[\'[^\]]+\'\])$')
match_inside_brackets = re.compile('\[\'([^\]]+)\'\]')
match_triplequote = re.compile('"""')

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
#app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                         for x in xrange(32))

word_file_list = daconfig.get('words', list())
if type(word_file_list) is not list:
    word_file_list = [word_file_list]
for word_file in word_file_list:
    logmessage("Reading from " + str(word_file))
    file_info = get_info_from_file_reference(word_file)
    if 'fullpath' in file_info:
        with open(file_info['fullpath'], 'r') as stream:
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
    user_manager = current_app.user_manager
    flask.ext.user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
    logout_user()
    reset_session(session.get('i', default_yaml_filename))
    flash(word('You have signed out successfully.'), 'success')
    next = request.args.get('next', _endpoint_url(user_manager.after_logout_endpoint))
    return redirect(next)

def setup_app(app, db):
    from docassemble.webapp.users.forms import MyRegisterForm
    from docassemble.webapp.users.views import user_profile_page
    #from docassemble.webapp.users import models
    #from docassemble.webapp.pages import views
    #from docassemble.webapp.users import views
    db_adapter = SQLAlchemyAdapter(db, User, UserAuthClass=UserAuth)
    user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm, user_profile_view_function=user_profile_page, logout_view_function=logout)
    return(app)

setup_app(app, db)
lm = LoginManager(app)
lm.login_view = 'login'

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
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash(word('Authentication failed.'), 'error')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email, active=True)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=False)
    if not current_user.is_anonymous:
        #update_user_id(session['uid'])
        flash(word('Welcome!  You are logged in as ') + email, 'success')
    return redirect(url_for('index'))

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
    return redirect(url_for('index'))

@app.route("/exit", methods=['POST', 'GET'])
def exit():
    return redirect(exit_page)

@app.route("/", methods=['POST', 'GET'])
def index():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', default_yaml_filename)
    steps = 0
    need_to_reset = False
    yaml_parameter = request.args.get('i', None)
    session_parameter = request.args.get('session', None)
    if yaml_parameter is not None:
        yaml_filename = yaml_parameter
        user_code, user_dict = reset_session(yaml_filename)
        session_id = session.get('uid', None)
        if 'key_logged' in session:
            del session['key_logged']
        need_to_reset = True
    if session_parameter is not None:
        session_id = session_parameter
        session['uid'] = session_id
        user_code = session_id
        steps, user_dict = fetch_user_dict(user_code, yaml_filename)
        if 'key_logged' in session:
            del session['key_logged']
        need_to_reset = True
    if session_id:
        user_code = session_id
        steps, user_dict = fetch_user_dict(user_code, yaml_filename)
        if user_dict is None:
            del user_code
            del user_dict
    try:
        user_dict
        user_code
    except:
        user_code, user_dict = reset_session(yaml_filename)
        if 'key_logged' in session:
            del session['key_logged']
        steps = 0
    action = None
    if current_user.is_authenticated and 'key_logged' not in session:
        save_user_dict_key(user_code, yaml_filename)
        session['key_logged'] = True 
    if len(request.args):
        if 'action' in request.args:
            action = json.loads(myb64unquote(request.args['action']))
        for argname in request.args:
            if argname in ('filename', 'question', 'format', 'index', 'i', 'action'):
                continue
            if re.match('[A-Za-z_]+', argname):
                exec("url_args['" + argname + "'] = " + repr(request.args.get(argname).encode('unicode_escape')), user_dict)
            need_to_reset = True
    if need_to_reset:
        save_user_dict(user_code, user_dict, yaml_filename)
        return redirect(url_for('index'))
    post_data = request.form.copy()
    if '_email_attachments' in post_data and '_attachment_email_address' in post_data and '_question_number' in post_data:
        success = False
        question_number = post_data['_question_number']
        attachment_email_address = post_data['_attachment_email_address']
        if '_attachment_include_rtf' in post_data:
            if post_data['_attachment_include_rtf'] == 'True':
                include_rtfs = True
            else:
                include_rtfs = False
            del post_data['_attachment_include_rtf']
        else:
            include_rtfs = False
        del post_data['_question_number']
        del post_data['_email_attachments']
        del post_data['_attachment_email_address']
        logmessage("Got e-mail request for " + str(question_number) + " with e-mail " + str(attachment_email_address) + " and rtf inclusion of " + str(include_rtfs) + " and using yaml file " + yaml_filename)
        the_user_dict = get_attachment_info(user_code, question_number, yaml_filename)
        if the_user_dict is not None:
            logmessage("the_user_dict is not none!")
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
                    if include_rtfs and ('rtf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']):
                        file_formats.append('rtf')
                    for the_format in file_formats:
                        the_filename = the_attachment['file'][the_format]
                        if the_format == "pdf":
                            mime_type = 'application/pdf'
                        elif the_format == "rtf":
                            mime_type = 'application/rtf'
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
                        with open(attach_info['path'], 'r') as fp:
                            msg.attach(attach_info['filename'], attach_info['mimetype'], fp.read())
                    try:
                        mail.send(msg)
                        success = True
                    except Exception as errmess:
                        logmessage(str(errmess))
                        success = False
        if success:
            flash(word("Your documents were e-mailed to") + " " + str(attachment_email_address) + ".", 'info')
        else:
            flash(word("Unable to e-mail your documents to") + " " + str(attachment_email_address) + ".", 'error')
    if '_back_one' in post_data and steps > 1:
        steps, user_dict = fetch_previous_user_dict(user_code, yaml_filename)
        #logmessage("Went back")
    elif 'filename' in request.args:
        #logmessage("Got a GET statement with filename!")
        the_user_dict = get_attachment_info(user_code, request.args.get('question'), request.args.get('filename'))
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
            if key_requires_preassembly.search(key):
                should_assemble = True
                break
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
        file_field = post_data['_save_as'];
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
                file_number = get_new_file_number(session['uid'], filename)
                extension, mimetype = get_ext_and_mimetype(filename)
                path = get_file_path(file_number)
                with open(path, 'w') as ifile:
                    ifile.write(theImage)
                os.symlink(path, path + '.' + extension)
                #sys.stderr.write("Saved theImage\n")
                string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ", filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')"
            else:
                string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ")"
            #sys.stderr.write(string + "\n")
            try:
                exec(string, user_dict)
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
        for file_field in file_fields:
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
            for file_field in file_fields:
                #logmessage("There is a file_field")
                if file_field in request.files:
                    #logmessage("There is a file_field in request.files")
                    the_files = request.files.getlist(file_field)
                    if the_files:
                        files_to_process = list()
                        for the_file in the_files:
                            #logmessage("There is a file_field in request.files and it has a type of " + str(type(the_file)) + " and its str representation is " + str(the_file))
                            filename = secure_filename(the_file.filename)
                            file_number = get_new_file_number(session['uid'], filename)
                            extension, mimetype = get_ext_and_mimetype(filename)
                            path = get_file_path(file_number)
                            if extension == "jpg" and 'imagemagick' in daconfig:
                                unrotated = tempfile.NamedTemporaryFile(suffix="jpg")
                                the_file.save(unrotated.name)
                                call_array = [daconfig['imagemagick'], str(unrotated.name), '-auto-orient', '-density', '300']
                                call_array.append('jpeg:' + str(path))
                                result = call(call_array)
                                if result > 0:
                                    shutil.copyfile(unrotated.name, path)
                            else:
                                the_file.save(path)
                            os.symlink(path, path + '.' + extension)
                            if mimetype == 'video/quicktime' and 'ffmpeg' in daconfig:
                                call_array = [daconfig['ffmpeg'], '-i', path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', path + '.ogv']
                                result = call(call_array)
                                call_array = [daconfig['ffmpeg'], '-i', path + '.' + extension, '-vcodec', 'copy', '-acodec', 'copy', path + '.mp4']
                                result = call(call_array)
                            if mimetype == 'video/mp4' and 'ffmpeg' in daconfig:
                                call_array = [daconfig['ffmpeg'], '-i', path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', path + '.ogv']
                                result = call(call_array)
                            if mimetype == 'video/ogg' and 'ffmpeg' in daconfig:
                                call_array = [daconfig['ffmpeg'], '-i', path + '.' + extension, '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '22', '-c:a', 'libmp3lame', '-qscale:a', '2', '-ac', '2', '-ar', '44100', path + '.mp4']
                                result = call(call_array)
                            if mimetype == 'audio/mpeg' and 'pacpl' in daconfig:
                                call_array = [daconfig['pacpl'], '-t', 'ogg', path + '.' + extension]
                                result = call(call_array)
                            if mimetype == 'audio/ogg' and 'pacpl' in daconfig:
                                call_array = [daconfig['pacpl'], '-t', 'mp3', path + '.' + extension]
                                result = call(call_array)
                            if mimetype in ['audio/3gpp'] and 'ffmpeg' in daconfig:
                                call_array = [daconfig['ffmpeg'], '-i', path + '.' + extension, path + '.ogg']
                                result = call(call_array)
                                call_array = [daconfig['ffmpeg'], '-i', path + '.' + extension, path + '.mp3']
                                result = call(call_array)
                            if mimetype in ['audio/x-wav', 'audio/wav'] and 'pacpl' in daconfig:
                                call_array = [daconfig['pacpl'], '-t', 'mp3', path + '.' + extension]
                                result = call(call_array)
                                call_array = [daconfig['pacpl'], '-t', 'ogg', path + '.' + extension]
                                result = call(call_array)
                            if extension == "pdf":
                                make_image_files(path)
                            files_to_process.append((filename, file_number, mimetype, extension))
                        if match_invalid.search(file_field):
                            error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                            break
                        if len(files_to_process) > 0:
                            elements = list()
                            indexno = 0
                            for (filename, file_number, mimetype, extension) in files_to_process:
                                elements.append("docassemble.base.core.DAFile('" + file_field + "[" + str(indexno) + "]', filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')")
                                indexno += 1
                            string = file_field + " = docassemble.base.core.DAFileList('" + file_field + "', elements=[" + ", ".join(elements) + "])"
                        else:
                            string = file_field + " = None"
                        logmessage("Doing " + string)
                        try:
                            exec(string, user_dict)
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
    known_variables = dict()
    for key in post_data:
        if key in ['_checkboxes', '_back_one', '_files', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_tracker', '_track_location']:
            continue
        #logmessage("Got a key: " + key)
        data = post_data[key]
        if match_invalid.search(key):
            error_messages.append(("error", "Error: Invalid character in key: " + key))
            break
        #data = re.sub(r'"""', '', data)
        if match_brackets.search(key):
            #logmessage("Searching key " + str(key))
            match = match_inside_and_outside_brackets.search(key)
            key = match.group(1)
            real_key = key
            bracket = match_inside_brackets.sub(process_bracket_expression, match.group(2))
            #logmessage("key is " + str(key) + " and bracket is " + str(bracket))
            if key in user_dict:
                known_variables[key] = True
            if key not in known_variables:
                try:
                    eval(key, user_dict)
                except:
                    #logmessage("setting key " + str(key) + " to empty dict")
                    string = key + ' = dict()'
                    try:
                        exec(string, user_dict)
                        known_variables[key] = True
                    except:
                        raise DAError("cannot initialize " + key)
            key = key + bracket
        else:
            real_key = key
        #logmessage("Real key is " + real_key + " and key is " + key)
        if real_key in known_datatypes:
            #logmessage("key " + real_key + "is in datatypes: " + known_datatypes[key])
            if known_datatypes[real_key] in ['boolean', 'checkboxes', 'yesno', 'noyes', 'yesnowide', 'noyeswide']:
                if data == "True":
                    data = "True"
                else:
                    data = "False"
            elif known_datatypes[key] == 'integer':
                if data == '':
                    data = 0
                data = "int(" + repr(data) + ")"
            elif known_datatypes[key] in ['number', 'float', 'currency']:
                if data == '':
                    data = 0
                data = "float(" + repr(data) + ")"
            elif known_datatypes[key] in ['object']:
                if data == '':
                    continue
                #logmessage("Got to here")
                data = "_internal['objselections'][" + repr(key) + "][" + repr(data) + "]"
            else:
                data = repr(data)
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
        string = key + ' = ' + data
        logmessage("Doing " + str(string))
        try:
            exec(string, user_dict)
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
    if len(interview_status.attachments) > 0:
        #logmessage("Updating attachment info")
        update_attachment_info(user_code, user_dict, interview_status)
    if interview_status.question.question_type == "restart":
        url_args = user_dict['url_args']
        user_dict = initial_dict.copy()
        user_dict['url_args'] = url_args
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request))
        reset_user_dict(user_code, user_dict, yaml_filename)
        steps = 0
        changed = False
        interview.assemble(user_dict, interview_status)
    if USE_PROGRESS_BAR and interview_status.question.progress is not None and interview_status.question.progress > user_dict['_internal']['progress']:
        user_dict['_internal']['progress'] = interview_status.question.progress
    if interview_status.question.question_type == "exit":
        user_dict = initial_dict.copy()
        reset_user_dict(user_code, user_dict, yaml_filename)
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
    # if 'x' in user_dict:
    #     del user_dict['x']
    # if 'i' in user_dict:
    #     del user_dict['i']
    save_user_dict(user_code, user_dict, yaml_filename, changed=changed)
    flash_content = ""
    messages = get_flashed_messages(with_categories=True) + error_messages
    if messages:
        #flash_content += '<div class="container">'
        for classname, message in messages:
            if classname == 'error':
                classname = 'danger'
            flash_content += '<div class="row"><div class="col-md-6"><div class="alert alert-' + classname + '"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div></div></div>'
            #flash_content += '</div>'
    scripts = """
    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
    <script src="//ajax.aspnetcdn.com/ajax/jquery.validate/1.13.1/jquery.validate.min.js"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/js/jasny-bootstrap.min.js"></script>
"""
    scripts += '    <script src="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.js') + '"></script>' + """
    <script>
    $( document ).ready(function() {
      $(function () {
        $('.tabs a:last').tab('show')
      })
      $(function () {
        $('[data-toggle="popover"]').popover()
      })
      $("#daform input, #daform textarea, #daform select").first().focus();
      $(".to-labelauty").labelauty({ width: "100%" });
      $(".to-labelauty-icon").labelauty({ label: false });
      $(function(){ 
        var navMain = $("#navbar-collapse");
        navMain.on("click", "a", null, function () {
          $(this).css('color', '')
          navMain.collapse('hide');
        });
        $("#sourcetoggle").on("click", function(){
          $(this).toggleClass("sourceactive");
        });
      });
    });
    </script>"""
    if interview_status.question.question_type == "signature":
        output = '<!doctype html>\n<html lang="en">\n  <head><meta charset="utf-8"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=0" /><title>' + word('Signature') + '</title><script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script><script src="' + url_for('static', filename='app/signature.js') + '"></script><link rel="stylesheet" href="' + url_for('static', filename='app/signature.css') + '"><title>' + word('Sign Your Name') + '</title></head>\n  <body onresize="resizeCanvas()">'
        output += signature_html(interview_status, DEBUG, ROOT)
        output += """\n  </body>\n</html>"""
    else:
        extra_scripts = list()
        extra_css = list()
        content = as_html(interview_status, extra_scripts, extra_css, url_for, DEBUG, ROOT)
        output = '<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="utf-8"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1"><link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css" rel="stylesheet"><link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css" rel="stylesheet"><link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css"><link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" /><link href="' + url_for('static', filename='jquery-labelauty/source/jquery-labelauty.css') + '" rel="stylesheet"><link rel="stylesheet" href="' + url_for('static', filename='app/app.css') + '">'
        if DEBUG:
            output += '<link rel="stylesheet" href="' + url_for('static', filename='app/pygments.css') + '">'
        output += "".join(extra_css)
        output += '    <title>' + app.config['BRAND_NAME'] + '</title>\n  </head>\n  <body>\n'
        output += make_navbar(interview_status, app.config['BRAND_NAME'], steps, SHOW_LOGIN) + '    <div class="container">' + "\n      "+ '<div class="tab-content">' + flash_content
        if USE_PROGRESS_BAR:
            output += progress_bar(user_dict['_internal']['progress'])
        output += content + "</div>\n"
        if DEBUG:
            output += '      <div id="source" class="col-md-12 collapse">' + "\n"
            output += '        <h3>' + word('Source code for question') + '</h3>' + "\n"
            if interview_status.question.source_code is None:
                output += word('unavailable')
            else:
                output += highlight(interview_status.question.source_code, YamlLexer(), HtmlFormatter())
            if len(interview_status.seeking) > 1:
                output += '        <h4>' + word('How question came to be asked') + '</h4>' + "\n"
                for stage in interview_status.seeking:
                    if 'question' in stage and 'reason' in stage and stage['question'] is not interview_status.question:
                        if stage['reason'] == 'initial':
                            output += "        <h5>" + word('Ran initial code') + "</h5>\n"
                        elif stage['reason'] == 'mandatory question':
                            output += "        <h5>" + word('Tried to ask mandatory question') + "</h5>\n"
                        elif stage['reason'] == 'mandatory code':
                            output += "        <h5>" + word('Tried to run mandatory code') + "</h5>\n"
                        elif stage['reason'] == 'asking':
                            output += "        <h5>" + word('Tried to ask question') + "</h5>\n"
                        if stage['question'].from_source.path != interview.source.path:
                            output += '        <p style="font-weight: bold;"><small>(' + word('from') + ' ' + stage['question'].from_source.path +")</small></p>\n"
                        if stage['question'].source_code is None:
                            output += word('unavailable')
                        else:
                            output += highlight(stage['question'].source_code, YamlLexer(), HtmlFormatter())
                    elif 'variable' in stage:
                        output += "        <h5>" + word('Needed definition of') + " <code>" + str(stage['variable']) + "</code></h5>\n"
                #output += '        <h4>' + word('Variables defined') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(user_dict)]) + '</p>' + "\n"
                output += '        <h4>' + word('Variables defined') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(docassemble.base.util.pickleable_objects(user_dict))]) + '</p>' + "\n"
            output += '      </div>' + "\n"
        output += '    </div>'
        output += scripts + "\n    " + "".join(extra_scripts) + """\n  </body>\n</html>"""
    #logmessage(output.encode('utf8'))
    response = make_response(output.encode('utf8'), '200 OK')
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    return response

if __name__ == "__main__":
    app.run()

def process_bracket_expression(match):
    #return("[" + repr(urllib.unquote(match.group(1)).encode('unicode_escape')) + "]")
    return("[" + repr(codecs.decode(match.group(1), 'base64').decode('utf-8')) + "]")

def myb64unquote(string):
    return(codecs.decode(string, 'base64').decode('utf-8'))
    
def progress_bar(progress):
    if progress == 0:
        return('');
    return('<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="' + str(progress) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(progress) + '%;"></div></div>')

def get_unique_name(filename):
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
        new_user_dict = UserDict(key=newname, filename=filename, dictionary=codecs.encode(pickle.dumps(initial_dict.copy()), 'base64').decode())
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
    
def get_attachment_info(the_user_code, question_number, filename):
    the_user_dict = None
    existing_entry = Attachments.query.filter_by(key=the_user_code, question=question_number, filename=filename).first()
    if existing_entry and existing_entry.dictionary:
        the_user_dict = pickle.loads(codecs.decode(existing_entry.dictionary, 'base64'))
    # cur = conn.cursor()
    # cur.execute("select dictionary from attachments where key=%s and question=%s and filename=%s", [the_user_code, question_number, filename])
    # for d in cur:
    #     if d[0]:
    #         the_user_dict = pickle.loads(codecs.decode(d[0], 'base64'))
    #     break
    # conn.commit()
    return the_user_dict

def update_attachment_info(the_user_code, the_user_dict, the_interview_status):
    #logmessage("Got to update_attachment_info")
    Attachments.query.filter_by(key=the_user_code, question=the_interview_status.question.number, filename=the_interview_status.question.interview.source.path).delete()
    db.session.commit()
    new_attachment = Attachments(key=the_user_code, dictionary=codecs.encode(pickle.dumps(pickleable_objects(the_user_dict)), 'base64').decode(), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path)
    db.session.add(new_attachment)
    db.session.commit()
    # cur = conn.cursor()
    # cur.execute("delete from attachments where key=%s and question=%s and filename=%s", [the_user_code, the_interview_status.question.number, the_interview_status.question.interview.source.path])
    # conn.commit()
    # cur.execute("insert into attachments (key, dictionary, question, filename) values (%s, %s, %s, %s)", [the_user_code, codecs.encode(pickle.dumps(pickleable_objects(the_user_dict)), 'base64').decode(), the_interview_status.question.number, the_interview_status.question.interview.source.path])
    # conn.commit()
    #logmessage("Delete from attachments where key = " + the_user_code + " and question is " + str(the_interview_status.question.number) + " and filename is " + the_interview_status.question.interview.source.path)
    #logmessage("Insert into attachments (key, dictionary, question, filename) values (" + the_user_code + ", saved_user_dict, " + str(the_interview_status.question.number) + ", " + the_interview_status.question.interview.source.path + ")")
    return

def fetch_user_dict(user_code, filename):
    user_dict = None
    steps = 0
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('count')).filter(UserDict.key == user_code and UserDict.filename == filename).subquery()
    results = db.session.query(UserDict.dictionary, subq.c.count).join(subq, subq.c.indexno == UserDict.indexno)
    for d in results:
        if d.dictionary:
            user_dict = pickle.loads(codecs.decode(d.dictionary, 'base64'))
        if d.count:
            steps = d.count
        break
    # cur = conn.cursor()
    # cur.execute("SELECT a.dictionary, b.count from userdict as a inner join (select max(indexno) as indexno, count(indexno) as count from userdict where key=%s and filename=%s and dictionary is not null) as b on (a.indexno=b.indexno)", [user_code, filename])
    # for d in cur:
    #     if d[0]:
    #         user_dict = pickle.loads(codecs.decode(d[0], 'base64'))
    #     if d[1]:
    #         steps = d[1]
    #     break
    # conn.commit()
    return steps, user_dict

def fetch_previous_user_dict(user_code, filename):
    user_dict = None
    max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(UserDict.key == user_code and UserDict.filename == filename).scalar()
    # cur = conn.cursor()
    # cur.execute("select max(indexno) as indexno from userdict where key=%s and filename=%s and dictionary is not null", [user_code, filename])
    # max_indexno = None
    # for d in cur:
    #     max_indexno = d[0]
    if max_indexno is not None:
        UserDict.query.filter_by(indexno=max_indexno).delete()
        db.session.commit()
        #cur.execute("delete from userdict where indexno=%s", [max_indexno])
    #conn.commit()
    return fetch_user_dict(user_code, filename)

def advance_progress(user_dict):
    user_dict['_internal']['progress'] += 0.05*(100-user_dict['_internal']['progress'])
    return

# def advance_tracker(user_dict):
#     user_dict['_internal']['tracker'] += 1
#     return

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
    # cur = conn.cursor()
    # cur.execute("select indexno from userdictkeys where key=%s and filename=%s and user_id=%s", [user_code, filename, current_user.id])
    # found = False
    # for d in cur:
    #     found = True
    # if not found:
    #     cur.execute("INSERT INTO userdictkeys (key, filename, user_id) values (%s, %s, %s)", [user_code, filename, current_user.id])
    # conn.commit()
    return

def save_user_dict(user_code, user_dict, filename, changed=False):
    #cur = conn.cursor()
    #logmessage(repr(pickle.dumps(pickleable_objects(user_dict))))
    if current_user.is_authenticated and not current_user.is_anonymous:
        the_user_id = current_user.id
    else:
        the_user_id = None
    if changed is True:
        if USE_PROGRESS_BAR:
            advance_progress(user_dict)
        new_record = UserDict(key=user_code, dictionary=codecs.encode(pickle.dumps(pickleable_objects(user_dict)), 'base64').decode(), filename=filename, user_id=the_user_id)
        db.session.add(new_record)
        db.session.commit()
        #cur.execute("INSERT INTO userdict (key, dictionary, filename, user_id) values (%s, %s, %s, %s)", [user_code, codecs.encode(pickle.dumps(pickleable_objects(user_dict)), 'base64').decode(), filename, the_user_id])
    else:
        max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(UserDict.key == user_code and UserDict.filename == filename).scalar()
        # cur.execute("select max(indexno) as indexno from userdict where key=%s and filename=%s", [user_code, filename])
        # max_indexno = None
        # for d in cur:
        #     max_indexno = d[0]
        if max_indexno is None:
            new_record = UserDict(key=user_code, dictionary=codecs.encode(pickle.dumps(pickleable_objects(user_dict)), 'base64').decode(), filename=filename, user_id=the_user_id)
            db.session.add(new_record)
            db.session.commit()
            #cur.execute("INSERT INTO userdict (key, dictionary, filename, user_id) values (%s, %s, %s, %s)", [user_code, codecs.encode(pickle.dumps(pickleable_objects(user_dict)), 'base64').decode(), filename, the_user_id])
        else:
            for record in UserDict.query.filter_by(key=user_code, filename=filename, indexno=max_indexno).all():
                record.dictionary = codecs.encode(pickle.dumps(pickleable_objects(user_dict)), 'base64').decode()
            db.session.commit()
            #cur.execute("UPDATE userdict SET dictionary=%s where key=%s and filename=%s and indexno=%s", [codecs.encode(pickle.dumps(pickleable_objects(user_dict)), 'base64').decode(), user_code, filename, max_indexno])
    #conn.commit()
    return

def reset_user_dict(user_code, user_dict, filename):
    UserDict.query.filter_by(key=user_code, filename=filename).delete()
    UserDictKeys.query.filter_by(key=user_code, filename=filename).delete()
    db.session.commit()
    #cur = conn.cursor()
    #cur.execute("DELETE FROM userdict where key=%s and filename=%s", [user_code, filename])
    #cur.execute("DELETE FROM userdictkeys where key=%s and filename=%s", [user_code, filename])
    #conn.commit()
    save_user_dict(user_code, user_dict, filename)
    return

def get_new_file_number(user_code, file_name):
    new_upload = Uploads(key=user_code, filename=file_name)
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

def get_file_path(indexno):
    path = get_path_from_file_number(indexno, directory=True)
    if not os.path.isdir(path):
        os.makedirs(path)
    return (os.path.join(path, 'file'))

def make_navbar(status, page_title, steps, show_login):
    navbar = """\
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
"""
    if status.question.helptext is not None:
        navbar += """\
            <span style="background-color: yellow" class="icon-bar"></span>
            <span style="background-color: yellow" class="icon-bar"></span>
            <span style="background-color: yellow" class="icon-bar"></span>
"""
    else:
        navbar += """\
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
"""
    navbar += """\
          </button>
"""
    if steps > 1:
        navbar += """\
          <span class="navbar-brand"><form style="inline-block" id="backbutton" method="POST"><input type="hidden" name="_back_one" value="1"><button style="background:none; cursor:pointer; border:none; margin:0; padding:0;" type="submit"><i style="font-size:1.2em;" class="glyphicon glyphicon-chevron-left"></i></button></form></span>
"""
    navbar += """\
          <span class="navbar-brand">""" + page_title + """</span>
        </div>
        <div class="collapse navbar-collapse" id="navbar-collapse">
          <ul class="nav navbar-nav navbar-left">
            <li class="active"><a href="#question" data-toggle="tab">""" + word('Question') + """</a></li>"""
    if status.question.helptext is None:
        navbar += '<li><a href="#help" data-toggle="tab">' + word('Help') + "</a></li>\n"
    else:
        navbar += '<li><a style="color: yellow" href="#help" data-toggle="tab">' + word('Help') + ' <i class="glyphicon glyphicon-star"></i>' + "</a></li>\n"
    if DEBUG:
        navbar += """\
            <li><a id="sourcetoggle" href="#source" data-toggle="collapse" aria-expanded="false" aria-controls="source">""" + word('Source') + """</a></li>
"""
    navbar += """\
          </ul>
          <ul class="nav navbar-nav navbar-right">
"""
    if show_login:
        if current_user.is_anonymous:
            #logmessage("is_anonymous is " + str(current_user.is_anonymous))
            navbar += '            <li><a href="' + url_for('user.login', next=url_for('index')) + '">' + word('Sign in') + '</a></li>' + "\n"
        else:
            navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">' + current_user.email + '<b class="caret"></b></a><ul class="dropdown-menu">'
            if current_user.has_role('admin', 'developer'):
                navbar +='<li><a href="' + url_for('package_page') + '">' + word('Package Management') + '</a></li>'
                navbar +='<li><a href="' + url_for('sandbox_page') + '">' + word('Sandbox') + '</a></li>'
                if current_user.has_role('admin'):
                    navbar +='<li><a href="' + url_for('user_list') + '">' + word('User List') + '</a></li>'
                    navbar +='<li><a href="' + url_for('privilege_list') + '">' + word('Privileges List') + '</a></li>'
                    navbar +='<li><a href="' + url_for('config_page') + '">' + word('Configuration') + '</a></li>'
            navbar += '<li><a href="' + url_for('user_profile_page') + '">' + word('Profile') + '</a></li><li><a href="' + url_for('user.logout') + '">' + word('Sign out') + '</a></li></ul></li>'
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

def reset_session(yaml_filename):
    session['i'] = yaml_filename
    session['uid'] = get_unique_name(yaml_filename)
    user_code = session['uid']
    user_dict = initial_dict.copy()
    return(user_code, user_dict)

def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url

@app.route('/uploadedfile/<number>.<extension>', methods=['GET'])
def serve_uploaded_file_with_extension(number, extension):
    number = re.sub(r'[^0-9]', '', str(number))
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
    # file_info = get_info_from_file_reference(number)
    # block_size = 4096
    # status = '200 OK'
        filename = file_info['path'] + 'page-' + str(page) + '.png'
        if os.path.isfile(filename):
            return(send_file(filename, mimetype='image/png'))
        else:
            abort(404)

@app.route('/uploadsignature', methods=['POST'])
def upload_draw():
    post_data = request.form.copy()
    #sys.stderr.write("Got to upload_draw\n")
    if '_success' in post_data and post_data['_success'] and '_the_image' in post_data:
        theImage = base64.b64decode(re.search(r'base64,(.*)', post_data['_the_image']).group(1) + '==')
        #sys.stderr.write("Got theImage and it is " + str(len(theImage)) + " bytes long\n")
        with open('/tmp/testme.png', 'w') as ifile:
            ifile.write(theImage)
        #sys.stderr.write("Saved theImage\n")
    #sys.stderr.write("Done with upload_draw\n")
    return redirect(url_for('index'))
        
@app.route('/testsignature', methods=['GET'])
def test_signature():
    output = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=0" /><title>' + word('Signature') + '</title><script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script><script src="' + url_for('static', filename='app/signature.js') + '"></script><link rel="stylesheet" href="' + url_for('static', filename='app/signature.css') + '"><title>' + word('Signature') + '</title></head><body onresize="resizeCanvas()"><div id="page"><div class="header" id="header"><a id="new" class="navbtn nav-left">Clear</a><a id="save" class="navbtn nav-right">Save</a><div class="title">' + word('Your Signature') + '</div></div><div class="toppart" id="toppart">' + word('I am a citizen of the United States.') + '</div><div id="content"><p style="text-align:center"></p></div><div class="bottompart" id="bottompart">' + word('Jonathan Pyle') + '</div></div><form id="daform" action="' + url_for('upload_draw') + '" method="post"><input type="hidden" name="variable" value="' + word('Jonathan Pyle') + '"><input type="hidden" id="theImage" name="_the_image" value=""><input type="hidden" id="success" name="_success" value="0"></form></body></html>'
    status = '200 OK'
    response = make_response(output.encode('utf8'), status)
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    return response
        
@app.route('/uploadedpagescreen/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    file_info = get_info_from_file_number(number)
    if 'path' not in file_info:
        abort(404)
    else:
    # block_size = 4096
    # status = '200 OK'
        filename = file_info['path'] + 'screen-' + str(page) + '.png'
        if os.path.isfile(filename):
            return(send_file(filename, mimetype='image/png'))
        else:
            abort(404)

def user_can_edit_package(pkgname=None, giturl=None):
    #cur = conn.cursor()
    #sys.stderr.write("Got to user_can_edit_package\n")
    if pkgname is not None:
        #sys.stderr.write("Testing for:" + pkgname + ":\n")
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(Package.name == pkgname)
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
        # cur.execute("select a.id, b.user_id, b.authtype from package as a left outer join package_auth as b on (a.id=b.package_id) where a.name=%s", [pkgname])
        # if cur.rowcount <= 0:
        #     return(True)
        # for d in cur:
        #     if d[1] == current_user.id:
        #         return(True)
    if giturl is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(Package.giturl == giturl)
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
        # cur.execute("select a.id, b.user_id, b.authtype from package as a left outer join package_auth as b on (a.id=b.package_id) where a.giturl=%s", [giturl])
        # if cur.rowcount <= 0:
        #     return(True)
        # for d in cur:
        #     if d[1] == current_user.id:
        #         return(True)
    return(False)
                
@app.route('/updatepackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package():
    form = UpdatePackageForm(request.form, current_user)
    if request.method == 'POST' and form.validate_on_submit():
        temp_directory = tempfile.mkdtemp()
        pip_log = tempfile.NamedTemporaryFile()
        if 'zipfile' in request.files and request.files['zipfile'].filename:
            try:
                the_file = request.files['zipfile']
                filename = secure_filename(the_file.filename)
                pkgname = re.sub(r'\.zip$', r'', filename)
                if user_can_edit_package(pkgname=pkgname):
                    zippath = os.path.join(temp_directory, filename)
                    the_file.save(zippath)
                    commands = ['install', zippath, '--egg', '--no-index', '--src=' + tempfile.mkdtemp(), '--log-file=' + pip_log.name, '--upgrade', "--install-option=--user"]
                    returnval = pip.main(commands)
                    if returnval > 0:
                        with open(pip_log.name) as x: logfilecontents = x.read()
                        flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + '</pre>', 'error')
                    else:
                        if Package.query.filter_by(name=pkgname).first() is None:
                            package_auth = PackageAuth(user_id=current_user.id)
                            package_entry = Package(name=packagename, package_auth=package_auth)
                            db.session.add(package_auth)
                            db.session.add(package_entry)
                            db.session.commit()
                        flash(word("Install successful"), 'success')
                        restart_wsgi()
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            except Exception as errMess:
                flash("Error processing upload: " + str(errMess), "error")
        else:
            if form.giturl.data:
                giturl = form.giturl.data.strip()
                packagename = re.sub(r'.*/', '', giturl)
                if user_can_edit_package(giturl=giturl) and user_can_edit_package(pkgname=packagename):
                    commands = ['install', '--egg', '--src=' + temp_directory, '--log-file=' + pip_log.name, '--upgrade', "--install-option=--user", 'git+' + giturl + '.git#egg=' + packagename]
                    returnval = pip.main(commands)
                    if returnval > 0:
                        with open(pip_log.name) as x: logfilecontents = x.read()
                        flash("pip " + " ".join(commands) + "<pre>" + str(logfilecontents) + "</pre>", 'error')
                    else:
                        if Package.query.filter_by(name=packagename).first() is None and Package.query.filter_by(giturl=giturl).first() is None:
                            package_auth = PackageAuth(user_id=current_user.id)
                            package_entry = Package(name=packagename, giturl=giturl, package_auth=package_auth)
                            db.session.add(package_auth)
                            db.session.add(package_entry)
                            db.session.commit()
                        else:
                            package_entry = Package.query.filter_by(name=packagename).first()
                            if package_entry is not None and not package_entry.giturl:
                                package_entry.giturl = giturl
                                db.session.commit()
                        flash(word("Install successful"), 'success')
                        restart_wsgi()
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            else:
                flash(word('You need to either supply a Git URL or upload a file.'), 'error')
    return render_template('pages/update_package.html', form=form), 200

@app.route('/createpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_package():
    form = CreatePackageForm(request.form, current_user)
    if request.method == 'POST' and form.validate():
        pkgname = re.sub(r'^docassemble_', r'', form.name.data)
        if not user_can_edit_package(pkgname='docassemble_' + pkgname):
            flash(word('Sorry, that package name is already in use by someone else'), 'error')
        else:
            #foobar = Package.query.filter_by(name='docassemble_' + pkgname).first()
            #sys.stderr.write("this is it: " + str(foobar) + "\n")
            if Package.query.filter_by(name='docassemble_' + pkgname).first() is None:
                package_auth = PackageAuth(user_id=current_user.id)
                package_entry = Package(name='docassemble_' + pkgname, package_auth=package_auth)
                db.session.add(package_auth)
                db.session.add(package_entry)
                db.session.commit()
                #sys.stderr.write("Ok, did the commit\n")
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
            packagedir = os.path.join(directory, 'docassemble_' + str(pkgname))
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
            archive = tempfile.NamedTemporaryFile(delete=False)
            zf = zipfile.ZipFile(archive.name, mode='w')
            trimlength = len(directory) + 1
            for root, dirs, files in os.walk(packagedir):
                for file in files:
                    thefilename = os.path.join(root, file)
                    zf.write(thefilename, thefilename[trimlength:])
            zf.close()
            resp = send_file(archive.name, mimetype='application/zip', as_attachment=True, attachment_filename='docassemble_' + str(pkgname) + '.zip')
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
    if request.method == 'POST':
        if form.submit.data and form.config_content.data:
            with open(daconfig['config_file'], 'w') as fp:
                fp.write(form.config_content.data)
                flash(word('The configuration file was saved.'), 'success')
                restart_wsgi()
        elif form.cancel.data:
            flash(word('Configuration not updated.'), 'info')
        else:
            flash(word('Configuration not updated.  There was an error.'), 'error')
        return redirect(url_for('index'))
    with open(daconfig['config_file'], 'r') as fp:
        content = fp.read()
        return render_template('pages/config.html', extra_css=Markup('\n    <link rel="stylesheet" href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    <script>\n      daTextArea=document.getElementById("config_content");\n      daTextArea.value = ' + json.dumps(content) + ';\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", tabSize: 2, tabindex: 70, autofocus: true, lineNumbers: true});\n    </script>'), form=form), 200
    abort(404)

@app.route('/sandbox', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def sandbox_page():
    form = SandboxForm(request.form, current_user)
    path = os.path.join(UPLOAD_DIRECTORY, 'sandbox')
    javascript = ''
    if not os.path.exists(path):
        os.makedirs(path)
    filename = os.path.join(path, str(current_user.id))
    if not os.path.isfile(filename):
        with open(filename, 'a'):
            os.utime(filename, None)
    if request.method == 'POST':
        if (form.submit.data or form.run.data) and form.sandbox_content.data:
            the_time = time.strftime('%H:%M:%S %Z', time.localtime())
            with open(filename, 'w') as fp:
                fp.write(form.sandbox_content.data)
            if form.submit.data:
                flash(word('The sandbox was saved at ' + the_time + '.'), 'success')
            else:
                flash(word('The sandbox was saved at ' + the_time + '.  Running in other tab.'), 'info')
                javascript = "\n    window.open(" + repr(url_for('index', i=filename)) + ", '_blank' );"
        else:
            flash(word('Sandbox not saved.  There was an error.'), 'error')
    with open(filename, 'r') as fp:
        content = fp.read()
        return render_template('pages/sandbox.html', extra_css=Markup('\n    <link rel="stylesheet" href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    <script>\n      daTextArea=document.getElementById("sandbox_content");\n      daTextArea.value = ' + json.dumps(content) + ';\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", tabSize: 2, tabindex: 70, autofocus: true, lineNumbers: true});\n    ' + javascript + '</script>'), form=form), 200
    abort(404)

@app.route('/packages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def package_page():
    return render_template('pages/packages.html'), 200

def make_image_files(path):
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
    return render_template('pages/501.html', error=errmess, logtext=str(the_trace)), 501

def restart_wsgi():
    wsgi_file = daconfig.get('webapp', '/var/lib/docassemble/docassemble.wsgi')
    if os.path.isfile(wsgi_file):
        with open(wsgi_file, 'a'):
            os.utime(wsgi_file, None)
    return

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
    return_val = {'session': session['uid'], 'yaml_filename': yaml, 'url': url, 'user': {'is_anonymous': current_user.is_anonymous, 'is_authenticated': current_user.is_authenticated}}
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

