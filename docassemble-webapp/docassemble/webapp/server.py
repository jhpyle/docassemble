import os
import sys
import datetime
import time
import pip
import docassemble.base.parse
import docassemble.base.interview_cache
from docassemble.base.standardformatter import as_html
import docassemble.webapp.database
import mimetypes
import tempfile
import zipfile
from docassemble.base.error import DAError
from docassemble.base.util import pickleable_objects
from docassemble.base.util import word
from docassemble.base.logger import logmessage
import mimetypes
import logging
import psycopg2
import pickle
import string
import random
import cgi
import Cookie
import re
import urlparse
import json
from flask import make_response
from flask import render_template
from flask import request
from flask import session
from flask import send_file
from flask import redirect
from flask import url_for
from flask import current_app
from flask import get_flashed_messages
from flask import flash
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask.ext.user import login_required, roles_required, UserManager, SQLAlchemyAdapter
from flask.ext.user.forms import LoginForm
from docassemble.webapp.develop import CreatePackageForm, UpdatePackageForm
from flask_mail import Mail, Message
import flask.ext.user.signals
import httplib2
from werkzeug import secure_filename
from rauth import OAuth1Service, OAuth2Service
from flask_kvsession import KVSessionExtension
from simplekv.db.sql import SQLAlchemyStore
from sqlalchemy import create_engine, MetaData
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.users.models import UserAuth, User
from docassemble.webapp.packages.models import Package, PackageAuth
from docassemble.webapp.config import daconfig
from PIL import Image
import pyPdf
from subprocess import call

yaml_filename = 'docassemble.demo:data/questions/questions.yml'
#yaml_filename = 'docassemble.hello-world:data/questions/questions.yaml'

if not daconfig['mail']:
    daconfig['mail'] = dict()
os.environ['PYTHON_EGG_CACHE'] = tempfile.mkdtemp()
DEBUG = daconfig.get('debug', False)
app.config['APP_NAME'] = daconfig.get('appname', 'docassemble')
app.config['BRAND_NAME'] = daconfig.get('brandname', daconfig.get('appname', 'docassemble'))
app.config['MAIL_USERNAME'] = daconfig['mail'].get('username', None)
app.config['MAIL_PASSWORD'] = daconfig['mail'].get('password', None)
app.config['MAIL_DEFAULT_SENDER'] = daconfig['mail'].get('default_sender', None)
app.config['MAIL_SERVER'] = daconfig['mail'].get('server', 'localhost')
app.config['MAIL_PORT'] = daconfig['mail'].get('port', 25)
app.config['MAIL_USE_SSL'] = daconfig['mail'].get('use_ssl', False)
app.config['MAIL_USE_TLS'] = daconfig['mail'].get('use_tls', False)
app.config['ADMINS'] = [daconfig.get('admin_address', None)]
app.config['APP_SYSTEM_ERROR_SUBJECT_LINE'] = app.config['APP_NAME'] + " system error"
app.config['APPLICATION_ROOT'] = daconfig.get('root', None)
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
PNG_RESOLUTION = daconfig.get('png_resolution', 300)
PNG_SCREEN_RESOLUTION = daconfig.get('png_screen_resolution', 72)
PDFTOPPM_COMMAND = daconfig.get('pdftoppm_command', 'pdftoppm')
docassemble.base.util.set_language(daconfig.get('language', 'en'))
docassemble.base.util.set_locale(daconfig.get('locale', 'US.UTF8'))
docassemble.base.util.update_locale()
app.logger.info("default sender is " + app.config['MAIL_DEFAULT_SENDER'] + "\n")
exit_page = daconfig.get('exitpage', '/')
USE_PROGRESS_BAR = daconfig.get('use_progress_bar', True)
#USER_PACKAGES = daconfig.get('user_packages', '/var/lib/docassemble/dist-packages')
#sys.path.append(USER_PACKAGES)
if USE_PROGRESS_BAR:
    initial_dict = daconfig.get('initial_dict', dict(progress=0))
else:
    initial_dict = daconfig.get('initial_dict', dict())
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
    
conn = psycopg2.connect(connect_string)

KVSessionExtension(store, app)

file_handler = logging.FileHandler(filename=LOGFILE)
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)

def flask_logger(message):
    app.logger.info(message)
    return

#docassemble.base.logger.set_logmessage(flask_logger)

logmessage("foo bar\n")

