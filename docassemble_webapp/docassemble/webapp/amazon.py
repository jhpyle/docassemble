import boto
import boto.s3.connection
import boto.s3.key
#from docassemble.base.logger import logmessage

class s3object(object):
    def __init__(self, s3_config):
        #logmessage("Trying to connect with " + s3_config['access_key_id'] + " and " + s3_config['secret_access_key'] + " and " + s3_config['bucket'])
        if 'access key id' in s3_config and s3_config['access key id'] is not None:
            self.conn = boto.s3.connection.S3Connection(s3_config['access key id'], s3_config['secret access key'])
        else:
            self.conn = boto.connect_s3()
        self.bucket = self.conn.get_bucket(s3_config['bucket'])
    def get_key(self, key_name):
        key = boto.s3.key.Key(bucket=self.bucket, name=key_name)
        return key
    def search_key(self, key_name):
        for key in self.bucket.list(prefix=key_name, delimiter='/'):
            return key
    def list_keys(self, prefix):
        return self.bucket.list(prefix=prefix, delimiter='/')
