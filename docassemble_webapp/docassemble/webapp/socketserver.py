import sys
from flask import render_template, session, request
from flask_kvsession import KVSessionExtension
from sqlalchemy import create_engine, MetaData, or_, and_
from simplekv.db.sql import SQLAlchemyStore
from flask_socketio import SocketIO, join_room, disconnect
import docassemble.base.config
docassemble.base.config.load(filename="/usr/share/docassemble/config/config.yml")
from docassemble.base.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED, dbtableprefix, hostname, in_celery
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.backend import s3, initial_dict, can_access_file_number, get_info_from_file_number, get_info_from_file_reference, get_mail_variable, async_mail, get_new_file_number, pad, unpad, encrypt_phrase, pack_phrase, decrypt_phrase, unpack_phrase, nice_utc_date, nice_date_from_utc, fetch_user_dict
from docassemble.webapp.users.models import User, ChatLog
import docassemble.webapp.database
from docassemble.base.functions import get_default_timezone
import redis
import json
import eventlet
import datetime
import pytz
import pickle
import re
import time
eventlet.monkey_patch()

alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
engine = create_engine(alchemy_connect_string, convert_unicode=True)
metadata = MetaData(bind=engine)
store = SQLAlchemyStore(engine, metadata, 'kvstore')
kv_session = KVSessionExtension(store, app)

async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode)
threads = dict()
secrets = dict()

rr = redis.StrictRedis()

