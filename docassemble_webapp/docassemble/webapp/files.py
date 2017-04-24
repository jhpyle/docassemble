import os
import re
import shutil
import urllib
import pycurl
import tempfile
import mimetypes
import zipfile
import datetime
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
from docassemble.base.config import daconfig
import docassemble.webapp.cloud

cloud = docassemble.webapp.cloud.get_cloud()

UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')

class SavedFile(object):
    def __init__(self, file_number, extension=None, fix=False, section='files', filename='file'):
        self.file_number = file_number
        self.extension = extension
        self.fixed = False
        self.section = section
        self.filename = filename
        if cloud is None:
            if self.section == 'files':
                parts = re.sub(r'(...)', r'\1/', '{0:012x}'.format(int(file_number))).split('/')
                self.directory = os.path.join(UPLOAD_DIRECTORY, *parts)
            else:
                self.directory = os.path.join(UPLOAD_DIRECTORY, str(self.section), str(file_number))
            self.path = os.path.join(self.directory, filename)
        if fix:
            self.fix()
    # def __del__(self):
    #     logmessage("Deleting a file")
    #     if cloud is not None and hasattr(self, 'directory') and os.path.isdir(self.directory):
    #         pass
            #shutil.rmtree(self.directory)
    def fix(self):
        if self.fixed:
            return
        if cloud is not None:
            self.modtimes = dict()
            self.keydict = dict()
            self.directory = tempfile.mkdtemp(prefix='SavedFile')
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            #logmessage("fix: prefix is " + prefix)
            for key in cloud.list_keys(prefix):
                filename = re.sub(r'.*/', '', key.name)
                fullpath = os.path.join(self.directory, filename)
                #logmessage("fix: saving to " + fullpath)
                key.get_contents_to_filename(fullpath)
                self.modtimes[filename] = os.path.getmtime(fullpath)
                #logmessage("cloud modtime for file " + filename + " is " + str(key.last_modified))
                self.keydict[filename] = key
            self.path = os.path.join(self.directory, self.filename)
        else:
            if not os.path.isdir(self.directory):
                os.makedirs(self.directory)        
        self.fixed = True
    def delete(self):
        if cloud is not None:
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            for key in cloud.list_keys(prefix):
                key.delete()
        if hasattr(self, 'directory') and os.path.isdir(self.directory):
            shutil.rmtree(self.directory)
    def save(self, finalize=False):
        if not self.fixed:
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
        if not self.fixed:
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
        # cookiejar = cookielib.LWPCookieJar()
        # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        # response = opener.open(url)
        # f = open(os.path.join(self.directory, filename), 'wb')
        # block_sz = 8192
        # while True:
        #     buffer = u.read(block_sz)
        #     if not buffer:
        #         break

        #     f.write(buffer)
        # f.close()
        #urllib.urlretrieve(url, os.path.join(self.directory, filename))
        self.save()
        return
    def fetch_url_post(self, url, post_args, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if not self.fixed:
            self.fix()
        urllib.urlretrieve(url, os.path.join(self.directory, filename), None, urllib.urlencode(post_args))
        self.save()
        return
    def size_in_bytes(self, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if cloud is not None and not self.fixed:
            key = cloud.search_key(str(self.section) + '/' + str(self.file_number) + '/' + str(filename))
            return key.size
        else:
            return os.path.getsize(os.path.join(self.directory, filename))
    def copy_from(self, orig_path, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if not self.fixed:
            self.fix()
        shutil.copyfile(orig_path, os.path.join(self.directory, filename))
        self.save()
        return
    def get_modtime(self, **kwargs):
        filename = kwargs.get('filename', self.filename)
        #logmessage("Get modtime called with filename " + str(filename))
        if cloud is not None:
            key_name = str(self.section) + '/' + str(self.file_number) + '/' + str(filename)
            key = cloud.search_key(key_name)
            #logmessage("Modtime for key " + key_name + " is now " + str(key.last_modified))
            return key.last_modified
        else:
            return os.path.getmtime(os.path.join(self.directory, filename))
    def write_content(self, content, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if not self.fixed:
            self.fix()
        with open(os.path.join(self.directory, filename), 'wb') as ifile:
            ifile.write(content)
        if kwargs.get('save', True):
            self.save()
        return
    def url_for(self, **kwargs):
        if 'ext' in kwargs:
            extn = kwargs['ext']
            extn = re.sub(r'^\.', '', extn)
        else:
            extn = None
        filename = kwargs.get('filename', self.filename)
        if cloud is not None:
            keyname = str(self.section) + '/' + str(self.file_number) + '/' + str(filename)
            page = kwargs.get('page', None)
            if page:
                size = kwargs.get('size', 'page')
                page = re.sub(r'[^0-9]', '', page)
                if size == 'screen':
                    keyname += 'screen-' + str(page) + '.png'
                else:
                    keyname += 'page-' + str(page) + '.png'
            elif extn:
                keyname += '.' + extn
            key = cloud.get_key(keyname)
            if key.exists():
                return(key.generate_url(3600))
            else:
                return('about:blank')
        else:
            if extn is None:
                extn = ''
            else:
                extn = '.' + extn
            root = daconfig.get('root', '/')
            fileroot = daconfig.get('fileserver', root)
            if self.section == 'files':
                if 'page' in kwargs and kwargs['page']:
                    page = re.sub(r'[^0-9]', '', str(kwargs['page']))
                    size = kwargs.get('size', 'page')
                    url = fileroot + 'uploadedpage'
                    if size == 'screen':
                        url += 'screen'
                    url += '/' + str(self.file_number) + '/' + str(page)
                else:
                    url = fileroot + 'uploadedfile/' + str(self.file_number) + extn
            else:
                url = 'about:blank'
            return(url)
    def finalize(self):
        if cloud is None:
            return
        if not self.fixed:
            raise DAError("SavedFile: finalize called before fix")
        existing_files = list()
        for filename in os.listdir(self.directory):
            existing_files.append(filename)
            fullpath = os.path.join(self.directory, filename)
            #logmessage("Found " + fullpath)
            if os.path.isfile(fullpath):
                save = True
                if filename in self.keydict:
                    key = self.keydict[filename]
                    if self.modtimes[filename] == os.path.getmtime(fullpath):
                        save = False
                else:
                    key = cloud.get_key(str(self.section) + '/' + str(self.file_number) + '/' + str(filename))
                    if filename == self.filename:
                        extension, mimetype = get_ext_and_mimetype(filename + '.' + self.extension)
                        key.content_type = mimetype
                if save:
                    key.set_contents_from_filename(fullpath)
        for filename, key in self.keydict.iteritems():
            if filename not in existing_files:
                logmessage("Deleting filename " + str(filename) + " from cloud")
                key.delete()
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
    return(extension, mimetype)

def make_package_zip(pkgname, info, author_info):
    temp_zip = tempfile.NamedTemporaryFile(suffix=".zip")
    area = dict()
    for sec in ['playground', 'playgroundtemplate', 'playgroundstatic', 'playgroundsources', 'playgroundmodules']:
        area[sec] = SavedFile(author_info['id'], fix=True, section=sec)
    dependencies = ", ".join(map(lambda x: repr(x), sorted(info['dependencies'])))
    dependency_links = ", ".join(map(lambda x: repr(x), sorted(info['dependency_links'])))
    initpy = """\
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    __path__ = __import__('pkgutil').extend_path(__path__, __name__)

"""
    licensetext = info['license']
    if re.search(r'MIT License', licensetext):
        licensetext += '\n\nCopyright (c) ' + str(datetime.datetime.now().year) + ' ' + unicode(author_info['first name']) + " " + unicode(author_info['last name']) + """

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
        readme = info['readme']
    else:
        readme = '# docassemble.' + str(pkgname) + "\n\n" + info['description'] + "\n\n## Author\n\n" + author_info['author name and email'] + "\n\n"
    setuppy = """\
#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
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
      version=""" + repr(info['version']) + """,
      description=(""" + repr(info['description']) + """),
      author=""" + repr(author_info['author name']) + """,
      author_email=""" + repr(author_info['author email']) + """,
      license=""" + repr(info['license']) + """,
      url=""" + repr(info['url']) + """,
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=[""" + dependencies + """],
      dependency_links=[""" + dependency_links + """],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/""" + str(pkgname) + """/', package='docassemble.""" + str(pkgname) + """'),
     )

"""
    templatereadme = """\
# Template directory

If you want to use non-standard document templates with pandoc,
put template files in this directory.
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
    directory = tempfile.mkdtemp()
    packagedir = os.path.join(directory, 'docassemble-' + str(pkgname))
    maindir = os.path.join(packagedir, 'docassemble', str(pkgname))
    questionsdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'questions')
    templatesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'templates')
    staticdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'static')
    sourcesdir = os.path.join(packagedir, 'docassemble', str(pkgname), 'data', 'sources')
    os.makedirs(questionsdir)
    os.makedirs(templatesdir)
    os.makedirs(staticdir)
    os.makedirs(sourcesdir)
    for the_file in info['interview_files']:
        orig_file = os.path.join(area['playground'].directory, the_file)
        if os.path.exists(orig_file):
            shutil.copyfile(orig_file, os.path.join(questionsdir, the_file))
    for the_file in info['template_files']:
        orig_file = os.path.join(area['playgroundtemplate'].directory, the_file)
        if os.path.exists(orig_file):
            shutil.copyfile(orig_file, os.path.join(templatesdir, the_file))
    for the_file in info['module_files']:
        orig_file = os.path.join(area['playgroundmodules'].directory, the_file)
        if os.path.exists(orig_file):
            shutil.copyfile(orig_file, os.path.join(maindir, the_file))
    for the_file in info['static_files']:
        orig_file = os.path.join(area['playgroundstatic'].directory, the_file)
        if os.path.exists(orig_file):
            shutil.copyfile(orig_file, os.path.join(staticdir, the_file))
    for the_file in info['sources_files']:
        orig_file = os.path.join(area['playgroundsources'].directory, the_file)
        if os.path.exists(orig_file):
            shutil.copyfile(orig_file, os.path.join(sourcesdir, the_file))
    with open(os.path.join(packagedir, 'README.md'), 'a') as the_file:
        the_file.write(readme)
    with open(os.path.join(packagedir, 'LICENSE'), 'a') as the_file:
        the_file.write(licensetext)
    with open(os.path.join(packagedir, 'setup.py'), 'a') as the_file:
        the_file.write(setuppy)
    with open(os.path.join(packagedir, 'docassemble', '__init__.py'), 'a') as the_file:
        the_file.write(initpy)
    with open(os.path.join(packagedir, 'docassemble', pkgname, '__init__.py'), 'a') as the_file:
        the_file.write('')
    with open(os.path.join(templatesdir, 'README.md'), 'a') as the_file:
        the_file.write(templatereadme)
    with open(os.path.join(staticdir, 'README.md'), 'a') as the_file:
        the_file.write(staticreadme)
    with open(os.path.join(sourcesdir, 'README.md'), 'a') as the_file:
        the_file.write(sourcesreadme)
    zf = zipfile.ZipFile(temp_zip.name, mode='w')
    trimlength = len(directory) + 1
    for root, dirs, files in os.walk(packagedir):
        for file in files:
            thefilename = os.path.join(root, file)
            zf.write(thefilename, thefilename[trimlength:])
    zf.close()
    shutil.rmtree(directory)
    return temp_zip
