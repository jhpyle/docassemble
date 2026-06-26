from flask import redirect, request
from rauth import OAuth2Service
from docassemble.base.error import DAException
from docassemble.webapp.config import daconfig
from .helpers import safe_json_loads
from .oauth import OAuthSignIn

class KeycloakSignIn(OAuthSignIn):

    def __init__(self):
        super().__init__('keycloak')
        try:
            realm = daconfig['oauth']['keycloak']['realm']
        except:
            realm = None
        try:
            protocol = daconfig['oauth']['keycloak']['protocol']
        except KeyError:
            protocol = 'https://'
        if not protocol.endswith('://'):
            protocol = protocol + '://'
        self.service = OAuth2Service(
            name='keycloak',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=protocol + str(self.consumer_domain) + '/realms/' + str(realm) + '/protocol/openid-connect/auth',
            access_token_url=protocol + str(self.consumer_domain) + '/realms/' + str(realm) + '/protocol/openid-connect/token',
            base_url=protocol + str(self.consumer_domain)
        )

    def authorize(self):
        if 'oauth' in daconfig and 'keycloak' in daconfig['oauth'] and daconfig['oauth']['keycloak'].get('enable', True) and self.consumer_domain is None:
            raise DAException("To use keycloak, you need to set your domain in the configuration.")
        return redirect(self.service.get_authorize_url(
            response_type='code',
            scope='openid profile email',
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
        me = oauth_session.get('realms/' + daconfig['oauth']['keycloak']['realm'] + '/protocol/openid-connect/userinfo').json()
        # logmessage("keycloak returned " + json.dumps(me))
        user_id = me.get('sub')
        social_id = 'keycloak$' + str(user_id)
        username = me.get('preferred_username')
        email = me.get('email')
        if email is None and '@' in username:
            email = username
        if user_id is None or username is None or email is None:
            raise DAException("Error: could not get necessary information from keycloak")
        info_dict = {'name': me.get('name', None)}
        if 'given_name' in me:
            info_dict['first_name'] = me.get('given_name')
        if 'family_name' in me:
            info_dict['last_name'] = me.get('family_name')
        return social_id, username, email, info_dict