def background_thread(sid=None, user_id=None, temp_user_id=None):
    if user_id is None:
        person = None
        user_is_temp = True
    else:
        person = User.query.filter_by(id=user_id).first()
        user_is_temp = False
    if person is not None and person.timezone is not None:
        the_timezone = pytz.timezone(person.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    r = redis.StrictRedis()
    pubsub = r.pubsub()
    pubsub.subscribe([sid])
    partners = set()
    for item in pubsub.listen():
        if item['type'] != 'message':
            continue
        sys.stderr.write("sid: " + str(sid) + ":\n")
        data = None
        try:
            data = json.loads(item['data'])
        except:
            sys.stderr.write("  JSON parse error: " + str(item['data']) + "\n")
            continue
        if data.get('message', None) == "KILL" and (('sid' in data and data['sid'] == sid) or 'sid' not in data):
            pubsub.unsubscribe(sid)
            sys.stderr.write("  interview unsubscribed and finished for " + str(sid) + "\n")
            break
        else:
            sys.stderr.write("  Got something for sid " + str(sid) + " from " + data.get('origin', "Unknown origin") + "\n")
            if 'messagetype' in data:
                if data['messagetype'] == 'chat':
                    sys.stderr.write("  Emitting interview chat message: " + str(data['message']['message']) + "\n")
                    if (user_is_temp is True and str(temp_user_id) == str(data['message'].get('temp_user_id', None))) or (user_is_temp is False and str(user_id) == str(data['message'].get('user_id', None))):
                        data['message']['is_self'] = True
                    else:
                        data['message']['is_self'] = False
                    socketio.emit('chatmessage', {'i': data['yaml_filename'], 'uid': data['uid'], 'userid': data['user_id'], 'data': data['message']}, namespace='/interview', room=sid)
                elif data['messagetype'] == 'departure':
                    partners.remove(data['sid'])
                    socketio.emit('departure', {'numpartners': len(partners)}, namespace='/interview', room=sid)
                elif data['messagetype'] == 'chatpartner':
                    partners.add(data['sid'])

@socketio.on('message', namespace='/interview')
def handle_message(message):
    socketio.emit('mymessage', {'data': "Hello"}, namespace='/interview')
    sys.stderr.write('received message from ' + str(session.get('uid', 'NO UID')) + ': ' + message['data'] + "\n")

def get_person(user_id, cache):
    if user_id in cache:
        return cache[user_id]
    for record in User.query.filter_by(id=user_id):
        cache[record.id] = record
        return record
    return None
    
def get_chat_log(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, self_temp_id):
    messages = list()
    people = dict()
    if user_id is not None:
        if get_person(user_id, people) is None:
            return list()
        chat_person_type = 'auth'
        chat_person_id = user_id
    else:
        chat_person_type = 'anon'
        chat_person_id = temp_user_id
    if self_user_id is not None:
        if get_person(self_user_id, people) is None:
            return list()
        self_person_type = 'auth'
        self_person_id = self_user_id
    else:
        self_person_type = 'anon'
        self_person_id = self_temp_id
    if chat_mode in ['peer', 'peerhelp']:
        open_to_peer = True
    else:
        open_to_peer = False
    if chat_person_type == 'auth':
        if chat_mode in ['peer', 'peerhelp']:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.owner_id == chat_person_id))).order_by(ChatLog.id).all()
        else:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.owner_id == chat_person_id)).order_by(ChatLog.id).all()
        for record in records:
            if record.encrypted:
                try:
                    message = decrypt_phrase(record.message, secret)
                except:
                    sys.stderr.write("Could not decrypt phrase with secret " + str(secret) + "\n")
                    continue
            else:
                message = unpack_phrase(record.message)
            modtime = nice_utc_date(record.modtime)
            if self_person_type == 'auth':
                if self_person_id == record.user_id:
                    is_self = True
                else:
                    is_self = False
            else:
                if self_person_id == record.temp_user_id:
                    is_self = True
                else:
                    is_self = False
            if record.user_id is not None:
                person = get_person(record.user_id, people)
                if person is None:
                    sys.stderr.write("Person " + str(record.user_id) + " did not exist\n")
                    continue
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=message, roles=[role.name for role in person.roles]))
            else:
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, modtime=modtime, message=message, roles=['user']))
    else:
        if chat_mode in ['peer', 'peerhelp']:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, or_(ChatLog.open_to_peer == True, ChatLog.temp_owner_id == chat_person_id))).order_by(ChatLog.id).all()
        else:
            records = ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id, ChatLog.temp_owner_id == chat_person_id)).order_by(ChatLog.id).all()
        for record in records:
            if record.encrypted:
                try:
                    message = decrypt_phrase(record.message, secret)
                except:
                    sys.stderr.write("Could not decrypt phrase with secret " + str(secret) + "\n")
                    continue
            else:
                message = unpack_phrase(record.message)
            modtime = nice_utc_date(record.modtime)
            if self_person_type == 'auth':
                if self_person_id == record.user_id:
                    is_self = True
                else:
                    is_self = False
            else:
                if self_person_id == record.temp_user_id:
                    is_self = True
                else:
                    is_self = False
            if record.user_id is not None:
                person = get_person(record.user_id, people)
                if person is None:
                    sys.stderr.write("Person " + str(record.user_id) + " did not exist\n")
                    continue
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=message, roles=[role.name for role in person.roles]))
            else:
                messages.append(dict(id=record.id, is_self=is_self, temp_owner_id=record.temp_owner_id, temp_user_id=record.temp_user_id, owner_id=record.owner_id, user_id=record.user_id, modtime=modtime, message=message, roles=['user']))
    return messages
    
@socketio.on('chat_log', namespace='/interview')
def chat_log(message):
    user_dict = get_dict()
    chat_mode = user_dict['_internal']['chat']['mode']
    yaml_filename = session.get('i', None)
    session_id = session.get('uid', None)
    user_id = session.get('user_id', None)
    if user_id is None:
        temp_user_id = session.get('tempuser', None)
    else:
        temp_user_id = None
    secret = request.cookies.get('secret', None)
    messages = get_chat_log(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, user_id, temp_user_id)
    socketio.emit('chat_log', {'data': messages}, namespace='/interview')
    #sys.stderr.write("Interview: sending back " + str(len(messages)) + " messages")

@socketio.on('transmit', namespace='/interview')
def handle_message(message):
    sys.stderr.write('received transmission from ' + str(session.get('uid', 'NO UID')) + ': ' + message['data'] + "\n")
    session_id = session.get('uid', None)
    if session_id is not None:
        rr.publish(session_id, json.dumps(dict(origin='client', room=request.sid, message=message['data'])))

@socketio.on('terminate', namespace='/interview')
def terminate_interview_connection():
    # hopefully the disconnect will be triggered
    # if request.sid in threads:
    #     rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))
    disconnect()

