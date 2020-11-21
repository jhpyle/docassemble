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
errors = list()
env_messages = list()

def env_true_false(var):
    value = str(os.getenv(var, 'false')).lower().strip()
    return value == 'true'

def env_exists(var):
    value = os.getenv(var)
    return value is not None

def env_translate(var):
    value = str(os.getenv(var)).strip()
    if value in ('true', 'True'):
        return True
    if value in ('false', 'False'):
        return False
    if value in ('null', 'None', 'Null'):
        return None
    if re.match(r'^\-?[0-9]+$', value):
        return int(value)
    return value

def override_config(the_config, messages, key, var, pre_key=None):
    value = env_translate(var)
    if value == '':
        return
    if value is None and (key in ('redis', 'rabbitmq', 'log server') or (pre_key == 'db' and key == 'host')):
        return
    if pre_key is None:
        if key in the_config and str(the_config[key]) != str(value):
            messages.append("The value of configuration key %s has been replaced with %s based on the value of environment variable %s" % (key, value, var))
        elif key not in the_config:
            messages.append("The value of configuration key %s has been set to %s based on the value of environment variable %s" % (key, value, var))
        the_config[key] = value
    else:
        if pre_key not in the_config:
            the_config[pre_key] = dict()
        if key in the_config[pre_key] and str(the_config[pre_key][key]) != str(value):
            messages.append("The value of configuration key %s in %s has been replaced with %s based on the value of environment variable %s" % (key, pre_key, value, var))
        elif key not in the_config[pre_key]:
            messages.append("The value of configuration key %s in %s has been set to %s based on the value of environment variable %s" % (key, pre_key, value, var))
        the_config[pre_key][key] = value

