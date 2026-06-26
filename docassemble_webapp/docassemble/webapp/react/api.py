import json
import re
import urllib
from urllib.parse import urlparse
from flask import current_app, request, abort, jsonify, session, Blueprint
from flask_cors import cross_origin
from flask_login import login_user, current_user
from sqlalchemy import select
from docassemble.base.generate_key import random_string
from docassemble.base.interview_cache import get_interview
from docassemble.base.language.words import word
from docassemble.base.thread_context import this_thread
from docassemble.webapp.config import (
    PREVENT_DEMO,
    google_api_key,
    reserved_argnames,
    final_default_yaml_filename,
    google_config,
    ga_configured,
    daconfig,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import csrf, db
from docassemble.webapp.interview.helpers import (
    go_back_in_session,
    create_new_interview,
    get_existing_session,
    reset_user_dict,
    get_question_data,
    set_session_variables,
)
from docassemble.webapp.lock import obtain_lock, release_lock
from docassemble.webapp.users.helpers import update_last_login
from docassemble.webapp.users.models import TempUser, UserModel
from docassemble.webapp.utils.helpers import (
    transform_json_variables,
    jsonify_with_status,
    true_or_false,
    url_for,
    from_safeid,
    json64unquote,
    tidy_action,
    current_info,
)
from docassemble.webapp.utils.logger import logmessage

react_bp = Blueprint(
    'react',
    __name__
)

@react_bp.route('/api/interview', methods=['GET', 'POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'HEAD'], automatic_options=True)
def api_interview():
    abort(404)
    if request.method == 'POST':
        post_data = request.get_json(silent=True)
        if post_data is None:
            return jsonify_with_status('The request must be JSON', 400)
        yaml_filename = post_data.get('i', None)
        secret = post_data.get('secret', None)
        session_id = post_data.get('session', None)
        url_args = post_data.get('url_args', None)
        user_code = post_data.get('user_code', None)
        command = post_data.get('command', None)
        referer = post_data.get('referer', None)
    else:
        yaml_filename = request.args.get('i', None)
        secret = request.args.get('secret', None)
        session_id = request.args.get('session', None)
        url_args = {}
        user_code = request.args.get('user_code', None)
        command = request.args.get('command', None)
        referer = request.args.get('referer', None)
        for key, val in request.args.items():
            if key not in ('session', 'secret', 'i', 'user_code', 'command', 'referer', 'action'):
                url_args[key] = val
        if len(url_args) == 0:
            url_args = None
    output = {}
    action = None
    reset_fully = False
    is_new = False
    changed = False
    if user_code:
        key = 'da:apiinterview:usercode:' + user_code
        user_info = r.get(key)
        if user_info is None:
            user_code = None
        else:
            r.expire(key, 60*60*24*30)
            try:
                user_info = json.loads(user_info)
            except:
                user_code = None
        if user_code:
            if user_info['user_id']:
                user = db.session.execute(select(UserModel).filter_by(id=user_info['user_id'])).scalar()
                if user is None or user.social_id.startswith('disabled$') or not user.active:
                    user_code = None
                else:
                    login_user(user, remember=False)
                    update_last_login(user)
            else:
                session['tempuser'] = user_info['temp_user_id']
    if not user_code:
        user_code = current_app.session_interface.manual_save_session(current_app, session).decode()
        if current_user.is_anonymous:
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            session['tempuser'] = new_temp_user.id
            user_info = {"user_id": None, "temp_user_id": new_temp_user.id, "sessions": {}}
        else:
            user_info = {"user_id": current_user.id, "temp_user_id": None, "sessions": {}}
        output['user_code'] = user_code
        changed = True
    need_to_reset = False
    new_session = False
    send_initial = False
    if yaml_filename.startswith('/'):
        parts = urlparse(yaml_filename)
        params = urllib.parse.parse_qs(parts.query)
        if params.get('action', '') != '':
            try:
                action = tidy_action(json64unquote(params['action']))
                assert len(action) > 0
            except:
                return jsonify_with_status(word("Invalid action."), 400)
        url_args = {}
        for key, val in dict(params).items():
            params[key] = val[0]
            if key not in reserved_argnames:
                url_args[key] = val[0]
        if parts.path == '/launch':
            code = params.get('c', None)
            if code is None:
                abort(403)
            the_key = 'da:resume_interview:' + str(code)
            data = r.get(the_key)
            if data is None:
                return jsonify_with_status(word("The link has expired."), 403)
            data = json.loads(data.decode())
            if data.get('once', False):
                r.delete(the_key)
            args = {}
            for key, val in params.items():
                if key != 'session':
                    args[key] = val
            yaml_filename = data['i']
            if 'session' in data:
                session_id = data['session']
                user_info['sessions'][yaml_filename] = session_id
            else:
                new_session = True
        if parts.path in ('/i', '/interview', '/'):
            ok = False
            if 'i' in params:
                yaml_filename = params['i']
                ok = True
            elif 'state' in params:
                try:
                    yaml_filename = re.sub(r'\^.*', '', from_safeid(params['state']))
                    ok = True
                except:
                    ok = False
            if not ok:
                if current_user.is_anonymous and not daconfig.get('allow anonymous access', True):
                    output['redirect'] = url_for('user.login')
                    return jsonify(output)
                if len(daconfig['dispatch']) > 0:
                    output['redirect'] = url_for('admin.interview_start')
                    return jsonify(output)
                yaml_filename = final_default_yaml_filename
        refer = None
        if parts.path.startswith('/start/') or parts.path.startswith('/run/'):
            m = re.search(r'/(start|run)/([^/]+)/$', parts.path)
            if m:
                refer = [m.group(1) + '_dispatch', m.group(2)]
                # dispatch = m.group(2)
            else:
                m = re.search(r'/(start|run)/([^/]+)/([^/]+)/(.*)/$', parts.path)
                if m:
                    refer = [m.group(1) + '_directory', m.group(2), m.group(3), m.group(4)]
                    yaml_filename = 'docassemble.' + m.group(2) + ':data/questions/' + m.group(3) + '/' + m.group(4) + '.yml'
                else:
                    m = re.search(r'/(start|run)/([^/]+)/(.*)/$', parts.path)
                    if m:
                        refer = [m.group(1), m.group(2), m.group(3)]
                        if re.search(r'playground[0-9]', m.group(2)):
                            yaml_filename = 'docassemble.' + m.group(2) + ':' + m.group(3) + '.yml'
                        else:
                            yaml_filename = 'docassemble.' + m.group(2) + ':data/questions/' + m.group(3) + '.yml'
                    else:
                        yaml_filename = None
            if yaml_filename is None:
                return jsonify_with_status("File not found", 404)
            if m.group(1) == 'start':
                new_session = True
        if true_or_false(params.get('reset', False)):
            need_to_reset = True
            if str(params['reset']) == '2':
                reset_fully = True
        if true_or_false(params.get('new_session', False)):
            new_session = True
        index_params = {'i': yaml_filename}
        output['i'] = yaml_filename
        output['page_sep'] = "#page"
        if refer is None:
            output['location_bar'] = url_for('interview.index', **index_params)
        elif refer[0] in ('start', 'run'):
            output['location_bar'] = url_for('interview.run_interview_in_package', package=refer[1], filename=refer[2])
            output['page_sep'] = "#/"
        elif refer[0] in ('start_dispatch', 'run_dispatch'):
            output['location_bar'] = url_for('interview.run_interview', dispatch=refer[1])
            output['page_sep'] = "#/"
        elif refer[0] in ('start_directory', 'run_directory'):
            output['location_bar'] = url_for('interview.run_interview_in_package_directory', package=refer[1], directory=refer[2], filename=refer[3])
            output['page_sep'] = "#/"
        else:
            output['location_bar'] = None
            for k, v in daconfig['dispatch'].items():
                if v == yaml_filename:
                    output['location_bar'] = url_for('interview.run_interview', dispatch=k)
                    output['page_sep'] = "#/"
                    break
            if output['location_bar'] is None:
                output['location_bar'] = url_for('interview.index', **index_params)
        send_initial = True
    if not yaml_filename:
        return jsonify_with_status("Parameter i is required.", 400)
    if not secret:
        secret = random_string(16)
        output['secret'] = secret
    secret = str(secret)
    this_thread.current_info = current_info(req=request, interface='api', secret=secret)
    if yaml_filename not in user_info['sessions'] or need_to_reset or new_session:
        # was_new = True
        if PREVENT_DEMO and (yaml_filename.startswith('docassemble.base:') or yaml_filename.startswith('docassemble.demo:')) and (current_user.is_anonymous or not current_user.has_role_or_permission('admin', 'developer', permissions=['demo_interviews'])):
            return jsonify_with_status(word("Not authorized"), 403)
        if current_user.is_anonymous and not daconfig.get('allow anonymous access', True):
            output['redirect'] = url_for('user.login', next=url_for('interview.index', i=yaml_filename, **url_args))
            return jsonify(output)
        if yaml_filename.startswith('docassemble.playground'):
            if not current_app.config['ENABLE_PLAYGROUND']:
                return jsonify_with_status(word("Not authorized"), 403)
        else:
            yaml_filename = re.sub(r':([^\/]+)$', r':data/questions/\1', yaml_filename)
        interview = get_interview(yaml_filename)
        if session_id is None:
            if need_to_reset and yaml_filename in user_info['sessions']:
                reset_user_dict(user_info['sessions'][yaml_filename], yaml_filename)
                del user_info['sessions'][yaml_filename]
            unique_sessions = interview.consolidated_metadata.get('sessions are unique', False)
            if unique_sessions is not False and not current_user.is_authenticated:
                if yaml_filename in user_info['sessions']:
                    del user_info['sessions'][yaml_filename]
                output['redirect'] = url_for('user.login', next=url_for('interview.index', i=yaml_filename, **url_args))
                return jsonify(output)
            if interview.consolidated_metadata.get('temporary session', False):
                if yaml_filename in user_info['sessions']:
                    reset_user_dict(user_info['sessions'][yaml_filename], yaml_filename)
                    del user_info['sessions'][yaml_filename]
                if current_user.is_authenticated:
                    while True:
                        the_session_id, encrypted = get_existing_session(yaml_filename, secret)  # pylint: disable=unused-variable
                        if the_session_id:
                            reset_user_dict(the_session_id, yaml_filename)
                        else:
                            break
                    need_to_reset = True
            if current_user.is_anonymous:
                if (not interview.allowed_to_initiate(is_anonymous=True)) or (not interview.allowed_to_access(is_anonymous=True)):
                    output['redirect'] = url_for('user.login', next=url_for('interview.index', i=yaml_filename, **url_args))
                    return jsonify(output)
            elif not interview.allowed_to_initiate(has_roles=[role.name for role in current_user.roles]):
                return jsonify_with_status(word("You are not allowed to access this interview."), 403)
            elif not interview.allowed_to_access(has_roles=[role.name for role in current_user.roles]):
                return jsonify_with_status(word("You are not allowed to access this interview."), 403)
            session_id = None
            if reset_fully:
                user_info['sessions'] = {}
            if (not need_to_reset) and (unique_sessions is True or (isinstance(unique_sessions, list) and len(unique_sessions) and current_user.has_role(*unique_sessions))):
                session_id, encrypted = get_existing_session(yaml_filename, secret)
        else:
            unique_sessions = interview.consolidated_metadata.get('sessions are unique', False)
            if unique_sessions is not False and not current_user.is_authenticated:
                if yaml_filename in user_info['sessions']:
                    del user_info['sessions'][yaml_filename]
                output['redirect'] = url_for('user.login', next=url_for('interview.index', i=yaml_filename, session=session_id, **url_args))
                return jsonify(output)
            if current_user.is_anonymous:
                if (not interview.allowed_to_initiate(is_anonymous=True)) or (not interview.allowed_to_access(is_anonymous=True)):
                    output['redirect'] = url_for('user.login', next=url_for('interview.index', i=yaml_filename, session=session_id, **url_args))
                    return jsonify(output)
            elif not interview.allowed_to_initiate(has_roles=[role.name for role in current_user.roles]):
                if yaml_filename in user_info['sessions']:
                    del user_info['sessions'][yaml_filename]
                return jsonify_with_status(word("You are not allowed to access this interview."), 403)
            elif not interview.allowed_to_access(has_roles=[role.name for role in current_user.roles]):
                if yaml_filename in user_info['sessions']:
                    del user_info['sessions'][yaml_filename]
                return jsonify_with_status(word("You are not allowed to access this interview."), 403)
            if need_to_reset:
                reset_user_dict(session_id, yaml_filename)
        session_id = None
    if new_session:
        session_id = None
        if yaml_filename in user_info['sessions']:
            del user_info['sessions'][yaml_filename]
    if not session_id:
        if yaml_filename in user_info['sessions']:
            session_id = user_info['sessions'][yaml_filename]
        else:
            try:
                (encrypted, session_id) = create_new_interview(yaml_filename, secret, url_args, referer, request)
            except BaseException as err:
                return jsonify_with_status(err.__class__.__name__ + ': ' + str(err), 400)
            user_info['sessions'][yaml_filename] = session_id
            changed = True
            is_new = True
        # output['session'] = session_id
    if changed:
        key = 'da:apiinterview:usercode:' + user_code
        pipe = r.pipeline()
        pipe.set(key, json.dumps(user_info))
        pipe.expire(key, 60*60*24*30)
        pipe.execute()
    if not is_new:
        if url_args is not None and isinstance(url_args, dict) and len(url_args) > 0:
            logmessage("url_args is " + repr(url_args))
            variables = {}
            for key, val in url_args.items():
                variables["url_args[%s]" % (repr(key),)] = val
            try:
                set_session_variables(yaml_filename, session_id, variables, secret=secret, use_lock=True)
            except BaseException as the_err:
                return jsonify_with_status(str(the_err), 400)
    obtain_lock(session_id, yaml_filename)
    if request.method == 'POST' and command == 'action':
        action = post_data.get('action', None)
    if action is not None:
        if not isinstance(action, dict) or 'action' not in action or 'arguments' not in action:
            release_lock(session_id, yaml_filename)
            return jsonify_with_status("Invalid action", 400)
        try:
            data = get_question_data(yaml_filename, session_id, secret, save=True, use_lock=False, action=action, post_setting=True, advance_progress_meter=True, encode=True)
        except BaseException as err:
            release_lock(session_id, yaml_filename)
            return jsonify_with_status(str(err), 400)
    else:
        try:
            data = get_question_data(yaml_filename, session_id, secret, save=False, use_lock=False, encode=True)
        except BaseException as err:
            release_lock(session_id, yaml_filename)
            return jsonify_with_status(str(err), 400)
    if request.method == 'POST':
        if command == 'back':
            if data['allow_going_back']:
                try:
                    data = go_back_in_session(yaml_filename, session_id, secret=secret, return_question=True, use_lock=False, encode=True)
                except BaseException as the_err:
                    release_lock(session_id, yaml_filename)
                    return jsonify_with_status(str(the_err), 400)
        elif command is None:
            variables = post_data.get('variables', None)
            if not isinstance(variables, dict):
                release_lock(session_id, yaml_filename)
                return jsonify_with_status("variables must be a dictionary", 400)
            if variables is not None:
                variables = transform_json_variables(variables)
            valid_variables = {}
            if 'fields' in data:
                for field in data['fields']:
                    if 'variable_name' in field and field.get('active', False):
                        valid_variables[field['variable_name']] = field
                    if field.get('required', False) and 'variable_name' in field:
                        if field['variable_name'] not in variables:
                            release_lock(session_id, yaml_filename)
                            return jsonify_with_status("variable %s is missing" % (field['variable_name'],), 400)
            for key, val in variables.items():
                if key not in valid_variables:
                    release_lock(session_id, yaml_filename)
                    return jsonify_with_status("invalid variable name " + repr(key), 400)
            try:
                data = set_session_variables(yaml_filename, session_id, variables, secret=secret, return_question=True, event_list=data.get('event_list', None), question_name=data.get('questionName', None), encode=True)
            except BaseException as the_err:
                release_lock(session_id, yaml_filename)
                return jsonify_with_status(str(the_err), 400)
        elif command != 'action':
            release_lock(session_id, yaml_filename)
            return jsonify_with_status("Invalid command", 400)
    if data.get('questionType', None) in ('response', 'sendfile'):
        output['question'] = {
            'questionType': data['questionType']
        }
    else:
        output['question'] = data
    release_lock(session_id, yaml_filename)
    if send_initial:
        output['setup'] = {}
        if google_api_key:
            output['setup']['googleApiKey'] = google_api_key
        if ga_configured and data['interview_options'].get('analytics on', True):
            interview_package = re.sub(r'^docassemble\.', '', re.sub(r':.*', '', yaml_filename))
            interview_filename = re.sub(r'\.ya?ml$', '', re.sub(r'.*[:\/]', '', yaml_filename), re.IGNORECASE)
            output['setup']['googleAnalytics'] = {'enable': True, 'ga_id': google_config.get('analytics id'), 'prefix': interview_package + '/' + interview_filename}
        else:
            output['setup']['googleAnalytics'] = {'enable': False}
    return jsonify(output)
