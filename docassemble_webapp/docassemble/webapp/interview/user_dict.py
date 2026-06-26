from sqlalchemy import delete, select, and_
from docassemble.webapp.extensions import db
from docassemble.webapp.utils.encryption import (
    decrypt_dictionary,
    unpack_dictionary,
)
from .models import UserDict


# @elapsed('fetch_user_dict')
def fetch_user_dict(user_code, filename, secret=None):
    # logmessage("fetch_user_dict: user_code is " + str(user_code) + " and filename is " + str(filename))
    user_dict = None
    steps = 1
    encrypted = True
    subq = select(db.func.max(UserDict.indexno).label('indexno'), db.func.count(UserDict.indexno).label('cnt')).where(and_(UserDict.key == user_code, UserDict.filename == filename)).subquery()  # pylint: disable=not-callable
    stmt = select(UserDict.indexno, UserDict.dictionary, UserDict.encrypted, subq.c.cnt).join(subq, subq.c.indexno == UserDict.indexno)
    result = db.session.execute(stmt)
    for d in list(result):
        # logmessage("fetch_user_dict: indexno is " + str(d.indexno))
        if d.dictionary and isinstance(d.dictionary, str):
            if d.encrypted:
                # logmessage("fetch_user_dict: entry was encrypted")
                user_dict = decrypt_dictionary(d.dictionary, secret)
                # logmessage("fetch_user_dict: decrypted dictionary")
            else:
                # logmessage("fetch_user_dict: entry was not encrypted")
                user_dict = unpack_dictionary(d.dictionary)
                # logmessage("fetch_user_dict: unpacked dictionary")
                encrypted = False
        if d.cnt:
            steps = d.cnt
        break
    return steps, user_dict, encrypted


# @elapsed('user_dict_exists')
# def user_dict_exists(user_code, filename):
#     result = db.session.execute(select(UserDict).where(and_(UserDict.key == user_code, UserDict.filename == filename))).first()
#     if result:
#         return True
#     return False


# @elapsed('fetch_previous_user_dict')
def fetch_previous_user_dict(user_code, filename, secret):
    max_indexno = db.session.execute(select(db.func.max(UserDict.indexno)).where(and_(UserDict.key == user_code, UserDict.filename == filename))).scalar()
    if max_indexno is not None:
        db.session.execute(delete(UserDict).where(UserDict.indexno == max_indexno))
        db.session.commit()
    return fetch_user_dict(user_code, filename, secret=secret)
