# pylint: disable=attribute-defined-outside-init,missing-class-docstring,too-many-instance-attributes
import re
import os
import copy
import datetime
import platform
from jinja2.exceptions import TemplateError
from jinja2 import FileSystemLoader, select_autoescape, TemplateNotFound
from jinja2.environment import Environment
from docassemble.base.error import DANotFoundError, DAError
from docassemble.base.logger import logmessage
from docassemble.base.functions import (
    package_question_filename,
    standard_question_filename,
    get_config,
)
from docassemble.base.hooks import (
    absolute_filename,
    get_configuration,
    get_server_redis,
)
from . import __version__ as da_version

da_arch = platform.machine()

class DAFileSystemLoader(FileSystemLoader):

    def get_source(self, environment, template):
        if ':' not in template:
            return super().get_source(environment, template)
        template_path = None
        for the_filename in question_path_options(template):
            if the_filename is not None:
                template_path = the_filename
                break
        if template_path is None or not os.path.isfile(template_path):
            raise TemplateNotFound(template)
        fspath = os.fspath(os.path.dirname(template_path))
        if fspath not in self.searchpath:
            self.searchpath.append(fspath)
        mtime = os.path.getmtime(template_path)
        with open(template_path, 'r', encoding='utf-8') as fp:
            source = fp.read()
        return source, template_path, lambda: mtime == os.path.getmtime(template_path)

class InterviewSource:

    def __init__(self, **kwargs):
        if not hasattr(self, 'package'):
            self.package = kwargs.get('package', None)
        self.language = kwargs.get('language', '*')
        self.dialect = kwargs.get('dialect', None)
        self.testing = kwargs.get('testing', False)
        self.translating = kwargs.get('translating', False)

    def __le__(self, other):
        return str(self) <= (str(other) if isinstance(other, InterviewSource) else other)

    def __ge__(self, other):
        return str(self) >= (str(other) if isinstance(other, InterviewSource) else other)

    def __gt__(self, other):
        return str(self) > (str(other) if isinstance(other, InterviewSource) else other)

    def __lt__(self, other):
        return str(self) < (str(other) if isinstance(other, InterviewSource) else other)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __str__(self):
        if hasattr(self, 'path'):
            return str(self.path)
        return 'interviewsource'

    def __hash__(self):
        if hasattr(self, 'path'):
            return hash((self.path,))
        return hash(('interviewsource',))

    def set_path(self, path):
        self.path = path

    def get_name(self):
        if ':' in self.path:
            return self.path
        return self.get_package() + ':data/questions/' + self.path

    def get_index(self):
        the_index = get_server_redis().get('da:interviewsource:' + self.path)
        if the_index is None:
            # logmessage("Updating index from get_index for " + self.path)
            the_index = get_server_redis().incr('da:interviewsource:' + self.path)
        return the_index

    def update_index(self):
        # logmessage("Updating index for " + self.path)
        get_server_redis().incr('da:interviewsource:' + self.path)

    def set_filepath(self, filepath):
        self.filepath = filepath

    def set_directory(self, directory):
        self.directory = directory

    def set_content(self, content):
        self.content = content

    def set_language(self, language):
        self.language = language

    def set_dialect(self, dialect):
        self.dialect = dialect

    def set_testing(self, testing):
        self.testing = testing

    def set_package(self, package):
        self.package = package

    def update(self, **kwargs):  # pylint: disable=unused-argument
        return True

    def get_modtime(self):
        return self._modtime  # pylint: disable=no-member

    def get_language(self):
        return self.language

    def get_dialect(self):
        return self.dialect

    def get_package(self):
        return self.package

    def get_testing(self):
        return self.testing

    def append(self, path):  # pylint: disable=unused-argument
        return None


class InterviewSourceString(InterviewSource):

    def __init__(self, **kwargs):
        self.set_path(kwargs.get('path', None))
        self.set_directory(kwargs.get('directory', None))
        self.set_content(kwargs.get('content', None))
        self._modtime = datetime.datetime.now(tz=datetime.timezone.utc)
        super().__init__(**kwargs)


