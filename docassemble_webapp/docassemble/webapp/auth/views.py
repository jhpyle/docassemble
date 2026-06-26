# pylint: disable=unused-import
# ruff: noqa: F401
import re
from flask import abort, flash, current_app, redirect, request, session
from flask_login import current_user, login_user
from sqlalchemy import select
from docassemble.base.language.words import word
from docassemble.webapp.config import daconfig
from docassemble.webapp.app_object import flaskapp as app
from docassemble.webapp.extensions import csrf
from docassemble.webapp.extensions import db
from docassemble.webapp.interview.helpers import (
    sub_temp_user_dict_key,
    sub_temp_other,
    substitute_secret,
    save_user_dict_key,
)
from docassemble.webapp.sessions import update_session, get_session
from docassemble.webapp.users.helpers import update_last_login
from docassemble.webapp.users.models import UserModel
from docassemble.webapp.utils.helpers import verify_email, MD5Hash, pad_to_16
from docassemble.webapp.utils.hooks import url_for
from .blueprint import auth_bp
from .oauth import OAuthSignIn

if app.config.get('USE_GOOGLE_LOGIN'):
    from . import google
if app.config.get('USE_FACEBOOK_LOGIN'):
    from . import facebook
if app.config.get('USE_ZITADEL_LOGIN'):
    from . import zitadel
if app.config.get('USE_AUTH0_LOGIN'):
    from . import auth0
if app.config.get('USE_KEYCLOAK_LOGIN'):
    from . import keycloak
if app.config.get('USE_AUTHENTIK_LOGIN'):
    from . import authentik
if app.config.get('USE_AZURE_LOGIN'):
    from . import azure
if app.config.get('USE_MINIORANGE_LOGIN'):
    from . import miniorange

@auth_bp.route('/authorize/<provider>', methods=['POST', 'GET'])
@csrf.exempt
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(current_app.user_manager.make_safe_url_function(request.args.get('next', url_for('admin.interview_list', from_login='1'))))
    oauth = OAuthSignIn.get_provider(provider)
    next_url = current_app.user_manager.make_safe_url_function(request.args.get('next', ''))
    if next_url:
        session['next'] = next_url
    return oauth.authorize()


@auth_bp.route('/callback/<provider>', methods=['POST', 'GET'])
@csrf.exempt
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('admin.interview_list', from_login='1'))
    if request.method == 'POST' and provider != 'google':
        return ('The method is not allowed for the requested URL.', 405)
    # for argument in request.args:
    #     logmessage("argument " + str(argument) + " is " + str(request.args[argument]))
    try:
        oauth = OAuthSignIn.get_provider(provider)
    except KeyError:
        abort(404)
    if not oauth.enabled():
        abort(404)
    social_id, username, email, name_data = oauth.callback()
    if not verify_email(email):
        flash(word('E-mail addresses with this domain are not authorized to register for accounts on this system.'), 'error')
        return redirect(url_for('user.login'))
    if social_id is None:
        flash(word('Authentication failed.'), 'error')
        return redirect(url_for('admin.interview_list', from_login='1'))
    user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(social_id=social_id)).scalar()
    if not user:
        user = db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).where(UserModel.email.ilike(email))).scalar()
        if user and not user.social_id.startswith('local') and not daconfig.get('allow external auth with multiple methods', False) and social_id.split('$')[0] != user.social_id.split('$')[0]:
            flash(word('There is already an account on the system with the e-mail address') + " " + str(email) + ".  " + word("Please log in to that account."), 'error')
            return redirect(url_for('user.login'))
    if user and user.social_id is not None and user.social_id.startswith('local') and not daconfig.get('allow external auth to bypass local auth', False):
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
        if 'language' in name_data and name_data['language']:
            user.language = name_data['language']
        db.session.add(user)
        db.session.commit()
    session["_flashes"] = []
    login_user(user, remember=False)
    update_last_login(user)
    if 'i' in session:  # TEMPORARY
        get_session(session['i'])
    to_convert = []
    if 'tempuser' in session:
        to_convert.extend(sub_temp_user_dict_key(session['tempuser'], user.id))
    if 'sessions' in session:
        for filename, info in session['sessions'].items():
            if (filename, info['uid']) not in to_convert:
                to_convert.append((filename, info['uid']))
                save_user_dict_key(info['uid'], filename, priors=True, user=user)
                update_session(filename, key_logged=True)
    # logmessage("oauth_callback: calling substitute_secret")
    secret = substitute_secret(str(request.cookies.get('secret', None)), pad_to_16(MD5Hash(data=social_id).hexdigest()), to_convert=to_convert)
    sub_temp_other(user)
    if 'next' in session:
        the_url = session['next']
        del session['next']
        response = redirect(the_url)
    else:
        response = redirect(url_for('admin.interview_list', from_login='1'))
    response.set_cookie('secret', secret, httponly=True, secure=current_app.config['SESSION_COOKIE_SECURE'], samesite=current_app.config['SESSION_COOKIE_SAMESITE'])
    return response
