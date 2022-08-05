from docassemble.base.util import DAGoogleAPI, DAFile
import apiclient

api = DAGoogleAPI()

__all__ = ['get_folder_names', 'get_files_in_folder', 'write_file_to_folder', 'download_file']


def get_folder_names():
    service = api.drive_service()
    items = []
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and sharedWithMe").execute()
        for the_file in response.get('files', []):
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return [item['name'] for item in items]


def get_folder_id(folder_name):
    service = api.drive_service()
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and sharedWithMe and name='" + str(folder_name) + "'").execute()
    folder_id = None
    for item in response.get('files', []):
        folder_id = item['id']
    return folder_id


def get_file_id(filename, folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        raise Exception("The folder was not found")
    service = api.drive_service()
    file_id = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType!='application/vnd.google-apps.folder' and '" + str(folder_id) + "' in parents and name='" + str(filename) + "'").execute()
    for item in response.get('files', []):
        file_id = item['id']
    return file_id


def get_files_in_folder(folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        raise Exception("The folder was not found")
    service = api.drive_service()
    items = []
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType!='application/vnd.google-apps.folder' and trashed=false and '" + str(folder_id) + "' in parents").execute()
        for the_file in response.get('files', []):
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return [item['name'] for item in items]


def write_file_to_folder(path, mimetype, filename, folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        raise Exception("The folder was not found")
    service = api.drive_service()
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = apiclient.http.MediaFileUpload(path, mimetype=mimetype)
    the_new_file = service.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()
    return the_new_file.get('id')


def download_file(filename, folder_name):
    file_id = get_file_id(filename, folder_name)
    if file_id is None:
        raise Exception("The file was not found")
    the_file = DAFile()
    the_file.set_random_instance_name()
    the_file.initialize(filename=filename)
    service = api.drive_service()
    with open(the_file.path(), 'wb') as fh:
        response = service.files().get_media(fileId=file_id)
        downloader = apiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
            status, done = downloader.next_chunk()  # pylint: disable=unused-variable
    the_file.commit()
    return the_file
