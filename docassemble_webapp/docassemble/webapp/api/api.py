import json
from flask import jsonify, request
from flask_cors import cross_origin
from flask_login import current_user
from sqlalchemy import select
from docassemble.webapp.config import PERMISSIONS_LIST
from docassemble.webapp.extensions import csrf
from docassemble.webapp.extensions import db
from docassemble.webapp.users.helpers import get_user_info
from docassemble.webapp.users.models import UserModel
from docassemble.webapp.utils.helpers import jsonify_with_status
from .blueprint import api_bp
from .helpers import (
    existing_api_names,
    get_api_key,
    update_api_key,
    api_verify,
    api_key_exists,
    get_api_info,
    add_api_key,
    delete_api_key,
)

def do_api_user_api(user_id):
    if request.method == 'GET':
        name = request.args.get('name', None)
        api_key = request.args.get('api_key', None)
        try:
            result = get_api_info(user_id, name=name, api_key=api_key)
        except:
            return jsonify_with_status("Error accessing API information", 400)
        if (name is not None or api_key is not None) and result is None:
            return jsonify_with_status("No such API key could be found.", 404)
        return jsonify(result)
    if request.method == 'DELETE':
        api_key = request.args.get('api_key', None)
        if api_key is None:
            return jsonify_with_status("An API key must supplied", 400)
        try:
            delete_api_key(user_id, api_key)
        except:
            return jsonify_with_status("Error deleting API key", 400)
        return ('', 204)
    if request.method == 'POST':
        post_data = request.get_json(silent=True)
        if post_data is None:
            post_data = request.form.copy()
        name = post_data.get('name', None)
        method = post_data.get('method', 'none')
        if method not in ('ip', 'referer', 'none'):
            return jsonify_with_status("Invalid security method", 400)
        allowed = post_data.get('allowed', [])
        if isinstance(allowed, str):
            try:
                allowed = json.loads(allowed)
            except:
                return jsonify_with_status("Allowed sites list not a valid list", 400)
        if not isinstance(allowed, list):
            return jsonify_with_status("Allowed sites list not a valid list", 400)
        try:
            for item in allowed:
                assert isinstance(item, str)
        except:
            return jsonify_with_status("Allowed sites list not a valid list", 400)
        if name is None:
            return jsonify_with_status("A name must be supplied", 400)
        if name in existing_api_names(user_id):
            return jsonify_with_status("The given name already exists", 400)
        if len(name) > 255:
            return jsonify_with_status("The name is invalid", 400)
        new_api_key = add_api_key(user_id, name, method, allowed)
        if new_api_key is None:
            return jsonify_with_status("Error creating API key", 400)
        return jsonify(new_api_key)
    if request.method == 'PATCH':
        user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=user_id)).scalar()
        patch_data = request.get_json(silent=True)
        if patch_data is None:
            patch_data = request.form.copy()
        if current_user.id == user_id:
            api_key = patch_data.get('api_key', get_api_key())
        else:
            api_key = patch_data.get('api_key', None)
            if api_key is None:
                return jsonify_with_status("No API key given", 400)
        if not api_key_exists(user_id, api_key):
            return jsonify_with_status("The given API key cannot be modified", 400)
        name = patch_data.get('name', None)
        if name is not None:
            if name in existing_api_names(user_id, except_for=api_key):
                return jsonify_with_status("The given name already exists", 400)
            if len(name) > 255:
                return jsonify_with_status("The name is invalid", 400)
        method = patch_data.get('method', None)
        if method is not None:
            if method not in ('ip', 'referer', 'none'):
                return jsonify_with_status("Invalid security method", 400)
        allowed = patch_data.get('allowed', None)
        add_to_allowed = patch_data.get('add_to_allowed', None)
        if add_to_allowed is not None:
            if add_to_allowed.startswith('['):
                try:
                    add_to_allowed = json.loads(add_to_allowed)
                    for item in add_to_allowed:
                        assert isinstance(item, str)
                except:
                    return jsonify_with_status("add_to_allowed is not a valid list", 400)
        remove_from_allowed = patch_data.get('remove_from_allowed', None)
        if remove_from_allowed is not None:
            if remove_from_allowed.startswith('['):
                try:
                    remove_from_allowed = json.loads(remove_from_allowed)
                    for item in remove_from_allowed:
                        assert isinstance(item, str)
                except:
                    return jsonify_with_status("remove_from_allowed is not a valid list", 400)
        if allowed is not None:
            if isinstance(allowed, str):
                try:
                    allowed = json.loads(allowed)
                except:
                    return jsonify_with_status("Allowed sites list not a valid list", 400)
            if not isinstance(allowed, list):
                return jsonify_with_status("Allowed sites list not a valid list", 400)
            try:
                for item in allowed:
                    assert isinstance(item, str)
            except:
                return jsonify_with_status("Allowed sites list not a valid list", 400)
        if not (user.has_role('admin') and current_user.has_role_or_permission('admin')):
            permissions = None
            add_to_permissions = None
            remove_from_permissions = None
        else:
            permissions = patch_data.get('permissions', None)
            add_to_permissions = patch_data.get('add_to_permissions', None)
            if add_to_permissions is not None:
                if add_to_permissions.startswith('['):
                    try:
                        add_to_permissions = json.loads(add_to_permissions)
                        for item in add_to_permissions:
                            assert isinstance(item, str)
                    except:
                        return jsonify_with_status("add_to_permissions is not a valid list", 400)
                    try:
                        for item in add_to_permissions:
                            assert item in PERMISSIONS_LIST
                    except:
                        return jsonify_with_status("add_to_permissions contained a permission that was not recognized", 400)
                elif add_to_permissions not in PERMISSIONS_LIST:
                    return jsonify_with_status("add_to_permissions contained a permission that was not recognized", 400)
            remove_from_permissions = patch_data.get('remove_from_permissions', None)
            if remove_from_permissions is not None:
                if remove_from_permissions.startswith('['):
                    try:
                        remove_from_permissions = json.loads(remove_from_permissions)
                        for item in remove_from_permissions:
                            assert isinstance(item, str)
                    except:
                        return jsonify_with_status("remove_from_permissions is not a valid list", 400)
                    try:
                        for item in remove_from_permissions:
                            assert item in PERMISSIONS_LIST
                    except:
                        return jsonify_with_status("remove_from_permissions contained a permission that was not recognized", 400)
                elif remove_from_permissions not in PERMISSIONS_LIST:
                    return jsonify_with_status("remove_from_permissions contained a permission that was not recognized", 400)
            if permissions is not None:
                if isinstance(permissions, str):
                    try:
                        permissions = json.loads(permissions)
                    except:
                        return jsonify_with_status("Permissions list not a valid list", 400)
                if not isinstance(permissions, list):
                    return jsonify_with_status("Permissions list not a valid list", 400)
                try:
                    for item in permissions:
                        assert isinstance(item, str)
                except:
                    return jsonify_with_status("Permissions list not a valid list", 400)
                try:
                    for item in permissions:
                        assert item in PERMISSIONS_LIST
                except:
                    return jsonify_with_status("Permissions list contained a permission that was not recognized", 400)
        result = update_api_key(user_id, api_key, name, method, allowed, add_to_allowed, remove_from_allowed, permissions, add_to_permissions, remove_from_permissions)
        if not result:
            return jsonify_with_status("Error updating API key", 400)
        return ('', 204)
    return ('', 204)


