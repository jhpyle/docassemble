import datetime
import copy
import re
from flask import flash, current_app, session
from flask_login import current_user
from sqlalchemy import select
import docassemble_flask_user
from docassemble.base.error import DAError, DAException
from docassemble.base.generate_key import random_alphanumeric
from docassemble.base.language.control import set_language
from docassemble.base.language.words import word
from docassemble.base.thread_context import this_thread
from docassemble.base.util import DAList, DADict
from docassemble.webapp.config import (
    PAGINATION_LIMIT_PLUS_ONE,
    final_default_yaml_filename,
    PERMISSIONS_LIST,
    PAGINATION_LIMIT,
    daconfig,
    allowed,
)
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.interview.helpers import (
    sub_temp_user_dict_key,
    substitute_secret,
    sub_temp_other,
    fix_secret,
    save_user_dict_key,
)
from docassemble.webapp.sessions import update_session, get_session
from docassemble.webapp.users.models import UserModel
from docassemble.webapp.utils.helpers import url_for, MD5Hash, pad_to_16
from docassemble.webapp.utils.logger import logmessage
from .models import UserAuthModel, MyUserInvitation, Role

@hookimpl(specname="server_get_user_info")
def get_user_info_adapter(user_id, email, case_sensitive, admin):
    return get_user_info(user_id=user_id, email=email, case_sensitive=case_sensitive, admin=admin)

def get_user_info(user_id=None, email=None, case_sensitive=False, admin=False):
    if user_id is not None:
        assert isinstance(user_id, int)
    if user_id is None and email is None:
        user_id = current_user.id
    if email is not None:
        assert isinstance(email, str)
        email = email.strip()
    user_info = {'privileges': []}
    if user_id is not None:
        user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.id == user_id)).scalar()
    else:
        if case_sensitive:
            user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(email=email)).scalar()
        else:
            email = re.sub(r'\%', '', email)
            user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.email.ilike(email))).scalar()
    if not (admin or current_user.has_role_or_permission('admin', 'advocate', permissions=['access_user_info']) or (user is not None and current_user.same_as(user_id))):
        raise DAException("You do not have sufficient privileges to access information about other users")
    if user is None or user.social_id.startswith('disabled$'):
        return None
    for role in user.roles:
        user_info['privileges'].append(role.name)
    for attrib in ('id', 'email', 'first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language', 'active'):
        user_info[attrib] = getattr(user, attrib)
    user_info['account_type'] = re.sub(r'\$.*', '', user.social_id)
    return user_info


@hookimpl
def make_user_inactive(user_id, email):
    if not current_user.has_role_or_permission('admin', permissions=['edit_user_active_status']):
        raise DAException("You do not have sufficient privileges to make a user inactive")
    if user_id is None and email is None:
        raise DAException("You must supply a user ID or an e-mail address to make a user inactive")
    if user_id is not None:
        user = db.session.execute(select(UserModel).filter_by(id=user_id)).scalar()
    else:
        assert isinstance(email, str)
        email = email.strip()
        user = db.session.execute(select(UserModel).filter_by(email=email)).scalar()
    if user is None:
        raise DAException("User not found")
    user.active = False
    db.session.commit()


