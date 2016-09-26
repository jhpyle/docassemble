from docassemble.webapp.app_and_db import app, db
from docassemble.base.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED, dbtableprefix, hostname, in_celery
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype
from docassemble.webapp.core.models import Uploads
from docassemble.base.logger import logmessage
import docassemble.webapp.database
import logging
import urllib
import tempfile
import pickle
import codecs
import string
import random
from Crypto.Cipher import AES
from dateutil import tz

import docassemble.base.parse
import re
import os
import sys
import pyPdf
from flask import session
from flask_mail import Mail, Message
from PIL import Image
import xml.etree.ElementTree as ET
import docassemble.webapp.worker
#sys.stderr.write("I am in backend\n")

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
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

DEBUG = daconfig.get('debug', False)
docassemble.base.parse.debug = DEBUG

connect_string = docassemble.webapp.database.connection_string()
alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()

app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')

def save_numbered_file(filename, orig_path, yaml_file_name=None):
    file_number = get_new_file_number(session['uid'], filename, yaml_file_name=yaml_file_name)
    extension, mimetype = get_ext_and_mimetype(filename)
    new_file = SavedFile(file_number, extension=extension, fix=True)
    new_file.copy_from(orig_path)
    new_file.save(finalize=True)
    return(file_number, extension, mimetype)

def get_mail_variable(*args, **kwargs):
    return mail

mail = Mail(app)

def async_mail(the_message):
    #logmessage("real async mail start")
    mail.send(the_message)
    #logmessage("real async mail finished")

#sys.stderr.write("setting mail variable\n")
docassemble.base.parse.set_mail_variable(get_mail_variable)
#sys.stderr.write("setting async_mail variable\n")
docassemble.base.parse.set_async_mail(async_mail)

docassemble.base.parse.set_save_numbered_file(save_numbered_file)
#sys.stderr.write("I am in backend again4\n")

import docassemble.base.functions
docassemble.base.functions.set_debug_status(DEBUG)
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
if 'timezone' in daconfig and daconfig['timezone'] is not None:
    docassemble.base.functions.set_default_timezone(daconfig['timezone'])
docassemble.base.functions.set_default_language(DEFAULT_LANGUAGE)
docassemble.base.functions.set_default_locale(DEFAULT_LOCALE)
docassemble.base.functions.set_default_dialect(DEFAULT_DIALECT)
docassemble.base.functions.set_language(DEFAULT_LANGUAGE, dialect=DEFAULT_DIALECT)
docassemble.base.functions.set_locale(DEFAULT_LOCALE)
docassemble.base.functions.set_da_config(daconfig)

docassemble.base.functions.update_locale()
if 'currency symbol' in daconfig:
    docassemble.base.functions.update_language_function('*', 'currency_symbol', lambda: daconfig['currency symbol'])
if S3_ENABLED:
    import docassemble.webapp.amazon
    s3 = docassemble.webapp.amazon.s3object(s3_config)
else:
    s3 = None
initial_dict = dict(_internal=dict(progress=0, tracker=0, steps_offset=0, secret=None, answered=set(), answers=dict(), objselections=dict(), starttime=None, modtime=None, accesstime=dict(), tasks=dict(), gather=list()), url_args=dict())
#else:
#    initial_dict = dict(_internal=dict(tracker=0, steps_offset=0, answered=set(), answers=dict(), objselections=dict()), url_args=dict())
if 'initial_dict' in daconfig:
    initial_dict.update(daconfig['initial_dict'])
docassemble.base.parse.set_initial_dict(initial_dict)
from docassemble.base.functions import pickleable_objects

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
    match = re.match(r'^/playgroundsources/([0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\.]', '', match.group(2))
        playground = SavedFile(match.group(1), section='playgroundsources', fix=True, filename=filename)
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
    elif re.search(r'^https*://', str(file_reference)):
        #logmessage(str(file_reference) + " is a URL")
        m = re.search('(\.[A-Za-z0-9]+)$', file_reference)
        if m:
            suffix = m.group(1)
        else:
            suffix = '.html'
        result = dict(tempfile=tempfile.NamedTemporaryFile(suffix=suffix))
        urllib.urlretrieve(file_reference, result['tempfile'].name)
        result['fullpath'] = result['tempfile'].name
        #logmessage("Downloaded to " + result['tempfile'].name)
    else:
        #logmessage(str(file_reference) + " is not a URL")
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
        result['fullpath'] = docassemble.base.functions.static_filename_path(file_reference)
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

docassemble.base.parse.set_file_finder(get_info_from_file_reference)

if in_celery:
    LOGFILE = daconfig.get('celery_flask_log', '/tmp/celery-flask.log')
else:
    LOGFILE = daconfig.get('flask_log', '/tmp/flask.log')

error_file_handler = logging.FileHandler(filename=LOGFILE)
error_file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(error_file_handler)

#sys.stderr.write("__name__ is " + str(__name__) + " and __package__ is " + str(__package__) + "\n")

def flask_logger(message):
    #app.logger.warning(message)
    sys.stderr.write(unicode(message) + "\n")
    return

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

def nice_date_from_utc(timestamp, timezone=tz.tzlocal()):
    return timestamp.replace(tzinfo=tz.tzutc()).astimezone(timezone).strftime('%x %X')


