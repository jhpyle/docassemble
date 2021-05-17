from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.base.config import daconfig, hostname, in_celery
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype
from docassemble.base.logger import logmessage
from docassemble.webapp.users.models import UserModel, Role, ChatLog, UserDict, UserDictKeys, UserAuthModel, UserRoles
from docassemble.webapp.core.models import Uploads, UploadsUserAuth, UploadsRoleAuth, SpeakList, ObjectStorage, Shortener, MachineLearning, GlobalObjectStorage, Email, EmailAttachment
from docassemble.webapp.packages.models import PackageAuth
from docassemble.base.generate_key import random_string, random_bytes, random_alphanumeric
from sqlalchemy import or_, and_, select, delete
import docassemble.webapp.database
import logging
import pickle
from io import IOBase as FileType
import codecs
#import string
#import random
import pprint
import datetime
import json
import types
from Cryptodome.Cipher import AES
from Cryptodome import Random
from dateutil import tz
import tzlocal
import ruamel.yaml
TypeType = type(type(None))
NoneType = type(None)

import docassemble.base.parse
import re
import os
import sys
from flask import session, current_app, has_request_context, url_for as base_url_for
from flask_mail import Mail as FlaskMail, Message
from flask_wtf.csrf import generate_csrf
from flask_login import current_user
import docassemble.webapp.worker
from docassemble.webapp.mailgun_mail import Mail as MailgunMail
from docassemble.webapp.sendgrid_mail import Mail as SendgridMail
from docassemble.webapp.fixpickle import fix_pickle_obj, fix_pickle_dict
from docassemble.webapp.screenreader import to_text
import pandas
import math
import xml.etree.ElementTree as ET

#sys.stderr.write("I am in backend\n")

import docassemble.webapp.setup

DEBUG = daconfig.get('debug', False)
#docassemble.base.parse.debug = DEBUG

from docassemble.webapp.file_access import get_info_from_file_number, get_info_from_file_reference, reference_exists, url_if_exists
from docassemble.webapp.file_number import get_new_file_number

import time

def elapsed(name_of_function):
    def elapse_decorator(func):
        def time_func(*pargs, **kwargs):
            time_start = time.time()
            result = func(*pargs, **kwargs)
            sys.stderr.write(name_of_function + ': ' + str(time.time() - time_start) + "\n")
            return result
        return time_func
    return elapse_decorator

def write_record(key, data):
    new_record = ObjectStorage(key=key, value=pack_object(data))
    db.session.add(new_record)
    db.session.commit()
    return new_record.id

def read_records(key):
    results = dict()
    for record in db.session.execute(select(ObjectStorage).filter_by(key=key).order_by(ObjectStorage.id)).scalars():
        results[record.id] = unpack_object(record.value)
    return results

def delete_record(key, id):
    db.session.execute(delete(ObjectStorage).filter_by(key=key, id=id))
    db.session.commit()

#@elapsed('save_numbered_file')
def save_numbered_file(filename, orig_path, yaml_file_name=None, uid=None):
    if uid is None:
        try:
            uid = docassemble.base.functions.get_uid()
            assert uid is not None
        except:
            uid = unattached_uid()
    if uid is None:
        raise Exception("save_numbered_file: uid not defined")
    file_number = get_new_file_number(uid, filename, yaml_file_name=yaml_file_name)
    extension, mimetype = get_ext_and_mimetype(filename)
    new_file = SavedFile(file_number, extension=extension, fix=True)
    new_file.copy_from(orig_path)
    new_file.save(finalize=True)
    return(file_number, extension, mimetype)

def fix_ml_files(playground_number, current_project):
    playground = SavedFile(playground_number, section='playgroundsources', fix=False)
    changed = False
    for filename in playground.list_of_files():
        if re.match(r'^ml-.*\.json', filename):
            playground.fix()
            try:
                if write_ml_source(playground, playground_number, current_project, filename, finalize=False):
                    changed = True
            except:
                logmessage("Error writing machine learning source file " + str(filename))
    if changed:
        playground.finalize()

def is_package_ml(parts):
    if len(parts) == 3 and parts[0].startswith('docassemble.') and re.match(r'data/sources/.*\.json', parts[1]):
        return True
    return False

def project_name(name):
    return '' if name == 'default' else name

def add_project(filename, current_project):
    if current_project == 'default':
        return filename
    else:
        return os.path.join(current_project, filename)

def directory_for(area, current_project):
    if current_project == 'default':
        return area.directory
    else:
        return os.path.join(area.directory, current_project)

def write_ml_source(playground, playground_number, current_project, filename, finalize=True):
    if re.match(r'ml-.*\.json', filename):
        output = dict()
        prefix = 'docassemble.playground' + str(playground_number) + project_name(current_project) + ':data/sources/' + str(filename)
        for record in db.session.execute(select(MachineLearning.group_id, MachineLearning.independent, MachineLearning.dependent, MachineLearning.key).where(MachineLearning.group_id.like(prefix + ':%'))).all():
            parts = record.group_id.split(':')
            if not is_package_ml(parts):
                continue
            if parts[2] not in output:
                output[parts[2]] = list()
            the_independent = record.independent
            if the_independent is not None:
                the_independent = fix_pickle_obj(codecs.decode(bytearray(the_independent, encoding='utf-8'), 'base64'))
            the_dependent = record.dependent
            if the_dependent is not None:
                the_dependent = fix_pickle_obj(codecs.decode(bytearray(the_dependent, encoding='utf-8'), 'base64'))
            the_entry = dict(independent=the_independent, dependent=the_dependent)
            if record.key is not None:
                the_entry['key'] = record.key
            output[parts[2]].append(the_entry)
        if len(output):
            playground.write_as_json(output, filename=os.path.join(directory_for(playground, current_project), filename))
            if finalize:
                playground.finalize()
            return True
    return False

