from docassemble.webapp.app_and_db import db
class Package(db.Model):
    __tablename__ = 'package'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    giturl = db.Column(db.String(255), nullable=True, unique=True)
    package_auth = db.relationship('PackageAuth', uselist=False, primaryjoin="PackageAuth.package_id==Package.id")
    active = db.Column(db.Boolean(), nullable=False, server_default='1')

class PackageAuth(db.Model):
    __tablename__ = 'package_auth'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer(), db.ForeignKey('package.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    authtype = db.Column(db.String(255), server_default='full')

