from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.base.config import daconfig, hostname, in_celery
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype
from docassemble.base.logger import logmessage
from docassemble.webapp.users.models import UserModel, ChatLog, UserDict, UserDictKeys
from docassemble.webapp.core.models import Uploads, SpeakList, ObjectStorage, Shortener, MachineLearning #Attachments
from docassemble.base.generate_key import random_string
from sqlalchemy import or_, and_
import docassemble.webapp.database
import logging
import cPickle as pickle
import codecs
#import string
#import random
import pprint
import datetime
import json
import types
from Crypto.Cipher import AES
from Crypto import Random
from dateutil import tz
import tzlocal

import docassemble.base.parse
import re
import os
import sys
from flask import session, current_app, has_request_context, url_for
from flask_mail import Mail as FlaskMail, Message
from flask_wtf.csrf import generate_csrf
from flask_login import current_user
import docassemble.webapp.worker
from docassemble.webapp.mailgun_mail import Mail as MailgunMail

#sys.stderr.write("I am in backend\n")

import docassemble.webapp.setup

DEBUG = daconfig.get('debug', False)
#docassemble.base.parse.debug = DEBUG

from docassemble.webapp.file_access import get_info_from_file_number, get_info_from_file_reference, reference_exists, url_if_exists
from docassemble.webapp.file_number import get_new_file_number

def write_record(key, data):
    new_record = ObjectStorage(key=key, value=pack_object(data))
    db.session.add(new_record)
    db.session.commit()
    return new_record.id

def read_records(key):
    results = dict()
    for record in ObjectStorage.query.filter_by(key=key).order_by(ObjectStorage.id):
        results[record.id] = unpack_object(record.value)
    return results

def delete_record(key, id):
    ObjectStorage.query.filter_by(key=key, id=id).delete()
    db.session.commit()

def save_numbered_file(filename, orig_path, yaml_file_name=None, uid=None):
    if uid is None:
        if has_request_context() and 'uid' in session:
            uid = session.get('uid', None)
        else:
            uid = docassemble.base.functions.get_uid()
    if uid is None:
        raise Exception("save_numbered_file: uid not defined")
    file_number = get_new_file_number(uid, filename, yaml_file_name=yaml_file_name)
    extension, mimetype = get_ext_and_mimetype(filename)
    new_file = SavedFile(file_number, extension=extension, fix=True)
    new_file.copy_from(orig_path)
    new_file.save(finalize=True)
    return(file_number, extension, mimetype)

def fix_ml_files(playground_number):
    playground = SavedFile(playground_number, section='playgroundsources', fix=False)
    changed = False
    for filename in playground.list_of_files():
        if re.match(r'^ml-.*\.json', filename):
            playground.fix()
            try:
                if write_ml_source(playground, playground_number, filename, finalize=False):
                    changed = True
            except:
                logmessage("Error writing machine learning source file " + str(filename))
    if changed:
        playground.finalize()

def is_package_ml(parts):
    if len(parts) == 3 and parts[0].startswith('docassemble.') and re.match(r'data/sources/.*\.json', parts[1]):
        return True
    return False

def write_ml_source(playground, playground_number, filename, finalize=True):
    if re.match(r'ml-.*\.json', filename):
        output = dict()
        prefix = 'docassemble.playground' + str(playground_number) + ':data/sources/' + str(filename)
        for record in db.session.query(MachineLearning.group_id, MachineLearning.independent, MachineLearning.dependent, MachineLearning.key).filter(MachineLearning.group_id.like(prefix + ':%')):
            parts = record.group_id.split(':')
            if not is_package_ml(parts):
                continue
            if parts[2] not in output:
                output[parts[2]] = list()
            the_entry = dict(independent=pickle.loads(codecs.decode(record.independent, 'base64')), dependent=pickle.loads(codecs.decode(record.dependent, 'base64')))
            if record.key is not None:
                the_entry['key'] = record.key
            output[parts[2]].append(the_entry)
        if len(output):
            playground.write_as_json(output, filename=filename)
            if finalize:
                playground.finalize()
            return True
    return False