def absolute_filename(the_file):
    match = re.match(r'^docassemble.playground([0-9]+)([A-Za-z]?[A-Za-z0-9]*):(.*)', the_file)
    #logmessage("absolute_filename call: " + the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        #logmessage("absolute_filename: filename is " + filename + " and subdir is " + match.group(2))
        playground = SavedFile(match.group(1), section='playground', fix=True, filename=filename, subdir=match.group(2))
        return playground
    match = re.match(r'^/playgroundtemplate/([0-9]+)/([A-Za-z0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        playground = SavedFile(match.group(1), section='playgroundtemplate', fix=True, filename=filename, subdir=match.group(2))
        return playground
    match = re.match(r'^/playgroundstatic/([0-9]+)/([A-Za-z0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        playground = SavedFile(match.group(1), section='playgroundstatic', fix=True, filename=filename, subdir=match.group(2))
        return playground
    match = re.match(r'^/playgroundsources/([0-9]+)/([A-Za-z0-9]+)/(.*)', the_file)
    if match:
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', match.group(3))
        playground = SavedFile(match.group(1), section='playgroundsources', fix=True, filename=filename, subdir=match.group(2))
        write_ml_source(playground, match.group(1), match.group(2), filename)
        return playground
    return(None)

if 'mailgun domain' in daconfig['mail'] and 'mailgun api key' in daconfig['mail']:
    mail = MailgunMail(app)
elif 'sendgrid api key' in daconfig['mail'] and daconfig['mail']['sendgrid api key']:
    mail = SendgridMail(app)
else:
    mail = FlaskMail(app)

def da_send_mail(the_message):
    mail.send(the_message)

import docassemble.webapp.machinelearning
import docassemble.base.functions
import docassemble.webapp.user_database
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

COOKIELESS_SESSIONS = daconfig.get('cookieless sessions', False)

def url_for(*pargs, **kwargs):
    if 'jsembed' in docassemble.base.functions.this_thread.misc:
        kwargs['_external'] = True
        if pargs[0] == 'index':
            kwargs['js_target'] = docassemble.base.functions.this_thread.misc['jsembed']
    if COOKIELESS_SESSIONS:
        if pargs[0] == 'index':
            pargs = list(pargs)
            pargs[0] = 'html_index'
        kwargs['_external'] = True
    return base_url_for(*pargs, **kwargs)

def sql_get(key, secret=None):
    for record in db.session.execute(select(GlobalObjectStorage).filter_by(key=key)).scalars():
        if record.encrypted:
            try:
                result = decrypt_object(record.value, secret)
            except:
                raise Exception("Unable to decrypt stored object.")
        else:
            try:
                result = unpack_object(record.value)
            except:
                raise Exception("Unable to unpack stored object.")
        return result
    return None

def sql_defined(key):
    record = db.session.execute(select(GlobalObjectStorage.id).filter_by(key=key)).first()
    if record is None:
        return False
    return True

def sql_set(key, val, encrypted=True, secret=None, the_user_id=None):
    user_id, temp_user_id = parse_the_user_id(the_user_id)
    updated = False
    for record in db.session.execute(select(GlobalObjectStorage).filter_by(key=key).with_for_update()).scalars():
        record.user_id = user_id
        record.temp_user_id = temp_user_id
        record.encrypted = encrypted
        if encrypted:
            record.value = encrypt_object(val, secret)
        else:
            record.value = pack_object(val)
        updated = True
    if not updated:
        if encrypted:
            record = GlobalObjectStorage(key=key, value=encrypt_object(val, secret), encrypted=True, user_id=user_id, temp_user_id=temp_user_id)
        else:
            record = GlobalObjectStorage(key=key, value=pack_object(val), encrypted=False, user_id=user_id, temp_user_id=temp_user_id)
        db.session.add(record)
    db.session.commit()

def sql_delete(key):
    db.session.execute(delete(GlobalObjectStorage).filter_by(key=key))
    db.session.commit()

def sql_keys(prefix):
    n = len(prefix)
    stmt = select(GlobalObjectStorage.key).where(GlobalObjectStorage.key.like(prefix + '%'))
    return list(set([y.key[n:] for y in db.session.execute(stmt)]))

def get_info_from_file_reference_with_uids(*pargs, **kwargs):
    if 'uids' not in kwargs:
        kwargs['uids'] = get_session_uids()
    return get_info_from_file_reference(*pargs, **kwargs)

def get_info_from_file_number_with_uids(*pargs, **kwargs):
    if 'uids' not in kwargs:
        kwargs['uids'] = get_session_uids()
    return get_info_from_file_number(*pargs, **kwargs)


classes = daconfig['table css class'].split(',')
DEFAULT_TABLE_CLASS = json.dumps(classes[0].strip())
if len(classes) > 1:
    DEFAULT_THEAD_CLASS = json.dumps(classes[1].strip())
else:
    DEFAULT_THEAD_CLASS = None
del classes

DEFAULT_COUNTRY = daconfig.get('country', None) or re.sub(r'^.*_', '', re.sub(r'\..*', r'', DEFAULT_LOCALE))


docassemble.base.functions.update_server(default_language=DEFAULT_LANGUAGE,
                                         default_locale=DEFAULT_LOCALE,
                                         default_dialect=DEFAULT_DIALECT,
                                         default_timezone=DEFAULT_TIMEZONE,
                                         default_country=DEFAULT_COUNTRY,
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
                                         file_finder=get_info_from_file_reference_with_uids,
                                         file_number_finder=get_info_from_file_number_with_uids,
                                         server_sql_get=sql_get,
                                         server_sql_defined=sql_defined,
                                         server_sql_set=sql_set,
                                         server_sql_delete=sql_delete,
                                         server_sql_keys=sql_keys,
                                         alchemy_url=docassemble.webapp.user_database.alchemy_url,
                                         connect_args=docassemble.webapp.user_database.connect_args,
                                         default_table_class=DEFAULT_TABLE_CLASS,
                                         default_thead_class=DEFAULT_THEAD_CLASS,
                                         to_text=to_text)
docassemble.base.functions.set_language(DEFAULT_LANGUAGE, dialect=DEFAULT_DIALECT)
docassemble.base.functions.set_locale(DEFAULT_LOCALE)
docassemble.base.functions.update_locale()

word_file_list = daconfig.get('words', list())
if type(word_file_list) is not list:
    word_file_list = [word_file_list]
for word_file in word_file_list:
    #sys.stderr.write("Reading from " + str(word_file) + "\n")
    if not isinstance(word_file, str):
        sys.stderr.write("Error reading words: file references must be plain text.\n")
        continue
    filename = docassemble.base.functions.static_filename_path(word_file)
    if filename is None:
        sys.stderr.write("Error reading " + str(word_file) + ": file not found.\n")
        continue
    if os.path.isfile(filename):
        if filename.lower().endswith('.yaml') or filename.lower().endswith('.yml'):
            with open(filename, 'r', encoding='utf-8') as stream:
                try:
                    for document in ruamel.yaml.safe_load_all(stream):
                        if document and type(document) is dict:
                            for lang, words in document.items():
                                if type(words) is dict:
                                    docassemble.base.functions.update_word_collection(lang, words)
                                else:
                                    sys.stderr.write("Error reading " + str(word_file) + ": words not in dictionary form.\n")
                        else:
                            sys.stderr.write("Error reading " + str(word_file) + ": yaml file not in dictionary form.\n")
                except:
                    sys.stderr.write("Error reading " + str(word_file) + ": yaml could not be processed.\n")
        elif filename.lower().endswith('.xlsx'):
            try:
                df = pandas.read_excel(filename, na_values=['#NA', '#N/A'], keep_default_na=False)
                invalid = False
                for column_name in ('orig_lang', 'tr_lang', 'orig_text', 'tr_text'):
                    if column_name not in df.columns:
                        invalid = True
                        break
                if invalid:
                    sys.stderr.write("Error reading " + str(word_file) + ": xlsx did not have the correct columns.\n")
                    continue
                translations = dict()
                problems = list()
                for indexno in df.index:
                    try:
                        assert df['orig_lang'][indexno]
                        assert df['tr_lang'][indexno]
                        assert df['orig_text'][indexno] != ''
                        assert df['tr_text'][indexno] != ''
                        if isinstance(df['orig_text'][indexno], float):
                            assert not math.isnan(df['orig_text'][indexno])
                        if isinstance(df['tr_text'][indexno], float):
                            assert not math.isnan(df['tr_text'][indexno])
                    except:
                        problems.append(str(indexno + 2))
                        continue
                    if df['tr_lang'][indexno] not in translations:
                        translations[df['tr_lang'][indexno]] = dict()
                    translations[df['tr_lang'][indexno]][str(df['orig_text'][indexno])] = str(df['tr_text'][indexno])
                for lang, the_dict in translations.items():
                    try:
                        docassemble.base.functions.update_word_collection(lang, the_dict)
                    except:
                        sys.stderr.write("Error reading " + str(word_file) + ": xlsx for language " + lang + " could not be processed.\n")
                if len(problems) > 0:
                    sys.stderr.write("Error reading " + str(word_file) + ": could not read lines " + ", ".join(problems) + ".\n")
            except Exception as err:
                sys.stderr.write("Error reading " + str(word_file) + ": xlsx processing raised exception " + err.__class__.__name__ + ": " + str(err) + "\n")
        elif filename.lower().endswith('.xlf') or filename.lower().endswith('.xliff'):
            try:
                tree = ET.parse(filename)
                root = tree.getroot()
                translations = dict()
                if root.attrib['version'] == "1.2":
                    for the_file in root.iter('{urn:oasis:names:tc:xliff:document:1.2}file'):
                        source_lang = the_file.attrib.get('source-language', 'en')
                        target_lang = the_file.attrib.get('target-language', 'en')
                        if target_lang not in translations:
                            translations[target_lang] = dict()
                        for transunit in the_file.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
                            orig_text = ''
                            tr_text = ''
                            for source in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}source'):
                                if source.text:
                                    orig_text += source.text
                                for mrk in source:
                                    orig_text += mrk.text
                                    if mrk.tail:
                                        orig_text += mrk.tail
                            for target in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}target'):
                                if target.text:
                                    tr_text += target.text
                                for mrk in target:
                                    tr_text += mrk.text
                                    if mrk.tail:
                                        tr_text += mrk.tail
                            if orig_text == '' or tr_text == '':
                                continue
                            translations[target_lang][orig_text] = tr_text
                elif root.attrib['version'] == "2.0":
                    source_lang = root.attrib['srcLang']
                    target_lang = root.attrib['trgLang']
                    if target_lang not in translations:
                        translations[target_lang] = dict()
                    for segment in root.iter('{urn:oasis:names:tc:xliff:document:2.0}segment'):
                        orig_text = ''
                        tr_text = ''
                        for source in segment.iter('{urn:oasis:names:tc:xliff:document:2.0}source'):
                            if source.text:
                                orig_text += source.text
                            for mrk in source:
                                orig_text += mrk.text
                                if mrk.tail:
                                    orig_text += mrk.tail
                        for target in segment.iter('{urn:oasis:names:tc:xliff:document:2.0}target'):
                            if target.text:
                                tr_text += target.text
                            for mrk in target:
                                tr_text += mrk.text
                                if mrk.tail:
                                    tr_text += mrk.tail
                        if orig_text == '' or tr_text == '':
                            continue
                        translations[target_lang][orig_text] = tr_text
                else:
                    sys.stderr.write("Error reading " + str(word_file) + ": invalid XLIFF version.\n")
                for lang, the_dict in translations.items():
                    try:
                        docassemble.base.functions.update_word_collection(lang, the_dict)
                    except:
                        sys.stderr.write("Error reading " + str(word_file) + ": xlf for language " + lang + " could not be processed.\n")
            except Exception as err:
                sys.stderr.write("Error reading " + str(word_file) + ": xlf processing raised exception " + err.__class__.__name__ + ": " + str(err) + "\n")
        else:
            sys.stderr.write("filename " + filename + " had an unknown type\n")
    else:
        sys.stderr.write("filename " + filename + " did not exist\n")

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

