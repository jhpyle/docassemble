import string
import random
import sys
import math

__all__ = ['random_string', 'random_alphanumeric']

r = random.SystemRandom()


def random_bytes(length):
    return bytearray(ord(r.choice(string.ascii_letters)) for i in range(length))


def random_lower_string(length):
    return ''.join(r.choice(string.ascii_lowercase) for i in range(length))


def random_string(length):
    return ''.join(r.choice(string.ascii_letters) for i in range(length))


def random_alphanumeric(length):
    return ''.join(r.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(length))


def random_digits(num):
    the_string = ("%0" + str(num) + "d") % int(random.random()*math.pow(10, int(num)))
    return the_string[0:int(num)]

if __name__ == "__main__":
    sys.stdout.write(random_string(32))
