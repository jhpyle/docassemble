from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.config import daconfig

def get_twilio_config():
    if 'twilio' in daconfig:
        the_twilio_config = {}
        the_twilio_config['account sid'] = {}
        the_twilio_config['number'] = {}
        the_twilio_config['whatsapp number'] = {}
        the_twilio_config['name'] = {}
        if not isinstance(daconfig['twilio'], list):
            config_list = [daconfig['twilio']]
        else:
            config_list = daconfig['twilio']
        for tconfig in config_list:
            if isinstance(tconfig, dict) and 'account sid' in tconfig and ('number' in tconfig or 'whatsapp number' in tconfig):
                the_twilio_config['account sid'][str(tconfig['account sid'])] = 1
                if tconfig.get('number'):
                    the_twilio_config['number'][str(tconfig['number'])] = tconfig
                if tconfig.get('whatsapp number'):
                    the_twilio_config['whatsapp number'][str(tconfig['whatsapp number'])] = tconfig
                if 'default' not in the_twilio_config['name']:
                    the_twilio_config['name']['default'] = tconfig
                if 'name' in tconfig:
                    the_twilio_config['name'][tconfig['name']] = tconfig
            else:
                logmessage("improper setup in twilio configuration")
        if 'default' not in the_twilio_config['name']:
            the_twilio_config = None
    else:
        the_twilio_config = None
    return the_twilio_config

twilio_config = get_twilio_config()
