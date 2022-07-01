import os
import sys
from sqlalchemy import delete
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import hostname
from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.webapp.core.models import Supervisors

def main():
    supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
    if supervisor_url:
        db.session.execute(delete(Supervisors).filter_by(hostname=hostname))
        db.session.commit()

if __name__ == "__main__":
    #import docassemble.webapp.database
    with app.app_context():
        #app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
        main()
        db.engine.dispose()
