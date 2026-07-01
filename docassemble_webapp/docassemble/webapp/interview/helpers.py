import zoneinfo
import copy
import datetime
import json
import re
import traceback
import os
from pygments import highlight
from pygments.lexers import YamlLexer  # pylint: disable=no-name-in-module
from pygments.formatters.html import HtmlFormatter
from flask import request, make_response, session, current_app
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
from sqlalchemy import or_, update, delete, select, not_, and_
from docassemble.base import DA
from docassemble.base.error import DAErrorMissingVariable, DAException
from docassemble.base.functions import get_message_log, serializable_dict, dict_as_json
from docassemble.base.generate_key import random_alphanumeric, random_string
from docassemble.base.hooks import manage_chat_logs, manage_global_objects, manage_email_server_objects, manage_tts_objects
from docassemble.base.interview_cache import get_interview
from docassemble.base.language.control import get_language
from docassemble.base.language.words import word
from docassemble.base.pandoc import word_to_markdown
from docassemble.base.parse import InterviewStatus
from docassemble.base.pdftk import read_fields as base_read_fields
from docassemble.base.save_status import SS_NEW, SS_OVERWRITE, SS_IGNORE
from docassemble.base.thread_context import global_context, this_thread, copy_of_globals
from docassemble.webapp.config import (
    PAGINATION_LIMIT_PLUS_ONE,
    NOTIFICATION_CONTAINER,
    NOTIFICATION_MESSAGE,
    default_short_title,
    DEFAULT_LANGUAGE,
    ALLOW_REGISTRATION,
    SHOW_LOGIN,
    default_title,
    ROOT,
    REQUIRE_IDEMPOTENT,
    PAGINATION_LIMIT,
    da_version,
    daconfig,
)
from docassemble.webapp.extensions import db
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.lock import lock_context, obtain_lock, release_lock
from docassemble.webapp.main.hooks import get_default_timezone
from docassemble.webapp.main.models import Uploads, UploadsUserAuth
from docassemble.webapp.packages.models import PackageAuth
from docassemble.webapp.sessions import update_session, get_session, session_context
from docassemble.webapp.users.common import get_person
from docassemble.webapp.users.models import UserModel, UserRoles, UserAuthModel
from docassemble.webapp.interview.dictionary import fresh_dictionary
from docassemble.webapp.utils.constants import NoneType
from docassemble.webapp.utils.encryption import (
    pack_dictionary,
    decrypt_dictionary,
    encrypt_dictionary,
    unpack_dictionary,
    nice_date_from_utc,
)
from docassemble.webapp.utils.helpers import (
    title_converter,
    docx_variable_fix,
    current_info,
    exit_href,
    illegal_variable_name,
    transform_json_variables,
    reset_session,
    add_referer,
    contains_volatile,
    jsonify_with_status,
    MD5Hash,
    pad_to_16,
    sanitize,
    true_or_false,
    manual_checkout,
    custom_send_file,
    CAN_CONVERT_WORD,
)
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from .config import main_page_parts, page_parts
from .models import UserDict, UserDictKeys
from .user_dict import fetch_user_dict, fetch_previous_user_dict

def sub_temp_user_dict_key(temp_user_id, user_id):
    temp_interviews = []
    for record in db.session.execute(select(UserDictKeys).filter_by(temp_user_id=temp_user_id).with_for_update()).scalars():
        record.temp_user_id = None
        record.user_id = user_id
        temp_interviews.append((record.filename, record.key))
    db.session.commit()
    return temp_interviews


def sub_temp_other(user):
    if 'tempuser' in session:
        device_id = request.cookies.get('ds', None)
        if device_id is None:
            device_id = random_string(16)
        url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
        url = url_root + 'interview'
        role_list = [role.name for role in user.roles]
        if len(role_list) == 0:
            role_list = ['user']
        the_current_info = {'user': {'email': user.email, 'roles': role_list, 'the_user_id': user.id, 'theid': user.id, 'firstname': user.first_name, 'lastname': user.last_name, 'nickname': user.nickname, 'country': user.country, 'subdivisionfirst': user.subdivisionfirst, 'subdivisionsecond': user.subdivisionsecond, 'subdivisionthird': user.subdivisionthird, 'organization': user.organization, 'timezone': user.timezone, 'language': user.language, 'location': None, 'session_uid': 'admin', 'device_id': device_id}, 'session': None, 'secret': None, 'yaml_filename': None, 'url': url, 'url_root': url_root, 'encrypted': False, 'action': None, 'interface': 'web', 'arguments': {}}
        this_thread.current_info = the_current_info
        manage_chat_logs(0, temp_user_id=session['tempuser'], new_user_id=user.id)
        manage_global_objects(0, temp_user_id=session['tempuser'], new_user_id=user.id, oldsecret=str(request.cookies.get('secret', None)), newsecret=session.get('newsecret', None))
        db.session.execute(update(UploadsUserAuth).where(UploadsUserAuth.temp_user_id == int(session['tempuser'])).values(user_id=user.id, temp_user_id=None))
        db.session.commit()
        del session['tempuser']


def save_user_dict_key(session_id, filename, priors=False, user=None):
    if user is not None:
        user_id = user.id
        is_auth = True
    else:
        if current_user.is_authenticated:
            is_auth = True
            user_id = current_user.id
        else:
            is_auth = False
            user_id = session.get('tempuser', None)
            if user_id is None:
                logmessage("save_user_dict_key: no user ID available for saving")
                return
    # logmessage("save_user_dict_key: called")
    the_interview_list = set([filename])
    found = set()
    if priors:
        for the_record in db.session.execute(select(UserDict.filename).filter_by(key=session_id).group_by(UserDict.filename)):
            the_interview_list.add(the_record.filename)
    for filename_to_search in the_interview_list:
        if is_auth:
            for the_record in db.session.execute(select(UserDictKeys).filter_by(key=session_id, filename=filename_to_search, user_id=user_id)):
                found.add(filename_to_search)
        else:
            for the_record in db.session.execute(select(UserDictKeys).filter_by(key=session_id, filename=filename_to_search, temp_user_id=user_id)):
                found.add(filename_to_search)
    for filename_to_save in (the_interview_list - found):
        if is_auth:
            new_record = UserDictKeys(key=session_id, filename=filename_to_save, user_id=user_id)
        else:
            new_record = UserDictKeys(key=session_id, filename=filename_to_save, temp_user_id=user_id)
        db.session.add(new_record)
        db.session.commit()


def save_user_dict(user_code, user_dict, filename, secret=None, changed=False, encrypt=True, manual_user_id=None, steps=None, max_indexno=None):
    # logmessage("save_user_dict: called with encrypt " + str(encrypt))
    if REQUIRE_IDEMPOTENT:
        for var_name in ('x', 'i', 'j', 'k', 'l', 'm', 'n', '__DANEWOBJECT'):
            if var_name in user_dict:
                del user_dict[var_name]
        user_dict['_internal']['objselections'] = {}
    if 'session_local' in user_dict:
        del user_dict['session_local']
    if 'device_local' in user_dict:
        del user_dict['device_local']
    if 'user_local' in user_dict:
        del user_dict['user_local']
    nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    if steps is not None:
        user_dict['_internal']['steps'] = steps
    user_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated):
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
        if max_indexno is None:
            max_indexno = db.session.execute(select(db.func.max(UserDict.indexno)).where(and_(UserDict.key == user_code, UserDict.filename == filename))).scalar()
        if max_indexno is None:
            if encrypt:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
            else:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
            db.session.add(new_record)
            db.session.commit()
        else:
            for record in db.session.execute(select(UserDict).filter_by(key=user_code, filename=filename, indexno=max_indexno).with_for_update()).scalars():
                if encrypt:
                    record.dictionary = encrypt_dictionary(user_dict, secret)
                    record.modtime = nowtime
                    record.encrypted = True
                else:
                    record.dictionary = pack_dictionary(user_dict)
                    record.modtime = nowtime
                    record.encrypted = False
            db.session.commit()


def get_existing_session(yaml_filename, secret):
    keys = [result.key for result in db.session.execute(select(UserDictKeys.filename, UserDictKeys.key).where(and_(UserDictKeys.user_id == current_user.id, UserDictKeys.filename == yaml_filename)).order_by(UserDictKeys.indexno))]
    for key in keys:
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(key, yaml_filename, secret=secret)  # pylint: disable=unused-variable
        except:
            logmessage("get_existing_session: unable to decrypt existing interview session " + key)
            continue
        update_session(yaml_filename, uid=key, key_logged=True, encrypted=is_encrypted)
        return key, is_encrypted
    return None, True


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


def delete_temp_user_data(temp_user_id, r):
    db.session.execute(delete(UserDictKeys).where(UserDictKeys.temp_user_id == temp_user_id))
    db.session.commit()
    db.session.execute(delete(UploadsUserAuth).where(UploadsUserAuth.temp_user_id == temp_user_id))
    db.session.commit()
    manage_chat_logs(1, temp_user_id=temp_user_id)
    manage_global_objects(1, temp_user_id=temp_user_id)
    manage_email_server_objects(0, temp_user_id=temp_user_id)
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
    manage_chat_logs(2, user_id=user_id)
    manage_global_objects(2, user_id=user_id)
    for package_auth in db.session.execute(select(PackageAuth).filter_by(user_id=user_id)).scalars():
        package_auth.user_id = 1
    db.session.commit()
    manage_email_server_objects(1, user_id=user_id)
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


