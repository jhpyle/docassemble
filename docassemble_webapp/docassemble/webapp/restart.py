import sys
import os
import docassemble.base.config
from docassemble.base.config import daconfig, da_config_file

if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')

def main():
    import docassemble.webapp.cloud
    cloud = docassemble.webapp.cloud.get_cloud()
    if cloud is not None:
        key = cloud.get_key('config.yml')
        if key.exists():
            key.get_contents_to_filename(da_config_file)
            sys.stderr.write("Wrote config file based on copy on cloud\n")
    wsgi_file = WEBAPP_PATH
    if os.path.isfile(wsgi_file):
        with open(wsgi_file, 'a'):
            os.utime(wsgi_file, None)
    sys.exit(0)

if __name__ == "__main__":
    main()
