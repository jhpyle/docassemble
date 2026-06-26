# pylint: disable=no-member
import zoneinfo
import ast
import datetime
import importlib
from urllib.parse import (
    quote as urllibquote,
    unquote as urllibunquote,
    urlsplit,
    urlencode,
)
import json
import math
import mimetypes
import os
import re
import shutil
import subprocess
from subprocess import Popen, PIPE
import tempfile
import time
import types
import unicodedata
import uuid
import xml.etree.ElementTree as ET
import codecs
import copy
import dateutil
import links_from_header
import celery
from Crypto.Hash import MD5
from dateutil import tz
from flask import (
    g,
    request,
    redirect,
    Response,
    jsonify,
    abort,
    send_file,
    flash,
    session,
    current_app,
)
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
from user_agents import parse as ua_parse
from markupsafe import Markup
import packaging
from sqlalchemy import or_, and_, select, update, inspect, create_engine
from werkzeug.datastructures import Headers
from docassemble.base.error import (
    DAErrorCompileError,
    DAError,
    DAErrorMissingVariable,
    DAErrorNoEndpoint,
    DAException,
)
from docassemble.base.functions import (
    get_uid,
    static_filename_path,
    url_of,
    modify_i_argument,
    indent,
    url_action,
    pickleable_objects,
    safeyaml,
)
from docassemble.base.generate_key import random_alphanumeric, random_string
from docassemble.base.hooks import get_ml_info
from docassemble.base.language.control import set_language, get_language
from docassemble.base.language.core import update_language_function
from docassemble.base.language.language import comma_and_list
from docassemble.base.language.words import update_word_collection, word
from docassemble.base.pandoc import can_convert_word_to_markdown
from docassemble.base.thread_context import this_thread
from docassemble.base.util import DAFile, DAFileList, DAFileCollection, DAStaticFile
from docassemble.webapp.cloud.utils import cloud
from docassemble.webapp.config import (
    PNG_SCREEN_RESOLUTION,
    PDFTOPPM_COMMAND,
    STATS,
    GITHUB_BRANCH,
    PACKAGE_PROTECTION,
    USE_GOOGLE_PLACES_NEW_API,
    USING_SUPERVISOR,
    NOTIFICATION_MESSAGE,
    DEFAULT_LANGUAGE,
    PNG_RESOLUTION,
    ROOT,
    BUTTON_COLOR_NAV_LOGIN,
    HTTP_TO_HTTPS,
    SUPERVISORCTL,
    DEFER,
    ALLOW_REGISTRATION,
    COOKIELESS_SESSIONS,
    google_config,
    google_api_key,
    da_version,
    START_TIME,
    daconfig,
    hostname,
    DEFAULT_TIMEZONE,
)
from docassemble.webapp.utils.constants import min_system_version
from docassemble.webapp.daredis import r
from docassemble.webapp.develop.common import get_repo_info, get_playground_user
from docassemble.webapp.extensions import db
from docassemble.webapp.files.file_access import (
    get_info_from_file_reference,
    url_if_exists,
)
from docassemble.webapp.files.common import can_access_file_number
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.info import system_packages
from docassemble.webapp.interview.common import get_unique_name
from docassemble.webapp.interview.dictionary import fresh_dictionary
from docassemble.webapp.mail.da_flask_mail import Message  # noqa: F401 # pylint: disable=unused-import
from docassemble.webapp.packages.models import Package, PackageAuth
from docassemble.webapp.sessions import (
    get_session_uids,
    get_session,
    update_session,
    clear_specific_session,
    clear_session,
)
from docassemble.webapp.tasks.app import celery_app
from docassemble.webapp.utils.encryption import encrypt_phrase
from docassemble.webapp.utils.filenames import directory_for
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.utils.request import get_requester_ip
from docassemble.webapp.utils.hooks import url_for
import docassemble.webapp.database
import docassemble.webapp.setup
import docassemble.webapp.user_database

CAN_CONVERT_WORD = can_convert_word_to_markdown()

if packaging.version.parse(min_system_version) > packaging.version.parse(daconfig['system version']):
    version_warning = word("A new docassemble system version is available.  If you are using Docker, install a new Docker image.")
else:
    version_warning = None  # pylint: disable=invalid-name

TheMethodType = types.FunctionType

equals_byte = bytes('=', 'utf-8')

request_active = True  # pylint: disable=invalid-name

emoji_match = re.compile(r':([A-Za-z][A-Za-z0-9\_\-]+):')
html_match = re.compile(r'(</?[A-Za-z\!][^>]*>|https*://[A-Za-z0-9\-\_:\%\/\@\.\#\&\=\~\?]+|mailto*://[A-Za-z0-9\-\_:\%\/\@\.\#\&\=\~]+\?)')

# pylint: disable=invalid-name
default_playground_yaml = """metadata:
  title: Default playground interview
  short title: Test
  comment: This is a learning tool.  Feel free to write over it.
---
objects:
  - client: Individual
---
question: |
  What is your name?
fields:
  - First Name: client.name.first
  - Middle Name: client.name.middle
    required: False
  - Last Name: client.name.last
  - Suffix: client.name.suffix
    required: False
    code: name_suffix()
---
question: |
  What is your date of birth?
fields:
  - Date of Birth: client.birthdate
    datatype: date
---
mandatory: True
question: |
  Here is your document, ${ client }.
subquestion: |
  In order ${ quest }, you will need this.
attachments:
  - name: Information Sheet
    filename: info_sheet
    content: |
      Your name is ${ client }.

      % if client.age_in_years() > 60:
      You are a senior.
      % endif
      Your quest is ${ quest }.  You
      are eligible for ${ benefits }.
---
question: |
  What is your quest?
fields:
  - Your quest: quest
    hint: to find the Loch Ness Monster
---
code: |
  if client.age_in_years() < 18:
    benefits = "CHIP"
  else:
    benefits = "Medicaid"
"""

ok_mimetypes = {
    "application/javascript": "javascript",
    "application/json": "javascript",
    "text/css": "css",
    "text/html": "htmlmixed",
    "text/x-python": "python"
}
ok_extensions = {
    "4th": "forth",
    "apl": "apl",
    "asc": "asciiarmor",
    "asn": "asn.1",
    "asn1": "asn.1",
    "aspx": "htmlembedded",
    "b": "brainfuck",
    "bash": "shell",
    "bf": "brainfuck",
    "c": "clike",
    "c++": "clike",
    "cc": "clike",
    "cl": "commonlisp",
    "clj": "clojure",
    "cljc": "clojure",
    "cljs": "clojure",
    "cljx": "clojure",
    "cob": "cobol",
    "coffee": "coffeescript",
    "cpp": "clike",
    "cpy": "cobol",
    "cql": "sql",
    "cr": "crystal",
    "cs": "clike",
    "csharp": "clike",
    "css": "css",
    "cxx": "clike",
    "cyp": "cypher",
    "cypher": "cypher",
    "d": "d",
    "dart": "dart",
    "diff": "diff",
    "dtd": "dtd",
    "dyalog": "apl",
    "dyl": "dylan",
    "dylan": "dylan",
    "e": "eiffel",
    "ecl": "ecl",
    "ecmascript": "javascript",
    "edn": "clojure",
    "ejs": "htmlembedded",
    "el": "commonlisp",
    "elm": "elm",
    "erb": "htmlembedded",
    "erl": "erlang",
    "f": "fortran",
    "f77": "fortran",
    "f90": "fortran",
    "f95": "fortran",
    "factor": "factor",
    "feature": "gherkin",
    "for": "fortran",
    "forth": "forth",
    "fs": "mllike",
    "fth": "forth",
    "fun": "mllike",
    "go": "go",
    "gradle": "groovy",
    "groovy": "groovy",
    "gss": "css",
    "h": "clike",
    "h++": "clike",
    "haml": "haml",
    "handlebars": "htmlmixed",
    "hbs": "htmlmixed",
    "hh": "clike",
    "hpp": "clike",
    "hs": "haskell",
    "html": "htmlmixed",
    "hx": "haxe",
    "hxml": "haxe",
    "hxx": "clike",
    "in": "properties",
    "ini": "properties",
    "ino": "clike",
    "intr": "dylan",
    "j2": "jinja2",
    "jade": "pug",
    "java": "clike",
    "jinja": "jinja2",
    "jinja2": "jinja2",
    "jl": "julia",
    "json": "json",
    "jsonld": "javascript",
    "jsp": "htmlembedded",
    "jsx": "jsx",
    "ksh": "shell",
    "kt": "clike",
    "less": "css",
    "lhs": "haskell-literate",
    "lisp": "commonlisp",
    "ls": "livescript",
    "ltx": "stex",
    "lua": "lua",
    "m": "octave",
    "markdown": "markdown",
    "mbox": "mbox",
    "md": "markdown",
    "mkd": "markdown",
    "mo": "modelica",
    "mps": "mumps",
    "msc": "mscgen",
    "mscgen": "mscgen",
    "mscin": "mscgen",
    "msgenny": "mscgen",
    "node": "javascript",
    "nq": "ntriples",
    "nsh": "nsis",
    "nsi": "nsis",
    "nt": "ntriples",
    "nut": "clike",
    "oz": "oz",
    "p": "pascal",
    "pas": "pascal",
    "patch": "diff",
    "pgp": "asciiarmor",
    "php": "php",
    "php3": "php",
    "php4": "php",
    "php5": "php",
    "php7": "php",
    "phtml": "php",
    "pig": "pig",
    "pl": "perl",
    "pls": "sql",
    "pm": "perl",
    "pp": "puppet",
    "pro": "idl",
    "properties": "properties",
    "proto": "protobuf",
    "ps1": "powershell",
    "psd1": "powershell",
    "psm1": "powershell",
    "pug": "pug",
    "pxd": "python",
    "pxi": "python",
    "py": "python",
    "pyx": "python",
    "q": "q",
    "r": "r",
    "rb": "ruby",
    "rq": "sparql",
    "rs": "rust",
    "rst": "rst",
    "s": "gas",
    "sas": "sas",
    "sass": "sass",
    "scala": "clike",
    "scm": "scheme",
    "scss": "css",
    "sh": "shell",
    "sieve": "sieve",
    "sig": "asciiarmor",
    "siv": "sieve",
    "slim": "slim",
    "smackspec": "mllike",
    "sml": "mllike",
    "soy": "soy",
    "sparql": "sparql",
    "sql": "sql",
    "ss": "scheme",
    "st": "smalltalk",
    "styl": "stylus",
    "swift": "swift",
    "tcl": "tcl",
    "tex": "stex",
    "textile": "textile",
    "toml": "toml",
    "tpl": "smarty",
    "ts": "javascript",
    "tsx": "javascript",
    "ttcn": "ttcn",
    "ttcn3": "ttcn",
    "ttcnpp": "ttcn",
    "ttl": "turtle",
    "vb": "vb",
    "vbs": "vbscript",
    "vhd": "vhdl",
    "vhdl": "vhdl",
    "vtl": "velocity",
    "vue": "vue",
    "wast": "wast",
    "wat": "wast",
    "webidl": "webidl",
    "xml": "xml",
    "xquery": "xquery",
    "xsd": "xml",
    "xsl": "xml",
    "xu": "mscgen",
    "xy": "xquery",
    "yaml": "yaml",
    "yml": "yaml",
    "ys": "yacas",
    "z80": "z80"
}

contains_volatile = re.compile(r'^(x\.|x\[|.*\[[ijklmn]\])')
is_integer = re.compile(r'^[0-9]+$')
detect_mobile = re.compile(r'Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|NetFront|Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|Dolfin|Dolphin|Skyfire|Zune')
alphanumeric_only = re.compile(r'[\W_]+')
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")
document_match = re.compile(r'^--- *$', flags=re.MULTILINE)
fix_tabs = re.compile(r'\t')
fix_initial = re.compile(r'^---\n')
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
extraneous_var = re.compile(r'^x\.|^x\[')
key_requires_preassembly = re.compile(r'^(session_local\.|device_local\.|user_local\.|x\.|x\[|_multiple_choice|.*\[[ijklmn]\])')
# match_invalid = re.compile('[^A-Za-z0-9_\[\].\'\%\-=]')
# match_invalid_key = re.compile('[^A-Za-z0-9_\[\].\'\%\- =]')
match_brackets = re.compile(r'\[[BRO]?\'[^\]]*\'\]$')
match_inside_and_outside_brackets = re.compile(r'(.*)(\[[BRO]?\'[^\]]*\'\])$')
match_inside_brackets = re.compile(r'\[([BRO]?)\'([^\]]*)\'\]')
valid_python_var = re.compile(r'^[A-Za-z][A-Za-z0-9\_]*$')
valid_python_exp = re.compile(r'^[A-Za-z][A-Za-z0-9\_\.]*$')


def update_editable():
    try:
        if 'editable mimetypes' in daconfig and isinstance(daconfig['editable mimetypes'], list):
            for item in daconfig['editable mimetypes']:
                if isinstance(item, str):
                    ok_mimetypes[item] = 'null'
    except:
        pass

    try:
        if 'editable extensions' in daconfig and isinstance(daconfig['editable extensions'], list):
            for item in daconfig['editable extensions']:
                if isinstance(item, str):
                    ok_extensions[item] = 'null'
    except:
        pass

update_editable()


class Object:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property


def _get_safe_next_param(param_name, default_endpoint):
    if param_name in request.args:
        safe_next = current_app.user_manager.make_safe_url_function(urllibunquote(request.args[param_name]))
        # safe_next = request.args[param_name]
    else:
        safe_next = _endpoint_url(default_endpoint)
    return safe_next

def nginx_send_file(path, mimetype=None, as_attachment=False, download_name=None, max_age=None):
    headers = Headers()
    f_stat = os.stat(path)
    size = f_stat.st_size
    mtime = f_stat.st_mtime
    if download_name is None:
        download_name = os.path.basename(path)

    if mimetype is None:
        if download_name is None:
            raise TypeError(
                "Unable to detect the MIME type because a file name is"
                " not available. Either set 'download_name', pass a"
                " path instead of a file, or set 'mimetype'."
            )
        mimetype, encoding = mimetypes.guess_type(download_name)  # pylint: disable=unused-variable
        if mimetype is None:
            mimetype = "application/octet-stream"

    if download_name is not None:
        try:
            download_name.encode("ascii")
        except UnicodeEncodeError:
            simple = unicodedata.normalize("NFKD", download_name)
            simple = simple.encode("ascii", "ignore").decode("ascii")
            quoted = urllibquote(download_name, safe="!#$&+-.^_`|~")
            names = {"filename": simple, "filename*": f"UTF-8''{quoted}"}
        else:
            names = {"filename": download_name}
        value = "attachment" if as_attachment else "inline"
        headers.set("Content-Disposition", value, **names)
    elif as_attachment:
        raise TypeError(
            "No name provided for attachment. Either set"
            " 'download_name' or pass a path instead of a file."
        )
    headers['X-Accel-Redirect'] = '/xaccel' + path
    rv = Response(
        None, mimetype=mimetype, headers=headers, direct_passthrough=True
    )
    if size is not None:
        rv.content_length = size
    if mtime is not None:
        rv.last_modified = mtime
    rv.cache_control.no_cache = True
    if max_age is None:
        max_age = current_app.get_send_file_max_age(path)
    if max_age is not None:
        if max_age > 0:
            rv.cache_control.no_cache = None
            rv.cache_control.public = True
        rv.cache_control.max_age = max_age
        rv.expires = int(time.time() + max_age)
    return rv

if daconfig['web server'] == 'nginx' and daconfig.get('use nginx to serve files', False):
    custom_send_file = nginx_send_file
else:
    custom_send_file = send_file

mimetypes.add_type('application/x-yaml', '.yml')
mimetypes.add_type('application/x-yaml', '.yaml')

