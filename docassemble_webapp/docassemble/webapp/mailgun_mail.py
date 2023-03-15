# Adapted from flask_mail
# import sys
import time
import requests
from requests.auth import HTTPBasicAuth
from docassemble.base.error import DAException
from docassemble.base.logger import logmessage
from docassemble.webapp.da_flask_mail import Message
from flask_mail import BadHeaderError, sanitize_addresses, email_dispatched, contextmanager, current_app


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
        data = {'to': ', '.join(list(sanitize_addresses(message.send_to)))}
        if hasattr(message, 'mailgun_variables') and isinstance(message.mailgun_variables, dict):
            for key, val in message.mailgun_variables.items():
                data['v:' + str(key)] = val
        response = requests.post(self.mail.api_url,
                                 auth=HTTPBasicAuth('api', self.mail.api_key),
                                 data=data,
                                 files={'message': ('mime_message', message.as_string())}, timeout=120)
        if response.status_code >= 400:
            logmessage("Mailgun status code: " + str(response.status_code))
            logmessage("Mailgun response headers: " + repr(response.headers))
            try:
                logmessage(repr(response.body))
            except:
                pass
            raise DAException("Failed to send e-mail message to " + self.mail.api_url)
        email_dispatched.send(message, app=current_app._get_current_object())

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

    def __init__(self, api_url, api_key,
                 default_sender, debug, suppress,
                 ascii_attachments=False):
        self.api_url = api_url
        self.api_key = api_key
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
            config.get('MAILGUN_API_URL'),
            config.get('MAILGUN_API_KEY'),
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
