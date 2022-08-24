import re
import email.utils
from docassemble_flask_user.forms import RegisterForm, LoginForm, password_validator, unique_email_validator
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, ValidationError, BooleanField, SelectField, SelectMultipleField, HiddenField, validators, TextAreaField
from wtforms.validators import DataRequired, Email, Optional
from wtforms.widgets import PasswordInput
from docassemble.base.functions import LazyWord as word, LazyArray
from docassemble.base.config import daconfig
from docassemble.base.generate_key import random_alphanumeric
from docassemble.base.logger import logmessage
from docassemble.webapp.daredis import r
from docassemble.webapp.db_object import db
from docassemble.webapp.users.models import UserModel, Role
from flask import flash, current_app, request, abort
from flask_login import current_user
from sqlalchemy import select
try:
    import ldap
except ImportError:
    if 'ldap login' not in daconfig:
        daconfig['ldap login'] = {}
    daconfig['ldap login']['enable'] = False

HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)
BAN_IP_ADDRESSES = daconfig.get('ip address ban enabled', True)


def get_requester_ip(req):
    if not req:
        return '127.0.0.1'
    if HTTP_TO_HTTPS:
        if 'X-Real-Ip' in req.headers:
            return req.headers['X-Real-Ip']
        if 'X-Forwarded-For' in req.headers:
            return req.headers['X-Forwarded-For']
    return req.remote_addr


def fix_nickname(form, field):
    field.data = str(form.first_name.data) + ' ' + str(form.last_name.data)


class MySignInForm(LoginForm):

    def validate(self):
        if BAN_IP_ADDRESSES:
            key = 'da:failedlogin:ip:' + str(get_requester_ip(request))
            failed_attempts = r.get(key)
            if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
                abort(404)
        if daconfig['ldap login'].get('enable', False):
            ldap_server = daconfig['ldap login'].get('server', 'localhost').strip()
            username = self.email.data
            password = self.password.data
            connect = ldap.initialize('ldap://' + ldap_server)
            connect.set_option(ldap.OPT_REFERRALS, 0)
            try:
                connect.simple_bind_s(username, password)
                if connect.whoami_s() is not None:
                    connect.unbind_s()
                    user_manager = current_app.user_manager
                    user, user_email = user_manager.find_user_by_email(self.email.data)  # pylint: disable=unused-variable
                    if not user:
                        while True:
                            new_social = 'ldap$' + random_alphanumeric(32)
                            existing_user = db.session.execute(select(UserModel).filter_by(social_id=new_social)).scalar()
                            if existing_user:
                                continue
                            break
                        user = UserModel(social_id=new_social, email=self.email.data, nickname='', active=True)
                        user_role = db.session.execute(select(Role).filter_by(name='user')).scalar_one()
                        user.roles.append(user_role)
                        db.session.add(user)
                        db.session.commit()
                    result = True
                else:
                    connect.unbind_s()
                    result = super().validate()
            except (ldap.LDAPError, ldap.INVALID_CREDENTIALS):
                connect.unbind_s()
                result = super().validate()
        else:
            user_manager = current_app.user_manager
            user, user_email = user_manager.find_user_by_email(self.email.data)
            if user is None:
                if daconfig.get('confirm registration', False):
                    self.email.errors = []
                    self.email.errors.append(word("Incorrect Email and/or Password"))
                    self.password.errors = []
                    self.password.errors.append(word("Incorrect Email and/or Password"))
                else:
                    self.email.errors = list(self.email.errors)
                    self.email.errors.append(word("Account did not exist."))
                return False
            if user and (user.password is None or (user.social_id is not None and not user.social_id.startswith('local$'))):
                self.email.errors = list(self.email.errors)
                if user.social_id.startswith('google$'):
                    self.email.errors.append(word("You need to log in with Google."))
                elif user.social_id.startswith('azure$'):
                    self.email.errors.append(word("You need to log in with Azure."))
                elif user.social_id.startswith('auth0$'):
                    self.email.errors.append(word("You need to log in with Auth0."))
                elif user.social_id.startswith('twitter$'):
                    self.email.errors.append(word("You need to log in with Twitter."))
                elif user.social_id.startswith('facebook$'):
                    self.email.errors.append(word("You need to log in with Facebook."))
                else:
                    self.email.errors.append(word("You cannot log in this way."))
                return False
            # logmessage("Trying super validate")
            result = super().validate()
            # logmessage("Super validate response was " + repr(result))
        if result is False:
            r.incr(key)
            r.expire(key, daconfig['ban period'])
        elif failed_attempts is not None:
            r.delete(key)
        return result