@socketio.on('chatmessage', namespace='/interview')
def chat_message(data):
    nowtime = datetime.datetime.utcnow()
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    encrypted = session.get('encrypted', True)
    secret = request.cookies.get('secret', None)
    if encrypted:
        message = encrypt_phrase(data['data'], secret)
    else:
        message = pack_phrase(data['data'], secret)
    user_id = session.get('user_id', None)
    if user_id is None:
        temp_user_id = session.get('tempuser', None)
    else:
        temp_user_id = None
    user_dict = get_dict()
    chat_mode = user_dict['_internal']['chat']['mode']
    if chat_mode in ['peer', 'peerhelp']:
        open_to_peer = True
    else:
        open_to_peer = False
    record = ChatLog(filename=yaml_filename, key=session_id, message=message, encrypted=encrypted, modtime=nowtime, temp_user_id=temp_user_id, user_id=user_id, open_to_peer=open_to_peer, temp_owner_id=temp_user_id, owner_id=user_id)
    db.session.add(record)
    db.session.commit()
    if user_id is not None:
        person = User.query.filter_by(id=user_id).first()
    else:
        person = None
    modtime = nice_utc_date(nowtime)
    if person is None:
        # if record.temp_user_id == temp_user_id:
        #     is_self = True
        # else:
        #     is_self = False
        rr.publish(request.sid, json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, yaml_filename=yaml_filename, uid=session_id, user_id='t' + str(temp_user_id), message=dict(id=record.id, temp_user_id=record.temp_user_id, modtime=modtime, message=data['data'], roles=['user']))))
    else:
        # if record.user_id == user_id:
        #     is_self = True
        # else:
        #     is_self = False
        rr.publish(request.sid, json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, yaml_filename=yaml_filename, uid=session_id, user_id=user_id, message=dict(id=record.id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=data['data'], roles=[role.name for role in person.roles]))))
    sys.stderr.write('received chat message from sid ' + str(request.sid) + ': ' + data['data'] + "\n")

def wait_for_channel(rr, channel):
    times = 0
    while times < 5 and rr.publish(channel, json.dumps(dict(messagetype='ping'))) == 0:
        times += 1
        time.sleep(0.5)
    if times >= 5:
        return False
    else:
        return True

@socketio.on('connect', namespace='/interview')
def on_interview_connect():
    sys.stderr.write("Client connected on interview\n")
    interview_connect()

@socketio.on('connectagain', namespace='/interview')
def on_interview_reconnect(data):
    sys.stderr.write("Client reconnected on interview\n")
    interview_connect()
    socketio.emit('reconnected', {}, namespace='/interview')
    
def interview_connect():
    session_id = session.get('uid', None)
    if session_id is not None:
        user_dict, is_encrypted = get_dict_encrypt()
        if is_encrypted:
            secret = request.cookies.get('secret', None)
        else:
            secret = None
        if user_dict is None:
            sys.stderr.write("user_dict did not exist.\n")
            terminate_interview_connection()
            return
        
        chat_info = user_dict['_internal']['chat']
        if chat_info['availability'] != 'available':
            sys.stderr.write("Socket started but chat not available.\n")
            terminate_interview_connection()
            return
        sys.stderr.write('chat info is ' + str(chat_info) + "\n")
        
        yaml_filename = session.get('i', None)
        the_user_id = session.get('user_id', 't' + str(session.get('tempuser', None)))
        
        if request.sid not in threads:
            threads[request.sid] = socketio.start_background_task(target=background_thread, sid=request.sid, user_id=session.get('user_id', None), temp_user_id=session.get('tempuser', None))
        channel_up = wait_for_channel(rr, request.sid)
        if not channel_up:
            sys.stderr.write("Channel did not come up.\n")
            terminate_interview_connection()
            return
        lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        sys.stderr.write("Searching: " + lkey + "\n")
        if not rr.exists(lkey):
            sys.stderr.write("Key does not exist: " + lkey + ".\n")
            terminate_interview_connection()
            return
        partner_keys = rr.lrange(lkey, 0, -1)
        sys.stderr.write("partner_keys is: " + str(type(partner_keys)) + " " + str(partner_keys) + "\n")
        if partner_keys is None:
            sys.stderr.write("No partner keys: " + lkey + ".\n")
            terminate_interview_connection()
            return
        rr.delete(lkey)
        failure = True
        for pkey in partner_keys:
            sys.stderr.write("Considering: " + pkey + "\n")
            partner_sid = rr.get(pkey)
            if partner_sid is not None:
                sys.stderr.write("Trying to pub to " + partner_sid + "\n")
                listeners = rr.publish(partner_sid, json.dumps(dict(messagetype='chatready', uid=session_id, i=yaml_filename, userid=the_user_id, secret=secret, sid=request.sid)))
                sys.stderr.write("Listeners: " + str(listeners) + "\n")
                rr.publish(request.sid, json.dumps(dict(messagetype='chatpartner', sid=partner_sid)))
                if listeners > 0:
                    failure = False
                    break
        if failure:
            sys.stderr.write("Unable to reach any potential chat partners.\n")
            terminate_interview_connection()
            return

        key = 'da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        rr.set(key, request.sid)
        join_room(request.sid)

