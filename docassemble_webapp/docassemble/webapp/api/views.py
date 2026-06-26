import json
import re
from urllib.parse import quote_plus as urllibquoteplus
from flask import render_template, request, flash, current_app
from flask_login import current_user
from markupsafe import Markup
from docassemble_flask_user import login_required
from docassemble.base.generate_key import random_alphanumeric
from docassemble.base.language.words import word
from docassemble.webapp.config import (
    daconfig,
    NOTIFICATION_MESSAGE,
    PERMISSIONS_LIST,
    DEFER,
    NOTIFICATION_CONTAINER,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.utils.api_key import encrypt_api_key
from docassemble.webapp.utils.helpers import redis_script, get_requester_ip
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from .blueprint import api_bp
from .forms import APIKey

@api_bp.route('/manage_api', methods=['GET', 'POST'])
@login_required
def manage_api():
    setup_translation()
    if not current_user.has_role(*daconfig.get('api privileges', ['admin', 'developer'])):
        return ('File not found', 404)
    form = APIKey(request.form)
    action = request.args.get('action', None)
    api_key = request.args.get('key', None)
    is_admin = current_user.has_role('admin')
    argu = {'is_admin': is_admin}
    argu['mode'] = 'list'
    if action is None:
        action = 'list'
    argu['form'] = form
    initial_values = {
        "daIpPlaceholder": word('e.g., 56.33.114.49'),
        "daHostnamePlaceholder": word('e.g., *example.com'),
        "daApiKeyCopied": word('API key copied to clipboard.'),
        "daNotificationContainer": NOTIFICATION_CONTAINER,
        "daNotificationMessage": NOTIFICATION_MESSAGE,
    }
    argu['extra_js'] = Markup(f"""\n    <script{DEFER} src="{url_for('static', filename="app/manage_api.min.js")}"></script>\n    {redis_script(initial_values)}""")
    form.method.choices = [('ip', word('IP Address')), ('referer', word('Referring URL')), ('none', word('No authentication'))]
    if is_admin:
        form.permissions.choices = [(permission, permission) for permission in PERMISSIONS_LIST]
    else:
        form.permissions.choices = []
    ip_address = get_requester_ip(request)
    if request.method == 'POST' and form.validate():
        action = form.action.data
        try:
            constraints = json.loads(form.security.data)
            if not isinstance(constraints, list):
                constraints = []
        except:
            constraints = []
        if action == 'new':
            argu['title'] = word("New API Key")
            argu['tab_title'] = argu['title']
            argu['page_title'] = argu['title']
            permissions_data = form.permissions.data if is_admin else []
            info = {'name': form.name.data, 'method': form.method.data, 'constraints': constraints, 'limits': permissions_data}
            success = False
            for attempt in range(10):  # pylint: disable=unused-variable
                api_key = random_alphanumeric(32)
                info['last_four'] = api_key[-4:]
                new_api_key = encrypt_api_key(api_key, current_app.secret_key)
                if len(r.keys('da:apikey:userid:*:key:' + new_api_key + ':info')) == 0:
                    r.set('da:apikey:userid:' + str(current_user.id) + ':key:' + new_api_key + ':info', json.dumps(info))
                    success = True
                    break
            if not success:
                flash(word("Could not create new key"), 'error')
                return render_template('api/manage_api.html', **argu)
            argu['description'] = Markup(
                    """<div class="card bg-info-subtle mb-3">
                      <div class="card-body">
                        <p class="card-text">
                        """ + (word("Your new API key, known internally as <strong>%s</strong>, is:<br />%s<br />") % (form.name.data, '<br /><span class="text-success"><i class="fa-solid fa-check"></i></span> <code id="daApiKey">' + api_key + '</code><wbr /><button aria-label=' + json.dumps(word("Copy API key")) + ' onclick="daCopyToClipboard()" class="btn btn-link ps-1 pt-1" type="button"><i class="fa-regular fa-copy"></i></button>')) + """
                        </p>
                        <p class="card-text">
                      """ + word("<strong>This is the only time you will be able to see your API key</strong>, so make sure to make a note of it and keep it in a secure place.") + """
                        </p>
                      </div>
                    </div>""")

        elif action == 'edit':
            argu['title'] = word("Edit API Key")
            argu['tab_title'] = argu['title']
            argu['page_title'] = argu['title']
            api_key = form.key.data
            argu['api_key'] = api_key
            rkey = 'da:apikey:userid:' + str(current_user.id) + ':key:' + str(form.key.data) + ':info'
            existing_key = r.get(rkey)
            if existing_key is None:
                flash(word("The key no longer exists"), 'error')
                return render_template('api/manage_api.html', **argu)
            existing_key = existing_key.decode()
            if form.delete.data:
                r.delete(rkey)
                flash(word("The key was deleted"), 'info')
            else:
                try:
                    info = json.loads(existing_key)
                except:
                    flash(word("The key no longer exists"), 'error')
                    return render_template('api/manage_api.html', **argu)
                info['name'] = form.name.data
                if form.method.data != info['method'] and form.method.data in ('ip', 'referer'):
                    info['method'] = form.method.data
                info['constraints'] = constraints
                if is_admin:
                    info['permissions'] = form.permissions.data
                else:
                    info['permissions'] = []
                r.set(rkey, json.dumps(info))
        action = 'list'
    if action == 'new':
        argu['title'] = word("New API Key")
        argu['tab_title'] = argu['title']
        argu['page_title'] = argu['title']
        argu['mode'] = 'new'
    if api_key is not None and action == 'edit':
        argu['title'] = word("Edit API Key")
        argu['tab_title'] = argu['title']
        argu['page_title'] = argu['title']
        argu['api_key'] = api_key
        argu['mode'] = 'edit'
        rkey = 'da:apikey:userid:' + str(current_user.id) + ':key:' + api_key + ':info'
        info = r.get(rkey)
        if info is not None:
            info = json.loads(info.decode())
            if isinstance(info, dict) and info.get('name', None) and info.get('method', None):
                argu['method'] = info.get('method')
                form.method.data = info.get('method')
                form.action.data = 'edit'
                form.key.data = api_key
                form.name.data = info.get('name')
                if is_admin:
                    if 'permissions' in info:
                        form.permissions.data = info['permissions']
                    else:
                        form.permissions.data = []
                argu['constraints'] = info.get('constraints')
                argu['display_key'] = ('*' * 28) + info.get('last_four')
        if ip_address != '127.0.0.1':
            argu['description'] = Markup(word("Your IP address is") + " <code>" + str(ip_address) + "</code>.")
    if action == 'list':
        argu['title'] = word("API Keys")
        argu['tab_title'] = argu['title']
        argu['page_title'] = argu['title']
        argu['mode'] = 'list'
        avail_keys = []
        for rkey in r.keys('da:apikey:userid:' + str(current_user.id) + ':key:*:info'):
            rkey = rkey.decode()
            try:
                info = json.loads(r.get(rkey).decode())
                if not isinstance(info, dict):
                    logmessage("manage_api: response from redis was not a dict")
                    continue
            except:
                logmessage("manage_api: response from redis had invalid json")
                continue
            m = re.match(r'da:apikey:userid:[0-9]+:key:([^:]+):info', rkey)
            if not m:
                logmessage("manage_api: error with redis key")
                continue
            api_key = m.group(1)
            info['encoded_api_key'] = urllibquoteplus(api_key)
            avail_keys.append(info)
        argu['avail_keys'] = avail_keys
        argu['has_any_keys'] = bool(len(avail_keys) > 0)
    return render_template('api/manage_api.html', **argu)
