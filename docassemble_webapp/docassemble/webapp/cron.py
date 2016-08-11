import sys
import copy
import datetime
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
from docassemble.webapp.server import User, UserDict, logmessage, unpack_dictionary, db, set_request_active, fetch_user_dict, save_user_dict, fresh_dictionary, reset_user_dict, app
import docassemble.base.interview_cache
import docassemble.base.parse
import docassemble.base.util
import os
import pickle
import codecs

set_request_active(False)

def get_cron_user():
    for user in User.query.all():
        for role in user.roles:
            if role.name == 'cron':
                return(user)
    sys.exit("Cron user not found")

def clear_old_interviews():
    interview_delete_days = docassemble.base.config.daconfig.get('interview_delete_days', 90)
    if interview_delete_days == 0:
        return
    stale = list()
    nowtime = datetime.datetime.utcnow()
    #sys.stderr.write("days is " + str(interview_delete_days) + "\n")
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('count')).group_by(UserDict.filename, UserDict.key).subquery()
    results = db.session.query(UserDict.dictionary, UserDict.key, UserDict.user_id, UserDict.filename, UserDict.modtime, subq.c.count).join(subq, subq.c.indexno == UserDict.indexno).order_by(UserDict.indexno)
    for record in results:
        delta = nowtime - record.modtime
        #sys.stderr.write("delta days is " + str(delta.days) + "\n")
        if delta.days > interview_delete_days:
            stale.append(dict(key=record.key, filename=record.filename))
    for item in stale:
        reset_user_dict(item['key'], item['filename'])
    
def run_cron(cron_type):
    #sys.stderr.write("calling send_email\n")
    #sys.stderr.write(str(app.config['MAIL_SERVER']) + "\n")
    #docassemble.base.util.send_email(to="jhpyle@gmail.com", body="Asdf", html="<p>Asdf</p>")
    cron_user = get_cron_user()
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
    for item in to_do:
        #sys.stderr.write("Doing " + str(item['key']) + " for " + str(item['filename']) + "\n")
        try:
            #sys.stderr.write("  " + str(cron_type) + " get interview\n")
            interview = docassemble.base.interview_cache.get_interview(item['filename'])
        except:
            continue
        if cron_type not in interview.questions:
            #sys.stderr.write("  " + str(cron_type) + " not enabled in this interview\n")
            continue
        #sys.stderr.write("  " + str(cron_type) + " is enabled in this interview\n")
        try:
            #sys.stderr.write("  " + str(cron_type) + " status\n")
            interview_status = docassemble.base.parse.InterviewStatus(current_info=dict(user=dict(is_anonymous=False, is_authenticated=True, email=cron_user.email, theid=cron_user.id, roles=[role.name for role in cron_user.roles], firstname=cron_user.first_name, lastname=cron_user.last_name, nickname=cron_user.nickname, country=cron_user.country, subdivisionfirst=cron_user.subdivisionfirst, subdivisionsecond=cron_user.subdivisionsecond, subdivisionthird=cron_user.subdivisionthird, organization=cron_user.organization, locatiion=None), session=item['key'], yaml_filename=item['filename'], url='http://localhost', action=cron_type, arguments=dict()))
            #sys.stderr.write("  " + str(cron_type) + " fetch\n")
            steps, user_dict, is_encrypted = fetch_user_dict(item['key'], item['filename'])
            #sys.stderr.write("  " + str(cron_type) + " assemble\n")
            interview.assemble(user_dict, interview_status)
            #sys.stderr.write("  " + str(cron_type) + " save\n")
            if interview_status.question.question_type in ["restart", "exit"]:
                sys.stderr.write("  Deleting dictionary\n")
                reset_user_dict(item['key'], item['filename'])
                sys.stderr.write("  Deleted dictionary\n")
            else:
                #sys.stderr.write("  Saving where type is " + cron_type + "\n")
                save_user_dict(item['key'], user_dict, item['filename'], encrypt=False, manual_user_id=cron_user.id)
                if interview_status.question.question_type == "response":
                    if not hasattr(interview_status.question, 'binaryresponse'):
                        sys.stdout.write(interview_status.questionText.rstrip().encode('utf8') + "\n")
        except:
            continue
            
if __name__ == "__main__":
    if cron_type == 'cron_daily':
        clear_old_interviews()
    with app.app_context():
        run_cron(cron_type)