initial_dict = dict(_internal=dict(session_local=dict(), device_local=dict(), user_local=dict(), dirty=dict(), progress=0, tracker=0, docvar=dict(), doc_cache=dict(), steps=1, steps_offset=0, secret=None, informed=dict(), livehelp=dict(availability='unavailable', mode='help', roles=list(), partner_roles=list()), answered=set(), answers=dict(), objselections=dict(), starttime=None, modtime=None, accesstime=dict(), tasks=dict(), gather=list(), event_stack=dict(), misc=dict()), url_args=dict(), nav=docassemble.base.functions.DANav())
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

#@elapsed('can_access_file_number')
def can_access_file_number(file_number, uids=None):
    upload = db.session.execute(select(Uploads).where(Uploads.indexno == file_number)).scalar()
    if upload is None:
        return False
    if current_user and current_user.is_authenticated and current_user.has_role('admin', 'developer', 'advocate', 'trainer'):
        return True
    if not upload.private:
        return True
    if uids is None or len(uids) == 0:
        new_uid = docassemble.base.functions.get_uid()
        if new_uid is not None:
            uids = [new_uid]
        else:
            uids = []
    if upload.key in uids:
        return True
    if current_user and current_user.is_authenticated:
        if db.session.execute(select(UserDictKeys).filter_by(key=upload.key, user_id=current_user.id)).first() or db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=current_user.id)).first() or db.session.execute(select(UploadsRoleAuth).join(UserRoles, and_(UserRoles.user_id == current_user.id, UploadsRoleAuth.role_id == UserRoles.role_id)).where(UploadsRoleAuth.uploads_indexno == file_number)).first():
            return True
    elif session and 'tempuser' in session:
        temp_user_id = int(session['tempuser'])
        if db.session.execute(select(UserDictKeys).filter_by(key=upload.key, temp_user_id=temp_user_id)).first() or db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, temp_user_id=temp_user_id)).first():
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
    sys.stderr.write(str(message) + "\n")
    return

