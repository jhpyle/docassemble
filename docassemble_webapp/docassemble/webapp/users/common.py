from sqlalchemy import select
from docassemble.webapp.extensions import db
from docassemble.webapp.users.models import UserModel

# @elapsed('get_person')
def get_person(user_id, cache):
    if user_id in cache:
        return cache[user_id]
    for record in db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=user_id)).unique().scalars():
        cache[record.id] = record
        return record
    return None


def user_is_developer(user_id):
    try:
        for user in db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles)).filter_by(id=int(user_id))).unique().scalars():
            for role in user.roles:
                if role.name in ('developer', 'admin'):
                    return True
    except:
        pass
    return False
