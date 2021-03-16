import sys
import re
import datetime
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig
from docassemble.base.functions import word
from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.webapp.users.models import UserModel, UserAuthModel, Role, UserDict, UserDictKeys, ChatLog
from docassemble.webapp.core.models import Uploads, ObjectStorage, SpeakList, Shortener, MachineLearning, GlobalObjectStorage, JsonStorage

import docassemble.webapp.core.models
from docassemble.webapp.packages.models import Package
from docassemble.webapp.update import add_dependencies
from sqlalchemy import create_engine, MetaData
#import random
#import string
from docassemble.base.generate_key import random_alphanumeric
from docassemble_flask_user import UserManager, SQLAlchemyAdapter
import pkg_resources
import os
from docassemble.webapp.database import alchemy_connection_string, connect_args, dbtableprefix
import time

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

def populate_tables(start_time=None):
    if start_time is None:
        start_time = time.time()
    sys.stderr.write("populate_tables: starting after " + str(time.time() - start_time) + "\n")
    user_manager = UserManager(SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel), app)
    admin_defaults = daconfig.get('default admin account', dict())
    if 'email' not in admin_defaults:
        admin_defaults['email'] = os.getenv('DA_ADMIN_EMAIL', 'admin@admin.com')
    if 'nickname' not in admin_defaults:
        admin_defaults['nickname'] = 'admin'
    if 'first_name' not in admin_defaults:
        admin_defaults['first_name'] = word('System')
    if 'last_name' not in admin_defaults:
        admin_defaults['last_name'] = word('Administrator')
    if 'password' not in admin_defaults:
        admin_defaults['password'] = os.getenv('DA_ADMIN_PASSWORD', 'password')
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
    add_dependencies(admin.id, start_time=start_time)
    git_packages = Package.query.filter_by(type='git')
    for package in git_packages:
        if package.name in ['docassemble', 'docassemble.base', 'docassemble.webapp', 'docassemble.demo']:
            package.giturl = None
            package.gitsubdir = None
            package.type = 'pip'
            if daconfig.get('stable version', False):
                package.limitation = '<1.1.0'
            db.session.commit()
    sys.stderr.write("populate_tables: ending after " + str(time.time() - start_time) + "\n")
    return

def main():
    from docassemble.webapp.database import dbprefix
    if dbprefix.startswith('postgresql') and not daconfig.get('force text to varchar upgrade', False):
        do_varchar_upgrade = False
    else:
        do_varchar_upgrade = True
    with app.app_context():
        if daconfig.get('use alembic', True):
            if do_varchar_upgrade:
                changed = False
                if db.engine.has_table(dbtableprefix + 'userdict'):
                    db.session.query(UserDict).filter(db.func.length(UserDict.filename) > 255).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'userdictkeys'):
                    db.session.query(UserDictKeys).filter(db.func.length(UserDictKeys.filename) > 255).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'chatlog'):
                    db.session.query(ChatLog).filter(db.func.length(ChatLog.filename) > 255).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'uploads'):
                    db.session.query(Uploads).filter(db.func.length(Uploads.filename) > 255).delete(synchronize_session=False)
                    db.session.query(Uploads).filter(db.func.length(Uploads.yamlfile) > 255).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'objectstorage'):
                    db.session.query(ObjectStorage).filter(db.func.length(ObjectStorage.key) > 1024).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'speaklist'):
                    db.session.query(SpeakList).filter(db.func.length(SpeakList.filename) > 255).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'shortener'):
                    db.session.query(Shortener).filter(db.func.length(Shortener.filename) > 255).delete(synchronize_session=False)
                    db.session.query(Shortener).filter(db.func.length(Shortener.key) > 255).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'machinelearning'):
                    db.session.query(MachineLearning).filter(db.func.length(MachineLearning.key) > 1024).delete(synchronize_session=False)
                    db.session.query(MachineLearning).filter(db.func.length(MachineLearning.group_id) > 1024).delete(synchronize_session=False)
                    changed = True
                if db.engine.has_table(dbtableprefix + 'globalobjectstorage'):
                    db.session.query(GlobalObjectStorage).filter(db.func.length(GlobalObjectStorage.key) > 1024).delete(synchronize_session=False)
                    changed = True
                if changed:
                    db.session.commit()
            packagedir = pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.webapp'), 'docassemble/webapp')
            if not os.path.isdir(packagedir):
                sys.exit("path for running alembic could not be found")
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config(os.path.join(packagedir, 'alembic.ini'))
            alembic_cfg.set_main_option("sqlalchemy.url", alchemy_connection_string())
            alembic_cfg.set_main_option("script_location", os.path.join(packagedir, 'alembic'))
            if not db.engine.has_table(dbtableprefix + 'alembic_version'):
                start_time = time.time()
                sys.stderr.write("Creating alembic stamp\n")
                command.stamp(alembic_cfg, "head")
                sys.stderr.write("Done creating alembic stamp after " + str(time.time() - start_time) + " seconds\n")
            if db.engine.has_table(dbtableprefix + 'user'):
                start_time = time.time()
                sys.stderr.write("Creating alembic stamp\n")
                sys.stderr.write("Running alembic upgrade\n")
                command.upgrade(alembic_cfg, "head")
                sys.stderr.write("Done running alembic upgrade after " + str(time.time() - start_time) + " seconds\n")
        #db.drop_all()
        start_time = time.time()
        try:
            sys.stderr.write("Trying to create tables\n")
            db.create_all()
        except:
            sys.stderr.write("Error trying to create tables; trying a second time.\n")
            try:
                db.create_all()
            except:
                sys.stderr.write("Error trying to create tables; trying a third time.\n")
                db.create_all()
        sys.stderr.write("Finished creating tables after " + str(time.time() - start_time) + " seconds.\n")
        populate_tables(start_time=start_time)
        db.engine.dispose()

if __name__ == "__main__":
    main()
