import sys
import pip
import socket
import tempfile
import threading
if __name__ == "__main__":
    import docassemble.webapp.config
    docassemble.webapp.config.load(arguments=sys.argv)
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.packages.models import Package, Install

def check_for_updates():
    from docassemble.webapp.config import hostname
    ok = True
    here_already = list()
    installed_packages = pip.get_installed_distributions()
    for package in installed_packages:
        here_already.append(package.key)
    packages = dict()
    installs = dict()
    to_install = list()
    to_uninstall = list()
    uninstalled_packages = dict()
    for package in Package.query.filter_by(active=True).all():
        if package.type is not None:
            packages[package.id] = package
            #print "Found a package " + package.name
    for package in Package.query.filter_by(active=False).all():
        uninstalled_packages[package.id] = package
    for install in Install.query.filter_by(hostname=hostname).all():
        installs[install.package_id] = install
        if install.package_id in uninstalled_packages:
            to_uninstall.append(uninstalled_packages[install.package_id])
    changed = False
    for package in packages.itervalues():
        if package.id not in installs and package.name in here_already:
            sys.stderr.write("Package " + package.name + " here already\n")
            install = Install(hostname=hostname, version=1, package_id=package.id)
            db.session.add(install)
            installs[package.id] = install
            changed = True
    if changed:
        db.session.commit()
    for package in packages.itervalues():
        if package.id not in installs or package.version > installs[package.id].version:
            to_install.append(package)
    for package in to_uninstall:
        returnval = uninstall_package(package)
        if returnval == 0:
            Install.query.filter_by(hostname=hostname, package_id=package.id).delete()
        else:
            ok = False
    for package in to_install:
        returnval = install_package(package)
        if returnval == 0:
            if package.id in installs:
                install = installs[package.id]
                install.version = package.version
            else:
                install = Install(hostname=hostname, version=package.version, package_id=package.id)
                db.session.add(install)
        else:
            ok = False
    db.session.commit()
    return ok

def install_package(package):
    #sys.stderr.write("install_package: installing " + package.name + "\n")
    #return 0
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    pip_log = tempfile.NamedTemporaryFile()
    if package.type == 'zip' and package.upload is not None:
        saved_file = SavedFile(package.upload, extension='zip', fix=True)
        commands = ['install', '--quiet', '--egg', '--no-index', '--src=' + tempfile.mkdtemp(), '--log-file=' + pip_log.name, '--upgrade', saved_file.path + '.zip']
    elif package.type == 'git' and package.giturl is not None:
        commands = ['install', '--quiet', '--egg', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + package.giturl + '.git#egg=' + package.name]
    elif package.type == 'pip':
        commands = ['install', '--quiet', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, package.name]
    else:
        return
    returnval = pip.main(commands)
    return returnval

def uninstall_package(package):
    #sys.stderr.write("uninstall_package: uninstalling " + package.name + "\n")
    #return 0
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    pip_log = tempfile.NamedTemporaryFile()
    commands = ['uninstall', '--quiet', '--log-file=' + pip_log.name, package.name]
    returnval = pip.main(commands)
    return returnval

if __name__ == "__main__":
    import docassemble.webapp.database
    app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
    check_for_updates()
