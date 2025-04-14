import os
import sys
import socket
import tempfile
import subprocess
import xmlrpc.client
import re
# from io import StringIO
import shutil
import time
import fcntl  # pylint: disable=import-error
from packaging import version
import docassemble.base.config
from docassemble.base.config import daconfig
from docassemble.base.logger import logmessage
from docassemble.webapp.info import system_packages

installed_distribution_cache = None

mode = 'initialize'

if __name__ == "__main__":
    docassemble.base.config.load(arguments=sys.argv)
    if 'initialize' in sys.argv:
        mode = 'initialize'
    elif 'check_for_updates' in sys.argv:
        mode = 'check_for_updates'
    else:
        mode = 'initialize'

USING_SUPERVISOR = bool(os.environ.get('SUPERVISOR_SERVER_URL', None))
SINGLE_SERVER = USING_SUPERVISOR and bool(':all:' in ':' + os.environ.get('CONTAINERROLE', 'all') + ':')


def fix_fnctl():
    try:
        flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
        logmessage("fix_fnctl: updated stdout")
    except:
        pass
    try:
        flags = fcntl.fcntl(sys.stderr, fcntl.F_GETFL)
        fcntl.fcntl(sys.stderr, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
        logmessage("fix_fnctl: updated stderr")
    except:
        pass


def remove_inactive_hosts(start_time=None):
    if start_time is None:
        start_time = time.time()
    logmessage("remove_inactive_hosts: starting after " + str(time.time() - start_time) + " seconds")
    if USING_SUPERVISOR:
        from docassemble.base.config import hostname  # pylint: disable=import-outside-toplevel
        # from docassemble.webapp.app_object import app  # pylint: disable=import-outside-toplevel
        from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
        from docassemble.webapp.core.models import Supervisors  # pylint: disable=import-outside-toplevel
        from sqlalchemy import select, delete  # pylint: disable=import-outside-toplevel
        to_delete = set()
        for host in db.session.execute(select(Supervisors)).scalars():
            if host.hostname == hostname:
                continue
            try:
                socket.gethostbyname(host.hostname)
                server = xmlrpc.client.Server(host.url + '/RPC2')
                server.supervisor.getState()
            except:
                to_delete.add(host.id)
        for id_to_delete in to_delete:
            db.session.execute(delete(Supervisors).filter_by(id=id_to_delete))
            db.session.commit()
    logmessage("remove_inactive_hosts: ended after " + str(time.time() - start_time) + " seconds")


class DummyPackage:

    def __init__(self, name):
        self.name = name
        self.type = 'pip'
        self.limitation = None


def clear_invalid_package(start_time=None):
    if start_time is None:
        start_time = time.time()
    logmessage("clear_invalid_package: starting after " + str(time.time() - start_time) + " seconds")
    from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.packages.models import Package  # pylint: disable=import-outside-toplevel
    from sqlalchemy import delete, select  # pylint: disable=import-outside-toplevel
    from sqlalchemy.orm import aliased  # pylint: disable=import-outside-toplevel
    PackageA = aliased(Package, name='a')
    PackageB = aliased(Package, name='b')
    result = db.session.execute(
        select(PackageA.id)
        .join(PackageB, PackageA.name.ilike(PackageB.name))
        .filter(PackageB.active == True)  # noqa: E712 # pylint: disable=singleton-comparison
        .filter(PackageB.id > PackageA.id)
        .group_by(PackageA.id)).all()
    for item in result:
        db.session.execute(delete(Package).filter_by(id=item.id))
    db.session.commit()
    logmessage("clear_invalid_package: finishing after " + str(time.time() - start_time) + " seconds")


def clear_invalid_package_auth(start_time=None):
    if start_time is None:
        start_time = time.time()
    logmessage("clear_invalid_package_auth: starting after " + str(time.time() - start_time) + " seconds")
    from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.packages.models import PackageAuth  # pylint: disable=import-outside-toplevel
    from sqlalchemy import delete  # pylint: disable=import-outside-toplevel
    db.session.execute(delete(PackageAuth).filter_by(package_id=None))
    db.session.commit()
    logmessage("clear_invalid_package_auth: finishing after " + str(time.time() - start_time) + " seconds")


def check_for_updates(start_time=None, invalidate_cache=True, full=True):
    if start_time is None:
        start_time = time.time()
    logmessage("check_for_updates: starting after " + str(time.time() - start_time) + " seconds")
    if invalidate_cache:
        invalidate_installed_distributions_cache()
    from docassemble.base.config import hostname  # pylint: disable=import-outside-toplevel
    # from docassemble.webapp.app_object import app  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.packages.models import Package, Install, PackageAuth  # pylint: disable=import-outside-toplevel
    from sqlalchemy import select, delete  # pylint: disable=import-outside-toplevel
    ok = True  # tracks whether there have been any errors
    here_already = {}  # packages that are installed on this server, based on pip list. package name -> package version
    results = {}  # result of actions taken on a package. package name -> message
    if full:
        logmessage("check_for_updates: 0.5 after " + str(time.time() - start_time) + " seconds")
        for package_name in ('psycopg2', 'pdfminer', 'pdfminer3k', 'py-bcrypt', 'pycrypto', 'constraint', 'distutils2', 'azure-storage', 'Flask-User', 'Marisol', 'sklearn', 'backports.zoneinfo', 'Flask-Babel', 'docassemble-backports', 'typing-extensions', 'Babel', 'pyasn1-modules', 'Pillow', 'email-validator', 'importlib-metadata', 'importlib-resources', 'prompt-toolkit', 'readme-renderer', 'parse-type', 'et-xmlfile', 'docassemble'):
            result = db.session.execute(delete(Package).filter_by(name=package_name))
            if result.rowcount > 0:
                db.session.commit()
        logmessage("check_for_updates: 1 after " + str(time.time() - start_time) + " seconds")
    installed_packages = get_installed_distributions(start_time=start_time)
    for package in installed_packages:
        here_already[package.key] = package.version
    changed = False
    # clean up old packages that cause problems.
    if full:
        if 'psycopg2' in here_already:
            logmessage("check_for_updates: uninstalling psycopg2")
            uninstall_package(DummyPackage('psycopg2'), start_time=start_time)
            if 'psycopg2-binary' in here_already:
                logmessage("check_for_updates: reinstalling psycopg2-binary")
                uninstall_package(DummyPackage('psycopg2-binary'), start_time=start_time)
                install_package(DummyPackage('psycopg2-binary'), start_time=start_time)
            changed = True
        if 'psycopg2-binary' not in here_already:
            logmessage("check_for_updates: installing psycopg2-binary")
            install_package(DummyPackage('psycopg2-binary'), start_time=start_time)
            changed = True
        if 'kombu' not in here_already or version.parse(here_already['kombu']) <= version.parse('4.1.0'):
            logmessage("check_for_updates: installing new kombu version")
            install_package(DummyPackage('kombu'), start_time=start_time)
            changed = True
        if 'celery' not in here_already or version.parse(here_already['celery']) <= version.parse('4.1.0'):
            logmessage("check_for_updates: installing new celery version")
            install_package(DummyPackage('celery'), start_time=start_time)
            changed = True
        if 'pycrypto' in here_already:
            logmessage("check_for_updates: uninstalling pycrypto")
            uninstall_package(DummyPackage('pycrypto'), start_time=start_time)
            if 'pycryptodome' in here_already:
                logmessage("check_for_updates: reinstalling pycryptodome")
                uninstall_package(DummyPackage('pycryptodome'), start_time=start_time)
                install_package(DummyPackage('pycryptodome'), start_time=start_time)
            changed = True
        if 'pycryptodome' not in here_already:
            logmessage("check_for_updates: installing pycryptodome")
            install_package(DummyPackage('pycryptodome'), start_time=start_time)
            changed = True
        if 'pdfminer' in here_already:
            logmessage("check_for_updates: uninstalling pdfminer")
            uninstall_package(DummyPackage('pdfminer'), start_time=start_time)
            changed = True
        if 'Marisol' in here_already:
            logmessage("check_for_updates: uninstalling Marisol")
            uninstall_package(DummyPackage('Marisol'), start_time=start_time)
            changed = True
        if 'pdfminer3k' in here_already:
            logmessage("check_for_updates: uninstalling pdfminer3k")
            uninstall_package(DummyPackage('pdfminer3k'), start_time=start_time)
            changed = True
        if 'docassemble' in here_already:
            logmessage("check_for_updates: uninstalling docassemble")
            uninstall_package(DummyPackage('docassemble'), start_time=start_time)
            changed = True
        if 'pdfminer.six' in here_already:
            try:
                from pdfminer.pdfparser import PDFParser  # noqa: F401 # pylint: disable=import-outside-toplevel,unused-import
                from pdfminer.pdfdocument import PDFDocument  # noqa: F401 # pylint: disable=import-outside-toplevel,unused-import
            except:
                logmessage("check_for_updates: reinstalling pdfminer.six")
                uninstall_package(DummyPackage('pdfminer.six'), start_time=start_time)
                install_package(DummyPackage('pdfminer.six'), start_time=start_time)
        else:
            logmessage("check_for_updates: installing pdfminer.six")
            install_package(DummyPackage('pdfminer.six'), start_time=start_time)
            changed = True
        if 'py-bcrypt' in here_already:
            logmessage("check_for_updates: uninstalling py-bcrypt")
            uninstall_package(DummyPackage('py-bcrypt'), start_time=start_time)
            changed = True
            if 'bcrypt' in here_already:
                logmessage("check_for_updates: reinstalling bcrypt")
                uninstall_package(DummyPackage('bcrypt'), start_time=start_time)
                install_package(DummyPackage('bcrypt'), start_time=start_time)
                changed = True
        if 'bcrypt' not in here_already:
            logmessage("check_for_updates: installing bcrypt")
            install_package(DummyPackage('bcrypt'), start_time=start_time)
            changed = True
        if changed:
            installed_packages = get_installed_distributions(start_time=start_time)
            here_already = {}
            for package in installed_packages:
                here_already[package.key] = package.version
    logmessages = ''
    packages = {}  # packages that the database says are active and that have a type; package id -> package row
    installs = {}  # install rows representing what the database says in installed; package id -> install row
    to_install = []  # package rows of packages to install
    to_uninstall = []  # package rows of packages to uninstall
    system_packages_to_fix = []
    uninstall_done = set()  # set of package names of packages already uninstalled
    uninstalled_packages = {}  # packages with active=False; package id -> package row
    package_ids_to_delete = set()  # set if IDs of package rows that have active=False but there is another row with active= True
    package_by_name = {}  # packages the database says are active; package name -> package row
    logmessage("check_for_updates: 2 after " + str(time.time() - start_time) + " seconds")
    # create dict package_by_name that maps a package name to a package database row,
    # for packages that the database says should be installed
    for package in db.session.execute(select(Package.name).filter_by(active=True)):
        package_by_name[package.name] = package
        # logmessage("check_for_updates: database includes a package called " + package.name + " after " + str(time.time() - start_time) + " seconds")
    # packages is what is supposed to be installed
    logmessage("check_for_updates: 3 after " + str(time.time() - start_time) + " seconds")
    # create dict packages that maps a package ID to a package database row if the type is not null
    for package in db.session.execute(select(Package).filter_by(active=True)).scalars():
        if package.type is not None:
            packages[package.id] = package
            # logmessage("check_for_updates: database includes a package called " + package.name + " that has a type after " + str(time.time() - start_time) + " seconds")
            # print("Found a package " + package.name)
    logmessage("check_for_updates: 4 after " + str(time.time() - start_time) + " seconds")
    # create dict uninstalled_packages that maps a package ID to a package database row if SQL wants the package deleted
    for package in db.session.execute(select(Package).filter_by(active=False)).scalars():
        # don't uninstall a system package
        if package.name in system_packages:
            logmessages += "Not uninstalling " + str(package.name) + " because it is a system package."
            system_packages_to_fix.append(package)
            continue
        if package.name in package_by_name:
            # there are two Package entries for the same package, one with active=True, one with active=False
            logmessage("check_for_updates: conflicting package entries for " + package.name + " after " + str(time.time() - start_time) + " seconds")
            # let's delete the one with active=False
            package_ids_to_delete.add(package.id)
        else:
            # logmessage("check_for_updates: database says " + package.name + " should be uninstalled after " + str(time.time() - start_time) + " seconds")
            uninstalled_packages[package.id] = package  # this is what the database says should be uninstalled
    logmessage("check_for_updates: 5 after " + str(time.time() - start_time) + " seconds")
    # build to_uninstall, which is the list of Package database entries targeted for uninstallation.
    # Only add if there is an Install entry linked to the package id and there is no active Package row
    # with the same name.
    # Also build installs, which is a dict mapping package IDs to install rows, based on
    # what the Install table says
    for install in db.session.execute(select(Install).filter_by(hostname=hostname)).scalars():
        installs[install.package_id] = install  # this is what the database says in installed on this server
        if install.package_id in uninstalled_packages and uninstalled_packages[install.package_id].name not in package_by_name:
            logmessage("check_for_updates: " + uninstalled_packages[install.package_id].name + " will be uninstalled after " + str(time.time() - start_time) + " seconds")
            to_uninstall.append(uninstalled_packages[install.package_id])  # uninstall if it is installed
    changed = False
    package_owner = {}
    logmessage("check_for_updates: 6 after " + str(time.time() - start_time) + " seconds")
    for auth in db.session.execute(select(PackageAuth).filter_by(authtype='owner')).scalars():
        package_owner[auth.package_id] = auth.user_id
    logmessage("check_for_updates: 7 after " + str(time.time() - start_time) + " seconds")
    # Add Install rows for any active Package rows with non-null types if the package is present on the server
    # Also add to the installs dict after adding.
    for package in packages.values():
        if package.id not in installs and package.name in here_already:
            logmessage("check_for_updates: package " + package.name + " here already.  Writing an Install record for it.")
            install = Install(hostname=hostname, packageversion=here_already[package.name], version=package.version, package_id=package.id)
            db.session.add(install)
            installs[package.id] = install
            changed = True
    if changed:
        db.session.commit()
    logmessage("check_for_updates: 8 after " + str(time.time() - start_time) + " seconds")
    for package in packages.values():
        # logmessage("check_for_updates: processing package id " + str(package.id))
        # logmessage("1: " + str(installs[package.id].packageversion) + " 2: " + str(package.packageversion))
        try:
            pack_vers = version.parse(package.packageversion)
            inst_vers = version.parse(installs[package.id].packageversion)
        except:
            pack_vers = version.parse('1.0.0')
            inst_vers = version.parse('1.0.0')
        if (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is None) or (package.packageversion is not None and package.id in installs and installs[package.id].packageversion is not None and pack_vers > inst_vers):
            logmessage("check_for_updates: a new version of " + package.name + " is needed because the necessary package version, " + str(package.packageversion) + ", is ahead of the installed version, " + str(installs[package.id].packageversion) + " after " + str(time.time() - start_time) + " seconds")
            new_version_needed = True
        else:
            new_version_needed = False
        # logmessage("got here and new version is " + str(new_version_needed))
        # Check for missing local packages
        if (package.name not in here_already) and (package.id in installs):
            logmessage("check_for_updates: the package " + package.name + " is supposed to be installed on this server, but was not detected after " + str(time.time() - start_time) + " seconds")
            package_missing = True
        else:
            package_missing = False
        if package.id in installs and package.version > installs[package.id].version:
            logmessage("check_for_updates: the package " + package.name + " has internal version " + str(package.version) + " but the installed version has version " + str(installs[package.id].version) + " after " + str(time.time() - start_time) + " seconds")
            package_version_greater = True
        else:
            package_version_greater = False
        if package.id not in installs:
            logmessage("check_for_updates: the package " + package.name + " is not in the table of installed packages for this server after " + str(time.time() - start_time) + " seconds")
        if package.id not in installs or package_version_greater or new_version_needed or package_missing:
            if package.name in system_packages:
                logmessages += "Not upgrading " + str(package.name) + " because it is a system package and its version needs to be consistent with the version of the package that is required by the docassemble.webapp package.\n"
                logmessage("check_for_updates: the package " + package.name + " is a system package and cannot be updated except through docassemble.webapp after " + str(time.time() - start_time) + " seconds")
                system_packages_to_fix.append(package)
            else:
                to_install.append(package)
    # logmessage("done with that")
    logmessage("check_for_updates: 9 after " + str(time.time() - start_time) + " seconds")
    for package in to_uninstall:
        # logmessage("Going to uninstall a package: " + package.name)
        if package.name in uninstall_done:
            logmessage("check_for_updates: skipping uninstallation of " + str(package.name) + " because already uninstalled after " + str(time.time() - start_time) + " seconds")
            continue
        if package.name not in here_already:
            logmessage("check_for_updates: skipping uninstallation of " + str(package.name) + " because not installed" + " after " + str(time.time() - start_time) + " seconds")
            returnval = 1
            newlog = ''
        else:
            logmessage("check_for_updates: calling uninstall_package on " + package.name)
            returnval, newlog = uninstall_package(package, start_time=start_time)
        uninstall_done.add(package.name)
        logmessages += newlog
        if returnval == 0:
            db.session.execute(delete(Install).filter_by(hostname=hostname, package_id=package.id))
            results[package.name] = 'pip uninstall command returned success code.  See log for details.'
        elif returnval == 1:
            db.session.execute(delete(Install).filter_by(hostname=hostname, package_id=package.id))
            results[package.name] = 'pip uninstall was not run because the package was not installed.'
        else:
            results[package.name] = 'pip uninstall command returned failure code'
            ok = False
    packages_to_delete = []
    logmessage("check_for_updates: 10 after " + str(time.time() - start_time) + " seconds")
    did_something = False
    for package in to_install:
        did_something = True
        logmessage("check_for_updates: going to install a package: " + package.name + " after " + str(time.time() - start_time) + " seconds")
        # if doing_startup and package.name.startswith('docassemble') and package.name in here_already:
        #     # adding this because of unpredictability of installing new versions of docassemble
        #     # just because of a system restart.
        #     logmessage("check_for_updates: skipping update on " + str(package.name))
        #     continue
        returnval, newlog = install_package(package, start_time=start_time)
        logmessages += newlog
        logmessage("check_for_updates: return value was " + str(returnval) + " after " + str(time.time() - start_time) + " seconds")
        if returnval != 0:
            logmessage("Return value was not good" + " after " + str(time.time() - start_time) + " seconds")
            ok = False
        if full:
            pip_info = get_pip_info(package.name, start_time=start_time)
            real_name = pip_info['Name']
            logmessage("check_for_updates: real name of package " + str(package.name) + " is " + str(real_name) + " after " + str(time.time() - start_time) + " seconds")
        else:
            real_name = package.name
        if real_name is None:
            results[package.name] = 'install failed'
            ok = False
            if package.name not in here_already:
                logmessage("check_for_updates: removing package entry for " + package.name + " after " + str(time.time() - start_time) + " seconds")
                packages_to_delete.append(package)
        elif returnval != 0:
            results[package.name] = 'pip install command returned failure code'
        else:
            results[package.name] = 'pip install command returned success code.  See log for details.'
            if real_name != package.name:
                logmessage("check_for_updates: changing name" + " after " + str(time.time() - start_time) + " seconds")
                package.name = real_name
            if package.id in installs:
                install = installs[package.id]
                install.version = package.version
            else:
                install = Install(hostname=hostname, packageversion=package.packageversion, version=package.version, package_id=package.id)
                db.session.add(install)
            db.session.commit()
    if did_something:
        update_versions(start_time=start_time)
        if full and add_dependencies(package_owner.get(package.id, 1), start_time=start_time):
            update_versions(start_time=start_time)
    logmessage("check_for_updates: 11 after " + str(time.time() - start_time) + " seconds")
    for package in packages_to_delete:
        try:
            db.session.delete(package)
        except:
            logmessage("check_for_updates: unable to uninstall package")
    logmessage("check_for_updates: 12 after " + str(time.time() - start_time) + " seconds")
    db.session.commit()
    logmessage("check_for_updates: finished uninstalling and installing after " + str(time.time() - start_time) + " seconds")
    return ok, logmessages, results


def update_versions(start_time=None):
    if start_time is None:
        start_time = time.time()
    logmessage("update_versions: starting after " + str(time.time() - start_time) + " seconds")
    from docassemble.base.config import hostname  # pylint: disable=import-outside-toplevel
    # from docassemble.webapp.app_object import app  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.packages.models import Package, Install  # pylint: disable=import-outside-toplevel
    from sqlalchemy import select  # pylint: disable=import-outside-toplevel
    install_by_id = {}
    for install in db.session.execute(select(Install).filter_by(hostname=hostname)).scalars():
        install_by_id[install.package_id] = install
    package_by_name = {}
    for package in db.session.execute(select(Package).filter_by(active=True).order_by(Package.name, Package.id.desc())).scalars():
        if package.name in package_by_name:
            continue
        package_by_name[package.name] = Object(id=package.id, packageversion=package.packageversion, name=package.name)
    installed_packages = get_installed_distributions(start_time=start_time)
    for package in installed_packages:
        if package.key in package_by_name:
            if package_by_name[package.key].id in install_by_id and package.version != install_by_id[package_by_name[package.key].id].packageversion:
                for install_row in db.session.execute(select(Install).filter_by(hostname=hostname, package_id=package_by_name[package.key].id)).scalars():
                    install_row.packageversion = package.version
            if package.version != package_by_name[package.key].packageversion:
                for package_row in db.session.execute(select(Package).filter_by(active=True, name=package_by_name[package.key].name).with_for_update()).scalars():
                    package_row.packageversion = package.version
    db.session.commit()
    logmessage("update_versions: ended after " + str(time.time() - start_time))


def get_home_page_dict():
    PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))
    FULL_PACKAGE_DIRECTORY = os.path.join(PACKAGE_DIRECTORY, 'lib', 'python' + str(sys.version_info.major) + '.' + str(sys.version_info.minor), 'site-packages')
    home_page = {}
    for d in os.listdir(FULL_PACKAGE_DIRECTORY):
        if not d.startswith('docassemble.'):
            continue
        metadata_path = os.path.join(d, 'METADATA')
        if os.path.isfile(metadata_path):
            name = None
            url = None
            with open(metadata_path, 'r', encoding='utf-8') as fp:
                for line in fp:
                    if line.startswith('Name: '):
                        name = line[6:]
                    elif line.startswith('Home-page: '):
                        url = line[11:].rstrip('/')
                        break
            if name:
                home_page[name.lower()] = url
    return home_page


