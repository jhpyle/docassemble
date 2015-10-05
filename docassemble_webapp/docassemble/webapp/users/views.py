from flask import redirect, render_template, render_template_string, request, url_for, flash
from flask_user import current_user, login_required, roles_required
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.users.forms import UserProfileForm, EditUserProfileForm, MyRegisterForm
from docassemble.webapp.users.models import UserAuth, User, Role
from docassemble.base.util import word
from docassemble.base.logger import logmessage
import random
import string

@app.route('/userlist', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def user_list():
    output = '<ol>';
    for user in db.session.query(User).order_by(User.last_name, User.first_name, User.email):
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
    return render_template('users/userlist.html', userlist=output)

@app.route('/user/<id>/editprofile', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_user_profile_page(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)
    the_role_id = None
    for role in user.roles:
        the_role_id = role.id
    form = EditUserProfileForm(request.form, user, role_id=the_role_id)
    form.role_id.choices = [(r.id, r.name) for r in Role.query.order_by('name')]
    logmessage("Setting default to " + str(the_role_id))
    
    if request.method == 'POST' and form.validate():

        form.populate_obj(user)
        roles_to_remove = list()
        for role in user.roles:
            roles_to_remove.append(role)
        for role in roles_to_remove:
            user.roles.remove(role)
        for role in Role.query.order_by('id'):
            if role.id == form.role_id.data:
                user.roles.append(role)
                break

        db.session.commit()

        flash(word('The information was saved.'), 'success')
        return redirect(url_for('user_list'))

    return render_template('users/edit_user_profile_page.html', form=form)
    
@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    form = UserProfileForm(request.form, current_user)

    if request.method == 'POST' and form.validate():

        form.populate_obj(current_user)

        db.session.commit()

        flash(word('Your information was saved.'), 'success')
        return redirect(url_for('index'))

    return render_template('users/user_profile_page.html',
        form=form)

