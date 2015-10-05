# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user.forms import RegisterForm
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, ValidationError, BooleanField, SelectField
from wtforms.validators import DataRequired, Email

from docassemble.base.util import word

# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields

def fix_nickname(form, field):
    field.data = form.first_name.data + ' ' + form.last_name.data
    return

class MyRegisterForm(RegisterForm):
    first_name = StringField('First name')
    last_name = StringField('Last name')
    social_id = StringField('Social ID')
    nickname = StringField('Nickname', [fix_nickname])

def length_two(form, field):
    if len(field.data) != 2:
        raise ValidationError(word('Must be a two-letter code'))
    
# Define the User profile form
class UserProfileForm(Form):
    first_name = StringField(word('First name'), validators=[
        DataRequired(word('First name is required'))])
    last_name = StringField(word('Last name'), validators=[
        DataRequired(word('Last name is required'))])
    country = StringField(word('Country Code'), validators=[
        DataRequired(word('Country Code is required')), length_two])
    subdivisionfirst = StringField(word('First Subdivision'), validators=[
        DataRequired(word('First Subdivision is required')), length_two])
    subdivisionsecond = StringField(word('Second Subdivision'), validators=[
        DataRequired(word('Second Subdivision is required'))])
    subdivisionthird = StringField(word('Third Subdivision'), validators=[
        DataRequired(word('Third Subdivision is required'))])
    organization = StringField(word('Organization'), validators=[
        DataRequired(word('Organization is required'))])
    submit = SubmitField('Save')

class EditUserProfileForm(UserProfileForm):
    email = StringField(word('E-mail'), validators=[Email(word('Must be a valid e-mail address')), DataRequired(word('E-mail is required'))])
    role_id = SelectField(word('Roles'), coerce=int)
    active = BooleanField(word('Active'), validators=[
        DataRequired(word('Active is required'))])