def pad(the_string):
    return the_string + bytearray((16 - len(the_string) % 16) * chr(16 - len(the_string) % 16), encoding='utf-8')

def unpad(the_string):
    if isinstance(the_string[-1], int):
        return the_string[0:-the_string[-1]]
    else:
        return the_string[0:-ord(the_string[-1])]

def encrypt_phrase(phrase, secret):
    iv = random_bytes(16)
    encrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, iv)
    if isinstance(phrase, str):
        phrase = bytearray(phrase, 'utf-8')
    return (iv + codecs.encode(encrypter.encrypt(pad(phrase)), 'base64')).decode('utf-8')

def pack_phrase(phrase):
    phrase = bytearray(phrase, encoding='utf-8')
    return codecs.encode(phrase, 'base64').decode('utf-8')

def decrypt_phrase(phrase_string, secret):
    phrase_string = bytearray(phrase_string, encoding='utf-8')
    decrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, phrase_string[:16])
    return unpad(decrypter.decrypt(codecs.decode(phrase_string[16:], 'base64'))).decode('utf-8')

def unpack_phrase(phrase_string):
    return codecs.decode(bytearray(phrase_string, encoding='utf-8'), 'base64').decode('utf-8')

def encrypt_dictionary(the_dict, secret):
    iv = random_bytes(16)
    encrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, iv)
    return (iv + codecs.encode(encrypter.encrypt(pad(pickle.dumps(pickleable_objects(the_dict)))), 'base64')).decode()

def pack_object(the_object):
    return codecs.encode(pickle.dumps(safe_pickle(the_object)), 'base64').decode()

