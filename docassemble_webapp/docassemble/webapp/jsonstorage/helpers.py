import datetime
from sqlalchemy import false, delete, select, func
from sqlalchemy.dialects.postgresql.json import JSONB
from docassemble.webapp.config import daconfig
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from .models import JsonStorage as CoreJsonStorage

custom_db = daconfig.get('variables snapshot db', None)

if custom_db is None:
    JsonStorage = CoreJsonStorage

    @hookimpl
    def variables_snapshot_connection():
        return db.engine.raw_connection()

    @hookimpl
    def variables_snapshot_connect():
        return db.engine.connect()
else:
    import docassemble.webapp.user_database  # pylint: disable=ungrouped-imports
    _snapshot_url = docassemble.webapp.user_database.alchemy_url('variables snapshot db')

    class JsonStorage(db.Model):
        __tablename__ = "jsonstorage"
        __bind_key__ = 'variables_snapshot'
        id = db.Column(db.Integer(), primary_key=True)
        filename = db.Column(db.String(255), index=True)
        key = db.Column(db.String(250), index=True)
        if _snapshot_url.startswith('postgresql'):
            data = db.Column(JSONB)
        else:
            data = db.Column(db.Text())
        tags = db.Column(db.Text())
        modtime = db.Column(db.DateTime(), server_default=func.now())  # pylint: disable=not-callable
        persistent = db.Column(db.Boolean(), nullable=False, server_default=false())

    @hookimpl
    def variables_snapshot_connection():
        return db.engines['variables_snapshot'].raw_connection()

    @hookimpl
    def variables_snapshot_connect():
        return db.engines['variables_snapshot'].connect()

@hookimpl
def read_answer_json(user_code, filename, tags, all_tags):
    if all_tags:
        entries = []
        for entry in db.session.execute(select(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags)).scalars():
            entries.append({'data': entry.data, 'tags': entry.tags, 'modtime': entry.modtime})
        return entries
    existing_entry = db.session.execute(select(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags)).scalar()
    if existing_entry is not None:
        return existing_entry.data
    return None

@hookimpl
def write_answer_json(user_code, filename, data, tags, persistent):
    existing_entry = db.session.execute(select(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags).with_for_update()).scalar()
    if existing_entry:
        existing_entry.data = data
        existing_entry.modtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        existing_entry.persistent = persistent
    else:
        new_entry = JsonStorage(filename=filename, key=user_code, data=data, tags=tags, persistent=persistent, modtime=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
        db.session.add(new_entry)
    db.session.commit()


@hookimpl
def delete_answer_json(user_code, filename, tags, delete_all, delete_persistent):
    if delete_all:
        if delete_persistent:
            db.session.execute(delete(JsonStorage).filter_by(filename=filename, key=user_code))
        else:
            db.session.execute(delete(JsonStorage).filter_by(filename=filename, key=user_code, persistent=False))
    else:
        db.session.execute(delete(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags))
    db.session.commit()


def create_custom_tables(app):
    if custom_db is None:
        return
    with app.app_context():
        db.create_all(bind_key='variables_snapshot')