@api_bp.route('/api/user/api', methods=['GET', 'POST', 'DELETE', 'PATCH'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'DELETE', 'PATCH', 'HEAD'], automatic_options=True)
def api_user_api():
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    if current_user.limited_api:
        if request.method == 'GET' and not current_user.can_do('access_user_api_info'):
            return jsonify_with_status("You do not have sufficient privileges to access user API information", 403)
        if request.method in ('PATCH', 'POST', 'DELETE') and not current_user.can_do('edit_user_api_info'):
            return jsonify_with_status("You do not have sufficient privileges to edit user API information", 403)
    return do_api_user_api(current_user.id)


@api_bp.route('/api/user/<int:user_id>/api', methods=['GET', 'POST', 'DELETE', 'PATCH'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'POST', 'DELETE', 'PATCH', 'HEAD'], automatic_options=True)
def api_user_userid_api(user_id):
    if not api_verify():
        return jsonify_with_status("Access denied.", 403)
    try:
        user_id = int(user_id)
    except:
        return jsonify_with_status("User ID must be an integer.", 400)
    if not current_user.same_as(user_id):
        if request.method == 'GET' and not current_user.has_role_or_permission('admin', permissions=['access_user_api_info']):
            return jsonify_with_status("You do not have sufficient privileges to access user API information", 403)
        if request.method in ('POST', 'DELETE', 'PATCH') and not current_user.has_role_or_permission('admin', permissions=['edit_user_api_info']):
            return jsonify_with_status("You do not have sufficient privileges to edit user API information", 403)
    try:
        user_info = get_user_info(user_id=user_id, admin=True)
    except BaseException as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status("User not found.", 404)
    return do_api_user_api(user_id)
