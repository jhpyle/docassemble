import os
import re
import shutil
import urllib
import tempfile
import mimetypes
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
from docassemble.webapp.config import daconfig, s3_config, S3_ENABLED, gc_config, GC_ENABLED

if S3_ENABLED:
    import docassemble.webapp.amazon
    s3 = docassemble.webapp.amazon.s3object(s3_config)

UPLOAD_DIRECTORY = daconfig.get('uploads', '/usr/share/docassemble/files')

class SavedFile(object):
    def __init__(self, file_number, extension=None, fix=False, section='files', filename='file'):
        self.file_number = file_number
        self.extension = extension
        self.fixed = False
        self.section = section
        self.filename = filename
        if not S3_ENABLED:
            if self.section == 'files':
                parts = re.sub(r'(...)', r'\1/', '{0:012x}'.format(int(file_number))).split('/')
                self.directory = os.path.join(UPLOAD_DIRECTORY, *parts)
            else:
                self.directory = os.path.join(UPLOAD_DIRECTORY, str(self.section), str(file_number))
            self.path = os.path.join(self.directory, filename)
        if fix:
            self.fix()
    def fix(self):
        if self.fixed:
            return
        if S3_ENABLED:
            self.modtimes = dict()
            self.keydict = dict()
            self.directory = tempfile.mkdtemp()
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            #logmessage("fix: prefix is " + prefix)
            for key in s3.bucket.list(prefix=prefix, delimiter='/'):
                filename = re.sub(r'.*/', '', key.name)
                fullpath = os.path.join(self.directory, filename)
                #logmessage("fix: saving to " + fullpath)
                key.get_contents_to_filename(fullpath)
                self.modtimes[filename] = os.path.getmtime(fullpath)
                #logmessage("S3 modtime for file " + filename + " is " + str(key.last_modified))
                self.keydict[filename] = key
            self.path = os.path.join(self.directory, self.filename)
        else:
            if not os.path.isdir(self.directory):
                os.makedirs(self.directory)        
        self.fixed = True
    def delete(self):
        if S3_ENABLED:
            prefix = str(self.section) + '/' + str(self.file_number) + '/'
            for key in s3.bucket.list(prefix=prefix, delimiter='/'):
                key.delete()
        else:
            if os.path.isdir(self.directory):
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
        urllib.urlretrieve(url, os.path.join(self.directory, filename))
        self.save()
        return
    def size_in_bytes(self, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if S3_ENABLED and not self.fixed:
            key = s3.search_key(str(self.section) + '/' + str(self.file_number) + '/' + str(filename))
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
        if S3_ENABLED:
            key_name = str(self.section) + '/' + str(self.file_number) + '/' + str(filename)
            key = s3.search_key(key_name)
            #logmessage("Modtime for key " + key_name + " is now " + str(key.last_modified))
            return key.last_modified
        else:
            return os.path.getmtime(os.path.join(self.directory, filename))
    def write_content(self, content, **kwargs):
        filename = kwargs.get('filename', self.filename)
        if not self.fixed:
            self.fix()
        with open(os.path.join(self.directory, filename), 'w') as ifile:
            ifile.write(content)
        self.save()
        return
    def url_for(self, **kwargs):
        if 'ext' in kwargs:
            extn = kwargs['ext']
            extn = re.sub(r'^\.', '', extn)
        else:
            extn = None
        filename = kwargs.get('filename', self.filename)
        if S3_ENABLED:
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
            key = s3.get_key(keyname)
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
        if not S3_ENABLED:
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
                    key = s3.new_key()
                    key.key = str(self.section) + '/' + str(self.file_number) + '/' + str(filename)
                    if filename == self.filename:
                        extension, mimetype = get_ext_and_mimetype(filename + '.' + self.extension)
                        key.content_type = mimetype
                if save:
                    key.set_contents_from_filename(fullpath)
        for filename, key in self.keydict.iteritems():
            if filename not in existing_files:
                logmessage("Deleting filename " + str(filename) + " from S3")
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
