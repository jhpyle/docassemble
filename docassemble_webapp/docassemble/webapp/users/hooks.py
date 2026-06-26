from sqlalchemy import select
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.users.models import UserModel

class FakeUser:
    pass


class FakeRole:
    pass

@hookimpl
def user_id_dict():
    output = {}
    for user in db.session.execute(select(UserModel).options(db.joinedload(UserModel.roles))).unique().scalars():
        output[user.id] = user
    anon = FakeUser()
    anon_role = FakeRole()
    anon_role.name = 'anonymous'
    anon.roles = [anon_role]
    anon.id = -1
    anon.firstname = 'Anonymous'
    anon.lastname = 'User'
    output[-1] = anon
    return output
