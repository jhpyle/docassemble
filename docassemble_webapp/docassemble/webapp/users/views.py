import datetime
import email.utils
import json
import re
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
# import docassemble.webapp.daredis
from docassemble.webapp.app_object import app
from docassemble.webapp.backend import delete_user_data
from docassemble.webapp.db_object import db
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.users.forms import UserProfileForm, EditUserProfileForm, PhoneUserProfileForm, MyInviteForm, NewPrivilegeForm, UserAddForm
from docassemble.webapp.users.models import UserAuthModel, UserModel, Role, MyUserInvitation
from docassemble.base.functions import word, debug_status, get_default_timezone, server
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig
from docassemble.base.generate_key import random_alphanumeric
from docassemble_flask_user import current_user, login_required, roles_required, emails
from sqlalchemy import and_, not_, select
from flask import make_response, redirect, render_template, request, flash, current_app, url_for
from markupsafe import Markup

HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)
PAGINATION_LIMIT = daconfig.get('pagination limit', 100)
PAGINATION_LIMIT_PLUS_ONE = PAGINATION_LIMIT + 1


@app.route('/privilegelist', methods=['GET', 'POST'])
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
            output += '        <tr><td>' + str(role.name) + '</td><td class="text-end"><a class="btn ' + app.config['BUTTON_CLASS'] + ' btn-danger btn-sm" href="' + url_for('delete_privilege', privilege_id=role.id) + '">Delete</a></td></tr>\n'
        else:
            output += '        <tr><td>' + str(role.name) + '</td><td>&nbsp;</td></tr>\n'

    output += """\
      </tbody>
    </table>
"""
    response = make_response(render_template('users/rolelist.html', version_warning=None, bodyclass='daadminbody', page_title=word('Privileges'), tab_title=word('Privileges'), privilegelist=output, can_edit=can_edit), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@app.route('/userlist', methods=['GET'])
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


@app.route('/privilege/<int:privilege_id>/delete', methods=['GET'])
@login_required
@roles_required('admin', permission='edit_privileges')
def delete_privilege(privilege_id):
    setup_translation()
    if not privilege_id:
        flash(word('The role could not be deleted.'), 'error')
        return redirect(url_for('privilege_list'))
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
    return redirect(url_for('privilege_list'))


@app.route('/user/<int:user_id>/editprofile', methods=['GET', 'POST'])
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
        return redirect(url_for('user_list'))
    user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=user_id)).unique().scalar_one()
    if not user:
        flash(word('The user account did not exit.'), 'danger')
        return redirect(url_for('user_list'))
    if not is_admin:
        protected_user = False
        for role in user.roles:
            if role.name in ('admin', 'developer', 'advocate'):
                protected_user = True
                break
        if protected_user:
            flash(word('You do not have sufficient privileges to edit this user.'), 'danger')
            return redirect(url_for('user_list'))
    the_tz = user.timezone if user.timezone else get_default_timezone()
    if user is None or user.social_id.startswith('disabled$'):
        return redirect(url_for('user_list'))
    if 'disable_mfa' in request.args and int(request.args['disable_mfa']) == 1:
        user.otp_secret = None
        db.session.commit()
        # docassemble.webapp.daredis.clear_user_cache()
        return redirect(url_for('edit_user_profile_page', user_id=user_id))
    if 'reset_email_confirmation' in request.args and int(request.args['reset_email_confirmation']) == 1:
        user.confirmed_at = None
        db.session.commit()
        # docassemble.webapp.daredis.clear_user_cache()
        return redirect(url_for('edit_user_profile_page', user_id=user_id))
    if can_delete and daconfig.get('admin can delete account', True) and user.id != current_user.id:
        if 'delete_account' in request.args and int(request.args['delete_account']) == 1:
            server.user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=False)
            delete_user_data(user_id, server.server_redis, server.server_redis_user)
            db.session.commit()
            flash(word('The user account was deleted.'), 'success')
            return redirect(url_for('user_list'))
        if 'delete_account_complete' in request.args and int(request.args['delete_account_complete']) == 1:
            server.user_interviews(user_id=user_id, secret=None, exclude_invalid=False, action='delete_all', delete_shared=True)
            delete_user_data(user_id, server.server_redis, server.server_redis_user)
            db.session.commit()
            flash(word('The user account was deleted.'), 'success')
            return redirect(url_for('user_list'))
    the_role_id = []
    for role in user.roles:
        the_role_id.append(role.id)
    if len(the_role_id) == 0:
        the_role_id = [db.session.execute(select(Role.id).filter_by(name='user')).scalar_one()]
    form = EditUserProfileForm(request.form, obj=user, role_id=the_role_id)
    if request.method == 'POST' and form.cancel.data:
        flash(word('The user profile was not changed.'), 'success')
        return redirect(url_for('user_list'))
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
        return redirect(url_for('user_list'))
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


@app.route('/privilege/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin', permission='edit_privileges')
def add_privilege():
    setup_translation()
    form = NewPrivilegeForm(request.form, obj=current_user)

    if request.method == 'POST' and form.validate():
        for role in db.session.execute(select(Role).order_by(Role.name)).scalars():
            if role.name == form.name.data:
                flash(word('The privilege could not be added because it already exists.'), 'error')
                return redirect(url_for('privilege_list'))

        db.session.add(Role(name=form.name.data))
        db.session.commit()
        flash(word('The privilege was added.'), 'success')
        return redirect(url_for('privilege_list'))

    response = make_response(render_template('users/new_role_page.html', version_warning=None, bodyclass='daadminbody', page_title=word('Add Privilege'), tab_title=word('Add Privilege'), form=form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    setup_translation()
    if not (app.config['SHOW_PROFILE'] or current_user.has_roles(['admin'])):
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
                if reg_field in app.config['USER_PROFILE_FIELDS']:
                    setattr(current_user, reg_field, getattr(form, reg_field).data)
        db.session.commit()
        # docassemble.webapp.daredis.clear_user_cache()
        flash(word('Your information was saved.'), 'success')
        return redirect(url_for('interview_list'))
    response = make_response(render_template('users/user_profile_page.html', version_warning=None, page_title=word('User Profile'), tab_title=word('User Profile'), form=form, debug=debug_status()), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url


@app.route('/user/invite', methods=['GET', 'POST'])
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
            return redirect(url_for('invite'))
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


@app.route('/user/add', methods=['GET', 'POST'])
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
        user, user_email = app.user_manager.find_user_by_email(add_form.email.data)  # pylint: disable=unused-variable
        if user:
            flash(word("A user with that e-mail has already registered"), "error")
            return redirect(url_for('user_add'))
        user_auth = UserAuthModel(password=app.user_manager.hash_password(add_form.password.data))
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
        return redirect(url_for('user_list'))
    response = make_response(render_template('users/add_user_page.html', version_warning=None, bodyclass='daadminbody', page_title=word('Add User'), tab_title=word('Add User'), form=add_form), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response