def config_error(error):
    errors.append(error)
    sys.stderr.write(error + "\n")

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
    global env_messages
    # changed = False
    if 'arguments' in kwargs and kwargs['arguments'] and len(kwargs['arguments']) > 1 and kwargs['arguments'][1] != '':
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
        sys.stderr.write("Configuration file " + str(filename) + " does not exist.  Trying default instead.\n")
        filename = '/usr/share/docassemble/config/config.yml'
    if not os.path.isfile(filename):
        sys.stderr.write("Configuration file " + str(filename) + " does not exist.\n")
        sys.exit(1)
    with open(filename, 'rU', encoding='utf-8') as stream:
        raw_daconfig = yaml.load(stream, Loader=yaml.FullLoader)
    if raw_daconfig is None:
        sys.stderr.write("Could not open configuration file from " + str(filename) + "\n")
        with open(filename, 'rU', encoding='utf-8') as fp:
            sys.stderr.write(fp.read() + "\n")
        sys.exit(1)
    daconfig.clear()
    for key, val in raw_daconfig.items():
        if re.search(r'_', key):
            config_error("Configuration keys may not contain underscores.  Your configuration key " + str(key) + " has been converted.")
            daconfig[re.sub(r'_', r' ', key)] = val
        else:
            daconfig[key] = val
    daconfig['config file'] = filename
    if 'modules' not in daconfig:
        daconfig['modules'] = os.getenv('DA_PYTHON', '/usr/share/docassemble/local' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))
    daconfig['python version'] = str(pkg_resources.get_distribution("docassemble.base").version)
    version_file = daconfig.get('version file', '/usr/share/docassemble/webapp/VERSION')
    if os.path.isfile(version_file) and os.access(version_file, os.R_OK):
        with open(version_file, 'rU', encoding='utf-8') as fp:
            daconfig['system version'] = fp.read().strip()
    else:
        daconfig['system version'] = '0.1.12'
    # for key in [['REDIS', 'redis'], ['RABBITMQ', 'rabbitmq'], ['EC2', 'ec2'], ['LOGSERVER', 'log server'], ['LOGDIRECTORY', 'log'], ['USEHTTPS', 'use https'], ['USELETSENCRYPT', 'use lets encrypt'], ['BEHINDHTTPSLOADBALANCER', 'behind https load balancer'], ['LETSENCRYPTEMAIL', 'lets encrypt email'], ['DAHOSTNAME', 'external hostname']]:
    #     if key[0] in os.environ:
    #         val = trenv(os.environ[key[0]])
    #         if key[1] not in daconfig or daconfig[key[1]] != val:
    #             daconfig[key[1]] = val
    #             changed = True
    if env_true_false('ENVIRONMENT_TAKES_PRECEDENCE'):
        null_messages = list()
        for env_var, key in (('S3ENABLE', 'enable'), ('S3ACCESSKEY', 'access key id'), ('S3SECRETACCESSKEY', 'secret access key'), ('S3BUCKET', 'bucket'), ('S3REGION', 'region'), ('S3ENDPOINTURL', 'endpoint url')):
            if env_exists(env_var):
                override_config(daconfig, null_messages, key, env_var, pre_key='s3')
        for env_var, key in (('AZUREENABLE', 'enable'), ('AZUREACCOUNTKEY', 'account key'), ('AZUREACCOUNTNAME', 'account name'), ('AZURECONTAINER', 'container')):
            if env_exists(env_var):
                override_config(daconfig, null_messages, key, env_var, pre_key='azure')
        if env_exists('KUBERNETES'):
            override_config(daconfig, null_messages, 'kubernetes', 'KUBERNETES')
    if 'maximum content length' in daconfig:
        if isinstance(daconfig['maximum content length'], (int, type(None))):
            if daconfig['maximum content length'] is not None and daconfig['maximum content length'] <= 0:
                daconfig['maximum content length'] = None
        else:
            config_error("The maximum content length must be an integer number of bytes, or null.")
            del daconfig['maximum content length']
    if 'social' not in daconfig or not isinstance(daconfig['social'], dict):
        daconfig['social'] = dict()
    if 'twitter' not in daconfig['social'] or not isinstance(daconfig['social']['twitter'], dict):
        daconfig['social']['twitter'] = dict()
    if 'og' not in daconfig['social'] or not isinstance(daconfig['social']['og'], dict):
        daconfig['social']['og'] = dict()
    if 'fb' not in daconfig['social'] or not isinstance(daconfig['social']['fb'], dict):
        daconfig['social']['fb'] = dict()
    for key in list(daconfig['social'].keys()):
        if key in ('og', 'twitter', 'fb'):
            continue
        if (not isinstance(daconfig['social'][key], str)) or daconfig['social'][key].strip() == '':
            del daconfig['social'][key]
        else:
            daconfig['social'][key] = noquote(daconfig['social'][key])
    for part in ('og', 'fb', 'twitter'):
        for key in list(daconfig['social'][part].keys()):
            if (not isinstance(daconfig['social'][part][key], str)) or daconfig['social'][part][key].strip() == '':
                del daconfig['social'][part][key]
            else:
                daconfig['social'][part][key] = noquote(daconfig['social'][part][key])
    if 'name' in daconfig['social']:
        del daconfig['social']['name']
    if 'title' in daconfig['social']['og']:
        del daconfig['social']['og']['title']
    if 'title' in daconfig['social']['twitter']:
        del daconfig['social']['twitter']['title']
    if 'url' in daconfig['social']['og']:
        del daconfig['social']['og']['url']
    if 'administrative interviews' in daconfig:
        new_admin_interviews = list()
        for item in daconfig['administrative interviews']:
            if isinstance(item, str):
                new_admin_interviews.append(dict(interview=item))
            else:
                new_admin_interviews.append(item)
        daconfig['administrative interviews'] = new_admin_interviews
    if 'session lifetime seconds' in daconfig:
        try:
            daconfig['session lifetime seconds'] = int(daconfig['session lifetime seconds'])
            assert daconfig['session lifetime seconds'] > 0
        except:
            config_error("Invalid session lifetime seconds.")
            del daconfig['session lifetime seconds']
    if 'pagination limit' in daconfig:
        try:
            assert isinstance(daconfig['pagination limit'], int)
            assert daconfig['pagination limit'] > 1
            assert daconfig['pagination limit'] < 1001
        except:
            daconfig['pagination limit'] = 100
    if 'page after login' in daconfig:
        if isinstance(daconfig['page after login'], str):
            daconfig['page after login'] = [{'*': daconfig['page after login']}]
        if isinstance(daconfig['page after login'], dict):
            daconfig['page after login'] = [daconfig['page after login']]
        page_after_login = []
        if isinstance(daconfig['page after login'], list):
            for item in daconfig['page after login']:
                if isinstance(item, dict):
                    for key, val in item.items():
                        if isinstance(key, str) and isinstance(val, str):
                            page_after_login.append((key, val))
                        else:
                            config_error('page after login keys and values must be strings')
                else:
                    config_error('page after login items must be dictionaries')
        else:
            config_error('page after login must be a string, a list, or a dict')
        daconfig['page after login'] = page_after_login
    else:
        daconfig['page after login'] = []
    if 'keymap' in daconfig and daconfig['keymap'] not in ['vim', 'emacs', 'sublime']:
        config_error("You used a keymap that is not supported.  Available values are vim, emacs, and sublime.")
        del daconfig['keymap']
    if 'voicerss' in daconfig:
        if isinstance(daconfig['voicerss'], dict):
            if 'languages' in daconfig['voicerss']:
                daconfig['voicerss']['dialects'] = daconfig['voicerss']['languages']
                del daconfig['voicerss']['languages']
        else:
            config_error('voicerss must be a dict')
            del daconfig['voicerss']
    if 'cross site domain' in daconfig and 'cross site domains' not in daconfig:
        daconfig['cross site domains'] = [daconfig['cross site domain'].strip()]
        del daconfig['cross site domain']
    if 'cross site domains' in daconfig:
        if isinstance(daconfig['cross site domains'], list):
            for item in daconfig['cross site domains']:
                if not isinstance(item, str):
                    config_error("The configuration directive cross site domains must be a list of strings.")
                    del daconfig['cross site domains']
                    break
            if len(daconfig['cross site domains']) == 1 and daconfig['cross site domains'] == '*':
                daconfig['cross site domains'] = '*'
        else:
            config_error("The configuration directive cross site domains must be a list.")
            del daconfig['cross site domains']
    if 'vim' in daconfig:
        config_error("The configuration directive vim is deprecated.  Please use keymap instead.")
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
    if 'azure' in daconfig and not isinstance(daconfig['azure'], dict):
        config_error('azure must be a dict')
    azure_config = daconfig.get('azure', None)
    if not isinstance(azure_config, dict) or ('enable' in azure_config and not azure_config['enable']) or 'account name' not in azure_config or azure_config['account name'] is None or 'account key' not in azure_config or azure_config['account key'] is None:
        AZURE_ENABLED = False
    else:
        AZURE_ENABLED = True
    if 'db' not in daconfig:
        daconfig['db'] = dict(name="docassemble", user="docassemble", password="abc123")
    dbtableprefix = daconfig['db'].get('table prefix', None)
    if not dbtableprefix:
        dbtableprefix = ''
    if daconfig.get('ec2', False) or (env_true_false('ENVIRONMENT_TAKES_PRECEDENCE') and env_true_false('EC2')):
        h = httplib2.Http()
        resp, content = h.request(daconfig.get('ec2 ip url', "http://169.254.169.254/latest/meta-data/local-hostname"), "GET")
        if resp['status'] and int(resp['status']) == 200:
            hostname = content.decode()
        else:
            config_error("Could not get hostname from ec2")
            sys.exit(1)
    elif daconfig.get('kubernetes', False) or (env_true_false('ENVIRONMENT_TAKES_PRECEDENCE') and env_true_false('KUBERNETES')):
        hostname = socket.gethostbyname(socket.gethostname())
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
    if 'ocr languages' not in daconfig:
        daconfig['ocr languages'] = dict()
    if not isinstance(daconfig['ocr languages'], dict):
        config_error('ocr languages must be a dict')
        daconfig['ocr languages'] = dict()
    if 'zh' not in daconfig['ocr languages']:
        daconfig['ocr languages']['zh'] = 'chi-tra'
    if 'attempt limit' not in daconfig:
        daconfig['attempt limit'] = 10
    if not isinstance(daconfig['attempt limit'], (int, float)):
        config_error('attempt limit must be a number')
        daconfig['attempt limit'] = 10
    if daconfig['attempt limit'] < 2:
        config_error('attempt limit cannot be less than 2')
        daconfig['attempt limit'] = 10
    if 'ban period' not in daconfig:
        daconfig['ban period'] = 86400
    if not isinstance(daconfig['ban period'], (int, float)):
        config_error('ban period must be a number')
        daconfig['ban period'] = 86400
    if daconfig['ban period'] < 2:
        config_error('ban period cannot be less than 2')
        daconfig['ban period'] = 86400
    if 'verification code digits' not in daconfig:
        daconfig['verification code digits'] = 6
    if not isinstance(daconfig['verification code digits'], (int, float)):
        config_error('verification code digits must be a number')
        daconfig['verification code digits'] = 6
    if daconfig['verification code digits'] < 1 or daconfig['verification code digits'] > 32:
        config_error('verification code digits must be between 1 and 32')
        daconfig['verification code digits'] = 6
    if 'verification code timeout' not in daconfig:
        daconfig['verification code timeout'] = 180
    if not isinstance(daconfig['verification code timeout'], (int, float)):
        config_error('verification code timeout must be a number')
        daconfig['verification code timeout'] = 180
    if daconfig['verification code timeout'] < 1:
        config_error('verification code timeout must be one or greater')
        daconfig['verification code timeout'] = 180
    if 'api privileges' in daconfig:
        if not isinstance(daconfig['api privileges'], list):
            config_error("api privileges must be in the form of a list")
            daconfig['api privileges'] = ['admin', 'developer']
    else:
        daconfig['api privileges'] = ['admin', 'developer']
    if 'two factor authentication' in daconfig:
        if isinstance(daconfig['two factor authentication'], bool):
            daconfig['two factor authentication'] = dict(enable=daconfig['two factor authentication'])
        if not isinstance(daconfig['two factor authentication'], dict):
            config_error('two factor authentication must be boolean or a dict')
            daconfig['two factor authentication'] = dict()
    else:
        daconfig['two factor authentication'] = dict(enable=False)
    if 'allowed for' in daconfig['two factor authentication']:
        if not isinstance(daconfig['two factor authentication']['allowed for'], list):
            config_error("two factor authentication allowed for must be in the form of a list")
            daconfig['two factor authentication']['allowed for'] = ['admin', 'developer']
    else:
        if 'two factor authentication privileges' in daconfig:
            if isinstance(daconfig['two factor authentication privileges'], list):
                daconfig['two factor authentication']['allowed for'] = daconfig['two factor authentication privileges']
            else:
                config_error("two factor authentication privileges must be in the form of a list")
                daconfig['two factor authentication']['allowed for'] = ['admin', 'developer']
        else:
            daconfig['two factor authentication']['allowed for'] = ['admin', 'developer']
    if 'email confirmation privileges' in daconfig:
        if not isinstance(daconfig['email confirmation privileges'], list):
            config_error("email confirmation privileges must be in the form of a list")
            daconfig['email confirmation privileges'] = []
    else:
        daconfig['email confirmation privileges'] = []
    loaded = True
    for key in ['global javascript', 'global css']:
        if key in daconfig:
            if daconfig[key] is None:
                del daconfig[key]
            elif not isinstance(daconfig[key], list):
                daconfig[key] = [daconfig[key]]
    if 'password complexity' in daconfig:
        if isinstance(daconfig['password complexity'], dict):
            for key in ('length', 'lowercase', 'uppercase', 'digits', 'punctuation'):
                if key in daconfig['password complexity'] and not isinstance(daconfig['password complexity'][key], int):
                    config_error("password complexity key " + key + " must be an integer.")
                    del daconfig['password complexity'][key]
        else:
            config_error("password complexity must be in the form of a dict.")
            del daconfig['password complexity']
    if 'checkin interval' in daconfig:
        if not isinstance(daconfig['checkin interval'], int):
            config_error("checkin interval must be an integer.")
            del daconfig['checkin interval']
        elif daconfig['checkin interval'] > 0 and daconfig['checkin interval'] < 1000:
            config_error("checkin interval must be at least 1000, if not 0.")
            del daconfig['checkin interval']
    if daconfig.get('checkin interval', 5) == 0:
        daconfig['enable monitor'] = False
    else:
        daconfig['enable monitor'] = True
    if daconfig.get('default icons', None) == 'font awesome':
        daconfig['use font awesome'] = True
    if 'websockets port' in daconfig and daconfig['websockets port']:
        try:
            daconfig['websockets port'] = int(daconfig['websockets port'])
        except:
            config_error("websockets port must be an integer")
            del daconfig['websockets port']
    if 'mail' not in daconfig:
        daconfig['mail'] = dict()
    if 'dispatch' not in daconfig:
        daconfig['dispatch'] = dict()
    if not isinstance(daconfig['dispatch'], dict):
        config_error("dispatch must be structured as a dictionary")
        daconfig['dispatch'] = dict()
    if 'ldap login' not in daconfig:
        daconfig['ldap login'] = dict()
    if not isinstance(daconfig['ldap login'], dict):
        config_error("ldap login must be structured as a dictionary")
        daconfig['ldap login'] = dict()
    if daconfig.get('auto resume interview', None) is not None:
        daconfig['show interviews link'] = False
    if 'use minio' not in daconfig:
        daconfig['use minio'] = False
    if 'server administrator email' not in daconfig or not daconfig['server administrator email']:
        daconfig['server administrator email'] = 'webmaster@localhost'
    if 'use cloud urls' not in daconfig:
        daconfig['use cloud urls'] = False
    else:
        daconfig['use cloud urls'] = True if daconfig['use cloud urls'] else False
    if 'use https' not in daconfig or not daconfig['use https']:
        daconfig['use https'] = False
    if 'use lets encrypt' not in daconfig or not daconfig['use lets encrypt']:
        daconfig['use lets encrypt'] = False
    if 'behind https load balancer' not in daconfig or not daconfig['behind https load balancer']:
        daconfig['behind https load balancer'] = False
    if 'websockets ip' in daconfig and not daconfig['websockets ip']:
        del daconfig['websockets ip']
    if 'websockets port' not in daconfig or not daconfig['websockets port']:
        daconfig['websockets port'] = 5000
    if 'root' not in daconfig or not daconfig['root']:
        daconfig['root'] = '/'
    if 'web server' not in daconfig or not daconfig['web server']:
        daconfig['web server'] = 'nginx'
    if 'table css class' not in daconfig or not isinstance(daconfig['table css class'], str):
        daconfig['table css class'] = 'table table-striped'
    if env_true_false('ENVIRONMENT_TAKES_PRECEDENCE'):
        messages = list()
        for env_var, key in (('DBPREFIX', 'prefix'), ('DBNAME', 'name'), ('DBUSER', 'user'), ('DBPASSWORD', 'password'), ('DBHOST', 'host'), ('DBPORT', 'port'), ('DBTABLEPREFIX', 'table prefix'), ('DBBACKUP', 'backup')):
            if env_exists(env_var):
                override_config(daconfig, messages, key, env_var, pre_key='db')
        if env_exists('DASECRETKEY'):
            override_config(daconfig, messages, 'secretkey', 'DASECRETKEY')
            daconfig['secretkey'] = env_translate('DASECRETKEY')
        if env_exists('DABACKUPDAYS'):
            override_config(daconfig, messages, 'backup days', 'DABACKUPDAYS')
        if env_exists('DASTABLEVERSION'):
            override_config(daconfig, messages, 'stable version', 'DASTABLEVERSION')
        if env_exists('DASSLPROTOCOLS'):
            override_config(daconfig, messages, 'nginx ssl protocols', 'DASSLPROTOCOLS')
        if env_exists('SERVERADMIN'):
            override_config(daconfig, messages, 'server administrator email', 'SERVERADMIN')
        if env_exists('LOCALE'):
            override_config(daconfig, messages, 'os locale', 'LOCALE')
        if env_exists('TIMEZONE'):
            override_config(daconfig, messages, 'timezone', 'TIMEZONE')
        if env_exists('REDIS'):
            override_config(daconfig, messages, 'redis', 'REDIS')
        if env_exists('RABBITMQ'):
            override_config(daconfig, messages, 'rabbitmq', 'RABBITMQ')
        for env_var, key in (('S3ENABLE', 'enable'), ('S3ACCESSKEY', 'access key id'), ('S3SECRETACCESSKEY', 'secret access key'), ('S3BUCKET', 'bucket'), ('S3REGION', 'region'), ('S3ENDPOINTURL', 'endpoint url')):
            if env_exists(env_var):
                override_config(daconfig, messages, key, env_var, pre_key='s3')
        for env_var, key in (('AZUREENABLE', 'enable'), ('AZUREACCOUNTKEY', 'account key'), ('AZUREACCOUNTNAME', 'account name'), ('AZURECONTAINER', 'container')):
            if env_exists(env_var):
                override_config(daconfig, messages, key, env_var, pre_key='azure')
        if env_exists('EC2'):
            override_config(daconfig, messages, 'ec2', 'EC2')
        if env_exists('COLLECTSTATISTICS'):
            override_config(daconfig, messages, 'collect statistics', 'COLLECTSTATISTICS')
        if env_exists('KUBERNETES'):
            override_config(daconfig, messages, 'kubernetes', 'KUBERNETES')
        if env_exists('LOGSERVER'):
            override_config(daconfig, messages, 'log server', 'LOGSERVER')
        if env_exists('USECLOUDURLS'):
            override_config(daconfig, messages, 'use cloud urls', 'USECLOUDURLS')
        if env_exists('USEMINIO'):
            override_config(daconfig, messages, 'use minio', 'USEMINIO')
        if env_exists('USEHTTPS'):
            override_config(daconfig, messages, 'use https', 'USEHTTPS')
        if env_exists('USELETSENCRYPT'):
            override_config(daconfig, messages, 'use lets encrypt', 'USELETSENCRYPT')
        if env_exists('LETSENCRYPTEMAIL'):
            override_config(daconfig, messages, 'lets encrypt email', 'LETSENCRYPTEMAIL')
        if env_exists('BEHINDHTTPSLOADBALANCER'):
            override_config(daconfig, messages, 'behind https load balancer', 'BEHINDHTTPSLOADBALANCER')
        if env_exists('XSENDFILE'):
            override_config(daconfig, messages, 'xsendfile', 'XSENDFILE')
        if env_exists('DAUPDATEONSTART'):
            override_config(daconfig, messages, 'update on start', 'DAUPDATEONSTART')
        if env_exists('URLROOT'):
            override_config(daconfig, messages, 'url root', 'URLROOT')
        if env_exists('DAHOSTNAME'):
            override_config(daconfig, messages, 'external hostname', 'DAHOSTNAME')
        if env_exists('DAEXPOSEWEBSOCKETS'):
            override_config(daconfig, messages, 'expose websockets', 'DAEXPOSEWEBSOCKETS')
        if env_exists('DAWEBSOCKETSIP'):
            override_config(daconfig, messages, 'websockets ip', 'DAWEBSOCKETSIP')
        if env_exists('DAWEBSOCKETSPORT'):
            override_config(daconfig, messages, 'websockets port', 'DAWEBSOCKETSPORT')
        if env_exists('POSTURLROOT'):
            override_config(daconfig, messages, 'root', 'POSTURLROOT')
        if env_exists('DAWEBSERVER'):
            override_config(daconfig, messages, 'web server', 'DAWEBSERVER')
        if env_exists('DASQLPING'):
            override_config(daconfig, messages, 'sql ping', 'DASQLPING')
        env_messages = messages
    return

