from sqlalchemy import select, delete
from docassemble.base.error import DAException
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.utils.encryption import (
    encrypt_object,
    pack_object,
    unpack_object,
    decrypt_object,
)
from docassemble.webapp.utils.helpers import parse_the_user_id
from .models import GlobalObjectStorage

@hookimpl(specname="server_sql_get")
def sql_get(key, secret):
    for record in db.session.execute(select(GlobalObjectStorage).filter_by(key=key)).scalars():
        if record.encrypted:
            try:
                result = decrypt_object(record.value, secret)
            except Exception as err:
                raise DAException("Unable to decrypt stored object") from err
        else:
            try:
                result = unpack_object(record.value)
            except Exception as err:
                raise DAException("Unable to unpack stored object") from err
        return result
    return None

@hookimpl(specname="server_sql_defined")
def sql_defined(key):
    record = db.session.execute(select(GlobalObjectStorage.id).filter_by(key=key)).first()
    if record is None:
        return False
    return True

@hookimpl(specname="server_sql_set")
def sql_set(key, val, encrypted, secret, the_user_id):
    user_id, temp_user_id = parse_the_user_id(the_user_id)
    updated = False
    for record in db.session.execute(select(GlobalObjectStorage).filter_by(key=key).with_for_update()).scalars():
        record.user_id = user_id
        record.temp_user_id = temp_user_id
        record.encrypted = encrypted
        if encrypted:
            record.value = encrypt_object(val, secret)
        else:
            record.value = pack_object(val)
        updated = True
    if not updated:
        if encrypted:
            record = GlobalObjectStorage(key=key, value=encrypt_object(val, secret), encrypted=True, user_id=user_id, temp_user_id=temp_user_id)
        else:
            record = GlobalObjectStorage(key=key, value=pack_object(val), encrypted=False, user_id=user_id, temp_user_id=temp_user_id)
        db.session.add(record)
    db.session.commit()

@hookimpl(specname="server_sql_delete")
def sql_delete(key):
    db.session.execute(delete(GlobalObjectStorage).filter_by(key=key))
    db.session.commit()

@hookimpl(specname="server_sql_keys")
def sql_keys(prefix):
    n = len(prefix)
    stmt = select(GlobalObjectStorage.key).where(GlobalObjectStorage.key.like(prefix + '%'))
    return list(set(y.key[n:] for y in db.session.execute(stmt)))