@hookimpl(specname="server_invite_user")
def invite_user(email_address, privilege, send):
    if not (current_user.is_authenticated and current_user.has_role_or_permission('admin', permissions=['create_user'])):
        raise DAError("You do not have sufficient privileges to create a new user")
    role_name = privilege or 'user'
    the_role_id = None
    for role in db.session.execute(select(Role).order_by('id')).scalars():
        if role.name == role_name:
            the_role_id = role.id
            break
    if the_role_id is None:
        raise DAError("Invalid privilege name " + repr(privilege))
    user, user_email = current_app.user_manager.find_user_by_email(email_address)  # pylint: disable=unused-variable
    if user:
        return DAError("A user with that email address already exists")
    user_invite = MyUserInvitation(email=email_address, role_id=the_role_id, invited_by_user_id=current_user.id)
    db.session.add(user_invite)
    db.session.commit()
    token = current_app.user_manager.generate_token(user_invite.id)
    accept_invite_link = url_for('user.register',
                                 token=token,
                                 _external=True)
    user_invite.token = token
    db.session.commit()
    if send:
        try:
            logmessage("Trying to send invite e-mail to " + str(user_invite.email))
            docassemble_flask_user.emails.send_invite_email(user_invite, accept_invite_link)
            logmessage("Sent e-mail invite to " + str(user_invite.email))
        except BaseException as e:
            try:
                logmessage("Failed to send invite e-mail: " + e.__class__.__name__ + ': ' + str(e))
            except:
                logmessage("Failed to send invite e-mail")
            db.session.delete(user_invite)
            db.session.commit()
            raise DAError("Invitation email failed to send") from e
        return None
    return accept_invite_link


@hookimpl
def get_privileges_list(admin):
    if admin is False and not current_user.has_role_or_permission('admin', 'developer', permissions=['access_privileges']):
        raise DAException('You do not have sufficient privileges to see the list of privileges.')
    role_names = []
    for role in db.session.execute(select(Role.name).order_by(Role.name)):
        role_names.append(role.name)
    return role_names


@hookimpl
def get_permissions_of_privilege(privilege, privileged):
    if not privileged and not current_user.has_role_or_permission('admin', 'developer', permissions=['access_privileges']):
        raise DAException('You do not have sufficient privileges to inspect privileges.')
    if privilege == 'admin':
        return copy.copy(PERMISSIONS_LIST)
    if privilege == 'developer':
        return ['demo_interviews', 'template_parse', 'interview_data']
    if privilege == 'advocate':
        return ['access_user_info', 'access_sessions', 'edit_sessions']
    if privilege == 'cron':
        return []
    if privilege in allowed:
        return list(allowed[privilege])
    return []


@hookimpl
def add_privilege(privilege):
    if not current_user.has_role_or_permission('admin', permissions=['edit_privileges']):
        raise DAException('You do not have sufficient privileges to add a privilege.')
    role_names = get_privileges_list(admin=False)
    if privilege in role_names:
        raise DAException("The given privilege already exists.")
    db.session.add(Role(name=privilege))
    db.session.commit()


@hookimpl
def remove_privilege(privilege):
    if not current_user.has_role_or_permission('admin', permissions=['edit_privileges']):
        raise DAException('You do not have sufficient privileges to delete a privilege.')
    if privilege in ['user', 'admin', 'developer', 'advocate', 'cron']:
        raise DAException('The specified privilege is built-in and cannot be deleted.')
    role = db.session.execute(select(Role).filter_by(name=privilege)).scalar()
    if role is None:
        raise DAException('The privilege ' + str(privilege) + ' did not exist.')
    db.session.delete(role)
    db.session.commit()


@hookimpl
def add_user_privilege(user_id, privilege):
    if not current_user.has_role_or_permission('admin', permissions=['edit_user_privileges']):
        raise DAException('You do not have sufficient privileges to give another user a privilege.')
    if privilege in ('admin', 'developer', 'advocate', 'cron') and not current_user.has_role_or_permission('admin'):
        raise DAException('You do not have sufficient privileges to give the user this privilege.')
    if privilege not in get_privileges_list(admin=True):
        raise DAException('The specified privilege does not exist.')
    if privilege == 'cron':
        raise DAException('You cannot give a user the cron privilege.')
    user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.id == user_id)).scalar()
    if user is None or user.social_id.startswith('disabled$'):
        raise DAException("The specified user did not exist")
    for role in user.roles:
        if role.name == privilege:
            raise DAException("The user already had that privilege.")
    role_to_add = None
    for role in db.session.execute(select(Role).order_by(Role.id)).scalars():
        if role.name == privilege:
            role_to_add = role
    if role_to_add is None:
        raise DAException("The specified privilege did not exist.")
    user.roles.append(role_to_add)
    db.session.commit()


