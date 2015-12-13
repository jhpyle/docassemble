import sys
import socket
import tempfile
from docassemble.webapp.config import hostname
if __name__ == "__main__":
    import docassemble.webapp.config
    docassemble.webapp.config.load(arguments=sys.argv)
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.packages.models import Package, Install

def check_for_updates():
    packages = dict()
    installs = dict()
    to_install = list()
    for package in Package.query.filter_by(active=True).all():
        if package.type is not None:
            packages[package.id] = package
            print "Found a package " + package.name
    for install in Install.query.filter_by(hostname=hostname).all():
        installs[install.package_id] = install
    for package in packages.itervalues():
        if package.id not in installs or package.version > installs[package.id].version:
            to_install.append(package)
    for package in to_install:
        returnval = install_package(package)
        if returnval == 0:
            if package.id in installs:
                install = installs[package.id]
                install.version = package.version
            else:
                install = Install(hostname=hostname, version=package.version, package_id=package.id)
                db.session.add(install)
    db.session.commit()

def install_package(package):
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    pip_log = tempfile.NamedTemporaryFile()
    if package.type == 'zip' and package.upload is not None:
        saved_file = SavedFile(package.upload, extension='zip', fix=True)
        commands = ['install', '--quiet', '--egg', '--no-index', '--src=' + tempfile.mkdtemp(), '--log-file=' + pip_log.name, '--upgrade', saved_file.path + '.zip']
    elif package.type == 'github' and package.giturl is not None:
        commands = ['install', '--quiet', '--egg', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + giturl + '.git#egg=' + package.name]
    elif package.type == 'pip':
        commands = ['install', '--quiet', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, package.name]
    returnval = pip.main(commands)
    return returnval

if __name__ == "__main__":
    import docassemble.webapp.database
    app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
    check_for_updates()
