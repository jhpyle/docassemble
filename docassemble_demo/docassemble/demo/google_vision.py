import io
import json
from docassemble.base.util get_config
from google.cloud import vision
from google.oauth2 import service_account

__all__ = ['gv_ocr']

service_account_creds = get_config('google', {}).get('service account credentials', "")

def gv_ocr(the_file):
    if service_account_creds == '':
        raise Exception("No service account credentials in the google configuration")
    info = json.loads(service_account_creds)
    storage_credentials = service_account.Credentials.from_service_account_info(info)
    client = vision.ImageAnnotatorClient(credentials=storage_credentials)
    image = vision.Image()
    with io.open(the_file.path(), 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    output = ''
    for text in response.text_annotations:
        output += text.description + "\n"
    if response.error.message:
        raise Exception(response.error.message)
    return output
