from docassemble.base.util import DAOAuth
from googleapiclient.discovery import build

__all__ = ['GoogleAuth']


class GoogleAuth(DAOAuth):

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.appname = 'mygoogle'
        self.token_uri = "https://www.googleapis.com/oauth2/v4/token"
        self.auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.scope = "https://www.googleapis.com/auth/spreadsheets"

    def test(self):
        service = build('sheets', 'v4', http=self.get_http())
        SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
        SAMPLE_RANGE_NAME = 'Class Data!A2:E'
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        return values
