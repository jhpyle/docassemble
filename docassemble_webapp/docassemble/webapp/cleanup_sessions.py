import sys
from datetime import timedelta
from simplekv.memory.redisstore import RedisStore
from docassemblekvsession import KVSessionExtension
from docassemble.webapp.app_object import app
import docassemble.webapp.daredis
import docassemble.base.util
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig

if 'session lifetime seconds' in daconfig:
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=daconfig['session lifetime seconds'])

store = RedisStore(docassemble.webapp.daredis.r_store)
kv_session = KVSessionExtension(store, app)
with app.app_context():
    kv_session.cleanup_sessions()
