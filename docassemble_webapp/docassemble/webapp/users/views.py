import datetime
import json
import re
from io import BytesIO
import email.utils
from urllib.parse import (
    parse_qsl,
    quote as urllibquote,
    urlencode,
    urlparse,
    urlunparse,
)
import zoneinfo
import pyotp
import qrcode
import wtforms
from user_agents import parse as ua_parse
from flask import (
    abort,
    current_app,
    flash,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_wtf.csrf import generate_csrf
from flask_login import logout_user, login_user
from sqlalchemy import and_, not_, select
from sqlalchemy.orm import joinedload
from markupsafe import Markup
from docassemble_flask_user import current_user, login_required, roles_required, emails
import docassemble_flask_user
from docassemble.base.functions import (
    debug_status,
    phone_number_in_e164,
    phone_number_is_valid,
)
from docassemble.base.generate_key import random_alphanumeric, random_digits
from docassemble.base.language.language import quantity_noun
from docassemble.base.language.language_en import comma_and_list_en
from docassemble.base.language.words import word
from docassemble.base.logger import logmessage
from docassemble.base.util import send_sms
from docassemble.webapp.config import (
    BAN_IP_ADDRESSES,
    DEFAULT_LANGUAGE,
    PAGINATION_LIMIT,
    PAGINATION_LIMIT_PLUS_ONE,
    daconfig,
    exit_page,
)
from docassemble.webapp.daredis import r_user, r
from docassemble.webapp.extensions import csrf, lm, db
from docassemble.webapp.interview.helpers import (
    delete_temp_user_data,
    delete_user_data,
    reset_user_dict,
    user_interviews,
)
from docassemble.webapp.interview.models import UserDictKeys
from docassemble.webapp.main.hooks import (
    get_default_timezone,
    get_server_redis,
    get_server_redis_user,
)
from docassemble.webapp.sessions import update_session
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.twilio.helpers import twilio_config
from docassemble.webapp.users.models import (
    MyUserInvitation,
    Role,
    UserAuthModel,
    UserModel,
)
from docassemble.webapp.utils.encryption import decrypt_phrase, decrypt_dictionary
from docassemble.webapp.utils.helpers import (
    _call_or_get,
    _endpoint_url,
    _get_safe_next_param,
    add_secret_to,
    as_int,
    delete_session_info,
    fix_http,
    get_base_url,
    get_requester_ip,
    get_url_from_file_reference,
    manual_checkout,
    repad,
)
from .helpers import update_last_login
from .forms import (
    EditUserProfileForm,
    MFAChooseForm,
    MFALoginForm,
    MFAReconfigureForm,
    MFASMSSetupForm,
    MFASetupForm,
    MFAVerifySMSSetupForm,
    ManageAccountForm,
    MyInviteForm,
    NewPrivilegeForm,
    PhoneUserProfileForm,
    UserAddForm,
    UserProfileForm,
)
from .blueprint import users_bp

@lm.user_loader
def load_user(the_id):
    return db.session.execute(
        select(UserModel)
        .options(joinedload(UserModel.roles))
        .where(UserModel.id == int(the_id))
    ).unique().scalar_one_or_none()


@users_bp.route('/privilegelist', methods=['GET', 'POST'])
@login_required
@roles_required('admin', permission='access_privileges')
def privilege_list():
    setup_translation()
    can_edit = bool(current_user.has_roles('admin') or current_user.can_do('edit_privileges'))
    output = """\
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">""" + word("Privilege") + """</th>
          <th scope="col" class="text-end">""" + word("Action") + """</th>
        </tr>
      </thead>
      <tbody>
"""
    for role in db.session.execute(select(Role).order_by(Role.name)).scalars():
        if can_edit and role.name not in ['user', 'admin', 'developer', 'advocate', 'cron', 'trainer']:
            output += '        <tr><td>' + str(role.name) + '</td><td class="text-end"><a class="btn ' + current_app.config['BUTTON_CLASS'] + ' btn-danger btn-sm" href="' + url_for('users.delete_privilege', privilege_id=role.id) + '">Delete</a></td></tr>\n'
        else:
            output += '        <tr><td>' + str(role.name) + '</td><td>&nbsp;</td></tr>\n'

    output += """\
      </tbody>
    </table>
"""
    response = make_response(render_template('users/rolelist.html', version_warning=None, bodyclass='daadminbody', page_title=word('Privileges'), tab_title=word('Privileges'), privilegelist=output, can_edit=can_edit), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@users_bp.route('/userlist', methods=['GET'])
@login_required
@roles_required(['admin', 'advocate'], permission='access_user_info')
def user_list():
    setup_translation()
    page = request.args.get('page', None)
    if page:
        try:
            page = int(page) - 1
            assert page >= 0
        except:
            page = 0
    else:
        page = 0
    users = []
    user_query = select(UserModel).options(db.joinedload(UserModel.roles)).where(and_(UserModel.nickname != 'cron', not_(UserModel.social_id.like('disabled$%')))).order_by(UserModel.id)
    if page > 0:
        user_query = user_query.offset(PAGINATION_LIMIT*page)
    user_query = user_query.limit(PAGINATION_LIMIT_PLUS_ONE)
    results_in_query = 0
    there_are_more = False
    for user in db.session.execute(user_query).unique().scalars():
        results_in_query += 1
        if results_in_query == PAGINATION_LIMIT_PLUS_ONE:
            there_are_more = True
            break
        role_names = [y.name for y in user.roles]
        if 'admin' in role_names:
            high_priv = 'admin'
        elif 'developer' in role_names:
            high_priv = 'developer'
        elif 'advocate' in role_names:
            high_priv = 'advocate'
        elif 'trainer' in role_names:
            high_priv = 'trainer'
        else:
            high_priv = 'user'
        name_string = ''
        if user.first_name:
            name_string += str(user.first_name) + " "
        if user.last_name:
            name_string += str(user.last_name)
        if name_string:
            name_string = str(name_string)
        if user.email is None:
            user_indicator = user.nickname
        else:
            user_indicator = user.email
        is_active = bool(user.active)
        users.append({'name': name_string, 'email': user_indicator, 'active': is_active, 'id': user.id, 'high_priv': high_priv})
    if there_are_more:
        next_page = page + 2
    else:
        next_page = None
    prev_page = page
    response = make_response(render_template('users/userlist.html', version_warning=None, bodyclass='daadminbody', page_title=word('User List'), tab_title=word('User List'), users=users, prev_page=prev_page, next_page=next_page), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@users_bp.route('/privilege/<int:privilege_id>/delete', methods=['GET'])
@login_required
@roles_required('admin', permission='edit_privileges')
def delete_privilege(privilege_id):
    setup_translation()
    if not privilege_id:
        flash(word('The role could not be deleted.'), 'error')
        return redirect(url_for('users.privilege_list'))
    role = db.session.execute(select(Role).filter_by(id=privilege_id)).scalar_one()
    user_role = db.session.execute(select(Role).filter_by(name='user')).scalar_one()
    if user_role is None or role is None or role.name in ['user', 'admin', 'developer', 'advocate', 'cron', 'trainer']:
        flash(word('The role could not be deleted.'), 'error')
    else:
        for user in db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles))).unique().scalars():
            roles_to_remove = []
            for the_role in user.roles:
                if the_role.name == role.name:
                    roles_to_remove.append(the_role)
            if len(roles_to_remove) > 0:
                for the_role in roles_to_remove:
                    user.roles.remove(the_role)
                if len(user.roles) == 0:
                    user.roles.append(user_role)
        db.session.commit()
        db.session.delete(role)
        db.session.commit()
        flash(word('The role ' + role.name + ' was deleted.'), 'success')
        # docassemble.webapp.daredis.clear_user_cache()
    return redirect(url_for('users.privilege_list'))


