import sys
import copy
import datetime
import dateutil
import re
import time
if __name__ == "__main__":
    cron_type = 'cron_daily'
    arguments = copy.deepcopy(sys.argv)
    remaining_arguments = list()
    while len(arguments):
        if arguments[0] == '-type' and len(arguments) > 1:
            arguments.pop(0)
            cron_type = arguments.pop(0)
            continue
        remaining_arguments.append(arguments.pop(0))
    import docassemble.base.config
    docassemble.base.config.load(arguments=remaining_arguments)
from docassemble.webapp.server import UserModel, UserDict, UserDictKeys, Role, logmessage, unpack_dictionary, db, set_request_active, fetch_user_dict, save_user_dict, fresh_dictionary, reset_user_dict, obtain_lock_patiently, release_lock, app, login_user, get_user_object, error_notification, user_interviews
from docassemble.webapp.users.models import UserRoles
import docassemble.webapp.backend
import docassemble.base.interview_cache
import docassemble.base.parse
import docassemble.base.util
import docassemble.base.functions
import pickle
import codecs
from sqlalchemy import or_, and_
from docassemble.webapp.daredis import r, r_user

set_request_active(False)

def get_filenames():
    results = list()
    for record in db.session.query(UserDict.filename).filter(UserDict.encrypted == False).group_by(UserDict.filename):
        results.append(record.filename)
    return results

def get_records(filename, last_index):
    subq = db.session.query(UserDict.key, UserDict.filename, db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('count')).group_by(UserDict.filename, UserDict.key).filter(UserDict.filename == filename, UserDict.encrypted == False, UserDict.indexno > last_index).subquery()
    results = list()
    for record in db.session.query(UserDict.key, UserDict.filename, UserDict.dictionary, subq.c.indexno, subq.c.count).join(subq, and_(subq.c.indexno == UserDict.indexno)).order_by(UserDict.indexno).limit(200):
        results.append((record.indexno, record.key, record.filename, record.dictionary, record.count))
    return results

def get_cron_user():
    for user in UserModel.query.options(db.joinedload('roles')).all():
        for role in user.roles:
            if role.name == 'cron':
                return(user)
    sys.exit("Cron user not found")

def delete_inactive_users():
    user_auto_delete = docassemble.base.config.daconfig.get('user auto delete', dict())
    if not isinstance(user_auto_delete, dict):
        sys.stderr.write("Error in configuration for user auto delete\n")
        return
    if not user_auto_delete.get('enable', True):
        return
    try:
        cutoff_days = int(user_auto_delete.get('inactive days', 0))
        assert cutoff_days >= 0
    except:
        sys.stderr.write("Error in configuration for user auto delete\n")
        return
    if cutoff_days == 0:
        return
    delete_shared = True if user_auto_delete.get('delete shared', False) else False
    role_ids = dict()
    for item in Role.query.all():
        role_ids[item.name] = item.id
    roles = user_auto_delete.get('privileges', ['user'])
    if isinstance(roles, str):
        roles = [roles]
    if not isinstance(roles, list):
        sys.stderr.write("Error in configuration for user auto delete\n")
        return
    search_roles = set()
    for item in roles:
        if not isinstance(item, str):
            sys.stderr.write("Error in configuration for user auto delete: invalid privilege\n")
            return
        if item not in role_ids:
            sys.stderr.write("Error in configuration for user auto delete: unknown privilege" + repr(item) + "\n")
            return
        if item == 'cron':
            sys.stderr.write("Error in configuration for user auto delete: invalid privilege\n")
            return
        search_roles.add(role_ids[item])
    filters = list()
    for item in search_roles:
        filters.append(UserRoles.role_id == item)
    cutoff_date = datetime.datetime.utcnow() - dateutil.relativedelta.relativedelta(days=cutoff_days)
    default_date = datetime.datetime(2020, 2, 24, 0, 0)
    candidates = list()
    for item in db.session.query(UserModel.id, UserModel.last_login).join(UserRoles, UserModel.id == UserRoles.user_id).filter(or_(*filters)).all():
        if item.last_login is None:
            the_date = default_date
        else:
            the_date = item.last_login
        if the_date < cutoff_date:
            candidates.append(item.id)
    for user_id in candidates:
        last_interview = db.session.query(UserDictKeys.user_id, db.func.max(UserDict.modtime).label('last_activity')).join(UserDict, and_(UserDictKeys.filename == UserDict.filename, UserDictKeys.key == UserDict.key)).filter(UserDictKeys.user_id == user_id).group_by(UserDictKeys.user_id).first()
        if last_interview is not None and last_interview.last_activity > cutoff_date:
            continue
        sys.stderr.write("delete_inactive_users: deleting %d\n" % (user_id,))
        user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=delete_shared, admin=True)
        docassemble.webapp.backend.delete_user_data(user_id, r, r_user)

