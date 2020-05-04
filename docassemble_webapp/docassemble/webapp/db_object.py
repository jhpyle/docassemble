db = None
UserMixin = None

def init_flask():
    global db
    global UserMixin
    import docassemble.webapp.database
    if docassemble.webapp.database.pool_pre_ping:
        from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
        class SQLAlchemy(_BaseSQLAlchemy):
            def apply_pool_defaults(self, app, options):
                super().apply_pool_defaults(app, options)
                options["pool_pre_ping"] = True
    else:
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
        db = sqlalchemy.create_engine(url, client_encoding='utf8', pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
    else:
        db = sqlalchemy.create_engine(url, pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
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
