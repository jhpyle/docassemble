import redis

r = redis.StrictRedis()
pubsub = r.pubsub(ignore_subscribe_messages=True)
pubsub.subscribe(['testme'])
for item in pubsub.listen():
    print "Got: " + str(item['data'])
    if item['data'] == 'moo':
        pubsub.subscribe(['testme2'])
        print "subscribing!"
