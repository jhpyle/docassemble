import json
import gspread
from docassemble.base.util import get_config
from oauth2client.service_account import ServiceAccountCredentials
credential_json = get_config('google', {}).get('service account credentials', None)
if credential_json is None:
    credential_info = None
else:
    credential_info = json.loads(credential_json, strict=False)

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

__all__ = ['read_sheet', 'append_to_sheet']

def read_sheet(sheet_name, worksheet_index=0):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).get_worksheet(worksheet_index)
    return sheet.get_all_records()

def append_to_sheet(sheet_name, vals, worksheet_index=0):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).get_worksheet(worksheet_index)
    sheet.append_row(vals)
