import os
import re
import importlib
import json
from pathlib import Path
from markupsafe import Markup
from flask import (
    current_app,
    request,
    redirect,
    Response,
    make_response,
    render_template,
    session,
)
from flask_login import current_user
import twilio
from docassemble_flask_user import login_required, roles_required
from docassemble.base.language.control import set_language
from docassemble.base.language.words import word
from docassemble.webapp.config import (
    DEBUG,
    DEFER,
    DEFAULT_LANGUAGE,
    ROOT,
    CHECKIN_INTERVAL,
    da_version,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import csrf
from docassemble.webapp.utils.fixpickle import fix_pickle_obj
from docassemble.webapp.interview.helpers import standard_app_values
from docassemble.webapp.sessions import update_session
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.twilio.helpers import twilio_config
from docassemble.webapp.users.helpers import needs_to_change_password
from docassemble.webapp.utils.helpers import (
    get_url_from_file_reference,
    indent_by,
    standard_scripts,
    decode_dict,
    redis_script,
    standard_html_start,
)
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from .blueprint import monitor_bp

@monitor_bp.route("/digits", methods=['POST', 'GET'])
@csrf.exempt
def digits_endpoint():
    set_language(DEFAULT_LANGUAGE)
    resp = twilio.twiml.voice_response.VoiceResponse()
    if twilio_config is None:
        logmessage("digits: ignoring call to digits because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("digits: request to digits did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    if "Digits" in request.form:
        the_digits = re.sub(r'[^0-9]', '', request.form["Digits"])
        logmessage("digits: got " + str(the_digits))
        phone_number = r.get('da:callforward:' + str(the_digits))
        if phone_number is None:
            resp.say(word("I am sorry.  The code you entered is invalid or expired.  Goodbye."))
            resp.hangup()
        else:
            phone_number = phone_number.decode()
            resp.dial(number=phone_number)
            r.delete('da:callforward:' + str(the_digits))
    else:
        logmessage("digits: no digits received")
        resp.say(word("No access code was entered."))
        resp.hangup()
    return Response(str(resp), mimetype='text/xml')


@monitor_bp.route("/voice", methods=['POST', 'GET'])
@csrf.exempt
def voice():
    set_language(DEFAULT_LANGUAGE)
    resp = twilio.twiml.voice_response.VoiceResponse()
    if twilio_config is None:
        logmessage("voice: ignoring call to voice because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if 'voice' not in twilio_config['name']['default'] or twilio_config['name']['default']['voice'] in (False, None):
        logmessage("voice: ignoring call to voice because voice feature not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("voice: request to voice did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    for item in request.form:
        logmessage("voice: item " + str(item) + " is " + str(request.form[item]))
    with resp.gather(action=url_for('monitor.digits_endpoint'), finishOnKey='#', method="POST", timeout=10, numDigits=5) as gg:
        gg.say(word("Please enter the four digit code, followed by the pound sign."))

    # twilio_config = daconfig.get('twilio', None)
    # if twilio_config is None:
    #     logmessage("Could not get twilio configuration")
    #     return
    # twilio_caller_id = twilio_config.get('number', None)
    # if "To" in request.form and request.form["To"] != '':
    #     dial = resp.dial(callerId=twilio_caller_id)
    #     if phone_pattern.match(request.form["To"]):
    #         dial.number(request.form["To"])
    #     else:
    #         dial.client(request.form["To"])
    # else:
    #     resp.say("Thanks for calling!")

    return Response(str(resp), mimetype='text/xml')


@monitor_bp.route('/visit_interview', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'advocate'])
def visit_interview():
    setup_translation()
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    key = 'da:session:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    try:
        obj = fix_pickle_obj(r.get(key))
    except:
        return ('Interview not found', 404)
    if 'secret' not in obj or 'encrypted' not in obj:
        return ('Interview not found', 404)
    update_session(i, uid=uid, encrypted=obj['encrypted'])
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    if 'tempuser' in session:
        del session['tempuser']
    response = redirect(url_for('interview.index', i=i))
    response.set_cookie('visitor_secret', obj['secret'], httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'])
    return response


@monitor_bp.route('/observer', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'advocate'])
def observer():
    setup_translation()
    session['observer'] = 1
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    the_key = 'da:html:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    html = r.get(the_key)
    if html is not None:
        obj = json.loads(html.decode())
    else:
        logmessage("observer: failed to load JSON from key " + the_key)
        obj = {}
    initial_values = standard_app_values()
    initial_values.update({
        "daUid": uid,
        "daUserObserved": str(userid),
        "daCheckinSeconds": CHECKIN_INTERVAL,
        "daUserId": current_user.id,
        "daJsEmbed": False,
        "daAllowGoingBack": False,
        "daSteps": obj['steps'],
        "daIsUser": False,
        "daChatStatus": 'off',
        "daChatAvailable": 'unavailable',
        "daChatMode": 'other',
        "daSendChanges": False,
        "daBeingControlled": False,
        "daInformed": {},
        "daUsingGA": False,
        "daUsingSegment": False,
        "daGaIds": None,
        "daDoAction": None,
        "daInterviewPackage": re.sub(r'^docassemble\.', '', re.sub(r':.*', '', i)),
        "daInterviewFilename": re.sub(r'\.ya?ml$', '', re.sub(r'.*[:\/]', '', i), re.IGNORECASE),
        "daQuestionID": {'id': obj['question_id']},
        "daInterviewUrl": url_for('interview.index', i=i),
        "daLocationBar": url_for('interview.index', i=i),
        "daPostURL": url_for('interview.index', i=i),
        "daYamlFilename": i,
        "daMessageLog": [],
        "daGetVariablesUrl": url_for('develop.get_variables', i=i),
        "daChatRoles": None,
        "daChatPartnerRoles": None,
        "daShouldForceFullScreen": False,
        "daPageSep": "#page",
        "daCheckinUrl": url_for('interview.checkin', i=i),
        "daCheckoutUrl": url_for('interview.checkout', i=i),
        "daShouldDebugReadabilityHelp": False,
        "daShouldDebugReadabilityQuestion": False,
        "daDefaultPopoverTrigger": 'focus',
        "daCheckinUrlWithInterview": url_for('interview.checkin', i=i),
        "daReloadAfterSeconds": 0,
        "daCustomItems": [],
        "daTrackingEnabled": False,
        "daInitialExtraScripts": obj['extra_scripts'],
        "daQuestionData": None,
        "daAutoColorScheme": False,
        "daObserverMode": True,
        "daRootUrl": ROOT
    })
    page_title = word('Observation')
    scripts = "\n    " + standard_scripts(interview_language=obj.get('lang', 'en'))
    if 'javascript' in obj['external_files']:
        for item in obj['external_files']:
            packageref = item[0]
            fileref = item[1]
            the_url = get_url_from_file_reference(fileref, {"_package": packageref})
            if the_url is not None:
                scripts += "\n" + f'    <script{DEFER} src="{get_url_from_file_reference(fileref, {"_package": packageref})}"></script>'
    output = standard_html_start(interview_language=obj.get('lang', 'en'), debug=DEBUG, bootstrap_theme=obj.get('bootstrap_theme', None))
    if 'css' in obj['external_files']:
        for item in obj['external_files']['css']:
            packageref = item[0]
            fileref = item[1]
            the_url = get_url_from_file_reference(fileref, {"_package": packageref})
            if the_url is not None:
                output += "\n" + '    <link href="' + the_url + '" rel="stylesheet">'
    output += current_app.config['GLOBAL_CSS'] + "\n" + indent_by("".join(obj.get('extra_css', [])), 4)
    output += '\n    <title>' + page_title + '</title>\n  </head>\n  <body class="' + obj.get('bodyclass', 'dabody da-pad-for-navbar da-pad-for-footer') + '">\n  <div id="dabody">\n  '
    output += obj.get('body', '')
    output += f"""    </div>
    </div>{scripts}
    {redis_script(initial_values)}
    {current_app.config['GLOBAL_JS']}
  </body>
</html>"""
    response = make_response(output.encode('utf-8'), '200 OK')
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    return response


@monitor_bp.route('/monitor', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'advocate'])
def monitor():
    if not current_app.config['ENABLE_MONITOR']:
        return ('File not found', 404)
    setup_translation()
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('monitor.monitor')))
    session['monitor'] = 1
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    phone_number_key = 'da:monitor:phonenumber:' + str(session['user_id'])
    default_phone_number = r.get(phone_number_key)
    if default_phone_number is None:
        default_phone_number = ''
    else:
        default_phone_number = default_phone_number.decode()
    sub_role_key = 'da:monitor:userrole:' + str(session['user_id'])
    if r.exists(sub_role_key):
        subscribed_roles = decode_dict(r.hgetall(sub_role_key))
        r.expire(sub_role_key, 2592000)
    else:
        subscribed_roles = {}
    key = 'da:monitor:available:' + str(current_user.id)
    if r.exists(key):
        da_available_for_chat = 'true'
    else:
        da_available_for_chat = 'false'
    call_forwarding_on = 'false'
    if twilio_config is not None:
        forwarding_phone_number = twilio_config['name']['default'].get('number', None)
        if forwarding_phone_number is not None:
            call_forwarding_on = 'true'
    initial_values = {
        "daUserid": str(current_user.id),
        "daPhoneOnMessage": word("The user can call you.  Click to cancel."),
        "daPhoneOffMessage": word("Click if you want the user to be able to call you."),
        "daUsePhone": call_forwarding_on,
        "daSubscribedRoles": subscribed_roles,
        "daAvailableForChat": da_available_for_chat,
        "daPhoneNumber": default_phone_number,
        "daBrowserTitle": word('Monitor'),
        "daFaviconIcoUrl": url_for('favicon', nocache="1"),
        "daChatIcoUrl": url_for('static', filename='app/chat.ico', v=da_version, nocache=1),
        "daAlreadyControlled": word("That screen is already being controlled by another operator"),
        "daNewMessageBelow": word("New message below"),
        "daNewConversationBelow": word("New conversation below"),
        "daNewMessageAbove": word("New message above"),
        "daNewConversationAbove": word("New conversation above"),
        "daCheckinInterval": str(CHECKIN_INTERVAL),
        "daOfflineWord": word("offline"),
        "daAnonymousVisitor": word("anonymous visitor"),
        "daUnblockWord": word("Unblock"),
        "daBlockWord": word("Block"),
        "daJoinWord": word("Join"),
        "daVisitInterviewUrl": url_for('monitor.visit_interview'),
        "daObserverUrl": url_for('monitor.observer'),
        "daObserveWord": word("Observe"),
        "daStopObservingWord": word("Stop Observing"),
        "daControlWord": word("Control"),
        "daStopControllingWord": word("Stop Controlling"),
        "daNotificationClickOnMp3": url_for('static', filename='sounds/notification-click-on.mp3', v=da_version),
        "daNotificationClickOnOgg": url_for('static', filename='sounds/notification-click-on.ogg', v=da_version),
        "daNotificationStaplerMp3": url_for('static', filename='sounds/notification-stapler.mp3', v=da_version),
        "daNotificationStaplerOgg": url_for('static', filename='sounds/notification-stapler.ogg', v=da_version),
        "daNotificationSnapMp3": url_for('static', filename='sounds/notification-snap.mp3', v=da_version),
        "daNotificationSnapOgg": url_for('static', filename='sounds/notification-snap.ogg', v=da_version),
        "daRootUrl": ROOT,
        "daNewChatConnection": word("New chat connection from"),
        "daSendWord": word("Send")
      }
    script = f"""
    <script{DEFER} src="{url_for('static', filename='app/monitorbundle.min.js', v=da_version)}"></script>
    {redis_script(initial_values)}"""
    response = make_response(render_template('monitor/monitor.html', version_warning=None, bodyclass='daadminbody', extra_js=Markup(script), tab_title=word('Monitor'), page_title=word('Monitor')), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@monitor_bp.route('/monitorbundle.js', methods=['GET'])
def monitor_bundle():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = ''
    for parts in [['app', 'socket.io.js'], ['app', 'monitor.js']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    return Response(output, mimetype='application/javascript')
