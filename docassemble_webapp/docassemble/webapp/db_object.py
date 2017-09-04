db = None
UserMixin = None

def init_flask():
    global db
    global UserMixin
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    import flask_user
    UserMixin = flask_user.UserMixin
    return db

def init_sqlalchemy():
    global db
    global UserMixin
    import sqlalchemy
    import docassemble.webapp.database
    url = docassemble.webapp.database.alchemy_connection_string()
    if url.startswith('postgresql'):
        db = sqlalchemy.create_engine(url, client_encoding='utf8')
    else:
        db = sqlalchemy.create_engine(url)
    #meta = sqlalchemy.MetaData(bind=con, reflect=True)
    from sqlalchemy.orm import sessionmaker, relationship, backref
    Session = sessionmaker(bind=db)
    from sqlalchemy.ext.declarative import declarative_base
    db.Model = declarative_base()
    db.Column = sqlalchemy.Column
    db.Integer = sqlalchemy.Integer
    db.String = sqlalchemy.String
    db.Boolean = sqlalchemy.Boolean
    db.Text = sqlalchemy.Text
    db.DateTime = sqlalchemy.DateTime
    db.func = sqlalchemy.func
    db.relationship = relationship
    db.backref = backref
    db.ForeignKey = sqlalchemy.ForeignKey
    db.session = Session()
    UserMixin = object
    return db
