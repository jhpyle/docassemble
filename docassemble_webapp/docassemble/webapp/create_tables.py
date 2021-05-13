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
from sqlalchemy import create_engine, MetaData, select, delete, inspect
#import random
#import string
from docassemble.base.generate_key import random_alphanumeric
from docassemble_flask_user import UserManager, SQLAlchemyAdapter
import pkg_resources
import os
from docassemble.webapp.database import alchemy_connection_string, connect_args, dbtableprefix
import time
import sys

def get_role(db, name, result=None):
    if result is None:
        result = dict()
    the_role = db.session.execute(select(Role).filter_by(name=name)).first()
    if the_role:
        return the_role
    the_role = Role(name=name)
    db.session.add(the_role)
    db.session.commit()
    result['changed'] = True
    return the_role

def get_user(db, role, defaults, result=None):
    if result is None:
        result = dict()
    the_user = db.session.execute(select(UserModel).filter_by(nickname=defaults['nickname'])).scalar()
    if the_user:
        return the_user
    while True:
        new_social = 'local$' + random_alphanumeric(32)
        existing_user = db.session.execute(select(UserModel).filter_by(social_id=new_social)).scalar()
        if existing_user:
            continue
        break
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
    result['changed'] = True
    return the_user

def populate_tables(start_time=None):
    if start_time is None:
        start_time = time.time()
    sys.stderr.write("create_tables.populate_tables: starting after " + str(time.time() - start_time) + "\n")
    user_manager = UserManager(SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel), app)
    sys.stderr.write("create_tables.populate_tables: obtained user_manager after " + str(time.time() - start_time) + "\n")
    result = dict()
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
    user_role = get_role(db, 'user', result=result)
    admin_role = get_role(db, 'admin', result=result)
    cron_role = get_role(db, 'cron', result=result)
    customer_role = get_role(db, 'customer', result=result)
    developer_role = get_role(db, 'developer', result=result)
    advocate_role = get_role(db, 'advocate', result=result)
    trainer_role = get_role(db, 'trainer', result=result)
    if daconfig.get('fix user roles', False):
        sys.stderr.write("create_tables.populate_tables: fixing user roles after " + str(time.time() - start_time) + "\n")
        to_fix = []
        for user in db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles))).scalars():
            if len(user.roles) == 0:
                to_fix.append(user)
        if len(to_fix):
            sys.stderr.write("create_tables.populate_tables: found user roles to fix after " + str(time.time() - start_time) + "\n")
            for user in to_fix:
                user.roles.append(user_role)
            db.session.commit()
        sys.stderr.write("create_tables.populate_tables: done fixing user roles after " + str(time.time() - start_time) + "\n")
    admin = get_user(db, admin_role, admin_defaults, result=result)
    cron = get_user(db, cron_role, cron_defaults, result=result)
    if admin.confirmed_at is None:
        admin.confirmed_at = datetime.datetime.now()
    if cron.confirmed_at is None:
        cron.confirmed_at = datetime.datetime.now()
    if result.get('changed', False):
        db.session.commit()
    sys.stderr.write("create_tables.populate_tables: calling add_dependencies after " + str(time.time() - start_time) + "\n")
    add_dependencies(admin.id, start_time=start_time)
    sys.stderr.write("create_tables.populate_tables: add_dependencies finished after " + str(time.time() - start_time) + "\n")
    git_packages = db.session.execute(select(Package).filter_by(type='git')).scalars().all()
    package_info_changed = False
    for package in git_packages:
        if package.name in ['docassemble', 'docassemble.base', 'docassemble.webapp', 'docassemble.demo']:
            if package.giturl:
                package.giturl = None
                package_info_changed = True
            if package.gitsubdir:
                package.gitsubdir = None
                package_info_changed = True
            if package.type != 'pip':
                package.type = 'pip'
                package_info_changed = True
            if daconfig.get('stable version', False):
                if package.limitation != '<1.1.0':
                    package.limitation = '<1.1.0'
                    package_info_changed = True
    if package_info_changed:
        db.session.commit()
    sys.stderr.write("create_tables.populate_tables: ending after " + str(time.time() - start_time) + "\n")
    return

