import pickle
from sqlalchemy import select, and_
from docassemble.base.error import DAError
from docassemble.base.functions import phone_number_in_e164, get_current_info
from docassemble.base.generate_key import random_string
from docassemble.webapp.config import default_yaml_filename
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.interview.common import get_unique_name
from docassemble.webapp.twilio.helpers import twilio_config
from docassemble.webapp.users.models import TempUser, UserModel
from docassemble.webapp.users.views import load_user
from docassemble.webapp.utils.fixpickle import fix_pickle_obj
from docassemble.webapp.utils.logger import logmessage

@hookimpl
def get_sms_session(phone_number, config):
    sess_info = None
    if twilio_config is None:
        raise DAError("get_sms_session: Twilio not enabled")
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    phone_number = phone_number_in_e164(phone_number)
    if phone_number is None:
        raise DAError("terminate_sms_session: phone_number " + str(phone_number) + " is invalid")
    sess_contents = r.get('da:sms:client:' + phone_number + ':server:' + tconfig['number'])
    if sess_contents is not None:
        try:
            sess_info = fix_pickle_obj(sess_contents)
        except:
            logmessage("get_sms_session: unable to decode session information")
    sess_info['email'] = None
    if 'user_id' in sess_info and sess_info['user_id'] is not None:
        user = load_user(sess_info['user_id'])
        if user is not None:
            sess_info['email'] = user.email
    return sess_info


@hookimpl
def initiate_sms_session(phone_number, yaml_filename, uid, secret, encrypted, user_id, email, new, config):
    phone_number = phone_number_in_e164(phone_number)
    if phone_number is None:
        raise DAError("initiate_sms_session: phone_number " + str(phone_number) + " is invalid")
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    the_current_info = get_current_info()
    if yaml_filename is None:
        yaml_filename = the_current_info.get('yaml_filename', None)
        if yaml_filename is None:
            yaml_filename = default_yaml_filename
    temp_user_id = None
    if user_id is None and email is not None:
        user = db.session.execute(select(UserModel).where(and_(UserModel.email.ilike(email), UserModel.active == True))).scalar()  # noqa: E712 # pylint: disable=singleton-comparison
        if user is not None:
            user_id = user.id
    if user_id is None:
        if not new:
            if 'user' in the_current_info:
                if 'theid' in the_current_info['user']:
                    if the_current_info['user'].get('is_authenticated', False):
                        user_id = the_current_info['user']['theid']
                    else:
                        temp_user_id = the_current_info['user']['theid']
        if user_id is None and temp_user_id is None:
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            temp_user_id = new_temp_user.id
    if secret is None:
        if not new:
            secret = the_current_info['secret']
        if secret is None:
            secret = random_string(16)
    if uid is None:
        if new:
            uid = get_unique_name(yaml_filename, secret)
        else:
            uid = the_current_info.get('session', None)
            if uid is None:
                uid = get_unique_name(yaml_filename, secret)
    if encrypted is None:
        if new:
            encrypted = True
        else:
            encrypted = the_current_info['encrypted']
    sess_info = {'yaml_filename': yaml_filename, 'uid': uid, 'secret': secret, 'number': phone_number, 'encrypted': encrypted, 'tempuser': temp_user_id, 'user_id': user_id}
    # logmessage("initiate_sms_session: setting da:sms:client:" + phone_number + ':server:' + tconfig['number'] + " to " + str(sess_info))
    r.set('da:sms:client:' + phone_number + ':server:' + tconfig['number'], pickle.dumps(sess_info))
    return True


@hookimpl
def terminate_sms_session(phone_number, config):
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    phone_number = phone_number_in_e164(phone_number)
    r.delete('da:sms:client:' + phone_number + ':server:' + tconfig['number'])
