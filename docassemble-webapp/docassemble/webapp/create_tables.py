from docassemble.webapp.interviews.models import Interview
import docassemble.webapp.database 
from sqlalchemy import create_engine, MetaData

alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()

engine = create_engine(alchemy_connect_string, convert_unicode=True)

meta = MetaData(bind=engine)

meta.drop_all()

meta.create_all()

result = engine.execute('grant all on interview to "www-data"')