def get_url_from_file_number(file_number, **kwargs):
    root = daconfig.get('root', None)
    if root is None:
        root = ''
    if 'page' in kwargs:
        page = kwargs['page']
        size = kwargs.get('size', 'page')
        url = root + '/uploadedpage'
        if size == 'screen':
            url += 'screen'
        url += '/' + str(file_number) + '/' + str(page)
    else:
        url = root + '/uploadedfile/' + str(file_number)
    return(url)

docassemble.base.parse.set_url_finder(get_url_from_file_number)

def get_path_from_file_number(file_number, directory=False):
    parts = re.sub(r'(...)', r'\1/', '{0:012x}'.format(int(file_number))).split('/')
    path = os.path.join(daconfig['uploads'], *parts)
    if directory:
        return(path)
    else:
        return (os.path.join(path, 'file'))

def get_info_from_file_number(file_number):
    result = dict()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM uploads where indexno=%s and key=%s", [file_number, session['uid']])
    for d in cur:
        result['path'] = get_path_from_file_number(file_number)
        result['filename'] = d[0]
        result['extension'], result['mimetype'] = get_ext_and_mimetype(result['filename'])
        break
    conn.commit()
    filename = result['path'] + '.' + result['extension']
    if os.path.isfile(filename):
        if result['extension'] == 'pdf':
            reader = pyPdf.PdfFileReader(open(filename))
            result['pages'] = reader.getNumPages()
        elif result['extension'] in ['png', 'jpg', 'gif']:
            im = Image.open(filename)
            result['width'], result['height'] = im.size
    else:
        logmessage("Filename DID NOT EXIST.\n")    
    return(result)

docassemble.base.parse.set_file_finder(get_info_from_file_number)

scripts = """\
    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    <script src="//ajax.aspnetcdn.com/ajax/jquery.validate/1.13.1/jquery.validate.min.js"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/js/jasny-bootstrap.min.js"></script>
    <script>$(function () {
              $('.tabs a:last').tab('show')
            })
    </script>
    <script>$("#daform input, #daform textarea, #daform button, #daform select").first().focus();</script>
"""

match_invalid = re.compile('[^A-Za-z0-9_\[\].]')
match_triplequote = re.compile('"""')

APPLICATION_NAME = 'docassemble'
app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
if 'oauth' in daconfig:
    app.config['OAUTH_CREDENTIALS'] = daconfig['oauth']
    if 'google' in daconfig['oauth']:
        app.config['USE_GOOGLE_LOGIN'] = True
    if 'facebook' in daconfig['oauth']:
        app.config['USE_FACEBOOK_LOGIN'] = True
else:
    app.config['USE_GOOGLE_LOGIN'] = False
    app.config['USE_FACEBOOK_LOGIN'] = False

app.secret_key = daconfig['secretkey']
#app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                         for x in xrange(32))

def logout():
    user_manager =  current_app.user_manager
    logmessage("Entering custom logout\n")

    # Send user_logged_out signal
    flask.ext.user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)

    # Use Flask-Login to sign out user
    logout_user()

    reset_session()

    # Prepare one-time system message
    flash(word('You have signed out successfully.'), 'success')

    # Redirect to logout_next endpoint or '/'
    next = request.args.get('next', _endpoint_url(user_manager.after_logout_endpoint))  # Get 'next' query param
    return redirect(next)

def setup_app(app, db):
    from docassemble.webapp.users.forms import MyRegisterForm
    from docassemble.webapp.users.views import user_profile_page
    from docassemble.webapp.users import models
    from docassemble.webapp.pages import views
    from docassemble.webapp.users import views
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
        logmessage("Entering authorize\n")
        result = urlparse.parse_qs(request.data)
        #logmessage("authorize: data is " + str() + "\n")
        session['google_id'] = result.get('id', [None])[0]
        session['google_email'] = result.get('email', [None])[0]
        logmessage("authorize: id is " + str(result.get('id', None)) + "\n")
        response = make_response(json.dumps('Successfully connected user.', 200))
        response.headers['Content-Type'] = 'application/json'
        logmessage("authorize: got to end\n")
        return response
    
    def callback(self):
        logmessage(str(session.get('credentials')) + "\n")
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

class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )
    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))
    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(me.get('id'))
        username = me.get('screen_name')
        return social_id, username, None   # Twitter does not provide email

