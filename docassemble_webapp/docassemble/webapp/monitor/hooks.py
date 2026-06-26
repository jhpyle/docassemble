import re
import zoneinfo
from types import SimpleNamespace
from dateutil import tz
from sqlalchemy import select, delete, or_, and_
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.main.hooks import get_default_timezone
from docassemble.webapp.users.common import get_person
from docassemble.webapp.users.helpers import get_user_object
from docassemble.webapp.utils.helpers import nice_utc_date
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.utils.encryption import (
    decrypt_phrase,
    pack_phrase,
    encrypt_phrase,
    unpack_phrase
)
from .models import ChatLog

class ChatPartners(SimpleNamespace):
    pass

@hookimpl(specname="get_chat_log_internal")
def get_chat_log(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, self_temp_id):
    messages = []
    people = {}
    if user_id is not None:
        if get_person(user_id, people) is None:
            return []
        chat_person_type = 'auth'
        chat_person_id = user_id
    else:
        chat_person_type = 'anon'
        chat_person_id = temp_user_id
    if self_user_id is not None:
        if get_person(self_user_id, people) is None:
            return []
        self_person_type = 'auth'
        self_person_id = self_user_id
    else:
        self_person_type = 'anon'
        self_person_id = self_temp_id
    if chat_person_type == 'auth':
        if chat_mode in ('peer', 'peerhelp'):
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.owner_id == chat_person_id))).order_by(ChatLog.id)).scalars().all()  # noqa: E712 # pylint: disable=singleton-comparison
        else:
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.owner_id == chat_person_id)).order_by(ChatLog.id)).scalars().all()
        for record in records:
            if record.encrypted:
                try:
                    message = decrypt_phrase(record.message, secret)
                except:
                    logmessage("Could not decrypt phrase with secret " + secret)
                    continue
            else:
                message = unpack_phrase(record.message)
            modtime = nice_utc_date(record.modtime)
            if self_person_type == 'auth':
                is_self = bool(self_person_id == record.user_id)
            else:
                is_self = bool(self_person_id == record.temp_user_id)
            if record.user_id is not None:
                person = get_person(record.user_id, people)
                if person is None:
                    logmessage("Person " + str(record.user_id) + " did not exist")
                    continue
                role_list = [role.name for role in person.roles]
                if len(role_list) == 0:
                    role_list = ['user']
                messages.append({'id': record.id, 'is_self': is_self, 'temp_owner_id': record.temp_owner_id, 'temp_user_id': record.temp_user_id, 'owner_id': record.owner_id, 'user_id': record.user_id, 'first_name': person.first_name, 'last_name': person.last_name, 'email': person.email, 'modtime': modtime, 'message': message, 'roles': role_list})
            else:
                messages.append({'id': record.id, 'is_self': is_self, 'temp_owner_id': record.temp_owner_id, 'temp_user_id': record.temp_user_id, 'owner_id': record.owner_id, 'user_id': record.user_id, 'modtime': modtime, 'message': message, 'roles': ['user']})
    else:
        if chat_mode in ['peer', 'peerhelp']:
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.temp_owner_id == chat_person_id))).order_by(ChatLog.id)).scalars().all()  # noqa: E712 # pylint: disable=singleton-comparison
        else:
            records = db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.temp_owner_id == chat_person_id)).order_by(ChatLog.id)).scalars().all()
        for record in records:
            if record.encrypted:
                try:
                    message = decrypt_phrase(record.message, secret)
                except:
                    logmessage("Could not decrypt phrase with secret " + secret)
                    continue
            else:
                message = unpack_phrase(record.message)
            modtime = nice_utc_date(record.modtime)
            if self_person_type == 'auth':
                is_self = bool(self_person_id == record.user_id)
            else:
                # logmessage("self person id is " + str(self_person_id) + " and record user id is " + str(record.temp_user_id))
                is_self = bool(self_person_id == record.temp_user_id)
            if record.user_id is not None:
                person = get_person(record.user_id, people)
                if person is None:
                    logmessage("Person " + str(record.user_id) + " did not exist")
                    continue
                role_list = [role.name for role in person.roles]
                if len(role_list) == 0:
                    role_list = ['user']
                messages.append({'id': record.id, 'is_self': is_self, 'temp_owner_id': record.temp_owner_id, 'temp_user_id': record.temp_user_id, 'owner_id': record.owner_id, 'user_id': record.user_id, 'first_name': person.first_name, 'last_name': person.last_name, 'email': person.email, 'modtime': modtime, 'message': message, 'roles': role_list})
            else:
                messages.append({'id': record.id, 'is_self': is_self, 'temp_owner_id': record.temp_owner_id, 'temp_user_id': record.temp_user_id, 'owner_id': record.owner_id, 'user_id': record.user_id, 'modtime': modtime, 'message': message, 'roles': ['user']})
    return messages

