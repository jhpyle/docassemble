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
    the_app = Flask(__name__)
    the_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from docassemble.base.config import daconfig
    import docassemble.webapp.database
    alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
    #the_app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
    the_app.secret_key = daconfig.get('secretkey', '38ihfiFehfoU34mcq_4clirglw3g4o87')
    #the_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #the_db = SQLAlchemy(the_app)
    if alchemy_connect_string.startswith('postgresql'):
        connect_args = docassemble.webapp.database.connect_args()
        the_db = sqlalchemy.create_engine(alchemy_connect_string, connect_args=connect_args, pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
    else:
        the_db = sqlalchemy.create_engine(alchemy_connect_string, pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
    Base = declarative_base()
    Base.metadata.bind = the_db
    #the_app.wsgi_app = ProxyFix(the_app.wsgi_app)
    the_db.Model = Base
    the_db.Column = sqlalchemy.Column
    the_db.Integer = sqlalchemy.Integer
    the_db.String = sqlalchemy.String
    the_db.Index = sqlalchemy.Index
    the_db.Boolean = sqlalchemy.Boolean
    the_db.Text = sqlalchemy.Text
    the_db.DateTime = sqlalchemy.DateTime
    the_db.func = sqlalchemy.func
    the_db.relationship = relationship
    the_db.backref = backref
    the_db.ForeignKey = sqlalchemy.ForeignKey
    docassemble.webapp.db_object.db = the_db
    #import flask_login
    docassemble.webapp.db_object.UserMixin = object
    if 'cross site domains' in daconfig and isinstance(daconfig['cross site domains'], list) and len(daconfig['cross site domains']) > 0:
        origins = daconfig['cross site domains']
    else:
        origins = [daconfig.get('url root', '*')]
    the_socketio = SocketIO(the_app, async_mode='eventlet', verify=False, logger=True, engineio_logger=True, cors_allowed_origins=origins)
    return the_app, the_db, the_socketio

app, db, socketio = create_app()