# @elapsed('reset_user_dict')
def reset_user_dict(user_code, filename, user_id=None, temp_user_id=None, force=False):
    # logmessage("reset_user_dict called with " + str(user_code) + " and " + str(filename) + " and " + str(user_id) + " and " + str(temp_user_id) + " and " + str(force))
    user_type = ''
    if force:
        the_user_id = None
    else:
        if user_id is None and temp_user_id is None:
            if current_user.is_authenticated:
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
        do_delete = not bool(existing_user_dict_key)
    if not force:
        files_to_save = []
        for upload in db.session.execute(select(Uploads).filter_by(key=user_code, yamlfile=filename, persistent=True)).scalars():
            files_to_save.append(upload.indexno)
        if len(files_to_save) > 0:
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
        manage_tts_objects(1, user_code=user_code, filename=filename)
        manage_global_objects(3, key=user_code, filename=filename)
        manage_chat_logs(3, key=user_code, filename=filename)
        manage_email_server_objects(2, user_code=user_code, filename=filename)
        # server.delete_answer_json(user_code, filename, delete_all=True)


def unattached_uid():
    while True:
        newname = random_alphanumeric(32)
        existing_key = db.session.execute(select(UserDict).filter_by(key=newname)).first()
        if existing_key:
            continue
        return newname


def decrypt_session(secret, user_code=None, filename=None):
    # logmessage("decrypt_session: user_code is " + str(user_code) + " and filename is " + str(filename))
    nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    if user_code is None or filename is None or secret is None:
        return
    manage_tts_objects(2, user_code=user_code, filename=filename, secret=secret)
    for record in db.session.execute(select(UserDict).filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).with_for_update()).scalars():
        the_dict = decrypt_dictionary(record.dictionary, secret)
        record.dictionary = pack_dictionary(the_dict)
        record.encrypted = False
        record.modtime = nowtime
    db.session.commit()
    manage_chat_logs(4, key=user_code, filename=filename, secret=secret)


def encrypt_session(secret, user_code=None, filename=None):
    # logmessage("encrypt_session: user_code is " + str(user_code) + " and filename is " + str(filename))
    nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    if user_code is None or filename is None or secret is None:
        return
    manage_tts_objects(3, user_code=user_code, filename=filename, secret=secret)
    for record in db.session.execute(select(UserDict).filter_by(key=user_code, filename=filename, encrypted=False).order_by(UserDict.indexno).with_for_update()).scalars():
        the_dict = unpack_dictionary(record.dictionary)
        record.dictionary = encrypt_dictionary(the_dict, secret)
        record.encrypted = True
        record.modtime = nowtime
    db.session.commit()
    manage_chat_logs(5, key=user_code, filename=filename, secret=secret)


def substitute_secret(oldsecret, newsecret, user=None, to_convert=None):
    if user is None:
        user = current_user
    device_id = request.cookies.get('ds', None)
    if device_id is None:
        device_id = random_string(16)
    the_current_info = current_info(yaml=None, req=request, action=None, session_info=None, secret=oldsecret, device_id=device_id)
    this_thread.current_info = the_current_info
    temp_user = session.get('tempuser', None)
    # logmessage("substitute_secret: " + repr(oldsecret) + " and " + repr(newsecret) + " and temp_user is " + repr(temp_user))
    if oldsecret in ('None', newsecret):
        # logmessage("substitute_secret: returning new secret without doing anything")
        return newsecret
    # logmessage("substitute_secret: continuing")
    if temp_user is not None:
        temp_user_info = {'email': None, 'the_user_id': 't' + str(temp_user), 'theid': temp_user, 'roles': []}
        the_current_info['user'] = temp_user_info
        manage_global_objects(7, user_id=user.id, oldsecret=oldsecret, newsecret=newsecret)
    if to_convert is None:
        to_do = set()
        if 'i' in session and 'uid' in session:  # TEMPORARY
            get_session(session['i'])
        if 'sessions' in session:
            for filename, info in session['sessions'].items():
                to_do.add((filename, info['uid']))
        for the_record in db.session.execute(select(UserDict.filename, UserDict.key).filter_by(user_id=user.id).group_by(UserDict.filename, UserDict.key)):
            to_do.add((the_record.filename, the_record.key))
        for the_record in db.session.execute(select(UserDictKeys.filename, UserDictKeys.key).join(UserDict, and_(UserDictKeys.filename == UserDict.filename, UserDictKeys.key == UserDict.key)).where(and_(UserDictKeys.user_id == user.id)).group_by(UserDictKeys.filename, UserDictKeys.key)):
            to_do.add((the_record.filename, the_record.key))
    else:
        to_do = set(to_convert)
    for (filename, user_code) in to_do:
        the_current_info['yaml_filename'] = filename
        the_current_info['session'] = user_code
        the_current_info['encrypted'] = True
        # obtain_lock(user_code, filename)
        # logmessage("substitute_secret: filename is " + str(filename) + " and key is " + str(user_code))
        manage_tts_objects(4, user_code=user_code, filename=filename, oldsecret=oldsecret, newsecret=newsecret)
        manage_global_objects(6, key=user_code, filename=filename, oldsecret=oldsecret, newsecret=newsecret)
        for record in db.session.execute(select(UserDict).filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).with_for_update()).scalars():
            # logmessage("substitute_secret: record was encrypted")
            try:
                the_dict = decrypt_dictionary(record.dictionary, oldsecret)
            except:
                logmessage("substitute_secret: error decrypting dictionary for filename " + filename + " and uid " + user_code)
                continue
            if not isinstance(the_dict, dict):
                logmessage("substitute_secret: dictionary was not a dict for filename " + filename + " and uid " + user_code)
                continue
            if temp_user:
                try:
                    old_entry = the_dict['_internal']['user_local']['t' + str(temp_user)]
                    del the_dict['_internal']['user_local']['t' + str(temp_user)]
                    the_dict['_internal']['user_local'][str(user.id)] = old_entry
                except:
                    pass
            record.dictionary = encrypt_dictionary(the_dict, newsecret)
        db.session.commit()
        if temp_user:
            for record in db.session.execute(select(UserDict).filter_by(key=user_code, filename=filename, encrypted=False).order_by(UserDict.indexno).with_for_update()).scalars():
                try:
                    the_dict = unpack_dictionary(record.dictionary)
                except:
                    logmessage("substitute_secret: error unpacking dictionary for filename " + filename + " and uid " + user_code)
                    continue
                if not isinstance(the_dict, dict):
                    logmessage("substitute_secret: dictionary was not a dict for filename " + filename + " and uid " + user_code)
                    continue
                try:
                    old_entry = the_dict['_internal']['user_local']['t' + str(temp_user)]
                    del the_dict['_internal']['user_local']['t' + str(temp_user)]
                    the_dict['_internal']['user_local'][str(user.id)] = old_entry
                except:
                    pass
                record.dictionary = pack_dictionary(the_dict)
            db.session.commit()
        manage_chat_logs(6, key=user_code, filename=filename, oldsecret=oldsecret, newsecret=newsecret)
        # release_lock(user_code, filename)
    manage_global_objects(7, user_id=user.id, oldsecret=oldsecret, newsecret=newsecret)
    return newsecret

@hookimpl(specname='server_get_session_variables')
def get_session_variables(yaml_filename, session_id, secret, simplify, use_lock):
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    # logmessage("get_session_variables: fetch_user_dict")
    with lock_context(session_id, yaml_filename, use_lock=use_lock), global_context(copy_of_globals(this_thread)):
        this_thread.current_info['yaml_filename'] = yaml_filename
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=str(secret))  # pylint: disable=unused-variable
        except BaseException as the_err:
            raise DAException("Unable to decrypt interview dictionary") from the_err
    if user_dict is None:
        raise DAException("Unable to obtain interview dictionary.")
    if simplify:
        variables = serializable_dict(user_dict, include_internal=True)
        # variables['_internal'] = serializable_dict(user_dict['_internal'])
        return variables
    return user_dict


@hookimpl(specname='server_go_back_in_session')
def go_back_in_session(yaml_filename, session_id, secret, return_question, use_lock, encode):
    with lock_context(session_id, yaml_filename, use_lock=use_lock), global_context(copy_of_globals(this_thread)):
        this_thread.current_info['yaml_filename'] = yaml_filename
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        except Exception as err:
            raise DAException("Unable to decrypt interview dictionary.") from err
        if user_dict is None:
            raise DAException("Unable to obtain interview dictionary.")
        if steps == 1:
            raise DAException("Cannot go back.")
        old_user_dict = user_dict
        steps, user_dict, is_encrypted = fetch_previous_user_dict(session_id, yaml_filename, secret)
        if user_dict is None:
            raise DAException("Unable to obtain interview dictionary.")
        if return_question:
            try:
                data = get_question_data(yaml_filename, session_id, secret, use_lock=False, user_dict=user_dict, steps=steps, is_encrypted=is_encrypted, old_user_dict=old_user_dict, encode=encode)
            except BaseException as the_err:
                raise DAException("Problem getting current question") from the_err
        else:
            data = None
    return data

@hookimpl(specname="server_set_session_variables")
def set_session_variables_adapter(yaml_filename, session_id, variables, secret, return_question, literal_variables, del_variables, question_name, event_list, advance_progress_meter, post_setting, use_lock, encode, process_objects):
    return set_session_variables(yaml_filename, session_id, variables, secret=secret, return_question=return_question, literal_variables=literal_variables, del_variables=del_variables, question_name=question_name, event_list=event_list, advance_progress_meter=advance_progress_meter, post_setting=post_setting, use_lock=use_lock, encode=encode, process_objects=process_objects)