def main():
    sys.stderr.write("create_tables.main: starting\n")
    start_time = time.time()
    from docassemble.webapp.database import dbprefix
    if dbprefix.startswith('postgresql') and not daconfig.get('force text to varchar upgrade', False):
        do_varchar_upgrade = False
    else:
        do_varchar_upgrade = True
    with app.app_context():
        sys.stderr.write("create_tables.main: inside app context after " + str(time.time() - start_time) + "\n")
        if daconfig.get('use alembic', True):
            sys.stderr.write("create_tables.main: running alembic after " + str(time.time() - start_time) + "\n")
            insp = inspect(db.engine)
            if do_varchar_upgrade:
                changed = False
                if insp.has_table(dbtableprefix + 'userdict'):
                    db.session.execute(delete(UserDict).where(db.func.length(UserDict.filename) > 255).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'userdictkeys'):
                    db.session.execute(delete(UserDictKeys).where(db.func.length(UserDictKeys.filename) > 255).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'chatlog'):
                    db.session.execute(delete(ChatLog).where(db.func.length(ChatLog.filename) > 255).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'uploads'):
                    db.session.execute(delete(Uploads).where(db.func.length(Uploads.filename) > 255).execution_options(synchronize_session=False))
                    db.session.execute(delete(Uploads).where(db.func.length(Uploads.yamlfile) > 255).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'objectstorage'):
                    db.session.execute(delete(ObjectStorage).where(db.func.length(ObjectStorage.key) > 1024).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'speaklist'):
                    db.session.execute(delete(SpeakList).where(db.func.length(SpeakList.filename) > 255).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'shortener'):
                    db.session.execute(delete(Shortener).where(db.func.length(Shortener.filename) > 255).execution_options(synchronize_session=False))
                    db.session.execute(delete(Shortener).where(db.func.length(Shortener.key) > 255).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'machinelearning'):
                    db.session.execute(delete(MachineLearning).where(db.func.length(MachineLearning.key) > 1024).execution_options(synchronize_session=False))
                    db.session.execute(delete(MachineLearning).where(db.func.length(MachineLearning.group_id) > 1024).execution_options(synchronize_session=False))
                    changed = True
                if insp.has_table(dbtableprefix + 'globalobjectstorage'):
                    db.session.execute(delete(GlobalObjectStorage).where(db.func.length(GlobalObjectStorage.key) > 1024).execution_options(synchronize_session=False))
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
            if not insp.has_table(dbtableprefix + 'alembic_version'):
                sys.stderr.write("create_tables.main: creating alembic stamp\n")
                command.stamp(alembic_cfg, "head")
                sys.stderr.write("create_tables.main: done creating alembic stamp after " + str(time.time() - start_time) + " seconds\n")
            if insp.has_table(dbtableprefix + 'user'):
                sys.stderr.write("create_tables.main: creating alembic stamp\n")
                sys.stderr.write("create_tables.main: running alembic upgrade\n")
                command.upgrade(alembic_cfg, "head")
                sys.stderr.write("create_tables.main: done running alembic upgrade after " + str(time.time() - start_time) + " seconds\n")
        #db.drop_all()
        try:
            sys.stderr.write("create_tables.main: trying to create tables\n")
            db.create_all()
        except:
            sys.stderr.write("create_tables.main: error trying to create tables; trying a second time.\n")
            try:
                db.create_all()
            except:
                sys.stderr.write("create_tables.main: error trying to create tables; trying a third time.\n")
                db.create_all()
        sys.stderr.write("create_tables.main: finished creating tables after " + str(time.time() - start_time) + " seconds.\n")
        populate_tables(start_time=start_time)
        db.engine.dispose()

if __name__ == "__main__":
    main()