def unpack_object(the_string):
    the_string = bytearray(the_string, encoding='utf-8')
    return fix_pickle_dict(codecs.decode(the_string, 'base64'))

def encrypt_object(obj, secret):
    iv = random_bytes(16)
    encrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, iv)
    return (iv + codecs.encode(encrypter.encrypt(pad(pickle.dumps(safe_pickle(obj)))), 'base64')).decode()

def decrypt_object(obj_string, secret):
    obj_string = bytearray(obj_string, encoding='utf-8')
    decrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, obj_string[:16])
    return fix_pickle_obj(unpad(decrypter.decrypt(codecs.decode(obj_string[16:], 'base64'))))

def parse_the_user_id(the_user_id):
    m = re.match(r'(t?)([0-9]+)', str(the_user_id))
    if m:
        if m.group(1) == 't':
            return None, int(m.group(2))
        else:
            return int(m.group(2)), None
    raise Exception("Invalid user ID")

def safe_pickle(the_object):
    if type(the_object) is list:
        return [safe_pickle(x) for x in the_object]
    if type(the_object) is dict:
        new_dict = dict()
        for key, value in the_object.items():
            new_dict[key] = safe_pickle(value)
        return new_dict
    if type(the_object) is set:
        new_set = set()
        for sub_object in the_object:
            new_set.add(safe_pickle(sub_object))
        return new_set
    if type(the_object) in [types.ModuleType, types.FunctionType, TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, FileType]:
        return None
    return the_object

def pack_dictionary(the_dict):
    retval = codecs.encode(pickle.dumps(pickleable_objects(the_dict)), 'base64').decode()
    return retval

def decrypt_dictionary(dict_string, secret):
    dict_string = bytearray(dict_string, encoding='utf-8')
    decrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, dict_string[:16])
    return fix_pickle_dict(unpad(decrypter.decrypt(codecs.decode(dict_string[16:], 'base64'))))

def unpack_dictionary(dict_string):
    dict_string = codecs.decode(bytearray(dict_string, encoding='utf-8'), 'base64')
    return fix_pickle_dict(dict_string)

def nice_date_from_utc(timestamp, timezone=tz.tzlocal()):
    return timestamp.replace(tzinfo=tz.tzutc()).astimezone(timezone).strftime('%x %X')

def nice_utc_date(timestamp, timezone=tz.tzlocal()):
    return timestamp.strftime('%F %T')

#@elapsed('fetch_user_dict')
def fetch_user_dict(user_code, filename, secret=None):
    #logmessage("fetch_user_dict: user_code is " + str(user_code) + " and filename is " + str(filename))
    user_dict = None
    steps = 1
    encrypted = True
    subq = select(db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('cnt')).where(and_(UserDict.key == user_code, UserDict.filename == filename)).subquery()
    stmt = select(UserDict.indexno, UserDict.dictionary, UserDict.encrypted, subq.c.cnt).join(subq, subq.c.indexno == UserDict.indexno)
    result = db.session.execute(stmt)
    for d in [d for d in result]:
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
        if d.cnt:
            steps = d.cnt
        break
    return steps, user_dict, encrypted

#@elapsed('user_dict_exists')
def user_dict_exists(user_code, filename):
    result = db.session.execute(select(UserDict).where(and_(UserDict.key == user_code, UserDict.filename == filename))).first()
    if result:
        return True
    return False

#@elapsed('fetch_previous_user_dict')
def fetch_previous_user_dict(user_code, filename, secret):
    user_dict = None
    max_indexno = db.session.execute(select(db.func.max(UserDict.indexno)).where(and_(UserDict.key == user_code, UserDict.filename == filename))).scalar()
    if max_indexno is not None:
        db.session.execute(delete(UserDict).where(UserDict.indexno == max_indexno))
        db.session.commit()
    return fetch_user_dict(user_code, filename, secret=secret)

def advance_progress(user_dict, interview):
    if user_dict['_internal']['progress'] is None:
        return
    if hasattr(interview, 'progress_bar_multiplier'):
        multiplier = interview.progress_bar_multiplier
    else:
        multiplier = 0.05
    if hasattr(interview, 'progress_bar_method') and interview.progress_bar_method == 'stepped':
        next_part = 100.0
        for value in sorted(interview.progress_points):
            if value > user_dict['_internal']['progress']:
                next_part = value
                break
        user_dict['_internal']['progress'] += multiplier*(next_part-user_dict['_internal']['progress'])
    else:
        user_dict['_internal']['progress'] += multiplier*(100-user_dict['_internal']['progress'])
    return

def delete_temp_user_data(temp_user_id, r):
    db.session.execute(delete(UserDictKeys).where(UserDictKeys.temp_user_id == temp_user_id))
    db.session.commit()
    db.session.execute(delete(UploadsUserAuth).where(UploadsUserAuth.temp_user_id == temp_user_id))
    db.session.commit()
    db.session.execute(delete(ChatLog).where(ChatLog.temp_owner_id == temp_user_id))
    db.session.commit()
    db.session.execute(delete(ChatLog).where(ChatLog.temp_user_id == temp_user_id))
    db.session.commit()
    db.session.execute(delete(GlobalObjectStorage).where(GlobalObjectStorage.temp_user_id == temp_user_id))
    db.session.commit()
    files_to_delete = list()
    for short_code_item in db.session.execute(select(Shortener).filter_by(temp_user_id=temp_user_id)).scalars():
        for email in db.session.execute(select(Email).filter_by(short=short_code_item.short)).scalars():
            for attachment in db.session.execute(select(EmailAttachment).filter_by(email_id=email.id)).scalars():
                files_to_delete.append(attachment.upload)
    for file_number in files_to_delete:
        the_file = SavedFile(file_number)
        the_file.delete()
    db.session.execute(delete(Shortener).where(Shortener.temp_user_id == temp_user_id))
    db.session.commit()
    keys_to_delete = set()
    for key in r.keys('*userid:t' + str(temp_user_id)):
        keys_to_delete.add(key)
    for key in r.keys('*userid:t' + str(temp_user_id) + ':*'):
        keys_to_delete.add(key)
    for key in keys_to_delete:
        r.delete(key)

