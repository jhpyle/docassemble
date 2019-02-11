from docassemble.webapp.db_object import db, UserMixin
from docassemble.base.config import daconfig, dbtableprefix

class UserModel(db.Model, UserMixin):
    __tablename__ = dbtableprefix + 'user'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(255), nullable=False, unique=True)
    nickname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True, unique=True, index=True)
    confirmed_at = db.Column(db.DateTime())
    active = db.Column('active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(255), nullable=False, server_default='')
    last_name = db.Column(db.String(255), nullable=False, server_default='')
    country = db.Column(db.String(3))
    subdivisionfirst = db.Column(db.String(255))
    subdivisionsecond = db.Column(db.String(255))
    subdivisionthird = db.Column(db.String(255))
    organization = db.Column(db.String(255))
    timezone = db.Column(db.String(64))
    language = db.Column(db.String(64))
    user_auth = db.relationship('UserAuthModel', uselist=False, primaryjoin="UserAuthModel.user_id==UserModel.id")
    roles = db.relationship('Role', secondary=dbtableprefix + 'user_roles', backref=db.backref(dbtableprefix + 'user', lazy='dynamic')) 
    password = db.Column(db.String(255), nullable=False, server_default='') # work around a bug
    otp_secret = db.Column(db.String(255), nullable=True)
    pypi_username = db.Column(db.String(255), nullable=True)
    pypi_password = db.Column(db.String(255), nullable=True)
    modified_at = db.Column(db.DateTime())
    #email_is_phone_number = db.Column(db.Boolean(), nullable=True, server_default='0')

class UserAuthModel(db.Model, UserMixin):
    __tablename__ = dbtableprefix + 'user_auth'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'), index=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    #active = db.Column(db.Boolean(), nullable=False, server_default='0')
    user = db.relationship('UserModel', uselist=False, primaryjoin="UserModel.id==UserAuthModel.user_id")

class Role(db.Model):
    __tablename__ = dbtableprefix + 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True)
    description = db.Column(db.String(255))

class UserRoles(db.Model):
    __tablename__ = dbtableprefix + 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'), index=True)
    role_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'role.id', ondelete='CASCADE'), index=True)

class UserDict(db.Model):
    __tablename__ = dbtableprefix + "userdict"
    indexno = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.Text(), index=True)
    key = db.Column(db.String(250), index=True)
    dictionary = db.Column(db.Text())
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    encrypted = db.Column(db.Boolean(), nullable=False, server_default='1')
    modtime = db.Column(db.DateTime())

db.Index(dbtableprefix + 'ix_userdict_key_filename', UserDict.key, UserDict.filename)
    
class UserDictKeys(db.Model):
    __tablename__ = dbtableprefix + "userdictkeys"
    indexno = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.Text(), index=True)
    key = db.Column(db.String(250), index=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'), index=True)
    temp_user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'tempuser.id', ondelete='CASCADE'), index=True)

db.Index(dbtableprefix + 'ix_userdictkeys_key_filename', UserDict.key, UserDict.filename)

# class UserDictLock(db.Model):
#     __tablename__ = dbtableprefix + "userdictlock"
#     indexno = db.Column(db.Integer(), primary_key=True)
#     filename = db.Column(db.Text())
#     key = db.Column(db.String(250))
#     #locktime = db.Column(db.DateTime(), server_default=db.func.now())

class TempUser(db.Model):
    __tablename__ = dbtableprefix + 'tempuser'
    id = db.Column(db.Integer, primary_key=True)
    
class ChatLog(db.Model):
    __tablename__ = dbtableprefix + "chatlog"
    id = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.Text(), index=True)
    key = db.Column(db.String(250), index=True)
    message = db.Column(db.Text())
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    temp_user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'tempuser.id', ondelete='CASCADE'))
    owner_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    temp_owner_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'tempuser.id', ondelete='CASCADE'))
    open_to_peer = db.Column(db.Boolean(), nullable=False, server_default='0')
    encrypted = db.Column(db.Boolean(), nullable=False, server_default='1')
    modtime = db.Column(db.DateTime())

class MyUserInvitation(db.Model):
    __tablename__ = dbtableprefix + 'user_invite'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'role.id', ondelete='CASCADE'))
    # save the user of the invitee
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey(dbtableprefix + 'user.id'))
    # token used for registration page to identify user registering
    token = db.Column(db.String(100), nullable=False, server_default='')
