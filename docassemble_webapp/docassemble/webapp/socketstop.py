import redis
import json

r = redis.Redis()
r.publish('mychan', json.dumps(dict(message='KILL')))
