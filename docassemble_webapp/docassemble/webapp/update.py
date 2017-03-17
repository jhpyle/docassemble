import os
import sys
import pip.utils.logging
import pip
import socket
import tempfile
import threading
import subprocess
import xmlrpclib
import re
from cStringIO import StringIO
import sys

from distutils.version import LooseVersion
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
from docassemble.webapp.app_object import app
from docassemble.webapp.db_object import db
from docassemble.webapp.packages.models import Package, Install, PackageAuth
from docassemble.webapp.core.models import Supervisors
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
    sys.stderr.write("check_for_updates: starting\n")
    from docassemble.base.config import hostname
    ok = True
    here_already = dict()
    results = dict()
    installed_packages = get_installed_distributions()
    for package in installed_packages:
        here_already[package.key] = package.version
    packages = dict()
    installs = dict()
    to_install = list()
    to_uninstall = list()
    uninstall_done = dict()
    uninstalled_packages = dict()
    logmessages = ''
    package_by_name = dict()
    for package in Package.query.filter_by(active=True).all():
        package_by_name[package.name] = package
    # packages is what is supposed to be installed
    for package in Package.query.filter_by(active=True).all():
        if package.type is not None:
            packages[package.id] = package
            #print "Found a package " + package.name
    for package in Package.query.filter_by(active=False).all():
        if package.name not in package_by_name:
            uninstalled_packages[package.id] = package # this is what the database says should be uninstalled
    for install in Install.query.filter_by(hostname=hostname).all():
        installs[install.package_id] = install # this is what the database says in installed on this server
        if install.package_id in uninstalled_packages and uninstalled_packages[install.package_id].name not in package_by_name:
            to_uninstall.append(uninstalled_packages[install.package_id]) # uninstall if it is installed
    changed = False
    package_owner = dict()
    for auth in PackageAuth.query.filter_by(authtype='owner').all():
        package_owner[auth.package_id] = auth.user_id
    for package in packages.itervalues():
        if package.id not in installs and package.name in here_already:
            sys.stderr.write("check_for_updates: package " + package.name + " here already\n")
            install = Install(hostname=hostname, packageversion=here_already[package.name], version=package.version, package_id=package.id)
            db.session.add(install)
            installs[package.id] = install
            changed = True
    if changed:
        db.session.commit()
    for package in packages.itervalues():
        #sys.stderr.write("check_for_updates: processing package id " + str(package.id) + "\n")
        #sys.stderr.write("1: " + str(installs[package.id].packageversion) + " 2: " + str(package.packageversion) + "\n")
        if (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is None) or (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is not None and LooseVersion(package.packageversion) > LooseVersion(installs[package.id].packageversion)):
            new_version_needed = True
        else:
            new_version_needed = False
        #sys.stderr.write("got here and new version is " + str(new_version_needed) + "\n")
        if package.id not in installs or package.version > installs[package.id].version or new_version_needed:
            to_install.append(package)
    #sys.stderr.write("done with that" + "\n")
    for package in to_uninstall:
        #sys.stderr.write("Going to uninstall a package: " + package.name + "\n")
        if package.name in uninstall_done:
            sys.stderr.write("check_for_updates: skipping uninstallation of " + str(package.name) + " because already uninstalled" + "\n")
            continue
        returnval, newlog = uninstall_package(package)
        uninstall_done[package.name] = 1
        logmessages += newlog
        if returnval == 0:
            Install.query.filter_by(hostname=hostname, package_id=package.id).delete()
            results[package.name] = 'successfully uninstalled'
        else:
            results[package.name] = 'uninstall failed'
            ok = False
    packages_to_delete = list()
    for package in to_install:
        sys.stderr.write("check_for_updates: going to install a package: " + package.name + "\n")
        returnval, newlog = install_package(package)
        logmessages += newlog
        sys.stderr.write("check_for_updates: return value was " + str(returnval) + "\n")
        if returnval != 0:
            sys.stderr.write("Return value was not good" + "\n")
            ok = False
        pip._vendor.pkg_resources._initialize_master_working_set()
        real_name = get_real_name(package.name)
        sys.stderr.write("check_for_updates: real name of package " + str(package.name) + " is " + str(real_name) + "\n")
        if real_name is None:
            results[package.name] = 'install failed'
            if package.name not in here_already:
                sys.stderr.write("check_for_updates: removing package entry for " + package.name + "\n")
                packages_to_delete.append(package)
        else:
            results[package.name] = 'successfully installed'
            if real_name != package.name:
                sys.stderr.write("check_for_updates: changing name" + "\n")
                package.name = real_name
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
    for package in packages_to_delete:
        package.active = False
    db.session.commit()
    sys.stderr.write("check_for_updates: finished uninstalling and installing" + "\n")
    return ok, logmessages, results

