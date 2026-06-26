import zoneinfo
import re
import datetime
import tempfile
import os
from urllib.parse import quote as urllibquote
from urllib.request import urlretrieve
import zipfile
import tailer
import humanize
import httplib2
from flask import current_app, Blueprint, render_template, request, make_response, flash
from docassemble_flask_user import login_required, roles_required
from docassemble.base.language.words import word
from docassemble.webapp.config import LOGSERVER, LOG_DIRECTORY
from docassemble.webapp.main.hooks import get_default_timezone
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.utils.filenames import secure_filename_spaces_ok
from docassemble.webapp.utils.helpers import (
    call_sync,
    true_or_false,
    version_warning,
    custom_send_file,
)
from .forms import LogForm

logs_bp = Blueprint(
    'logs',
    __name__,
    template_folder='templates'
)

@logs_bp.route('/logfile/<filename>', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def logfile(filename):
    if LOGSERVER is None:
        the_file = os.path.join(LOG_DIRECTORY, filename)
        if not os.path.isfile(the_file):
            return ('File not found', 404)
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8082', "GET")  # pylint: disable=unused-variable
        try:
            the_file, headers = urlretrieve("http://" + LOGSERVER + ':8082/' + urllibquote(filename))  # pylint: disable=unused-variable
        except:
            return ('File not found', 404)
    response = custom_send_file(the_file, as_attachment=True, mimetype='text/plain', download_name=filename, max_age=0)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@logs_bp.route('/logs', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def logs():
    setup_translation()
    if not current_app.config['ALLOW_LOG_VIEWING']:
        return ('File not found', 404)
    form = LogForm(request.form)
    use_zip = true_or_false(request.args.get('zip', None))
    if LOGSERVER is None and use_zip:
        timezone = get_default_timezone()
        zip_archive = tempfile.NamedTemporaryFile(mode="wb", prefix="datemp", suffix=".zip", delete=False)
        zf = zipfile.ZipFile(zip_archive, compression=zipfile.ZIP_DEFLATED, mode='w')
        for f in os.listdir(LOG_DIRECTORY):
            zip_path = os.path.join(LOG_DIRECTORY, f)
            if f.startswith('.') or not os.path.isfile(zip_path):
                continue
            info = zipfile.ZipInfo(f)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.date_time = datetime.datetime.fromtimestamp(os.path.getmtime(zip_path), datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)).timetuple()
            with open(zip_path, 'rb') as fp:
                zf.writestr(info, fp.read())
        zf.close()
        zip_file_name = re.sub(r'[^A-Za-z0-9_]+', '', current_app.config['APP_NAME']) + '_logs.zip'
        response = custom_send_file(zip_archive.name, mimetype='application/zip', as_attachment=True, download_name=zip_file_name)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    the_file = request.args.get('file', None)
    if the_file is not None:
        the_file = secure_filename_spaces_ok(the_file)
    default_filter_string = request.args.get('q', '')
    if request.method == 'POST' and form.file_name.data:
        the_file = form.file_name.data
    if the_file is not None and (the_file.startswith('.') or the_file.startswith('/') or the_file == ''):
        the_file = None
    if the_file is not None:
        the_file = secure_filename_spaces_ok(the_file)
    total_bytes = 0
    if LOGSERVER is None:
        call_sync()
        files = []
        for f in os.listdir(LOG_DIRECTORY):
            path = os.path.join(LOG_DIRECTORY, f)
            if not os.path.isfile(path):
                continue
            files.append(f)
            total_bytes += os.path.getsize(path)
        files = sorted(files)
        total_bytes = humanize.naturalsize(total_bytes)
        if the_file is None and len(files):
            if 'docassemble.log' in files:
                the_file = 'docassemble.log'
            else:
                the_file = files[0]
        if the_file is not None:
            filename = os.path.join(LOG_DIRECTORY, the_file)
        else:
            filename = ''
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8082', "GET")
        if int(resp['status']) >= 200 and int(resp['status']) < 300:
            files = [f for f in content.decode().split("\n") if f != '' and f is not None]
        else:
            return ('File not found', 404)
        if len(files) > 0:
            if the_file is None:
                the_file = files[0]
            filename, headers = urlretrieve("http://" + LOGSERVER + ':8082/' + urllibquote(the_file))  # pylint: disable=unused-variable
        else:
            filename = ''
    if len(files) > 0 and not os.path.isfile(filename):
        flash(word("The file you requested does not exist."), 'error')
        if len(files) > 0:
            the_file = files[0]
            filename = os.path.join(LOG_DIRECTORY, files[0])
    if len(files) > 0:
        if request.method == 'POST' and form.submit.data and form.filter_string.data:
            default_filter_string = form.filter_string.data
        try:
            reg_exp = re.compile(default_filter_string)
        except:
            flash(word("The regular expression you provided could not be parsed."), 'error')
            default_filter_string = ''
        if default_filter_string == '':
            try:
                lines = tailer.tail(open(filename, encoding='utf-8'), 30)
            except:
                lines = [word('Unable to read log file; please download.')]
        else:
            temp_file = tempfile.NamedTemporaryFile(mode='a+', encoding='utf-8')
            with open(filename, 'r', encoding='utf-8') as fp:
                for line in fp:
                    if reg_exp.search(line):
                        temp_file.write(line)
            temp_file.seek(0)
            try:
                lines = tailer.tail(temp_file, 30)
            except:
                lines = [word('Unable to read log file; please download.')]
            temp_file.close()
        content = "\n".join(map(lambda x: x, lines))
    else:
        content = "No log files available"
    show_download_all = bool(LOGSERVER is None)
    response = make_response(render_template('logs/logs.html', version_warning=version_warning, bodyclass='daadminbody', tab_title=word("Logs"), page_title=word("Logs"), form=form, files=files, current_file=the_file, content=content, default_filter_string=default_filter_string, show_download_all=show_download_all, total_bytes=total_bytes), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response
