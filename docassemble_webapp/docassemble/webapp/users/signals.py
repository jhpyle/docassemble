from sqlalchemy import select
from docassemble_flask_user import (
    user_logged_in,
    user_changed_password,
    user_registered,
)
from docassemble.webapp.extensions import db
from docassemble.webapp.interview.helpers import fix_secret
from .helpers import update_last_login, login_or_register
from .models import Role

def on_user_login(sender, user, **extra):
    # logmessage("on user login")
    update_last_login(user)
    login_or_register(sender, user, 'login', **extra)
    # flash(word('You have signed in successfully.'), 'success')


def on_password_change(sender, user, **extra):  # pylint: disable=unused-argument
    # logmessage("on password change")
    fix_secret(user=user)

# @user_reset_password.connect_via(app)
# def _on_password_reset(sender, user, **extra):
#     # logmessage("on password reset")
#     fix_secret(user=user)


def on_register_hook(sender, user, **extra):
    # why did I not just import it globally?
    # from docassemble.webapp.users.models import Role
    user_invite = extra.get('user_invite', None)
    this_user_role = None
    if user_invite is not None:
        this_user_role = db.session.execute(select(Role).filter_by(id=user_invite.role_id)).scalar()
    if this_user_role is None:
        this_user_role = db.session.execute(select(Role).filter_by(name='user')).scalar()
    roles_to_remove = []
    for role in user.roles:
        roles_to_remove.append(role)
    for role in roles_to_remove:
        user.roles.remove(role)
    user.roles.append(this_user_role)
    db.session.commit()
    update_last_login(user)
    login_or_register(sender, user, 'register', **extra)


def register_signals(app):
    user_logged_in.connect(on_user_login, app)
    user_changed_password.connect(on_password_change, app)
    user_registered.connect(on_register_hook, app)
