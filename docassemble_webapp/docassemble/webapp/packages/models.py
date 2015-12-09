from docassemble.webapp.app_and_db import db
from docassemble.webapp.config import daconfig, dbtableprefix

class Package(db.Model):
    __tablename__ = dbtableprefix + 'package'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    type = db.Column(db.Text()) #github, zip, pip
    giturl = db.Column(db.String(255), nullable=True, unique=True)
    upload = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'uploads.indexno', ondelete='CASCADE'))
    package_auth = db.relationship('PackageAuth', uselist=False, primaryjoin="PackageAuth.package_id==Package.id")
    version = db.Column(db.Integer())
    active = db.Column(db.Boolean(), nullable=False, server_default='1')

class PackageAuth(db.Model):
    __tablename__ = dbtableprefix + 'package_auth'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'package.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'user.id', ondelete='CASCADE'))
    authtype = db.Column(db.String(255), server_default='full')

class Install(db.Model):
    __tablename__ = dbtableprefix + "install"
    id = db.Column(db.Integer(), primary_key=True)
    hostname = db.Column(db.Text())
    version = db.Column(db.Integer())
    package_id = db.Column(db.Integer(), db.ForeignKey(dbtableprefix + 'package.id', ondelete='CASCADE'))