def clear_old_interviews():
    #sys.stderr.write("clear_old_interviews: starting\n")
    try:
        interview_delete_days = int(docassemble.base.config.daconfig.get('interview delete days', 90))
    except:
        sys.stderr.write("Error in configuration for interview delete days\n")
        interview_delete_days = 0
    days_by_filename = dict()
    if 'interview delete days by filename' in docassemble.base.config.daconfig:
        try:
            for filename, days in docassemble.base.config.daconfig['interview delete days by filename'].items():
                assert isinstance(filename, str)
                days_by_filename[filename] = int(days)
        except:
            sys.stderr.write("Error in configuration for interview delete days by filename\n")
    nowtime = datetime.datetime.utcnow()
    #sys.stderr.write("clear_old_interviews: days is " + str(interview_delete_days) + "\n")
    for filename, days in days_by_filename.items():
        last_index = -1
        while True:
            subq = db.session.query(UserDict.key, UserDict.filename, db.func.max(UserDict.indexno).label('indexno')).filter(UserDict.indexno > last_index, UserDict.filename == filename).group_by(UserDict.filename, UserDict.key).subquery()
            results = db.session.query(UserDict.indexno, UserDict.key, UserDict.filename, UserDict.modtime).join(subq, and_(subq.c.indexno == UserDict.indexno)).order_by(UserDict.indexno).limit(1000)
            if results.count() == 0:
                break
            stale = list()
            for record in results:
                last_index = record.indexno
                delta = nowtime - record.modtime
                #sys.stderr.write("clear_old_interviews: delta days is " + str(delta.days) + "\n")
                if delta.days > days:
                    stale.append(dict(key=record.key, filename=record.filename))
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
        subq = db.session.query(UserDict.key, UserDict.filename, db.func.max(UserDict.indexno).label('indexno')).filter(UserDict.indexno > last_index, UserDict.filename.notin_(days_by_filename.keys())).group_by(UserDict.filename, UserDict.key).subquery()
        results = db.session.query(UserDict.indexno, UserDict.key, UserDict.filename, UserDict.modtime).join(subq, and_(subq.c.indexno == UserDict.indexno)).order_by(UserDict.indexno).limit(1000)
        if results.count() == 0:
            break
        stale = list()
        for record in results:
            last_index = record.indexno
            delta = nowtime - record.modtime
            #sys.stderr.write("clear_old_interviews: delta days is " + str(delta.days) + "\n")
            if delta.days > interview_delete_days:
                stale.append(dict(key=record.key, filename=record.filename))
        for item in stale:
            obtain_lock_patiently(item['key'], item['filename'])
            reset_user_dict(item['key'], item['filename'], force=True)
            release_lock(item['key'], item['filename'])
            time.sleep(0.15)
        time.sleep(0.6)

