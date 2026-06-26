import json
import re
from flask import request, current_app
from flask_login import login_user, current_user
from sqlalchemy import select
from docassemble.base.generate_key import random_alphanumeric
from docassemble.base.thread_context import this_thread
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.utils.api_key import encrypt_api_key
from docassemble.webapp.daredis import r
from docassemble.webapp.utils.helpers import current_info, get_requester_ip
from docassemble.webapp.extensions import db
from docassemble.webapp.users.models import UserModel
from docassemble.webapp.users.helpers import update_last_login

def add_api_key(user_id, name, method, allowed):
    info = {'constraints': allowed, 'method': method, 'name': name}
    success = False
    for attempt in range(10):  # pylint: disable=unused-variable
        api_key = random_alphanumeric(32)
        info['last_four'] = api_key[-4:]
        new_api_key = encrypt_api_key(api_key, current_app.secret_key)
        if len(r.keys('da:apikey:userid:*:key:' + new_api_key + ':info')) == 0:
            r.set('da:apikey:userid:' + str(user_id) + ':key:' + new_api_key + ':info', json.dumps(info))
            success = True
            break
    if not success:
        return None
    return api_key


def api_key_exists(user_id, api_key):
    rkeys = r.keys('da:apikey:userid:' + str(user_id) + ':key:' + encrypt_api_key(str(api_key), current_app.secret_key) + ':info')
    if len(rkeys) > 0:
        return True
    return False


def existing_api_names(user_id, except_for=None):
    result = []
    rkeys = r.keys('da:apikey:userid:' + str(user_id) + ':key:*:info')
    for key in rkeys:
        key = key.decode()
        if except_for is not None:
            api_key = re.sub(r'.*:key:([^:]+):.*', r'\1', key)
            if api_key == encrypt_api_key(except_for, current_app.secret_key):
                continue
        try:
            info = json.loads(r.get(key).decode())
            result.append(info['name'])
        except:
            continue
    return result


def get_api_info(user_id, name=None, api_key=None):
    result = []
    rkeys = r.keys('da:apikey:userid:' + str(user_id) + ':key:*:info')
    if api_key is not None:
        api_key = encrypt_api_key(api_key, current_app.secret_key)
    for key in rkeys:
        key = key.decode()
        try:
            info = json.loads(r.get(key).decode())
        except:
            logmessage("API information could not be unpacked.")
            continue
        if name is not None:
            if info['name'] == name:
                return info
        info['key'] = ('*' * 28) + info['last_four']
        this_key = re.sub(r'.*:key:([^:]+):.*', r'\1', key)
        if api_key is not None and this_key == api_key:
            return info
        if name is not None or api_key is not None:
            continue
        if 'permissions' not in info:
            info['permissions'] = []
        result.append(info)
    if name is not None or api_key is not None:
        return None
    return result


def delete_api_key(user_id, api_key):
    key = 'da:apikey:userid:' + str(user_id) + ':key:' + encrypt_api_key(api_key, current_app.secret_key) + ':info'
    r.delete(key)


def update_api_key(user_id, api_key, name, method, allowed, add_to_allowed, remove_from_allowed, permissions, add_to_permissions, remove_from_permissions):
    key = 'da:apikey:userid:' + str(user_id) + ':key:' + encrypt_api_key(api_key, current_app.secret_key) + ':info'
    try:
        info = json.loads(r.get(key).decode())
    except:
        return False
    if name is not None:
        info['name'] = name
    if method is not None:
        if info['method'] != method:
            info['constraints'] = []
        info['method'] = method
    if allowed is not None:
        info['constraints'] = allowed
    if add_to_allowed is not None:
        if isinstance(add_to_allowed, list):
            info['constraints'].extend(add_to_allowed)
        elif isinstance(add_to_allowed, str):
            info['constraints'].append(add_to_allowed)
    if remove_from_allowed is not None:
        if isinstance(remove_from_allowed, list):
            to_remove = remove_from_allowed
        elif isinstance(remove_from_allowed, str):
            to_remove = [remove_from_allowed]
        else:
            to_remove = []
        for item in to_remove:
            if item in info['constraints']:
                info['constraints'].remove(item)
    if permissions is not None:
        info['permissions'] = permissions
    if add_to_permissions is not None:
        if isinstance(add_to_permissions, list):
            info['permissions'].extend(add_to_permissions)
        elif isinstance(add_to_permissions, str):
            info['permissions'].append(add_to_permissions)
    if remove_from_permissions is not None:
        if isinstance(remove_from_permissions, list):
            to_remove = remove_from_permissions
        elif isinstance(remove_from_permissions, str):
            to_remove = [remove_from_permissions]
        else:
            to_remove = []
        for item in to_remove:
            if item in info['permissions']:
                info['permissions'].remove(item)
    r.set(key, json.dumps(info))
    return True


