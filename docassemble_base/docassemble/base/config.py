import os
import re
import sys
import socket
import threading
import time
import base64
import json
import importlib.metadata
from packaging import version
import yaml
import httplib2
import boto3
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import docassemble.base.amazon
import docassemble.base.microsoft
from docassemble.base.generate_key import random_string

START_TIME = time.time()
dbtableprefix = None
daconfig = {}
s3_config = {}
S3_ENABLED = False
gc_config = {}
GC_ENABLED = False
azure_config = {}
AZURE_ENABLED = False
hostname = None
loaded = False
in_celery = False
in_cron = False
errors = []
env_messages = []
allowed = {}
DEBUG_BOOT = False


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
        root = the_config
        for the_key in pre_key:
            if the_key not in root:
                root[the_key] = {}
            root = root[the_key]
        if key in root and str(root[key]) != str(value):
            messages.append("The value of configuration key %s in %s has been replaced with %s based on the value of environment variable %s" % (key, ", ".join(pre_key), value, var))
        elif key not in root:
            messages.append("The value of configuration key %s in %s has been set to %s based on the value of environment variable %s" % (key, ", ".join(pre_key), value, var))
        root[key] = value


def config_error(error):
    errors.append(error)
    sys.stderr.write(error + "\n")


def cleanup_filename(filename):
    filename = filename.strip()
    parts = filename.split(':')
    if len(parts) != 2 or re.search(r'\s', parts[0]):
        return None
    if not parts[0].startswith('docassemble.playground') and not parts[1].startswith('data/questions/'):
        return parts[0] + ':' + 'data/questions/' + parts[1]
    return filename


def delete_environment():
    for var in ('AWS_ACCESS_KEY_ID', 'AWS_DEFAULT_REGION', 'AWS_SECRET_ACCESS_KEY', 'AZUREACCOUNTKEY', 'AZUREACCOUNTNAME', 'AZURECONNECTIONSTRING', 'AZURECONTAINER', 'AZUREENABLE', 'BEHINDHTTPSLOADBALANCER', 'COLLECTSTATISTICS', 'DAALLOWCONFIGURATIONEDITING', 'DAALLOWLOGVIEWING', 'DAALLOWUPDATES', 'DABACKUPDAYS', 'DACELERYWORKERS', 'DADEBUG', 'DAENABLEPLAYGROUND', 'DAEXPOSEWEBSOCKETS', 'DAHOSTNAME', 'DAMAXCELERYWORKERS', 'DAMAXCONTENTLENGTH', 'DAREADONLYFILESYSTEM', 'DAROOTOWNED', 'DASECRETKEY', 'DASQLPING', 'DASSLPROTOCOLS', 'DASTABLEVERSION', 'DASUPERVISORPASSWORD', 'DASUPERVISORUSERNAME', 'DATIMEOUT', 'DAUPDATEONSTART', 'DAWEBSERVER', 'DAWEBSOCKETSIP', 'DAWEBSOCKETSPORT', 'DBBACKUP', 'DBHOST', 'DBNAME', 'DBPASSWORD', 'DBPORT', 'DBPREFIX', 'DBSSLCERT', 'DBSSLKEY', 'DBSSLMODE', 'DBSSLROOTCERT', 'DBTABLEPREFIX', 'DBTYPE', 'DBUSER', 'EC2', 'ENVIRONMENT_TAKES_PRECEDENCE', 'KUBERNETES', 'LETSENCRYPTEMAIL', 'LOGSERVER', 'OTHERLOCALES', 'PACKAGES', 'PIPEXTRAINDEXURLS', 'PIPINDEXURL', 'PORT', 'POSTURLROOT', 'PYTHONPACKAGES', 'RABBITMQ', 'REDIS', 'REDISCLI', 'S3ACCESSKEY', 'S3BUCKET', 'S3ENABLE', 'S3ENDPOINTURL', 'S3REGION', 'S3SECRETACCESSKEY', 'S3_SSE_ALGORITHM', 'S3_SSE_CUSTOMER_ALGORITHM', 'S3_SSE_CUSTOMER_KEY', 'S3_SSE_KMS_KEY_ID', 'S4CMD_OPTS', 'SERVERADMIN', 'URLROOT', 'USECLOUDURLS', 'USEHTTPS', 'USELETSENCRYPT', 'USEMINIO', 'WSGIROOT', 'XSENDFILE'):
        if var in os.environ:
            del os.environ[var]

this_thread = threading.local()
this_thread.botoclient = {}
this_thread.azureclient = {}


def aws_get_region(arn):
    m = re.search(r'arn:aws:secretsmanager:([^:]+):', arn)
    if m:
        return m.group(1)
    return 'us-east-1'


