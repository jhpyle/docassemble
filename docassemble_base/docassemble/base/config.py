import yaml
import os
import sys
import httplib2
import socket
#import string
#import random
from docassemble.base.generate_key import random_string

dbtableprefix = None
daconfig = dict()
s3_config = dict()
S3_ENABLED = False
gc_config = dict()
GC_ENABLED = False
hostname = None
loaded = False
in_celery = False

def load(**kwargs):
    global daconfig
    global s3_config
    global S3_ENABLED
    global gc_config
    global GC_ENABLED
    global dbtableprefix
    global hostname
    global loaded
    global in_celery
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
        daconfig = yaml.load(stream)
    if daconfig is None:
        sys.stderr.write("Could not open configuration file from " + str(filename) + "\n")
        with open(filename, 'r') as fp:
            sys.stderr.write(fp.read() + "\n")
        sys.exit(1)
    daconfig['config_file'] = filename
    s3_config = daconfig.get('s3', None)
    if not s3_config or ('enable' in s3_config and not s3_config['enable']): # or not ('access_key_id' in s3_config and s3_config['access_key_id']) or not ('secret_access_key' in s3_config and s3_config['secret_access_key']):
        S3_ENABLED = False
    else:
        S3_ENABLED = True
    gc_config = daconfig.get('google_cloud', None)
    if not gc_config or ('enable' in gc_config and not gc_config['enable']) or not ('access_key_id' in gc_config and gc_config['access_key_id']) or not ('secret_access_key' in gc_config and gc_config['secret_access_key']):
        GC_ENABLED = False
    else:
        GC_ENABLED = True
    if 'db' not in daconfig:
        daconfig['db'] = dict(name="docassemble", user="docassemble", password="abc123")
    dbtableprefix = daconfig['db'].get('table_prefix', None)
    if not dbtableprefix:
        dbtableprefix = ''
    if daconfig.get('ec2', False):
        h = httplib2.Http()
        resp, content = h.request(daconfig.get('ec2_ip_url', "http://169.254.169.254/latest/meta-data/local-hostname"), "GET")
        if resp['status'] and int(resp['status']) == 200:
            hostname = content
        else:
            sys.stderr.write("Could not get hostname from ec2\n")
            sys.exit(1)
    else:
        hostname = os.getenv('SERVERHOSTNAME', socket.gethostname())
    if S3_ENABLED:
        import docassemble.webapp.amazon
        s3 = docassemble.webapp.amazon.s3object(s3_config)
        if 'host' not in daconfig['db'] or daconfig['db']['host'] is None:
            key = s3.get_key('hostname-sql')
            if key.exists():
                the_host = key.get_contents_as_string()
                if the_host == hostname:
                    daconfig['db']['host'] = 'localhost'
                else:
                    daconfig['db']['host'] = the_host
        if 'log server' not in daconfig or daconfig['log server'] is None:
            key = s3.get_key('hostname-log')
            if key.exists():
                the_host = key.get_contents_as_string()
                if the_host == hostname:
                    daconfig['log server'] = 'localhost'
                else:
                    daconfig['log server'] = the_host
        if 'redis' not in daconfig or daconfig['redis'] is None:
            key = s3.get_key('hostname-redis')
            if key.exists():
                the_host = key.get_contents_as_string()
                if the_host == hostname:
                    the_host = 'localhost'
                daconfig['redis'] = 'redis://' + the_host
        if 'rabbitmq' not in daconfig or daconfig['rabbitmq'] is None:
            key = s3.get_key('hostname-rabbitmq')
            if key.exists():
                the_host = key.get_contents_as_string()
                daconfig['rabbitmq'] = 'pyamqp://guest@' + str(the_host) + '//'
    if daconfig['db'].get('host', None) is None or daconfig['db'].get('host', '') == '':
        daconfig['db']['host'] = 'localhost'
    if daconfig['db'].get('name', None) is None or daconfig['db'].get('name', '') == '':
        daconfig['db']['name'] = 'docassemble'
    if daconfig['db'].get('user', None) is None or daconfig['db'].get('user', '') == '':
        daconfig['db']['user'] = 'docassemble'
    if daconfig['db'].get('password', None) is None or daconfig['db'].get('password', '') == '':
        daconfig['db']['password'] = 'abc123'
    if daconfig['db'].get('port', None) is None or daconfig['db'].get('port', '') == '':
        daconfig['db']['port'] = '5432'
    if 'ocr languages' not in daconfig or type(daconfig['ocr languages']) is not dict:
        daconfig['ocr languages'] = dict()
    if 'en' not in daconfig['ocr languages']:
        daconfig['ocr languages']['en'] = 'eng'
    if 'es' not in daconfig['ocr languages']:
        daconfig['ocr languages']['es'] = 'spa'
    loaded = True
    return

def default_config():
    config = """\
secretkey: """ + random_string(32) + """
mail:
  default_sender: '"Administrator" <no-reply@example.com>'
"""
    return config
