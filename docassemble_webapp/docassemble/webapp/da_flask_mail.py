from flask_mail import Mail, Connection as FlaskConnection, Message as FlaskMessage


class Connection(FlaskConnection):
    def send(self, message, envelope_from=None):  # pylint: disable=unused-argument
        if message.sender is None:
            message.sender = self.mail.default_sender
        super().send(message, envelope_from=envelope_from)


class FlaskMail(Mail):

    def __init__(self, app=None, config=None):
        self.app = app
        if app is not None or config is not None:
            self.state = self.init_app(app=app, config=config)
        else:
            self.state = None

    def init_app(self, app=None, config=None):
        if app is not None:
            if config is None:
                config = app.config
            state = self.init_mail(config, app.debug, app.testing)
            app.extensions = getattr(app, 'extensions', {})
            app.extensions['mail'] = state
        else:
            state = self.init_mail(config, False, False)
        return state

    def connect(self):
        try:
            return Connection(self.state)
        except KeyError:
            raise RuntimeError("The curent application was not configured with Flask-Mail")


class Message(FlaskMessage):

    def __init__(self, subject='',
                 recipients=None,
                 body=None,
                 html=None,
                 alts={},
                 sender=None,
                 cc=None,
                 bcc=None,
                 attachments=None,
                 reply_to=None,
                 date=None,
                 charset=None,
                 extra_headers=None,
                 mail_options=None,
                 rcpt_options=None):
        null_sender = sender is None
        super().__init__(subject, recipients, body, html, alts, sender, cc, bcc, attachments, reply_to, date, charset, extra_headers, mail_options, rcpt_options)
        if null_sender:
            self.sender = None