def aws_get_secret(data):
    region = aws_get_region(data)
    if region not in this_thread.botoclient:
        if env_exists('AWSACCESSKEY') and env_exists('AWSSECRETACCESSKEY'):
            sys.stderr.write("Using access keys\n")
            session = boto3.session.Session(aws_access_key_id=os.environ['AWSACCESSKEY'], aws_secret_access_key=os.environ['AWSSECRETACCESSKEY'])
        else:
            sys.stderr.write("Not using access keys\n")
            session = boto3.session.Session()
        this_thread.botoclient[region] = session.client(
            service_name='secretsmanager',
            region_name=region
        )
    try:
        response = this_thread.botoclient[region].get_secret_value(SecretId=data)
    except BaseException as e:
        if e.__class__.__name__ == 'ClientError':
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                sys.stderr.write("aws_get_secret: Secrets Manager can't decrypt the protected secret text using the provided KMS key.\n")
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                sys.stderr.write("aws_get_secret: An error occurred on the server side.\n")
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                sys.stderr.write("aws_get_secret: You provided an invalid value for a parameter.\n")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                sys.stderr.write("aws_get_secret: You provided a parameter value that is not valid for the current state of the resource.\n")
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                sys.stderr.write("aws_get_secret: We can't find the resource that you asked for.")
            else:
                sys.stderr.write("aws_get_secret: " + e.__class__.__name__ + ": " + str(e) + "\n")
        else:
            sys.stderr.write("aws_get_secret: " + e.__class__.__name__ + ": " + str(e) + "\n")
        return data
    if 'SecretString' in response:
        result = response['SecretString']
    else:
        result = base64.b64decode(response['SecretBinary'])
    try:
        result = json.loads(result)
    except:
        sys.stderr.write("aws_get_secret: problem decoding JSON\n")
    return result


def azure_get_secret(data):
    vault_name = None
    secret_name = None
    secret_version = None
    m = re.search(r'^@Microsoft.KeyVault\(([^\)]+)\)', data)
    if m:
        parts = m.group(1).split(';')
        for part in parts:
            mm = re.search(r'^([^=]+)=(.*)', part)
            if mm:
                if mm.group(1) == 'VaultName':
                    vault_name = mm.group(2)
                elif mm.group(1) == 'SecretName':
                    secret_name = mm.group(2)
                elif mm.group(1) == 'SecretVersion':
                    secret_version = mm.group(2)
                elif mm.group(1) == 'SecretUri':
                    mmm = re.search(r'https://([^\.]+).vault.azure.net/secrets/([^\/]+)/?$', mm.group(2))
                    if mmm:
                        vault_name = mmm.group(1)
                        secret_name = mmm.group(2)
                    else:
                        mmmm = re.search(r'https://([^\.]+).vault.azure.net/secrets/([^\/]+)/([^\/]+)/?$', mm.group(2))
                        if mmmm:
                            vault_name = mmmm.group(1)
                            secret_name = mmmm.group(2)
                            secret_version = mmmm.group(3)
    if vault_name is None or secret_name is None:
        return data
    if vault_name not in this_thread.azureclient:
        try:
            credential = DefaultAzureCredential()
            this_thread.azureclient[vault_name] = SecretClient(vault_url="https://" + vault_name + ".vault.azure.net/", credential=credential)
        except BaseException as err:
            sys.stderr.write("azure_get_secret: unable to create key vault client: " + err.__class__.__name__ + str(err) + "\n")
            return data
    try:
        if secret_version is not None:
            secret_data = this_thread.azureclient[vault_name].get_secret(secret_name, secret_version)
        else:
            secret_data = this_thread.azureclient[vault_name].get_secret(secret_name)
    except BaseException as err:
        sys.stderr.write("azure_get_secret: unable to retrieve secret: " + err.__class__.__name__ + str(err) + "\n")
        return data
    if isinstance(secret_data.properties.content_type, str):
        if secret_data.properties.content_type == 'application/json':
            try:
                data = json.loads(secret_data.value)
            except:
                sys.stderr.write("azure_get_secret: problem decoding JSON\n")
                data = secret_data.value
        elif secret_data.properties.content_type in ('application/x-yaml', 'application/yaml'):
            try:
                data = yaml.load(secret_data.value, Loader=yaml.FullLoader)
            except:
                sys.stderr.write("azure_get_secret: problem decoding YAML\n")
                data = secret_data.value
        else:
            data = secret_data.value
    else:
        data = secret_data.value
    return data


def recursive_fetch_cloud(data):
    if isinstance(data, str):
        if data.startswith('arn:aws:secretsmanager:'):
            data = aws_get_secret(data.strip())
        elif data.startswith('@Microsoft.KeyVault('):
            data = azure_get_secret(data.strip())
        return data
    if isinstance(data, (int, float, bool)):
        return data
    if isinstance(data, list):
        return [recursive_fetch_cloud(y) for y in data]
    if isinstance(data, dict):
        return {k: recursive_fetch_cloud(v) for k, v in data.items()}
    if isinstance(data, set):
        return {recursive_fetch_cloud(y) for y in data}
    if isinstance(data, tuple):
        return tuple(recursive_fetch_cloud(y) for y in data)
    return data


def fix_authorized_domain(domain):
    return '@' + re.sub(r'^@+', '', domain.lower().strip())


