import boto.s3.connection
import boto.s3.key
#from docassemble.base.logger import logmessage

class s3object(object):
    def __init__(self, s3_config):
        #logmessage("Trying to connect with " + s3_config['access_key_id'] + " and " + s3_config['secret_access_key'] + " and " + s3_config['bucket'])
        self.conn = boto.s3.connection.S3Connection(s3_config['access_key_id'], s3_config['secret_access_key'])
        self.bucket = self.conn.get_bucket(s3_config['bucket'])
    def get_key(self, key_name):
        key = boto.s3.key.Key(bucket=self.bucket, name=key_name)
        return key
    def search_key(self, key_name):
        for key in self.bucket.list(prefix=key_name, delimiter='/'):
            return key
    def new_key(self):
        return boto.s3.key.Key(bucket=self.bucket)
