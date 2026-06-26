# do not pre-load
import apiclient
from docassemble.base.util import DAGoogleAPI

__all__ = ['fetch_file']


def fetch_file(file_id, path):
    service = DAGoogleAPI().drive_service()
    with open(path, 'wb') as fh:
        response = service.files().get_media(fileId=file_id)  # pylint: disable=no-member
        downloader = apiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
            status, done = downloader.next_chunk()  # pylint: disable=unused-variable
