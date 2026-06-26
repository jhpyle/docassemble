import datetime
import re
import sys
import time
import dateutil
import click
from flask import current_app
from flask_login import login_user
from sqlalchemy import or_, and_, select
from sqlalchemy.orm import joinedload
from docassemble.base.functions import SS_NEW, SS_IGNORE, dict_as_json
from docassemble.base.interview_cache import get_interview
from docassemble.base.parse import InterviewStatus
from docassemble.base.thread_context import (
    empty_globals,
    global_context,
    this_thread,
    user_dict_context,
)
from docassemble.webapp.config import daconfig
from docassemble.webapp.daredis import r, r_user
from docassemble.webapp.errors import error_notification
from docassemble.webapp.extensions import db
from docassemble.webapp.interview.helpers import (
    save_user_dict,
    reset_user_dict,
    user_interviews,
    delete_user_data,
)
from docassemble.webapp.interview.models import UserDict, UserDictKeys
from docassemble.webapp.lock import release_lock, obtain_lock_patiently
from docassemble.webapp.tasks.app import celery_app
from docassemble.webapp.users.models import Role, UserModel
from docassemble.webapp.users.models import UserRoles
from docassemble.webapp.utils.helpers import set_request_active
from docassemble.webapp.utils.encryption import unpack_dictionary
from docassemble.webapp.utils.logger import logmessage
from . import cron_bp


def get_filenames():
    results = []
    for record in db.session.execute(select(UserDict.filename).where(UserDict.encrypted == False).group_by(UserDict.filename)):  # noqa: E712 # pylint: disable=singleton-comparison
        results.append(record.filename)
    return results


def get_records(filename, last_index):
    subq = select(UserDict.key, UserDict.filename, db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('cnt')).group_by(UserDict.filename, UserDict.key).where(UserDict.filename == filename, UserDict.encrypted == False, UserDict.indexno > last_index).subquery()  # noqa: E712 # pylint: disable=singleton-comparison
    results = []
    for record in db.session.execute(select(UserDict.key, UserDict.filename, UserDict.dictionary, subq.c.indexno, subq.c.cnt).join(subq, and_(subq.c.indexno == UserDict.indexno)).order_by(UserDict.indexno).limit(200)):
        results.append((record.indexno, record.key, record.filename, record.dictionary, record.cnt))
    return results


def get_cron_user():
    statement = (
        select(UserModel)
        .options(joinedload(UserModel.roles))
        .filter(UserModel.roles.any(name='cron'))
        .limit(1)
    )
    return db.session.scalars(statement).first()


def delete_inactive_users():
    user_auto_delete = daconfig.get('user auto delete', {})
    if not isinstance(user_auto_delete, dict):
        logmessage("Error in configuration for user auto delete")
        return
    if not user_auto_delete.get('enable', True):
        return
    try:
        cutoff_days = int(user_auto_delete.get('inactive days', 0))
        assert cutoff_days >= 0
    except:
        logmessage("Error in configuration for user auto delete")
        return
    if cutoff_days == 0:
        return
    delete_shared = bool(user_auto_delete.get('delete shared', False))
    role_ids = {}
    for item in db.session.scalars(select(Role)):
        role_ids[item.name] = item.id
    roles = user_auto_delete.get('privileges', ['user'])
    if isinstance(roles, str):
        roles = [roles]
    if not isinstance(roles, list):
        logmessage("Error in configuration for user auto delete")
        return
    search_roles = set()
    for item in roles:
        if not isinstance(item, str):
            logmessage("Error in configuration for user auto delete: invalid privilege")
            return
        if item not in role_ids:
            logmessage("Error in configuration for user auto delete: unknown privilege" + repr(item))
            return
        if item == 'cron':
            logmessage("Error in configuration for user auto delete: invalid privilege")
            return
        search_roles.add(role_ids[item])
    filters = []
    for item in search_roles:
        filters.append(UserRoles.role_id == item)
    cutoff_date = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - dateutil.relativedelta.relativedelta(days=cutoff_days)
    default_date = datetime.datetime(2020, 2, 24, 0, 0)
    candidates = []
    for item in db.session.execute(select(UserModel.id, UserModel.last_login).join(UserRoles, UserModel.id == UserRoles.user_id).where(or_(*filters))).all():
        if item.last_login is None:
            the_date = default_date
        else:
            the_date = item.last_login
        if the_date < cutoff_date:
            candidates.append(item.id)
    for user_id in candidates:
        last_interview = db.session.execute(select(UserDictKeys.user_id, db.func.max(UserDict.modtime).label('last_activity')).join(UserDict, and_(UserDictKeys.filename == UserDict.filename, UserDictKeys.key == UserDict.key)).where(UserDictKeys.user_id == user_id).group_by(UserDictKeys.user_id)).first()
        if last_interview is not None and last_interview.last_activity > cutoff_date:
            continue
        logmessage(f"delete_inactive_users: deleting {user_id:d}")
        user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=delete_shared, admin=True)
        delete_user_data(user_id, r, r_user)


