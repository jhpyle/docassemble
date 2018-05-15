import sys
from docassemble.base.config import daconfig
from docassemble.webapp.app_object import app
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
import docassemble.base.config
docassemble.base.config.load(arguments=sys.argv)
import docassemble.base.util
import docassemble.webapp.daredis
#import redis
#redis_host = daconfig.get('redis', None)
#if redis_host is None:
#    redis_host = 'redis://localhost'
#docassemble.base.util.set_redis_server(redis_host)
store = RedisStore(docassemble.webapp.daredis.r_store)
kv_session = KVSessionExtension(store, app)
with app.app_context():
    kv_session.cleanup_sessions()
