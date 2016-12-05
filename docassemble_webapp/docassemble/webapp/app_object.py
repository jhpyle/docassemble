#import sys
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from docassemble.base.config import daconfig
    import docassemble.webapp.database
    connect_string = docassemble.webapp.database.connection_string()
    alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
    app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
    app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from docassemble.webapp.db_object import db
    #sys.stderr.write("Setting up app\n")
    db.init_app(app)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app

app = create_app()

# def reset_db():
#     global db
#     if hasattr(db, 'engine'):
#         db.engine.dispose()
#     db = SQLAlchemy(app)
