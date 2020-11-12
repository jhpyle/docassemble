import sys
from docassemble.base.config import daconfig
from docassemble.webapp.app_object import app
from docassemblekvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
import docassemble.base.config
docassemble.base.config.load(arguments=sys.argv)
import docassemble.base.util
import docassemble.webapp.daredis

store = RedisStore(docassemble.webapp.daredis.r_store)
kv_session = KVSessionExtension(store, app)
with app.app_context():
    kv_session.cleanup_sessions()
