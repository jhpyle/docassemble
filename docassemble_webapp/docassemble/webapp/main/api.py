import json
import tempfile
from flask import current_app, request, jsonify, make_response
from flask_cors import cross_origin
import werkzeug
import yaml as standardyaml
from docassemble.base.functions import temp_redirect, safe_json, altyamlstring
from docassemble.base.pandoc import (
    convertible_extensions,
    word_to_markdown,
    convertible_mimetypes,
)
from docassemble.webapp.api.helpers import api_verify
from docassemble.webapp.cloud.utils import cloud
from docassemble.webapp.config import daconfig, START_TIME
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import csrf
from docassemble.webapp.main.helpers import restart_all
from docassemble.webapp.utils.filenames import get_ext_and_mimetype
from docassemble.webapp.utils.helpers import (
    jsonify_restart_task,
    transform_json_variables,
    jsonify_with_status,
    reset_process_running,
    true_or_false,
    CAN_CONVERT_WORD,
)
from .helpers import stash_data, retrieve_stashed_data
from .blueprint import main_bp

@main_bp.route('/api/temp_url', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_temporary_redirect():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    url = request.args.get('url', None)
    if url is None:
        return jsonify_with_status("No url supplied.", 400)
    try:
        one_time = true_or_false(request.args.get('one_time', 0))
    except:
        one_time = False
    try:
        expire = int(request.args.get('expire', 3600))
        assert expire > 0
    except:
        return jsonify_with_status("Invalid number of seconds.", 400)
    return jsonify(temp_redirect(url, expire, False, one_time))


@main_bp.route('/api/config', methods=['GET', 'POST', 'PATCH'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'PATCH', 'HEAD'], automatic_options=True)
def api_config():
    if not current_app.config['ALLOW_CONFIGURATION_EDITING']:
        return ('File not found', 404)
    if not api_verify(roles=['admin'], permissions=['manage_config']):
        return jsonify_with_status("Access denied.", 403)
    if request.method == 'GET':
        try:
            with open(daconfig['config file'], 'r', encoding='utf-8') as fp:
                content = fp.read()
            data = standardyaml.load(content, Loader=standardyaml.FullLoader)
        except:
            return jsonify_with_status("Could not parse Configuration.", 400)
        return jsonify(data)
    if request.method == 'POST':
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        if 'config' not in post_data:
            return jsonify_with_status("Configuration not supplied.", 400)
        if isinstance(post_data['config'], dict):
            data = post_data['config']
        else:
            try:
                data = json.loads(post_data['config'])
            except:
                return jsonify_with_status("Configuration was not valid JSON.", 400)
        yaml_data = altyamlstring.dump_to_string(data)
        if cloud is not None:
            key = cloud.get_key('config.yml')
            key.set_contents_from_string(yaml_data)
        with open(daconfig['config file'], 'w', encoding='utf-8') as fp:
            fp.write(yaml_data)
        return_val = jsonify_restart_task()
        restart_all()
        return return_val
    if request.method == 'PATCH':
        try:
            with open(daconfig['config file'], 'r', encoding='utf-8') as fp:
                content = fp.read()
            data = standardyaml.load(content, Loader=standardyaml.FullLoader)
        except:
            return jsonify_with_status("Could not parse Configuration.", 400)
        patch_data = request.get_json(silent=True)
        if patch_data is None:
            # using_json = False
            patch_data = request.form.copy()
        # else:
        #     using_json = True
        if 'config_changes' not in patch_data:
            return jsonify_with_status("Configuration changes not supplied.", 400)
        if isinstance(patch_data['config_changes'], dict):
            new_data = patch_data['config_changes']
        else:
            try:
                new_data = json.loads(patch_data['config_changes'])
            except:
                return jsonify_with_status("Configuration changes were not valid JSON.", 400)
        data.update(new_data)
        yaml_data = altyamlstring.dump_to_string(data)
        if cloud is not None:
            key = cloud.get_key('config.yml')
            key.set_contents_from_string(yaml_data)
        with open(daconfig['config file'], 'w', encoding='utf-8') as fp:
            fp.write(yaml_data)
        return_val = jsonify_restart_task()
        restart_all()
        return return_val
    return ('File not found', 404)


@main_bp.route('/api/restart', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_restart():
    if not current_app.config['ALLOW_RESTARTING']:
        return ('File not found', 404)
    if not api_verify(roles=['admin', 'developer'], permissions=['playground_control']):
        return jsonify_with_status("Access denied.", 403)
    return_val = jsonify_restart_task()
    restart_all()
    return return_val


@main_bp.route('/api/restart_status', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_restart_status():
    if not current_app.config['ALLOW_RESTARTING']:
        return ('File not found', 404)
    if not api_verify(roles=['admin', 'developer'], permissions=['playground_control']):
        return jsonify_with_status("Access denied.", 403)
    code = request.args.get('task_id', None)
    if code is None:
        return jsonify_with_status("Missing task_id", 400)
    the_key = 'da:restart_status:' + str(code)
    task_data = r.get(the_key)
    if task_data is None:
        return jsonify(status='unknown')
    task_info = json.loads(task_data.decode())
    if START_TIME <= task_info['server_start_time'] or reset_process_running():
        return jsonify(status='working')
    r.expire(the_key, 30)
    return jsonify(status='completed')


@main_bp.route('/api/convert_file', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_convert_file():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    post_data = request.form.copy()
    to_format = post_data.get('format', 'md')
    if to_format not in 'md':
        return jsonify_with_status("Invalid output file format.", 400)
    for filekey in request.files:
        the_files = request.files.getlist(filekey)
        if the_files:
            for the_file in the_files:
                filename = werkzeug.utils.secure_filename(the_file.filename)
                extension, mimetype = get_ext_and_mimetype(filename)
                if mimetype and mimetype in convertible_mimetypes:
                    the_format = convertible_mimetypes[mimetype]
                elif extension and extension in convertible_extensions:
                    the_format = convertible_extensions[extension]
                else:
                    return jsonify_with_status("Invalid input file format.", 400)
                with tempfile.NamedTemporaryFile() as temp_file:
                    the_file.save(temp_file.name)
                    if CAN_CONVERT_WORD:
                        result = word_to_markdown(temp_file.name, the_format)
                    else:
                        result = None
                    if result is None:
                        return jsonify_with_status("Unable to convert file.", 400)
                    with open(result.name, 'r', encoding='utf-8') as fp:
                        contents = fp.read()
                response = make_response(contents, 200)
                response.headers['Content-Type'] = 'text/plain'
                return response
    return ('File not found', 404)




@main_bp.route('/api/stash_data', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_stash_data():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
        if 'data' not in post_data:
            return jsonify_with_status("Data must be provided.", 400)
        try:
            data = json.loads(post_data['data'])
        except:
            return jsonify_with_status("Malformed data.", 400)
    else:
        data = post_data['data']
    if not true_or_false(post_data.get('raw', False)):
        data = transform_json_variables(data)
    expire = post_data.get('expire', None)
    if expire is None:
        expire = 60*60*24*90
    try:
        expire = int(expire)
        assert expire > 0
    except:
        expire = 60*60*24*90
    (key, secret) = stash_data(data, expire)
    return jsonify({'stash_key': key, 'secret': secret})


@main_bp.route('/api/retrieve_stashed_data', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_retrieve_stashed_data():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    do_delete = true_or_false(request.args.get('delete', False))
    refresh = request.args.get('refresh', None)
    if refresh:
        try:
            refresh = int(refresh)
            assert refresh > 0
        except:
            refresh = False
    stash_key = request.args.get('stash_key', None)
    secret = request.args.get('secret', None)
    if stash_key is None or secret is None:
        return jsonify_with_status("The stash key and secret parameters are required.", 400)
    try:
        data = retrieve_stashed_data(stash_key, secret, do_delete, refresh)
        assert data is not None
    except BaseException as err:
        return jsonify_with_status("The stashed data could not be retrieved: " + err.__class__.__name__ + " " + str(err) + ".", 400)
    return jsonify(safe_json(data))