def set_session_variables(yaml_filename, session_id, variables, secret=None, return_question=False, literal_variables=None, del_variables=None, question_name=None, event_list=None, advance_progress_meter=False, post_setting=True, use_lock=False, encode=False, process_objects=False):
    device_id = this_thread.current_info['user']['device_id']
    session_uid = this_thread.current_info['user']['session_uid']
    if secret is None:
        secret = this_thread.current_info.get('secret', None)
    with lock_context(session_id, yaml_filename, use_lock=use_lock), global_context(copy_of_globals(this_thread)), session_context():
        this_thread.current_info['yaml_filename'] = yaml_filename
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        except Exception as the_err:
            raise DAException("Unable to decrypt interview dictionary.") from the_err
        vars_set = set()
        old_values = {}
        if user_dict is None:
            raise DAException("Unable to obtain interview dictionary.")
        if process_objects:
            variables = transform_json_variables(variables)
        pre_assembly_necessary = False
        for key, val in variables.items():
            if contains_volatile.search(key):
                pre_assembly_necessary = True
                break
        if pre_assembly_necessary is False and literal_variables is not None:
            for key, val in literal_variables.items():
                if contains_volatile.search(key):
                    pre_assembly_necessary = True
                    break
        if pre_assembly_necessary is False and del_variables is not None:
            for key in del_variables:
                if contains_volatile.search(key):
                    pre_assembly_necessary = True
                    break
        if pre_assembly_necessary:
            interview = get_interview(yaml_filename)
            if current_user.is_anonymous:
                if not interview.allowed_to_access(is_anonymous=True):
                    raise DAException('Insufficient permissions to run this interview.')
            else:
                if not interview.allowed_to_access(has_roles=[role.name for role in current_user.roles]):
                    raise DAException('Insufficient permissions to run this interview.')
            ci = current_info(yaml=yaml_filename, req=request, secret=secret, device_id=device_id, session_uid=session_uid)
            ci['session'] = session_id
            ci['encrypted'] = is_encrypted
            ci['secret'] = secret
            interview_status = InterviewStatus(current_info=ci)
            try:
                interview.assemble(user_dict, interview_status)
            except BaseException as err:
                raise DAException("Error processing session: " + err.__class__.__name__ + ": " + str(err)) from err
        try:
            for key, val in variables.items():
                if illegal_variable_name(key):
                    raise DAException("Illegal value as variable name.")
                if isinstance(val, (str, bool, int, float, NoneType)):
                    exec(str(key) + ' = ' + repr(val), user_dict)
                else:
                    if key == '_xxxtempvarxxx':
                        continue
                    user_dict['_xxxtempvarxxx'] = copy.deepcopy(val)
                    exec(str(key) + ' = _xxxtempvarxxx', user_dict)
                    del user_dict['_xxxtempvarxxx']
                process_set_variable(str(key), user_dict, vars_set, old_values)
        except BaseException as the_err:
            if '_xxxtempvarxxx' in user_dict:
                del user_dict['_xxxtempvarxxx']
            raise DAException("Problem setting variables:" + str(the_err)) from the_err
        if literal_variables is not None:
            exec('import docassemble.base.util', user_dict)
            for key, val in literal_variables.items():
                if illegal_variable_name(key):
                    raise DAException("Illegal value as variable name.")
                exec(str(key) + ' = ' + val, user_dict)
                process_set_variable(str(key), user_dict, vars_set, old_values)
        if question_name is not None:
            interview = get_interview(yaml_filename)
            if current_user.is_anonymous:
                if not interview.allowed_to_access(is_anonymous=True):
                    raise DAException('Insufficient permissions to run this interview.')
            else:
                if not interview.allowed_to_access(has_roles=[role.name for role in current_user.roles]):
                    raise DAException('Insufficient permissions to run this interview.')
            if question_name in interview.questions_by_name:
                interview.questions_by_name[question_name].mark_as_answered(user_dict)
            else:
                raise DAException("Problem marking question as completed")
        if del_variables is not None:
            try:
                for key in del_variables:
                    if illegal_variable_name(key):
                        raise DAException("Illegal value as variable name.")
                    exec('del ' + str(key), user_dict)
            except BaseException as the_err:
                raise DAException("Problem deleting variables: " + str(the_err)) from the_err
        session_uid = this_thread.current_info['user']['session_uid']
        # if 'event_stack' in user_dict['_internal']:
        #     logmessage("Event stack starting as: " + repr(user_dict['_internal']['event_stack']))
        # else:
        #     logmessage("No event stack.")
        if event_list is not None and len(event_list) and 'event_stack' in user_dict['_internal'] and session_uid in user_dict['_internal']['event_stack'] and len(user_dict['_internal']['event_stack'][session_uid]):
            for event_name in event_list:
                if illegal_variable_name(event_name):
                    raise DAException("Illegal value as event name.")
                if user_dict['_internal']['event_stack'][session_uid][0]['action'] == event_name:
                    user_dict['_internal']['event_stack'][session_uid].pop(0)
                    # logmessage("Popped " + str(event_name))
                if len(user_dict['_internal']['event_stack'][session_uid]) == 0:
                    break
        if len(vars_set) > 0 and 'event_stack' in user_dict['_internal'] and session_uid in user_dict['_internal']['event_stack'] and len(user_dict['_internal']['event_stack'][session_uid]):
            for var_name in vars_set:
                if user_dict['_internal']['event_stack'][session_uid][0]['action'] == var_name:
                    user_dict['_internal']['event_stack'][session_uid].pop(0)
                    # logmessage("Popped " + str(var_name))
                if len(user_dict['_internal']['event_stack'][session_uid]) == 0:
                    break
        if question_name is not None:
            for var_name in vars_set:
                if var_name in interview.invalidation_todo or var_name in interview.onchange_todo:
                    interview.invalidate_dependencies(var_name, user_dict, old_values)
                try:
                    del user_dict['_internal']['dirty'][var_name]
                except:
                    pass
        # if 'event_stack' in user_dict['_internal']:
        #     logmessage("Event stack now: " + repr(user_dict['_internal']['event_stack']))
        if post_setting:
            steps += 1
        if return_question:
            try:
                data = get_question_data(yaml_filename, session_id, secret, use_lock=False, user_dict=user_dict, steps=steps, is_encrypted=is_encrypted, post_setting=post_setting, advance_progress_meter=advance_progress_meter, encode=encode)
            except BaseException as the_err:
                raise DAException("Problem getting current question:" + str(the_err)) from the_err
        else:
            data = None
        if not return_question:
            save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=post_setting, steps=steps)
            if 'multi_user' in vars_set:
                if user_dict.get('multi_user', False) is True and is_encrypted is True:
                    decrypt_session(secret, user_code=session_id, filename=yaml_filename)
                    is_encrypted = False
                if user_dict.get('multi_user', False) is False and is_encrypted is False:
                    encrypt_session(secret, user_code=session_id, filename=yaml_filename)
                    is_encrypted = True
    return data


@hookimpl(specname="server_create_session")
def create_new_interview(yaml_filename, secret, url_args, referer, req):
    interview = get_interview(yaml_filename)
    if current_user.is_anonymous:
        if not interview.allowed_to_initiate(is_anonymous=True):
            raise DAException('Insufficient permissions to run this interview.')
        if not interview.allowed_to_access(is_anonymous=True):
            raise DAException('Insufficient permissions to run this interview.')
    else:
        if (not current_user.has_role('admin')) and (not interview.allowed_to_initiate(has_roles=[role.name for role in current_user.roles])):
            raise DAException('Insufficient permissions to run this interview.')
        if not interview.allowed_to_access(has_roles=[role.name for role in current_user.roles]):
            raise DAException('Insufficient permissions to run this interview.')
    if req is None:
        req = request
    if secret is None:
        secret = random_string(16)
    with global_context(copy_of_globals(this_thread)), session_context():
        session_id, user_dict = reset_session(yaml_filename, secret)  # obtains a lock than needs to be released
        add_referer(user_dict, referer=referer)
        if url_args and (isinstance(url_args, dict) or (hasattr(url_args, 'instanceName') and hasattr(url_args, 'elements') and isinstance(url_args.elements, dict))):
            for key, val in url_args.items():
                if isinstance(val, str):
                    val = val.encode('unicode_escape').decode()
                user_dict['url_args'][key] = val
        device_id = this_thread.current_info['user']['device_id']
        session_uid = this_thread.current_info['user']['session_uid']
        ci = current_info(yaml=yaml_filename, req=req, secret=secret, device_id=device_id, session_uid=session_uid)
        ci['session'] = session_id
        ci['encrypted'] = True
        ci['secret'] = secret
        interview_status = InterviewStatus(current_info=ci)
        interview_status.checkin = True
        try:
            interview.assemble(user_dict, interview_status)
        except DAErrorMissingVariable:
            pass
        except BaseException as e:
            release_lock(session_id, yaml_filename)
            if hasattr(e, 'traceback'):
                the_trace = e.traceback
            else:
                the_trace = traceback.format_exc()
            raise DAException("create_new_interview: failure to assemble interview: " + e.__class__.__name__ + ": " + str(e) + "\n" + str(the_trace))  # pylint: disable=raise-missing-from
    encrypted = not bool(user_dict.get('multi_user', False) is True)
    save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=encrypted, changed=False, steps=1)
    save_user_dict_key(session_id, yaml_filename)
    release_lock(session_id, yaml_filename)
    return (encrypted, session_id)


@hookimpl(specname='server_get_question_data')
def get_question_data_adapter(yaml_filename, session_id, secret, use_lock, user_dict, steps, is_encrypted, old_user_dict, save, post_setting, advance_progress_meter, action, encode):
    return get_question_data(yaml_filename, session_id, secret, use_lock=use_lock, user_dict=user_dict, steps=steps, is_encrypted=is_encrypted, old_user_dict=old_user_dict, save=save, post_setting=post_setting, advance_progress_meter=advance_progress_meter, action=action, encode=encode)

