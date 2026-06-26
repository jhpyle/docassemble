from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column
import docassemble.webapp.users.models  # noqa: F401 # pylint: disable=unused-import
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base

class SpeakList(Base):
    __tablename__ = dbtableprefix + "speaklist"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    key: Mapped[Optional[str]] = mapped_column(String(250), index=True)
    phrase: Mapped[Optional[str]] = mapped_column(Text)
    question: Mapped[Optional[int]] = mapped_column(Integer)
    type: Mapped[Optional[str]] = mapped_column(String(20))
    language: Mapped[Optional[str]] = mapped_column(String(10))
    dialect: Mapped[Optional[str]] = mapped_column(String(10))
    voice: Mapped[Optional[str]] = mapped_column(String(20))
    upload: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "uploads.indexno", ondelete="CASCADE"),
        index=True
    )
    encrypted: Mapped[bool] = mapped_column(Boolean, server_default=true())
    digest: Mapped[Optional[str]] = mapped_column(Text)
