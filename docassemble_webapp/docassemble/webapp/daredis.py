import redis
from docassemble.base.config import parse_redis_uri

(redis_host, redis_port, redis_username, redis_password, redis_offset, redis_cli) = parse_redis_uri()

r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset, password=redis_password, username=redis_username)
r_store = redis.StrictRedis(host=redis_host, port=redis_port, db=1 + redis_offset, password=redis_password, username=redis_username)
r_user = redis.StrictRedis(host=redis_host, port=redis_port, db=2 + redis_offset, password=redis_password, username=redis_username)

# def clear_user_cache(user_id=None):
#     if user_id is None:
#         keys_to_delete = [y.decode() for y in r.keys('da:usercache:*')]
#         for key in keys_to_delete:
#             r.delete(key)
#     else:
#         r.delete('da:usercache:' + str(user_id))
