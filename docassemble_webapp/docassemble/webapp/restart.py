import sys
import os
import docassemble.webapp.config
from docassemble.webapp.config import daconfig
config_file = "/usr/share/docassemble/config.yml"

if os.path.isfile(config_file):
    if not os.access(config_file, os.R_OK):
        sys.stderr.write("Cannot read from " + config_file + "\n")
        sys.exit(1)
    if not os.access(config_file, os.W_OK):
        sys.stderr.write("Cannot write to " + config_file + "\n")
        sys.exit(1)
else:
    sys.stderr.write("Config file " + config_file + " does not exist\n")

docassemble.webapp.config.load(filename=config_file)
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
s3_config = daconfig.get('s3', None)
if not s3_config or ('enable' in s3_config and not s3_config['enable']) or not ('access_key_id' in s3_config and s3_config['access_key_id']) or not ('secret_access_key' in s3_config and s3_config['secret_access_key']):
    S3_ENABLED = False
else:
    S3_ENABLED = True

if S3_ENABLED:
    import docassemble.webapp.amazon
    s3 = docassemble.webapp.amazon.s3object(s3_config)
    key = s3.get_key('config.yml')
    if key.exists():
        key.get_contents_to_filename(config_file)
        sys.stderr.write("Wrote config file based on copy on s3\n")

wsgi_file = WEBAPP_PATH
if os.path.isfile(wsgi_file):
    with open(wsgi_file, 'a'):
        os.utime(wsgi_file, None)
sys.exit(0)
