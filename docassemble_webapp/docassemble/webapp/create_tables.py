import sys
import os
import time
import datetime
import importlib.resources
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig
from docassemble.base.functions import word
from docassemble.base.generate_key import random_alphanumeric
from docassemble.base.logger import logmessage
from docassemble.webapp.app_object import app
from docassemble.webapp.core.models import Uploads, ObjectStorage, SpeakList, Shortener, MachineLearning, GlobalObjectStorage
from docassemble.webapp.database import alchemy_connection_string, dbtableprefix
from docassemble.webapp.db_object import db
from docassemble.webapp.packages.models import Package
from docassemble.webapp.update import add_dependencies
from docassemble.webapp.users.models import UserModel, UserAuthModel, Role, UserDict, UserDictKeys, ChatLog, TempUser, MyUserInvitation, UserRoles
from docassemble.webapp.database import dbprefix
import docassemble.webapp.core.models
import docassemble.webapp.packages.models
from docassemble.webapp.api_key import add_specific_api_key
from sqlalchemy import select, delete, inspect
from sqlalchemy.sql import text
# import random
# import string
from docassemble_flask_user import UserManager, SQLAlchemyAdapter
from alembic.config import Config
from alembic import command


def get_role(the_db, name, result=None):
    if result is None:
        result = {}
    the_role = the_db.session.execute(select(Role).filter_by(name=name)).scalar()
    if the_role:
        return the_role
    the_role = Role(name=name)
    the_db.session.add(the_role)
    the_db.session.commit()
    result['changed'] = True
    return the_role


def get_user(the_db, role, defaults, result=None):
    if result is None:
        result = {}
    the_user = the_db.session.execute(select(UserModel).filter_by(nickname=defaults['nickname'])).scalar()
    if the_user:
        return the_user
    while True:
        new_social = 'local$' + random_alphanumeric(32)
        existing_user = the_db.session.execute(select(UserModel).filter_by(social_id=new_social)).scalar()
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
        first_name=defaults.get('first_name', ''),
        last_name=defaults.get('last_name', ''),
        country=defaults.get('country', ''),
        subdivisionfirst=defaults.get('subdivisionfirst', ''),
        subdivisionsecond=defaults.get('subdivisionsecond', ''),
        subdivisionthird=defaults.get('subdivisionthird', ''),
        organization=defaults.get('organization', ''),
        confirmed_at=datetime.datetime.now()
    )
    the_user.roles.append(role)
    the_db.session.add(user_auth)
    the_db.session.add(the_user)
    the_db.session.commit()
    result['changed'] = True
    return the_user


def test_for_errors(start_time=None):
    todo = [['chatlog', 'id', ChatLog],
            ['email', 'id', docassemble.webapp.core.models.Email],
            ['emailattachment', 'id', docassemble.webapp.core.models.EmailAttachment],
            ['globalobjectstorage', 'id', docassemble.webapp.core.models.GlobalObjectStorage],
            ['install', 'id', docassemble.webapp.packages.models.Install],
            ['jsonstorage', 'id', docassemble.webapp.core.models.JsonStorage],
            ['machinelearning', 'id', docassemble.webapp.core.models.MachineLearning],
            ['objectstorage', 'id', docassemble.webapp.core.models.ObjectStorage],
            ['package_auth', 'id', docassemble.webapp.packages.models.PackageAuth],
            ['package', 'id', Package],
            ['role', 'id', Role],
            ['shortener', 'id', docassemble.webapp.core.models.Shortener],
            ['speaklist', 'id', docassemble.webapp.core.models.SpeakList],
            ['supervisors', 'id', docassemble.webapp.core.models.Supervisors],
            ['tempuser', 'id', TempUser],
            ['uploads', 'indexno', docassemble.webapp.core.models.Uploads],
            ['uploadsroleauth', 'id', docassemble.webapp.core.models.UploadsRoleAuth],
            ['uploadsuserauth', 'id', docassemble.webapp.core.models.UploadsUserAuth],
            ['user_auth', 'id', UserAuthModel],
            ['user', 'id', UserModel],
            ['user_invite', 'id', MyUserInvitation],
            ['user_roles', 'id', UserRoles],
            ['userdict', 'indexno', UserDict],
            ['userdictkeys', 'indexno', UserDictKeys]]
    for table, column, tableclass in todo:
        last_value = 0
        for results in db.session.execute(text('select last_value from "' + dbtableprefix + table + '_' + column + '_seq"')):
            last_value = results[0]
        max_value = db.session.execute(select(db.func.max(getattr(tableclass, column)))).scalar()
        if max_value is not None and max_value > last_value:
            logmessage('create_tables.test_for_errors: ' + dbtableprefix + table + " has an error: " + str(last_value) + " " + str(max_value) + " after " + str(time.time() - start_time) + " seconds.")
            db.session.execute(text('alter sequence "' + dbtableprefix + table + '_' + column + '_seq" restart with :newval'), {'newval': max_value + 1})
            db.session.commit()


