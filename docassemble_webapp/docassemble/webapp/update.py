import os
import sys
import pip.utils.logging
import pip
import socket
import tempfile
import threading
import subprocess
import xmlrpclib

from distutils.version import LooseVersion
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.packages.models import Package, Install, PackageAuth
from docassemble.webapp.core.models import Supervisors
from docassemble.base.logger import logmessage
from docassemble.webapp.files import SavedFile

supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
if supervisor_url:
    USING_SUPERVISOR = True
else:
    USING_SUPERVISOR = False

def remove_inactive_hosts():
    from docassemble.base.config import hostname
    if USING_SUPERVISOR:
        to_delete = set()
        for host in Supervisors.query.all():
            if host.hostname == hostname:
                continue
            try:
                socket.gethostbyname(host.hostname)
                server = xmlrpclib.Server(host.url + '/RPC2')
                result = server.supervisor.getState()
            except:
                to_delete.add(host.id)
        for id_to_delete in to_delete:
            Supervisors.query.filter_by(id=id_to_delete).delete()

def check_for_updates():
    logmessage("check_for_update: starting")
    from docassemble.base.config import hostname
    ok = True
    here_already = dict()
    installed_packages = get_installed_distributions()
    for package in installed_packages:
        here_already[package.key] = package.version
    packages = dict()
    installs = dict()
    to_install = list()
    to_uninstall = list()
    uninstalled_packages = dict()
    logmessages = ''
    package_by_name = dict()
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        if package.name in package_by_name:
            continue
        package_by_name[package.name] = package
    to_cull = list()
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        if package.id != package_by_name[package.name].id:
            to_cull.append(package.id)
    if len(to_cull):
        for pid in to_cull:
            Package.query.filter_by(id=pid).delete()
        db.session.commit()
    # packages is what is supposed to be installed
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        if package.type is not None:
            packages[package.id] = package
            #print "Found a package " + package.name
    for package in Package.query.filter_by(active=False).all():
        uninstalled_packages[package.id] = package # this is what the database says should be uninstalled
    for install in Install.query.filter_by(hostname=hostname).all():
        installs[install.package_id] = install # this is what the database says in installed on this server
        if install.package_id in uninstalled_packages:
            to_uninstall.append(uninstalled_packages[install.package_id]) # uninstall if it is installed
    changed = False
    package_owner = dict()
    for auth in PackageAuth.query.filter_by(authtype='owner').all():
        package_owner[auth.package_id] = auth.user_id
    for package in packages.itervalues():
        if package.id not in installs and package.name in here_already:
            logmessage("Package " + package.name + " here already")
            install = Install(hostname=hostname, packageversion=here_already[package.name], version=package.version, package_id=package.id)
            db.session.add(install)
            installs[package.id] = install
            changed = True
    if changed:
        db.session.commit()
    for package in packages.itervalues():
        #logmessage("Processing package id " + str(package.id))
        #logmessage("1: " + str(installs[package.id].packageversion) + " 2: " + str(package.packageversion))
        if (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is None) or (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is not None and LooseVersion(package.packageversion) > LooseVersion(installs[package.id].packageversion)):
            new_version_needed = True
        else:
            new_version_needed = False
        #logmessage("got here and new version is " + str(new_version_needed))
        if package.id not in installs or package.version > installs[package.id].version or new_version_needed:
            to_install.append(package)
    #logmessage("done with that")
    for package in to_uninstall:
        #logmessage("Going to uninstall a package")
        returnval, newlog = uninstall_package(package)
        logmessages += newlog
        if returnval == 0:
            Install.query.filter_by(hostname=hostname, package_id=package.id).delete()
        else:
            ok = False
    for package in to_install:
        #logmessage("Going to install a package")
        returnval, newlog = install_package(package)
        logmessages += newlog
        if returnval == 0:
            if package.id in installs:
                install = installs[package.id]
                install.version = package.version
            else:
                install = Install(hostname=hostname, packageversion=package.packageversion, version=package.version, package_id=package.id)
                db.session.add(install)
            db.session.commit()
            update_versions()
            add_dependencies(package_owner.get(package.id, 1))
            update_versions()
        else:
            ok = False
    db.session.commit()
    #logmessage("check_for_update: finished uninstalling and installing")
    return ok, logmessages

