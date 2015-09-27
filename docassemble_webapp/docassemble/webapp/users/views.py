from flask import redirect, render_template, render_template_string, request, url_for, flash
from flask_user import current_user, login_required, roles_required
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.users.forms import UserProfileForm, EditUserProfileForm, MyRegisterForm
from docassemble.webapp.users.models import UserAuth, User
from docassemble.base.util import word
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
            name_string = ' (' + str(name_string) + ')'    
        output += '<li><a href="' + url_for('edit_user_profile_page', id=user.id) + '">' + str(user.email) + "</a>" + str(name_string) + "</li>"
    output += '</ol>'
    return render_template('users/userlist.html', userlist=output)

@app.route('/user/<id>/editprofile', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_user_profile_page(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)
    form = EditUserProfileForm(request.form, user)

    if request.method == 'POST' and form.validate():

        form.populate_obj(user)

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

