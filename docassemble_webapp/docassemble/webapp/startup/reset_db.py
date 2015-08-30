from __future__ import print_function
import datetime

from app.app_and_db import app, db
from app.startup.init_app import init_app
from app.users.models import User, UserAuth, Role


def reset_db(app, db):
    """
    Delete all tables; Create all tables; Populate roles and users.
    """

    # Drop all tables
    print('Dropping all tables')
    db.drop_all()

    # Create all tables
    print('Creating all tables')
    db.create_all()

    # Adding roles
    print('Adding roles')
    admin_role = Role(name='admin')
    db.session.add(admin_role)

    # Add users
    print('Adding users')
    user = add_user(app, db, 'admin', 'Admin', 'User', 'admin@example.com', 'Password1')
    user.roles.append(admin_role)
    db.session.commit()


def add_user(app, db, username, first_name, last_name, email, password):
    """
    Create UserAuth and User records.
    """
    user_auth = UserAuth(username=username, password=app.user_manager.hash_password(password))
    user = User(
        active=True,
        first_name=first_name,
        last_name=last_name,
        email=email,
        confirmed_at=datetime.datetime.now(),
        user_auth=user_auth
    )
    db.session.add(user_auth)
    db.session.add(user)
    return user


# Initialize the app and reset the database
if __name__ == "__main__":
    init_app(app, db)
    reset_db(app, db)