def get_question_data(yaml_filename, session_id, secret, use_lock=True, user_dict=None, steps=None, is_encrypted=None, old_user_dict=None, save=True, post_setting=False, advance_progress_meter=False, action=None, encode=False):
    with lock_context(session_id, yaml_filename, use_lock=use_lock):
        with global_context(copy_of_globals(this_thread)), session_context():
            interview = get_interview(yaml_filename)
            if current_user.is_anonymous:
                if not interview.allowed_to_access(is_anonymous=True):
                    raise DAException('Insufficient permissions to run this interview.')
            else:
                if not interview.allowed_to_access(has_roles=[role.name for role in current_user.roles]):
                    raise DAException('Insufficient permissions to run this interview.')
            device_id = this_thread.current_info['user']['device_id']
            session_uid = this_thread.current_info['user']['session_uid']
            ci = current_info(yaml=yaml_filename, req=request, secret=secret, device_id=device_id, action=action, session_uid=session_uid)
            ci['session'] = session_id
            ci['secret'] = secret
            this_thread.current_info = ci
            if user_dict is None:
                try:
                    steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
                except BaseException as err:
                    raise DAException("Unable to obtain interview dictionary") from err
            ci['encrypted'] = is_encrypted
            interview_status = InterviewStatus(current_info=ci)
            # interview_status.checkin = True
            try:
                interview.assemble(user_dict, interview_status=interview_status, old_user_dict=old_user_dict)
            except DAErrorMissingVariable as err:
                return {'questionType': 'undefined_variable', 'variable': err.variable, 'message_log': get_message_log()}
            except BaseException as e:
                raise DAException("get_question_data: failure to assemble interview: " + e.__class__.__name__ + ": " + str(e)) from e
            save_status = this_thread.misc.get('save_status', SS_NEW)
        try:
            the_section = user_dict['nav'].get_section()
            the_section_display = user_dict['nav'].get_section(display=True)
            the_sections = user_dict['nav'].get_sections()
        except:
            the_section = None
            the_section_display = None
            the_sections = []
        if advance_progress_meter:
            if interview.use_progress_bar and interview_status.question.progress is None and save_status == SS_NEW:
                advance_progress(user_dict, interview)
            if interview.use_progress_bar and interview_status.question.progress is not None and (user_dict['_internal']['progress'] is None or interview.options.get('strict progress', False) or interview_status.question.progress > user_dict['_internal']['progress']):
                user_dict['_internal']['progress'] = interview_status.question.progress
        if save:
            save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=post_setting, steps=steps)
            if user_dict.get('multi_user', False) is True and is_encrypted is True:
                decrypt_session(secret, user_code=session_id, filename=yaml_filename)
                is_encrypted = False
            if user_dict.get('multi_user', False) is False and is_encrypted is False:
                encrypt_session(secret, user_code=session_id, filename=yaml_filename)
                is_encrypted = True
    if interview_status.question.question_type == "response":
        if hasattr(interview_status.question, 'response_code'):
            resp_code = interview_status.question.response_code
        else:
            resp_code = 200
        if hasattr(interview_status.question, 'all_variables'):
            if hasattr(interview_status.question, 'include_internal'):
                include_internal = interview_status.question.include_internal
            else:
                include_internal = False
            response_to_send = make_response(dict_as_json(user_dict, include_internal=include_internal).encode('utf-8'), resp_code)
        elif hasattr(interview_status.question, 'binaryresponse'):
            response_to_send = make_response(interview_status.question.binaryresponse, resp_code)
        else:
            response_to_send = make_response(interview_status.question_text.encode('utf-8'), resp_code)
        response_to_send.headers['Content-Type'] = interview_status.extras['content_type']
        return {'questionType': 'response', 'response': response_to_send}
    if interview_status.question.question_type == "sendfile":
        if interview_status.question.response_file is not None:
            the_path = interview_status.question.response_file.path()
        else:
            return jsonify_with_status("Could not send file because the response was None", 404)
        if not os.path.isfile(the_path):
            return jsonify_with_status("Could not send file because " + str(the_path) + " not found", 404)
        response_to_send = custom_send_file(the_path, mimetype=interview_status.extras['content_type'])
        response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return {'questionType': 'response', 'response': response_to_send}
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    title_info = interview.get_title(user_dict, status=interview_status, converter=lambda content, part: title_converter(content, part, interview_status))
    interview_status.exit_url = title_info.get('exit url', None)
    interview_status.exit_link = title_info.get('exit link', 'leave')
    interview_status.exit_label = title_info.get('exit label', word('Exit'))
    interview_status.title = title_info.get('full', default_title)
    interview_status.display_title = title_info.get('logo', interview_status.title)
    interview_status.tabtitle = title_info.get('tab', interview_status.title)
    interview_status.short_title = title_info.get('short', title_info.get('full', default_short_title))
    interview_status.display_short_title = title_info.get('short logo', title_info.get('logo', interview_status.short_title))
    interview_status.title_url = title_info.get('title url', None)
    interview_status.title_url_opens_in_other_window = title_info.get('title url opens in other window', True)
    interview_status.nav_item = title_info.get('navigation bar html', '')
    the_main_page_parts = main_page_parts.get(interview_language, main_page_parts.get('*'))
    interview_status.pre = title_info.get('pre', the_main_page_parts['main page pre'])
    interview_status.post = title_info.get('post', the_main_page_parts['main page post'])
    interview_status.footer = title_info.get('footer', the_main_page_parts['main page footer'] or get_part('global footer'))
    if interview_status.footer:
        interview_status.footer = re.sub(r'</?p.*?>', '', str(interview_status.footer), flags=re.IGNORECASE).strip()
        if interview_status.footer == 'off':
            interview_status.footer = ''
    interview_status.submit = title_info.get('submit', the_main_page_parts['main page submit'])
    interview_status.back = title_info.get('back button label', the_main_page_parts['main page back button label'] or interview_status.question.back())
    interview_status.cornerback = title_info.get('corner back button label', the_main_page_parts['main page corner back button label'] or interview_status.question.cornerback())
    if steps is None:
        steps = user_dict['_internal']['steps']
    allow_going_back = bool(interview_status.extras['can_go_back'] and (steps is None or (steps - user_dict['_internal']['steps_offset']) > 1))
    data = {'browser_title': interview_status.tabtitle, 'exit_link': interview_status.exit_link, 'exit_url': interview_status.exit_url, 'exit_label': interview_status.exit_label, 'title': interview_status.title, 'display_title': interview_status.display_title, 'short_title': interview_status.short_title, 'lang': interview_language, 'steps': steps, 'allow_going_back': allow_going_back, 'message_log': get_message_log(), 'section': the_section, 'display_section': the_section_display, 'sections': the_sections}
    if allow_going_back:
        data['cornerBackButton'] = interview_status.cornerback
    data.update(interview_status.as_data(user_dict, encode=encode))
    if current_app.config['ENABLE_PLAYGROUND'] and 'source' in data:
        data['source']['varsLink'] = url_for('develop.get_variables', i=yaml_filename)
        data['source']['varsLabel'] = word('Show variables and values')
    # if interview_status.question.question_type == "review" and len(interview_status.question.fields_used):
    #     next_action_review = {'action': list(interview_status.question.fields_used)[0], 'arguments': {}}
    # else:
    #     next_action_review = None
    if 'reload_after' in interview_status.extras:
        reload_after = 1000 * int(interview_status.extras['reload_after'])
    else:
        reload_after = 0
    # if next_action_review:
    #     data['next_action'] = next_action_review
    data['interview_options'] = interview.options
    if reload_after and reload_after > 0:
        data['reload_after'] = reload_after
    for key in list(data.keys()):
        if key == "_question_name":
            data['questionName'] = data[key]
            del data[key]
        elif key.startswith('_'):
            del data[key]
    data['menu'] = {'items': []}
    menu_items = data['menu']['items']
    if 'menu_items' in interview_status.extras:
        if not isinstance(interview_status.extras['menu_items'], list):
            menu_items.append({'anchor': word("Error: menu_items is not a Python list")})
        elif len(interview_status.extras['menu_items']) > 0:
            for menu_item in interview_status.extras['menu_items']:
                if not (isinstance(menu_item, dict) and 'url' in menu_item and 'label' in menu_item):
                    menu_items.append({'anchor': word("Error: menu item is not a Python dict with keys of url and label")})
                else:
                    match_action = re.search(r'^\?action=([^\&]+)', menu_item['url'])
                    if match_action:
                        menu_items.append({'href': menu_item['url'], 'action': match_action.group(1), 'anchor': menu_item['label']})
                    else:
                        menu_items.append({'href': menu_item['url'], 'anchor': menu_item['label']})
    if ALLOW_REGISTRATION:
        sign_in_text = word('Sign in or sign up to save answers')
    else:
        sign_in_text = word('Sign in to save answers')
    if daconfig.get('resume interview after login', False):
        login_url = url_for('user.login', next=url_for('interview.index', i=yaml_filename))
    else:
        login_url = url_for('user.login')
    if interview.consolidated_metadata.get('show login', SHOW_LOGIN):
        if current_user.is_anonymous:
            if len(menu_items) > 0:
                data['menu']['top'] = {'anchor': word("Menu")}
                menu_items.append({'href': login_url, 'anchor': sign_in_text})
            else:
                data['menu']['top'] = {'href': login_url, 'anchor': sign_in_text}
        else:
            if len(menu_items) == 0 and interview.options.get('hide standard menu', False):
                data['menu']['top'] = {'anchor': (current_user.email if current_user.email else re.sub(r'.*\$', '', current_user.social_id))}
            else:
                data['menu']['top'] = {'anchor': current_user.email if current_user.email else re.sub(r'.*\$', '', current_user.social_id)}
                if not interview.options.get('hide standard menu', False):
                    if current_user.has_role('admin', 'developer') and interview.debug:
                        menu_items.append({'href': '#source', 'title': word("How this question came to be asked"), 'anchor': word('Source')})
                    if current_user.has_role('admin', 'advocate') and current_app.config['ENABLE_MONITOR']:
                        menu_items.append({'href': url_for('monitor.monitor'), 'anchor': word('Monitor')})
                    if current_user.has_role('admin', 'developer', 'trainer'):
                        menu_items.append({'href': url_for('ml.train'), 'anchor': word('Train')})
                    if current_user.has_role('admin', 'developer'):
                        if current_app.config['ALLOW_UPDATES']:
                            menu_items.append({'href': url_for('packages.update_package'), 'anchor': word('Package Management')})
                        if current_app.config['ALLOW_LOG_VIEWING']:
                            menu_items.append({'href': url_for('logs.logs'), 'anchor': word('Logs')})
                        if current_app.config['ENABLE_PLAYGROUND']:
                            menu_items.append({'href': url_for('develop.playground_page'), 'anchor': word('Playground')})
                            menu_items.append({'href': url_for('develop.utilities'), 'anchor': word('Utilities')})
                        if current_user.has_role('admin', 'advocate') or current_user.can_do('access_user_info'):
                            menu_items.append({'href': url_for('users.user_list'), 'anchor': word('User List')})
                        if current_user.has_role('admin') and current_app.config['ALLOW_CONFIGURATION_EDITING']:
                            menu_items.append({'href': url_for('admin.config_page'), 'anchor': word('Configuration')})
                    if current_app.config['SHOW_DISPATCH']:
                        menu_items.append({'href': url_for('admin.interview_start'), 'anchor': word('Available Interviews')})
                    for item in current_app.config['ADMIN_INTERVIEWS']:
                        if item.can_use() and item.is_not(this_thread.current_info.get('yaml_filename', '')):
                            menu_items.append({'href': item.get_url(), 'anchor': item.get_title(get_language())})
                    if current_app.config['SHOW_MY_INTERVIEWS'] or current_user.has_role('admin'):
                        menu_items.append({'href': url_for('admin.interview_list'), 'anchor': word('My Interviews')})
                    if current_user.has_role('admin', 'developer'):
                        menu_items.append({'href': url_for('users.user_profile_page'), 'anchor': word('Profile')})
                    else:
                        if current_app.config['SHOW_PROFILE'] or current_user.has_role('admin'):
                            menu_items.append({'href': url_for('users.user_profile_page'), 'anchor': word('Profile')})
                        else:
                            menu_items.append({'href': url_for('user.change_password'), 'anchor': word('Change Password')})
                    menu_items.append({'href': url_for('user.logout'), 'anchor': word('Sign Out')})
    else:
        if len(menu_items) > 0:
            data['menu']['top'] = {'anchor': word("Menu")}
            if not interview.options.get('hide standard menu', False):
                menu_items.append({'href': exit_href(data=True), 'anchor': interview_status.exit_label})
        else:
            data['menu']['top'] = {'href': exit_href(data=True), 'anchor': interview_status.exit_label}
    # logmessage("Ok returning")
    return data


