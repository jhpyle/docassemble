from flask_user import UserMixin
from docassemble.webapp.app_and_db import db
from docassemble.webapp.config import daconfig, dbtableprefix

class User(UserMixin, db.Model):
    __tablename__ = dbtableprefix + 'user'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True, unique=True)
    confirmed_at = db.Column(db.DateTime())
    active = db.Column('active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(50), nullable=False, server_default='')
    last_name = db.Column(db.String(50), nullable=False, server_default='')
    country = db.Column(db.String(2))
    subdivisionfirst = db.Column(db.String(2))
    subdivisionsecond = db.Column(db.String(50))
    subdivisionthird = db.Column(db.String(50))
    organization = db.Column(db.String(64))
    user_auth = db.relationship('UserAuth', uselist=False, primaryjoin="UserAuth.user_id==User.id")
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('user', lazy='dynamic'))

class UserAuth(db.Model, UserMixin):
    __tablename__ = dbtableprefix + 'user_auth'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    #active = db.Column(db.Boolean(), nullable=False, server_default='0')
    user = db.relationship('User', uselist=False, primaryjoin="User.id==UserAuth.user_id")

class Role(db.Model):
    __tablename__ = dbtableprefix + 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))

class UserRoles(db.Model):
    __tablename__ = dbtableprefix + 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'role.id', ondelete='CASCADE'))

class UserDict(db.Model):
    __tablename__ = dbtableprefix + "userdict"
    indexno = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.Text())
    key = db.Column(db.String(250))
    dictionary = db.Column(db.Text())
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))

class UserDictKeys(db.Model):
    __tablename__ = dbtableprefix + "userdictkeys"
    indexno = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.Text())
    key = db.Column(db.String(250))
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))

class UserDictLock(db.Model):
    __tablename__ = dbtableprefix + "userdictlock"
    indexno = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.Text())
    key = db.Column(db.String(250))
    locktime = db.Column(db.DateTime(), server_default=db.func.now())
