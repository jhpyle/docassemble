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