@users_bp.route('/user/<int:user_id>/editprofile', methods=['GET', 'POST'])
@login_required
@roles_required('admin', permission='edit_user_info')
def edit_user_profile_page(user_id):
    setup_translation()
    is_admin = bool(current_user.has_roles('admin'))
    if is_admin:
        can_edit_privileges = True
        can_delete = True
        can_edit_user_active_status = True
    else:
        can_edit_privileges = current_user.can_do('edit_user_privileges')
        can_delete = current_user.can_do('delete_user') and current_user.can_do('access_sessions') and current_user.can_do('edit_sessions')
        can_edit_user_active_status = current_user.can_do('edit_user_active_status')
    if not user_id:
        flash(word('The user account did not exit.'), 'danger')
        return redirect(url_for('users.user_list'))
    user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=user_id)).unique().scalar_one()
    if not user:
        flash(word('The user account did not exit.'), 'danger')
        return redirect(url_for('users.user_list'))
    if not is_admin:
        protected_user = False
        for role in user.roles:
            if role.name in ('admin', 'developer', 'advocate'):
                protected_user = True
                break
        if protected_user:
            flash(word('You do not have sufficient privileges to edit this user.'), 'danger')
            return redirect(url_for('users.user_list'))
    the_tz = user.timezone if user.timezone else get_default_timezone()
    if user is None or user.social_id.startswith('disabled$'):
        return redirect(url_for('users.user_list'))
    if 'disable_mfa' in request.args and int(request.args['disable_mfa']) == 1:
        user.otp_secret = None
        db.session.commit()
        # docassemble.webapp.daredis.clear_user_cache()
        return redirect(url_for('users.edit_user_profile_page', user_id=user_id))
    if 'reset_email_confirmation' in request.args and int(request.args['reset_email_confirmation']) == 1:
        user.confirmed_at = None
        db.session.commit()
        # docassemble.webapp.daredis.clear_user_cache()
        return redirect(url_for('users.edit_user_profile_page', user_id=user_id))
    if can_delete and daconfig.get('admin can delete account', True) and user.id != current_user.id:
        if 'delete_account' in request.args and int(request.args['delete_account']) == 1:
            user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=False)
            delete_user_data(user_id, get_server_redis(), get_server_redis_user())
            db.session.commit()
            flash(word('The user account was deleted.'), 'success')
            return redirect(url_for('users.user_list'))
        if 'delete_account_complete' in request.args and int(request.args['delete_account_complete']) == 1:
            user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=True)
            delete_user_data(user_id, get_server_redis(), get_server_redis_user())
            db.session.commit()
            flash(word('The user account was deleted.'), 'success')
            return redirect(url_for('users.user_list'))
    the_role_id = []
    for role in user.roles:
        the_role_id.append(role.id)
    if len(the_role_id) == 0:
        the_role_id = [db.session.execute(select(Role.id).filter_by(name='user')).scalar_one()]
    form = EditUserProfileForm(request.form, obj=user, role_id=the_role_id)
    if request.method == 'POST' and form.cancel.data:
        flash(word('The user profile was not changed.'), 'success')
        return redirect(url_for('users.user_list'))
    if user.social_id.startswith('local$') or daconfig.get('allow external auth with admin accounts', False):
        form.role_id.choices = [(r.id, r.name) for r in db.session.execute(select(Role.id, Role.name).where(Role.name != 'cron').order_by('name'))]
        privileges_note = None
    else:
        form.role_id.choices = [(r.id, r.name) for r in db.session.execute(select(Role.id, Role.name).where(and_(Role.name != 'cron', Role.name != 'admin')).order_by('name'))]
        privileges_note = word("Note: only users with e-mail/password accounts can be given admin privileges.")
    form.timezone.choices = [(x, x) for x in sorted(list(zoneinfo.available_timezones()))]
    form.timezone.default = the_tz
    if str(form.timezone.data) == 'None' or str(form.timezone.data) == '':
        form.timezone.data = the_tz
    form.uses_mfa.data = bool(user.otp_secret is not None)
    admin_id = db.session.execute(select(Role.id).filter_by(name='admin')).scalar_one()
    if request.method == 'POST' and form.validate(user.id, admin_id):
        if not can_edit_user_active_status:
            form.active.data = user.active
        form.populate_obj(user)
        if can_edit_privileges:
            roles_to_remove = []
            the_role_id = []
            for role in user.roles:
                if not is_admin and role.name in ('admin', 'developer', 'advocate'):
                    continue
                roles_to_remove.append(role)
            for role in roles_to_remove:
                user.roles.remove(role)
            for role in db.session.execute(select(Role).order_by('id')).scalars():
                if not is_admin and role.name in ('admin', 'developer', 'advocate'):
                    continue
                if role.id in form.role_id.data:
                    user.roles.append(role)
                    the_role_id.append(role.id)
        db.session.commit()
        flash(word('The information was saved.'), 'success')
        return redirect(url_for('users.user_list'))
    confirmation_feature = bool(user.id > 2)
    script = """
    <script>
      document.addEventListener("DOMContentLoaded", function () {
        $( document ).ready(function() {
          $(".dadeleteaccount").click(function(event){
            if (!confirm(""" + json.dumps(word("Are you sure you want to permanently delete this user's account?")) + """)){
              event.preventDefault();
              return false;
            }
          });
        });
      });
    </script>"""
    form.role_id.process_data(the_role_id)
    if user.active:
        form.active.default = 'checked'
    response = make_response(render_template('users/edit_user_profile_page.html', version_warning=None, page_title=word('Edit User Profile'), tab_title=word('Edit User Profile'), form=form, confirmation_feature=confirmation_feature, privileges_note=privileges_note, is_self=(user.id == current_user.id), extra_js=Markup(script), is_admin=is_admin, can_edit_privileges=can_edit_privileges, can_delete=can_delete, can_edit_user_active_status=can_edit_user_active_status), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@users_bp.route('/privilege/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin', permission='edit_privileges')
def add_privilege():
    setup_translation()
    form = NewPrivilegeForm(request.form, obj=current_user)

    if request.method == 'POST' and form.validate():
        for role in db.session.execute(select(Role).order_by(Role.name)).scalars():
            if role.name == form.name.data:
                flash(word('The privilege could not be added because it already exists.'), 'error')
                return redirect(url_for('users.privilege_list'))

        db.session.add(Role(name=form.name.data))
        db.session.commit()
        flash(word('The privilege was added.'), 'success')
        return redirect(url_for('users.privilege_list'))

    response = make_response(render_template('users/new_role_page.html', version_warning=None, bodyclass='daadminbody', page_title=word('Add Privilege'), tab_title=word('Add Privilege'), form=form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@users_bp.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    setup_translation()
    if not (current_app.config['SHOW_PROFILE'] or current_user.has_roles(['admin'])):
        return ('File not found', 404)
    the_tz = current_user.timezone if current_user.timezone else get_default_timezone()
    if current_user.social_id and current_user.social_id.startswith('phone$'):
        form = PhoneUserProfileForm(request.form, obj=current_user)
    else:
        form = UserProfileForm(request.form, obj=current_user)
    form.timezone.choices = [(x, x) for x in sorted(list(zoneinfo.available_timezones()))]
    form.timezone.default = the_tz
    if str(form.timezone.data) == 'None' or str(form.timezone.data) == '':
        form.timezone.data = the_tz
    if request.method == 'POST' and form.validate():
        if current_user.has_roles(['admin', 'developer']):
            form.populate_obj(current_user)
        else:
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            if current_user.social_id and current_user.social_id.startswith('phone$'):
                current_user.email = form.email.data
            for reg_field in ('country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'language', 'timezone'):
                if reg_field in current_app.config['USER_PROFILE_FIELDS']:
                    setattr(current_user, reg_field, getattr(form, reg_field).data)
        db.session.commit()
        # docassemble.webapp.daredis.clear_user_cache()
        flash(word('Your information was saved.'), 'success')
        return redirect(url_for('users.interview_list'))
    response = make_response(render_template('users/user_profile_page.html', version_warning=None, page_title=word('User Profile'), tab_title=word('User Profile'), form=form, debug=debug_status()), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@users_bp.route('/user/invite', methods=['GET', 'POST'])
@login_required
@roles_required('admin', permission='create_user')
def invite():
    """ Allows users to send invitations to register an account """
    setup_translation()
    is_admin = bool(current_user.has_roles('admin'))
    user_manager = current_app.user_manager

    the_next = request.args.get('next',
                                _endpoint_url(user_manager.after_invite_endpoint))

    user_role = db.session.execute(select(Role).filter_by(name='user')).scalar_one()
    invite_form = MyInviteForm(request.form)
    if is_admin:
        invite_form.role_id.choices = [(str(r.id), str(r.name)) for r in db.session.execute(select(Role.id, Role.name).where(and_(Role.name != 'cron', Role.name != 'admin')).order_by('name'))]
    else:
        invite_form.role_id.choices = [(str(r.id), str(r.name)) for r in db.session.execute(select(Role.id, Role.name).where(and_(Role.name != 'cron', Role.name != 'admin', Role.name != 'developer', Role.name != 'advocate')).order_by('name'))]
    if request.method == 'POST' and invite_form.validate():
        email_addresses = []
        for email_address in re.split(r'[\n\r]+', invite_form.email.data.strip()):
            (part_one, part_two) = email.utils.parseaddr(email_address)  # pylint: disable=unused-variable
            email_addresses.append(part_two)

        the_role_id = None

        for role in db.session.execute(select(Role).order_by('id')).scalars():
            if not is_admin and role.name in ('admin', 'developer', 'advocate'):
                continue
            if role.id == int(invite_form.role_id.data) and role.name != 'admin' and role.name != 'cron':
                the_role_id = role.id

        if the_role_id is None:
            the_role_id = user_role.id

        has_error = False
        for email_address in email_addresses:
            user, user_email = user_manager.find_user_by_email(email_address)  # pylint: disable=unused-variable
            if user:
                flash(word("A user with that e-mail has already registered") + " (" + email_address + ")", "error")
                has_error = True
                continue
            user_invite = MyUserInvitation(email=email_address, role_id=the_role_id, invited_by_user_id=current_user.id)
            db.session.add(user_invite)
            db.session.commit()
            token = user_manager.generate_token(user_invite.id)
            accept_invite_link = url_for('user.register',
                                         token=token,
                                         _external=True)

            user_invite.token = token
            db.session.commit()
            # docassemble.webapp.daredis.clear_user_cache()
            try:
                logmessage("Trying to send invite e-mail to " + str(user_invite.email))
                emails.send_invite_email(user_invite, accept_invite_link)
                logmessage("Sent e-mail invite to " + str(user_invite.email))
            except BaseException as e:
                try:
                    logmessage("Failed to send invite e-mail: " + e.__class__.__name__ + ': ' + str(e))
                except:
                    logmessage("Failed to send invite e-mail")
                db.session.delete(user_invite)
                db.session.commit()
                # docassemble.webapp.daredis.clear_user_cache()
                flash(word('Unable to send e-mail.  Error was: ') + str(e), 'error')
                has_error = True
        if has_error:
            return redirect(url_for('users.invite'))
        if len(email_addresses) > 1:
            flash(word('Invitations have been sent.'), 'success')
        else:
            flash(word('Invitation has been sent.'), 'success')
        return redirect(the_next)
    if invite_form.role_id.data is None:
        invite_form.role_id.process_data(str(user_role.id))
    response = make_response(render_template('flask_user/invite.html', version_warning=None, bodyclass='daadminbody', page_title=word('Invite User'), tab_title=word('Invite User'), form=invite_form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@users_bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin', permission='create_user')
def user_add():
    setup_translation()
    is_admin = bool(current_user.has_roles('admin'))
    user_role = db.session.execute(select(Role).filter_by(name='user')).scalar_one()
    add_form = UserAddForm(request.form, role_id=[str(user_role.id)])
    if is_admin:
        add_form.role_id.choices = [(r.id, r.name) for r in db.session.execute(select(Role.id, Role.name).where(Role.name != 'cron').order_by('name'))]
    else:
        add_form.role_id.choices = [(r.id, r.name) for r in db.session.execute(select(Role.id, Role.name).where(and_(Role.name != 'cron', Role.name != 'admin', Role.name != 'developer', Role.name != 'advocate')).order_by('name'))]
    add_form.role_id.default = user_role.id
    if str(add_form.role_id.data) == 'None':
        add_form.role_id.data = user_role.id
    if request.method == 'POST' and add_form.validate():
        user, user_email = current_app.user_manager.find_user_by_email(add_form.email.data)  # pylint: disable=unused-variable
        if user:
            flash(word("A user with that e-mail has already registered"), "error")
            return redirect(url_for('users.user_add'))
        user_auth = UserAuthModel(password=current_app.user_manager.hash_password(add_form.password.data))
        while True:
            new_social = 'local$' + random_alphanumeric(32)
            existing_user = db.session.execute(select(UserModel).filter_by(social_id=new_social)).scalar()
            if existing_user:
                continue
            break
        the_user = UserModel(
            active=True,
            nickname=re.sub(r'@.*', '', add_form.email.data),
            social_id=new_social,
            email=add_form.email.data,
            user_auth=user_auth,
            first_name=add_form.first_name.data,
            last_name=add_form.last_name.data,
            confirmed_at=datetime.datetime.now()
        )
        num_roles = 0
        for role in db.session.execute(select(Role).order_by('id')).scalars():
            if not is_admin and role.name in ('admin', 'developer', 'advocate'):
                continue
            if role.id in add_form.role_id.data:
                if role.name != 'cron':
                    the_user.roles.append(role)
                    num_roles += 1
        if num_roles == 0:
            the_user.roles.append(user_role)
        db.session.add(user_auth)
        db.session.add(the_user)
        db.session.commit()
        # docassemble.webapp.daredis.clear_user_cache()
        flash(word("The new user has been created"), "success")
        return redirect(url_for('users.user_list'))
    response = make_response(render_template('users/add_user_page.html', version_warning=None, bodyclass='daadminbody', page_title=word('Add User'), tab_title=word('Add User'), form=add_form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def custom_register():
    """Display registration form and create new User."""
    is_json = bool(('json' in request.form and as_int(request.form['json'])) or ('json' in request.args and as_int(request.args['json'])))

    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter

    safe_next = _get_safe_next_param('next', user_manager.after_login_endpoint)
    safe_reg_next = _get_safe_next_param('reg_next', user_manager.after_register_endpoint)
    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        if safe_next == url_for(user_manager.after_login_endpoint):
            url_parts = list(urlparse(safe_next))
            query = dict(parse_qsl(url_parts[4]))
            query.update({'from_login': 1})
            url_parts[4] = urlencode(query)
            safe_next = urlunparse(url_parts)
        return add_secret_to(redirect(safe_next))

    setup_translation()

    # Initialize form
    login_form = user_manager.login_form()                      # for login_or_register.html
    register_form = user_manager.register_form(request.form)    # for register.html

    # invite token used to determine validity of registeree
    invite_token = request.values.get("token")

    the_tz = get_default_timezone()

    # require invite without a token should disallow the user from registering
    if user_manager.require_invitation and not invite_token:
        flash(word("Registration is invite only"), "error")
        return redirect(url_for('user.login'))

    user_invite = None
    if invite_token and db_adapter.UserInvitationClass:
        user_invite = db_adapter.find_first_object(db_adapter.UserInvitationClass, token=invite_token)
        if user_invite:
            register_form.invite_token.data = invite_token
        else:
            flash(word("Invalid invitation token"), "error")
            return redirect(url_for('user.login'))

    if request.method != 'POST':
        login_form.next.data = register_form.next.data = safe_next
        login_form.reg_next.data = register_form.reg_next.data = safe_reg_next
        if user_invite:
            register_form.email.data = user_invite.email

    register_form.timezone.choices = [(x, x) for x in sorted(list(zoneinfo.available_timezones()))]
    register_form.timezone.default = the_tz
    if str(register_form.timezone.data) == 'None' or str(register_form.timezone.data) == '':
        register_form.timezone.data = the_tz
    if request.method == 'POST':
        if 'timezone' not in current_app.config['USER_PROFILE_FIELDS']:
            register_form.timezone.data = the_tz
        for reg_field in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'language'):
            if reg_field not in current_app.config['USER_PROFILE_FIELDS']:
                getattr(register_form, reg_field).data = ""

    # Process valid POST
    if request.method == 'POST' and register_form.validate():
        email_taken = False
        if daconfig.get('confirm registration', False):
            try:
                docassemble_flask_user.forms.unique_email_validator(register_form, register_form.email)
            except wtforms.ValidationError:
                email_taken = True
        if email_taken:
            flash(word('A confirmation email has been sent to %(email)s with instructions to complete your registration.' % {'email': register_form.email.data}), 'success')
            subject, html_message, text_message = docassemble_flask_user.emails._render_email(
                'flask_user/emails/reregistered',
                app_name=current_app.config['APP_NAME'],
                sign_in_link=url_for('user.login', _external=True))

            # Send email message using Flask-Mail
            user_manager.send_email_function(register_form.email.data, subject, html_message, text_message)
            return redirect(url_for('user.login'))

        # Create a User object using Form fields that have a corresponding User field
        User = db_adapter.UserClass  # pylint: disable=invalid-name
        user_class_fields = User.__dict__
        user_fields = {}
        user_auth_fields = {}
        user_email_fields = {}

        # Create a UserEmail object using Form fields that have a corresponding UserEmail field
        if db_adapter.UserEmailClass:
            UserEmail = db_adapter.UserEmailClass  # pylint: disable=invalid-name
            user_email_class_fields = UserEmail.__dict__
            user_email_fields = {}

        # Create a UserAuth object using Form fields that have a corresponding UserAuth field
        if db_adapter.UserAuthClass:
            UserAuth = db_adapter.UserAuthClass  # pylint: disable=invalid-name
            user_auth_class_fields = UserAuth.__dict__
            user_auth_fields = {}

        # Enable user account
        if db_adapter.UserProfileClass:
            if hasattr(db_adapter.UserProfileClass, 'active'):
                user_auth_fields['active'] = True
            elif hasattr(db_adapter.UserProfileClass, 'is_enabled'):
                user_auth_fields['is_enabled'] = True
            else:
                user_auth_fields['is_active'] = True
        else:
            if hasattr(db_adapter.UserClass, 'active'):
                user_fields['active'] = True
            elif hasattr(db_adapter.UserClass, 'is_enabled'):
                user_fields['is_enabled'] = True
            else:
                user_fields['is_active'] = True

        # For all form fields
        for field_name, field_value in register_form.data.items():
            # Hash password field
            if field_name == 'password':
                hashed_password = user_manager.hash_password(field_value)
                if db_adapter.UserAuthClass:
                    user_auth_fields['password'] = hashed_password
                else:
                    user_fields['password'] = hashed_password
            # Store corresponding Form fields into the User object and/or UserProfile object
            else:
                if field_name in user_class_fields:
                    user_fields[field_name] = field_value
                if db_adapter.UserEmailClass:
                    if field_name in user_email_class_fields:
                        user_email_fields[field_name] = field_value
                if db_adapter.UserAuthClass:
                    if field_name in user_auth_class_fields:
                        user_auth_fields[field_name] = field_value
        while True:
            new_social = 'local$' + random_alphanumeric(32)
            existing_user = db.session.execute(select(UserModel).filter_by(social_id=new_social)).first()
            if existing_user:
                continue
            break
        user_fields['social_id'] = new_social
        # Add User record using named arguments 'user_fields'
        user = db_adapter.add_object(User, **user_fields)

        # Add UserEmail record using named arguments 'user_email_fields'
        if db_adapter.UserEmailClass:
            user_email = db_adapter.add_object(UserEmail,
                                               user=user,
                                               is_primary=True,
                                               **user_email_fields)
        else:
            user_email = None

        # Add UserAuth record using named arguments 'user_auth_fields'
        if db_adapter.UserAuthClass:
            user_auth = db_adapter.add_object(UserAuth, **user_auth_fields)
            if db_adapter.UserProfileClass:
                user = user_auth
            else:
                user.user_auth = user_auth

        require_email_confirmation = True
        if user_invite:
            if user_invite.email == register_form.email.data:
                require_email_confirmation = False
                db_adapter.update_object(user, confirmed_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))

        db_adapter.commit()

        # Send 'registered' email and delete new User object if send fails
        if user_manager.send_registered_email:
            try:
                # Send 'registered' email
                docassemble_flask_user.views._send_registered_email(user, user_email, require_email_confirmation)
            except:
                # delete new User object if send fails
                db_adapter.delete_object(user)
                db_adapter.commit()
                raise

        # Send user_registered signal
        docassemble_flask_user.signals.user_registered.send(current_app._get_current_object(),
                                                            user=user,
                                                            user_invite=user_invite)

        # Redirect if USER_ENABLE_CONFIRM_EMAIL is set
        if user_manager.enable_confirm_email and require_email_confirmation:
            safe_reg_next = user_manager.make_safe_url_function(register_form.reg_next.data)
            return redirect(safe_reg_next)

        # Auto-login after register or redirect to login page
        if register_form.next.data:
            safe_reg_next = user_manager.make_safe_url_function(register_form.next.data)
        elif register_form.reg_next.data:
            safe_reg_next = user_manager.make_safe_url_function(register_form.reg_next.data)
        else:
            safe_reg_next = _endpoint_url(user_manager.after_confirm_endpoint)

        if user_manager.auto_login_after_register:
            if current_app.config['USE_MFA']:
                if user.otp_secret is None and len(current_app.config['MFA_REQUIRED_FOR_ROLE']) and user.has_role(*current_app.config['MFA_REQUIRED_FOR_ROLE']):
                    session['validated_user'] = user.id
                    session['next'] = safe_reg_next
                    if current_app.config['MFA_ALLOW_APP'] and (twilio_config is None or not current_app.config['MFA_ALLOW_SMS']):
                        return redirect(url_for('users.mfa_setup'))
                    if not current_app.config['MFA_ALLOW_APP']:
                        return redirect(url_for('users.mfa_sms_setup'))
                    return redirect(url_for('users.mfa_choose'))
            return docassemble_flask_user.views._do_login_user(user, safe_reg_next)
        return redirect(url_for('user.login') + '?next=' + urllibquote(safe_reg_next))

    # Process GET or invalid POST
    if is_json:
        return jsonify(action='register', csrf_token=generate_csrf())
    response = make_response(user_manager.render_function(user_manager.register_template,
                                                          form=register_form,
                                                          login_form=login_form,
                                                          register_form=register_form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def custom_login():
    """ Prompt for username/email and password and sign the user in."""
    # logmessage("In custom_login\n")

    is_json = bool(('json' in request.form and as_int(request.form['json'])) or ('json' in request.args and as_int(request.args['json'])))
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter

    safe_next = _get_safe_next_param('next', user_manager.after_login_endpoint)
    safe_reg_next = _get_safe_next_param('reg_next', user_manager.after_register_endpoint)
    if safe_next and '/officeaddin' in safe_next:
        g.embed = True

    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        if safe_next == url_for(user_manager.after_login_endpoint):
            url_parts = list(urlparse(safe_next))
            query = dict(parse_qsl(url_parts[4]))
            query.update({'from_login': 1})
            url_parts[4] = urlencode(query)
            safe_next = urlunparse(url_parts)
        return add_secret_to(redirect(safe_next))

    setup_translation()

    login_form = user_manager.login_form(request.form)
    register_form = user_manager.register_form()
    if request.method != 'POST':
        login_form.next.data = register_form.next.data = safe_next
        login_form.reg_next.data = register_form.reg_next.data = safe_reg_next
    if request.method == 'GET' and 'validated_user' in session:
        del session['validated_user']
    if request.method == 'POST' and login_form.validate():
        user = None
        if user_manager.enable_username:
            user = user_manager.find_user_by_username(login_form.username.data)
            user_email = None  # pylint: disable=unused-variable
            if user and db_adapter.UserEmailClass:
                user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
                                                          user_id=int(user.get_id()),
                                                          is_primary=True,
                                                          )
            if not user and user_manager.enable_email:
                user, user_email = user_manager.find_user_by_email(login_form.username.data)
        else:
            user, user_email = user_manager.find_user_by_email(login_form.email.data)
        # if not user and daconfig['ldap login'].get('enabled', False):
        if user:
            safe_next = user_manager.make_safe_url_function(login_form.next.data)
            # safe_next = login_form.next.data
            # safe_next = url_for('post_login', next=login_form.next.data)
            if current_app.config['USE_MFA']:
                if user.otp_secret is None and len(current_app.config['MFA_REQUIRED_FOR_ROLE']) and user.has_role(*current_app.config['MFA_REQUIRED_FOR_ROLE']):
                    session['validated_user'] = user.id
                    session['next'] = safe_next
                    if current_app.config['MFA_ALLOW_APP'] and (twilio_config is None or not current_app.config['MFA_ALLOW_SMS']):
                        return redirect(url_for('users.mfa_setup'))
                    if not current_app.config['MFA_ALLOW_APP']:
                        return redirect(url_for('users.mfa_sms_setup'))
                    return redirect(url_for('users.mfa_choose'))
                if user.otp_secret is not None:
                    session['validated_user'] = user.id
                    session['next'] = safe_next
                    if user.otp_secret.startswith(':phone:'):
                        phone_number = re.sub(r'^:phone:', '', user.otp_secret)
                        verification_code = random_digits(daconfig['verification code digits'])
                        message = word("Your verification code is") + " " + str(verification_code) + "."
                        key = 'da:mfa:phone:' + str(phone_number) + ':code'
                        pipe = r.pipeline()
                        pipe.set(key, verification_code)
                        pipe.expire(key, daconfig['verification code timeout'])
                        pipe.execute()
                        success = send_sms(to=phone_number, body=message)
                        if not success:
                            flash(word("Unable to send verification code."), 'error')
                            return redirect(url_for('user.login'))
                    return add_secret_to(redirect(url_for('users.mfa_login')))
            if user_manager.enable_email and user_manager.enable_confirm_email \
               and len(daconfig['email confirmation privileges']) \
               and user.has_role(*daconfig['email confirmation privileges']) \
               and not user.has_confirmed_email():
                url = url_for('user.resend_confirm_email', email=user.email)
                flash(word('You cannot log in until your e-mail address has been confirmed.') + '<br><a href="' + url + '">' + word('Click here to confirm your e-mail') + '</a>.', 'error')
                return redirect(url_for('user.login'))
            return add_secret_to(docassemble_flask_user.views._do_login_user(user, safe_next, login_form.remember_me.data))
    if is_json:
        return jsonify(action='login', csrf_token=generate_csrf())
    # if 'officeaddin' in safe_next:
    #     extra_css = """
    # <script src="https://appsforoffice.microsoft.com/lib/1.1/hosted/office.debug.js"></script>"""
    #     extra_js = """
    # <script src=""" + '"' + url_for('static', filename='office/fabric.js') + '"' + """></script>
    # <script src=""" + '"' + url_for('static', filename='office/polyfill.js') + '"' + """></script>
    # <script src=""" + '"' + url_for('static', filename='office/app.js') + '"' + """></script>"""
    #     return render_template(user_manager.login_template,
    #                            form=login_form,
    #                            login_form=login_form,
    #                            register_form=register_form,
    #                            extra_css=Markup(extra_css),
    #                            extra_js=Markup(extra_js))
    # else:
    if current_app.config['AUTO_LOGIN'] and not (current_app.config['USE_PASSWORD_LOGIN'] or ('admin' in request.args and request.args['admin'] == '1') or ('from_logout' in request.args and request.args['from_logout'] == '1')):
        if current_app.config['AUTO_LOGIN'] is True:
            number_of_methods = 0
            the_method = None
            for login_method in ('USE_PHONE_LOGIN', 'USE_GOOGLE_LOGIN', 'USE_FACEBOOK_LOGIN', 'USE_ZITADEL_LOGIN', 'USE_AUTH0_LOGIN', 'USE_KEYCLOAK_LOGIN', 'USE_AUTHENTIK_LOGIN', 'USE_AZURE_LOGIN', 'USE_MINIORANGE_LOGIN'):
                if current_app.config[login_method]:
                    number_of_methods += 1
                    the_method = re.sub(r'USE_(.*)_LOGIN', r'\1', login_method).lower()
            if number_of_methods > 1:
                the_method = None
        else:
            the_method = current_app.config['AUTO_LOGIN']
        if the_method == 'phone':
            if not current_app.config['USE_PHONE_LOGIN']:
                abort(404)
            return redirect(url_for('phonelogin.phone_login'))
        if the_method == 'google':
            return redirect(url_for('auth.google_page', next=request.args.get('next', '')))
        if the_method in ('facebook', 'auth0', 'keycloak', 'authentik', 'azure', 'zitadel', 'miniorange'):
            return redirect(url_for('auth.oauth_authorize', provider=the_method, next=request.args.get('next', '')))
    response = make_response(user_manager.render_function(user_manager.login_template,
                                                          form=login_form,
                                                          login_form=login_form,
                                                          register_form=register_form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def logout():
    setup_translation()
    # secret = request.cookies.get('secret', None)
    # if secret is None:
    #     secret = random_string(16)
    #     set_cookie = True
    # else:
    #     secret = str(secret)
    #     set_cookie = False
    user_manager = current_app.user_manager
    next_url = None
    if 'next' in request.args and request.args['next'] != '':
        try:
            next_url = decrypt_phrase(repad(bytearray(request.args['next'], encoding='utf-8')).decode(), current_app.secret_key)
        except:
            pass
    if next_url is None:
        next_url = daconfig.get('logoutpage', None)
    if next_url is None:
        if session.get('language', None) and session['language'] != DEFAULT_LANGUAGE:
            next_url = _endpoint_url(user_manager.after_logout_endpoint, lang=session['language'], from_logout='1')
        else:
            next_url = _endpoint_url(user_manager.after_logout_endpoint, from_logout='1')
    if current_user.is_authenticated:
        if current_user.social_id.startswith('auth0$') and 'oauth' in daconfig and 'auth0' in daconfig['oauth'] and 'domain' in daconfig['oauth']['auth0']:
            if next_url.startswith('/'):
                next_url = get_base_url() + next_url
            next_url = 'https://' + daconfig['oauth']['auth0']['domain'] + '/v2/logout?' + urlencode({'returnTo': next_url, 'client_id': daconfig['oauth']['auth0']['id']})
        if current_user.social_id.startswith('zitadel$') and 'oauth' in daconfig and 'zitadel' in daconfig['oauth'] and 'domain' in daconfig['oauth']['zitadel'] and 'id' in daconfig['oauth']['zitadel']:
            next_url = 'https://' + daconfig['oauth']['zitadel']['domain'] + '/oidc/v1/end_session?' + urlencode({'post_logout_redirect_uri': url_for('user.login', _external=True), 'client_id': daconfig['oauth']['zitadel']['id']})
        if current_user.social_id.startswith('keycloak$') and 'oauth' in daconfig and 'keycloak' in daconfig['oauth'] and 'domain' in daconfig['oauth']['keycloak']:
            if next_url.startswith('/'):
                next_url = get_base_url() + next_url
            protocol = daconfig['oauth']['keycloak'].get('protocol', 'https://')
            if not protocol.endswith('://'):
                protocol = protocol + '://'
            next_url = protocol + daconfig['oauth']['keycloak']['domain'] + '/realms/' + daconfig['oauth']['keycloak']['realm'] + '/protocol/openid-connect/logout?' + urlencode({'post_logout_redirect_uri': next_url, 'client_id': daconfig['oauth']['keycloak']['id']})
        if current_user.social_id.startswith('authentik$') and 'oauth' in daconfig and 'authentik' in daconfig['oauth'] and 'domain' in daconfig['oauth']['authentik'] and daconfig['oauth']['authentik'].get('application slug', None):
            protocol = daconfig['oauth']['authentik'].get('protocol', 'https://')
            if not protocol.endswith('://'):
                protocol = protocol + '://'
            next_url = f'{protocol}{daconfig["oauth"]["authentik"]["domain"]}/application/o/{daconfig["oauth"]["authentik"]["application slug"]}/end-session/'
    docassemble_flask_user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
    logout_user()
    delete_session_info()
    session.clear()
    if next_url.startswith('/') and current_app.config['FLASH_LOGIN_MESSAGES']:
        flash(word('You have signed out successfully.'), 'success')
    response = redirect(next_url)
    response.set_cookie('remember_token', '', expires=0)
    response.set_cookie('visitor_secret', '', expires=0)
    response.set_cookie('secret', '', expires=0)
    response.set_cookie('session', '', expires=0)
    return response

# def custom_login():
#     logmessage("custom_login")
#     user_manager = current_app.user_manager
#     db_adapter = user_manager.db_adapter
#     secret = request.cookies.get('secret', None)
#     if secret is not None:
#         secret = str(secret)
#     next_url = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
#     reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))

#     if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
#         return redirect(next_url)

#     login_form = user_manager.login_form(request.form)
#     register_form = user_manager.register_form()
#     if request.method != 'POST':
#         login_form.next.data     = register_form.next.data = next_url
#         login_form.reg_next.data = register_form.reg_next.data = reg_next

#     if request.method == 'POST':
#         try:
#             login_form.validate()
#         except:
#             logmessage("custom_login: got an error when validating login")
#             pass
#     if request.method == 'POST' and login_form.validate():
#         user = None
#         user_email = None
#         if user_manager.enable_username:
#             user = user_manager.find_user_by_username(login_form.username.data)
#             user_email = None
#             if user and db_adapter.UserEmailClass:
#                 user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
#                         user_id=int(user.get_id()),
#                         is_primary=True,
#                         )
#             if not user and user_manager.enable_email:
#                 user, user_email = user_manager.find_user_by_email(login_form.username.data)
#         else:
#             user, user_email = user_manager.find_user_by_email(login_form.email.data)

#         if user:
#             return _do_login_user(user, login_form.password.data, secret, login_form.next.data, login_form.remember_me.data)

#     return render_template(user_manager.login_template, page_title=word('Sign In'), tab_title=word('Sign In'), form=login_form, login_form=login_form, register_form=register_form)


def unauthenticated():
    if not request.args.get('nm', False):
        flash(word("You need to log in before you can access") + " " + word(request.path), 'error')
    the_url = url_for('user.login', next=fix_http(request.url))
    return redirect(the_url)


def unauthorized():
    flash(word("You are not authorized to access") + " " + word(request.path), 'error')
    return redirect(url_for('admin.interview_list', next=fix_http(request.url)))


def custom_resend_confirm_email():
    user_manager = current_app.user_manager
    form = user_manager.resend_confirm_email_form(request.form)
    if request.method == 'GET' and 'email' in request.args:
        form.email.data = request.args['email']
    if request.method == 'POST' and form.validate():
        the_email = form.email.data
        user, user_email = user_manager.find_user_by_email(the_email)
        if user:
            docassemble_flask_user.views._send_confirm_email(user, user_email)
        return redirect(docassemble_flask_user.views._endpoint_url(user_manager.after_resend_confirm_email_endpoint))
    response = make_response(user_manager.render_function(user_manager.resend_confirm_email_template, form=form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def password_validator(form, field):  # pylint: disable=unused-argument
    password = list(field.data)
    password_length = len(password)

    lowers = uppers = digits = punct = 0
    for ch in password:
        if ch.islower():
            lowers += 1
        if ch.isupper():
            uppers += 1
        if ch.isdigit():
            digits += 1
        if not (ch.islower() or ch.isupper() or ch.isdigit()):
            punct += 1

    rules = daconfig.get('password complexity', {})
    is_valid = password_length >= rules.get('length', 6) and lowers >= rules.get('lowercase', 1) and uppers >= rules.get('uppercase', 1) and digits >= rules.get('digits', 1) and punct >= rules.get('punctuation', 0)
    if not is_valid:
        if 'error message' in rules:
            error_message = str(rules['error message'])
        else:
            # word("Password must be at least six characters long with at least one lowercase letter, at least one uppercase letter, and at least one number.")
            error_message = 'Password must be at least ' + quantity_noun(rules.get('length', 6), 'character', language='en') + ' long'
            standards = []
            if rules.get('lowercase', 1) > 0:
                standards.append('at least ' + quantity_noun(rules.get('lowercase', 1), 'lowercase letter', language='en'))
            if rules.get('uppercase', 1) > 0:
                standards.append('at least ' + quantity_noun(rules.get('uppercase', 1), 'uppercase letter', language='en'))
            if rules.get('digits', 1) > 0:
                standards.append('at least ' + quantity_noun(rules.get('digits', 1), 'number', language='en'))
            if rules.get('punctuation', 0) > 0:
                standards.append('at least ' + quantity_noun(rules.get('punctuation', 1), 'punctuation character', language='en'))
            if len(standards) > 0:
                error_message += ' with ' + comma_and_list_en(standards)
            error_message += '.'
        raise wtforms.ValidationError(word(error_message))

@users_bp.route('/user/autologin', methods=['GET'])
def auto_login():
    ua_string = request.headers.get('User-Agent', None)
    if ua_string is not None:
        response = ua_parse(ua_string)
        if response.device.brand == 'Spider':
            return render_template_string('')
    if 'key' not in request.args or len(request.args['key']) != 40:
        abort(403)
    code = str(request.args['key'][16:40])
    decryption_key = str(request.args['key'][0:16])
    the_key = 'da:auto_login:' + code
    info_text = r.get(the_key)
    if info_text is None:
        abort(403)
    r.delete(the_key)
    info_text = info_text.decode()
    try:
        info = decrypt_dictionary(info_text, decryption_key)
    except:
        abort(403)
    user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.id == info['user_id'])).scalar()
    if (not user) or user.social_id.startswith('disabled$') or not user.active:
        abort(403)
    login_user(user, remember=False)
    update_last_login(user)
    if 'i' in info:
        url_info = {'i': info['i']}
        if 'url_args' in info:
            url_info.update(info['url_args'])
        next_url = url_for('interview.index', **url_info)
        if 'session' in info:
            update_session(info['i'], uid=info['session'], encrypted=info['encrypted'])
    elif 'next' in info:
        url_info = info.get('url_args', {})
        next_url = get_url_from_file_reference(info['next'], url_info)
    else:
        next_url = url_for('admin.interview_list', from_login='1')
    response = redirect(next_url)
    response.set_cookie('secret', info['secret'], httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'])
    return response

@users_bp.route('/headers', methods=['POST', 'GET'])
@csrf.exempt
def show_headers():
    return jsonify(headers=dict(request.headers), ipaddress=request.remote_addr)

@users_bp.route('/mfa_setup', methods=['POST', 'GET'])
def mfa_setup():
    in_login = False
    if current_user.is_authenticated:
        user = current_user
    elif 'validated_user' in session:
        in_login = True
        user = load_user(session['validated_user'])
    else:
        return ('File not found', 404)
    if not current_app.config['USE_MFA'] or not user.has_role(*current_app.config['MFA_ROLES']) or not user.social_id.startswith('local'):
        return ('File not found', 404)
    form = MFASetupForm(request.form)
    if request.method == 'POST' and form.submit.data:
        if 'otp_secret' not in session:
            return ('File not found', 404)
        otp_secret = session['otp_secret']
        del session['otp_secret']
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        totp = pyotp.TOTP(otp_secret)
        if not totp.verify(supplied_verification_code):
            flash(word("Your verification code was invalid."), 'error')
            if in_login:
                del session['validated_user']
                if 'next' in session:
                    del session['next']
                return redirect(url_for('user.login'))
            return redirect(url_for('users.user_profile_page'))
        user = load_user(user.id)
        user.otp_secret = otp_secret
        db.session.commit()
        if in_login:
            if 'next' in session:
                next_url = session['next']
                del session['next']
            else:
                next_url = url_for('admin.interview_list', from_login='1')
            return docassemble_flask_user.views._do_login_user(user, next_url, False)
        flash(word("You are now set up with two factor authentication."), 'success')
        return redirect(url_for('users.user_profile_page'))
    otp_secret = pyotp.random_base32()
    if user.email:
        the_name = user.email
    else:
        the_name = re.sub(r'.*\$', '', user.social_id)
    the_url = pyotp.totp.TOTP(otp_secret).provisioning_uri(the_name, issuer_name=current_app.config['APP_NAME'])
    im = qrcode.make(the_url, image_factory=qrcode.image.svg.SvgPathImage)
    output = BytesIO()
    im.save(output)
    the_qrcode = output.getvalue().decode()
    the_qrcode = re.sub(r"<\?xml version='1.0' encoding='UTF-8'\?>\n", '', the_qrcode)
    the_qrcode = re.sub(r'height="[0-9]+mm" ', '', the_qrcode)
    the_qrcode = re.sub(r'width="[0-9]+mm" ', '', the_qrcode)
    m = re.search(r'(viewBox="[^"]+")', the_qrcode)
    if m:
        viewbox = ' ' + m.group(1)
    else:
        viewbox = ''
    the_qrcode = '<svg class="damfasvg"' + viewbox + '><g transform="scale(1.0)">' + the_qrcode + '</g></svg>'
    session['otp_secret'] = otp_secret
    return render_template('flask_user/mfa_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("Scan the barcode with your phone's authenticator app and enter the verification code."), the_qrcode=Markup(the_qrcode), manual_code=otp_secret)


@login_required
@users_bp.route('/mfa_reconfigure', methods=['POST', 'GET'])
def mfa_reconfigure():
    setup_translation()
    if not current_app.config['USE_MFA'] or not current_user.has_role(*current_app.config['MFA_ROLES']) or not current_user.social_id.startswith('local'):
        return ('File not found', 404)
    user = load_user(current_user.id)
    if user.otp_secret is None:
        if current_app.config['MFA_ALLOW_APP'] and (twilio_config is None or not current_app.config['MFA_ALLOW_SMS']):
            return redirect(url_for('users.mfa_setup'))
        if not current_app.config['MFA_ALLOW_APP']:
            return redirect(url_for('users.mfa_sms_setup'))
        return redirect(url_for('users.mfa_choose'))
    form = MFAReconfigureForm(request.form)
    if request.method == 'POST':
        if form.reconfigure.data:
            if current_app.config['MFA_ALLOW_APP'] and (twilio_config is None or not current_app.config['MFA_ALLOW_SMS']):
                return redirect(url_for('users.mfa_setup'))
            if not current_app.config['MFA_ALLOW_APP']:
                return redirect(url_for('users.mfa_sms_setup'))
            return redirect(url_for('users.mfa_choose'))
        if form.disable.data and not (len(current_app.config['MFA_REQUIRED_FOR_ROLE']) and current_user.has_role(*current_app.config['MFA_REQUIRED_FOR_ROLE'])):
            user.otp_secret = None
            db.session.commit()
            flash(word("Your account no longer uses two-factor authentication."), 'success')
            return redirect(url_for('users.user_profile_page'))
        if form.cancel.data:
            return redirect(url_for('users.user_profile_page'))
    if len(current_app.config['MFA_REQUIRED_FOR_ROLE']) > 0 and current_user.has_role(*current_app.config['MFA_REQUIRED_FOR_ROLE']):
        return render_template('flask_user/mfa_reconfigure.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), allow_disable=False, description=word("Would you like to reconfigure two-factor authentication?"))
    return render_template('flask_user/mfa_reconfigure.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), allow_disable=True, description=word("Your account already has two-factor authentication enabled.  Would you like to reconfigure or disable two-factor authentication?"))


@users_bp.route('/mfa_choose', methods=['POST', 'GET'])
def mfa_choose():
    in_login = False
    if current_user.is_authenticated:
        user = current_user
    elif 'validated_user' in session:
        in_login = True
        user = load_user(session['validated_user'])
    else:
        return ('File not found', 404)
    if not current_app.config['USE_MFA'] or user.is_anonymous or not user.has_role(*current_app.config['MFA_ROLES']) or not user.social_id.startswith('local'):
        return ('File not found', 404)
    if current_app.config['MFA_ALLOW_APP'] and (twilio_config is None or not current_app.config['MFA_ALLOW_SMS']):
        return redirect(url_for('users.mfa_setup'))
    if not current_app.config['MFA_ALLOW_APP']:
        return redirect(url_for('users.mfa_sms_setup'))
    user = load_user(user.id)
    form = MFAChooseForm(request.form)
    if request.method == 'POST':
        if form.sms.data:
            return redirect(url_for('users.mfa_sms_setup'))
        if form.auth.data:
            return redirect(url_for('users.mfa_setup'))
        if in_login:
            del session['validated_user']
            if 'next' in session:
                del session['next']
            return redirect(url_for('user.login'))
        return redirect(url_for('users.user_profile_page'))
    return render_template('flask_user/mfa_choose.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=Markup(word("""Which type of two-factor authentication would you like to use?  The first option is to use an authentication app like <a target="_blank" href="https://en.wikipedia.org/wiki/Google_Authenticator">Google Authenticator</a> or <a target="_blank" href="https://authy.com/">Authy</a>.  The second option is to receive a text (SMS) message containing a verification code.""")))


@users_bp.route('/mfa_sms_setup', methods=['POST', 'GET'])
def mfa_sms_setup():
    in_login = False
    if current_user.is_authenticated:
        user = current_user
    elif 'validated_user' in session:
        in_login = True
        user = load_user(session['validated_user'])
    else:
        return ('File not found', 404)
    if twilio_config is None or not current_app.config['USE_MFA'] or not user.has_role(*current_app.config['MFA_ROLES']) or not user.social_id.startswith('local'):
        return ('File not found', 404)
    form = MFASMSSetupForm(request.form)
    user = load_user(user.id)
    if request.method == 'GET' and user.otp_secret is not None and user.otp_secret.startswith(':phone:'):
        form.phone_number.data = re.sub(r'^:phone:', '', user.otp_secret)
    if request.method == 'POST' and form.submit.data:
        phone_number = form.phone_number.data
        if phone_number_is_valid(phone_number):
            phone_number = phone_number_in_e164(phone_number)
            verification_code = random_digits(daconfig['verification code digits'])
            message = word("Your verification code is") + " " + str(verification_code) + "."
            success = send_sms(to=phone_number, body=message)
            if success:
                session['phone_number'] = phone_number
                key = 'da:mfa:phone:' + str(phone_number) + ':code'
                pipe = r.pipeline()
                pipe.set(key, verification_code)
                pipe.expire(key, daconfig['verification code timeout'])
                pipe.execute()
                return redirect(url_for('users.mfa_verify_sms_setup'))
            flash(word("There was a problem sending the text message."), 'error')
            if in_login:
                del session['validated_user']
                if 'next' in session:
                    del session['next']
                return redirect(url_for('user.login'))
            return redirect(url_for('users.user_profile_page'))
        flash(word("Invalid phone number."), 'error')
    return render_template('flask_user/mfa_sms_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("""Enter your phone number.  A confirmation code will be sent to you."""))


@users_bp.route('/mfa_verify_sms_setup', methods=['POST', 'GET'])
def mfa_verify_sms_setup():
    in_login = False
    if current_user.is_authenticated:
        user = current_user
    elif 'validated_user' in session:
        in_login = True
        user = load_user(session['validated_user'])
    else:
        return ('File not found', 404)
    if 'phone_number' not in session or twilio_config is None or not current_app.config['USE_MFA'] or not user.has_role(*current_app.config['MFA_ROLES']) or not user.social_id.startswith('local'):
        return ('File not found', 404)
    form = MFAVerifySMSSetupForm(request.form)
    if request.method == 'POST' and form.submit.data:
        phone_number = session['phone_number']
        del session['phone_number']
        key = 'da:mfa:phone:' + str(phone_number) + ':code'
        verification_code = r.get(key)
        r.delete(key)
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        if verification_code is None:
            flash(word('Your verification code was missing or expired'), 'error')
            return redirect(url_for('users.user_profile_page'))
        if verification_code.decode() == supplied_verification_code:
            user = load_user(user.id)
            user.otp_secret = ':phone:' + phone_number
            db.session.commit()
            if in_login:
                if 'next' in session:
                    next_url = session['next']
                    del session['next']
                else:
                    next_url = url_for('users.interview_list', from_login='1')
                return docassemble_flask_user.views._do_login_user(user, next_url, False)
            flash(word("You are now set up with two factor authentication."), 'success')
            return redirect(url_for('users.user_profile_page'))
    return render_template('flask_user/mfa_verify_sms_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word('We just sent you a text message with a verification code.  Enter the verification code to proceed.'))


@users_bp.route('/mfa_login', methods=['POST', 'GET'])
def mfa_login():
    if not current_app.config['USE_MFA']:
        logmessage("mfa_login: two factor authentication not configured")
        return ('File not found', 404)
    if 'validated_user' not in session:
        logmessage("mfa_login: validated_user not in session")
        return ('File not found', 404)
    user = load_user(session['validated_user'])
    if current_user.is_authenticated and current_user.id != user.id:
        del session['validated_user']
        return ('File not found', 404)
    if user is None or user.otp_secret is None or not user.social_id.startswith('local'):
        logmessage("mfa_login: user not setup for MFA where validated_user was " + str(session['validated_user']))
        return ('File not found', 404)
    form = MFALoginForm(request.form)
    if not form.next.data:
        form.next.data = _get_safe_next_param('next', url_for('admin.interview_list', from_login='1'))
    if request.method == 'POST' and form.submit.data:
        del session['validated_user']
        if 'next' in session:
            safe_next = session['next']
            del session['next']
        else:
            safe_next = form.next.data
        if BAN_IP_ADDRESSES:
            fail_key = 'da:failedlogin:ip:' + str(get_requester_ip(request))
            failed_attempts = r.get(fail_key)
            if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
                return ('File not found', 404)
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        if user.otp_secret.startswith(':phone:'):
            phone_number = re.sub(r'^:phone:', '', user.otp_secret)
            key = 'da:mfa:phone:' + str(phone_number) + ':code'
            verification_code = r.get(key)
            r.delete(key)
            if verification_code is None or supplied_verification_code != verification_code.decode():
                r.incr(fail_key)
                r.expire(fail_key, 86400)
                flash(word("Your verification code was invalid or expired."), 'error')
                return redirect(url_for('user.login'))
            if failed_attempts is not None:
                r.delete(fail_key)
        else:
            totp = pyotp.TOTP(user.otp_secret)
            if not totp.verify(supplied_verification_code):
                r.incr(fail_key)
                r.expire(fail_key, 86400)
                flash(word("Your verification code was invalid."), 'error')
                if 'validated_user' in session:
                    del session['validated_user']
                if 'next' in session:
                    return redirect(url_for('user.login', next=session['next']))
                return redirect(url_for('user.login'))
            if failed_attempts is not None:
                r.delete(fail_key)
        return docassemble_flask_user.views._do_login_user(user, safe_next, False)
    description = word("This account uses two-factor authentication.")
    if user.otp_secret.startswith(':phone:'):
        description += "  " + word("Please enter the verification code from the text message we just sent you.")
    else:
        description += "  " + word("Please enter the verification code from your authentication app.")
    return render_template('flask_user/mfa_login.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=description)


@users_bp.route('/user/manage', methods=['POST', 'GET'])
def manage_account():
    if (current_user.is_authenticated and current_user.has_roles(['admin'])) or not daconfig.get('user can delete account', True):
        abort(403)
    if current_user.is_anonymous and not daconfig.get('allow anonymous access', True):
        return redirect(url_for('user.login'))
    secret = request.cookies.get('secret', None)
    if current_user.is_anonymous:
        logged_in = False
        if 'tempuser' not in session:
            return ('File not found', 404)
        temp_user_id = int(session['tempuser'])
    else:
        logged_in = True
        temp_user_id = -1
    delete_shared = daconfig.get('delete account deletes shared', False)
    form = ManageAccountForm(request.form)
    if request.method == 'POST' and form.validate():
        if current_user.is_authenticated:
            user_interviews(user_id=current_user.id, secret=secret, exclude_invalid=False, action='delete_all', delete_shared=delete_shared)
            the_user_id = current_user.id
            logout_user()
            delete_user_data(the_user_id, r, r_user)
        else:
            sessions_to_delete = set()
            interview_query = db.session.execute(select(UserDictKeys.filename, UserDictKeys.key).where(UserDictKeys.temp_user_id == temp_user_id).group_by(UserDictKeys.filename, UserDictKeys.key))
            for interview_info in interview_query:
                sessions_to_delete.add((interview_info.key, interview_info.filename))
            for session_id, yaml_filename in sessions_to_delete:
                manual_checkout(manual_session_id=session_id, manual_filename=yaml_filename)
                reset_user_dict(session_id, yaml_filename, temp_user_id=temp_user_id, force=delete_shared)
            delete_temp_user_data(temp_user_id, r)
        delete_session_info()
        session.clear()
        response = redirect(exit_page)
        response.set_cookie('remember_token', '', expires=0)
        response.set_cookie('visitor_secret', '', expires=0)
        response.set_cookie('secret', '', expires=0)
        response.set_cookie('session', '', expires=0)
        return response
    if logged_in:
        description = word("""You can delete your account on this page.  Type "delete my account" (in lowercase, without the quotes) into the box below and then press the "Delete account" button.  This will erase your interview sessions and your user profile.  To go back to your user profile page, press the "Cancel" button.""")
    else:
        description = word("""You can delete your account on this page.  Type "delete my account" (in lowercase, without the quotes) into the box below and then press the "Delete account" button.  This will erase your interview sessions.""")
    return render_template('users/manage_account.html', form=form, version_warning=None, title=word("Manage account"), tab_title=word("Manage account"), page_title=word("Manage account"), description=description, logged_in=logged_in)


@users_bp.route('/me', methods=['GET'])
def whoami():
    if current_user.is_authenticated:
        return jsonify(logged_in=True, user_id=current_user.id, email=current_user.email, roles=[role.name for role in current_user.roles], firstname=current_user.first_name, lastname=current_user.last_name, country=current_user.country, subdivisionfirst=current_user.subdivisionfirst, subdivisionsecond=current_user.subdivisionsecond, subdivisionthird=current_user.subdivisionthird, organization=current_user.organization, timezone=current_user.timezone)
    return jsonify(logged_in=False)
