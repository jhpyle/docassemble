import datetime
import io
import mimetypes
import os
import re
import logging
import yaml
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, ContentSettings, generate_blob_sas
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

logger = logging.getLogger('azure.mgmt.resource')
logger.setLevel(logging.WARNING)

epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=datetime.timezone.utc)


class azureobject:

    def __init__(self, azure_config):
        if ('key vault name' in azure_config and azure_config['key vault name'] is not None and 'managed identity' in azure_config and azure_config['managed identity'] is not None):
            self.credential = ManagedIdentityCredential()
            self.key_vault_name = azure_config.get('key vault name', None)
            self.key_vault_base_url = 'https://%s.vault.azure.net/' % (self.key_vault_name)
            self.secret_client = SecretClient(vault_url=self.key_vault_base_url, credential=self.credential)
            self.key_vault_reference_regex = r'(\@Microsoft\.KeyVault\(SecretUri=https:\/\/([\w-]+)\.vault\.azure\.net\/secrets\/([\w-]+)\/(\w+)?\))'
            azure_config = self.load_with_secrets(azure_config)
        if ('account name' in azure_config and azure_config['account name'] is not None and 'account key' in azure_config and azure_config['account key'] is not None and 'container' in azure_config and azure_config['container'] is not None) or ('connection string' in azure_config and azure_config['connection string'] is not None and 'container' in azure_config and azure_config['container'] is not None):
            connection_string = azure_config.get('connection string', None)
            if not connection_string:
                endpoint_suffix = azure_config.get('endpoint suffix', None)
                if not endpoint_suffix:
                    endpoint_suffix = 'core.windows.net'
                endpoints_protocol = azure_config.get('endpoints protocol', None)
                if not endpoints_protocol:
                    endpoints_protocol = 'https'
                connection_string = 'DefaultEndpointsProtocol=%s;AccountName=%s;AccountKey=%s;EndpointSuffix=%s' % (endpoints_protocol, azure_config['account name'], azure_config['account key'], endpoint_suffix)
            self.service_client = BlobServiceClient.from_connection_string(connection_string)
            self.container = azure_config['container']
            self.container_client = self.service_client.get_container_client(azure_config['container'])
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
        for blob in self.container_client.list_blobs(name_starts_with=key_name):
            if blob.name == key_name:
                return azurekey(self, blob.name)
        return None

    def list_keys(self, prefix):
        output = []
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            output.append(azurekey(self, blob.name))
        return output

    def get_secret(self, key_vault_reference):
        new_secret = azuresecret(self, key_vault_reference)
        return new_secret.get_secret_as_string()

    def replace_secrets(self, match):
        match = match.groups()
        return self.get_secret(match[0])

    def load_with_secrets(self, config):
        config_dump_raw = yaml.dump(config)
        config_dump_replace_secrets = re.sub(self.key_vault_reference_regex, self.replace_secrets, config_dump_raw)
        loaded_config_with_secrets = yaml.load(config_dump_replace_secrets, Loader=yaml.FullLoader)
        return loaded_config_with_secrets


class azurekey:

    def __init__(self, azure_object, key_name, load=True):
        self.azure_object = azure_object
        self.blob_client = azure_object.container_client.get_blob_client(key_name)
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
        return self.blob_client.download_blob().readall().decode()

    def exists(self):
        return self.blob_client.exists()

    def delete(self):
        self.blob_client.delete_blob()

    def get_contents_to_filename(self, filename):
        with open(filename, "wb") as fp:
            download_stream = self.blob_client.download_blob()
            fp.write(download_stream.readall())
        secs = (self.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))

    def set_contents_from_filename(self, filename):
        if hasattr(self, 'content_type') and self.content_type is not None:
            mimetype = self.content_type
        else:
            mimetype, encoding = mimetypes.guess_type(filename)  # pylint: disable=unused-variable
        content_length = os.path.getsize(filename)
        if mimetype is not None:
            with open(filename, "rb") as data:
                self.blob_client.upload_blob(data=data, content_settings=ContentSettings(content_type=mimetype), length=content_length, overwrite=True)
        else:
            with open(filename, "rb") as data:
                self.blob_client.upload_blob(data=data, length=content_length, overwrite=True)
        self.get_properties()
        secs = (self.last_modified - epoch).total_seconds()
        os.utime(filename, (secs, secs))

    def set_contents_from_string(self, text):
        text = text.encode()
        with io.BytesIO(text) as data:
            self.blob_client.upload_blob(data=data, length=len(text), overwrite=True)

    def get_epoch_modtime(self):
        if not hasattr(self, 'last_modified'):
            self.get_properties()
        return (self.last_modified - epoch).total_seconds()

    def generate_url(self, seconds, display_filename=None, content_type=None, inline=False):
        if content_type is None:
            content_type = self.content_type
        if display_filename is not None:
            disposition = "attachment; filename=" + display_filename
        elif inline:
            disposition = "inline"
        else:
            disposition = None
        token = generate_blob_sas(
            self.blob_client.account_name,
            self.blob_client.container_name,
            self.blob_client.blob_name,
            snapshot=self.blob_client.snapshot,
            account_key=self.blob_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds),
            cache_control='no-cache',
            content_disposition=disposition,
            content_type=content_type
        )
        return self.blob_client.url + '?' + token


class azuresecret:

    def __init__(self, azure_object, key_vault_reference):
        self.azure_object = azure_object
        self.secret_client = azure_object.secret_client
        self.key_vault_reference = key_vault_reference
        self.key_vault_reference_regex = azure_object.key_vault_reference_regex
        self.secret = None
        self.secret_value = None
        self.reference_secret_name = None
        self.reference_secret_version = None

    def set_secret_reference_components(self):
        secret_regex = re.compile(self.key_vault_reference_regex)
        secret_match = secret_regex.search(self.key_vault_reference)
        if secret_match is not None:
            self.reference_vault_name = secret_match.groups()[1]
            self.reference_secret_name = secret_match.groups()[2]
            if len(secret_match.groups()) > 3:
                self.reference_secret_version = secret_match.groups()[3]
        else:
            raise Exception("Invalid format for Azure Key Vault reference value in configuration!")

    def get_secret_from_vault(self):
        self.secret = self.secret_client.get_secret(self.reference_secret_name, self.reference_secret_version)
        self.secret_value = self.secret.value

    def get_secret_as_string(self):
        if self.secret is None:
            self.set_secret_reference_components()
            self.get_secret_from_vault()
        return self.secret_value
