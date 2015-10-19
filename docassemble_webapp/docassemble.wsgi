import docassemble.webapp.config
docassemble.webapp.config.load(filename="/etc/docassemble/config.yml")
from docassemble.webapp.server import app as application
