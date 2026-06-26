import json
import shutil
import re
import tempfile
import os
from urllib.parse import quote as urllibquote
import werkzeug
from flask import redirect
from flask_login import current_user
from sqlalchemy import select, delete
from docassemble.base.error import DAException
from docassemble.base.functions import package_data_filename
from docassemble.base.util import DAFile, DAFileList, DAFileCollection, DAStaticFile
from docassemble.webapp.cloud.utils import cloud
from docassemble.webapp.config import daconfig
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import db
from docassemble.webapp.files.common import can_access_file_number
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.main.models import UploadsRoleAuth, Uploads, UploadsUserAuth
from docassemble.webapp.sessions import get_session_uids
from docassemble.webapp.users.models import Role, UserModel
from docassemble.webapp.utils.filenames import (
    get_ext_and_mimetype,
    secure_filename_unicode_ok,
)
from docassemble.webapp.utils.helpers import custom_send_file
from docassemble.webapp.utils.logger import logmessage
from .file_access import get_info_from_file_number, get_info_from_file_reference
from .savedfile import SavedFile

# @elapsed('file_set_attributes')
@hookimpl
def file_set_attributes(file_number, private, persistent, session, filename):
    upload = db.session.execute(select(Uploads).filter_by(indexno=file_number).with_for_update()).scalar()
    if upload is None:
        db.session.commit()
        raise DAException("file_set_attributes: file number " + str(file_number) + " not found.")
    if private in [True, False] and upload.private != private:
        upload.private = private
    if persistent in [True, False] and upload.persistent != persistent:
        upload.persistent = persistent
    if isinstance(session, str):
        upload.key = session
    if isinstance(filename, str):
        upload.filename = filename
    db.session.commit()


@hookimpl
def file_user_access(file_number, allow_user_id, allow_email, disallow_user_id, disallow_email, disallow_all):
    something_added = False
    if allow_user_id:
        for user_id in set(allow_user_id):
            existing_user = db.session.execute(select(UserModel).filter_by(id=user_id)).first()
            if not existing_user:
                logmessage("file_user_access: invalid user ID " + repr(user_id))
                continue
            if db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=user_id)).first():
                continue
            new_auth_record = UploadsUserAuth(uploads_indexno=file_number, user_id=user_id)
            db.session.add(new_auth_record)
            something_added = True
    if something_added:
        db.session.commit()
    something_added = False
    if allow_email:
        for email in set(allow_email):
            existing_user = db.session.execute(select(UserModel).filter_by(email=email)).first()
            if not existing_user:
                logmessage("file_user_access: invalid email " + repr(email))
                continue
            if db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=existing_user.id)).first():
                continue
            new_auth_record = UploadsUserAuth(uploads_indexno=file_number, user_id=existing_user.id)
            db.session.add(new_auth_record)
            something_added = True
    if something_added:
        db.session.commit()
    if disallow_user_id:
        for user_id in set(disallow_user_id):
            db.session.execute(delete(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=user_id))
        db.session.commit()
    if disallow_email:
        for email in set(disallow_email):
            existing_user = db.session.execute(select(UserModel).filter_by(email=email)).scalar()
            if not existing_user:
                logmessage("file_user_access: invalid email " + repr(email))
                continue
            db.session.execute(delete(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=existing_user.id))
        db.session.commit()
    if disallow_all:
        db.session.execute(delete(UploadsUserAuth).filter_by(uploads_indexno=file_number))
    if not (allow_user_id or allow_email or disallow_user_id or disallow_email or disallow_all):
        result = {'user_ids': [], 'emails': [], 'temp_user_ids': []}
        for auth in db.session.execute(select(UploadsUserAuth.user_id, UploadsUserAuth.temp_user_id, UserModel.email).outerjoin(UserModel, UploadsUserAuth.user_id == UserModel.id).where(UploadsUserAuth.uploads_indexno == file_number)).all():
            if auth.user_id is not None:
                result['user_ids'].append(auth.user_id)
            if auth.temp_user_id is not None:
                result['temp_user_ids'].append(auth.temp_user_id)
            if auth.email:
                result['emails'].append(auth.email)
        return result
    return None