@app.route('/authorize/<provider>', methods=['POST', 'GET'])
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash(word('Authentication failed.'))
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email, active=True)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=False)
    if not current_user.is_anonymous():
        update_user_id(session['uid'])
        flash(word('Welcome!  You are logged in as ') + email, 'success')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    msg = Message("Test message",
                  sender="Docassemble <no-reply@docassemble.org>",
                  recipients=["jhpyle@gmail.com"])
    msg.body = "Testing, testing"
    msg.html = "<p>Testing, testing.  Someone used the login page.</p>"
    mail.send(msg)
    form = LoginForm()
    return render_template('flask_user/login.html', form=form, login_form=form, title="Sign in")

@app.route('/slogin')
def slogin():
    output = standard_start() + """<div class="container">"""
    output += "<h1>Welcome to " + daconfig['appname'] + "</h1>"
    output += '<div class="g-signin2" data-onsuccess="onSignIn"></div>'
    output += '<div><a href="' + url_for('oauth_authorize', provider='facebook') + '">' + word('Login with Facebook') + '</a></div>'
    output += '<div><a href="' + url_for('oauth_authorize', provider='twitter') + '">' + word('Login with Twitter') + '</a></div>'
    extra_script = """\
          <script src="https://apis.google.com/js/platform.js" async defer></script>
          <script>
          function onSignIn(googleUser) {
            var profile = googleUser.getBasicProfile();
            console.log('ID: ' + profile.getId());
            console.log('Name: ' + profile.getName());
            console.log('Image URL: ' + profile.getImageUrl());
            console.log('Email: ' + profile.getEmail());
            if (profile.getId()){
              $.ajax({
                type: 'POST',
                url: '""" + url_for('oauth_authorize', provider='google') + """',
                contentType: 'application/octet-stream; charset=utf-8',
                success: function(result) {
                  console.log(result);
                  window.location = '""" + url_for('oauth_callback', provider='google', _external=True) + """';
                },
                dataType: "json",
                data: {
                  "id": profile.getId(),
                  "name": profile.getName(),
                  "image": profile.getImageUrl(),
                  "email": profile.getEmail()
                }
              });
            }
            else if (authResult['error']) {
              console.log('There was an error: ' + authResult['error']);
            }
          }
          </script>
"""
    output += """</div>""" + scripts + extra_script + """</body></html>"""
    response = make_response(output, 200)
    response.headers['Content-Type'] = 'text/html'
    return response
  
