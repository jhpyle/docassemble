from flask import redirect, request
from rauth import OAuth2Service
from .helpers import safe_json_loads
from .oauth import OAuthSignIn

class FacebookSignIn(OAuthSignIn):

    def __init__(self):
        super().__init__('facebook')
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
            decoder=safe_json_loads,
            data={'code': request.args['code'],
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me', params={'fields': 'id,name,first_name,middle_name,last_name,name_format,email'}).json()
        # logmessage("Facebook: returned " + json.dumps(me))
        return (
            'facebook$' + str(me['id']),
            me.get('email').split('@')[0],
            me.get('email'),
            {'first_name': me.get('first_name', None),
             'last_name': me.get('last_name', None),
             'name': me.get('name', None)}
        )