def default_config():
    config = """\
secretkey: """ + random_string(32) + """
mail:
  default sender: '"Administrator" <no-reply@example.com>'
"""
    return config

def parse_redis_uri():
    redis_host = daconfig.get('redis', None)
    if redis_host is None:
        redis_host = 'redis://localhost'
    redis_host = redis_host.strip()
    if not redis_host.startswith('redis://'):
        redis_host = 'redis://' + redis_host
    m = re.search(r'redis://([^:@\?]*):([^:@\?]*)@(.*)', redis_host)
    if m:
        redis_password = m.group(2)
        redis_host = 'redis://' + m.group(3)
    else:
        redis_password = None
    m = re.search(r'[?\&]password=([^&]+)', redis_host)
    if m:
        redis_password = m.group(1)
    m = re.search(r'[?\&]db=([0-9]+)', redis_host)
    if m:
        redis_db = int(m.group(1))
    else:
        redis_db = 0

    redis_host = re.sub(r'\?.*', '', redis_host)
    redis_host = re.sub(r'^redis://', r'', redis_host)
    m = re.search(r'/([0-9]+)', redis_host)
    if m:
        redis_db = int(m.group(1))
    redis_host = re.sub(r'/.*', r'', redis_host)
    m = re.search(r':([0-9]+)$', redis_host)
    if m:
        redis_port = m.group(1)
        redis_host = re.sub(r':([0-9]+)$', '', redis_host)
    else:
        redis_port = '6379'

    redis_offset = daconfig.get('redis database offset', redis_db)
    redis_cli = 'redis-cli'
    if redis_host != 'localhost' or redis_port != '6379':
        redis_cli += ' -h ' + redis_host + ' -p ' + redis_port
    if redis_password is not None:
        redis_cli += ' -a ' + redis_password
    return (redis_host, redis_port, redis_password, redis_offset, redis_cli)

def noquote(string):
    if isinstance(string, str):
        return string.replace('\n', ' ').replace('"', '&quot;').strip()
    return string
