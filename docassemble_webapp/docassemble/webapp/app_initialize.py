from werkzeug.middleware.proxy_fix import ProxyFix
from docassemble.base.plugin_manager import pm
from docassemble.webapp.extensions import (
    csrf,
    cors,
    babel,
    lm,
    the_user_manager,
    kv_session,
    db,
)

def init_app(the_app):
    # get configuration
    from docassemble.webapp.config import daconfig, in_cron
    from docassemble.webapp import setup
    setup.init_app(the_app)
    import docassemble.webapp.log_initialize
    # secret key
    the_app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
    # flask-sqlalchemy
    from docassemble.webapp import flask_sql_config
    flask_sql_config.init_app(the_app, other_databases=True)
    db.init_app(the_app)
    # session data in redis
    from docassemble.webapp.daredis import r_store
    from simplekv.memory.redisstore import RedisStore
    kv_session.init_app(the_app, session_kvstore=RedisStore(r_store))
    if daconfig.get('behind https load balancer', False):
        the_app.wsgi_app = ProxyFix(the_app.wsgi_app, x_proto=1, x_host=1)
    if 'cross site domains' in daconfig:
        cors.init_app(the_app, origins=daconfig['cross site domains'], supports_credentials=True)
    # import docassemble_flask_user here
    from docassemble_flask_user import SQLAlchemyAdapter
    # user_manager
    from docassemble.webapp.users.models import (
        UserModel,
        UserAuthModel,
        MyUserInvitation,
    )
    from docassemble.webapp.users.forms import (
        MySignInForm,
        MyRegisterForm,
        MyResendConfirmEmailForm,
        MyInviteForm,
    )
    from docassemble.webapp.users.views import (
        user_profile_page,
        logout,
        unauthorized,
        unauthenticated,
        custom_login,
        custom_register,
        custom_resend_confirm_email,
        password_validator,
        invite,
    )
    from docassemble.webapp.users.signals import register_signals
    from docassemble.webapp.utils.helpers import make_safe_url
    the_db_adapter = SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel, UserInvitationClass=MyUserInvitation)
    the_user_manager.init_app(the_app, db_adapter=the_db_adapter, login_form=MySignInForm, register_form=MyRegisterForm, user_profile_view_function=user_profile_page, logout_view_function=logout, unauthorized_view_function=unauthorized, unauthenticated_view_function=unauthenticated, login_view_function=custom_login, register_view_function=custom_register, resend_confirm_email_view_function=custom_resend_confirm_email, resend_confirm_email_form=MyResendConfirmEmailForm, password_validator=password_validator, make_safe_url_function=make_safe_url, invite_form=MyInviteForm, invite_view_function=invite)
    register_signals(the_app)
    # users blueprint
    from docassemble.webapp.users import users_bp
    import docassemble.webapp.users.loginurl
    pm.register(docassemble.webapp.users.loginurl)
    import docassemble.webapp.users.helpers
    pm.register(docassemble.webapp.users.helpers)
    import docassemble.webapp.users.hooks
    pm.register(docassemble.webapp.users.hooks)
    the_app.register_blueprint(users_bp)
    # user_database
    import docassemble.webapp.user_database
    pm.register(docassemble.webapp.user_database)
    # login_manager
    lm.init_app(the_app)
    lm.login_view = 'custom_login'
    from docassemble.webapp.users.models import AnonymousUserModel
    lm.anonymous_user = AnonymousUserModel
    # admin blueprint
    from docassemble.webapp.admin import admin_bp
    import docassemble.webapp.admin.funcs
    pm.register(docassemble.webapp.admin.funcs)
    the_app.register_blueprint(admin_bp)
    # main blueprint
    from docassemble.webapp.main import main_bp
    if the_app.config['ENABLE_API']:
        import docassemble.webapp.main.api
    import docassemble.webapp.main.views
    import docassemble.webapp.main.hooks
    pm.register(docassemble.webapp.main.hooks)
    import docassemble.webapp.main.helpers
    pm.register(docassemble.webapp.main.helpers)
    the_app.register_blueprint(main_bp)
    # objectstore
    if the_app.config['ENABLE_OBJECT_STORAGE']:
        import docassemble.webapp.objectstore.models
        import docassemble.webapp.objectstore.hooks
        pm.register(docassemble.webapp.objectstore.hooks)
    # daglobal
    if the_app.config['ENABLE_DAGLOBAL']:
        import docassemble.webapp.daglobal.models
        import docassemble.webapp.daglobal.hooks
        import docassemble.webapp.daglobal.helpers
        pm.register(docassemble.webapp.daglobal.hooks)
        pm.register(docassemble.webapp.daglobal.helpers)
    # jsonstorage
    if the_app.config['ENABLE_JSON_STORAGE']:
        import docassemble.webapp.jsonstorage.helpers
        pm.register(docassemble.webapp.jsonstorage.helpers)
    # files blueprint
    from docassemble.webapp.files import files_bp
    if the_app.config['ENABLE_API']:
        import docassemble.webapp.files.api
    import docassemble.webapp.files.views
    import docassemble.webapp.files.hooks
    pm.register(docassemble.webapp.files.hooks)
    import docassemble.webapp.files.helpers
    pm.register(docassemble.webapp.files.helpers)
    import docassemble.webapp.files.file_number
    pm.register(docassemble.webapp.files.file_number)
    the_app.register_blueprint(files_bp)
    # packages blueprint
    from docassemble.webapp.packages import packages_bp
    if the_app.config['ENABLE_API']:
        import docassemble.webapp.packages.api
    import docassemble.webapp.packages.views
    the_app.register_blueprint(packages_bp)
    # develop blueprint
    from docassemble.webapp.develop import develop_bp
    if the_app.config['ENABLE_API']:
        import docassemble.webapp.develop.api
    import docassemble.webapp.develop.views
    the_app.register_blueprint(develop_bp)
    # monitor blueprint
    if the_app.config['ENABLE_MONITOR']:
        from docassemble.webapp.monitor import monitor_bp
        import docassemble.webapp.monitor.views
        import docassemble.webapp.monitor.hooks
        pm.register(docassemble.webapp.monitor.hooks)
        the_app.register_blueprint(monitor_bp)
    # training blueprint
    if the_app.config['ENABLE_TRAINING']:
        import docassemble.webapp.ml.config
        from docassemble.webapp.ml import ml_bp
        import docassemble.webapp.ml.views
        the_app.register_blueprint(ml_bp)
        import docassemble.webapp.ml.hooks
        pm.register(docassemble.webapp.ml.hooks)
    # interview blueprint
    from docassemble.webapp.interview import interview_bp
    import docassemble.webapp.interview.hooks
    pm.register(docassemble.webapp.interview.hooks)
    import docassemble.webapp.interview.helpers
    pm.register(docassemble.webapp.interview.helpers)
    if the_app.config['ENABLE_API']:
        import docassemble.webapp.interview.api
    import docassemble.webapp.interview.views
    the_app.register_blueprint(interview_bp)
    # api blueprint
    if the_app.config['ENABLE_API']:
        from docassemble.webapp.api import api_bp
        import docassemble.webapp.api.api
        import docassemble.webapp.api.views
        the_app.register_blueprint(api_bp)
    # translation blueprint
    from docassemble.webapp.translation import translation_bp
    the_app.register_blueprint(translation_bp)
    # fax blueprint
    if the_app.config['ENABLE_FAX']:
        from docassemble.webapp.fax import fax_bp
        import docassemble.webapp.fax.helpers
        pm.register(docassemble.webapp.fax.helpers)
        the_app.register_blueprint(fax_bp)
    # logs blueprint
    if the_app.config['ALLOW_LOG_VIEWING']:
        from docassemble.webapp.logs import logs_bp
        the_app.register_blueprint(logs_bp)
    # auth blueprint
    if the_app.config['USE_GOOGLE_LOGIN'] or \
       the_app.config['USE_FACEBOOK_LOGIN'] or \
       the_app.config['USE_ZITADEL_LOGIN'] or \
       the_app.config['USE_AUTH0_LOGIN'] or \
       the_app.config['USE_KEYCLOAK_LOGIN'] or \
       the_app.config['USE_AUTHENTIK_LOGIN'] or \
       the_app.config['USE_AZURE_LOGIN'] or \
       the_app.config['USE_MINIORANGE_LOGIN']:
        from docassemble.webapp.auth import auth_bp
        import docassemble.webapp.auth.views
        the_app.register_blueprint(auth_bp)
        # phonelogin blueprint
    if the_app.config['USE_PHONE_LOGIN']:
        from docassemble.webapp.phonelogin import phonelogin_bp
        the_app.register_blueprint(phonelogin_bp)
    # sms blueprint
    if the_app.config['ENABLE_SMS_INTERFACE']:
        from docassemble.webapp.sms import sms_bp
        import docassemble.webapp.sms.helpers
        pm.register(docassemble.webapp.sms.helpers)
        import docassemble.webapp.sms.views
        pm.register(docassemble.webapp.sms.views)
        the_app.register_blueprint(sms_bp)
    # tts blueprint
    if the_app.config['ENABLE_TTS']:
        from docassemble.webapp.tts import tts_bp
        import docassemble.webapp.tts.models
        import docassemble.webapp.tts.hooks
        pm.register(docassemble.webapp.tts.hooks)
        the_app.register_blueprint(tts_bp)
    # mail
    import docassemble.webapp.mail.hooks
    pm.register(docassemble.webapp.mail.hooks)
    # utils
    import docassemble.webapp.utils.hooks
    pm.register(docassemble.webapp.utils.hooks)
    import docassemble.webapp.utils.filenames
    pm.register(docassemble.webapp.utils.filenames)
    import docassemble.webapp.utils.fixpickle
    pm.register(docassemble.webapp.utils.fixpickle)
    import docassemble.webapp.utils.helpers
    pm.register(docassemble.webapp.utils.helpers)
    import docassemble.webapp.lock
    pm.register(docassemble.webapp.lock)
    import docassemble.webapp.screenreader
    pm.register(docassemble.webapp.screenreader)
    import docassemble.webapp.cloud.utils
    pm.register(docassemble.webapp.cloud.utils)
    # email server
    if the_app.config['ENABLE_EMAIL_SERVER']:
        import docassemble.webapp.emailserver.helpers
        pm.register(docassemble.webapp.emailserver.helpers)
    # cron blueprint
    if in_cron:
        from docassemble.webapp.cron_tasks import cron_bp
        import docassemble.webapp.cron_tasks.cli
        the_app.register_blueprint(cron_bp)
    # celery
    from docassemble.webapp.tasks.app import celery_app
    celery_app.set_current()
    import docassemble.webapp.tasks.hooks
    pm.register(docassemble.webapp.tasks.hooks)
    # jinja
    from docassemble.webapp.utils.helpers import url_for_interview
    from docassemble.webapp.utils.hooks import url_for
    the_app.jinja_env.globals.update(url_for=url_for, url_for_interview=url_for_interview)
    # lifecycle
    from docassemble.webapp import lifecycle
    lifecycle.init_app(the_app)
    # error handling
    from docassemble.webapp import errors
    errors.init_app(the_app)
    # csrf
    csrf.init_app(the_app)
    # babel
    babel.init_app(the_app)
    # create tables for jsonstorage if necessary
    if the_app.config['ENABLE_JSON_STORAGE']:
        docassemble.webapp.jsonstorage.helpers.create_custom_tables(the_app)
    # misc
    from .utils.helpers import my_default_url
    the_app.handle_url_build_error = my_default_url
    from flask import abort
    _orig_send_static = the_app.send_static_file
    def _custom_send_static(filename):
        if not daconfig.get('debug', True) and filename.lower().endswith(('.css.map', '.js.map')):
            abort(404)
        return _orig_send_static(filename)
    the_app.send_static_file = _custom_send_static
    return the_app
