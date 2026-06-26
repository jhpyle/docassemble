# pylint: disable=global-statement
# import sqlalchemy
# from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
# from sqlalchemy.orm import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship, backref
# import docassemble_flask_user

def init_app(app, other_databases=False):
    import docassemble.webapp.database
    from docassemble.webapp.config import daconfig
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()
    app.config['SQLALCHEMY_DATABASE_URI'] = alchemy_connect_string
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
      "pool_pre_ping": docassemble.webapp.database.pool_pre_ping,
    }
    if alchemy_connect_string.startswith('postgres'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS']['connect_args'] = docassemble.webapp.database.connect_args()
    if other_databases and daconfig.get('variables snapshot db') is not None:
        import docassemble.webapp.user_database
        snapshot_url = docassemble.webapp.user_database.alchemy_url('variables snapshot db')
        snapshot_bind = {'url': snapshot_url, 'pool_pre_ping': daconfig.get('sql ping', False)}
        snapshot_connect_args = docassemble.webapp.user_database.connect_args('variables snapshot db')
        if snapshot_connect_args:
            snapshot_bind['connect_args'] = snapshot_connect_args
        app.config['SQLALCHEMY_BINDS'] = {'variables_snapshot': snapshot_bind}

# Am I getting rid of this?

# db = None
# UserMixin = None  # pylint: disable=invalid-name

# def init_flask():
#     global db
#     global UserMixin
#     import docassemble.webapp.database
#     if docassemble.webapp.database.pool_pre_ping:
#         class SQLAlchemy(_BaseSQLAlchemy):
#             def apply_pool_defaults(self, app, options):
#                 super().apply_pool_defaults(app, options)
#                 options["pool_pre_ping"] = True
#                 options["future"] = True
#                 return options
#     else:
#         class SQLAlchemy(_BaseSQLAlchemy):
#             def apply_pool_defaults(self, app, options):
#                 super().apply_pool_defaults(app, options)
#                 options["future"] = True
#                 return options
#     db = SQLAlchemy()
#     UserMixin = docassemble_flask_user.UserMixin
#     return db

# # Am I getting rid of this?

# def init_sqlalchemy():
#     global db
#     global UserMixin
#     import docassemble.webapp.database
#     url = docassemble.webapp.database.alchemy_connection_string()
#     if url.startswith('postgresql'):
#         connect_args = docassemble.webapp.database.connect_args()
#         db = sqlalchemy.create_engine(url, client_encoding='utf8', connect_args=connect_args, pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
#     else:
#         db = sqlalchemy.create_engine(url, pool_pre_ping=docassemble.webapp.database.pool_pre_ping)
#     # meta = sqlalchemy.MetaData(bind=con, reflect=True)
#     Session = sessionmaker(bind=db)
#     db.Model = declarative_base()
#     db.Column = sqlalchemy.Column
#     db.Integer = sqlalchemy.Integer
#     db.String = sqlalchemy.String
#     db.Boolean = sqlalchemy.Boolean
#     db.Text = sqlalchemy.Text
#     db.DateTime = sqlalchemy.DateTime
#     db.func = sqlalchemy.func
#     db.relationship = relationship
#     db.backref = backref
#     db.ForeignKey = sqlalchemy.ForeignKey
#     db.session = Session()
#     UserMixin = object
#     return db
