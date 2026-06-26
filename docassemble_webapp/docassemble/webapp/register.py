import os

def main():
    supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
    if supervisor_url:
        from sqlalchemy import delete
        from docassemble.webapp.config import hostname
        from docassemble.webapp.db import session_scope
        from docassemble.webapp.main.models import Supervisors
        with session_scope() as session:
            session.execute(delete(Supervisors).filter_by(hostname=hostname))
        with session_scope() as session:
            new_entry = Supervisors(hostname=hostname, url="http://" + hostname + ":9001", role=os.environ.get('CONTAINERROLE', None))
            session.add(new_entry)

if __name__ == "__main__":
    main()
