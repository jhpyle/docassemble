import json
import redis

r = redis.Redis()
r.publish('mychan', json.dumps(dict(message='KILL')))