def get_api_key():
    api_key = request.args.get('key', None)
    if api_key is None and request.method in ('POST', 'PUT', 'PATCH'):
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        if 'key' in post_data:
            api_key = post_data['key']
    if api_key is None and 'X-API-Key' in request.cookies:
        api_key = request.cookies['X-API-Key']
    if api_key is None and 'X-API-Key' in request.headers:
        api_key = request.headers['X-API-Key']
    if api_key is None and 'Authorization' in request.headers:
        m = re.search(r'^bearer (.*)', request.headers['Authorization'], flags=re.IGNORECASE)
        if m:
            api_key = m.group(1).strip()
    return api_key


def api_verify(roles=None, permissions=None):
    api_key = get_api_key()
    if api_key is None:
        logmessage("api_verify: no API key provided")
        return False
    api_key = encrypt_api_key(api_key, current_app.secret_key)
    rkeys = r.keys('da:apikey:userid:*:key:' + api_key + ':info')
    if len(rkeys) == 0:
        logmessage("api_verify: API key not found")
        return False
    try:
        info = json.loads(r.get(rkeys[0].decode()).decode())
    except:
        logmessage("api_verify: API information could not be unpacked")
        return False
    m = re.match(r'da:apikey:userid:([0-9]+):key:' + re.escape(api_key) + ':info', rkeys[0].decode())
    if not m:
        logmessage("api_verify: user id could not be extracted")
        return False
    user_id = m.group(1)
    if not isinstance(info, dict):
        logmessage("api_verify: API information was in the wrong format")
        return False
    if len(info['constraints']) > 0:
        clientip = get_requester_ip(request)
        if info['method'] == 'ip' and clientip not in info['constraints']:
            logmessage("api_verify: IP address " + str(clientip) + " did not match")
            return False
        if info['method'] == 'referer':
            if not request.referrer:
                the_referer = request.headers.get('Origin', None)
                if not the_referer:
                    logmessage("api_verify: could not authorize based on referer because no referer provided")
                    return False
            else:
                the_referer = request.referrer
            matched = False
            for constraint in info['constraints']:
                constraint = re.sub(r'^[\*]+|[\*]+$', '', constraint)
                constraint = re.escape(constraint)
                constraint = re.sub(r'\\\*+', '.*', constraint)
                the_referer = re.sub(r'\?.*', '', the_referer)
                the_referer = re.sub(r'^https?://([^/]*)/', r'\1', the_referer)
                if re.search(constraint, the_referer):
                    matched = True
                    break
            if not matched:
                logmessage("api_verify: authorization failure referer " + str(the_referer) + " could not be matched")
                return False
    user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.id == user_id)).scalar()
    if user is None or user.social_id.startswith('disabled$'):
        logmessage("api_verify: user does not exist")
        return False
    if not user.active:
        logmessage("api_verify: user is no longer active")
        return False
    login_user(user, remember=False)
    update_last_login(user)
    if current_user.has_role('admin') and 'permissions' in info and len(info['permissions']) > 0:
        current_user.limited_api = True
        current_user.limits = info['permissions']
    ok_permission = False
    if permissions:
        for permission in permissions:
            if current_user.can_do(permission):
                ok_permission = True
                break
        if current_user.limited_api and not ok_permission:
            logmessage("api_verify: user did not have correct privileges for resource")
            return False
    if roles and not ok_permission:
        ok_role = False
        for role in roles:
            if current_user.has_role(role):
                ok_role = True
                break
        if not ok_role:
            logmessage("api_verify: user did not have correct privileges for resource")
            return False
    this_thread.current_info = current_info(req=request, interface='api', device_id=request.cookies.get('ds', None), session_uid=current_user.email)
    return True


def fix_api_key(match):
    return 'da:apikey:userid:' + match.group(1) + ':key:' + encrypt_api_key(match.group(2), current_app.secret_key) + ':info'


def fix_api_keys():
    to_delete = []
    for rkey in r.keys('da:api:userid:*:key:*:info'):
        try:
            rkey = rkey.decode()
        except:
            continue
        try:
            info = json.loads(r.get(rkey).decode())
            assert isinstance(info, dict)
        except:
            to_delete.append(rkey)
            continue
        info['last_four'] = re.sub(r'da:api:userid:.*:key:.*(....):info', r'\1', rkey)
        new_rkey = re.sub(r'da:api:userid:(.*):key:(.*):info', fix_api_key, rkey)
        r.set(new_rkey, json.dumps(info))
        to_delete.append(rkey)
    for rkey in to_delete:
        r.delete(rkey)
