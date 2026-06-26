# ruff: noqa: F401
# pylint: disable=unused-import, wrong-import-position
import json
import sys
import os
import re
import tempfile
import tzlocal
import packaging
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base import __version__ as da_version
from docassemble.base.config import (
    daconfig,
    s3_config,
    S3_ENABLED,
    azure_config,
    AZURE_ENABLED,
    allowed,
    DEBUG_BOOT,
    boot_log,
    in_celery,
    in_cron,
    env_messages,
    errors,
    hostname,
    START_TIME,
    parse_redis_uri,
)

DEFAULT_SECRET_KEY = '38ihfiFehfoU34mcq_4clirglw3g4o87'
HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)

BAN_IP_ADDRESSES = daconfig.get('ip address ban enabled', True)

COOKIELESS_SESSIONS = daconfig.get('cookieless sessions', False)

BUTTON_COLOR_NAV_LOGIN = daconfig['button colors'].get('navigation bar login', 'primary')
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'en_US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
DEFAULT_VOICE = daconfig.get('voice', None)
if 'timezone' in daconfig and daconfig['timezone'] is not None:
    DEFAULT_TIMEZONE = daconfig['timezone']
else:
    try:
        DEFAULT_TIMEZONE = tzlocal.get_localzone_name()
    except:
        DEFAULT_TIMEZONE = 'America/New_York'


os.environ['PYTHON_EGG_CACHE'] = tempfile.gettempdir()


audio_mimetype_table = {'mp3': 'audio/mpeg', 'ogg': 'audio/ogg'}

valid_voicerss_dialects = {
    'ar': ['eg', 'sa'],
    'bg': ['bg'],
    'ca': ['es'],
    'cs': ['cz'],
    'da': ['dk'],
    'de': ['de', 'at', 'ch'],
    'el': ['gr'],
    'en': ['au', 'ca', 'gb', 'in', 'ie', 'us'],
    'es': ['mx', 'es'],
    'fi': ['fi'],
    'fr': ['ca', 'fr', 'ch'],
    'he': ['il'],
    'hi': ['in'],
    'hr': ['hr'],
    'hu': ['hu'],
    'id': ['id'],
    'it': ['it'],
    'ja': ['jp'],
    'ko': ['kr'],
    'ms': ['my'],
    'nb': ['no'],
    'nl': ['be', 'nl'],
    'pl': ['pl'],
    'pt': ['br', 'pt'],
    'ro': ['ro'],
    'ru': ['ru'],
    'sk': ['sk'],
    'sl': ['si'],
    'sv': ['se'],
    'ta': ['in'],
    'th': ['th'],
    'tr': ['tr'],
    'vi': ['vn'],
    'zh': ['cn', 'hk', 'tw']
    }

voicerss_config = daconfig.get('voicerss', None)
VOICERSS_ENABLED = not bool(not voicerss_config or ('enable' in voicerss_config and not voicerss_config['enable']) or not ('key' in voicerss_config and voicerss_config['key']))
ROOT = daconfig.get('root', '/')
# current_app.logger.warning("default sender is " + current_app.config['MAIL_DEFAULT_SENDER'] + "\n")
exit_page = daconfig.get('exitpage', 'https://docassemble.org')

SUPERVISORCTL = [daconfig.get('supervisorctl', 'supervisorctl')]
if daconfig['supervisor'].get('username', None):
    SUPERVISORCTL.extend(['--username', daconfig['supervisor']['username'], '--password', daconfig['supervisor']['password']])

# PACKAGE_CACHE = daconfig.get('packagecache', '/var/www/.cache')
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
if packaging.version.parse(daconfig.get('system version', '0.1.12')) < packaging.version.parse('1.4.0'):
    READY_FILE = daconfig.get('ready file', '/usr/share/docassemble/webapp/ready')
else:
    READY_FILE = daconfig.get('ready file', '/var/run/docassemble/ready')

UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')
PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))
FULL_PACKAGE_DIRECTORY = os.path.join(PACKAGE_DIRECTORY, 'lib', 'python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor), 'site-packages')
LOG_DIRECTORY = daconfig.get('log', '/usr/share/docassemble/log')
TTS_ENABLED = daconfig.get('enable tts', True)

PAGINATION_LIMIT = daconfig.get('pagination limit', 100)
PAGINATION_LIMIT_PLUS_ONE = PAGINATION_LIMIT + 1

# PLAYGROUND_MODULES_DIRECTORY = daconfig.get('playground_modules', )

# init_py_file = """
# __import__('pkg_resources').declare_namespace(__name__)
# """

# if not os.path.isfile(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py')):
#     with open(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py'), 'a') as the_file:
#         the_file.write(init_py_file)

# USE_PROGRESS_BAR = daconfig.get('use_progress_bar', True)
SHOW_LOGIN = daconfig.get('show login', True)
ALLOW_REGISTRATION = daconfig.get('allow registration', True)
# USER_PACKAGES = daconfig.get('user_packages', '/var/lib/docassemble/dist-packages')
# sys.path.append(USER_PACKAGES)
# if USE_PROGRESS_BAR:

if in_celery:
    LOGFILE = daconfig.get('celery flask log', '/tmp/celery-flask.log')
else:
    LOGFILE = daconfig.get('flask log', '/tmp/flask.log')
# APACHE_LOGFILE = daconfig.get('apache_log', '/var/log/apache2/error.log')

# connect_string = docassemble.webapp.database.connection_string()
# alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()

STATS = daconfig.get('collect statistics', False)
DEBUG = daconfig.get('debug', False)
ERROR_TYPES_NO_EMAIL = daconfig.get('suppress error notificiations', [])
COOKIELESS_SESSIONS = daconfig.get('cookieless sessions', False)
BAN_IP_ADDRESSES = daconfig.get('ip address ban enabled', True)
CONCURRENCY_LOCK_TIMEOUT = daconfig.get('concurrency lock timeout', 4)
DEFER = ' defer' if daconfig['javascript defer'] else ''

if DEBUG:
    PREVENT_DEMO = False
elif daconfig.get('allow demo', False):
    PREVENT_DEMO = False
else:
    PREVENT_DEMO = True

REQUIRE_IDEMPOTENT = not daconfig.get('allow non-idempotent questions', True)
STRICT_MODE = daconfig.get('restrict input variables', False)
PACKAGE_PROTECTION = daconfig.get('package protection', True)
PERMISSIONS_LIST = [
    'access_privileges',
    'access_sessions',
    'access_user_info',
    'access_user_api_info',
    'create_user',
    'delete_user',
    'demo_interviews',
    'edit_privileges',
    'edit_sessions',
    'edit_user_active_status',
    'edit_user_info',
    'edit_user_api_info',
    'edit_user_password',
    'edit_user_privileges',
    'interview_data',
    'log_user_in',
    'playground_control',
    'template_parse'
    ]

HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)
GITHUB_BRANCH = daconfig.get('github default branch name', 'main')
USE_GOOGLE_PLACES_NEW_API = daconfig['google']['use places api new']
default_yaml_filename = daconfig.get('default interview', None)
final_default_yaml_filename = daconfig.get('default interview', 'docassemble.base:data/questions/default-interview.yml')
keymap = daconfig.get('keymap', None) or 'default'
google_config = daconfig['google']
if 'google maps api key' in google_config:
    google_api_key = google_config.get('google maps api key')
elif 'api key' in google_config:
    google_api_key = google_config.get('api key')
else:
    google_api_key = None  # pylint: disable=invalid-name

default_title = daconfig.get('default title', daconfig.get('brandname', 'docassemble'))
default_short_title = daconfig.get('default short title', default_title)
PNG_RESOLUTION = daconfig.get('png resolution', 300)
PNG_SCREEN_RESOLUTION = daconfig.get('png screen resolution', 72)
PDFTOPPM_COMMAND = daconfig.get('pdftoppm', 'pdftoppm')
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'en_US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
DEFAULT_VOICE = daconfig.get('voice', None)
LOGSERVER = daconfig.get('log server', None)
CHECKIN_INTERVAL = int(daconfig.get('checkin interval', 6000))
# message_sequence = dbtableprefix + 'message_id_seq'
NOTIFICATION_CONTAINER = daconfig.get('alert container html', '<div class="datopcenter col-sm-7 col-md-6 col-lg-5" id="daflash">%s</div>')
NOTIFICATION_MESSAGE = daconfig.get('alert html', '<div class="da-alert alert alert-%s alert-dismissible fade show" role="alert">%s<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>')

USING_SUPERVISOR = bool(os.environ.get('SUPERVISOR_SERVER_URL', None))

SINGLE_SERVER = daconfig.get('single server', USING_SUPERVISOR and bool(':all:' in ':' + os.environ.get('CONTAINERROLE', 'all') + ':'))
if DEBUG_BOOT:
    boot_log("backend: configuring common functions")

classes = daconfig['table css class'].split(',')
DEFAULT_TABLE_CLASS = json.dumps(classes[0].strip())
if len(classes) > 1:
    DEFAULT_THEAD_CLASS = json.dumps(classes[1].strip())
else:
    DEFAULT_THEAD_CLASS = ''
del classes

DEFAULT_COUNTRY = daconfig.get('country', None) or re.sub(r'^.*_', '', re.sub(r'\..*', r'', DEFAULT_LOCALE))

DEBUG = daconfig.get('debug', False)

ga_configured = bool(google_config.get('analytics id', None) is not None)

if google_config.get('analytics id', None) is not None or daconfig.get('segment id', None) is not None:
    analytics_configured = True  # pylint: disable=invalid-name
    reserved_argnames = ('i', 'json', 'js_target', 'from_list', 'session', 'cache', 'reset', 'new_session', 'action', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content')
else:
    analytics_configured = False  # pylint: disable=invalid-name
    reserved_argnames = ('i', 'json', 'js_target', 'from_list', 'session', 'cache', 'reset', 'new_session', 'action')
