import datetime
import os
import time
from azure.storage.blob import BlockBlobService
from azure.storage.blob import BlobPermissions

class azureobject(object):
    def __init__(self, azure_config):
        if 'account name' in azure_config and azure_config['account name'] is not None and 'account key' in azure_config and azure_config['account key'] is not None and 'container' in azure_config and azure_config['container'] is not None:
            self.conn = BlockBlobService(account_name=azure_config['account name'], account_key=azure_config['account key'])
            self.container = azure_config['container']
        else:
            raise Exception("Cannot connect to Azure without account name, account key, and container specified")
    def get_key(self, key_name):
        return azurekey(self, key_name)
    def search_key(self, key_name):
        for blob in self.conn.list_blobs(self.container, prefix=key_name, delimiter='/'):
            return azurekey(self, blob.name)
    def list_keys(self, prefix):
        output = list()
        for blob in self.conn.list_blobs(self.container, prefix=prefix, delimiter='/'):
            output.append(azurekey(self, blob.name, load=True))
        return output
    
class azurekey(object):
    def __init__(self, azure_object, key_name, load=True):
        self.azure_object = azure_object
        self.name = key_name
        if load and self.exists():
            properties = self.azure_object.conn.get_blob_properties(self.azure_object.container, self.name).properties
            self.size = properties.content_length
            self.last_modified = properties.last_modified
            self.content_type = properties.content_settings.content_type
    def get_contents_as_string(self):
        return self.azure_object.conn.get_blob_to_text(self.azure_object.container, self.name).content
    def exists(self):
        return self.azure_object.conn.exists(self.azure_object.container, self.name)
    def delete(self):
        self.azure_object.conn.delete_blob(self.azure_object.container, self.name)
    def get_contents_to_filename(self, filename):
        self.azure_object.conn.get_blob_to_path(self.azure_object.container, self.name, filename)
        secs = time.mktime(self.last_modified.timetuple())
        os.utime(filename, (secs, secs))
    def set_contents_from_filename(self, filename):
        self.azure_object.conn.create_blob_from_path(self.azure_object.container, self.name, filename)
    def set_contents_from_string(self, text):
        self.azure_object.conn.create_blob_from_text(self.azure_object.container, self.name, text)
    def generate_url(self, seconds, display_filename=None, content_type=None):
        if content_type is None:
            content_type = self.content_type
        params = dict(permission=BlobPermissions.READ, expiry=datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds), content_type=content_type)
        if display_filename is not None:
            params['content_disposition'] = "attachment; filename=" + display_filename
        sas_token = self.azure_object.conn.generate_blob_shared_access_signature(self.azure_object.container, self.name, **params)
        return self.azure_object.conn.make_blob_url(self.azure_object.container, self.name, sas_token=sas_token)