def clear_old_interviews():
    # logmessage("clear_old_interviews: starting")
    try:
        interview_delete_days = int(daconfig.get('interview delete days', 90))
    except:
        logmessage("Error in configuration for interview delete days")
        interview_delete_days = 0
    days_by_filename = {}
    if 'interview delete days by filename' in daconfig:
        try:
            for filename, days in daconfig['interview delete days by filename'].items():
                assert isinstance(filename, str)
                days_by_filename[filename] = int(days)
        except:
            logmessage("Error in configuration for interview delete days by filename")
    nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    # logmessage("clear_old_interviews: days is " + str(interview_delete_days))
    for filename, days in days_by_filename.items():
        last_index = -1
        if days == 0:
            continue
        while True:
            subq = select(UserDict.key, UserDict.filename, db.func.max(UserDict.indexno).label('indexno')).where(UserDict.indexno > last_index, UserDict.filename == filename).group_by(UserDict.filename, UserDict.key).subquery()
            results = db.session.execute(select(UserDict.indexno, UserDict.key, UserDict.filename, UserDict.modtime).join(subq, and_(subq.c.indexno == UserDict.indexno)).order_by(UserDict.indexno).limit(1000))
            stale = []
            results_count = 0
            for record in results:
                results_count += 1
                last_index = record.indexno
                delta = nowtime - record.modtime
                # logmessage("clear_old_interviews: delta days is " + str(delta.days))
                if delta.days > days:
                    stale.append({'key': record.key, 'filename': record.filename})
            if results_count == 0:
                break
            for item in stale:
                obtain_lock_patiently(item['key'], item['filename'])
                reset_user_dict(item['key'], item['filename'], force=True)
                release_lock(item['key'], item['filename'])
                time.sleep(0.15)
            time.sleep(0.6)
    if interview_delete_days == 0:
        return
    last_index = -1
    while True:
        subq = select(UserDict.key, UserDict.filename, db.func.max(UserDict.indexno).label('indexno')).where(UserDict.indexno > last_index, UserDict.filename.notin_(days_by_filename.keys())).group_by(UserDict.filename, UserDict.key).subquery()
        results = db.session.execute(select(UserDict.indexno, UserDict.key, UserDict.filename, UserDict.modtime).join(subq, and_(subq.c.indexno == UserDict.indexno)).order_by(UserDict.indexno).limit(1000))
        stale = []
        results_count = 0
        for record in results:
            results_count += 1
            last_index = record.indexno
            delta = nowtime - record.modtime
            # logmessage("clear_old_interviews: delta days is " + str(delta.days))
            if delta.days > interview_delete_days:
                stale.append({'key': record.key, 'filename': record.filename})
        if results_count == 0:
            break
        for item in stale:
            obtain_lock_patiently(item['key'], item['filename'])
            reset_user_dict(item['key'], item['filename'], force=True)
            release_lock(item['key'], item['filename'])
            time.sleep(0.15)
        time.sleep(0.6)


