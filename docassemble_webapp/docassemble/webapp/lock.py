import time
from contextlib import contextmanager
from docassemble.base.error import DAException
from docassemble.webapp.config import CONCURRENCY_LOCK_TIMEOUT
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.daredis import r

@contextmanager
def lock_context(user_code, filename, patient=False, use_lock=True):
    try:
        if use_lock:
            if patient:
                obtain_lock_patiently(user_code, filename)
            else:
                obtain_lock(user_code, filename)
        yield
    finally:
        if use_lock:
            release_lock(user_code, filename)

def obtain_lock(user_code, filename):
    key = f'da:lock:{user_code}:{filename}'
    # logmessage("obtain_lock: getting " + key)
    found = False
    count = CONCURRENCY_LOCK_TIMEOUT * 3
    while count > 0:
        record = r.get(key)
        if record:
            logmessage("obtain_lock: waiting for " + key)
            time.sleep(1.0)
        else:
            found = False
            break
        found = True
        count -= 1
    if found:
        logmessage("Request for " + key + " deadlocked")
        release_lock(user_code, filename)
    pipe = r.pipeline()
    pipe.set(key, 1)
    pipe.expire(key, CONCURRENCY_LOCK_TIMEOUT)
    pipe.execute()


def obtain_lock_patiently(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    # logmessage("obtain_lock: getting " + key)
    found = False
    count = 200
    while count > 0:
        record = r.get(key)
        if record:
            logmessage("obtain_lock: waiting for " + key)
            time.sleep(3.0)
        else:
            found = False
            break
        found = True
        count -= 1
    if found:
        # logmessage("Request for " + key + " deadlocked")
        # release_lock(user_code, filename)
        raise DAException("obtain_lock_patiently: aborting attempt to obtain lock on " + user_code + " for " + filename + " due to deadlock")
    pipe = r.pipeline()
    pipe.set(key, 1)
    pipe.expire(key, CONCURRENCY_LOCK_TIMEOUT)
    pipe.execute()

@hookimpl
def release_lock(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    # logmessage("release_lock: releasing " + key)
    r.delete(key)
