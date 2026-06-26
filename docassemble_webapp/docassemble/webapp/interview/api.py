import tempfile
import json
import re
import os
from flask import request, jsonify, make_response
from flask_cors import cross_origin
from flask_login import current_user
from docassemble.base.functions import safe_json
from docassemble.base.generate_key import random_string
from docassemble.base.interview_source import interview_source_from_string
from docassemble.base.parse import Interview, InterviewStatus
from docassemble.base.thread_context import this_thread
from docassemble.webapp.admin.funcs import interview_menu
from docassemble.webapp.api.helpers import api_verify
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import csrf
from docassemble.webapp.files.file_number import get_new_file_number
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.utils.filenames import (
    get_ext_and_mimetype,
    secure_filename_unicode_ok,
    secure_filename,
)
from docassemble.webapp.utils.helpers import (
    process_file,
    illegal_variable_name,
    from_safeid,
    get_vars_in_use,
    transform_json_variables,
    parse_api_sessions_query,
    jsonify_with_status,
    true_or_false,
    current_info,
    safeid,
)
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from .blueprint import interview_bp
from .helpers import (
    user_interviews,
    get_session_variables,
    go_back_in_session,
    read_fields,
    create_new_interview,
    get_question_data,
    set_session_variables,
    run_action_in_session,
)