def da_unique_email_validator(form, field):
    if daconfig['ldap login'].get('enable', False) and daconfig['ldap login'].get('base dn', None) is not None and daconfig['ldap login'].get('bind email', None) is not None and daconfig['ldap login'].get('bind password', None) is not None:
        ldap_server = daconfig['ldap login'].get('server', 'localhost').strip()
        base_dn = daconfig['ldap login']['base dn'].strip()
        search_filter = daconfig['ldap login'].get('search pattern', "mail=%s") % (form.email.data,)
        connect = ldap.initialize('ldap://' + ldap_server)
        try:
            connect.simple_bind_s(daconfig['ldap login']['bind email'], daconfig['ldap login']['bind password'])
            if len(connect.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)) > 0:
                raise ValidationError(word("This Email is already in use. Please try another one."))
        except ldap.LDAPError:
            pass
    if daconfig.get('confirm registration', False):
        return True
    return unique_email_validator(form, field)


def da_registration_restrict_validator(form, field):  # pylint: disable=unused-argument
    if len(daconfig['authorized registration domains']) == 0:
        return True
    user_email = str(form.email.data).lower().strip()
    for domain in daconfig['authorized registration domains']:
        if user_email.endswith(domain):
            return True
    errors = list(form.email.errors)
    errors.append(word('E-mail addresses with this domain are not authorized to register for accounts on this system.'))
    form.email.errors = tuple(errors)
    return False


class MyRegisterForm(RegisterForm):
    first_name = StringField(word('First name'), [validators.Length(min=0, max=255)])
    last_name = StringField(word('Last name'), [validators.Length(min=0, max=255)])
    country = StringField(word('Country code'), [validators.Length(min=0, max=2)])
    subdivisionfirst = StringField(word('First subdivision'), [validators.Length(min=0, max=64)])
    subdivisionsecond = StringField(word('Second subdivision'), [validators.Length(min=0, max=64)])
    subdivisionthird = StringField(word('Third subdivision'), [validators.Length(min=0, max=64)])
    organization = StringField(word('Organization'), [validators.Length(min=0, max=64)])
    language = StringField(word('Language'), [validators.Length(min=0, max=64)])
    timezone = SelectField(word('Time Zone'), [validators.Length(min=0, max=64)])
    nickname = StringField(word('Nickname'), [fix_nickname])
    email = StringField(word('Email'), validators=[
        validators.DataRequired(word('Email is required')),
        validators.Email(word('Invalid Email')),
        da_unique_email_validator,
        da_registration_restrict_validator])


def length_two(form, field):  # pylint: disable=unused-argument
    if len(field.data) != 2:
        raise ValidationError(word('Must be a two-letter code'))


class NewPrivilegeForm(FlaskForm):
    name = StringField(word('Name of new privilege'), validators=[
        DataRequired(word('Name of new privilege is required'))])
    submit = SubmitField(word('Add'))


class UserProfileForm(FlaskForm):
    first_name = StringField(word('First name'), [validators.Length(min=0, max=255)])
    last_name = StringField(word('Last name'), [validators.Length(min=0, max=255)])
    country = StringField(word('Country code'), [validators.Length(min=0, max=2)])
    subdivisionfirst = StringField(word('First subdivision'), [validators.Length(min=0, max=64)])
    subdivisionsecond = StringField(word('Second subdivision'), [validators.Length(min=0, max=64)])
    subdivisionthird = StringField(word('Third subdivision'), [validators.Length(min=0, max=64)])
    organization = StringField(word('Organization'), [validators.Length(min=0, max=64)])
    language = StringField(word('Language'), [validators.Length(min=0, max=64)])
    timezone = SelectField(word('Time Zone'), [validators.Length(min=0, max=64)])
    pypi_username = StringField(word('PyPI Username'), [validators.Length(min=0, max=255)])
    pypi_password = StringField(word('PyPI Password'), [validators.Length(min=0, max=255)])
    confirmed_at = DateField(word('Confirmation Date'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))


class EditUserProfileForm(UserProfileForm):
    email = StringField(word('E-mail'), validators=[Email(word('Must be a valid e-mail address')), DataRequired(word('E-mail is required'))])
    role_id = SelectMultipleField(word('Privileges'), coerce=int)
    active = BooleanField(word('Active'))
    uses_mfa = BooleanField(word('Uses two-factor authentication'))

    def validate(self, user_id, admin_id):  # pylint: disable=arguments-differ
        user_manager = current_app.user_manager
        rv = UserProfileForm.validate(self)
        if not rv:
            return False
        user, user_email = user_manager.find_user_by_email(self.email.data)  # pylint: disable=unused-variable
        if user is not None and user.id != user_id:
            self.email.errors.append(word('That e-mail address is already taken.'))
            return False
        if current_user.id == user_id and current_user.has_roles('admin'):
            if admin_id not in self.role_id.data:
                self.role_id.errors.append(word('You cannot take away your own admin privilege.'))
                return False
            self.active.data = True
        return True


