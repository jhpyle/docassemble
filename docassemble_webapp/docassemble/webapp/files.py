import sys
import os
import re
import json
import pytz
import shutil
import requests
import pycurl
import tempfile
import mimetypes
import zipfile
import datetime
import subprocess
import time
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
from docassemble.base.config import daconfig
import docassemble.webapp.cloud
import docassemble.base.functions
from docassemble.base.generate_key import random_alphanumeric
from distutils.version import LooseVersion

cloud = docassemble.webapp.cloud.get_cloud()

UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')

def listfiles(directory):
    result = list()
    directory = directory.rstrip(os.sep)
    trimstart = len(directory) + 1
    for root, dirs, files in os.walk(directory):
        for filename in files:
            result.append(os.path.join(root, filename)[trimstart:])
    return result

def listdirs(directory):
    result = list()
    directory = directory.rstrip(os.sep)
    trimstart = len(directory) + 1
    for root, dirs, files in os.walk(directory):
        for subdir in dirs:
            result.append(os.path.join(root, subdir)[trimstart:])
    return result

def path_to_key(path):
    return '/'.join(str(path).split(os.sep))

def url_sanitize(url):
    return re.sub(r'\s', ' ', url)

class SavedFile:
    def __init__(self, file_number, extension=None, fix=False, section='files', filename='file', project=None, subdir=None):
        file_number = int(file_number)
        section = str(section)
        if section not in docassemble.base.functions.this_thread.saved_files:
            docassemble.base.functions.this_thread.saved_files[section] = dict()
        if file_number in docassemble.base.functions.this_thread.saved_files[section]:
            # sys.stderr.write("SavedFile: using cache for " + section + '/' + str(file_number) + "\n")
            sf = docassemble.base.functions.this_thread.saved_files[section][file_number]
            for attribute in ['file_number', 'fixed', 'section', 'filename', 'extension', 'directory', 'path', 'modtimes', 'keydict', 'subdir']:
                if hasattr(sf, attribute):
                    setattr(self, attribute, getattr(sf, attribute))
            self.extension = extension
            self.filename = filename
            self.subdir = subdir
        else:
            # sys.stderr.write("SavedFile: not using cache for " + section + '/' + str(file_number) + "\n")
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
            self.fix()
    def fix(self):
        if self.fixed:
            return
        # sys.stderr.write("fix: starting " + str(self.section) + '/' + str(self.file_number) + "\n")
        if cloud is not None:
            dirs_in_use = set()
            self.modtimes = dict()
            self.keydict = dict()
            if not os.path.isdir(self.directory):
                os.makedirs(self.directory)
            #self.directory = tempfile.mkdtemp(prefix='SavedFile')
            #docassemble.base.functions.this_thread.temporary_resources.add(self.directory)
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            #sys.stderr.write("fix: prefix is " + prefix + "\n")
            for key in cloud.list_keys(prefix):
                filename = os.path.join(*key.name[len(prefix):].split('/'))
                fullpath = os.path.join(self.directory, filename)
                fulldir = os.path.dirname(fullpath)
                dirs_in_use.add(fulldir)
                if not os.path.isdir(fulldir):
                    os.makedirs(fulldir)
                server_time = key.get_epoch_modtime()
                if not os.path.isfile(fullpath):
                    key.get_contents_to_filename(fullpath)
                else:
                    local_time = os.path.getmtime(fullpath)
                    access_time = os.path.getatime(fullpath)
                    if self.section == 'files':
                        if local_time != server_time:
                            key.get_contents_to_filename(fullpath)
                        update_access_time(fullpath)
                    else:
                        if not (local_time == server_time):
                            key.get_contents_to_filename(fullpath)
                self.modtimes[filename] = server_time

                #logmessage("cloud modtime for file " + filename + " is " + str(key.last_modified))
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
            if not os.path.isdir(self.directory):
                os.makedirs(self.directory)
        self.fixed = True
        # sys.stderr.write("fix: ending " + str(self.section) + '/' + str(self.file_number) + "\n")
    def delete_file(self, filename):
        if cloud is not None:
            prefix = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)
            to_delete = list()
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
            prefix = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(directory)
            to_delete = list()
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
            for key in [x for x in cloud.list_keys(prefix)]:
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
        return
    def fetch_url(self, url, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        cookiefile = tempfile.NamedTemporaryFile(suffix='.txt')
        f = open(os.path.join(self.directory, filename), 'wb')
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.WRITEDATA, f)
        c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36')
        c.setopt(pycurl.COOKIEFILE, cookiefile.name)
        c.perform()
        c.close()
        cookiefile.close()
        self.save()
        return
    def fetch_url_post(self, url, post_args, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        r = requests.post(url_sanitize(url), data=post_args)
        if r.status_code != 200:
            raise DAError('fetch_url_post: retrieval from ' + url + 'failed')
        with open(os.path.join(self.directory, filename), 'wb') as fp:
            for block in r.iter_content(1024):
                fp.write(block)
        self.save()
        return
    def size_in_bytes(self, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if cloud is not None and not self.fixed:
            key = cloud.search_key(str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename))
            if key is None or not key.does_exist:
                raise DAError("size_in_bytes: file " + filename + " in " + self.section + " did not exist")
            return key.size
        else:
            return os.path.getsize(os.path.join(self.directory, filename))
    def list_of_files(self):
        output = list()
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
        #logmessage("Saving to " + os.path.join(self.directory, filename))
        new_file = os.path.join(self.directory, filename)
        new_file_dir = os.path.dirname(new_file)
        if not os.path.isdir(new_file_dir):
            os.path.makedirs(new_file_dir)
        shutil.copyfile(orig_path, new_file)
        if 'filename' not in kwargs:
            self.save()
    def get_modtime(self, **kwargs):
        filename = kwargs.get('filename', self.filename)
        #logmessage("Get modtime called with filename " + str(filename))
        if cloud is not None and not self.fixed:
            key_name = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)
            key = cloud.search_key(key_name)
            if key is None or not key.does_exist:
                raise DAError("get_modtime: file " + filename + " in " + self.section + " did not exist")
            #logmessage("Modtime for key " + key_name + " is now " + str(key.last_modified))
            #return key.last_modified
            return key.get_epoch_modtime()
        else:
            the_path = os.path.join(self.directory, filename)
            if not os.path.isfile(the_path):
                raise DAError("get_modtime: file " + filename + " in " + self.section + " did not exist")
            return os.path.getmtime(the_path)
    def write_content(self, content, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        if kwargs.get('binary', False):
            with open(os.path.join(self.directory, filename), 'wb') as ifile:
                ifile.write(content)
        else:
            with open(os.path.join(self.directory, filename), 'w', encoding='utf-8') as ifile:
                ifile.write(content)
        if kwargs.get('save', True):
            self.save()
        return
    def write_as_json(self, obj, **kwargs):
        filename = kwargs.get('filename', self.filename)
        self.fix()
        #logmessage("write_as_json: writing to " + os.path.join(self.directory, filename))
        with open(os.path.join(self.directory, filename), 'w', encoding='utf-8') as ifile:
            json.dump(obj, ifile, sort_keys=True, indent=2)
        if kwargs.get('save', True):
            self.save()
        return
    def temp_url_for(self, **kwargs):
        if kwargs.get('_attachment', False):
            suffix = 'download'
        else:
            suffix = ''
        filename = kwargs.get('filename', self.filename)
        seconds = kwargs.get('seconds', None)
        if type(seconds) is float:
            seconds = int(seconds)
        if type(seconds) is not int:
            seconds = 30
        if cloud is not None and daconfig.get('use cloud urls', False):
            keyname = str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename)
            key = cloud.get_key(keyname)
            inline = False if kwargs.get('_attachment', False) else True
            if key.does_exist:
                return key.generate_url(seconds, display_filename=kwargs.get('display_filename', None), inline=inline, content_type=kwargs.get('content_type', None))
            else:
                sys.stderr.write("key " + str(keyname) + " did not exist\n")
                return('about:blank')
        r = docassemble.base.functions.server.server_redis
        while True:
            code = random_alphanumeric(32)
            keyname = 'da:tempfile:' + code
            if r.setnx(keyname, str(self.section) + '^' + str(self.file_number)):
                r.expire(keyname, seconds)
                break
        use_external = kwargs.get('_external', True if 'jsembed' in docassemble.base.functions.this_thread.misc else False)
        from flask import url_for
        url = url_for('rootindex', _external=use_external).rstrip('/')
        url += '/tempfile' + suffix + '/' + code + '/' + path_to_key(kwargs.get('display_filename', filename))
        return(url)
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
            inline = False if kwargs.get('_attachment', False) else True
            if key.does_exist:
                return key.generate_url(3600, display_filename=kwargs.get('display_filename', None), inline=inline, content_type=kwargs.get('content_type', None))
            else:
                #logmessage("Key " + str(keyname) + " did not exist")
                #why not serve right from uploadedpage in this case?
                sys.stderr.write("key " + str(keyname) + " did not exist\n")
                return('about:blank')
        else:
            if kwargs.get('_attachment', False):
                suffix = 'download'
            else:
                suffix = ''
            use_external = kwargs.get('_external', True if 'jsembed' in docassemble.base.functions.this_thread.misc else False)
            from flask import url_for
            base_url = url_for('rootindex', _external=use_external).rstrip('/')
            if extn is None:
                extn = ''
            else:
                extn = '.' + extn
            if 'display_filename' in kwargs:
                filename = kwargs['display_filename']
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
                        url = base_url + '/uploadedfile' + suffix + '/' + str(self.file_number) + '/' + path_to_key(filename)
                    elif extn != '':
                        url = base_url + '/uploadedfile' + suffix + '/' + str(self.file_number) + '/' + path_to_key(filename) + extn
                    else:
                        url = base_url + '/uploadedfile' + suffix + '/' + str(self.file_number)
            else:
                sys.stderr.write("section " + section + " was wrong\n")
                url = 'about:blank'
            return(url)
    def finalize(self):
        #sys.stderr.write("finalize: starting " + str(self.section) + '/' + str(self.file_number) + "\n")
        if cloud is None:
            return
        if not self.fixed:
            raise DAError("SavedFile: finalize called before fix")
        for filename in listfiles(self.directory):
            fullpath = os.path.join(self.directory, filename)
            #logmessage("Found " + fullpath)
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
                        extension, mimetype = get_ext_and_mimetype(filename + '.' + self.extension)
                    else:
                        extension, mimetype = get_ext_and_mimetype(filename)
                    key.content_type = mimetype
                    #sys.stderr.write("finalize: saving " + str(self.section) + '/' + str(self.file_number) + '/' + str(filename) + "\n")
                    if not os.path.isfile(fullpath):
                        continue
                    try:
                        key.set_contents_from_filename(fullpath)
                        self.modtimes[filename] = key.get_epoch_modtime()
                    except FileNotFoundError:
                        sys.stderr.write("finalize: error while saving " + str(self.section) + '/' + str(self.file_number) + '/' + str(filename) + "; path " + str(fullpath) + " disappeared\n")
        for filename, key in self.keydict.items():
            if not os.path.isfile(os.path.join(self.directory, filename)):
                sys.stderr.write("finalize: deleting " + str(self.section) + '/' + str(self.file_number) + '/' + path_to_key(filename) + "\n")
                try:
                    key.delete()
                except:
                    pass
        #sys.stderr.write("finalize: ending " + str(self.section) + '/' + str(self.file_number) + "\n")
        return

