import os
import mimetypes
import datetime
from botocore.errorfactory import ClientError
import boto3

epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=datetime.timezone.utc)


class s3object:

    def __init__(self, s3_config):
        self.upload_args = {}
        self.download_args = {}
        if 'server side encryption' in s3_config and isinstance(s3_config['server side encryption'], dict):
            if s3_config['server side encryption'].get('algorithm'):
                self.upload_args['ServerSideEncryption'] = s3_config['server side encryption']['algorithm']
            if s3_config['server side encryption'].get('customer algorithm'):
                self.upload_args['SSECustomerAlgorithm'] = s3_config['server side encryption']['customer algorithm']
                self.download_args['SSECustomerAlgorithm'] = s3_config['server side encryption']['customer algorithm']
            if s3_config['server side encryption'].get('customer key'):
                self.upload_args['SSECustomerKey'] = s3_config['server side encryption']['customer key']
                self.download_args['SSECustomerKey'] = s3_config['server side encryption']['customer key']
            if s3_config['server side encryption'].get('KMS key ID'):
                self.upload_args['SSEKMSKeyId'] = s3_config['server side encryption']['KMS key ID']
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
            self.does_exist = True
        else:
            self.does_exist = False

    def get_contents_as_string(self):
        resp = self.key_obj.get(**self.s3_object.download_args)
        self.size = resp['ContentLength']
        self.content_type = resp['ContentType']
        self.last_modified = resp['LastModified']
        return resp['Body'].read().decode()

    def exists(self):
        try:
            resp = self.s3_object.client.head_object(Bucket=self.s3_object.bucket_name, Key=self.name, **self.s3_object.download_args)
            self.size = resp['ContentLength']
            self.content_type = resp['ContentType']
            self.last_modified = resp['LastModified']
        except ClientError:
            return False
        return True

    def delete(self):
        self.key_obj.delete()
        self.does_exist = False

    def get_epoch_modtime(self):
        return (self.last_modified - epoch).total_seconds()

    def get_contents_to_filename(self, filename):
        self.s3_object.conn.Bucket(self.s3_object.bucket_name).download_file(self.name, filename, ExtraArgs=self.s3_object.download_args)
        secs = (self.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))

    def set_contents_from_filename(self, filename):
        if hasattr(self, 'content_type') and self.content_type is not None:
            mimetype = self.content_type
        else:
            mimetype, encoding = mimetypes.guess_type(filename)  # pylint: disable=unused-variable
        if self.key_obj.__class__.__name__ == 's3.ObjectSummary':
            self.key_obj = self.s3_object.conn.Object(self.s3_object.bucket_name, self.name)
        if mimetype is not None:
            self.key_obj.upload_file(filename, ExtraArgs={'ContentType': mimetype, **self.s3_object.upload_args})
        else:
            self.key_obj.upload_file(filename, ExtraArgs=self.s3_object.upload_args)
        resp = self.s3_object.client.head_object(Bucket=self.s3_object.bucket_name, Key=self.name, **self.s3_object.download_args)
        self.size = resp['ContentLength']
        self.content_type = resp['ContentType']
        self.last_modified = resp['LastModified']
        secs = (self.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))

    def set_contents_from_string(self, text):
        if hasattr(self, 'content_type') and self.content_type is not None:
            self.key_obj.put(Body=bytes(text, encoding='utf-8'), ContentType=self.content_type, **self.s3_object.upload_args)
        else:
            self.key_obj.put(Body=bytes(text, encoding='utf-8'), **self.s3_object.upload_args)
        resp = self.s3_object.client.head_object(Bucket=self.s3_object.bucket_name, Key=self.name, **self.s3_object.download_args)
        self.size = resp['ContentLength']
        self.content_type = resp['ContentType']
        self.last_modified = resp['LastModified']

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
