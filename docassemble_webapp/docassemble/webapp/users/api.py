import re
import json
import email as emailpackage
from flask import request, jsonify, current_app
from flask_cors import cross_origin
from flask_login import current_user
from sqlalchemy import select
import docassemble_flask_user
from docassemble.base.generate_key import random_alphanumeric
from docassemble.webapp.api.helpers import api_verify
from docassemble.webapp.daredis import r_user, r
from docassemble.webapp.extensions import csrf, db
from docassemble.webapp.interview.helpers import (
    user_interviews,
    delete_user_data,
)
from docassemble.webapp.utils.helpers import (
    jsonify_with_status,
    true_or_false,
    url_for,
    from_safeid,
    safeid,
)
from docassemble.webapp.utils.logger import logmessage
from .blueprint import users_bp
from .loginurl import get_login_url
from .helpers import (
    add_privilege,
    get_secret,
    add_user_privilege,
    make_user_inactive,
    get_user_info,
    remove_privilege,
    remove_user_privilege,
    get_privileges_list,
    get_user_list,
    create_user,
    set_user_info,
)
from .models import MyUserInvitation, Role

@users_bp.route('/api/user', methods=['GET', 'POST', 'PATCH'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'PATCH', 'HEAD'], automatic_options=True)
def api_user():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    if current_user.limited_api and not current_user.can_do('access_user_info'):
        return jsonify_with_status("You do not have sufficient privileges to access user information", 403)
    try:
        user_info = get_user_info(user_id=current_user.id)
    except BaseException as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status('User not found', 404)
    if request.method == 'GET':
        return jsonify(user_info)
    if request.method in ('POST', 'PATCH'):
        if current_user.limited_api and not current_user.can_do('edit_user_info'):
            return jsonify_with_status("You do not have sufficient privileges to edit a user's information", 403)
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        info = {}
        for key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language', 'password', 'old_password'):
            if key in post_data:
                info[key] = post_data[key]
        if 'password' in info and not current_user.has_role_or_permission('admin', permissions='edit_user_password'):
            return jsonify_with_status("You do not have sufficient privileges to change a user's password.", 403)
        try:
            set_user_info({"user_id": current_user.id, **info})
        except BaseException as err:
            return jsonify_with_status(str(err), 400)
        return ('', 204)
    return ('', 204)


