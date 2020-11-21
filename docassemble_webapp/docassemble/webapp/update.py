import os
import sys
import socket
import tempfile
import subprocess
import xmlrpc.client
import re
#from io import StringIO
import sys
import shutil
import time
import fcntl

from distutils.version import LooseVersion
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)
    if 'initialize' in sys.argv:
        mode = 'initialize'
    elif 'check_for_updates' in sys.argv:
        mode = 'check_for_updates'
    else:
        mode = 'initialize'

supervisor_url = os.environ.get('SUPERVISOR_SERVER_URL', None)
if supervisor_url:
    USING_SUPERVISOR = True
else:
    USING_SUPERVISOR = False

def fix_fnctl():
    try:
        flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL);
        fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags&~os.O_NONBLOCK);
        sys.stderr.write("fix_fnctl: updated stdout\n")
    except:
        pass
    try:
        flags = fcntl.fcntl(sys.stderr, fcntl.F_GETFL);
        fcntl.fcntl(sys.stderr, fcntl.F_SETFL, flags&~os.O_NONBLOCK);
        sys.stderr.write("fix_fnctl: updated stderr\n")
    except:
        pass

def remove_inactive_hosts():
    start_time = time.time()
    sys.stderr.write("remove_inactive_hosts: starting\n")
    if USING_SUPERVISOR:
        from docassemble.base.config import hostname
        from docassemble.webapp.app_object import app
        from docassemble.webapp.db_object import db
        from docassemble.webapp.core.models import Supervisors
        to_delete = set()
        for host in Supervisors.query.all():
            if host.hostname == hostname:
                continue
            try:
                socket.gethostbyname(host.hostname)
                server = xmlrpc.client.Server(host.url + '/RPC2')
                result = server.supervisor.getState()
            except:
                to_delete.add(host.id)
        for id_to_delete in to_delete:
            Supervisors.query.filter_by(id=id_to_delete).delete()
    sys.stderr.write("remove_inactive_hosts: ended after " + str(time.time() - start_time) + " seconds\n")

class DummyPackage(object):
    def __init__(self, name):
        self.name = name
        self.type = 'pip'
        self.limitation = None