def update_versions():
    sys.stderr.write("update_versions: starting" + "\n")
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
    #sys.stderr.write('add_dependencies: user_id is ' + str(user_id) + "\n")
    from docassemble.base.config import hostname, daconfig
    docassemble_git_url = daconfig.get('docassemble git url', 'https://github.com/jhpyle/docassemble')
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

def fix_names():
    installed_packages = [package.key for package in get_installed_distributions()]
    for package in Package.query.filter_by(active=True).all():
        if package.name not in installed_packages:
            actual_name = get_real_name(package.name)
            if actual_name is not None:
                package.name = actual_name
                db.session.commit()
            else:
                sys.stderr.write("fix_names: package " + package.name + " does not appear to be installed" + "\n")

def install_package(package):
    if package.type == 'zip' and package.upload is None:
        return 0, ''
    sys.stderr.write('install_package: ' + package.name + "\n")
    from docassemble.base.config import daconfig
    PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local')
    logfilecontents = ''
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    pip_log = tempfile.NamedTemporaryFile()
    if package.type == 'zip' and package.upload is not None:
        saved_file = SavedFile(package.upload, extension='zip', fix=True)
        commands = ['install', '--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + tempfile.mkdtemp(), '--log-file=' + pip_log.name, '--upgrade', saved_file.path + '.zip']
    elif package.type == 'git' and package.giturl is not None:
        commands = ['install', '--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, 'git+' + package.giturl + '.git#egg=' + package.name]
    elif package.type == 'pip':
        if package.limitation is None:
            limit = ""
        else:
            limit = str(package.limitation)
        commands = ['install', '--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + tempfile.mkdtemp(), '--upgrade', '--log-file=' + pip_log.name, package.name + limit]
    else:
        return 1, 'Unable to recognize package type: ' + package.name
    #sys.stderr.write("install_package: running pip " + " ".join(commands) + "\n")
    logfilecontents += "pip " + " ".join(commands) + "\n"
    returnval = pip.main(commands)
    with open(pip_log.name, 'rU') as x:
        logfilecontents += x.read().decode('utf8')
    sys.stderr.write(logfilecontents + "\n")
    sys.stderr.write('install_package: done' + "\n")
    return returnval, logfilecontents

def uninstall_package(package):
    sys.stderr.write('uninstall_package: ' + package.name + "\n")
    logfilecontents = ''
    #sys.stderr.write("uninstall_package: uninstalling " + package.name + "\n")
    #return 0
    pip.utils.logging._log_state = threading.local()
    pip.utils.logging._log_state.indentation = 0
    pip_log = tempfile.NamedTemporaryFile()
    commands = ['uninstall', '-y', '--log-file=' + pip_log.name, package.name]
    #sys.stderr.write("Running pip " + " ".join(commands) + "\n")
    logfilecontents += "pip " + " ".join(commands) + "\n"
    returnval = pip.main(commands)
    #sys.stderr.write('Finished running pip' + "\n")
    with open(pip_log.name, 'rU') as x:
        logfilecontents += x.read().decode('utf8')
    sys.stderr.write(logfilecontents + "\n")
    sys.stderr.write('uninstall_package: done' + "\n")
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
    old_stdout = sys.stdout
    sys.stdout = saved_stdout = StringIO()
    pip.main(['freeze'])
    sys.stdout = old_stdout
    output = saved_stdout.getvalue()
    for line in output.split('\n'):
        a = line.split("==")
        if len(a) == 2:
            results.append(Object(key=a[0], version=a[1]))
    return results

def get_real_name(package_name):
    old_stdout = sys.stdout
    sys.stdout = saved_stdout = StringIO()
    pip.main(['show', package_name])
    sys.stdout = old_stdout
    output = saved_stdout.getvalue()
    for line in output.split('\n'):
        a = line.split(": ")
        if len(a) == 2 and a[0] == 'Name':
            return a[1]
    return None

if __name__ == "__main__":
    #import docassemble.webapp.database
    with app.app_context():
        #app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
        any_package = Package.query.filter_by(active=True).first()
        if any_package is None:
            add_dependencies(1)
        check_for_updates()
        remove_inactive_hosts()
        from docassemble.base.config import daconfig
        sys.stderr.write("update: touched wsgi file" + "\n")
        wsgi_file = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
        if os.path.isfile(wsgi_file):
            with open(wsgi_file, 'a'):
                os.utime(wsgi_file, None)
        db.engine.dispose()
    sys.exit(0)
