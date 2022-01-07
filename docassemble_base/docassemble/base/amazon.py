import os
import mimetypes
import datetime
import pytz
from botocore.errorfactory import ClientError
import boto3

epoch = pytz.utc.localize(datetime.datetime.utcfromtimestamp(0))

class s3object:
    def __init__(self, s3_config):
        if 'access key id' in s3_config and s3_config['access key id'] is not None:
            self.conn = boto3.resource('s3', region_name=s3_config.get('region', None),
                                       aws_access_key_id=s3_config['access key id'],
                                       aws_secret_access_key=s3_config['secret access key'],
                                       endpoint_url=s3_config.get('endpoint url', None))
            self.client = boto3.client('s3', region_name=s3_config.get('region', None),
                                       aws_access_key_id=s3_config['access key id'],
                                       aws_secret_access_key=s3_config['secret access key'],
                                       endpoint_url=s3_config.get('endpoint url', None))
        else:
            self.conn = boto3.resource('s3', region_name=s3_config.get('region', None),
                                       endpoint_url=s3_config.get('endpoint url', None))
            self.client = boto3.client('s3', region_name=s3_config.get('region', None),
                                       endpoint_url=s3_config.get('endpoint url', None))
        self.bucket = self.conn.Bucket(s3_config['bucket'])
        self.bucket_name = s3_config['bucket']
    def get_key(self, key_name):
        return s3key(self, self.conn.Object(self.bucket_name, key_name))
    def search_key(self, key_name):
        for key in self.bucket.objects.filter(Prefix=key_name, Delimiter='/'):
            if key.key == key_name:
                return s3key(self, self.conn.Object(self.bucket_name, key.key))
        return None
    def list_keys(self, prefix):
        output = []
        for obj in self.bucket.objects.filter(Prefix=prefix):
            new_key = s3key(self, obj)
            new_key.size = obj.size
            new_key.last_modified = obj.last_modified
            output.append(new_key)
        return output

class s3key:
    def __init__(self, s3_object, key_obj):
        self.s3_object = s3_object
        self.key_obj = key_obj
        self.name = key_obj.key
        if self.key_obj.__class__.__name__ == 's3.ObjectSummary':
            self.size = self.key_obj.size
            self.last_modified = self.key_obj.last_modified
            self.does_exist = True
        elif self.exists():
            self.size = self.key_obj.content_length
            self.content_type = self.key_obj.content_type
            self.last_modified = self.key_obj.last_modified
            self.does_exist = True
        else:
            self.does_exist = False
    def get_contents_as_string(self):
        return self.key_obj.get()['Body'].read().decode()
    def exists(self):
        try:
            self.s3_object.client.head_object(Bucket=self.s3_object.bucket_name, Key=self.name)
        except ClientError:
            return False
        return True
    def delete(self):
        self.key_obj.delete()
    def get_epoch_modtime(self):
        return (self.key_obj.last_modified - epoch).total_seconds()
    def get_contents_to_filename(self, filename):
        self.s3_object.conn.Bucket(self.s3_object.bucket_name).download_file(self.name, filename)
        secs = (self.key_obj.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))
    def set_contents_from_filename(self, filename):
        if hasattr(self, 'content_type') and self.content_type is not None:
            mimetype = self.content_type
        else:
            mimetype, encoding = mimetypes.guess_type(filename)
        if self.key_obj.__class__.__name__ == 's3.ObjectSummary':
            self.key_obj = self.s3_object.conn.Object(self.s3_object.bucket_name, self.name)
        if mimetype is not None:
            self.key_obj.upload_file(filename, ExtraArgs={'ContentType': mimetype})
        else:
            self.key_obj.upload_file(filename)
        secs = (self.key_obj.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))
    def set_contents_from_string(self, text):
        if hasattr(self, 'content_type') and self.content_type is not None:
            self.key_obj.put(Body=bytes(text, encoding='utf-8'), ContentType=self.content_type)
        else:
            self.key_obj.put(Body=bytes(text, encoding='utf-8'))
    def generate_url(self, expires, content_type=None, display_filename=None, inline=False):
        params = dict(Bucket=self.s3_object.bucket_name, Key=self.key_obj.key)
        if content_type is not None:
            params['ResponseContentType'] = content_type
        if display_filename is not None:
            params['ResponseContentDisposition'] = "attachment; filename=" + display_filename
        if inline:
            params['ResponseContentDisposition'] = "inline"
        return self.s3_object.client.generate_presigned_url(
            ClientMethod='get_object',
            Params=params,
            ExpiresIn=expires)
