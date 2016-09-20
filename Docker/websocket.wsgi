import os, site
import docassemble.base.config
docassemble.base.config.load(filename="/usr/share/docassemble/config/config.yml")
os.environ["PYTHONUSERBASE"] = docassemble.base.config.daconfig.get('packages', "/usr/share/docassemble/local")
os.environ["XDG_CACHE_HOME"] = docassemble.base.config.daconfig.get('packagecache', "/var/www/.cache")
site.addusersitepackages("") 
from docassemble.webapp.socketserver import app as application
