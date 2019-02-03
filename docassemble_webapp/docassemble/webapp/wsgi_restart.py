import sys
import os
import docassemble.base.config
from io import open

if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)

def main():
    from docassemble.base.config import daconfig
    webapp_path = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
    wsgi_file = webapp_path
    if os.path.isfile(wsgi_file):
        with open(wsgi_file, 'a'):
            os.utime(wsgi_file, None)
            sys.stderr.write("Restarted WSGI.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
