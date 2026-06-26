# do not pre-load
from googleapiclient.discovery import build
from docassemble.base.util import DAOAuth

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
        sheet = service.spreadsheets()
        sample_spreadsheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
        sample_range_name = 'Class Data!A2:E'
        result = sheet.values().get(spreadsheetId=sample_spreadsheet_id,
                                    range=sample_range_name).execute()
        values = result.get('values', [])
        return values
