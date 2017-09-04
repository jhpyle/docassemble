from docassemble.webapp.db_object import db
from docassemble.base.config import daconfig, dbtableprefix
from sqlalchemy import true, false

class Attachments(db.Model):
    __tablename__ = dbtableprefix + "attachments"
    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(250))
    dictionary = db.Column(db.Text())
    question = db.Column(db.Integer())
    filename = db.Column(db.Text())
    encrypted = db.Column(db.Boolean(), nullable=False, server_default=true())

class Uploads(db.Model):
    __tablename__ = dbtableprefix + "uploads"
    indexno = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(250))
    filename = db.Column(db.Text())
    yamlfile = db.Column(db.Text())
    private = db.Column(db.Boolean(), nullable=False, server_default=true())
    persistent = db.Column(db.Boolean(), nullable=False, server_default=false())

class ObjectStorage(db.Model):
    __tablename__ = dbtableprefix + "objectstorage"
    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.Text())
    value = db.Column(db.Text())

class SpeakList(db.Model):
    __tablename__ = dbtableprefix + "speaklist"
    id = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.Text())
    key = db.Column(db.String(250))
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
    id = db.Column(db.Integer(), primary_key=True)
    hostname = db.Column(db.Text())
    url = db.Column(db.Text())
    start_time = db.Column(db.DateTime(), server_default=db.func.now())
    role = db.Column(db.Text())

class MachineLearning(db.Model):
    __tablename__ = dbtableprefix + "machinelearning"
    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.Text())
    key = db.Column(db.Text())
    independent = db.Column(db.Text())
    dependent = db.Column(db.Text())
    info = db.Column(db.Text())
    create_time = db.Column(db.DateTime())
    modtime = db.Column(db.DateTime())
    active = db.Column(db.Boolean(), nullable=False, server_default=false())

class Shortener(db.Model):
    __tablename__ = dbtableprefix + "shortener"
    id = db.Column(db.Integer(), primary_key=True)
    short = db.Column(db.String(250), nullable=False, unique=True)
    filename = db.Column(db.Text())
    uid = db.Column(db.String(250))
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    temp_user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'tempuser.id', ondelete='CASCADE'))
    key = db.Column(db.Text())
    index = db.Column(db.Integer())
    modtime = db.Column(db.DateTime(), server_default=db.func.now())

class Email(db.Model):
    __tablename__ = dbtableprefix + "email"
    id = db.Column(db.Integer(), primary_key=True)
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
    id = db.Column(db.Integer(), primary_key=True)
    email_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'email.id', ondelete='CASCADE'))
    index = db.Column(db.Integer())
    content_type = db.Column(db.Text())
    extension = db.Column(db.Text())
    upload = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'uploads.indexno', ondelete='CASCADE'))
    
# class DbInfo(db.Model):
#     __tablename__ = dbtableprefix + "dbinfo"
#     key = db.Column(db.Text(), primary_key=True)
#     value = db.Column(db.Text())
