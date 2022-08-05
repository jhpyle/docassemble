from contextlib import contextmanager
import datetime
import json
import random
import re
import sys
import time
import eventlet
eventlet.sleep()
eventlet.monkey_patch()
import docassemble.base.config  # noqa: E402
docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig  # noqa: E402
import docassemble.base.functions  # noqa: E402
import docassemble.base.util  # noqa: E402
docassemble.base.functions.server_context.context = 'websockets'
from docassemble.base.functions import get_default_timezone, word  # noqa: E402,F401 # pylint: disable=unused-import
from docassemble.base.logger import logmessage  # noqa: E402
import docassemble.webapp.daredis  # noqa: E402
from docassemble.webapp.app_socket import app, db, socketio  # noqa: E402
from docassemble.webapp.backend import nice_utc_date, fetch_user_dict, get_chat_log, encrypt_phrase, pack_phrase, fix_pickle_obj, get_session  # noqa: E402
from docassemble.webapp.daredis import r as rr, redis_host, redis_port, redis_offset  # noqa: E402
from docassemble.webapp.users.models import UserModel, ChatLog  # noqa: E402
from docassemblekvsession import KVSessionExtension  # noqa: E402
from flask import session, request  # noqa: E402
from flask_socketio import join_room  # noqa: E402
from simplekv.memory.redisstore import RedisStore  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import sessionmaker, joinedload  # noqa: E402
import netifaces as ni  # noqa: E402 # pylint: disable=import-error
import redis  # noqa: E402

store = RedisStore(docassemble.webapp.daredis.r_store)
kv_session = KVSessionExtension(store, app)
threads = {}
secrets = {}
Session = sessionmaker(bind=db)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    dbsession = Session()
    db.session = dbsession
    try:
        yield dbsession
        dbsession.commit()
    except:
        dbsession.rollback()
        raise
    finally:
        dbsession.close()