def check_for_updates(doing_startup=False):
    start_time = time.time()
    sys.stderr.write("check_for_updates: starting\n")
    from docassemble.base.config import hostname
    from docassemble.webapp.app_object import app
    from docassemble.webapp.db_object import db
    from docassemble.webapp.packages.models import Package, Install, PackageAuth
    ok = True
    here_already = dict()
    results = dict()
    sys.stderr.write("check_for_updates: 0.5 after " + str(time.time() - start_time) + " seconds\n")

    num_deleted = Package.query.filter_by(name='psycopg2').delete()
    if num_deleted > 0:
        db.session.commit()
    num_deleted = Package.query.filter_by(name='pdfminer').delete()
    if num_deleted > 0:
        db.session.commit()
    num_deleted = Package.query.filter_by(name='pdfminer3k').delete()
    if num_deleted > 0:
        db.session.commit()
    num_deleted = Package.query.filter_by(name='py-bcrypt').delete()
    if num_deleted > 0:
        db.session.commit()
    num_deleted = Package.query.filter_by(name='pycrypto').delete()
    if num_deleted > 0:
        db.session.commit()
    num_deleted = Package.query.filter_by(name='constraint').delete()
    if num_deleted > 0:
        db.session.commit()
    num_deleted = Package.query.filter_by(name='distutils2').delete()
    if num_deleted > 0:
        db.session.commit()
    sys.stderr.write("check_for_updates: 1 after " + str(time.time() - start_time) + " seconds\n")
    installed_packages = get_installed_distributions()
    for package in installed_packages:
        here_already[package.key] = package.version
    changed = False
    if 'psycopg2' in here_already:
        sys.stderr.write("check_for_updates: uninstalling psycopg2\n")
        uninstall_package(DummyPackage('psycopg2'))
        if 'psycopg2-binary' in here_already:
            sys.stderr.write("check_for_updates: reinstalling psycopg2-binary\n")
            uninstall_package(DummyPackage('psycopg2-binary'))
            install_package(DummyPackage('psycopg2-binary'))
        changed = True
    if 'psycopg2-binary' not in here_already:
        sys.stderr.write("check_for_updates: installing psycopg2-binary\n")
        install_package(DummyPackage('psycopg2-binary'))
        change = True
    if 'kombu' not in here_already or LooseVersion(here_already['kombu']) <= LooseVersion('4.1.0'):
        sys.stderr.write("check_for_updates: installing new kombu version\n")
        install_package(DummyPackage('kombu'))
        changed = True
    if 'celery' not in here_already or LooseVersion(here_already['celery']) <= LooseVersion('4.1.0'):
        sys.stderr.write("check_for_updates: installing new celery version\n")
        install_package(DummyPackage('celery'))
        changed = True
    if 'pycrypto' in here_already:
        sys.stderr.write("check_for_updates: uninstalling pycrypto\n")
        uninstall_package(DummyPackage('pycrypto'))
        if 'pycryptodome' in here_already:
            sys.stderr.write("check_for_updates: reinstalling pycryptodome\n")
            uninstall_package(DummyPackage('pycryptodome'))
            install_package(DummyPackage('pycryptodome'))
        changed = True
    if 'pycryptodome' not in here_already:
        sys.stderr.write("check_for_updates: installing pycryptodome\n")
        install_package(DummyPackage('pycryptodome'))
        changed = True
    if 'pdfminer' in here_already:
        sys.stderr.write("check_for_updates: uninstalling pdfminer\n")
        uninstall_package(DummyPackage('pdfminer'))
        changed = True
    if 'pdfminer3k' in here_already:
        sys.stderr.write("check_for_updates: uninstalling pdfminer3k\n")
        uninstall_package(DummyPackage('pdfminer3k'))
        changed = True
    if 'pdfminer.six' in here_already:
        try:
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
        except:
            sys.stderr.write("check_for_updates: reinstalling pdfminer.six\n")
            uninstall_package(DummyPackage('pdfminer.six'))
            install_package(DummyPackage('pdfminer.six'))
    else:
        sys.stderr.write("check_for_updates: installing pdfminer.six\n")
        install_package(DummyPackage('pdfminer.six'))
        changed = True
    if 'py-bcrypt' in here_already:
        sys.stderr.write("check_for_updates: uninstalling py-bcrypt\n")
        uninstall_package(DummyPackage('py-bcrypt'))
        changed = True
        if 'bcrypt' in here_already:
            sys.stderr.write("check_for_updates: reinstalling bcrypt\n")
            uninstall_package(DummyPackage('bcrypt'))
            install_package(DummyPackage('bcrypt'))
            changed = True
    if 'bcrypt' not in here_already:
        sys.stderr.write("check_for_updates: installing bcrypt\n")
        install_package(DummyPackage('bcrypt'))
        changed = True
    if changed:
        installed_packages = get_installed_distributions()
        here_already = dict()
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
    sys.stderr.write("check_for_updates: 2 after " + str(time.time() - start_time) + " seconds\n")
    for package in Package.query.filter_by(active=True).all():
        package_by_name[package.name] = package
        #sys.stderr.write("check_for_updates: database includes a package called " + package.name + " after " + str(time.time() - start_time) + " seconds\n")
    # packages is what is supposed to be installed
    sys.stderr.write("check_for_updates: 3 after " + str(time.time() - start_time) + " seconds\n")
    for package in Package.query.filter_by(active=True).all():
        if package.type is not None:
            packages[package.id] = package
            #sys.stderr.write("check_for_updates: database includes a package called " + package.name + " that has a type after " + str(time.time() - start_time) + " seconds\n")
            #print("Found a package " + package.name)
    sys.stderr.write("check_for_updates: 4 after " + str(time.time() - start_time) + " seconds\n")
    for package in Package.query.filter_by(active=False).all():
        if package.name not in package_by_name:
            #sys.stderr.write("check_for_updates: database says " + package.name + " should be uninstalled after " + str(time.time() - start_time) + " seconds\n")
            uninstalled_packages[package.id] = package # this is what the database says should be uninstalled
    sys.stderr.write("check_for_updates: 5 after " + str(time.time() - start_time) + " seconds\n")
    for install in Install.query.filter_by(hostname=hostname).all():
        installs[install.package_id] = install # this is what the database says in installed on this server
        if install.package_id in uninstalled_packages and uninstalled_packages[install.package_id].name not in package_by_name:
            sys.stderr.write("check_for_updates: " + uninstalled_packages[install.package_id].name + " will be uninstalled after " + str(time.time() - start_time) + " seconds\n")
            to_uninstall.append(uninstalled_packages[install.package_id]) # uninstall if it is installed
    changed = False
    package_owner = dict()
    sys.stderr.write("check_for_updates: 6 after " + str(time.time() - start_time) + " seconds\n")
    for auth in PackageAuth.query.filter_by(authtype='owner').all():
        package_owner[auth.package_id] = auth.user_id
    sys.stderr.write("check_for_updates: 7 after " + str(time.time() - start_time) + " seconds\n")
    for package in packages.values():
        if package.id not in installs and package.name in here_already:
            sys.stderr.write("check_for_updates: package " + package.name + " here already.  Writing an Install record for it.\n")
            install = Install(hostname=hostname, packageversion=here_already[package.name], version=package.version, package_id=package.id)
            db.session.add(install)
            installs[package.id] = install
            changed = True
    if changed:
        db.session.commit()
    sys.stderr.write("check_for_updates: 8 after " + str(time.time() - start_time) + " seconds\n")
    for package in packages.values():
        #sys.stderr.write("check_for_updates: processing package id " + str(package.id) + "\n")
        #sys.stderr.write("1: " + str(installs[package.id].packageversion) + " 2: " + str(package.packageversion) + "\n")
        if (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is None) or (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is not None and LooseVersion(package.packageversion) > LooseVersion(installs[package.id].packageversion)):
            sys.stderr.write("check_for_updates: a new version of " + package.name + " is needed because the necessary package version, " + str(package.packageversion) + ", is ahead of the installed version, " + str(installs[package.id].packageversion) + " after " + str(time.time() - start_time) + " seconds\n")
            new_version_needed = True
        else:
            new_version_needed = False
        #sys.stderr.write("got here and new version is " + str(new_version_needed) + "\n")
        # Check for missing local packages
        if (package.name not in here_already) and (package.id in installs):
            sys.stderr.write("check_for_updates: the package " + package.name + " is supposed to be installed on this server, but was not detected after " + str(time.time() - start_time) + " seconds\n")
            package_missing = True
        else:
            package_missing = False
        if package.id in installs and package.version > installs[package.id].version:
            sys.stderr.write("check_for_updates: the package " + package.name + " has internal version " + str(package.version) + " but the installed version has version " + str(installs[package.id].version) + " after " + str(time.time() - start_time) + " seconds\n")
            package_version_greater = True
        else:
            package_version_greater = False
        if package.id not in installs:
            sys.stderr.write("check_for_updates: the package " + package.name + " is not in the table of installed packages for this server after " + str(time.time() - start_time) + " seconds\n")
        if package.id not in installs or package_version_greater or new_version_needed or package_missing:
            to_install.append(package)
    #sys.stderr.write("done with that" + "\n")
    sys.stderr.write("check_for_updates: 9 after " + str(time.time() - start_time) + " seconds\n")
    for package in to_uninstall:
        #sys.stderr.write("Going to uninstall a package: " + package.name + "\n")
        if package.name in uninstall_done:
            sys.stderr.write("check_for_updates: skipping uninstallation of " + str(package.name) + " because already uninstalled after " + str(time.time() - start_time) + " seconds" + "\n")
            continue
        if package.name not in here_already:
            sys.stderr.write("check_for_updates: skipping uninstallation of " + str(package.name) + " because not installed" + " after " + str(time.time() - start_time) + " seconds\n")
            returnval = 1
            newlog = ''
        else:
            returnval, newlog = uninstall_package(package)
        uninstall_done[package.name] = 1
        logmessages += newlog
        if returnval == 0:
            Install.query.filter_by(hostname=hostname, package_id=package.id).delete()
            results[package.name] = 'pip uninstall command returned success code.  See log for details.'
        elif returnval == 1:
            Install.query.filter_by(hostname=hostname, package_id=package.id).delete()
            results[package.name] = 'pip uninstall was not run because the package was not installed.'
        else:
            results[package.name] = 'pip uninstall command returned failure code'
            ok = False
    packages_to_delete = list()
    sys.stderr.write("check_for_updates: 10 after " + str(time.time() - start_time) + " seconds\n")
    for package in to_install:
        sys.stderr.write("check_for_updates: going to install a package: " + package.name + "after " + str(time.time() - start_time) + " seconds\n")
        # if doing_startup and package.name.startswith('docassemble') and package.name in here_already:
        #     #adding this because of unpredictability of installing new versions of docassemble
        #     #just because of a system restart.
        #     sys.stderr.write("check_for_updates: skipping update on " + str(package.name) + "\n")
        #     continue
        returnval, newlog = install_package(package)
        logmessages += newlog
        sys.stderr.write("check_for_updates: return value was " + str(returnval) + " after " + str(time.time() - start_time) + " seconds\n")
        if returnval != 0:
            sys.stderr.write("Return value was not good" + " after " + str(time.time() - start_time) + " seconds\n")
            ok = False
        #pip._vendor.pkg_resources._initialize_master_working_set()
        pip_info = get_pip_info(package.name)
        real_name = pip_info['Name']
        sys.stderr.write("check_for_updates: real name of package " + str(package.name) + " is " + str(real_name) + "\n after " + str(time.time() - start_time) + " seconds")
        if real_name is None:
            results[package.name] = 'install failed'
            ok = False
            if package.name not in here_already:
                sys.stderr.write("check_for_updates: removing package entry for " + package.name + " after " + str(time.time() - start_time) + " seconds\n")
                packages_to_delete.append(package)
        elif returnval != 0:
            results[package.name] = 'pip install command returned failure code'
        else:
            results[package.name] = 'pip install command returned success code.  See log for details.'
            if real_name != package.name:
                sys.stderr.write("check_for_updates: changing name" + " after " + str(time.time() - start_time) + " seconds\n")
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
    sys.stderr.write("check_for_updates: 11 after " + str(time.time() - start_time) + " seconds\n")
    for package in packages_to_delete:
        db.session.delete(package)
    sys.stderr.write("check_for_updates: 12 after " + str(time.time() - start_time) + " seconds\n")
    db.session.commit()
    sys.stderr.write("check_for_updates: finished uninstalling and installing after " + str(time.time() - start_time) + " seconds\n")
    return ok, logmessages, results

