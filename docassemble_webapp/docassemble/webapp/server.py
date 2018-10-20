min_system_version = '0.2.36'
import re
re._MAXCACHE = 10000
import os
import sys
import tempfile
import ruamel.yaml
import tarfile
from textstat.textstat import textstat
import docassemble.base.config
if not docassemble.base.config.loaded:
    docassemble.base.config.load()
import docassemble.base.functions
from urllib import unquote
from docassemble.base.config import daconfig, hostname, in_celery

DEBUG = daconfig.get('debug', False)
if DEBUG:
    PREVENT_DEMO = False
elif daconfig.get('allow demo', False):
    PREVENT_DEMO = False
else:
    PREVENT_DEMO = True

PACKAGE_PROTECTION = daconfig.get('package protection', True)
    
HTTP_TO_HTTPS = daconfig.get('behind https load balancer', False)
request_active = True

default_playground_yaml = """metadata:
  title: Default playground interview
  short title: Test
  comment: This is a learning tool.  Feel free to write over it.
---
include:
  - basic-questions.yml
---
mandatory: True
question: |
  Here is your document, ${ client }.
subquestion: |
  In order ${ quest }, you will need this.
attachments:
  - name: Information Sheet
    filename: info_sheet
    content: |
      Your name is ${ client }.
      
      % if user.age_in_years() > 60:
      You are a senior.
      % endif
      Your quest is ${ quest }.  You
      are eligible for ${ benefits }.
---
question: |
  What is your quest?
fields:
  - Your quest: quest
    hint: to find the Loch Ness Monster
---
code: |
  if user.age_in_years() < 18:
    benefits = "CHIP"
  else:
    benefits = "Medicaid"
"""

ok_mimetypes = {"application/javascript": "javascript", "text/x-python": "python", "application/json": "json", "text/css": "css", 'text/html': 'htmlmixed'}
ok_extensions = {"yml": "yaml", "yaml": "yaml", "md": "markdown", "markdown": "markdown", 'py': "python", "json": "json", "css": "css", "html": "htmlmixed"}

default_yaml_filename = daconfig.get('default interview', None)
final_default_yaml_filename = daconfig.get('default interview', 'docassemble.demo:data/questions/default-interview.yml')
keymap = daconfig.get('keymap', None)
google_config = daconfig.get('google', dict())

detect_mobile = re.compile('Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|NetFront|Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|Dolfin|Dolphin|Skyfire|Zune')
alphanumeric_only = re.compile('[\W_]+')
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")
document_match = re.compile(r'^--- *$', flags=re.MULTILINE)
fix_tabs = re.compile(r'\t')
fix_initial = re.compile(r'^---\n')
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
extraneous_var = re.compile(r'^x\.|^x\[')
key_requires_preassembly = re.compile('^(x\.|x\[|_multiple_choice|.*\[[ijklmn]\])')
match_invalid = re.compile('[^A-Za-z0-9_\[\].\'\%\-=]')
match_invalid_key = re.compile('[^A-Za-z0-9_\[\].\'\%\- =]')
match_brackets = re.compile('\[\'.*\'\]$')
match_inside_and_outside_brackets = re.compile('(.*)(\[u?\'[^\]]+\'\])$')
match_inside_brackets = re.compile('\[u?\'([^\]]+)\'\]')
valid_python_var = re.compile(r'[A-Za-z][A-Za-z0-9\_]+')

default_title = daconfig.get('default title', daconfig.get('brandname', 'docassemble'))
default_short_title = daconfig.get('default short title', default_title)
os.environ['PYTHON_EGG_CACHE'] = tempfile.gettempdir()
PNG_RESOLUTION = daconfig.get('png resolution', 300)
PNG_SCREEN_RESOLUTION = daconfig.get('png screen resolution', 72)
PDFTOPPM_COMMAND = daconfig.get('pdftoppm', 'pdftoppm')
DEFAULT_LANGUAGE = daconfig.get('language', 'en')
DEFAULT_LOCALE = daconfig.get('locale', 'en_US.utf8')
DEFAULT_DIALECT = daconfig.get('dialect', 'us')
LOGSERVER = daconfig.get('log server', None)
CHECKIN_INTERVAL = int(daconfig.get('checkin interval', 6000))
#message_sequence = dbtableprefix + 'message_id_seq'

if os.environ.get('SUPERVISOR_SERVER_URL', None):
    USING_SUPERVISOR = True
    #sys.stderr.write("Using supervisor and hostname is " + str(hostname) + "\n")
else:
    USING_SUPERVISOR = False
    #sys.stderr.write("Not using supervisor and hostname is " + str(hostname) + "\n")

audio_mimetype_table = {'mp3': 'audio/mpeg', 'ogg': 'audio/ogg'}

valid_voicerss_languages = {
    'ca': ['es'],
    'zh': ['cn', 'hk', 'tw'],
    'da': ['dk'],
    'nl': ['nl'],
    'en': ['au', 'ca', 'gb', 'in', 'us'],
    'fi': ['fi'],
    'fr': ['ca, fr'],
    'de': ['de'],
    'it': ['it'],
    'ja': ['jp'],
    'ko': ['kr'],
    'nb': ['no'],
    'pl': ['pl'],
    'pt': ['br', 'pt'],
    'ru': ['ru'],
    'es': ['mx', 'es'],
    'sv': ['se']
    }

voicerss_config = daconfig.get('voicerss', None)
if not voicerss_config or ('enable' in voicerss_config and not voicerss_config['enable']) or not ('key' in voicerss_config and voicerss_config['key']):
    VOICERSS_ENABLED = False
else:
    VOICERSS_ENABLED = True
ROOT = daconfig.get('root', '/')
#app.logger.warning("default sender is " + current_app.config['MAIL_DEFAULT_SENDER'] + "\n")
exit_page = daconfig.get('exitpage', 'https://docassemble.org')

SUPERVISORCTL = daconfig.get('supervisorctl', 'supervisorctl')
#PACKAGE_CACHE = daconfig.get('packagecache', '/var/www/.cache')
WEBAPP_PATH = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local')
UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')
FULL_PACKAGE_DIRECTORY = os.path.join(PACKAGE_DIRECTORY, 'lib', 'python2.7', 'site-packages')
LOG_DIRECTORY = daconfig.get('log', '/usr/share/docassemble/log')
#PLAYGROUND_MODULES_DIRECTORY = daconfig.get('playground_modules', )

init_py_file = """try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)
"""
    
#if not os.path.isfile(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py')):
#    with open(os.path.join(PLAYGROUND_MODULES_DIRECTORY, 'docassemble', '__init__.py'), 'a') as the_file:
#        the_file.write(init_py_file)

#USE_PROGRESS_BAR = daconfig.get('use_progress_bar', True)
SHOW_LOGIN = daconfig.get('show login', True)
ALLOW_REGISTRATION = daconfig.get('allow registration', True)
#USER_PACKAGES = daconfig.get('user_packages', '/var/lib/docassemble/dist-packages')
#sys.path.append(USER_PACKAGES)
#if USE_PROGRESS_BAR:

if in_celery:
    LOGFILE = daconfig.get('celery flask log', '/tmp/celery-flask.log')
else:
    LOGFILE = daconfig.get('flask log', '/tmp/flask.log')
#APACHE_LOGFILE = daconfig.get('apache_log', '/var/log/apache2/error.log')

#connect_string = docassemble.webapp.database.connection_string()
#alchemy_connect_string = docassemble.webapp.database.alchemy_connection_string()

def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property

def _endpoint_url(endpoint):
    url = '/'
    if endpoint:
        url = url_for(endpoint)
    return url

def _get_safe_next_param(param_name, default_endpoint):
    if param_name in request.args:
        #safe_next = current_app.user_manager.make_safe_url_function(unquote(request.args[param_name]))
        safe_next = request.args[param_name]
    else:
        safe_next = _endpoint_url(default_endpoint)
    return safe_next

# def _do_login_user(user, safe_next, remember_me=False):
#     if not user: return unauthenticated()

#     if not _call_or_get(user.is_active):
#         flash(word('Your account has not been enabled.'), 'error')
#         return redirect(url_for('user.login'))

#     user_manager = current_app.user_manager
#     if user_manager.enable_email and user_manager.enable_confirm_email \
#             and not current_app.user_manager.enable_login_without_confirm_email \
#             and not user.has_confirmed_email():
#         url = url_for('user.resend_confirm_email')
#         flash(flask_user.translations.gettext('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="%(url)s">Re-send confirmation email</a>.', url=url), 'error')
#         return redirect(url_for('user.login'))

#     login_user(user, remember=remember_me)

#     signals.user_logged_in.send(current_app._get_current_object(), user=user)

#     flash(word('You have signed in successfully.'), 'success')

#     return redirect(safe_next)

def custom_resend_confirm_email():
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter
    form = user_manager.resend_confirm_email_form(request.form)
    if request.method=='GET' and 'email' in request.args:
        form.email.data = request.args['email']
    if request.method=='POST' and form.validate():
        email = form.email.data
        user, user_email = user_manager.find_user_by_email(email)
        if user:
            flask_user.views._send_confirm_email(user, user_email)
        return redirect(flask_user.views._endpoint_url(user_manager.after_resend_confirm_email_endpoint))
    return user_manager.render_function(user_manager.resend_confirm_email_template, form=form)

def custom_register():
    """ Display registration form and create new User."""
    if ('json' in request.form and int(request.form['json'])) or ('json' in request.args and int(request.args['json'])):
        is_json = True
    else:
        is_json = False
        
    user_manager =  current_app.user_manager
    db_adapter = user_manager.db_adapter

    safe_next = _get_safe_next_param('next', user_manager.after_login_endpoint)
    safe_reg_next = _get_safe_next_param('reg_next', user_manager.after_register_endpoint)

    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        return add_secret_to(redirect(safe_next))

    # Initialize form
    login_form = user_manager.login_form()                      # for login_or_register.html
    register_form = user_manager.register_form(request.form)    # for register.html

    # invite token used to determine validity of registeree
    invite_token = request.values.get("token")

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
        login_form.next.data     = register_form.next.data     = safe_next
        login_form.reg_next.data = register_form.reg_next.data = safe_reg_next
        if user_invite:
            register_form.email.data = user_invite.email

    # Process valid POST
    if request.method == 'POST' and register_form.validate():
        # Create a User object using Form fields that have a corresponding User field
        User = db_adapter.UserClass
        user_class_fields = User.__dict__
        user_fields = {}

        # Create a UserEmail object using Form fields that have a corresponding UserEmail field
        if db_adapter.UserEmailClass:
            UserEmail = db_adapter.UserEmailClass
            user_email_class_fields = UserEmail.__dict__
            user_email_fields = {}

        # Create a UserAuth object using Form fields that have a corresponding UserAuth field
        if db_adapter.UserAuthClass:
            UserAuth = db_adapter.UserAuthClass
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

        # Add User record using named arguments 'user_fields'
        user = db_adapter.add_object(User, **user_fields)
        if db_adapter.UserProfileClass:
            user_profile = user

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
                db_adapter.update_object(user, confirmed_at=datetime.datetime.utcnow())

        db_adapter.commit()

        # Send 'registered' email and delete new User object if send fails
        if user_manager.send_registered_email:
            try:
                # Send 'registered' email
                flask_user.views._send_registered_email(user, user_email, require_email_confirmation)
            except Exception as e:
                # delete new User object if send fails
                db_adapter.delete_object(user)
                db_adapter.commit()
                raise

        # Send user_registered signal
        flask_user.signals.user_registered.send(current_app._get_current_object(),
                                                user=user,
                                                user_invite=user_invite)

        # Redirect if USER_ENABLE_CONFIRM_EMAIL is set
        if user_manager.enable_confirm_email and require_email_confirmation:
            safe_reg_next = user_manager.make_safe_url_function(register_form.reg_next.data)
            return redirect(safe_reg_next)

        # Auto-login after register or redirect to login page
        if 'reg_next' in request.args:
            safe_reg_next = user_manager.make_safe_url_function(register_form.reg_next.data)
        else:
            safe_reg_next = _endpoint_url(user_manager.after_confirm_endpoint)
        if user_manager.auto_login_after_register:
            return flask_user.views._do_login_user(user, safe_reg_next)
        else:
            return redirect(url_for('user.login') + '?next=' + urllib.quote(safe_reg_next))

    # Process GET or invalid POST
    if is_json:
        return jsonify(action='register', csrf_token=generate_csrf())
    return user_manager.render_function(user_manager.register_template,
            form=register_form,
            login_form=login_form,
            register_form=register_form)

def custom_login():
    """ Prompt for username/email and password and sign the user in."""
    if ('json' in request.form and int(request.form['json'])) or ('json' in request.args and int(request.args['json'])):
        is_json = True
    else:
        is_json = False
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter

    safe_next = _get_safe_next_param('next', user_manager.after_login_endpoint)
    safe_reg_next = _get_safe_next_param('reg_next', user_manager.after_register_endpoint)

    if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
        return add_secret_to(redirect(safe_next))

    login_form = user_manager.login_form(request.form)
    register_form = user_manager.register_form()
    if request.method != 'POST':
        login_form.next.data     = register_form.next.data     = safe_next
        login_form.reg_next.data = register_form.reg_next.data = safe_reg_next

    if request.method=='POST' and login_form.validate():
        user = None
        user_email = None
        if user_manager.enable_username:
            user = user_manager.find_user_by_username(login_form.username.data)
            user_email = None
            if user and db_adapter.UserEmailClass:
                user_email = db_adapter.find_first_object(db_adapter.UserEmailClass,
                        user_id=int(user.get_id()),
                        is_primary=True,
                        )
            if not user and user_manager.enable_email:
                user, user_email = user_manager.find_user_by_email(login_form.username.data)
        else:
            user, user_email = user_manager.find_user_by_email(login_form.email.data)
        #if not user and daconfig['ldap login'].get('enabled', False):
        if user:
            safe_next = user_manager.make_safe_url_function(login_form.next.data)
            safe_next = login_form.next.data
            #safe_next = url_for('post_login', next=login_form.next.data)
            if daconfig.get('two factor authentication', False) is True and user.otp_secret is not None:
                session['validated_user'] = user.id
                if user.otp_secret.startswith(':phone:'):
                    phone_number = re.sub(r'^:phone:', '', user.otp_secret)
                    verification_code = random_digits(daconfig['verification code digits'])
                    message = word("Your verification code is") + " " + str(verification_code) + "."
                    key = 'da:mfa:phone:' + str(phone_number) + ':code'
                    pipe = r.pipeline()
                    pipe.set(key, verification_code)
                    pipe.expire(key, daconfig['verification code timeout'])
                    pipe.execute()
                    success = docassemble.base.util.send_sms(to=phone_number, body=message)
                    if not success:
                        flash(word("Unable to send verification code."), 'error')
                        return add_secret_to(redirect(url_for('user.login')))
                return add_secret_to(redirect(url_for('mfa_login', next=safe_next)))
            if user_manager.enable_email and user_manager.enable_confirm_email \
               and len(daconfig['email confirmation privileges']) \
               and user.has_role(*daconfig['email confirmation privileges']) \
               and not user.has_confirmed_email():
                url = url_for('user.resend_confirm_email', email=user.email)
                flash(word('You cannot log in until your e-mail address has been confirmed.') + '<br><a href="' + url + '">' + word('Click here to confirm your e-mail') + '</a>.', 'error')
                return add_secret_to(redirect(url_for('user.login')))
            return add_secret_to(flask_user.views._do_login_user(user, safe_next, login_form.remember_me.data))
    if is_json:
        return jsonify(action='login', csrf_token=generate_csrf())
    # if 'officeaddin' in safe_next:
    #     extra_css = """
    # <script type="text/javascript" src="https://appsforoffice.microsoft.com/lib/1.1/hosted/office.debug.js"></script>"""
    #     extra_js = """
    # <script type="text/javascript" src=""" + '"' + url_for('static', filename='office/fabric.js') + '"' + """></script>
    # <script type="text/javascript" src=""" + '"' + url_for('static', filename='office/polyfill.js') + '"' + """></script>
    # <script type="text/javascript" src=""" + '"' + url_for('static', filename='office/app.js') + '"' + """></script>"""
    #     return render_template(user_manager.login_template,
    #                            form=login_form,
    #                            login_form=login_form,
    #                            register_form=register_form,
    #                            extra_css=Markup(extra_css),
    #                            extra_js=Markup(extra_js))
    # else:
    return user_manager.render_function(user_manager.login_template,
                                        form=login_form,
                                        login_form=login_form,
                                        register_form=register_form)

def add_secret_to(response):
    if 'newsecret' in session:
        response.set_cookie('secret', session['newsecret'])
        del session['newsecret']
    return response

def logout():
    # secret = request.cookies.get('secret', None)
    # if secret is None:
    #     secret = random_string(16)
    #     set_cookie = True
    # else:
    #     secret = str(secret)
    #     set_cookie = False
    user_manager = current_app.user_manager
    next = request.args.get('next', _endpoint_url(user_manager.after_logout_endpoint))
    if current_user.is_authenticated and current_user.social_id.startswith('auth0$') and 'oauth' in daconfig and 'auth0' in daconfig['oauth'] and 'domain' in daconfig['oauth']['auth0']:
        if next.startswith('/'):
            next = docassemble.base.functions.get_url_root() + next
        next = 'https://' + daconfig['oauth']['auth0']['domain'] + '/v2/logout?' + urllib.urlencode(dict(returnTo=next, client_id=daconfig['oauth']['auth0']['id']))
    set_cookie = False
    flask_user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
    logout_user()
    delete_session()
    flash(word('You have signed out successfully.'), 'success')
    response = redirect(next)
    if set_cookie:
        response.set_cookie('secret', secret)
    else:
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
#     next = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
#     reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))

#     if _call_or_get(current_user.is_authenticated) and user_manager.auto_login_at_login:
#         return redirect(next)

#     login_form = user_manager.login_form(request.form)
#     register_form = user_manager.register_form()
#     if request.method != 'POST':
#         login_form.next.data     = register_form.next.data = next
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
    return redirect(url_for('interview_list', next=fix_http(request.url)))

def my_default_url(error, endpoint, values):
    return url_for('index')

def make_safe_url(url):
    parts = urlparse.urlsplit(url)
    safe_url = parts.path
    if parts.query != '':
        safe_url += '?' + parts.query
    if parts.fragment != '':
        safe_url += '#' + parts.fragment
    return safe_url

def password_validator(form, field):
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

    rules = daconfig.get('password complexity', dict())
    is_valid = password_length >= rules.get('length', 6) and lowers >= rules.get('lowercase', 1) and uppers >= rules.get('uppercase', 1) and digits >= rules.get('digits', 1) and punct >= rules.get('punctuation', 0)
    if not is_valid:
        import wtforms
        if 'error message' in rules:
            error_message = unicode(rules['error message'])
        else:
            error_message = 'Password must be at least ' + docassemble.base.functions.quantity_noun(rules.get('length', 6), 'character') + ' long'
            standards = list()
            if rules.get('lowercase', 1) > 0:
                standards.append('at least ' + docassemble.base.functions.quantity_noun(rules.get('lowercase', 1), 'lowercase letter'))
            if rules.get('uppercase', 1) > 0:
                standards.append('at least ' + docassemble.base.functions.quantity_noun(rules.get('uppercase', 1), 'uppercase letter'))
            if rules.get('digits', 1) > 0:
                standards.append('at least ' + docassemble.base.functions.quantity_noun(rules.get('digits', 1), 'number'))
            if rules.get('punctuation', 0) > 0:
                standards.append('at least ' + docassemble.base.functions.quantity_noun(rules.get('punctuation', 1), 'punctuation character'))
            if len(standards):
                error_message += ' with ' + docassemble.base.functions.comma_and_list(standards)
            error_message += '.'
        raise wtforms.ValidationError(word(error_message))

import docassemble.webapp.setup
from docassemble.webapp.app_object import app, csrf, flaskbabel
from docassemble.webapp.db_object import db
from docassemble.webapp.users.forms import MyRegisterForm, MyInviteForm, MySignInForm, PhoneLoginForm, PhoneLoginVerifyForm, MFASetupForm, MFAReconfigureForm, MFALoginForm, MFAChooseForm, MFASMSSetupForm, MFAVerifySMSSetupForm, MyResendConfirmEmailForm
from docassemble.webapp.users.models import UserModel, UserAuthModel, MyUserInvitation, Role
from flask_user import UserManager, SQLAlchemyAdapter
db_adapter = SQLAlchemyAdapter(db, UserModel, UserAuthClass=UserAuthModel, UserInvitationClass=MyUserInvitation)
from docassemble.webapp.users.views import user_profile_page
user_manager = UserManager()
user_manager.init_app(app, db_adapter=db_adapter, login_form=MySignInForm, register_form=MyRegisterForm, user_profile_view_function=user_profile_page, logout_view_function=logout, unauthorized_view_function=unauthorized, unauthenticated_view_function=unauthenticated, login_view_function=custom_login, register_view_function=custom_register, resend_confirm_email_view_function=custom_resend_confirm_email, resend_confirm_email_form=MyResendConfirmEmailForm, password_validator=password_validator)
from flask_login import LoginManager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'custom_login'

from twilio.rest import Client as TwilioRestClient
import twilio.twiml
import twilio.twiml.messaging_response
import twilio.twiml.voice_response
from PIL import Image
import socket
import copy
import threading
import urllib
import urllib2
import tailer
import datetime
from dateutil import tz
import dateutil
import dateutil.parser
import time
#import pip.utils.logging
#import pip
import shutil
import filecmp
import codecs
import weakref
import types
import stat
import pkg_resources
import babel.dates
import pytz
import httplib2
import zipfile
import operator
import traceback
from Crypto.Hash import MD5
import mimetypes
import logging
import cPickle as pickle
import cgi
import Cookie
import urlparse
import json
import base64
import requests
#import redis
import yaml
import inspect
import pyotp
import qrcode
import qrcode.image.svg
import StringIO
import links_from_header
from distutils.version import LooseVersion
from subprocess import call, Popen, PIPE
import subprocess
from pygments import highlight
from pygments.lexers import YamlLexer, PythonLexer
from pygments.formatters import HtmlFormatter
from flask import make_response, abort, render_template, render_template_string, request, session, send_file, redirect, current_app, get_flashed_messages, flash, Markup, jsonify, Response, g
from flask import url_for
from flask_login import login_user, logout_user, current_user
from flask_user import login_required, roles_required
from flask_user import signals, user_logged_in, user_changed_password, user_registered, user_reset_password
#from flask_wtf.csrf import generate_csrf
from docassemble.webapp.develop import CreatePackageForm, CreatePlaygroundPackageForm, UpdatePackageForm, ConfigForm, PlaygroundForm, PlaygroundUploadForm, LogForm, Utilities, PlaygroundFilesForm, PlaygroundFilesEditForm, PlaygroundPackagesForm, GoogleDriveForm, OneDriveForm, GitHubForm, PullPlaygroundPackage, TrainingForm, TrainingUploadForm, APIKey, AddinUploadForm
import flask_user.signals
import flask_user.translations
import flask_user.views
import werkzeug
from rauth import OAuth1Service, OAuth2Service
import apiclient
import oauth2client.client
import strict_rfc3339
import io
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from sqlalchemy import or_, and_
import docassemble.base.parse
import docassemble.base.pdftk
import docassemble.base.interview_cache
#import docassemble.webapp.update
from docassemble.base.standardformatter import as_html, as_sms, get_choices_with_abb, is_empty_mc
from docassemble.base.pandoc import word_to_markdown, convertible_mimetypes, convertible_extensions
from docassemble.webapp.screenreader import to_text
from docassemble.base.error import DAError, DAErrorNoEndpoint, DAErrorMissingVariable, DAErrorCompileError
from docassemble.base.functions import pickleable_objects, word, comma_and_list, get_default_timezone, ReturnValue
from docassemble.base.logger import logmessage
from docassemble.webapp.backend import cloud, initial_dict, can_access_file_number, get_info_from_file_number, da_send_mail, get_new_file_number, pad, unpad, encrypt_phrase, pack_phrase, decrypt_phrase, unpack_phrase, encrypt_dictionary, pack_dictionary, decrypt_dictionary, unpack_dictionary, nice_date_from_utc, fetch_user_dict, fetch_previous_user_dict, advance_progress, reset_user_dict, get_chat_log, save_numbered_file, generate_csrf, get_info_from_file_reference, reference_exists, write_ml_source, fix_ml_files, is_package_ml, user_dict_exists, file_set_attributes, url_if_exists, get_person, Message
from docassemble.webapp.core.models import Uploads, SpeakList, Supervisors, Shortener, Email, EmailAttachment, MachineLearning #Attachments
from docassemble.webapp.packages.models import Package, PackageAuth, Install
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype, make_package_zip
from docassemble.base.generate_key import random_string, random_lower_string, random_alphanumeric, random_digits
import docassemble.webapp.backend
import docassemble.base.util
from docassemble.base.util import DAEmail, DAEmailRecipientList, DAEmailRecipient, DAFileList, DAFile, DAObject, DAFileCollection, DAStaticFile, DADict
from user_agents import parse as ua_parse
import docassemble.base.ocr
from jinja2.exceptions import TemplateError
import uuid
from bs4 import BeautifulSoup

import importlib
modules_to_import = daconfig.get('preloaded modules', None)
if type(modules_to_import) is list:
    for module_name in daconfig['preloaded modules'] + ['docassemble.base.legal']:
        try:
            importlib.import_module(module_name)
        except:
            pass
        
mimetypes.add_type('application/x-yaml', '.yml')
mimetypes.add_type('application/x-yaml', '.yaml')

#docassemble.base.parse.debug = DEBUG
#docassemble.base.util.set_redis_server(redis_host)

from docassemble.webapp.daredis import r_store

store = RedisStore(r_store)
#store = RedisStore(redis.StrictRedis(host=docassemble.base.util.redis_server, db=1))

kv_session = KVSessionExtension(store, app)

if 'twilio' in daconfig:
    twilio_config = dict()
    twilio_config['account sid'] = dict()
    twilio_config['number'] = dict()
    twilio_config['name'] = dict()
    if type(daconfig['twilio']) is not list:
        config_list = [daconfig['twilio']]
    else:
        config_list = daconfig['twilio']
    for tconfig in config_list:
        if type(tconfig) is dict and 'account sid' in tconfig and 'number' in tconfig:
            twilio_config['account sid'][unicode(tconfig['account sid'])] = 1
            twilio_config['number'][unicode(tconfig['number'])] = tconfig
            if 'default' not in twilio_config['name']:
                twilio_config['name']['default'] = tconfig
            if 'name' in tconfig:
                twilio_config['name'][tconfig['name']] = tconfig
        else:
            logmessage("improper setup in twilio configuration")    
    if 'default' not in twilio_config['name']:
        twilio_config = None
else:
    twilio_config = None

app.debug = False
app.handle_url_build_error = my_default_url
app.config['USE_GOOGLE_LOGIN'] = False
app.config['USE_FACEBOOK_LOGIN'] = False
app.config['USE_TWITTER_LOGIN'] = False
app.config['USE_AUTH0_LOGIN'] = False
app.config['USE_AZURE_LOGIN'] = False
app.config['USE_GOOGLE_DRIVE'] = False
app.config['USE_ONEDRIVE'] = False
app.config['USE_PHONE_LOGIN'] = False
app.config['USE_GITHUB'] = False
if daconfig.get('password login', True) is False:
    app.config['USE_PASSWORD_LOGIN'] = False
else:
    app.config['USE_PASSWORD_LOGIN'] = True
if twilio_config is not None and daconfig.get('phone login', False) is True:
    app.config['USE_PHONE_LOGIN'] = True
if 'oauth' in daconfig:
    app.config['OAUTH_CREDENTIALS'] = daconfig['oauth']
    if 'google' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['google'] and daconfig['oauth']['google']['enable'] is False):
        app.config['USE_GOOGLE_LOGIN'] = True
    else:
        app.config['USE_GOOGLE_LOGIN'] = False
    if 'facebook' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['facebook'] and daconfig['oauth']['facebook']['enable'] is False):
        app.config['USE_FACEBOOK_LOGIN'] = True
    else:
        app.config['USE_FACEBOOK_LOGIN'] = False
    if 'twitter' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['twitter'] and daconfig['oauth']['twitter']['enable'] is False):
        app.config['USE_TWITTER_LOGIN'] = True
    else:
        app.config['USE_TWITTER_LOGIN'] = False
    if 'auth0' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['auth0'] and daconfig['oauth']['auth0']['enable'] is False):
        app.config['USE_AUTH0_LOGIN'] = True
    else:
        app.config['USE_AUTH0_LOGIN'] = False
    if 'azure' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['azure'] and daconfig['oauth']['azure']['enable'] is False):
        app.config['USE_AZURE_LOGIN'] = True
    else:
        app.config['USE_AZURE_LOGIN'] = False
    if 'googledrive' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['googledrive'] and daconfig['oauth']['googledrive']['enable'] is False):
        app.config['USE_GOOGLE_DRIVE'] = True
    else:
        app.config['USE_GOOGLE_DRIVE'] = False
    if 'onedrive' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['onedrive'] and daconfig['oauth']['onedrive']['enable'] is False):
        app.config['USE_ONEDRIVE'] = True
    else:
        app.config['USE_ONEDRIVE'] = False
    if 'github' in daconfig['oauth'] and not ('enable' in daconfig['oauth']['github'] and daconfig['oauth']['github']['enable'] is False):
        app.config['USE_GITHUB'] = True
    else:
        app.config['USE_GITHUB'] = False
else:
    app.config['OAUTH_CREDENTIALS'] = dict()
    
if daconfig.get('button size', 'medium') == 'medium':
    app.config['BUTTON_CLASS'] = 'btn-da'
elif daconfig.get('button size', 'medium') == 'large':
    app.config['BUTTON_CLASS'] = 'btn-lg btn-da'
elif daconfig.get('button size', 'medium') == 'small':
    app.config['BUTTON_CLASS'] = 'btn-sm btn-da'
else:
    app.config['BUTTON_CLASS'] = 'btn-da'

page_parts = dict()
for page_key in ('login page', 'register page', 'interview page', 'start page', 'profile page', 'reset password page', 'forgot password page', 'change password page', '404 page'):
    for part_key in ('title', 'tab title', 'extra css', 'extra javascript', 'heading', 'pre', 'submit', 'post'):
        key = page_key + ' ' + part_key
        if key in daconfig:
            if type(daconfig[key]) is dict:
                page_parts[key] = dict()
                for lang, val in daconfig[key].iteritems():
                    page_parts[key][lang] = Markup(val)
            else:
                page_parts[key] = {'*': Markup(unicode(daconfig[key]))}

main_page_parts = dict()
lang_list = set()
for key in ('main page pre', 'main page submit', 'main page post'):
    if key in daconfig and type(daconfig[key]) is dict:
        for lang in daconfig[key]:
            lang_list.add(lang)
lang_list.add(DEFAULT_LANGUAGE)
lang_list.add('*')
for lang in lang_list:
    main_page_parts[lang] = dict()
for key in ('main page pre', 'main page submit', 'main page post'):
    for lang in lang_list:
        if key in daconfig:
            if type(daconfig[key]) is dict:
                main_page_parts[lang][key] = daconfig[key].get(lang, daconfig[key].get('*', ''))
            else:
                main_page_parts[lang][key] = daconfig[key]
        else:
            main_page_parts[lang][key] = ''
del lang_list

def get_sms_session(phone_number, config='default'):
    sess_info = None
    if twilio_config is None:
        raise DAError("get_sms_session: Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
    if phone_number is None:
        raise DAError("terminate_sms_session: phone_number " + str(phone_number) + " is invalid")
    sess_contents = r.get('da:sms:client:' + phone_number + ':server:' + tconfig['number'])
    if sess_contents is not None:
        try:        
            sess_info = pickle.loads(sess_contents)
        except:
            logmessage("get_sms_session: unable to decode session information")
    sess_info['email'] = None
    if 'user_id' in sess_info and sess_info['user_id'] is not None:
        user = load_user(sess_info['user_id'])
        if user is not None:
            sess_info['email'] = user.email
    return sess_info

def initiate_sms_session(phone_number, yaml_filename=None, uid=None, secret=None, encrypted=None, user_id=None, email=None, new=False, config='default'):
    phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
    if phone_number is None:
        raise DAError("initiate_sms_session: phone_number " + str(phone_number) + " is invalid")
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    current_info = docassemble.base.functions.get_current_info()
    if yaml_filename is None:
        yaml_filename = current_info.get('yaml_filename', None)
        if yaml_filename is None:
            yaml_filename = default_yaml_filename
    temp_user_id = None
    if user_id is None and email is not None:
        user = UserModel.query.filter_by(email=email, active=True).first()
        if user is not None:
            user_id = user.id
    if user_id is None:
        if not new:
            if 'user' in current_info:
                if 'theid' in current_info['user']:
                    if current_info['user'].get('is_authenticated', False):
                        user_id = current_info['user']['theid']
                    else:
                        temp_user_id = current_info['user']['theid']
        if user_id is None and temp_user_id is None:
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            temp_user_id = new_temp_user.id
    if secret is None:
        if not new:
            secret = current_info['secret']
        if secret is None:
            secret = random_string(16)
    if uid is None:
        if new:
            uid = get_unique_name(yaml_filename, secret)
        else:
            uid = current_info.get('session', None)
            if uid is None:
                uid = get_unique_name(yaml_filename, secret)
    if encrypted is None:
        if new:
            encrypted = True
        else:
            encrypted = current_info['encrypted']
    sess_info = dict(yaml_filename=yaml_filename, uid=uid, secret=secret, number=phone_number, encrypted=encrypted, tempuser=temp_user_id, user_id=user_id)
    #logmessage("initiate_sms_session: setting da:sms:client:" + phone_number + ':server:' + tconfig['number'] + " to " + str(sess_info))
    r.set('da:sms:client:' + phone_number + ':server:' + tconfig['number'], pickle.dumps(sess_info))
    return True
        
def terminate_sms_session(phone_number, config='default'):
    sess_info = None
    if config not in twilio_config['name']:
        raise DAError("get_sms_session: Invalid twilio configuration")
    tconfig = twilio_config['name'][config]
    phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
    r.delete('da:sms:client:' + phone_number + ':server:' + tconfig['number'])

def fix_http(url):
    if HTTP_TO_HTTPS:
        return re.sub(r'^http:', 'https:', url)
    else:
        return url

def remove_question_package(args):
    if '_question' in args:
        del args['_question']
    if '_package' in args:
        del args['_package']
    
def get_url_from_file_reference(file_reference, **kwargs):
    if 'privileged' in kwargs:
        privileged = kwargs['privileged']
    else:
        privileged = False
    if isinstance(file_reference, DAFileList) and len(file_reference.elements) > 0:
        file_reference = file_reference.elements[0]
    elif isinstance(file_reference, DAFileCollection):
        file_reference = file_reference._first_file()
    elif isinstance(file_reference, DAStaticFile):
        return file_reference.url_for(**kwargs)
    if isinstance(file_reference, DAFile) and hasattr(file_reference, 'number'):
        file_number = file_reference.number
        if privileged or can_access_file_number(file_number):
            url_properties = dict()
            if hasattr(file_reference, 'filename') and len(file_reference.filename):
                url_properties['display_filename'] = file_reference.filename
            if hasattr(file_reference, 'extension'):
                url_properties['ext'] = file_reference.extension
            for key, val in kwargs.iteritems():
                url_properties[key] = val
            the_file = SavedFile(file_number)
            if kwargs.get('temporary', False):
                return(the_file.temp_url_for(**url_properties))
            else:
                return(the_file.url_for(**url_properties))
    file_reference = str(file_reference)
    if re.search(r'^http', file_reference):
        return(file_reference)
    if file_reference in ('login', 'signin'):
        remove_question_package(kwargs)
        return(url_for('user.login', **kwargs))
    elif file_reference == 'profile':
        remove_question_package(kwargs)
        return(url_for('user_profile_page', **kwargs))
    elif file_reference == 'change_password':
        remove_question_package(kwargs)
        return(url_for('user.change_password', **kwargs))
    elif file_reference == 'register':
        remove_question_package(kwargs)
        return(url_for('user.register', **kwargs))
    elif file_reference == 'leave':
        remove_question_package(kwargs)
        return(url_for('leave', **kwargs))
    elif file_reference == 'logout':
        remove_question_package(kwargs)
        return(url_for('user.logout', **kwargs))
    elif file_reference == 'restart':
        remove_question_package(kwargs)
        return(url_for('restart_session', **kwargs))
    elif file_reference == 'new_session':
        remove_question_package(kwargs)
        return(url_for('new_session', **kwargs))
    elif file_reference == 'help':
        return('javascript:show_help_tab()');
    elif file_reference == 'interview':
        remove_question_package(kwargs)
        return(url_for('index', **kwargs))
    elif file_reference == 'interviews':
        remove_question_package(kwargs)
        return(url_for('interview_list', **kwargs))
    elif file_reference == 'exit':
        remove_question_package(kwargs)
        return(url_for('exit', **kwargs))
    elif file_reference == 'exit_logout':
        remove_question_package(kwargs)
        return(url_for('exit_logout', **kwargs))
    elif file_reference == 'dispatch':
        remove_question_package(kwargs)
        return(url_for('interview_start', **kwargs))
    elif file_reference == 'interview_list':
        remove_question_package(kwargs)
        return(url_for('interview_list', **kwargs))
    elif file_reference == 'playground':
        remove_question_package(kwargs)
        return(url_for('playground_page', **kwargs))
    elif file_reference == 'playgroundtemplate':
        return(url_for('playground_files', section='template'))
    elif file_reference == 'playgroundstatic':
        return(url_for('playground_files', section='static'))
    elif file_reference == 'playgroundsources':
        return(url_for('playground_files', section='sources'))
    elif file_reference == 'playgroundmodules':
        return(url_for('playground_files', section='modules'))
    elif file_reference == 'playgroundpackages':
        remove_question_package(kwargs)
        return(url_for('playground_packages', **kwargs))
    elif file_reference == 'playgroundfiles':
        remove_question_package(kwargs)
        return(url_for('playground_files', **kwargs))
    elif file_reference == 'create_playground_package':
        remove_question_package(kwargs)
        return(url_for('create_playground_package', **kwargs))
    elif file_reference == 'configuration':
        remove_question_package(kwargs)
        return(url_for('config_page', **kwargs))
    elif file_reference == 'root':
        remove_question_package(kwargs)
        return(url_for('rootindex', **kwargs))
    if re.search('^[0-9]+$', file_reference):
        remove_question_package(kwargs)
        file_number = file_reference
        if kwargs.get('temporary', False):
            url = SavedFile(file_number).temp_url_for(**kwargs)
        elif can_access_file_number(file_number):
            url = SavedFile(file_number).url_for(**kwargs)
        else:
            logmessage("Problem accessing " + str(file_number))
            url = 'about:blank'
    else:
        question = kwargs.get('_question', None)
        package_arg = kwargs.get('_package', None)
        root = daconfig.get('root', '/')
        fileroot = daconfig.get('fileserver', root)
        if 'ext' in kwargs and kwargs['ext'] is not None:
            extn = kwargs['ext']
            extn = re.sub(r'^\.', '', extn)
            extn = '.' + extn
        else:
            extn = ''
        parts = file_reference.split(':')
        if len(parts) < 2:
            file_reference = re.sub(r'^data/static/', '', file_reference)
            the_package = None
            if question is not None and question.from_source is not None and hasattr(question.from_source, 'package'):
                the_package = question.from_source.package
            if the_package is None and package_arg is not None:
                the_package = package_arg
            if the_package is None:
                the_package = 'docassemble.base'
            parts = [the_package, file_reference]
        parts[1] = re.sub(r'^data/[^/]+/', '', parts[1])
        url = url_if_exists(parts[0] + ':data/static/' + parts[1] + extn)
        # if reference_exists(parts[0] + ':data/static/' + parts[1]):
        #     url = fileroot + 'packagestatic/' + parts[0] + '/' + parts[1] + extn
        # else:
        #     url = None
        if kwargs.get('_external', False) and url is not None and url.startswith('/'):
            url = docassemble.base.functions.get_url_root() + url
    return(url)

def user_id_dict():
    output = dict()
    for user in UserModel.query.all():
        output[user.id] = user
    anon = FakeUser()
    anon_role = FakeRole()
    anon_role.name = word('anonymous')
    anon.roles = [anon_role]
    anon.id = -1
    anon.firstname = 'Anonymous'
    anon.lastname = 'User'
    output[-1] = anon
    return output

def get_base_words():
    documentation = get_info_from_file_reference('docassemble.base:data/sources/base-words.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def get_documentation_dict():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def get_name_info():
    docstring = get_info_from_file_reference('docassemble.base:data/questions/docstring.yml')
    if 'fullpath' in docstring and docstring['fullpath'] is not None:
        with open(docstring['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def get_title_documentation():
    documentation = get_info_from_file_reference('docassemble.base:data/questions/title_documentation.yml')
    if 'fullpath' in documentation and documentation['fullpath'] is not None:
        with open(documentation['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            return(ruamel.yaml.safe_load(content))
    return(None)

def _call_or_get(function_or_property):
    return function_or_property() if callable(function_or_property) else function_or_property

def pad_to_16(the_string):
    if len(the_string) >= 16:
        return the_string[:16]
    return str(the_string) + (16 - len(the_string)) * '0'

def decrypt_session(secret, user_code=None, filename=None):
    #logmessage("decrypt_session: user_code is " + str(user_code) + " and filename is " + str(filename))
    nowtime = datetime.datetime.utcnow()
    if user_code == None or filename == None or secret is None:
        return
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        phrase = decrypt_phrase(record.phrase, secret)
        record.phrase = pack_phrase(phrase)
        record.encrypted = False
        changed = True
    if changed:
        db.session.commit()
    # changed = False
    # for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
    #     if record.dictionary:
    #         the_dict = decrypt_dictionary(record.dictionary, secret)
    #         record.dictionary = pack_dictionary(the_dict)
    #         record.encrypted = False
    #         record.modtime = nowtime
    #         changed = True
    # if changed:
    #     db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).all():
        the_dict = decrypt_dictionary(record.dictionary, secret)
        record.dictionary = pack_dictionary(the_dict)
        record.encrypted = False
        record.modtime = nowtime
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        phrase = decrypt_phrase(record.message, secret)
        record.message = pack_phrase(phrase)
        record.encrypted = False
        changed = True
    if changed:
        db.session.commit()
    return

def encrypt_session(secret, user_code=None, filename=None):
    #logmessage("encrypt_session: user_code is " + str(user_code) + " and filename is " + str(filename))
    nowtime = datetime.datetime.utcnow()
    if user_code == None or filename == None or secret is None:
        return
    changed = False
    for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        phrase = unpack_phrase(record.phrase)
        record.phrase = encrypt_phrase(phrase, secret)
        record.encrypted = True
        changed = True
    if changed:
        db.session.commit()
    # changed = False
    # for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
    #     if record.dictionary:
    #         the_dict = unpack_dictionary(record.dictionary)
    #         record.dictionary = encrypt_dictionary(the_dict, secret)
    #         record.encrypted = True
    #         record.modtime = nowtime
    #         changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=False).order_by(UserDict.indexno).all():
        the_dict = unpack_dictionary(record.dictionary)
        record.dictionary = encrypt_dictionary(the_dict, secret)
        record.encrypted = True
        record.modtime = nowtime
        changed = True
    if changed:
        db.session.commit()
    changed = False
    for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=False).all():
        phrase = unpack_phrase(record.message)
        record.message = encrypt_phrase(phrase, secret)
        record.encrypted = True
        changed = True
    if changed:
        db.session.commit()
    return

def substitute_secret(oldsecret, newsecret, user=None):
    if user is None:
        user = current_user
    #logmessage("substitute_secret: " + repr(oldsecret) + " and " + repr(newsecret))
    if oldsecret == 'None' or oldsecret == newsecret:
        #logmessage("substitute_secret: returning new secret without doing anything")
        return newsecret
    #logmessage("substitute_secret: continuing")
    user_code = session.get('uid', None)
    to_do = set()
    if 'i' in session and user_code is not None:
        to_do.add((session['i'], user_code))
    for the_record in db.session.query(UserDict.filename, UserDict.key).filter_by(user_id=user.id).group_by(UserDict.filename, UserDict.key).all():
        to_do.add((the_record.filename, the_record.key))
    for the_record in db.session.query(UserDictKeys.filename, UserDictKeys.key).filter_by(user_id=user.id).group_by(UserDictKeys.filename, UserDictKeys.key).all():
        to_do.add((the_record.filename, the_record.key))
    if user_code:
        for the_record in db.session.query(UserDict.filename).filter_by(key=user_code).group_by(UserDict.filename).all():
            to_do.add((the_record.filename, user_code))
    for (filename, user_code) in to_do:
        #logmessage("substitute_secret: filename is " + str(filename) + " and key is " + str(user_code))
        changed = False
        for record in SpeakList.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
            phrase = decrypt_phrase(record.phrase, oldsecret)
            record.phrase = encrypt_phrase(phrase, newsecret)
            changed = True
        if changed:
            db.session.commit()
        # changed = False
        # for record in Attachments.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
        #     if record.dictionary:
        #         the_dict = decrypt_dictionary(record.dictionary, oldsecret)
        #         record.dictionary = encrypt_dictionary(the_dict, newsecret)
        #         changed = True
        # if changed:
        #     db.session.commit()
        changed = False
        for record in UserDict.query.filter_by(key=user_code, filename=filename, encrypted=True).order_by(UserDict.indexno).all():
            #logmessage("substitute_secret: record was encrypted")
            try:
                the_dict = decrypt_dictionary(record.dictionary, oldsecret)
            except Exception as e:
                logmessage("substitute_secret: error decrypting dictionary for filename " + filename + " and uid " + user_code)
                continue
            if type(the_dict) is not dict:
                logmessage("substitute_secret: dictionary was not a dict for filename " + filename + " and uid " + user_code)
                continue
            record.dictionary = encrypt_dictionary(the_dict, newsecret)
            changed = True
        if changed:
            db.session.commit()
        changed = False
        for record in ChatLog.query.filter_by(key=user_code, filename=filename, encrypted=True).all():
            try:
                phrase = decrypt_phrase(record.message, oldsecret)
            except Exception as e:
                logmessage("substitute_secret: error decrypting phrase for filename " + filename + " and uid " + user_code)
                continue
            record.message = encrypt_phrase(phrase, newsecret)
            changed = True
        if changed:
            db.session.commit()
    return newsecret

def MD5Hash(data=None):
    if data is None:
        data = ''
    h = MD5.new()
    h.update(data)
    return h

# def _do_login_user(user, password, secret, next, remember_me=False):
#     logmessage("_do_login_user")
#     if not user:
#         return unauthenticated()

#     if not _call_or_get(user.is_active):
#         flash(word('Your account has not been enabled.'), 'error')
#         return redirect(url_for('user.login'))

#     user_manager = current_app.user_manager
#     if user_manager.enable_email and user_manager.enable_confirm_email \
#             and not current_app.user_manager.enable_login_without_confirm_email \
#             and not user.has_confirmed_email():
#         url = url_for('user.resend_confirm_email')
#         flash('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="' + str(url) + '">Re-send confirmation email</a>.', 'error')
#         return redirect(url_for('user.login'))

#     login_user(user, remember=remember_me)

#     if 'i' in session and 'uid' in session:
#         save_user_dict_key(session['uid'], session['i'])
#         session['key_logged'] = True 

#     signals.user_logged_in.send(current_app._get_current_object(), user=user)

#     if 'tempuser' in session:
#         changed = False
#         for chat_entry in ChatLog.query.filter_by(temp_user_id=int(session['tempuser'])).all():
#             chat_entry.user_id = user.id
#             chat_entry.temp_user_id = None
#             changed = True
#         if changed:
#             db.session.commit()
#         changed = False
#         for chat_entry in ChatLog.query.filter_by(temp_owner_id=int(session['tempuser'])).all():
#             chat_entry.owner_id = user.id
#             chat_entry.temp_owner_id = None
#             changed = True
#         if changed:
#             db.session.commit()
#         del session['tempuser']
#     session['user_id'] = user.id
#     flash(word('You have signed in successfully.'), 'success')

#     newsecret = substitute_secret(secret, pad_to_16(MD5Hash(data=password).hexdigest()))
#     response = redirect(next)
#     response.set_cookie('secret', newsecret)
#     return response

def set_request_active(value):
    global request_active
    request_active = value

def syslog_message(message):
    message = re.sub(r'\n', ' ', message)
    if current_user and current_user.is_authenticated and not current_user.is_anonymous:
        the_user = current_user.email
    else:
        the_user = "anonymous"
    if request_active:
        sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': request.remote_addr, 'yamlfile': session.get('i', 'na'), 'user': the_user, 'session': session.get('uid', 'na')})
    else:
        sys_logger.debug('%s', LOGFORMAT % {'message': message, 'clientip': 'localhost', 'yamlfile': 'na', 'user': 'na', 'session': 'na'})

def syslog_message_with_timestamp(message):
    syslog_message(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message)
    
def copy_playground_modules():
    devs = list()
    for user in UserModel.query.filter_by(active=True).all():
        for role in user.roles:
            if role.name == 'admin' or role.name == 'developer':
                devs.append(user.id)
    key = 'da:pgcopylock'
    found = False
    count = 20
    while count > 0:
        record = r.get(key)
        if record:
            time.sleep(1.0)
        else:
            found = False
            break
        found = True
        count -= 1
    if found:
        sys.stderr.write("Request for " + key + " deadlocked\n")
        r.delete(key)        
    pipe = r.pipeline()
    pipe.set(key, 1)
    pipe.expire(key, 4)
    pipe.execute()
    for user_id in devs:
        mod_dir = SavedFile(user_id, fix=True, section='playgroundmodules')
        local_dir = os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'playground' + str(user_id))
        if os.path.isdir(local_dir):
            try:
                shutil.rmtree(local_dir)
            except:
                pass
        os.makedirs(local_dir)
        #sys.stderr.write("Copying " + str(mod_dir.directory) + " to " + str(local_dir) + "\n")
        for f in [f for f in os.listdir(mod_dir.directory) if re.search(r'^[A-Za-z].*\.py$', f)]:
            shutil.copyfile(os.path.join(mod_dir.directory, f), os.path.join(local_dir, f))
        #shutil.copytree(mod_dir.directory, local_dir)
        with open(os.path.join(local_dir, '__init__.py'), 'w') as the_file:
            the_file.write(init_py_file)
    r.delete(key)

def proc_example_list(example_list, examples):
    for example in example_list:
        if type(example) is dict:
            for key, value in example.iteritems():
                sublist = list()
                proc_example_list(value, sublist)
                examples.append({'title': str(key), 'list': sublist})
                break
            continue
        result = dict()
        result['id'] = example
        result['interview'] = url_for('index', reset=1, i="docassemble.base:data/questions/examples/" + example + ".yml")
        example_file = 'docassemble.base:data/questions/examples/' + example + '.yml'
        result['image'] = url_for('static', filename='examples/' + example + ".png")
        file_info = get_info_from_file_reference(example_file)
        start_block = 1
        end_block = 2
        if 'fullpath' not in file_info or file_info['fullpath'] is None:
            logmessage("proc_example_list: could not find " + example_file)
            continue
        with open(file_info['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            content = fix_initial.sub('', content)
            blocks = map(lambda x: x.strip(), document_match.split(content))
            if len(blocks):
                has_context = False
                for block in blocks:
                    if re.search(r'metadata:', block):
                        try:
                            the_block = ruamel.yaml.safe_load(block)
                            if type(the_block) is dict and 'metadata' in the_block:
                                the_metadata = the_block['metadata']
                                result['title'] = the_metadata.get('title', the_metadata.get('short title', word('Untitled'))).rstrip()
                                result['documentation'] = the_metadata.get('documentation', None)
                                start_block = int(the_metadata.get('example start', 1))
                                end_block = int(the_metadata.get('example end', start_block)) + 1
                                break
                        except Exception as err:
                            logmessage("proc_example_list: error processing " + example_file + ": " + str(err))
                            continue
                if 'title' not in result:
                    logmessage("proc_example_list: no title in " + example_file)
                    continue
                if re.search(r'metadata:', blocks[0]) and start_block > 0:
                    initial_block = 1
                else:
                    initial_block = 0
                if start_block > initial_block:
                    result['before_html'] = highlight("\n---\n".join(blocks[initial_block:start_block]) + "\n---", YamlLexer(), HtmlFormatter())
                    has_context = True
                else:
                    result['before_html'] = ''
                if len(blocks) > end_block:
                    result['after_html'] = highlight("---\n" + "\n---\n".join(blocks[end_block:len(blocks)]), YamlLexer(), HtmlFormatter())
                    has_context = True
                else:
                    result['after_html'] = ''
                result['source'] = "\n---\n".join(blocks[start_block:end_block])
                result['html'] = highlight(result['source'], YamlLexer(), HtmlFormatter())
                result['has_context'] = has_context
            else:
                logmessage("proc_example_list: no blocks in " + example_file)
                continue
        examples.append(result)
    
def get_examples():
    examples = list()
    example_list_file = get_info_from_file_reference('docassemble.base:data/questions/example-list.yml')
    if 'fullpath' in example_list_file and example_list_file['fullpath'] is not None:
        example_list = list()
        with open(example_list_file['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
            content = fix_tabs.sub('  ', content)
            proc_example_list(ruamel.yaml.safe_load(content), examples)
    #logmessage("Examples: " + str(examples))
    return(examples)

def add_timestamps(the_dict, manual_user_id=None):
    nowtime = datetime.datetime.utcnow()
    the_dict['_internal']['starttime'] = nowtime 
    the_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated and not current_user.is_anonymous):
        if manual_user_id is not None:
            the_user_id = manual_user_id
        else:
            the_user_id = current_user.id
        the_dict['_internal']['accesstime'][the_user_id] = nowtime
    else:
        the_dict['_internal']['accesstime'][-1] = nowtime
    return

def fresh_dictionary():
    the_dict = copy.deepcopy(initial_dict)
    add_timestamps(the_dict)
    return the_dict    

def manual_checkout(manual_session_id=None, manual_filename=None, user_id=None):
    if manual_session_id is not None:
        session_id = manual_session_id
    else:
        session_id = session.get('uid', None)
    if manual_filename is not None:
        yaml_filename = manual_filename
    else:
        yaml_filename = session.get('i', None)
    if session_id is None or yaml_filename is None:
        return
    if user_id is None:
        if current_user.is_anonymous:
            the_user_id = 't' + str(session.get('tempuser', None))
        else:
            the_user_id = current_user.id
    else:
        the_user_id = user_id
    endpart = ':uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    pipe = r.pipeline()
    pipe.expire('da:session' + endpart, 12)
    pipe.expire('da:html' + endpart, 12)
    pipe.expire('da:interviewsession' + endpart, 12)
    pipe.expire('da:ready' + endpart, 12)
    pipe.expire('da:block' + endpart, 12)
    pipe.execute()
    #r.publish('da:monitor', json.dumps(dict(messagetype='refreshsessions')))
    #logmessage("Done checking out from " + endpart)
    return

def chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles):
    key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    if mode in ('peer', 'peerhelp'):
        peer_ok = True
    else:
        peer_ok = False
    if mode in ('help', 'peerhelp'):
        help_ok = True
    else:
        help_ok = False
    potential_partners = set()
    if help_ok and len(partner_roles) and not r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
        chat_session_key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        for role in partner_roles:
            for the_key in r.keys('da:monitor:role:' + role + ':userid:*'):
                user_id = re.sub(r'^.*:userid:', '', the_key)
                potential_partners.add(user_id)
        for the_key in r.keys('da:monitor:chatpartners:*'):
            user_id = re.sub(r'^.*chatpartners:', '', the_key)
            if user_id not in potential_partners:
                for chat_key in r.hgetall(the_key):
                    if chat_key == chat_session_key:
                        potential_partners.add(user_id)
    num_peer = 0
    if peer_ok:
        for sess_key in r.keys('da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
            if sess_key != key:
                num_peer += 1
    result = ChatPartners()
    result.peer = num_peer
    result.help = len(potential_partners)
    #return (dict(peer=num_peer, help=len(potential_partners)))
    return result
    
def do_redirect(url, is_ajax, is_json):
    if is_ajax:
        return jsonify(action='redirect', url=url, csrf_token=generate_csrf())
    else:
        if is_json:
            if re.search(r'\?', url):
                url = url + '&json=1'
            else:
                url = url + '?json=1'
        return redirect(url)

def do_refresh(is_ajax, yaml_filename):
    if is_ajax:
        return jsonify(action='refresh', csrf_token=generate_csrf())
    else:
        return redirect(url_for('index', i=yaml_filename))

def standard_scripts():
    return '\n    <script src="' + url_for('static', filename='app/jquery.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/jquery.validate.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/additional-methods.min.js') + '"></script>\n    <script src="' + url_for('static', filename='popper/umd/popper.min.js') + '"></script>\n    <script src="' + url_for('static', filename='popper/umd/tooltip.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap/js/bootstrap.min.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-slider/dist/bootstrap-slider.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>\n    <script src="' + url_for('static', filename='app/app.js') + '"></script>\n    <script src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>\n    <script src="' + url_for('static', filename='labelauty/source/jquery-labelauty.js') + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-combobox/js/bootstrap-combobox.js') + '"></script>'

def standard_html_start(interview_language=DEFAULT_LANGUAGE, debug=False, bootstrap_theme=None):
    if bootstrap_theme is None:
        bootstrap_part = '\n    <link href="' + url_for('static', filename='bootstrap/css/bootstrap.min.css') + '" rel="stylesheet">'
    else:
        bootstrap_part = '\n    <link href="' + bootstrap_theme + '" rel="stylesheet">'
    output = '<!DOCTYPE html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    <link rel="shortcut icon" href="' + url_for('favicon') + '">\n    <link rel="apple-touch-icon" sizes="180x180" href="' + url_for('apple_touch_icon') + '">\n    <link rel="icon" type="image/png" href="' + url_for('favicon_md') + '" sizes="32x32">\n    <link rel="icon" type="image/png" href="' + url_for('favicon_sm') + '" sizes="16x16">\n    <link rel="manifest" href="' + url_for('favicon_manifest_json') + '">\n    <link rel="mask-icon" href="' + url_for('favicon_safari_pinned_tab') + '" color="' + daconfig.get('favicon mask color', '#698aa7') + '">\n    <meta name="theme-color" content="' + daconfig.get('favicon theme color', '#83b3dd') + '">\n    <script defer src="' + url_for('static', filename='fontawesome/js/all.js') + '"></script>' + bootstrap_part + '\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />\n    <link href="' + url_for('static', filename='labelauty/source/jquery-labelauty.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-combobox/css/bootstrap-combobox.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-slider/dist/css/bootstrap-slider.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/app.css') + '" rel="stylesheet">'
    if debug:
        output += '\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'
    return output

def process_file(saved_file, orig_file, mimetype, extension, initial=True):
    if extension == "gif" and daconfig.get('imagemagick', 'convert') is not None:
        unconverted = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".gif", delete=False)
        converted = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".png", delete=False)
        shutil.move(orig_file, unconverted.name)
        call_array = [daconfig.get('imagemagick', 'convert'), str(unconverted.name), 'png:' + converted.name]
        result = call(call_array)
        if result == 0:
            saved_file.copy_from(converted.name, filename=re.sub(r'\.[^\.]+$', '', saved_file.filename) + '.png')
        else:
            logmessage("process_file: error converting from gif to png")
        shutil.move(unconverted.name, saved_file.path)
        saved_file.save()
    elif extension == "jpg" and daconfig.get('imagemagick', 'convert') is not None:
        unrotated = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".jpg", delete=False)
        rotated = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".jpg", delete=False)
        shutil.move(orig_file, unrotated.name)
        call_array = [daconfig.get('imagemagick', 'convert'), str(unrotated.name), '-auto-orient', '-density', '300', 'jpeg:' + rotated.name]
        result = call(call_array)
        if result == 0:
            saved_file.copy_from(rotated.name)
        else:
            saved_file.copy_from(unrotated.name)
    elif initial:
        shutil.move(orig_file, saved_file.path)
        saved_file.save()
    if mimetype == 'video/quicktime' and daconfig.get('avconv', 'avconv') is not None:
        call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
        result = call(call_array)
        call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'copy', '-acodec', 'copy', saved_file.path + '.mp4']
        result = call(call_array)
    if mimetype == 'video/mp4' and daconfig.get('avconv', 'avconv') is not None:
        call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-vcodec', 'libtheora', '-acodec', 'libvorbis', saved_file.path + '.ogv']
        result = call(call_array)
    if mimetype == 'video/ogg' and daconfig.get('avconv', 'avconv') is not None:
        call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '22', '-c:a', 'libmp3lame', '-qscale:a', '2', '-ac', '2', '-ar', '44100', saved_file.path + '.mp4']
        result = call(call_array)
    if mimetype == 'audio/mpeg' and daconfig.get('pacpl', 'pacpl') is not None:
        call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
        result = call(call_array)
    if mimetype == 'audio/ogg' and daconfig.get('pacpl', 'pacpl') is not None:
        call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
        result = call(call_array)
    if mimetype == 'audio/3gpp' and daconfig.get('avconv', 'avconv') is not None:
        call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, saved_file.path + '.ogg']
        result = call(call_array)
        call_array = [daconfig.get('avconv', 'avconv'), '-i', saved_file.path + '.' + extension, saved_file.path + '.mp3']
        result = call(call_array)
    if mimetype in ('audio/x-wav', 'audio/wav') and daconfig.get('pacpl', 'pacpl') is not None:
        call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'mp3', saved_file.path + '.' + extension]
        result = call(call_array)
        call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', saved_file.path + '.' + extension]
        result = call(call_array)
    #if extension == "pdf":
    #    make_image_files(saved_file.path)
    saved_file.finalize()

def sub_temp_user_dict_key(temp_user_id, user_id):
    for record in UserDictKeys.query.filter_by(temp_user_id=temp_user_id).all():
        record.temp_user_id = None
        record.user_id = user_id
    db.session.commit()

def save_user_dict_key(session_id, filename, priors=False, user=None):
    if user is not None:
        user_id = user.id
    else:
        if current_user.is_authenticated and not current_user.is_anonymous:
            is_auth = True
            user_id = current_user.id
        else:
            is_auth = False
            user_id = session.get('tempuser', None)
            if user_id is None:
                logmessage("save_user_dict_key: no user ID available for saving")
                return
    #logmessage("save_user_dict_key: called")
    interview_list = set([filename])
    found = set()
    if priors:
        for the_record in db.session.query(UserDict.filename).filter_by(key=session_id).group_by(UserDict.filename).all():
            # if the_record.filename not in interview_list:
            #     logmessage("Other interview found: " + the_record.filename)
            interview_list.add(the_record.filename)
    for filename_to_search in interview_list:
        the_record = UserDictKeys.query.filter_by(key=session_id, filename=filename_to_search, user_id=user_id).first()
        if the_record:
            found.add(filename_to_search)
    for filename_to_save in (interview_list - found):
        if is_auth:
            new_record = UserDictKeys(key=session_id, filename=filename_to_save, user_id=user_id)
        else:
            new_record = UserDictKeys(key=session_id, filename=filename_to_save, temp_user_id=user_id)
        db.session.add(new_record)
        db.session.commit()
    return

def save_user_dict(user_code, user_dict, filename, secret=None, changed=False, encrypt=True, manual_user_id=None, steps=None):
    #logmessage("save_user_dict: called with encrypt " + str(encrypt))
    nowtime = datetime.datetime.utcnow()
    if steps is not None:
        user_dict['_internal']['steps'] = steps
    user_dict['_internal']['modtime'] = nowtime
    if manual_user_id is not None or (current_user and current_user.is_authenticated and not current_user.is_anonymous):
        if manual_user_id is not None:
            the_user_id = manual_user_id
        else:
            the_user_id = current_user.id
        user_dict['_internal']['accesstime'][the_user_id] = nowtime
    else:
        user_dict['_internal']['accesstime'][-1] = nowtime
        the_user_id = None
    if changed is True:
        if encrypt:
            new_record = UserDict(modtime=nowtime, key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
        else:
            new_record = UserDict(modtime=nowtime, key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
        db.session.add(new_record)
        db.session.commit()
    else:
        max_indexno = db.session.query(db.func.max(UserDict.indexno)).filter(and_(UserDict.key == user_code, UserDict.filename == filename)).scalar()
        if max_indexno is None:
            if encrypt:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=encrypt_dictionary(user_dict, secret), filename=filename, user_id=the_user_id, encrypted=True)
            else:
                new_record = UserDict(modtime=nowtime, key=user_code, dictionary=pack_dictionary(user_dict), filename=filename, user_id=the_user_id, encrypted=False)
            db.session.add(new_record)
            db.session.commit()
        else:
            for record in UserDict.query.filter_by(key=user_code, filename=filename, indexno=max_indexno).all():
                if encrypt:
                    record.dictionary = encrypt_dictionary(user_dict, secret)
                    record.modtime = nowtime
                    record.encrypted = True
                else:
                    record.dictionary = pack_dictionary(user_dict)
                    record.modtime = nowtime
                    record.encrypted = False                   
            db.session.commit()
    return

def process_bracket_expression(match):
    try:
        inner = codecs.decode(match.group(1), 'base64').decode('utf8')
    except:
        inner = match.group(1)
    return("[" + re.sub(r'^u', r'', repr(inner)) + "]")

def myb64unquote(the_string):
    return(codecs.decode(the_string, 'base64').decode('utf8'))

def safeid(text):
    return codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '')

def from_safeid(text):
    return(codecs.decode(text, 'base64').decode('utf8'))

def test_for_valid_var(varname):
    if not valid_python_var.match(varname):
        raise DAError(varname + " is not a valid name.  A valid name consists only of letters, numbers, and underscores, and begins with a letter.")

def navigation_bar(nav, interview, wrapper=True, inner_div_class=None, show_links=True, hide_inactive_subs=True, a_class=None, show_nesting=True, include_arrows=False):
    if inner_div_class is None:
        inner_div_class = 'nav flex-column nav-pills danav danavlinks danav-vertical danavnested'
    if a_class is None:
        a_class = 'nav-link danavlink'
    #logmessage("navigation_bar: starting: " + str(section))
    the_language = docassemble.base.functions.get_language()
    if the_language not in nav.sections:
        the_language = DEFAULT_LANGUAGE
    if the_language not in nav.sections:
        the_language = '*'
    if the_language not in nav.sections:
        return ''
        #raise DAError("Could not find a navigation bar to display.  " + str(nav.sections))
    the_sections = nav.sections[the_language]
    if len(the_sections) == 0:
        return('')
    the_section = nav.current
    #logmessage("Current section is " + repr(the_section))
    #logmessage("Past sections are: " + str(nav.past))
    if the_section is None:
        if type(the_sections[0]) is dict:
            the_section = the_sections[0].keys()[0]
        else:
            the_section = the_sections[0]
    max_section = the_section
    if wrapper:
        output = '<div role="navigation" class="offset-xl-1 col-xl-2 col-lg-3 col-md-3 d-none d-md-block danavdiv">' + "\n" + '  <div class="nav flex-column nav-pills danav danav-vertical danavlinks">' + "\n"
    else:
        output = ''
    section_reached = False
    indexno = 0
    seen = set()
    on_first = True
    #logmessage("Sections is " + repr(the_sections))
    for x in the_sections:
        if include_arrows and not on_first:
            output += '<span class="dainlinearrow"><i class="fas fa-chevron-right"></i></span>'
        on_first = False
        indexno += 1
        the_key = None
        subitems = None
        currently_active = False
        if type(x) is dict:
            #logmessage("It is a dict")
            if len(x) == 2 and 'subsections' in x:
                for key, val in x.iteritems():
                    if key == 'subsections':
                        subitems = val
                    else:
                        the_key = key
                        test_for_valid_var(the_key)
                        the_title = val
            elif len(x) == 1:
                #logmessage("The len is one")
                the_key = x.keys()[0]
                test_for_valid_var(the_key)
                value = x[the_key]
                if type(value) is list:
                    subitems = value
                    the_title = the_key
                else:
                    the_title = value
            else:
                raise DAError("navigation_bar: too many keys in dict.  " + unicode(the_sections))
        else:
            #logmessage("It is not a dict")
            the_key = None
            the_title = unicode(x)
        if (the_key is not None and the_section == the_key) or the_section == the_title:
            #output += '<li role="presentation" class="' + li_class + ' active">'
            section_reached = True
            currently_active = True
            active_class = ' active'
        else:
            active_class = ''
            #output += '<li class="' + li_class + '" role="presentation">'
        new_key = the_title if the_key is None else the_key
        seen.add(new_key)
        #logmessage("new_key is: " + str(new_key))
        #logmessage("seen sections are: " + str(seen))
        #logmessage("nav past sections are: " + repr(nav.past))
        if len(nav.past.difference(seen)) or new_key in nav.past or the_title in nav.past:
            seen_more = True
        else:
            seen_more = False
        #logmessage("the title is " + str(the_title) + " and show links is " + str(show_links) + " and seen_more is " + str(seen_more) + " and currently_active is " + str(currently_active) + " and section_reached is " + str(section_reached) + " and the_key is " + str(the_key) + " and interview is " + unicode(interview) + " and in q is " + ('in q' if the_key in interview.questions else 'not in q'))
        if show_links and (seen_more or currently_active or not section_reached) and the_key is not None and interview is not None and the_key in interview.questions:
            #url = docassemble.base.functions.interview_url_action(the_key)
            if section_reached and not currently_active and not seen_more:
                output += '<a tabindex="0" data-index="' + str(indexno) + '" class="' + a_class + ' notavailableyet">' + unicode(the_title) + '</a>'
            else:
                if active_class == '' and not (seen_more and not section_reached):
                    output += '<a tabindex="0" data-index="' + str(indexno) + '" class="' + a_class + ' inactive">' + unicode(the_title) + '</a>'
                else:
                    output += '<a tabindex="0" data-key="' + the_key + '" data-index="' + str(indexno) + '" class="clickable ' + a_class + active_class + '">' + unicode(the_title) + '</a>'
        else:
            if section_reached and not currently_active and not seen_more:
                output += '<a tabindex="0" data-index="' + str(indexno) + '" class="' + a_class + ' notavailableyet">' + unicode(the_title) + '</a>'
            else:
                if active_class == '' and not (seen_more and not section_reached):
                    output += '<a tabindex="0" data-index="' + str(indexno) + '" class="' + a_class + ' inactive">' + unicode(the_title) + '</a>'
                else:
                    output += '<a tabindex="0" data-index="' + str(indexno) + '" class="' + a_class + active_class + '">' + unicode(the_title) + '</a>'
        suboutput = ''
        if subitems:
            current_is_within = False
            oldindexno = indexno
            first_sub = True
            for y in subitems:
                if include_arrows:
                    suboutput += '<span class="dainlinearrow"><i class="fas fa-chevron-right"></i></span>'
                first_sub = False
                indexno += 1
                sub_currently_active = False
                if type(y) is dict:
                    if len(y) == 1:
                        sub_key = y.keys()[0]
                        test_for_valid_var(sub_key)
                        sub_title = y[sub_key]
                    else:
                        raise DAError("navigation_bar: too many keys in dict.  " + unicode(the_sections))
                        continue
                else:
                    sub_key = None
                    sub_title = unicode(y)
                if (sub_key is not None and the_section == sub_key) or the_section == sub_title:
                    #suboutput += '<li class="' + li_class + ' active" role="presentation">'
                    section_reached = True
                    current_is_within = True
                    sub_currently_active = True
                    sub_active_class = ' active'
                else:
                    sub_active_class = ''
                    #suboutput += '<li class="' + li_class + '" role="presentation">'
                new_sub_key = sub_title if sub_key is None else sub_key
                seen.add(new_sub_key)
                #logmessage("sub: seen sections are: " + str(seen))
                if len(nav.past.difference(seen)) or new_sub_key in nav.past:
                    seen_more = True
                else:
                    seen_more = False
                if show_links and (seen_more or sub_currently_active or not section_reached) and sub_key is not None and interview is not None and sub_key in interview.questions:
                    #url = docassemble.base.functions.interview_url_action(sub_key)
                    suboutput += '<a tabindex="0" data-key="' + sub_key + '" data-index="' + str(indexno) + '" class="clickable ' + a_class + sub_active_class + '">' + unicode(sub_title) + '</a>'
                else:
                    if section_reached and not sub_currently_active and not seen_more:
                        suboutput += '<a tabindex="0" data-index="' + str(indexno) + '" class="' + a_class + ' notavailableyet">' + unicode(sub_title) + '</a>'
                    else:
                        suboutput += '<a tabindex="0" data-index="' + str(indexno) + '" class="' + a_class + sub_active_class + ' inactive">' + unicode(sub_title) + '</a>'
                #suboutput += "</li>"
            if currently_active or current_is_within or hide_inactive_subs is False or show_nesting:
                if currently_active or current_is_within:
                    suboutput = '<div class="' + inner_div_class + '">' + suboutput
                else:
                    suboutput = '<div style="display: none;" class="notshowing ' + inner_div_class + '">' + suboutput
                suboutput += "</div>"
                output += suboutput
            else:
                indexno = oldindexno
        #output += "</li>"
    if wrapper:
        output += "\n</div>\n</div>\n"
    if not section_reached:
        logmessage("Section \"" + unicode(the_section) + "\" did not exist.")
    return output        

def progress_bar(progress, interview):
    if progress is None:
        return('');
    progress = float(progress)
    if progress <= 0:
        return('');
    if progress > 100:
        progress = 100
    if hasattr(interview, 'show_progress_bar_percentage') and interview.show_progress_bar_percentage:
        percentage = unicode(int(progress)) + '%'
    else:
        percentage = ''
    return('<div class="progress mt-2"><div class="progress-bar" role="progressbar" aria-valuenow="' + str(progress) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(progress) + '%;">' + percentage + '</div></div>\n')

def get_unique_name(filename, secret):
    nowtime = datetime.datetime.utcnow()
    while True:
        newname = random_string(32)
        obtain_lock(newname, filename)
        existing_key = UserDict.query.filter_by(key=newname).first()
        if existing_key:
            release_lock(newname, filename)
            continue
        new_user_dict = UserDict(modtime=nowtime, key=newname, filename=filename, dictionary=encrypt_dictionary(fresh_dictionary(), secret))
        db.session.add(new_user_dict)
        db.session.commit()
        return newname

# def get_attachment_info(the_user_code, question_number, filename, secret):
#     the_user_dict = None
#     existing_entry = Attachments.query.filter_by(key=the_user_code, question=question_number, filename=filename).first()
#     if existing_entry and existing_entry.dictionary:
#         if existing_entry.encrypted:
#             the_user_dict = decrypt_dictionary(existing_entry.dictionary, secret)
#         else:
#             the_user_dict = unpack_dictionary(existing_entry.dictionary)
#     return the_user_dict, existing_entry.encrypted

# def update_attachment_info(the_user_code, the_user_dict, the_interview_status, secret, encrypt=True):
#     Attachments.query.filter_by(key=the_user_code, question=the_interview_status.question.number, filename=the_interview_status.question.interview.source.path).delete()
#     db.session.commit()
#     if encrypt:
#         new_attachment = Attachments(key=the_user_code, dictionary=encrypt_dictionary(the_user_dict, secret), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=True)
#     else:
#         new_attachment = Attachments(key=the_user_code, dictionary=pack_dictionary(the_user_dict), question = the_interview_status.question.number, filename=the_interview_status.question.interview.source.path, encrypted=False)
#     db.session.add(new_attachment)
#     db.session.commit()
#     return

def obtain_lock(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    found = False
    count = 4
    while count > 0:
        record = r.get(key)
        if record:
            sys.stderr.write("obtain_lock: waiting for " + key + "\n")
            time.sleep(1.0)
        else:
            found = False
            break
        found = True
        count -= 1
    if found:
        sys.stderr.write("Request for " + key + " deadlocked\n")
        release_lock(user_code, filename)
    pipe = r.pipeline()
    pipe.set(key, 1)
    pipe.expire(key, 4)
    pipe.execute()
    
def release_lock(user_code, filename):
    key = 'da:lock:' + user_code + ':' + filename
    r.delete(key)

def make_navbar(status, steps, show_login, chat_info, debug_mode):
    if 'inverse navbar' in status.question.interview.options:
        if status.question.interview.options['inverse navbar']:
            inverse = 'navbar-dark bg-dark '
        else:
            inverse = 'navbar-light bg-light '
    elif daconfig.get('inverse navbar', True):
        inverse = 'navbar-dark bg-dark '
    else:
        inverse = 'navbar-light-bg-light '
    navbar = """\
    <div class="navbar fixed-top navbar-expand-md """ + inverse + '"' + """>
      <div class="container danavcontainer justify-content-start">
"""
    if status.question.can_go_back and steps > 1:
        if status.question.interview.navigation_back_button:
            navbar += """\
        <span class="navbar-brand"><form style="inline-block" id="backbutton" method="POST"><input type="hidden" name="csrf_token" value=""" + '"' + generate_csrf() + '"' + """/><input type="hidden" name="_back_one" value="1"><button class="dabackicon text-muted backbuttoncolor" type="submit" title=""" + json.dumps(word("Go back to the previous question")) + """><i class="fas fa-chevron-left"></i><span class="daback">""" + word('Back') + """</span></button></form></span>
"""
        else:
            navbar += """\
        <form style="inline-block" id="backbutton" method="POST"><input type="hidden" name="csrf_token" value=""" + '"' + generate_csrf() + '"' + """/><input type="hidden" name="_back_one" value="1"></form>
"""
    navbar += """\
        <a id="pagetitle" class="navbar-brand pointer" href="#"><span class="d-none d-md-block">""" + status.display_title + """</span><span class="d-block d-md-none">""" + status.display_short_title + """</span></a>
"""
    help_message = word("Help is available")
    help_label = None
    for help_section in status.helpText:
        if status.question.interview.question_help_button and help_section['from'] == 'question':
            continue
        if help_section['label']:
            help_label = help_section['label']
            break
    if help_label is None:
        help_label = status.question.help()
    extra_help_message = word("Help is available for this question")
    phone_message = word("Phone help is available")
    chat_message = word("Live chat is available")
    source_message = word("How this question came to be asked")
    if debug_mode:
        source_button = '<li class="nav-item d-none d-md-block"><a class="no-outline nav-link" title=' + json.dumps(source_message) + ' id="sourcetoggle" href="#source" data-toggle="collapse" aria-expanded="false" aria-controls="source">' + word('Source') + '</a></li>'
    else:
        source_button = ''
    navbar += '        <ul class="nav navbar-nav mynavbar-right">' + source_button + '<li class="nav-item invisible"><a class="nav-link" tabindex="0" id="questionlabel" data-target="#question">' + word('Question') + '</a></li>'
    if len(status.helpText):
        if status.question.helptext is None or status.question.interview.question_help_button:
            navbar += '<li class="nav-item"><a tabindex="0" class="pointer no-outline nav-link helptrigger" data-target="#help" id="helptoggle" title=' + json.dumps(help_message) + '>' + help_label + '</a></li>'
        else:
            navbar += '<li class="nav-item"><a tabindex="0" class="pointer no-outline nav-link helptrigger" data-target="#help" id="helptoggle" title=' + json.dumps(extra_help_message) + '><span class="daactivetext">' + help_label + ' <i class="fas fa-star"></i></span></a></li>'
    navbar += '<li class="nav-item invisible" id="daPhoneAvailable"><a data-target="#help" title=' + json.dumps(phone_message) + ' class="nav-link pointer helptrigger"><i class="fas fa-phone chat-active"></i></a></li><li class="nav-item invisible" id="daChatAvailable"><a tabindex="0" data-target="#help" title=' + json.dumps(chat_message) + ' class="nav-link pointer helptrigger" ><i class="fas fa-comment-alt"></i></a></li></ul>'
    navbar += """
        <button id="mobile-toggler" type="button" class="navbar-toggler ml-auto" data-toggle="collapse" data-target="#navbar-collapse">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbar-collapse">
          <ul class="navbar-nav ml-auto">
"""
    if 'menu_items' in status.extras:
        if type(status.extras['menu_items']) is not list:
            custom_menu += '<a tabindex="0" class="dropdown-item">' + word("Error: menu_items is not a Python list") + '</a>'
        elif len(status.extras['menu_items']):
            custom_menu = ""
            for menu_item in status.extras['menu_items']:
                if not (type(menu_item) is dict and 'url' in menu_item and 'label' in menu_item):
                    custom_menu += '<a tabindex="0" class="dropdown-item">' + word("Error: menu item is not a Python dict with keys of url and label") + '</li>'
                else:
                    match_action = re.search(r'^\?action=([^\&]+)', menu_item['url'])
                    if match_action:
                        custom_menu += '<a class="dropdown-item" data-embaction="' + match_action.group(1) + '" href="' + menu_item['url'] + '">' + menu_item['label'] + '</a>'
                    else:
                        custom_menu += '<a class="dropdown-item" href="' + menu_item['url'] + '">' + menu_item['label'] + '</a>'
        else:
            custom_menu = False
    else:
        custom_menu = False
    if ALLOW_REGISTRATION:
        sign_in_text = word('Sign in or sign up to save answers')
    else:
        sign_in_text = word('Sign in to save answers')
    if show_login:
        if current_user.is_anonymous:
            if custom_menu:
                navbar += '            <li class="nav-item dropdown"><a href="#" class="nav-link dropdown-toggle d-none d-md-block" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '</a><div class="dropdown-menu dropdown-menu-right">' + custom_menu + '<a class="dropdown-item" href="' + url_for('user.login') + '">' + sign_in_text + '</a></div></li>'
            else:
                navbar += '            <li class="nav-item"><a class="nav-link" href="' + url_for('user.login') + '">' + sign_in_text + '</a></li>'
        else:
            if (custom_menu is False or custom_menu == '') and status.question.interview.options.get('hide standard menu', False):
                navbar += '            <li class="nav-item"><a class="nav-link" tabindex="0">' + (current_user.email if current_user.email else re.sub(r'.*\$', '', current_user.social_id)) + '</a></li>'
            else:
                navbar += '            <li class="nav-item dropdown"><a class="nav-link dropdown-toggle d-none d-md-block" href="#" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + (current_user.email if current_user.email else re.sub(r'.*\$', '', current_user.social_id)) + '</a><div class="dropdown-menu dropdown-menu-right">'
                if custom_menu:
                    navbar += custom_menu
                if not status.question.interview.options.get('hide standard menu', False):
                    if current_user.has_role('admin', 'advocate'):
                        navbar +='<a class="dropdown-item" href="' + url_for('monitor') + '">' + word('Monitor') + '</a>'
                    if current_user.has_role('admin', 'developer', 'trainer'):
                        navbar +='<a class="dropdown-item" href="' + url_for('train') + '">' + word('Train') + '</a>'
                    if current_user.has_role('admin', 'developer'):
                        navbar +='<a class="dropdown-item" href="' + url_for('update_package') + '">' + word('Package Management') + '</a>'
                        navbar +='<a class="dropdown-item" href="' + url_for('logs') + '">' + word('Logs') + '</a>'
                        navbar +='<a class="dropdown-item" href="' + url_for('playground_page') + '">' + word('Playground') + '</a>'
                        navbar +='<a class="dropdown-item" href="' + url_for('utilities') + '">' + word('Utilities') + '</a>'
                        if current_user.has_role('admin'):
                            navbar +='<a class="dropdown-item" href="' + url_for('user_list') + '">' + word('User List') + '</a>'
                            navbar +='<a class="dropdown-item" href="' + url_for('config_page') + '">' + word('Configuration') + '</a>'
                    if app.config['SHOW_DISPATCH']:
                        navbar += '<a class="dropdown-item" href="' + url_for('interview_start') + '">' + word('Available Interviews') + '</a>'
                    if app.config['SHOW_MY_INTERVIEWS'] or current_user.has_role('admin'):
                        navbar += '<a class="dropdown-item" href="' + url_for('interview_list') + '">' + word('My Interviews') + '</a>'
                    if current_user.has_role('admin', 'developer'):
                        navbar += '<a class="dropdown-item" href="' + url_for('user_profile_page') + '">' + word('Profile') + '</a>'
                    else:
                        if app.config['SHOW_PROFILE'] or current_user.has_role('admin'):
                            navbar += '<a class="dropdown-item" href="' + url_for('user_profile_page') + '">' + word('Profile') + '</a>'
                        else:
                            navbar += '<a class="dropdown-item" href="' + url_for('user.change_password') + '">' + word('Change Password') + '</a>'
                    navbar += '<a class="dropdown-item" href="' + url_for('user.logout') + '">' + word('Sign Out') + '</a>'
            navbar += '</div></li>'
    else:
        if custom_menu:
            navbar += '            <li class="nav-item dropdown"><a class="nav-link dropdown-toggle" href="#" class="dropdown-toggle d-none d-md-block" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + word("Menu") + '</a><div class="dropdown-menu dropdown-menu-right">' + custom_menu
            if not status.question.interview.options.get('hide standard menu', False):
                navbar += '<a class="dropdown-item" href="' + url_for(status.exit_link) + '">' + word(status.exit_label) + '</a>'
            navbar += '</div></li>'
        else:
            navbar += '            <li class="nav-item"><a class="nav-link" href="' + url_for(status.exit_link) + '">' + word(status.exit_label) + '</a></li>'
    navbar += """
          </ul>
        </div>
      </div>
    </div>
"""
    return(navbar)

def delete_session_for_interview():
    for key in ('i', 'uid', 'key_logged', 'action', 'encrypted', 'chatstatus', 'observer', 'monitor', 'doing_sms'):
        if key in session:
            del session[key]
    return

def delete_session():
    for key in ('i', 'uid', 'key_logged', 'action', 'tempuser', 'user_id', 'encrypted', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'playgroundfile', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules', 'playgroundpackages', 'taskwait', 'phone_number', 'otp_secret', 'validated_user', 'github_next'):
        if key in session:
            del session[key]
    return

def backup_session():
    backup = dict()
    for key in ('i', 'uid', 'key_logged', 'action', 'tempuser', 'user_id', 'encrypted', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'playgroundfile', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules', 'playgroundpackages', 'taskwait', 'phone_number', 'otp_secret', 'validated_user', 'github_next'):
        if key in session:
            backup[key] = session[key]
    return backup

def restore_session(backup):
    for key in ('i', 'uid', 'key_logged', 'action', 'tempuser', 'user_id', 'encrypted', 'google_id', 'google_email', 'chatstatus', 'observer', 'monitor', 'variablefile', 'doing_sms', 'playgroundfile', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules', 'playgroundpackages', 'taskwait', 'phone_number', 'otp_secret', 'validated_user', 'github_next'):
        if key in backup:
            session[key] = backup[key]

def reset_session(yaml_filename, secret, retain_code=False):
    #logmessage("reset_session: retain_code is " + str(retain_code))
    session['i'] = yaml_filename
    if retain_code is False or 'uid' not in session:
        session['uid'] = get_unique_name(yaml_filename, secret)
    if 'key_logged' in session:
        del session['key_logged']
    if 'action' in session:
        del session['action']
    user_code = session['uid']
    #logmessage("reset_session: user_code is " + str(user_code))
    user_dict = fresh_dictionary()
    return(user_code, user_dict)

def _endpoint_url(endpoint):
    url = url_for('index')
    if endpoint:
        url = url_for(endpoint)
    return url

def user_can_edit_package(pkgname=None, giturl=None):
    if not PACKAGE_PROTECTION:
        if pkgname in ('docassemble.base', 'docassemble.demo', 'docassemble.webapp'):
            return False
        return True
    if pkgname is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(and_(Package.name == pkgname, Package.active == True))
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    if giturl is not None:
        results = db.session.query(Package.id, PackageAuth.user_id, PackageAuth.authtype).outerjoin(PackageAuth, Package.id == PackageAuth.package_id).filter(and_(Package.giturl == giturl, Package.active == True))
        if results.count() == 0:
            return(True)
        for d in results:
            if d.user_id == current_user.id:
                return True
    return(False)

def uninstall_package(packagename):
    #logmessage("server uninstall_package: " + packagename)
    existing_package = Package.query.filter_by(name=packagename, active=True).order_by(Package.id.desc()).first()
    if existing_package is None:
        flash(word("Package did not exist"), 'error')
        return
    for package in Package.query.filter_by(name=packagename, active=True).all():
        package.active = False
    db.session.commit()
    return

def summarize_results(results, logmessages):
    output = '<br>'.join([x + ':&nbsp;' + results[x] for x in sorted(results.keys())])
    if len(logmessages):
        if len(output):
            output += '<br><br><strong>'+ word("pip log") + ':</strong><br>'
        else:
            output = ''
        output += re.sub(r'\n', r'<br>', logmessages)
    return Markup(output)

def install_zip_package(packagename, file_number):
    #logmessage("install_zip_package: " + packagename + " " + str(file_number))
    existing_package = Package.query.filter_by(name=packagename).order_by(Package.id.desc()).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, upload=file_number, active=True, type='zip', version=1)
        db.session.add(package_auth)
        db.session.add(package_entry)
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None and existing_package.upload != file_number:
            SavedFile(existing_package.upload).delete()
        existing_package.package_auth.user_id = current_user.id
        existing_package.package_auth.authtype = 'owner'
        existing_package.upload = file_number
        existing_package.active = True
        existing_package.limitation = None
        existing_package.giturl = None
        existing_package.gitbranch = None
        existing_package.type = 'zip'
        existing_package.version += 1
    db.session.commit()
    return

def install_git_package(packagename, giturl, branch=None):
    #logmessage("install_git_package: " + packagename + " " + str(giturl))
    if branch is None or str(branch).lower().strip() in ('none', ''):
        branch = 'master'
    if Package.query.filter_by(name=packagename).first() is None and Package.query.filter_by(giturl=giturl).first() is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, giturl=giturl, package_auth=package_auth, version=1, active=True, type='git', upload=None, limitation=None, gitbranch=branch)
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        existing_package = Package.query.filter_by(name=packagename).order_by(Package.id.desc()).first()
        if existing_package is None:
            existing_package = Package.query.filter_by(giturl=giturl).order_by(Package.id.desc()).first()
        if existing_package is not None:
            if existing_package.type == 'zip' and existing_package.upload is not None:
                SavedFile(existing_package.upload).delete()
            existing_package.package_auth.user_id = current_user.id
            existing_package.package_auth.authtype = 'owner'
            existing_package.name = packagename
            existing_package.giturl = giturl
            existing_package.upload = None
            existing_package.version += 1
            existing_package.limitation = None
            existing_package.active = True
            if branch:
                existing_package.gitbranch = branch
            existing_package.type = 'git'
            db.session.commit()
        else:
            logmessage("install_git_package: package " + str(giturl) + " appeared to exist but could not be found")
    return

def install_pip_package(packagename, limitation):
    existing_package = Package.query.filter_by(name=packagename).order_by(Package.id.desc()).first()
    if existing_package is None:
        package_auth = PackageAuth(user_id=current_user.id)
        package_entry = Package(name=packagename, package_auth=package_auth, limitation=limitation, version=1, active=True, type='pip')
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
    else:
        if existing_package.type == 'zip' and existing_package.upload is not None:
            SavedFile(existing_package.upload).delete()
        existing_package.package_auth.user_id = current_user.id
        existing_package.package_auth.authtype = 'owner'
        existing_package.version += 1
        existing_package.type = 'pip'
        existing_package.limitation = limitation
        existing_package.giturl = None
        existing_package.gitbranch = None
        existing_package.upload = None
        existing_package.active = True
        db.session.commit()
    return

def get_package_info(exclude_core=False):
    if current_user.has_role('admin'):
        is_admin = True
    else:
        is_admin = False
    package_list = list()
    package_auth = dict()
    seen = dict()
    for auth in PackageAuth.query.all():
        if auth.package_id not in package_auth:
            package_auth[auth.package_id] = dict()
        package_auth[auth.package_id][auth.user_id] = auth.authtype
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        #if exclude_core and package.name in ('docassemble', 'docassemble.base', 'docassemble.webapp'):
        #    continue
        if package.name in seen:
            continue
        seen[package.name] = 1
        if package.type is not None:
            if package.type == 'zip':
                can_update = False
            else:
                can_update = True
            if is_admin or (package.id in package_auth and current_user.id in package_auth[package.id]):
                can_uninstall = True
            else:
                can_uninstall = False
            if package.core:
                can_uninstall = False
                can_update = is_admin
            if exclude_core and package.name in ('docassemble', 'docassemble.base', 'docassemble.webapp'):
                can_uninstall = False
                can_update = False
            package_list.append(Object(package=package, can_update=can_update, can_uninstall=can_uninstall))
    return package_list, package_auth

def name_of_user(user, include_email=False):
    output = ''
    if user.first_name:
        output += user.first_name
        if user.last_name:
            output += ' '
    if user.last_name:
        output += user.last_name
    if include_email and user.email:
        if output:
            output += ', '
        output += user.email
    return output

def flash_as_html(message, message_type="info", is_ajax=True):
    if message_type == 'error':
        message_type = 'danger'
    output = """
        <div class="alert alert-""" + str(message_type) + """"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>""" + str(message) + """</div>
"""
    if not is_ajax:
        flash(message, message_type)
    return output

def make_example_html(examples, first_id, example_html, data_dict):
    example_html.append('          <ul class="nav flex-column nav-pills example-list example-hidden">\n')
    for example in examples:
        if 'list' in example:
            example_html.append('          <li class="nav-item"><a tabindex="0" class="nav-link example-heading">' + example['title'] + '</a>')
            make_example_html(example['list'], first_id, example_html, data_dict)
            example_html.append('          </li>')
            continue
        if len(first_id) == 0:
            first_id.append(example['id'])
        example_html.append('            <li class="nav-item"><a tabindex="0" class="nav-link example-link" data-example="' + example['id'] + '">' + example['title'] + '</a></li>')
        data_dict[example['id']] = example
    example_html.append('          </ul>')

def public_method(method, the_class):
    if isinstance(method, types.MethodType) and method.__name__ != 'init' and not method.__name__.startswith('_') and method.__name__ in the_class.__dict__:
        return True
    return False

def noquote(string):
    if string is None:
        return string
    string = amp_match.sub('&amp;', string)
    string = noquote_match.sub('&quot;', string)
    string = lt_match.sub('&lt;', string)
    string = gt_match.sub('&gt;', string)
    return string

def infobutton(title):
    docstring = ''
    if 'doc' in title_documentation[title]:
        docstring += noquote(title_documentation[title]['doc']) + "<br>"
    if 'url' in title_documentation[title]:
        docstring += "<a target='_blank' href='" + title_documentation[title]['url'] + "'>" + word("View documentation") + "</a>"
    return '&nbsp;<a tabindex="0" class="daquestionsign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + docstring + '" title=' + json.dumps(word("Help")) + ' data-selector="true" data-title="' + noquote(title_documentation[title].get('title', title)) + '"><i class="fas fa-question-circle"></i></a>'

def search_button(var, field_origins, name_origins, interview_source, all_sources):
    in_this_file = False
    usage = dict()
    if var in field_origins:
        for x in sorted(field_origins[var]):
            if x is interview_source:
                in_this_file = True
            else:
                if x.path not in usage:
                    usage[x.path] = set()
                usage[x.path].add('defined')
                all_sources.add(x)
    if var in name_origins:
        for x in sorted(name_origins[var]):
            if x is interview_source:
                in_this_file = True
            else:
                if x.path not in usage:
                    usage[x.path] = set()
                usage[x.path].add('used')
                all_sources.add(x)
    usage_type = [set(), set(), set()]
    for path, the_set in usage.iteritems():
        if 'defined' in the_set and 'used' in the_set:
            usage_type[2].add(path)
        elif 'used' in the_set:
            usage_type[1].add(path)
        elif 'defined' in the_set:
            usage_type[0].add(path)
        else:
            continue
    messages = list()
    if len(usage_type[2]):
        messages.append(word("Defined and used in " + docassemble.base.functions.comma_and_list(sorted(usage_type[2]))))
    elif len(usage_type[0]):
        messages.append(word("Defined in") + ' ' + docassemble.base.functions.comma_and_list(sorted(usage_type[0])))
    elif len(usage_type[2]):
        messages.append(word("Used in") + ' ' + docassemble.base.functions.comma_and_list(sorted(usage_type[0])))
    if len(messages):
        title = 'title="' + '; '.join(messages) + '" '
    else:
        title = ''
    if in_this_file:
        classname = 'dasearchthis'
    else:
        classname = 'dasearchother'
    return '<a tabindex="0" class="dasearchicon ' + classname + '" ' + title + 'data-name="' + noquote(var) + '"><i class="fas fa-search"></i></a>'

search_key = """
                  <tr><td><h4>""" + word("Note") + """</h4></td></tr>
                  <tr><td><a tabindex="0" class="dasearchicon dasearchthis"><i class="fas fa-search"></i></a> """ + word("means the name is located in this file") + """</td></tr>
                  <tr><td><a tabindex="0" class="dasearchicon dasearchother"><i class="fas fa-search"></i></a> """ + word("means the name may be located in a file included by reference, such as:") + """</td></tr>"""

def find_needed_names(interview, needed_names, the_name=None, the_question=None):
    if the_name is not None:
        needed_names.add(the_name)
        if the_name in interview.questions:
            for lang in interview.questions[the_name]:
                for question in interview.questions[the_name][lang]:
                    find_needed_names(interview, needed_names, the_question=question)
    elif the_question is not None:
        for the_set in (the_question.mako_names, the_question.names_used):
            for name in the_set:
                if name in needed_names:
                    continue
                find_needed_names(interview, needed_names, the_name=name)
    else:
        for question in interview.questions_list:
            #if not (question.is_mandatory or question.is_initial):
            #    continue
            find_needed_names(interview, needed_names, the_question=question)

def get_ml_info(varname, default_package, default_file):
    parts = varname.split(':')
    if len(parts) == 3 and parts[0].startswith('docassemble.') and re.match(r'data/sources/.*\.json', parts[1]):
        the_package = parts[0]
        the_file = parts[1]
        the_varname = parts[2]
    elif len(parts) == 2 and parts[0] == 'global':
        the_package = '_global'
        the_file = '_global'
        the_varname = parts[1]
    elif len(parts) == 2 and (re.match(r'data/sources/.*\.json', parts[0]) or re.match(r'[^/]+\.json', parts[0])):
        the_package = default_package
        the_file = re.sub(r'^data/sources/', '', parts[0])
        the_varname = parts[1]
    elif len(parts) != 1:
        the_package = '_global'
        the_file = '_global'
        the_varname = varname
    else:
        the_package = default_package
        the_file = default_file
        the_varname = varname
    return (the_package, the_file, the_varname)
        
def get_vars_in_use(interview, interview_status, debug_mode=False, return_json=False, show_messages=True, show_jinja_help=False):
    user_dict = fresh_dictionary()
    has_no_endpoint = False
    if 'uid' not in session:
        session['uid'] = random_string(32)
    if debug_mode:
        has_error = True
        error_message = "Not checking variables because in debug mode."
        error_type = Exception
    else:
        if not interview.success:
            has_error = True
            error_type = DAErrorCompileError
        else:
            try:
                interview.assemble(user_dict, interview_status)
                has_error = False
            except Exception as errmess:
                has_error = True
                error_message = str(errmess)
                error_type = type(errmess)
                logmessage("get_vars_in_use: failed assembly with error type " + str(error_type) + " and message: " + error_message)
    fields_used = set()
    names_used = set()
    field_origins = dict()
    name_origins = dict()
    all_sources = set()
    names_used.update(interview.names_used)
    for question in interview.questions_list:
        for the_set in (question.mako_names, question.names_used, question.fields_used):
            names_used.update(the_set)
            for key in the_set:
                if key not in name_origins:
                    name_origins[key] = set()
                name_origins[key].add(question.from_source)
        fields_used.update(question.fields_used)
        for key in question.fields_used:
            if key not in field_origins:
                field_origins[key] = set()
            field_origins[key].add(question.from_source)
            # if key == 'advocate':
            #     try:
            #         logmessage("Found advocate in " + question.content.original_text)
            #     except:
            #         logmessage("Found advocate")
    for val in interview.questions:
        names_used.add(val)
        if val not in name_origins:
            name_origins[val] = set()
        for lang in interview.questions[val]:
            for q in interview.questions[val][lang]:
                name_origins[val].add(q.from_source)
        fields_used.add(val)
        if val not in field_origins:
            field_origins[val] = set()
        for lang in interview.questions[val]:
            for q in interview.questions[val][lang]:
                field_origins[val].add(q.from_source)
    needed_names = set()
    find_needed_names(interview, needed_names)
    functions = set()
    modules = set()
    classes = set()
    name_info = copy.deepcopy(base_name_info)
    area = SavedFile(current_user.id, fix=True, section='playgroundtemplate')
    templates = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    area = SavedFile(current_user.id, fix=True, section='playgroundstatic')
    static = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    area = SavedFile(current_user.id, fix=True, section='playgroundsources')
    sources = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    area = SavedFile(current_user.id, fix=True, section='playgroundmodules')
    avail_modules = sorted([re.sub(r'.py$', '', f) for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    for val in user_dict:
        if type(user_dict[val]) is types.FunctionType:
            functions.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val) + '()', 'tag': str(val) + str(inspect.formatargspec(*inspect.getargspec(user_dict[val])))}
        elif type(user_dict[val]) is types.ModuleType:
            modules.add(val)
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val)}
        elif type(user_dict[val]) is types.TypeType or type(user_dict[val]) is types.ClassType:
            classes.add(val)
            bases = list()
            for x in list(user_dict[val].__bases__):
                if x.__name__ != 'DAObject':
                    bases.append(x.__name__)
            methods = inspect.getmembers(user_dict[val], predicate=lambda x: public_method(x, user_dict[val]))
            method_list = list()
            for name, value in methods:
                method_list.append({'insert': '.' + str(name) + '()', 'name': str(name), 'doc': noquote(inspect.getdoc(value)), 'tag': '.' + str(name) + str(inspect.formatargspec(*inspect.getargspec(value)))})
            name_info[val] = {'doc': noquote(inspect.getdoc(user_dict[val])), 'name': str(val), 'insert': str(val), 'bases': bases, 'methods': method_list}
    for val in docassemble.base.functions.pickleable_objects(user_dict):
        names_used.add(val)
        if val not in name_info:
            name_info[val] = dict()
        name_info[val]['type'] = user_dict[val].__class__.__name__
        if hasattr(user_dict[val], '__iter__') and not isinstance(user_dict[val], basestring):
            name_info[val]['iterable'] = True
        else:
            name_info[val]['iterable'] = False
    for var in base_name_info:
        if base_name_info[var]['show']:
            names_used.add(var)
    names_used = set([i for i in names_used if not extraneous_var.search(i)])
    for var in ('_internal', '__object_type'):
        names_used.discard(var)
    for var in interview.mlfields:
        names_used.discard(var + '.text')
    if len(interview.mlfields):
        classes.add('DAModel')
        method_list = [{'insert': '.predict()', 'name': 'predict', 'doc': "Generates a prediction based on the 'text' attribute and sets the attributes 'entry_id,' 'predictions,' 'prediction,' and 'probability.'  Called automatically.", 'tag': '.predict(self)'}]
        name_info['DAModel'] = {'doc': 'Applies natural language processing to user input and returns a prediction.', 'name': 'DAModel', 'insert': 'DAModel', 'bases': list(), 'methods': method_list}
    view_doc_text = word("View documentation")
    word_documentation = word("Documentation")
    attr_documentation = word("Show attributes")
    ml_parts = interview.get_ml_store().split(':')
    if len(ml_parts) == 2:
        ml_parts[1] = re.sub(r'^data/sources/ml-|\.json$', '', ml_parts[1])
    else:
        ml_parts = ['_global', '_global']
    for var in documentation_dict:
        if var not in name_info:
            name_info[var] = dict()
        if 'doc' in name_info[var] and name_info[var]['doc'] is not None:
            name_info[var]['doc'] += '<br>'
        else:
            name_info[var]['doc'] = ''
        name_info[var]['doc'] += "<a target='_blank' href='" + documentation_dict[var] + "'>" + view_doc_text + "</a>"
    for var in name_info:
        if 'methods' in name_info[var]:
            for method in name_info[var]['methods']:
                if var + '.' + method['name'] in documentation_dict:
                    if method['doc'] is None:
                        method['doc'] = ''
                    else:
                        method['doc'] += '<br>'
                    method['doc'] += "<a target='_blank' href='" + documentation_dict[var + '.' + method['name']] + "'>" + view_doc_text + "</a>"                
    content = ''
    if has_error and show_messages:
        error_style = 'danger'
        if error_type is DAErrorNoEndpoint:
            error_style = 'warning'
            message_to_use = title_documentation['incomplete']['doc']
        elif error_type is DAErrorCompileError:
            message_to_use = title_documentation['compilefail']['doc']
        elif error_type is DAErrorMissingVariable:
            message_to_use = error_message
        else:
            message_to_use = title_documentation['generic error']['doc']
        content += '\n                  <tr><td class="playground-warning-box"><div class="alert alert-' + error_style + '">' + message_to_use + '</div></td></tr>'
    vocab_dict = dict()
    vocab_set = (names_used | functions | classes | modules | fields_used | set([key for key in base_name_info if not re.search(r'\.', key)]) | set([key for key in name_info if not re.search(r'\.', key)]) | set(templates) | set(static) | set(sources) | set(avail_modules) | set(interview.images.keys()))
    vocab_set = set([i for i in vocab_set if not extraneous_var.search(i)])
    names_used = names_used.difference( functions | classes | modules | set(avail_modules) )
    undefined_names = names_used.difference(fields_used | set(base_name_info.keys()) | set([x for x in names_used if '.' in x]))
    implicitly_defined = set()
    for var in fields_used:
        the_var = var
        while '.' in the_var:
            the_var = re.sub(r'(.*)\..*$', r'\1', the_var)
            implicitly_defined.add(the_var)
    for var in ('_internal', '__object_type'):
        undefined_names.discard(var)
        vocab_set.discard(var)
    for var in [x for x in undefined_names if x.endswith(']')]:
        undefined_names.discard(var)
    names_used = names_used.difference( undefined_names )
    if return_json:
        if len(names_used):
            has_parent = dict()
            has_children = set()
            for var in names_used:
                parent = re.sub(r'[\.\[].*', '', var)
                if parent != var:
                    has_parent[var] = parent
                    has_children.add(parent)
            var_list = list()
            for var in sorted(names_used):
                var_trans = re.sub(r'\[[0-9]\]', '[i]', var)
                var_trans = re.sub(r'\[i\](.*)\[i\](.*)\[i\]', r'[i]\1[j]\2[k]', var_trans)
                var_trans = re.sub(r'\[i\](.*)\[i\]', r'[i]\1[j]', var_trans)
                info = dict(var=var, to_insert=var)
                if var_trans != var:
                    info['var_base'] = var_trans
                if var in has_parent:
                    info['hide'] = True
                else:
                    info['hide'] = False
                if var in base_name_info:
                    if not base_name_info[var]['show']:
                        continue
                if var in documentation_dict or var in base_name_info:
                    info['var_type'] = 'builtin'
                elif var not in fields_used and var not in implicitly_defined and var_trans not in fields_used and var_trans not in implicitly_defined:
                    info['var_type'] = 'not_used'
                elif var not in needed_names:
                    info['var_type'] = 'possibly_not_used'
                else:
                    info['var_type'] = 'default'
                if var in name_info and 'type' in name_info[var] and name_info[var]['type']:
                    info['class_name'] = name_info[var]['type']
                elif var in interview.mlfields:
                    info['class_name'] = 'DAModel'
                if var in name_info and 'iterable' in name_info[var]:
                    info['iterable'] = name_info[var]['iterable']
                if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                if var in interview.mlfields:
                    if 'ml_group' in interview.mlfields[var] and not interview.mlfields[var]['ml_group'].uses_mako:
                        (ml_package, ml_file, ml_group_id) = get_ml_info(interview.mlfields[var]['ml_group'].original_text, ml_parts[0], ml_parts[1])
                        info['train_link'] = url_for('train', package=ml_package, file=ml_file, group_id=ml_group_id)
                    else:
                        info['train_link'] = url_for('train', package=ml_parts[0], file=ml_parts[1], group_id=var)
                var_list.append(info)
        functions_list = list()
        if len(functions):
            for var in sorted(functions):
                info = dict(var=var, to_insert=name_info[var]['insert'], name=name_info[var]['tag'])
                if 'doc' in name_info[var] and name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                functions_list.append(info)
        classes_list = list()
        if len(classes):
            for var in sorted(classes):
                info = dict(var=var, to_insert=name_info[var]['insert'], name=name_info[var]['name'])
                if name_info[var]['bases']:
                    info['bases'] = name_info[var]['bases']
                if 'doc' in name_info[var] and name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                if 'methods' in name_info[var] and len(name_info[var]['methods']):
                    info['methods'] = list()
                    for method_item in name_info[var]['methods']:
                        method_info = dict(name=method_item['name'], to_insert=method_item['insert'], tag=method_item['tag'])
                        if method_item['doc']:
                            method_info['doc_content'] = method_item['doc']
                            method_info['doc_title'] = word_documentation
                        info['methods'].append(method_info)
                classes_list.append(info)
        modules_list = list()
        if len(modules):
            for var in sorted(modules):
                info = dict(var=var, to_insert=name_info[var]['insert'])
                if name_info[var]['doc']:
                    info['doc_content'] = name_info[var]['doc']
                    info['doc_title'] = word_documentation
                modules_list.append(info)
        modules_available_list = list()
        if len(avail_modules):
            for var in sorted(avail_modules):
                info = dict(var=var, to_insert="." + var)
                modules_available_list.append(info)
        templates_list = list()
        if len(templates):
            for var in sorted(templates):
                info = dict(var=var, to_insert=var)
                templates_list.append(info)
        sources_list = list()
        if len(sources):
            for var in sorted(sources):
                info = dict(var=var, to_insert=var)
                sources_list.append(info)
        images_list = list()
        if len(interview.images):
            for var in sorted(interview.images):
                info = dict(var=var, to_insert=var)
                the_ref = get_url_from_file_reference(interview.images[var].get_reference())
                if the_ref:
                    info['url'] = the_ref
                images_list.append(info)
        return dict(undefined_names=list(sorted(undefined_names)), var_list=var_list, functions_list=functions_list, classes_list=classes_list, modules_list=modules_list, modules_available_list=modules_available_list, templates_list=templates_list, sources_list=sources_list, images_list=images_list), sorted(vocab_set)
    if len(undefined_names):
        content += '\n                  <tr><td><h4>' + word('Undefined names') + infobutton('undefined') + '</h4></td></tr>'
        for var in sorted(undefined_names):
            content += '\n                  <tr><td>' + search_button(var, field_origins, name_origins, interview.source, all_sources) + '<a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-danger btn-sm playground-variable">' + var + '</a></td></tr>'
            vocab_dict[var] = var
    if len(names_used):
        content += '\n                  <tr><td><h4>' + word('Variables') + infobutton('variables') + '</h4></td></tr>'
        has_parent = dict()
        has_children = set()
        for var in names_used:
            parent = re.sub(r'[\.\[].*', '', var)
            if parent != var:
                has_parent[var] = parent
                has_children.add(parent)
        in_nest = False
        for var in sorted(names_used):
            var_trans = re.sub(r'\[[0-9]\]', '[i]', var)
            var_trans = re.sub(r'\[i\](.*)\[i\](.*)\[i\]', r'[i]\1[j]\2[k]', var_trans)
            var_trans = re.sub(r'\[i\](.*)\[i\]', r'[i]\1[j]', var_trans)
            if var in has_parent:
                hide_it = ' style="display: none" data-parent="' + noquote(has_parent[var]) + '"'
            else:
                hide_it = ''
            if var in base_name_info:
                if not base_name_info[var]['show']:
                    continue
            if var in documentation_dict or var in base_name_info:
                class_type = 'info'
                title = 'title=' + json.dumps(word("Special variable")) + ' '
            elif var not in fields_used and var not in implicitly_defined and var_trans not in fields_used and var_trans not in implicitly_defined:
                class_type = 'default'
                title = 'title=' + json.dumps(word("Possibly not defined")) + ' '
            elif var not in needed_names:
                class_type = 'warning'
                title = 'title=' + json.dumps(word("Possibly not used")) + ' '
            else:
                class_type = 'primary'
                title = ''
            content += '\n                  <tr' + hide_it + '><td>' + search_button(var, field_origins, name_origins, interview.source, all_sources) + '<a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" ' + title + 'class="btn btn-sm btn-' + class_type + ' playground-variable">' + var + '</a>'
            vocab_dict[var] = var
            if var in has_children:
                content += '&nbsp;<a tabindex="0" class="dashowattributes" role="button" data-name="' + noquote(var) + '" title=' + json.dumps(attr_documentation) + '><i class="fas fa-ellipsis-h"></i></a>'
            if var in name_info and 'type' in name_info[var] and name_info[var]['type']:
                content +='&nbsp;<span data-ref="' + noquote(name_info[var]['type']) + '" class="daparenthetical">(' + name_info[var]['type'] + ')</span>'
            elif var in interview.mlfields:
                content +='&nbsp;<span data-ref="DAModel" class="daparenthetical">(DAModel)</span>'
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title=' + json.dumps(word_documentation) + ' data-selector="true" data-title="' + var + '"><i class="fas fa-info-circle"></i></a>'
            if var in interview.mlfields:
                if 'ml_group' in interview.mlfields[var] and not interview.mlfields[var]['ml_group'].uses_mako:
                    (ml_package, ml_file, ml_group_id) = get_ml_info(interview.mlfields[var]['ml_group'].original_text, ml_parts[0], ml_parts[1])
                    content += '&nbsp;<a class="datrain" target="_blank" href="' + url_for('train', package=ml_package, file=ml_file, group_id=ml_group_id) + '" title=' + json.dumps(word("Train")) + '><i class="fas fa-graduation-cap"></i></a>'
                else:
                    content += '&nbsp;<a class="datrain" target="_blank" href="' + url_for('train', package=ml_parts[0], file=ml_parts[1], group_id=var) + '" title=' + json.dumps(word("Train")) + '><i class="fas fa-graduation-cap"></i></a>'
            content += '</td></tr>'
        if len(all_sources):
            content += search_key
            content += '\n                <tr><td>'
            content += '\n                  <ul>'
            for path in sorted([x.path for x in all_sources]):
                content += '\n                    <li><a target="_blank" href="' + url_for('view_source', i=path)+ '">' + path + '<a></li>'
            content += '\n                  </ul>'
            content += '\n                </td></tr>'
    if len(functions):
        content += '\n                  <tr><td><h4>' + word('Functions') + infobutton('functions') + '</h4></td></tr>'
        for var in sorted(functions):
            content += '\n                  <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="btn btn-sm btn-warning playground-variable">' + name_info[var]['tag'] + '</a>'
            vocab_dict[var] = name_info[var]['insert']
            if var in name_info and 'doc' in name_info[var] and name_info[var]['doc']:
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title=' + json.dumps(word_documentation) + ' data-selector="true" data-title="' + var + '"><i class="fas fa-info-circle"></i></a>'
            content += '</td></tr>'
    if len(classes):
        content += '\n                  <tr><td><h4>' + word('Classes') + infobutton('classes') + '</h4></td></tr>'
        for var in sorted(classes):
            content += '\n                  <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="btn btn-sm btn-info playground-variable">' + name_info[var]['name'] + '</a>'
            vocab_dict[var] = name_info[var]['insert']
            if name_info[var]['bases']:
                content += '&nbsp;<span data-ref="' + noquote(name_info[var]['bases'][0]) + '" class="daparenthetical">(' + name_info[var]['bases'][0] + ')</span>'
            if name_info[var]['doc']:
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title=' + json.dumps(word_documentation) + ' data-selector="true" data-title="' + var + '"><i class="fas fa-info-circle"></i></a>'
            if len(name_info[var]['methods']):
                content += '&nbsp;<a tabindex="0" class="dashowmethods" role="button" data-showhide="XMETHODX' + var + '" title=' + json.dumps(word('Methods')) + '><i class="fas fa-cog"></i></a>'
                content += '<div style="display: none;" id="XMETHODX' + var + '"><table><tbody>'
                for method_info in name_info[var]['methods']:
                    content += '<tr><td><a tabindex="0" data-name="' + noquote(method_info['name']) + '" data-insert="' + noquote(method_info['insert']) + '" class="btn btn-sm btn-warning playground-variable">' + method_info['tag'] + '</a>'
                    #vocab_dict[method_info['name']] = method_info['insert']
                    if method_info['doc']:
                        content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + method_info['doc'] + '" title=' + json.dumps(word_documentation) + ' data-selector="true" data-title="' + noquote(method_info['name']) + '"><i class="fas fa-info-circle"></i></a>'
                    content += '</td></tr>'
                content += '</tbody></table></div>'
            content += '</td></tr>'
    if len(modules):
        content += '\n                  <tr><td><h4>' + word('Modules defined') + infobutton('modules') + '</h4></td></tr>'
        for var in sorted(modules):
            content += '\n                  <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(name_info[var]['insert']) + '" class="btn btn-sm btn-success playground-variable">' + name_info[var]['name'] + '</a>'
            vocab_dict[var] = name_info[var]['insert']
            if name_info[var]['doc']:
                content += '&nbsp;<a tabindex="0" class="dainfosign" role="button" data-container="body" data-toggle="popover" data-placement="auto" data-content="' + name_info[var]['doc'] + '" title=' + json.dumps(word_documentation) + ' data-selector="true" data-title="' + noquote(var) + '"><i class="fas fa-info-circle"></i></a>'
            content += '</td></tr>'
    if len(avail_modules):
        content += '\n                  <tr><td><h4>' + word('Modules available in Playground') + infobutton('playground_modules') + '</h4></td></tr>'
        for var in avail_modules:
            content += '\n                  <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert=".' + noquote(var) + '" class="btn btn-sm btn-success playground-variable">.' + noquote(var) + '</a>'
            vocab_dict[var] = var
            content += '</td></tr>'
    if len(templates):
        content += '\n                  <tr><td><h4>' + word('Templates') + infobutton('templates') + '</h4></td></tr>'
        for var in templates:
            content += '\n                  <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-secondary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            content += '</td></tr>'
    if len(static):
        content += '\n                  <tr><td><h4>' + word('Static files') + infobutton('static') + '</h4></td></tr>'
        for var in static:
            content += '\n                  <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-secondary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            content += '</td></tr>'
    if len(sources):
        content += '\n                  <tr><td><h4>' + word('Source files') + infobutton('sources') + '</h4></td></tr>'
        for var in sources:
            content += '\n                  <tr><td><a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-secondary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            content += '</td></tr>'
    if len(interview.images):
        content += '\n                  <tr><td><h4>' + word('Decorations') + infobutton('decorations') + '</h4></td></tr>'
        if cloud and len(interview.images) > 10:
            show_images = False
        else:
            show_images = True
        for var in sorted(interview.images):
            content += '\n                  <tr><td>'
            the_ref = get_url_from_file_reference(interview.images[var].get_reference())
            if the_ref is None:
                content += '<a tabindex="0" title=' + json.dumps(word("This image file does not exist")) + ' data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-danger playground-variable">' + noquote(var) + '</a>'
            else:
                if show_images:
                    content += '<img class="daimageicon" src="' + the_ref + '">&nbsp;'
                content += '<a tabindex="0" data-name="' + noquote(var) + '" data-insert="' + noquote(var) + '" class="btn btn-sm btn-primary playground-variable">' + noquote(var) + '</a>'
            vocab_dict[var] = var
            content += '</td></tr>'
    if show_messages:
        content += "\n                  <tr><td><br><em>" + word("Type Ctrl-space to autocomplete.") + "</em></td><tr>"
    if show_jinja_help:
        content += "\n                  <tr><td><h4 class=\"mt-2\">" + word("Using Jinja2") + infobutton('jinja2') + "</h4>\n                  " + re.sub("table-striped", "table-bordered", docassemble.base.util.markdown_to_html(word("Jinja2 help template"), trim=False, do_terms=False, indent=18)) + "</td><tr>"
    for item in base_name_info:
        if item not in vocab_dict and not base_name_info.get('exclude', False):
            vocab_dict[item] = base_name_info.get('insert', item)
    return content, sorted(vocab_set), vocab_dict

def make_png_for_pdf(doc, prefix, page=None):
    if prefix == 'page':
        resolution = PNG_RESOLUTION
    else:
        resolution = PNG_SCREEN_RESOLUTION
    task = docassemble.webapp.worker.make_png_for_pdf.delay(doc, prefix, resolution, session['uid'], PDFTOPPM_COMMAND, page=page)
    return task.id

def fg_make_png_for_pdf(doc, prefix, page=None):
    if prefix == 'page':
        resolution = PNG_RESOLUTION
    else:
        resolution = PNG_SCREEN_RESOLUTION
    docassemble.base.ocr.make_png_for_pdf(doc, prefix, resolution, PDFTOPPM_COMMAND, page=page)

def fg_make_png_for_pdf_path(path, prefix, page=None):
    if prefix == 'page':
        resolution = PNG_RESOLUTION
    else:
        resolution = PNG_SCREEN_RESOLUTION
    docassemble.base.ocr.make_png_for_pdf_path(path, prefix, resolution, PDFTOPPM_COMMAND, page=page)

def fg_make_pdf_for_word_path(path, extension):
    success = docassemble.base.pandoc.word_to_pdf(path, extension, path + ".pdf")
    if not success:
        raise DAError("fg_make_pdf_for_word_path: unable to make PDF from " + path + " using extension " + extension + " and writing to " + path + ".pdf")
    
def task_ready(task_id):
    result = docassemble.webapp.worker.workerapp.AsyncResult(id=task_id)
    if result.ready():
        return True
    return False

def wait_for_task(task_id, timeout=None):
    if timeout is None:
        timeout = 3
    #logmessage("wait_for_task: starting")
    try:
        result = docassemble.webapp.worker.workerapp.AsyncResult(id=task_id)
        if result.ready():
            #logmessage("wait_for_task: was ready")
            return True
        #logmessage("wait_for_task: waiting for task to complete")
        result.get(timeout=timeout)
        #logmessage("wait_for_task: returning true")
        return True
    except docassemble.webapp.worker.celery.exceptions.TimeoutError as the_error:
        logmessage("wait_for_task: timed out")
        return False
    except Exception as the_error:
        logmessage("wait_for_task: got error: " + str(the_error))
        return False

# def make_image_files(path):
#     if PDFTOPPM_COMMAND is not None:
#         args = [PDFTOPPM_COMMAND, '-r', str(PNG_RESOLUTION), '-png', path, path + 'page']
#         result = call(args)
#         if result > 0:
#             raise DAError("Call to pdftoppm failed")
#         args = [PDFTOPPM_COMMAND, '-r', str(PNG_SCREEN_RESOLUTION), '-png', path, path + 'screen']
#         result = call(args)
#         if result > 0:
#             raise DAError("Call to pdftoppm failed")
#     return

def trigger_update(except_for=None):
    logmessage("trigger_update: except_for is " + str(except_for) + " and hostname is " + hostname)
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url and not (except_for and host.hostname == except_for):
                if host.hostname == hostname:
                    the_url = 'http://localhost:9001'
                    logmessage("trigger_update: using http://localhost:9001")
                else:
                    the_url = host.url
                args = [SUPERVISORCTL, '-s', the_url, 'start update']
                result = call(args)
                if result == 0:
                    logmessage("trigger_update: sent reset to " + str(host.hostname))
                else:
                    logmessage("trigger_update: call to supervisorctl on " + str(host.hostname) + " was not successful")
    return

def restart_on(host):
    logmessage("restart_on: " + str(host.hostname))
    if host.hostname == hostname:
        the_url = 'http://localhost:9001'
    else:
        the_url = host.url
    if re.search(r':(web|all):', host.role):
        args = [SUPERVISORCTL, '-s', the_url, 'start reset']
        result = call(args)
        if result == 0:
            logmessage("restart_on: sent reset to " + str(host.hostname))
        else:
            logmessage("restart_on: call to supervisorctl with reset on " + str(host.hostname) + " was not successful")
    return

def restart_all():
    for interview_path in [x for x in r.keys('da:interviewsource:*')]:
        r.delete(interview_path)
    restart_others()
    restart_this()
    return

def restart_this():
    logmessage("restart_this: hostname is " + str(hostname))
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url:
                logmessage("restart_this: considering " + str(host.hostname) + " against " + str(hostname))
                if host.hostname == hostname:
                    restart_on(host)
            #else:
            #    logmessage("restart_this: unable to get host url")
    else:
        logmessage("restart_this: touching wsgi file")
        wsgi_file = WEBAPP_PATH
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a'):
                os.utime(wsgi_file, None)
    return

def restart_others():
    logmessage("restart_others: starting")
    if USING_SUPERVISOR:
        for host in Supervisors.query.all():
            if host.url:
                if host.hostname != hostname:
                    restart_on(host)
            #else:
            #    logmessage("restart_others: unable to get host url")
    return

def current_info(yaml=None, req=None, action=None, location=None, interface='web'):
    #logmessage("interface is " + str(interface))
    if current_user.is_authenticated and not current_user.is_anonymous:
        ext = dict(email=current_user.email, roles=[role.name for role in current_user.roles], the_user_id=current_user.id, theid=current_user.id, firstname=current_user.first_name, lastname=current_user.last_name, nickname=current_user.nickname, country=current_user.country, subdivisionfirst=current_user.subdivisionfirst, subdivisionsecond=current_user.subdivisionsecond, subdivisionthird=current_user.subdivisionthird, organization=current_user.organization, timezone=current_user.timezone, language=current_user.language)
    else:
        ext = dict(email=None, the_user_id='t' + str(session.get('tempuser', None)), theid=session.get('tempuser', None), roles=list())
    headers = dict()
    if req is None:
        url = 'http://localhost'
        url_root = 'http://localhost'
        secret = None
        clientip = None
        method = None
        unique_id = '0'
    else:
        url = req.base_url
        url_root = req.url_root
        secret = req.cookies.get('secret', None)
        for key, value in req.headers.iteritems():
            headers[key] = value
        clientip = req.remote_addr
        method = req.method
        unique_id = str(request.cookies.get('session'))[5:15]
        if unique_id == '':
            if current_user.is_authenticated and not current_user.is_anonymous and current_user.email:
                unique_id = str(current_user.email)
            else:
                unique_id = random_string(10)
    if secret is not None:
        secret = str(secret)
    return_val = {'session': session.get('uid', None), 'secret': secret, 'yaml_filename': yaml, 'interface': interface, 'url': url, 'url_root': url_root, 'encrypted': session.get('encrypted', True), 'user': {'is_anonymous': current_user.is_anonymous, 'is_authenticated': current_user.is_authenticated, 'session_uid': unique_id}, 'headers': headers, 'clientip': clientip, 'method': method}
    if action is not None:
        #logmessage("current_info: setting an action " + repr(action))
        return_val.update(action)
        # return_val['orig_action'] = action['action']
        # return_val['orig_arguments'] = action['arguments']
    if location is not None:
        ext['location'] = location
    else:
        ext['location'] = None
    return_val['user'].update(ext)
    return(return_val)

def html_escape(text):
    text = re.sub('&', '&amp;', text)
    text = re.sub('<', '&lt;', text)
    text = re.sub('>', '&gt;', text)
    return text;

def indent_by(text, num):
    if not text:
        return ""
    return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"
    
def call_sync():
    if not USING_SUPERVISOR:
        return
    args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'start', 'sync']
    result = call(args)
    if result == 0:
        pass
        #logmessage("call_sync: sent message to " + hostname)
    else:
        logmessage("call_sync: call to supervisorctl on " + hostname + " was not successful")
        abort(404)
    in_process = 1
    counter = 10
    check_args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'status', 'sync']
    while in_process == 1 and counter > 0:
        output, err = Popen(check_args, stdout=PIPE, stderr=PIPE).communicate()
        if not re.search(r'RUNNING', output):
            in_process = 0
        else:
            time.sleep(1)
        counter -= 1
    return

def formatted_current_time():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime('%H:%M:%S %Z')

def formatted_current_date():
    if current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(the_timezone).strftime("%Y-%m-%d")

class Object(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    pass

class FakeUser(object):
    pass

class FakeRole(object):
    pass

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'].get(provider_name, dict())
        self.consumer_id = credentials.get('id', None)
        self.consumer_secret = credentials.get('secret', None)
        self.consumer_domain = credentials.get('domain', None)

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=None,
            access_token_url=None,
            base_url=None
        )
    def authorize(self):
        result = urlparse.parse_qs(request.data)
        logmessage("GoogleSignIn, args: " + str([str(arg) + ": " + str(request.args[arg]) for arg in request.args]))
        logmessage("GoogleSignIn, request: " + str(request.data))
        session['google_id'] = result.get('id', [None])[0]
        session['google_email'] = result.get('email', [None])[0]
        session['google_name'] = result.get('name', [None])[0]
        response = make_response(json.dumps('Successfully connected user.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # oauth_session = self.service.get_auth_session(
        #     data={'code': request.args['code'],
        #           'grant_type': 'authorization_code',
        #           'redirect_uri': self.get_callback_url()}
        # )
        return response
    
    def callback(self):
        #logmessage("GoogleCallback, args: " + str([str(arg) + ": " + str(request.args[arg]) for arg in request.args]))
        #logmessage("GoogleCallback, request: " + str(request.data))
        email = session.get('google_email', None)
        google_id = session.get('google_id', None)
        google_name = session.get('google_name', None)
        if 'google_id' in session:
            del session['google_id']
        if 'google_email' in session:
            del session['google_email']
        if 'google_name' in session:
            del session['google_name']
        if email is not None and google_id is not None:
            return (
                'google$' + str(google_id),
                email.split('@')[0],
                email,
                {'name': google_name}
            )
        else:
            raise Exception("Could not get Google authorization information")

class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://www.facebook.com/v3.0/dialog/oauth',           
            access_token_url='https://graph.facebook.com/v3.0/oauth/access_token',
            base_url='https://graph.facebook.com/v3.0'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='public_profile,email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None, None
        oauth_session = self.service.get_auth_session(
            decoder=json.loads,
            data={'code': request.args['code'],
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me', params={'fields': 'id,name,first_name,middle_name,last_name,name_format,email'}).json()
        #logmessage("Facebook: returned " + json.dumps(me))
        return (
            'facebook$' + str(me['id']),
            me.get('email').split('@')[0],
            me.get('email'),
            {'first': me.get('first_name', None),
             'middle': me.get('middle_name', None),
             'last': me.get('last_name', None),
             'name': me.get('name', None),
             'name_format': me.get('name_format', None)}
        )

class AzureSignIn(OAuthSignIn):
    def __init__(self):
        super(AzureSignIn, self).__init__('azure')
        self.service = OAuth2Service(
            name='azure',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://login.microsoftonline.com/common/oauth2/authorize',
            access_token_url='https://login.microsoftonline.com/common/oauth2/token',
            base_url='https://graph.microsoft.com/v1.0/'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            client_id=self.consumer_id,
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None, None
        oauth_session = self.service.get_auth_session(
            decoder=json.loads,
            data={'code': request.args['code'],
                  'client_id': self.consumer_id,
                  'client_secret': self.consumer_secret,
                  'resource': 'https://graph.microsoft.com/',
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        return (
            'azure$' + str(me['id']),
            me.get('mail').split('@')[0],
            me.get('mail'),
            {'first_name': me.get('givenName', None),
             'last_name': me.get('surname', None),
             'name': me.get('displayName', me.get('userPrincipalName', None))}
        )
    
class Auth0SignIn(OAuthSignIn):
    def __init__(self):
        super(Auth0SignIn, self).__init__('auth0')
        if self.consumer_domain is None:
            raise Exception("To use Auth0, you need to set your domain in the configuration.")
        self.service = OAuth2Service(
            name='auth0',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://' + self.consumer_domain + '/authorize',
            access_token_url='https://' + self.consumer_domain + '/oauth/token',
            base_url='https://' + self.consumer_domain
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            scope='openid profile email',
            audience='https://' + self.consumer_domain + '/userinfo',
            redirect_uri=self.get_callback_url())
        )
    def callback(self):
        if 'code' not in request.args:
            return None, None, None, None
        oauth_session = self.service.get_auth_session(
            decoder=json.loads,
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('userinfo').json()
        #logmessage("Auth0 returned " + json.dumps(me))
        user_id = me.get('sub', me.get('user_id'))
        social_id = 'auth0$' + str(user_id)
        username = me.get('name')
        email = me.get('email')
        if user_id is None or username is None or email is None:
            raise Exception("Error: could not get necessary information from Auth0")
        return social_id, username, email, {'name': me.get('name', None)}

class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )
    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))
    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json', params={'skip_status': 'true', 'include_email': 'true', 'include_entites': 'false'}).json()
        #logmessage("Twitter returned " + json.dumps(me))
        social_id = 'twitter$' + str(me.get('id_str'))
        username = me.get('screen_name')
        email = me.get('email')
        return social_id, username, email, {'name': me.get('name', None)}

@flaskbabel.localeselector
def get_locale():
    translations = [str(translation) for translation in flaskbabel.list_translations()]
    return request.accept_languages.best_match(translations)

def get_user_object(user_id):
    the_user = UserModel.query.filter_by(id=user_id).first()
    return the_user

@lm.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

# @app.route('/post_login', methods=['GET'])
# def post_login():
#     #logmessage("post_login")
#     response = redirect(request.args.get('next', url_for('interview_list')))
#     if 'newsecret' in session:
#         response.set_cookie('secret', session['newsecret'])
#         #logmessage("post_login: setting the cookie to " + session['newsecret'])
#         del session['newsecret']
#     # else:
#     #     logmessage("post_login: no newsecret")
#     return response

@app.route('/headers', methods=['POST', 'GET'])
@csrf.exempt
def show_headers():
    return jsonify(headers=dict(request.headers), ipaddress=request.remote_addr)

@app.route('/authorize/<provider>', methods=['POST', 'GET'])
@csrf.exempt
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
@csrf.exempt
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('interview_list'))
    # for argument in request.args:
    #     logmessage("argument " + str(argument) + " is " + str(request.args[argument]))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, name_data = oauth.callback()
    if social_id is None:
        flash(word('Authentication failed.'), 'error')
        return redirect(url_for('interview_list'))
    user = UserModel.query.filter_by(social_id=social_id).first()
    if not user:
        user = UserModel.query.filter_by(email=email).first()
    if user and user.social_id is not None and user.social_id.startswith('local'):
        flash(word('There is already a username and password on this system with the e-mail address') + " " + str(email) + ".  " + word("Please log in."), 'error')
        return redirect(url_for('user.login'))
    if not user:
        user = UserModel(social_id=social_id, nickname=username, email=email, active=True)
        if 'first_name' in name_data and 'last_name' in name_data and name_data['first_name'] is not None and name_data['last_name'] is not None:
            user.first_name = name_data['first_name']
            user.last_name = name_data['last_name']
        elif 'name' in name_data and name_data['name'] is not None and ' ' in name_data['name']:
            user.first_name = re.sub(r' .*', '', name_data['name'])
            user.last_name = re.sub(r'.* ', '', name_data['name'])
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=False)
    if 'i' in session and 'uid' in session:
        if 'tempuser' in session:
            sub_temp_user_dict_key(session['tempuser'], user.id)
        save_user_dict_key(session['uid'], session['i'], priors=True)
        session['key_logged'] = True
    #logmessage("oauth_callback: calling substitute_secret")
    secret = substitute_secret(str(request.cookies.get('secret', None)), pad_to_16(MD5Hash(data=social_id).hexdigest()))
    response = redirect(url_for('interview_list'))
    response.set_cookie('secret', secret)
    return response

@app.route('/phone_login', methods=['POST', 'GET'])
def phone_login():
    if not app.config['USE_PHONE_LOGIN']:
        abort(404)
    form = PhoneLoginForm(request.form)
    #next = request.args.get('next', url_for('interview_list'))
    if request.method == 'POST' and form.submit.data:
        ok = True
        if form.validate():
            phone_number = form.phone_number.data
            if docassemble.base.functions.phone_number_is_valid(phone_number):
                phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
            else:
                ok = False
        else:
            ok = False
        if ok:
            verification_code = random_digits(daconfig['verification code digits'])
            message = word("Your verification code is") + " " + str(verification_code) + "."
            user_agent = request.headers.get('User-Agent', '')
            if detect_mobile.search(user_agent):
                message += '  ' + word("You can also follow this link: ") + url_for('phone_login_verify', _external=True, p=phone_number, c=verification_code)
            tracker_prefix = 'da:phonelogin:ip:' + str(request.remote_addr) + ':phone:'
            tracker_key = tracker_prefix + str(phone_number)
            pipe = r.pipeline()
            pipe.incr(tracker_key)
            pipe.expire(tracker_key, daconfig['ban period'])
            pipe.execute()
            total_attempts = 0
            for key in r.keys(tracker_prefix + '*'):
                val = r.get(key)
                total_attempts += int(val)
            if total_attempts > daconfig['attempt limit']:
                logmessage("IP address " + str(request.remote_addr) + " attempted to log in too many times.")
                flash(word("You have made too many login attempts."), 'error')
                return redirect(url_for('user.login'))
            total_attempts = 0
            for key in r.keys('da:phonelogin:ip:*:phone:' + phone_number):
                val = r.get(key)
                total_attempts += int(val)
            if total_attempts > daconfig['attempt limit']:
                logmessage("Too many attempts were made to log in to phone number " + str(phone_number))
                flash(word("You have made too many login attempts."), 'error')
                return redirect(url_for('user.login'))
            key = 'da:phonelogin:' + str(phone_number) + ':code'
            pipe = r.pipeline()
            pipe.set(key, verification_code)
            pipe.expire(key, daconfig['verification code timeout'])
            pipe.execute()
            #logmessage("Writing code " + str(verification_code) + " to " + key)
            docassemble.base.functions.this_thread.current_info = current_info(req=request)
            success = docassemble.base.util.send_sms(to=phone_number, body=message)
            if success:
                session['phone_number'] = phone_number
                return redirect(url_for('phone_login_verify'))
            else:
                flash(word("There was a problem sending you a text message.  Please log in another way."), 'error')
                return redirect(url_for('user.login'))
        else:
            flash(word("Please enter a valid phone number"), 'error')
    return render_template('flask_user/phone_login.html', form=form, version_warning=None, title=word("Sign in with your mobile phone"), tab_title=word("Sign In"), page_title=word("Sign in"))

@app.route('/pv', methods=['POST', 'GET'])
def phone_login_verify():
    if not app.config['USE_PHONE_LOGIN']:
        abort(404)
    phone_number = session.get('phone_number', request.args.get('p', None))
    if phone_number is None:
        abort(404)
    form = PhoneLoginVerifyForm(request.form)
    form.phone_number.data = phone_number
    if 'c' in request.args and 'p' in request.args:
        submitted = True
        form.verification_code.data = request.args.get('c', None)
    else:
        submitted = False
    if submitted or (request.method == 'POST' and form.submit.data):
        if form.validate():
            social_id = 'phone$' + str(phone_number)
            user = UserModel.query.filter_by(social_id=social_id).first()
            if user and user.active is False:
                flash(word("Your account has been disabled."), 'error')
                return redirect(url_for('user.login'))
            if not user:
                user = UserModel(social_id=social_id, nickname=phone_number, active=True)
                db.session.add(user)
                db.session.commit()
            login_user(user, remember=False)
            r.delete('da:phonelogin:ip:' + str(request.remote_addr) + ':phone:' + phone_number)
            if 'i' in session and 'uid' in session:
                if 'tempuser' in session:
                    sub_temp_user_dict_key(session['tempuser'], user.id)
                save_user_dict_key(session['uid'], session['i'], priors=True)
                session['key_logged'] = True
            secret = substitute_secret(str(request.cookies.get('secret', None)), pad_to_16(MD5Hash(data=social_id).hexdigest()))
            response = redirect(url_for('interview_list'))
            response.set_cookie('secret', secret)
            return response
        else:
            logmessage("IP address " + str(request.remote_addr) + " made a failed login attempt using phone number " + str(phone_number) + ".")
            flash(word("Your verification code is invalid or expired.  Please try again."), 'error')
            return redirect(url_for('user.login'))
    return render_template('flask_user/phone_login_verify.html', form=form, version_warning=None, title=word("Verify your phone"), tab_title=word("Enter code"), page_title=word("Enter code"), description=word("We just sent you a text message with a verification code.  Enter the verification code to proceed."))

@login_required
@app.route('/mfa_setup', methods=['POST', 'GET'])
def mfa_setup():
    if daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    form = MFASetupForm(request.form)
    if request.method == 'POST' and form.submit.data:
        if 'otp_secret' not in session:
            abort(404)
        otp_secret = session['otp_secret']
        del session['otp_secret']
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        totp = pyotp.TOTP(otp_secret)
        if not totp.verify(supplied_verification_code):
            flash(word("Your verification code was invalid."), 'error')
            return redirect(url_for('user_profile_page'))
        user = load_user(current_user.id)
        user.otp_secret = otp_secret
        db.session.commit()
        flash(word("You are now set up with two factor authentication."), 'success')
        return redirect(url_for('user_profile_page'))
    otp_secret = pyotp.random_base32()
    if current_user.email:
        the_name = current_user.email
    else:
        the_name = re.sub(r'.*\$', '', current_user.social_id)
    the_url = pyotp.totp.TOTP(otp_secret).provisioning_uri(the_name, issuer_name=app.config['APP_NAME'])
    im = qrcode.make(the_url, image_factory=qrcode.image.svg.SvgPathImage)
    output = StringIO.StringIO()
    im.save(output)
    the_qrcode = output.getvalue()
    the_qrcode = re.sub("<\?xml version='1.0' encoding='UTF-8'\?>\n", '', the_qrcode)
    the_qrcode = re.sub(r'height="[0-9]+mm" ', '', the_qrcode)
    the_qrcode = re.sub(r'width="[0-9]+mm" ', '', the_qrcode)
    m = re.search(r'(viewBox="[^"]+")', the_qrcode)
    if m:
        viewbox = ' ' + m.group(1)
    else:
        viewbox = ''
    the_qrcode = '<svg class="mfasvg"' + viewbox + '><g transform="scale(1.0)">' + the_qrcode + '</g></svg>'
    session['otp_secret'] = otp_secret
    return render_template('flask_user/mfa_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("Scan the barcode with your phone's authenticator app and enter the verification code."), the_qrcode=Markup(the_qrcode))

@login_required
@app.route('/mfa_reconfigure', methods=['POST', 'GET'])
def mfa_reconfigure():
    if daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    user = load_user(current_user.id)
    if user.otp_secret is None:
        if twilio_config is None:
            return redirect(url_for('mfa_setup'))
        return redirect(url_for('mfa_choose'))
    form = MFAReconfigureForm(request.form)
    if request.method == 'POST':
        if form.reconfigure.data:
            if twilio_config is None:
                return redirect(url_for('mfa_setup'))
            return redirect(url_for('mfa_choose'))
        elif form.disable.data:
            user.otp_secret = None
            db.session.commit()
            flash(word("Your account no longer uses two-factor authentication."), 'success')
            return redirect(url_for('user_profile_page'))
        elif form.cancel.data:
            return redirect(url_for('user_profile_page'))
    return render_template('flask_user/mfa_reconfigure.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("Your account already has two-factor authentication enabled.  Would you like to reconfigure or disable two-factor authentication?"))

@login_required
@app.route('/mfa_choose', methods=['POST', 'GET'])
def mfa_choose():
    if daconfig.get('two factor authentication', False) is not True or current_user.is_anonymous or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    if twilio_config is None:
        return redirect(url_for('mfa_setup'))
    user = load_user(current_user.id)
    form = MFAChooseForm(request.form)
    if request.method == 'POST':
        if form.sms.data:
            return redirect(url_for('mfa_sms_setup'))
        elif form.auth.data:
            return redirect(url_for('mfa_setup'))
        else:
            return redirect(url_for('user_profile_page'))
    return render_template('flask_user/mfa_choose.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=Markup(word("""Which type of two-factor authentication would you like to use?  The first option is to use an authentication app like <a target="_blank" href="https://en.wikipedia.org/wiki/Google_Authenticator">Google Authenticator</a> or <a target="_blank" href="https://authy.com/">Authy</a>.  The second option is to receive a text (SMS) message containing a verification code.""")))

@login_required
@app.route('/mfa_sms_setup', methods=['POST', 'GET'])
def mfa_sms_setup():
    if twilio_config is None or daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
    form = MFASMSSetupForm(request.form)
    user = load_user(current_user.id)
    if request.method == 'GET' and user.otp_secret is not None and user.otp_secret.startswith(':phone:'):
        form.phone_number.data = re.sub(r'^:phone:', '', user.otp_secret)
    if request.method == 'POST' and form.submit.data:
        phone_number = form.phone_number.data
        if docassemble.base.functions.phone_number_is_valid(phone_number):
            phone_number = docassemble.base.functions.phone_number_in_e164(phone_number)
            verification_code = random_digits(daconfig['verification code digits'])
            message = word("Your verification code is") + " " + str(verification_code) + "."
            success = docassemble.base.util.send_sms(to=phone_number, body=message)
            if success:
                session['phone_number'] = phone_number
                key = 'da:mfa:phone:' + str(phone_number) + ':code'
                pipe = r.pipeline()
                pipe.set(key, verification_code)
                pipe.expire(key, daconfig['verification code timeout'])
                pipe.execute()
                return redirect(url_for('mfa_verify_sms_setup'))
            else:
                flash(word("There was a problem sending the text message."), 'error')
                return redirect(url_for('user_profile_page'))
        else:
            flash(word("Invalid phone number."), 'error')            
    return render_template('flask_user/mfa_sms_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word("""Enter your phone number.  A confirmation code will be sent to you."""))

@login_required
@app.route('/mfa_verify_sms_setup', methods=['POST', 'GET'])
def mfa_verify_sms_setup():
    if 'phone_number' not in session or twilio_config is None or daconfig.get('two factor authentication', False) is not True or not current_user.has_role(*daconfig['two factor authentication privileges']) or not current_user.social_id.startswith('local'):
        abort(404)
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
            return redirect(url_for('user_profile_page'))
        if verification_code == supplied_verification_code:
            user = load_user(current_user.id)
            user.otp_secret = ':phone:' + phone_number
            db.session.commit()
            flash(word("You are now set up with two factor authentication."), 'success')
            return redirect(url_for('user_profile_page'))
    return render_template('flask_user/mfa_verify_sms_setup.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=word('We just sent you a text message with a verification code.  Enter the verification code to proceed.'))

@app.route('/mfa_login', methods=['POST', 'GET'])
def mfa_login():
    if daconfig.get('two factor authentication', False) is not True:
        logmessage("mfa_login: two factor authentication not configured")
        abort(404)
    if 'validated_user' not in session:
        logmessage("mfa_login: validated_user not in session")
        abort(404)
    user = load_user(session['validated_user'])
    if user is None or user.otp_secret is None or not user.social_id.startswith('local'):
        logmessage("mfa_login: user not setup for MFA where validated_user was " + str(session['validated_user']))
        abort(404)
    form = MFALoginForm(request.form)
    if not form.next.data:
        form.next.data = _get_safe_next_param('next', url_for('interview_list'))
    if request.method == 'POST' and form.submit.data:
        del session['validated_user']
        fail_key = 'da:failedlogin:ip:' + str(request.remote_addr)
        failed_attempts = r.get(fail_key)
        if failed_attempts is not None and int(failed_attempts) > daconfig['attempt limit']:
            abort(404)
        supplied_verification_code = re.sub(r'[^0-9]', '', form.verification_code.data)
        if user.otp_secret.startswith(':phone:'):
            phone_number = re.sub(r'^:phone:', '', user.otp_secret)
            key = 'da:mfa:phone:' + str(phone_number) + ':code'
            verification_code = r.get(key)
            r.delete(key)
            if verification_code is None or supplied_verification_code != verification_code:
                r.incr(fail_key)
                r.expire(fail_key, 86400)
                flash(word("Your verification code was invalid or expired."), 'error')
                return redirect(url_for('user.login'))
            elif failed_attempts is not None:
                r.delete(fail_key)
        else:
            totp = pyotp.TOTP(user.otp_secret)
            if not totp.verify(supplied_verification_code):
                r.incr(fail_key)
                r.expire(fail_key, 86400)
                flash(word("Your verification code was invalid."), 'error')
                return redirect(url_for('user.login'))
            elif failed_attempts is not None:
                r.delete(fail_key)
        #safe_next = user_manager.make_safe_url_function(form.next.data)
        safe_next = form.next.data
        return flask_user.views._do_login_user(user, safe_next, False)
    description = word("This account uses two-factor authentication.")
    if user.otp_secret.startswith(':phone:'):
        description += "  " + word("Please enter the verification code from the text message we just sent you.")
    else:
        description += "  " + word("Please enter the verification code from your authentication app.")
    return render_template('flask_user/mfa_login.html', form=form, version_warning=None, title=word("Two-factor authentication"), tab_title=word("Authentication"), page_title=word("Authentication"), description=description)

def get_github_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('github', dict())
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('GitHub integration is not configured')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='repo admin:public_key read:user user:email read:org',
        redirect_uri=url_for('github_oauth_callback', _external=True),
        auth_uri='http://github.com/login/oauth/authorize',
        token_uri='https://github.com/login/oauth/access_token',
        access_type='offline',
        prompt='consent')
    return flow

def delete_ssh_keys():
    area = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    area.delete_file('.ssh-private')
    area.delete_file('.ssh-public')
    #area.delete_file('.ssh_command.sh')
    area.finalize()

def get_ssh_keys(email):
    area = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    private_key_file = os.path.join(area.directory, '.ssh-private')
    public_key_file = os.path.join(area.directory, '.ssh-public')
    if not (os.path.isfile(private_key_file) and os.path.isfile(private_key_file)):
        from Crypto.PublicKey import RSA
        key = RSA.generate(4096)
        pubkey = key.publickey()
        area.write_content(key.exportKey('PEM'), filename=private_key_file, save=False)
        area.write_content(pubkey.exportKey('OpenSSH') + " " + str(email) + "\n", filename=public_key_file, save=False)
        area.finalize()
    return (private_key_file, public_key_file)

def get_next_link(resp):
    if 'link' in resp and resp['link']:
        link_info = links_from_header.extract(resp['link'])
        if 'next' in link_info:
            return link_info['next']
    return None

@app.route('/github_menu', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_menu():
    if not app.config['USE_GITHUB']:
        abort(404)
    form = GitHubForm(request.form)
    if request.method == 'POST':
        if form.configure.data:
            return redirect(url_for('github_configure'))
        elif form.unconfigure.data:
            return redirect(url_for('github_unconfigure'))
        elif form.cancel.data:
            return redirect(url_for('user_profile_page'))
    uses_github = r.get('da:using_github:userid:' + str(current_user.id))
    if uses_github:
        description = "Your GitHub integration is currently turned on.  You can disconnect GitHub integration if you no longer wish to use it."
    else:
        description = "If you have a GitHub account, you can turn on GitHub integration.  This will allow you to use GitHub as a version control system for packages from inside the Playground."
    return render_template('pages/github.html', form=form, version_warning=None, title=word("GitHub Integration"), tab_title=word("GitHub"), page_title=word("GitHub"), description=description, uses_github=uses_github, bodyclass='adminbody')

@app.route('/github_configure', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_configure():
    if not app.config['USE_GITHUB']:
        abort(404)
    storage = RedisCredStorage(app='github')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        state_string = random_string(16)
        session['github_next'] = json.dumps(dict(state=state_string, path='github_configure', arguments=request.args))
        flow = get_github_flow()
        uri = flow.step1_get_authorize_url(state=state_string)
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    found = False
    resp, content = http.request("https://api.github.com/user/emails", "GET")
    if int(resp['status']) == 200:
        user_info_list = json.loads(content)
        if len(user_info_list):
            user_info = user_info_list[0]
            if user_info.get('email', None) is None:
                raise DAError("github_configure: could not get e-mail address")
        else:
            raise DAError("github_configure: could not get list of e-mail addresses")
    else:
        raise DAError("github_configure: could not get information about user")
    resp, content = http.request("https://api.github.com/user/keys", "GET")
    if int(resp['status']) == 200:
        for key in json.loads(content):
            if key['title'] == app.config['APP_NAME']:
                found = True
    else:
        raise DAError("github_configure: could not get information about ssh keys")
    while found is False:
        next_link = get_next_link(resp)
        if next_link:
            resp, content = http.request(next_link, "GET")
            if int(resp['status']) == 200:
                for key in json.loads(content):
                    if key['title'] == app.config['APP_NAME']:
                        found = True
            else:
                raise DAError("github_configure: could not get additional information about ssh keys")
        else:
            break
    if found:
        flash(word("Your GitHub integration has already been configured."), 'info')
    if not found:
        (private_key_file, public_key_file) = get_ssh_keys(user_info['email'])
        with open(public_key_file, 'rb') as fp:
            public_key = fp.read()
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(dict(title=app.config['APP_NAME'], key=public_key))
        resp, content = http.request("https://api.github.com/user/keys", "POST", headers=headers, body=body)
        if int(resp['status']) == 201:
            flash(word("GitHub integration was successfully configured."), 'info')
        else:
            raise DAError("github_configure: error setting public key")
    r.set('da:using_github:userid:' + str(current_user.id), 1)
    return redirect(url_for('user_profile_page'))

@app.route('/github_unconfigure', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_unconfigure():
    if not app.config['USE_GITHUB']:
        abort(404)
    storage = RedisCredStorage(app='github')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        state_string = random_string(16)
        session['github_next'] = json.dumps(dict(state=state_string, path='github_unconfigure', arguments=request.args))
        flow = get_github_flow()
        uri = flow.step1_get_authorize_url(state=state_string)
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    found = False
    resp, content = http.request("https://api.github.com/user/keys", "GET")
    if int(resp['status']) == 200:
        for key in json.loads(content):
            if key['title'] == app.config['APP_NAME']:
                found = True
                id_to_remove = key['id']
    else:
        raise DAError("github_configure: could not get information about ssh keys")
    while found is False:
        next_link = get_next_link(resp)
        if next_link:
            resp, content = http.request(next_link, "GET")
            if int(resp['status']) == 200:
                for key in json.loads(content):
                    if key['title'] == app.config['APP_NAME']:
                        found = True
                        id_to_remove = key['id']
            else:
                raise DAError("github_configure: could not get additional information about ssh keys")
        else:
            break
    if found:
        resp, content = http.request("https://api.github.com/user/keys/" + str(id_to_remove), "DELETE")
        if int(resp['status']) != 204:
            raise DAError("github_configure: error deleting public key " + str(id_to_remove) + ": " + str(resp['status']) + " content: " + str(content))
    delete_ssh_keys()
    r.delete('da:github:userid:' + str(current_user.id))
    r.delete('da:using_github:userid:' + str(current_user.id))
    flash(word("GitHub integration was successfully disconnected."), 'info')
    return redirect(url_for('user_profile_page'))

@app.route('/github_oauth_callback', methods=['POST', 'GET'])
@login_required
@roles_required(['admin', 'developer'])
def github_oauth_callback():
    failed = False
    if not app.config['USE_GITHUB']:
        logmessage('github_oauth_callback: server does not use github')
        failed = True
    elif 'github_next' not in session:
        logmessage('github_oauth_callback: github_next not in session')
        failed = True
    if failed is False:
        github_next = json.loads(session['github_next'])
        del session['github_next']
        if 'code' not in request.args or 'state' not in request.args:
            logmessage('github_oauth_callback: code and state not in args')
            failed = True
        elif request.args['state'] != github_next['state']:
            logmessage('github_oauth_callback: state did not match')
            failed = True
    if failed:
        r.delete('da:github:userid:' + str(current_user.id))
        r.delete('da:using_github:userid:' + str(current_user.id))
        abort(404)
    flow = get_github_flow()
    credentials = flow.step2_exchange(request.args['code'])
    storage = RedisCredStorage(app='github')
    storage.put(credentials)
    return redirect(github_next['path'], **github_next['arguments'])

@app.route('/user/google-sign-in')
def google_page():
    return render_template('flask_user/google_login.html', version_warning=None, title=word("Sign In"), tab_title=word("Sign In"), page_title=word("Sign in"))

@app.route("/user/post-sign-in", methods=['GET'])
def post_sign_in():
    session_id = session.get('uid', None)
    return redirect(url_for('interview_list'))

@app.route("/leave", methods=['GET'])
def leave():
    the_exit_page = request.args.get('next', exit_page)
    if current_user.is_authenticated:
        flask_user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
        logout_user()
    delete_session_for_interview()
    #delete_session()
    #response = redirect(exit_page)
    #response.set_cookie('visitor_secret', '', expires=0)
    #response.set_cookie('secret', '', expires=0)
    #response.set_cookie('session', '', expires=0)
    #return response
    return redirect(the_exit_page)

@app.route("/restart_session", methods=['GET'])
def restart_session():
    manual_checkout()
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if session_id is None or yaml_filename is None:
        return redirect(url_for('index'))
    if 'visitor_secret' in request.cookies:
        secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        return redirect(url_for('index'))
    url_args = user_dict['url_args']
    url_args['reset'] = '1'
    return redirect(url_for('index', **url_args))

@app.route("/new_session", methods=['GET'])
def new_session():
    manual_checkout()
    yaml_filename = session.get('i', None)
    if yaml_filename is None:
        return redirect(url_for('index'))
    url_args = dict(i=yaml_filename, new_session='1')
    return redirect(url_for('index', **url_args))

@app.route("/exit", methods=['GET'])
def exit():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    the_exit_page = request.args.get('next', exit_page)
    if 'key_logged' in session:
        del session['key_logged']
    if session_id is not None and yaml_filename is not None:
        manual_checkout()
        obtain_lock(session_id, yaml_filename)
        reset_user_dict(session_id, yaml_filename)
        release_lock(session_id, yaml_filename)
    delete_session_for_interview()
    #delete_session()
    #response = redirect(the_exit_page)
    #response.set_cookie('visitor_secret', '', expires=0)
    #response.set_cookie('secret', '', expires=0)
    #response.set_cookie('session', '', expires=0)
    #return response
    return redirect(the_exit_page)

@app.route("/exit_logout", methods=['GET'])
def exit_logout():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    the_exit_page = request.args.get('next', exit_page)
    if 'key_logged' in session:
        del session['key_logged']
    if session_id is not None and yaml_filename is not None:
        manual_checkout()
        obtain_lock(session_id, yaml_filename)
        reset_user_dict(session_id, yaml_filename)
        release_lock(session_id, yaml_filename)
    if current_user.is_authenticated:
        flask_user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
        logout_user()
    delete_session() # used to be indented
    response = redirect(the_exit_page)
    response.set_cookie('visitor_secret', '', expires=0)
    response.set_cookie('secret', '', expires=0)
    response.set_cookie('session', '', expires=0)
    return response

@app.route("/cleanup_sessions", methods=['GET'])
def cleanup_sessions():
    kv_session.cleanup_sessions()
    return render_template('base_templates/blank.html')

@app.route("/health_check", methods=['GET'])
def health_check():
    return render_template('pages/health_check.html', version_warning=None, content="OK")

@app.route("/checkout", methods=['POST', 'GET'])
def checkout():
    try:
        manual_checkout()
    except:
        return jsonify(success=False)
    return jsonify(success=True)

@app.route("/restart_ajax", methods=['POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_ajax():
    #logmessage("restart_ajax: action is " + str(request.form.get('action', None)))
    #if current_user.has_role('admin', 'developer'):
    #    logmessage("restart_ajax: user has permission")
    #else:
    #    logmessage("restart_ajax: user has no permission")
    if request.form.get('action', None) == 'restart' and current_user.has_role('admin', 'developer'):
        logmessage("restart_ajax: restarting")
        restart_all()
        return jsonify(success=True)

class ChatPartners(object):
    pass

def get_current_chat_log(yaml_filename, session_id, secret, utc=True, timezone=None):
    if timezone is None:
        timezone = get_default_timezone()
    timezone = pytz.timezone(timezone)
    output = []
    if yaml_filename is None or session_id is None:
        return output
    user_cache = user_id_dict()
    for record in ChatLog.query.filter(and_(ChatLog.filename == yaml_filename, ChatLog.key == session_id)).order_by(ChatLog.id).all():
        if record.encrypted:
            try:
                message = decrypt_phrase(record.message, secret)
            except:
                sys.stderr.write("get_current_chat_log: Could not decrypt phrase with secret " + secret + "\n")
                continue
        else:
            message = unpack_phrase(record.message)
        # if record.temp_owner_id:
        #     owner_first_name = None
        #     owner_last_name = None
        #     owner_email = None
        # elif record.owner_id in user_cache:
        #     owner_first_name = user_cache[record.owner_id].first_name
        #     owner_last_name = user_cache[record.owner_id].last_name
        #     owner_email = user_cache[record.owner_id].email
        # else:
        #     sys.stderr.write("get_current_chat_log: Invalid owner ID in chat log\n")
        #     continue
        if record.temp_user_id:
            user_first_name = None
            user_last_name = None
            user_email = None
        elif record.user_id in user_cache:
            user_first_name = user_cache[record.user_id].first_name
            user_last_name = user_cache[record.user_id].last_name
            user_email = user_cache[record.user_id].email
        else:
            sys.stderr.write("get_current_chat_log: Invalid user ID in chat log\n")
            continue
        if utc:
            the_datetime = record.modtime.replace(tzinfo=tz.tzutc())
        else:
            the_datetime = record.modtime.replace(tzinfo=tz.tzutc()).astimezone(timezone)
        output.append(dict(message=message, datetime=the_datetime, user_email=user_email, user_first_name=user_first_name, user_last_name=user_last_name))
    return output

@app.route("/checkin", methods=['POST', 'GET'])
def checkin():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if 'visitor_secret' in request.cookies:
        secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    #session_cookie_id = request.cookies.get('session', None)
    if session_id is None or yaml_filename is None:
        return jsonify(success=False)
    if current_user.is_anonymous:
        the_user_id = 't' + str(session['tempuser'])
        auth_user_id = None
        temp_user_id = int(session['tempuser'])
    else:
        auth_user_id = current_user.id
        the_user_id = current_user.id
        temp_user_id = None
    if request.form.get('action', None) == 'chat_log':
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        if user_dict is None or user_dict['_internal']['livehelp']['availability'] != 'available':
            return jsonify(success=False)
        messages = get_chat_log(user_dict['_internal']['livehelp']['mode'], yaml_filename, session_id, auth_user_id, temp_user_id, secret, auth_user_id, temp_user_id)
        return jsonify(success=True, messages=messages)
    if request.form.get('action', None) == 'checkin':
        commands = list()
        checkin_code = request.form.get('checkinCode', None)
        do_action = request.form.get('do_action', None)
        #logmessage("in checkin")
        if do_action is not None:
            parameters = dict()
            form_parameters = request.form.get('parameters', None)
            if form_parameters is not None:
                parameters = json.loads(form_parameters)
            #logmessage("Action was " + str(do_action) + " and parameters were " + repr(parameters))
            obtain_lock(session_id, yaml_filename)
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
            interview = docassemble.base.interview_cache.get_interview(yaml_filename)
            interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=dict(action=do_action, arguments=parameters)))
            interview_status.checkin = True
            interview.assemble(user_dict, interview_status)
            if interview_status.question.question_type == "backgroundresponse":
                the_response = interview_status.question.backgroundresponse
                if type(the_response) is dict and 'pargs' in the_response and type(the_response['pargs']) is list and len(the_response['pargs']) == 2 and the_response['pargs'][1] in ('javascript', 'flash', 'refresh', 'fields'):
                    commands.append(dict(action=do_action, value=docassemble.base.functions.safe_json(the_response['pargs'][0]), extra=the_response['pargs'][1]))
                elif type(the_response) is list and len(the_response) == 2 and the_response[1] in ('javascript', 'flash', 'refresh', 'fields'):
                    commands.append(dict(action=do_action, value=docassemble.base.functions.safe_json(the_response[0]), extra=the_response[1]))
                elif isinstance(the_response, basestring) and the_response == 'refresh':
                    commands.append(dict(action=do_action, value=docassemble.base.functions.safe_json(None), extra='refresh'))
                else:
                    commands.append(dict(action=do_action, value=docassemble.base.functions.safe_json(the_response), extra='backgroundresponse'))
            elif interview_status.question.question_type == "template" and interview_status.question.target is not None:
                commands.append(dict(action=do_action, value=dict(target=interview_status.question.target, content=docassemble.base.util.markdown_to_html(interview_status.questionText, trim=True)), extra='backgroundresponse'))
            save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, steps=steps)
            release_lock(session_id, yaml_filename)
        peer_ok = False
        help_ok = False
        num_peers = 0
        help_available = 0
        old_chatstatus = session.get('chatstatus', None)
        chatstatus = request.form.get('chatstatus', 'off')
        if old_chatstatus != chatstatus:
            session['chatstatus'] = chatstatus
        obj = dict(chatstatus=chatstatus, i=yaml_filename, uid=session_id, userid=the_user_id)
        key = 'da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        call_forwarding_on = False
        forwarding_phone_number = None
        if twilio_config is not None:
            forwarding_phone_number = twilio_config['name']['default'].get('number', None)
            if forwarding_phone_number is not None:
                call_forwarding_on = True
        call_forwarding_code = None
        call_forwarding_message = None
        if call_forwarding_on:
            for call_key in r.keys(re.sub(r'^da:session:uid:', 'da:phonecode:monitor:*:uid:', key)):
                call_forwarding_code = r.get(call_key)
                if call_forwarding_code is not None:
                    other_value = r.get('da:callforward:' + str(call_forwarding_code))
                    if other_value is None:
                        r.delete(call_key)
                        continue
                    remaining_seconds = r.ttl(call_key)
                    if remaining_seconds > 30:
                        call_forwarding_message = '<span class="phone-message"><i class="fas fa-phone"></i> ' + word('To reach an advocate who can assist you, call') + ' <a class="phone-number" href="tel:' + str(forwarding_phone_number) + '">' + str(forwarding_phone_number) + '</a> ' + word("and enter the code") + ' <span class="phone-code">' + str(call_forwarding_code) + '</span>.</span>'
                        break
        chat_session_key = 'da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        potential_partners = list()
        if str(chatstatus) != 'off': #in ('waiting', 'standby', 'ringing', 'ready', 'on', 'hangup', 'observeonly'):
            obtain_lock(session_id, yaml_filename)
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
            release_lock(session_id, yaml_filename)
            if user_dict is None:
                sys.stderr.write("checkin: error accessing dictionary for %s and %s" % (session_id, yaml_filename))
                return jsonify(success=False)
            obj['chatstatus'] = chatstatus
            obj['secret'] = secret
            obj['encrypted'] = is_encrypted
            obj['mode'] = user_dict['_internal']['livehelp']['mode']
            if obj['mode'] in ('peer', 'peerhelp'):
                peer_ok = True
            if obj['mode'] in ('help', 'peerhelp'):
                help_ok = True
            obj['partner_roles'] = user_dict['_internal']['livehelp']['partner_roles']
            if current_user.is_authenticated:
                for attribute in ('email', 'confirmed_at', 'first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
                    obj[attribute] = unicode(getattr(current_user, attribute, None))
            else:
                obj['temp_user_id'] = temp_user_id
            if help_ok and len(obj['partner_roles']) and not r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
                pipe = r.pipeline()
                for role in obj['partner_roles']:
                    role_key = 'da:chat:roletype:' + str(role)
                    pipe.set(role_key, 1)
                    pipe.expire(role_key, 2592000)
                pipe.execute()
                for role in obj['partner_roles']:
                    for the_key in r.keys('da:monitor:role:' + role + ':userid:*'):
                        user_id = re.sub(r'^.*:userid:', '', the_key)
                        if user_id not in potential_partners:
                            potential_partners.append(user_id)
                for the_key in r.keys('da:monitor:chatpartners:*'):
                    user_id = re.sub(r'^.*chatpartners:', '', the_key)
                    if user_id not in potential_partners:
                        for chat_key in r.hgetall(the_key):
                            if chat_key == chat_session_key:
                                potential_partners.append(user_id)
            if len(potential_partners) > 0:
                if chatstatus == 'ringing':
                    lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
                    #logmessage("Writing to " + str(lkey))
                    pipe = r.pipeline()
                    failure = True
                    for user_id in potential_partners:
                        for the_key in r.keys('da:monitor:available:' + str(user_id)):
                            pipe.rpush(lkey, the_key)
                            failure = False
                    if peer_ok:
                        for the_key in r.keys('da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                            if the_key != chat_session_key:
                                pipe.rpush(lkey, the_key)
                                failure = False
                    if failure:
                        if peer_ok:
                            chatstatus = 'ready'
                        else:
                            chatstatus = 'waiting'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                    else:
                        pipe.expire(lkey, 60)
                        pipe.execute()
                        chatstatus = 'ready'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                elif chatstatus == 'on':
                    if len(potential_partners) > 0:
                        already_connected_to_help = False
                        current_helper = None
                        for user_id in potential_partners:
                            for the_key in r.hgetall('da:monitor:chatpartners:' + str(user_id)):
                                if the_key == chat_session_key:
                                    already_connected_to_help = True
                                    current_helper = user_id
                        if not already_connected_to_help:
                            for user_id in potential_partners:
                                mon_sid = r.get('da:monitor:available:' + str(user_id))
                                if mon_sid is None:
                                    continue
                                int_sid = r.get('da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id))
                                if int_sid is None:
                                    continue
                                r.publish(mon_sid, json.dumps(dict(messagetype='chatready', uid=session_id, i=yaml_filename, userid=the_user_id, secret=secret, sid=int_sid)))
                                r.publish(int_sid, json.dumps(dict(messagetype='chatpartner', sid=mon_sid)))
                                break
                if chatstatus in ('waiting', 'hangup'):
                    chatstatus = 'standby'
                    session['chatstatus'] = chatstatus
                    obj['chatstatus'] = chatstatus
            else:
                if peer_ok:
                    if chatstatus == 'ringing':
                        lkey = 'da:ready:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
                        pipe = r.pipeline()
                        failure = True
                        for the_key in r.keys('da:interviewsession:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                            if the_key != chat_session_key:
                                pipe.rpush(lkey, the_key)
                                failure = False
                        if not failure:
                            pipe.expire(lkey, 6000)
                            pipe.execute()
                        chatstatus = 'ready'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                    elif chatstatus in ('waiting', 'hangup'):
                        chatstatus = 'standby'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
                else:
                    if chatstatus in ('standby', 'ready', 'ringing', 'hangup'):
                        chatstatus = 'waiting'
                        session['chatstatus'] = chatstatus
                        obj['chatstatus'] = chatstatus
            if peer_ok:
                for sess_key in r.keys('da:session:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:*'):
                    if sess_key != key:
                        num_peers += 1
        help_available = len(potential_partners)
        html_key = 'da:html:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        if old_chatstatus != chatstatus:
            html = r.get(html_key)
            if html is not None:
                html_obj = json.loads(html)
                if 'browser_title' in html_obj:
                    obj['browser_title'] = html_obj['browser_title']
                if r.exists('da:block:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)):
                    obj['blocked'] = True
                else:
                    obj['blocked'] = False
                r.publish('da:monitor', json.dumps(dict(messagetype='sessionupdate', key=key, session=obj)))
            else:
                logmessage("checkin: the html was not found at " + str(html_key))
        pipe = r.pipeline()
        pipe.set(key, pickle.dumps(obj))
        pipe.expire(key, 60)
        pipe.expire(html_key, 60)
        pipe.execute()
        ocontrol_key = 'da:control:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        ocontrol = r.get(ocontrol_key)
        if ocontrol is None:
            observer_control = False
        else:
            observer_control = True
        parameters = request.form.get('raw_parameters', None)
        if parameters is not None:
            key = 'da:input:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
            #logmessage("checkin: published parameters to " + key)
            r.publish(key, parameters)
        worker_key = 'da:worker:uid:' + str(session_id) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
        worker_len = r.llen(worker_key)
        if worker_len > 0:
            workers_inspected = 0
            while workers_inspected <= worker_len:
                worker_id = r.lpop(worker_key)
                if worker_id is not None:
                    try:
                        result = docassemble.webapp.worker.workerapp.AsyncResult(id=worker_id)
                        if result.ready():
                            if type(result.result) == ReturnValue:
                                commands.append(dict(value=result.result.value, extra=result.result.extra))
                        else:
                            r.rpush(worker_key, worker_id)
                    except Exception as errstr:
                        logmessage("checkin: got error " + str(errstr))
                        r.rpush(worker_key, worker_id)
                workers_inspected += 1
        if peer_ok or help_ok:
            return jsonify(success=True, chat_status=chatstatus, num_peers=num_peers, help_available=help_available, phone=call_forwarding_message, observerControl=observer_control, commands=commands, checkin_code=checkin_code)
        else:
            return jsonify(success=True, chat_status=chatstatus, phone=call_forwarding_message, observerControl=observer_control, commands=commands, checkin_code=checkin_code)
    return jsonify(success=False)

@app.before_first_request
def setup_celery():
    docassemble.webapp.worker.workerapp.set_current()

@app.before_request
def setup_variables():
    #sys.stderr.write("Request on " + str(os.getpid()) + " " + str(threading.current_thread().ident) + " for " + request.path + " at " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    #g.request_start_time = time.time()
    #docassemble.base.functions.reset_thread_variables()
    docassemble.base.functions.reset_local_variables()

# @app.after_request
# def print_time_of_request(response):
#     time_spent = time.time() - g.request_start_time
#     sys.stderr.write("Request on " + str(os.getpid()) + " " + str(threading.current_thread().ident) + " complete after " + str("%.5fs" % time_spent) + "\n")
#     if time_spent > 3.0:
#         if hasattr(g, 'start_index'):
#             logmessage("Duration to beginning: %fs" % (g.start_index - g.request_start_time))
#         if hasattr(g, 'got_dict'):
#             logmessage("Duration to getting dictionary: %fs" % (g.got_dict - g.request_start_time))
#         if hasattr(g, 'before_interview'):
#             logmessage("Duration to before interview: %fs" % (g.before_interview - g.request_start_time))
#         if hasattr(g, 'after_interview'):
#             logmessage("Duration to after interview: %fs" % (g.after_interview - g.request_start_time))
#         if hasattr(g, 'status_created'):
#             logmessage("Duration to status: %fs" % (g.status_created - g.request_start_time))
#         if hasattr(g, 'assembly_start'):
#             logmessage("Duration to assembly start: %fs" % (g.assembly_start - g.request_start_time))
#         if hasattr(g, 'assembly_end'):
#             logmessage("Duration to assembly end: %fs" % (g.assembly_end - g.request_start_time))
#         logmessage("Duration to end of request: %fs" % time_spent)
#         if hasattr(g, 'interview') and hasattr(g, 'interview_status'):
#             logmessage(to_text(get_history(g.interview, g.interview_status)))
#     return response

# @app.before_request
# def setup_celery():
#     docassemble.webapp.worker.workerapp.set_current()

# @app.before_request
# def before_request():
#     docassemble.base.functions.reset_thread_variables()
#     docassemble.base.functions.reset_local_variables()
#     g.request_start_time = time.time()
#     g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

@app.route("/vars", methods=['POST', 'GET'])
def get_variables():
    session_id = session.get('uid', None)
    yaml_filename = session.get('i', None)
    if 'visitor_secret' in request.cookies:
        secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    #session_cookie_id = request.cookies.get('session', None)
    if session_id is None or yaml_filename is None:
        return jsonify(success=False)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        return jsonify(success=False)
    variables = docassemble.base.functions.serializable_dict(user_dict, include_internal=True)
    #variables['_internal'] = docassemble.base.functions.serializable_dict(user_dict['_internal'])
    return jsonify(success=True, variables=variables, steps=steps, encrypted=is_encrypted, uid=session_id, i=yaml_filename)

@app.route("/", methods=['GET'])
def rootindex():
    url = daconfig.get('root redirect url', None)
    if url is not None:
        return redirect(url)
    yaml_filename = session.get('i', default_yaml_filename)
    yaml_parameter = request.args.get('i', None)
    if yaml_filename is None and yaml_parameter is None:
        if len(daconfig['dispatch']):
            return redirect(url_for('interview_start'))
        yaml_filename = final_default_yaml_filename
    the_args = dict()
    for key, val in request.args.iteritems():
        the_args[key] = val
    if yaml_parameter is None and yaml_filename is not None:
        the_args['i'] = yaml_filename
    return redirect(url_for('index', **the_args))

@app.route("/interview", methods=['POST', 'GET'])
def index():
    if 'ajax' in request.form and int(request.form['ajax']):
        is_ajax = True
    else:
        is_ajax = False
    return_fake_html = False
        # if 'newsecret' in session:
        #     logmessage("interview_list: fixing cookie")
        #     response = redirect(url_for('index'))
        #     response.set_cookie('secret', session['newsecret'])
        #     del session['newsecret']
        #     return response
    if ('json' in request.form and int(request.form['json'])) or ('json' in request.args and int(request.args['json'])):
        the_interface = 'json'
        is_json = True
    else:
        the_interface = 'web'
        is_json = False
    chatstatus = session.get('chatstatus', 'off')
    session_id = session.get('uid', None)
    #logmessage("index: session uid is " + str(session_id))
    if current_user.is_anonymous:
        #logmessage("index: is anonymous")
        if 'tempuser' not in session:
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            session['tempuser'] = new_temp_user.id
    else:
        #logmessage("index: is not anonymous")
        if 'user_id' not in session:
            session['user_id'] = current_user.id
    expire_visitor_secret = False
    if 'visitor_secret' in request.cookies:
        #logmessage("index: there is a visitor secret")
        if 'session' in request.args:
            secret = request.cookies.get('secret', None)
            expire_visitor_secret = True
        else:
            secret = request.cookies['visitor_secret']
    else:
        secret = request.cookies.get('secret', None)
    #logmessage("index: secret is " + repr(secret))
    use_cache = int(request.args.get('cache', 1))
    reset_interview = int(request.args.get('reset', 0))
    new_interview = int(request.args.get('new_session', 0))
    encrypted = session.get('encrypted', True)
    #logmessage("index: session says encrypted is " + str(encrypted))
    if secret is None:
        #logmessage("index: setting set_cookie to True")
        secret = random_string(16)
        set_cookie = True
    else:
        #logmessage("index: setting set_cookie to False")
        secret = str(secret)
        set_cookie = False
    yaml_filename = session.get('i', default_yaml_filename)
    #logmessage("index: yaml_filename from session/default is " + str(yaml_filename))
    steps = 1
    need_to_reset = False
    need_to_resave = False
    yaml_parameter = request.args.get('i', None)
    if yaml_filename is None and yaml_parameter is None:
        if len(daconfig['dispatch']):
            return redirect(url_for('interview_start'))
        else:
            yaml_filename = final_default_yaml_filename
    session_parameter = request.args.get('session', None)
    #logmessage("index: session_parameter is " + str(session_parameter))
    #g.start_index = time.time()
    if yaml_parameter is not None:
        #logmessage("index: yaml_parameter is not None: " + str(yaml_parameter))
        yaml_filename = yaml_parameter
        old_yaml_filename = session.get('i', None)
        #logmessage("index: old_yaml_filename is " + str(old_yaml_filename))
        if old_yaml_filename != yaml_filename or reset_interview or new_interview:
            #logmessage("index: change in yaml filename detected")
            if (PREVENT_DEMO) and (yaml_filename.startswith('docassemble.base:') or yaml_filename.startswith('docassemble.demo:')) and (current_user.is_anonymous or not current_user.has_role('admin', 'developer')):
                raise DAError("Not authorized")
            show_flash = False
            if not yaml_filename.startswith('docassemble.playground'):
                yaml_filename = re.sub(r':([^\/]+)$', r':data/questions/\1', yaml_filename)
            session['i'] = yaml_filename
            if old_yaml_filename is not None and request.args.get('from_list', None) is None and not yaml_filename.startswith("docassemble.playground") and not yaml_filename.startswith("docassemble.base") and not yaml_filename.startswith("docassemble.demo") and SHOW_LOGIN and not new_interview:
                show_flash = True
            if current_user.is_authenticated and current_user.has_role('admin', 'developer', 'advocate'):
                show_flash = False
            if session_parameter is None:
                #logmessage("index: change in yaml filename detected and session_parameter is None")
                if show_flash:
                    if current_user.is_authenticated:
                        message = "Starting a new interview.  To go back to your previous interview, go to My Interviews on the menu."
                    else:
                        message = "Starting a new interview.  To go back to your previous interview, log in to see a list of your interviews."
                #logmessage("index: calling reset_session with retain_code")
                # if (('uid' in session and user_dict_exists(session['uid'], yaml_filename)) or old_yaml_filename != yaml_filename):
                #     retain_code = False
                # else:
                #     retain_code = True
                if reset_interview and 'uid' in session:
                    reset_user_dict(session['uid'], yaml_filename)
                user_code, user_dict = reset_session(yaml_filename, secret)
                add_referer(user_dict)
                save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
                release_lock(user_code, yaml_filename)
                session_id = session.get('uid', None)
                if 'key_logged' in session:
                    del session['key_logged']
                #logmessage("Need to reset because session_parameter is none")
                need_to_resave = True
                need_to_reset = True
            else:
                #logmessage("index: both i and session provided")
                if show_flash:
                    if current_user.is_authenticated:
                        message = "Entering a different interview.  To go back to your previous interview, go to My Interviews on the menu."
                    else:
                        message = "Entering a different interview.  To go back to your previous interview, log in to see a list of your interviews."
            if show_flash:
                flash(word(message), 'info')
    else:
        if session_parameter is None and (reset_interview or new_interview):
            if 'uid' in session and reset_interview:
                reset_user_dict(session['uid'], yaml_filename)
            user_code, user_dict = reset_session(yaml_filename, secret, retain_code=False)
            add_referer(user_dict)
            save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
            release_lock(user_code, yaml_filename)
            session_id = session.get('uid', None)
            if 'key_logged' in session:
                del session['key_logged']
            need_to_resave = True
            need_to_reset = True
        elif not (is_ajax or is_json):
            #logmessage("index: need_to_reset is True because not ajax/json and yaml_parameter is None")
            need_to_reset = True
    if session_parameter is not None:
        #logmessage("index: session parameter is not None: " + str(session_parameter))
        session_id = session_parameter
        session['uid'] = session_id
        if yaml_parameter is not None:
            #logmessage("index: yaml_parameter is not None: " + str(yaml_filename))
            session['i'] = yaml_filename
        if 'key_logged' in session:
            del session['key_logged']
        #logmessage("index: resetting because session_parameter not none")
        need_to_reset = True
    if session_id:
        #logmessage("index: session_id is defined")
        user_code = session_id
        obtain_lock(user_code, yaml_filename)
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(user_code, yaml_filename, secret=secret)
        except Exception as the_err:
            sys.stderr.write("index: there was an exception after fetch_user_dict with %s and %s, so we need to reset\n" % (user_code, yaml_filename))
            sys.stderr.write(unicode(the_err.__class__.__name__) + " " + unicode(the_err) + "\n")
            release_lock(user_code, yaml_filename)
            logmessage("index: dictionary fetch failed, resetting without retain_code")
            user_code, user_dict = reset_session(yaml_filename, secret)
            add_referer(user_dict)
            encrypted = False
            session['encrypted'] = encrypted
            is_encrypted = encrypted
            need_to_resave = True
            need_to_reset = True
        if encrypted != is_encrypted:
            #logmessage("index: change in encryption; encrypted is " + str(encrypted) + " but is_encrypted is " + str(is_encrypted))
            encrypted = is_encrypted
            session['encrypted'] = encrypted
        if user_dict is None:
            #logmessage("index: user_dict is None")
            try:
                release_lock(user_code, yaml_filename)
            except:
                pass
            del user_code
            del user_dict
    try:
        user_dict
        user_code
    except:
        #logmessage("index: 02 Calling without retain_code")
        user_code, user_dict = reset_session(yaml_filename, secret)
        add_referer(user_dict)
        encrypted = False
        session['encrypted'] = encrypted
        steps = 1
    #g.got_dict = time.time()
    action = None
    if user_dict.get('multi_user', False) is True and encrypted is True:
        #logmessage("index: encryption mismatch, should be False")
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
    # else:
    #     logmessage("index: no encryption mismatch for should be False")        
    if user_dict.get('multi_user', False) is False and encrypted is False:
        #logmessage("index: encryption mismatch, should be True")
        encrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
        encrypted = True
        session['encrypted'] = encrypted
    # else:
    #     logmessage("index: no encryption mismatch for should be True")        
    # if current_user.is_authenticated and 'key_logged' not in session:
    if 'key_logged' not in session:
        #logmessage("index: need to save user dict key")
        save_user_dict_key(user_code, yaml_filename)
        session['key_logged'] = True
    if 'action' in session:
        #logmessage("index: action in session")
        action = json.loads(myb64unquote(session['action']))
        del session['action']
    if '_action' in request.form:
        action = json.loads(myb64unquote(request.form['_action']))
        #logmessage("index: action from _action is " + str(action))
    if len(request.args):
        #logmessage("index: there were args")
        if 'action' in request.args:
            session['action'] = request.args['action']
            response = do_redirect(url_for('index', i=yaml_filename), is_ajax, is_json)
            if set_cookie:
                response.set_cookie('secret', secret)
            if expire_visitor_secret:
                response.set_cookie('visitor_secret', '', expires=0)
            release_lock(user_code, yaml_filename)
            #logmessage("index: returning action response")
            return response
        for argname in request.args:
            if argname in ('i', 'json'):
                continue
            if argname in ('from_list', 'session', 'cache', 'reset', 'new_session'):
                # 'filename', 'question', 'format', 'index', 'action'
                need_to_reset = True
                continue
            if re.match('[A-Za-z_][A-Za-z0-9_]*', argname):
                exec("url_args['" + argname + "'] = " + repr(request.args.get(argname).encode('unicode_escape')), user_dict)
                #logmessage("index: there was an argname " + str(argname) + " and we need to reset")
            need_to_resave = True
            need_to_reset = True
    if need_to_reset:
        #logmessage("index: needed to reset, so redirecting; encrypted is " + str(encrypted))
        if use_cache == 0:
            # docassemble.base.parse.interview_source_from_string(yaml_filename).reset_modtime()
            #sys.stderr.write("Updating index because of cache being 0\n")
            docassemble.base.parse.interview_source_from_string(yaml_filename).update_index()
        if need_to_resave:
            save_user_dict(user_code, user_dict, yaml_filename, secret=secret, encrypt=encrypted)
        response = do_redirect(url_for('index', i=yaml_filename), is_ajax, is_json)
        if set_cookie:
            response.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
        release_lock(user_code, yaml_filename)
        return response
    #logmessage("index: made it through")
    post_data = request.form.copy()
    if current_user.is_anonymous:
        the_user_id = 't' + str(session['tempuser'])
    else:
        the_user_id = current_user.id
    # if '_email_attachments' in post_data and '_attachment_email_address' in post_data and '_question_number' in post_data:
    #     success = False
    #     question_number = post_data['_question_number']
    #     attachment_email_address = post_data['_attachment_email_address']
    #     if '_attachment_include_editable' in post_data:
    #         if post_data['_attachment_include_editable'] == 'True':
    #             include_editable = True
    #         else:
    #             include_editable = False
    #         del post_data['_attachment_include_editable']
    #     else:
    #         include_editable = False
    #     del post_data['_question_number']
    #     del post_data['_email_attachments']
    #     del post_data['_attachment_email_address']
    #     ci = current_info(yaml=yaml_filename, req=request)
    #     worker_key = 'da:worker:uid:' + str(user_code) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
    #     for email_address in re.split(r' *[,;] *', attachment_email_address.strip()):
    #         try:
    #             result = docassemble.webapp.worker.email_attachments.delay(yaml_filename, ci['user'], user_code, secret, ci['url'], ci['url_root'], email_address, question_number, include_editable)
    #             r.rpush(worker_key, result.id)
    #             success = True
    #         except Exception as errmess:
    #             success = False
    #             logmessage("index: failed with " + str(errmess))
    #             break
    #     if success:
    #         flash(word("Your documents will be e-mailed to") + " " + str(attachment_email_address) + ".", 'success')
    #     else:
    #         flash(word("Unable to e-mail your documents to") + " " + str(attachment_email_address) + ".", 'error')
    if '_back_one' in post_data and steps > 1:
        old_user_dict = user_dict
        steps, user_dict, is_encrypted = fetch_previous_user_dict(user_code, yaml_filename, secret)
        if encrypted != is_encrypted:
            encrypted = is_encrypted
            session['encrypted'] = encrypted
    else:
        old_user_dict = None
    # elif 'filename' in request.args:
    #     the_user_dict, attachment_encrypted = get_attachment_info(user_code, request.args.get('question'), request.args.get('i'), secret)
    #     if the_user_dict is not None:
    #         interview = docassemble.base.interview_cache.get_interview(request.args.get('i'))
    #         interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=request.args.get('i'), req=request, action=action))
    #         interview.assemble(the_user_dict, interview_status)
    #         if len(interview_status.attachments) > 0:
    #             the_attachment = interview_status.attachments[int(request.args.get('index'))]
    #             the_file_number = the_attachment['file'][request.args.get('format')]
    #             the_format = request.args.get('format')
    #             if the_format == "pdf":
    #                 mime_type = 'application/pdf'
    #             elif the_format == "tex":
    #                 mime_type = 'application/x-latex'
    #             elif the_format == "rtf":
    #                 mime_type = 'application/rtf'
    #             elif the_format == "docx":
    #                 mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    #             response = send_file(the_filename, mimetype=str(mime_type), as_attachment=True, attachment_filename=str(the_attachment['filename']) + '.' + str(the_format))
    #             response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    #             release_lock(user_code, yaml_filename)
    #             return(response)
    known_varnames = dict()
    if '_varnames' in post_data:
        known_varnames = json.loads(myb64unquote(post_data['_varnames']))
    if '_visible' in post_data and post_data['_visible'] != "":
        visible_field_names = json.loads(myb64unquote(post_data['_visible']))
    else:
        visible_field_names = list()
    #logmessage("Visible field names is " + repr(visible_field_names))
    field_numbers = dict()
    numbered_fields = dict()
    for kv_key, kv_var in known_varnames.iteritems():
        try:
            field_identifier = myb64unquote(kv_key)
            m = re.search(r'_field_([0-9]+)', field_identifier)
            if m:
                numbered_fields[kv_var] = kv_key
                field_numbers[kv_var] = int(m.group(1))
        except:
            logmessage("index: error where kv_key is " + unicode(kv_key) + " and kv_var is " + unicode(kv_var))
    visible_fields = set()
    for field_name in visible_field_names:
        try:
            m = re.search(r'(.*)(\[[^\]]+\])$', from_safeid(field_name))
            if m:
                #logmessage("Found a checkbox var " + m.group(1))
                #logmessage("Found a checkbox index " + m.group(2))
                if safeid(m.group(1)) in known_varnames:
                    #logmessage("Adding " + from_safeid(known_varnames[safeid(m.group(1))]) + m.group(2) + " to visible_fields")
                    visible_fields.add(safeid(from_safeid(known_varnames[safeid(m.group(1))]) + m.group(2)))
        except Exception as the_err:
            #logmessage("Failure to unpack " + field_name + " because of " + unicode(the_err))
            pass
        if field_name in known_varnames:
            visible_fields.add(known_varnames[field_name])
        else:
            visible_fields.add(field_name)
    #logmessage("known_varnames is " + repr(known_varnames))
    #logmessage("Visible fields is " + repr(visible_fields))
    #logmessage("Numbered fields is " + repr(numbered_fields))
    if '_checkboxes' in post_data:
        checkbox_fields = json.loads(myb64unquote(post_data['_checkboxes'])) #post_data['_checkboxes'].split(",")
        #logmessage("checkbox_fields is " + repr(checkbox_fields))
        for checkbox_field, checkbox_value in checkbox_fields.iteritems():
            if checkbox_field in visible_fields and checkbox_field not in post_data and not (checkbox_field in numbered_fields and numbered_fields[checkbox_field] in post_data):
                #logmessage("Checkbox: adding " + checkbox_field + " set to " + checkbox_value)
                post_data.add(checkbox_field, checkbox_value)
    if '_empties' in post_data:
        empty_fields = json.loads(myb64unquote(post_data['_empties']))
        for empty_field in empty_fields:
            if empty_field not in post_data:
                post_data.add(empty_field, 'None')
    else:
        empty_fields = dict()
    if '_ml_info' in post_data:
        ml_info = json.loads(myb64unquote(post_data['_ml_info']))
    else:
        ml_info = dict()
    something_changed = False
    if '_tracker' in post_data and user_dict['_internal']['tracker'] != int(post_data['_tracker']):
        if user_dict['_internal']['tracker'] > int(post_data['_tracker']):
            logmessage("index: the assemble function has been run since the question was posed.")
        else:
            logmessage("index: the tracker in the dictionary is behind the tracker in the question.")
        something_changed = True
        user_dict['_internal']['tracker'] = max(int(post_data['_tracker']), user_dict['_internal']['tracker'])
    if '_track_location' in post_data and post_data['_track_location']:
        logmessage("index: found track location of " + post_data['_track_location'])
        the_location = json.loads(post_data['_track_location'])
    else:
        the_location = None
    should_assemble = False
    for key in post_data:
        if key.startswith('_') or key in ('csrf_token', 'ajax', 'json', 'informed'):
            continue
        try:
            if key_requires_preassembly.search(from_safeid(key)):
                should_assemble = True
                #logmessage("index: pre-assembly necessary")
                break
        except:
            logmessage("index: bad key was " + unicode(key))
    #g.before_interview = time.time()
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    #g.after_interview = time.time()
    #g.interview = interview
    if not interview.from_cache and len(interview.mlfields):
        ensure_training_loaded(interview)
    debug_mode = interview.debug
    # if should_assemble and '_action_context' in post_data:
    #     action = json.loads(myb64unquote(post_data['_action_context']))
    interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, action=action, location=the_location, interface=the_interface), tracker=user_dict['_internal']['tracker'])
    #g.interview_status = interview_status
    #g.status_created = time.time()
    vars_set = set()
    if ('_email_attachments' in post_data and '_attachment_email_address' in post_data) or '_download_attachments' in post_data:
        should_assemble = True
    if should_assemble or something_changed:
        #logmessage("index: assemble 1")
        interview.assemble(user_dict, interview_status)
        if '_question_name' in post_data and post_data['_question_name'] != interview_status.question.name:
            logmessage("index: not the same question name: " + post_data['_question_name'] + " versus " + interview_status.question.name)
    changed = False
    error_messages = list()
    if '_email_attachments' in post_data and '_attachment_email_address' in post_data:
        success = False
        attachment_email_address = post_data['_attachment_email_address']
        if '_attachment_include_editable' in post_data:
            if post_data['_attachment_include_editable'] == 'True':
                include_editable = True
            else:
                include_editable = False
            del post_data['_attachment_include_editable']
        else:
            include_editable = False
        del post_data['_email_attachments']
        del post_data['_attachment_email_address']
        if len(interview_status.attachments) > 0:
            attached_file_count = 0
            attachment_info = list()
            for the_attachment in interview_status.attachments:
                file_formats = list()
                if 'pdf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                    file_formats.append('pdf')
                if include_editable or 'pdf' not in file_formats:
                    if 'rtf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                        file_formats.append('rtf')
                    if 'docx' in the_attachment['valid_formats']:
                        file_formats.append('docx')
                    if 'rtf to docx' in the_attachment['valid_formats']:
                        file_formats.append('rtf to docx')
                for the_format in file_formats:
                    attachment_info.append({'filename': str(the_attachment['filename']) + '.' + str(docassemble.base.parse.extension_of_doc_format[the_format]), 'number': the_attachment['file'][the_format], 'mimetype': the_attachment['mimetype'][the_format], 'attachment': the_attachment})
                    attached_file_count += 1
            worker_key = 'da:worker:uid:' + str(user_code) + ':i:' + str(yaml_filename) + ':userid:' + str(the_user_id)
            for email_address in re.split(r' *[,;] *', attachment_email_address.strip()):
                try:
                    result = docassemble.webapp.worker.email_attachments.delay(user_code, email_address, attachment_info)
                    r.rpush(worker_key, result.id)
                    success = True
                except Exception as errmess:
                    success = False
                    logmessage("index: failed with " + str(errmess))
                    break
            if success:
                flash(word("Your documents will be e-mailed to") + " " + unicode(attachment_email_address) + ".", 'success')
            else:
                flash(word("Unable to e-mail your documents to") + " " + unicode(attachment_email_address) + ".", 'error')
        else:
            flash(word("Unable to find documents to e-mail."), 'error')
    if '_download_attachments' in post_data:
        success = False
        if '_attachment_include_editable' in post_data:
            if post_data['_attachment_include_editable'] == 'True':
                include_editable = True
            else:
                include_editable = False
            del post_data['_attachment_include_editable']
        else:
            include_editable = False
        del post_data['_download_attachments']
        if len(interview_status.attachments) > 0:
            attached_file_count = 0
            files_to_zip = list()
            if 'zip_filename' in interview_status.extras and interview_status.extras['zip_filename']:
                zip_file_name = interview_status.extras['zip_filename']
            else:
                zip_file_name = 'file.zip'
            for the_attachment in interview_status.attachments:
                file_formats = list()
                if 'pdf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                    file_formats.append('pdf')
                if include_editable or 'pdf' not in file_formats:
                    if 'rtf' in the_attachment['valid_formats'] or '*' in the_attachment['valid_formats']:
                        file_formats.append('rtf')
                    if 'docx' in the_attachment['valid_formats']:
                        file_formats.append('docx')
                    if 'rtf to docx' in the_attachment['valid_formats']:
                        file_formats.append('rtf to docx')
                for the_format in file_formats:
                    files_to_zip.append(str(the_attachment['file'][the_format]))
                    attached_file_count += 1
            the_zip_file = docassemble.base.util.zip_file(*files_to_zip, filename=zip_file_name)
            response = send_file(the_zip_file.path(), mimetype='application/zip', as_attachment=True, attachment_filename=zip_file_name)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return(response)
    if '_the_image' in post_data:
        file_field = from_safeid(post_data['_save_as']);
        if match_invalid.search(file_field):
            error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
        else:
            if something_changed and key_requires_preassembly.search(file_field) and not should_assemble:
                #logmessage("index: assemble 2")
                interview.assemble(user_dict, interview_status)
            initial_string = 'import docassemble.base.core'
            try:
                #logmessage("index: doing " + initial_string)
                exec(initial_string, user_dict)
            except Exception as errMess:
                error_messages.append(("error", "Error: " + unicode(errMess)))
            if '_success' in post_data and post_data['_success']:
                theImage = base64.b64decode(re.search(r'base64,(.*)', post_data['_the_image']).group(1) + '==')
                filename = secure_filename('canvas.png')
                file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                extension, mimetype = get_ext_and_mimetype(filename)
                new_file = SavedFile(file_number, extension=extension, fix=True)
                new_file.write_content(theImage)
                new_file.finalize()
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ", filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', make_pngs=True, extension='" + str(extension) + "')"
            else:
                the_string = file_field + " = docassemble.base.core.DAFile(" + repr(file_field) + ")"
            #logmessage("0Doing " + the_string)
            vars_set.add(file_field)
            try:
                exec(the_string, user_dict)
                if not changed:
                    steps += 1
                    user_dict['_internal']['steps'] = steps
                    changed = True
            except Exception as errMess:
                error_messages.append(("error", "Error: " + unicode(errMess)))
    known_datatypes = dict()
    if '_next_action_to_set' in post_data:
        next_action_to_set = json.loads(myb64unquote(post_data['_next_action_to_set']))
        #logmessage("next_action_to_set is " + str(next_action_to_set))
    else:
        next_action_to_set = None
    # restore this, maybe
    if False and '_next_action' in post_data:
        next_action = json.loads(myb64unquote(post_data['_next_action']))
        #logmessage("next_action is " + str(next_action))
    else:
        next_action = None
    if '_datatypes' in post_data:
        known_datatypes = json.loads(myb64unquote(post_data['_datatypes']))
    #logmessage("field_numbers is " + str(field_numbers))
    if '_question_name' in post_data and post_data['_question_name'] in interview.questions_by_name:
        the_question = interview.questions_by_name[post_data['_question_name']]
        if not (should_assemble or something_changed):
            if the_question.validation_code is not None:
                #logmessage("index: assemble 3")
                interview.assemble(user_dict, interview_status)
            else:
                for the_field in the_question.fields:
                    if hasattr(the_field, 'validate'):
                        #logmessage("index: assemble 4")
                        interview.assemble(user_dict, interview_status)
                        break
    else:
        the_question = None
    #known_variables = dict()
    for orig_key in copy.deepcopy(post_data):
        if orig_key in ('_checkboxes', '_empties', '_ml_info', '_back_one', '_files', '_files_inline', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_event', '_visible', '_tracker', '_track_location', '_varnames', '_next_action', '_next_action_to_set', 'ajax', 'json', 'informed', 'csrf_token', '_action') or orig_key.startswith('_ignore'):
            continue
        try:
            key = myb64unquote(orig_key)
        except:
            continue
        if key.startswith('_field_'):
            if orig_key in known_varnames:
                if not (known_varnames[orig_key] in post_data and post_data[known_varnames[orig_key]] != '' and post_data[orig_key] == ''):
                    post_data[known_varnames[orig_key]] = post_data[orig_key]
            else:
                #logmessage("orig_key " + orig_key + " is not in known_varnames")
                m = re.search(r'^(_field_[0-9]+)(\[.*\])', key)
                if m:
                    #logmessage("got a match")
                    base_orig_key = safeid(m.group(1))
                    if base_orig_key in known_varnames:
                        full_key = safeid(myb64unquote(known_varnames[base_orig_key]) + m.group(2))
                        #logmessage("Adding " + full_key + " to post_data")
                        post_data[full_key] = post_data[orig_key]
                    #else:
                    #    logmessage("foo 1")
                #else:
                #    logmessage("foo 2")
        if key.endswith('.gathered'):
            objname = re.sub(r'\.gathered$', '', key)
            #logmessage("Considering gathered key: " + str(key))
            try:
                eval(objname, user_dict)
            except:
                safe_objname = safeid(objname)
                if safe_objname in known_datatypes:
                    if known_datatypes[safe_objname] == 'object_checkboxes':
                        docassemble.base.parse.ensure_object_exists(objname, 'object_checkboxes', user_dict)
                    elif known_datatypes[safe_objname] == 'checkboxes':
                        docassemble.base.parse.ensure_object_exists(objname, 'checkboxes', user_dict)
    field_error = dict()
    validated = True
    imported_core = False
    #blank_fields = set(known_datatypes.keys())
    #logmessage("blank_fields is " + repr(blank_fields))
    for orig_key in post_data:
        if orig_key in ('_checkboxes', '_empties', '_ml_info', '_back_one', '_files', '_files_inline', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_event', '_visible', '_tracker', '_track_location', '_varnames', '_next_action', '_next_action_to_set', 'ajax', 'json', 'informed', 'csrf_token', '_action') or orig_key.startswith('_ignore'):
            continue
        data = post_data[orig_key]
        #logmessage("The data type is " + unicode(type(data)))
        try:
            key = myb64unquote(orig_key)
        except:
            raise DAError("index: invalid name " + unicode(orig_key))
        #logmessage("Processing a key: " + key)
        #if orig_key in blank_fields:
            #logmessage(key + " is not a blank field")
            #blank_fields.discard(orig_key)
        if key.startswith('_field_'):
            continue
        bracket_expression = None
        if orig_key in empty_fields:
            #logmessage("orig_key " + str(orig_key) + " is set to empty: " + str(empty_fields[orig_key]))
            set_to_empty = empty_fields[orig_key]
        else:
            #logmessage("orig_key " + str(orig_key) + " is not set to empty")
            set_to_empty = None #used to be False
        #logmessage("Searching key " + str(key))
        if match_brackets.search(key):
            match = match_inside_and_outside_brackets.search(key)
            try:
                key = match.group(1)
            except:
                raise DAError("index: invalid bracket name " + unicode(match.group(1)))
            real_key = safeid(key)
            b_match = match_inside_brackets.search(match.group(2))
            if b_match:
                try:
                    bracket_expression = from_safeid(b_match.group(1))
                except:
                    bracket_expression = b_match.group(1)
            bracket = match_inside_brackets.sub(process_bracket_expression, match.group(2))
            parse_result = docassemble.base.parse.parse_var_name(key)
            if not parse_result['valid']:
                error_messages.append(("error", "Error: Invalid key " + key + ": " + parse_result['reason']))
                break
            key = key + bracket
            core_key_name = parse_result['final_parts'][0]
            whole_key = core_key_name + parse_result['final_parts'][1]
            real_key = safeid(whole_key)
            # logmessage("core key name is " + str(core_key_name) + " whole key is " + str(whole_key) + " Checking for existence of " + str(whole_key))
            if whole_key in user_dict:
                it_exists = True
            else:
                try:
                    the_object = eval(whole_key, user_dict)
                    it_exists = True
                except:
                    it_exists = False
            # if it_exists:
            #     logmessage(whole_key + "exists and is a " + the_object.__class__.__name__)
            if not it_exists:
                # logmessage("It does not exist")
                method = None
                commands = list()
                # logmessage(repr(parse_result['final_parts']))
                if parse_result['final_parts'][1] != '':
                    if parse_result['final_parts'][1][0] == '.':
                        try:
                            #logmessage("Evaling " + core_key_name)
                            core_key = eval(core_key_name, user_dict)
                            if hasattr(core_key, 'instanceName'):
                                method = 'attribute'
                        except:
                            pass
                    elif parse_result['final_parts'][1][0] == '[':
                        try:
                            #logmessage("Evaling " + core_key_name)
                            core_key = eval(core_key_name, user_dict)
                            if hasattr(core_key, 'instanceName'):
                                method = 'index'
                        except:
                            pass
                datatype = known_datatypes.get(real_key, None)
                #logmessage("datatype is " + str(datatype))
                #logmessage("method is " + str(method))
                if not imported_core:
                    commands.append("import docassemble.base.core")
                    imported_core = True
                if method == 'attribute':
                    attribute_name = parse_result['final_parts'][1][1:]
                    #logmessage("Checkbox object is " + attribute_name)
                    if datatype == 'checkboxes':
                        commands.append(core_key_name + ".initializeAttribute(" + repr(attribute_name) + ", docassemble.base.core.DADict, auto_gather=False, gathered=True)")
                    elif datatype == 'object_checkboxes':
                        commands.append(core_key_name + ".initializeAttribute(" + repr(attribute_name) + ", docassemble.base.core.DAList, auto_gather=False, gathered=True)")
                    vars_set.add(core_key_name)
                elif method == 'index':
                    index_name = parse_result['final_parts'][1][1:-1]
                    #logmessage("Checkbox object is " + index_name)
                    if datatype == 'checkboxes':
                        commands.append(core_key_name + ".initializeObject(" + repr(index_name) + ", docassemble.base.core.DADict, auto_gather=False, gathered=True)")
                    elif datatype == 'object_checkboxes':
                        commands.append(core_key_name + ".initializeObject(" + repr(index_name) + ", docassemble.base.core.DAList, auto_gather=False, gathered=True)")
                    vars_set.add(core_key_name)
                else:
                    #logmessage("Checkbox object is " + whole_key)
                    if datatype == 'checkboxes':
                        commands.append(whole_key + ' = docassemble.base.core.DADict(' + repr(whole_key) + ', auto_gather=False, gathered=True)')
                    elif datatype == 'object_checkboxes':
                        commands.append(whole_key + ' = docassemble.base.core.DAList(' + repr(whole_key) + ', auto_gather=False, gathered=True)')
                    vars_set.add(whole_key)
                for command in commands:
                    #logmessage("1Doing " + command)
                    exec(command, user_dict)            
            #logmessage("key is now " + key)
            # match = match_inside_and_outside_brackets.search(key)
            # try:
            #     key = match.group(1)
            # except:
            #     raise DAError("index: invalid bracket name " + str(match.group(1)))
            # real_key = safeid(key)
            # if match_invalid_key.search(key):
            #     error_messages.append(("error", "Error: Invalid character in key: " + key))
            #     break
            # b_match = match_inside_brackets.search(match.group(2))
            # if b_match:
            #     try:
            #         bracket_expression = from_safeid(b_match.group(1))
            #     except:
            #         bracket_expression = b_match.group(1)
            # bracket = match_inside_brackets.sub(process_bracket_expression, match.group(2))
            # #logmessage("key is " + str(key) + " and bracket is " + str(bracket))
            # if key in user_dict:
            #     known_variables[key] = True
            # if key not in known_variables:
            #     try:
            #         eval(key, user_dict)
            #     except:
            #         #logmessage("setting key " + str(key) + " to empty dict")
            #         #m = re.search(r'(.*)\.([^.]+)', key)
            #         use_initialize = False
            #         if re.search(r'\.', key):
            #             core_key_name = re.sub(r'^(.*)\..*', r'\1', key)
            #             attribute_name = re.sub(r'.*\.', '', key)
            #             #logmessage("Core key is " + str(core_key_name))
            #             try:
            #                 core_key = eval(core_key, user_dict)
            #                 if isinstance(core_key, DAObject):
            #                     use_initialize = True
            #             except:
            #                 pass
            #         objtype = 'DADict'
            #         if orig_key in known_datatypes:
            #             #logmessage("key " + key + " is a " + known_datatypes[orig_key])
            #             if known_datatypes[orig_key] == 'object_checkboxes':
            #                 objtype = 'DAList'
            #         if use_initialize:
            #             the_string = "import docassemble.base.core\n" + core_key_name + ".initializeAttribute(" + repr(attribute_name) + ", docassemble.base." + objtype + ", auto_gather=False, gathered=True)"
            #         else:
            #             the_string = "import docassemble.base.core\n" + key + ' = docassemble.base.core.' + objtype + '(' + repr(key) + ', auto_gather=False, gathered=True)'
            #         try:
            #             exec(the_string, user_dict)
            #             known_variables[key] = True
            #         except:
            #             raise DAError("cannot initialize " + key)
            # key = key + bracket
        else:
            real_key = orig_key
            parse_result = docassemble.base.parse.parse_var_name(key)
            if not parse_result['valid']:
                error_messages.append(("error", "Error: Invalid character in key: " + key))
                break
        #logmessage("Real key is " + real_key + " and key is " + key)
        do_append = False
        do_opposite = False
        is_ml = False
        is_date = False
        test_data = data
        if real_key in known_datatypes:
            #logmessage("real key " + real_key + " is in datatypes: " + known_datatypes[real_key])
            if known_datatypes[real_key] in ('boolean', 'checkboxes'):
                #logmessage("Processing boolean")
                if data == "True":
                    data = "True"
                    test_data = True
                else:
                    data = "False"
                    test_data = False
            elif known_datatypes[real_key] == 'threestate':
                if data == "True":
                    data = "True"
                    test_data = True
                elif data == "None":
                    data = "None"
                    test_data = None
                else:
                    data = "False"
                    test_data = False
            elif known_datatypes[real_key] in ('date', 'datetime'):
                if type(data) in (str, unicode):
                    data = data.strip()
                    if data != '':
                        try:
                            dateutil.parser.parse(data)
                        except:
                            validated = False
                            if known_datatypes[real_key] == 'date':
                                field_error[orig_key] = word("You need to enter a valid date.")
                            else:
                                field_error[orig_key] = word("You need to enter a valid date and time.")
                            continue
                        test_data = data
                        is_date = True
                        data = 'docassemble.base.util.as_datetime(' + repr(data) + ')'
                    else:
                        data = repr('')
                else:
                    data = repr('')
            elif known_datatypes[real_key] == 'time':
                if type(data) in (str, unicode):
                    data = data.strip()
                    if data != '':
                        try:
                            dateutil.parser.parse(data)
                        except:
                            validated = False
                            field_error[orig_key] = word("You need to enter a valid time.")
                            continue
                        test_data = data
                        is_date = True
                        data = 'docassemble.base.util.as_datetime(' + repr(data) + ').time()'
                    else:
                        data = repr('')
                else:
                    data = repr('')
            elif known_datatypes[real_key] == 'integer':
                if data == '':
                    data = 0
                test_data = int(data)
                data = "int(" + repr(data) + ")"
            elif known_datatypes[real_key] in ('ml', 'mlarea'):
                is_ml = True
            elif known_datatypes[real_key] in ('number', 'float', 'currency', 'range'):
                if data == '':
                    data = 0.0
                if isinstance(data, basestring):
                    data = re.sub(r',', '', data)
                test_data = float(data)
                data = "float(" + repr(data) + ")"
            elif known_datatypes[real_key] in ('object', 'object_radio'):
                #logmessage("We have an object type and objselections is " + str(user_dict['_internal']['objselections']))
                #logmessage("We have an object type and key is " + str(key))
                #logmessage("We have an object type and data is " + str(data))
                #logmessage("We have an object type and set_to_empty is " + str(set_to_empty))
                if data == '' or set_to_empty:
                    continue
                data = "_internal['objselections'][" + repr(key) + "][" + repr(data) + "]"
            elif known_datatypes[real_key] == 'object_checkboxes' and bracket_expression is not None:
                if data not in ('True', 'False', 'None') or set_to_empty:
                    continue
                do_append = True
                if data == 'False':
                    do_opposite = True
                data = "_internal['objselections'][" + repr(from_safeid(real_key)) + "][" + repr(bracket_expression) + "]"
            elif set_to_empty == 'object_checkboxes':
                continue
            else:
                if isinstance(data, basestring):
                    #data = fixunicode(data)
                    data = data.strip()
                    #logmessage("data is " + data)
                if data == "None" and set_to_empty is not None:
                    #logmessage("setting None; set_to_empty is " + unicode(set_to_empty))
                    test_data = None
                    data = "None"
                else:
                    test_data = data
                    data = repr(data)
            if known_datatypes[real_key] == 'object_checkboxes':
                do_append = True
        elif orig_key in known_datatypes:
            #logmessage("key " + key + " is in datatypes: " + known_datatypes[orig_key])
            if known_datatypes[orig_key] in ('boolean', 'checkboxes'):
                #logmessage("Processing boolean")
                if data == "True":
                    data = "True"
                    test_data = True
                else:
                    data = "False"
                    test_data = False
            elif known_datatypes[orig_key] == 'threestate':
                if data == "True":
                    data = "True"
                    test_data = True
                elif data == "None":
                    data = "None"
                    test_data = None
                else:
                    data = "False"
                    test_data = False
            elif known_datatypes[orig_key] in ('date', 'datetime'):
                if type(data) in (str, unicode):
                    data = data.strip()
                    if data != '':
                        try:
                            dateutil.parser.parse(data)
                        except:
                            validated = False
                            if known_datatypes[orig_key] == 'date':
                                field_error[orig_key] = word("You need to enter a valid date.")
                            else:
                                field_error[orig_key] = word("You need to enter a valid date and time.")
                            continue
                        test_data = data
                        is_date = True
                        data = 'docassemble.base.util.as_datetime(' + repr(data) + ')'
                    else:
                        data = repr('')
                else:
                    data = repr('')
            elif known_datatypes[orig_key] == 'time':
                if type(data) in (str, unicode):
                    data = data.strip()
                    if data != '':
                        try:
                            dateutil.parser.parse(data)
                        except:
                            validated = False
                            field_error[orig_key] = word("You need to enter a valid time.")
                            continue
                        test_data = data
                        is_date = True
                        data = 'docassemble.base.util.as_datetime(' + repr(data) + ').time()'
                    else:
                        data = repr('')
                else:
                    data = repr('')
            elif known_datatypes[orig_key] == 'integer':
                if data == '':
                    data = 0
                test_data = int(data)
                data = "int(" + repr(data) + ")"
            elif known_datatypes[orig_key] in ('ml', 'mlarea'):
                is_ml = True
            elif known_datatypes[orig_key] in ('number', 'float', 'currency', 'range'):
                if data == '':
                    data = 0.0
                if isinstance(data, basestring):
                    data = re.sub(r',', '', data)
                test_data = float(data)
                data = "float(" + repr(data) + ")"
            elif known_datatypes[orig_key] in ('object', 'object_radio'):
                if data == '' or set_to_empty:
                    continue
                data = "_internal['objselections'][" + repr(key) + "][" + repr(data) + "]"
            elif set_to_empty == 'object_checkboxes':
                continue    
            else:
                if isinstance(data, basestring):
                    #data = fixunicode(data)
                    data = data.strip()
                    #logmessage("data is " + data)
                test_data = data
                data = repr(data)
        elif key == "_multiple_choice":
            #logmessage("key is multiple choice")
            data = "int(" + repr(data) + ")"
        else:
            #logmessage("key is not in datatypes where datatypes is " + str(known_datatypes))
            data = repr(data)
        if key == "_multiple_choice":
            #interview.assemble(user_dict, interview_status)
            #if interview_status.question.question_type == "multiple_choice" and not hasattr(interview_status.question.fields[0], 'saveas'):
                #key = '_internal["answers"]["' + interview_status.question.name + '"]'
            if '_question_name' in post_data:
                key = '_internal["answers"][' + repr(post_data['_question_name']) + ']'
            #else:
                #continue
                #error_messages.append(("error", "Error: multiple choice values were supplied, but docassemble was not waiting for an answer to a multiple choice question."))
        if is_date:
            #logmessage("index: doing import docassemble.base.util")
            try:
                exec("import docassemble.base.util", user_dict)
            except Exception as errMess:
                error_messages.append(("error", "Error: " + unicode(errMess)))
        if is_ml:
            #logmessage("index: doing import docassemble.base.util")
            try:
                exec("import docassemble.base.util", user_dict)
            except Exception as errMess:
                error_messages.append(("error", "Error: " + unicode(errMess)))
            if orig_key in ml_info and 'train' in ml_info[orig_key]:
                if not ml_info[orig_key]['train']:
                    use_for_training = 'False'
                else:
                    use_for_training = 'True'
            else:
                use_for_training = 'True'
            if orig_key in ml_info and 'group_id' in ml_info[orig_key]:
                data = 'docassemble.base.util.DAModel(' + repr(key) + ', group_id=' + repr(ml_info[orig_key]['group_id']) + ', text=' + repr(data) + ', store=' + repr(interview.get_ml_store()) + ', use_for_training=' + use_for_training + ')'
            else:
                data = 'docassemble.base.util.DAModel(' + repr(key) + ', text=' + repr(data) + ', store=' + repr(interview.get_ml_store()) + ', use_for_training=' + use_for_training + ')'
        if set_to_empty:
            if set_to_empty == 'checkboxes':
                try:
                    exec("import docassemble.base.core", user_dict)
                except Exception as errMess:
                    error_messages.append(("error", "Error: " + unicode(errMess)))
                data = 'docassemble.base.core.DADict(' + repr(key) + ', auto_gather=False, gathered=True)'
            else:
                data = 'None'
        if do_append and not set_to_empty:
            key_to_use = from_safeid(real_key)
            if do_opposite:
                the_string = 'if ' + data + ' in ' + key_to_use + '.elements:\n    ' + key_to_use + '.remove(' + data + ')'
            else:
                the_string = 'if ' + data + ' not in ' + key_to_use + '.elements:\n    ' + key_to_use + '.append(' + data + ')'
        else:
            #logmessage("data is " + data)
            vars_set.add(key)
            the_string = key + ' = ' + data
            if orig_key in field_numbers and the_question is not None and len(the_question.fields) > field_numbers[orig_key] and hasattr(the_question.fields[field_numbers[orig_key]], 'validate'):
                #logmessage("field " + orig_key + " has validation function")
                field_name = safeid('_field_' + str(field_numbers[orig_key]))
                if field_name in post_data:
                    the_key = field_name
                else:
                    the_key = orig_key
                the_func = eval(the_question.fields[field_numbers[orig_key]].validate['compute'], user_dict)
                try:
                    the_result = the_func(test_data)
                    #logmessage("the result was " + str(the_result))
                    if not the_result:
                        field_error[the_key] = word("Please enter a valid value.")
                        validated = False
                        continue
                except Exception as errstr:
                    #logmessage("the result was an exception")
                    field_error[the_key] = unicode(errstr)
                    validated = False
                    continue
        #logmessage("2Doing " + str(the_string))
        try:
            exec(the_string, user_dict)
            if not changed:
                steps += 1
                user_dict['_internal']['steps'] = steps
                changed = True
        except Exception as errMess:
            error_messages.append(("error", "Error: " + unicode(errMess)))
            try:
                logmessage("Error: " + unicode(errMess))
            except:
                pass
    if validated:
        #for orig_key in blank_fields:
            #key = myb64unquote(orig_key)
            #logmessage("Found a blank field " + key + " of type " + known_datatypes[orig_key])
        for orig_key in empty_fields:
            key = myb64unquote(orig_key)
            #logmessage("3Doing empty key " + str(key))
            vars_set.add(key + '.gathered')
            if empty_fields[orig_key] == 'object_checkboxes':
                docassemble.base.parse.ensure_object_exists(key, 'object_checkboxes', user_dict)
                exec(key + '.clear()' , user_dict)
                exec(key + '.gathered = True' , user_dict)
            elif empty_fields[orig_key] in ('object', 'object_radio'):
                vars_set.add(key)
                try:
                    eval(key, user_dict)
                except:
                    exec(key + ' = None' , user_dict)
        if the_question is not None and the_question.validation_code:
            try:
                exec(the_question.validation_code, user_dict)
            except Exception as validation_error:
                the_error_message = unicode(validation_error)
                if the_error_message == '':
                    the_error_message = word("Please enter a valid value.")
                error_messages.append(("error", the_error_message))
                validated = False
    if validated:
        if '_files_inline' in post_data:
            fileDict = json.loads(myb64unquote(post_data['_files_inline']))
            if type(fileDict) is not dict:
                raise DAError("inline files was not a dict")
            file_fields = fileDict['keys']
            has_invalid_fields = False
            should_assemble_now = False
            for orig_file_field in file_fields:
                if orig_file_field in known_varnames:
                    orig_file_field = known_varnames[orig_file_field]
                if orig_file_field not in visible_fields:
                    continue
                try:
                    file_field = from_safeid(orig_file_field)
                except:
                    error_messages.append(("error", "Error: Invalid file_field: " + orig_file_field))
                    break
                if match_invalid.search(file_field):
                    has_invalid_fields = True
                    error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                    break
                if key_requires_preassembly.search(file_field):
                    should_assemble_now = True
            if not has_invalid_fields:
                #logmessage("4Doing import docassemble.base.core")
                initial_string = 'import docassemble.base.core'
                try:
                    exec(initial_string, user_dict)
                except Exception as errMess:
                    error_messages.append(("error", "Error: " + unicode(errMess)))
                if something_changed and should_assemble_now and not should_assemble:
                    #logmessage("index: assemble 5")
                    interview.assemble(user_dict, interview_status)
                for orig_file_field_raw in file_fields:
                    if orig_file_field_raw in known_varnames:
                        orig_file_field_raw = known_varnames[orig_file_field_raw]
                    if orig_file_field_raw not in visible_fields:
                        continue
                    if not validated:
                        break
                    orig_file_field = orig_file_field_raw
                    var_to_store = orig_file_field_raw
                    if orig_file_field not in fileDict['values'] and len(known_varnames):
                        for key, val in known_varnames.iteritems():
                            if val == orig_file_field_raw:
                                orig_file_field = key
                                var_to_store = val
                                break
                    if orig_file_field in fileDict['values']:
                        the_files = fileDict['values'][orig_file_field]
                        if the_files:
                            files_to_process = list()
                            for the_file in the_files:
                                temp_file = tempfile.NamedTemporaryFile(prefix="datemp", delete=False)
                                start_index = 0
                                char_index = 0
                                for char in the_file['content']:
                                    char_index += 1
                                    if char == ',':
                                        start_index = char_index
                                        break
                                temp_file.write(codecs.decode(the_file['content'][start_index:], 'base64'))
                                temp_file.close()
                                filename = secure_filename(the_file['name'])
                                extension, mimetype = get_ext_and_mimetype(filename)
                                try:
                                    img = Image.open(temp_file.name)
                                    the_format = img.format.lower()
                                    the_format = re.sub(r'jpeg', 'jpg', the_format)
                                except:
                                    the_format = extension
                                    logmessage("Could not read file type from file " + str(filename))
                                if the_format != extension:
                                    filename = re.sub(r'\.[^\.]+$', '', filename) + '.' + the_format
                                    extension, mimetype = get_ext_and_mimetype(filename)
                                file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                                saved_file = SavedFile(file_number, extension=extension, fix=True)
                                process_file(saved_file, temp_file.name, mimetype, extension)
                                files_to_process.append((filename, file_number, mimetype, extension))
                            try:
                                file_field = from_safeid(var_to_store)
                            except:
                                error_messages.append(("error", "Error: Invalid file_field: " + var_to_store))
                                break
                            if match_invalid.search(file_field):
                                error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                                break
                            if len(files_to_process) > 0:
                                elements = list()
                                indexno = 0
                                for (filename, file_number, mimetype, extension) in files_to_process:
                                    elements.append("docassemble.base.core.DAFile(" + repr(file_field + "[" + str(indexno) + "]") + ", filename=" + repr(filename) + ", number=" + str(file_number) + ", make_pngs=True, mimetype=" + repr(mimetype) + ", extension=" + repr(extension) + ")")
                                    indexno += 1
                                the_file_list = "docassemble.base.core.DAFileList(" + repr(file_field) + ", elements=[" + ", ".join(elements) + "])"
                                #logmessage("field_numbers is " + repr(field_numbers))
                                #logmessage("orig_file_field is " + repr(orig_file_field))
                                if orig_file_field in field_numbers and the_question is not None and len(the_question.fields) > field_numbers[orig_file_field] and hasattr(the_question.fields[field_numbers[orig_file_field]], 'validate'):
                                    #logmessage("field " + orig_file_field + " has validation function")
                                    the_key = orig_file_field
                                    the_func = eval(the_question.fields[field_numbers[orig_file_field]].validate['compute'], user_dict)
                                    try:
                                        the_result = the_func(eval(the_file_list))
                                        #logmessage("the result was " + str(the_result))
                                        if not the_result:
                                            field_error[the_key] = word("Please enter a valid value.")
                                            validated = False
                                            break
                                    except Exception as errstr:
                                        #logmessage("the result was an exception")
                                        field_error[the_key] = unicode(errstr)
                                        validated = False
                                        break
                                the_string = file_field + " = " + the_file_list
                            else:
                                the_string = file_field + " = None"
                            #logmessage("5Doing " + the_string)
                            vars_set.add(file_field)
                            try:
                                exec(the_string, user_dict)
                                if not changed:
                                    steps += 1
                                    user_dict['_internal']['steps'] = steps
                                    changed = True
                            except Exception as errMess:
                                sys.stderr.write("Error: " + unicode(errMess) + "\n")
                                error_messages.append(("error", "Error: " + unicode(errMess)))
        if '_files' in post_data:
            file_fields = json.loads(myb64unquote(post_data['_files'])) #post_data['_files'].split(",")
            has_invalid_fields = False
            should_assemble_now = False
            for orig_file_field in file_fields:
                if orig_file_field in known_varnames:
                    orig_file_field = known_varnames[orig_file_field]
                if orig_file_field not in visible_fields:
                    continue
                try:
                    file_field = from_safeid(orig_file_field)
                except:
                    error_messages.append(("error", "Error: Invalid file_field: " + orig_file_field))
                    break
                if match_invalid.search(file_field):
                    has_invalid_fields = True
                    error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                    break
                if key_requires_preassembly.search(file_field):
                    should_assemble_now = True
            if not has_invalid_fields:
                initial_string = 'import docassemble.base.core'
                try:
                    exec(initial_string, user_dict)
                except Exception as errMess:
                    error_messages.append(("error", "Error: " + unicode(errMess)))
                if something_changed and should_assemble_now and not should_assemble:
                    #logmessage("index: assemble 6")
                    interview.assemble(user_dict, interview_status)
                for orig_file_field_raw in file_fields:
                    if orig_file_field_raw in known_varnames:
                        orig_file_field_raw = known_varnames[orig_file_field_raw]
                    if orig_file_field_raw not in visible_fields:
                        continue
                    if not validated:
                        break
                    orig_file_field = orig_file_field_raw
                    var_to_store = orig_file_field_raw
                    if orig_file_field not in request.files and len(known_varnames):
                        for key, val in known_varnames.iteritems():
                            if val == orig_file_field_raw:
                                orig_file_field = key
                                var_to_store = val
                                break
                    if orig_file_field in request.files:
                        the_files = request.files.getlist(orig_file_field)
                        if the_files:
                            files_to_process = list()
                            for the_file in the_files:
                                if is_ajax:
                                    return_fake_html = True
                                filename = secure_filename(the_file.filename)
                                file_number = get_new_file_number(session.get('uid', None), filename, yaml_file_name=yaml_filename)
                                extension, mimetype = get_ext_and_mimetype(filename)
                                # original_extension = extension
                                # if extension == 'gif':
                                #     extension == 'png'
                                #     mimetype = 'image/png'
                                #     filename = re.sub(r'\.gif$', '.png', filename, re.IGNORECASE)
                                saved_file = SavedFile(file_number, extension=extension, fix=True)
                                temp_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.' + extension, delete=False)
                                the_file.save(temp_file.name)
                                process_file(saved_file, temp_file.name, mimetype, extension)
                                #sys.stderr.write("Upload was processed\n")
                                files_to_process.append((filename, file_number, mimetype, extension))
                            try:
                                file_field = from_safeid(var_to_store)
                            except:
                                error_messages.append(("error", "Error: Invalid file_field: " + var_to_store))
                                break
                            if match_invalid.search(file_field):
                                error_messages.append(("error", "Error: Invalid character in file_field: " + file_field))
                                break
                            if len(files_to_process) > 0:
                                elements = list()
                                indexno = 0
                                for (filename, file_number, mimetype, extension) in files_to_process:
                                    elements.append("docassemble.base.core.DAFile(" + repr(file_field + '[' + str(indexno) + ']') + ", filename=" + repr(filename) + ", number=" + str(file_number) + ", make_pngs=True, mimetype=" + repr(mimetype) + ", extension=" + repr(extension) + ")")
                                    indexno += 1
                                the_file_list = "docassemble.base.core.DAFileList(" + repr(file_field) + ", elements=[" + ", ".join(elements) + "])"
                                #logmessage("field_numbers is " + repr(field_numbers))
                                #logmessage("orig_file_field is " + repr(orig_file_field))
                                if orig_file_field in field_numbers and the_question is not None and len(the_question.fields) > field_numbers[orig_file_field] and hasattr(the_question.fields[field_numbers[orig_file_field]], 'validate'):
                                    #logmessage("field " + orig_file_field + " has validation function")
                                    the_key = orig_file_field
                                    the_func = eval(the_question.fields[field_numbers[orig_file_field]].validate['compute'], user_dict)
                                    try:
                                        the_result = the_func(eval(the_file_list))
                                        #logmessage("the result was " + str(the_result))
                                        if not the_result:
                                            field_error[the_key] = word("Please enter a valid value.")
                                            validated = False
                                            break
                                    except Exception as errstr:
                                        #logmessage("the result was an exception")
                                        field_error[the_key] = unicode(errstr)
                                        validated = False
                                        break
                                the_string = file_field + " = " + the_file_list
                            else:
                                the_string = file_field + " = None"
                            #logmessage("6Doing " + the_string)
                            vars_set.add(file_field)
                            if validated:
                                try:
                                    exec(the_string, user_dict)
                                    if not changed:
                                        steps += 1
                                        user_dict['_internal']['steps'] = steps
                                        changed = True
                                except Exception as errMess:
                                    sys.stderr.write("Error: " + unicode(errMess) + "\n")
                                    error_messages.append(("error", "Error: " + unicode(errMess)))
        if validated:
            if 'informed' in request.form:
                user_dict['_internal']['informed'][the_user_id] = dict()
                for key in request.form['informed'].split(','):
                    user_dict['_internal']['informed'][the_user_id][key] = 1
            if changed and '_question_name' in post_data and post_data['_question_name'] not in user_dict['_internal']['answers']:
                try:
                    interview.questions_by_name[post_data['_question_name']].mark_as_answered(user_dict)
                except:
                    logmessage("index: question name could not be found")
            #logmessage("start: event_stack is " + repr(user_dict['_internal']['event_stack']))
            if '_event' in post_data and 'event_stack' in user_dict['_internal']:
                events_list = json.loads(myb64unquote(post_data['_event']))
                #logmessage("events_list was " + repr(events_list))
                if len(events_list):
                    session_uid = interview_status.current_info['user']['session_uid']
                    if session_uid in user_dict['_internal']['event_stack'] and len(user_dict['_internal']['event_stack'][session_uid]):
                        for event_name in events_list:
                            if user_dict['_internal']['event_stack'][session_uid][0]['action'] == event_name:
                                user_dict['_internal']['event_stack'][session_uid].pop(0)
                                if 'action' in interview_status.current_info and interview_status.current_info['action'] == event_name:
                                    del interview_status.current_info['action']
                                    if 'arguments' in interview_status.current_info:
                                        del interview_status.current_info['arguments']
                                #logmessage("popped!")
                                break
            #logmessage("vars_set was " + repr(vars_set))
            if len(vars_set) and 'event_stack' in user_dict['_internal']:
                session_uid = interview_status.current_info['user']['session_uid']
                if session_uid in user_dict['_internal']['event_stack'] and len(user_dict['_internal']['event_stack'][session_uid]):
                    for var_name in vars_set:
                        if user_dict['_internal']['event_stack'][session_uid][0]['action'] == var_name:
                            #logmessage("popped based on vars_set!")
                            user_dict['_internal']['event_stack'][session_uid].pop(0)
            #logmessage("finish: event_stack is " + repr(user_dict['_internal']['event_stack']))
        else:
            steps, user_dict, is_encrypted = fetch_user_dict(user_code, yaml_filename, secret=secret)
    else:
        steps, user_dict, is_encrypted = fetch_user_dict(user_code, yaml_filename, secret=secret)
    # restore this, maybe
    #if next_action:
    #    the_next_action = next_action.pop(0)
    #    interview_status.next_action = next_action
    #    interview_status.current_info.update(the_next_action)
    #startTime = int(round(time.time() * 1000))
    #g.assembly_start = time.time()
    #logmessage("index: assemble 7")
    interview.assemble(user_dict, interview_status, old_user_dict)
    #g.assembly_end = time.time()
    #endTime = int(round(time.time() * 1000))
    #logmessage(str(endTime - startTime))
    current_language = docassemble.base.functions.get_language()
    if current_language != DEFAULT_LANGUAGE:
        session['language'] = current_language
    if not interview_status.can_go_back:
        user_dict['_internal']['steps_offset'] = steps
    # if len(interview_status.attachments) > 0:
    #     #logmessage("Updating attachment info")
    #     update_attachment_info(user_code, user_dict, interview_status, secret)
    # restore this, maybe
    #if interview_status.question.question_type == "review" and len(interview_status.question.fields_used):
    #    next_action_review = dict(action=list(interview_status.question.fields_used)[0], arguments=dict())
    #else:
    #    next_action_review = None
    if interview_status.question.question_type == "new_session":
        manual_checkout()
        referer = user_dict['_internal'].get('referer', None)
        user_dict = fresh_dictionary()
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, interface=the_interface))
        release_lock(user_code, yaml_filename)
        user_code, user_dict = reset_session(yaml_filename, secret)
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
        if 'visitor_secret' not in request.cookies:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        steps = 1
        changed = False
        #logmessage("index: assemble 7.9")
        interview.assemble(user_dict, interview_status)        
    if interview_status.question.question_type == "restart":
        manual_checkout()
        url_args = user_dict['url_args']
        referer = user_dict['_internal'].get('referer', None)
        user_dict = fresh_dictionary()
        user_dict['url_args'] = url_args
        user_dict['_internal']['referer'] = referer
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml=yaml_filename, req=request, interface=the_interface))
        reset_user_dict(user_code, yaml_filename)
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret)
        #if current_user.is_authenticated and 'visitor_secret' not in request.cookies:
        if 'visitor_secret' not in request.cookies:
            save_user_dict_key(user_code, yaml_filename)
            session['key_logged'] = True
        steps = 1
        changed = False
        #logmessage("index: assemble 8")
        interview.assemble(user_dict, interview_status)
    will_save = True
    if interview_status.question.question_type == "refresh":
        #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        release_lock(user_code, yaml_filename)
        return do_refresh(is_ajax, yaml_filename)
    if interview_status.question.question_type == "signin":
        #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        release_lock(user_code, yaml_filename)
        return do_redirect(url_for('user.login', next=url_for('index', i=yaml_filename, session=user_code)), is_ajax, is_json)
    if interview_status.question.question_type == "register":
        #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        release_lock(user_code, yaml_filename)
        return do_redirect(url_for('user.register', next=url_for('index', i=yaml_filename, session=user_code)), is_ajax, is_json)
    if interview_status.question.question_type == "leave":
        save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        release_lock(user_code, yaml_filename)
        if interview_status.questionText != '':
            return do_redirect(interview_status.questionText, is_ajax, is_json)
        else:
            return do_redirect(exit_page, is_ajax, is_json)
    if interview_status.question.interview.use_progress_bar and interview_status.question.progress is not None and interview_status.question.progress > user_dict['_internal']['progress']:
        user_dict['_internal']['progress'] = interview_status.question.progress
    if interview_status.question.interview.use_navigation and interview_status.question.section is not None:
        if user_dict['nav'].set_section(interview_status.question.section):
            pass
            #logmessage("Section changed")
            #changed = True
            #steps += 1
    if interview_status.question.question_type == "exit":
        manual_checkout()
        if interview_status.question.question_type == "exit":
            reset_user_dict(user_code, yaml_filename)
        delete_session_for_interview()
        release_lock(user_code, yaml_filename)
        if interview_status.questionText != '':
            response = do_redirect(interview_status.questionText, is_ajax, is_json)
        else:
            response = do_redirect(exit_page, is_ajax, is_json)
        return response
    if interview_status.question.question_type in ("exit_logout", "logout"):
        manual_checkout()
        if interview_status.question.question_type == "exit_logout":
            reset_user_dict(user_code, yaml_filename)
        #else:
        #    save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        release_lock(user_code, yaml_filename)
        delete_session()
        if interview_status.questionText != '':
            response = do_redirect(interview_status.questionText, is_ajax, is_json)
        else:
            response = do_redirect(exit_page, is_ajax, is_json)
        if current_user.is_authenticated:
            flask_user.signals.user_logged_out.send(current_app._get_current_object(), user=current_user)
            logout_user()
        delete_session()
        response.set_cookie('visitor_secret', '', expires=0)
        response.set_cookie('secret', '', expires=0)
        response.set_cookie('session', '', expires=0)
        return response
    if interview_status.question.question_type == "response":
        if is_ajax:
            # Duplicative to save here?
            #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
            release_lock(user_code, yaml_filename)
            return jsonify(action='resubmit', csrf_token=generate_csrf())
        else:
            if hasattr(interview_status.question, 'all_variables'):
                if hasattr(interview_status.question, 'include_internal'):
                    include_internal = interview_status.question.include_internal
                else:
                    include_internal = False
                response_to_send = make_response(docassemble.base.functions.dict_as_json(user_dict, include_internal=include_internal).encode('utf8'), '200 OK')
            elif hasattr(interview_status.question, 'binaryresponse'):
                response_to_send = make_response(interview_status.question.binaryresponse, '200 OK')
            else:
                response_to_send = make_response(interview_status.questionText.encode('utf8'), '200 OK')
            response_to_send.headers['Content-Type'] = interview_status.extras['content_type']
        if set_cookie:
            response_to_send.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
    elif interview_status.question.question_type == "sendfile":
        if is_ajax:
            #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
            release_lock(user_code, yaml_filename)
            return jsonify(action='resubmit', csrf_token=generate_csrf())
        else:
            # Duplicative to save here?  Just for the 404?
            #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
            if interview_status.question.response_file is not None:
                the_path = interview_status.question.response_file.path()
            else:
                logmessage("index: could not send file because the response was None")
                abort(404)                
            if not os.path.isfile(the_path):
                logmessage("index: could not send file because file (" + the_path + ") not found")
                abort(404)
            response_to_send = send_file(the_path, mimetype=interview_status.extras['content_type'])
            response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        if set_cookie:
            response_to_send.set_cookie('secret', secret)
        if expire_visitor_secret:
            response.set_cookie('visitor_secret', '', expires=0)
    elif interview_status.question.question_type == "redirect":
        # Duplicative to save here?
        #save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted)
        response_to_send = do_redirect(interview_status.questionText, is_ajax, is_json)
    else:
        response_to_send = None
    # Why do this?  To prevent loops of redirects?
    # Commenting this line out is necessary for force-gather.yml to work.
    # user_dict['_internal']['answers'] = dict()
    if (not interview_status.followed_mc) and len(user_dict['_internal']['answers']):
        user_dict['_internal']['answers'].clear()
    # Not sure we need this anymore
    # if interview_status.question.name and interview_status.question.name in user_dict['_internal']['answers']:
    #     del user_dict['_internal']['answers'][interview_status.question.name]
    if action and not changed:
        changed = True
        steps += 1
        user_dict['_internal']['steps'] = steps
        #logmessage("Incrementing steps because action")
    if changed and interview_status.question.interview.use_progress_bar and interview_status.question.progress is None:
        advance_progress(user_dict)
    #logmessage("index: saving user dict where encrypted is " + str(encrypted))
    save_user_dict(user_code, user_dict, yaml_filename, secret=secret, changed=changed, encrypt=encrypted, steps=steps)
    if user_dict.get('multi_user', False) is True and encrypted is True:
        #logmessage("index: post interview, encryption should be False")
        encrypted = False
        session['encrypted'] = encrypted
        decrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
    # else:
    #     logmessage("index: post interview, no detection of encryption should be False")
    if user_dict.get('multi_user', False) is False and encrypted is False:
        #logmessage("index: post interview, encryption should be True")
        encrypt_session(secret, user_code=session.get('uid', None), filename=session.get('i', None))
        encrypted = True
        session['encrypted'] = encrypted
    # else:
    #     logmessage("index: post interview, no detection of encryption should be True")
    if response_to_send is not None:
        release_lock(user_code, yaml_filename)
        return response_to_send
    flash_content = ""
    messages = get_flashed_messages(with_categories=True) + error_messages
    if messages and len(messages):
        flash_content += '<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">'
        for classname, message in messages:
            if classname == 'error':
                classname = 'danger'
            flash_content += '<div class="alert alert-' + classname + '"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>'
        flash_content += '</div>'
    if 'reload_after' in interview_status.extras:
        reload_after = 1000 * int(interview_status.extras['reload_after'])
    else:
        reload_after = 0
    if interview_status.question.can_go_back and (steps - user_dict['_internal']['steps_offset']) > 1:
        allow_going_back = True
    else:
        allow_going_back = False
    if hasattr(interview_status.question, 'id'):
        question_id = interview_status.question.id
    else:
        question_id = None;
    interview_package = re.sub(r'^docassemble\.', '', re.sub(r':.*', '', yaml_filename))
    interview_filename = re.sub(r'\.ya?ml$', '', re.sub(r'.*[:\/]', '', yaml_filename), re.IGNORECASE)
    if not is_ajax:
        scripts = standard_scripts()
        if 'google maps api key' in google_config:
            api_key = google_config.get('google maps api key')
        elif 'api key' in google_config:
            api_key = google_config.get('api key')
        else:
            api_key = None
        if 'analytics id' in google_config:
            ga_id = google_config.get('analytics id')
        else:
            ga_id = None
        if api_key is not None:
            scripts += "\n" + '    <script async src="https://maps.googleapis.com/maps/api/js?key=' + api_key + '&libraries=places"></script>'
        if ga_id is not None:
            scripts += """
    <script async src="https://www.googletagmanager.com/gtag/js?id=""" + ga_id + """"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      function daPageview(){
        if (daQuestionID != null){
          gtag('config', """ + json.dumps(ga_id) + """, {'page_path': """ + json.dumps(interview_package) + """ + "/" + """ + json.dumps(interview_filename) + """ + "/" + daQuestionID.replace(/[^A-Za-z0-9]+/g, '_')});
        }
      }
    </script>
"""
        if 'javascript' in interview_status.question.interview.external_files:
            for packageref, fileref in interview_status.question.interview.external_files['javascript']:
                the_url = get_url_from_file_reference(fileref, _package=packageref)
                if the_url is not None:
                    scripts += "\n" + '    <script src="' + get_url_from_file_reference(fileref, _package=packageref) + '"></script>'
                else:
                    logmessage("index: could not find javascript file " + str(fileref))
        if interview_status.question.checkin is not None:
            do_action = json.dumps(interview_status.question.checkin)
        else:
            do_action = 'null'
        chat_available = user_dict['_internal']['livehelp']['availability']
        chat_mode = user_dict['_internal']['livehelp']['mode']
        #logmessage("index: chat_available is " + str(chat_available))
        if chat_available == 'unavailable':
            chat_status = 'off'
            session['chatstatus'] = 'off'
        elif chat_available == 'observeonly':
            chat_status = 'observeonly'
            session['chatstatus'] = 'observeonly'
        else:
            chat_status = chatstatus
        if chat_status in ('ready', 'on'):
            chat_status = 'ringing'
            session['chatstatus'] = 'ringing'
        if chat_status != 'off':
            send_changes = 'true'
        else:
            if do_action != 'null':
                send_changes = 'true'
            else:
                send_changes = 'false'
        if current_user.is_authenticated:
            user_id_string = str(current_user.id)
            if current_user.has_role('admin', 'developer', 'advocate'):
                is_user = 'false'
            else:
                is_user = 'true'
        else:
            user_id_string = 't' + str(session['tempuser'])
            is_user = 'true'
        if 'uid' in session and 'i' in session:
            if r.get('da:control:uid:' + str(session['uid']) + ':i:' + str(session['i']) + ':userid:' + str(the_user_id)) is not None:
                being_controlled = 'true'
            else:
                being_controlled = 'false'
        else:
            being_controlled = 'false'
        if debug_mode:
            debug_readability_help = """
            $("#readability-help").show();
            $("#readability-question").hide();
"""
            debug_readability_question = """
            $("#readability-help").hide();
            $("#readability-question").show();
"""
        #     debug_init = """
        # $("#showvariables").on('click', function(e){
        #   $(this).parent().parent().append($("<h4>").html(""" + json.dumps(word("Variables and values")) + """));
        #   $(this).parent().parent().append($('<iframe class="jsonvars" src=""" + '"' + url_for('get_variables') + '"' + """>'));
        #   $(this).remove();
        #   e.preventDefault();
        # });"""
        else:
            debug_readability_help = ''
            debug_readability_question = ''
        if interview_status.question.interview.force_fullscreen is True or (re.search(r'mobile', str(interview_status.question.interview.force_fullscreen).lower()) and is_mobile_or_tablet()):
            forceFullScreen = """
          if (data.steps > 1 && window != top) {
            top.location.href = location.href;
            return;
          }
"""
        else:
            forceFullScreen = ''
        the_checkin_interval = interview_status.question.interview.options.get('checkin interval', CHECKIN_INTERVAL)
#      //var daNextAction = """ + json.dumps(next_action_review) + """;
        scripts += """
    <script type="text/javascript" charset="utf-8">
      var map_info = null;
      var whichButton = null;
      var socket = null;
      var chatHistory = [];
      var daCheckinCode = null;
      var daCheckingIn = 0;
      var daShowingHelp = 0;
      var daAllowGoingBack = """ + ('true' if allow_going_back else 'false') + """;
      var daSteps = """ + str(steps) + """;
      var daIsUser = """ + is_user + """;
      var daChatStatus = """ + json.dumps(chat_status) + """;
      var daChatAvailable = """ + json.dumps(chat_available) + """;
      var daChatPartnersAvailable = 0;
      var daPhoneAvailable = false;
      var daChatMode = """ + json.dumps(chat_mode) + """;
      var daSendChanges = """ + send_changes + """;
      var daInitialized = false;
      var notYetScrolled = true;
      var daBeingControlled = """ + being_controlled + """;
      var daInformedChanged = false;
      var daInformed = """ + json.dumps(user_dict['_internal']['informed'].get(user_id_string, dict())) + """;
      var daShowingSpinner = false;
      var daSpinnerTimeout = null;
      var daSubmitter = null;
      var daUsingGA = """ + ("true" if ga_id is not None else 'false') + """;
      var daDoAction = """ + do_action + """;
      var daQuestionID = """ + json.dumps(question_id) + """;
      var daCsrf = """ + json.dumps(generate_csrf()) + """;
      var daShowIfInProcess = false;
      var fieldsToSkip = ['_checkboxes', '_empties', '_ml_info', '_back_one', '_files', '_files_inline', '_question_name', '_the_image', '_save_as', '_success', '_datatypes', '_event', '_visible', '_tracker', '_track_location', '_varnames', '_next_action', '_next_action_to_set', 'ajax', 'json', 'informed', 'csrf_token', '_action'];
      var varlookup;
      var varlookuprev;
      var valLookup;
      function getField(fieldName){
        if (typeof valLookup[fieldName] == "undefined"){
          var fieldNameEscaped = btoa(fieldName);//.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
          if ($("[name='" + fieldNameEscaped + "']").length == 0 && typeof varlookup[btoa(fieldName)] != "undefined"){
            fieldName = varlookup[btoa(fieldName)];
            fieldNameEscaped = fieldName;//.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
          }
          var varList = $("[name='" + fieldNameEscaped + "']");
          if (varList.length == 0){
            varList = $("input[type='radio'][name='" + fieldNameEscaped + "']");
          }
          if (varList.length == 0){
            varList = $("input[type='checkbox'][name='" + fieldNameEscaped + "']");
          }
          if (varList.length > 0){
            elem = varList[0];
          }
          else{
            return null;
          }
        }
        else {
          elem = valLookup[fieldName];
        }
        return elem;
      }
      function setField(fieldName, val){
        var elem = getField(fieldName);
        if (elem == null){
          console.log('setField: reference to non-existent field ' + fieldName);
          return;
        }
        if ($(elem).attr('type') == "checkbox"){
          if (val){
            if ($(elem).prop('checked') != true){
              $(elem).prop('checked', true);
              $(elem).trigger('change');
            }
          }
          else{
            if ($(elem).prop('checked') != false){
              $(elem).prop('checked', false);
              $(elem).trigger('change');
            }
          }
        }
        else if ($(elem).attr('type') == "radio"){
          var fieldNameEscaped = $(elem).attr('name').replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
          var wasSet = false;
          $("input[name='" + fieldNameEscaped + "']").each(function(){
            if ($(this).val() == val){
              if ($(this).prop('checked') != true){
                $(this).prop('checked', true);
                $(this).trigger('change');
              }
              wasSet = true;
              return false;
            }
          });
          if (!wasSet){
            console.log('setField: could not set radio button ' + fieldName + ' to ' + val);
          }
        }
        else{
          if ($(elem).val() != val){
            $(elem).val(val);
            $(elem).trigger('change');
          }
        }
      }
      function val(fieldName){
        var elem = getField(fieldName);
        if (elem == null){
          return null;
        }
        var showifParents = $(elem).parents(".jsshowif");
        if (showifParents.length !== 0 && !($(showifParents[0]).data("isVisible") == '1')){
          theVal = null;
        }
        else if ($(elem).attr('type') == "checkbox"){
          if ($(elem).prop('checked')){
            theVal = true;
          }
          else{
            theVal = false;
          }
        }
        else if ($(elem).attr('type') == "radio"){
          var fieldNameEscaped = $(elem).attr('name').replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
          theVal = $("input[name='" + fieldNameEscaped + "']:checked").val();
          if (typeof(theVal) == 'undefined'){
            theVal = null;
          }
          else{
            if (theVal == 'True'){
              theVal = true;
            }
            else if (theVal == 'False'){
              theVal = false;
            }
          }
        }
        else{
          theVal = $(elem).val();
        }
        return theVal;
      }
      function formAsJSON(){
        var formData = $("#daform").serializeArray();
        var data = Object();
        var n = formData.length;
        for (var i = 0; i < n; ++i){
          var key = formData[i]['name'];
          var val = formData[i]['value'];
          if ($.inArray(key, fieldsToSkip) != -1 || key.startsWith('_ignore')){
            continue;
          }
          if (typeof varlookuprev[key] != "undefined"){
            data[atob(varlookuprev[key])] = val;
          }
          else{
            data[atob(key)] = val;
          }
        }
        return JSON.stringify(data);
      }
      var daMessageLog = JSON.parse(atob(""" + json.dumps(safeid(json.dumps(docassemble.base.functions.get_message_log()))) + """));
      function preloadImage(url){
        var img = new Image();
        img.src = url;
      }
      preloadImage('""" + str(url_for('static', filename='app/chat.ico')) + """');
      function show_help_tab(){
          $('#helptoggle').tab('show');
      }
      function flash(message, priority){
        if (priority == null){
          priority = 'info'
        }
        if (!$("#flash").length){
          $("#dabody").append('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash"></div>');
        }
        $("#flash").append('<div class="alert alert-' + priority + ' alert-interlocutory"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>');
        if (priority == 'success'){
          setTimeout(function(){
            $("#flash .alert-success").hide(300, function(){
              $(this).remove();
            });
          }, 3000);
        }
      }
      function url_action(action, args){
          if (args == null){
              args = {};
          }
          data = {action: action, arguments: args};
          return '?action=' + encodeURIComponent(btoa(JSON.stringify(data)));
      }
      function url_action_call(action, args, callback){
          if (args == null){
              args = {};
          }
          if (callback == null){
              callback = function(){};
          }
          var data = {action: action, arguments: args};
          $.ajax({
            type: "GET",
            url: "?action=" + encodeURIComponent(btoa(JSON.stringify(data))),
            success: callback,
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
      }
      function url_action_perform(action, args){
          if (args == null){
              args = {};
          }
          var data = {action: action, arguments: args};
          daSpinnerTimeout = setTimeout(showSpinner, 1000);
          $.ajax({
            type: "POST",
            url: """ + '"' + url_for('index') + '"' + """,
            data: $.param({_action: btoa(JSON.stringify(data)), csrf_token: daCsrf, ajax: 1}),
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, $("#daform"), 1);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            },
            dataType: 'json'
          });
      }
      function url_action_perform_with_next(action, args, next_data){
          //console.log("url_action_perform_with_next: " + action + " | " + next_data)
          if (args == null){
              args = {};
          }
          var data = {action: action, arguments: args};
          daSpinnerTimeout = setTimeout(showSpinner, 1000);
          $.ajax({
            type: "POST",
            url: """ + '"' + url_for('index') + '"' + """,
            data: $.param({_action: btoa(JSON.stringify(data)), _next_action_to_set: btoa(JSON.stringify(next_data)), csrf_token: daCsrf, ajax: 1}),
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, $("#daform"), 1);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            },
            dataType: 'json'
          });
      }
      function get_interview_variables(callback){
        if (callback == null){
          callback = function(){};
        }
        $.ajax({
          type: "GET",
          url: """ + '"' + url_for('get_variables') + '"' + """,
          success: callback,
          error: function(xhr, status, error){
            setTimeout(function(){
              daProcessAjaxError(xhr, status, error);
            }, 0);
          }
        });
      }
      function inform_about(subject){
        if (subject in daInformed || (subject != 'chatmessage' && !daIsUser)){
          return;
        }
        if (daShowingHelp && subject != 'chatmessage'){
          daInformed[subject] = 1;
          daInformedChanged = true;
          return;
        }
        if (daShowingHelp && subject == 'chatmessage'){
          return;
        }
        var target;
        var message;
        var waitPeriod = 3000;
        if (subject == 'chat'){
          target = "#daChatAvailable a";
          message = """ + json.dumps(word("Get help through live chat by clicking here.")) + """;
        }
        else if (subject == 'chatmessage'){
          target = "#daChatAvailable a";
          message = """ + json.dumps(word("A chat message has arrived.")) + """;
        }
        else if (subject == 'phone'){
          target = "#daPhoneAvailable a";
          message = """ + json.dumps(word("Click here to get help over the phone.")) + """;
        }
        else{
          return;
        }
        if (subject != 'chatmessage'){
          daInformed[subject] = 1;
          daInformedChanged = true;
        }
        $(target).popover({"content": message, "placement": "bottom", "trigger": "manual", "container": "body"});
        $(target).popover('show');
        setTimeout(function(){
          $(target).popover('dispose');
          $(target).removeAttr('title');
        }, waitPeriod);
      }
      // function daCloseSocket(){
      //   if (typeof socket !== 'undefined' && socket.connected){
      //     //socket.emit('terminate');
      //     //io.unwatch();
      //   }
      // }
      function publishMessage(data){
        var newDiv = document.createElement('li');
        $(newDiv).addClass("list-group-item");
        if (data.is_self){
          $(newDiv).addClass("list-group-item-warning dalistright");
        }
        else{
          $(newDiv).addClass("list-group-item-info");
        }
        //var newSpan = document.createElement('span');
        //$(newSpan).html(data.message);
        //$(newSpan).appendTo($(newDiv));
        //var newName = document.createElement('span');
        //$(newName).html(userNameString(data));
        //$(newName).appendTo($(newDiv));
        $(newDiv).html(data.message);
        $("#daCorrespondence").append(newDiv);
      }
      function scrollChat(){
        var chatScroller = $("#daCorrespondence");
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
          //console.log("Slow scrolling to " + height);
          if (height == 0){
            notYetScrolled = true;
            return;
          }
          chatScroller.animate({scrollTop: height}, 800);
        }
        else{
          console.log("scrollChat: error");
        }
      }
      function scrollChatFast(){
        var chatScroller = $("#daCorrespondence");
        if (chatScroller.length){
          var height = chatScroller[0].scrollHeight;
          if (height == 0){
            notYetScrolled = true;
            return;
          }
          //console.log("Scrolling to " + height + " where there are " + chatScroller[0].childElementCount + " children");
          chatScroller.scrollTop(height);
        }
        else{
          console.log("scrollChatFast: error");
        }
      }
      function daSender(){
        //console.log("daSender");
        if ($("#daMessage").val().length){
          socket.emit('chatmessage', {data: $("#daMessage").val()});
          $("#daMessage").val("");
          $("#daMessage").focus();
        }
        return false;
      }
      function show_control(mode){
        //console.log("You are now being controlled");
        if ($("body").hasClass("dacontrolled")){
          return;
        }
        $('input[type="submit"], button[type="submit"]').prop("disabled", true);
        $("body").addClass("dacontrolled");
        var newDiv = document.createElement('div');
        $(newDiv).addClass("top-alert col-xs-10 col-sm-7 col-md-6 col-lg-5 col-centered");
        $(newDiv).html(""" + json.dumps(word("Your screen is being controlled by an operator.")) + """)
        $(newDiv).attr('id', "controlAlert");
        $(newDiv).css("display", "none");
        $(newDiv).appendTo($("#dabody"));
        if (mode == 'animated'){
          $(newDiv).slideDown();
        }
        else{
          $(newDiv).show();
        }
      }
      function hide_control(){
        //console.log("You are no longer being controlled");
        if (! $("body").hasClass("dacontrolled")){
          return;
        }
        $('input[type="submit"], button[type="submit"]').prop("disabled", false);
        $("body").removeClass("dacontrolled");
        $("#controlAlert").html(""" + json.dumps(word("The operator is no longer controlling your screen.")) + """);
        setTimeout(function(){
          $("#controlAlert").slideUp(300, function(){
            $("#controlAlert").remove();
          });
        }, 2000);
      }
      function daInitializeSocket(){
        if (socket != null){
            if (socket.connected){
                //console.log("Calling connectagain");
                if (daChatStatus == 'ready'){
                  socket.emit('connectagain', {data: 1});
                }
                if (daBeingControlled){
                    show_control('animated');
                    socket.emit('start_being_controlled', {data: 1});
                }
            }
            else{
                //console.log('daInitializeSocket: socket.connect()');
                socket.connect();
            }
            return;
        }
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/wsinterview", {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/wsinterview" + location.port, {path: '/ws/socket.io'});
        }
        //console.log("daInitializeSocket: socket is " + socket);
        if (socket != null){
            socket.on('connect', function() {
                if (socket == null){
                    console.log("Error: socket is null");
                    return;
                }
                //console.log("Connected socket with sid " + socket.id);
                if (daChatStatus == 'ready'){
                    daChatStatus = 'on';
                    display_chat();
                    pushChanges();
                    //daTurnOnChat();
                    //console.log("Emitting chat_log from on connect");
                    socket.emit('chat_log', {data: 1});
                }
                if (daBeingControlled){
                    show_control('animated')
                    socket.emit('start_being_controlled', {data: 1});
                }
            });
            socket.on('chat_log', function(arg) {
                //console.log("Got chat_log");
                $("#daCorrespondence").html('');
                chatHistory = []; 
                var messages = arg.data;
                for (var i = 0; i < messages.length; ++i){
                    chatHistory.push(messages[i]);
                    publishMessage(messages[i]);
                }
                scrollChatFast();
            });
            socket.on('chatready', function(data) {
                //var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                //console.log('chatready');
            });
            socket.on('terminate', function() {
                //console.log("interview: terminating socket");
                socket.disconnect();
            });
            socket.on('controllerstart', function(){
              daBeingControlled = true;
              show_control('animated');
            });
            socket.on('controllerexit', function(){
              daBeingControlled = false;
              //console.log("Hiding control 2");
              hide_control();
              if (daChatStatus != 'on'){
                if (socket != null && socket.connected){
                  //console.log('Terminating interview socket because control over');
                  socket.emit('terminate');
                }
              }
            });
            socket.on('disconnect', function() {
                //console.log("Disconnected socket");
                //socket = null;
            });
            socket.on('reconnected', function() {
                //console.log("Reconnected");
                daChatStatus = 'on';
                display_chat();
                pushChanges();
                daTurnOnChat();
                //console.log("Emitting chat_log from reconnected");
                socket.emit('chat_log', {data: 1});
            });
            socket.on('mymessage', function(arg) {
                //console.log("Received " + arg.data);
                $("#daPushResult").html(arg.data);
            });
            socket.on('departure', function(arg) {
                //console.log("Departure " + arg.numpartners);
                if (arg.numpartners == 0){
                    daCloseChat();
                }
            });
            socket.on('chatmessage', function(arg) {
                //console.log("Received chat message " + arg.data);
                chatHistory.push(arg.data);
                publishMessage(arg.data);
                scrollChat();
                inform_about('chatmessage');
            });
            socket.on('newpage', function(incoming) {
                //console.log("newpage received");
                var data = incoming.obj;
                daProcessAjax(data, $("#daform"), 1);
            });
            socket.on('controllerchanges', function(data) {
                //console.log("controllerchanges: " + data.parameters);
                var valArray = Object();
                var values = JSON.parse(data.parameters);
                for (var i = 0; i < values.length; i++) {
                    valArray[values[i].name] = values[i].value;
                }
                //console.log("valArray is " + JSON.stringify(valArray));
                $("#daform").each(function(){
                    $(this).find(':input').each(function(){
                        var type = $(this).attr('type');
                        var id = $(this).attr('id');
                        var name = $(this).attr('name');
                        if (type == 'checkbox'){
                            if (name in valArray){
                                if (valArray[name] == 'True'){
                                    if ($(this).prop('checked') != true){
                                        $(this).prop('checked', true);
                                        $(this).trigger('change');
                                    }
                                }
                                else{
                                    if ($(this).prop('checked') != false){
                                        $(this).prop('checked', false);
                                        $(this).trigger('change');
                                    }
                                }
                            }
                            else{
                                if ($(this).prop('checked') != false){
                                    $(this).prop('checked', false);
                                    $(this).trigger('change');
                                }
                            }
                        }
                        else if (type == 'radio'){
                            if (name in valArray){
                                if (valArray[name] == $(this).val()){
                                    if ($(this).prop('checked') != true){
                                        $(this).prop('checked', true);
                                        $(this).trigger('change');
                                    }
                                }
                                else{
                                    if ($(this).prop('checked') != false){
                                        $(this).prop('checked', false);
                                        $(this).trigger('change');
                                    }
                                }
                            }
                        }
                        else if ($(this).data().hasOwnProperty('sliderMax')){
                            $(this).slider('setValue', parseInt(valArray[name]));
                        }
                        else{
                            if (name in valArray){
                                $(this).val(valArray[name]);
                            }
                        }
                    });
                });
                if (data.clicked){
                    //console.log("Need to click " + data.clicked);
                    $(data.clicked).prop("disabled", false);
                    $(data.clicked).addClass("click-selected");
                    if ($(data.clicked).prop("tagName") == 'A' && typeof $(data.clicked).attr('href') != 'undefined' && ($(data.clicked).attr('href').startsWith('javascript') || $(data.clicked).attr('href').startsWith('#'))){
                      setTimeout(function(){
                        $(data.clicked).removeClass("click-selected");
                      }, 2200);
                    }
                    setTimeout(function(){
                      //console.log("Clicking it now");
                      $(data.clicked).click();
                      //console.log("Clicked it.");
                    }, 200);
                }
            });
        }
      }
      var checkinSeconds = """ + str(the_checkin_interval) + """;
      var checkinInterval = null;
      var daReloader = null;
      var dadisable = null;
      var daChatRoles = """ + json.dumps(user_dict['_internal']['livehelp']['roles']) + """;
      var daChatPartnerRoles = """ + json.dumps(user_dict['_internal']['livehelp']['partner_roles']) + """;
      function unfake_html_response(text){
        text = text.replace(/^.*ABCDABOUNDARYSTARTABC/, '');
        text = text.replace(/ABCDABOUNDARYENDABC.*/, '');
        text = atob(text);
        return text;
      }
      function daValidationHandler(form){
        //form.submit();
        //console.log("daValidationHandler");
        var visibleElements = [];
        var seen = Object();
        $(form).find("input, select, textarea").filter(":not(:disabled)").each(function(){
          //console.log("Considering an element");
          if ($(this).attr('name') && $(this).attr('type') != "hidden" && (($(this).hasClass('labelauty') && $(this).parent().is(":visible")) || $(this).is(":visible"))){
            var theName = $(this).attr('name');
            //console.log("Including an element " + theName);
            if (!seen.hasOwnProperty(theName)){
              visibleElements.push(theName);
              seen[theName] = 1;
            }
          }
        });
        $(form).find("input[name='_visible']").val(btoa(JSON.stringify(visibleElements)));
        $(form).each(function(){
          $(this).find(':input').off('change', pushChanges);
        });
        $("meta[name=viewport]").attr('content', "width=device-width, minimum-scale=1.0, maximum-scale=1.0, initial-scale=1.0");
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
        dadisable = setTimeout(function(){
          $(form).find('input[type="submit"]').prop("disabled", true);
          $(form).find('button[type="submit"]').prop("disabled", true);
        }, 1);
        if (whichButton != null){
          $(".btn-da").each(function(){
            if (this != whichButton){
              $(this).removeClass("btn-primary btn-info btn-warning btn-danger btn-light");
              $(this).addClass("btn-secondary");
            }
          });
          if ($(whichButton).hasClass("btn-success")){
            $(whichButton).removeClass("btn-success");
            $(whichButton).addClass("btn-primary");
          }
          else{
            $(whichButton).removeClass("btn-primary btn-info btn-warning btn-danger btn-secondary btn-light");
            $(whichButton).addClass("btn-success");
          }
        }
        whichButton = null;
        if (daSubmitter != null){
          $('<input>').attr({
            type: 'hidden',
            name: daSubmitter.name,
            value: daSubmitter.value
          }).appendTo($(form));
        }
        if (daInformedChanged){
          $("<input>").attr({
            type: 'hidden',
            name: 'informed',
            value: Object.keys(daInformed).join(',')
          }).appendTo($(form));
        }
        $('<input>').attr({
          type: 'hidden',
          name: 'ajax',
          value: '1'
        }).appendTo($(form));
        daSpinnerTimeout = setTimeout(showSpinner, 1000);
        var do_iframe_upload = false;
        if ($('input[name="_files"]').length){
          var filesToRead = 0;
          var filesRead = 0;
          var newFileList = Array();
          var fileArray = {keys: Array(), values: Object()};
          var file_list = JSON.parse(atob($('input[name="_files"]').val()));
          var inline_file_list = Array();
          for (var i = 0; i < file_list.length; i++){
            var file_input = $('#' + file_list[i].replace(/(:|\.|\[|\]|,|=|\/|\")/g, '\\\\$1'))[0];
            var max_size = $(file_input).data('maximagesize');
            var hasImages = false;
            if (typeof max_size != 'undefined'){
              for (var j = 0; j < file_input.files.length; j++){
                var the_file = file_input.files[j];
                if (the_file.type.match(/image.*/)){
                  hasImages = true;
                }
              }
            }
            if (hasImages){
              for (var j = 0; j < file_input.files.length; j++){
                var the_file = file_input.files[j];
                filesToRead++;
              }
              inline_file_list.push(file_list[i]);
            }
            else if (file_input.files.length > 0){
              newFileList.push(file_list[i]);
            }
          }
          if (inline_file_list.length > 0){
            if (newFileList.length == 0){
              $('input[name="_files"]').remove();
            }
            else{
              $('input[name="_files"]').val(btoa(JSON.stringify(newFileList)));
            }
            for (var i = 0; i < inline_file_list.length; i++){
              fileArray.keys.push(inline_file_list[i])
              fileArray.values[inline_file_list[i]] = Array()
              var fileInfoList = fileArray.values[inline_file_list[i]];
              var file_input = $('#' + inline_file_list[i].replace(/(:|\.|\[|\]|,|=|\/|\")/g, '\\\\$1'))[0];
              var max_size = parseInt($(file_input).data('maximagesize'));
              for (var j = 0; j < file_input.files.length; j++){
                var the_file = file_input.files[j];
                var tempFunc = function(the_file, max_size){
                  var reader = new FileReader();
                  var thisFileInfo = {name: the_file.name, size: the_file.size, type: the_file.type};
                  fileInfoList.push(thisFileInfo);
                  //console.log("need to check type property " + the_file.type + " for " + the_file.name);
                  reader.onload = function(readerEvent){
                    //console.log("checking type property " + the_file.type + " for " + the_file.name);
                    if (the_file.type.match(/image.*/) && !the_file.type.startsWith('image/svg')){
                      //console.log("this one is an image");
                      var image = new Image();
                      image.onload = function(imageEvent) {
                        var canvas = document.createElement('canvas'),
                          width = image.width,
                          height = image.height;
                        if (width > height) {
                          if (width > max_size) {
                              height *= max_size / width;
                              width = max_size;
                          }
                        }
                        else {
                          if (height > max_size) {
                            width *= max_size / height;
                            height = max_size;
                          }
                        }
                        canvas.width = width;
                        canvas.height = height;
                        canvas.getContext('2d').drawImage(image, 0, 0, width, height);
                        thisFileInfo['content'] = canvas.toDataURL(the_file.type);
                        filesRead++;
                        //console.log("file read");
                        if (filesRead >= filesToRead){
                          //console.log("this is the last one!");
                          resumeUploadSubmission(form, fileArray, inline_file_list, newFileList);
                        }
                      };
                      image.src = reader.result;
                    }
                    else{
                      //console.log("this one is not an image");
                      thisFileInfo['content'] = reader.result;
                      filesRead++;
                      if (filesRead >= filesToRead){
                        //console.log("this is the last one!");
                        resumeUploadSubmission(form, fileArray, inline_file_list, newFileList);
                      }
                    }
                    //console.log("done checking type property");
                  };
                  reader.readAsDataURL(the_file);
                };
                tempFunc(the_file, max_size);
              }
            }
            return;
          }
          if (newFileList.length == 0){
            $('input[name="_files"]').remove();
          }
          else{
            do_iframe_upload = true;            
          }
        }
        if (do_iframe_upload){
          $("#uploadiframe").remove();
          var iframe = $('<iframe name="uploadiframe" id="uploadiframe" style="display: none"></iframe>');
          $("#dabody").append(iframe);
          $(form).attr("target", "uploadiframe");
          iframe.bind('load', function(){
            setTimeout(function(){
              try {
                daProcessAjax($.parseJSON(unfake_html_response($("#uploadiframe").contents().text())), form, 1);
              }
              catch (e){
                daShowErrorScreen(document.getElementById('uploadiframe').contentWindow.document.body.innerHTML);
              }
            }, 0);
          });
          form.submit();
        }
        else{
          $.ajax({
            type: "POST",
            url: $(form).attr('action'),
            data: $(form).serialize(), 
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, form, 1);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
        }
        return(false);
      }
      function resumeUploadSubmission(form, fileArray, inline_file_list, newFileList){
        $('<input>').attr({
          type: 'hidden',
          name: '_files_inline',
          value: btoa(JSON.stringify(fileArray))
        }).appendTo($(form));
        for (var i = 0; i < inline_file_list.length; ++i){
          document.getElementById(inline_file_list[i]).disabled = true;
        }
        if (newFileList.length > 0){
          $("#uploadiframe").remove();
          var iframe = $('<iframe name="uploadiframe" id="uploadiframe" style="display: none"></iframe>');
          $("#dabody").append(iframe);
          $(form).attr("target", "uploadiframe");
          iframe.bind('load', function(){
            setTimeout(function(){
              daProcessAjax($.parseJSON($("#uploadiframe").contents().text()), form, 1);
            }, 0);
          });
          form.submit();
        }
        else{
          $.ajax({
            type: "POST",
            url: $(form).attr('action'),
            data: $(form).serialize(), 
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, form, 1);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
        }
      }
      function pushChanges(){
        //console.log("pushChanges");
        if (checkinSeconds == 0 || daShowIfInProcess){
          return;
        }
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
        daCheckin();
        checkinInterval = setInterval(daCheckin, checkinSeconds);
      }
      function daProcessAjaxError(xhr, status, error){
        $("#dabody").html(xhr.responseText);
      }
      function addScriptToHead(src){
        var head = document.getElementsByTagName("head")[0];
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = src;
        script.async = true;
        script.defer = true;
        head.appendChild(script);
      }
      $(document).on('keydown', function(e){
        if (e.which == 13 && daShowingHelp == 0 && $("#daform button").length == 1){
          var tag = $( document.activeElement ).prop("tagName");
          if (tag != "INPUT" && tag != "TEXTAREA"){
            e.preventDefault();
            e.stopPropagation();
            $("#daform button").click();
            return false;
          }
        }
      });
      function daShowErrorScreen(data){
        console.log('daShowErrorScreen');
        if ("activeElement" in document){
          document.activeElement.blur();
        }
        $("#dabody").html(data);
      }
      function daProcessAjax(data, form, doScroll){
        daInformedChanged = false;
        if (dadisable != null){
          clearTimeout(dadisable);
        }
        daCsrf = data.csrf_token;
        if (data.action == 'body'){""" + forceFullScreen + """
          if ("activeElement" in document){
            document.activeElement.blur();
          }
          $("#dabody").html(data.body);
          $("body").removeClass();
          $("body").addClass(data.bodyclass);
          $("meta[name=viewport]").attr('content', "width=device-width, initial-scale=1");
          daDoAction = data.do_action;
          //daNextAction = data.next_action;
          daChatAvailable = data.livehelp.availability;
          daChatMode = data.livehelp.mode;
          daChatRoles = data.livehelp.roles;
          daChatPartnerRoles = data.livehelp.partner_roles;
          daSteps = data.steps;
          daAllowGoingBack = data.allow_going_back;
          daQuestionID = data.id;
          daMessageLog = data.message_log;
          //console.log("daProcessAjax: pushing " + daSteps);
          history.pushState({steps: daSteps}, data.browser_title + " - page " + daSteps, "#page" + daSteps);
          daInitialize(doScroll);
          var tempDiv = document.createElement('div');
          tempDiv.innerHTML = data.extra_scripts;
          var scripts = tempDiv.getElementsByTagName('script');
          for (var i = 0; i < scripts.length; i++){
            //console.log("Found one script");
            if (scripts[i].src != ""){
              //console.log("Added script to head");
              addScriptToHead(scripts[i].src);
            }
            else{
              eval(scripts[i].innerHTML);
            }
          }
          for (var i = 0; i < data.extra_css.length; i++){
            $("head").append(data.extra_css[i]);
          }
          document.title = data.browser_title;
          if ($("html").attr("lang") != data.lang){
            $("html").attr("lang", data.lang);
          }
          if (daReloader != null){
            clearTimeout(daReloader);
          }
          if (data.reload_after != null && data.reload_after > 0){
            //daReloader = setTimeout(function(){location.reload();}, data.reload_after);
            daReloader = setTimeout(function(){daRefreshSubmit();}, data.reload_after);
          }
          daUpdateHeight();
        }
        else if (data.action == 'redirect'){
          window.location = data.url;
        }
        else if (data.action == 'refresh'){
          daRefreshSubmit();
        }
        else if (data.action == 'resubmit'){
          $("input[name='ajax']").remove();
          if (daSubmitter != null){
            var input = $("<input>")
              .attr("type", "hidden")
              .attr("name", daSubmitter.name).val(daSubmitter.value);
            $(form).append($(input));
          }
          form.submit();
        }
      }
      function daEmbeddedJs(e){
        //console.log("using embedded js");
        var data = decodeURIComponent($(this).data('js'));
        eval(data);
        e.preventDefault();
        return false;
      }
      function daEmbeddedAction(e){
        var data = decodeURIComponent($(this).data('embaction'));
        $.ajax({
          type: "POST",
          url: """ + '"' + url_for('index') + '"' + """,
          data: $.param({_action: data, csrf_token: daCsrf, ajax: 1}),
          success: function(data){
            setTimeout(function(){
              daProcessAjax(data, $("#daform"), 1);
            }, 0);
          },
          error: function(xhr, status, error){
            setTimeout(function(){
              daProcessAjaxError(xhr, status, error);
            }, 0);
          },
          dataType: 'json'
        });
        e.preventDefault();
        return false;
      }
      function daReviewAction(e){
        //url_action_perform_with_next($(this).data('action'), null, daNextAction);
        var info = $.parseJSON(atob($(this).data('action')));
        url_action_perform(info['action'], info['arguments']);
        e.preventDefault();
        return false;
      }
      function daRingChat(){
        daChatStatus = 'ringing';
        pushChanges();
      }
      function daTurnOnChat(){
        //console.log("Publishing from daTurnOnChat");
        $("#daChatOnButton").addClass("invisible");
        $("#daChatBox").removeClass("invisible");
        $("#daCorrespondence").html('');
        for(var i = 0; i < chatHistory.length; i++){
          publishMessage(chatHistory[i]);
        }
        scrollChatFast();
        $("#daMessage").prop('disabled', false);
        if (daShowingHelp){
          $("#daMessage").focus();
        }
      }
      function daCloseChat(){
        //console.log('daCloseChat');
        daChatStatus = 'hangup';
        pushChanges();
        if (socket != null && socket.connected){
          socket.disconnect();
        }
      }
      // function daTurnOffChat(){
      //   $("#daChatOnButton").removeClass("invisible");
      //   $("#daChatBox").addClass("invisible");
      //   //daCloseSocket();
      //   $("#daMessage").prop('disabled', true);
      //   $("#daSend").unbind();
      //   //daStartCheckingIn();
      // }
      function display_chat(){
        if (daChatStatus == 'off' || daChatStatus == 'observeonly'){
          $("#daChatBox").addClass("invisible");
          $("#daChatAvailable").addClass("invisible");
          $("#daChatOnButton").addClass("invisible");
        }
        else{
          if (daChatStatus == 'waiting'){
            if (daChatPartnersAvailable > 0){
              $("#daChatBox").removeClass("invisible");
            }
          }
          else {
            $("#daChatBox").removeClass("invisible");
          }
        }
        if (daChatStatus == 'waiting'){
          //console.log("I see waiting")
          if (chatHistory.length > 0){
            $("#daChatAvailable a i").removeClass("chat-active");
            $("#daChatAvailable a i").addClass("chat-inactive");
            $("#daChatAvailable").removeClass("invisible");
          }
          else{
            $("#daChatAvailable a i").removeClass("chat-active");
            $("#daChatAvailable a i").removeClass("chat-inactive");
            $("#daChatAvailable").addClass("invisible");
          }
          $("#daChatOnButton").addClass("invisible");
          $("#daChatOffButton").addClass("invisible");
          $("#daMessage").prop('disabled', true);
          $("#daSend").prop('disabled', true);
        }
        if (daChatStatus == 'standby' || daChatStatus == 'ready'){
          //console.log("I see standby")
          $("#daChatAvailable").removeClass("invisible");
          $("#daChatAvailable a i").removeClass("chat-inactive");
          $("#daChatAvailable a i").addClass("chat-active");
          $("#daChatOnButton").removeClass("invisible");
          $("#daChatOffButton").addClass("invisible");
          $("#daMessage").prop('disabled', true);
          $("#daSend").prop('disabled', true);
          inform_about('chat');
        }
        if (daChatStatus == 'on'){
          $("#daChatAvailable").removeClass("invisible");
          $("#daChatAvailable a i").removeClass("chat-inactive");
          $("#daChatAvailable a i").addClass("chat-active");
          $("#daChatOnButton").addClass("invisible");
          $("#daChatOffButton").removeClass("invisible");
          $("#daMessage").prop('disabled', false);
          if (daShowingHelp){
            $("#daMessage").focus();
          }
          $("#daSend").prop('disabled', false);
          inform_about('chat');
        }
      }
      function daChatLogCallback(data){
        //console.log("daChatLogCallback: success is " + data.success);
        if (data.success){
          $("#daCorrespondence").html('');
          chatHistory = []; 
          var messages = data.messages;
          for (var i = 0; i < messages.length; ++i){
            chatHistory.push(messages[i]);
            publishMessage(messages[i]);
          }
          display_chat();
          scrollChatFast();
        }
      }
      function daRefreshSubmit(){
        $.ajax({
          type: "POST",
          url: $('#daform').attr('action'),
          data: 'csrf_token=' + daCsrf + '&ajax=1',
          success: function(data){
            setTimeout(function(){
              daProcessAjax(data, $("#daform"), 0);
            }, 0);
          },
          error: function(xhr, status, error){
            setTimeout(function(){
              daProcessAjaxError(xhr, status, error);
            }, 0);
          }
        });
      }
      function daResetCheckinCode(){
        daCheckinCode = Math.random();
      }
      function daCheckinCallback(data){
        daCheckingIn = 0;
        //console.log("daCheckinCallback: success is " + data.success);
        if (data.checkin_code != daCheckinCode){
          console.log("Ignoring checkincallback because code is wrong");
          return;
        }
        if (data.success){
          if (data.commands.length > 0){
            for (var i = 0; i < data.commands.length; ++i){
              var command = data.commands[i];
              if (command.extra == 'flash'){
                if (!$("#flash").length){
                  $("#dabody").append('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash"></div>');
                }
                $("#flash").append('<div class="alert alert-info alert-interlocutory"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + command.value + '</div>');
                //console.log("command is " + command.value);
              }
              else if (command.extra == 'refresh'){
                daRefreshSubmit();
              }
              else if (command.extra == 'javascript'){
                //console.log("I should eval" + command.value);
                eval(command.value);
              }
              else if (command.extra == 'fields'){
                for (var key in command.value){
                  if (command.value.hasOwnProperty(key)){
                    setField(key, command.value[key]);
                  }
                }
              }
              else if (command.extra == 'backgroundresponse'){
                var assignments = Array();
                if (command.value.hasOwnProperty('target') && command.value.hasOwnProperty('content')){
                  assignments.push({target: command.value.target, content: command.value.content});
                }
                if (Array.isArray(command.value)){
                  for (i = 0; i < command.value.length; ++i){
                    var possible_assignment = command.value[i];
                    if (possible_assignment.hasOwnProperty('target') && possible_assignment.hasOwnProperty('content')){
                      assignments.push({target: possible_assignment.target, content: possible_assignment.content});
                    }
                  }
                }
                for (i = 0; i < assignments.length; ++i){
                  var assignment = assignments[i];
                  $('#datarget' + assignment.target.replace(/[^A-Za-z0-9\_]/g)).html(assignment.content);
                }
                //console.log("Triggering daCheckIn");
                $(document).trigger('daCheckIn', [command.action, command.value]);
              }
            }
            // setTimeout(function(){
            //   $("#flash .alert-interlocutory").hide(300, function(){
            //     $(self).remove();
            //   });
            // }, 5000);
          }
          oldDaChatStatus = daChatStatus;
          //console.log("daCheckinCallback: from " + daChatStatus + " to " + data.chat_status);
          if (data.phone == null){
            $("#daPhoneMessage").addClass("invisible");
            $("#daPhoneMessage p").html('');
            $("#daPhoneAvailable").addClass("invisible");
            daPhoneAvailable = false;
          }
          else{
            $("#daPhoneMessage").removeClass("invisible");
            $("#daPhoneMessage p").html(data.phone);
            $("#daPhoneAvailable").removeClass("invisible");
            daPhoneAvailable = true;
            inform_about('phone');
          }
          var statusChanged;
          if (daChatStatus == data.chat_status){
            statusChanged = false;
          }
          else{
            statusChanged = true;
          }
          if (statusChanged){
            daChatStatus = data.chat_status;
            display_chat();
            if (daChatStatus == 'ready'){
              //console.log("calling initialize socket because ready");
              daInitializeSocket();
            }
          }
          daChatPartnersAvailable = 0;
          if (daChatMode == 'peer' || daChatMode == 'peerhelp'){
            daChatPartnersAvailable += data.num_peers;
            if (data.num_peers == 1){
              $("#peerMessage").html('<span class="btn btn-info">' + data.num_peers + ' ' + """ + json.dumps(word("other user")) + """ + '</span>');
            }
            else{
              $("#peerMessage").html('<span class="btn btn-info">' + data.num_peers + ' ' + """ + json.dumps(word("other users")) + """ + '</span>');
            }
            $("#peerMessage").removeClass("invisible");
          }
          else{
            $("#peerMessage").addClass("invisible");
          }
          if (daChatMode == 'peerhelp' || daChatMode == 'help'){
            if (data.help_available == 1){
              $("#peerHelpMessage").html('<span class="badge badge-primary">' + data.help_available + ' ' + """ + json.dumps(word("operator")) + """ + '</span>');
            }
            else{
              $("#peerHelpMessage").html('<span class="badge badge-primary">' + data.help_available + ' ' + """ + json.dumps(word("operators")) + """ + '</span>');
            }
            $("#peerHelpMessage").removeClass("invisible");
          }
          else{
            $("#peerHelpMessage").addClass("invisible");
          }
          if (daBeingControlled){
            if (!data.observerControl){
              daBeingControlled = false;
              //console.log("Hiding control 1");
              hide_control();
              if (daChatStatus != 'on'){
                if (socket != null && socket.connected){
                  //console.log('Terminating interview socket because control is over');
                  socket.emit('terminate');
                }
              }
            }
          }
          else{
            if (data.observerControl){
              daBeingControlled = true;
              daInitializeSocket();
            }
          }
        }
      }
      function daCheckoutCallback(data){
      }
      function daCheckin(){
        //console.log("daCheckin");
        daCheckingIn += 1;
        if (daCheckingIn > 1 && !(daCheckingIn % 3)){
          //console.log("daCheckin: request already pending, not re-sending");
          return;
        }
        var datastring;
        if ((daChatStatus != 'off') && $("#daform").length > 0 && !daBeingControlled){ // daChatStatus == 'waiting' || daChatStatus == 'standby' || daChatStatus == 'ringing' || daChatStatus == 'ready' || daChatStatus == 'on' || daChatStatus == 'observeonly'
          if (daDoAction != null){
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode, parameters: formAsJSON(), raw_parameters: JSON.stringify($("#daform").serializeArray()), do_action: daDoAction});
          }
          else{
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode, parameters: formAsJSON(), raw_parameters: JSON.stringify($("#daform").serializeArray())});
          }
        }
        else{
          if (daDoAction != null){
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode, do_action: daDoAction, parameters: formAsJSON()});
          }
          else{
            datastring = $.param({action: 'checkin', chatstatus: daChatStatus, chatmode: daChatMode, csrf_token: daCsrf, checkinCode: daCheckinCode});
          }
        }
        //console.log("Doing checkin with " + daChatStatus);
        $.ajax({
          type: 'POST',
          url: """ + "'" + url_for('checkin') + "'" + """,
          data: datastring,
          success: daCheckinCallback,
          dataType: 'json'
        });
        return true;
      }
      function daCheckout(){
        $.ajax({
          type: 'POST',
          url: """ + "'" + url_for('checkout') + "'" + """,
          data: 'csrf_token=' + daCsrf + '&action=checkout',
          success: daCheckoutCallback,
          dataType: 'json'
        });
        return true;
      }
      function daStopCheckingIn(){
        daCheckout();
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
      }
      function showSpinner(){
        if ($("#question").length > 0){
          $('<div id="daSpinner" class="spinner-container top-for-navbar"><div class="container"><div class="row"><div class="col-centered"><span class="da-spinner text-muted"><i class="fas fa-spinner fa-spin"></i></span></div></div></div></div>').appendTo("#dabody");
        }
        else{
          var newSpan = document.createElement('span');
          var newI = document.createElement('i');
          $(newI).addClass("fas fa-spinner fa-spin");
          $(newI).appendTo(newSpan);
          $(newSpan).attr("id", "daSpinner");
          $(newSpan).addClass("da-sig-spinner text-muted top-for-navbar");
          $(newSpan).appendTo("#sigtoppart");
        }
        daShowingSpinner = true;
      }
      function hideSpinner(){
        $("#daSpinner").remove();
        daShowingSpinner = false;
        daSpinnerTimeout = null;
      }
      function adjustInputWidth(e){
        var contents = $(this).val();
        contents = contents.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/ /g, '&nbsp;');
        $('<span class="input-embedded" id="dawidth">').html( contents ).appendTo('#question');
        $("#dawidth").css('min-width', $(this).css('min-width'));
        $("#dawidth").css('background-color', $("#dabody").css('background-color'));
        $("#dawidth").css('color', $("#dabody").css('background-color'));
        $(this).width($('#dawidth').width() + 16);
        setTimeout(function(){
          $("#dawidth").remove();
        }, 0);
      }
      function showNotifications(){
        var n = daMessageLog.length;
        for (var i = 0; i < n; i++){
          var message = daMessageLog[i];
          if (message.priority == 'console'){
            console.log(message.message);
          }
          else if (message.priority == 'success' || message.priority == 'warning' || message.priority == 'danger' || message.priority == 'secondary' || message.priority == 'info' || message.priority == 'secondary' || message.priority == 'dark' || message.priority == 'light' || message.priority == 'primary'){
            flash(message.message, message.priority);
          }
          else{
            flash(message.message, 'info');
          }
        }
      }
      function showIfCompare(theVal, showIfVal){
        if (typeof theVal == 'string' && theVal.match(/^-?\d+\.\d+$/)){
          theVal = parseFloat(theVal);
        }
        else if (typeof theVal == 'string' && theVal.match(/^-?\d+$/)){
          theVal = parseInt(theVal);
        }
        if (typeof showIfVal == 'string' && showIfVal.match(/^-?\d+\.\d+$/)){
          showIfVal = parseFloat(showIfVal);
        }
        else if (typeof showIfVal == 'string' && showIfVal.match(/^-?\d+$/)){
          showIfVal = parseInt(showIfVal);
        }
        if (typeof theVal == 'string' || typeof showIfVal == 'string'){
          return (String(theVal) == String(showIfVal));
        }
        return (theVal == showIfVal);
      }
      function daInitialize(doScroll){
        daResetCheckinCode();
        if (daSpinnerTimeout != null){
          clearTimeout(daSpinnerTimeout);
          daSpinnerTimeout = null;
        }
        if (daShowingSpinner){
          hideSpinner();
        }
        notYetScrolled = true;
        $(".helptrigger").click(function(e) {
          e.preventDefault();
          $(this).tab('show');
        });
        $('#questionlabel').click(function(e) {
          e.preventDefault();
          $(this).tab('show');
        });
        $('#pagetitle').click(function(e) {
          e.preventDefault();
          $('#questionlabel').tab('show');
        });
        if (navigator.userAgent.match(/(iPad|iPhone|iPod touch);/i)) {
          var selects = document.querySelectorAll("select");
          for (var i = 0; i < selects.length; i++){
            selects[i].appendChild(document.createElement("optgroup"));
          }
        }
        $(".to-labelauty").labelauty({ class: "labelauty fullwidth" });
        $(".to-labelauty-icon").labelauty({ label: false });
        $("button").on('click', function(){
          whichButton = this;
        });
        $('#source').on('hide.bs.collapse', function (e) {
          $("#readability").slideUp();
        });
        $('#source').on('show.bs.collapse', function (e) {
          if (daShowingHelp){
            $("#readability-question").hide();
            $("#readability-help").show();
          }
          else{
            $("#readability-help").hide();
            $("#readability-question").show();
          }
          $("#readability").slideDown();
        });
        $('a[data-target="#help"], a[data-target="#question"]').on('shown.bs.tab', function (e) {
          if ($(this).data("target") == '#help'){
            daShowingHelp = 1;
            if (notYetScrolled){
              scrollChatFast();
              notYetScrolled = false;
            }""" + debug_readability_help + """
          }
          else if ($(this).data("target") == '#question'){
            daShowingHelp = 0;""" + debug_readability_question + """
          }
        });
        $("input.nota-checkbox").click(function(){
          $(this).parent().find('input.non-nota-checkbox').each(function(){
            var existing_val = $(this).prop('checked');
            $(this).prop('checked', false);
            if (existing_val != false){
              $(this).trigger('change');
            }
          });
        });
        $("input.non-nota-checkbox").click(function(){
          $(this).parent().find('input.nota-checkbox').each(function(){
            var existing_val = $(this).prop('checked');
            $(this).prop('checked', false);
            if (existing_val != false){
              $(this).trigger('change');
            }
          });
        });
        $("input.dafile").fileinput();
        $('.combobox').combobox();
        $("#emailform").validate({'submitHandler': daValidationHandler, 'rules': {'_attachment_email_address': {'minlength': 1, 'required': true, 'email': true}}, 'messages': {'_attachment_email_address': {'required': """ + json.dumps(word("An e-mail address is required.")) + """, 'email': """ + json.dumps(word("You need to enter a complete e-mail address.")) + """}}, 'errorClass': 'da-has-error'});
        $("a[data-embaction]").click(daEmbeddedAction);
        $("a[data-js]").click(daEmbeddedJs);
        $("a.review-action").click(daReviewAction);
        $("input.input-embedded").on('keyup', adjustInputWidth);
        $("input.input-embedded").each(adjustInputWidth);
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'focus', html: true})
        });
        $('[data-toggle="popover"]').on('click', function(event){
          event.preventDefault();
          event.stopPropagation();
          $(this).popover("show");
        });
        if (daPhoneAvailable){
          $("#daPhoneAvailable").removeClass("invisible");
        }
        $("#questionhelpbutton").on('click', function(event){
          event.preventDefault();
          $('#helptoggle').tab('show');
          return false;
        });
        $("#questionbackbutton").on('click', function(event){
          event.preventDefault();
          $("#backbutton").submit();
          return false;
        });
        $("#backbutton").on('submit', function(event){
          if (daShowingHelp){
            event.preventDefault();
            $('#questionlabel').tab('show');
            return false;
          }
          $("#backbutton").addClass("dabackiconpressed");
          var informed = '';
          if (daInformedChanged){
            informed = '&informed=' + Object.keys(daInformed).join(',');
          }
          $.ajax({
            type: "POST",
            url: $("#backbutton").attr('action'),
            data: $("#backbutton").serialize() + '&ajax=1' + informed, 
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, document.getElementById('backbutton'), 1);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
          daSpinnerTimeout = setTimeout(showSpinner, 1000);
          event.preventDefault();
        });
        $("#daChatOnButton").click(daRingChat);
        $("#daChatOffButton").click(daCloseChat);
        $('#daMessage').bind('keypress keydown keyup', function(e){
          if(e.keyCode == 13) { daSender(); e.preventDefault(); }
        });
        $('#daform button[type="submit"]').click(function(){
          daSubmitter = this;
          return true;
        });
        $('#daform input[type="submit"]').click(function(){
          daSubmitter = this;
          return true;
        });
        $('#emailform button[type="submit"]').click(function(){
          daSubmitter = this;
          return true;
        });
        $('#downloadform button[type="submit"]').click(function(){
          daSubmitter = this;
          return true;
        });
        $(".danavlinks a.clickable").click(function(e){
          var the_key = $(this).data('key');
          url_action_perform("_da_priority_action", {action: the_key});
          e.preventDefault();
          return false;
        });
        $(".danav-vertical .danavnested").each(function(){
          var box = this;
          var prev = $(this).prev();
          if (prev && !prev.hasClass('active')){
            var toggler = $('<span class="toggler">');
            if ($(box).hasClass('notshowing')){
              $('<i class="fas fa-caret-right">').appendTo(toggler);
            }
            else{
              $('<i class="fas fa-caret-down">').appendTo(toggler);
            }
            toggler.appendTo(prev);
            toggler.on('click', function(e){
              $(this).find("svg").each(function(){
                if ($(this).attr('data-icon') == 'caret-down'){
                  $(this).removeClass('fa-caret-down');
                  $(this).addClass('fa-caret-right');
                  $(this).attr('data-icon', 'caret-right');
                  $(box).hide();
                  $(box).toggleClass('notshowing');
                }
                else if ($(this).attr('data-icon') == 'caret-right'){
                  $(this).removeClass('fa-caret-right');
                  $(this).addClass('fa-caret-down');
                  $(this).attr('data-icon', 'caret-down');
                  $(box).show();
                  $(box).toggleClass('notshowing');
                }
              });
              e.stopPropagation();
              e.preventDefault();
              return false;
            });
          }
        });
        $("body").focus();
        var firstInput = $("#daform input, #daform textarea, #daform select").first();
        if (firstInput.length > 0){
          $(firstInput).focus();
          var inputType = $(firstInput).attr('type');
          if ($(firstInput).prop('tagName') != 'SELECT' && inputType != "checkbox" && inputType != "radio" && inputType != "hidden" && inputType != "submit" && inputType != "file" && inputType != "range" && inputType != "number" && inputType != "date" && inputType != "time"){
            var strLength = $(firstInput).val().length * 2;
            if (strLength > 0){
              try {
                $(firstInput)[0].setSelectionRange(strLength, strLength);
              }
              catch(err) {
                console.log(err.message);
              }
            }
          }
        }
        $(".uncheckothers").on('change', function(){
          if ($(this).is(":checked")){
            $(".uncheckable").prop("checked", false);
            $(".uncheckable").trigger('change');
          }
        });
        $(".uncheckable").on('change', function(){
          if ($(this).is(":checked")){
            $(".uncheckothers").prop("checked", false);
            $(".uncheckothers").trigger('change');
          }
        });
        var navMain = $("#navbar-collapse");
        navMain.on("click", "a", null, function () {
          if (!($(this).hasClass("dropdown-toggle"))){
            navMain.collapse('hide');
          }
        });
        $("a[data-target='#help']").on("shown.bs.tab", function(){
          window.scrollTo(0, 1);
          $("#helptoggle span").removeClass('daactivetext')
          $("#helptoggle").blur();
        });
        $("#sourcetoggle").on("click", function(){
          $(this).parent().toggleClass("active");
          $(this).blur();
        });
        $('#backToQuestion').click(function(event){
          event.preventDefault();
          $('#questionlabel').tab('show');
        });
        varlookup = Object();
        varlookuprev = Object();
        if ($("input[name='_varnames']").length){
          the_hash = $.parseJSON(atob($("input[name='_varnames']").val()));
          for (var key in the_hash){
            if (the_hash.hasOwnProperty(key)){
              varlookup[the_hash[key]] = key;
              varlookuprev[key] = the_hash[key];
            }
          }
        }
        if ($("input[name='_checkboxes']").length){
          the_hash = $.parseJSON(atob($("input[name='_checkboxes']").val()));
          for (var key in the_hash){
            if (the_hash.hasOwnProperty(key)){
              var checkboxName = atob(key);
              var baseName = checkboxName;
              bracketPart = checkboxName.replace(/^.*(\[['"][^\]]*['"]\])$/, "$1");
              checkboxName = checkboxName.replace(/^.*\[['"]([^\]]*)['"]\]$/, "$1");
              if (checkboxName != baseName){
                baseName = baseName.replace(/^(.*)\[.*/, "$1");
                var transBaseName = baseName;
                if (($("[name='" + key + "']").length == 0) && (typeof varlookup[btoa(transBaseName)] != "undefined")){
                   transBaseName = atob(varlookup[btoa(transBaseName)]);
                }
                var convertedName;
                try {
                  convertedName = atob(checkboxName);
                }
                catch (e) {
                  continue;
                }
                varlookuprev[btoa(transBaseName + bracketPart)] = btoa(baseName + "['" + convertedName + "']");
                varlookup[btoa(baseName + "['" + convertedName + "']")] = btoa(transBaseName + bracketPart);
                varlookup[btoa(baseName + "[u'" + convertedName + "']")] = btoa(transBaseName + bracketPart);
                varlookup[btoa(baseName + '["' + convertedName + '"]')] = btoa(transBaseName + bracketPart);
              }
            }
          }
        }
        daShowIfInProcess = true;
        valLookup = Object();
        $(".jsshowif").each(function(){
          var showIfDiv = this;
          var jsInfo = JSON.parse(atob($(this).data('jsshowif')));
          var showIfSign = jsInfo['sign'];
          var jsExpression = jsInfo['expression'];
          var n = jsInfo['vars'].length;
          for (var i = 0; i < n; ++i){
            var showIfVar = btoa(jsInfo['vars'][i]);
            var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
            if ($("[name='" + showIfVarEscaped + "']").length == 0 && typeof varlookup[showIfVar] != "undefined"){
              showIfVar = varlookup[showIfVar];
              showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
            }
            var varList = $("[name='" + showIfVarEscaped + "']");
            if (varList.length == 0){
              varList = $("input[type='radio'][name='" + showIfVarEscaped + "']");
            }
            if (varList.length == 0){
              varList = $("input[type='checkbox'][name='" + showIfVarEscaped + "']");
            }
            if (varList.length > 0){
              valLookup[jsInfo['vars'][i]] = varList[0];
            }
            else{
              console.log("ERROR: could not set " + jsInfo['vars'][i]);
            }
            var showHideDiv = function(speed){
              var resultt = eval(jsExpression);
              if(resultt){
                if (showIfSign){
                  $(showIfDiv).show(speed);
                  $(showIfDiv).data('isVisible', '1');
                  $(showIfDiv).find('input, textarea, select').prop("disabled", false);
                }
                else{
                  $(showIfDiv).hide(speed);
                  $(showIfDiv).data('isVisible', '0');
                  $(showIfDiv).find('input, textarea, select').prop("disabled", true);
                }
              }
              else{
                if (showIfSign){
                  $(showIfDiv).hide(speed);
                  $(showIfDiv).data('isVisible', '0');
                  $(showIfDiv).find('input, textarea, select').prop("disabled", true);
                }
                else{
                  $(showIfDiv).show(speed);
                  $(showIfDiv).data('isVisible', '1');
                  $(showIfDiv).find('input, textarea, select').prop("disabled", false);
                }
              }
              var daThis = this;
              if (!daShowIfInProcess){
                daShowIfInProcess = true;
                $(":input").each(function(){
                  if (this != daThis){
                    $(this).trigger('change');
                  }
                });
                daShowIfInProcess = false;
              }
            };
            var showHideDivImmediate = function(){
              showHideDiv.apply(this, [null]);
            }
            var showHideDivFast = function(){
              showHideDiv.apply(this, ['fast']);
            }
            $("#" + showIfVarEscaped).each(showHideDivImmediate);
            $("#" + showIfVarEscaped).change(showHideDivFast);
            $("input[type='radio'][name='" + showIfVarEscaped + "']").each(showHideDivImmediate);
            $("input[type='radio'][name='" + showIfVarEscaped + "']").change(showHideDivFast);
            $("input[type='checkbox'][name='" + showIfVarEscaped + "']").each(showHideDivImmediate);
            $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(showHideDivFast);
          }
        });
        $(".showif").each(function(){
          var showIfSign = $(this).data('showif-sign');
          var showIfVar = $(this).data('showif-var');
          var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
          if ($("[name='" + showIfVarEscaped + "']").length == 0 && typeof varlookup[showIfVar] != "undefined"){
            //console.log("Set showIfVarEscaped " + showIfVar + " to alternate, " + varlookup[showIfVar]);
            showIfVar = varlookup[showIfVar];
            showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
          }
          //console.log("showIfVar is now " + showIfVar);
          var showIfVal = $(this).data('showif-val');
          var saveAs = $(this).data('saveas');
          //var isSame = (saveAs == showIfVar);
          var showIfDiv = this;
          //console.log("Processing saveAs " + atob(saveAs) + " with showIfVar " + atob(showIfVar));
          var showHideDiv = function(speed){
            //console.log("showHideDiv for saveAs " + atob(saveAs) + " with showIfVar " + showIfVar);
            var theVal;
            var showifParents = $(this).parents(".showif");
            if (showifParents.length !== 0 && !($(showifParents[0]).data("isVisible") == '1')){
              theVal = '';
              //console.log("Setting theVal to blank.");
            }
            else if ($(this).attr('type') == "checkbox"){
              theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
              if (typeof(theVal) == 'undefined'){
                //console.log('manually setting checkbox value to False');
                theVal = 'False';
              }
            }
            else if ($(this).attr('type') == "radio"){
              theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
              if (typeof(theVal) == 'undefined'){
                theVal = '';
              }
            }
            else{
              theVal = $(this).val();
            }
            //console.log("this is " + $(this).attr('id') + " and saveAs is " + atob(saveAs) + " and showIfVar is " + atob(showIfVar) + " and val is " + String(theVal) + " and showIfVal is " + String(showIfVal));
            if(showIfCompare(theVal, showIfVal)){
              //console.log("They are the same");
              if (showIfSign){
                //console.log("Showing1!");
                //$(showIfDiv).removeClass("invisible");
                $(showIfDiv).show(speed);
                $(showIfDiv).data('isVisible', '1');
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
              else{
                //console.log("Hiding1!");
                //$(showIfDiv).addClass("invisible");
                $(showIfDiv).hide(speed);
                $(showIfDiv).data('isVisible', '0');
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
            }
            else{
              //console.log("They are not the same");
              if (showIfSign){
                //console.log("Hiding2!");
                $(showIfDiv).hide(speed);
                $(showIfDiv).data('isVisible', '0');
                //$(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
              else{
                //console.log("Showing2!");
                $(showIfDiv).show(speed);
                $(showIfDiv).data('isVisible', '1');
                //$(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
            }
            var daThis = this;
            if (!daShowIfInProcess){
              daShowIfInProcess = true;
              $(":input").each(function(){
                if (this != daThis){
                  $(this).trigger('change');
                }
              });
              daShowIfInProcess = false;
            }
          };
          var showHideDivImmediate = function(){
            showHideDiv.apply(this, [null]);
          }
          var showHideDivFast = function(){
            showHideDiv.apply(this, ['fast']);
          }
          //console.log("showIfVarEscaped is #" + showIfVarEscaped);
          $("#" + showIfVarEscaped).each(showHideDivImmediate);
          $("#" + showIfVarEscaped).change(showHideDivFast);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").each(showHideDivImmediate);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").change(showHideDivFast);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").each(showHideDivImmediate);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(showHideDivFast);
        });
        $("a.danavlink").last().addClass('thelast');
        $("a.danavlink").each(function(){
          if ($(this).hasClass('btn') && !$(this).hasClass('notavailableyet')){
            var the_a = $(this);
            var the_delay = 1000 + 250 * parseInt($(this).data('index'));
            setTimeout(function(){
              $(the_a).removeClass('btn-secondary');
              if ($(the_a).hasClass('active')){
                $(the_a).addClass('btn-success');
              }
              else{
                $(the_a).addClass('btn-warning');
              }
            }, the_delay);
          }
        });
        daShowIfInProcess = false;
        $("#daSend").click(daSender);
        if (daChatAvailable == 'unavailable'){
          daChatStatus = 'off';
        }
        if (daChatAvailable == 'observeonly'){
          daChatStatus = 'observeonly';
        }
        if ((daChatStatus == 'off' || daChatStatus == 'observeonly') && daChatAvailable == 'available'){
          daChatStatus = 'waiting';
        }
        display_chat();
        if (daBeingControlled){
          show_control('fast');
        }
        if (daChatStatus == 'ready' || daBeingControlled){
          daInitializeSocket();
        }
        if (daInitialized == false && checkinSeconds > 0){ // why was this set to always retrieve the chat log?
          setTimeout(function(){
            //console.log("daInitialize call to chat_log in checkin");
            $.ajax({
              type: 'POST',
              url: """ + "'" + url_for('checkin') + "'" + """,
              data: $.param({action: 'chat_log', csrf_token: daCsrf}),
              success: daChatLogCallback,
              dataType: 'json'
            });
          }, 200);
        }
        if (daInitialized == true){
          //console.log("Publishing from memory");
          $("#daCorrespondence").html('');
          for(var i = 0; i < chatHistory.length; i++){
            publishMessage(chatHistory[i]);
          }
        }
        if (daChatStatus != 'off'){
          daSendChanges = true;
        }
        else{
          if (daDoAction == null){
            daSendChanges = false;
          }
          else{
            daSendChanges = true;
          }
        }
        if (daSendChanges){
          $("#daform").each(function(){
            $(this).find(':input').change(pushChanges);
          });
        }
        daInitialized = true;
        daShowingHelp = 0;
        daSubmitter = null;
        setTimeout(function(){
          $("#flash .alert-success").hide(300, function(){
            $(self).remove();
          });
        }, 3000);
        if (doScroll){
          setTimeout(function () {
            window.scrollTo(0, 1);
          }, 10);
        }
        if (daShowingSpinner){
          hideSpinner();
        }
        if (checkinInterval != null){
          clearInterval(checkinInterval);
        }
        if (checkinSeconds > 0){
          setTimeout(daCheckin, 100);
          checkinInterval = setInterval(daCheckin, checkinSeconds);
        }
        showNotifications();
        if (daUsingGA){
          daPageview();
        }
        $(document).trigger('daPageLoad');
      }
      $(document).ready(function(){
        daInitialize(1);
        //console.log("ready: replaceState " + daSteps);
        history.replaceState({steps: daSteps}, "", "#page" + daSteps);
        var daReloadAfter = """ + str(int(reload_after)) + """;
        if (daReloadAfter > 0){
          daReloader = setTimeout(function(){daRefreshSubmit();}, daReloadAfter);
        }
        window.onpopstate = function(event) {
          if (event.state != null && event.state.steps < daSteps && daAllowGoingBack){
            $("#backbutton").submit();
          }
        };
        $( window ).bind('unload', function() {
          daStopCheckingIn();
          if (socket != null && socket.connected){
            //console.log('Terminating interview socket because window unloaded');
            socket.emit('terminate');
          }
        });
      });
      $(window).ready(daUpdateHeight);
      $(window).resize(daUpdateHeight);
      function daUpdateHeight(){
        $(".googleMap").each(function(){
          var size = $( this ).width();
          $( this ).css('height', size);
        });
      }
      function daAddMap(map_num, center_lat, center_lon){
        var map = new google.maps.Map(document.getElementById("map" + map_num), {
          zoom: 11,
          center: new google.maps.LatLng(center_lat, center_lon),
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });
        var infowindow = new google.maps.InfoWindow();
        return({map: map, infowindow: infowindow});
      }
      function daAddMarker(map, marker_info, show_marker){
        var marker;
        if (marker_info.icon){
          if (marker_info.icon.path){
            marker_info.icon.path = google.maps.SymbolPath[marker_info.icon.path];
          }
        }
        else{
          marker_info.icon = null;
        }
        marker = new google.maps.Marker({
          position: new google.maps.LatLng(marker_info.latitude, marker_info.longitude),
          map: map.map,
          icon: marker_info.icon
        });
        if(marker_info.info){
          google.maps.event.addListener(marker, 'click', (function(marker, info) {
            return function() {
              map.infowindow.setContent(info);
              map.infowindow.open(map.map, marker);
            }
          })(marker, marker_info.info));
        }
        if(show_marker){
          map.infowindow.setContent(marker_info.info);
          map.infowindow.open(map.map, marker);
        }
        return marker;
      }
      function daInitMap(){
        maps = [];
        map_info_length = map_info.length;
        for (var i = 0; i < map_info_length; i++){
          the_map = map_info[i];
          var bounds = new google.maps.LatLngBounds();
          maps[i] = daAddMap(i, the_map.center.latitude, the_map.center.longitude);
          marker_length = the_map.markers.length;
          if (marker_length == 1){
            show_marker = true
          }
          else{
            show_marker = false
          }
          for (var j = 0; j < marker_length; j++){
            var new_marker = daAddMarker(maps[i], the_map.markers[j], show_marker);
            bounds.extend(new_marker.getPosition());
          }
          if (marker_length > 1){
            maps[i].map.fitBounds(bounds);
          }
        }
      }
      $.validator.setDefaults({
        highlight: function(element) {
            $(element).closest('.form-group').addClass('has-error');
        },
        unhighlight: function(element) {
            $(element).closest('.form-group').removeClass('has-error');
        },
        errorElement: 'span',
        errorClass: 'help-block',
        errorPlacement: function(error, element) {
            var elementName = $(element).attr("name");
            var lastInGroup = $.map(validation_rules['groups'], function(thefields, thename){
              var fieldsArr;
              if (thefields.indexOf(elementName) >= 0) {
                fieldsArr = thefields.split(" ");
                return fieldsArr[fieldsArr.length - 1];
              }
              else {
                return null;
              }
            })[0];
            if (element.hasClass('input-embedded')){
              error.insertAfter(element);
            }
            else if (element.hasClass('file-embedded')){
              error.insertAfter(element);
            }
            else if (element.hasClass('radio-embedded')){
              element.parent().append(error);
            }
            else if (element.hasClass('checkbox-embedded')){
              element.parent().append(error);
            }
            else if (element.hasClass('uncheckable') && lastInGroup){
              $("input[name='" + lastInGroup + "']").parent().append(error);
            }
            else if (element.parent().hasClass('combobox-container')){
              error.insertAfter(element.parent());
            }
            else if (element.hasClass('dafile')){
              var fileContainer = $(element).parents(".file-input").first();
              if (fileContainer.length > 0){
                $(fileContainer).append(error);
              }
              else{
                error.insertAfter(element.parent());
              }
            }
            else if (element.parent('.input-group').length) {
              error.insertAfter(element.parent());
            }
            else if (element.hasClass('labelauty')){
              var choice_with_help = $(element).parents(".choicewithhelp").first();
              if (choice_with_help.length > 0){
                $(choice_with_help).parent().append(error);
              }
              else{
                element.parent().append(error);
              }
            }
            else if (element.hasClass('non-nota-checkbox')){
              element.parent().append(error);
            }
            else {
              error.insertAfter(element);
            }
        }
      });
      $.validator.addMethod("datetime", function(a, b){
        return true;
      });
      $.validator.addMethod('checkone', function(value, element, params){
        var number_needed = params[0];
        var css_query = params[1];
        if ($(css_query).length >= number_needed){
          return true;
        }
        else{
          return false;
        }
      }, """ + json.dumps(word("Please check at least one.")) + """);
      $.validator.addMethod('checkatleast', function(value, element, params){
        if ($(element).attr('name') != '_ignore' + params[0]){
          return true;
        }
        if ($('.dafield' + params[0] + ':checked').length >= params[1]){
          return true;
        }
        else{
          return false;
        }
      }, function(params, element){
        if (params[1] == 1){
          return """ + json.dumps(word("Please select one.")) + """;
        }
        else{
          return """ + json.dumps(word("Please select at least")) + """ + " " + params[1] + ".";
        }
      });
      $.validator.addMethod('checkatmost', function(value, element, params){
        if ($(element).attr('name') != '_ignore' + params[0]){
          return true;
        }
        if ($('.dafield' + params[0] + ':checked').length > params[1]){
          return false;
        }
        else{
          return true;
        }
      }, function(params, element){
        return """ + json.dumps(word("Please select no more than")) + """ + " " + params[1] + ".";
      });
      $.validator.addMethod('checkexactly', function(value, element, params){
        if ($(element).attr('name') != '_ignore' + params[0]){
          return true;
        }
        if ($('.dafield' + params[0] + ':checked').length != params[1]){
          return false;
        }
        else{
          return true;
        }
      }, function(params, element){
        return """ + json.dumps(word("Please select exactly")) + """ + " " + params[1] + ".";
      });
      $.validator.addMethod('mindate', function(value, element, params){
        try {
          var date = new Date(value);
          var comparator = new Date(params);
          if (date >= comparator) {
            return true;
          }
        } catch (e) {}
        return false;
      }, """ + json.dumps(word("Please enter a valid date.")) + """);
      $.validator.addMethod('maxdate', function(value, element, params){
        try {
          var date = new Date(value);
          var comparator = new Date(params);
          if (date <= comparator) {
            return true;
          }
        } catch (e) {}
        return false;
      }, """ + json.dumps(word("Please enter a valid date.")) + """);
      $.validator.addMethod('minmaxdate', function(value, element, params){
        try {
          var date = new Date(value);
          var before_comparator = new Date(params[0]);
          var after_comparator = new Date(params[1]);
          if (date >= before_comparator && date <= after_comparator) {
            return true;
          }
        } catch (e) {}
        return false;
      }, """ + json.dumps(word("Please enter a valid date.")) + """);
    </script>"""
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    validation_rules = {'rules': {}, 'messages': {}, 'errorClass': 'da-has-error', 'debug': False}
    title_info = interview_status.question.interview.get_title(user_dict)
    interview_status.exit_link = title_info.get('exit link', 'exit')
    interview_status.exit_label = title_info.get('exit label', 'Exit')
    interview_status.title = title_info.get('full', default_title)
    interview_status.display_title = title_info.get('logo', interview_status.title)
    interview_status.tabtitle = title_info.get('tab', interview_status.title)
    interview_status.short_title = title_info.get('short', title_info.get('full', default_short_title))
    interview_status.display_short_title = title_info.get('logo', interview_status.short_title)
    the_main_page_parts = main_page_parts.get(interview_language, main_page_parts.get('*'))
    interview_status.pre = title_info.get('pre', the_main_page_parts['main page pre'])
    interview_status.post = title_info.get('post', the_main_page_parts['main page post'])
    interview_status.submit = title_info.get('submit', the_main_page_parts['main page submit'])
    bootstrap_theme = interview_status.question.interview.get_bootstrap_theme()
    if not is_ajax:
        standard_header_start = standard_html_start(interview_language=interview_language, debug=debug_mode, bootstrap_theme=bootstrap_theme)
    if interview_status.question.question_type == "signature":
        interview_status.extra_scripts.append('<script>$( document ).ready(function() {daInitializeSignature();});</script>')
        bodyclass="dasignature"
    else:
        bodyclass="dabody pad-for-navbar"
        # if not is_ajax:
        #     start_output = standard_header_start + '\n    <title>' + browser_title + '</title>\n  </head>\n  <body class="dasignature">\n'
        # output = make_navbar(interview_status, default_title, default_short_title, (steps - user_dict['_internal']['steps_offset']), SHOW_LOGIN, user_dict['_internal']['livehelp'], debug_mode)
        # output += signature_html(interview_status, debug_mode, url_for('index', i=yaml_filename), validation_rules)
        # if not is_ajax:
        #     end_output = scripts + "\n    " + "\n    ".join(interview_status.extra_scripts) + """\n  </body>\n</html>"""
    if debug_mode:
        interview_status.screen_reader_text = dict()
    if 'speak_text' in interview_status.extras and interview_status.extras['speak_text']:
        interview_status.initialize_screen_reader()
        util_language = docassemble.base.functions.get_language()
        util_dialect = docassemble.base.functions.get_dialect()
        question_language = interview_status.question.language
        if question_language != '*':
            the_language = question_language
        else:
            the_language = util_language
        if the_language == util_language and util_dialect is not None:
            the_dialect = util_dialect
        elif voicerss_config and 'languages' in voicerss_config and the_language in voicerss_config['languages']:
            the_dialect = voicerss_config['languages'][the_language]
        elif the_language in valid_voicerss_languages:
            the_dialect = valid_voicerss_languages[the_language][0]
        else:
            logmessage("index: unable to determine dialect; reverting to default")
            the_language = DEFAULT_LANGUAGE
            the_dialect = DEFAULT_DIALECT
        for question_type in ('question', 'help'):
            for audio_format in ('mp3', 'ogg'):
                interview_status.screen_reader_links[question_type].append([url_for('speak_file', question=interview_status.question.number, digest='XXXTHEXXX' + question_type + 'XXXHASHXXX', type=question_type, format=audio_format, language=the_language, dialect=the_dialect), audio_mimetype_table[audio_format]])
    if (not validated) and the_question.name == interview_status.question.name:
        for def_key, def_val in post_data.iteritems():
            if def_key in field_numbers:
                interview_status.defaults[field_numbers[def_key]] = def_val
        the_field_errors = field_error
    else:
        the_field_errors = None
    # restore this, maybe
    # if next_action_to_set:
    #     interview_status.next_action.append(next_action_to_set)
    if next_action_to_set:
        logmessage("Setting the next_action")
        if 'event_stack' not in user_dict['_internal']:
            user_dict['_internal']['event_stack'] = dict()
        session_uid = interview_status.current_info['user']['session_uid']
        if session_uid not in user_dict['_internal']['event_stack']:
            user_dict['_internal']['event_stack'][session_uid] = list()
        already_there = False
        for event_item in user_dict['_internal']['event_stack'][session_uid]:
            if event_item['action'] == next_action_to_set['action']:
                already_there = True
                break
        if not already_there:
            user_dict['_internal']['event_stack'][session_uid].insert(0, next_action_to_set)
    if interview_status.question.interview.use_progress_bar:
        the_progress_bar = progress_bar(user_dict['_internal']['progress'], interview_status.question.interview)
    else:
        the_progress_bar = None
    if interview_status.question.interview.use_navigation:
        if interview_status.question.interview.use_navigation == 'horizontal':
            the_nav_bar = navigation_bar(user_dict['nav'], interview_status.question.interview, wrapper=False, inner_div_class='nav flex-row justify-content-center align-items-center nav-pills danav danavlinks danav-horiz danavnested-horiz')
            if the_nav_bar != '':
                #offset-xl-3 offset-lg-3 col-xl-6 col-lg-6 offset-md-2 col-md-8 col-sm-12
                the_nav_bar = '        <div class="col d-none d-md-block">\n          <div class="nav flex-row justify-content-center align-items-center nav-pills danav danavlinks danav-horiz">\n            ' + the_nav_bar + '\n          </div>\n        </div>\n      </div>\n      <div class="row tab-content">\n'
        else:
            the_nav_bar = navigation_bar(user_dict['nav'], interview_status.question.interview)
        if the_nav_bar != '':
            if interview_status.question.interview.use_navigation == 'horizontal':
                interview_status.using_navigation = 'horizontal'
            else:
                interview_status.using_navigation = 'vertical'
        else:
            interview_status.using_navigation = False
    else:
        the_nav_bar = ''
        interview_status.using_navigation = False
    content = as_html(interview_status, url_for, debug_mode, url_for('index', i=yaml_filename), validation_rules, the_field_errors, the_progress_bar, steps - user_dict['_internal']['steps_offset'])
    if debug_mode:
        readability = dict()
        for question_type in ('question', 'help'):
            if question_type not in interview_status.screen_reader_text:
                continue
            phrase = to_text(interview_status.screen_reader_text[question_type]).encode('utf8')
            if (not phrase) or len(phrase) < 10:
                phrase = "The sky is blue."
            phrase = re.sub(r'[^A-Za-z 0-9\.\,\?\#\!\%\&\(\)]', r' ', phrase)
            readability[question_type] = [('Flesch Reading Ease', textstat.flesch_reading_ease(phrase)),
                                          ('Flesch-Kincaid Grade Level', textstat.flesch_kincaid_grade(phrase)),
                                          ('Gunning FOG Scale', textstat.gunning_fog(phrase)),
                                          ('SMOG Index', textstat.smog_index(phrase)),
                                          ('Automated Readability Index', textstat.automated_readability_index(phrase)),
                                          ('Coleman-Liau Index', textstat.coleman_liau_index(phrase)),
                                          ('Linsear Write Formula', textstat.linsear_write_formula(phrase)),
                                          ('Dale-Chall Readability Score', textstat.dale_chall_readability_score(phrase)),
                                          ('Readability Consensus', textstat.text_standard(phrase))]
        readability_report = ''
        for question_type in ('question', 'help'):
            if question_type in readability:
                readability_report += '          <table style="display: none;" class="table" id="readability-' + question_type +'">' + "\n"
                readability_report += '            <tr><th>Formula</th><th>Score</th></tr>' + "\n"
                for read_type, value in readability[question_type]:
                    readability_report += '            <tr><td>' + read_type +'</td><td>' + str(value) + "</td></tr>\n"
                readability_report += '          </table>' + "\n"
    if interview_status.using_screen_reader:
        for question_type in ('question', 'help'):
            #phrase = codecs.encode(to_text(interview_status.screen_reader_text[question_type]).encode('utf8'), 'base64').decode().replace('\n', '')
            if question_type not in interview_status.screen_reader_text:
                continue
            phrase = to_text(interview_status.screen_reader_text[question_type]).encode('utf8')
            #logmessage("Phrase is " + repr(phrase))
            if encrypted:
                the_phrase = encrypt_phrase(phrase, secret)
            else:
                the_phrase = pack_phrase(phrase)
            the_hash = MD5Hash(data=phrase).hexdigest()
            content = re.sub(r'XXXTHEXXX' + question_type + 'XXXHASHXXX', the_hash, content)
            existing_entry = SpeakList.query.filter_by(filename=yaml_filename, key=user_code, question=interview_status.question.number, digest=the_hash, type=question_type, language=the_language, dialect=the_dialect).first()
            if existing_entry:
                if existing_entry.encrypted:
                    existing_phrase = decrypt_phrase(existing_entry.phrase, secret)
                else:
                    existing_phrase = unpack_phrase(existing_entry.phrase)
                if phrase != existing_phrase:
                    logmessage("index: the phrase changed; updating it")
                    existing_entry.phrase = the_phrase
                    existing_entry.upload = None
                    existing_entry.encrypted = encrypted
                    db.session.commit()
            else:
                new_entry = SpeakList(filename=yaml_filename, key=user_code, phrase=the_phrase, question=interview_status.question.number, digest=the_hash, type=question_type, language=the_language, dialect=the_dialect, encrypted=encrypted)
                db.session.add(new_entry)
                db.session.commit()
    if not is_ajax:
        start_output = standard_header_start
        if 'css' in interview_status.question.interview.external_files:
            for packageref, fileref in interview_status.question.interview.external_files['css']:
                the_url = get_url_from_file_reference(fileref, _package=packageref)
                if the_url is not None:
                    start_output += "\n" + '    <link href="' + the_url + '" rel="stylesheet">'
                else:
                    logmessage("index: could not find css file " + str(fileref))
        start_output += global_css
        if len(interview_status.extra_css):
            start_output += '\n' + indent_by("".join(interview_status.extra_css).strip(), 4).rstrip()
        start_output += '\n    <title>' + interview_status.tabtitle + '</title>\n  </head>\n  <body class="' + bodyclass + '">\n  <div id="dabody">\n'
    output = make_navbar(interview_status, (steps - user_dict['_internal']['steps_offset']), interview_status.question.interview.consolidated_metadata.get('show login', SHOW_LOGIN), user_dict['_internal']['livehelp'], debug_mode) + flash_content + '    <div class="container">' + "\n      " + '<div class="row tab-content">' + "\n"
    if the_nav_bar != '':
        output += the_nav_bar
    output += content
    if 'rightText' in interview_status.extras:
        if interview_status.using_navigation == 'vertical':
            output += '          <section id="daright" class="d-none d-lg-block col-lg-3 col-xl-2 daright">\n'
        else:
            if interview_status.question.interview.flush_left:
                output += '          <section id="daright" class="d-none d-lg-block col-lg-6 col-xl-5 daright">\n'
            else:
                output += '          <section id="daright" class="d-none d-lg-block col-lg-3 col-xl-3 daright">\n'
        output += docassemble.base.util.markdown_to_html(interview_status.extras['rightText'], trim=False, status=interview_status) + "\n"
        output += '          </section>\n'
    #output += "        </div>\n      </div>\n"
    output += "      </div>\n"
    if len(interview_status.attributions):
        output += '      <div class="row">' + "\n"
        if interview_status.using_navigation == 'vertical':
            output += '        <div class="offset-xl-3 offset-lg-3 offset-md-3 col-lg-6 col-md-9 col-sm-12 daattributions" id="attributions">\n'
        else:
            if interview_status.question.interview.flush_left:
                output += '        <div class="offset-xl-1 col-xl-5 col-lg-6 col-md-8 col-sm-12 daattributions" id="attributions">\n'
            else:
                output += '        <div class="offset-xl-3 offset-lg-3 col-xl-6 col-lg-6 offset-md-2 col-md-8 col-sm-12 daattributions" id="attributions">\n'
        output += '        <br/><br/><br/><br/><br/><br/><br/>\n'
        for attribution in sorted(interview_status.attributions):
            output += '        <div><attribution><small>' + docassemble.base.util.markdown_to_html(attribution, status=interview_status, strip_newlines=True) + '</small></attribution></div>\n'
        output += '      </div>' + "\n"
    if debug_mode:
        output += '      <div class="row">' + "\n"
        if interview_status.using_navigation == 'vertical':
            output += '        <div class="offset-xl-3 offset-lg-3 offset-md-3 col-xl-6 col-lg-6 col-md-9 col-sm-12" style="display: none" id="readability">' + readability_report + '</div>'
        else:
            if interview_status.question.interview.flush_left:
                output += '        <div class="offset-xl-1 col-xl-5 col-lg-6 col-md-8 col-sm-12" style="display: none" id="readability">' + readability_report + '</div>'
            else:
                output += '        <div class="offset-xl-3 offset-lg-3 col-xl-6 col-lg-6 offset-md-2 col-md-8 col-sm-12" style="display: none" id="readability">' + readability_report + '</div>'
        output += '      </div>' + "\n"
        output += '      <div class="row">' + "\n"
        output += '        <div id="source" class="col-md-12 collapse">' + "\n"
        #output += '          <h3>' + word('SMS version') + '</h3>' + "\n"
        #output += '            <pre style="white-space: pre-wrap;">' + sms_content + '</pre>\n'
        if interview_status.using_screen_reader:
            output += '          <h3>' + word('Plain text of sections') + '</h3>' + "\n"
            for question_type in ('question', 'help'):
                if question_type in interview_status.screen_reader_text:
                    output += '<pre style="white-space: pre-wrap;">' + to_text(interview_status.screen_reader_text[question_type]) + '</pre>\n'
        output += '          <h3>' + word('Source code for question') + '</h3>' + "\n"
        if interview_status.question.source_code is None:
            output += word('unavailable')
        else:
            output += highlight(interview_status.question.source_code, YamlLexer(), HtmlFormatter())
        # if len(interview_status.question.fields_used):
        #     output += "<p>Variables set: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.fields_used)]) + "</p>"
        # if len(interview_status.question.names_used):
        #     output += "<p>Variables in code: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.names_used)]) + "</p>"
        # if len(interview_status.question.mako_names):
        #     output += "<p>Variables in templates: " + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview_status.question.mako_names)]) + "</p>"
        if len(interview_status.seeking) > 1:
            output += '          <h4>' + word('How question came to be asked') + '</h4>' + "\n"
            # output += '<ul>\n'
            # for foo in user_dict['_internal']['answered']:
            #     output += "<li>" + str(foo) + "</li>"
            # output += '</ul>\n'
            output += get_history(interview, interview_status)
        #output += '          <h4>' + word('Names defined') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(user_dict)]) + '</p>' + "\n"
        #output += '          <h4>' + word('Question names') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview.questions_by_name.keys())]) + '</p>' + "\n"
        #if len(interview.questions_by_id):
        #    output += '          <h4>' + word('Question IDs') + '</h4>' + "\n        <p>" + ", ".join(['<code>' + obj + '</code>' for obj in sorted(interview.questions_by_id.keys())]) + '</p>' + "\n"
        output += '          <p><a target="_blank" href="' + url_for('get_variables') + '">' + word('Show variables and values') + '</a></p>' + "\n"
            # output += '          <h4>' + word('Variables as JSON') + '</h4>' + "\n        <pre>" + docassemble.base.functions.dict_as_json(user_dict) + '</pre>' + "\n"
        output += '        </div>' + "\n"
        output += '      </div>' + "\n"
    output += '    </div>'
    if not is_ajax:
        end_output = scripts + global_js + "\n" + indent_by("".join(interview_status.extra_scripts).strip(), 4).rstrip() + "\n  </div>\n  </body>\n</html>"
    #logmessage(output.encode('utf8'))
    #logmessage("Request time interim: " + str(g.request_time()))
    if 'uid' in session and 'i' in session:
        key = 'da:html:uid:' + str(session['uid']) + ':i:' + str(session['i']) + ':userid:' + str(the_user_id)
        #logmessage("Setting html key " + key)
        pipe = r.pipeline()
        pipe.set(key, json.dumps(dict(body=output, extra_scripts=interview_status.extra_scripts, global_css=global_css, extra_css=interview_status.extra_css, browser_title=interview_status.tabtitle, lang=interview_language, bodyclass=bodyclass, bootstrap_theme=bootstrap_theme)))
        pipe.expire(key, 60)
        pipe.execute()
        #sys.stderr.write("10\n")
        #logmessage("Done setting html key " + key)
        #if session.get('chatstatus', 'off') in ('waiting', 'standby', 'ringing', 'ready', 'on'):
        if user_dict['_internal']['livehelp']['availability'] != 'unavailable':
            inputkey = 'da:input:uid:' + str(session['uid']) + ':i:' + str(session['i']) + ':userid:' + str(the_user_id)
            r.publish(inputkey, json.dumps(dict(message='newpage', key=key)))
    if is_json:
        data = dict(browser_title=interview_status.tabtitle, lang=interview_language, csrf_token=generate_csrf(), steps=steps, allow_going_back=allow_going_back, message_log=docassemble.base.functions.get_message_log(), id=question_id)
        data.update(interview_status.as_data())
        #if next_action_review:
        #    data['next_action'] = next_action_review
        if reload_after and reload_after > 0:
            data['reload_after'] = reload_after
        if 'action' in data and data['action'] == 'redirect' and 'url' in data:
            response = redirect(data['url'])
        else:
            response = jsonify(**data)
    elif is_ajax:
        if interview_status.question.checkin is not None:
            do_action = interview_status.question.checkin
        else:
            do_action = None
        response = jsonify(action='body', body=output, extra_scripts=interview_status.extra_scripts, extra_css=interview_status.extra_css, browser_title=interview_status.tabtitle, lang=interview_language, bodyclass=bodyclass, reload_after=reload_after, livehelp=user_dict['_internal']['livehelp'], csrf_token=generate_csrf(), do_action=do_action, steps=steps, allow_going_back=allow_going_back, message_log=docassemble.base.functions.get_message_log(), id=question_id)
        #response = jsonify(action='body', body=output, extra_scripts=interview_status.extra_scripts, extra_css=interview_status.extra_css, browser_title=interview_status.tabtitle, lang=interview_language, bodyclass=bodyclass, reload_after=reload_after, livehelp=user_dict['_internal']['livehelp'], csrf_token=generate_csrf(), do_action=do_action, next_action=next_action_review, steps=steps, allow_going_back=allow_going_back, message_log=docassemble.base.functions.get_message_log(), id=question_id)
        if return_fake_html:
            response.set_data('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Response</title></head><body><pre>ABCDABOUNDARYSTARTABC' + response.get_data().encode('base64') + 'ABCDABOUNDARYENDABC</pre></body></html>')
            response.headers['Content-type'] = 'text/html; charset=utf-8'
    else:
        output = start_output + output + end_output
        response = make_response(output.encode('utf8'), '200 OK')
        response.headers['Content-type'] = 'text/html; charset=utf-8'
    if set_cookie:
        response.set_cookie('secret', secret)
    if expire_visitor_secret:
        response.set_cookie('visitor_secret', '', expires=0)
    release_lock(user_code, yaml_filename)
    #logmessage("Request time final: " + str(g.request_time()))
    #sys.stderr.write("11\n")
    return response

def fixunicode(data):
    return data.decode('utf-8','ignore').encode("utf-8")

def get_history(interview, interview_status):
    output = ''
    if hasattr(interview_status, 'question'):
        has_question = True
    else:
        has_question = False
    index = 0
    if len(interview_status.seeking):
        starttime = interview_status.seeking[0]['time']
        for stage in interview_status.seeking:
            index += 1
            if index < len(interview_status.seeking) and 'reason' in interview_status.seeking[index] and interview_status.seeking[index]['reason'] == 'asking' and interview_status.seeking[index]['question'] is stage['question']:
                continue
            the_time = " at %.5fs" % (stage['time'] - starttime)
            if 'question' in stage and 'reason' in stage and (has_question is False or stage['question'] is not interview_status.question):
                if stage['reason'] == 'initial':
                    output += "          <h5>Ran initial code" + the_time + "</h5>\n"
                elif stage['reason'] == 'mandatory question':
                    output += "          <h5>Tried to ask mandatory question" + the_time + "</h5>\n"
                elif stage['reason'] == 'mandatory code':
                    output += "          <h5>Tried to run mandatory code" + the_time + "</h5>\n"
                elif stage['reason'] == 'asking':
                    output += "          <h5>Tried to ask question" + the_time + "</h5>\n"
                elif stage['reason'] == 'considering':
                    output += "          <h5>Considered asking question" + the_time + "</h5>\n"
                if stage['question'].from_source.path != interview.source.path:
                    output += '          <p style="font-weight: bold;"><small>(' + word('from') + ' ' + stage['question'].from_source.path +")</small></p>\n"
                if stage['question'].source_code is None:
                    output += word('(embedded question, source code not available)')
                else:
                    output += highlight(stage['question'].source_code, YamlLexer(), HtmlFormatter())
            elif 'variable' in stage:
                output += "          <h5>Needed definition of <code>" + str(stage['variable']) + "</code>" + the_time + "</h5>\n"
            elif 'done' in stage:
                output += "          <h5>Completed processing" + the_time + "</h5>\n"
    return output

def is_mobile_or_tablet():
    ua_string = request.headers.get('User-Agent', None)
    if ua_string is not None:
        response = ua_parse(ua_string)
        if response.is_mobile or response.is_tablet:
            return True
    return False

def add_referer(user_dict):
    if request.referrer:
        user_dict['_internal']['referer'] = request.referrer
    else:
        user_dict['_internal']['referer'] = None

@app.template_filter('word')
def word_filter(text):
    return docassemble.base.functions.word(unicode(text))

def get_part(part, default=None):
    if default is None:
        default = unicode()
    if part not in page_parts:
        return default
    if 'language' in session:
        lang = session['language']
    else:
        lang = DEFAULT_LANGUAGE
    if lang in page_parts[part]:
        return page_parts[part][lang]
    if lang != DEFAULT_LANGUAGE and DEFAULT_LANGUAGE in page_parts[part]:
        return page_parts[part][DEFAULT_LANGUAGE]
    if '*' in page_parts[part]:
        return page_parts[part]['*']
    return default

@app.context_processor
def utility_processor():
    def user_designator(the_user):
        if the_user.email:
            return the_user.email
        else:
            return re.sub(r'.*\$', '', the_user.social_id)
    if 'language' in session:
        docassemble.base.functions.set_language(session['language'])
    else:
        docassemble.base.functions.set_language(DEFAULT_LANGUAGE)
    def in_debug():
        return DEBUG
    return dict(word=docassemble.base.functions.word, in_debug=in_debug, user_designator=user_designator, get_part=get_part)

@app.route('/speakfile', methods=['GET'])
def speak_file():
    audio_file = None
    filename = session.get('i', None)
    key = session.get('uid', None)
    encrypted = session.get('encrypted', False)
    question = request.args.get('question', None)
    question_type = request.args.get('type', None)
    file_format = request.args.get('format', None)
    the_language = request.args.get('language', None)
    the_dialect = request.args.get('dialect', None)
    the_hash = request.args.get('digest', None)
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if file_format not in ('mp3', 'ogg') or not (filename and key and question and question_type and file_format and the_language and the_dialect):
        logmessage("speak_file: could not serve speak file because invalid or missing data was provided: filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    entry = SpeakList.query.filter_by(filename=filename, key=key, question=question, digest=the_hash, type=question_type, language=the_language, dialect=the_dialect).first()
    if not entry:
        logmessage("speak_file: could not serve speak file because no entry could be found in speaklist for filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        abort(404)
    if not entry.upload:
        existing_entry = SpeakList.query.filter(and_(SpeakList.phrase == entry.phrase, SpeakList.language == entry.language, SpeakList.dialect == entry.dialect, SpeakList.upload != None, SpeakList.encrypted == entry.encrypted)).first()
        if existing_entry:
            logmessage("speak_file: found existing entry: " + str(existing_entry.id) + ".  Setting to " + str(existing_entry.upload))
            entry.upload = existing_entry.upload
            db.session.commit()
        else:
            if not VOICERSS_ENABLED:
                logmessage("speak_file: could not serve speak file because voicerss not enabled")
                abort(404)
            new_file_number = get_new_file_number(key, 'speak.mp3', yaml_file_name=filename)
            #phrase = codecs.decode(entry.phrase, 'base64')
            if entry.encrypted:
                phrase = decrypt_phrase(entry.phrase, secret)
            else:
                phrase = unpack_phrase(entry.phrase)
            url = voicerss_config.get('url', "https://api.voicerss.org/")
            #logmessage("Retrieving " + url)
            audio_file = SavedFile(new_file_number, extension='mp3', fix=True)
            audio_file.fetch_url_post(url, dict(f=voicerss_config.get('format', '16khz_16bit_stereo'), key=voicerss_config['key'], src=phrase, hl=str(entry.language) + '-' + str(entry.dialect)))
            if audio_file.size_in_bytes() > 100:
                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', audio_file.path + '.mp3']
                logmessage("speak_file: calling " + " ".join(call_array))
                result = call(call_array)
                if result != 0:
                    logmessage("speak_file: failed to convert downloaded mp3 (" + audio_file.path + '.mp3' + ") to ogg")
                    abort(404)
                entry.upload = new_file_number
                audio_file.finalize()
                db.session.commit()
            else:
                logmessage("speak_file: download from voicerss (" + url + ") failed")
                abort(404)
    if not entry.upload:
        logmessage("speak_file: upload file number was not set")
        abort(404)
    if not audio_file:
        audio_file = SavedFile(entry.upload, extension='mp3', fix=True)
    the_path = audio_file.path + '.' + file_format
    if not os.path.isfile(the_path):
        logmessage("speak_file: could not serve speak file because file (" + the_path + ") not found")
        abort(404)
    response = send_file(the_path, mimetype=audio_mimetype_table[file_format])
    return(response)

def interview_menu(absolute_urls=False, start_new=False):
    interview_info = list()
    for key, yaml_filename in sorted(daconfig['dispatch'].iteritems()):
        try:
            interview = docassemble.base.interview_cache.get_interview(yaml_filename)
            if interview.is_unlisted():
                continue
            if interview.source is None:
                package = None
            else:
                package = interview.source.get_package()
            titles = interview.get_title(dict(_internal=dict()))
            tags = interview.get_tags(dict(_internal=dict()))
            interview_title = titles.get('full', titles.get('short', word('Untitled')))
            subtitle = titles.get('sub', None)
            status_class = None
            subtitle_class = None
        except:
            interview_title = yaml_filename
            tags = set()
            package = None
            subtitle = None
            status_class = 'dainterviewhaserror'
            subtitle_class = 'invisible'
            logmessage("interview_dispatch: unable to load interview file " + yaml_filename)
        if absolute_urls:
            if start_new:
                url = url_for('index', i=yaml_filename, _external=True, reset='1')
            else:
                url = url_for('index', i=yaml_filename, _external=True)
        else:
            if start_new:
                url = url_for('index', i=yaml_filename, reset='1')
            else:
                url = url_for('index', i=yaml_filename)
        interview_info.append(dict(link=url, title=interview_title, status_class=status_class, subtitle=subtitle, subtitle_class=subtitle_class, filename=yaml_filename, package=package, tags=sorted(tags)))
    return interview_info

@app.route('/list', methods=['GET'])
def interview_start():
    delete_session_for_interview()
    if len(daconfig['dispatch']) == 0:
        return redirect(url_for('index', i=final_default_yaml_filename))
    if ('json' in request.form and int(request.form['json'])) or ('json' in request.args and int(request.args['json'])):
        is_json = True
    else:
        is_json = False
    if daconfig.get('dispatch interview', None) is not None:
        if is_json:
            return redirect(url_for('index', i=daconfig.get('dispatch interview'), from_list='1', json='1'))
        else:
            return redirect(url_for('index', i=daconfig.get('dispatch interview'), from_list='1'))
    if 'embedded' in request.args and int(request.args['embedded']):
        the_page = 'pages/start-embedded.html'
        embed = True
    else:
        embed = False
    interview_info = interview_menu(absolute_urls=embed)
    if is_json:
        return jsonify(action='menu', interviews=interview_info)
    argu = dict(version_warning=None, interview_info=interview_info) #extra_css=Markup(global_css), extra_js=Markup(global_js), tab_title=daconfig.get('start page title', word('Interviews')), title=daconfig.get('start page heading', word('Available interviews'))
    if embed:
        the_page = 'pages/start-embedded.html'
    else:
        if 'start page template' in daconfig and daconfig['start page template']:
            the_page = docassemble.base.functions.package_template_filename(daconfig['start page template'])
            if the_page is None:
                raise DAError("Could not find start page template " + daconfig['start page template'])
            with open(the_page, 'rU') as fp:
                template_string = fp.read().decode('utf8')
                return render_template_string(template_string, **argu)
        else:
            the_page = 'pages/start.html'
    resp = make_response(render_template(the_page, **argu))
    if embed:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/start/<dispatch>', methods=['GET'])
def redirect_to_interview(dispatch):
    #logmessage("redirect_to_interview: the dispatch is " + str(dispatch))
    yaml_filename = daconfig['dispatch'].get(dispatch, None)
    if yaml_filename is None:
        abort(404)
    arguments = dict()
    for arg in request.args:
        arguments[arg] = request.args[arg]
    arguments['i'] = yaml_filename
    return redirect(url_for('index', **arguments))

@app.route('/storedfile/<uid>/<number>/<filename>.<extension>', methods=['GET'])
def serve_stored_file(uid, number, filename, extension):
    number = re.sub(r'[^0-9]', '', str(number))
    if not can_access_file_number(number, uid=uid):
        abort(404)
    try:
        file_info = get_info_from_file_number(number, privileged=True)
    except:
        abort(404)
    if 'path' not in file_info:
        abort(404)
    else:
        response = send_file(file_info['path'], mimetype=file_info['mimetype'])
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)

@app.route('/tempfile/<code>/<filename>.<extension>', methods=['GET'])
def serve_temporary_file(code, filename, extension):
    file_info = r.get('da:tempfile:' + str(code))
    if file_info is None:
        logmessage("file_info was none")
        abort(404)
    (section, file_number) = file_info.split('^')
    the_file = SavedFile(file_number, fix=True, section=section)
    the_path = the_file.path
    (extension, mimetype) = get_ext_and_mimetype(filename + '.' + extension)
    return send_file(the_path, mimetype=mimetype)

@app.route('/uploadedfile/<number>/<filename>.<extension>', methods=['GET'])
def serve_uploaded_file_with_filename_and_extension(number, filename, extension):
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    number = re.sub(r'[^0-9]', '', str(number))
    if cloud is not None:
        if not can_access_file_number(number):
            abort(404)
        the_file = SavedFile(number)
    else:
        try:
            file_info = get_info_from_file_number(number, privileged=privileged)
        except:
            abort(404)
        if 'path' not in file_info:
            abort(404)
        else:
            #logmessage("Filename is " + file_info['path'] + '.' + extension)
            if os.path.isfile(file_info['path'] + '.' + extension):
                #logmessage("Using " + file_info['path'] + '.' + extension)
                extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
                response = send_file(file_info['path'] + '.' + extension, mimetype=mimetype)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return(response)
            elif os.path.isfile(os.path.join(os.path.dirname(file_info['path']), filename + '.' + extension)):
                #logmessage("Using " + os.path.join(os.path.dirname(file_info['path']), filename + '.' + extension))
                extension, mimetype = get_ext_and_mimetype(filename + '.' + extension)
                response = send_file(os.path.join(os.path.dirname(file_info['path']), filename + '.' + extension), mimetype=mimetype)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return(response)
            else:
                abort(404)

@app.route('/uploadedfile/<number>.<extension>', methods=['GET'])
def serve_uploaded_file_with_extension(number, extension):
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    number = re.sub(r'[^0-9]', '', str(number))
    if cloud is not None:
        if not can_access_file_number(number):
            abort(404)
        the_file = SavedFile(number)
    else:
        try:
            file_info = get_info_from_file_number(number, privileged=privileged)
        except:
            abort(404)
        if 'path' not in file_info:
            abort(404)
        else:
            if os.path.isfile(file_info['path'] + '.' + extension):
                extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
                response = send_file(file_info['path'] + '.' + extension, mimetype=mimetype)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return(response)
            else:
                abort(404)
    abort(404)

@app.route('/uploadedfile/<number>', methods=['GET'])
def serve_uploaded_file(number):
    number = re.sub(r'[^0-9]', '', str(number))
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    try:
        file_info = get_info_from_file_number(number, privileged=privileged)
    except:
        abort(404)
    #file_info = get_info_from_file_reference(number)
    if 'path' not in file_info:
        abort(404)
    else:
        #block_size = 4096
        #status = '200 OK'
        response = send_file(file_info['path'], mimetype=file_info['mimetype'])
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/uploadedpage/<number>/<page>', methods=['GET'])
def serve_uploaded_page(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    try:
        file_info = get_info_from_file_number(number, privileged=privileged)
    except:
        abort(404)
    if 'path' not in file_info:
        abort(404)
    else:
        max_pages = 1 + int(file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        filename = file_info['path'] + 'page-' + (formatter % int(page)) + '.png'
        if os.path.isfile(filename):
            response = send_file(filename, mimetype='image/png')
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return(response)
        else:
            abort(404)

@app.route('/uploadedpagescreen/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen(number, page):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
        privileged = True
    else:
        privileged = False
    try:
        file_info = get_info_from_file_number(number, privileged=privileged)
    except:
        abort(404)
    if 'path' not in file_info:
        logmessage('serve_uploaded_pagescreen: no access to file number ' + str(number))
        abort(404)
    else:
        try:
            the_file = DAFile(mimetype=file_info['mimetype'], extension=file_info['extension'], number=number, make_thumbnail=page)
            # max_pages = 1 + int(file_info['pages'])
            # formatter = '%0' + str(len(str(max_pages))) + 'd'
            # filename = file_info['path'] + 'screen-' + (formatter % int(page)) + '.png'
            filename = the_file.page_path(page, 'screen')
        except:
            filename = None
        if filename is None:
            the_file = docassemble.base.functions.package_data_filename('docassemble.base:data/static/blank_page.png')
            response = send_file(the_file, mimetype='image/png')
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return(response)
        if os.path.isfile(filename):
            response = send_file(filename, mimetype='image/png')
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return(response)
        else:
            logmessage('serve_uploaded_pagescreen: path ' + filename + ' is not a file')
            abort(404)

@app.route('/visit_interview', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'advocate'])
def visit_interview():
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    key = 'da:session:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    try:
        obj = pickle.loads(r.get(key))
    except:
        abort(404)
    if 'secret' not in obj or 'encrypted' not in obj:
        abort(404)
    session['i'] = i
    session['uid'] = uid
    session['encrypted'] = obj['encrypted']
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    session['key_logged'] = True
    if 'tempuser' in session:
        del session['tempuser']
    response = redirect(url_for('index', i=i))
    response.set_cookie('visitor_secret', obj['secret'])
    return response

@app.route('/observer', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'advocate'])
def observer():
    session['observer'] = 1
    i = request.args.get('i', None)
    uid = request.args.get('uid', None)
    userid = request.args.get('userid', None)
    observation_script = """
    <script>
      var whichButton = null;
      var daSendChanges = false;
      var daNoConnectionCount = 0;
      var daConnected = false;
      var daConfirmed = false;
      var observerChangesInterval = null;
      var daInitialized = false;
      var daShowingHelp = false;
      var daInformedChanged = false;
      var dadisable = null;
      var daCsrf = """ + json.dumps(generate_csrf()) + """;
      window.turnOnControl = function(){
        //console.log("Turning on control");
        daSendChanges = true;
        daNoConnectionCount = 0;
        resetPushChanges();
        socket.emit('observerStartControl', {uid: """ + json.dumps(uid) + """, i: """ + json.dumps(i) + """, userid: """ + json.dumps(str(userid)) + """});
      }
      window.turnOffControl = function(){
        //console.log("Turning off control");
        if (!daSendChanges){
          //console.log("Already turned off");
          return;
        }
        daSendChanges = false;
        daConfirmed = false;
        stopPushChanges();
        socket.emit('observerStopControl', {uid: """ + json.dumps(uid) + """, i: """ + json.dumps(i) + """, userid: """ + json.dumps(str(userid)) + """});
        return;
      }
      function daValidationHandler(form){
        //console.log("observer: daValidationHandler");
        return(false);
      }
      function stopPushChanges(){
        if (observerChangesInterval != null){
          clearInterval(observerChangesInterval);
        }
      }
      function resetPushChanges(){
        if (observerChangesInterval != null){
          clearInterval(observerChangesInterval);
        }
        observerChangesInterval = setInterval(pushChanges, """ + str(CHECKIN_INTERVAL) + """);
      }
      function pushChanges(){
        //console.log("Pushing changes");
        if (observerChangesInterval != null){
          clearInterval(observerChangesInterval);
        }
        if (!daSendChanges || !daConnected){
          return;
        }
        observerChangesInterval = setInterval(pushChanges, """ + str(CHECKIN_INTERVAL) + """);
        socket.emit('observerChanges', {uid: """ + json.dumps(uid) + """, i: """ + json.dumps(i) + """, userid: """ + json.dumps(str(userid)) + """, parameters: JSON.stringify($("#daform").serializeArray())});
      }
      function daProcessAjaxError(xhr, status, error){
        $("#dabody").html(xhr.responseText);
      }
      function addScriptToHead(src){
        var head = document.getElementsByTagName("head")[0];
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = src;
        script.async = true;
        script.defer = true;
        head.appendChild(script);
      }
      function daSubmitter(event){
        if (!daSendChanges || !daConnected){
          event.preventDefault();
          return false;
        }
        var theAction = null;
        if ($(this).hasClass('review-action')){
          theAction = $(this).data('action');
        }
        var embeddedJs = $(this).data('js');
        var embeddedAction = $(this).data('embaction');
        var linkNum = $(this).data('linknum');
        var theId = $(this).attr('id');
        if (theId == 'pagetitle'){
          theId = 'questionlabel';
        }
        var theName = $(this).attr('name');
        var theValue = $(this).val();
        var skey;
        if (linkNum){
          skey = 'a[data-linknum="' + linkNum + '"]';
        }
        else if (embeddedAction){
          skey = 'a[data-embaction="' + embeddedAction.replace(/(:|\.|\[|\]|,|=|\/|\")/g, '\\\\$1') + '"]';
        }
        else if (theAction){
          skey = 'a[data-action="' + theAction.replace(/(:|\.|\[|\]|,|=|\/|\")/g, '\\\\$1') + '"]';
        }
        else if (theId){
          skey = '#' + theId.replace(/(:|\.|\[|\]|,|=|\/|\")/g, '\\\\$1');
        }
        else if (theName){
          skey = '#' + $(this).parents("form").attr('id') + ' ' + $(this).prop('tagName').toLowerCase() + '[name="' + theName.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1') + '"]';
          if (typeof theValue !== 'undefined'){
            skey += '[value="' + theValue + '"]'
          }
        }
        else{
          skey = '#' + $(this).parents("form").attr('id') + ' ' + $(this).prop('tagName').toLowerCase() + '[type="submit"]';
        }
        //console.log("Need to click on " + skey);
        if (observerChangesInterval != null && embeddedJs == null && theId != "backToQuestion" && theId != "helptoggle" && theId != "questionlabel"){
          clearInterval(observerChangesInterval);
        }
        socket.emit('observerChanges', {uid: """ + json.dumps(uid) + """, i: """ + json.dumps(i) + """, userid: """ + json.dumps(str(userid)) + """, clicked: skey, parameters: JSON.stringify($("#daform").serializeArray())});
        if (embeddedJs != null){
          //console.log("Running the embedded js");
          eval(decodeURIComponent(embeddedJs));
        }
        if (theId != "backToQuestion" && theId != "helptoggle" && theId != "questionlabel"){
          event.preventDefault();
          return false;
        }
      }
      function adjustInputWidth(e){
        var contents = $(this).val();
        contents = contents.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/ /g, '&nbsp;');
        $('<span class="input-embedded" id="dawidth">').html( contents ).appendTo('#question');
        $("#dawidth").css('min-width', $(this).css('min-width'));
        $("#dawidth").css('background-color', $("#dabody").css('background-color'));
        $("#dawidth").css('color', $("#dabody").css('background-color'));
        $(this).width($('#dawidth').width() + 16);
        setTimeout(function(){
          $("#dawidth").remove();
        }, 0);
      }
      function show_help_tab(){
          $('#helptoggle').tab('show');
      }
      function flash(message, priority){
        if (priority == null){
          priority = 'info'
        }
        if (!$("#flash").length){
          $("#dabody").append('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash"></div>');
        }
        $("#flash").append('<div class="alert alert-' + priority + ' alert-interlocutory"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>');
        if (priority == 'success'){
          setTimeout(function(){
            $("#flash .alert-success").hide(300, function(){
              $(self).remove();
            });
          }, 3000);
        }
      }
      function url_action(action, args){
          //console.log("Got to a url_action");
          //redo
          if (args == null){
              args = {};
          }
          data = {action: action, arguments: args};
          return '?action=' + encodeURIComponent(btoa(JSON.stringify(data)));
      }
      function url_action_call(action, args, callback){
          //redo
          if (args == null){
              args = {};
          }
          if (callback == null){
              callback = function(){};
          }
          var data = {action: action, arguments: args};
          $.ajax({
            type: "GET",
            url: "?action=" + encodeURIComponent(btoa(JSON.stringify(data))),
            success: callback,
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
      }
      function url_action_perform(action, args){
          //redo
          if (args == null){
              args = {};
          }
          var data = {action: action, arguments: args};
          daSpinnerTimeout = setTimeout(showSpinner, 1000);
          $.ajax({
            type: "POST",
            url: """ + '"' + url_for('index') + '"' + """,
            data: $.param({_action: btoa(JSON.stringify(data)), csrf_token: daCsrf, ajax: 1}),
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, $("#daform"), 1);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            },
            dataType: 'json'
          });
      }
      function url_action_perform_with_next(action, args, next_data){
          //redo
          //console.log("url_action_perform_with_next: " + action + " | " + next_data)
          if (args == null){
              args = {};
          }
          var data = {action: action, arguments: args};
          daSpinnerTimeout = setTimeout(showSpinner, 1000);
          $.ajax({
            type: "POST",
            url: """ + '"' + url_for('index') + '"' + """,
            data: $.param({_action: btoa(JSON.stringify(data)), _next_action_to_set: btoa(JSON.stringify(next_data)), csrf_token: daCsrf, ajax: 1}),
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, $("#daform"), 1);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            },
            dataType: 'json'
          });
      }
      function get_interview_variables(callback){
        if (callback == null){
          callback = function(){};
        }
        $.ajax({
          type: "GET",
          url: """ + '"' + url_for('get_variables') + '"' + """,
          success: callback,
          error: function(xhr, status, error){
            setTimeout(function(){
              daProcessAjaxError(xhr, status, error);
            }, 0);
          }
        });
      }
      function daInitialize(doScroll){
        $('button[type="submit"], input[type="submit"], a.review-action, #backToQuestion, #questionlabel, #pagetitle, #helptoggle, a[data-linknum], a[data-embaction], #backbutton').click(daSubmitter);
        $(".to-labelauty").labelauty({ class: "labelauty fullwidth" });
        $(".to-labelauty-icon").labelauty({ label: false });
        var navMain = $("#navbar-collapse");
        navMain.on("click", "a", null, function () {
          if (!($(this).hasClass("dropdown-toggle"))){
            navMain.collapse('hide');
          }
        });
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'focus', html: true})
        });
        $("input.nota-checkbox").click(function(){
          $(this).parent().find('input.non-nota-checkbox').each(function(){
            if ($(this).prop('checked') != false){
              $(this).prop('checked', false);
              $(this).trigger('change');
            }
          });
        });
        $("input.non-nota-checkbox").click(function(){
          $(this).parent().find('input.nota-checkbox').each(function(){
            if ($(this).prop('checked') != false){
              $(this).prop('checked', false);
              $(this).trigger('change');
            }
          });
        });
        $("input.input-embedded").on('keyup', adjustInputWidth);
        $("input.input-embedded").each(adjustInputWidth);
        $(".helptrigger").click(function(e) {
          e.preventDefault();
          $(this).tab('show');
        });
        $("#questionlabel").click(function(e) {
          e.preventDefault();
          $(this).tab('show');
        });
        $("#pagetitle").click(function(e) {
          e.preventDefault();
          $('#questionlabel').tab('show');
        });        
        $("#help").on("shown.bs.tab", function(){
          window.scrollTo(0, 1);
          $("#helptoggle span").removeClass('daactivetext')
          $("#helptoggle").blur();
        });
        $("#sourcetoggle").on("click", function(){
          $(this).parent().toggleClass("active");
          $(this).blur();
        });
        $('#backToQuestion').click(function(event){
          event.preventDefault();
          $('#questionlabel').tab('show');
        });
        $(".showif").each(function(){
          var showIfSign = $(this).data('showif-sign');
          var showIfVar = $(this).data('showif-var');
          var showIfVarEscaped = showIfVar.replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
          var showIfVal = $(this).data('showif-val');
          var saveAs = $(this).data('saveas');
          //var isSame = (saveAs == showIfVar);
          var showIfDiv = this;
          var showHideDiv = function(speed){
            if($(this).parents(".showif").length !== 0){
              return;
            }
            var theVal;
            if ($(this).attr('type') == "checkbox" || $(this).attr('type') == "radio"){
              theVal = $("input[name='" + showIfVarEscaped + "']:checked").val();
            }
            else{
              theVal = $(this).val();
            }
            //console.log("val is " + theVal + " and showIfVal is " + showIfVal)
            if($(this).parent().is(":visible") && showIfCompare(theVal, showIfVal)){
              //console.log("They are the same");
              if (showIfSign){
                $(showIfDiv).show(speed);
                //$(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
              else{
                $(showIfDiv).hide(speed);
                //$(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
            }
            else{
              //console.log("They are not the same");
              if (showIfSign){
                $(showIfDiv).hide(speed);
                //$(showIfDiv).addClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", true);
              }
              else{
                $(showIfDiv).show(speed);
                //$(showIfDiv).removeClass("invisible");
                $(showIfDiv).find('input, textarea, select').prop("disabled", false);
              }
            }
            var daThis = this;
            if (!daShowIfInProcess){
              daShowIfInProcess = true;
              $(":input").each(function(){
                if (this != daThis){
                  $(this).trigger('change');
                }
              });
              daShowIfInProcess = false;
            }
          };
          var showHideDivImmediate = function(){
            showHideDiv.apply(this, [null]);
          }
          var showHideDivFast = function(){
            showHideDiv.apply(this, ['fast']);
          }
          $("#" + showIfVarEscaped).each(showHideDivImmediate);
          $("#" + showIfVarEscaped).change(showHideDivFast);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").each(showHideDivImmediate);
          $("input[type='radio'][name='" + showIfVarEscaped + "']").change(showHideDivFast);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").each(showHideDivImmediate);
          $("input[type='checkbox'][name='" + showIfVarEscaped + "']").change(showHideDivFast);
        });
        // dadisable = setTimeout(function(){
        //   $("#daform").find('button[type="submit"]').prop("disabled", true);
        //   //$("#daform").find(':input').prop("disabled", true);
        // }, 1);
        $("#daform").each(function(){
          $(this).find(':input').on('change', pushChanges);
        });
        daInitialized = true;
        daShowingHelp = 0;
        setTimeout(function(){
          $("#flash .alert-success").hide(300, function(){
            $(self).remove();
          });
        }, 3000);
        $(document).trigger('daPageLoad');
      }
      $( document ).ready(function(){
        daInitialize(1);
        $( window ).bind('unload', function() {
          if (socket != null && socket.connected){
            socket.emit('terminate');
          }
        });
        if (location.protocol === 'http:' || document.location.protocol === 'http:'){
            socket = io.connect("http://" + document.domain + "/observer" + location.port, {path: '/ws/socket.io'});
        }
        if (location.protocol === 'https:' || document.location.protocol === 'https:'){
            socket = io.connect("https://" + document.domain + "/observer" + location.port, {path: '/ws/socket.io'});
        }
        if (typeof socket !== 'undefined') {
            socket.on('connect', function() {
                //console.log("Connected!");
                socket.emit('observe', {uid: """ + json.dumps(uid) + """, i: """ + json.dumps(i) + """, userid: """ + json.dumps(str(userid)) + """});
                daConnected = true;
            });
            socket.on('terminate', function() {
                //console.log("Terminating socket");
                socket.disconnect();
            });
            socket.on('disconnect', function() {
                //console.log("Disconnected socket");
                //socket = null;
            });
            socket.on('stopcontrolling', function(data) {
                window.parent.stopControlling(data.key);
            });
            socket.on('start_being_controlled', function(data) {
                //console.log("Got start_being_controlled");
                daConfirmed = true;
                pushChanges();
                window.parent.gotConfirmation(data.key);
            });
            socket.on('abortcontrolling', function(data) {
                //console.log("Got abortcontrolling");
                //daSendChanges = false;
                //daConfirmed = false;
                //stopPushChanges();
                window.parent.abortControlling(data.key);
            });
            socket.on('noconnection', function(data) {
                //console.log("warning: no connection");
                if (daNoConnectionCount++ > 2){
                    //console.log("error: no connection");
                    window.parent.stopControlling(data.key);
                }
            });
            socket.on('newpage', function(incoming) {
                //console.log("Got newpage")
                var data = incoming.obj;
                $("#dabody").html(data.body);
                $("body").removeClass();
                $("body").addClass(data.bodyclass);
                daInitialize(1);
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.extra_scripts;
                var scripts = tempDiv.getElementsByTagName('script');
                for (var i = 0; i < scripts.length; i++){
                  if (scripts[i].src != ""){
                    //console.log("Added script to head");
                    addScriptToHead(scripts[i].src);
                  }
                  else{
                    eval(scripts[i].innerHTML);
                  }
                }
                for (var i = 0; i < data.extra_css.length; i++){
                  $("head").append(data.extra_css[i]);
                }
                document.title = data.browser_title;
                if ($("html").attr("lang") != data.lang){
                  $("html").attr("lang", data.lang);
                }
                pushChanges();
            });
            socket.on('pushchanges', function(data) {
                //console.log("Got pushchanges: " + JSON.stringify(data));
                var valArray = Object();
                var values = data.parameters;
                for (var i = 0; i < values.length; i++) {
                    valArray[values[i].name] = values[i].value;
                }
                $("#daform").each(function(){
                    $(this).find(':input').each(function(){
                        var type = $(this).attr('type');
                        var id = $(this).attr('id');
                        var name = $(this).attr('name');
                        if (type == 'checkbox'){
                            if (name in valArray){
                                if (valArray[name] == 'True'){
                                    if ($(this).prop('checked') != true){
                                        $(this).prop('checked', true);
                                        $(this).trigger('change');
                                    }
                                }
                                else{
                                    if ($(this).prop('checked') != false){
                                        $(this).prop('checked', false);
                                        $(this).trigger('change');
                                    }
                                }
                            }
                            else{
                                if ($(this).prop('checked') != false){
                                    $(this).prop('checked', false);
                                    $(this).trigger('change');
                                }
                            }
                        }
                        else if (type == 'radio'){
                            if (name in valArray){
                                if (valArray[name] == $(this).val()){
                                    if ($(this).prop('checked') != true){
                                        $(this).prop('checked', true);
                                        $(this).trigger('change');
                                    }
                                }
                                else{
                                    if ($(this).prop('checked') != false){
                                        $(this).prop('checked', false);
                                        $(this).trigger('change');
                                    }
                                }
                            }
                        }
                        else if ($(this).data().hasOwnProperty('sliderMax')){
                            $(this).slider('setValue', parseInt(valArray[name]));
                        }
                        else{
                            if (name in valArray){
                                $(this).val(valArray[name]);
                            }
                        }
                    });
                });
            });
        }
        observerChangesInterval = setInterval(pushChanges, """ + str(CHECKIN_INTERVAL) + """);
    });
    </script>
"""
    the_key = 'da:html:uid:' + str(uid) + ':i:' + str(i) + ':userid:' + str(userid)
    html = r.get(the_key)
    if html is not None:
        obj = json.loads(html)
    else:
        logmessage("observer: failed to load JSON from key " + the_key)
        obj = dict()
    output = standard_html_start(interview_language=obj.get('lang', 'en'), debug=DEBUG, bootstrap_theme=obj.get('bootstrap_theme', None))
    output += obj.get('global_css', '') + "\n" + indent_by("".join(obj.get('extra_css', list())), 4)
    output += '\n    <title>' + word('Observation') + '</title>\n  </head>\n  <body class="' + obj.get('bodyclass', 'dabody pad-for-navbar') + '">\n  <div id="dabody">\n  '
    output += obj.get('body', '')
    output += standard_scripts() + observation_script + "\n    " + "".join(obj.get('extra_scripts', list())) + "\n  </div>\n  </body>\n</html>"
    response = make_response(output.encode('utf8'), '200 OK')
    response.headers['Content-type'] = 'text/html; charset=utf-8'
    return response

@app.route('/monitor', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'advocate'])
def monitor():
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('interview_list')))
    session['monitor'] = 1
    if 'user_id' not in session:
        session['user_id'] = current_user.id
    phone_number_key = 'da:monitor:phonenumber:' + str(session['user_id'])
    default_phone_number = r.get(phone_number_key)
    if default_phone_number is None:
        default_phone_number = ''
    sub_role_key = 'da:monitor:userrole:' + str(session['user_id'])
    if r.exists(sub_role_key):
        subscribed_roles = r.hgetall(sub_role_key)
        r.expire(sub_role_key, 2592000)
    else:
        subscribed_roles = dict()
    key = 'da:monitor:available:' + str(current_user.id)
    if r.exists(key):
        daAvailableForChat = 'true'
    else:
        daAvailableForChat = 'false'
    call_forwarding_on = 'false'
    if twilio_config is not None:
        forwarding_phone_number = twilio_config['name']['default'].get('number', None)
        if forwarding_phone_number is not None:
            call_forwarding_on = 'true'
    script = "\n" + '    <script type="text/javascript" src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>' + "\n" + """    <script type="text/javascript" charset="utf-8">
      var daAudioContext = null;
      var socket;
      var soundBuffer = Object();
      var daShowingNotif = false;
      var daUpdatedSessions = Object();
      var daUserid = """ + str(current_user.id) + """;
      var daPhoneOnMessage = """ + json.dumps(word("The user can call you.  Click to cancel.")) + """;
      var daPhoneOffMessage = """ + json.dumps(word("Click if you want the user to be able to call you.")) + """;
      var daSessions = Object();
      var daAvailRoles = Object();
      var daChatPartners = Object();
      var daPhonePartners = Object();
      var daNewPhonePartners = Object();
      var daTermPhonePartners = Object();
      var daUsePhone = """ + call_forwarding_on + """;
      var daSubscribedRoles = """ + json.dumps(subscribed_roles) + """;
      var daAvailableForChat = """ + daAvailableForChat + """;
      var daPhoneNumber = """ + json.dumps(default_phone_number) + """;
      var daFirstTime = 1;
      var updateMonitorInterval = null;
      var daNotificationsEnabled = false;
      var daControlling = Object();
      var daBrowserTitle = """ + json.dumps(word('Monitor')) + """;
      window.gotConfirmation = function(key){
          //console.log("Got confirmation in parent for key " + key);
          // daControlling[key] = 2;
          // var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          // $("#listelement" + skey).find("a").each(function(){
          //     if ($(this).data('name') == "stopControlling"){
          //         $(this).removeClass('invisible');
          //         console.log("Found it");
          //     }
          // });
      }
      function faviconRegular(){
        var link = document.querySelector("link[rel*='shortcut icon'") || document.createElement('link');
        link.type = 'image/x-icon';
        link.rel = 'shortcut icon';
        link.href = '""" + url_for('favicon', nocache="1") + """';
        document.getElementsByTagName('head')[0].appendChild(link);
      }
      function faviconAlert(){
        var link = document.querySelector("link[rel*='shortcut icon'") || document.createElement('link');
        link.type = 'image/x-icon';
        link.rel = 'shortcut icon';
        link.href = '""" + url_for('static', filename='app/chat.ico') + """?nocache=1';
        document.getElementsByTagName('head')[0].appendChild(link);
      }
      function topMessage(message){
          var newDiv = document.createElement('div');
          $(newDiv).addClass("top-alert col-xs-10 col-sm-7 col-md-6 col-lg-5 col-centered");
          $(newDiv).html(message)
          $(newDiv).css("display", "none");
          $(newDiv).appendTo($("#dabody"));
          $(newDiv).slideDown();
          setTimeout(function(){
            $(newDiv).slideUp(300, function(){
              $(newDiv).remove();
            });
          }, 2000);
      }
      window.abortControlling = function(key){
          topMessage(""" + json.dumps(word("That screen is already being controlled by another operator")) + """);
          stopControlling(key);
      }
      window.stopControlling = function(key){
          //console.log("Got stopControlling in parent for key " + key);
          // if (daControlling.hasOwnProperty(key)){
          //   delete daControlling[key];
          // }
          var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          $("#listelement" + skey).find("a").each(function(){
              if ($(this).data('name') == "stopControlling"){
                  $(this).click();
                  //console.log("Found it");
              }
          });
      }
      function daOnError(){
          console.log('daOnError');
      }
      function loadSoundBuffer(key, url_a, url_b){
          //console.log("loadSoundBuffer");
          var pos = 0;
          if (daAudioContext == null){
              return;
          }
          var request = new XMLHttpRequest();
          request.open('GET', url_a, true);
          request.responseType = 'arraybuffer';
          request.onload = function(){
              daAudioContext.decodeAudioData(request.response, function(buffer){
                  if (!buffer){
                      if (pos == 1){
                          console.error('loadSoundBuffer: error decoding file data');
                          return;
                      }
                      else {
                          pos = 1;
                          console.info('loadSoundBuffer: error decoding file data, trying next source');
                          request.open("GET", url_b, true);
                          return request.send();
                      }
                  }
                  soundBuffer[key] = buffer;
              },
              function(error){
                  if (pos == 1){
                      console.error('loadSoundBuffer: decodeAudioData error');
                      return;
                  }
                  else{
                      pos = 1;
                      console.info('loadSoundBuffer: decodeAudioData error, trying next source');
                      request.open("GET", url_b, true);
                      return request.send();
                  }
              });
          }
          request.send();
      }
      function playSound(key) {
          //console.log("playSound");
          var buffer = soundBuffer[key];
          if (!daAudioContext || !buffer){
              return;
          }
          var source = daAudioContext.createBufferSource();
          source.buffer = buffer;
          source.connect(daAudioContext.destination);
          source.start(0);
      }
      function checkNotifications(){
          //console.log("checkNotifications");
          if (daNotificationsEnabled){
              return;
          }
          if (!("Notification" in window)) {
              daNotificationsEnabled = false;
              return;
          }
          if (Notification.permission === "granted") {
              daNotificationsEnabled = true;
              return;
          }
          if (Notification.permission !== 'denied') {
              Notification.requestPermission(function (permission) {
                  if (permission === "granted") {
                      daNotificationsEnabled = true;
                  }
              });
          }
      }
      function notifyOperator(key, mode, message) {
          //console.log("notifyOperator: " + key + " " + mode + " " + message);
          var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          if (mode == "chat"){
            playSound('newmessage');
          }
          else{
            playSound('newconversation');
          }
          if ($("#listelement" + skey).offset().top > $(window).scrollTop() + $(window).height()){
            if (mode == "chat"){
              $("#chat-message-below").html(""" + json.dumps(word("New message below")) + """);
            }
            else{
              $("#chat-message-below").html(""" + json.dumps(word("New conversation below")) + """);
            }
            //$("#chat-message-below").data('key', key);
            $("#chat-message-below").slideDown();
            daShowingNotif = true;
            markAsUpdated(key);
          }
          else if ($("#listelement" + skey).offset().top + $("#listelement" + skey).height() < $(window).scrollTop() + 32){
            if (mode == "chat"){
              $("#chat-message-above").html(""" + json.dumps(word("New message above")) + """);
            }
            else{
              $("#chat-message-above").html(""" + json.dumps(word("New conversation above")) + """);
            }
            //$("#chat-message-above").data('key', key);
            $("#chat-message-above").slideDown();
            daShowingNotif = true;
            markAsUpdated(key);
          }
          else{
            //console.log("It is visible");
          }
          if (!daNotificationsEnabled){
              //console.log("Browser will not enable notifications")
              return;
          }
          if (!("Notification" in window)) {
              return;
          }
          if (Notification.permission === "granted") {
              var notification = new Notification(message);
          }
          else if (Notification.permission !== 'denied') {
              Notification.requestPermission(function (permission) {
                  if (permission === "granted") {
                      var notification = new Notification(message);
                      daNotificationsEnabled = true;
                  }
              });
          }
      }
      function phoneNumberOk(){
          //console.log("phoneNumberOk");
          var phoneNumber = $("#daPhoneNumber").val();
          if (phoneNumber == '' || phoneNumber.match(/^\+?[1-9]\d{1,14}$/)){
              return true;
          }
          else{
              return false;
          }
      }
      function checkPhone(){
          //console.log("checkPhone");
          $("#daPhoneNumber").val($("#daPhoneNumber").val().replace(/[^0-9\+]/g, ''));
          var the_number = $("#daPhoneNumber").val();
          if (the_number[0] != '+'){
              $("#daPhoneNumber").val('+' + the_number);
          }
          if (phoneNumberOk()){
              $("#daPhoneNumber").parent().removeClass("has-error");
              $("#daPhoneError").addClass("invisible");
              daPhoneNumber = $("#daPhoneNumber").val();
              if (daPhoneNumber == ''){
                  daPhoneNumber = null;
              }
              else{
                  $(".phone").removeClass("invisible");
              }
              $("#daPhoneSaved").removeClass("invisible");
              setTimeout(function(){
                  $("#daPhoneSaved").addClass("invisible");
              }, 2000);
          }
          else{
              $("#daPhoneNumber").parent().addClass("has-error");
              $("#daPhoneError").removeClass("invisible");
              daPhoneNumber = null;
              $(".phone").addClass("invisible");
          }
      }
      function allSessions(uid, yaml_filename){
          //console.log("allSessions");
          var prefix = 'da:session:uid:' + uid + ':i:' + yaml_filename + ':userid:';
          var output = Array();
          for (var key in daSessions){
              if (daSessions.hasOwnProperty(key) && key.indexOf(prefix) == 0){
                  output.push(key);
              }
          }
          return(output);
      }
      function scrollChat(key){
          var chatScroller = $(key).find('ul').first();
          if (chatScroller.length){
              var height = chatScroller[0].scrollHeight;
              chatScroller.animate({scrollTop: height}, 800);
          }
          else{
              console.log("scrollChat: error")
          }
      }
      function scrollChatFast(key){
          var chatScroller = $(key).find('ul').first();
          if (chatScroller.length){
            var height = chatScroller[0].scrollHeight;
              //console.log("Scrolling to " + height + " where there are " + chatScroller[0].childElementCount + " children");
              chatScroller.scrollTop(height);
            }
          else{
              console.log("scrollChatFast: error")
          }
      }
      function do_update_monitor(){
          //console.log("do_update_monitor with " + daAvailableForChat);
          if (phoneNumberOk()){
            daPhoneNumber = $("#daPhoneNumber").val();
            if (daPhoneNumber == ''){
              daPhoneNumber = null;
            }
          }
          else{
            daPhoneNumber = null;
          }
          socket.emit('updatemonitor', {available_for_chat: daAvailableForChat, phone_number: daPhoneNumber, subscribed_roles: daSubscribedRoles, phone_partners_to_add: daNewPhonePartners, phone_partners_to_terminate: daTermPhonePartners});
      }
      function update_monitor(){
          //console.log("update_monitor with " + daAvailableForChat);
          if (updateMonitorInterval != null){
              clearInterval(updateMonitorInterval);
          }
          do_update_monitor();
          updateMonitorInterval = setInterval(do_update_monitor, """ + str(CHECKIN_INTERVAL) + """);
          //console.log("update_monitor");
      }
      function isHidden(ref){
          if ($(ref).length){
              if (($(ref).offset().top + $(ref).height() < $(window).scrollTop() + 32)){
                  return -1;
              }
              else if ($(ref).offset().top > $(window).scrollTop() + $(window).height()){
                  return 1;
              }
              else{
                  return 0;
              }
          }
          else{
              return 0;
          }
      }
      function markAsUpdated(key){
          //console.log("markAsUpdated with " + key);
          var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          if (isHidden("#listelement" + skey)){
              daUpdatedSessions["#listelement" + skey] = 1;
          }
      }
      function activateChatArea(key){
          //console.log("activateChatArea with " + key);
          var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          if (!$("#chatarea" + skey).find('input').first().is(':focus')){
            $("#listelement" + skey).addClass("new-message");
            if (daBrowserTitle == document.title){
              document.title = '* ' + daBrowserTitle;
              faviconAlert();
            }
          }
          markAsUpdated(key);
          $("#chatarea" + skey).removeClass('invisible');
          $("#chatarea" + skey).find('input, button').prop("disabled", false);
          $("#chatarea" + skey).find('ul').html('');
          socket.emit('chat_log', {key: key});
      }
      function deActivateChatArea(key){
          //console.log("daActivateChatArea with " + key);
          var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          $("#chatarea" + skey).find('input, button').prop("disabled", true);
          $("#listelement" + skey).removeClass("new-message");
          if (document.title != daBrowserTitle){
              document.title = daBrowserTitle;
              faviconRegular();
          }
      }
      function undraw_session(key){
          //console.log("Undrawing...");
          var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          var xButton = document.createElement('a');
          var xButtonIcon = document.createElement('i');
          $(xButton).addClass("corner-remove");
          $(xButtonIcon).addClass("fas fa-times-circle");
          $(xButtonIcon).appendTo($(xButton));
          $("#listelement" + skey).addClass("list-group-item-danger");
          $("#session" + skey).find("a").remove();
          $("#session" + skey).find("span").first().html(""" + json.dumps(word("offline")) + """);
          $("#session" + skey).find("span").first().removeClass('btn-info');
          $("#session" + skey).find("span").first().addClass('btn-danger');
          $(xButton).click(function(){
              $("#listelement" + skey).slideUp(300, function(){
                  $("#listelement" + skey).remove();
                  check_if_empty();
              });
          });
          $(xButton).appendTo($("#session" + skey));
          $("#chatarea" + skey).find('input, button').prop("disabled", true);
          var theIframe = $("#iframe" + skey).find('iframe')[0];
          if (theIframe){
              $(theIframe).contents().find('body').addClass("dainactive");
              if (theIframe.contentWindow && theIframe.contentWindow.turnOffControl){
                  theIframe.contentWindow.turnOffControl();
              }
          }
          if (daControlling.hasOwnProperty(key)){
              delete daControlling[key];
          }
          delete daSessions[key];
      }
      function publish_chat_log(uid, yaml_filename, userid, mode, messages){
          //console.log("publish_chat_log with " + uid + " " + yaml_filename + " " + userid + " " + mode + " " + messages);
          var keys; 
          //if (mode == 'peer' || mode == 'peerhelp'){
          //    keys = allSessions(uid, yaml_filename);
          //}
          //else{
              keys = ['da:session:uid:' + uid + ':i:' + yaml_filename + ':userid:' + userid];
          //}
          for (var i = 0; i < keys.length; ++i){
              key = keys[i];
              var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
              var chatArea = $("#chatarea" + skey).find('ul').first();
              for (var i = 0; i < messages.length; ++i){
                  var message = messages[i];
                  var newLi = document.createElement('li');
                  $(newLi).addClass("list-group-item");
                  if (message.is_self){
                      $(newLi).addClass("list-group-item-warning dalistright");
                  }
                  else{
                      $(newLi).addClass("list-group-item-info");
                  }
                  $(newLi).html(message.message);
                  $(newLi).appendTo(chatArea);
              }
              scrollChatFast("#chatarea" + skey);
          }
      }
      function check_if_empty(){
          if ($("#monitorsessions").find("li").length > 0){
              $("#emptylist").addClass("invisible");
          }
          else{
              $("#emptylist").removeClass("invisible");
          }
      }
      function draw_session(key, obj){
          //console.log("draw_session with " + key);
          var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
          var the_html;
          var wants_to_chat;
          if (obj.chatstatus != 'off'){ //obj.chatstatus == 'waiting' || obj.chatstatus == 'standby' || obj.chatstatus == 'ringing' || obj.chatstatus == 'ready' || obj.chatstatus == 'on' || obj.chatstatus == 'observeonly'
              wants_to_chat = true;
          }
          if (wants_to_chat){
              the_html = obj.browser_title + ' &mdash; '
              if (obj.hasOwnProperty('first_name')){
                the_html += obj.first_name + ' ' + obj.last_name;
              }
              else{
                the_html += """ + json.dumps(word("anonymous visitor") + ' ') + """ + obj.temp_user_id;
              }
          }
          var theListElement;
          var sessionDiv;
          var theIframeContainer;
          var theChatArea;
          if ($("#session" + skey).length && !(key in daSessions)){
              $("#listelement" + skey).removeClass("list-group-item-danger");
              $("#iframe" + skey).find('iframe').first().contents().find('body').removeClass("dainactive");
          }
          daSessions[key] = 1;
          if ($("#session" + skey).length){
              theListElement = $("#listelement" + skey).first();
              sessionDiv = $("#session" + skey).first();
              //controlDiv = $("#control" + skey).first();
              theIframeContainer = $("#iframe" + skey).first();
              theChatArea = $("#chatarea" + skey).first();
              $(sessionDiv).empty();
              if (obj.chatstatus == 'on' && key in daChatPartners && $("#chatarea" + skey).find('button').first().prop("disabled") == true){
                  activateChatArea(key);
              }
          }
          else{
              var theListElement = document.createElement('li');
              $(theListElement).addClass('list-group-item');
              $(theListElement).attr('id', "listelement" + key);
              var sessionDiv = document.createElement('div');
              $(sessionDiv).attr('id', "session" + key);
              $(sessionDiv).addClass('chat-session');
              $(sessionDiv).appendTo($(theListElement));
              $(theListElement).appendTo("#monitorsessions");
              // controlDiv = document.createElement('div');
              // $(controlDiv).attr('id', "control" + key);
              // $(controlDiv).addClass("chatcontrol invisible chat-session");
              // $(controlDiv).appendTo($(theListElement));
              theIframeContainer = document.createElement('div');
              $(theIframeContainer).addClass("observer-container invisible");
              $(theIframeContainer).attr('id', 'iframe' + key);
              var theIframe = document.createElement('iframe');
              $(theIframe).addClass("observer");
              $(theIframe).attr('name', 'iframe' + key);
              $(theIframe).appendTo($(theIframeContainer));
              $(theIframeContainer).appendTo($(theListElement));
              var theChatArea = document.createElement('div');
              $(theChatArea).addClass('monitor-chat-area invisible');
              $(theChatArea).html('<div class="row"><div class="col-md-12"><ul class="list-group dachatbox" id="daCorrespondence"></ul></div></div><form autocomplete="off"><div class="row"><div class="col-md-12"><div class="input-group"><input type="text" class="form-control" disabled><span class="input-group-btn"><button class="btn btn-secondary" type="button" disabled>""" + word("Send") + """</button></span></div></div></div></form>');
              $(theChatArea).attr('id', 'chatarea' + key);
              var submitter = function(){
                  //console.log("I am the submitter and I am submitting " + key);
                  var input = $(theChatArea).find("input").first();
                  var message = input.val().trim();
                  if (message == null || message == ""){
                      //console.log("Message was blank");
                      return false;
                  }
                  socket.emit('chatmessage', {key: key, data: input.val()});
                  input.val('');
                  return false;
              };
              $(theChatArea).find("button").click(submitter);
              $(theChatArea).find("input").bind('keypress keydown keyup', function(e){
                  if(e.keyCode == 13) { submitter(); e.preventDefault(); }
              });
              $(theChatArea).find("input").focus(function(){
                  $(theListElement).removeClass("new-message");
                  if (document.title != daBrowserTitle){
                      document.title = daBrowserTitle;
                      faviconRegular();
                  }
              });
              $(theChatArea).appendTo($(theListElement));
              if (obj.chatstatus == 'on' && key in daChatPartners){
                  activateChatArea(key);
              }
          }
          var theText = document.createElement('span');
          $(theText).addClass('chat-title-label');
          theText.innerHTML = the_html;
          var statusLabel = document.createElement('span');
          $(statusLabel).addClass("badge badge-info chat-status-label");
          $(statusLabel).html(obj.chatstatus == 'observeonly' ? 'off' : obj.chatstatus);
          $(statusLabel).appendTo($(sessionDiv));
          if (daUsePhone){
            var phoneButton = document.createElement('a');
            var phoneIcon = document.createElement('i');
            $(phoneIcon).addClass("fas fa-phone");
            $(phoneIcon).appendTo($(phoneButton));
            $(phoneButton).addClass("btn phone");
            $(phoneButton).data('name', 'phone');
            if (key in daPhonePartners){
              $(phoneButton).addClass("phone-on btn-success");
              $(phoneButton).attr('title', daPhoneOnMessage);
            }
            else{
              $(phoneButton).addClass("phone-off btn-secondary");
              $(phoneButton).attr('title', daPhoneOffMessage);
            }
            $(phoneButton).attr('tabindex', 0);
            $(phoneButton).addClass('observebutton')
            $(phoneButton).appendTo($(sessionDiv));
            $(phoneButton).attr('href', '#');
            if (daPhoneNumber == null){
              $(phoneButton).addClass("invisible");
            }
            $(phoneButton).click(function(e){
              if ($(this).hasClass("phone-off") && daPhoneNumber != null){
                $(this).removeClass("phone-off");
                $(this).removeClass("btn-secondary");
                $(this).addClass("phone-on");
                $(this).addClass("btn-success");
                $(this).attr('title', daPhoneOnMessage);
                daPhonePartners[key] = 1;
                daNewPhonePartners[key] = 1;
                if (key in daTermPhonePartners){
                  delete daTermPhonePartners[key];
                }
                update_monitor();
              }
              else{
                $(this).removeClass("phone-on");
                $(this).removeClass("btn-success");
                $(this).addClass("phone-off");
                $(this).addClass("btn-secondary");
                $(this).attr('title', daPhoneOffMessage);
                if (key in daPhonePartners){
                  delete daPhonePartners[key];
                }
                if (key in daNewPhonePartners){
                  delete daNewPhonePartners[key];
                }
                daTermPhonePartners[key] = 1;
                update_monitor();
              }
              e.preventDefault();
              return false;
            });
          }
          var unblockButton = document.createElement('a');
          $(unblockButton).addClass("btn btn-info observebutton");
          $(unblockButton).data('name', 'unblock');
          if (!obj.blocked){
              $(unblockButton).addClass("invisible");
          }
          $(unblockButton).html(""" + json.dumps(word("Unblock")) + """);
          $(unblockButton).attr('href', '#');
          $(unblockButton).appendTo($(sessionDiv));
          var blockButton = document.createElement('a');
          $(blockButton).addClass("btn btn-danger observebutton");
          if (obj.blocked){
              $(blockButton).addClass("invisible");
          }
          $(blockButton).html(""" + json.dumps(word("Block")) + """);
          $(blockButton).attr('href', '#');
          $(blockButton).data('name', 'block');
          $(blockButton).appendTo($(sessionDiv));
          $(blockButton).click(function(e){
              $(unblockButton).removeClass("invisible");
              $(this).addClass("invisible");
              deActivateChatArea(key);
              socket.emit('block', {key: key});
              e.preventDefault();
              return false;
          });
          $(unblockButton).click(function(e){
              $(blockButton).removeClass("invisible");
              $(this).addClass("invisible");
              socket.emit('unblock', {key: key});
              e.preventDefault();
              return false;
          });
          var joinButton = document.createElement('a');
          $(joinButton).addClass("btn btn-warning observebutton");
          $(joinButton).html(""" + json.dumps(word("Join")) + """);
          $(joinButton).attr('href', """ + json.dumps(url_for('visit_interview') + '?') + """ + $.param({i: obj.i, uid: obj.uid, userid: obj.userid}));
          $(joinButton).data('name', 'join');
          $(joinButton).attr('target', '_blank');
          $(joinButton).appendTo($(sessionDiv));
          if (wants_to_chat){
              var openButton = document.createElement('a');
              $(openButton).addClass("btn btn-primary observebutton");
              $(openButton).attr('href', """ + json.dumps(url_for('observer') + '?') + """ + $.param({i: obj.i, uid: obj.uid, userid: obj.userid}));
              //$(openButton).attr('href', 'about:blank');
              $(openButton).attr('id', 'observe' + key);
              $(openButton).attr('target', 'iframe' + key);
              $(openButton).html(""" + json.dumps(word("Observe")) + """);
              $(openButton).data('name', 'open');
              $(openButton).appendTo($(sessionDiv));
              var stopObservingButton = document.createElement('a');
              $(stopObservingButton).addClass("btn btn-secondary observebutton invisible");
              $(stopObservingButton).html(""" + json.dumps(word("Stop Observing")) + """);
              $(stopObservingButton).attr('href', '#');
              $(stopObservingButton).data('name', 'stopObserving');
              $(stopObservingButton).appendTo($(sessionDiv));
              var controlButton = document.createElement('a');
              $(controlButton).addClass("btn btn-info observebutton");
              $(controlButton).html(""" + json.dumps(word("Control")) + """);
              $(controlButton).attr('href', '#');
              $(controlButton).data('name', 'control');
              $(controlButton).appendTo($(sessionDiv));
              var stopControllingButton = document.createElement('a');
              $(stopControllingButton).addClass("btn btn-secondary observebutton invisible");
              $(stopControllingButton).html(""" + json.dumps(word("Stop Controlling")) + """);
              $(stopControllingButton).attr('href', '#');
              $(stopControllingButton).data('name', 'stopControlling');
              $(stopControllingButton).appendTo($(sessionDiv));
              $(controlButton).click(function(event){
                  event.preventDefault();
                  //console.log("Controlling...");
                  $(this).addClass("invisible");
                  $(stopControllingButton).removeClass("invisible");
                  $(stopObservingButton).addClass("invisible");
                  var theIframe = $("#iframe" + skey).find('iframe')[0];
                  if (theIframe != null && theIframe.contentWindow){
                      theIframe.contentWindow.turnOnControl();
                  }
                  else{
                      console.log("Cannot turn on control");
                  }
                  daControlling[key] = 1;
                  return false;
              });
              $(stopControllingButton).click(function(event){
                  //console.log("Got click on stopControllingButton");
                  event.preventDefault();
                  var theIframe = $("#iframe" + skey).find('iframe')[0];
                  if (theIframe != null && theIframe.contentWindow && theIframe.contentWindow.turnOffControl){
                      theIframe.contentWindow.turnOffControl();
                  }
                  else{
                      console.log("Cannot turn off control");
                      return false;
                  }
                  //console.log("Stop controlling...");
                  $(this).addClass("invisible");
                  $(controlButton).removeClass("invisible");
                  $(stopObservingButton).removeClass("invisible");
                  if (daControlling.hasOwnProperty(key)){
                      delete daControlling[key];
                  }
                  return false;
              });
              $(openButton).click(function(){
                  //console.log("Observing..");
                  $(this).addClass("invisible");
                  $(stopObservingButton).removeClass("invisible");
                  $("#iframe" + skey).removeClass("invisible");
                  $(controlButton).removeClass("invisible");
                  return true;
              });
              $(stopObservingButton).click(function(e){
                  //console.log("Unobserving...");
                  $(this).addClass("invisible");
                  $(openButton).removeClass("invisible");
                  $(controlButton).addClass("invisible");
                  $(stopObservingButton).addClass("invisible");
                  $(stopControllingButton).addClass("invisible");
                  var theIframe = $("#iframe" + skey).find('iframe')[0];
                  if (daControlling.hasOwnProperty(key)){
                      delete daControlling[key];
                      if (theIframe != null && theIframe.contentWindow && theIframe.contentWindow.turnOffControl){
                          //console.log("Calling turnOffControl in iframe");
                          theIframe.contentWindow.turnOffControl();
                      }
                  }
                  if (theIframe != null && theIframe.contentWindow){
                      //console.log("Deleting the iframe");
                      theIframe.contentWindow.document.open();
                      theIframe.contentWindow.document.write("");
                      theIframe.contentWindow.document.close();
                  }
                  $("#iframe" + skey).slideUp(400, function(){
                      $(this).css("display", "").addClass("invisible");
                  });
                  e.preventDefault();
                  return false;
              });
              if ($(theIframeContainer).hasClass("invisible")){
                  $(openButton).removeClass("invisible");
                  $(stopObservingButton).addClass("invisible");
                  $(controlButton).addClass("invisible");
                  $(stopControllingButton).addClass("invisible");
                  if (daControlling.hasOwnProperty(key)){
                      delete daControlling[key];
                  }
              }
              else{
                  $(openButton).addClass("invisible");
                  if (daControlling.hasOwnProperty(key)){
                      $(stopObservingButton).addClass("invisible");
                      $(controlButton).addClass("invisible");
                      $(stopControllingButton).removeClass("invisible");
                  }
                  else{
                      $(stopObservingButton).removeClass("invisible");
                      $(controlButton).removeClass("invisible");
                      $(stopControllingButton).addClass("invisible");
                  }
              }
          }
          $(theText).appendTo($(sessionDiv));
          if (obj.chatstatus == 'on' && key in daChatPartners && $("#chatarea" + skey).hasClass('invisible')){
              activateChatArea(key);
          }
          if ((obj.chatstatus != 'on' || !(key in daChatPartners)) && $("#chatarea" + skey).find('button').first().prop("disabled") == false){
              deActivateChatArea(key);
          }
          else if (obj.blocked){
              deActivateChatArea(key);
          }
      }
      function onScrollResize(){
          if (document.title != daBrowserTitle){
              document.title = daBrowserTitle;
              faviconRegular();
          }
          if (!daShowingNotif){
              return true;
          }
          var obj = Array();
          for (var key in daUpdatedSessions){
              if (daUpdatedSessions.hasOwnProperty(key)){
                  obj.push(key);
              }
          }
          var somethingAbove = false;
          var somethingBelow = false;
          var firstElement = -1;
          var lastElement = -1;
          for (var i = 0; i < obj.length; ++i){
              var result = isHidden(obj[i]);
              if (result == 0){
                  delete daUpdatedSessions[obj[i]];
              }
              else if (result < 0){
                  var top = $(obj[i]).offset().top;
                  somethingAbove = true;
                  if (firstElement == -1 || top < firstElement){
                      firstElement = top;
                  }
              }
              else if (result > 0){
                  var top = $(obj[i]).offset().top;
                  somethingBelow = true;
                  if (lastElement == -1 || top > lastElement){
                      lastElement = top;
                  }
              }
          }
          if (($("#chat-message-above").is(":visible")) && !somethingAbove){
              $("#chat-message-above").hide();
          }
          if (($("#chat-message-below").is(":visible")) && !somethingBelow){
              $("#chat-message-below").hide();
          }
          if (!(somethingAbove || somethingBelow)){
              daShowingNotif = false;
          }
          return true;
      }
      $(document).ready(function(){
          //console.log("document ready");
          try {
              window.AudioContext = window.AudioContext || window.webkitAudioContext;
              daAudioContext = new AudioContext();
          }
          catch(e) {
              console.log('Web Audio API is not supported in this browser');
          }
          loadSoundBuffer('newmessage', '""" + url_for('static', filename='sounds/notification-click-on.mp3') + """', '""" + url_for('static', filename='sounds/notification-click-on.ogg') + """');
          loadSoundBuffer('newconversation', '""" + url_for('static', filename='sounds/notification-stapler.mp3') + """', '""" + url_for('static', filename='sounds/notification-stapler.ogg') + """');
          loadSoundBuffer('signinout', '""" + url_for('static', filename='sounds/notification-snap.mp3') + """', '""" + url_for('static', filename='sounds/notification-snap.ogg') + """');
          if (location.protocol === 'http:' || document.location.protocol === 'http:'){
              socket = io.connect("http://" + document.domain + "/monitor" + location.port, {path: '/ws/socket.io'});
          }
          if (location.protocol === 'https:' || document.location.protocol === 'https:'){
              socket = io.connect("https://" + document.domain + "/monitor" + location.port, {path: '/ws/socket.io'});
          }
          //console.log("socket is " + socket)
          if (typeof socket !== 'undefined') {
              socket.on('connect', function() {
                  //console.log("Connected!");
                  update_monitor();
              });
              socket.on('terminate', function() {
                  //console.log("monitor: terminating socket");
                  socket.disconnect();
              });
              socket.on('disconnect', function() {
                  //console.log("monitor: disconnected socket");
                  //socket = null;
              });
              socket.on('refreshsessions', function(data) {
                  update_monitor();
              });
              // socket.on('abortcontroller', function(data) {
              //     console.log("Got abortcontroller message for " + data.key);
              // });
              socket.on('chatready', function(data) {
                  var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                  //console.log('chatready: ' + key);
                  activateChatArea(key);
                  notifyOperator(key, "chatready", """ + json.dumps(word("New chat connection from")) + """ + ' ' + data.name)
              });
              socket.on('chatstop', function(data) {
                  var key = 'da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid
                  //console.log('chatstop: ' + key);
                  if (key in daChatPartners){
                      delete daChatPartners[key];
                  }
                  deActivateChatArea(key);
              });
              socket.on('chat_log', function(arg) {
                  //console.log('chat_log: ' + arg.userid);
                  publish_chat_log(arg.uid, arg.i, arg.userid, arg.mode, arg.data);
              });            
              socket.on('block', function(arg) {
                  //console.log("back from blocking " + arg.key);
                  update_monitor();
              });            
              socket.on('unblock', function(arg) {
                  //console.log("back from unblocking " + arg.key);
                  update_monitor();
              });            
              socket.on('chatmessage', function(data) {
                  //console.log("chatmessage");
                  var keys; 
                  if (data.data.mode == 'peer' || data.data.mode == 'peerhelp'){
                    keys = allSessions(data.uid, data.i);
                  }
                  else{
                    keys = ['da:session:uid:' + data.uid + ':i:' + data.i + ':userid:' + data.userid];
                  }
                  for (var i = 0; i < keys.length; ++i){
                    key = keys[i];
                    var skey = key.replace(/(:|\.|\[|\]|,|=|\/)/g, '\\\\$1');
                    //console.log("Received chat message for #chatarea" + skey);
                    var chatArea = $("#chatarea" + skey).find('ul').first();
                    var newLi = document.createElement('li');
                    $(newLi).addClass("list-group-item");
                    if (data.data.is_self){
                      $(newLi).addClass("list-group-item-warning dalistright");
                    }
                    else{
                      $(newLi).addClass("list-group-item-info");
                    }
                    $(newLi).html(data.data.message);
                    $(newLi).appendTo(chatArea);
                    scrollChat("#chatarea" + skey);
                    if (data.data.is_self){
                      $("#listelement" + skey).removeClass("new-message");
                      if (document.title != daBrowserTitle){
                        document.title = daBrowserTitle;
                        faviconRegular();
                      }
                    }
                    else{
                      if (!$("#chatarea" + skey).find('input').first().is(':focus')){
                        $("#listelement" + skey).addClass("new-message");
                        if (daBrowserTitle == document.title){
                          document.title = '* ' + daBrowserTitle;
                          faviconAlert();
                        }
                      }
                      if (data.data.hasOwnProperty('temp_user_id')){
                        notifyOperator(key, "chat", """ + json.dumps(word("anonymous visitor")) + """ + ' ' + data.data.temp_user_id + ': ' + data.data.message);
                      }
                      else{
                        if (data.data.first_name && data.data.first_name != ''){
                          notifyOperator(key, "chat", data.data.first_name + ' ' + data.data.last_name + ': ' + data.data.message);
                        }
                        else{
                          notifyOperator(key, "chat", data.data.email + ': ' + data.data.message);
                        }
                      }
                    }
                  }
              });
              socket.on('sessionupdate', function(data) {
                  //console.log("Got session update: " + data.session.chatstatus);
                  draw_session(data.key, data.session);
                  check_if_empty();
              });
              socket.on('updatemonitor', function(data) {
                  //console.log("Got update monitor response");
                  //console.log("updatemonitor: chat partners are: " + data.chatPartners);
                  daChatPartners = data.chatPartners;
                  daNewPhonePartners = Object();
                  daTermPhonePartners = Object();
                  daPhonePartners = data.phonePartners;
                  var newSubscribedRoles = Object();
                  for (var key in data.subscribedRoles){
                      if (data.subscribedRoles.hasOwnProperty(key)){
                          newSubscribedRoles[key] = 1;
                      }
                  }
                  for (var i = 0; i < data.availRoles.length; ++i){
                      var key = data.availRoles[i];
                      var skey = key.replace(/(:|\.|\[|\]|,|=|\/| )/g, '\\\\$1');
                      if ($("#role" + skey).length == 0){
                          var div = document.createElement('div');
                          $(div).addClass("form-check form-check-inline");
                          var label = document.createElement('label');
                          $(label).addClass('form-check-label');
                          $(label).attr('for', "role" + key);
                          var input = document.createElement('input');
                          $(input).addClass('form-check-input');
                          var text = document.createTextNode(key);
                          $(input).attr('type', 'checkbox');
                          $(input).attr('id', "role" + key);
                          if (key in newSubscribedRoles){
                              $(input).prop('checked', true);
                          }
                          else{
                              $(input).prop('checked', false);
                          }
                          $(input).val(key);
                          $(text).appendTo($(label));
                          $(input).appendTo($(div));
                          $(label).appendTo($(div));
                          $(div).appendTo($("#monitorroles"));
                          $(input).change(function(){
                              var key = $(this).val();
                              //console.log("change to " + key);
                              if ($(this).is(":checked")) {
                                  //console.log("it is checked");
                                  daSubscribedRoles[key] = 1;
                              }
                              else{
                                  //console.log("it is not checked");
                                  if (key in daSubscribedRoles){
                                      delete daSubscribedRoles[key];
                                  }
                              }
                              update_monitor();
                          });
                      }
                      else{
                          var input = $("#role" + skey).first();
                          if (key in newSubscribedRoles){
                              $(input).prop('checked', true);
                          }
                          else{
                              $(input).prop('checked', false);
                          }
                      }
                  }
                  daSubscribedRoles = newSubscribedRoles;
                  newDaSessions = Object();
                  for (var key in data.sessions){
                      if (data.sessions.hasOwnProperty(key)){
                          var user_id = key.replace(/^.*:userid:/, '');
                          if (true || user_id != daUserid){
                              var obj = data.sessions[key];
                              newDaSessions[key] = obj;
                              draw_session(key, obj);
                          }
                      }
                  }
                  var toDelete = Array();
                  var numSessions = 0;
                  for (var key in daSessions){
                      if (daSessions.hasOwnProperty(key)){
                          numSessions++;
                          if (!(key in newDaSessions)){
                              toDelete.push(key);
                          }
                      }
                  }
                  for (var i = 0; i < toDelete.length; ++i){
                      var key = toDelete[i];
                      undraw_session(key);
                  }
                  if ($("#monitorsessions").find("li").length > 0){
                      $("#emptylist").addClass("invisible");
                  }
                  else{
                      $("#emptylist").removeClass("invisible");
                  }
              });
          }
          if (daAvailableForChat){
              $("#daNotAvailable").addClass("invisible");
              checkNotifications();
          }
          else{
              $("#daAvailable").addClass("invisible");
          }
          $("#daAvailable").click(function(){
              $("#daAvailable").addClass("invisible");
              $("#daNotAvailable").removeClass("invisible");
              daAvailableForChat = false;
              //console.log("daAvailableForChat: " + daAvailableForChat);
              update_monitor();
              playSound('signinout');
          });
          $("#daNotAvailable").click(function(){
              checkNotifications();
              $("#daNotAvailable").addClass("invisible");
              $("#daAvailable").removeClass("invisible");
              daAvailableForChat = true;
              //console.log("daAvailableForChat: " + daAvailableForChat);
              update_monitor();
              playSound('signinout');
          });
          $( window ).bind('unload', function() {
            if (typeof socket !== 'undefined'){
              socket.emit('terminate');
            }
          });
          if (daUsePhone){
            $("#daPhoneInfo").removeClass("invisible");
            $("#daPhoneNumber").val(daPhoneNumber);
            $("#daPhoneNumber").change(checkPhone);
            $("#daPhoneNumber").bind('keypress keydown keyup', function(e){
              if(e.keyCode == 13) { $(this).blur(); e.preventDefault(); }
            });
          }
          $(window).on('scroll', onScrollResize);
          $(window).on('resize', onScrollResize);
          $(".chat-notifier").click(function(e){
              //var key = $(this).data('key');
              var direction = 0;
              if ($(this).attr('id') == "chat-message-above"){
                  direction = -1;
              }
              else{
                  direction = 1;
              }
              var target = -1;
              var targetElement = null;
              for (var key in daUpdatedSessions){
                  if (daUpdatedSessions.hasOwnProperty(key)){
                      var top = $(key).offset().top;
                      if (direction == -1){
                          if (target == -1 || top < target){
                              target = top;
                              targetElement = key;
                          }
                      }
                      else{
                          if (target == -1 || top > target){
                              target = top;
                              targetElement = key;
                          }
                      }
                  }
              }
              if (target >= 0){
                  $("html, body").animate({scrollTop: target - 60}, 500, function(){
                      $(targetElement).find("input").first().focus();
                  });
              }
              e.preventDefault();
              return false;
          });
      });
    </script>"""
    return render_template('pages/monitor.html', version_warning=None, bodyclass='adminbody', extra_js=Markup(script), tab_title=word('Monitor'), page_title=word('Monitor')), 200

@app.route('/updatingpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package_wait():
    next_url = request.args.get('next', url_for('update_package'))
    my_csrf = generate_csrf()
    script = """
    <script>
      var checkinInterval = null;
      var resultsAreIn = false;
      var pollDelay = 0;
      var pollPending = false;
      function daRestartCallback(data){
        //console.log("Restart result: " + data.success);
      }
      function daRestart(){
        $.ajax({
          type: 'POST',
          url: """ + json.dumps(url_for('restart_ajax')) + """,
          data: 'csrf_token=""" + my_csrf + """&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        });
        return true;
      }
      function daUpdateCallback(data){
        pollPending = false;
        if (data.success){
          if (data.status == 'finished'){
            resultsAreIn = true;
            if (data.ok){
              $("#notification").html(""" + json.dumps(word("The package update was successful.  The logs are below.")) + """);
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-danger");
              $("#notification").addClass("alert-success");
            }
            else{
              $("#notification").html(""" + json.dumps(word("The package update was not fully successful.  The logs are below.")) + """);
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-success");
              $("#notification").addClass("alert-danger");
            }
            $("#resultsContainer").show();
            $("#resultsArea").html(data.summary);
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
            daRestart();
          }
          else if (data.status == 'failed' && !resultsAreIn){
            resultsAreIn = true;
            $("#notification").html(""" + json.dumps(word("There was an error updating the packages.")) + """);
            $("#notification").removeClass("alert-info");
            $("#notification").removeClass("alert-success");
            $("#notification").addClass("alert-danger");
            $("#resultsContainer").show();
            if (data.error_message){
              $("#resultsArea").html(data.error_message);
            }
            else if (data.summary){
              $("#resultsArea").html(data.summary);
            }
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
          }
        }
        else if (!resultsAreIn){
          $("#notification").html(""" + json.dumps(word("There was an error.")) + """);
          $("#notification").removeClass("alert-info");
          $("#notification").removeClass("alert-success");
          $("#notification").addClass("alert-danger");
          if (checkinInterval != null){
            clearInterval(checkinInterval);
          }
        }
      }
      function daUpdate(){
        if (pollDelay > 5){
          $("#notification").html(""" + json.dumps(word("Server did not respond to request for update.")) + """);
          $("#notification").removeClass("alert-info");
          $("#notification").removeClass("alert-success");
          $("#notification").addClass("alert-danger");
          if (checkinInterval != null){
            clearInterval(checkinInterval);
          }
          return;
        }
        if (pollPending){
          pollDelay += 1;
          return;
        }
        if (resultsAreIn){
          return;
        }
        pollDelay = 0;
        pollPending = true;
        $.ajax({
          type: 'POST',
          url: """ + json.dumps(url_for('update_package_ajax')) + """,
          data: 'csrf_token=""" + my_csrf + """',
          success: daUpdateCallback,
          dataType: 'json'
        });
        return true;
      }
      $( document ).ready(function() {
        //console.log("page loaded");
        checkinInterval = setInterval(daUpdate, 6000);
      });
    </script>"""
    return render_template('pages/update_package_wait.html', version_warning=None, bodyclass='adminbody', extra_js=Markup(script), tab_title=word('Updating'), page_title=word('Updating'), next_page=next_url)

@app.route('/update_package_ajax', methods=['POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package_ajax():
    if 'taskwait' not in session:
        return jsonify(success=False)
    result = docassemble.webapp.worker.workerapp.AsyncResult(id=session['taskwait'])
    if result.ready():
        #if 'taskwait' in session:
        #    del session['taskwait']
        the_result = result.get()
        if type(the_result) is ReturnValue:
            if the_result.ok:
                #logmessage("update_package_ajax: success")
                return jsonify(success=True, status='finished', ok=the_result.ok, summary=summarize_results(the_result.results, the_result.logmessages))
            elif hasattr(the_result, 'error_message'):
                logmessage("update_package_ajax: failed return value is " + str(the_result.error_message))
                return jsonify(success=True, status='failed', error_message=str(the_result.error_message))
            elif hasattr(the_result, 'results') and hasattr(the_result, 'logmessages'):
                return jsonify(success=True, status='failed', summary=summarize_results(the_result.results, the_result.logmessages))
            else:
                return jsonify(success=True, status='failed', error_message=str("No error message.  Result is " + str(the_result)))
        else:
            logmessage("update_package_ajax: failed return value is a " + str(type(the_result)))
            logmessage("update_package_ajax: failed return value is " + str(the_result))
            return jsonify(success=True, status='failed', error_message=str(the_result))
    else:
        return jsonify(success=True, status='waiting')

def get_package_name_from_zip(zippath):
    with zipfile.ZipFile(zippath, mode='r') as zf:
        min_level = 999999
        setup_py = None
        for zinfo in zf.infolist():
            parts = splitall(zinfo.filename)
            if parts[-1] == 'setup.py':
                if len(parts) < min_level:
                    setup_py = zinfo
                    min_level = len(parts)
        if setup_py is None:
            raise Exception("Not a Python package zip file")
        contents = zf.read(setup_py)
    contents = re.sub(r'.*setup\(', '', contents, flags=re.DOTALL)
    extracted = dict()
    for line in contents.splitlines():
        m = re.search(r"^ *([a-z_]+) *= *\(?u?'(.*)'", line)
        if m:
            extracted[m.group(1)] = m.group(2)
        m = re.search(r'^ *([a-z_]+) *= *\(?u?"(.*)"', line)
        if m:
            extracted[m.group(1)] = m.group(2)
        m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
    if 'name' not in extracted:
        raise Exception("Could not find name of Python package")
    return extracted['name']    
    
@app.route('/updatepackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def update_package():
    if 'taskwait' in session:
        del session['taskwait']
    #pip.utils.logging._log_state = threading.local()
    #pip.utils.logging._log_state.indentation = 0
    form = UpdatePackageForm(request.form)
    form.gitbranch.choices = [('', "Not applicable")]
    if form.gitbranch.data:
        form.gitbranch.choices.append((form.gitbranch.data, form.gitbranch.data))
    action = request.args.get('action', None)
    target = request.args.get('package', None)
    is_base_upgrade = request.args.get('base', False)
    branch = None
    if action is not None and target is not None:
        package_list, package_auth = get_package_info()
        the_package = None
        for package in package_list:
            if package.package.name == target:
                the_package = package
                break
        if the_package is not None:
            if action == 'uninstall' and the_package.can_uninstall:
                uninstall_package(target)
            elif action == 'update' and the_package.can_update:
                existing_package = Package.query.filter_by(name=target, active=True).order_by(Package.id.desc()).first()
                if existing_package is not None:
                    if existing_package.type == 'git' and existing_package.giturl is not None:
                        if existing_package.gitbranch:
                            install_git_package(target, existing_package.giturl, branch=existing_package.gitbranch)
                        else:
                            install_git_package(target, existing_package.giturl)
                    elif existing_package.type == 'pip':
                        install_pip_package(existing_package.name, existing_package.limitation)
        result = docassemble.webapp.worker.update_packages.delay()
        session['taskwait'] = result.id
        return redirect(url_for('update_package_wait'))
    if request.method == 'POST' and form.validate_on_submit():
        use_pip_cache = form.use_cache.data
        pipe = r.pipeline()
        pipe.set('da:updatepackage:use_pip_cache', 1 if use_pip_cache else 0)
        pipe.expire('da:updatepackage:use_pip_cache', 120)
        pipe.execute()
        if 'zipfile' in request.files and request.files['zipfile'].filename:
            try:
                the_file = request.files['zipfile']
                filename = secure_filename(the_file.filename)
                file_number = get_new_file_number(session.get('uid', None), filename)
                saved_file = SavedFile(file_number, extension='zip', fix=True)
                file_set_attributes(file_number, private=False, persistent=True)
                zippath = saved_file.path
                the_file.save(zippath)
                saved_file.save()
                saved_file.finalize()
                pkgname = get_package_name_from_zip(zippath)
                if user_can_edit_package(pkgname=pkgname):
                    install_zip_package(pkgname, file_number)
                    result = docassemble.webapp.worker.update_packages.delay()
                    session['taskwait'] = result.id
                    return redirect(url_for('update_package_wait'))
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            except Exception as errMess:
                flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        else:
            if form.giturl.data:
                giturl = form.giturl.data.strip()
                branch = form.gitbranch.data.strip()
                packagename = re.sub(r'/*$', '', giturl)
                packagename = re.sub(r'^git+', '', packagename)
                packagename = re.sub(r'#.*', '', packagename)
                packagename = re.sub(r'\.git$', '', packagename)
                packagename = re.sub(r'.*/', '', packagename)
                if user_can_edit_package(giturl=giturl) and user_can_edit_package(pkgname=packagename):
                    if branch:
                        install_git_package(packagename, giturl, branch=branch)
                    else:
                        install_git_package(packagename, giturl)
                    result = docassemble.webapp.worker.update_packages.delay()
                    session['taskwait'] = result.id
                    return redirect(url_for('update_package_wait'))
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            elif form.pippackage.data:
                m = re.match(r'([^>=<]+)([>=<]+.+)', form.pippackage.data)
                if m:
                    packagename = m.group(1)
                    limitation = m.group(2)
                else:
                    packagename = form.pippackage.data
                    limitation = None
                packagename = re.sub(r'[^A-Za-z0-9\_\-\.]', '', packagename)
                if user_can_edit_package(pkgname=packagename):
                    install_pip_package(packagename, limitation)
                    result = docassemble.webapp.worker.update_packages.delay()
                    session['taskwait'] = result.id
                    return redirect(url_for('update_package_wait'))
                else:
                    flash(word("You do not have permission to install this package."), 'error')
            else:
                flash(word('You need to supply a Git URL, upload a file, or supply the name of a package on PyPI.'), 'error')
    package_list, package_auth = get_package_info(exclude_core=True)
    form.pippackage.data = None
    form.giturl.data = None
    extra_js = """
    <script>
      var default_branch = """ + json.dumps(branch if branch else 'master') + """;
      function get_branches(){
        var elem = $("#gitbranch");
        elem.empty();
        var opt = $("<option></option>");
        opt.attr("value", "").text("Not applicable");
        elem.append(opt);
        var github_url = $("#giturl").val();
        if (!github_url){
          return;
        }
        $.get(""" + json.dumps(url_for('get_git_branches')) + """, { url: github_url }, "json")
        .done(function(data){
          //console.log(data);
          if (data.success){
            var n = data.result.length;
            if (n > 0){
              elem.empty();
              for (var i = 0; i < n; i++){
                opt = $("<option></option>");
                opt.attr("value", data.result[i].name).text(data.result[i].name);
                if (data.result[i].name == default_branch){
                  opt.prop('selected', true);
                }
                $(elem).append(opt);
              }
            }
          }
        });
      }
      $( document ).ready(function() {
        get_branches();
        $("#giturl").on('change', get_branches);
      });
      $('#zipfile').on('change', function(){
        var fileName = $(this).val();
        fileName = fileName.replace(/.*\\\\/, '');
        fileName = fileName.replace(/.*\\//, '');
        $(this).next('.custom-file-label').html(fileName);
      });
    </script>"""
    python_version = daconfig.get('python version', word('Unknown'))
    version = word("Current") + ': <span class="badge badge-secondary">' + unicode(python_version) + '</span>'
    dw_status = pypi_status('docassemble.webapp')
    if not dw_status['error'] and 'info' in dw_status and 'info' in dw_status['info'] and 'version' in dw_status['info']['info'] and dw_status['info']['info']['version'] != unicode(python_version):
        version += ' ' + word("Available") + ': <span class="badge badge-success">' + dw_status['info']['info']['version'] + '</span>'
    return render_template('pages/update_package.html', version_warning=version_warning, bodyclass='adminbody', form=form, package_list=package_list, tab_title=word('Package Management'), page_title=word('Package Management'), extra_js=Markup(extra_js), version=Markup(version)), 200

# @app.route('/testws', methods=['GET', 'POST'])
# def test_websocket():
#     script = '<script type="text/javascript" src="' + url_for('static', filename='app/socket.io.min.js') + '"></script>' + """<script type="text/javascript" charset="utf-8">
#     var socket;
#     $(document).ready(function(){
#         if (location.protocol === 'http:' || document.location.protocol === 'http:'){
#             socket = io.connect("http://" + document.domain + "/wsinterview", {path: '/ws/socket.io'});
#         }
#         if (location.protocol === 'https:' || document.location.protocol === 'https:'){
#             socket = io.connect("https://" + document.domain + "/wsinterview" + location.port, {path: '/ws/socket.io'});
#         }
#         if (typeof socket !== 'undefined') {
#             socket.on('connect', function() {
#                 //console.log("Connected!");
#                 socket.emit('chat_log', {data: 1});
#             });
#             socket.on('mymessage', function(arg) {
#                 //console.log("Received " + arg.data);
#                 $("#daPushResult").html(arg.data);
#             });
#             socket.on('chatmessage', function(arg) {
#                 console.log("Received chat message " + arg.data);
#                 var newDiv = document.createElement('div');
#                 $(newDiv).html(arg.data.message);
#                 $("#daCorrespondence").append(newDiv);
#             });
#         }
#         $("#daSend").click(daSender);
#     });
# </script>"""
#     return render_template('pages/socketserver.html', extra_js=Markup(script)), 200

@app.route('/createplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_playground_package():
    form = CreatePlaygroundPackageForm(request.form)
    current_package = request.args.get('package', None)
    do_pypi = request.args.get('pypi', False)
    do_github = request.args.get('github', False)
    do_install = request.args.get('install', False)
    branch = request.args.get('branch', None)
    if branch is not None:
        branch = branch.strip()
    if branch in ('', 'None'):
        branch = None
    if app.config['USE_GITHUB']:
        github_auth = r.get('da:using_github:userid:' + str(current_user.id))
    else:
        github_auth = None
    if do_github:
        if not app.config['USE_GITHUB']:
            abort(404)
        if current_package is None:
            logmessage('create_playground_package: package not specified')
            abort(404)
        if not github_auth:
            logmessage('create_playground_package: github button called when github auth not enabled.')
            abort(404)
        github_package_name = 'docassemble-' + re.sub(r'^docassemble-', r'', current_package)
        #github_package_name = re.sub(r'[^A-Za-z\_\-]', '', github_package_name)
        if github_package_name in ('docassemble-base', 'docassemble-webapp', 'docassemble-demo'):
            abort(404)
        commit_message = request.args.get('commit_message', 'a commit')
        storage = RedisCredStorage(app='github')
        credentials = storage.get()
        if not credentials or credentials.invalid:
            state_string = random_string(16)
            session['github_next'] = json.dumps(dict(state=state_string, path='create_playground_package', arguments=request.args))
            flow = get_github_flow()
            uri = flow.step1_get_authorize_url(state=state_string)
            return redirect(uri)
        http = credentials.authorize(httplib2.Http())
        resp, content = http.request("https://api.github.com/user", "GET")
        if int(resp['status']) == 200:
            user_info = json.loads(content)
            github_user_name = user_info.get('login', None)
            github_email = user_info.get('email', None)
        else:
            raise DAError("create_playground_package: could not get information about GitHub User")
        if github_email is None:
            resp, content = http.request("https://api.github.com/user/emails", "GET")
            if int(resp['status']) == 200:
                info = json.loads(content)
                if len(info) and 'email' in info[0]:
                    github_email = info[0]['email']
        if github_user_name is None or github_email is None:
            raise DAError("create_playground_package: login and/or email not present in user info from GitHub")
        all_repositories = dict()
        repositories = get_user_repositories(http)
        for repository in repositories:
            if repository['name'] in all_repositories and repository['owner']['login'] == github_user_name:
                continue
            all_repositories[repository['name']] = repository
    area = dict()
    area['playgroundpackages'] = SavedFile(current_user.id, fix=True, section='playgroundpackages')
    file_list = dict()
    file_list['playgroundpackages'] = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    the_choices = list()
    for file_option in file_list['playgroundpackages']:
        the_choices.append((file_option, file_option))
    form.name.choices = the_choices
    if request.method == 'POST':
        if form.validate():
            current_package = form.name.data
            #flash("form validated", 'success')
        else:
            the_error = ''
            for error in form.name.errors:
                the_error += str(error)
            flash("form did not validate with " + str(form.name.data) + " " + str(the_error) + " among " + str(form.name.choices), 'error')
    if current_package is not None:
        pkgname = re.sub(r'^docassemble-', r'', current_package)
        if not user_can_edit_package(pkgname='docassemble.' + pkgname):
            flash(word('That package name is already in use by someone else.  Please change the name.'), 'error')
            current_package = None
    if current_package is not None and current_package not in file_list['playgroundpackages']:
        flash(word('Sorry, that package name does not exist in the playground'), 'error')
        current_package = None
    if current_package is not None:
        section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
        for sec in ('playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules'):
            area[sec] = SavedFile(current_user.id, fix=True, section=sec)
            file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        if os.path.isfile(os.path.join(area['playgroundpackages'].directory, current_package)):
            filename = os.path.join(area['playgroundpackages'].directory, current_package)
            info = dict()
            with open(filename, 'rU') as fp:
                content = fp.read().decode('utf8')
                info = yaml.load(content)
            for field in ('dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files'):
                if field not in info:
                    info[field] = list()
            info['dependencies'] = [x for x in info['dependencies'] if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp')]
            for package in info['dependencies']:
                logmessage("create_playground_package: considering " + str(package))
                existing_package = Package.query.filter_by(name=package, active=True).first()
                if existing_package is not None:
                    logmessage("create_playground_package: package " + str(package) + " exists")
                    if existing_package.giturl is None or existing_package.giturl == 'https://github.com/jhpyle/docassemble':
                        logmessage("create_playground_package: package " + str(package) + " exists but I will skip it; name is " + str(existing_package.name) + " and giturl is " + str(existing_package.giturl))
                        continue
                    # https://github.com/jhpyle/docassemble-helloworld
                    # git+https://github.com/fact-project/smart_fact_crawler.git@master#egg=smart_fact_crawler-0
                    #the_package_name = re.sub(r'.*/', '', existing_package.giturl)
                    #the_package_name = re.sub(r'-', '_', the_package_name)
                    #new_url = existing_package.giturl + '/archive/master.zip'
                    new_url = 'git+' + existing_package.giturl + '#egg=' + existing_package.name + '-' + existing_package.packageversion
                else:
                    logmessage("create_playground_package: package " + str(package) + " does not exist")
            info['modtime'] = os.path.getmtime(filename)
            author_info = dict()
            author_info['author name and email'] = name_of_user(current_user, include_email=True)
            author_info['author name'] = name_of_user(current_user)
            author_info['author email'] = current_user.email
            author_info['first name'] = current_user.first_name
            author_info['last name'] = current_user.last_name
            author_info['id'] = current_user.id
            if do_pypi:
                if current_user.pypi_username is None or current_user.pypi_password is None or current_user.pypi_username == '' or current_user.pypi_password == '':
                    flash("Could not publish to PyPI because username and password were not defined")
                    return redirect(url_for('playground_packages', file=current_package))
                if current_user.timezone:
                    the_timezone = current_user.timezone
                else:
                    the_timezone = get_default_timezone()
                fix_ml_files(author_info['id'])
                logmessages = docassemble.webapp.files.publish_package(pkgname, info, author_info, the_timezone)
                flash(logmessages, 'info')
                time.sleep(3.0)
                return redirect(url_for('playground_packages', file=current_package))
            if do_github:
                if github_package_name in all_repositories:
                    first_time = False
                else:
                    first_time = True
                    headers = {'Content-Type': 'application/json'}
                    the_license = 'mit' if re.search(r'MIT License', info.get('license', '')) else None
                    body = json.dumps(dict(name=github_package_name, description=info.get('description', None), homepage=info.get('url', None), license_template=the_license))
                    resp, content = http.request("https://api.github.com/user/repos", "POST", headers=headers, body=body)
                    if int(resp['status']) != 201:
                        raise DAError("create_playground_package: unable to create GitHub repository: status " + str(resp['status']) + " " + str(content))
                    all_repositories[github_package_name] = json.loads(content)
                directory = tempfile.mkdtemp()
                (private_key_file, public_key_file) = get_ssh_keys(github_email)
                os.chmod(private_key_file, stat.S_IRUSR | stat.S_IWUSR)
                os.chmod(public_key_file, stat.S_IRUSR | stat.S_IWUSR)
                ssh_script = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.sh', delete=False)
                with open(ssh_script.name, 'w') as fp:
                    fp.write('# /bin/bash\n\nssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i "' + str(private_key_file) + '" $1 $2 $3 $4 $5 $6')
                ssh_script.close()
                os.chmod(ssh_script.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR )
                #git_prefix = "GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i \"" + str(private_key_file) + "\"' "
                git_prefix = "GIT_SSH=" + ssh_script.name + " "
                ssh_url = all_repositories[github_package_name].get('ssh_url', None)
                github_url = all_repositories[github_package_name].get('html_url', None)
                if ssh_url is None:
                    raise DAError("create_playground_package: could not obtain ssh_url for package")
                output = ''
                if branch:
                    branch_option = '-b ' + str(branch) + ' '
                else:
                    branch_option = ''
                output += "Doing " + git_prefix + "git clone " + branch_option + ssh_url + "\n"
                try:
                    output += subprocess.check_output(git_prefix + "git clone " + branch_option + ssh_url, cwd=directory, stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git clone.  " + output)
                if current_user.timezone:
                    the_timezone = current_user.timezone
                else:
                    the_timezone = get_default_timezone()
                fix_ml_files(author_info['id'])
                docassemble.webapp.files.make_package_dir(pkgname, info, author_info, the_timezone, directory=directory)
                packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
                if not os.path.isdir(packagedir):
                    raise DAError("create_playground_package: package directory did not exist")
                # try:
                #     output += subprocess.check_output(["git", "init"], cwd=packagedir, stderr=subprocess.STDOUT)
                # except subprocess.CalledProcessError as err:
                #     output += err.output
                #     raise DAError("create_playground_package: error running git init.  " + output)
                output += "Doing git config user.email " + json.dumps(github_email) + "\n"
                try:
                    output += subprocess.check_output(["git", "config", "user.email", json.dumps(github_email)], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git config user.email.  " + output)
                output += "Doing git config user.name " + json.dumps(unicode(current_user.first_name) + " " + unicode(current_user.last_name)) + "\n"
                try:
                    output += subprocess.check_output(["git", "config", "user.name", json.dumps(unicode(current_user.first_name) + " " + unicode(current_user.last_name))], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git config user.email.  " + output)
                output += "Doing git add .\n"
                try:
                    output += subprocess.check_output(["git", "add", "."], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git add.  " + output)
                output += "Doing git status\n"
                try:
                    output += subprocess.check_output(["git", "status"], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git status.  " + output)
                output += "Doing git commit -m " + repr(str(commit_message)) + "\n"
                try:
                    output += subprocess.check_output(["git", "commit", "-am", str(commit_message)], cwd=packagedir, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("create_playground_package: error running git commit.  " + output)
                if False:
                    try:
                        output += subprocess.check_output(["git", "remote", "add", "origin", ssh_url], cwd=packagedir, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as err:
                        output += err.output
                        raise DAError("create_playground_package: error running git remote add origin.  " + output)
                    if branch:
                        the_branch = branch
                    else:
                        the_branch = 'master'
                    output += "Doing " + git_prefix + "git push -u origin " + the_branch + "\n"
                    try:
                        output += subprocess.check_output(git_prefix + "git push -u origin " + the_branch, cwd=packagedir, stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError as err:
                        output += err.output
                        raise DAError("create_playground_package: error running first git push.  " + output)
                else:
                    if branch:
                        output += "Doing " + git_prefix + "git push --set-upstream origin " + str(branch) + "\n"
                        try:
                            output += subprocess.check_output(git_prefix + "git push --set-upstream origin " + str(branch), cwd=packagedir, stderr=subprocess.STDOUT, shell=True)
                        except subprocess.CalledProcessError as err:
                            output += err.output
                            raise DAError("create_playground_package: error running git push.  " + output)
                    else:
                        output += "Doing " + git_prefix + "git push\n"
                        try:
                            output += subprocess.check_output(git_prefix + "git push", cwd=packagedir, stderr=subprocess.STDOUT, shell=True)
                        except subprocess.CalledProcessError as err:
                            output += err.output
                            raise DAError("create_playground_package: error running git push.  " + output)
                logmessage(output)
                flash(word("Pushed commit to GitHub.") + "  " + output, 'info')
                time.sleep(3.0)
                shutil.rmtree(directory)
                if branch:
                    return redirect(url_for('playground_packages', pull='1', github_url=ssh_url, branch=branch, show_message='0'))
                else:
                    return redirect(url_for('playground_packages', pull='1', github_url=ssh_url, show_message='0'))
                #return redirect(url_for('playground_packages', file=current_package))
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            file_set_attributes(file_number, private=False, persistent=True)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            if current_user.timezone:
                the_timezone = current_user.timezone
            else:
                the_timezone = get_default_timezone()
            fix_ml_files(author_info['id'])
            zip_file = docassemble.webapp.files.make_package_zip(pkgname, info, author_info, the_timezone)
            saved_file.copy_from(zip_file.name)
            saved_file.finalize()
            # # Why do this here?  To reserve the name?  It is all done by install_zip_package
            # # and otherwise why mess up the package listing?
            # existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).first()
            # if existing_package is None:
            #     package_auth = PackageAuth(user_id=current_user.id)
            #     package_entry = Package(name='docassemble.' + pkgname, package_auth=package_auth, upload=file_number, type='zip')
            #     db.session.add(package_auth)
            #     db.session.add(package_entry)
            #     #sys.stderr.write("Ok, did the commit\n")
            # else:
            #     existing_package.upload = file_number
            #     existing_package.active = True
            #     existing_package.version += 1
            # db.session.commit()
            if do_install:
                install_zip_package('docassemble.' + pkgname, file_number)
                result = docassemble.webapp.worker.update_packages.delay()
                session['taskwait'] = result.id
                return redirect(url_for('update_package_wait', next=url_for('playground_packages', file=current_package)))
                #return redirect(url_for('playground_packages', file=current_package))
            else:
                response = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return(response)
    return render_template('pages/create_playground_package.html', version_warning=version_warning, bodyclass='adminbody', form=form, current_package=current_package, package_names=file_list['playgroundpackages'], tab_title=word('Playground Packages'), page_title=word('Playground Packages')), 200

@app.route('/createpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def create_package():
    form = CreatePackageForm(request.form)
    if request.method == 'POST' and form.validate():
        pkgname = re.sub(r'^docassemble-', r'', form.name.data)
        if not user_can_edit_package(pkgname='docassemble.' + pkgname):
            flash(word('Sorry, that package name is already in use by someone else'), 'error')
        else:
            #foobar = Package.query.filter_by(name='docassemble_' + pkgname).first()
            #sys.stderr.write("this is it: " + str(foobar) + "\n")
            initpy = """\
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

"""
            licensetext = """\
The MIT License (MIT)

"""
            licensetext += 'Copyright (c) ' + str(datetime.datetime.now().year) + ' ' + unicode(current_user.first_name) + " " + unicode(current_user.last_name) + """

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
            readme = '# docassemble.' + str(pkgname) + "\n\nA docassemble extension.\n\n## Author\n\n" + name_of_user(current_user, include_email=True) + "\n"
            manifestin = """\
include README.md
"""
            setupcfg = """\
[metadata]
description-file = README
"""
            setuppy = """\
#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils2.util import convert_path

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info', '.git', '.gitignore')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

"""
            setuppy += "setup(name='docassemble." + str(pkgname) + "',\n" + """\
      version='0.0.1',
      description=('A docassemble extension.'),
      long_description=""" + repr(readme) + """,
      long_description_content_type='text/markdown',
      author=""" + repr(unicode(name_of_user(current_user))) + """,
      author_email=""" + repr(unicode(current_user.email)) + """,
      license='MIT',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      zip_safe = False,
      package_data=find_package_data(where='docassemble/""" + str(pkgname) + """/', package='docassemble.""" + str(pkgname) + """'),
     )

"""
            questionfiletext = """\
---
metadata:
  title: I am the title of the application
  short title: Mobile title
  description: |
    Insert description of question file here.
  authors:
    - name: """ + unicode(current_user.first_name) + " " + unicode(current_user.last_name) + """
      organization: """ + unicode(current_user.organization) + """
  revision_date: """ + formatted_current_date() + """
---
mandatory: True
code: |
  user_done
---
question: |
  % if user_doing_well:
  Good to hear it!
  % else:
  Sorry to hear that!
  % endif
sets: user_done
buttons:
  - Exit: exit
  - Restart: restart
---
question: Are you doing well today?
yesno: user_doing_well
...
"""
            templatereadme = """\
# Template directory

If you want to use non-standard document templates with pandoc,
put template files in this directory.
"""
            staticreadme = """\
# Static file directory

If you want to make files available in the web app, put them in
this directory.
"""
            sourcesreadme = """\
# Sources directory

This directory is used to store word translation files, 
machine learning training files, and other source files.
"""
            objectfile = """\
# This is a Python module in which you can write your own Python code,
# if you want to.
#
# Include this module in a docassemble interview by writing:
# ---
# modules:
#   - docassemble.""" + pkgname + """.objects
# ---
#
# Then you can do things like:
# ---
# objects:
#   - favorite_fruit: Fruit
# ---
# mandatory: True
# question: |
#   When I eat some ${ favorite_fruit.name }, 
#   I think, "${ favorite_fruit.eat() }"
# ---
# question: What is the best fruit?
# fields:
#   - Fruit Name: favorite_fruit.name
# ---
from docassemble.base.core import DAObject

class Fruit(DAObject):
    def eat(self):
        return "Yum, that " + self.name + " was good!"
"""
            directory = tempfile.mkdtemp()
            packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
            questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
            templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
            staticdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'static')
            sourcesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'sources')
            if not os.path.isdir(questionsdir):
                os.makedirs(questionsdir)
            if not os.path.isdir(templatesdir):
                os.makedirs(templatesdir)
            if not os.path.isdir(staticdir):
                os.makedirs(staticdir)
            if not os.path.isdir(sourcesdir):
                os.makedirs(sourcesdir)
            with open(os.path.join(packagedir, 'README.md'), 'w') as the_file:
                the_file.write(readme)
            with open(os.path.join(packagedir, 'LICENSE'), 'w') as the_file:
                the_file.write(licensetext)
            with open(os.path.join(packagedir, 'setup.py'), 'w') as the_file:
                the_file.write(setuppy)
            with open(os.path.join(packagedir, 'setup.cfg'), 'w') as the_file:
                the_file.write(setupcfg)
            with open(os.path.join(packagedir, 'MANIFEST.in'), 'w') as the_file:
                the_file.write(manifestin)
            with open(os.path.join(packagedir, 'docassemble', '__init__.py'), 'w') as the_file:
                the_file.write(initpy)
            with open(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), 'w') as the_file:
                the_file.write('')
            with open(os.path.join(packagedir, 'docassemble', pkgname, 'objects.py'), 'w') as the_file:
                the_file.write(objectfile)
            with open(os.path.join(templatesdir, 'README.md'), 'w') as the_file:
                the_file.write(templatereadme)
            with open(os.path.join(staticdir, 'README.md'), 'w') as the_file:
                the_file.write(staticreadme)
            with open(os.path.join(sourcesdir, 'README.md'), 'w') as the_file:
                the_file.write(sourcesreadme)
            with open(os.path.join(questionsdir, 'questions.yml'), 'w') as the_file:
                the_file.write(questionfiletext)
            nice_name = 'docassemble-' + str(pkgname) + '.zip'
            file_number = get_new_file_number(session.get('uid', None), nice_name)
            file_set_attributes(file_number, private=False, persistent=True)
            saved_file = SavedFile(file_number, extension='zip', fix=True)
            zf = zipfile.ZipFile(saved_file.path, mode='w')
            trimlength = len(directory) + 1
            if current_user.timezone:
                the_timezone = pytz.timezone(current_user.timezone)
            else:
                the_timezone = pytz.timezone(get_default_timezone())
            for root, dirs, files in os.walk(packagedir):
                for file in files:
                    thefilename = os.path.join(root, file)
                    info = zipfile.ZipInfo(thefilename[trimlength:])
                    info.date_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(thefilename)).replace(tzinfo=pytz.utc).astimezone(the_timezone).timetuple()
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0644 << 16L
                    with open(thefilename, 'rb') as fp:
                        zf.writestr(info, fp.read())
                    #zf.write(thefilename, thefilename[trimlength:])
            zf.close()
            saved_file.save()
            saved_file.finalize()
            shutil.rmtree(directory)
            # do not edit the package table just because a package is created without being installed
            # existing_package = Package.query.filter_by(name='docassemble.' + pkgname, active=True).order_by(Package.id.desc()).first()
            # if existing_package is None:
            #     package_auth = PackageAuth(user_id=current_user.id)
            #     package_entry = Package(name='docassemble.' + pkgname, package_auth=package_auth, upload=file_number, type='zip')
            #     db.session.add(package_auth)
            #     db.session.add(package_entry)
            #     #sys.stderr.write("Ok, did the commit\n")
            # else:
            #     existing_package.upload = file_number
            #     existing_package.active = True
            #     existing_package.version += 1
            # db.session.commit()
            response = send_file(saved_file.path, mimetype='application/zip', as_attachment=True, attachment_filename=nice_name)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            flash(word("Package created"), 'success')
            return response
    return render_template('pages/create_package.html', version_warning=version_warning, bodyclass='adminbody', form=form, tab_title=word('Create Package'), page_title=word('Create Package')), 200

@app.route('/restart', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def restart_page():
    script = """
    <script>
      function daRestartCallback(data){
        //console.log("Restart result: " + data.success);
      }
      function daRestart(){
        $.ajax({
          type: 'POST',
          url: """ + json.dumps(url_for('restart_ajax')) + """,
          data: 'csrf_token=""" + generate_csrf() + """&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        });
        return true;
      }
      $( document ).ready(function() {
        //console.log("restarting");
        setTimeout(daRestart, 100);
      });
    </script>"""
    next_url = request.args.get('next', url_for('interview_list'))
    extra_meta = """\n    <meta http-equiv="refresh" content="8;URL='""" + next_url + """'">"""
    return render_template('pages/restart.html', version_warning=None, bodyclass='adminbody', extra_meta=Markup(extra_meta), extra_js=Markup(script), tab_title=word('Restarting'), page_title=word('Restarting'))

def get_gd_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('googledrive', dict())
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('Google Drive is not configured.')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='https://www.googleapis.com/auth/drive',
        redirect_uri=url_for('google_drive_callback', _external=True),
        access_type='offline',
        approval_prompt='force')
    return flow

def get_gd_folder():
    key = 'da:googledrive:mapping:userid:' + str(current_user.id)
    return r.get(key)

def set_gd_folder(folder):
    key = 'da:googledrive:mapping:userid:' + str(current_user.id)
    if folder is None:
        r.delete(key)
    else:
        set_od_folder(None)
        r.set(key, folder)

def get_od_flow():
    app_credentials = current_app.config['OAUTH_CREDENTIALS'].get('onedrive', dict())
    client_id = app_credentials.get('id', None)
    client_secret = app_credentials.get('secret', None)
    if client_id is None or client_secret is None:
        raise DAError('OneDrive is not configured.')
    flow = oauth2client.client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='files.readwrite.all user.read offline_access',
        redirect_uri=url_for('onedrive_callback', _external=True),
        response_type='code',
        auth_uri='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        token_uri='https://login.microsoftonline.com/common/oauth2/v2.0/token')
    return flow

def get_od_folder():
    key = 'da:onedrive:mapping:userid:' + str(current_user.id)
    return r.get(key)

def set_od_folder(folder):
    key = 'da:onedrive:mapping:userid:' + str(current_user.id)
    if folder is None:
        r.delete(key)
    else:
        set_gd_folder(None)
        r.set(key, folder)

class RedisCredStorage(oauth2client.client.Storage):
    def __init__(self, app='googledrive'):
        self.key = 'da:' + app + ':userid:' + str(current_user.id)
        self.lockkey = 'da:' + app + ':lock:userid:' + str(current_user.id)        
    def acquire_lock(self):
        pipe = r.pipeline()
        pipe.set(self.lockkey, 1)
        pipe.expire(self.lockkey, 5)
        pipe.execute()
    def release_lock(self):
        r.delete(self.lockkey)
    def locked_get(self):
        json_creds = r.get(self.key)
        creds = None
        if json_creds is not None:
            try:
                creds = oauth2client.client.Credentials.new_from_json(json_creds)
            except:
                logmessage("RedisCredStorage: could not read credentials from " + str(json_creds))
        return creds
    def locked_put(self, credentials):
        r.set(self.key, credentials.to_json())
    def locked_delete(self):
        r.delete(self.key)

@app.route('/google_drive_callback', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def google_drive_callback():
    for key in request.args:
        logmessage("google_drive_callback: argument " + str(key) + ": " + str(request.args[key]))
    if 'code' in request.args:
        flow = get_gd_flow()
        credentials = flow.step2_exchange(request.args['code'])
        storage = RedisCredStorage(app='googledrive')
        storage.put(credentials)
        error = None
    elif 'error' in request.args:
        error = request.args['error']
    else:
        error = word("could not connect to Google Drive")
    if error:
        flash(word('There was a Google Drive error: ' + error), 'error')
        return redirect(url_for('interview_list'))
    else:
        flash(word('Connected to Google Drive'), 'success')
    return redirect(url_for('google_drive_page'))

def trash_gd_file(section, filename):
    if section == 'template':
        section = 'templates'
    the_folder = get_gd_folder()
    if the_folder is None:
        logmessage('trash_gd_file: folder not configured')
        return False
    storage = RedisCredStorage(app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('trash_gd_file: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)
    response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()
    trashed = response.get('trashed', False)
    the_mime_type = response.get('mimeType', None)
    if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
        logmessage('trash_gd_file: folder did not exist')
        return False
    subdir = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(section) + "' and '" + str(the_folder) + "' in parents").execute()
    for the_file in response.get('files', []):
        if 'id' in the_file:
            subdir = the_file['id']
            break
    if subdir is None:
        logmessage('trash_gd_file: section ' + str(section) + ' could not be found')
        return False
    id_of_filename = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType!='application/vnd.google-apps.folder' and trashed=false and name='" + str(filename) + "' and '" + str(subdir) + "' in parents").execute()
    for the_file in response.get('files', []):
        if 'id' in the_file:
            id_of_filename = the_file['id']
            break
    if id_of_filename is None:
        logmessage('trash_gd_file: file ' + str(filename) + ' could not be found in ' + str(section))
        return False
    file_metadata = { 'trashed': True }
    service.files().update(fileId=id_of_filename,
                           body=file_metadata).execute()
    logmessage('trash_gd_file: file ' + str(filename) + ' trashed from '  + str(section))
    return True

@app.route('/sync_with_google_drive', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def sync_with_google_drive():
    next = request.args.get('next', url_for('playground_page'))
    if app.config['USE_GOOGLE_DRIVE'] is False:
        flash(word("Google Drive is not configured"), "error")
        return redirect(url_for('interview_list'))
    storage = RedisCredStorage(app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        return redirect(uri)
    task = docassemble.webapp.worker.sync_with_google_drive.delay(current_user.id)
    session['taskwait'] = task.id
    return redirect(url_for('gd_sync_wait', next=next))

@app.route('/gdsyncing', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def gd_sync_wait():
    next_url = request.args.get('next', url_for('playground_page'))
    my_csrf = generate_csrf()
    script = """
    <script>
      var checkinInterval = null;
      var resultsAreIn = false;
      function daRestartCallback(data){
        //console.log("Restart result: " + data.success);
      }
      function daRestart(){
        $.ajax({
          type: 'POST',
          url: """ + json.dumps(url_for('restart_ajax')) + """,
          data: 'csrf_token=""" + my_csrf + """&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        });
        return true;
      }
      function daSyncCallback(data){
        if (data.success){
          if (data.status == 'finished'){
            resultsAreIn = true;
            if (data.ok){
              $("#notification").html(""" + json.dumps(word("The synchronization was successful.")) + """);
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-danger");
              $("#notification").addClass("alert-success");
            }
            else{
              $("#notification").html(""" + json.dumps(word("The synchronization was not successful.")) + """);
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-success");
              $("#notification").addClass("alert-danger");
            }
            $("#resultsContainer").show();
            $("#resultsArea").html(data.summary);
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
            if (data.restart){
              daRestart();
            }
          }
          else if (data.status == 'failed' && !resultsAreIn){
            resultsAreIn = true;
            $("#notification").html(""" + json.dumps(word("There was an error with the synchronization.")) + """);
            $("#notification").removeClass("alert-info");
            $("#notification").removeClass("alert-success");
            $("#notification").addClass("alert-danger");
            $("#resultsContainer").show();
            if (data.error_message){
              $("#resultsArea").html(data.error_message);
            }
            else if (data.summary){
              $("#resultsArea").html(data.summary);
            }
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
          }
        }
        else if (!resultsAreIn){
          $("#notification").html(""" + json.dumps(word("There was an error.")) + """);
          $("#notification").removeClass("alert-info");
          $("#notification").removeClass("alert-success");
          $("#notification").addClass("alert-danger");
          if (checkinInterval != null){
            clearInterval(checkinInterval);
          }
        }
      }
      function daSync(){
        if (resultsAreIn){
          return;
        }
        $.ajax({
          type: 'POST',
          url: """ + json.dumps(url_for('checkin_sync_with_google_drive')) + """,
          data: 'csrf_token=""" + my_csrf + """',
          success: daSyncCallback,
          dataType: 'json'
        });
        return true;
      }
      $( document ).ready(function() {
        //console.log("page loaded");
        checkinInterval = setInterval(daSync, 2000);
      });
    </script>"""
    return render_template('pages/gd_sync_wait.html', version_warning=None, bodyclass='adminbody', extra_js=Markup(script), tab_title=word('Synchronizing'), page_title=word('Synchronizing'), next_page=next_url)

@app.route('/onedrive_callback', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def onedrive_callback():
    for key in request.args:
        logmessage("onedrive_callback: argument " + str(key) + ": " + str(request.args[key]))
    if 'code' in request.args:
        flow = get_od_flow()
        credentials = flow.step2_exchange(request.args['code'])
        storage = RedisCredStorage(app='onedrive')
        storage.put(credentials)
        error = None
    elif 'error' in request.args:
        error = request.args['error']
    else:
        error = word("could not connect to OneDrive")
    if error:
        flash(word('There was a OneDrive error: ' + error), 'error')
        return redirect(url_for('interview_list'))
    else:
        flash(word('Connected to OneDrive'), 'success')
    return redirect(url_for('onedrive_page'))

def trash_od_file(section, filename):
    if section == 'template':
        section = 'templates'
    the_folder = get_od_folder()
    if the_folder is None:
        logmessage('trash_od_file: folder not configured')
        return False
    storage = RedisCredStorage(app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        logmessage('trash_od_file: credentials missing or expired')
        return False
    http = credentials.authorize(httplib2.Http())
    r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllib.quote(the_folder), "GET")
    if int(r['status']) != 200:
        trashed = True
    else:
        info = json.loads(content)
        #logmessage("Found " + repr(info))
        if info.get('deleted', None):
            trashed = True
        else:
            trashed = False
    if trashed is True or 'folder' not in info:
        logmessage('trash_od_file: folder did not exist')
        return False
    r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + urllib.quote(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
    subdir = None
    while True:
        if int(r['status']) != 200:
            logmessage('trash_od_file: could not obtain subfolders')
            return False
        info = json.loads(content)
        #logmessage("Found " + repr(info))
        for item in info['value']:
            if item.get('deleted', None) or 'folder' not in item:
                continue
            if item['name'] == section:
                subdir = item['id']
                break
        if subdir is not None or "@odata.nextLink" not in info:
            break
        r, content = http.request(info["@odata.nextLink"], "GET")
    if subdir is None:
        logmessage('trash_od_file: could not obtain subfolder')
        return False
    id_of_filename = None
    r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + unicode(subdir) + "/children?$select=id,name,deleted,folder", "GET")
    while True:
        if int(r['status']) != 200:
            logmessage('trash_od_file: could not obtain contents of subfolder')
            return False
        info = json.loads(content)
        #logmessage("Found " + repr(info))
        for item in info['value']:
            if item.get('deleted', None) or 'folder' in item:
                continue
            if item['name'] == filename:
                id_of_filename = item['id']
                break
        if id_of_filename is not None or "@odata.nextLink" not in info:
            break
        r, content = http.request(info["@odata.nextLink"], "GET")
    r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + unicode(id_of_filename), "DELETE")
    if int(r['status']) != 204:
        logmessage('trash_od_file: could not delete ')
        return False
    logmessage('trash_od_file: file ' + str(filename) + ' trashed from '  + str(section))
    return True

@app.route('/sync_with_onedrive', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def sync_with_onedrive():
    next = request.args.get('next', url_for('playground_page'))
    if app.config['USE_ONEDRIVE'] is False:
        flash(word("OneDrive is not configured"), "error")
        return redirect(url_for('interview_list'))
    storage = RedisCredStorage(app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        return redirect(uri)
    task = docassemble.webapp.worker.sync_with_onedrive.delay(current_user.id)
    session['taskwait'] = task.id
    return redirect(url_for('od_sync_wait', next=next))

@app.route('/odsyncing', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def od_sync_wait():
    next_url = request.args.get('next', url_for('playground_page'))
    my_csrf = generate_csrf()
    script = """
    <script>
      var checkinInterval = null;
      var resultsAreIn = false;
      function daRestartCallback(data){
        //console.log("Restart result: " + data.success);
      }
      function daRestart(){
        $.ajax({
          type: 'POST',
          url: """ + json.dumps(url_for('restart_ajax')) + """,
          data: 'csrf_token=""" + my_csrf + """&action=restart',
          success: daRestartCallback,
          dataType: 'json'
        });
        return true;
      }
      function daSyncCallback(data){
        if (data.success){
          if (data.status == 'finished'){
            resultsAreIn = true;
            if (data.ok){
              $("#notification").html(""" + json.dumps(word("The synchronization was successful.")) + """);
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-danger");
              $("#notification").addClass("alert-success");
            }
            else{
              $("#notification").html(""" + json.dumps(word("The synchronization was not successful.")) + """);
              $("#notification").removeClass("alert-info");
              $("#notification").removeClass("alert-success");
              $("#notification").addClass("alert-danger");
            }
            $("#resultsContainer").show();
            $("#resultsArea").html(data.summary);
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
            if (data.restart){
              daRestart();
            }
          }
          else if (data.status == 'failed' && !resultsAreIn){
            resultsAreIn = true;
            $("#notification").html(""" + json.dumps(word("There was an error with the synchronization.")) + """);
            $("#notification").removeClass("alert-info");
            $("#notification").removeClass("alert-success");
            $("#notification").addClass("alert-danger");
            $("#resultsContainer").show();
            if (data.error_message){
              $("#resultsArea").html(data.error_message);
            }
            else if (data.summary){
              $("#resultsArea").html(data.summary);
            }
            if (checkinInterval != null){
              clearInterval(checkinInterval);
            }
          }
        }
        else if (!resultsAreIn){
          $("#notification").html(""" + json.dumps(word("There was an error.")) + """);
          $("#notification").removeClass("alert-info");
          $("#notification").removeClass("alert-success");
          $("#notification").addClass("alert-danger");
          if (checkinInterval != null){
            clearInterval(checkinInterval);
          }
        }
      }
      function daSync(){
        if (resultsAreIn){
          return;
        }
        $.ajax({
          type: 'POST',
          url: """ + json.dumps(url_for('checkin_sync_with_onedrive')) + """,
          data: 'csrf_token=""" + my_csrf + """',
          success: daSyncCallback,
          dataType: 'json'
        });
        return true;
      }
      $( document ).ready(function() {
        //console.log("page loaded");
        checkinInterval = setInterval(daSync, 2000);
      });
    </script>"""
    return render_template('pages/od_sync_wait.html', version_warning=None, bodyclass='adminbody', extra_js=Markup(script), tab_title=word('Synchronizing'), page_title=word('Synchronizing'), next_page=next_url)

# @app.route('/old_sync_with_google_drive', methods=['GET', 'POST'])
# @login_required
# @roles_required(['admin', 'developer'])
# def old_sync_with_google_drive():
#     next = request.args.get('next', url_for('playground_page'))
#     extra_meta = """\n    <meta http-equiv="refresh" content="1; url='""" + url_for('do_sync_with_google_drive', next=next) + """'">"""
#     return render_template('pages/google_sync.html', version_warning=None, bodyclass='adminbody', extra_meta=Markup(extra_meta), tab_title=word('Synchronizing'), page_title=word('Synchronizing'))

def add_br(text):
    return re.sub(r'[\n\r]+', "<br>", text)

@app.route('/checkin_sync_with_google_drive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def checkin_sync_with_google_drive():
    if 'taskwait' not in session:
        return jsonify(success=False)
    result = docassemble.webapp.worker.workerapp.AsyncResult(id=session['taskwait'])
    if result.ready():
        if 'taskwait' in session:
            del session['taskwait']
        the_result = result.get()
        if type(the_result) is ReturnValue:
            if the_result.ok:
                logmessage("checkin_sync_with_google_drive: success")
                return jsonify(success=True, status='finished', ok=the_result.ok, summary=add_br(the_result.summary), restart=the_result.restart)
            elif hasattr(the_result, 'error'):
                logmessage("checkin_sync_with_google_drive: failed return value is " + str(the_result.error))
                return jsonify(success=True, status='failed', error_message=str(the_result.error), restart=False)
            elif hasattr(the_result, 'summary'):
                return jsonify(success=True, status='failed', summary=add_br(the_result.summary), restart=False)
            else:
                return jsonify(success=True, status='failed', error_message=str("No error message.  Result is " + str(the_result)), restart=False)
        else:
            logmessage("checkin_sync_with_google_drive: failed return value is a " + str(type(the_result)))
            logmessage("checkin_sync_with_google_drive: failed return value is " + str(the_result))
            return jsonify(success=True, status='failed', error_message=str(the_result), restart=False)
    else:
        return jsonify(success=True, status='waiting', restart=False)

@app.route('/checkin_sync_with_onedrive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def checkin_sync_with_onedrive():
    if 'taskwait' not in session:
        return jsonify(success=False)
    result = docassemble.webapp.worker.workerapp.AsyncResult(id=session['taskwait'])
    if result.ready():
        if 'taskwait' in session:
            del session['taskwait']
        the_result = result.get()
        if type(the_result) is ReturnValue:
            if the_result.ok:
                logmessage("checkin_sync_with_onedrive: success")
                return jsonify(success=True, status='finished', ok=the_result.ok, summary=add_br(the_result.summary), restart=the_result.restart)
            elif hasattr(the_result, 'error'):
                logmessage("checkin_sync_with_onedrive: failed return value is " + str(the_result.error))
                return jsonify(success=True, status='failed', error_message=str(the_result.error), restart=False)
            elif hasattr(the_result, 'summary'):
                return jsonify(success=True, status='failed', summary=add_br(the_result.summary), restart=False)
            else:
                return jsonify(success=True, status='failed', error_message=str("No error message.  Result is " + str(the_result)), restart=False)
        else:
            logmessage("checkin_sync_with_onedrive: failed return value is a " + str(type(the_result)))
            logmessage("checkin_sync_with_onedrive: failed return value is " + str(the_result))
            return jsonify(success=True, status='failed', error_message=str(the_result), restart=False)
    else:
        return jsonify(success=True, status='waiting', restart=False)

# @app.route('/do_sync_with_google_drive', methods=['GET', 'POST'])
# @login_required
# @roles_required(['admin', 'developer'])
# def do_sync_with_google_drive():
#     if app.config['USE_GOOGLE_DRIVE'] is False:
#         flash(word("Google Drive is not configured"), "error")
#         return redirect(url_for('interview_list'))
#     storage = RedisCredStorage(app='googledrive')
#     credentials = storage.get()
#     if not credentials or credentials.invalid:
#         flow = get_gd_flow()
#         uri = flow.step1_get_authorize_url()
#         return redirect(uri)
#     http = credentials.authorize(httplib2.Http())
#     service = apiclient.discovery.build('drive', 'v3', http=http)
#     the_folder = get_gd_folder()
#     response = service.files().get(fileId=the_folder, fields="mimeType, id, name, trashed").execute()
#     the_mime_type = response.get('mimeType', None)
#     trashed = response.get('trashed', False)
#     if trashed is True or the_mime_type != "application/vnd.google-apps.folder":
#         flash(word("Error accessing Google Drive"), 'error')
#         return redirect(url_for('google_drive'))
#     local_files = dict()
#     local_modtimes = dict()
#     gd_files = dict()
#     gd_ids = dict()
#     gd_modtimes = dict()
#     gd_deleted = dict()
#     sections_modified = set()
#     commentary = ''
#     for section in ('static', 'templates', 'questions', 'modules', 'sources'):
#         local_files[section] = set()
#         local_modtimes[section] = dict()
#         if section == 'questions':
#             the_section = 'playground'
#         elif section == 'templates':
#             the_section = 'playgroundtemplate'
#         else:
#             the_section = 'playground' + section
#         area = SavedFile(current_user.id, fix=True, section=the_section)
#         for f in os.listdir(area.directory):
#             local_files[section].add(f)
#             local_modtimes[section][f] = os.path.getmtime(os.path.join(area.directory, f))
#         subdirs = list()
#         page_token = None
#         while True:
#             response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + section + "' and '" + str(the_folder) + "' in parents").execute()
#             for the_file in response.get('files', []):
#                 if 'id' in the_file:
#                     subdirs.append(the_file['id'])
#             page_token = response.get('nextPageToken', None)
#             if page_token is None:
#                 break
#         if len(subdirs) == 0:
#             flash(word("Error accessing " + section + " in Google Drive"), 'error')
#             return redirect(url_for('google_drive'))
#         subdir = subdirs[0]
#         gd_files[section] = set()
#         gd_ids[section] = dict()
#         gd_modtimes[section] = dict()
#         gd_deleted[section] = set()
#         page_token = None
#         while True:
#             response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name, modifiedTime, trashed)", q="mimeType!='application/vnd.google-apps.folder' and '" + str(subdir) + "' in parents").execute()
#             for the_file in response.get('files', []):
#                 if re.search(r'(\.tmp|\.gdoc)$', the_file['name']):
#                     continue
#                 if re.search(r'^\~', the_file['name']):
#                     continue
#                 gd_ids[section][the_file['name']] = the_file['id']
#                 gd_modtimes[section][the_file['name']] = strict_rfc3339.rfc3339_to_timestamp(the_file['modifiedTime'])
#                 logmessage("Google says modtime on " + unicode(the_file) + " is " + the_file['modifiedTime'])
#                 if the_file['trashed']:
#                     gd_deleted[section].add(the_file['name'])
#                     continue
#                 gd_files[section].add(the_file['name'])
#             page_token = response.get('nextPageToken', None)
#             if page_token is None:
#                 break
#         gd_deleted[section] = gd_deleted[section] - gd_files[section]
#         for f in gd_files[section]:
#             logmessage("Considering " + f + " on GD")
#             if f not in local_files[section] or gd_modtimes[section][f] - local_modtimes[section][f] > 3:
#                 logmessage("Considering " + f + " to copy to local")
#                 sections_modified.add(section)
#                 commentary += "Copied " + f + " from Google Drive.  "
#                 the_path = os.path.join(area.directory, f)
#                 with open(the_path, 'wb') as fh:
#                     response = service.files().get_media(fileId=gd_ids[section][f])
#                     downloader = apiclient.http.MediaIoBaseDownload(fh, response)
#                     done = False
#                     while done is False:
#                         status, done = downloader.next_chunk()
#                         #logmessage("Download %d%%." % int(status.progress() * 100))
#                 os.utime(the_path, (gd_modtimes[section][f], gd_modtimes[section][f]))
#         for f in local_files[section]:
#             logmessage("Considering " + f + ", which is a local file")
#             if f not in gd_deleted[section]:
#                 logmessage("Considering " + f + " is not in Google Drive deleted")
#                 if f not in gd_files[section]:
#                     logmessage("Considering " + f + " is not in Google Drive")
#                     the_path = os.path.join(area.directory, f)
#                     if os.path.getsize(the_path) == 0:
#                         logmessage("Found zero byte file: " + the_path)
#                         continue
#                     logmessage("Copying " + f + " to Google Drive.")
#                     commentary += "Copied " + f + " to Google Drive.  "
#                     extension, mimetype = get_ext_and_mimetype(the_path)
#                     the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
#                     logmessage("Setting GD modtime on new file " + unicode(f) + " to " + unicode(the_modtime))
#                     file_metadata = { 'name': f, 'parents': [subdir], 'modifiedTime': the_modtime, 'createdTime': the_modtime }
#                     media = apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
#                     the_new_file = service.files().create(body=file_metadata,
#                                                           media_body=media,
#                                                           fields='id').execute()
#                     new_id = the_new_file.get('id')
#                 elif local_modtimes[section][f] - gd_modtimes[section][f] > 3:
#                     logmessage("Considering " + f + " is in Google Drive but local is more recent")
#                     the_path = os.path.join(area.directory, f)
#                     if os.path.getsize(the_path) == 0:
#                         logmessage("Found zero byte file during update: " + the_path)
#                         continue
#                     commentary += "Updated " + f + " on Google Drive.  "
#                     extension, mimetype = get_ext_and_mimetype(the_path)
#                     the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
#                     logmessage("Setting GD modtime on modified " + unicode(f) + " to " + unicode(the_modtime))
#                     file_metadata = { 'modifiedTime': the_modtime }
#                     media = apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
#                     service.files().update(fileId=gd_ids[section][f],
#                                            body=file_metadata,
#                                            media_body=media).execute()
#         for f in gd_deleted[section]:
#             logmessage("Considering " + f + " is deleted on Google Drive")
#             if f in local_files[section]:
#                 logmessage("Considering " + f + " is deleted on Google Drive but exists locally")
#                 if local_modtimes[section][f] - gd_modtimes[section][f] > 3:
#                     logmessage("Considering " + f + " is deleted on Google Drive but exists locally and needs to be undeleted on GD")
#                     commentary += "Undeleted and updated " + f + " on Google Drive.  "
#                     the_path = os.path.join(area.directory, f)
#                     extension, mimetype = get_ext_and_mimetype(the_path)
#                     the_modtime = strict_rfc3339.timestamp_to_rfc3339_utcoffset(local_modtimes[section][f])
#                     logmessage("Setting GD modtime on undeleted file " + unicode(f) + " to " + unicode(the_modtime))
#                     file_metadata = { 'modifiedTime': the_modtime, 'trashed': False }
#                     media = apiclient.http.MediaFileUpload(the_path, mimetype=mimetype)
#                     service.files().update(fileId=gd_ids[section][f],
#                                            body=file_metadata,
#                                            media_body=media).execute()
#                 else:
#                     logmessage("Considering " + f + " is deleted on Google Drive but exists locally and needs to deleted locally")
#                     sections_modified.add(section)
#                     commentary += "Deleted " + f + " from Playground.  "
#                     the_path = os.path.join(area.directory, f)
#                     if os.path.isfile(the_path):
#                         area.delete_file(f)
#         area.finalize()
#     for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + ':*'):
#         r.incr(key)
#     if commentary != '':
#         flash(commentary, 'info')
#         logmessage(commentary)
#     next = request.args.get('next', url_for('playground_page'))
#     if 'modules' in sections_modified:
#         return redirect(url_for('restart_page', next=next))
#     return redirect(next)
#     #return render_template('pages/testgoogledrive.html', tab_title=word('Google Drive Test'), page_title=word('Google Drive Test'), commentary=commentary)

@app.route('/google_drive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def google_drive_page():
    if app.config['USE_GOOGLE_DRIVE'] is False:
        flash(word("Google Drive is not configured"), "error")
        return redirect(url_for('interview_list'))
    form = GoogleDriveForm(request.form)
    if request.method == 'POST' and form.cancel.data:
        return redirect(url_for('user.profile'))
    storage = RedisCredStorage(app='googledrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_gd_flow()
        uri = flow.step1_get_authorize_url()
        # logmessage("google_drive_page: uri is " + str(uri))
        return redirect(uri)
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)
    items = [dict(id='', name=word('-- Do not link --'))]
    #items = []
    page_token = None
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents").execute()
        for the_file in response.get('files', []):
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    item_ids = [x['id'] for x in items if x['id'] != '']
    if request.method == 'POST' and form.submit.data:
        if form.folder.data == '':
            set_gd_folder(None)
            storage.locked_delete()
            flash(word("Google Drive is not linked."), 'success')
        elif form.folder.data == -1 or form.folder.data == '-1':
            file_metadata = {
                'name' : 'docassemble',
                'mimeType' : 'application/vnd.google-apps.folder'
            }
            new_file = service.files().create(body=file_metadata,
                                              fields='id').execute()
            new_folder = new_file.get('id', None)
            set_gd_folder(new_folder)
            gd_fix_subdirs(service, new_folder)
            if new_folder is not None:
                active_folder = dict(id=new_folder, name='docassemble')
                items.append(active_folder)
                item_ids.append(new_folder)
            flash(word("Your Playground is connected to your Google Drive."), 'success')
        elif form.folder.data in item_ids:
            flash(word("Your Playground is connected to your Google Drive."), 'success')
            set_gd_folder(form.folder.data)
            gd_fix_subdirs(service, form.folder.data)
        else:
            flash(word("The supplied folder " + unicode(form.folder.data) + "could not be found."), 'error')
            set_gd_folder(None)
        return redirect(url_for('user.profile'))
    the_folder = get_gd_folder()
    active_folder = None
    if the_folder is not None:
        try:
            response = service.files().get(fileId=the_folder, fields="mimeType, trashed").execute()
        except:
            set_gd_folder(None)
            return redirect(url_for('google_drive_page'))
        the_mime_type = response.get('mimeType', None)
        trashed = response.get('trashed', False)
        if trashed is False and the_mime_type == "application/vnd.google-apps.folder":
            active_folder = dict(id=the_folder, name=response.get('name', 'no name'))
            if the_folder not in item_ids:
                items.append(active_folder)
        else:
            set_gd_folder(None)
            the_folder = None
            flash(word("The mapping was reset because the folder does not appear to exist anymore."), 'error')
    if the_folder is None:
        for item in items:
            if (item['name'].lower() == 'docassemble'):
                active_folder = item
                break
    if active_folder is None:
        active_folder = dict(id=-1, name='docassemble')
        items.append(active_folder)
        item_ids.append(-1)
    if the_folder is not None:
        gd_fix_subdirs(service, the_folder)
    if the_folder is None:
        the_folder = ''
    description = 'Select the folder from your Google Drive that you want to be synchronized with the Playground.'
    if app.config['USE_ONEDRIVE'] is True and get_od_folder() is not None:
        description += '  ' + word('Note that if you connect to a Google Drive folder, you will disable your connection to OneDrive.')
    return render_template('pages/googledrive.html', version_warning=version_warning, description=description, bodyclass='adminbody', header=word('Google Drive'), tab_title=word('Google Drive'), items=items, the_folder=the_folder, page_title=word('Google Drive'), form=form)

def gd_fix_subdirs(service, the_folder):
    subdirs = list()
    page_token = None
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and trashed=false and '" + str(the_folder) + "' in parents").execute()
        for the_file in response.get('files', []):
            subdirs.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    todo = set(['questions', 'static', 'sources', 'templates', 'modules'])
    done = set([x['name'] for x in subdirs if x['name'] in todo])
    for key in todo - done:
        file_metadata = {
            'name' : key,
            'mimeType' : 'application/vnd.google-apps.folder',
            'parents': [the_folder]
        }
        new_file = service.files().create(body=file_metadata,
                                          fields='id').execute()

@app.route('/onedrive', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def onedrive_page():
    if app.config['USE_ONEDRIVE'] is False:
        flash(word("OneDrive is not configured"), "error")
        return redirect(url_for('user.profile'))
    form = OneDriveForm(request.form)
    if request.method == 'POST' and form.cancel.data:
        return redirect(url_for('user.profile'))
    storage = RedisCredStorage(app='onedrive')
    credentials = storage.get()
    if not credentials or credentials.invalid:
        flow = get_od_flow()
        uri = flow.step1_get_authorize_url()
        logmessage("one_drive_page: uri is " + str(uri))
        return redirect(uri)
    items = [dict(id='', name=word('-- Do not link --'))]
    http = credentials.authorize(httplib2.Http())
    r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/root/children?$select=id,name,deleted,folder", "GET")
    while True:
        if int(r['status']) != 200:
            flash("Error: could not connect to OneDrive; response code was " + unicode(r['status']) + ".   " + unicode(content), 'danger')
            return redirect(url_for('user.profile'))
        info = json.loads(content)
        for item in info['value']:
            if 'folder' not in item:
                continue
            items.append(dict(id=item['id'], name=item['name']))
        if "@odata.nextLink" not in info:
            break
        r, content = http.request(info["@odata.nextLink"], "GET")
    item_ids = [x['id'] for x in items if x['id'] != '']
    if request.method == 'POST' and form.submit.data:
        if form.folder.data == '':
            set_od_folder(None)
            storage.locked_delete()
            flash(word("OneDrive is not linked."), 'success')
        elif form.folder.data == -1 or form.folder.data == '-1':
            headers = {'Content-Type': 'application/json'}
            info = dict()
            info['name'] = 'docassemble'
            info['folder'] = dict()
            info["@microsoft.graph.conflictBehavior"] = "overwrite"
            r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/root/children", "POST", headers=headers, body=json.dumps(info))
            if int(r['status']) == 201:
                new_item = json.loads(content)
                set_od_folder(new_item['id'])
                od_fix_subdirs(http, new_item['id'])
                flash(word("Your Playground is connected to your OneDrive."), 'success')
            else:
                flash(word("Could not create folder.  " + unicode(content)), 'danger')
        elif form.folder.data in item_ids:
            set_od_folder(form.folder.data)
            od_fix_subdirs(http, form.folder.data)
            flash(word("Your Playground is connected to your OneDrive."), 'success')
        else:
            flash(word("The supplied folder " + unicode(form.folder.data) + "could not be found."), 'danger')
            set_od_folder(None)
        return redirect(url_for('user.profile'))
    the_folder = get_od_folder()
    active_folder = None
    if the_folder is not None:
        r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + unicode(the_folder), "GET")
        if int(r['status']) != 200:
            set_od_folder(None)
            flash(word("The previously selected OneDrive folder does not exist.") + "  " + unicode(the_folder) + " " + unicode(content) + " status: " + repr(r['status']), "info")
            return redirect(url_for('onedrive_page'))
        info = json.loads(content)
        logmessage("Found " + repr(info))
        if info.get('deleted', None):
            set_od_folder(None)
            flash(word("The previously selected OneDrive folder was deleted."), "info")
            return redirect(url_for('onedrive_page'))
        active_folder = dict(id=the_folder, name=info.get('name', 'no name'))
        if the_folder not in item_ids:
            items.append(active_folder)
            item_ids.append(the_folder)
    if the_folder is None:
        for item in items:
            if (item['name'].lower() == 'docassemble'):
                active_folder = item
                break
    if active_folder is None:
        active_folder = dict(id=-1, name='docassemble')
        items.append(active_folder)
        item_ids.append(-1)
    if the_folder is not None:
        od_fix_subdirs(http, the_folder)
    if the_folder is None:
        the_folder = ''
    description = word('Select the folder from your OneDrive that you want to be synchronized with the Playground.')
    if app.config['USE_GOOGLE_DRIVE'] is True and get_gd_folder() is not None:
        description += '  ' + word('Note that if you connect to a OneDrive folder, you will disable your connection to Google Drive.')
    return render_template('pages/onedrive.html', version_warning=version_warning, bodyclass='adminbody', header=word('OneDrive'), tab_title=word('OneDrive'), items=items, the_folder=the_folder, page_title=word('OneDrive'), form=form, description=Markup(description))

def od_fix_subdirs(http, the_folder):
    subdirs = set()
    r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + unicode(the_folder) + "/children?$select=id,name,deleted,folder", "GET")
    while True:
        if int(r['status']) != 200:
            raise DAError("od_fix_subdirs: could not get contents of folder")
        info = json.loads(content)
        logmessage("Found " + repr(info))
        for item in info['value']:
            if 'folder' in item:
                subdirs.add(item['name'])
        if "@odata.nextLink" not in info:
            break
        r, content = http.request(info["@odata.nextLink"], "GET")
    todo = set(['questions', 'static', 'sources', 'templates', 'modules'])
    for folder_name in (todo - subdirs):
        headers = {'Content-Type': 'application/json'}
        data = dict()
        data['name'] = folder_name
        data['folder'] = dict()
        data["@microsoft.graph.conflictBehavior"] = "rename"
        r, content = http.request("https://graph.microsoft.com/v1.0/me/drive/items/" + unicode(the_folder) + "/children", "POST", headers=headers, body=json.dumps(data))
        if int(r['status']) != 201:
            raise DAError("od_fix_subdirs: could not create subfolder " + folder_name + ' in ' + unicode(the_folder) + '.  ' + unicode(content) + ' status: ' + unicode(r['status']))

@app.route('/config', methods=['GET', 'POST'])
@login_required
@roles_required(['admin'])
def config_page():
    form = ConfigForm(request.form)
    content = None
    ok = True
    if request.method == 'POST':
        if form.submit.data and form.config_content.data:
            try:
                yaml.load(form.config_content.data)
            except Exception as errMess:
                ok = False
                content = form.config_content.data
                errMess = word("Configuration not updated.  There was a syntax error in the configuration YAML.") + '<pre>' + str(errMess) + '</pre>'
                flash(str(errMess), 'error')
                logmessage('config_page: ' + str(errMess))
            if ok:
                if cloud is not None:
                    key = cloud.get_key('config.yml')
                    key.set_contents_from_string(form.config_content.data)
                with open(daconfig['config file'], 'w') as fp:
                    fp.write(form.config_content.data.encode('utf8'))
                    flash(word('The configuration file was saved.'), 'success')
                #session['restart'] = 1
                return redirect(url_for('restart_page'))
        elif form.cancel.data:
            flash(word('Configuration not updated.'), 'info')
            return redirect(url_for('interview_list'))
        else:
            flash(word('Configuration not updated.  There was an error.'), 'error')
            return redirect(url_for('interview_list'))
    if ok:
        with open(daconfig['config file'], 'rU') as fp:
            content = fp.read().decode('utf8')
    if content is None:
        abort(404)
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    python_version = daconfig.get('python version', word('Unknown'))
    system_version = daconfig.get('system version', word('Unknown'))
    if python_version == system_version:
        version = word("Version ") + unicode(python_version)
    else:
        version = word("Version ") + unicode(python_version) + ' (Python); ' + unicode(system_version) + ' (' + word('system') + ')'
    return render_template('pages/config.html', version_warning=version_warning, version=version, bodyclass='adminbody', tab_title=word('Configuration'), page_title=word('Configuration'), extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    ' + kbLoad + '<script>\n      daTextArea=document.getElementById("config_content");\n      daTextArea.value = JSON.parse(atob("' + safeid(json.dumps(content)) + '"));\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "yaml", ' + kbOpt + 'tabSize: 2, tabindex: 70, autofocus: true, lineNumbers: true, matchBrackets: true});\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});\n      daCodeMirror.setOption("coverGutterNextToScrollbar", true);\n    </script>'), form=form), 200

@app.route('/view_source', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def view_source():
    source_path = request.args.get('i', None)
    if source_path is None:
        logmessage("view_source: no source path")
        abort(404)
    try:
        if re.search(r':', source_path):
            source = docassemble.base.parse.interview_source_from_string(source_path)
        else:
            try:
                source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + source_path)
            except:
                source = docassemble.base.parse.interview_source_from_string(source_path)
    except Exception as errmess:
        logmessage("view_source: no source: " + str(errmess))
        abort(404)
    header = source_path
    return render_template('pages/view_source.html', version_warning=None, bodyclass='adminbody', tab_title="Source", page_title="Source", extra_css=Markup('\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), header=header, contents=Markup(highlight(source.content, YamlLexer(), HtmlFormatter(cssclass="highlight fullheight")))), 200

@app.route('/playgroundstatic/<userid>/<filename>', methods=['GET'])
def playground_static(userid, filename):
    #filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundstatic')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        return(response)
    abort(404)

@app.route('/playgroundmodules/<userid>/<filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_modules(userid, filename):
    #filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundmodules')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        return(response)
    abort(404)

@app.route('/playgroundsources/<userid>/<filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_sources(userid, filename):
    filename = re.sub(r'[^A-Za-z0-9\-\_\(\)\. ]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundsources')
    reslt = write_ml_source(area, userid, filename)
    # if reslt:
    #     logmessage("playground_sources: was True")
    # else:
    #     logmessage("playground_sources: was False")
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/playgroundtemplate/<userid>/<filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_template(userid, filename):
    #filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    area = SavedFile(userid, fix=True, section='playgroundtemplate')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/playgrounddownload/<userid>/<filename>', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def playground_download(userid, filename):
    #filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
    area = SavedFile(userid, fix=True, section='playground')
    filename = os.path.join(area.directory, filename)
    if os.path.isfile(filename):
        extension, mimetype = get_ext_and_mimetype(filename)
        response = send_file(filename, mimetype=str(mimetype))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return(response)
    abort(404)

@app.route('/officefunctionfile', methods=['GET', 'POST'])
def playground_office_functionfile():
    return render_template('pages/officefunctionfile.html', page_title=word("Docassemble Playground"), tab_title=word("Playground"), parent_origin=daconfig.get('office addin url', daconfig.get('url root', request.base_url))), 200

@app.route('/officetaskpane', methods=['GET', 'POST'])
def playground_office_taskpane():
    defaultDaServer = daconfig.get('url root', None)
    if defaultDaServer is None:
        defaultDaServer = request.url_root
    return render_template('pages/officeouter.html', page_title=word("Docassemble Playground"), tab_title=word("Playground"), defaultDaServer=defaultDaServer, extra_js=Markup("\n        <script>" + indent_by(variables_js(office_mode=True), 9) + "        </script>")), 200

@app.route('/officeaddin', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_office_addin():
    if request.args.get('fetchfiles', None):
        playground = SavedFile(current_user.id, fix=True, section='playground')
        files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        return jsonify(success=True, files=files)
    pg_var_file = request.args.get('pgvars', None)
    #logmessage("playground_office_addin: YAML file is " + unicode(pg_var_file))
    use_html = request.args.get('html', False)
    uploadform = AddinUploadForm(request.form)
    if request.method == 'POST':
        area = SavedFile(current_user.id, fix=True, section='playgroundtemplate')
        filename = secure_filename(uploadform.filename.data)
        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', filename)
        if filename == '':
            return jsonify({'success': False})
        content = unicode(uploadform.content.data)
        start_index = 0
        char_index = 0
        for char in content:
            char_index += 1
            if char == ',':
                start_index = char_index
                break
        area.write_content(codecs.decode(content[start_index:], 'base64'), filename=filename)
        area.finalize()
        if use_html:
            if pg_var_file is None:
                pg_var_file = ''
        else:
            if pg_var_file is None or pg_var_file == '':
                return jsonify({'success': True, 'variables_json': [], 'vocab_list': []})
    if pg_var_file is not None:
        playground = SavedFile(current_user.id, fix=True, section='playground')
        files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
        if pg_var_file in files:
            #logmessage("playground_office_addin: file " + unicode(pg_var_file) + " was found")
            interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + pg_var_file)
            interview_source.set_testing(True)
        else:
            #logmessage("playground_office_addin: file " + unicode(pg_var_file) + " was not found")
            if pg_var_file == '':
                pg_var_file = 'test.yml'
            content = "modules:\n  - docassemble.base.util\n---\nmandatory: True\nquestion: hi"
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, package="docassemble.playground" + str(current_user.id), path="docassemble.playground" + str(current_user.id) + ":" + pg_var_file, testing=True)
        interview = interview_source.get_interview()
        ensure_ml_file_exists(interview, pg_var_file)
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + pg_var_file, req=request, action=None))
        if use_html:
            variables_html, vocab_list, vocab_dict = get_vars_in_use(interview, interview_status, debug_mode=False, show_messages=False, show_jinja_help=True)
            return jsonify({'success': True, 'variables_html': variables_html, 'vocab_list': list(vocab_list), 'vocab_dict': vocab_dict})
        else:
            variables_json, vocab_list = get_vars_in_use(interview, interview_status, debug_mode=False, return_json=True)
            return jsonify({'success': True, 'variables_json': variables_json, 'vocab_list': list(vocab_list)})
    parent_origin = re.sub(r'^(https?://[^/]+)/.*', r'\1', daconfig.get('office addin url', daconfig.get('url root', request.base_url)))
    return render_template('pages/officeaddin.html', page_title=word("Docassemble Office Add-in"), tab_title=word("Office Add-in"), parent_origin=parent_origin, form=uploadform), 200

@app.route('/playgroundfiles', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_files():
    if app.config['USE_ONEDRIVE'] is False or get_od_folder() is None:
        use_od = False
    else:
        use_od = True
    if app.config['USE_GOOGLE_DRIVE'] is False or get_gd_folder() is None:
        use_gd = False
    else:
        use_gd = True
        use_od = False
    form = PlaygroundFilesForm(request.form)
    formtwo = PlaygroundFilesEditForm(request.form)
    if 'ajax' in request.form and int(request.form['ajax']):
        is_ajax = True
    else:
        is_ajax = False
    section = request.args.get('section', 'template')
    the_file = request.args.get('file', '')
    scroll = False
    if the_file:
        scroll = True
    if request.method == 'GET':
        is_new = request.args.get('new', False)
    else:
        is_new = False
    if is_new:
        scroll = True
        the_file = ''
    if request.method == 'POST':
        if (form.section.data):
            section = form.section.data
        if (formtwo.file_name.data):
            the_file = formtwo.file_name.data
            the_file = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', the_file)
    if section not in ("template", "static", "sources", "modules", "packages"):
        section = "template"
    pgarea = SavedFile(current_user.id, fix=True, section='playground')
    pulldown_files = sorted([f for f in os.listdir(pgarea.directory) if os.path.isfile(os.path.join(pgarea.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    if 'variablefile' in session:
        if session['variablefile'] in pulldown_files:
            active_file = session['variablefile']
        else:
            del session['variablefile']
            active_file = None
    else:
        active_file = None
    if active_file is None:
        if 'playgroundfile' in session and session['playgroundfile'] in pulldown_files:
            active_file = session['playgroundfile']
        elif len(pulldown_files):
            active_file = pulldown_files[0]
    area = SavedFile(current_user.id, fix=True, section='playground' + section)
    if request.args.get('delete', False):
        #argument = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', request.args.get('delete'))
        argument = request.args.get('delete')
        if argument:
            filename = os.path.join(area.directory, argument)
            if os.path.exists(filename):
                os.remove(filename)
                area.finalize()
                for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + ':*'):
                    r.incr(key)
                if use_gd:
                    try:
                        trash_gd_file(section, argument)
                    except Exception as the_err:
                        logmessage("playground_files: unable to delete file on Google Drive.  " + str(the_err))
                elif use_od:
                    try:
                        trash_od_file(section, argument)
                    except Exception as the_err:
                        logmessage("playground_files: unable to delete file on OneDrive.  " + str(the_err))
                flash(word("Deleted file: ") + argument, "success")
                for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + ':*'):
                    r.incr(key)
                return redirect(url_for('playground_files', section=section))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.args.get('convert', False):
        #argument = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', request.args.get('convert'))
        argument = request.args.get('convert')
        if argument:
            filename = os.path.join(area.directory, argument)
            if os.path.exists(filename):
                to_file = os.path.splitext(argument)[0] + '.md'
                to_path = os.path.join(area.directory, to_file)
                if not os.path.exists(to_path):
                    extension, mimetype = get_ext_and_mimetype(argument)
                    if (mimetype and mimetype in convertible_mimetypes):
                        the_format = convertible_mimetypes[mimetype]
                    elif extension and extension in convertible_extensions:
                        the_format = convertible_extensions[extension]
                    else:
                        flash(word("File format not understood: ") + argument, "error")
                        return redirect(url_for('playground_files', section=section))
                    result = word_to_markdown(filename, the_format)
                    if result is None:
                        flash(word("File could not be converted: ") + argument, "error")
                        return redirect(url_for('playground_files', section=section))
                    shutil.copyfile(result.name, to_path)
                    flash(word("Created new Markdown file called ") + to_file + word("."), "success")
                    area.finalize()
                    return redirect(url_for('playground_files', section=section, file=to_file))
            else:
                flash(word("File not found: ") + argument, "error")
    if request.method == 'POST':
        if 'uploadfile' in request.files:
            the_files = request.files.getlist('uploadfile')
            if the_files:
                for up_file in the_files:
                    try:
                        filename = secure_filename(up_file.filename)
                        filename = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', filename)
                        the_file = filename
                        filename = os.path.join(area.directory, filename)
                        up_file.save(filename)
                        for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + ':*'):
                            r.incr(key)
                        area.finalize()
                        if section == 'modules':
                            return redirect(url_for('restart_page', next=url_for('playground_files', section=section, file=the_file)))
                    except Exception as errMess:
                        flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
                flash(word("Upload successful"), "success")
        if formtwo.delete.data:
            if the_file != '':
                filename = os.path.join(area.directory, the_file)
                if os.path.exists(filename):
                    os.remove(filename)
                    for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + ':*'):
                        r.incr(key)
                    area.finalize()
                    flash(word("Deleted file: ") + the_file, "success")
                    return redirect(url_for('playground_files', section=section))
                else:
                    flash(word("File not found: ") + the_file, "error")            
        if formtwo.submit.data and formtwo.file_content.data:
            if the_file != '':
                if formtwo.original_file_name.data and formtwo.original_file_name.data != the_file:
                    old_filename = os.path.join(area.directory, formtwo.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                filename = os.path.join(area.directory, the_file)
                with open(filename, 'w') as fp:
                    fp.write(re.sub(r'\r\n', r'\n', formtwo.file_content.data).encode('utf8'))
                the_time = formatted_current_time()
                for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + ':*'):
                    r.incr(key)
                area.finalize()
                if formtwo.active_file.data and formtwo.active_file.data != the_file:
                    #interview_file = os.path.join(pgarea.directory, formtwo.active_file.data)
                    r.incr('da:interviewsource:docassemble.playground' + str(current_user.id) + ':' + formtwo.active_file.data)
                    #if os.path.isfile(interview_file):
                    #    with open(interview_file, 'a'):
                    #        os.utime(interview_file, None)
                    #    pgarea.finalize()
                flash_message = flash_as_html(str(the_file) + ' ' + word('was saved at') + ' ' + the_time + '.', message_type='success', is_ajax=is_ajax)
                if section == 'modules':
                    #restart_all()
                    return redirect(url_for('restart_page', next=url_for('playground_files', section=section, file=the_file)))
                if is_ajax:
                    return jsonify(success=True, flash_message=flash_message)
                else:
                    return redirect(url_for('playground_files', section=section, file=the_file))
            else:
                flash(word('You need to type in a name for the file'), 'error')                
    files = sorted([f for f in os.listdir(area.directory) if os.path.isfile(os.path.join(area.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])

    editable_files = list()
    convertible_files = list()
    trainable_files = dict()
    mode = "yaml"
    for a_file in files:
        extension, mimetype = get_ext_and_mimetype(a_file)
        if (mimetype and mimetype in ok_mimetypes) or (extension and extension in ok_extensions) or (mimetype and mimetype.startswith('text')):
            if section == 'sources' and re.match(r'ml-.*\.json', a_file):
                trainable_files[a_file] = re.sub(r'^ml-|\.json$', '', a_file)
            else:
                editable_files.append(dict(name=a_file, modtime=os.path.getmtime(os.path.join(area.directory, a_file))))
    assign_opacity(editable_files)
    editable_file_listing = [x['name'] for x in editable_files]
    for a_file in files:
        extension, mimetype = get_ext_and_mimetype(a_file)
        b_file = os.path.splitext(a_file)[0] + '.md'
        if b_file not in editable_file_listing and ((mimetype and mimetype in convertible_mimetypes) or (extension and extension in convertible_extensions)):
            convertible_files.append(a_file)
    if the_file and not is_new and the_file not in editable_file_listing:
        the_file = ''
    if not the_file and not is_new:
        if 'playground' + section in session and session['playground' + section] in editable_file_listing:
            the_file = session['playground' + section]
        else:
            if 'playground' + section in session:
                del session['playground' + section]
            if len(editable_files):
                the_file = sorted(editable_files, key=lambda x: x['modtime'])[-1]['name']
            else:
                if section == 'modules':
                    the_file = 'test.py'
                elif section == 'sources':
                    the_file = 'test.json'
                else:
                    the_file = 'test.md'
    if the_file in editable_file_listing:
        session['playground' + section] = the_file
    if the_file != '':
        extension, mimetype = get_ext_and_mimetype(the_file)
        if (mimetype and mimetype in ok_mimetypes):
            mode = ok_mimetypes[mimetype]
        elif (extension and extension in ok_extensions):
            mode = ok_extensions[extension]
        elif (mimetype and mimetype.startswith('text')):
            mode = 'null'
    if mode != 'markdown':
        active_file = None
    formtwo.original_file_name.data = the_file
    formtwo.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(area.directory, the_file)):
        filename = os.path.join(area.directory, the_file)
    else:
        filename = None
    if filename is not None:
        area.finalize()
        with open(filename, 'rU') as fp:
            content = fp.read().decode('utf8')
    elif formtwo.file_content.data:
        content = re.sub(r'\r\n', r'\n', formtwo.file_content.data)
    else:
        content = ''
    lowerdescription = None
    description = None
    if (section == "template"):
        header = word("Templates")
        description = 'Add files here that you want want to include in your interviews using <a target="_blank" href="https://docassemble.org/docs/documents.html#docx template file"><code>docx template file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#pdf template file"><code>pdf template file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#content file"><code>content file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#initial yaml"><code>initial yaml</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#additional yaml"><code>additional yaml</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#template file"><code>template file</code></a>, <a target="_blank" href="https://docassemble.org/docs/documents.html#rtf template file"><code>rtf template file</code></a>, or <a target="_blank" href="https://docassemble.org/docs/documents.html#docx reference file"><code>docx reference file</code></a>.'
        upload_header = word("Upload a template file")
        list_header = word("Existing template files")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "static"):
        header = word("Static Files")
        description = 'Add files here that you want to include in your interviews with <a target="_blank" href="https://docassemble.org/docs/initial.html#images"><code>images</code></a>, <a target="_blank" href="https://docassemble.org/docs/initial.html#image sets"><code>image sets</code></a>, <a target="_blank" href="https://docassemble.org/docs/markup.html#inserting%20images"><code>[FILE]</code></a> or <a target="_blank" href="https://docassemble.org/docs/functions.html#url_of"><code>url_of()</code></a>.'
        upload_header = word("Upload a static file")
        list_header = word("Existing static files")
        edit_header = word('Edit text files')
        after_text = None
    elif (section == "sources"):
        header = word("Source Files")
        description = 'Add files here that you want to make available to your interview code, such as word translation files and training data for machine learning.'
        upload_header = word("Upload a source file")
        list_header = word("Existing source files")
        edit_header = word('Edit source files')
        after_text = None
    elif (section == "modules"):
        header = word("Modules")
        upload_header = word("Upload a Python module")
        list_header = word("Existing module files")
        edit_header = word('Edit module files')
        description = 'You can use this page to add Python module files (.py files) that you want to include in your interviews using <a target="_blank" href="https://docassemble.org/docs/initial.html#modules"><code>modules</code></a> or <a target="_blank" href="https://docassemble.org/docs/initial.html#imports"><code>imports</code></a>.'
        lowerdescription = Markup("""<p>To use this in an interview, write a <a target="_blank" href="https://docassemble.org/docs/initial.html#modules"><code>modules</code></a> block that refers to this module using Python's syntax for specifying a "relative import" of a module (i.e., prefix the module name with a period).</p>""" + highlight('---\nmodules:\n  - .' + re.sub(r'\.py$', '', the_file) + '\n---', YamlLexer(), HtmlFormatter()))
        after_text = None
    if scroll:
        extra_command = """
        if ($("#file_name").val().length > 0){
          daCodeMirror.focus();
        }
        else{
          $("#file_name").focus()
        }
        scrollBottom();"""
    else:
        extra_command = ""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    extra_js = """
    <script>
      var daCodeMirror;
      var daTextArea;
      var vocab = [];
      var currentFile = """ + json.dumps(the_file) + """;
      var daIsNew = """ + ('true' if is_new else 'false') + """;
      var existingFiles = """ + json.dumps(files) + """;
      var daSection = """ + '"' + section + '";' + """
      var attrs_showing = Object();
""" + indent_by(variables_js(form='formtwo'), 6) + """
""" + indent_by(search_js(form='formtwo'), 6) + """
      function saveCallback(data){
        fetchVars(true);
        if ($("#flash").length){
          $("#flash").html(data.flash_message);
        }
        else{
          $("#main").prepend('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">' + data.flash_message + '</div>');
        }
      }
      function scrollBottom(){
        $("html, body").animate({
          scrollTop: $("#editnav").offset().top - 53
        }, "slow");
      }
      $( document ).ready(function() {
        $("#file_name").on('change', function(){
          var newFileName = $(this).val();
          if ((!daIsNew) && newFileName == currentFile){
            return;
          }
          for (var i = 0; i < existingFiles.length; i++){
            if (newFileName == existingFiles[i]){
              alert(""" + json.dumps(word("Warning: a file by that name already exists.  If you save, you will overwrite it.")) + """);
              return;
            }
          }
          return;
        });
        $("#uploadbutton").click(function(event){
          if ($("#uploadfile").val() == ""){
            event.preventDefault();
            return false;
          }
        });
        daTextArea = document.getElementById("file_content");
        daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: """ + ('{name: "markdown", underscoresBreakWords: false}' if mode == 'markdown' else json.dumps(mode)) + """, """ + kbOpt + """tabSize: 2, tabindex: 580, autofocus: false, lineNumbers: true, matchBrackets: true});
        $(window).bind("beforeunload", function(){
          daCodeMirror.save();
          $("#formtwo").trigger("checkform.areYouSure");
        });
        $("#daDelete").click(function(event){
          if (!confirm(""" + json.dumps(word("Are you sure that you want to delete this file?")) + """)){
            event.preventDefault();
          }
        });
        $("#formtwo").areYouSure(""" + json.dumps(json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")})) + """);
        $("#formtwo").bind("submit", function(e){
          daCodeMirror.save();
          $("#formtwo").trigger("reinitialize.areYouSure");
          if (daSection != 'modules' && !daIsNew){
            var extraVariable = ''
            if ($("#daVariables").length){
              extraVariable = '&active_file=' + encodeURIComponent($("#daVariables").val());
            }
            $.ajax({
              type: "POST",
              url: """ + '"' + url_for('playground_files') + '"' + """,
              data: $("#formtwo").serialize() + extraVariable + '&submit=Save&ajax=1',
              success: function(data){
                saveCallback(data);
                setTimeout(function(){
                  $("#flash .alert-success").hide(300, function(){
                    $(self).remove();
                  });
                }, 3000);
              },
              dataType: 'json'
            });
            e.preventDefault();
            return false;
          }
          return true;
        });
        daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});
        daCodeMirror.setOption("coverGutterNextToScrollbar", true);
        searchReady();
        variablesReady();
        fetchVars(false);""" + extra_command + """
      });
      searchReady();
      $('#uploadfile').on('change', function(){
        var fileName = $(this).val();
        fileName = fileName.replace(/.*\\\\/, '');
        fileName = fileName.replace(/.*\\//, '');
        $(this).next('.custom-file-label').html(fileName);
      });
    </script>"""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    if len(editable_files):
        any_files = True
    else:
        any_files = False
    #back_button = Markup('<a href="' + url_for('playground_page') + '" class="btn btn-sm navbar-btn nav-but"><i class="fas fa-arrow-left"></i> ' + word("Back") + '</a>')
    back_button = Markup('<span class="navbar-brand"><a href="' + url_for('playground_page') + '" class="playground-back text-muted backbuttoncolor" type="submit" title=' + json.dumps(word("Go back to the main Playground page")) + '><i class="fas fa-chevron-left"></i><span class="daback">' + word('Back') + '</span></a></span>')
    cm_mode = ''
    if mode == 'null':
        modes = []
    elif mode == 'htmlmixed':
        modes = ['css', 'xml', 'htmlmixed']
    else:
        modes = [mode]
    for the_mode in modes:
        cm_mode += '\n    <script src="' + url_for('static', filename="codemirror/mode/" + the_mode + "/" + ('damarkdown' if the_mode == 'markdown' else the_mode) + ".js") + '"></script>'
    return render_template('pages/playgroundfiles.html', version_warning=None, bodyclass='adminbody', use_gd=use_gd, use_od=use_od, back_button=back_button, tab_title=header, page_title=header, extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    ' + kbLoad + '<script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>' + cm_mode + extra_js), header=header, upload_header=upload_header, list_header=list_header, edit_header=edit_header, description=Markup(description), lowerdescription=lowerdescription, form=form, files=files, section=section, userid=current_user.id, editable_files=editable_files, editable_file_listing=editable_file_listing, trainable_files=trainable_files, convertible_files=convertible_files, formtwo=formtwo, current_file=the_file, content=content, after_text=after_text, is_new=str(is_new), any_files=any_files, pulldown_files=pulldown_files, active_file=active_file, playground_package='docassemble.playground' + str(current_user.id)), 200

@app.route('/pullplaygroundpackage', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def pull_playground_package():
    form = PullPlaygroundPackage(request.form)
    if request.method == 'POST':
        if form.pull.data:
            if form.github_url.data and form.pypi.data:
                flash(word("You cannot pull from GitHub and PyPI at the same time.  Please fill in one and leave the other blank."), 'error')
            elif form.github_url.data:
                return redirect(url_for('playground_packages', pull='1', github_url=form.github_url.data, branch=form.github_branch.data))
            elif form.pypi.data:
                return redirect(url_for('playground_packages', pull='1', pypi=form.pypi.data))
        if form.cancel.data:
            return redirect(url_for('playground_packages'))
    elif 'github' in request.args:
        form.github_url.data = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['github'])
    elif 'pypi' in request.args:
        form.pypi.data = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['pypi'])
    form.github_branch.choices = list()
    description = word("Enter a URL of a GitHub repository containing an extension package.  When you press Pull, the contents of that repository will be copied into the Playground, overwriting any files with the same names.")
    branch = request.args.get('branch')
    extra_js = """
    <script>
      var default_branch = """ + json.dumps(branch if branch else 'master') + """;
      function get_branches(){
        var elem = $("#github_branch");
        elem.empty();
        var opt = $("<option></option>");
        opt.attr("value", "").text("Not applicable");
        elem.append(opt);
        var github_url = $("#github_url").val();
        if (!github_url){
          return;
        }
        $.get(""" + json.dumps(url_for('get_git_branches')) + """, { url: github_url }, "json")
        .done(function(data){
          //console.log(data);
          if (data.success){
            var n = data.result.length;
            if (n > 0){
              elem.empty();
              for (var i = 0; i < n; i++){
                opt = $("<option></option>");
                opt.attr("value", data.result[i].name).text(data.result[i].name);
                if (data.result[i].name == default_branch){
                  opt.prop('selected', true);
                }
                $(elem).append(opt);
              }
            }
          }
        });
      }
      $( document ).ready(function() {
        get_branches();
        $("#github_url").on('change', get_branches);
      });
    </script>
"""
    return render_template('pages/pull_playground_package.html', form=form, description=description, version_warning=version_warning, bodyclass='adminbody', title=word("Pull GitHub or PyPI Package"), tab_title=word("Pull"), page_title=word("Pull"), extra_js=Markup(extra_js)), 200

@app.route('/get_git_branches', methods=['GET'])
@login_required
@roles_required(['developer', 'admin'])
def get_git_branches():
    if 'url' not in request.args:
        abort(404)
    if app.config['USE_GITHUB']:
        github_auth = r.get('da:using_github:userid:' + str(current_user.id))
    else:
        github_auth = None
    repo_name = request.args['url']
    m = re.search(r'//(.+):x-oauth-basic@github.com', repo_name)
    if m:
        access_token_part = '?access_token=' + m.group(1)
    else:
        access_token_part = ''
    repo_name = re.sub(r'^http.*github.com/', '', repo_name)
    repo_name = re.sub(r'.*@github.com:', '', repo_name)
    repo_name = re.sub(r'.git$', '', repo_name)
    try:
        if github_auth and access_token_part == '':
            storage = RedisCredStorage(app='github')
            credentials = storage.get()
            if not credentials or credentials.invalid:
                return jsonify(dict(success=False, reason="bad credentials"))
            http = credentials.authorize(httplib2.Http())
        else:
            http = httplib2.Http()
        the_url = "https://api.github.com/repos/" + repo_name + '/branches' + access_token_part
        branches = list()
        resp, content = http.request(the_url, "GET")
        if int(resp['status']) == 200:
            branches.extend(json.loads(content))
            while True:
                next_link = get_next_link(resp)
                if next_link:
                    resp, content = http.request(next_link, "GET")
                    if int(resp['status']) != 200:
                        return jsonify(dict(success=False, reason=repo_name + " fetch failed"))
                    else:
                        branches.extend(json.loads(content))
                else:
                    break
            return jsonify(dict(success=True, result=branches))
        return jsonify(dict(success=False, reason=the_url + " fetch failed on first try; got " + str(resp['status'])))
    except Exception as err:
        return jsonify(dict(success=False, reason=str(err)))
    return jsonify(dict(success=False))

def get_user_repositories(http):
    repositories = list()
    resp, content = http.request("https://api.github.com/user/repos", "GET")
    if int(resp['status']) == 200:
        repositories.extend(json.loads(content))
        while True:
            next_link = get_next_link(resp)
            if next_link:
                resp, content = http.request(next_link, "GET")
                if int(resp['status']) != 200:
                    raise DAError("get_user_repositories: could not get information from next URL")
                else:
                    repositories.extend(json.loads(content))
            else:
                break
    else:
        raise DAError("playground_packages: could not get information about repositories")
    return repositories

def get_orgs_info(http):
    orgs_info = list()
    resp, content = http.request("https://api.github.com/user/orgs", "GET")
    if int(resp['status']) == 200:
        orgs_info.extend(json.loads(content))
        while True:
            next_link = get_next_link(resp)
            if next_link:
                resp, content = http.request(next_link, "GET")
                if int(resp['status']) != 200:
                    raise DAError("get_orgs_info: could not get additional information about organizations")
                else:
                    orgs_info.extend(json.loads(content))
            else:
                break
    else:
        raise DAError("get_orgs_info: failed to get orgs using https://api.github.com/user/orgs")
    return orgs_info

def get_branch_info(http, full_name):
    branch_info = list()
    resp, content = http.request("https://api.github.com/repos/" + str(full_name) + '/branches', "GET")
    if int(resp['status']) == 200:
        branch_info.extend(json.loads(content))
        while True:
            next_link = get_next_link(resp)
            if next_link:
                resp, content = http.request(next_link, "GET")
                if int(resp['status']) != 200:
                    raise DAError("get_branch_info: could not get additional information from next URL")
                else:
                    branch_info.extend(json.loads(content))
            else:
                break
    else:
        logmessage("get_branch_info: could not get info from https://api.github.com/repos/" + str(full_name) + '/branches')
    return branch_info

@app.route('/playgroundpackages', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_packages():
    form = PlaygroundPackagesForm(request.form)
    fileform = PlaygroundUploadForm(request.form)
    the_file = request.args.get('file', '')
    if the_file == '':
        no_file_specified = True
    else:
        no_file_specified = False
    scroll = False
    allow_pypi = daconfig.get('pypi', False)
    pypi_username = current_user.pypi_username
    pypi_password = current_user.pypi_password
    pypi_url = daconfig.get('pypi url', 'https://pypi.python.org/pypi')
    if allow_pypi is True and pypi_username is not None and pypi_password is not None and pypi_username != '' and pypi_password != '':
        can_publish_to_pypi = True
    else:
        can_publish_to_pypi = False
    if app.config['USE_GITHUB']:
        can_publish_to_github = r.get('da:using_github:userid:' + str(current_user.id))
    else:
        can_publish_to_github = None
    show_message = true_or_false(request.args.get('show_message', True))
    github_message = None
    pypi_message = None
    pypi_version = None        
    package_list, package_auth = get_package_info()
    package_names = sorted([package.package.name for package in package_list])
    for default_package in ('docassemble', 'docassemble.base', 'docassemble.webapp'):
        if default_package in package_names:
            package_names.remove(default_package)
    # if the_file:
    #     scroll = True
    if request.method == 'GET':
        is_new = request.args.get('new', False)
    else:
        is_new = False
    if is_new:
        # scroll = True
        the_file = ''
    area = dict()
    file_list = dict()
    section_name = {'playground': 'Interview files', 'playgroundpackages': 'Packages', 'playgroundtemplate': 'Template files', 'playgroundstatic': 'Static files', 'playgroundsources': 'Source files', 'playgroundmodules': 'Modules'}
    section_sec = {'playgroundtemplate': 'template', 'playgroundstatic': 'static', 'playgroundsources': 'sources', 'playgroundmodules': 'modules'}
    section_field = {'playground': form.interview_files, 'playgroundtemplate': form.template_files, 'playgroundstatic': form.static_files, 'playgroundsources': form.sources_files, 'playgroundmodules': form.module_files}
    for sec in ('playground', 'playgroundpackages', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules'):
        area[sec] = SavedFile(current_user.id, fix=True, section=sec)
        file_list[sec] = sorted([f for f in os.listdir(area[sec].directory) if os.path.isfile(os.path.join(area[sec].directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    for sec, field in section_field.iteritems():
        the_list = []
        for item in file_list[sec]:
            the_list.append((item, item))
        field.choices = the_list
    the_list = []
    for item in package_names:
        the_list.append((item, item))
    form.dependencies.choices = the_list
    validated = False
    form.github_branch.choices = list()
    if form.github_branch.data:
        form.github_branch.choices.append((form.github_branch.data, form.github_branch.data))
    else:
        form.github_branch.choices.append(('', ''))
    if request.method == 'POST' and 'uploadfile' not in request.files:
        if form.validate():
            the_file = form.file_name.data
            validated = True
        else:
            the_error = ''
            for attrib in ('original_file_name', 'file_name', 'license', 'description', 'author_name', 'author_email', 'version', 'url', 'dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files', 'readme', 'github_branch', 'commit_message', 'submit', 'download', 'install', 'pypi', 'github', 'cancel', 'delete'):
                the_field = getattr(form, attrib)
                for error in the_field.errors:
                    the_error += str(error)
            raise DAError("Form did not validate with " + str(the_error))
    the_file = re.sub(r'[^A-Za-z0-9\-\_\.]+', '-', the_file)
    the_file = re.sub(r'^docassemble-', r'', the_file)
    files = sorted([f for f in os.listdir(area['playgroundpackages'].directory) if os.path.isfile(os.path.join(area['playgroundpackages'].directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    editable_files = list()
    mode = "yaml"
    for a_file in files:
        editable_files.append(dict(name=a_file, modtime=os.path.getmtime(os.path.join(area['playgroundpackages'].directory, a_file))))
    assign_opacity(editable_files)
    editable_file_listing = [x['name'] for x in editable_files]
    if request.method == 'GET' and not the_file and not is_new:
        if 'playgroundpackages' in session and session['playgroundpackages'] in editable_file_listing:
            the_file = session['playgroundpackages']
        else:
            if 'playgroundpackages' in session:
                del session['playgroundpackages']
            if len(editable_files):
                the_file = sorted(editable_files, key=lambda x: x['modtime'])[-1]['name']
            else:
                the_file = ''
    if the_file != '' and not user_can_edit_package(pkgname='docassemble.' + the_file):
        flash(word('Sorry, that package name,') + ' ' + the_file + word(', is already in use by someone else'), 'error')
        validated = False
    if request.method == 'GET' and the_file in editable_file_listing:
        session['playgroundpackages'] = the_file
    if the_file == '' and len(file_list['playgroundpackages']) and not is_new:
        the_file = file_list['playgroundpackages'][0]
    old_info = dict()
    on_github = False
    branch_info = list()
    github_http = None
    github_ssh = None
    github_use_ssh = False
    github_user_name = None
    github_email = None
    github_author_name = None
    if the_file != '' and can_publish_to_github and not is_new:
        github_package_name = 'docassemble-' + the_file
        try:
            storage = RedisCredStorage(app='github')
            credentials = storage.get()
            if not credentials or credentials.invalid:
                if form.github.data:
                    state_string = random_string(16)
                    session['github_next'] = json.dumps(dict(state=state_string, path='playground_packages', arguments=request.args))
                    flow = get_github_flow()
                    uri = flow.step1_get_authorize_url(state=state_string)
                    return redirect(uri)
                else:
                    raise Exception('GitHub integration expired.')
            http = credentials.authorize(httplib2.Http())
            resp, content = http.request("https://api.github.com/user", "GET")
            if int(resp['status']) == 200:
                info = json.loads(content)
                github_user_name = info.get('login', None)
                github_author_name = info.get('name', None)
                github_email = info.get('email', None)
            else:
                raise DAError("playground_packages: could not get information about GitHub User")
            if github_email is None:
                resp, content = http.request("https://api.github.com/user/emails", "GET")
                if int(resp['status']) == 200:
                    info = json.loads(content)
                    if len(info) and 'email' in info[0]:
                        github_email = info[0]['email']
            if github_user_name is None or github_email is None:
                raise DAError("playground_packages: login not present in user info from GitHub")
            found = False
            resp, content = http.request("https://api.github.com/repos/" + str(github_user_name) + "/" + github_package_name, "GET")
            if int(resp['status']) == 200:
                repo_info = json.loads(content)
                github_http = repo_info['html_url']
                github_ssh = repo_info['ssh_url']
                if repo_info['private']:
                    github_use_ssh = True
                github_message = word('This package is') + ' <a target="_blank" href="' + repo_info.get('html_url', 'about:blank') + '">' + word("published on GitHub") + '</a>.'
                if github_author_name:
                    github_message += "  " + word("The author is") + " " + github_author_name + "."
                on_github = True
                branch_info = get_branch_info(http, repo_info['full_name'])
                found = True
            if found is False:
                repositories = get_user_repositories(http)
                for repo_info in repositories:
                    if repo_info['name'] != github_package_name:
                        continue
                    github_http = repo_info['html_url']
                    github_ssh = repo_info['ssh_url']
                    if repo_info['private']:
                        github_use_ssh = True
                    github_message = word('This package is') + ' <a target="_blank" href="' + repo_info.get('html_url', 'about:blank') + '">' + word("published on your GitHub account") + '</a>.'
                    on_github = True
                    branch_info = get_branch_info(http, repo_info['full_name'])
                    found = True
                    break
            if found is False:
                orgs_info = get_orgs_info(http)
                for org_info in orgs_info:
                    resp, content = http.request("https://api.github.com/repos/" + str(org_info['login']) + "/" + github_package_name, "GET")
                    if int(resp['status']) == 200:
                        repo_info = json.loads(content)
                        github_http = repo_info['html_url']
                        github_ssh = repo_info['ssh_url']
                        if repo_info['private']:
                            github_use_ssh = True
                        github_message = word('This package is') + ' <a target="_blank" href="' + repo_info.get('html_url', 'about:blank') + '">' + word("published on your GitHub account") + '</a>.'
                        on_github = True
                        branch_info = get_branch_info(http, repo_info['full_name'])
                        found = True
                        break
            if found is False:
                github_message = word('This package is not yet published on your GitHub account.')
        except Exception as e:
            logmessage('playground_packages: GitHub error.  ' + str(e))
            on_github = None
            github_message = word('Unable to determine if the package is published on your GitHub account.')
    github_url_from_file = None
    pypi_package_from_file = None
    if request.method == 'GET' and the_file != '':
        if the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
            filename = os.path.join(area['playgroundpackages'].directory, the_file)
            with open(filename, 'rU') as fp:
                content = fp.read().decode('utf8')
                old_info = yaml.load(content)
                if type(old_info) is dict:
                    github_url_from_file = old_info.get('github_url', None)
                    pypi_package_from_file = old_info.get('pypi_package_name', None)
                    for field in ('license', 'description', 'author_name', 'author_email', 'version', 'url', 'readme'):
                        if field in old_info:
                            form[field].data = old_info[field]
                        else:
                            form[field].data = ''
                    if 'dependencies' in old_info and type(old_info['dependencies']) is list and len(old_info['dependencies']):
                        for item in ('docassemble', 'docassemble.base', 'docassemble.webapp'):
                            if item in old_info['dependencies']:
                                del old_info['dependencies'][item]
                    for field in ('dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files'):
                        if field in old_info and type(old_info[field]) is list and len(old_info[field]):
                            form[field].data = old_info[field]
        else:
            filename = None
    if request.method == 'POST' and 'uploadfile' in request.files:
        the_files = request.files.getlist('uploadfile')
        need_to_restart = False
        if current_user.timezone:
            the_timezone = pytz.timezone(current_user.timezone)
        else:
            the_timezone = pytz.timezone(get_default_timezone())
        epoch_date = datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.utc)
        if the_files:
            for up_file in the_files:
                #try:
                    zip_filename = secure_filename(up_file.filename)
                    zippath = tempfile.NamedTemporaryFile(mode="wb", suffix=".zip", delete=True)
                    up_file.save(zippath.name)
                    area_sec = dict(templates='playgroundtemplate', static='playgroundstatic', sources='playgroundsources', questions='playground')
                    with zipfile.ZipFile(zippath.name, mode='r') as zf:
                        readme_text = ''
                        setup_py = ''
                        extracted = dict()
                        data_files = dict(templates=list(), static=list(), sources=list(), interviews=list(), modules=list(), questions=list())
                        for zinfo in zf.infolist():
                            #logmessage("Found a " + zinfo.filename)
                            if zinfo.filename.endswith('/'):
                                continue
                            (directory, filename) = os.path.split(zinfo.filename)
                            if filename.startswith('#') or filename.endswith('~'):
                                continue
                            dirparts = splitall(directory)
                            if '.git' in dirparts:
                                continue
                            levels = re.findall(r'/', directory)
                            time_tuple = zinfo.date_time
                            the_time = time.mktime(datetime.datetime(*time_tuple).timetuple())
                            for sec in ('templates', 'static', 'sources', 'questions'):
                                if directory.endswith('data/' + sec) and filename != 'README.md':
                                    data_files[sec].append(filename)
                                    target_filename = os.path.join(area[area_sec[sec]].directory, filename)
                                    with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                        shutil.copyfileobj(source_fp, target_fp)
                                    os.utime(target_filename, (the_time, the_time))
                            if filename == 'README.md' and len(levels) == 0:
                                readme_text = zf.read(zinfo)
                            if filename == 'setup.py' and len(levels) == 0:
                                setup_py = zf.read(zinfo)
                            elif len(levels) >= 2 and filename.endswith('.py') and filename != '__init__.py' and 'tests' not in dirparts:
                                need_to_restart = True
                                data_files['modules'].append(filename)
                                target_filename = os.path.join(area['playgroundmodules'].directory, filename)
                                with zf.open(zinfo) as source_fp, open(target_filename, 'wb') as target_fp:
                                    shutil.copyfileobj(source_fp, target_fp)
                                    os.utime(target_filename, (the_time, the_time))
                        setup_py = re.sub(r'.*setup\(', '', setup_py, flags=re.DOTALL)
                        for line in setup_py.splitlines():
                            m = re.search(r"^ *([a-z_]+) *= *\(?u?'(.*)'", line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\(?u?"(.*)"', line)
                            if m:
                                extracted[m.group(1)] = m.group(2)
                            m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
                            if m:
                                the_list = list()
                                for item in re.split(r', *', m.group(2)):
                                    inner_item = re.sub(r"'$", '', item)
                                    inner_item = re.sub(r"^u?'", '', inner_item)
                                    inner_item = re.sub(r'"+$', '', inner_item)
                                    inner_item = re.sub(r'^u?"+', '', inner_item)
                                    the_list.append(inner_item)
                                extracted[m.group(1)] = the_list
                        info_dict = dict(readme=readme_text, interview_files=data_files['questions'], sources_files=data_files['sources'], static_files=data_files['static'], module_files=data_files['modules'], template_files=data_files['templates'], dependencies=extracted.get('install_requires', list()), description=extracted.get('description', ''), author_name=extracted.get('author', ''), author_email=extracted.get('author_email', ''), license=extracted.get('license', ''), url=extracted.get('url', ''), version=extracted.get('version', ''))
                        info_dict['dependencies'] = [x for x in info_dict['dependencies'] if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp')]
                        package_name = re.sub(r'^docassemble\.', '', extracted.get('name', 'unknown'))
                        with open(os.path.join(area['playgroundpackages'].directory, package_name), 'w') as fp:
                            the_yaml = yaml.safe_dump(info_dict, default_flow_style=False, default_style='|')
                            fp.write(the_yaml.encode('utf8'))
                        for key in r.keys('da:interviewsource:docassemble.playground' + str(current_user.id) + ':*'):
                            r.incr(key)
                        for sec in area:
                            area[sec].finalize()
                        the_file = package_name
                    zippath.close()
                #except Exception as errMess:
                    #flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        if show_message:
            flash(word("The package was unpacked into the Playground."), 'success')
        if need_to_restart:
            return redirect(url_for('restart_page', next=url_for('playground_packages', file=the_file)))
        return redirect(url_for('playground_packages', file=the_file))
    if request.method == 'GET' and 'pull' in request.args and int(request.args['pull']) == 1 and ('github_url' in request.args or 'pypi' in request.args):
        area_sec = dict(templates='playgroundtemplate', static='playgroundstatic', sources='playgroundsources', questions='playground')
        readme_text = ''
        setup_py = ''
        branch = request.args.get('branch', None)
        if branch in ('', 'None'):
            branch = None
        if branch:
            branch_option = '-b ' + branch + ' '
        else:
            branch_option = ''
        need_to_restart = False
        extracted = dict()
        data_files = dict(templates=list(), static=list(), sources=list(), interviews=list(), modules=list(), questions=list())
        directory = tempfile.mkdtemp()
        output = ''
        #logmessage("Can publish " + repr(can_publish_to_github))
        #logmessage("username " + repr(github_user_name))
        #logmessage("email " + repr(github_email))
        #logmessage("author name " + repr(github_author_name))
        github_url = None
        pypi_package = None
        if 'github_url' in request.args:
            github_url = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['github_url'])
            if github_url.startswith('git@') and can_publish_to_github and github_user_name and github_email:
                (private_key_file, public_key_file) = get_ssh_keys(github_email)
                os.chmod(private_key_file, stat.S_IRUSR | stat.S_IWUSR)
                os.chmod(public_key_file, stat.S_IRUSR | stat.S_IWUSR)
                ssh_script = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.sh', delete=False)
                with open(ssh_script.name, 'w') as fp:
                    fp.write('# /bin/bash\n\nssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i "' + str(private_key_file) + '" $1 $2 $3 $4 $5 $6')
                ssh_script.close()
                os.chmod(ssh_script.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR )
                #git_prefix = "GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -i \"" + str(private_key_file) + "\"' "
                git_prefix = "GIT_SSH=" + ssh_script.name + " "
                output += "Doing " + git_prefix + "git clone " + branch_option + github_url + "\n"
                try:
                    output += subprocess.check_output(git_prefix + "git clone " + branch_option + github_url, cwd=directory, stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("playground_packages: error running git clone.  " + output)
            else:
                try:
                    if branch is not None:
                        output += subprocess.check_output(['git', 'clone', '-b', branch, github_url], cwd=directory, stderr=subprocess.STDOUT)
                    else:
                        output += subprocess.check_output(['git', 'clone', github_url], cwd=directory, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as err:
                    output += err.output
                    raise DAError("playground_packages: error running git clone.  " + output)
            logmessage(output)
        elif 'pypi' in request.args:
            pypi_package = re.sub(r'[^A-Za-z0-9\-\.\_\~\:\/\?\#\[\]\@\!\$\&\'\(\)\*\+\,\;\=\`]', '', request.args['pypi'])
            pypi_package = 'docassemble.' + re.sub(r'^docassemble\.', '', pypi_package)
            package_file = tempfile.NamedTemporaryFile(suffix='.tar.gz')
            try:
                http = httplib2.Http()
                resp, content = http.request("https://pypi.python.org/pypi/" + str(pypi_package) + "/json", "GET")
                pypi_url = None
                if int(resp['status']) == 200:
                    pypi_response = json.loads(content)
                    for file_option in pypi_response['releases'][pypi_response['info']['version']]:
                        if file_option['packagetype'] == 'sdist':
                            pypi_url = file_option['url']
                            break
                else:
                    flash(word("The package you specified could not be downloaded from PyPI."), 'error')
                    return redirect(url_for('playground_packages'))
                if pypi_url is None:
                    flash(word("The package you specified could not be downloaded from PyPI as a tar.gz file."), 'error')
                    return redirect(url_for('playground_packages'))
            except Exception as err:
                raise DAError("playground_packages: error getting information about PyPI package.  " + str(err))
            try:
                urllib.urlretrieve(pypi_url, package_file.name)
            except Exception as err:
                raise DAError("playground_packages: error downloading PyPI package.  " + str(err))
            try:
                tar = tarfile.open(package_file.name)
                tar.extractall(path=directory)
                tar.close()
            except Exception as err:
                raise DAError("playground_packages: error unpacking PyPI package.  " + str(err))
            package_file.close()
        initial_directories = len(splitall(directory)) + 1
        for root, dirs, files in os.walk(directory):
            for file in files:
                orig_file = os.path.join(root, file)
                #output += "Original file is " + orig_file + "\n"
                thefilename = os.path.join(*splitall(orig_file)[initial_directories:])
                (the_directory, filename) = os.path.split(thefilename)
                if filename.startswith('#') or filename.endswith('~'):
                    continue
                dirparts = splitall(the_directory)
                if '.git' in dirparts:
                    continue
                levels = re.findall(r'/', the_directory)
                for sec in ('templates', 'static', 'sources', 'questions'):
                    if the_directory.endswith('data/' + sec) and filename != 'README.md':
                        data_files[sec].append(filename)
                        target_filename = os.path.join(area[area_sec[sec]].directory, filename)
                        #output += "Copying " + orig_file + "\n"
                        copy_if_different(orig_file, target_filename)
                if filename == 'README.md' and len(levels) == 0:
                    with open(orig_file, 'rU') as fp:
                        readme_text = fp.read().decode('utf8')
                if filename == 'setup.py' and len(levels) == 0:
                    with open(orig_file, 'rU') as fp:
                        setup_py = fp.read().decode('utf8')
                elif len(levels) >= 1 and filename.endswith('.py') and filename != '__init__.py' and 'tests' not in dirparts:
                    data_files['modules'].append(filename)
                    target_filename = os.path.join(area['playgroundmodules'].directory, filename)
                    #output += "Copying " + orig_file + "\n"
                    if (not os.path.isfile(target_filename)) or filecmp.cmp(orig_file, target_filename) is False:
                        need_to_restart = True
                    copy_if_different(orig_file, target_filename)
        #output += "setup.py is " + str(len(setup_py)) + " characters long\n"
        setup_py = re.sub(r'.*setup\(', '', setup_py, flags=re.DOTALL)
        for line in setup_py.splitlines():
            m = re.search(r"^ *([a-z_]+) *= *\(?u?'(.*)'", line)
            if m:
                extracted[m.group(1)] = m.group(2)
            m = re.search(r'^ *([a-z_]+) *= *\(?u?"(.*)"', line)
            if m:
                extracted[m.group(1)] = m.group(2)
            m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
            if m:
                the_list = list()
                for item in re.split(r', *', m.group(2)):
                    inner_item = re.sub(r"'$", '', item)
                    inner_item = re.sub(r"^u?'", '', inner_item)
                    inner_item = re.sub(r'"+$', '', inner_item)
                    inner_item = re.sub(r'^u?"+', '', inner_item)
                    the_list.append(inner_item)
                extracted[m.group(1)] = the_list
        info_dict = dict(readme=readme_text, interview_files=data_files['questions'], sources_files=data_files['sources'], static_files=data_files['static'], module_files=data_files['modules'], template_files=data_files['templates'], dependencies=extracted.get('install_requires', list()), description=extracted.get('description', ''), author_name=extracted.get('author', ''), author_email=extracted.get('author_email', ''), license=extracted.get('license', ''), url=extracted.get('url', ''), version=extracted.get('version', ''), github_url=github_url, github_branch=branch, pypi_package_name=pypi_package)
        info_dict['dependencies'] = [x for x in info_dict['dependencies'] if x not in ('docassemble', 'docassemble.base', 'docassemble.webapp')]
        #output += "info_dict is set\n"
        package_name = re.sub(r'^docassemble\.', '', extracted.get('name', 'unknown'))
        if not user_can_edit_package(pkgname='docassemble.' + package_name):
            index = 1
            orig_package_name = package_name
            while index < 100 and not user_can_edit_package(pkgname='docassemble.' + package_name):
                index += 1
                package_name = orig_package_name + str(index)
        with open(os.path.join(area['playgroundpackages'].directory, package_name), 'w') as fp:
            the_yaml = yaml.safe_dump(info_dict, default_flow_style=False, default_style='|')
            fp.write(the_yaml.encode('utf8'))
        area['playgroundpackages'].finalize()
        for sec in area:
            area[sec].finalize()
        for key in r.keys('da:interviewsource:playground' + str(current_user.id) + ':*'):
            r.incr(key)
        the_file = package_name
        if show_message:
            flash(word("The package was unpacked into the Playground."), 'success')
        #shutil.rmtree(directory)
        if need_to_restart:
            return redirect(url_for('restart_page', next=url_for('playground_packages', file=the_file)))
        return redirect(url_for('playground_packages', file=the_file))
    if request.method == 'POST' and form.delete.data and the_file != '' and the_file == form.file_name.data and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
        os.remove(os.path.join(area['playgroundpackages'].directory, the_file))
        area['playgroundpackages'].finalize()
        flash(word("Deleted package"), "success")
        return redirect(url_for('playground_packages'))
    if not is_new:
        pkgname = 'docassemble.' + the_file
        pypi_info = pypi_status(pkgname)
        if can_publish_to_pypi:
            if pypi_info['error']:
                pypi_message = word("Unable to determine if the package is published on PyPI.")
            else:
                if pypi_info['exists'] and 'info' in pypi_info['info']:
                    pypi_version = pypi_info['info']['info'].get('version', None)
                    pypi_message = word('This package is') + ' <a target="_blank" href="' + pypi_url + '/' + pkgname + '/' + pypi_version + '">' + word("published on PyPI") + '</a>.'
                    pypi_author = pypi_info['info']['info'].get('author', None)
                    if pypi_author:
                        pypi_message += "  " + word("The author is") + " " + pypi_author + "."
                    if pypi_version != form['version'].data:
                        pypi_message += "  " + word("The version on PyPI is") + " " + str(pypi_version) + ".  " + word("Your version is") + " " + str(form['version'].data) + "."
                else:
                    pypi_message = word('This package is not yet published on PyPI.')
    if request.method == 'POST' and validated:
        new_info = dict()
        for field in ('license', 'description', 'author_name', 'author_email', 'version', 'url', 'readme', 'dependencies', 'interview_files', 'template_files', 'module_files', 'static_files', 'sources_files'):
            new_info[field] = form[field].data
        #logmessage("found " + str(new_info))
        if form.submit.data or form.download.data or form.install.data or form.pypi.data or form.github.data:
            if the_file != '':
                area['playgroundpackages'].finalize()
                if form.original_file_name.data and form.original_file_name.data != the_file:
                    old_filename = os.path.join(area['playgroundpackages'].directory, form.original_file_name.data)
                    if os.path.isfile(old_filename):
                        os.remove(old_filename)
                if form.pypi.data and pypi_version is not None:
                    versions = pypi_version.split(".")
                    while True:
                        versions[-1] = str(int(versions[-1]) + 1)
                        new_info['version'] = ".".join(versions)
                        if 'releases' not in pypi_info['info'] or new_info['version'] not in pypi_info['info']['releases'].keys():
                            break
                        versions = new_info['version'].split(".")
                filename = os.path.join(area['playgroundpackages'].directory, the_file)
                with open(filename, 'w') as fp:
                    the_yaml = yaml.safe_dump(new_info, default_flow_style=False, default_style = '|')
                    fp.write(the_yaml.encode('utf8'))
                area['playgroundpackages'].finalize()
                if form.download.data:
                    return redirect(url_for('create_playground_package', package=the_file))
                if form.install.data:
                    return redirect(url_for('create_playground_package', package=the_file, install='1'))
                if form.pypi.data:
                    return redirect(url_for('create_playground_package', package=the_file, pypi='1'))
                if form.github.data:
                    return redirect(url_for('create_playground_package', package=the_file, github='1', commit_message=form.commit_message.data, branch=form.github_branch.data))
                the_time = formatted_current_time()
                # existing_package = Package.query.filter_by(name='docassemble.' + the_file, active=True).order_by(Package.id.desc()).first()
                # if existing_package is None:
                #     package_auth = PackageAuth(user_id=current_user.id)
                #     package_entry = Package(name='docassemble.' + the_file, package_auth=package_auth, upload=file_number, type='zip')
                #     db.session.add(package_auth)
                #     db.session.add(package_entry)
                #     #sys.stderr.write("Ok, did the commit\n")
                # else:
                #     existing_package.upload = file_number
                #     existing_package.active = True
                #     existing_package.version += 1
                # db.session.commit()
                if show_message:
                    flash(word('The package information was saved.'), 'success')                
    form.original_file_name.data = the_file
    form.file_name.data = the_file
    if the_file != '' and os.path.isfile(os.path.join(area['playgroundpackages'].directory, the_file)):
        filename = os.path.join(area['playgroundpackages'].directory, the_file)
    else:
        filename = None
    header = word("Packages")
    upload_header = None
    edit_header = None
    description = Markup("""Describe your package and choose the files from your Playground that will go into it.""")
    after_text = None
    if scroll:
        extra_command = "        scrollBottom();"
    else:
        extra_command = ""
    extra_command += upload_js() + """
        $("#daCancel").click(function(event){
          var whichButton = this;
          $("#commit_message_div").hide();
          $(".btn-da").each(function(){
            if (this != whichButton && $(this).is(":hidden")){
              $(this).show();
            }
          });
          $("#daGitHub").html(""" + json.dumps(word("GitHub")) + """);
          $(this).hide();
          event.preventDefault();
          return false;
        });
        $("#daGitHub").click(function(event){
          var whichButton = this;
          if ($("#commit_message").val().length == 0 || $("#commit_message_div").is(":hidden")){
            if ($("#commit_message_div").is(":visible")){
              $("#commit_message").parent().addClass("has-error");
            }
            else{
              $("#commit_message_div").show();
              $(".btn-da").each(function(){
                if (this != whichButton && $(this).is(":visible")){
                  $(this).hide();
                }
              });
              $(this).html(""" + json.dumps(word("Commit")) + """);
              $("#daCancel").show();
            }
            $("#commit_message").focus();
            window.scrollTo(0, document.body.scrollHeight);
            event.preventDefault();
            return false;
          }
        });"""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    if len(editable_files):
        any_files = True
    else:
        any_files = False
    #back_button = Markup('<a href="' + url_for('playground_page') + '" class="btn btn-sm navbar-btn nav-but"><i class="fas fa-arrow-left"></i> ' + word("Back") + '</a>')
    back_button = Markup('<span class="navbar-brand"><a href="' + url_for('playground_page') + '" class="playground-back text-muted backbuttoncolor" type="submit" title=' + json.dumps(word("Go back to the main Playground page")) + '><i class="fas fa-chevron-left"></i><span class="daback">' + word('Back') + '</span></a></span>')
    if can_publish_to_pypi:
        if pypi_message is not None:
            pypi_message = Markup(pypi_message)
    else:
        pypi_message = None
    extra_js = '\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/markdown/markdown.js") + '"></script>\n    '
    extra_js += kbLoad
    extra_js += """<script>
      var isNew = """ + json.dumps(is_new) + """;
      var existingFiles = """ + json.dumps(files) + """;
      var currentFile = """ + json.dumps(the_file) + """;
      function scrollBottom(){
        $("html, body").animate({ scrollTop: $(document).height() }, "slow");
      }
      $( document ).ready(function() {
        $("#file_name").on('change', function(){
          var newFileName = $(this).val();
          if ((!isNew) && newFileName == currentFile){
            return;
          }
          for (var i = 0; i < existingFiles.length; i++){
            if (newFileName == existingFiles[i]){
              alert(""" + json.dumps(word("Warning: a package definition by that name already exists.  If you save, you will overwrite it.")) + """);
              return;
            }
          }
          return;
        });
        $("#daDelete").click(function(event){
          if (!confirm(""" + '"' + word("Are you sure that you want to delete this package?") + '"' + """)){
            event.preventDefault();
          }
        });
        $("#daPyPI").click(function(event){
          if(!confirm(""" + '"' + word("Are you sure that you want to publish this package to PyPI?") + '"' + """)){
            event.preventDefault();
          }
        });
        daTextArea = document.getElementById("readme");
        var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {mode: "markdown", """ + kbOpt + """tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true, matchBrackets: true});
        $(window).bind("beforeunload", function(){
          daCodeMirror.save();
          $("#form").trigger("checkform.areYouSure");
        });
        $("#form").areYouSure(""" + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + """);
        $("#form").bind("submit", function(){
          daCodeMirror.save();
          $("#form").trigger("reinitialize.areYouSure");
          return true;
        });
        daCodeMirror.setOption("extraKeys", { Tab: function(cm){ var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }});
        daCodeMirror.setOption("coverGutterNextToScrollbar", true);""" + extra_command + """
      });
    </script>"""
    if github_use_ssh:
        the_github_url = github_ssh
    else:
        the_github_url = github_http
    if the_github_url is None and github_url_from_file is not None:
        the_github_url = github_url_from_file
    if the_github_url is None:
        the_pypi_package_name = pypi_package_from_file
    else:
        the_pypi_package_name = None
    if github_message is not None and github_url_from_file is not None and github_url_from_file != github_http and github_url_from_file != github_ssh:
        github_message += '  ' + word("This package was originally pulled from") + ' <a target="_blank" href="' + github_as_http(github_url_from_file) + '">' + word('a GitHub repository') + '</a>.'
    if github_message is not None:
        github_message = Markup(github_message)
    branch = old_info.get('github_branch', None)
    if branch is not None:
        branch = branch.strip()
    branch_choices = list()
    branch_names = set()
    for br in branch_info:
        branch_names.add(br['name'])
        branch_choices.append((br['name'], br['name']))
    if branch and branch in branch_names:
        form.github_branch.data = branch
    elif 'master' in branch_names:
        form.github_branch.data = 'master'
    form.github_branch.choices = branch_choices
    default_branch = branch if branch else 'master'
    if form.author_name.data in ('', None) and current_user.first_name and current_user.last_name:
        form.author_name.data = current_user.first_name + " " + current_user.last_name
    if form.author_email.data in ('', None) and current_user.email:
        form.author_email.data = current_user.email
    return render_template('pages/playgroundpackages.html', branch=default_branch, version_warning=None, bodyclass='adminbody', can_publish_to_pypi=can_publish_to_pypi, pypi_message=pypi_message, can_publish_to_github=can_publish_to_github, github_message=github_message, github_url=the_github_url, pypi_package_name=the_pypi_package_name, back_button=back_button, tab_title=header, page_title=header, extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup(extra_js), header=header, upload_header=upload_header, edit_header=edit_header, description=description, form=form, fileform=fileform, files=files, file_list=file_list, userid=current_user.id, editable_files=editable_files, current_file=the_file, after_text=after_text, section_name=section_name, section_sec=section_sec, section_field=section_field, package_names=package_names, any_files=any_files), 200

def github_as_http(url):
    if url.startswith('http'):
        return url
    return re.sub('^[^@]+@([^:]+):(.*)\.git$', r'https://\1/\2', url)

def copy_if_different(source, destination):
    if (not os.path.isfile(destination)) or filecmp.cmp(source, destination) is False:
        shutil.copyfile(source, destination)

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

@app.route('/playground_redirect', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_redirect():
    key = 'da:runplayground:' + str(current_user.id)
    counter = 0
    while counter < 15:
        the_url = r.get(key)
        #logmessage("playground_redirect: key " + str(key) + " is " + str(the_url))
        if the_url is not None:
            r.delete(key)
            return redirect(the_url)
        time.sleep(1)
        counter += 1
    abort(404)

def upload_js():
    return """
        $("#uploadlink").on('click', function(event){
          $("#uploadlabel").click();
          event.preventDefault();
          return false;
        });
        $("#uploadlabel").on('click', function(event){
          event.stopPropagation();
          event.preventDefault();
          $("#uploadfile").click();
          return false;
        });
        $("#uploadfile").on('click', function(event){
          event.stopPropagation();
        });
        $("#uploadfile").on('change', function(event){
          $("#fileform").submit();
        });"""
    
def search_js(form=None):
    if form is None:
        form = 'form'
    return """
var origPosition = null;
var searchMatches = null;

function searchReady(){
  $("#""" + form + """ input[name='search_term']").on("focus", function(event){
    origPosition = daCodeMirror.getCursor('from');
  });
  $("#""" + form + """ input[name='search_term']").change(update_search);
  $("#""" + form + """ input[name='search_term']").on("keydown", enter_search);
  $("#""" + form + """ input[name='search_term']").on("keyup", update_search);
  $("#daSearchPrevious").click(function(event){
    var query = $("#""" + form + """ input[name='search_term']").val();
    if (query.length == 0){
      clear_matches();
      daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      return;
    }
    origPosition = daCodeMirror.getCursor('from');
    var sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findPrevious();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
    }
    else{
      var lastLine = daCodeMirror.lastLine()
      var lastChar = daCodeMirror.lineInfo(lastLine).text.length
      origPosition = { line: lastLine, ch: lastChar, xRel: 1 }
      sc = daCodeMirror.getSearchCursor(query, origPosition);
      show_matches(query);
      var found = sc.findPrevious();
      if (found){
        daCodeMirror.setSelection(sc.from(), sc.to());
        scroll_to_selection();
        $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      }
      else{
        $("#""" + form + """ input[name='search_term']").addClass("search-error");
      }
    }
    event.preventDefault();
    return false;
  });
  $("#daSearchNext").click(function(event){
    var query = $("#""" + form + """ input[name='search_term']").val();
    if (query.length == 0){
      clear_matches();
      daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      return;
    }
    origPosition = daCodeMirror.getCursor('to');
    var sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findNext();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $("#""" + form + """ input[name='search_term']").removeClass("search-error");
    }
    else{
      origPosition = { line: 0, ch: 0, xRel: 1 }
      sc = daCodeMirror.getSearchCursor(query, origPosition);
      show_matches(query);
      var found = sc.findNext();
      if (found){
        daCodeMirror.setSelection(sc.from(), sc.to());
        scroll_to_selection();
        $("#""" + form + """ input[name='search_term']").removeClass("search-error");
      }
      else{
        $("#""" + form + """ input[name='search_term']").addClass("search-error");
      }
    }
    event.preventDefault();
    return false;
  });
}

function show_matches(query){
  clear_matches();
  if (query.length == 0){
    daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
    $("#""" + form + """ input[name='search_term']").removeClass("search-error");
    return;
  }
  searchMatches = daCodeMirror.showMatchesOnScrollbar(query);
}

function clear_matches(){
  if (searchMatches != null){
    try{
      searchMatches.clear();
    }
    catch(err){}
  }
}

function scroll_to_selection(){
  daCodeMirror.scrollIntoView(daCodeMirror.getCursor('from'))
  var t = daCodeMirror.charCoords(daCodeMirror.getCursor('from'), "local").top;
  daCodeMirror.scrollTo(null, t);
}

function enter_search(event){
  if(event.keyCode == 13) {
    event.preventDefault();
    $("#daSearchNext").click();
    return false;
  }
}

function update_search(event){
  var query = $(this).val();
  if (query.length == 0){
    clear_matches();
    daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
    $(this).removeClass("search-error");
    return;
  }
  if(event.keyCode == 13) {
    event.preventDefault();
    return false;
  }
  var sc = daCodeMirror.getSearchCursor(query, origPosition);
  show_matches(query);

  var found = sc.findNext();
  if (found){
    daCodeMirror.setSelection(sc.from(), sc.to());
    scroll_to_selection();
    $(this).removeClass("search-error");
  }
  else{
    origPosition = { line: 0, ch: 0, xRel: 1 }
    sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findNext();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $(this).removeClass("search-error");
    }
    else{
      $(this).addClass("search-error");
    }
  }
}

"""
    
def variables_js(form=None, office_mode=False):
    output = """
function activatePopovers(){
  $(function () {
    $('[data-toggle="popover"]').popover({trigger: 'focus', html: true})
  });
}

function activateVariables(){
  $(".daparenthetical").on("click", function(event){
    var reference = $(this).data("ref");
    //console.log("reference is " + reference);
    var target = $('[data-name="' + reference + '"]').first();
    if (target.length > 0){
      //console.log("target is " + target);
      //console.log("scrolltop is now " + $('#daplaygroundcard').scrollTop());
      //console.log("Scrolling to " + target.parent().parent().position().top);
      $('#daplaygroundcard').animate({
          scrollTop: target.parent().parent().position().top
      }, 1000);
    }
    event.preventDefault();
  });

  $(".dashowmethods").on("click", function(event){
    var target_id = $(this).data("showhide");
    $("#" + target_id).slideToggle();
  });

  $(".dashowattributes").each(function(){
    var basename = $(this).data('name');
    if (attrs_showing.hasOwnProperty(basename)){
      if (attrs_showing[basename]){
        $('tr[data-parent="' + basename + '"]').show();
      }
    }
    else{
      attrs_showing[basename] = false;
    }
  });

  $(".dashowattributes").on("click", function(event){
    var basename = $(this).data('name');
    attrs_showing[basename] = !attrs_showing[basename];
    $('tr[data-parent="' + basename + '"]').each(function(){
      $(this).toggle();
    });
  });"""
    if office_mode:
        return output + "\n}"
    if form is None:
        form = 'form'
    output += """
  $(".playground-variable").on("click", function(event){
    daCodeMirror.replaceSelection($(this).data("insert"), "around");
    daCodeMirror.focus();
  });

  $(".dasearchicon").on("click", function(event){
    var query = $(this).data('name');
    if (query == null || query.length == 0){
      clear_matches();
      daCodeMirror.setCursor(daCodeMirror.getCursor('from'));
      return;
    }
    origPosition = daCodeMirror.getCursor('to');
    $("#""" + form + """ input[name='search_term']").val(query);
    var sc = daCodeMirror.getSearchCursor(query, origPosition);
    show_matches(query);
    var found = sc.findNext();
    if (found){
      daCodeMirror.setSelection(sc.from(), sc.to());
      scroll_to_selection();
      $("#form input[name='search_term']").removeClass('search-error');
    }
    else{
      origPosition = { line: 0, ch: 0, xRel: 1 }
      sc = daCodeMirror.getSearchCursor(query, origPosition);
      show_matches(query);
      var found = sc.findNext();
      if (found){
        daCodeMirror.setSelection(sc.from(), sc.to());
        scroll_to_selection();
        $("#""" + form + """ input[name='search_term']").removeClass('search-error');
      }
      else{
        $("#""" + form + """ input[name='search_term']").addClass('search-error');
      }
    }
    event.preventDefault();
    return false;
  });
}

var interviewBaseUrl = '""" + url_for('index', reset='1', cache='0', i='docassemble.playground' + str(current_user.id) + ':.yml') + """';

function updateRunLink(){
  $("#daRunButton").attr("href", interviewBaseUrl.replace('.yml', $("#daVariables").val()));
}

function fetchVars(changed){
  daCodeMirror.save();
  updateRunLink();
  $.ajax({
    type: "POST",
    url: """ + '"' + url_for('playground_variables') + '"' + """,
    data: 'csrf_token=' + $("#""" + form + """ input[name='csrf_token']").val() + '&variablefile=' + $("#daVariables").val() + '&changed=' + (changed ? 1 : 0),
    success: function(data){
      if (data.vocab_list != null){
        vocab = data.vocab_list;
      }
      if (data.variables_html != null){
        $("#daplaygroundtable").html(data.variables_html);
        $(function () {
          $('[data-toggle="popover"]').popover({trigger: 'focus', html: true})
        });
        activateVariables();
      }
    },
    dataType: 'json'
  });
  $("#daVariables").blur();
}

function variablesReady(){
  $("#daVariables").change(function(event){
    fetchVars(true);
  });
}

"""
    return output

@app.route('/playgroundvariables', methods=['POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_variables():
    playground = SavedFile(current_user.id, fix=True, section='playground')
    files = sorted([f for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f)) and re.search(r'^[A-Za-z0-9]', f)])
    if len(files) == 0:
        return jsonify(success=False, reason=1)
    post_data = request.form.copy()
    if request.method == 'POST' and 'variablefile' in post_data:
        active_file = post_data['variablefile']
        if post_data['variablefile'] in files:
            if 'changed' in post_data and int(post_data['changed']):
                session['variablefile'] = active_file
            interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + active_file)
            interview_source.set_testing(True)
        else:
            if active_file == '':
                active_file = 'test.yml'
            content = ''
            if 'playground_content' in post_data:
                content = re.sub(r'\r\n', r'\n', post_data['playground_content'])
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, package="docassemble.playground" + str(current_user.id), path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        interview = interview_source.get_interview()
        ensure_ml_file_exists(interview, active_file)
        interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
        variables_html, vocab_list, vocab_dict = get_vars_in_use(interview, interview_status, debug_mode=False)
        return jsonify(success=True, variables_html=variables_html, vocab_list=vocab_list)
    return jsonify(success=False, reason=2)

def ensure_ml_file_exists(interview, yaml_file):
    if len(interview.mlfields):
        if hasattr(interview, 'ml_store'):
            parts = interview.ml_store.split(':')
            if parts[0] != 'docassemble.playground' + str(current_user.id):
                return
            source_filename = re.sub(r'.*/', '', parts[1])
        else:
            source_filename = 'ml-' + re.sub(r'\.ya?ml$', '', yaml_file) + '.json'
        #logmessage("Source filename is " + source_filename)
        source_dir = SavedFile(current_user.id, fix=False, section='playgroundsources')
        if source_filename not in source_dir.list_of_files():
            #logmessage("Source filename does not exist yet")
            source_dir.fix()
            source_path = os.path.join(source_dir.directory, source_filename)
            with open(source_path, 'a'):
                os.utime(source_path, None)
            source_dir.finalize()

def assign_opacity(files):
    if len(files) == 1:
        files[0]['opacity'] = 1.0
    else:
        indexno = 0.0
        max_indexno = float(len(files) - 1)
        for file_dict in sorted(files, key=lambda x: x['modtime']):
            file_dict['opacity'] = round(0.2 + 0.8*(indexno/max_indexno), 2)
            indexno += 1.0
            
@app.route('/playground', methods=['GET', 'POST'])
@login_required
@roles_required(['developer', 'admin'])
def playground_page():
    if 'ajax' in request.form and int(request.form['ajax']):
        is_ajax = True
        use_gd = False
        use_od = False
    else:
        is_ajax = False
        if app.config['USE_ONEDRIVE'] is False or get_od_folder() is None:
            use_od = False
        else:
            use_od = True
        if app.config['USE_GOOGLE_DRIVE'] is False or get_gd_folder() is None:
            use_gd = False
        else:
            use_gd = True
            use_od = False
        if request.method == 'GET' and needs_to_change_password():
            return redirect(url_for('user.change_password', next=url_for('playground_page')))
    fileform = PlaygroundUploadForm(request.form)
    form = PlaygroundForm(request.form)
    interview = None
    the_file = request.args.get('file', '')
    if request.method == 'GET':
        is_new = request.args.get('new', False)
        debug_mode = request.args.get('debug', False)
    else:
        debug_mode = False
        is_new = False
    if is_new:
        the_file = ''
    playground = SavedFile(current_user.id, fix=True, section='playground')
    #path = os.path.join(UPLOAD_DIRECTORY, 'playground', str(current_user.id))
    #if not os.path.exists(path):
    #    os.makedirs(path)
    if request.method == 'POST' and 'uploadfile' in request.files:
        the_files = request.files.getlist('uploadfile')
        if the_files:
            for up_file in the_files:
                try:
                    filename = secure_filename(up_file.filename)
                    extension, mimetype = get_ext_and_mimetype(filename)
                    if extension not in ('yml', 'yaml'):
                        flash(word("Sorry, only YAML files can be uploaded here.  To upload other types of files, use the Folders."), 'error')
                        return redirect(url_for('playground_page'))
                    filename = re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', filename)
                    new_file = filename
                    filename = os.path.join(playground.directory, filename)
                    up_file.save(filename)
                    try:
                        with open(filename, 'rU') as fp:
                            fp.read().decode('utf8')
                    except:
                        os.remove(filename)
                        flash(word("There was a problem reading the YAML file you uploaded.  Are you sure it is a YAML file?  File was not saved."), 'error')
                        return redirect(url_for('playground_page'))
                    playground.finalize()
                    r.incr('da:interviewsource:docassemble.playground' + str(current_user.id) + ':' + new_file)
                    return redirect(url_for('playground_page', file=os.path.basename(filename)))
                except Exception as errMess:
                    flash("Error of type " + str(type(errMess)) + " processing upload: " + str(errMess), "error")
        return redirect(url_for('playground_page'))
    if request.method == 'POST' and (form.submit.data or form.run.data or form.delete.data):
        if (form.playground_name.data):
            the_file = form.playground_name.data
            the_file = re.sub(r'[^A-Za-z0-9\_\-\. ]', '', the_file)
            if the_file != '':
                if not re.search(r'\.ya?ml$', the_file):
                    the_file = re.sub(r'\..*', '', the_file) + '.yml'
                filename = os.path.join(playground.directory, the_file)
                if not os.path.isfile(filename):
                    with open(filename, 'a'):
                        os.utime(filename, None)
            else:
                flash(word('You need to type in a name for the interview'), 'error')
                is_new = True
        else:
            flash(word('You need to type in a name for the interview'), 'error')
            is_new = True
    the_file = re.sub(r'[^A-Za-z0-9\_\-\. ]', '', the_file)
    files = sorted([dict(name=f, modtime=os.path.getmtime(os.path.join(playground.directory, f))) for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f)) and re.search(r'^[A-Za-z0-9].*[A-Za-z]$', f)], key=lambda x: x['name'])
    file_listing = [x['name'] for x in files]
    assign_opacity(files)
    content = ''
    if the_file and not is_new and the_file not in file_listing:
        the_file = ''
    is_default = False
    if request.method == 'GET' and not the_file and not is_new:
        if 'playgroundfile' in session and session['playgroundfile'] in files:
            the_file = session['playgroundfile']
        else:
            if 'playgroundfile' in session:
                del session['playgroundfile']
            if len(files):
                the_file = sorted(files, key=lambda x: x['modtime'])[-1]['name']
            else:
                the_file = 'test.yml'
                is_default = True
                content = default_playground_yaml
    if the_file in file_listing:
        session['playgroundfile'] = the_file
    active_file = the_file
    if 'variablefile' in session:
        if session['variablefile'] in file_listing:
            active_file = session['variablefile']
        else:
            del session['variablefile']
    if the_file != '':
        filename = os.path.join(playground.directory, the_file)
        if not os.path.isfile(filename):
            with open(filename, 'w') as fp:
                fp.write(content.encode('utf8'))
            playground.finalize()
    post_data = request.form.copy()
    # if request.method == 'POST' and 'variablefile' in post_data:
    #     active_file = post_data['variablefile']
    #     if post_data['variablefile'] in files:
    #         session['variablefile'] = active_file
    #         interview_source = docassemble.base.parse.interview_source_from_string('docassemble.playground' + str(current_user.id) + ':' + active_file)
    #         interview_source.set_testing(True)
    #     else:
    #         if active_file == '':
    #             active_file = 'test.yml'
    #         content = ''
    #         if form.playground_content.data:
    #             content = form.playground_content.data
    #         interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
    #     interview = interview_source.get_interview()
    #     interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
    #     variables_html, vocab_list, vocab_dict = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
    #     if is_ajax:
    #         return jsonify(variables_html=variables_html, vocab_list=vocab_list)
    if request.method == 'POST' and the_file != '' and form.validate():
        if form.delete.data:
            filename_to_del = os.path.join(playground.directory, form.playground_name.data)
            if os.path.isfile(filename_to_del):
                os.remove(filename_to_del)
                flash(word('File deleted.'), 'info')
                r.delete('da:interviewsource:docassemble.playground' + str(current_user.id) + ':' + the_file)
                if active_file != the_file:
                    r.incr('da:interviewsource:docassemble.playground' + str(current_user.id) + ':' + active_file)
                playground.finalize()
                if use_gd:
                    try:
                        trash_gd_file('questions', form.playground_name.data)
                    except Exception as the_err:
                        logmessage("playground_page: unable to delete file on Google Drive.  " + str(the_err))
                if use_od:
                    try:
                        trash_od_file('questions', form.playground_name.data)
                    except Exception as the_err:
                        logmessage("playground_page: unable to delete file on OneDrive.  " + str(the_err))
                if 'variablefile' in session and (session['variablefile'] == the_file or session['variablefile'] == form.playground_name.data):
                    del session['variablefile']
                return redirect(url_for('playground_page'))
            else:
                flash(word('File not deleted.  There was an error.'), 'error')
        if (form.submit.data or form.run.data) and form.playground_content.data:
            if form.original_playground_name.data and form.original_playground_name.data != the_file:
                old_filename = os.path.join(playground.directory, form.original_playground_name.data)
                if not is_ajax:
                    flash(word("Changed name of interview"), 'success')
                if os.path.isfile(old_filename):
                    os.remove(old_filename)
                    files = sorted([dict(name=f, modtime=os.path.getmtime(os.path.join(playground.directory, f))) for f in os.listdir(playground.directory) if os.path.isfile(os.path.join(playground.directory, f)) and re.search(r'^[A-Za-z0-9].*[A-Za-z]$', f)], key=lambda x: x['name'])
                    file_listing = [x['name'] for x in files]
                    assign_opacity(files)
            the_time = formatted_current_time()
            should_save = True
            the_content = re.sub(r'\r\n', r'\n', form.playground_content.data)
            if os.path.isfile(filename):
                with open(filename, 'rU') as fp:
                    orig_content = fp.read().decode('utf8')
                    if orig_content == the_content:
                        #logmessage("No need to save")
                        should_save = False
            if should_save:
                with open(filename, 'w') as fp:
                    fp.write(the_content.encode('utf8'))
            this_interview_string = 'docassemble.playground' + str(current_user.id) + ':' + the_file
            active_interview_string = 'docassemble.playground' + str(current_user.id) + ':' + active_file
            r.incr('da:interviewsource:' + this_interview_string)
            if the_file != active_file:
                r.incr('da:interviewsource:' + active_interview_string)
            # for a_file in files:
            #     docassemble.base.interview_cache.clear_cache('docassemble.playground' + str(current_user.id) + ':' + a_file)
            #     a_filename = os.path.join(playground.directory, a_file)
            #     if a_filename != filename and os.path.isfile(a_filename):
            #         with open(a_filename, 'a'):
            #             os.utime(a_filename, None)
            # a_filename = os.path.join(playground.directory, active_file)
            # if a_filename != filename and os.path.isfile(a_filename):
            #     with open(a_filename, 'a'):
            #         os.utime(a_filename, None)
            playground.finalize()
            docassemble.base.interview_cache.clear_cache(this_interview_string)
            if active_interview_string != this_interview_string:
                docassemble.base.interview_cache.clear_cache(active_interview_string)
            if not form.submit.data:
                the_url = url_for('index', reset=1, i=this_interview_string)
                key = 'da:runplayground:' + str(current_user.id)
                #logmessage("Setting key " + str(key) + " to " + str(the_url))
                pipe = r.pipeline()
                pipe.set(key, the_url)
                pipe.expire(key, 12)
                pipe.execute()
            try:
                interview_source = docassemble.base.parse.interview_source_from_string(active_interview_string)
                interview_source.set_testing(True)
                interview = interview_source.get_interview()
                ensure_ml_file_exists(interview, active_file)
                interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
                variables_html, vocab_list, vocab_dict = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
                if form.submit.data:
                    flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.', 'success', is_ajax=is_ajax)
                else:
                    flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Running in other tab.'), message_type='success', is_ajax=is_ajax)
            except DAError as foo:
                variables_html = None
                flash_message = flash_as_html(word('Saved at') + ' ' + the_time + '.  ' + word('Problem detected.'), message_type='error', is_ajax=is_ajax)
            if is_ajax:
                return jsonify(variables_html=variables_html, vocab_list=vocab_list, flash_message=flash_message)
        else:
            flash(word('Playground not saved.  There was an error.'), 'error')
    interview_path = None
    if the_file != '':
        with open(filename, 'rU') as fp:
            form.original_playground_name.data = the_file
            form.playground_name.data = the_file
            content = fp.read().decode('utf8')
            #if not form.playground_content.data:
                #form.playground_content.data = content
    if active_file != '':
        is_fictitious = False
        interview_path = 'docassemble.playground' + str(current_user.id) + ':' + active_file
        if is_default:
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        else:
            interview_source = docassemble.base.parse.interview_source_from_string(interview_path)
            interview_source.set_testing(True)
    else:
        is_fictitious = True
        active_file = 'test.yml'
        if form.playground_content.data:
            content = re.sub(r'\r', '', form.playground_content.data)
            interview_source = docassemble.base.parse.InterviewSourceString(content=content, directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
        else:
            interview_source = docassemble.base.parse.InterviewSourceString(content='', directory=playground.directory, path="docassemble.playground" + str(current_user.id) + ":" + active_file, testing=True)
    interview = interview_source.get_interview()
    interview_status = docassemble.base.parse.InterviewStatus(current_info=current_info(yaml='docassemble.playground' + str(current_user.id) + ':' + active_file, req=request, action=None))
    variables_html, vocab_list, vocab_dict = get_vars_in_use(interview, interview_status, debug_mode=debug_mode)
    pulldown_files = [x['name'] for x in files]
    define_examples()
    if is_fictitious or is_new or is_default:
        new_active_file = word('(New file)')
        if new_active_file not in pulldown_files:
            pulldown_files.insert(0, new_active_file)
        if is_fictitious:
            active_file = new_active_file
    ajax = """
var exampleData;
var originalFileName = """ + json.dumps(the_file) + """;
var isNew = """ + json.dumps(is_new) + """;
var vocab = """ + json.dumps(vocab_list) + """;
var existingFiles = """ + json.dumps(file_listing) + """;
var currentFile = """ + json.dumps(the_file) + """;
var attrs_showing = Object();

""" + variables_js() + """

""" + search_js() + """

function activateExample(id, scroll){
  var info = exampleData[id];
  $("#example-source").html(info['html']);
  $("#example-source-before").html(info['before_html']);
  $("#example-source-after").html(info['after_html']);
  $("#example-image-link").attr("href", info['interview']);
  $("#example-image").attr("src", info['image']);
  if (info['documentation'] != null){
    $("#example-documentation-link").attr("href", info['documentation']);
    $("#example-documentation-link").removeClass("example-hidden");
    //$("#example-documentation-link").slideUp();
  }
  else{
    $("#example-documentation-link").addClass("example-hidden");
    //$("#example-documentation-link").slideDown();
  }
  $(".example-list").addClass("example-hidden");
  $(".example-link").removeClass("example-active");
  $(".example-link").removeClass("active");
  $(".example-link").each(function(){
    if ($(this).data("example") == id){
      $(this).addClass("example-active");
      $(this).addClass("active");
      $(this).parents(".example-list").removeClass("example-hidden");
      if (scroll){
        setTimeout(function(){
          //console.log($(this).parents("li").last()[0].offsetTop);
          //console.log($(this).parents("li").last().parent()[0].offsetTop);
          $(".example-active").parents("ul").last().scrollTop($(".example-active").parents("li").last()[0].offsetTop);
        }, 0);
      }
      //$(this).parents(".example-list").slideDown();
    }
  });
  $("#hide-full-example").addClass("invisible");
  if (info['has_context']){
    $("#show-full-example").removeClass("invisible");
  }
  else{
    $("#show-full-example").addClass("invisible");
  }
  $("#example-source-before").addClass("invisible");
  $("#example-source-after").addClass("invisible");
}

function saveCallback(data){
  if ($("#flash").length){
    $("#flash").html(data.flash_message);
  }
  else{
    $("#main").prepend('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash">' + data.flash_message + '</div>');
  }
  if (data.vocab_list != null){
    vocab = data.vocab_list;
  }
  if (data.variables_html != null){
    $("#daplaygroundtable").html(data.variables_html);
    activateVariables();
    $("#form").trigger("reinitialize.areYouSure");
    $(function () {
      $('[data-toggle="popover"]').popover({trigger: 'focus', html: true});
    });
  }
}

$( document ).ready(function() {
  variablesReady();
  searchReady();
  $("#playground_name").on('change', function(){
    var newFileName = $(this).val();
    if ((!isNew) && newFileName == currentFile){
      return;
    }
    for (var i = 0; i < existingFiles.length; i++){
      if (newFileName == existingFiles[i] || newFileName + '.yml' == existingFiles[i]){
        alert(""" + json.dumps(word("Warning: a file by that name already exists.  If you save, you will overwrite it.")) + """);
        return;
      }
    }
    return;
  });
  $("#daRun").click(function(event){
    if (originalFileName != $("#playground_name").val()){
      $("#form button[name='submit']").click();
      event.preventDefault();
      return false;
    }
    daCodeMirror.save();
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&run=Save+and+Run&ajax=1',
      success: function(data){
        saveCallback(data);
      },
      dataType: 'json'
    });
    //event.preventDefault();
    return true;
  });
  $("#form button[name='submit']").click(function(event){
    daCodeMirror.save();
    if (isNew == "True" || originalFileName != $("#playground_name").val() || $("#playground_name").val().trim() == ""){
      return true;
    }
    $.ajax({
      type: "POST",
      url: """ + '"' + url_for('playground_page') + '"' + """,
      data: $("#form").serialize() + '&submit=Save&ajax=1',
      success: function(data){
        saveCallback(data);
        setTimeout(function(){
          $("#flash .alert-success").hide(300, function(){
            $(self).remove();
          });
        }, 3000);
      },
      dataType: 'json'
    });
    event.preventDefault();
    return false;
  });

  $(".example-link").on("click", function(){
    var id = $(this).data("example");
    activateExample(id, false);
  });

  $(".example-copy").on("click", function(event){
    if (daCodeMirror.somethingSelected()){
      daCodeMirror.replaceSelection("");
    }
    var id = $(".example-active").data("example");
    var curPos = daCodeMirror.getCursor();
    var notFound = 1;
    var insertLine = daCodeMirror.lastLine();
    daCodeMirror.eachLine(curPos.line, insertLine, function(line){
      if (notFound){
        if (line.text.substring(0, 3) == "---" || line.text.substring(0, 3) == "..."){
          insertLine = daCodeMirror.getLineNumber(line)
          //console.log("Found break at line number " + insertLine)
          notFound = 0;
        }
      }
    });
    if (notFound){
      daCodeMirror.setSelection({'line': insertLine, 'ch': null});
      daCodeMirror.replaceSelection("\\n---\\n" + exampleData[id]['source'] + "\\n", "around");
    }
    else{
      daCodeMirror.setSelection({'line': insertLine, 'ch': 0});
      daCodeMirror.replaceSelection("---\\n" + exampleData[id]['source'] + "\\n", "around");
    }
    daCodeMirror.focus();
    event.preventDefault();
    return false;
  });

  $(".example-heading").on("click", function(){
    var list = $(this).parent().children("ul").first();
    if (list != null){
      if (!list.hasClass("example-hidden")){
        return;
      }
      $(".example-list").addClass("example-hidden");
      //$(".example-list").slideUp();
      var new_link = $(this).parent().find("a.example-link").first();
      if (new_link.length){
        var id = new_link.data("example");
        activateExample(id, true);
      }
    }
  });

  activatePopovers();

  $("#show-full-example").on("click", function(){
    var id = $(".example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("invisible");
    $("#hide-full-example").removeClass("invisible");
    $("#example-source-before").removeClass("invisible");
    $("#example-source-after").removeClass("invisible");
  });

  $("#hide-full-example").on("click", function(){
    var id = $(".example-active").data("example");
    var info = exampleData[id];
    $(this).addClass("invisible");
    $("#show-full-example").removeClass("invisible");
    $("#example-source-before").addClass("invisible");
    $("#example-source-after").addClass("invisible");
  });
  if ($("#playground_name").val().length > 0){
    daCodeMirror.focus();
  }
  else{
    $("#playground_name").focus()
  }
  activateVariables();
  updateRunLink();
  origPosition = daCodeMirror.getCursor();
});
"""
    if len(files):
        any_files = True
    else:
        any_files = False
    cm_setup = """
    <script>
      var word_re = /[\w$]+/
      $( document ).ready(function(){
        CodeMirror.registerHelper("hint", "yaml", function(editor, options){
          var cur = editor.getCursor(), curLine = editor.getLine(cur.line);
          var end = cur.ch, start = end;
          while (start && word_re.test(curLine.charAt(start - 1))) --start;
          var curWord = start != end && curLine.slice(start, end);
          var list = [];
          if (curWord){
            var n = vocab.length;
            for (var i = 0; i < n; ++i){
              if (vocab[i].indexOf(curWord) == 0){
                list.push(vocab[i]);
              }
            }
          }
          return {list: list, from: CodeMirror.Pos(cur.line, start), to: CodeMirror.Pos(cur.line, end)};
        });""" + upload_js() + """
      });
    </script>"""
    if keymap:
        kbOpt = 'keyMap: "' + keymap + '", cursorBlinkRate: 0, '
        kbLoad = '<script src="' + url_for('static', filename="codemirror/keymap/" + keymap + ".js") + '"></script>\n    '
    else:
        kbOpt = ''
        kbLoad = ''
    return render_template('pages/playground.html', version_warning=None, bodyclass='adminbody', use_gd=use_gd, use_od=use_od, userid=current_user.id, page_title=word("Playground"), tab_title=word("Playground"), extra_css=Markup('\n    <link href="' + url_for('static', filename='codemirror/lib/codemirror.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/search/matchesonscrollbar.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/scroll/simplescrollbars.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='codemirror/addon/hint/show-hint.css') + '" rel="stylesheet">\n    <link href="' + url_for('static', filename='app/pygments.css') + '" rel="stylesheet">'), extra_js=Markup('\n    <script src="' + url_for('static', filename="areyousure/jquery.are-you-sure.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/lib/codemirror.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/searchcursor.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/scroll/annotatescrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/search/matchesonscrollbar.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/edit/matchbrackets.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/addon/hint/show-hint.js") + '"></script>\n    <script src="' + url_for('static', filename="codemirror/mode/yaml/yaml.js") + '"></script>\n    ' + kbLoad + '<script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>' + cm_setup + '\n    <script>\n      $("#daDelete").click(function(event){if(!confirm("' + word("Are you sure that you want to delete this playground file?") + '")){event.preventDefault();}});\n      daTextArea = document.getElementById("playground_content");\n      var daCodeMirror = CodeMirror.fromTextArea(daTextArea, {specialChars: /[\u00a0\u0000-\u001f\u007f-\u009f\u00ad\u061c\u200b-\u200f\u2028\u2029\ufeff]/, mode: "yaml", ' + kbOpt + 'tabSize: 2, tabindex: 70, autofocus: false, lineNumbers: true, matchBrackets: true});\n      $(window).bind("beforeunload", function(){daCodeMirror.save(); $("#form").trigger("checkform.areYouSure");});\n      $("#form").areYouSure(' + json.dumps({'message': word("There are unsaved changes.  Are you sure you wish to leave this page?")}) + ');\n      $("#form").bind("submit", function(){daCodeMirror.save(); $("#form").trigger("reinitialize.areYouSure"); return true;});\n      daCodeMirror.setSize(null, null);\n      daCodeMirror.setOption("extraKeys", { Tab: function(cm) { var spaces = Array(cm.getOption("indentUnit") + 1).join(" "); cm.replaceSelection(spaces); }, "Ctrl-Space": "autocomplete" });\n      daCodeMirror.setOption("coverGutterNextToScrollbar", true);\n' + indent_by(ajax, 6) + '\n      exampleData = JSON.parse(atob("' + pg_ex['encoded_data_dict'] + '"));\n      activateExample("' + str(pg_ex['pg_first_id'][0]) + '", false);\n    </script>'), form=form, fileform=fileform, files=files, any_files=any_files, pulldown_files=pulldown_files, current_file=the_file, active_file=active_file, content=content, variables_html=Markup(variables_html), example_html=pg_ex['encoded_example_html'], interview_path=interview_path, is_new=str(is_new)), 200

# nameInfo = ' + str(json.dumps(vars_in_use['name_info'])) + ';

# def mydump(data_dict):
#     output = ""
#     for key, val in data_dict.iteritems():
#         output += "      exampleData[" + str(repr(key)) + "] = " + str(json.dumps(val)) + "\n"
#     return output

# @app.route('/packages', methods=['GET', 'POST'])
# @login_required
# @roles_required(['admin', 'developer'])
# def package_page():
#     if request.method == 'GET' and needs_to_change_password():
#         return redirect(url_for('user.change_password', next=url_for('interview_list')))
#     return render_template('pages/packages.html', version_warning=version_warning, bodyclass='adminbody', tab_title=word("Package Management"), page_title=word("Package Management")), 200

@app.errorhandler(404)
def page_not_found_error(the_error):
    return render_template('pages/404.html'), 404

@app.errorhandler(Exception)
def server_error(the_error):
    if hasattr(the_error, 'interview') and the_error.interview.debug and hasattr(the_error, 'interview_status'):
        the_history = get_history(the_error.interview, the_error.interview_status)
    else:
        the_history = None
    the_vars = None
    if isinstance(the_error, DAError):
        errmess = unicode(the_error)
        the_trace = None
        logmessage(errmess)
    elif isinstance(the_error, TemplateError):
        errmess = unicode(the_error)
        # if hasattr(the_error, 'lineno') and the_error.lineno is not None:
        #     errmess += "; lineno: " + unicode(the_error.lineno)
        if hasattr(the_error, 'name') and the_error.name is not None:
            errmess += "\nName: " + unicode(the_error.name)
        if hasattr(the_error, 'filename') and the_error.filename is not None:
            errmess += "\nFilename: " + unicode(the_error.filename)
        if hasattr(the_error, 'docx_context'):
            errmess += "\n\nContext:\n" + "\n".join(map(lambda x: "  " + x, the_error.docx_context))
        the_trace = traceback.format_exc()
        try:
            logmessage(errmess)
        except:
            logmessage("Could not log the error message")
    else:
        errmess = unicode(type(the_error).__name__) + ": " + unicode(the_error)
        if hasattr(the_error, 'traceback'):
            the_trace = the_error.traceback
        else:
            the_trace = traceback.format_exc()
        if hasattr(the_error, 'da_line_with_error'):
            errmess += "\nIn line: " + unicode(the_error.da_line_with_error)
        logmessage(the_trace)
    if isinstance(the_error, DAError):
        error_code = the_error.error_code
    else:
        error_code = 501
    if hasattr(the_error, 'user_dict'):
        the_vars = the_error.user_dict
    if hasattr(the_error, 'interview'):
        special_error_markdown = the_error.interview.consolidated_metadata.get('error help', None)
    else:
        special_error_markdown = None
    if special_error_markdown is None:
        special_error_markdown = daconfig.get('error help', None)
    if special_error_markdown is not None:
        special_error_html = docassemble.base.util.markdown_to_html(special_error_markdown)
    else:
        special_error_html = None
    flask_logtext = []
    if os.path.exists(LOGFILE):
        with open(LOGFILE) as the_file:
            for line in the_file:
                if re.match('Exception', line):
                    flask_logtext = []
                flask_logtext.append(line)
    orig_errmess = errmess
    #errmess = the_error.__class__.__name__ + ": " + noquote(errmess)
    errmess = noquote(errmess)
    if re.search(r'\n', errmess):
        errmess = '<pre>' + errmess + '</pre>'
    else:
        errmess = '<blockquote class="blockquote">' + errmess + '</blockquote>'
    script = """
    <script>
      var daMessageLog = JSON.parse(atob(""" + json.dumps(safeid(json.dumps(docassemble.base.functions.get_message_log()))) + """));
      function flash(message, priority){
        if (priority == null){
          priority = 'info'
        }
        if (!$("#flash").length){
          $("#dabody").append('<div class="topcenter col-centered col-sm-7 col-md-6 col-lg-5" id="flash"></div>');
        }
        $("#flash").append('<div class="alert alert-' + priority + ' alert-interlocutory"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>');
        if (priority == 'success'){
          setTimeout(function(){
            $("#flash .alert-success").hide(300, function(){
              $(self).remove();
            });
          }, 3000);
        }
      }
      function showNotifications(){
        var n = daMessageLog.length;
        for (var i = 0; i < n; i++){
          var message = daMessageLog[i];
          if (message.priority == 'console'){
            console.log(message.message);
          }
          else if (message.priority == 'success' || message.priority == 'warning' || message.priority == 'danger' || message.priority == 'secondary' || message.priority == 'info' || message.priority == 'secondary' || message.priority == 'dark' || message.priority == 'light' || message.priority == 'primary'){
            flash(message.message, message.priority);
          }
          else{
            flash(message.message, 'info');
          }
        }
      }
      $( document ).ready(function() {
        showNotifications();
      });
    </script>"""
    error_notification(the_error, message=errmess, history=the_history, trace=the_trace, the_request=request, the_vars=the_vars)
    return render_template('pages/501.html', version_warning=None, tab_title=word("Error"), page_title=word("Error"), error=errmess, historytext=unicode(the_history), logtext=unicode(the_trace), extra_js=Markup(script), special_error=special_error_html), error_code
    #return render_template('pages/501.html', version_warning=None, tab_title=word("Error"), page_title=word("Error"), error=errmess, historytext=None, logtext=str(the_trace)), error_code

# @app.route('/testpost', methods=['GET', 'POST'])
# def test_post():
#     errmess = "Hello, " + str(request.method) + "!"
#     is_redir = request.args.get('redir', None)
#     if is_redir or request.method == 'GET':
#         return render_template('pages/testpost.html', error=errmess), 200
#     newargs = dict(request.args)
#     newargs['redir'] = '1'
#     logtext = url_for('test_post', **newargs)
#     #return render_template('pages/testpost.html', error=errmess, logtext=logtext), 200
#     return redirect(logtext, code=307)

@app.route('/packagestatic/<package>/<filename>', methods=['GET'])
def package_static(package, filename):
    if package == 'fonts':
        return redirect(url_for('static', filename='bootstrap/fonts/' + filename))
    try:
        filename = re.sub(r'^\.+', '', filename)
        filename = re.sub(r'\/\.+', '\/', filename)
        the_file = docassemble.base.functions.package_data_filename(str(package) + ':data/static/' + str(filename))
    except:
        abort(404)
    if the_file is None:
        abort(404)
    extension, mimetype = get_ext_and_mimetype(the_file)
    response = send_file(the_file, mimetype=str(mimetype))
    return(response)

# @app.route('/twiliotest', methods=['GET', 'POST'])
# def twilio_test():
#     account_sid = "ACfad8e668b5f9e15d499ab823523b9358"
#     auth_token = "86549c9a407b25d32f21c758e7b09546"
#     application_sid = "AP67affb53323193b8e2af0872aad387ad"
#     capability = TwilioCapability(account_sid, auth_token)
#     capability.allow_client_outgoing(application_sid)
#     token = capability.generate()
#     return render_template('pages/twiliotest.html', token=token)

@app.route('/logfile/<filename>', methods=['GET'])
@login_required
@roles_required(['admin', 'developer'])
def logfile(filename):
    if LOGSERVER is None:
        the_file = os.path.join(LOG_DIRECTORY, filename)
        if not os.path.isfile(the_file):
            abort(404)
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8080', "GET")
        the_file, headers = urllib.urlretrieve("http://" + LOGSERVER + ':8080/' + urllib.quote(filename))
    response = send_file(the_file, as_attachment=True, mimetype='text/plain', attachment_filename=filename, cache_timeout=0)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return(response)

@app.route('/logs', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def logs():
    form = LogForm(request.form)
    the_file = request.args.get('file', None)
    default_filter_string = ''
    if request.method == 'POST' and form.file_name.data:
        the_file = form.file_name.data
    if the_file is not None and (the_file.startswith('.') or the_file.startswith('/') or the_file == ''):
        the_file = None
    if LOGSERVER is None:
        call_sync()
        files = sorted([f for f in os.listdir(LOG_DIRECTORY) if os.path.isfile(os.path.join(LOG_DIRECTORY, f))])
        if the_file is None and len(files):
            if 'docassemble.log' in files:
                the_file = 'docassemble.log'
            else:
                the_file = files[0]
        if the_file is not None:
            filename = os.path.join(LOG_DIRECTORY, the_file)
    else:
        h = httplib2.Http()
        resp, content = h.request("http://" + LOGSERVER + ':8080', "GET")
        if int(resp['status']) >= 200 and int(resp['status']) < 300:
            files = [f for f in content.split("\n") if f != '' and f is not None]
        else:
            abort(404)
        if len(files):
            if the_file is None:
                the_file = files[0]
            filename, headers = urllib.urlretrieve("http://" + LOGSERVER + ':8080/' + urllib.quote(the_file))
    if not os.path.isfile(filename):
        flash(word("The file you requested does not exist."), 'error')
        if len(files):
            the_file = files[0]
            filename = os.path.join(LOG_DIRECTORY, files[0])
    if len(files):
        if request.method == 'POST' and form.submit.data and form.filter_string.data:
            default_filter_string = form.filter_string.data
            reg_exp = re.compile(form.filter_string.data)
            temp_file = tempfile.NamedTemporaryFile()
            with open(filename, 'rU') as fp:
                for line in fp:
                    if reg_exp.search(line):
                        temp_file.write(line)
            lines = tailer.tail(temp_file, 30)
            temp_file.close()
        else:
            lines = tailer.tail(open(filename), 30)
        content = "\n".join(map(lambda x: x.decode('utf8'), lines))
    else:
        content = "No log files available"
    return render_template('pages/logs.html', version_warning=version_warning, bodyclass='adminbody', tab_title=word("Logs"), page_title=word("Logs"), form=form, files=files, current_file=the_file, content=content, default_filter_string=default_filter_string), 200

@app.route('/reqdev', methods=['GET', 'POST'])
@login_required
def request_developer():
    from docassemble.webapp.users.forms import RequestDeveloperForm
    form = RequestDeveloperForm(request.form)
    recipients = list()
    if request.method == 'POST':
        for user in UserModel.query.filter_by(active=True).all():
            for role in user.roles:
                if role.name == 'admin':
                    recipients.append(user.email)
        url = request.base_url
        url = re.sub(r'^(https?://[^/]+)/.*', r'\1', url)
        body = "User " + str(current_user.email) + " (" + str(current_user.id) + ") has requested developer privileges.\n\n"
        if form.reason.data:
            body += "Reason given: " + str(form.reason.data) + "\n\n"
        body += "Go to " + str(url) + url_for('edit_user_profile_page', id=current_user.id) + " to change the user's privileges."
        msg = Message("Request for developer account from " + str(current_user.email), recipients=recipients, body=body)
        if not len(recipients):
            flash(word('No administrators could be found.'), 'error')
        else:
            try:
                da_send_mail(msg)
                flash(word('Your request was submitted.'), 'success')
            except:
                flash(word('We were unable to submit your request.'), 'error')
        return redirect(url_for('interview_list'))
    return render_template('users/request_developer.html', version_warning=None, bodyclass='adminbody', tab_title=word("Developer Access"), page_title=word("Developer Access"), form=form)

def docx_variable_fix(variable):
    variable = re.sub(r'\\', '', variable)
    variable = re.sub(r'^([A-Za-z\_][A-Za-z\_0-9]*).*', r'\1', variable)
    return variable

@app.route('/utilities', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer'])
def utilities():
    form = Utilities(request.form)
    fields_output = None
    word_box = None
    uses_null = False
    file_type = None
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('utilities')))
    if request.method == 'POST':
        if 'language' in request.form:
            language = request.form['language']
            result = dict()
            result[language] = dict()
            existing = docassemble.base.functions.word_collection.get(language, dict())
            if 'google' in daconfig and 'api key' in daconfig['google'] and daconfig['google']['api key']:
                from googleapiclient.discovery import build
                try:
                    service = build('translate', 'v2',
                                    developerKey=daconfig['google']['api key'])
                    use_google_translate = True
                except:
                    logmessage("utilities: attempt to call Google Translate failed")
                    use_google_translate = False
            else:
                use_google_translate = False
            words_to_translate = list()
            for the_word in base_words:
                if the_word in existing and existing[the_word] is not None:
                    result[language][the_word] = existing[the_word]
                    continue
                words_to_translate.append(the_word)
            chunk_limit = daconfig.get('google translate words at a time', 20)
            chunks = list()
            interim_list = list()
            while len(words_to_translate):
                the_word = words_to_translate.pop(0)
                interim_list.append(the_word)
                if len(interim_list) >= chunk_limit:
                    chunks.append(interim_list)
                    interim_list = list()
            if len(interim_list):
                chunks.append(interim_list)
            for chunk in chunks:
                if use_google_translate:
                    try:
                        resp = service.translations().list(
                            source='en',
                            target=language,
                            q=chunk
                        ).execute()
                    except Exception as errstr:
                        logmessage("utilities: translation failed: " + str(errstr))
                        resp = None
                    if type(resp) is dict and u'translations' in resp and type(resp[u'translations']) is list and len(resp[u'translations']) == len(chunk):
                        for index in range(len(chunk)):
                            if type(resp[u'translations'][index]) is dict and 'translatedText' in resp[u'translations'][index]:
                                result[language][chunk[index]] = re.sub(r'&#39;', r"'", resp['translations'][index]['translatedText'])
                            else:
                                result[language][chunk[index]] = 'XYZNULLXYZ'
                                uses_null = True
                    else:
                        result[language][the_word] = 'XYZNULLXYZ'
                        uses_null = True
                else:
                    for the_word in chunk:
                        result[language][the_word] = 'XYZNULLXYZ'
                    uses_null = True
            word_box = ruamel.yaml.safe_dump(result, default_flow_style=False, default_style = '"', allow_unicode=True, width=1000).decode('utf8')
            word_box = re.sub(r'"XYZNULLXYZ"', r'Null', word_box)
        if 'pdfdocxfile' in request.files and request.files['pdfdocxfile'].filename:
            filename = secure_filename(request.files['pdfdocxfile'].filename)
            extension, mimetype = get_ext_and_mimetype(filename)
            if mimetype == 'application/pdf':
                file_type = 'pdf'
                pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=True)
                the_file = request.files['pdfdocxfile']
                the_file.save(pdf_file.name)
                fields = docassemble.base.pdftk.read_fields(pdf_file.name)
                fields_seen = set()
                pdf_file.close()
                if fields is None:
                    fields_output = word("Error: no fields could be found in the file")
                else:
                    fields_output = "---\nquestion: " + word("Here is your document.") + "\nevent: " + 'some_event' + "\nattachment:" + "\n  - name: " + os.path.splitext(the_file.filename)[0] + "\n    filename: " + os.path.splitext(the_file.filename)[0] + "\n    pdf template file: " + re.sub(r'[^A-Za-z0-9\-\_\. ]+', '_', the_file.filename) + "\n    fields:\n"
                    for field, default, pageno, rect, field_type in fields:
                        if field not in fields_seen:
                            fields_output += '      - "' + unicode(field) + '": ' + unicode(default) + "\n"
                            fields_seen.add(field)
                    fields_output += "---"
            elif mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                file_type = 'docx'
                docx_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".docx", delete=True)
                the_file = request.files['pdfdocxfile']
                the_file.save(docx_file.name)
                result_file = word_to_markdown(docx_file.name, 'docx')
                docx_file.close()
                if result_file is None:
                    fields_output = word("Error: no fields could be found in the file")
                else:
                    with open(result_file.name, 'rU') as fp:
                        result = fp.read().decode('utf8')
                    fields = set()
                    for variable in re.findall(r'{{ *([^\} ]+) *}}', result):
                        fields.add(docx_variable_fix(variable))
                    for variable in re.findall(r'{%[a-z]* for [A-Za-z\_][A-Za-z0-9\_]* in *([^\} ]+) *%}', result):
                        fields.add(docx_variable_fix(variable))
                    if len(fields):
                        fields_output = "---\nquestion: " + word("Here is your document.") + "\nevent: " + 'some_event' + "\nattachment:" + "\n  - name: " + os.path.splitext(the_file.filename)[0] + "\n    filename: " + os.path.splitext(the_file.filename)[0] + "\n    docx template file: " + the_file.filename + "\n    fields:\n"
                        for field in fields:
                            fields_output += '      "' + field + '": ' + "Something\n"
                        fields_output += "---"
                    else:
                        fields_output = word("Error: no fields could be found in the file")
        if form.officeaddin_submit.data:
            resp = make_response(render_template('pages/officemanifest.xml', office_app_version=form.officeaddin_version.data, guid=str(uuid.uuid4())))
            resp.headers['Content-type'] = 'text/xml; charset=utf-8'
            resp.headers['Content-Disposition'] = 'attachment; filename="manifest.xml"'
            return resp
    extra_js = """
    <script>
      $('#pdfdocxfile').on('change', function(){
        var fileName = $(this).val();
        fileName = fileName.replace(/.*\\\\/, '');
        fileName = fileName.replace(/.*\\//, '');
        $(this).next('.custom-file-label').html(fileName);
      });
    </script>"""
    return render_template('pages/utilities.html', extra_js=Markup(extra_js), version_warning=version_warning, bodyclass='adminbody', tab_title=word("Utilities"), page_title=word("Utilities"), form=form, fields=fields_output, word_box=word_box, uses_null=uses_null, file_type=file_type, language_placeholder=word("Enter an ISO-639-1 language code (e.g., es, fr, it)"))

# @app.route('/save', methods=['GET', 'POST'])
# def save_for_later():
#     if current_user.is_authenticated and not current_user.is_anonymous:
#         return render_template('pages/save_for_later.html', interview=sdf)
#     secret = request.cookies.get('secret', None)

@app.route('/after_reset', methods=['GET', 'POST'])
def after_reset():
    #logmessage("after_reset")
    response = redirect(url_for('user.login'))
    if 'newsecret' in session:
        #logmessage("after_reset: fixing cookie")
        response.set_cookie('secret', session['newsecret'])
        del session['newsecret']
    return response

# @app.before_request
# def reset_thread_local():
#     docassemble.base.functions.reset_thread_local()

# @app.after_request
# def remove_temporary_files(response):
#     docassemble.base.functions.close_files()
#     return response

def needs_to_change_password():
    if not current_user.has_role('admin'):
        return False
    #logmessage("needs_to_change_password: starting")
    if app.user_manager.verify_password('password', current_user):
        flash(word("Your password is insecure and needs to be changed"), "warning")
        return True
    #logmessage("needs_to_change_password: ending")
    return False

def fix_group_id(the_package, the_file, the_group_id):
    if the_package == '_global':
        group_id_to_use = the_group_id
    else:
        group_id_to_use = the_package
        if re.search(r'^data/', the_file):
            group_id_to_use += ':' + the_file
        else:
            group_id_to_use += ':data/sources/ml-' + the_file + '.json'
        group_id_to_use += ':' + the_group_id
    return group_id_to_use

def ensure_training_loaded(interview):
    # parts = yaml_filename.split(':')
    # if len(parts) != 2:
    #     logmessage("ensure_training_loaded: could not read yaml_filename " + str(yaml_filename))
    #     return
    # source_filename = parts[0] + ':data/sources/ml-' + re.sub(r'\.ya?ml$', '', re.sub(r'.*/', '', parts[1])) + '.json'
    #logmessage("Source filename is " + source_filename)
    source_filename = interview.get_ml_store()
    parts = source_filename.split(':')
    if len(parts) == 3 and parts[0].startswith('docassemble.') and re.match(r'data/sources/.*\.json', parts[1]):
        the_file = docassemble.base.functions.package_data_filename(source_filename)
        if the_file is not None:
            record = db.session.query(MachineLearning.group_id).filter(MachineLearning.group_id.like(source_filename + ':%')).first()
            if record is None:
                if os.path.isfile(the_file):
                    with open(the_file, 'rU') as fp:
                        content = fp.read().decode('utf8')
                    if len(content):
                        try:
                            href = json.loads(content)
                            if type(href) is dict:
                                nowtime = datetime.datetime.utcnow()
                                for group_id, train_list in href.iteritems:
                                    if type(train_list) is list:
                                        for entry in train_list:
                                            if 'independent' in entry:
                                                new_entry = MachineLearning(group_id=source_filename + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(entry.get('dependent', None)), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None))
                                                db.session.add(new_entry)
                                db.session.commit()
                            else:
                                logmessage("ensure_training_loaded: source filename " + source_filename + " not used because it did not contain a dict")
                        except:
                            logmessage("ensure_training_loaded: source filename " + source_filename + " not used because it did not contain valid JSON")
                    else:
                        logmessage("ensure_training_loaded: source filename " + source_filename + " not used because its content was empty")
                else:
                    logmessage("ensure_training_loaded: source filename " + source_filename + " not used because it did not exist")
            else:
                logmessage("ensure_training_loaded: source filename " + source_filename + " not used because training data existed")
        else:
            logmessage("ensure_training_loaded: source filename " + source_filename + " did not exist")
    else:
        logmessage("ensure_training_loaded: source filename " + source_filename + " was not part of a package")
        
def get_corresponding_interview(the_package, the_file):
    #logmessage("get_corresponding_interview: " + the_package + " " + the_file)
    interview = None
    if re.match(r'docassemble.playground[0-9]+', the_package):
        separator = ':'
    else:
        separator = ':data/questions/'
    for interview_file in (the_package + separator + the_file + '.yml', the_package + separator + the_file + '.yaml', the_package + separator + 'examples/' + the_file + '.yml'):
        #logmessage("Looking for " + interview_file)
        try:
            interview = docassemble.base.interview_cache.get_interview(interview_file)
            break
        except Exception as the_err:
            #logmessage("There was an exception looking for " + interview_file + ": " + str(the_err))
            continue
    return interview

def ml_prefix(the_package, the_file):
    the_prefix = the_package
    if re.search(r'^data/', the_file):
        the_prefix += ':' + the_file
    else:
        the_prefix += ':data/sources/ml-' + the_file + '.json'
    return the_prefix

@app.route('/train', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'trainer'])
def train():
    the_package = request.args.get('package', None)
    the_file = request.args.get('file', None)
    the_group_id = request.args.get('group_id', None)
    show_all = int(request.args.get('show_all', 0))
    form = TrainingForm(request.form)
    uploadform = TrainingUploadForm(request.form)
    if request.method == 'POST' and the_package is not None and the_file is not None:
        if the_package == '_global':
            the_prefix = ''
        else:
            the_prefix = ml_prefix(the_package, the_file)
        json_file = None
        if the_package != '_global' and uploadform.usepackage.data == 'yes':
            the_file = docassemble.base.functions.package_data_filename(the_prefix)
            if the_file is None or not os.path.isfile(the_file):
                flash(word("Error reading JSON file from package.  File did not exist."), 'error')
                return redirect(url_for('train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
            json_file = open(the_file, 'rU')
        if uploadform.usepackage.data == 'no' and 'jsonfile' in request.files and request.files['jsonfile'].filename:
            json_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".json")
            request.files['jsonfile'].save(json_file.name)
            json_file.seek(0)
        if json_file is not None:
            try:
                href = json.load(json_file)
            except:
                flash(word("Error reading JSON file.  Not a valid JSON file."), 'error')
                return redirect(url_for('train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
            json_file.close()
            if type(href) is not dict:
                flash(word("Error reading JSON file.  The JSON file needs to contain a dictionary at the root level."), 'error')
                return redirect(url_for('train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
            nowtime = datetime.datetime.utcnow()
            for group_id, train_list in href.iteritems():
                if type(train_list) is not list:
                    logmessage("train: could not import part of JSON file.  Items in dictionary must be lists.")
                    continue
                if uploadform.importtype.data == 'replace':
                    MachineLearning.query.filter_by(group_id=the_prefix + ':' + group_id).delete()
                    db.session.commit()
                    for entry in train_list:
                        if 'independent' in entry:
                            new_entry = MachineLearning(group_id=the_prefix + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(entry.get('dependent', None)), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None))
                            db.session.add(new_entry)
                elif uploadform.importtype.data == 'merge':
                    indep_in_use = set()
                    for record in MachineLearning.query.filter_by(group_id=the_prefix + ':' + group_id).all():
                        indep_in_use.add(pickle.loads(codecs.decode(record.independent, 'base64')))
                    for entry in train_list:
                        if 'independent' in entry and entry['independent'] not in indep_in_use:
                            new_entry = MachineLearning(group_id=the_prefix + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(entry.get('dependent', None)), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None))
                            db.session.add(new_entry)
            db.session.commit()
            flash(word("Training data were successfully imported."), 'success')
            return redirect(url_for('train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
        if form.cancel.data:
            return redirect(url_for('train', package=the_package, file=the_file, show_all=show_all))
        if form.submit.data:
            group_id_to_use = fix_group_id(the_package, the_file, the_group_id)
            post_data = request.form.copy()
            deleted = set()
            for key, val in post_data.iteritems():
                m = re.match(r'delete([0-9]+)', key)
                if not m:
                    continue
                entry_id = int(m.group(1))
                model = docassemble.base.util.SimpleTextMachineLearner(group_id=group_id_to_use)
                model.delete_by_id(entry_id)
                deleted.add('dependent' + m.group(1))
            for key in deleted:
                if key in post_data:
                    del post_data[key]
            for key, val in post_data.iteritems():
                m = re.match(r'dependent([0-9]+)', key)
                if not m:
                    continue
                orig_key = 'original' + m.group(1)
                delete_key = 'delete' + m.group(1)
                if orig_key in post_data and post_data[orig_key] != val and val != '':
                    entry_id = int(m.group(1))
                    model = docassemble.base.util.SimpleTextMachineLearner(group_id=group_id_to_use)
                    model.set_dependent_by_id(entry_id, val)
            if post_data.get('newindependent', '') != '':
                model = docassemble.base.util.SimpleTextMachineLearner(group_id=group_id_to_use)
                if post_data.get('newdependent', '') != '':
                    model.add_to_training_set(post_data['newindependent'], post_data['newdependent'])
                else:
                    model.save_for_classification(post_data['newindependent'])
            return redirect(url_for('train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
    if show_all:
        show_all = 1
        show_cond = MachineLearning.id != None
    else:
        show_all = 0
        show_cond = MachineLearning.dependent == None
    package_list = dict()
    file_list = dict()
    group_id_list = dict()
    entry_list = list()
    if current_user.has_role('admin', 'developer'):
        playground_package = 'docassemble.playground' + str(current_user.id)
    else:
        playground_package = None
    if the_package is None:
        for record in db.session.query(MachineLearning.group_id, db.func.count(MachineLearning.id).label('count')).filter(show_cond).group_by(MachineLearning.group_id):
            group_id = record.group_id
            parts = group_id.split(':')
            if is_package_ml(parts):
                if parts[0] not in package_list:
                    package_list[parts[0]] = 0
                package_list[parts[0]] += record.count
            else:
                if '_global' not in package_list:
                    package_list['_global'] = 0
                package_list['_global'] += record.count
        if not show_all:
            for record in db.session.query(MachineLearning.group_id).group_by(MachineLearning.group_id):
                parts = record.group_id.split(':')
                if is_package_ml(parts):
                    if parts[0] not in package_list:
                        package_list[parts[0]] = 0
            if '_global' not in package_list:
                package_list['_global'] = 0
        if playground_package and playground_package not in package_list:
            package_list[playground_package] = 0
        package_list = [(x, package_list[x]) for x in sorted(package_list)]
        return render_template('pages/train.html', version_warning=version_warning, bodyclass='adminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_file=the_file, the_group_id=the_group_id, package_list=package_list, file_list=file_list, group_id_list=group_id_list, entry_list=entry_list, show_all=show_all, show_package_list=True, playground_package=playground_package)
    if playground_package and the_package == playground_package:
        the_package_display = word("My Playground")
    else:
        the_package_display = the_package
    if the_file is None:
        file_list = dict()
        for record in db.session.query(MachineLearning.group_id, db.func.count(MachineLearning.id).label('count')).filter(and_(MachineLearning.group_id.like(the_package + ':%'), show_cond)).group_by(MachineLearning.group_id):
            parts = record.group_id.split(':')
            #logmessage("Group id is " + str(parts))
            if not is_package_ml(parts):
                continue
            if re.match(r'data/sources/ml-.*\.json', parts[1]):
                parts[1] = re.sub(r'^data/sources/ml-|\.json$', '', parts[1])
            if parts[1] not in file_list:
                file_list[parts[1]] = 0
            file_list[parts[1]] += record.count
        if not show_all:
            for record in db.session.query(MachineLearning.group_id).filter(MachineLearning.group_id.like(the_package + ':%')).group_by(MachineLearning.group_id):
                parts = record.group_id.split(':')
                #logmessage("Other group id is " + str(parts))
                if not is_package_ml(parts):
                    continue
                if re.match(r'data/sources/ml-.*\.json', parts[1]):
                    parts[1] = re.sub(r'^data/sources/ml-|\.json$', '', parts[1])
                if parts[1] not in file_list:
                    file_list[parts[1]] = 0
        if playground_package and the_package == playground_package:
            area = SavedFile(current_user.id, fix=False, section='playgroundsources')
            for filename in area.list_of_files():
                #logmessage("hey file is " + str(filename))
                if re.match(r'ml-.*\.json', filename):
                    short_file_name = re.sub(r'^ml-|\.json$', '', filename)
                    if short_file_name not in file_list:
                        file_list[short_file_name] = 0
        file_list = [(x, file_list[x]) for x in sorted(file_list)]
        return render_template('pages/train.html', version_warning=version_warning, bodyclass='adminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_package_display=the_package_display, the_file=the_file, the_group_id=the_group_id, package_list=package_list, file_list=file_list, group_id_list=group_id_list, entry_list=entry_list, show_all=show_all, show_file_list=True)
    if the_group_id is None:
        the_prefix = ml_prefix(the_package, the_file)
        the_package_file = docassemble.base.functions.package_data_filename(the_prefix)
        if the_package_file is not None and os.path.isfile(the_package_file):
            package_file_available = True
        else:
            package_file_available = False
        if 'download' in request.args and request.args['download']:
            output = dict()
            if the_package == '_global':
                json_filename = 'ml-global.json'
                for record in db.session.query(MachineLearning.id, MachineLearning.group_id, MachineLearning.independent, MachineLearning.dependent, MachineLearning.key):
                    if is_package_ml(record.group_id.split(':')):
                        continue
                    if record.group_id not in output:
                        output[record.group_id] = list()
                    if record.dependent is None:
                        the_dependent = None
                    else:
                        the_dependent = pickle.loads(codecs.decode(record.dependent, 'base64'))
                    the_independent = pickle.loads(codecs.decode(record.independent, 'base64'))
                    try:
                        unicode(the_independent) + ""
                        unicode(the_dependent) + ""
                    except Exception as e:
                        logmessage("Bad record: id " + str(record.id) + " where error was " + str(e))
                        continue
                    the_entry = dict(independent=pickle.loads(codecs.decode(record.independent, 'base64')), dependent=the_dependent)
                    if record.key is not None:
                        the_entry['key'] = record.key
                    output[record.group_id].append(the_entry)
            else:
                json_filename = 'ml-' + the_file + '.json'
                prefix = ml_prefix(the_package, the_file)
                for record in db.session.query(MachineLearning.group_id, MachineLearning.independent, MachineLearning.dependent, MachineLearning.key).filter(MachineLearning.group_id.like(prefix + ':%')):
                    parts = record.group_id.split(':')
                    if not is_package_ml(parts):
                        continue
                    if parts[2] not in output:
                        output[parts[2]] = list()
                    if record.dependent is None:
                        the_dependent = None
                    else:
                        the_dependent = pickle.loads(codecs.decode(record.dependent, 'base64'))
                    the_entry = dict(independent=pickle.loads(codecs.decode(record.independent, 'base64')), dependent=the_dependent)
                    if record.key is not None:
                        the_entry['key'] = record.key
                    output[parts[2]].append(the_entry)
            if len(output):
                the_json_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".json", delete=False)
                with open(the_json_file.name, 'w') as fp:
                    json.dump(output, fp, sort_keys=True, indent=2)
                response = send_file(the_json_file, mimetype='application/json', as_attachment=True, attachment_filename=json_filename)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return(response)
            else:
                flash(word("No data existed in training set.  JSON file not created."), "error")
                return redirect(url_for('train', package=the_package, file=the_file, show_all=show_all))
        if the_package == '_global':
            for record in db.session.query(MachineLearning.group_id, db.func.count(MachineLearning.id).label('count')).filter(show_cond).group_by(MachineLearning.group_id):
                if is_package_ml(record.group_id.split(':')):
                    continue
                if record.group_id not in group_id_list:
                    group_id_list[record.group_id] = 0
                group_id_list[record.group_id] += record.count
            if not show_all:
                for record in db.session.query(MachineLearning.group_id).group_by(MachineLearning.group_id):
                    if is_package_ml(record.group_id.split(':')):
                        continue
                    if record.group_id not in group_id_list:
                        group_id_list[record.group_id] = 0
        else:
            the_prefix = ml_prefix(the_package, the_file)
            #logmessage("My prefix is " + the_prefix)
            for record in db.session.query(MachineLearning.group_id, db.func.count(MachineLearning.id).label('count')).filter(and_(MachineLearning.group_id.like(the_prefix + ':%'), show_cond)).group_by(MachineLearning.group_id):
                parts = record.group_id.split(':')
                if not is_package_ml(parts):
                    continue
                if parts[2] not in group_id_list:
                    group_id_list[parts[2]] = 0
                group_id_list[parts[2]] += record.count
            if not show_all:
                for record in db.session.query(MachineLearning.group_id).filter(MachineLearning.group_id.like(the_prefix + ':%')).group_by(MachineLearning.group_id):
                    parts = record.group_id.split(':')
                    if not is_package_ml(parts):
                        continue
                    if parts[2] not in group_id_list:
                        group_id_list[parts[2]] = 0
        if the_package != '_global' and not re.search(r'^data/', the_file):
            interview = get_corresponding_interview(the_package, the_file)
            if interview is not None and len(interview.mlfields):
                for saveas in interview.mlfields:
                    if 'ml_group' in interview.mlfields[saveas] and not interview.mlfields[saveas]['ml_group'].uses_mako:
                        the_saveas = interview.mlfields[saveas]['ml_group'].original_text
                    else:
                        the_saveas = saveas
                    if not re.search(r':', the_saveas):
                        if the_saveas not in group_id_list:
                            group_id_list[the_saveas] = 0
        group_id_list = [(x, group_id_list[x]) for x in sorted(group_id_list)]
        extra_js = """
    <script>
      $( document ).ready(function() {
        $("#showimport").click(function(e){
          $("#showimport").hide();
          $("#hideimport").show();
          $("#importcontrols").show('fast');
          e.preventDefault();
          return false;
        });
        $("#hideimport").click(function(e){
          $("#showimport").show();
          $("#hideimport").hide();
          $("#importcontrols").hide('fast');
          e.preventDefault();
          return false;
        });
        $("input[type=radio][name=usepackage]").on('change', function(e) {
          if ($(this).val() == 'no'){
            $("#uploadinput").show();
          }
          else{
            $("#uploadinput").hide();
          }
          e.preventDefault();
          return false;
        });
      });
    </script>"""        
        return render_template('pages/train.html', extra_js=Markup(extra_js), version_warning=version_warning, bodyclass='adminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_package_display=the_package_display, the_file=the_file, the_group_id=the_group_id, package_list=package_list, file_list=file_list, group_id_list=group_id_list, entry_list=entry_list, show_all=show_all, show_group_id_list=True, package_file_available=package_file_available, the_package_location=the_prefix, uploadform=uploadform)
    else:
        group_id_to_use = fix_group_id(the_package, the_file, the_group_id)
        model = docassemble.base.util.SimpleTextMachineLearner(group_id=group_id_to_use)
        for record in db.session.query(MachineLearning.id, MachineLearning.group_id, MachineLearning.key, MachineLearning.info, MachineLearning.independent, MachineLearning.dependent, MachineLearning.create_time, MachineLearning.modtime, MachineLearning.active).filter(and_(MachineLearning.group_id == group_id_to_use, show_cond)):
            new_entry = dict(id=record.id, group_id=record.group_id, key=record.key, independent=pickle.loads(codecs.decode(record.independent, 'base64')) if record.independent is not None else None, dependent=pickle.loads(codecs.decode(record.dependent, 'base64')) if record.dependent is not None else None, info=pickle.loads(codecs.decode(record.info, 'base64')) if record.info is not None else None, create_type=record.create_time, modtime=record.modtime, active=MachineLearning.active)
            if isinstance(new_entry['independent'], DADict) or type(new_entry['independent']) is dict:
                new_entry['independent_display'] = '<div class="mldatacontainer">' + '<br>'.join(['<span class="mldatakey">' + unicode(key) + '</span>: <span class="mldatavalue">' + unicode(val) + ' (' + str(val.__class__.__name__) + ')</span>' for key, val in new_entry['independent'].iteritems()]) + '</div>'
                new_entry['type'] = 'data'
            else:
                new_entry['type'] = 'text'
            if new_entry['dependent'] is None:
                new_entry['predictions'] = model.predict(new_entry['independent'], probabilities=True)
                if len(new_entry['predictions']) == 0:
                    new_entry['predictions'] = None
                elif len(new_entry['predictions']) > 10:
                    new_entry['predictions'] = new_entry['predictions'][0:10]
                if new_entry['predictions'] is not None:
                    new_entry['predictions'] = [(prediction, '%d%%' % (100.0*probability)) for prediction, probability in new_entry['predictions']]
            else:
                new_entry['predictions'] = None
            if new_entry['info'] is not None:
                if isinstance(new_entry['info'], DAFile):
                    image_file_list = [new_entry['info']]
                elif isinstance(new_entry['info'], DAFileList):
                    image_file_list = new_entry['info']
                else:
                    logmessage("train: info is not a DAFile or DAFileList")
                    continue
                new_entry['image_files'] = list()
                for image_file in image_file_list:
                    if not isinstance(image_file, DAFile):
                        logmessage("train: file is not a DAFile")
                        continue
                    if not image_file.ok:
                        logmessage("train: file does not have a number")
                        continue
                    if image_file.extension not in ('pdf', 'png', 'jpg', 'jpeg', 'gif'):
                        logmessage("train: file did not have a recognizable image type")
                        continue
                    doc_url = get_url_from_file_reference(image_file)
                    if image_file.extension == 'pdf':
                        image_url = get_url_from_file_reference(image_file, size="screen", page=1, ext='pdf')
                    else:
                        image_url = doc_url
                    new_entry['image_files'].append(dict(doc_url=doc_url, image_url=image_url))
            entry_list.append(new_entry)
        if len(entry_list) == 0:
            record = db.session.query(MachineLearning.independent).filter(and_(MachineLearning.group_id == group_id_to_use, MachineLearning.independent != None)).first()
            if record is not None:
                sample_indep = pickle.loads(codecs.decode(record.independent, 'base64'))
            else:
                sample_indep = None
        else:
            sample_indep = entry_list[0]['independent']
        if isinstance(sample_indep, DADict) or type(sample_indep) is dict:
            is_data = True
        else:
            is_data = False
        choices = dict()
        for record in db.session.query(MachineLearning.dependent, db.func.count(MachineLearning.id).label('count')).filter(and_(MachineLearning.group_id == group_id_to_use)).group_by(MachineLearning.dependent):
            #logmessage("There is a choice")
            if record.dependent is None:
                continue
            key = pickle.loads(codecs.decode(record.dependent, 'base64'))
            choices[key] = record.count
        if len(choices):
            #logmessage("There are choices")
            choices = [(x, choices[x]) for x in sorted(choices, key=operator.itemgetter(0), reverse=False)]
        else:
            #logmessage("There are no choices")
            choices = None
        extra_js = """
    <script>
      $( document ).ready(function(){
        $("button.prediction").click(function(){
          if (!($("#dependent" + $(this).data("id-number")).prop('disabled'))){
            $("#dependent" + $(this).data("id-number")).val($(this).data("prediction"));
          }
        });
        $("select.trainer").change(function(){
          var the_number = $(this).data("id-number");
          if (the_number == "newdependent"){
            $("#newdependent").val($(this).val());
          }
          else{
            $("#dependent" + the_number).val($(this).val());
          }
        });
        $("div.delete-observation input").change(function(){
          var the_number = $(this).data("id-number");
          if ($(this).is(':checked')){
            $("#dependent" + the_number).prop('disabled', true);
            $("#selector" + the_number).prop('disabled', true);
          }
          else{
            $("#dependent" + the_number).prop('disabled', false);
            $("#selector" + the_number).prop('disabled', false);
          }
        });
      });
    </script>"""
        return render_template('pages/train.html', extra_js=Markup(extra_js), form=form, version_warning=version_warning, bodyclass='adminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_package_display=the_package_display, the_file=the_file, the_group_id=the_group_id, entry_list=entry_list, choices=choices, show_all=show_all, show_entry_list=True, is_data=is_data)

def user_interviews(user_id=None, secret=None, exclude_invalid=True, action=None, filename=None, session=None, tag=None, include_dict=True):
    # logmessage("user_interviews: user_id is " + str(user_id) + " and secret is " + str(secret))
    if user_id is None and not in_celery and (current_user.is_anonymous or not current_user.has_role('admin', 'advocate')):
        raise Exception('user_interviews: only administrators and advocates can access information about other users')
    if user_id is not None and not in_celery and not current_user.is_anonymous and current_user.id != user_id and not current_user.has_role('admin', 'advocate'):
        raise Exception('user_interviews: only administrators and advocates can access information about other users')
    if action is not None and not current_user.has_role('admin', 'advocate'):
        if user_id is None:
            raise Exception("user_interviews: no user_id provided")
        the_user = get_person(int(user_id), dict())
        if the_user is None:
            raise Exception("user_interviews: user_id " + str(user_id) + " not valid")
    if action == 'delete_all':
        sessions_to_delete = set()
        if tag:
            for interview_info in user_interviews(user_id=user_id, secret=secret, tag=tag):
                sessions_to_delete.add((interview_info['session'], interview_info['filename'], interview_info['user_id']))
        else:
            if user_id is None:
                if filename is None:
                    interview_query = db.session.query(UserDict.filename, UserDict.key).group_by(UserDict.filename, UserDict.key)
                else:
                    interview_query = db.session.query(UserDict.filename, UserDict.key).filter(UserDict.filename == filename).group_by(UserDict.filename, UserDict.key)
                for interview_info in interview_query:
                    sessions_to_delete.add((interview_info.key, interview_info.filename, None))
            else:
                if filename is None:
                    interview_query = db.session.query(UserDictKeys.filename, UserDictKeys.key).filter(UserDictKeys.user_id == user_id).group_by(UserDictKeys.filename, UserDictKeys.key)
                else:
                    interview_query = db.session.query(UserDictKeys.filename, UserDictKeys.key).filter(UserDictKeys.user_id == user_id, UserDictKeys.filename == filename).group_by(UserDictKeys.filename, UserDictKeys.key)
                for interview_info in interview_query:
                    sessions_to_delete.add((interview_info.key, interview_info.filename, user_id))
            if user_id is not None:
                if filename is None:
                    interview_query = db.session.query(UserDict.filename, UserDict.key).filter(UserDict.user_id == user_id).group_by(UserDict.filename, UserDict.key)
                else:
                    interview_query = db.session.query(UserDict.filename, UserDict.key).filter(UserDict.user_id == user_id, UserDict.filename == filename).group_by(UserDict.filename, UserDict.key)
                for interview_info in interview_query:
                    sessions_to_delete.add((interview_info.key, interview_info.filename, user_id))
        logmessage("Deleting " + str(len(sessions_to_delete)) + " interviews")
        if len(sessions_to_delete):
            for session_id, yaml_filename, the_user_id in sessions_to_delete:
                manual_checkout(manual_session_id=session_id, manual_filename=yaml_filename, user_id=the_user_id)
                obtain_lock(session_id, yaml_filename)
                if the_user_id is None:
                    reset_user_dict(session_id, yaml_filename, user_id=the_user_id, force=True)
                else:
                    reset_user_dict(session_id, yaml_filename, user_id=the_user_id)
                release_lock(session_id, yaml_filename)
        return len(sessions_to_delete)
    if action == 'delete':
        if filename is None or session is None:
            raise Exception("user_interviews: filename and session must be provided in order to delete interview")
        manual_checkout(manual_session_id=session, manual_filename=filename, user_id=user_id)
        obtain_lock(session, filename)
        reset_user_dict(session, filename, user_id=user_id)
        release_lock(session, filename)
        return True
    if current_user and current_user.is_authenticated and current_user.timezone:
        the_timezone = pytz.timezone(current_user.timezone)
    else:
        the_timezone = pytz.timezone(get_default_timezone())
    subq = db.session.query(db.func.max(UserDict.indexno).label('indexno'), UserDict.filename, UserDict.key).group_by(UserDict.filename, UserDict.key).subquery()
    if user_id is not None:
        if filename is not None:
            interview_query = db.session.query(UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted, UserModel.email).join(subq, and_(subq.c.filename == UserDictKeys.filename, subq.c.key == UserDictKeys.key)).join(UserDict, and_(UserDict.indexno == subq.c.indexno, UserDict.key == UserDictKeys.key, UserDict.filename == UserDictKeys.filename)).join(UserModel, UserModel.id == UserDictKeys.user_id).filter(UserDictKeys.user_id == user_id, UserDictKeys.filename == filename).group_by(UserModel.email, UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted, UserDictKeys.indexno).order_by(UserDictKeys.indexno)
        else:
            interview_query = db.session.query(UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted, UserModel.email).join(subq, and_(subq.c.filename == UserDictKeys.filename, subq.c.key == UserDictKeys.key)).join(UserDict, and_(UserDict.indexno == subq.c.indexno, UserDict.key == UserDictKeys.key, UserDict.filename == UserDictKeys.filename)).join(UserModel, UserModel.id == UserDictKeys.user_id).filter(UserDictKeys.user_id == user_id).group_by(UserModel.email, UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDictKeys.filename, UserDictKeys.key, UserDict.dictionary, UserDict.encrypted, UserDictKeys.indexno).order_by(UserDictKeys.indexno)
    else:
        if filename is not None:
            interview_query = db.session.query(UserDict).join(subq, and_(UserDict.indexno == subq.c.indexno, UserDict.key == subq.c.key, UserDict.filename == subq.c.filename)).outerjoin(UserDictKeys, and_(UserDict.filename == UserDictKeys.filename, UserDict.key == UserDictKeys.key)).outerjoin(UserModel, and_(UserDictKeys.user_id == UserModel.id, UserModel.active == True)).filter(UserDict.filename == filename).group_by(UserModel.email, UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDict.filename, UserDict.key, UserDict.dictionary, UserDict.encrypted, UserDictKeys.indexno).order_by(UserDictKeys.indexno).with_entities(UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDict.filename, UserDict.key, UserDict.dictionary, UserDict.encrypted, UserModel.email)
        else:
            interview_query = db.session.query(UserDict).join(subq, and_(UserDict.indexno == subq.c.indexno, UserDict.key == subq.c.key, UserDict.filename == subq.c.filename)).outerjoin(UserDictKeys, and_(UserDict.filename == UserDictKeys.filename, UserDict.key == UserDictKeys.key)).outerjoin(UserModel, and_(UserDictKeys.user_id == UserModel.id, UserModel.active == True)).group_by(UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDict.filename, UserDict.key, UserDict.dictionary, UserDict.encrypted, UserDictKeys.indexno, UserModel.email).order_by(UserDictKeys.indexno).with_entities(UserDictKeys.user_id, UserDictKeys.temp_user_id, UserDict.filename, UserDict.key, UserDict.dictionary, UserDict.encrypted, UserModel.email)
    #logmessage(str(interview_query))
    interviews = list()
    for interview_info in interview_query:
        #logmessage("filename is " + str(interview_info.filename) + " " + str(interview_info.key))
        if session is not None and interview_info.key != session:
            continue
        interview_title = dict()
        is_valid = True
        interview_valid = True
        try:
            interview = docassemble.base.interview_cache.get_interview(interview_info.filename)
        except Exception as the_err:
            if exclude_invalid:
                continue
            logmessage("user_interviews: unable to load interview file " + interview_info.filename)
            interview_title['full'] = word('Error: interview not found')
            interview_valid = False
            is_valid = False
        #logmessage("Found old interview with title " + interview_title)
        if interview_info.encrypted:
            try:
                dictionary = decrypt_dictionary(interview_info.dictionary, secret)
            except Exception as the_err:
                if exclude_invalid:
                    continue
                try:
                    logmessage("user_interviews: unable to decrypt dictionary.  " + str(the_err.__class__.__name__) + ": " + unicode(the_err))
                except:
                    logmessage("user_interviews: unable to decrypt dictionary.  " + str(the_err.__class__.__name__))
                dictionary = fresh_dictionary()
                dictionary['_internal']['starttime'] = None
                dictionary['_internal']['modtime'] = None
                is_valid = False
        else:
            dictionary = unpack_dictionary(interview_info.dictionary)
        if type(dictionary) is not dict:
            logmessage("user_interviews: found a dictionary that was not a dictionary")
            continue
        if is_valid:
            interview_title = interview.get_title(dictionary)
            metadata = copy.deepcopy(interview.consolidated_metadata)
            tags = interview.get_tags(dictionary)
        elif interview_valid:
            interview_title = interview.get_title(dict(_internal=dict()))
            metadata = copy.deepcopy(interview.consolidated_metadata)
            tags = interview.get_tags(dictionary)
            if 'full' not in interview_title:
                interview_title['full'] = word("Interview answers cannot be decrypted")
            else:
                interview_title['full'] += ' - ' + word('interview answers cannot be decrypted')
        else:
            interview_title['full'] = word('Error: interview not found and answers could not be decrypted')
            metadata = dict()
            tags = set()
        if dictionary['_internal']['starttime']:
            utc_starttime = dictionary['_internal']['starttime']
            starttime = nice_date_from_utc(dictionary['_internal']['starttime'], timezone=the_timezone)
        else:
            utc_starttime = None
            starttime = ''
        if dictionary['_internal']['modtime']:
            utc_modtime = dictionary['_internal']['modtime']
            modtime = nice_date_from_utc(dictionary['_internal']['modtime'], timezone=the_timezone)
        else:
            utc_modtime = None
            modtime = ''
        if tag is not None and tag not in tags:
            continue
        out = {'filename': interview_info.filename, 'session': interview_info.key, 'modtime': modtime, 'starttime': starttime, 'utc_modtime': utc_modtime, 'utc_starttime': utc_starttime, 'title': interview_title.get('full', word('Untitled')), 'subtitle': interview_title.get('sub', None), 'valid': is_valid, 'metadata': metadata, 'tags': tags, 'email': interview_info.email, 'user_id': interview_info.user_id, 'temp_user_id': interview_info.temp_user_id}
        if include_dict:
            out['dict'] = dictionary
        interviews.append(out)
    return interviews
    
@app.route('/interviews', methods=['GET', 'POST'])
@login_required
def interview_list():
    if ('json' in request.form and int(request.form['json'])) or ('json' in request.args and int(request.args['json'])):
        is_json = True
    else:
        is_json = False
    if 'lang' in request.form:
        session['language'] = request.form['lang']
        docassemble.base.functions.set_language(session['language'])
    tag = request.args.get('tag', None)
    if 'newsecret' in session:
        #logmessage("interview_list: fixing cookie")
        if is_json:
            if tag:
                response = redirect(url_for('interview_list', json='1', tag=tag))
            else:
                response = redirect(url_for('interview_list', json='1'))
        else:
            if tag:
                response = redirect(url_for('interview_list', tag=tag))
            else:
                response = redirect(url_for('interview_list'))
        response.set_cookie('secret', session['newsecret'])
        del session['newsecret']
        return response
    if request.method == 'GET' and needs_to_change_password():
        return redirect(url_for('user.change_password', next=url_for('interview_list')))
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    #logmessage("interview_list: secret is " + repr(secret))
    if 'action' in request.args and request.args.get('action') == 'delete_all':
        num_deleted = user_interviews(user_id=current_user.id, secret=secret, action='delete_all', tag=tag)
        if num_deleted > 0:
            flash(word("Deleted interviews"), 'success')
        if is_json:
            return redirect(url_for('interview_list', json='1'))
        else:
            return redirect(url_for('interview_list'))
    elif 'action' in request.args and request.args.get('action') == 'delete':
        yaml_file = request.args.get('filename', None)
        session_id = request.args.get('session', None)
        if yaml_file is not None and session_id is not None:
            user_interviews(user_id=current_user.id, secret=secret, action='delete', session=session_id, filename=yaml_file)
            flash(word("Deleted interview"), 'success')
        if is_json:
            return redirect(url_for('interview_list', json='1'))
        else:
            return redirect(url_for('interview_list'))
    if daconfig.get('session list interview', None) is not None:
        if is_json:
            return redirect(url_for('index', i=daconfig.get('session list interview'), from_list='1', json='1'))
        else:
            return redirect(url_for('index', i=daconfig.get('session list interview'), from_list='1'))
    if current_user.has_role('admin', 'developer'):
        exclude_invalid = False
    else:
        exclude_invalid = True
    resume_interview = request.args.get('resume', None)
    if resume_interview is None and daconfig.get('auto resume interview', None) is not None and re.search(r'user/(register|sign-in)', str(request.referrer)):
        resume_interview = daconfig['auto resume interview']
    if resume_interview is not None:
        interviews = user_interviews(user_id=current_user.id, secret=secret, exclude_invalid=exclude_invalid, filename=resume_interview)
        if len(interviews):
            return redirect(url_for('index', i=interviews[0]['filename'], session=interviews[0]['session'], from_list='1'))
        return redirect(url_for('index', i=resume_interview, from_list='1'))
    interviews = user_interviews(user_id=current_user.id, secret=secret, exclude_invalid=exclude_invalid, tag=tag)
    if interviews is None:
        raise Exception("interview_list: could not obtain list of interviews")
    if is_json:
        for interview in interviews:
            if 'dict' in interview:
                del interview['dict']
            if 'tags' in interview:
                interview['tags'] = sorted(interview['tags'])
        return jsonify(action="interviews", interviews=interviews)
    script = """
    <script>
      $("#deleteall").on('click', function(event){
        if (confirm(""" + json.dumps(word("Are you sure you want to delete all saved interviews?")) + """)){
          return true;
        }
        event.preventDefault();
        return false;
      });
    </script>"""
    script += global_js
    if re.search(r'user/register', str(request.referrer)) and len(interviews) == 1:
        return redirect(url_for('index', i=interviews[0]['filename'], session=interviews[0]['session'], from_list=1))
    tags_used = set()
    for interview in interviews:
        for the_tag in interview['tags']:
            if the_tag != tag:
                tags_used.add(the_tag)
    #interview_page_title = word(daconfig.get('interview page title', 'Interviews'))
    #title = word(daconfig.get('interview page heading', 'Resume an interview'))
    argu = dict(version_warning=version_warning, tags_used=sorted(tags_used) if len(tags_used) else None, numinterviews=len(interviews), interviews=sorted(interviews, key=valid_date_key), tag=tag) # extra_css=Markup(global_css), extra_js=Markup(script), tab_title=interview_page_title, page_title=interview_page_title, title=title
    if 'interview page template' in daconfig and daconfig['interview page template']:
        the_page = docassemble.base.functions.package_template_filename(daconfig['interview page template'])
        if the_page is None:
            raise DAError("Could not find start page template " + daconfig['start page template'])
        with open(the_page, 'rU') as fp:
            template_string = fp.read().decode('utf8')
            return render_template_string(template_string, **argu)
    else:
        return render_template('pages/interviews.html', **argu)

def valid_date_key(x):
    if x['dict']['_internal']['starttime'] is None:
        return datetime.datetime.now()
    return x['dict']['_internal']['starttime']
    
def fix_secret(user=None):
    #logmessage("fix_secret starting")
    if user is None:
        user = current_user
    password = str(request.form.get('password', request.form.get('new_password', None)))
    if password is not None:
        secret = str(request.cookies.get('secret', None))
        newsecret = pad_to_16(MD5Hash(data=password).hexdigest())
        if secret == 'None' or secret != newsecret:
            #logmessage("fix_secret: calling substitute_secret with " + str(secret) + ' and ' + str(newsecret))
            #logmessage("fix_secret: setting newsecret session")
            session['newsecret'] = substitute_secret(str(secret), newsecret, user=user)
        # else:
        #     logmessage("fix_secret: secrets are the same")
    else:
        logmessage("fix_secret: password not in request")

def login_or_register(sender, user, **extra):
    #logmessage("login or register!")
    if 'i' in session and 'uid' in session:
        if 'tempuser' in session:
            sub_temp_user_dict_key(session['tempuser'], user.id)
        save_user_dict_key(session['uid'], session['i'], priors=True, user=user)
        session['key_logged'] = True
    fix_secret(user=user)
    if 'tempuser' in session:
        changed = False
        for chat_entry in ChatLog.query.filter_by(temp_user_id=int(session['tempuser'])).all():
            chat_entry.user_id = user.id
            chat_entry.temp_user_id = None
            changed = True
        if changed:
            db.session.commit()
        changed = False
        for chat_entry in ChatLog.query.filter_by(temp_owner_id=int(session['tempuser'])).all():
            chat_entry.owner_id = user.id
            chat_entry.temp_owner_id = None
            changed = True
        if changed:
            db.session.commit()
        del session['tempuser']
    session['user_id'] = user.id
    if user.language and user.language != DEFAULT_LANGUAGE:
        session['language'] = user.language

@user_logged_in.connect_via(app)
def _on_user_login(sender, user, **extra):
    #logmessage("on user login")
    login_or_register(sender, user, **extra)
    #flash(word('You have signed in successfully.'), 'success')

@user_changed_password.connect_via(app)
def _on_password_change(sender, user, **extra):
    #logmessage("on password change")
    fix_secret(user=user)
    
@user_reset_password.connect_via(app)
def _on_password_reset(sender, user, **extra):
    #logmessage("on password reset")
    fix_secret(user=user)

@user_registered.connect_via(app)
def on_register_hook(sender, user, **extra):
    #why did I not just import it globally?
    #from docassemble.webapp.users.models import Role
    user_invite = extra.get('user_invite', None)
    this_user_role = None
    if user_invite is not None:
        this_user_role = Role.query.filter_by(id=user_invite.role_id).first()
    if this_user_role is None:
        this_user_role = Role.query.filter_by(name='user').first()
    roles_to_remove = list()
    for role in user.roles:
        roles_to_remove.append(role)
    for role in roles_to_remove:
        user.roles.remove(role)
    user.roles.append(this_user_role)
    db.session.commit()
    login_or_register(sender, user, **extra)
    #flash(word('You have registered successfully.'), 'success')

# @user_logged_in.connect_via(app)
# def _after_login_hook(sender, user, **extra):
#     if 'i' in session and 'uid' in session:
#         save_user_dict_key(session['uid'], session['i'])
#         session['key_logged'] = True 
#     newsecret = substitute_secret(secret, pad_to_16(MD5Hash(data=password).hexdigest()))
#     # Redirect to 'next' URL
#     response = redirect(next)
#     response.set_cookie('secret', newsecret)
#     return response

# @app.teardown_appcontext
# def close_db(error):
#     if hasattr(db, 'engine'):
#         db.engine.dispose()

# @app.route('/webrtc')
# def webrtc():
#     return render_template('pages/webrtc.html', tab_title=word("WebRTC"), page_title=word("WebRTC"))

# @app.route('/webrtc_token', methods=['GET'])
# @csrf.exempt
# def webrtc_token():
#     if twilio_config is None:
#         logmessage("webrtc_token: could not get twilio configuration")
#         return
#     account_sid = twilio_config['name']['default'].get('account sid', None)
#     auth_token = twilio_config['name']['default'].get('auth token', None)
#     application_sid = twilio_config['name']['default'].get('app sid', None)

#     logmessage("webrtc_token: account sid is " + str(account_sid) + "; auth_token is " + str(auth_token) + "; application_sid is " + str(application_sid))

#     identity = 'testuser2'

#     capability = TwilioCapability(account_sid, auth_token)
#     capability.allow_client_outgoing(application_sid)
#     capability.allow_client_incoming(identity)
#     token = capability.generate()

#     return jsonify(identity=identity, token=token)

@app.route("/fax_callback", methods=['POST'])
@csrf.exempt
def fax_callback():
    if twilio_config is None:
        logmessage("fax_callback: Twilio not enabled")
        return ('', 204)
    post_data = request.form.copy()
    if 'FaxSid' not in post_data or 'AccountSid' not in post_data:
        logmessage("fax_callback: FaxSid and/or AccountSid missing")
        return ('', 204)
    tconfig = None
    for config_name, config_info in twilio_config['name'].iteritems():
        if 'account sid' in config_info and config_info['account sid'] == post_data['AccountSid']:
            tconfig = config_info
    if tconfig is None:
        logmessage("fax_callback: account sid of fax callback did not match any account sid in the Twilio configuration")
    if 'fax' not in tconfig or tconfig['fax'] in (False, None):
        logmessage("fax_callback: fax feature not enabled")
        return ('', 204)
    params = dict()
    for param in ('FaxSid', 'From', 'To', 'RemoteStationId', 'FaxStatus', 'ApiVersion', 'OriginalMediaUrl', 'NumPages', 'MediaUrl', 'ErrorCode', 'ErrorMessage'):
        params[param] = post_data.get(param, None)
    the_key = 'da:faxcallback:sid:' + post_data['FaxSid']
    pipe = r.pipeline()
    pipe.set(the_key, json.dumps(params))
    pipe.expire(the_key, 86400)
    pipe.execute()
    return ('', 204)

@app.route("/voice", methods=['POST', 'GET'])
@csrf.exempt
def voice():
    resp = twilio.twiml.voice_response.VoiceResponse()
    if twilio_config is None:
        logmessage("voice: ignoring call to voice because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if 'voice' not in twilio_config['name']['default'] or twilio_config['name']['default']['voice'] in (False, None):
        logmessage("voice: ignoring call to voice because voice feature not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("voice: request to voice did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    for item in request.form:
        logmessage("voice: item " + str(item) + " is " + str(request.form[item]))
    with resp.gather(action=daconfig.get('root', '/') + "digits", finishOnKey='#', method="POST", timeout=10, numDigits=5) as gg:
        gg.say(word("Please enter the four digit code, followed by the pound sign."))

    # twilio_config = daconfig.get('twilio', None)
    # if twilio_config is None:
    #     logmessage("Could not get twilio configuration")
    #     return
    # twilio_caller_id = twilio_config.get('number', None)
    # if "To" in request.form and request.form["To"] != '':
    #     dial = resp.dial(callerId=twilio_caller_id)
    #     if phone_pattern.match(request.form["To"]):
    #         dial.number(request.form["To"])
    #     else:
    #         dial.client(request.form["To"])
    # else:
    #     resp.say("Thanks for calling!")

    return Response(str(resp), mimetype='text/xml')

@app.route("/digits", methods=['POST', 'GET'])
@csrf.exempt
def digits():
    resp = twilio.twiml.voice_response.VoiceResponse()
    if twilio_config is None:
        logmessage("digits: ignoring call to digits because Twilio not enabled")
        return Response(str(resp), mimetype='text/xml')
    if "AccountSid" not in request.form or request.form["AccountSid"] != twilio_config['name']['default'].get('account sid', None):
        logmessage("digits: request to digits did not authenticate")
        return Response(str(resp), mimetype='text/xml')
    if "Digits" in request.form:
        the_digits = re.sub(r'[^0-9]', '', request.form["Digits"])
        logmessage("digits: got " + str(the_digits))
        phone_number = r.get('da:callforward:' + str(the_digits))
        if phone_number is None:
            resp.say(word("I am sorry.  The code you entered is invalid or expired.  Goodbye."))
            resp.hangup()
        else:
            dial = resp.dial(number=phone_number)
            r.delete('da:callforward:' + str(the_digits))
    else:
        logmessage("digits: no digits received")
        resp.say(word("No access code was entered."))
        resp.hangup()
    return Response(str(resp), mimetype='text/xml')

def sms_body(phone_number, body='question', config='default'):
    if twilio_config is None:
        raise DAError("sms_body: Twilio not enabled")
    if config not in twilio_config['name']:
        raise DAError("sms_body: specified config value, " + str(config) + ", not in Twilio configuration")
    tconfig = twilio_config['name'][config]
    if 'sms' not in tconfig or tconfig['sms'] in (False, None, 0):
        raise DAError("sms_body: sms feature is not enabled in Twilio configuration")
    if 'account sid' not in tconfig:
        raise DAError("sms_body: account sid not in Twilio configuration")
    if 'number' not in tconfig:
        raise DAError("sms_body: phone number not in Twilio configuration")
    if 'doing_sms' in session:
        raise DAError("Cannot call sms_body from within sms_body")
    form = dict(To=tconfig['number'], From=phone_number, Body=body, AccountSid=tconfig['account sid'])
    base_url = request.base_url
    url_root = request.url_root
    tbackup = docassemble.base.functions.backup_thread_variables()
    sbackup = backup_session()
    session['doing_sms'] = True
    resp = do_sms(form, base_url, url_root, save=False)
    restore_session(sbackup)
    docassemble.base.functions.restore_thread_variables(tbackup)
    if resp is None or len(resp.verbs) == 0 or len(resp.verbs[0].verbs) == 0:
        return None
    return resp.verbs[0].verbs[0].body

def favicon_file(filename):
    the_dir = docassemble.base.functions.package_data_filename(daconfig.get('favicon', 'docassemble.webapp:data/static/favicon'))
    if the_dir is None or not os.path.isdir(the_dir):
        logmessage("favicon_file: could not find favicon directory")
        abort(404)
    the_file = os.path.join(the_dir, filename)
    if not os.path.isfile(the_file):
        abort(404)
    extension, mimetype = get_ext_and_mimetype(the_file)
    response = send_file(the_file, mimetype=mimetype)
    return(response)

@app.route("/favicon.ico", methods=['GET'])
def favicon():
    return(favicon_file('favicon.ico'))
@app.route("/apple-touch-icon.png", methods=['GET'])
def apple_touch_icon():
    return(favicon_file('apple-touch-icon.png'))
@app.route("/favicon-32x32.png", methods=['GET'])
def favicon_md():
    return(favicon_file('favicon-32x32.png'))
@app.route("/favicon-16x16.png", methods=['GET'])
def favicon_sm():
    return(favicon_file('favicon-16x16.png'))
@app.route("/manifest.json", methods=['GET'])
def favicon_manifest_json():
    return(favicon_file('manifest.json'))
@app.route("/safari-pinned-tab.svg", methods=['GET'])
def favicon_safari_pinned_tab():
    return(favicon_file('safari-pinned-tab.svg'))
@app.route("/android-chrome-192x192.png", methods=['GET'])
def favicon_android_md():
    return(favicon_file('android-chrome-192x192.png'))
@app.route("/android-chrome-512x512.png", methods=['GET'])
def favicon_android_lg():
    return(favicon_file('android-chrome-512x512.png'))
@app.route("/mstile-150x150.png", methods=['GET'])
def favicon_mstile():
    return(favicon_file('mstile-150x150.png'))
@app.route("/browserconfig.xml", methods=['GET'])
def favicon_browserconfig():
    return(favicon_file('browserconfig.xml'))

@app.route("/robots.txt", methods=['GET'])
def robots():
    the_file = docassemble.base.functions.package_data_filename(daconfig.get('robots', 'docassemble.webapp:data/static/robots.txt'))
    if the_file is None:
        abort(404)
    response = send_file(the_file, mimetype='text/plain')
    return(response)

@app.route("/sms", methods=['POST'])
@csrf.exempt
def sms():
    #logmessage("Received: " + str(request.form))
    form = request.form
    base_url = request.base_url
    url_root = request.url_root
    resp = do_sms(form, base_url, url_root)
    return Response(str(resp), mimetype='text/xml')

def do_sms(form, base_url, url_root, config='default', save=True):
    resp = twilio.twiml.messaging_response.MessagingResponse()
    special_messages = list()
    if twilio_config is None:
        logmessage("do_sms: ignoring message to sms because Twilio not enabled")
        return resp
    if "AccountSid" not in form or form["AccountSid"] not in twilio_config['account sid']:
        logmessage("do_sms: request to sms did not authenticate")
        return resp
    if "To" not in form or form["To"] not in twilio_config['number']:
        logmessage("do_sms: request to sms ignored because recipient number " + str(form.get('To', None)) + " not in configuration, " + str(twilio_config))
        return resp
    tconfig = twilio_config['number'][form["To"]]
    if 'sms' not in tconfig or tconfig['sms'] in (False, None, 0):
        logmessage("do_sms: ignoring message to sms because SMS not enabled")
        return resp
    if "From" not in form or not re.search(r'[0-9]', form["From"]):
        logmessage("do_sms: request to sms ignored because unable to determine caller ID")
        return resp
    if "Body" not in form:
        logmessage("do_sms: request to sms ignored because message had no content")
        return resp
    inp = form['Body'].strip()
    #logmessage("do_sms: received >" + inp + "<")
    key = 'da:sms:client:' + form["From"] + ':server:' + tconfig['number']
    #logmessage("Searching for " + key)
    for try_num in (0, 1):
        sess_contents = r.get(key)
        if sess_contents is None:
            #logmessage("do_sms: received input '" + str(inp) + "' from new user")
            yaml_filename = tconfig.get('default interview', default_yaml_filename)
            if 'dispatch' in tconfig and type(tconfig['dispatch']) is dict:
                if inp.lower() in tconfig['dispatch']:
                    yaml_filename = tconfig['dispatch'][inp.lower()]
                    #logmessage("do_sms: using interview from dispatch: " + str(yaml_filename))
            if yaml_filename is None:
                #logmessage("do_sms: request to sms ignored because no interview could be determined")
                return resp
            if (not DEBUG) and (yaml_filename.startswith('docassemble.base') or yaml_filename.startswith('docassemble.demo')):
                raise Exception("do_sms: not authorized to run interviews in docassemble.base or docassemble.demo")
            secret = random_string(16)
            uid = get_unique_name(yaml_filename, secret)
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            sess_info = dict(yaml_filename=yaml_filename, uid=uid, secret=secret, number=form["From"], encrypted=True, tempuser=new_temp_user.id, user_id=None)
            r.set(key, pickle.dumps(sess_info))
            accepting_input = False
        else:
            try:        
                sess_info = pickle.loads(sess_contents)
            except:
                logmessage("do_sms: unable to decode session information")
                return resp
            accepting_input = True
        if inp.lower() in (word('exit'), word('quit')):
            logmessage("do_sms: exiting")
            if save:
                reset_user_dict(sess_info['uid'], sess_info['yaml_filename'], temp_user_id=sess_info['tempuser'])
            r.delete(key)
            return resp
        session['uid'] = sess_info['uid']
        obtain_lock(sess_info['uid'], sess_info['yaml_filename'])
        steps, user_dict, is_encrypted = fetch_user_dict(sess_info['uid'], sess_info['yaml_filename'], secret=sess_info['secret'])
        if user_dict is None:
            r.delete(key)
            continue
        break
    encrypted = sess_info['encrypted']
    action = None
    action_performed = False
    while True:
        if user_dict.get('multi_user', False) is True and encrypted is True:
            encrypted = False
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                decrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if user_dict.get('multi_user', False) is False and encrypted is False:
            encrypted = True
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                encrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        interview = docassemble.base.interview_cache.get_interview(sess_info['yaml_filename'])
        if 'skip' not in user_dict['_internal']:
            user_dict['_internal']['skip'] = dict()
        # if 'smsgather' in user_dict['_internal']:
        #     #logmessage("do_sms: need to gather smsgather " + user_dict['_internal']['smsgather'])
        #     sms_variable = user_dict['_internal']['smsgather']
        # else:
        #     sms_variable = None
        # if action is not None:
        #     action_manual = True
        # else:
        #     action_manual = False
        user = None
        if sess_info['user_id'] is not None:
            user = load_user(sess_info['user_id'])
        if user is None:
            ci = dict(user=dict(is_anonymous=True, is_authenticated=False, email=None, theid=sess_info['tempuser'], the_user_id='t' + str(sess_info['tempuser']), roles=['user'], firstname='SMS', lastname='User', nickname=None, country=None, subdivisionfirst=None, subdivisionsecond=None, subdivisionthird=None, organization=None, timezone=None, location=None), session=sess_info['uid'], secret=sess_info['secret'], yaml_filename=sess_info['yaml_filename'], interface='sms', url=base_url, url_root=url_root, encrypted=encrypted, headers=dict(), clientip=None, method=None, skip=user_dict['_internal']['skip'], sms_sender=form["From"])
        else:
            ci = dict(user=dict(is_anonymous=False, is_authenticated=True, email=user.email, theid=user.id, the_user_id=user.id, roles=user.roles, firstname=user.first_name, lastname=user.last_name, nickname=user.nickname, country=user.country, subdivisionfirst=user.subdivisionfirst, subdivisionsecond=user.subdivisionsecond, subdivisionthird=user.subdivisionthird, organization=user.organization, timezone=user.timezone, location=None), session=sess_info['uid'], secret=sess_info['secret'], yaml_filename=sess_info['yaml_filename'], interface='sms', url=base_url, url_root=url_root, encrypted=encrypted, headers=dict(), clientip=None, method=None, skip=user_dict['_internal']['skip'])
        if action is not None:
            logmessage("do_sms: setting action to " + str(action))
            ci.update(action)
        interview_status = docassemble.base.parse.InterviewStatus(current_info=ci)
        interview.assemble(user_dict, interview_status)
        logmessage("do_sms: back from assemble 1; had been seeking variable " + str(interview_status.sought))
        logmessage("do_sms: question is " + interview_status.question.name)
        if action is not None:
            logmessage('do_sms: question is now ' + interview_status.question.name + ' because action')
            sess_info['question'] = interview_status.question.name
            r.set(key, pickle.dumps(sess_info))
        elif 'question' in sess_info and sess_info['question'] != interview_status.question.name:
            if inp not in (word('?'), word('back'), word('question'), word('exit')):
                logmessage("do_sms: blanking the input because question changed from " + str(sess_info['question']) + " to " + str(interview_status.question.name))
                sess_info['question'] = interview_status.question.name
                inp = 'question'
                r.set(key, pickle.dumps(sess_info))

        #logmessage("do_sms: inp is " + inp.lower() + " and steps is " + str(steps) + " and can go back is " + str(interview_status.can_go_back))
        m = re.search(r'^(' + word('menu') + '|' + word('link') + ')([0-9]+)', inp.lower())
        if m:
            #logmessage("Got " + inp)
            arguments = dict()
            selection_type = m.group(1)
            selection_number = int(m.group(2)) - 1
            links = list()
            menu_items = list()
            sms_info = as_sms(interview_status, links=links, menu_items=menu_items)
            target_url = None
            if selection_type == word('menu') and selection_number < len(menu_items):
                (target_url, label) = menu_items[selection_number]
            if selection_type == word('link') and selection_number < len(links):
                (target_url, label) = links[selection_number]
            if target_url is not None:
                uri_params = re.sub(r'^[\?]*\?', r'', target_url)
                for statement in re.split(r'&', uri_params):
                    parts = re.split(r'=', statement)
                    arguments[parts[0]] = parts[1]
            if 'action' in arguments:
                #logmessage(myb64unquote(urllib.unquote(arguments['action'])))
                action = json.loads(myb64unquote(urllib.unquote(arguments['action'])))
                #logmessage("Action is " + str(action))
                action_performed = True
                accepting_input = False
                inp = ''
                continue
            break
        if inp.lower() == word('back'):
            if 'skip' in user_dict['_internal'] and len(user_dict['_internal']['skip']):
                max_entry = -1
                for the_entry in user_dict['_internal']['skip'].keys():
                    if the_entry > max_entry:
                        max_entry = the_entry
                if max_entry in user_dict['_internal']['skip']:
                    del user_dict['_internal']['skip'][max_entry]
                if 'command_cache' in user_dict['_internal'] and max_entry in user_dict['_internal']['command_cache']:
                    del user_dict['_internal']['command_cache'][max_entry]
                save_user_dict(sess_info['uid'], user_dict, sess_info['yaml_filename'], secret=sess_info['secret'], encrypt=encrypted, changed=False, steps=steps)
                accepting_input = False
                inp = ''
                continue
            elif steps > 1 and interview_status.can_go_back:
                old_user_dict = user_dict
                steps, user_dict, is_encrypted = fetch_previous_user_dict(sess_info['uid'], sess_info['yaml_filename'], secret=sess_info['secret'])
                if 'question' in sess_info:
                    del sess_info['question']
                    r.set(key, pickle.dumps(sess_info))
                accepting_input = False
                inp = ''
                continue
            else:
                break
        else:
            break
    false_list = [word('no'), word('n'), word('false'), word('f')]
    true_list = [word('yes'), word('y'), word('true'), word('t')]
    inp_lower = inp.lower()
    skip_it = False
    changed = False
    nothing_more = False
    if accepting_input:
        if inp_lower == word('?'):
            sms_info = as_sms(interview_status)
            message = ''
            if sms_info['help'] is None:
                message += word('Sorry, no help is available for this question.')
            else:
                message += sms_info['help']
            message += "\n" + word("To read the question again, type question.")
            resp.message(message)
            release_lock(sess_info['uid'], sess_info['yaml_filename'])
            if 'uid' in session:
                del session['uid']
            return resp
        if inp_lower == word('question'):
            accepting_input = False
    if inp_lower == word('skip'):
        user_entered_skip = True
    else:
        user_entered_skip = False
    if accepting_input:
        saveas = None
        if len(interview_status.question.fields):
            question = interview_status.question
            if question.question_type == "fields":
                field = None
                next_field = None
                for the_field in interview_status.get_field_list():
                    if hasattr(the_field, 'datatype') and the_field.datatype in ('html', 'note', 'script', 'css'):
                        continue
                    if is_empty_mc(interview_status, the_field):
                        continue
                    if the_field.number in user_dict['_internal']['skip']:
                        continue
                    if field is None:
                        field = the_field
                    elif next_field is None:
                        next_field = the_field
                    else:
                        break
                if field is None:
                    logmessage("do_sms: unclear what field is necessary!")
                    # if 'smsgather' in user_dict['_internal']:
                    #     del user_dict['_internal']['smsgather']
                    field = interview_status.question.fields[0]
                    next_field = None
                saveas = myb64unquote(field.saveas)
            else:
                if hasattr(interview_status.question.fields[0], 'saveas'):
                    saveas = myb64unquote(interview_status.question.fields[0].saveas)
                    logmessage("do_sms: variable to set is " + str(saveas))
                else:
                    saveas = None
                field = interview_status.question.fields[0]
                next_field = None
            if question.question_type == "settrue":
                if inp_lower == word('ok'):
                    data = 'True'
                else:
                    data = None
            elif question.question_type == 'signature':
                filename = 'canvas.png'
                extension = 'png'
                mimetype = 'image/png'
                temp_image_file = tempfile.NamedTemporaryFile(suffix='.' + extension)
                image = Image.new("RGBA", (200, 50))
                image.save(temp_image_file.name, 'PNG')
                (file_number, extension, mimetype) = save_numbered_file(filename, temp_image_file.name, yaml_file_name=sess_info['yaml_filename'], uid=sess_info['uid'])
                if inp_lower == word('x'):
                    the_string = saveas + " = docassemble.base.core.DAFile('" + saveas + "', filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')"
                    logmessage("do_sms: doing import docassemble.base.core")
                    logmessage("do_sms: doing signature: " + the_string)
                    try:
                        exec('import docassemble.base.core', user_dict)
                        exec(the_string, user_dict)
                        if not changed:
                            steps += 1
                            user_dict['_internal']['steps'] = steps
                            changed = True
                    except Exception as errMess:
                        logmessage("do_sms: error: " + str(errMess))
                        special_messages.append(word("Error") + ": " + str(errMess))
                    skip_it = True
                    data = repr('')
                else:
                    data = None
            elif hasattr(field, 'datatype') and field.datatype in ("ml", "mlarea"):
                try:
                    exec("import docassemble.base.util", user_dict)
                except Exception as errMess:
                    special_messages.append("Error: " + str(errMess))
                if 'ml_train' in interview_status.extras and field.number in interview_status.extras['ml_train']:
                    if not interview_status.extras['ml_train'][field.number]:
                        use_for_training = 'False'
                    else:
                        use_for_training = 'True'
                else:
                    use_for_training = 'True'
                if 'ml_group' in interview_status.extras and field.number in interview_status.extras['ml_group']:
                    data = 'docassemble.base.util.DAModel(' + repr(saveas) + ', group_id=' + repr(interview_status.extras['ml_group'][field.number]) + ', text=' + repr(inp) + ', store=' + repr(interview.get_ml_store()) + ', use_for_training=' + use_for_training + ')'
                else:
                    data = 'docassemble.base.util.DAModel(' + repr(saveas) + ', text=' + repr(inp) + ', store=' + repr(interview.get_ml_store()) + ', use_for_training=' + use_for_training + ')'
            elif hasattr(field, 'datatype') and field.datatype in ("file", "files", "camera", "user", "environment", "camcorder", "microphone"):
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    skip_it = True
                    data = repr('')
                else:
                    files_to_process = list()
                    num_media = int(form.get('NumMedia', '0'))
                    fileindex = 0
                    while True:
                        if field.datatype == "file" and fileindex > 0:
                            break
                        if fileindex >= num_media or 'MediaUrl' + str(fileindex) not in form:
                            break
                        #logmessage("mime type is" + form.get('MediaContentType' + str(fileindex), 'Unknown'))
                        mimetype = form.get('MediaContentType' + str(fileindex), 'image/jpeg')
                        extension = re.sub(r'\.', r'', mimetypes.guess_extension(mimetype))
                        if extension == 'jpe':
                            extension = 'jpg'
                        # original_extension = extension
                        # if extension == 'gif':
                        #     extension == 'png'
                        #     mimetype = 'image/png'
                        filename = 'file' + '.' + extension
                        file_number = get_new_file_number(sess_info['uid'], filename, yaml_file_name=sess_info['yaml_filename'])
                        saved_file = SavedFile(file_number, extension=extension, fix=True)
                        the_url = form['MediaUrl' + str(fileindex)]
                        #logmessage("Fetching from >" + the_url + "<")
                        saved_file.fetch_url(the_url)
                        process_file(saved_file, saved_file.path, mimetype, extension)
                        files_to_process.append((filename, file_number, mimetype, extension))
                        fileindex += 1
                    if len(files_to_process) > 0:
                        elements = list()
                        indexno = 0
                        for (filename, file_number, mimetype, extension) in files_to_process:
                            elements.append("docassemble.base.core.DAFile(" + repr(saveas + "[" + str(indexno) + "]") + ", filename=" + repr(filename) + ", number=" + str(file_number) + ", mimetype=" + repr(mimetype) + ", extension=" + repr(extension) + ")")
                            indexno += 1
                        the_string = saveas + " = docassemble.base.core.DAFileList(" + repr(saveas) + ", elements=[" + ", ".join(elements) + "])"
                        logmessage("do_sms: doing import docassemble.base.core")
                        logmessage("do_sms: doing file: " + the_string)
                        try:
                            exec('import docassemble.base.core', user_dict)
                            exec(the_string, user_dict)
                            if not changed:
                                steps += 1
                                user_dict['_internal']['steps'] = steps
                                changed = True
                        except Exception as errMess:
                            logmessage("do_sms: error: " + str(errMess))
                            special_messages.append(word("Error") + ": " + str(errMess))
                        skip_it = True
                        data = repr('')
                    else:
                        data = None
                        if interview_status.extras['required'][field.number]:
                            special_messages.append(word("You must attach a file."))
            elif question.question_type == "yesno" or (hasattr(field, 'datatype') and (hasattr(field, 'datatype') and field.datatype == 'boolean' and (hasattr(field, 'sign') and field.sign > 0))):
                if inp_lower in true_list:
                    data = 'True'
                elif inp_lower in false_list:
                    data = 'False'
                else:
                    data = None
            elif question.question_type == "yesnomaybe" or (hasattr(field, 'datatype') and (field.datatype == 'threestate' and (hasattr(field, 'sign') and field.sign > 0))):
                if inp_lower in true_list:
                    data = 'True'
                elif inp_lower in false_list:
                    data = 'False'
                else:
                    data = 'None'
            elif question.question_type == "noyes" or (hasattr(field, 'datatype') and (field.datatype in ('noyes', 'noyeswide') or (field.datatype == 'boolean' and (hasattr(field, 'sign') and field.sign < 0)))):
                if inp_lower in true_list:
                    data = 'False'
                elif inp_lower in false_list:
                    data = 'True'
                else:
                    data = None
            elif question.question_type in ('noyesmaybe', 'noyesmaybe', 'noyeswidemaybe') or (hasattr(field, 'datatype') and field.datatype == 'threestate' and (hasattr(field, 'sign') and field.sign < 0)):
                if inp_lower in true_list:
                    data = 'False'
                elif inp_lower in false_list:
                    data = 'True'
                else:
                    data = 'None'
            elif question.question_type == 'multiple_choice' or hasattr(field, 'choicetype') or (hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio', 'checkboxes', 'object_checkboxes')) or (hasattr(field, 'inputtype') and field.inputtype == 'radio'):
                cdata, choice_list = get_choices_with_abb(interview_status, field)
                data = None
                if hasattr(field, 'datatype') and field.datatype in ('checkboxes', 'object_checkboxes') and saveas is not None:
                    if 'command_cache' not in user_dict['_internal']:
                        user_dict['_internal']['command_cache'] = dict()
                    if field.number not in user_dict['_internal']['command_cache']:
                        user_dict['_internal']['command_cache'][field.number] = list()
                    docassemble.base.parse.ensure_object_exists(saveas, field.datatype, user_dict, commands=user_dict['_internal']['command_cache'][field.number])
                    saveas = saveas + '.gathered'
                    data = 'True'
                if (user_entered_skip or (inp_lower == word('none') and hasattr(field, 'datatype') and field.datatype in ('checkboxes', 'object_checkboxes'))) and ((hasattr(field, 'disableothers') and field.disableothers) or (hasattr(field, 'datatype') and field.datatype in ('checkboxes', 'object_checkboxes')) or not (interview_status.extras['required'][field.number] or (question.question_type == 'multiple_choice' and hasattr(field, 'saveas')))):
                    logmessage("do_sms: skip accepted")
                    # user typed 'skip,' or, where checkboxes, 'none.'  Also:
                    # field is skippable, either because it has disableothers, or it is a checkbox field, or
                    # it is not required.  Multiple choice fields with saveas are considered required.
                    if hasattr(field, 'datatype'):
                        if field.datatype in ('object', 'object_radio'):
                            skip_it = True
                            data = repr('')
                        if field.datatype in ('checkboxes', 'object_checkboxes'):
                            for choice in choice_list:
                                if choice[1] is None:
                                    continue
                                user_dict['_internal']['command_cache'][field.number].append(choice[1] + ' = False')
                        elif (question.question_type == 'multiple_choice' and hasattr(field, 'saveas')) or hasattr(field, 'choicetype'):
                            if user_entered_skip:
                                data = repr(None)
                            else:
                                logmessage("do_sms: setting skip_it to True")
                                skip_it = True
                                data = repr('')
                        elif field.datatype == 'integer':
                            data = '0'
                        elif field.datatype in ('number', 'float', 'currency', 'range'):
                            data = '0.0'
                        else:
                            data = repr('')
                    else:
                        data = repr('')
                else:
                    # There is a real value here
                    if hasattr(field, 'datatype') and field.datatype == 'object_checkboxes':
                        true_values = set()
                        for selection in re.split(r' *[,;] *', inp_lower):
                            for potential_abb, value in cdata['abblower'].iteritems():
                                if selection and selection.startswith(potential_abb):
                                    for choice in choice_list:
                                        if value == choice[0]:
                                            true_values.add(choice[2])
                        the_saveas = myb64unquote(field.saveas)
                        logmessage("do_sms: the_saveas is " + repr(the_saveas))
                        for choice in choice_list:
                            if choice[2] is None:
                                continue
                            if choice[2] in true_values:
                                logmessage("do_sms: " + choice[2] + " is in true_values")
                                the_string = 'if ' + choice[2] + ' not in ' + the_saveas + '.elements:\n    ' + the_saveas + '.append(' + choice[2] + ')'
                            else:
                                the_string = 'if ' + choice[2] + ' in ' + the_saveas + '.elements:\n    ' + the_saveas + '.remove(' + choice[2] + ')'
                            user_dict['_internal']['command_cache'][field.number].append(the_string)
                    elif hasattr(field, 'datatype') and field.datatype == 'checkboxes':
                        true_values = set()
                        for selection in re.split(r' *[,;] *', inp_lower):
                            for potential_abb, value in cdata['abblower'].iteritems():
                                if selection and selection.startswith(potential_abb):
                                    for choice in choice_list:
                                        if value == choice[0]:
                                            true_values.add(choice[1])
                        for choice in choice_list:
                            if choice[1] is None:
                                continue
                            if choice[1] in true_values:
                                the_string = choice[1] + ' = True'
                            else:
                                the_string = choice[1] + ' = False'
                            user_dict['_internal']['command_cache'][field.number].append(the_string)
                    else:
                        #regular multiple choice
                        #logmessage("do_sms: user selected " + inp_lower + " and data is " + str(cdata))
                        for potential_abb, value in cdata['abblower'].iteritems():
                            if inp_lower.startswith(potential_abb):
                                #logmessage("do_sms: user selected " + value)
                                for choice in choice_list:
                                    #logmessage("do_sms: considering " + choice[0])
                                    if value == choice[0]:
                                        #logmessage("do_sms: found a match")
                                        saveas = choice[1]
                                        if hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio'):
                                            data = choice[2]
                                        else:
                                            data = repr(choice[2])
                                        break
                                break
            elif hasattr(field, 'datatype') and field.datatype == 'integer':
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\-\.]', '', inp)
                    if data == '':
                        data = '0'
                    try:
                        the_value = eval("int(" + repr(data) + ")")
                        data = "int(" + repr(data) + ")"
                    except:
                        special_messages.append('"' + inp + '" ' + word("is not a whole number."))
                        data = None
            elif hasattr(field, 'datatype') and field.datatype in ('date', 'datetime'):
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    try:
                        dateutil.parser.parse(inp)
                        data = docassemble.base.util.as_datetime(inp)
                    except Exception as the_err:
                        logmessage("do_sms: date validation error was " + str(the_err))
                        if field.datatype == 'date':
                            special_messages.append('"' + inp + '" ' + word("is not a valid date."))
                        else:
                            special_messages.append('"' + inp + '" ' + word("is not a valid date and time."))
                        data = None                    
            elif hasattr(field, 'datatype') and field.datatype == 'time':
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    try:
                        dateutil.parser.parse(inp)
                        data = docassemble.base.util.as_datetime(inp).time()
                    except Exception as the_err:
                        logmessage("do_sms: time validation error was " + str(the_err))
                        special_messages.append('"' + inp + '" ' + word("is not a valid time."))
                        data = None                    
            elif hasattr(field, 'datatype') and field.datatype == 'range':
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\-\.]', '', inp)
                    try:
                        the_value = eval("float(" + repr(data) + ")", user_dict)
                        if the_value > int(interview_status.extras['max'][field.number]) or the_value < int(interview_status.extras['min'][field.number]):
                            special_messages.append('"' + inp + '" ' + word("is not within the range."))
                            data = None
                    except:
                        data = None
            elif hasattr(field, 'datatype') and field.datatype in ('number', 'float', 'currency'):
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\-\.]', '', inp)
                    if data == '':
                        data = '0.0'
                    try:
                        the_value = eval("float(" + json.dumps(data) + ")", user_dict)
                        data = "float(" + json.dumps(data) + ")"
                    except:
                        special_messages.append('"' + inp + '" ' + word("is not a valid number."))
                        data = None
            else:
                if user_entered_skip:
                    if interview_status.extras['required'][field.number]:
                        data = repr(inp)
                    else:
                        data = repr('')
                        skip_it = True
                else:
                    data = repr(inp)
        else:
            data = None
        if data is None:
            logmessage("do_sms: could not process input: " + inp)
            special_messages.append(word("I do not understand what you mean by") + ' "' + inp + '."')
        else:
            the_string = saveas + ' = ' + data
            try:
                if not skip_it:
                    if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                        logmessage("do_sms: disabling others")
                        next_field = None
                    if next_field is not None:
                        if 'command_cache' not in user_dict['_internal']:
                            user_dict['_internal']['command_cache'] = dict()
                        if field.number not in user_dict['_internal']['command_cache']:
                            user_dict['_internal']['command_cache'][field.number] = list()
                        user_dict['_internal']['command_cache'][field.number].append(the_string)
                        logmessage("do_sms: storing in command cache: " + str(the_string))
                    else:
                        for the_field in interview_status.get_field_list():
                            if is_empty_mc(interview_status, the_field):
                                logmessage("do_sms: a field is empty")
                                the_saveas = myb64unquote(the_field.saveas)
                                if 'command_cache' not in user_dict['_internal']:
                                    user_dict['_internal']['command_cache'] = dict()
                                if the_field.number not in user_dict['_internal']['command_cache']:
                                    user_dict['_internal']['command_cache'][the_field.number] = list()
                                if hasattr(the_field, 'datatype'):
                                    if the_field.datatype == 'object_checkboxes':
                                        docassemble.base.parse.ensure_object_exists(the_saveas, 'object_checkboxes', user_dict, commands=user_dict['_internal']['command_cache'][the_field.number])
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + '.clear()')
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + '.gathered = True')
                                    elif the_field.datatype in ('object', 'object_radio'):
                                        try:
                                            eval(the_saveas, user_dict)
                                        except:
                                            user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + ' = None')
                                    elif the_field.datatype == 'checkboxes':
                                        docassemble.base.parse.ensure_object_exists(the_saveas, 'checkboxes', user_dict, commands=user_dict['_internal']['command_cache'][the_field.number])
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + '.gathered = True')
                                    else:
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + ' = None')
                                else:
                                    user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + ' = None')
                        if 'command_cache' in user_dict['_internal']:
                            for field_num in sorted(user_dict['_internal']['command_cache'].keys()):
                                for pre_string in user_dict['_internal']['command_cache'][field_num]:
                                    logmessage("do_sms: doing command cache: " + pre_string)
                                    exec(pre_string, user_dict)
                        logmessage("do_sms: doing regular: " + the_string)
                        exec(the_string, user_dict)
                        if not changed:
                            steps += 1
                            user_dict['_internal']['steps'] = steps
                            changed = True
                if next_field is None:
                    if skip_it:
                        # Run the commands that we have been storing up
                        if 'command_cache' in user_dict['_internal']:
                            for field_num in sorted(user_dict['_internal']['command_cache'].keys()):
                                for pre_string in user_dict['_internal']['command_cache'][field_num]:
                                    logmessage("do_sms: doing command cache: " + pre_string)
                                    exec(pre_string, user_dict)
                            if not changed:
                                steps += 1
                                user_dict['_internal']['steps'] = steps
                                changed = True
                    logmessage("do_sms: next_field is None")
                    if 'skip' in user_dict['_internal']:
                        user_dict['_internal']['skip'].clear()
                    if 'command_cache' in user_dict['_internal']:
                        user_dict['_internal']['command_cache'].clear()
                    # if 'sms_variable' in interview_status.current_info:
                    #     del interview_status.current_info['sms_variable']
                else:
                    logmessage("do_sms: next_field is not None")
                    user_dict['_internal']['skip'][field.number] = True
                    #user_dict['_internal']['smsgather'] = interview_status.sought
                # if 'smsgather' in user_dict['_internal'] and user_dict['_internal']['smsgather'] == saveas:
                #     #logmessage("do_sms: deleting " + user_dict['_internal']['smsgather'])
                #     del user_dict['_internal']['smsgather']
            except Exception as the_err:
                logmessage("do_sms: failure to set variable with " + the_string)
                logmessage("do_sms: error was " + str(the_err))
                release_lock(sess_info['uid'], sess_info['yaml_filename'])
                if 'uid' in session:
                    del session['uid']
                return resp
        if changed and next_field is None and question.name not in user_dict['_internal']['answers']:
            logmessage("do_sms: setting internal answers for " + str(question.name))
            question.mark_as_answered(user_dict)
        interview.assemble(user_dict, interview_status)
        logmessage("do_sms: back from assemble 2; had been seeking variable " + str(interview_status.sought))
        logmessage("do_sms: question is now " + str(interview_status.question.name))
        sess_info['question'] = interview_status.question.name
        r.set(key, pickle.dumps(sess_info))
    else:
        logmessage("do_sms: not accepting input.")    
    if interview_status.question.question_type in ("restart", "exit", "logout", "exit_logout", "new_session"):
        logmessage("do_sms: exiting because of restart or exit")
        if save:
            reset_user_dict(sess_info['uid'], sess_info['yaml_filename'], temp_user_id=sess_info['tempuser'])
        r.delete(key)
        if interview_status.question.question_type in ('restart', 'new_session'):
            sess_info = dict(yaml_filename=sess_info['yaml_filename'], uid=get_unique_name(sess_info['yaml_filename'], sess_info['secret']), secret=sess_info['secret'], number=form["From"], encrypted=True, tempuser=sess_info['tempuser'], user_id=None)
            r.set(key, pickle.dumps(sess_info))
            form = dict(To=form['To'], From=form['From'], AccountSid=form['AccountSid'], Body=word('question'))
            return do_sms(form, base_url, url_root, config=config, save=True)
    else:
        if not interview_status.can_go_back:
            user_dict['_internal']['steps_offset'] = steps
        #I had commented this out in do_sms(), but not in index()
        #user_dict['_internal']['answers'] = dict()
        if (not interview_status.followed_mc) and len(user_dict['_internal']['answers']):
            user_dict['_internal']['answers'].clear()
        # if interview_status.question.name and interview_status.question.name in user_dict['_internal']['answers']:
        #     del user_dict['_internal']['answers'][interview_status.question.name]
        #logmessage("do_sms: " + as_sms(interview_status))
        #twilio_client = TwilioRestClient(tconfig['account sid'], tconfig['auth token'])
        #message = twilio_client.messages.create(to=form["From"], from_=form["To"], body=as_sms(interview_status))
        logmessage("do_sms: calling as_sms")
        sms_info = as_sms(interview_status)
        qoutput = sms_info['question']
        if sms_info['next'] is not None:
            logmessage("do_sms: next variable is " + sms_info['next'])
            if interview_status.sought is None:
                logmessage("do_sms: sought variable is None")
            #user_dict['_internal']['smsgather'] = interview_status.sought
        if (accepting_input or changed or action_performed or sms_info['next'] is not None) and save:
            save_user_dict(sess_info['uid'], user_dict, sess_info['yaml_filename'], secret=sess_info['secret'], encrypt=encrypted, changed=changed, steps=steps)
        for special_message in special_messages:
            qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + special_message + 'XXXXMESSAGE_AREAXXXX', qoutput)
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', '', qoutput)
        if user_dict.get('multi_user', False) is True and encrypted is True:
            encrypted = False
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                decrypt_session(secret, user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if user_dict.get('multi_user', False) is False and encrypted is False:
            encrypted = True
            sess_info['encrypted'] = encrypted
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                encrypt_session(secret, user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if len(interview_status.attachments) > 0:
            with resp.message(qoutput) as m:
                media_count = 0
                for attachment in interview_status.attachments:
                    if media_count >= 9:
                        break
                    for doc_format in attachment['formats_to_use']:
                        if media_count >= 9:
                            break
                        if doc_format not in ('pdf', 'rtf'):
                            continue
                        filename = attachment['filename'] + '.' + docassemble.base.parse.extension_of_doc_format[doc_format]
                        #saved_file = save_numbered_file(filename, attachment['file'][doc_format], yaml_file_name=sess_info['yaml_filename'], uid=sess_info['uid'])
                        url = re.sub(r'/$', r'', url_root) + url_for('serve_stored_file', uid=sess_info['uid'], number=attachment['file'][doc_format], filename=attachment['filename'], extension=docassemble.base.parse.extension_of_doc_format[doc_format])
                        #logmessage('sms: url is ' + str(url))
                        m.media(url)
                        media_count += 1
        else:
            resp.message(qoutput)
    release_lock(sess_info['uid'], sess_info['yaml_filename'])
    #logmessage(str(form))
    if 'uid' in session:
        del session['uid']
    return resp

def api_verify(req, roles=None):
    api_key = request.args.get('key', None)
    if api_key is None and request.method == 'POST':
        post_data = request.form.copy()
        if 'key' in post_data:
            api_key = post_data['key']
    if api_key is None:
        logmessage("api_verify: no API key provided")
        return False
    rkeys = r.keys('da:api:userid:*:key:' + api_key + ':info')
    if len(rkeys) == 0:
        logmessage("api_verify: API key not found")
        return False
    try:
        info = json.loads(r.get(rkeys[0]))
    except:
        logmessage("api_verify: API information could not be unpacked")
        return False
    m = re.match('da:api:userid:([0-9]+):key:' + api_key + ':info', rkeys[0])
    if not m:
        logmessage("api_verify: user id could not be extracted")
        return False
    user_id = m.group(1)
    if type(info) is not dict:
        logmessage("api_verify: API information was in the wrong format")
        return False
    if len(info['constraints']):
        if info['method'] == 'ip' and request.remote_addr not in info['constraints']:
            logmessage("api_verify: IP address " + str(request.remote_addr) + " did not match")
            return False
        if info['method'] == 'referer':
            if not request.referrer:
                logmessage("api_verify: could not authorize based on referer because no referer provided")
                return False
            matched = False
            for constraint in info['constraints']:
                constraint = re.sub(r'^[\*]+|[\*]+$', '', constraint)
                constraint = re.escape(constraint)
                constraint = re.sub(r'\\\*+', '.*', constraint)
                referer = re.sub(r'\?.*', '', request.referrer)
                if re.search(constraint, referer):
                    matched = True
                    break
            if not matched:
                logmessage("api_verify: authorization failure referer " + str(request.referrer) + " could not be matched")
                return False
    user = UserModel.query.filter_by(id=user_id).first()
    if user is None:
        logmessage("api_verify: user does not exist")
        return False
    if not user.active:
        logmessage("api_verify: user is no longer active")
        return False
    login_user(user, remember=False)
    if roles:
        ok_role = False
        for role in roles:
            if current_user.has_role(role):
                ok_role = True
                break
        if not ok_role:
            logmessage("api_verify: user did not have correct privileges for resource")
            return False
    return True
    
def jsonify_with_status(data, code):
    resp = jsonify(data)
    resp.status_code = code
    return resp

def true_or_false(text):
    if text is False or text == 0 or str(text).lower().strip() in ('0', 'false', 'f'):
        return False
    return True

def get_user_list(include_inactive=False):
    if not (current_user.is_authenticated and current_user.has_role('admin', 'advocate')):
        raise Exception("You cannot call get_user_list() unless you are an administrator or advocate")
    if include_inactive:
        the_users = UserModel.query.order_by(UserModel.id).all()
    else:
        the_users = UserModel.query.filter_by(active=True).order_by(UserModel.id).all()
    user_list = list()
    for user in the_users:
        user_info = dict(roles=[])
        for role in user.roles:
            user_info['roles'].append(role.name)
        for attrib in ('id', 'email', 'first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
            user_info[attrib] = getattr(user, attrib)
        if include_inactive:
            user_info['active'] = getattr(user, 'active')
        user_list.append(user_info)
    return user_list

@app.route('/api/user_list', methods=['GET'])
def api_user_list():
    if not api_verify(request, roles=['admin', 'advocate']):
        return jsonify_with_status("Access denied.", 403)
    include_inactive = true_or_false(request.args.get('include_inactive', False))
    user_list = get_user_list(include_inactive)
    return jsonify(user_list)

def get_user_info(user_id=None, email=None):
    if current_user.is_anonymous:
        raise Exception("You cannot call get_user_info() unless you are logged in")
    if user_id is None and email is None:
        user_id = current_user.id
    if not (current_user.has_role('admin', 'advocate')):
        if (user_id is not None and current_user.id != user_id) or (email is not None and current_user.email != email):
            raise Exception("You cannot call get_user_info() unless you are an administrator or advocate")
    user_info = dict(privileges=[])
    if user_id is not None:
        user = UserModel.query.filter_by(id=user_id).first()
    else:
        user = UserModel.query.filter_by(email=email).first()
    if user is None:
        return None
    for role in user.roles:
        user_info['privileges'].append(role.name)
    for attrib in ('id', 'email', 'first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language', 'active'):
        user_info[attrib] = getattr(user, attrib)
    return user_info    

def make_user_inactive(user_id=None, email=None):
    if current_user.is_anonymous:
        raise Exception("You cannot call make_user_inactive() unless you are logged in")
    if not (current_user.has_role('admin')):
        raise Exception("You cannot call make_user_inactive() unless you are an administrator")
    if user_id is None and email is None:
        raise Exception("You must call make_user_inactive() with a user ID or an e-mail address")
    if user_id is not None:
        user = UserModel.query.filter_by(id=user_id).first()
    else:
        user = UserModel.query.filter_by(email=email).first()
    if user is None:
        raise Exception("User not found")
    user.active = False
    db.session.commit()

@app.route('/api/user', methods=['GET', 'POST'])
@csrf.exempt
def api_user():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    try:
        user_info = get_user_info(user_id=current_user.id)
    except Exception as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status('User not found', 404)
    if request.method == 'GET':
        return jsonify(user_info)
    elif request.method == 'POST':
        post_data = request.form.copy()
        info = dict()
        for key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
            if key in post_data:
                info[key] = post_data[key]
        set_user_info(user_id=current_user.id, **info)
        return ('', 204)

@app.route('/api/user/privileges', methods=['GET'])
@csrf.exempt
def api_user_privileges():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    try:
        user_info = get_user_info(user_id=current_user.id)
    except Exception as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status('User not found', 404)
    if request.method == 'GET':
        return jsonify(user_info['privileges'])

@app.route('/api/user/<user_id>', methods=['GET', 'DELETE', 'POST'])
@csrf.exempt
def api_user_by_id(user_id):
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    try:
        user_id = int(user_id)
    except:
        return jsonify_with_status("User ID must be an integer.", 400)
    try:
        user_info = get_user_info(user_id=user_id)
    except Exception as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status("User not found.", 404)
    if request.method == 'GET':
        return jsonify(user_info)
    elif request.method == 'DELETE':
        make_user_inactive(user_id=user_id)
        return ('', 204)
    elif request.method == 'POST':
        post_data = request.form.copy()
        info = dict()
        for key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
            if key in post_data:
                info[key] = post_data[key]
        set_user_info(user_id=user_id, **info)
        return ('', 204)

@app.route('/api/privileges', methods=['GET', 'DELETE', 'POST'])
@csrf.exempt
def api_privileges():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    if request.method == 'GET':
        return jsonify(get_privileges_list())
    if request.method == 'DELETE':
        if not (current_user.has_role('admin')):
            return jsonify_with_status("Access denied.", 403)
        if 'privilege' not in request.args:
            return jsonify_with_status("A privilege name must be provided.", 400)
        try:
            remove_privilege(request.args['privilege'])
        except Exception as err:
            return jsonify_with_status(str(err), 400)
        return ('', 204)
    if request.method == 'POST':
        if not (current_user.has_role('admin')):
            return jsonify_with_status("Access denied.", 403)
        post_data = request.form.copy()
        if 'privilege' not in post_data:
            return jsonify_with_status("A privilege name must be provided.", 400)
        try:
            add_privilege(post_data['privilege'])
        except Exception as err:
            return jsonify_with_status(str(err), 400)
        return ('', 204)

def get_privileges_list():
    if not (current_user.has_role('admin', 'developer')):
        raise Exception('You must have admin or developer privileges to call get_privileges_list().')
    role_names = []
    for role in Role.query.order_by('name'):
        role_names.append(role.name)
    return role_names
    
def add_privilege(privilege):
    if not (current_user.has_role('admin')):
        raise Exception('You must have admin privileges to call add_privilege().')
    role_names = get_privileges_list()
    if privilege in role_names:
        raise Exception("The given privilege already exists.")
    db.session.add(Role(name=privilege))
    db.session.commit()

def remove_privilege(privilege):
    if not (current_user.has_role('admin')):
        raise Exception('You must have admin privileges to call remove_privilege().')
    if privilege in ['user', 'admin', 'developer', 'advocate', 'cron']:
        raise Exception('The specified privilege is built-in and cannot be deleted.')
    user_role = Role.query.filter_by(name='user').first()
    role = Role.query.filter_by(name=privilege).first()
    if role is None:
        raise Exception('The privilege ' + unicode(privilege) + ' did not exist.')
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

@app.route('/api/user/<user_id>/privileges', methods=['GET', 'DELETE', 'POST'])
@csrf.exempt
def api_user_by_id_privileges(user_id):
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    try:
        user_info = get_user_info(user_id=user_id)
    except Exception as err:
        return jsonify_with_status("Error obtaining user information: " + str(err), 400)
    if user_info is None:
        return jsonify_with_status('User not found', 404)
    if request.method == 'GET':
        return jsonify(user_info['privileges'])
    if request.method in ('DELETE', 'POST'):
        if not (current_user.has_role('admin')):
            return jsonify_with_status("Access denied.", 403)
        if request.method == 'DELETE':
            role_name = request.args.get('privilege', None)
            if role_name is None:
                return jsonify_with_status("A privilege name must be provided", 400)
            try:
                remove_user_privilege(user_id, role_name)
            except Exception as err:
                return jsonify_with_status(str(err), 400)
        elif request.method == 'POST':
            post_data = request.form.copy()
            role_name = post_data.get('privilege', None)
            if role_name is None:
                return jsonify_with_status("A privilege name must be provided", 400)
            try:
                add_user_privilege(user_id, role_name)
            except Exception as err:
                return jsonify_with_status(str(err), 400)
        db.session.commit()
        return ('', 204)

def add_user_privilege(user_id, privilege):
    if not (current_user.has_role('admin')):
        raise Exception('You must have admin privileges to call add_user_privilege().')
    if privilege not in get_privileges_list():
        raise Exception('The specified privilege does not exist.')
    user = UserModel.query.filter_by(id=user_id).first()
    if user is None:
        raise Exception("The specified user did not exist")
    for role in user.roles:
        if role.name == privilege:
            raise Exception("The user already had that privilege.")
    role_to_add = None
    for role in Role.query.order_by('id'):
        if role.name == privilege:
            role_to_add = role
    if role_to_add is None:
        raise Exception("The specified privilege did not exist.")
    user.roles.append(role_to_add)
    db.session.commit()

def remove_user_privilege(user_id, privilege):
    if not (current_user.has_role('admin')):
        raise Exception('You must have admin privileges to call remove_user_privilege().')
    if current_user.id == user_id and privilege == 'admin':
        raise Exception('You cannot take away the admin privilege from the current user.')
    if privilege not in get_privileges_list():
        raise Exception('The specified privilege does not exist.')
    user = UserModel.query.filter_by(id=user_id).first()
    if user is None:
        raise Exception("The specified user did not exist")
    role_to_remove = None
    for role in user.roles:
        if role.name == privilege:
            role_to_remove = role
    if role_to_remove is None:
        raise Exception("The user did not already have that privilege.")
    user.roles.remove(role_to_remove)
    db.session.commit()
    
def set_user_info(**kwargs):
    if current_user.is_anonymous:
        raise Exception("You cannot call set_user_info() unless you are logged in")
    user_id = kwargs.get('user_id', None)
    email = kwargs.get('email', None)
    if user_id is None and email is None:
        user_id = current_user.id
    if not (current_user.has_role('admin')):
        if (user_id is not None and current_user.id != user_id) or (email is not None and current_user.email != email):
            raise Exception("You cannot call set_user_info() unless you are an administrator")
    if user_id is not None:
        user = UserModel.query.filter_by(id=user_id).first()
    else:
        user = UserModel.query.filter_by(email=email).first()
    if user is None:
        raise Exception("User not found")
    for key, val in kwargs.iteritems():
        if key in ('first_name', 'last_name', 'country', 'subdivisionfirst', 'subdivisionsecond', 'subdivisionthird', 'organization', 'timezone', 'language'):
            setattr(user, key, val)
    if 'active' in kwargs:
        if type(kwargs['active']) is not bool:
            raise Exception("The active parameter must be True or False")
        if user.id == current_user.id:
            raise Exception("Cannot change active status of the current user.")
        user.active = kwargs['active']
    db.session.commit()
    if 'privileges' in kwargs and type(kwargs['privileges']) in (list, tuple):
        if len(kwargs['privileges']) == 0:
            raise Exception("Cannot remove all of a user's privileges.")
        roles_to_add = []
        roles_to_delete = []
        role_names = [role.name for role in user.roles]
        for role in role_names:
            if role not in kwargs['privileges']:
                roles_to_delete.append(role)
        for role in kwargs['privileges']:
            if role not in role_names:
                roles_to_add.append(role)
        for role in roles_to_delete:
            remove_user_privilege(user.id, role)
        for role in roles_to_add:
            add_user_privilege(user.id, role)
    
@app.route('/api/secret', methods=['GET'])
def api_get_secret():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    username = request.args.get('username', None)
    password = request.args.get('password', None)
    if username is None or password is None:
        return jsonify_with_status("A username and password must be supplied", 400)
    try:
        secret = get_secret(username, password)
    except Exception as err:
        return jsonify_with_status(str(err), 403)
    return jsonify(secret)
    
def get_secret(username, password):
    user = UserModel.query.filter_by(active=True, email=username).first()
    if user is None:
        raise Exception("Username not known")
    if daconfig.get('two factor authentication', False) is True and user.otp_secret is not None:
        raise Exception("Secret will not be supplied because two factor authentication is enabled")
    user_manager = current_app.user_manager
    if not user_manager.get_password(user):
        raise Exception("Password not set")
    if not user_manager.verify_password(password, user):
        raise Exception("Incorrect password")
    return pad_to_16(MD5Hash(data=password).hexdigest())

@app.route('/api/users/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
def api_users_interviews():
    if not api_verify(request, roles=['admin', 'advocate']):
        return jsonify_with_status("Access denied.", 403)
    user_id = request.args.get('user_id', None)
    filename = request.args.get('i', None)
    secret = request.args.get('secret', None)
    tag = request.args.get('tag', None)
    if secret is not None:
        secret = str(secret)
    if request.method == 'GET':
        include_dict = true_or_false(request.args.get('include_dictionary', False))
        try:
            the_list = user_interviews(user_id=user_id, secret=secret, exclude_invalid=False, tag=tag, filename=filename, include_dict=include_dict)
        except:
            return jsonify_with_status("Error getting interview list.", 400)
    elif request.method == 'DELETE':
        try:
            the_list = user_interviews(user_id=user_id, exclude_invalid=False, tag=tag, filename=filename)
        except:
            return jsonify_with_status("Error reading interview list.", 400)
        for info in the_list:
            user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
        return ('', 204)

@app.route('/api/user/<user_id>/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
def api_user_user_id_interviews(user_id):
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    if not (current_user.id == user_id or current_user.has_role('admin', 'advocate')):
        return jsonify_with_status("Access denied.", 403)
    filename = request.args.get('i', None)
    secret = request.args.get('secret', None)
    tag = request.args.get('tag', None)
    if secret is not None:
        secret = str(secret)
    include_dict = true_or_false(request.args.get('include_dictionary', False))
    if request.method == 'GET':
        try:
            the_list = user_interviews(user_id=user_id, secret=secret, exclude_invalid=False, tag=tag, filename=filename, include_dict=include_dict)
        except:
            return jsonify_with_status("Error reading interview list.", 400)
        return jsonify(docassemble.base.functions.safe_json(the_list))
    elif request.method == 'DELETE':
        try:
            the_list = user_interviews(user_id=user_id, exclude_invalid=False, tag=tag, filename=filename)
        except:
            return jsonify_with_status("Error reading interview list.", 400)
        for info in the_list:
            user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
        return ('', 204)

@app.route('/api/session/back', methods=['POST'])
@csrf.exempt
def api_session_back():
    post_data = request.form.copy()
    yaml_filename = post_data.get('i', None)
    session_id = post_data.get('session', None)
    secret = str(post_data.get('secret', None))
    reply_with_question = true_or_false(post_data.get('question', True))
    if yaml_filename is None or session_id is None:
        return jsonify_with_status("Parameters i and session are required.", 400)
    try:
        data = go_back_in_session(yaml_filename, session_id, secret=secret, return_question=reply_with_question)
    except Exception as the_err:
        return jsonify_with_status(str(the_err), 400)
    if data is None:
        return ('', 204)
    if data.get('questionType', None) is 'response':
        return data['response']
    return jsonify(**data)

@app.route('/api/session', methods=['GET', 'POST', 'DELETE'])
@csrf.exempt
def api_session():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    if request.method == 'GET':
        yaml_filename = request.args.get('i', None)
        session_id = request.args.get('session', None)
        secret = request.args.get('secret', None)
        if secret is not None:
            secret = str(secret)
        if yaml_filename is None or session_id is None:
            return jsonify_with_status("Parameters i and session are required.", 400)
        try:
            variables = get_session_variables(yaml_filename, session_id, secret=secret)
        except Exception as the_err:
            return jsonify_with_status(str(the_err), 400)
        return jsonify(variables)
    elif request.method == 'POST':
        post_data = request.form.copy()
        yaml_filename = post_data.get('i', None)
        session_id = post_data.get('session', None)
        secret = str(post_data.get('secret', None))
        reply_with_question = true_or_false(post_data.get('question', True))
        if yaml_filename is None or session_id is None:
            return jsonify_with_status("Parameters i and session are required.", 400)
        try:
            variables = json.loads(post_data.get('variables', '{}'))
        except:
            return jsonify_with_status("Malformed variables.", 400)
        try:
            file_variables = json.loads(post_data.get('file_variables', '{}'))
        except:
            return jsonify_with_status("Malformed list of file variables.", 400)
        try:
            del_variables = json.loads(post_data.get('delete_variables', '[]'))
        except:
            return jsonify_with_status("Malformed list of delete variables.", 400)
        if type(variables) is not dict:
            return jsonify_with_status("Variables data is not a dict.", 400)
        if type(file_variables) is not dict:
            return jsonify_with_status("File variables data is not a dict.", 400)
        if type(del_variables) is not list:
            return jsonify_with_status("Delete variables data is not a list.", 400)
        files = []
        literal_variables = dict()
        for filekey in request.files:
            if filekey not in file_variables:
                file_variables[filekey] = filekey
            the_files = request.files.getlist(filekey)
            files_to_process = []
            if the_files:
                for the_file in the_files:
                    filename = secure_filename(the_file.filename)
                    file_number = get_new_file_number(session_id, filename, yaml_file_name=yaml_filename)
                    extension, mimetype = get_ext_and_mimetype(filename)
                    saved_file = SavedFile(file_number, extension=extension, fix=True)
                    temp_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.' + extension, delete=False)
                    the_file.save(temp_file.name)
                    process_file(saved_file, temp_file.name, mimetype, extension)
                    files_to_process.append((filename, file_number, mimetype, extension))
            file_field = file_variables[filekey]
            if len(files_to_process) > 0:
                elements = list()
                indexno = 0
                for (filename, file_number, mimetype, extension) in files_to_process:
                    elements.append("docassemble.base.core.DAFile(" + repr(file_field + '[' + str(indexno) + ']') + ", filename=" + repr(filename) + ", number=" + str(file_number) + ", make_pngs=True, mimetype=" + repr(mimetype) + ", extension=" + repr(extension) + ")")
                    indexno += 1
                literal_variables[file_field] = "docassemble.base.core.DAFileList(" + repr(file_field) + ", elements=[" + ", ".join(elements) + "])"
            else:
                literal_variables[file_field] = "None"
        try:
            data = set_session_variables(yaml_filename, session_id, variables, secret=secret, return_question=reply_with_question, literal_variables=literal_variables, del_variables=del_variables)
        except Exception as the_err:
            return jsonify_with_status(str(the_err), 400)            
        if data is None:
            return ('', 204)
        if data.get('questionType', None) is 'response':
            return data['response']
        return jsonify(**data)
    elif request.method == 'DELETE':
        yaml_filename = request.args.get('i', None)
        session_id = request.args.get('session', None)
        if yaml_filename is None or session_id is None:
            return jsonify_with_status("Parameters i and session are required.", 400)
        user_interviews(action='delete', filename=yaml_filename, session=session_id)
        return ('', 204)

@app.route('/api/file/<file_number>', methods=['GET'])
def api_file(file_number):
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    if request.method == 'GET':
        yaml_filename = request.args.get('i', None)
        session_id = request.args.get('session', None)
        number = re.sub(r'[^0-9]', '', str(file_number))
        if current_user.is_authenticated and current_user.has_role('admin', 'advocate'):
            privileged = True
        else:
            privileged = False
        try:
            file_info = get_info_from_file_number(number, privileged=privileged)
        except:
            return ('File not found', 404)
        if 'path' not in file_info:
            return ('File not found', 404)
        else:
            if 'extension' in request.args:
                if os.path.isfile(file_info['path'] + '.' + request.args['extension']):
                    the_path = file_info['path'] + '.' + request.args['extension']
                    extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + request.args['extension'])
                else:
                    return ('File not found', 404)
            elif 'filename' in request.args:
                if os.path.isfile(os.path.join(os.path.dirname(file_info['path']), request.args['filename'])):
                    the_path = os.path.join(os.path.dirname(file_info['path']), request.args['filename'])
                    extension, mimetype = get_ext_and_mimetype(request.args['filename'])
                else:
                    return ('File not found', 404)
            else:
                the_path = file_info['path']
                mimetype = file_info['mimetype']
            response = send_file(the_path, mimetype=mimetype)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            return(response)
        return ('File not found', 404)
    
def get_session_variables(yaml_filename, session_id, secret=None, simplify=True):
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=str(secret))
    except Exception as the_err:
        raise Exception("Unable to decrypt interview dictionary: " + str(the_err))
    if user_dict is None:
        raise Exception("Unable to obtain interview dictionary.")
    if simplify:
        variables = docassemble.base.functions.serializable_dict(user_dict, include_internal=True)
        #variables['_internal'] = docassemble.base.functions.serializable_dict(user_dict['_internal'])
        return variables
    return user_dict

def go_back_in_session(yaml_filename, session_id, secret=None, return_question=False):
    obtain_lock(session_id, yaml_filename)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        release_lock(session_id, yaml_filename)
        raise Exception("Unable to decrypt interview dictionary.")
    if user_dict is None:
        release_lock(session_id, yaml_filename)
        raise Exception("Unable to obtain interview dictionary.")
    if steps == 1:
        release_lock(session_id, yaml_filename)
        raise Exception("Cannot go back.")
    old_user_dict = user_dict
    steps, user_dict, is_encrypted = fetch_previous_user_dict(session_id, yaml_filename, secret)
    if user_dict is None:
        release_lock(session_id, yaml_filename)
        raise Exception("Unable to obtain interview dictionary.")
    if return_question:
        try:
            data = get_question_data(yaml_filename, session_id, secret, use_lock=False, user_dict=user_dict, steps=steps, is_encrypted=is_encrypted, old_user_dict=old_user_dict)
        except Exception as the_err:
            release_lock(session_id, yaml_filename)
            raise Exception("Problem getting current question:" + str(the_err))
        release_lock(session_id, yaml_filename)
    else:
        data = None
    return data

def set_session_variables(yaml_filename, session_id, variables, secret=None, return_question=False, literal_variables=None, del_variables=None):
    obtain_lock(session_id, yaml_filename)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        release_lock(session_id, yaml_filename)
        raise Exception("Unable to decrypt interview dictionary.")
    if user_dict is None:
        release_lock(session_id, yaml_filename)
        raise Exception("Unable to obtain interview dictionary.")
    try:
        for key, val in variables.iteritems():
            exec(unicode(key) + ' = ' + repr(val), user_dict)
    except Exception as the_err:
        release_lock(session_id, yaml_filename)
        raise Exception("Problem deleting variables:" + str(the_err))
    if literal_variables is not None:
        exec('import docassemble.base.core', user_dict)
        for key, val in literal_variables.iteritems():
            exec(unicode(key) + ' = ' + val, user_dict)
    if del_variables is not None:
        try:
            for key in del_variables:
                exec('del ' + unicode(key), user_dict)
        except Exception as the_err:
            release_lock(session_id, yaml_filename)
            raise Exception("Problem deleting variables: " + str(the_err))
    if return_question:
        try:
            data = get_question_data(yaml_filename, session_id, secret, use_lock=False, user_dict=user_dict, steps=steps, is_encrypted=is_encrypted)
        except Exception as the_err:
            release_lock(session_id, yaml_filename)
            raise Exception("Problem getting current question:" + str(the_err))
    else:
        data = None
    steps += 1
    save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=True, steps=steps)
    release_lock(session_id, yaml_filename)
    return data

@app.route('/api/session/new', methods=['GET'])
def api_session_new():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    yaml_filename = request.args.get('i', None)
    if yaml_filename is None:
        return jsonify_with_status("Parameter i is required.", 400)
    secret = request.args.get('secret', None)
    if secret is None:
        new_secret = True
        secret = random_string(16)
    else:
        new_secret = False
    secret = str(secret)
    url_args = dict()
    for argname in request.args:
        if argname in ('i', 'secret', 'key'):
            continue
        if re.match('[A-Za-z_][A-Za-z0-9_]*', argname):
            url_args[argname] = request.args[argname]
    try:
        (encrypted, session_id) = create_new_interview(yaml_filename, secret, url_args=url_args, request=request)
    except Exception as err:
        return jsonify_with_status(str(err), 400)
    if encrypted and new_secret:
        return jsonify(dict(session=session_id, i=yaml_filename, secret=secret, encrypted=encrypted))
    else:
        return jsonify(dict(session=session_id, i=yaml_filename, encrypted=encrypted))
        
def create_new_interview(yaml_filename, secret, url_args=None, request=None):
    session_id, user_dict = reset_session(yaml_filename, secret)
    add_referer(user_dict)
    if url_args:
        for key, val in url_args.iteritems():
            exec("url_args['" + key + "'] = " + repr(val.encode('unicode_escape')), user_dict)
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    ci = current_info(yaml=yaml_filename, req=request)
    ci['session'] = session_id
    ci['encrypted'] = True
    interview_status = docassemble.base.parse.InterviewStatus(current_info=ci)
    interview_status.checkin = True
    try:
        interview.assemble(user_dict, interview_status)
    except DAErrorMissingVariable as err:
        pass
    except Exception as e:
        release_lock(session_id, yaml_filename)
        raise Exception("Failure to assemble interview: " + str(e))
    if user_dict.get('multi_user', False) is True:
        encrypted = False
    else:
        encrypted = True
    save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=encrypted, changed=False, steps=1)
    release_lock(session_id, yaml_filename)
    return (encrypted, session_id)

@app.route('/api/session/question', methods=['GET'])
def api_session_question():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    yaml_filename = request.args.get('i', None)
    session_id = request.args.get('session', None)
    secret = request.args.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if yaml_filename is None or session_id is None:
        return jsonify_with_status("Parameters i and session are required.", 400)
    try:
        data = get_question_data(yaml_filename, session_id, secret)
    except Exception as err:
        return jsonify_with_status(str(err), 400)
    if data.get('questionType', None) is 'response':
        return data['response']
    return jsonify(**data)    

def get_question_data(yaml_filename, session_id, secret, use_lock=True, user_dict=None, steps=None, is_encrypted=None, old_user_dict=None):
    if use_lock:
        obtain_lock(session_id, yaml_filename)
        try:
            steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
        except Exception as err:
            release_lock(session_id, yaml_filename)
            raise Exception("Unable to obtain interview dictionary")
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    ci = current_info(yaml=yaml_filename, req=request)
    ci['session'] = session_id
    ci['encrypted'] = is_encrypted
    interview_status = docassemble.base.parse.InterviewStatus(current_info=ci)
    interview_status.checkin = True
    try:
        if old_user_dict is not None:
            interview.assemble(user_dict, interview_status, old_user_dict)
        else:
            interview.assemble(user_dict, interview_status)
    except DAErrorMissingVariable as err:
        if use_lock:
            save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=False, steps=steps)
            release_lock(session_id, yaml_filename)
        return dict(questionType='undefined_variable', variable=err.variable, message_log=docassemble.base.functions.get_message_log())
    except Exception as e:
        if use_lock:
            release_lock(session_id, yaml_filename)
        raise Exception("Failure to assemble interview: " + str(e))
    if use_lock:
        save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=False, steps=steps)
        release_lock(session_id, yaml_filename)
    if interview_status.question.question_type == "response":
        if hasattr(interview_status.question, 'all_variables'):
            if hasattr(interview_status.question, 'include_internal'):
                include_internal = interview_status.question.include_internal
            else:
                include_internal = False
            response_to_send = make_response(docassemble.base.functions.dict_as_json(user_dict, include_internal=include_internal).encode('utf8'), '200 OK')
        elif hasattr(interview_status.question, 'binaryresponse'):
            response_to_send = make_response(interview_status.question.binaryresponse, '200 OK')
        else:
            response_to_send = make_response(interview_status.questionText.encode('utf8'), '200 OK')
        response_to_send.headers['Content-Type'] = interview_status.extras['content_type']
        return dict(questionType='response', response=response_to_send)
    elif interview_status.question.question_type == "sendfile":
        if interview_status.question.response_file is not None:
            the_path = interview_status.question.response_file.path()
        else:
            return jsonify_with_status("Could not send file because the response was None", 404)
        if not os.path.isfile(the_path):
            return jsonify_with_status("Could not send file because " + str(the_path) + " not found", 404)
        response_to_send = send_file(the_path, mimetype=interview_status.extras['content_type'])
        response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return dict(questionType='response', response=response_to_send)
    if interview_status.question.language != '*':
        interview_language = interview_status.question.language
    else:
        interview_language = DEFAULT_LANGUAGE
    title_info = interview_status.question.interview.get_title(user_dict)
    interview_status.exit_link = title_info.get('exit link', 'exit')
    interview_status.exit_label = title_info.get('exit label', 'Exit')
    interview_status.title = title_info.get('full', default_title)
    interview_status.display_title = title_info.get('logo', interview_status.title)
    interview_status.tabtitle = title_info.get('tab', interview_status.title)
    interview_status.short_title = title_info.get('short', title_info.get('full', default_short_title))
    interview_status.display_short_title = title_info.get('logo', interview_status.short_title)
    the_main_page_parts = main_page_parts.get(interview_language, main_page_parts.get('*'))
    interview_status.pre = title_info.get('pre', the_main_page_parts['main page pre'])
    interview_status.post = title_info.get('post', the_main_page_parts['main page post'])
    interview_status.submit = title_info.get('submit', the_main_page_parts['main page submit'])
    if interview_status.question.can_go_back and (steps - user_dict['_internal']['steps_offset']) > 1:
        allow_going_back = True
    else:
        allow_going_back = False
    data = dict(browser_title=interview_status.tabtitle, exit_link=interview_status.exit_link, exit_label=interview_status.exit_label, title=interview_status.title, display_title=interview_status.display_title, short_title=interview_status.short_title, lang=interview_language, steps=steps, allow_going_back=allow_going_back, message_log=docassemble.base.functions.get_message_log())
    data.update(interview_status.as_data(encode=False))
    #if interview_status.question.question_type == "review" and len(interview_status.question.fields_used):
    #    next_action_review = dict(action=list(interview_status.question.fields_used)[0], arguments=dict())
    #else:
    #    next_action_review = None
    if 'reload_after' in interview_status.extras:
        reload_after = 1000 * int(interview_status.extras['reload_after'])
    else:
        reload_after = 0
    #if next_action_review:
    #    data['next_action'] = next_action_review
    if reload_after and reload_after > 0:
        data['reload_after'] = reload_after
    for key in data.keys():
        if key == "_question_name":
            data['questionName'] = data[key]
            del data[key]
        elif key.startswith('_'):
            del data[key]
    return data

@app.route('/api/session/action', methods=['POST'])
@csrf.exempt
def api_session_action():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    post_data = request.form.copy()
    yaml_filename = post_data.get('i', None)
    session_id = post_data.get('session', None)
    secret = post_data.get('secret', None)
    action = post_data.get('action', None)
    if yaml_filename is None or session_id is None or action is None:
        return jsonify_with_status("Parameters i, session, and action are required.", 400)
    secret = str(secret)
    if 'arguments' in post_data:
        try:
            arguments = json.loads(post_data.get('arguments', dict()))
        except:
            return jsonify_with_status("Malformed arguments.", 400)
        if type(arguments) is not dict:
            return jsonify_with_status("Arguments data is not a dict.", 400)
    else:
        arguments = dict()
    obtain_lock(session_id, yaml_filename)
    try:
        steps, user_dict, is_encrypted = fetch_user_dict(session_id, yaml_filename, secret=secret)
    except:
        release_lock(session_id, yaml_filename)
        return jsonify_with_status("Unable to obtain interview dictionary.", 400)
    interview = docassemble.base.interview_cache.get_interview(yaml_filename)
    ci = current_info(yaml=yaml_filename, req=request, action=dict(action=action, arguments=arguments))
    ci['session'] = session_id
    ci['encrypted'] = is_encrypted
    interview_status = docassemble.base.parse.InterviewStatus(current_info=ci)
    interview_status.checkin = True
    try:
        interview.assemble(user_dict, interview_status)
    except DAErrorMissingVariable as err:
        steps += 1
        save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=True, steps=steps)
        release_lock(session_id, yaml_filename)
        return ('', 204)        
    except Exception as e:
        release_lock(session_id, yaml_filename)
        return jsonify_with_status("Failure to assemble interview: " + str(e), 400)
    steps += 1
    save_user_dict(session_id, user_dict, yaml_filename, secret=secret, encrypt=is_encrypted, changed=True, steps=steps)
    release_lock(session_id, yaml_filename)
    if interview_status.question.question_type == "response":
        if hasattr(interview_status.question, 'all_variables'):
            if hasattr(interview_status.question, 'include_internal'):
                include_internal = interview_status.question.include_internal
            else:
                include_internal = False
            response_to_send = make_response(docassemble.base.functions.dict_as_json(user_dict, include_internal=include_internal).encode('utf8'), '200 OK')
        elif hasattr(interview_status.question, 'binaryresponse'):
            response_to_send = make_response(interview_status.question.binaryresponse, '200 OK')
        else:
            response_to_send = make_response(interview_status.questionText.encode('utf8'), '200 OK')
        response_to_send.headers['Content-Type'] = interview_status.extras['content_type']
        return response_to_send
    elif interview_status.question.question_type == "sendfile":
        if interview_status.question.response_file is not None:
            the_path = interview_status.question.response_file.path()
        else:
            return jsonify_with_status("Could not send file because the response was None", 404)
        if not os.path.isfile(the_path):
            return jsonify_with_status("Could not send file because " + str(the_path) + " not found", 404)
        response_to_send = send_file(the_path, mimetype=interview_status.extras['content_type'])
        response_to_send.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response_to_send
    else:
        return ('', 204)
    
@app.route('/api/list', methods=['GET'])
def api_list():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    return jsonify(interview_menu(absolute_urls=true_or_false(request.args.get('absolute_urls', True))))

@app.route('/api/user/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
def api_user_interviews():
    if not api_verify(request):
        return jsonify_with_status("Access denied.", 403)
    filename = request.args.get('i', None)
    session = request.args.get('session', None)
    tag = request.args.get('tag', None)
    secret = request.args.get('secret', None)
    if secret is not None:
        secret = str(secret)
    include_dict = true_or_false(request.args.get('include_dictionary', False))
    if request.method == 'GET':
        try:
            the_list = user_interviews(user_id=current_user.id, secret=secret, filename=filename, session=session, exclude_invalid=False, tag=tag, include_dict=include_dict)
        except:
            return jsonify_with_status("Error reading interview list.", 400)            
        return jsonify(docassemble.base.functions.safe_json(the_list))
    elif request.method == 'DELETE':
        try:
            the_list = user_interviews(user_id=current_user.id, filename=filename, session=session, exclude_invalid=False, tag=tag)
        except:
            return jsonify_with_status("Error reading interview list.", 400)
        for info in the_list:
            user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
        return ('', 204)

@app.route('/api/interviews', methods=['GET', 'DELETE'])
@csrf.exempt
def api_interviews():
    if not api_verify(request, roles=['admin', 'advocate']):
        return jsonify_with_status("Access denied.", 403)
    filename = request.args.get('i', None)
    session = request.args.get('session', None)
    tag = request.args.get('tag', None)
    secret = request.args.get('secret', None)
    if secret is not None:
        secret = str(secret)
    include_dict = true_or_false(request.args.get('include_dictionary', False))
    if request.method == 'GET':
        try:
            the_list = user_interviews(secret=secret, filename=filename, session=session, exclude_invalid=False, tag=tag, include_dict=include_dict)
        except Exception as err:
            return jsonify_with_status("Error reading interview list: " + str(err), 400)            
        return jsonify(docassemble.base.functions.safe_json(the_list))
    elif request.method == 'DELETE':
        try:
            the_list = user_interviews(filename=filename, session=session, exclude_invalid=False, tag=tag)
        except:
            return jsonify_with_status("Error reading interview list.", 400)
        for info in the_list:
            user_interviews(user_id=info['user_id'], action='delete', filename=info['filename'], session=info['session'])
        return ('', 204)

@app.route('/manage_api', methods=['GET', 'POST'])
@login_required
def manage_api():
    if not current_user.has_role(*daconfig.get('api privileges', ['admin', 'developer'])):
        abort(404)
    form = APIKey(request.form)
    action = request.args.get('action', None)
    api_key = request.args.get('key', None)
    argu = dict()
    argu['mode'] = 'list'
    if action is None:
        action = 'list'
    argu['form'] = form
    argu['extra_js'] = Markup("""
<script>
  function remove_constraint(elem){
    $(elem).parents('.constraintlist div').remove();
    fix_constraints();
  }
  function fix_constraints(){
    var empty;
    var filled_exist = 0;
    var empty_exist = 0;
    if ($("#method").val() == 'none'){
      $(".constraintlist").hide();
      return;
    }
    else{
      $(".constraintlist").show();
    }
    $(".constraintlist input").each(function(){
      if ($(this).val() == ''){
        empty_exist = 1;
      }
      else{
        filled_exist = 1;
      }
      if (!($(this).next().length)){
        var inner_div = $('<div>');
        $(inner_div).addClass('input-group-append');
        var new_button = $('<button>');
        var new_i = $('<i>');
        $(new_button).addClass('btn btn-outline-secondary');
        $(new_i).addClass('fas fa-times');
        $(new_button).append(new_i);
        $(new_button).on('click', function(){remove_constraint(this);});
        $(inner_div).append(new_button);
        $(this).parent().append(inner_div);
      }
    });
    if (empty_exist == 0){
      var new_div = $('<div>');
      var inner_div = $('<div>');
      var new_input = $('<input>');
      $(new_div).append(new_input);
      $(new_div).addClass('input-group');
      $(inner_div).addClass('input-group-append');
      $(new_input).addClass('form-control');
      $(new_input).attr('type', 'text');
      if ($("#method").val() == 'ip'){
        $(new_input).attr('placeholder', """ + json.dumps(word('e.g., 56.33.114.49')) + """);
      }
      else{
        $(new_input).attr('placeholder', """ + json.dumps(word('e.g., *example.com')) + """);
      }
      $(new_input).on('change', fix_constraints);
      $(new_input).on('keyup', fix_constraints);
      $(".constraintlist").append(new_div);
      var new_button = $('<button>');
      var new_i = $('<i>');
      $(new_button).addClass('btn btn-outline-secondary');
      $(new_i).addClass('fas fa-times');
      $(new_button).append(new_i);
      $(new_button).on('click', function(){remove_constraint(this);});
      $(inner_div).append(new_button);
      $(new_div).append(inner_div);
    }
  }
  $( document ).ready(function(){
    $(".constraintlist input").on('change', fix_constraints);
    $("#method").on('change', function(){
      $(".constraintlist div.input-group").remove();
      fix_constraints();
    });
    $("#submit").on('click', function(){
      var the_constraints = [];
      $(".constraintlist input").each(function(){
        if ($(this).val() != ''){
          the_constraints.push($(this).val());
        }
      });
      $("#security").val(JSON.stringify(the_constraints));
    });
    fix_constraints();
  });
</script>
""")
    form.method.choices = [('ip', 'IP Address'), ('referer', 'Referring URL'), ('none', 'No authentication')]
    if request.method == 'POST' and form.validate():
        action = form.action.data
        try:
            constraints = json.loads(form.security.data)
            if type(constraints) is not list:
                constraints = []
        except:
            constraints = []
        if action == 'new':
            argu['title'] = word("New API Key")
            argu['tab_title'] = argu['title']
            argu['page_title'] = argu['title']
            info = json.dumps(dict(name=form.name.data, method=form.method.data, constraints=constraints))
            success = False
            for attempt in range(10):
                api_key = random_alphanumeric(32)
                if not len(r.keys('da:api:userid:*:key:' + api_key + ':info')):
                    r.set('da:api:userid:' + str(current_user.id) + ':key:' + api_key + ':info', info)
                    success = True
                    break
            if not success:
                flash(word("Could not create new key"), 'error')
                return render_template('pages/manage_api.html', **argu)
            argu['description'] = Markup(word("Your new API key, known internally as") + " " + form.name.data + ", " + word("is") + " <code>" + api_key + "</code>.")
        elif action == 'edit':
            argu['title'] = word("Edit API Key")
            argu['tab_title'] = argu['title']
            argu['page_title'] = argu['title']
            api_key = form.key.data
            argu['api_key'] = api_key
            rkey = 'da:api:userid:' + str(current_user.id) + ':key:' + str(form.key.data) + ':info'
            existing_key = r.get(rkey)
            if existing_key is None:
                flash(word("The key no longer exists"), 'error')
                return render_template('pages/manage_api.html', **argu)
            if form.delete.data:
                r.delete(rkey)
                flash(word("The key was deleted"), 'error')
            else:
                try:
                    info = json.loads(existing_key)
                except:
                    flash(word("The key no longer exists"), 'error')
                    return render_template('pages/manage_api.html', **argu)
                info['name'] = form.name.data
                if form.method.data != info['method'] and form.method.data in ('ip', 'referer'):
                    info['method'] = form.method.data
                info['constraints'] = constraints
                r.set(rkey, json.dumps(info))
        action = 'list'
    if action == 'new':
        argu['title'] = word("New API Key")
        argu['tab_title'] = argu['title']
        argu['page_title'] = argu['title']
        argu['mode'] = 'new'
    if api_key is not None and action == 'edit':
        argu['title'] = word("Edit API Key")
        argu['tab_title'] = argu['title']
        argu['page_title'] = argu['title']
        argu['api_key'] = api_key
        argu['mode'] = 'edit'
        rkey = 'da:api:userid:' + str(current_user.id) + ':key:' + api_key + ':info'
        info = r.get(rkey)
        if info is not None:
            info = json.loads(info)
            if type(info) is dict and info.get('name', None) and info.get('method', None):
                argu['method'] = info.get('method')
                form.method.data = info.get('method')
                form.action.data = 'edit'
                form.key.data = api_key
                form.name.data = info.get('name')
                argu['constraints'] = info.get('constraints')
    if action == 'list':
        argu['title'] = word("API Keys")
        argu['tab_title'] = argu['title']
        argu['page_title'] = argu['title']
        argu['mode'] = 'list'
        avail_keys = list()
        for rkey in r.keys('da:api:userid:' + str(current_user.id) + ':key:*:info'):
            try:
                info = json.loads(r.get(rkey))
                if type(info) is not dict:
                    logmessage("manage_api: response from redis was not a dict")
                    continue
            except:
                logmessage("manage_api: response from redis had invalid json")
                continue
            m = re.match(r'da:api:userid:[0-9]+:key:([^:]+):info', rkey)
            if not m:
                logmessage("manage_api: error with redis key")
                continue
            api_key = m.group(1)
            info['api_key'] = api_key
            avail_keys.append(info)
        argu['avail_keys'] = avail_keys
        argu['has_any_keys'] = True if len(avail_keys) > 0 else False
    return render_template('pages/manage_api.html', **argu)

@app.route('/me', methods=['GET'])
def whoami():
    if current_user.is_authenticated:
        return jsonify(logged_in=True, user_id=current_user.id, email=current_user.email, roles=[role.name for role in current_user.roles], firstname=current_user.first_name, lastname=current_user.last_name, country=current_user.country, subdivisionfirst=current_user.subdivisionfirst, subdivisionsecond=current_user.subdivisionsecond, subdivisionthird=current_user.subdivisionthird, organization=current_user.organization, timezone=current_user.timezone)
    else:
        return jsonify(logged_in=False)

def retrieve_email(email_id):
    email = Email.query.filter_by(id=email_id).first()
    if email is None:
        raise DAError("E-mail did not exist")
    short_record = Shortener.query.filter_by(short=email.short).first()
    if short_record.user_id is not None:
        user = UserModel.query.filter_by(id=short_record.user_id, active=True).first()
    else:
        user = None
    if short_record is None:
        raise DAError("Short code did not exist")
    return get_email_obj(email, short_record, user)

class AddressEmail(object):
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return unicode(self.address)

def retrieve_emails(**pargs):
    key = pargs.get('key', None)
    index = pargs.get('index', None)
    if key is None and index is not None:
        raise DAError("retrieve_emails: if you provide an index you must provide a key")
    if 'i' in pargs:
        yaml_filename = pargs['i']
    else:
        yaml_filename = session.get('i', None)
    if 'uid' in pargs:
        uid = pargs['uid']
    else:
        uid = session.get('uid', None)
    if 'user_id' in pargs:
        user_id = pargs['user_id']
        temp_user_id = None
    elif 'temp_user_id' in pargs:
        user_id = None
        temp_user_id = pargs['temp_user_id']
    elif current_user.is_anonymous:
        user_id = None
        temp_user_id = session.get('tempuser', None)
    else:
        user_id = current_user.id
        temp_user_id = None
    user_cache = user_id_dict()
    results = list()
    if key is None:
        the_query = Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id).order_by(Shortener.modtime)
    else:
        if index is None:
            the_query = Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key).order_by(Shortener.modtime)
        else:
            the_query = Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key, index=index).order_by(Shortener.modtime)
    for record in the_query:
        result_for_short = AddressEmail()
        result_for_short.address = record.short
        result_for_short.key = record.key
        result_for_short.index = record.index
        result_for_short.emails = list()
        if record.user_id is not None:
            user = user_cache[record.user_id]
            result_for_short.owner = user.email
        else:
            user = None
            result_for_short.owner = None
        for email in Email.query.filter_by(short=record.short).order_by(Email.datetime_received):
            result_for_short.emails.append(get_email_obj(email, record, user))
        results.append(result_for_short)
    return results

def get_email_obj(email, short_record, user):
    email_obj = DAEmail(short=email.short)
    email_obj.key = short_record.key
    email_obj.index = short_record.index
    email_obj.initializeAttribute('to_address', DAEmailRecipientList, json.loads(email.to_addr), gathered=True)
    email_obj.initializeAttribute('cc_address', DAEmailRecipientList, json.loads(email.cc_addr), gathered=True)
    email_obj.initializeAttribute('from_address', DAEmailRecipient, **json.loads(email.from_addr))
    email_obj.initializeAttribute('reply_to', DAEmailRecipient, **json.loads(email.reply_to_addr))
    email_obj.initializeAttribute('return_path', DAEmailRecipient, **json.loads(email.return_path_addr))
    email_obj.subject = email.subject
    email_obj.datetime_message = email.datetime_message
    email_obj.datetime_received = email.datetime_received
    email_obj.initializeAttribute('attachment', DAFileList, gathered=True)
    if user is None:
        email_obj.address_owner = None
    else:
        email_obj.address_owner = user.email
    for attachment_record in EmailAttachment.query.filter_by(email_id=email.id).order_by(EmailAttachment.index):
        #sys.stderr.write("Attachment record is " + str(attachment_record.id) + "\n")
        upload = Uploads.query.filter_by(indexno=attachment_record.upload).first()
        if upload is None:
            continue
        #sys.stderr.write("Filename is " + upload.filename + "\n")
        saved_file_att = SavedFile(attachment_record.upload, extension=attachment_record.extension, fix=True)
        process_file(saved_file_att, saved_file_att.path, attachment_record.content_type, attachment_record.extension, initial=False)
        extension, mimetype = get_ext_and_mimetype(upload.filename)
        if upload.filename == 'headers.json':
            #sys.stderr.write("Processing headers\n")
            email_obj.initializeAttribute('headers', DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
        elif upload.filename == 'attachment.txt' and attachment_record.index < 3:
            #sys.stderr.write("Processing body text\n")
            email_obj.initializeAttribute('body_text', DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
        elif upload.filename == 'attachment.html' and attachment_record.index < 3:
            email_obj.initializeAttribute('body_html', DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
        else:
            email_obj.attachment.appendObject(DAFile, mimetype=mimetype, extension=extension, number=attachment_record.upload)
    if not hasattr(email_obj, 'headers'):
        email_obj.headers = None
    if not hasattr(email_obj, 'body_text'):
        email_obj.body_text = None
    if not hasattr(email_obj, 'body_html'):
        email_obj.body_html = None
    return email_obj

def da_send_fax(fax_number, the_file, config):
    if twilio_config is None:
        logmessage("da_send_fax: ignoring call to da_send_fax because Twilio not enabled")
        return None
    if config not in twilio_config['name'] or 'fax' not in twilio_config['name'][config] or twilio_config['name'][config]['fax'] in (False, None):
        logmessage("da_send_fax: ignoring call to da_send_fax because fax feature not enabled")
        return None
    account_sid = twilio_config['name'][config].get('account sid', None)
    auth_token = twilio_config['name'][config].get('auth token', None)
    from_number = twilio_config['name'][config].get('number', None)
    if account_sid is None or auth_token is None or from_number is None:
        logmessage("da_send_fax: ignoring call to da_send_fax because account sid, auth token, and/or number missing")
        return None
    client = TwilioRestClient(account_sid, auth_token)
    fax = client.fax.v1.faxes.create(
        from_=from_number,
        to=fax_number,
        media_url=the_file.url_for(temporary=True, seconds=600),
        status_callback=url_for('fax_callback', _external=True)
    )
    return fax.sid

def write_pypirc():
    pypirc_file = daconfig.get('pypirc path', '/var/www/.pypirc')
    #pypi_username = daconfig.get('pypi username', None)
    #pypi_password = daconfig.get('pypi password', None)
    pypi_url = daconfig.get('pypi url', 'https://upload.pypi.org/legacy/')
    # if pypi_username is None or pypi_password is None:
    #     return
    if os.path.isfile(pypirc_file):
        with open(pypirc_file, 'rU') as fp:
            existing_content = fp.read()
    else:
        existing_content = None
    content = """\
[distutils]
index-servers =
  pypi

[pypi]
repository: """ + pypi_url + "\n"
#     """
# username: """ + pypi_username + """
# password: """ + pypi_password + "\n"
    if existing_content != content:
        with open(pypirc_file, 'w') as fp:
            fp.write(content)
        os.chmod(pypirc_file, stat.S_IRUSR | stat.S_IWUSR)
    
def pypi_status(packagename):
    result = dict()
    pypi_url = daconfig.get('pypi url', 'https://pypi.python.org/pypi')
    try:
        handle = urllib2.urlopen(pypi_url + '/' + str(packagename) + '/json')
    except urllib2.HTTPError, e:
        if e.code == 404:
            result['error'] = False
            result['exists'] = False
        else:
            result['error'] = e.code
    except Exception, e:
        result['error'] = str(e)
    else:
        try:
            result['info'] = json.load(handle)
        except:
            result['error'] = 'json'
        else:
            result['error'] = False
            result['exists'] = True
    return result

def secure_filename(filename):
    filename = werkzeug.secure_filename(filename)
    extension, mimetype = get_ext_and_mimetype(filename)
    filename = re.sub(r'\..*', '', filename) + '.' + extension
    return filename

def get_short_code(**pargs):
    key = pargs.get('key', None)
    index = pargs.get('index', None)
    if key is None and index is not None:
        raise DAError("get_short_code: if you provide an index you must provide a key")
    if 'i' in pargs:
        yaml_filename = pargs['i']
    else:
        yaml_filename = session.get('i', None)
    if 'uid' in pargs:
        uid = pargs['uid']
    else:
        uid = session.get('uid', None)
    if 'user_id' in pargs:
        user_id = pargs['user_id']
        temp_user_id = None
    elif 'temp_user_id' in pargs:
        user_id = None
        temp_user_id = pargs['temp_user_id']
    elif current_user.is_anonymous:
        user_id = None
        temp_user_id = session.get('tempuser', None)
    else:
        user_id = current_user.id
        temp_user_id = None
    short_code = None
    for record in Shortener.query.filter_by(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, key=key, index=index):
        short_code = record.short
    if short_code is not None:
        return short_code
    counter = 0
    new_record = None
    while counter < 20:
        existing_id = None
        new_short = random_lower_string(6)
        for record in Shortener.query.filter_by(short=new_short):
            existing_id = record.id
        if existing_id is None:
            new_record = Shortener(filename=yaml_filename, uid=uid, user_id=user_id, temp_user_id=temp_user_id, short=new_short, key=key, index=index)
            db.session.add(new_record)
            db.session.commit()
            break
        counter += 1
    if new_record is None:
        raise SystemError("Failed to generate unique short code")
    return new_short

def error_notification(err, message=None, history=None, trace=None, referer=None, the_request=None, the_vars=None):
    recipient_email = daconfig.get('error notification email', None)
    if not recipient_email:
        return
    if err.__class__.__name__ in ('CSRFError', 'ClientDisconnected'):
        return
    if message is None:
        errmess = unicode(err)
    else:
        errmess = message
    try:
        email_address = current_user.email
    except:
        email_address = None
    if the_request:
        try:
            referer = unicode(the_request.referrer)
        except:
            referer = None
        try:
            ipaddress = the_request.remote_addr
        except:
            ipaddress = None
    else:
        referer = None
        ipaddress = None
    if daconfig.get('error notification variables', DEBUG):
        if the_vars is None:
            try:
                the_vars = docassemble.base.functions.all_variables(include_internal=True)
            except:
                pass
    else:
        the_vars = None
    json_filename = None
    if the_vars is not None and len(the_vars):
        try:
            with tempfile.NamedTemporaryFile(prefix="datemp", suffix='.json', delete=False) as fp:
                fp.write(json.dumps(the_vars, sort_keys=True, indent=2).encode('utf8'))
                json_filename = fp.name
        except Exception as the_err:
            pass
    interview_path = docassemble.base.functions.interview_path()
    try:
        the_key = 'da:errornotification:' + str(ipaddress)
        existing = r.get(the_key)
        pipe = r.pipeline()
        pipe.set(the_key, 1)
        pipe.expire(the_key, 60)
        pipe.execute()
        if existing:
            return
    except:
        pass
    try:
        try:
            body = "There was an error in the " + app.config['APP_NAME'] + " application.\n\nThe error message was:\n\n" + err.__class__.__name__ + ": " + unicode(errmess)
            if trace is not None:
                body += "\n\n" + unicode(trace)
            if history is not None:
                body += "\n\n" + BeautifulSoup(history, "html.parser").get_text('\n')
            if referer is not None and referer != 'None':
                body += "\n\nThe referer URL was " + unicode(referer)
            elif interview_path is not None:
                body += "\n\nThe interview was " + unicode(interview_path)
            if email_address is not None:
                body += "\n\nThe user was " + unicode(email_address)
            html = "<html>\n  <body>\n    <p>There was an error in the " + app.config['APP_NAME'] + " application.</p>\n    <p>The error message was:</p>\n<pre>" + err.__class__.__name__ + ": " + unicode(errmess)
            if trace is not None:
                html += "\n\n" + unicode(trace)
            html += "</pre>\n"
            if history is not None:
                html += unicode(history)
            if referer is not None and referer != 'None':
                html += "<p>The referer URL was " + unicode(referer) + "</p>"
            elif interview_path is not None:
                body += "<p>The interview was " + unicode(interview_path) + "</p>"
            if email_address is not None:
                body += "<p>The user was " + unicode(email_address) + "</p>"
            html += "\n  </body>\n</html>"
            msg = Message(app.config['APP_NAME'] + " error: " + err.__class__.__name__, recipients=[recipient_email], body=body, html=html)
            if json_filename:
                with open(json_filename, 'rb') as fp:
                    msg.attach('variables.json', 'application/json', fp.read())
            da_send_mail(msg)
        except Exception as zerr:
            logmessage(unicode(zerr))
            body = "There was an error in the " + app.config['APP_NAME'] + " application."
            html = "<html>\n  <body>\n    <p>There was an error in the " + app.config['APP_NAME'] + " application.</p>\n  </body>\n</html>"
            msg = Message(app.config['APP_NAME'] + " error: " + err.__class__.__name__, recipients=[recipient_email], body=body, html=html)
            if json_filename:
                with open(json_filename, 'rb') as fp:
                    msg.attach('variables.json', 'application/json', fp.read())
            da_send_mail(msg)
    except:
        pass

for path in (FULL_PACKAGE_DIRECTORY, UPLOAD_DIRECTORY, LOG_DIRECTORY): #PACKAGE_CACHE
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            sys.exit("Could not create path: " + path)
    if not os.access(path, os.W_OK):
        sys.exit("Unable to create files in directory: " + path)
if not os.access(WEBAPP_PATH, os.W_OK):
    sys.exit("Unable to modify the timestamp of the WSGI file: " + WEBAPP_PATH)

from docassemble.webapp.daredis import r, r_user
#r = redis.StrictRedis(host=docassemble.base.util.redis_server, db=0)
#docassemble.base.functions.set_server_redis(r)

#docassemble.base.util.set_twilio_config(twilio_config)
docassemble.base.functions.update_server(url_finder=get_url_from_file_reference,
                                         navigation_bar=navigation_bar,
                                         chat_partners_available=chat_partners_available,
                                         get_chat_log=get_current_chat_log,
                                         sms_body=sms_body,
                                         send_fax=da_send_fax,
                                         get_sms_session=get_sms_session,
                                         initiate_sms_session=initiate_sms_session,
                                         terminate_sms_session=terminate_sms_session,
                                         twilio_config=twilio_config,
                                         server_redis=r,
                                         server_redis_user=r_user,
                                         user_id_dict=user_id_dict,
                                         retrieve_emails=retrieve_emails,
                                         get_short_code=get_short_code,
                                         make_png_for_pdf=make_png_for_pdf,
                                         task_ready=task_ready,
                                         wait_for_task=wait_for_task,
                                         user_interviews=user_interviews,
                                         interview_menu=interview_menu,
                                         get_user_list=get_user_list,
                                         get_user_info=get_user_info,
                                         set_user_info=set_user_info,
                                         make_user_inactive=make_user_inactive,
                                         get_secret=get_secret,
                                         get_session_variables=get_session_variables,
                                         go_back_in_session=go_back_in_session,
                                         set_session_variables=set_session_variables,
                                         get_privileges_list=get_privileges_list,
                                         add_privilege=add_privilege,
                                         remove_privilege=remove_privilege,
                                         add_user_privilege=add_user_privilege,
                                         remove_user_privilege=remove_user_privilege,
                                         file_set_attributes=file_set_attributes,
                                         fg_make_png_for_pdf=fg_make_png_for_pdf,
                                         fg_make_png_for_pdf_path=fg_make_png_for_pdf_path,
                                         fg_make_pdf_for_word_path=fg_make_pdf_for_word_path)
#docassemble.base.util.set_user_id_function(user_id_dict)
#docassemble.base.functions.set_generate_csrf(generate_csrf)
#docassemble.base.parse.set_url_finder(get_url_from_file_reference)
#docassemble.base.parse.set_url_for(url_for)
#APPLICATION_NAME = 'docassemble'

base_words = get_base_words()
title_documentation = get_title_documentation()
documentation_dict = get_documentation_dict()
base_name_info = get_name_info()
for val in base_name_info:
    base_name_info[val]['name'] = val
    if 'insert' not in base_name_info[val]:
        base_name_info[val]['insert'] = val
    if 'show' not in base_name_info[val]:
        base_name_info[val]['show'] = False
    if 'exclude' not in base_name_info[val]:
        base_name_info[val]['exclude'] = False

#docassemble.base.functions.set_chat_partners_available(chat_partners_available)

password_secret_key = daconfig.get('password secretkey', app.secret_key)

sys_logger = logging.getLogger('docassemble')
sys_logger.setLevel(logging.DEBUG)

LOGFORMAT = 'docassemble: ip=%(clientip)s i=%(yamlfile)s uid=%(session)s user=%(user)s %(message)s'

if LOGSERVER is None:
    docassemble_log_handler = logging.FileHandler(filename=os.path.join(LOG_DIRECTORY, 'docassemble.log'))
    sys_logger.addHandler(docassemble_log_handler)
else:
    import logging.handlers
    handler = logging.handlers.SysLogHandler(address=(LOGSERVER, 514), socktype=socket.SOCK_STREAM)
    sys_logger.addHandler(handler)

if not in_celery:
    if LOGSERVER is None:
        docassemble.base.logger.set_logmessage(syslog_message_with_timestamp)
    else:
        docassemble.base.logger.set_logmessage(syslog_message)

def null_func(*pargs, **kwargs):
    logmessage("Null function called")
    return None

if in_celery:
    docassemble.base.functions.update_server(bg_action=null_func,
                                             #async_ocr=null_func,
                                             ocr_page=null_func,
                                             ocr_finalize=null_func,
                                             worker_convert=null_func)
else:
    import docassemble.webapp.worker
    #sys.stderr.write("calling set worker now\n")
    docassemble.base.functions.update_server(bg_action=docassemble.webapp.worker.background_action,
                                             #async_ocr=docassemble.webapp.worker.async_ocr,
                                             chord=docassemble.webapp.worker.chord,
                                             ocr_page=docassemble.webapp.worker.ocr_page,
                                             ocr_finalize=docassemble.webapp.worker.ocr_finalize,
                                             worker_convert=docassemble.webapp.worker.convert)

pg_ex = dict()

global_css = ''
        
global_js = ''

def define_examples():
    if 'encoded_example_html' in pg_ex:
        return
    example_html = list()
    example_html.append('        <div class="col-md-2">\n          <h5 class="mb-1">Example blocks</h5>')
    pg_ex['pg_first_id'] = list()
    data_dict = dict()
    make_example_html(get_examples(), pg_ex['pg_first_id'], example_html, data_dict)
    example_html.append('        </div>')
    example_html.append('        <div class="col-md-4 example-source-col"><h5 class="mb-1">' + word('Source') + '<a href="#" tabindex="0" class="badge badge-success example-copy">' + word("Insert") + '</a></h5><div id="example-source-before" class="invisible"></div><div id="example-source"></div><div id="example-source-after" class="invisible"></div><div><a tabindex="0" class="example-hider" id="show-full-example">' + word("Show context of example") + '</a><a tabindex="0" class="example-hider invisible" id="hide-full-example">' + word("Hide context of example") + '</a></div></div>')
    example_html.append('        <div class="col-md-6"><h5 class="mb-1">' + word("Preview") + '<a href="#" target="_blank" class="badge badge-primary example-documentation example-hidden" id="example-documentation-link">' + word("View documentation") + '</a></h5><a href="#" target="_blank" id="example-image-link"><img title=' + json.dumps(word("Click to try this interview")) + ' class="example_screenshot" id="example-image"></a></div>')
    pg_ex['encoded_data_dict'] = safeid(json.dumps(data_dict))
    pg_ex['encoded_example_html'] = Markup("\n".join(example_html))

if LooseVersion(min_system_version) > LooseVersion(daconfig['system version']):
    version_warning = word("A new docassemble system version is available.  If you are using Docker, install a new Docker image.")
else:
    version_warning = None

import docassemble.webapp.machinelearning
docassemble.base.util.set_knn_machine_learner(docassemble.webapp.machinelearning.SimpleTextMachineLearner)
docassemble.base.util.set_svm_machine_learner(docassemble.webapp.machinelearning.SVMMachineLearner)
docassemble.base.util.set_random_forest_machine_learner(docassemble.webapp.machinelearning.RandomForestMachineLearner)
docassemble.base.util.set_machine_learning_entry(docassemble.webapp.machinelearning.MachineLearningEntry)

from docassemble.webapp.users.models import UserAuthModel, UserModel, UserDict, UserDictKeys, TempUser, ChatLog

def random_social():
    while True:
        new_social = 'local$' + random_alphanumeric(32)
        existing_user = UserModel.query.filter_by(social_id=new_social).first()
        if existing_user:
            continue
        break
    return new_social

with app.app_context():
    app.user_manager.random_social = random_social
    if 'bootstrap theme' in daconfig and daconfig['bootstrap theme']:
        app.config['BOOTSTRAP_THEME'] = get_url_from_file_reference(daconfig['bootstrap theme'])
        app.config['BOOTSTRAP_THEME_DEFAULT'] = False
    else:
        app.config['BOOTSTRAP_THEME'] = None
        app.config['BOOTSTRAP_THEME_DEFAULT'] = True
    if 'global css' in daconfig:
        for fileref in daconfig['global css']:
            global_css += "\n" + '    <link href="' + get_url_from_file_reference(fileref) + '" rel="stylesheet">'
    if 'global javascript' in daconfig:
        for fileref in daconfig['global javascript']:
            global_js += "\n" + '    <script src="' + get_url_from_file_reference(fileref) + '"></script>';
    if 'raw global css' in daconfig:
        global_css += "\n" + daconfig['raw global css']
    if 'raw global javascript' in daconfig:
        global_js += "\n" + daconfig['raw global javascript']
    app.config['GLOBAL_CSS'] = global_css
    app.config['GLOBAL_JS'] = global_js
    app.config['PARTS'] = page_parts
    copy_playground_modules()
    write_pypirc()

if __name__ == "__main__":
    app.run()
