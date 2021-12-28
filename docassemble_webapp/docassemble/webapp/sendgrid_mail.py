# Adapted from flask_mail
import base64
import sys
import time
from docassemble.base.functions import word
from flask_mail import Message, BadHeaderError, sanitize_addresses, email_dispatched, contextmanager, current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SGMail, Attachment, FileContent, FileName, FileType, Disposition, Email, To, ReplyTo

class Connection:
    def __init__(self, mail):
        self.mail = mail
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, tb):
        pass
    def send(self, message, envelope_from=None):
        assert message.send_to, "No recipients have been added"
        assert message.sender, (
                "The message does not specify a sender and a default sender "
                "has not been configured")
        if message.has_bad_headers():
            raise BadHeaderError
        if message.date is None:
            message.date = time.time()
        if not message.subject:
            message.subject = word("(no subject)")
        sgmessage = SGMail(
            from_email=Email(message.sender),
            to_emails=[To(addressee) for addressee in sanitize_addresses(message.recipients)],
            subject=message.subject,
            plain_text_content=message.body,
            html_content=message.html)
        if message.reply_to:
            sgmessage.reply_to = ReplyTo(message.reply_to)
        if message.cc:
            for recipient in list(sanitize_addresses(message.cc)):
                sgmessage.add_cc(recipient)
        if message.bcc:
            for recipient in list(sanitize_addresses(message.bcc)):
                sgmessage.add_bcc(recipient)
        if message.attachments:
            for flask_attachment in message.attachments:
                attachment = Attachment()
                attachment.file_content = FileContent(base64.b64encode(flask_attachment.data).decode())
                attachment.file_type = FileType(flask_attachment.content_type)
                attachment.file_name = FileName(flask_attachment.filename)
                attachment.disposition = Disposition(flask_attachment.disposition)
                sgmessage.add_attachment(attachment)
        sg = SendGridAPIClient(self.mail.api_key)
        response = sg.send(sgmessage)
        if response.status_code >= 400:
            sys.stderr.write("SendGrid status code: " + str(response.status_code) + "\n")
            sys.stderr.write("SendGrid response headers: " + repr(response.headers) + "\n")
            try:
                sys.stderr.write(repr(response.body) + "\n")
            except:
                pass
            raise Exception("Failed to send e-mail message to SendGrid")
        email_dispatched.send(message, app=current_app._get_current_object())
    def send_message(self, *args, **kwargs):
        self.send(Message(*args, **kwargs))

class _MailMixin:

    @contextmanager
    def record_messages(self):
        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message, app):
            outbox.append(message)

        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)

    def send(self, message):
        with self.connect() as connection:
            message.send(connection)

    def send_message(self, *args, **kwargs):
        self.send(Message(*args, **kwargs))

    def connect(self):
        app = getattr(self, "app", None) or current_app
        try:
            return Connection(app.extensions['mail'])
        except KeyError:
            raise RuntimeError("The curent application was not configured with Flask-Mail")

class _Mail(_MailMixin):
    def __init__(self, api_key,
                 default_sender, debug, suppress,
                 ascii_attachments=False):
        self.api_key = api_key
        self.default_sender = default_sender
        self.debug = debug
        self.suppress = suppress
        self.ascii_attachments = ascii_attachments

class Mail(_MailMixin):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.state = self.init_app(app)
        else:
            self.state = None

    def init_mail(self, config, debug=False, testing=False):
        return _Mail(
            config.get('SENDGRID_API_KEY'),
            config.get('MAIL_DEFAULT_SENDER'),
            int(config.get('MAIL_DEBUG', debug)),
            config.get('MAIL_SUPPRESS_SEND', testing),
            config.get('MAIL_ASCII_ATTACHMENTS', False)
        )

    def init_app(self, app):
        state = self.init_mail(app.config, app.debug, app.testing)
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mail'] = state
        return state

    def __getattr__(self, name):
        return getattr(self.state, name, None)