@users_bp.route('/api/user/privileges', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_user_privileges():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    try:
        user_info = get_user_info(user_id=current_user.id)
    except BaseException as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status('User not found', 404)
    return jsonify(user_info['privileges'])


@users_bp.route('/api/user/new', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_create_user():
    if not api_verify(roles=['admin'], permissions=['create_user']):
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    if 'email' in post_data and 'username' not in post_data:  # temporary
        post_data['username'] = post_data['email'].strip()
        del post_data['email']
    if 'username' not in post_data:
        return jsonify_with_status("An e-mail address must be supplied.", 400)
    info = {}
    for key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
        if key in post_data:
            info[key] = post_data[key].strip()
    if 'privileges' in post_data and isinstance(post_data['privileges'], list):
        role_list = post_data['privileges']
    else:
        try:
            role_list = json.loads(post_data.get('privileges', '[]'))
        except:
            role_list = [post_data['privileges']]
    if not isinstance(role_list, list):
        if not isinstance(role_list, str):
            return jsonify_with_status("List of privileges must be a string or a list.", 400)
        role_list = [role_list]
    valid_role_names = set()
    for rol in db.session.execute(select(Role).where(Role.name != 'cron').order_by(Role.id)).scalars():
        valid_role_names.add(rol.name)
    for role_name in role_list:
        if role_name not in valid_role_names:
            return jsonify_with_status("Invalid privilege name.  " + str(role_name) + " is not an existing privilege.", 400)
    password = post_data.get('password', random_alphanumeric(10)).strip()
    if len(password) < 4 or len(password) > 254:
        return jsonify_with_status("Password too short or too long", 400)
    try:
        password = str(password)
        user_id = create_user(post_data['username'], password, role_list, info)
    except BaseException as err:
        return jsonify_with_status(str(err), 400)
    return jsonify_with_status({'user_id': user_id, 'password': password}, 200)


@users_bp.route('/api/user_invite', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_invite_user():
    if not api_verify(roles=['admin'], permissions=['create_user']):
        return jsonify_with_status("Access denied.", 403)
    is_admin = current_user.has_role('admin')
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    send_emails = true_or_false(post_data.get('send_emails', True))
    role_name = str(post_data.get('privilege', 'user')).strip() or 'user'
    valid_role_names = set()
    for rol in db.session.execute(select(Role).where(Role.name != 'cron').order_by(Role.id)).scalars():
        if not is_admin and rol.name in ('admin', 'developer', 'advocate'):
            continue
        valid_role_names.add(rol.name)
    if role_name not in valid_role_names:
        return jsonify_with_status("Invalid privilege name.", 400)
    raw_email_addresses = post_data.get('email_addresses', post_data.get('email_address', []))
    if isinstance(raw_email_addresses, str):
        if raw_email_addresses.startswith('[') or raw_email_addresses.startswith('"'):
            try:
                raw_email_addresses = json.loads(raw_email_addresses)
            except:
                return jsonify_with_status("The email_addresses field did not contain valid JSON.", 400)
    if not isinstance(raw_email_addresses, list):
        raw_email_addresses = [str(raw_email_addresses)]
    email_addresses = []
    for email_address in raw_email_addresses:
        (part_one, part_two) = emailpackage.utils.parseaddr(str(email_address))  # pylint: disable=unused-variable
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', part_two):
            return jsonify_with_status("Invalid e-mail address.", 400)
        email_addresses.append(part_two)
    if len(email_addresses) == 0:
        return jsonify_with_status("One or more 'email_addresses' must be supplied.", 400)
    the_role_id = None
    for role in db.session.execute(select(Role).order_by('id')).scalars():
        if role.name == role_name:
            the_role_id = role.id
            break
    if the_role_id is None:
        return jsonify_with_status("Invalid privilege name.", 400)
    for email_address in email_addresses:
        user, user_email = current_app.user_manager.find_user_by_email(email_address)  # pylint: disable=unused-variable
        if user:
            return jsonify_with_status("That e-mail address is already being used.", 400)
    invite_info = []
    for email_address in email_addresses:
        user_invite = MyUserInvitation(email=email_address, role_id=the_role_id, invited_by_user_id=current_user.id)
        db.session.add(user_invite)
        db.session.commit()
        token = current_app.user_manager.generate_token(user_invite.id)
        accept_invite_link = url_for('user.register',
                                     token=token,
                                     _external=True)
        user_invite.token = token
        db.session.commit()
        info = {'email': email_address}
        if send_emails:
            try:
                logmessage("Trying to send invite e-mail to " + str(user_invite.email))
                docassemble_flask_user.emails.send_invite_email(user_invite, accept_invite_link)
                logmessage("Sent e-mail invite to " + str(user_invite.email))
                info['invitation_sent'] = True
                info['url'] = accept_invite_link
            except BaseException as e:
                try:
                    logmessage("Failed to send invite e-mail: " + e.__class__.__name__ + ': ' + str(e))
                except:
                    logmessage("Failed to send invite e-mail")
                db.session.delete(user_invite)
                db.session.commit()
                info['invitation_sent'] = False
        else:
            info['url'] = accept_invite_link
        invite_info.append(info)
    return jsonify(invite_info)


@users_bp.route('/api/user_info', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_user_info():
    if not api_verify(roles=['admin', 'advocate'], permissions=['access_user_info']):
        return jsonify_with_status("Access denied.", 403)
    if 'username' not in request.args:
        return jsonify_with_status("An e-mail address must be supplied.", 400)
    case_sensitive = true_or_false(request.args.get('case_sensitive', False))
    try:
        user_info = get_user_info(email=request.args['username'], case_sensitive=case_sensitive)
    except BaseException as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status("User not found.", 404)
    return jsonify(user_info)


@users_bp.route('/api/user/<int:user_id>', methods=['GET', 'DELETE', 'POST', 'PATCH'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'DELETE', 'POST', 'PATCH', 'HEAD'], automatic_options=True)
def api_user_by_id(user_id):
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    try:
        user_id = int(user_id)
    except:
        return jsonify_with_status("User ID must be an integer.", 400)
    if not (current_user.same_as(user_id) or current_user.has_role_or_permission('admin', 'advocate', permissions=['access_user_info'])):
        return jsonify_with_status("You do not have sufficient privileges to access user information", 403)
    try:
        user_info = get_user_info(user_id=user_id)
    except BaseException as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status("User not found.", 404)
    if request.method == 'GET':
        return jsonify(user_info)
    if request.method == 'DELETE':
        if user_id in (1, current_user.id):
            return jsonify_with_status("This user account cannot be deleted or deactivated.", 403)
        if request.args.get('remove', None) == 'account':
            if not (current_user.id == user_id or current_user.has_role_or_permission('admin', permissions=['delete_user'])):
                return jsonify_with_status("You do not have sufficient privileges to delete user accounts.", 403)
            user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=False)
            delete_user_data(user_id, r, r_user)
        elif request.args.get('remove', None) == 'account_and_shared':
            if not current_user.has_role_or_permission('admin', permissions=['delete_user']):
                return jsonify_with_status("You do not have sufficient privileges to delete user accounts.", 403)
            user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=True)
            delete_user_data(user_id, r, r_user)
        else:
            if not current_user.has_role_or_permission('admin', permissions=['edit_user_active_status']):
                return jsonify_with_status("You do not have sufficient privileges to inactivate user accounts.", 403)
            make_user_inactive(user_id=user_id, email=None)
        return ('', 204)
    if request.method in ('POST', 'PATCH'):
        if not (current_user.has_role_or_permission('admin', permissions=['edit_user_info']) or current_user.same_as(user_id)):
            return jsonify_with_status("You do not have sufficient privileges to edit user information.", 403)
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        info = {}
        for key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language', 'password', 'old_password'):
            if key in post_data:
                info[key] = post_data[key]
        if 'active' in post_data:
            if user_id in (1, current_user.id):
                return jsonify_with_status("The active status of this user account cannot be changed.", 403)
            if not current_user.has_role_or_permission('admin', permissions=['edit_user_active_status']):
                return jsonify_with_status("You do not have sufficient privileges to change the active status of user accounts.", 403)
            active_status = true_or_false(post_data['active'])
            if user_info['active'] and not active_status:
                info['active'] = False
            elif not user_info['active'] and active_status:
                info['active'] = True
        if 'password' in info and not current_user.has_role_or_permission('admin', permissions=['edit_user_password']):
            return jsonify_with_status("You must have admin privileges to change a password.", 403)
        try:
            set_user_info({"user_id": user_id, **info})
        except BaseException as err:
            return jsonify_with_status(str(err), 400)
        return ('', 204)
    return ('', 204)


@users_bp.route('/api/privileges', methods=['GET', 'DELETE', 'POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'DELETE', 'POST', 'HEAD'], automatic_options=True)
def api_privileges():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    if request.method == 'GET':
        try:
            return jsonify(get_privileges_list(admin=False))
        except BaseException as err:
            return jsonify_with_status(str(err), 400)
    if request.method == 'DELETE':
        if not current_user.has_role_or_permission('admin', permissions=['edit_privileges']):
            return jsonify_with_status("Access denied.", 403)
        if 'privilege' not in request.args:
            return jsonify_with_status("A privilege name must be provided.", 400)
        try:
            remove_privilege(request.args['privilege'])
        except BaseException as err:
            return jsonify_with_status(str(err), 400)
        return ('', 204)
    if request.method == 'POST':
        if not current_user.has_role_or_permission('admin', permissions=['edit_privileges']):
            return jsonify_with_status("Access denied.", 403)
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        if 'privilege' not in post_data:
            return jsonify_with_status("A privilege name must be provided.", 400)
        try:
            add_privilege(post_data['privilege'])
        except BaseException as err:
            return jsonify_with_status(str(err), 400)
        return ('', 204)
    return ('', 204)


@users_bp.route('/api/user/<int:user_id>/privileges', methods=['GET', 'DELETE', 'POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'DELETE', 'POST', 'HEAD'], automatic_options=True)
def api_user_by_id_privileges(user_id):
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    try:
        user_info = get_user_info(user_id=user_id)
    except BaseException as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status('User not found', 404)
    if request.method == 'GET':
        return jsonify(user_info['privileges'])
    if request.method in ('DELETE', 'POST'):
        if not current_user.has_role_or_permission('admin', permissions=['edit_user_privileges']):
            return jsonify_with_status("Access denied.", 403)
        if request.method == 'DELETE':
            role_name = request.args.get('privilege', None)
            if role_name is None:
                return jsonify_with_status("A privilege name must be provided", 400)
            try:
                remove_user_privilege(user_id, role_name)
            except BaseException as err:
                return jsonify_with_status(str(err), 400)
        elif request.method == 'POST':
            post_data = request.get_json(silent=True)
            if post_data is None:
                post_data = request.form.copy()
            role_name = post_data.get('privilege', None)
            if role_name is None:
                return jsonify_with_status("A privilege name must be provided", 400)
            try:
                add_user_privilege(user_id, role_name)
            except BaseException as err:
                return jsonify_with_status(str(err), 400)
        db.session.commit()
        return ('', 204)
    return ('', 204)


@users_bp.route('/api/secret', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_get_secret():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    username = request.args.get('username', None)
    password = request.args.get('password', None)
    if username is None or password is None:
        return jsonify_with_status("A username and password must be supplied", 400)
    try:
        secret = get_secret(str(username), str(password), False)
    except BaseException as err:
        return jsonify_with_status(str(err), 403)
    return jsonify(secret)


@users_bp.route('/api/login_url', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def api_login_url():
    if not api_verify(roles=['admin'], permissions=['log_user_in']):
        return jsonify_with_status("Access denied.", 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    result = get_login_url(post_data)
    if result['status'] == 'error':
        return jsonify_with_status(result['message'], 400)
    if result['status'] == 'auth_error':
        return jsonify_with_status(result['message'], 403)
    if result['status'] == 'success':
        return jsonify(result['url'])
    return jsonify_with_status("Error", 400)


@users_bp.route('/api/user_list', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def api_user_list():
    if not api_verify(roles=['admin', 'advocate'], permissions=['access_user_info']):
        return jsonify_with_status("Access denied.", 403)
    include_inactive = true_or_false(request.args.get('include_inactive', False))
    next_id_code = request.args.get('next_id', None)
    if next_id_code:
        try:
            start_id = int(from_safeid(next_id_code))
            assert start_id >= 0
        except:
            start_id = None
    else:
        start_id = None
    try:
        (user_list, start_id) = get_user_list(include_inactive=include_inactive, start_id=start_id)
    except BaseException as err:
        return jsonify_with_status(str(err), 400)
    if start_id is None:
        next_id = None
    else:
        next_id = safeid(str(start_id))
    return jsonify({'next_id': next_id, 'items': user_list})
