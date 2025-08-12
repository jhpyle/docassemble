import datetime
import json
import mimetypes
import os
import re
import shutil
import subprocess
# import sys
import tempfile
import zipfile
import tomli_w
import urllib.parse
from packaging import version
from flask import url_for
from flask_login import current_user
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
import requests
from docassemble.base.config import daconfig
from docassemble.base.error import DAError
from docassemble.base.generate_key import random_alphanumeric
from docassemble.base.logger import logmessage
import docassemble.webapp.spdx
import docassemble.base.functions
from docassemble.webapp.update import get_pip_info
import docassemble.webapp.cloud

cloud = docassemble.webapp.cloud.get_cloud()

UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')

DEFAULT_GITIGNORE = """\
__pycache__/
*.py[cod]
*$py.class
.mypy_cache/
.dmypy.json
dmypy.json
*.egg-info/
.installed.cfg
*.egg
.vscode
*~
.#*
en
.history/
.idea
.dir-locals.el
.flake8
*.swp
.DS_Store
.envrc
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
"""


def listfiles(directory):
    result = []
    directory = directory.rstrip(os.sep)
    trimstart = len(directory) + 1
    for root, dirs, files in os.walk(directory):  # pylint: disable=unused-variable
        for filename in files:
            result.append(os.path.join(root, filename)[trimstart:])
    return result


def listdirs(directory):
    result = []
    directory = directory.rstrip(os.sep)
    trimstart = len(directory) + 1
    for root, dirs, files in os.walk(directory):  # pylint: disable=unused-variable
        for subdir in dirs:
            result.append(os.path.join(root, subdir)[trimstart:])
    return result


def path_to_key(path):
    return '/'.join(str(path).split(os.sep))


def url_sanitize(url):
    return re.sub(r'\s', ' ', url)


