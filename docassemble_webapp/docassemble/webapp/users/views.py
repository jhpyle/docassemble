from flask import redirect, render_template, render_template_string, request, flash
from flask import url_for as flask_url_for
from flask_user import current_user, login_required, roles_required, emails
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.users.forms import UserProfileForm, EditUserProfileForm, MyRegisterForm, MyInviteForm, NewPrivilegeForm
from docassemble.webapp.users.models import UserAuthModel, UserModel, Role, MyUserInvitation
from docassemble.base.functions import word, debug_status, get_default_timezone
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig

import random
import string
import pytz

HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)

def url_for(*pargs, **kwargs):
    if HTTP_TO_HTTPS:
        kwargs['_external'] = True
        kwargs['_scheme'] = 'https'
    return flask_url_for(*pargs, **kwargs)

@app.route('/privilegelist', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def privilege_list():
    output = '<ol>';
    for role in db.session.query(Role).order_by(Role.name):
        if role.name not in ['user', 'admin', 'developer', 'advocate', 'cron']:
            output += '<li>' + str(role.name) + ' <a href="' + url_for('delete_privilege', id=role.id) + '">Delete</a></li>'
        else:
            output += '<li>' + str(role.name) + '</li>'
            
    output += '</ol>'
    return render_template('users/rolelist.html', page_title=word('Privileges'), tab_title=word('Privileges'), privilegelist=output)

@app.route('/userlist', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def user_list():
    output = '<ol>';
    for user in db.session.query(UserModel).order_by(UserModel.last_name, UserModel.first_name, UserModel.email):
        if user.nickname == 'cron':
            continue
        name_string = ''
        if user.first_name:
            name_string += str(user.first_name) + " "
        if user.last_name:
            name_string += str(user.last_name)
        if name_string:
            name_string = str(name_string) + ', '
        active_string = ''
        if not user.active:
            active_string = ' (account disabled)'
        output += '<li>' + str(name_string) + '<a href="' + url_for('edit_user_profile_page', id=user.id) + '">' + str(user.email) + "</a>" + active_string + "</li>"
    output += '</ol>'
    return render_template('users/userlist.html', page_title=word('User List'), tab_title=word('User List'), userlist=output)

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
    the_role_id = list()
    for role in user.roles:
        the_role_id.append(str(role.id))
    if len(the_role_id) == 0:
        the_role_id = [str(Role.query.filter_by(name='user').first().id)]
    form = EditUserProfileForm(request.form, user, role_id=the_role_id)
    form.role_id.choices = [(r.id, r.name) for r in db.session.query(Role).filter(Role.name != 'cron', Role.name != 'admin').order_by('name')]
    form.timezone.choices = [(x, x) for x in sorted([tz for tz in pytz.all_timezones])]
    form.timezone.default = the_tz
    if str(form.timezone.data) == 'None':
        form.timezone.data = the_tz
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
    return render_template('users/edit_user_profile_page.html', page_title=word('Edit User Profile'), tab_title=word('Edit User Profile'), form=form)

@app.route('/privilege/add', methods=['GET', 'POST'])
@login_required
def add_privilege():
    form = NewPrivilegeForm(request.form, current_user)

    if request.method == 'POST' and form.validate():
        for role in db.session.query(Role).order_by(Role.name):
            if role.name == form.name.data:
                flash(word('The privilege could not be added because it already exists.'), 'error')
                return redirect(url_for('privilege_list'))
        
        db.session.add(Role(name=form.name.data))
        db.session.commit()
        flash(word('The privilege was added.'), 'success')
        return redirect(url_for('privilege_list'))

    return render_template('users/new_role_page.html', page_title=word('Add Privilege'), tab_title=word('Add Privilege'), form=form)

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    the_tz = (current_user.timezone if current_user.timezone else get_default_timezone())
    form = UserProfileForm(request.form, current_user)
    form.timezone.choices = [(x, x) for x in sorted([tz for tz in pytz.all_timezones])]
    form.timezone.default = the_tz
    if str(form.timezone.data) == 'None':
        form.timezone.data = the_tz
    if request.method == 'POST' and form.validate():
        form.populate_obj(current_user)
        db.session.commit()
        flash(word('Your information was saved.'), 'success')
        return redirect(url_for('interview_list'))
    return render_template('users/user_profile_page.html', page_title=word('User Profile'), tab_title=word('User Profile'), form=form, debug=debug_status())

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
    user_manager = app.user_manager

    next = request.args.get('next',
                            _endpoint_url(user_manager.after_invite_endpoint))

    user_role = Role.query.filter_by(name='user').first()
    invite_form = MyInviteForm(request.form)
    invite_form.role_id.choices = [(str(r.id), str(r.name)) for r in db.session.query(Role).filter(Role.name != 'cron', Role.name != 'admin').order_by('name')]
    invite_form.role_id.default = str(user_role.id)
    if str(invite_form.role_id.data) == 'None':
        invite_form.role_id.data = str(user_role.id)
    if request.method=='POST' and invite_form.validate():
        email = invite_form.email.data

        the_role_id = None
        
        for role in Role.query.order_by('id'):
            if role.id == invite_form.role_id and role.name != 'admin' and role.name != 'cron':
                the_role_id = role.id

        if the_role_id is None:
            the_role_id = user_role.id

        # user_class_fields = User.__dict__
        # user_fields = {
        #     "email": email
        # }

        user, user_email = user_manager.find_user_by_email(email)
        if user:
            flash("A user with that email has already registered", "error")
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
            # Send 'invite' email
            logmessage("Trying to send e-mail")
            emails.send_invite_email(user_invite, accept_invite_link)
        except Exception as e:
            logmessage("Failed to send e-mail")
            # delete new User object if send fails
            user_invite.delete()
            db.session.commit()
            flash(word('Unable to send e-mail.  Error was: ') + str(e), 'error')
            return redirect(url_for('invite'))
        # signals \
        #     .user_sent_invitation \
        #     .send(app._get_current_object(), user_invite=user_invite,
        #           form=invite_form)

        flash(word('Invitation has been sent.'), 'success')
        return redirect(next)

    return render_template('flask_user/invite.html', form=invite_form)