@hookimpl
def remove_user_privilege(user_id, privilege):
    if not current_user.has_role_or_permission('admin', permissions=['edit_user_privileges']):
        raise DAException('You do not have sufficient privileges to take a privilege away from a user.')
    if current_user.id == user_id and privilege == 'admin':
        raise DAException('You cannot take away the admin privilege from the current user.')
    if privilege in ('admin', 'developer', 'advocate', 'cron') and not current_user.has_role('admin'):
        raise DAException('You do not have sufficient privileges to take away this privilege.')
    if privilege not in get_privileges_list(admin=True):
        raise DAException('The specified privilege does not exist.')
    user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.id == user_id)).scalar()
    if user is None or user.social_id.startswith('disabled$'):
        raise DAException("The specified user did not exist")
    role_to_remove = None
    for role in user.roles:
        if role.name == privilege:
            role_to_remove = role
    if role_to_remove is None:
        raise DAException("The user did not already have that privilege.")
    user.roles.remove(role_to_remove)
    db.session.commit()


@hookimpl(specname="server_create_user")
def create_user(email, password, privileges, info):
    if not current_user.has_role_or_permission('admin', permissions=['create_user']):
        raise DAException("You do not have sufficient privileges to create a user")
    email = email.strip()
    password = str(password).strip()
    if len(password) < 4 or len(password) > 254:
        raise DAException("Password too short or too long")
    if privileges is None:
        privileges = []
    if isinstance(privileges, DAList):
        info = info.elements
    if not isinstance(privileges, list):
        if not isinstance(privileges, str):
            raise DAException("The privileges parameter to create_user() must be a list or a string.")
        privileges = [privileges]
    if info is None:
        info = {}
    if isinstance(info, DADict):
        info = info.elements
    if not isinstance(info, dict):
        raise DAException("The info parameter to create_user() must be a dictionary.")
    user, user_email = current_app.user_manager.find_user_by_email(email)  # pylint: disable=unused-variable
    if user:
        raise DAException("That e-mail address is already being used.")
    user_auth = UserAuthModel(password=current_app.user_manager.hash_password(password))
    while True:
        new_social = 'local$' + random_alphanumeric(32)
        existing_user = db.session.execute(select(UserModel).filter_by(social_id=new_social)).first()
        if existing_user:
            continue
        break
    the_user = UserModel(
        active=True,
        nickname=re.sub(r'@.*', '', email),
        social_id=new_social,
        email=email,
        user_auth=user_auth,
        first_name=info.get('first_name', ''),
        last_name=info.get('last_name', ''),
        country=info.get('country', ''),
        subdivisionfirst=info.get('subdivisionfirst', ''),
        subdivisionsecond=info.get('subdivisionsecond', ''),
        subdivisionthird=info.get('subdivisionthird', ''),
        organization=info.get('organization', ''),
        timezone=info.get('timezone', ''),
        language=info.get('language', ''),
        confirmed_at=datetime.datetime.now()
    )
    num_roles = 0
    is_admin = current_user.has_role('admin')
    for role in db.session.execute(select(Role).where(Role.name != 'cron').order_by(Role.id)).scalars():
        if role.name in privileges and (is_admin or role.name not in ('admin', 'developer', 'advocate')):
            the_user.roles.append(role)
        num_roles += 1
    if num_roles == 0:
        user_role = db.session.execute(select(Role).filter_by(name='user')).scalar_one()
        the_user.roles.append(user_role)
    db.session.add(user_auth)
    db.session.add(the_user)
    db.session.commit()
    return the_user.id