@app.route("/", methods=['POST', 'GET'])
def index():
    session_id = session.get('uid', None)
    steps = 0
    if session_id:
        user_code = session_id
        logmessage("Found user code " + session_id + "\n")
        steps, user_dict = fetch_user_dict(user_code, yaml_filename)
        if user_dict is None:
            logmessage("No dictionary for that code\n")
            del user_code
            del user_dict
    else:
        logmessage("Did not find user code in session\n")
    try:
        user_dict
        user_code
    except:
        user_code, user_dict = reset_session()
        steps = 0
    post_data = request.form.copy()
    if 'back_one' in post_data and steps > 1:
        steps, user_dict = fetch_previous_user_dict(user_code, yaml_filename)
        logmessage("Went back\n")
    elif 'filename' in request.args:
        logmessage("Got a GET statement with filename!\n")
        the_user_dict = get_attachment_info(user_code, request.args.get('question'), request.args.get('filename'))
        if the_user_dict is not None:
            logmessage("the_user_dict is not none!\n")
            interview = docassemble.base.interview_cache.get_interview(request.args.get('filename'))
            interview_status = docassemble.base.parse.InterviewStatus()
            interview.assemble(the_user_dict, interview_status)
            if len(interview_status.attachments) > 0:
                logmessage("there are attachments!\n")
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
    status = '200 OK'
    flash_content = ""
    messages = get_flashed_messages(with_categories=True)
    if messages:
        flash_content += '<div class="container">'
        for classname, message in messages:
            if classname == 'error':
                classname = 'danger'
            flash_content += '<div class="row"><div class="col-sm-6"><div class="alert alert-' + classname + '"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div></div></div>'
        flash_content += '</div>'
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    interview_status = docassemble.base.parse.InterviewStatus()
    changed = False
    if 'files' in post_data:
        logmessage("There are files\n")
        interview.assemble(user_dict, interview_status)
        file_fields = post_data['files'].split(",")
        for file_field in file_fields:
            logmessage("There is a file_field\n")
            if file_field in request.files:
                logmessage("There is a file_field in request.files\n")
                the_file = request.files[file_field]
                if the_file:
                    logmessage("There is a file_field in request.files and it is there\n")
                    filename = secure_filename(the_file.filename)
                    file_number = get_new_file_number(session['uid'], filename)
                    extension, mimetype = get_ext_and_mimetype(filename)
                    path = get_file_path(file_number)
                    the_file.save(path)
                    os.symlink(path, path + '.' + extension)
                    if extension == "pdf":
                        make_image_files(path)
                    if match_invalid.search(file_field):
                        flash_content += "<p>Error: Invalid character in file_field: " + file_field + " </p>"
                        break
                    string = file_field + " = DAFile('" + file_field + "', filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')"
                    try:
                        exec(string, user_dict)
                        changed = True
                        steps += 1
                    except Exception as errMess:
                        flash_content += "<p>Error: " + str(errMess) + "</p>"
                    #post_data.add(file_field, str(file_number))
    if 'checkboxes' in post_data:
        checkbox_fields = post_data['checkboxes'].split(",")
        for checkbox_field in checkbox_fields:
            if checkbox_field not in post_data:
                post_data.add(checkbox_field, 'False')
    for key in post_data:
        if key == 'checkboxes' or key == 'back_one' or key == 'files' or key == 'questionname':
            continue
        logmessage("Got a key: " + key + "\n")
        data = post_data[key]
        if match_invalid.search(key):
            flash_content += "<p>Error: Invalid character in key: " + key + " </p>"
            break
        data = re.sub(r'"""', '', data)
        if not (data == "True" or data == "False"):
            data = 'ur"""' + unicode(data) + '"""'
        if key == "multiple_choice":
            interview.assemble(user_dict, interview_status)
            if interview_status.question.question_type == "multiple_choice" and not hasattr(interview_status.question.fields[0], 'saveas'):
                key = 'answers["' + interview_status.question.name + '"]'
            else:
                flash_content += "<p>Error: this was not the question</p>"
        string = key + ' = ' + data
        logmessage("Doing " + str(string) + "\n")
        try:
            exec(string, user_dict)
            changed = True
            steps += 1
        except Exception as errMess:
            flash_content += "<p>Error: " + str(errMess) + "</p>"
    if changed and 'questionname' in post_data:
        user_dict['answered'].add(post_data['questionname'])
    interview.assemble(user_dict, interview_status)
    if len(interview_status.attachments) > 0:
        logmessage("Updating attachment info\n")
        update_attachment_info(user_code, user_dict, interview_status)
    if interview_status.question.question_type == "restart":
        user_dict = initial_dict.copy()
        interview_status = docassemble.base.parse.InterviewStatus()
        reset_user_dict(user_code, user_dict, yaml_filename)
        steps = 0
        changed = False
        interview.assemble(user_dict, interview_status)
    if USE_PROGRESS_BAR and interview_status.question.progress is not None and interview_status.question.progress > user_dict['progress']:
        user_dict['progress'] = interview_status.question.progress
    if interview_status.question.question_type == "exit":
        return redirect(exit_page)
    save_user_dict(user_code, user_dict, yaml_filename, changed=changed)
    output = standard_start() + make_navbar(daconfig['brandname'], steps) + flash_content + '<div class="container"><div class="tab-content">'
    if USE_PROGRESS_BAR:
        output += progress_bar(user_dict['progress'])
    validation_rules = {'rules': {}, 'messages': {}, 'errorClass': 'help-inline'}
    output += as_html(interview_status, validation_rules, DEBUG)
    extra_scripts = '<script>$("#daform").validate(' + json.dumps(validation_rules) + ');</script>'
    output += """</div></div>""" + scripts + extra_scripts + """</body></html>"""
    response = make_response(output.encode('utf8'), status)
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    return response

if __name__ == "__main__":
    app.run()

def progress_bar(progress):
    if progress == 0:
        return('');
    return('<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="' + str(progress) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(progress) + '%;"></div></div>')

def get_unique_name(filename):
    while True:
        newname = ''.join(random.choice(string.ascii_letters) for i in range(32))
        cur = conn.cursor()
        cur.execute("SELECT key from userdict where key=%s", [newname])
        if cur.fetchone():
            logmessage("Key already exists in database")
            continue
        cur.execute("INSERT INTO userdict (key, filename, dictionary) values (%s, %s, %s);", [newname, filename, pickle.dumps(initial_dict.copy())])
        conn.commit()
        return newname

