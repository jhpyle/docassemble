from typing import Optional
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, text, true, false
from sqlalchemy.orm import Mapped, mapped_column, relationship
from docassemble.webapp.database import dbtableprefix
from docassemble.webapp.db_base import Base


class Package(Base):
    __tablename__ = dbtableprefix + 'package'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[Optional[str]] = mapped_column(Text)  # github, zip, pip
    giturl: Mapped[Optional[str]] = mapped_column(String(255))
    gitsubdir: Mapped[Optional[str]] = mapped_column(Text)
    upload: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "uploads.indexno", ondelete="CASCADE"),
    )
    package_auth: Mapped[Optional["PackageAuth"]] = relationship(primaryjoin="PackageAuth.package_id==Package.id")
    version: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'))
    packageversion: Mapped[Optional[str]] = mapped_column(Text)
    limitation: Mapped[Optional[str]] = mapped_column(Text)
    dependency: Mapped[bool] = mapped_column(Boolean, server_default=false())
    core: Mapped[bool] = mapped_column(Boolean, server_default=false())
    active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    gitbranch: Mapped[Optional[str]] = mapped_column(String(255))


class PackageAuth(Base):
    __tablename__ = dbtableprefix + 'package_auth'
    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "package.id", ondelete="CASCADE"),
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "user.id", ondelete="CASCADE"),
    )
    authtype: Mapped[Optional[str]] = mapped_column(String(255), server_default=text("'owner'"))


class Install(Base):
    __tablename__ = dbtableprefix + "install"
    id: Mapped[int] = mapped_column(primary_key=True)
    hostname: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[Optional[int]] = mapped_column(Integer)
    packageversion: Mapped[Optional[str]] = mapped_column(Text)
    package_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(dbtableprefix + "package.id", ondelete="CASCADE"),
    )
