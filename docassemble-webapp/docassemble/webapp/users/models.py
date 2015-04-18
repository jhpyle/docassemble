# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
from docassemble.webapp.app_and_db import db

# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True, unique=True)
    confirmed_at = db.Column(db.DateTime())
    active = db.Column('active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(50), nullable=False, server_default='')
    last_name = db.Column(db.String(50), nullable=False, server_default='')
    country = db.Column(db.String(2))
    subdivisionfirst = db.Column(db.String(2))
    subdivisionsecond = db.Column(db.String(50))
    subdivisionthird = db.Column(db.String(50))
    organization = db.Column(db.String(64))
    user_auth = db.relationship('UserAuth', uselist=False, primaryjoin="UserAuth.user_id==User.id")
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('user', lazy='dynamic'))


# Define the UserAuth data model.
class UserAuth(db.Model, UserMixin):
    __tablename__ = 'user_auth'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    #username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    user = db.relationship('User', uselist=False, primaryjoin="User.id==UserAuth.user_id")


# Define the Role data model
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))


# Define the UserRoles association model
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

