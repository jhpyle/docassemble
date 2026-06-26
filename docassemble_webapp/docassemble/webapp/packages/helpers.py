import importlib
import fnmatch
from io import TextIOWrapper
import re
import os
import traceback
import zipfile
import tomli
from flask import current_app
from docassemble.base.error import DAException
from docassemble.base.thread_context import this_thread
from docassemble.webapp.config import FULL_PACKAGE_DIRECTORY, daconfig
from docassemble.webapp.users.helpers import login_as_admin
from docassemble.webapp.utils.logger import logmessage
from docassemble.webapp.utils.path import splitall

def import_necessary(url, url_root):
    login_as_admin(url, url_root)
    modules_to_import = daconfig.get('preloaded modules', None)
    if isinstance(modules_to_import, list):
        for module_name in daconfig['preloaded modules']:
            try:
                importlib.import_module(module_name)
            except:
                pass

    start_dir = len(FULL_PACKAGE_DIRECTORY.split(os.sep))
    avoid_dirs = [os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'base'),
                  os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'demo'),
                  os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble', 'webapp')]
    modules = ['docassemble.base.legal']
    use_whitelist = 'module whitelist' in daconfig
    for root, dirs, files in os.walk(os.path.join(FULL_PACKAGE_DIRECTORY, 'docassemble')):  # pylint: disable=unused-variable
        ok = True
        for avoid in avoid_dirs:
            if root.startswith(avoid):
                ok = False
                break
        if not ok:
            continue
        for the_file in files:
            if not the_file.endswith('.py'):
                continue
            thefilename = os.path.join(root, the_file)
            if use_whitelist:
                parts = thefilename.split(os.sep)[start_dir:]
                parts[-1] = parts[-1][0:-3]
                module_name = '.'.join(parts)
                module_name = re.sub(r'\.__init__$', '', module_name)
                if any(fnmatch.fnmatchcase(module_name, whitelist_item) for whitelist_item in daconfig['module whitelist']):
                    modules.append(module_name)
                continue
            with open(thefilename, 'r', encoding='utf-8') as fp:
                for line in fp:
                    if line.startswith('# do not pre-load'):
                        break
                    if line.startswith('class ') or line.startswith('# pre-load') or 'docassemble.base.util.update' in line:
                        parts = thefilename.split(os.sep)[start_dir:]
                        parts[-1] = parts[-1][0:-3]
                        module_name = '.'.join(parts)
                        module_name = re.sub(r'\.__init__$', '', module_name)
                        modules.append(module_name)
                        break
    for module_name in modules:
        if any(fnmatch.fnmatchcase(module_name, blacklist_item) for blacklist_item in daconfig['module blacklist']):
            continue
        current_package = re.sub(r'\.[^\.]+$', '', module_name)
        this_thread.current_package = current_package
        this_thread.current_info.update({'yaml_filename': current_package + ':data/questions/test.yml'})
        try:
            importlib.import_module(module_name)
        except BaseException:
            try:
                error_trace = traceback.format_exc()
                logmessage("Import of " + module_name + " failed.  " + error_trace)
            except:
                logmessage("Import of " + module_name + " failed.")
    current_app.login_manager._update_request_context_with_user()


def get_package_name_from_zip(zippath):
    with zipfile.ZipFile(zippath, mode='r') as zf:
        min_level = 999999
        setup_py = None
        pyproject_toml = None
        for zinfo in zf.infolist():
            parts = splitall(zinfo.filename)
            if parts[-1] in ('setup.py', 'pyproject.toml'):
                if len(parts) <= min_level:
                    if parts[-1] == 'setup.py':
                        setup_py = zinfo
                    else:
                        pyproject_toml = zinfo
                    min_level = len(parts)
        if setup_py:
            with zf.open(setup_py) as f:
                the_file = TextIOWrapper(f, encoding='utf8')
                contents = the_file.read()
                extracted = {}
                for line in contents.splitlines():
                    m = re.search(r"^NAME *= *\(?'(.*)'", line)
                    if m:
                        extracted['name'] = m.group(1)
                    m = re.search(r'^NAME *= *\(?"(.*)"', line)
                    if m:
                        extracted['name'] = m.group(1)
                    m = re.search(r'^NAME *= *\[(.*)\]', line)
                    if m:
                        extracted['name'] = m.group(1)
                if 'name' in extracted:
                    return extracted['name']
                contents = re.sub(r'.*setup\(', '', contents, flags=re.DOTALL)
                extracted = {}
                for line in contents.splitlines():
                    m = re.search(r"^ *([a-z_]+) *= *\(?'(.*)'", line)
                    if m:
                        extracted[m.group(1)] = m.group(2)
                    m = re.search(r'^ *([a-z_]+) *= *\(?"(.*)"', line)
                    if m:
                        extracted[m.group(1)] = m.group(2)
                    m = re.search(r'^ *([a-z_]+) *= *\[(.*)\]', line)
                    if m:
                        extracted[m.group(1)] = m.group(2)
                if 'name' not in extracted:
                    raise DAException("Could not find name of Python package")
                return extracted['name']
        if pyproject_toml:
            with zf.open(pyproject_toml) as f:
                the_file = TextIOWrapper(f, encoding='utf8')
                contents = the_file.read()
                data = tomli.loads(contents)
                if 'project' in data and 'name' in data['project']:
                    return data['project']['name']
                raise DAException("Could not find name of Python package")
    raise DAException("Not a Python package zip file")
