import sys
from flask import render_template, session, request
from flask_kvsession import KVSessionExtension
from sqlalchemy import create_engine, MetaData
from simplekv.db.sql import SQLAlchemyStore
from flask_socketio import SocketIO, join_room
import docassemble.base.config
docassemble.base.config.load(filename="/usr/share/docassemble/config/config.yml")
from docassemble.base.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED, dbtableprefix, hostname, in_celery
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.backend import s3, initial_dict, can_access_file_number, get_info_from_file_number, get_info_from_file_reference, get_mail_variable, async_mail, get_new_file_number
import docassemble.webapp.database
import redis
import json
import eventlet
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
                sys.stderr.write("  Emitting chat message: " + str(data['message']) + "\n")
                socketio.emit('chatmessage', {'data': data['message']}, namespace='/myns', room=sid)
#            elif 'origin' in data and data['origin'] == 'server':
#                socketio.emit('mymessage', {'data': data['message']}, namespace='/myns', room=sid)

@socketio.on('message', namespace='/myns')
def handle_message(message):
    socketio.emit('mymessage', {'data': "Hello"}, namespace='/myns')
    sys.stderr.write('received message from ' + str(session.get('uid', 'NO UID')) + ': ' + message['data'] + "\n")

@socketio.on('transmit', namespace='/myns')
def handle_message(message):
    rr.publish('mychan', json.dumps(dict(origin='client', room=session.get('uid', 'NO UID'), message=message['data'])))
    sys.stderr.write('received transmission from ' + str(session.get('uid', 'NO UID')) + ': ' + message['data'] + "\n")

@socketio.on('chatmessage', namespace='/myns')
def chat_message(message):
    rr.publish('mychan', json.dumps(dict(origin='client', messagetype='chat', sid=request.sid, uid=session.get('uid', 'NO UID'), message=message['data'])))
    sys.stderr.write('received chat message from ' + str(session.get('uid', 'NO UID')) + ': ' + message['data'] + "\n")

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
