from flask import request, current_app, render_template
from rauth import OAuth2Service
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from docassemble.base.language.words import word
from docassemble.base.error import DAException
from docassemble.webapp.utils.logger import logmessage
from . import auth_bp
from .oauth import OAuthSignIn

class GoogleSignIn(OAuthSignIn):

    def __init__(self):
        super().__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=None,
            access_token_url=None,
            base_url=None
        )

    def authorize(self):
        pass

    def callback(self):
        # logmessage("GoogleCallback, args: " + str([str(arg) + ": " + str(request.args[arg]) for arg in request.args]))
        # logmessage("GoogleCallback, request: " + str(request.data))
        csrf_cookie = request.cookies.get('g_csrf_token', None)
        post_data = request.form.copy()
        csrf_body = post_data.get('g_csrf_token', None)
        token = post_data.get('credential', None)
        if token is None or csrf_cookie is None or csrf_cookie != csrf_body or not current_app.config['USE_GOOGLE_LOGIN']:
            logmessage("Google authentication problem")
            return (None, None, None, None)
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), current_app.config['OAUTH_CREDENTIALS']['google']['id'])
        except ValueError:
            logmessage("Google ID did not verify")
            return (None, None, None, None)
        google_id = idinfo.get('sub', None)
        email = idinfo.get('email', None)
        google_name = idinfo.get('name', None)
        first_name = idinfo.get('given_name', None)
        last_name = idinfo.get('family_name', None)
        if email is not None and google_id is not None:
            return (
                'google$' + str(google_id),
                email.split('@')[0],
                email,
                {'name': google_name, 'first_name': first_name, 'last_name': last_name}
            )
        raise DAException("Could not get Google authorization information")


@auth_bp.route('/user/google-sign-in')
def google_page():
    return render_template('auth/google_login.html', version_warning=None, title=word("Sign In"), tab_title=word("Sign In"), page_title=word("Sign in"))
