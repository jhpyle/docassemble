import redis
import re
from docassemble.base.config import daconfig

redis_host = daconfig.get('redis', None)
if redis_host is None:
    redis_host = 'redis://localhost'
redis_host = redis_host.strip()
redis_host = re.sub(r'^redis://', r'', redis_host)
m = re.search(r':([0-9]+)$', redis_host)
if m:
    redis_port = m.group(1)
    redis_host = re.sub(r':([0-9]+)$', '', redis_host)
else:
    redis_port = '6379'

redis_offset = daconfig.get('redis database offset', 0)

r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset)
r_store = redis.StrictRedis(host=redis_host, port=redis_port, db=1 + redis_offset)
r_user = redis.StrictRedis(host=redis_host, port=redis_port, db=2 + redis_offset)

# def clear_user_cache(user_id=None):
#     if user_id is None:
#         keys_to_delete = [y.decode() for y in r.keys('da:usercache:*')]
#         for key in keys_to_delete:
#             r.delete(key)
#     else:
#         r.delete('da:usercache:' + str(user_id))
