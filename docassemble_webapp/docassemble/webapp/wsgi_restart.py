import os
import sys
import docassemble.base.config
if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.base.config import daconfig
from docassemble.base.logger import logmessage


def main():
    webapp_path = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
    wsgi_file = webapp_path
    if os.path.isfile(wsgi_file):
        with open(wsgi_file, 'a', encoding='utf-8'):
            os.utime(wsgi_file, None)
            logmessage("Restarted WSGI.\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