def delete_user_data(user_id, r, r_user):
    db.session.execute(delete(UserDict).where(UserDict.user_id == user_id))
    db.session.commit()
    db.session.execute(delete(UserDictKeys).where(UserDictKeys.user_id == user_id))
    db.session.commit()
    db.session.execute(delete(UploadsUserAuth).where(UploadsUserAuth.user_id == user_id))
    db.session.commit()
    db.session.execute(delete(ChatLog).where(ChatLog.owner_id == user_id))
    db.session.commit()
    db.session.execute(delete(ChatLog).where(ChatLog.user_id == user_id))
    db.session.commit()
    db.session.execute(delete(GlobalObjectStorage).where(GlobalObjectStorage.user_id == user_id))
    db.session.commit()
    for package_auth in db.session.execute(select(PackageAuth).filter_by(user_id=user_id)).scalars():
        package_auth.user_id = 1
    db.session.commit()
    files_to_delete = list()
    for short_code_item in db.session.execute(select(Shortener).filter_by(user_id=user_id)).scalars():
        for email in db.session.execute(select(Email).filter_by(short=short_code_item.short)).scalars():
            for attachment in db.session.execute(select(EmailAttachment).filter_by(email_id=email.id)).scalars():
                files_to_delete.append(attachment.upload)
    for file_number in files_to_delete:
        the_file = SavedFile(file_number)
        the_file.delete()
    db.session.execute(delete(Shortener).where(Shortener.user_id == user_id))
    db.session.commit()
    db.session.execute(delete(UserRoles).where(UserRoles.user_id == user_id))
    db.session.commit()
    for user_auth in db.session.execute(select(UserAuthModel).filter_by(user_id=user_id).with_for_update()).scalars():
        user_auth.password = ''
        user_auth.reset_password_token = ''
    db.session.commit()
    for section in ('playground', 'playgroundmodules', 'playgroundpackages', 'playgroundsources', 'playgroundstatic', 'playgroundtemplate'):
        the_section = SavedFile(user_id, section=section)
        the_section.delete()
    old_email = None
    for user_object in db.session.execute(select(UserModel).filter_by(id=user_id)).scalars():
        old_email = user_object.email
        user_object.active = False
        user_object.first_name = ''
        user_object.last_name = ''
        user_object.nickname = ''
        user_object.email = None
        user_object.country = ''
        user_object.subdivisionfirst = ''
        user_object.subdivisionsecond = ''
        user_object.subdivisionthird = ''
        user_object.organization = ''
        user_object.timezone = None
        user_object.language = None
        user_object.pypi_username = None
        user_object.pypi_password = None
        user_object.otp_secret = None
        user_object.confirmed_at = None
        user_object.last_login = None
        user_object.social_id = 'disabled$' + str(user_id)
    db.session.commit()
    keys_to_delete = set()
    for key in r.keys('*userid:' + str(user_id)):
        keys_to_delete.add(key)
    for key in r.keys('*userid:' + str(user_id) + ':*'):
        keys_to_delete.add(key)
    for key in keys_to_delete:
        r.delete(key)
    keys_to_delete = set()
    for key in r_user.keys('*:user:' + str(old_email)):
        keys_to_delete.add(key)
    for key in keys_to_delete:
        r_user.delete(key)

