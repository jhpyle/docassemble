from .helpers import (
    do_serve_uploaded_page,
    do_serve_uploaded_file_with_filename_and_extension,
    do_serve_temporary_file,
    do_serve_uploaded_file_with_extension,
    do_serve_stored_file,
    do_serve_uploaded_file,
)
from .blueprint import files_bp

@files_bp.route('/storedfile/<uid>/<number>/<filename>.<extension>', methods=['GET'])
def serve_stored_file(uid, number, filename, extension):
    return do_serve_stored_file(uid, number, filename, extension)


@files_bp.route('/storedfiledownload/<uid>/<number>/<filename>.<extension>', methods=['GET'])
def serve_stored_file_download(uid, number, filename, extension):
    return do_serve_stored_file(uid, number, filename, extension, download=True)


@files_bp.route('/tempfile/<code>/<filename>.<extension>', methods=['GET'])
def serve_temporary_file(code, filename, extension):
    return do_serve_temporary_file(code, filename, extension)


@files_bp.route('/tempfiledownload/<code>/<filename>.<extension>', methods=['GET'])
def serve_temporary_file_download(code, filename, extension):
    return do_serve_temporary_file(code, filename, extension, download=True)


@files_bp.route('/uploadedfile/<number>/<filename>.<extension>', methods=['GET'])
def serve_uploaded_file_with_filename_and_extension(number, filename, extension):
    return do_serve_uploaded_file_with_filename_and_extension(number, filename, extension)


@files_bp.route('/uploadedfiledownload/<number>/<filename>.<extension>', methods=['GET'])
def serve_uploaded_file_with_filename_and_extension_download(number, filename, extension):
    return do_serve_uploaded_file_with_filename_and_extension(number, filename, extension, download=True)


@files_bp.route('/uploadedfile/<number>.<extension>', methods=['GET'])
def serve_uploaded_file_with_extension(number, extension):
    return do_serve_uploaded_file_with_extension(number, extension)


@files_bp.route('/uploadedfiledownload/<number>.<extension>', methods=['GET'])
def serve_uploaded_file_with_extension_download(number, extension):
    return do_serve_uploaded_file_with_extension(number, extension, download=True)


@files_bp.route('/uploadedfile/<number>', methods=['GET'])
def serve_uploaded_file(number):
    return do_serve_uploaded_file(number)


@files_bp.route('/uploadedpage/<number>/<page>', methods=['GET'])
def serve_uploaded_page(number, page):
    return do_serve_uploaded_page(number, page, size='page')


@files_bp.route('/uploadedpagedownload/<number>/<page>', methods=['GET'])
def serve_uploaded_page_download(number, page):
    return do_serve_uploaded_page(number, page, download=True, size='page')


@files_bp.route('/uploadedpagescreen/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen(number, page):
    return do_serve_uploaded_page(number, page, size='screen')


@files_bp.route('/uploadedpagescreendownload/<number>/<page>', methods=['GET'])
def serve_uploaded_pagescreen_download(number, page):
    return do_serve_uploaded_page(number, page, download=True, size='screen')
