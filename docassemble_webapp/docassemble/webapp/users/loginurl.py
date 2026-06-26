import json
import re
from sqlalchemy import select
from docassemble.base.generate_key import random_string
from docassemble.base.thread_context import this_thread
from docassemble.webapp.config import daconfig
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.interview.helpers import user_interviews
from docassemble.webapp.interview.user_dict import fetch_user_dict
from docassemble.webapp.daredis import r
from docassemble.webapp.utils.encryption import encrypt_dictionary
from docassemble.webapp.utils.helpers import (
    get_url_from_file_reference,
    true_or_false,
    url_for,
)
from .helpers import get_secret
from .models import UserModel


@hookimpl
def get_login_url(kwargs):
    username = kwargs.get('username', None)
    password = kwargs.get('password', None)
    if username is None or password is None:
        return {"status": "error", "message": "A username and password must be supplied"}
    username = str(username)
    password = str(password)
    try:
        secret = get_secret(username, password, False)
    except BaseException as err:
        return {"status": "auth_error", "message": str(err)}
    try:
        expire = int(kwargs.get('expire', 15))
        assert expire > 0
    except:
        return {"status": "error", "message": "Invalid number of seconds."}
    if 'url_args' in kwargs:
        if isinstance(kwargs['url_args'], dict):
            url_args = kwargs['url_args']
        else:
            try:
                url_args = json.loads(kwargs['url_args'])
                assert isinstance(url_args, dict)
            except:
                return {"status": "error", "message": "Malformed URL arguments"}
    else:
        url_args = {}
    username = re.sub(r'\%', '', username)
    user = db.session.execute(select(UserModel).where(UserModel.email.ilike(username))).scalar()
    if user is None:
        return {"status": "auth_error", "message": "Username not known"}
    info = {'user_id': user.id, 'secret': secret}
    del user
    if 'next' in kwargs:
        try:
            path = get_url_from_file_reference(kwargs['next'], {})
            assert isinstance(path, str)
            assert not path.startswith('javascript')
        except:
            return {"status": "error", "message": "Unknown path for next"}
    for key in ['i', 'next', 'session']:
        if key in kwargs:
            info[key] = kwargs[key]
    if len(url_args) > 0:
        info['url_args'] = url_args
    if 'i' in info:
        old_yaml_filename = this_thread.current_info.get('yaml_filename', None)
        this_thread.current_info['yaml_filename'] = info['i']
        if 'session' in info:
            try:
                steps, user_dict, is_encrypted = fetch_user_dict(info['session'], info['i'], secret=secret)  # pylint: disable=unused-variable
                info['encrypted'] = is_encrypted
            except:
                if old_yaml_filename:
                    this_thread.current_info['yaml_filename'] = old_yaml_filename
                return {"status": "error", "message": "Could not decrypt dictionary"}
        elif true_or_false(kwargs.get('resume_existing', False)) or daconfig.get('auto login resume existing', False):
            interviews = user_interviews(user_id=info['user_id'], secret=secret, exclude_invalid=True, filename=info['i'], include_dict=True)[0]
            if len(interviews) > 0:
                info['session'] = interviews[0]['session']
                info['encrypted'] = interviews[0]['encrypted']
            del interviews
        if old_yaml_filename:
            this_thread.current_info['yaml_filename'] = old_yaml_filename
    encryption_key = random_string(16)
    encrypted_text = encrypt_dictionary(info, encryption_key)
    while True:
        code = random_string(24)
        the_key = 'da:auto_login:' + code
        if r.get(the_key) is None:
            break
    pipe = r.pipeline()
    pipe.set(the_key, encrypted_text)
    pipe.expire(the_key, expire)
    pipe.execute()
    return {"status": "success", "url": url_for('users.auto_login', key=encryption_key + code, _external=True)}