#@elapsed('reset_user_dict')
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
        db.session.execute(delete(UserDictKeys).filter_by(key=user_code, filename=filename))
        db.session.commit()
        do_delete = True
    else:
        if user_type == 'user':
            db.session.execute(delete(UserDictKeys).filter_by(key=user_code, filename=filename, user_id=the_user_id))
        else:
            db.session.execute(delete(UserDictKeys).filter_by(key=user_code, filename=filename, temp_user_id=the_user_id))
        db.session.commit()
        existing_user_dict_key = db.session.execute(select(UserDictKeys).filter_by(key=user_code, filename=filename)).scalar()
        if not existing_user_dict_key:
            do_delete = True
        else:
            do_delete = False
    if not force:
        files_to_save = list()
        for upload in db.session.execute(select(Uploads).filter_by(key=user_code, yamlfile=filename, persistent=True)).scalars():
            files_to_save.append(upload.indexno)
        if len(files_to_save):
            something_added = False
            if user_type == 'user':
                for uploads_indexno in files_to_save:
                    existing_auth = db.session.execute(select(UploadsUserAuth).filter_by(user_id=the_user_id, uploads_indexno=uploads_indexno)).scalar()
                    if not existing_auth:
                        new_auth_record = UploadsUserAuth(user_id=the_user_id, uploads_indexno=uploads_indexno)
                        db.session.add(new_auth_record)
                        something_added = True
            else:
                for uploads_indexno in files_to_save:
                    existing_auth = db.session.execute(select(UploadsUserAuth).filter_by(temp_user_id=the_user_id, uploads_indexno=uploads_indexno)).scalar()
                    if not existing_auth:
                        new_auth_record = UploadsUserAuth(temp_user_id=the_user_id, uploads_indexno=uploads_indexno)
                        db.session.add(new_auth_record)
                        something_added = True
            if something_added:
                db.session.commit()
    if do_delete:
        db.session.execute(delete(UserDict).filter_by(key=user_code, filename=filename))
        db.session.commit()
        files_to_delete = list()
        for speaklist in db.session.execute(select(SpeakList).filter_by(key=user_code, filename=filename)).scalars():
            if speaklist.upload is not None:
                files_to_delete.append(speaklist.upload)
        db.session.execute(delete(SpeakList).filter_by(key=user_code, filename=filename))
        db.session.commit()
        for upload in db.session.execute(select(Uploads).filter_by(key=user_code, yamlfile=filename, persistent=False)).scalars():
            files_to_delete.append(upload.indexno)
        db.session.execute(delete(Uploads).filter_by(key=user_code, yamlfile=filename, persistent=False))
        db.session.commit()
        db.session.execute(delete(GlobalObjectStorage).where(GlobalObjectStorage.key.like('da:uid:' + user_code + ':i:' + filename + ':%')).execution_options(synchronize_session=False))
        db.session.commit()
        db.session.execute(delete(ChatLog).filter_by(key=user_code, filename=filename))
        db.session.commit()
        for short_code_item in db.session.execute(select(Shortener).filter_by(uid=user_code, filename=filename)).scalars():
            for email in db.session.execute(select(Email).filter_by(short=short_code_item.short)).scalars():
                for attachment in db.session.execute(select(EmailAttachment).filter_by(email_id=email.id)).scalars():
                    files_to_delete.append(attachment.upload)
        db.session.execute(delete(Shortener).filter_by(uid=user_code, filename=filename))
        db.session.commit()
        # docassemble.base.functions.server.delete_answer_json(user_code, filename, delete_all=True)
        for file_number in files_to_delete:
            the_file = SavedFile(file_number)
            the_file.delete()
    return

#@elapsed('get_person')
def get_person(user_id, cache):
    if user_id in cache:
        return cache[user_id]
    for record in db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=user_id)).unique().scalars():
        cache[record.id] = record
        return record
    return None

#@elapsed('get_chat_log')
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
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.owner_id == chat_person_id))).order_by(ChatLog.id)).scalars().all()
        else:
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.owner_id == chat_person_id)).order_by(ChatLog.id)).scalars().all()
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
                role_list = [role.name for role in person.roles]
                if len(role_list) == 0:
                    role_list = ['user']
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=message, roles=role_list))
            else:
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, modtime=modtime, message=message, roles=['user']))
    else:
        if chat_mode in ['peer', 'peerhelp']:
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.temp_owner_id == chat_person_id))).order_by(ChatLog.id)).scalars().all()
        else:
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.temp_owner_id == chat_person_id)).order_by(ChatLog.id)).scalars().all()
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
                role_list = [role.name for role in person.roles]
                if len(role_list) == 0:
                    role_list = ['user']
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=message, roles=role_list))
            else:
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, modtime=modtime, message=message, roles=['user']))
    return messages

#@elapsed('file_set_attributes')
def file_set_attributes(file_number, **kwargs):
    upload = db.session.execute(select(Uploads).filter_by(indexno=file_number).with_for_update()).scalar()
    if upload is None:
        db.session.commit()
        raise Exception("file_set_attributes: file number " + str(file_number) + " not found.")
    if 'private' in kwargs and kwargs['private'] in [True, False] and upload.private != kwargs['private']:
        upload.private = kwargs['private']
    if 'persistent' in kwargs and kwargs['persistent'] in [True, False] and upload.persistent != kwargs['persistent']:
        upload.persistent = kwargs['persistent']
    if 'session' in kwargs and isinstance(kwargs['session'], str):
        upload.key = kwargs['session']
    if 'filename' in kwargs and isinstance(kwargs['filename'], str):
        upload.filename = kwargs['filename']
    db.session.commit()

def file_user_access(file_number, allow_user_id=None, allow_email=None, disallow_user_id=None, disallow_email=None, disallow_all=False):
    something_added = False
    if allow_user_id:
        for user_id in set(allow_user_id):
            existing_user = db.session.execute(select(UserModel).filter_by(id=user_id)).first()
            if not existing_user:
                logmessage("file_user_access: invalid user ID " + repr(user_id))
                continue
            if db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=user_id)).first():
                continue
            new_auth_record = UploadsUserAuth(uploads_indexno=file_number, user_id=user_id)
            db.session.add(new_auth_record)
            something_added = True
    if something_added:
        db.session.commit()
    something_added = False
    if allow_email:
        for email in set(allow_email):
            existing_user = db.session.execute(select(UserModel).filter_by(email=email)).first()
            if not existing_user:
                logmessage("file_user_access: invalid email " + repr(email))
                continue
            if db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=existing_user.id)).first():
                continue
            new_auth_record = UploadsUserAuth(uploads_indexno=file_number, user_id=existing_user.id)
            db.session.add(new_auth_record)
            something_added = True
    if something_added:
        db.session.commit()
    if disallow_user_id:
        for user_id in set(disallow_user_id):
            db.session.execute(delete(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=user_id))
        db.session.commit()
    if disallow_email:
        for email in set(disallow_email):
            existing_user = db.session.execute(select(UserModel).filter_by(email=email)).scalar()
            if not existing_user:
                logmessage("file_user_access: invalid email " + repr(email))
                continue
            db.session.execute(delete(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=existing_user.id))
        db.session.commit()
    if disallow_all:
        db.session.execute(delete(UploadsUserAuth).filter_by(uploads_indexno=file_number))
    if not (allow_user_id or allow_email or disallow_user_id or disallow_email or disallow_all):
        result = dict(user_ids=list(), emails=list(), temp_user_ids=list())
        for auth in db.session.execute(select(UploadsUserAuth.user_id, UploadsUserAuth.temp_user_id, UserModel.email).outerjoin(UserModel, UploadsUserAuth.user_id == UserModel.id).where(UploadsUserAuth.uploads_indexno == file_number)).scalars().all():
            if auth.user_id is not None:
                result['user_ids'].append(auth.user_id)
            if auth.temp_user_id is not None:
                result['temp_user_ids'].append(auth.temp_user_id)
            if auth.email:
                result['emails'].append(auth.email)
        return result

