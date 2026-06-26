from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, true, false, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base


class ChatLog(Base):
    __tablename__ = dbtableprefix + "chatlog"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    key: Mapped[Optional[str]] = mapped_column(String(250), index=True)
    message: Mapped[Optional[str]] = mapped_column(Text)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
    )
    temp_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "tempuser.id", ondelete="CASCADE"),
    )
    owner_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
    )
    temp_owner_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "tempuser.id", ondelete="CASCADE"),
    )
    open_to_peer: Mapped[bool] = mapped_column(Boolean, server_default=false())
    encrypted: Mapped[bool] = mapped_column(Boolean, server_default=true())
    modtime: Mapped[Optional[datetime]] = mapped_column(DateTime)
