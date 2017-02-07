#import sys
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel

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
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app, csrf, babel

app, csrf, flaskbabel = create_app()
