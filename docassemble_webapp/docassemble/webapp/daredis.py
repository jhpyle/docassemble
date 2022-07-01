import redis
from docassemble.base.config import parse_redis_uri

(redis_host, redis_port, redis_username, redis_password, redis_offset, redis_cli, ssl_opts) = parse_redis_uri()

r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_offset, password=redis_password, username=redis_username, **ssl_opts)
r_store = redis.StrictRedis(host=redis_host, port=redis_port, db=1 + redis_offset, password=redis_password, username=redis_username, **ssl_opts)
r_user = redis.StrictRedis(host=redis_host, port=redis_port, db=2 + redis_offset, password=redis_password, username=redis_username, **ssl_opts)
