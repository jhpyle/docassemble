import requests
import docassemble.base.util
from docassemble.base.error import DAException


def send_fax(fax_number, the_file, config, country=None):  # pylint: disable=unused-argument
    if not bool((hasattr(the_file, 'extension') and the_file.extension == 'pdf') or (hasattr(the_file, 'mimetype') and the_file.mimetype == 'application/pdf')):
        the_file = docassemble.base.util.pdf_concatenate(the_file)
    telnyx_api_endpoint = config.get('api endpoint', 'https://api.telnyx.com/v2/faxes')
    headers = {"Authorization": "Bearer " + config['api key']}
    media_url = the_file.url_for(temporary=True, seconds=600)
    r = requests.post(telnyx_api_endpoint, json={"media_url": media_url, "connection_id": config['app id'], "to": fax_number, "from": config['number']}, headers=headers, timeout=600)
    if r.status_code != 202:
        raise DAException("Exception when calling Telnyx: status code is " + str(r.status_code) + " and response is " + r.text)
    try:
        response = r.json()
    except:
        raise DAException("Exception when calling Telnyx: response not JSON: " + r.text)
    try:
        response['data']['id']
    except:
        raise DAException("Exception when calling Telnyx: id not in response: " + r.text)
    try:
        response['data']['latest_update_time'] = response['data']['created_at']
    except:
        raise DAException("Exception when calling Telnyx: could not find created_at time " + r.text)
    return response['data']
