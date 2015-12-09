from docassemble.webapp.app_and_db import db
from docassemble.webapp.config import daconfig, dbtableprefix

class Attachments(db.Model):
    __tablename__ = dbtableprefix + "attachments"
    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(250))
    dictionary = db.Column(db.Text())
    question = db.Column(db.Integer())
    filename = db.Column(db.Text())

class Uploads(db.Model):
    __tablename__ = dbtableprefix + "uploads"
    indexno = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(250))
    filename = db.Column(db.Text())

class KVStore(db.Model):
    __tablename__ = dbtableprefix + "kvstore"
    key = db.Column(db.String(250), primary_key=True)
    value = db.Column(db.LargeBinary(), nullable=False)

class Ticket(db.Model):
    __tablename__ = dbtableprefix + 'ticket'
    id = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.String(255))
    request_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text())
    opened_by = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    open_time = db.Column(db.DateTime(), server_default=db.func.now())
    close_time = db.Column(db.DateTime())
    closed_by = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    close_type = db.Column(db.String(50))
    close_description = db.Column(db.Text())
    status = db.Column(db.String(50))

class TicketNote(db.Model):
    __tablename__ = dbtableprefix + "ticketnote"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    note_type = db.Column(db.String(50), nullable=False)
    ticket_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'ticket.id', ondelete='CASCADE'))
    create_time = db.Column(db.DateTime(), server_default=db.func.now())
    description = db.Column(db.Text())

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

class Messages(db.Model):
    __tablename__ = dbtableprefix + "messages"
    id = db.Column(db.Integer(), db.Sequence(dbtableprefix + 'messages_id_seq'), primary_key=True)
    message = db.Column(db.Text())
    create_time = db.Column(db.DateTime(), server_default=db.func.now())

class Supervisors(db.Model):
    __tablename__ = dbtableprefix + "supervisors"
    id = db.Column(db.Integer(), primary_key=True)
    hostname = db.Column(db.Text())
    url = db.Column(db.Text())
    start_time = db.Column(db.DateTime(), server_default=db.func.now())