@hookimpl(specname="server_run_action_in_session")
def run_action_in_session(kwargs):
    yaml_filename = kwargs.get('i', None)
    session_id = kwargs.get('session', None)
    secret = kwargs.get('secret', None)
    action = kwargs.get('action', None)
    persistent = true_or_false(kwargs.get('persistent', False))
    overwrite = true_or_false(kwargs.get('overwrite', False))
    readonly = true_or_false(kwargs.get('read_only', False))
    if yaml_filename is None or session_id is None or action is None:
        return {"status": "error", "message": "Parameters i, session, and action are required."}
    secret = str(secret)
    if 'arguments' in kwargs and kwargs['arguments'] is not None:
        if isinstance(kwargs['arguments'], dict):
            arguments = kwargs['arguments']
        else:
            try:
                arguments = json.loads(kwargs['arguments'])
            except:
                return {"status": "error", "message": "Malformed arguments."}
            if not isinstance(arguments, dict):
                return {"status": "error", "message": "Arguments data is not a dict."}
    else:
        arguments = {}
    device_id = this_thread.current_info['user']['device_id']
    session_uid = this_thread.current_info['user']['session_uid']
    ci = current_info(yaml=yaml_filename, req=request, action={'action': action, 'arguments': arguments}, secret=secret, device_id=device_id, session_uid=session_uid)
    ci['session'] = session_id
    ci['secret'] = secret
    interview = get_interview(yaml_filename)
    if current_user.is_anonymous:
        if not interview.allowed_to_access(is_anonymous=True):
            raise DAException('Insufficient permissions to run this interview.')
    else:
        if not interview.allowed_to_access(has_roles=[role.name for role in current_user.roles]):
            raise DAException('Insufficient permissions to run this interview.')
    with global_context(copy_of_globals(this_thread)), session_context():
        this_thread.current_info = ci
        if readonly:
            this_thread.misc['save_status'] = SS_IGNORE
            overwrite = False
        else:
            obtain_lock(session_id, yaml_filename)
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        except:
            if this_thread.misc.get('save_status', SS_NEW) != SS_IGNORE:
                release_lock(session_id, yaml_filename)
            return {"status": "error", "message": "Unable to obtain interview dictionary."}
        ci['encrypted'] = is_encrypted
        interview_status = InterviewStatus(current_info=ci)
        if not persistent:
            interview_status.checkin = True
        changed = True
        try:
            interview.assemble(user_dict, interview_status)
        except DAErrorMissingVariable:
            if overwrite:
                save_status = SS_OVERWRITE
                changed = False
            else:
                save_status = this_thread.misc.get('save_status', SS_NEW)
            if save_status == SS_NEW:
                steps += 1
                user_dict['_internal']['steps'] = steps
            if save_status != SS_IGNORE:
                save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=changed, steps=steps)
                if user_dict.get('multi_user', False) is True and is_encrypted is True:
                    is_encrypted = False
                    decrypt_session(secret, user_code=session_id, filename=yaml_filename)
                if user_dict.get('multi_user', False) is False and is_encrypted is False:
                    encrypt_session(secret, user_code=session_id, filename=yaml_filename)
                    is_encrypted = True
                release_lock(session_id, yaml_filename)
            return {"status": "success"}
        except BaseException as e:
            if this_thread.misc.get('save_status', SS_NEW) != SS_IGNORE:
                release_lock(session_id, yaml_filename)
            return {"status": "error", "message": "api_session_action: failure to assemble interview: " + e.__class__.__name__ + ": " + str(e)}
        if overwrite:
            save_status = SS_OVERWRITE
            changed = False
        else:
            save_status = this_thread.misc.get('save_status', SS_NEW)
        if save_status == SS_NEW:
            steps += 1
            user_dict['_internal']['steps'] = steps
        if save_status != SS_IGNORE:
            save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=changed, steps=steps)
            if user_dict.get('multi_user', False) is True and is_encrypted is True:
                is_encrypted = False
                decrypt_session(secret, user_code=session_id, filename=yaml_filename)
            if user_dict.get('multi_user', False) is False and is_encrypted is False:
                encrypt_session(secret, user_code=session_id, filename=yaml_filename)
                is_encrypted = True
            release_lock(session_id, yaml_filename)
        if interview_status.question.question_type == "response":
            if hasattr(interview_status.question, 'all_variables'):
                if hasattr(interview_status.question, 'include_internal'):
                    include_internal = interview_status.question.include_internal
                else:
                    include_internal = False
                response_to_send = make_response(dict_as_json(user_dict, include_internal=include_internal).encode('utf-8'), '200 OK')
            elif hasattr(interview_status.question, 'binaryresponse'):
                response_to_send = make_response(interview_status.question.binaryresponse, '200 OK')
            else:
                response_to_send = make_response(interview_status.question_text.encode('utf-8'), '200 OK')
            response_to_send.headers['Content-Type'] = interview_status.extras['content_type']
            return response_to_send
        if interview_status.question.question_type == "sendfile":
            if interview_status.question.response_file is not None:
                the_path = interview_status.question.response_file.path()
            else:
                return jsonify_with_status("Could not send file because the response was None", 404)
            if not os.path.isfile(the_path):
                return jsonify_with_status("Could not send file because " + str(the_path) + " not found", 404)
            response_to_send = custom_send_file(the_path, mimetype=interview_status.extras['content_type'])
            response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return response_to_send
    return {'status': 'success'}


def refresh_or_continue(interview, post_data):
    return_val = False
    try:
        if interview.questions_by_name[post_data['_question_name']].fields[0].choices[int(post_data['X211bHRpcGxlX2Nob2ljZQ'])]['key'].question_type in ('refresh', 'continue'):
            return_val = True
    except:
        pass
    return return_val


def update_current_info_with_session_info(the_current_info, session_info):
    if session_info is not None:
        user_code = session_info['uid']
        encrypted = session_info['encrypted']
    else:
        user_code = None
        encrypted = True
    the_current_info.update({'session': user_code, 'encrypted': encrypted})


def remove_i_from_dict(the_dict):
    the_dict = copy.copy(the_dict)
    if 'i' in the_dict:
        del the_dict['i']
    return the_dict


