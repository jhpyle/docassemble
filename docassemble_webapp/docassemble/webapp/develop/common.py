import re
import json
import httplib2
from sqlalchemy import select
from flask import current_app, session
from flask_login import current_user
from docassemble.base.error import DAException
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.users.models import UserModel
from docassemble.webapp.utils.redis_cred_storage import RedisCredStorage

def project_name(name):
    return '' if name == 'default' else name

def get_repo_info(giturl):
    giturl = re.sub(r'#.*', '', giturl)
    repo_name = re.sub(r'/*$', '', giturl)
    m = re.search(r'//(.+):x-oauth-basic@github.com', repo_name)
    if m:
        access_token = m.group(1)
    else:
        access_token = None
    repo_name = re.sub(r'^git\+', '', repo_name)
    repo_name = re.sub(r'^http.*github.com/', '', repo_name)
    repo_name = re.sub(r'.*@github.com:', '', repo_name)
    repo_name = re.sub(r'[@#].*', '', repo_name)
    repo_name = re.sub(r'.git$', '', repo_name)
    if current_app.config['USE_GITHUB']:
        github_auth = r.get('da:using_github:userid:' + str(current_user.id))
    else:
        github_auth = None
    if github_auth and access_token is None:
        storage = RedisCredStorage(oauth_app='github')
        credentials = storage.get()
        if not credentials or credentials.invalid:
            http = httplib2.Http()
        else:
            http = credentials.authorize(httplib2.Http())
    else:
        http = httplib2.Http()
    the_url = "https://api.github.com/repos/" + repo_name
    if access_token:
        resp, content = http.request(the_url, "GET", headers={'Authorization': "token " + access_token})
    else:
        resp, content = http.request(the_url, "GET")
    if int(resp['status']) == 200:
        return json.loads(content.decode())
    raise DAException(the_url + " fetch failed on first try; got " + str(resp['status']))


def get_playground_user():
    if 'playground_user' in session:
        user = db.session.execute(select(UserModel).filter_by(id=session['playground_user'])).scalar()
        return user
    return current_user
