import sys
from flask_user.forms import RegisterForm, LoginForm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, BooleanField, SelectField, SelectMultipleField, HiddenField, validators
from wtforms.validators import DataRequired, Email

from docassemble.base.functions import word

def fix_nickname(form, field):
    field.data = form.first_name.data + ' ' + form.last_name.data
    return

class MySignInForm(LoginForm):
    def validate(self):
        import redis
        import docassemble.base.util
        from flask import request
        r = redis.StrictRedis(host=docassemble.base.util.redis_server, db=0)
        key = 'da:failedlogin:ip:' + str(request.remote_addr)
        failed_attempts = r.get(key)
        if failed_attempts is not None and int(failed_attempts) > 10:
            return False
        result = super(MySignInForm, self).validate()
        if result is False:
            r.incr(key)
            r.expire(key, 86400)
        return result

class MyRegisterForm(RegisterForm):
    first_name = StringField(word('First name'))
    last_name = StringField(word('Last name'))
    social_id = StringField(word('Social ID'))
    nickname = StringField(word('Nickname'), [fix_nickname])

def length_two(form, field):
    if len(field.data) != 2:
        raise ValidationError(word('Must be a two-letter code'))

class NewPrivilegeForm(FlaskForm):
    name = StringField(word('Name of new privilege'), validators=[
        DataRequired(word('Name of new privilege is required'))])
    submit = SubmitField(word('Add'))

class UserProfileForm(FlaskForm):
    first_name = StringField(word('First name'), validators=[
        DataRequired(word('First name is required'))])
    last_name = StringField(word('Last name'), validators=[
        DataRequired(word('Last name is required'))])
    country = StringField(word('Country code'), [validators.Length(min=0, max=2)])
    subdivisionfirst = StringField(word('First subdivision'), [validators.Length(min=0, max=3)])
    subdivisionsecond = StringField(word('Second subdivision'), [validators.Length(min=0, max=50)])
    subdivisionthird = StringField(word('Third subdivision'), [validators.Length(min=0, max=50)])
    organization = StringField(word('Organization'), [validators.Length(min=0, max=64)])
    language = StringField(word('Language'), [validators.Length(min=0, max=64)])
    timezone = SelectField(word('Time Zone'))
    submit = SubmitField(word('Save'))

class EditUserProfileForm(UserProfileForm):
    email = StringField(word('E-mail'), validators=[Email(word('Must be a valid e-mail address')), DataRequired(word('E-mail is required'))])
    role_id = SelectMultipleField(word('Privileges'), coerce=int)
    active = BooleanField(word('Active'))

class RequestDeveloperForm(FlaskForm):
    reason = StringField(word('Reason for needing developer account (optional)'))
    submit = SubmitField(word('Submit'))

class MyInviteForm(FlaskForm):
    email = StringField(word('E-mail'), validators=[
        validators.Required(word('E-mail is required')),
        validators.Email(word('Invalid E-mail'))])
    role_id = SelectField(word('Role'))
    next = HiddenField()
    submit = SubmitField(word('Invite'))

