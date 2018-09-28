import sys
import copy
import datetime
import re
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
from docassemble.webapp.server import UserModel, UserDict, logmessage, unpack_dictionary, db, set_request_active, fetch_user_dict, save_user_dict, fresh_dictionary, reset_user_dict, obtain_lock, release_lock, app, login_user, get_user_object, error_notification
import docassemble.webapp.backend
import docassemble.base.interview_cache
import docassemble.base.parse
import docassemble.base.util
import docassemble.base.functions
import cPickle as pickle
import codecs
from sqlalchemy import or_, and_
#import docassemble.webapp.worker

set_request_active(False)

def get_cron_user():
    for user in UserModel.query.all():
        for role in user.roles:
            if role.name == 'cron':
                return(user)
    sys.exit("Cron user not found")

def clear_old_interviews():
    #sys.stderr.write("clear_old_interviews: starting\n")
    interview_delete_days = docassemble.base.config.daconfig.get('interview delete days', 90)
    if interview_delete_days == 0:
        return
    stale = list()
    nowtime = datetime.datetime.utcnow()
    #sys.stderr.write("clear_old_interviews: days is " + str(interview_delete_days) + "\n")
    subq = db.session.query(UserDict.key, UserDict.filename, db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('count')).group_by(UserDict.filename, UserDict.key).subquery()
    results = db.session.query(UserDict.key, UserDict.filename, UserDict.modtime, subq.c.count).join(subq, and_(subq.c.indexno == UserDict.indexno, subq.c.key == UserDict.key, subq.c.filename == UserDict.filename)).order_by(UserDict.indexno)
    for record in results:
        delta = nowtime - record.modtime
        #sys.stderr.write("clear_old_interviews: delta days is " + str(delta.days) + "\n")
        if delta.days > interview_delete_days:
            stale.append(dict(key=record.key, filename=record.filename))
    for item in stale:
        obtain_lock(item['key'], item['filename'])
        reset_user_dict(item['key'], item['filename'], force=True)
        release_lock(item['key'], item['filename'])
    