class InterviewSourceFile(InterviewSource):

    def __init__(self, **kwargs):
        self.playground = None
        if 'filepath' in kwargs:
            if kwargs['filepath'].__class__.__name__.endswith('SavedFile'):
                self.playground = kwargs['filepath']
                if self.playground.subdir and self.playground.subdir != 'default':
                    self.playground_file = os.path.join(self.playground.subdir, self.playground.filename)
                else:
                    self.playground_file = self.playground.filename
                # logmessage("The path is " + repr(self.playground.path))
                if os.path.isfile(self.playground.path) and os.access(self.playground.path, os.R_OK):
                    self.set_filepath(self.playground.path)
                else:
                    logmessage("Details of playground path reference:")
                    logmessage("Keyword arguments were " + repr(kwargs))
                    for attribute in ['file_number', 'fixed', 'section', 'filename', 'extension', 'directory', 'path', 'modtimes', 'keydict', 'subdir']:
                        if hasattr(self.playground, attribute):
                            logmessage(attribute + " is " + repr(getattr(self.playground, attribute)))
                        else:
                            logmessage(attribute + " did not exist")
                    if os.path.exists(self.playground.path):
                        if os.path.isfile(self.playground.path):
                            if os.access(self.playground.path, os.R_OK):
                                logmessage("path is a file and is readable")
                            else:
                                logmessage("path is a file but is not readable")
                        else:
                            logmessage("path was not a file")
                    else:
                        logmessage("path did not exist")
                    raise DANotFoundError("Reference to invalid playground path.")
            else:
                self.set_filepath(kwargs['filepath'])
        else:
            self.filepath = None
        if 'path' in kwargs:
            self.set_path(kwargs['path'])
        super().__init__(**kwargs)

    def set_path(self, path):
        self.path = path
        parts = path.split(":")
        if len(parts) == 2:
            self.package = parts[0]
            self.basename = parts[1]
        else:
            self.package = None
        # if self.package is None:
        #     m = re.search(r'^/(playground\.[0-9]+)/', path)
        #     if m:
        #         self.package = m.group(1)
        if self.filepath is None:
            self.set_filepath(interview_source_from_string(self.path))
        if self.package is None and re.search(r'docassemble.base.data.', self.filepath):
            self.package = 'docassemble.base'

    def set_filepath(self, filepath):
        # logmessage("Called set_filepath with " + str(filepath))
        self.filepath = filepath
        if self.filepath is None:
            self.directory = None
        else:
            self.set_directory(os.path.dirname(self.filepath))

    def reset_modtime(self):
        try:
            with open(self.filepath, 'a', encoding='utf-8'):
                os.utime(self.filepath, None)
        except:
            logmessage("InterviewSourceFile: could not reset modification time on interview")

    def update(self, **kwargs):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as the_file:
                orig_text = the_file.read()
        except:
            return False
        if not orig_text.startswith('# use jinja'):
            self.set_content(orig_text)
            return True
        env = Environment(
            loader=DAFileSystemLoader(self.directory),
            autoescape=select_autoescape()
        )
        if kwargs.get('raise_jinja_errors', True):
            template = env.get_template(os.path.basename(self.filepath))
        else:
            try:
                template = env.get_template(os.path.basename(self.filepath))
            except TemplateError:
                self.set_content(orig_text)
                return True
        data = copy.deepcopy(get_config('jinja data'))
        data['__config__'] = copy.deepcopy(get_configuration())
        data['__version__'] = da_version
        data['__architecture__'] = da_arch
        data['__filename__'] = self.path
        data['__current_package__'] = self.package
        data['__parent_filename__'] = kwargs.get('parent_source', self).path
        data['__parent_package__'] = kwargs.get('parent_source', self).package
        data['__interview_filename__'] = kwargs.get('interview_source', self).path
        data['__interview_package__'] = kwargs.get('interview_source', self).package
        data['__hostname__'] = get_config('external hostname', None) or 'localhost'
        data['__debug__'] = bool(get_config('debug', True))
        try:
            self.set_content(template.render(data))
        except BaseException as err:
            self.set_content("__error__: " + repr("Jinja2 rendering error: " + err.__class__.__name__ + ": " + str(err)))
        return True

    def get_modtime(self):
        # logmessage("get_modtime called in parse where path is " + str(self.path))
        if self.playground is not None:
            return self.playground.get_modtime(filename=self.playground_file)
        self._modtime = os.path.getmtime(self.filepath)
        return self._modtime

    def append(self, path):
        new_file = os.path.join(self.directory, path)
        if os.path.isfile(new_file) and os.access(new_file, os.R_OK):
            new_source = InterviewSourceFile()
            new_source.path = path
            new_source.directory = self.directory
            new_source.basename = path
            new_source.filepath = new_file
            new_source.playground = self.playground
            if hasattr(self, 'package'):
                new_source.package = self.package
            if new_source.update():
                return new_source
        return None

def question_path_options(path):
    n = 0
    while n < 3:
        if n == 0:
            yield package_question_filename(path)
        elif n == 1:
            yield standard_question_filename(path)
        elif n == 2:
            yield absolute_filename(path)
        n += 1

def interview_source_from_string(path, **kwargs):
    if path is None:
        raise DAError("Passed None to interview_source_from_string")
    # logmessage("Trying to find " + path)
    path = re.sub(r'(docassemble.playground[0-9]+[^:]*:)data/questions/(.*)', r'\1\2', path)
    for the_filename in question_path_options(path):
        if the_filename is not None:
            new_source = InterviewSourceFile(filepath=the_filename, path=path)
            if new_source.update(**kwargs):
                return new_source
    raise DANotFoundError("Interview " + str(path) + " not found")
