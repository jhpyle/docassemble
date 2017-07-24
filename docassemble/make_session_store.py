from simplekv.db.sql import SQLAlchemyStore
from sqlalchemy import create_engine, MetaData

session_store = 'postgresql+psycopg2://:@/docassembly'

engine = create_engine(session_store, echo=True)

metadata = MetaData(bind=engine)

store = SQLAlchemyStore(engine, metadata, 'kvstore')

metadata.create_all()

