import os
import sys
import re
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.webapp.core.models import Supervisors

def main():
    from docassemble.base.config import hostname
    supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
    if supervisor_url:
        Supervisors.query.filter_by(hostname=hostname).delete()
        db.session.commit()
        new_entry = Supervisors(hostname=hostname, url="http://" + hostname + ":9001", role=os.environ.get('CONTAINERROLE', None))
        db.session.add(new_entry)
        db.session.commit()

if __name__ == "__main__":
    #import docassemble.webapp.database
    with app.app_context():
        #app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
        main()
        db.engine.dispose()