@hookimpl(specname="server_set_user_info")
def set_user_info(kwargs):
    user_id = kwargs.get('user_id', None)
    email = kwargs.get('email', None)
    if user_id is None and email is None:
        user_id = int(current_user.id)
    if not current_user.has_role_or_permission('admin', permissions=['edit_user_info']):
        if (user_id is not None and current_user.id != user_id) or (email is not None and current_user.email != email):
            raise DAException("You do not have sufficient privileges to edit user information")
    if user_id is not None:
        user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=user_id)).scalar()
    else:
        user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(email=email)).scalar()
    if user is None or user.social_id.startswith('disabled$'):
        raise DAException("User not found")
    editing_self = current_user.same_as(user.id)
    if not current_user.has_role_or_permission('admin'):
        if not editing_self:
            if user.has_role('admin', 'developer', 'advocate', 'cron'):
                raise DAException("You do not have sufficient privileges to edit this user's information.")
            if 'password' in kwargs and not current_user.can_do('edit_user_password'):
                raise DAException("You do not have sufficient privileges to change this user's password.")
        if 'privileges' in kwargs:
            if user.has_role('admin', 'developer', 'advocate', 'cron') or not current_user.can_do('edit_user_privileges'):
                raise DAException("You do not have sufficient privileges to edit this user's privileges.")
    if 'active' in kwargs:
        if not isinstance(kwargs['active'], bool):
            raise DAException("The active parameter must be True or False")
        if editing_self:
            raise DAException("Cannot change active status of the current user.")
        if not current_user.has_role_or_permission('admin', permissions=['edit_user_active_status']):
            raise DAException("You do not have sufficient privileges to edit this user's active status.")
    for key, val in kwargs.items():
        if key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
            setattr(user, key, val)
    if 'password' in kwargs:
        if not editing_self and not current_user.has_role_or_permission('admin', permissions=['edit_user_password']):
            raise DAException("You do not have sufficient privileges to change a user's password.")
        if 'old_password' in kwargs and kwargs['password'] != kwargs['old_password']:
            user_manager = current_app.user_manager
            if (not user_manager.get_password(user)) or (not user_manager.verify_password(kwargs['old_password'], user)):
                raise DAException("The old_password is incorrect")
            substitute_secret(pad_to_16(MD5Hash(data=kwargs['old_password']).hexdigest()), pad_to_16(MD5Hash(data=kwargs['password']).hexdigest()), user=user)
        user.user_auth.password = current_app.user_manager.hash_password(kwargs['password'])
    if 'active' in kwargs:
        user.active = kwargs['active']
    db.session.commit()
    if 'privileges' in kwargs and isinstance(kwargs['privileges'], (list, tuple, set)):
        if len(kwargs['privileges']) == 0:
            raise DAException("Cannot remove all of a user's privileges.")
        roles_to_add = []
        roles_to_delete = []
        role_names = [role.name for role in user.roles]
        for role in role_names:
            if role not in kwargs['privileges']:
                roles_to_delete.append(role)
        for role in kwargs['privileges']:
            if role not in role_names:
                roles_to_add.append(role)
        for role in roles_to_delete:
            remove_user_privilege(user.id, role)
        for role in roles_to_add:
            add_user_privilege(user.id, role)


@hookimpl(specname="server_get_secret")
def get_secret(username, password, case_sensitive):
    if case_sensitive:
        user = db.session.execute(select(UserModel).filter_by(email=username)).scalar()
    else:
        username = re.sub(r'\%', '', username)
        user = db.session.execute(select(UserModel).where(UserModel.email.ilike(username))).scalar()
    if user is None:
        raise DAException("Username not known")
    if current_app.config['USE_MFA'] and user.otp_secret is not None:
        raise DAException("Secret will not be supplied because two factor authentication is enabled")
    user_manager = current_app.user_manager
    if not user_manager.get_password(user):
        raise DAException("Password not set")
    if not user_manager.verify_password(password, user):
        raise DAException("Incorrect password")
    return pad_to_16(MD5Hash(data=password).hexdigest())


