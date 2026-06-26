from flask import redirect, request
from rauth import OAuth2Service
from .helpers import safe_json_loads
from .oauth import OAuthSignIn

class AzureSignIn(OAuthSignIn):

    def __init__(self):
        super().__init__('azure')
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
            decoder=safe_json_loads,
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