def absolute_filename(the_file):
    match = re.match(r'^docassemble.playground([0-9]+):(.*)', the_file)
    #logmessage("absolute_filename call: " + the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(2))
        #logmessage("absolute_filename: filename is " + filename)
        playground = SavedFile(match.group(1), section='playground', fix=True, filename=filename)
        return playground
    match = re.match(r'^/playgroundtemplate/([0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(2))
        playground = SavedFile(match.group(1), section='playgroundtemplate', fix=True, filename=filename)
        return playground
    match = re.match(r'^/playgroundstatic/([0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(2))
        playground = SavedFile(match.group(1), section='playgroundstatic', fix=True, filename=filename)
        return playground
    match = re.match(r'^/playgroundsources/([0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(2))
        playground = SavedFile(match.group(1), section='playgroundsources', fix=True, filename=filename)
        write_ml_source(playground, match.group(1), filename)
        return playground
    return(None)

if 'mailgun domain' in daconfig['mail'] and 'mailgun api key' in daconfig['mail']:
    mail = MailgunMail(app)
else:
    mail = FlaskMail(app)
    
def da_send_mail(the_message):
    mail.send(the_message)

import docassemble.webapp.machinelearning
import docassemble.base.functions
from docassemble.base.functions import dict_as_json
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'en_US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
if 'timezone' in daconfig and daconfig['timezone'] is not None:
    DEFAULT_TIMEZONE = daconfig['timezone']
else:
    try:
        DEFAULT_TIMEZONE = tzlocal.get_localzone().zone
    except:
        DEFAULT_TIMEZONE = 'America/New_York'

docassemble.base.functions.update_server(default_language=DEFAULT_LANGUAGE,
                                         default_locale=DEFAULT_LOCALE,
                                         default_dialect=DEFAULT_DIALECT,
                                         default_timezone=DEFAULT_TIMEZONE,
                                         default_country=daconfig.get('country', re.sub(r'\..*', r'', DEFAULT_LOCALE)),
                                         daconfig=daconfig,
                                         hostname=hostname,
                                         debug_status=DEBUG,
                                         save_numbered_file=save_numbered_file,
                                         send_mail=da_send_mail,
                                         absolute_filename=absolute_filename,
                                         write_record=write_record,
                                         read_records=read_records,
                                         delete_record=delete_record,
                                         generate_csrf=generate_csrf,
                                         url_for=url_for,
                                         get_new_file_number=get_new_file_number,
                                         get_ext_and_mimetype=get_ext_and_mimetype,
                                         file_finder=get_info_from_file_reference,
                                         file_number_finder=get_info_from_file_number)
docassemble.base.functions.set_language(DEFAULT_LANGUAGE, dialect=DEFAULT_DIALECT)
docassemble.base.functions.set_locale(DEFAULT_LOCALE)
docassemble.base.functions.update_locale()
if 'currency symbol' in daconfig:
    docassemble.base.functions.update_language_function('*', 'currency_symbol', lambda: daconfig['currency symbol'])

import docassemble.webapp.cloud
cloud = docassemble.webapp.cloud.get_cloud()

import docassemble.webapp.google_api

cloud_cache = dict()

def cloud_custom(provider, config):
    config_id = str(provider) + str(config)
    if config_id in cloud_cache:
        return cloud_cache[config_id]
    the_config = daconfig.get(config, None)
    if the_config is None or type(the_config) is not dict:
        logmessage("cloud_custom: invalid cloud configuration")
        return None
    cloud_cache[config_id] = docassemble.webapp.cloud.get_custom_cloud(provider, the_config)
    return cloud_cache[config_id]

docassemble.base.functions.update_server(cloud=cloud,
                                         cloud_custom=cloud_custom,
                                         google_api=docassemble.webapp.google_api)

initial_dict = dict(_internal=dict(progress=0, tracker=0, docvar=dict(), doc_cache=dict(), steps=1, steps_offset=0, secret=None, informed=dict(), livehelp=dict(availability='unavailable', mode='help', roles=list(), partner_roles=list()), answered=set(), answers=dict(), objselections=dict(), starttime=None, modtime=None, accesstime=dict(), tasks=dict(), gather=list(), event_stack=dict()), url_args=dict(), nav=docassemble.base.functions.DANav())
#else:
#    initial_dict = dict(_internal=dict(tracker=0, steps_offset=0, answered=set(), answers=dict(), objselections=dict()), url_args=dict())
if 'initial_dict' in daconfig:
    initial_dict.update(daconfig['initial dict'])
docassemble.base.parse.set_initial_dict(initial_dict)
from docassemble.base.functions import pickleable_objects

# def absolute_validator(the_file):
#     #logmessage("Running my validator")
#     if the_file.startswith(os.path.join(UPLOAD_DIRECTORY, 'playground')) and current_user.is_authenticated and not current_user.is_anonymous and current_user.has_role('admin', 'developer') and os.path.dirname(the_file) == os.path.join(UPLOAD_DIRECTORY, 'playground', str(current_user.id)):
#         return True
#     return False

#docassemble.base.parse.set_absolute_filename(absolute_filename)
#logmessage("Server started")

def can_access_file_number(file_number, uid=None):
    if current_user and current_user.is_authenticated and current_user.has_role('admin', 'developer', 'advocate', 'trainer'):
        return True
    if uid is None:
        if has_request_context() and 'uid' in session:
            uid = session.get('uid', None)
        else:
            uid = docassemble.base.functions.get_uid()
    if uid is None:
        raise Exception("can_access_file_number: uid not defined")
    upload = Uploads.query.filter(and_(Uploads.indexno == file_number, or_(Uploads.key == uid, Uploads.private == False))).first()
    if upload:
        return True
    return False

if in_celery:
    LOGFILE = daconfig.get('celery flask log', '/tmp/celery-flask.log')
else:
    LOGFILE = daconfig.get('flask log', '/tmp/flask.log')

if not os.path.exists(LOGFILE):
    with open(LOGFILE, 'a'):
        os.utime(LOGFILE, None)

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
    iv = current_app.secret_key[:16]
    encrypter = AES.new(secret, AES.MODE_CBC, iv)
    if isinstance(phrase, unicode):
        phrase = phrase.encode('utf8')
    return iv + codecs.encode(encrypter.encrypt(pad(phrase)), 'base64').decode()

def pack_phrase(phrase):
    return codecs.encode(phrase, 'base64').decode()

def decrypt_phrase(phrase_string, secret):
    decrypter = AES.new(secret, AES.MODE_CBC, str(phrase_string[:16]))
    return unpad(decrypter.decrypt(codecs.decode(phrase_string[16:], 'base64'))).decode('utf8')

def unpack_phrase(phrase_string):
    return codecs.decode(phrase_string, 'base64')

def encrypt_dictionary(the_dict, secret):
    #sys.stderr.write("40\n")
    iv = random_string(16)
    #iv = Random.new().read(AES.block_size)
    #sys.stderr.write("41\n")
    #sys.stderr.write("iv is " + str(iv) + "\n")
    #sys.stderr.write("block size is " + str(AES.block_size) + "\n")
    #sys.stderr.write("secret is " + str(repr(secret)) + "\n")
    encrypter = AES.new(secret, AES.MODE_CBC, iv)
    #sys.stderr.write("42\n")
    #one = pickleable_objects(the_dict)
    #sys.stderr.write("43\n")
    #two = pickle.dumps(one)
    #sys.stderr.write("44\n")
    #three = pad(two)
    #sys.stderr.write("45\n")
    #four = encrypter.encrypt(three)
    #sys.stderr.write("46\n")
    #logmessage(pprint.pformat(pickleable_objects(the_dict)))
    return iv + codecs.encode(encrypter.encrypt(pad(pickle.dumps(pickleable_objects(the_dict)))), 'base64').decode()

def pack_object(the_object):
    return codecs.encode(pickle.dumps(safe_pickle(the_object)), 'base64').decode()

def unpack_object(the_string):
    return pickle.loads(codecs.decode(the_string, 'base64'))

def safe_pickle(the_object):
    if type(the_object) is list:
        return [safe_pickle(x) for x in the_object]
    if type(the_object) is dict:
        new_dict = dict()
        for key, value in the_object.iteritems():
            new_dict[key] = safe_pickle(value)
        return new_dict
    if type(the_object) is set:
        new_set = set()
        for sub_object in the_object:
            new_set.add(safe_pickle(sub_object))
        return new_set
    if type(the_object) in [types.ModuleType, types.FunctionType, types.TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, types.ClassType, file]:
        return None
    return the_object

def pack_dictionary(the_dict):
    # sys.stderr.write("pack_dictionary keys:\n")
    # for key in pickleable_objects(the_dict):
    #     sys.stderr.write("  " + key + ": " + pprint.pformat(the_dict[key]) + "\n")
    return codecs.encode(pickle.dumps(pickleable_objects(the_dict)), 'base64').decode()

def decrypt_dictionary(dict_string, secret):
    #sys.stderr.write("60\n")
    #sys.stderr.write("secret is " + str(repr(secret)) + "\n")
    decrypter = AES.new(secret, AES.MODE_CBC, str(dict_string[:16]))
    #sys.stderr.write("61\n")
    #one = codecs.decode(dict_string[16:], 'base64')
    #sys.stderr.write("62\n")
    #two = decrypter.decrypt(one)
    #sys.stderr.write("63\n")
    #three = unpad(two)
    #sys.stderr.write("64\n")
    #four = pickle.loads(three)
    #sys.stderr.write(pprint.pformat(four, depth=4, indent=4) + "\n")
    #sys.stderr.write(json.dumps(four) + "\n")
    #sys.stderr.write("65\n")
    #return four
    return pickle.loads(unpad(decrypter.decrypt(codecs.decode(dict_string[16:], 'base64'))))

def unpack_dictionary(dict_string):
    return pickle.loads(codecs.decode(dict_string, 'base64'))

def nice_date_from_utc(timestamp, timezone=tz.tzlocal()):
    return timestamp.replace(tzinfo=tz.tzutc()).astimezone(timezone).strftime('%x %X')

def nice_utc_date(timestamp, timezone=tz.tzlocal()):
    return timestamp.strftime('%F %T')

def fetch_user_dict(user_code, filename, secret=None):
    #logmessage("fetch_user_dict: user_code is " + str(user_code) + " and filename is " + str(filename))
    user_dict = None
    steps = 1
    encrypted = True
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('count')).filter(and_(UserDict.key == user_code, UserDict.filename == filename)).subquery()
    results = db.session.query(UserDict.indexno, UserDict.dictionary, UserDict.encrypted, subq.c.count).join(subq, subq.c.indexno == UserDict.indexno)
    #logmessage("fetch_user_dict: 01 query is " + str(results))
    for d in results:
        #logmessage("fetch_user_dict: indexno is " + str(d.indexno))
        if d.dictionary:
            if d.encrypted:
                #logmessage("fetch_user_dict: entry was encrypted")
                user_dict = decrypt_dictionary(d.dictionary, secret)
                #logmessage("fetch_user_dict: decrypted dictionary")
            else:
                #logmessage("fetch_user_dict: entry was not encrypted")
                user_dict = unpack_dictionary(d.dictionary)
                #logmessage("fetch_user_dict: unpacked dictionary")
                encrypted = False
        if d.count:
            steps = d.count
        break
    return steps, user_dict, encrypted

def user_dict_exists(user_code, filename):
    result = UserDict.query.filter(and_(UserDict.key == user_code, UserDict.filename == filename)).first()
    if result:
        return True
    return False

def fetch_previous_user_dict(user_code, filename, secret):
    user_dict = None
    max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(and_(UserDict.key == user_code, UserDict.filename == filename)).scalar()
    if max_indexno is not None:
        UserDict.query.filter_by(indexno=max_indexno).delete()
        db.session.commit()
    return fetch_user_dict(user_code, filename, secret=secret)

def advance_progress(user_dict):
    user_dict['_internal']['progress'] += 0.05*(100-user_dict['_internal']['progress'])
    return

def reset_user_dict(user_code, filename, user_id=None, temp_user_id=None, force=False):
    #logmessage("reset_user_dict called with " + str(user_code) + " and " + str(filename))
    if force:
        the_user_id = None
    else:
        if user_id is None and temp_user_id is None:
            if current_user.is_authenticated and not current_user.is_anonymous:
                user_type = 'user'
                the_user_id = current_user.id
            else:
                user_type = 'tempuser'
                the_user_id = session.get('tempuser', None)
        elif user_id is not None:
            user_type = 'user'
            the_user_id = user_id
        else:
            user_type = 'tempuser'
            the_user_id = temp_user_id
    if the_user_id is None:
        UserDictKeys.query.filter_by(key=user_code, filename=filename).delete()
        db.session.commit()
        do_delete = True
    else:
        if user_type == 'user':
            UserDictKeys.query.filter_by(key=user_code, filename=filename, user_id=the_user_id).delete()
        else:
            UserDictKeys.query.filter_by(key=user_code, filename=filename, temp_user_id=the_user_id).delete()
        db.session.commit()
        existing_user_dict_key = UserDictKeys.query.filter_by(key=user_code, filename=filename).first()
        if not existing_user_dict_key:
            do_delete = True
        else:
            do_delete = False
    if do_delete:
        UserDict.query.filter_by(key=user_code, filename=filename).delete()
        db.session.commit()
        for upload in Uploads.query.filter_by(key=user_code, yamlfile=filename, persistent=False).all():
            old_file = SavedFile(upload.indexno)
            old_file.delete()
        Uploads.query.filter_by(key=user_code, yamlfile=filename, persistent=False).delete()
        db.session.commit()
        # Attachments.query.filter_by(key=user_code, filename=filename).delete()
        # db.session.commit()
        SpeakList.query.filter_by(key=user_code, filename=filename).delete()
        db.session.commit()
        ChatLog.query.filter_by(key=user_code, filename=filename).delete()
        db.session.commit()
        Shortener.query.filter_by(uid=user_code, filename=filename).delete()
        db.session.commit()
    #logmessage("reset_user_dict: done")
    return

def get_person(user_id, cache):
    if user_id in cache:
        return cache[user_id]
    for record in UserModel.query.filter_by(id=user_id):
        cache[record.id] = record
        return record
    return None

def get_chat_log(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, self_temp_id):
    messages = list()
    people = dict()
    if user_id is not None:
        if get_person(user_id, people) is None:
            return list()
        chat_person_type = 'auth'
        chat_person_id = user_id
    else:
        chat_person_type = 'anon'
        chat_person_id = temp_user_id
    if self_user_id is not None:
        if get_person(self_user_id, people) is None:
            return list()
        self_person_type = 'auth'
        self_person_id = self_user_id
    else:
        self_person_type = 'anon'
        self_person_id = self_temp_id
    if chat_mode in ['peer', 'peerhelp']:
        open_to_peer = True
    else:
        open_to_peer = False
    if chat_person_type == 'auth':
        if chat_mode in ['peer', 'peerhelp']:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.owner_id == chat_person_id))).order_by(ChatLog.id).all()
        else:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.owner_id == chat_person_id)).order_by(ChatLog.id).all()
        for record in records:
            if record.encrypted:
                try:
                    message = decrypt_phrase(record.message, secret)
                except:
                    sys.stderr.write("Could not decrypt phrase with secret " + secret + "\n")
                    continue
            else:
                message = unpack_phrase(record.message)
            modtime = nice_utc_date(record.modtime)
            if self_person_type == 'auth':
                if self_person_id == record.user_id:
                    is_self = True
                else:
                    is_self = False
            else:
                if self_person_id == record.temp_user_id:
                    is_self = True
                else:
                    is_self = False
            if record.user_id is not None:
                person = get_person(record.user_id, people)
                if person is None:
                    sys.stderr.write("Person " + str(record.user_id) + " did not exist\n")
                    continue
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=message, roles=[role.name for role in person.roles]))
            else:
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, modtime=modtime, message=message, roles=['user']))
    else:
        if chat_mode in ['peer', 'peerhelp']:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.temp_owner_id == chat_person_id))).order_by(ChatLog.id).all()
        else:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.temp_owner_id == chat_person_id)).order_by(ChatLog.id).all()
        for record in records:
            if record.encrypted:
                try:
                    message = decrypt_phrase(record.message, secret)
                except:
                    sys.stderr.write("Could not decrypt phrase with secret " + secret + "\n")
                    continue
            else:
                message = unpack_phrase(record.message)
            modtime = nice_utc_date(record.modtime)
            if self_person_type == 'auth':
                if self_person_id == record.user_id:
                    is_self = True
                else:
                    is_self = False
            else:
                #logmessage("self person id is " + str(self_person_id) + " and record user id is " + str(record.temp_user_id))
                if self_person_id == record.temp_user_id:
                    is_self = True
                else:
                    is_self = False
            if record.user_id is not None:
                person = get_person(record.user_id, people)
                if person is None:
                    sys.stderr.write("Person " + str(record.user_id) + " did not exist\n")
                    continue
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=message, roles=[role.name for role in person.roles]))
            else:
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, modtime=modtime, message=message, roles=['user']))
    return messages

def file_set_attributes(file_number, **kwargs):
    upload = Uploads.query.filter_by(indexno=file_number).first()
    if upload is None:
        raise Exception("file_set_attributes: file number " + str(file_number) + " not found.")
    changed = False
    if 'private' in kwargs and kwargs['private'] in [True, False] and upload.private != kwargs['private']:
        upload.private = kwargs['private']
        changed = True
    if 'persistent' in kwargs and kwargs['persistent'] in [True, False] and upload.persistent != kwargs['persistent']:
        upload.persistent = kwargs['persistent']
        changed = True
    if 'session' in kwargs and type(kwargs['session']) in (str, unicode):
        upload.key = kwargs['session']
    if 'filename' in kwargs and type(kwargs['filename']) in (str, unicode):
        upload.filename = kwargs['filename']
    if changed:
        db.session.commit()
