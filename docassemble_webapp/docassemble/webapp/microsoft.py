import datetime
import os
import time
import pytz
import mimetypes
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from azure.identity import ClientSecretCredential

epoch = pytz.utc.localize(datetime.datetime.utcfromtimestamp(0))

class azureobject(object):
    def __init__(self, azure_config):
        if ('account name' in azure_config and azure_config['account name'] is not None and 'account key' in azure_config and azure_config['account key'] is not None and 'container' in azure_config and azure_config['container'] is not None) or ('connection string' in azure_config and azure_config['connection string'] is not None and 'container' in azure_config and azure_config['container'] is not None):
            connection_string = azure_config.get('connection string', None)
            if not connection_string:
                endpoint_suffix = azure_config.get('endpoint suffix', None)
                if not endpoint_suffix:
                    endpoint_suffix = core.windows.net
                endpoints_protocol = azure_config.get('endpoints protocol', None)
                if not endpoints_protocol:
                    endpoints_protocol = 'https'
                connection_string = 'DefaultEndpointsProtocol=%s;AccountName=%s;AccountKey=%s;EndpointSuffix=%s' % (endpoints_protocol, azure_config['account name'], azure_config['account key'], endpoint_suffix)
            service_client = BlobServiceClient.from_connection_string(connection_string)
            #self.container = azure_config['container']
            self.conn = service_client.get_container_client(azure_config['container'])
            #self.conn = (account_name=azure_config['account name'], account_key=azure_config['account key'])
        else:
            raise Exception("Cannot connect to Azure without account name, account key, and container specified")
    def get_key(self, key_name):
        new_key = azurekey(self, key_name, load=False)
        if new_key.exists():
            new_key.get_properties()
            new_key.does_exist = True
        else:
            new_key.does_exist = False
        return new_key
    def search_key(self, key_name):
        for blob in self.conn.list_blobs(name_starts_with=key_name):
            if blob.name == key_name:
                return azurekey(self, blob.name)
        return None
    def list_keys(self, prefix):
        output = list()
        for blob in self.conn.list_blobs(name_starts_with=prefix):
            output.append(azurekey(self, blob.name))
        return output

"""
{'name': 'postgres/docassemble', 'container': 'azuretest2-docassemble-org', 'snapshot': None, 'version_id': None, 'is_current_version': None, 'blob_type': <BlobType.BlockBlob: 'BlockBlob'>, 'metadata': {}, 'encrypted_metadata': None, 'last_modified': datetime.datetime(2019, 10, 31, 0, 27, 3, tzinfo=datetime.timezone.utc), 'etag': '"0x8D75D990D888CC8"', 'size': 1768957, 'content_range': None, 'append_blob_committed_block_count': None, 'is_append_blob_sealed': None, 'page_blob_sequence_number': None, 'server_encrypted': True, 'copy': {'id': None, 'source': None, 'status': None, 'progress': None, 'completion_time': None, 'status_description': None, 'incremental_copy': None, 'destination_snapshot': None}, 'content_settings': {'content_type': 'application/octet-stream', 'content_encoding': None, 'content_language': None, 'content_md5': bytearray(b'zy\x9e\xa65d\x88\x07A\x976Y\r\xe6\xa0\x94'), 'content_disposition': None, 'cache_control': None}, 'lease': {'status': 'unlocked', 'state': 'available', 'duration': None}, 'blob_tier': 'Cool', 'rehydrate_priority': None, 'blob_tier_change_time': None, 'blob_tier_inferred': True, 'deleted': False, 'deleted_time': None, 'remaining_retention_days': None, 'creation_time': datetime.datetime(2019, 8, 28, 10, 31, 10, tzinfo=datetime.timezone.utc), 'archive_status': None, 'encryption_key_sha256': None, 'encryption_scope': None, 'request_server_encrypted': True, 'object_replication_source_properties': [], 'object_replication_destination_policy': None, 'last_accessed_on': None, 'tag_count': None, 'tags': None}
"""
    
class azurekey(object):
    def __init__(self, azure_object, key_name, load=True):
        self.azure_object = azure_object
        self.blob_client = azure_object.conn.get_blob_client(key_name)
        self.name = key_name
        if load:
            if not key_name.endswith('/'):
                self.get_properties()
                self.does_exist = True
    def get_properties(self):
        properties = self.blob_client.get_blob_properties()
        self.size = properties.size
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
        #secs = time.mktime(self.last_modified.timetuple())
        secs = (self.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))
    def set_contents_from_filename(self, filename):
        if hasattr(self, 'content_type') and self.content_type is not None:
            mimetype = self.content_type
        else:
            mimetype, encoding = mimetypes.guess_type(filename)
        if mimetype is not None:
            self.azure_object.conn.create_blob_from_path(self.azure_object.container, self.name, filename, content_settings=ContentSettings(content_type=mimetype))
        else:
            self.azure_object.conn.create_blob_from_path(self.azure_object.container, self.name, filename)
        self.get_properties()
        secs = (self.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))
    def set_contents_from_string(self, text):
        self.azure_object.conn.create_blob_from_text(self.azure_object.container, self.name, text)
    def get_epoch_modtime(self):
        if not hasattr(self, 'last_modified'):
            self.get_properties()
        return (self.last_modified - epoch).total_seconds()
    def generate_url(self, seconds, display_filename=None, content_type=None, inline=False):
        if content_type is None:
            content_type = self.content_type
        params = dict(permission=BlobPermissions.READ, expiry=datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds), content_type=content_type)
        if display_filename is not None:
            params['content_disposition'] = "attachment; filename=" + display_filename
        elif inline:
            params['content_disposition'] = "inline"
        sas_token = self.azure_object.conn.generate_blob_shared_access_signature(self.azure_object.container, self.name, **params)
        return self.azure_object.conn.make_blob_url(self.azure_object.container, self.name, sas_token=sas_token)
