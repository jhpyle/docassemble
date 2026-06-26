from sqlalchemy import select, delete
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.objectstore.models import ObjectStorage
from docassemble.webapp.utils.encryption import unpack_object, pack_object

@hookimpl
def write_record(key, data):
    new_record = ObjectStorage(key=key, value=pack_object(data))
    db.session.add(new_record)
    db.session.commit()
    return new_record.id


@hookimpl
def read_records(key):
    results = {}
    for record in db.session.execute(select(ObjectStorage).filter_by(key=key).order_by(ObjectStorage.id)).scalars():
        results[record.id] = unpack_object(record.value)
    return results


@hookimpl
def delete_record(key, the_id):
    db.session.execute(delete(ObjectStorage).filter_by(key=key, id=the_id))
    db.session.commit()
