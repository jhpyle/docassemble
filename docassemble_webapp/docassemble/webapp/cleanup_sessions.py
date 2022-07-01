import sys
from simplekv.memory.redisstore import RedisStore
from docassemblekvsession import KVSessionExtension
from docassemble.webapp.app_object import app
import docassemble.webapp.daredis
import docassemble.base.util
import docassemble.base.config
docassemble.base.config.load(arguments=sys.argv)

store = RedisStore(docassemble.webapp.daredis.r_store)
kv_session = KVSessionExtension(store, app)
with app.app_context():
    kv_session.cleanup_sessions()
