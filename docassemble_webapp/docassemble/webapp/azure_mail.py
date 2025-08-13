# Adapted from flask_mail
import base64
# import sys
import time
from docassemble.base.functions import word
from docassemble.base.logger import logmessage
from docassemble.base.error import DAException
from docassemble.webapp.da_flask_mail import Message
from flask_mail import BadHeaderError, email_dispatched, contextmanager
import msal
import requests
import re

scopes = ["https://graph.microsoft.com/.default"]


def extract_raw_email(email):
    m = re.search(r"<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>", email)
    if m:
        return m.group(1)
    return email


class Connection:

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def send(self, message, envelope_from=None):  # pylint: disable=unused-argument
        assert message.send_to, "No recipients have been added"
        if message.sender is None:
            message.sender = self.mail.default_sender
        assert message.sender, (
                "The message does not specify a sender and a default sender "
                "has not been configured")
        if message.has_bad_headers():
            raise BadHeaderError
        if message.date is None:
            message.date = time.time()
        if not message.subject:
            message.subject = word("(no subject)")
        authority = f"https://login.microsoftonline.com/{self.mail.tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id=self.mail.client_id,
            client_credential=self.mail.client_secret,
            authority=authority
        )
        result = app.acquire_token_for_client(scopes=scopes)
        if "access_token" not in result:
            raise DAException("Error acquiring token: " + result.get("error_description"))
        access_token = result["access_token"]

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "text/plain"
        }

        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{extract_raw_email(message.sender)}/sendMail",
            headers=headers,
            data=base64.b64encode(message.as_string().encode()).decode(),
            timeout=60
        )

        if response.status_code == 202:
            print("Email sent successfully!")
        else:
            logmessage("Azure status code: " + str(response.status_code))
            logmessage("Azure response headers: " + repr(response.headers))
            logmessage(repr(response.text))
            raise DAException("Failed to send e-mail message to Azure")

    def send_message(self, *args, **kwargs):
        self.send(Message(*args, **kwargs))


class _MailMixin:

    @contextmanager
    def record_messages(self):
        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message, app):  # pylint: disable=unused-argument
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


class _Mail(_MailMixin):

    def __init__(self, client_id, client_secret, tenant_id,
                 default_sender, debug, suppress,
                 ascii_attachments=False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.default_sender = default_sender
        self.debug = debug
        self.suppress = suppress
        self.ascii_attachments = ascii_attachments


class Mail(_MailMixin):

    def __init__(self, app=None, config=None):
        self.app = app
        if app is not None or config is not None:
            self.state = self.init_app(app=app, config=config)
        else:
            self.state = None

    def init_mail(self, config, debug=False, testing=False):
        return _Mail(
            config.get('AZURE_CLIENT_ID'),
            config.get('AZURE_CLIENT_SECRET'),
            config.get('AZURE_TENANT_ID'),
            config.get('MAIL_DEFAULT_SENDER'),
            int(config.get('MAIL_DEBUG', debug)),
            config.get('MAIL_SUPPRESS_SEND', testing),
            config.get('MAIL_ASCII_ATTACHMENTS', False)
        )

    def init_app(self, app=None, config=None):
        if app is not None:
            if config is None:
                config = app.config
            state = self.init_mail(config, app.debug, app.testing)
            app.extensions = getattr(app, 'extensions', {})
            app.extensions['mail'] = self
        else:
            state = self.init_mail(config, False, False)
        return state

    def __getattr__(self, name):
        return getattr(self.state, name, None)

    def connect(self):
        try:
            return Connection(self.state)
        except KeyError:
            raise RuntimeError("The curent application was not configured with Flask-Mail")