@hookimpl
def file_privilege_access(file_number, allow, disallow, disallow_all):
    something_added = False
    if allow:
        for privilege in set(allow):
            existing_role = db.session.execute(select(Role).filter_by(name=privilege)).scalar_one()
            if not existing_role:
                logmessage("file_privilege_access: invalid privilege " + repr(privilege))
                continue
            if db.session.execute(select(UploadsRoleAuth).filter_by(uploads_indexno=file_number, role_id=existing_role.id)).first():
                continue
            new_auth_record = UploadsRoleAuth(uploads_indexno=file_number, role_id=existing_role.id)
            db.session.add(new_auth_record)
            something_added = True
    if something_added:
        db.session.commit()
    if disallow:
        for privilege in set(disallow):
            existing_role = db.session.execute(select(Role).filter_by(name=privilege)).scalar_one()
            if not existing_role:
                logmessage("file_privilege_access: invalid privilege " + repr(privilege))
                continue
            db.session.execute(delete(UploadsRoleAuth).filter_by(uploads_indexno=file_number, role_id=existing_role.id))
        db.session.commit()
    if disallow_all:
        db.session.execute(delete(UploadsRoleAuth).filter_by(uploads_indexno=file_number))
    if not (allow or disallow or disallow_all):
        result = []
        for auth in db.session.execute(select(UploadsRoleAuth.id, Role.name).join(Role, UploadsRoleAuth.role_id == Role.id).where(UploadsRoleAuth.uploads_indexno == file_number)).all():
            result.append(auth.name)
        return result
    return None

@hookimpl(specname="file_finder")
def file_finder(file_reference, question, folder, package, filename, return_nonexistent, uids):
    return get_info_from_file_reference_with_uids(file_reference, question=question, folder=folder, package=package, filename=filename, return_nonexistent=return_nonexistent, uids=uids)

def get_info_from_file_reference_with_uids(*pargs, **kwargs):
    if 'uids' not in kwargs:
        kwargs['uids'] = get_session_uids()
    return get_info_from_file_reference(*pargs, **kwargs)


@hookimpl(specname="file_number_finder")
def get_info_from_file_number_with_uids(file_number, filename, uids, privileged):
    if uids is None:
        uids = get_session_uids()
    return get_info_from_file_number(file_number, privileged=privileged, filename=filename, uids=uids)


@hookimpl
def path_from_reference(file_reference):
    if isinstance(file_reference, DAFileCollection):
        file_reference = file_reference._first_file()
    if isinstance(file_reference, DAFileList):
        file_reference = file_reference[0]
    if isinstance(file_reference, DAFile):
        file_info = get_info_from_file_number(file_reference.number, uids=get_session_uids())
        if 'fullpath' not in file_info:
            raise DAException("File not found")
        friendly_path = os.path.join(tempfile.mkdtemp(prefix='SavedFile'), file_reference.filename)
        try:
            os.symlink(file_info['fullpath'], friendly_path)
        except:
            shutil.copyfile(file_info['fullpath'], friendly_path)
        return friendly_path
    if isinstance(file_reference, DAStaticFile):
        return file_reference.path()
    if file_reference is None:
        return None
    file_info = get_info_from_file_reference(file_reference)
    if 'fullpath' not in file_info:
        raise DAException("File not found")
    return file_info['fullpath']


def do_serve_stored_file(uid, number, filename, extension, download=False):
    number = re.sub(r'[^0-9]', '', str(number))
    if not can_access_file_number(number, uids=[uid]):
        return ('File not found', 404)
    try:
        file_info = get_info_from_file_number(number, privileged=True, uids=get_session_uids())
    except:
        return ('File not found', 404)
    if 'path' not in file_info:
        return ('File not found', 404)
    if not os.path.isfile(file_info['path']):
        return ('File not found', 404)
    response = custom_send_file(file_info['path'], mimetype=file_info['mimetype'], download_name=filename + '.' + extension)
    if download:
        response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename + '.' + extension))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def do_serve_temporary_file(code, filename, extension, download=False):
    file_info = r.get('da:tempfile:' + str(code))
    if file_info is None:
        logmessage("serve_temporary_file: file_info was none")
        return ('File not found', 404)
    (section, file_number) = file_info.decode().split('^')
    the_file = SavedFile(file_number, fix=True, section=section)
    the_path = the_file.path
    if not os.path.isfile(the_path):
        return ('File not found', 404)
    (extension, mimetype) = get_ext_and_mimetype(filename + '.' + extension)
    response = custom_send_file(the_path, mimetype=mimetype, download_name=filename + '.' + extension)
    if download:
        response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename + '.' + extension))
    return response


