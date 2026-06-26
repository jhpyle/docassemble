from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    func,
    false,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column
import docassemble.webapp.users.models  # noqa: F401 # pylint: disable=unused-import
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base


class Uploads(Base):
    __tablename__ = dbtableprefix + "uploads"
    indexno: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[Optional[str]] = mapped_column(String(250), index=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    yamlfile: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    private: Mapped[bool] = mapped_column(Boolean, server_default=true())
    persistent: Mapped[bool] = mapped_column(Boolean, server_default=false())


class UploadsUserAuth(Base):
    __tablename__ = dbtableprefix + "uploadsuserauth"
    id: Mapped[int] = mapped_column(primary_key=True)
    uploads_indexno: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "uploads.indexno", ondelete="CASCADE"),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
        index=True
    )
    temp_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "tempuser.id", ondelete="CASCADE"),
        index=True
    )


class UploadsRoleAuth(Base):
    __tablename__ = dbtableprefix + "uploadsroleauth"
    id: Mapped[int] = mapped_column(primary_key=True)
    uploads_indexno: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "uploads.indexno", ondelete="CASCADE"),
        index=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "role.id", ondelete="CASCADE"),
        index=True
    )


class Supervisors(Base):
    __tablename__ = dbtableprefix + "supervisors"
    id: Mapped[int] = mapped_column(primary_key=True)
    hostname: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())  # pylint: disable=not-callable
    role: Mapped[Optional[str]] = mapped_column(Text)
