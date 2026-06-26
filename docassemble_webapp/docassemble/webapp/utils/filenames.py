import re
import os
import mimetypes
import unicodedata
import werkzeug
from docassemble.base.error import DAException
from docassemble.webapp.hooks.impl import hookimpl

@hookimpl
def get_ext_and_mimetype(filename):
    mimetype, encoding = mimetypes.guess_type(filename)  # pylint: disable=unused-variable
    extension = filename.lower()
    extension = re.sub(r'.*\.', '', extension)
    if extension == "jpeg":
        extension = "jpg"
    if extension == "tiff":
        extension = "tif"
    if extension == '3gpp':
        mimetype = 'audio/3gpp'
    if extension in ('yaml', 'yml'):
        mimetype = 'text/plain'
    return (extension, mimetype)


@hookimpl
def secure_filename_spaces_ok(filename):
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, "_")
    filename = str(re.sub(r'[^A-Za-z0-9\_\.\- ]', '', " ".join(filename.split(' ')))).strip("._ ")
    return filename


@hookimpl
def secure_filename_unicode_ok(the_filename):
    for sep in (os.path.sep, os.path.altsep):
        if sep:
            the_filename = the_filename.replace(sep, "_")
    the_filename = re.sub(r'[^\w_\.\- ]', '', the_filename, flags=re.UNICODE).strip("._ ")
    return the_filename


@hookimpl
def secure_filename(filename):
    filename = werkzeug.utils.secure_filename(filename).strip("._ ")
    if filename == '':
        filename = 'file'
    if '.' in filename:
        extension, mimetype = get_ext_and_mimetype(filename)  # pylint: disable=unused-variable
        filename = re.sub(r'\.[^\.]+$', '', filename).strip("._ ")
        if filename == '':
            filename = 'file'
        filename = filename + '.' + extension
    return filename


def sanitize_arguments(*pargs):
    for item in pargs:
        if isinstance(item, str):
            if item.startswith('/') or item.startswith('.') or re.search(r'\s', item):
                raise DAException("Invalid parameter " + item)


def directory_for(area, current_project):
    if current_project == 'default':
        return area.directory
    return os.path.join(area.directory, current_project)
