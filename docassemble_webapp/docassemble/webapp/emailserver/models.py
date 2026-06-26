from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base

class Email(Base):
    __tablename__ = dbtableprefix + "email"
    id: Mapped[int] = mapped_column(primary_key=True)
    short: Mapped[Optional[str]] = mapped_column(
        String(250),
        ForeignKey(dbtableprefix + "shortener.short", ondelete="CASCADE"),
    )
    all_addr: Mapped[Optional[str]] = mapped_column(Text)
    to_addr: Mapped[Optional[str]] = mapped_column(Text)
    cc_addr: Mapped[Optional[str]] = mapped_column(Text)
    from_addr: Mapped[Optional[str]] = mapped_column(Text)
    reply_to_addr: Mapped[Optional[str]] = mapped_column(Text)
    return_path_addr: Mapped[Optional[str]] = mapped_column(Text)
    subject: Mapped[Optional[str]] = mapped_column(Text)
    datetime_message: Mapped[Optional[datetime]] = mapped_column(DateTime)
    datetime_received: Mapped[Optional[datetime]] = mapped_column(DateTime)


class EmailAttachment(Base):
    __tablename__ = dbtableprefix + "emailattachment"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_id: Mapped[Optional[int]] = mapped_column(
        Integer(),
        ForeignKey(dbtableprefix + "email.id", ondelete="CASCADE"),
    )
    index: Mapped[Optional[int]] = mapped_column(Integer)
    content_type: Mapped[Optional[str]] = mapped_column(Text)
    extension: Mapped[Optional[str]] = mapped_column(Text)
    upload: Mapped[Optional[int]] = mapped_column(
        Integer(),
        ForeignKey(dbtableprefix + "uploads.indexno", ondelete="CASCADE"),
    )


class Shortener(Base):
    __tablename__ = dbtableprefix + "shortener"
    id: Mapped[int] = mapped_column(primary_key=True)
    short: Mapped[str] = mapped_column(String(250), unique=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    uid: Mapped[Optional[str]] = mapped_column(String(250))
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer(),
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
    )
    temp_user_id: Mapped[Optional[int]] = mapped_column(
        Integer(),
        ForeignKey(dbtableprefix + "tempuser.id", ondelete="CASCADE"),
    )
    key: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    index: Mapped[Optional[int]] = mapped_column(Integer)
    modtime: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())  # pylint: disable=not-callable