def add_dependencies(user_id, start_time=None):
    if start_time is None:
        start_time = time.time()
    # logmessage('add_dependencies: user_id is ' + str(user_id))
    logmessage("add_dependencies: starting after " + str(time.time() - start_time) + " seconds")
    from docassemble.base.config import hostname  # pylint: disable=import-outside-toplevel
    # from docassemble.webapp.app_object import app  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.packages.models import Package, Install, PackageAuth  # pylint: disable=import-outside-toplevel
    from sqlalchemy import select, delete  # pylint: disable=import-outside-toplevel
    packages_known = set()
    for package in db.session.execute(select(Package.name).filter_by(active=True)):
        packages_known.add(package.name)
    installed_packages = get_installed_distributions(start_time=start_time)
    # logmessage("add_dependencies: installed_packages is " + repr(installed_packages))
    home_pages = None
    packages_to_add = []
    for package in installed_packages:
        # logmessage("add_dependencies: package is " + repr(package.key))
        if package.key in packages_known:
            continue
        if package.key.startswith('mysqlclient') or package.key.startswith('mysql-connector') or package.key.startswith('MySQL-python'):
            continue
        # logmessage("add_dependencies: going to delete " + repr(package.key))
        db.session.execute(delete(Package).filter_by(name=package.key))
        packages_to_add.append(package)
    did_something = False
    if len(packages_to_add) > 0:
        did_something = True
        db.session.commit()
        for package in packages_to_add:
            if package.key.startswith('docassemble.'):
                if home_pages is None:
                    home_pages = get_home_page_dict()
                home_page = home_pages.get(package.key.lower(), None)
                if home_page is not None and re.search(r'/github.com/', home_page):
                    package_entry = Package(name=package.key, package_auth=PackageAuth(user_id=user_id), type='git', giturl=home_page, packageversion=package.version, dependency=True)
                else:
                    package_entry = Package(name=package.key, package_auth=PackageAuth(user_id=user_id), type='pip', packageversion=package.version, dependency=True)
            else:
                package_entry = Package(name=package.key, package_auth=PackageAuth(user_id=user_id), type='pip', packageversion=package.version, dependency=True)
            db.session.add(package_entry)
            db.session.commit()
            install = Install(hostname=hostname, packageversion=package_entry.packageversion, version=package_entry.version, package_id=package_entry.id)
            db.session.add(install)
            db.session.commit()
    logmessage("add_dependencies: ending after " + str(time.time() - start_time) + " seconds")
    return did_something


