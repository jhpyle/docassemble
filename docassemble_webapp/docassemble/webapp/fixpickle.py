from six import string_types, text_type, PY2
import datetime
TypeType = type(type(None))
NoneType = type(None)
from docassemble.base.logger import logmessage

def fix_pickle_obj(the_obj):
    if PY2:
        return the_obj
    return recursive_fix_pickle(the_obj, seen=set())

def fix_pickle_dict(the_dict):
    if PY2 or '_internal' in the_dict:
        return the_dict
    return recursive_fix_pickle(the_dict, seen=set())

def recursive_fix_pickle(the_object, seen):
    if isinstance(the_object, (string_types, bool, int, float, complex, NoneType, datetime.datetime, TypeType)):
        return the_object
    if isinstance(the_object, bytes):
        try:
            return the_object.decode()
        except:
            logmessage("Could not decode bytes " + repr(the_object))
            return the_object
    object_id = id(the_object)
    if object_id in seen:
        return the_object
    if isinstance(the_object, dict):
        new_dict = type(the_object)()
        for key, val in the_object.items():
            new_dict[recursive_fix_pickle(key, seen=seen)] = recursive_fix_pickle(val, seen=seen)
        seen.add(object_id)
        return new_dict
    if isinstance(the_object, list):
        new_list = type(the_object)()
        for item in the_object:
            new_list.append(recursive_fix_pickle(item, seen=seen))
        seen.add(object_id)
        return new_list
    if isinstance(the_object, set):
        new_set = type(the_object)()
        for item in the_object:
            new_set.add(recursive_fix_pickle(item, seen=seen))
        seen.add(object_id)
        return new_set
    the_object.__dict__ = dict((recursive_fix_pickle(k, seen=seen), recursive_fix_pickle(v, seen=seen)) for k, v in the_object.__dict__.items())
    seen.add(object_id)
    return the_object
