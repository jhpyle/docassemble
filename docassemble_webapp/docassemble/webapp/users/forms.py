import sys
import re
from flask_user.forms import RegisterForm, LoginForm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, BooleanField, SelectField, SelectMultipleField, HiddenField, validators
from wtforms.validators import DataRequired, Email, Optional

from docassemble.base.functions import word
from docassemble.base.config import daconfig

def fix_nickname(form, field):
    field.data = form.first_name.data + ' ' + form.last_name.data
    return

class MySignInForm(LoginForm):
    def validate(self):
        import redis
        import docassemble.base.util
        from flask import request, abort
        r = redis.StrictRedis(host=docassemble.base.util.redis_server, db=0)
        key = 'da:failedlogin:ip:' + str(request.remote_addr)
        failed_attempts = r.get(key)
        if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
            abort(404)
        result = super(MySignInForm, self).validate()
        if result is False:
            r.incr(key)
            r.expire(key, daconfig['ban period'])
        elif failed_attempts is not None:
            r.delete(key)
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
    uses_mfa = BooleanField(word('Uses two-factor authentication'))

class PhoneUserProfileForm(UserProfileForm):
    def validate(self):
        if self.email.data:
            from flask_login import current_user
            if current_user.social_id.startswith('phone$'):
                from docassemble.webapp.users.models import UserModel
                from flask import flash
                existing_user = UserModel.query.filter_by(email=self.email.data, active=True).first()
                if existing_user is not None and existing_user.id != current_user.id:
                    flash(word("Please choose a different e-mail address."), 'error')
                    return False
        return super(PhoneUserProfileForm, self).validate()
    email = StringField(word('E-mail'), validators=[Optional(), Email(word('Must be a valid e-mail address'))])

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

class PhoneLoginForm(FlaskForm):
    phone_number = StringField(word('Phone number'), [validators.Length(min=5, max=255)])
    #next = HiddenField()
    submit = SubmitField(word('Go'))

class PhoneLoginVerifyForm(FlaskForm):
    phone_number = StringField(word('Phone number'), [validators.Length(min=5, max=255)])
    verification_code = StringField(word('Verification code'), [validators.Length(min=daconfig['verification code digits'], max=daconfig['verification code digits'])])
    #next = HiddenField()
    submit = SubmitField(word('Verify'))
    def validate(self):
        import redis
        import docassemble.base.util
        from docassemble.base.logger import logmessage
        from flask import request, abort
        result = True
        r = redis.StrictRedis(host=docassemble.base.util.redis_server, db=0)
        key = 'da:failedlogin:ip:' + str(request.remote_addr)
        failed_attempts = r.get(key)
        if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
            abort(404)
        verification_key = 'da:phonelogin:' + str(self.phone_number.data) + ':code'
        verification_code = r.get(verification_key)
        #r.delete(verification_key)
        supplied_verification_code = re.sub(r'[^0-9]', '', self.verification_code.data)
        logmessage("Supplied code is " + str(supplied_verification_code))
        if verification_code is None:
            logmessage("Verification code with " + str(verification_key) + " is None")
            result = False
        elif verification_code != supplied_verification_code:
            logmessage("Verification code with " + str(verification_key) + " which is " + str(verification_code) + " does not match supplied code, which is " + str(self.verification_code.data))
            result = False
        else:
            logmessage("Code matched")
        if result is False:
            logmessage("Problem with form")
            r.incr(key)
            r.expire(key, 86400)
        elif failed_attempts is not None:
            r.delete(key)
        return result

class MFASetupForm(FlaskForm):
    verification_code = StringField(word('Verification code'))
    submit = SubmitField(word('Verify'))

class MFALoginForm(FlaskForm):
    verification_code = StringField(word('Verification code'))
    next = HiddenField()
    submit = SubmitField(word('Verify'))

class MFAReconfigureForm(FlaskForm):
    reconfigure = SubmitField(word('Reconfigure'))
    disable = SubmitField(word('Disable'))
    cancel = SubmitField(word('Cancel'))

class MFAChooseForm(FlaskForm):
    auth = SubmitField(word('App'))
    sms = SubmitField(word('SMS'))
    cancel = SubmitField(word('Cancel'))

class MFASMSSetupForm(FlaskForm):
    phone_number = StringField(word('Phone number'), [validators.Length(min=5, max=255)])
    submit = SubmitField(word('Verify'))

class MFAVerifySMSSetupForm(FlaskForm):
    verification_code = StringField(word('Verification code'))
    submit = SubmitField(word('Verify'))
