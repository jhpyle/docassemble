import sys
import os
import docassemble.webapp.config
from docassemble.webapp.config import daconfig, s3_config, S3_ENABLED
if __name__ == "__main__":
    docassemble.webapp.config.load(arguments=sys.argv)
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')

def main():
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

if __name__ == "__main__":
    main()