def obtain_lock(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    found = False
    count = 4
    while count > 0:
        record = rr.get(key)
        if record:
            logmessage("obtain_lock: waiting for " + key)
            time.sleep(1.0)
        else:
            found = False
            break
        found = True
        count -= 1
    if found:
        logmessage("Request for " + key + " deadlocked")
        release_lock(user_code, filename)
    pipe = rr.pipeline()
    pipe.set(key, 1)
    pipe.expire(key, 4)
    pipe.execute()


def release_lock(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    rr.delete(key)

# @app.teardown_appcontext
# def close_db(error):
#     # logmessage("Teardown of app context")
#     if hasattr(db, 'engine'):
#         # logmessage("Tearing down")
#         db.engine.dispose()


def background_thread(sid=None, user_id=None, temp_user_id=None):
    if user_id is not None:
        user_id = int(user_id)
    if temp_user_id is not None:
        temp_user_id = int(temp_user_id)
    logmessage("Started client thread for " + str(sid) + " who is " + str(user_id) + " or " + str(temp_user_id))
    if user_id is None:
        person = None
        user_is_temp = True
    else:
        with session_scope() as dbsession:
            person = dbsession.execute(select(UserModel).options(joinedload(UserModel.roles)).filter_by(id=user_id)).scalar()
        user_is_temp = False
    if not (person is not None and person.timezone is not None):
        r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset)

    partners = set()
    pubsub = r.pubsub()
    pubsub.subscribe([sid])
    for item in pubsub.listen():
        with session_scope() as dbsession:
            logmessage("0\n" + repr(item))
            if item['type'] != 'message':
                continue
            # logmessage("sid: " + str(sid) + ":")
            data = None
            try:
                data = json.loads(item['data'].decode())
            except:
                logmessage("  JSON parse error: " + str(item['data'].decode()))
                continue
            if data.get('message', None) == "KILL" and (('sid' in data and data['sid'] == sid) or 'sid' not in data):
                pubsub.unsubscribe(sid)
                logmessage("  interview unsubscribed and finished for " + str(sid))
                break
            logmessage("  Got something for sid " + str(sid) + " from " + data.get('origin', "Unknown origin"))
            if 'messagetype' in data:
                if data['messagetype'] == 'chat':
                    # logmessage("  Emitting interview chat message: " + str(data['message']['message']))
                    data['message']['is_self'] = bool((user_is_temp is True and str(temp_user_id) == str(data['message'].get('temp_user_id', None))) or (user_is_temp is False and str(user_id) == str(data['message'].get('user_id', None))))
                    socketio.emit('chatmessage', {'i': data['yaml_filename'], 'uid': data['uid'], 'userid': data['user_id'], 'data': data['message']}, namespace='/wsinterview', room=sid)
                elif data['messagetype'] == 'chatready':
                    pubsub.subscribe(data['sid'])
                    partners.add(data['sid'])
                    logmessage("chatready 2")
                    socketio.emit('chatready', {}, namespace='/wsinterview', room=sid)
                elif data['messagetype'] == 'departure':
                    if data['sid'] in partners:
                        partners.remove(data['sid'])
                    socketio.emit('departure', {'numpartners': len(partners)}, namespace='/wsinterview', room=sid)
                elif data['messagetype'] == 'block':
                    if data['sid'] in partners:
                        partners.remove(data['sid'])
                    socketio.emit('departure', {'numpartners': len(partners)}, namespace='/wsinterview', room=sid)
                elif data['messagetype'] == 'chatpartner':
                    partners.add(data['sid'])
                elif data['messagetype'] == 'controllerchanges':
                    socketio.emit('controllerchanges', {'parameters': data['parameters'], 'clicked': data['clicked']}, namespace='/wsinterview', room=sid)
                elif data['messagetype'] == 'controllerstart':
                    socketio.emit('controllerstart', {}, namespace='/wsinterview', room=sid)
                elif data['messagetype'] == 'controllerexit':
                    socketio.emit('controllerexit', {}, namespace='/wsinterview', room=sid)
                # elif data['messagetype'] == "newpage":
                #     logmessage("  Got new page for interview")
                #     try:
                #         obj = json.loads(r.get(data['key']))
                #     except:
                #         logmessage("  newpage JSON parse error")
                #         continue
                #     socketio.emit('newpage', {'obj': obj}, namespace='/wsinterview', room=sid)
            logmessage('  exiting interview thread for sid ' + str(sid))


@socketio.on('start_being_controlled', namespace='/wsinterview')
def interview_start_being_controlled(data):
    # logmessage("received start_being_controlled")
    yaml_filename = data['i']
    session_info = get_session(yaml_filename)
    if session_info is not None:
        session_id = session_info['uid']
        the_user_id = session.get('user_id', 't' + str(session.get('tempuser', None)))
        key = 'da:input:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        rr.publish(key, json.dumps(dict(message='start_being_controlled', key=re.sub(r'^da:input:uid:', 'da:session:uid:', key))))


@socketio.on('chat_log', namespace='/wsinterview')
def chat_log(data):
    with session_scope():
        yaml_filename = data['i']
        user_dict = get_dict(yaml_filename)
        if user_dict is None:
            return
        chat_mode = user_dict['_internal']['livehelp']['mode']
        session_info = get_session(yaml_filename)
        if session_info is not None:
            session_id = session_info['uid']
            user_id = session.get('user_id', None)
            if user_id is None:
                temp_user_id = session.get('tempuser', None)
            else:
                temp_user_id = None
            if user_id is not None:
                user_id = int(user_id)
            if temp_user_id is not None:
                temp_user_id = int(temp_user_id)
            secret = request.cookies.get('secret', None)
            if secret is not None:
                secret = str(secret)
            # logmessage("chat_log: " + str(repr(user_id)) + " " + str(repr(temp_user_id)))
            messages = get_chat_log(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, user_id, temp_user_id)
            socketio.emit('chat_log', {'data': messages}, namespace='/wsinterview', room=request.sid)
    # logmessage("Interview: sending back " + str(len(messages)) + " messages")


@socketio.on('transmit', namespace='/wsinterview')
def handle_message(message):
    session_info = get_session(message['i'])
    if session_info is not None:
        rr.publish(session_info['uid'], json.dumps(dict(origin='client', room=request.sid, message=message['data'])))


@socketio.on('terminate', namespace='/wsinterview')
def terminate_interview_connection():
    logmessage("terminate_interview_connection")
    # hopefully the disconnect will be triggered
    # if request.sid in threads:
    #     rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))
    socketio.emit('terminate', {}, namespace='/wsinterview', room=request.sid)
    # disconnect()


@socketio.on('chatmessage', namespace='/wsinterview')
def chat_message(data):
    nowtime = datetime.datetime.utcnow()
    yaml_filename = data['i']
    session_info = get_session(yaml_filename)
    if session_info is not None:
        session_id = session_info['uid']
        encrypted = session_info['encrypted']
    else:
        session_id = None
        encrypted = True
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if encrypted:
        message = encrypt_phrase(data['data'], secret)
    else:
        message = pack_phrase(data['data'])
    user_id = session.get('user_id', None)
    if user_id is None:
        temp_user_id = session.get('tempuser', None)
    else:
        temp_user_id = None
    if user_id is not None:
        user_id = int(user_id)
    if temp_user_id is not None:
        temp_user_id = int(temp_user_id)
    with session_scope() as dbsession:
        user_dict = get_dict(yaml_filename)
        chat_mode = user_dict['_internal']['livehelp']['mode']
        open_to_peer = bool(chat_mode in ['peer', 'peerhelp'])
        record = ChatLog(filename=yaml_filename, key=session_id, message=message, encrypted=encrypted, modtime=nowtime, temp_user_id=temp_user_id, user_id=user_id, open_to_peer=open_to_peer, temp_owner_id=temp_user_id, owner_id=user_id)
        dbsession.add(record)
        dbsession.commit()
        if user_id is not None:
            person = dbsession.execute(select(UserModel).options(joinedload(UserModel.roles)).filter_by(id=user_id)).scalar()
        else:
            person = None
        modtime = nice_utc_date(nowtime)
        if person is None:
            rr.publish(request.sid, json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, yaml_filename=yaml_filename, uid=session_id, user_id='t' + str(temp_user_id), message=dict(id=record.id, temp_user_id=record.temp_user_id, modtime=modtime, message=data['data'], roles=['user'], mode=chat_mode))))
        else:
            role_list = [role.name for role in person.roles]
            if len(role_list) == 0:
                role_list = ['user']
            rr.publish(request.sid, json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, yaml_filename=yaml_filename, uid=session_id, user_id=user_id, message=dict(id=record.id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=data['data'], roles=role_list, mode=chat_mode))))
    # logmessage('received chat message from sid ' + str(request.sid) + ': ' + data['data'])


def wait_for_channel(the_rr, channel):
    times = 0
    while times < 5 and the_rr.publish(channel, json.dumps(dict(messagetype='ping'))) == 0:
        times += 1
        time.sleep(0.5)
    if times >= 5:
        return False
    return True


@socketio.on('connect', namespace='/wsinterview')
def on_interview_connect():
    with session_scope():
        logmessage("Client connected on interview")
        join_room(request.sid)
        interview_connect(request.args['i'])
        rr.publish('da:monitor', json.dumps(dict(messagetype='refreshsessions')))


@socketio.on('connectagain', namespace='/wsinterview')
def on_interview_reconnect(data):
    with session_scope():
        logmessage("Client reconnected on interview")
        interview_connect(data['i'])
        rr.publish('da:monitor', json.dumps(dict(messagetype='refreshsessions')))
        socketio.emit('reconnected', {}, namespace='/wsinterview', room=request.sid)


