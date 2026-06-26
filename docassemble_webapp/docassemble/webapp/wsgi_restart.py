import os
import sys
from docassemble.webapp.config import daconfig


def main():
    webapp_path = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
    wsgi_file = webapp_path
    if os.path.isfile(wsgi_file):
        with open(wsgi_file, 'a', encoding='utf-8'):
            os.utime(wsgi_file, None)
            sys.stdout.write("Restarted WSGI.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
