import boto.s3.connection
import boto.s3.key

#conn = boto.s3.connection.S3Connection('AKIAJ4DPAVNHB7QLPZGA', 'VAgG1Gv4a1fITEYSy0RL+qTgwxPZ2fPKb26SHcKM')
#bucket = conn.get_bucket('docassemble')
#bucket.list(prefix='files/14/')
class s3object(object):
    def __init__(self, s3_config):
        self.conn = boto.s3.connection.S3Connection(s3_config['access_key_id'], s3_config['secret_access_key'])
        self.bucket = self.conn.get_bucket(s3_config['bucket'])
    def get_key(self, key_name):
        key = boto.s3.key.Key(bucket=self.bucket, name=key_name)
        return key
    def new_key(self):
        return boto.s3.key.Key(bucket=self.bucket)
