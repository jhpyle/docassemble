# pylint: disable=wrong-import-position
# restart.py runs this through subprocess
# initialize.sh runs this.
# so it should not load Flask
import sys
import os
import time
import datetime
import traceback
import importlib.resources
# from flask import Flask
from alembic.config import Config
from alembic import command
from sqlalchemy import select, delete, inspect
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text, func
# import random
# import string
# from docassemble_flask_user import UserManager, SQLAlchemyAdapter
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.generate_key import random_alphanumeric
from docassemble.base.language.words import word
from docassemble.webapp.config import daconfig
from docassemble.webapp.daglobal.models import GlobalObjectStorage
from docassemble.webapp.database import (
    alchemy_connection_string,
    dbtableprefix,
    dbprefix,
)
from docassemble.webapp.db import session_scope, binds
from docassemble.webapp.db_base import Base, JsonBase
from docassemble.webapp.extensions import db
from docassemble.webapp.emailserver.models import Shortener, Email, EmailAttachment
from docassemble.webapp.interview.models import UserDict, UserDictKeys
from docassemble.webapp.jsonstorage.models import JsonStorage
from docassemble.webapp.objectstore.models import ObjectStorage
from docassemble.webapp.tts.models import SpeakList
from docassemble.webapp.main.models import (
    Uploads,
    UploadsRoleAuth,
    UploadsUserAuth,
    Supervisors,
)
from docassemble.webapp.ml.models import MachineLearning
from docassemble.webapp.monitor.models import ChatLog
from docassemble.webapp.packages.models import Package, Install, PackageAuth
from docassemble.webapp.update import add_dependencies
from docassemble.webapp.users.models import (
    UserAuthModel,
    UserModel,
    MyUserInvitation,
    Role,
    UserRoles,
    TempUser,
)
from docassemble.webapp.utils.api_key import add_specific_api_key
from docassemble.webapp.utils.logger import logmessage

FLASK_APP = None

def get_flask_app():
    global FLASK_APP  # pylint: disable=global-statement
    if FLASK_APP is not None:
        return FLASK_APP
    from flask import Flask
    from docassemble_flask_user import UserManager, SQLAlchemyAdapter
    from docassemble.webapp.config import DEFAULT_SECRET_KEY
    app = Flask('docassemble.webapp.app_object')
    app.secret_key = daconfig.get('secretkey', DEFAULT_SECRET_KEY)
    from docassemble.webapp.database import alchemy_connection_string
    app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connection_string()
    db.init_app(app)

    the_db_adapter = SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel, UserInvitationClass=MyUserInvitation)
    the_user_manager = UserManager()
    the_user_manager.init_app(app, db_adapter=the_db_adapter)
    FLASK_APP = app
    return app


def get_role(session, name, result=None):
    if result is None:
        result = {}
    the_role = session.execute(select(Role).filter_by(name=name)).scalar()
    if the_role:
        return the_role
    the_role = Role(name=name)
    session.add(the_role)
    session.flush()
    result['changed'] = True
    return the_role


def get_user(session, role, defaults, result=None):
    if result is None:
        result = {}
    the_user = session.execute(select(UserModel).filter_by(nickname=defaults['nickname'])).scalar()
    if the_user:
        return the_user
    while True:
        new_social = 'local$' + random_alphanumeric(32)
        existing_user = session.execute(select(UserModel).filter_by(social_id=new_social)).scalar()
        if existing_user:
            continue
        break
    user_auth = UserAuthModel(password=get_flask_app().user_manager.hash_password(defaults.get('password', 'password')))  # pylint: disable=no-member
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
    session.add(user_auth)
    session.add(the_user)
    session.flush()
    result['changed'] = True
    return the_user