def populate_tables(start_time=None):
    if start_time is None:
        start_time = time.time()
    logmessage("create_tables.populate_tables: starting after " + str(time.time() - start_time) + " seconds.")
    UserManager(SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel), app)
    logmessage("create_tables.populate_tables: obtained UserManager after " + str(time.time() - start_time) + " seconds.")
    result = {}
    admin_defaults = daconfig.get('default admin account', {})
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
    if 'api key' not in admin_defaults:
        api_key = os.getenv('DA_ADMIN_API_KEY', '')
        if api_key:
            admin_defaults['api key'] = api_key
    cron_defaults = daconfig.get('default cron account', {'nickname': 'cron', 'email': 'cron@admin.com', 'first_name': 'Cron', 'last_name': 'User'})
    cron_defaults['active'] = False
    user_role = get_role(db, 'user', result=result)
    admin_role = get_role(db, 'admin', result=result)
    cron_role = get_role(db, 'cron', result=result)
    get_role(db, 'customer', result=result)
    get_role(db, 'developer', result=result)
    get_role(db, 'advocate', result=result)
    get_role(db, 'trainer', result=result)
    if daconfig.get('fix user roles', False):
        logmessage("create_tables.populate_tables: fixing user roles after " + str(time.time() - start_time) + " seconds.")
        to_fix = []
        for user in db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles))).scalars():
            if len(user.roles) == 0:
                to_fix.append(user)
        if len(to_fix) > 0:
            logmessage("create_tables.populate_tables: found user roles to fix after " + str(time.time() - start_time) + " seconds.")
            for user in to_fix:
                user.roles.append(user_role)
            db.session.commit()
        logmessage("create_tables.populate_tables: done fixing user roles after " + str(time.time() - start_time) + " seconds.")
    admin = get_user(db, admin_role, admin_defaults, result=result)
    cron = get_user(db, cron_role, cron_defaults, result=result)
    if admin.confirmed_at is None:
        admin.confirmed_at = datetime.datetime.now()
    if cron.confirmed_at is None:
        cron.confirmed_at = datetime.datetime.now()
    if result.get('changed', False):
        db.session.commit()
    if 'api key' in admin_defaults:
        api_result = add_specific_api_key('default', admin_defaults['api key'], admin.id, daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87'))
        if api_result:
            logmessage("create_tables.populate_tables: added API key")
    logmessage("create_tables.populate_tables: calling add_dependencies after " + str(time.time() - start_time) + " seconds.")
    add_dependencies(admin.id, start_time=start_time)
    logmessage("create_tables.populate_tables: add_dependencies finished after " + str(time.time() - start_time) + " seconds.")
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
    logmessage("create_tables.populate_tables: ending after " + str(time.time() - start_time) + " seconds.")


def main():
    logmessage("create_tables.main: starting")
    start_time = time.time()
    if dbprefix.startswith('postgresql') and not daconfig.get('force text to varchar upgrade', False):
        do_varchar_upgrade = False
    else:
        do_varchar_upgrade = True
    with app.app_context():
        insp = inspect(db.engine)
        tables_exist = insp.has_table(dbtableprefix + 'userdict')
        logmessage("create_tables.main: inside app context after " + str(time.time() - start_time) + " seconds.")
        if daconfig.get('use alembic', True):
            logmessage("create_tables.main: running alembic after " + str(time.time() - start_time) + " seconds.")
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
            packagedir = importlib.resources.files('docassemble.webapp')
            if not packagedir.is_dir():
                sys.exit("path for running alembic could not be found")
            alembic_cfg = Config(os.path.join(packagedir, 'alembic.ini'))
            alembic_cfg.set_main_option("sqlalchemy.url", alchemy_connection_string())
            alembic_cfg.set_main_option("script_location", os.path.join(packagedir, 'alembic'))
            if not insp.has_table(dbtableprefix + 'alembic_version'):
                logmessage("create_tables.main: creating alembic stamp")
                command.stamp(alembic_cfg, "head")
                logmessage("create_tables.main: done creating alembic stamp after " + str(time.time() - start_time) + " seconds.")
            if insp.has_table(dbtableprefix + 'user'):
                logmessage("create_tables.main: creating alembic stamp")
                logmessage("create_tables.main: running alembic upgrade")
                command.upgrade(alembic_cfg, "head")
                logmessage("create_tables.main: done running alembic upgrade after " + str(time.time() - start_time) + " seconds.")
        # db.drop_all()
        try:
            logmessage("create_tables.main: trying to create tables")
            db.create_all()
        except:
            logmessage("create_tables.main: error trying to create tables; trying a second time.")
            try:
                db.create_all()
            except:
                logmessage("create_tables.main: error trying to create tables; trying a third time.")
                db.create_all()
        logmessage("create_tables.main: finished creating tables after " + str(time.time() - start_time) + " seconds.")
        if dbprefix.startswith('postgresql'):
            try:
                test_for_errors(start_time=start_time)
            except:
                logmessage("create_tables.main: unable to test for errors after " + str(time.time() - start_time) + " seconds.")
        logmessage("create_tables.main: populating tables after " + str(time.time() - start_time) + " seconds.")
        if not tables_exist:
            time.sleep(4)
        populate_tables(start_time=start_time)
        logmessage("create_tables.main: disposing engine after " + str(time.time() - start_time) + " seconds.")
        db.engine.dispose()
    logmessage("create_tables.main: finishing after " + str(time.time() - start_time) + " seconds.")

if __name__ == "__main__":
    main()
