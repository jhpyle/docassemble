from six import string_types, text_type, PY2
import datetime
TypeType = type(type(None))
NoneType = type(None)
from docassemble.base.logger import logmessage
if PY2:
    import cPickle as pickle
    FileType = file
else:
    import pickle
    from io import IOBase as FileType

def fix_pickle_obj(data):
    if PY2:
        return pickle.loads(data)
    return recursive_fix_pickle(pickle.loads(data, encoding="bytes", fix_imports=True), seen=set())

def fix_pickle_dict(the_dict):
    if PY2:
        return pickle.loads(the_dict)
    try:
        obj = pickle.loads(the_dict)
        assert '_internal' in obj
        return obj
    except:
        obj = pickle.loads(the_dict, encoding="bytes", fix_imports=True)
        return recursive_fix_pickle(obj, seen=set())

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
    if isinstance(the_object, tuple):
        new_list = list()
        for item in the_object:
            new_list.append(recursive_fix_pickle(item, seen=seen))
        seen.add(object_id)
        return type(the_object)(new_list)
    the_object.__dict__ = dict((recursive_fix_pickle(k, seen=seen), recursive_fix_pickle(v, seen=seen)) for k, v in the_object.__dict__.items())
    seen.add(object_id)
    return the_object
