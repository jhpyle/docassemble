import json
import importlib
import os
import re
from pathlib import Path
from urllib.parse import quote as urllibquote
from user_agents import parse as ua_parse
from markupsafe import Markup
from flask import (
    current_app,
    redirect,
    request,
    abort,
    jsonify,
    Response,
    make_response,
    render_template_string,
    render_template,
    session,
)
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
from docassemble_flask_user import login_required, roles_required
from docassemble.base.error import DAError
from docassemble.base.functions import package_data_filename
from docassemble.base.language.words import word
from docassemble.webapp.config import (
    READY_FILE,
    da_version,
    DEFER,
    daconfig,
    START_TIME,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import kv_session, csrf
from docassemble.webapp.sessions import update_session
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.utils.filenames import get_ext_and_mimetype
from docassemble.webapp.utils.helpers import (
    custom_send_file,
    jsonify_restart_task,
    jsonify_with_status,
    reset_process_running,
)
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from .blueprint import main_bp
from .helpers import restart_all

@main_bp.route('/rjs/<key>.js', methods=['GET'])
def rjs(key):
    the_key = 'da:rjs:' + key
    data = r.get(the_key)
    r.delete(the_key)
    if data is None:
        return ('File not found', 404)
    response = make_response(data, 200)
    response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@main_bp.route('/goto', methods=['GET'])
def run_temp():
    code = request.args.get('c', None)
    if code is None:
        abort(403)
    ua_string = request.headers.get('User-Agent', None)
    if ua_string is not None:
        response = ua_parse(ua_string)
        if response.device.brand == 'Spider':
            return render_template_string('')
    the_key = 'da:temporary_url:' + str(code)
    data = r.get(the_key)
    if data is None:
        raise DAError(word("The link has expired."), code=403)
    try:
        data = json.loads(data.decode())
        if data.get('once', False):
            r.delete(the_key)
        url = data.get('url')
    except:
        r.delete(the_key)
        url = data.decode()
    return redirect(url)


@main_bp.route("/user/post-sign-in", methods=['GET'])
def post_sign_in():
    return redirect(url_for('admin.interview_list', from_login='1'))


@main_bp.route("/cleanup_sessions", methods=['GET'])
def cleanup_sessions():
    kv_session.cleanup_sessions()
    return render_template('base_templates/blank.html')


@main_bp.route("/health_status", methods=['GET'])
def health_status():
    ok = True
    if request.args.get('ready', False):
        if not os.path.isfile(READY_FILE):
            ok = False
    return jsonify({'ok': ok, 'server_start_time': START_TIME, 'version': da_version})


@main_bp.route("/health_check", methods=['GET'])
def health_check():
    if request.args.get('ready', False):
        if not os.path.isfile(READY_FILE):
            return ('', 400)
    response = make_response(render_template('pages/health_check.html', content="OK"), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@main_bp.route('/check_restart_status', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def check_restart_status():
    if not current_app.config['ALLOW_RESTARTING']:
        return ('File not found', 404)
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


@main_bp.route("/restart_ajax", methods=['POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_ajax():
    if not current_app.config['ALLOW_RESTARTING']:
        return ('File not found', 404)
    # logmessage("restart_ajax: action is " + str(request.form.get('action', None)))
    # if current_user.has_role('admin', 'developer'):
    #     logmessage("restart_ajax: user has permission")
    # else:
    #     logmessage("restart_ajax: user has no permission")
    if request.form.get('action', None) == 'restart' and current_user.has_role('admin', 'developer'):
        logmessage("restart_ajax: restarting")
        return_val = jsonify_restart_task()
        restart_all()
        return return_val
    return jsonify(success=False)


@main_bp.route("/dark_mode", methods=['GET'])
def force_dark_mode():
    session['color_scheme'] = 2
    return ('', 200)


@main_bp.route("/color_scheme", methods=['PATCH'])
@csrf.exempt
def change_color_scheme():
    patch_data = request.form.copy()
    if 'scheme' in patch_data and patch_data['scheme'] in ('0', '1', '2'):
        session['color_scheme'] = int(patch_data['scheme'])
        return jsonify({'scheme': session['color_scheme']})
    return ('{"scheme": 0}', 200)


@main_bp.route("/resume", methods=['POST'])
@csrf.exempt
def resume():
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    if 'session' not in post_data or 'i' not in post_data:
        abort(403)
    update_session(post_data['i'], uid=post_data['session'])
    del post_data['session']
    if 'ajax' in post_data:
        ajax_value = int(post_data['ajax'])
        del post_data['ajax']
        if ajax_value:
            return jsonify(action='redirect', url=url_for('interview.index', **post_data), csrf_token=generate_csrf())
    return redirect(url_for('interview.index', **post_data))


@main_bp.route('/restart', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_page():
    setup_translation()
    if not current_app.config['ALLOW_RESTARTING']:
        return ('File not found', 404)
    next_url = current_app.user_manager.make_safe_url_function(request.args.get('next', url_for('admin.interview_list', post_restart=1)))
    script = f"""
    <script{DEFER}>
      var nextUrl = {json.dumps(next_url)};
      var pollInterval = null;
      var taskId = null;
      function daRestartCallback(data){{
        taskId = data.task_id;
        pollInterval = setInterval(daPoll, 4000);
      }}
      function daPoll(){{
        $.ajax({{
          type: 'GET',
          url: {json.dumps(url_for('main.check_restart_status'))} + '?' + $.param({{"task_id": taskId}}),
          success: daCheckStatus,
          error: daIgnoreStatus,
          dataType: 'json',
          timeout: 3500
        }});
      }}
      function daCheckStatus(data){{
        if (data.status == "completed"){{
          clearInterval(pollInterval);
          window.location.replace(nextUrl);
        }}
        else{{
          console.log("Status of restart was: " + data.status + ".");
        }}
      }}
      function daIgnoreStatus(data){{
        console.log("Unable to check status of restart. Perhaps the server will respond again.")
      }}
      function daRestart(){{
        $.ajax({{
          type: 'POST',
          url: {json.dumps(url_for('main.restart_ajax'))},
          data: 'csrf_token={generate_csrf()}&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        }});
        return true;
      }}
      document.addEventListener("DOMContentLoaded", function () {{
        $( document ).ready(function() {{
          //console.log("restarting");
          setTimeout(daRestart, 100);
        }});
      }});
    </script>"""
    response = make_response(render_template('main/restart.html', version_warning=None, bodyclass='daadminbody', extra_js=Markup(script), tab_title=word('Restarting'), page_title=word('Restarting')), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@main_bp.route('/bundle.css', methods=['GET'])
def css_bundle():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = ''
    for parts in [['bootstrap', 'css', 'bootstrap-icons.css'], ['bootstrap-fileinput', 'css', 'fileinput.css'], ['labelauty', 'source', 'jquery-labelauty.css'], ['bootstrap-combobox', 'css', 'bootstrap-combobox.css'], ['bootstrap-slider', 'dist', 'css', 'bootstrap-slider.css'], ['app', 'app.css']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    return Response(output, mimetype='text/css')


@main_bp.route('/bundle.js', methods=['GET'])
def js_bundle():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = ''
    for parts in [['app', 'jquery.js'], ['app', 'jquery.validate.js'], ['app', 'additional-methods.js'], ['app', 'jquery.visible.js'], ['bootstrap', 'js', 'bootstrap.bundle.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-fileinput', 'js', 'plugins', 'buffer.js'], ['bootstrap-fileinput', 'js', 'plugins', 'filetype.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.js'], ['bootstrap-fileinput', 'js', 'plugins', 'sortable.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['app', 'app.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js'], ['app', 'socket.io.js'], ['app', 'signature_pad.umd.min.js']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    return Response(output, mimetype='application/javascript')


@main_bp.route('/adminbundle.js', methods=['GET'])
def js_admin_bundle():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = ''
    for parts in [['app', 'jquery.js'], ['bootstrap', 'js', 'bootstrap.bundle.js'], ['app', 'admin.js']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    return Response(output, mimetype='application/javascript')


@main_bp.route('/bundlewrapjquery.js', methods=['GET'])
def js_bundle_wrap():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = '(function($) {'
    for parts in [['app', 'jquery.validate.js'], ['app', 'additional-methods.js'], ['app', 'jquery.visible.js'], ['bootstrap', 'js', 'bootstrap.bundle.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'buffer.js'], ['bootstrap-fileinput', 'js', 'plugins', 'filetype.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.js'], ['bootstrap-fileinput', 'js', 'plugins', 'sortable.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['app', 'app.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js'], ['app', 'socket.io.js']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    output += '})(jQuery);'
    return Response(output, mimetype='application/javascript')


@main_bp.route('/bundlenojquery.js', methods=['GET'])
def js_bundle_no_query():
    base_path = Path(importlib.resources.files('docassemble.webapp'), 'static')
    output = ''
    for parts in [['app', 'jquery.validate.js'], ['app', 'additional-methods.js'], ['app', 'jquery.visible.js'], ['bootstrap', 'js', 'bootstrap.bundle.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.js'], ['bootstrap-fileinput', 'js', 'plugins', 'buffer.js'], ['bootstrap-fileinput', 'js', 'plugins', 'filetype.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.js'], ['bootstrap-fileinput', 'js', 'plugins', 'sortable.js'], ['bootstrap-fileinput', 'js', 'fileinput.js'], ['app', 'app.js'], ['labelauty', 'source', 'jquery-labelauty.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.js'], ['app', 'socket.io.js']]:
        with open(os.path.join(base_path, *parts), encoding='utf-8') as fp:
            output += fp.read()
        output += "\n"
    output += ''
    return Response(output, mimetype='application/javascript')


@main_bp.route('/packagestatic/<package>/<path:filename>', methods=['GET'])
def package_static(package, filename):
    try:
        attach = int(request.args.get('attachment', 0))
    except:
        attach = 0
    if '../' in filename:
        return ('File not found', 404)
    if package == 'fonts':
        return redirect(url_for('static', filename='bootstrap/fonts/' + filename, v=da_version))
    try:
        filename = re.sub(r'^\.+', '', filename)
        filename = re.sub(r'\/\.+', '/', filename)
        the_file = package_data_filename(str(package) + ':data/static/' + str(filename))
    except:
        return ('File not found', 404)
    if the_file is None:
        return ('File not found', 404)
    if not os.path.isfile(the_file):
        return ('File not found', 404)
    extension, mimetype = get_ext_and_mimetype(the_file)  # pylint: disable=unused-variable
    response = custom_send_file(the_file, mimetype=str(mimetype), download_name=filename)
    if attach:
        filename = os.path.basename(filename)
        response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename))
    return response


def favicon_file(filename, alt=None):
    the_dir = package_data_filename(daconfig.get('favicon', 'docassemble.webapp:data/static/favicon'))
    if the_dir is None or not os.path.isdir(the_dir):
        logmessage("favicon_file: could not find favicon directory")
        return ('File not found', 404)
    the_file = os.path.join(the_dir, filename)
    if not os.path.isfile(the_file):
        if alt is not None:
            the_file = os.path.join(the_dir, alt)
        if not os.path.isfile(the_file):
            return ('File not found', 404)
    if filename == 'site.webmanifest':
        mimetype = 'application/manifest+json'
    else:
        extension, mimetype = get_ext_and_mimetype(the_file)  # pylint: disable=unused-variable
    response = custom_send_file(the_file, mimetype=mimetype, download_name=filename)
    return response


@main_bp.route("/favicon.ico", methods=['GET'])
def favicon():
    return favicon_file('favicon.ico')


@main_bp.route("/apple-touch-icon.png", methods=['GET'])
def apple_touch_icon():
    return favicon_file('apple-touch-icon.png')


@main_bp.route("/favicon-32x32.png", methods=['GET'])
def favicon_md():
    return favicon_file('favicon-32x32.png')


@main_bp.route("/favicon-16x16.png", methods=['GET'])
def favicon_sm():
    return favicon_file('favicon-16x16.png')


@main_bp.route("/site.webmanifest", methods=['GET'])
def favicon_site_webmanifest():
    return favicon_file('site.webmanifest', alt='manifest.json')


@main_bp.route("/manifest.json", methods=['GET'])
def favicon_manifest_json():
    return favicon_file('manifest.json', alt='site.webmanifest')


@main_bp.route("/safari-pinned-tab.svg", methods=['GET'])
def favicon_safari_pinned_tab():
    return favicon_file('safari-pinned-tab.svg')


@main_bp.route("/android-chrome-192x192.png", methods=['GET'])
def favicon_android_md():
    return favicon_file('android-chrome-192x192.png')


@main_bp.route("/android-chrome-512x512.png", methods=['GET'])
def favicon_android_lg():
    return favicon_file('android-chrome-512x512.png')


@main_bp.route("/mstile-150x150.png", methods=['GET'])
def favicon_mstile():
    return favicon_file('mstile-150x150.png')


@main_bp.route("/browserconfig.xml", methods=['GET'])
def favicon_browserconfig():
    return favicon_file('browserconfig.xml')


@main_bp.route("/robots.txt", methods=['GET'])
def robots():
    if 'robots' not in daconfig and daconfig.get('allow robots', False):
        response = make_response("User-agent: *\nDisallow:", 200)
        response.mimetype = "text/plain"
        return response
    the_file = package_data_filename(daconfig.get('robots', 'docassemble.webapp:data/static/robots.txt'))
    if the_file is None:
        return ('File not found', 404)
    if not os.path.isfile(the_file):
        return ('File not found', 404)
    response = custom_send_file(the_file, mimetype='text/plain', download_name='robots.txt')
    return response
