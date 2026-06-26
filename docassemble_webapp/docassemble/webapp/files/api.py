import os
import re
import werkzeug
from flask import request
from flask_cors import cross_origin
from flask_login import current_user
from docassemble.webapp.api.helpers import api_verify
from docassemble.webapp.utils.helpers import jsonify_with_status, custom_send_file
from docassemble.webapp.sessions import get_session_uids
from docassemble.webapp.utils.filenames import (
    get_ext_and_mimetype,
    secure_filename_unicode_ok,
)
from .file_access import get_info_from_file_number
from .blueprint import files_bp

@files_bp.route('/api/file/<int:file_number>', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_file(file_number):
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    # yaml_filename = request.args.get('i', None)
    # session_id = request.args.get('session', None)
    number = re.sub(r'[^0-9]', '', str(file_number))
    privileged = bool(current_user.is_authenticated and current_user.has_role('admin', 'advocate'))
    try:
        file_info = get_info_from_file_number(number, privileged=privileged, uids=get_session_uids())
    except:
        return ('File not found', 404)
    if 'path' not in file_info:
        return ('File not found', 404)
    if 'extension' in request.args:
        extension = werkzeug.utils.secure_filename(request.args['extension'])
        if os.path.isfile(file_info['path'] + '.' + extension):
            the_path = file_info['path'] + '.' + extension
            extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
        else:
            return ('File not found', 404)
    elif 'filename' in request.args:
        the_filename = secure_filename_unicode_ok(request.args['filename'])
        if os.path.isfile(os.path.join(os.path.dirname(file_info['path']), the_filename)):
            the_path = os.path.join(os.path.dirname(file_info['path']), the_filename)
            extension, mimetype = get_ext_and_mimetype(the_filename)
        else:
            return ('File not found', 404)
    else:
        the_path = file_info['path']
        mimetype = file_info['mimetype']
    if not os.path.isfile(the_path):
        return ('File not found', 404)
    response = custom_send_file(the_path, mimetype=mimetype)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response