@socketio.on('disconnect', namespace='/interview')
def on_interview_disconnect():
    sys.stderr.write('Client disconnected from interview\n')
    yaml_filename = session.get('i', None)
    session_id = session.get('uid', None)
    the_user_id = session.get('user_id', 't' + str(session.get('tempuser', None)))
    if request.sid in secrets:
        del secrets[request.sid]
    if session_id is not None:
        key = 'da:chatsession:uid:' + str(session.get('uid', None)) + ':i:' + str(session.get('i', None)) + ':userid:' + str(the_user_id)
        rr.delete(key)
        rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))

def get_dict():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    secret = request.cookies.get('secret', None)
    if session_id is None or yaml_filename is None:
        sys.stderr.write('Attempt to get dictionary where session not defined\n')
        return None
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        return None
    return user_dict

def get_dict_encrypt():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    secret = request.cookies.get('secret', None)
    if session_id is None or yaml_filename is None:
        sys.stderr.write('Attempt to get dictionary where session not defined\n')
        return None, None
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        return None, None
    return user_dict, is_encrypted

def monitor_thread(sid=None, user_id=None):
    sys.stderr.write("Started monitor thread for " + str(sid) + " who is " + str(user_id) + "\n")
    if user_id is not None:
        person = User.query.filter_by(id=user_id).first()
    else:
        person = None
    if person is not None and person.timezone is not None:
        the_timezone = pytz.timezone(person.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    r = redis.StrictRedis()
    listening_sids = set()
    pubsub = r.pubsub()
    pubsub.subscribe(['da:monitor', sid])
    for item in pubsub.listen():
        if item['type'] != 'message':
            continue
        sys.stderr.write("monitor sid: " + str(sid) + ":\n")
        data = None
        try:
            data = json.loads(item['data'])
        except:
            sys.stderr.write("  monitor JSON parse error: " + str(item['data']) + "\n")
            continue
        if 'message' in data and data['message'] == "KILL":
            if item['channel'] == str(sid):
                sys.stderr.write("  monitor unsubscribed from all\n")
                pubsub.unsubscribe()
                for interview_sid in listening_sids:
                    r.publish(interview_sid, json.dumps(dict(messagetype='departure', sid=sid)))
                break
            elif item['channel'] != 'da:monitor':
                pubsub.unsubscribe(item['channel'])
                if data['sid'] in listening_sids:
                    listening_sids.remove(data['sid'])
                sys.stderr.write("  monitor unsubscribed from " + str(item['channel']) + "\n")
            continue
        else:
            sys.stderr.write("  Got something for monitor\n")
            if 'messagetype' in data:
                if data['messagetype'] == 'sessionupdate':
                    sys.stderr.write("  Got a session update: " + str(data['session']) + "\n")
                    socketio.emit('sessionupdate', {'key': data['key'], 'session': data['session']}, namespace='/monitor', room=sid);
                if data['messagetype'] == 'chatready':
                    pubsub.subscribe(data['sid'])
                    listening_sids.add(data['sid'])
                    secrets[data['sid']] = data['secret']
                    socketio.emit('chatready', {'uid': data['uid'], 'i': data['i'], 'userid': data['userid']}, namespace='/monitor', room=sid);
                if data['messagetype'] == 'refreshsessions':
                    socketio.emit('refreshsessions', {}, namespace='/monitor', room=sid);
                if data['messagetype'] == 'chat':
                    sys.stderr.write("  Emitting monitor chat message: " + str(data['message']['message']) + "\n")
                    if str(user_id) == str(data['message'].get('user_id', None)):
                        data['message']['is_self'] = True
                    else:
                        data['message']['is_self'] = False
                    socketio.emit('chatmessage', {'i': data['yaml_filename'], 'uid': data['uid'], 'userid': data['user_id'], 'data': data['message']}, namespace='/monitor', room=sid)
                if data['messagetype'] == 'chatstop':
                    sys.stderr.write("  Chat termination for sid " + data['sid'] + "\n")
                    pubsub.unsubscribe(data['sid'])
                    socketio.emit('chatstop', {'uid': data['uid'], 'i': data['i'], 'userid': data['userid']}, namespace='/monitor', room=sid);

@socketio.on('connect', namespace='/monitor')
def on_monitor_connect():
    if 'monitor' not in session:
        terminate_monitor_connection()
        return
    sys.stderr.write('Client connected on monitor and will join room monitor\n')
    key = 'da:monitor:' + str(request.sid)
    rr.set(key, 1)
    join_room('monitor')
    join_room(request.sid)
    user_id = session.get('user_id', None)
    if request.sid not in threads:
        threads[request.sid] = socketio.start_background_task(target=monitor_thread, sid=request.sid, user_id=user_id)

@socketio.on('disconnect', namespace='/monitor')
def on_monitor_disconnect():
    user_id = session.get('user_id', None)
    sys.stderr.write('Client disconnected from monitor\n')
    rr.delete('da:monitor:' + str(request.sid))
    #rr.delete('da:monitor:available:' + str(user_id))
    for key in rr.keys('da:monitor:role:*:userid:' + str(user_id)):
        rr.delete(key)
    rr.publish(request.sid, json.dumps(dict(message='KILL', sid=request.sid)))

@socketio.on('terminate', namespace='/monitor')
def terminate_monitor_connection():
    # hopefully the disconnect will be triggered
    # if request.sid in threads:
    #     rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))
    disconnect()
    
@socketio.on('updatemonitor', namespace='/monitor')
def update_monitor(message):
    #sys.stderr.write('received message from ' + str(request.sid) + "\n")
    available_for_chat = message['available_for_chat']
    new_subscribed_roles = message['subscribed_roles']
    #sys.stderr.write('subscribed roles are type ' + str(type(new_subscribed_roles)) + " which is "  + str(new_subscribed_roles) + "\n")
    key = 'da:monitor:available:' + str(session['user_id'])
    key_exists = rr.exists(key)
    #sys.stderr.write('daAvailableForChat is ' + str(available_for_chat) + " for key " + key + "\n")
    if available_for_chat:
        pipe = rr.pipeline()
        pipe.set(key, request.sid)
        pipe.expire(key, 60)
        pipe.execute()
    elif key_exists:
        #sys.stderr.write("Deleting shit\n")
        pipe = rr.pipeline()
        pipe.delete(key)
        for avail_key in rr.keys('da:monitor:role:*:userid:' + str(session['user_id'])):
            pipe.delete(avail_key)
        pipe.execute()
    avail_roles = list()
    for key in rr.keys('da:chat:roletype:*'):
        avail_roles.append(re.sub(r'^da:chat:roletype:', r'', key))
    sub_role_key = 'da:monitor:userrole:' + str(session['user_id'])
    if rr.exists(sub_role_key):
        subscribed_roles = rr.hgetall(sub_role_key)
    else:
        subscribed_roles = dict()
    del_mon_role_keys = list()
    for role_key in new_subscribed_roles.keys():
        if role_key not in avail_roles:
            #sys.stderr.write("role_key is " + str(role_key) + " which is " + str(type(role_key)) + "\n")
            del new_subscribed_roles[role_key]
    for role_key in subscribed_roles.keys():
        if role_key not in avail_roles:
            rr.hdel(sub_role_key, role_key)
            del_mon_role_keys.append('da:monitor:role:' + role_key + ':userid:' + str(session['user_id']))

    for role_key in new_subscribed_roles.keys():
        if role_key not in subscribed_roles:
            rr.hset(sub_role_key, role_key, 1)
            subscribed_roles[role_key] = 1;
    for role_key in subscribed_roles.keys():
        if role_key not in new_subscribed_roles:
            rr.hdel(sub_role_key, role_key)
            del_mon_role_keys.append('da:monitor:role:' + role_key + ':userid:' + str(session['user_id']))
            del subscribed_roles[role_key]

    if len(del_mon_role_keys):
        pipe = rr.pipeline()
        for key in del_mon_role_keys:
            pipe.delete(key)
        pipe.execute()

    if available_for_chat and len(subscribed_roles):
        pipe = rr.pipeline()
        for role_key in subscribed_roles.keys():
            key = 'da:monitor:role:' + role_key + ':userid:' + str(session['user_id'])
            pipe.set(key, 1)
            pipe.expire(key, 60)
        pipe.execute()
    keylist = list()
    for key in rr.keys('da:session:*'):
        keylist.append(key)
    sessions = dict()
    for key in keylist:
        try:
            sessobj = pickle.loads(rr.get(key))
        except:
            sys.stderr.write('error parsing value of ' + str(key) + " which was " + str(rr.get(key)) + "\n")
            continue
        if sessobj.get('chatstatus', None) in ('waiting', 'standby', 'ringing', 'ready', 'on'):
            html = rr.get(re.sub(r'^da:session:', 'da:html:', key))
            if html is not None:
                obj = json.loads(html)
                sessobj['browser_title'] = obj.get('browser_title', 'not available')
                sessions[key] = sessobj;
    socketio.emit('updatemonitor', {'available_for_chat': available_for_chat, 'subscribedRoles': subscribed_roles, 'sessions': sessions, 'availRoles': sorted(avail_roles)}, namespace='/monitor');

@socketio.on('chatmessage', namespace='/monitor')
def monitor_chat_message(data):
    key = data.get('key', None)
    sys.stderr.write("Key is " + str(key) + "\n")
    if key is None:
        sys.stderr.write("No key provided\n")
        return
    m = re.match(r'da:session:uid:(.*):i:(.*):userid:(.*)', key)
    if not m:
        sys.stderr.write("Invalid key provided\n")
        return
    session_id = m.group(1)
    yaml_filename = m.group(2)
    chat_user_id = m.group(3)
    key = 'da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(chat_user_id)
    sid = rr.get(key)
    if sid is None:
        sys.stderr.write("No sid for monitor chat message with key " + str(key) + "\n")
        return

    secret = secrets.get(sid, None)
    try:
        steps, user_dict, encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        sys.stderr.write("Could not get dictionary for monitor_chat_message\n")
        return
    nowtime = datetime.datetime.utcnow()
    if encrypted:
        message = encrypt_phrase(data['data'], secret)
    else:
        message = pack_phrase(data['data'], secret)
    user_id = session.get('user_id', None)
    person = User.query.filter_by(id=user_id).first()
    chat_mode = user_dict['_internal']['chat']['mode']
    m = re.match('t([0-9]+)', chat_user_id)
    if m:
        temp_owner_id = m.group(1)
        owner_id = None
    else:
        temp_owner_id = None
        owner_id = chat_user_id
    if chat_mode in ['peer', 'peerhelp']:
        open_to_peer = True
    else:
        open_to_peer = False
    record = ChatLog(filename=yaml_filename, key=session_id, message=message, encrypted=encrypted, modtime=nowtime, user_id=user_id, temp_owner_id=temp_owner_id, owner_id=owner_id, open_to_peer=open_to_peer)
    db.session.add(record)
    db.session.commit()
    modtime = nice_utc_date(nowtime)
    rr.publish(sid, json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, yaml_filename=yaml_filename, uid=session_id, user_id=chat_user_id, message=dict(id=record.id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=data['data'], roles=[role.name for role in person.roles]))))
    sys.stderr.write('received chat message on monitor from sid ' + str(request.sid) + ': ' + data['data'] + "\n")
    
