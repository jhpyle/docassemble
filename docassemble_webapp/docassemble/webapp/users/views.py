from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from flask import redirect, render_template, render_template_string, request, flash, current_app
from flask import url_for as url_for
from flask_user import current_user, login_required, roles_required, emails
from docassemble.webapp.users.forms import UserProfileForm, EditUserProfileForm, PhoneUserProfileForm, MyRegisterForm, MyInviteForm, NewPrivilegeForm, UserAddForm
from docassemble.webapp.users.models import UserAuthModel, UserModel, Role, MyUserInvitation
from docassemble.base.functions import word, debug_status, get_default_timezone
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig
from docassemble.base.generate_key import random_alphanumeric
from sqlalchemy import or_, and_

import random
import string
import pytz
import datetime
import re

HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)

# def url_for(*pargs, **kwargs):
#     if HTTP_TO_HTTPS:
#         kwargs['_external'] = True
#         kwargs['_scheme'] = 'https'
#     return flask_url_for(*pargs, **kwargs)

@app.route('/privilegelist', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def privilege_list():
    output = """\
    <table class="table">
      <thead>
        <tr>
          <th scope="col">""" + word("Privilege") + """</th>
          <th scope="col">""" + word("Action") + """</th>
        </tr>
      </thead>
      <tbody>
"""
    for role in db.session.query(Role).order_by(Role.name):
        if role.name not in ['user', 'admin', 'developer', 'advocate', 'cron', 'trainer']:
            output += '        <tr><td>' + str(role.name) + '</td><td><a class="btn btn-danger btn-sm" href="' + url_for('delete_privilege', id=role.id) + '">Delete</a></td></tr>\n'
        else:
            output += '        <tr><td>' + str(role.name) + '</td><td>&nbsp;</td></tr>\n'
            
    output += """\
      </tbody>
    </table>
"""
    return render_template('users/rolelist.html', version_warning=None, bodyclass='adminbody', page_title=word('Privileges'), tab_title=word('Privileges'), privilegelist=output)

@app.route('/userlist', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def user_list():
    users = list()
    for user in db.session.query(UserModel).order_by(UserModel.id):
        if user.nickname == 'cron':
            continue
        name_string = ''
        if user.first_name:
            name_string += str(user.first_name) + " "
        if user.last_name:
            name_string += str(user.last_name)
        if name_string:
            name_string = str(name_string)
        active_string = ''
        if user.email is None:
            user_indicator = user.nickname
        else:
            user_indicator = user.email
        if user.active:
            is_active = True
        else:
            is_active = False
        users.append(dict(name=name_string, email=user_indicator, active=is_active, id=user.id))
    return render_template('users/userlist.html', version_warning=None, bodyclass='adminbody', page_title=word('User List'), tab_title=word('User List'), users=users)

@app.route('/privilege/<id>/delete', methods=['GET'])
@login_required
@roles_required('admin')
def delete_privilege(id):
    role = Role.query.filter_by(id=id).first()
    user_role = Role.query.filter_by(name='user').first()
    if role is None or role.name in ['user', 'admin', 'developer', 'advocate', 'cron']:
        flash(word('The role could not be deleted.'), 'error')
    else:
        for user in db.session.query(UserModel):
            roles_to_remove = list()
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
    return redirect(url_for('privilege_list'))

@app.route('/user/<id>/editprofile', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_user_profile_page(id):
    user = UserModel.query.filter_by(id=id).first()
    the_tz = (user.timezone if user.timezone else get_default_timezone())
    if user is None:
        abort(404)
    if 'disable_mfa' in request.args and int(request.args['disable_mfa']) == 1:
        user.otp_secret = None
        db.session.commit()
        return redirect(url_for('edit_user_profile_page', id=id))
    if 'reset_email_confirmation' in request.args and int(request.args['reset_email_confirmation']) == 1:
        user.confirmed_at = None
        db.session.commit()
        return redirect(url_for('edit_user_profile_page', id=id))
    the_role_id = list()
    for role in user.roles:
        the_role_id.append(str(role.id))
    if len(the_role_id) == 0:
        the_role_id = [str(Role.query.filter_by(name='user').first().id)]
    form = EditUserProfileForm(request.form, obj=user, role_id=the_role_id)
    form.role_id.choices = [(r.id, r.name) for r in db.session.query(Role).filter(Role.name != 'cron').order_by('name')]
    form.timezone.choices = [(x, x) for x in sorted([tz for tz in pytz.all_timezones])]
    form.timezone.default = the_tz
    if str(form.timezone.data) == 'None':
        form.timezone.data = the_tz
    if user.otp_secret is None:
        form.uses_mfa.data = False
    else:
        form.uses_mfa.data = True
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        roles_to_remove = list()
        the_role_id = list()
        for role in user.roles:
            roles_to_remove.append(role)
        for role in roles_to_remove:
            user.roles.remove(role)
        for role in Role.query.order_by('id'):
            if role.id in form.role_id.data:
                user.roles.append(role)
                the_role_id.append(role.id)

        db.session.commit()

        flash(word('The information was saved.'), 'success')
        return redirect(url_for('user_list'))

    form.role_id.default = the_role_id
    confirmation_feature = True if user.id > 2 else False
    return render_template('users/edit_user_profile_page.html', version_warning=None, page_title=word('Edit User Profile'), tab_title=word('Edit User Profile'), form=form, confirmation_feature=confirmation_feature)

@app.route('/privilege/add', methods=['GET', 'POST'])
@login_required
def add_privilege():
    form = NewPrivilegeForm(request.form, obj=current_user)

    if request.method == 'POST' and form.validate():
        for role in db.session.query(Role).order_by(Role.name):
            if role.name == form.name.data:
                flash(word('The privilege could not be added because it already exists.'), 'error')
                return redirect(url_for('privilege_list'))
        
        db.session.add(Role(name=form.name.data))
        db.session.commit()
        flash(word('The privilege was added.'), 'success')
        return redirect(url_for('privilege_list'))

    return render_template('users/new_role_page.html', version_warning=None, bodyclass='adminbody', page_title=word('Add Privilege'), tab_title=word('Add Privilege'), form=form)

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    the_tz = (current_user.timezone if current_user.timezone else get_default_timezone())
    if current_user.social_id and current_user.social_id.startswith('phone$'):
        form = PhoneUserProfileForm(request.form, obj=current_user)
    else:
        form = UserProfileForm(request.form, obj=current_user)
    form.timezone.choices = [(x, x) for x in sorted([tz for tz in pytz.all_timezones])]
    form.timezone.default = the_tz
    if str(form.timezone.data) == 'None':
        form.timezone.data = the_tz
    if request.method == 'POST' and form.validate():
        form.populate_obj(current_user)
        db.session.commit()
        flash(word('Your information was saved.'), 'success')
        return redirect(url_for('interview_list'))
    return render_template('users/user_profile_page.html', version_warning=None, page_title=word('User Profile'), tab_title=word('User Profile'), form=form, debug=debug_status())

def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url

@app.route('/user/invite', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def invite():
    """ Allows users to send invitations to register an account """
    user_manager = current_app.user_manager

    next = request.args.get('next',
                            _endpoint_url(user_manager.after_invite_endpoint))

    user_role = Role.query.filter_by(name='user').first()
    invite_form = MyInviteForm(request.form)
    invite_form.role_id.choices = [(str(r.id), str(r.name)) for r in db.session.query(Role).filter(and_(Role.name != 'cron', Role.name != 'admin')).order_by('name')]
    invite_form.role_id.default = str(user_role.id)
    if str(invite_form.role_id.data) == 'None':
        invite_form.role_id.data = str(user_role.id)
    if request.method=='POST' and invite_form.validate():
        email = invite_form.email.data

        the_role_id = None
        
        for role in Role.query.order_by('id'):
            if role.id == int(invite_form.role_id.data) and role.name != 'admin' and role.name != 'cron':
                the_role_id = role.id

        if the_role_id is None:
            the_role_id = user_role.id

        user, user_email = user_manager.find_user_by_email(email)
        if user:
            flash(word("A user with that e-mail has already registered"), "error")
            return redirect(url_for('invite'))
        else:
            user_invite = MyUserInvitation(email=email, role_id=the_role_id, invited_by_user_id=current_user.id)
            db.session.add(user_invite)
            db.session.commit()
        token = user_manager.generate_token(user_invite.id)
        accept_invite_link = url_for('user.register',
                                     token=token,
                                     _external=True)

        user_invite.token = token
        db.session.commit()
        try:
            logmessage("Trying to send e-mail to " + str(user_invite.email))
            emails.send_invite_email(user_invite, accept_invite_link)
        except Exception as e:
            logmessage("Failed to send e-mail")
            db.session.delete(user_invite)
            db.session.commit()
            flash(word('Unable to send e-mail.  Error was: ') + str(e), 'error')
            return redirect(url_for('invite'))
        flash(word('Invitation has been sent.'), 'success')
        return redirect(next)

    return render_template('flask_user/invite.html', version_warning=None, bodyclass='adminbody', page_title=word('Invite User'), tab_title=word('Invite User'), form=invite_form)

@app.route('/user/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def user_add():
    user_role = Role.query.filter_by(name='user').first()
    add_form = UserAddForm(request.form, role_id=[str(user_role.id)])
    add_form.role_id.choices = [(r.id, r.name) for r in db.session.query(Role).filter(Role.name != 'cron').order_by('name')]
    add_form.role_id.default = user_role.id
    if str(add_form.role_id.data) == 'None':
        add_form.role_id.data = user_role.id
    if request.method == 'POST' and add_form.validate():
        user, user_email = app.user_manager.find_user_by_email(add_form.email.data)
        if user:
            flash(word("A user with that e-mail has already registered"), "error")
            return redirect(url_for('user_add'))
        user_auth = UserAuthModel(password=app.user_manager.hash_password(add_form.password.data))
        while True:
            new_social = 'local$' + random_alphanumeric(32)
            existing_user = UserModel.query.filter_by(social_id=new_social).first()
            if existing_user:
                continue
            break
        the_user = UserModel(
            active=True,
            nickname=re.sub(r'@.*', '', add_form.email.data),
            social_id=new_social,
            email=add_form.email.data,
            user_auth=user_auth,
            first_name = add_form.first_name.data,
            last_name = add_form.last_name.data,
            confirmed_at = datetime.datetime.now()
        )
        num_roles = 0
        for role in Role.query.order_by('id'):
            if role.id in add_form.role_id.data:
                the_user.roles.append(role)
                num_roles +=1
        if num_roles == 0:
            the_user.roles.append(user_role)
        db.session.add(user_auth)
        db.session.add(the_user)
        db.session.commit()
        flash(word("The new user has been created"), "success")
        return redirect(url_for('user_list'))
    return render_template('users/add_user_page.html', version_warning=None, bodyclass='adminbody', page_title=word('Add User'), tab_title=word('Add User'), form=add_form)
