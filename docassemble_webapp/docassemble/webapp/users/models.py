from datetime import datetime
from typing import Optional
from flask_login import AnonymousUserMixin
from sqlalchemy import Integer, String, ForeignKey, DateTime, text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from docassemble_flask_user import UserMixin
from docassemble.webapp.config import allowed
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base

class AnonymousUserModel(AnonymousUserMixin):

    @property
    def id(self):
        return -1

    def same_as(self, user_id):  # pylint: disable=unused-argument
        return False

    def has_role(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        return False

    def has_roles(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        return False

    def has_role_or_permission(self, *specified_role_names, permissions=None):  # pylint: disable=unused-argument
        if isinstance(permissions, list):
            for task in permissions:
                if self.can_do(task):
                    return True
        return False

    def can_do(self, task):
        return bool('anonymous' in allowed and task in allowed['anonymous'])


class UserModel(Base, UserMixin):
    __tablename__ = dbtableprefix + 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    social_id: Mapped[str] = mapped_column(String(255), unique=True)
    nickname: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    active: Mapped[bool] = mapped_column(Boolean, server_default="0")
    first_name: Mapped[str] = mapped_column(String(255), server_default=text("''"))
    last_name: Mapped[str] = mapped_column(String(255), server_default=text("''"))
    country: Mapped[Optional[str]] = mapped_column(String(3))
    subdivisionfirst: Mapped[Optional[str]] = mapped_column(String(255))
    subdivisionsecond: Mapped[Optional[str]] = mapped_column(String(255))
    subdivisionthird: Mapped[Optional[str]] = mapped_column(String(255))
    organization: Mapped[Optional[str]] = mapped_column(String(255))
    timezone: Mapped[Optional[str]] = mapped_column(String(64))
    language: Mapped[Optional[str]] = mapped_column(String(64))
    user_auth: Mapped[Optional["UserAuthModel"]] = relationship(primaryjoin="UserAuthModel.user_id==UserModel.id", back_populates="user")
    roles: Mapped[list["Role"]] = relationship(secondary=dbtableprefix + 'user_roles', backref=backref(dbtableprefix + 'user', lazy='dynamic'))
    password: Mapped[str] = mapped_column(String(255), server_default=text("''"))
    otp_secret: Mapped[Optional[str]] = mapped_column(String(255))
    pypi_username: Mapped[Optional[str]] = mapped_column(String(255))
    pypi_password: Mapped[Optional[str]] = mapped_column(String(255))
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    limited_api = False

    def same_as(self, user_id):
        if self.limited_api:
            return False
        return self.id == user_id

    def has_role(self, *specified_role_names):
        if len(self.roles) == 0 and 'user' in specified_role_names:
            return True
        return super().has_role(*specified_role_names)

    def has_role_or_permission(self, *specified_role_names, permissions=None):
        if self.limited_api:
            if isinstance(permissions, list):
                for task in permissions:
                    if self.can_do(task):
                        return True
            return False
        role_result = self.has_role(*specified_role_names)
        if not role_result and isinstance(permissions, list):
            for task in permissions:
                if self.can_do(task):
                    return True
        return role_result

    def can_do(self, task):
        if self.is_anonymous:
            return False
        if self.limited_api:
            return bool(task in self.limits)
        if hasattr(self, 'roles'):
            the_roles = self.roles
        else:
            if hasattr(self, 'user_profile') and hasattr(self.user_profile, 'roles'):  # pylint: disable=no-member
                the_roles = self.user_profile.roles  # pylint: disable=no-member
            else:
                the_roles = None
        for role in the_roles:
            if role.name in allowed and task in allowed[role.name]:
                return True
        return False


class UserAuthModel(Base, UserMixin):
    __tablename__ = dbtableprefix + 'user_auth'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
        index=True
    )
    password: Mapped[str] = mapped_column(String(255), server_default="''")
    reset_password_token: Mapped[str] = mapped_column(String(100), server_default="''")
    # active = db.Column(db.Boolean(), nullable=False, server_default='0')
    user: Mapped[Optional["UserModel"]] = relationship(primaryjoin="UserModel.id==UserAuthModel.user_id", back_populates="user_auth")


class Role(Base):
    __tablename__ = dbtableprefix + 'role'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))


class UserRoles(Base):
    __tablename__ = dbtableprefix + 'user_roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
        index=True
    )
    role_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "role.id", ondelete="CASCADE"),
        index=True
    )


class TempUser(Base):
    __tablename__ = dbtableprefix + 'tempuser'
    id: Mapped[int] = mapped_column(primary_key=True)


class MyUserInvitation(Base):
    __tablename__ = dbtableprefix + 'user_invite'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "role.id", ondelete="CASCADE"),
    )
    # save the user of the invitee
    invited_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
    )
    # token used for registration page to identify user registering
    token: Mapped[str] = mapped_column(String(100), server_default="''")