@socketio.on('chat_log', namespace='/monitor')
def monitor_chat_log(data):
    key = data.get('key', None)
    sys.stderr.write("Key is " + str(key) + "\n")
    if key is None:
        sys.stderr.write("No key provided\n")
        return
    m = re.match(r'da:session:uid:(.*):i:(.*):userid:(.*)', key)
    if not m:
        sys.stderr.write("Invalid key provided\n")
        return
    session_id = m.group(1)
    yaml_filename = m.group(2)
    chat_user_id = m.group(3)
    key = 'da:chatsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(chat_user_id)
    sid = rr.get(key)
    if sid is None:
        sys.stderr.write("No sid for monitor chat message with key " + str(key) + "\n")
        return

    secret = secrets.get(sid, None)
    try:
        steps, user_dict, encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        sys.stderr.write("Could not get dictionary for monitor_chat_message\n")
        return
    chat_mode = user_dict['_internal']['chat']['mode']
    m = re.match('t([0-9]+)', chat_user_id)
    if m:
        temp_user_id = m.group(1)
        user_id = None
    else:
        temp_user_id = None
        user_id = chat_user_id
    self_user_id = session.get('user_id', None)
    messages = get_chat_log(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, None)
    socketio.emit('chat_log', {'uid': session_id, 'i': yaml_filename, 'userid': chat_user_id, 'data': messages}, namespace='/monitor')
    #sys.stderr.write("Monitor: sending back " + str(len(messages)) + " messages")