class SavedFile:

    def __init__(self, file_number, extension=None, fix=False, section='files', filename='file', subdir=None, should_not_exist=False, must_exist=False):  # pylint: disable=too-many-positional-arguments
        file_number = int(file_number)
        section = str(section)
        if section not in docassemble.base.functions.this_thread.saved_files:
            docassemble.base.functions.this_thread.saved_files[section] = {}
        if file_number in docassemble.base.functions.this_thread.saved_files[section]:
            # logmessage("SavedFile: using cache for " + section + '/' + str(file_number))
            sf = docassemble.base.functions.this_thread.saved_files[section][file_number]
            for attribute in ['file_number', 'fixed', 'section', 'filename', 'extension', 'directory', 'path', 'modtimes', 'keydict', 'subdir']:
                if hasattr(sf, attribute):
                    setattr(self, attribute, getattr(sf, attribute))
            self.extension = extension
            self.filename = filename
            self.subdir = subdir
        else:
            # logmessage("SavedFile: not using cache for " + section + '/' + str(file_number))
            self.fixed = False
            self.file_number = file_number
            self.section = section
            self.extension = extension
            self.filename = filename
            self.subdir = subdir
            if cloud is None:
                if self.section == 'files':
                    parts = re.sub(r'(...)', r'\1/', '{0:012x}'.format(int(file_number))).split('/')
                    self.directory = os.path.join(UPLOAD_DIRECTORY, *parts)
                else:
                    self.directory = os.path.join(UPLOAD_DIRECTORY, str(self.section), str(file_number))
            else:
                self.directory = os.path.join(tempfile.gettempdir(), str(self.section), str(self.file_number))
        docassemble.base.functions.this_thread.saved_files[section][file_number] = self
        if self.subdir and self.subdir != '' and self.subdir != 'default':
            self.path = os.path.join(self.directory, self.subdir, self.filename)
        else:
            self.path = os.path.join(self.directory, self.filename)
        if fix:
            self.fix(must_exist=must_exist)
            if must_exist and not os.path.isfile(self.path):
                return None
            if should_not_exist and os.path.isdir(self.directory):
                found_error = False
                for root, dirs, files in os.walk(self.directory):  # pylint: disable=unused-variable
                    if len(files) > 0 or len(dirs) > 0:
                        found_error = True
                        break
                if found_error:
                    logmessage("WARNING! Possible database corruption due to an unsafe shutdown. Your database indicated that the next file number is " + str(file_number) + ", but there is already a file in the file storage for that number. It is recommended that you restart your system. If that does not make this error go away, you should investigate why there are existing files in the file system.")
                    if cloud is not None:
                        prefix = str(self.section) + '/' + str(self.file_number) + '/'
                        for key in list(cloud.list_keys(prefix)):
                            try:
                                key.delete()
                            except:
                                pass
                    if hasattr(self, 'directory') and os.path.isdir(self.directory):
                        shutil.rmtree(self.directory)
                    if not os.path.isdir(self.directory):
                        os.makedirs(self.directory, exist_ok=True)
        return None

    def fix(self, must_exist=False):
        if self.fixed:
            return
        # logmessage("fix: starting " + str(self.section) + '/' + str(self.file_number))
        if cloud is not None:
            dirs_in_use = set()
            self.modtimes = {}
            self.keydict = {}
            if not os.path.isdir(self.directory):
                os.makedirs(self.directory, exist_ok=True)
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            # logmessage("fix: prefix is " + prefix)
            for key in cloud.list_keys(prefix):
                filename = os.path.join(*key.name[len(prefix):].split('/'))
                fullpath = os.path.join(self.directory, filename)
                fulldir = os.path.dirname(fullpath)
                dirs_in_use.add(fulldir)
                if not os.path.isdir(fulldir):
                    os.makedirs(fulldir, exist_ok=True)
                server_time = key.get_epoch_modtime()
                if not os.path.isfile(fullpath):
                    key.get_contents_to_filename(fullpath)
                else:
                    local_time = os.path.getmtime(fullpath)
                    if self.section == 'files':
                        if local_time != server_time:
                            key.get_contents_to_filename(fullpath)
                        update_access_time(fullpath)
                    else:
                        if local_time != server_time:
                            key.get_contents_to_filename(fullpath)
                self.modtimes[filename] = server_time
                # logmessage("cloud modtime for file " + filename + " is " + str(key.last_modified))
                self.keydict[filename] = key
            if self.subdir and self.subdir != '' and self.subdir != 'default':
                self.path = os.path.join(self.directory, self.subdir, self.filename)
            else:
                self.path = os.path.join(self.directory, self.filename)
            for filename in listfiles(self.directory):
                if filename not in self.modtimes:
                    os.remove(os.path.join(self.directory, filename))
            for subdir in listdirs(self.directory):
                if subdir not in dirs_in_use and os.path.isdir(subdir):
                    shutil.rmtree(subdir)
        else:
            if not os.path.isdir(self.directory) and not must_exist:
                os.makedirs(self.directory, exist_ok=True)
        self.fixed = True
        # logmessage("fix: ending " + str(self.section) + '/' + str(self.file_number))

    def delete_file(self, filename):
        if cloud is not None:
            prefix = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)
            to_delete = []
            for key in cloud.list_keys(prefix):
                to_delete.append(key)
            for key in to_delete:
                try:
                    key.delete()
                except:
                    pass
        if hasattr(self, 'directory') and os.path.isdir(self.directory):
            the_path = os.path.join(self.directory, filename)
            if os.path.isfile(the_path):
                os.remove(the_path)

    def delete_directory(self, directory):
        if cloud is not None:
            prefix = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(directory) + '/'
            to_delete = []
            for key in cloud.list_keys(prefix):
                to_delete.append(key)
            for key in to_delete:
                try:
                    key.delete()
                except:
                    pass
        if hasattr(self, 'directory') and os.path.isdir(self.directory):
            the_path = os.path.join(self.directory, directory)
            if os.path.isdir(the_path):
                shutil.rmtree(the_path)

    def delete(self):
        if cloud is not None:
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            for key in list(cloud.list_keys(prefix)):
                try:
                    key.delete()
                except:
                    pass
        if hasattr(self, 'directory') and os.path.isdir(self.directory):
            shutil.rmtree(self.directory)
        del docassemble.base.functions.this_thread.saved_files[str(self.section)][int(self.file_number)]

    def save(self, finalize=False):
        self.fix()
        if self.extension is not None:
            if os.path.isfile(self.path + '.' + self.extension):
                os.remove(self.path + '.' + self.extension)
            try:
                os.symlink(self.path, self.path + '.' + self.extension)
            except:
                shutil.copyfile(self.path, self.path + '.' + self.extension)
        if finalize:
            self.finalize()

    def fetch_url(self, url, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(os.path.join(self.directory, filename), 'wb') as fp:
                    for chunk in r.iter_content(8192):
                        fp.write(chunk)
        except requests.exceptions.HTTPError as err:
            raise DAError("from_url: Error %s" % (str(err),))
        self.save()

    def fetch_url_post(self, url, post_args, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        r = requests.post(url_sanitize(url), data=post_args, timeout=600)
        if r.status_code != 200:
            raise DAError('fetch_url_post: retrieval from ' + url + 'failed')
        with open(os.path.join(self.directory, filename), 'wb') as fp:
            for block in r.iter_content(8192):
                fp.write(block)
        self.save()

    def size_in_bytes(self, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if cloud is not None and not self.fixed:
            key = cloud.search_key(str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename))
            if key is None or not key.does_exist:
                raise DAError("size_in_bytes: file " + filename + " in " + self.section + " did not exist")
            return key.size
        return os.path.getsize(os.path.join(self.directory, filename))

    def list_of_files(self):
        output = []
        if cloud is not None and not self.fixed:
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            for key in cloud.list_keys(prefix):
                output.append(os.path.join(*key.name[len(prefix):].split('/')))
        else:
            if os.path.isdir(self.directory):
                for filename in listfiles(self.directory):
                    output.append(filename)
        return sorted(output)

    def list_of_dirs(self):
        dir_list = set()
        for path in self.list_of_files():
            parts = path.split(os.sep)
            if len(parts) > 1:
                dir_list.add(parts[0])
        return sorted(list(dir_list))

    def copy_from(self, orig_path, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        # logmessage("Saving to " + os.path.join(self.directory, filename))
        new_file = os.path.join(self.directory, filename)
        new_file_dir = os.path.dirname(new_file)
        if not os.path.isdir(new_file_dir):
            os.makedirs(new_file_dir, exist_ok=True)
        shutil.copyfile(orig_path, new_file)
        if 'filename' not in kwargs:
            self.save()

    def get_modtime(self, **kwargs):
        filename = kwargs.get('filename', self.filename)
        # logmessage("Get modtime called with filename " + str(filename))
        if cloud is not None and not self.fixed:
            key_name = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)
            key = cloud.search_key(key_name)
            if key is None or not key.does_exist:
                raise DAError("get_modtime: file " + filename + " in " + self.section + " did not exist")
            # logmessage("Modtime for key " + key_name + " is now " + str(key.last_modified))
            return key.get_epoch_modtime()
        the_path = os.path.join(self.directory, filename)
        if not os.path.isfile(the_path):
            raise DAError("get_modtime: file " + filename + " in " + self.section + " did not exist")
        return os.path.getmtime(the_path)

    def write_content(self, content, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        the_directory = directory_for(self, kwargs.get('project', 'default'))
        if kwargs.get('binary', False):
            with open(os.path.join(the_directory, filename), 'wb') as ifile:
                ifile.write(content)
        else:
            with open(os.path.join(the_directory, filename), 'w', encoding='utf-8') as ifile:
                ifile.write(content)
        if kwargs.get('save', True):
            self.save()

    def write_as_json(self, obj, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        the_directory = directory_for(self, kwargs.get('project', 'default'))
        # logmessage("write_as_json: writing to " + os.path.join(self.directory, filename))
        with open(os.path.join(the_directory, filename), 'w', encoding='utf-8') as ifile:
            json.dump(obj, ifile, sort_keys=True, indent=2)
        if kwargs.get('save', True):
            self.save()

    def temp_url_for(self, **kwargs):
        if kwargs.get('_attachment', False):
            suffix = 'download'
        else:
            suffix = ''
        filename = kwargs.get('filename', self.filename)
        seconds = kwargs.get('seconds', None)
        if isinstance(seconds, float):
            seconds = int(seconds)
        if not isinstance(seconds, int):
            seconds = 30
        if cloud is not None and daconfig.get('use cloud urls', False):
            keyname = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)
            key = cloud.get_key(keyname)
            inline = not bool(kwargs.get('_attachment', False))
            if key.does_exist:
                return key.generate_url(seconds, display_filename=kwargs.get('display_filename', None), inline=inline, content_type=kwargs.get('content_type', None))
            logmessage("key " + str(keyname) + " did not exist")
            return 'about:blank'
        r = docassemble.base.functions.server.server_redis
        while True:
            code = random_alphanumeric(32)
            keyname = 'da:tempfile:' + code
            if r.setnx(keyname, str(self.section) + '^' + str(self.file_number)):
                r.expire(keyname, seconds)
                break
        use_external = kwargs.get('_external', bool('jsembed' in docassemble.base.functions.this_thread.misc))
        url = url_for('rootindex', _external=use_external).rstrip('/')
        url += '/tempfile' + suffix + '/' + code + '/' + urllib.parse.quote(path_to_key(kwargs.get('display_filename', filename)))
        return url

    def cloud_path(self, filename=None):
        if cloud is None:
            return None
        if filename is None:
            filename = self.filename
        return str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)

    def url_for(self, **kwargs):
        if 'ext' in kwargs and kwargs['ext'] is not None:
            extn = kwargs['ext']
            extn = re.sub(r'^\.', '', extn)
        else:
            extn = None
        filename = kwargs.get('filename', self.filename)
        if cloud is not None and not (self.section == 'files' and 'page' in kwargs and kwargs['page']) and daconfig.get('use cloud urls', False):
            keyname = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)
            page = kwargs.get('page', None)
            if page:
                size = kwargs.get('size', 'page')
                page = re.sub(r'[^0-9]', '', str(page))
                if size == 'screen':
                    keyname += 'screen-' + str(page) + '.png'
                else:
                    keyname += 'page-' + str(page) + '.png'
            elif extn:
                keyname += '.' + extn
            key = cloud.get_key(keyname)
            inline = not bool(kwargs.get('_attachment', False))
            if key.does_exist:
                return key.generate_url(3600, display_filename=kwargs.get('display_filename', None), inline=inline, content_type=kwargs.get('content_type', None))
            # why not serve right from uploadedpage in this case?
            logmessage("key " + str(keyname) + " did not exist")
            return 'about:blank'
        if kwargs.get('_attachment', False):
            suffix = 'download'
        else:
            suffix = ''
        use_external = kwargs.get('_external', bool('jsembed' in docassemble.base.functions.this_thread.misc))
        base_url = url_for('rootindex', _external=use_external).rstrip('/')
        if extn is None:
            extn = ''
        else:
            extn = '.' + extn
        filename = kwargs.get('display_filename', filename)
        if self.section == 'files':
            if 'page' in kwargs and kwargs['page']:
                page = re.sub(r'[^0-9]', '', str(kwargs['page']))
                size = kwargs.get('size', 'page')
                url = base_url + '/uploadedpage'
                if size == 'screen':
                    url += 'screen'
                url += suffix
                url += '/' + str(self.file_number) + '/' + str(page)
            else:
                if re.search(r'\.', str(filename)):
                    url = base_url + '/uploadedfile' + suffix + '/' + str(self.file_number) + '/' + urllib.parse.quote(path_to_key(filename))
                elif extn != '':
                    url = base_url + '/uploadedfile' + suffix + '/' + str(self.file_number) + '/' + urllib.parse.quote(path_to_key(filename) + extn)
                else:
                    url = base_url + '/uploadedfile' + suffix + '/' + str(self.file_number)
        else:
            logmessage("section " + self.section + " was wrong")
            url = 'about:blank'
        return url

    def finalize(self):
        # logmessage("finalize: starting " + str(self.section) + '/' + str(self.file_number))
        if cloud is None:
            return
        if not self.fixed:
            raise DAError("SavedFile: finalize called before fix")
        for filename in listfiles(self.directory):
            fullpath = os.path.join(self.directory, filename)
            # logmessage("Found " + fullpath)
            if os.path.isfile(fullpath):
                save = True
                if filename in self.keydict:
                    key = self.keydict[filename]
                    if self.modtimes[filename] == os.path.getmtime(fullpath):
                        save = False
                else:
                    key = cloud.get_key(str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename))
                if save:
                    if self.extension is not None and filename == self.filename:
                        extension, mimetype = get_ext_and_mimetype(filename + '.' + self.extension)  # pylint: disable=unused-variable
                    else:
                        extension, mimetype = get_ext_and_mimetype(filename)
                    key.content_type = mimetype
                    # logmessage("finalize: saving " + str(self.section) + '/' + str(self.file_number) + '/' + str(filename))
                    if not os.path.isfile(fullpath):
                        continue
                    try:
                        key.set_contents_from_filename(fullpath)
                        self.modtimes[filename] = key.get_epoch_modtime()
                    except FileNotFoundError:
                        logmessage("finalize: error while saving " + str(self.section) + '/' + str(self.file_number) + '/' + str(filename) + "; path " + str(fullpath) + " disappeared")
        for filename, key in self.keydict.items():
            if not os.path.isfile(os.path.join(self.directory, filename)):
                logmessage("finalize: deleting " + str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename))
                try:
                    key.delete()
                except:
                    pass
        # logmessage("finalize: ending " + str(self.section) + '/' + str(self.file_number))


