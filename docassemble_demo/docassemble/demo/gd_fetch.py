from docassemble.base.util import DAGoogleAPI
import apiclient

__all__ = ['fetch_file']

def fetch_file(file_id, path):
    service = DAGoogleAPI().drive_service()
    with open(path, 'wb') as fh:
        response = service.files().get_media(fileId=file_id)
        downloader = apiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