def update_versions():
    start_time = time.time()
    sys.stderr.write("update_versions: starting" + "\n")
    from docassemble.base.config import hostname
    from docassemble.webapp.app_object import app
    from docassemble.webapp.db_object import db
    from docassemble.webapp.packages.models import Package, Install, PackageAuth
    from docassemble.webapp.daredis import r
    install_by_id = dict()
    for install in Install.query.filter_by(hostname=hostname).all():
        install_by_id[install.package_id] = install
    package_by_name = dict()
    for package in Package.query.filter_by(active=True).order_by(Package.name, Package.id.desc()).all():
        if package.name in package_by_name:
            continue
        package_by_name[package.name] = Object(id=package.id, packageversion=package.packageversion, name=package.name)
    installed_packages = get_installed_distributions()
    for package in installed_packages:
        if package.key in package_by_name:
            if package_by_name[package.key].id in install_by_id and package.version != install_by_id[package_by_name[package.key].id].packageversion:
                install_row = Install.query.filter_by(hostname=hostname, package_id=package_by_name[package.key].id).first()
                install_row.packageversion = package.version
            if package.version != package_by_name[package.key].packageversion:
                package_row = Package.query.filter_by(active=True, name=package_by_name[package.key].name).with_for_update().first()
                package_row.packageversion = package.version
    db.session.commit()
    sys.stderr.write("update_versions: ended after " + str(time.time() - start_time) + "\n")
    return

