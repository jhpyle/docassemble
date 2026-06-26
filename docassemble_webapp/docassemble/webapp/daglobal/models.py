from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, true
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base

class GlobalObjectStorage(Base):
    __tablename__ = dbtableprefix + "globalobjectstorage"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[Optional[str]] = mapped_column(String(1024), index=True)
    value: Mapped[Optional[str]] = mapped_column(Text)
    encrypted: Mapped[bool] = mapped_column(Boolean, server_default=true())
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE")
    )
    temp_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "tempuser.id", ondelete="CASCADE")
    )
