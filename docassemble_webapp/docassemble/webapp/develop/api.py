import shutil
import re
import os
import datetime
from io import TextIOWrapper
import tempfile
import time
import zipfile
import tomli
import yaml as standardyaml
from flask import request, jsonify, current_app
from flask_cors import cross_origin
from flask_login import current_user
import werkzeug
from docassemble.base.hooks import fix_ml_files
from docassemble.base.thread_context import this_thread
from docassemble.webapp.api.helpers import api_verify
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import csrf
from docassemble.webapp.files.savedfile import SavedFile, make_package_zip
from docassemble.webapp.main.hooks import get_default_timezone
from docassemble.webapp.main.helpers import restart_all
from docassemble.webapp.playground import PlaygroundSection
from docassemble.webapp.utils.filenames import secure_filename_spaces_ok, directory_for
from docassemble.webapp.users.helpers import get_user_object
from docassemble.webapp.utils.helpers import (
    custom_send_file,
    jsonify_restart_task,
    get_master_branch,
    jsonify_with_status,
    true_or_false,
    name_of_user,
)
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.utils.path import splitall
from .common import project_name
from .views import (
    delete_project,
    create_project,
    do_playground_pull,
    develop_bp,
    get_list_of_projects,
)

@develop_bp.route('/api/playground_pull', methods=['GET', 'POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_playground_pull():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if not api_verify(roles=['admin', 'developer'], permissions=['playground_control']):
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    do_restart = true_or_false(post_data.get('restart', True))
    current_project = post_data.get('project', 'default')
    try:
        if current_app.config['ENABLE_SHARING_PLAYGROUNDS'] or current_user.has_role_or_permission('admin', permissions=['playground_control']):
            user_id = int(post_data.get('user_id', current_user.id))
        else:
            if 'user_id' in post_data:
                assert int(post_data['user_id']) == current_user.id
            user_id = current_user.id
    except:
        return jsonify_with_status("Invalid user_id.", 400)
    if current_project != 'default' and current_project not in get_list_of_projects(user_id):
        return jsonify_with_status("Invalid project.", 400)
    this_thread.current_info['user'] = {'is_anonymous': False, 'theid': user_id}
    if current_app.config['USE_GITHUB']:
        github_auth = r.get('da:using_github:userid:' + str(current_user.id))
        can_publish_to_github = bool(github_auth is not None)
    else:
        can_publish_to_github = None
    github_url = None
    branch = None
    pypi_package = None
    if 'github_url' in post_data:
        github_url = post_data['github_url'].rstrip('/')
        branch = post_data.get('branch', None)
        if branch is None:
            branch = get_master_branch(github_url)
        m = re.search(r'#egg=(.*)', github_url)
        if m:
            packagename = re.sub(r'&.*', '', m.group(1))
            github_url = re.sub(r'#.*', '', github_url)
        else:
            packagename = re.sub(r'/*$', '', github_url)
            packagename = re.sub(r'^git+', '', packagename)
            packagename = re.sub(r'#.*', '', packagename)
            packagename = re.sub(r'\.git$', '', packagename)
            packagename = re.sub(r'.*/', '', packagename)
            packagename = re.sub(r'^docassemble-', 'docassemble.', packagename)
    elif 'pip' in post_data:
        m = re.match(r'([^>=<]+)([>=<]+.+)', post_data['pip'])
        if m:
            pypi_package = m.group(1)
            # limitation = m.group(2)
        else:
            pypi_package = post_data['pip']
            # limitation = None
        packagename = re.sub(r'[^A-Za-z0-9\_\-\.]', '', pypi_package)
    else:
        return jsonify_with_status("Either github_url or pip is required.", 400)
    area = {}
    # area_sec = {'templates': 'playgroundtemplate', 'static': 'playgroundstatic', 'sources': 'playgroundsources', 'questions': 'playground'}
    for sec in ('playground', 'playgroundpackages', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules'):
        area[sec] = SavedFile(user_id, fix=True, section=sec)
    result = do_playground_pull(area, current_project, github_url=github_url, branch=branch, pypi_package=pypi_package, can_publish_to_github=can_publish_to_github, github_email=current_user.email)
    if result['action'] in ('error', 'fail'):
        return jsonify_with_status("Pull process encountered an error: " + result['message'], 400)
    if result['action'] == 'finished':
        if result['need_to_restart'] and do_restart:
            return_val = jsonify_restart_task()
            restart_all()
            return return_val
    return ('', 204)


@develop_bp.route('/api/playground_install', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_playground_install():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if not api_verify(roles=['admin', 'developer'], permissions=['playground_control']):
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    do_restart = true_or_false(post_data.get('restart', True))
    current_project = post_data.get('project', 'default')
    try:
        if current_app.config['ENABLE_SHARING_PLAYGROUNDS'] or current_user.has_role_or_permission('admin', permissions=['playground_control']):
            user_id = int(post_data.get('user_id', current_user.id))
        else:
            if 'user_id' in post_data:
                assert int(post_data['user_id']) == current_user.id
            user_id = current_user.id
    except:
        return jsonify_with_status("Invalid user_id.", 400)
    if current_project != 'default' and current_project not in get_list_of_projects(user_id):
        return jsonify_with_status("Invalid project.", 400)
    this_thread.current_info['user'] = {'is_anonymous': False, 'theid': user_id}
    found = False
    expected_name = 'unknown'
    need_to_restart = False
    area = {}
    area_sec = {'templates': 'playgroundtemplate', 'static': 'playgroundstatic', 'sources': 'playgroundsources', 'questions': 'playground'}
    for sec in ('playground', 'playgroundpackages', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules'):
        area[sec] = SavedFile(user_id, fix=True, section=sec)
    try:
        for filekey in request.files:
            the_files = request.files.getlist(filekey)
            if not the_files:
                continue
            for up_file in the_files:
                found = True
                zippath = tempfile.NamedTemporaryFile(mode="wb", prefix='datemp', suffix=".zip", delete=False)
                up_file.save(zippath)
                up_file.close()
                zippath.close()
                with zipfile.ZipFile(zippath.name, mode='r') as zf:
                    readme_text = ''
                    gitignore_text = ''
                    setup_py = ''
                    pyproject_toml = ''
                    extracted = {}
                    data_files = {'templates': [], 'static': [], 'sources': [], 'interviews': [], 'modules': [], 'questions': []}
                    has_docassemble_dir = set()
                    has_setup_file = set()
                    for zinfo in zf.infolist():
                        if zinfo.is_dir():
                            if zinfo.filename.endswith('/docassemble/'):
                                has_docassemble_dir.add(re.sub(r'/docassemble/$', '', zinfo.filename))
                            if zinfo.filename == 'docassemble/':
                                has_docassemble_dir.add('')
                        elif zinfo.filename.endswith('/setup.py') or zinfo.filename.endswith('/pyproject.toml') or zinfo.filename.endswith('/setup.cfg'):
                            (directory, filename) = os.path.split(zinfo.filename)
                            has_setup_file.add(directory)
                        elif zinfo.filename in ('setup.py', 'pyproject.toml', 'setup.cfg'):
                            has_setup_file.add('')
                    root_dir = None
                    for directory in has_docassemble_dir.union(has_setup_file):
                        if root_dir is None or len(directory) < len(root_dir):
                            root_dir = directory
                    if root_dir is None:
                        return jsonify_with_status("Not a docassemble package.", 400)
                    for zinfo in zf.infolist():
                        if zinfo.filename.endswith('/'):
                            continue
                        (directory, filename) = os.path.split(zinfo.filename)
                        if filename.startswith('#') or filename.endswith('~'):
                            continue
                        dirparts = splitall(directory)
                        if '.git' in dirparts:
                            continue
                        levels = re.findall(r'/', directory)
                        time_tuple = zinfo.date_time
                        the_time = time.mktime(datetime.datetime(*time_tuple).timetuple())
                        for sec in ('templates', 'static', 'sources', 'questions'):
                            if directory.endswith('data/' + sec) and filename != 'README.md':
                                data_files[sec].append(filename)
                                target_filename = os.path.join(directory_for(area[area_sec[sec]], current_project), filename)
                                with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                    shutil.copyfileobj(source_fp, target_fp)
                                os.utime(target_filename, (the_time, the_time))
                        if filename == 'README.md' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                readme_text = the_file_obj.read()
                        if filename == '.gitignore' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                gitignore_text = the_file_obj.read()
                        if filename == 'setup.py' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                setup_py = the_file_obj.read()
                        if filename == 'pyproject.toml' and directory == root_dir:
                            with zf.open(zinfo) as f:
                                the_file_obj = TextIOWrapper(f, encoding='utf8')
                                pyproject_toml = the_file_obj.read()
                        elif len(levels) >= 1 and directory != root_dir and filename.endswith('.py') and filename != '__init__.py' and 'tests' not in dirparts and 'data' not in dirparts:
                            need_to_restart = True
                            data_files['modules'].append(filename)
                            target_filename = os.path.join(directory_for(area['playgroundmodules'], current_project), filename)
                            with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                shutil.copyfileobj(source_fp, target_fp)
                                os.utime(target_filename, (the_time, the_time))
                    if setup_py:
                        setup_py = re.sub(r'.*setup\(', '', setup_py, flags=re.DOTALL)
                        for line in setup_py.splitlines():
                            m = re.search(r"^ *([a-z_]+) *= *\(?'(.*)'", line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\(?"(.*)"', line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
                            if m:
                                the_list = []
                                for item in re.split(r', *', m.group(2)):
                                    inner_item = re.sub(r"'$", '', item)
                                    inner_item = re.sub(r"^'", '', inner_item)
                                    inner_item = re.sub(r'"+$', '', inner_item)
                                    inner_item = re.sub(r'^"+', '', inner_item)
                                    the_list.append(inner_item)
                                extracted[m.group(1)] = the_list
                    if pyproject_toml:
                        data = tomli.loads(pyproject_toml)
                        if 'project' in data and isinstance(data['project'], dict):
                            extracted['description'] = data['project'].get('description', '')
                            extracted['name'] = data['project'].get('name', '')
                            extracted['version'] = data['project'].get('version', '')
                            extracted['license'] = data['project'].get('license', '')
                            if 'authors' in data['project'] and isinstance(data['project']['authors'], list) and len(data['project']['authors']) > 0 and isinstance(data['project']['authors'][0], dict):
                                extracted['author'] = data['project']['authors'][0].get('name', '')
                                extracted['author_email'] = data['project']['authors'][0].get('email', '')
                            if 'dependencies' in data['project'] and isinstance(data['project']['dependencies'], list):
                                extracted['install_requires'] = data['project']['dependencies']
                            if 'urls' in data['project'] and isinstance(data['project']['urls'], dict):
                                extracted['url'] = data['project']['urls'].get('Homepage', '')
                    info_dict = {'readme': readme_text, 'gitignore': gitignore_text, 'interview_files': data_files['questions'], 'sources_files': data_files['sources'], 'static_files': data_files['static'], 'module_files': data_files['modules'], 'template_files': data_files['templates'], 'dependencies': list(map(lambda y: re.sub(r'[\>\<\=].*', '', y), extracted.get('install_requires', []))), 'description': extracted.get('description', ''), 'author_name': extracted.get('author', ''), 'author_email': extracted.get('author_email', ''), 'license': extracted.get('license', ''), 'url': extracted.get('url', ''), 'version': extracted.get('version', '')}

                    info_dict['dependencies'] = [x.strip() for x in map(lambda y: re.sub(r'[\>\<\=@].*', '', y), info_dict['dependencies']) if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp')]
                    package_name = re.sub(r'^docassemble\.', '', extracted.get('name', expected_name))
                    with open(os.path.join(directory_for(area['playgroundpackages'], current_project), 'docassemble.' + package_name), 'w', encoding='utf-8') as fp:
                        the_yaml = standardyaml.safe_dump(info_dict, default_flow_style=False, default_style='|')
                        fp.write(str(the_yaml))
                    for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + project_name(current_project) + ':*'):  # pylint: disable=consider-using-dict-items
                        r.incr(key.decode())
                    for the_area in area.values():
                        the_area.finalize()
                    # the_file = package_name
                zippath.close()
    except BaseException as err:
        logmessage("api_playground_install: " + err.__class__.__name__ + ": " + str(err))
        return jsonify_with_status("Error installing packages.", 400)
    if not found:
        return jsonify_with_status("No package found.", 400)
    for key in r.keys('da:interviewsource:docassemble.playground' + str(user_id) + project_name(current_project) + ':*'):
        r.incr(key.decode())
    if do_restart and need_to_restart:
        return_val = jsonify_restart_task()
        restart_all()
        return return_val
    return ('', 204)


@develop_bp.route('/api/playground/project', methods=['GET', 'POST', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'DELETE', 'HEAD'], automatic_options=True)
def api_playground_projects():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if not api_verify(roles=['admin', 'developer'], permissions=['playground_control']):
        return jsonify_with_status("Access denied.", 403)
    user_id = -1
    if request.method in ('GET', 'DELETE'):
        try:
            if current_app.config['ENABLE_SHARING_PLAYGROUNDS'] or current_user.has_role_or_permission('admin', permissions=['playground_control']):
                user_id = int(request.args.get('user_id', current_user.id))
            else:
                if 'user_id' in request.args:
                    assert int(request.args['user_id']) == current_user.id
                user_id = current_user.id
        except:
            return jsonify_with_status("Invalid user_id.", 400)
    if request.method == 'GET':
        return jsonify(get_list_of_projects(user_id))
    if request.method == 'DELETE':
        if 'project' not in request.args:
            return jsonify_with_status("Project not provided.", 400)
        project = request.args['project']
        if project not in get_list_of_projects(user_id) or project == 'default':
            return jsonify_with_status("Invalid project.", 400)
        delete_project(user_id, project)
        return ('', 204)
    if request.method == 'POST':
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        try:
            if current_app.config['ENABLE_SHARING_PLAYGROUNDS'] or current_user.has_role_or_permission('admin', permissions=['playground_control']):
                user_id = int(post_data.get('user_id', current_user.id))
            else:
                if 'user_id' in post_data:
                    assert int(post_data['user_id']) == current_user.id
                user_id = current_user.id
        except:
            return jsonify_with_status("Invalid user_id.", 400)
        if 'project' not in post_data:
            return jsonify_with_status("Project not provided.", 400)
        project = post_data['project']
        if re.search('^[0-9]', project) or re.search('[^A-Za-z0-9]', project):
            return jsonify_with_status("Invalid project name.", 400)
        if project in get_list_of_projects(user_id) or project == 'default':
            return jsonify_with_status("Invalid project.", 400)
        create_project(user_id, project)
        return ('', 204)
    return ('File not found', 404)


@develop_bp.route('/api/playground', methods=['GET', 'POST', 'DELETE'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'DELETE', 'HEAD'], automatic_options=True)
def api_playground():
    if not current_app.config['ENABLE_PLAYGROUND']:
        return ('File not found', 404)
    if not api_verify(roles=['admin', 'developer'], permissions=['playground_control']):
        return jsonify_with_status("Access denied.", 403)
    folder = ''
    project = ''
    user_id = -1
    if request.method in ('GET', 'DELETE'):
        folder = request.args.get('folder', 'static')
        project = request.args.get('project', 'default')
        try:
            if current_app.config['ENABLE_SHARING_PLAYGROUNDS'] or current_user.has_role_or_permission('admin', permissions=['playground_control']):
                user_id = int(request.args.get('user_id', current_user.id))
            else:
                if 'user_id' in request.args:
                    assert int(request.args['user_id']) == current_user.id
                user_id = current_user.id
        except:
            return jsonify_with_status("Invalid user_id.", 400)
    elif request.method == 'POST':
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        folder = post_data.get('folder', 'static')
        project = post_data.get('project', 'default')
        do_restart = true_or_false(post_data.get('restart', True))
        try:
            if current_app.config['ENABLE_SHARING_PLAYGROUNDS'] or current_user.has_role_or_permission('admin', permissions=['playground_control']):
                user_id = int(post_data.get('user_id', current_user.id))
            else:
                if 'user_id' in post_data:
                    assert int(post_data['user_id']) == current_user.id
                user_id = current_user.id
        except:
            return jsonify_with_status("Invalid user_id.", 400)
    if request.method == 'DELETE':
        do_restart = true_or_false(request.args.get('restart', True))
        if 'filename' not in request.args:
            return jsonify_with_status("Missing filename.", 400)
    if folder not in ('questions', 'sources', 'static', 'templates', 'modules', 'packages'):
        return jsonify_with_status("Invalid folder.", 400)
    if project != 'default' and project not in get_list_of_projects(user_id):
        return jsonify_with_status("Invalid project.", 400)
    if folder == 'questions':
        section = ''
    elif folder == 'templates':
        section = 'template'
    else:
        section = folder
    this_thread.current_info['user'] = {'is_anonymous': False, 'theid': user_id}
    if folder == 'packages':
        if request.method != 'GET' or not current_app.config['ENABLE_PLAYGROUND']:
            return ('File not found', 404)
        the_directory = directory_for(SavedFile(user_id, fix=True, section='playgroundpackages'), project)
        if not os.path.isdir(the_directory):
            return ('File not found', 404)
        the_filename = request.args.get('filename', request.args.get('package', None))
        if the_filename is None:
            return jsonify(sorted([f for f in os.listdir(the_directory) if f.startswith('docassemble') and os.path.isfile(os.path.join(the_directory, f))]))
        the_package = re.sub(r'^docassemble\.', '', secure_filename_spaces_ok(the_filename))
        filename = os.path.join(the_directory, 'docassemble.' + the_package)
        if not os.path.isfile(filename):
            return ('File not found', 404)
        playground_user = get_user_object(user_id)
        info = {}
        with open(filename, 'r', encoding='utf-8') as fp:
            content = fp.read()
            info = standardyaml.load(content, Loader=standardyaml.FullLoader)
        for field in ('dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files'):
            if field not in info:
                info[field] = []
        info['dependencies'] = list(x for x in map(lambda y: re.sub(r'[\>\<\=].*', '', y), info['dependencies']) if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp'))
        info['modtime'] = os.path.getmtime(filename)
        author_info = {}
        author_info['author name and email'] = name_of_user(playground_user, include_email=True)
        author_info['author name'] = name_of_user(playground_user)
        author_info['author email'] = playground_user.email
        author_info['first name'] = playground_user.first_name
        author_info['last name'] = playground_user.last_name
        author_info['id'] = playground_user.id
        nice_name = 'docassemble-' + str(the_package) + '.zip'
        if playground_user.timezone:
            the_timezone = playground_user.timezone
        else:
            the_timezone = get_default_timezone()
        fix_ml_files(author_info['id'], project)
        zip_file = make_package_zip(the_package, info, author_info, the_timezone, current_project=project)
        response = custom_send_file(zip_file.name, mimetype='application/zip', as_attachment=True, download_name=nice_name)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    pg_section = PlaygroundSection(section=section, project=project)
    if request.method == 'GET':
        if 'filename' not in request.args:
            return jsonify(pg_section.file_list)
        the_filename = secure_filename_spaces_ok(request.args['filename'])
        if not pg_section.file_exists(the_filename):
            return jsonify_with_status("File not found", 404)
        response_to_send = custom_send_file(pg_section.get_file(the_filename), mimetype=pg_section.get_mimetype(the_filename))
        response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response_to_send
    if request.method == 'DELETE':
        pg_section.delete_file(secure_filename_spaces_ok(request.args['filename']))
        if section == 'modules' and do_restart:
            return_val = jsonify_restart_task()
            restart_all()
            return return_val
        return ('', 204)
    if request.method == 'POST':
        found = False
        try:
            for filekey in request.files:
                the_files = request.files.getlist(filekey)
                if the_files:
                    for the_file in the_files:
                        filename = werkzeug.utils.secure_filename(the_file.filename)
                        temp_file = tempfile.NamedTemporaryFile(prefix="datemp", delete=False)
                        the_file.save(temp_file.name)
                        pg_section.copy_from(temp_file.name, filename=filename)
                        found = True
        except:
            return jsonify_with_status("Error saving file(s).", 400)
        if not found:
            return jsonify_with_status("No file found.", 400)
        for key in r.keys('da:interviewsource:docassemble.playground' + str(user_id) + project_name(project) + ':*'):
            r.incr(key.decode())
        if section == 'modules' and do_restart:
            return_val = jsonify_restart_task()
            restart_all()
            return return_val
        return ('', 204)
    return ('', 204)