def interview_connect(yaml_filename):
    session_info = get_session(yaml_filename)
    if session_info is not None:
        session_id = session_info['uid']
        user_dict, is_encrypted = get_dict_encrypt(yaml_filename)
        if is_encrypted:
            secret = request.cookies.get('secret', None)
        else:
            secret = None
        if secret is not None:
            secret = str(secret)
        if user_dict is None:
            logmessage("user_dict did not exist.")
            socketio.emit('terminate', {}, namespace='/wsinterview', room=request.sid)
            return

        chat_info = user_dict['_internal']['livehelp']
        if chat_info['availability'] == 'unavailable':
            logmessage("Socket started but chat is unavailable.")
            socketio.emit('terminate', {}, namespace='/wsinterview', room=request.sid)
            return
        # logmessage('chat info is ' + str(chat_info))
        peer_ok = bool(user_dict['_internal']['livehelp']['mode'] in ['peer', 'peerhelp'])
        the_user_id = session.get('user_id', 't' + str(session.get('tempuser', None)))

        if request.sid not in threads:
            # logmessage('Starting thread for sid ' + str(request.sid))
            threads[request.sid] = socketio.start_background_task(target=background_thread, sid=request.sid, user_id=session.get('user_id', None), temp_user_id=session.get('tempuser', None))
        channel_up = wait_for_channel(rr, request.sid)
        if not channel_up:
            logmessage("Channel did not come up.")
            socketio.emit('terminate', {}, namespace='/wsinterview', room=request.sid)
            return
        lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        # logmessage("Searching: " + lkey)
        lkey_exists = bool(rr.exists(lkey))
        if lkey_exists is False and peer_ok is False:
            logmessage("Key does not exist: " + lkey + ".")
            # socketio.emit('terminate', {}, namespace='/wsinterview', room=request.sid)
            # return
        failed_to_find_partner = True
        found_help = False
        if lkey_exists:
            partner_keys = rr.lrange(lkey, 0, -1)
            # logmessage("partner_keys is: " + str(type(partner_keys)) + " " + str(partner_keys))
            if partner_keys is None and not peer_ok:
                logmessage("No partner keys: " + lkey + ".")
                socketio.emit('terminate', {}, namespace='/wsinterview', room=request.sid)
                return
            rr.delete(lkey)
            for pkey in partner_keys:
                pkey = pkey.decode()
                # logmessage("Considering: " + pkey)
                partner_sid = rr.get(pkey)
                if partner_sid is not None:
                    partner_sid = partner_sid.decode()
                    is_help = bool(re.match(r'^da:monitor:available:.*', pkey))
                    if is_help and found_help:
                        continue
                    # logmessage("Trying to pub to " + str(partner_sid) + " from " + str(pkey))
                    listeners = rr.publish(partner_sid, json.dumps(dict(messagetype='chatready', uid=session_id, i=yaml_filename, userid=the_user_id, secret=secret, sid=request.sid)))
                    # logmessage("Listeners: " + str(listeners))
                    if re.match(r'^da:interviewsession.*', pkey):
                        rr.publish(request.sid, json.dumps(dict(messagetype='chatready', sid=partner_sid)))
                    else:
                        rr.publish(request.sid, json.dumps(dict(messagetype='chatpartner', sid=partner_sid)))
                    if listeners > 0:
                        if is_help:
                            found_help = True
                        failed_to_find_partner = False
        if failed_to_find_partner and peer_ok is False:
            logmessage("Unable to reach any potential chat partners.")
            # socketio.emit('terminate', {}, namespace='/wsinterview', room=request.sid)
            # return
        key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        rr.set(key, request.sid)


@socketio.on('manual_disconnect', namespace='/wsinterview')
def on_interview_manual_disconnect(data):
    logmessage("Client manual disconnect")
    yaml_filename = data['i']
    session_info = get_session(yaml_filename)
    session_id = session_info['uid']
    the_user_id = session.get('user_id', 't' + str(session.get('tempuser', None)))
    if request.sid in secrets:
        del secrets[request.sid]
    if session_id is not None:
        rr.delete('da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id))
        key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        rr.expire(key, 10)
        rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))


@socketio.on('disconnect', namespace='/wsinterview')
def on_interview_disconnect():
    logmessage('Client disconnected from interview')


def get_current_info(yaml_filename, session_id, secret):
    url_root = daconfig.get('url root', 'http://localhost') + daconfig.get('root', '/')
    url = url_root + 'interview'
    return dict(user=dict(is_anonymous=False, is_authenticated=True, email='admin@admin.com', theid=1, the_user_id=1, roles=['admin'], firstname='Admin', lastname='User', nickname='', country='', subdivisionfirst='', subdivisionsecond='', subdivisionthird='', organization='', location=None, session_uid='admin', device_id='admin'), session=session_id, secret=secret, yaml_filename=yaml_filename, url=url, url_root=url_root, encrypted=True, action=None, interface='chat', arguments={})


def get_dict(yaml_filename):
    session_info = get_session(yaml_filename)
    if session_info is not None:
        session_id = session_info['uid']
    else:
        session_id = None
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if session_id is None or yaml_filename is None:
        logmessage('Attempt to get dictionary where session not defined')
        return None
    # obtain_lock(session_id, yaml_filename)
    docassemble.base.functions.this_thread.current_info = get_current_info(yaml_filename, session_id, secret)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)  # pylint: disable=unused-variable
    except Exception as err:
        # release_lock(session_id, yaml_filename)
        logmessage('get_dict: attempt to get dictionary failed: ' + str(err))
        return None
    docassemble.base.functions.this_thread.current_info['encrypted'] = is_encrypted
    # release_lock(session_id, yaml_filename)
    return user_dict


