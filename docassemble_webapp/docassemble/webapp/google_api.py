import json
import apiclient
from google.oauth2 import service_account
import google.cloud.storage
from docassemble.base.util import get_config
from oauth2client.service_account import ServiceAccountCredentials
import sys
credential_json = get_config('google', dict()).get('service account credentials', None)

if credential_json is None:
    credential_info = None
else:
    credential_info = json.loads(credential_json, strict=False)

def google_api_credentials(scope):
    """Returns an OAuth2 credentials object for the given scope."""
    if credential_info is None:
        raise Exception("google service account credentials not defined in configuration")
    if scope is None:
        scope = ['https://www.googleapis.com/auth/drive']
    if type(scope) is not list:
        scope = [scope]
    return ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)

def google_cloud_credentials(scope):
    """Returns google.oauth2.service_account.Credentials that can be used with the google.cloud API."""
    if credential_info is None:
        raise Exception("google service account credentials not defined in configuration")
    if scope is None:
        scope = ['https://www.googleapis.com/auth/devstorage.full_control']
    return service_account.Credentials.from_service_account_info(credential_info)

def project_id():
    """Returns the project ID as defined in the google service account credentials in the Configuration."""
    return credential_info['project_id']

def google_cloud_storage_client(scope=None):
    """Returns a Client object for google.cloud.storage."""
    if scope is None:
        scope = ['https://www.googleapis.com/auth/devstorage.full_control']
    return google.cloud.storage.Client(credentials=google_cloud_credentials(scope), project=credential_info['project_id'])
