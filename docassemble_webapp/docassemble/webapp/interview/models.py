from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, ForeignKey, Index, DateTime, true, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base


class UserDict(Base):
    __tablename__ = dbtableprefix + "userdict"
    __table_args__ = (
        Index(dbtableprefix + 'ix_userdict_key_filename', 'key', 'filename'),
    )
    indexno: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    key: Mapped[Optional[str]] = mapped_column(String(250), index=True)
    dictionary: Mapped[Optional[str]] = mapped_column(Text)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
    )
    encrypted: Mapped[bool] = mapped_column(Boolean, server_default=true())
    modtime: Mapped[Optional[datetime]] = mapped_column(DateTime)


class UserDictKeys(Base):
    __tablename__ = dbtableprefix + "userdictkeys"
    __table_args__ = (
        Index(dbtableprefix + 'ix_userdictkeys_key_filename', 'key', 'filename'),
    )
    indexno: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    key: Mapped[Optional[str]] = mapped_column(String(250), index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
        index=True
    )
    temp_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "tempuser.id", ondelete="CASCADE"),
        index=True
    )