def standard_app_values():
    return {
        "daThicknessScalingFactor": daconfig.get("signature pen thickness scaling factor"),
        "daCsrf": generate_csrf(),
        "daComboboxButtonLabel": word("Dropdown"),
        "daInputBox": word("Input box"),
        "daNotificationContainer": NOTIFICATION_CONTAINER,
        "daNotificationMessage": NOTIFICATION_MESSAGE,
        "daImageToPreLoad": url_for('static', filename='app/chat.ico', v=da_version),
        "daLiveHelpMessage": word("Get help through live chat by clicking here."),
        "daLiveHelpMessagePhone": word("Click here to get help over the phone."),
        "daNewChatMessage": word("New chat message"),
        "daLiveHelpAvailableMessage": word("Live chat is available"),
        "daScreenBeingControlled": word("Your screen is being controlled by an operator."),
        "daScreenNoLongerBeingControlled": word("The operator is no longer controlling your screen."),
        "daPathRoot": ROOT,
        "daAreYouSure": word("Are you sure you want to delete this item?"),
        "daOtherUser": word("other user"),
        "daOtherUsers": word("other users"),
        "daOperator": word("operator"),
        "daOperators": word("operators"),
        "daAllButtonClasses": current_app.config['BUTTON_STYLE'] + 'primary ' + current_app.config['BUTTON_STYLE'] + 'info ' + current_app.config['BUTTON_STYLE'] + 'warning ' + current_app.config['BUTTON_STYLE'] + 'danger ' + current_app.config['BUTTON_STYLE'] + 'secondary',
        "daButtonStyle": current_app.config['BUTTON_STYLE'],
        "daCurrencyDecimalPlaces": daconfig.get('currency decimal places', 2),
        "daSecureCookies": bool(current_app.config['SESSION_COOKIE_SECURE']),
        "daEmailAddressRequired": word("An e-mail address is required."),
        "daNeedCompleteEmail": word("You need to enter a complete e-mail address."),
        "daToggleWord": word("Toggle")
    }




def get_history(interview, interview_status):
    output = ''
    has_question = bool(hasattr(interview_status, 'question'))
    the_index = 0
    seeking_len = len(interview_status.seeking)
    if seeking_len:
        starttime = interview_status.seeking[0]['time']
        seen_done = False
        for stage in interview_status.seeking:
            if seen_done:
                output = ''
                seen_done = False
            the_index += 1
            if the_index < seeking_len and 'reason' in interview_status.seeking[the_index] and interview_status.seeking[the_index]['reason'] in ('asking', 'running') and interview_status.seeking[the_index]['question'] is stage['question'] and 'question' in stage and 'reason' in stage and stage['reason'] == 'considering':
                continue
            the_time = " at %.5fs" % (stage['time'] - starttime)
            if 'question' in stage and 'reason' in stage and (has_question is False or the_index < (seeking_len - 1) or stage['question'] is not interview_status.question):
                if stage['reason'] == 'initial':
                    output += "          <h5>Ran initial code" + the_time + "</h5>\n"
                elif stage['reason'] == 'mandatory question':
                    output += "          <h5>Tried to ask mandatory question" + the_time + "</h5>\n"
                elif stage['reason'] == 'mandatory code':
                    output += "          <h5>Tried to run mandatory code" + the_time + "</h5>\n"
                elif stage['reason'] == 'asking':
                    output += "          <h5>Tried to ask question" + the_time + "</h5>\n"
                elif stage['reason'] == 'running':
                    output += "          <h5>Tried to run block" + the_time + "</h5>\n"
                elif stage['reason'] == 'considering':
                    output += "          <h5>Considered using block" + the_time + "</h5>\n"
                elif stage['reason'] == 'objects from file':
                    output += "          <h5>Tried to load objects from file" + the_time + "</h5>\n"
                elif stage['reason'] == 'data':
                    output += "          <h5>Tried to load data" + the_time + "</h5>\n"
                elif stage['reason'] == 'objects':
                    output += "          <h5>Tried to load objects" + the_time + "</h5>\n"
                elif stage['reason'] == 'result of multiple choice':
                    output += "          <h5>Followed the result of multiple choice selection" + the_time + "</h5>\n"
                if stage['question'].from_source.path != interview.source.path and stage['question'].from_source.path is not None:
                    output += '          <p style="font-weight: bold;"><small>(' + word('from') + ' ' + stage['question'].from_source.path + ")</small></p>\n"
                if (not hasattr(stage['question'], 'source_code')) or stage['question'].source_code is None:
                    output += word('(embedded question, source code not available)')
                else:
                    output += highlight(stage['question'].source_code, YamlLexer(), HtmlFormatter(cssclass='highlight dahighlight'))
            elif 'variable' in stage:
                output += '          <h5>Needed definition of <code class="da-variable-needed">' + str(stage['variable']) + "</code>" + the_time + "</h5>\n"
            elif 'done' in stage:
                output += "          <h5>Completed processing" + the_time + "</h5>\n"
                seen_done = True
    return output


def read_fields(filename, orig_file_name, input_format, output_format):
    if output_format == 'yaml':
        if input_format == 'pdf':
            fields = base_read_fields(filename)
            fields_seen = set()
            if fields is None:
                raise DAException(word("Error: no fields could be found in the file"))
            fields_output = "---\nquestion: " + word("Here is your document.") + "\nevent: " + 'some_event' + "\nattachment:" + "\n  - name: " + os.path.splitext(orig_file_name)[0] + "\n    filename: " + os.path.splitext(orig_file_name)[0] + "\n    pdf template file: " + re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', orig_file_name) + "\n    fields:\n"
            for field, default, pageno, rect, field_type, export_value in fields:
                if field not in fields_seen:
                    fields_output += '      - "' + str(field) + '": ' + sanitize(default) + "\n"
                    fields_seen.add(field)
            fields_output += "---"
            return fields_output
        if input_format in ('docx', 'markdown'):
            result = ''
            if input_format == 'docx' and CAN_CONVERT_WORD:
                result_file = word_to_markdown(filename, 'docx')
                if result_file is None:
                    raise DAException(word("Error: no fields could be found in the file"))
                with open(result_file.name, 'r', encoding='utf-8') as fp:
                    result = fp.read()
            elif input_format == 'markdown':
                with open(filename, 'r', encoding='utf-8') as fp:
                    result = fp.read()
            fields = set()
            for variable in re.findall(r'{{[pr] \s*([^\}\s]+)\s*}}', result):
                fields.add(docx_variable_fix(variable))
            for variable in re.findall(r'{{\s*([^\}\s]+)\s*}}', result):
                fields.add(docx_variable_fix(variable))
            for variable in re.findall(r'{%[a-z]* for [A-Za-z\_][A-Za-z0-9\_]* in *([^\} ]+) *%}', result):
                fields.add(docx_variable_fix(variable))
            if len(fields) == 0:
                raise DAException(word("Error: no fields could be found in the file"))
            fields_output = "---\nquestion: " + word("Here is your document.") + "\nevent: " + 'some_event' + "\nattachment:" + "\n  - name: " + os.path.splitext(orig_file_name)[0] + "\n    filename: " + os.path.splitext(orig_file_name)[0] + "\n    docx template file: " + re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', orig_file_name) + "\n    fields:\n"
            for field in fields:
                fields_output += '      "' + field + '": ' + "Something\n"
            fields_output += "---"
            return fields_output
    if output_format == 'json':
        if input_format == 'pdf':
            default_text = word("something")
            output = {'fields': [], 'default_values': {}, 'types': {}, 'locations': {}, 'export_values': {}}
            fields = base_read_fields(filename)
            if fields is not None:
                fields_seen = set()
                for field, default, pageno, rect, field_type, export_value in fields:
                    real_default = str(default)
                    if real_default == default_text:
                        real_default = ''
                    if field not in fields_seen:
                        output['fields'].append(str(field))
                        output['default_values'][field] = real_default
                        output['types'][field] = re.sub(r"'", r'', str(field_type))
                        output['locations'][field] = {'page': int(pageno), 'box': rect}
                        output['export_values'][field] = export_value
            return json.dumps(output, sort_keys=True, indent=2)
        if input_format in ('docx', 'markdown'):
            if input_format == 'docx':
                if CAN_CONVERT_WORD:
                    result_file = word_to_markdown(filename, 'docx')
                else:
                    result_file = None
                if result_file is None:
                    return json.dumps({'fields': []}, indent=2)
                with open(result_file.name, 'r', encoding='utf-8') as fp:
                    result = fp.read()
            elif input_format == 'markdown':
                with open(filename, 'r', encoding='utf-8') as fp:
                    result = fp.read()
            fields = set()
            for variable in re.findall(r'{{ *([^\} ]+) *}}', result):
                fields.add(docx_variable_fix(variable))
            for variable in re.findall(r'{%[a-z]* for [A-Za-z\_][A-Za-z0-9\_]* in *([^\} ]+) *%}', result):
                fields.add(docx_variable_fix(variable))
            return json.dumps({'fields': list(fields)}, sort_keys=True, indent=2)
    return None


def get_corresponding_interview(the_package, the_file):
    # logmessage("get_corresponding_interview: " + the_package + " " + the_file)
    interview = None
    if re.match(r'docassemble.playground[0-9]+', the_package):
        separator = ':'
    else:
        separator = ':data/questions/'
    for interview_file in (the_package + separator + the_file + '.yml', the_package + separator + the_file + '.yaml', the_package + separator + 'examples/' + the_file + '.yml'):
        # logmessage("Looking for " + interview_file)
        try:
            interview = get_interview(interview_file)
            break
        except:
            # logmessage("There was an exception looking for " + interview_file + ": " + str(the_err))
            continue
    return interview






