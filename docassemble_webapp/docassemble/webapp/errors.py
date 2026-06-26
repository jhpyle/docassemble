import json
import traceback
import re
import os
import tempfile
from jinja2.exceptions import TemplateError
from markupsafe import Markup
from flask_wtf.csrf import CSRFError
from bs4 import BeautifulSoup
import werkzeug.exceptions
from flask import (
    request,
    redirect,
    jsonify,
    render_template,
    flash,
    session,
    current_app,
)
from flask_login import current_user
from docassemble.base.error import (
    DANotFoundError,
    DAInvalidFilename,
    DAError,
    DASourceError,
)
from docassemble.base.functions import get_message_log, all_variables, interview_path
from docassemble.base.language.control import get_language
from docassemble.base.language.words import word
from docassemble.base.save_status import SS_NEW, SS_IGNORE
from docassemble.base.thread_context import this_thread
from docassemble.base.util import markdown_to_html
from docassemble.webapp.config import (
    ERROR_TYPES_NO_EMAIL,
    DEBUG,
    NOTIFICATION_CONTAINER,
    NOTIFICATION_MESSAGE,
    DEFER,
    DEFAULT_LANGUAGE,
    LOGFILE,
    daconfig,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.interview.helpers import get_history, get_part
from docassemble.webapp.interview.views import index
from docassemble.webapp.lock import release_lock
from docassemble.webapp.mail.da_flask_mail import Message
from docassemble.webapp.mail.hooks import da_send_mail
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.utils.helpers import noquote, get_requester_ip
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage

def init_app(app):
    @app.errorhandler(404)
    def page_not_found_error(the_error):  # pylint: disable=unused-argument
        return render_template('pages/404.html'), 404


    @app.errorhandler(Exception)
    def server_error(the_error):
        setup_translation()
        if hasattr(the_error, 'interview') and the_error.interview.debug and hasattr(the_error, 'interview_status'):
            the_history = get_history(the_error.interview, the_error.interview_status)
        else:
            the_history = None
        the_vars = None
        if isinstance(the_error, DASourceError):
            if (DEBUG and daconfig.get('development site is protected', False)) or (current_user.is_authenticated and current_user.has_role('admin', 'developer')):
                errmess = str(the_error)
            else:
                errmess = word("There was an error. Please contact the system administrator.")
            the_trace = None
            logmessage(str(the_error))
        elif isinstance(the_error, (DAError, DANotFoundError, DAInvalidFilename)):
            errmess = str(the_error)
            the_trace = None
            logmessage(errmess)
        elif isinstance(the_error, TemplateError):
            errmess = str(the_error)
            if hasattr(the_error, 'name') and the_error.name is not None:
                errmess += "\nName: " + str(the_error.name)
            if hasattr(the_error, 'filename') and the_error.filename is not None:
                errmess += "\nFilename: " + str(the_error.filename)
            if hasattr(the_error, 'docx_context'):
                errmess += "\n\nContext:\n" + "\n".join(map(lambda x: "  " + x, the_error.docx_context))
            the_trace = traceback.format_exc()
            try:
                logmessage(errmess)
            except:
                logmessage("Could not log the error message")
        else:
            try:
                errmess = str(type(the_error).__name__) + ": " + str(the_error)
            except:
                errmess = str(type(the_error).__name__)
            if hasattr(the_error, 'traceback'):
                the_trace = the_error.traceback
            else:
                the_trace = traceback.format_exc()
            if hasattr(this_thread, 'misc') and 'current_field' in this_thread.misc:
                errmess += "\nIn field index number " + str(this_thread.misc['current_field'])
            if hasattr(the_error, 'da_line_with_error'):
                errmess += "\nIn line: " + str(the_error.da_line_with_error)
            try:
                logmessage(errmess)
            except:
                logmessage("Could not log the error message")
            logmessage(the_trace)
        if isinstance(the_error, DAError):
            error_code = the_error.error_code
        if isinstance(the_error, DANotFoundError):
            error_code = 404
        elif isinstance(the_error, werkzeug.exceptions.HTTPException):
            error_code = the_error.code
        else:
            error_code = 501
        if hasattr(the_error, 'user_dict'):
            the_vars = the_error.user_dict
        if hasattr(the_error, 'interview'):
            special_error_markdown = the_error.interview.consolidated_metadata.get('error help', None)
            if isinstance(special_error_markdown, dict):
                language = get_language()
                if language in special_error_markdown:
                    special_error_markdown = special_error_markdown[language]
                elif '*' in special_error_markdown:
                    special_error_markdown = special_error_markdown['*']
                elif DEFAULT_LANGUAGE in special_error_markdown:
                    special_error_markdown = special_error_markdown[DEFAULT_LANGUAGE]
                else:
                    special_error_markdown = None
        else:
            special_error_markdown = None
        if special_error_markdown is None:
            special_error_markdown = daconfig.get('error help', None)
        if special_error_markdown is not None:
            special_error_html = markdown_to_html(special_error_markdown)
        else:
            special_error_html = None
        flask_logtext = []
        if os.path.exists(LOGFILE):
            with open(LOGFILE, encoding='utf-8') as the_file:
                for line in the_file:
                    if re.match('Exception', line):
                        flask_logtext = []
                    flask_logtext.append(line)
        orig_errmess = errmess
        errmess = noquote(errmess)
        if re.search(r'\n', errmess):
            errmess = '<pre>' + errmess + '</pre>'
        else:
            errmess = '<blockquote class="blockquote">' + errmess + '</blockquote>'
        initial_values = {
            "daMessageLog": get_message_log(),
            "daNotificationContainer": NOTIFICATION_CONTAINER % ('',),
            "daNotificationMessage": NOTIFICATION_MESSAGE,
        }
        script = f"""
    <script{DEFER} src="{url_for('static', filename="app/501.min.js")}"></script>
    <script{DEFER}>Object.assign(window, {json.dumps(initial_values)});</script>"""
        error_notification(the_error, message=errmess, history=the_history, trace=the_trace, the_request=request, the_vars=the_vars)
        if (request.path.endswith('/interview') or request.path.endswith('/start') or request.path.endswith('/run')) and interview_path() is not None:
            if this_thread.misc.get('save_status', SS_NEW) != SS_IGNORE:
                try:
                    release_lock(this_thread.current_info['session'], this_thread.current_info['yaml_filename'])
                except:
                    pass
            if 'in error' not in session and this_thread.interview is not None and 'error action' in this_thread.interview.consolidated_metadata:
                session['in error'] = True
                return index(action_argument={'action': this_thread.interview.consolidated_metadata['error action'], 'arguments': {'error_message': orig_errmess, 'error_history': the_history, 'error_trace': the_trace}}, refer=['error'])
        if int(int(error_code)/100) == 4:
            show_debug = False
        elif isinstance(the_error, (DAError, DAInvalidFilename)):
            show_debug = False
        elif DEBUG and daconfig.get('development site is protected', False):
            show_debug = True
        elif current_user.is_authenticated and current_user.has_role('admin', 'developer'):
            show_debug = True
        else:
            show_debug = False
        if error_code == 404:
            the_template = 'pages/404.html'
        else:
            the_template = 'pages/501.html'
        try:
            yaml_filename = interview_path()
        except:
            yaml_filename = None
        show_retry = request.path.endswith('/interview') or request.path.endswith('/start') or request.path.endswith('/run')
        extra_js = Markup(script)
        error_page_extra_js = get_part('error page extra javascript')
        if isinstance(error_page_extra_js, Markup):
            extra_js += error_page_extra_js
        return render_template(the_template, verbose=daconfig.get('verbose error messages', True), version_warning=None, error=errmess, historytext=str(the_history), logtext=str(the_trace), extra_js=extra_js, special_error=special_error_html, show_debug=show_debug, yaml_filename=yaml_filename, show_retry=show_retry), error_code


    @app.errorhandler(CSRFError)
    def handle_csrf_error(the_error):
        if request.method == 'POST' and '/checkout' not in request.url:
            setup_translation()
            if 'ajax' in request.form and int(request.form['ajax']):
                flash(word("Input not processed because the page expired."), "success")
                return jsonify({'action': 'reload', 'reason': 'csrf_error'})
            try:
                referer = str(request.referrer)
            except:
                referer = None
            if referer and referer != 'None':
                flash(word("Input not processed because the page expired."), "success")
                return redirect(referer)
        return server_error(the_error)


def error_notification(err, message=None, history=None, trace=None, referer=None, the_request=None, the_vars=None):
    recipient_email = daconfig.get('error notification email', None)
    if not recipient_email:
        return
    if err.__class__.__name__ in ['CSRFError', 'ClientDisconnected', 'MethodNotAllowed', 'DANotFoundError', 'DAInvalidFilename'] + ERROR_TYPES_NO_EMAIL:
        return
    email_recipients = []
    if isinstance(recipient_email, list):
        email_recipients.extend(recipient_email)
    else:
        email_recipients.append(recipient_email)
    if message is None:
        errmess = str(err)
    else:
        errmess = message
    try:
        email_address = current_user.email
    except:
        email_address = None
    if the_request:
        try:
            referer = str(the_request.referrer)
        except:
            referer = None
        ipaddress = get_requester_ip(the_request)
    else:
        referer = None
        ipaddress = None
    if daconfig.get('error notification variables', DEBUG):
        if the_vars is None:
            try:
                the_vars = all_variables(include_internal=True)
            except:
                pass
    else:
        the_vars = None
    json_filename = None
    if the_vars is not None and len(the_vars):
        try:
            with tempfile.NamedTemporaryFile(mode='w', prefix="datemp", suffix='.json', delete=False, encoding='utf-8') as fp:
                fp.write(json.dumps(the_vars, sort_keys=True, indent=2))
                json_filename = fp.name
        except:
            pass
    the_interview_path = interview_path()
    try:
        the_key = 'da:errornotification:' + str(ipaddress)
        existing = r.get(the_key)
        pipe = r.pipeline()
        pipe.set(the_key, 1)
        pipe.expire(the_key, 60)
        pipe.execute()
        if existing:
            return
    except:
        pass
    try:
        try:
            html = "<html>\n  <body>\n    <p>There was an error in the " + current_app.config['APP_NAME'] + " current_application.</p>\n    <p>The error message was:</p>\n<pre>" + err.__class__.__name__ + ": " + str(errmess) + "</pre>\n"
            body = "There was an error in the " + current_app.config['APP_NAME'] + " application.\n\nThe error message was:\n\n" + err.__class__.__name__ + ": " + str(errmess)
            if trace is not None:
                body += "\n\n" + str(trace)
                html += "<pre>" + str(trace) + "</pre>"
            if history is not None:
                body += "\n\n" + BeautifulSoup(history, "html.parser").get_text('\n')
                html += history
            if referer is not None and referer != 'None':
                body += "\n\nThe referer URL was " + str(referer)
                html += "<p>The referer URL was " + str(referer) + "</p>"
            elif the_interview_path is not None:
                body += "\n\nThe interview was " + str(the_interview_path)
                html += "<p>The interview was " + str(the_interview_path) + "</p>"
            if email_address is not None:
                body += "\n\nThe user was " + str(email_address)
                html += "<p>The user was " + str(email_address) + "</p>"
            if trace is not None:
                body += "\n\n" + str(trace)
                html += "<pre>" + str(trace) + "</pre>"
            if 'external hostname' in daconfig and daconfig['external hostname'] is not None:
                body += "\n\nThe external hostname was " + str(daconfig['external hostname'])
                html += "<p>The external hostname was " + str(daconfig['external hostname']) + "</p>"
            html += "\n  </body>\n</html>"
            msg = Message(current_app.config['APP_NAME'] + " error: " + err.__class__.__name__, recipients=email_recipients, body=body, html=html)
            if json_filename:
                with open(json_filename, 'r', encoding='utf-8') as fp:
                    msg.attach('variables.json', 'application/json', fp.read())
            da_send_mail(msg, None)
        except BaseException as zerr:
            logmessage(str(zerr))
            body = "There was an error in the " + current_app.config['APP_NAME'] + " application."
            html = "<html>\n  <body>\n    <p>There was an error in the " + current_app.config['APP_NAME'] + " application.</p>\n  </body>\n</html>"
            msg = Message(current_app.config['APP_NAME'] + " error: " + err.__class__.__name__, recipients=email_recipients, body=body, html=html)
            if json_filename:
                with open(json_filename, 'r', encoding='utf-8') as fp:
                    msg.attach('variables.json', 'application/json', fp.read())
            da_send_mail(msg, None)
    except:
        pass
