from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from docassemble.webapp.db_base import Base
from docassemble.webapp.config import daconfig
from docassemble.webapp.database import (
    alchemy_connection_string,
    connect_args,
    pool_pre_ping,
)

_SessionLocal = None  # pylint: disable=invalid-name

binds = {}

def _build_session_local():
    url = alchemy_connection_string()
    if url.startswith('postgresql'):
        the_connect_args = connect_args()
        engine_main = create_engine(url, client_encoding='utf8', connect_args=the_connect_args, pool_pre_ping=pool_pre_ping)
    else:
        engine_main = create_engine(url, pool_pre_ping=pool_pre_ping)
    engines = {None: engine_main}
    if daconfig.get('variables snapshot db'):
        import docassemble.webapp.user_database
        snapshot_url = docassemble.webapp.user_database.alchemy_url('variables snapshot db')
        snapshot_connect_args = docassemble.webapp.user_database.connect_args('variables snapshot db')
        engines['variables_snapshot'] = create_engine(snapshot_url, connect_args=snapshot_connect_args, pool_pre_ping=pool_pre_ping)
    for mapper in Base.registry.mappers:
        if not hasattr(mapper.class_, '__bind_key__'):
            continue
        bind_key = mapper.class_.__bind_key__
        if bind_key is None or bind_key not in engines:
            continue
        binds[mapper.class_] = engines[bind_key]
    return sessionmaker(bind=engine_main)

@contextmanager
def get_session():
    global _SessionLocal  # pylint: disable=global-statement
    if _SessionLocal is None:
        _SessionLocal = _build_session_local()
    dbsession = _SessionLocal()
    try:
        yield dbsession
    finally:
        dbsession.close()

@contextmanager
def session_scope():
    global _SessionLocal  # pylint: disable=global-statement
    if _SessionLocal is None:
        _SessionLocal = _build_session_local()
    with _SessionLocal.begin() as session:  # pylint: disable=no-member
        yield session