def update_user_id(the_user_code):
    if current_user.id is not None and the_user_code is not None:
        cur = conn.cursor()
        cur.execute("UPDATE userdict set user_id=%s where key=%s", [current_user.id, the_user_code])
        conn.commit()
    return
    
def get_attachment_info(the_user_code, question_number, filename):
    the_user_dict = None
    cur = conn.cursor()
    cur.execute("select dictionary from attachments where key=%s and question=%s and filename=%s", [the_user_code, question_number, filename])
    for d in cur:
        if d[0]:
            the_user_dict = pickle.loads(d[0])
        break
    conn.commit()
    return the_user_dict

def update_attachment_info(the_user_code, the_user_dict, the_interview_status):
    logmessage("Got to update_attachment_info\n")
    cur = conn.cursor()
    cur.execute("delete from attachments where key=%s and question=%s and filename=%s", [the_user_code, the_interview_status.question.number, the_interview_status.question.interview.source.path])
    conn.commit()
    cur.execute("insert into attachments (key, dictionary, question, filename) values (%s, %s, %s, %s)", [the_user_code, pickle.dumps(pickleable_objects(the_user_dict)), the_interview_status.question.number, the_interview_status.question.interview.source.path])
    conn.commit()
    logmessage("Delete from attachments where key = " + the_user_code + " and question is " + str(the_interview_status.question.number) + " and filename is " + the_interview_status.question.interview.source.path + "\n")
    logmessage("Insert into attachments (key, dictionary, question, filename) values (" + the_user_code + ", saved_user_dict, " + str(the_interview_status.question.number) + ", " + the_interview_status.question.interview.source.path + ")\n")
    return

def fetch_user_dict(user_code, filename):
    user_dict = None
    steps = 0
    cur = conn.cursor()
    cur.execute("SELECT a.dictionary, b.count from userdict as a inner join (select max(indexno) as indexno, count(indexno) as count from userdict where key=%s and filename=%s and dictionary is not null) as b on (a.indexno=b.indexno)", [user_code, filename])
    for d in cur:
        if d[0]:
            user_dict = pickle.loads(d[0])
        if d[1]:
            steps = d[1]
        break
    conn.commit()
    return steps, user_dict

def fetch_previous_user_dict(user_code, filename):
    user_dict = None
    cur = conn.cursor()
    cur.execute("select max(indexno) as indexno from userdict where key=%s and filename=%s and dictionary is not null", [user_code, filename])
    max_indexno = None
    for d in cur:
        max_indexno = d[0]
    if max_indexno is not None:
        cur.execute("delete from userdict where indexno=%s", [max_indexno])
    conn.commit()
    return fetch_user_dict(user_code, filename)

def advance_progress(user_dict):
    user_dict['progress'] += 0.05*(100-user_dict['progress'])
    return

def save_user_dict(user_code, user_dict, filename, changed=False):
    cur = conn.cursor()
    if changed is True:
        if USE_PROGRESS_BAR:
            advance_progress(user_dict)
        cur.execute("INSERT INTO userdict (key, dictionary, filename) values (%s, %s, %s)", [user_code, pickle.dumps(pickleable_objects(user_dict)), filename])
    else:
        cur.execute("select max(indexno) as indexno from userdict where key=%s and filename=%s", [user_code, filename])
        max_indexno = None
        for d in cur:
            max_indexno = d[0]
        if max_indexno is None:
            cur.execute("INSERT INTO userdict (key, dictionary, filename) values (%s, %s, %s)", [user_code, pickle.dumps(pickleable_objects(user_dict)), filename])
        else:
            cur.execute("UPDATE userdict SET dictionary=%s where key=%s and filename=%s and indexno=%s", [pickle.dumps(pickleable_objects(user_dict)), user_code, filename, max_indexno])
    conn.commit()
    return

def reset_user_dict(user_code, user_dict, filename):
    cur = conn.cursor()
    cur.execute("DELETE FROM userdict where key=%s and filename=%s", [user_code, filename])
    conn.commit()
    save_user_dict(user_code, user_dict, filename)
    return