def get_dict_encrypt(yaml_filename):
    session_info = get_session(yaml_filename)
    if session_info is not None:
        session_id = session_info['uid']
    else:
        session_id = None
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if session_id is None or yaml_filename is None:
        logmessage('Attempt to get dictionary where session not defined')
        return None, None
    # obtain_lock(session_id, yaml_filename)
    docassemble.base.functions.this_thread.current_info = get_current_info(yaml_filename, session_id, secret)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)  # pylint: disable=unused-variable
    except Exception as err:
        # release_lock(session_id, yaml_filename)
        logmessage('get_dict_encrypt: attempt to get dictionary failed: ' + str(err))
        return None, None
    docassemble.base.functions.this_thread.current_info['encrypted'] = is_encrypted
    # release_lock(session_id, yaml_filename)
    return user_dict, is_encrypted

# monitor


def monitor_thread(sid=None, user_id=None):
    logmessage("Started monitor thread for " + str(sid) + " who is " + str(user_id))
    with session_scope() as dbsession:
        if user_id is not None:
            person = dbsession.execute(select(UserModel).options(joinedload(UserModel.roles)).filter_by(id=user_id)).scalar()
        else:
            person = None
    r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset)
    listening_sids = set()
    pubsub = r.pubsub()
    pubsub.subscribe(['da:monitor', sid])
    for item in pubsub.listen():
        with session_scope() as dbsession:
            logmessage("1\n" + repr(item))
            if item['type'] != 'message':
                continue
            # logmessage("monitor sid: " + str(sid) + ":")
            data = None
            try:
                data = json.loads(item['data'].decode())
            except:
                logmessage("  monitor JSON parse error: " + item['data'].decode())
                continue
            if 'message' in data and data['message'] == "KILL":
                if item['channel'].decode() == str(sid):
                    logmessage("  monitor unsubscribed from all")
                    pubsub.unsubscribe()
                    for interview_sid in listening_sids:
                        r.publish(interview_sid, json.dumps(dict(messagetype='departure', sid=sid)))
                    break
                if item['channel'].decode() != 'da:monitor':
                    pubsub.unsubscribe(item['channel'].decode())
                    if data['sid'] in listening_sids:
                        listening_sids.remove(data['sid'])
                    logmessage("  monitor unsubscribed from " + item['channel'].decode())
                continue
            logmessage("  Got something for monitor")
            if 'messagetype' in data:
                # if data['messagetype'] == 'abortcontroller':
                #    socketio.emit('abortcontroller', {'key': data['key']}, namespace='/monitor', room=sid)
                if data['messagetype'] == 'sessionupdate':
                    # logmessage("  Got a session update: " + str(data['session']))
                    # logmessage("  Got a session update")
                    socketio.emit('sessionupdate', {'key': data['key'], 'session': data['session']}, namespace='/monitor', room=sid)
                if data['messagetype'] == 'chatready':
                    pubsub.subscribe(data['sid'])
                    listening_sids.add(data['sid'])
                    secrets[data['sid']] = data['secret']
                    r.hset('da:monitor:chatpartners:' + str(user_id), 'da:interviewsession:uid:' + str(data['uid']) + ':i:' + str(data['i']) + ':userid:' + str(data['userid']), 1)
                    if str(data['userid']).startswith('t'):
                        name = word("anonymous visitor") + ' ' + str(data['userid'])[1:]
                    else:
                        person = dbsession.execute(select(UserModel).options(joinedload(UserModel.roles)).filter_by(id=data['userid'])).scalar()
                        if person.first_name:
                            name = str(person.first_name) + ' ' + str(person.last_name)
                        else:
                            name = str(person.email)
                    logmessage("chatready 1")
                    socketio.emit('chatready', {'uid': data['uid'], 'i': data['i'], 'userid': data['userid'], 'name': name}, namespace='/monitor', room=sid)
                if data['messagetype'] == 'block':
                    pubsub.unsubscribe(item['channel'].decode())
                    if item['channel'].decode() in listening_sids:
                        listening_sids.remove(item['channel'].decode())
                    logmessage("  monitor unsubscribed from " + item['channel'].decode())
                if data['messagetype'] == 'refreshsessions':
                    socketio.emit('refreshsessions', {}, namespace='/monitor', room=sid)
                if data['messagetype'] == 'chat':
                    # logmessage("  Emitting monitor chat message: " + str(data['message']['message']))
                    data['message']['is_self'] = bool(str(user_id) == str(data['message'].get('user_id', None)))
                    socketio.emit('chatmessage', {'i': data['yaml_filename'], 'uid': data['uid'], 'userid': data['user_id'], 'data': data['message']}, namespace='/monitor', room=sid)
                if data['messagetype'] == 'chatstop':
                    logmessage("  Chat termination for sid " + data['sid'])
                    pubsub.unsubscribe(data['sid'])
                    if data['sid'] in secrets:
                        del secrets[data['sid']]
                    r.hdel('da:monitor:chatpartners:' + str(user_id), 'da:interviewsession:uid:' + str(data['uid']) + ':i:' + str(data['i']) + ':userid:' + data['userid'])
                    socketio.emit('chatstop', {'uid': data['uid'], 'i': data['i'], 'userid': data['userid']}, namespace='/monitor', room=sid)
            logmessage('  exiting monitor thread for sid ' + str(sid))


@socketio.on('connect', namespace='/monitor')
def on_monitor_connect():
    if 'monitor' not in session:
        socketio.emit('terminate', {}, namespace='/monitor', room=request.sid)
        return
    logmessage('Client connected on monitor and will join room monitor')
    key = 'da:monitor:' + str(request.sid)
    pipe = rr.pipeline()
    pipe.set(key, 1)
    pipe.expire(key, 60)
    pipe.execute()
    join_room('monitor')
    join_room(request.sid)
    user_id = session.get('user_id', None)
    if request.sid not in threads:
        threads[request.sid] = socketio.start_background_task(target=monitor_thread, sid=request.sid, user_id=user_id)