def get_home_page_dict():
    from docassemble.base.config import daconfig
    PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))
    FULL_PACKAGE_DIRECTORY = os.path.join(PACKAGE_DIRECTORY, 'lib', 'python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor), 'site-packages')
    home_page = dict()
    for d in os.listdir(FULL_PACKAGE_DIRECTORY):
        if not d.startswith('docassemble.'):
            continue
        metadata_path = os.path.join(d, 'METADATA')
        if os.path.isfile(metadata_path):
            name = None
            url = None
            with open(metadata_path, 'rU', encoding='utf-8') as fp:
                for line in fp:
                    if line.startswith('Name: '):
                        name = line[6:]
                    elif line.startswith('Home-page: '):
                        url = line[11:]
                        break
            if name:
                home_page[name.lower()] = url
    return home_page

def add_dependencies(user_id):
    start_time = time.time()
    #sys.stderr.write('add_dependencies: user_id is ' + str(user_id) + "\n")
    sys.stderr.write("add_dependencies: starting\n")
    from docassemble.base.config import hostname
    from docassemble.webapp.app_object import app
    from docassemble.webapp.db_object import db
    from docassemble.webapp.packages.models import Package, Install, PackageAuth
    packages_known = set()
    for package in Package.query.filter_by(active=True).all():
        packages_known.add(package.name)
    installed_packages = get_installed_distributions()
    home_pages = None
    packages_to_add = list()
    for package in installed_packages:
        if package.key in packages_known:
            continue
        if package.key.startswith('mysqlclient') or package.key.startswith('mysql-connector') or package.key.startswith('MySQL-python'):
            continue
        Package.query.filter_by(name=package.key).delete()
        packages_to_add.append(package)
    if len(packages_to_add):
        db.session.commit()
        for package in packages_to_add:
            package_auth = PackageAuth(user_id=user_id)
            if package.key.startswith('docassemble.'):
                if home_pages is None:
                    home_pages = get_home_page_dict()
                home_page = home_pages.get(package.key.lower(), None)
                if home_page is not None and re.search(r'/github.com/', home_page):
                    package_entry = Package(name=package.key, package_auth=package_auth, type='git', giturl=home_page, packageversion=package.version, dependency=True)
                else:
                    package_entry = Package(name=package.key, package_auth=package_auth, type='pip', packageversion=package.version, dependency=True)
            else:
                package_entry = Package(name=package.key, package_auth=package_auth, type='pip', packageversion=package.version, dependency=True)
            db.session.add(package_entry)
            db.session.commit()
            install = Install(hostname=hostname, packageversion=package_entry.packageversion, version=package_entry.version, package_id=package_entry.id)
            db.session.add(install)
            db.session.commit()
    sys.stderr.write("add_dependencies: ending after " + str(time.time() - start_time) + " seconds\n")
    return

def fix_names():
    from docassemble.webapp.app_object import app
    from docassemble.webapp.db_object import db
    from docassemble.webapp.packages.models import Package, Install, PackageAuth
    installed_packages = [package.key for package in get_installed_distributions()]
    for package in Package.query.filter_by(active=True).with_for_update().all():
        if package.name not in installed_packages:
            pip_info = get_pip_info(package.name)
            actual_name = pip_info['Name']
            if actual_name is not None:
                package.name = actual_name
            else:
                sys.stderr.write("fix_names: package " + package.name + " does not appear to be installed" + "\n")
    db.session.commit()

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def install_package(package):
    sys.stderr.write("install_package: " + package.name + "\n")
    if package.type == 'zip' and package.upload is None:
        return 0, ''
    sys.stderr.write('install_package: ' + package.name + "\n")
    from docassemble.base.config import daconfig
    from docassemble.webapp.daredis import r
    from docassemble.webapp.files import SavedFile
    PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))
    logfilecontents = ''
    pip_log = tempfile.NamedTemporaryFile()
    temp_dir = tempfile.mkdtemp()
    #use_pip_cache = r.get('da:updatepackage:use_pip_cache')
    #if use_pip_cache is None:
    #    disable_pip_cache = False
    #elif int(use_pip_cache):
    #    disable_pip_cache = False
    #else:
    #    disable_pip_cache = True
    disable_pip_cache = True
    if package.type == 'zip' and package.upload is not None:
        saved_file = SavedFile(package.upload, extension='zip', fix=True)
        commands = ['pip', 'install']
        if disable_pip_cache:
            commands.append('--no-cache-dir')
        commands.extend(['--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + temp_dir, '--log-file=' + pip_log.name, '--upgrade', saved_file.path + '.zip'])
    elif package.type == 'git' and package.giturl is not None:
        if package.gitbranch is not None:
            branchpart = '@' + str(package.gitbranch)
        else:
            branchpart = ''
        if package.gitsubdir is not None:
            commands = ['pip', 'install']
            if disable_pip_cache:
                commands.append('--no-cache-dir')
            commands.extend(['--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + temp_dir, '--upgrade', '--log-file=' + pip_log.name, 'git+' + str(package.giturl) + '.git' + branchpart + '#egg=' + package.name + '&subdirectory=' + str(package.gitsubdir)])
        else:
            commands = ['pip', 'install']
            if disable_pip_cache:
                commands.append('--no-cache-dir')
            commands.extend(['--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + temp_dir, '--upgrade', '--log-file=' + pip_log.name, 'git+' + str(package.giturl) + '.git' + branchpart + '#egg=' + package.name])
    elif package.type == 'pip':
        if package.limitation is None:
            limit = ""
        else:
            limit = str(package.limitation)
        commands = ['pip', 'install']
        if disable_pip_cache:
            commands.append('--no-cache-dir')
        commands.extend(['--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + temp_dir, '--upgrade', '--log-file=' + pip_log.name, package.name + limit])
    else:
        sys.stderr.write("Wrong package type\n")
        return 1, 'Unable to recognize package type: ' + package.name
    sys.stderr.write("install_package: running " + " ".join(commands) + "\n")
    logfilecontents += " ".join(commands) + "\n"
    returnval = 1
    try:
        subprocess.run(commands)
        returnval = 0
    except subprocess.CalledProcessError as err:
        returnval = err.returncode
    fix_fnctl()
    sys.stderr.flush()
    sys.stdout.flush()
    time.sleep(4)
    with open(pip_log.name, 'rU', encoding='utf-8') as x:
        logfilecontents += x.read()
    pip_log.close()
    try:
        sys.stderr.write(logfilecontents + "\n")
    except:
        pass
    sys.stderr.flush()
    sys.stdout.flush()
    time.sleep(4)
    sys.stderr.write('returnval is: ' + str(returnval) + "\n")
    sys.stderr.write('install_package: done' + "\n")
    shutil.rmtree(temp_dir)
    return returnval, logfilecontents

def uninstall_package(package):
    sys.stderr.write('uninstall_package: ' + package.name + "\n")
    logfilecontents = ''
    #sys.stderr.write("uninstall_package: uninstalling " + package.name + "\n")
    pip_log = tempfile.NamedTemporaryFile()
    commands = ['pip', 'uninstall', '--yes', '--log-file=' + pip_log.name, package.name]
    sys.stderr.write("Running " + " ".join(commands) + "\n")
    logfilecontents += " ".join(commands) + "\n"
    #returnval = pip.main(commands)
    try:
        subprocess.run(commands)
        returnval = 0
    except subprocess.CalledProcessError as err:
        returnval = err.returncode
    fix_fnctl()
    sys.stderr.flush()
    sys.stdout.flush()
    time.sleep(4)
    sys.stderr.write('Finished running pip' + "\n")
    with open(pip_log.name, 'rU', encoding='utf-8') as x:
        logfilecontents += x.read()
    pip_log.close()
    try:
        sys.stderr.write(logfilecontents + "\n")
    except:
        pass
    sys.stderr.flush()
    sys.stdout.flush()
    time.sleep(4)
    sys.stderr.write('uninstall_package: done' + "\n")
    return returnval, logfilecontents

class Object(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    pass

def get_installed_distributions():
    start_time = time.time()
    sys.stderr.write("get_installed_distributions: starting\n")
    results = list()
    try:
        output = subprocess.check_output(['pip', '--version']).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError as err:
        output = err.output.decode('utf-8', 'ignore')
    sys.stderr.write("get_installed_distributions: pip version:\n" + output)
    try:
        output = subprocess.check_output(['pip', 'list', '--format=freeze']).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError as err:
        output = err.output.decode('utf-8', 'ignore')
    #sys.stderr.write("get_installed_distributions: result of pip list --format freeze was:\n" + str(output) + "\n")
    for line in output.split('\n'):
        a = line.split("==")
        if len(a) == 2:
            results.append(Object(key=a[0], version=a[1]))
    sys.stderr.write("get_installed_distributions: ending after " + str(time.time() - start_time) + " seconds\n")
    #sys.stderr.write(repr([x.key for x in results]) + "\n")
    return results

def get_pip_info(package_name):
    #sys.stderr.write("get_pip_info: " + package_name + "\n")
    try:
        output = subprocess.check_output(['pip', 'show', package_name]).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError as err:
        output = ""
        sys.stderr.write("get_pip_info: error.  output was " + err.output.decode('utf-8', 'ignore') + "\n")
    # old_stdout = sys.stdout
    # sys.stdout = saved_stdout = StringIO()
    # pip.main(['show', package_name])
    # sys.stdout = old_stdout
    # output = saved_stdout.getvalue()
    results = dict()
    if not isinstance(output, str):
        output = output.decode('utf-8', 'ignore')
    for line in output.split('\n'):
        #sys.stderr.write("Found line " + str(line) + "\n")
        a = line.split(": ")
        if len(a) == 2:
            #sys.stderr.write("Found " + a[0] + " which was " + a[1] + "\n")
            results[a[0]] = a[1]
    for key in ['Name', 'Home-page', 'Version']:
        if key not in results:
            results[key] = None
    return results

if __name__ == "__main__":
    #import docassemble.webapp.database
    from docassemble.webapp.app_object import app
    with app.app_context():
        from docassemble.webapp.db_object import db
        from docassemble.webapp.packages.models import Package, Install, PackageAuth
        from docassemble.webapp.daredis import r
        #app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
        if mode == 'initialize':
            sys.stderr.write("updating with mode initialize\n")
            update_versions()
            any_package = Package.query.filter_by(active=True).first()
            if any_package is None:
                add_dependencies(1)
                update_versions()
            check_for_updates(doing_startup=True)
            remove_inactive_hosts()
        else:
            sys.stderr.write("updating with mode check_for_updates\n")
            check_for_updates()
            from docassemble.base.config import daconfig
            if USING_SUPERVISOR:
                SUPERVISORCTL = daconfig.get('supervisorctl', 'supervisorctl')
                container_role = ':' + os.environ.get('CONTAINERROLE', '') + ':'
                if re.search(r':(web|celery|all):', container_role):
                    sys.stderr.write("Sending reset signal\n")
                    args = [SUPERVISORCTL, '-s', 'http://localhost:9001', 'start', 'reset']
                    subprocess.run(args)
                else:
                    sys.stderr.write("Not sending reset signal because not web or celery\n")
            else:
                sys.stderr.write("update: touched wsgi file" + "\n")
                wsgi_file = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
                if os.path.isfile(wsgi_file):
                    with open(wsgi_file, 'a'):
                        os.utime(wsgi_file, None)
        db.engine.dispose()
    sys.exit(0)
