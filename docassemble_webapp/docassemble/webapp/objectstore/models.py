from typing import Optional
from sqlalchemy import (
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
import docassemble.webapp.users.models  # noqa: F401 # pylint: disable=unused-import
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base


class ObjectStorage(Base):
    __tablename__ = dbtableprefix + "objectstorage"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[Optional[str]] = mapped_column(String(1024), index=True)
    value: Mapped[Optional[str]] = mapped_column(Text)