@hookimpl
def get_current_chat_log(yaml_filename, session_id, secret, utc=True, timezone=None):
    if timezone is None:
        timezone = get_default_timezone()
    timezone = zoneinfo.ZoneInfo(timezone)
    output = []
    if yaml_filename is None or session_id is None:
        return output
    user_cache = {}
    for record in db.session.execute(select(ChatLog).where(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id)).order_by(ChatLog.id)).scalars():
        if record.encrypted:
            try:
                message = decrypt_phrase(record.message, secret)
            except:
                logmessage("get_current_chat_log: Could not decrypt phrase with secret " + secret)
                continue
        else:
            message = unpack_phrase(record.message)
        # if record.temp_owner_id:
        #     owner_first_name = None
        #     owner_last_name = None
        #     owner_email = None
        # elif record.owner_id in user_cache:
        #     owner_first_name = user_cache[record.owner_id].first_name
        #     owner_last_name = user_cache[record.owner_id].last_name
        #     owner_email = user_cache[record.owner_id].email
        # else:
        #     logmessage("get_current_chat_log: Invalid owner ID in chat log")
        #     continue
        if record.temp_user_id:
            user_first_name = None
            user_last_name = None
            user_email = None
        elif record.user_id in user_cache:
            user_first_name = user_cache[record.user_id].first_name
            user_last_name = user_cache[record.user_id].last_name
            user_email = user_cache[record.user_id].email
        else:
            new_user = get_user_object(record.user_id)
            if new_user is None:
                logmessage("get_current_chat_log: Invalid user ID in chat log")
                continue
            user_cache[record.user_id] = new_user
            user_first_name = user_cache[record.user_id].first_name
            user_last_name = user_cache[record.user_id].last_name
            user_email = user_cache[record.user_id].email
        if utc:
            the_datetime = record.modtime.replace(tzinfo=tz.tzutc())
        else:
            the_datetime = record.modtime.replace(tzinfo=tz.tzutc()).astimezone(timezone)
        output.append({'message': message, 'datetime': the_datetime, 'user_email': user_email, 'user_first_name': user_first_name, 'user_last_name': user_last_name})
    return output