def get_ext_and_mimetype(filename):
    mimetype, encoding = mimetypes.guess_type(filename)
    extension = filename.lower()
    extension = re.sub('.*\.', '', extension)
    if extension == "jpeg":
        extension = "jpg"
    if extension == "tiff":
        extension = "tif"
    if extension == '3gpp':
        mimetype = 'audio/3gpp'
    if extension in ('yaml', 'yml'):
        mimetype = 'text/plain'
    return(extension, mimetype)

def publish_package(pkgname, info, author_info, tz_name, current_project='default'):
    from flask_login import current_user
    #raise Exception("email is " + repr(current_user.email) + " and pypi is " + repr(current_user.pypi_username))
    directory = make_package_dir(pkgname, info, author_info, tz_name, current_project=current_project)
    packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
    output = "Publishing docassemble." + pkgname + " to PyPI . . .\n\n"
    try:
        output += subprocess.check_output(['python', 'setup.py', 'sdist'], cwd=packagedir, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as err:
        output += err.output.decode()
    dist_file = None
    dist_dir = os.path.join(packagedir, 'dist')
    had_error = False
    if not os.path.isdir(dist_dir):
        output += "dist directory " + str(dist_dir) + " did not exist after calling sdist"
        had_error = True
    else:
        # for f in os.listdir(dist_dir):
        #     try:
        #         #output += str(['twine', 'register', '--repository', 'pypi', '--username', str(current_user.pypi_username), '--password', str(current_user.pypi_password), os.path.join('dist', f)]) + "\n"
        #         #raise Exception(repr(['twine', 'register', '--repository', 'pypi', '--username', str(current_user.pypi_username), '--password', str(current_user.pypi_password), os.path.join('dist', f)]))
        #         output += subprocess.check_output(['twine', 'register', '--repository', 'pypi', '--username', str(current_user.pypi_username), '--password', str(current_user.pypi_password), os.path.join('dist', f)], cwd=packagedir, stderr=subprocess.STDOUT)
        #     except subprocess.CalledProcessError as err:
        #         output += "Error calling twine register.\n"
        #         output += err.output
        try:
            #output += str(['twine', 'upload', '--repository', 'pypi', '--username', str(current_user.pypi_username), '--password', str(current_user.pypi_password), os.path.join('dist', '*')])
            output += subprocess.check_output(['twine', 'upload', '--repository', 'pypi', '--username', str(current_user.pypi_username), '--password', str(current_user.pypi_password), os.path.join('dist', '*')], cwd=packagedir, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as err:
            output += "Error calling twine upload.\n"
            output += err.output.decode()
            had_error = True
    output = re.sub(r'\n', '<br>', output)
    shutil.rmtree(directory)
    logmessage(output)
    return had_error, output

def make_package_zip(pkgname, info, author_info, tz_name, current_project='default'):
    directory = make_package_dir(pkgname, info, author_info, tz_name, current_project=current_project)
    trimlength = len(directory) + 1
    packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
    temp_zip = tempfile.NamedTemporaryFile(suffix=".zip")
    zf = zipfile.ZipFile(temp_zip.name, mode='w')
    the_timezone = pytz.timezone(tz_name)
    for root, dirs, files in os.walk(packagedir):
        for file in files:
            thefilename = os.path.join(root, file)
            zinfo = zipfile.ZipInfo(thefilename[trimlength:], date_time=datetime.datetime.utcfromtimestamp(os.path.getmtime(thefilename)).replace(tzinfo=pytz.utc).astimezone(the_timezone).timetuple())
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zinfo.external_attr = 0o644 << 16
            with open(thefilename, 'rb') as fp:
                zf.writestr(zinfo, fp.read())
            #zf.write(thefilename, thefilename[trimlength:])
    zf.close()
    shutil.rmtree(directory)
    return temp_zip

def get_version_suffix(package_name):
    from docassemble.webapp.update import get_pip_info
    info = get_pip_info(package_name)
    if 'Version' in info:
        installed_version = LooseVersion(info['Version'].strip())
        latest_release = None
        printable_latest_release = None
        try:
            r = requests.get("https://pypi.org/pypi/%s/json" % package_name, timeout=5)
            assert r.status_code == 200
            pypi_info = r.json()
            for the_version in pypi_info['releases'].keys():
                past_version = LooseVersion(the_version)
                if past_version <= installed_version and (latest_release is None or past_version > latest_release):
                    latest_release = past_version
                    printable_latest_release = the_version
                    if past_version == installed_version:
                        break
        except:
            pass
        if printable_latest_release:
            return '>=' + printable_latest_release
    return ''

def make_package_dir(pkgname, info, author_info, tz_name, directory=None, current_project='default'):
    the_timezone = pytz.timezone(tz_name)
    area = dict()
    for sec in ['playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules']:
        area[sec] = SavedFile(author_info['id'], fix=True, section=sec)
    dependencies = ", ".join(map(lambda x: repr(x + get_version_suffix(x)), sorted(info['dependencies'])))
    initpy = """\
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

"""
    licensetext = str(info['license'])
    if re.search(r'MIT License', licensetext):
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
    if info['readme'] and re.search(r'[A-Za-z]', info['readme']):
        readme = str(info['readme'])
    else:
        readme = '# docassemble.' + str(pkgname) + "\n\n" + info['description'] + "\n\n## Author\n\n" + author_info['author name and email'] + "\n\n"
    manifestin = """\
include README.md
"""
    setupcfg = """\
[metadata]
description-file = README.md
"""
    setuppy = """\
import os
import sys
from setuptools import setup, find_packages
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
      packages=find_packages(),
      namespace_packages=['docassemble'],
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
        directory = tempfile.mkdtemp()
        #docassemble.base.functions.this_thread.temporary_resources.add(directory)
    packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
    maindir = os.path.join(packagedir, 'docassemble', str(pkgname))
    questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
    templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
    staticdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'static')
    sourcesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'sources')
    if not os.path.isdir(questionsdir):
        os.makedirs(questionsdir)
    if not os.path.isdir(templatesdir):
        os.makedirs(templatesdir)
    if not os.path.isdir(staticdir):
        os.makedirs(staticdir)
    if not os.path.isdir(sourcesdir):
        os.makedirs(sourcesdir)
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
    with open(os.path.join(packagedir, 'docassemble', '__init__.py'), 'w', encoding='utf-8') as the_file:
        the_file.write(initpy)
    os.utime(os.path.join(packagedir, 'docassemble', '__init__.py'), (info['modtime'], info['modtime']))
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
    else:
        return os.path.join(area.directory, current_project)

def update_access_time(filepath):
    with open(filepath, "rb") as fp:
        fp.seek(0, 0)
        first_byte = fp.read(1)