def add_secret_to(response):
    if 'newsecret' in session:
        if 'embed' in g:
            response.set_cookie('secret', session['newsecret'], httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite='None')
        else:
            response.set_cookie('secret', session['newsecret'], httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'])
        del session['newsecret']
    return response


def as_int(val):
    try:
        return int(val)
    except:
        return 0


def my_default_url(error, endpoint, values):  # pylint: disable=unused-argument
    return url_for('interview.index')


def make_safe_url(url):
    if url is None:
        return url
    parts = urlsplit(url)
    safe_url = parts.path
    if parts.query != '':
        safe_url += '?' + parts.query
    if parts.fragment != '':
        safe_url += '#' + parts.fragment
    if len(safe_url) > 0 and safe_url[0] not in ('?', '#', '/'):
        safe_url = '/' + safe_url
    safe_url = re.sub(r'^//+', '/', safe_url)
    return safe_url


def redis_script(data):
    js = f"Object.assign(window, {json.dumps(data)});"
    while True:
        random_key = str(uuid.uuid4())
        key = 'da:rjs:' + random_key
        with r.pipeline() as pipe:
            pipe.watch(key)
            if not pipe.exists(key):
                pipe.multi()
                pipe.set(key, js)
                pipe.expire(key, 60)
                pipe.execute()
                break
    return f'<script{DEFER} src="{url_for("main.rjs", key=random_key)}"></script>'


def url_for_interview(**args):
    for k, v in daconfig.get('dispatch').items():
        if v == args['i']:
            args['dispatch'] = k
            del args['i']
            is_new = False
            try:
                if true_or_false(args['new_session']):
                    is_new = True
                    del args['new_session']
            except:
                is_new = False
            if is_new:
                return url_of('run_new_dispatch', **args)
            return url_of('run_dispatch', **args)
    return url_for('interview.index', **args)


def manual_checkout(manual_session_id=None, manual_filename=None, user_id=None, delete_session=False, temp_user_id=None):
    if manual_filename is not None:
        yaml_filename = manual_filename
    else:
        yaml_filename = this_thread.current_info.get('yaml_filename', None)
    if yaml_filename is None:
        return
    if manual_session_id is not None:
        session_id = manual_session_id
    else:
        session_info = get_session(yaml_filename)
        if session_info is not None:
            session_id = session_info['uid']
        else:
            session_id = None
    if session_id is None:
        return
    if user_id is None:
        if temp_user_id is not None:
            the_user_id = 't' + str(temp_user_id)
        else:
            if current_user.is_anonymous:
                the_user_id = 't' + str(session.get('tempuser', None))
            else:
                the_user_id = current_user.id
    else:
        the_user_id = user_id
    if delete_session:
        if not (not current_user.is_anonymous and user_id != current_user.id):
            clear_specific_session(yaml_filename, session_id)
    endpart = ':uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    pipe = r.pipeline()
    pipe.expire('da:session' + endpart, 12)
    pipe.expire('da:html' + endpart, 12)
    pipe.expire('da:interviewsession' + endpart, 12)
    pipe.expire('da:ready' + endpart, 12)
    pipe.expire('da:block' + endpart, 12)
    pipe.execute()
    # r.publish('da:monitor', json.dumps({'messagetype': 'refreshsessions'}))
    # logmessage("Done checking out from " + endpart)




def do_redirect(url, is_ajax, is_json, js_target):
    if is_ajax:
        return jsonify(action='redirect', url=url, csrf_token=generate_csrf())
    if is_json:
        if re.search(r'\?', url):
            url = url + '&json=1'
        else:
            url = url + '?json=1'
    if js_target and 'js_target=' not in url:
        if re.search(r'\?', url):
            url = url + '&js_target=' + js_target
        else:
            url = url + '?js_target=' + js_target
    return redirect(url)


def do_refresh(is_ajax, yaml_filename):
    if is_ajax:
        return jsonify(action='refresh', csrf_token=generate_csrf())
    return redirect(url_for('interview.index', i=yaml_filename))


def standard_scripts(interview_language=DEFAULT_LANGUAGE, external=False):
    if interview_language in ('ar', 'az', 'bg', 'ca', 'cr', 'cs', 'da', 'de', 'el', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'gl', 'he', 'hu', 'id', 'it', 'ja', 'ka', 'kr', 'kz', 'lt', 'lv', 'ms', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'zh'):
        fileinput_locale = f'\n  <script{DEFER} src="{url_for("static", filename="bootstrap-fileinput/js/locales/" + interview_language + ".js", v=da_version, _external=external)}"></script>'
    else:
        fileinput_locale = ''
    return f'\n  <script{DEFER} src="{url_for("static", filename="app/bundle.min.js", v=da_version, _external=external)}"></script>{fileinput_locale}'


def additional_scripts(ga_ids, as_javascript=False):
    output = ''
    if google_api_key is not None:
        if USE_GOOGLE_PLACES_NEW_API:
            script_text = f"""\
    (g=>{{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={{}});var d=b.maps||(b.maps={{}}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${{c}}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))}})({{
      key: "{google_api_key}",
      v: "weekly",
    }});
"""
            if as_javascript:
                output += script_text
            else:
                output += f"""\
  <script>
    {script_text}
  </script>
"""
        else:
            region = google_config.get('region', None)
            if region is None:
                region = ''
            else:
                region = '&region=' + region
            url = json.dumps(f"https://maps.googleapis.com/maps/api/js?key={google_api_key}{region}&libraries=places&loading=async")
            if as_javascript:
                output += f"""\
    var daScript = document.createElement('script');
    daScript.src = {url};
    document.head.appendChild(daScript);
"""
            else:
                output += f"""
  <script async src={url}></script>"""
    if ga_ids is not None:
        if as_javascript:
            output += ""  # If embedding, Google Analytics needs to be handled by the host page.
        else:
            output += f"""
  <script defer src="https://www.googletagmanager.com/gtag/js?id={ga_ids[0]}"></script>
"""
    return output


def additional_css(interview_status, js_only=False):
    if 'segment id' in daconfig and interview_status.question.interview.options.get('analytics on', True):
        segment_id = daconfig['segment id']
    else:
        segment_id = None
    output = ''
    if segment_id is not None:
        segment_js = """\
      !function(){var analytics=window.analytics=window.analytics||[];if(!analytics.initialize)if(analytics.invoked)window.console&&console.error&&console.error("Segment snippet included twice.");else{analytics.invoked=!0;analytics.methods=["trackSubmit","trackClick","trackLink","trackForm","pageview","identify","reset","group","track","ready","alias","debug","page","once","off","on"];analytics.factory=function(t){return function(){var e=Array.prototype.slice.call(arguments);e.unshift(t);analytics.push(e);return analytics}};for(var t=0;t<analytics.methods.length;t++){var e=analytics.methods[t];analytics[e]=analytics.factory(e)}analytics.load=function(t,e){var n=document.createElement("script");n.type="text/javascript";n.async=!0;n.src="https://cdn.segment.com/analytics.js/v1/"+t+"/analytics.min.js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(n,a);analytics._loadOptions=e};analytics.SNIPPET_VERSION="4.1.0";
      analytics.load(""" + json.dumps(segment_id) + """);
      analytics.page();
      }}();
      function daSegmentEvent(){
        var idToUse = daQuestionID['id'];
        useArguments = false;
        if (daQuestionID['segment'] && daQuestionID['segment']['id']){
          idToUse = daQuestionID['segment']['id'];
          if (daQuestionID['segment']['arguments']){
            for (var keyToUse in daQuestionID['segment']['arguments']){
              if (daQuestionID['segment']['arguments'].hasOwnProperty(keyToUse)){
                useArguments = true;
                break;
              }
            }
          }
        }
        if (idToUse != null){
          if (useArguments){
            analytics.track(idToUse.replace(/[^A-Za-z0-9]+/g, '_'), daQuestionID['segment']['arguments']);
          }
          else{
            analytics.track(idToUse.replace(/[^A-Za-z0-9]+/g, '_'));
          }
        }
      }
"""
        if js_only:
            return segment_js
        output += f"""
    <script{DEFER}>
{segment_js}
    </script>"""
    elif js_only:
        return ''
    if len(interview_status.extra_css) > 0:
        output += '\n' + indent_by("".join(interview_status.extra_css).strip(), 4).rstrip()
    return output


def standard_html_start(interview_language=DEFAULT_LANGUAGE, debug=False, bootstrap_theme=None, external=False, page_title=None, social=None, yaml_filename=None):
    if social is None:
        social = {}
    if page_title is None:
        page_title = current_app.config['BRAND_NAME']
    if bootstrap_theme is None and current_app.config['BOOTSTRAP_THEME'] is not None:
        bootstrap_theme = current_app.config['BOOTSTRAP_THEME']
    if bootstrap_theme is None:
        bootstrap_part = '\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap.min.css', v=da_version, _external=external) + '" rel="stylesheet">'
    else:
        bootstrap_part = '\n    <link href="' + bootstrap_theme + '" rel="stylesheet">'
    if session.get('color_scheme', 0):
        color_scheme_part = ' data-bs-theme="dark"'
    else:
        color_scheme_part = ''
    output = '<!DOCTYPE html>\n<html lang="' + interview_language + '" itemscope itemtype="http://schema.org/WebPage"' + color_scheme_part + '>\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    ' + ('<link rel="shortcut icon" href="' + url_for('main.favicon', _external=external, **current_app.config['FAVICON_PARAMS']) + '">\n    ' if current_app.config['USE_FAVICON'] else '') + ('<link rel="apple-touch-icon" sizes="180x180" href="' + url_for('main.apple_touch_icon', _external=external, **current_app.config['FAVICON_PARAMS']) + '">\n    ' if current_app.config['USE_APPLE_TOUCH_ICON'] else '') + ('<link rel="icon" type="image/png" href="' + url_for('main.favicon_md', _external=external, **current_app.config['FAVICON_PARAMS']) + '" sizes="32x32">\n    ' if current_app.config['USE_FAVICON_MD'] else '') + ('<link rel="icon" type="image/png" href="' + url_for('main.favicon_sm', _external=external, **current_app.config['FAVICON_PARAMS']) + '" sizes="16x16">\n    ' if current_app.config['USE_FAVICON_SM'] else '') + ('<link rel="manifest" href="' + url_for('main.favicon_site_webmanifest', _external=external, **current_app.config['FAVICON_PARAMS']) + '">\n    ' if current_app.config['USE_SITE_WEBMANIFEST'] else '') + ('<link rel="mask-icon" href="' + url_for('main.favicon_safari_pinned_tab', _external=external, **current_app.config['FAVICON_PARAMS']) + '" color="' + current_app.config['FAVICON_MASK_COLOR'] + '">\n    ' if current_app.config['USE_SAFARI_PINNED_TAB'] else '') + '<meta name="msapplication-TileColor" content="' + current_app.config['FAVICON_TILE_COLOR'] + '">\n    <meta name="theme-color" content="' + current_app.config['FAVICON_THEME_COLOR'] + '">\n    <script defer src="' + url_for('static', filename='fontawesome/js/all.min.js', v=da_version, _external=external) + '"></script>' + bootstrap_part + '\n    <link href="' + url_for('static', filename='app/bundle.css', v=da_version, _external=external) + '" rel="stylesheet">'
    if debug:
        output += '\n    <link href="' + url_for('static', filename='app/pygments.min.css', v=da_version, _external=external) + '" rel="stylesheet">'
    page_title = page_title.replace('\n', ' ').replace('"', '&quot;').strip()
    for key, val in social.items():
        if key not in ('twitter', 'og', 'fb'):
            output += '\n    <meta name="' + key + '" content="' + social[key] + '">'
    if 'description' in social:
        output += '\n    <meta itemprop="description" content="' + social['description'] + '">'
    if 'image' in social:
        output += '\n    <meta itemprop="image" content="' + social['image'] + '">'
    if 'name' in social:
        output += '\n    <meta itemprop="name" content="' + social['name'] + '">'
    else:
        output += '\n    <meta itemprop="name" content="' + page_title + '">'
    if 'twitter' in social:
        if 'card' not in social['twitter']:
            output += '\n    <meta name="twitter:card" content="summary">'
        for key, val in social['twitter'].items():
            output += '\n    <meta name="twitter:' + key + '" content="' + val + '">'
        if 'title' not in social['twitter']:
            output += '\n    <meta name="twitter:title" content="' + page_title + '">'
    if 'fb' in social:
        for key, val in social['fb'].items():
            output += '\n    <meta name="fb:' + key + '" content="' + val + '">'
    if 'og' in social and 'image' in social['og']:
        for key, val in social['og'].items():
            output += '\n    <meta name="og:' + key + '" content="' + val + '">'
        if 'title' not in social['og']:
            output += '\n    <meta name="og:title" content="' + page_title + '">'
        if yaml_filename and 'url' not in social['og']:
            output += '\n    <meta name="og:url" content="' + url_for('interview.index', i=yaml_filename, _external=True) + '">'
        if 'site_name' not in social['og']:
            output += '\n    <meta name="og:site_name" content="' + current_app.config['BRAND_NAME'].replace('\n', ' ').replace('"', '&quot;').strip() + '">'
        if 'locale' not in social['og']:
            output += '\n    <meta name="og:locale" content="' + current_app.config['OG_LOCALE'] + '">'
        if 'type' not in social['og']:
            output += '\n    <meta name="og:type" content="website">'
    return output


