import json
from flask import request, Blueprint
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import csrf
from docassemble.webapp.twilio.helpers import twilio_config
from docassemble.webapp.utils.logger import logmessage
from .helpers import telnyx_config, clicksend_config, fax_provider

fax_bp = Blueprint(
    'fax',
    __name__
)

@fax_bp.route("/fax_callback", methods=['POST'])
@csrf.exempt
def fax_callback():
    if twilio_config is None:
        logmessage("fax_callback: Twilio not enabled")
        return ('', 204)
    post_data = request.form.copy()
    if 'FaxSid' not in post_data or 'AccountSid' not in post_data:
        logmessage("fax_callback: FaxSid and/or AccountSid missing")
        return ('', 204)
    tconfig = None
    for config_name, config_info in twilio_config['name'].items():  # pylint: disable=unused-variable
        if 'account sid' in config_info and config_info['account sid'] == post_data['AccountSid']:
            tconfig = config_info
    if tconfig is None:
        logmessage("fax_callback: account sid of fax callback did not match any account sid in the Twilio configuration")
    if 'fax' not in tconfig or tconfig['fax'] in (False, None):
        logmessage("fax_callback: fax feature not enabled")
        return ('', 204)
    params = {}
    for param in ('FaxSid', 'From', 'To', 'RemoteStationId', 'FaxStatus', 'ApiVersion', 'OriginalMediaUrl', 'NumPages', 'MediaUrl', 'ErrorCode', 'ErrorMessage'):
        params[param] = post_data.get(param, None)
    the_key = 'da:faxcallback:sid:' + post_data['FaxSid']
    pipe = r.pipeline()
    pipe.set(the_key, json.dumps(params))
    pipe.expire(the_key, 86400)
    pipe.execute()
    return ('', 204)


@fax_bp.route("/clicksend_fax_callback", methods=['POST'])
@csrf.exempt
def clicksend_fax_callback():
    if clicksend_config is None or fax_provider != 'clicksend':
        logmessage("clicksend_fax_callback: Clicksend not enabled")
        return ('', 204)
    post_data = request.form.copy()
    if 'message_id' not in post_data:
        logmessage("clicksend_fax_callback: message_id missing")
        return ('', 204)
    the_key = 'da:faxcallback:sid:' + post_data['message_id']
    the_json = r.get(the_key)
    try:
        params = json.loads(the_json)
    except:
        logmessage("clicksend_fax_callback: existing fax record could not be found")
        return ('', 204)
    for param in ('timestamp_send', 'timestamp', 'message_id', 'status', 'status_code', 'status_text', 'error_code', 'error_text', 'custom_string', 'user_id', 'subaccount_id', 'message_type'):
        params[param] = post_data.get(param, None)
    pipe = r.pipeline()
    pipe.set(the_key, json.dumps(params))
    pipe.expire(the_key, 86400)
    pipe.execute()
    return ('', 204)


@fax_bp.route("/telnyx_fax_callback", methods=['POST'])
@csrf.exempt
def telnyx_fax_callback():
    if telnyx_config is None:
        logmessage("telnyx_fax_callback: Telnyx not enabled")
        return ('', 204)
    data = request.get_json(silent=True)
    try:
        the_id = data['data']['payload']['fax_id']
    except:
        logmessage("telnyx_fax_callback: fax_id not found")
        return ('', 204)
    the_key = 'da:faxcallback:sid:' + str(the_id)
    the_json = r.get(the_key)
    try:
        params = json.loads(the_json)
    except:
        logmessage("telnyx_fax_callback: existing fax record could not be found")
        return ('', 204)
    try:
        params['status'] = data['data']['payload']['status']
        if params['status'] == 'failed' and 'failure_reason' in data['data']['payload']:
            params['status'] += ': ' + data['data']['payload']['failure_reason']
            logmessage("telnyx_fax_callback: failure because " + data['data']['payload']['failure_reason'])
    except:
        logmessage("telnyx_fax_callback: could not find status")
    try:
        params['latest_update_time'] = data['data']['occurred_at']
    except:
        logmessage("telnyx_fax_callback: could not update latest_update_time")
    if 'status' in params and params['status'] == 'delivered':
        try:
            params['page_count'] = data['data']['payload']['page_count']
        except:
            logmessage("telnyx_fax_callback: could not update page_count")
    pipe = r.pipeline()
    pipe.set(the_key, json.dumps(params))
    pipe.expire(the_key, 86400)
    pipe.execute()
    return ('', 204)