def update_versions():
    logmessage("update_versions")
    install_by_id = dict()
    from docassemble.base.config import hostname
    for install in Install.query.filter_by(hostname=hostname).all():
        install_by_id[install.package_id] = install
    package_by_name = dict()
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        if package.name in package_by_name:
            continue
        package_by_name[package.name] = package
    installed_packages = get_installed_distributions()
    for package in installed_packages:
        if package.key in package_by_name:
            if package_by_name[package.key].id in install_by_id and package.version != install_by_id[package_by_name[package.key].id].packageversion:
                install_by_id[package_by_name[package.key].id].packageversion = package.version
                db.session.commit()
            if package.version != package_by_name[package.key].packageversion:
                package_by_name[package.key].packageversion = package.version
                db.session.commit()
    return

def add_dependencies(user_id):
    logmessage('add_dependencies: ' + str(user_id))
    from docassemble.base.config import hostname
    package_by_name = dict()
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        if package.name in package_by_name:
            continue
        package_by_name[package.name] = package
    installed_packages = get_installed_distributions()
    for package in installed_packages:
        if package.key in package_by_name:
            continue
        package_auth = PackageAuth(user_id=user_id)
        if package.key in ['docassemble', 'docassemble.base', 'docassemble.webapp', 'docassemble.demo']:
            package_entry = Package(name=package.key, package_auth=package_auth, giturl=docassemble_git_url, packageversion=package.version, gitsubdir=re.sub(r'\.', '-', package.key), type='git', core=True)
        else:
            package_entry = Package(name=package.key, package_auth=package_auth, type='pip', packageversion=package.version, dependency=True)
        db.session.add(package_auth)
        db.session.add(package_entry)
        db.session.commit()
        install = Install(hostname=hostname, packageversion=package_entry.packageversion, version=package_entry.version, package_id=package_entry.id)
        db.session.add(install)
        db.session.commit()
    return

def install_package(package):
    if package.type == 'zip' and package.upload is None:
        return 0, ''
    logmessage('install_package: ' + package.name)
    logfilecontents = ''
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    pip_log = tempfile.NamedTemporaryFile()
    if package.type == 'zip' and package.upload is not None:
        saved_file = SavedFile(package.upload, extension='zip', fix=True)
        commands = ['install', '--egg', '--no-index', '--quiet', '--src=' + tempfile.mkdtemp(), '--log-file=' + pip_log.name, '--upgrade', saved_file.path + '.zip']
    elif package.type == 'git' and package.giturl is not None:
        commands = ['install', '--egg', '--quiet', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + package.giturl + '.git#egg=' + package.name]
    elif package.type == 'pip':
        if package.limitation is None:
            limit = ""
        else:
            limit = str(package.limitation)
        commands = ['install', '--quiet', '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, package.name + limit]
    else:
        return 1, 'Unable to recognize package type: ' + package.name
    logmessage("Running pip " + " ".join(commands))
    logfilecontents += "Running pip " + " ".join(commands) + "\n"
    returnval = pip.main(commands)
    with open(pip_log.name) as x:
        logfilecontents += x.read()
    logmessage(logfilecontents)
    logmessage('install_package: done')
    return returnval, logfilecontents

def uninstall_package(package):
    logmessage('uninstall_package: ' + package.name)
    logfilecontents = ''
    #sys.stderr.write("uninstall_package: uninstalling " + package.name + "\n")
    #return 0
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    pip_log = tempfile.NamedTemporaryFile()
    commands = ['uninstall', '-y', '--log-file=' + pip_log.name, package.name]
    logmessage("Running pip " + " ".join(commands))
    logfilecontents += "Running pip " + " ".join(commands) + "\n"
    returnval = pip.main(commands)
    logmessage('Finished running pip')
    with open(pip_log.name) as x:
        logfilecontents += x.read()
    logmessage(logfilecontents)
    logmessage('uninstall_package: done')
    return returnval, logfilecontents

class Object(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    pass

def get_installed_distributions():
    from docassemble.base.config import daconfig
    PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local')
    results = list()
    output, err = subprocess.Popen([daconfig.get('pip', os.path.join(PACKAGE_DIRECTORY, 'bin', 'pip')), 'freeze'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    for line in output.split('\n'):
        a = line.split("==")
        if len(a) == 2:
            results.append(Object(key=a[0].lower(), version=a[1]))
        #else:
            #logmessage("Did not understand line: " + str(line))
    return results

if __name__ == "__main__":
    import docassemble.webapp.database
    app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
    check_for_updates()
    remove_inactive_hosts()
    from docassemble.base.config import daconfig
    logmessage("update: touched wsgi file")
    wsgi_file = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
    if os.path.isfile(wsgi_file):
        with open(wsgi_file, 'a'):
            os.utime(wsgi_file, None)
    db.engine.dispose()
    sys.exit(0)
