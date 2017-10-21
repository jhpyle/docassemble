import boto3
import time
import os
from botocore.errorfactory import ClientError

class s3object(object):
    def __init__(self, s3_config):
        if 'access key id' in s3_config and s3_config['access key id'] is not None:
            self.conn = boto3.resource('s3', region_name=s3_config.get('region', None), aws_access_key_id=s3_config['access key id'], aws_secret_access_key=s3_config['secret access key'])
            self.client = boto3.client('s3', region_name=s3_config.get('region', None), aws_access_key_id=s3_config['access key id'], aws_secret_access_key=s3_config['secret access key'])
        else:
            self.conn = boto3.resource('s3', region_name=s3_config.get('region', None))
            self.client = boto3.client('s3', region_name=s3_config.get('region', None))
        self.bucket = self.conn.Bucket(s3_config['bucket'])
        self.bucket_name = s3_config['bucket']
    def get_key(self, key_name):
        return s3key(self, self.conn.Object(self.bucket_name, key_name))
    def search_key(self, key_name):
        for key in self.bucket.objects.filter(Prefix=key_name, Delimiter='/'):
            return s3key(self, self.conn.Object(self.bucket_name, key.key))
    def list_keys(self, prefix):
        output = list()
        for obj in self.bucket.objects.filter(Prefix=prefix, Delimiter='/'):
            output.append(s3key(self, self.conn.Object(self.bucket_name, obj.key), load=True))
        return output

class s3key(object):
    def __init__(self, s3_object, key_obj, load=True):
        self.s3_object = s3_object
        self.key_obj = key_obj
        self.name = key_obj.key
        if load and self.exists():
            self.size = self.key_obj.content_length
            self.last_modified = self.key_obj.last_modified
            self.content_type = self.key_obj.content_type
    def get_contents_as_string(self):
        return self.key_obj.get()['Body'].read()
    def exists(self):
        try:
            self.s3_object.client.head_object(Bucket=self.s3_object.bucket_name, Key=self.key_obj.key)
        except ClientError as e:
            return False
        return True
    def delete(self):
        self.key_obj.delete()
    def get_contents_to_filename(self, filename):
        #try:
        self.s3_object.conn.Bucket(self.s3_object.bucket_name).download_file(self.key_obj.key, filename)
        #except ClientError as e:
        #    raise    
        secs = time.mktime(self.key_obj.last_modified.timetuple())
        os.utime(filename, (secs, secs))
    def set_contents_from_filename(self, filename):
        self.key_obj.upload_file(filename)
        self.update_metadata()
    def set_contents_from_string(self, text):
        self.key_obj.put(Body=bytes(text))
        self.update_metadata()
    def update_metadata():
        if self.content_type is not None and self.content_type != self.key_obj.content_type:
            self.key_obj.put(Metadata={'Content-Type': self.content_type})
    def generate_url(self, expires, content_type=None, display_filename=None):
        params = dict(Bucket=self.s3_object.bucket_name, Key=self.key_obj.key)
        if content_type is not None:
            params['ResponseContentType'] = content_type
        if display_filename is not None:
            params['ResponseContentDisposition'] = "attachment; filename=" + display_filename
        return self.s3_object.client.generate_presigned_url(
            ClientMethod='get_object',
            Params=params,
            ExpiresIn=expires)
