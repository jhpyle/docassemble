import os #, site
import docassemble.base.config
docassemble.base.config.load(filename=os.environ.get('DOCASSEMBLE_CONFIG', '/usr/share/docassemble/config/config.yml'))
#os.environ["PYTHONUSERBASE"] = docassemble.base.config.daconfig.get('packages', "/usr/share/docassemble/local")
os.environ["XDG_CACHE_HOME"] = docassemble.base.config.daconfig.get('packagecache', "/tmp/docassemble-cache")
#site.addusersitepackages("") 
from docassemble.webapp.server import app as application
