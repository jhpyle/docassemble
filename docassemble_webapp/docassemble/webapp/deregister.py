# pylint: disable=wrong-import-position
import os
from sqlalchemy import delete
from docassemble.webapp.config import hostname
from docassemble.webapp.db import session_scope
from docassemble.webapp.main.models import Supervisors

def main():
    supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
    if supervisor_url:
        with session_scope() as session:
            session.execute(delete(Supervisors).filter_by(hostname=hostname))

if __name__ == "__main__":
    main()