@hookimpl
def chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles):
    key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    peer_ok = bool(mode in ('peer', 'peerhelp'))
    help_ok = bool(mode in ('help', 'peerhelp'))
    potential_partners = set()
    if help_ok and len(partner_roles) and not r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
        chat_session_key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        for role in partner_roles:
            for the_key in r.keys('da:monitor:role:' + role + ':userid:*'):
                user_id = re.sub(r'^.*:userid:', '', the_key.decode())
                potential_partners.add(user_id)
        for the_key in r.keys('da:monitor:chatpartners:*'):
            the_key = the_key.decode()
            user_id = re.sub(r'^.*chatpartners:', '', the_key)
            if user_id not in potential_partners:
                for chat_key in r.hgetall(the_key):
                    if chat_key.decode() == chat_session_key:
                        potential_partners.add(user_id)
    num_peer = 0
    if peer_ok:
        for sess_key in r.keys('da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
            if sess_key.decode() != key:
                num_peer += 1
    result = ChatPartners()
    result.peer = num_peer
    result.help = len(potential_partners)
    return result

@hookimpl
def get_ml_info(varname, default_package, default_file):
    parts = varname.split(':')
    if len(parts) == 3 and parts[0].startswith('docassemble.') and re.match(r'data/sources/.*\.json', parts[1]):
        the_package = parts[0]
        the_file = parts[1]
        the_varname = parts[2]
    elif len(parts) == 2 and parts[0] == 'global':
        the_package = '_global'
        the_file = '_global'
        the_varname = parts[1]
    elif len(parts) == 2 and (re.match(r'data/sources/.*\.json', parts[0]) or re.match(r'[^/]+\.json', parts[0])):
        the_package = default_package
        the_file = re.sub(r'^data/sources/', '', parts[0])
        the_varname = parts[1]
    elif len(parts) != 1:
        the_package = '_global'
        the_file = '_global'
        the_varname = varname
    else:
        the_package = default_package
        the_file = default_file
        the_varname = varname
    return (the_package, the_file, the_varname)


@hookimpl
def manage_chat_logs(mode, kwargs):
    if mode == 0:
        for chat_entry in db.session.execute(select(ChatLog).filter_by(temp_user_id=int(kwargs['temp_user_id'])).with_for_update()).scalars():
            chat_entry.user_id = kwargs['new_user_id']
            chat_entry.temp_user_id = None
        db.session.commit()
        for chat_entry in db.session.execute(select(ChatLog).filter_by(temp_owner_id=int(kwargs['temp_user_id'])).with_for_update()).scalars():
            chat_entry.owner_id = kwargs['new_user_id']
            chat_entry.temp_owner_id = None
        db.session.commit()
    elif mode == 1:
        db.session.execute(delete(ChatLog).where(ChatLog.temp_owner_id == kwargs['temp_user_id']))
        db.session.commit()
        db.session.execute(delete(ChatLog).where(ChatLog.temp_user_id == kwargs['temp_user_id']))
        db.session.commit()
    elif mode == 2:
        db.session.execute(delete(ChatLog).where(ChatLog.owner_id == kwargs['user_id']))
        db.session.commit()
        db.session.execute(delete(ChatLog).where(ChatLog.user_id == kwargs['user_id']))
        db.session.commit()
    elif mode == 3:
        db.session.execute(delete(ChatLog).filter_by(key=kwargs['key'], filename=kwargs['filename']))
        db.session.commit()
    elif mode == 4:
        for record in db.session.execute(select(ChatLog).filter_by(key=kwargs['key'], filename=kwargs['filename'], encrypted=True).with_for_update()).scalars():
            phrase = decrypt_phrase(record.message, kwargs['secret'])
            record.message = pack_phrase(phrase)
            record.encrypted = False
        db.session.commit()
    elif mode == 5:
        for record in db.session.execute(select(ChatLog).filter_by(key=kwargs['key'], filename=kwargs['filename'], encrypted=False).with_for_update()).scalars():
            phrase = unpack_phrase(record.message)
            record.message = encrypt_phrase(phrase, kwargs['secret'])
            record.encrypted = True
        db.session.commit()
    elif mode == 6:
        for record in db.session.execute(select(ChatLog).filter_by(key=kwargs['key'], filename=kwargs['filename'], encrypted=True).with_for_update()).scalars():
            try:
                phrase = decrypt_phrase(record.message, kwargs['oldsecret'])
            except:
                logmessage("substitute_secret: error decrypting phrase for filename " + kwargs['filename'] + " and uid " + kwargs['key'])
                continue
            record.message = encrypt_phrase(phrase, kwargs['newsecret'])
        db.session.commit()
