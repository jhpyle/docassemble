import os
import sys
if __name__ == "__main__":
    import docassemble.webapp.config
    docassemble.webapp.config.load(arguments=sys.argv)
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.core.models import Supervisors
from docassemble.base.logger import logmessage

def main():
    from docassemble.webapp.config import hostname
    supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
    if supervisor_url:
        Supervisors.query.filter_by(hostname=hostname).delete()
        db.session.commit()

if __name__ == "__main__":
    import docassemble.webapp.database
    app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
    main()
