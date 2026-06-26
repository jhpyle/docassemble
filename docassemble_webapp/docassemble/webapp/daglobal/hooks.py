import re
from sqlalchemy import select, delete, or_, and_
from docassemble.webapp.daglobal.models import GlobalObjectStorage
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.utils.encryption import encrypt_object, decrypt_object
from docassemble.webapp.utils.logger import logmessage

@hookimpl
def manage_global_objects(mode, kwargs):
    if mode == 0:
        temp_user_id = int(kwargs['temp_user_id'])
        new_user_id = kwargs['new_user_id']
        oldsecret = kwargs.get('oldsecret', None)
        newsecret = kwargs.get('newsecret', None)
        keys_in_use = {}
        for object_entry in db.session.execute(select(GlobalObjectStorage.id, GlobalObjectStorage.key).filter(or_(GlobalObjectStorage.key.like('da:userid:{:d}:%'.format(new_user_id)), GlobalObjectStorage.key.like('da:daglobal:userid:{:d}:%'.format(new_user_id))))).all():
            if object_entry.key not in keys_in_use:
                keys_in_use[object_entry.key] = []
            keys_in_use[object_entry.key].append(object_entry.id)
        ids_to_delete = []
        for object_entry in db.session.execute(select(GlobalObjectStorage).filter_by(temp_user_id=temp_user_id).with_for_update()).scalars():
            object_entry.user_id = new_user_id
            object_entry.temp_user_id = None
            if object_entry.key.startswith('da:userid:t{:d}:'.format(temp_user_id)):
                new_key = re.sub(r'^da:userid:t{:d}:'.format(temp_user_id), 'da:userid:{:d}:'.format(new_user_id), object_entry.key)
                object_entry.key = new_key
                if new_key in keys_in_use:
                    ids_to_delete.extend(keys_in_use[new_key])
            if object_entry.encrypted and newsecret is not None:
                try:
                    object_entry.value = encrypt_object(decrypt_object(object_entry.value, oldsecret), newsecret)
                except BaseException as err:
                    logmessage("Failure to change encryption of object " + object_entry.key + ": " + str(err))
        for object_entry in db.session.execute(select(GlobalObjectStorage).filter(and_(GlobalObjectStorage.temp_user_id == None, GlobalObjectStorage.user_id == None, GlobalObjectStorage.key.like('da:daglobal:userid:t{:d}:%'.format(temp_user_id)))).with_for_update()).scalars():  # noqa: E711 # pylint: disable=singleton-comparison
            new_key = re.sub(r'^da:daglobal:userid:t{:d}:'.format(temp_user_id), 'da:daglobal:userid:{:d}:'.format(new_user_id), object_entry.key)
            object_entry.key = new_key
            if new_key in keys_in_use:
                ids_to_delete.extend(keys_in_use[new_key])
        for the_id in ids_to_delete:
            db.session.execute(delete(GlobalObjectStorage).filter_by(id=the_id))
        db.session.commit()
    elif mode == 1:
        temp_user_id = kwargs['temp_user_id']
        db.session.execute(delete(GlobalObjectStorage).where(GlobalObjectStorage.temp_user_id == temp_user_id))
        db.session.commit()
        db.session.execute(delete(GlobalObjectStorage).where(or_(GlobalObjectStorage.key.like('da:userid:t' + str(temp_user_id) + ':%'), GlobalObjectStorage.key.like('da:daglobal:userid:t' + str(temp_user_id) + ':%'))).execution_options(synchronize_session=False))
        db.session.commit()
    elif mode == 2:
        user_id = kwargs['user_id']
        db.session.execute(delete(GlobalObjectStorage).where(GlobalObjectStorage.user_id == user_id))
        db.session.commit()
        db.session.execute(delete(GlobalObjectStorage).where(or_(GlobalObjectStorage.key.like('da:userid:' + str(user_id) + ':%'), GlobalObjectStorage.key.like('da:daglobal:userid:' + str(user_id) + ':%'))).execution_options(synchronize_session=False))
        db.session.commit()
    elif mode == 3:
        key = kwargs['key']
        filename = kwargs['filename']
        db.session.execute(delete(GlobalObjectStorage).where(or_(GlobalObjectStorage.key.like('da:uid:' + key + ':i:' + filename + ':%'), GlobalObjectStorage.key.like('da:daglobal:uid:' + key + ':i:' + filename + ':%'))).execution_options(synchronize_session=False))
        db.session.commit()
    elif mode == 6:
        key = kwargs['key']
        filename = kwargs['filename']
        oldsecret = kwargs['oldsecret']
        newsecret = kwargs['newsecret']
        for object_entry in db.session.execute(select(GlobalObjectStorage).where(and_(GlobalObjectStorage.key.like('da:uid:' + key + ':i:' + filename + ':%'), GlobalObjectStorage.encrypted == True)).with_for_update()).scalars():  # noqa: E712 # pylint: disable=singleton-comparison
            try:
                object_entry.value = encrypt_object(decrypt_object(object_entry.value, oldsecret), newsecret)
            except:
                pass
        db.session.commit()
    elif mode == 7:
        user_id = kwargs['user_id']
        oldsecret = kwargs['oldsecret']
        newsecret = kwargs['newsecret']
        for object_entry in db.session.execute(select(GlobalObjectStorage).where(and_(GlobalObjectStorage.user_id == user_id, GlobalObjectStorage.encrypted == True)).with_for_update()).scalars():  # noqa: E712 # pylint: disable=singleton-comparison
            try:
                object_entry.value = encrypt_object(decrypt_object(object_entry.value, oldsecret), newsecret)
            except BaseException as err:
                logmessage("Failure to change encryption of object " + str(object_entry.key) + ": " + str(err))
        db.session.commit()
