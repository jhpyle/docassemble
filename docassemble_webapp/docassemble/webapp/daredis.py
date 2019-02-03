import redis
import re
from docassemble.base.config import daconfig

redis_host = daconfig.get('redis', None)
if redis_host is None:
    redis_host = 'redis://localhost'
redis_host = re.sub(r'^redis://', r'', redis_host)
    
r = redis.StrictRedis(host=redis_host, db=0)
r_store = redis.StrictRedis(host=redis_host, db=1)
r_user = redis.StrictRedis(host=redis_host, db=2)

# def clear_user_cache(user_id=None):
#     if user_id is None:
#         keys_to_delete = [y.decode() for y in r.keys('da:usercache:*')]
#         for key in keys_to_delete:
#             r.delete(key)
#     else:
#         r.delete('da:usercache:' + str(user_id))
