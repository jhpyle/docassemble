from docassemble.webapp.app_object import app
from docassemble.base.config import daconfig
import docassemble.webapp.database
app.config['APP_NAME'] = daconfig.get('appname', 'docassemble')
app.config['BRAND_NAME'] = daconfig.get('brandname', daconfig.get('appname', 'docassemble'))
app.config['SHOW_PROFILE'] = True if daconfig.get('show profile link', True) else False
app.config['SHOW_MY_INTERVIEWS'] = True if daconfig.get('show interviews link', True) else False
app.config['SHOW_DISPATCH'] = True if len(daconfig['dispatch']) and daconfig.get('show dispatch link', False) else False
app.config['MAIL_USERNAME'] = daconfig['mail'].get('username', None)
app.config['MAIL_PASSWORD'] = daconfig['mail'].get('password', None)
app.config['MAIL_DEFAULT_SENDER'] = daconfig['mail'].get('default sender', None)
app.config['MAIL_SERVER'] = daconfig['mail'].get('server', 'localhost')
app.config['MAIL_PORT'] = daconfig['mail'].get('port', 25)
app.config['MAIL_USE_SSL'] = daconfig['mail'].get('use ssl', False)
app.config['MAIL_USE_TLS'] = daconfig['mail'].get('use tls', True)
#app.config['ADMINS'] = [daconfig.get('admin address', None)]
app.config['APP_SYSTEM_ERROR_SUBJECT_LINE'] = app.config['APP_NAME'] + " system error"
app.config['APPLICATION_ROOT'] = daconfig.get('root', '/')
app.config['CSRF_ENABLED'] = False
if daconfig['two factor authentication'].get('enable', True):
    app.config['USE_MFA'] = True
else:
    app.config['USE_MFA'] = False
if daconfig['two factor authentication'].get('allow sms', True):
    app.config['MFA_ALLOW_SMS'] = True
else:
    app.config['MFA_ALLOW_SMS'] = False
if daconfig['two factor authentication'].get('allow app', True):
    app.config['MFA_ALLOW_APP'] = True
else:
    app.config['MFA_ALLOW_APP'] = False
if 'required for' in daconfig['two factor authentication'] and isinstance(daconfig['two factor authentication']['required for'], list):
    app.config['MFA_REQUIRED_FOR_ROLE'] = daconfig['two factor authentication']['required for']
else:
    app.config['MFA_REQUIRED_FOR_ROLE'] = []
app.config['MFA_ROLES'] = daconfig['two factor authentication'].get('allowed for', ['admin', 'developer'])
if not (app.config['MFA_ALLOW_SMS'] or app.config['MFA_ALLOW_APP']):
    app.config['USE_MFA'] = False
app.config['API_ROLES'] = daconfig.get('api privileges', ['admin', 'developer'])
app.config['WTF_CSRF_TIME_LIMIT'] = 604800
app.config['WTF_CSRF_SSL_STRICT'] = daconfig.get('require referer', True)
app.config['USER_APP_NAME'] = app.config['APP_NAME']
app.config['USER_SEND_PASSWORD_CHANGED_EMAIL'] = False
app.config['USER_SEND_REGISTERED_EMAIL'] = False
app.config['USER_SEND_USERNAME_CHANGED_EMAIL'] = False
app.config['USER_ENABLE_RETYPE_PASSWORD'] = True if daconfig.get('retype password', True) else False
app.config['USER_ENABLE_REMEMBER_ME'] = True if daconfig.get('enable remember me', True) else False
app.config['USER_ENABLE_EMAIL'] = True
app.config['USER_ENABLE_USERNAME'] = False
app.config['USER_ENABLE_REGISTRATION'] = True
app.config['USER_ENABLE_CHANGE_USERNAME'] = False
app.config['USER_ENABLE_CONFIRM_EMAIL'] = False
app.config['USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL'] = True
app.config['USER_AUTO_LOGIN_AFTER_REGISTER'] = True
app.config['USER_AUTO_LOGIN_AFTER_RESET_PASSWORD'] = False
app.config['USER_AFTER_FORGOT_PASSWORD_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_CHANGE_PASSWORD_ENDPOINT'] = 'after_reset'
app.config['USER_AFTER_CHANGE_USERNAME_ENDPOINT'] = 'user.login'
app.config['USER_INVITE_ENDPOINT'] = 'user_list'
app.config['USER_AFTER_CONFIRM_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_LOGIN_ENDPOINT'] = 'interview_list'
app.config['USER_AFTER_LOGOUT_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'interview_list'
app.config['USER_AFTER_RESEND_CONFIRM_EMAIL_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_RESET_PASSWORD_ENDPOINT'] = 'user.login'
app.config['USER_INVITE_URL'] = '/user/invite'
app.config['USER_ENABLE_INVITATION'] = True
app.config['USER_INVITE_EMAIL_TEMPLATE'] = 'flask_user/emails/invite'
app.config['FAVICON_MASK_COLOR'] = daconfig.get('favicon mask color', '#698aa7')
app.config['FAVICON_THEME_COLOR'] = daconfig.get('favicon theme color', '#83b3dd')

if not daconfig.get('allow registration', True):
    app.config['USER_REQUIRE_INVITATION'] = True
app.config['MAX_CONTENT_LENGTH'] = daconfig.get('maximum content length', 16 * 1024 * 1024)
app.config['USE_X_SENDFILE'] = daconfig.get('xsendfile', True)
#if daconfig.get('behind https load balancer', False):
#    app.config['PREFERRED_URL_SCHEME'] = 'https'
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
connect_string = docassemble.webapp.database.connection_string()
alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
app.config['MAILGUN_API_URL'] = daconfig['mail'].get('mailgun api url', 'https://api.mailgun.net/v3/%s/messages.mime') % daconfig['mail'].get('mailgun domain', 'NOT_USING_MAILGUN')
app.config['MAILGUN_API_KEY'] = daconfig['mail'].get('mailgun api key', None)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