def user_interviews_filter(obj):
    if isinstance(obj, DA.Condition):
        leftside = user_interviews_filter(obj.leftside)
        rightside = user_interviews_filter(obj.rightside)
        if obj.operator == 'and':
            return leftside & rightside
        if obj.operator == 'xor':
            return leftside ^ rightside
        if obj.operator == 'or':
            return leftside | rightside
        if obj.operator == 'not':
            return not_(leftside)
        if obj.operator == 'le':
            return leftside <= rightside
        if obj.operator == 'ge':
            return leftside >= rightside
        if obj.operator == 'gt':
            return leftside > rightside
        if obj.operator == 'lt':
            return leftside < rightside
        if obj.operator == 'eq':
            return leftside == rightside
        if obj.operator == 'ne':
            return leftside != rightside
        if obj.operator == 'like':
            return leftside.like(rightside)
        if obj.operator == 'in':
            return leftside.in_(rightside)
        raise DAException("Operator not recognized")
    if isinstance(obj, DA.Group):
        items = [user_interviews_filter(item) for item in obj.items]
        if obj.group_type == 'and':
            return and_(*items)
        if obj.group_type == 'or':
            return or_(*items)
        raise DAException("Group type not recognized")
    if isinstance(obj, DA.Column):
        if obj.name == 'indexno':
            return UserDict.indexno
        if obj.name == 'modtime':
            return UserDict.modtime
        if obj.name == 'filename':
            return UserDictKeys.filename
        if obj.name == 'key':
            return UserDictKeys.key
        if obj.name == 'encrypted':
            return UserDict.encrypted
        if obj.name == 'user_id':
            return UserDictKeys.user_id
        if obj.name == 'email':
            return UserModel.email
        if obj.name == 'first_name':
            return UserModel.first_name
        if obj.name == 'last_name':
            return UserModel.last_name
        if obj.name == 'country':
            return UserModel.country
        if obj.name == 'subdivisionfirst':
            return UserModel.subdivisionfirst
        if obj.name == 'subdivisionsecond':
            return UserModel.subdivisionsecond
        if obj.name == 'subdivisionthird':
            return UserModel.subdivisionthird
        if obj.name == 'organization':
            return UserModel.organization
        if obj.name == 'timezone':
            return UserModel.timezone
        if obj.name == 'language':
            return UserModel.language
        if obj.name == 'last_login':
            return UserModel.last_login
        raise DAException("Column " + repr(obj.name) + " not available")
    return obj


@hookimpl(specname='user_interviews')
def user_interviews_adapter(user_id, secret, exclude_invalid, action, filename, session, tag, include_dict, delete_shared, admin, start_id, temp_user_id, query, minimal):  # pylint: disable=redefined-outer-name
    return user_interviews(user_id=user_id, secret=secret, exclude_invalid=exclude_invalid, action=action, filename=filename, session=session, tag=tag, include_dict=include_dict, delete_shared=delete_shared, admin=admin, start_id=start_id, temp_user_id=temp_user_id, query=query, minimal=minimal)