class PhoneUserProfileForm(UserProfileForm):

    def validate(self):  # pylint: disable=arguments-differ
        if self.email.data:
            if current_user.social_id.startswith('phone$'):
                existing_user = db.session.execute(select(UserModel).filter_by(email=self.email.data, active=True)).scalar()
                if existing_user is not None and existing_user.id != current_user.id:
                    flash(word("Please choose a different e-mail address."), 'error')
                    return False
        return super().validate()
    email = StringField(word('E-mail'), validators=[Optional(), Email(word('Must be a valid e-mail address'))])


class RequestDeveloperForm(FlaskForm):
    reason = StringField(word('Reason for needing developer account (optional)'))
    submit = SubmitField(word('Submit'))


class MyInviteForm(FlaskForm):

    def validate(self):  # pylint: disable=arguments-differ
        has_error = False
        if self.email.data:
            for email_address in re.split(r'[\n\r]+', self.email.data.strip()):
                (part_one, part_two) = email.utils.parseaddr(email_address)  # pylint: disable=unused-variable
                if part_two == '':
                    the_errors = list(self.email.errors)
                    the_errors.append(word("Invalid e-mail address: " + email_address))
                    self.email.errors = tuple(the_errors)
                    has_error = True
        if has_error:
            return False
        return super().validate()
    email = TextAreaField(word('One or more e-mail addresses (separated by newlines)'), validators=[
        validators.InputRequired(word('At least one e-mail address must be listed'))
    ])
    role_id = SelectField(word('Role'))
    next = HiddenField()
    submit = SubmitField(word('Invite'))


class UserAddForm(FlaskForm):
    email = StringField(word('E-mail'), validators=[
        validators.InputRequired(word('E-mail is required')),
        validators.Email(word('Invalid E-mail'))])
    first_name = StringField(word('First name'), [validators.Length(min=0, max=255)])
    last_name = StringField(word('Last name'), [validators.Length(min=0, max=255)])
    role_id = SelectMultipleField(word('Privileges'), coerce=int)
    password = StringField(word('Password'), widget=PasswordInput(hide_value=False), validators=[password_validator])
    submit = SubmitField(word('Add'))


class PhoneLoginForm(FlaskForm):
    phone_number = StringField(word('Phone number'), [validators.Length(min=5, max=255)])
    submit = SubmitField(word('Go'))


class PhoneLoginVerifyForm(FlaskForm):
    phone_number = StringField(word('Phone number'), [validators.Length(min=5, max=255)])
    verification_code = StringField(word('Verification code'), [validators.Length(min=daconfig['verification code digits'], max=daconfig['verification code digits'])])
    submit = SubmitField(word('Verify'))

    def validate(self):  # pylint: disable=arguments-differ
        result = True
        if BAN_IP_ADDRESSES:
            key = 'da:failedlogin:ip:' + str(get_requester_ip(request))
            failed_attempts = r.get(key)
            if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
                abort(404)
        verification_key = 'da:phonelogin:' + str(self.phone_number.data) + ':code'
        verification_code = r.get(verification_key)
        # r.delete(verification_key)
        supplied_verification_code = re.sub(r'[^0-9]', '', self.verification_code.data)
        logmessage("Supplied code is " + str(supplied_verification_code))
        if verification_code is None:
            logmessage("Verification code with " + str(verification_key) + " is None")
            result = False
        elif verification_code.decode() != supplied_verification_code:
            logmessage("Verification code with " + str(verification_key) + " which is " + str(verification_code.decode()) + " does not match supplied code, which is " + str(self.verification_code.data))
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


class MyResendConfirmEmailForm(FlaskForm):
    email = StringField(word('Your e-mail address'), validators=[
        validators.DataRequired(word('E-mail address is required')),
        validators.Email(word('Invalid e-mail address')),
        ])
    submit = SubmitField(word('Send confirmation email'))


class ManageAccountForm(FlaskForm):
    confirm = StringField(word('Type \"delete my account\" here to confirm that you want to delete your account.'), [validators.AnyOf(LazyArray([word("delete my account")]), message=word('Since you did not type \"delete my account\" I did not delete your account.'))])
    delete = SubmitField(word('Delete Account'))


class InterviewsListForm(FlaskForm):
    i = StringField()
    session = StringField()
    tags = StringField()
    delete = SubmitField()
    delete_all = SubmitField()
