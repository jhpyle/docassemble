# import sys
try:
    from werkzeug.middleware.proxy_fix import ProxyFix
    proxyfix_version = 15
except ImportError:
    from werkzeug.contrib.fixers import ProxyFix
    proxyfix_version = 14
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_cors import CORS
import docassemble.base.functions


def create_app():
    the_app = Flask(__name__)
    the_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from docassemble.base.config import daconfig  # pylint: disable=import-outside-toplevel
    import docassemble.webapp.database  # pylint: disable=import-outside-toplevel,redefined-outer-name
    import docassemble.webapp.db_object  # pylint: disable=import-outside-toplevel,redefined-outer-name
    alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
    the_app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
    if alchemy_connect_string.startswith('postgres'):
        the_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = dict(
            connect_args=docassemble.webapp.database.connect_args()
        )
    the_app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
    the_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    the_db = docassemble.webapp.db_object.init_flask()
    the_db.init_app(the_app)
    the_csrf = CSRFProtect()
    the_csrf.init_app(the_app)
    the_babel = Babel()
    the_babel.init_app(the_app)
    if daconfig.get('behind https load balancer', False):
        if proxyfix_version >= 15:
            the_app.wsgi_app = ProxyFix(the_app.wsgi_app, x_proto=1, x_host=1)
        else:
            the_app.wsgi_app = ProxyFix(the_app.wsgi_app)
    if 'cross site domains' in daconfig:
        CORS(the_app, origins=daconfig['cross site domains'], supports_credentials=True)
    return the_app, the_csrf, the_babel

if docassemble.base.functions.server_context.context == 'websockets':
    from docassemble.webapp.app_socket import app  # pylint: disable=unused-import
else:
    app, csrf, flaskbabel = create_app()