def user_interviews(user_id=None, secret=None, exclude_invalid=True, action=None, filename=None, session=None, tag=None, include_dict=True, delete_shared=False, admin=False, start_id=None, temp_user_id=None, query=None, minimal=False):  # pylint: disable=redefined-outer-name
    # logmessage("user_interviews: user_id is " + str(user_id) + " and secret is " + str(secret))
    if minimal is False:
        if session is not None and user_id is None and temp_user_id is None and current_user.is_authenticated and not current_user.has_role_or_permission('admin', 'advocate', permissions=['access_sessions']):
            user_id = current_user.id
        elif user_id is None and (current_user.is_anonymous or not current_user.has_role_or_permission('admin', 'advocate', permissions=['access_sessions'])):
            raise DAException('user_interviews: you do not have sufficient privileges to access information about other users')
        if user_id is not None and admin is False and not (current_user.is_authenticated and (current_user.same_as(user_id) or current_user.has_role_or_permission('admin', 'advocate', permissions=['access_sessions']))):
            raise DAException('user_interviews: you do not have sufficient privileges to access information about other users')
        if action is not None and admin is False and not current_user.has_role_or_permission('admin', 'advocate', permissions=['edit_sessions']):
            if user_id is None:
                raise DAException("user_interviews: no user_id provided")
            the_user = get_person(int(user_id), {})
            if the_user is None:
                raise DAException("user_interviews: user_id " + str(user_id) + " not valid")
    if query is not None:
        the_query = user_interviews_filter(query)
    if action == 'delete_all':
        sessions_to_delete = set()
        if tag or query is not None:
            start_id = None
            while True:
                (the_list, start_id) = user_interviews(user_id=user_id, secret=secret, filename=filename, session=session, tag=tag, include_dict=False, exclude_invalid=False, start_id=start_id, temp_user_id=temp_user_id, query=query, minimal=True)
                for interview_info in the_list:
                    sessions_to_delete.add((interview_info['session'], interview_info['filename'], interview_info['user_id'], interview_info['temp_user_id']))
                if start_id is None:
                    break
        else:
            where_clause = []
            if temp_user_id is not None:
                where_clause.append(UserDictKeys.temp_user_id == temp_user_id)
            elif user_id is not None:
                where_clause.append(UserDictKeys.user_id == user_id)
            if filename is not None:
                where_clause.append(UserDictKeys.filename == filename)
            if session is not None:
                where_clause.append(UserDictKeys.key == session)
            interview_query = db.session.execute(select(UserDictKeys.filename, UserDictKeys.key, UserDictKeys.user_id, UserDictKeys.temp_user_id).where(*where_clause).group_by(UserDictKeys.filename, UserDictKeys.key, UserDictKeys.user_id, UserDictKeys.temp_user_id))
            for interview_info in interview_query:
                sessions_to_delete.add((interview_info.key, interview_info.filename, interview_info.user_id, interview_info.temp_user_id))
            if user_id is not None:
                if filename is None:
                    interview_query = db.session.execute(select(UserDict.filename, UserDict.key).where(UserDict.user_id == user_id).group_by(UserDict.filename, UserDict.key))
                else:
                    interview_query = db.session.execute(select(UserDict.filename, UserDict.key).where(UserDict.user_id == user_id, UserDict.filename == filename).group_by(UserDict.filename, UserDict.key))
                for interview_info in interview_query:
                    sessions_to_delete.add((interview_info.key, interview_info.filename, user_id, None))
        logmessage("Deleting " + str(len(sessions_to_delete)) + " interviews")
        if len(sessions_to_delete) > 0:
            for session_id, yaml_filename, the_user_id, the_temp_user_id in sessions_to_delete:
                manual_checkout(manual_session_id=session_id, manual_filename=yaml_filename, user_id=the_user_id, delete_session=True, temp_user_id=the_temp_user_id)
                # obtain_lock(session_id, yaml_filename)
                if the_user_id is None or delete_shared:
                    reset_user_dict(session_id, yaml_filename, user_id=the_user_id, temp_user_id=the_temp_user_id, force=True)
                else:
                    reset_user_dict(session_id, yaml_filename, user_id=the_user_id, temp_user_id=the_temp_user_id)
                # release_lock(session_id, yaml_filename)
        return len(sessions_to_delete)
    if action == 'delete':
        if filename is None or session is None:
            raise DAException("user_interviews: filename and session must be provided in order to delete interview")
        manual_checkout(manual_session_id=session, manual_filename=filename, user_id=user_id, temp_user_id=temp_user_id, delete_session=True)
        # obtain_lock(session, filename)
        reset_user_dict(session, filename, user_id=user_id, temp_user_id=temp_user_id, force=delete_shared)
        # release_lock(session, filename)
        return True
    if minimal:
        the_timezone = None
    elif admin is False and current_user and current_user.is_authenticated and current_user.timezone:
        the_timezone = zoneinfo.ZoneInfo(current_user.timezone)
    else:
        the_timezone = zoneinfo.ZoneInfo(get_default_timezone())

    interviews_length = 0
    interviews = []

    while True:
        there_are_more = False
        if temp_user_id is not None:
            query_elements = [UserDict.indexno, UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDictKeys.filename, UserDictKeys.key, UserModel.email]
            subq_filter_elements = [UserDictKeys.temp_user_id == temp_user_id]
            if include_dict:
                query_elements.extend([UserDict.dictionary, UserDict.encrypted])
            else:
                query_elements.append(UserDict.modtime)
            if filename is not None:
                subq_filter_elements.append(UserDictKeys.filename == filename)
            if session is not None:
                subq_filter_elements.append(UserDictKeys.key == session)
            if start_id is not None:
                subq_filter_elements.append(UserDict.indexno > start_id)
            subq = select(UserDictKeys.filename, UserDictKeys.key, db.func.max(UserDict.indexno).label('indexno')).join(UserDict, and_(UserDictKeys.filename == UserDict.filename, UserDictKeys.key == UserDict.key))  # pylint: disable=not-callable
            if len(subq_filter_elements) > 0:
                subq = subq.where(and_(*subq_filter_elements))
            subq = subq.group_by(UserDictKeys.filename, UserDictKeys.key).subquery()
            interview_query = select(*query_elements).select_from(subq.join(UserDict, subq.c.indexno == UserDict.indexno).join(UserDictKeys, and_(UserDict.filename == UserDictKeys.filename, UserDict.key == UserDictKeys.key, UserDictKeys.temp_user_id == temp_user_id)).outerjoin(UserModel, 0 == 1))  # pylint: disable=comparison-of-constants
            if query is not None:
                interview_query = interview_query.where(the_query)
            interview_query = interview_query.order_by(UserDict.indexno)
        elif user_id is not None:
            query_elements = [UserDict.indexno, UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDictKeys.filename, UserDictKeys.key, UserModel.email]
            subq_filter_elements = [UserDictKeys.user_id == user_id]
            if include_dict:
                query_elements.extend([UserDict.dictionary, UserDict.encrypted])
            else:
                query_elements.append(UserDict.modtime)
            if filename is not None:
                subq_filter_elements.append(UserDictKeys.filename == filename)
            if session is not None:
                subq_filter_elements.append(UserDictKeys.key == session)
            if start_id is not None:
                subq_filter_elements.append(UserDict.indexno > start_id)
            subq = select(UserDictKeys.filename, UserDictKeys.key, db.func.max(UserDict.indexno).label('indexno')).join(UserDict, and_(UserDictKeys.filename == UserDict.filename, UserDictKeys.key == UserDict.key))  # pylint: disable=not-callable
            if len(subq_filter_elements) > 0:
                subq = subq.where(and_(*subq_filter_elements))
            subq = subq.group_by(UserDictKeys.filename, UserDictKeys.key).subquery()
            interview_query = select(*query_elements).select_from(subq.join(UserDict, subq.c.indexno == UserDict.indexno).join(UserDictKeys, and_(UserDict.filename == UserDictKeys.filename, UserDict.key == UserDictKeys.key, UserDictKeys.user_id == user_id)).join(UserModel, UserDictKeys.user_id == UserModel.id))
            if query is not None:
                interview_query = interview_query.where(the_query)
            interview_query = interview_query.order_by(UserDict.indexno)
        else:
            query_elements = [UserDict.indexno, UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDict.filename, UserDict.key, UserModel.email]
            subq_filter_elements = []
            if include_dict:
                query_elements.extend([UserDict.dictionary, UserDict.encrypted])
            else:
                query_elements.append(UserDict.modtime)
            if filename is not None:
                subq_filter_elements.append(UserDict.filename == filename)
            if session is not None:
                subq_filter_elements.append(UserDict.key == session)
            if start_id is not None:
                subq_filter_elements.append(UserDict.indexno > start_id)
            subq = select(UserDict.filename, UserDict.key, db.func.max(UserDict.indexno).label('indexno'))  # pylint: disable=not-callable
            if len(subq_filter_elements) > 0:
                subq = subq.where(and_(*subq_filter_elements))
            subq = subq.group_by(UserDict.filename, UserDict.key).subquery()
            interview_query = select(*query_elements).select_from(subq.join(UserDict, subq.c.indexno == UserDict.indexno).join(UserDictKeys, and_(UserDict.filename == UserDictKeys.filename, UserDict.key == UserDictKeys.key)).outerjoin(UserModel, and_(UserDictKeys.user_id == UserModel.id, UserModel.active == True)))  # noqa: E712 # pylint: disable=singleton-comparison
            if query is not None:
                interview_query = interview_query.where(the_query)
            interview_query = interview_query.order_by(UserDict.indexno)
        interview_query = interview_query.limit(PAGINATION_LIMIT_PLUS_ONE)
        stored_info = []
        results_in_query = 0
        for interview_info in db.session.execute(interview_query):
            results_in_query += 1
            if results_in_query == PAGINATION_LIMIT_PLUS_ONE:
                there_are_more = True
                break
            # logmessage("filename is " + str(interview_info.filename) + " " + str(interview_info.key))
            if session is not None and interview_info.key != session:
                continue
            if include_dict and interview_info.dictionary is None:
                continue
            if include_dict:
                stored_info.append({'filename': interview_info.filename,
                                    'encrypted': interview_info.encrypted,
                                    'dictionary': interview_info.dictionary,
                                    'key': interview_info.key,
                                    'email': interview_info.email,
                                    'user_id': interview_info.user_id,
                                    'temp_user_id': interview_info.temp_user_id,
                                    'indexno': interview_info.indexno})
            else:
                stored_info.append({'filename': interview_info.filename,
                                    'modtime': interview_info.modtime,
                                    'key': interview_info.key,
                                    'email': interview_info.email,
                                    'user_id': interview_info.user_id,
                                    'temp_user_id': interview_info.temp_user_id,
                                    'indexno': interview_info.indexno})
        for interview_info in stored_info:
            if interviews_length == PAGINATION_LIMIT:
                there_are_more = True
                break
            start_id = interview_info['indexno']
            if minimal:
                interviews.append({'filename': interview_info['filename'], 'session': interview_info['key'], 'user_id': interview_info['user_id'], 'temp_user_id': interview_info['temp_user_id']})
                interviews_length += 1
                continue
            interview_title = {}
            is_valid = True
            interview_valid = True
            try:
                interview = get_interview(interview_info['filename'])
            except:
                if exclude_invalid:
                    continue
                logmessage("user_interviews: unable to load interview file " + interview_info['filename'])
                interview_title['full'] = word('Error: interview not found')
                interview_valid = False
                is_valid = False
            # logmessage("Found old interview with title " + interview_title)
            if include_dict:
                if interview_info['encrypted']:
                    try:
                        dictionary = decrypt_dictionary(interview_info['dictionary'], secret)
                    except BaseException as the_err:
                        if exclude_invalid:
                            continue
                        try:
                            logmessage("user_interviews: unable to decrypt dictionary.  " + str(the_err.__class__.__name__) + ": " + str(the_err))
                        except:
                            logmessage("user_interviews: unable to decrypt dictionary.  " + str(the_err.__class__.__name__))
                        dictionary = fresh_dictionary()
                        dictionary['_internal']['starttime'] = None
                        dictionary['_internal']['modtime'] = None
                        is_valid = False
                else:
                    try:
                        dictionary = unpack_dictionary(interview_info['dictionary'])
                    except BaseException as the_err:
                        if exclude_invalid:
                            continue
                        try:
                            logmessage("user_interviews: unable to unpack dictionary.  " + str(the_err.__class__.__name__) + ": " + str(the_err))
                        except:
                            logmessage("user_interviews: unable to unpack dictionary.  " + str(the_err.__class__.__name__))
                        dictionary = fresh_dictionary()
                        dictionary['_internal']['starttime'] = None
                        dictionary['_internal']['modtime'] = None
                        is_valid = False
                if not isinstance(dictionary, dict):
                    logmessage("user_interviews: found a dictionary that was not a dictionary")
                    continue
            if is_valid:
                if include_dict:
                    interview_title = interview.get_title(dictionary)
                    tags = interview.get_tags(dictionary)
                else:
                    interview_title = interview.get_title({'_internal': {}})
                    tags = interview.get_tags({'_internal': {}})
                metadata = copy.deepcopy(interview.consolidated_metadata)
            elif interview_valid:
                interview_title = interview.get_title({'_internal': {}})
                metadata = copy.deepcopy(interview.consolidated_metadata)
                if include_dict:
                    tags = interview.get_tags(dictionary)
                    if 'full' not in interview_title:
                        interview_title['full'] = word("Interview answers cannot be decrypted")
                    else:
                        interview_title['full'] += ' - ' + word('interview answers cannot be decrypted')
                else:
                    tags = interview.get_tags({'_internal': {}})
                    if 'full' not in interview_title:
                        interview_title['full'] = word('Unknown')
            else:
                interview_title['full'] = word('Error: interview not found and answers could not be decrypted')
                metadata = {}
                tags = set()
            if include_dict:
                if dictionary['_internal']['starttime'] and isinstance(dictionary['_internal']['starttime'], datetime.datetime):
                    utc_starttime = dictionary['_internal']['starttime']
                    starttime = nice_date_from_utc(dictionary['_internal']['starttime'], timezone=the_timezone)
                else:
                    utc_starttime = None
                    starttime = ''
                if dictionary['_internal']['modtime']:
                    utc_modtime = dictionary['_internal']['modtime']
                    modtime = nice_date_from_utc(dictionary['_internal']['modtime'], timezone=the_timezone)
                else:
                    utc_modtime = None
                    modtime = ''
            else:
                utc_starttime = None
                starttime = ''
                utc_modtime = interview_info['modtime']
                modtime = nice_date_from_utc(interview_info['modtime'], timezone=the_timezone)
            if tag is not None and tag not in tags:
                continue
            out = {'filename': interview_info['filename'], 'session': interview_info['key'], 'modtime': modtime, 'starttime': starttime, 'utc_modtime': utc_modtime, 'utc_starttime': utc_starttime, 'title': interview_title.get('full', word('Untitled')), 'subtitle': interview_title.get('sub', None), 'valid': is_valid, 'metadata': metadata, 'tags': tags, 'email': interview_info['email'], 'user_id': interview_info['user_id'], 'temp_user_id': interview_info['temp_user_id']}
            if include_dict:
                out['dict'] = dictionary
                out['encrypted'] = interview_info['encrypted']
            interviews.append(out)
            interviews_length += 1
        if interviews_length == PAGINATION_LIMIT or results_in_query < PAGINATION_LIMIT_PLUS_ONE:
            break
    if there_are_more:
        return (interviews, start_id)
    return (interviews, None)


def valid_date_key(x):
    if x['dict']['_internal']['starttime'] is None:
        return datetime.datetime.now()
    return x['dict']['_internal']['starttime']


def fix_secret(user=None, to_convert=None):
    # logmessage("fix_secret starting")
    if user is None:
        user = current_user
    password = str(request.form.get('password', request.form.get('new_password', None)))
    if password is not None:
        secret = str(request.cookies.get('secret', None))
        newsecret = pad_to_16(MD5Hash(data=password).hexdigest())
        if secret == 'None' or secret != newsecret:
            # logmessage("fix_secret: calling substitute_secret with " + str(secret) + ' and ' + str(newsecret))
            # logmessage("fix_secret: setting newsecret session")
            session['newsecret'] = substitute_secret(str(secret), newsecret, user=user, to_convert=to_convert)
        # else:
        #     logmessage("fix_secret: secrets are the same")
    else:
        logmessage("fix_secret: password not in request")


def get_part(part, default=None):
    if default is None:
        default = str()
    if part not in page_parts:
        return default
    if 'language' in session:
        lang = session['language']
    else:
        lang = DEFAULT_LANGUAGE
    if lang in page_parts[part]:
        return page_parts[part][lang]
    if lang != DEFAULT_LANGUAGE and DEFAULT_LANGUAGE in page_parts[part]:
        return page_parts[part][DEFAULT_LANGUAGE]
    if '*' in page_parts[part]:
        return page_parts[part]['*']
    return default


def process_set_variable(field_name, user_dict, vars_set, old_values):
    vars_set.add(field_name)
    try:
        old_values[field_name] = eval(field_name, user_dict)
    except:
        pass
