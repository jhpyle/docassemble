import json
from flask import session
from flask_login import current_user
from sqlalchemy import select, delete
from docassemble.base.error import DAError
from docassemble.base.functions import get_uid
from docassemble.base.generate_key import random_lower_string
from docassemble.base.thread_context import this_thread
from docassemble.base.util import (
    DAEmailRecipient,
    DAFile,
    DAEmail,
    DAEmailRecipientList,
    DAFileList,
)
from docassemble.webapp.extensions import db
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.main.models import Uploads
from docassemble.webapp.users.helpers import get_user_object
from docassemble.webapp.users.models import UserModel
from docassemble.webapp.utils.filenames import get_ext_and_mimetype
from docassemble.webapp.utils.helpers import process_file
from .models import Email, Shortener, EmailAttachment

@hookimpl
def get_short_code(kwargs):
    key = kwargs.get('key', None)
    the_index = kwargs.get('index', None)
    if key is None and the_index is not None:
        raise DAError("get_short_code: if you provide an index you must provide a key")
    yaml_filename = kwargs.get('i', this_thread.current_info.get('yaml_filename', None))
    uid = kwargs.get('uid', get_uid())
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']
        temp_user_id = None
    elif 'temp_user_id' in kwargs:
        user_id = None
        temp_user_id = kwargs['temp_user_id']
    elif current_user.is_anonymous:
        user_id = None
        temp_user_id = session.get('tempuser', None)
    else:
        user_id = current_user.id
        temp_user_id = None
    short_code = None
    for record in db.session.execute(select(Shortener.short).filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key, index=the_index)):
        short_code = record.short
    if short_code is not None:
        return short_code
    counter = 0
    new_record = None
    while counter < 20:
        existing_id = None
        new_short = random_lower_string(6)
        for record in db.session.execute(select(Shortener.id).filter_by(short=new_short)):
            existing_id = record.id
        if existing_id is None:
            new_record = Shortener(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, short=new_short, key=key, index=the_index)
            db.session.add(new_record)
            db.session.commit()
            break
        counter += 1
    if new_record is None:
        raise SystemError("Failed to generate unique short code")
    return new_short


@hookimpl
def retrieve_email(email_id):
    if not isinstance(email_id, int):
        raise DAError("email_id not provided")
    email = db.session.execute(select(Email).filter_by(id=email_id)).scalar()
    if email is None:
        raise DAError("E-mail did not exist")
    short_record = db.session.execute(select(Shortener).filter_by(short=email.short)).scalar()
    if short_record is not None and short_record.user_id is not None:
        user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=short_record.user_id, active=True)).scalar()
    else:
        user = None
    if short_record is None:
        raise DAError("Short code did not exist")
    return get_email_obj(email, short_record, user)


class AddressEmail:

    def __str__(self):
        return str(self.address)


@hookimpl
def retrieve_emails(kwargs):
    key = kwargs.get('key', None)
    the_index = kwargs.get('index', None)
    if key is None and the_index is not None:
        raise DAError("retrieve_emails: if you provide an index you must provide a key")
    yaml_filename = kwargs.get('i', this_thread.current_info.get('yaml_filename', None))
    uid = kwargs.get('uid', get_uid())
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']
        temp_user_id = None
    elif 'temp_user_id' in kwargs:
        user_id = None
        temp_user_id = kwargs['temp_user_id']
    elif current_user.is_anonymous:
        user_id = None
        temp_user_id = session.get('tempuser', None)
    else:
        user_id = current_user.id
        temp_user_id = None
    user_cache = {}
    results = []
    if key is None:
        the_query = db.session.execute(select(Shortener).filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id).order_by(Shortener.modtime)).scalars()
    else:
        if the_index is None:
            the_query = db.session.execute(select(Shortener).filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key).order_by(Shortener.modtime)).scalars()
        else:
            the_query = db.session.execute(select(Shortener).filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key, index=the_index).order_by(Shortener.modtime)).scalars()
    for record in the_query:
        result_for_short = AddressEmail()
        result_for_short.address = record.short
        result_for_short.key = record.key
        result_for_short.index = record.index
        result_for_short.emails = []
        if record.user_id is not None:
            if record.user_id in user_cache:
                user = user_cache[record.user_id]
            else:
                user = get_user_object(record.user_id)
                user_cache[record.user_id] = user
            result_for_short.owner = user.email
        else:
            user = None
            result_for_short.owner = None
        for email in db.session.execute(select(Email).filter_by(short=record.short).order_by(Email.datetime_received)).scalars():
            result_for_short.emails.append(get_email_obj(email, record, user))
        results.append(result_for_short)
    return results


