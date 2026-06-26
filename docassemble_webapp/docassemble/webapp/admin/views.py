import re
import sys
import shutil
import werkzeug
import humanize
from markupsafe import Markup
import yaml as standardyaml
import ruamel.yaml
from flask import (
    redirect,
    jsonify,
    make_response,
    session,
    render_template_string,
    render_template,
    flash,
    current_app,
    Blueprint,
    request,
)
from flask_login import current_user
from docassemble_flask_user import login_required, roles_required
from docassemble.base.error import DAError, DAException
from docassemble.base.functions import package_template_filename
from docassemble.base.generate_key import random_string
from docassemble.base.language.control import set_language
from docassemble.base.language.words import word
from docassemble.base.thread_context import this_thread
from docassemble.webapp.cloud.utils import cloud
from docassemble.webapp.config import (
    daconfig,
    errors as config_errors,
    env_messages,
    da_version,
    final_default_yaml_filename,
    keymap,
    DEFER,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.interview.helpers import user_interviews, valid_date_key
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.users.helpers import needs_to_change_password
from docassemble.webapp.utils.helpers import (
    get_url_from_file_reference,
    page_after_login,
    as_int,
    redis_script,
    from_safeid,
    current_info,
    safeid,
    version_warning,
)
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from .forms import ConfigForm, InterviewsListForm
from .funcs import interview_menu

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='templates'
)

