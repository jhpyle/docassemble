from random import randint
import json
import redis

r = redis.Redis()
r.publish('mychan', json.dumps(dict(origin='server', room='RMXgFEzlgqdZsDSSJPPFuzDdoMYuKkBG', message='Hey random ' + str(randint(0, 99)))))
