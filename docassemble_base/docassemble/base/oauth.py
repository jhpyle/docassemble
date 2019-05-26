from docassemble.base.util import DARedis, user_info, DAObject, get_config, interview_url, response, message, log
import oauth2client.client
import json
import string
import random
import httplib2
import re
from six import text_type

__all__ = ['DAOAuth']

def random_string(length):
    r = random.SystemRandom()
    return ''.join(r.choice(string.ascii_letters) for i in range(length))

class DAOAuth(DAObject):
    """A base class for performing OAuth2 authorization in an interview"""
    def init(self, *pargs, **kwargs):
        if 'url_args' not in kwargs:
            raise Exception("DAOAuth: you must pass the url_args as a keyword parameter")
        self.url_args = kwargs['url_args']
        del kwargs['url_args']
        super(DAOAuth, self).init(*pargs, **kwargs)
    def get_flow(self):
        app_credentials = get_config('oauth', dict()).get(self.appname, dict())
        client_id = app_credentials.get('id', None)
        client_secret = app_credentials.get('secret', None)
        if client_id is None or client_secret is None:
            raise Exception('The application ' + self.appname + " is not configured in the Configuration")
        flow = oauth2client.client.OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope=self.scope,
            redirect_uri=re.sub(r'\?.*', '', interview_url()),
            auth_uri=self.auth_uri,
            token_uri=self.token_uri,
            access_type='offline',
            prompt='consent')
        return flow
    def get_credentials(self):
        r = DARedis()
        r_key = 'da:' + self.appname + ':status:user:' + user_info().email
        stored_state = r.get(r_key)
        if stored_state is not None:
            if 'code' in self.url_args and 'state' in self.url_args:
                r.delete(r_key)
                if self.url_args['state'] != stored_state.decode():
                    raise Exception("State did not match")
                flow = self.get_flow()
                credentials = flow.step2_exchange(self.url_args['code'])
                storage = RedisCredStorage(self.appname)
                storage.put(credentials)
                del self.url_args['code']
                del self.url_args['state']
            else:
                message("Please wait.", "You are in the process of authenticating.")
        storage = RedisCredStorage(self.appname)
        credentials = storage.get()
        if not credentials or credentials.invalid:
            state_string = random_string(16)
            pipe = r.pipeline()
            pipe.set(r_key, state_string)
            pipe.expire(r_key, 60)
            pipe.execute()
            flow = self.get_flow()
            uri = flow.step1_get_authorize_url(state=state_string)
            if 'state' in self.url_args:
                del self.url_args['state']
            if 'code' in self.url_args:
                del self.url_args['code']
            response(url=uri)
        return credentials
    def get_http(self):
        return self.get_credentials().authorize(httplib2.Http())

class RedisCredStorage(oauth2client.client.Storage):
    def __init__(self, app):
        self.r = DARedis()
        self.key = 'da:' + app + ':user:' + user_info().email
        self.lockkey = 'da:' + app + ':lock:user:' + user_info().email
    def acquire_lock(self):
        pipe = self.r.pipeline()
        pipe.set(self.lockkey, 1)
        pipe.expire(self.lockkey, 5)
        pipe.execute()
    def release_lock(self):
        self.r.delete(self.lockkey)
    def locked_get(self):
        json_creds = self.r.get(self.key)
        creds = None
        if json_creds is not None:
            json_creds = json_creds.decode()
            try:
                creds = oauth2client.client.Credentials.new_from_json(json_creds)
            except:
                log("RedisCredStorage: could not read credentials from " + str(json_creds))
        return creds
    def locked_put(self, credentials):
        self.r.set(self.key, credentials.to_json())
    def locked_delete(self):
        self.r.delete(self.key)


