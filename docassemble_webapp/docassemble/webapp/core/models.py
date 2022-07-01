from docassemble.webapp.db_object import db
from docassemble.base.config import dbtableprefix
from docassemble.webapp.database import dbprefix
from sqlalchemy import true, false
from sqlalchemy.dialects.postgresql.json import JSONB
import docassemble.webapp.users.models

class Uploads(db.Model):
    __tablename__ = dbtableprefix + "uploads"
    indexno = db.Column(db.Integer(), primary_key=True, unique=True)
    key = db.Column(db.String(250), index=True)
    filename = db.Column(db.String(255), index=True)
    yamlfile = db.Column(db.String(255), index=True)
    private = db.Column(db.Boolean(), nullable=False, server_default=true())
    persistent = db.Column(db.Boolean(), nullable=False, server_default=false())

class UploadsUserAuth(db.Model):
    __tablename__ = dbtableprefix + "uploadsuserauth"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    uploads_indexno = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'uploads.indexno', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'), index=True)
    temp_user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'tempuser.id', ondelete='CASCADE'), index=True)

class UploadsRoleAuth(db.Model):
    __tablename__ = dbtableprefix + "uploadsroleauth"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    uploads_indexno = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'uploads.indexno', ondelete='CASCADE'), nullable=False, index=True)
    role_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'role.id', ondelete='CASCADE'), nullable=False, index=True)

class ObjectStorage(db.Model):
    __tablename__ = dbtableprefix + "objectstorage"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    key = db.Column(db.String(1024), index=True)
    value = db.Column(db.Text())

class SpeakList(db.Model):
    __tablename__ = dbtableprefix + "speaklist"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    filename = db.Column(db.String(255), index=True)
    key = db.Column(db.String(250), index=True)
    phrase = db.Column(db.Text())
    question = db.Column(db.Integer())
    type = db.Column(db.String(20))
    language = db.Column(db.String(10))
    dialect = db.Column(db.String(10))
    upload = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'uploads.indexno', ondelete='CASCADE'))
    encrypted = db.Column(db.Boolean(), nullable=False, server_default=true())
    digest = db.Column(db.Text())

class Supervisors(db.Model):
    __tablename__ = dbtableprefix + "supervisors"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    hostname = db.Column(db.Text())
    url = db.Column(db.Text())
    start_time = db.Column(db.DateTime(), server_default=db.func.now())
    role = db.Column(db.Text())

class MachineLearning(db.Model):
    __tablename__ = dbtableprefix + "machinelearning"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    group_id = db.Column(db.String(1024))
    key = db.Column(db.String(1024), index=True)
    independent = db.Column(db.Text())
    dependent = db.Column(db.Text())
    info = db.Column(db.Text())
    create_time = db.Column(db.DateTime())
    modtime = db.Column(db.DateTime())
    active = db.Column(db.Boolean(), nullable=False, server_default=false())

class Shortener(db.Model):
    __tablename__ = dbtableprefix + "shortener"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    short = db.Column(db.String(250), nullable=False, unique=True)
    filename = db.Column(db.String(255), index=True)
    uid = db.Column(db.String(250))
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    temp_user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'tempuser.id', ondelete='CASCADE'))
    key = db.Column(db.String(255), index=True)
    index = db.Column(db.Integer())
    modtime = db.Column(db.DateTime(), server_default=db.func.now())

class Email(db.Model):
    __tablename__ = dbtableprefix + "email"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    short = db.Column(db.String(250), db.ForeignKey(dbtableprefix + 'shortener.short', ondelete='CASCADE'))
    all_addr = db.Column(db.Text())
    to_addr = db.Column(db.Text())
    cc_addr = db.Column(db.Text())
    from_addr = db.Column(db.Text())
    reply_to_addr = db.Column(db.Text())
    return_path_addr = db.Column(db.Text())
    subject = db.Column(db.Text())
    datetime_message = db.Column(db.DateTime())
    datetime_received = db.Column(db.DateTime())

class EmailAttachment(db.Model):
    __tablename__ = dbtableprefix + "emailattachment"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    email_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'email.id', ondelete='CASCADE'))
    index = db.Column(db.Integer())
    content_type = db.Column(db.Text())
    extension = db.Column(db.Text())
    upload = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'uploads.indexno', ondelete='CASCADE'))
    
# class DbInfo(db.Model):
#     __tablename__ = dbtableprefix + "dbinfo"
#     key = db.Column(db.Text(), primary_key=True)
#     value = db.Column(db.Text())

class GlobalObjectStorage(db.Model):
    __tablename__ = dbtableprefix + "globalobjectstorage"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    key = db.Column(db.String(1024), index=True)
    value = db.Column(db.Text())
    encrypted = db.Column(db.Boolean(), nullable=False, server_default=true())
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    temp_user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'tempuser.id', ondelete='CASCADE'))

class JsonStorage(db.Model):
    __tablename__ = dbtableprefix + "jsonstorage"
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    filename = db.Column(db.String(255), index=True)
    key = db.Column(db.String(250), index=True)
    if dbprefix.startswith('postgresql'):
        data = db.Column(JSONB)
    else:
        data = db.Column(db.Text())
    tags = db.Column(db.Text())
    modtime = db.Column(db.DateTime(), server_default=db.func.now())
    persistent = db.Column(db.Boolean(), nullable=False, server_default=false())
