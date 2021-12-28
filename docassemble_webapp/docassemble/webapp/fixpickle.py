import datetime
import pickle
from docassemble.base.logger import logmessage
TypeType = type(type(None))
NoneType = type(None)

def fix_pickle_obj(data):
    try:
        return recursive_fix_pickle(pickle.loads(data, encoding="bytes", fix_imports=True), seen=set())
    except:
        return recursive_fix_pickle(pickle.loads(data, encoding="latin1", fix_imports=True), seen=set())

def fix_pickle_dict(the_dict):
    try:
        obj = pickle.loads(the_dict)
        assert '_internal' in obj
        return obj
    except:
        try:
            obj = pickle.loads(the_dict, encoding="bytes", fix_imports=True)
        except:
            obj = pickle.loads(the_dict, encoding="latin1", fix_imports=True)
        return recursive_fix_pickle(obj, seen=set())

def recursive_fix_pickle(the_object, seen):
    if isinstance(the_object, (str, bool, int, float, complex, NoneType, datetime.datetime, TypeType)):
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
    seen.add(object_id)
    if isinstance(the_object, dict):
        new_dict = type(the_object)()
        for key, val in the_object.items():
            new_dict[recursive_fix_pickle(key, seen=seen)] = recursive_fix_pickle(val, seen=seen)
        #seen.add(object_id)
        return new_dict
    if isinstance(the_object, list):
        new_list = type(the_object)()
        for item in the_object:
            new_list.append(recursive_fix_pickle(item, seen=seen))
        #seen.add(object_id)
        return new_list
    if isinstance(the_object, set):
        new_set = type(the_object)()
        for item in the_object:
            new_set.add(recursive_fix_pickle(item, seen=seen))
        #seen.add(object_id)
        return new_set
    if isinstance(the_object, tuple):
        new_list = []
        for item in the_object:
            new_list.append(recursive_fix_pickle(item, seen=seen))
        #seen.add(object_id)
        return type(the_object)(new_list)
    if hasattr(the_object, '__dict__'):
        try:
            the_object.__dict__ = dict((recursive_fix_pickle(k, seen=seen), recursive_fix_pickle(v, seen=seen)) for k, v in the_object.__dict__.items())
        except:
            pass
    #seen.add(object_id)
    return the_object