@interview_bp.route('/api/fields', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_fields():
    if not api_verify(roles=['admin', 'developer'], permissions=['template_parse']):
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    output_format = post_data.get('format', 'json')
    if output_format not in ('json', 'yaml'):
        return jsonify_with_status("Invalid output format.", 400)
    if 'template' not in request.files:
        return jsonify_with_status("File not included.", 400)
    the_files = request.files.getlist('template')
    if not the_files:
        return jsonify_with_status("File not included.", 400)
    for the_file in the_files:
        filename = secure_filename(the_file.filename)
        temp_file = tempfile.NamedTemporaryFile(prefix="datemp", delete=False)
        the_file.save(temp_file.name)
        try:
            input_format = os.path.splitext(filename.lower())[1][1:]
        except:
            input_format = 'bin'
        if input_format == 'md':
            input_format = 'markdown'
        if input_format not in ('docx', 'markdown', 'pdf'):
            return jsonify_with_status("Invalid input format.", 400)
        try:
            output = read_fields(temp_file.name, filename, input_format, output_format)
        except BaseException as err:
            logmessage("api_fields: got error " + err.__class__.__name__ + ": " + str(err))
            if output_format == 'yaml':
                return jsonify_with_status("No fields could be found.", 400)
            return jsonify({'fields': []})
        break
    if output_format == 'yaml':
        response = make_response(output.encode('utf-8'), '200 OK')
        response.headers['Content-type'] = 'text/plain; charset=utf-8'
    else:
        response = make_response(output.encode('utf-8'), 200)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


@interview_bp.route('/api/session/back', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_session_back():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    yaml_filename = post_data.get('i', None)
    session_id = post_data.get('session', None)
    secret = str(post_data.get('secret', None))
    reply_with_question = true_or_false(post_data.get('question', True))
    if yaml_filename is None or session_id is None:
        return jsonify_with_status("Parameters i and session are required.", 400)
    this_thread.current_info['yaml_filename'] = yaml_filename
    try:
        data = go_back_in_session(yaml_filename, session_id, secret=secret, return_question=reply_with_question, use_lock=False, encode=False)
    except BaseException as the_err:
        return jsonify_with_status(str(the_err), 400)
    if data is None:
        return ('', 204)
    if data.get('questionType', None) == 'response':
        return data['response']
    return jsonify(**data)


@interview_bp.route('/api/session', methods=['GET', 'POST', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'DELETE', 'HEAD'], automatic_options=True)
def api_session():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    if request.method == 'GET':
        yaml_filename = request.args.get('i', None)
        session_id = request.args.get('session', None)
        secret = request.args.get('secret', None)
        if secret is not None:
            secret = str(secret)
        if yaml_filename is None or session_id is None:
            return jsonify_with_status("Parameters i and session are required.", 400)
        this_thread.current_info['yaml_filename'] = yaml_filename
        try:
            variables = get_session_variables(yaml_filename, session_id, secret=secret, simplify=True, use_lock=False)
        except BaseException as the_err:
            return jsonify_with_status(str(the_err), 400)
        return jsonify(variables)
    if request.method == 'POST':
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        yaml_filename = post_data.get('i', None)
        session_id = post_data.get('session', None)
        secret = str(post_data.get('secret', None))
        question_name = post_data.get('question_name', None)
        treat_as_raw = true_or_false(post_data.get('raw', False))
        advance_progress_meter = true_or_false(post_data.get('advance_progress_meter', False))
        post_setting = not true_or_false(post_data.get('overwrite', False))
        reply_with_question = true_or_false(post_data.get('question', True))
        if yaml_filename is None or session_id is None:
            return jsonify_with_status("Parameters i and session are required.", 400)
        this_thread.current_info['yaml_filename'] = yaml_filename
        if 'variables' in post_data and isinstance(post_data['variables'], dict):
            variables = post_data['variables']
        else:
            try:
                variables = json.loads(post_data.get('variables', '{}'))
            except:
                return jsonify_with_status("Malformed variables.", 400)
        if not treat_as_raw:
            variables = transform_json_variables(variables)
        if 'file_variables' in post_data and isinstance(post_data['file_variables'], dict):
            file_variables = post_data['file_variables']
        else:
            try:
                file_variables = json.loads(post_data.get('file_variables', '{}'))
            except:
                return jsonify_with_status("Malformed list of file variables.", 400)
        if 'delete_variables' in post_data and isinstance(post_data['delete_variables'], list):
            del_variables = post_data['delete_variables']
        else:
            try:
                del_variables = json.loads(post_data.get('delete_variables', '[]'))
            except:
                return jsonify_with_status("Malformed list of delete variables.", 400)
        if 'event_list' in post_data and isinstance(post_data['event_list'], list):
            event_list = post_data['event_list']
        else:
            try:
                event_list = json.loads(post_data.get('event_list', '[]'))
                assert isinstance(event_list, list)
            except:
                return jsonify_with_status("Malformed event list.", 400)
        if not isinstance(variables, dict):
            return jsonify_with_status("Variables data is not a dict.", 400)
        if not isinstance(file_variables, dict):
            return jsonify_with_status("File variables data is not a dict.", 400)
        if not isinstance(del_variables, list):
            return jsonify_with_status("Delete variables data is not a list.", 400)
        if not isinstance(event_list, list):
            return jsonify_with_status("Event list data is not a list.", 400)
        literal_variables = {}
        for filekey in request.files:
            if filekey not in file_variables:
                file_variables[filekey] = filekey
            the_files = request.files.getlist(filekey)
            files_to_process = []
            if the_files:
                for the_file in the_files:
                    safe_filename = secure_filename(the_file.filename)
                    filename = secure_filename_unicode_ok(the_file.filename)
                    file_number = get_new_file_number(session_id, safe_filename, yaml_filename)
                    extension, mimetype = get_ext_and_mimetype(filename)
                    saved_file = SavedFile(file_number, extension=extension, fix=True, should_not_exist=True)
                    temp_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.' + extension, delete=False)
                    the_file.save(temp_file.name)
                    process_file(saved_file, temp_file.name, mimetype, extension)
                    files_to_process.append((filename, file_number, mimetype, extension))
            file_field = file_variables[filekey]
            if illegal_variable_name(file_field):
                return jsonify_with_status("Malformed file variable.", 400)
            if len(files_to_process) > 0:
                elements = []
                indexno = 0
                for (filename, file_number, mimetype, extension) in files_to_process:
                    elements.append("docassemble.base.util.DAFile(" + repr(file_field + '[' + str(indexno) + ']') + ", filename=" + repr(filename) + ", number=" + str(file_number) + ", make_pngs=True, mimetype=" + repr(mimetype) + ", extension=" + repr(extension) + ")")
                    indexno += 1
                literal_variables[file_field] = "docassemble.base.util.DAFileList(" + repr(file_field) + ", elements=[" + ", ".join(elements) + "])"
            else:
                literal_variables[file_field] = "None"
        try:
            data = set_session_variables(yaml_filename, session_id, variables, secret=secret, return_question=reply_with_question, literal_variables=literal_variables, del_variables=del_variables, question_name=question_name, event_list=event_list, advance_progress_meter=advance_progress_meter, post_setting=post_setting)
        except BaseException as the_err:
            return jsonify_with_status(str(the_err), 400)
        if data is None:
            return ('', 204)
        if data.get('questionType', None) == 'response':
            return data['response']
        return jsonify(**data)
    if request.method == 'DELETE':
        yaml_filename = request.args.get('i', None)
        session_id = request.args.get('session', None)
        if yaml_filename is None or session_id is None:
            return jsonify_with_status("Parameters i and session are required.", 400)
        user_interviews(action='delete', filename=yaml_filename, session=session_id)
        return ('', 204)
    return ('', 204)


@interview_bp.route('/api/session/new', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_session_new():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    yaml_filename = request.args.get('i', None)
    if yaml_filename is None:
        return jsonify_with_status("Parameter i is required.", 400)
    secret = request.args.get('secret', None)
    if secret is None:
        new_secret = True
        secret = random_string(16)
    else:
        new_secret = False
    secret = str(secret)
    url_args = {}
    for argname in request.args:
        if argname in ('i', 'secret', 'key'):
            continue
        if re.match('[A-Za-z_][A-Za-z0-9_]*', argname):
            url_args[argname] = request.args[argname]
    this_thread.current_info['yaml_filename'] = yaml_filename
    try:
        (encrypted, session_id) = create_new_interview(yaml_filename, secret, url_args, None, request)
    except BaseException as err:
        return jsonify_with_status(err.__class__.__name__ + ': ' + str(err), 400)
    if encrypted and new_secret:
        return jsonify({'session': session_id, 'i': yaml_filename, 'secret': secret, 'encrypted': encrypted})
    return jsonify({'session': session_id, 'i': yaml_filename, 'encrypted': encrypted})


@interview_bp.route('/api/session/question', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_session_question():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    yaml_filename = request.args.get('i', None)
    session_id = request.args.get('session', None)
    secret = request.args.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if yaml_filename is None or session_id is None:
        return jsonify_with_status("Parameters i and session are required.", 400)
    this_thread.current_info['yaml_filename'] = yaml_filename
    try:
        data = get_question_data(yaml_filename, session_id, secret)
    except BaseException as err:
        return jsonify_with_status(str(err), 400)
    if data.get('questionType', None) == 'response':
        return data['response']
    return jsonify(**data)


@interview_bp.route('/api/session/action', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_session_action():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    result = run_action_in_session(post_data)
    if not isinstance(result, dict):
        return result
    if result['status'] == 'success':
        return ('', 204)
    return jsonify_with_status(result['message'], 400)


@interview_bp.route('/api/list', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_list():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    return jsonify(interview_menu(absolute_urls=true_or_false(request.args.get('absolute_urls', True)), start_new=False, tag=request.args.get('tag', None)))


@interview_bp.route('/api/user/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'DELETE', 'HEAD'], automatic_options=True)
def api_user_interviews():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    filename = request.args.get('i', None)
    session_id = request.args.get('session', None)
    query = request.args.get('query', None)
    try:
        query = parse_api_sessions_query(query)
    except:
        return jsonify_with_status("Invalid query parameter", 400)
    tag = request.args.get('tag', None)
    secret = request.args.get('secret', None)
    if secret is not None:
        secret = str(secret)
    include_dict = true_or_false(request.args.get('include_dictionary', False))
    next_id_code = request.args.get('next_id', None)
    if next_id_code:
        try:
            start_id = int(from_safeid(next_id_code))
            assert start_id >= 0
        except:
            start_id = None
    else:
        start_id = None
    if request.method == 'GET':
        try:
            (the_list, start_id) = user_interviews(user_id=current_user.id, secret=secret, filename=filename, session=session_id, query=query, exclude_invalid=False, tag=tag, include_dict=include_dict, start_id=start_id)
        except:
            return jsonify_with_status("Error reading interview list.", 400)
        if start_id is None:
            next_id = None
        else:
            next_id = safeid(str(start_id))
        return jsonify({'next_id': next_id, 'items': safe_json(the_list)})
    if request.method == 'DELETE':
        start_id = None
        while True:
            try:
                (the_list, start_id) = user_interviews(user_id=current_user.id, filename=filename, session=session_id, query=query, exclude_invalid=False, tag=tag, include_dict=False, start_id=start_id)
            except:
                return jsonify_with_status("Error reading interview list.", 400)
            for info in the_list:
                user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
            if start_id is None:
                break
        return ('', 204)
    return ('', 204)


@interview_bp.route('/api/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'DELETE', 'HEAD'], automatic_options=True)
def api_interviews():
    if not api_verify(roles=['admin', 'advocate'], permissions=['access_sessions']):
        return jsonify_with_status("Access denied.", 403)
    filename = request.args.get('i', None)
    session_id = request.args.get('session', None)
    query = request.args.get('query', None)
    try:
        query = parse_api_sessions_query(query)
    except:
        return jsonify_with_status("Invalid query parameter", 400)
    tag = request.args.get('tag', None)
    secret = request.args.get('secret', None)
    if secret is not None:
        secret = str(secret)
    include_dict = true_or_false(request.args.get('include_dictionary', False))
    next_id_code = request.args.get('next_id', None)
    if next_id_code:
        try:
            start_id = int(from_safeid(next_id_code))
            assert start_id >= 0
        except:
            start_id = None
    else:
        start_id = None
    if request.method == 'GET':
        try:
            (the_list, start_id) = user_interviews(secret=secret, filename=filename, session=session_id, query=query, exclude_invalid=False, tag=tag, include_dict=include_dict, start_id=start_id)
        except BaseException as err:
            return jsonify_with_status("Error reading interview list: " + str(err), 400)
        if start_id is None:
            next_id = None
        else:
            next_id = safeid(str(start_id))
        return jsonify({'next_id': next_id, 'items': safe_json(the_list)})
    if request.method == 'DELETE':
        if not current_user.has_role_or_permission('admin', 'advocate', permissions=['edit_sessions']):
            return jsonify_with_status("Access denied.", 403)
        start_id = None
        while True:
            try:
                (the_list, start_id) = user_interviews(filename=filename, session=session_id, query=query, exclude_invalid=False, tag=tag, include_dict=False, start_id=start_id)
            except:
                return jsonify_with_status("Error reading interview list.", 400)
            for info in the_list:
                if info['user_id'] is not None:
                    user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
                else:
                    user_interviews(temp_user_id=info['temp_user_id'], action='delete', filename=info['filename'], session=info['session'])
            if start_id is None:
                break
        return ('', 204)
    return ('', 204)


@interview_bp.route('/api/users/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'DELETE', 'HEAD'], automatic_options=True)
def api_users_interviews():
    if not api_verify(roles=['admin', 'advocate'], permissions=['access_sessions']):
        return jsonify_with_status("Access denied.", 403)
    user_id = request.args.get('user_id', None)
    filename = request.args.get('i', None)
    session_id = request.args.get('session', None)
    query = request.args.get('query', None)
    try:
        query = parse_api_sessions_query(query)
    except:
        return jsonify_with_status("Invalid query parameter", 400)
    secret = request.args.get('secret', None)
    tag = request.args.get('tag', None)
    next_id_code = request.args.get('next_id', None)
    if next_id_code:
        try:
            start_id = int(from_safeid(next_id_code))
            assert start_id >= 0
        except:
            start_id = None
    else:
        start_id = None
    if secret is not None:
        secret = str(secret)
    if request.method == 'GET':
        include_dict = true_or_false(request.args.get('include_dictionary', False))
        try:
            (the_list, start_id) = user_interviews(user_id=user_id, secret=secret, exclude_invalid=False, tag=tag, filename=filename, session=session_id, query=query, include_dict=include_dict, start_id=start_id)
        except BaseException as err:
            return jsonify_with_status("Error getting interview list.  " + str(err), 400)
        if start_id is None:
            next_id = None
        else:
            next_id = safeid(str(start_id))
        return jsonify({'next_id': next_id, 'items': safe_json(the_list)})
    if request.method == 'DELETE':
        start_id = None
        while True:
            try:
                (the_list, start_id) = user_interviews(user_id=user_id, exclude_invalid=False, tag=tag, filename=filename, session=session_id, query=query, include_dict=False, start_id=start_id)
            except:
                return jsonify_with_status("Error reading interview list.", 400)
            for info in the_list:
                user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
            if start_id is None:
                break
        return ('', 204)
    return ('', 204)


@interview_bp.route('/api/user/<int:user_id>/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'DELETE', 'HEAD'], automatic_options=True)
def api_user_user_id_interviews(user_id):
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    if not (current_user.id == user_id or current_user.has_role_or_permission('admin', 'advocate', permissions=['access_sessions'])):
        return jsonify_with_status("Access denied.", 403)
    filename = request.args.get('i', None)
    session_id = request.args.get('session', None)
    query = request.args.get('query', None)
    try:
        query = parse_api_sessions_query(query)
    except:
        return jsonify_with_status("Invalid query parameter", 400)
    secret = request.args.get('secret', None)
    tag = request.args.get('tag', None)
    next_id_code = request.args.get('next_id', None)
    if next_id_code:
        try:
            start_id = int(from_safeid(next_id_code))
            assert start_id >= 0
        except:
            start_id = None
    else:
        start_id = None
    if secret is not None:
        secret = str(secret)
    include_dict = true_or_false(request.args.get('include_dictionary', False))
    if request.method == 'GET':
        try:
            (the_list, start_id) = user_interviews(user_id=user_id, secret=secret, exclude_invalid=False, tag=tag, filename=filename, session=session_id, query=query, include_dict=include_dict, start_id=start_id)
        except:
            return jsonify_with_status("Error reading interview list.", 400)
        if start_id is None:
            next_id = None
        else:
            next_id = safeid(str(start_id))
        return jsonify({'next_id': next_id, 'items': safe_json(the_list)})
    if request.method == 'DELETE':
        start_id = None
        while True:
            try:
                (the_list, start_id) = user_interviews(user_id=user_id, exclude_invalid=False, tag=tag, filename=filename, session=session_id, query=query, include_dict=False, start_id=start_id)
            except:
                return jsonify_with_status("Error reading interview list.", 400)
            for info in the_list:
                user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
            if start_id is None:
                break
        return ('', 204)
    return ('', 204)


@interview_bp.route('/api/resume_url', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_resume_url():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    filename = post_data.get('i', None)
    if filename is None:
        return jsonify_with_status("No filename supplied.", 400)
    session_id = post_data.get('session', post_data.get('session_id', None))
    if 'url_args' in post_data:
        if isinstance(post_data['url_args'], dict):
            url_args = post_data['url_args']
        else:
            try:
                url_args = json.loads(post_data['url_args'])
                assert isinstance(url_args, dict)
            except:
                return jsonify_with_status("Malformed URL arguments", 400)
    else:
        url_args = {}
    try:
        one_time = bool(int(post_data.get('one_time', 0)))
    except:
        one_time = False
    try:
        expire = int(post_data.get('expire', 3600))
        assert expire > 0
    except:
        return jsonify_with_status("Invalid number of seconds.", 400)
    info = {'i': filename}
    if session_id:
        info['session'] = session_id
    if one_time:
        info['once'] = True
    if len(url_args):
        info['url_args'] = url_args
    while True:
        code = random_string(32)
        the_key = 'da:resume_interview:' + code
        if r.get(the_key) is None:
            break
    pipe = r.pipeline()
    pipe.set(the_key, json.dumps(info))
    pipe.expire(the_key, expire)
    pipe.execute()
    return jsonify(url_for('interview.launch', c=code, _external=True))


@interview_bp.route('/api/clear_cache', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_clear_cache():
    if not api_verify(roles=['admin', 'developer'], permissions=['playground_control']):
        return jsonify_with_status("Access denied.", 403)
    for key in r.keys('da:interviewsource:*'):
        r.incr(key.decode())
    return ('', 204)


@interview_bp.route('/api/interview_data', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_interview_data():
    if not api_verify(roles=['admin', 'developer'], permissions=['interview_data']):
        return jsonify_with_status("Access denied.", 403)
    filename = request.args.get('i', None)
    if filename is None:
        return jsonify_with_status("No filename supplied.", 400)
    try:
        interview_source = interview_source_from_string(filename, testing=True)
    except BaseException as err:
        return jsonify_with_status("Error finding interview: " + str(err), 400)
    try:
        interview = Interview(source=interview_source)
    except BaseException as err:
        return jsonify_with_status("Error finding interview: " + str(err), 400)
    device_id = this_thread.current_info['user']['device_id']
    interview_status = InterviewStatus(current_info=current_info(yaml=filename, req=request, action=None, device_id=device_id))
    m = re.search('docassemble.playground([0-9]+)([^:]*):', filename)
    if m:
        use_playground = bool(current_user.id == int(m.group(1)))
        if m.group(2) != '':
            current_project = m.group(2)
        else:
            current_project = 'default'
    else:
        use_playground = False
        current_project = 'default'
    variables_json, vocab_list, vocab_dict, ac_list = get_vars_in_use(interview, interview_status, debug_mode=False, return_json=True, use_playground=use_playground, current_project=current_project)  # pylint: disable=unused-variable
    return jsonify({'names': variables_json, 'vocabulary': list(vocab_list)})
