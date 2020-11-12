#import sys
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

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from docassemble.base.config import daconfig
    import docassemble.webapp.database
    import docassemble.webapp.db_object
    connect_string = docassemble.webapp.database.connection_string()
    alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
    app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
    app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = docassemble.webapp.db_object.init_flask()
    db.init_app(app)
    csrf = CSRFProtect()
    csrf.init_app(app)
    babel = Babel()
    babel.init_app(app)
    if daconfig.get('behind https load balancer', False):
        if proxyfix_version >= 15:
            app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
        else:
            app.wsgi_app = ProxyFix(app.wsgi_app)
    if 'cross site domains' in daconfig:
        CORS(app, origins=daconfig['cross site domains'], supports_credentials=True)
    return app, csrf, babel

import docassemble.base.functions
if docassemble.base.functions.server_context.context == 'websockets':
    from docassemble.webapp.app_socket import app
else:
    app, csrf, flaskbabel = create_app()
