import sys
import pip
import re
import docassemble.base.config
from docassemble.base.config import daconfig
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.functions import word
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.packages.models import Package, PackageAuth, Install
from docassemble.webapp.core.models import Attachments, Uploads, SpeakList, Supervisors#, KVStore
from docassemble.webapp.users.models import UserModel, UserAuthModel, Role, UserRoles, UserDict, UserDictKeys, TempUser, ChatLog # UserDictLock
from docassemble.webapp.update import get_installed_distributions
from sqlalchemy import create_engine, MetaData
import docassemble.webapp.database
import random
import string
from flask_user import UserManager, SQLAlchemyAdapter

if __name__ == "__main__":
    app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
    app.secret_key = daconfig.get('secretkey', '28ihfiFehfoU34mcq_4clirglw3g4o87')

def get_role(db, name):
    the_role = Role.query.filter_by(name=word(name)).first()
    if the_role:
        return the_role
    the_role = Role(name=word(name))
    db.session.add(the_role)
    return the_role

def get_user(db, role, defaults):
    the_user = UserModel.query.filter_by(nickname=word(defaults['nickname'])).first()
    if the_user:
        return the_user
    user_auth = UserAuthModel(password=app.user_manager.hash_password(defaults.get('password', 'password')))
    the_user = UserModel(
        active=defaults.get('active', True),
        nickname=defaults['nickname'],
        social_id='local$' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32)),
        email=defaults['email'],
        user_auth=user_auth,
        first_name = defaults.get('first_name', ''),
        last_name = defaults.get('last_name', ''),
        country = defaults.get('country', ''),
        subdivisionfirst = defaults.get('subdivisionfirst', ''),
        subdivisionsecond = defaults.get('subdivisionsecond', ''),
        subdivisionthird = defaults.get('subdivisionthird', ''),
        organization = defaults.get('organization', '')
    )
    the_user.roles.append(role)
    db.session.add(user_auth)
    db.session.add(the_user)
    return the_user

def populate_tables():
    user_manager = UserManager(SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel), app)
    admin_defaults = daconfig.get('default_admin_account', {'nickname': 'admin', 'email': 'admin@admin.com', 'first_name': 'System', 'last_name': 'Administrator'})
    cron_defaults = daconfig.get('default_cron_account', {'nickname': 'cron', 'email': 'cron@admin.com', 'first_name': 'Cron', 'last_name': 'User'})
    cron_defaults['active'] = False
    admin_role = get_role(db, 'admin')
    user_role = get_role(db, 'user')
    developer_role = get_role(db, 'developer')
    advocate_role = get_role(db, 'advocate')
    cron_role = get_role(db, 'cron')
    admin = get_user(db, admin_role, admin_defaults)
    cron = get_user(db, cron_role, cron_defaults)
    db.session.commit()
    docassemble_git_url = daconfig.get('docassemble_git_url', 'https://github.com/jhpyle/docassemble')
    installed_packages = sorted(get_installed_distributions())
    package_auth = PackageAuth.query.filter_by(user_id=admin.id).first()
    if not package_auth:
        package_auth = PackageAuth(user_id=admin.id)
    existing_packages = [package.name for package in Package.query.all()]
    for package in installed_packages:
        if package in existing_packages:
            continue
        if package.key in ['docassemble', 'docassemble.base', 'docassemble.webapp', 'docassemble.demo']:
            package_entry = Package(name=package.key, package_auth=package_auth, giturl=docassemble_git_url, packageversion=package.version, gitsubdir=re.sub(r'\.', '_', package.key), type='git', core=True)
        else:
            package_entry = Package(name=package.key, package_auth=package_auth, packageversion=package.version, type='pip', core=True)
        db.session.add(package_auth)
        db.session.add(package_entry)
    db.session.commit()
    return

if __name__ == "__main__":
    #db.drop_all()
    db.create_all()
    populate_tables()
    db.engine.dispose()
