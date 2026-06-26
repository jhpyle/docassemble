import oauth2client
from docassemble.webapp.utils.logger import logmessage

class RedisCredStorage(oauth2client.client.Storage):

    def __init__(self, r, user_id, oauth_app='googledrive'):
        self.r = r
        self.key = 'da:' + oauth_app + ':userid:' + str(user_id)
        self.lockkey = 'da:' + oauth_app + ':lock:userid:' + str(user_id)
        super().__init__()

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
                logmessage("RedisCredStorage: could not read credentials from " + str(json_creds))
        return creds

    def locked_put(self, credentials):
        self.r.set(self.key, credentials.to_json())

    def locked_delete(self):
        self.r.delete(self.key)