def fix_names():
    # from docassemble.webapp.app_object import app  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
    from docassemble.webapp.packages.models import Package  # pylint: disable=import-outside-toplevel
    from sqlalchemy import select  # pylint: disable=import-outside-toplevel
    installed_packages = [package.key for package in get_installed_distributions()]
    for package in db.session.execute(select(Package).filter_by(active=True).with_for_update()).scalars():
        if package.name not in installed_packages:
            pip_info = get_pip_info(package.name)
            actual_name = pip_info['Name']
            if actual_name is not None:
                package.name = actual_name
            else:
                logmessage("fix_names: package " + package.name + " does not appear to be installed")
    db.session.commit()


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        if parts[1] == path:
            allparts.insert(0, parts[1])
            break
        path = parts[0]
        allparts.insert(0, parts[1])
    return allparts


def install_package(package, start_time=None):
    if start_time is None:
        start_time = time.time()
    invalidate_installed_distributions_cache()
    logmessage("install_package: " + package.name + " after " + str(time.time() - start_time) + " seconds")
    if package.type == 'zip' and package.upload is None:
        return 0, ''
    from docassemble.webapp.files import SavedFile  # pylint: disable=import-outside-toplevel
    PACKAGE_DIRECTORY = daconfig.get('packages', '/usr/share/docassemble/local' + str(sys.version_info.major) + '.' + str(sys.version_info.minor))
    logfilecontents = ''
    pip_log = tempfile.NamedTemporaryFile()
    temp_dir = tempfile.mkdtemp(prefix='SavedFile')
    # use_pip_cache = r.get('da:updatepackage:use_pip_cache')
    # if use_pip_cache is None:
    #     disable_pip_cache = False
    # elif int(use_pip_cache):
    #     disable_pip_cache = False
    # else:
    #     disable_pip_cache = True
    disable_pip_cache = True
    if package.type in ('zip', 'git'):
        logmessage("install_package: calling uninstall_package on " + package.name + " after " + str(time.time() - start_time) + " seconds")
        returnval, newlog = uninstall_package(package, start_time=start_time)
        logfilecontents += newlog
    if package.type == 'zip' and package.upload is not None:
        saved_file = SavedFile(package.upload, extension='zip', fix=True)
        commands = ['pip', 'install']
        if disable_pip_cache:
            commands.append('--no-cache-dir')
        commands.extend(['--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + temp_dir, '--log-file=' + pip_log.name, '--upgrade', saved_file.path + '.zip'])
    elif package.type == 'git' and package.giturl:
        if package.gitbranch is not None:
            branchpart = '@' + str(package.gitbranch)
        else:
            branchpart = ''
        if str(package.giturl).endswith('.git'):
            gitsuffix = ''
        else:
            gitsuffix = '.git'
        if str(package.giturl).startswith('git+'):
            gitprefix = ''
        else:
            gitprefix = 'git+'
        if package.gitsubdir is not None:
            commands = ['pip', 'install']
            if disable_pip_cache:
                commands.append('--no-cache-dir')
            commands.extend(['--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + temp_dir, '--upgrade', '--log-file=' + pip_log.name, gitprefix + str(package.giturl).rstrip('/') + gitsuffix + branchpart + '#egg=' + package.name + '&subdirectory=' + str(package.gitsubdir)])
        else:
            commands = ['pip', 'install']
            if disable_pip_cache:
                commands.append('--no-cache-dir')
            commands.extend(['--quiet', '--prefix=' + PACKAGE_DIRECTORY, '--src=' + temp_dir, '--upgrade', '--log-file=' + pip_log.name, gitprefix + str(package.giturl).rstrip('/') + gitsuffix + branchpart + '#egg=' + package.name])
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
        logmessage("install_package: wrong package type after " + str(time.time() - start_time) + " seconds")
        return 1, 'Unable to recognize package type: ' + package.name
    logmessage("install_package: running " + " ".join(commands) + " after " + str(time.time() - start_time) + " seconds")
    logfilecontents += "install_package: running " + " ".join(commands) + "\n"
    returnval = 1
    try:
        subprocess.run(commands, check=False)
        returnval = 0
    except subprocess.CalledProcessError as err:
        returnval = err.returncode
    pip_log.seek(0)
    with open(pip_log.name, 'r', encoding='utf-8') as x:
        logfilecontents += x.read()
    pip_log.close()
    shutil.rmtree(temp_dir)
    logmessage('install_package: returnval is: ' + str(returnval))
    logmessage('install_package: done' + " after " + str(time.time() - start_time) + " seconds")
    return returnval, logfilecontents


def uninstall_package(package, start_time=None):
    if start_time is None:
        start_time = time.time()
    invalidate_installed_distributions_cache()
    logmessage('uninstall_package: ' + package.name + " after " + str(time.time() - start_time) + " seconds")
    logfilecontents = 'uninstall_package: ' + package.name + "\n"
    pip_log = tempfile.NamedTemporaryFile()
    commands = ['pip', 'uninstall', '--yes', '--log-file=' + pip_log.name, package.name]
    logmessage("uninstall_package: running " + " ".join(commands) + " after " + str(time.time() - start_time) + " seconds")
    logfilecontents += "Running " + (" ".join(commands)) + "\n"
    try:
        subprocess.run(commands, check=False)
        returnval = 0
    except subprocess.CalledProcessError as err:
        returnval = err.returncode
    pip_log.seek(0)
    with open(pip_log.name, 'r', encoding='utf-8') as x:
        logfilecontents += x.read()
    pip_log.close()
    logmessage('uninstall_package: returnval is: ' + str(returnval))
    logmessage("uninstall_package: done after " + str(time.time() - start_time) + " seconds")
    logfilecontents += 'returnval is: ' + str(returnval) + "\n"
    logfilecontents += 'uninstall_package: done' + "\n"
    return returnval, logfilecontents


class Object:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def invalidate_installed_distributions_cache():
    global installed_distribution_cache
    installed_distribution_cache = None


def get_installed_distributions(start_time=None):
    global installed_distribution_cache
    if installed_distribution_cache is not None:
        return installed_distribution_cache
    if start_time is None:
        start_time = time.time()
    logmessage("get_installed_distributions: starting after " + str(time.time() - start_time) + " seconds")
    results = []
    # try:
    #     output = subprocess.check_output(['pip', '--version']).decode('utf-8', 'ignore')
    # except subprocess.CalledProcessError as err:
    #     output = err.output.decode('utf-8', 'ignore')
    # logmessage("get_installed_distributions: pip version: " + output.strip() + " after " + str(time.time() - start_time) + " seconds")
    try:
        output = subprocess.check_output(['pip', 'list', '--format=freeze']).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError as err:
        output = err.output.decode('utf-8', 'ignore')
    # logmessage("get_installed_distributions: result of pip list --format freeze was:\n" + str(output))
    for line in output.split('\n'):
        a = line.split("==")
        if len(a) == 2:
            results.append(Object(key=a[0], version=a[1]))
    installed_distribution_cache = results
    logmessage("get_installed_distributions: ending after " + str(time.time() - start_time) + " seconds")
    # logmessage(repr([x.key for x in results]))
    return results


def get_pip_info(package_name, start_time=None):
    if start_time is None:
        start_time = time.time()
    logmessage("get_pip_info: " + package_name + " after " + str(time.time() - start_time) + " seconds")
    try:
        output = subprocess.check_output(['pip', 'show', package_name]).decode('utf-8', 'ignore')
    except subprocess.CalledProcessError as err:
        output = ""
        logmessage("get_pip_info: error.  output was " + err.output.decode('utf-8', 'ignore') + " after " + str(time.time() - start_time) + " seconds")
    # old_stdout = sys.stdout
    # sys.stdout = saved_stdout = StringIO()
    # pip.main(['show', package_name])
    # sys.stdout = old_stdout
    # output = saved_stdout.getvalue()
    results = {}
    if not isinstance(output, str):
        output = output.decode('utf-8', 'ignore')
    for line in output.split('\n'):
        # logmessage("Found line " + str(line))
        a = line.split(": ")
        if len(a) == 2:
            # logmessage("Found " + a[0] + " which was " + a[1])
            results[a[0]] = a[1]
    for key in ['Name', 'Home-page', 'Version']:
        if key not in results:
            results[key] = None
    logmessage("get_pip_info: returning after " + str(time.time() - start_time) + " seconds")
    return results


def main():
    # import docassemble.webapp.database  # pylint: disable=import-outside-toplevel
    start_time = time.time()
    from docassemble.webapp.app_object import app  # pylint: disable=import-outside-toplevel
    with app.app_context():
        from docassemble.webapp.db_object import db  # pylint: disable=import-outside-toplevel
        from docassemble.webapp.packages.models import Package  # pylint: disable=import-outside-toplevel
        from sqlalchemy import select  # pylint: disable=import-outside-toplevel
        # app.config['SQLALCHEMY_DATABASE_URI'] = docassemble.webapp.database.alchemy_connection_string()
        clear_invalid_package(start_time=start_time)
        clear_invalid_package_auth(start_time=start_time)
        if mode == 'initialize':
            logmessage("update: updating with mode initialize after " + str(time.time() - start_time) + " seconds")
            update_versions(start_time=start_time)
            any_package = db.session.execute(select(Package).filter_by(active=True)).first()
            if any_package is None:
                add_dependencies(1, start_time=start_time)
                update_versions(start_time=start_time)
            check_for_updates(start_time=start_time, invalidate_cache=False)
            if not SINGLE_SERVER:
                remove_inactive_hosts(start_time=start_time)
        else:
            logmessage("update: updating with mode check_for_updates after " + str(time.time() - start_time) + " seconds")
            check_for_updates(start_time=start_time)
            if USING_SUPERVISOR:
                SUPERVISORCTL = [daconfig.get('supervisorctl', 'supervisorctl')]
                if daconfig['supervisor'].get('username', None):
                    SUPERVISORCTL.extend(['--username', daconfig['supervisor']['username'], '--password', daconfig['supervisor']['password']])
                container_role = ':' + os.environ.get('CONTAINERROLE', '') + ':'
                if re.search(r':(web|celery|all):', container_role):
                    logmessage("update: sending reset signal after " + str(time.time() - start_time) + " seconds")
                    args = SUPERVISORCTL + ['-s', 'http://localhost:9001', 'start', 'reset']
                    subprocess.run(args, check=False)
                else:
                    logmessage("update: not sending reset signal because not web or celery after " + str(time.time() - start_time) + " seconds")
            else:
                logmessage("update: touched wsgi file after " + str(time.time() - start_time) + " seconds")
                wsgi_file = daconfig.get('webapp', '/usr/share/docassemble/webapp/docassemble.wsgi')
                if os.path.isfile(wsgi_file):
                    with open(wsgi_file, 'a', encoding='utf-8'):
                        os.utime(wsgi_file, None)
        db.engine.dispose()
    sys.exit(0)

if __name__ == "__main__":
    main()