def get_new_file_number(user_code, file_name):
    indexno = None
    cur = conn.cursor()
    cur.execute("INSERT INTO uploads (key, filename) values (%s, %s) RETURNING indexno", [user_code, file_name])
    for d in cur:
        indexno = d[0]
    conn.commit()
    return (indexno)

def get_file_path(indexno):
    path = get_path_from_file_number(indexno, directory=True)
    if not os.path.isdir(path):
        os.makedirs(path)
    return (os.path.join(path, 'file'))

def make_navbar(page_title, steps):
    navbar = """\
    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>"""
    if steps > 1:
        navbar += """\
          <span class="navbar-brand"><form style="inline-block" id="backbutton" method="POST"><input type="hidden" name="back_one" value="1"><button style="background:none; cursor:pointer; border:none; margin:0; padding:0;" type="submit"><i style="font-size:1.2em;" class="glyphicon glyphicon-chevron-left"></i></button></form></span>"""
    navbar += """\
          <span class="navbar-brand">""" + page_title + """</span>
        </div>
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
          <ul class="nav navbar-nav navbar-left">
            <li class="active"><a href="#question" data-toggle="tab">""" + word('Question') + """</a></li>
            <li><a href="#help" data-toggle="tab">""" + word('Help') + """</a></li>
          </ul>
          <ul class="nav navbar-nav navbar-right">
"""
    if current_user.is_anonymous():
        navbar += '            <li><a href="' + url_for('user.login', next=url_for('index')) + '">' + word('Sign in') + '</a></li>'
    else:
        navbar += '            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">' + current_user.email + '<b class="caret"></b></a><ul class="dropdown-menu">'
        if current_user.has_roles(['admin', 'developer']):
            navbar +='<li><a href="' + url_for('package_page') + '">' + word('Package Management') + '</a></li>'
        navbar += '<li><a href="' + url_for('user_profile_page') + '">' + word('Profile') + '</a></li><li><a href="' + url_for('user.logout') + '">' + word('Sign out') + '</a></li></ul></li>'
    navbar += """\
          </ul>
        </div><!--/.nav-collapse -->
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

def standard_start():
    return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="apple-mobile-web-app-capable" content="yes"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1"><link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet"><link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css" rel="stylesheet"><link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css"><link rel="stylesheet" href="' + url_for('static', filename='app/app.css') + '"><title>docassemble</title></head><body>'

def reset_session():
    session['uid'] = get_unique_name(yaml_filename)
    user_code = session['uid']
    logmessage("Saving a dictionary for code " + user_code + "\n")
    user_dict = initial_dict.copy()
    return(user_code, user_dict)

def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url

@app.route('/uploadedfile/<number>', methods=['GET'])
def serve_uploaded_file(number):
    number = re.sub(r'[^0-9]', '', str(number))
    file_info = get_info_from_file_number(number)
    block_size = 4096
    status = '200 OK'
    return(send_file(file_info['path'], mimetype=file_info['mimetype']))

@app.route('/uploadedpage/<number>/<page>', methods=['GET'])
def serve_uploaded_page(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    file_info = get_info_from_file_number(number)
    block_size = 4096
    status = '200 OK'
    filename = file_info['path'] + 'page-' + str(page) + '.png'
    if os.path.isfile(filename):
        return(send_file(filename, mimetype='image/png'))
    else:
        abort(401)

@app.route('/uploadedpagescreen/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    file_info = get_info_from_file_number(number)
    block_size = 4096
    status = '200 OK'
    filename = file_info['path'] + 'screen-' + str(page) + '.png'
    if os.path.isfile(filename):
        return(send_file(filename, mimetype='image/png'))
    else:
        abort(401)

def user_can_edit_package(pkgname=None, giturl=None):
    cur = conn.cursor()
    sys.stderr.write("Got to user_can_edit_package\n")
    if pkgname is not None:
        sys.stderr.write("Testing for:" + pkgname + ":\n")
        cur.execute("select a.id, b.user_id, b.authtype from package as a left outer join package_auth as b on (a.id=b.package_id) where a.name=%s", [pkgname])
        if cur.rowcount <= 0:
            return(True)
        for d in cur:
            if d[1] == current_user.id:
                return(True)
    if giturl is not None:
        cur.execute("select a.id, b.user_id, b.authtype from package as a left outer join package_auth as b on (a.id=b.package_id) where a.giturl=%s", [giturl])
        if cur.rowcount <= 0:
            return(True)
        for d in cur:
            if d[1] == current_user.id:
                return(True)
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
            licensetext += 'Copyright (c) ' + str(datetime.datetime.now().year) + ' ' + str(current_user.first_name) + " " + str(current_user.last_name) + """

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
            readme = '# docassemble.' + str(pkgname) + "\n\nA docassemble extension.\n\n## Author\n" + str(current_user.first_name) + " " + str(current_user.last_name) + ", " + str(current_user.email) + "\n"
            setuppy = """\
#!/usr/bin/env python

import os
from setuptools import setup, find_packages

"""
            setuppy += "setup(name='docassemble." + str(pkgname) + "',\n" + """\
      version='0.1',
      description=('A docassemble extension.'),
      author='""" + str(current_user.first_name) + " " + str(current_user.last_name) + """',
      author_email='""" + str(current_user.email) + """',
      license='MIT',
      url='http://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      zip_safe = False,
      package_data={'docassemble.""" + str(pkgname) + """': ['data/templates/*', 'data/questions/*']},
     )

"""
            questionfiletext = """\
---
metadata:
  description: |
    Insert description of question file here.
  authors:
    - name: """ + str(current_user.first_name) + " " + str(current_user.last_name) + """
      organization: """ + str(current_user.organization) + """
  revision_date: """ + time.strftime("%Y-%m-%d") + """
---
include:
  - basic-questions.yml
---
mandatory: true
question: |
  % if user.doing_well:
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
yesno: user.doing_well
...
"""
            templatereadme = """\
# Template directory

If you wanted to use non-standard document templates with pandoc,
you would put template files in this directory.
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
# question: |
#   When I eat ${ indefinite_article(favorite_fruit.name) }, 
#   I think, "${ favorite_fruit.eat() }"  Do you agree?
# yesno: agrees_favorite_fruit_is_good
# ---
# question: What is the best fruit?
# fields:
#   - Fruit Name: favorite_fruit.name
# ---

class Fruit(DAObject):
    def eat():
        return("Yum, that " + self.name + " was good!")
"""
            directory = tempfile.mkdtemp()
            packagedir = os.path.join(directory, 'docassemble_' + str(pkgname))
            questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
            templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
            os.makedirs(questionsdir)
            os.makedirs(templatesdir)
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
            with open(os.path.join(questionsdir, 'questions.yml'), 'a') as the_file:
                the_file.write(questionfiletext)
            archive = tempfile.NamedTemporaryFile()
            zf = zipfile.ZipFile(archive.name, mode='w')
            trimlength = len(directory) + 1
            for root, dirs, files in os.walk(packagedir):
                for file in files:
                    thefilename = os.path.join(root, file)
                    zf.write(thefilename, thefilename[trimlength:])
            zf.close()
            return(send_file(archive.name, mimetype='application/zip', as_attachment=True, attachment_filename='docassemble_' + str(pkgname) + '.zip'))
    return render_template('pages/create_package.html', form=form), 200

