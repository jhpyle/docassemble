from flask import session
from flask_login import current_user
from sqlalchemy import and_, select
from docassemble.base.functions import get_uid
from docassemble.webapp.extensions import db
from docassemble.webapp.interview.models import UserDictKeys
from docassemble.webapp.main.models import UploadsRoleAuth, Uploads, UploadsUserAuth
from docassemble.webapp.users.models import UserRoles

# @elapsed('can_access_file_number')
def can_access_file_number(file_number, uids=None):
    upload = db.session.execute(select(Uploads).where(Uploads.indexno == file_number)).scalar()
    if upload is None:
        return False
    if current_user and current_user.is_authenticated and current_user.has_role('admin', 'developer', 'advocate', 'trainer'):
        return True
    if not upload.private:
        return True
    if uids is None or len(uids) == 0:
        new_uid = get_uid()
        if new_uid is not None:
            uids = [new_uid]
        else:
            uids = []
    if upload.key in uids:
        return True
    if current_user and current_user.is_authenticated:
        if db.session.execute(select(UserDictKeys).filter_by(key=upload.key, user_id=current_user.id)).first() or db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, user_id=current_user.id)).first() or db.session.execute(select(UploadsRoleAuth).join(UserRoles, and_(UserRoles.user_id == current_user.id, UploadsRoleAuth.role_id == UserRoles.role_id)).where(UploadsRoleAuth.uploads_indexno == file_number)).first():
            return True
    elif session and 'tempuser' in session:
        temp_user_id = int(session['tempuser'])
        if db.session.execute(select(UserDictKeys).filter_by(key=upload.key, temp_user_id=temp_user_id)).first() or db.session.execute(select(UploadsUserAuth).filter_by(uploads_indexno=file_number, temp_user_id=temp_user_id)).first():
            return True
    return False