def run_cron(cron_type):
    cron_types = [cron_type]
    if not re.search(r'_background$', cron_type):
        cron_types.append(str(cron_type) + "_background")
    cron_user = get_cron_user()
    cron_user_id = cron_user.id
    user_info = dict(is_anonymous=False, is_authenticated=True, email=cron_user.email, theid=cron_user_id, the_user_id=cron_user_id, roles=[role.name for role in cron_user.roles], firstname=cron_user.first_name, lastname=cron_user.last_name, nickname=cron_user.nickname, country=cron_user.country, subdivisionfirst=cron_user.subdivisionfirst, subdivisionsecond=cron_user.subdivisionsecond, subdivisionthird=cron_user.subdivisionthird, organization=cron_user.organization, location=None, session_uid='cron', device_id='cron')
    base_url = docassemble.base.config.daconfig.get('url root', 'http://localhost') + docassemble.base.config.daconfig.get('root', '/')
    path_url = base_url + 'interview'
    with app.app_context():
        with app.test_request_context(base_url=base_url, path=path_url):
            login_user(cron_user, remember=False)
            filenames = list()
            for filename in get_filenames():
                try:
                    interview = docassemble.base.interview_cache.get_interview(filename)
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
                    interview = docassemble.base.interview_cache.get_interview(filename)
                except:
                    continue
                last_index = -1
                while True:
                    records = get_records(filename, last_index)
                    if len(records) == 0:
                        break
                    to_do = list()
                    for indexno, key, filename, dictionary, steps in records:
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
                                new_task = docassemble.webapp.worker.background_action.delay(filename, user_info, key, None, None, None, {'action': cron_type_to_use, 'arguments': dict()})
                            else:
                                try:
                                    docassemble.base.functions.reset_local_variables()
                                    obtain_lock_patiently(key, filename)
                                    interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=dict(is_anonymous=False, is_authenticated=True, email=cron_user.email, theid=cron_user_id, the_user_id=cron_user_id, roles=[role.name for role in cron_user.roles], firstname=cron_user.first_name, lastname=cron_user.last_name, nickname=cron_user.nickname, country=cron_user.country, subdivisionfirst=cron_user.subdivisionfirst, subdivisionsecond=cron_user.subdivisionsecond, subdivisionthird=cron_user.subdivisionthird, organization=cron_user.organization, location=None, session_uid='cron', device_id='cron'), session=key, secret=None, yaml_filename=filename, url=None, url_root=None, encrypted=False, action=cron_type_to_use, interface='cron', arguments=dict()))
                                    interview.assemble(the_dict, interview_status)
                                    save_status = docassemble.base.functions.this_thread.misc.get('save_status', 'new')
                                    if interview_status.question.question_type in ["restart", "exit", "exit_logout"]:
                                        reset_user_dict(key, filename, force=True)
                                    if interview_status.question.question_type in ["restart", "exit", "logout", "exit_logout", "new_session"]:
                                        release_lock(key, filename)
                                        interview_status.do_sleep()
                                    elif interview_status.question.question_type == "backgroundresponseaction":
                                        new_action = interview_status.question.action
                                        interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=key, secret=None, yaml_filename=filename, url=None, url_root=None, encrypted=False, action=new_action['action'], arguments=new_action['arguments'], interface='cron'))
                                        try:
                                            interview.assemble(the_dict, interview_status)
                                        except:
                                            pass
                                        save_status = docassemble.base.functions.this_thread.misc.get('save_status', 'new')
                                        if save_status != 'ignore':
                                            save_user_dict(key, the_dict, filename, encrypt=False, manual_user_id=cron_user_id, steps=steps, max_indexno=indexno)
                                        release_lock(key, filename)
                                        interview_status.do_sleep()
                                    elif interview_status.question.question_type == "response" and interview_status.questionText == 'null':
                                        release_lock(key, filename)
                                        interview_status.do_sleep()
                                    else:
                                        if save_status != 'ignore':
                                            save_user_dict(key, the_dict, filename, encrypt=False, manual_user_id=cron_user_id, steps=steps, max_indexno=indexno)
                                        release_lock(key, filename)
                                        interview_status.do_sleep()
                                        if interview_status.question.question_type == "response":
                                            if hasattr(interview_status.question, 'all_variables'):
                                                if hasattr(interview_status.question, 'include_internal'):
                                                    include_internal = interview_status.question.include_internal
                                                else:
                                                    include_internal = False
                                                sys.stdout.write(docassemble.webapp.backend.dict_as_json(the_dict, include_internal=include_internal).encode('utf8') + "\n")
                                            elif not hasattr(interview_status.question, 'binaryresponse'):
                                                if interview_status.questionText != 'Empty Response':
                                                    try:
                                                        sys.stdout.write(interview_status.questionText.rstrip() + "\n")
                                                    except:
                                                        sys.stdout.write("Unable to write output to standard error\n")
                                except Exception as err:
                                    release_lock(key, filename)
                                    sys.stderr.write("Cron error: " + str(key) + " " + str(filename) + " " + str(err.__class__.__name__) + ": " + str(err) + "\n")
                                    if hasattr(err, 'traceback'):
                                        error_trace = str(err.traceback)
                                        if hasattr(err, 'da_line_with_error'):
                                            error_trace += "\nIn line: " + str(err.da_line_with_error)
                                    else:
                                        error_trace = None
                                    error_notification(err, trace=error_trace)
                                    continue
                    time.sleep(0.4)

if __name__ == "__main__":
    with app.app_context():
        if cron_type == 'cron_daily':
            clear_old_interviews()
            delete_inactive_users()
        run_cron(cron_type)
        db.engine.dispose()
    sys.exit(0)
