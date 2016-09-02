import yaml
import os
import sys
import httplib2
import socket

dbtableprefix = None
daconfig = dict()
s3_config = dict()
S3_ENABLED = False
gc_config = dict()
GC_ENABLED = False
hostname = None
loaded = False

def load(**kwargs):
    global daconfig
    global s3_config
    global S3_ENABLED
    global gc_config
    global GC_ENABLED
    global dbtableprefix
    global hostname
    global loaded
    if 'arguments' in kwargs and kwargs['arguments'] and len(kwargs['arguments']) > 1:
        filename = kwargs['arguments'][1]
    else:
        filename = kwargs.get('filename', os.getenv('DA_CONFIG_FILE', '/usr/share/docassemble/config/config.yml'))
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
    else:
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
    dbtableprefix = daconfig['db'].get('table_prefix', None)
    if not dbtableprefix:
        dbtableprefix = ''
    hostname = socket.gethostname()
    if daconfig.get('ec2', False):
        h = httplib2.Http()
        resp, content = h.request(daconfig.get('ec2_ip_url', "http://169.254.169.254/latest/meta-data/local-ipv4"), "GET")
        if resp['status'] and int(resp['status']) == 200:
            hostname = content
        else:
            sys.stderr.write("Could not get hostname from ec2\n")
            sys.exit(1)
    # else:
    #     sys.stderr.write("ec2 was set to " + str(daconfig.get('ec2', False)))
    loaded = True
    return

def default_config():
    config = """\
debug: true
root: /
exitpage: /
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: localhost
  port: null
secretkey: 28asflwjeifwlfjsd2fejfiefw3g4o87
password_secretkey: 2f928j3rwjf82498rje9t
appname: docassemble
brandname: demo
packagecache: /var/www/.cache
uploads: /usr/share/docassemble/files
packages: /usr/share/docassemble/local
webapp: /usr/share/docassemble/webapp/docassemble.wsgi
mail:
  default_sender: '"Administrator" <no-reply@example.com>'
admin_address: '"Administrator" <admin@example.com>'
use_progress_bar: false
default_interview: docassemble.demo:data/questions/questions.yml
flask_log: /tmp/flask.log
language: en
locale: en_US.utf8
default_admin_account:
  nickname: admin
  email: admin@admin.com
  password: password
"""
    return config
