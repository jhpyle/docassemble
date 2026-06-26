from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, String, Text, DateTime, text
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base

class MachineLearning(Base):
    __tablename__ = dbtableprefix + "machinelearning"
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[Optional[str]] = mapped_column(String(1024))
    key: Mapped[Optional[str]] = mapped_column(String(1024), index=True)
    independent: Mapped[Optional[str]] = mapped_column(Text)
    dependent: Mapped[Optional[str]] = mapped_column(Text)
    info: Mapped[Optional[str]] = mapped_column(Text)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    modtime: Mapped[Optional[datetime]] = mapped_column(DateTime)
    active: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
