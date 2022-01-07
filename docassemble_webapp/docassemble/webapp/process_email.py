import datetime
import email
import json
import mimetypes
import re
import sys
from email.utils import parseaddr, parsedate, getaddresses
from time import mktime
from sqlalchemy import select
import docassemble.base.config
docassemble.base.config.load()
import docassemble.webapp.worker
import docassemble.webapp.db_object
from docassemble.webapp.core.models import Shortener, Email, EmailAttachment
from docassemble.webapp.file_number import get_new_file_number
from docassemble.webapp.files import SavedFile
from docassemble.webapp.users.models import UserModel

db = docassemble.webapp.db_object.init_sqlalchemy()

def main():
    fp = open("/tmp/mail.log", "a", encoding="utf-8")
    #fp.write("The file is " + sys.argv[1] + "\n")
    try:
        with open(sys.argv[1], 'r', encoding="utf-8") as email_fp:
            msg = email.message_from_file(email_fp)
    except Exception as errMess:
        fp.write("Failed to read e-mail message: " + str(errMess) + "\n")
        sys.exit("Failed to read e-mail message")
    raw_date = msg.get('Date', msg.get('Resent-Date', None))
    addr_return_path = msg.get('Return-path', None)
    addr_reply_to = msg.get('Reply-to', None)
    addr_to = msg.get('Envelope-to', None)
    addr_from = msg.get('From', msg.get('Sender', None))
    subject = msg.get('Subject', None)
    fp.write("Message to " + str(addr_to) + "\n")
    #fp.write("From was " + str(addr_from) + "\n")
    #fp.write("Subject was " + str(subject) + "\n")
    to_recipients = []
    for recipient in getaddresses(msg.get_all('to', []) + msg.get_all('resent-to', [])):
        to_recipients.append(dict(name=recipient[0], address=recipient[1]))
    cc_recipients = []
    for recipient in getaddresses(msg.get_all('cc', []) + msg.get_all('resent-cc', [])):
        cc_recipients.append(dict(name=recipient[0], address=recipient[1]))
    recipients = []
    for recipient in getaddresses(msg.get_all('to', []) + msg.get_all('cc', []) + msg.get_all('resent-to', []) + msg.get_all('resent-cc', [])):
        recipients.append(dict(name=recipient[0], address=recipient[1]))
    if addr_to is None and len(recipients) > 0:
        addr_to = recipients[0]['address']
    #fp.write("recipients are " + str(recipients) + "\n")
    if addr_to is not None:
        #fp.write("parsed envelope-to: " + str(parseaddr(addr_to)) + "\n")
        short_code = re.sub(r'@.*', '', parseaddr(addr_to)[1])
    else:
        short_code = None
    #fp.write("short code is " + str(short_code) + "\n")
    record = db.session.execute(select(Shortener).filter_by(short=short_code)).scalar()
    if record is None:
        fp.write("short code not found\n")
        sys.exit("short code not found")
        #fp.write("short code found\n")
    #file_number = get_new_file_number(record.uid, 'email', yaml_file_name=record.filename)
    ##fp.write("file number is " + str(file_number) + "\n")
    #saved_file_email = SavedFile(file_number, fix=True)
    if addr_from is not None:
        #fp.write("parsed from: " + str(parseaddr(addr_from)[1]) + "\n")
        addr_from = dict(name=parseaddr(addr_from)[0], address=parseaddr(addr_from)[1])
    else:
        addr_from = dict(empty=True)
    if addr_return_path is not None:
        #fp.write("parsed return_path: " + str(parseaddr(addr_return_path)[1]) + "\n")
        addr_return_path = dict(name=parseaddr(addr_return_path)[0], address=parseaddr(addr_return_path)[1])
    else:
        addr_return_path = dict(empty=True)
    #fp.write("return_path is " + str(addr_return_path) + "\n")
    if addr_reply_to is not None:
        #fp.write("parsed reply-to: " + str(parseaddr(addr_reply_to)[1]) + "\n")
        addr_reply_to = dict(name=parseaddr(addr_reply_to)[0], address=parseaddr(addr_reply_to)[1])
        #fp.write("reply-to is " + str(addr_reply_to) + "\n")
    else:
        addr_reply_to = dict(empty=True)
    #fp.write("reply-to is " + str(addr_reply_to) + "\n")
    msg_current_time = datetime.datetime.now()
    if raw_date is not None:
        msg_date = datetime.datetime.fromtimestamp(mktime(parsedate(raw_date)))
        #fp.write("msg_date is " + str(msg_date) + "\n")
    else:
        msg_date = msg_current_time
        #fp.write("msg_date set to current time\n")
    headers = []
    for item in msg.items():
        headers.append([item[0], item[1]])
    #fp.write("headers:\n" + json.dumps(headers) + "\n")

    email_record = Email(short=short_code, to_addr=json.dumps(to_recipients), cc_addr=json.dumps(cc_recipients), from_addr=json.dumps(addr_from), reply_to_addr=json.dumps(addr_reply_to), return_path_addr=json.dumps(addr_return_path), subject=subject, datetime_message=msg_date, datetime_received=msg_current_time)
    db.session.add(email_record)
    db.session.commit()

    save_attachment(record.uid, record.filename, 'headers.json', email_record.id, 0, 'application/json', 'json', json.dumps(headers))

    counter = 1
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        filename = part.get_filename()
        if part.get_content_type() == 'text/plain':
            ext = '.txt'
        else:
            ext = mimetypes.guess_extension(part.get_content_type())
        if not ext:
            ext = '.bin'
        if filename:
            filename = '%03d-%s' % (counter, secure_filename(filename))
        else:
            filename = '%03d-attachment%s' % (counter, ext)
        #fp.write("Filename is " + str(filename) + "\n")
        #fp.write("Content type is " + str(part.get_content_type()) + "\n")

        real_filename = re.sub(r'[0-9][0-9][0-9]-', r'', filename)
        real_ext = re.sub(r'^\.', r'', ext)
        save_attachment(record.uid, record.filename, real_filename, email_record.id, counter, part.get_content_type(), real_ext, part.get_payload(decode=True))
        counter += 1
    fp.close()
    user = None
    if record.user_id is not None:
        user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=record.user_id)).scalar()
    if user is None:
        user_info = dict(email=None, the_user_id='t' + str(record.temp_user_id), theid=record.temp_user_id, roles=[])
    else:
        role_list = [role.name for role in user.roles]
        if len(role_list) == 0:
            role_list = ['user']
        user_info = dict(email=user.email, roles=role_list, the_user_id=user.id, theid=user.id, firstname=user.first_name, lastname=user.last_name, nickname=user.nickname, country=user.country, subdivisionfirst=user.subdivisionfirst, subdivisionsecond=user.subdivisionsecond, subdivisionthird=user.subdivisionthird, organization=user.organization)
    docassemble.webapp.worker.background_action.delay(record.filename, user_info, record.uid, None, None, None, dict(action='incoming_email', arguments=dict(id=email_record.id)), extra=None)

def save_attachment(uid, yaml_filename, filename, email_id, index, content_type, extension, content):
    att_file_number = get_new_file_number(uid, filename, yaml_file_name=yaml_filename)
    attachment_record = EmailAttachment(email_id=email_id, index=index, content_type=content_type, extension=extension, upload=att_file_number)
    db.session.add(attachment_record)
    db.session.commit()
    saved_file_attachment = SavedFile(att_file_number, extension=extension, fix=True, should_not_exist=True)
    saved_file_attachment.write_content(content)
    saved_file_attachment.finalize()

def secure_filename(filename):
    filename = re.sub(r'[^A-Za-z0-9\_\-\. ]+', r'_', filename)
    return filename.strip('_')

main()
