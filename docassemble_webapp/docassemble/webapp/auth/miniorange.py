from flask import redirect, request, session
from rauth import OAuth2Service
from docassemble.base.generate_key import random_alphanumeric
from .helpers import safe_json_loads
from .oauth import OAuthSignIn

class MiniOrangeOAuthSignIn(OAuthSignIn):

    def __init__(self):
        super().__init__('miniorange')
        self.service = OAuth2Service(
            name='azure',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://' + str(self.consumer_domain) + '/wp-json/moserver/authorize',
            access_token_url='https://' + str(self.consumer_domain) + '/wp-json/moserver/token',
            base_url='https://' + str(self.consumer_domain)
        )

    def authorize(self):
        session['miniorange_verifier'] = random_alphanumeric(43)
        return redirect(self.service.get_authorize_url(
            response_type='code',
            client_id=self.consumer_id,
            redirect_uri=self.get_callback_url(),
            scope='openid profile email',
            state=session['miniorange_verifier'])
        )

    def callback(self):
        if 'code' not in request.args or 'miniorange_verifier' not in session:
            return None, None, None, None
        the_state = request.args.get('state', '')
        if the_state != session['miniorange_verifier']:
            del session['miniorange_verifier']
            return None, None, None, None
        the_data = {'code': request.args['code'],
                    'grant_type': 'authorization_code',
                    'client_id': self.consumer_id,
                    'client_secret': self.consumer_secret,
                    'redirect_uri': self.get_callback_url()}
        oauth_session = self.service.get_auth_session(
            decoder=safe_json_loads,
            data=the_data
        )
        me = oauth_session.get('wp-json/moserver/resource').json()
        del session['miniorange_verifier']
        return (
            'miniorange$' + str(me['id']),
            me.get('email').split('@')[0],
            me.get('email'),
            {'first_name': me.get('first_name', None),
             'last_name': me.get('last_name', None),
             'name': (me.get('first_name', '') + ' ' + me.get('last_name', '')).strip()}
        )
