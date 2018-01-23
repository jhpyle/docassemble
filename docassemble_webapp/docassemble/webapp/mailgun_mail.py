# Adapted from flask_mail
import time
import requests
from requests.auth import HTTPBasicAuth
from flask_mail import Message, BadHeaderError, sanitize_addresses, email_dispatched, contextmanager, current_app

class Connection(object):
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
        response = requests.post(self.mail.api_url,
                                 auth=HTTPBasicAuth('api', self.mail.api_key),
                                 data={'to': ', '.join(list(sanitize_addresses(message.send_to)))},
                                 files={'message': ('mime_message', message.as_string())})
        if response.status_code >= 400:
            raise Exception("Failed to send e-mail message to " + self.mail.api_url)
        email_dispatched.send(message, app=current_app._get_current_object())
    def send_message(self, *args, **kwargs):
        self.send(Message(*args, **kwargs))

class _MailMixin(object):

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
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.state = self.init_app(app)
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

    def init_app(self, app):
        state = self.init_mail(app.config, app.debug, app.testing)
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mail'] = state
        return state

    def __getattr__(self, name):
        return getattr(self.state, name, None)

"""POST https://api.mailgun.net/v3/<domain>/messages.mime

>>> import requests
>>> from pprint import pprint
>>> url = 'http://httpbin.org/post'
>>> files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}
>>> response = requests.post(url, data={
...   'description' :'Some desc',
...   'release_notes_url':'Someurl.pdf'
...   }, files=files)

>>> url = 'http://httpbin.org/post'
>>> files = {'message': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}

>>> r = requests.post(url, files=files)
>>> r.text

multipart/form-data
to 	Email address of the recipient(s). Example: "Bob <bob@host.com>". You can use commas to separate multiple recipients. Make sure to include all To, Cc and Bcc recipients of the message.
message 	MIME string of the message. Make sure to use multipart/form-data to send this as a file upload.
o:tag 	Tag string. See Tagging for more information.
o:deliverytime 	Desired time of delivery. See Date Format. Note: Messages can be scheduled for a maximum of 3 days in the future.
o:dkim 	Enables/disabled DKIM signatures on per-message basis. Pass yes or no
o:testmode 	Enables sending in test mode. Pass yes if needed. See Sending in Test Mode
o:tracking 	Toggles tracking on a per-message basis, see Tracking Messages for details. Pass yes or no.
o:tracking-clicks 	Toggles clicks tracking on a per-message basis. Has higher priority than domain-level setting. Pass yes, no or htmlonly.
o:tracking-opens 	Toggles opens tracking on a per-message basis. Has higher priority than domain-level setting. Pass yes or no.
h:X-My-Header 	h: prefix followed by an arbitrary value allows to append a custom MIME header to the message (X-My-Header in this case). For example, h:Reply-To to specify Reply-To address.
v:my-var 	v: prefix followed by an arbitrary name allows to attach a custom JSON data to the message. See Attaching Data to Messages for more information.
"""
