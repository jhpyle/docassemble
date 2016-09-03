import os
import sys
import re
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.core.models import Supervisors

def main():
    from docassemble.base.config import hostname, S3_ENABLED, s3_config
    supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
    if supervisor_url:
        Supervisors.query.filter_by(hostname=hostname).delete()
        db.session.commit()
    roles = os.environ.get('CONTAINERROLE', None)
    if S3_ENABLED and roles is not None:
        import docassemble.webapp.amazon
        s3 = docassemble.webapp.amazon.s3object(s3_config)
        roles = re.sub(r'^:+|:+$', r'', roles)
        role_list = roles.split(":")
        if 'all' in role_list:
            role_list = ['sql', 'log', 'redis', 'rabbitmq']
        for role in role_list:
            if role in ['sql', 'log', 'redis', 'rabbitmq']:
                key = s3.get_key('hostname-' + role)
                if key.exists():
                    key.delete()

if __name__ == "__main__":
    import docassemble.webapp.database
    app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
    main()
