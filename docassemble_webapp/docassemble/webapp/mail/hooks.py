from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.hooks.impl import hookimpl
from .da_flask_mail import Message
from .helpers import mail_configs

@hookimpl(specname="send_mail")
def da_send_mail(the_message, config):
    if config is None:
        config = 'default'
    if config not in mail_configs:
        logmessage("invalid mail configuration " + config)
        config = 'default'
    mail_configs[config]['mail'].send(the_message)

@hookimpl
def get_mail_class():
    return Message
