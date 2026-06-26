import json
from docassemble.base.error import DAException
from docassemble.webapp.app_object import flaskapp as app
from docassemble.webapp.config import daconfig, DEFAULT_COUNTRY
from docassemble.webapp.daredis import r
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.twilio.helpers import twilio_config
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage

fax_provider = daconfig.get('fax provider', None) or 'clicksend'

clicksend_config = {}
telnyx_config = {}


def get_clicksend_config():
    if 'clicksend' in daconfig and isinstance(daconfig['clicksend'], (list, dict)):
        the_clicksend_config = {'name': {}, 'number': {}}
        if isinstance(daconfig['clicksend'], dict):
            config_list = [daconfig['clicksend']]
        else:
            config_list = daconfig['clicksend']
        for the_config in config_list:
            if isinstance(the_config, dict) and 'api username' in the_config and 'api key' in the_config and 'number' in the_config:
                if 'country' not in the_config:
                    the_config['country'] = DEFAULT_COUNTRY or 'US'
                if 'from email' not in the_config:
                    the_config['from email'] = app.config['MAIL_DEFAULT_SENDER']
                the_clicksend_config['number'][str(the_config['number'])] = the_config
                if 'default' not in the_clicksend_config['name']:
                    the_clicksend_config['name']['default'] = the_config
                if 'name' in the_config:
                    the_clicksend_config['name'][the_config['name']] = the_config
            else:
                logmessage("improper setup in clicksend configuration")
        if 'default' not in the_clicksend_config['name']:
            the_clicksend_config = None
    else:
        the_clicksend_config = None
    # if fax_provider == 'clicksend' and the_clicksend_config is None:
    #    logmessage("improper clicksend configuration; faxing will not be functional")
    return the_clicksend_config

def get_telnyx_config():
    if 'telnyx' in daconfig and isinstance(daconfig['telnyx'], (list, dict)):
        the_telnyx_config = {'name': {}, 'number': {}}
        if isinstance(daconfig['telnyx'], dict):
            config_list = [daconfig['telnyx']]
        else:
            config_list = daconfig['telnyx']
        for the_config in config_list:
            if isinstance(the_config, dict) and 'app id' in the_config and 'api key' in the_config and 'number' in the_config:
                if 'country' not in the_config:
                    the_config['country'] = DEFAULT_COUNTRY or 'US'
                if 'from email' not in the_config:
                    the_config['from email'] = app.config['MAIL_DEFAULT_SENDER']
                the_telnyx_config['number'][str(the_config['number'])] = the_config
                if 'default' not in the_telnyx_config['name']:
                    the_telnyx_config['name']['default'] = the_config
                if 'name' in the_config:
                    the_telnyx_config['name'][the_config['name']] = the_config
            else:
                logmessage("improper setup in twilio configuration")
        if 'default' not in the_telnyx_config['name']:
            the_telnyx_config = None
    else:
        the_telnyx_config = None
    if fax_provider == 'telnyx' and the_telnyx_config is None:
        logmessage("improper telnyx configuration; faxing will not be functional")
    return the_telnyx_config

@hookimpl(specname="send_fax")
def da_send_fax(fax_number, the_file, config, country):
    if clicksend_config is not None and fax_provider == 'clicksend':
        if config not in clicksend_config['name']:
            raise DAException("There is no ClickSend configuration called " + str(config))
        import docassemble.webapp.fax.clicksend
        info = docassemble.webapp.fax.clicksend.send_fax(fax_number, the_file, clicksend_config['name'][config], country)
        the_key = 'da:faxcallback:sid:' + info['message_id']
        pipe = r.pipeline()
        pipe.set(the_key, json.dumps(info))
        pipe.expire(the_key, 86400)
        pipe.execute()
        return info['message_id']
    if telnyx_config is not None and fax_provider == 'telnyx':
        if config not in telnyx_config['name']:
            raise DAException("There is no Telnyx configuration called " + str(config))
        import docassemble.webapp.fax.telnyx
        info = docassemble.webapp.fax.telnyx.send_fax(fax_number, the_file, telnyx_config['name'][config], country)
        the_key = 'da:faxcallback:sid:' + info['id']
        pipe = r.pipeline()
        pipe.set(the_key, json.dumps(info))
        pipe.expire(the_key, 86400)
        pipe.execute()
        return info['id']
    if twilio_config is None:
        logmessage("da_send_fax: ignoring call to da_send_fax because Twilio not enabled")
        return None
    if config not in twilio_config['name'] or 'fax' not in twilio_config['name'][config] or twilio_config['name'][config]['fax'] in (False, None):
        logmessage("da_send_fax: ignoring call to da_send_fax because fax feature not enabled")
        return None
    account_sid = twilio_config['name'][config].get('account sid', None)
    auth_token = twilio_config['name'][config].get('auth token', None)
    from_number = twilio_config['name'][config].get('number', None)
    if account_sid is None or auth_token is None or from_number is None:
        logmessage("da_send_fax: ignoring call to da_send_fax because account sid, auth token, and/or number missing")
        return None
    from twilio.rest import Client as TwilioRestClient
    client = TwilioRestClient(account_sid, auth_token)
    fax = client.fax.v1.faxes.create(  # pylint: disable=no-member
        from_=from_number,
        to=fax_number,
        media_url=the_file.url_for(temporary=True, seconds=600),
        status_callback=url_for('fax.fax_callback', _external=True)
    )
    return fax.sid


def populate_fax_config():
    clicksend_config.clear()
    conf = get_clicksend_config()
    if conf is not None:
        clicksend_config.update(conf)
    telnyx_config.clear()
    conf = get_telnyx_config()
    if conf is not None:
        telnyx_config.update()
