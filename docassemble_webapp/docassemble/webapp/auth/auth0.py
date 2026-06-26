from flask import redirect, request
from rauth import OAuth2Service
from docassemble.base.error import DAException
from docassemble.webapp.config import daconfig
from .helpers import safe_json_loads
from .oauth import OAuthSignIn

class Auth0SignIn(OAuthSignIn):

    def __init__(self):
        super().__init__('auth0')
        self.service = OAuth2Service(
            name='auth0',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://' + str(self.consumer_domain) + '/authorize',
            access_token_url='https://' + str(self.consumer_domain) + '/oauth/token',
            base_url='https://' + str(self.consumer_domain)
        )

    def authorize(self):
        if 'oauth' in daconfig and 'auth0' in daconfig['oauth'] and daconfig['oauth']['auth0'].get('enable', True) and self.consumer_domain is None:
            raise DAException("To use Auth0, you need to set your domain in the configuration.")
        audience_domain = daconfig['oauth']['auth0'].get('audience domain') or self.consumer_domain
        return redirect(self.service.get_authorize_url(
            response_type='code',
            scope='openid profile email',
            audience=f'https://{audience_domain}/userinfo',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None, None
        oauth_session = self.service.get_auth_session(
            decoder=safe_json_loads,
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('userinfo').json()
        # logmessage("Auth0 returned " + json.dumps(me))
        user_id = me.get('sub', me.get('user_id'))
        social_id = 'auth0$' + str(user_id)
        username = me.get('name')
        email = me.get('email')
        if user_id is None or username is None or email is None:
            raise DAException("Error: could not get necessary information from Auth0")
        return social_id, username, email, {'name': me.get('name', None)}