@app.route('/packages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def package_page():
    return render_template('pages/packages.html'), 200

def make_image_files(path):
    args = [PDFTOPPM_COMMAND, '-r', str(PNG_RESOLUTION), '-png', path, path + 'page']
    result = call(args)
    if result > 0:
        raise DAError("Call to pdftoppm failed")
    args = [PDFTOPPM_COMMAND, '-r', str(PNG_SCREEN_RESOLUTION), '-png', path, path + 'screen']
    result = call(args)
    if result > 0:
        raise DAError("Call to pdftoppm failed")
    return

@app.errorhandler(DAError)
def server_error(e):
    flask_logtext = []
    with open(LOGFILE) as the_file:
        for line in the_file:
            if re.match('Exception', line):
                flask_logtext = []
            flask_logtext.append(line)
    apache_logtext = []
    # with open(APACHE_LOGFILE) as the_file:
    #     for line in the_file:
    #         if re.search('configured -- resuming normal operations', line):
    #             apache_logtext = []
    #         apache_logtext.append(line)
    return render_template('pages/501.html', error=e, logtext=''.join(flask_logtext)), 501

def get_ext_and_mimetype(filename):
    mimetype, encoding = mimetypes.guess_type(filename)
    extension = filename.lower()
    extension = re.sub('.*\.', '', extension)
    if extension == "jpeg":
        extension = "jpg"
    if extension == "tiff":
        extension = "tif"
    return(extension, mimetype)