@admin_bp.route('/config', methods=['GET', 'POST'])
@login_required
@roles_required(['admin'])
def config_page():
    setup_translation()
    if not current_app.config['ALLOW_CONFIGURATION_EDITING']:
        return ('File not found', 404)
    form = ConfigForm(request.form)
    content = None
    ok = True
    if request.method == 'POST':
        if form.submit.data and form.config_content.data:
            try:
                standardyaml.load(form.config_content.data, Loader=standardyaml.FullLoader)
                yml = ruamel.yaml.YAML()
                yml.allow_duplicate_keys = False
                yml.load(form.config_content.data)
            except BaseException as err_mess:
                ok = False
                content = form.config_content.data
                err_mess = word("Configuration not updated.  There was a syntax error in the configuration YAML.") + '<pre>' + str(err_mess) + '</pre>'
                flash(str(err_mess), 'error')
                logmessage('config_page: ' + str(err_mess))
            if ok:
                if cloud is not None:
                    key = cloud.get_key('config.yml')
                    key.set_contents_from_string(form.config_content.data)
                with open(daconfig['config file'], 'w', encoding='utf-8') as fp:
                    fp.write(form.config_content.data)
                    flash(word('The configuration file was saved.'), 'success')
                # session['restart'] = 1
                pipe = r.pipeline()
                pipe.set('da:skip_create_tables', 1)
                pipe.expire('da:skip_create_tables', 10)
                pipe.execute()
                return redirect(url_for('main.restart_page'))
        elif form.cancel.data:
            flash(word('Configuration not updated.'), 'info')
            return redirect(url_for('admin.interview_list'))
        else:
            flash(word('Configuration not updated.  There was an error.'), 'error')
            return redirect(url_for('admin.interview_list'))
    if ok:
        with open(daconfig['config file'], 'r', encoding='utf-8') as fp:
            content = fp.read()
    if content is None:
        return ('File not found', 404)
    (disk_total, disk_used, disk_free) = shutil.disk_usage(daconfig['config file'])  # pylint: disable=unused-variable
    python_version = daconfig.get('python version', word('Unknown'))
    system_version = daconfig.get('system version', word('Unknown'))
    if python_version == system_version:
        version = word("Version") + " " + str(python_version)
    else:
        version = word("Version") + " " + str(python_version) + ' (Python); ' + str(system_version) + ' (' + word('system') + ')'
    initial_values = {
        "daContent": content,
        "daKeymap": keymap
    }
    extra_js = f"""
    <script{DEFER} src="{url_for('static', filename="app/cm6.min.js", v=da_version)}"></script>
    <script{DEFER} src="{url_for('static', filename="app/config.min.js", v=da_version)}"></script>
    {redis_script(initial_values)}"""
    response = make_response(render_template('admin/config.html', underlying_python_version=re.sub(r' \(.*', '', sys.version, flags=re.DOTALL), free_disk_space=humanize.naturalsize(disk_free), config_errors=config_errors, config_messages=env_messages, version_warning=version_warning, version=version, bodyclass='daadminbody', tab_title=word('Configuration'), page_title=word('Configuration'), extra_js=Markup(extra_js), form=form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@admin_bp.route('/list', methods=['GET'])
def interview_start():
    if current_user.is_anonymous and not daconfig.get('allow anonymous access', True):
        return redirect(url_for('user.login', next=url_for('admin.interview_start', **request.args)))
    if not current_user.is_anonymous and not current_user.is_authenticated:
        response = redirect(url_for('admin.interview_start'))
        response.set_cookie('remember_token', '', expires=0)
        response.set_cookie('visitor_secret', '', expires=0)
        response.set_cookie('secret', '', expires=0)
        response.set_cookie('session', '', expires=0)
        return response
    setup_translation()
    if len(daconfig['dispatch']) == 0:
        return redirect(url_for('interview.index', i=final_default_yaml_filename))
    is_json = bool(('json' in request.form and as_int(request.form['json'])) or ('json' in request.args and as_int(request.args['json'])))
    tag = request.args.get('tag', None)
    if daconfig.get('dispatch interview', None) is not None:
        if is_json:
            if tag:
                return redirect(url_for('interview.index', i=daconfig.get('dispatch interview'), from_list='1', json='1', tag=tag))
            return redirect(url_for('interview.index', i=daconfig.get('dispatch interview'), from_list='1', json='1'))
        if tag:
            return redirect(url_for('interview.index', i=daconfig.get('dispatch interview'), from_list='1', tag=tag))
        return redirect(url_for('interview.index', i=daconfig.get('dispatch interview'), from_list='1'))
    if 'embedded' in request.args and int(request.args['embedded']):
        the_page = 'admin/start-embedded.html'
        embed = True
    else:
        embed = False
    interview_info = interview_menu(absolute_urls=embed, start_new=False, tag=tag)
    if is_json:
        return jsonify(action='menu', interviews=interview_info)
    argu = {'version_warning': None, 'interview_info': interview_info}
    if embed:
        the_page = 'admin/start-embedded.html'
    else:
        if 'start page template' in daconfig and daconfig['start page template']:
            the_page = package_template_filename(daconfig['start page template'])
            if the_page is None:
                raise DAError("Could not find start page template " + daconfig['start page template'])
            with open(the_page, 'r', encoding='utf-8') as fp:
                template_string = fp.read()
                return render_template_string(template_string, **argu)
        else:
            the_page = 'admin/start.html'
    resp = make_response(render_template(the_page, **argu))
    if embed:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@admin_bp.route('/interviews', methods=['GET', 'POST'])
@login_required
def interview_list():
    setup_translation()
    form = InterviewsListForm(request.form)
    is_json = bool(('json' in request.form and as_int(request.form['json'])) or ('json' in request.args and as_int(request.args['json'])))
    if 'lang' in request.form:
        session['language'] = request.form['lang']
        set_language(session['language'])
    tag = request.args.get('tag', None)
    if request.method == 'POST':
        tag = form.tags.data
    if tag is not None:
        tag = werkzeug.utils.secure_filename(tag)
    if 'newsecret' in session:
        # logmessage("interview_list: fixing cookie")
        the_args = {}
        if is_json:
            the_args['json'] = '1'
        if tag:
            the_args['tag'] = tag
        if 'from_login' in request.args:
            the_args['from_login'] = request.args['from_login']
        if 'post_restart' in request.args:
            the_args['post_restart'] = request.args['post_restart']
        if 'resume' in request.args:
            the_args['resume'] = request.args['resume']
        response = redirect(url_for('admin.interview_list', **the_args))
        response.set_cookie('secret', session['newsecret'], httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'])
        del session['newsecret']
        return response
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('admin.interview_list')))
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    # logmessage("interview_list: secret is " + repr(secret))
    if request.method == 'POST':
        if form.delete_all.data:
            num_deleted = user_interviews(user_id=current_user.id, secret=secret, action='delete_all', tag=tag)
            if num_deleted > 0:
                flash(word("Deleted interviews"), 'success')
            if is_json:
                return redirect(url_for('admin.interview_list', json='1'))
            return redirect(url_for('admin.interview_list'))
        if form.delete.data:
            yaml_file = form.i.data
            session_id = form.session.data
            if yaml_file is not None and session_id is not None:
                user_interviews(user_id=current_user.id, secret=secret, action='delete', session=session_id, filename=yaml_file)
                flash(word("Deleted interview"), 'success')
            if is_json:
                return redirect(url_for('admin.interview_list', json='1'))
            return redirect(url_for('admin.interview_list'))
    # if daconfig.get('resume interview after login', False) and 'i' in session and 'uid' in session and (request.args.get('from_login', False) or (re.search(r'user/(register|sign-in)', str(request.referrer)) and 'next=' not in str(request.referrer))):
    #     if is_json:
    #         return redirect(url_for('index', i=session['i'], json='1'))
    #     else:
    #         return redirect(url_for('index', i=session['i']))
    if request.args.get('from_login', False) or (re.search(r'user/(register|sign-in)', str(request.referrer)) and 'next=' not in str(request.referrer)):
        # If this condition is true, then the user is being directed to this endpoint for purposes of being redirected elsewhere.
        # They should go either to the URL in the `next` param, or to the `page after login` of their role.
        # However, if the `next` param or the `page after login` is this endpoint, we should not redirect.
        next_page = request.args.get('next', '')
        if bool(next_page):
            next_page = current_app.user_manager.make_safe_url_function(next_page)
            if not next_page.startswith(url_for('admin.interview_list')):
                return redirect(next_page)
        else:
            the_after_login_page = page_after_login()
            if the_after_login_page is not None and the_after_login_page not in ('interview_list', 'interviews'):
                return redirect(get_url_from_file_reference(the_after_login_page, {}))
    if daconfig.get('session list interview', None) is not None:
        if is_json:
            return redirect(url_for('interview.index', i=daconfig.get('session list interview'), from_list='1', json='1'))
        return redirect(url_for('interview.index', i=daconfig.get('session list interview'), from_list='1'))
    exclude_invalid = not current_user.has_role('admin', 'developer')
    resume_interview = request.args.get('resume', None)
    if resume_interview is None and daconfig.get('auto resume interview', None) is not None and (request.args.get('from_login', False) or (re.search(r'user/(register|sign-in)', str(request.referrer)) and 'next=' not in str(request.referrer))):
        resume_interview = daconfig['auto resume interview']
    device_id = request.cookies.get('ds', None)
    if device_id is None:
        device_id = random_string(16)
    the_current_info = current_info(yaml=None, req=request, interface='web', session_info=None, secret=secret, device_id=device_id)
    this_thread.current_info = the_current_info
    if resume_interview is not None:
        (interviews, start_id) = user_interviews(user_id=current_user.id, secret=secret, exclude_invalid=True, filename=resume_interview, include_dict=True)
        if len(interviews) > 0:
            return redirect(url_for('interview.index', i=interviews[0]['filename'], session=interviews[0]['session'], from_list='1'))
        return redirect(url_for('interview.index', i=resume_interview, from_list='1'))
    next_id_code = request.args.get('next_id', None)
    if next_id_code:
        try:
            start_id = int(from_safeid(next_id_code))
            assert start_id >= 0
            show_back = True
        except:
            start_id = None
            show_back = False
    else:
        start_id = None
        show_back = False
    result = user_interviews(user_id=current_user.id, secret=secret, exclude_invalid=exclude_invalid, tag=tag, start_id=start_id)
    if result is None:
        raise DAException("interview_list: could not obtain list of interviews")
    (interviews, start_id) = result
    if start_id is None:
        next_id = None
    else:
        next_id = safeid(str(start_id))
    if is_json:
        for interview in interviews:
            if 'dict' in interview:
                del interview['dict']
            if 'tags' in interview:
                interview['tags'] = sorted(interview['tags'])
        return jsonify(action="interviews", interviews=interviews, next_id=next_id)
    if re.search(r'user/register', str(request.referrer)) and len(interviews) == 1:
        return redirect(url_for('interview.index', i=interviews[0]['filename'], session=interviews[0]['session'], from_list=1))
    tags_used = set()
    for interview in interviews:
        for the_tag in interview['tags']:
            if the_tag != tag:
                tags_used.add(the_tag)
    # interview_page_title = word(daconfig.get('interview page title', 'Interviews'))
    # title = word(daconfig.get('interview page heading', 'Resume an interview'))
    argu = {'version_warning': version_warning, 'tags_used': sorted(tags_used) if len(tags_used) > 0 else None, 'numinterviews': len([y for y in interviews if not y['metadata'].get('hidden', False)]), 'interviews': sorted(interviews, key=valid_date_key), 'tag': tag, 'next_id': next_id, 'show_back': show_back, 'form': form}
    if 'interview page template' in daconfig and daconfig['interview page template']:
        the_page = package_template_filename(daconfig['interview page template'])
        if the_page is None:
            raise DAError("Could not find start page template " + daconfig['start page template'])
        with open(the_page, 'r', encoding='utf-8') as fp:
            template_string = fp.read()
            response = make_response(render_template_string(template_string, **argu), 200)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return response
    else:
        response = make_response(render_template('admin/interviews.html', **argu), 200)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