@socketio.on('disconnect', namespace='/monitor')
def on_monitor_disconnect():
    user_id = session.get('user_id', None)
    logmessage('Client disconnected from monitor')
    rr.delete('da:monitor:' + str(request.sid))
    rr.expire('da:monitor:available:' + str(user_id), 5)
    for key in rr.keys('da:monitor:role:*:userid:' + str(user_id)):
        key = key.decode()
        rr.expire(key, 5)
    for key in rr.keys('da:phonecode:monitor:' + str(user_id) + ':uid:*'):
        key = key.decode()
        the_code = rr.get(key)
        if the_code is not None:
            the_code = the_code.decode()
            rr.expire('da:callforward:' + the_code, 5)
        rr.expire(key, 5)
    rr.expire('da:monitor:chatpartners:' + str(user_id), 5)
    rr.publish(request.sid, json.dumps(dict(message='KILL', sid=request.sid)))


@socketio.on('terminate', namespace='/monitor')
def terminate_monitor_connection():
    logmessage("terminate_monitor_connection")
    # hopefully the disconnect will be triggered
    # if request.sid in threads:
    #     rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))
    socketio.emit('terminate', {}, namespace='/monitor', room=request.sid)
    # disconnect()


@socketio.on('block', namespace='/monitor')
def monitor_block(data):
    if 'monitor' not in session:
        socketio.emit('terminate', {}, namespace='/monitor', room=request.sid)
        return
    key = data.get('key', None)
    if key is None:
        logmessage("No key provided")
        return
    rr.set(re.sub(r'^da:session:', 'da:block:', key), 1)
    sid = rr.get(re.sub(r'^da:session:', 'da:interviewsession:', key))
    if sid is not None:
        sid = sid.decode()
        rr.publish(sid, json.dumps(dict(messagetype='block', sid=request.sid)))
        logmessage("Blocking")
    else:
        logmessage("Could not block because could not get sid")
    socketio.emit('block', {'key': key}, namespace='/monitor', room=request.sid)


@socketio.on('unblock', namespace='/monitor')
def monitor_unblock(data):
    if 'monitor' not in session:
        socketio.emit('terminate', {}, namespace='/monitor', room=request.sid)
        return
    key = data.get('key', None)
    if key is None:
        logmessage("No key provided")
        return
    logmessage("Unblocking")
    rr.delete(re.sub(r'^da:session:', 'da:block:', key))
    sid = rr.get(re.sub(r'^da:session:', 'da:interviewsession:', key))
    if sid is not None:
        sid = sid.decode()
        rr.publish(sid, json.dumps(dict(messagetype='chatpartner', sid=request.sid)))
    socketio.emit('unblock', {'key': key}, namespace='/monitor', room=request.sid)


def decode_dict(the_dict):
    out_dict = {}
    for k, v in the_dict.items():
        out_dict[k.decode()] = v.decode()
    return out_dict