#observer

def observer_thread(sid=None, key=None):
    sys.stderr.write("Started observer thread\n")
    r = redis.StrictRedis()
    pubsub = r.pubsub()
    pubsub.subscribe([key])
    for item in pubsub.listen():
        if item['type'] != 'message':
            continue
        sys.stderr.write("observer sid: " + str(sid) + ":\n")
        data = None
        try:
            data = json.loads(item['data'])
        except:
            sys.stderr.write("  observer JSON parse error: " + str(item['data']) + "\n")
            continue
        if 'message' in data and data['message'] == "KILL" and (('sid' in data and data['sid'] == sid) or 'sid' not in data):
            pubsub.unsubscribe()
            sys.stderr.write("  observer unsubscribed and finished for " + str(sid) + "\n")
            break
        elif 'message' in data and data['message'] == "newpage":
            sys.stderr.write("  Got new page for observer\n")
            try:
                obj = json.loads(r.get(data['key']))
            except:
                sys.stderr.write("  newpage JSON parse error\n")
                continue
            socketio.emit('newpage', {'obj': obj}, namespace='/observer', room=sid);
        else:
            sys.stderr.write("  Got something for observer\n")
            socketio.emit('pushchanges', {'parameters': data}, namespace='/observer', room=sid);

@socketio.on('connect', namespace='/observer')
def on_observer_connect():
    if 'observer' not in session:
        terminate_observer_connection()
        return
    join_room(request.sid)

@socketio.on('observe', namespace='/observer')
def on_observe(message):
    if request.sid not in threads:
        key = 'da:input:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
        sys.stderr.write('Observing ' + key + '\n')
        threads[request.sid] = socketio.start_background_task(target=observer_thread, sid=request.sid, key=key)

@socketio.on('disconnect', namespace='/observer')
def on_observer_disconnect():
    sys.stderr.write('Client disconnected from observer\n')
    key = 'da:observer:' + str(request.sid)
    rr.delete(key)
    rr.publish('da:observer', json.dumps(dict(origin='client', message='KILL', sid=request.sid)))
    
@socketio.on('terminate', namespace='/observer')
def terminate_observer_connection():
    # hopefully the disconnect will be triggered
    # if request.sid in threads:
    #     rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))
    disconnect()

if __name__ == '__main__':
    socketio.run(app)