def run_cron(the_cron_type):
    cron_types = [the_cron_type]
    if not re.search(r'_background$', the_cron_type):
        cron_types.append(str(the_cron_type) + "_background")
    cron_user = get_cron_user()
    cron_user_id = cron_user.id
    user_info = {'is_anonymous': False, 'is_authenticated': True, 'email': cron_user.email, 'theid': cron_user_id, 'the_user_id': cron_user_id, 'roles': [role.name for role in cron_user.roles], 'firstname': cron_user.first_name, 'lastname': cron_user.last_name, 'nickname': cron_user.nickname, 'country': cron_user.country, 'subdivisionfirst': cron_user.subdivisionfirst, 'subdivisionsecond': cron_user.subdivisionsecond, 'subdivisionthird': cron_user.subdivisionthird, 'organization': cron_user.organization, 'location': None, 'session_uid': 'cron', 'device_id': 'cron'}
    base_url = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    path_url = base_url + 'interview'
    with current_app.test_request_context(base_url=base_url, path=path_url):
        current_app.preprocess_request()
        login_user(cron_user, remember=False)
        filenames = []
        for filename in get_filenames():
            try:
                interview = get_interview(filename)
            except:
                continue
            found = False
            for cron_type_to_use in cron_types:
                if cron_type_to_use in interview.questions:
                    found = True
            if found:
                filenames.append(filename)
        for filename in filenames:
            try:
                interview = get_interview(filename)
            except:
                continue
            last_index = -1
            while True:
                records = get_records(filename, last_index)
                if len(records) == 0:
                    break
                for indexno, key, the_filename, dictionary, steps in records:
                    with global_context(empty_globals()):
                        this_thread.current_info = {'user': user_info, 'session': key, 'secret': None, 'yaml_filename': the_filename, 'url': base_url, 'url_root': path_url, 'encrypted': False, 'action': None, 'interface': 'cron', 'arguments': {}}
                        last_index = indexno
                        try:
                            the_dict = unpack_dictionary(dictionary)
                        except:
                            continue
                        if not the_dict.get('allow_cron', False):
                            continue
                        for cron_type_to_use in cron_types:
                            if cron_type_to_use not in interview.questions:
                                continue
                            if re.search(r'_background$', cron_type_to_use):
                                celery_app.signature('tasks.background_action', args=[the_filename, user_info, key, None, None, None, {'action': cron_type_to_use, 'arguments': {}}]).delay()
                            else:
                                try:
                                    # reset_local_variables()
                                    with global_context(empty_globals()), user_dict_context(the_dict):
                                        ci = {'user': user_info, 'session': key, 'secret': None, 'yaml_filename': the_filename, 'url': base_url, 'url_root': path_url, 'encrypted': False, 'action': cron_type_to_use, 'interface': 'cron', 'arguments': {}}
                                        this_thread.current_info = ci
                                        interview_status = InterviewStatus(current_info=ci)
                                        obtain_lock_patiently(key, the_filename)
                                        interview.assemble(the_dict, interview_status)
                                        save_status = this_thread.misc.get('save_status', SS_NEW)
                                        if interview_status.question.question_type in ["restart", "exit", "exit_logout"]:
                                            reset_user_dict(key, the_filename, force=True)
                                        if interview_status.question.question_type in ["restart", "exit", "logout", "exit_logout", "new_session"]:
                                            if save_status != SS_IGNORE:
                                                release_lock(key, the_filename)
                                            interview_status.do_sleep()
                                        elif interview_status.question.question_type == "backgroundresponseaction":
                                            new_action = interview_status.question.action
                                            interview_status = InterviewStatus(current_info={'user': user_info, 'session': key, 'secret': None, 'yaml_filename': the_filename, 'url': None, 'url_root': None, 'encrypted': False, 'action': new_action['action'], 'arguments': new_action['arguments'], 'interface': 'cron'})
                                            try:
                                                interview.assemble(the_dict, interview_status)
                                            except:
                                                pass
                                            save_status = this_thread.misc.get('save_status', SS_NEW)
                                            if save_status != SS_IGNORE:
                                                save_user_dict(key, the_dict, the_filename, encrypt=False, manual_user_id=cron_user_id, steps=steps, max_indexno=indexno)
                                                release_lock(key, the_filename)
                                            interview_status.do_sleep()
                                        elif interview_status.question.question_type == "response" and interview_status.question_text == 'null':
                                            if save_status != SS_IGNORE:
                                                release_lock(key, the_filename)
                                            interview_status.do_sleep()
                                        else:
                                            if save_status != SS_IGNORE:
                                                save_user_dict(key, the_dict, the_filename, encrypt=False, manual_user_id=cron_user_id, steps=steps, max_indexno=indexno)
                                                release_lock(key, the_filename)
                                            interview_status.do_sleep()
                                            if interview_status.question.question_type == "response":
                                                if hasattr(interview_status.question, 'all_variables'):
                                                    if hasattr(interview_status.question, 'include_internal'):
                                                        include_internal = interview_status.question.include_internal
                                                    else:
                                                        include_internal = False
                                                    sys.stdout.write(dict_as_json(the_dict, include_internal=include_internal).encode('utf8') + "\n")
                                                elif not hasattr(interview_status.question, 'binaryresponse'):
                                                    if interview_status.question_text != 'Empty Response':
                                                        try:
                                                            sys.stdout.write(interview_status.question_text.rstrip() + "\n")
                                                        except:
                                                            sys.stdout.write("Unable to write output to standard error\n")
                                except BaseException as err:
                                    if save_status != SS_IGNORE:
                                        release_lock(key, the_filename)
                                    logmessage("Cron error: " + str(key) + " " + str(the_filename) + " " + str(err.__class__.__name__) + ": " + str(err))
                                    if hasattr(err, 'traceback'):
                                        error_trace = str(err.traceback)
                                        if hasattr(err, 'da_line_with_error'):
                                            error_trace += "\nIn line: " + str(err.da_line_with_error)
                                    else:
                                        error_trace = None
                                    error_notification(err, trace=error_trace)
                                    continue
                time.sleep(0.4)

@cron_bp.cli.command('run')
@click.argument('task')
def cli_cron_run(task=None):
    set_request_active(False)
    if task == 'cron_daily':
        clear_old_interviews()
        delete_inactive_users()
    run_cron(task)