def process_file(saved_file, orig_file, mimetype, extension, initial=True):
    if extension == "gif" and daconfig.get('imagemagick', 'convert') is not None:
        unconverted = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".gif", delete=False)
        converted = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".png", delete=False)
        shutil.move(orig_file, unconverted.name)
        call_array = [daconfig.get('imagemagick', 'convert'), str(unconverted.name), 'png:' + converted.name]
        try:
            result = subprocess.run(call_array, timeout=60, check=False).returncode
        except subprocess.TimeoutExpired:
            logmessage("process_file: convert from gif took too long")
            result = 1
        if result == 0:
            saved_file.copy_from(converted.name, filename=re.sub(r'\.[^\.]+$', '', saved_file.filename) + '.png')
        else:
            logmessage("process_file: error converting from gif to png")
        shutil.move(unconverted.name, saved_file.path)
        saved_file.save()
    elif extension == "jpg" and daconfig.get('imagemagick', 'convert') is not None:
        unrotated = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".jpg", delete=False)
        rotated = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".jpg", delete=False)
        shutil.move(orig_file, unrotated.name)
        call_array = [daconfig.get('imagemagick', 'convert'), str(unrotated.name), '-auto-orient', '-density', '300', 'jpeg:' + rotated.name]
        try:
            result = subprocess.run(call_array, timeout=60, check=False).returncode
        except subprocess.TimeoutExpired:
            logmessage("process_file: convert from jpeg took too long")
            result = 1
        if result == 0:
            saved_file.copy_from(rotated.name)
        else:
            saved_file.copy_from(unrotated.name)
    elif initial:
        shutil.move(orig_file, saved_file.path)
        saved_file.save()
    # if mimetype == 'video/quicktime' and daconfig.get('ffmpeg', 'ffmpeg') is not None:
    #     call_array = [daconfig.get('ffmpeg', 'ffmpeg'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
    #     try:
    #         result = subprocess.run(call_array, timeout=120).returncode
    #     except subprocess.TimeoutExpired:
    #         result = 1
    #     call_array = [daconfig.get('ffmpeg', 'ffmpeg'), '-i', saved_file.path + '.' + extension, '-vcodec', 'copy', '-acodec', 'copy', saved_file.path + '.mp4']
    #     try:
    #         result = subprocess.run(call_array, timeout=120).returncode
    #     except subprocess.TimeoutExpired:
    #         result = 1
    # if mimetype == 'video/mp4' and daconfig.get('ffmpeg', 'ffmpeg') is not None:
    #     call_array = [daconfig.get('ffmpeg', 'ffmpeg'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
    #     try:
    #         result = subprocess.run(call_array, timeout=120).returncode
    #     except subprocess.TimeoutExpired:
    #         result = 1
    # if mimetype == 'video/ogg' and daconfig.get('ffmpeg', 'ffmpeg') is not None:
    #     call_array = [daconfig.get('ffmpeg', 'ffmpeg'), '-i', saved_file.path + '.' + extension, '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '22', '-c:a', 'libmp3lame', '-qscale:a', '2', '-ac', '2', '-ar', '44100', saved_file.path + '.mp4']
    #     try:
    #         result = subprocess.run(call_array, timeout=120).returncode
    #     except subprocess.TimeoutExpired:
    #         result = 1
    # if mimetype == 'audio/mpeg' and daconfig.get('pacpl', 'pacpl') is not None:
    #     call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
    #     try:
    #         result = subprocess.run(call_array, timeout=120).returncode
    #     except subprocess.TimeoutExpired:
    #         result = 1
    if mimetype == 'audio/ogg' and daconfig.get('pacpl', 'pacpl') is not None:
        call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
        try:
            result = subprocess.run(call_array, timeout=120, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
    if mimetype == 'audio/3gpp' and daconfig.get('ffmpeg', 'ffmpeg') is not None:
        call_array = [daconfig.get('ffmpeg', 'ffmpeg'), '-i', saved_file.path + '.' + extension, saved_file.path + '.ogg']
        try:
            result = subprocess.run(call_array, timeout=120, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
        call_array = [daconfig.get('ffmpeg', 'ffmpeg'), '-i', saved_file.path + '.' + extension, saved_file.path + '.mp3']
        try:
            result = subprocess.run(call_array, timeout=120, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
    if mimetype in ('audio/x-wav', 'audio/wav') and daconfig.get('pacpl', 'pacpl') is not None:
        call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
        try:
            result = subprocess.run(call_array, timeout=120, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
        call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
        try:
            result = subprocess.run(call_array, timeout=120, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
    # if extension == "pdf":
    #    make_image_files(saved_file.path)
    saved_file.finalize()




def process_bracket_expression(match):
    if match.group(1) in ('B', 'R', 'O'):
        try:
            inner = codecs.decode(repad(bytearray(match.group(2), encoding='utf-8')), 'base64').decode('utf-8')
        except:
            inner = match.group(2)
    else:
        inner = match.group(2)
    return "[" + repr(inner) + "]"


def myb64unquote(the_string):
    return codecs.decode(repad(bytearray(the_string, encoding='utf-8')), 'base64').decode('utf-8')


def safeid(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())


def from_safeid(text):
    return codecs.decode(repad(bytearray(text, encoding='utf-8')), 'base64').decode('utf-8')


def repad(text):
    return text + (equals_byte * ((4 - len(text) % 4) % 4))


def test_for_valid_var(varname):
    if not valid_python_var.match(varname):
        raise DAError(varname + " is not a valid name.  A valid name consists only of letters, numbers, and underscores, and begins with a letter.")

@hookimpl(specname='navigation_bar')
def navigation_bar_adapter(nav, interview, wrapper, inner_div_class, inner_div_extra, show_links, hide_inactive_subs, a_class, show_nesting, include_arrows, always_open, return_dict):
    return navigation_bar(nav, interview, wrapper=wrapper, inner_div_class=inner_div_class, inner_div_extra=inner_div_extra, show_links=show_links, hide_inactive_subs=hide_inactive_subs, a_class=a_class, show_nesting=show_nesting, include_arrows=include_arrows, always_open=always_open, return_dict=return_dict)

def navigation_bar(nav, interview, wrapper=True, inner_div_class=None, inner_div_extra=None, show_links=None, hide_inactive_subs=True, a_class=None, show_nesting=True, include_arrows=False, always_open=False, return_dict=None):
    if show_links is None:
        show_links = not bool(hasattr(nav, 'disabled') and nav.disabled)
    if inner_div_class is None:
        inner_div_class = 'nav flex-column nav-pills danav danavlinks danav-vertical danavnested'
    if inner_div_extra is None:
        inner_div_extra = ''
    if a_class is None:
        a_class = 'nav-link danavlink'
        muted_class = ' text-body-secondary'
    else:
        muted_class = ''
    # logmessage("navigation_bar: starting: " + str(section))
    the_language = get_language()
    non_progressive = bool(hasattr(nav, 'progressive') and not nav.progressive)
    auto_open = bool(always_open or (hasattr(nav, 'auto_open') and nav.auto_open))
    if the_language not in nav.sections:
        the_language = DEFAULT_LANGUAGE
    if the_language not in nav.sections:
        the_language = '*'
    if the_language not in nav.sections:
        return ''
        # raise DAError("Could not find a navigation bar to display.  " + str(nav.sections))
    the_sections = nav.sections[the_language]
    if len(the_sections) == 0:
        return ''
    if this_thread.current_question.section is not None and this_thread.current_section:
        the_section = this_thread.current_section
    else:
        the_section = nav.current
    # logmessage("Current section is " + repr(the_section))
    # logmessage("Past sections are: " + str(nav.past))
    if the_section is None:
        if isinstance(the_sections[0], dict):
            the_section = list(the_sections[0])[0]
        else:
            the_section = the_sections[0]
    if wrapper:
        output = '<div role="navigation" class="' + daconfig['grid classes']['vertical navigation']['bar'] + ' d-none d-md-block danavdiv">\n  <div class="nav flex-column nav-pills danav danav-vertical danavlinks">\n'
    else:
        output = ''
    section_reached = False
    indexno = 0
    seen = set()
    on_first = True
    # logmessage("Sections is " + repr(the_sections))
    for x in the_sections:
        if include_arrows and not on_first:
            output += '<span class="dainlinearrow"><i class="fa-solid fa-chevron-right"></i></span>'
        on_first = False
        indexno += 1
        the_key = None
        subitems = None
        currently_active = False
        if isinstance(x, dict):
            # logmessage("It is a dict")
            if len(x) == 2 and 'subsections' in x:
                for key, val in x.items():
                    if key == 'subsections':
                        subitems = val
                    else:
                        the_key = key
                        test_for_valid_var(the_key)
                        the_title = val
            elif len(x) == 1:
                # logmessage("The len is one")
                the_key = list(x)[0]
                value = x[the_key]
                if isinstance(value, list):
                    subitems = value
                    the_title = the_key
                else:
                    test_for_valid_var(the_key)
                    the_title = value
            else:
                raise DAError("navigation_bar: too many keys in dict.  " + str(the_sections))
        else:
            # logmessage("It is not a dict")
            the_key = None
            the_title = str(x)
        if (the_key is not None and the_section == the_key) or the_section == the_title:
            # output += '<li role="presentation" class="' + li_class + ' active">'
            section_reached = True
            currently_active = True
            active_class = ' active'
            if return_dict is not None:
                return_dict['parent_key'] = the_key
                return_dict['parent_title'] = the_title
                return_dict['key'] = the_key
                return_dict['title'] = the_title
        else:
            active_class = ''
            # output += '<li class="' + li_class + '" role="presentation">'
        new_key = the_title if the_key is None else the_key
        seen.add(new_key)
        # logmessage("new_key is: " + str(new_key))
        # logmessage("seen sections are: " + str(seen))
        # logmessage("nav past sections are: " + repr(nav.past))
        relevant_past = nav.past.intersection(set(nav.section_ids()))
        seen_more = bool(len(relevant_past.difference(seen)) > 0 or new_key in nav.past or the_title in nav.past)
        if non_progressive:
            seen_more = True
            section_reached = False
        # logmessage("the title is " + str(the_title) + " and non_progressive is " + str(non_progressive) + " and show links is " + str(show_links) + " and seen_more is " + str(seen_more) + " and active_class is " + repr(active_class) + " and currently_active is " + str(currently_active) + " and section_reached is " + str(section_reached) + " and the_key is " + str(the_key) + " and interview is " + str(interview) + " and in q is " + ('in q' if the_key in interview.questions else 'not in q'))
        if show_links and (seen_more or currently_active or not section_reached) and the_key is not None and interview is not None and the_key in interview.questions:
            # url = interview_url_action(the_key)
            if section_reached and not currently_active and not seen_more:
                output += '<span tabindex="-1" data-index="' + str(indexno) + '" class="' + a_class + ' danotavailableyet' + muted_class + '">' + str(the_title) + '</span>'
            else:
                if active_class == '' and not section_reached and not seen_more:
                    output += '<span tabindex="-1" data-index="' + str(indexno) + '" class="' + a_class + ' inactive' + muted_class + '">' + str(the_title) + '</span>'
                else:
                    output += '<a href="#" data-key="' + the_key + '" data-index="' + str(indexno) + '" class="daclickable ' + a_class + active_class + '">' + str(the_title) + '</a>'
        else:
            if section_reached and not currently_active and not seen_more:
                output += '<span tabindex="-1" data-index="' + str(indexno) + '" class="' + a_class + ' danotavailableyet' + muted_class + '">' + str(the_title) + '</span>'
            else:
                if active_class == '' and not section_reached and not seen_more:
                    output += '<span tabindex="-1" data-index="' + str(indexno) + '" class="' + a_class + ' inactive' + muted_class + '">' + str(the_title) + '</span>'
                else:
                    output += '<a tabindex="-1" data-index="' + str(indexno) + '" class="' + a_class + active_class + '">' + str(the_title) + '</a>'
        suboutput = ''
        if subitems:
            current_is_within = False
            oldindexno = indexno
            for y in subitems:
                if include_arrows:
                    suboutput += '<span class="dainlinearrow"><i class="fa-solid fa-chevron-right"></i></span>'
                indexno += 1
                sub_currently_active = False
                if isinstance(y, dict):
                    if len(y) == 1:
                        sub_key = list(y)[0]
                        test_for_valid_var(sub_key)
                        sub_title = y[sub_key]
                    else:
                        raise DAError("navigation_bar: too many keys in dict.  " + str(the_sections))
                else:
                    sub_key = None
                    sub_title = str(y)
                if (sub_key is not None and the_section == sub_key) or the_section == sub_title:
                    # suboutput += '<li class="' + li_class + ' active" role="presentation">'
                    section_reached = True
                    current_is_within = True
                    sub_currently_active = True
                    sub_active_class = ' active'
                    if return_dict is not None:
                        return_dict['key'] = sub_key
                        return_dict['title'] = sub_title
                else:
                    sub_active_class = ''
                    # suboutput += '<li class="' + li_class + '" role="presentation">'
                new_sub_key = sub_title if sub_key is None else sub_key
                seen.add(new_sub_key)
                # logmessage("sub: seen sections are: " + str(seen))
                relevant_past = nav.past.intersection(set(nav.section_ids()))
                seen_more = bool(len(relevant_past.difference(seen)) > 0 or new_sub_key in nav.past or sub_title in nav.past)
                if non_progressive:
                    # logmessage("Setting seen_more to True bc non-progressive")
                    seen_more = True
                    section_reached = False
                # logmessage("First sub is %s, indexno is %d, sub_currently_active is %s, sub_key is %s, sub_title is %s, section_reached is %s, current_is_within is %s, sub_active_class is %s, new_sub_key is %s, seen_more is %s, section_reached is %s, show_links is %s" % (str(first_sub), indexno, str(sub_currently_active), sub_key, sub_title, section_reached, current_is_within, sub_active_class, new_sub_key, str(seen_more), str(section_reached), str(show_links)))
                if show_links and (seen_more or sub_currently_active or not section_reached) and sub_key is not None and interview is not None and sub_key in interview.questions:
                    # url = interview_url_action(sub_key)
                    suboutput += '<a href="#" data-key="' + sub_key + '" data-index="' + str(indexno) + '" class="daclickable ' + a_class + sub_active_class + '">' + str(sub_title) + '</a>'
                else:
                    if section_reached and not sub_currently_active and not seen_more:
                        suboutput += '<span tabindex="-1" data-index="' + str(indexno) + '" class="' + a_class + ' danotavailableyet' + muted_class + '">' + str(sub_title) + '</span>'
                    else:
                        suboutput += '<a tabindex="-1" data-index="' + str(indexno) + '" class="' + a_class + sub_active_class + ' inactive">' + str(sub_title) + '</a>'
                # suboutput += "</li>"
            if currently_active or current_is_within or hide_inactive_subs is False or show_nesting:
                if currently_active or current_is_within or auto_open:
                    suboutput = '<div class="' + inner_div_class + '"' + inner_div_extra + '>' + suboutput
                else:
                    suboutput = '<div style="display: none;" class="danotshowing ' + inner_div_class + '"' + inner_div_extra + '>' + suboutput
                suboutput += "</div>"
                output += suboutput
            else:
                indexno = oldindexno
        # output += "</li>"
    if wrapper:
        output += "\n</div>\n</div>\n"
    if (not non_progressive) and (not section_reached):
        logmessage("Section \"" + str(the_section) + "\" did not exist.")
    return output


def progress_bar(progress, interview):
    if progress is None:
        return ''
    progress = float(progress)
    if progress <= 0:
        return ''
    progress = min(progress, 100)
    if hasattr(interview, 'show_progress_bar_percentage') and interview.show_progress_bar_percentage:
        percentage = str(int(progress)) + '%'
    else:
        percentage = ''
    return '<div class="progress mt-2" role="progressbar" aria-label="' + noquote(word('Interview Progress')) + '" aria-valuenow="' + str(progress) + '" aria-valuemin="0" aria-valuemax="100"><div class="progress-bar" style="width: ' + str(progress) + '%;">' + percentage + '</div></div>\n'


def make_navbar(status, steps, show_login, chat_info, debug_mode, index_params, extra_class=None):  # pylint: disable=unused-argument
    if 'inverse navbar' in status.question.interview.options:
        if status.question.interview.options['inverse navbar']:
            inverse = 'bg-dark'
            theme = 'dark'
        else:
            inverse = 'bg-body-tertiary'
            theme = 'light'
    elif daconfig.get('inverse navbar', True):
        inverse = 'bg-dark'
        theme = 'dark'
    else:
        inverse = 'bg-body-tertiary'
        theme = 'light'
    if 'jsembed' in this_thread.misc:
        fixed_top = ''
    else:
        fixed_top = ' fixed-top'
    if extra_class is not None:
        fixed_top += ' ' + extra_class
    navbar = """\
    <div class="danavbarcontainer" data-bs-theme=""" + '"' + theme + '"' + """>
      <div class="navbar""" + fixed_top + """ navbar-expand-md """ + inverse + '"' + """ role="banner">
        <div class="container danavcontainer justify-content-start">
"""
    if status.extras['can_go_back'] and steps > 1:
        if status.question.interview.navigation_back_button:
            navbar += """\
          <form style="display: inline-block" id="dabackbutton" method="POST" action=""" + json.dumps(url_for('interview.index', **index_params)) + """><input type="hidden" name="csrf_token" value=""" + '"' + generate_csrf() + '"' + """/><input type="hidden" name="_back_one" value="1"/><button class="navbar-brand navbar-nav dabackicon dabackbuttoncolor me-3" type="submit" title=""" + json.dumps(word("Go back to the previous question")) + """><span class="nav-link"><i class="fa-solid fa-chevron-left"></i><span class="daback">""" + status.cornerback + """</span></span></button></form>
"""
        else:
            navbar += """\
          <form hidden style="display: inline-block" id="dabackbutton" method="POST" action=""" + json.dumps(url_for('interview.index', **index_params)) + """><input type="hidden" name="csrf_token" value=""" + '"' + generate_csrf() + '"' + """/><input type="hidden" name="_back_one" value="1"/></form>
"""
    if status.title_url:
        if str(status.title_url_opens_in_other_window) == 'False':
            target = ''
        else:
            target = ' target="_blank"'
        navbar += """\
          <a id="dapagetitle" class="navbar-brand danavbar-title dapointer" href=""" + '"' + status.title_url + '"' + target + """><span class="d-none d-lg-block">""" + status.display_title + """</span><span class="d-block d-lg-none">""" + status.display_short_title + """</span></a>
"""
    else:
        navbar += """\
          <span id="dapagetitle" class="navbar-brand danavbar-title"><span class="d-none d-lg-block">""" + status.display_title + """</span><span class="d-block d-lg-none">""" + status.display_short_title + """</span></span>
"""
    help_message = word("Help is available")
    help_label = None
    if status.question.interview.question_help_button:
        the_sections = status.interview_help_text
    else:
        the_sections = status.help_text + status.interview_help_text
    for help_section in the_sections:
        if help_section['label']:
            help_label = help_section['label']
            break
    if help_label is None:
        help_label = status.extras.get('help label text', None)
    if help_label is None:
        help_label = status.question.help()
    extra_help_message = word("Help is available for this question")
    phone_sr = word("Phone help")
    phone_message = word("Phone help is available")
    chat_sr = word("Live chat")
    source_message = word("Information for the developer")
    if debug_mode:
        source_button = '<div class="nav-item navbar-nav d-none d-md-block"><button class="btn btn-link nav-link da-no-outline" title=' + json.dumps(source_message) + ' id="dasourcetoggle" data-bs-toggle="collapse" data-bs-target="#dasource"><i class="fa-solid fa-code"></i></button></div>'
        source_menu_item = '<a class="dropdown-item d-block d-lg-none" title=' + json.dumps(source_message) + ' href="#dasource" data-bs-toggle="collapse" aria-expanded="false" aria-controls="source">' + word('Source') + '</a>'
    else:
        source_button = ''
        source_menu_item = ''
    hidden_question_button = '<li class="nav-item visually-hidden-focusable"><button class="btn btn-link nav-link active da-no-outline" id="daquestionlabel" data-bs-toggle="tab" data-bs-target="#daquestion">' + word('Question') + '</button></li>'
    navbar += '          ' + source_button + '<ul id="nav-bar-tab-list" class="nav navbar-nav damynavbar-right" role="tablist">' + hidden_question_button
    if len(status.interview_help_text) > 0 or (len(status.help_text) > 0 and not status.question.interview.question_help_button):
        if status.question.helptext is None or status.question.interview.question_help_button:
            navbar += '<li class="nav-item" role="presentation"><button class="btn btn-link nav-link dahelptrigger da-no-outline" data-bs-target="#dahelp" data-bs-toggle="tab" role="tab" id="dahelptoggle" title=' + json.dumps(help_message) + '>' + help_label + '</button></li>'
        else:
            navbar += '<li class="nav-item" role="presentation"><button class="btn btn-link nav-link dahelptrigger da-no-outline daactivetext" data-bs-target="#dahelp" data-bs-toggle="tab" role="tab" id="dahelptoggle" title=' + json.dumps(extra_help_message) + '>' + help_label + ' <i class="fa-solid fa-star"></i></button></li>'
    else:
        navbar += '<li hidden class="nav-item dainvisible" role="presentation"><button class="btn btn-link nav-link dahelptrigger da-no-outline" id="dahelptoggle" data-bs-target="#dahelp" data-bs-toggle="tab" role="tab">' + word('Help') + '</button></li>'
    navbar += '<li hidden class="nav-item dainvisible" id="daPhoneAvailable"><button data-bs-target="#dahelp" data-bs-toggle="tab" role="tab" title=' + json.dumps(phone_message) + ' class="btn btn-link nav-link dapointer dahelptrigger da-no-outline"><i class="fa-solid fa-phone da-chat-active"></i><span class="visually-hidden">' + phone_sr + '</span></button></li>' + \
              '<li class="nav-item dainvisible" id="daChatAvailable"><button data-bs-target="#dahelp" data-bs-toggle="tab" class="btn btn-link nav-link dapointer dahelptrigger da-no-outline"><i class="fa-solid fa-comment-alt"></i><span class="visually-hidden">' + chat_sr + '</span></button></li></ul>'
    if not status.question.interview.options.get('hide corner interface', False):
        navbar += """
          <button id="damobile-toggler" type="button" class="navbar-toggler ms-auto" data-bs-toggle="collapse" data-bs-target="#danavbar-collapse">
            <span class="navbar-toggler-icon"></span><span class="visually-hidden">""" + word("Display the menu") + """</span>
          </button>
          <div class="collapse navbar-collapse" id="danavbar-collapse">
            <ul class="navbar-nav ms-auto">
"""
        navbar += status.nav_item
        if 'menu_items' in status.extras:
            if not isinstance(status.extras['menu_items'], list):
                custom_menu = '<a tabindex="-1" class="dropdown-item">' + word("Error: menu_items is not a Python list") + '</a>'
            elif len(status.extras['menu_items']) > 0:
                custom_menu = ""
                for menu_item in status.extras['menu_items']:
                    if not (isinstance(menu_item, dict) and 'url' in menu_item and 'label' in menu_item):
                        custom_menu += '<a tabindex="-1" class="dropdown-item">' + word("Error: menu item is not a Python dict with keys of url and label") + '</li>'
                    else:
                        screen_size = menu_item.get('screen_size', '')
                        if screen_size == 'small':
                            menu_item_classes = ' d-block d-md-none'
                        elif screen_size == 'large':
                            menu_item_classes = ' d-none d-md-block'
                        else:
                            menu_item_classes = ''
                        match_action = re.search(r'\?action=([^\&]+)', menu_item['url'])
                        if match_action:
                            custom_menu += '<a class="dropdown-item' + menu_item_classes + '" data-embaction="' + match_action.group(1) + '" href="' + menu_item['url'] + '">' + menu_item['label'] + '</a>'
                        else:
                            custom_menu += '<a class="dropdown-item' + menu_item_classes + '" href="' + menu_item['url'] + '">' + menu_item['label'] + '</a>'
            else:
                custom_menu = ""
        else:
            custom_menu = ""
        if ALLOW_REGISTRATION:
            sign_in_text = word('Sign in or sign up to save answers')
            if daconfig.get('resume interview after login', False):
                register_url = url_for('user.register', next=url_for('interview.index', **index_params))
            else:
                register_url = url_for('user.register')
        else:
            sign_in_text = word('Sign in to save answers')
        if daconfig.get('resume interview after login', False):
            login_url = url_for('user.login', next=url_for('interview.index', **index_params))
        else:
            login_url = url_for('user.login')
        admin_menu = ''
        if not status.question.interview.options.get('hide standard menu', False):
            for item in current_app.config['ADMIN_INTERVIEWS']:
                if item.can_use() and item.is_not(this_thread.current_info.get('yaml_filename', '')):
                    admin_menu += '<a class="dropdown-item" href="' + item.get_url() + '">' + item.get_title(get_language()) + '</a>'
        if show_login:
            if current_user.is_anonymous:
                if custom_menu or admin_menu:
                    navbar += '              <li class="nav-item dropdown"><a href="#" class="nav-link dropdown-toggle d-none d-md-block" data-bs-toggle="dropdown" role="button" id="damenuLabel" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '</a><div class="dropdown-menu dropdown-menu-end" aria-labelledby="damenuLabel">' + custom_menu + admin_menu + '<a class="dropdown-item" href="' + login_url + '">' + sign_in_text + '</a></div></li>'
                else:
                    if daconfig.get('login link style', 'normal') == 'button':
                        if ALLOW_REGISTRATION:
                            navbar += '              <li class="nav-item"><a class="nav-link d-block d-md-none" href="' + register_url + '">' + word('Sign up') + '</a></li>'
                        navbar += '              <li class="nav-item"><a class="nav-link d-block d-md-none" href="' + login_url + '">' + word('Sign in') + '</a>'
                    else:
                        navbar += '              <li class="nav-item"><a class="nav-link" href="' + login_url + '">' + sign_in_text + '</a></li>'
            elif current_user.is_authenticated:
                if custom_menu == '' and status.question.interview.options.get('hide standard menu', False):
                    navbar += '              <li class="nav-item"><a class="nav-link" tabindex="-1">' + (current_user.email if current_user.email else re.sub(r'.*\$', '', current_user.social_id)) + '</a></li>'
                else:
                    navbar += '              <li class="nav-item dropdown"><a class="nav-link dropdown-toggle d-none d-md-block" href="#" data-bs-toggle="dropdown" role="button" id="damenuLabel" aria-haspopup="true" aria-expanded="false">' + (current_user.email if current_user.email else re.sub(r'.*\$', '', current_user.social_id)) + '</a><div class="dropdown-menu dropdown-menu-end" aria-labelledby="damenuLabel">'
                    if custom_menu:
                        navbar += custom_menu
                    if not status.question.interview.options.get('hide standard menu', False):
                        if current_user.has_role('admin', 'developer'):
                            navbar += source_menu_item
                        if current_user.has_role('admin', 'advocate') and current_app.config['ENABLE_MONITOR']:
                            navbar += '<a class="dropdown-item" href="' + url_for('monitor.monitor') + '">' + word('Monitor') + '</a>'
                        if current_user.has_role('admin', 'developer', 'trainer') and current_app.config['ENABLE_TRAINING']:
                            navbar += '<a class="dropdown-item" href="' + url_for('ml.train') + '">' + word('Train') + '</a>'
                        if current_user.has_role('admin', 'developer'):
                            if current_app.config['ALLOW_UPDATES'] and (current_app.config['DEVELOPER_CAN_INSTALL'] or current_user.has_role('admin')):
                                navbar += '<a class="dropdown-item" href="' + url_for('packages.update_package') + '">' + word('Package Management') + '</a>'
                            if current_app.config['ALLOW_LOG_VIEWING']:
                                navbar += '<a class="dropdown-item" href="' + url_for('logs.logs') + '">' + word('Logs') + '</a>'
                            if current_app.config['ENABLE_PLAYGROUND']:
                                navbar += '<a class="dropdown-item" href="' + url_for('develop.playground_page') + '">' + word('Playground') + '</a>'
                            navbar += '<a class="dropdown-item" href="' + url_for('develop.utilities') + '">' + word('Utilities') + '</a>'
                        if current_user.has_role('admin', 'advocate') or current_user.can_do('access_user_info'):
                            navbar += '<a class="dropdown-item" href="' + url_for('users.user_list') + '">' + word('User List') + '</a>'
                        if current_user.has_role('admin') and current_app.config['ALLOW_CONFIGURATION_EDITING']:
                            navbar += '<a class="dropdown-item" href="' + url_for('admin.config_page') + '">' + word('Configuration') + '</a>'
                        if current_app.config['SHOW_DISPATCH']:
                            navbar += '<a class="dropdown-item" href="' + url_for('admin.interview_start') + '">' + word('Available Interviews') + '</a>'
                        navbar += admin_menu
                        if current_app.config['SHOW_MY_INTERVIEWS'] or current_user.has_role('admin'):
                            navbar += '<a class="dropdown-item" href="' + url_for('admin.interview_list') + '">' + word('My Interviews') + '</a>'
                        if current_user.has_role('admin', 'developer'):
                            navbar += '<a class="dropdown-item" href="' + url_for('users.user_profile_page') + '">' + word('Profile') + '</a>'
                        else:
                            if current_app.config['SHOW_PROFILE'] or current_user.has_role('admin', 'developer'):
                                navbar += '<a class="dropdown-item" href="' + url_for('users.user_profile_page') + '">' + word('Profile') + '</a>'
                            elif current_user.social_id.startswith('local') and current_app.config['ALLOW_CHANGING_PASSWORD']:
                                navbar += '<a class="dropdown-item" href="' + url_for('user.change_password') + '">' + word('Change Password') + '</a>'
                        navbar += '<a class="dropdown-item" href="' + url_for('user.logout') + '">' + word('Sign Out') + '</a>'
                    navbar += '</div></li>'
        else:
            if custom_menu or admin_menu:
                navbar += '              <li class="nav-item dropdown"><a class="nav-link dropdown-toggle" href="#" class="dropdown-toggle d-none d-md-block" data-bs-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '</a><div class="dropdown-menu dropdown-menu-end">' + custom_menu + admin_menu
                if not status.question.interview.options.get('hide standard menu', False):
                    navbar += '<a class="dropdown-item" href="' + exit_href() + '">' + status.exit_label + '</a>'
                navbar += '</div></li>'
            else:
                navbar += '              <li class="nav-item"><a class="nav-link" href="' + exit_href() + '">' + status.exit_label + '</a></li>'
        navbar += """
            </ul>"""
        if daconfig.get('login link style', 'normal') == 'button' and show_login and current_user.is_anonymous and not custom_menu:
            if ALLOW_REGISTRATION:
                navbar += '\n            <a class="btn btn-' + BUTTON_COLOR_NAV_LOGIN + ' btn-sm mb-0 ms-3 d-none d-md-block" href="' + register_url + '">' + word('Sign up') + '</a>'
            navbar += '\n            <a class="btn btn-' + BUTTON_COLOR_NAV_LOGIN + ' btn-sm mb-0 ms-3 d-none d-md-block" href="' + login_url + '">' + word('Sign in') + '</a>'
        navbar += """
          </div>"""
    else:
        if status.nav_item:
            navbar += '<ul class="navbar-nav ms-auto">' + status.nav_item + '</ul>'
    navbar += """
        </div>
      </div>
    </div>
"""
    return navbar


def exit_href(data=False):
    url = url_action('_da_exit')
    if not data:
        action_search = re.search(r'[\?\&]action=([^\&]+)', url)
        if action_search:
            return url + '" data-embaction="' + action_search.group(1)
    return url


def delete_session_for_interview(i=None):
    if i is not None:
        clear_session(i)
    for key in ('i', 'uid', 'key_logged', 'encrypted', 'chatstatus', 'observer', 'monitor', 'doing_sms', 'alt_session'):
        if key in session:
            del session[key]


def delete_session_sessions():
    if 'sessions' in session:
        del session['sessions']


def delete_session_info():
    for key in ('i', 'uid', 'key_logged', 'tempuser', 'user_id', 'encrypted', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'playgroundfile', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules', 'playgroundpackages', 'taskwait', 'phone_number', 'otp_secret', 'validated_user', 'github_next', 'next', 'sessions', 'alt_session', 'zitadel_verifier', 'miniorange_verifier'):
        if key in session:
            del session[key]


def reset_session(yaml_filename, secret):
    user_dict = fresh_dictionary()
    user_code = get_unique_name(yaml_filename, secret)
    if STATS:
        r.incr('da:stats:sessions')
    update_session(yaml_filename, uid=user_code)
    return (user_code, user_dict)


def _endpoint_url(endpoint, **kwargs):
    if endpoint:
        return url_for(endpoint, **kwargs)
    return url_for('interview.index')


def user_can_edit_package(pkgname=None, giturl=None):
    if current_user.has_role('admin'):
        return True
    if not PACKAGE_PROTECTION:
        if pkgname in ('docassemble.base', 'docassemble.demo', 'docassemble.webapp'):
            return False
        return True
    if pkgname is not None:
        pkgname = pkgname.strip()
        if pkgname == '' or re.search(r'\s', pkgname):
            return False
        results = db.session.execute(select(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).where(and_(Package.name == pkgname, Package.active == True))).all()  # noqa: E712 # pylint: disable=singleton-comparison
        the_count = 0
        the_count += len(results)
        if the_count == 0:
            return True
        for d in results:
            if d.user_id == current_user.id:
                return True
    if giturl is not None:
        giturl = giturl.strip()
        if giturl == '' or re.search(r'\s', giturl):
            return False
        results = db.session.execute(select(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).where(and_(or_(Package.giturl == giturl + '/', Package.giturl == giturl), Package.active == True))).all()  # noqa: E712 # pylint: disable=singleton-comparison
        the_count = len(results)
        if the_count == 0:
            return True
        for d in results:
            if d.user_id == current_user.id:
                return True
    return False


def uninstall_package(packagename):
    # logmessage("server uninstall_package: " + packagename)
    existing_package = db.session.execute(select(Package).filter_by(name=packagename, active=True).order_by(Package.id.desc())).first()
    if existing_package is None:
        flash(word("Package did not exist"), 'error')
        return
    db.session.execute(update(Package).where(Package.name == packagename, Package.active == True).values(active=False))  # noqa: E712 # pylint: disable=singleton-comparison
    db.session.commit()


def summarize_results(results, logmessages, html=True):
    if html:
        output = '<br>'.join([x + ':&nbsp;' + results[x] for x in sorted(results.keys())])
        if len(logmessages) > 0:
            if len(output) > 0:
                output += '<br><br><strong>' + word("pip log") + ':</strong><br>'
            else:
                output = ''
            output += re.sub(r'\n', r'<br>', logmessages)
        return Markup(output)
    output = '\n'.join([x + ': ' + results[x] for x in sorted(results.keys())])
    if len(logmessages) > 0:
        if len(output) > 0:
            output += "\n" + word("pip log") + ':\n'
        else:
            output = ''
        output += logmessages
    if len(output) > 210000:
        output = output[0:100000] + "\n\nTRUNCATED\n\n" + output[-100000:]
    return output


def install_zip_package(packagename, file_number):
    # logmessage("install_zip_package: " + packagename + " " + str(file_number))
    existing_package = db.session.execute(select(Package).filter_by(name=packagename).order_by(Package.id.desc()).with_for_update()).scalar()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, upload=file_number, active=True, type='zip', version=1)
        db.session.add(package_auth)
        db.session.add(package_entry)
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None and existing_package.upload != file_number:
            logmessage("install_zip_package: deleting old ZIP file for " + packagename + " with number " + str(existing_package.upload))
            SavedFile(existing_package.upload).delete()
        existing_package.package_auth.user_id = current_user.id
        existing_package.package_auth.authtype = 'owner'
        existing_package.upload = file_number
        existing_package.active = True
        existing_package.limitation = None
        existing_package.giturl = None
        existing_package.gitbranch = None
        existing_package.type = 'zip'
        existing_package.version += 1
    db.session.commit()


def install_git_package(packagename, giturl, branch):
    # logmessage("install_git_package: " + packagename + " " + str(giturl))
    giturl = str(giturl).rstrip('/')
    if branch is None or str(branch).lower().strip() in ('none', ''):
        branch = GITHUB_BRANCH
    if db.session.execute(select(Package).filter_by(name=packagename)).first() is None and db.session.execute(select(Package).where(or_(Package.giturl == giturl, Package.giturl == giturl + '/')).with_for_update()).scalar() is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, giturl=giturl, package_auth=package_auth, version=1, active=True, type='git', upload=None, limitation=None, gitbranch=branch)
        db.session.add(package_auth)
        db.session.add(package_entry)
    else:
        existing_package = db.session.execute(select(Package).filter_by(name=packagename).order_by(Package.id.desc()).with_for_update()).scalar()
        if existing_package is None:
            existing_package = db.session.execute(select(Package).where(or_(Package.giturl == giturl, Package.giturl == giturl + '/')).order_by(Package.id.desc()).with_for_update()).scalar()
        if existing_package is not None:
            if existing_package.type == 'zip' and existing_package.upload is not None:
                logmessage("install_git_package: deleting old ZIP file for " + packagename + " with number " + str(existing_package.upload))
                SavedFile(existing_package.upload).delete()
            existing_package.package_auth.user_id = current_user.id
            existing_package.package_auth.authtype = 'owner'
            existing_package.name = packagename
            existing_package.giturl = giturl
            existing_package.upload = None
            existing_package.version += 1
            existing_package.limitation = None
            existing_package.active = True
            if branch:
                existing_package.gitbranch = branch
            existing_package.type = 'git'
        else:
            logmessage("install_git_package: package " + str(giturl) + " appeared to exist but could not be found")
    db.session.commit()


def install_pip_package(packagename, limitation):
    # logmessage("install_pip_package: " + packagename + " " + str(limitation))
    existing_package = db.session.execute(select(Package).filter_by(name=packagename).order_by(Package.id.desc()).with_for_update()).scalar()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, limitation=limitation, version=1, active=True, type='pip')
        db.session.add(package_auth)
        db.session.add(package_entry)
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None:
            logmessage("install_pip_package: deleting old ZIP file for " + packagename + " with number " + str(existing_package.upload))
            SavedFile(existing_package.upload).delete()
        existing_package.package_auth.user_id = current_user.id
        existing_package.package_auth.authtype = 'owner'
        existing_package.version += 1
        existing_package.type = 'pip'
        existing_package.limitation = limitation
        existing_package.giturl = None
        existing_package.gitbranch = None
        existing_package.upload = None
        existing_package.active = True
    db.session.commit()


def get_package_info():
    is_admin = current_user.has_role('admin')
    package_list = []
    package_auth = {}
    seen = {}
    for auth in db.session.execute(select(PackageAuth)).scalars():
        if auth.package_id not in package_auth:
            package_auth[auth.package_id] = {}
        package_auth[auth.package_id][auth.user_id] = auth.authtype
    for package in db.session.execute(select(Package).filter_by(active=True).order_by(Package.name, Package.id.desc())).scalars():
        # if exclude_core and package.name in ('docassemble', 'docassemble.base', 'docassemble.webapp'):
        #     continue
        if package.name in seen:
            continue
        seen[package.name] = 1
        if package.type is not None:
            can_update = not bool(package.type == 'zip')
            can_uninstall = bool(is_admin or (package.id in package_auth and current_user.id in package_auth[package.id]))
            if package.name in system_packages:
                can_uninstall = False
                can_update = False
            if package.name == 'docassemble.webapp':
                can_uninstall = False
                can_update = is_admin
            package_list.append(Object(package=package, can_update=can_update, can_uninstall=can_uninstall))
    return package_list, package_auth


def name_of_user(user, include_email=False):
    output = ''
    if user.first_name:
        output += user.first_name
        if user.last_name:
            output += ' '
    if user.last_name:
        output += user.last_name
    if include_email and user.email:
        if output:
            output += ', '
        output += user.email
    return output


def flash_as_html(message, message_type="info", is_ajax=True):
    if message_type == 'error':
        message_type = 'danger'
    output = "\n        " + (NOTIFICATION_MESSAGE % (message_type, str(message))) + "\n"
    if not is_ajax:
        flash(message, message_type)
    return output


def make_example_html(examples, first_id, example_html, data_dict):
    example_html.append('          <ul class="nav flex-column nav-pills da-example-list da-example-hidden">\n')
    for example in examples:
        if 'list' in example:
            example_html.append('          <li class="nav-item"><a tabindex="0" class="nav-link da-example-heading">' + example['title'] + '</a>')
            make_example_html(example['list'], first_id, example_html, data_dict)
            example_html.append('          </li>')
            continue
        if len(first_id) == 0:
            first_id.append(example['id'])
        example_html.append('            <li class="nav-item"><a tabindex="0" class="nav-link da-example-link" data-example="' + example['id'] + '">' + example['title'] + '</a></li>')
        data_dict[example['id']] = example
    example_html.append('          </ul>')


def public_method(method, the_class):
    if isinstance(method, TheMethodType) and method.__name__ != 'init' and not method.__name__.startswith('_') and method.__name__ in the_class.__dict__:
        return True
    return False


def noquotetrunc(string):
    string = noquote(string)
    if string is not None:
        try:
            str('') + string
        except:
            string = ''
        if len(string) > 163:
            string = string[:160] + '...'
    return string


def noquote(string):
    if string is None:
        return string
    string = amp_match.sub('&amp;', string)
    string = noquote_match.sub('&quot;', string)
    string = lt_match.sub('&lt;', string)
    string = gt_match.sub('&gt;', string)
    return string


def infobutton(title):
    docstring = ''
    if 'doc' in title_documentation[title]:
        docstring += noquote(title_documentation[title]['doc'])
    if 'url' in title_documentation[title]:
        docstring += "<br><a target='_blank' href='" + title_documentation[title]['url'] + "'>" + word("View documentation") + "</a>"
    return '&nbsp;<a tabindex="0" role="button" class="daquestionsign" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="auto" data-bs-content="' + docstring + '" title="' + noquote(title_documentation[title].get('title', title)) + '"><i class="fa-solid fa-question-circle"></i></a>'
    # title=' + json.dumps(word("Help"))
    # data-bs-selector="true"


def search_button(var, field_origins, name_origins, interview_source, all_sources):
    in_this_file = False
    usage = {}
    if var in field_origins:
        for x in sorted(field_origins[var]):
            if x is interview_source:
                in_this_file = True
            else:
                if x.path not in usage:
                    usage[x.path] = set()
                usage[x.path].add('defined')
                all_sources.add(x)
    if var in name_origins:
        for x in sorted(name_origins[var]):
            if x is interview_source:
                in_this_file = True
            else:
                if x.path not in usage:
                    usage[x.path] = set()
                usage[x.path].add('used')
                all_sources.add(x)
    usage_type = [set(), set(), set()]
    for path, the_set in usage.items():
        if 'defined' in the_set and 'used' in the_set:
            usage_type[2].add(path)
        elif 'used' in the_set:
            usage_type[1].add(path)
        elif 'defined' in the_set:
            usage_type[0].add(path)
        else:
            continue
    messages = []
    if len(usage_type[2]) > 0:
        messages.append(word("Defined and used in " + comma_and_list(sorted(usage_type[2]))))
    elif len(usage_type[0]) > 0:
        messages.append(word("Defined in") + ' ' + comma_and_list(sorted(usage_type[0])))
    elif len(usage_type[2]) > 0:
        messages.append(word("Used in") + ' ' + comma_and_list(sorted(usage_type[0])))
    if len(messages) > 0:
        title = 'title="' + '; '.join(messages) + '" '
    else:
        title = ''
    if in_this_file:
        classname = 'dasearchthis'
    else:
        classname = 'dasearchother'
    return '<a tabindex="0" class="dasearchicon ' + classname + '" ' + title + 'data-name="' + noquote(var) + '"><i class="fa-solid fa-search"></i></a>'

search_key = """
                  <tr><td><h4>""" + word("Note") + """</h4></td></tr>
                  <tr><td><a tabindex="0" class="dasearchicon dasearchthis"><i class="fa-solid fa-search"></i></a> """ + word("means the name is located in this file") + """</td></tr>
                  <tr><td><a tabindex="0" class="dasearchicon dasearchother"><i class="fa-solid fa-search"></i></a> """ + word("means the name may be located in a file included by reference, such as:") + """</td></tr>"""


def find_needed_names(interview, needed_names, the_name=None, the_question=None):
    if the_name is not None:
        needed_names.add(the_name)
        if the_name in interview.questions:
            for lang in interview.questions[the_name]:
                for question in interview.questions[the_name][lang]:
                    find_needed_names(interview, needed_names, the_question=question)
    elif the_question is not None:
        for the_set in (the_question.mako_names, the_question.names_used):
            for name in the_set:
                if name in needed_names:
                    continue
                find_needed_names(interview, needed_names, the_name=name)
    else:
        for question in interview.questions_list:
            # if not (question.is_mandatory or question.is_initial):
            #     continue
            find_needed_names(interview, needed_names, the_question=question)


def source_code_url(the_name, datatype=None):
    if datatype == 'module':
        try:
            if (not hasattr(the_name, '__path__')) or (not the_name.__path__):
                # logmessage("Nothing for module " + the_name)
                return None
            source_file = re.sub(r'\.pyc$', r'.py', the_name.__path__[0])
            line_number = 1
        except:
            return None
    elif datatype == 'class':
        try:
            source_file = inspect.getsourcefile(the_name)
            line_number = inspect.findsource(the_name)[1]
        except:
            # logmessage("Nothing for class " + the_name)
            return None
    elif hasattr(the_name, '__code__'):
        source_file = the_name.__code__.co_filename
        line_number = the_name.__code__.co_firstlineno
    else:
        # logmessage("Nothing for " + the_name)
        return None
    source_file = re.sub(r'.*/site-packages/', '', source_file)
    m = re.search(r'^docassemble/(base|webapp|demo)/', source_file)
    if m:
        output = 'https://github.com/jhpyle/docassemble/blob/master/docassemble_' + m.group(1) + '/' + source_file
        if line_number == 1:
            return output
        return output + '#L' + str(line_number)
    # logmessage("no match for " + str(source_file))
    return None


def get_vars_in_use(interview, interview_status, debug_mode=False, return_json=False, show_messages=True, show_jinja_help=False, current_project='default', use_playground=True):
    user_dict = fresh_dictionary()
    # if 'uid' not in session:
    #     session['uid'] = random_alphanumeric(32)
    if debug_mode:
        has_error = True
        error_message = "Not checking variables because in debug mode."
        error_type = Exception
    else:
        if not interview.success:
            has_error = True
            error_type = DAErrorCompileError
        else:
            old_language = get_language()
            try:
                interview.assemble(user_dict, interview_status)
                has_error = False
            except BaseException as errmess:
                has_error = True
                error_message = str(errmess)
                error_type = type(errmess)
                logmessage("get_vars_in_use: failed assembly with error type " + str(error_type) + " and message: " + error_message)
            set_language(old_language)
    fields_used = set()
    names_used = set()
    field_origins = {}
    name_origins = {}
    all_sources = set()
    names_used.update(interview.names_used)
    for question in interview.questions_list:
        for the_set in (question.mako_names, question.names_used, question.fields_used):
            names_used.update(the_set)
            for key in the_set:
                if key not in name_origins:
                    name_origins[key] = set()
                name_origins[key].add(question.from_source)
        fields_used.update(question.fields_used)
        for key in question.fields_used:
            if key not in field_origins:
                field_origins[key] = set()
            field_origins[key].add(question.from_source)
    for val in interview.questions:
        names_used.add(val)
        if val not in name_origins:
            name_origins[val] = set()
        for lang in interview.questions[val]:
            for q in interview.questions[val][lang]:
                name_origins[val].add(q.from_source)
        fields_used.add(val)
        if val not in field_origins:
            field_origins[val] = set()
        for lang in interview.questions[val]:
            for q in interview.questions[val][lang]:
                field_origins[val].add(q.from_source)
    needed_names = set()
    find_needed_names(interview, needed_names)
    functions = set()
    modules = set()
    classes = set()
    name_info = copy.deepcopy(base_name_info)
    if use_playground:
        playground_user = get_playground_user()
        area = SavedFile(playground_user.id, fix=True, section='playgroundtemplate')
        the_directory = directory_for(area, current_project)
        templates = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        area = SavedFile(playground_user.id, fix=True, section='playgroundstatic')
        the_directory = directory_for(area, current_project)
        static = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        area = SavedFile(playground_user.id, fix=True, section='playgroundsources')
        the_directory = directory_for(area, current_project)
        sources = sorted([f for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        area = SavedFile(playground_user.id, fix=True, section='playgroundmodules')
        the_directory = directory_for(area, current_project)
        avail_modules = sorted([re.sub(r'.py$', '', f) for f in os.listdir(the_directory) if os.path.isfile(os.path.join(the_directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    else:
        templates = []
        static = []
        sources = []
        avail_modules = []
    for val in user_dict:
        if isinstance(user_dict[val], types.FunctionType):
            if val not in pg_code_cache:
                try:
                    pg_code_cache[val] = {'doc': noquotetrunc(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val) + '()', 'tag': str(val) + str(inspect.signature(user_dict[val])), 'git': source_code_url(user_dict[val])}
                except:
                    pg_code_cache[val] = {'doc': '', 'name': str(val), 'insert': str(val) + '()', 'tag': str(val) + '()', 'git': source_code_url(user_dict[val])}
            name_info[val] = copy.copy(pg_code_cache[val])
            if 'tag' in name_info[val]:
                functions.add(val)
        elif isinstance(user_dict[val], types.ModuleType):
            if val not in pg_code_cache:
                try:
                    pg_code_cache[val] = {'doc': noquotetrunc(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val), 'git': source_code_url(user_dict[val], datatype='module')}
                except:
                    pg_code_cache[val] = {'doc': '', 'name': str(val), 'insert': str(val), 'git': source_code_url(user_dict[val], datatype='module')}
            name_info[val] = copy.copy(pg_code_cache[val])
            modules.add(val)
        elif isinstance(user_dict[val], TypeType):
            if val not in pg_code_cache:
                bases = []
                for x in list(user_dict[val].__bases__):
                    if x.__name__ != 'DAObject':
                        bases.append(x.__name__)
                try:
                    methods = inspect.getmembers(user_dict[val], predicate=lambda x, the_val=val: public_method(x, user_dict[the_val]))
                except:
                    methods = []
                method_list = []
                for name, value in methods:
                    try:
                        method_list.append({'insert': '.' + str(name) + '()', 'name': str(name), 'doc': noquotetrunc(inspect.getdoc(value)), 'tag': '.' + str(name) + str(inspect.signature(value)), 'git': source_code_url(value)})
                    except:
                        method_list.append({'insert': '.' + str(name) + '()', 'name': str(name), 'doc': '', 'tag': '.' + str(name) + '()', 'git': source_code_url(value)})
                try:
                    pg_code_cache[val] = {'doc': noquotetrunc(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val), 'bases': bases, 'methods': method_list, 'git': source_code_url(user_dict[val], datatype='class')}
                except:
                    pg_code_cache[val] = {'doc': '', 'name': str(val), 'insert': str(val), 'bases': bases, 'methods': method_list, 'git': source_code_url(user_dict[val], datatype='class')}
            name_info[val] = copy.copy(pg_code_cache[val])
            if 'methods' in name_info[val]:
                classes.add(val)
    for val in pickleable_objects(user_dict):
        names_used.add(val)
        if val not in name_info:
            name_info[val] = {}
        name_info[val]['type'] = user_dict[val].__class__.__name__
        name_info[val]['iterable'] = bool(hasattr(user_dict[val], '__iter__') and not isinstance(user_dict[val], str))
    for var, val in base_name_info.items():
        if val['show']:
            names_used.add(var)
    names_used = set(i for i in names_used if not extraneous_var.search(i))
    for var in ('_internal', '__object_type', '_DAOBJECTDEFAULTDA'):
        names_used.discard(var)
    for var in interview.mlfields:
        names_used.discard(var + '.text')
    if len(interview.mlfields) > 0:
        classes.add('DAModel')
        method_list = [{'insert': '.predict()', 'name': 'predict', 'doc': "Generates a prediction based on the 'text' attribute and sets the attributes 'entry_id,' 'predictions,' 'prediction,' and 'probability.'  Called automatically.", 'tag': '.predict(self)'}]
        name_info['DAModel'] = {'doc': 'Applies natural language processing to user input and returns a prediction.', 'name': 'DAModel', 'insert': 'DAModel', 'bases': [], 'methods': method_list}
    view_doc_text = word("View documentation")
    word_documentation = word("Documentation")
    attr_documentation = word("Show attributes")
    ml_parts = interview.get_ml_store().split(':')
    if len(ml_parts) == 2:
        ml_parts[1] = re.sub(r'^data/sources/ml-|\.json$', '', ml_parts[1])
    else:
        ml_parts = ['_global', '_global']
    for var, val in documentation_dict.items():
        if var not in name_info:
            name_info[var] = {}
        if 'doc' in name_info[var] and name_info[var]['doc'] is not None:
            name_info[var]['doc'] += '<br>'
        else:
            name_info[var]['doc'] = ''
        name_info[var]['doc'] += "<a target='_blank' href='" + DOCUMENTATION_BASE + val + "'>" + view_doc_text + "</a>"
    for var, val in name_info.items():
        if 'methods' in val:
            for method in val['methods']:
                if var + '.' + method['name'] in documentation_dict:
                    if method['doc'] is None:
                        method['doc'] = ''
                    else:
                        method['doc'] += '<br>'
                    if view_doc_text not in method['doc']:
                        method['doc'] += "<a target='_blank' href='" + DOCUMENTATION_BASE + documentation_dict[var + '.' + method['name']] + "'>" + view_doc_text + "</a>"
    content = ''
    if has_error and show_messages:
        error_style = 'danger'
        if error_type is DAErrorNoEndpoint:
            error_style = 'warning'
            message_to_use = title_documentation['incomplete']['doc']
        elif error_type is DAErrorCompileError:
            message_to_use = title_documentation['compilefail']['doc']
        elif error_type is DAErrorMissingVariable:
            message_to_use = error_message
        else:
            message_to_use = title_documentation['generic error']['doc']
        content += '\n                <tr><td class="playground-warning-box"><div class="alert alert-' + error_style + '">' + message_to_use + '</div></td></tr>'
    vocab_dict = {}
    vocab_set = (names_used | functions | classes | modules | fields_used | set(key for key in base_name_info if not re.search(r'\.', key)) | set(key for key in name_info if not re.search(r'\.', key)) | set(templates) | set(static) | set(sources) | set(avail_modules) | set(interview.images.keys()))
    vocab_set = set(i for i in vocab_set if not extraneous_var.search(i))
    names_used = names_used.difference(functions | classes | modules | set(avail_modules))
    undefined_names = names_used.difference(fields_used | set(base_name_info.keys()) | set(x for x in names_used if '.' in x))
    implicitly_defined = set()
    for var in fields_used:
        the_var = var
        while '.' in the_var:
            the_var = re.sub(r'(.*)\..*$', r'\1', the_var, flags=re.DOTALL)
            implicitly_defined.add(the_var)
    for var in ('_internal', '__object_type', '_DAOBJECTDEFAULTDA'):
        undefined_names.discard(var)
        vocab_set.discard(var)
    for var in [x for x in undefined_names if x.endswith(']')]:
        undefined_names.discard(var)
    for var in (functions | classes | modules):
        undefined_names.discard(var)
    for var in user_dict:
        undefined_names.discard(var)
    names_used = names_used.difference(undefined_names)
    if return_json:
        if len(names_used) > 0:
            has_parent = {}
            has_children = set()
            for var in names_used:
                parent = re.sub(r'[\.\[].*', '', var)
                if parent != var:
                    has_parent[var] = parent
                    has_children.add(parent)
            var_list = []
            for var in sorted(names_used):
                var_trans = re.sub(r'\[[0-9]+\]', '[i]', var)
                # var_trans = re.sub(r'\[i\](.*)\[i\](.*)\[i\](.*)\[i\](.*)\[i\](.*)\[i\]', r'[i]\1[j]\2[k]\3[l]\4[m]\5[n]', var_trans)
                # var_trans = re.sub(r'\[i\](.*)\[i\](.*)\[i\](.*)\[i\](.*)\[i\]', r'[i]\1[j]\2[k]\3[l]\4[m]', var_trans)
                # var_trans = re.sub(r'\[i\](.*)\[i\](.*)\[i\](.*)\[i\]', r'[i]\1[j]\2[k]\3[l]', var_trans)
                var_trans = re.sub(r'\[i\](.*)\[i\](.*)\[i\]', r'[i]\1[j]\2[k]', var_trans)
                var_trans = re.sub(r'\[i\](.*)\[i\]', r'[i]\1[j]', var_trans)
                info = {'var': var, 'to_insert': var}
                if var_trans != var:
                    info['var_base'] = var_trans
                info['hide'] = bool(var in has_parent)
                if var in base_name_info:
                    if not base_name_info[var]['show']:
                        continue
                if var in documentation_dict or var in base_name_info:
                    info['var_type'] = 'builtin'
                elif var not in fields_used and var not in implicitly_defined and var_trans not in fields_used and var_trans not in implicitly_defined:
                    info['var_type'] = 'not_used'
                elif var not in needed_names:
                    info['var_type'] = 'possibly_not_used'
                else:
                    info['var_type'] = 'default'
                if var in name_info and 'type' in name_info[var] and name_info[var]['type']:
                    info['class_name'] = name_info[var]['type']
                elif var in interview.mlfields:
                    info['class_name'] = 'DAModel'
                if var in name_info and 'iterable' in name_info[var]:
                    info['iterable'] = name_info[var]['iterable']
                if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                if current_app.config['ENABLE_TRAINING'] and var in interview.mlfields:
                    if 'ml_group' in interview.mlfields[var] and not interview.mlfields[var]['ml_group'].uses_mako:
                        (ml_package, ml_file, ml_group_id) = get_ml_info(interview.mlfields[var]['ml_group'].original_text, ml_parts[0], ml_parts[1])
                        info['train_link'] = url_for('ml.train', package=ml_package, file=ml_file, group_id=ml_group_id)
                    else:
                        info['train_link'] = url_for('ml.train', package=ml_parts[0], file=ml_parts[1], group_id=var)
                var_list.append(info)
        functions_list = []
        if len(functions) > 0:
            for var in sorted(functions):
                info = {'var': var, 'to_insert': name_info[var]['insert'], 'name': name_info[var]['tag']}
                if 'doc' in name_info[var] and name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                functions_list.append(info)
        classes_list = []
        if len(classes) > 0:
            for var in sorted(classes):
                info = {'var': var, 'to_insert': name_info[var]['insert'], 'name': name_info[var]['name']}
                if name_info[var]['bases']:
                    info['bases'] = name_info[var]['bases']
                if 'doc' in name_info[var] and name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                if 'methods' in name_info[var] and len(name_info[var]['methods']):
                    info['methods'] = []
                    for method_item in name_info[var]['methods']:
                        method_info = {'name': method_item['name'], 'to_insert': method_item['insert'], 'tag': method_item['tag']}
                        if 'git' in method_item:
                            method_info['git'] = method_item['git']
                        if method_item['doc']:
                            method_info['doc_content'] = method_item['doc']
                            method_info['doc_title'] = word_documentation
                        info['methods'].append(method_info)
                classes_list.append(info)
        modules_list = []
        if len(modules) > 0:
            for var in sorted(modules):
                info = {'var': var, 'to_insert': name_info[var]['insert']}
                if name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                modules_list.append(info)
        if use_playground:
            modules_available_list = []
            if len(avail_modules) > 0:
                for var in sorted(avail_modules):
                    info = {'var': var, 'to_insert': "." + var}
                    modules_available_list.append(info)
            templates_list = []
            if len(templates) > 0:
                for var in sorted(templates):
                    info = {'var': var, 'to_insert': var}
                    templates_list.append(info)
            sources_list = []
            if len(sources) > 0:
                for var in sorted(sources):
                    info = {'var': var, 'to_insert': var}
                    sources_list.append(info)
            static_list = []
            if len(static) > 0:
                for var in sorted(static):
                    info = {'var': var, 'to_insert': var}
                    static_list.append(info)
        images_list = []
        if len(interview.images) > 0:
            for var in sorted(interview.images):
                info = {'var': var, 'to_insert': var}
                the_ref = get_url_from_file_reference(interview.images[var].get_reference(), {})
                if the_ref:
                    info['url'] = the_ref
                images_list.append(info)
        if use_playground:
            return {'undefined_names': list(sorted(undefined_names)), 'var_list': var_list, 'functions_list': functions_list, 'classes_list': classes_list, 'modules_list': modules_list, 'modules_available_list': modules_available_list, 'templates_list': templates_list, 'sources_list': sources_list, 'images_list': images_list, 'static_list': static_list}, sorted(vocab_set), vocab_dict, []
        return {'undefined_names': list(sorted(undefined_names)), 'var_list': var_list, 'functions_list': functions_list, 'classes_list': classes_list, 'modules_list': modules_list, 'images_list': images_list}, sorted(vocab_set), vocab_dict, []
    ac_list = []
    if len(undefined_names) > 0:
        content += '\n                <tr><td><h4>' + word('Undefined names') + infobutton('undefined') + '</h4></td></tr>'
        for var in sorted(undefined_names):
            content += '\n                <tr><td>' + search_button(var, field_origins, name_origins, interview.source, all_sources) + '<a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-danger btn-sm playground-variable">' + var + '</a></td></tr>'
            vocab_dict[var] = var
            ac_list.append({"label": var, "type": "variable"})
    if len(names_used) > 0:
        content += '\n                <tr><td><h4>' + word('Variables') + infobutton('variables') + '</h4></td></tr>'
        has_parent = {}
        has_children = set()
        for var in names_used:
            parent = re.sub(r'[\.\[].*', '', var)
            if parent != var:
                has_parent[var] = parent
                has_children.add(parent)
        for var in sorted(names_used):
            var_trans = re.sub(r'\[[0-9]\]', '[i]', var)
            var_trans = re.sub(r'\[i\](.*)\[i\](.*)\[i\]', r'[i]\1[j]\2[k]', var_trans)
            var_trans = re.sub(r'\[i\](.*)\[i\]', r'[i]\1[j]', var_trans)
            if var in has_parent:
                hide_it = ' style="display: none" data-parent="' + noquote(has_parent[var]) + '"'
            else:
                hide_it = ''
            if var in base_name_info:
                if not base_name_info[var]['show']:
                    continue
            if var in documentation_dict or var in base_name_info:
                class_type = 'btn-info'
                title = 'title=' + json.dumps(word("Special variable")) + ' '
            elif var not in fields_used and var not in implicitly_defined and var_trans not in fields_used and var_trans not in implicitly_defined:
                class_type = 'btn-secondary'
                title = 'title=' + json.dumps(word("Possibly not defined")) + ' '
            elif var not in needed_names:
                class_type = 'btn-warning'
                title = 'title=' + json.dumps(word("Possibly not used")) + ' '
            else:
                class_type = 'btn-primary'
                title = ''
            content += '\n                <tr' + hide_it + '><td>' + search_button(var, field_origins, name_origins, interview.source, all_sources) + '<a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" ' + title + 'class="btn btn-sm ' + class_type + ' playground-variable">' + var + '</a>'
            vocab_dict[var] = var
            ac_list.append({"label": var, "type": "variable"})
            if var in has_children:
                content += '&nbsp;<a tabindex="0" class="dashowattributes" role="button" data-name="' + noquote(var) + '" title=' + json.dumps(attr_documentation) + '><i class="fa-solid fa-ellipsis-h"></i></a>'
            if var in name_info and 'type' in name_info[var] and name_info[var]['type']:
                content += '&nbsp;<span data-ref="' + noquote(name_info[var]['type']) + '" class="daparenthetical">(' + name_info[var]['type'] + ')</span>'
            elif var in interview.mlfields:
                content += '&nbsp;<span data-ref="DAModel" class="daparenthetical">(DAModel)</span>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                if 'git' in name_info[var] and name_info[var]['git']:
                    git_link = noquote("<a class='float-end' target='_blank' href='" + name_info[var]['git'] + "'><i class='fa-solid fa-code'></i></a>")
                else:
                    git_link = ''
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="auto" data-bs-content="' + name_info[var]['doc'] + '"  title="' + var + git_link + '"><i class="fa-solid fa-info-circle"></i></a>'  # data-bs-selector="true" title=' + json.dumps(word_documentation) + '
            if current_app.config['ENABLE_TRAINING'] and var in interview.mlfields:
                if 'ml_group' in interview.mlfields[var] and not interview.mlfields[var]['ml_group'].uses_mako:
                    (ml_package, ml_file, ml_group_id) = get_ml_info(interview.mlfields[var]['ml_group'].original_text, ml_parts[0], ml_parts[1])
                    content += '&nbsp;<a class="datrain" target="_blank" href="' + url_for('ml.train', package=ml_package, file=ml_file, group_id=ml_group_id) + '" title=' + json.dumps(word("Train")) + '><i class="fa-solid fa-graduation-cap"></i></a>'
                else:
                    content += '&nbsp;<a class="datrain" target="_blank" href="' + url_for('ml.train', package=ml_parts[0], file=ml_parts[1], group_id=var) + '" title=' + json.dumps(word("Train")) + '><i class="fa-solid fa-graduation-cap"></i></a>'
            content += '</td></tr>'
        if len(all_sources) > 0 and show_messages:
            content += search_key
            content += '\n                <tr><td>'
            content += '\n                  <ul>'
            for path in sorted([x.path for x in all_sources]):
                content += '\n                    <li><a target="_blank" href="' + url_for('develop.view_source', i=path, project=current_project) + '">' + path + '<a></li>'
            content += '\n                  </ul>'
            content += '\n                </td></tr>'
    if len(functions) > 0:
        content += '\n                <tr><td><h4>' + word('Functions') + infobutton('functions') + '</h4></td></tr>'
        for var in sorted(functions):
            if var in name_info:
                content += '\n                <tr><td><a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="btn btn-sm btn-warning playground-variable">' + name_info[var]['tag'] + '</a>'
            vocab_dict[var] = name_info[var]['insert']
            ac_list.append({"label": var, "type": "function"})
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                if 'git' in name_info[var] and name_info[var]['git']:
                    git_link = noquote("<a class='float-end' target='_blank' href='" + name_info[var]['git'] + "'><i class='fa-solid fa-code'></i></a>")
                else:
                    git_link = ''
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="auto" data-bs-content="' + name_info[var]['doc'] + '" title="' + var + git_link + '"><i class="fa-solid fa-info-circle"></i></a>'  # data-bs-selector="true" title=' + json.dumps(word_documentation) + '
            content += '</td></tr>'
    if len(classes) > 0:
        content += '\n                <tr><td><h4>' + word('Classes') + infobutton('classes') + '</h4></td></tr>'
        for var in sorted(classes):
            content += '\n                <tr><td><a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="btn btn-sm btn-info playground-variable">' + name_info[var]['name'] + '</a>'
            vocab_dict[var] = name_info[var]['insert']
            ac_list.append({"label": var, "type": "class"})
            if name_info[var]['bases']:
                content += '&nbsp;<span data-ref="' + noquote(name_info[var]['bases'][0]) + '" class="daparenthetical">(' + name_info[var]['bases'][0] + ')</span>'
            if name_info[var]['doc']:
                if 'git' in name_info[var] and name_info[var]['git']:
                    git_link = noquote("<a class='float-end' target='_blank' href='" + name_info[var]['git'] + "'><i class='fa-solid fa-code'></i></a>")
                else:
                    git_link = ''
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="auto" data-bs-content="' + name_info[var]['doc'] + '" title="' + var + git_link + '"><i class="fa-solid fa-info-circle"></i></a>'  # data-bs-selector="true" title=' + json.dumps(word_documentation) + '
            if len(name_info[var]['methods']) > 0:
                content += '&nbsp;<a tabindex="0" class="dashowmethods" role="button" data-showhide="XMETHODX' + var + '" title=' + json.dumps(word('Methods')) + '><i class="fa-solid fa-cog"></i></a>'
                content += '<div style="display: none;" id="XMETHODX' + var + '"><table><tbody>'
                for method_info in name_info[var]['methods']:
                    if 'git' in method_info and method_info['git']:
                        git_link = noquote("<a class='float-end' target='_blank' href='" + method_info['git'] + "'><i class='fa-solid fa-code'></i></a>")
                    else:
                        git_link = ''
                    content += '<tr><td><a tabindex="0" role="button" data-name="' + noquote(method_info['name']) + '" data-insert="' + noquote(method_info['insert']) + '" class="btn btn-sm btn-warning playground-variable">' + method_info['tag'] + '</a>'
                    # vocab_dict[method_info['name']] = method_info['insert']
                    if method_info['doc']:
                        content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="auto" data-bs-content="' + method_info['doc'] + '" data-bs-title="' + noquote(method_info['name']) + git_link + '"><i class="fa-solid fa-info-circle"></i></a>'  # data-bs-selector="true" title=' + json.dumps(word_documentation) + '
                    content += '</td></tr>'
                content += '</tbody></table></div>'
            content += '</td></tr>'
    if len(modules) > 0:
        content += '\n                <tr><td><h4>' + word('Modules defined') + infobutton('modules') + '</h4></td></tr>'
        for var in sorted(modules):
            content += '\n                <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" role="button" class="btn btn-sm btn-success playground-variable">' + name_info[var]['name'] + '</a>'
            vocab_dict[var] = name_info[var]['insert']
            ac_list.append({"label": var, "type": "keyword"})
            if name_info[var]['doc']:
                if 'git' in name_info[var] and name_info[var]['git']:
                    git_link = noquote("<a class='float-end' target='_blank' href='" + name_info[var]['git'] + "'><i class='fa-solid fa-code'></i></a>")
                else:
                    git_link = ''
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="auto" data-bs-content="' + name_info[var]['doc'] + '" data-bs-title="' + noquote(var) + git_link + '"><i class="fa-solid fa-info-circle"></i></a>'  # data-bs-selector="true" title=' + json.dumps(word_documentation) + '
            content += '</td></tr>'
    if len(avail_modules) > 0:
        content += '\n                <tr><td><h4>' + word('Modules available in Playground') + infobutton('playground_modules') + '</h4></td></tr>'
        for var in avail_modules:
            content += '\n                <tr><td><a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert=".' + noquote(var) + '" class="btn btn-sm btn-success playground-variable">.' + noquote(var) + '</a>'
            vocab_dict[var] = var
            ac_list.append({"label": var, "type": "keyword"})
            content += '</td></tr>'
    if len(templates) > 0:
        content += '\n                <tr><td><h4>' + word('Templates') + infobutton('templates') + '</h4></td></tr>'
        for var in templates:
            content += '\n                <tr><td><a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-secondary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            ac_list.append({"label": var, "type": "keyword"})
            content += '</td></tr>'
    if len(static) > 0:
        content += '\n                <tr><td><h4>' + word('Static files') + infobutton('static') + '</h4></td></tr>'
        for var in static:
            content += '\n                <tr><td><a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-secondary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            ac_list.append({"label": var, "type": "keyword"})
            content += '</td></tr>'
    if len(sources) > 0:
        content += '\n                <tr><td><h4>' + word('Source files') + infobutton('sources') + '</h4></td></tr>'
        for var in sources:
            content += '\n                <tr><td><a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-secondary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            ac_list.append({"label": var, "type": "keyword"})
            content += '</td></tr>'
    if len(interview.images) > 0:
        content += '\n                <tr><td><h4>' + word('Decorations') + infobutton('decorations') + '</h4></td></tr>'
        show_images = not bool(cloud and len(interview.images) > 10)
        for var in sorted(interview.images):
            content += '\n                <tr><td>'
            the_ref = get_url_from_file_reference(interview.images[var].get_reference(), {})
            if the_ref is None:
                content += '<a role="button" tabindex="0" title=' + json.dumps(word("This image file does not exist")) + ' data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-danger playground-variable">' + noquote(var) + '</a>'
            else:
                if show_images:
                    content += '<img class="daimageicon" src="' + the_ref + '">&nbsp;'
                content += '<a role="button" tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-primary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            ac_list.append({"label": var, "type": "keyword"})
            content += '</td></tr>'
    if show_messages:
        content += "\n                <tr><td><br><em>" + word("Type Ctrl-space to autocomplete.") + "</em></td><tr>"
    if show_jinja_help:
        content += "\n                <tr><td><h4 class=\"mt-2\">" + word("Using Jinja2") + infobutton('jinja2') + "</h4>\n                  " + re.sub("table-striped", "table-bordered", docassemble.base.util.markdown_to_html(word("Jinja2 help template"), trim=False, do_terms=False)) + "</td><tr>"
    for item, item_info in base_name_info.items():
        if item not in vocab_dict and not item_info.get('exclude', False):
            vocab_dict[item] = item_info.get('insert', item)
            if 'insert' in item_info and '()' in item_info['insert']:
                ac_list.append({"label": var, "type": "function"})
            else:
                ac_list.append({"label": var, "type": "variable"})
    return content, sorted(vocab_set), vocab_dict, ac_list


@hookimpl
def ocr_google_in_background(image_file, raw_result, user_code):
    return celery_app.signature('tasks.ocr_google', args=[image_file, raw_result, user_code]).delay()


@hookimpl
def make_png_for_pdf(doc, prefix, page):
    if prefix == 'page':
        resolution = PNG_RESOLUTION
    else:
        resolution = PNG_SCREEN_RESOLUTION
    session_id = get_uid()
    task = celery_app.signature('tasks.make_png_for_pdf', args=[doc, prefix, resolution, session_id, PDFTOPPM_COMMAND], kwargs={'page': page}).delay()
    return task.id


@hookimpl
def fg_make_png_for_pdf(doc, prefix, page):
    if prefix == 'page':
        resolution = PNG_RESOLUTION
    else:
        resolution = PNG_SCREEN_RESOLUTION
    docassemble.base.util.make_png_for_pdf(doc, prefix, resolution, PDFTOPPM_COMMAND, page=page)


@hookimpl
def fg_make_png_for_pdf_path(path, prefix, page):
    if prefix == 'page':
        resolution = PNG_RESOLUTION
    else:
        resolution = PNG_SCREEN_RESOLUTION
    docassemble.base.util.make_png_for_pdf_path(path, prefix, resolution, PDFTOPPM_COMMAND, page=page)


@hookimpl
def fg_make_pdf_for_word_path(path, extension):
    success = docassemble.base.pandoc.word_to_pdf(path, extension, path + ".pdf")
    if not success:
        raise DAError("fg_make_pdf_for_word_path: unable to make PDF from " + path + " using extension " + extension + " and writing to " + path + ".pdf")

@hookimpl
def task_ready(task_id):
    result = celery_app.AsyncResult(id=task_id)
    if result.ready():
        return True
    return False

@hookimpl
def wait_for_task(task_id, timeout):
    if timeout is None:
        timeout = 3
    # logmessage("wait_for_task: starting")
    try:
        result = celery_app.AsyncResult(id=task_id)
        if result.ready():
            # logmessage("wait_for_task: was ready")
            return True
        # logmessage("wait_for_task: waiting for task to complete")
        result.get(timeout=timeout)
        # logmessage("wait_for_task: returning true")
        return True
    except celery.exceptions.TimeoutError:  # pylint: disable=possibly-used-before-assignment
        logmessage("wait_for_task: timed out")
        return False
    except BaseException as the_error:
        logmessage("wait_for_task: got error: " + str(the_error))
        return False

# def make_image_files(path):
#     if PDFTOPPM_COMMAND is not None:
#         args = [PDFTOPPM_COMMAND, '-r', str(PNG_RESOLUTION), '-png', path, path + 'page']
#         result = call(args)
#         if result > 0:
#             raise DAError("Call to pdftoppm failed")
#         args = [PDFTOPPM_COMMAND, '-r', str(PNG_SCREEN_RESOLUTION), '-png', path, path + 'screen']
#         result = call(args)
#         if result > 0:
#             raise DAError("Call to pdftoppm failed")


def current_info(yaml=None, req=None, action=None, location=None, interface='web', session_info=None, secret=None, device_id=None, session_uid=None):  # pylint: disable=redefined-outer-name
    # logmessage("interface is " + str(interface))
    if current_user.is_authenticated:
        role_list = [str(role.name) for role in current_user.roles]
        if len(role_list) == 0:
            role_list = ['user']
        login_method = current_user.social_id.split('$')[0]
        ext = {'email': current_user.email, 'roles': role_list, 'the_user_id': current_user.id, 'theid': current_user.id, 'login_method': login_method, 'firstname': current_user.first_name, 'lastname': current_user.last_name, 'nickname': current_user.nickname, 'country': current_user.country, 'subdivisionfirst': current_user.subdivisionfirst, 'subdivisionsecond': current_user.subdivisionsecond, 'subdivisionthird': current_user.subdivisionthird, 'organization': current_user.organization, 'timezone': current_user.timezone, 'language': current_user.language}
    else:
        ext = {'email': None, 'the_user_id': 't' + str(session.get('tempuser', None)), 'theid': session.get('tempuser', None), 'roles': []}
    headers = {}
    if req is None:
        url_root = daconfig.get('url root', 'http://localhost') + ROOT
        url = url_root + 'interview'
        clientip = None
        method = None
        session_uid = '0'
    else:
        url_root = url_for('interview.rootindex', _external=True)
        url = url_root + 'interview'
        if secret is None:
            secret = req.cookies.get('secret', None)
        for key, value in req.headers.items():
            headers[key] = value
        clientip = get_requester_ip(req)
        method = req.method
        if session_uid is None:
            if 'session' in req.cookies:
                session_uid = str(req.cookies.get('session'))[5:15]
            else:
                session_uid = ''
            if session_uid == '':
                session_uid = current_app.session_interface.manual_save_session(current_app, session).decode()[5:15]
        # logmessage("unique id is " + session_uid)
    if device_id is None:
        device_id = random_string(16)
    if secret is not None:
        secret = str(secret)
    if session_info is None and yaml is not None:
        session_info = get_session(yaml)
    if session_info is not None:
        user_code = session_info['uid']
        encrypted = session_info['encrypted']
    else:
        user_code = None
        encrypted = True
    return_val = {'session': user_code, 'secret': secret, 'yaml_filename': yaml, 'interface': interface, 'url': url, 'url_root': url_root, 'encrypted': encrypted, 'user': {'is_anonymous': bool(current_user.is_anonymous), 'is_authenticated': bool(current_user.is_authenticated), 'session_uid': session_uid, 'device_id': device_id}, 'headers': headers, 'clientip': clientip, 'method': method}
    if action is not None:
        # logmessage("current_info: setting an action " + repr(action))
        return_val.update(action)
        # return_val['orig_action'] = action['action']
        # return_val['orig_arguments'] = action['arguments']
    if location is not None:
        ext['location'] = location
    else:
        ext['location'] = None
    return_val['user'].update(ext)
    return return_val


def html_escape(text):
    text = re.sub('&', '&amp;', text)
    text = re.sub('<', '&lt;', text)
    text = re.sub('>', '&gt;', text)
    return text


def indent_by(text, num):
    if not text:
        return ""
    return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"


def call_sync():
    if not USING_SUPERVISOR:
        return
    args = SUPERVISORCTL + ['-s', 'http://localhost:9001', 'start', 'sync']
    result = subprocess.run(args, check=False).returncode
    if result == 0:
        pass
        # logmessage("call_sync: sent message to " + hostname)
    else:
        logmessage("call_sync: call to supervisorctl on " + hostname + " was not successful")
        abort(404)
    in_process = 1
    counter = 10
    check_args = SUPERVISORCTL + ['-s', 'http://localhost:9001', 'status', 'sync']
    while in_process == 1 and counter > 0:
        output, err = Popen(check_args, stdout=PIPE, stderr=PIPE).communicate()  # pylint: disable=unused-variable
        if not re.search(r'RUNNING', output.decode()):
            in_process = 0
        else:
            time.sleep(1)
        counter -= 1


def reset_process_running():
    if not USING_SUPERVISOR:
        return False
    check_args = SUPERVISORCTL + ['-s', 'http://localhost:9001', 'status', 'reset']
    output, err = Popen(check_args, stdout=PIPE, stderr=PIPE).communicate()  # pylint: disable=unused-variable
    if re.search(r'RUNNING', output.decode()):
        return True
    return False


def formatted_current_time():
    if current_user.timezone:
        the_timezone = zoneinfo.ZoneInfo(current_user.timezone)
    else:
        the_timezone = zoneinfo.ZoneInfo(DEFAULT_TIMEZONE)
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime('%H:%M:%S %Z')


def formatted_current_date():
    if current_user.timezone:
        the_timezone = zoneinfo.ZoneInfo(current_user.timezone)
    else:
        the_timezone = zoneinfo.ZoneInfo(DEFAULT_TIMEZONE)
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime("%Y-%m-%d")


TypeType = type(type(None))
NoneType = type(None)

# def elapsed(name_of_function):
#     def elapse_decorator(func):
#         def time_func(*pargs, **kwargs):
#             time_start = time.time()
#             result = func(*pargs, **kwargs)
#             logmessage(name_of_function + ': ' + str(time.time() - time_start))
#             return result
#         return time_func
#     return elapse_decorator



def fix_words():
    word_file_list = daconfig.get('words', [])
    if not isinstance(word_file_list, list):
        word_file_list = [word_file_list]
    for word_file in word_file_list:
        # logmessage("Reading from " + str(word_file))
        if not isinstance(word_file, str):
            logmessage("Error reading words: file references must be plain text.")
            continue
        filename = static_filename_path(word_file)
        if filename is None:
            logmessage("Error reading " + str(word_file) + ": file not found.")
            continue
        if os.path.isfile(filename):
            if filename.lower().endswith('.yaml') or filename.lower().endswith('.yml'):
                with open(filename, 'r', encoding='utf-8') as stream:
                    try:
                        for document in safeyaml.load_all(stream):
                            if document and isinstance(document, dict):
                                for lang, words in document.items():
                                    if isinstance(words, dict):
                                        update_word_collection(lang, words)
                                    else:
                                        logmessage("Error reading " + str(word_file) + ": words not in dictionary form.")
                            else:
                                logmessage("Error reading " + str(word_file) + ": yaml file not in dictionary form.")
                    except:
                        logmessage("Error reading " + str(word_file) + ": yaml could not be processed.")
            elif filename.lower().endswith('.xlsx'):
                try:
                    import pandas  # pylint: disable=import-outside-toplevel
                    df = pandas.read_excel(filename, na_values=['#NA', '#N/A'], keep_default_na=False)
                    invalid = False
                    for column_name in ('orig_lang', 'tr_lang', 'orig_text', 'tr_text'):
                        if column_name not in df.columns:
                            invalid = True
                            break
                    if invalid:
                        logmessage("Error reading " + str(word_file) + ": xlsx did not have the correct columns.")
                        continue
                    translations = {}
                    problems = []
                    for indexno in df.index:
                        try:
                            assert df['orig_lang'][indexno]
                            assert df['tr_lang'][indexno]
                            assert df['orig_text'][indexno] != ''
                            assert df['tr_text'][indexno] != ''
                            if isinstance(df['orig_text'][indexno], float):
                                assert not math.isnan(df['orig_text'][indexno])
                            if isinstance(df['tr_text'][indexno], float):
                                assert not math.isnan(df['tr_text'][indexno])
                        except:
                            problems.append(str(indexno + 2))
                            continue
                        if df['tr_lang'][indexno] not in translations:
                            translations[df['tr_lang'][indexno]] = {}
                        translations[df['tr_lang'][indexno]][str(df['orig_text'][indexno])] = str(df['tr_text'][indexno])
                    for lang, the_dict in translations.items():
                        try:
                            update_word_collection(lang, the_dict)
                        except:
                            logmessage("Error reading " + str(word_file) + ": xlsx for language " + lang + " could not be processed.")
                    if len(problems) > 0:
                        logmessage("Error reading " + str(word_file) + ": could not read lines " + ", ".join(problems) + ".")
                except BaseException as err:
                    logmessage("Error reading " + str(word_file) + ": xlsx processing raised exception " + err.__class__.__name__ + ": " + str(err))
            elif filename.lower().endswith('.xlf') or filename.lower().endswith('.xliff'):
                try:
                    tree = ET.parse(filename)
                    root = tree.getroot()
                    translations = {}
                    if root.attrib['version'] == "1.2":
                        for the_file in root.iter('{urn:oasis:names:tc:xliff:document:1.2}file'):
                            target_lang = the_file.attrib.get('target-language', 'en')
                            if target_lang not in translations:
                                translations[target_lang] = {}
                            for transunit in the_file.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
                                orig_text = ''
                                tr_text = ''
                                for source in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}source'):
                                    if source.text:
                                        orig_text += source.text
                                    for mrk in source:
                                        orig_text += mrk.text
                                        if mrk.tail:
                                            orig_text += mrk.tail
                                for target in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}target'):
                                    if target.text:
                                        tr_text += target.text
                                    for mrk in target:
                                        tr_text += mrk.text
                                        if mrk.tail:
                                            tr_text += mrk.tail
                                if orig_text == '' or tr_text == '':
                                    continue
                                translations[target_lang][orig_text] = tr_text
                    elif root.attrib['version'] == "2.0":
                        target_lang = root.attrib['trgLang']
                        if target_lang not in translations:
                            translations[target_lang] = {}
                        for segment in root.iter('{urn:oasis:names:tc:xliff:document:2.0}segment'):
                            orig_text = ''
                            tr_text = ''
                            for source in segment.iter('{urn:oasis:names:tc:xliff:document:2.0}source'):
                                if source.text:
                                    orig_text += source.text
                                for mrk in source:
                                    orig_text += mrk.text
                                    if mrk.tail:
                                        orig_text += mrk.tail
                            for target in segment.iter('{urn:oasis:names:tc:xliff:document:2.0}target'):
                                if target.text:
                                    tr_text += target.text
                                for mrk in target:
                                    tr_text += mrk.text
                                    if mrk.tail:
                                        tr_text += mrk.tail
                            if orig_text == '' or tr_text == '':
                                continue
                            translations[target_lang][orig_text] = tr_text
                    else:
                        logmessage("Error reading " + str(word_file) + ": invalid XLIFF version.")
                    for lang, the_dict in translations.items():
                        try:
                            update_word_collection(lang, the_dict)
                        except:
                            logmessage("Error reading " + str(word_file) + ": xlf for language " + lang + " could not be processed.")
                except BaseException as err:
                    logmessage("Error reading " + str(word_file) + ": xlf processing raised exception " + err.__class__.__name__ + ": " + str(err))
            else:
                logmessage("filename " + filename + " had an unknown type")
        else:
            logmessage("filename " + filename + " did not exist")


if 'currency symbol' in daconfig:
    update_language_function('*', 'currency_symbol', lambda: daconfig['currency symbol'])


@hookimpl(specname="google_api")
def get_google_api():
    import docassemble.webapp.google_api  # pylint: disable=import-outside-toplevel, redefined-outer-name
    return docassemble.webapp.google_api


def parse_the_user_id(the_user_id):
    if the_user_id is None:
        return (None, None)
    m = re.match(r'(t?)([0-9]+)', str(the_user_id))
    if m:
        if m.group(1) == 't':
            return None, int(m.group(2))
        return int(m.group(2)), None
    raise DAException("Invalid user ID")


def nice_utc_date(timestamp):
    return timestamp.strftime('%F %T')


def illegal_variable_name(var):
    if re.search(r'[\n\r]', var):
        return True
    try:
        t = ast.parse(var)
    except:
        return True
    detector = docassemble.base.astparser.DetectIllegal()
    detector.visit(t)
    return detector.illegal


def illegal_sessions_query(expr):
    if re.search(r'[\n\r]', expr):
        return True
    try:
        t = ast.parse(expr)
    except:
        return True
    detector = docassemble.base.astparser.DetectIllegalQuery()
    detector.visit(t)
    return detector.illegal


def mako_parts(expression):
    in_percent = False
    in_var = False
    in_square = False
    var_depth = 0
    in_colon = 0
    in_html = 0
    in_pre_bracket = False
    in_post_bracket = False
    output = []
    current = ''
    i = 0
    expression = emoji_match.sub(r'^^\1^^', expression)
    expression = html_match.sub(r'!@\1!@', expression)
    n = len(expression)
    while i < n:
        if in_html:
            if i + 1 < n and expression[i:i+2] == '!@':
                in_html = False
                if current != '':
                    output.append([current, 2])
                current = ''
                i += 2
            else:
                current += expression[i]
                i += 1
            continue
        if in_percent:
            if expression[i] in ["\n", "\r"]:
                in_percent = False
                current += expression[i]
                output.append([current, 1])
                current = ''
                i += 1
                continue
        elif in_var:
            if expression[i] == '{' and expression[i-1] != "\\":
                var_depth += 1
            elif expression[i] == '}' and expression[i-1] != "\\":
                var_depth -= 1
                if var_depth == 0:
                    current += expression[i]
                    if current != '':
                        output.append([current, 2])
                    current = ''
                    in_var = False
                    i += 1
                    continue
        elif in_pre_bracket:
            if i + 2 < n:
                if expression[i:i+3] == '</%':
                    in_pre_bracket = False
                    in_post_bracket = True
                    current += expression[i:i+3]
                    i += 3
                    continue
            if i + 1 < n and expression[i:i+2] == '%>':
                in_pre_bracket = False
                current += expression[i:i+2]
                if current != '':
                    output.append([current, 1])
                current = ''
                i += 2
                continue
        elif in_post_bracket:
            if expression[i] == '>' and expression[i-1] != "\\":
                current += expression[i]
                if current != '':
                    output.append([current, 1])
                current = ''
                in_post_bracket = False
                i += 1
                continue
        elif in_square:
            if expression[i] == ']' and (i == 0 or expression[i-1] != "\\"):
                mode = 0
                current += expression[i]
                for pattern in ['[FILE', '[TARGET ', '[EMOJI ', '[QR ', '[YOUTUBE', '[VIMEO]', '[PAGENUM]', '[BEGIN_TWOCOL]', '[BREAK]', '[END_TWOCOL', '[BEGIN_CAPTION]', '[VERTICAL_LINE]', '[END_CAPTION]', '[TIGHTSPACING]', '[SINGLESPACING]', '[DOUBLESPACING]', '[ONEANDAHALFSPACING]', '[TRIPLESPACING]', '[START_INDENTATION]', '[STOP_INDENTATION]', '[NBSP]', '[REDACTION', '[ENDASH]', '[EMDASH]', '[HYPHEN]', '[CHECKBOX]', '[BLANK]', '[BLANKFILL]', '[PAGEBREAK]', '[PAGENUM]', '[SECTIONNUM]', '[SKIPLINE]', '[NEWLINE]', '[NEWPAR]', '[BR]', '[TAB]', '[END]', '[BORDER]', '[NOINDENT]', '[FLUSHLEFT]', '[FLUSHRIGHT]', '[CENTER]', '[BOLDCENTER]', '[NO_EMOJIS]', '[INDENTBY', '[${']:
                    if current.startswith(pattern):
                        mode = 2
                        break
                if current != '':
                    output.append([current, mode])
                current = ''
                in_square = False
                i += 1
                continue
            if i + 1 < n and expression[i:i+2] == '^^':
                if in_colon:
                    in_colon = False
                    current += ':'
                    output.append([current, 2])
                    current = ''
                else:
                    in_colon = True
                    if current.startswith('[${'):
                        output.append([current, 2])
                    else:
                        output.append([current, 0])
                    current = ':'
                i += 2
                continue
            if i + 1 < n and expression[i:i+2] == '!@':
                in_html = True
                if current != '':
                    if current.startswith('[${'):
                        output.append([current, 2])
                    else:
                        output.append([current, 0])
                current = ''
                i += 2
                continue
        elif in_colon:
            if i + 1 < n and expression[i:i+2] == '^^':
                current += ':'
                if current != '':
                    output.append([current, 2])
                current = ''
                in_colon = False
                i += 2
                continue
        elif i + 1 < n:
            if expression[i:i+2] == '${':
                in_var = True
                var_depth += 1
                if current != '':
                    output.append([current, 0])
                current = expression[i:i+2]
                i += 2
                continue
            if expression[i:i+2] == '^^':
                in_colon = True
                if current != '':
                    output.append([current, 0])
                current = ':'
                i += 2
                continue
            if expression[i:i+2] == '!@':
                in_html = True
                if current != '':
                    output.append([current, 0])
                current = ''
                i += 2
                continue
            if expression[i:i+2] == '<%':
                in_pre_bracket = True
                if current != '':
                    output.append([current, 0])
                current = expression[i:i+2]
                i += 2
                continue
            if expression[i:i+2] == '% ' and start_of_line(expression, i):
                in_percent = True
                if current != '':
                    output.append([current, 0])
                current = expression[i:i+2]
                i += 2
                continue
            if expression[i] == '[' and (i == 0 or expression[i-1] != "\\"):
                in_square = True
                if current != '':
                    output.append([current, 0])
                current = expression[i]
                i += 1
                continue
        current += expression[i]
        i += 1
    if current != '':
        if in_pre_bracket or in_post_bracket or in_percent:
            output.append([current, 1])
        elif in_var:
            output.append([current, 2])
        else:
            output.append([current, 0])
    return output


def start_of_line(expression, i):
    if i == 0:
        return True
    i -= 1
    while i >= 0:
        if expression[i] in ("\n", "\r"):
            return True
        if expression[i] in (" ", "\t"):
            i -= 1
            continue
        return False
    return True


@hookimpl
def applock(action, application, maxtime):
    if maxtime is None:
        maxtime = 4
    key = 'da:applock:' + application + ':' + hostname
    if action == 'obtain':
        found = False
        count = maxtime
        while count > 0:
            record = r.get(key)
            if record:
                logmessage("obtain_applock: waiting for " + key)
                time.sleep(1.0)
            else:
                found = False
                break
            found = True
            count -= 1
        if found:
            logmessage("Request for applock " + key + " deadlocked")
            r.delete(key)
        pipe = r.pipeline()
        pipe.set(key, 1)
        pipe.expire(key, maxtime)
        pipe.execute()
    elif action == 'release':
        r.delete(key)


def fix_http(url):
    if HTTP_TO_HTTPS:
        return re.sub(r'^http:', 'https:', url)
    return url


def safe_quote_func(string, safe='', encoding=None, errors=None):  # pylint: disable=unused-argument
    return urllibquote(string, safe='', encoding=encoding, errors=errors)


def remove_question_package(args):
    if '_question' in args:
        del args['_question']
    if '_package' in args:
        del args['_package']


def encrypt_next(args):
    if 'next' not in args:
        return
    args['next'] = re.sub(r'\s', '', encrypt_phrase(args['next'], current_app.secret_key)).rstrip('=')


@hookimpl(specname="url_finder")
def get_url_from_file_reference(file_reference, kwargs):
    if 'jsembed' in this_thread.misc or COOKIELESS_SESSIONS:
        kwargs['_external'] = True
    privileged = kwargs.get('privileged', False)
    if isinstance(file_reference, DAFileList) and len(file_reference.elements) > 0:
        file_reference = file_reference.elements[0]
    elif isinstance(file_reference, DAFileCollection):
        file_reference = file_reference._first_file()
    elif isinstance(file_reference, DAStaticFile):
        return file_reference.url_for(**kwargs)
    if isinstance(file_reference, DAFile) and hasattr(file_reference, 'number'):
        file_number = file_reference.number
        if privileged or can_access_file_number(file_number, uids=get_session_uids()):
            url_properties = {}
            if hasattr(file_reference, 'filename') and len(file_reference.filename) and file_reference.has_specific_filename:
                url_properties['display_filename'] = file_reference.filename
            if hasattr(file_reference, 'extension'):
                url_properties['ext'] = file_reference.extension
            for key, val in kwargs.items():
                url_properties[key] = val
            the_file = SavedFile(file_number)
            if kwargs.get('temporary', False):
                return the_file.temp_url_for(**url_properties)
            return the_file.url_for(**url_properties)
    file_reference = str(file_reference)
    if re.search(r'^https?://', file_reference) or re.search(r'^mailto:', file_reference) or file_reference.startswith('/') or file_reference.startswith('?'):
        if '?' not in file_reference:
            args = {}
            for key, val in kwargs.items():
                if key in ('_package', '_question', '_external'):
                    continue
                args[key] = val
            if len(args) > 0:
                if file_reference.startswith('mailto:') and 'body' in args:
                    args['body'] = re.sub(r'(?<!\r)\n', '\r\n', args['body'], re.MULTILINE)
                return file_reference + '?' + urlencode(args, quote_via=safe_quote_func)
        return file_reference
    kwargs_with_i = copy.copy(kwargs)
    if 'i' not in kwargs_with_i:
        yaml_filename = this_thread.current_info.get('yaml_filename', None)
        if yaml_filename is not None:
            kwargs_with_i['i'] = yaml_filename
    if file_reference in ('login', 'signin'):
        remove_question_package(kwargs)
        return url_for('user.login', **kwargs)
    if file_reference == 'profile':
        remove_question_package(kwargs)
        return url_for('users.user_profile_page', **kwargs)
    if file_reference == 'change_password':
        remove_question_package(kwargs)
        return url_for('user.change_password', **kwargs)
    if file_reference == 'register':
        remove_question_package(kwargs)
        return url_for('user.register', **kwargs)
    if file_reference == 'config':
        remove_question_package(kwargs)
        return url_for('admin.config_page', **kwargs)
    if file_reference == 'leave':
        remove_question_package(kwargs)
        encrypt_next(kwargs)
        return url_for('interview.leave', **kwargs)
    if file_reference == 'logout':
        remove_question_package(kwargs)
        encrypt_next(kwargs)
        return url_for('user.logout', **kwargs)
    if file_reference == 'restart':
        remove_question_package(kwargs_with_i)
        return url_for('interview.restart_session', **kwargs_with_i)
    if file_reference == 'new_session':
        remove_question_package(kwargs_with_i)
        return url_for('interview.new_session_endpoint', **kwargs_with_i)
    if file_reference == 'help':
        return 'javascript:daShowHelpTab()'
    if file_reference == 'interview':
        remove_question_package(kwargs)
        modify_i_argument(kwargs)
        return url_for('interview.index', **kwargs)
    if file_reference == 'flex_interview':
        remove_question_package(kwargs)
        how_called = this_thread.misc.get('call', None)
        if how_called is None:
            return url_for('interview.index', **kwargs)
        try:
            if int(kwargs.get('new_session')):
                is_new = True
                del kwargs['new_session']
            else:
                is_new = False
        except:
            is_new = False
        if how_called[0] in ('start', 'run'):
            del kwargs['i']
            kwargs['package'] = how_called[1]
            kwargs['filename'] = how_called[2]
            if is_new:
                return url_for('interview.redirect_to_interview_in_package', **kwargs)
            return url_for('interview.run_interview_in_package', **kwargs)
        if how_called[0] in ('start_dispatch', 'run_dispatch'):
            del kwargs['i']
            kwargs['dispatch'] = how_called[1]
            if is_new:
                return url_for('interview.redirect_to_interview', **kwargs)
            return url_for('interview.run_interview', **kwargs)
        if how_called[0] in ('start_directory', 'run_directory'):
            del kwargs['i']
            kwargs['package'] = how_called[1]
            kwargs['directory'] = how_called[2]
            kwargs['filename'] = how_called[3]
            if is_new:
                return url_for('interview.redirect_to_interview_in_package_directory', **kwargs)
            return url_for('interview.run_interview_in_package_directory', **kwargs)
        if is_new:
            kwargs['new_session'] = 1
        return url_for('interview.index', **kwargs)
    if file_reference == 'interviews':
        remove_question_package(kwargs)
        return url_for('admin.interview_list', **kwargs)
    if file_reference == 'exit':
        remove_question_package(kwargs_with_i)
        encrypt_next(kwargs_with_i)
        return url_for('interview.exit_endpoint', **kwargs_with_i)
    if file_reference == 'exit_logout':
        remove_question_package(kwargs_with_i)
        encrypt_next(kwargs_with_i)
        return url_for('interview.exit_logout', **kwargs_with_i)
    if file_reference == 'dispatch':
        remove_question_package(kwargs)
        return url_for('admin.interview_start', **kwargs)
    if file_reference == 'manage':
        remove_question_package(kwargs)
        return url_for('users.manage_account', **kwargs)
    if file_reference == 'interview_list':
        remove_question_package(kwargs)
        return url_for('admin.interview_list', **kwargs)
    if file_reference == 'playground':
        remove_question_package(kwargs)
        return url_for('develop.playground_page', **kwargs)
    if file_reference == 'playgroundtemplate':
        kwargs['section'] = 'template'
        remove_question_package(kwargs)
        return url_for('develop.playground_files', **kwargs)
    if file_reference == 'playgroundstatic':
        kwargs['section'] = 'static'
        remove_question_package(kwargs)
        return url_for('develop.playground_files', **kwargs)
    if file_reference == 'playgroundsources':
        kwargs['section'] = 'sources'
        remove_question_package(kwargs)
        return url_for('develop.playground_files', **kwargs)
    if file_reference == 'playgroundmodules':
        kwargs['section'] = 'modules'
        remove_question_package(kwargs)
        return url_for('develop.playground_files', **kwargs)
    if file_reference == 'playgroundpackages':
        remove_question_package(kwargs)
        return url_for('develop.playground_packages', **kwargs)
    if file_reference == 'playgroundfiles':
        remove_question_package(kwargs)
        return url_for('develop.playground_files', **kwargs)
    if file_reference == 'create_playground_package':
        remove_question_package(kwargs)
        return url_for('develop.create_playground_package', **kwargs)
    if file_reference == 'configuration':
        remove_question_package(kwargs)
        return url_for('admin.config_page', **kwargs)
    if file_reference == 'root':
        remove_question_package(kwargs)
        return url_for('interview.rootindex', **kwargs)
    if file_reference == 'run':
        remove_question_package(kwargs)
        return url_for('interview.run_interview_in_package', **kwargs)
    if file_reference == 'run_dispatch':
        remove_question_package(kwargs)
        return url_for('interview.run_interview', **kwargs)
    if file_reference == 'run_new':
        remove_question_package(kwargs)
        return url_for('interview.redirect_to_interview_in_package', **kwargs)
    if file_reference == 'run_new_dispatch':
        remove_question_package(kwargs)
        return url_for('interview.redirect_to_interview', **kwargs)
    if re.search('^[0-9]+$', file_reference):
        remove_question_package(kwargs)
        file_number = file_reference
        if kwargs.get('temporary', False):
            url = SavedFile(file_number).temp_url_for(**kwargs)
        elif can_access_file_number(file_number, uids=get_session_uids()):
            url = SavedFile(file_number).url_for(**kwargs)
        else:
            logmessage("Problem accessing " + str(file_number))
            url = 'about:blank'
    else:
        question = kwargs.get('_question', None)
        package_arg = kwargs.get('_package', None)
        if 'ext' in kwargs and kwargs['ext'] is not None:
            extn = kwargs['ext']
            extn = re.sub(r'^\.', '', extn)
            extn = '.' + extn
        else:
            extn = ''
        parts = file_reference.split(':')
        if len(parts) < 2:
            file_reference = re.sub(r'^data/static/', '', file_reference)
            the_package = None
            if question is not None and question.from_source is not None and hasattr(question.from_source, 'package'):
                the_package = question.from_source.package
            if the_package is None and package_arg is not None:
                the_package = package_arg
            if the_package is None:
                the_package = 'docassemble.base'
            parts = [the_package, file_reference]
        parts[1] = re.sub(r'^data/[^/]+/', '', parts[1])
        url = url_if_exists(parts[0] + ':data/static/' + parts[1] + extn, **kwargs)
    return url


def get_base_words():
    documentation = get_info_from_file_reference('docassemble.base:data/sources/base-words.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'r', encoding='utf-8') as fp:
            content = fp.read()
            content = fix_tabs.sub('  ', content)
            return safeyaml.load(content)
    return None



def get_pg_code_cache():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/pgcodecache.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'r', encoding='utf-8') as fp:
            content = fp.read()
            content = fix_tabs.sub('  ', content)
            if not content:
                return {}
            return safeyaml.load(content)
    return {}


def get_documentation_dict():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'r', encoding='utf-8') as fp:
            content = fp.read()
            content = fix_tabs.sub('  ', content)
            return safeyaml.load(content)
    return None


def get_name_info():
    docstring = get_info_from_file_reference('docassemble.base:data/questions/docstring.yml')
    if 'fullpath' in docstring and docstring['fullpath'] is not None:
        with open(docstring['fullpath'], 'r', encoding='utf-8') as fp:
            content = fp.read()
            content = fix_tabs.sub('  ', content)
            info = safeyaml.load(content)
        for val in info:
            info[val]['name'] = val
            if 'insert' not in info[val]:
                info[val]['insert'] = val
            if 'show' not in info[val]:
                info[val]['show'] = False
            if 'exclude' not in info[val]:
                info[val]['exclude'] = False
        return info
    return None


def get_title_documentation():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/title_documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'r', encoding='utf-8') as fp:
            content = fp.read()
            content = fix_tabs.sub('  ', content)
            return safeyaml.load(content)
    return None


def pad_to_16(the_string):
    if len(the_string) >= 16:
        return the_string[:16]
    return str(the_string) + (16 - len(the_string)) * '0'


def MD5Hash(data=None):
    if data is None:
        data = ''
    h = MD5.new()
    h.update(bytearray(data, encoding='utf-8'))
    return h


def set_request_active(value):
    global request_active
    request_active = value


@hookimpl(specname="get_url")
def get_request_url():
    return {'args': dict(request.args),
            'base_url': request.base_url,
            'full_path': request.full_path,
            'path': request.path,
            'scheme': request.scheme,
            'url': request.url,
            'url_root': request.url_root}


def verify_email(email):
    if len(daconfig['authorized registration domains']) != 0:
        ok = False
        email = str(email).lower().strip()
        for domain in daconfig['authorized registration domains']:
            if email.endswith(domain):
                ok = True
                break
        if not ok:
            return False
    return True


def jsonify_with_status(data, code):
    resp = jsonify(data)
    resp.status_code = code
    return resp


def true_or_false(text):
    if text in (False, None) or text == 0 or str(text).lower().strip() in ('0', 'false', 'f'):
        return False
    return True


def title_converter(content, part, status):
    if part in ('exit link', 'exit url', 'title url', 'title url opens in other window'):
        return content
    if part in ('title', 'subtitle', 'short title', 'tab title', 'exit label', 'back button label', 'corner back button label', 'logo', 'short logo', 'navigation bar html'):
        return docassemble.base.util.markdown_to_html(content, status=status, trim=True, do_terms=False)
    return docassemble.base.util.markdown_to_html(content, status=status)


def get_next_link(resp):
    if 'link' in resp and resp['link']:
        link_info = links_from_header.extract(resp['link'])
        if 'next' in link_info:
            return link_info['next']
    return None


def jsonify_with_cache(*pargs, **kwargs):
    response = jsonify(*pargs, **kwargs)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def json64unquote(text):
    try:
        return json.loads(myb64unquote(text))
    except:
        return {}


def tidy_action(action):
    result = {}
    if not isinstance(action, dict):
        return result
    if 'action' in action:
        result['action'] = action['action']
    if 'arguments' in action:
        result['arguments'] = action['arguments']
    return result


def make_response_wrapper(set_cookie, secret, set_device_id, device_id, expire_visitor_secret):

    def the_wrapper(response):
        if set_cookie:
            response.set_cookie('secret', secret, httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'])
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
        if set_device_id:
            response.set_cookie('ds', device_id, httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'], expires=datetime.datetime.now() + datetime.timedelta(weeks=520))
    return the_wrapper


def populate_social(social, metadata):
    for key in ('image', 'description'):
        if key in metadata:
            if metadata[key] is None:
                if key in social:
                    del social[key]
            elif isinstance(metadata[key], str):
                social[key] = metadata[key].replace('\n', ' ').replace('"', '&quot;').strip()
    for key in ('og', 'fb', 'twitter'):
        if key in metadata and isinstance(metadata[key], dict):
            for subkey, val in metadata[key].items():
                if val is None:
                    if subkey in social[key]:
                        del social[key][subkey]
                elif isinstance(val, str):
                    social[key][subkey] = val.replace('\n', ' ').replace('"', '&quot;').strip()


def is_mobile_or_tablet():
    ua_string = request.headers.get('User-Agent', None)
    if ua_string is not None:
        response = ua_parse(ua_string)
        if response.is_mobile or response.is_tablet:
            return True
    return False


@hookimpl
def get_referer():
    return request.referrer or None


def add_referer(user_dict, referer=None):
    if referer:
        user_dict['_internal']['referer'] = referer
    elif request.referrer:
        user_dict['_internal']['referer'] = request.referrer
    else:
        user_dict['_internal']['referer'] = None


def decode_dict(the_dict):
    out_dict = {}
    for k, v in the_dict.items():
        out_dict[k.decode()] = v.decode()
    return out_dict


def get_master_branch(giturl):
    try:
        return get_repo_info(giturl).get('default_branch', GITHUB_BRANCH)
    except:
        return GITHUB_BRANCH


def docx_variable_fix(variable):
    variable = re.sub(r'\\', '', variable)
    variable = re.sub(r'^([A-Za-z\_][A-Za-z\_0-9]*).*', r'\1', variable)
    return variable


def sanitize(default):
    default = re.sub(r'\n?\r\n?', "\n", str(default))
    if re.search(r'[\#\!\?\:\n\r\"\'\[\]\{\}]+', default):
        return "|\n" + indent(default, by=10)
    return default


def parse_api_sessions_query(query):
    if query is None or query.strip() == '':
        return None
    if illegal_sessions_query(query):
        raise DAException("Illegal query")
    return eval(query, {'DA': docassemble.base.DA})


@hookimpl
def transform_json_variables(obj):
    if isinstance(obj, str):
        if re.search(r'^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', obj):
            try:
                return docassemble.base.util.as_datetime(dateutil.parser.parse(obj))
            except:
                pass
        elif re.search(r'^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]', obj):
            try:
                return datetime.time.fromisoformat(obj)
            except:
                pass
        return obj
    if isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, dict):
        if '_class' in obj and obj['_class'] == 'type' and 'name' in obj and isinstance(obj['name'], str) and obj['name'].startswith('docassemble.') and not illegal_variable_name(obj['name']):
            if '.' in obj['name']:
                the_module = re.sub(r'\.[^\.]+$', '', obj['name'])
            else:
                the_module = None
            try:
                if the_module:
                    importlib.import_module(the_module)
                new_obj = eval(obj['name'])
                if not isinstance(new_obj, TypeType):
                    raise DAException("name is not a class")
                return new_obj
            except BaseException as err:
                logmessage("transform_json_variables: " + err.__class__.__name__ + ": " + str(err))
                return None
        if '_class' in obj and isinstance(obj['_class'], str) and 'instanceName' in obj and obj['_class'].startswith('docassemble.') and not illegal_variable_name(obj['_class']) and isinstance(obj['instanceName'], str):
            the_module = re.sub(r'\.[^\.]+$', '', obj['_class'])
            try:
                importlib.import_module(the_module)
                the_class = eval(obj['_class'])
                if not isinstance(the_class, TypeType):
                    raise DAException("_class was not a class")
                new_obj = the_class(obj['instanceName'])
                for key, val in obj.items():
                    if key == '_class':
                        continue
                    setattr(new_obj, key, transform_json_variables(val))
                return new_obj
            except BaseException as err:
                logmessage("transform_json_variables: " + err.__class__.__name__ + ": " + str(err))
                return None
        new_dict = {}
        for key, val in obj.items():
            new_dict[transform_json_variables(key)] = transform_json_variables(val)
        return new_dict
    if isinstance(obj, list):
        return [transform_json_variables(val) for val in obj]
    if isinstance(obj, set):
        return set(transform_json_variables(val) for val in obj)
    return obj


def uid_or_random(yaml_filename):
    session_info = get_session(yaml_filename)
    if session_info is not None:
        return session_info['uid']
    return random_alphanumeric(32)


def jsonify_task(result):
    while True:
        code = random_string(24)
        the_key = 'da:install_status:' + code
        if r.get(the_key) is None:
            break
    pipe = r.pipeline()
    pipe.set(the_key, json.dumps({'id': result.id, 'server_start_time': START_TIME}))
    pipe.expire(the_key, 3600)
    pipe.execute()
    return jsonify({'task_id': code})


def jsonify_restart_task():
    while True:
        code = random_string(24)
        the_key = 'da:restart_status:' + code
        if r.get(the_key) is None:
            break
    pipe = r.pipeline()
    pipe.set(the_key, json.dumps({'server_start_time': START_TIME}))
    pipe.expire(the_key, 3600)
    pipe.execute()
    return jsonify({'task_id': code, 'success': True})


def should_run_create(package_name):
    if package_name in ('docassemble.base', 'docassemble.webapp', 'docassemble.demo', 'docassemble'):
        return True
    return False


def page_after_login():
    if current_user.is_authenticated:
        for role, page in daconfig['page after login']:
            if role == '*' or current_user.has_role(role):
                return page
    return None


@hookimpl
def register_db(db_name):
    if db_name in db.engines:
        return db
    url = docassemble.webapp.user_database.alchemy_url(db_name)
    bind = {'url': url, 'pool_pre_ping': daconfig.get('sql ping', False)}
    connect_args = docassemble.webapp.user_database.connect_args(db_name)
    if connect_args:
        bind['connect_args'] = connect_args
    if url.startswith('postgres'):
        engine = create_engine(url, connect_args=connect_args, pool_pre_ping=daconfig.get('sql ping', False))
    else:
        engine = create_engine(url, pool_pre_ping=daconfig.get('sql ping', False))
    db._make_metadata(db_name)
    db._app_engines[current_app._get_current_object()][db_name] = engine
    return db


@hookimpl
def create_objects_in_db(db_name):
    db.create_all(bind_key=db_name)
    url = docassemble.webapp.user_database.alchemy_url(db_name)
    conn_args = docassemble.webapp.user_database.connect_args(db_name)
    return (url, conn_args, db.engines[db_name])


def get_base_url():
    return re.sub(r'^(https?://[^/]+).*', r'\1', url_for('interview.rootindex', _external=True))


def null_func(*pargs, **kwargs):  # pylint: disable=unused-argument
    logmessage("Null function called")


base_name_info = {}
title_documentation = {}
documentation_dict = {}
pg_code_cache = {}

def populate_dicts():
    base_name_info.clear()
    base_name_info.update(get_name_info())
    pg_code_cache.clear()
    pg_code_cache.update(get_pg_code_cache())
    title_documentation.clear()
    title_documentation.update(get_title_documentation())
    documentation_dict.clear()
    documentation_dict.update(get_documentation_dict())

DOCUMENTATION_BASE = daconfig.get('documentation base url', 'https://docassemble.org/docs/')