def test_for_errors(start_time=None):
    todo = [['chatlog', 'id', ChatLog],
            ['email', 'id', Email],
            ['emailattachment', 'id', EmailAttachment],
            ['globalobjectstorage', 'id', GlobalObjectStorage],
            ['install', 'id', Install],
            ['jsonstorage', 'id', JsonStorage],
            ['machinelearning', 'id', MachineLearning],
            ['objectstorage', 'id', ObjectStorage],
            ['package_auth', 'id', PackageAuth],
            ['package', 'id', Package],
            ['role', 'id', Role],
            ['shortener', 'id', Shortener],
            ['speaklist', 'id', SpeakList],
            ['supervisors', 'id', Supervisors],
            ['tempuser', 'id', TempUser],
            ['uploads', 'indexno', Uploads],
            ['uploadsroleauth', 'id', UploadsRoleAuth],
            ['uploadsuserauth', 'id', UploadsUserAuth],
            ['user_auth', 'id', UserAuthModel],
            ['user', 'id', UserModel],
            ['user_invite', 'id', MyUserInvitation],
            ['user_roles', 'id', UserRoles],
            ['userdict', 'indexno', UserDict],
            ['userdictkeys', 'indexno', UserDictKeys]]
    with session_scope() as session:
        for table, column, tableclass in todo:
            last_value = 0
            for results in session.execute(text('select last_value from "' + dbtableprefix + table + '_' + column + '_seq"')):
                last_value = results[0]
            max_value = session.execute(select(func.max(getattr(tableclass, column)))).scalar()
            if max_value is not None and max_value > last_value:
                logmessage('create_tables.test_for_errors: ' + dbtableprefix + table + " has an error: " + str(last_value) + " " + str(max_value) + " after " + str(time.time() - start_time) + " seconds.")
                session.execute(text('alter sequence "' + dbtableprefix + table + '_' + column + '_seq" restart with :newval'), {'newval': max_value + 1})


