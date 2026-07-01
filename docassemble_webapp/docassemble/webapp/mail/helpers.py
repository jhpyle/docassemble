import copy
from docassemble.webapp.config import daconfig

mail_configs = {}

def get_mail_config(app):
    the_mail_configs = {}
    default_config = None
    for mail_config in daconfig['mail']:
        if mail_config.get('name', None) == 'default':
            default_config = mail_config
    if default_config is None and len(daconfig['mail']) > 0:
        default_config = daconfig['mail'][0]
    if default_config is None:
        default_config = {'username': None, 'password': None, 'default sender': None, 'server': 'localhost', 'port': 25, 'use ssl': False, 'use tls': True}
    app.config['MAIL_USERNAME'] = default_config.get('username', None)
    app.config['MAIL_PASSWORD'] = default_config.get('password', None)
    app.config['MAIL_DEFAULT_SENDER'] = default_config.get('default sender', None)
    app.config['MAIL_SERVER'] = default_config.get('server', 'localhost')
    app.config['MAIL_PORT'] = default_config.get('port', 25)
    app.config['MAIL_USE_SSL'] = default_config.get('use ssl', False)
    app.config['MAIL_USE_TLS'] = default_config.get('use tls', True)
    count = 0
    for mail_config in daconfig['mail']:
        the_config = copy.deepcopy(mail_config)
        if the_config.get('mailgun api key', None):
            try:
                the_config['mailgun api url'] = mail_config.get('mailgun api url', 'https://api.mailgun.net/v3/%s/messages.mime') % mail_config.get('mailgun domain', 'NOT_USING_MAILGUN')
            except:
                the_config['mailgun api url'] = f"https://api.mailgun.net/v3/{mail_config.get('mailgun domain', 'NOT_USING_MAILGUN')}/messages.mime"
        if not the_config.get('name', None):
            the_config['name'] = 'config' + str(count)
        the_mail_configs[the_config['name']] = the_config
        if 'default' not in the_mail_configs and mail_config is default_config:
            the_mail_configs['default'] = the_config
        count += 1
    if 'default' not in the_mail_configs:
        the_mail_configs['default'] = default_config
    for config_name, mail_config in the_mail_configs.items():
        if mail_config.get('mailgun domain', None) and mail_config.get('mailgun api key', None):
            from .mailgun_mail import Mail as MailgunMail  # pylint: disable=import-outside-toplevel
            mail_class = MailgunMail
            config = {
                'MAILGUN_API_URL': mail_config['mailgun api url'],
                'MAILGUN_API_KEY': mail_config['mailgun api key'],
                'MAIL_DEFAULT_SENDER': mail_config.get('default sender', None),
                'MAIL_DEBUG': app.config.get('MAIL_DEBUG', False),
                'MAIL_MAX_EMAILS': app.config.get('MAIL_MAX_EMAILS'),
                'MAIL_SUPPRESS_SEND': app.config.get('MAIL_SUPPRESS_SEND', False),
                'MAIL_ASCII_ATTACHMENTS': app.config.get('MAIL_ASCII_ATTACHMENTS', False)
            }
        elif 'sendgrid api key' in mail_config and mail_config['sendgrid api key']:
            from .sendgrid_mail import Mail as SendgridMail  # pylint: disable=import-outside-toplevel
            mail_class = SendgridMail
            config = {
                'SENDGRID_API_KEY': mail_config['sendgrid api key'],
                'MAIL_DEFAULT_SENDER': mail_config.get('default sender', None),
                'MAIL_DEBUG': app.config.get('MAIL_DEBUG', False),
                'MAIL_MAX_EMAILS': app.config.get('MAIL_MAX_EMAILS'),
                'MAIL_SUPPRESS_SEND': app.config.get('MAIL_SUPPRESS_SEND', False),
                'MAIL_ASCII_ATTACHMENTS': app.config.get('MAIL_ASCII_ATTACHMENTS', False)
            }
        elif 'azure client id' in mail_config and mail_config['azure client id']:
            from .azure_mail import Mail as AzureMail  # pylint: disable=import-outside-toplevel
            mail_class = AzureMail
            config = {
                'AZURE_CLIENT_ID': mail_config['azure client id'],
                'AZURE_CLIENT_SECRET': mail_config.get('azure client secret', None),
                'AZURE_TENANT_ID': mail_config.get('azure tenant id', None),
                'MAIL_DEFAULT_SENDER': mail_config.get('default sender', None),
                'MAIL_DEBUG': app.config.get('MAIL_DEBUG', False),
                'MAIL_MAX_EMAILS': app.config.get('MAIL_MAX_EMAILS'),
                'MAIL_SUPPRESS_SEND': app.config.get('MAIL_SUPPRESS_SEND', False),
                'MAIL_ASCII_ATTACHMENTS': app.config.get('MAIL_ASCII_ATTACHMENTS', False)
            }
        else:
            from .da_flask_mail import FlaskMail  # pylint: disable=import-outside-toplevel
            mail_class = FlaskMail
            config = {
                'MAIL_SERVER': mail_config.get('server', 'localhost'),
                'MAIL_USERNAME': mail_config.get('username', None),
                'MAIL_PASSWORD': mail_config.get('password', None),
                'MAIL_PORT': mail_config.get('port', 25),
                'MAIL_USE_TLS': mail_config.get('use tls', True),
                'MAIL_USE_SSL': mail_config.get('use ssl', False),
                'MAIL_DEFAULT_SENDER': mail_config.get('default sender', None),
                'MAIL_DEBUG': app.config.get('MAIL_DEBUG', False),
                'MAIL_MAX_EMAILS': app.config.get('MAIL_MAX_EMAILS'),
                'MAIL_SUPPRESS_SEND': app.config.get('MAIL_SUPPRESS_SEND', False),
                'MAIL_ASCII_ATTACHMENTS': app.config.get('MAIL_ASCII_ATTACHMENTS', False)
            }
        if config_name == 'default':
            mail_config['mail'] = mail_class(app=app, config=config)
        else:
            mail_config['mail'] = mail_class(config=config)
    return the_mail_configs


def compute_mail_config(app):
    mail_configs.clear()
    mail_configs.update(get_mail_config(app))