def get_email_obj(email, short_record, user):
    email_obj = DAEmail(short=email.short)
    email_obj.key = short_record.key
    email_obj.index = short_record.index
    email_obj.initializeAttribute('to_address', DAEmailRecipientList, json.loads(email.to_addr), gathered=True)
    email_obj.initializeAttribute('cc_address', DAEmailRecipientList, json.loads(email.cc_addr), gathered=True)
    email_obj.initializeAttribute('from_address', DAEmailRecipient, **json.loads(email.from_addr))
    email_obj.initializeAttribute('reply_to', DAEmailRecipient, **json.loads(email.reply_to_addr))
    email_obj.initializeAttribute('return_path', DAEmailRecipient, **json.loads(email.return_path_addr))
    email_obj.subject = email.subject
    email_obj.datetime_message = email.datetime_message
    email_obj.datetime_received = email.datetime_received
    email_obj.initializeAttribute('attachment', DAFileList, gathered=True)
    if user is None:
        email_obj.address_owner = None
    else:
        email_obj.address_owner = user.email
    for attachment_record in db.session.execute(select(EmailAttachment).filter_by(email_id=email.id).order_by(EmailAttachment.index)).scalars():
        # logmessage("Attachment record is " + str(attachment_record.id))
        upload = db.session.execute(select(Uploads).filter_by(indexno=attachment_record.upload)).scalar()
        if upload is None:
            continue
        # logmessage("Filename is " + upload.filename)
        saved_file_att = SavedFile(attachment_record.upload, extension=attachment_record.extension, fix=True)
        process_file(saved_file_att, saved_file_att.path, attachment_record.content_type, attachment_record.extension, initial=False)
        extension, mimetype = get_ext_and_mimetype(upload.filename)
        if upload.filename == 'headers.json':
            # logmessage("Processing headers")
            email_obj.initializeAttribute('headers', DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
        elif upload.filename == 'attachment.txt' and attachment_record.index < 3:
            # logmessage("Processing body text")
            email_obj.initializeAttribute('body_text', DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
        elif upload.filename == 'attachment.html' and attachment_record.index < 3:
            email_obj.initializeAttribute('body_html', DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
        else:
            email_obj.attachment.appendObject(DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
    if not hasattr(email_obj, 'headers'):
        email_obj.headers = None
    if not hasattr(email_obj, 'body_text'):
        email_obj.body_text = None
    if not hasattr(email_obj, 'body_html'):
        email_obj.body_html = None
    return email_obj

@hookimpl
def manage_email_server_objects(mode, kwargs):
    if mode == 0:
        temp_user_id = kwargs['temp_user_id']
        files_to_delete = []
        for short_code_item in db.session.execute(select(Shortener).filter_by(temp_user_id=temp_user_id)).scalars():
            for email in db.session.execute(select(Email).filter_by(short=short_code_item.short)).scalars():
                for attachment in db.session.execute(select(EmailAttachment).filter_by(email_id=email.id)).scalars():
                    files_to_delete.append(attachment.upload)
        for file_number in files_to_delete:
            the_file = SavedFile(file_number)
            the_file.delete()
        db.session.execute(delete(Shortener).where(Shortener.temp_user_id == temp_user_id))
        db.session.commit()
    if mode == 1:
        user_id = kwargs['user_id']
        files_to_delete = []
        for short_code_item in db.session.execute(select(Shortener).filter_by(user_id=user_id)).scalars():
            for email in db.session.execute(select(Email).filter_by(short=short_code_item.short)).scalars():
                for attachment in db.session.execute(select(EmailAttachment).filter_by(email_id=email.id)).scalars():
                    files_to_delete.append(attachment.upload)
        for file_number in files_to_delete:
            the_file = SavedFile(file_number)
            the_file.delete()
        db.session.execute(delete(Shortener).where(Shortener.user_id == user_id))
        db.session.commit()
    if mode == 2:
        user_code = kwargs['user_code']
        filename = kwargs['user_code']
        files_to_delete = []
        for short_code_item in db.session.execute(select(Shortener).filter_by(uid=user_code, filename=filename)).scalars():
            for email in db.session.execute(select(Email).filter_by(short=short_code_item.short)).scalars():
                for attachment in db.session.execute(select(EmailAttachment).filter_by(email_id=email.id)).scalars():
                    files_to_delete.append(attachment.upload)
        for file_number in files_to_delete:
            the_file = SavedFile(file_number)
            the_file.delete()
        db.session.execute(delete(Shortener).filter_by(uid=user_code, filename=filename))
        db.session.commit()