@socketio.on('updatemonitor', namespace='/monitor')
def update_monitor(message):
    if 'monitor' not in session:
        socketio.emit('terminate', {}, namespace='/monitor', room=request.sid)
        return
    # logmessage('received message from ' + str(request.sid))
    available_for_chat = message['available_for_chat']
    new_subscribed_roles = message['subscribed_roles']
    new_phone_partners = message['phone_partners_to_add']
    term_phone_partners = message['phone_partners_to_terminate']
    phone_number = message['phone_number']
    phone_number_key = 'da:monitor:phonenumber:' + str(session['user_id'])
    if phone_number is None or phone_number == '':
        rr.delete(phone_number_key)
    else:
        pipe = rr.pipeline()
        pipe.set(phone_number_key, phone_number)
        pipe.expire(phone_number_key, 2592000)
        pipe.execute()
    phone_partners = {}
    prefix = 'da:phonecode:monitor:' + str(session['user_id']) + ':uid:'
    for key in term_phone_partners:
        key_for_phone_code = re.sub(r'da:session:uid:', prefix, key)
        the_code = rr.get(key_for_phone_code)
        if the_code is not None:
            the_code = the_code.decode()
            rr.delete(key_for_phone_code)
            rr.delete('da:callforward:' + the_code)
    if phone_number is None or phone_number == '':
        for key in rr.keys(prefix + '*'):
            key = key.decode()
            the_code = rr.get(key)
            if the_code is not None:
                the_code = the_code.decode()
                rr.delete(key)
                rr.delete('da:callforward:' + the_code)
    else:
        codes_in_use = set()
        for key in rr.keys('da:callforward:*'):
            key = key.decode()
            code = re.sub(r'^da:callforward:', '', key)
            codes_in_use.add(code)
        for key in rr.keys(prefix + '*'):
            key = key.decode()
            phone_partners[re.sub(r'^da:phonecode:monitor:[0-9]*:uid:', 'da:session:uid:', key)] = 1
        for key in new_phone_partners:
            if key in phone_partners:
                continue
            times = 0
            while times < 1000:
                times += 1
                code = "%04d" % random.randint(1000, 9999)
                if code in codes_in_use:
                    continue
                the_code = code
                new_key = re.sub(r'^da:session:uid:', prefix, key)
                code_key = 'da:callforward:' + str(code)
                pipe = rr.pipeline()
                pipe.set(new_key, code)
                pipe.set(code_key, phone_number)
                pipe.expire(new_key, 300)
                pipe.expire(code_key, 300)
                pipe.execute()
                phone_partners[key] = 1
                break
            if times >= 1000:
                logmessage("update_monitor: could not get a random integer")
    # logmessage('subscribed roles are type ' + str(type(new_subscribed_roles)) + " which is "  + str(new_subscribed_roles))
    monitor_key = 'da:monitor:' + str(request.sid)
    pipe = rr.pipeline()
    pipe.set(monitor_key, 1)
    pipe.expire(monitor_key, 60)
    pipe.execute()
    key = 'da:monitor:available:' + str(session['user_id'])
    key_exists = rr.exists(key)
    chat_partners = {}
    for cp_key in rr.hgetall('da:monitor:chatpartners:' + str(session['user_id'])):
        cp_key = cp_key.decode()
        if rr.get(cp_key) is None:
            rr.hdel('da:monitor:chatpartners:' + str(session['user_id']), cp_key)
        else:
            chat_partners[re.sub('^da:interviewsession:uid:', r'da:session:uid:', cp_key)] = 1
    # logmessage('daAvailableForChat is ' + str(available_for_chat) + " for key " + key)
    if available_for_chat:
        pipe = rr.pipeline()
        pipe.set(key, request.sid)
        pipe.expire(key, 60)
        pipe.execute()
    elif key_exists:
        # logmessage("Not available to chat; deleting da:monitor:role")
        pipe = rr.pipeline()
        pipe.delete(key)
        for avail_key in rr.keys('da:monitor:role:*:userid:' + str(session['user_id'])):
            pipe.delete(avail_key.decode())
        pipe.execute()
    avail_roles = []
    for key in rr.keys('da:chat:roletype:*'):
        avail_roles.append(re.sub(r'^da:chat:roletype:', r'', key.decode()))
    sub_role_key = 'da:monitor:userrole:' + str(session['user_id'])
    if rr.exists(sub_role_key):
        subscribed_roles = decode_dict(rr.hgetall(sub_role_key))
    else:
        subscribed_roles = {}
    del_mon_role_keys = []
    for role_key in list(new_subscribed_roles.keys()):
        if role_key not in avail_roles:
            # logmessage("role_key is " + str(role_key) + " which is " + str(type(role_key)))
            del new_subscribed_roles[role_key]
    for role_key in list(subscribed_roles.keys()):
        if role_key not in avail_roles:
            rr.hdel(sub_role_key, role_key)
            del_mon_role_keys.append('da:monitor:role:' + role_key + ':userid:' + str(session['user_id']))

    for role_key in list(new_subscribed_roles.keys()):
        if role_key not in subscribed_roles:
            rr.hset(sub_role_key, role_key, 1)
            subscribed_roles[role_key] = 1
    for role_key in list(subscribed_roles.keys()):
        if role_key not in new_subscribed_roles:
            rr.hdel(sub_role_key, role_key)
            del_mon_role_keys.append('da:monitor:role:' + role_key + ':userid:' + str(session['user_id']))
            del subscribed_roles[role_key]

    if len(del_mon_role_keys) > 0:
        pipe = rr.pipeline()
        for key in del_mon_role_keys:
            pipe.delete(key)
        pipe.execute()

    if available_for_chat and len(subscribed_roles) > 0:
        pipe = rr.pipeline()
        for role_key in list(subscribed_roles.keys()):
            key = 'da:monitor:role:' + role_key + ':userid:' + str(session['user_id'])
            pipe.set(key, 1)
            pipe.expire(key, 60)
        pipe.execute()
    keylist = []
    for key in rr.keys('da:session:*'):
        keylist.append(key.decode())
    sessions = {}
    for key in keylist:
        try:
            sessobj = fix_pickle_obj(rr.get(key))
        except:
            logmessage('error parsing value of ' + str(key) + " which was " + repr(rr.get(key)))
            continue
        if sessobj.get('chatstatus', None) != 'off':
            html = rr.get(re.sub(r'^da:session:', 'da:html:', key))
            if html is not None:
                html = html.decode()
                obj = json.loads(html)
                sessobj['browser_title'] = obj.get('browser_title', 'not available')
                sessobj['blocked'] = bool(rr.exists(re.sub(r'^da:session:', 'da:block:', key)))
                sessions[key] = sessobj
    socketio.emit('updatemonitor', {'available_for_chat': available_for_chat, 'subscribedRoles': subscribed_roles, 'sessions': sessions, 'availRoles': sorted(avail_roles), 'chatPartners': chat_partners, 'phonePartners': phone_partners}, namespace='/monitor', room=request.sid)


@socketio.on('chatmessage', namespace='/monitor')
def monitor_chat_message(data):
    if 'monitor' not in session:
        socketio.emit('terminate', {}, namespace='/monitor', room=request.sid)
        return
    key = data.get('key', None)
    # logmessage("Key is " + str(key))
    if key is None:
        logmessage("No key provided")
        return
    m = re.match(r'da:session:uid:(.*):i:(.*):userid:(.*)', key)
    if not m:
        logmessage("Invalid key provided")
        return
    session_id = m.group(1)
    yaml_filename = m.group(2)
    chat_user_id = m.group(3)
    key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(chat_user_id)
    sid = rr.get(key)
    if sid is None:
        logmessage("No sid for monitor chat message with key " + str(key))
        return
    sid = sid.decode()
    secret = secrets.get(sid, None)
    if secret is not None:
        secret = str(secret)
    # obtain_lock(session_id, yaml_filename)
    docassemble.base.functions.this_thread.current_info = get_current_info(yaml_filename, session_id, secret)
    with session_scope() as dbsession:
        try:
            steps, user_dict, encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)  # pylint: disable=unused-variable
        except Exception as err:
            # release_lock(session_id, yaml_filename)
            logmessage("monitor_chat_message: could not get dictionary: " + str(err))
            return
        # release_lock(session_id, yaml_filename)
        docassemble.base.functions.this_thread.current_info['encrypted'] = encrypted
        nowtime = datetime.datetime.utcnow()
        if encrypted:
            message = encrypt_phrase(data['data'], secret)
        else:
            message = pack_phrase(data['data'])
        user_id = session.get('user_id', None)
        if user_id is not None:
            user_id = int(user_id)
        person = dbsession.execute(select(UserModel).options(joinedload(UserModel.roles)).filter_by(id=user_id)).scalar()
        chat_mode = user_dict['_internal']['livehelp']['mode']
        m = re.match('t([0-9]+)', chat_user_id)
        if m:
            temp_owner_id = m.group(1)
            owner_id = None
        else:
            temp_owner_id = None
            owner_id = chat_user_id
        open_to_peer = bool(chat_mode in ['peer', 'peerhelp'])
        record = ChatLog(filename=yaml_filename, key=session_id, message=message, encrypted=encrypted, modtime=nowtime, user_id=user_id, temp_owner_id=temp_owner_id, owner_id=owner_id, open_to_peer=open_to_peer)
        dbsession.add(record)
        dbsession.commit()
        modtime = nice_utc_date(nowtime)
        role_list = [role.name for role in person.roles]
        if len(role_list) == 0:
            role_list = ['user']
        rr.publish(sid, json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, yaml_filename=yaml_filename, uid=session_id, user_id=chat_user_id, message=dict(id=record.id, user_id=record.user_id, first_name=person.first_name, last_name=person.last_name, email=person.email, modtime=modtime, message=data['data'], roles=role_list, mode=chat_mode))))
    # logmessage('received chat message on monitor from sid ' + str(request.sid) + ': ' + data['data'])


