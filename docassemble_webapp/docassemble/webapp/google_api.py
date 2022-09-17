import logging
import json
from google.oauth2 import service_account
import google.cloud.storage
import google.cloud.vision
from docassemble.base.config import daconfig
from oauth2client.service_account import ServiceAccountCredentials

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
credential_json = daconfig.get('google').get('service account credentials', None)

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
    if not isinstance(scope, list):
        scope = [scope]
    return ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)


def google_cloud_credentials():
    """Returns google.oauth2.service_account.Credentials that can be used with the google.cloud API."""
    if credential_info is None:
        raise Exception("google service account credentials not defined in configuration")
    return service_account.Credentials.from_service_account_info(credential_info)


def project_id():
    """Returns the project ID as defined in the google service account credentials in the Configuration."""
    return credential_info['project_id']


def google_cloud_storage_client():
    """Returns a Client object for google.cloud.storage."""
    return google.cloud.storage.Client(credentials=google_cloud_credentials(), project=credential_info['project_id'])


def google_cloud_vision_client():
    """Returns an ImageAnnotatorClient object for google.cloud.vision."""
    return google.cloud.vision.ImageAnnotatorClient(credentials=google_cloud_credentials())
