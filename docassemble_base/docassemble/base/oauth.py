from docassemble.base.util import DARedis, user_info, DAObject, get_config, interview_url, response, message, log
from docassemble.base.generate_key import random_alphanumeric
import oauth2client.client
import json
import string
import random
import httplib2
import re
import codecs

__all__ = ['DAOAuth']

def safeid(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())

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
        super().init(*pargs, **kwargs)
    def _get_flow(self):
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
    def _setup(self):
        if hasattr(self, 'use_random_unique_id') and self.use_random_unique_id and not hasattr(self, 'unique_id'):
            self.unique_id = self._get_random_unique_id()
        if not hasattr(self, 'expires'):
            if hasattr(self, 'unique_id'):
                self.expires = 86400
            else:
                self.expires = 15724800
        try:
            if not isinstance(self.expires, int):
                self.expires = int(self.expires)
            assert self.expires > 0
        except:
            self.expires = None
    def _get_redis_key(self):
        if hasattr(self, 'unique_id'):
            return 'da:' + self.appname + ':status:uniqueid:' + str(self.unique_id)
        return 'da:' + self.appname + ':status:user:' + user_info().email
    def _get_redis_cred_storage(self):
        if hasattr(self, 'unique_id'):
            key = 'da:' + self.appname + ':uniqueid:' + str(self.unique_id)
            lock = 'da:' + self.appname + ':lock:uniqueid:' + str(self.unique_id)
        else:
            key = 'da:' + self.appname + ':user:' + user_info().email
            lock = 'da:' + self.appname + ':lock:user:' + user_info().email
        return RedisCredStorage(key, lock, self.expires)
    def _get_random_unique_id(self):
        r = DARedis()
        tries = 10
        while tries > 0:
            key = random_alphanumeric(32)
            if r.setnx('da:' + self.appname + ':status:uniqueid:' + key, 'None'):
                r.expire('da:' + self.appname + ':status:uniqueid:' + key, 300)
                return key
            tries -= 1
        raise Exception("DAOAuth: unable to set a random unique id")
    def get_credentials(self):
        self._setup()
        r = DARedis()
        r_key = self._get_redis_key()
        stored_state = r.get(r_key)
        if stored_state is not None and stored_state.decode() == 'None':
            stored_state = None
        if stored_state is not None:
            if 'code' in self.url_args and 'state' in self.url_args:
                r.delete(r_key)
                if self.url_args['state'] != stored_state.decode():
                    raise Exception("State did not match.  " + repr(self.url_args['state']) + " vs " + repr(stored_state.decode()) + " where r_key is " + repr(r_key))
                flow = self._get_flow()
                credentials = flow.step2_exchange(self.url_args['code'])
                storage = self._get_redis_cred_storage()
                storage.put(credentials)
                del self.url_args['code']
                del self.url_args['state']
            else:
                message("Please wait.", "You are in the process of authenticating.")
        storage = self._get_redis_cred_storage()
        credentials = storage.get()
        if not credentials or credentials.invalid:
            state_string = safeid(user_info().filename + '^' + random_string(8))
            pipe = r.pipeline()
            pipe.set(r_key, state_string)
            pipe.expire(r_key, 300)
            pipe.execute()
            flow = self._get_flow()
            uri = flow.step1_get_authorize_url(state=state_string)
            if 'state' in self.url_args:
                del self.url_args['state']
            if 'code' in self.url_args:
                del self.url_args['code']
            response(url=uri)
        return credentials
    def delete_credentials(self):
        """Deletes the stored credentials."""
        self._setup()
        r = DARedis()
        r.delete(self._get_redis_key())
        storage = self._get_redis_cred_storage()
        storage.locked_delete()
    def get_http(self):
        """Returns an http object that can be used to communicate with the OAuth-enabled API."""
        return self.get_credentials().authorize(httplib2.Http())
    def ensure_authorized(self):
        """If the credentials are not valid, starts the authorization process."""
        self.get_http()
    def active(self):
        """Returns True if user has stored credentials, whether they are valid or not.  Otherwise returns False."""
        self._setup()
        storage = self._get_redis_cred_storage()
        credentials = storage.get()
        if not credentials:
            return False
        return True
    def is_authorized(self):
        """Returns True if user has stored credentials and the credentials are valid."""
        self._setup()
        storage = self._get_redis_cred_storage()
        credentials = storage.get()
        if not credentials or credentials.invalid:
            return False
        return True

class RedisCredStorage(oauth2client.client.Storage):
    def __init__(self, key, lock, expires):
        self.r = DARedis()
        self.key = key
        self.lockkey = lock
        self.expires = expires
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
            self.r.expire(self.key, self.expires)
            json_creds = json_creds.decode()
            try:
                creds = oauth2client.client.Credentials.new_from_json(json_creds)
            except:
                log("RedisCredStorage: could not read credentials from " + str(json_creds))
        return creds
    def locked_put(self, credentials):
        if self.expires:
            pipe = self.r.pipeline()
            pipe.set(self.key, credentials.to_json())
            pipe.expire(self.key, self.expires)
            pipe.execute()
        else:
            self.r.set(self.key, credentials.to_json())
    def locked_delete(self):
        self.r.delete(self.key)
