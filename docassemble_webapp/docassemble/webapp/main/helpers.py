import os
import time
import subprocess
from flask_login import current_user
from sqlalchemy import select, delete as sqldelete
from docassemble.base.functions import package_data_filename
from docassemble.base.generate_key import random_alphanumeric, random_string
from docassemble.base.interview_cache import get_interview
from docassemble.base.language.words import word
from docassemble.webapp.config import (
    DEFAULT_LANGUAGE,
    daconfig,
    WEBAPP_PATH,
    hostname,
    SINGLE_SERVER,
    USING_SUPERVISOR,
    SUPERVISORCTL,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.utils.encryption import decrypt_dictionary, encrypt_dictionary
from docassemble.webapp.utils.helpers import url_for_interview
from docassemble.webapp.utils.logger import logmessage
from .models import Supervisors

@hookimpl
def stash_data(data, expire):
    while True:
        key = random_alphanumeric(16)
        if r.get(key) is None:
            break
    secret = random_string(16)
    packed_data = encrypt_dictionary(data, secret)
    pipe = r.pipeline()
    pipe.set('da:stash:' + key, packed_data)
    pipe.expire('da:stash:' + key, expire)
    pipe.execute()
    return (key, secret)


@hookimpl
def retrieve_stashed_data(key, secret, delete, refresh):
    packed_data = r.get('da:stash:' + key)
    if packed_data is None:
        return None
    try:
        data = decrypt_dictionary(packed_data.decode(), secret)
    except:
        return None
    if delete:
        r.delete('da:stash:' + key)
    elif refresh and isinstance(refresh, int) and refresh > 0:
        r.expire('da:stash:' + key, refresh)
    return data


class AdminInterview:

    def is_not(self, interview):
        return self.interview != interview

    def can_use(self):
        if (self.require_login or self.unique_sessions) and current_user.is_anonymous:
            return False
        if self.roles is None:
            return True
        if current_user.is_anonymous:
            if 'anonymous' in self.roles:
                return True
            return False
        if current_user.has_roles(self.roles):
            return True
        return False

    def get_title(self, language):
        if isinstance(self.title, str):
            return word(self.title, language=language)
        if language in self.title:
            return self.title[language]
        if '*' in self.title:
            return self.title['*']
        if DEFAULT_LANGUAGE in self.title:
            return self.title[DEFAULT_LANGUAGE]
        for lang, title in self.title.items():  # pylint: disable=unused-variable
            return word(title, language=language)

    def get_url(self):
        return url_for_interview(i=self.interview, new_session='1')


class MenuItem:

    def is_not(self, interview):  # pylint: disable=unused-argument
        return True

    def can_use(self):
        if self.require_login and current_user.is_anonymous:
            return False
        if self.roles is None:
            return True
        if current_user.is_anonymous:
            if 'anonymous' in self.roles:
                return True
            return False
        if current_user.has_roles(self.roles):
            return True
        return False

    def get_title(self, language):
        if language in self.label:
            return self.label[language]
        if '*' in self.label:
            return self.label['*']
        if DEFAULT_LANGUAGE in self.label:
            return self.label[DEFAULT_LANGUAGE]
        for lang, label in self.label.items():  # pylint: disable=unused-variable
            return word(label, language=language)

    def get_url(self):
        return self.url


def set_admin_interviews():
    admin_interviews = []
    if 'administrative interviews' in daconfig:
        if isinstance(daconfig['administrative interviews'], list):
            for item in daconfig['administrative interviews']:
                if isinstance(item, dict):
                    if 'url' in item and 'label' in item and isinstance(item['url'], str) and isinstance(item['label'], dict):
                        menu_item = MenuItem()
                        menu_item.url = item['url']
                        menu_item.label = item['label']
                        menu_item.roles = item['roles']
                        menu_item.require_login = item['require_login']
                        menu_item.unique_sessions = item['unique_sessions']
                        admin_interviews.append(menu_item)
                    elif 'interview' in item and isinstance(item['interview'], str):
                        try:
                            interview = get_interview(item['interview'])
                        except:
                            logmessage("interview " + item['interview'] + " in administrative interviews did not exist")
                            continue
                        if 'title' in item:
                            the_title = item['title']
                        else:
                            the_title = interview.consolidated_metadata.get('short title', interview.consolidated_metadata.get('title', None))
                            if the_title is None:
                                logmessage("interview in administrative interviews needs to be given a title")
                                continue
                        admin_interview = AdminInterview()
                        admin_interview.interview = item['interview']
                        if isinstance(the_title, (str, dict)):
                            if isinstance(the_title, dict):
                                fault = False
                                for key, val in the_title.items():
                                    if not (isinstance(key, str) and isinstance(val, str)):
                                        fault = True
                                        break
                                if fault:
                                    logmessage("title of administrative interviews item must be a string or a dictionary with keys and values that are strings")
                                    continue
                            admin_interview.title = the_title
                        else:
                            logmessage("title of administrative interviews item must be a string or a dictionary")
                            continue
                        if 'required privileges' not in item:
                            roles = set()
                            for metadata in interview.metadata:
                                if 'required privileges for listing' in metadata:
                                    roles = set()
                                    privs = metadata['required privileges for listing']
                                    if isinstance(privs, list):
                                        for priv in privs:
                                            if isinstance(priv, str):
                                                roles.add(priv)
                                    elif isinstance(privs, str):
                                        roles.add(privs)
                                elif 'required privileges' in metadata:
                                    roles = set()
                                    privs = metadata['required privileges']
                                    if isinstance(privs, list):
                                        for priv in privs:
                                            if isinstance(priv, str):
                                                roles.add(priv)
                                    elif isinstance(privs, str):
                                        roles.add(privs)
                            if len(roles) > 0:
                                item['required privileges'] = list(roles)
                        if 'required privileges' in item:
                            fault = False
                            if isinstance(item['required privileges'], list):
                                for rolename in item['required privileges']:
                                    if not isinstance(rolename, str):
                                        fault = True
                                        break
                            else:
                                fault = True
                            if fault:
                                logmessage("required privileges in administrative interviews item must be a list of strings")
                                admin_interview.roles = None
                            else:
                                admin_interview.roles = item['required privileges']
                        else:
                            admin_interview.roles = None
                        admin_interview.require_login = False
                        if 'require login' in item and item['require login'] is not None:
                            admin_interview.require_login = bool(item['require login'])
                        else:
                            for metadata in interview.metadata:
                                if 'require login' in metadata:
                                    admin_interview.require_login = bool(metadata['require login'])
                        admin_interview.unique_sessions = False
                        if 'sessions are unique' in item and item['sessions are unique'] is not None:
                            admin_interview.unique_sessions = bool(item['sessions are unique'])
                        else:
                            for metadata in interview.metadata:
                                if 'sessions are unique' in metadata:
                                    admin_interview.unique_sessions = bool(metadata['sessions are unique'])
                        admin_interviews.append(admin_interview)
                    else:
                        logmessage("item in administrative interviews must contain a valid interview name")
                else:
                    logmessage("item in administrative interviews is not a dict")
        else:
            logmessage("administrative interviews is not a list")
    return admin_interviews


def test_favicon_file(filename, alt=None):
    the_dir = package_data_filename(daconfig.get('favicon', 'docassemble.webapp:data/static/favicon'))
    if the_dir is None or not os.path.isdir(the_dir):
        return False
    the_file = os.path.join(the_dir, filename)
    if not os.path.isfile(the_file):
        if alt is not None:
            the_file = os.path.join(the_dir, alt)
        if not os.path.isfile(the_file):
            return False
    return True


def trigger_update(except_for=None):
    logmessage("trigger_update: except_for is " + str(except_for) + " and hostname is " + hostname)
    if USING_SUPERVISOR:
        to_delete = set()
        for host in db.session.execute(select(Supervisors)).scalars():
            if host.url and not (except_for and host.hostname == except_for):
                if host.hostname == hostname:
                    the_url = 'http://localhost:9001'
                    logmessage("trigger_update: using http://localhost:9001")
                else:
                    the_url = host.url
                args = SUPERVISORCTL + ['-s', the_url, 'start', 'update']
                result = subprocess.run(args, check=False).returncode
                if result == 0:
                    logmessage("trigger_update: sent update to " + str(host.hostname) + " using " + the_url)
                else:
                    logmessage("trigger_update: call to supervisorctl on " + str(host.hostname) + " was not successful")
                    to_delete.add(host.id)
        for id_to_delete in to_delete:
            db.session.execute(sqldelete(Supervisors).filter_by(id=id_to_delete))
            db.session.commit()


def restart_on(host):
    if not USING_SUPERVISOR:
        return True
    logmessage("restart_on: " + str(host.hostname))
    if host.hostname == hostname:
        the_url = 'http://localhost:9001'
    else:
        the_url = host.url
    args = SUPERVISORCTL + ['-s', the_url, 'start', 'reset']
    result = subprocess.run(args, check=False).returncode
    if result == 0:
        logmessage("restart_on: sent reset to " + str(host.hostname))
    else:
        logmessage("restart_on: call to supervisorctl with reset on " + str(host.hostname) + " was not successful")
        return False
    return True


def restart_all():
    logmessage("restarting all")
    for interview_path in [x.decode() for x in r.keys('da:interviewsource:*')]:
        r.delete(interview_path)
    if not SINGLE_SERVER:
        restart_others()
    restart_this()


def restart_this():
    logmessage("restart_this: hostname is " + str(hostname))
    if SINGLE_SERVER and USING_SUPERVISOR:
        args = SUPERVISORCTL + ['-s', 'http://localhost:9001', 'start', 'reset']
        result = subprocess.run(args, check=False).returncode
        if result == 0:
            logmessage("restart_this: sent reset")
        else:
            logmessage("restart_this: call to supervisorctl with reset was not successful")
        return
    if USING_SUPERVISOR:
        to_delete = set()
        for host in db.session.execute(select(Supervisors)).scalars():
            if host.url:
                logmessage("restart_this: considering " + str(host.hostname) + " against " + str(hostname))
                if host.hostname == hostname:
                    result = restart_on(host)
                    if not result:
                        to_delete.add(host.id)
        for id_to_delete in to_delete:
            db.session.execute(sqldelete(Supervisors).filter_by(id=id_to_delete))
            db.session.commit()
    else:
        logmessage("restart_this: touching wsgi file")
        wsgi_file = WEBAPP_PATH
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a', encoding='utf-8'):
                os.utime(wsgi_file, None)


def restart_others():
    logmessage("restart_others: starting")
    if USING_SUPERVISOR:
        cron_key = 'da:cron_restart'
        cron_url = None
        to_delete = set()
        for host in db.session.execute(select(Supervisors)).scalars():
            if host.url and host.hostname != hostname and ':cron:' in str(host.role):
                pipe = r.pipeline()
                pipe.set(cron_key, 1)
                pipe.expire(cron_key, 10)
                pipe.execute()
                result = restart_on(host)
                if not result:
                    to_delete.add(host.id)
                while r.get(cron_key) is not None:
                    time.sleep(1)
                cron_url = host.url
        for host in db.session.execute(select(Supervisors)).scalars():
            if host.url and host.url != cron_url and host.hostname != hostname and host.id not in to_delete:
                result = restart_on(host)
                if not result:
                    to_delete.add(host.id)
        for id_to_delete in to_delete:
            db.session.execute(sqldelete(Supervisors).filter_by(id=id_to_delete))
            db.session.commit()