def file_privilege_access(file_number, allow=None, disallow=None, disallow_all=False):
    something_added = False
    if allow:
        for privilege in set(allow):
            existing_role = db.session.execute(select(Role).filter_by(name=privilege)).scalar_one()
            if not existing_role:
                logmessage("file_privilege_access: invalid privilege " + repr(privilege))
                continue
            if db.session.execute(select(UploadsRoleAuth).filter_by(uploads_indexno=file_number, role_id=existing_role.id)).first():
                continue
            new_auth_record = UploadsRoleAuth(uploads_indexno=file_number, role_id=existing_role.id)
            db.session.add(new_auth_record)
            something_added = True
    if something_added:
        db.session.commit()
    if disallow:
        for privilege in set(disallow):
            existing_role = db.session.execute(select(Role).filter_by(name=privilege)).scalar_one()
            if not existing_role:
                logmessage("file_privilege_access: invalid privilege " + repr(privilege))
                continue
            db.session.execute(delete(UploadsRoleAuth).filter_by(uploads_indexno=file_number, role_id=existing_role.id))
        db.session.commit()
    if disallow_all:
        db.session.execute(delete(UploadsRoleAuth).filter_by(uploads_indexno=file_number))
    if not (allow or disallow or disallow_all):
        result = list()
        for auth in db.session.execute(select(UploadsRoleAuth.id, Role.name).join(Role, UploadsRoleAuth.role_id == Role.id).where(UploadsRoleAuth.uploads_indexno == file_number)).scalars():
            result.append(auth.name)
        return result

def clear_session(i):
    if 'sessions' in session and i in session['sessions']:
        del session['sessions'][i]

def clear_specific_session(i, uid):
    if 'sessions' in session and i in session['sessions']:
        if session['sessions'][i]['uid'] == uid:
            del session['sessions'][i]

def guess_yaml_filename():
    yaml_filename = None
    if 'i' in session and 'uid' in session: #TEMPORARY
        yaml_filename = session['i']
    if 'sessions' in session:
        for item in session['sessions']:
            yaml_filename = item
            break
    return yaml_filename

def delete_obsolete():
    for name in ('i', 'uid', 'key_logged', 'encrypted', 'chatstatus'):
        if name in session:
            del session[name]

def get_session(i):
    if 'sessions' not in session:
        session['sessions'] = dict()
    if i in session['sessions']:
        return session['sessions'][i]
    if 'i' in session and 'uid' in session: #TEMPORARY
        session['sessions'][session['i']] = dict(uid=session['uid'], encrypted=session.get('encrypted', True), key_logged=session.get('key_logged', False), chatstatus=session.get('chatstatus', 'off'))
        if i == session['i']:
            delete_obsolete()
            return session['sessions'][i]
        delete_obsolete()
    return None

def unattached_uid():
    while True:
        newname = random_alphanumeric(32)
        existing_key = db.session.execute(select(UserDict).filter_by(key=newname)).first()
        if existing_key:
            continue
        return newname

def get_uid_for_filename(i):
    if 'sessions' not in session:
        session['sessions'] = dict()
    if i not in session['sessions']:
        return None
    return session['sessions'][i]['uid']

def update_session(i, uid=None, encrypted=None, key_logged=None, chatstatus=None):
    if 'sessions' not in session:
        session['sessions'] = dict()
    if i not in session['sessions'] or uid is not None:
        if uid is None:
            raise Exception("update_session: cannot create new session without a uid")
        if encrypted is None:
            encrypted = True
        if key_logged is None:
            key_logged = False
        if chatstatus is None:
            chatstatus = 'off'
        session['sessions'][i] = dict(uid=uid, encrypted=encrypted, key_logged=key_logged, chatstatus=chatstatus)
    else:
        if uid is not None:
            session['sessions'][i]['uid'] = uid
        if encrypted is not None:
            session['sessions'][i]['encrypted'] = encrypted
        if key_logged is not None:
            session['sessions'][i]['key_logged'] = key_logged
        if chatstatus is not None:
            session['sessions'][i]['chatstatus'] = chatstatus
    session.modified = True
    return session['sessions'][i]

def get_session_uids():
    if 'i' in session: #TEMPORARY
        get_session(session['i'])
    if 'sessions' in session:
        return [item['uid'] for item in session['sessions'].values()]
    return []