def run_cron(cron_type):
    cron_types = [cron_type]
    if not re.search(r'_background$', cron_type):
        cron_types.append(str(cron_type) + "_background")
    cron_user = get_cron_user()
    user_info = dict(is_anonymous=False, is_authenticated=True, email=cron_user.email, theid=cron_user.id, the_user_id=cron_user.id, roles=[role.name for role in cron_user.roles], firstname=cron_user.first_name, lastname=cron_user.last_name, nickname=cron_user.nickname, country=cron_user.country, subdivisionfirst=cron_user.subdivisionfirst, subdivisionsecond=cron_user.subdivisionsecond, subdivisionthird=cron_user.subdivisionthird, organization=cron_user.organization, location=None)
    #sys.stderr.write("cron_user id is " + str(cron_user.id) + ".\n")
    to_do = list()
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('count')).group_by(UserDict.filename, UserDict.key).filter(UserDict.encrypted == False).subquery()
    results = db.session.query(UserDict.dictionary, UserDict.key, UserDict.user_id, UserDict.filename, UserDict.modtime, subq.c.count).join(subq, subq.c.indexno == UserDict.indexno).order_by(UserDict.indexno)
    for record in results:
        #sys.stderr.write("Trying " + str(record.key) + " for " + str(record.filename) + "\n")
        try:
            the_dict = unpack_dictionary(record.dictionary)
        except:
            continue
        if 'allow_cron' in the_dict:
            if the_dict['allow_cron']:
                to_do.append(dict(key=record.key, user_id=record.user_id, filename=record.filename))
    with app.app_context():
        with app.test_request_context():
            login_user(cron_user, remember=False)
            for item in to_do:
                # sys.stderr.write("Doing " + str(item['key']) + " for " + str(item['filename']) + "\n")
                try:
                    #sys.stderr.write("  " + str(cron_type) + " get interview\n")
                    interview = docassemble.base.interview_cache.get_interview(item['filename'])
                except:
                    continue
                for cron_type_to_use in cron_types:
                    if cron_type_to_use not in interview.questions:
                        continue
                    if re.search(r'_background$', cron_type_to_use):
                        #sys.stderr.write("  Spawning bg task: " + str(cron_type_to_use) + "\n")
                        new_task = docassemble.webapp.worker.background_action.delay(item['filename'], user_info, item['key'], None, None, None, {'action': cron_type_to_use, 'arguments': dict()})
                    else:
                        try:
                            # sys.stderr.write("  " + str(cron_type_to_use) + " status\n")
                            docassemble.base.functions.reset_local_variables()
                            obtain_lock(item['key'], item['filename'])
                            steps, user_dict, is_encrypted = fetch_user_dict(item['key'], item['filename'])
                            interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=dict(is_anonymous=False, is_authenticated=True, email=cron_user.email, theid=cron_user.id, the_user_id=cron_user.id, roles=[role.name for role in cron_user.roles], firstname=cron_user.first_name, lastname=cron_user.last_name, nickname=cron_user.nickname, country=cron_user.country, subdivisionfirst=cron_user.subdivisionfirst, subdivisionsecond=cron_user.subdivisionsecond, subdivisionthird=cron_user.subdivisionthird, organization=cron_user.organization, location=None, session_uid='cron'), session=item['key'], secret=None, yaml_filename=item['filename'], url=None, url_root=None, encrypted=is_encrypted, action=cron_type_to_use, interface='cron', arguments=dict()))
                            # sys.stderr.write("  " + str(cron_type_to_use) + " fetch\n")
                            # sys.stderr.write("  " + str(cron_type_to_use) + " assemble\n")
                            interview.assemble(user_dict, interview_status)
                            # sys.stderr.write("  " + str(cron_type_to_use) + " save\n")
                            if interview_status.question.question_type in ["restart", "exit", "exit_logout"]:
                                #sys.stderr.write("  Deleting dictionary\n")
                                reset_user_dict(item['key'], item['filename'], force=True)
                            if interview_status.question.question_type in ["restart", "exit", "logout", "exit_logout", "new_session"]:
                                release_lock(item['key'], item['filename'])
                                #sys.stderr.write("  Deleted dictionary\n")
                            elif interview_status.question.question_type in ["backgroundresponseaction"]:
                                #sys.stderr.write("  Got background response action\n")
                                new_action = interview_status.question.action
                                interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=user_info, session=item['key'], secret=None, yaml_filename=item['filename'], url=None, url_root=None, encrypted=is_encrypted, action=new_action['action'], arguments=new_action['arguments'], interface='cron'))
                                try:
                                    interview.assemble(user_dict, interview_status)
                                    #sys.stderr.write("Assembled 2 ok\n")
                                except:
                                    #sys.stderr.write("Assembled 2 not ok\n")
                                    pass
                                save_user_dict(item['key'], user_dict, item['filename'], encrypt=False, manual_user_id=cron_user.id, steps=steps)
                                release_lock(item['key'], item['filename'])
                            else:
                                # sys.stderr.write("  Saving where type is " + str(cron_type_to_use) + "\n")
                                save_user_dict(item['key'], user_dict, item['filename'], encrypt=False, manual_user_id=cron_user.id, steps=steps)
                                release_lock(item['key'], item['filename'])
                                if interview_status.question.question_type == "response":
                                    if hasattr(interview_status.question, 'all_variables'):
                                        if hasattr(interview_status.question, 'include_internal'):
                                            include_internal = interview_status.question.include_internal
                                        else:
                                            include_internal = False
                                        sys.stdout.write(docassemble.webapp.backend.dict_as_json(user_dict, include_internal=include_internal).encode('utf8') + "\n")
                                    elif not hasattr(interview_status.question, 'binaryresponse'):
                                        sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
                        except Exception as err:
                            sys.stderr.write(str(err.__class__.__name__) + ": " + str(err) + "\n")
                            release_lock(item['key'], item['filename'])
                            if hasattr(err, 'traceback'):
                                error_trace = unicode(err.traceback)
                                if hasattr(err, 'da_line_with_error'):
                                    error_trace += "\nIn line: " + unicode(err.da_line_with_error)
                            else:
                                error_trace = None
                            error_notification(err, trace=error_trace)
                            continue
            
if __name__ == "__main__":
    with app.app_context():
        if cron_type == 'cron_daily':
            clear_old_interviews()
        run_cron(cron_type)
        db.engine.dispose()
    sys.exit(0)

