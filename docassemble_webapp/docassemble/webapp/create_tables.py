import sys
#import pip
import re
import datetime
#import subprocess
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig
from docassemble.base.functions import word
from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.webapp.packages.models import Package, PackageAuth, Install
from docassemble.webapp.core.models import Attachments, Uploads, SpeakList, Supervisors
from docassemble.webapp.users.models import UserModel, UserAuthModel, Role, UserRoles, UserDict, UserDictKeys, TempUser, ChatLog
from docassemble.webapp.update import get_installed_distributions, add_dependencies
from sqlalchemy import create_engine, MetaData
#import random
#import string
from docassemble.base.generate_key import random_alphanumeric
from flask_user import UserManager, SQLAlchemyAdapter
import pkg_resources
import os
from docassemble.webapp.database import alchemy_connection_string, dbtableprefix

def get_role(db, name):
    the_role = Role.query.filter_by(name=name).first()
    if the_role:
        return the_role
    the_role = Role(name=name)
    db.session.add(the_role)
    db.session.commit()
    return the_role

def get_user(db, role, defaults):
    while True:
        new_social = 'local$' + random_alphanumeric(32)
        existing_user = UserModel.query.filter_by(social_id=new_social).first()
        if existing_user:
            continue
        break
    the_user = UserModel.query.filter_by(nickname=defaults['nickname']).first()
    if the_user:
        return the_user
    user_auth = UserAuthModel(password=app.user_manager.hash_password(defaults.get('password', 'password')))
    the_user = UserModel(
        active=defaults.get('active', True),
        nickname=defaults['nickname'],
        social_id=new_social,
        email=defaults['email'],
        user_auth=user_auth,
        first_name = defaults.get('first_name', ''),
        last_name = defaults.get('last_name', ''),
        country = defaults.get('country', ''),
        subdivisionfirst = defaults.get('subdivisionfirst', ''),
        subdivisionsecond = defaults.get('subdivisionsecond', ''),
        subdivisionthird = defaults.get('subdivisionthird', ''),
        organization = defaults.get('organization', ''),
        confirmed_at = datetime.datetime.now()
    )
    the_user.roles.append(role)
    db.session.add(user_auth)
    db.session.add(the_user)
    db.session.commit()
    return the_user

def populate_tables():
    user_manager = UserManager(SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel), app)
    admin_defaults = daconfig.get('default admin account', dict())
    if 'email' not in admin_defaults:
        admin_defaults['email'] = 'admin@admin.com'
    if 'nickname' not in admin_defaults:
        admin_defaults['nickname'] = 'admin'
    if 'first_name' not in admin_defaults:
        admin_defaults['first_name'] = word('System')
    if 'last_name' not in admin_defaults:
        admin_defaults['last_name'] = word('Administrator')
    cron_defaults = daconfig.get('default cron account', {'nickname': 'cron', 'email': 'cron@admin.com', 'first_name': 'Cron', 'last_name': 'User'})
    cron_defaults['active'] = False
    user_role = get_role(db, 'user')
    admin_role = get_role(db, 'admin')
    cron_role = get_role(db, 'cron')
    customer_role = get_role(db, 'customer')
    developer_role = get_role(db, 'developer')
    advocate_role = get_role(db, 'advocate')
    trainer_role = get_role(db, 'trainer')
    for user in UserModel.query.all():
        if len(user.roles) == 0:
            user.roles.append(user_role)
            db.session.commit()
    admin = get_user(db, admin_role, admin_defaults)
    cron = get_user(db, cron_role, cron_defaults)
    if admin.confirmed_at is None:
        admin.confirmed_at = datetime.datetime.now()
    if cron.confirmed_at is None:
        cron.confirmed_at = datetime.datetime.now()
    db.session.commit()
    add_dependencies(admin.id)
    git_packages = Package.query.filter_by(type='git')
    for package in git_packages:
        if package.name in ['docassemble', 'docassemble.base', 'docassemble.webapp', 'docassemble.demo']:
            package.giturl = None
            package.gitsubdir = None
            package.type = 'pip'
            db.session.commit()
    # docassemble_git_url = daconfig.get('docassemble git url', 'https://github.com/jhpyle/docassemble')
    # installed_packages = get_installed_distributions()
    # existing_packages = [package.name for package in Package.query.all()]
    # for package in installed_packages:
    #     if package.key in existing_packages:
    #         continue
    #     package_auth = PackageAuth(user_id=admin.id)
    #     if package.key in ['docassemble', 'docassemble.base', 'docassemble.webapp', 'docassemble.demo']:
    #         package_entry = Package(name=package.key, package_auth=package_auth, giturl=docassemble_git_url, packageversion=package.version, gitsubdir=re.sub(r'\.', '_', package.key), type='git', core=True)
    #     else:
    #         package_entry = Package(name=package.key, package_auth=package_auth, packageversion=package.version, type='pip', core=True)
    #     db.session.add(package_auth)
    #     db.session.add(package_entry)
    return

def main():
    with app.app_context():
        if daconfig.get('use alembic', True):
            packagedir = pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.webapp'), 'docassemble/webapp')
            if not os.path.isdir(packagedir):
                sys.exit("path for running alembic could not be found")
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config(os.path.join(packagedir, 'alembic.ini'))
            alembic_cfg.set_main_option("sqlalchemy.url", alchemy_connection_string())
            alembic_cfg.set_main_option("script_location", os.path.join(packagedir, 'alembic'))
            if not db.engine.has_table(dbtableprefix + 'alembic_version'):
                command.stamp(alembic_cfg, "head")
            if db.engine.has_table(dbtableprefix + 'user'):
                command.upgrade(alembic_cfg, "head")
        #db.drop_all()
        db.create_all()
        populate_tables()
        db.engine.dispose()

if __name__ == "__main__":
    main()
