from docassemble.base.error import DAException
from docassemble.base.functions import get_uid
from docassemble.webapp.files.file_number import get_new_file_number
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.interview.helpers import unattached_uid
from docassemble.webapp.utils.filenames import get_ext_and_mimetype
from .savedfile import SavedFile

@hookimpl
def save_numbered_file(filename, orig_path, yaml_file_name, uid):
    if uid is None:
        try:
            uid = get_uid()
            assert uid is not None
        except:
            uid = unattached_uid()
    if uid is None:
        raise DAException("save_numbered_file: uid not defined")
    file_number = get_new_file_number(uid, filename, yaml_file_name)
    extension, mimetype = get_ext_and_mimetype(filename)
    new_file = SavedFile(file_number, extension=extension, fix=True, should_not_exist=True)
    new_file.copy_from(orig_path)
    new_file.save(finalize=True)
    return (file_number, extension, mimetype)

@hookimpl
def get_saved_file_class():
    return SavedFile
