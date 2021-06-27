import mimetypes
import traceback
import re
from jinja2.runtime import StrictUndefined, UndefinedError
from jinja2.exceptions import TemplateError
from jinja2.environment import Environment
from jinja2.environment import Template as JinjaTemplate
from jinja2 import meta as jinja2meta
from jinja2.lexer import Token
from jinja2.utils import internalcode, missing, object_type_repr
from jinja2.ext import Extension
import ast
import ruamel.yaml as yaml
import string
import os
import os.path
import sys
import types
from urllib.request import urlretrieve
equals_byte = bytes('=', 'utf-8')
import httplib2
import datetime
import time
import operator
import pprint
import copy
import codecs
import array
import random
import tempfile
import json
import docassemble.base.filter
import docassemble.base.pdftk
import docassemble.base.file_docx
from docassemble.base.error import DAError, DANotFoundError, MandatoryQuestion, DAErrorNoEndpoint, DAErrorMissingVariable, ForcedNameError, QuestionError, ResponseError, BackgroundResponseError, BackgroundResponseActionError, CommandError, CodeExecute, DAValidationError, ForcedReRun, LazyNameError, DAAttributeError, DAIndexError
import docassemble.base.functions
import docassemble.base.util
from docassemble.base.functions import pickleable_objects, word, get_language, server, RawValue, get_config
from docassemble.base.logger import logmessage
from docassemble.base.pandoc import MyPandoc, word_to_markdown
from docassemble.base.mako.template import Template as MakoTemplate
from docassemble.base.mako.exceptions import SyntaxException, CompileException
from docassemble.base.astparser import myvisitnode
import collections.abc as abc
from collections import OrderedDict
from types import CodeType
import pandas
import dateutil.parser
import pytz
from itertools import groupby, chain
from collections import namedtuple
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from docassemble_textstat.textstat import textstat
from html.parser import HTMLParser
from io import StringIO
import qrcode
import qrcode.image.svg
RangeType = type(range(1,2))
NoneType = type(None)

debug = True
import_core = compile("import docassemble.base.core", '<code block>', 'exec')
import_util = compile('from docassemble.base.util import *', '<code block>', 'exec')
import_process_action = compile('from docassemble.base.util import process_action', '<code block>', 'exec')
run_process_action = compile('process_action()', '<code block>', 'exec')
match_process_action = re.compile(r'process_action\(')
match_mako = re.compile(r'<%|\${|% if|% for|% while|\#\#')
emoji_match = re.compile(r':([^ ]+):')
valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')
nameerror_match = re.compile(r'\'(.*)\' (is not defined|referenced before assignment|is undefined)')
document_match = re.compile(r'^--- *$', flags=re.MULTILINE)
remove_trailing_dots = re.compile(r'[\n\r]+\.\.\.$')
fix_tabs = re.compile(r'\t')
dot_split = re.compile(r'([^\.\[\]]+(?:\[.*?\])?)')
match_brackets_at_end = re.compile(r'^(.*)(\[.+?\])')
match_inside_brackets = re.compile(r'\[(.+?)\]')
match_brackets = re.compile(r'(\[.+?\])')
match_brackets_or_dot = re.compile(r'(\[.+?\]|\.[a-zA-Z_][a-zA-Z0-9_]*)')
complications = re.compile(r'[\.\[]')
list_of_indices = ['i', 'j', 'k', 'l', 'm', 'n']
extension_of_doc_format = {'pdf':'pdf', 'docx': 'docx', 'rtf': 'rtf', 'rtf to docx': 'docx', 'tex': 'tex', 'html': 'html'}
do_not_translate = """<%doc>
  do not translate
</%doc>
"""

def process_audio_video_list(the_list, the_user_dict):
    output = list()
    for the_item in the_list:
        output.append({'text': the_item['text'].text(the_user_dict), 'package': the_item['package'], 'type': the_item['type']})
    return output

def textify(data, the_user_dict):
    return list(map((lambda x: x.text(the_user_dict)), data))

# def set_absolute_filename(func):
#     #logmessage("Running set_absolute_filename in parse")
#     docassemble.base.functions.set_absolute_filename(func)

# def set_url_finder(func):
#     docassemble.base.filter.set_url_finder(func)
#     docassemble.base.functions.set_url_finder(func)

# def set_url_for(func):
#     docassemble.base.filter.set_url_for(func)

# def set_file_finder(func):
#     docassemble.base.filter.set_file_finder(func)

# def set_da_send_mail(func):
#     docassemble.base.filter.set_da_send_mail(func)

# def blank_save_numbered_file(*args, **kwargs):
#     return(None, None, None)

# save_numbered_file = blank_save_numbered_file

# def set_save_numbered_file(func):
#     global save_numbered_file
#     #logmessage("set the save_numbered_file function to " + str(func))
#     save_numbered_file = func
#     return

initial_dict = dict(_internal=dict(session_local=dict(), device_local=dict(), user_local=dict(), dirty=dict(), progress=0, tracker=0, docvar=dict(), doc_cache=dict(), steps=1, steps_offset=0, secret=None, informed=dict(), livehelp=dict(availability='unavailable', mode='help', roles=list(), partner_roles=list()), answered=set(), answers=dict(), objselections=dict(), starttime=None, modtime=None, accesstime=dict(), tasks=dict(), gather=list(), event_stack=dict(), misc=dict()), url_args=dict(), nav=docassemble.base.functions.DANav())

def set_initial_dict(the_dict):
    global initial_dict
    initial_dict = the_dict
    return

def get_initial_dict():
    return copy.deepcopy(initial_dict);

class PackageImage:
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename', None)
        self.attribution = kwargs.get('attribution', None)
        self.setname = kwargs.get('setname', None)
        self.package = kwargs.get('package', 'docassemble.base')
    def get_filename(self):
        return(docassemble.base.functions.static_filename_path(str(self.package) + ':' + str(self.filename)))
    def get_reference(self):
        #logmessage("get_reference is considering " + str(self.package) + ':' + str(self.filename))
        return str(self.package) + ':' + str(self.filename)

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
        else:
            return hash(('interviewsource',))
    def set_path(self, path):
        self.path = path
        return
    def get_name(self):
        if ':' in self.path:
            return self.path
        return self.get_package() + ':data/questions/' + self.path
    def get_index(self):
        the_index = docassemble.base.functions.server.server_redis.get('da:interviewsource:' + self.path)
        if the_index is None:
            #sys.stderr.write("Updating index from get_index for " + self.path + "\n")
            the_index = docassemble.base.functions.server.server_redis.incr('da:interviewsource:' + self.path)
        return the_index
    def update_index(self):
        #sys.stderr.write("Updating index for " + self.path + "\n")
        docassemble.base.functions.server.server_redis.incr('da:interviewsource:' + self.path)
    def set_filepath(self, filepath):
        self.filepath = filepath
        return
    def set_directory(self, directory):
        self.directory = directory
        return
    def set_content(self, content):
        self.content = content
        return
    def set_language(self, language):
        self.language = language
        return
    def set_dialect(self, dialect):
        self.dialect = dialect
        return
    def set_testing(self, testing):
        self.testing = testing
        return
    def set_package(self, package):
        self.package = package
        return
    def update(self):
        return True
    def get_modtime(self):
        return self._modtime
    def get_language(self):
        return self.language
    def get_dialect(self):
        return self.dialect
    def get_package(self):
        return self.package
    def get_testing(self):
        return self.testing
    def get_interview(self):
        return Interview(source=self)
    def append(self, path):
        return None

class InterviewSourceString(InterviewSource):
    def __init__(self, **kwargs):
        self.set_path(kwargs.get('path', None))
        self.set_directory(kwargs.get('directory', None))
        self.set_content(kwargs.get('content', None))
        self._modtime = datetime.datetime.utcnow()
        return super().__init__(**kwargs)

class InterviewSourceFile(InterviewSource):
    def __init__(self, **kwargs):
        self.playground = None
        if 'filepath' in kwargs:
            if re.search(r'SavedFile', str(type(kwargs['filepath']))):
                self.playground = kwargs['filepath']
                if self.playground.subdir and self.playground.subdir != 'default':
                    self.playground_file = os.path.join(self.playground.subdir, self.playground.filename)
                else:
                    self.playground_file = self.playground.filename
                #sys.stderr.write("The path is " + repr(self.playground.path) + "\n")
                if os.path.isfile(self.playground.path) and os.access(self.playground.path, os.R_OK):
                    self.set_filepath(self.playground.path)
                else:
                    raise DAError("Reference to invalid playground path")
            else:
                self.set_filepath(kwargs['filepath'])
        else:
            self.filepath = None
        if 'path' in kwargs:
            self.set_path(kwargs['path'])
        return super().__init__(**kwargs)
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
        return
    def set_filepath(self, filepath):
        #logmessage("Called set_filepath with " + str(filepath))
        self.filepath = filepath
        if self.filepath is None:
            self.directory = None
        else:
            self.set_directory(os.path.dirname(self.filepath))
        return
    def reset_modtime(self):
        try:
            with open(self.filepath, 'a'):
                os.utime(self.filepath, None)
        except:
            logmessage("InterviewSourceFile: could not reset modification time on interview")
    def update(self):
        #logmessage("Update: " + str(self.filepath))
        try:
            with open(self.filepath, 'r', encoding='utf-8') as the_file:
                self.set_content(the_file.read())
                #sys.stderr.write("Returning true\n")
                return True
        except Exception as errmess:
            #sys.stderr.write("Error: " + str(errmess) + "\n")
            pass
        return False
    def get_modtime(self):
        #logmessage("get_modtime called in parse where path is " + str(self.path))
        if self.playground is not None:
            return self.playground.get_modtime(filename=self.playground_file)
        self._modtime = os.path.getmtime(self.filepath)
        return(self._modtime)
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
                return(new_source)
        return(None)

def dummy_embed_input(status, variable):
    return variable

class InterviewStatus:
    def __init__(self, current_info=dict(), **kwargs):
        self.current_info = current_info
        self.attributions = set()
        self.seeking = list()
        self.tracker = kwargs.get('tracker', -1)
        self.maps = list()
        self.extra_scripts = list()
        self.extra_css = list()
        self.using_screen_reader = False
        self.can_go_back = True
        self.attachments = None
        self.linkcounter = 0
        #restore this, maybe
        #self.next_action = list()
        self.embedded = set()
        self.extras = dict()
        self.followed_mc = False
        self.tentatively_answered = set()
        self.checkin = False
    def get_all_fields_used(self, user_dict):
        if 'list_collect' in self.extras:
            all_fields = set()
            allow_append = self.extras['list_collect_allow_append']
            iterator_re = re.compile(r"\[%s\]" % (self.extras['list_iterator'],))
            list_len = len(self.extras['list_collect'].elements)
            if hasattr(self.extras['list_collect'], 'minimum_number') and self.extras['list_collect'].minimum_number is not None and self.extras['list_collect'].minimum_number > list_len:
                list_len = self.extras['list_collect'].minimum_number
            if list_len == 0:
                list_len = 1
            if self.extras['list_collect'].ask_object_type or not allow_append:
                extra_amount = 0
            else:
                extra_amount = get_config('list collect extra count', 15)
            for list_indexno in range(list_len + extra_amount):
                for field_used in self.question.fields_used:
                    all_fields.add(re.sub(iterator_re, '[' + str(list_indexno) +']', field_used))
            return all_fields
        else:
            return self.question.fields_used
    def get_fields_and_sub_fields_and_collect_fields(self, user_dict):
        all_fields = self.question.get_fields_and_sub_fields(user_dict)
        if 'list_collect' in self.extras:
            allow_append = self.extras['list_collect_allow_append']
            iterator_re = re.compile(r"\[%s\]" % (self.extras['list_iterator'],))
            if 'sub_fields' in self.extras:
                field_list = list()
                for field in self.question.fields:
                    if field.number in self.extras['sub_fields']:
                        field_list.extend(self.extras['sub_fields'][field.number])
                    else:
                        field_list.append(field)
            else:
                field_list = self.question.fields
            list_len = len(self.extras['list_collect'].elements)
            if hasattr(self.extras['list_collect'], 'minimum_number') and self.extras['list_collect'].minimum_number is not None and self.extras['list_collect'].minimum_number > list_len:
                list_len = self.extras['list_collect'].minimum_number
            if list_len == 0:
                list_len = 1
            if self.extras['list_collect'].ask_object_type or not allow_append:
                extra_amount = 0
            else:
                extra_amount = get_config('list collect extra count', 15)
            for list_indexno in range(list_len + extra_amount):
                for field in field_list:
                    the_field = copy.deepcopy(field)
                    the_field.number = str(list_indexno) + '_' + str(the_field.number)
                    if hasattr(the_field, 'saveas'):
                        the_field.saveas = safeid(re.sub(iterator_re, '[' + str(list_indexno) +']', from_safeid(field.saveas)))
                        all_fields.append(the_field)
        return all_fields
    def is_empty_mc(self, field):
        if hasattr(field, 'choicetype') and not (hasattr(field, 'inputtype') and field.inputtype == 'combobox'):
            if field.choicetype in ['compute', 'manual']:
                if field.number not in self.selectcompute:
                    return False
                pairlist = list(self.selectcompute[field.number])
            else:
                logmessage("is_empty_mc: unknown choicetype " + str(field.choicetype))
                return False
            if len(pairlist) == 0:
                return True
        return False
    def get_field_info(self):
        datatypes = dict()
        hiddens = dict()
        files = list()
        ml_info = dict()
        checkboxes = dict()
        saveas_by_number = dict()
        saveas_to_use = dict()
        if self.extras.get('list_collect', False) is not False:
            list_collect_list = self.extras['list_collect'].instanceName
        else:
            list_collect_list = None
        if self.orig_sought is not None:
            orig_sought = self.orig_sought
        else:
            orig_sought = None
        if self.question.question_type == "signature":
            signature_saveas = self.question.fields[0].saveas
        else:
            signature_saveas = None
        if hasattr(self.question, 'fields_saveas'):
            datatypes[safeid(self.question.fields_saveas)] = "boolean"
            fields_saveas = self.question.fields_saveas
        else:
            fields_saveas = None
        if self.question.question_type in ["yesno", "yesnomaybe"]:
            datatypes[self.question.fields[0].saveas] = self.question.fields[0].datatype
        elif self.question.question_type in ["noyes", "noyesmaybe"]:
            datatypes[self.question.fields[0].saveas] = self.question.fields[0].datatype
        elif self.question.question_type == "review" and hasattr(self.question, 'review_saveas'):
            datatypes[safeid(self.question.review_saveas)] = "boolean"
        elif self.question.question_type == "fields":
            the_field_list = self.get_field_list()
            for field in the_field_list:
                if hasattr(field, 'saveas'):
                    if (hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in self.extras) or 'show_if_js' in field.extras)) or (hasattr(field, 'disableothers') and field.disableothers):
                        the_saveas = safeid('_field_' + str(field.number))
                    else:
                        the_saveas = field.saveas
                    saveas_to_use[field.saveas] = the_saveas
                    saveas_by_number[field.number] = the_saveas
            for field in the_field_list:
                if not self.extras['ok'][field.number]:
                    continue
                if self.is_empty_mc(field):
                    if hasattr(field, 'datatype'):
                        hiddens[field.saveas] = field.datatype
                    else:
                        hiddens[field.saveas] = True
                    if hasattr(field, 'datatype'):
                        datatypes[field.saveas] = field.datatype
                        if field.datatype in ('object_multiselect', 'object_checkboxes'):
                            datatypes[safeid(from_safeid(field.saveas) + ".gathered")] = 'boolean'
                    continue
                if hasattr(field, 'extras'):
                    if 'ml_group' in field.extras or 'ml_train' in field.extras:
                        ml_info[field.saveas] = dict()
                        if 'ml_group' in field.extras:
                            ml_info[field.saveas]['group_id'] = self.extras['ml_group'][field.number]
                        if 'ml_train' in field.extras:
                            ml_info[field.saveas]['train'] = self.extras['ml_train'][field.number]
                if hasattr(field, 'choicetype'):
                    vals = set([str(x['key']) for x in self.selectcompute[field.number]])
                    if len(vals) == 1 and ('True' in vals or 'False' in vals):
                        datatypes[field.saveas] = 'boolean'
                    elif len(vals) == 1 and 'None' in vals:
                        datatypes[field.saveas] = 'threestate'
                    elif len(vals) == 2 and ('True' in vals and 'False' in vals):
                        datatypes[field.saveas] = 'boolean'
                    elif len(vals) == 2 and (('True' in vals and 'None' in vals) or ('False' in vals and 'None' in vals)):
                        datatypes[field.saveas] = 'threestate'
                    elif len(vals) == 3 and ('True' in vals and 'False' in vals and 'None' in vals):
                        datatypes[field.saveas] = 'threestate'
                    else:
                        datatypes[field.saveas] = field.datatype
                elif hasattr(field, 'datatype') and hasattr(field, 'saveas'):
                    datatypes[field.saveas] = field.datatype
                if hasattr(field, 'datatype') and hasattr(field, 'saveas'):
                    if (field.datatype in ['files', 'file', 'camera', 'user', 'environment', 'camcorder', 'microphone']):
                        files.append(saveas_by_number[field.number])
                    if not hasattr(field, 'choicetype'):
                        datatypes[field.saveas] = field.datatype
                    if field.datatype == 'boolean':
                        if field.sign > 0:
                            checkboxes[field.saveas] = 'False'
                        else:
                            checkboxes[field.saveas] = 'True'
                    elif field.datatype == 'threestate':
                        checkboxes[field.saveas] = 'None'
                    elif field.datatype in ['multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes']:
                        if field.choicetype in ['compute', 'manual']:
                            pairlist = list(self.selectcompute[field.number])
                        else:
                            pairlist = list()
                        for pair in pairlist:
                            if isinstance(pair['key'], str):
                                checkboxes[safeid(from_safeid(field.saveas) + "[B" + myb64quote(pair['key']) + "]")] = 'False'
                            else:
                                checkboxes[safeid(from_safeid(field.saveas) + "[R" + myb64quote(repr(pair['key'])) + "]")] = 'False'
                    elif not self.extras['required'][field.number]:
                        checkboxes[field.saveas] = 'None'
                if field.datatype in ('object_multiselect', 'object_checkboxes'):
                    datatypes[safeid(from_safeid(field.saveas) + ".gathered")] = 'boolean'
            if self.extras.get('list_collect_is_final', False):
                if self.extras['list_collect'].ask_number:
                    datatypes[safeid(self.extras['list_collect'].instanceName + ".target_number")] = 'integer'
                else:
                    datatypes[safeid(self.extras['list_collect'].instanceName + ".there_is_another")] = 'boolean'
        elif self.question.question_type == "settrue":
            datatypes[self.question.fields[0].saveas] = "boolean"
        elif self.question.question_type == "multiple_choice" and hasattr(self.question.fields[0], 'datatype'):
            datatypes[self.question.fields[0].saveas] = self.question.fields[0].datatype
        return {'datatypes': datatypes, 'hiddens': hiddens, 'files': files, 'ml_info': ml_info, 'checkboxes': checkboxes, 'list_collect_list': list_collect_list, 'orig_sought': orig_sought, 'fields_saveas': fields_saveas, 'signature_saveas': signature_saveas}
    def do_sleep(self):
        if hasattr(self.question, 'sleep'):
            try:
                time.sleep(self.question.sleep)
            except:
                sys.stderr.write("do_sleep: invalid sleep amount " + repr(self.question.sleep) + "\n")
    def get_field_list(self):
        if 'sub_fields' in self.extras:
            field_list = list()
            for field in self.question.fields:
                if field.number in self.extras['sub_fields']:
                    field_list.extend(self.extras['sub_fields'][field.number])
                else:
                    field_list.append(field)
        else:
            field_list = self.question.fields
        if 'list_collect' in self.extras:
            full_field_list = list()
            allow_append = self.extras['list_collect_allow_append']
            iterator_re = re.compile(r"\[%s\]" % (self.extras['list_iterator'],))
            list_len = len(self.extras['list_collect'].elements)
            if hasattr(self.extras['list_collect'], 'minimum_number') and self.extras['list_collect'].minimum_number is not None and self.extras['list_collect'].minimum_number > list_len:
                list_len = self.extras['list_collect'].minimum_number
            if list_len == 0:
                list_len = 1
            if self.extras['list_collect'].ask_object_type or not allow_append:
                extra_amount = 0
            else:
                extra_amount = get_config('list collect extra count', 15)
            for list_indexno in range(list_len + extra_amount):
                header_field = Field({'type': 'html', 'extras': {'html': TextObject('')}})
                if list_indexno >= list_len:
                    header_field.collect_type = 'extraheader'
                elif list_indexno == 0:
                    header_field.collect_type = 'firstheader'
                else:
                    header_field.collect_type = 'header'
                header_field.collect_number = list_indexno
                header_field.number = str(list_indexno)
                full_field_list.append(header_field)
                self.extras['ok'][str(list_indexno)] = True
                self.extras['required'][str(list_indexno)] = False
                for field in field_list:
                    the_field = copy.deepcopy(field)
                    the_field.number = str(list_indexno) + '_' + str(the_field.number)
                    if hasattr(the_field, 'saveas'):
                        the_field.saveas = safeid(re.sub(iterator_re, '[' + str(list_indexno) + ']', from_safeid(the_field.saveas)))
                        if hasattr(the_field, 'disableothers') and the_field.disableothers:
                            list_of_other_fields = list()
                            if isinstance(the_field.disableothers, list):
                                for other_saveas in the_field.disableothers:
                                    list_of_other_fields.append(re.sub(iterator_re, '[' + str(list_indexno) + ']', other_saveas))
                            else:
                                for other_field in field_list:
                                    if not hasattr(other_field, 'saveas'):
                                        continue
                                    if other_field.number == field.number:
                                        continue
                                    list_of_other_fields.append(re.sub(iterator_re, '[' + str(list_indexno) +']', from_safeid(other_field.saveas)))
                            the_field.disableothers = list_of_other_fields
                        if hasattr(the_field, 'uncheckothers') and the_field.uncheckothers:
                            list_of_other_fields = list()
                            if isinstance(the_field.uncheckothers, list):
                                for other_saveas in the_field.uncheckothers:
                                    list_of_other_fields.append(re.sub(iterator_re, '[' + str(list_indexno) +']', from_safeid(other_saveas)))
                            else:
                                for other_field in field_list:
                                    if not hasattr(other_field, 'saveas'):
                                        continue
                                    if other_field.number == field.number or not (hasattr(other_field, 'inputtype') and other_field.inputtype in ['yesno', 'noyes', 'yesnowide', 'noyeswide']):
                                        continue
                                    list_of_other_fields.append(re.sub(iterator_re, '[' + str(list_indexno) +']', from_safeid(other_field.saveas)))
                            the_field.uncheckothers = list_of_other_fields
                    if hasattr(the_field, 'extras'):
                        if 'show_if_var' in the_field.extras:
                            the_field.extras['show_if_var'] = safeid(re.sub(r'\[' + self.extras['list_iterator'] + r'\]', '[' + str(list_indexno) + ']', from_safeid(the_field.extras['show_if_var'])))
                        if 'show_if_js' in the_field.extras:
                            the_field.extras['show_if_js']['expression'].original_text = re.sub(iterator_re, '[' + str(list_indexno) + ']', the_field.extras['show_if_js']['expression'].original_text)
                            self.extras['show_if_js'][the_field.number]['expression'] = re.sub(iterator_re, '[' + str(list_indexno) + ']', self.extras['show_if_js'][the_field.number]['expression'])
                            if the_field.extras['show_if_js']['expression'].uses_mako:
                                the_field.extras['show_if_js']['expression'].template = MakoTemplate(the_field.extras['show_if_js']['expression'].original_text, strict_undefined=True, input_encoding='utf-8')
                            for ii in range(len(the_field.extras['show_if_js']['vars'])):
                                the_field.extras['show_if_js']['vars'][ii] = re.sub(iterator_re, '[' + str(list_indexno) + ']', the_field.extras['show_if_js']['vars'][ii])
                            for ii in range(len(self.extras['show_if_js'][the_field.number]['vars'])):
                                self.extras['show_if_js'][the_field.number]['vars'][ii] = re.sub(iterator_re, '[' + str(list_indexno) + ']', self.extras['show_if_js'][the_field.number]['vars'][ii])
                    if list_indexno >= list_len:
                        the_field.collect_type = 'extra'
                    else:
                        the_field.collect_type = 'mid'
                    the_field.collect_number = list_indexno
                    full_field_list.append(the_field)
                post_header_field = Field({'type': 'html', 'extras': {'html': TextObject('')}})
                if extra_amount > 0 and list_indexno == list_len + extra_amount - 1:
                    post_header_field.collect_type = 'extrafinalpostheader'
                elif list_indexno >= list_len:
                    post_header_field.collect_type = 'extrapostheader'
                else:
                    post_header_field.collect_type = 'postheader'
                post_header_field.collect_number = list_indexno
                post_header_field.number = str(list_indexno)
                full_field_list.append(post_header_field)
            return full_field_list
        else:
            return field_list
    def mark_tentative_as_answered(self, the_user_dict):
        for question in self.tentatively_answered:
            question.mark_as_answered(the_user_dict)
        self.tentatively_answered.clear()
    def initialize_screen_reader(self):
        self.using_screen_reader = True
        self.screen_reader_text = dict()
        self.screen_reader_links = {'question': [], 'help': []}
    def populate(self, question_result):
        self.question = question_result['question']
        self.questionText = question_result['question_text']
        self.subquestionText = question_result['subquestion_text']
        self.continueLabel = question_result['continue_label']
        self.decorations = question_result['decorations']
        self.audiovideo = question_result['audiovideo']
        self.helpText = question_result['help_text']
        self.attachments = question_result['attachments']
        self.selectcompute = question_result['selectcompute']
        self.defaults = question_result['defaults']
        self.other_defaults = dict()
        #self.defined = question_result['defined']
        self.hints = question_result['hints']
        self.helptexts = question_result['helptexts']
        self.extras = question_result['extras']
        self.labels = question_result['labels']
        self.sought = question_result['sought']
        self.orig_sought = question_result['orig_sought']
    def set_tracker(self, tracker):
        self.tracker = tracker
    def get_history(self):
        output = {'steps': []}
        if self.question.from_source.path != self.question.interview.source.path and self.question.from_source.path is not None:
            output['source_file'] = self.question.from_source.path
        if hasattr(self.question, 'source_code') and self.question.source_code is not None:
            output['source_code'] = self.question.source_code
        index = 0
        seeking_len = len(self.seeking)
        if seeking_len:
            starttime = self.seeking[0]['time']
            for stage in self.seeking:
                index += 1
                if index < seeking_len and 'reason' in self.seeking[index] and self.seeking[index]['reason'] in ('asking', 'running') and self.seeking[index]['question'] is stage['question'] and 'question' in stage and 'reason' in stage and stage['reason'] == 'considering':
                    continue
                the_stage = {'time': "%.5fs" % (stage['time'] - starttime), 'index': index}
                if 'question' in stage and 'reason' in stage and (index < (seeking_len - 1) or stage['question'] is not self.question):
                    the_stage['reason'] = stage['reason']
                    if stage['reason'] == 'initial':
                        the_stage['reason_text'] = "Ran initial code"
                    elif stage['reason'] == 'mandatory question':
                        the_stage['reason_text'] = "Tried to ask mandatory question"
                    elif stage['reason'] == 'mandatory code':
                        the_stage['reason_text'] = "Tried to run mandatory code"
                    elif stage['reason'] == 'asking':
                        the_stage['reason_text'] = "Tried to ask question"
                    elif stage['reason'] == 'running':
                        the_stage['reason_text'] = "Tried to run block"
                    elif stage['reason'] == 'considering':
                        the_stage['reason_text'] = "Considered using block"
                    elif stage['reason'] == 'objects from file':
                        the_stage['reason_text'] = "Tried to load objects from file"
                    elif stage['reason'] == 'data':
                        the_stage['reason_text'] = "Tried to load data"
                    elif stage['reason'] == 'objects':
                        the_stage['reason_text'] = "Tried to load objects"
                    elif stage['reason'] == 'result of multiple choice':
                        the_stage['reason_text'] = "Followed the result of multiple choice selection"
                    if stage['question'].from_source.path != self.question.interview.source.path and stage['question'].from_source.path is not None:
                        the_stage['source_file'] = stage['question'].from_source.path
                    if (not hasattr(stage['question'], 'source_code')) or stage['question'].source_code is None:
                        the_stage['embedded'] = True
                    else:
                        the_stage['code'] = stage['question'].source_code
                elif 'variable' in stage:
                    the_stage['reason'] = 'needed'
                    the_stage['reason_text'] = "Needed definition of"
                    the_stage['variable_name'] = str(stage['variable'])
                elif 'done' in stage:
                    the_stage['reason'] = 'complete'
                    the_stage['reason_text'] = "Completed processing"
                else:
                    continue
                output['steps'].append(the_stage)
        return output
    def as_data(self, the_user_dict, encode=True):
        result = dict(language=self.question.language)
        debug = self.question.interview.debug
        if debug:
            output = dict(question='', help='')
        if 'progress' in the_user_dict['_internal']:
            result['progress'] = the_user_dict['_internal']['progress']
        if self.question.language in self.question.interview.default_validation_messages:
            result['validation_messages'] = copy.copy(self.question.interview.default_validation_messages[self.question.language])
        else:
            result['validation_messages'] = dict()
        if 'reload_after' in self.extras:
            result['reload'] = 1000 * int(self.extras['reload_after'])
        lang = docassemble.base.functions.get_language()
        if len(self.question.terms) or len(self.question.interview.terms):
            result['terms'] = dict()
            if 'terms' in self.extras:
                for term, vals in self.extras['terms'].items():
                    result['terms'][term] = vals['definition']
            if lang in self.question.interview.terms and len(self.question.interview.terms[lang]):
                for term, vals in self.question.interview.terms[lang].items():
                    result['terms'][term] = vals['definition']
            elif self.question.language in self.question.interview.terms and len(self.question.interview.terms[self.question.language]):
                for term, vals in self.question.interview.terms[self.question.language].items():
                    result['terms'][term] = vals['definition']
        if len(self.question.autoterms) or len(self.question.interview.autoterms):
            result['autoterms'] = dict()
            if 'autoterms' in self.extras:
                for term, vals in self.extras['autoterms'].items():
                    result['autoterms'][term] = vals['definition']
            if lang in self.question.interview.autoterms and len(self.question.interview.autoterms[lang]):
                for term, vals in question.interview.autoterms[lang].items():
                    result['autoterms'][term] = vals['definition']
            elif self.question.language in self.question.interview.autoterms and len(self.question.interview.autoterms[self.question.language]):
                for term, vals in self.question.interview.autoterms[self.question.language].items():
                    result['autoterms'][term] = vals['definition']
        if self.orig_sought is not None:
            result['event_list'] = [self.orig_sought]
        if 'action_buttons' in self.extras:
            result['additional_buttons'] = []
            for item in self.extras['action_buttons']:
                new_item = copy.deepcopy(item)
                new_item['label'] = docassemble.base.filter.markdown_to_html(item['label'], trim=True, do_terms=False, status=self, verbatim=(not encode))
                if debug:
                    output['question'] += '<p>' + new_item['label'] + '</p>'
        for param in ('questionText',):
            if hasattr(self, param) and getattr(self, param) is not None:
                result[param] = docassemble.base.filter.markdown_to_html(getattr(self, param).rstrip(), trim=True, status=self, verbatim=(not encode))
                if debug:
                    output['question'] += result[param]
        if hasattr(self, 'subquestionText') and self.subquestionText is not None:
            if self.question.question_type == "fields":
                embedder = dummy_embed_input
            else:
                embedder = None
            result['subquestionText'] = docassemble.base.filter.markdown_to_html(self.subquestionText.rstrip(), status=self, verbatim=(not encode), embedder=embedder)
            if debug:
                output['question'] += result['subquestionText']
        for param in ('continueLabel', 'helpLabel'):
            if hasattr(self, param) and getattr(self, param) is not None:
                result[param] = docassemble.base.filter.markdown_to_html(getattr(self, param).rstrip(), trim=True, do_terms=False, status=self, verbatim=(not encode))
                if debug:
                    output['question'] += '<p>' + result[param] + '</p>'
        if 'menu_items' in self.extras and isinstance(self.extras['menu_items'], list):
            result['menu_items'] = self.extras['menu_items']
        for param in ('cssClass', 'tableCssClass', 'css', 'script'):
            if param in self.extras and isinstance(self.extras[param], str):
                result[param] = self.extras[param].rstrip()
        for param in ('back_button_label',):
            if param in self.extras and isinstance(self.extras[param], str):
                result[param] = docassemble.base.filter.markdown_to_html(self.extras[param].rstrip(), trim=True, do_terms=False, status=self, verbatim=(not encode))
        for param in ('rightText', 'underText'):
            if param in self.extras and isinstance(self.extras[param], str):
                result[param] = docassemble.base.filter.markdown_to_html(self.extras[param].rstrip(), status=self, verbatim=(not encode))
                if debug:
                    output['question'] += result[param]
        if 'continueLabel' not in result:
            if self.question.question_type == "review":
                result['continueLabel'] = word('Resume')
            else:
                result['continueLabel'] = word('Continue')
            if debug:
                output['question'] += '<p>' + result['continueLabel'] + '</p>'
        if self.question.question_type == "yesno":
            result['yesLabel'] = self.question.yes()
            result['noLabel'] = self.question.no()
        elif self.question.question_type == "noyes":
            result['noLabel'] = self.question.yes()
            result['yesLabel'] = self.question.no()
        elif self.question.question_type == "yesnomaybe":
            result['yesLabel'] = self.question.yes()
            result['noLabel'] = self.question.no()
            result['maybeLabel'] = self.question.maybe()
        elif self.question.question_type == "noyesmaybe":
            result['noLabel'] = self.question.yes()
            result['yesLabel'] = self.question.no()
            result['maybeLabel'] = self.question.maybe()
        steps = the_user_dict['_internal']['steps'] - the_user_dict['_internal']['steps_offset']
        if self.can_go_back and steps > 1:
            result['allow_going_back'] = True
            result['backTitle'] = word("Go back to the previous question")
            back_button_val = self.extras.get('back_button', None)
            if (back_button_val or (back_button_val is None and self.question.interview.question_back_button)):
                result['questionBackButton'] = self.back
        else:
            result['allow_going_back'] = False
        if self.question.question_type == "signature":
            result['signaturePhrases'] = {
                'clear': word('Clear'),
                'noSignature': word("You must sign your name to continue."),
                'loading': word('Loading.  Please wait . . . '),
                }
        if 'questionMetadata' in self.extras:
            result['question_metadata'] = self.extras['questionMetadata']
        if 'segment' in self.extras:
            result['segment'] = self.extras['segment']
        if 'ga_id' in self.extras:
            result['ga_id'] = self.extras['ga_id']
        if hasattr(self.question, 'id'):
            result['id'] = self.question.id
        if hasattr(self, 'audiovideo') and self.audiovideo is not None:
            audio_result = docassemble.base.filter.get_audio_urls(self.audiovideo)
            video_result = docassemble.base.filter.get_video_urls(self.audiovideo)
            if len(audio_result) > 0:
                result['audio'] = [dict(url=re.sub(r'.*"(http[^"]+)".*', r'\1', x)) if isinstance(x, str) else dict(url=x[0], mime_type=x[1]) for x in audio_result]
            if len(video_result) > 0:
                result['video'] = [dict(url=re.sub(r'.*"(http[^"]+)".*', r'\1', x)) if isinstance(x, str) else dict(url=x[0], mime_type=x[1]) for x in video_result]
        if hasattr(self, 'helpText') and len(self.helpText) > 0:
            result['helpText'] = list()
            result['helpBackLabel'] = word("Back to question")
            for help_text in self.helpText:
                the_help = dict()
                if 'audiovideo' in help_text and help_text['audiovideo'] is not None:
                    audio_result = docassemble.base.filter.get_audio_urls(help_text['audiovideo'])
                    video_result = docassemble.base.filter.get_video_urls(help_text['audiovideo'])
                    if len(audio_result) > 0:
                        the_help['audio'] = [dict(url=x[0], mime_type=x[1]) for x in audio_result]
                    if len(video_result) > 0:
                        the_help['video'] = [dict(url=x[0], mime_type=x[1]) for x in video_result]
                if 'content' in help_text and help_text['content'] is not None:
                    the_help['content'] = docassemble.base.filter.markdown_to_html(help_text['content'].rstrip(), status=self, verbatim=(not encode))
                    if debug:
                        output['help'] += the_help['content']
                if 'heading' in help_text and help_text['heading'] is not None:
                    the_help['heading'] = help_text['heading'].rstrip()
                    if debug:
                        output['help'] += '<p>' + the_help['heading'] + '</p>'
                elif len(self.helpText) > 1:
                    the_help['heading'] = word('Help with this question')
                result['helpText'].append(the_help)
            result['help'] = dict()
            if self.helpText[0]['label']:
                result['help']['label'] = docassemble.base.filter.markdown_to_html(self.helpText[0]['label'], trim=True, do_terms=False, status=self, verbatim=(not encode))
            else:
                result['help']['label'] = self.question.help()
            result['help']['title'] = word("Help is available for this question")
            result['help']['specific'] = False if self.question.helptext is None else True
        if 'questionText' not in result and self.question.question_type == "signature":
            result['questionText'] = word('Sign Your Name')
            if debug:
                output['question'] += '<p>' + result['questionText'] + '</p>'
        result['questionType'] = self.question.question_type
        if hasattr(self.question, 'question_variety'):
            result['questionVariety'] = self.question.question_variety
        if self.question.is_mandatory or self.question.mandatory_code is not None:
            result['mandatory'] = True
        if hasattr(self.question, 'name'):
            result['_question_name'] = self.question.name
        result['_tracker'] = self.tracker
        if hasattr(self, 'datatypes'):
            result['_datatypes'] = safeid(json.dumps(self.datatypes))
        if hasattr(self, 'varnames'):
            result['_varnames'] = safeid(json.dumps(self.varnames))
        if len(self.question.fields) > 0:
            result['fields'] = list()
        if hasattr(self.question, 'review_saveas'):
            result['question_variable_name'] = self.question.review_saveas
        if hasattr(self.question, 'fields_saveas'):
            result['question_variable_name'] = self.question.fields_saveas
        if self.decorations is not None:
            width_value = get_config('decoration size', 2.0)
            width_units = get_config('decoration units', 'em')
            for decoration in self.decorations:
                if 'image' in decoration:
                    result['decoration'] = {}
                    the_image = self.question.interview.images.get(decoration['image'], None)
                    if the_image is not None:
                        the_url = docassemble.base.functions.server.url_finder(str(the_image.package) + ':' + str(the_image.filename))
                        width = str(width_value) + str(width_units)
                        filename = docassemble.base.functions.server.file_finder(str(the_image.package) + ':' + str(the_image.filename))
                        if 'extension' in filename and filename['extension'] == 'svg' and 'width' in filename:
                            if filename['width'] and filename['height']:
                                height = str(width_value * (filename['height']/filename['width'])) + str(width_units)
                        else:
                            height = 'auto'
                        if the_url is not None:
                            result['decoration']['url'] = the_url
                            result['decoration']['size'] = {"width": width, "height": height}
                            if the_image.attribution is not None:
                                self.attributions.add(the_image.attribution)
                            break
                    elif get_config('default icons', None) in ('material icons', 'font awesome'):
                        result['decoration']['name'] = decoration['image']
                        result['decoration']['size'] = str(width_value) + str(width_units)
                        break
        if len(self.attachments) > 0:
            result['attachments'] = list()
            if self.current_info['user']['is_authenticated'] and self.current_info['user']['email']:
                result['default_email'] = self.current_info['user']['email']
            for attachment in self.attachments:
                the_attachment = dict(url=dict(), number=dict(), filename_with_extension=dict())
                if 'orig_variable_name' in attachment and attachment['orig_variable_name']:
                    the_attachment['variable_name'] = attachment['orig_variable_name']
                if 'name' in attachment:
                    if attachment['name']:
                        the_attachment['name'] = docassemble.base.filter.markdown_to_html(attachment['name'], trim=True, status=self, verbatim=(not encode))
                        if debug:
                            output['question'] += '<p>' + the_attachment['name'] + '</p>'
                if 'description' in attachment:
                    if attachment['description']:
                        the_attachment['description'] = docassemble.base.filter.markdown_to_html(attachment['description'], status=self, verbatim=(not encode))
                        if debug:
                            output['question'] += the_attachment['description']
                for key in ('valid_formats', 'filename', 'content', 'markdown', 'raw'):
                    if key in attachment:
                        if attachment[key]:
                            the_attachment[key] = attachment[key]
                for the_format in attachment['file']:
                    the_attachment['url'][the_format] = docassemble.base.functions.server.url_finder(attachment['file'][the_format], filename=attachment['filename'] + '.' + extension_of_doc_format[the_format])
                    the_attachment['number'][the_format] = attachment['file'][the_format]
                    the_attachment['filename_with_extension'][the_format] = attachment['filename'] + '.' + extension_of_doc_format[the_format]
                result['attachments'].append(the_attachment)
        if self.extras.get('list_collect', False) is not False:
            result['listCollect'] = {
                'deleteLabel': word('Delete'),
                'addAnotherLabel': self.extras['list_collect_add_another_label'] if self.extras['list_collect_add_another_label'] else word("Add another"),
                'deletedLabel': word("(Deleted)"),
                'undeleteLabel': word("Undelete"),
            }
        validation_rules_used = set()
        file_fields = list()
        for field in self.question.fields:
            the_field = dict()
            the_field['number'] = field.number
            if hasattr(field, 'saveas'):
                the_field['variable_name'] = from_safeid(field.saveas)
                if encode:
                    the_field['variable_name_encoded'] = field.saveas
                the_field['validation_messages'] = dict()
                if self.question.question_type == 'multiple_choice' and self.question.question_variety in ["radio", "dropdown", "combobox"]:
                    if self.question.question_variety == 'combobox':
                         the_field['validation_messages']['required'] = field.validation_message('combobox required', self, word("You need to select one or type in a new value."))
                    else:
                        the_field['validation_messages']['required'] = field.validation_message('multiple choice required', self, word("You need to select one."))
                elif not (hasattr(field, 'datatype') and field.datatype in ['multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes']):
                    if hasattr(field, 'inputtype') and field.inputtype == 'combobox':
                        the_field['validation_messages']['required'] = field.validation_message('combobox required', self, word("You need to select one or type in a new value."))
                    elif hasattr(field, 'inputtype') and field.inputtype == 'ajax':
                        the_field['validation_messages']['required'] = field.validation_message('combobox required', self, word("You need to select one."))
                    elif hasattr(field, 'datatype') and (field.datatype == 'object_radio' or (hasattr(field, 'inputtype') and field.inputtype in ('yesnoradio', 'noyesradio', 'radio', 'dropdown'))):
                        the_field['validation_messages']['required'] = field.validation_message('multiple choice required', self, word("You need to select one."))
                    else:
                        the_field['validation_messages']['required'] = field.validation_message('required', self, word("This field is required."))
                if hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes', 'yesnowide', 'noyeswide'] and hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                    the_field['validation_messages']['uncheckothers'] = field.validation_message('checkboxes required', self, word("Check at least one option, or check “%s”"), parameters=tuple([strip_tags(self.labels[field.number])]))
                if hasattr(field, 'datatype') and field.datatype not in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                    for key in ('minlength', 'maxlength'):
                        if hasattr(field, 'extras') and key in field.extras and key in self.extras:
                            if key == 'minlength':
                                the_field['validation_messages'][key] = field.validation_message(key, self, word("You must type at least %s characters."), parameters=tuple([self.extras[key][field.number]]))
                            elif key == 'maxlength':
                                the_field['validation_messages'][key] = field.validation_message(key, self, word("You cannot type more than %s characters."), parameters=tuple([self.extras[key][field.number]]))
            if hasattr(field, 'datatype'):
                if field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes') and ((hasattr(field, 'nota') and self.extras['nota'][field.number] is not False) or (hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in self.extras) or ('maxlength' in field.extras and 'maxlength' in self.extras)))):
                    if field.datatype.endswith('checkboxes'):
                        d_type = 'checkbox'
                    else:
                        d_type = 'multiselect'
                    if hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in self.extras) or ('maxlength' in field.extras and 'maxlength' in self.extras)):
                        checkbox_messages = dict()
                        if 'minlength' in field.extras and 'minlength' in self.extras and 'maxlength' in field.extras and 'maxlength' in self.extras and self.extras['minlength'][field.number] == self.extras['maxlength'][field.number] and self.extras['minlength'][field.number] > 0:
                            if 'nota' not in self.extras:
                                self.extras['nota'] = dict()
                            self.extras['nota'][field.number] = False
                            if d_type == 'checkbox':
                                checkbox_messages['checkexactly'] = field.validation_message(d_type + ' minmaxlength', self, word("Please select exactly %s."), parameters=tuple([self.extras['maxlength'][field.number]]))
                            else:
                                checkbox_messages['selectexactly'] = field.validation_message(d_type + ' minmaxlength', self, word("Please select exactly %s."), parameters=tuple([self.extras['maxlength'][field.number]]))
                        else:
                            if 'minlength' in field.extras and 'minlength' in self.extras:
                                if d_type == 'checkbox':
                                    if self.extras['minlength'][field.number] == 1:
                                        checkbox_messages['checkatleast'] = field.validation_message('checkbox minlength', self, word("Please select one."))
                                    else:
                                        checkbox_messages['checkatleast'] = field.validation_message('checkbox minlength', self, word("Please select at least %s."), parameters=tuple([self.extras['minlength'][field.number]]))
                                    if int(float(self.extras['minlength'][field.number])) > 0:
                                        if 'nota' not in self.extras:
                                            self.extras['nota'] = dict()
                                        self.extras['nota'][field.number] = False
                                else:
                                    if self.extras['minlength'][field.number] == 1:
                                        checkbox_messages['minlength'] = field.validation_message(d_type + ' minlength', self, word("Please select one."))
                                    else:
                                        checkbox_messages['minlength'] = field.validation_message(d_type + ' minlength', self, word("Please select at least %s."), parameters=tuple([self.extras['minlength'][field.number]]))
                            if 'maxlength' in field.extras and 'maxlength' in self.extras:
                                if d_type == 'checkbox':
                                    checkbox_messages['checkatmost'] = field.validation_message(d_type + ' maxlength', self, word("Please select no more than %s."), parameters=tuple([self.extras['maxlength'][field.number]]))
                                else:
                                    checkbox_messages['maxlength'] = field.validation_message(d_type + ' maxlength', self, word("Please select no more than %s."), parameters=tuple([self.extras['maxlength'][field.number]]))
                        the_field['validation_messages'].update(checkbox_messages)
                    if d_type == 'checkbox':
                        if hasattr(field, 'nota') and self.extras['nota'][field.number] is not False:
                            the_field['validation_messages']['checkatleast'] = field.validation_message('checkboxes required', self, word("Check at least one option, or check “%s”"), parameters=tuple([self.extras['nota'][field.number]]))
                if field.datatype == 'date':
                    the_field['validation_messages']['date'] = field.validation_message('date', self, word("You need to enter a valid date."))
                    if hasattr(field, 'extras') and 'min' in field.extras and 'min' in self.extras and 'max' in field.extras and 'max' in self.extras and field.number in self.extras['min'] and field.number in self.extras['max']:
                        the_field['validation_messages']['minmax'] = field.validation_message('date minmax', self, word("You need to enter a date between %s and %s."), parameters=(docassemble.base.util.format_date(self.extras['min'][field.number], format='medium'), docassemble.base.util.format_date(self.extras['max'][field.number], format='medium')))
                    else:
                        was_defined = dict()
                        for key in ['min', 'max']:
                            if hasattr(field, 'extras') and key in field.extras and key in self.extras and field.number in self.extras[key]:
                                was_defined[key] = True
                                if key == 'min':
                                    the_field['validation_messages']['min'] = field.validation_message('date min', self, word("You need to enter a date on or after %s."), parameters=tuple([docassemble.base.util.format_date(self.extras[key][field.number], format='medium')]))
                                elif key == 'max':
                                    the_field['validation_messages']['max'] = field.validation_message('date max', self, word("You need to enter a date on or before %s."), parameters=tuple([docassemble.base.util.format_date(self.extras[key][field.number], format='medium')]))
                        if len(was_defined) == 0 and 'default date min' in self.question.interview.options and 'default date max' in self.question.interview.options:
                            the_field['min'] = docassemble.base.util.format_date(self.question.interview.options['default date min'], format='yyyy-MM-dd')
                            the_field['max'] = docassemble.base.util.format_date(self.question.interview.options['default date max'], format='yyyy-MM-dd')
                            the_field['validation_messages']['minmax'] = field.validation_message('date minmax', self, word("You need to enter a date between %s and %s."), parameters=(docassemble.base.util.format_date(self.question.interview.options['default date min'], format='medium'), docassemble.base.util.format_date(self.question.interview.options['default date max'], format='medium')))
                        elif 'max' not in was_defined and 'default date max' in self.question.interview.options:
                            the_field['max'] = docassemble.base.util.format_date(self.question.interview.options['default date max'], format='yyyy-MM-dd')
                            the_field['validation_messages']['max'] = field.validation_message('date max', self, word("You need to enter a date on or before %s."), parameters=tuple([docassemble.base.util.format_date(self.question.interview.options['default date max'], format='medium')]))
                        elif 'min' not in was_defined and 'default date min' in self.question.interview.options:
                            the_field['min'] = docassemble.base.util.format_date(self.question.interview.options['default date min'], format='yyyy-MM-dd')
                            the_field['validation_messages']['min'] = field.validation_message('date min', self, word("You need to enter a date on or after %s."), parameters=tuple([docassemble.base.util.format_date(self.question.interview.options['default date min'], format='medium')]))
                if field.datatype == 'time':
                    the_field['validation_messages']['time'] = field.validation_message('time', self, word("You need to enter a valid time."))
                if field.datatype in ['datetime', 'datetime-local']:
                    the_field['validation_messages']['datetime'] = field.validation_message('datetime', self, word("You need to enter a valid date and time."))
                if field.datatype == 'email':
                    the_field['validation_messages']['email'] = field.validation_message('email', self, word("You need to enter a complete e-mail address."))
                if field.datatype in ['number', 'currency', 'float', 'integer']:
                    the_field['validation_messages']['number'] = field.validation_message('number', self, word("You need to enter a number."))
                    if field.datatype == 'integer' and not ('step' in self.extras and field.number in self.extras['step']):
                        the_field['validation_messages']['step'] = field.validation_message('integer', self, word("Please enter a whole number."))
                    elif 'step' in self.extras and field.number in self.extras['step']:
                        the_field['validation_messages']['step'] = field.validation_message('step', self, word("Please enter a multiple of {0}."))
                    for key in ['min', 'max']:
                        if hasattr(field, 'extras') and key in field.extras and key in self.extras and field.number in self.extras[key]:
                            if key == 'min':
                                the_field['validation_messages'][key] = field.validation_message('min', self, word("You need to enter a number that is at least %s."), parameters=tuple([self.extras[key][field.number]]))
                            elif key == 'max':
                                the_field['validation_messages'][key] = field.validation_message('max', self, word("You need to enter a number that is at most %s."), parameters=tuple([self.extras[key][field.number]]))
                if (field.datatype in ['files', 'file', 'camera', 'user', 'environment', 'camcorder', 'microphone']):
                    file_fields.append(field)
                    the_field['validation_messages']['required'] = field.validation_message('file required', self, word("You must provide a file."))
                    if 'accept' in self.extras and field.number in self.extras['accept']:
                        the_field['validation_messages']['accept'] = field.validation_message('accept', self, word("Please upload a file with a valid file format."))
                    if get_config('maximum content length') is not None:
                        the_field['max'] = get_config('maximum content length')
                        the_field['validation_messages']['max'] = field.validation_message('maxuploadsize', self, word("Your file upload is larger than the server can accept. Please reduce the size of your file upload."))
            for param in ('datatype', 'fieldtype', 'sign', 'inputtype', 'address_autocomplete'):
                if hasattr(field, param):
                    the_field[param] = getattr(field, param)
            if hasattr(field, 'shuffle') and field.shuffle is not False:
                the_field['shuffle'] = True
            if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                the_field['disable_others'] = True
            if hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                the_field['uncheck_others'] = True
            for key in ('minlength', 'maxlength', 'min', 'max', 'step', 'scale', 'inline', 'inline width', 'rows', 'accept', 'currency symbol', 'field metadata'):
                if key in self.extras and field.number in self.extras[key]:
                    if key in ('minlength', 'maxlength', 'min', 'max', 'step'):
                        validation_rules_used.add(key)
                    the_field[key] = self.extras[key][field.number]
            if hasattr(field, 'saveas') and field.saveas in self.embedded:
                the_field['embedded'] = True
            if hasattr(self, 'shuffle'):
                the_field['shuffle'] = self.shuffle
            if field.number in self.defaults:
                the_default = self.defaults[field.number]
                if isinstance(the_default, (str, int, bool, float)):
                    the_field['default'] = the_default
            else:
                the_default = None
            if self.question.question_type == 'multiple_choice' or hasattr(field, 'choicetype') or (hasattr(field, 'datatype') and field.datatype in ('object', 'multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes', 'object_radio')):
                the_field['choices'] = self.get_choices_data(field, the_default, the_user_dict, encode=encode)
            if hasattr(field, 'nota'):
                the_field['none_of_the_above'] = docassemble.base.filter.markdown_to_html(self.extras['nota'][field.number], do_terms=False, status=self, verbatim=(not encode))
            the_field['active'] = self.extras['ok'][field.number]
            if field.number in self.extras['required']:
                the_field['required'] = self.extras['required'][field.number]
                if the_field['required']:
                    validation_rules_used.add('required')
            if 'validation messages' in self.extras and field.number in self.extras['validation messages']:
                the_field['validation_messages'].update(self.extras['validation messages'][field.number])
            if 'permissions' in self.extras:
                the_field['permissions'] = self.extras['permissions'][field.number]
            if hasattr(field, 'datatype') and field.datatype in ('file', 'files', 'camera', 'user', 'environment') and 'max_image_size' in self.extras and self.extras['max_image_size']:
                the_field['max_image_size'] = self.extras['max_image_size']
            if hasattr(field, 'datatype') and field.datatype in ('file', 'files', 'camera', 'user', 'environment') and 'image_type' in self.extras and self.extras['image_type']:
                the_field['image_type'] = self.extras['image_type']
            if hasattr(field, 'extras'):
                if 'ml_group' in field.extras or 'ml_train' in field.extras:
                    the_field['ml_info'] = dict()
                    if 'ml_group' in field.extras:
                        the_field['ml_info']['group_id'] = self.extras['ml_group'][field.number]
                    if 'ml_train' in field.extras:
                        the_field['ml_info']['train'] = self.extras['ml_train'][field.number]
                if 'show_if_var' in field.extras and 'show_if_val' in self.extras:
                    the_field['show_if_sign'] = field.extras['show_if_sign']
                    the_field['show_if_var'] = from_safeid(field.extras['show_if_var'])
                    the_field['show_if_val'] = self.extras['show_if_val'][field.number]
                if 'show_if_js' in field.extras:
                    the_field['show_if_js'] = dict(expression=field.extras['show_if_js']['expression'].text(the_user_dict), vars=field.extras['show_if_js']['vars'], sign=field.extras['show_if_js']['sign'], mode=field.extras['show_if_js']['mode'])
            if 'note' in self.extras and field.number in self.extras['note']:
                the_field['note'] = docassemble.base.filter.markdown_to_html(self.extras['note'][field.number], status=self, verbatim=(not encode))
            if 'html' in self.extras and field.number in self.extras['html']:
                the_field['html'] = self.extras['html'][field.number]
            if field.number in self.hints:
                the_field['hint'] = self.hints[field.number]
                if debug:
                    output['question'] += '<p>' + the_field['hint'] + '</p>'
            if field.number in self.labels:
                the_field['label'] = docassemble.base.filter.markdown_to_html(self.labels[field.number], trim=True, status=self, verbatim=(not encode))
                if debug:
                    output['question'] += '<p>' + the_field['label'] + '</p>'
            if field.number in self.helptexts:
                the_field['helptext'] = docassemble.base.filter.markdown_to_html(self.helptexts[field.number], status=self, verbatim=(not encode))
                if debug:
                    output['question'] += the_field['helptext']
            if self.question.question_type in ("yesno", "yesnomaybe"):
                the_field['true_label'] = docassemble.base.filter.markdown_to_html(self.question.yes(), trim=True, do_terms=False, status=self, verbatim=(not encode))
                the_field['false_label'] = docassemble.base.filter.markdown_to_html(self.question.no(), trim=True, do_terms=False, status=self, verbatim=(not encode))
                if debug:
                    output['question'] += '<p>' + the_field['true_label'] + '</p>'
                    output['question'] += '<p>' + the_field['false_label'] + '</p>'
            if self.question.question_type == 'yesnomaybe':
                the_field['maybe_label'] = docassemble.base.filter.markdown_to_html(self.question.maybe(), trim=True, do_terms=False, status=self, verbatim=(not encode))
                if debug:
                    output['question'] += '<p>' + the_field['maybe_label'] + '</p>'
            result['fields'].append(the_field)
        if len(self.attributions):
            result['attributions'] = [x.rstrip() for x in self.attributions]
        if 'track_location' in self.extras and self.extras['track_location']:
            result['track_location'] = True
        if 'inverse navbar' in self.question.interview.options:
            if self.question.interview.options['inverse navbar']:
                result['navbarVariant'] = 'dark'
            else:
                result['navbarVariant'] = 'light'
        elif get_config('inverse navbar', True):
            result['navbarVariant'] = 'dark'
        else:
            result['navbarVariant'] = 'light'
        if debug:
            readability = dict()
            for question_type in ('question', 'help'):
                if question_type not in output:
                    continue
                phrase = docassemble.base.functions.server.to_text(output[question_type])
                if (not phrase) or len(phrase) < 10:
                    phrase = "The sky is blue."
                phrase = re.sub(r'[^A-Za-z 0-9\.\,\?\#\!\%\&\(\)]', r' ', phrase)
                readability[question_type] = [('Flesch Reading Ease', textstat.flesch_reading_ease(phrase)),
                                              ('Flesch-Kincaid Grade Level', textstat.flesch_kincaid_grade(phrase)),
                                              ('Gunning FOG Scale', textstat.gunning_fog(phrase)),
                                              ('SMOG Index', textstat.smog_index(phrase)),
                                              ('Automated Readability Index', textstat.automated_readability_index(phrase)),
                                              ('Coleman-Liau Index', textstat.coleman_liau_index(phrase)),
                                              ('Linsear Write Formula', textstat.linsear_write_formula(phrase)),
                                              ('Dale-Chall Readability Score', textstat.dale_chall_readability_score(phrase)),
                                              ('Readability Consensus', textstat.text_standard(phrase))]
            result['source'] = {'label': word("Source"), 'title': word("How this question came to be asked"), 'history': self.get_history(), 'readability': readability}
        return result
    def get_choices(self, field, the_user_dict):
        question = self.question
        choice_list = list()
        if hasattr(field, 'saveas') and field.saveas is not None:
            saveas = from_safeid(field.saveas)
            if self.question.question_type == "multiple_choice":
                #if hasattr(field, 'has_code') and field.has_code:
                pairlist = list(self.selectcompute[field.number])
                for pair in pairlist:
                    choice_list.append([pair['label'], saveas, pair['key']])
            elif hasattr(field, 'choicetype'):
                if field.choicetype in ('compute', 'manual'):
                    pairlist = list(self.selectcompute[field.number])
                elif field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                    pairlist = list()
                if field.datatype in ('object_multiselect', 'object_checkboxes'):
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas, from_safeid(pair['key'])])
                elif field.datatype in ('object', 'object_radio'):
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas, from_safeid(pair['key'])])
                elif field.datatype in ('multiselect', 'checkboxes'):
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas + "[" + repr(pair['key']) + "]", True])
                else:
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas, pair['key']])
                if hasattr(field, 'nota') and (field.datatype.endswith('checkboxes') and self.extras['nota'][field.number] is not False): #or (field.datatype.endswith('multiselect') and self.extras['nota'][field.number] is True)
                    if self.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = self.extras['nota'][field.number]
                    choice_list.append([formatted_item, None, None])
        else:
            indexno = 0
            for choice in self.selectcompute[field.number]:
                choice_list.append([choice['label'], '_internal["answers"][' + repr(question.extended_question_name(the_user_dict)) + ']', indexno])
                indexno += 1
        return choice_list
    def icon_url(self, name):
        the_image = self.question.interview.images.get(name, None)
        if the_image is None:
            return None
        if the_image.attribution is not None:
            self.attributions.add(the_image.attribution)
        url = docassemble.base.functions.server.url_finder(str(the_image.package) + ':' + str(the_image.filename))
        return url
    def get_choices_data(self, field, defaultvalue, the_user_dict, encode=True):
        question = self.question
        choice_list = list()
        if hasattr(field, 'saveas') and field.saveas is not None:
            saveas = from_safeid(field.saveas)
            if self.question.question_type == "multiple_choice":
                pairlist = list(self.selectcompute[field.number])
                for pair in pairlist:
                    item = dict(label=docassemble.base.filter.markdown_to_html(pair['label'], trim=True, do_terms=False, status=self, verbatim=encode), value=pair['key'])
                    if 'help' in pair:
                        item['help'] = docassemble.base.filter.markdown_to_html(pair['help'].rstrip(), trim=True, do_terms=False, status=self, verbatim=encode)
                    if 'default' in pair:
                        item['default'] = pair['default']
                    if 'image' in pair:
                        if isinstance(pair['image'], dict):
                            if pair['image']['type'] == 'url':
                                item['image'] = pair['image']['value']
                            else:
                                item['image'] = self.icon_url(pair['image']['value'])
                        else:
                            item['image'] = self.icon_url(pair['image'])
                    choice_list.append(item)
            elif hasattr(field, 'choicetype'):
                if field.choicetype in ('compute', 'manual'):
                    pairlist = list(self.selectcompute[field.number])
                elif field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                    pairlist = list()
                if field.datatype in ('object_multiselect', 'object_checkboxes'):
                    for pair in pairlist:
                        item = dict(label=docassemble.base.filter.markdown_to_html(pair['label'], trim=True, do_terms=False, status=self, verbatim=encode), value=from_safeid(pair['key']))
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (list, set)) and str(pair['key']) in defaultvalue) or (isinstance(defaultvalue, dict) and str(pair['key']) in defaultvalue and defaultvalue[str(pair['key'])]) or (isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                            item['selected'] = True
                        if 'help' in pair:
                            item['help'] = pair['help']
                        choice_list.append(item)
                elif field.datatype in ('object', 'object_radio'):
                    for pair in pairlist:
                        item = dict(label=docassemble.base.filter.markdown_to_html(pair['label'], trim=True, do_terms=False, status=self, verbatim=encode), value=from_safeid(pair['key']))
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                            item['selected'] = True
                        if 'default' in pair:
                            item['default'] = str(pair['default'])
                        if 'help' in pair:
                            item['help'] = pair['help']
                        choice_list.append(item)
                elif field.datatype in ('multiselect', 'checkboxes'):
                    for pair in pairlist:
                        item = dict(label=docassemble.base.filter.markdown_to_html(pair['label'], trim=True, do_terms=False, status=self, verbatim=encode), variable_name=saveas + "[" + repr(pair['key']) + "]", value=True)
                        if encode:
                            item['variable_name_encoded'] = safeid(saveas + "[" + repr(pair['key']) + "]")
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (list, set)) and str(pair['key']) in defaultvalue) or (isinstance(defaultvalue, dict) and str(pair['key']) in defaultvalue and defaultvalue[str(pair['key'])]) or (isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                            item['selected'] = True
                        if 'help' in pair:
                            item['help'] = pair['help']
                        choice_list.append(item)
                else:
                    for pair in pairlist:
                        item = dict(label=docassemble.base.filter.markdown_to_html(pair['label'], trim=True, do_terms=False, status=self, verbatim=encode), value=pair['key'])
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                            item['selected'] = True
                        choice_list.append(item)
                if hasattr(field, 'nota') and self.extras['nota'][field.number] is not False:
                    if self.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = self.extras['nota'][field.number]
                    choice_list.append(dict(label=docassemble.base.filter.markdown_to_html(formatted_item, trim=True, do_terms=False, status=self, verbatim=encode)))
        else:
            indexno = 0
            for choice in self.selectcompute[field.number]:
                item = dict(label=docassemble.base.filter.markdown_to_html(choice['label'], trim=True, do_terms=False, status=self, verbatim=encode), variable_name='_internal["answers"][' + repr(question.extended_question_name(the_user_dict)) + ']', value=indexno)
                if encode:
                    item['variable_name_encoded'] = safeid('_internal["answers"][' + repr(question.extended_question_name(the_user_dict)) + ']')
                if 'image' in choice:
                    the_image = self.icon_url(choice['image'])
                    if the_image:
                        item['image'] = the_image
                if 'help' in choice:
                    item['help'] = choice['help']
                if 'default' in choice:
                    item['default'] = choice['default']
                choice_list.append(item)
                indexno += 1
        return choice_list

# def new_counter(initial_value=0):
#     d = {'counter': initial_value}
#     def f():
#         return_value = d['counter']
#         d['counter'] += 1
#         return(return_value)
#     return f

# increment_question_counter = new_counter()

class TextObject:
    def __deepcopy__(self, memo):
        return TextObject(self.original_text)
    def __init__(self, x, question=None, translate=True):
        self.original_text = x
        self.other_lang = dict()
        if translate and question is not None and question.interview.source.translating and isinstance(x, str) and re.search(r'[^\s0-9]', self.original_text) and not re.search(r'\<%doc\>\s*do not translate', self.original_text, re.IGNORECASE) and self.original_text != 'no label':
            if not hasattr(question, 'translations'):
                question.translations = list()
            if self.original_text not in question.translations:
                question.translations.append(self.original_text)
        if isinstance(x, str) and match_mako.search(x):
            if question is None:
                names_used = set()
            else:
                names_used = question.names_used
            self.template = MakoTemplate(x, strict_undefined=True, input_encoding='utf-8')
            for x in self.template.names_used - self.template.names_set:
                names_used.add(x)
            self.uses_mako = True
        else:
            self.uses_mako = False
        if translate and question is not None and len(question.interview.translations) and isinstance(x, str):
            if self.original_text in question.interview.translation_dict:
                if question.language == '*':
                    self.language = docassemble.base.functions.server.default_language
                else:
                    self.language = question.language
                for orig_lang in question.interview.translation_dict[self.original_text]:
                    if orig_lang == question.language or (question.language == '*' and orig_lang == docassemble.base.functions.server.default_language):
                        for target_lang in question.interview.translation_dict[self.original_text][orig_lang]:
                            if self.uses_mako:
                                self.other_lang[target_lang] = (question.interview.translation_dict[self.original_text][orig_lang][target_lang], MakoTemplate(question.interview.translation_dict[self.original_text][orig_lang][target_lang], strict_undefined=True, input_encoding='utf-8'))
                            else:
                                self.other_lang[target_lang] = (question.interview.translation_dict[self.original_text][orig_lang][target_lang],)
    def text(self, the_user_dict):
        if len(self.other_lang):
            target_lang = docassemble.base.functions.get_language()
            if self.language != target_lang and target_lang in self.other_lang:
                if self.uses_mako:
                    return(self.other_lang[target_lang][1].render(**the_user_dict))
                else:
                    return(self.other_lang[target_lang][0])
        if self.uses_mako:
            return(self.template.render(**the_user_dict))
        else:
            return(self.original_text)

def myb64quote(text):
    return "'" + re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode()) + "'"

def safeid(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode())

def from_safeid(text):
    return(codecs.decode(repad(bytearray(text, encoding='utf-8')), 'base64').decode('utf8'))

def repad(text):
    return text + (equals_byte * ((4 - len(text) % 4) % 4))

class Field:
    def __init__(self, data):
        if 'number' in data:
            self.number = data['number']
        else:
            self.number = 0
        if 'saveas' in data:
            self.saveas = safeid(data['saveas'])
        if 'saveas_code' in data:
            self.saveas_code = data['saveas_code']
        if 'showif_code' in data:
            self.showif_code = data['showif_code']
        if 'action' in data:
            self.action = data['action']
        if 'label' in data:
            self.label = data['label']
        if 'type' in data:
            self.datatype = data['type']
        if 'choicetype' in data:
            self.choicetype = data['choicetype']
        if 'disable others' in data:
            self.disableothers = data['disable others']
        if 'uncheck others' in data:
            self.uncheckothers = data['uncheck others']
        if 'default' in data:
            self.default = data['default']
        if 'combobox action' in data:
            self.combobox_action = data['combobox action']
        if 'hint' in data:
            self.hint = data['hint']
        if 'data' in data:
            self.data = data['data']
        if 'help' in data:
            self.helptext = data['help']
        if 'validate' in data:
            self.validate = data['validate']
        if 'validation messages' in data:
            self.validation_messages = data['validation messages']
        if 'address_autocomplete' in data:
            self.address_autocomplete = data['address_autocomplete']
        if 'max_image_size' in data:
            self.max_image_size = data['max_image_size']
        if 'image_type' in data:
            self.image_type = data['image_type']
        if 'accept' in data:
            self.accept = data['accept']
        if 'persistent' in data or 'private' in data or 'allow_users' in data or 'allow_privileges' in data:
            self.permissions = dict(persistent=data.get('persistent', None), private=data.get('private', None), allow_users=data.get('allow_users', None), allow_privileges=data.get('allow_privileges', None))
        if 'rows' in data:
            self.rows = data['rows']
        if 'object_labeler' in data:
            self.object_labeler = data['object_labeler']
        if 'help_generator' in data:
            self.help_generator = data['help_generator']
        if 'image_generator' in data:
            self.image_generator = data['image_generator']
        if 'extras' in data:
            self.extras = data['extras']
        if 'selections' in data:
            self.selections = data['selections']
        if 'boolean' in data:
            self.datatype = 'boolean'
            self.sign = data['boolean']
            if 'type' in data:
                self.inputtype = data['type']
        if 'threestate' in data:
            self.datatype = 'threestate'
            self.sign = data['threestate']
            if 'type' in data:
                self.inputtype = data['type']
        if 'choices' in data:
            self.fieldtype = 'multiple_choice'
            self.choices = data['choices']
        if 'inputtype' in data:
            self.inputtype = data['inputtype']
        if 'has_code' in data:
            self.has_code = True
        # if 'script' in data:
        #     self.script = data['script']
        # if 'css' in data:
        #     self.css = data['css']
        if 'shuffle' in data:
            self.shuffle = data['shuffle']
        if 'nota' in data:
            self.nota = data['nota']
        if 'required' in data:
            self.required = data['required']
        else:
            self.required = True
    def validation_message(self, validation_type, status, default_message, parameters=None):
        message = None
        if 'validation messages' in status.extras and self.number in status.extras['validation messages']:
            validation_type_tail = re.sub(r'.* ', '', validation_type)
            if validation_type in status.extras['validation messages'][self.number]:
                message = status.extras['validation messages'][self.number][validation_type]
            elif validation_type != validation_type_tail and validation_type_tail in status.extras['validation messages'][self.number]:
                message = status.extras['validation messages'][self.number][validation_type_tail]
        if message is None and status.question.language in status.question.interview.default_validation_messages and validation_type in status.question.interview.default_validation_messages[status.question.language]:
            message = status.question.interview.default_validation_messages[status.question.language][validation_type]
        if message is None:
            message = default_message
        if parameters is not None and len(parameters) > 0:
            try:
                message = message % parameters
            except TypeError:
                pass
        return message

def recursive_eval_dataobject(target, the_user_dict):
    if isinstance(target, dict) or (hasattr(target, 'elements') and isinstance(target.elements, dict)):
        new_dict = dict()
        for key, val in target.items():
            new_dict[key] = recursive_eval_dataobject(val, the_user_dict)
        return new_dict
    if isinstance(target, list) or (hasattr(target, 'elements') and isinstance(target.elements, list)):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_eval_dataobject(val, the_user_dict))
        return new_list
    if isinstance(target, set) or (hasattr(target, 'elements') and isinstance(target.elements, set)):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_eval_dataobject(val, the_user_dict))
        return new_set
    if isinstance(target, (bool, float, int, NoneType)):
        return target
    if isinstance(target, TextObject):
        return target.text(the_user_dict)
    else:
        raise DAError("recursive_eval_dataobject: expected a TextObject, but found a " + str(type(target)))

def recursive_eval_data_from_code(target, the_user_dict):
    if isinstance(target, dict):
        new_dict = dict()
        for key, val in target.items():
            new_dict[key] = recursive_eval_data_from_code(val, the_user_dict)
        return new_dict
    if isinstance(target, list):
        new_list = list()
        for val in target:
            new_list.append(recursive_eval_data_from_code(val, the_user_dict))
        return new_list
    if isinstance(target, set):
        new_set = set()
        for val in target:
            new_set.add(recursive_eval_data_from_code(val, the_user_dict))
        return new_set
    if isinstance(target, CodeType):
        return eval(target, the_user_dict)
    else:
        return target

def recursive_textobject(target, question):
    if isinstance(target, dict) or (hasattr(target, 'elements') and isinstance(target.elements, dict)):
        new_dict = dict()
        for key, val in target.items():
            new_dict[key] = recursive_textobject(val, question)
        return new_dict
    if isinstance(target, list) or (hasattr(target, 'elements') and isinstance(target.elements, list)):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_textobject(val, question))
        return new_list
    if isinstance(target, set) or (hasattr(target, 'elements') and isinstance(target.elements, set)):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_textobject(val, question))
        return new_set
    return TextObject(str(target), question=question)

def recursive_eval_textobject(target, the_user_dict, question, tpl, skip_undefined):
    if isinstance(target, dict) or (hasattr(target, 'elements') and isinstance(target.elements, dict)):
        new_dict = dict()
        for key, val in target.items():
            new_dict[key] = recursive_eval_textobject(val, the_user_dict, question, tpl, skip_undefined)
        return new_dict
    if isinstance(target, list) or (hasattr(target, 'elements') and isinstance(target.elements, list)):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_eval_textobject(val, the_user_dict, question, tpl, skip_undefined))
        return new_list
    if isinstance(target, set) or (hasattr(target, 'elements') and isinstance(target.elements, set)):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_eval_textobject(val, the_user_dict, question, tpl, skip_undefined))
        return new_set
    if isinstance(target, (bool, NoneType)):
        return target
    if isinstance(target, TextObject):
        if skip_undefined:
            try:
                text = target.text(the_user_dict)
            except:
                text = ''
        else:
            text = target.text(the_user_dict)
        return docassemble.base.file_docx.transform_for_docx(text, question, tpl)
    else:
        raise DAError("recursive_eval_textobject: expected a TextObject, but found a " + str(type(target)))

def recursive_textobject_or_primitive(target, question):
    if isinstance(target, dict) or (hasattr(target, 'elements') and isinstance(target.elements, dict)):
        new_dict = dict()
        for key, val in target.items():
            new_dict[key] = recursive_textobject_or_primitive(val, question)
        return new_dict
    if isinstance(target, list) or (hasattr(target, 'elements') and isinstance(target.elements, list)):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_textobject_or_primitive(val, question))
        return new_list
    if isinstance(target, set) or (hasattr(target, 'elements') and isinstance(target.elements, set)):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_textobject_or_primitive(val, question))
        return new_set
    if isinstance(target, (int, bool, float, NoneType)):
        return target
    return TextObject(str(target), question=question)

def recursive_eval_textobject_or_primitive(target, the_user_dict):
    if isinstance(target, dict) or (hasattr(target, 'elements') and isinstance(target.elements, dict)):
        new_dict = dict()
        for key, val in target.items():
            new_dict[key] = recursive_eval_textobject_or_primitive(val, the_user_dict)
        return new_dict
    if isinstance(target, list) or (hasattr(target, 'elements') and isinstance(target.elements, list)):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_eval_textobject_or_primitive(val, the_user_dict))
        return new_list
    if isinstance(target, set) or (hasattr(target, 'elements') and isinstance(target.elements, set)):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_eval_textobject_or_primitive(val, the_user_dict))
        return new_set
    if isinstance(target, (bool, int, float, NoneType)):
        return target
    if isinstance(target, TextObject):
        return target.text(the_user_dict)
    else:
        raise DAError("recursive_eval_textobject_or_primitive: expected a TextObject, but found a " + str(type(target)))

def fix_quotes(match):
    instring = match.group(1)
    n = len(instring)
    output = ''
    i = 0
    while i < n:
        if instring[i] == '\u201c' or instring[i] == '\u201d':
            output += '"'
        elif instring[i] == '\u2018' or instring[i] == '\u2019':
            output += "'"
        elif instring[i] == '&' and i + 4 < n and instring[i:i+5] == '&amp;':
            output += '&'
            i += 4
        else:
            output += instring[i]
        i += 1
    return output

def docx_variable_fix(variable):
    variable = re.sub(r'\\', '', variable)
    variable = re.sub(r'^([A-Za-z\_][A-Za-z\_0-9]*).*', r'\1', variable)
    return variable

def url_sanitize(url):
    return re.sub(r'\s', ' ', url)

class FileInPackage:
    def __init__(self, fileref, area, package):
        if area == 'template' and not isinstance(fileref, dict):
            docassemble.base.functions.package_template_filename(fileref, package=package)
        self.fileref = fileref
        if isinstance(self.fileref, dict):
            self.is_code = True
            if 'code' not in self.fileref:
                raise DAError("A docx or pdf template file expressed in the form of a dictionary must have 'code' as the key" + str(self.fileref))
            self.code = compile(self.fileref['code'], '<template file code>', 'eval')
        else:
            self.is_code = False
        self.area = area
        self.package = package
    def path(self, the_user_dict=dict()):
        if self.area == 'template':
            if self.is_code:
                if len(the_user_dict) == 0:
                    raise Exception("FileInPackage.path: called with empty dict")
                the_file_ref = eval(self.code, the_user_dict)
                if isinstance(the_file_ref, list) and len(the_file_ref):
                    the_file_ref = the_file_ref[0]
                if the_file_ref.__class__.__name__ == 'DAFile':
                    the_file_ref = the_file_ref.path()
                elif the_file_ref.__class__.__name__ == 'DAFileList' and len(the_file_ref.elements) > 0:
                    the_file_ref = the_file_ref.elements[0].path()
                elif the_file_ref.__class__.__name__ == 'DAStaticFile':
                    the_file_ref = the_file_ref.path()
                elif re.search(r'^https?://', str(the_file_ref)):
                    temp_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
                    try:
                        urlretrieve(url_sanitize(str(the_file_ref)), temp_template_file.name)
                    except Exception as err:
                        raise DAError("FileInPackage: error downloading " + str(the_file_ref) + ": " + str(err))
                    the_file_ref = temp_template_file.name
                if not str(the_file_ref).startswith('/'):
                    the_file_ref = docassemble.base.functions.package_template_filename(str(the_file_ref), package=self.package)
                return the_file_ref
            else:
                return docassemble.base.functions.package_template_filename(self.fileref, package=self.package)
    def paths(self, the_user_dict=dict()):
        if self.area == 'template':
            result = []
            if self.is_code:
                if len(the_user_dict) == 0:
                    raise Exception("FileInPackage.path: called with empty dict")
                the_file_refs = eval(self.code, the_user_dict)
                if not isinstance(the_file_refs, list):
                    the_file_refs = [the_file_refs]
                for the_file_ref in the_file_refs:
                    if the_file_ref.__class__.__name__ == 'DAFile':
                        result.append(the_file_ref.path())
                    elif the_file_ref.__class__.__name__ == 'DAFileList' and len(the_file_ref.elements) > 0:
                        for item in the_file_ref.elements:
                            result.append(item.path())
                    elif the_file_ref.__class__.__name__ == 'DAStaticFile':
                        result.append(the_file_ref.path())
                    elif re.search(r'^https?://', str(the_file_ref)):
                        temp_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
                        try:
                            urlretrieve(url_sanitize(str(the_file_ref)), temp_template_file.name)
                        except Exception as err:
                            raise DAError("FileInPackage: error downloading " + str(the_file_ref) + ": " + str(err))
                        result.append(temp_template_file.name)
                    else:
                        result.append(the_file_ref)
            else:
                result.append(docassemble.base.functions.package_template_filename(self.fileref, package=self.package))
            final_result = []
            for the_file_ref in result:
                if not str(the_file_ref).startswith('/'):
                    final_result.append(docassemble.base.functions.package_template_filename(str(the_file_ref), package=self.package))
                else:
                    final_result.append(the_file_ref)
            return final_result

class FileOnServer:
    def __init__(self, fileref, question):
        self.fileref = fileref
        self.question = question
    def path(self):
        info = docassemble.base.functions.server.file_finder(self.fileref, question=self.question)
        if 'fullpath' in info and info['fullpath']:
            return info['fullpath']
        raise DAError("Could not find the file " + str(self.fileref))

class Question:
    def idebug(self, data):
        if hasattr(self, 'from_source') and hasattr(self, 'package'):
            return "\nIn file " + str(self.from_source.path) + " from package " + str(self.package) + ":\n\n" + yaml.dump(data)
        else:
            return yaml.dump(data)
    def __init__(self, orig_data, caller, **kwargs):
        if not isinstance(orig_data, dict):
            raise DAError("A block must be in the form of a dictionary." + self.idebug(orig_data))
        data = dict()
        for key, value in orig_data.items():
            data[key.lower()] = value
        should_append = True
        if 'register_target' in kwargs:
            register_target = kwargs['register_target']
            main_list = False
        else:
            register_target = self
            main_list = True
        self.from_source = kwargs.get('source', None)
        self.package = kwargs.get('package', None)
        self.interview = caller
        if self.interview.debug:
            self.source_code = kwargs.get('source_code', None)
        self.fields = []
        self.attachments = []
        self.is_generic = False
        self.name = None
        self.role = list()
        self.condition = list()
        self.terms = dict()
        self.autoterms = dict()
        self.need = None
        self.need_post = None
        self.scan_for_variables = True
        self.embeds = False
        self.helptext = None
        self.subcontent = None
        self.reload_after = None
        self.continuelabel = None
        self.backbuttonlabel = None
        self.cornerbackbuttonlabel = None
        self.helplabel = None
        self.progress = None
        self.section = None
        self.script = None
        self.css = None
        self.checkin = None
        self.target = None
        self.decorations = None
        self.audiovideo = None
        self.compute_attachment = None
        self.can_go_back = True
        self.other_fields_used = set()
        self.fields_used = set()
        self.fields_for_invalidation = set()
        self.fields_for_onchange = set()
        self.names_used = set()
        self.mako_names = set()
        self.reconsider = list()
        self.undefine = list()
        self.action_buttons = list()
        self.validation_code = None
        num_directives = 0
        for directive in ('yesno', 'noyes', 'yesnomaybe', 'noyesmaybe', 'fields', 'buttons', 'choices', 'dropdown', 'combobox', 'signature', 'review'):
            if directive in data:
                num_directives += 1
        if num_directives > 1:
            raise DAError("There can only be one directive in a question.  You had more than one.\nThe directives are yesno, noyes, yesnomaybe, noyesmaybe, fields, buttons, choices, dropdown, combobox, and signature." + self.idebug(data))
        if num_directives > 0 and 'question' not in data:
            raise DAError("This block is missing a 'question' directive." + self.idebug(data))
        if self.interview.debug:
            for key in data:
                if key not in ('features', 'scan for variables', 'only sets', 'question', 'code', 'event', 'translations', 'default language', 'on change', 'sections', 'progressive', 'auto open', 'section', 'machine learning storage', 'language', 'prevent going back', 'back button', 'usedefs', 'continue button label', 'resume button label', 'back button label', 'corner back button label', 'skip undefined', 'list collect', 'mandatory', 'attachment options', 'script', 'css', 'initial', 'default role', 'command', 'objects from file', 'use objects', 'data', 'variable name', 'data from code', 'objects', 'id', 'ga id', 'segment id', 'segment', 'supersedes', 'order', 'image sets', 'images', 'def', 'mako', 'interview help', 'default screen parts', 'default validation messages', 'generic object', 'generic list object', 'comment', 'metadata', 'modules', 'reset', 'imports', 'terms', 'auto terms', 'role', 'include', 'action buttons', 'if', 'validation code', 'require', 'orelse', 'attachment', 'attachments', 'attachment code', 'attachments code', 'allow emailing', 'allow downloading', 'email subject', 'email body', 'email address default', 'progress', 'zip filename', 'action', 'backgroundresponse', 'response', 'binaryresponse', 'all_variables', 'response filename', 'content type', 'redirect url', 'null response', 'sleep', 'include_internal', 'css class', 'table css class', 'response code', 'subquestion', 'reload', 'help', 'audio', 'video', 'decoration', 'signature', 'under', 'pre', 'post', 'right', 'check in', 'yesno', 'noyes', 'yesnomaybe', 'noyesmaybe', 'sets', 'event', 'choices', 'buttons', 'dropdown', 'combobox', 'field', 'shuffle', 'review', 'need', 'depends on', 'target', 'table', 'rows', 'columns', 'require gathered', 'allow reordering', 'edit', 'delete buttons', 'confirm', 'read only', 'edit header', 'confirm', 'show if empty', 'template', 'content file', 'content', 'subject', 'reconsider', 'undefine', 'continue button field', 'fields', 'indent', 'url', 'default', 'datatype', 'extras', 'allowed to set', 'show incomplete', 'not available label', 'required', 'always include editable files', 'question metadata', 'include attachment notice', 'include download tab', 'manual attachment list'):
                    logmessage("Ignoring unknown dictionary key '" + key + "'." + self.idebug(data))
        if 'features' in data:
            should_append = False
            if not isinstance(data['features'], dict):
                raise DAError("A features section must be a dictionary." + self.idebug(data))
            if data['features'].get('use catchall', False):
                self.interview.options['use catchall'] = True
            if 'table width' in data['features']:
                if not isinstance(data['features']['table width'], int):
                    raise DAError("Table width in features must be an integer." + self.idebug(data))
                self.interview.table_width = data['features']['table width']
            if 'progress bar' in data['features']:
                self.interview.use_progress_bar = True if data['features']['progress bar'] else False
            if 'progress can go backwards' in data['features'] and data['features']['progress can go backwards']:
                self.interview.options['strict progress'] = True
            if 'show progress bar percentage' in data['features'] and data['features']['show progress bar percentage']:
                self.interview.show_progress_bar_percentage = True
            if 'progress bar method' in data['features'] and isinstance(data['features']['progress bar method'], str):
                self.interview.progress_bar_method = data['features']['progress bar method']
            if 'progress bar multiplier' in data['features'] and isinstance(data['features']['progress bar multiplier'], (int, float)):
                if data['features']['progress bar multiplier'] <= 0.0 or data['features']['progress bar multiplier'] >= 1.0:
                    raise DAError("progress bar multiplier in features must be between 0 and 1." + self.idebug(data))
                self.interview.progress_bar_method = data['features']['progress bar multiplier']
            if 'question back button' in data['features']:
                self.interview.question_back_button = True if data['features']['question back button'] else False
            if 'question help button' in data['features']:
                self.interview.question_help_button = True if data['features']['question help button'] else False
            if 'navigation back button' in data['features']:
                self.interview.navigation_back_button = True if data['features']['navigation back button'] else False
            if 'go full screen' in data['features'] and data['features']['go full screen']:
                self.interview.force_fullscreen = data['features']['go full screen']
            if 'navigation' in data['features'] and data['features']['navigation']:
                self.interview.use_navigation = data['features']['navigation']
            if 'small screen navigation' in data['features']:
                if data['features']['small screen navigation'] == 'dropdown':
                    self.interview.use_navigation_on_small_screens = 'dropdown'
                else:
                    if not data['features']['small screen navigation']:
                        self.interview.use_navigation_on_small_screens = False
            if 'centered' in data['features'] and not data['features']['centered']:
                self.interview.flush_left = True
            if 'maximum image size' in data['features']:
                self.interview.max_image_size = eval(str(data['features']['maximum image size']))
            if 'image upload type' in data['features']:
                self.interview.image_type = str(data['features']['image upload type'])
            if 'debug' in data['features'] and isinstance(data['features']['debug'], bool):
                self.interview.debug = data['features']['debug']
            if 'cache documents' in data['features']:
                self.interview.cache_documents = data['features']['cache documents']
            if 'loop limit' in data['features']:
                self.interview.loop_limit = data['features']['loop limit']
            if 'recursion limit' in data['features']:
                self.interview.recursion_limit = data['features']['recursion limit']
            if 'pdf/a' in data['features'] and data['features']['pdf/a'] in (True, False):
                self.interview.use_pdf_a = data['features']['pdf/a']
            if 'tagged pdf' in data['features'] and data['features']['tagged pdf'] in (True, False):
                self.interview.use_tagged_pdf = data['features']['tagged pdf']
            if 'bootstrap theme' in data['features'] and data['features']['bootstrap theme']:
                self.interview.bootstrap_theme = data['features']['bootstrap theme']
            if 'inverse navbar' in data['features']:
                self.interview.options['inverse navbar'] = data['features']['inverse navbar']
            if 'popover trigger' in data['features']:
                self.interview.options['popover trigger'] = data['features']['popover trigger']
            if 'review button color' in data['features']:
                self.interview.options['review button color'] = data['features']['review button color']
            if 'review button icon' in data['features']:
                self.interview.options['review button icon'] = data['features']['review button icon']
            if 'disable analytics' in data['features'] and data['features']['disable analytics']:
                self.interview.options['analyics on'] = data['features']['disable analytics']
            if 'hide navbar' in data['features']:
                self.interview.options['hide navbar'] = data['features']['hide navbar']
            if 'hide standard menu' in data['features']:
                self.interview.options['hide standard menu'] = data['features']['hide standard menu']
            if 'labels above fields' in data['features']:
                self.interview.options['labels above'] = True if data['features']['labels above fields'] else False
            if 'send question data' in data['features']:
                self.interview.options['send question data'] = True if data['features']['send question data'] else False
            if 'checkin interval' in data['features']:
                if not isinstance(data['features']['checkin interval'], int):
                    raise DAError("A features section checkin interval entry must be an integer." + self.idebug(data))
                if data['features']['checkin interval'] > 0 and data['features']['checkin interval'] < 1000:
                    raise DAError("A features section checkin interval entry must be at least 1000, if not 0." + self.idebug(data))
                self.interview.options['checkin interval'] = data['features']['checkin interval']
            for key in ('javascript', 'css'):
                if key in data['features']:
                    if isinstance(data['features'][key], list):
                        the_list = data['features'][key]
                    elif isinstance(data['features'][key], dict):
                        raise DAError("A features section " + key + " entry must be a list or plain text." + self.idebug(data))
                    else:
                        the_list = [data['features'][key]]
                    for the_file in the_list:
                        if key not in self.interview.external_files:
                            self.interview.external_files[key] = list()
                        self.interview.external_files[key].append((self.from_source.get_package(), the_file))
            for key in ('default date min', 'default date max'):
                if key in data['features']:
                    if not isinstance(data['features'][key], str):
                        raise DAError("A features section " + key + " entry must be plain text." + self.idebug(data))
                    try:
                        self.interview.options[key] = pytz.timezone(docassemble.base.functions.get_default_timezone()).localize(dateutil.parser.parse(data['features'][key]))
                    except:
                        raise DAError("The " + key + " in features did not contain a valid date." + self.idebug(data))
        if 'field' in data and not ('yesno' in data or 'noyes' in data or 'yesnomaybe' in data or 'noyesmaybe' in data or 'buttons' in data or 'choices' in data or 'dropdown' in data or 'combobox' in data):
            data['continue button field'] = data['field']
            del data['field']
        if 'scan for variables' in data:
            if data['scan for variables']:
                self.scan_for_variables = True
            else:
                self.scan_for_variables = False
        if 'only sets' in data:
            if isinstance(data['only sets'], str):
                self.fields_used.add(data['only sets'])
            elif isinstance(data['only sets'], list):
                for key in data['only sets']:
                    self.fields_used.add(key)
            else:
                raise DAError("An only sets phrase must be text or a list." + self.idebug(data))
            self.scan_for_variables = False
        if 'question' in data and 'code' in data:
            raise DAError("A block can be a question block or a code block but cannot be both at the same time." + self.idebug(data))
        if 'event' in data:
            if 'field' in data or 'fields' in data or 'yesno' in data or 'noyes' in data:
                raise DAError("The 'event' designator is for special screens that do not gather information and can only be used with 'buttons' or with no other controls." + self.idebug(data))
        if 'translations' in data:
            should_append = False
            if not isinstance(data['translations'], list):
                raise DAError("A 'translations' block must be a list" + self.idebug(data))
            tr_todo = list()
            for item in data['translations']:
                if not isinstance(item, str):
                    raise DAError("A 'translations' block must be a list of text items" + self.idebug(data))
                if not (item.endswith('.xlsx') or item.endswith('.xlf') or item.endswith('.xliff')):
                    raise DAError("Invalid translations entry '" + item + "'.  A translations entry must refer to a file ending in .xlsx, .xlf, or .xliff." + self.idebug(data))
                parts = item.split(":")
                if len(parts) == 1:
                    item = re.sub(r'^data/sources/', '', item)
                    the_package = self.from_source.get_package()
                    if the_package is not None:
                        item = self.from_source.get_package() + ':data/sources/' + item
                    tr_todo.append(item)
                elif len(parts) == 2 and parts[0].startswith('docassemble.') and parts[1].startswith('data/sources/'):
                    tr_todo.append(item)
                else:
                    raise DAError("Invalid translations entry: " + item + ".  A translations entry must refer to a data sources file" + self.idebug(data))
            for item in tr_todo:
                self.interview.translations.append(item)
                if item.endswith(".xlsx"):
                    the_xlsx_file = docassemble.base.functions.package_data_filename(item)
                    if not os.path.isfile(the_xlsx_file):
                        raise DAError("The translations file " + the_xlsx_file + " could not be found")
                    df = pandas.read_excel(the_xlsx_file)
                    for column_name in ('interview', 'question_id', 'index_num', 'hash', 'orig_lang', 'tr_lang', 'orig_text', 'tr_text'):
                        if column_name not in df.columns:
                            raise DAError("Invalid translations file " + os.path.basename(the_xlsx_file) + ": column " + column_name + " is missing")
                    for indexno in df.index:
                        if not isinstance(df['tr_text'][indexno], str) or df['tr_text'][indexno] == '':
                            continue
                        if df['orig_text'][indexno] not in self.interview.translation_dict:
                            self.interview.translation_dict[df['orig_text'][indexno]] = dict()
                        if df['orig_lang'][indexno] not in self.interview.translation_dict[df['orig_text'][indexno]]:
                            self.interview.translation_dict[df['orig_text'][indexno]][df['orig_lang'][indexno]] = dict()
                        self.interview.translation_dict[df['orig_text'][indexno]][df['orig_lang'][indexno]][df['tr_lang'][indexno]] = df['tr_text'][indexno]
                elif item.endswith(".xlf") or item.endswith(".xliff"):
                    the_xlf_file = docassemble.base.functions.package_data_filename(item)
                    if not os.path.isfile(the_xlf_file):
                        continue
                    tree = ET.parse(the_xlf_file)
                    root = tree.getroot()
                    indexno = 1
                    if root.attrib['version'] == "1.2":
                        for the_file in root.iter('{urn:oasis:names:tc:xliff:document:1.2}file'):
                            source_lang = the_file.attrib.get('source-language', 'en')
                            target_lang = the_file.attrib.get('target-language', 'en')
                            for transunit in the_file.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
                                orig_text = ''
                                tr_text = ''
                                for source in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}source'):
                                    if source.text:
                                        orig_text += source.text
                                    for mrk in source:
                                        orig_text += mrk.text
                                        if mrk.tail:
                                            orig_text += mrk.tail
                                for target in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}target'):
                                    if target.text:
                                        tr_text += target.text
                                    for mrk in target:
                                        tr_text += mrk.text
                                        if mrk.tail:
                                            tr_text += mrk.tail
                                if orig_text == '' or tr_text == '':
                                    continue
                                if orig_text not in self.interview.translation_dict:
                                    self.interview.translation_dict[orig_text] = dict()
                                if source_lang not in self.interview.translation_dict[orig_text]:
                                    self.interview.translation_dict[orig_text][source_lang] = dict()
                                self.interview.translation_dict[orig_text][source_lang][target_lang] = tr_text
                    elif root.attrib['version'] == "2.0":
                        source_lang = root.attrib.get('srcLang', 'en')
                        target_lang = root.attrib.get('trgLang', 'en')
                        for segment in root.iter('{urn:oasis:names:tc:xliff:document:2.0}segment'):
                            orig_text = ''
                            tr_text = ''
                            for source in segment.iter('{urn:oasis:names:tc:xliff:document:2.0}source'):
                                if source.text:
                                    orig_text += source.text
                                for mrk in source:
                                    orig_text += mrk.text
                                    if mrk.tail:
                                        orig_text += mrk.tail
                            for target in segment.iter('{urn:oasis:names:tc:xliff:document:2.0}target'):
                                if target.text:
                                    tr_text += target.text
                                for mrk in target:
                                    tr_text += mrk.text
                                    if mrk.tail:
                                        tr_text += mrk.tail
                            if orig_text == '' or tr_text == '':
                                continue
                            if orig_text not in self.interview.translation_dict:
                                self.interview.translation_dict[orig_text] = dict()
                            if source_lang not in self.interview.translation_dict[orig_text]:
                                self.interview.translation_dict[orig_text][source_lang] = dict()
                            self.interview.translation_dict[orig_text][source_lang][target_lang] = tr_text
        if 'default language' in data:
            should_append = False
            self.from_source.set_language(data['default language'])
        if 'on change' in data:
            should_append = False
            self.scan_for_variables = False
            if not isinstance(data['on change'], dict):
                raise DAError("An on change block must be a dictionary." + self.idebug(data))
            if len(data) > 1:
                raise DAError("An on change block must not contain any other keys." + self.idebug(data))
            for key, val in data['on change'].items():
                if not (isinstance(key, str) and isinstance(val, str)):
                    raise DAError("An on change block must be a dictionary where the keys are field names and the values are Python code." + self.idebug(data))
                if key not in self.interview.onchange:
                    self.interview.onchange[key] = list()
                self.interview.onchange[key].append(compile(val, '<on change code>', 'exec'))
                self.find_fields_in(val)
        if 'sections' in data:
            should_append = False
            if not isinstance(data['sections'], list):
                raise DAError("A sections list must be a list." + self.idebug(data))
            if 'language' in data:
                the_language = data['language']
            else:
                the_language = '*'
            self.interview.sections[the_language] = data['sections']
        if 'progressive' in data:
            if 'sections' not in data:
                raise DAError("A progressive directive can only be used with sections." + self.idebug(data))
            if not isinstance(data['progressive'], bool):
                raise DAError("A progressive directive can only be true or false." + self.idebug(data))
            self.interview.sections_progressive = data['progressive']
        if 'auto open' in data:
            if 'sections' not in data:
                raise DAError("An auto open directive can only be used with sections." + self.idebug(data))
            if not isinstance(data['auto open'], bool):
                raise DAError("An auto open directive can only be true or false." + self.idebug(data))
            self.interview.sections_auto_open = data['auto open']
        if 'section' in data:
            if 'question' not in data:
                raise DAError("You can only set the section from a question." + self.idebug(data))
            self.section = data['section']
        if 'machine learning storage' in data:
            should_append = False
            new_storage = data['machine learning storage']
            if not new_storage.endswith('.json'):
                raise DAError("Invalid machine learning storage entry '" + str(data['machine learning storage']) + ".'  A machine learning storage entry must refer to a file ending in .json." + self.idebug(data))
            parts = new_storage.split(":")
            if len(parts) == 1:
                new_storage = re.sub(r'^data/sources/', '', new_storage)
                the_package = self.from_source.get_package()
                if the_package is not None:
                    new_storage = self.from_source.get_package() + ':data/sources/' + new_storage
                self.interview.set_ml_store(new_storage)
            elif len(parts) == 2 and parts[0].startswith('docassemble.') and parts[1].startswith('data/sources/'):
                self.interview.set_ml_store(data['machine learning storage'])
            else:
                raise DAError("Invalid machine learning storage entry: " + str(data['machine learning storage']) + self.idebug(data))
        if 'language' in data:
            self.language = data['language']
        else:
            self.language = self.from_source.get_language()
        if 'prevent going back' in data and data['prevent going back']:
            self.can_go_back = False
        if 'back button' in data:
            if isinstance(data['back button'], (bool, NoneType)):
                self.back_button = data['back button']
            else:
                self.back_button = compile(data['back button'], '<back button>', 'eval')
        else:
            self.back_button = None
        if 'allowed to set' in data:
            if isinstance(data['allowed to set'], list):
                for item in data['allowed to set']:
                    if not isinstance(item, str):
                        raise DAError("When allowed to set is a list, it must be a list of text items." + self.idebug(data))
                self.allowed_to_set = data['allowed to set']
            elif isinstance(data['allowed to set'], str):
                self.allowed_to_set = compile(data['allowed to set'], '<allowed to set>', 'eval')
                self.find_fields_in(data['allowed to set'])
            else:
                raise DAError("When allowed to set is not a list, it must be plain text." + self.idebug(data))
        if 'usedefs' in data:
            defs = list()
            if isinstance(data['usedefs'], list):
                usedefs = data['usedefs']
            else:
                usedefs = [data['usedefs']]
            for usedef in usedefs:
                if isinstance(usedef, (dict, list, set, bool)):
                    raise DAError("A usedefs section must consist of a list of strings or a single string." + self.idebug(data))
                if usedef not in self.interview.defs:
                    raise DAError('Referred to a non-existent def "' + usedef + '."  All defs must be defined before they are used.' + self.idebug(data))
                defs.extend(self.interview.defs[usedef])
            definitions = "\n".join(defs) + "\n";
        else:
            definitions = "";
        if 'continue button label' in data:
            if 'yesno' in data or 'noyes' in data or 'yesnomaybe' in data or 'noyesmaybe' in data or 'buttons' in data:
                raise DAError("You cannot set a continue button label if the type of question is yesno, noyes, yesnomaybe, noyesmaybe, or buttons." + self.idebug(data))
            self.continuelabel = TextObject(definitions + str(data['continue button label']), question=self)
        if 'resume button label' in data:
            if 'review' not in data:
                raise DAError("You cannot set a resume button label if the type of question is not review." + self.idebug(data))
            self.continuelabel = TextObject(definitions + str(data['resume button label']), question=self)
        if 'back button label' in data:
            self.backbuttonlabel = TextObject(definitions + str(data['back button label']), question=self)
        if 'corner back button label' in data:
            self.cornerbackbuttonlabel = TextObject(definitions + str(data['corner back button label']), question=self)
        if 'skip undefined' in data:
            if 'review' not in data:
                raise DAError("You cannot set the skip undefined directive if the type of question is not review." + self.idebug(data))
            if not data['skip undefined']:
                self.skip_undefined = False
        if 'list collect' in data:
            if 'fields' not in data:
                raise DAError("You cannot set list collect without a fields specifier." + self.idebug(data))
            if isinstance(data['list collect'], (str, bool)):
                self.list_collect = compile(str(data['list collect']), '<list collect code>', 'eval')
            elif isinstance(data['list collect'], dict):
                if 'enable' in data['list collect']:
                    self.list_collect = compile(str(data['list collect']['enable']), '<list collect code>', 'eval')
                else:
                    self.list_collect = compile('True', '<list collect code>', 'eval')
                if 'label' in data['list collect']:
                    self.list_collect_label = TextObject(definitions + str(data['list collect']['label']), question=self)
                if 'is final' in data['list collect']:
                    self.list_collect_is_final = compile(str(data['list collect']['is final']), '<list collect final code>', 'eval')
                if 'allow append' in data['list collect']:
                    self.list_collect_allow_append = compile(str(data['list collect']['allow append']), '<list collect allow append code>', 'eval')
                if 'allow delete' in data['list collect']:
                    self.list_collect_allow_delete = compile(str(data['list collect']['allow delete']), '<list collect allow delete code>', 'eval')
                if 'add another label' in data['list collect']:
                    self.list_collect_add_another_label = TextObject(definitions + str(data['list collect']['add another label']), question=self)
            else:
                raise DAError("Invalid data under list collect." + self.idebug(data))
        if 'mandatory' in data:
            if 'initial' in data:
                raise DAError("You cannot use the mandatory modifier and the initial modifier at the same time." + self.idebug(data))
            if 'id' not in data and self.interview.debug and self.interview.source.package.startswith('docassemble.playground'):
                self.interview.issue['mandatory_id'] = True
            if 'question' not in data and 'code' not in data and 'objects' not in data and 'attachment' not in data and 'data' not in data and 'data from code' not in data:
                raise DAError("You cannot use the mandatory modifier on this type of block." + self.idebug(data))
            if data['mandatory'] is True:
                self.is_mandatory = True
                self.mandatory_code = None
            elif data['mandatory'] in (False, None):
                self.is_mandatory = False
                self.mandatory_code = None
            else:
                self.is_mandatory = False
                if isinstance(data['mandatory'], str):
                    self.mandatory_code = compile(data['mandatory'], '<mandatory code>', 'eval')
                    self.find_fields_in(data['mandatory'])
                else:
                    self.mandatory_code = None
        else:
            self.is_mandatory = False
            self.mandatory_code = None
        if 'attachment options' in data:
            should_append = False
            if not isinstance(data['attachment options'], list):
                data['attachment options'] = [data['attachment options']]
            for attachment_option in data['attachment options']:
                if not isinstance(attachment_option, dict):
                    raise DAError("An attachment option must a dictionary." + self.idebug(data))
                for key in attachment_option:
                    value = attachment_option[key]
                    if key == 'initial yaml':
                        if 'initial_yaml' not in self.interview.attachment_options:
                            self.interview.attachment_options['initial_yaml'] = list()
                        if isinstance(value, list):
                            the_list = value
                        else:
                            the_list = [value]
                        for yaml_file in the_list:
                            if not isinstance(yaml_file, str):
                                raise DAError('An initial yaml file must be a string.' + self.idebug(data))
                            self.interview.attachment_options['initial_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
                    elif key == 'additional yaml':
                        if 'additional_yaml' not in self.interview.attachment_options:
                            self.interview.attachment_options['additional_yaml'] = list()
                        if isinstance(value, list):
                            the_list = value
                        else:
                            the_list = [value]
                        for yaml_file in the_list:
                            if not isinstance(yaml_file, str):
                                raise DAError('An additional yaml file must be a string.' + self.idebug(data))
                            self.interview.attachment_options['additional_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
                    elif key == 'template file':
                        if not isinstance(value, str):
                            raise DAError('The template file must be a string.' + self.idebug(data))
                        self.interview.attachment_options['template_file'] = FileInPackage(value, 'template', self.package)
                    elif key == 'rtf template file':
                        if not isinstance(value, str):
                            raise DAError('The rtf template file must be a string.' + self.idebug(data))
                        self.interview.attachment_options['rtf_template_file'] = FileInPackage(value, 'template', self.package)
                    elif key == 'docx reference file':
                        if not isinstance(value, str):
                            raise DAError('The docx reference file must be a string.' + self.idebug(data))
                        self.interview.attachment_options['docx_reference_file'] = FileInPackage(value, 'template', self.package)
        if 'script' in data:
            if not isinstance(data['script'], str):
                raise DAError("A script section must be plain text." + self.idebug(data))
            self.script = TextObject(definitions + do_not_translate + str(data['script']), question=self)
        if 'css' in data:
            if not isinstance(data['css'], str):
                raise DAError("A css section must be plain text." + self.idebug(data))
            self.css = TextObject(definitions + do_not_translate + str(data['css']), question=self)
        if 'initial' in data and 'code' not in data:
            raise DAError("Only a code block can be marked as initial." + self.idebug(data))
        if 'initial' in data or 'default role' in data:
            if 'default role' in data or data['initial'] is True:
                self.is_initial = True
                self.initial_code = None
            elif data['initial'] in (False, None):
                self.is_initial = False
                self.initial_code = None
            else:
                self.is_initial = False
                if isinstance(data['initial'], str):
                    self.initial_code = compile(data['initial'], '<initial code>', 'eval')
                    self.find_fields_in(data['initial'])
                else:
                    self.initial_code = None
        else:
            self.is_initial = False
            self.initial_code = None
        if 'command' in data and data['command'] in ('exit', 'logout', 'exit_logout', 'continue', 'restart', 'leave', 'refresh', 'signin', 'register', 'new_session'):
            self.question_type = data['command']
            self.content = TextObject(data.get('url', ''), question=self)
            return
        if 'objects from file' in data:
            if not isinstance(data['objects from file'], list):
                data['objects from file'] = [data['objects from file']]
            if 'use objects' in data and data['use objects']:
                self.question_type = 'objects_from_file_da'
            else:
                self.question_type = 'objects_from_file'
            self.objects_from_file = data['objects from file']
            for item in data['objects from file']:
                if isinstance(item, dict):
                    for key in item:
                        self.fields.append(Field({'saveas': key, 'type': 'object_from_file', 'file': item[key]}))
                        if self.scan_for_variables:
                            self.fields_used.add(key)
                        else:
                            self.other_fields_used.add(key)
                else:
                    raise DAError("An objects section cannot contain a nested list." + self.idebug(data))
        if 'data' in data and 'variable name' in data:
            if not isinstance(data['variable name'], str):
                raise DAError("A data block variable name must be plain text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['variable name'].strip())
            else:
                self.other_fields_used.add(data['variable name'].strip())
            if 'use objects' in data and data['use objects']:
                self.question_type = 'data_da'
            else:
                self.question_type = 'data'
            self.fields.append(Field({'saveas': data['variable name'].strip(), 'type': 'data', 'data': self.recursive_dataobject(data['data'])}))
        if 'data from code' in data and 'variable name' in data:
            if not isinstance(data['variable name'], str):
                raise DAError("A data from code block variable name must be plain text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['variable name'])
            else:
                self.other_fields_used.add(data['variable name'])
            if 'use objects' in data and data['use objects']:
                self.question_type = 'data_from_code_da'
            else:
                self.question_type = 'data_from_code'
            self.fields.append(Field({'saveas': data['variable name'], 'type': 'data_from_code', 'data': self.recursive_data_from_code(data['data from code'])}))
        if 'objects' in data:
            if not isinstance(data['objects'], list):
                data['objects'] = [data['objects']]
                #raise DAError("An objects section must be organized as a list." + self.idebug(data))
            self.question_type = 'objects'
            self.objects = data['objects']
            for item in data['objects']:
                if isinstance(item, dict):
                    for key in item:
                        self.fields.append(Field({'saveas': key, 'type': 'object', 'objecttype': item[key]}))
                        if self.scan_for_variables:
                            self.fields_used.add(key)
                        else:
                            self.other_fields_used.add(key)
                else:
                    raise DAError("An objects section cannot contain a nested list." + self.idebug(data))
        if 'id' in data:
            # if str(data['id']) in self.interview.ids_in_use:
            #     raise DAError("The id " + str(data['id']) + " is already in use by another block.  Id names must be unique." + self.idebug(data))
            self.id = str(data['id']).strip()
            if self.interview.debug and self.interview.source.package.startswith('docassemble.playground') and self.id in self.interview.ids_in_use:
                self.interview.issue['id_collision'] = self.id
            self.interview.ids_in_use.add(self.id)
            self.interview.questions_by_id[self.id] = self
        if 'ga id' in data:
            if not isinstance(data['ga id'], str):
                raise DAError("A 'ga id' must refer to text." + self.idebug(data))
            self.ga_id = TextObject(definitions + str(data['ga id']), question=self)
        if 'segment id' in data:
            if not isinstance(data['segment id'], str):
                raise DAError("A 'segment id' must refer to text." + self.idebug(data))
            if not hasattr(self, 'segment'):
                self.segment = dict(arguments=dict())
            self.segment['id'] = TextObject(definitions + str(data['segment id']), question=self)
        if 'segment' in data:
            if not isinstance(data['segment'], dict):
                raise DAError("A 'segment' must refer to a dictionary." + self.idebug(data))
            if 'id' in data['segment']:
                if not isinstance(data['segment']['id'], str):
                    raise DAError("An 'id' under 'segment' must refer to text." + self.idebug(data))
                if not hasattr(self, 'segment'):
                    self.segment = dict(arguments=dict())
                self.segment['id'] = TextObject(definitions + str(data['segment']['id']), question=self)
            if 'arguments' in data['segment']:
                if not isinstance(data['segment']['arguments'], dict):
                    raise DAError("An 'arguments' under 'segment' must refer to a dictionary." + self.idebug(data))
                if not hasattr(self, 'segment'):
                    self.segment = dict(arguments=dict())
                for key, val in data['segment']['arguments'].items():
                    if not isinstance(val, (str, int, float, bool)):
                        raise DAError("Each item under 'arguments' in a 'segment' must be plain text." + self.idebug(data))
                    self.segment['arguments'][key] = TextObject(definitions + str(val), question=self)
        if 'supersedes' in data:
            if not isinstance(data['supersedes'], list):
                supersedes_list = [str(data['supersedes'])]
            else:
                supersedes_list = [str(x) for x in data['supersedes']]
            self.interview.id_orderings.append(dict(type="supersedes", question=self, supersedes=supersedes_list))
        if 'order' in data:
            should_append = False
            if 'question' in data or 'code' in data or 'attachment' in data or 'attachments' in data or 'template' in data:
                raise DAError("An 'order' block cannot be combined with another type of block." + self.idebug(data))
            if not isinstance(data['order'], list):
                raise DAError("An 'order' block must be a list." + self.idebug(data))
            self.interview.id_orderings.append(dict(type="order", order=[str(x) for x in data['order']]))
        for key in ('image sets', 'images'):
            if key not in data:
                continue
            should_append = False
            if not isinstance(data[key], dict):
                raise DAError("The '" + key + "' section needs to be a dictionary, not a list or text." + self.idebug(data))
            if key == 'images':
                data[key] = {'unspecified': {'images': data[key]}}
            elif 'images' in data[key] and 'attribution' in data[key]:
                data[key] = {'unspecified': data[key]}
            for setname, image_set in data[key].items():
                if not isinstance(image_set, dict):
                    if key == 'image sets':
                        raise DAError("Each item in the 'image sets' section needs to be a dictionary, not a list.  Each dictionary item should have an 'images' definition (which can be a dictionary or list) and an optional 'attribution' definition (which must be text)." + self.idebug(data))
                    else:
                        raise DAError("Each item in the 'images' section needs to be a dictionary, not a list." + self.idebug(data))
                if 'attribution' in image_set:
                    if not isinstance(image_set['attribution'], str):
                        raise DAError("An attribution in an 'image set' section cannot be a dictionary or a list." + self.idebug(data))
                    attribution = re.sub(r'\n', ' ', image_set['attribution'].strip())
                else:
                    attribution = None
                if 'images' in image_set:
                    if isinstance(image_set['images'], list):
                        image_list = image_set['images']
                    elif isinstance(image_set['images'], dict):
                        image_list = [image_set['images']]
                    else:
                        if key == 'image set':
                            raise DAError("An 'images' definition in an 'image set' item must be a dictionary or a list." + self.idebug(data))
                        else:
                            raise DAError("An 'images' section must be a dictionary or a list." + self.idebug(data))
                    for image in image_list:
                        if not isinstance(image, dict):
                            the_image = {str(image): str(image)}
                        else:
                            the_image = image
                        for key, value in the_image.items():
                            self.interview.images[key] = PackageImage(filename=value, attribution=attribution, setname=setname, package=self.package)
        if 'def' in data:
            should_append = False
            if not isinstance(data['def'], str):
                raise DAError("A def name must be a string." + self.idebug(data))
            if data['def'] not in self.interview.defs:
                self.interview.defs[data['def']] = list()
            if 'mako' in data:
                if isinstance(data['mako'], str):
                    list_of_defs = [data['mako']]
                elif isinstance(data['mako'], list):
                    list_of_defs = data['mako']
                else:
                    raise DAError("A mako template definition must be a string or a list of strings." + self.idebug(data))
                for definition in list_of_defs:
                    if not isinstance(definition, str):
                        raise DAError("A mako template definition must be a string." + self.idebug(data))
                    self.interview.defs[data['def']].append(definition)
        if 'interview help' in data:
            should_append = False
            if isinstance(data['interview help'], list):
                raise DAError("An interview help section must not be in the form of a list." + self.idebug(data))
            elif not isinstance(data['interview help'], dict):
                data['interview help'] = {'content': str(data['interview help'])}
            audiovideo = list()
            if 'label' in data['interview help']:
                data['interview help']['label'] = str(data['interview help']['label'])
            if 'audio' in data['interview help']:
                if not isinstance(data['interview help']['audio'], list):
                    the_list = [data['interview help']['audio']]
                else:
                    the_list = data['interview help']['audio']
                audiovideo = list()
                for the_item in the_list:
                    if isinstance(the_item, (list, dict)):
                        raise DAError("An interview help audio section must be in the form of a text item or a list of text items." + self.idebug(data))
                    audiovideo.append({'text': TextObject(definitions + str(data['interview help']['audio']), question=self), 'package': self.package, 'type': 'audio'})
            if 'video' in data['interview help']:
                if not isinstance(data['interview help']['video'], list):
                    the_list = [data['interview help']['video']]
                else:
                    the_list = data['interview help']['video']
                for the_item in the_list:
                    if isinstance(the_item, (list, dict)):
                        raise DAError("An interview help video section must be in the form of a text item or a list of text items." + self.idebug(data))
                    audiovideo.append({'text': TextObject(definitions + str(data['interview help']['video']), question=self), 'package': self.package, 'type': 'video'})
            if 'video' not in data['interview help'] and 'audio' not in data['interview help']:
                audiovideo = None
            if 'heading' in data['interview help']:
                if not isinstance(data['interview help']['heading'], (dict, list)):
                    help_heading = TextObject(definitions + str(data['interview help']['heading']), question=self)
                else:
                    raise DAError("A heading within an interview help section must be text, not a list or a dictionary." + self.idebug(data))
            else:
                help_heading = None
            if 'content' in data['interview help']:
                if not isinstance(data['interview help']['content'], (dict, list)):
                    help_content = TextObject(definitions + str(data['interview help']['content']), question=self)
                else:
                    raise DAError("Help content must be text, not a list or a dictionary." + self.idebug(data))
            else:
                raise DAError("No content section was found in an interview help section." + self.idebug(data))
            if 'label' in data['interview help']:
                if not isinstance(data['interview help']['label'], (dict, list)):
                    help_label = TextObject(definitions + str(data['interview help']['label']), question=self)
                else:
                    raise DAError("Help label must be text, not a list or a dictionary." + self.idebug(data))
            else:
                help_label = None
            if self.language not in self.interview.helptext:
                self.interview.helptext[self.language] = list()
            self.interview.helptext[self.language].append({'content': help_content, 'heading': help_heading, 'audiovideo': audiovideo, 'label': help_label, 'from': 'interview'})
        if 'default screen parts' in data:
            should_append = False
            if not isinstance(data['default screen parts'], dict):
                raise DAError("A default screen parts block must be in the form of a dictionary." + self.idebug(data))
            if self.language not in self.interview.default_screen_parts:
                self.interview.default_screen_parts[self.language] = dict()
            for key, content in data['default screen parts'].items():
                if content is None:
                    if key in self.interview.default_screen_parts[self.language]:
                        del self.interview.default_screen_parts[self.language][key]
                else:
                    if not (isinstance(key, str) and isinstance(content, str)):
                        raise DAError("A default screen parts block must be a dictionary of text keys and text values." + self.idebug(data))
                self.interview.default_screen_parts[self.language][key] = TextObject(definitions + str(content.strip()), question=self)
        if 'default validation messages' in data:
            should_append = False
            if not isinstance(data['default validation messages'], dict):
                raise DAError("A default validation messages block must be in the form of a dictionary." + self.idebug(data))
            if self.language not in self.interview.default_validation_messages:
                self.interview.default_validation_messages[self.language] = dict()
            for validation_key, validation_message in data['default validation messages'].items():
                if not (isinstance(validation_key, str) and isinstance(validation_message, str)):
                    raise DAError("A validation messages block must be a dictionary of text keys and text values." + self.idebug(data))
                self.interview.default_validation_messages[self.language][validation_key] = validation_message.strip()
        if 'generic object' in data:
            self.is_generic = True
            #self.is_generic_list = False
            self.generic_object = data['generic object']
        elif 'generic list object' in data:
            self.is_generic = True
            #self.is_generic_list = True
            self.generic_object = data['generic list object']
        else:
            self.is_generic = False
        if 'comment' in data and len(data) == 1:
            should_append = False
        if 'metadata' in data:
            for key in data:
                if key not in ('metadata', 'comment'):
                    raise DAError("A metadata directive cannot be mixed with other directives." + self.idebug(data))
            should_append = False
            if isinstance(data['metadata'], dict):
                data['metadata']['_origin_path'] = self.from_source.path
                data['metadata']['_origin_package'] = self.from_source.get_package()
                self.interview.metadata.append(data['metadata'])
            else:
                raise DAError("A metadata section must be organized as a dictionary." + self.idebug(data))
        if 'modules' in data:
            if isinstance(data['modules'], str):
                data['modules'] = [data['modules']]
            if isinstance(data['modules'], list):
                if 'docassemble.base.util' in data['modules'] or 'docassemble.base.legal' in data['modules']:
                    # logmessage("setting imports_util to true")
                    self.interview.imports_util = True
                # else:
                #     logmessage("not setting imports_util to true")
                self.question_type = 'modules'
                self.module_list = data['modules']
            else:
                raise DAError("A modules section must be organized as a list." + self.idebug(data))
        if 'reset' in data:
            #logmessage("Found a reset")
            if isinstance(data['reset'], str):
                data['reset'] = [data['reset']]
            if isinstance(data['reset'], list):
                self.question_type = 'reset'
                self.reset_list = data['reset']
            else:
                raise DAError("A reset section must be organized as a list." + self.idebug(data))
        if 'imports' in data:
            if isinstance(data['imports'], str):
                data['imports'] = [data['imports']]
            if isinstance(data['imports'], list):
                self.question_type = 'imports'
                self.module_list = data['imports']
            else:
                raise DAError("An imports section must be organized as a list." + self.idebug(data))
        if 'terms' in data and 'question' in data:
            if not isinstance(data['terms'], (dict, list)):
                raise DAError("Terms must be organized as a dictionary or a list." + self.idebug(data))

            if isinstance(data['terms'], dict):
                data['terms'] = [data['terms']]
            for termitem in data['terms']:
                if not isinstance(termitem, dict):
                    raise DAError("A terms section organized as a list must be a list of dictionary items." + self.idebug(data))
                if len(termitem) == 2 and 'phrases' in termitem and isinstance(termitem['phrases'], list) and 'definition' in termitem:
                    termitems = [(phrase, termitem['definition']) for phrase in termitem['phrases']]
                else:
                    termitems = termitem.items()
                for term, definition in termitems:
                    lower_term = re.sub(r'\s+', ' ', term.lower())
                    term_textobject = TextObject(str(lower_term), question=self)
                    alt_terms = dict()
                    re_dict = dict()
                    re_dict[self.language] = re.compile(r"{(?i)(%s)(\|[^\}]*)?}" % (re.sub(r'\s', '\\\s+', lower_term),), re.IGNORECASE | re.DOTALL)
                    for lang, tr_tuple in term_textobject.other_lang.items():
                        lower_other = re.sub(r'\s+', ' ', tr_tuple[0].lower())
                        re_dict[lang] = re.compile(r"{(?i)(%s)(\|[^\}]*)?}" % (re.sub(r'\s', '\\\s+', lower_other),), re.IGNORECASE | re.DOTALL)
                        alt_terms[lang] = tr_tuple[0]
                    self.terms[lower_term] = {'definition': TextObject(definitions + str(definition), question=self), 're': re_dict, 'alt_terms': alt_terms}
        if 'auto terms' in data and 'question' in data:
            if not isinstance(data['auto terms'], (dict, list)):
                raise DAError("Terms must be organized as a dictionary or a list." + self.idebug(data))
            if isinstance(data['auto terms'], dict):
                data['auto terms'] = [data['auto terms']]
            for termitem in data['auto terms']:
                if not isinstance(termitem, dict):
                    raise DAError("A terms section organized as a list must be a list of dictionary items." + self.idebug(data))
                if len(termitem) == 2 and 'phrases' in termitem and isinstance(termitem['phrases'], list) and 'definition' in termitem:
                    termitems = [(phrase, termitem['definition']) for phrase in termitem['phrases']]
                else:
                    termitems = termitem.items()
                for term, definition in termitems:
                    lower_term = re.sub(r'\s+', ' ', term.lower())
                    term_textobject = TextObject(str(lower_term), question=self)
                    alt_terms = dict()
                    re_dict = dict()
                    re_dict[self.language] = re.compile(r"{?(?i)\b(%s)\b}?" % (re.sub(r'\s', '\\\s+', lower_term),), re.IGNORECASE | re.DOTALL)
                    for lang, tr_tuple in term_textobject.other_lang.items():
                        lower_other = re.sub(r'\s+', ' ', tr_tuple[0].lower())
                        re_dict[lang] = re.compile(r"{?(?i)\b(%s)\b}?" % (re.sub(r'\s', '\\\s+', lower_other),), re.IGNORECASE | re.DOTALL)
                        alt_terms[lang] = tr_tuple[0]
                    self.autoterms[lower_term] = {'definition': TextObject(definitions + str(definition), question=self), 're': re_dict, 'alt_terms': alt_terms}
        if 'terms' in data and 'question' not in data:
            should_append = False
            if self.language not in self.interview.terms:
                self.interview.terms[self.language] = dict()
            if isinstance(data['terms'], list):
                for termitem in data['terms']:
                    if isinstance(termitem, dict):
                        if len(termitem) == 2 and 'phrases' in termitem and isinstance(termitem['phrases'], list) and 'definition' in termitem:
                            termitems = [(phrase, termitem['definition']) for phrase in termitem['phrases']]
                        else:
                            termitems = termitem.items()
                        for term, definition in termitems:
                            lower_term = re.sub(r'\s+', ' ', term.lower())
                            term_textobject = TextObject(str(lower_term), question=self)
                            definition_textobject = TextObject(str(definition), question=self)
                            self.interview.terms[self.language][lower_term] = {'definition': str(definition), 're': re.compile(r"{(?i)(%s)(\|[^\}]*)?}" % (re.sub(r'\s', '\\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}
                            for lang, tr_tuple in term_textobject.other_lang.items():
                                if lang not in self.interview.terms:
                                    self.interview.terms[lang] = dict()
                                if tr_tuple[0] not in self.interview.terms[lang]:
                                    if lang in definition_textobject.other_lang:
                                        lower_other = re.sub(r'\s+', ' ', tr_tuple[0].lower())
                                        self.interview.terms[lang][tr_tuple[0]] = {'definition': definition_textobject.other_lang[lang][0], 're': re.compile(r"{(?i)(%s)(\|[^\}]*)?}" % (re.sub(r'\s', '\\\s+', lower_other),), re.IGNORECASE | re.DOTALL)}
                    else:
                        raise DAError("A terms section organized as a list must be a list of dictionary items." + self.idebug(data))
            elif isinstance(data['terms'], dict):
                for term in data['terms']:
                    lower_term = re.sub(r'\s+', ' ', term.lower())
                    term_textobject = TextObject(str(lower_term), question=self)
                    definition_textobject = TextObject(str(data['terms'][term]), question=self)
                    self.interview.terms[self.language][lower_term] = {'definition': str(data['terms'][term]), 're': re.compile(r"{(?i)(%s)(\|[^\}]*)?}" % (re.sub(r'\s', '\\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}
                    for lang, tr_tuple in term_textobject.other_lang.items():
                        if lang not in self.interview.terms:
                            self.interview.terms[lang] = dict()
                        if tr_tuple[0] not in self.interview.terms[lang]:
                            if lang in definition_textobject.other_lang:
                                lower_other = re.sub(r'\s+', ' ', tr_tuple[0].lower())
                                self.interview.terms[lang][tr_tuple[0]] = {'definition': definition_textobject.other_lang[lang][0], 're': re.compile(r"{(?i)(%s)(\|[^\}]*)?}" % (re.sub(r'\s', '\\\s+', lower_other),), re.IGNORECASE | re.DOTALL)}
            else:
                raise DAError("A terms section must be organized as a dictionary or a list." + self.idebug(data))
        if 'auto terms' in data and 'question' not in data:
            should_append = False
            if self.language not in self.interview.autoterms:
                self.interview.autoterms[self.language] = dict()
            if isinstance(data['auto terms'], list):
                for termitem in data['auto terms']:
                    if isinstance(termitem, dict):
                        if len(termitem) == 2 and 'phrases' in termitem and isinstance(termitem['phrases'], list) and 'definition' in termitem:
                            termitems = [(phrase, termitem['definition']) for phrase in termitem['phrases']]
                        else:
                            termitems = termitem.items()
                        for term, definition in termitems:
                            lower_term = re.sub(r'\s+', ' ', term.lower())
                            term_textobject = TextObject(str(lower_term), question=self)
                            definition_textobject = TextObject(str(definition), question=self)
                            self.interview.autoterms[self.language][lower_term] = {'definition': str(definition), 're': re.compile(r"{?(?i)\b(%s)\b}?" % (re.sub(r'\s', '\\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}
                            for lang, tr_tuple in term_textobject.other_lang.items():
                                if lang not in self.interview.autoterms:
                                    self.interview.autoterms[lang] = dict()
                                if tr_tuple[0] not in self.interview.autoterms[lang]:
                                    if lang in definition_textobject.other_lang:
                                        lower_other = re.sub(r'\s+', ' ', tr_tuple[0].lower())
                                        self.interview.autoterms[lang][tr_tuple[0]] = {'definition': definition_textobject.other_lang[lang][0], 're': re.compile(r"{?(?i)\b(%s)\b}?" % (re.sub(r'\s', '\\\s+', lower_other),), re.IGNORECASE | re.DOTALL)}
                    else:
                        raise DAError("An auto terms section organized as a list must be a list of dictionary items." + self.idebug(data))
            elif isinstance(data['auto terms'], dict):
                for term in data['auto terms']:
                    lower_term = re.sub(r'\s+', ' ', term.lower())
                    term_textobject = TextObject(str(lower_term), question=self)
                    definition_textobject = TextObject(str(data['auto terms'][term]), question=self)
                    self.interview.autoterms[self.language][lower_term] = {'definition': str(data['auto terms'][term]), 're': re.compile(r"{?(?i)\b(%s)\b}?" % (re.sub(r'\s', '\\\s+', lower_term),), re.IGNORECASE | re.DOTALL)}
                    for lang, tr_tuple in term_textobject.other_lang.items():
                        if lang not in self.interview.autoterms:
                            self.interview.autoterms[lang] = dict()
                        if tr_tuple[0] not in self.interview.autoterms[lang]:
                            if lang in definition_textobject.other_lang:
                                lower_other = re.sub(r'\s+', ' ', tr_tuple[0].lower())
                                self.interview.autoterms[lang][tr_tuple[0]] = {'definition': definition_textobject.other_lang[lang][0], 're': re.compile(r"{?(?i)\b(%s)\b}?" % (re.sub(r'\s', '\\\s+', lower_other),), re.IGNORECASE | re.DOTALL)}
            else:
                raise DAError("An auto terms section must be organized as a dictionary or a list." + self.idebug(data))
        if 'default role' in data:
            if 'code' not in data:
                should_append = False
            if isinstance(data['default role'], str):
                self.interview.default_role = [data['default role']]
            elif isinstance(data['default role'], list):
                self.interview.default_role = data['default role']
            else:
                raise DAError("A default role must be a list or a string." + self.idebug(data))
        if 'role' in data:
            if isinstance(data['role'], str):
                if data['role'] not in self.role:
                    self.role.append(data['role'])
            elif isinstance(data['role'], list):
                for rolename in data['role']:
                    if data['role'] not in self.role:
                        self.role.append(rolename)
            else:
                raise DAError("The role of a question must be a string or a list." + self.idebug(data))
        else:
            self.role = list()
        if 'include' in data:
            should_append = False
            if isinstance(data['include'], str):
                data['include'] = [data['include']]
            if isinstance(data['include'], list):
                for questionPath in data['include']:
                    if ':' in questionPath:
                        self.interview.read_from(interview_source_from_string(questionPath))
                    else:
                        new_source = self.from_source.append(questionPath)
                        if new_source is None:
                            new_source = interview_source_from_string('docassemble.base:data/questions/' + re.sub(r'^data/questions/', '', questionPath))
                            if new_source is None:
                                raise DANotFoundError('Question file ' + questionPath + ' not found')
                        self.interview.read_from(new_source)
            else:
                raise DAError("An include section must be organized as a list." + self.idebug(data))
        if 'action buttons' in data:
            if isinstance(data['action buttons'], dict) and len(data['action buttons']) == 1 and 'code' in data['action buttons']:
                self.action_buttons.append(compile(data['action buttons']['code'], '<action buttons code>', 'eval'))
            else:
                if not isinstance(data['action buttons'], list):
                    raise DAError("An action buttons specifier must be a list." + self.idebug(data))
                for item in data['action buttons']:
                    if not isinstance(item, dict):
                        raise DAError("An action buttons item must be a dictionary." + self.idebug(data))
                    action = item.get('action', None)
                    target = item.get('new window', None)
                    if target is True:
                        target = '_blank'
                    elif target is False:
                        target = None
                    label = item.get('label', None)
                    color = item.get('color', 'primary')
                    icon = item.get('icon', None)
                    placement = item.get('placement', None)
                    forget_prior = item.get('forget prior', False)
                    given_arguments = item.get('arguments', dict())
                    if not isinstance(action, str):
                        raise DAError("An action buttons item must contain an action in plain text." + self.idebug(data))
                    if not isinstance(target, (str, NoneType)):
                        raise DAError("The new window specifier in an action buttons item must refer to True or plain text." + self.idebug(data))
                    if not isinstance(given_arguments, dict):
                        raise DAError("The arguments specifier in an action buttons item must refer to a dictionary." + self.idebug(data))
                    if not isinstance(label, str):
                        raise DAError("An action buttons item must contain a label in plain text." + self.idebug(data))
                    if not isinstance(color, str):
                        raise DAError("The color specifier in an action buttons item must refer to plain text." + self.idebug(data))
                    if not isinstance(icon, (str, NoneType)):
                        raise DAError("The icon specifier in an action buttons item must refer to plain text." + self.idebug(data))
                    if not isinstance(placement, (str, NoneType)):
                        raise DAError("The placement specifier in an action buttons item must refer to plain text." + self.idebug(data))
                    if not isinstance(forget_prior, bool):
                        raise DAError("The forget prior specifier in an action buttons item must refer to true or false." + self.idebug(data))
                    button = dict(action=TextObject(definitions + action, question=self), label=TextObject(definitions + label, question=self), color=TextObject(definitions + color, question=self))
                    if target is not None:
                        button['target'] = TextObject(definitions + target, question=self)
                    else:
                        button['target'] = None
                    if icon is not None:
                        button['icon'] = TextObject(definitions + icon, question=self)
                    else:
                        button['icon'] = None
                    if placement is not None:
                        button['placement'] = TextObject(definitions + placement, question=self)
                    else:
                        button['placement'] = None
                    if forget_prior:
                        button['forget_prior'] = True
                    else:
                        button['forget_prior'] = False
                    button['arguments'] = dict()
                    for key, val in given_arguments.items():
                        if isinstance(val, (list, dict)):
                            raise DAError("The arguments specifier in an action buttons item must refer to plain items." + self.idebug(data))
                        if isinstance(val, str):
                            button['arguments'][key] = TextObject(definitions + val, question=self)
                        else:
                            button['arguments'][key] = val
                    self.action_buttons.append(button)
        if 'if' in data:
            if isinstance(data['if'], str):
                self.condition = [compile(data['if'], '<if code>', 'eval')]
                self.find_fields_in(data['if'])
            elif isinstance(data['if'], list):
                self.condition = [compile(x, '<if code>', 'eval') for x in data['if']]
                for x in data['if']:
                    self.find_fields_in(x)
            else:
                raise DAError("An if statement must either be text or a list." + self.idebug(data))
        if 'validation code' in data:
            if not isinstance(data['validation code'], str):
                raise DAError("A validation code statement must be text." + self.idebug(data))
            self.validation_code = compile(data['validation code'], '<code block>', 'exec')
            self.find_fields_in(data['validation code'])
        if 'require' in data:
            if isinstance(data['require'], list):
                self.question_type = 'require'
                try:
                    self.require_list = list(map((lambda x: compile(x, '<require code>', 'eval')), data['require']))
                    for x in data['require']:
                        self.find_fields_in(x)
                except:
                    logmessage("Compile error in require:\n" + str(data['require']) + "\n" + str(sys.exc_info()[0]))
                    raise
                if 'orelse' in data:
                    if isinstance(data['orelse'], dict):
                        self.or_else_question = Question(data['orelse'], self.interview, register_target=register_target, source=self.from_source, package=self.package)
                    else:
                        raise DAError("The orelse part of a require section must be organized as a dictionary." + self.idebug(data))
                else:
                    raise DAError("A require section must have an orelse part." + self.idebug(data))
            else:
                raise DAError("A require section must be organized as a list." + self.idebug(data))
        if 'attachment' in data:
            self.attachments = self.process_attachment_list(data['attachment'])
        elif 'attachments' in data:
            self.attachments = self.process_attachment_list(data['attachments'])
        elif 'attachment code' in data:
            self.process_attachment_code(data['attachment code'])
        elif 'attachments code' in data:
            self.process_attachment_code(data['attachments code'])
        if 'allow emailing' in data:
            self.allow_emailing = data['allow emailing']
        if 'allow downloading' in data:
            self.allow_downloading = data['allow downloading']
        if 'email subject' in data:
            self.email_subject = TextObject(definitions + str(data['email subject']), question=self)
        if 'email body' in data:
            self.email_body = TextObject(definitions + str(data['email body']), question=self)
        if 'email template' in data:
            self.email_template = compile(data['email template'], '<email template>', 'eval')
            self.find_fields_in(data['email template'])
        if 'email address default' in data:
            self.email_default = TextObject(definitions + str(data['email address default']), question=self)
        if 'always include editable files' in data:
            self.always_include_editable_files = data['always include editable files']
        if 'include attachment notice' in data:
            self.attachment_notice = data['include attachment notice']
        if 'include download tab' in data:
            self.download_tab = data['include download tab']
        if 'manual attachment list' in data:
            self.manual_attachment_list = data['manual attachment list']
        # if 'role' in data:
        #     if isinstance(data['role'], list):
        #         for rolename in data['role']:
        #             if rolename not in self.role:
        #                 self.role.append(rolename)
        #     elif isinstance(data['role'], str) and data['role'] not in self.role:
        #         self.role.append(data['role'])
        #     else:
        #         raise DAError("A role section must be text or a list." + self.idebug(data))
        if 'progress' in data:
            if data['progress'] is None:
                self.progress = -1
            else:
                try:
                    self.progress = int(data['progress'])
                    self.interview.progress_points.add(self.progress)
                except:
                    logmessage("Invalid progress number " + repr(data['progress']))
        if 'zip filename' in data:
            self.zip_filename = TextObject(definitions + str(data['zip filename']), question=self)
        if 'action' in data:
            self.question_type = 'backgroundresponseaction'
            self.content = TextObject('action')
            self.action = data['action']
        if 'backgroundresponse' in data:
            self.question_type = 'backgroundresponse'
            self.content = TextObject('backgroundresponse')
            self.backgroundresponse = data['backgroundresponse']
        if 'response' in data:
            self.content = TextObject(definitions + str(data['response']), question=self)
            self.question_type = 'response'
        elif 'binaryresponse' in data:
            self.question_type = 'response'
            self.content = TextObject('binary')
            self.binaryresponse = data['binaryresponse']
            if 'response' not in data:
                self.content = TextObject('')
        elif 'all_variables' in data:
            self.question_type = 'response'
            self.all_variables = True
            if 'include_internal' in data:
                self.include_internal = data['include_internal']
            self.content = TextObject('all_variables')
        elif 'response filename' in data:
            self.question_type = 'sendfile'
            if data['response filename'].__class__.__name__ == 'DAFile':
                self.response_file = data['response filename']
                if hasattr(data['response filename'], 'mimetype') and data['response filename'].mimetype:
                    self.content_type = TextObject(data['response filename'].mimetype)
            else:
                info = docassemble.base.functions.server.file_finder(data['response filename'], question=self)
                if 'fullpath' in info and info['fullpath']:
                    self.response_file = FileOnServer(data['response filename'], self) #info['fullpath']
                else:
                    self.response_file = None
                if 'mimetype' in info and info['mimetype']:
                    self.content_type = TextObject(info['mimetype'])
                else:
                    self.content_type = TextObject('text/plain; charset=utf-8')
            self.content = TextObject('')
            if 'content type' in data:
                self.content_type = TextObject(definitions + str(data['content type']), question=self)
            elif not (hasattr(self, 'content_type') and self.content_type):
                if self.response_file is not None:
                    self.content_type = TextObject(get_mimetype(self.response_file.path()))
                else:
                    self.content_type = TextObject('text/plain; charset=utf-8')
        elif 'redirect url' in data:
            self.question_type = 'redirect'
            self.content = TextObject(definitions + str(data['redirect url']), question=self)
        elif 'null response' in data:
            self.content = TextObject('null')
            self.question_type = 'response'
        if 'sleep' in data:
            self.sleep = data['sleep']
        if 'response' in data or 'binaryresponse' in data or 'all_variables' or 'null response' in data:
            if 'include_internal' in data:
                self.include_internal = data['include_internal']
            if 'content type' in data:
                self.content_type = TextObject(definitions + str(data['content type']), question=self)
            else:
                self.content_type = TextObject('text/plain; charset=utf-8')
            if 'response code' in data:
                self.response_code = data['response code']
        if 'css class' in data:
            if 'question' not in data:
                raise DAError("A css class can only accompany a question." + self.idebug(data))
            self.css_class = TextObject(definitions + str(data['css class']), question=self)
        if 'table css class' in data:
            if 'question' not in data:
                raise DAError("A table css class can only accompany a question." + self.idebug(data))
            self.table_css_class = TextObject(definitions + str(data['table css class']), question=self)
        if 'question' in data:
            self.content = TextObject(definitions + str(data['question']), question=self)
        if 'subquestion' in data:
            self.subcontent = TextObject(definitions + str(data['subquestion']), question=self)
        if 'reload' in data and data['reload']:
            self.reload_after = TextObject(definitions + str(data['reload']), question=self)
        if 'help' in data:
            if isinstance(data['help'], dict):
                for key, value in data['help'].items():
                    if key == 'label':
                        self.helplabel = TextObject(definitions + str(value), question=self)
                    if key == 'audio':
                        if not isinstance(value, list):
                            the_list = [value]
                        else:
                            the_list = value
                        for list_item in the_list:
                            if isinstance(list_item, (dict, list, set)):
                                raise DAError("An audio declaration in a help block can only contain a text item or a list of text items." + self.idebug(data))
                            if self.audiovideo is None:
                                self.audiovideo = dict()
                            if 'help' not in self.audiovideo:
                                self.audiovideo['help'] = list()
                            self.audiovideo['help'].append({'text': TextObject(definitions + str(list_item.strip()), question=self), 'package': self.package, 'type': 'audio'})
                    if key == 'video':
                        if not isinstance(value, list):
                            the_list = [value]
                        else:
                            the_list = value
                        for list_item in the_list:
                            if isinstance(list_item, (dict, list, set)):
                                raise DAError("A video declaration in a help block can only contain a text item or a list of text items." + self.idebug(data))
                            if self.audiovideo is None:
                                self.audiovideo = dict()
                            if 'help' not in self.audiovideo:
                                self.audiovideo['help'] = list()
                            self.audiovideo['help'].append({'text': TextObject(definitions + str(list_item.strip()), question=self), 'package': self.package, 'type': 'video'})
                    if key == 'content':
                        if isinstance(value, (dict, list, set)):
                            raise DAError("A content declaration in a help block can only contain text." + self.idebug(data))
                        self.helptext = TextObject(definitions + str(value), question=self)
            else:
                self.helptext = TextObject(definitions + str(data['help']), question=self)
        if 'audio' in data:
            if not isinstance(data['audio'], list):
                the_list = [data['audio']]
            else:
                the_list = data['audio']
            for list_item in the_list:
                if isinstance(list_item, (dict, list, set)):
                    raise DAError("An audio declaration can only contain a text item or a list of text items." + self.idebug(data))
                if self.audiovideo is None:
                    self.audiovideo = dict()
                if 'question' not in self.audiovideo:
                    self.audiovideo['question'] = list()
                self.audiovideo['question'].append({'text': TextObject(definitions + str(list_item.strip()), question=self), 'package': self.package, 'type': 'audio'})
        if 'video' in data:
            if not isinstance(data['video'], list):
                the_list = [data['video']]
            else:
                the_list = data['video']
            for list_item in the_list:
                if isinstance(list_item, (dict, list, set)):
                    raise DAError("A video declaration can only contain a text item or a list of text items." + self.idebug(data))
                if self.audiovideo is None:
                    self.audiovideo = dict()
                if 'question' not in self.audiovideo:
                    self.audiovideo['question'] = list()
                self.audiovideo['question'].append({'text': TextObject(definitions + str(list_item.strip()), question=self), 'package': self.package, 'type': 'video'})
        if 'decoration' in data:
            if isinstance(data['decoration'], dict):
                decoration_list = [data['decoration']]
            elif isinstance(data['decoration'], list):
                decoration_list = data['decoration']
            else:
                decoration_list = [{'image': str(data['decoration'])}]
            processed_decoration_list = []
            for item in decoration_list:
                if isinstance(item, dict):
                    the_item = item
                else:
                    the_item = {'image': str(item.rstrip())}
                item_to_add = dict()
                for key, value in the_item.items():
                    item_to_add[key] = TextObject(do_not_translate + value, question=self)
                processed_decoration_list.append(item_to_add)
            self.decorations = processed_decoration_list
        if 'signature' in data:
            self.question_type = 'signature'
            if 'required' in data:
                if isinstance(data['required'], bool):
                    is_required = data['required']
                else:
                    is_required = {'compute': compile(data['required'], '<required code>', 'eval'), 'sourcecode': data['required']}
                    self.find_fields_in(data['required'])
                self.fields.append(Field({'saveas': data['signature'], 'required': is_required}))
            else:
                self.fields.append(Field({'saveas': data['signature']}))
            if self.scan_for_variables:
                self.fields_used.add(data['signature'])
            else:
                self.other_fields_used.add(data['signature'])
        elif 'required' in data:
            raise DAError("The required modifier can only be used on a signature block" + self.idebug(data))
        if 'question metadata' in data:
            self.question_metadata = recursive_textobject_or_primitive(data['question metadata'], self)
        if 'under' in data:
            self.undertext = TextObject(definitions + str(data['under']), question=self)
        if 'pre' in data:
            self.pretext = TextObject(definitions + str(data['pre']), question=self)
        if 'post' in data:
            self.posttext = TextObject(definitions + str(data['post']), question=self)
        if 'right' in data:
            self.righttext = TextObject(definitions + str(data['right']), question=self)
        if 'check in' in data:
            self.interview.uses_action = True
            if isinstance(data['check in'], (dict, list, set)):
                raise DAError("A check in event must be text or a list." + self.idebug(data))
            self.checkin = str(data['check in'])
            self.names_used.add(str(data['check in']))
        if 'yesno' in data:
            if not isinstance(data['yesno'], str):
                raise DAError("A yesno must refer to text." + self.idebug(data))
            self.fields.append(Field({'saveas': data['yesno'], 'boolean': 1}))
            if self.scan_for_variables:
                self.fields_used.add(data['yesno'])
            else:
                self.other_fields_used.add(data['yesno'])
            self.question_type = 'yesno'
        if 'noyes' in data:
            if not isinstance(data['noyes'], str):
                raise DAError("A noyes must refer to text." + self.idebug(data))
            self.fields.append(Field({'saveas': data['noyes'], 'boolean': -1}))
            if self.scan_for_variables:
                self.fields_used.add(data['noyes'])
            else:
                self.other_fields_used.add(data['noyes'])
            self.question_type = 'noyes'
        if 'yesnomaybe' in data:
            if not isinstance(data['yesnomaybe'], str):
                raise DAError("A yesnomaybe must refer to text." + self.idebug(data))
            self.fields.append(Field({'saveas': data['yesnomaybe'], 'threestate': 1}))
            if self.scan_for_variables:
                self.fields_used.add(data['yesnomaybe'])
            else:
                self.other_fields_used.add(data['yesnomaybe'])
            self.question_type = 'yesnomaybe'
        if 'noyesmaybe' in data:
            if not isinstance(data['noyesmaybe'], str):
                raise DAError("A noyesmaybe must refer to text." + self.idebug(data))
            self.fields.append(Field({'saveas': data['noyesmaybe'], 'threestate': -1}))
            if self.scan_for_variables:
                self.fields_used.add(data['noyesmaybe'])
            else:
                self.other_fields_used.add(data['noyesmaybe'])
            self.question_type = 'noyesmaybe'
        if 'sets' in data:
            if isinstance(data['sets'], str):
                self.fields_used.add(data['sets'])
            elif isinstance(data['sets'], list):
                for key in data['sets']:
                    self.fields_used.add(key)
            else:
                raise DAError("A sets phrase must be text or a list." + self.idebug(data))
        if 'event' in data:
            self.interview.uses_action = True
            if isinstance(data['event'], str):
                self.fields_used.add(data['event'])
            elif isinstance(data['event'], list):
                for key in data['event']:
                    self.fields_used.add(key)
            else:
                raise DAError("An event phrase must be text or a list." + self.idebug(data))
        if 'choices' in data or 'buttons' in data or 'dropdown' in data or 'combobox' in data:
            if 'field' in data:
                uses_field = True
                data['field'] = data['field'].strip()
            else:
                uses_field = False
            if 'shuffle' in data and data['shuffle']:
                shuffle = True
            else:
                shuffle = False
            if 'choices' in data or 'dropdown' in data or 'combobox' in data:
                if 'choices' in data:
                    has_code, choices = self.parse_fields(data['choices'], register_target, uses_field)
                    self.question_variety = 'radio'
                elif 'combobox' in data:
                    has_code, choices = self.parse_fields(data['combobox'], register_target, uses_field)
                    self.question_variety = 'combobox'
                else:
                    has_code, choices = self.parse_fields(data['dropdown'], register_target, uses_field)
                    self.question_variety = 'dropdown'
                field_data = {'choices': choices, 'shuffle': shuffle}
                if has_code:
                    field_data['has_code'] = True
                if 'default' in data:
                    field_data['default'] = TextObject(definitions + str(data['default']), question=self)
            elif 'buttons' in data:
                has_code, choices = self.parse_fields(data['buttons'], register_target, uses_field)
                field_data = {'choices': choices, 'shuffle': shuffle}
                if has_code:
                    field_data['has_code'] = True
                self.question_variety = 'buttons'
            if 'validation messages' in data:
                if not isinstance(data['validation messages'], dict):
                    raise DAError("A validation messages indicator must be a dictionary." + self.idebug(data))
                field_data['validation messages'] = dict()
                for validation_key, validation_message in data['validation messages'].items():
                    if not (isinstance(validation_key, str) and isinstance(validation_message, str)):
                        raise DAError("A validation messages indicator must be a dictionary of text keys and text values." + self.idebug(data))
                    field_data['validation messages'][validation_key] = TextObject(definitions + str(validation_message).strip(), question=self)
            if uses_field:
                data['field'] = data['field'].strip()
                if invalid_variable_name(data['field']):
                    raise DAError("Missing or invalid variable name " + repr(data['field']) + "." + self.idebug(data))
                if self.scan_for_variables:
                    self.fields_used.add(data['field'])
                else:
                    self.other_fields_used.add(data['field'])
                field_data['saveas'] = data['field']
                if 'datatype' in data and 'type' not in field_data:
                    field_data['type'] = data['datatype']
                elif is_boolean(field_data):
                    field_data['type'] = 'boolean'
                elif is_threestate(field_data):
                    field_data['type'] = 'threestate'
            self.fields.append(Field(field_data))
            self.question_type = 'multiple_choice'
        elif 'continue button field' in data and 'fields' not in data and 'yesno' not in data and 'noyes' not in data and 'yesnomaybe' not in data and 'noyesmaybe' not in data and 'signature' not in data:
            if not isinstance(data['continue button field'], str):
                raise DAError("A continue button field must be plain text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['continue button field'])
            else:
                self.other_fields_used.add(data['continue button field'])
            if 'review' in data:
                self.review_saveas = data['continue button field']
            else:
                field_data = {'saveas': data['continue button field']}
                self.fields.append(Field(field_data))
                self.question_type = 'settrue'
        if 'need' in data:
            if isinstance(data['need'], (str, dict)):
                need_list = [data['need']]
            elif isinstance(data['need'], list):
                need_list = data['need']
            else:
                raise DAError("A need phrase must be text or a list." + self.idebug(data))
            pre_need_list = []
            post_need_list = []
            for item in need_list:
                if isinstance(item, dict):
                    if not (('pre' in item and len(item) == 1) or ('post' in item and len(item) == 1) or ('pre' in item and 'post' in item and len(item) == 2)):
                        raise DAError("If 'need' contains a dictionary it can only include keys 'pre' or 'post'." + self.idebug(data))
                    if 'post' in item:
                        if isinstance(item['post'], str):
                            post_need_list.append(item['post'])
                        elif isinstance(item['post'], list):
                            post_need_list.extend(item['post'])
                        else:
                            raise DAError("A need post phrase must be text or a list." + self.idebug(data))
                    if 'pre' in item:
                        if isinstance(item['pre'], str):
                            pre_need_list.append(item['pre'])
                        elif isinstance(item['pre'], list):
                            pre_need_list.extend(item['pre'])
                        else:
                            raise DAError("A need pre phrase must be text or a list." + self.idebug(data))
                else:
                    pre_need_list.append(item)
            for sub_item in pre_need_list + post_need_list:
                if not isinstance(sub_item, str):
                    raise DAError("In 'need', the items must be text strings." + self.idebug(data))
            if len(pre_need_list):
                try:
                    self.need = list(map((lambda x: compile(x, '<need expression>', 'eval')), pre_need_list))
                    for x in pre_need_list:
                        self.find_fields_in(x)
                except:
                    logmessage("Question: compile error in need code:\n" + str(data['need']) + "\n" + str(sys.exc_info()[0]))
                    raise
            if len(post_need_list):
                try:
                    self.need_post = list(map((lambda x: compile(x, '<post need expression>', 'eval')), post_need_list))
                    for x in post_need_list:
                        self.find_fields_in(x)
                except:
                    logmessage("Question: compile error in need code:\n" + str(data['need']) + "\n" + str(sys.exc_info()[0]))
                    raise
        if 'depends on' in data:
            if not isinstance(data['depends on'], list):
                depends_list = [str(data['depends on'])]
            else:
                depends_list = [str(x) for x in data['depends on']]
            # if len(depends_list):
            #     if self.need is None:
            #         self.need = list()
            #     self.need += list(map((lambda x: compile(x, '<depends expression>', 'exec')), depends_list))
        else:
            depends_list = []
        if 'target' in data:
            self.interview.uses_action = True
            if isinstance(data['target'], (list, dict, set, bool, int, float)):
                raise DAError("The target of a template must be plain text." + self.idebug(data))
            if 'template' not in data:
                raise DAError("A target directive can only be used with a template." + self.idebug(data))
            self.target = data['target']
        if 'table' in data or 'rows' in data or 'columns' in data:
            if 'table' not in data or 'rows' not in data or 'columns' not in data:
                raise DAError("A table definition must have definitions for table, row, and column." + self.idebug(data))
            if isinstance(data['rows'], (list, dict, set, bool, int, float)):
                raise DAError("The row part of a table definition must be plain Python code." + self.idebug(data))
            data['rows'] = data['rows'].strip()
            if not isinstance(data['columns'], list):
                raise DAError("The column part of a table definition must be a list." + self.idebug(data))
            row = compile(data['rows'], '<row code>', 'eval')
            self.find_fields_in(data['rows'])
            header = list()
            column = list()
            read_only = dict(edit=True, delete=True)
            is_editable = False
            require_gathered = True
            if 'require gathered' in data and data['require gathered'] is False:
                require_gathered = False
            else:
                require_gathered = True
            if 'show incomplete' in data and data['show incomplete'] is True:
                show_incomplete = True
            else:
                show_incomplete = False
            if show_incomplete is True or require_gathered is False:
                ensure_complete = False
            else:
                ensure_complete = True
            if 'not available label' in data and isinstance(data['not available label'], str):
                not_available_label = data['not available label'].strip()
            else:
                # word('n/a')
                not_available_label = 'n/a'
            for col in data['columns']:
                if not isinstance(col, dict):
                    raise DAError("The column items in a table definition must be dictionaries." + self.idebug(data))
                if len(col) == 0:
                    raise DAError("A column item in a table definition cannot be empty." + self.idebug(data))
                if 'header' in col and 'cell' in col:
                    header_text = col['header']
                    cell_text = str(col['cell']).strip()
                else:
                    for key, val in col.items():
                        header_text = key
                        cell_text = str(val).strip()
                        break
                if header_text == '':
                    header.append(TextObject('&nbsp;'))
                else:
                    header.append(TextObject(definitions + str(header_text), question=self))
                self.find_fields_in(cell_text)
                column.append(compile(cell_text, '<column code>', 'eval'))
            if 'allow reordering' in data and data['allow reordering'] is not False:
                reorder = True
            else:
                reorder = False
            if 'edit' in data and data['edit'] is not False:
                is_editable = True
                if isinstance(data['edit'], list):
                    if len(data['edit']) == 0:
                        raise DAError("The edit directive must be a list of attributes, or True or False" + self.idebug(data))
                    for attribute_name in data['edit']:
                        if not isinstance(attribute_name, str):
                            raise DAError("The edit directive must be a list of attribute names" + self.idebug(data))
                elif not isinstance(data['edit'], bool):
                    raise DAError("The edit directive must be a list of attributes, or True or False" + self.idebug(data))
                keyword_args = ''
                if 'delete buttons' in data and not data['delete buttons']:
                    keyword_args += ', delete=False'
                if 'confirm' in data and data['confirm']:
                    keyword_args += ', confirm=True'
                if 'read only' in data:
                    if not isinstance(data['read only'], str):
                        raise DAError("The read only directive must be plain text referring to an attribute" + self.idebug(data))
                    keyword_args += ', read_only_attribute=' + repr(data['read only'].strip())
                if isinstance(data['edit'], list):
                    column.append(compile('(' + data['rows'] + ').item_actions(row_item, row_index, ' + ', '.join([repr(y) for y in data['edit']]) + keyword_args + ', reorder=' + repr(reorder) + ', ensure_complete=' + repr(ensure_complete) + ')', '<edit code>', 'eval'))
                else:
                    column.append(compile('(' + data['rows'] + ').item_actions(row_item, row_index' + keyword_args + ', reorder=' + repr(reorder) + ', ensure_complete=' + repr(ensure_complete) + ')', '<edit code>', 'eval'))
                if 'edit header' in data:
                    if not isinstance(data['edit header'], str):
                        raise DAError("The edit header directive must be text" + self.idebug(data))
                    if data['edit header'] == '':
                        header.append(TextObject('&nbsp;'))
                    else:
                        header.append(TextObject(definitions + str(data['edit header']), question=self))
                else:
                    header.append(TextObject(word("Actions")))
            elif ('delete buttons' in data and data['delete buttons']) or reorder:
                is_editable = True
                keyword_args = ''
                if 'read only' in data:
                    if not isinstance(data['read only'], str):
                        raise DAError("The read only directive must be plain text referring to an attribute" + self.idebug(data))
                    keyword_args += ', read_only_attribute=' + repr(data['read only'].strip())
                if 'confirm' in data and data['confirm']:
                    keyword_args += ', confirm=True'
                if 'delete buttons' in data and data['delete buttons']:
                    column.append(compile('(' + data['rows'] + ').item_actions(row_item, row_index, edit=False' + keyword_args + ', reorder=' + repr(reorder) + ', ensure_complete=' + repr(ensure_complete) + ')', '<delete button code>', 'eval'))
                else:
                    column.append(compile('(' + data['rows'] + ').item_actions(row_item, row_index, edit=False' + keyword_args + ', delete=False, reorder=' + repr(reorder) + ', ensure_complete=' + repr(ensure_complete) + ')', '<reorder buttons code>', 'eval'))
                if 'edit header' in data:
                    if not isinstance(data['edit header'], str):
                        raise DAError("The edit header directive must be text" + self.idebug(data))
                    if data['edit header'] == '':
                        header.append(TextObject('&nbsp;'))
                    else:
                        header.append(TextObject(definitions + str(data['edit header']), question=self))
                else:
                    header.append(TextObject(word("Actions")))
            if self.scan_for_variables:
                self.fields_used.add(data['table'])
            else:
                self.other_fields_used.add(data['table'])
            empty_message = data.get('show if empty', True)
            if empty_message not in (True, False, None):
                empty_message = TextObject(definitions + str(empty_message), question=self)
            field_data = {'saveas': data['table'], 'extras': dict(header=header, row=row, column=column, empty_message=empty_message, indent=data.get('indent', False), is_editable=is_editable, require_gathered=require_gathered, show_incomplete=show_incomplete, not_available_label=not_available_label)}
            self.fields.append(Field(field_data))
            self.content = TextObject('')
            self.subcontent = TextObject('')
            self.question_type = 'table'
        if 'template' in data and 'content file' in data:
            if isinstance(data['content file'], dict):
                if len(data['content file']) == 1 and 'code' in data['content file'] and isinstance(data['content file']['code'], str):
                    if self.scan_for_variables:
                        self.fields_used.add(data['template'])
                    else:
                        self.other_fields_used.add(data['template'])
                    field_data = {'saveas': data['template']}
                    self.fields.append(Field(field_data))
                    self.compute = compile(data['content file']['code'], '<content file code>', 'eval')
                    self.sourcecode = data['content file']['code']
                    self.find_fields_in(data['content file']['code'])
                    self.question_type = 'template_code'
                else:
                    raise DAError('A content file must be specified as text, as a list of text filenames, or as a dictionary with code as the key' + self.idebug(data))
            else:
                if not isinstance(data['content file'], list):
                    data['content file'] = [data['content file']]
                data['content'] = ''
                for content_file in data['content file']:
                    if not isinstance(content_file, str):
                        raise DAError('A content file must be specified as text, as a list of text filenames, or as a dictionary with code as the key' + self.idebug(data))
                    file_to_read = docassemble.base.functions.package_template_filename(content_file, package=self.package)
                    #if file_to_read is not None and get_mimetype(file_to_read) != 'text/markdown':
                    #    raise DAError('The content file ' + str(data['content file']) + ' is not a markdown file ' + str(file_to_read) + self.idebug(data))
                    if file_to_read is not None and os.path.isfile(file_to_read) and os.access(file_to_read, os.R_OK):
                        with open(file_to_read, 'r', encoding='utf-8') as the_file:
                            data['content'] += the_file.read()
                    else:
                        raise DAError('Unable to read content file ' + str(data['content file']) + ' after trying to find it at ' + str(file_to_read) + self.idebug(data))
        if 'template' in data and 'content' in data:
            if isinstance(data['template'], (list, dict)):
                raise DAError("A template must designate a single variable expressed as text." + self.idebug(data))
            if isinstance(data['content'], (list, dict)):
                raise DAError("The content of a template must be expressed as text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['template'])
            else:
                self.other_fields_used.add(data['template'])
            field_data = {'saveas': data['template']}
            self.fields.append(Field(field_data))
            self.content = TextObject(definitions + str(data['content']), question=self)
            #logmessage("keys are: " + str(self.mako_names))
            if 'subject' in data:
                self.subcontent = TextObject(definitions + str(data['subject']), question=self)
            else:
                self.subcontent = TextObject("")
            self.question_type = 'template'
            #if self.scan_for_variables:
            #    self.reset_list = self.fields_used
        if 'code' in data:
            if 'event' in data:
                self.question_type = 'event_code'
                self.scan_for_variables = False
            else:
                self.question_type = 'code'
            if isinstance(data['code'], str):
                if not self.interview.calls_process_action and match_process_action.search(data['code']):
                    self.interview.calls_process_action = True
                try:
                    self.compute = compile(data['code'], '<code block>', 'exec')
                    self.sourcecode = data['code']
                except:
                    logmessage("Question: compile error in code:\n" + str(data['code']) + "\n" + str(sys.exc_info()[0]))
                    raise
                self.find_fields_in(data['code'])
            else:
                raise DAError("A code section must be text, not a list or a dictionary." + self.idebug(data))
        if 'reconsider' in data:
            #if not isinstance(data['reconsider'], bool):
            #    raise DAError("A reconsider directive must be true or false." + self.idebug(data))
            if isinstance(data['reconsider'], bool):
                if data['reconsider']:
                    if self.is_generic:
                        if self.generic_object not in self.interview.reconsider_generic:
                            self.interview.reconsider_generic[self.generic_object] = set()
                        self.interview.reconsider_generic[self.generic_object].update(self.fields_used)
                    else:
                        self.interview.reconsider.update(self.fields_used)
            else:
                if isinstance(data['reconsider'], str):
                    fields = [data['reconsider']]
                elif isinstance(data['reconsider'], list):
                    fields = data['reconsider']
                else:
                    raise DAError("A reconsider directive must be true, false, a single variable or a list." + self.idebug(data))
                for the_field in fields:
                    if not isinstance(the_field, str):
                        raise DAError("A reconsider directive must refer to variable names expressed as text." + self.idebug(data))
                    self.find_fields_in(the_field)
                    self.reconsider.append(the_field)
        if 'undefine' in data:
            if isinstance(data['undefine'], str):
                fields = [data['undefine']]
            elif isinstance(data['undefine'], list):
                fields = data['undefine']
            else:
                raise DAError("A undefine directive must a single variable or a list." + self.idebug(data))
            for the_field in fields:
                if not isinstance(the_field, str):
                    raise DAError("A undefine directive must refer to variable names expressed as text." + self.idebug(data))
                self.find_fields_in(the_field)
                self.undefine.append(the_field)
        if 'continue button field' in data and 'question' in data and ('field' in data or 'fields' in data or 'yesno' in data or 'noyes' in data or 'yesnomaybe' in data or 'noyesmaybe' in data or 'signature' in data):
            if not isinstance(data['continue button field'], str):
                raise DAError("A continue button field must be plain text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['continue button field'])
            else:
                self.other_fields_used.add(data['continue button field'])
            self.fields_saveas = data['continue button field']
        if 'fields' in data:
            self.question_type = 'fields'
            if isinstance(data['fields'], dict):
                data['fields'] = [data['fields']]
            if not isinstance(data['fields'], list):
                raise DAError("The fields must be written in the form of a list." + self.idebug(data))
            else:
                field_number = 0
                for field in data['fields']:
                    docassemble.base.functions.this_thread.misc['current_field'] = field_number
                    if isinstance(field, dict):
                        manual_keys = set()
                        field_info = {'type': 'text', 'number': field_number}
                        if 'datatype' in field:
                            if field['datatype'] in ('radio', 'combobox', 'pulldown', 'ajax'):
                                field['input type'] = field['datatype']
                                field['datatype'] = 'text'
                            if field['datatype'] == 'mlarea':
                                field['input type'] = 'area'
                                field['datatype'] = 'ml'
                            if field['datatype'] == 'area':
                                field['input type'] = 'area'
                                field['datatype'] = 'text'
                        if 'input type' in field and field['input type'] == 'ajax':
                            if 'action' not in field:
                                raise DAError("An ajax field must have an associated action." + self.idebug(data))
                            if 'choices' in field or 'code' in field:
                                raise DAError("An ajax field cannot contain a list of choices except through an action." + self.idebug(data))
                        if len(field) == 1 and 'code' in field:
                            field_info['type'] = 'fields_code'
                            self.find_fields_in(field['code'])
                            field_info['extras'] = dict(fields_code=compile(field['code'], '<fields code>', 'eval'))
                            self.fields.append(Field(field_info))
                            field_number += 1
                            if 'current_field' in docassemble.base.functions.this_thread.misc:
                                del docassemble.base.functions.this_thread.misc['current_field']
                            continue
                        if 'datatype' in field and field['datatype'] in ('object', 'object_radio', 'multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes') and not ('choices' in field or 'code' in field):
                            raise DAError("A multiple choice field must refer to a list of choices." + self.idebug(data))
                        if 'input type' in field and field['input type'] in ('radio', 'combobox', 'pulldown') and not ('choices' in field or 'code' in field):
                            raise DAError("A multiple choice field must refer to a list of choices." + self.idebug(data))
                        if 'object labeler' in field and ('datatype' not in field or not field['datatype'].startswith('object')):
                            raise DAError("An object labeler can only be used with an object data type")
                        if 'note' in field and 'html' in field:
                            raise DAError("You cannot include both note and html in a field." + self.idebug(data))
                        for key in field:
                            if key == 'default' and 'datatype' in field and field['datatype'] in ('object', 'object_radio', 'object_multiselect', 'object_checkboxes'):
                                continue
                            if key == 'input type':
                                field_info['inputtype'] = field[key]
                            elif 'datatype' in field and field['datatype'] in ('ml', 'mlarea') and key in ('using', 'keep for training'):
                                if key == 'using':
                                    if 'extras' not in field_info:
                                        field_info['extras'] = dict()
                                    field_info['extras']['ml_group'] = TextObject(definitions + str(field[key]), question=self)
                                if key == 'keep for training':
                                    if 'extras' not in field_info:
                                        field_info['extras'] = dict()
                                    if isinstance(field[key], bool):
                                        field_info['extras']['ml_train'] = field[key]
                                    else:
                                        field_info['extras']['ml_train'] = {'compute': compile(field[key], '<keep for training code>', 'eval'), 'sourcecode': field[key]}
                                        self.find_fields_in(field[key])
                            elif key == 'validation messages':
                                if not isinstance(field[key], dict):
                                    raise DAError("A validation messages indicator must be a dictionary." + self.idebug(data))
                                field_info['validation messages'] = dict()
                                for validation_key, validation_message in field[key].items():
                                    if not (isinstance(validation_key, str) and isinstance(validation_message, str)):
                                        raise DAError("A validation messages indicator must be a dictionary of text keys and text values." + self.idebug(data))
                                    field_info['validation messages'][validation_key] = TextObject(definitions + str(validation_message).strip(), question=self)
                            elif key == 'validate':
                                field_info['validate'] = {'compute': compile(field[key], '<validate code>', 'eval'), 'sourcecode': field[key]}
                                self.find_fields_in(field[key])
                            elif key == 'rows' and (('input type' in field and field['input type'] == 'area') or ('datatype' in field and field['datatype'] in ('multiselect', 'object_multiselect'))):
                                field_info['rows'] = {'compute': compile(str(field[key]), '<rows code>', 'eval'), 'sourcecode': str(field[key])}
                                self.find_fields_in(field[key])
                            elif key == 'maximum image size' and 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment'):
                                field_info['max_image_size'] = {'compute': compile(str(field[key]), '<maximum image size code>', 'eval'), 'sourcecode': str(field[key])}
                                self.find_fields_in(field[key])
                            elif key == 'image upload type' and 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment'):
                                if field[key].lower().strip() in ('jpeg', 'jpg', 'bmp', 'png'):
                                    field_info['image_type'] = {'compute': compile(repr(field[key]), '<image upload type code>', 'eval'), 'sourcecode': repr(field[key])}
                                else:
                                    field_info['image_type'] = {'compute': compile(str(field[key]), '<image upload type code>', 'eval'), 'sourcecode': str(field[key])}
                            elif key == 'accept' and 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment'):
                                field_info['accept'] = {'compute': compile(field[key], '<accept code>', 'eval'), 'sourcecode': field[key]}
                                self.find_fields_in(field[key])
                            elif key == 'allow privileges' and 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment'):
                                if isinstance(field[key], list):
                                    for item in field[key]:
                                        if not isinstance(item, str):
                                            raise DAError("An allow privileges specifier must be a list of plain text items or code." + self.idebug(data))
                                    field_info['allow_privileges'] = field[key]
                                elif isinstance(field[key], str):
                                    field_info['allow_privileges'] = [field[key]]
                                elif isinstance(field[key], dict) and len(field[key]) == 1 and 'code' in field[key]:
                                    field_info['allow_privileges'] = {'compute': compile(field[key]['code'], '<allow privileges code>', 'eval'), 'sourcecode': field[key]['code']}
                                    self.find_fields_in(field[key]['code'])
                                else:
                                    raise DAError("An allow privileges specifier must be a list of plain text items or code." + self.idebug(data))
                            elif key == 'allow users' and 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment'):
                                if isinstance(field[key], list):
                                    for item in field[key]:
                                        if not isinstance(item, (str, int)):
                                            raise DAError("An allow users specifier must be a list of integers and plain text items or code." + self.idebug(data))
                                    field_info['allow_users'] = field[key]
                                elif isinstance(field[key], str):
                                    field_info['allow_users'] = [field[key]]
                                elif isinstance(field[key], dict) and len(field[key]) == 1 and 'code' in field[key]:
                                    field_info['allow_users'] = {'compute': compile(field[key]['code'], '<allow users code>', 'eval'), 'sourcecode': field[key]['code']}
                                    self.find_fields_in(field[key]['code'])
                                else:
                                    raise DAError("An allow users specifier must be a list of integers and plain text items or code." + self.idebug(data))
                            elif key == 'persistent' and 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment'):
                                if isinstance(field[key], bool):
                                    field_info['persistent'] = field[key]
                                else:
                                    field_info['persistent'] = {'compute': compile(field[key], '<persistent code>', 'eval'), 'sourcecode': field[key]}
                                    self.find_fields_in(field[key])
                            elif key == 'private' and 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment'):
                                if isinstance(field[key], bool):
                                    field_info['private'] = field[key]
                                else:
                                    field_info['private'] = {'compute': compile(field[key], '<public code>', 'eval'), 'sourcecode': field[key]}
                                    self.find_fields_in(field[key])
                            elif key == 'object labeler':
                                field_info['object_labeler'] = {'compute': compile(str(field[key]), '<object labeler code>', 'eval'), 'sourcecode': str(field[key])}
                                self.find_fields_in(field[key])
                            elif key == 'help generator':
                                field_info['help_generator'] = {'compute': compile(str(field[key]), '<help generator code>', 'eval'), 'sourcecode': str(field[key])}
                                self.find_fields_in(field[key])
                            elif key == 'image generator':
                                field_info['image_generator'] = {'compute': compile(str(field[key]), '<image generator code>', 'eval'), 'sourcecode': str(field[key])}
                                self.find_fields_in(field[key])
                            elif key == 'required':
                                if isinstance(field[key], bool):
                                    field_info['required'] = field[key]
                                else:
                                    field_info['required'] = {'compute': compile(field[key], '<required code>', 'eval'), 'sourcecode': field[key]}
                                    self.find_fields_in(field[key])
                            elif key == 'js show if' or key == 'js hide if':
                                if not isinstance(field[key], str):
                                    raise DAError("A js show if or js hide if expression must be a string" + self.idebug(data))
                                js_info = dict()
                                if key == 'js show if':
                                    js_info['sign'] = True
                                else:
                                    js_info['sign'] = False
                                js_info['mode'] = 0
                                js_info['expression'] = TextObject(definitions + str(field[key]).strip(), question=self, translate=False)
                                js_info['vars'] = list(set(re.findall(r'val\(\'([^\)]+)\'\)', field[key]) + re.findall(r'val\("([^\)]+)"\)', field[key])))
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['extras']['show_if_js'] = js_info
                            elif key == 'js disable if' or key == 'js enable if':
                                if not isinstance(field[key], str):
                                    raise DAError("A js disable if or js enable if expression must be a string" + self.idebug(data))
                                js_info = dict()
                                if key == 'js enable if':
                                    js_info['sign'] = True
                                else:
                                    js_info['sign'] = False
                                js_info['mode'] = 1
                                js_info['expression'] = TextObject(definitions + str(field[key]).strip(), question=self, translate=False)
                                js_info['vars'] = list(set(re.findall(r'val\(\'([^\)]+)\'\)', field[key]) + re.findall(r'val\("([^\)]+)"\)', field[key])))
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['extras']['show_if_js'] = js_info
                            elif key == 'show if' or key == 'hide if':
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                if isinstance(field[key], dict):
                                    showif_valid = False
                                    if 'variable' in field[key] and 'is' in field[key]:
                                        if 'js show if' in field or 'js hide if' in field:
                                            raise DAError("You cannot mix js show if and non-js show if" + self.idebug(data))
                                        if 'js disable if' in field or 'js enable if' in field:
                                            raise DAError("You cannot mix js disable if and non-js show if" + self.idebug(data))
                                        field_info['extras']['show_if_var'] = safeid(field[key]['variable'].strip())
                                        if isinstance(field[key]['is'], str):
                                            field_info['extras']['show_if_val'] = TextObject(definitions + str(field[key]['is']).strip(), question=self)
                                        else:
                                            field_info['extras']['show_if_val'] = TextObject(str(field[key]['is']))
                                        showif_valid = True
                                    if 'code' in field[key]:
                                        field_info['showif_code'] = compile(field[key]['code'], '<show if code>', 'eval')
                                        self.find_fields_in(field[key]['code'])
                                        showif_valid = True
                                    if not showif_valid:
                                        raise DAError("The keys of '" + key + "' must be 'variable' and 'is,' or 'code.'" + self.idebug(data))
                                elif isinstance(field[key], list):
                                    raise DAError("The keys of '" + key + "' cannot be a list" + self.idebug(data))
                                elif isinstance(field[key], str):
                                    field_info['extras']['show_if_var'] = safeid(field[key].strip())
                                    field_info['extras']['show_if_val'] = TextObject('True')
                                else:
                                    raise DAError("Invalid variable name in show if/hide if")
                                exclusive = False
                                if isinstance(field[key], dict) and 'code' in field[key]:
                                    if len(field[key]) == 1:
                                        exclusive = True
                                    if key == 'show if':
                                        field_info['extras']['show_if_sign_code'] = 1
                                    else:
                                        field_info['extras']['show_if_sign_code'] = 0
                                if not exclusive:
                                    if key == 'show if':
                                        field_info['extras']['show_if_sign'] = 1
                                    else:
                                        field_info['extras']['show_if_sign'] = 0
                                field_info['extras']['show_if_mode'] = 0
                            elif key == 'disable if' or key == 'enable if':
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                if isinstance(field[key], dict):
                                    showif_valid = False
                                    if 'variable' in field[key] and 'is' in field[key]:
                                        if 'js show if' in field or 'js hide if' in field:
                                            raise DAError("You cannot mix js show if and non-js disable if" + self.idebug(data))
                                        if 'js disable if' in field or 'js enable if' in field:
                                            raise DAError("You cannot mix js disable if and non-js disable if" + self.idebug(data))
                                        field_info['extras']['show_if_var'] = safeid(field[key]['variable'].strip())
                                        if isinstance(field[key]['is'], str):
                                            field_info['extras']['show_if_val'] = TextObject(definitions + str(field[key]['is']).strip(), question=self)
                                        else:
                                            field_info['extras']['show_if_val'] = TextObject(str(field[key]['is']))
                                        showif_valid = True
                                    if 'code' in field[key]:
                                        field_info['showif_code'] = compile(field[key]['code'], '<show if code>', 'eval')
                                        self.find_fields_in(field[key]['code'])
                                        showif_valid = True
                                    if not showif_valid:
                                        raise DAError("The keys of '" + key + "' must be 'variable' and 'is,' or 'code.'" + self.idebug(data))
                                elif isinstance(field[key], list):
                                    raise DAError("The keys of '" + key + "' cannot be a list" + self.idebug(data))
                                elif isinstance(field[key], str):
                                    field_info['extras']['show_if_var'] = safeid(field[key].strip())
                                    field_info['extras']['show_if_val'] = TextObject('True')
                                else:
                                    raise DAError("Invalid variable name in disable if/enable if")
                                exclusive = False
                                if isinstance(field[key], dict) and 'code' in field[key]:
                                    if len(field[key]) == 1:
                                        exclusive = True
                                    if key == 'enable if':
                                        field_info['extras']['show_if_sign_code'] = 1
                                    else:
                                        field_info['extras']['show_if_sign_code'] = 0
                                if not exclusive:
                                    if key == 'enable if':
                                        field_info['extras']['show_if_sign'] = 1
                                    else:
                                        field_info['extras']['show_if_sign'] = 0
                                field_info['extras']['show_if_mode'] = 1
                            elif key == 'default' or key == 'hint' or key == 'help':
                                if not isinstance(field[key], dict) and not isinstance(field[key], list):
                                    field_info[key] = TextObject(definitions + str(field[key]), question=self)
                                if key == 'default':
                                    if isinstance(field[key], dict) and 'code' in field[key]:
                                        if 'extras' not in field_info:
                                            field_info['extras'] = dict()
                                        field_info['extras']['default'] = {'compute': compile(field[key]['code'], '<default code>', 'eval'), 'sourcecode': field[key]['code']}
                                        self.find_fields_in(field[key]['code'])
                                    else:
                                        if isinstance(field[key], (dict, list)):
                                            field_info[key] = field[key]
                                        if 'datatype' not in field and 'code' not in field and 'choices' not in field:
                                            auto_determine_type(field_info, the_value=field[key])
                            elif key == 'disable others':
                                if 'datatype' in field and field['datatype'] in ('file', 'files', 'range', 'multiselect', 'checkboxes', 'camera', 'user', 'environment', 'camcorder', 'microphone', 'object_multiselect', 'object_checkboxes'): #'yesno', 'yesnowide', 'noyes', 'noyeswide',
                                    raise DAError("A 'disable others' directive cannot be used with this data type." + self.idebug(data))
                                if not isinstance(field[key], (list, bool)):
                                    raise DAError("A 'disable others' directive must be True, False, or a list of variable names." + self.idebug(data))
                                field_info['disable others'] = field[key]
                                if field[key] is not False:
                                    field_info['required'] = False
                            elif key == 'uncheck others' and 'datatype' in field and field['datatype'] in ('yesno', 'yesnowide', 'noyes', 'noyeswide'):
                                if not isinstance(field[key], (list, bool)):
                                    raise DAError("An 'uncheck others' directive must be True, False, or a list of variable names." + self.idebug(data))
                                field_info['uncheck others'] = field[key]
                            elif key == 'datatype':
                                field_info['type'] = field[key]
                                if field[key] in ('yesno', 'yesnowide', 'noyes', 'noyeswide') and 'required' not in field_info:
                                    field_info['required'] = False
                                if field[key] == 'range' and 'required' not in field_info:
                                    field_info['required'] = False
                                if field[key] == 'range' and not ('min' in field and 'max' in field):
                                    raise DAError("If the datatype of a field is 'range', you must provide a min and a max." + self.idebug(data))
                                if field[key] in ('yesno', 'yesnowide', 'yesnoradio'):
                                    field_info['boolean'] = 1
                                elif field[key] in ('noyes', 'noyeswide', 'noyesradio'):
                                    field_info['boolean'] = -1
                                elif field[key] == 'yesnomaybe':
                                    field_info['threestate'] = 1
                                elif field[key] == 'noyesmaybe':
                                    field_info['threestate'] = -1
                            elif key == 'code':
                                self.find_fields_in(field[key])
                                field_info['choicetype'] = 'compute'
                                field_info['selections'] = {'compute': compile(field[key], '<choices code>', 'eval'), 'sourcecode': field[key]}
                                self.find_fields_in(field[key])
                                if 'exclude' in field:
                                    if isinstance(field['exclude'], dict):
                                        raise DAError("An exclude entry cannot be a dictionary." + self.idebug(data))
                                    if not isinstance(field['exclude'], list):
                                        field_info['selections']['exclude'] = [compile(field['exclude'], '<expression>', 'eval')]
                                        self.find_fields_in(field['exclude'])
                                    else:
                                        field_info['selections']['exclude'] = list()
                                        for x in field['exclude']:
                                            field_info['selections']['exclude'].append(compile(x, '<expression>', 'eval'))
                                            self.find_fields_in(x)
                            elif key == 'address autocomplete':
                                field_info['address_autocomplete'] = True
                            elif key == 'action' and 'input type' in field and field['input type'] == 'ajax':
                                if not isinstance(field[key], str):
                                    raise DAError("An action must be plain text" + self.idebug(data))
                                if 'combobox action' not in field_info:
                                    field_info['combobox action'] = dict(trig=4)
                                field_info['combobox action']['action'] = field[key]
                            elif key == 'trigger at' and 'action' in field and 'input type' in field and field['input type'] == 'ajax':
                                if (not isinstance(field[key], int)) or field[key] < 2:
                                    raise DAError("A trigger at must an integer greater than one" + self.idebug(data))
                                if 'combobox action' not in field_info:
                                    field_info['combobox action'] = dict()
                                field_info['combobox action']['trig'] = field[key]
                            elif key == 'exclude':
                                pass
                            elif key == 'choices':
                                if 'datatype' in field and field['datatype'] in ('object', 'object_radio', 'object_multiselect', 'object_checkboxes'):
                                    field_info['choicetype'] = 'compute'
                                    if not isinstance(field[key], (list, str)):
                                        raise DAError("choices is not in appropriate format" + self.idebug(data))
                                    field_info['selections'] = dict()
                                else:
                                    field_info['choicetype'] = 'manual'
                                    field_info['selections'] = dict(values=self.process_selections_manual(field[key]))
                                    if 'datatype' not in field:
                                        auto_determine_type(field_info)
                                    for item in field_info['selections']['values']:
                                        if isinstance(item['key'], TextObject):
                                            if not item['key'].uses_mako:
                                                manual_keys.add(item['key'].original_text)
                                        else:
                                            manual_keys.add(item['key'])
                                if 'exclude' in field:
                                    if isinstance(field['exclude'], dict):
                                        raise DAError("An exclude entry cannot be a dictionary." + self.idebug(data))
                                    if not isinstance(field['exclude'], list):
                                        self.find_fields_in(field['exclude'])
                                        field_info['selections']['exclude'] = [compile(field['exclude'].strip(), '<expression>', 'eval')]
                                    else:
                                        field_info['selections']['exclude'] = list()
                                        for x in field['exclude']:
                                            self.find_fields_in(x)
                                            field_info['selections']['exclude'].append(compile(x, '<expression>', 'eval'))
                            elif key in ('note', 'html'):
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['extras'][key] = TextObject(definitions + str(field[key]), question=self)
                            elif key == 'field metadata':
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['extras'][key] = recursive_textobject_or_primitive(field[key], self)
                            elif key in ('min', 'max', 'minlength', 'maxlength', 'step', 'scale', 'inline', 'inline width', 'currency symbol'):
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['extras'][key] = TextObject(definitions + str(field[key]), question=self)
                            # elif key in ('css', 'script'):
                            #     if 'extras' not in field_info:
                            #         field_info['extras'] = dict()
                            #     if field_info['type'] == 'text':
                            #         field_info['type'] = key
                            #     field_info['extras'][key] = TextObject(definitions + str(field[key]), question=self)
                            elif key == 'shuffle':
                                field_info['shuffle'] = field[key]
                            elif key == 'none of the above' and 'datatype' in field and field['datatype'] in ('checkboxes', 'object_checkboxes', 'object_radio'):
                                if isinstance(field[key], bool):
                                    field_info['nota'] = field[key]
                                else:
                                    field_info['nota'] = TextObject(definitions + interpret_label(field[key]), question=self)
                            elif key == 'field':
                                if 'label' not in field:
                                    raise DAError("If you use 'field' to indicate a variable in a 'fields' section, you must also include a 'label.'" + self.idebug(data))
                                if not isinstance(field[key], str):
                                    raise DAError("Fields in a 'field' section must be plain text." + self.idebug(data))
                                field[key] = field[key].strip()
                                if invalid_variable_name(field[key]):
                                    raise DAError("Missing or invalid variable name " + repr(field[key]) + "." + self.idebug(data))
                                field_info['saveas'] = field[key]
                            elif key == 'label':
                                if 'field' not in field:
                                    raise DAError("If you use 'label' to label a field in a 'fields' section, you must also include a 'field.'" + self.idebug(data))
                                field_info['label'] = TextObject(definitions + interpret_label(field[key]), question=self)
                            else:
                                if 'label' in field_info:
                                    raise DAError("Syntax error: field label '" + str(key) + "' overwrites previous label, '" + str(field_info['label'].original_text) + "'" + self.idebug(data))
                                field_info['label'] = TextObject(definitions + interpret_label(key), question=self)
                                if not isinstance(field[key], str):
                                    raise DAError("Fields in a 'field' section must be plain text." + self.idebug(data))
                                field[key] = field[key].strip()
                                if invalid_variable_name(field[key]):
                                    raise DAError("Missing or invalid variable name " + repr(field[key]) + " for key " + repr(key) + "." + self.idebug(data))
                                field_info['saveas'] = field[key]
                        if 'type' in field_info:
                            if field_info['type'] in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes') and 'nota' not in field_info:
                                field_info['nota'] = True
                            if field_info['type'] == 'object_radio' and 'nota' not in field_info:
                                field_info['nota'] = False
                        if 'choicetype' in field_info and field_info['choicetype'] == 'compute' and 'type' in field_info and field_info['type'] in ('object', 'object_radio', 'object_multiselect', 'object_checkboxes'):
                            if 'choices' not in field:
                                raise DAError("You need to have a choices element if you want to set a variable to an object." + self.idebug(data))
                            if not isinstance(field['choices'], list):
                                select_list = [str(field['choices'])]
                            else:
                                select_list = field['choices']
                            if 'exclude' in field:
                                if isinstance(field['exclude'], dict):
                                    raise DAError("choices exclude list is not in appropriate format" + self.idebug(data))
                                if not isinstance(field['exclude'], list):
                                    exclude_list = [str(field['exclude']).strip()]
                                else:
                                    exclude_list = [x.strip() for x in field['exclude']]
                                if len(exclude_list):
                                    select_list.append('exclude=[' + ", ".join(exclude_list) + ']')
                            if 'default' in field:
                                if not isinstance(field['default'], (list, str)):
                                    raise DAError("default list is not in appropriate format" + self.idebug(data))
                                if not isinstance(field['default'], list):
                                    default_list = [str(field['default'])]
                                else:
                                    default_list = field['default']
                            else:
                                default_list = list()
                            if field_info['type'] in ('object_multiselect', 'object_checkboxes'):
                                default_list.append('_DAOBJECTDEFAULTDA')
                            if len(default_list):
                                select_list.append('default=[' + ", ".join(default_list) + ']')
                            additional_parameters = ''
                            if 'object_labeler' in field_info:
                                additional_parameters += ", object_labeler=_DAOBJECTLABELER"
                            if 'help_generator' in field_info:
                                additional_parameters += ", help_generator=_DAHELPGENERATOR"
                            if 'image_generator' in field_info:
                                additional_parameters += ", image_generator=_DAIMAGEGENERATOR"
                            source_code = "docassemble.base.core.selections(" + ", ".join(select_list) + additional_parameters + ")"
                            #logmessage("source_code is " + source_code)
                            field_info['selections'] = {'compute': compile(source_code, '<expression>', 'eval'), 'sourcecode': source_code}
                        if 'saveas' in field_info:
                            if not isinstance(field_info['saveas'], str):
                                raise DAError("Invalid variable name " + repr(field_info['saveas']) + "." + self.idebug(data))
                            self.fields.append(Field(field_info))
                            if 'type' in field_info:
                                if field_info['type'] in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                                    if self.scan_for_variables:
                                        self.fields_used.add(field_info['saveas'])
                                        self.fields_used.add(field_info['saveas'] + '.gathered')
                                        if field_info['type'] in ('multiselect', 'checkboxes'):
                                            for the_key in manual_keys:
                                                self.fields_used.add(field_info['saveas'] + '[' + repr(the_key) + ']')
                                    else:
                                        self.other_fields_used.add(field_info['saveas'])
                                        self.other_fields_used.add(field_info['saveas'] + '.gathered')
                                        if field_info['type'] in ('multiselect', 'checkboxes'):
                                            for the_key in manual_keys:
                                                self.other_fields_used.add(field_info['saveas'] + '[' + repr(the_key) + ']')
                                elif field_info['type'] == 'ml':
                                    if self.scan_for_variables:
                                        self.fields_used.add(field_info['saveas'])
                                    else:
                                        self.other_fields_used.add(field_info['saveas'])
                                    self.interview.mlfields[field_info['saveas']] = dict(saveas=field_info['saveas'])
                                    if 'extras' in field_info and 'ml_group' in field_info['extras']:
                                        self.interview.mlfields[field_info['saveas']]['ml_group'] = field_info['extras']['ml_group']
                                    if re.search(r'\.text$', field_info['saveas']):
                                        field_info['saveas'] = field_info['saveas'].strip()
                                        if invalid_variable_name(field_info['saveas']):
                                            raise DAError("Missing or invalid variable name " + repr(field_info['saveas']) + "." + self.idebug(data))
                                        field_info['saveas'] = re.sub(r'\.text$', '', field_info['saveas'])
                                        if self.scan_for_variables:
                                            self.fields_used.add(field_info['saveas'])
                                        else:
                                            self.other_fields_used.add(field_info['saveas'])
                                    else:
                                        if self.scan_for_variables:
                                            self.fields_used.add(field_info['saveas'] + '.text')
                                        else:
                                            self.other_fields_used.add(field_info['saveas'] + '.text')
                                else:
                                    if self.scan_for_variables:
                                        self.fields_used.add(field_info['saveas'])
                                    else:
                                        self.other_fields_used.add(field_info['saveas'])
                            else:
                                if self.scan_for_variables:
                                    self.fields_used.add(field_info['saveas'])
                                else:
                                    self.other_fields_used.add(field_info['saveas'])
                        elif 'note' in field or 'html' in field:
                            if 'note' in field:
                                field_info['type'] = 'note'
                            else:
                                field_info['type'] = 'html'
                            self.fields.append(Field(field_info))
                        else:
                            raise DAError("A field was listed without indicating a label or a variable name, and the field was not a note or raw HTML." + self.idebug(data) + " and field_info was " + repr(field_info))
                    else:
                        raise DAError("Each individual field in a list of fields must be expressed as a dictionary item, e.g., ' - Fruit: user.favorite_fruit'." + self.idebug(data))
                    field_number += 1
                if 'current_field' in docassemble.base.functions.this_thread.misc:
                    del docassemble.base.functions.this_thread.misc['current_field']
        if 'review' in data:
            self.question_type = 'review'
            if self.is_mandatory and 'continue button field' not in data:
                raise DAError("A review block without a continue button field cannot be mandatory." + self.idebug(data))
            if isinstance(data['review'], dict):
                data['review'] = [data['review']]
            if not isinstance(data['review'], list):
                raise DAError("The review must be written in the form of a list." + self.idebug(data))
            field_number = 0
            for field in data['review']:
                if not isinstance(field, dict):
                    raise DAError("Each individual field in a list of fields must be expressed as a dictionary item, e.g., ' - Fruit: user.favorite_fruit'." + self.idebug(data))
                field_info = {'number': field_number, 'data': []}
                for key in field:
                    if key == 'action':
                        continue
                    elif key == 'help':
                        if not isinstance(field[key], dict) and not isinstance(field[key], list):
                            field_info[key] = TextObject(definitions + str(field[key]), question=self)
                        if 'button' in field: #or 'css' in field or 'script' in field:
                            raise DAError("In a review block, you cannot mix help text with a button item." + self.idebug(data)) #, css, or script
                    elif key == 'button':
                        if not isinstance(field[key], dict) and not isinstance(field[key], list):
                            field_info['help'] = TextObject(definitions + str(field[key]), question=self)
                            field_info['type'] = 'button'
                    elif key in ('note', 'html'):
                        if 'type' not in field_info:
                            field_info['type'] = key
                        if 'extras' not in field_info:
                            field_info['extras'] = dict()
                        field_info['extras'][key] = TextObject(definitions + str(field[key]), question=self)
                    elif key == 'show if':
                        if not isinstance(field[key], list):
                            field_list = [field[key]]
                        else:
                            field_list = field[key]
                        field_data = []
                        for the_saveas in field_list:
                            #if not isinstance(the_saveas, str):
                            #    raise DAError("Invalid variable name in fields." + self.idebug(data))
                            the_saveas = str(the_saveas).strip()
                            #if invalid_variable_name(the_saveas):
                            #    raise DAError("Missing or invalid variable name " + repr(the_saveas) + " ." + self.idebug(data))
                            if the_saveas not in field_data:
                                field_data.append(the_saveas)
                            self.find_fields_in(the_saveas)
                        if len(field_list):
                            if 'saveas_code' not in field_info:
                                field_info['saveas_code'] = []
                            field_info['saveas_code'].extend([(compile(y, '<expression>', 'eval'), True) for y in field_list])
                    elif key in ('field', 'fields'):
                        if 'label' not in field:
                            raise DAError("If you use 'field' or 'fields' to indicate variables in a 'review' section, you must also include a 'label.'" + self.idebug(data))
                        if not isinstance(field[key], list):
                            field_list = [field[key]]
                        else:
                            field_list = field[key]
                        field_info['data'] = []
                        for the_saveas in field_list:
                            if isinstance(the_saveas, dict) and len(the_saveas) == 1 and ('undefine' in the_saveas or 'recompute' in the_saveas or 'set' in the_saveas or 'follow up' in the_saveas):
                                if 'set' in the_saveas:
                                    if not isinstance(the_saveas['set'], list):
                                        raise DAError("The set statement must refer to a list." + self.idebug(data))
                                    clean_list = []
                                    for the_dict in the_saveas['set']:
                                        if not isinstance(the_dict, dict):
                                            raise DAError("A set command must refer to a list of dicts." + self.idebug(data))
                                        for the_var, the_val in the_dict.items():
                                            if not isinstance(the_var, str):
                                                raise DAError("A set command must refer to a list of dicts with keys as variable names." + self.idebug(data))
                                            the_var_stripped = the_var.strip()
                                        if invalid_variable_name(the_var_stripped):
                                            raise DAError("Missing or invalid variable name " + repr(the_var) + " ." + self.idebug(data))
                                        self.find_fields_in(the_var_stripped)
                                        clean_list.append([the_var_stripped, the_val])
                                    field_info['data'].append(dict(action='_da_set', arguments=dict(variables=clean_list)))
                                if 'follow up' in the_saveas:
                                    if not isinstance(the_saveas['follow up'], list):
                                        raise DAError("The follow up statement must refer to a list." + self.idebug(data))
                                    for var in the_saveas['follow up']:
                                        if not isinstance(var, str):
                                            raise DAError("Invalid variable name in follow up " + command + "." + self.idebug(data))
                                        var_saveas = var.strip()
                                        if invalid_variable_name(var_saveas):
                                            raise DAError("Missing or invalid variable name " + repr(var_saveas) + " ." + self.idebug(data))
                                        self.find_fields_in(var_saveas)
                                        #field_info['data'].append(dict(action="_da_follow_up", arguments=dict(action=var)))
                                        field_info['data'].append(dict(action=var, arguments=dict()))
                                for command in ('undefine', 'invalidate', 'recompute'):
                                    if command not in the_saveas:
                                        continue
                                    if not isinstance(the_saveas[command], list):
                                        raise DAError("The " + command + " statement must refer to a list." + self.idebug(data))
                                    clean_list = []
                                    for undef_var in the_saveas[command]:
                                        if not isinstance(undef_var, str):
                                            raise DAError("Invalid variable name " + repr(undef_var) + " in " + command + "." + self.idebug(data))
                                        undef_saveas = undef_var.strip()
                                        if invalid_variable_name(undef_saveas):
                                            raise DAError("Missing or invalid variable name " + repr(undef_saveas) + " ." + self.idebug(data))
                                        self.find_fields_in(undef_saveas)
                                        clean_list.append(undef_saveas)
                                    if command == 'invalidate':
                                        field_info['data'].append(dict(action='_da_invalidate', arguments=dict(variables=clean_list)))
                                    else:
                                        field_info['data'].append(dict(action='_da_undefine', arguments=dict(variables=clean_list)))
                                    if command == 'recompute':
                                        field_info['data'].append(dict(action='_da_compute', arguments=dict(variables=clean_list)))
                                continue
                            if isinstance(the_saveas, dict) and len(the_saveas) == 2 and 'action' in the_saveas and 'arguments' in the_saveas:
                                if not isinstance(the_saveas['arguments'], dict):
                                    raise DAError("An arguments directive must refer to a dictionary.  " + repr(data))
                                field_info['data'].append(dict(action=the_saveas['action'], arguments=the_saveas['arguments']))
                            if not isinstance(the_saveas, str):
                                raise DAError("Invalid variable name " + repr(the_saveas) + " in fields." + self.idebug(data))
                            the_saveas = the_saveas.strip()
                            if invalid_variable_name(the_saveas):
                                raise DAError("Missing or invalid variable name " + repr(the_saveas) + " ." + self.idebug(data))
                            if the_saveas not in field_info['data']:
                                field_info['data'].append(the_saveas)
                            self.find_fields_in(the_saveas)
                        if 'action' in field:
                            field_info['action'] = dict(action=field['action'], arguments=dict())
                    elif key == 'label':
                        if 'field' not in field and 'fields' not in field:
                            raise DAError("If you use 'label' to label a field in a 'review' section, you must also include a 'field' or 'fields.'" + self.idebug(data))
                        field_info['label'] = TextObject(definitions + interpret_label(field[key]), question=self)
                    else:
                        field_info['label'] = TextObject(definitions + interpret_label(key), question=self)
                        if not isinstance(field[key], list):
                            field_list = [field[key]]
                        else:
                            field_list = field[key]
                        field_info['data'] = []
                        for the_saveas in field_list:
                            if isinstance(the_saveas, dict) and len(the_saveas) == 1 and ('undefine' in the_saveas or 'recompute' in the_saveas):
                                if 'set' in the_saveas:
                                    if not isinstance(the_saveas['set'], list):
                                        raise DAError("The set statement must refer to a list." + self.idebug(data))
                                    clean_list = []
                                    for the_dict in the_saveas['set']:
                                        if not isinstance(the_dict, dict):
                                            raise DAError("A set command must refer to a list of dicts." + self.idebug(data))
                                        for the_var, the_val in the_dict.items():
                                            if not isinstance(the_var, str):
                                                raise DAError("A set command must refer to a list of dicts with keys as variable names." + self.idebug(data))
                                            the_var_stripped = the_var.strip()
                                        if invalid_variable_name(the_var_stripped):
                                            raise DAError("Missing or invalid variable name " + repr(the_var) + " ." + self.idebug(data))
                                        self.find_fields_in(the_var_stripped)
                                        clean_list.append([the_var_stripped, the_val])
                                    field_info['data'].append(dict(action='_da_set', arguments=dict(variables=clean_list)))
                                for command in ('undefine', 'recompute'):
                                    if command not in the_saveas:
                                        continue
                                    if not isinstance(the_saveas[command], list):
                                        raise DAError("The " + command + " statement must refer to a list." + self.idebug(data))
                                    clean_list = []
                                    for undef_var in the_saveas[command]:
                                        if not isinstance(undef_var, str):
                                            raise DAError("Invalid variable name " + repr(undef_var) + " in fields " + command + "." + self.idebug(data))
                                        undef_saveas = undef_var.strip()
                                        if invalid_variable_name(undef_saveas):
                                            raise DAError("Missing or invalid variable name " + repr(undef_saveas) + " ." + self.idebug(data))
                                        self.find_fields_in(undef_saveas)
                                        clean_list.append(undef_saveas)
                                    if command == 'invalidate':
                                        field_info['data'].append(dict(action='_da_invalidate', arguments=dict(variables=clean_list)))
                                    else:
                                        field_info['data'].append(dict(action='_da_undefine', arguments=dict(variables=clean_list)))
                                    if command == 'recompute':
                                        field_info['data'].append(dict(action='_da_compute', arguments=dict(variables=clean_list)))
                                continue
                            if not isinstance(the_saveas, str):
                                raise DAError("Invalid variable name " + repr(the_saveas) + " in fields." + self.idebug(data))
                            the_saveas = the_saveas.strip()
                            if invalid_variable_name(the_saveas):
                                raise DAError("Missing or invalid variable name " + repr(the_saveas) + " ." + self.idebug(data))
                            #if the_saveas not in field_info['data']:
                            field_info['data'].append(the_saveas)
                            self.find_fields_in(the_saveas)
                        if 'action' in field:
                            field_info['action'] = dict(action=field['action'], arguments=dict())
                    if 'type' in field_info and field_info['type'] in ('note', 'html') and 'label' in field_info:
                        del field_info['type']
                if len(field_info['data']):
                    if 'saveas_code' not in field_info:
                        field_info['saveas_code'] = []
                    field_info['saveas_code'].extend([(compile(y, '<expression>', 'eval'), False) for y in field_info['data'] if isinstance(y, str)])
                    if 'action' not in field_info:
                        if len(field_info['data']) == 1 and isinstance(field_info['data'][0], str):
                            field_info['action'] = dict(action=field_info['data'][0], arguments=dict())
                        else:
                            field_info['action'] = dict(action="_da_force_ask", arguments=dict(variables=field_info['data']))
                if len(field_info['data']) or ('type' in field_info and field_info['type'] in ('note', 'html')):
                    self.fields.append(Field(field_info))
                else:
                    raise DAError("A field in a review list was listed without indicating a label or a variable name, and the field was not a note or raw HTML." + self.idebug(field_info))
                field_number += 1
        if not hasattr(self, 'question_type'):
            if len(self.attachments) and len(self.fields_used) and not hasattr(self, 'content'):
                self.question_type = 'attachments'
            elif hasattr(self, 'content'):
                self.question_type = 'deadend'
        if should_append:
            if not hasattr(self, 'question_type'):
                raise DAError("No question type could be determined for this section." + self.idebug(data))
            if main_list:
                self.interview.questions_list.append(self)
            self.number = self.interview.next_number()
            #self.number = len(self.interview.questions_list) - 1
            if hasattr(self, 'id'):
                self.name = "ID " + self.id
                # if self.name in self.interview.questions_by_name:
                #     raise DAError("Question ID " + str(self.id) + " results in duplicate question name")
            else:
                self.name = "Question_" + str(self.number)
        else:
            self.number = self.interview.next_block_number()
            if self.name is None:
                self.name = "Block_" + str(self.number)
        self.interview.all_questions.append(self)
        # if hasattr(self, 'id'):
        #     try:
        #         self.interview.questions_by_id[self.id].append(self)
        #     except:
        #         self.interview.questions_by_id[self.id] = [self]
        if self.name is not None:
            self.interview.questions_by_name[self.name] = self
        foundmatch = False
        for field_name in self.fields_used:
            if re.search(r'\[', field_name):
                foundmatch = True
                break
        while foundmatch:
            foundmatch = False
            vars_to_add = set()
            for field_name in self.fields_used:
                for m in re.finditer(r'^(.*?)\[\'([^\'\"]*)\'\](.*)', field_name):
                    new_var = m.group(1) + "['" + m.group(2) + "']" + m.group(3)
                    if new_var not in self.fields_used:
                        foundmatch = True
                        #logmessage("Adding " + new_var)
                        vars_to_add.add(new_var)
                    # new_var = m.group(1) + '["' + m.group(2) + '"]' + m.group(3)
                    # if new_var not in self.fields_used:
                    #     foundmatch = True
                    #     logmessage("Adding " + new_var)
                    #     vars_to_add.add(new_var)
                for m in re.finditer(r'^(.*?)\[\"([^\"\']*)\"\](.*)', field_name):
                    new_var = m.group(1) + "['" + m.group(2) + "']" + m.group(3)
                    if new_var not in self.fields_used:
                        foundmatch = True
                        #logmessage("Adding " + new_var)
                        vars_to_add.add(new_var)
                    new_var = m.group(1) + "['" + m.group(2) + "']" + m.group(3)
                    if new_var not in self.fields_used:
                        foundmatch = True
                        #logmessage("Adding " + new_var)
                        vars_to_add.add(new_var)
                for m in re.finditer(r'^(.*?)\[u\'([^\'\"]*)\'\](.*)', field_name):
                    new_var = m.group(1) + "['" + m.group(2) + "']" + m.group(3)
                    if new_var not in self.fields_used:
                        foundmatch = True
                        #logmessage("Adding " + new_var)
                        vars_to_add.add(new_var)
                    # new_var = m.group(1) + '["' + m.group(2) + '"]' + m.group(3)
                    # if new_var not in self.fields_used:
                    #     foundmatch = True
                    #     logmessage("Adding " + new_var)
                    #     vars_to_add.add(new_var)
            for new_var in vars_to_add:
                #logmessage("Really adding " + new_var)
                self.fields_used.add(new_var)
        for field_name in self.fields_used:
            if field_name not in self.interview.questions:
                self.interview.questions[field_name] = dict()
            if self.language not in self.interview.questions[field_name]:
                self.interview.questions[field_name][self.language] = list()
            self.interview.questions[field_name][self.language].append(register_target)
            if self.is_generic:
                if self.generic_object not in self.interview.generic_questions:
                    self.interview.generic_questions[self.generic_object] = dict()
                if field_name not in self.interview.generic_questions[self.generic_object]:
                    self.interview.generic_questions[self.generic_object][field_name] = dict()
                if self.language not in self.interview.generic_questions[self.generic_object][field_name]:
                    self.interview.generic_questions[self.generic_object][field_name][self.language] = list()
                self.interview.generic_questions[self.generic_object][field_name][self.language].append(register_target)
            for variable in depends_list:
                if variable not in self.interview.invalidation:
                    self.interview.invalidation[variable] = set()
                self.interview.invalidation[variable].add(field_name)
        if len(self.attachments):
            indexno = 0
            for att in self.attachments:
                att['question_name'] = self.name
                att['indexno'] = indexno
                indexno += 1
        self.data_for_debug = data
    def get_old_values(self, user_dict):
        old_values = dict()
        for field_name in self.fields_for_invalidation:
            try:
                old_values[field_name] = eval(field_name, user_dict)
            except Exception as err:
                if field_name in user_dict['_internal']['dirty']:
                    old_values[field_name] = user_dict['_internal']['dirty'][field_name]
        return old_values
    def invalidate_dependencies_of_variable(self, the_user_dict, field_name, old_value):
        if field_name in self.interview.invalidation_todo or field_name in self.interview.onchange_todo:
            self.interview.invalidate_dependencies(field_name, the_user_dict, { field_name: old_value })
        try:
            del the_user_dict['_internal']['dirty'][field_name]
        except:
            pass
    def invalidate_dependencies(self, the_user_dict, old_values):
        for field_name in self.fields_used.union(self.other_fields_used):
            if field_name in self.interview.invalidation_todo or field_name in self.interview.onchange_todo:
                self.interview.invalidate_dependencies(field_name, the_user_dict, old_values)
            try:
                del the_user_dict['_internal']['dirty'][field_name]
            except:
                pass
    def post_exec(self, the_user_dict):
        if self.need_post is not None:
            for need_code in self.need_post:
                eval(need_code, the_user_dict)
    def exec_setup(self, is_generic, the_x, iterators, the_user_dict):
        if is_generic:
            if the_x != 'None':
                exec("x = " + the_x, the_user_dict)
        if len(iterators):
            for indexno in range(len(iterators)):
                exec(list_of_indices[indexno] + " = " + iterators[indexno], the_user_dict)
        for the_field in self.undefine:
            docassemble.base.functions.undefine(the_field)
        if len(self.reconsider) > 0:
            docassemble.base.functions.reconsider(*[substitute_vars(item, is_generic, the_x, iterators) for item in self.reconsider])
        if self.need is not None:
            for need_code in self.need:
                eval(need_code, the_user_dict)
    def recursive_data_from_code(self, target):
        if isinstance(target, dict) or (hasattr(target, 'elements') and isinstance(target.elements, dict)):
            new_dict = dict()
            for key, val in target.items():
                new_dict[key] = self.recursive_data_from_code(val)
            return new_dict
        if isinstance(target, list) or (hasattr(target, 'elements') and isinstance(target.elements, list)):
            new_list = list()
            for val in target.__iter__():
                new_list.append(self.recursive_data_from_code(val))
            return new_list
        if isinstance(target, set) or (hasattr(target, 'elements') and isinstance(target.elements, set)):
            new_set = set()
            for val in target.__iter__():
                new_set.add(self.recursive_data_from_code(val))
            return new_set
        if isinstance(target, (bool, float, int, NoneType)):
            return target
        self.find_fields_in(target)
        return compile(target, '<expression>', 'eval')
    def recursive_dataobject(self, target):
        if isinstance(target, dict) or (hasattr(target, 'elements') and isinstance(target.elements, dict)):
            new_dict = dict()
            for key, val in target.items():
                new_dict[key] = self.recursive_dataobject(val)
            return new_dict
        if isinstance(target, list) or (hasattr(target, 'elements') and isinstance(target.elements, list)):
            new_list = list()
            for val in target.__iter__():
                new_list.append(self.recursive_dataobject(val))
            return new_list
        if isinstance(target, set) or (hasattr(target, 'elements') and isinstance(target.elements, set)):
            new_set = set()
            for val in target.__iter__():
                new_set.add(self.recursive_dataobject(val, self.mako_names))
            return new_set
        if isinstance(target, (bool, float, int, NoneType)):
            return target
        return TextObject(str(target), question=self)

    def find_fields_in(self, code):
        myvisitor = myvisitnode()
        t = ast.parse(str(code))
        myvisitor.visit(t)
        predefines = set(globals().keys()) | set(locals().keys())
        if self.scan_for_variables:
            for item in myvisitor.targets.keys():
                if item not in predefines:
                    self.fields_used.add(item)
        else:
            for item in myvisitor.targets.keys():
                if item not in predefines:
                    self.other_fields_used.add(item)
        definables = set(predefines) | set(myvisitor.targets.keys())
        for item in myvisitor.names.keys():
            if item not in definables:
                self.names_used.add(item)
    def yes(self):
        return word("Yes")
    def no(self):
        return word("No")
    def maybe(self):
        return word("I don't know")
    def back(self):
        return word("Back")
    def cornerback(self):
        return word("Back")
    def help(self):
        return word("Help")
    def process_attachment_code(self, sourcecode):
        if not isinstance(sourcecode, str):
            raise DAError("An attachment code specifier must be plain text")
        try:
            self.compute_attachment = compile(sourcecode, '<expression>', 'eval')
            self.find_fields_in(sourcecode)
            self.sourcecode = sourcecode
        except:
            logmessage("Question: compile error in code:\n" + str(sourcecode) + "\n" + str(sys.exc_info()[0]))
            raise
    def process_attachment_list(self, target):
        if isinstance(target, list):
            att_list = list(map((lambda x: self.process_attachment(x)), target))
            return att_list
        else:
            return([self.process_attachment(target)])
    def process_attachment(self, orig_target):
        metadata = dict()
        variable_name = str()
        defs = list()
        options = dict()
        if isinstance(orig_target, dict):
            target = dict()
            for key, value in orig_target.items():
                target[key.lower()] = value
            if 'language' in target:
                options['language'] = target['language']
            if 'name' not in target:
                target['name'] = word("Document")
            if 'filename' not in target:
                #target['filename'] = docassemble.base.functions.space_to_underscore(target['name'])
                target['filename'] = ''
            if 'description' not in target:
                target['description'] = ''
            if 'redact' in target:
                if isinstance(target['redact'], bool) or isinstance(target['redact'], NoneType):
                    options['redact'] = target['redact']
                else:
                    options['redact'] = compile(target['redact'], '<expression>', 'eval')
                    self.find_fields_in(target['redact'])
            if 'checkbox export value' in target and 'pdf template file' in target:
                if not isinstance(target['checkbox export value'], str):
                    raise DAError("A checkbox export value must be a string." + self.idebug(target))
                options['checkbox_export_value'] = TextObject(target['checkbox export value'])
            if 'decimal places' in target and 'pdf template file' in target:
                if not isinstance(target['decimal places'], (str, int)):
                    raise DAError("A decimal places directive must be an integer or string." + self.idebug(target))
                options['decimal_places'] = TextObject(str(target['decimal places']))
            if 'initial yaml' in target:
                if not isinstance(target['initial yaml'], list):
                    target['initial yaml'] = [target['initial yaml']]
                options['initial_yaml'] = list()
                for yaml_file in target['initial yaml']:
                    if not isinstance(yaml_file, str):
                        raise DAError('An initial yaml file must be a string.' + self.idebug(target))
                    options['initial_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
            if 'additional yaml' in target:
                if not isinstance(target['additional yaml'], list):
                    target['additional yaml'] = [target['additional yaml']]
                options['additional_yaml'] = list()
                for yaml_file in target['additional yaml']:
                    if not isinstance(yaml_file, str):
                        raise DAError('An additional yaml file must be a string.' + self.idebug(target))
                    options['additional_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
            if 'template file' in target:
                if not isinstance(target['template file'], str):
                    raise DAError('The template file must be a string.' + self.idebug(target))
                options['template_file'] = FileInPackage(target['template file'], 'template', self.package)
            if 'rtf template file' in target:
                if not isinstance(target['rtf template file'], str):
                    raise DAError('The rtf template file must be a string.' + self.idebug(target))
                options['rtf_template_file'] = FileInPackage(target['rtf template file'], 'template', self.package)
            if 'docx reference file' in target:
                if not isinstance(target['docx reference file'], str):
                    raise DAError('The docx reference file must be a string.' + self.idebug(target))
                options['docx_reference_file'] = FileInPackage(target['docx reference file'], 'template', self.package)
            if 'usedefs' in target:
                if isinstance(target['usedefs'], str):
                    the_list = [target['usedefs']]
                elif isinstance(target['usedefs'], list):
                    the_list = target['usedefs']
                else:
                    raise DAError('The usedefs included in an attachment must be specified as a list of strings or a single string.' + self.idebug(target))
                for def_key in the_list:
                    if not isinstance(def_key, str):
                        raise DAError('The defs in an attachment must be strings.' + self.idebug(target))
                    if def_key not in self.interview.defs:
                        raise DAError('Referred to a non-existent def "' + def_key + '."  All defs must be defined before they are used.' + self.idebug(target))
                    defs.extend(self.interview.defs[def_key])
            if 'variable name' in target:
                variable_name = target['variable name']
                if variable_name is None:
                    raise DAError('A variable name cannot be None.' + self.idebug(target))
                if self.scan_for_variables:
                    self.fields_used.add(target['variable name'])
                else:
                    self.other_fields_used.add(target['variable name'])
            else:
                variable_name = "_internal['docvar'][" + str(self.interview.next_attachment_number()) + "]"
            if 'metadata' in target:
                if not isinstance(target['metadata'], dict):
                    raise DAError('Unknown data type ' + str(type(target['metadata'])) + ' in attachment metadata.' + self.idebug(target))
                for key in target['metadata']:
                    data = target['metadata'][key]
                    if data is list:
                        for sub_data in data:
                            if sub_data is not str:
                                raise DAError('Unknown data type ' + str(type(sub_data)) + ' in list in attachment metadata' + self.idebug(target))
                        newdata = list(map((lambda x: TextObject(x, question=self)), data))
                        metadata[key] = newdata
                    elif isinstance(data, str):
                        metadata[key] = TextObject(data, question=self)
                    elif isinstance(data, bool):
                        metadata[key] = data
                    else:
                        raise DAError('Unknown data type ' + str(type(data)) + ' in key in attachment metadata' + self.idebug(target))
            if 'raw' in target and target['raw']:
                if 'content file' in target:
                    content_file = target['content file']
                    if isinstance(content_file, dict):
                        target['valid formats'] = ['raw']
                        target['raw'] = '.txt'
                    else:
                        if not isinstance(content_file, list):
                            content_file = [content_file]
                        the_ext = None
                        for item in content_file:
                            (the_base, the_ext) = os.path.splitext(item)
                        if the_ext:
                            target['raw'] = the_ext
                            target['valid formats'] = ['raw']
                        else:
                            target['raw'] = False
                else:
                    target['raw'] = False
            else:
                target['raw'] = False
            if 'content file' in target:
                if isinstance(target['content file'], dict):
                    if len(target['content file']) == 1 and 'code' in target['content file'] and isinstance(target['content file']['code'], str):
                        options['content file code'] = compile(target['content file']['code'], '<content file code>', 'eval')
                        self.find_fields_in(target['content file']['code'])
                    else:
                        raise DAError('A content file must be specified as text, a list of text filenames, or a dictionary where the one key is code' + self.idebug(target))
                else:
                    if not isinstance(target['content file'], list):
                        target['content file'] = [target['content file']]
                    target['content'] = ''
                    for content_file in target['content file']:
                        if not isinstance(content_file, str):
                            raise DAError('A content file must be specified as text, a list of text filenames, or a dictionary where the one key is code' + self.idebug(target))
                        file_to_read = docassemble.base.functions.package_template_filename(content_file, package=self.package)
                        if file_to_read is not None and os.path.isfile(file_to_read) and os.access(file_to_read, os.R_OK):
                            with open(file_to_read, 'r', encoding='utf-8') as the_file:
                                target['content'] += the_file.read()
                        else:
                            raise DAError('Unable to read content file ' + str(content_file) + ' after trying to find it at ' + str(file_to_read) + self.idebug(target))
            if 'pdf template file' in target and ('code' in target or 'field variables' in target or 'field code' in target or 'raw field variables' in target) and 'fields' not in target:
                target['fields'] = dict()
                field_mode = 'manual'
            elif 'docx template file' in target:
                if 'update references' in target:
                    if isinstance(target['update references'], bool):
                        options['update_references'] = target['update references']
                    elif isinstance(target['update references'], str):
                        options['update_references'] = compile(target['update references'], '<expression>', 'eval')
                        self.find_fields_in(target['update references'])
                    else:
                        raise DAError('Unknown data type in attachment "update references".' + self.idebug(target))
                if 'fields' in target:
                    field_mode = 'manual'
                else:
                    target['fields'] = dict()
                    if 'code' in target or 'field variables' in target or 'field code' in target or 'raw field variables' in target:
                        field_mode = 'manual'
                    else:
                        field_mode = 'auto'
            else:
                field_mode = 'manual'
            if 'fields' in target:
                if 'pdf template file' not in target and 'docx template file' not in target:
                    raise DAError('Fields supplied to attachment but no pdf template file or docx template file supplied' + self.idebug(target))
                if 'pdf template file' in target and 'docx template file' in target:
                    raise DAError('You cannot use a pdf template file and a docx template file at the same time' + self.idebug(target))
                if 'pdf template file' in target:
                    template_type = 'pdf'
                    target['valid formats'] = ['pdf']
                    if 'editable' in target:
                        options['editable'] = compile(str(target['editable']), '<editable expression>', 'eval')
                elif 'docx template file' in target:
                    template_type = 'docx'
                    if 'valid formats' in target:
                        if isinstance(target['valid formats'], str):
                            target['valid formats'] = [target['valid formats']]
                        elif not isinstance(target['valid formats'], list):
                            raise DAError('Unknown data type in attachment valid formats.' + self.idebug(target))
                        if 'rtf to docx' in target['valid formats']:
                            raise DAError('Valid formats cannot include "rtf to docx" when "docx template file" is used' + self.idebug(target))
                    else:
                        target['valid formats'] = ['docx', 'pdf']
                if template_type == 'docx':
                    if not isinstance(target['docx template file'], (str, dict, list)):
                        raise DAError(template_type + ' template file supplied to attachment must be a string, dict, or list' + self.idebug(target))
                    if not isinstance(target['docx template file'], list):
                        target[template_type + ' template file'] = [target['docx template file']]
                else:
                    if not isinstance(target[template_type + ' template file'], (str, dict)):
                        raise DAError(template_type + ' template file supplied to attachment must be a string or dict' + self.idebug(target))
                if field_mode == 'auto':
                    options['fields'] = 'auto'
                elif not isinstance(target['fields'], (list, dict)):
                    raise DAError('fields supplied to attachment must be a list or dictionary' + self.idebug(target))
                target['content'] = ''
                if template_type == 'docx':
                    options[template_type + '_template_file'] = [FileInPackage(item, 'template', package=self.package) for item in target['docx template file']]
                    for item in target['docx template file']:
                        if not isinstance(item, (str, dict)):
                            raise DAError('docx template file supplied to attachment must be a string or dict' + self.idebug(target))
                    template_files = []
                    for template_file in options['docx_template_file']:
                        if not template_file.is_code:
                            the_docx_path = template_file.path()
                            if not os.path.isfile(the_docx_path):
                                raise DAError("Missing docx template file " + os.path.basename(the_docx_path))
                            template_files.append(the_docx_path)
                    if len(template_files):
                        if len(template_files) == 1:
                            the_docx_path = template_files[0]
                        else:
                            the_docx_path = docassemble.base.file_docx.concatenate_files(template_files)
                        try:
                            docx_template = docassemble.base.file_docx.DocxTemplate(the_docx_path)
                            the_env = custom_jinja_env()
                            the_xml = docx_template.get_xml()
                            the_xml = re.sub(r'<w:p>', '\n<w:p>', the_xml)
                            the_xml = re.sub(r'({[\%\{].*?[\%\}]})', fix_quotes, the_xml)
                            the_xml = docx_template.patch_xml(the_xml)
                            parsed_content = the_env.parse(the_xml)
                        except TemplateError as the_error:
                            if the_error.filename is None:
                                try:
                                    the_error.filename = os.path.basename(options['docx_template_file'].path())
                                except:
                                    pass
                            if hasattr(the_error, 'lineno') and the_error.lineno is not None:
                                line_number = max(the_error.lineno - 4, 0)
                                the_error.docx_context = map(lambda x: re.sub(r'<[^>]+>', '', x), the_xml.splitlines()[line_number:(line_number + 7)])
                            raise the_error
                        for key in jinja2meta.find_undeclared_variables(parsed_content):
                            if not key.startswith('_'):
                                self.mako_names.add(key)
                    for key in ('field code', 'fields'):
                        if key in target:
                            if isinstance(target[key], list):
                                for item in target[key]:
                                    for field_name in item.keys():
                                        try:
                                            self.names_used.remove(field_name)
                                        except:
                                            pass
                                        try:
                                            self.mako_names.remove(field_name)
                                        except:
                                            pass
                            elif isinstance(target[key], dict):
                                for field_name in target[key].keys():
                                    try:
                                        self.names_used.remove(field_name)
                                    except:
                                        pass
                                    try:
                                        self.mako_names.remove(field_name)
                                    except:
                                        pass
                else:
                    options[template_type + '_template_file'] = FileInPackage(target[template_type + ' template file'], 'template', package=self.package)
                if field_mode == 'manual':
                    options['fields'] = recursive_textobject(target['fields'], self)
                    if 'code' in target:
                        if isinstance(target['code'], str):
                            options['code'] = compile(target['code'], '<expression>', 'eval')
                            self.find_fields_in(target['code'])
                    if 'field variables' in target:
                        if not isinstance(target['field variables'], list):
                            raise DAError('The field variables must be expressed in the form of a list' + self.idebug(target))
                        if 'code dict' not in options:
                            options['code dict'] = dict()
                        for varname in target['field variables']:
                            if not valid_variable_match.match(str(varname)):
                                raise DAError('The variable ' + str(varname) + " cannot be used in a code list" + self.idebug(target))
                            options['code dict'][varname] = compile(varname, '<expression>', 'eval')
                            self.find_fields_in(varname)
                    if 'raw field variables' in target:
                        if not isinstance(target['raw field variables'], list):
                            raise DAError('The raw field variables must be expressed in the form of a list' + self.idebug(target))
                        if 'raw code dict' not in options:
                            options['raw code dict'] = dict()
                        for varname in target['raw field variables']:
                            if not valid_variable_match.match(str(varname)):
                                raise DAError('The variable ' + str(varname) + " cannot be used in a code list" + self.idebug(target))
                            options['raw code dict'][varname] = compile(varname, '<expression>', 'eval')
                            self.find_fields_in(varname)
                    if 'field code' in target:
                        if 'code dict' not in options:
                            options['code dict'] = dict()
                        if not isinstance(target['field code'], list):
                            target['field code'] = [target['field code']]
                        for item in target['field code']:
                            if not isinstance(item, dict):
                                raise DAError('The field code must be expressed in the form of a dictionary' + self.idebug(target))
                            for key, val in item.items():
                                options['code dict'][key] = compile(str(val), '<expression>', 'eval')
                                self.find_fields_in(val)
            if 'valid formats' in target:
                if isinstance(target['valid formats'], str):
                    target['valid formats'] = [target['valid formats']]
                elif not isinstance(target['valid formats'], list):
                    raise DAError('Unknown data type in attachment valid formats.' + self.idebug(target))
                if 'rtf to docx' in target['valid formats'] and 'docx' in target['valid formats']:
                    raise DAError('Valid formats cannot include both "rtf to docx" and "docx."' + self.idebug(target))
            else:
                target['valid formats'] = ['*']
            if 'password' in target:
                options['password'] = TextObject(target['password'])
            if 'template password' in target:
                options['template_password'] = TextObject(target['template password'])
            if 'persistent' in target:
                if isinstance(target['persistent'], bool):
                    options['persistent'] = target['persistent']
                elif isinstance(target['persistent'], str):
                    options['persistent'] = compile(target['persistent'], '<persistent expression>', 'eval')
                    self.find_fields_in(target['persistent'])
                else:
                    raise DAError('Unknown data type in attachment persistent.' + self.idebug(target))
            if 'private' in target:
                if isinstance(target['private'], bool):
                    options['private'] = target['private']
                elif isinstance(target['private'], str):
                    options['private'] = compile(target['private'], '<public expression>', 'eval')
                    self.find_fields_in(target['private'])
                else:
                    raise DAError('Unknown data type in attachment public.' + self.idebug(target))
            if 'allow privileges' in target:
                if isinstance(target['allow privileges'], dict) and len(target['allow privileges']) == 1 and 'code' in target['allow privileges'] and isinstance(target['allow privileges']['code'], str):
                    options['allow privileges'] = compile(target['allow privileges']['code'], '<allow privileges expression>', 'eval')
                elif isinstance(target['allow privileges'], str):
                    options['allow privileges'] = [target['allow privileges']]
                elif isinstance(target['allow privileges'], list):
                    for item in target['allow privileges']:
                        if not isinstance(item, str):
                            raise DAError('Unknown data type in attachment allow privileges.' + self.idebug(target))
                    options['allow privileges'] = target['allow privileges']
            if 'allow users' in target:
                if isinstance(target['allow users'], dict) and len(target['allow users']) == 1 and 'code' in target['allow users'] and isinstance(target['allow users']['code'], str):
                    options['allow users'] = compile(target['allow users']['code'], '<allow users expression>', 'eval')
                elif isinstance(target['allow users'], (str, int)):
                    options['allow users'] = [target['allow users']]
                elif isinstance(target['allow users'], list):
                    for item in target['allow users']:
                        if not isinstance(item, (str, int)):
                            raise DAError('Unknown data type in attachment allow users.' + self.idebug(target))
                    options['allow users'] = target['allow users']
            if 'hyperlink style' in target:
                if isinstance(target['hyperlink style'], str):
                    options['hyperlink_style'] = TextObject(target['hyperlink style'].strip(), question=self)
                else:
                    raise DAError('Unknown data type in attachment hyperlink style.' + self.idebug(target))
            if 'pdf/a' in target:
                if isinstance(target['pdf/a'], bool):
                    options['pdf_a'] = target['pdf/a']
                elif isinstance(target['pdf/a'], str):
                    options['pdf_a'] = compile(target['pdf/a'], '<pdfa expression>', 'eval')
                    self.find_fields_in(target['pdf/a'])
                else:
                    raise DAError('Unknown data type in attachment pdf/a.' + self.idebug(target))
            if 'skip undefined' in target:
                if isinstance(target['skip undefined'], bool):
                    options['skip_undefined'] = target['skip undefined']
                elif isinstance(target['skip undefined'], str):
                    options['skip_undefined'] = compile(target['skip undefined'], '<skip undefined expression>', 'eval')
                    self.find_fields_in(target['skip undefined'])
                else:
                    raise DAError('Unknown data type in attachment skip undefined.' + self.idebug(target))
            else:
                options['skip_undefined'] = False;
            if 'tagged pdf' in target:
                if isinstance(target['tagged pdf'], bool):
                    options['tagged_pdf'] = target['tagged pdf']
                elif isinstance(target['tagged pdf'], str):
                    options['tagged_pdf'] = compile(target['tagged pdf'], '<tagged pdf expression>', 'eval')
                    self.find_fields_in(target['tagged pdf'])
                else:
                    raise DAError('Unknown data type in attachment tagged pdf.' + self.idebug(target))
            if 'content' not in target:
                if 'content file code' in options:
                    return({'name': TextObject(target['name'], question=self), 'filename': TextObject(target['filename'], question=self), 'description': TextObject(target['description'], question=self), 'content': None, 'valid_formats': target['valid formats'], 'metadata': metadata, 'variable_name': variable_name, 'orig_variable_name': variable_name, 'options': options, 'raw': target['raw']})
                raise DAError("No content provided in attachment")
            #logmessage("The content is " + str(target['content']))
            return({'name': TextObject(target['name'], question=self), 'filename': TextObject(target['filename'], question=self), 'description': TextObject(target['description'], question=self), 'content': TextObject("\n".join(defs) + "\n" + target['content'], question=self), 'valid_formats': target['valid formats'], 'metadata': metadata, 'variable_name': variable_name, 'orig_variable_name': variable_name, 'options': options, 'raw': target['raw']})
        elif isinstance(orig_target, str):
            return({'name': TextObject('Document'), 'filename': TextObject('Document'), 'description': TextObject(''), 'content': TextObject(orig_target, question=self), 'valid_formats': ['*'], 'metadata': metadata, 'variable_name': variable_name, 'orig_variable_name': variable_name, 'options': options, 'raw': False})
        else:
            raise DAError("Unknown data type in attachment")
    def get_question_for_field_with_sub_fields(self, field, user_dict):
        field_list = eval(field.extras['fields_code'], user_dict)
        if not isinstance(field_list, list):
            raise DAError("A code directive that defines items in fields must return a list")
        new_interview_source = InterviewSourceString(content='')
        new_interview = new_interview_source.get_interview()
        reproduce_basics(self.interview, new_interview)
        return Question(dict(question='n/a', fields=field_list), new_interview, source=new_interview_source, package=self.package)
    def get_fields_and_sub_fields(self, user_dict):
        all_fields = list()
        for field in self.fields:
            if hasattr(field, 'extras') and 'fields_code' in field.extras:
                the_question = self.get_question_for_field_with_sub_fields(field, user_dict)
                for sub_field in the_question.fields:
                    all_fields.append(sub_field)
            else:
                all_fields.append(field)
        return all_fields
    def ask(self, user_dict, old_user_dict, the_x, iterators, sought, orig_sought, process_list_collect=True, test_for_objects=True):
        #logmessage("ask: orig_sought is " + str(orig_sought) + " and q is " + self.name)
        docassemble.base.functions.this_thread.current_question = self
        if the_x != 'None':
            exec("x = " + the_x, user_dict)
        if len(iterators):
            for indexno in range(len(iterators)):
                #logmessage("Running " + list_of_indices[indexno] + " = " + iterators[indexno])
                exec(list_of_indices[indexno] + " = " + iterators[indexno], user_dict)
        if self.need is not None:
            for need_code in self.need:
                eval(need_code, user_dict)
        for the_field in self.undefine:
            docassemble.base.functions.undefine(the_field)
        if len(self.reconsider) > 0:
            docassemble.base.functions.reconsider(*self.reconsider)
        question_text = self.content.text(user_dict)
        #logmessage("Asking " + str(question_text))
        #sys.stderr.write("Asking " + str(question_text) + "\n")
        if self.subcontent is not None:
            subquestion = self.subcontent.text(user_dict)
        else:
            subquestion = None
        the_default_titles = dict()
        if self.language in self.interview.default_title:
            the_default_titles.update(self.interview.default_title[self.language])
        for key, val in self.interview.default_title['*'].items():
            if key not in the_default_titles:
                the_default_titles[key] = val
        extras = dict()
        if len(self.action_buttons) > 0:
            extras['action_buttons'] = list()
            for item in self.action_buttons:
                if isinstance(item, dict):
                    label = item['label'].text(user_dict).strip()
                    given_arguments = item.get('arguments', dict())
                    arguments = dict()
                    forget_prior = item.get('forget_prior', False)
                    for key, val in given_arguments.items():
                        if isinstance(val, TextObject):
                            arguments[key] = val.text(user_dict).strip()
                        else:
                            arguments[key] = val
                    action = item['action'].text(user_dict).strip()
                    if not (re.search(r'^https?://', action) or action.startswith('javascript:') or action.startswith('/') or action.startswith('?')):
                        if forget_prior:
                            arguments = {'_action': action, '_arguments': arguments}
                            action = '_da_priority_action'
                        action = docassemble.base.functions.url_action(action, **arguments)
                    color = item['color'].text(user_dict).strip()
                    if item['target'] is not None:
                        target = item['target'].text(user_dict).strip()
                    else:
                        target = None
                    if item['icon'] is not None:
                        icon = item['icon'].text(user_dict).strip()
                    else:
                        icon = None
                    if item['placement'] is not None:
                        placement = item['placement'].text(user_dict).strip()
                    else:
                        placement = None
                    extras['action_buttons'].append(dict(action=action, label=label, color=color, icon=icon, placement=placement, forget_prior=forget_prior, target=target))
                else:
                    action_buttons = eval(item, user_dict)
                    if hasattr(action_buttons, 'instanceName') and hasattr(action_buttons, 'elements'):
                        action_buttons = action_buttons.elements
                    if not isinstance(action_buttons, list):
                        raise DAError("action buttons code did not evaluate to a list")
                    for button in action_buttons:
                        if not (isinstance(button, dict) and 'label' in button and 'action' in button and isinstance(button['label'], str) and isinstance(button['action'], str)):
                            raise DAError("action buttons code did not evaluate to a list of dictionaries with label and action items")
                        if 'new window' in button and not isinstance(button['new window'], (str, bool, NoneType)):
                            raise DAError("action buttons code included a new window item that was not boolean, text, or None")
                        if 'color' in button and not isinstance(button['color'], (str, NoneType)):
                            raise DAError("action buttons code included a color item that was not text or None")
                        if 'icon' in button and not isinstance(button['icon'], (str, NoneType)):
                            raise DAError("action buttons code included an icon item that was not text or None")
                        color = button.get('color', 'primary')
                        if color is None:
                            color = 'primary'
                        icon = button.get('icon', None)
                        placement = button.get('placement', None)
                        target = button.get('new window', None)
                        if target is True:
                            target = '_blank'
                        elif target is False:
                            target = None
                        arguments = button.get('arguments', dict())
                        forget_prior = button.get('forget_prior', False)
                        if arguments is None:
                            arguments = dict()
                        if not isinstance(arguments, dict):
                            raise DAError("action buttons code included an arguments item that was not a dictionary")
                        action = button['action']
                        if not (re.search(r'^https?://', action) or action.startswith('javascript:') or action.startswith('/') or action.startswith('?')):
                            if forget_prior:
                                arguments = {'_action': action, '_arguments': arguments}
                                action = '_da_priority_action'
                            action = docassemble.base.functions.url_action(action, **arguments)
                        label = button['label']
                        extras['action_buttons'].append(dict(action=action, label=label, color=color, icon=icon, placement=placement, target=target))
            for item in extras['action_buttons']:
                if color not in ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark', 'link'):
                    raise DAError("color in action buttons not valid: " + repr(color))
        if hasattr(self, 'question_metadata'):
            extras['questionMetadata'] = recursive_eval_textobject_or_primitive(self.question_metadata, user_dict)
        if hasattr(self, 'css_class') and self.css_class is not None:
            extras['cssClass'] = self.css_class.text(user_dict)
        elif 'css class' in user_dict['_internal'] and user_dict['_internal']['css class'] is not None:
            extras['cssClass'] = user_dict['_internal']['css class']
        elif self.language in self.interview.default_screen_parts and 'css class' in self.interview.default_screen_parts[self.language]:
            extras['cssClass'] = self.interview.default_screen_parts[self.language]['css class'].text(user_dict)
        elif 'css class' in the_default_titles:
            extras['cssClass'] = the_default_titles['css class']
        if hasattr(self, 'table_css_class') and self.table_css_class is not None:
            extras['tableCssClass'] = self.table_css_class.text(user_dict)
        elif 'table css class' in user_dict['_internal'] and user_dict['_internal']['table css class'] is not None:
            extras['tableCssClass'] = user_dict['_internal']['table css class']
        elif self.language in self.interview.default_screen_parts and 'table css class' in self.interview.default_screen_parts[self.language]:
            extras['tableCssClass'] = self.interview.default_screen_parts[self.language]['table css class'].text(user_dict)
        elif 'table css class' in the_default_titles:
            extras['tableCssClass'] = the_default_titles['table css class']
        if hasattr(self, 'undertext') and self.undertext is not None:
            extras['underText'] = self.undertext.text(user_dict)
        elif 'under' in user_dict['_internal'] and user_dict['_internal']['under'] is not None:
            extras['underText'] = user_dict['_internal']['under']
        elif self.language in self.interview.default_screen_parts and 'under' in self.interview.default_screen_parts[self.language]:
            extras['underText'] = self.interview.default_screen_parts[self.language]['under'].text(user_dict)
        elif 'under' in the_default_titles:
            extras['underText'] = the_default_titles['under']
        if hasattr(self, 'pretext') and self.pretext is not None:
            extras['pre text'] = self.pretext.text(user_dict)
        elif 'pre' in user_dict['_internal'] and user_dict['_internal']['pre'] is not None:
            extras['pre text'] = user_dict['_internal']['pre']
        elif self.language in self.interview.default_screen_parts and 'pre' in self.interview.default_screen_parts[self.language]:
            extras['pre text'] = self.interview.default_screen_parts[self.language]['pre'].text(user_dict)
        elif 'pre' in the_default_titles:
            extras['pre text'] = the_default_titles['pre']
        if hasattr(self, 'posttext') and self.posttext is not None:
            extras['post text'] = self.posttext.text(user_dict)
        elif 'post' in user_dict['_internal'] and user_dict['_internal']['post'] is not None:
            extras['post text'] = user_dict['_internal']['post']
        elif self.language in self.interview.default_screen_parts and 'post' in self.interview.default_screen_parts[self.language]:
            extras['post text'] = self.interview.default_screen_parts[self.language]['post'].text(user_dict)
        elif 'post' in the_default_titles:
            extras['post text'] = the_default_titles['post']
        if hasattr(self, 'righttext') and self.righttext is not None:
            extras['rightText'] = self.righttext.text(user_dict)
        elif 'right' in user_dict['_internal'] and user_dict['_internal']['right'] is not None:
            extras['rightText'] = user_dict['_internal']['right']
        elif self.language in self.interview.default_screen_parts and 'right' in self.interview.default_screen_parts[self.language]:
            extras['rightText'] = self.interview.default_screen_parts[self.language]['right'].text(user_dict)
        elif 'right' in the_default_titles:
            extras['rightText'] = the_default_titles['right']
        for screen_part in ('footer', 'submit', 'exit link', 'exit label', 'exit url', 'full', 'logo', 'title', 'subtitle', 'tab title', 'short title', 'logo', 'title url', 'title url opens in other window'):
            if screen_part in user_dict['_internal'] and user_dict['_internal'][screen_part] is not None:
                extras[screen_part + ' text'] = user_dict['_internal'][screen_part]
        if self.language in self.interview.default_screen_parts:
            for screen_part in self.interview.default_screen_parts[self.language]:
                if screen_part in ('footer', 'submit', 'exit link', 'exit label', 'exit url', 'full', 'logo', 'title', 'subtitle', 'tab title', 'short title', 'logo', 'title url', 'title url opens in other window') and (screen_part + ' text') not in extras:
                    extras[screen_part + ' text'] = self.interview.default_screen_parts[self.language][screen_part].text(user_dict)
        for key, val in the_default_titles.items():
            if key in ('pre', 'post', 'footer', 'submit', 'exit link', 'exit label', 'exit url', 'full', 'logo', 'title', 'subtitle', 'tab title', 'short title', 'logo', 'title url', 'title url opens in other window') and (key + ' text') not in extras:
                extras[key + ' text'] = val
        if len(self.terms):
            lang = docassemble.base.functions.get_language()
            extras['terms'] = dict()
            for termitem, definition in self.terms.items():
                if lang in definition['alt_terms']:
                    extras['terms'][definition['alt_terms'][lang].lower()] = dict(definition=definition['definition'].text(user_dict))
                else:
                    extras['terms'][termitem] = dict(definition=definition['definition'].text(user_dict))
        if len(self.autoterms):
            lang = docassemble.base.functions.get_language()
            extras['autoterms'] = dict()
            for termitem, definition in self.autoterms.items():
                if lang in definition['alt_terms']:
                    extras['autoterms'][definition['alt_terms'][lang].lower()] = dict(definition=definition['definition'].text(user_dict))
                else:
                    extras['autoterms'][termitem] = dict(definition=definition['definition'].text(user_dict))
        for term_type in ('terms', 'autoterms'):
            if term_type in user_dict['_internal']:
                extras['interview_' + term_type] = dict()
                for lang, termdefs in getattr(self.interview, term_type).items():
                    if lang not in extras['interview_' + term_type]:
                        extras['interview_' + term_type][lang] = dict()
                    for term, term_info in termdefs.items():
                        extras['interview_' + term_type][lang][term] = term_info
                for lang, termdefs in user_dict['_internal'][term_type].items():
                    if lang not in extras['interview_' + term_type]:
                        extras['interview_' + term_type][lang] = dict()
                    for term, term_info in termdefs.items():
                        extras['interview_' + term_type][lang][term] = term_info
        if self.css is not None:
            extras['css'] = self.css.text(user_dict)
        if self.script is not None:
            extras['script'] = self.script.text(user_dict)
        if self.continuelabel is not None:
            continuelabel = self.continuelabel.text(user_dict)
        elif self.question_type == 'review':
            if 'resume button label' in user_dict['_internal'] and user_dict['_internal']['resume button label'] is not None:
                continuelabel = user_dict['_internal']['resume button label']
            elif self.language in self.interview.default_screen_parts and 'resume button label' in self.interview.default_screen_parts[self.language]:
                continuelabel = self.interview.default_screen_parts[self.language]['resume button label'].text(user_dict)
            elif 'resume button label' in the_default_titles:
                continuelabel = the_default_titles['resume button label']
            else:
                continuelabel = None
        else:
            if 'continue button label' in user_dict['_internal'] and user_dict['_internal']['continue button label'] is not None:
                continuelabel = user_dict['_internal']['continue button label']
            elif self.language in self.interview.default_screen_parts and 'continue button label' in self.interview.default_screen_parts[self.language]:
                continuelabel = self.interview.default_screen_parts[self.language]['continue button label'].text(user_dict)
            elif 'continue button label' in the_default_titles:
                continuelabel = the_default_titles['continue button label']
            else:
                continuelabel = None
        if self.backbuttonlabel is not None:
            extras['back button label text'] = self.backbuttonlabel.text(user_dict)
        elif 'back button label' in user_dict['_internal'] and user_dict['_internal']['back button label'] is not None:
            extras['back button label text'] = user_dict['_internal']['back button label']
        elif self.language in self.interview.default_screen_parts and 'back button label' in self.interview.default_screen_parts[self.language]:
            extras['back button label text'] = self.interview.default_screen_parts[self.language]['back button label'].text(user_dict)
        elif 'back button label' in the_default_titles:
            extras['back button label text'] = the_default_titles['back button label']
        else:
            extras['back button label text'] = None
        if self.cornerbackbuttonlabel is not None:
            extras['corner back button label text'] = self.cornerbackbuttonlabel.text(user_dict)
        elif 'corner back button label' in user_dict['_internal'] and user_dict['_internal']['corner back button label'] is not None:
            extras['corner back button label text'] = user_dict['_internal']['corner back button label']
        elif self.language in self.interview.default_screen_parts and 'corner back button label' in self.interview.default_screen_parts[self.language]:
            extras['corner back button label text'] = self.interview.default_screen_parts[self.language]['corner back button label'].text(user_dict)
        elif 'corner back button label' in the_default_titles:
            extras['corner back button label text'] = the_default_titles['corner back button label']
        else:
            extras['corner back button label text'] = None
        if self.helptext is not None:
            if self.helplabel is not None:
                helplabel = self.helplabel.text(user_dict)
            elif 'help label' in user_dict['_internal'] and user_dict['_internal']['help label'] is not None:
                helplabel = user_dict['_internal']['help label']
            elif self.language in self.interview.default_screen_parts and 'help label' in self.interview.default_screen_parts[self.language]:
                helplabel = self.interview.default_screen_parts[self.language]['help label'].text(user_dict)
            elif 'help label' in the_default_titles:
                helplabel = the_default_titles['help label']
            else:
                helplabel = None
            if self.audiovideo is not None and 'help' in self.audiovideo:
                the_audio_video = process_audio_video_list(self.audiovideo['help'], user_dict)
            else:
                the_audio_video = None
            help_content = self.helptext.text(user_dict)
            if re.search(r'[^\s]', help_content) or the_audio_video is not None:
                help_text_list = [{'heading': None, 'content': help_content, 'audiovideo': the_audio_video, 'label': helplabel, 'from': 'question'}]
            else:
                help_text_list = list()
        else:
            help_text_list = list()
            if self.language in self.interview.default_screen_parts and 'help label' in self.interview.default_screen_parts[self.language]:
                extras['help label text'] = self.interview.default_screen_parts[self.language]['help label'].text(user_dict)
            elif 'help label' in the_default_titles:
                extras['help label text'] = the_default_titles['help label']
        interview_help_text_list = self.interview.processed_helptext(user_dict, self.language)
        if len(interview_help_text_list) > 0:
            help_text_list.extend(interview_help_text_list)
        if self.audiovideo is not None and 'question' in self.audiovideo:
            audiovideo = process_audio_video_list(self.audiovideo['question'], user_dict)
        else:
            audiovideo = None
        if self.decorations is not None:
            decorations = list()
            for decoration_item in self.decorations:
                processed_item = dict()
                for key, value in decoration_item.items():
                    processed_item[key] = value.text(user_dict).strip()
                decorations.append(processed_item)
        else:
            decorations = None
        selectcompute = dict()
        defaults = dict()
        defined = dict()
        hints = dict()
        helptexts = dict()
        labels = dict()
        extras['required'] = dict()
        if hasattr(self, 'back_button'):
            if isinstance(self.back_button, (bool, NoneType)):
                extras['back_button'] = self.back_button
            else:
                extras['back_button'] = eval(self.back_button, user_dict)
        if hasattr(self, 'allowed_to_set'):
            if isinstance(self.allowed_to_set, list):
                extras['allowed_to_set'] = self.allowed_to_set
            else:
                extras['allowed_to_set'] = eval(self.allowed_to_set, user_dict)
                if not isinstance(extras['allowed_to_set'], list):
                    raise DAError("allowed to set code did not evaluate to a list")
                for item in extras['allowed_to_set']:
                    if not isinstance(item, str):
                        raise DAError("allowed to set code did not evaluate to a list of text items")
        if self.reload_after is not None:
            number = str(self.reload_after.text(user_dict))
            if number not in ("False", "false", "Null", "None", "none", "null"):
                if number in ("True", "true"):
                    number = "10"
                if number:
                    number = re.sub(r'[^0-9]', r'', number)
                else:
                    number = "10"
                if int(number) < 4:
                    number = "4"
                extras['reload_after'] = number
        if hasattr(self, 'allow_downloading'):
            if isinstance(self.allow_downloading, bool):
                extras['allow_downloading'] = self.allow_downloading
            else:
                extras['allow_downloading'] = eval(self.allow_downloading, user_dict)
        if hasattr(self, 'always_include_editable_files'):
            if isinstance(self.always_include_editable_files, bool):
                extras['always_include_editable_files'] = self.always_include_editable_files
            else:
                extras['always_include_editable_files'] = eval(self.always_include_editable_files, user_dict)
        if hasattr(self, 'attachment_notice'):
            if isinstance(self.attachment_notice, bool):
                extras['attachment_notice'] = self.attachment_notice
            else:
                extras['attachment_notice'] = eval(self.attachment_notice, user_dict)
        if hasattr(self, 'download_tab'):
            if isinstance(self.download_tab, bool):
                extras['download_tab'] = self.download_tab
            else:
                extras['download_tab'] = eval(self.download_tab, user_dict)
        if hasattr(self, 'manual_attachment_list'):
            if isinstance(self.manual_attachment_list, bool):
                extras['manual_attachment_list'] = self.manual_attachment_list
            else:
                extras['manual_attachment_list'] = eval(self.manual_attachment_list, user_dict)
        if hasattr(self, 'allow_emailing'):
            if isinstance(self.allow_emailing, bool):
                extras['allow_emailing'] = self.allow_emailing
            else:
                extras['allow_emailing'] = eval(self.allow_emailing, user_dict)
        if hasattr(self, 'zip_filename'):
            extras['zip_filename'] = docassemble.base.functions.single_paragraph(self.zip_filename.text(user_dict))
        if hasattr(self, 'ga_id'):
            extras['ga_id'] = self.ga_id.text(user_dict)
        if hasattr(self, 'segment') and 'id' in self.segment:
            extras['segment'] = dict(arguments=dict())
            extras['segment']['id'] = self.segment['id'].text(user_dict)
            if 'arguments' in self.segment:
                for key, val in self.segment['arguments'].items():
                    extras['segment']['arguments'][key] = self.segment['arguments'][key].text(user_dict)
        if self.question_type == 'response':
            extras['content_type'] = self.content_type.text(user_dict)
            # if hasattr(self, 'binaryresponse'):
            #     extras['binaryresponse'] = self.binaryresponse
        elif self.question_type == 'sendfile':
            # if self.response_file:
            #     extras['response_filename'] = self.response_file.path()
            # else:
            #     extras['response_filename'] = None
            extras['content_type'] = self.content_type.text(user_dict)
        elif self.question_type == 'review':
            if hasattr(self, 'skip_undefined') and not self.skip_undefined:
                skip_undefined = False
            else:
                skip_undefined = True
            extras['ok'] = dict()
            for field in self.fields:
                docassemble.base.functions.this_thread.misc['current_field'] = field.number
                extras['ok'][field.number] = False
                if hasattr(field, 'saveas_code'):
                    failed = False
                    for (expression, is_showif) in field.saveas_code:
                        if skip_undefined:
                            try:
                                the_val = eval(expression, user_dict)
                            except LazyNameError:
                                raise
                            except Exception as err:
                                if self.interview.debug:
                                    logmessage("Exception in review block: " + err.__class__.__name__ + ": " + str(err))
                                failed = True
                                break
                            if is_showif and not the_val:
                                failed = True
                                break
                        else:
                            the_val = eval(expression, user_dict)
                            if is_showif and not the_val:
                                failed = True
                                break
                    if failed:
                        continue
                if hasattr(field, 'action'):
                    if 'action' not in extras:
                        extras['action'] = dict()
                    extras['action'][field.number] = json.dumps(substitute_vars_action(field.action, self.is_generic, the_x, iterators))
                if hasattr(field, 'extras'):
                    if 'show_if_js' in field.extras:
                        if 'show_if_js' not in extras:
                            extras['show_if_js'] = dict()
                        extras['show_if_js'][field.number] = dict(expression=field.extras['show_if_js']['expression'].text(user_dict), vars=copy.deepcopy(field.extras['show_if_js']['vars']), sign=field.extras['show_if_js']['sign'], mode=field.extras['show_if_js']['mode'])
                    if 'field metadata' in field.extras:
                        if 'field metadata' not in extras:
                            extras['field metadata'] = dict()
                        if skip_undefined:
                            try:
                                extras['field metadata'][field.number] = recursive_eval_textobject_or_primitive(field.extras['field metadata'], user_dict)
                            except LazyNameError:
                                raise
                            except Exception as err:
                                if self.interview.debug:
                                    logmessage("Exception in field metadata: " + err.__class__.__name__ + ": " + str(err))
                                continue
                        else:
                            extras['field metadata'][field.number] = recursive_eval_textobject_or_primitive(field.extras['field metadata'], user_dict)
                    for key in ('note', 'html', 'min', 'max', 'minlength', 'maxlength', 'step', 'scale', 'inline', 'inline width', 'currency symbol'): # 'script', 'css',
                        if key in field.extras:
                            if key not in extras:
                                extras[key] = dict()
                            if skip_undefined:
                                try:
                                    extras[key][field.number] = field.extras[key].text(user_dict).strip()
                                except LazyNameError:
                                    raise
                                except Exception as err:
                                    if self.interview.debug:
                                        logmessage("Exception in review block: " + err.__class__.__name__ + ": " + str(err))
                                    continue
                            else:
                                extras[key][field.number] = field.extras[key].text(user_dict)
                            if isinstance(extras[key][field.number], str):
                                extras[key][field.number] = extras[key][field.number].strip()
                                if extras[key][field.number] == '':
                                    del extras[key][field.number]
                if hasattr(field, 'helptext'):
                    if skip_undefined:
                        try:
                            helptexts[field.number] = field.helptext.text(user_dict)
                        except LazyNameError:
                            raise
                        except Exception as err:
                            if self.interview.debug:
                                logmessage("Exception in review block: " + err.__class__.__name__ + ": " + str(err))
                            continue
                    else:
                        helptexts[field.number] = field.helptext.text(user_dict)
                if hasattr(field, 'label'):
                    if skip_undefined:
                        try:
                            labels[field.number] = field.label.text(user_dict)
                        except LazyNameError:
                            raise
                        except Exception as err:
                            if self.interview.debug:
                                logmessage("Exception in review block: " + err.__class__.__name__ + ": " + str(err))
                            continue
                    else:
                        labels[field.number] = field.label.text(user_dict)
                extras['ok'][field.number] = True
            if 'current_field' in docassemble.base.functions.this_thread.misc:
                del docassemble.base.functions.this_thread.misc['current_field']
        else:
            if hasattr(self, 'list_collect') and process_list_collect and eval(self.list_collect, user_dict):
                fields_to_scan = self.get_fields_and_sub_fields(user_dict)
                indexno = 0
                common_var = None
                for field in fields_to_scan:
                    if not hasattr(field, 'saveas'):
                        continue
                    the_saveas = from_safeid(field.saveas)
                    if common_var is None:
                        common_var = the_saveas
                        continue
                    mismatch = False
                    for char_index in range(len(common_var)):
                        if the_saveas[char_index] != common_var[char_index]:
                            mismatch = True
                            break
                    if mismatch:
                        common_var = common_var[0:char_index]
                common_var = re.sub(r'[^\]]*$', '', common_var)
                m = re.search(r'^(.*)\[([ijklmn])\]$', common_var)
                if not m:
                    raise DAError("Cannot use list collect on these fields.  " + common_var)
                the_list_varname = m.group(1)
                if hasattr(self, 'list_collect_is_final'):
                    extras['list_collect_is_final'] = eval(self.list_collect_is_final, user_dict)
                else:
                    extras['list_collect_is_final'] = True
                if hasattr(self, 'list_collect_allow_append'):
                    extras['list_collect_allow_append'] = eval(self.list_collect_allow_append, user_dict)
                else:
                    extras['list_collect_allow_append'] = True
                if hasattr(self, 'list_collect_allow_delete'):
                    extras['list_collect_allow_delete'] = eval(self.list_collect_allow_delete, user_dict)
                else:
                    extras['list_collect_allow_delete'] = True
                if hasattr(self, 'list_collect_add_another_label'):
                    extras['list_collect_add_another_label'] = self.list_collect_add_another_label.text(user_dict)
                else:
                    extras['list_collect_add_another_label'] = None
                extras['list_iterator'] = m.group(2)
                the_list = eval(the_list_varname, user_dict)
                if not hasattr(the_list, 'elements') or not isinstance(the_list.elements, list):
                    raise DAError("Cannot use list collect on a variable that is not a DAList.")
                extras['list_collect'] = the_list
                extras['list_message'] = dict()
                if hasattr(the_list, 'minimum_number') and the_list.minimum_number:
                    extras['list_minimum'] = the_list.minimum_number
                iterator_index = list_of_indices.index(extras['list_iterator'])
                length_to_use = len(the_list.elements)
                if hasattr(the_list, 'minimum_number') and the_list.minimum_number is not None and the_list.minimum_number > length_to_use:
                    length_to_use = the_list.minimum_number
                if length_to_use == 0:
                    length_to_use = 1
                if the_list.ask_object_type or not extras['list_collect_allow_append']:
                    extra_amount = 0
                else:
                    extra_amount = get_config('list collect extra count', 15)
                for list_indexno in range(length_to_use + extra_amount):
                    new_iterators = copy.copy(iterators)
                    new_iterators[iterator_index] = str(list_indexno)
                    ask_result = self.ask(user_dict, old_user_dict, the_x, new_iterators, sought, orig_sought, process_list_collect=False, test_for_objects=(list_indexno < length_to_use))
                    if hasattr(self, 'list_collect_label'):
                        extras['list_message'][list_indexno] = self.list_collect_label.text(user_dict)
                    else:
                        extras['list_message'][list_indexno] = ''
                    for key in ('selectcompute', 'defaults', 'hints', 'helptexts', 'labels'):
                        for field_num, val in ask_result[key].items():
                            if key == 'selectcompute':
                                selectcompute[str(list_indexno) + '_' + str(field_num)] = val
                                if list_indexno == length_to_use - 1:
                                    selectcompute[str(list_indexno + 1) + '_' + str(field_num)] = val
                                    #for ii in range(1, extra_amount + 1):
                                    #    selectcompute[str(list_indexno + ii) + '_' + str(field_num)] = val
                            elif key == 'defaults':
                                defaults[str(list_indexno) + '_' + str(field_num)] = val
                                #if list_indexno == length_to_use - 1:
                                    #for ii in range(1, extra_amount + 1):
                                    #    defaults[str(list_indexno + ii) + '_' + str(field_num)] = val
                            elif key == 'hints':
                                hints[str(list_indexno) + '_' + str(field_num)] = val
                                #if list_indexno == length_to_use - 1:
                                    #for ii in range(1, extra_amount + 1):
                                    #    hints[str(list_indexno + ii) + '_' + str(field_num)] = val
                            elif key == 'helptexts':
                                helptexts[str(list_indexno) + '_' + str(field_num)] = val
                                #if list_indexno == length_to_use - 1:
                                    #for ii in range(1, extra_amount + 1):
                                    #    helptexts[str(list_indexno + ii) + '_' + str(field_num)] = val
                            elif key == 'labels':
                                labels[str(list_indexno) + '_' + str(field_num)] = val
                                #if list_indexno == length_to_use - 1:
                                    #for ii in range(1, extra_amount + 1):
                                    #    labels[str(list_indexno + ii) + '_' + str(field_num)] = val
                    for key, possible_dict in ask_result['extras'].items():
                        if isinstance(possible_dict, dict):
                            if key not in extras:
                                extras[key] = dict()
                            for field_num, val in possible_dict.items():
                                extras[key][str(list_indexno) + '_' + str(field_num)] = val
                                #if list_indexno == length_to_use - 1:
                                    #for ii in range(1, extra_amount + 1):
                                    #    extras[key][str(list_indexno + ii) + '_' + str(field_num)] = val
                if len(iterators):
                    for indexno in range(len(iterators)):
                        exec(list_of_indices[indexno] + " = " + iterators[indexno], user_dict)
            else:
                if hasattr(self, 'fields_saveas'):
                    only_empty_fields_exist = False
                else:
                    only_empty_fields_exist = True
                commands_to_run = list()
                for field in self.fields:
                    if hasattr(field, 'inputtype') and field.inputtype == 'combobox':
                        only_empty_fields_exist = False
                    docassemble.base.functions.this_thread.misc['current_field'] = field.number
                    if hasattr(field, 'has_code') and field.has_code:
                        # standalone multiple-choice questions
                        selectcompute[field.number] = list()
                        for choice in field.choices:
                            if 'compute' in choice and isinstance(choice['compute'], CodeType):
                                selectcompute[field.number].extend(process_selections(eval(choice['compute'], user_dict)))
                            else:
                                new_item = dict()
                                if 'image' in choice:
                                    new_item['image'] = choice['image']
                                if 'help' in choice:
                                    new_item['help'] = choice['help'].text(user_dict)
                                if 'default' in choice:
                                    new_item['default'] = choice['default']
                                if isinstance(choice['key'], TextObject):
                                    new_item['key'] = choice['key'].text(user_dict)
                                else:
                                    new_item['key'] = choice['key']
                                new_item['label'] = choice['label'].text(user_dict)
                                selectcompute[field.number].append(new_item)
                        if len(selectcompute[field.number]) > 0:
                            only_empty_fields_exist = False
                        elif test_for_objects:
                            if hasattr(field, 'datatype') and field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                                ensure_object_exists(from_safeid(field.saveas), field.datatype, user_dict, commands=commands_to_run)
                                commands_to_run.append(from_safeid(field.saveas) + ".gathered = True")
                            else:
                                if not (hasattr(field, 'inputtype') and field.inputtype == 'combobox'):
                                    commands_to_run.append(from_safeid(field.saveas) + ' = None')
                    elif hasattr(field, 'choicetype') and field.choicetype == 'compute':
                        # multiple choice field in choices
                        if hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio', 'object_multiselect', 'object_checkboxes', 'multiselect', 'checkboxes'):
                            exec("import docassemble.base.core", user_dict)
                        if hasattr(field, 'object_labeler'):
                            labeler_func = eval(field.object_labeler['compute'], user_dict)
                            if not isinstance(labeler_func, types.FunctionType):
                                raise DAError("The object labeler was not a function")
                            user_dict['_DAOBJECTLABELER'] = labeler_func
                        else:
                            labeler_func = None
                        if hasattr(field, 'help_generator'):
                            help_generator_func = eval(field.help_generator['compute'], user_dict)
                            if not isinstance(help_generator_func, types.FunctionType):
                                raise DAError("The help generator was not a function")
                            user_dict['_DAHELPGENERATOR'] = help_generator_func
                        else:
                            help_generator_func = None
                        if hasattr(field, 'image_generator'):
                            image_generator_func = eval(field.image_generator['compute'], user_dict)
                            if not isinstance(image_generator_func, types.FunctionType):
                                raise DAError("The image generator was not a function")
                            user_dict['_DAIMAGEGENERATOR'] = image_generator_func
                        else:
                            image_generator_func = None
                        to_compute = field.selections['compute']
                        if field.datatype in ('object_multiselect', 'object_checkboxes'):
                            default_exists = False
                            #logmessage("Testing for " + from_safeid(field.saveas))
                            try:
                                assert test_for_objects
                                eval(from_safeid(field.saveas), user_dict)
                                default_to_use = from_safeid(field.saveas)
                            except:
                                default_to_use = 'None'
                            #logmessage("Running " + '_DAOBJECTDEFAULTDA = ' + default_to_use)
                            exec('_DAOBJECTDEFAULTDA = ' + default_to_use, user_dict)
                        if 'exclude' in field.selections:
                            exclude_list = list()
                            for x in field.selections['exclude']:
                                exclude_list.append(eval(x, user_dict))
                            selectcompute[field.number] = process_selections(eval(to_compute, user_dict), exclude=exclude_list)
                        else:
                            #logmessage("Doing " + field.selections.get('sourcecode', "No source code"))
                            selectcompute[field.number] = process_selections(eval(to_compute, user_dict))
                        if field.datatype in ('object_multiselet', 'object_checkboxes') and '_DAOBJECTDEFAULTDA' in user_dict:
                            del user_dict['_DAOBJECTDEFAULTDA']
                        if labeler_func is not None:
                            del user_dict['_DAOBJECTLABELER']
                        if help_generator_func is not None:
                            del user_dict['_DAHELPGENERATOR']
                        if image_generator_func is not None:
                            del user_dict['_DAIMAGEGENERATOR']
                        if len(selectcompute[field.number]) > 0:
                            only_empty_fields_exist = False
                        elif test_for_objects:
                            if hasattr(field, 'datatype') and field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                                ensure_object_exists(from_safeid(field.saveas), field.datatype, user_dict, commands=commands_to_run)
                                commands_to_run.append(from_safeid(field.saveas) + '.gathered = True')
                            else:
                                if not (hasattr(field, 'inputtype') and field.inputtype == 'combobox'):
                                    commands_to_run.append(from_safeid(field.saveas) + ' = None')
                    elif hasattr(field, 'choicetype') and field.choicetype == 'manual':
                        if 'exclude' in field.selections:
                            to_exclude = list()
                            for x in field.selections['exclude']:
                                to_exclude.append(eval(x, user_dict))
                            to_exclude = unpack_list(to_exclude)
                            selectcompute[field.number] = list()
                            for candidate in field.selections['values']:
                                if isinstance(candidate['key'], TextObject):
                                    new_item = dict(key=candidate['key'].text(user_dict), label=candidate['label'].text(user_dict))
                                else:
                                    new_item = dict(key=candidate['key'], label=candidate['label'].text(user_dict))
                                if 'image' in candidate:
                                    new_item['image'] = candidate['image']
                                if 'help' in candidate:
                                    new_item['help'] = candidate['help'].text(user_dict)
                                if 'default' in candidate:
                                    new_item['default'] = candidate['default']
                                if new_item['key'] not in to_exclude:
                                    selectcompute[field.number].append(new_item)
                        else:
                            selectcompute[field.number] = list()
                            for item in field.selections['values']:
                                if isinstance(item['key'], TextObject):
                                    new_item = dict(key=item['key'].text(user_dict), label=item['label'].text(user_dict))
                                else:
                                    new_item = dict(key=item['key'], label=item['label'].text(user_dict))
                                if 'image' in item:
                                    new_item['image'] = item['image']
                                if 'help' in item:
                                    new_item['help'] = item['help'].text(user_dict)
                                if 'default' in item:
                                    new_item['default'] = item['default']
                                selectcompute[field.number].append(new_item)
                        if len(selectcompute[field.number]) > 0:
                            only_empty_fields_exist = False
                        else:
                            if not (hasattr(field, 'inputtype') and field.inputtype == 'combobox'):
                                commands_to_run.append(from_safeid(field.saveas) + ' = None')
                    elif hasattr(field, 'saveas') and self.question_type == "multiple_choice":
                        selectcompute[field.number] = list()
                        for item in field.choices:
                            new_item = dict()
                            if 'image' in item:
                                new_item['image'] = item['image']
                            if 'help' in item:
                                new_item['help'] = item['help'].text(user_dict)
                            if 'default' in item:
                                new_item['default'] = item['default']
                            if isinstance(item['key'], TextObject):
                                new_item['key'] = item['key'].text(user_dict)
                            else:
                                new_item['key'] = item['key']
                            new_item['label'] = item['label'].text(user_dict)
                            selectcompute[field.number].append(new_item)
                        if len(selectcompute[field.number]) > 0:
                            only_empty_fields_exist = False
                        else:
                            if not (hasattr(field, 'inputtype') and field.inputtype == 'combobox'):
                                commands_to_run.append(from_safeid(field.saveas) + ' = None')
                    elif self.question_type == "multiple_choice":
                        selectcompute[field.number] = list()
                        for item in field.choices:
                            new_item = dict()
                            if 'image' in item:
                                new_item['image'] = item['image']
                            if 'help' in item:
                                new_item['help'] = item['help'].text(user_dict)
                            if 'default' in item:
                                new_item['default'] = item['default']
                            new_item['label'] = item['label'].text(user_dict)
                            new_item['key'] = item['key']
                            selectcompute[field.number].append(new_item)
                        only_empty_fields_exist = False
                    else:
                        only_empty_fields_exist = False
                if len(self.fields) > 0 and only_empty_fields_exist:
                    if test_for_objects:
                        assumed_objects = set()
                        for field in self.fields:
                            if hasattr(field, 'saveas'):
                                parse_result = parse_var_name(from_safeid(field.saveas))
                                if not parse_result['valid']:
                                    raise DAError("Variable name " + from_safeid(field.saveas) + " is invalid: " + parse_result['reason'])
                                if len(parse_result['objects']):
                                    assumed_objects.add(parse_result['objects'][-1])
                                if len(parse_result['bracket_objects']):
                                    assumed_objects.add(parse_result['bracket_objects'][-1])
                        for var in assumed_objects:
                            if complications.search(var) or var not in user_dict:
                                eval(var, user_dict)
                    raise CodeExecute(commands_to_run, self)
                if 'current_field' in docassemble.base.functions.this_thread.misc:
                    del docassemble.base.functions.this_thread.misc['current_field']
                extras['ok'] = dict()
                for field in self.fields:
                    docassemble.base.functions.this_thread.misc['current_field'] = field.number
                    if hasattr(field, 'showif_code'):
                        result = eval(field.showif_code, user_dict)
                        if hasattr(field, 'extras') and 'show_if_sign_code' in field.extras and field.extras['show_if_sign_code'] == 0:
                            if result:
                                extras['ok'][field.number] = False
                                continue
                        else:
                            if not result:
                                extras['ok'][field.number] = False
                                continue
                    extras['ok'][field.number] = True
                    if hasattr(field, 'nota'):
                        if 'nota' not in extras:
                            extras['nota'] = dict()
                        if isinstance(field.nota, bool):
                            extras['nota'][field.number] = field.nota
                        else:
                            extras['nota'][field.number] = field.nota.text(user_dict)
                    if hasattr(field, 'permissions'):
                        if 'permissions' not in extras:
                            extras['permissions'] = dict()
                        extras['permissions'][field.number] = dict()
                        if isinstance(field.permissions['private'], bool):
                            extras['permissions'][field.number]['private'] = field.permissions['private']
                        elif field.permissions['private'] is not None:
                            extras['permissions'][field.number]['private'] = True if eval(field.permissions['private']['compute'], user_dict) else False
                        if isinstance(field.permissions['persistent'], bool):
                            extras['permissions'][field.number]['persistent'] = field.permissions['persistent']
                        elif field.permissions['persistent'] is not None:
                            extras['permissions'][field.number]['persistent'] = True if eval(field.permissions['persistent']['compute'], user_dict) else False
                        if field.permissions['allow_users'] is not None:
                            if isinstance(field.permissions['allow_users'], list):
                                extras['permissions'][field.number]['allow_users'] = allow_users_list(field.permissions['allow_users'])
                            else:
                                extras['permissions'][field.number]['allow_users'] = allow_users_list(eval(field.permissions['allow_users']['compute'], user_dict))
                        if field.permissions['allow_privileges'] is not None:
                            if isinstance(field.permissions['allow_privileges'], list):
                                extras['permissions'][field.number]['allow_privileges'] = allow_privileges_list(field.permissions['allow_privileges'])
                            else:
                                extras['permissions'][field.number]['allow_privileges'] = allow_privileges_list(eval(field.permissions['allow_privileges']['compute'], user_dict))
                    if isinstance(field.required, bool):
                        extras['required'][field.number] = field.required
                    else:
                        extras['required'][field.number] = eval(field.required['compute'], user_dict)
                    if hasattr(field, 'max_image_size') and hasattr(field, 'datatype') and field.datatype in ('file', 'files', 'camera', 'user', 'environment'):
                        extras['max_image_size'] = eval(field.max_image_size['compute'], user_dict)
                    if hasattr(field, 'image_type') and hasattr(field, 'datatype') and field.datatype in ('file', 'files', 'camera', 'user', 'environment'):
                        extras['image_type'] = eval(field.image_type['compute'], user_dict)
                    if hasattr(field, 'accept') and hasattr(field, 'datatype') and field.datatype in ('file', 'files', 'camera', 'user', 'environment'):
                        if 'accept' not in extras:
                            extras['accept'] = dict()
                        extras['accept'][field.number] = eval(field.accept['compute'], user_dict)
                    if hasattr(field, 'rows') and ((hasattr(field, 'inputtype') and field.inputtype == 'area') or (hasattr(field, 'datatype') and field.datatype in ('multiselect', 'object_multiselect'))):
                        if 'rows' not in extras:
                            extras['rows'] = dict()
                        extras['rows'][field.number] = eval(field.rows['compute'], user_dict)
                    if hasattr(field, 'validation_messages'):
                        if 'validation messages' not in extras:
                            extras['validation messages'] = dict()
                        extras['validation messages'][field.number] = dict()
                        for validation_key, validation_message_template in field.validation_messages.items():
                            extras['validation messages'][field.number][validation_key] = validation_message_template.text(user_dict)
                    if hasattr(field, 'validate'):
                        the_func = eval(field.validate['compute'], user_dict)
                        try:
                            if hasattr(field, 'datatype'):
                                if field.datatype in ('number', 'integer', 'currency', 'range'):
                                    the_func(0)
                                elif field.datatype in ('text', 'password', 'email'):
                                    the_func('')
                                elif field.datatype == 'date':
                                    the_func('01/01/1970')
                                elif field.datatype == 'time':
                                    the_func('12:00 AM')
                                elif field.datatype == 'datetime':
                                    the_func('01/01/1970 12:00 AM')
                                elif field.datatype.startswith('yesno') or field.datatype.startswith('noyes'):
                                    the_func(True)
                            else:
                                the_func('')
                        except DAValidationError as err:
                            pass
                    if hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio', 'object_multiselect', 'object_checkboxes'):
                        if process_list_collect:
                            saveas_to_use = from_safeid(field.saveas)
                        else:
                            saveas_to_use = substitute_vars(from_safeid(field.saveas), self.is_generic, the_x, iterators, last_only=True)
                        if field.number not in selectcompute:
                            raise DAError("datatype was set to object but no code or selections was provided")
                        string = "_internal['objselections'][" + repr(saveas_to_use) + "] = dict()"
                        # logmessage("Doing " + string)
                        try:
                            exec(string, user_dict)
                            for selection in selectcompute[field.number]:
                                key = selection['key']
                                #logmessage("key is " + str(key))
                                real_key = from_safeid(key)
                                string = "_internal['objselections'][" + repr(saveas_to_use) + "][" + repr(key) + "] = " + real_key
                                #logmessage("Doing " + string)
                                exec(string, user_dict)
                        except Exception as err:
                            raise DAError("Failure while processing field with datatype of object: " + err.__class__.__name__ + " " + str(err))
                    if hasattr(field, 'label'):
                        labels[field.number] = field.label.text(user_dict)
                    if hasattr(field, 'extras'):
                        if 'fields_code' in field.extras:
                            the_question = self.get_question_for_field_with_sub_fields(field, user_dict)
                            ask_result = the_question.ask(user_dict, old_user_dict, the_x, iterators, sought, orig_sought)
                            for key in ('selectcompute', 'defaults', 'hints', 'helptexts', 'labels'):
                                for field_num, val in ask_result[key].items():
                                    if key == 'selectcompute':
                                        selectcompute[str(field.number) + '_' + str(field_num)] = val
                                    elif key == 'defaults':
                                        defaults[str(field.number) + '_' + str(field_num)] = val
                                    elif key == 'hints':
                                        hints[str(field.number) + '_' + str(field_num)] = val
                                    elif key == 'helptexts':
                                        helptexts[str(field.number) + '_' + str(field_num)] = val
                                    elif key == 'labels':
                                        labels[str(field.number) + '_' + str(field_num)] = val
                            for key, possible_dict in ask_result['extras'].items():
                                #logmessage(repr("key is " + str(key) + " and possible dict is " + repr(possible_dict)))
                                if isinstance(possible_dict, dict):
                                    #logmessage("key points to a dict")
                                    if key not in extras:
                                        extras[key] = dict()
                                    for field_num, val in possible_dict.items():
                                        #logmessage("Setting " + str(field.number) + '_' + str(field_num))
                                        extras[key][str(field.number) + '_' + str(field_num)] = val
                            for sub_field in the_question.fields:
                                sub_field.number = str(field.number) + '_' + str(sub_field.number)
                            if 'sub_fields' not in extras:
                                extras['sub_fields'] = dict()
                            extras['sub_fields'][field.number] = the_question.fields
                        if 'show_if_js' in field.extras:
                            if 'show_if_js' not in extras:
                                extras['show_if_js'] = dict()
                            extras['show_if_js'][field.number] = dict(expression=field.extras['show_if_js']['expression'].text(user_dict), vars=copy.deepcopy(field.extras['show_if_js']['vars']), sign=field.extras['show_if_js']['sign'], mode=field.extras['show_if_js']['mode'])
                        if 'field metadata' in field.extras:
                            if 'field metadata' not in extras:
                                extras['field metadata'] = dict()
                            extras['field metadata'][field.number] = recursive_eval_textobject_or_primitive(field.extras['field metadata'], user_dict)
                        for key in ('note', 'html', 'min', 'max', 'minlength', 'maxlength', 'show_if_val', 'step', 'scale', 'inline', 'inline width', 'ml_group', 'currency symbol'): # , 'textresponse', 'content_type' #'script', 'css',
                            if key in field.extras:
                                if key not in extras:
                                    extras[key] = dict()
                                extras[key][field.number] = field.extras[key].text(user_dict)
                                if isinstance(extras[key][field.number], str):
                                    extras[key][field.number] = extras[key][field.number].strip()
                                    if extras[key][field.number] == '':
                                        del extras[key][field.number]
                        for key in ('ml_train',):
                            if key in field.extras:
                                if key not in extras:
                                    extras[key] = dict()
                                if isinstance(field.extras[key], bool):
                                    extras[key][field.number] = field.extras[key]
                                else:
                                    extras[key][field.number] = eval(field.extras[key]['compute'], user_dict)
                    if hasattr(field, 'saveas'):
                        try:
                            if not test_for_objects:
                                raise Exception('not setting defaults now')
                            if old_user_dict is not None:
                                for varname in ('x', 'i', 'j', 'k', 'l', 'm', 'n'):
                                    if varname in user_dict:
                                        old_user_dict[varname] = user_dict[varname]
                                    elif varname in old_user_dict:
                                        del old_user_dict[varname]
                                try:
                                    defaults[field.number] = eval(from_safeid(field.saveas), old_user_dict)
                                except:
                                    defaults[field.number] = eval(from_safeid(field.saveas), user_dict)
                            else:
                                defaults[field.number] = eval(from_safeid(field.saveas), user_dict)
                        except:
                            try:
                                defaults[field.number] = user_dict['_internal']['dirty'][substitute_vars(from_safeid(field.saveas), self.is_generic, the_x, iterators)]
                            except:
                                if hasattr(field, 'default'):
                                    if isinstance(field.default, TextObject):
                                        defaults[field.number] = field.default.text(user_dict).strip()
                                    else:
                                        defaults[field.number] = field.default
                                elif hasattr(field, 'extras') and 'default' in field.extras:
                                    defaults[field.number] = eval(field.extras['default']['compute'], user_dict)
                        if hasattr(field, 'hint'):
                            hints[field.number] = field.hint.text(user_dict)
                    if hasattr(field, 'helptext'):
                        helptexts[field.number] = field.helptext.text(user_dict)
                if 'current_field' in docassemble.base.functions.this_thread.misc:
                    del docassemble.base.functions.this_thread.misc['current_field']
        if len(self.attachments) or self.compute_attachment is not None:
            if hasattr(self, 'email_default'):
                the_email_address = self.email_default.text(user_dict).strip()
                if '@' in the_email_address and not re.search(r'\s', the_email_address):
                    extras['email_default'] = the_email_address
            if hasattr(self, 'email_subject'):
                extras['email_subject'] = re.sub(r'[\n\r]+', ' ', self.email_subject.text(user_dict).strip())
            if hasattr(self, 'email_body'):
                extras['email_html'] = '<html><body>' + docassemble.base.filter.markdown_to_html(self.email_body.text(user_dict), status=docassemble.base.functions.this_thread.interview_status, question=self, external=True) + '</body></html>'
                extras['email_body'] = BeautifulSoup(extras['email_html'], "html.parser").get_text('\n')
            if hasattr(self, 'email_template') and ('email_subject' not in extras or 'email_html' not in extras):
                template = eval(self.email_template, user_dict)
                if 'email_subject' not in extras:
                    the_subject = re.sub(r'[\n\r]+', ' ', template.subject.strip())
                    if the_subject:
                        extras['email_subject'] = the_subject
                if 'email_html' not in extras:
                    extras['email_html'] = '<html><body>' + template.content_as_html(external=True) + '</body></html>'
                    extras['email_body'] = BeautifulSoup(extras['email_html'], "html.parser").get_text('\n')
            attachment_text = self.processed_attachments(user_dict) # , the_x=the_x, iterators=iterators
        else:
            attachment_text = []
        if test_for_objects:
            assumed_objects = set()
            for field in self.fields:
                if field.number in extras['ok'] and not extras['ok'][field.number]:
                    continue
                docassemble.base.functions.this_thread.misc['current_field'] = field.number
                if hasattr(field, 'saveas'):
                    # m = re.match(r'(.*)\.[^\.]+', from_safeid(field.saveas))
                    # if m and m.group(1) != 'x':
                    #     assumed_objects.add(m.group(1))
                    parse_result = parse_var_name(from_safeid(field.saveas))
                    if not parse_result['valid']:
                        raise DAError("Variable name " + from_safeid(field.saveas) + " is invalid: " + parse_result['reason'])
                    if len(parse_result['objects']):
                        assumed_objects.add(parse_result['objects'][-1])
                    if len(parse_result['bracket_objects']):
                        assumed_objects.add(parse_result['bracket_objects'][-1])
            if 'current_field' in docassemble.base.functions.this_thread.misc:
                del docassemble.base.functions.this_thread.misc['current_field']
            for var in assumed_objects:
                if complications.search(var) or var not in user_dict:
                    eval(var, user_dict)
        if 'menu_items' in user_dict:
            extras['menu_items'] = user_dict['menu_items']
        if 'track_location' in user_dict:
            extras['track_location'] = user_dict['track_location']
        if 'speak_text' in user_dict:
            extras['speak_text'] = user_dict['speak_text']
        if 'role' in user_dict:
            current_role = user_dict['role']
            if len(self.role) > 0:
                if current_role not in self.role and 'role_event' not in self.fields_used and self.question_type not in ('exit', 'logout', 'exit_logout', 'continue', 'restart', 'leave', 'refresh', 'signin', 'register', 'new_session'):
                    # logmessage("Calling role_event with " + ", ".join(self.fields_used))
                    user_dict['role_needed'] = self.role
                    raise NameError("name 'role_event' is not defined")
            elif self.interview.default_role is not None and current_role not in self.interview.default_role and 'role_event' not in self.fields_used and self.question_type not in ('exit', 'logout', 'exit_logout', 'continue', 'restart', 'leave', 'refresh', 'signin', 'register', 'new_session'):
                # logmessage("Calling role_event with " + ", ".join(self.fields_used))
                user_dict['role_needed'] = self.interview.default_role
                raise NameError("name 'role_event' is not defined")
        if self.question_type == 'review' and sought is not None and not hasattr(self, 'review_saveas'):
            if 'event_stack' not in user_dict['_internal']:
                user_dict['_internal']['event_stack'] = dict()
            session_uid = docassemble.base.functions.this_thread.current_info['user']['session_uid']
            if session_uid not in user_dict['_internal']['event_stack']:
                user_dict['_internal']['event_stack'][session_uid] = list()
            already_there = False
            for event_item in user_dict['_internal']['event_stack'][session_uid]:
                if event_item['action'] in (sought, orig_sought):
                    already_there = True
                    break
            if not already_there:
                user_dict['_internal']['event_stack'][session_uid].insert(0, dict(action=orig_sought, arguments=dict(), context=dict()))
        if self.need_post is not None:
            for need_code in self.need_post:
                eval(need_code, user_dict)
        return({'type': 'question', 'question_text': question_text, 'subquestion_text': subquestion, 'continue_label': continuelabel, 'audiovideo': audiovideo, 'decorations': decorations, 'help_text': help_text_list, 'attachments': attachment_text, 'question': self, 'selectcompute': selectcompute, 'defaults': defaults, 'hints': hints, 'helptexts': helptexts, 'extras': extras, 'labels': labels, 'sought': sought, 'orig_sought': orig_sought}) #'defined': defined,
    def processed_attachments(self, the_user_dict, **kwargs):
        use_cache = kwargs.get('use_cache', True)
        if self.compute_attachment is not None:
            use_cache = False
        seeking_var = kwargs.get('seeking_var', '__novar')
        steps = the_user_dict['_internal'].get('steps', -1)
        #logmessage("processed_attachments: steps is " + str(steps))
        if use_cache and self.interview.cache_documents and hasattr(self, 'name') and self.name + '__SEEKING__' + seeking_var in the_user_dict['_internal']['doc_cache']:
            if steps in the_user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var]:
                #logmessage("processed_attachments: result was in document cache")
                return the_user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var][steps]
            the_user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var].clear()
        result_list = list()
        items = list()
        for x in self.attachments:
            items.append([x, self.prepare_attachment(x, the_user_dict, **kwargs), None])
        for item in items:
            result_list.append(self.finalize_attachment(item[0], item[1], the_user_dict))
        if self.compute_attachment is not None:
            computed_attachment_list = eval(self.compute_attachment, the_user_dict)
            if not (isinstance(computed_attachment_list, list) or (hasattr(computed_attachment_list, 'elements') and isinstance(computed_attachment_list.elements, list))):
                computed_attachment_list = [computed_attachment_list]
            for the_att in computed_attachment_list:
                if the_att.__class__.__name__ == 'DAFileCollection':
                    file_dict = dict()
                    for doc_format in ('pdf', 'rtf', 'docx', 'rtf to docx', 'tex', 'html', 'raw'):
                        if hasattr(the_att, doc_format):
                            the_dafile = getattr(the_att, doc_format)
                            if hasattr(the_dafile, 'number'):
                                file_dict[doc_format] = the_dafile.number
                    if 'formats' not in the_att.info:
                        the_att.info['formats'] = list(file_dict.keys())
                        if 'valid_formats' not in the_att.info:
                            the_att.info['valid_formats'] = list(file_dict.keys())
                    result_list.append({'name': the_att.info['name'], 'filename': the_att.info['filename'], 'description': the_att.info['description'], 'valid_formats': the_att.info.get('valid_formats', ['*']), 'formats_to_use': the_att.info['formats'], 'markdown': the_att.info.get('markdown', dict()), 'content': the_att.info.get('content', dict()), 'extension': the_att.info.get('extension', dict()), 'mimetype': the_att.info.get('mimetype', dict()), 'file': file_dict, 'metadata': the_att.info.get('metadata', dict()), 'variable_name': '', 'orig_variable_name': getattr(the_att, 'instanceName', ''), 'raw': the_att.info.get('raw', False)})
                    #convert_to_pdf_a
                    #file is dict of file numbers
                # if the_att.__class__.__name__ == 'DAFileCollection' and 'attachment' in the_att.info and isinstance(the_att.info, dict) and 'name' in the_att.info['attachment'] and 'number' in the_att.info['attachment'] and len(self.interview.questions_by_name[the_att.info['attachment']['name']].attachments) > the_att.info['attachment']['number']:
                #     attachment = self.interview.questions_by_name[the_att.info['attachment']['name']].attachments[the_att.info['attachment']['number']]
                #     items.append([attachment, self.prepare_attachment(attachment, the_user_dict, **kwargs)])
        if self.interview.cache_documents and hasattr(self, 'name'):
            if self.name + '__SEEKING__' + seeking_var not in the_user_dict['_internal']['doc_cache']:
                the_user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var] = dict()
            the_user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var][steps] = result_list
        return result_list
        #return(list(map((lambda x: self.make_attachment(x, the_user_dict, **kwargs)), self.attachments)))
    def parse_fields(self, the_list, register_target, uses_field):
        result_list = list()
        has_code = False
        if isinstance(the_list, dict):
            new_list = list()
            for key, value in the_list.items():
                new_item = dict()
                new_item[key] = value
                new_list.append(new_item)
            the_list = new_list
        if not isinstance(the_list, list):
            raise DAError("Multiple choices need to be provided in list form.  " + self.idebug(the_list))
        for the_dict in the_list:
            if not isinstance(the_dict, (dict, list)):
                the_dict = {str(the_dict): the_dict}
            elif not isinstance(the_dict, dict):
                raise DAError("Unknown data type for the_dict in parse_fields.  " + self.idebug(the_list))
            result_dict = dict()
            for key, value in the_dict.items():
                if len(the_dict) > 1:
                    if key == 'image':
                        result_dict['image'] = value
                        continue
                    if key == 'help':
                        result_dict['help'] = TextObject(value, question=self)
                        continue
                    if key == 'default':
                        result_dict['default'] = value
                        continue
                if uses_field:
                    if key == 'code':
                        has_code = True
                        result_dict['compute'] = compile(value, '<expression>', 'eval')
                        self.find_fields_in(value)
                    else:
                        result_dict['label'] = TextObject(key, question=self)
                        result_dict['key'] = TextObject(value, question=self, translate=False)
                elif isinstance(value, dict):
                    result_dict['label'] = TextObject(key, question=self)
                    self.embeds = True
                    result_dict['key'] = Question(value, self.interview, register_target=register_target, source=self.from_source, package=self.package, source_code=codecs.decode(bytearray(yaml.safe_dump(value, default_flow_style=False, default_style = '|', allow_unicode=True), encoding='utf-8'), 'utf-8'))
                elif isinstance(value, str):
                    if value in ('exit', 'logout', 'exit_logout', 'leave') and 'url' in the_dict:
                        self.embeds = True
                        result_dict['label'] = TextObject(key, question=self)
                        result_dict['key'] = Question({'command': value, 'url': the_dict['url']}, self.interview, register_target=register_target, source=self.from_source, package=self.package)
                    elif value in ('continue', 'restart', 'refresh', 'signin', 'register', 'exit', 'logout', 'exit_logout', 'leave', 'new_session'):
                        self.embeds = True
                        result_dict['label'] = TextObject(key, question=self)
                        result_dict['key'] = Question({'command': value}, self.interview, register_target=register_target, source=self.from_source, package=self.package)
                    elif key == 'url':
                        pass
                    else:
                        result_dict['label'] = TextObject(key, question=self)
                        result_dict['key'] = TextObject(key, question=self, translate=False)
                elif isinstance(value, bool):
                    result_dict['label'] = TextObject(key, question=self)
                    result_dict['key'] = value
                else:
                    raise DAError("Unknown data type in parse_fields:" + str(type(value)) + ".  " + self.idebug(the_list))
            result_list.append(result_dict)
        return(has_code, result_list)
    def mark_as_answered(self, the_user_dict):
        if self.is_mandatory or self.mandatory_code is not None:
            the_user_dict['_internal']['answered'].add(self.name)
    def sub_fields_used(self):
        all_fields_used = set()
        for var_name in self.fields_used:
            all_fields_used.add(var_name)
        if len(self.fields) > 0 and hasattr(self.fields[0], 'choices'):
            for choice in self.fields[0].choices:
                if isinstance(choice['key'], Question):
                    all_fields_used.update(choice['key'].sub_fields_used())
        return all_fields_used
    def extended_question_name(self, the_user_dict):
        if not self.name:
            return self.name
        the_name = self.name
        uses = set()
        for var_name in self.sub_fields_used():
            if re.search(r'^x\b', var_name):
                uses.add('x')
            for iterator in re.findall(r'\[([ijklmn])\]', var_name):
                uses.add(iterator)
        if len(uses) > 0:
            ok_to_use_extra = True
            for var_name in uses:
                if var_name not in the_user_dict:
                    ok_to_use_extra = False
            if ok_to_use_extra and 'x' in uses and not hasattr(the_user_dict['x'], 'instanceName'):
                ok_to_use_extra = False
            if ok_to_use_extra:
                extras = []
                if 'x' in uses:
                    extras.append(the_user_dict['x'].instanceName)
                for var_name in ['i', 'j', 'k', 'l', 'm', 'n']:
                    if var_name in uses:
                        extras.append(str(the_user_dict[var_name]))
                the_name += "|WITH|" + '|'.join(extras)
        return the_name
    def follow_multiple_choice(self, the_user_dict, interview_status, is_generic, the_x, iterators):
        if not self.embeds:
            return(self)
        if is_generic:
            if the_x != 'None':
                exec("x = " + the_x, the_user_dict)
        if len(iterators):
            for indexno in range(len(iterators)):
                exec(list_of_indices[indexno] + " = " + iterators[indexno], the_user_dict)
        the_name = self.extended_question_name(the_user_dict)
        if the_name and the_name in the_user_dict['_internal']['answers']:
            interview_status.followed_mc = True
            interview_status.tentatively_answered.add(self)
            qtarget = self.fields[0].choices[the_user_dict['_internal']['answers'][the_name]].get('key', False)
            if isinstance(qtarget, Question):
                return(qtarget.follow_multiple_choice(the_user_dict, interview_status, is_generic, the_x, iterators))
        return(self)
    def finalize_attachment(self, attachment, result, the_user_dict):
        if self.interview.cache_documents and attachment['variable_name']:
            try:
                existing_object = eval(attachment['variable_name'], the_user_dict)
                for doc_format in ('pdf', 'rtf', 'docx', 'rtf to docx', 'tex', 'html', 'raw'):
                    if hasattr(existing_object, doc_format):
                        the_file = getattr(existing_object, doc_format)
                        for key in ('extension', 'mimetype', 'content', 'markdown', 'raw'):
                            if hasattr(the_file, key):
                                result[key][doc_format] = getattr(the_file, key)
                        if hasattr(the_file, 'number'):
                            result['file'][doc_format] = the_file.number
                #logmessage("finalize_attachment: returning " + attachment['variable_name'] + " from cache")
                for key in ('template', 'field_data', 'images', 'data_strings', 'convert_to_pdf_a', 'convert_to_tagged_pdf', 'password', 'template_password', 'update_references', 'permissions'):
                    if key in result:
                        del result[key]
                return result
            except:
                pass
            #logmessage("finalize_attachment: " + attachment['variable_name'] + " was not in cache")
        #logmessage("In finalize where redact is " + repr(result['redact']))
        docassemble.base.functions.this_thread.misc['redact'] = result['redact']
        if 'language' in attachment['options']:
            old_language = docassemble.base.functions.get_language()
            docassemble.base.functions.set_language(attachment['options']['language'])
        else:
            old_language = None
        try:
            for doc_format in result['formats_to_use']:
                if doc_format == 'raw':
                    the_temp = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=result['raw'], delete=False)
                    with open(the_temp.name, 'w', encoding='utf-8') as the_file:
                        the_file.write(result['markdown'][doc_format].lstrip("\n"))
                    result['file'][doc_format], result['extension'][doc_format], result['mimetype'][doc_format] = docassemble.base.functions.server.save_numbered_file(result['filename'] + result['raw'], the_temp.name, yaml_file_name=self.interview.source.path)
                    result['content'][doc_format] = result['markdown'][doc_format].lstrip("\n")
                elif doc_format in ('pdf', 'rtf', 'rtf to docx', 'tex', 'docx'):
                    if 'fields' in attachment['options']:
                        if doc_format == 'pdf' and 'pdf_template_file' in attachment['options']:
                            if 'checkbox_export_value' in attachment['options']:
                                default_export_value = attachment['options']['checkbox_export_value'].text(the_user_dict).strip()
                            else:
                                default_export_value = None
                            docassemble.base.functions.set_context('pdf')
                            the_pdf_file = docassemble.base.pdftk.fill_template(attachment['options']['pdf_template_file'].path(the_user_dict=the_user_dict), data_strings=result['data_strings'], images=result['images'], editable=result['editable'], pdfa=result['convert_to_pdf_a'], password=result['password'], template_password=result['template_password'], default_export_value=default_export_value)
                            result['file'][doc_format], result['extension'][doc_format], result['mimetype'][doc_format] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.' + extension_of_doc_format[doc_format], the_pdf_file, yaml_file_name=self.interview.source.path)
                            for key in ('images', 'data_strings', 'convert_to_pdf_a', 'convert_to_tagged_pdf', 'password', 'template_password', 'update_references', 'permissions'):
                                if key in result:
                                    del result[key]
                            docassemble.base.functions.reset_context()
                        elif (doc_format == 'docx' or (doc_format == 'pdf' and 'docx' not in result['formats_to_use'])) and 'docx_template_file' in attachment['options']:
                            #logmessage("field_data is " + repr(result['field_data']))
                            if result['template'].current_rendering_part is None:
                                result['template'].current_rendering_part = result['template'].docx._part
                            docassemble.base.functions.set_context('docx', template=result['template'])
                            docassemble.base.functions.this_thread.misc['docx_subdocs'] = []
                            try:
                                the_template = result['template']
                                template_loop_count = 0
                                while True: # Rerender if there's a subdoc using include_docx_template
                                    old_count = docassemble.base.functions.this_thread.misc.get('docx_include_count', 0)
                                    the_template.render(result['field_data'], jinja_env=custom_jinja_env())
                                    if docassemble.base.functions.this_thread.misc.get('docx_include_count', 0) > old_count and template_loop_count < 10:
                                        # There's another template included
                                        new_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
                                        the_template.save(new_template_file.name) # Save and refresh the template
                                        the_template = docassemble.base.file_docx.DocxTemplate(new_template_file.name)
                                        if result['hyperlink_style'] and result['hyperlink_style'] in the_template.docx.styles:
                                            the_template.da_hyperlink_style = result['hyperlink_style']
                                        elif 'Hyperlink' in result['template'].docx.styles:
                                            the_template.da_hyperlink_style = 'Hyperlink'
                                        elif 'InternetLink' in result['template'].docx.styles:
                                            the_template.da_hyperlink_style = 'InternetLink'
                                        else:
                                            the_template.da_hyperlink_style = None
                                        docassemble.base.functions.this_thread.misc['docx_template'] = the_template
                                        template_loop_count += 1
                                    else:
                                        break
                                # Copy over images, etc from subdoc to master template
                                subdocs = docassemble.base.functions.this_thread.misc.get('docx_subdocs', []) # Get the subdoc file list
                                the_template_docx = the_template.docx
                                for subdoc in subdocs:
                                    docassemble.base.file_docx.fix_subdoc(the_template_docx, subdoc)

                            except TemplateError as the_error:
                                if (not hasattr(the_error, 'filename')) or the_error.filename is None:
                                    docx_paths = []
                                    for item in attachment['options']['docx_template_file']:
                                        for subitem in item.paths(the_user_dict=the_user_dict):
                                            docx_paths.append(os.path.basename(subitem))
                                    the_error.filename = ', '.join(docx_paths)
                                #logmessage("TemplateError:\n" + traceback.format_exc())
                                raise the_error
                            docassemble.base.functions.reset_context()
                            docx_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
                            the_template.save(docx_file.name)
                            if result['update_references']:
                                docassemble.base.pandoc.update_references(docx_file.name)
                            if 'docx' in result['formats_to_use']:
                                result['file']['docx'], result['extension']['docx'], result['mimetype']['docx'] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.docx', docx_file.name, yaml_file_name=self.interview.source.path)
                            if 'pdf' in result['formats_to_use']:
                                pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
                                docassemble.base.pandoc.word_to_pdf(docx_file.name, 'docx', pdf_file.name, pdfa=result['convert_to_pdf_a'], password=result['password'], update_refs=result['update_references'], tagged=result['convert_to_tagged_pdf'], filename=result['filename'])
                                result['file']['pdf'], result['extension']['pdf'], result['mimetype']['pdf'] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.pdf', pdf_file.name, yaml_file_name=self.interview.source.path)
                            for key in ['template', 'field_data', 'images', 'data_strings', 'convert_to_pdf_a', 'convert_to_tagged_pdf', 'password', 'template_password', 'update_references', 'permissions']:
                                if key in result:
                                    del result[key]
                    else:
                        converter = MyPandoc(pdfa=result['convert_to_pdf_a'], password=result['password'])
                        converter.output_format = doc_format
                        converter.input_content = result['markdown'][doc_format]
                        if 'initial_yaml' in attachment['options']:
                            converter.initial_yaml = [x.path(the_user_dict=the_user_dict) for x in attachment['options']['initial_yaml']]
                        elif 'initial_yaml' in self.interview.attachment_options:
                            converter.initial_yaml = [x.path(the_user_dict=the_user_dict) for x in self.interview.attachment_options['initial_yaml']]
                        if 'additional_yaml' in attachment['options']:
                            converter.additional_yaml = [x.path(the_user_dict=the_user_dict) for x in attachment['options']['additional_yaml']]
                        elif 'additional_yaml' in self.interview.attachment_options:
                            converter.additional_yaml = [x.path(the_user_dict=the_user_dict) for x in self.interview.attachment_options['additional_yaml']]
                        if doc_format in ('rtf', 'rtf to docx'):
                            if 'rtf_template_file' in attachment['options']:
                                converter.template_file = attachment['options']['rtf_template_file'].path(the_user_dict=the_user_dict)
                            elif 'rtf_template_file' in self.interview.attachment_options:
                                converter.template_file = self.interview.attachment_options['rtf_template_file'].path(the_user_dict=the_user_dict)
                        elif doc_format == 'docx':
                            if 'docx_reference_file' in attachment['options']:
                                converter.reference_file = attachment['options']['docx_reference_file'].path(the_user_dict=the_user_dict)
                            elif 'docx_reference_file' in self.interview.attachment_options:
                                converter.reference_file = self.interview.attachment_options['docx_reference_file'].path(the_user_dict=the_user_dict)
                        else:
                            if 'template_file' in attachment['options']:
                                converter.template_file = attachment['options']['template_file'].path(the_user_dict=the_user_dict)
                            elif 'template_file' in self.interview.attachment_options:
                                converter.template_file = self.interview.attachment_options['template_file'].path(the_user_dict=the_user_dict)
                        converter.metadata = result['metadata']
                        converter.convert(self)
                        result['file'][doc_format], result['extension'][doc_format], result['mimetype'][doc_format] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.' + extension_of_doc_format[doc_format], converter.output_filename, yaml_file_name=self.interview.source.path)
                        result['content'][doc_format] = result['markdown'][doc_format]
                elif doc_format in ['html']:
                    result['content'][doc_format] = docassemble.base.filter.markdown_to_html(result['markdown'][doc_format], use_pandoc=True, question=self)
            if attachment['variable_name']:
                string = "import docassemble.base.core"
                exec(string, the_user_dict)
                variable_name = attachment['variable_name']
                m = re.search(r'^(.*)\.([A-Za-z0-9\_]+)$', attachment['variable_name'])
                if m:
                    base_var = m.group(1)
                    attrib = m.group(2)
                    the_var = eval(base_var, the_user_dict)
                    if hasattr(the_var, 'instanceName'):
                        variable_name = the_var.instanceName + '.' + attrib
                string = variable_name + " = docassemble.base.core.DAFileCollection(" + repr(variable_name) + ")"
                # logmessage("Executing " + string + "\n")
                exec(string, the_user_dict)
                the_name = attachment['name'].text(the_user_dict).strip()
                the_filename = attachment['filename'].text(the_user_dict).strip()
                if the_filename == '':
                    the_filename = docassemble.base.functions.space_to_underscore(the_name)
                the_user_dict['_attachment_info'] = dict(name=the_name, filename=the_filename, description=attachment['description'].text(the_user_dict), valid_formats=result['valid_formats'], formats=result['formats_to_use'], attachment=dict(name=attachment['question_name'], number=attachment['indexno']), extension=result.get('extension', dict()), mimetype=result.get('mimetype', dict()), content=result.get('content', dict()), markdown=result.get('markdown', dict()), metadata=result.get('metadata', dict()), convert_to_pdf_a=result.get('convert_to_pdf_a', False), convert_to_tagged_pdf=result.get('convert_to_tagged_pdf', False), orig_variable_name=result.get('orig_variable_name', None), raw=result['raw'], permissions=result.get('permissions', None))
                exec(variable_name + '.info = _attachment_info', the_user_dict)
                del the_user_dict['_attachment_info']
                for doc_format in result['file']:
                    if doc_format == 'raw':
                        variable_string = variable_name + '.raw'
                    else:
                        variable_string = variable_name + '.' + extension_of_doc_format[doc_format]
                    # filename = result['filename'] + '.' + doc_format
                    # file_number, extension, mimetype = docassemble.base.functions.server.save_numbered_file(filename, result['file'][doc_format], yaml_file_name=self.interview.source.path)
                    if result['file'][doc_format] is None:
                        raise Exception("Could not save numbered file")
                    if 'content' in result and doc_format in result['content']:
                        content_string = ', content=' + repr(result['content'][doc_format])
                    else:
                        content_string = ''
                    if 'markdown' in result and doc_format in result['markdown']:
                        markdown_string = ', markdown=' + repr(result['markdown'][doc_format])
                    else:
                        markdown_string = ''
                    if result['raw']:
                        the_ext = result['raw']
                    else:
                        the_ext = '.' + extension_of_doc_format[doc_format]
                    string = variable_string + " = docassemble.base.core.DAFile(" + repr(variable_string) + ", filename=" + repr(str(result['filename']) + the_ext) + ", number=" + str(result['file'][doc_format]) + ", mimetype='" + str(result['mimetype'][doc_format]) + "', extension='" + str(result['extension'][doc_format]) + "'" + content_string + markdown_string + ")"
                    #logmessage("Executing " + string + "\n")
                    exec(string, the_user_dict)
                for doc_format in result['content']:
                    # logmessage("Considering " + doc_format)
                    if doc_format not in result['file']:
                        variable_string = variable_name + '.' + extension_of_doc_format[doc_format]
                        # logmessage("Setting " + variable_string)
                        string = variable_string + " = docassemble.base.core.DAFile(" + repr(variable_string) + ', markdown=' + repr(result['markdown'][doc_format]) + ', content=' + repr(result['content'][doc_format]) + ")"
                        exec(string, the_user_dict)
                if 'permissions' in result:
                    if result['permissions']['private'] is not None or result['permissions']['persistent'] is not None:
                        params = list()
                        if 'private' in result['permissions']:
                            params.append('private=' + repr(result['permissions']['private']))
                        if 'persistent' in result['permissions']:
                            params.append('persistent=' + repr(result['permissions']['persistent']))
                        string = variable_name + '.set_attributes(' + ','.join(params) + ')'
                        exec(string, the_user_dict)
                    if len(result['permissions']['allow users']):
                        string = variable_name + '.user_access(' + ', '.join([repr(y) for y in result['permissions']['allow users']]) + ')'
                        exec(string, the_user_dict)
                    if len(result['permissions']['allow privileges']):
                        string = variable_name + '.privilege_access(' + ', '.join([repr(y) for y in result['permissions']['allow privileges']]) + ')'
                        exec(string, the_user_dict)
        except:
            if old_language is not None:
                docassemble.base.functions.set_language(old_language)
            raise
        if old_language is not None:
            docassemble.base.functions.set_language(old_language)
        return(result)
    def prepare_attachment(self, attachment, the_user_dict, **kwargs):
        if 'language' in attachment['options']:
            old_language = docassemble.base.functions.get_language()
            docassemble.base.functions.set_language(attachment['options']['language'])
        else:
            old_language = None
        try:
            the_name = attachment['name'].text(the_user_dict).strip()
            the_filename = attachment['filename'].text(the_user_dict).strip()
            the_filename = docassemble.base.functions.secure_filename(the_filename)
            if the_filename == '':
                the_filename = docassemble.base.functions.secure_filename(docassemble.base.functions.space_to_underscore(the_name))
            result = {'name': the_name, 'filename': the_filename, 'description': attachment['description'].text(the_user_dict), 'valid_formats': attachment['valid_formats']}
            actual_extension = attachment['raw']
            if attachment['content'] is None and 'content file code' in attachment['options']:
                raw_content = ''
                the_filenames = eval(attachment['options']['content file code'], the_user_dict)
                if not isinstance(the_filenames, list):
                    if hasattr(the_filenames, 'instanceName') and hasattr(the_filenames, 'elements') and isinstance(the_filenames.elements, list):
                        the_filenames = the_filenames.elements
                    else:
                        the_filenames = [the_filenames]
                for the_filename in the_filenames:
                    the_orig_filename = the_filename
                    if the_filename.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DAStaticFile'):
                        the_filename = the_filename.path()
                    elif isinstance(the_filename, str):
                        if re.search(r'^https?://', str(the_filename)):
                            temp_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
                            try:
                                urlretrieve(url_sanitize(str(the_filename)), temp_template_file.name)
                            except Exception as err:
                                raise DAError("prepare_attachment: error downloading " + str(the_filename) + ": " + str(err))
                            the_filename = temp_template_file.name
                        else:
                            the_filename = docassemble.base.functions.package_template_filename(the_filename, package=self.package)
                    else:
                        the_filename = None
                    if the_filename is None or not os.path.isfile(the_filename):
                        raise DAError("prepare_attachment: error obtaining template file from code: " + repr(the_orig_filename))
                    (the_base, actual_extension) = os.path.splitext(the_filename)
                    with open(the_filename, 'r', encoding='utf-8') as the_file:
                        raw_content += the_file.read()
                the_content = TextObject(raw_content, question=self)
            else:
                the_content = attachment['content']
            if 'redact' in attachment['options']:
                if isinstance(attachment['options']['redact'], CodeType):
                    result['redact'] = eval(attachment['options']['redact'], the_user_dict)
                else:
                    result['redact'] = attachment['options']['redact']
            else:
                result['redact'] = True
            if 'editable' in attachment['options']:
                result['editable'] = eval(attachment['options']['editable'], the_user_dict)
            else:
                result['editable'] = True
            docassemble.base.functions.this_thread.misc['redact'] = result['redact']
            result['markdown'] = dict();
            result['content'] = dict();
            result['extension'] = dict();
            result['mimetype'] = dict();
            result['file'] = dict();
            if attachment['raw']:
                result['raw'] = actual_extension
                result['formats_to_use'] = ['raw']
            else:
                result['raw'] = False
                if '*' in attachment['valid_formats']:
                    result['formats_to_use'] = ['pdf', 'rtf', 'html']
                else:
                    result['formats_to_use'] = attachment['valid_formats']
            result['metadata'] = dict()
            if len(attachment['metadata']) > 0:
                for key in attachment['metadata']:
                    data = attachment['metadata'][key]
                    if isinstance(data, bool):
                        result['metadata'][key] = data
                    elif isinstance(data, list):
                        result['metadata'][key] = textify(data, the_user_dict)
                    else:
                        result['metadata'][key] = data.text(the_user_dict)
            if 'pdf_a' in attachment['options']:
                if isinstance(attachment['options']['pdf_a'], bool):
                    result['convert_to_pdf_a'] = attachment['options']['pdf_a']
                else:
                    result['convert_to_pdf_a'] = eval(attachment['options']['pdf_a'], the_user_dict)
            else:
                result['convert_to_pdf_a'] = self.interview.use_pdf_a
            if 'hyperlink_style' in attachment['options']:
                result['hyperlink_style'] = attachment['options']['hyperlink_style'].text(the_user_dict).strip()
            else:
                result['hyperlink_style'] = None
            result['permissions'] = dict()
            if 'persistent' in attachment['options']:
                if isinstance(attachment['options']['persistent'], bool):
                    result['permissions']['persistent'] = attachment['options']['persistent']
                else:
                    result['permissions']['persistent'] = eval(attachment['options']['persistent'], the_user_dict)
            else:
                result['permissions']['persistent'] = None
            if 'private' in attachment['options']:
                if isinstance(attachment['options']['private'], bool):
                    result['permissions']['private'] = attachment['options']['private']
                else:
                    result['permissions']['private'] = eval(attachment['options']['private'], the_user_dict)
            else:
                result['permissions']['private'] = None
            if 'allow users' in attachment['options']:
                if isinstance(attachment['options']['allow users'], list):
                    result['permissions']['allow users'] = allow_users_list(attachment['options']['allow users'])
                else:
                    result['permissions']['allow users'] = eval(attachment['options']['allow users'], the_user_dict)
                result['permissions']['allow users'] = allow_users_list(result['permissions']['allow users'])
            else:
                result['permissions']['allow users'] = []
            if 'allow privileges' in attachment['options']:
                if isinstance(attachment['options']['allow privileges'], list):
                    result['permissions']['allow privileges'] = allow_privileges_list(attachment['options']['allow privileges'])
                else:
                    result['permissions']['allow privileges'] = allow_privileges_list(eval(attachment['options']['allow privileges'], the_user_dict))
            else:
                result['permissions']['allow privileges'] = []
            if 'tagged_pdf' in attachment['options']:
                if isinstance(attachment['options']['tagged_pdf'], bool):
                    result['convert_to_tagged_pdf'] = attachment['options']['tagged_pdf']
                else:
                    result['convert_to_tagged_pdf'] = eval(attachment['options']['tagged_pdf'], the_user_dict)
            else:
                result['convert_to_tagged_pdf'] = self.interview.use_tagged_pdf
            if 'orig_variable_name' in attachment and attachment['orig_variable_name']:
                result['orig_variable_name'] = attachment['orig_variable_name']
            if 'update_references' in attachment['options']:
                if isinstance(attachment['options']['update_references'], bool):
                    result['update_references'] = attachment['options']['update_references']
                else:
                    result['update_references'] = eval(attachment['options']['update_references'], the_user_dict)
            else:
                result['update_references'] = False
            if 'password' in attachment['options']:
                result['password'] = attachment['options']['password'].text(the_user_dict)
            else:
                result['password'] = None
            if 'template_password' in attachment['options']:
                result['template_password'] = attachment['options']['template_password'].text(the_user_dict)
            else:
                result['template_password'] = None
            for doc_format in result['formats_to_use']:
                if doc_format in ['pdf', 'rtf', 'rtf to docx', 'tex', 'docx', 'raw']:
                    if 'decimal_places' in attachment['options']:
                        try:
                            float_formatter = '%.' + str(int(attachment['options']['decimal_places'].text(the_user_dict).strip())) + 'f'
                        except:
                            logmessage("prepare_attachment: error in float_formatter")
                            float_formatter = None
                    else:
                        float_formatter = None
                    if 'fields' in attachment['options'] and 'docx_template_file' in attachment['options']:
                        if doc_format == 'docx' or ('docx' not in result['formats_to_use'] and doc_format == 'pdf'):
                            docx_paths = []
                            for docx_reference in attachment['options']['docx_template_file']:
                                for docx_path in docx_reference.paths(the_user_dict=the_user_dict):
                                    if not os.path.isfile(docx_path):
                                        raise DAError("Missing docx template file " + os.path.basename(docx_path))
                                    docx_paths.append(docx_path)
                            if len(docx_paths) == 1:
                                docx_path = docx_paths[0]
                            else:
                                docx_path = docassemble.base.file_docx.concatenate_files(docx_paths)
                            result['template'] = docassemble.base.file_docx.DocxTemplate(docx_path)
                            if result['hyperlink_style'] and result['hyperlink_style'] in result['template'].docx.styles:
                                result['template'].da_hyperlink_style = result['hyperlink_style']
                            elif 'Hyperlink' in result['template'].docx.styles:
                                result['template'].da_hyperlink_style = 'Hyperlink'
                            elif 'InternetLink' in result['template'].docx.styles:
                                result['template'].da_hyperlink_style = 'InternetLink'
                            else:
                                result['template'].da_hyperlink_style = None
                            if result['template'].current_rendering_part is None:
                                result['template'].current_rendering_part = result['template'].docx._part
                            docassemble.base.functions.set_context('docx', template=result['template'])
                            if isinstance(attachment['options']['fields'], str):
                                result['field_data'] = the_user_dict
                            else:
                                the_field_data = recursive_eval_textobject(attachment['options']['fields'], the_user_dict, self, result['template'], attachment['options']['skip_undefined'])
                                new_field_data = dict()
                                if isinstance(the_field_data, list):
                                    for item in the_field_data:
                                        if isinstance(item, dict):
                                            new_field_data.update(item)
                                    the_field_data = new_field_data
                                result['field_data'] = copy.deepcopy(pickleable_objects(the_user_dict))
                                self.interview.populate_non_pickleable(result['field_data'])
                                if 'alpha' not in result['field_data']:
                                    raise Exception("fuck this")
                                result['field_data'].update(the_field_data)
                            result['field_data']['_codecs'] = codecs
                            result['field_data']['_array'] = array
                            if 'code' in attachment['options']:
                                if attachment['options']['skip_undefined']:
                                    try:
                                        additional_dict = eval(attachment['options']['code'], the_user_dict)
                                    except:
                                        additional_dict = {}
                                else:
                                    additional_dict = eval(attachment['options']['code'], the_user_dict)
                                if isinstance(additional_dict, dict):
                                    for key, val in additional_dict.items():
                                        if isinstance(val, float) and float_formatter is not None:
                                            result['field_data'][key] = float_formatter % val
                                        elif isinstance(val, RawValue):
                                            result['field_data'][key] = val.value
                                        else:
                                            result['field_data'][key] = docassemble.base.file_docx.transform_for_docx(val, self, result['template'])
                                else:
                                    raise DAError("code in an attachment returned something other than a dictionary")
                            if 'raw code dict' in attachment['options']:
                                for varname, var_code in attachment['options']['raw code dict'].items():
                                    if attachment['options']['skip_undefined']:
                                        try:
                                            val = eval(var_code, the_user_dict)
                                        except:
                                            val = ''
                                    else:
                                        val = eval(var_code, the_user_dict)
                                    if isinstance(val, float) and float_formatter is not None:
                                        result['field_data'][varname] = float_formatter % val
                                    else:
                                        result['field_data'][varname] = val
                            if 'code dict' in attachment['options']:
                                for varname, var_code in attachment['options']['code dict'].items():
                                    if attachment['options']['skip_undefined']:
                                        try:
                                            val = eval(var_code, the_user_dict)
                                        except:
                                            val = ''
                                    else:
                                        val = eval(var_code, the_user_dict)
                                    if isinstance(val, float) and float_formatter is not None:
                                        result['field_data'][varname] = float_formatter % val
                                    elif isinstance(val, RawValue):
                                        result['field_data'][varname] = val.value
                                    else:
                                        result['field_data'][varname] = docassemble.base.file_docx.transform_for_docx(val, self, result['template'])
                            docassemble.base.functions.reset_context()
                    elif doc_format == 'pdf' and 'fields' in attachment['options'] and 'pdf_template_file' in attachment['options']:
                        docassemble.base.functions.set_context('pdf')
                        result['data_strings'] = []
                        result['images'] = []
                        if isinstance(attachment['options']['fields'], dict):
                            the_fields = [attachment['options']['fields']]
                        else:
                            the_fields = attachment['options']['fields']
                        for item in the_fields:
                            for key, val in item.items():
                                if attachment['options']['skip_undefined']:
                                    try:
                                        answer = val.text(the_user_dict).rstrip()
                                    except:
                                        answer = ''
                                else:
                                    answer = val.text(the_user_dict).rstrip()
                                if answer == 'True':
                                    answer = 'Yes'
                                elif answer == 'False':
                                    answer = 'No'
                                elif answer == 'None':
                                    answer = ''
                                answer = re.sub(r'\[(NEWLINE|BR)\]', r'\n', answer)
                                answer = re.sub(r'\[(BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|BOLDCENTER|CENTER)\]', r'', answer)
                                #logmessage("Found a " + str(key) + " with a |" + str(answer) + '|')
                                m = re.search(r'\[FILE ([^\]]+)\]', answer)
                                if m:
                                    file_reference = re.sub(r'[ ,].*', '', m.group(1))
                                    file_info = docassemble.base.functions.server.file_finder(file_reference, convert={'svg': 'png'})
                                    result['images'].append((key, file_info))
                                else:
                                    m = re.search(r'\[QR ([^\]]+)\]', answer)
                                    if m:
                                        im = qrcode.make(re.sub(r' *,.*', '', m.group(1)))
                                        the_image = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".png", delete=False)
                                        im.save(the_image.name)
                                        result['images'].append((key, {'fullpath': the_image.name}))
                                    else:
                                        result['data_strings'].append((key, answer))
                        if 'code' in attachment['options']:
                            if attachment['options']['skip_undefined']:
                                try:
                                    additional_fields = eval(attachment['options']['code'], the_user_dict)
                                except:
                                    additional_fields = []
                            else:
                                additional_fields = eval(attachment['options']['code'], the_user_dict)
                            if not isinstance(additional_fields, list):
                                additional_fields = [additional_fields]
                            for item in additional_fields:
                                if not isinstance(item, dict):
                                    raise DAError("code in an attachment returned something other than a dictionary or a list of dictionaries")
                                for key, val in item.items():
                                    if val is True:
                                        val = 'Yes'
                                    elif val is False:
                                        val = 'No'
                                    elif val is None:
                                        val = ''
                                    elif isinstance(val, float) and float_formatter is not None:
                                        val = float_formatter % val
                                    else:
                                        val = str(val)
                                    val = re.sub(r'\s*\[(NEWLINE|BR)\]\s*', r'\n', val)
                                    val = re.sub(r'\s*\[(BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|BOLDCENTER|CENTER)\]\s*', r'', val)
                                    m = re.search(r'\[FILE ([^\]]+)\]', val)
                                    if m:
                                        file_reference = re.sub(r'[ ,].*', '', m.group(1))
                                        file_info = docassemble.base.functions.server.file_finder(file_reference, convert={'svg': 'png'})
                                        result['images'].append((key, file_info))
                                    else:
                                        result['data_strings'].append((key, val))
                        if 'code dict' in attachment['options']:
                            additional_fields = attachment['options']['code dict']
                            if not isinstance(additional_fields, list):
                                additional_fields = [additional_fields]
                            for item in additional_fields:
                                if not isinstance(item, dict):
                                    raise DAError("code dict in an attachment returned something other than a dictionary or a list of dictionaries")
                                for key, var_code in item.items():
                                    if attachment['options']['skip_undefined']:
                                        try:
                                            val = eval(var_code, the_user_dict)
                                        except:
                                            val = ''
                                    else:
                                        val = eval(var_code, the_user_dict)
                                    if val is True:
                                        val = 'Yes'
                                    elif val is False:
                                        val = 'No'
                                    elif val is None:
                                        val = ''
                                    elif isinstance(val, float) and float_formatter is not None:
                                        val = float_formatter % val
                                    else:
                                        val = str(val)
                                    val = re.sub(r'\[(NEWLINE|BR)\]', r'\n', val)
                                    val = re.sub(r'\[(BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|BOLDCENTER|CENTER)\]', r'', val)
                                    m = re.search(r'\[FILE ([^\]]+)\]', val)
                                    if m:
                                        file_reference = re.sub(r'[ ,].*', '', m.group(1))
                                        file_info = docassemble.base.functions.server.file_finder(file_reference, convert={'svg': 'png'})
                                        result['images'].append((key, file_info))
                                    else:
                                        result['data_strings'].append((key, val))
                        if 'raw code dict' in attachment['options']:
                            additional_fields = attachment['options']['raw code dict']
                            if not isinstance(additional_fields, list):
                                additional_fields = [additional_fields]
                            for item in additional_fields:
                                if not isinstance(item, dict):
                                    raise DAError("raw code dict in an attachment returned something other than a dictionary or a list of dictionaries")
                                for key, var_code in item.items():
                                    if attachment['options']['skip_undefined']:
                                        try:
                                            val = eval(var_code, the_user_dict)
                                        except:
                                            val = ''
                                    else:
                                        val = eval(var_code, the_user_dict)
                                    if val is True:
                                        val = 'Yes'
                                    elif val is False:
                                        val = 'No'
                                    elif isinstance(val, float) and float_formatter is not None:
                                        val = float_formatter % val
                                    elif val is None:
                                        val = ''
                                    val = re.sub(r'\[(NEWLINE|BR)\]', r'\n', val)
                                    val = re.sub(r'\[(BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|BOLDCENTER|CENTER)\]', r'', val)
                                    m = re.search(r'\[FILE ([^\]]+)\]', val)
                                    if m:
                                        file_reference = re.sub(r'[ ,].*', '', m.group(1))
                                        file_info = docassemble.base.functions.server.file_finder(file_reference, convert={'svg': 'png'})
                                        result['images'].append((key, file_info))
                                    else:
                                        result['data_strings'].append((key, val))
                        docassemble.base.functions.reset_context()
                    elif doc_format == 'raw':
                        docassemble.base.functions.set_context('raw')
                        the_markdown = the_content.text(the_user_dict)
                        result['markdown'][doc_format] = the_markdown
                        docassemble.base.functions.reset_context()
                    else:
                        the_markdown = ""
                        if len(result['metadata']):
                            modified_metadata = dict()
                            for key, data in result['metadata'].items():
                                if re.search(r'Footer|Header', key) and 'Lines' not in key:
                                    #modified_metadata[key] = docassemble.base.filter.metadata_filter(data, doc_format) + str('[END]')
                                    modified_metadata[key] = data + str('[END]')
                                else:
                                    modified_metadata[key] = data
                            the_markdown += '---\n' + codecs.decode(bytearray(yaml.safe_dump(modified_metadata, default_flow_style=False, default_style = '|', allow_unicode=False), encoding='utf-8'), 'utf-8') + "...\n"
                        docassemble.base.functions.set_context('pandoc')
                        the_markdown += the_content.text(the_user_dict)
                        #logmessage("Markdown is:\n" + repr(the_markdown) + "END")
                        if emoji_match.search(the_markdown) and len(self.interview.images) > 0:
                            the_markdown = emoji_match.sub(emoji_matcher_insert(self), the_markdown)
                        result['markdown'][doc_format] = the_markdown
                        docassemble.base.functions.reset_context()
                elif doc_format in ['html']:
                    result['markdown'][doc_format] = the_content.text(the_user_dict)
                    if emoji_match.search(result['markdown'][doc_format]) and len(self.interview.images) > 0:
                        result['markdown'][doc_format] = emoji_match.sub(emoji_matcher_html(self), result['markdown'][doc_format])
                    #logmessage("output was:\n" + repr(result['content'][doc_format]))
        except:
            if old_language is not None:
                docassemble.base.functions.set_language(old_language)
            raise
        if old_language is not None:
            docassemble.base.functions.set_language(old_language)
        return(result)
    def process_selections_manual(self, data):
        result = []
        if isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    the_item = dict()
                    for key in entry:
                        if len(entry) > 1:
                            if key in ['default', 'help', 'image']:
                                continue
                            if 'key' in entry and 'label' in entry and key != 'key':
                                continue
                            if 'default' in entry:
                                the_item['default'] = entry['default']
                            if 'help' in entry:
                                the_item['help'] = TextObject(entry['help'], question=self)
                            if 'image' in entry:
                                if entry['image'].__class__.__name__ == 'DAFile':
                                    entry['image'].retrieve()
                                    if entry['image'].mimetype is not None and entry['image'].mimetype.startswith('image'):
                                        the_item['image'] = dict(type='url', value=entry['image'].url_for())
                                elif entry['image'].__class__.__name__ == 'DAFileList':
                                    entry['image'][0].retrieve()
                                    if entry['image'][0].mimetype is not None and entry['image'][0].mimetype.startswith('image'):
                                        the_item['image'] = dict(type='url', value=entry['image'][0].url_for())
                                elif entry['image'].__class__.__name__ == 'DAStaticFile':
                                    the_item['image'] = dict(type='url', value=entry['image'].url_for())
                                else:
                                    the_item['image'] = dict(type='decoration', value=entry['image'])
                            if 'key' in entry and 'label' in entry:
                                the_item['key'] = TextObject(entry['key'], question=self, translate=False)
                                the_item['label'] = TextObject(entry['label'], question=self)
                                result.append(the_item)
                                continue
                        the_item['key'] = TextObject(entry[key], question=self, translate=False)
                        the_item['label'] = TextObject(key, question=self)
                        result.append(the_item)
                if isinstance(entry, (list, tuple)):
                    result.append(dict(key=TextObject(entry[0], question=self), label=TextObject(entry[1], question=self)))
                elif isinstance(entry, str):
                    result.append(dict(key=TextObject(entry, question=self), label=TextObject(entry, question=self)))
                elif isinstance(entry, (int, float, bool, NoneType)):
                    result.append(dict(key=TextObject(str(entry), question=self), label=TextObject(str(entry), question=self)))
        elif isinstance(data, dict):
            for key, value in sorted(data.items(), key=operator.itemgetter(1)):
                result.append(dict(key=TextObject(value, question=self), label=TextObject(key, question=self)))
        else:
            raise DAError("Unknown data type in manual choices selection: " + re.sub(r'[<>]', '', repr(data)))
        return(result)

def emoji_matcher_insert(obj):
    return (lambda x: docassemble.base.filter.emoji_insert(x.group(1), images=obj.interview.images))

def emoji_matcher_html(obj):
    return (lambda x: docassemble.base.filter.emoji_html(x.group(1), images=obj.interview.images))

def interview_source_from_string(path, **kwargs):
    if path is None:
        raise DAError("Passed None to interview_source_from_string")
    #sys.stderr.write("Trying to find " + path + "\n")
    for the_filename in [docassemble.base.functions.package_question_filename(path), docassemble.base.functions.standard_question_filename(path), docassemble.base.functions.server.absolute_filename(path)]:
        #sys.stderr.write("Trying " + str(the_filename) + " with path " + str(path) + "\n")
        if the_filename is not None:
            new_source = InterviewSourceFile(filepath=the_filename, path=path)
            if new_source.update():
                return(new_source)
    raise DANotFoundError("Interview " + str(path) + " not found")

def is_boolean(field_data):
    if 'choices' not in field_data:
        return False
    if 'has_code' in field_data:
        return False
    for entry in field_data['choices']:
        if 'key' in entry and 'label' in entry:
            if isinstance(entry['key'], TextObject):
                if not isinstance(entry['key'].original_text, bool):
                    return False
            else:
                if not isinstance(entry['key'], bool):
                    return False
    return True

def is_threestate(field_data):
    if 'choices' not in field_data:
        return False
    if 'has_code' in field_data:
        return False
    for entry in field_data['choices']:
        if 'key' in entry and 'label' in entry:
            if isinstance(entry['key'], TextObject):
                if not (isinstance(entry['key'].original_text, (bool, NoneType)) or (isinstance(entry['key'].original_text, str) and entry['key'].original_text == 'None')):
                    return False
            else:
                if not (isinstance(entry['key'], (bool, NoneType)) or (isinstance(entry['key'], str) and entry['key'].original_text == 'None')):
                    return False
    return True

class TableInfo:
    pass

def recursive_update(base, target):
    for key, val in target.items():
        if isinstance(val, abc.Mapping):
            base[key] = recursive_update(base.get(key, {}), val)
        else:
            base[key] = val
    return base

def recursive_add_classes(class_list, the_class):
    for cl in the_class.__bases__:
        class_list.append(cl.__name__)
        recursive_add_classes(class_list, cl)

def unqualified_name(variable, the_user_dict):
    if variable == 'x' or variable.startswith('x[') or variable.startswith('x.') and 'x' in the_user_dict and hasattr(the_user_dict['x'], 'instanceName'):
        variable = re.sub(r'^x', the_user_dict['x'].instanceName, variable)
    for index_var in ['i', 'j', 'k', 'l', 'm', 'n']:
        if '[' + index_var + ']' in variable and index_var in the_user_dict:
            variable = re.sub(r'\[' + index_var + '\]', '[' + repr(the_user_dict[index_var]) + ']', variable)
    return variable

def make_backup_vars(the_user_dict):
    backups = dict()
    for var in ['x', 'i', 'j', 'k', 'l', 'm', 'n']:
        if var in the_user_dict:
            backups[var] = the_user_dict[var]
    return backups

def restore_backup_vars(the_user_dict, backups):
    for var, val in backups.items():
        the_user_dict[var] = val

def illegal_variable_name(var):
    if re.search(r'[\n\r]', var):
        return True
    try:
        t = ast.parse(var)
    except:
        return True
    detector = docassemble.base.astparser.detectIllegal()
    detector.visit(t)
    return detector.illegal

class Interview:
    def __init__(self, **kwargs):
        self.source = None
        self.questions = dict()
        self.generic_questions = dict()
        self.questions_by_id = dict()
        self.questions_by_name = dict()
        self.questions_list = list()
        self.all_questions = list()
        self.progress_points = set()
        self.ids_in_use = set()
        self.id_orderings = list()
        self.invalidation = dict()
        self.invalidation_todo = dict()
        self.onchange = dict()
        self.onchange_todo = dict()
        self.orderings = list()
        self.orderings_by_question = dict()
        self.images = dict()
        self.metadata = list()
        self.helptext = dict()
        self.defs = dict()
        self.terms = dict()
        self.mlfields = dict()
        self.autoterms = dict()
        self.includes = set()
        self.reconsider = set()
        self.reconsider_generic = dict()
        self.question_index = 0
        self.block_index = 0
        self.translating = False
        self.default_role = None
        self.default_validation_messages = dict()
        self.default_screen_parts = dict()
        self.title = None
        self.debug = get_config('debug', True)
        self.use_progress_bar = False
        self.question_back_button = False
        self.question_help_button = False
        self.navigation_back_button = True
        self.force_fullscreen = False
        self.use_pdf_a = get_config('pdf/a', False)
        self.use_tagged_pdf = get_config('tagged pdf', False)
        self.loop_limit = get_config('loop limit', 500)
        self.recursion_limit = get_config('recursion limit', 500)
        self.cache_documents = True
        self.use_navigation = False
        self.use_navigation_on_small_screens = True
        self.flush_left = False
        self.max_image_size = get_config('maximum image size', None)
        self.image_type = get_config('image upload type', None)
        self.bootstrap_theme = get_config('bootstrap theme', None)
        self.sections = dict()
        self.names_used = set()
        self.attachment_options = dict()
        self.attachment_index = 0
        self.external_files = dict()
        self.options = dict()
        self.calls_process_action = False
        self.uses_action = False
        self.imports_util = False
        self.table_width = 65
        self.success = True
        self.translation_dict = dict()
        self.translations = list()
        self.scan_for_emojis = False
        self.consolidated_metadata = dict()
        self.issue = dict()
        if 'source' in kwargs:
            self.read_from(kwargs['source'])
            self.cross_reference_dependencies()
    def cross_reference_dependencies(self):
        to_listen_for = set(self.invalidation.keys()).union(set(self.onchange.keys()))
        todo = dict()
        for question in self.questions_list:
            for field_name in question.fields_used.union(question.other_fields_used):
                totry = list()
                variants = list()
                level_dict = dict()
                generic_dict = dict()
                expression_as_list = [x for x in match_brackets_or_dot.split(field_name) if x != '']
                expression_as_list.append('')
                recurse_indices(expression_as_list, list_of_indices, [], variants, level_dict, [], generic_dict, [])
                for variant in variants:
                    if variant in to_listen_for:
                        totry.append({'real': field_name, 'vari': variant, 'iterators': level_dict[variant], 'generic': generic_dict[variant], 'is_generic': 0 if generic_dict[variant] == '' else 1, 'num_dots': variant.count('.'), 'num_iterators': variant.count('[')})
                totry = sorted(sorted(sorted(sorted(totry, key=lambda x: len(x['iterators'])), key=lambda x: x['num_iterators'], reverse=True), key=lambda x: x['num_dots'], reverse=True), key=lambda x: x['is_generic'])
                for attempt in totry:
                    if field_name not in todo:
                        todo[field_name] = []
                    found = False
                    for existing_item in todo[field_name]:
                        if attempt['vari'] == existing_item['vari']:
                            found = True
                    if not found:
                        todo[field_name].append(attempt)
                    if attempt['vari'] in self.invalidation:
                        for var in self.invalidation[attempt['vari']]:
                            if field_name not in self.invalidation_todo:
                                self.invalidation_todo[field_name] = []
                            if not found:
                                self.invalidation_todo[field_name].append({'target': var, 'context': attempt})
                            question.fields_for_invalidation.add(field_name)
                    if attempt['vari'] in self.onchange:
                        if field_name not in self.onchange_todo:
                            self.onchange_todo[field_name] = []
                        if not found:
                            self.onchange_todo[field_name].append({'target': self.onchange[attempt['vari']], 'context': attempt})
                        question.fields_for_onchange.add(field_name)
    def ordered(self, the_list):
        if len(the_list) <= 1:
            return the_list
    def invalidate_dependencies(self, field_name, the_user_dict, old_values):
        try:
            current_value = eval(field_name, the_user_dict)
        except:
            return
        try:
            if current_value == old_values[field_name]:
                return
            do_invalidation = True
        except:
            do_invalidation = False
        if do_invalidation:
            if field_name in self.invalidation_todo:
                for info in self.invalidation_todo[field_name]:
                    unqualified_variable = info['target']
                    if info['context']['is_generic'] or len(info['context']['iterators']) > 0:
                        if info['context']['is_generic']:
                            unqualified_variable = re.sub('^x', info['context']['generic'], info['target'])
                        for index_num, index_var in enumerate(['i', 'j', 'k', 'l', 'm', 'n']):
                            if index_num >= len(info['context']['iterators']):
                                break
                            unqualified_variable = re.sub(r'\[' + index_var + '\]', '[' + info['context']['iterators'][index_num] + ']', unqualified_variable)
                    unqualified_variable = unqualified_name(unqualified_variable, the_user_dict)
                    try:
                        exec("_internal['dirty'][" + repr(unqualified_variable) + "] = " + unqualified_variable, the_user_dict)
                    except:
                        continue
                    try:
                        exec("del " + unqualified_variable, the_user_dict)
                        #logmessage("Interview.invalidate_dependencies: deleted " + unqualified_variable)
                    except:
                        pass
        if field_name in self.onchange_todo:
            if 'alpha' not in the_user_dict:
                self.load_util(the_user_dict)
            for info in self.onchange_todo[field_name]:
                if info['context']['is_generic'] or len(info['context']['iterators']) > 0:
                    backup_vars = make_backup_vars(the_user_dict)
                    if info['context']['is_generic']:
                        try:
                            the_user_dict['x'] = eval(info['context']['generic'], the_user_dict)
                        except:
                            restore_backup_vars(the_user_dict, backup_vars)
                            continue
                    failed = False
                    for index_num, index_var in enumerate(['i', 'j', 'k', 'l', 'm', 'n']):
                        if index_num >= len(info['context']['iterators']):
                            break
                        if index_var == info['context']['iterators'][index_num]:
                            continue
                        try:
                            the_user_dict[index_var] = eval(info['context']['iterators'][index_num], the_user_dict)
                        except:
                            failed = True
                            break
                    if failed:
                        restore_backup_vars(the_user_dict, backup_vars)
                        continue
                else:
                    backup_vars = None
                for code_to_run in info['target']:
                    try:
                        exec(code_to_run, the_user_dict)
                    except Exception as err:
                        logmessage("Exception raised by on change code: " + err.__class__.__name__ + ": " + str(err))
                if backup_vars:
                    restore_backup_vars(the_user_dict, backup_vars)
    def get_ml_store(self):
        if hasattr(self, 'ml_store'):
            return self.ml_store
        else:
            return self.standard_ml_store()
    def set_ml_store(self, ml_store):
        self.ml_store = ml_store
    def standard_ml_store(self):
        if self.source is None:
            ml_store = None
        else:
            ml_store = self.source.get_package()
        if ml_store is None:
            ml_store = ''
        else:
            ml_store += ':data/sources/'
        if self.source and self.source.path is not None:
            ml_store += 'ml-' + re.sub(r'\..*', '', re.sub(r'.*[/:]', '', self.source.path)) + '.json'
        else:
            ml_store += 'ml-default.json'
        return ml_store
    def get_bootstrap_theme(self):
        if self.bootstrap_theme is None:
            return None
        result = docassemble.base.functions.server.url_finder(self.bootstrap_theme, _package=self.source.package)
        return result
    def get_tags(self, the_user_dict):
        if 'tags' in the_user_dict['_internal']:
            return the_user_dict['_internal']['tags']
        else:
            tags = set()
            for metadata in self.metadata:
                if 'tags' in metadata and isinstance(metadata['tags'], list):
                    for tag in metadata['tags']:
                        tags.add(tag)
            return tags
    def get_title(self, the_user_dict, status=None, converter=None):
        if converter is None:
            converter = lambda y: y
        mapping = (('title', 'full'), ('logo', 'logo'), ('short title', 'short'), ('tab title', 'tab'), ('subtitle', 'sub'), ('exit link', 'exit link'), ('exit label', 'exit label'), ('exit url', 'exit url'), ('submit', 'submit'), ('pre', 'pre'), ('post', 'post'), ('footer', 'footer'), ('continue button label', 'continue button label'), ('resume button label', 'resume button label'), ('back button label', 'back button label'), ('corner back button label', 'corner back button label'), ('under', 'under'), ('right', 'right'), ('logo', 'logo'), ('css class', 'css class'), ('table css class', 'table css class'), ('date format', 'date format'), ('time format', 'time format'), ('datetime format', 'datetime format'), ('title url', 'title url'), ('title url opens in other window', 'title url opens in other window'))
        title = dict()
        for title_name, title_abb in mapping:
            if '_internal' in the_user_dict and title_name in the_user_dict['_internal'] and the_user_dict['_internal'][title_name] is not None:
                title[title_abb] = str(the_user_dict['_internal'][title_name]).strip()
            elif status is not None and (title_name + ' text') in status.extras and status.extras[title_name + ' text'] is not None:
                if title_name in ('exit link', 'exit url', ('title url', 'title url'), ('title url opens in other window', 'title url opens in other window')):
                    title[title_abb] = status.extras[title_name + ' text']
                else:
                    title[title_abb] = converter(status.extras[title_name + ' text'], title_name)
                the_user_dict['_internal'][title_name + ' default'] = title[title_abb]
            elif status is None and (title_name + ' default') in the_user_dict['_internal'] and the_user_dict['_internal'][title_name + ' default'] is not None:
                title[title_abb] = the_user_dict['_internal'][title_name + ' default']
        base_lang = get_language()
        if base_lang in self.default_title:
            for key, val in self.default_title[base_lang].items():
                if key not in title:
                    title[key] = val
        if '*' in self.default_title:
            for key, val in self.default_title['*'].items():
                if key not in title:
                    title[key] = val
        return title
    def allowed_to_access(self, is_anonymous=False, has_roles=None):
        if isinstance(has_roles, list) and len(has_roles) == 0:
            has_roles = ['user']
        roles = set()
        for metadata in self.metadata:
            if 'required privileges' in metadata:
                roles = set()
                privs = metadata['required privileges']
                if isinstance(privs, list) or (hasattr(privs, 'instanceName') and hasattr(privs, 'elements') and isinstance(privs.elements, list)):
                    for priv in privs:
                        if isinstance(priv, str):
                            roles.add(priv)
                elif isinstance(privs, str):
                    roles.add(privs)
        if len(roles):
            if is_anonymous:
                if 'anonymous' in roles:
                    return True
                return False
            if has_roles is not None:
                return len(set(roles).intersection(set(has_roles))) > 0
        if is_anonymous:
            require_login = False
            for metadata in self.metadata:
                if 'require login' in metadata:
                    require_login = True if metadata['require login'] else False
            if require_login:
                return False
        return True
    def allowed_to_initiate(self, is_anonymous=False, has_roles=None):
        if isinstance(has_roles, list) and len(has_roles) == 0:
            has_roles = ['user']
        if not self.allowed_to_access(is_anonymous=is_anonymous, has_roles=has_roles):
            return False
        roles = set()
        is_none = False
        for metadata in self.metadata:
            if 'required privileges for initiating' in metadata:
                roles = set()
                is_none = False
                privs = metadata['required privileges for initiating']
                if isinstance(privs, list) or (hasattr(privs, 'instanceName') and hasattr(privs, 'elements') and isinstance(privs.elements, list)):
                    if len(privs) == 0:
                        is_none = True
                    else:
                        for priv in privs:
                            if isinstance(priv, str):
                                roles.add(priv)
                elif isinstance(privs, str):
                    roles.add(privs)
                elif isinstance(privs, NoneType):
                    is_none = True
        if is_none:
            return False
        if len(roles):
            if is_anonymous:
                if 'anonymous' in roles:
                    return True
                return False
            if has_roles is not None:
                return len(set(roles).intersection(set(has_roles))) > 0
        return True
    def allowed_to_see_listed(self, is_anonymous=False, has_roles=None):
        if isinstance(has_roles, list) and len(has_roles) == 0:
            has_roles = ['user']
        if not self.allowed_to_access(is_anonymous=is_anonymous, has_roles=has_roles):
            return False
        roles = set()
        for metadata in self.metadata:
            if 'required privileges for listing' in metadata:
                roles = set()
                privs = metadata['required privileges for listing']
                if isinstance(privs, list) or (hasattr(privs, 'instanceName') and hasattr(privs, 'elements') and isinstance(privs.elements, list)):
                    for priv in privs:
                        if isinstance(priv, str):
                            roles.add(priv)
                elif isinstance(privs, str):
                    roles.add(privs)
        if len(roles):
            if is_anonymous:
                if 'anonymous' in roles:
                    return True
                return False
            if has_roles is not None:
                return len(set(roles).intersection(set(has_roles))) > 0
        if is_anonymous:
            require_login = False
            for metadata in self.metadata:
                if 'require login' in metadata:
                    require_login = True if metadata['require login'] else False
            if require_login:
                return False
        return True
    def is_unlisted(self):
        unlisted = False
        for metadata in self.metadata:
            if 'unlisted' in metadata:
                unlisted = metadata['unlisted']
        return unlisted
    def next_attachment_number(self):
        self.attachment_index += 1
        return(self.attachment_index - 1)
    def next_number(self):
        self.question_index += 1
        return(self.question_index - 1)
    def next_block_number(self):
        self.block_index += 1
        return(self.block_index - 1)
    def read_from(self, source):
        if self.source is None:
            self.source = source
            #self.firstPath = source.path
            #self.rootDirectory = source.directory
        if hasattr(source, 'package') and source.package:
            source_package = source.package
            if source_package.startswith('docassemble.playground'):
                self.debug = True
        else:
            source_package = None
        if hasattr(source, 'path'):
            if source.path in self.includes:
                logmessage("Interview: source " + str(source.path) + " has already been included.  Skipping.")
                return
            self.includes.add(source.path)
        #for document in yaml.safe_load_all(source.content):
        for source_code in document_match.split(source.content):
            source_code = remove_trailing_dots.sub('', source_code)
            source_code = fix_tabs.sub('  ', source_code)
            if source.testing:
                try:
                    #logmessage("Package is " + str(source_package))
                    document = yaml.safe_load(source_code)
                    if document is not None:
                        question = Question(document, self, source=source, package=source_package, source_code=source_code)
                        self.names_used.update(question.fields_used)
                except Exception as errMess:
                    #sys.stderr.write(str(source_code) + "\n")
                    try:
                        logmessage('Interview: error reading YAML file ' + str(source.path) + '\n\nDocument source code was:\n\n---\n' + str(source_code) + '---\n\nError was:\n\n' + str(errMess))
                    except:
                        try:
                            logmessage('Interview: error reading YAML file ' + str(source.path) + '. Error was:\n\n' + str(errMess))
                        except:
                            if isinstance(errMess, yaml.error.MarkedYAMLError):
                                logmessage('Interview: error reading YAML file ' + str(source.path) + '. Error type was:\n\n' + errMess.problem)
                            else:
                                logmessage('Interview: error reading YAML file ' + str(source.path) + '. Error type was:\n\n' + errMess.__class__.__name__)
                    self.success = False
                    pass
            else:
                try:
                    document = yaml.safe_load(source_code)
                except Exception as errMess:
                    self.success = False
                    #sys.stderr.write("Error: " + str(source_code) + "\n")
                    #str(source_code)
                    try:
                        raise DAError('Error reading YAML file ' + str(source.path) + '\n\nDocument source code was:\n\n---\n' + str(source_code) + '---\n\nError was:\n\n' + str(errMess))
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        raise DAError('Error reading YAML file ' + str(source.path) + '\n\nDocument source code was:\n\n---\n' + str(source_code) + '---\n\nError was:\n\n' + str(errMess.__class__.__name__))
                if document is not None:
                    try:
                        question = Question(document, self, source=source, package=source_package, source_code=source_code)
                        self.names_used.update(question.fields_used)
                    except SyntaxException as qError:
                        self.success = False
                        raise Exception("Syntax Exception: " + str(qError) + "\n\nIn file " + str(source.path) + " from package " + str(source_package) + ":\n" + str(source_code))
                    except CompileException as qError:
                        self.success = False
                        raise Exception("Compile Exception: " + str(qError) + "\n\nIn file " + str(source.path) + " from package " + str(source_package) + ":\n" + str(source_code))
                    except SyntaxError as qError:
                        self.success = False
                        raise Exception("Syntax Error: " + str(qError) + "\n\nIn file " + str(source.path) + " from package " + str(source_package) + ":\n" + str(source_code))
        for ordering in self.id_orderings:
            if ordering['type'] == 'supersedes' and hasattr(ordering['question'], 'number'):
                new_list = [ordering['question'].number]
                for question_id in ordering['supersedes']:
                    if question_id in self.questions_by_id:
                        new_list.append(self.questions_by_id[question_id].number)
                    else:
                        logmessage("warning: reference in a supersedes directive to an id " + question_id + " that does not exist in interview")
            elif ordering['type'] == 'order':
                new_list = list()
                for question_id in ordering['order']:
                    if question_id in self.questions_by_id and hasattr(self.questions_by_id[question_id], 'number'):
                        new_list.append(self.questions_by_id[question_id].number)
                    else:
                        logmessage("warning: reference in an order directive to id " + question_id + " that does not exist in interview")
            else:
                new_list = list()
            self.orderings.append(new_list)
        for ordering in self.orderings:
            for question_a in ordering:
                mode = 1
                for question_b in ordering:
                    if question_a == question_b:
                        mode = -1
                        continue
                    if question_b not in self.orderings_by_question:
                        self.orderings_by_question[question_b] = dict()
                    self.orderings_by_question[question_b][question_a] = mode
        #logmessage(repr(self.orderings_by_question))
        self.sorter = self.make_sorter()
        if len(self.images) > 0 or get_config('default icons', 'font awesome') in ('material icons', 'font awesome'):
            self.scan_for_emojis = True
        for metadata in self.metadata:
            if 'social' in metadata and isinstance(metadata['social'], dict):
                if 'image' in metadata['social'] and isinstance(metadata['social']['image'], str):
                    metadata['social']['image'] = docassemble.base.functions.server.url_finder(metadata['social']['image'], _package=metadata['_origin_package'], _external=True)
                    if metadata['social']['image'] is None:
                        logmessage("Invalid image reference in social meta tags")
                        del metadata['social']['image']
                for key, subkey in (('og', 'image'), ('twitter', 'image')):
                    if key in metadata['social'] and isinstance(metadata['social'][key], dict) and subkey in metadata['social'][key] and isinstance(metadata['social'][key][subkey], str):
                        metadata['social'][key][subkey] = docassemble.base.functions.server.url_finder(metadata['social'][key][subkey], _package=metadata['_origin_package'], _external=True)
                        if metadata['social'][key][subkey] is None:
                            logmessage("Invalid image reference in social meta tags")
                            del metadata['social'][key][subkey]
                for key, val in metadata['social'].items():
                    if isinstance(val, dict):
                        for subkey, subval in val.items():
                            if isinstance(subval, str):
                                metadata['social'][key][subkey] = subval.replace('\n', ' ').replace('"', '&quot;').strip()
                    elif isinstance(val, str):
                        metadata['social'][key] = val.replace('\n', ' ').replace('"', '&quot;').strip()
            for key, val in metadata.items():
                if key in self.consolidated_metadata and isinstance(self.consolidated_metadata[key], dict) and isinstance(val, dict):
                    recursive_update(self.consolidated_metadata[key], val)
                else:
                    self.consolidated_metadata[key] = val
        mapping = (('title', 'full'), ('logo', 'logo'), ('short title', 'short'), ('tab title', 'tab'), ('subtitle', 'sub'), ('exit link', 'exit link'), ('exit label', 'exit label'), ('exit url', 'exit url'), ('submit', 'submit'), ('pre', 'pre'), ('post', 'post'), ('footer', 'footer'), ('help label', 'help label'), ('continue button label', 'continue button label'), ('resume button label', 'resume button label'), ('back button label', 'back button label'), ('corner back button label', 'corner back button label'), ('right', 'right'), ('under', 'under'), ('submit', 'submit'), ('css class', 'css class'), ('table css class', 'table css class'), ('date format', 'date format'), ('time format', 'time format'), ('datetime format', 'datetime format'), ('title url', 'title url'), ('title url opens in other window', 'title url opens in other window'))
        self.default_title = {'*': dict()}
        for metadata in self.metadata:
            for title_name, title_abb in mapping:
                if metadata.get(title_name, None) is not None:
                    if isinstance(metadata[title_name], dict):
                        for lang, val in metadata[title_name].items():
                            if lang not in self.default_title:
                                self.default_title[lang] = dict()
                            self.default_title[lang][title_abb] = str(val).strip()
                    else:
                        self.default_title['*'][title_abb] = str(metadata[title_name]).strip()
        for lang, parts in docassemble.base.functions.server.main_page_parts.items():
            if lang not in self.default_title:
                self.default_title[lang] = dict()
            for title_name, title_abb in mapping:
                if title_abb in self.default_title[lang]:
                    continue
                if parts.get('main page ' + title_name, '') != '':
                    self.default_title[lang][title_abb] = parts['main page ' + title_name].strip()
    def make_sorter(self):
        lookup_dict = self.orderings_by_question
        class K:
            def __init__(self, obj, *args):
                self.obj = obj.number
                self.lookup = lookup_dict
            def __lt__(self, other):
                if self.obj == other.obj:
                    return False
                if self.obj in self.lookup and other.obj in self.lookup[self.obj] and self.lookup[self.obj][other.obj] == -1:
                    return True
                return False
            def __gt__(self, other):
                if self.obj == other.obj:
                    return False
                if self.obj in self.lookup and other.obj in self.lookup[self.obj] and self.lookup[self.obj][other.obj] == 1:
                    return True
                return False
            def __eq__(self, other):
                if self.obj == other.obj or self.obj not in self.lookup or other.obj not in self.lookup:
                    return True
                return False
            def __le__(self, other):
                if self.obj == other.obj or self.obj not in self.lookup or other.obj not in self.lookup:
                    return True
                if self.lookup[self.obj][other.obj] == -1:
                    return True
                return False
            def __ge__(self, other):
                if self.obj == other.obj or self.obj not in self.lookup or other.obj not in self.lookup:
                    return True
                if self.lookup[self.obj][other.obj] == 1:
                    return True
                return False
            def __ne__(self, other):
                if self.obj == other.obj or self.obj not in self.lookup or other.obj not in self.lookup:
                    return False
                return True
        return K
    def sort_with_orderings(self, the_list):
        if len(the_list) <= 1:
            return the_list
        result = sorted(the_list, key=self.sorter)
        # logmessage(repr([y for y in reversed([x.number for x in result])]))
        return reversed(result)
    def processed_helptext(self, the_user_dict, language):
        result = list()
        if language in self.helptext:
            for source in self.helptext[language]:
                help_item = dict()
                help_item['from'] = source['from']
                if source['label'] is None:
                    help_item['label'] = None
                else:
                    help_item['label'] = source['label'].text(the_user_dict)
                if source['heading'] is None:
                    help_item['heading'] = None
                else:
                    help_item['heading'] = source['heading'].text(the_user_dict)
                if source['audiovideo'] is None:
                    help_item['audiovideo'] = None
                else:
                    help_item['audiovideo'] = process_audio_video_list(source['audiovideo'], the_user_dict)
                help_item['content'] = source['content'].text(the_user_dict)
                result.append(help_item)
        return result
    def populate_non_pickleable(self, user_dict_copy):
        if not self.imports_util and not self.consolidated_metadata.get('suppress loading util', False):
            exec(import_util, user_dict_copy)
        for question in self.questions_list:
            if question.question_type == 'imports':
                for module_name in question.module_list:
                    if module_name.startswith('.'):
                        exec('import ' + str(question.package) + module_name, user_dict_copy)
                    else:
                        exec('import ' + module_name, user_dict_copy)
            if question.question_type == 'modules':
                for module_name in question.module_list:
                    if module_name.startswith('.'):
                        exec('from ' + str(question.package) + module_name + ' import *', user_dict_copy)
                    else:
                        exec('from ' + module_name + ' import *', user_dict_copy)
    def assemble(self, user_dict, interview_status=None, old_user_dict=None, force_question=None):
        #sys.stderr.write("assemble\n")
        user_dict['_internal']['tracker'] += 1
        if interview_status is None:
            interview_status = InterviewStatus()
        #if interview_status.current_info['url'] is not None:
        #    user_dict['_internal']['url'] = interview_status.current_info['url']
        interview_status.set_tracker(user_dict['_internal']['tracker'])
        #docassemble.base.functions.reset_local_variables()
        interview_status.current_info.update({'default_role': self.default_role})
        docassemble.base.functions.this_thread.misc['reconsidered'] = set()
        docassemble.base.functions.this_thread.current_package = self.source.package
        docassemble.base.functions.this_thread.current_info = interview_status.current_info
        docassemble.base.functions.this_thread.interview = self
        docassemble.base.functions.this_thread.interview_status = interview_status
        docassemble.base.functions.this_thread.internal = user_dict['_internal']
        if user_dict['nav'].sections is None:
            user_dict['nav'].sections = self.sections
            if hasattr(self, 'sections_progressive'):
                user_dict['nav'].progressive = self.sections_progressive
            if hasattr(self, 'sections_auto_open'):
                user_dict['nav'].auto_open = self.sections_auto_open
        for question in self.questions_list:
            if question.question_type == 'imports':
                for module_name in question.module_list:
                    if module_name.startswith('.'):
                        exec('import ' + str(question.package) + module_name, user_dict)
                    else:
                        exec('import ' + module_name, user_dict)
            if question.question_type == 'modules':
                for module_name in question.module_list:
                    if module_name.startswith('.'):
                        exec('from ' + str(question.package) + module_name + ' import *', user_dict)
                    else:
                        exec('from ' + module_name + ' import *', user_dict)
            if question.question_type == 'reset':
                for var in question.reset_list:
                    if complications.search(var):
                        try:
                            exec('del ' + str(var), user_dict)
                        except:
                            pass
                    elif var in user_dict:
                        del user_dict[var]
        if 'x' in user_dict and user_dict['x'].__class__.__name__ in self.reconsider_generic:
            for var in self.reconsider_generic[user_dict['x'].__class__.__name__]:
                try:
                    exec('del ' + str(var), user_dict)
                except:
                    pass
        for var in self.reconsider:
            if complications.search(var):
                try:
                    exec('del ' + str(var), user_dict)
                except:
                    pass
            elif var in user_dict:
                del user_dict[var]
        session_uid = interview_status.current_info['user']['session_uid']
        device_id = interview_status.current_info['user']['device_id']
        user_id = str(interview_status.current_info['user']['the_user_id'])
        if 'session_local' not in user_dict['_internal']: ### take out after a time
            user_dict['_internal']['session_local'] = dict()
            user_dict['_internal']['device_local'] = dict()
            user_dict['_internal']['user_local'] = dict()
        if session_uid not in user_dict['_internal']['session_local'] or device_id not in user_dict['_internal']['device_local'] or user_id not in user_dict['_internal']['user_local']:
            exec('import docassemble.base.core')
            if session_uid not in user_dict['_internal']['session_local']:
                user_dict['_internal']['session_local'][session_uid] = eval("docassemble.base.core.DASessionLocal()")
            if device_id not in user_dict['_internal']['device_local']:
                user_dict['_internal']['device_local'][device_id] = eval("docassemble.base.core.DADeviceLocal()")
            if user_id not in user_dict['_internal']['user_local']:
                user_dict['_internal']['user_local'][user_id] = eval("docassemble.base.core.DAUserLocal()")
        user_dict['session_local'] = user_dict['_internal']['session_local'][session_uid]
        user_dict['device_local'] = user_dict['_internal']['device_local'][device_id]
        user_dict['user_local'] = user_dict['_internal']['user_local'][user_id]
        number_loops = 0
        variables_sought = set()
        try:
            while True:
                number_loops += 1
                if number_loops > self.loop_limit:
                    docassemble.base.functions.wrap_up(user_dict)
                    raise DAError("There appears to be a circularity.  Variables involved: " + ", ".join(variables_sought) + ".")
                docassemble.base.functions.reset_gathering_mode()
                if 'action' in interview_status.current_info:
                    #logmessage("assemble: there is an action in the current_info: " + repr(interview_status.current_info['action']))
                    if interview_status.current_info['action'] in ('_da_list_remove', '_da_list_add', '_da_list_complete'):
                        for the_key in ('list', 'item', 'items'):
                            if the_key in interview_status.current_info['arguments']:
                                if illegal_variable_name(interview_status.current_info['arguments'][the_key]):
                                    raise DAError("Invalid name " + interview_status.current_info['arguments'][the_key])
                                interview_status.current_info['action_' + the_key] = eval(interview_status.current_info['arguments'][the_key], user_dict)
                    if interview_status.current_info['action'] in ('_da_dict_remove', '_da_dict_add', '_da_dict_complete'):
                        for the_key in ('dict', 'item', 'items'):
                            if the_key in interview_status.current_info['arguments']:
                                if illegal_variable_name(interview_status.current_info['arguments'][the_key]):
                                    raise DAError("Invalid name " + interview_status.current_info['arguments'][the_key])
                                interview_status.current_info['action_' + the_key] = eval(interview_status.current_info['arguments'][the_key], user_dict)
                #else:
                #    logmessage("assemble: there is no action in the current_info")
                try:
                    if not self.imports_util:
                        if self.consolidated_metadata.get('suppress loading util', False):
                            exec(import_process_action, user_dict)
                        elif 'alpha' not in user_dict:
                            exec(import_util, user_dict)
                    if force_question is not None:
                        if self.debug:
                            interview_status.seeking.append({'question': question, 'reason': 'multiple choice question', 'time': time.time()})
                        docassemble.base.functions.this_thread.current_question = force_question
                        interview_status.populate(force_question.ask(user_dict, old_user_dict, 'None', [], None, None))
                        raise MandatoryQuestion()
                    if not self.calls_process_action:
                        exec(run_process_action, user_dict)
                    for question in self.questions_list:
                        if question.question_type == 'code' and (question.is_initial or (question.initial_code is not None and eval(question.initial_code, user_dict))):
                            #logmessage("Running some initial code:\n\n" + question.sourcecode)
                            if self.debug:
                                interview_status.seeking.append({'question': question, 'reason': 'initial', 'time': time.time()})
                            docassemble.base.functions.this_thread.current_question = question
                            exec_with_trap(question, user_dict)
                            continue
                        if question.name and question.name in user_dict['_internal']['answered']:
                            #logmessage("Skipping " + question.name + " because answered")
                            continue
                        if question.question_type in ("objects_from_file", "objects_from_file_da"):
                            if self.debug:
                                interview_status.seeking.append({'question': question, 'reason': 'objects from file', 'time': time.time()})
                            if question.question_type == "objects_from_file_da":
                                use_objects = True
                            else:
                                use_objects = False
                            for keyvalue in question.objects_from_file:
                                for variable, the_file in keyvalue.items():
                                    exec(import_core, user_dict)
                                    command = variable + ' = docassemble.base.core.objects_from_file("' + str(the_file) + '", name=' + repr(variable) + ', use_objects=' + repr(use_objects) + ', package=' + repr(question.package) + ')'
                                    #logmessage("Running " + command)
                                    exec(command, user_dict)
                            question.mark_as_answered(user_dict)
                        if question.is_mandatory or (question.mandatory_code is not None and eval(question.mandatory_code, user_dict)):
                            if question.question_type == "data":
                                if self.debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'data', 'time': time.time()})
                                string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_dataobject(question.fields[0].data, user_dict))
                                exec(string, user_dict)
                                question.mark_as_answered(user_dict)
                            if question.question_type == "data_da":
                                if self.debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'data', 'time': time.time()})
                                exec(import_core, user_dict)
                                string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.objects_from_structure(' + repr(recursive_eval_dataobject(question.fields[0].data, user_dict)) + ', root=' + repr(from_safeid(question.fields[0].saveas)) + ')'
                                exec(string, user_dict)
                                question.mark_as_answered(user_dict)
                            if question.question_type == "data_from_code":
                                if self.debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'data', 'time': time.time()})
                                string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_data_from_code(question.fields[0].data, user_dict))
                                exec(string, user_dict)
                                question.mark_as_answered(user_dict)
                            if question.question_type == "data_from_code_da":
                                if self.debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'data', 'time': time.time()})
                                exec(import_core, user_dict)
                                string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.objects_from_structure(' + repr(recursive_eval_data_from_code(question.fields[0].data, user_dict)) + ', root=' + repr(from_safeid(question.fields[0].saveas)) + ')'
                                exec(string, user_dict)
                                question.mark_as_answered(user_dict)
                            if question.question_type == "objects":
                                if self.debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'objects', 'time': time.time()})
                                #logmessage("Going into objects")
                                docassemble.base.functions.this_thread.current_question = question
                                for keyvalue in question.objects:
                                    for variable in keyvalue:
                                        object_type_name = keyvalue[variable]
                                        user_dict["__object_type"] = eval(object_type_name, user_dict)
                                        if False and re.search(r"\.", variable):
                                            m = re.search(r"(.*)\.(.*)", variable)
                                            variable = m.group(1)
                                            attribute = m.group(2)
                                            command = variable + ".initializeAttribute(" + repr(attribute) + ", __object_type)"
                                            #command = variable + "." + attribute + " = " + object_type + "()"
                                            #logmessage("Running " + command)
                                            exec(command, user_dict)
                                        else:
                                            if user_dict["__object_type"].__class__.__name__ == 'DAObjectPlusParameters':
                                                command = variable + ' = __object_type.object_type(' + repr(variable) + ', **__object_type.parameters)'
                                            else:
                                                command = variable + ' = __object_type(' + repr(variable) + ')'
                                            # command = variable + ' = ' + object_type + '(' + repr(variable) + ')'
                                            #logmessage("Running " + command)
                                            exec(command, user_dict)
                                        if "__object_type" in user_dict:
                                            del user_dict["__object_type"]
                                question.mark_as_answered(user_dict)
                            if question.question_type == 'code':
                                if self.debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'mandatory code', 'time': time.time()})
                                #logmessage("Running some code:\n\n" + question.sourcecode)
                                #logmessage("Question name is " + question.name)
                                docassemble.base.functions.this_thread.current_question = question
                                exec_with_trap(question, user_dict)
                                #logmessage("Code completed")
                                if question.name:
                                    user_dict['_internal']['answered'].add(question.name)
                                    #logmessage("Question " + str(question.name) + " marked as answered")
                            elif hasattr(question, 'content') and question.name:
                                if self.debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'mandatory question', 'time': time.time()})
                                if question.name and question.name in user_dict['_internal']['answers']:
                                    the_question = question.follow_multiple_choice(user_dict, interview_status, False, 'None', [])
                                    if self.debug and the_question is not question:
                                        interview_status.seeking.append({'question': the_question, 'reason': 'result of multiple choice', 'time': time.time()})
                                    if the_question.question_type in ["code", "event_code"]:
                                        docassemble.base.functions.this_thread.current_question = the_question
                                        exec_with_trap(the_question, user_dict)
                                        interview_status.mark_tentative_as_answered(user_dict)
                                        continue
                                    elif hasattr(the_question, 'content'):
                                        interview_status.populate(the_question.ask(user_dict, old_user_dict, 'None', [], None, None))
                                        interview_status.mark_tentative_as_answered(user_dict)
                                    else:
                                        raise DAError("An embedded question can only be a code block or a regular question block.  The question type was " + getattr(the_question, 'question_type', 'unknown'))
                                else:
                                    interview_status.populate(question.ask(user_dict, old_user_dict, 'None', [], None, None))
                                if interview_status.question.question_type == 'continue':
                                    user_dict['_internal']['answered'].add(question.name)
                                else:
                                    raise MandatoryQuestion()
                except ForcedReRun as the_exception:
                    continue
                except (NameError, DAAttributeError, DAIndexError) as the_exception:
                    if 'pending_error' in docassemble.base.functions.this_thread.misc:
                        del docassemble.base.functions.this_thread.misc['pending_error']
                    #logmessage("Error in " + the_exception.__class__.__name__ + " is " + str(the_exception))
                    if self.debug and docassemble.base.functions.this_thread.evaluation_context == 'docx':
                        logmessage("NameError exception during document assembly: " + str(the_exception))
                    docassemble.base.functions.reset_context()
                    seeking_question = False
                    if isinstance(the_exception, ForcedNameError):
                        #logmessage("assemble: got a ForcedNameError for " + str(the_exception.name))
                        follow_mc = False
                        seeking_question = True
                        #logmessage("next action is " + repr(the_exception.next_action))
                        if the_exception.next_action is not None and not interview_status.checkin:
                            if 'event_stack' not in user_dict['_internal']:
                                user_dict['_internal']['event_stack'] = dict()
                            if session_uid not in user_dict['_internal']['event_stack']:
                                user_dict['_internal']['event_stack'][session_uid] = list()
                            new_items = list()
                            for new_item in the_exception.next_action:
                                already_there = False
                                for event_item in user_dict['_internal']['event_stack'][session_uid]:
                                    if (isinstance(new_item, dict) and event_item['action'] == new_item['action']) or (isinstance(new_item, str) and event_item['action'] == new_item):
                                        already_there = True
                                        break
                                if not already_there:
                                    new_items.append(new_item)
                            if len(new_items):
                                user_dict['_internal']['event_stack'][session_uid] = new_items + user_dict['_internal']['event_stack'][session_uid]
                            #interview_status.next_action.extend(the_exception.next_action)
                            if the_exception.name.startswith('_da_'):
                                continue
                            docassemble.base.functions.this_thread.misc['forgive_missing_question'] = [the_exception.name]
                        if the_exception.arguments is not None:
                            docassemble.base.functions.this_thread.current_info.update(dict(action=the_exception.name, arguments=the_exception.arguments))
                        missingVariable = the_exception.name
                    else:
                        follow_mc = True
                        missingVariable = extract_missing_name(the_exception)
                    variables_sought.add(missingVariable)
                    question_result = self.askfor(missingVariable, user_dict, old_user_dict, interview_status, seeking=interview_status.seeking, follow_mc=follow_mc, seeking_question=seeking_question)
                    if question_result['type'] in ('continue', 're_run'):
                        continue
                    elif question_result['type'] == 'refresh':
                        pass
                    else:
                        interview_status.populate(question_result)
                        break
                except UndefinedError as the_exception:
                    #logmessage("UndefinedError")
                    if self.debug and docassemble.base.functions.this_thread.evaluation_context == 'docx':
                        #logmessage(the_exception.__class__.__name__ + " exception during document assembly: " + str(the_exception) + "\n" + traceback.format_exc())
                        logmessage(the_exception.__class__.__name__ + " exception during document assembly: " + str(the_exception) + "\n")
                    docassemble.base.functions.reset_context()
                    missingVariable = extract_missing_name(the_exception)
                    #logmessage("extracted " + missingVariable)
                    variables_sought.add(missingVariable)
                    question_result = self.askfor(missingVariable, user_dict, old_user_dict, interview_status, seeking=interview_status.seeking, follow_mc=True)
                    if question_result['type'] in ('continue', 're_run'):
                        continue
                    elif question_result['type'] == 'refresh':
                        pass
                    else:
                        interview_status.populate(question_result)
                        break
                except CommandError as qError:
                    #logmessage("CommandError")
                    docassemble.base.functions.reset_context()
                    question_data = dict(command=qError.return_type, url=qError.url, sleep=qError.sleep)
                    new_interview_source = InterviewSourceString(content='')
                    new_interview = new_interview_source.get_interview()
                    reproduce_basics(self, new_interview)
                    new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                    new_question.name = "Question_Temp"
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None, None))
                    break
                except ResponseError as qError:
                    docassemble.base.functions.reset_context()
                    #logmessage("Trapped ResponseError")
                    question_data = dict(extras=dict())
                    if hasattr(qError, 'response') and qError.response is not None:
                        question_data['response'] = qError.response
                    elif hasattr(qError, 'binaryresponse') and qError.binaryresponse is not None:
                        question_data['binaryresponse'] = qError.binaryresponse
                    elif hasattr(qError, 'filename') and qError.filename is not None:
                        question_data['response filename'] = qError.filename
                    elif hasattr(qError, 'url') and qError.url is not None:
                        question_data['redirect url'] = qError.url
                    elif hasattr(qError, 'all_variables') and qError.all_variables:
                        if hasattr(qError, 'include_internal'):
                            question_data['include_internal'] = qError.include_internal
                        question_data['content type'] = 'application/json'
                        question_data['all_variables'] = True
                    elif hasattr(qError, 'nullresponse') and qError.nullresponse:
                        question_data['null response'] = qError.nullresponse
                    elif hasattr(qError, 'sleep') and qError.sleep:
                        question_data['sleep'] = qError.sleep
                    if hasattr(qError, 'content_type') and qError.content_type:
                        question_data['content type'] = qError.content_type
                    if hasattr(qError, 'response_code') and qError.response_code:
                        question_data['response code'] = qError.response_code
                    # new_interview = copy.deepcopy(self)
                    # if self.source is None:
                    #     new_interview_source = InterviewSourceString(content='')
                    # else:
                    #     new_interview_source = self.source
                    new_interview_source = InterviewSourceString(content='')
                    new_interview = new_interview_source.get_interview()
                    reproduce_basics(self, new_interview)
                    new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                    new_question.name = "Question_Temp"
                    #the_question = new_question.follow_multiple_choice(user_dict)
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None, None))
                    break
                except BackgroundResponseError as qError:
                    docassemble.base.functions.reset_context()
                    #logmessage("Trapped BackgroundResponseError")
                    question_data = dict(extras=dict())
                    if hasattr(qError, 'backgroundresponse'):
                        question_data['backgroundresponse'] = qError.backgroundresponse
                    if hasattr(qError, 'sleep'):
                        question_data['sleep'] = qError.sleep
                    new_interview_source = InterviewSourceString(content='')
                    new_interview = new_interview_source.get_interview()
                    reproduce_basics(self, new_interview)
                    new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                    new_question.name = "Question_Temp"
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None, None))
                    break
                except BackgroundResponseActionError as qError:
                    docassemble.base.functions.reset_context()
                    #logmessage("Trapped BackgroundResponseActionError")
                    question_data = dict(extras=dict())
                    if hasattr(qError, 'action'):
                        question_data['action'] = qError.action
                    new_interview_source = InterviewSourceString(content='')
                    new_interview = new_interview_source.get_interview()
                    reproduce_basics(self, new_interview)
                    new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                    new_question.name = "Question_Temp"
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None, None))
                    break
                # except SendFileError as qError:
                #     #logmessage("Trapped SendFileError")
                #     question_data = dict(extras=dict())
                #     if hasattr(qError, 'filename') and qError.filename is not None:
                #         question_data['response filename'] = qError.filename
                #     if hasattr(qError, 'content_type') and qError.content_type:
                #         question_data['content type'] = qError.content_type
                #     new_interview_source = InterviewSourceString(content='')
                #     new_interview = new_interview_source.get_interview()
                #     new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                #     new_question.name = "Question_Temp"
                #     interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None))
                #     break
                except QuestionError as qError:
                    #logmessage("QuestionError")
                    docassemble.base.functions.reset_context()
                    question_data = dict()
                    if qError.question:
                        question_data['question'] = qError.question
                    if qError.subquestion:
                        question_data['subquestion'] = qError.subquestion
                    if qError.reload:
                        question_data['reload'] = qError.reload
                    if qError.dead_end:
                        pass
                    elif qError.buttons:
                        question_data['buttons'] = qError.buttons
                    else:
                        buttons = list()
                        if qError.show_exit is not False and not (qError.show_leave is True and qError.show_exit is None):
                            exit_button = {word('Exit'): 'exit'}
                            if qError.url:
                                exit_button.update(dict(url=qError.url))
                            buttons.append(exit_button)
                        if qError.show_leave:
                            leave_button = {word('Leave'): 'leave'}
                            if qError.url:
                                leave_button.update(dict(url=qError.url))
                            buttons.append(leave_button)
                        if qError.show_restart is not False:
                            buttons.append({word('Restart'): 'restart'})
                        if len(buttons):
                            question_data['buttons'] = buttons
                    new_interview_source = InterviewSourceString(content='')
                    new_interview = new_interview_source.get_interview()
                    reproduce_basics(self, new_interview)
                    new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                    new_question.name = "Question_Temp"
                    new_question.embeds = True
                    # will this be a problem?  Maybe, since the question name can vary by thread.
                    the_question = new_question.follow_multiple_choice(user_dict, interview_status, False, 'None', [])
                    interview_status.populate(the_question.ask(user_dict, old_user_dict, 'None', [], None, None))
                    break
                except AttributeError as the_error:
                    #logmessage("Regular attributeerror")
                    docassemble.base.functions.reset_context()
                    #logmessage(str(the_error.args))
                    docassemble.base.functions.wrap_up(user_dict)
                    raise DAError('Got error ' + str(the_error) + " " + traceback.format_exc() + "\nHistory was " + pprint.pformat(interview_status.seeking))
                except MandatoryQuestion:
                    #logmessage("MandatoryQuestion")
                    docassemble.base.functions.reset_context()
                    break
                except CodeExecute as code_error:
                    #logmessage("CodeExecute")
                    docassemble.base.functions.reset_context()
                    #if self.debug:
                    #    interview_status.seeking.append({'question': question, 'reason': 'mandatory code'})
                    exec(code_error.compute, user_dict)
                    code_error.question.mark_as_answered(user_dict)
                except SyntaxException as qError:
                    #logmessage("SyntaxException")
                    docassemble.base.functions.reset_context()
                    the_question = None
                    try:
                        the_question = question
                    except:
                        pass
                    docassemble.base.functions.wrap_up(user_dict)
                    if the_question is not None:
                        raise DAError(str(qError) + "\n\n" + str(self.idebug(self.data_for_debug)))
                    raise DAError("no question available: " + str(qError))
                except CompileException as qError:
                    #logmessage("CompileException")
                    docassemble.base.functions.reset_context()
                    the_question = None
                    try:
                        the_question = question
                    except:
                        pass
                    docassemble.base.functions.wrap_up(user_dict)
                    if the_question is not None:
                        raise DAError(str(qError) + "\n\n" + str(self.idebug(self.data_for_debug)))
                    raise DAError("no question available: " + str(qError))
                else:
                    docassemble.base.functions.wrap_up(user_dict)
                    raise DAErrorNoEndpoint('Docassemble has finished executing all code blocks marked as initial or mandatory, and finished asking all questions marked as mandatory (if any).  It is a best practice to end your interview with a question that says goodbye and offers an Exit button.')
        except Exception as the_error:
            #logmessage("Untrapped exception")
            if self.debug:
                the_error.interview = self
                the_error.interview_status = interview_status
                the_error.user_dict = docassemble.base.functions.serializable_dict(user_dict)
                if not hasattr(the_error, '__traceback__'):
                    cl, exc, tb = sys.exc_info()
                    the_error.__traceback__ = tb
                    del cl
                    del exc
                    del tb
            raise the_error
        if docassemble.base.functions.this_thread.prevent_going_back:
            interview_status.can_go_back = False
        docassemble.base.functions.wrap_up(user_dict)
        if self.debug:
            interview_status.seeking.append({'done': True, 'time': time.time()})
        #return(pickleable_objects(user_dict))
    def load_util(self, the_user_dict):
        if not self.imports_util:
            if not self.consolidated_metadata.get('suppress loading util', False):
                exec(import_util, the_user_dict)
    def askfor(self, missingVariable, user_dict, old_user_dict, interview_status, **kwargs):
        seeking_question = kwargs.get('seeking_question', False)
        variable_stack = kwargs.get('variable_stack', set())
        questions_tried = kwargs.get('questions_tried', dict())
        recursion_depth = kwargs.get('recursion_depth', 0)
        recursion_depth += 1
        language = get_language()
        current_question = None
        follow_mc = kwargs.get('follow_mc', True)
        seeking = kwargs.get('seeking', list())
        if self.debug:
            seeking.append({'variable': missingVariable, 'time': time.time()})
        if recursion_depth > self.recursion_limit:
            raise DAError("There appears to be an infinite loop.  Variables in stack are " + ", ".join(sorted(variable_stack)) + ".")
        #logmessage("askfor: I don't have " + str(missingVariable) + " for language " + str(language))
        #sys.stderr.write("I don't have " + str(missingVariable) + " for language " + str(language) + "\n")
        origMissingVariable = missingVariable
        docassemble.base.functions.set_current_variable(origMissingVariable)
        # if missingVariable in variable_stack:
        #     raise DAError("Infinite loop: " + missingVariable + " already looked for, where stack is " + str(variable_stack))
        # variable_stack.add(missingVariable)
        found_generic = False
        realMissingVariable = missingVariable
        totry = list()
        variants = list()
        level_dict = dict()
        generic_dict = dict()
        expression_as_list = [x for x in match_brackets_or_dot.split(missingVariable) if x != '']
        expression_as_list.append('')
        recurse_indices(expression_as_list, list_of_indices, [], variants, level_dict, [], generic_dict, [])
        #logmessage("variants: " + repr(variants))
        for variant in variants:
            totry.append({'real': missingVariable, 'vari': variant, 'iterators': level_dict[variant], 'generic': generic_dict[variant], 'is_generic': 0 if generic_dict[variant] == '' else 1, 'num_dots': variant.count('.'), 'num_iterators': variant.count('[')})
        totry = sorted(sorted(sorted(sorted(totry, key=lambda x: len(x['iterators'])), key=lambda x: x['num_iterators'], reverse=True), key=lambda x: x['num_dots'], reverse=True), key=lambda x: x['is_generic'])
        #logmessage("ask_for: totry is " + "\n".join([x['vari'] for x in totry]))
        questions_to_try = list()
        for mv in totry:
            realMissingVariable = mv['real']
            missingVariable = mv['vari']
            #logmessage("Trying missingVariable " + missingVariable + " and realMissingVariable " + realMissingVariable)
            if mv['is_generic']:
                #logmessage("Testing out generic " + mv['generic'])
                try:
                    root_evaluated = eval(mv['generic'], user_dict)
                    #logmessage("Root was evaluated")
                    classes_to_look_for = [type(root_evaluated).__name__]
                    recursive_add_classes(classes_to_look_for, type(root_evaluated))
                    for generic_object in classes_to_look_for:
                        #logmessage("Looking for generic object " + generic_object + " for " + missingVariable)
                        if generic_object in self.generic_questions and missingVariable in self.generic_questions[generic_object] and (language in self.generic_questions[generic_object][missingVariable] or '*' in self.generic_questions[generic_object][missingVariable]):
                            for lang in [language, '*']:
                                if lang in self.generic_questions[generic_object][missingVariable]:
                                    for the_question_to_use in self.sort_with_orderings(self.generic_questions[generic_object][missingVariable][lang]):
                                        questions_to_try.append((the_question_to_use, True, mv['generic'], mv['iterators'], missingVariable, generic_object))
                except:
                    pass
                continue
            # logmessage("askfor: questions to try is " + str(questions_to_try))
            if missingVariable in self.questions:
                for lang in [language, '*']:
                    # logmessage("lang is " + lang)
                    if lang in self.questions[missingVariable]:
                        for the_question in self.sort_with_orderings(self.questions[missingVariable][lang]):
                            questions_to_try.append((the_question, False, 'None', mv['iterators'], missingVariable, None))
        # logmessage("askfor: questions to try is " + str(questions_to_try))
        num_cycles = 0
        missing_var = "_unknown"
        while True:
            num_cycles += 1
            if num_cycles > self.loop_limit:
                raise DAError("Infinite loop detected while looking for " + missing_var)
            a_question_was_skipped = False
            docassemble.base.functions.reset_gathering_mode(origMissingVariable)
            #logmessage("Starting the while loop")
            try:
                for the_question, is_generic, the_x, iterators, missing_var, generic_object in questions_to_try:
                    #logmessage("In for loop with question " + the_question.name)
                    if missing_var in questions_tried and the_question in questions_tried[missing_var]:
                        a_question_was_skipped = True
                        # logmessage("Skipping question " + the_question.name)
                        continue
                    current_question = the_question
                    if self.debug:
                        seeking.append({'question': the_question, 'reason': 'considering', 'time': time.time()})
                    question = current_question
                    if len(question.condition) > 0:
                        if is_generic:
                            if the_x != 'None':
                                exec("x = " + the_x, user_dict)
                        if len(iterators):
                            for indexno in range(len(iterators)):
                                exec(list_of_indices[indexno] + " = " + iterators[indexno], user_dict)
                        condition_success = True
                        for condition in question.condition:
                            if not eval(condition, user_dict):
                                condition_success = False
                                break
                        if not condition_success:
                            continue
                    if follow_mc:
                        question = the_question.follow_multiple_choice(user_dict, interview_status, is_generic, the_x, iterators)
                    else:
                        question = the_question
                    if question is not current_question:
                        if len(question.condition) > 0:
                            if is_generic:
                                if the_x != 'None':
                                    exec("x = " + the_x, user_dict)
                            if len(iterators):
                                for indexno in range(len(iterators)):
                                    exec(list_of_indices[indexno] + " = " + iterators[indexno], user_dict)
                            condition_success = True
                            for condition in question.condition:
                                if not eval(condition, user_dict):
                                    condition_success = False
                                    break
                            if not condition_success:
                                continue
                    if question.question_type == 'fields':
                        field_id = safeid(missing_var)
                        if is_generic:
                            if the_x != 'None':
                                exec("x = " + the_x, user_dict)
                        if len(iterators):
                            for indexno in range(len(iterators)):
                                exec(list_of_indices[indexno] + " = " + iterators[indexno], user_dict)
                        skip_question = None
                        for field in question.fields:
                            if hasattr(field, 'showif_code') and hasattr(field, 'saveas') and field.saveas == field_id:
                                docassemble.base.functions.this_thread.misc['current_field'] = field.number
                                result = eval(field.showif_code, user_dict)
                                if hasattr(field, 'extras') and 'show_if_sign_code' in field.extras and field.extras['show_if_sign_code'] == 0:
                                    if result:
                                        if skip_question is not False:
                                            skip_question = True
                                    else:
                                        skip_question = False
                                else:
                                    if not result:
                                        if skip_question is not False:
                                            skip_question = True
                                    else:
                                        skip_question = False
                        if skip_question:
                            continue
                    if self.debug:
                        if question.question_type in ('signature', 'yesno', 'noyes', 'yesnomaybe', 'noyesmaybe', 'multiple_choice', 'settrue', 'fields', 'review', 'deadend'):
                            seeking.append({'question': question, 'reason': 'asking', 'time': time.time()})
                        else:
                            seeking.append({'question': question, 'reason': 'running', 'time': time.time()})
                    if question.question_type == "data":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        old_values = question.get_old_values(user_dict)
                        string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_dataobject(question.fields[0].data, user_dict))
                        exec(string, user_dict)
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        question.invalidate_dependencies(user_dict, old_values)
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == "data_da":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        old_values = question.get_old_values(user_dict)
                        exec(import_core, user_dict)
                        string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.objects_from_structure(' + repr(recursive_eval_dataobject(question.fields[0].data, user_dict)) + ', root=' + repr(from_safeid(question.fields[0].saveas)) + ')'
                        exec(string, user_dict)
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        question.invalidate_dependencies(user_dict, old_values)
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == "data_from_code":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        old_values = question.get_old_values(user_dict)
                        string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_data_from_code(question.fields[0].data, user_dict))
                        exec(string, user_dict)
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        question.invalidate_dependencies(user_dict, old_values)
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == "data_from_code_da":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        old_values = question.get_old_values(user_dict)
                        exec(import_core, user_dict)
                        string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.objects_from_structure(' + repr(recursive_eval_data_from_code(question.fields[0].data, user_dict)) + ', root=' + repr(from_safeid(question.fields[0].saveas)) + ')'
                        exec(string, user_dict)
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        question.invalidate_dependencies(user_dict, old_values)
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == "objects":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        success = False
                        old_variable = None
                        docassemble.base.functions.this_thread.current_question = question
                        for keyvalue in question.objects:
                            # logmessage("In a for loop for keyvalue")
                            for variable, object_type_name in keyvalue.items():
                                if variable != missing_var:
                                    continue
                                was_defined = False
                                try:
                                    exec("__oldvariable__ = " + str(missing_var), user_dict)
                                    old_variable = user_dict['__oldvariable__']
                                    exec("del " + str(missing_var), user_dict)
                                    was_defined = True
                                except:
                                    pass
                                user_dict["__object_type"] = eval(object_type_name, user_dict)
                                if re.search(r"\.", variable):
                                    m = re.search(r"(.*)\.(.*)", variable)
                                    variable = m.group(1)
                                    attribute = m.group(2)
                                    # command = variable + "." + attribute + " = " + object_type + "()"
                                    command = variable + ".initializeAttribute(" + repr(attribute) + ", __object_type)"
                                    # logmessage("Running " + command)
                                    exec(command, user_dict)
                                else:
                                    if user_dict["__object_type"].__class__.__name__ == 'DAObjectPlusParameters':
                                        command = variable + ' = __object_type.object_type(' + repr(variable) + ', **__object_type.parameters)'
                                    else:
                                        command = variable + ' = __object_type(' + repr(variable) + ')'
                                    # logmessage("Running " + command)
                                    exec(command, user_dict)
                                if "__object_type" in user_dict:
                                    del user_dict["__object_type"]
                                if missing_var in variable_stack:
                                    variable_stack.remove(missing_var)
                                try:
                                    eval(missing_var, user_dict)
                                    success = True
                                    # logmessage("the variable was defined")
                                    break
                                except:
                                    # logmessage("the variable was not defined")
                                    if was_defined:
                                        try:
                                            exec(str(missing_var) + " = __oldvariable__", user_dict)
                                            #exec("__oldvariable__ = " + str(missing_var), user_dict)
                                            exec("del __oldvariable__", user_dict)
                                        except:
                                            pass
                                    continue
                            if success:
                                # logmessage("success, break")
                                break
                        # logmessage("testing for success")
                        if not success:
                            # logmessage("no success, continue")
                            continue
                        #question.mark_as_answered(user_dict)
                        # logmessage("pop current variable")
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        if old_variable is not None:
                            question.invalidate_dependencies_of_variable(user_dict, missing_var, old_variable)
                        # logmessage("Returning")
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == "template":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        temp_vars = dict()
                        if is_generic:
                            if the_x != 'None':
                                temp_vars['x'] = user_dict['x']
                        if len(iterators):
                            for indexno in range(len(iterators)):
                                temp_vars[list_of_indices[indexno]] = user_dict[list_of_indices[indexno]]
                        if question.target is not None:
                            return({'type': 'template', 'question_text': question.content.text(user_dict).rstrip(), 'subquestion_text': None, 'continue_label': None, 'audiovideo': None, 'decorations': None, 'help_text': None, 'attachments': None, 'question': question, 'selectcompute': dict(), 'defaults': dict(), 'hints': dict(), 'helptexts': dict(), 'extras': dict(), 'labels': dict(), 'sought': missing_var, 'orig_sought': origMissingVariable})
                        if question.decorations is None:
                            decoration_list = []
                        else:
                            decoration_list = question.decorations
                        actual_saveas = substitute_vars(from_safeid(question.fields[0].saveas), is_generic, the_x, iterators)
                        #docassemble.base.functions.this_thread.template_vars.append(actual_saveas)
                        found_object = False
                        try:
                            the_object = eval(actual_saveas, user_dict)
                            if the_object.__class__.__name__ == 'DALazyTemplate':
                                found_object = True
                        except:
                            pass
                        if not found_object:
                            string = "import docassemble.base.core"
                            exec(string, user_dict)
                            string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.DALazyTemplate(' + repr(actual_saveas) + ')'
                            exec(string, user_dict)
                            the_object = eval(actual_saveas, user_dict)
                            if the_object.__class__.__name__ != 'DALazyTemplate':
                                raise DAError("askfor: failure to define template object")
                        the_object.source_content = question.content
                        the_object.source_subject = question.subcontent
                        the_object.source_decorations = [dec['image'] for dec in decoration_list]
                        the_object.userdict = user_dict
                        the_object.tempvars = temp_vars
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == "template_code":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        the_filenames = eval(question.compute, user_dict)
                        if not isinstance(the_filenames, list):
                            if hasattr(the_filenames, 'instanceName') and hasattr(the_filenames, 'elements') and isinstance(the_filenames.elements, list):
                                the_filenames = the_filenames.elements
                            else:
                                the_filenames = [the_filenames]
                        raw_content = ''
                        for the_filename in the_filenames:
                            the_orig_filename = the_filename
                            if the_filename.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DAStaticFile'):
                                the_filename = the_filename.path()
                            elif isinstance(the_filename, str):
                                if re.search(r'^https?://', str(the_filename)):
                                    temp_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
                                    try:
                                        urlretrieve(url_sanitize(str(the_filename)), temp_template_file.name)
                                    except Exception as err:
                                        raise DAError("askfor: error downloading " + str(the_filename) + ": " + str(err))
                                    the_filename = temp_template_file.name
                                else:
                                    the_filename = docassemble.base.functions.package_template_filename(the_filename, package=question.package)
                            else:
                                the_filename = None
                            if the_filename is None or not os.path.isfile(the_filename):
                                raise DAError("askfor: error obtaining template file from code: " + repr(the_orig_filename))
                            with open(the_filename, 'r', encoding='utf-8') as the_file:
                                raw_content += the_file.read()
                        temp_vars = dict()
                        if is_generic:
                            if the_x != 'None':
                                temp_vars['x'] = user_dict['x']
                        if len(iterators):
                            for indexno in range(len(iterators)):
                                temp_vars[list_of_indices[indexno]] = user_dict[list_of_indices[indexno]]
                        if question.decorations is None:
                            decoration_list = []
                        else:
                            decoration_list = question.decorations
                        actual_saveas = substitute_vars(from_safeid(question.fields[0].saveas), is_generic, the_x, iterators)
                        found_object = False
                        try:
                            the_object = eval(actual_saveas, user_dict)
                            if the_object.__class__.__name__ == 'DALazyTemplate':
                                found_object = True
                        except:
                            pass
                        if not found_object:
                            string = "import docassemble.base.core"
                            exec(string, user_dict)
                            string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.DALazyTemplate(' + repr(actual_saveas) + ')'
                            exec(string, user_dict)
                            the_object = eval(actual_saveas, user_dict)
                            if the_object.__class__.__name__ != 'DALazyTemplate':
                                raise DAError("askfor: failure to define template object")
                        the_object.source_content = TextObject(raw_content, question=question)
                        the_object.source_subject = question.subcontent
                        the_object.source_decorations = [dec['image'] for dec in decoration_list]
                        the_object.userdict = user_dict
                        the_object.tempvars = temp_vars
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == "table":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        temp_vars = dict()
                        if is_generic:
                            if the_x != 'None':
                                temp_vars['x'] = user_dict['x']
                        if len(iterators):
                            for indexno in range(len(iterators)):
                                temp_vars[list_of_indices[indexno]] = user_dict[list_of_indices[indexno]]
                        table_info = TableInfo()
                        table_info.header = question.fields[0].extras['header']
                        table_info.is_editable = question.fields[0].extras['is_editable']
                        table_info.require_gathered = question.fields[0].extras['require_gathered']
                        table_info.show_incomplete = question.fields[0].extras['show_incomplete']
                        table_info.not_available_label = question.fields[0].extras['not_available_label']
                        table_info.row = question.fields[0].extras['row']
                        table_info.column = question.fields[0].extras['column']
                        table_info.indent = " " * (4 * int(question.fields[0].extras['indent']))
                        table_info.table_width = self.table_width
                        table_info.empty_message = question.fields[0].extras['empty_message']
                        table_info.saveas = from_safeid(question.fields[0].saveas)
                        actual_saveas = substitute_vars(table_info.saveas, is_generic, the_x, iterators)
                        #docassemble.base.functions.this_thread.template_vars.append(actual_saveas)
                        string = "import docassemble.base.core"
                        exec(string, user_dict)
                        found_object = False
                        try:
                            the_object = eval(actual_saveas, user_dict)
                            if the_object.__class__.__name__ == 'DALazyTableTemplate':
                                found_object = True
                        except:
                            pass
                        if not found_object:
                            string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.DALazyTableTemplate(' + repr(actual_saveas) + ')'
                            exec(string, user_dict)
                            the_object = eval(actual_saveas, user_dict)
                            if the_object.__class__.__name__ != 'DALazyTableTemplate':
                                raise DAError("askfor: failure to define template object")
                        the_object.table_info = table_info
                        the_object.userdict = user_dict
                        the_object.tempvars = temp_vars
                        #logmessage("Pop variable for table")
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type == 'attachments':
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        old_values = question.get_old_values(user_dict)
                        #logmessage("original missing variable is " + origMissingVariable)
                        attachment_text = question.processed_attachments(user_dict, seeking_var=origMissingVariable, use_cache=False)
                        if missing_var in variable_stack:
                            variable_stack.remove(missing_var)
                        try:
                            eval(missing_var, user_dict)
                            #question.mark_as_answered(user_dict)
                        except Exception as err:
                            logmessage("Problem with attachments block: " + err.__class__.__name__ + ": " + str(err))
                            continue
                        question.post_exec(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        question.invalidate_dependencies(user_dict, old_values)
                        return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    if question.question_type in ["code", "event_code"]:
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        was_defined = False
                        old_values = question.get_old_values(user_dict)
                        try:
                            exec("__oldvariable__ = " + str(missing_var), user_dict)
                            exec("del " + str(missing_var), user_dict)
                            was_defined = True
                        except:
                            pass
                        if question.question_type == 'event_code':
                            docassemble.base.functions.pop_event_stack(origMissingVariable)
                        docassemble.base.functions.this_thread.current_question = question
                        if was_defined:
                            exec_with_trap(question, user_dict, old_variable=missing_var)
                        else:
                            exec_with_trap(question, user_dict)
                        interview_status.mark_tentative_as_answered(user_dict)
                        if missing_var in variable_stack:
                            variable_stack.remove(missing_var)
                        if question.question_type == 'event_code':
                            docassemble.base.functions.pop_current_variable()
                            docassemble.base.functions.pop_event_stack(origMissingVariable)
                            question.invalidate_dependencies(user_dict, old_values)
                            if was_defined:
                                exec("del __oldvariable__", user_dict)
                            return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                        try:
                            eval(missing_var, user_dict)
                            if was_defined:
                                exec("del __oldvariable__", user_dict)
                            if seeking_question:
                                continue
                            #question.mark_as_answered(user_dict)
                            docassemble.base.functions.pop_current_variable()
                            docassemble.base.functions.pop_event_stack(origMissingVariable)
                            question.invalidate_dependencies(user_dict, old_values)
                            return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                        except:
                            if was_defined:
                                try:
                                    exec(str(missing_var) + " = __oldvariable__", user_dict)
                                    #exec("__oldvariable__ = " + str(missing_var), user_dict)
                                    exec("del __oldvariable__", user_dict)
                                except:
                                    pass
                            continue
                    else:
                        interview_status.mark_tentative_as_answered(user_dict)
                        if question.question_type == 'continue':
                            continue
                        return question.ask(user_dict, old_user_dict, the_x, iterators, missing_var, origMissingVariable)
                if a_question_was_skipped:
                    raise DAError("Infinite loop: " + missingVariable + " already looked for, where stack is " + str(variable_stack))
                if 'forgive_missing_question' in docassemble.base.functions.this_thread.misc and origMissingVariable in docassemble.base.functions.this_thread.misc['forgive_missing_question']:
                    docassemble.base.functions.pop_current_variable()
                    docassemble.base.functions.pop_event_stack(origMissingVariable)
                    if 'action' in docassemble.base.functions.this_thread.current_info and docassemble.base.functions.this_thread.current_info['action'] == origMissingVariable:
                        del docassemble.base.functions.this_thread.current_info['action']
                    return({'type': 'continue', 'sought': origMissingVariable, 'orig_sought': origMissingVariable})
                if self.options.get('use catchall', False) and not origMissingVariable.endswith('.value'):
                    string = "import docassemble.base.core"
                    exec(string, user_dict)
                    string = origMissingVariable + ' = docassemble.base.core.DACatchAll(' + repr(origMissingVariable) + ')'
                    exec(string, user_dict)
                    docassemble.base.functions.pop_current_variable()
                    docassemble.base.functions.pop_event_stack(origMissingVariable)
                    return({'type': 'continue', 'sought': origMissingVariable, 'orig_sought': origMissingVariable})
                raise DAErrorMissingVariable("Interview has an error.  There was a reference to a variable '" + origMissingVariable + "' that could not be looked up in the question file (for language '" + str(language) + "') or in any of the files incorporated by reference into the question file.", variable=origMissingVariable)
            except ForcedReRun as the_exception:
                docassemble.base.functions.pop_current_variable()
                docassemble.base.functions.pop_event_stack(origMissingVariable)
                return({'type': 're_run', 'sought': origMissingVariable, 'orig_sought': origMissingVariable})
            except (NameError, DAAttributeError, DAIndexError) as the_exception:
                if 'pending_error' in docassemble.base.functions.this_thread.misc:
                    del docassemble.base.functions.this_thread.misc['pending_error']
                #logmessage("Error in " + the_exception.__class__.__name__ + " is " + str(the_exception))
                if self.debug and docassemble.base.functions.this_thread.evaluation_context == 'docx':
                    logmessage("NameError exception during document assembly: " + str(the_exception))
                docassemble.base.functions.reset_context()
                seeking_question = False
                if isinstance(the_exception, ForcedNameError):
                    #logmessage("askfor: got a ForcedNameError for " + str(the_exception.name))
                    follow_mc = False
                    seeking_question = True
                    #logmessage("Seeking question is True")
                    newMissingVariable = the_exception.name
                    #logmessage("next action is " + repr(the_exception.next_action))
                    if the_exception.next_action is not None and not interview_status.checkin:
                        if 'event_stack' not in user_dict['_internal']:
                            user_dict['_internal']['event_stack'] = dict()
                        session_uid = interview_status.current_info['user']['session_uid']
                        if session_uid not in user_dict['_internal']['event_stack']:
                            user_dict['_internal']['event_stack'][session_uid] = list()
                        new_items = list()
                        for new_item in the_exception.next_action:
                            already_there = False
                            for event_item in user_dict['_internal']['event_stack'][session_uid]:
                                if event_item['action'] == new_item:
                                    already_there = True
                                    break
                            if not already_there:
                                new_items.append(new_item)
                        if len(new_items):
                            user_dict['_internal']['event_stack'][session_uid] = new_items + user_dict['_internal']['event_stack'][session_uid]
                        #interview_status.next_action.extend(the_exception.next_action)
                    if the_exception.arguments is not None:
                        docassemble.base.functions.this_thread.current_info.update(dict(action=the_exception.name, arguments=the_exception.arguments))
                    if the_exception.name.startswith('_da_'):
                        docassemble.base.functions.pop_current_variable()
                        docassemble.base.functions.pop_event_stack(origMissingVariable)
                        return({'type': 're_run', 'sought': origMissingVariable, 'orig_sought': origMissingVariable})
                    docassemble.base.functions.this_thread.misc['forgive_missing_question'] = [the_exception.name]
                else:
                    #logmessage("regular nameerror")
                    follow_mc = True
                    newMissingVariable = extract_missing_name(the_exception)
                if newMissingVariable == 'file':
                    raise
                #newMissingVariable = str(the_exception).split("'")[1]
                #if newMissingVariable in questions_tried and newMissingVariable in variable_stack:
                #    raise DAError("Infinite loop: " + missingVariable + " already looked for, where stack is " + str(variable_stack))
                if newMissingVariable not in questions_tried:
                    questions_tried[newMissingVariable] = set()
                else:
                    variable_stack.add(missingVariable)
                if current_question.question_type != 'objects':
                    questions_tried[newMissingVariable].add(current_question)
                try:
                    eval(origMissingVariable, user_dict)
                    was_defined = True
                except:
                    was_defined = False
                question_result = self.askfor(newMissingVariable, user_dict, old_user_dict, interview_status, variable_stack=variable_stack, questions_tried=questions_tried, seeking=seeking, follow_mc=follow_mc, recursion_depth=recursion_depth, seeking_question=seeking_question)
                if question_result['type'] == 'continue' and missing_var != newMissingVariable:
                    if not was_defined:
                        try:
                            eval(origMissingVariable, user_dict)
                            now_defined = True
                        except:
                            now_defined = False
                        if now_defined:
                            docassemble.base.functions.pop_current_variable()
                            return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                    # logmessage("Continuing after asking for newMissingVariable " + str(newMissingVariable))
                    continue
                docassemble.base.functions.pop_current_variable()
                return(question_result)
            except UndefinedError as the_exception:
                #logmessage("UndefinedError")
                if self.debug and docassemble.base.functions.this_thread.evaluation_context == 'docx':
                    #logmessage(the_exception.__class__.__name__ + " exception during document assembly: " + str(the_exception) + "\n" + traceback.format_exc())
                    logmessage(the_exception.__class__.__name__ + " exception during document assembly: " + str(the_exception) + "\n")
                docassemble.base.functions.reset_context()
                newMissingVariable = extract_missing_name(the_exception)
                if newMissingVariable not in questions_tried:
                    questions_tried[newMissingVariable] = set()
                else:
                    variable_stack.add(missingVariable)
                if current_question.question_type != 'objects':
                    questions_tried[newMissingVariable].add(current_question)
                question_result = self.askfor(newMissingVariable, user_dict, old_user_dict, interview_status, variable_stack=variable_stack, questions_tried=questions_tried, seeking=seeking, follow_mc=True, recursion_depth=recursion_depth, seeking_question=seeking_question)
                if question_result['type'] == 'continue':
                    continue
                docassemble.base.functions.pop_current_variable()
                return(question_result)
            except CommandError as qError:
                #logmessage("CommandError: " + str(qError))
                docassemble.base.functions.reset_context()
                question_data = dict(command=qError.return_type, url=qError.url, sleep=qError.sleep)
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var, origMissingVariable))
            except ResponseError as qError:
                #logmessage("ResponseError")
                docassemble.base.functions.reset_context()
                #logmessage("Trapped ResponseError2")
                question_data = dict(extras=dict())
                if hasattr(qError, 'response') and qError.response is not None:
                    question_data['response'] = qError.response
                elif hasattr(qError, 'binaryresponse') and qError.binaryresponse is not None:
                    question_data['binaryresponse'] = qError.binaryresponse
                elif hasattr(qError, 'filename') and qError.filename is not None:
                    question_data['response filename'] = qError.filename
                elif hasattr(qError, 'url') and qError.url is not None:
                    question_data['redirect url'] = qError.url
                elif hasattr(qError, 'all_variables') and qError.all_variables:
                    if hasattr(qError, 'include_internal'):
                        question_data['include_internal'] = qError.include_internal
                    question_data['content type'] = 'application/json'
                    question_data['all_variables'] = True
                elif hasattr(qError, 'nullresponse') and qError.nullresponse:
                    question_data['null response'] = qError.nullresponse
                elif hasattr(qError, 'sleep') and qError.sleep:
                    question_data['sleep'] = qError.sleep
                if hasattr(qError, 'content_type') and qError.content_type:
                    question_data['content type'] = qError.content_type
                if hasattr(qError, 'response_code') and qError.response_code:
                    question_data['response code'] = qError.response_code
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                #the_question = new_question.follow_multiple_choice(user_dict)
                docassemble.base.functions.pop_event_stack(origMissingVariable)
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var, origMissingVariable))
            except BackgroundResponseError as qError:
                # logmessage("BackgroundResponseError")
                docassemble.base.functions.reset_context()
                #logmessage("Trapped BackgroundResponseError2")
                question_data = dict(extras=dict())
                if hasattr(qError, 'backgroundresponse'):
                    question_data['backgroundresponse'] = qError.backgroundresponse
                if hasattr(qError, 'sleep'):
                    question_data['sleep'] = qError.sleep
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                docassemble.base.functions.pop_event_stack(origMissingVariable)
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var, origMissingVariable))
            except BackgroundResponseActionError as qError:
                # logmessage("BackgroundResponseActionError")
                docassemble.base.functions.reset_context()
                #logmessage("Trapped BackgroundResponseActionError2")
                question_data = dict(extras=dict())
                if hasattr(qError, 'action'):
                    question_data['action'] = qError.action
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                docassemble.base.functions.pop_event_stack(origMissingVariable)
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var, origMissingVariable))
            except QuestionError as qError:
                #logmessage("QuestionError")
                docassemble.base.functions.reset_context()
                #logmessage("Trapped QuestionError")
                question_data = dict()
                if qError.question:
                    question_data['question'] = qError.question
                if qError.subquestion:
                    question_data['subquestion'] = qError.subquestion
                if qError.dead_end:
                    pass
                elif qError.buttons:
                    question_data['buttons'] = qError.buttons
                else:
                    buttons = list()
                    if qError.show_exit is not False and not (qError.show_leave is True and qError.show_exit is None):
                        exit_button = {word('Exit'): 'exit'}
                        if qError.url:
                            exit_button.update(dict(url=qError.url))
                        buttons.append(exit_button)
                    if qError.show_leave:
                        leave_button = {word('Leave'): 'leave'}
                        if qError.url:
                            leave_button.update(dict(url=qError.url))
                        buttons.append(leave_button)
                    if qError.show_restart is not False:
                        buttons.append({word('Restart'): 'restart'})
                    if len(buttons):
                        question_data['buttons'] = buttons
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                new_question.embeds = True
                # will this be a problem? yup
                the_question = new_question.follow_multiple_choice(user_dict, interview_status, False, 'None', [])
                return(the_question.ask(user_dict, old_user_dict, 'None', [], missing_var, origMissingVariable))
            except CodeExecute as code_error:
                #logmessage("CodeExecute")
                docassemble.base.functions.reset_context()
                #if self.debug:
                #    interview_status.seeking.append({'question': question, 'reason': 'mandatory code'})
                #logmessage("Going to execute " + str(code_error.compute) + " where missing_var is " + str(missing_var))
                exec(code_error.compute, user_dict)
                try:
                    eval(missing_var, user_dict)
                    code_error.question.mark_as_answered(user_dict)
                    #logmessage("Got here 1")
                    #logmessage("returning from running code")
                    docassemble.base.functions.pop_current_variable()
                    #logmessage("Got here 2")
                    return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
                except:
                    #raise DAError("Problem setting that variable")
                    continue
            except SyntaxException as qError:
                #logmessage("SyntaxException")
                docassemble.base.functions.reset_context()
                the_question = None
                try:
                    the_question = question
                except:
                    pass
                if the_question is not None:
                    raise DAError(str(qError) + "\n\n" + str(self.idebug(self.data_for_debug)))
                raise DAError("no question available in askfor: " + str(qError))
            except CompileException as qError:
                #logmessage("CompileException")
                docassemble.base.functions.reset_context()
                the_question = None
                try:
                    the_question = question
                except:
                    pass
                if the_question is not None:
                    raise DAError(str(qError) + "\n\n" + str(self.idebug(self.data_for_debug)))
                raise DAError("no question available in askfor: " + str(qError))
            # except SendFileError as qError:
            #     #logmessage("Trapped SendFileError2")
            #     question_data = dict(extras=dict())
            #     if hasattr(qError, 'filename') and qError.filename is not None:
            #         question_data['response filename'] = qError.filename
            #     if hasattr(qError, 'content_type') and qError.content_type:
            #         question_data['content type'] = qError.content_type
            #     new_interview_source = InterviewSourceString(content='')
            #     new_interview = new_interview_source.get_interview()
            #     new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
            #     new_question.name = "Question_Temp"
            #     return(new_question.ask(user_dict, old_user_dict, 'None', [], None, None))
        if 'forgive_missing_question' in docassemble.base.functions.this_thread.misc and origMissingVariable in docassemble.base.functions.this_thread.misc['forgive_missing_question']:
            docassemble.base.functions.pop_current_variable()
            docassemble.base.functions.pop_event_stack(origMissingVariable)
            return({'type': 'continue', 'sought': missing_var, 'orig_sought': origMissingVariable})
        raise DAErrorMissingVariable("Interview has an error.  There was a reference to a variable '" + origMissingVariable + "' that could not be found in the question file (for language '" + str(language) + "') or in any of the files incorporated by reference into the question file.", variable=origMissingVariable)

def substitute_vars(var, is_generic, the_x, iterators, last_only=False):
    if is_generic:
        if the_x != 'None':
            var = re.sub(r'^x\b', the_x, var)
    if len(iterators):
        if last_only:
            indexno = len(iterators) - 1
            var = re.sub(r'\[' + list_of_indices[indexno] + r'\]', '[' + str(iterators[indexno]) + ']', var)
        else:
            for indexno in range(len(iterators)):
                #the_iterator = iterators[indexno]
                #if isinstance(the_iterator, str) and re.match(r'^-?[0-9]+$', the_iterator):
                #    the_iterator = int(the_iterator)
                #var = re.sub(r'\[' + list_of_indices[indexno] + r'\]', '[' + repr(the_iterator) + ']', var)
                var = re.sub(r'\[' + list_of_indices[indexno] + r'\]', '[' + str(iterators[indexno]) + ']', var)
    return var

def substitute_vars_action(action, is_generic, the_x, iterators):
    if isinstance(action, str):
        return substitute_vars(action, is_generic, the_x, iterators)
    elif isinstance(action, dict):
        new_dict = dict()
        for key, val in action.items():
            if key == 'action' and not key.startswith('_da_'):
                new_dict[key] = substitute_vars_action(val, is_generic, the_x, iterators)
            elif key == 'arguments' and isinstance(val, dict) and 'variables' in val and len(val) == 1:
                new_dict[key] = substitute_vars_action(val, is_generic, the_x, iterators)
            elif key == 'variables' and isinstance(val, list):
                new_dict[key] = substitute_vars_action(val, is_generic, the_x, iterators)
            else:
                new_dict[key] = val
        return new_dict
    elif isinstance(action, list):
        new_list = list()
        for item in action:
            new_list.append(substitute_vars_action(item, is_generic, the_x, iterators))
        return new_list
    else:
        return action

def reproduce_basics(interview, new_interview):
    new_interview.metadata = interview.metadata
    new_interview.external_files = interview.external_files

def unpack_list(item, target_list=None):
    if target_list is None:
        target_list = list()
    if not isinstance(item, (list, dict)):
        target_list.append(item)
    else:
        for subitem in item:
            unpack_list(subitem, target_list)
    return target_list

def process_selections(data, manual=False, exclude=None):
    if exclude is None:
        to_exclude = list()
    else:
        to_exclude = unpack_list(exclude)
    result = []
    if (isinstance(data, abc.Iterable) and not isinstance(data, (str, dict)) and not (hasattr(data, 'elements') and isinstance(data.elements, dict))) or (hasattr(data, 'elements') and isinstance(data.elements, (list, set))):
        for entry in data:
            if isinstance(entry, dict) or (hasattr(entry, 'elements') and isinstance(entry.elements, dict)):
                the_item = dict()
                for key in entry:
                    if len(entry) > 1:
                        if key in ['default', 'help', 'image', 'label']:
                            continue
                        if 'default' in entry:
                            the_item['default'] = entry['default']
                        if 'help' in entry:
                            the_item['help'] = entry['help']
                        if 'image' in entry:
                            if entry['image'].__class__.__name__ == 'DAFile':
                                entry['image'].retrieve()
                                if entry['image'].mimetype is not None and entry['image'].mimetype.startswith('image'):
                                    the_item['image'] = dict(type='url', value=entry['image'].url_for())
                            elif entry['image'].__class__.__name__ == 'DAFileList':
                                entry['image'][0].retrieve()
                                if entry['image'][0].mimetype is not None and entry['image'][0].mimetype.startswith('image'):
                                    the_item['image'] = dict(type='url', value=entry['image'][0].url_for())
                            elif entry['image'].__class__.__name__ == 'DAFileCollection':
                                the_file = entry['image']._first_file()
                                the_file.retrieve()
                                if the_file.mimetype is not None and the_file.mimetype.startswith('image'):
                                    the_item['image'] = dict(type='url', value=entry['image'][0].url_for())
                            elif entry['image'].__class__.__name__ == 'DAStaticFile':
                                the_item['image'] = dict(type='url', value=entry['image'].url_for())
                            else:
                                the_item['image'] = dict(type='decoration', value=entry['image'])
                    if key == 'value' and 'label' in entry:
                        the_item['key'] = entry[key]
                        the_item['label'] = entry['label']
                        if entry[key] not in to_exclude and ((not isinstance(entry['label'], bool)) or entry['label'] is True):
                            result.append(the_item)
                    else:
                        the_item['key'] = key
                        the_item['label'] = entry[key]
                        is_not_boolean = False
                        for key, val in entry.items():
                            if key in ['default', 'help', 'image', 'label']:
                                continue
                            if val not in (True, False):
                                is_not_boolean = True
                        if key not in to_exclude and (is_not_boolean or entry[key] is True):
                            result.append(the_item)
            if (isinstance(entry, (list, tuple)) or (hasattr(entry, 'elements') and isinstance(entry.elements, list))) and len(entry) > 0:
                if entry[0] not in to_exclude:
                    if len(entry) >= 4:
                        result.append(dict(key=entry[0], label=entry[1], default=entry[2], help=entry[3]))
                    elif len(entry) == 3:
                        result.append(dict(key=entry[0], label=entry[1], default=entry[2]))
                    elif len(entry) == 1:
                        result.append(dict(key=entry[0], label=entry[0]))
                    else:
                        result.append(dict(key=entry[0], label=entry[1]))
            elif isinstance(entry, (str, bool, int, float)):
                if entry not in to_exclude:
                    result.append(dict(key=entry, label=entry))
            elif hasattr(entry, 'instanceName'):
                if entry not in to_exclude:
                    result.append(dict(key=str(entry), label=str(entry)))
    elif isinstance(data, dict) or (hasattr(data, 'elements') and isinstance(data.elements, dict)):
        if isinstance(data, OrderedDict) or (hasattr(data, 'elements') and isinstance(data.elements, OrderedDict)):
            the_items = data.items()
        else:
            the_items = sorted(data.items(), key=operator.itemgetter(1))
        for key, value in the_items:
            if key not in to_exclude:
                if isinstance(value, (str, bool, int, float)):
                    result.append(dict(key=key, label=value))
                elif hasattr(value, 'instanceName'):
                    result.append(dict(key=key, label=str(value)))
                else:
                    logmessage("process_selections: non-label passed as label in dictionary")
    else:
        raise DAError("Unknown data type in choices selection: " + re.sub(r'[<>]', '', repr(data)))
    return(result)

def extract_missing_name(the_error):
    #logmessage("extract_missing_name: string was " + str(string))
    m = nameerror_match.search(str(the_error))
    if m:
        return m.group(1)
    else:
        raise the_error

def auto_determine_type(field_info, the_value=None):
    types = dict()
    if 'selections' in field_info:
        for item in field_info['selections']:
            the_type = type(item[0]).__name__
            if the_type not in types:
                types[the_type] = 0
            types[the_type] += 1
    if the_value is not None:
        the_type = type(the_value).__name__
        if the_type not in types:
            types[the_type] = 0
        types[the_type] += 1
    if 'str' in types or 'unicode' in types:
        return
    if len(types) == 2:
        if 'int' in types and 'float' in types:
            field_info['type'] = 'float'
            return
    if len(types) > 1:
        return
    if 'bool' in types:
        field_info['type'] = 'boolean'
        return
    if 'int' in types:
        field_info['type'] = 'integer'
        return
    if 'float' in types:
        field_info['type'] = 'float'
        return
    return

def get_mimetype(filename):
    if filename is None:
        return 'text/plain; charset=utf-8'
    mimetype, encoding = mimetypes.guess_type(filename)
    extension = filename.lower()
    extension = re.sub('.*\.', '', extension)
    if extension == '3gpp':
        mimetype = 'audio/3gpp'
    if mimetype is None:
        mimetype = 'text/plain'
    return mimetype

def interpret_label(text):
    if text is None:
        return 'no label'
    return str(text)

def recurse_indices(expression_array, variable_list, pre_part, final_list, var_subs_dict, var_subs, generic_dict, generic):
    if len(expression_array) == 0:
        return
    the_expr = "".join(pre_part) + "".join(expression_array)
    if the_expr not in final_list and the_expr != 'x':
        final_list.append(the_expr)
        var_subs_dict[the_expr] = var_subs
        generic_dict[the_expr] = "".join(generic)
    first_part = expression_array.pop(0)
    if match_brackets.match(first_part) and len(variable_list) > 0:
        new_var_subs = copy.copy(var_subs)
        new_var_subs.append(re.sub(r'^\[|\]$', r'', first_part))
        new_list_of_indices = copy.copy(variable_list)
        var_to_use = new_list_of_indices.pop(0)
        new_part = copy.copy(pre_part)
        new_part.append('[' + var_to_use + ']')
        recurse_indices(copy.copy(expression_array), new_list_of_indices, new_part, final_list, var_subs_dict, new_var_subs, generic_dict, generic)
        if len(new_var_subs) == 0 and len(generic) == 0:
            recurse_indices(copy.copy(expression_array), new_list_of_indices, ['x', '[' + var_to_use + ']'], final_list, var_subs_dict, new_var_subs, generic_dict, copy.copy(pre_part))
    pre_part.append(first_part)
    recurse_indices(copy.copy(expression_array), variable_list, copy.copy(pre_part), final_list, var_subs_dict, var_subs, generic_dict, copy.copy(generic))
    if len(var_subs) == 0 and len(generic) == 0:
        recurse_indices(copy.copy(expression_array), variable_list, ['x'], final_list, var_subs_dict, var_subs, generic_dict, copy.copy(pre_part))

def ensure_object_exists(saveas, datatype, the_user_dict, commands=None):
    # logmessage("ensure object exists: " + str(saveas))
    if commands is None:
        execute = True
        commands = list()
    else:
        execute = False
    already_there = False
    try:
        eval(saveas, the_user_dict)
        already_there = True
    except:
        pass
    if already_there:
        #logmessage("ensure object exists: already there")
        return
    use_initialize = False
    parse_result = parse_var_name(saveas)
    if not parse_result['valid']:
        raise DAError("Variable name " + saveas + " is invalid: " + parse_result['reason'])
    method = None
    if parse_result['final_parts'][1] != '':
        if parse_result['final_parts'][1][0] == '.':
            try:
                core_key = eval(parse_result['final_parts'][0], the_user_dict)
                if hasattr(core_key, 'instanceName'):
                    method = 'attribute'
            except:
                pass
        elif parse_result['final_parts'][1][0] == '[':
            try:
                core_key = eval(parse_result['final_parts'][0], the_user_dict)
                if hasattr(core_key, 'instanceName'):
                    method = 'index'
            except:
                pass
    if "import docassemble.base.core" not in commands:
        commands.append("import docassemble.base.core")
    if method == 'attribute':
        attribute_name = parse_result['final_parts'][1][1:]
        if datatype in ('multiselect', 'checkboxes'):
            commands.append(parse_result['final_parts'][0] + ".initializeAttribute(" + repr(attribute_name) + ", docassemble.base.core.DADict, auto_gather=False)")
        elif datatype in ('object_multiselect', 'object_checkboxes'):
            commands.append(parse_result['final_parts'][0] + ".initializeAttribute(" + repr(attribute_name) + ", docassemble.base.core.DAList, auto_gather=False)")
    elif method == 'index':
        index_name = parse_result['final_parts'][1][1:-1]
        if datatype in ('multiselect', 'checkboxes'):
            commands.append(parse_result['final_parts'][0] + ".initializeObject(" + repr(index_name) + ", docassemble.base.core.DADict, auto_gather=False)")
        elif datatype in ('object_multiselect', 'object_checkboxes'):
            commands.append(parse_result['final_parts'][0] + ".initializeObject(" + repr(index_name) + ", docassemble.base.core.DAList, auto_gather=False)")
    else:
        if datatype in ('multiselect', 'checkboxes'):
            commands.append(saveas + ' = docassemble.base.core.DADict(' + repr(saveas) + ', auto_gather=False)')
        elif datatype in ('object_multiselect', 'object_checkboxes'):
            commands.append(saveas + ' = docassemble.base.core.DAList(' + repr(saveas) + ', auto_gather=False)')
    if execute:
        for command in commands:
            #logmessage("Doing " + command)
            exec(command, the_user_dict)

def invalid_variable_name(varname):
    if not isinstance(varname, str):
        return True
    if re.search(r'[\n\r\(\)\{\}\*\^\#]', varname):
        return True
    varname = re.sub(r'[\.\[].*', '', varname)
    if not valid_variable_match.match(varname):
        return True
    return False

def exec_with_trap(the_question, the_dict, old_variable=None):
    try:
        exec(the_question.compute, the_dict)
        the_question.post_exec(the_dict)
    except (NameError, UndefinedError, CommandError, ResponseError, BackgroundResponseError, BackgroundResponseActionError, QuestionError, AttributeError, MandatoryQuestion, CodeExecute, SyntaxException, CompileException):
        if old_variable is not None:
            try:
                exec(str(old_variable) + " = __oldvariable__", the_dict)
                exec("del __oldvariable__", the_dict)
            except:
                pass
        raise
    except Exception as e:
        cl, exc, tb = sys.exc_info()
        exc.user_dict = docassemble.base.functions.serializable_dict(the_dict)
        if len(traceback.extract_tb(tb)) == 2:
            line_with_error = traceback.extract_tb(tb)[-1][1]
            if isinstance(line_with_error, int) and line_with_error > 0 and hasattr(the_question, 'sourcecode'):
                exc.da_line_with_error = the_question.sourcecode.splitlines()[line_with_error - 1]
                exc.__traceback__ = tb
        del cl
        del exc
        del tb
        raise

ok_outside_string = string.ascii_letters + string.digits + '.[]_'
ok_inside_string = string.ascii_letters + string.digits + string.punctuation + " "

def parse_var_name(var):
    var_len = len(var)
    cur_pos = 0
    in_bracket = 0
    in_quote = 0
    the_quote = None
    dots = list()
    brackets = list()
    while cur_pos < var_len:
        char = var[cur_pos]
        if char == '[':
            if cur_pos == 0:
                return dict(valid=False, reason='bracket at start')
            if var[cur_pos - 1] == '.':
                return dict(valid=False, reason='dot before bracket')
            if not in_quote:
                if in_bracket:
                    return dict(valid=False, reason='nested brackets')
                in_bracket = 1
                brackets.append(cur_pos)
        elif char == ']':
            if cur_pos == 0:
                return dict(valid=False)
            if var[cur_pos - 1] == '.':
                return dict(valid=False, reason='dot before bracket')
            if not in_quote:
                if in_bracket:
                    in_bracket = 0
                else:
                    return dict(valid=False, reason='unexpected end bracket')
        elif char in ("'", '"'):
            if cur_pos == 0 or not in_bracket:
                return dict(valid=False, reason='unexpected quote mark')
            if in_quote:
                if char == the_quote and var[cur_pos - 1] != "\\":
                    in_quote = 0
            else:
                in_quote = 1
                the_quote = char
        else:
            if not (in_quote or in_bracket):
                if char not in ok_outside_string:
                    return dict(valid=False, reason='invalid character in variable name')
            if cur_pos == 0:
                if char in string.digits or char == '.':
                    return dict(valid=False, reason='starts with digit or dot')
            else:
                if var[cur_pos - 1] == '.' and char in string.digits:
                    return dict(valid=False, reason='attribute starts with digit')
            if in_quote:
                if char not in ok_inside_string:
                    return dict(valid=False, reason='invalid character in string')
            else:
                if char == '.':
                    if in_bracket:
                        return dict(valid=False, reason="dot in bracket")
                    if cur_pos > 0 and var[cur_pos - 1] == '.':
                        return dict(valid=False, reason = 'two dots')
                    dots.append(cur_pos)
        cur_pos += 1
    if in_bracket:
        return dict(valid=False, reason='dangling bracket part')
    if in_quote:
        return dict(valid=False, reason='dangling quote part')
    objects = [var[0:dot_pos] for dot_pos in dots]
    bracket_objects = [var[0:bracket_pos] for bracket_pos in brackets]
    final_cut = 0
    if len(dots):
        final_cut = dots[-1]
    if len(brackets):
        if brackets[-1] > final_cut:
            final_cut = brackets[-1]
    if final_cut > 0:
        final_parts = (var[0:final_cut], var[final_cut:])
    else:
        final_parts = (var, '')
    return dict(valid=True, objects=objects, bracket_objects=bracket_objects, final_parts=final_parts)

class DAExtension(Extension):
    def filter_stream(self, stream):
        in_var = False
        met_pipe = False
        for token in stream:
            if token.type == 'variable_begin':
                in_var = True
                met_pipe = False
            if token.type == 'variable_end':
                in_var = False
                if not met_pipe:
                    yield Token(token.lineno, 'pipe', None)
                    yield Token(token.lineno, 'name', 'ampersand_filter')
            # if in_var and token.type == 'pipe':
            #     met_pipe = True
            yield token

class DAEnvironment(Environment):
    def from_string(self, source, **kwargs):
        source = re.sub(r'({[\%\{].*?[\%\}]})', fix_quotes, source)
        return super().from_string(source, **kwargs)
    def getitem(self, obj, argument):
        try:
            return obj[argument]
        except (AttributeError, TypeError, LookupError):
            return self.undefined(obj=obj, name=argument, accesstype='item')

    def getattr(self, obj, attribute):
        try:
            return getattr(obj, attribute)
        except AttributeError:
            pass
        return self.undefined(obj=obj, name=attribute, accesstype='attribute')

def ampersand_filter(value):
    if value.__class__.__name__ in ('DAFile', 'DALink', 'DAStaticFile', 'DAFileCollection', 'DAFileList'):
        return value
    if value.__class__.__name__ in ('InlineImage', 'RichText', 'Listing', 'Document', 'Subdoc', 'DALazyTemplate'):
        return str(value)
    if isinstance(value, (int, bool, float, NoneType)):
        return value
    if not isinstance(value, str):
        value = str(value)
    value = docassemble.base.file_docx.sanitize_xml(value)
    if '<w:r>' in value or '</w:t>' in value:
        return re.sub(r'&(?!#?[0-9A-Za-z]+;)', '&amp;', value)
    return re.sub(r'>', '&gt;', re.sub(r'<', '&lt;', re.sub(r'&(?!#?[0-9A-Za-z]+;)', '&amp;', value)))

class DAStrictUndefined(StrictUndefined):
    __slots__ = ('_undefined_type')
    def __init__(self, hint=None, obj=missing, name=None, exc=UndefinedError, accesstype=None):
        self._undefined_hint = hint
        self._undefined_obj = obj
        self._undefined_name = name
        self._undefined_exception = exc
        self._undefined_type = accesstype

    @internalcode
    def __getattr__(self, name):
        if name[:2] == '__':
            raise AttributeError(name)
        return self._fail_with_undefined_error(attribute=True)

    @internalcode
    def __getitem__(self, index):
        if index[:2] == '__':
            raise IndexError(index)
        return self._fail_with_undefined_error(item=True)

    @internalcode
    def _fail_with_undefined_error(self, *args, **kwargs):
        if True or self._undefined_hint is None:
            if self._undefined_obj is missing:
                hint = "'%s' is undefined" % self._undefined_name
            elif self._undefined_type == 'item' and hasattr(self._undefined_obj, 'instanceName'):
                hint = "'%s[%r]' is undefined" % (
                    self._undefined_obj.instanceName,
                    self._undefined_name
                )
            elif 'attribute' in kwargs or self._undefined_type == 'attribute':
                if hasattr(self._undefined_obj, 'instanceName'):
                    hint = "'%s.%s' is undefined" % (
                        self._undefined_obj.instanceName,
                        self._undefined_name
                    )
                else:
                    hint = '%r has no attribute %r' % (
                        object_type_repr(self._undefined_obj),
                        self._undefined_name
                    )
            else:
                if hasattr(self._undefined_obj, 'instanceName'):
                    hint = "'%s[%r]' is undefined" % (
                        self._undefined_obj.instanceName,
                        self._undefined_name
                    )
                else:
                    hint = '%s has no element %r' % (
                        object_type_repr(self._undefined_obj),
                        self._undefined_name
                    )
        else:
            hint = self._undefined_hint
        raise self._undefined_exception(hint)
    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
        __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = \
        __float__ = __complex__ = __pow__ = __rpow__ = __sub__ = \
        __rsub__= __iter__ = __str__ = __len__ = __nonzero__ = __eq__ = \
        __ne__ = __bool__ = __hash__ = _fail_with_undefined_error


def mygetattr(y, attr):
    for attribute in attr.split('.'):
        y = getattr(y, attribute)
    return y

def str_or_original(y, case_sensitive):
    if case_sensitive:
        if hasattr(y, 'instanceName'):
            if y.__class__.__name__ in ('Value', 'PeriodicValue'):
                return y.amount()
            return str(y)
        return y
    if hasattr(y, 'instanceName'):
        if y.__class__.__name__ in ('Value', 'PeriodicValue'):
            return y.amount()
        return str(y).lower()
    try:
        return y.lower()
    except:
        return y

def dictsort_filter(dictionary, case_sensitive=False, by='key', reverse=False):
    if by == 'value':
        return sorted(dictionary.items(), key=lambda y: str_or_original(y[1], case_sensitive), reverse=reverse)
    else:
        return sorted(dictionary.items(), key=lambda y: str_or_original(y[0], case_sensitive), reverse=reverse)

def sort_filter(array, reverse=False, case_sensitive=False, attribute=None):
    if attribute is None:
        if not case_sensitive:
            def key_func(y):
                return str_or_original(y, case_sensitive)
        else:
            key_func = None
    else:
        if isinstance(attribute, list):
            attributes = [str(y).strip() for y in attribute]
        else:
            attributes = [y.strip() for y in str(attribute).split(',')]
        def key_func(y):
            return [str_or_original(mygetattr(y, attribute), case_sensitive) for attribute in attributes]
    return sorted(array, key=key_func, reverse=reverse)

_GroupTuple = namedtuple('_GroupTuple', ['grouper', 'list'])
_GroupTuple.__repr__ = tuple.__repr__
_GroupTuple.__str__ = tuple.__str__

def groupby_filter(array, attr_name):
    def func(y):
        return mygetattr(y, attr_name)
    return [_GroupTuple(key, list(values)) for key, values in groupby(sorted(array, key=func), func)]

def max_filter(array, case_sensitive=False, attribute=None):
    it = iter(array)
    try:
        first = next(it)
    except StopIteration:
        raise DAError("max: list was empty")
    if attribute:
        def key_func(y):
            return str_or_original(mygetattr(y, attribute), case_sensitive=case_sensitive)
    else:
        def key_func(y):
            return str_or_original(y, case_sensitive=case_sensitive)
    return max(chain([first], it), key=key_func)

def min_filter(array, case_sensitive=False, attribute=None):
    it = iter(array)
    try:
        first = next(it)
    except StopIteration:
        raise DAError("min: list was empty")
    if attribute:
        def key_func(y):
            return str_or_original(mygetattr(y, attribute), case_sensitive=case_sensitive)
    else:
        def key_func(y):
            return str_or_original(y, case_sensitive=case_sensitive)
    return min(chain([first], it), key=key_func)

def sum_filter(array, attribute=None, start=0):
    if attribute is not None:
        array = [mygetattr(y, attribute) for y in array]
    return sum(array, start)

def unique_filter(array, case_sensitive=False, attribute=None):
    seen = set()
    if attribute is None:
        for item in array:
            new_item = str_or_original(item, case_sensitive)
            if new_item not in seen:
                seen.add(new_item)
                yield item
    else:
        for item in array:
            new_item = str_or_original(mygetattr(item, attribute), case_sensitive)
            if new_item not in seen:
                seen.add(new_item)
                yield mygetattr(item, attribute)

def join_filter(array, d="", attribute=None):
    if attribute is not None:
        return d.join([str(mygetattr(y, attribute)) for y in array])
    return d.join([str(y) for y in array])

def attr_filter(var, attr_name):
    return mygetattr(var, attr_name)

def selectattr_filter(*pargs, **kwargs):
    if len(pargs) > 2:
        array = pargs[0]
        attr_name = pargs[1]
        func_name = pargs[2]
        env = custom_jinja_env()
        func = lambda item: env.call_test(func_name, item, pargs[3:], kwargs)
        for item in array:
            if func(mygetattr(item, attr_name)):
                yield item
    else:
        for item in pargs[0]:
            if mygetattr(item, pargs[1]):
                yield item

def rejectattr_filter(*pargs, **kwargs):
    if len(pargs) > 2:
        array = pargs[0]
        attr_name = pargs[1]
        func_name = pargs[2]
        env = custom_jinja_env()
        func = lambda item: env.call_test(func_name, item, pargs[3:], kwargs)
        for item in array:
            if not func(mygetattr(item, attr_name)):
                yield item
    else:
        for item in pargs[0]:
            if not mygetattr(item, pargs[1]):
                yield item

def map_filter(*pargs, **kwargs):
    if len(pargs) >= 2:
        array = pargs[0]
        the_filter = pargs[1]
        env = custom_jinja_env()
        if the_filter not in env.filters:
            raise DAError('filter passed to map() does not exist')
        for item in array:
            yield env.call_filter(the_filter, item, pargs[2:], kwargs)
    else:
        if 'attribute' in kwargs:
            if 'default' in kwargs:
                for item in pargs[0]:
                    yield mygetattr(item, kwargs['attribute'], kwargs['default'])
            else:
                for item in pargs[0]:
                    yield mygetattr(item, kwargs['attribute'])
        elif 'index' in kwargs:
            if 'default' in kwargs:
                for item in pargs[0]:
                    yield item.get(kwargs['index'], kwargs['default'])
            else:
                for item in pargs[0]:
                    yield item[kwargs['index']]
        elif 'function' in kwargs:
            the_kwargs = kwargs.get('kwargs', dict())
            the_pargs = kwargs.get('pargs', list())
            if not isinstance(the_kwargs, dict):
                raise DAError('kwargs passed to map() must be a dictionary')
            if not isinstance(the_pargs, list):
                raise DAError('pargs passed to map() must be a list')
            for item in pargs[0]:
                yield kwargs['function'](item, *the_pargs, **the_kwargs)
        else:
            raise DAError('map() must refer to a function, index, attribute, or filter')

def markdown_filter(text):
    return docassemble.base.file_docx.markdown_to_docx(str(text), docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None))

def inline_markdown_filter(text):
    return docassemble.base.file_docx.inline_markdown_to_docx(str(text), docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None))

builtin_jinja_filters = {
    'ampersand_filter': ampersand_filter,
    'markdown': markdown_filter,
    'add_separators': docassemble.base.functions.add_separators,
    'inline_markdown': inline_markdown_filter,
    'paragraphs': docassemble.base.functions.single_to_double_newlines,
    'manual_line_breaks': docassemble.base.functions.manual_line_breaks,
    'RichText': docassemble.base.file_docx.RichText,
    'groupby': groupby_filter,
    'max': max_filter,
    'min': min_filter,
    'sum': sum_filter,
    'unique': unique_filter,
    'join': join_filter,
    'attr': attr_filter,
    'selectattr': selectattr_filter,
    'rejectattr': rejectattr_filter,
    'sort': sort_filter,
    'dictsort': dictsort_filter,
    'nice_number': docassemble.base.functions.nice_number,
    'ordinal': docassemble.base.functions.ordinal,
    'ordinal_number': docassemble.base.functions.ordinal_number,
    'currency': docassemble.base.functions.currency,
    'comma_list': docassemble.base.functions.comma_list,
    'comma_and_list': docassemble.base.functions.comma_and_list,
    'capitalize': docassemble.base.functions.capitalize,
    'salutation': docassemble.base.functions.salutation,
    'alpha': docassemble.base.functions.alpha,
    'roman': docassemble.base.functions.roman,
    'word': docassemble.base.functions.word,
    'bold': docassemble.base.functions.bold,
    'italic': docassemble.base.functions.italic,
    'title_case': docassemble.base.functions.title_case,
    'single_paragraph': docassemble.base.functions.single_paragraph,
    'phone_number_formatted': docassemble.base.functions.phone_number_formatted,
    'phone_number_in_e164': docassemble.base.functions.phone_number_in_e164,
    'country_name': docassemble.base.functions.country_name,
    'fix_punctuation': docassemble.base.functions.fix_punctuation,
    'redact': docassemble.base.functions.redact,
    'verbatim': docassemble.base.functions.verbatim,
    'map': map_filter
}

registered_jinja_filters = {}

def custom_jinja_env():
    env = DAEnvironment(undefined=DAStrictUndefined, extensions=[DAExtension])
    env.filters.update(registered_jinja_filters)
    env.filters.update(builtin_jinja_filters)
    return env

def register_jinja_filter(filter_name, func):
    if filter_name in builtin_jinja_filters:
        raise DAError("Cannot register filter with same name as built-in filter %s" % filter_name)
    registered_jinja_filters[filter_name] = func

def get_docx_variables(the_path):
    import docassemble.base.legal
    names = set()
    if not os.path.isfile(the_path):
        raise DAError("Missing docx template file " + os.path.basename(the_path))
    try:
        docx_template = docassemble.base.file_docx.DocxTemplate(the_path)
        the_env = custom_jinja_env()
        the_xml = docx_template.get_xml()
        the_xml = re.sub(r'<w:p>', '\n<w:p>', the_xml)
        the_xml = re.sub(r'({[\%\{].*?[\%\}]})', fix_quotes, the_xml)
        the_xml = docx_template.patch_xml(the_xml)
        parsed_content = the_env.parse(the_xml)
    except Exception as the_err:
        raise DAError("There was an error parsing the docx file: " + the_err.__class__.__name__ + " " + str(the_err))
    for key in jinja2meta.find_undeclared_variables(parsed_content):
        if not key.startswith('_'):
            names.add(key)
    for name in docassemble.base.legal.__all__:
        if name in names:
            names.remove(name)
    return sorted(list(names))

def allow_users_list(obj):
    if not (isinstance(obj, list) or (hasattr(obj, 'instanceName') and hasattr(obj, 'elements') and isinstance(obj.elements, list))):
        obj = [obj]
    new_list = list()
    for item in obj:
        if isinstance(item, str) and re.search(r'^[0-9]+$', item):
            item = int(item)
        if isinstance(item, (int, str)):
            new_list.append(item)
        else:
            email_address_method = getattr(item, 'email_address', None)
            if callable(email_address_method):
                new_list.append(item.email)
            else:
                new_list.append(str(item))
    return new_list

def allow_privileges_list(obj):
    if not (isinstance(obj, list) or (hasattr(obj, 'instanceName') and hasattr(obj, 'elements') and isinstance(obj.elements, list))):
        obj = [obj]
    new_list = list()
    for item in obj:
        if isinstance(item, str):
            new_list.append(item)
    return new_list

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