def get_ext_and_mimetype(filename):
    mimetype, encoding = mimetypes.guess_type(filename)  # pylint: disable=unused-variable
    extension = filename.lower()
    extension = re.sub(r'.*\.', '', extension)
    if extension == "jpeg":
        extension = "jpg"
    if extension == "tiff":
        extension = "tif"
    if extension == '3gpp':
        mimetype = 'audio/3gpp'
    if extension in ('yaml', 'yml'):
        mimetype = 'text/plain'
    return (extension, mimetype)


def publish_package(pkgname, info, author_info, current_project='default'):
    directory = make_package_dir(pkgname, info, author_info, current_project=current_project)
    packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
    output = "Publishing docassemble." + pkgname + " to PyPI . . .\n\n"
    try:
        output += subprocess.check_output(['python', '-m', 'build', '.', '--sdist'], cwd=packagedir, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as err:
        output += err.output.decode()
    dist_dir = os.path.join(packagedir, 'dist')
    had_error = False
    if not os.path.isdir(dist_dir):
        output += "dist directory " + str(dist_dir) + " did not exist after calling sdist"
        had_error = True
    else:
        try:
            output += subprocess.check_output(['twine', 'upload', '--repository', 'pypi', '--username', str(current_user.pypi_username), '--password', str(current_user.pypi_password), os.path.join('dist', '*')], cwd=packagedir, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as err:
            output += "Error calling twine upload.\n"
            output += err.output.decode()
            had_error = True
    output = re.sub(r'\n', '<br>', output)
    shutil.rmtree(directory)
    logmessage(output)
    return (had_error, output)


def make_package_zip(pkgname, info, author_info, tz_name, current_project='default'):
    directory = make_package_dir(pkgname, info, author_info, current_project=current_project)
    trimlength = len(directory) + 1
    packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
    temp_zip = tempfile.NamedTemporaryFile(suffix=".zip")
    zf = zipfile.ZipFile(temp_zip, compression=zipfile.ZIP_DEFLATED, mode='w')
    the_timezone = zoneinfo.ZoneInfo(tz_name)
    for root, dirs, files in os.walk(packagedir):  # pylint: disable=unused-variable
        for file in files:
            thefilename = os.path.join(root, file)
            zinfo = zipfile.ZipInfo(thefilename[trimlength:], date_time=datetime.datetime.fromtimestamp(os.path.getmtime(thefilename), tz=datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).astimezone(the_timezone).timetuple())
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zinfo.external_attr = 0o644 << 16
            with open(thefilename, 'rb') as fp:
                zf.writestr(zinfo, fp.read())
    zf.close()
    shutil.rmtree(directory)
    return temp_zip


def get_package_identifier(package_name):
    from docassemble.webapp.package_info import retrieve_package_info  # pylint: disable=import-outside-toplevel
    package_info = retrieve_package_info(package_name)
    logmessage("package_info is " + repr(package_info))
    if package_info is not None and package_info['type'] == 'git':
        output = package_info['name'] + ' @ git+' + package_info['giturl'] + '.git'
        if package_info['gitbranch']:
            output += '@' + package_info['gitbranch']
        logmessage("returning " + repr(output))
        return output
    info = get_pip_info(package_name)
    if 'Version' in info:
        the_version = info['Version']
        if the_version is None:
            the_version = '1.0'
        installed_version = version.parse(the_version.strip())
        latest_release = None
        printable_latest_release = None
        try:
            r = requests.get("https://pypi.org/pypi/%s/json" % package_name, timeout=5)
            assert r.status_code == 200
            pypi_info = r.json()
            for the_version in pypi_info['releases'].keys():
                past_version = version.parse(the_version)
                if past_version <= installed_version and (latest_release is None or past_version > latest_release):
                    latest_release = past_version
                    printable_latest_release = the_version
                    if past_version == installed_version:
                        break
        except:
            pass
        if printable_latest_release:
            return package_name + '>=' + printable_latest_release
    return ''


def make_package_dir(pkgname, info, author_info, directory=None, current_project='default'):
    area = {}
    for sec in ['playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules']:
        area[sec] = SavedFile(author_info['id'], fix=True, section=sec)
    dependencies_list = [y for y in map(lambda x: get_package_identifier(x), sorted(info['dependencies'])) if y != ""]
    dependencies = ", ".join(map(lambda x: repr(x), dependencies_list))
    licensetext = str(info['license'])
    if re.search(r'MIT', licensetext):
        licensetext += '\n\nCopyright (c) ' + str(datetime.datetime.now().year) + ' ' + str(info.get('author_name', '')) + """

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    using_default = {'gitignore': False, 'readme': False}
    if info.get('gitignore') and re.search(r'[A-Za-z]', info['gitignore']):
        gitignore = str(info['gitignore'])
    else:
        gitignore = daconfig.get('default gitignore', DEFAULT_GITIGNORE)
        using_default['gitignore'] = True
    if info.get('readme') and re.search(r'[A-Za-z]', info['readme']):
        readme = str(info['readme'])
    else:
        readme = '# docassemble.' + str(pkgname) + "\n\n" + info['description'] + "\n\n## Author\n\n" + author_info['author name and email'] + "\n\n"
        using_default['readme'] = True
    the_license = str(info.get('license', 'MIT'))
    if not the_license:
        the_license = 'MIT'
    if the_license not in docassemble.webapp.spdx.LICENSES:
        if re.search(r'MIT', the_license):
            the_license = 'MIT'
        else:
            the_license = ''
    pyprojecttoml = tomli_w.dumps({'build-system': {'requires': ['setuptools>=80.9.0'], 'build-backend': 'setuptools.build_meta'}, 'project': {'name': f'docassemble.{pkgname}', 'version': info.get('version', '0.0.1'), 'description': info.get('description', 'A docassemble extension.'), 'readme': 'README.md', 'authors': [{'name': str(info.get('author_name', '')), 'email': str(info.get('author_email', ''))}], 'license': str(the_license), 'license-files': ['LICENSE'], 'dependencies': dependencies_list, 'urls': {'Homepage': info['url'] or 'https://docassemble.org'}}, 'tool': {'setuptools': {'packages': {'find': {'where': ['.']}}}}})

    manifestin = f"""\
include README.md
graft docassemble/{pkgname}/data
recursive-exclude * *.egg-info
recursive-exclude .git *
recursive-exclude venv *
recursive-exclude .github *
recursive-exclude .pytest_cache *
recursive-exclude .vscode *
recursive-exclude build *
recursive-exclude dist *
recursive-exclude * __pycache__
recursive-exclude * *.pyc
recursive-exclude * *.pyo
recursive-exclude * *.orig
recursive-exclude * *~
recursive-exclude * *.bak
recursive-exclude * *.swp
"""
    setupcfg = """\
[metadata]
long_description = file: README.md
"""
    setuppy = """\
import os
import sys
from setuptools import setup, find_namespace_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')

def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

"""
    setuppy += "setup(name='docassemble." + str(pkgname) + "',\n" + """\
      version=""" + repr(info.get('version', '')) + """,
      description=(""" + repr(info.get('description', '')) + """),
      long_description=""" + repr(readme) + """,
      long_description_content_type='text/markdown',
      author=""" + repr(info.get('author_name', '')) + """,
      author_email=""" + repr(info.get('author_email', '')) + """,
      license=""" + repr(info.get('license', '')) + """,
      url=""" + repr(info['url'] if info['url'] else 'https://docassemble.org') + """,
      packages=find_namespace_packages(),
      install_requires=[""" + dependencies + """],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/""" + str(pkgname) + """/', package='docassemble.""" + str(pkgname) + """'),
     )

"""
    templatereadme = """\
# Template directory

If you want to use templates for document assembly, put them in this directory.
"""
    staticreadme = """\
# Static file directory

If you want to make files available in the web app, put them in
this directory.
"""
    sourcesreadme = """\
# Sources directory

This directory is used to store word translation files,
machine learning training files, and other source files.
"""
    if directory is None:
        directory = tempfile.mkdtemp(prefix='SavedFile')
    packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
    maindir = os.path.join(packagedir, 'docassemble', str(pkgname))
    questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
    templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
    staticdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'static')
    sourcesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'sources')
    if not os.path.isdir(questionsdir):
        os.makedirs(questionsdir, exist_ok=True)
    if not os.path.isdir(templatesdir):
        os.makedirs(templatesdir, exist_ok=True)
    if not os.path.isdir(staticdir):
        os.makedirs(staticdir, exist_ok=True)
    if not os.path.isdir(sourcesdir):
        os.makedirs(sourcesdir, exist_ok=True)
    dir_questions = directory_for(area['playground'], current_project)
    dir_template = directory_for(area['playgroundtemplate'], current_project)
    dir_modules = directory_for(area['playgroundmodules'], current_project)
    dir_static = directory_for(area['playgroundstatic'], current_project)
    dir_sources = directory_for(area['playgroundsources'], current_project)
    for the_file in info['interview_files']:
        orig_file = os.path.join(dir_questions, the_file)
        if os.path.exists(orig_file):
            shutil.copy2(orig_file, os.path.join(questionsdir, the_file))
        else:
            logmessage("failure on " + orig_file)
    for the_file in info['template_files']:
        orig_file = os.path.join(dir_template, the_file)
        if os.path.exists(orig_file):
            shutil.copy2(orig_file, os.path.join(templatesdir, the_file))
        else:
            logmessage("failure on " + orig_file)
    for the_file in info['module_files']:
        orig_file = os.path.join(dir_modules, the_file)
        if os.path.exists(orig_file):
            shutil.copy2(orig_file, os.path.join(maindir, the_file))
        else:
            logmessage("failure on " + orig_file)
    for the_file in info['static_files']:
        orig_file = os.path.join(dir_static, the_file)
        if os.path.exists(orig_file):
            shutil.copy2(orig_file, os.path.join(staticdir, the_file))
        else:
            logmessage("failure on " + orig_file)
    for the_file in info['sources_files']:
        orig_file = os.path.join(dir_sources, the_file)
        if os.path.exists(orig_file):
            shutil.copy2(orig_file, os.path.join(sourcesdir, the_file))
        else:
            logmessage("failure on " + orig_file)
    if not using_default['gitignore'] or not os.path.isfile(os.path.join(packagedir, '.gitignore')):
        with open(os.path.join(packagedir, '.gitignore'), 'w', encoding='utf-8') as the_file:
            the_file.write(gitignore)
        os.utime(os.path.join(packagedir, '.gitignore'), (info['modtime'], info['modtime']))
    if not using_default['readme'] or not os.path.isfile(os.path.join(packagedir, 'README.md')):
        with open(os.path.join(packagedir, 'README.md'), 'w', encoding='utf-8') as the_file:
            the_file.write(readme)
        os.utime(os.path.join(packagedir, 'README.md'), (info['modtime'], info['modtime']))
    with open(os.path.join(packagedir, 'LICENSE'), 'w', encoding='utf-8') as the_file:
        the_file.write(licensetext)
    os.utime(os.path.join(packagedir, 'LICENSE'), (info['modtime'], info['modtime']))
    with open(os.path.join(packagedir, 'setup.py'), 'w', encoding='utf-8') as the_file:
        the_file.write(setuppy)
    os.utime(os.path.join(packagedir, 'setup.py'), (info['modtime'], info['modtime']))
    with open(os.path.join(packagedir, 'setup.cfg'), 'w', encoding='utf-8') as the_file:
        the_file.write(setupcfg)
    os.utime(os.path.join(packagedir, 'setup.cfg'), (info['modtime'], info['modtime']))
    with open(os.path.join(packagedir, 'MANIFEST.in'), 'w', encoding='utf-8') as the_file:
        the_file.write(manifestin)
    os.utime(os.path.join(packagedir, 'MANIFEST.in'), (info['modtime'], info['modtime']))
    with open(os.path.join(packagedir, 'pyproject.toml'), 'w', encoding='utf-8') as the_file:
        the_file.write(pyprojecttoml)
    os.utime(os.path.join(packagedir, 'pyproject.toml'), (info['modtime'], info['modtime']))
    with open(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), 'w', encoding='utf-8') as the_file:
        the_file.write("__version__ = " + repr(info.get('version', '')) + "\n")
    os.utime(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), (info['modtime'], info['modtime']))
    with open(os.path.join(templatesdir, 'README.md'), 'w', encoding='utf-8') as the_file:
        the_file.write(templatereadme)
    os.utime(os.path.join(templatesdir, 'README.md'), (info['modtime'], info['modtime']))
    with open(os.path.join(staticdir, 'README.md'), 'w', encoding='utf-8') as the_file:
        the_file.write(staticreadme)
    os.utime(os.path.join(staticdir, 'README.md'), (info['modtime'], info['modtime']))
    with open(os.path.join(sourcesdir, 'README.md'), 'w', encoding='utf-8') as the_file:
        the_file.write(sourcesreadme)
    os.utime(os.path.join(sourcesdir, 'README.md'), (info['modtime'], info['modtime']))
    return directory


def directory_for(area, current_project):
    if current_project == 'default':
        return area.directory
    return os.path.join(area.directory, current_project)


def update_access_time(filepath):
    with open(filepath, "rb") as fp:
        fp.seek(0, 0)
        fp.read(1)