def populate_tables(start_time=None):
    if start_time is None:
        start_time = time.time()
    logmessage("create_tables.populate_tables: starting after " + str(time.time() - start_time) + " seconds.")
    # UserManager(SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel), app)
    # logmessage("create_tables.populate_tables: obtained UserManager after " + str(time.time() - start_time) + " seconds.")
    # not sure why obtaining UserManager is important
    result = {}
    admin_defaults = daconfig.get('default admin account', {})
    if 'email' not in admin_defaults:
        admin_defaults['email'] = os.getenv('DA_ADMIN_EMAIL', 'admin@example.com')
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
    with session_scope() as session:
        user_role = get_role(session, 'user', result=result)
        admin_role = get_role(session, 'admin', result=result)
        cron_role = get_role(session, 'cron', result=result)
        get_role(session, 'customer', result=result)
        get_role(session, 'developer', result=result)
        get_role(session, 'advocate', result=result)
        get_role(session, 'trainer', result=result)
        if daconfig.get('fix user roles', False):
            logmessage("create_tables.populate_tables: fixing user roles after " + str(time.time() - start_time) + " seconds.")
            to_fix = []
            for user in session.execute(select(UserModel).options(joinedload(UserModel.roles))).scalars():
                if len(user.roles) == 0:
                    to_fix.append(user)
            if len(to_fix) > 0:
                logmessage("create_tables.populate_tables: found user roles to fix after " + str(time.time() - start_time) + " seconds.")
                for user in to_fix:
                    user.roles.append(user_role)
            logmessage("create_tables.populate_tables: done fixing user roles after " + str(time.time() - start_time) + " seconds.")
        admin = get_user(session, admin_role, admin_defaults, result=result)
        admin_id = admin.id
        cron = get_user(session, cron_role, cron_defaults, result=result)
        if admin.confirmed_at is None:
            admin.confirmed_at = datetime.datetime.now()
        if cron.confirmed_at is None:
            cron.confirmed_at = datetime.datetime.now()
    # if result.get('changed', False):
    #     session.commit()
    if 'api key' in admin_defaults:
        api_result = add_specific_api_key('default', admin_defaults['api key'], admin_id, daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87'))
        if api_result:
            logmessage("create_tables.populate_tables: added API key")
    with session_scope() as session:
        logmessage("create_tables.populate_tables: calling add_dependencies after " + str(time.time() - start_time) + " seconds.")
        add_dependencies(session, admin_id, start_time=start_time)
        logmessage("create_tables.populate_tables: add_dependencies finished after " + str(time.time() - start_time) + " seconds.")
        git_packages = session.execute(select(Package).filter_by(type='git')).scalars().all()
        for package in git_packages:
            if package.name in ['docassemble', 'docassemble.base', 'docassemble.webapp', 'docassemble.demo']:
                if package.giturl:
                    package.giturl = None
                if package.gitsubdir:
                    package.gitsubdir = None
                if package.type != 'pip':
                    package.type = 'pip'
                if daconfig.get('stable version', False):
                    if package.limitation != '<1.1.0':
                        package.limitation = '<1.1.0'
    logmessage("create_tables.populate_tables: ending after " + str(time.time() - start_time) + " seconds.")


def main():
    logmessage("create_tables.main: starting")
    start_time = time.time()
    if dbprefix.startswith('postgresql') and not daconfig.get('force text to varchar upgrade', False):
        do_varchar_upgrade = False
    else:
        do_varchar_upgrade = True
    # with app.app_context():
    with session_scope() as session:
        insp = inspect(session.get_bind())
        tables_exist = insp.has_table(dbtableprefix + 'userdict')
        logmessage("create_tables.main: inside app context after " + str(time.time() - start_time) + " seconds.")
        if daconfig.get('use alembic', True):
            logmessage("create_tables.main: running alembic after " + str(time.time() - start_time) + " seconds.")
            if do_varchar_upgrade:
                if insp.has_table(dbtableprefix + 'userdict'):
                    session.execute(delete(UserDict).where(func.length(UserDict.filename) > 255).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'userdictkeys'):
                    session.execute(delete(UserDictKeys).where(func.length(UserDictKeys.filename) > 255).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'chatlog'):
                    session.execute(delete(ChatLog).where(func.length(ChatLog.filename) > 255).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'uploads'):
                    session.execute(delete(Uploads).where(func.length(Uploads.filename) > 255).execution_options(synchronize_session=False))
                    session.execute(delete(Uploads).where(func.length(Uploads.yamlfile) > 255).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'objectstorage'):
                    session.execute(delete(ObjectStorage).where(func.length(ObjectStorage.key) > 1024).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'speaklist'):
                    session.execute(delete(SpeakList).where(func.length(SpeakList.filename) > 255).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'shortener'):
                    session.execute(delete(Shortener).where(func.length(Shortener.filename) > 255).execution_options(synchronize_session=False))
                    session.execute(delete(Shortener).where(func.length(Shortener.key) > 255).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'machinelearning'):
                    session.execute(delete(MachineLearning).where(func.length(MachineLearning.key) > 1024).execution_options(synchronize_session=False))
                    session.execute(delete(MachineLearning).where(func.length(MachineLearning.group_id) > 1024).execution_options(synchronize_session=False))
                if insp.has_table(dbtableprefix + 'globalobjectstorage'):
                    session.execute(delete(GlobalObjectStorage).where(func.length(GlobalObjectStorage.key) > 1024).execution_options(synchronize_session=False))
    if daconfig.get('use alembic', True):
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
    with session_scope() as session:
        try:
            logmessage("create_tables.main: trying to create tables")
            Base.metadata.create_all(session.bind)
        except:
            logmessage("create_tables.main: error trying to create tables; trying a second time.")
            try:
                Base.metadata.create_all(session.bind)
            except:
                logmessage("create_tables.main: error trying to create tables; trying a third time.")
                Base.metadata.create_all(session.bind)
        JsonBase.metadata.create_all(binds.get(JsonStorage, session.bind))
    logmessage("create_tables.main: finished creating tables after " + str(time.time() - start_time) + " seconds.")
    if dbprefix.startswith('postgresql'):
        try:
            test_for_errors(start_time=start_time)
        except:
            logmessage("create_tables.main: unable to test for errors after " + str(time.time() - start_time) + " seconds.\n" + traceback.format_exc())
    logmessage("create_tables.main: populating tables after " + str(time.time() - start_time) + " seconds.")
    if not tables_exist:
        time.sleep(4)
    populate_tables(start_time=start_time)
    logmessage("create_tables.main: finishing after " + str(time.time() - start_time) + " seconds.")

if __name__ == "__main__":
    main()
