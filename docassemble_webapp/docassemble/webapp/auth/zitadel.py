import re
import base64
import hashlib
from flask import redirect, request, session
from rauth import OAuth2Service
from docassemble.base.generate_key import random_alphanumeric
from .helpers import safe_json_loads
from .oauth import OAuthSignIn

class ZitadelSignIn(OAuthSignIn):

    def __init__(self):
        super().__init__('zitadel')
        self.service = OAuth2Service(
            name='zitadel',
            client_id=self.consumer_id,
            client_secret=None,
            authorize_url='https://' + str(self.consumer_domain) + '/oauth/v2/authorize',
            access_token_url='https://' + str(self.consumer_domain) + '/oauth/v2/token',
            base_url='https://' + str(self.consumer_domain)
        )

    def authorize(self):
        session['zitadel_verifier'] = random_alphanumeric(43)
        code_challenge = base64.b64encode(hashlib.sha256(session['zitadel_verifier'].encode()).digest()).decode()
        code_challenge = re.sub(r'\+', '-', code_challenge)
        code_challenge = re.sub(r'/', '_', code_challenge)
        code_challenge = re.sub(r'=', '', code_challenge)
        the_url = self.service.get_authorize_url(
            scope='openid email profile',
            response_type='code',
            redirect_uri=self.get_callback_url(),
            code_challenge=code_challenge,
            code_challenge_method='S256')
        return redirect(the_url)

    def callback(self):
        if 'code' not in request.args or 'zitadel_verifier' not in session:
            return None, None, None, None
        the_data = {'code': request.args['code'],
                    'grant_type': 'authorization_code',
                    'code_verifier': session['zitadel_verifier'],
                    'redirect_uri': self.get_callback_url()}
        oauth_session = self.service.get_auth_session(
            decoder=safe_json_loads,
            data=the_data
        )
        me = oauth_session.get('oidc/v1/userinfo').json()
        del session['zitadel_verifier']
        return (
            'zitadel$' + str(me['sub']),
            me.get('email').split('@')[0],
            me.get('email'),
            {'first_name': me.get('given_name', None),
             'last_name': me.get('family_name', None),
             'name': me.get('name', None),
             'language': me.get('locale', None)}
        )
