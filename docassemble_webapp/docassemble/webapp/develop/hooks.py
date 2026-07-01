import json
from flask_login import current_user
from flask import current_app, redirect, request, session
from docassemble.base.generate_key import random_string
from docassemble.webapp.daredis import r
from docassemble.webapp.utils.redis_cred_storage import RedisCredStorage
from ..hooks.impl import hookimpl
from .helpers import get_github_flow

@hookimpl
def devel_login():
    if current_app.config['USE_GITHUB'] and r.get('da:using_github:userid:' + str(current_user.id)) is not None:
        storage = RedisCredStorage(oauth_app='github')
        credentials = storage.get()
        if not credentials or credentials.invalid:
            state_string = random_string(16)
            session['github_next'] = json.dumps({'state': state_string, 'path': 'update_package', 'arguments': request.args})
            flow = get_github_flow()
            uri = flow.step1_get_authorize_url(state=state_string)
            return redirect(uri)
    return None
