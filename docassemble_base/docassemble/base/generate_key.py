import string
import random
import sys

__all__ = ['random_string', 'random_alphanumeric']

r = random.SystemRandom()

def random_lower_string(length):
    return ''.join(r.choice(string.ascii_lowercase) for i in range(length))

def random_string(length):
    return ''.join(r.choice(string.ascii_letters) for i in range(length))

def random_alphanumeric(length):
    return ''.join(r.choice(string.ascii_uppercase + string.digits) for x in xrange(length))

if __name__ == "__main__":
    sys.stdout.write(random_string(32))
