import sys
from flask import render_template, session, request
from flask_kvsession import KVSessionExtension
from sqlalchemy import create_engine, MetaData
from simplekv.db.sql import SQLAlchemyStore
from flask_socketio import SocketIO, join_room, disconnect
import docassemble.base.config
docassemble.base.config.load(filename="/usr/share/docassemble/config/config.yml")
from docassemble.base.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED, dbtableprefix, hostname, in_celery
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.backend import s3, initial_dict, can_access_file_number, get_info_from_file_number, get_info_from_file_reference, get_mail_variable, async_mail, get_new_file_number, pad, unpad, encrypt_phrase, pack_phrase, decrypt_phrase, unpack_phrase, nice_date_from_utc
from docassemble.webapp.users.models import User, ChatLog
import docassemble.webapp.database
from docassemble.base.functions import get_default_timezone
import redis
import json
import eventlet
import datetime
import pytz
eventlet.monkey_patch()

alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
engine = create_engine(alchemy_connect_string, convert_unicode=True)
metadata = MetaData(bind=engine)
store = SQLAlchemyStore(engine, metadata, 'kvstore')
kv_session = KVSessionExtension(store, app)

async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode)
threads = dict()

rr = redis.StrictRedis()

def background_thread(uid=None, sid=None):
    r = redis.StrictRedis()
    pubsub = r.pubsub()
    pubsub.subscribe(['mychan'])
    for item in pubsub.listen():
        sys.stderr.write("sid: " + str(sid) + ":\n")
        data = None
        try:
            data = json.loads(item['data'])
        except:
            sys.stderr.write("  JSON parse error: " + str(item['data']) + "\n")
            continue
        if data['message'] == "KILL" and (('sid' in data and data['sid'] == sid) or 'sid' not in data):
            pubsub.unsubscribe()
            sys.stderr.write("  unsubscribed and finished for " + str(sid) + "\n")
            break
        else:
            sys.stderr.write("  Got something for uid " + data.get('uid', 'Unknown UID') + " from " + data.get('origin', "Unknown origin") + "\n")
            if 'messagetype' in data and data['messagetype'] == 'chat' and 'uid' in data and data['uid'] == uid:
                sys.stderr.write("  Emitting chat message: " + str(data['message']['message']) + "\n")
                socketio.emit('chatmessage', {'data': data['message'], 'sid': data['sid']}, namespace='/myns', room=sid)

@socketio.on('message', namespace='/myns')
def handle_message(message):
    socketio.emit('mymessage', {'data': "Hello"}, namespace='/myns')
    sys.stderr.write('received message from ' + str(session.get('uid', 'NO UID')) + ': ' + message['data'] + "\n")

@socketio.on('chat_log', namespace='/myns')
def chat_log(message):
    secret = request.cookies.get('secret', None)
    people = dict()
    for record in User.query.filter_by(active=True):
        people[record.id] = record
    if 'user_id' in session and session['user_id'] in people and people[session['user_id']].timezone is not None:
        the_timezone = pytz.timezone(people[session['user_id']].timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    if 'user_id' in session and session['user_id'] in people:
        self_person_type = 'auth'
        self_person_id = session['user_id']
    else:
        self_person_type = 'anon'
        self_person_id = session['tempuser']
    messages = list()
    for record in ChatLog.query.filter_by(filename=session.get('i', None), key=session.get('uid', None)).order_by(ChatLog.id).all():
        if record.encrypted:
            message = decrypt_phrase(record.message, secret)
        else:
            message = unpack_phrase(record.message)
        modtime = nice_date_from_utc(record.modtime, timezone=the_timezone)
        if record.user_id is not None:
            person = people[record.user_id]
            if self_person_type == 'auth' and record.user_id == self_person_id:
                is_self = True
            else:
                is_self = False
            messages.append(dict(id=record.id, is_self=is_self, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=message, roles=[role.name for role in person.roles]))
        else:
            if self_person_type == 'anon' and record.temp_user_id == self_person_id:
                is_self = True
            else:
                is_self = False
            messages.append(dict(id=record.id, is_self=is_self, temp_user_id=record.temp_user_id, modtime=modtime, message=message, roles=['user']))
    socketio.emit('chat_log', {'data': messages}, namespace='/myns')

@socketio.on('transmit', namespace='/myns')
def handle_message(message):
    rr.publish('mychan', json.dumps(dict(origin='client', room=session.get('uid', 'NO UID'), message=message['data'])))
    sys.stderr.write('received transmission from ' + str(session.get('uid', 'NO UID')) + ': ' + message['data'] + "\n")

@socketio.on('terminate', namespace='/myns')
def terminate_connection():
    #socketio.disconnect(request.sid, namespace='/myns')
    disconnect()

@socketio.on('chatmessage', namespace='/myns')
def chat_message(data):
    nowtime = datetime.datetime.utcnow()
    encrypted = session.get('encrypted', True)
    secret = request.cookies.get('secret', None)
    if encrypted:
        message = encrypt_phrase(data['data'], secret)
    else:
        message = pack_phrase(data['data'], secret)
    user_id = session.get('user_id', None)
    temp_user_id = session.get('tempuser', None)
    record = ChatLog(filename=session.get('i', None), key=session.get('uid', None), message=message, encrypted=encrypted, modtime=nowtime, temp_user_id=temp_user_id, user_id=user_id)
    db.session.add(record)
    db.session.commit()
    if user_id is not None:
        person = User.query.filter_by(id=user_id).first()
    else:
        person = None
    if person is not None and person.timezone is not None:
        the_timezone = pytz.timezone(people[session['user_id']].timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    modtime = nice_date_from_utc(nowtime, timezone=the_timezone)
    if person is None:
        if record.temp_user_id == temp_user_id:
            is_self = True
        else:
            is_self = False
        rr.publish('mychan', json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, uid=session.get('uid', 'NO UID'), message=dict(id=record.id, is_self=is_self, temp_user_id=record.temp_user_id, modtime=modtime, message=data['data'], roles=['user']))))
    else:
        if record.user_id == user_id:
            is_self = True
        else:
            is_self = False
        rr.publish('mychan', json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, uid=session.get('uid', 'NO UID'), message=dict(id=record.id, is_self=is_self, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=data['data'], roles=[role.name for role in person.roles]))))
    sys.stderr.write('received chat message from sid ' + str(request.sid) + " and uid " + str(session.get('uid', 'NO UID')) + ': ' + data['data'] + "\n")

@socketio.on('connect', namespace='/myns')
def on_connect():
    sys.stderr.write('Client connected on myns and will join room ' + session.get('uid', 'NO UID') + "\n")
    join_room(session.get('uid', 'NO UID'))
    if request.sid not in threads:
        threads[request.sid] = socketio.start_background_task(target=background_thread, uid=session.get('uid', None), sid=request.sid)

@socketio.on('disconnect', namespace='/myns')
def on_disconnect():
    sys.stderr.write('Client disconnected from myns\n')
    rr.publish('mychan', json.dumps(dict(origin='client', uid=session.get('uid', 'NO UID'), message='KILL', sid=request.sid)))

if __name__ == '__main__':
    socketio.run(app)
