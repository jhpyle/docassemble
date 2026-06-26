from flask import current_app
from docassemble.webapp.utils.hooks import url_for

class OAuthSignIn:
    providers = {}
    providers_obtained = False

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'].get(provider_name, {})
        self.consumer_id = credentials.get('id', None)
        self.consumer_secret = credentials.get('secret', None)
        self.consumer_domain = credentials.get('domain', None)

    def authorize(self):
        pass

    def enabled(self):
        return current_app.config.get(f"USE_{self.provider_name.upper()}_LOGIN", False)

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('auth.oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if not cls.providers_obtained:
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
            cls.providers_obtained = True
        return cls.providers[provider_name]
