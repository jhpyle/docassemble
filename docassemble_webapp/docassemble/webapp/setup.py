import re
import importlib
from datetime import timedelta
from docassemble.webapp.config import daconfig, DEFAULT_SECRET_KEY, da_version
from docassemble.webapp.database import alchemy_connection_string
from .twilio.helpers import twilio_config

def init_app(app):
    app.config['DA_VERSION'] = da_version
    app.config['APP_NAME'] = daconfig.get('appname', 'docassemble')
    app.config['BRAND_NAME'] = daconfig.get('brandname', daconfig.get('appname', 'docassemble'))
    app.config['SHOW_PROFILE'] = bool(daconfig.get('show profile link', True))
    app.config['SHOW_MY_INTERVIEWS'] = bool(daconfig.get('show interviews link', True))
    app.config['SHOW_DISPATCH'] = bool(len(daconfig['dispatch']) and daconfig.get('show dispatch link', False) > 0)
    # app.config['ADMINS'] = [daconfig.get('admin address', None)]
    app.config['APP_SYSTEM_ERROR_SUBJECT_LINE'] = app.config['APP_NAME'] + " system error"
    app.config['APPLICATION_ROOT'] = daconfig.get('root', '/')
    app.config['CSRF_ENABLED'] = False
    app.config['USE_MFA'] = bool(daconfig['two factor authentication'].get('enable', True))
    app.config['MFA_ALLOW_SMS'] = bool(daconfig['two factor authentication'].get('allow sms', True))
    app.config['MFA_ALLOW_APP'] = bool(daconfig['two factor authentication'].get('allow app', True))
    if 'required for' in daconfig['two factor authentication'] and isinstance(daconfig['two factor authentication']['required for'], list):
        app.config['MFA_REQUIRED_FOR_ROLE'] = daconfig['two factor authentication']['required for']
    else:
        app.config['MFA_REQUIRED_FOR_ROLE'] = []
    app.config['MFA_ROLES'] = daconfig['two factor authentication'].get('allowed for', ['admin', 'developer'])
    app.config['MFA_ROLES'] = list(set(app.config['MFA_ROLES'] + app.config['MFA_REQUIRED_FOR_ROLE']))
    if not (app.config['MFA_ALLOW_SMS'] or app.config['MFA_ALLOW_APP']):
        app.config['USE_MFA'] = False
    app.config['API_ROLES'] = daconfig.get('api privileges', ['admin', 'developer'])
    app.config['WTF_CSRF_TIME_LIMIT'] = 604800
    app.config['WTF_CSRF_SSL_STRICT'] = daconfig.get('require referer', bool(daconfig.get('cross site domains', None) is None))
    app.config['USER_APP_NAME'] = app.config['APP_NAME']
    app.config['USER_SEND_PASSWORD_CHANGED_EMAIL'] = False
    app.config['USER_SEND_REGISTERED_EMAIL'] = bool(daconfig.get('confirm registration', False))
    app.config['USER_SEND_USERNAME_CHANGED_EMAIL'] = False
    app.config['USER_ENABLE_RETYPE_PASSWORD'] = bool(daconfig.get('retype password', True))
    app.config['USER_ENABLE_REMEMBER_ME'] = False
    app.config['USER_ENABLE_EMAIL'] = True
    app.config['USER_ENABLE_USERNAME'] = False
    app.config['USER_ENABLE_REGISTRATION'] = True
    app.config['USER_ENABLE_CHANGE_USERNAME'] = False
    app.config['ALLOW_CHANGING_PASSWORD'] = bool(daconfig.get('allow changing password', True))
    app.config['USER_ENABLE_CONFIRM_EMAIL'] = bool(daconfig.get('confirm registration', False))
    app.config['USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL'] = not bool(daconfig.get('confirm registration', False))
    app.config['USER_AUTO_LOGIN_AFTER_REGISTER'] = not bool(daconfig.get('confirm registration', False))
    app.config['USER_SHOW_USERNAME_EMAIL_DOES_NOT_EXIST'] = not bool(daconfig.get('confirm registration', False))
    app.config['USER_AUTO_LOGIN_AFTER_RESET_PASSWORD'] = False
    app.config['FLASH_LOGIN_MESSAGES'] = not bool(daconfig.get('suppress login alerts', False))
    app.config['USER_AFTER_FORGOT_PASSWORD_ENDPOINT'] = 'user.login'
    app.config['USER_AFTER_CHANGE_PASSWORD_ENDPOINT'] = 'interview.after_reset'
    app.config['USER_AFTER_CHANGE_USERNAME_ENDPOINT'] = 'user.login'
    app.config['USER_INVITE_ENDPOINT'] = 'users.user_list'
    app.config['USER_AFTER_CONFIRM_ENDPOINT'] = 'user.login'
    app.config['USER_AFTER_LOGIN_ENDPOINT'] = 'admin.interview_list'
    app.config['USER_AFTER_LOGOUT_ENDPOINT'] = 'user.login'
    app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login' if daconfig.get('confirm registration', False) else 'admin.interview_list'
    app.config['USER_AFTER_RESEND_CONFIRM_EMAIL_ENDPOINT'] = 'user.login'
    app.config['USER_AFTER_RESET_PASSWORD_ENDPOINT'] = 'user.login'
    app.config['USER_INVITE_URL'] = '/user/invite'
    app.config['USER_ENABLE_INVITATION'] = True
    app.config['USER_INVITE_EMAIL_TEMPLATE'] = 'flask_user/emails/invite'
    app.config['USER_ENABLE_FORGOT_PASSWORD'] = bool(daconfig.get('allow forgot password', True))
    fi_version = daconfig.get('favicon version', None)

    if fi_version is None and 'favicon' in daconfig and isinstance(daconfig['favicon'], str):
        m = re.search(r'([^:]+):', daconfig['favicon'])
        if m:
            try:
                importlib.import_module(m.group(1))
                fi_version = eval(m.group(1) + '.__version__')
            except:
                pass

    if fi_version is not None:
        app.config['FAVICON_VERSION'] = '?v=' + str(fi_version)
        app.config['FAVICON_PARAMS'] = {'v': str(fi_version)}
    else:
        app.config['FAVICON_VERSION'] = ''
        app.config['FAVICON_PARAMS'] = {}

    app.config['FAVICON_MASK_COLOR'] = daconfig.get('favicon mask color', '#698aa7')
    app.config['FAVICON_TILE_COLOR'] = daconfig.get('favicon tile color', '#da532c')
    app.config['FAVICON_THEME_COLOR'] = daconfig.get('favicon theme color', '#83b3dd')

    if not daconfig.get('allow registration', True):
        app.config['USER_REQUIRE_INVITATION'] = True
    app.config['MAX_CONTENT_LENGTH'] = daconfig.get('maximum content length', 16 * 1024 * 1024)
    app.config['MAX_FORM_MEMORY_SIZE'] = app.config['MAX_CONTENT_LENGTH']
    app.config['USE_X_SENDFILE'] = daconfig.get('xsendfile', True) if daconfig.get('web server', 'nginx') == 'apache' else False
    # if daconfig.get('behind https load balancer', False):
    #     app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    alchemy_connect_string = alchemy_connection_string()
    app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
    app.secret_key = daconfig.get('secretkey', DEFAULT_SECRET_KEY)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['ENABLE_MANAGE_ACCOUNT'] = daconfig.get('user can delete account', True)
    app.config['ENABLE_REQUEST_DEVELOPER_ACCOUNT'] = daconfig.get('user can request developer account', False)
    app.config['ENABLE_DELETE_SHARED'] = daconfig.get('delete account deletes shared', False)
    app.config['ENABLE_DELETE_ACCOUNT'] = daconfig.get('admin can delete account', True)
    app.config['SESSION_COOKIE_SECURE'] = daconfig.get('use https', False) or daconfig.get('behind https load balancer', False)
    if daconfig.get('allow embedding', 'Lax') is True:
        app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    elif daconfig.get('allow embedding', 'Lax') is False:
        app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    else:
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_SECURE'] = app.config['SESSION_COOKIE_SECURE']
    if 'session lifetime seconds' in daconfig:
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=daconfig['session lifetime seconds'])
    app.config['SOCIAL'] = daconfig['social']
    app.config['OG_LOCALE'] = re.sub(r'\..*', '', daconfig.get('locale', 'en_US.utf8'))
    app.config['ENABLE_API'] = daconfig.get('enable api', True)
    app.config['ENABLE_EMAIL_SERVER'] = daconfig.get('enable email server', True)
    app.config['ENABLE_OBJECT_STORAGE'] = daconfig.get('enable object storage', True)
    app.config['ENABLE_DAGLOBAL'] = daconfig.get('enable daglobal', True)
    app.config['ENABLE_JSON_STORAGE'] = daconfig.get('enable json storage', True)
    app.config['ENABLE_SMS_INTERFACE'] = daconfig.get('enable sms interface', True)
    app.config['ENABLE_MONITOR'] = daconfig.get('enable monitor', True)
    app.config['ENABLE_TRAINING'] = daconfig.get('enable training', True)
    app.config['ENABLE_FAX'] = daconfig.get('enable faxing', True)
    app.config['ENABLE_TTS'] = daconfig.get('enable tts', True)
    app.config['INVERSE_NAVBAR'] = bool(daconfig.get('inverse navbar', True))
    app.config['AUTO_COLOR_SCHEME'] = bool(daconfig.get('auto color scheme', True))
    app.config['ENABLE_PLAYGROUND'] = daconfig.get('enable playground', True)
    app.config['DEVELOPER_CAN_INSTALL'] = daconfig.get('developer can install', True)
    app.config['ENABLE_SHARING_PLAYGROUNDS'] = daconfig.get('enable sharing playgrounds', False)
    app.config['ALLOW_LOG_VIEWING'] = daconfig.get('allow log viewing', True)
    app.config['ALLOW_UPDATES'] = daconfig.get('allow updates', True)
    app.config['ALLOW_CONFIGURATION_EDITING'] = daconfig.get('allow configuration editing', True)
    app.config['ALLOW_RESTARTING'] = bool(app.config['ENABLE_PLAYGROUND'] or app.config['ALLOW_UPDATES'] or app.config['ALLOW_CONFIGURATION_EDITING'])
    app.config['USER_PROFILE_FIELDS'] = daconfig.get('user profile fields', [])
    app.config['GRID_CLASSES_USER'] = daconfig['grid classes']['user']
    app.config['GRID_CLASSES_WIDE'] = daconfig['grid classes']['admin wide']
    app.config['GRID_CLASSES_ADMIN'] = daconfig['grid classes']['admin']
    app.config['DEFER'] = daconfig['javascript defer']
    app.debug = False
    app.config['CONTAINER_CLASS'] = 'container-fluid' if daconfig.get('admin full width', False) else 'container'
    app.config['USE_GOOGLE_LOGIN'] = False
    app.config['USE_FACEBOOK_LOGIN'] = False
    app.config['USE_ZITADEL_LOGIN'] = False
    app.config['USE_MINIORANGE_LOGIN'] = False
    app.config['USE_AUTH0_LOGIN'] = False
    app.config['USE_KEYCLOAK_LOGIN'] = False
    app.config['USE_AUTHENTIK_LOGIN'] = False
    app.config['USE_AZURE_LOGIN'] = False
    app.config['USE_GOOGLE_DRIVE'] = False
    app.config['USE_ONEDRIVE'] = False
    app.config['USE_PHONE_LOGIN'] = False
    app.config['USE_GITHUB'] = False
    app.config['USE_PASSWORD_LOGIN'] = not bool(daconfig.get('password login', True) is False)
    app.config['AUTO_LOGIN'] = daconfig.get('auto login', False)
    if twilio_config is not None and daconfig.get('phone login', False) is True:
        app.config['USE_PHONE_LOGIN'] = True
    if 'oauth' in daconfig:
        app.config['OAUTH_CREDENTIALS'] = daconfig['oauth']
        oauth_providers = [
            ('USE_GOOGLE_LOGIN', 'google'),
            ('USE_FACEBOOK_LOGIN', 'facebook'),
            ('USE_ZITADEL_LOGIN', 'zitadel'),
            ('USE_MINIORANGE_LOGIN', 'miniorange'),
            ('USE_AUTH0_LOGIN', 'auth0'),
            ('USE_KEYCLOAK_LOGIN', 'keycloak'),
            ('USE_AUTHENTIK_LOGIN', 'authentik'),
            ('USE_AZURE_LOGIN', 'azure'),
            ('USE_GOOGLE_DRIVE', 'googledrive'),
            ('USE_ONEDRIVE', 'onedrive'),
            ('USE_GITHUB', 'github'),
        ]
        for env_var, oauth_key in oauth_providers:
            app.config[env_var] = bool(oauth_key in daconfig['oauth'] and not ('enable' in daconfig['oauth'][oauth_key] and daconfig['oauth'][oauth_key]['enable'] is False))
    else:
        app.config['OAUTH_CREDENTIALS'] = {}
    app.config['USE_PYPI'] = daconfig.get('pypi', False)

    if daconfig.get('button size', 'medium') == 'medium':
        app.config['BUTTON_CLASS'] = 'btn-da'
    elif daconfig['button size'] == 'large':
        app.config['BUTTON_CLASS'] = 'btn-lg btn-da'
    elif daconfig['button size'] == 'small':
        app.config['BUTTON_CLASS'] = 'btn-sm btn-da'
    else:
        app.config['BUTTON_CLASS'] = 'btn-da'

    if daconfig.get('button style', 'normal') == 'normal':
        app.config['BUTTON_STYLE'] = 'btn-'
    elif daconfig['button style'] == 'outline':
        app.config['BUTTON_STYLE'] = 'btn-outline-'
    else:
        app.config['BUTTON_STYLE'] = 'btn-'
    app.config['FOOTER_CLASS'] = str(daconfig.get('footer css class', 'bg-secondary-subtle')).strip() + ' dafooter'
