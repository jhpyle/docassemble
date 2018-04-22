import yaml
import os
import re
import sys
import httplib2
import socket
import pkg_resources
from docassemble.base.generate_key import random_string

# def trenv(key):
#     if os.environ[key] == 'null':
#         return None
#     elif os.environ[key] == 'true':
#         return True
#     elif os.environ[key] == 'false':
#         return False
#     return os.environ[key]

dbtableprefix = None
daconfig = dict()
s3_config = dict()
S3_ENABLED = False
gc_config = dict()
GC_ENABLED = False
azure_config = dict()
AZURE_ENABLED = False
hostname = None
loaded = False
in_celery = False

def load(**kwargs):
    global daconfig
    global s3_config
    global S3_ENABLED
    global gc_config
    global GC_ENABLED
    global azure_config
    global AZURE_ENABLED
    global dbtableprefix
    global hostname
    global loaded
    global in_celery
    # changed = False
    if 'arguments' in kwargs and kwargs['arguments'] and len(kwargs['arguments']) > 1:
        filename = kwargs['arguments'][1]
    else:
        filename = kwargs.get('filename', os.getenv('DA_CONFIG_FILE', '/usr/share/docassemble/config/config.yml'))
    if 'in_celery' in kwargs and kwargs['in_celery']:
        in_celery = True
    if not os.path.isfile(filename):
        if not os.access(os.path.dirname(filename), os.W_OK):
            sys.stderr.write("Configuration file " + str(filename) + " does not exist and cannot be created\n")
            sys.exit(1)
        with open(filename, 'w') as config_file:
            config_file.write(default_config())
            sys.stderr.write("Wrote configuration file to " + str(filename) + "\n")
    if not os.path.isfile(filename):
        sys.stderr.write("Configuration file " + str(filename) + " does not exist\n")
    with open(filename, 'rU') as stream:
        raw_daconfig = yaml.load(stream)
    if raw_daconfig is None:
        sys.stderr.write("Could not open configuration file from " + str(filename) + "\n")
        with open(filename, 'rU') as fp:
            sys.stderr.write(fp.read().decode('utf8') + "\n")
        sys.exit(1)
    daconfig.clear()
    for key, val in raw_daconfig.iteritems():
        if re.search(r'_', key):
            sys.stderr.write("WARNING!  Configuration keys should not contain underscores.  Your configuration key " + str(key) + " has been converted.\n")
            daconfig[re.sub(r'_', r' ', key)] = val
        else:
            daconfig[key] = val
    daconfig['config file'] = filename
    daconfig['python version'] = unicode(pkg_resources.get_distribution("docassemble.base").version)
    version_file = daconfig.get('version file', '/usr/share/docassemble/webapp/VERSION')
    if os.path.isfile(version_file) and os.access(version_file, os.R_OK):
        with open(version_file, 'rU') as fp:
            daconfig['system version'] = fp.read().decode('utf8').strip()
    else:
        daconfig['system version'] = '0.1.12'
    # for key in [['REDIS', 'redis'], ['RABBITMQ', 'rabbitmq'], ['EC2', 'ec2'], ['LOGSERVER', 'log server'], ['LOGDIRECTORY', 'log'], ['USEHTTPS', 'use https'], ['USELETSENCRYPT', 'use lets encrypt'], ['BEHINDHTTPSLOADBALANCER', 'behind https load balancer'], ['LETSENCRYPTEMAIL', 'lets encrypt email'], ['DAHOSTNAME', 'external hostname']]:
    #     if key[0] in os.environ:
    #         val = trenv(os.environ[key[0]])
    #         if key[1] not in daconfig or daconfig[key[1]] != val:
    #             daconfig[key[1]] = val
    #             changed = True
    if 'keymap' in daconfig and daconfig['keymap'] not in ['vim', 'emacs', 'sublime']:
        sys.stderr.write("WARNING!  You used a keymap that is not supported.  Available values are vim, emacs, and sublime.\n")
        del daconfig['keymap']
    if 'vim' in daconfig:
        sys.stderr.write("WARNING!  The configuration directive vim is deprecated.  Please use keymap instead.\n")
        if daconfig['vim'] and 'keymap' not in daconfig:
            daconfig['keymap'] = 'vim'
    # for key in [['S3BUCKET', 'bucket'], ['S3SECRETACCESSKEY', 'secret access key'], ['S3ACCESSKEY', 'access key id'], ['S3ENABLE', 'enable']]:
    #     if key[0] in os.environ:
    #         if 's3' not in daconfig:
    #             daconfig['s3'] = dict()
    #         val = trenv(os.environ[key[0]])
    #         if key[1] not in daconfig['s3'] or daconfig['s3'][key[1]] != val:
    #             daconfig['s3'][key[1]] = val
    #             changed = True
    s3_config = daconfig.get('s3', None)
    if not s3_config or ('enable' in s3_config and not s3_config['enable']):
        S3_ENABLED = False
    else:
        S3_ENABLED = True
    gc_config = daconfig.get('google cloud', None)
    if not gc_config or ('enable' in gc_config and not gc_config['enable']) or not ('access key id' in gc_config and gc_config['access key id']) or not ('secret access key' in gc_config and gc_config['secret access key']):
        GC_ENABLED = False
    else:
        GC_ENABLED = True
    # for key in [['AZURECONTAINER', 'container'], ['AZUREACCOUNTKEY', 'account key'], ['AZUREACCOUNTNAME', 'account name'], ['AZUREENABLE', 'enable']]:
    #     if key[0] in os.environ:
    #         if 'azure' not in daconfig:
    #             daconfig['azure'] = dict()
    #         val = trenv(os.environ[key[0]])
    #         if key[1] not in daconfig['azure'] or daconfig['azure'][key[1]] != val:
    #             daconfig['azure'][key[1]] = val
    #             changed = True
    azure_config = daconfig.get('azure', None)
    if type(azure_config) is not dict or ('enable' in azure_config and not azure_config['enable']) or 'account name' not in azure_config or azure_config['account name'] is None or 'account key' not in azure_config or azure_config['account key'] is None:
        AZURE_ENABLED = False
    else:
        AZURE_ENABLED = True
    if 'db' not in daconfig:
        daconfig['db'] = dict(name="docassemble", user="docassemble", password="abc123")
    # for key in [['DBPREFIX', 'prefix'], ['DBNAME', 'name'], ['DBUSER', 'user'], ['DBPASSWORD', 'password'], ['DBHOST', 'host'], ['DBPORT', 'port'], ['DBTABLEPREFIX', 'table prefix']]:
    #     if key[0] in os.environ:
    #         val = trenv(os.environ[key[0]])
    #         if key[1] not in daconfig['db'] or daconfig['db'][key[1]] != val:
    #             daconfig['db'][key[1]] = val
    #             changed = True
    dbtableprefix = daconfig['db'].get('table prefix', None)
    if not dbtableprefix:
        dbtableprefix = ''
    if daconfig.get('ec2', False):
        h = httplib2.Http()
        resp, content = h.request(daconfig.get('ec2 ip url', "http://169.254.169.254/latest/meta-data/local-hostname"), "GET")
        if resp['status'] and int(resp['status']) == 200:
            hostname = content
        else:
            sys.stderr.write("Could not get hostname from ec2\n")
            sys.exit(1)
    else:
        hostname = os.getenv('SERVERHOSTNAME', socket.gethostname())
    if S3_ENABLED:
        import docassemble.webapp.amazon
        cloud = docassemble.webapp.amazon.s3object(s3_config)
    elif AZURE_ENABLED:
        import docassemble.webapp.microsoft
        cloud = docassemble.webapp.microsoft.azureobject(azure_config)
    else:
        cloud = None
    if cloud is not None:
        if 'host' not in daconfig['db'] or daconfig['db']['host'] is None:
            key = cloud.get_key('hostname-sql')
            if key.does_exist:
                the_host = key.get_contents_as_string()
                if the_host == hostname:
                    daconfig['db']['host'] = 'localhost'
                else:
                    daconfig['db']['host'] = the_host
        if 'log server' not in daconfig or daconfig['log server'] is None:
            key = cloud.get_key('hostname-log')
            if key.does_exist:
                the_host = key.get_contents_as_string()
                if the_host == hostname:
                    daconfig['log server'] = 'localhost'
                else:
                    daconfig['log server'] = the_host
        if 'redis' not in daconfig or daconfig['redis'] is None:
            key = cloud.get_key('hostname-redis')
            if key.does_exist:
                the_host = key.get_contents_as_string()
                if the_host == hostname:
                    the_host = 'localhost'
                daconfig['redis'] = 'redis://' + the_host
        if 'rabbitmq' not in daconfig or daconfig['rabbitmq'] is None:
            key = cloud.get_key('hostname-rabbitmq')
            if key.does_exist:
                the_host = key.get_contents_as_string()
                daconfig['rabbitmq'] = 'pyamqp://guest@' + str(the_host) + '//'
    if daconfig['db'].get('prefix', None) is None or daconfig['db'].get('prefix', '') == '':
        daconfig['db']['prefix'] = 'postgresql+psycopg2://'
    if daconfig['db'].get('host', None) is None or daconfig['db'].get('host', '') == '':
        daconfig['db']['host'] = 'localhost'
    if daconfig['db'].get('name', None) is None or daconfig['db'].get('name', '') == '':
        daconfig['db']['name'] = 'docassemble'
    if daconfig['db'].get('user', None) is None or daconfig['db'].get('user', '') == '':
        daconfig['db']['user'] = 'docassemble'
    if daconfig['db'].get('password', None) is None or daconfig['db'].get('password', '') == '':
        daconfig['db']['password'] = 'abc123'
    if daconfig['db'].get('port', None) is None or daconfig['db'].get('port', '') == '':
        if daconfig['db']['prefix'].startswith('postgresql'):
            daconfig['db']['port'] = '5432'
        elif daconfig['db']['prefix'].startswith('mysql'):
            daconfig['db']['port'] = '3306'
        elif daconfig['db']['prefix'].startswith('oracle'):
            daconfig['db']['port'] = '1521'
    if 'ocr languages' not in daconfig or type(daconfig['ocr languages']) is not dict:
        daconfig['ocr languages'] = dict()
    if 'zh' not in daconfig['ocr languages']:
        daconfig['ocr languages']['zh'] = 'chi-tra'
    if 'attempt limit' not in daconfig or type(daconfig['attempt limit']) not in [int, float] or daconfig['attempt limit'] < 2:
        daconfig['attempt limit'] = 10
    if 'ban period' not in daconfig or type(daconfig['ban period']) not in [int, float] or daconfig['ban period'] < 2:
        daconfig['ban period'] = 86400
    if 'verification code digits' not in daconfig or type(daconfig['verification code digits']) not in [int, float] or daconfig['verification code digits'] < 1 or daconfig['verification code digits'] > 32:
        daconfig['verification code digits'] = 6
    if 'verification code timeout' not in daconfig or type(daconfig['verification code timeout']) not in [int, float] or daconfig['verification code timeout'] < 1:
        daconfig['verification code timeout'] = 180
    if 'api privileges' in daconfig:
        if type(daconfig['api privileges']) is not list:
            sys.stderr.write("api privileges must be in the form of a list\n")
            daconfig['api privileges'] = ['admin', 'developer']
    else:
        daconfig['api privileges'] = ['admin', 'developer']
    if 'two factor authentication privileges' in daconfig:
        if type(daconfig['two factor authentication privileges']) is not list:
            sys.stderr.write("two factor authentication privileges must be in the form of a list\n")
            daconfig['two factor authentication privileges'] = ['admin', 'developer']
    else:
        daconfig['two factor authentication privileges'] = ['admin', 'developer']
    if 'email confirmation privileges' in daconfig:
        if type(daconfig['email confirmation privileges']) is not list:
            sys.stderr.write("email confirmation privileges must be in the form of a list\n")
            daconfig['email confirmation privileges'] = []
    else:
        daconfig['email confirmation privileges'] = []
    loaded = True
    for key in ['global javascript', 'global css']:
        if key in daconfig:
            if daconfig[key] is None:
                del daconfig[key]
            elif type(daconfig[key]) is not list:
                daconfig[key] = [daconfig[key]]
    if 'password complexity' in daconfig:
        if type(daconfig['password complexity']) is dict:
            for key in ('length', 'lowercase', 'uppercase', 'digits', 'punctuation'):
                if key in daconfig['password complexity'] and type(daconfig['password complexity'][key]) is not int:
                    sys.stderr.write("password complexity key " + key + " must be an integer.\n")
                    del daconfig['password complexity'][key]
        else:
            sys.stderr.write("password complexity must be in the form of a dict.\n")
            del daconfig['password complexity']
    if 'checkin interval' in daconfig:
        if type(daconfig['checkin interval']) is not int:
            sys.stderr.write("checkin interval must be an integer.\n")
            del daconfig['checkin interval']
        elif daconfig['checkin interval'] > 0 and daconfig['checkin interval'] < 1000:
            sys.stderr.write("checkin interval must be at least 1000, if not 0.\n")
            del daconfig['checkin interval']
    if daconfig.get('default icons', None) == 'font awesome':
        daconfig['use font awesome'] = True
    if 'mail' not in daconfig:
        daconfig['mail'] = dict()
    if 'dispatch' not in daconfig or type(daconfig['dispatch']) is not dict:
        daconfig['dispatch'] = dict()
    if 'ldap login' not in daconfig or type(daconfig['ldap login']) is not dict:
        daconfig['ldap login'] = dict()
    if daconfig.get('auto resume interview', None) is not None:
        daconfig['show interviews link'] = False
    return

def default_config():
    config = """\
secretkey: """ + random_string(32) + """
mail:
  default sender: '"Administrator" <no-reply@example.com>'
"""
    return config
