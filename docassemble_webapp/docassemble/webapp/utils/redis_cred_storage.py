from flask_login import current_user
import oauth2client
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.daredis import r

class RedisCredStorage(oauth2client.client.Storage):

    def __init__(self, oauth_app='googledrive'):
        self.key = 'da:' + oauth_app + ':userid:' + str(current_user.id)
        self.lockkey = 'da:' + oauth_app + ':lock:userid:' + str(current_user.id)
        super().__init__()

    def acquire_lock(self):
        pipe = r.pipeline()
        pipe.set(self.lockkey, 1)
        pipe.expire(self.lockkey, 5)
        pipe.execute()

    def release_lock(self):
        r.delete(self.lockkey)

    def locked_get(self):
        json_creds = r.get(self.key)
        creds = None
        if json_creds is not None:
            json_creds = json_creds.decode()
            try:
                creds = oauth2client.client.Credentials.new_from_json(json_creds)
            except:
                logmessage("RedisCredStorage: could not read credentials from " + str(json_creds))
        return creds

    def locked_put(self, credentials):
        r.set(self.key, credentials.to_json())

    def locked_delete(self):
        r.delete(self.key)
