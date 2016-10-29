import sys
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
import docassemble.base.config
docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED, dbtableprefix, hostname, in_celery
from docassemble.webapp.app_and_db import app, db
import docassemble.base.util
import redis

redis_host = daconfig.get('redis', None)
if redis_host is None:
    redis_host = 'redis://localhost'
docassemble.base.util.set_redis_server(redis_host)
store = RedisStore(redis.StrictRedis(host=docassemble.base.util.redis_server, db=1))
kv_session = KVSessionExtension(store, app)
with app.app_context():
    kv_session.cleanup_sessions()
