import datetime
from sqlalchemy import select
from docassemble.base.generate_key import random_alphanumeric
from docassemble.webapp.extensions import db
from docassemble.webapp.lock import obtain_lock, release_lock
from docassemble.webapp.utils.encryption import encrypt_dictionary
from docassemble.webapp.interview.dictionary import fresh_dictionary
from .models import UserDict

def get_unique_name(filename, secret):
    nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    while True:
        newname = random_alphanumeric(32)
        obtain_lock(newname, filename)
        existing_key = db.session.execute(select(UserDict).filter_by(key=newname)).first()
        if existing_key:
            release_lock(newname, filename)
            continue
        new_user_dict = UserDict(modtime=nowtime, key=newname, filename=filename, dictionary=encrypt_dictionary(fresh_dictionary(), secret))
        db.session.add(new_user_dict)
        db.session.commit()
        return newname
