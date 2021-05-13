from docassemble.base.config import daconfig
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, Text, DateTime, func, create_engine, or_, and_, true, false, delete, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql.json import JSONB
import sys
from docassemble.base.functions import server
import datetime

custom_db = daconfig.get('variables snapshot db', None)

if custom_db is None:
    from docassemble.webapp.core.models import JsonStorage
    import docassemble.webapp.db_object
    JsonDb = docassemble.webapp.db_object.db.session
    def variables_snapshot_connection():
        return docassemble.webapp.db_object.db.engine.raw_connection()
else:
    Base = declarative_base()

    url = server.alchemy_url('variables snapshot db')

    class JsonStorage(Base):
        __tablename__ = "jsonstorage"
        id = Column(Integer(), primary_key=True)
        filename = Column(String(255), index=True)
        key = Column(String(250), index=True)
        if url.startswith('postgresql'):
            data = Column(JSONB)
        else:
            data = Column(Text())
        tags = Column(Text())
        modtime = Column(DateTime(), server_default=func.now())
        persistent = Column(Boolean(), nullable=False, server_default=false())

    if url.startswith('postgres'):
        connect_args = server.connect_args('variables snapshot db')
        engine = create_engine(url, connect_args=connect_args, pool_pre_ping=daconfig.get('sql ping', False))
    else:
        engine = create_engine(url, pool_pre_ping=daconfig.get('sql ping', False))
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    JsonDb = sessionmaker(bind=engine)()

    def variables_snapshot_connection():
        return engine.raw_connection()
    
def read_answer_json(user_code, filename, tags=None, all_tags=False):
    if all_tags:
        entries = list()
        for entry in JsonDb.execute(select(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags)).scalars():
            entries.append(dict(data=entry.data, tags=entry.tags, modtime=entry.modtime))
        return entries
    existing_entry = JsonDb.execute(select(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags)).scalar()
    if existing_entry is not None:
        return existing_entry.data
    return None

def write_answer_json(user_code, filename, data, tags=None, persistent=False):
    existing_entry = JsonDb.execute(select(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags).with_for_update()).scalar()
    if existing_entry:
        existing_entry.data = data
        existing_entry.modtime = datetime.datetime.utcnow()
        existing_entry.persistent = persistent
    else:
        new_entry = JsonStorage(filename=filename, key=user_code, data=data, tags=tags, persistent=persistent)
        JsonDb.add(new_entry)
    JsonDb.commit()

def delete_answer_json(user_code, filename, tags=None, delete_all=False, delete_persistent=False):
    if delete_all:
        if delete_persistent:
            JsonDb.execute(delete(JsonStorage).filter_by(filename=filename, key=user_code))
        else:
            JsonDb.execute(delete(JsonStorage).filter_by(filename=filename, key=user_code, persistent=False))
    else:
        JsonDb.execute(delete(JsonStorage).filter_by(filename=filename, key=user_code, tags=tags))
    JsonDb.commit()
