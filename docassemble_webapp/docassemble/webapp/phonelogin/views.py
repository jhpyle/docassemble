from flask import (
    current_app,
    request,
    redirect,
    render_template,
    flash,
    session,
    Blueprint,
)
from flask_login import login_user
from sqlalchemy import select
from docassemble.base.functions import phone_number_in_e164, phone_number_is_valid
from docassemble.base.generate_key import random_digits
from docassemble.base.language.words import word
from docassemble.base.thread_context import this_thread
from docassemble.base.util import send_sms
from docassemble.webapp.config import daconfig
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.interview.helpers import (
    sub_temp_user_dict_key,
    substitute_secret,
    save_user_dict_key,
)
from docassemble.webapp.sessions import update_session, get_session
from docassemble.webapp.users.helpers import update_last_login
from docassemble.webapp.users.models import UserModel
from docassemble.webapp.utils.helpers import (
    detect_mobile,
    get_requester_ip,
    MD5Hash,
    pad_to_16,
    url_for,
    current_info,
)
from docassemble.webapp.utils.logger import logmessage
from .forms import PhoneLoginVerifyForm, PhoneLoginForm

phonelogin_bp = Blueprint(
    'phonelogin',
    __name__,
    template_folder='templates'
)

@phonelogin_bp.route('/phone_login', methods=['POST', 'GET'])
def phone_login():
    if not current_app.config['USE_PHONE_LOGIN']:
        return ('File not found', 404)
    form = PhoneLoginForm(request.form)
    # next = request.args.get('next', url_for('admin.interview_list'))
    if request.method == 'POST' and form.submit.data:
        ok = True
        if form.validate():
            phone_number = form.phone_number.data
            if phone_number_is_valid(phone_number):
                phone_number = phone_number_in_e164(phone_number)
            else:
                ok = False
        else:
            ok = False
        if ok:
            social_id = 'phone$' + str(phone_number)
            user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(social_id=social_id)).scalar()
            if user and user.active is False:
                flash(word("Your account has been disabled."), 'error')
                return redirect(url_for('phonelogin.phone_login'))
            verification_code = random_digits(daconfig['verification code digits'])
            message = word("Your verification code is") + " " + str(verification_code) + "."
            user_agent = request.headers.get('User-Agent', '')
            if detect_mobile.search(user_agent):
                message += '  ' + word("You can also follow this link: ") + url_for('phonelogin.phone_login_verify', _external=True, p=phone_number, c=verification_code)
            tracker_prefix = 'da:phonelogin:ip:' + str(get_requester_ip(request)) + ':phone:'
            tracker_key = tracker_prefix + str(phone_number)
            pipe = r.pipeline()
            pipe.incr(tracker_key)
            pipe.expire(tracker_key, daconfig['ban period'])
            pipe.execute()
            total_attempts = 0
            for key in r.keys(tracker_prefix + '*'):
                val = r.get(key.decode())
                total_attempts += int(val)
            if total_attempts > daconfig['attempt limit']:
                logmessage("IP address " + str(get_requester_ip(request)) + " attempted to log in too many times.")
                flash(word("You have made too many login attempts."), 'error')
                return redirect(url_for('user.login'))
            total_attempts = 0
            for key in r.keys('da:phonelogin:ip:*:phone:' + phone_number):
                val = r.get(key.decode())
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
            # logmessage("Writing code " + str(verification_code) + " to " + key)
            this_thread.current_info = current_info(req=request)
            success = send_sms(to=phone_number, body=message)
            if success:
                session['phone_number'] = phone_number
                return redirect(url_for('phonelogin.phone_login_verify'))
            flash(word("There was a problem sending you a text message.  Please log in another way."), 'error')
            return redirect(url_for('user.login'))
        flash(word("Please enter a valid phone number"), 'error')
    return render_template('phonelogin/phone_login.html', form=form, version_warning=None, title=word("Sign in with your mobile phone"), tab_title=word("Sign In"), page_title=word("Sign in"))


@phonelogin_bp.route('/pv', methods=['POST', 'GET'])
def phone_login_verify():
    if not current_app.config['USE_PHONE_LOGIN']:
        return ('File not found', 404)
    phone_number = session.get('phone_number', request.args.get('p', None))
    if phone_number is None:
        return ('File not found', 404)
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
            user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(social_id=social_id)).scalar()
            if user and user.active is False:
                flash(word("Your account has been disabled."), 'error')
                return redirect(url_for('phonelogin.phone_login'))
            if not user:
                user = UserModel(social_id=social_id, nickname=phone_number, active=True)
                db.session.add(user)
                db.session.commit()
            login_user(user, remember=False)
            update_last_login(user)
            r.delete('da:phonelogin:ip:' + str(get_requester_ip(request)) + ':phone:' + phone_number)
            to_convert = []
            if 'i' in session:  # TEMPORARY
                get_session(session['i'])
            if 'tempuser' in session:
                to_convert.extend(sub_temp_user_dict_key(session['tempuser'], user.id))
            if 'sessions' in session:
                for filename, info in session['sessions'].items():
                    if (filename, info['uid']) not in to_convert:
                        to_convert.append((filename, info['uid']))
                        save_user_dict_key(info['uid'], filename, priors=True, user=user)
                        update_session(filename, key_logged=True)
            secret = substitute_secret(str(request.cookies.get('secret', None)), pad_to_16(MD5Hash(data=social_id).hexdigest()), user=user, to_convert=to_convert)
            response = redirect(url_for('admin.interview_list', from_login='1'))
            response.set_cookie('secret', secret, httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'])
            return response
        logmessage("IP address " + str(get_requester_ip(request)) + " made a failed login attempt using phone number " + str(phone_number) + ".")
        flash(word("Your verification code is invalid or expired.  Please try again."), 'error')
        return redirect(url_for('user.login'))
    return render_template('phonelogin/phone_login_verify.html', form=form, version_warning=None, title=word("Verify your phone"), tab_title=word("Enter code"), page_title=word("Enter code"), description=word("We just sent you a text message with a verification code.  Enter the verification code to proceed."))