@hookimpl(specname="server_get_user_list")
def get_user_list(include_inactive, start_id):
    if not (current_user.is_authenticated and current_user.has_role_or_permission('admin', 'advocate', permissions=['access_user_info', 'create_user'])):
        raise DAException("You do not have sufficient privileges to access information about other users")
    user_length = 0
    user_list = []
    while True:
        there_are_more = False
        filter_list = []
        if start_id is not None:
            filter_list.append(UserModel.id > start_id)
        if not include_inactive:
            filter_list.append(UserModel.active == True)  # noqa: E712 # pylint: disable=singleton-comparison
        the_users = select(UserModel).options(db.joinedload(UserModel.roles))
        if len(filter_list) > 0:
            the_users = the_users.where(*filter_list)
        the_users = the_users.order_by(UserModel.id).limit(PAGINATION_LIMIT_PLUS_ONE)
        results_in_query = 0
        for user in db.session.execute(the_users).unique().scalars():
            results_in_query += 1
            if results_in_query == PAGINATION_LIMIT_PLUS_ONE:
                there_are_more = True
                break
            start_id = user.id
            if user.social_id.startswith('disabled$'):
                continue
            if user_length == PAGINATION_LIMIT:
                there_are_more = True
                break
            user_info = {}
            user_info['privileges'] = []
            for role in user.roles:
                user_info['privileges'].append(role.name)
            for attrib in ('id', 'email', 'first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
                user_info[attrib] = getattr(user, attrib)
            if include_inactive:
                user_info['active'] = getattr(user, 'active')
            user_list.append(user_info)
            user_length += 1
        if user_length == PAGINATION_LIMIT or results_in_query < PAGINATION_LIMIT_PLUS_ONE:
            break
    if not there_are_more:
        start_id = None
    return (user_list, start_id)


def login_as_admin(url, url_root):
    found = False
    for admin_user in db.session.execute(select(UserModel).filter_by(nickname='admin').order_by(UserModel.id)).scalars():
        if not found:
            found = True
            current_app.login_manager._update_request_context_with_user(admin_user)
            this_thread.current_info = {'user': {'is_anonymous': False, 'is_authenticated': True, 'email': admin_user.email, 'theid': admin_user.id, 'the_user_id': admin_user.id, 'roles': ['admin'], 'firstname': admin_user.first_name, 'lastname': admin_user.last_name, 'nickname': admin_user.nickname, 'country': admin_user.country, 'subdivisionfirst': admin_user.subdivisionfirst, 'subdivisionsecond': admin_user.subdivisionsecond, 'subdivisionthird': admin_user.subdivisionthird, 'organization': admin_user.organization, 'location': None, 'session_uid': 'admin', 'device_id': 'admin'}, 'session': None, 'secret': None, 'yaml_filename': final_default_yaml_filename, 'url': url, 'url_root': url_root, 'encrypted': False, 'action': None, 'interface': 'initialization', 'arguments': {}}


@hookimpl
def get_user_object(user_id):
    the_user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.id == user_id)).scalar()
    return the_user


def needs_to_change_password():
    if not current_user.has_role('admin'):
        return False
    if not (current_user.social_id and current_user.social_id.startswith('local')):
        return False
    if r.get('da:insecure_password_present') is not None:
        r.delete('da:insecure_password_present')
        session.pop('_flashes', None)
        flash(word("Your password is insecure and needs to be changed"), "warning")
        return True
    return False


def login_or_register(sender, user, source, **extra):  # pylint: disable=unused-argument
    # logmessage("login or register!")
    if 'i' in session:  # TEMPORARY
        get_session(session['i'])
    to_convert = []
    if 'tempuser' in session:
        to_convert.extend(sub_temp_user_dict_key(session['tempuser'], user.id))
    if 'sessions' in session:
        for filename, info in session['sessions'].items():
            if (filename, info['uid']) not in to_convert:
                to_convert.append((filename, info['uid']))
                save_user_dict_key(info['uid'], filename, priors=True, user=user)
                update_session(filename, key_logged=True)
    fix_secret(user=user, to_convert=to_convert)
    sub_temp_other(user)
    if not (source == 'register' and daconfig.get('confirm registration', False)):
        session['user_id'] = user.id
    if user.language:
        session['language'] = user.language
        set_language(user.language)


def update_last_login(user):
    user.last_login = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db.session.commit()
