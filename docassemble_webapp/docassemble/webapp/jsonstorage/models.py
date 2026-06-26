from datetime import datetime
from typing import Optional
from sqlalchemy import Any, String, Text, DateTime, func, Boolean, false
from sqlalchemy.orm import Mapped, mapped_column
from docassemble.webapp.database import dbtableprefix, json_dbprefix
from docassemble.webapp.config import daconfig
from docassemble.webapp.db_base import JsonBase

class JsonStorage(JsonBase):
    __tablename__ = dbtableprefix + "jsonstorage"
    if daconfig.get('variables snapshot db'):
        __bind_key__ = 'variables_snapshot'
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    key: Mapped[Optional[str]] = mapped_column(String(250), index=True)
    if json_dbprefix.startswith('postgresql'):
        from sqlalchemy.dialects.postgresql import JSONB
        data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    else:
        data: Mapped[Optional[str]] = mapped_column(Text)  # type: ignore[no-redef]
    tags: Mapped[Optional[str]] = mapped_column(Text)
    modtime: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())  # pylint: disable=not-callable
    persistent: Mapped[bool] = mapped_column(Boolean, server_default=false())
