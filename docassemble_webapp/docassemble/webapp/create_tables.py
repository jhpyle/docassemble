import random
import string
import sys
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.user import UserManager, SQLAlchemyAdapter
from docassemble.base.util import word
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.packages.models import Package, PackageAuth
from docassemble.webapp.users.models import User, UserAuth, Role, UserRoles, UserDict, UserDictLock, Attachments, Uploads, KVStore, Ticket, TicketNote
from sqlalchemy import create_engine, MetaData
import docassemble.webapp.config
from docassemble.webapp.config import daconfig
if len(sys.argv) > 1:
    yaml_config = sys.argv[1]
else:
    yaml_config = '/etc/docassemble/config.yml'
docassemble.webapp.config.load(filename=yaml_config)
import docassemble.webapp.database

app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
app.secret_key = daconfig.get('secretkey','28ihfiFehfoU34mcq_4clirglw3g4o87')

def populate_tables():
    defaults = daconfig.get('default_admin_account', {'nickname': 'admin', 'email': 'admin@admin.com', 'password': 'password'})
    admin_role = Role(name=word('admin'))
    user_role = Role(name=word('user'))
    developer_role = Role(name=word('developer'))
    advocate_role = Role(name=word('advocate'))
    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.add(developer_role)
    db.session.add(advocate_role)
    user_manager = UserManager(SQLAlchemyAdapter(db, User, UserAuthClass=UserAuth), app)
    user_auth = UserAuth(password=app.user_manager.hash_password(defaults['password']))
    user = User(
        active=True,
        nickname=defaults['nickname'],
        social_id='local$' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32)),
        email=defaults['email'],
        user_auth=user_auth
    )
    user.roles.append(admin_role)
    db.session.add(user_auth)
    db.session.add(user)
    db.session.commit()
    return

if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    populate_tables()