@socketio.on('chat_log', namespace='/monitor')
def monitor_chat_log(data):
    with session_scope():
        if 'monitor' not in session:
            socketio.emit('terminate', {}, namespace='/monitor', room=request.sid)
            return
        key = data.get('key', None)
        scroll = data.get('scroll', True)
        # logmessage("Key is " + str(key))
        # logmessage("scroll is " + repr(scroll))
        if key is None:
            logmessage("No key provided")
            return
        m = re.match(r'da:session:uid:(.*):i:(.*):userid:(.*)', key)
        if not m:
            logmessage("Invalid key provided")
            return
        session_id = m.group(1)
        yaml_filename = m.group(2)
        chat_user_id = m.group(3)
        key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(chat_user_id)
        sid = rr.get(key)
        if sid is None:
            logmessage("No sid for monitor chat message with key " + str(key))
            return
        sid = sid.decode()
        secret = secrets.get(sid, None)
        if secret is not None:
            secret = str(secret)
        # obtain_lock(session_id, yaml_filename)
        docassemble.base.functions.this_thread.current_info = get_current_info(yaml_filename, session_id, secret)
        try:
            steps, user_dict, encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)  # pylint: disable=unused-variable
        except Exception as err:
            # release_lock(session_id, yaml_filename)
            logmessage("monitor_chat_log: could not get dictionary: " + str(err))
            return
        docassemble.base.functions.this_thread.current_info['encrypted'] = encrypted
        # release_lock(session_id, yaml_filename)
        chat_mode = user_dict['_internal']['livehelp']['mode']
        m = re.match('t([0-9]+)', chat_user_id)
        if m:
            temp_user_id = m.group(1)
            user_id = None
        else:
            temp_user_id = None
            user_id = chat_user_id
        self_user_id = session.get('user_id', None)
        if user_id is not None:
            user_id = int(user_id)
        if temp_user_id is not None:
            temp_user_id = int(temp_user_id)
        if self_user_id is not None:
            self_user_id = int(self_user_id)
        messages = get_chat_log(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, None)
        socketio.emit('chat_log', {'uid': session_id, 'i': yaml_filename, 'userid': chat_user_id, 'mode': chat_mode, 'data': messages, 'scroll': scroll}, namespace='/monitor', room=request.sid)
        # logmessage("Monitor: sending back " + str(len(messages)) + " messages")

# observer


def observer_thread(sid=None, key=None):
    logmessage("Started observer thread for " + str(sid))
    r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset)
    pubsub = r.pubsub()
    pubsub.subscribe([key, sid])
    for item in pubsub.listen():
        logmessage("2\n" + repr(item))
        if item['type'] != 'message':
            continue
        # logmessage("observer sid: " + str(sid) + ":")
        data = None
        try:
            data = json.loads(item['data'].decode())
        except:
            logmessage("  observer JSON parse error: " + item['data'].decode())
            continue
        if 'message' in data and data['message'] == "KILL" and (('sid' in data and data['sid'] == sid) or 'sid' not in data):
            pubsub.unsubscribe()
            logmessage("  observer unsubscribed and finished for " + str(sid))
            break
        if 'message' in data:
            if data['message'] == "newpage":
                # logmessage("  Got new page for observer")
                try:
                    obj = json.loads(r.get(data['key']).decode())
                except:
                    logmessage("  newpage JSON parse error")
                    continue
                socketio.emit('newpage', {'obj': obj}, namespace='/observer', room=sid)
            elif data['message'] == "start_being_controlled":
                # logmessage("  got start_being_controlled message with key " + str(data['key']))
                socketio.emit('start_being_controlled', {'key': data['key']}, namespace='/observer', room=sid)
        else:
            # logmessage("  Got parameters for observer")
            socketio.emit('pushchanges', {'parameters': data}, namespace='/observer', room=sid)
        logmessage('  exiting observer thread for sid ' + str(sid))


@socketio.on('connect', namespace='/observer')
def on_observer_connect():
    if 'observer' not in session:
        socketio.emit('terminate', {}, namespace='/observer', room=request.sid)
        return
    join_room(request.sid)


@socketio.on('observe', namespace='/observer')
def on_observe(message):
    if 'observer' not in session:
        socketio.emit('terminate', {}, namespace='/observer', room=request.sid)
        return
    if request.sid not in threads:
        key = 'da:input:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
        # logmessage('Observing ' + key)
        threads[request.sid] = socketio.start_background_task(target=observer_thread, sid=request.sid, key=key)