def load(**kwargs):
    global daconfig
    global s3_config
    global S3_ENABLED
    global gc_config
    global GC_ENABLED
    global azure_config
    global AZURE_ENABLED
    global DEBUG_BOOT
    global dbtableprefix
    global hostname
    global loaded
    global in_celery
    global in_cron
    global env_messages
    # changed = False
    filename = None
    container_role = os.environ.get('CONTAINERROLE', None) or ':all:'
    single_server = ':all:' in container_role
    if 'arguments' in kwargs and isinstance(kwargs['arguments'], list) and len(kwargs['arguments']) > 1:
        for arg in kwargs['arguments'][1:]:
            if arg.startswith('--'):
                continue
            if os.path.isfile(arg):
                filename = arg
    if filename is None:
        filename = kwargs.get('filename', os.getenv('DA_CONFIG_FILE', '/usr/share/docassemble/config/config.yml'))
    if 'in_celery' in kwargs and kwargs['in_celery']:
        in_celery = True
    if 'in_cron' in kwargs and kwargs['in_cron']:
        in_cron = True
    if not os.path.isfile(filename):
        if not os.access(os.path.dirname(filename), os.W_OK):
            sys.stderr.write("Configuration file " + str(filename) + " does not exist and cannot be created\n")
            sys.exit(1)
        with open(filename, 'w', encoding='utf-8') as config_file:
            config_file.write(default_config())
            sys.stderr.write("Wrote configuration file to " + str(filename) + "\n")
    if not os.path.isfile(filename):
        sys.stderr.write("Configuration file " + str(filename) + " does not exist.  Trying default instead.\n")
        filename = '/usr/share/docassemble/config/config.yml'
    if not os.path.isfile(filename):
        sys.stderr.write("Configuration file " + str(filename) + " does not exist.\n")
        sys.exit(1)
    with open(filename, 'r', encoding='utf-8') as stream:
        raw_daconfig = yaml.load(stream, Loader=yaml.FullLoader)
    if raw_daconfig is None:
        sys.stderr.write("Could not open configuration file from " + str(filename) + "\n")
        with open(filename, 'r', encoding='utf-8') as fp:
            sys.stderr.write(fp.read() + "\n")
        sys.exit(1)
    daconfig.clear()
    raw_daconfig = recursive_fetch_cloud(raw_daconfig)
    if raw_daconfig.get('config from', None) and isinstance(raw_daconfig['config from'], dict):
        raw_daconfig.update(raw_daconfig['config from'])
        del raw_daconfig['config from']
    for key, val in raw_daconfig.items():
        if re.search(r'_', key):
            config_error("Configuration keys may not contain underscores.  Your configuration key " + str(key) + " has been converted.")
            daconfig[re.sub(r'_', r' ', key)] = val
        else:
            daconfig[key] = val
    if 'google' in daconfig:
        if not isinstance(daconfig['google'], dict):
            daconfig['google'] = {}
    else:
        daconfig['google'] = {}
    daconfig['google']['use places api new'] = bool(daconfig['google'].get('use places api new', False))
    if (daconfig['google'].get('google maps api key', None) or daconfig['google'].get('google maps api key', None)) and not daconfig['google']['use places api new']:
        config_error("Google has migrated to 'Places API (New)' and the old 'Places API' is now deprecated. Please enable Places API (New) in Google Cloud Console and set 'use places api new: True' within your 'google' configuration. Support for the old 'Places API' will be removed in a future version.")
    if 'analytics id' in daconfig['google']:
        if isinstance(daconfig['google']['analytics id'], str):
            daconfig['google']['analytics id'] = [daconfig['google']['analytics id']]
        if isinstance(daconfig['google']['analytics id'], list):
            new_list = []
            for item in daconfig['google']['analytics id']:
                if isinstance(item, str):
                    new_list.append(item)
            if len(new_list) > 0:
                daconfig['google']['analytics id'] = new_list
            else:
                daconfig['google']['analytics id'] = None
        else:
            daconfig['google']['analytics id'] = None
    if 'grid classes' in daconfig:
        if not isinstance(daconfig['grid classes'], dict):
            config_error("The Configuration directive grid classes must be a dictionary.")
            daconfig['grid classes'] = {}
        has_error = False
        for key, item in daconfig['grid classes'].items():
            if key in ('vertical navigation', 'flush left', 'centered'):
                if isinstance(item, dict):
                    for subkey, subitem in item.items():
                        if not isinstance(subitem, str):
                            config_error("Under the Configuration directive grid classes, " + key + ", " + str(subkey) + " must be a dictionary of string values.")
                            has_error = True
                            break
                else:
                    config_error("Under the Configuration directive grid classes, " + key + " must be a dictionary.")
                    has_error = True
            elif not isinstance(item, str):
                config_error("The Configuration directive grid classes must only refer to strings.")
                has_error = True
                break
        if has_error:
            daconfig['grid classes'] = {}
    else:
        daconfig['grid classes'] = {}
    daconfig['javascript defer'] = bool(daconfig.get('javascript defer', False))
    for key in ('vertical navigation', 'flush left', 'centered'):
        if key not in daconfig['grid classes']:
            daconfig['grid classes'][key] = {}
    if not daconfig['grid classes'].get('user', None):
        daconfig['grid classes']['user'] = 'offset-lg-3 col-lg-6 offset-md-2 col-md-8 offset-sm-1 col-sm-10'
    if not daconfig['grid classes'].get('admin wide', None):
        daconfig['grid classes']['admin wide'] = 'col-sm-10'
    if not daconfig['grid classes'].get('admin', None):
        daconfig['grid classes']['admin'] = 'col-md-7 col-lg-6'
    if not daconfig['grid classes'].get('label width', None):
        daconfig['grid classes']['label width'] = 'md-4'
    daconfig['grid classes']['label grid breakpoint'] = re.sub(r'-.*', '', daconfig['grid classes']['label width'])
    daconfig['grid classes']['label grid number'] = re.sub(r'[^0-9]', '', daconfig['grid classes']['label width'])
    try:
        daconfig['grid classes']['label grid number'] = int(daconfig['grid classes']['label grid number'])
        assert daconfig['grid classes']['label grid number'] >= 1
        assert daconfig['grid classes']['label grid number'] <= 12
    except:
        daconfig['grid classes']['label grid number'] = 4
    if not daconfig['grid classes'].get('field width', None):
        daconfig['grid classes']['field width'] = 'md-8'
    daconfig['grid classes']['field grid breakpoint'] = re.sub(r'-.*', '', daconfig['grid classes']['field width'])
    daconfig['grid classes']['field grid number'] = re.sub(r'[^0-9]', '', daconfig['grid classes']['field width'])
    try:
        daconfig['grid classes']['field grid number'] = int(daconfig['grid classes']['field grid number'])
        assert daconfig['grid classes']['field grid number'] >= 1
        assert daconfig['grid classes']['field grid number'] <= 12
    except:
        daconfig['grid classes']['field grid number'] = 8
    if not daconfig['grid classes'].get('grid breakpoint', None):
        daconfig['grid classes']['grid breakpoint'] = 'md'
    if not daconfig['grid classes'].get('item grid breakpoint', None):
        daconfig['grid classes']['item grid breakpoint'] = 'md'
    if not daconfig['grid classes']['vertical navigation'].get('bar', None):
        daconfig['grid classes']['vertical navigation']['bar'] = 'offset-xl-1 col-xl-2 col-lg-3 col-md-3'
    if not daconfig['grid classes']['vertical navigation'].get('body', None):
        daconfig['grid classes']['vertical navigation']['body'] = 'col-lg-6 col-md-9'
    if not daconfig['grid classes']['vertical navigation'].get('right', None):
        daconfig['grid classes']['vertical navigation']['right'] = 'd-none d-lg-block col-lg-3 col-xl-2'
    if not daconfig['grid classes']['vertical navigation'].get('right small screen', None):
        daconfig['grid classes']['vertical navigation']['right small screen'] = 'd-block d-lg-none'
    if not daconfig['grid classes']['flush left'].get('body', None):
        daconfig['grid classes']['flush left']['body'] = 'offset-xxl-1 col-xxl-5 col-lg-6 col-md-8'
    if not daconfig['grid classes']['flush left'].get('right', None):
        daconfig['grid classes']['flush left']['right'] = 'd-none d-lg-block col-xxl-5 col-lg-6'
    if not daconfig['grid classes']['flush left'].get('right small screen', None):
        daconfig['grid classes']['flush left']['right small screen'] = 'd-block d-lg-none'
    if not daconfig['grid classes']['centered'].get('body', None):
        daconfig['grid classes']['centered']['body'] = 'offset-lg-3 col-lg-6 offset-md-2 col-md-8'
    if not daconfig['grid classes']['centered'].get('right', None):
        daconfig['grid classes']['centered']['right'] = 'd-none d-lg-block col-lg-3'
    if not daconfig['grid classes']['centered'].get('right small screen', None):
        daconfig['grid classes']['centered']['right small screen'] = 'd-block d-lg-none'
    if 'signature pen thickness scaling factor' not in daconfig:
        daconfig['signature pen thickness scaling factor'] = 1.0
    if 'celery modules' in daconfig:
        ok = True
        if isinstance(daconfig['celery modules'], list):
            for item in daconfig['celery modules']:
                if not isinstance(item, str):
                    ok = False
                    break
        else:
            ok = False
        if not ok:
            config_error("celery modules must be a list of strings")
            daconfig['celery modules'] = []
    else:
        daconfig['celery modules'] = []
    if isinstance(daconfig['signature pen thickness scaling factor'], int):
        daconfig['signature pen thickness scaling factor'] = float(daconfig['signature pen thickness scaling factor'])
    if not isinstance(daconfig['signature pen thickness scaling factor'], float):
        config_error("signature pen thickness scaling factor must be a floating point value")
        daconfig['signature pen thickness scaling factor'] = 1.0
    if 'avconv' in daconfig:
        config_error("The Configuration directive avconv has been renamed ffmpeg.")
        daconfig['ffmpeg'] = daconfig['avconv']
        del daconfig['avconv']
    daconfig['config file'] = filename
    if 'modules' not in daconfig:
        daconfig['modules'] = os.getenv('DA_PYTHON', '/usr/share/docassemble/local' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))
    daconfig['python version'] = importlib.metadata.version("docassemble.base")
    version_file = daconfig.get('version file', '/usr/share/docassemble/webapp/VERSION')
    if os.path.isfile(version_file) and os.access(version_file, os.R_OK):
        with open(version_file, 'r', encoding='utf-8') as fp:
            daconfig['system version'] = fp.read().strip()
    else:
        daconfig['system version'] = '0.1.12'
    if version.parse(daconfig['system version']) >= version.parse('1.2.50'):
        daconfig['has_celery_single_queue'] = True
    else:
        daconfig['has_celery_single_queue'] = False
    null_messages = []
    for env_var, key in (('DASUPERVISORUSERNAME', 'username'), ('DASUPERVISORPASSWORD', 'password')):
        value = os.getenv(env_var)
        if value not in (None, ''):
            override_config(daconfig, null_messages, key, env_var, pre_key=['supervisor'])
    if env_true_false('ENVIRONMENT_TAKES_PRECEDENCE'):
        for env_var, key in (('S3ENABLE', 'enable'), ('S3ACCESSKEY', 'access key id'), ('S3SECRETACCESSKEY', 'secret access key'), ('S3BUCKET', 'bucket'), ('S3REGION', 'region'), ('S3ENDPOINTURL', 'endpoint url')):
            if env_exists(env_var):
                override_config(daconfig, null_messages, key, env_var, pre_key=['s3'])
        for env_var, key in (('S3_SSE_ALGORITHM', 'algorithm'), ('S3_SSE_CUSTOMER_ALGORITHM', 'customer algorithm'), ('S3_SSE_CUSTOMER_KEY', 'customer key'), ('S3_SSE_KMS_KEY_ID', 'KMS key ID')):
            if env_exists(env_var):
                override_config(daconfig, null_messages, key, env_var, pre_key=['s3', 'server side encryption'])
        for env_var, key in (('AZUREENABLE', 'enable'), ('AZUREACCOUNTKEY', 'account key'), ('AZUREACCOUNTNAME', 'account name'), ('AZURECONTAINER', 'container'), ('AZURECONNECTIONSTRING', 'connection string')):
            if env_exists(env_var):
                override_config(daconfig, null_messages, key, env_var, pre_key=['azure'])
        if env_exists('KUBERNETES'):
            override_config(daconfig, null_messages, 'kubernetes', 'KUBERNETES')
    s3_config = daconfig.get('s3', None)
    if not s3_config or ('enable' in s3_config and not s3_config['enable']):
        S3_ENABLED = False
    else:
        S3_ENABLED = True
        if not s3_config.get('access key id', None) and env_exists('AWSACCESSKEY'):
            s3_config['access key id'] = os.environ['AWSACCESSKEY']
        if not s3_config.get('secret access key', None) and env_exists('AWSSECRETACCESSKEY'):
            s3_config['secret access key'] = os.environ['AWSSECRETACCESSKEY']
    gc_config = daconfig.get('google cloud', None)
    if not gc_config or ('enable' in gc_config and not gc_config['enable']) or not ('access key id' in gc_config and gc_config['access key id']) or not ('secret access key' in gc_config and gc_config['secret access key']):
        GC_ENABLED = False
    else:
        GC_ENABLED = True
    if 'azure' in daconfig and not isinstance(daconfig['azure'], dict):
        config_error('azure must be a dict')
    azure_config = daconfig.get('azure', None)
    if not isinstance(azure_config, dict) or ('enable' in azure_config and not azure_config['enable']) or 'account name' not in azure_config or azure_config['account name'] is None or 'account key' not in azure_config or azure_config['account key'] is None:
        AZURE_ENABLED = False
    else:
        AZURE_ENABLED = True
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
        cloud = docassemble.base.amazon.s3object(s3_config)
    elif AZURE_ENABLED:
        cloud = docassemble.base.microsoft.azureobject(azure_config)
        if ('key vault name' in azure_config and azure_config['key vault name'] is not None and 'managed identity' in azure_config and azure_config['managed identity'] is not None):
            daconfig = cloud.load_with_secrets(daconfig)
    else:
        cloud = None
    if 'debug startup process' in daconfig and daconfig['debug startup process']:
        DEBUG_BOOT = True
    if 'supervisor' in daconfig:
        if not (isinstance(daconfig['supervisor'], dict) and daconfig['supervisor'].get('username', None) and daconfig['supervisor'].get('password', None)):
            daconfig['supervisor'] = {}
    else:
        daconfig['supervisor'] = {}
    if 'suppress error notificiations' in daconfig and isinstance(daconfig['suppress error notificiations'], list):
        ok = True
        for item in daconfig['suppress error notificiations']:
            if not isinstance(item, str):
                ok = False
                break
        if not ok:
            daconfig['suppress error notificiations'] = []
            config_error("Configuration file suppress error notifications directive not valid")
    else:
        daconfig['suppress error notificiations'] = []
    if 'words' not in daconfig:
        daconfig['words'] = ['docassemble.base:data/sources/us-words.yml']
    if 'concurrency lock timeout' in daconfig:
        if not (isinstance(daconfig['concurrency lock timeout'], int) and daconfig['concurrency lock timeout'] > 0):
            config_error("The value of concurrency lock timeout is invalid.")
            del daconfig['concurrency lock timeout']
    if 'maximum content length' in daconfig:
        if isinstance(daconfig['maximum content length'], (int, type(None))):
            if daconfig['maximum content length'] is not None and daconfig['maximum content length'] <= 0:
                daconfig['maximum content length'] = None
        else:
            config_error("The maximum content length must be an integer number of bytes, or null.")
            del daconfig['maximum content length']
    if 'maximum content length' not in daconfig:
        daconfig['maximum content length'] = 16 * 1024 * 1024
    new_button_colors = {}
    if 'button colors' in daconfig and isinstance(daconfig['button colors'], dict):
        for button_type, color in daconfig['button colors'].items():
            if isinstance(button_type, str) and isinstance(color, str):
                new_button_colors[button_type] = color
    daconfig['button colors'] = new_button_colors
    del new_button_colors
    if 'social' not in daconfig or not isinstance(daconfig['social'], dict):
        daconfig['social'] = {}
    if 'twitter' not in daconfig['social'] or not isinstance(daconfig['social']['twitter'], dict):
        daconfig['social']['twitter'] = {}
    if 'og' not in daconfig['social'] or not isinstance(daconfig['social']['og'], dict):
        daconfig['social']['og'] = {}
    if 'fb' not in daconfig['social'] or not isinstance(daconfig['social']['fb'], dict):
        daconfig['social']['fb'] = {}
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
        if isinstance(daconfig['administrative interviews'], list):
            new_admin_interviews = []
            for item in daconfig['administrative interviews']:
                if isinstance(item, str):
                    new_item = cleanup_filename(item)
                    if new_item:
                        new_admin_interviews.append({'interview': new_item})
                elif isinstance(item, dict):
                    if 'interview' in item and isinstance(item['interview'], str):
                        item['interview'] = cleanup_filename(item['interview'])
                        if item['interview'] is not None:
                            new_admin_interviews.append(item)
                    elif 'url' in item and isinstance(item['url'], str) and 'title' in item:
                        new_item = {'url': item['url']}
                        if isinstance(item['title'], str):
                            new_item['label'] = {'*': item['title']}
                        elif isinstance(item['title'], dict):
                            ok = True
                            for lang, label in item['title'].items():
                                if not (isinstance(lang, str) and isinstance(label, str)):
                                    ok = False
                                    break
                            if not ok:
                                config_error("Invalid title data type in administrative interviews.")
                                continue
                            new_item['label'] = item['title']
                        else:
                            config_error("Invalid title data type in administrative interviews.")
                            continue
                        if 'required privileges' in item:
                            if not isinstance(item['required privileges'], list):
                                config_error("Invalid required privileges data type in administrative interviews.")
                                continue
                            ok = True
                            for role_item in item['required privileges']:
                                if not isinstance(role_item, str):
                                    ok = False
                                    break
                            if not ok:
                                config_error("Invalid data type in administrative interviews.")
                                continue
                            new_item['roles'] = item['required privileges']
                        else:
                            new_item['roles'] = None
                        new_item['require_login'] = bool(item.get('require login', False))
                        new_item['unique_sessions'] = bool(item.get('sessions are unique', False))
                        new_admin_interviews.append(new_item)
                    else:
                        config_error("Unrecognized item in administrative interviews.")
            daconfig['administrative interviews'] = new_admin_interviews
        else:
            del daconfig['administrative interviews']
    if 'single server' in daconfig:
        daconfig['single server'] = bool(daconfig['single server'])
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
    if 'db' not in daconfig:
        daconfig['db'] = {'name': "docassemble", 'user': "docassemble", 'password': "abc123"}
    dbtableprefix = daconfig['db'].get('table prefix', None)
    if not dbtableprefix:
        dbtableprefix = ''
    if cloud is not None and not single_server:
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
    if 'default admin account' in daconfig:
        config_error('For security, delete the default admin account directive, which is no longer needed')
    if 'ocr languages' not in daconfig:
        daconfig['ocr languages'] = {}
    if 'default gitignore' in daconfig and not isinstance(daconfig['default gitignore'], str):
        config_error('default gitignore must be a string')
        del daconfig['default gitignore']
    if not isinstance(daconfig['ocr languages'], dict):
        config_error('ocr languages must be a dict')
        daconfig['ocr languages'] = {}
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
    if 'module whitelist' in daconfig:
        if isinstance(daconfig['module whitelist'], list):
            daconfig['module whitelist'] = [y.strip() for y in daconfig['module whitelist'] if isinstance(y, str)]
        else:
            del daconfig['module whitelist']
    if 'module blacklist' in daconfig:
        if isinstance(daconfig['module blacklist'], list):
            daconfig['module blacklist'] = [y.strip() for y in daconfig['module blacklist'] if isinstance(y, str)]
        else:
            daconfig['module blacklist'] = []
    else:
        daconfig['module blacklist'] = []
    if 'user profile fields' in daconfig:
        if isinstance(daconfig['user profile fields'], list):
            daconfig['user profile fields'] = [y for y in daconfig['user profile fields'] if y in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language')]
        else:
            config_error('user profile fields must be a list')
            daconfig['user profile fields'] = []
    else:
        daconfig['user profile fields'] = []
    if 'permissions' in daconfig:
        if not isinstance(daconfig['permissions'], dict):
            config_error("permissions must be in the form of a dict")
            daconfig['permissions'] = {}
        has_error = False
        for key, val in daconfig['permissions'].items():
            if key in ('admin', 'developer', 'cron', 'user'):
                config_error("permissions cannot be used to change the allowed actions of the " + key + " privilege")
                has_error = True
                break
            if not (isinstance(key, str) and isinstance(val, list)):
                config_error("permissions must be a dictionary where the keys are strings and the values are lists")
                has_error = True
                break
            for item in val:
                if not isinstance(item, str):
                    config_error("permissions must be a dictionary where the values are lists of strings")
                    has_error = True
                    break
            if has_error:
                break
        if has_error:
            daconfig['permissions'] = {}
        for key, val in daconfig['permissions'].items():
            if key not in allowed:
                allowed[key] = set()
            for item in val:
                allowed[key].add(item)
    if 'api privileges' in daconfig:
        if not isinstance(daconfig['api privileges'], list):
            config_error("api privileges must be in the form of a list")
            daconfig['api privileges'] = ['admin', 'developer']
    else:
        daconfig['api privileges'] = ['admin', 'developer']
    authorized_domains = []
    if 'authorized registration domains' in daconfig:
        if isinstance(daconfig['authorized registration domains'], str):
            authorized_domains.append(fix_authorized_domain(daconfig['authorized registration domains']))
        elif isinstance(daconfig['authorized registration domains'], list):
            for domain in daconfig['authorized registration domains']:
                if isinstance(domain, str):
                    authorized_domains.append(fix_authorized_domain(domain))
    daconfig['authorized registration domains'] = authorized_domains
    if 'two factor authentication' in daconfig:
        if isinstance(daconfig['two factor authentication'], bool):
            daconfig['two factor authentication'] = {'enable': daconfig['two factor authentication']}
        if not isinstance(daconfig['two factor authentication'], dict):
            config_error('two factor authentication must be boolean or a dict')
            daconfig['two factor authentication'] = {}
    else:
        daconfig['two factor authentication'] = {'enable': False}
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
    try:
        assert isinstance(daconfig['jinja data'], dict)
    except:
        daconfig['jinja data'] = {}
    if daconfig.get('default icons', None) == 'font awesome':
        daconfig['use font awesome'] = True
    if 'websockets port' in daconfig and daconfig['websockets port']:
        try:
            daconfig['websockets port'] = int(daconfig['websockets port'])
        except:
            config_error("websockets port must be an integer")
            del daconfig['websockets port']
    if 'mail' in daconfig:
        if isinstance(daconfig['mail'], dict):
            if not daconfig['mail'].get('name', None):
                daconfig['mail']['name'] = 'default'
            daconfig['mail'] = [daconfig['mail']]
        elif isinstance(daconfig['mail'], list):
            ok = True
            for item in daconfig['mail']:
                if not isinstance(item, dict):
                    config_error("mail must be a dictionary or a list of dictionaries")
                    ok = False
                    break
            if not ok:
                daconfig['mail'] = []
        else:
            config_error("mail must be a dictionary or a list of dictionaries")
            daconfig['mail'] = []
    else:
        daconfig['mail'] = []
    if 'dispatch' not in daconfig:
        daconfig['dispatch'] = {}
    if not isinstance(daconfig['dispatch'], dict):
        config_error("dispatch must be structured as a dictionary")
        daconfig['dispatch'] = {}
    if len(daconfig['dispatch']):
        new_dispatch = {}
        for shortcut, filename in daconfig['dispatch'].items():
            if isinstance(shortcut, str) and isinstance(filename, str):
                new_filename = cleanup_filename(filename)
                if new_filename:
                    new_dispatch[shortcut] = new_filename
        daconfig['dispatch'] = new_dispatch
    if 'interview delete days by filename' in daconfig and isinstance(daconfig['interview delete days by filename'], dict):
        new_delete_days = {}
        for filename, days in daconfig['interview delete days by filename'].items():
            new_filename = cleanup_filename(filename)
            if new_filename:
                new_delete_days[new_filename] = days
        daconfig['interview delete days by filename'] = new_delete_days
    for key in ('default interview', 'session list interview', 'dispatch interview', 'auto resume interview'):
        if key in daconfig:
            if isinstance(daconfig[key], str):
                daconfig[key] = cleanup_filename(daconfig[key])
                if daconfig[key] is None:
                    del daconfig[key]
            else:
                del daconfig[key]
    if 'ldap login' not in daconfig:
        daconfig['ldap login'] = {}
    if not isinstance(daconfig['ldap login'], dict):
        config_error("ldap login must be structured as a dictionary")
        daconfig['ldap login'] = {}
    if 'initial dict' in daconfig and not isinstance(daconfig['initial dict'], dict):
        config_error("initial dict must be structured as a dictionary")
        del daconfig['initial dict']
    if daconfig.get('auto resume interview', None) is not None:
        daconfig['show interviews link'] = False
    if 'use minio' not in daconfig:
        daconfig['use minio'] = False
    if 'server administrator email' not in daconfig or not daconfig['server administrator email']:
        daconfig['server administrator email'] = 'webmaster@localhost'
    if 'use cloud urls' not in daconfig:
        daconfig['use cloud urls'] = False
    else:
        daconfig['use cloud urls'] = bool(daconfig['use cloud urls'])
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
        messages = []
        for env_var, key in (('DBPREFIX', 'prefix'), ('DBNAME', 'name'), ('DBUSER', 'user'), ('DBPASSWORD', 'password'), ('DBHOST', 'host'), ('DBPORT', 'port'), ('DBTABLEPREFIX', 'table prefix'), ('DBBACKUP', 'backup'), ('DBSSLMODE', 'ssl mode'), ('DBSSLCERT', 'ssl cert'), ('DBSSLKEY', 'ssl key'), ('DBSSLROOTCERT', 'ssl root cert')):
            if env_exists(env_var):
                override_config(daconfig, messages, key, env_var, pre_key=['db'])
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
        if env_exists('DACELERYWORKERS'):
            override_config(daconfig, messages, 'celery processes', 'DACELERYWORKERS')
        if env_exists('DAMAXCELERYWORKERS'):
            override_config(daconfig, messages, 'max celery processes', 'DAMAXCELERYWORKERS')
        if env_exists('PIPINDEXURL'):
            override_config(daconfig, messages, 'pip index url', 'PIPINDEXURL')
        if env_exists('PIPEXTRAINDEXURLS'):
            override_config(daconfig, messages, 'pip extra index urls', 'PIPEXTRAINDEXURLS')
        for env_var, key in (('S3ENABLE', 'enable'), ('S3ACCESSKEY', 'access key id'), ('S3SECRETACCESSKEY', 'secret access key'), ('S3BUCKET', 'bucket'), ('S3REGION', 'region'), ('S3ENDPOINTURL', 'endpoint url')):
            if env_exists(env_var):
                override_config(daconfig, messages, key, env_var, pre_key=['s3'])
        for env_var, key in (('S3_SSE_ALGORITHM', 'algorithm'), ('S3_SSE_CUSTOMER_ALGORITHM', 'customer algorithm'), ('S3_SSE_CUSTOMER_KEY', 'customer key'), ('S3_SSE_KMS_KEY_ID', 'KMS key ID')):
            if env_exists(env_var):
                override_config(daconfig, messages, key, env_var, pre_key=['s3', 'server side encryption'])
        for env_var, key in (('AZUREENABLE', 'enable'), ('AZUREACCOUNTKEY', 'account key'), ('AZUREACCOUNTNAME', 'account name'), ('AZURECONTAINER', 'container'), ('AZURECONNECTIONSTRING', 'connection string')):
            if env_exists(env_var):
                override_config(daconfig, messages, key, env_var, pre_key=['azure'])
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
        if env_exists('PORT'):
            override_config(daconfig, messages, 'http port', 'PORT')
        if env_exists('DAALLOWUPDATES'):
            override_config(daconfig, messages, 'allow updates', 'DAALLOWUPDATES')
        if env_exists('DAALLOWCONFIGURATIONEDITING'):
            override_config(daconfig, messages, 'allow configuration editing', 'DAALLOWCONFIGURATIONEDITING')
        if env_exists('DAENABLEPLAYGROUND'):
            override_config(daconfig, messages, 'enable playground', 'DAENABLEPLAYGROUND')
        if env_exists('DADEBUG'):
            override_config(daconfig, messages, 'debug', 'DADEBUG')
        if env_exists('DAALLOWLOGVIEWING'):
            override_config(daconfig, messages, 'allow log viewing', 'DAALLOWLOGVIEWING')
        if env_exists('DAROOTOWNED'):
            override_config(daconfig, messages, 'root owned', 'DAROOTOWNED')
        if env_exists('DAREADONLYFILESYSTEM'):
            override_config(daconfig, messages, 'read only file system', 'DAREADONLYFILESYSTEM')
        if env_exists('ENABLEUNOCONV'):
            override_config(daconfig, messages, 'enable unoconv', 'ENABLEUNOCONV')
        if env_exists('GOTENBERGURL'):
            override_config(daconfig, messages, 'gotenberg url', 'GOTENBERGURL')
        env_messages = messages
    if DEBUG_BOOT:
        boot_log("config: load complete")


def default_config():
    config = """\
secretkey: """ + random_string(32) + """
mail:
  default sender: '"Administrator" <no-reply@example.com>'
"""
    return config


def parse_redis_uri():
    redis_url = daconfig.get('redis', None)
    if redis_url is None:
        redis_url = 'redis://localhost'
    redis_url = redis_url.strip()
    if not (redis_url.startswith('redis://') or redis_url.startswith('rediss://')):
        redis_url = 'redis://' + redis_url
    m = re.search(r'(rediss?://)([^:@\?]*):([^:@\?]*)@(.*)', redis_url)
    if m:
        redis_username = m.group(2)
        if redis_username == '':
            redis_username = None
        redis_password = m.group(3)
        redis_url = m.group(1) + m.group(4)
    else:
        redis_username = None
        m = re.search(r'rediss?://([^:@\?]*)@(.*)', redis_url)
        if m:
            redis_password = m.group(1)
        else:
            redis_password = None
    m = re.search(r'[?\&]password=([^&]+)', redis_url)
    if m:
        redis_password = m.group(1)
    m = re.search(r'[?\&]db=([0-9]+)', redis_url)
    if m:
        redis_db = int(m.group(1))
    else:
        redis_db = 0

    redis_host = re.sub(r'\?.*', '', redis_url)
    redis_host = re.sub(r'^rediss?://', r'', redis_host)
    redis_host = re.sub(r'^.*@', r'', redis_host)
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
    if redis_url.startswith('rediss://'):
        redis_ssl = True
        directory = daconfig.get('cert install directory', '/etc/ssl/docassemble')
        redis_ca_cert = os.path.join(directory, 'redis_ca.crt')
        redis_cert = os.path.join(directory, 'redis.crt')
        redis_key = os.path.join(directory, 'redis.key')
        if not os.path.isfile(redis_ca_cert):
            redis_ca_cert = None
        if not os.path.isfile(redis_cert):
            redis_cert = None
        if not os.path.isfile(redis_key):
            redis_key = None
    else:
        redis_ssl = False
        redis_ca_cert = None
        redis_cert = None
        redis_key = None
    redis_cli = 'redis-cli'
    if redis_host != 'localhost' or redis_port != '6379':
        redis_cli += ' -h ' + redis_host + ' -p ' + redis_port
    if redis_password is not None:
        redis_cli += ' -a ' + redis_password
    ssl_opts = {}
    if redis_ssl:
        redis_cli += ' --tls'
        ssl_opts['ssl'] = True
        if redis_ca_cert is not None:
            redis_cli += '--cacert ' + json.dumps(redis_ca_cert)
            ssl_opts['ssl_ca_certs'] = redis_ca_cert
        if redis_cert is not None:
            redis_cli += '--cert ' + json.dumps(redis_cert)
            ssl_opts['ssl_certfile'] = redis_cert
        if redis_key is not None:
            redis_cli += ' --key ' + json.dumps(redis_key)
            ssl_opts['ssl_keyfile'] = redis_key
    return (redis_host, redis_port, redis_username, redis_password, redis_offset, redis_cli, ssl_opts)


def noquote(string):
    if isinstance(string, str):
        return string.replace('\n', ' ').replace('"', '&quot;').strip()
    return string


def boot_log(message):
    sys.stderr.write('%.3fs %s\n' % (time.time() - START_TIME, message))
