#import sys
#from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import docassemble.webapp.db_object
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from docassemble.base.config import daconfig
    import docassemble.webapp.database
    connect_string = docassemble.webapp.database.connection_string()
    alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
    #app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
    app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #db = SQLAlchemy(app)
    if alchemy_connect_string.startswith('postgresql'):
        connect_args = docassemble.webapp.database.connect_args()
        db = sqlalchemy.create_engine(alchemy_connect_string, connect_args=connect_args, pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
    else:
        db = sqlalchemy.create_engine(alchemy_connect_string, pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
    Base = declarative_base()
    Base.metadata.bind = db
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    db.Model = Base
    db.Column = sqlalchemy.Column
    db.Integer = sqlalchemy.Integer
    db.String = sqlalchemy.String
    db.Index = sqlalchemy.Index
    db.Boolean = sqlalchemy.Boolean
    db.Text = sqlalchemy.Text
    db.DateTime = sqlalchemy.DateTime
    db.func = sqlalchemy.func
    db.relationship = relationship
    db.backref = backref
    db.ForeignKey = sqlalchemy.ForeignKey
    docassemble.webapp.db_object.db = db
    #import flask_login
    docassemble.webapp.db_object.UserMixin = object
    if 'cross site domains' in daconfig and isinstance(daconfig['cross site domains'], list) and len(daconfig['cross site domains']) > 0:
        origins = daconfig['cross site domains']
    else:
        origins = [daconfig.get('url root', '*')]
    socketio = SocketIO(app, async_mode='eventlet', verify=False, logger=True, engineio_logger=True, cors_allowed_origins=origins)
    return app, db, socketio

app, db, socketio = create_app()