@socketio.on('observerStartControl', namespace='/observer')
def start_control(message):
    if 'observer' not in session:
        socketio.emit('terminate', {}, namespace='/observer', room=request.sid)
        return
    self_key = 'da:control:sid:' + str(request.sid)
    key = 'da:control:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
    existing_sid = rr.get(key)
    if existing_sid is None or existing_sid.decode() == request.sid:
        # logmessage('Controlling ' + key)
        pipe = rr.pipeline()
        pipe.set(self_key, key)
        pipe.expire(self_key, 12)
        pipe.set(key, request.sid)
        pipe.expire(key, 12)
        pipe.execute()
        int_key = 'da:interviewsession:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
        int_sid = rr.get(int_key)
        if int_sid is not None:
            int_sid = int_sid.decode()
            rr.publish(int_sid, json.dumps(dict(messagetype='controllerstart')))
    else:
        logmessage('That key ' + key + ' is already taken')
        key = 'da:session:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
        # rr.publish('da:monitor', json.dumps(dict(messagetype='abortcontroller', key=key)))
        socketio.emit('abortcontrolling', {'key': key}, namespace='/observer', room=request.sid)


@socketio.on('observerStopControl', namespace='/observer')
def stop_control(message):
    if 'observer' not in session:
        socketio.emit('terminate', {}, namespace='/observer', room=request.sid)
        return
    self_key = 'da:control:sid:' + str(request.sid)
    key = 'da:control:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
    logmessage('Stop controlling ' + key)
    existing_sid = rr.get(key)
    pipe = rr.pipeline()
    pipe.delete(self_key)
    if existing_sid is not None and existing_sid.decode() == request.sid:
        pipe.delete(key)
        pipe.execute()
        sid = rr.get('da:interviewsession:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid']))
        if sid is not None:
            sid = sid.decode()
            logmessage("Calling controllerexit 1")
            rr.publish(sid, json.dumps(dict(messagetype='controllerexit', sid=request.sid)))
    else:
        pipe.execute()


@socketio.on('observerChanges', namespace='/observer')
def observer_changes(message):
    logmessage('observerChanges')
    if 'observer' not in session:
        socketio.emit('terminate', {}, namespace='/observer', room=request.sid)
        return
    sid = rr.get('da:interviewsession:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid']))
    if sid is None:
        key = 'da:session:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
        logmessage('observerChanges: sid is none.')
        if rr.get(key) is None:
            logmessage('observerChanges: session has gone away for good.  Sending stopcontrolling.')
            socketio.emit('stopcontrolling', {'key': key}, namespace='/observer', room=request.sid)
        else:
            socketio.emit('noconnection', {'key': key}, namespace='/observer', room=request.sid)
    else:
        sid = sid.decode()
        logmessage('observerChanges: sid exists at ' + time.strftime("%Y-%m-%d %H:%M:%S"))
        rr.publish(sid, json.dumps(dict(messagetype='controllerchanges', sid=request.sid, clicked=message.get('clicked', None), parameters=message['parameters'])))
        # sid=request.sid, yaml_filename=str(message['i']), uid=str(message['uid']), user_id=str(message['userid'])
        self_key = 'da:control:sid:' + str(request.sid)
        key = 'da:control:uid:' + str(message['uid']) + ':i:' + str(message['i']) + ':userid:' + str(message['userid'])
        # logmessage('Controlling ' + key)
        pipe = rr.pipeline()
        pipe.set(self_key, key)
        pipe.expire(key, 12)
        pipe.set(key, request.sid)
        pipe.expire(key, 12)
        pipe.execute()


@socketio.on('disconnect', namespace='/observer')
def on_observer_disconnect():
    logmessage('Client disconnected from observer')
    self_key = 'da:control:sid:' + str(request.sid)
    int_key = rr.get(self_key)
    if int_key is not None:
        int_key = int_key.decode()
        rr.delete(int_key)
        other_sid = rr.get(re.sub(r'^da:control:uid:', 'da:interviewsession:uid:', int_key))
    else:
        other_sid = None
    rr.delete(self_key)
    if other_sid is not None:
        other_sid = other_sid.decode()
        logmessage("Calling controllerexit 2")
        rr.publish(other_sid, json.dumps(dict(messagetype='controllerexit', sid=request.sid)))
    rr.publish(request.sid, json.dumps(dict(message='KILL', sid=request.sid)))


@socketio.on('terminate', namespace='/observer')
def terminate_observer_connection():
    logmessage("terminate_observer_connection")
    # hopefully the disconnect will be triggered
    # if request.sid in threads:
    #     rr.publish(request.sid, json.dumps(dict(origin='client', message='KILL', sid=request.sid)))
    socketio.emit('terminate', {}, namespace='/observer', room=request.sid)
    # disconnect()

if __name__ == '__main__':
    if daconfig.get('expose websockets', False):
        try:
            if 'websockets ip' in daconfig and daconfig['websockets ip']:
                host = daconfig['websockets ip']
            else:
                ifaces = [iface for iface in ni.interfaces() if iface != 'lo']
                host = ni.ifaddresses(ifaces[0])[ni.AF_INET][0]['addr']
            socketio.run(app, host=host, port=daconfig.get('websockets port', 5000))
        except:
            logmessage("Could not find the external IP address")
            if 'websockets ip' in daconfig and daconfig['websockets ip']:
                socketio.run(app, host=daconfig['websockets ip'], port=daconfig.get('websockets port', 5000))
            elif 'websockets port' in daconfig and daconfig['websockets port']:
                socketio.run(app, port=daconfig['websockets port'])
            else:
                socketio.run(app)
    else:
        if 'websockets ip' in daconfig and daconfig['websockets ip']:
            socketio.run(app, host=daconfig['websockets ip'], port=daconfig.get('websockets port', daconfig.get('websockets port', 5000)))
        elif 'websockets port' in daconfig and daconfig['websockets port']:
            socketio.run(app, port=daconfig['websockets port'])
        else:
            socketio.run(app)