def do_serve_uploaded_file_with_filename_and_extension(number, filename, extension, download=False):
    filename = secure_filename_unicode_ok(filename)
    extension = werkzeug.utils.secure_filename(extension)
    privileged = bool(current_user.is_authenticated and current_user.has_role('admin', 'advocate'))
    number = re.sub(r'[^0-9]', '', str(number))
    if cloud is not None and daconfig.get('use cloud urls', False):
        if not (privileged or can_access_file_number(number, uids=get_session_uids())):
            return ('File not found', 404)
        the_file = SavedFile(number)
        if download:
            return redirect(the_file.temp_url_for(_attachment=True))
        return redirect(the_file.temp_url_for())
    try:
        file_info = get_info_from_file_number(number, privileged=privileged, uids=get_session_uids())
    except:
        return ('File not found', 404)
    if 'path' not in file_info:
        return ('File not found', 404)
    # logmessage("Filename is " + file_info['path'] + '.' + extension)
    if os.path.isfile(file_info['path'] + '.' + extension):
        # logmessage("Using " + file_info['path'] + '.' + extension)
        extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
        response = custom_send_file(file_info['path'] + '.' + extension, mimetype=mimetype, download_name=filename + '.' + extension)
        if download:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename + '.' + extension))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    if os.path.isfile(os.path.join(os.path.dirname(file_info['path']), filename + '.' + extension)):
        # logmessage("Using " + os.path.join(os.path.dirname(file_info['path']), filename + '.' + extension))
        extension, mimetype = get_ext_and_mimetype(filename + '.' + extension)
        response = custom_send_file(os.path.join(os.path.dirname(file_info['path']), filename + '.' + extension), mimetype=mimetype, download_name=filename + '.' + extension)
        if download:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(filename + '.' + extension))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    return ('File not found', 404)


def do_serve_uploaded_file_with_extension(number, extension, download=False):
    extension = werkzeug.utils.secure_filename(extension)
    privileged = bool(current_user.is_authenticated and current_user.has_role('admin', 'advocate'))
    number = re.sub(r'[^0-9]', '', str(number))
    if cloud is not None and daconfig.get('use cloud urls', False):
        if not can_access_file_number(number, uids=get_session_uids()):
            return ('File not found', 404)
        the_file = SavedFile(number)
        if download:
            return redirect(the_file.temp_url_for(_attachment=True))
        return redirect(the_file.temp_url_for())
    try:
        file_info = get_info_from_file_number(number, privileged=privileged, uids=get_session_uids())
    except:
        return ('File not found', 404)
    if 'path' not in file_info:
        return ('File not found', 404)
    if os.path.isfile(file_info['path'] + '.' + extension):
        extension, mimetype = get_ext_and_mimetype(file_info['path'] + '.' + extension)
        response = custom_send_file(file_info['path'] + '.' + extension, mimetype=mimetype, download_name=str(number) + '.' + extension)
        if download:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(str(number) + '.' + extension))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    return ('File not found', 404)


def do_serve_uploaded_file(number, download=False):
    number = re.sub(r'[^0-9]', '', str(number))
    privileged = bool(current_user.is_authenticated and current_user.has_role('admin', 'advocate'))
    try:
        file_info = get_info_from_file_number(number, privileged=privileged, uids=get_session_uids())
    except:
        return ('File not found', 404)
    if 'path' not in file_info:
        return ('File not found', 404)
    if not os.path.isfile(file_info['path']):
        return ('File not found', 404)
    response = custom_send_file(file_info['path'], mimetype=file_info['mimetype'], download_name=os.path.basename(file_info['path']))
    if download:
        response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(os.path.basename(file_info['path'])))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


def do_serve_uploaded_page(number, page, download=False, size='page'):
    number = re.sub(r'[^0-9]', '', str(number))
    page = re.sub(r'[^0-9]', '', str(page))
    privileged = bool(current_user.is_authenticated and current_user.has_role('admin', 'advocate'))
    try:
        file_info = get_info_from_file_number(number, privileged=privileged, uids=get_session_uids())
    except BaseException as err:
        logmessage("do_serve_uploaded_page: " + err.__class__.__name__ + str(err))
        return ('File not found', 404)
    if 'path' not in file_info:
        logmessage('serve_uploaded_page: no access to file number ' + str(number))
        return ('File not found', 404)
    try:
        the_file = DAFile(mimetype=file_info['mimetype'], extension=file_info['extension'], number=number, make_thumbnail=page)
        filename = the_file.page_path(page, size)
        assert filename is not None
    except BaseException as err:
        logmessage("Could not make thumbnail: " + err.__class__.__name__ + ": " + str(err))
        filename = None
    if filename is None:
        logmessage("do_serve_uploaded_page: sending blank image")
        the_file = package_data_filename('docassemble.base:data/static/blank_page.png')
        response = custom_send_file(the_file, mimetype='image/png', download_name='blank_page.png')
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    if os.path.isfile(filename):
        response = custom_send_file(filename, mimetype='image/png', download_name=os.path.basename(filename))
        if download:
            response.headers['Content-Disposition'] = 'attachment; filename=' + json.dumps(urllibquote(os.path.basename(filename)))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    logmessage('do_serve_uploaded_page: path ' + filename + ' is not a file')
    return ('File not found', 404)
