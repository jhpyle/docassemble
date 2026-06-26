import pickle
import codecs
import types
from io import IOBase as FileType
from dateutil import tz
from Cryptodome.Cipher import AES
from docassemble.base.generate_key import random_bytes
from docassemble.base.functions import pickleable_objects
from docassemble.webapp.utils.fixpickle import fix_pickle_obj, fix_pickle_dict

TypeType = type(type(None))
NoneType = type(None)

def pad(the_string):
    return the_string + bytearray((16 - len(the_string) % 16) * chr(16 - len(the_string) % 16), encoding='utf-8')


def unpad(the_string):
    if isinstance(the_string[-1], int):
        return the_string[0:-the_string[-1]]
    return the_string[0:-ord(the_string[-1])]


def encrypt_phrase(phrase, secret):
    iv = random_bytes(16)
    encrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, iv)
    if isinstance(phrase, str):
        phrase = bytearray(phrase, 'utf-8')
    return (iv + codecs.encode(encrypter.encrypt(pad(phrase)), 'base64')).decode('utf-8')


def pack_phrase(phrase):
    phrase = bytearray(phrase, encoding='utf-8')
    return codecs.encode(phrase, 'base64').decode('utf-8')


def decrypt_phrase(phrase_string, secret):
    phrase_string = bytearray(phrase_string, encoding='utf-8')
    decrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, phrase_string[:16])
    return unpad(decrypter.decrypt(codecs.decode(phrase_string[16:], 'base64'))).decode('utf-8')


def unpack_phrase(phrase_string):
    return codecs.decode(bytearray(phrase_string, encoding='utf-8'), 'base64').decode('utf-8')


def encrypt_dictionary(the_dict, secret):
    iv = random_bytes(16)
    encrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, iv)
    return (iv + codecs.encode(encrypter.encrypt(pad(pickle.dumps(pickleable_objects(the_dict)))), 'base64')).decode()


def pack_object(the_object):
    return codecs.encode(pickle.dumps(safe_pickle(the_object)), 'base64').decode()


def unpack_object(the_string):
    the_string = bytearray(the_string, encoding='utf-8')
    return fix_pickle_dict(codecs.decode(the_string, 'base64'))


def encrypt_object(obj, secret):
    iv = random_bytes(16)
    encrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, iv)
    return (iv + codecs.encode(encrypter.encrypt(pad(pickle.dumps(safe_pickle(obj)))), 'base64')).decode()


def decrypt_object(obj_string, secret):
    obj_string = bytearray(obj_string, encoding='utf-8')
    decrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, obj_string[:16])
    return fix_pickle_obj(unpad(decrypter.decrypt(codecs.decode(obj_string[16:], 'base64'))))


def safe_pickle(the_object):
    if isinstance(the_object, list):
        return [safe_pickle(x) for x in the_object]
    if isinstance(the_object, dict):
        new_dict = {}
        for key, value in the_object.items():
            new_dict[key] = safe_pickle(value)
        return new_dict
    if isinstance(the_object, set):
        new_set = set()
        for sub_object in the_object:
            new_set.add(safe_pickle(sub_object))
        return new_set
    if isinstance(the_object, (types.ModuleType, types.FunctionType, TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, FileType)):
        return None
    return the_object


def pack_dictionary(the_dict):
    retval = codecs.encode(pickle.dumps(pickleable_objects(the_dict)), 'base64').decode()
    return retval


def decrypt_dictionary(dict_string, secret):
    dict_string = bytearray(dict_string, encoding='utf-8')
    decrypter = AES.new(bytearray(secret, encoding='utf-8'), AES.MODE_CBC, dict_string[:16])
    return fix_pickle_dict(unpad(decrypter.decrypt(codecs.decode(dict_string[16:], 'base64'))))


def unpack_dictionary(dict_string):
    dict_string = codecs.decode(bytearray(dict_string, encoding='utf-8'), 'base64')
    return fix_pickle_dict(dict_string)


def nice_date_from_utc(timestamp, timezone=tz.tzlocal()):
    return timestamp.replace(tzinfo=tz.tzutc()).astimezone(timezone).strftime('%x %X')
