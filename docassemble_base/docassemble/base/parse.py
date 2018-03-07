import mimetypes
import traceback
import re
from jinja2.runtime import StrictUndefined, UndefinedError
from jinja2.exceptions import TemplateError
from jinja2.environment import Environment
from jinja2.environment import Template as JinjaTemplate
from jinja2 import meta as jinja2meta
import ast
import ruamel.yaml
import string
import os
import os.path
import sys
import urllib
import httplib2
import datetime
import time
import operator
import pprint
import copy
import codecs
import random
import tempfile
import json
import docassemble.base.filter
import docassemble.base.pdftk
import docassemble.base.file_docx
from docassemble.base.error import DAError, MandatoryQuestion, DAErrorNoEndpoint, DAErrorMissingVariable, ForcedNameError, QuestionError, ResponseError, BackgroundResponseError, BackgroundResponseActionError, CommandError, CodeExecute
import docassemble.base.functions
from docassemble.base.functions import pickleable_objects, word, get_language, server, RawValue, get_config
from docassemble.base.logger import logmessage
from docassemble.base.pandoc import MyPandoc, word_to_markdown
from docassemble.base.mako.template import Template as MakoTemplate
from docassemble.base.mako.exceptions import SyntaxException
from docassemble.base.astparser import myvisitnode
from types import CodeType, NoneType

debug = True
import_core = "import docassemble.base.core"
import_and_run_process_action = compile('from docassemble.base.util import *\nprocess_action()', '<code block>', 'exec')
run_process_action = compile('process_action()', '<code block>', 'exec')
match_process_action = re.compile(r'process_action\(')
match_mako = re.compile(r'<%|\${|% if|% for|% while')
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

def process_audio_video_list(the_list, user_dict):
    output = list()
    for the_item in the_list:
        output.append({'text': the_item['text'].text(user_dict), 'package': the_item['package'], 'type': the_item['type']})
    return output

def table_safe(text):
    text = unicode(text)
    text = re.sub(r'[\n\r\|]', ' ', text)
    if re.match(r'[\-:]+', text):
        text = '  ' + text + '  '
    return text

def textify(data, user_dict):
    return list(map((lambda x: x.text(user_dict)), data))

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

initial_dict = dict(_internal=dict(progress=0, tracker=0, docvar=dict(), doc_cache=dict(), steps=1, steps_offset=0, secret=None, informed=dict(), livehelp=dict(availability='unavailable', mode='help', roles=list(), partner_roles=list()), answered=set(), answers=dict(), objselections=dict(), starttime=None, modtime=None, accesstime=dict(), tasks=dict(), gather=list()), url_args=dict(), nav=docassemble.base.functions.DANav())

def set_initial_dict(the_dict):
    global initial_dict
    initial_dict = the_dict
    return

def get_initial_dict():
    return copy.deepcopy(initial_dict);

class PackageImage(object):
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

class InterviewSource(object):
    def __init__(self, **kwargs):
        if not hasattr(self, 'package'):
            self.package = kwargs.get('package', None)
        self.language = kwargs.get('language', '*')
        self.dialect = kwargs.get('dialect', None)
        self.testing = kwargs.get('testing', False)
    def set_path(self, path):
        self.path = path
        return
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
        #self.playground = None
        #self.package = None
        #self.set_filepath(kwargs.get('filepath', None))
        self.set_path(kwargs.get('path', None))
        self.set_directory(kwargs.get('directory', None))
        self.set_content(kwargs.get('content', None))
        self._modtime = datetime.datetime.utcnow()
        return super(InterviewSourceString, self).__init__(**kwargs)

class InterviewSourceFile(InterviewSource):
    def __init__(self, **kwargs):
        self.playground = None
        if 'filepath' in kwargs:
            if re.search(r'SavedFile', str(type(kwargs['filepath']))):
                #logmessage("We have a saved file on our hands")
                self.playground = kwargs['filepath']
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
        return super(InterviewSourceFile, self).__init__(**kwargs)
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
            with open(self.filepath, 'rU') as the_file:
                self.set_content(the_file.read().decode('utf8'))
                #sys.stderr.write("Returning true\n")
                return True
        except Exception as errmess:
            #sys.stderr.write("Error: " + str(errmess) + "\n")
            pass
        return False
    def get_modtime(self):
        #logmessage("get_modtime called in parse where path is " + str(self.path))
        if self.playground is not None:
            return self.playground.get_modtime(filename=self.basename)
        self._modtime = os.path.getmtime(self.filepath)
        return(self._modtime)
    def append(self, path):
        new_file = os.path.join(self.directory, path)
        if os.path.isfile(new_file) and os.access(new_file, os.R_OK):
            new_source = InterviewSourceFile()
            new_source.path = path
            new_source.basename = path
            new_source.filepath = new_file
            new_source.playground = self.playground
            if hasattr(self, 'package'):
                new_source.package = self.package
            if new_source.update():
                return(new_source)
        return(None)
    
class InterviewSourceURL(InterviewSource):
    def __init__(self, **kwargs):
        self.set_path(kwargs.get('path', None))
        return super(InterviewSourceURL, self).__init__(**kwargs)
    def set_path(self, path):
        self.path = path
        if self.path is None:
            self.directory = None
        else:
            self.directory = re.sub('/[^/]*$', '', re.sub('\?.*', '', self.path))
        return
    def update(self):
        try:
            h = httplib2.Http()
            resp, content = h.request(self.path, "GET")
            if resp['status'] >= 200 and resp['status'] < 300:
                self.set_content(content)
                self._modtime = datetime.datetime.utcnow()
                return True
        except:
            pass
        return False
    def append(self, path):
        new_file = os.path.join(self.directory, path)
        if os.path.isfile(new_file) and os.access(new_file, os.R_OK):
            new_source = InterviewSourceFile()
            new_source.path = path
            new_source.filepath = new_file
            if new_source.update():
                return(new_source)
        return None

class InterviewStatus(object):
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
        self.next_action = list()
        self.embedded = set()
        self.extras = dict()
        self.followed_mc = False
        self.tentatively_answered = set()
    def get_field_list(self):
        if 'sub_fields' in self.extras:
            field_list = list()
            for field in self.question.fields:
                if field.number in self.extras['sub_fields']:
                    field_list.extend(self.extras['sub_fields'][field.number])
                else:
                    field_list.append(field)
            return field_list
        return self.question.fields
    def mark_tentative_as_answered(self, user_dict):
        for question in self.tentatively_answered:
            question.mark_as_answered(user_dict)
        self.tentatively_answered.clear()
    def initialize_screen_reader(self):
        self.using_screen_reader = True
        self.screen_reader_text = dict()
        self.screen_reader_links = {'question': [], 'help': []}
    def populate(self, question_result):
        self.question = question_result['question']
        self.questionText = question_result['question_text']
        self.subquestionText = question_result['subquestion_text']
        self.underText = question_result['under_text']
        self.continueLabel = question_result['continue_label']
        self.decorations = question_result['decorations']
        self.audiovideo = question_result['audiovideo']
        self.helpText = question_result['help_text']
        self.attachments = question_result['attachments']
        self.selectcompute = question_result['selectcompute']
        self.defaults = question_result['defaults']
        #self.defined = question_result['defined']
        self.hints = question_result['hints']
        self.helptexts = question_result['helptexts']
        self.extras = question_result['extras']
        self.labels = question_result['labels']
        self.sought = question_result['sought']
    def set_tracker(self, tracker):
        self.tracker = tracker
    def as_data(self, encode=True):
        result = dict()
        for param in ('questionText', 'subquestionText', 'underText', 'continueLabel', 'helpLabel'):
            if hasattr(self, param) and getattr(self, param) is not None:
                result[param] = getattr(self, param).rstrip()
        if hasattr(self, 'audiovideo') and self.audiovideo is not None:
            audio_result = docassemble.base.filter.get_audio_urls(self.audiovideo)
            video_result = docassemble.base.filter.get_video_urls(self.audiovideo)
            if len(audio_result) > 0:
                result['audio'] = [dict(url=re.sub(r'.*"(http[^"]+)".*', r'\1', x)) if type(x) in (str, unicode) else dict(url=x[0], mime_type=x[1]) for x in audio_result]
            if len(video_result) > 0:
                result['video'] = [dict(url=re.sub(r'.*"(http[^"]+)".*', r'\1', x)) if type(x) in (str, unicode) else dict(url=x[0], mime_type=x[1]) for x in video_result]
        if hasattr(self, 'helpText') and len(self.helpText) > 0:
            result['helpText'] = list()
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
                    the_help['content'] = help_text['content'].rstrip()
                if 'heading' in help_text and help_text['heading'] is not None:
                    the_help['heading'] = help_text['heading'].rstrip()
                result['helpText'].append(the_help)
        if 'questionText' not in result and self.question.question_type == "signature":
            result['questionText'] = word('Sign Your Name')
        result['questionType'] = self.question.question_type
        if hasattr(self.question, 'name'):
            result['_question_name'] = self.question.name
        result['_tracker'] = self.tracker
        if hasattr(self, 'datatypes'):
            result['_datatypes'] = safeid(json.dumps(self.datatypes))
        if hasattr(self, 'varnames'):
            result['_varnames'] = safeid(json.dumps(self.varnames))
        if len(self.question.fields) > 0:
            result['fields'] = list()
        if self.decorations is not None:
            for decoration in self.decorations:
                if 'image' in decoration:
                    the_image = self.question.interview.images.get(decoration['image'], None)
                    if the_image is not None:
                        the_url = docassemble.base.functions.server.url_finder(str(the_image.package) + ':' + str(the_image.filename))
                        if the_url is not None and the_image.attribution is not None:
                            result['decoration_url'] = the_url
                            self.attributions.add(the_image.attribution)
                        break
                    elif get_config('default icons', None) in ('material icons', 'font awesome'):
                        result['decoration_name'] = decoration['image']
                        break
        if len(self.attachments) > 0:
            result['attachments'] = list()
            if self.current_info['user']['is_authenticated'] and self.current_info['user']['email']:
                result['default_email'] = self.current_info['user']['email']
            for attachment in self.attachments:
                the_attachment = dict(url=dict())
                for key in ('valid_formats', 'filename', 'name', 'description', 'content', 'markdown'):
                    if key in attachment:
                        if attachment[key]:
                            the_attachment[key] = attachment[key]
                for the_format in attachment['file']:
                    the_attachment['url'][the_format] = docassemble.base.functions.server.url_finder(attachment['file'][the_format], filename=attachment['filename'] + '.' + extension_of_doc_format[the_format])
                result['attachments'].append(the_attachment)
        for field in self.question.fields:
            the_field = dict()
            the_field['number'] = field.number
            if hasattr(field, 'saveas'):
                the_field['variable_name'] = from_safeid(field.saveas)
                if encode:
                    the_field['variable_name_encoded'] = field.saveas
            for param in ('datatype', 'fieldtype', 'sign', 'inputtype', 'address_autocomplete'):
                if hasattr(field, param):
                    the_field[param] = getattr(field, param)
            if hasattr(field, 'shuffle') and field.shuffle is not False:
                the_field['shuffle'] = True
            if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                the_field['disable_others'] = True
            if hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                the_field['uncheck_others'] = True
            for key in ('minlength', 'maxlength', 'min', 'max', 'step', 'inline width'):
                if hasattr(field, 'extras') and key in field.extras and key in self.extras:
                    the_field[key] = self.extras[key][field.number]
            if hasattr(field, 'saveas') and field.saveas in self.embedded:
                the_field['embedded'] = True
            if hasattr(self, 'shuffle'):
                the_field['shuffle'] = self.shuffle
            if field.number in self.defaults:
                the_default = self.defaults[field.number]
                if type(the_default) in (str, unicode, int, bool, float):
                    the_field['default'] = the_default
            else:
                the_default = None
            if self.question.question_type == 'multiple_choice' or hasattr(field, 'choicetype') or (hasattr(field, 'datatype') and field.datatype in ('object', 'checkboxes', 'object_checkboxes', 'object_radio')):
                the_field['choices'] = self.get_choices_data(field, the_default, encode=encode)
            if hasattr(field, 'nota'):
                the_field['none_of_the_above'] = self.extras['nota'][field.number]
            the_field['active'] = self.extras['ok'][field.number]
            if field.number in self.extras['required']:
                the_field['required'] = True
            else:
                the_field['required'] = False
            if hasattr(field, 'extras'):
                if 'ml_group' in field.extras or 'ml_train' in field.extras:
                    the_field['ml_info'] = dict()
                    if 'ml_group' in field.extras:
                        the_field['ml_info']['group_id'] = self.extras['ml_group'][field.number]
                    if 'ml_train' in field.extras:
                        the_field['ml_info']['train'] = self.extras['ml_train'][field.number]
                if 'show_if_var' in field.extras and 'show_if_val' in self.extras:
                    the_field['show_if_sign'] = field.extras['show_if_sign']
                    the_field['show_if_var'] = field.extras['show_if_var']
                    the_field['show_if_val'] = self.extras['show_if_val'][field.number]
            if hasattr(field, 'datatype'):
                if field.datatype == 'note' and 'note' in self.extras and field.number in self.extras['note']:
                    the_field['note'] = self.extras['note'][field.number]
                if field.datatype == 'html' and 'html' in self.extras and field.number in self.extras['html']:
                    the_field['html'] = self.extras['html'][field.number]
                if field.number in self.labels:
                    the_field['label'] = self.labels[field.number]
                if field.number in self.helptexts:
                    the_field['helptext'] = self.helptexts[field.number]
            result['fields'].append(the_field)
            if self.question.question_type in ("yesno", "yesnomaybe"):
                the_field['true_label'] = self.question.yes()
                the_field['false_label'] = self.question.no()
            if self.question.question_type == 'yesnomaybe':
                the_field['maybe_label'] = self.question.maybe()
        if len(self.attributions):
            result['attributions'] = [x.rstrip() for x in self.attributions]
        return result
    def get_choices(self, field):
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
                elif field.datatype in ('checkboxes', 'object_checkboxes'):
                    pairlist = list()
                if field.datatype == 'object_checkboxes':
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas, from_safeid(pair['key'])])
                elif field.datatype in ('object', 'object_radio'):
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas, from_safeid(pair['key'])])
                elif field.datatype == 'checkboxes':
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas + "[" + repr(pair['key']) + "]", True])
                else:
                    for pair in pairlist:
                        choice_list.append([pair['label'], saveas, pair['key']])
                if hasattr(field, 'nota') and self.extras['nota'][field.number] is not False:
                    if self.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = self.extras['nota'][field.number]
                    choice_list.append([formatted_item, None, None])
        else:
            indexno = 0
            for choice in self.selectcompute[field.number]:
                choice_list.append([choice['label'], '_internal["answers"][' + repr(question.name) + ']', indexno])
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
    def get_choices_data(self, field, defaultvalue, encode=True):
        question = self.question
        choice_list = list()
        if hasattr(field, 'saveas') and field.saveas is not None:
            saveas = from_safeid(field.saveas)
            if self.question.question_type == "multiple_choice":
                pairlist = list(self.selectcompute[field.number])
                for pair in pairlist:
                    item = dict(label=pair['label'], value=pair['key'])
                    if 'help' in pair:
                        item['help'] = pair['help'].rstrip()
                    if 'default' in pair:
                        item['default'] = pair['default']
                    if 'image' in pair:
                        if type(pair['image']) is dict:
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
                elif field.datatype in ('checkboxes', 'object_checkboxes'):
                    pairlist = list()
                if field.datatype == 'object_checkboxes':
                    for pair in pairlist:
                        item = dict(label=pair['label'], value=from_safeid(pair['key']))
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in (list, set) and unicode(pair['key']) in defaultvalue) or (type(defaultvalue) is dict and unicode(pair['key']) in defaultvalue and defaultvalue[unicode(pair['key'])]) or (type(defaultvalue) in (str, unicode, int, bool, float) and unicode(pair['key']) == unicode(defaultvalue)):
                            item['selected'] = True
                        if 'help' in pair:
                            item['help'] = pair['help']
                        choice_list.append(item)
                elif field.datatype in ('object', 'object_radio'):
                    for pair in pairlist:
                        item = dict(label=pair['label'], value=from_safeid(pair['key']))
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in (str, unicode, int, bool, float) and unicode(pair['key']) == unicode(defaultvalue)):
                            item['selected'] = True
                        if 'default' in pair:
                            item['default'] = unicode(pair['default'])
                        if 'help' in pair:
                            item['help'] = pair['help']
                        choice_list.append(item)
                elif field.datatype == 'checkboxes':
                    for pair in pairlist:
                        item = dict(label=pair['label'], variable_name=saveas + "[" + repr(pair['key']) + "]", value=True)
                        if encode:
                            item[variable_name_encoded] = safeid(saveas + "[" + repr(pair['key']) + "]")
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in (list, set) and unicode(pair['key']) in defaultvalue) or (type(defaultvalue) is dict and unicode(pair['key']) in defaultvalue and defaultvalue[unicode(pair['key'])]) or (type(defaultvalue) in (str, unicode, int, bool, float) and unicode(pair['key']) == unicode(defaultvalue)):
                            item['selected'] = True
                        if 'help' in pair:
                            item['help'] = pair['help']
                        choice_list.append(item)
                else:
                    for pair in pairlist:
                        item = dict(label=pair['label'], value=pair['key'])
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in (str, unicode, int, bool, float) and unicode(pair['key']) == unicode(defaultvalue)):
                            item['selected'] = True
                        choice_list.append(item)
                if hasattr(field, 'nota') and self.extras['nota'][field.number] is not False:
                    if self.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = self.extras['nota'][field.number]
                    choice_list.append(dict(label=formatted_item))
        else:
            indexno = 0
            for choice in self.selectcompute[field.number]:
                item = dict(label=choice['label'], variable_name='_internal["answers"][' + repr(question.name) + ']', value=indexno)
                if encode:
                    item['variable_name_encoded'] = safeid('_internal["answers"][' + repr(question.name) + ']')
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

class TextObject(object):
    def __init__(self, x, names_used=set()):
        self.original_text = x
        if type(x) in (str, unicode) and match_mako.search(x):
            self.template = MakoTemplate(x, strict_undefined=True, input_encoding='utf-8')
            for x in self.template.names_used:
                if x not in self.template.names_set:
                    names_used.add(x)
            self.uses_mako = True
        else:
            self.uses_mako = False
    def text(self, user_dict):
        if self.uses_mako:
            return(self.template.render(**user_dict))
        else:
            return(self.original_text)

def safeid(text):
    return codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '')

def from_safeid(text):
    return(codecs.decode(text, 'base64').decode('utf8'))

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
        if 'hint' in data:
            self.hint = data['hint']
        if 'data' in data:
            self.data = data['data']
        if 'help' in data:
            self.helptext = data['help']
        if 'validate' in data:
            self.validate = data['validate']
        if 'address_autocomplete' in data:
            self.address_autocomplete = data['address_autocomplete']
        if 'max_image_size' in data:
            self.max_image_size = data['max_image_size']
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

def recursive_eval_dataobject(target, user_dict):
    if type(target) is dict or (hasattr(target, 'elements') and type(target.elements) is dict):
        new_dict = dict()
        for key, val in target.iteritems():
            new_dict[key] = recursive_eval_dataobject(val, user_dict)
        return new_dict
    if type(target) is list or (hasattr(target, 'elements') and type(target.elements) is list):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_eval_dataobject(val, user_dict))
        return new_list
    if type(target) is set or (hasattr(target, 'elements') and type(target.elements) is set):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_eval_dataobject(val, user_dict))
        return new_set
    if type(target) in (bool, float, int, NoneType):
        return target
    if type(target) is TextObject:
        return target.text(user_dict)
    else:
        raise DAError("recursive_eval_dataobject: expected a TextObject, but found a " + str(type(target)))

def recursive_eval_data_from_code(target, user_dict):
    if type(target) is dict:
        new_dict = dict()
        for key, val in target.iteritems():
            new_dict[key] = recursive_eval_data_from_code(val, user_dict)
        return new_dict
    if type(target) is list:
        new_list = list()
        for val in target:
            new_list.append(recursive_eval_data_from_code(val, user_dict))
        return new_list
    if type(target) is set:
        new_set = set()
        for val in target:
            new_set.add(recursive_eval_data_from_code(val, user_dict))
        return new_set
    if type(target) is CodeType:
        return eval(target, user_dict)
    else:
        return target
    
def recursive_textobject(target, names_used):
    if type(target) is dict or (hasattr(target, 'elements') and type(target.elements) is dict):
        new_dict = dict()
        for key, val in target.iteritems():
            new_dict[key] = recursive_textobject(val, names_used)
        return new_dict
    if type(target) is list or (hasattr(target, 'elements') and type(target.elements) is list):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_textobject(val, names_used))
        return new_list
    if type(target) is set or (hasattr(target, 'elements') and type(target.elements) is set):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_textobject(val, names_used))
        return new_set
    return TextObject(unicode(target), names_used=names_used)

def recursive_eval_textobject(target, user_dict, question, tpl):
    if type(target) is dict or (hasattr(target, 'elements') and type(target.elements) is dict):
        new_dict = dict()
        for key, val in target.iteritems():
            new_dict[key] = recursive_eval_textobject(val, user_dict, question, tpl)
        return new_dict
    if type(target) is list or (hasattr(target, 'elements') and type(target.elements) is list):
        new_list = list()
        for val in target.__iter__():
            new_list.append(recursive_eval_textobject(val, user_dict, question, tpl))
        return new_list
    if type(target) is set or (hasattr(target, 'elements') and type(target.elements) is set):
        new_set = set()
        for val in target.__iter__():
            new_set.add(recursive_eval_textobject(val, user_dict, question, tpl))
        return new_set
    if type(target) in (bool, NoneType):
        return target
    if type(target) is TextObject:
        text = target.text(user_dict)
        return docassemble.base.file_docx.transform_for_docx(text, question, tpl)
    else:
        raise DAError("recursive_eval_textobject: expected a TextObject, but found a " + str(type(target)))

def docx_variable_fix(variable):
    variable = re.sub(r'\\', '', variable)
    variable = re.sub(r'^([A-Za-z\_][A-Za-z\_0-9]*).*', r'\1', variable)
    return variable

class FileInPackage:
    def __init__(self, fileref, area, package):
        if area == 'template' and type(fileref) is not dict:
            docassemble.base.functions.package_template_filename(fileref, package=package)
        self.fileref = fileref
        if type(self.fileref) is dict:
            self.is_code = True
            if 'code' not in self.fileref:
                raise DAError("A docx or pdf template file expressed in the form of a dictionary must have 'code' as the key" + str(self.fileref))
            self.code = compile(self.fileref['code'], '<template file code>', 'eval')
        else:
            self.is_code = False
        self.area = area
        self.package = package
    def path(self, user_dict=dict()):
        if self.area == 'template':
            if self.is_code:
                if len(user_dict) == 0:
                    raise Exception("FileInPackage.path: called with empty dict")
                the_file_ref = eval(self.code, user_dict)
                if the_file_ref.__class__.__name__ == 'DAFile':
                    the_file_ref = the_file_ref.path()
                elif the_file_ref.__class__.__name__ == 'DAFileList' and len(the_file_ref.elements) > 0:
                    the_file_ref = the_file_ref.elements[0].path()
                elif the_file_ref.__class__.__name__ == 'DAStaticFile':
                    the_file_ref = the_file_ref.path()
                elif re.search(r'^https?://', str(the_file_ref)):
                    temp_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
                    try:
                        urllib.urlretrieve(str(the_file_ref), temp_template_file.name)
                    except Exception as err:
                        raise DAError("FileInPackage: error downloading " + str(the_file_ref) + ": " + str(err))
                    the_file_ref = temp_template_file.name
                if not str(the_file_ref).startswith('/'):
                    the_file_ref = docassemble.base.functions.package_template_filename(str(the_file_ref), package=self.package)
                return the_file_ref
            else:
                return docassemble.base.functions.package_template_filename(self.fileref, package=self.package)

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
            return "\nIn file " + str(self.from_source.path) + " from package " + str(self.package) + ":\n\n" + ruamel.yaml.dump(data)
        else:
            return ruamel.yaml.dump(data)
    def __init__(self, orig_data, caller, **kwargs):
        if type(orig_data) is not dict:
            raise DAError("A block must be in the form of a dictionary." + self.idebug(orig_data))
        data = dict()
        for key, value in orig_data.iteritems():
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
        if debug:
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
        self.scan_for_variables = True
        self.helptext = None
        self.subcontent = None
        self.reload_after = None
        self.undertext = None
        self.continuelabel = None
        self.helplabel = None
        self.progress = None
        self.section = None
        self.script = None
        self.css = None
        self.checkin = None
        self.target = None
        self.decorations = None
        self.audiovideo = None
        self.allow_emailing = True
        self.compute_attachment = None
        self.can_go_back = True
        self.fields_used = set()
        self.names_used = set()
        self.mako_names = set()
        self.validation_code = None
        num_directives = 0
        for directive in ('yesno', 'noyes', 'yesnomaybe', 'noyesmaybe', 'fields', 'buttons', 'choices', 'dropdown', 'combobox', 'signature', 'review'):
            if directive in data:
                num_directives += 1
        if num_directives > 1:
            raise DAError("There can only be one directive in a question.  You had more than one.\nThe directives are yesno, noyes, yesnomaybe, noyesmaybe, fields, buttons, choices, dropdown, combobox, and signature." + self.idebug(data))
        if num_directives > 0 and 'question' not in data:
            raise DAError("This block is missing a 'question' directive." + self.idebug(data))
        if 'features' in data:
            should_append = False
            if type(data['features']) is not dict:
                raise DAError("A features section must be a dictionary." + self.idebug(data))
            if 'table width' in data['features']:
                if type(data['features']['table width']) is not int:
                    raise DAError("Table width in features must be an integer." + self.idebug(data))
                self.interview.table_width = data['features']['table width']
            if 'progress bar' in data['features']:
                self.interview.use_progress_bar = True if data['features']['progress bar'] else False
            if 'question back button' in data['features']:
                self.interview.question_back_button = True if data['features']['question back button'] else False
            if 'question help button' in data['features']:
                self.interview.question_help_button = True if data['features']['question help button'] else False
            if 'navigation back button' in data['features']:
                self.interview.navigation_back_button = True if data['features']['navigation back button'] else False
            if 'go full screen' in data['features'] and data['features']['go full screen']:
                self.interview.force_fullscreen = data['features']['go full screen']
            if 'navigation' in data['features'] and data['features']['navigation']:
                self.interview.use_navigation = True
            if 'maximum image size' in data['features']:
                self.interview.max_image_size = eval(str(data['features']['maximum image size']))
            if 'cache documents' in data['features']:
                self.interview.cache_documents = data['features']['cache documents']
            if 'loop limit' in data['features']:
                self.interview.loop_limit = data['features']['loop limit']
            if 'recursion limit' in data['features']:
                self.interview.recursion_limit = data['features']['recursion limit']
            if 'pdf/a' in data['features'] and data['features']['pdf/a'] in (True, False):
                self.interview.use_pdf_a = data['features']['pdf/a']
            if 'bootstrap theme' in data['features'] and data['features']['bootstrap theme']:
                self.interview.bootstrap_theme = data['features']['bootstrap theme']
            if 'inverse navbar' in data['features']:
                self.interview.options['inverse navbar'] = data['features']['inverse navbar']
            if 'hide standard menu' in data['features']:
                self.interview.options['hide standard menu'] = data['features']['hide standard menu']
            if 'checkin interval' in data['features']:
                if type(data['features']['checkin interval']) is not int:
                    raise DAError("A features section checkin interval entry must be an integer." + self.idebug(data))
                if data['features']['checkin interval'] > 0 and data['features']['checkin interval'] < 1000:
                    raise DAError("A features section checkin interval entry must be at least 1000, if not 0." + self.idebug(data))
                self.interview.options['checkin interval'] = data['features']['checkin interval']
            for key in ('javascript', 'css'):
                if key in data['features']:
                    if type(data['features'][key]) is list:
                        the_list = data['features'][key]
                    elif type(data['features'][key]) is dict:
                        raise DAError("A features section " + key + " entry must be a list or plain text." + self.idebug(data))
                    else:
                        the_list = [data['features'][key]]
                    for the_file in the_list:
                        if key not in self.interview.external_files:
                            self.interview.external_files[key] = list()
                        self.interview.external_files[key].append((self.from_source.get_package(), the_file))
        if 'scan for variables' in data:
            if data['scan for variables']:
                self.scan_for_variables = True
            else:
                self.scan_for_variables = False
        if 'question' in data and 'code' in data:
            raise DAError("A block can be a question block or a code block but cannot be both at the same time." + self.idebug(data))
        if 'event' in data:
            if 'field' in data or 'fields' in data or 'yesno' in data or 'noyes' in data:
                raise DAError("The 'event' designator is for special screens that do not gather information and can only be used with 'buttons' or with no other controls." + self.idebug(data))
        if 'default language' in data:
            should_append = False
            self.from_source.set_language(data['default language'])
        if 'sections' in data:
            should_append = False
            if type(data['sections']) is not list:
                raise DAError("A sections list must be a list." + self.idebug(data))
            if 'language' in data:
                the_language = data['language']
            else:
                the_language = '*'
            self.interview.sections[the_language] = data['sections']
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
        if 'usedefs' in data:
            defs = list()
            if type(data['usedefs']) is list:
                usedefs = data['usedefs']
            else:
                usedefs = [data['usedefs']]
            for usedef in usedefs:
                if type(usedef) in (dict, list, set, bool):
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
            self.continuelabel = TextObject(definitions + unicode(data['continue button label']), names_used=self.mako_names)
        if 'resume button label' in data:
            if 'review' not in data:
                raise DAError("You cannot set a resume button label if the type of question is not review." + self.idebug(data))
            self.continuelabel = TextObject(definitions + unicode(data['resume button label']), names_used=self.mako_names)
        if 'mandatory' in data:
            if data['mandatory'] is True:
                self.is_mandatory = True
                self.mandatory_code = None
            elif data['mandatory'] in (False, None):
                self.is_mandatory = False
                self.mandatory_code = None
            else:
                self.is_mandatory = False
                if type(data['mandatory']) in (str, unicode):
                    self.mandatory_code = compile(data['mandatory'], '<mandatory code>', 'eval')
                    self.find_fields_in(data['mandatory'])
                else:
                    self.mandatory_code = None
        else:
            self.is_mandatory = False
            self.mandatory_code = None
        if 'attachment options' in data:
            should_append = False
            if type(data['attachment options']) is not list:
                data['attachment options'] = [data['attachment options']]
            for attachment_option in data['attachment options']:
                if type(attachment_option) is not dict:
                    raise DAError("An attachment option must a dictionary." + self.idebug(data))
                for key in attachment_option:
                    value = attachment_option[key]
                    if key == 'initial yaml':
                        if 'initial_yaml' not in self.interview.attachment_options:
                            self.interview.attachment_options['initial_yaml'] = list()
                        if type(value) is list:
                            the_list = value
                        else:
                            the_list = [value]
                        for yaml_file in the_list:
                            if type(yaml_file) is not str:
                                raise DAError('An initial yaml file must be a string.' + self.idebug(data))
                            self.interview.attachment_options['initial_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
                    elif key == 'additional yaml':
                        if 'additional_yaml' not in self.interview.attachment_options:
                            self.interview.attachment_options['additional_yaml'] = list()
                        if type(value) is list:
                            the_list = value
                        else:
                            the_list = [value]
                        for yaml_file in the_list:
                            if type(yaml_file) is not str:
                                raise DAError('An additional yaml file must be a string.' + self.idebug(data))
                            self.interview.attachment_options['additional_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
                    elif key == 'template file':
                        if type(value) is not str:
                            raise DAError('The template file must be a string.' + self.idebug(data))
                        self.interview.attachment_options['template_file'] = FileInPackage(value, 'template', self.package)
                    elif key == 'rtf template file':
                        if type(value) is not str:
                            raise DAError('The rtf template file must be a string.' + self.idebug(data))
                        self.interview.attachment_options['rtf_template_file'] = FileInPackage(value, 'template', self.package)
                    elif key == 'docx reference file':
                        if type(value) is not str:
                            raise DAError('The docx reference file must be a string.' + self.idebug(data))
                        self.interview.attachment_options['docx_reference_file'] = FileInPackage(value, 'template', self.package)
        if 'script' in data:
            if type(data['script']) not in (str, unicode):
                raise DAError("A script section must be plain text." + self.idebug(data))
            self.script = TextObject(definitions + unicode(data['script']), names_used=self.mako_names)
        if 'css' in data:
            if type(data['css']) not in (str, unicode):
                raise DAError("A css section must be plain text." + self.idebug(data))
            self.css = TextObject(definitions + unicode(data['css']), names_used=self.mako_names)
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
                if type(data['initial']) in (str, unicode):
                    self.initial_code = compile(data['initial'], '<initial code>', 'eval')
                    self.find_fields_in(data['initial'])
                else:
                    self.initial_code = None
        else:
            self.is_initial = False
            self.initial_code = None
        if 'command' in data and data['command'] in ('exit', 'logout', 'continue', 'restart', 'leave', 'refresh', 'signin', 'register'):
            self.question_type = data['command']
            self.content = TextObject(data.get('url', ''), names_used=self.mako_names)
            return
        if 'objects from file' in data:
            if type(data['objects from file']) is not list:
                data['objects from file'] = [data['objects from file']]
            self.question_type = 'objects_from_file'
            self.objects_from_file = data['objects from file']
            for item in data['objects from file']:
                if type(item) is dict:
                    for key in item:
                        self.fields.append(Field({'saveas': key, 'type': 'object_from_file', 'file': item[key]}))
                        if self.scan_for_variables:
                            self.fields_used.add(key)
                else:
                    raise DAError("An objects section cannot contain a nested list." + self.idebug(data))
        if 'data' in data and 'variable name' in data:
            if type(data['variable name']) not in (str, unicode):
                raise DAError("A data block variable name must be plain text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['variable name'].strip())
            self.question_type = 'data'
            self.fields.append(Field({'saveas': data['variable name'].strip(), 'type': 'data', 'data': self.recursive_dataobject(data['data'])}))
        if 'data from code' in data and 'variable name' in data:
            if type(data['variable name']) not in (str, unicode):
                raise DAError("A data from code block variable name must be plain text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['variable name'])
            self.question_type = 'data_from_code'
            self.fields.append(Field({'saveas': data['variable name'], 'type': 'data_from_code', 'data': self.recursive_data_from_code(data['data from code'])}))
        if 'objects' in data:
            if type(data['objects']) is not list:
                data['objects'] = [data['objects']]
                #raise DAError("An objects section must be organized as a list." + self.idebug(data))
            self.question_type = 'objects'
            self.objects = data['objects']
            for item in data['objects']:
                if type(item) is dict:
                    for key in item:
                        self.fields.append(Field({'saveas': key, 'type': 'object', 'objecttype': item[key]}))
                        if self.scan_for_variables:
                            self.fields_used.add(key)
                else:
                    raise DAError("An objects section cannot contain a nested list." + self.idebug(data))
        if 'id' in data:
            # if unicode(data['id']) in self.interview.ids_in_use:
            #     raise DAError("The id " + unicode(data['id']) + " is already in use by another block.  Id names must be unique." + self.idebug(data))
            self.id = unicode(data['id']).strip()
            self.interview.ids_in_use.add(self.id)
            self.interview.questions_by_id[self.id] = self
        if 'supersedes' in data:
            if type(data['supersedes']) is not list:
                supersedes_list = [unicode(data['supersedes'])]
            else:
                supersedes_list = [unicode(x) for x in data['supersedes']]
            self.interview.id_orderings.append(dict(type="supersedes", question=self, supersedes=supersedes_list))
        if 'order' in data:
            should_append = False
            if 'question' in data or 'code' in data or 'attachment' in data or 'attachments' in data or 'template' in data:
                raise DAError("An 'order' block cannot be combined with another type of block." + self.idebug(data))
            if type(data['order']) is not list:
                raise DAError("An 'order' block must be a list." + self.idebug(data))
            self.interview.id_orderings.append(dict(type="order", order=[unicode(x) for x in data['order']]))
        for key in ('image sets', 'images'):
            if key not in data:
                continue
            should_append = False
            if type(data[key]) is not dict:
                raise DAError("The '" + key + "' section needs to be a dictionary, not a list or text." + self.idebug(data))
            if key == 'images':
                data[key] = {'unspecified': {'images': data[key]}}
            elif 'images' in data[key] and 'attribution' in data[key]:
                data[key] = {'unspecified': data[key]}
            for setname, image_set in data[key].iteritems():
                if type(image_set) is not dict:
                    if key == 'image sets':
                        raise DAError("Each item in the 'image sets' section needs to be a dictionary, not a list.  Each dictionary item should have an 'images' definition (which can be a dictionary or list) and an optional 'attribution' definition (which must be text)." + self.idebug(data))
                    else:
                        raise DAError("Each item in the 'images' section needs to be a dictionary, not a list." + self.idebug(data))
                if 'attribution' in image_set:
                    if type(image_set['attribution']) in (dict, list, set):
                        raise DAError("An attribution in an 'image set' section cannot be a dictionary or a list." + self.idebug(data))
                    attribution = image_set['attribution']
                else:
                    attribution = None
                if 'images' in image_set:
                    if type(image_set['images']) is list:
                        image_list = image_set['images']
                    elif type(image_set['images']) is dict:
                        image_list = [image_set['images']]
                    else:
                        if key == 'image set':
                            raise DAError("An 'images' definition in an 'image set' item must be a dictionary or a list." + self.idebug(data))
                        else:
                            raise DAError("An 'images' section must be a dictionary or a list." + self.idebug(data))                            
                    for image in image_list:
                        if type(image) is not dict:
                            the_image = {str(image): str(image)}
                        else:
                            the_image = image
                        for key, value in the_image.iteritems():
                            self.interview.images[key] = PackageImage(filename=value, attribution=attribution, setname=setname, package=self.package)
        if 'def' in data:
            should_append = False
            if type(data['def']) is not str:
                raise DAError("A def name must be a string." + self.idebug(data))
            if data['def'] not in self.interview.defs:
                self.interview.defs[data['def']] = list()
            if 'mako' in data:
                if type(data['mako']) is str:
                    list_of_defs = [data['mako']]
                elif type(data['mako']) is list:
                    list_of_defs = data['mako']
                else:
                    raise DAError("A mako template definition must be a string or a list of strings." + self.idebug(data))
                for definition in list_of_defs:
                    if type(definition) is not str:
                        raise DAError("A mako template definition must be a string." + self.idebug(data))
                    self.interview.defs[data['def']].append(definition)
        if 'interview help' in data:
            should_append = False
            if type(data['interview help']) is list:
                raise DAError("An interview help section must not be in the form of a list." + self.idebug(data))
            elif type(data['interview help']) is not dict:
                data['interview help'] = {'content': unicode(data['interview help'])}
            audiovideo = list()
            if 'label' in data['interview help']:
                data['interview help']['label'] = unicode(data['interview help']['label'])
            if 'audio' in data['interview help']:
                if type(data['interview help']['audio']) is not list:
                    the_list = [data['interview help']['audio']]
                else:
                    the_list = data['interview help']['audio']
                audiovideo = list()
                for the_item in the_list:
                    if type(the_item) in (list, dict):
                        raise DAError("An interview help audio section must be in the form of a text item or a list of text items." + self.idebug(data))
                    audiovideo.append({'text': TextObject(definitions + unicode(data['interview help']['audio']), names_used=self.mako_names), 'package': self.package, 'type': 'audio'})
            if 'video' in data['interview help']:
                if type(data['interview help']['video']) is not list:
                    the_list = [data['interview help']['video']]
                else:
                    the_list = data['interview help']['video']
                for the_item in the_list:
                    if type(the_item) in (list, dict):
                        raise DAError("An interview help video section must be in the form of a text item or a list of text items." + self.idebug(data))
                    audiovideo.append({'text': TextObject(definitions + unicode(data['interview help']['video']), names_used=self.mako_names), 'package': self.package, 'type': 'video'})
            if 'video' not in data['interview help'] and 'audio' not in data['interview help']:
                audiovideo = None
            if 'heading' in data['interview help']:
                if type(data['interview help']['heading']) not in (dict, list):
                    help_heading = TextObject(definitions + unicode(data['interview help']['heading']), names_used=self.mako_names)
                else:
                    raise DAError("A heading within an interview help section must be text, not a list or a dictionary." + self.idebug(data))
            else:
                help_heading = None
            if 'content' in data['interview help']:
                if type(data['interview help']['content']) not in (dict, list):
                    help_content = TextObject(definitions + unicode(data['interview help']['content']), names_used=self.mako_names)
                else:
                    raise DAError("Help content must be text, not a list or a dictionary." + self.idebug(data))
            else:
                raise DAError("No content section was found in an interview help section." + self.idebug(data))
            if 'label' in data['interview help']:
                if type(data['interview help']['label']) not in (dict, list):
                    help_label = TextObject(definitions + unicode(data['interview help']['label']), names_used=self.mako_names)
                else:
                    raise DAError("Help label must be text, not a list or a dictionary." + self.idebug(data))
            else:
                help_label = None
            if self.language not in self.interview.helptext:
                self.interview.helptext[self.language] = list()
            self.interview.helptext[self.language].append({'content': help_content, 'heading': help_heading, 'audiovideo': audiovideo, 'label': help_label, 'from': 'interview'})
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
            if type(data['metadata']) == dict:
                data['metadata']['origin_path'] = self.from_source.path
                self.interview.metadata.append(data['metadata'])
            else:
                raise DAError("A metadata section must be organized as a dictionary." + self.idebug(data))
        if 'modules' in data:
            if type(data['modules']) is str:
                data['modules'] = [data['modules']]
            if type(data['modules']) is list:
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
            if type(data['reset']) is str:
                data['reset'] = [data['reset']]
            if type(data['reset']) is list:
                self.question_type = 'reset'
                self.reset_list = data['reset']
            else:
                raise DAError("A reset section must be organized as a list." + self.idebug(data))
        if 'imports' in data:
            if type(data['imports']) is str:
                data['imports'] = [data['imports']]
            if type(data['imports']) is list:
                self.question_type = 'imports'
                self.module_list = data['imports']
            else:
                raise DAError("An imports section must be organized as a list." + self.idebug(data))
        if 'terms' in data and 'question' in data:
            if type(data['terms']) not in (dict, list):
                raise DAError("Terms must be organized as a dictionary or a list." + self.idebug(data))
            if type(data['terms']) is dict:
                data['terms'] = [data['terms']]
            for termitem in data['terms']:
                if type(termitem) is not dict:
                    raise DAError("A terms section organized as a list must be a list of dictionary items." + self.idebug(data))
                for term in termitem:
                    lower_term = term.lower()
                    self.terms[lower_term] = {'definition': TextObject(definitions + unicode(termitem[term]), names_used=self.mako_names), 're': re.compile(r"{(?i)(%s)}" % (lower_term,), re.IGNORECASE)}
        if 'auto terms' in data and 'question' in data:
            if type(data['auto terms']) not in (dict, list):
                raise DAError("Terms must be organized as a dictionary or a list." + self.idebug(data))
            if type(data['auto terms']) is dict:
                data['auto terms'] = [data['auto terms']]
            for termitem in data['auto terms']:
                if type(termitem) is not dict:
                    raise DAError("A terms section organized as a list must be a list of dictionary items." + self.idebug(data))
                for term in termitem:
                    lower_term = term.lower()
                    self.autoterms[lower_term] = {'definition': TextObject(definitions + unicode(termitem[term]), names_used=self.mako_names), 're': re.compile(r"{?(?i)\b(%s)\b}?" % (lower_term,), re.IGNORECASE)}
        if 'terms' in data and 'question' not in data:
            should_append = False
            if self.language not in self.interview.terms:
                self.interview.terms[self.language] = dict()
            if type(data['terms']) is list:
                for termitem in data['terms']:
                    if type(termitem) is dict:
                        for term in termitem:
                            lower_term = term.lower()
                            self.interview.terms[self.language][lower_term] = {'definition': termitem[term], 're': re.compile(r"{(?i)(%s)}" % (lower_term,), re.IGNORECASE)}
                    else:
                        raise DAError("A terms section organized as a list must be a list of dictionary items." + self.idebug(data))
            elif type(data['terms']) is dict:
                for term in data['terms']:
                    lower_term = term.lower()
                    self.interview.terms[self.language][lower_term] = {'definition': data['terms'][term], 're': re.compile(r"{(?i)(%s)}" % (lower_term,), re.IGNORECASE)}
            else:
                raise DAError("A terms section must be organized as a dictionary or a list." + self.idebug(data))
        if 'auto terms' in data and 'question' not in data:
            should_append = False
            if self.language not in self.interview.autoterms:
                self.interview.autoterms[self.language] = dict()
            if type(data['auto terms']) is list:
                for termitem in data['auto terms']:
                    if type(termitem) is dict:
                        for term in termitem:
                            lower_term = term.lower()
                            self.interview.autoterms[self.language][lower_term] = {'definition': termitem[term], 're': re.compile(r"{?(?i)\b(%s)\b}?" % (lower_term,), re.IGNORECASE)}
                    else:
                        raise DAError("An auto terms section organized as a list must be a list of dictionary items." + self.idebug(data))
            elif type(data['auto terms']) is dict:
                for term in data['auto terms']:
                    lower_term = term.lower()
                    self.interview.autoterms[self.language][lower_term] = {'definition': data['auto terms'][term], 're': re.compile(r"{?(?i)\b(%s)\b}?" % (lower_term,), re.IGNORECASE)}
            else:
                raise DAError("An auto terms section must be organized as a dictionary or a list." + self.idebug(data))
        if 'default role' in data:
            if 'code' not in data:
                should_append = False
            if type(data['default role']) is str:
                self.interview.default_role = [data['default role']]
            elif type(data['default role']) is list:
                self.interview.default_role = data['default role']
            else:
                raise DAError("A default role must be a list or a string." + self.idebug(data))
        if 'role' in data:
            if type(data['role']) is str:
                if data['role'] not in self.role:
                    self.role.append(data['role'])
            elif type(data['role']) is list:
                for rolename in data['role']:
                    if data['role'] not in self.role:
                        self.role.append(rolename)
            else:
                raise DAError("The role of a question must be a string or a list." + self.idebug(data))
        else:
            self.role = list()
        if 'include' in data:
            should_append = False
            if type(data['include']) is str:
                data['include'] = [data['include']]
            if type(data['include']) is list:
                for questionPath in data['include']:
                    self.interview.read_from(interview_source_from_string(questionPath, context_interview=self.interview))
            else:
                raise DAError("An include section must be organized as a list." + self.idebug(data))
        if 'if' in data:
            if type(data['if']) == str:
                self.condition = [compile(data['if'], '<if code>', 'eval')]
                self.find_fields_in(data['if'])
            elif type(data['if']) == list:
                self.condition = [compile(x, '<if code>', 'eval') for x in data['if']]
                for x in data['if']:
                    self.find_fields_in(x)
            else:
                raise DAError("An if statement must either be text or a list." + self.idebug(data))
        if 'validation code' in data:
            if type(data['validation code']) not in (str, unicode):
                raise DAError("A validation code statement must be text." + self.idebug(data))
            self.validation_code = compile(data['validation code'], '<code block>', 'exec')
            self.find_fields_in(data['validation code'])
        if 'require' in data:
            if type(data['require']) is list:
                self.question_type = 'require'
                try:
                    self.require_list = list(map((lambda x: compile(x, '<require code>', 'eval')), data['require']))
                    for x in data['require']:
                        self.find_fields_in(x)
                except:
                    logmessage("Compile error in require:\n" + str(data['require']) + "\n" + str(sys.exc_info()[0]))
                    raise
                if 'orelse' in data:
                    if type(data['orelse']) is dict:
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
        # if 'role' in data:
        #     if type(data['role']) is list:
        #         for rolename in data['role']:
        #             if rolename not in self.role:
        #                 self.role.append(rolename)
        #     elif type(data['role']) is str and data['role'] not in self.role:
        #         self.role.append(data['role'])
        #     else:
        #         raise DAError("A role section must be text or a list." + self.idebug(data))
        if 'progress' in data:
            self.progress = data['progress']
        if 'action' in data:
            self.question_type = 'backgroundresponseaction'
            self.content = TextObject('action')
            self.action = data['action']
        if 'backgroundresponse' in data:
            self.question_type = 'backgroundresponse'
            self.content = TextObject('backgroundresponse')
            self.backgroundresponse = data['backgroundresponse']
        if 'response' in data:
            self.content = TextObject(definitions + unicode(data['response']), names_used=self.mako_names)
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
                self.content_type = TextObject(definitions + unicode(data['content type']), names_used=self.mako_names)
            elif not (hasattr(self, 'content_type') and self.content_type):
                if self.response_file is not None:
                    self.content_type = TextObject(get_mimetype(self.response_file.path()))
                else:
                    self.content_type = TextObject('text/plain; charset=utf-8')
        elif 'redirect url' in data:
            self.question_type = 'redirect'
            self.content = TextObject(definitions + unicode(data['redirect url']), names_used=self.mako_names)
        if 'response' in data or 'binaryresponse' in data or 'all_variables' in data:
            if 'content type' in data:
                self.content_type = TextObject(definitions + unicode(data['content type']), names_used=self.mako_names)
            else:
                self.content_type = TextObject('text/plain; charset=utf-8')
        if 'question' in data:
            self.content = TextObject(definitions + unicode(data['question']), names_used=self.mako_names)
        if 'subquestion' in data:
            self.subcontent = TextObject(definitions + unicode(data['subquestion']), names_used=self.mako_names)
        if 'reload' in data and data['reload']:
            self.reload_after = TextObject(definitions + unicode(data['reload']), names_used=self.mako_names)
        if 'help' in data:
            if type(data['help']) is dict:
                for key, value in data['help'].iteritems():
                    if key == 'label':
                        self.helplabel = TextObject(definitions + unicode(value), names_used=self.mako_names)
                    if key == 'audio':
                        if type(value) is not list:
                            the_list = [value]
                        else:
                            the_list = value
                        for list_item in the_list:
                            if type(list_item) in (dict, list, set):
                                raise DAError("An audio declaration in a help block can only contain a text item or a list of text items." + self.idebug(data))
                            if self.audiovideo is None:
                                self.audiovideo = dict()
                            if 'help' not in self.audiovideo:
                                self.audiovideo['help'] = list()
                            self.audiovideo['help'].append({'text': TextObject(definitions + unicode(list_item.strip()), names_used=self.mako_names), 'package': self.package, 'type': 'audio'})
                    if key == 'video':
                        if type(value) is not list:
                            the_list = [value]
                        else:
                            the_list = value
                        for list_item in the_list:
                            if type(list_item) in (dict, list, set):
                                raise DAError("A video declaration in a help block can only contain a text item or a list of text items." + self.idebug(data))
                            if self.audiovideo is None:
                                self.audiovideo = dict()
                            if 'help' not in self.audiovideo:
                                self.audiovideo['help'] = list()
                            self.audiovideo['help'].append({'text': TextObject(definitions + unicode(list_item.strip()), names_used=self.mako_names), 'package': self.package, 'type': 'video'})
                    if key == 'content':
                        if type(value) in (dict, list, set):
                            raise DAError("A content declaration in a help block can only contain text." + self.idebug(data))
                        self.helptext = TextObject(definitions + unicode(value), names_used=self.mako_names)
            else:
                self.helptext = TextObject(definitions + unicode(data['help']), names_used=self.mako_names)
        if 'audio' in data:
            if type(data['audio']) is not list:
                the_list = [data['audio']]
            else:
                the_list = data['audio']
            for list_item in the_list:
                if type(list_item) in (dict, list, set):
                    raise DAError("An audio declaration can only contain a text item or a list of text items." + self.idebug(data))
                if self.audiovideo is None:
                    self.audiovideo = dict()    
                if 'question' not in self.audiovideo:
                    self.audiovideo['question'] = list()
                self.audiovideo['question'].append({'text': TextObject(definitions + unicode(list_item.strip()), names_used=self.mako_names), 'package': self.package, 'type': 'audio'})
        if 'video' in data:
            if type(data['video']) is not list:
                the_list = [data['video']]
            else:
                the_list = data['video']
            for list_item in the_list:
                if type(list_item) in (dict, list, set):
                    raise DAError("A video declaration can only contain a text item or a list of text items." + self.idebug(data))
                if self.audiovideo is None:
                    self.audiovideo = dict()    
                if 'question' not in self.audiovideo:
                    self.audiovideo['question'] = list()
                self.audiovideo['question'].append({'text': TextObject(definitions + unicode(list_item.strip()), names_used=self.mako_names), 'package': self.package, 'type': 'video'})
        if 'decoration' in data:
            if type(data['decoration']) is dict:
                decoration_list = [data['decoration']]
            elif type(data['decoration']) is list:
                decoration_list = data['decoration']
            else:
                decoration_list = [{'image': str(data['decoration'])}]
            processed_decoration_list = []
            for item in decoration_list:
                if type(item) is dict:
                    the_item = item
                else:
                    the_item = {'image': str(item.rstrip())}
                item_to_add = dict()
                for key, value in the_item.iteritems():
                    item_to_add[key] = TextObject(value, names_used=self.mako_names)
                processed_decoration_list.append(item_to_add)
            self.decorations = processed_decoration_list
        if 'signature' in data:
            self.question_type = 'signature'
            self.fields.append(Field({'saveas': data['signature']}))
            if self.scan_for_variables:
                self.fields_used.add(data['signature'])
        if 'under' in data:
            self.undertext = TextObject(definitions + unicode(data['under']), names_used=self.mako_names)
        if 'check in' in data:
            self.interview.uses_action = True
            if type(data['check in']) in (dict, list, set):
                raise DAError("A check in event must be text or a list." + self.idebug(data))
            self.checkin = str(data['check in'])
            self.names_used.add(str(data['check in']))
        if 'yesno' in data:
            self.fields.append(Field({'saveas': data['yesno'], 'boolean': 1}))
            if self.scan_for_variables:
                self.fields_used.add(data['yesno'])
            self.question_type = 'yesno'
        if 'noyes' in data:
            self.fields.append(Field({'saveas': data['noyes'], 'boolean': -1}))
            if self.scan_for_variables:
                self.fields_used.add(data['noyes'])
            self.question_type = 'noyes'
        if 'yesnomaybe' in data:
            self.fields.append(Field({'saveas': data['yesnomaybe'], 'threestate': 1}))
            if self.scan_for_variables:
                self.fields_used.add(data['yesnomaybe'])
            self.question_type = 'yesnomaybe'
        if 'noyesmaybe' in data:
            self.fields.append(Field({'saveas': data['noyesmaybe'], 'threestate': -1}))
            if self.scan_for_variables:
                self.fields_used.add(data['noyesmaybe'])
            self.question_type = 'noyesmaybe'
        if 'sets' in data:
            if type(data['sets']) is str:
                self.fields_used.add(data['sets'])
            elif type(data['sets']) is list:
                for key in data['sets']:
                    self.fields_used.add(key)
            else:
                raise DAError("A sets phrase must be text or a list." + self.idebug(data))
        if 'event' in data:
            self.interview.uses_action = True
            if type(data['event']) is str:
                self.fields_used.add(data['event'])
            elif type(data['event']) is list:
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
                    field_data['default'] = TextObject(definitions + unicode(data['default']), names_used=self.mako_names)
            elif 'buttons' in data:
                has_code, choices = self.parse_fields(data['buttons'], register_target, uses_field)
                field_data = {'choices': choices, 'shuffle': shuffle}
                if has_code:
                    field_data['has_code'] = True
                self.question_variety = 'buttons'
            if uses_field:
                data['field'] = data['field'].strip()
                if invalid_variable_name(data['field']):
                    raise DAError("Missing or invalid variable name " + repr(data['field']) + "." + self.idebug(data))
                if self.scan_for_variables:
                    self.fields_used.add(data['field'])
                field_data['saveas'] = data['field']
                if 'datatype' in data and 'type' not in field_data:
                    field_data['type'] = data['datatype']
                elif is_boolean(field_data):
                    field_data['type'] = 'boolean'
                elif is_threestate(field_data):
                    field_data['type'] = 'threestate'
            self.fields.append(Field(field_data))
            self.question_type = 'multiple_choice'
        elif 'field' in data:
            if type(data['field']) not in (str, unicode):
                raise DAError("A field must be plain text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['field'])
            field_data = {'saveas': data['field']}
            self.fields.append(Field(field_data))
            self.question_type = 'settrue'
        if 'need' in data:
            if type(data['need']) == str:
                need_list = [data['need']]
            elif type(data['need']) == list:
                need_list = data['need']
            else:
                raise DAError("A need phrase must be text or a list." + self.idebug(data))
            try:
                self.need = list(map((lambda x: compile(x, '<code block>', 'exec')), need_list))
                for x in need_list:
                    self.find_fields_in(x)
            except:
                logmessage("Question: compile error in need code:\n" + str(data['need']) + "\n" + str(sys.exc_info()[0]))
                raise
        if 'target' in data:
            self.interview.uses_action = True
            if type(data['target']) in (list, dict, set, bool, int, float):
                raise DAError("The target of a template must be plain text." + self.idebug(data))
            if 'template' not in data:
                raise DAError("A target directive can only be used with a template." + self.idebug(data))
            self.target = data['target']
        if 'table' in data or 'rows' in data or 'columns' in data:
            if 'table' not in data or 'rows' not in data or 'columns' not in data:
                raise DAError("A table definition must have definitions for table, row, and column." + self.idebug(data))
            if type(data['rows']) in (list, dict, set, bool, int, float):
                raise DAError("The row part of a table definition must be plain Python code." + self.idebug(data))
            if type(data['columns']) is not list:
                raise DAError("The column part of a table definition must be a list." + self.idebug(data))
            # if 'header' in data:
            #     if type(data['header']) is not list:
            #         raise DAError("The header part of a table definition must be a list." + self.idebug(data))
            #     if len(data['header']) != len(data['column']):
            #         raise DAError("The header part of a table definition must be the same length as the column part." + self.idebug(data))
            #     header = list(map(lambda x: TextObject(definitions + unicode(x), names_used=self.mako_names), data['header']))
            # else:
            #     header = list(map(lambda x: TextObject('&nbsp;'), data['column']))
            row = compile(data['rows'], '<row code>', 'eval')
            self.find_fields_in(data['rows'])
            header = list()
            column = list()
            for col in data['columns']:
                if type(col) is not dict:
                    raise DAError("The column items in a table definition must be dictionaries." + self.idebug(data))
                if len(col) == 0:
                    raise DAError("A column item in a table definition cannot be empty." + self.idebug(data))
                if 'header' in col and 'cell' in col:
                    header_text = col['header']
                    cell_text = col['cell']
                else:
                    for key, val in col.iteritems():
                        header_text = key
                        cell_text = val
                        break
                if header_text == '':
                    header.append(TextObject('&nbsp;'))
                else:
                    header.append(TextObject(definitions + unicode(header_text), names_used=self.mako_names))
                self.find_fields_in(cell_text)
                column.append(compile(cell_text, '<column code>', 'eval'))
            #column = list(map(lambda x: compile(x, '<expression>', 'eval'), data['column']))
            if self.scan_for_variables:
                self.fields_used.add(data['table'])
            empty_message = data.get('show if empty', True)
            if empty_message not in (True, False, None):
                empty_message = TextObject(definitions + unicode(empty_message), names_used=self.mako_names)
            field_data = {'saveas': data['table'], 'extras': dict(header=header, row=row, column=column, empty_message=empty_message, indent=data.get('indent', False))}
            self.fields.append(Field(field_data))
            self.content = TextObject('')
            self.subcontent = TextObject('')
            self.question_type = 'table'
            if self.scan_for_variables:
                self.reset_list = self.fields_used
        if 'template' in data and 'content file' in data:
            if type(data['content file']) is not list:
                data['content file'] = [data['content file']]
            data['content'] = ''
            for content_file in data['content file']:
                if type(content_file) is not str:
                    raise DAError('A content file must be specified as text or a list of text filenames' + self.idebug(data))
                file_to_read = docassemble.base.functions.package_template_filename(content_file, package=self.package)
                if get_mimetype(file_to_read) != 'text/markdown':
                    raise DAError('The content file ' + str(target['content file']) + ' is not a markdown file ' + str(file_to_read) + self.idebug(data))
                if file_to_read is not None and os.path.isfile(file_to_read) and os.access(file_to_read, os.R_OK):
                    with open(file_to_read, 'rU') as the_file:
                        data['content'] += the_file.read().decode('utf8')
                else:
                    raise DAError('Unable to read content file ' + str(target['content file']) + ' after trying to find it at ' + str(file_to_read) + self.idebug(data))
        if 'template' in data and 'content' in data:
            if type(data['template']) in (list, dict):
                raise DAError("A template must designate a single variable expressed as text." + self.idebug(data))
            if type(data['content']) in (list, dict):
                raise DAError("The content of a template must be expressed as text." + self.idebug(data))
            if self.scan_for_variables:
                self.fields_used.add(data['template'])
            field_data = {'saveas': data['template']}
            self.fields.append(Field(field_data))
            self.content = TextObject(definitions + unicode(data['content']), names_used=self.mako_names)
            #logmessage("keys are: " + str(self.mako_names))
            if 'subject' in data:
                self.subcontent = TextObject(definitions + unicode(data['subject']), names_used=self.mako_names)
            else:
                self.subcontent = TextObject("")
            self.question_type = 'template'
            if self.scan_for_variables:
                self.reset_list = self.fields_used
        if 'code' in data:
            if 'event' in data:
                self.question_type = 'event_code'
            else:
                self.question_type = 'code'
            if type(data['code']) in (str, unicode):
                if not self.interview.calls_process_action and match_process_action.search(data['code']):
                    self.interview.calls_process_action = True
                try:
                    self.compute = compile(data['code'], '<code block>', 'exec')
                    self.sourcecode = data['code']
                except:
                    logmessage("Question: compile error in code:\n" + unicode(data['code']) + "\n" + str(sys.exc_info()[0]))
                    raise
                if self.question_type == 'code':
                    self.find_fields_in(data['code'])
            else:
                raise DAError("A code section must be text, not a list or a dictionary." + self.idebug(data))
            if 'reconsider' in data:
                if type(data['reconsider']) is not bool:
                    raise DAError("A reconsider designation must be true or false." + self.idebug(data))
                if data['reconsider'] is True:
                    if self.is_generic:
                        if self.generic_object not in self.interview.reconsider_generic:
                            self.interview.reconsider_generic[self.generic_object] = set()
                        self.interview.reconsider_generic[self.generic_object].update(self.fields_used)
                    else:
                        self.interview.reconsider.update(self.fields_used)
        if 'fields' in data:
            self.question_type = 'fields'
            if type(data['fields']) is dict:
                data['fields'] = [data['fields']]
            if type(data['fields']) is not list:
                raise DAError("The fields must be written in the form of a list." + self.idebug(data))
            else:
                field_number = 0
                for field in data['fields']:
                    if type(field) is dict:
                        manual_keys = set()
                        field_info = {'type': 'text', 'number': field_number}
                        if len(field) == 1 and 'code' in field:
                            field_info['type'] = 'fields_code'
                            self.find_fields_in(field['code'])
                            field_info['extras'] = dict(fields_code=compile(field['code'], '<fields code>', 'eval'))
                            self.fields.append(Field(field_info))
                            continue
                        if 'datatype' in field and field['datatype'] in ('radio', 'object', 'object_radio', 'combobox', 'checkboxes', 'object_checkboxes') and not ('choices' in field or 'code' in field):
                            raise DAError("A multiple choice field must refer to a list of choices." + self.idebug(data))
                        for key in field:
                            if key == 'default' and 'datatype' in field and field['datatype'] in ('object', 'object_radio', 'object_checkboxes'):
                                continue
                            if 'datatype' in field and field['datatype'] in ('ml', 'mlarea') and key in ('using', 'keep for training'):
                                if key == 'using':
                                    if 'extras' not in field_info:
                                        field_info['extras'] = dict()
                                    field_info['extras']['ml_group'] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                                if key == 'keep for training':
                                    if 'extras' not in field_info:
                                        field_info['extras'] = dict()
                                    if type(field[key]) is bool:
                                        field_info['extras']['ml_train'] = field[key]
                                    else:
                                        field_info['extras']['ml_train'] = {'compute': compile(field[key], '<keep for training code>', 'eval'), 'sourcecode': field[key]}
                                        self.find_fields_in(field[key])
                            elif key == 'validate':
                                field_info['validate'] = {'compute': compile(field[key], '<validate code>', 'eval'), 'sourcecode': field[key]}
                                self.find_fields_in(field[key])
                            elif 'datatype' in field and field['datatype'] in ('file', 'files', 'camera', 'user', 'environment') and key == 'maximum image size':
                                field_info['max_image_size'] = {'compute': compile(unicode(field[key]), '<maximum image size code>', 'eval'), 'sourcecode': unicode(field[key])}
                                self.find_fields_in(field[key])
                            elif key == 'required':
                                if type(field[key]) is bool:
                                    field_info['required'] = field[key]
                                else:
                                    field_info['required'] = {'compute': compile(field[key], '<required code>', 'eval'), 'sourcecode': field[key]}
                                    self.find_fields_in(field[key])
                            elif key == 'show if' or key == 'hide if':
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                if type(field[key]) is dict:
                                    if 'variable' in field[key] and 'is' in field[key]:
                                        field_info['extras']['show_if_var'] = safeid(field[key]['variable'])
                                        field_info['extras']['show_if_val'] = TextObject(definitions + unicode(field[key]['is']), names_used=self.mako_names)
                                    elif 'code' in field[key]:
                                        field_info['showif_code'] = compile(field[key]['code'], '<show if code>', 'eval')
                                        self.find_fields_in(field[key]['code'])
                                    else:
                                        raise DAError("The keys of '" + key + "' must be 'variable' and 'is.'" + self.idebug(data))
                                elif type(field[key]) is list:
                                    raise DAError("The keys of '" + key + "' cannot be a list" + self.idebug(data))
                                elif type(field[key]) in (str, unicode):
                                    field_info['extras']['show_if_var'] = safeid(field[key])
                                    field_info['extras']['show_if_val'] = TextObject('True')
                                else:
                                    raise DAError("Invalid variable name in show if/hide if")
                                if key == 'show if':
                                    field_info['extras']['show_if_sign'] = 1
                                else:
                                    field_info['extras']['show_if_sign'] = 0
                            elif key == 'default' or key == 'hint' or key == 'help':
                                if type(field[key]) is not dict and type(field[key]) is not list:
                                    field_info[key] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                                if key == 'default':
                                    if type(field[key]) is dict and 'code' in field[key]:
                                        if 'extras' not in field_info:
                                            field_info['extras'] = dict()
                                        field_info['extras']['default'] = {'compute': compile(field[key]['code'], '<default code>', 'eval'), 'sourcecode': field[key]['code']}
                                        self.find_fields_in(field[key]['code'])
                                    else:
                                        if type(field[key]) in (dict, list):
                                            field_info[key] = field[key]
                                        if 'datatype' not in field and 'code' not in field and 'choices' not in field:
                                            auto_determine_type(field_info, the_value=field[key])
                            elif key == 'disable others':
                                field_info['disable others'] = True
                                field_info['required'] = False
                            elif key == 'uncheck others' and 'datatype' in field and field['datatype'] in ('yesno', 'yesnowide', 'noyes', 'noyeswide'):
                                if type(field[key]) not in (list, bool):
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
                                    if type(field['exclude']) is dict:
                                        raise DAError("An exclude entry cannot be a dictionary." + self.idebug(data))
                                    if type(field['exclude']) is not list:
                                        field_info['selections']['exclude'] = [compile(field['exclude'], '<expression>', 'eval')]
                                        self.find_fields_in(field['exclude'])
                                    else:
                                        field_info['selections']['exclude'] = list()
                                        for x in field['exclude']:
                                            field_info['selections']['exclude'].append(compile(x, '<expression>', 'eval'))
                                            self.find_fields_in(x)
                            elif key == 'address autocomplete':
                                field_info['address_autocomplete'] = True
                            elif key == 'exclude':
                                pass
                            elif key == 'choices':
                                if 'datatype' in field and field['datatype'] in ('object', 'object_radio', 'object_checkboxes'):
                                    field_info['choicetype'] = 'compute'
                                    if type(field[key]) not in (list, str):
                                        raise DAError("choices is not in appropriate format" + self.idebug(data))
                                    field_info['selections'] = dict()
                                else:
                                    field_info['choicetype'] = 'manual'
                                    field_info['selections'] = dict(values=process_selections_manual(field[key]))
                                    if 'datatype' not in field:
                                        auto_determine_type(field_info)
                                    for item in field_info['selections']['values']:
                                        if not item['key'].uses_mako:
                                            manual_keys.add(item['key'].original_text)
                                if 'exclude' in field:
                                    if type(field['exclude']) is dict:
                                        raise DAError("An exclude entry cannot be a dictionary." + self.idebug(data))
                                    if type(field['exclude']) is not list:
                                        self.find_fields_in(field['exclude'])
                                        field_info['selections']['exclude'] = [compile(field['exclude'].strip(), '<expression>', 'eval')]
                                    else:
                                        field_info['selections']['exclude'] = list()
                                        for x in field['exclude']:
                                            self.find_fields_in(x)
                                            field_info['selections']['exclude'].append(compile(x, '<expression>', 'eval'))
                            elif key == 'note':
                                field_info['type'] = 'note'
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['extras']['note'] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                            elif key in ('min', 'max', 'minlength', 'maxlength', 'step', 'inline width'):
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['extras'][key] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                            elif key == 'html':
                                if 'extras' not in field_info:
                                    field_info['extras'] = dict()
                                field_info['type'] = 'html'
                                field_info['extras'][key] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                            # elif key in ('css', 'script'):
                            #     if 'extras' not in field_info:
                            #         field_info['extras'] = dict()
                            #     if field_info['type'] == 'text':
                            #         field_info['type'] = key
                            #     field_info['extras'][key] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                            elif key == 'shuffle':
                                field_info['shuffle'] = field[key]
                            elif key == 'none of the above' and 'datatype' in field and field['datatype'] in ('checkboxes', 'object_checkboxes'):
                                if type(field[key]) is bool:
                                    field_info['nota'] = field[key]
                                else:
                                    field_info['nota'] = TextObject(definitions + interpret_label(field[key]), names_used=self.mako_names)
                            elif key == 'field':
                                if 'label' not in field:
                                    raise DAError("If you use 'field' to indicate a variable in a 'fields' section, you must also include a 'label.'" + self.idebug(data))
                                field[key] = field[key].strip()
                                if invalid_variable_name(field[key]):
                                    raise DAError("Missing or invalid variable name " + repr(field[key]) + "." + self.idebug(data))
                                field_info['saveas'] = field[key]                                
                            elif key == 'label':
                                if 'field' not in field:
                                    raise DAError("If you use 'label' to label a field in a 'fields' section, you must also include a 'field.'" + self.idebug(data))                                    
                                field_info['label'] = TextObject(definitions + interpret_label(field[key]), names_used=self.mako_names)
                            else:
                                if 'label' in field_info:
                                    raise DAError("Syntax error: field label '" + str(key) + "' overwrites previous label, '" + str(field_info['label'].original_text) + "'" + self.idebug(data))
                                field_info['label'] = TextObject(definitions + interpret_label(key), names_used=self.mako_names)
                                field[key] = field[key].strip()
                                if invalid_variable_name(field[key]):
                                    raise DAError("Missing or invalid variable name " + repr(field[key]) + " for key " + repr(key) + "." + self.idebug(data))
                                field_info['saveas'] = field[key]
                        if 'type' in field_info and field_info['type'] in ('checkboxes', 'object_checkboxes') and 'nota' not in field_info:
                            field_info['nota'] = True
                        if 'choicetype' in field_info and field_info['choicetype'] == 'compute' and 'type' in field_info and field_info['type'] in ('object', 'object_radio', 'object_checkboxes'):
                            if 'choices' not in field:
                                raise DAError("You need to have a choices element if you want to set a variable to an object." + self.idebug(data))
                            if type(field['choices']) is not list:
                                select_list = [str(field['choices'])]
                            else:
                                select_list = field['choices']
                            if 'exclude' in field:
                                if type(field['exclude']) is dict:
                                    raise DAError("choices exclude list is not in appropriate format" + self.idebug(data))
                                if type(field['exclude']) is not list:
                                    exclude_list = [str(field['exclude']).strip()]
                                else:
                                    exclude_list = [x.strip() for x in field['exclude']]
                                if len(exclude_list):
                                    select_list.append('exclude=[' + ", ".join(exclude_list) + ']')
                            if 'default' in field:
                                if type(field['default']) not in (list, str):
                                    raise DAError("default list is not in appropriate format" + self.idebug(data))
                                if type(field['default']) is not list:
                                    default_list = [str(field['default'])]
                                else:
                                    default_list = field['default']
                            else:
                                default_list = list()
                            if field_info['type'] == 'object_checkboxes':
                                default_list.append('_DAOBJECTDEFAULTDA')
                            if len(default_list):
                                select_list.append('default=[' + ", ".join(default_list) + ']')
                            source_code = "docassemble.base.core.selections(" + ", ".join(select_list) + ")"
                            #logmessage("source_code is " + source_code)
                            field_info['selections'] = {'compute': compile(source_code, '<expression>', 'eval'), 'sourcecode': source_code}
                        if 'saveas' in field_info:
                            if type(field_info['saveas']) not in (str, unicode):
                                raise DAError("Invalid variable name " + repr(field_info['saveas']) + "." + self.idebug(data))
                            self.fields.append(Field(field_info))
                            if 'type' in field_info:
                                if field_info['type'] in ('checkboxes', 'object_checkboxes'):
                                    if self.scan_for_variables:
                                        self.fields_used.add(field_info['saveas'])
                                        self.fields_used.add(field_info['saveas'] + '.gathered')
                                        if field_info['type'] == 'checkboxes':
                                            for the_key in manual_keys:
                                                self.fields_used.add(field_info['saveas'] + '[' + repr(the_key) + ']')
                                elif field_info['type'] in ('ml', 'mlarea'):
                                    if self.scan_for_variables:
                                        self.fields_used.add(field_info['saveas'])
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
                                        if self.scan_for_variables:
                                            self.fields_used.add(field_info['saveas'] + '.text')
                                else:
                                    if self.scan_for_variables:
                                        self.fields_used.add(field_info['saveas'])
                            else:
                                if self.scan_for_variables:
                                    self.fields_used.add(field_info['saveas'])
                        elif 'type' in field_info and field_info['type'] in ('note', 'html'): #, 'script', 'css'
                            self.fields.append(Field(field_info))
                        else:
                            raise DAError("A field was listed without indicating a label or a variable name, and the field was not a note or raw HTML." + self.idebug(data))
                    else:
                        raise DAError("Each individual field in a list of fields must be expressed as a dictionary item, e.g., ' - Fruit: user.favorite_fruit'." + self.idebug(data))
                    field_number += 1
        if 'review' in data:
            self.question_type = 'review'
            if type(data['review']) is dict:
                data['review'] = [data['review']]
            if type(data['review']) is not list:
                raise DAError("The review must be written in the form of a list." + self.idebug(data))
            field_number = 0
            for field in data['review']:
                if type(field) is not dict:
                    raise DAError("Each individual field in a list of fields must be expressed as a dictionary item, e.g., ' - Fruit: user.favorite_fruit'." + self.idebug(data))
                field_info = {'number': field_number}
                for key in field:
                    if key == 'action':
                        continue
                    elif key == 'help':
                        if type(field[key]) is not dict and type(field[key]) is not list:
                            field_info[key] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                        if 'button' in field or 'note' in field or 'html' in field: #or 'css' in field or 'script' in field:
                            raise DAError("In a review block, you cannot mix help text with note, or html items." + self.idebug(data)) #, css, or script
                    elif key == 'button':
                        if type(field[key]) is not dict and type(field[key]) is not list:
                            field_info['help'] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                            field_info['type'] = 'button'
                    elif key == 'note':
                        field_info['type'] = 'note'
                        if 'extras' not in field_info:
                            field_info['extras'] = dict()
                        field_info['extras']['note'] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                    elif key == 'html':
                        if 'extras' not in field_info:
                            field_info['extras'] = dict()
                        field_info['type'] = 'html'
                        field_info['extras'][key] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                    # elif key in ('css', 'script'):
                    #     if 'extras' not in field_info:
                    #         field_info['extras'] = dict()
                    #     if field_info['type'] == 'text':
                    #         field_info['type'] = key
                    #     field_info['extras'][key] = TextObject(definitions + unicode(field[key]), names_used=self.mako_names)
                    elif key == 'show if':
                        field_info['saveas_code'] = compile(field[key], '<expression>', 'eval')
                        self.find_fields_in(field[key])
                        field[key] = field[key].strip()
                        if invalid_variable_name(field[key]):
                            raise DAError("Missing or invalid variable name " + repr(field[key]) + "." + self.idebug(data))
                        field_info['saveas'] = field[key]
                    elif key == 'field':
                        if 'label' not in field:
                            raise DAError("If you use 'field' to indicate a variable in a 'review' section, you must also include a 'label.'" + self.idebug(data))
                        field[key] = field[key].strip()
                        if invalid_variable_name(field[key]):
                            raise DAError("Missing or invalid variable name " + repr(field[key]) + " ." + self.idebug(data))
                        field_info['saveas'] = field[key]
                    elif key == 'label':
                        if 'field' not in field:
                            raise DAError("If you use 'label' to label a field in a 'fields' section, you must also include a 'field.'" + self.idebug(data))                                    
                        field_info['label'] = TextObject(definitions + interpret_label(field[key]), names_used=self.mako_names)
                    else:
                        field_info['label'] = TextObject(definitions + interpret_label(key), names_used=self.mako_names)
                        field[key] = field[key].strip()
                        if invalid_variable_name(field[key]):
                            raise DAError("Missing or invalid variable name " + repr(field[key]) + "." + self.idebug(data))
                        field_info['saveas'] = field[key]
                        if 'action' in field:
                            field_info['action'] = field['action']
                        else:
                            field_info['action'] = field[key]
                        field_info['saveas_code'] = compile(field[key], '<expression>', 'eval')
                        self.find_fields_in(field[key])
                if 'saveas' in field_info or ('type' in field_info and field_info['type'] in ('note', 'html')): #, 'script', 'css'
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
                #     raise DAError("Question ID " + unicode(self.id) + " results in duplicate question name")
            else:
                self.name = "Question_" + str(self.number)
        # if hasattr(self, 'id'):
        #     try:
        #         self.interview.questions_by_id[self.id].append(self)
        #     except:
        #         self.interview.questions_by_id[self.id] = [self]
        if self.name is not None:
            self.interview.questions_by_name[self.name] = self
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
        if len(self.attachments):
            indexno = 0
            for att in self.attachments:
                att['question_name'] = self.name
                att['indexno'] = indexno
                indexno += 1
        self.data_for_debug = data
    def exec_setup(self, is_generic, the_x, iterators, user_dict):
        if is_generic:
            if the_x != 'None':
                exec("x = " + the_x, user_dict)
        if len(iterators):
            for indexno in range(len(iterators)):
                exec(list_of_indices[indexno] + " = " + iterators[indexno], user_dict)
        if self.need is not None:
            for need_code in self.need:
                exec(need_code, user_dict)
    def recursive_data_from_code(self, target):
        if type(target) is dict or (hasattr(target, 'elements') and type(target.elements) is dict):
            new_dict = dict()
            for key, val in target.iteritems():
                new_dict[key] = self.recursive_data_from_code(val)
            return new_dict
        if type(target) is list or (hasattr(target, 'elements') and type(target.elements) is list):
            new_list = list()
            for val in target.__iter__():
                new_list.append(self.recursive_data_from_code(val))
            return new_list
        if type(target) is set or (hasattr(target, 'elements') and type(target.elements) is set):
            new_set = set()
            for val in target.__iter__():
                new_set.add(self.recursive_data_from_code(val))
            return new_set
        if type(target) in (bool, float, int, NoneType):
            return target
        self.find_fields_in(target)
        return compile(target, '<expression>', 'eval')
    def recursive_dataobject(self, target):
        if type(target) is dict or (hasattr(target, 'elements') and type(target.elements) is dict):
            new_dict = dict()
            for key, val in target.iteritems():
                new_dict[key] = self.recursive_dataobject(val)
            return new_dict
        if type(target) is list or (hasattr(target, 'elements') and type(target.elements) is list):
            new_list = list()
            for val in target.__iter__():
                new_list.append(self.recursive_dataobject(val))
            return new_list
        if type(target) is set or (hasattr(target, 'elements') and type(target.elements) is set):
            new_set = set()
            for val in target.__iter__():
                new_set.add(self.recursive_dataobject(val, self.mako_names))
            return new_set
        if type(target) in (bool, float, int, NoneType):
            return target
        return TextObject(unicode(target), names_used=self.mako_names)
        
    def find_fields_in(self, code):
        myvisitor = myvisitnode()
        t = ast.parse(code)
        myvisitor.visit(t)
        predefines = set(globals().keys()) | set(locals().keys())
        if self.scan_for_variables:
            for item in myvisitor.targets.keys():
                if item not in predefines:
                    self.fields_used.add(item)
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
    def help(self):
        return word("Help")
    def process_attachment_code(self, sourcecode):
        try:
            self.compute_attachment = compile(sourcecode, '<expression>', 'eval')
            self.find_fields_in(sourcecode)
            self.sourcecode = sourcecode
        except:
            logmessage("Question: compile error in code:\n" + unicode(sourcecode) + "\n" + str(sys.exc_info()[0]))
            raise
    def process_attachment_list(self, target):
        if type(target) is list:
            att_list = list(map((lambda x: self.process_attachment(x)), target))
            return att_list
        else:
            return([self.process_attachment(target)])
    def process_attachment(self, orig_target):
        metadata = dict()
        variable_name = str()
        defs = list()
        options = dict()
        if type(orig_target) is dict:
            target = dict()
            for key, value in orig_target.iteritems():
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
            if 'checkbox export value' in target and 'pdf template file' in target:
                if type(target['checkbox export value']) not in (str, unicode):
                    raise DAError("A checkbox export value must be a string." + self.idebug(target))
                options['checkbox_export_value'] = TextObject(target['checkbox export value'])
            if 'decimal places' in target and 'pdf template file' in target:
                if type(target['decimal places']) not in (str, unicode, int):
                    raise DAError("A decimal places directive must be an integer or string." + self.idebug(target))
                options['decimal_places'] = TextObject(unicode(target['decimal places']))
            if 'initial yaml' in target:
                if type(target['initial yaml']) is not list:
                    target['initial yaml'] = [target['initial yaml']]
                options['initial_yaml'] = list()
                for yaml_file in target['initial yaml']:
                    if type(yaml_file) is not str:
                        raise DAError('An initial yaml file must be a string.' + self.idebug(target))
                    options['initial_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
            if 'additional yaml' in target:
                if type(target['additional yaml']) is not list:
                    target['additional yaml'] = [target['additional yaml']]
                options['additional_yaml'] = list()
                for yaml_file in target['additional yaml']:
                    if type(yaml_file) is not str:
                        raise DAError('An additional yaml file must be a string.' + self.idebug(target))
                    options['additional_yaml'].append(FileInPackage(yaml_file, 'template', self.package))
            if 'template file' in target:
                if type(target['template file']) is not str:
                    raise DAError('The template file must be a string.' + self.idebug(target))
                options['template_file'] = FileInPackage(target['template file'], 'template', self.package)
            if 'rtf template file' in target:
                if type(target['rtf template file']) is not str:
                    raise DAError('The rtf template file must be a string.' + self.idebug(target))
                options['rtf_template_file'] = FileInPackage(target['rtf template file'], 'template', self.package)
            if 'docx reference file' in target:
                if type(target['docx reference file']) is not str:
                    raise DAError('The docx reference file must be a string.' + self.idebug(target))
                options['docx_reference_file'] = FileInPackage(target['docx reference file'], 'template', self.package)
            if 'usedefs' in target:
                if type(target['usedefs']) is str:
                    the_list = [target['usedefs']]
                elif type(target['usedefs']) is list:
                    the_list = target['usedefs']
                else:
                    raise DAError('The usedefs included in an attachment must be specified as a list of strings or a single string.' + self.idebug(target))
                for def_key in the_list:
                    if type(def_key) is not str:
                        raise DAError('The defs in an attachment must be strings.' + self.idebug(target))
                    if def_key not in self.interview.defs:
                        raise DAError('Referred to a non-existent def "' + def_key + '."  All defs must be defined before they are used.' + self.idebug(target))
                    defs.extend(self.interview.defs[def_key])
            if 'variable name' in target:
                variable_name = target['variable name']
                if self.scan_for_variables:
                    self.fields_used.add(target['variable name'])
            else:
                variable_name = "_internal['docvar'][" + str(self.interview.next_attachment_number()) + "]"
            if 'metadata' in target:
                if type(target['metadata']) is not dict:
                    raise DAError('Unknown data type ' + str(type(target['metadata'])) + ' in attachment metadata.' + self.idebug(target))
                for key in target['metadata']:
                    data = target['metadata'][key]
                    if data is list:
                        for sub_data in data:
                            if sub_data is not str:
                                raise DAError('Unknown data type ' + str(type(sub_data)) + ' in list in attachment metadata' + self.idebug(target))
                        newdata = list(map((lambda x: TextObject(x, names_used=self.mako_names)), data))
                        metadata[key] = newdata
                    elif type(data) is str:
                        metadata[key] = TextObject(data, names_used=self.mako_names)
                    elif type(data) is bool:
                        metadata[key] = data
                    else:
                        raise DAError('Unknown data type ' + str(type(data)) + ' in key in attachment metadata' + self.idebug(target))
            if 'content file' in target:
                if type(target['content file']) is not list:
                    target['content file'] = [target['content file']]
                target['content'] = ''
                for content_file in target['content file']:
                    if type(content_file) is not str:
                        raise DAError('A content file must be specified as text or a list of text filenames' + self.idebug(target))
                    file_to_read = docassemble.base.functions.package_template_filename(content_file, package=self.package)
                    if file_to_read is not None and os.path.isfile(file_to_read) and os.access(file_to_read, os.R_OK):
                        with open(file_to_read, 'rU') as the_file:
                            target['content'] += the_file.read().decode('utf8')
                    else:
                        raise DAError('Unable to read content file ' + str(content_file) + ' after trying to find it at ' + str(file_to_read) + self.idebug(target))
            if 'pdf template file' in target and ('code' in target or 'field variables' in target or 'field code' in target or 'raw field variables' in target) and 'fields' not in target:
                target['fields'] = dict()
                field_mode = 'manual'
            elif 'docx template file' in target:
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
                    if 'editable' in target and not target['editable']:
                        options['editable'] = False
                elif 'docx template file' in target:
                    template_type = 'docx'
                    if 'valid formats' in target:
                        if type(target['valid formats']) is str:
                            target['valid formats'] = [target['valid formats']]
                        elif type(target['valid formats']) is not list:
                            raise DAError('Unknown data type in attachment valid formats.' + self.idebug(target))
                        if 'rtf to docx' in target['valid formats']:
                            raise DAError('Valid formats cannot include "rtf to docx" when "docx template file" is used' + self.idebug(target))
                    else:
                        target['valid formats'] = ['docx', 'pdf']
                if type(target[template_type + ' template file']) not in (str, unicode, dict):
                    raise DAError(template_type + ' template file supplied to attachment must be a string or a dict' + self.idebug(target))
                if field_mode == 'auto':
                    options['fields'] = 'auto'
                elif type(target['fields']) not in (list, dict):
                    raise DAError('fields supplied to attachment must be a list or dictionary' + self.idebug(target))
                target['content'] = ''
                options[template_type + '_template_file'] = FileInPackage(target[template_type + ' template file'], 'template', package=self.package)
                if template_type == 'docx' and type(target[template_type + ' template file']) in (str, unicode):
                    try:
                        docx_template = docassemble.base.file_docx.DocxTemplate(options['docx_template_file'].path())
                        the_env = Environment()
                        the_xml = docx_template.get_xml()
                        the_xml = docx_template.patch_xml(the_xml)
                        parsed_content = the_env.parse(the_xml)
                    except TemplateError as the_error:
                        if the_error.filename is None:
                            try:
                                the_error.filename = os.path.basename(options['docx_template_file'].path())
                            except:
                                pass
                        raise the_error
                    for key in jinja2meta.find_undeclared_variables(parsed_content):
                        if not key.startswith('_'):
                            self.mako_names.add(key)
                if field_mode == 'manual':
                    options['fields'] = recursive_textobject(target['fields'], self.mako_names)
                    if 'code' in target:
                        if type(target['code']) in (str, unicode):
                            options['code'] = compile(target['code'], '<expression>', 'eval')
                            self.find_fields_in(target['code'])
                    if 'field variables' in target:
                        if type(target['field variables']) is not list:
                            raise DAError('The field variables must be expressed in the form of a list' + self.idebug(target))
                        if 'code dict' not in options:
                            options['code dict'] = dict()
                        for varname in target['field variables']:
                            if not valid_variable_match.match(str(varname)):
                                raise DAError('The variable ' + str(varname) + " cannot be used in a code list" + self.idebug(target))
                            options['code dict'][varname] = compile(varname, '<expression>', 'eval')
                            self.find_fields_in(varname)
                    if 'raw field variables' in target:
                        if type(target['raw field variables']) is not list:
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
                        if type(target['field code']) is not list:
                            target['field code'] = [target['field code']]
                        for item in target['field code']:
                            if type(item) is not dict:
                                raise DAError('The field code must be expressed in the form of a dictionary' + self.idebug(target))
                            for key, val in item.iteritems():
                                options['code dict'][key] = compile(val, '<expression>', 'eval')
                                self.find_fields_in(val)
            if 'valid formats' in target:
                if type(target['valid formats']) is str:
                    target['valid formats'] = [target['valid formats']]
                elif type(target['valid formats']) is not list:
                    raise DAError('Unknown data type in attachment valid formats.' + self.idebug(target))
                if 'rtf to docx' in target['valid formats'] and 'docx' in target['valid formats']:
                    raise DAError('Valid formats cannot include both "rtf to docx" and "docx."' + self.idebug(target))
            else:
                target['valid formats'] = ['*']
            if 'password' in target:
                options['password'] = TextObject(target['password'])
            if 'pdf/a' in target:
                if type(target['pdf/a']) is bool:
                    options['pdf_a'] = target['pdf/a']
                elif type(target['pdf/a']) in (str, unicode):
                    options['pdf_a'] = compile(target['pdf/a'], '<expression>', 'eval')
                    self.find_fields_in(target['pdf/a'])
                else:
                    raise DAError('Unknown data type in attachment pdf/a.' + self.idebug(target))
            if 'content' not in target:
                raise DAError("No content provided in attachment")
            #logmessage("The content is " + str(target['content']))
            return({'name': TextObject(target['name'], names_used=self.mako_names), 'filename': TextObject(target['filename'], names_used=self.mako_names), 'description': TextObject(target['description'], names_used=self.mako_names), 'content': TextObject("\n".join(defs) + "\n" + target['content'], names_used=self.mako_names), 'valid_formats': target['valid formats'], 'metadata': metadata, 'variable_name': variable_name, 'options': options})
        elif type(orig_target) in (str, unicode):
            return({'name': TextObject('Document'), 'filename': TextObject('Document'), 'description': TextObject(''), 'content': TextObject(orig_target, names_used=self.mako_names), 'valid_formats': ['*'], 'metadata': metadata, 'variable_name': variable_name, 'options': options})
        else:
            raise DAError("Unknown data type in attachment")

    def ask(self, user_dict, old_user_dict, the_x, iterators, sought):
        docassemble.base.functions.this_thread.current_question = self
        if the_x != 'None':
            exec("x = " + the_x, user_dict)
        if len(iterators):
            for indexno in range(len(iterators)):
                #logmessage("Running " + list_of_indices[indexno] + " = " + iterators[indexno])
                exec(list_of_indices[indexno] + " = " + iterators[indexno], user_dict)
        if self.need is not None:
            for need_code in self.need:
                exec(need_code, user_dict)
        question_text = self.content.text(user_dict)
        #logmessage("Asking " + str(question_text))
        #sys.stderr.write("Asking " + str(question_text) + "\n")
        if self.subcontent is not None:
            subquestion = self.subcontent.text(user_dict)
        else:
            subquestion = None
        if self.undertext is not None:
            undertext = self.undertext.text(user_dict)
        else:
            undertext = None
        extras = dict()
        if len(self.terms):
            extras['terms'] = dict()
            for termitem, definition in self.terms.iteritems():
                extras['terms'][termitem] = dict(definition=definition['definition'].text(user_dict))
        if len(self.autoterms):
            extras['autoterms'] = dict()
            for termitem, definition in self.autoterms.iteritems():
                extras['autoterms'][termitem] = dict(definition=definition['definition'].text(user_dict))
        if self.css is not None:
            extras['css'] = self.css.text(user_dict)
        if self.script is not None:
            extras['script'] = self.script.text(user_dict)
        if self.continuelabel is not None:
            continuelabel = self.continuelabel.text(user_dict)
        else:
            continuelabel = None
        if self.helptext is not None:
            if self.helplabel is not None:
                helplabel = self.helplabel.text(user_dict)
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
                for key, value in decoration_item.iteritems():
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
            extras['ok'] = dict()
            for field in self.fields:
                extras['ok'][field.number] = False
                if hasattr(field, 'saveas_code'):
                    try:
                        eval(field.saveas_code, user_dict)
                    except:
                        continue
                if hasattr(field, 'extras'):
                    for key in ('note', 'html', 'min', 'max', 'minlength', 'maxlength', 'step', 'inline width'): # 'script', 'css', 
                        if key in field.extras:
                            if key not in extras:
                                extras[key] = dict()
                            try:
                                extras[key][field.number] = field.extras[key].text(user_dict)
                            except:
                                continue
                if hasattr(field, 'helptext'):
                    try:
                        helptexts[field.number] = field.helptext.text(user_dict)
                    except:
                        continue
                if hasattr(field, 'label'):
                    try:
                        labels[field.number] = field.label.text(user_dict)
                    except:
                        continue
                extras['ok'][field.number] = True
        else:
            only_empty_fields_exist = True
            commands_to_run = list()
            for field in self.fields:
                if hasattr(field, 'has_code') and field.has_code:
                    # standalone multiple-choice questions
                    selectcompute[field.number] = list()
                    for choice in field.choices:
                        if 'compute' in choice and type(choice['compute']) is CodeType:
                            selectcompute[field.number].extend(process_selections(eval(choice['compute'], user_dict)))
                        else:
                            new_item = dict()
                            if 'image' in choice:
                                new_item['image'] = choice['image']
                            if 'help' in choice:
                                new_item['help'] = choice['help'].text(user_dict)
                            if 'default' in choice:
                                new_item['default'] = choice['default']
                            new_item['key'] = choice['key'].text(user_dict)
                            new_item['label'] = choice['label'].text(user_dict)
                            selectcompute[field.number].append(new_item)
                    if len(selectcompute[field.number]) > 0:
                        only_empty_fields_exist = False
                    else:
                        if hasattr(field, 'datatype') and field.datatype in ('checkboxes', 'object_checkboxes'):
                            ensure_object_exists(from_safeid(field.saveas), field.datatype, user_dict, commands=commands_to_run)
                            commands_to_run.append(from_safeid(field.saveas) + ".gathered = True")
                        else:
                            commands_to_run.append(from_safeid(field.saveas) + ' = None')
                elif hasattr(field, 'choicetype') and field.choicetype == 'compute':
                    # multiple choice field in choices
                    if hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio', 'object_checkboxes', 'checkboxes'):
                        exec("import docassemble.base.core", user_dict)
                    to_compute = field.selections['compute']
                    if field.datatype == 'object_checkboxes':
                        default_exists = False
                        #logmessage("Testing for " + from_safeid(field.saveas))
                        try:
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
                    if field.datatype == 'object_checkboxes' and '_DAOBJECTDEFAULTDA' in user_dict:
                        del user_dict['_DAOBJECTDEFAULTDA']
                    if len(selectcompute[field.number]) > 0:
                        only_empty_fields_exist = False
                    else:
                        if hasattr(field, 'datatype') and field.datatype in ('checkboxes', 'object_checkboxes'):
                            ensure_object_exists(from_safeid(field.saveas), field.datatype, user_dict, commands=commands_to_run)
                            commands_to_run.append(from_safeid(field.saveas) + '.gathered = True')
                        else:
                            commands_to_run.append(from_safeid(field.saveas) + ' = None')
                elif hasattr(field, 'choicetype') and field.choicetype == 'manual':
                    if 'exclude' in field.selections:
                        to_exclude = list()
                        for x in field.selections['exclude']:
                            to_exclude.append(eval(x, user_dict))
                        to_exclude = unpack_list(to_exclude)
                        selectcompute[field.number] = list()
                        for candidate in field.selections['values']:
                            new_item = dict(key=candidate['key'].text(user_dict), label=candidate['label'].text(user_dict))
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
                            new_item = dict(key=item['key'].text(user_dict), label=item['label'].text(user_dict))
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
                        new_item['key'] = item['key'].text(user_dict)
                        new_item['label'] = item['label'].text(user_dict)
                        selectcompute[field.number].append(new_item)
                    if len(selectcompute[field.number]) > 0:
                        only_empty_fields_exist = False
                    else:
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
                raise CodeExecute(commands_to_run, self)
            extras['ok'] = dict()
            for field in self.fields:
                if hasattr(field, 'showif_code'):
                    result = eval(field.showif_code, user_dict)
                    if hasattr(field, 'extras') and 'show_if_sign' in field.extras and field.extras['show_if_sign'] == 0:
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
                    if type(field.nota) is bool:
                        extras['nota'][field.number] = field.nota
                    else:
                        extras['nota'][field.number] = field.nota.text(user_dict)
                if type(field.required) is bool:
                    extras['required'][field.number] = field.required
                else:
                    extras['required'][field.number] = eval(field.required['compute'], user_dict)
                if hasattr(field, 'max_image_size') and hasattr(field, 'datatype') and field.datatype in ('file', 'files', 'camera', 'user', 'environment'):
                    extras['max_image_size'] = eval(field.max_image_size['compute'], user_dict)
                if hasattr(field, 'validate'):
                    the_func = eval(field.validate['compute'], user_dict)
                    if hasattr(field, 'datatype'):
                        if field.datatype in ('number', 'integer', 'currency', 'range'):
                            the_func(0)
                        elif field.datatype in ('text', 'area', 'password', 'email', 'radio'):
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
                if hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio', 'object_checkboxes'):
                    if field.number not in selectcompute:
                        raise DAError("datatype was set to object but no code or selections was provided")
                    string = "_internal['objselections'][" + repr(from_safeid(field.saveas)) + "] = dict()"
                    # logmessage("Doing " + string)
                    try:
                        exec(string, user_dict)
                        for selection in selectcompute[field.number]:
                            key = selection['key']
                            #logmessage("key is " + str(key))
                            real_key = codecs.decode(key, 'base64').decode('utf8')
                            string = "_internal['objselections'][" + repr(from_safeid(field.saveas)) + "][" + repr(key) + "] = " + real_key
                            #logmessage("Doing " + string)
                            exec(string, user_dict)
                    except Exception as err:
                        raise DAError("Failure while processing field with datatype of object: " + str(err))
                if hasattr(field, 'label'):
                    labels[field.number] = field.label.text(user_dict)
                if hasattr(field, 'extras'):
                    if 'fields_code' in field.extras:
                        field_list = eval(field.extras['fields_code'], user_dict)
                        if type(field_list) is not list:
                            raise DAError("A code directive that defines items in fields must return a list")
                        new_interview_source = InterviewSourceString(content='')
                        new_interview = new_interview_source.get_interview()
                        reproduce_basics(self.interview, new_interview)
                        the_question = Question(dict(question='n/a', fields=field_list), new_interview, source=new_interview_source, package=self.package)
                        ask_result = the_question.ask(user_dict, old_user_dict, the_x, iterators, sought)
                        for key in ('selectcompute', 'defaults', 'hints', 'helptexts', 'labels'):
                            for field_num, val in ask_result[key].iteritems():
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
                        for key, possible_dict in ask_result['extras'].iteritems():
                            #logmessage(repr("key is " + str(key) + " and possible dict is " + repr(possible_dict)))
                            if type(possible_dict) is dict:
                                #logmessage("key points to a dict")
                                if key not in extras:
                                    extras[key] = dict()
                                for field_num, val in possible_dict.iteritems():
                                    #logmessage("Setting " + str(field.number) + '_' + str(field_num))
                                    extras[key][str(field.number) + '_' + str(field_num)] = val
                        for sub_field in the_question.fields:
                            sub_field.number = str(field.number) + '_' + str(sub_field.number)
                        if 'sub_fields' not in extras:
                            extras['sub_fields'] = dict()
                        extras['sub_fields'][field.number] = the_question.fields
                    for key in ('note', 'html', 'min', 'max', 'minlength', 'maxlength', 'show_if_val', 'step', 'inline width', 'ml_group'): # , 'textresponse', 'content_type' #'script', 'css', 
                        if key in field.extras:
                            if key not in extras:
                                extras[key] = dict()
                            extras[key][field.number] = field.extras[key].text(user_dict)
                    for key in ('ml_train',):
                        if key in field.extras:
                            if key not in extras:
                                extras[key] = dict()
                            if type(field.extras[key]) is bool:
                                extras[key][field.number] = field.extras[key]
                            else:
                                extras[key][field.number] = eval(field.extras[key]['compute'], user_dict)
                if hasattr(field, 'saveas'):
                    try:
                        if old_user_dict is not None:
                            try:
                                defaults[field.number] = eval(from_safeid(field.saveas), old_user_dict)
                            except:
                                defaults[field.number] = eval(from_safeid(field.saveas), user_dict)
                        else:
                            defaults[field.number] = eval(from_safeid(field.saveas), user_dict)
                    except:
                        if hasattr(field, 'default'):
                            if isinstance(field.default, TextObject):
                                defaults[field.number] = field.default.text(user_dict).strip()
                            else:
                                defaults[field.number] = field.default
                        elif hasattr(field, 'extras') and 'default' in field.extras:
                            defaults[field.number] = eval(field.extras['default']['compute'], user_dict)
                    if hasattr(field, 'helptext'):
                        helptexts[field.number] = field.helptext.text(user_dict)
                    if hasattr(field, 'hint'):
                        hints[field.number] = field.hint.text(user_dict)
        if len(self.attachments) or self.compute_attachment is not None:
            attachment_text = self.processed_attachments(user_dict) # , the_x=the_x, iterators=iterators
        else:
            attachment_text = []
        assumed_objects = set()
        for field in self.fields:
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
                if current_role not in self.role and 'role_event' not in self.fields_used and self.question_type not in ('exit', 'logout', 'continue', 'restart', 'leave', 'refresh', 'signin', 'register'):
                    # logmessage("Calling role_event with " + ", ".join(self.fields_used))
                    user_dict['role_needed'] = self.role
                    raise NameError("name 'role_event' is not defined")
            elif self.interview.default_role is not None and current_role not in self.interview.default_role and 'role_event' not in self.fields_used and self.question_type not in ('exit', 'logout', 'continue', 'restart', 'leave', 'refresh', 'signin', 'register'):
                # logmessage("Calling role_event with " + ", ".join(self.fields_used))
                user_dict['role_needed'] = self.interview.default_role
                raise NameError("name 'role_event' is not defined")
        return({'type': 'question', 'question_text': question_text, 'subquestion_text': subquestion, 'under_text': undertext, 'continue_label': continuelabel, 'audiovideo': audiovideo, 'decorations': decorations, 'help_text': help_text_list, 'attachments': attachment_text, 'question': self, 'selectcompute': selectcompute, 'defaults': defaults, 'hints': hints, 'helptexts': helptexts, 'extras': extras, 'labels': labels, 'sought': sought}) #'defined': defined, 
    def processed_attachments(self, user_dict, **kwargs):
        seeking_var = kwargs.get('seeking_var', '__novar')
        steps = user_dict['_internal'].get('steps', -1)
        # logmessage("processed_attachments: steps is " + str(steps))
        if self.interview.cache_documents and hasattr(self, 'name') and self.name + '__SEEKING__' + seeking_var in user_dict['_internal']['doc_cache']:
            if steps in user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var]:
            #logmessage("processed_attachments: result was in document cache")
                return user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var][steps]
            user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var].clear()
        result_list = list()
        items = list()
        for x in self.attachments:
            items.append([x, self.prepare_attachment(x, user_dict, **kwargs), None])
        for item in items:
            result_list.append(self.finalize_attachment(item[0], item[1], user_dict))
        if self.compute_attachment is not None:
            computed_attachment_list = eval(self.compute_attachment, user_dict)
            if type(computed_attachment_list) is not list:
                computed_attachment_list = [computed_attachment_list]
            for the_att in computed_attachment_list:
                if the_att.__class__.__name__ == 'DAFileCollection':
                    file_dict = dict()
                    for doc_format in ('pdf', 'rtf', 'docx', 'rtf to docx', 'tex', 'html'):
                        if hasattr(the_att, doc_format):
                            the_dafile = getattr(the_att, doc_format)
                            if hasattr(the_dafile, 'number'):
                                file_dict[doc_format] = the_dafile.number
                    result_list.append({'name': the_att.info['name'], 'filename': the_att.info['filename'], 'description': the_att.info['description'], 'valid_formats': the_att.info.get('valid_formats', ['*']), 'formats_to_use': the_att.info['formats'], 'markdown': the_att.info.get('markdown', dict()), 'content': the_att.info.get('content', dict()), 'extension': the_att.info.get('extension', dict()), 'mimetype': the_att.info.get('mimetype', dict()), 'file': file_dict, 'metadata': the_att.info.get('metadata', dict()), 'variable_name': str()})
                    #convert_to_pdf_a
                    #file is dict of file numbers
                # if the_att.__class__.__name__ == 'DAFileCollection' and 'attachment' in the_att.info and type(the_att.info) is dict and 'name' in the_att.info['attachment'] and 'number' in the_att.info['attachment'] and len(self.interview.questions_by_name[the_att.info['attachment']['name']].attachments) > the_att.info['attachment']['number']:
                #     attachment = self.interview.questions_by_name[the_att.info['attachment']['name']].attachments[the_att.info['attachment']['number']] #PPP
                #     items.append([attachment, self.prepare_attachment(attachment, user_dict, **kwargs)])
        if self.interview.cache_documents and hasattr(self, 'name'):
            if self.name + '__SEEKING__' + seeking_var not in user_dict['_internal']['doc_cache']:
                user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var] = dict()
            user_dict['_internal']['doc_cache'][self.name + '__SEEKING__' + seeking_var][steps] = result_list
        return result_list
        #return(list(map((lambda x: self.make_attachment(x, user_dict, **kwargs)), self.attachments)))
    def parse_fields(self, the_list, register_target, uses_field):
        result_list = list()
        has_code = False
        if type(the_list) is dict:
            new_list = list()
            for key, value in the_list.iteritems():
                new_item = dict()
                new_item[key] = value
                new_list.append(new_item)
            the_list = new_list
        if type(the_list) is not list:
            raise DAError("Multiple choices need to be provided in list form.  " + self.idebug(the_list))
        for the_dict in the_list:
            if type(the_dict) not in (dict, list):
                the_dict = {unicode(the_dict): the_dict}
            elif type(the_dict) is not dict:
                raise DAError("Unknown data type for the_dict in parse_fields.  " + self.idebug(the_list))
            result_dict = dict()
            for key, value in the_dict.iteritems():
                if len(the_dict) > 1:
                    if key == 'image':
                        result_dict['image'] = value
                        continue
                    if key == 'help':
                        result_dict['help'] = TextObject(value)
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
                        result_dict['label'] = TextObject(key)
                        result_dict['key'] = TextObject(value)
                elif type(value) is dict:
                    result_dict['label'] = TextObject(key)
                    result_dict['key'] = Question(value, self.interview, register_target=register_target, source=self.from_source, package=self.package, source_code=ruamel.yaml.safe_dump(value, default_flow_style=False, default_style = '|'))
                elif type(value) in (str, unicode):
                    if value in ('exit', 'logout', 'leave') and 'url' in the_dict:
                        result_dict['label'] = TextObject(key)
                        result_dict['key'] = Question({'command': value, 'url': the_dict['url']}, self.interview, register_target=register_target, source=self.from_source, package=self.package)
                    elif value in ('continue', 'restart', 'refresh', 'signin', 'register', 'exit', 'logout', 'leave'):
                        result_dict['label'] = TextObject(key)
                        result_dict['key'] = Question({'command': value}, self.interview, register_target=register_target, source=self.from_source, package=self.package)
                    elif key == 'url':
                        pass
                    else:
                        result_dict['label'] = TextObject(key)
                        result_dict['key'] = value
                elif type(value) is bool:
                    result_dict['label'] = TextObject(key)
                    result_dict['key'] = value
                else:
                    raise DAError("Unknown data type in parse_fields:" + str(type(value)) + ".  " + self.idebug(the_list))
            result_list.append(result_dict)
        return(has_code, result_list)
    def mark_as_answered(self, user_dict):
        user_dict['_internal']['answered'].add(self.name)
    def follow_multiple_choice(self, user_dict, interview_status):
        # logmessage("follow_multiple_choice")
        # if self.name:
        #     logmessage("question is " + self.name)
        # else:
        #     logmessage("question has no name")
        # logmessage("question type is " + str(self.question_type))
        if self.name and self.name in user_dict['_internal']['answers']:
            interview_status.followed_mc = True
            interview_status.tentatively_answered.add(self)
            # self.mark_as_answered(user_dict)
            # logmessage("question in answers")
            # user_dict['_internal']['answered'].add(self.name)
            # logmessage("2 Question name was " + self.name)
            the_choice = self.fields[0].choices[user_dict['_internal']['answers'][self.name]]
            for key in the_choice:
                if len(the_choice) > 1 and key in ('image', 'compute', 'help', 'default'):
                    continue
                # logmessage("Setting target")
                target = the_choice[key]
                break
            if target:
                # logmessage("Target defined")
                if type(target) is str:
                    pass
                elif isinstance(target, Question):
                    # logmessage("Reassigning question")
                    return(target.follow_multiple_choice(user_dict, interview_status))
        return(self)
    def finalize_attachment(self, attachment, result, user_dict):
        if self.interview.cache_documents and attachment['variable_name']:
            try:
                existing_object = eval(attachment['variable_name'], user_dict)
                for doc_format in ('pdf', 'rtf', 'docx', 'rtf to docx', 'tex', 'html'):
                    if hasattr(existing_object, doc_format):
                        the_file = getattr(existing_object, doc_format)
                        for key in ('extension', 'mimetype', 'content', 'markdown'):
                            if hasattr(the_file, key):
                                result[key][doc_format] = getattr(the_file, key)
                        if hasattr(the_file, 'number'):
                            result['file'][doc_format] = the_file.number
                #logmessage("finalize_attachment: returning " + attachment['variable_name'] + " from cache")
                for key in ('template', 'field_data', 'images', 'data_strings', 'convert_to_pdf_a', 'password'):
                    if key in result:
                        del result[key]
                return result
            except:
                pass
            #logmessage("finalize_attachment: " + attachment['variable_name'] + " was not in cache")
        for doc_format in result['formats_to_use']:
            if doc_format in ('pdf', 'rtf', 'rtf to docx', 'tex', 'docx'):
                if 'fields' in attachment['options']:
                    if doc_format == 'pdf' and 'pdf_template_file' in attachment['options']:
                        the_pdf_file = docassemble.base.pdftk.fill_template(attachment['options']['pdf_template_file'].path(user_dict=user_dict), data_strings=result['data_strings'], images=result['images'], editable=attachment['options'].get('editable', True), pdfa=result['convert_to_pdf_a'], password=result['password'])
                        result['file'][doc_format], result['extension'][doc_format], result['mimetype'][doc_format] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.' + extension_of_doc_format[doc_format], the_pdf_file, yaml_file_name=self.interview.source.path)
                        for key in ('images', 'data_strings', 'convert_to_pdf_a', 'password'):
                            if key in result:
                                del result[key]
                    elif (doc_format == 'docx' or (doc_format == 'pdf' and 'docx' not in result['formats_to_use'])) and 'docx_template_file' in attachment['options']:
                        #logmessage("field_data is " + str(result['field_data']))
                        docassemble.base.functions.set_context('docx', template=result['template'])
                        try:
                            the_template = result['template']
                            while True:
                                old_count = docassemble.base.functions.this_thread.docx_include_count
                                the_template.render(result['field_data'], jinja_env=Environment(undefined=StrictUndefined))
                                if docassemble.base.functions.this_thread.docx_include_count > old_count:
                                    new_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
                                    the_template.save(new_template_file.name)
                                    the_template = docassemble.base.file_docx.DocxTemplate(new_template_file.name)
                                    docassemble.base.functions.this_thread.docx_template = the_template
                                else:
                                    break
                        except TemplateError as the_error:
                            if (not hasattr(the_error, 'filename')) or the_error.filename is None:
                                the_error.filename = os.path.basename(attachment['options']['docx_template_file'].path(user_dict=user_dict))
                            raise the_error
                        docassemble.base.functions.reset_context()
                        docx_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
                        the_template.save(docx_file.name)
                        if 'docx' in result['formats_to_use']:
                            result['file']['docx'], result['extension']['docx'], result['mimetype']['docx'] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.docx', docx_file.name, yaml_file_name=self.interview.source.path)
                        if 'pdf' in result['formats_to_use']:
                            pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
                            docassemble.base.pandoc.word_to_pdf(docx_file.name, 'docx', pdf_file.name, pdfa=result['convert_to_pdf_a'], password=result['password'])
                            result['file']['pdf'], result['extension']['pdf'], result['mimetype']['pdf'] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.pdf', pdf_file.name, yaml_file_name=self.interview.source.path)
                        for key in ['template', 'field_data', 'images', 'data_strings', 'convert_to_pdf_a', 'password']:
                            if key in result:
                                del result[key]
                else:
                    converter = MyPandoc(pdfa=result['convert_to_pdf_a'], password=result['password'])
                    converter.output_format = doc_format
                    converter.input_content = result['markdown'][doc_format]
                    if 'initial_yaml' in attachment['options']:
                        converter.initial_yaml = [x.path(user_dict=user_dict) for x in attachment['options']['initial_yaml']]
                    elif 'initial_yaml' in self.interview.attachment_options:
                        converter.initial_yaml = [x.path(user_dict=user_dict) for x in self.interview.attachment_options['initial_yaml']]
                    if 'additional_yaml' in attachment['options']:
                        converter.additional_yaml = [x.path(user_dict=user_dict) for x in attachment['options']['additional_yaml']]
                    elif 'additional_yaml' in self.interview.attachment_options:
                        converter.additional_yaml = [x.path(user_dict=user_dict) for x in self.interview.attachment_options['additional_yaml']]
                    if doc_format in ('rtf', 'rtf to docx'):
                        if 'rtf_template_file' in attachment['options']:
                            converter.template_file = attachment['options']['rtf_template_file'].path(user_dict=user_dict)
                        elif 'rtf_template_file' in self.interview.attachment_options:
                            converter.template_file = self.interview.attachment_options['rtf_template_file'].path(user_dict=user_dict)
                    elif doc_format == 'docx':
                        if 'docx_reference_file' in attachment['options']:
                            converter.reference_file = attachment['options']['docx_reference_file'].path(user_dict=user_dict)
                        elif 'docx_reference_file' in self.interview.attachment_options:
                            converter.reference_file = self.interview.attachment_options['docx_reference_file'].path(user_dict=user_dict)
                    else:
                        if 'template_file' in attachment['options']:
                            converter.template_file = attachment['options']['template_file'].path(user_dict=user_dict)
                        elif 'template_file' in self.interview.attachment_options:
                            converter.template_file = self.interview.attachment_options['template_file'].path(user_dict=user_dict)
                    converter.metadata = result['metadata']
                    converter.convert(self)
                    result['file'][doc_format], result['extension'][doc_format], result['mimetype'][doc_format] = docassemble.base.functions.server.save_numbered_file(result['filename'] + '.' + extension_of_doc_format[doc_format], converter.output_filename, yaml_file_name=self.interview.source.path)
                    result['content'][doc_format] = result['markdown'][doc_format]
            elif doc_format in ['html']:
                result['content'][doc_format] = docassemble.base.filter.markdown_to_html(result['markdown'][doc_format], use_pandoc=True, question=self)
        if attachment['variable_name']:
            string = "import docassemble.base.core"
            exec(string, user_dict)
            variable_name = attachment['variable_name']
            m = re.search(r'^(.*)\.([A-Za-z0-9\_]+)$', attachment['variable_name'])
            if m:
                base_var = m.group(1)
                attrib = m.group(2)
                the_var = eval(base_var, user_dict)
                if hasattr(the_var, 'instanceName'):
                    variable_name = the_var.instanceName + '.' + attrib
            string = variable_name + " = docassemble.base.core.DAFileCollection(" + repr(variable_name) + ")"
            # logmessage("Executing " + string + "\n")
            exec(string, user_dict)
            the_name = attachment['name'].text(user_dict).strip()
            the_filename = attachment['filename'].text(user_dict).strip()
            if the_filename == '':
                the_filename = docassemble.base.functions.space_to_underscore(the_name)
            user_dict['_attachment_info'] = dict(name=the_name, filename=the_filename, description=attachment['description'].text(user_dict), valid_formats=result['valid_formats'], formats=result['formats_to_use'], attachment=dict(name=attachment['question_name'], number=attachment['indexno']), extension=result.get('extension', dict()), mimetype=result.get('mimetype', dict()), content=result.get('content', dict()), markdown=result.get('markdown', dict()), metadata=result.get('metadata', dict()), convert_to_pdf_a=result.get('convert_to_pdf_a', False))
            exec(variable_name + '.info = _attachment_info', user_dict)
            del user_dict['_attachment_info']
            for doc_format in result['file']:
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
                string = variable_string + " = docassemble.base.core.DAFile(" + repr(variable_string) + ", filename=" + repr(str(result['filename']) + '.' + extension_of_doc_format[doc_format]) + ", number=" + str(result['file'][doc_format]) + ", mimetype='" + str(result['mimetype'][doc_format]) + "', extension='" + str(result['extension'][doc_format]) + "'" + content_string + markdown_string + ")"
                #logmessage("Executing " + string + "\n")
                exec(string, user_dict)
            for doc_format in result['content']:
                # logmessage("Considering " + doc_format)
                if doc_format not in result['file']:
                    variable_string = variable_name + '.' + extension_of_doc_format[doc_format]
                    # logmessage("Setting " + variable_string)
                    string = variable_string + " = docassemble.base.core.DAFile(" + repr(variable_string) + ', markdown=' + repr(result['markdown'][doc_format]) + ', content=' + repr(result['content'][doc_format]) + ")"
                    exec(string, user_dict)
        return(result)
    def prepare_attachment(self, attachment, user_dict, **kwargs):
        if 'language' in attachment['options']:
            old_language = docassemble.base.functions.get_language()
            docassemble.base.functions.set_language(attachment['options']['language'])
        else:
            old_language = None
        the_name = attachment['name'].text(user_dict).strip()
        the_filename = attachment['filename'].text(user_dict).strip()
        if the_filename == '':
            the_filename = docassemble.base.functions.space_to_underscore(the_name)
        result = {'name': the_name, 'filename': the_filename, 'description': attachment['description'].text(user_dict), 'valid_formats': attachment['valid_formats']}
        result['markdown'] = dict();
        result['content'] = dict();
        result['extension'] = dict();
        result['mimetype'] = dict();
        result['file'] = dict();
        if '*' in attachment['valid_formats']:
            result['formats_to_use'] = ['pdf', 'rtf', 'html']
        else:
            result['formats_to_use'] = attachment['valid_formats']
        result['metadata'] = dict()
        if len(attachment['metadata']) > 0:
            for key in attachment['metadata']:
                data = attachment['metadata'][key]
                if type(data) is bool:
                    result['metadata'][key] = data
                elif type(data) is list:
                    result['metadata'][key] = textify(data, user_dict)
                else:
                    result['metadata'][key] = data.text(user_dict)
        if 'pdf_a' in attachment['options']:
            if type(attachment['options']['pdf_a']) is bool:
                result['convert_to_pdf_a'] = attachment['options']['pdf_a']
            else:
                result['convert_to_pdf_a'] = eval(attachment['options']['pdf_a'], user_dict)
        else:
            result['convert_to_pdf_a'] = self.interview.use_pdf_a
        if 'password' in attachment['options']:
            result['password'] = attachment['options']['password'].text(user_dict)
        else:
            result['password'] = None
        for doc_format in result['formats_to_use']:
            if doc_format in ['pdf', 'rtf', 'rtf to docx', 'tex', 'docx']:
                if 'decimal_places' in attachment['options']:
                    try:
                        float_formatter = '%.' + str(int(attachment['options']['decimal_places'].text(user_dict).strip())) + 'f'
                    except:
                        logmessage("prepare_attachment: error in float_formatter")
                        float_formatter = None
                else:
                    float_formatter = None
                if 'fields' in attachment['options'] and 'docx_template_file' in attachment['options']:
                    if doc_format == 'docx' or ('docx' not in result['formats_to_use'] and doc_format == 'pdf'):
                        result['template'] = docassemble.base.file_docx.DocxTemplate(attachment['options']['docx_template_file'].path(user_dict=user_dict))
                        if type(attachment['options']['fields']) in (str, unicode):
                            result['field_data'] = user_dict
                        else:
                            the_field_data = recursive_eval_textobject(attachment['options']['fields'], user_dict, self, result['template'])
                            new_field_data = dict()
                            if type(the_field_data) is list:
                                for item in the_field_data:
                                    if type(item) is dict:
                                        new_field_data.update(item)
                                the_field_data = new_field_data
                            result['field_data'] = new_field_data
                        if 'code' in attachment['options']:
                            additional_dict = eval(attachment['options']['code'], user_dict)
                            if type(additional_dict) is dict:
                                for key, val in additional_dict.iteritems():
                                    if type(val) is float and float_formatter is not None:
                                        result['field_data'][key] = float_formatter % val
                                    elif type(val) is RawValue:
                                        result['field_data'][key] = val.value
                                    else:
                                        result['field_data'][key] = docassemble.base.file_docx.transform_for_docx(val, self, result['template'])
                            else:
                                raise DAError("code in an attachment returned something other than a dictionary")
                        if 'raw code dict' in attachment['options']:
                            for varname, var_code in attachment['options']['raw code dict'].iteritems():
                                val = eval(var_code, user_dict)
                                if type(val) is float and float_formatter is not None:
                                    result['field_data'][varname] = float_formatter % val
                                else:
                                    result['field_data'][varname] = val
                        if 'code dict' in attachment['options']:
                            for varname, var_code in attachment['options']['code dict'].iteritems():
                                val = eval(var_code, user_dict)
                                if type(val) is float and float_formatter is not None:
                                    result['field_data'][varname] = float_formatter % val
                                elif type(val) is RawValue:
                                    result['field_data'][varname] = val.value
                                else:
                                    result['field_data'][varname] = docassemble.base.file_docx.transform_for_docx(val, self, result['template'])
                elif doc_format == 'pdf' and 'fields' in attachment['options'] and 'pdf_template_file' in attachment['options']:
                    result['data_strings'] = []
                    result['images'] = []
                    if type(attachment['options']['fields']) is dict:
                        the_fields = [attachment['options']['fields']]
                    else:
                        the_fields = attachment['options']['fields']
                    if 'checkbox_export_value' in attachment['options']:
                        yes_value = attachment['options']['checkbox_export_value'].text(user_dict).strip()
                    else:
                        yes_value = 'Yes'
                    docassemble.base.functions.this_thread.misc['checkbox_export_value'] = yes_value
                    for item in the_fields:
                        for key, val in item.iteritems():
                            answer = val.text(user_dict).rstrip()
                            if answer == 'True':
                                answer = yes_value
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
                                result['data_strings'].append((key, answer))
                    if 'code' in attachment['options']:
                        additional_fields = eval(attachment['options']['code'], user_dict)
                        if type(additional_fields) is not list:
                            additional_fields = [additional_fields]
                        for item in additional_fields:
                            if type(item) is not dict:
                                raise DAError("code in an attachment returned something other than a dictionary or a list of dictionaries")
                            for key, val in item.iteritems():
                                if val is True:
                                    val = yes_value
                                elif val is False:
                                    val = 'No'
                                elif val is None:
                                    val = ''
                                elif type(val) is float and float_formatter is not None:
                                    val = float_formatter % val
                                else:
                                    val = unicode(val)
                                val = re.sub(r'\[(NEWLINE|BR)\]', r'\n', val)
                                val = re.sub(r'\[(BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|BOLDCENTER|CENTER)\]', r'', val)
                                m = re.search(r'\[FILE ([^\]]+)\]', val)
                                if m:
                                    file_reference = re.sub(r'[ ,].*', '', m.group(1))
                                    file_info = docassemble.base.functions.server.file_finder(file_reference, convert={'svg': 'png'})
                                    result['images'].append((key, file_info))
                                else:
                                    result['data_strings'].append((key, val))
                    if 'code dict' in attachment['options']:
                        additional_fields = attachment['options']['code dict']
                        if type(additional_fields) is not list:
                            additional_fields = [additional_fields]
                        for item in additional_fields:
                            if type(item) is not dict:
                                raise DAError("code dict in an attachment returned something other than a dictionary or a list of dictionaries")
                            for key, var_code in item.iteritems():
                                val = eval(var_code, user_dict)
                                if val is True:
                                    val = yes_value
                                elif val is False:
                                    val = 'No'
                                elif val is None:
                                    val = ''
                                elif type(val) is float and float_formatter is not None:
                                    val = float_formatter % val
                                else:
                                    val = unicode(val)
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
                        if type(additional_fields) is not list:
                            additional_fields = [additional_fields]
                        for item in additional_fields:
                            if type(item) is not dict:
                                raise DAError("raw code dict in an attachment returned something other than a dictionary or a list of dictionaries")
                            for key, var_code in item.iteritems():
                                val = eval(var_code, user_dict)
                                if val is True:
                                    val = yes_value
                                elif val is False:
                                    val = 'No'
                                elif type(val) is float and float_formatter is not None:
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
                else:
                    the_markdown = ""
                    if len(result['metadata']):
                        modified_metadata = dict()
                        for key, data in result['metadata'].iteritems():
                            if re.search(r'Footer|Header', key):
                                #modified_metadata[key] = docassemble.base.filter.metadata_filter(data, doc_format) + unicode('[END]')
                                modified_metadata[key] = data + unicode('[END]')
                            else:
                                modified_metadata[key] = data
                        the_markdown += "---\n" + ruamel.yaml.safe_dump(modified_metadata, default_flow_style=False, default_style = '|') + "...\n"
                    the_markdown += attachment['content'].text(user_dict)
                    #logmessage("Markdown is:\n" + repr(the_markdown) + "END")
                    if emoji_match.search(the_markdown) and len(self.interview.images) > 0:
                        the_markdown = emoji_match.sub(emoji_matcher_insert(self), the_markdown)
                    result['markdown'][doc_format] = the_markdown
            elif doc_format in ['html']:
                result['markdown'][doc_format] = attachment['content'].text(user_dict)
                if emoji_match.search(result['markdown'][doc_format]) and len(self.interview.images) > 0:
                    result['markdown'][doc_format] = emoji_match.sub(emoji_matcher_html(self), result['markdown'][doc_format])
                #logmessage("output was:\n" + repr(result['content'][doc_format]))
        if old_language is not None:
            docassemble.base.functions.set_language(old_language)
        return(result)

def emoji_matcher_insert(obj):
    return (lambda x: docassemble.base.filter.emoji_insert(x.group(1), images=obj.interview.images))

def emoji_matcher_html(obj):
    return (lambda x: docassemble.base.filter.emoji_html(x.group(1), images=obj.interview.images))

def interview_source_from_string(path, **kwargs):
    if path is None:
        raise DAError("Passed None to interview_source_from_string")
    if re.search(r'^https*://', path):
        new_source = InterviewSourceURL(path=path)
        if new_source.update():
            return new_source
    context_interview = kwargs.get('context_interview', None)
    if context_interview is not None:
        new_source = context_interview.source.append(path)
        if new_source is not None:
            return new_source
    #sys.stderr.write("Trying to find it\n")
    for the_filename in [docassemble.base.functions.package_question_filename(path), docassemble.base.functions.standard_question_filename(path), docassemble.base.functions.server.absolute_filename(path)]:
        #sys.stderr.write("Trying " + str(the_filename) + " with path " + str(path) + "\n")
        if the_filename is not None:
            new_source = InterviewSourceFile(filepath=the_filename, path=path)
            if new_source.update():
                return(new_source)
    raise DAError("YAML file " + str(path) + " not found", code=404)

def is_boolean(field_data):
    if 'choices' not in field_data:
        return False
    if 'has_code' in field_data:
        return False
    for entry in field_data['choices']:
        if 'key' in entry and 'label' in entry:
            if type(entry['key'].original_text) is not bool:
                return False
    return True

def is_threestate(field_data):
    if 'choices' not in field_data:
        return False
    if 'has_code' in field_data:
        return False
    for entry in field_data['choices']:
        if 'key' in entry and 'label' in entry:
            if type(entry['key'].original_text) is not bool and type(entry['key'].original_text) is not NoneType:
                return False
    return True

class Interview:
    def __init__(self, **kwargs):
        self.source = None
        self.questions = dict()
        self.generic_questions = dict()
        self.questions_by_id = dict()
        self.questions_by_name = dict()
        self.questions_list = list()
        self.ids_in_use = set()
        self.id_orderings = list()
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
        self.default_role = None
        self.title = None
        self.use_progress_bar = False
        self.question_back_button = False
        self.question_help_button = False
        self.navigation_back_button = True
        self.force_fullscreen = False
        self.use_pdf_a = get_config('pdf/a', False)
        self.loop_limit = get_config('loop limit', 500)
        self.recursion_limit = get_config('recursion limit', 500)
        self.cache_documents = True
        self.use_navigation = False
        self.max_image_size = get_config('maximum image size', None)
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
        if 'source' in kwargs:
            self.read_from(kwargs['source'])
    def ordered(self, the_list):
        if len(the_list) <= 1:
            return the_list
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
    def get_metadata(self):
        result = dict()
        for metadata in self.metadata:
            for key, val in metadata.iteritems():
                result[key] = val
        return result
    def get_tags(self, user_dict):
        if 'tags' in user_dict['_internal']:
            return user_dict['_internal']['tags']
        else:
            tags = set()
            for metadata in self.metadata:
                if 'tags' in metadata and type(metadata['tags']) is list:
                    for tag in metadata['tags']:
                        tags.add(tag)
            return tags
    def get_title(self, user_dict):
        mapping = (('title', 'full'), ('logo', 'logo'), ('short title', 'short'), ('tab title', 'tab'), ('subtitle', 'sub'), ('exit link', 'exit link'), ('exit label', 'exit label'), ('submit', 'submit'), ('pre', 'pre'), ('post', 'post'))
        if not hasattr(self, 'default_title'):
            self.default_title = dict()
            for metadata in self.metadata:
                for title_name, title_abb in mapping:
                    if metadata.get(title_name, None) is not None:
                        if type(metadata[title_name]) is dict:
                            value = metadata[title_name].get(get_language(), None)
                            if value is not None:
                                self.default_title[title_abb] = unicode(value).strip()
                            else:
                                value = metadata[title_name].get('*', None)
                                if value is not None:
                                    self.default_title[title_abb] = unicode(value).strip()
                                else:
                                    value = metadata[title_name].get(docassemble.base.functions.server.default_language, None)
                                    if value is not None:
                                        self.default_title[title_abb] = unicode(value).strip()
                        else:
                            self.default_title[title_abb] = unicode(metadata[title_name]).strip()
        title = dict()
        for title_name, title_abb in mapping:
            if '_internal' in user_dict and title_name in user_dict['_internal'] and user_dict['_internal'][title_name] is not None:
                title[title_abb] = unicode(user_dict['_internal'][title_name]).strip()
        for key, val in self.default_title.iteritems():
            if key not in title:
                title[key] = val
        return title
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
    def read_from(self, source):
        if self.source is None:
            self.source = source
            #self.firstPath = source.path
            #self.rootDirectory = source.directory
        if hasattr(source, 'package'):
            source_package = source.package
        else:
            source_package = None
        if hasattr(source, 'path'):
            if source.path in self.includes:
                logmessage("Interview: source " + unicode(source.path) + " has already been included.  Skipping.")
                return
            self.includes.add(source.path)
        #for document in ruamel.yaml.safe_load_all(source.content):
        for source_code in document_match.split(source.content):
            source_code = remove_trailing_dots.sub('', source_code)
            source_code = fix_tabs.sub('  ', source_code)
            if source.testing:
                try:
                    #logmessage("Package is " + str(source_package))
                    document = ruamel.yaml.safe_load(source_code)
                    if document is not None:
                        question = Question(document, self, source=source, package=source_package, source_code=source_code)
                        self.names_used.update(question.fields_used)
                except Exception as errMess:
                    #sys.stderr.write(unicode(source_code) + "\n")
                    try:
                        logmessage('Interview: error reading YAML file ' + unicode(source.path) + '\n\nDocument source code was:\n\n---\n' + unicode(source_code) + '---\n\nError was:\n\n' + unicode(errMess))
                    except:
                        logmessage('Interview: error reading YAML file ' + unicode(source.path) + '. Error was:\n\n' + unicode(errMess))
                    self.success = False
                    pass
            else:
                try:
                    document = ruamel.yaml.safe_load(source_code)
                except Exception as errMess:
                    self.success = False
                    #sys.stderr.write("Error: " + unicode(source_code) + "\n")
                    #unicode(source_code)
                    raise DAError('Error reading YAML file ' + unicode(source.path) + '\n\nDocument source code was:\n\n---\n' + unicode(source_code) + '---\n\nError was:\n\n' + unicode(errMess))
                if document is not None:
                    try:
                        question = Question(document, self, source=source, package=source_package, source_code=source_code)
                        self.names_used.update(question.fields_used)
                    except SyntaxException as qError:
                        self.success = False
                        raise Exception("Syntax Exception: " + unicode(qError) + "\n\nIn file " + unicode(source.path) + " from package " + unicode(source_package) + ":\n" + unicode(source_code))
                    except SyntaxError as qError:
                        self.success = False
                        raise Exception("Syntax Error: " + unicode(qError) + "\n\nIn file " + unicode(source.path) + " from package " + unicode(source_package) + ":\n" + unicode(source_code))
        for ordering in self.id_orderings:
            if ordering['type'] == 'supersedes':
                new_list = [ordering['question'].number]
                for question_id in ordering['supersedes']:
                    if question_id in self.questions_by_id:
                        new_list.append(self.questions_by_id[question_id].number)
                    else:
                        logmessage("warning: reference in a supersedes directive to an id " + question_id + " that does not exist in interview")
            elif ordering['type'] == 'order':
                new_list = list()
                for question_id in ordering['order']:
                    if question_id in self.questions_by_id:
                        new_list.append(self.questions_by_id[question_id].number)
                    else:
                        logmessage("warning: reference in an order directive to id " + question_id + " that does not exist in interview")
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
        if len(self.images) > 0 or get_config('default icons', None) in ('material icons', 'font awesome'):
            self.scan_for_emojis = True
        else:
            self.scan_for_emojis = False
    def make_sorter(self):
        lookup_dict = self.orderings_by_question
        class K(object):
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
    def processed_helptext(self, user_dict, language):
        result = list()
        if language in self.helptext:
            for source in self.helptext[language]:
                help_item = dict()
                help_item['from'] = source['from']
                if source['label'] is None:
                    help_item['label'] = None
                else:
                    help_item['label'] = source['label'].text(user_dict)
                if source['heading'] is None:
                    help_item['heading'] = None
                else:
                    help_item['heading'] = source['heading'].text(user_dict)
                if source['audiovideo'] is None:
                    help_item['audiovideo'] = None
                else:
                    help_item['audiovideo'] = process_audio_video_list(source['audiovideo'], user_dict)
                help_item['content'] = source['content'].text(user_dict)
                result.append(help_item)
        return result
    def assemble(self, user_dict, *args):
        #sys.stderr.write("assemble\n")
        #logmessage("assemble: starting")
        user_dict['_internal']['tracker'] += 1
        if len(args):
            interview_status = args[0]
            if len(args) >= 2:
                old_user_dict = args[1]
            else:
                old_user_dict = None
        else:
            interview_status = InterviewStatus()
            old_user_dict = None
        if 'docvar' not in user_dict['_internal']: # waste of CPU cycles; eventually take out!
            user_dict['_internal']['docvar'] = dict()
        if 'doc_cache' not in user_dict['_internal']: # waste of CPU cycles; eventually take out!
            user_dict['_internal']['doc_cache'] = dict()
        if interview_status.current_info['url'] is not None:
            user_dict['_internal']['url'] = interview_status.current_info['url']
        interview_status.set_tracker(user_dict['_internal']['tracker'])
        #docassemble.base.functions.reset_local_variables()
        interview_status.current_info.update({'default_role': self.default_role})
        docassemble.base.functions.this_thread.current_package = self.source.package
        docassemble.base.functions.this_thread.current_info = interview_status.current_info
        docassemble.base.functions.this_thread.interview = self
        docassemble.base.functions.this_thread.interview_status = interview_status
        docassemble.base.functions.this_thread.internal = user_dict['_internal']
        if 'nav' not in user_dict: # waste of CPU cycles; eventually take out!
            user_dict['nav'] = docassemble.base.functions.DANav()
        if user_dict['nav'].sections is None:
            user_dict['nav'].sections = self.sections
        for question in self.questions_list:
            if question.question_type == 'imports':
                for module_name in question.module_list:
                    if module_name.startswith('.'):
                        exec('import ' + str(self.source.package) + module_name, user_dict)
                    else:
                        exec('import ' + module_name, user_dict)
            if question.question_type == 'modules':
                for module_name in question.module_list:
                    if module_name.startswith('.'):
                        exec('from ' + str(self.source.package) + module_name + ' import *', user_dict)
                    else:
                        exec('from ' + module_name + ' import *', user_dict)
            if question.question_type in ['reset', 'template', 'table']:
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
        number_loops = 0
        variables_sought = set()
        try:
            while True:
                number_loops += 1
                if number_loops > self.loop_limit:
                    docassemble.base.functions.close_files()
                    raise DAError("There appears to be a circularity.  Variables involved: " + ", ".join(variables_sought) + ".")
                docassemble.base.functions.reset_gathering_mode()
                try:
                    if (self.imports_util or self.uses_action or 'action' in interview_status.current_info) and not self.calls_process_action:
                        if self.imports_util:
                            exec(run_process_action, user_dict)
                        else:
                            exec(import_and_run_process_action, user_dict)
                    for question in self.questions_list:
                        if question.question_type == 'code' and (question.is_initial or (question.initial_code is not None and eval(question.initial_code, user_dict))):
                            #logmessage("Running some initial code:\n\n" + question.sourcecode)
                            if debug:
                                interview_status.seeking.append({'question': question, 'reason': 'initial', 'time': time.time()})
                            docassemble.base.functions.this_thread.current_question = question
                            exec_with_trap(question, user_dict)
                            continue
                        if question.name and question.name in user_dict['_internal']['answered']:
                            #logmessage("Skipping " + question.name + " because answered")
                            continue
                        if question.question_type == "objects_from_file":
                            for keyvalue in question.objects_from_file:
                                for variable, the_file in keyvalue.iteritems():
                                    exec(import_core, user_dict)
                                    command = variable + ' = docassemble.base.core.objects_from_file("' + str(the_file) + '", name=' + repr(variable) + ')'
                                    #logmessage("Running " + command)
                                    exec(command, user_dict)
                            question.mark_as_answered(user_dict)
                        if (question.is_mandatory or (question.mandatory_code is not None and eval(question.mandatory_code, user_dict))):
                            if question.question_type == "data":
                                string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_dataobject(question.fields[0].data, user_dict))
                                exec(string, user_dict)
                                question.mark_as_answered(user_dict)
                            if question.question_type == "data_from_code":
                                string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_data_from_code(question.fields[0].data, user_dict))
                                exec(string, user_dict)
                                question.mark_as_answered(user_dict)
                            if question.question_type == "objects":
                                #logmessage("Going into objects")
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
                                if debug:
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
                                if debug:
                                    interview_status.seeking.append({'question': question, 'reason': 'mandatory question', 'time': time.time()})
                                if question.name and question.name in user_dict['_internal']['answers']:
                                    #logmessage("in answers")
                                    #question.mark_as_answered(user_dict)
                                    #interview_status.populate(question.follow_multiple_choice(user_dict, interview_status).ask(user_dict, old_user_dict, 'None', [], None))
                                    the_question = question.follow_multiple_choice(user_dict, interview_status)
                                    if the_question.question_type in ["code", "event_code"]:
                                        docassemble.base.functions.this_thread.current_question = the_question
                                        exec_with_trap(the_question, user_dict)
                                        interview_status.mark_tentative_as_answered(user_dict)
                                        continue
                                    elif hasattr(the_question, 'content'):
                                        interview_status.populate(the_question.ask(user_dict, old_user_dict, 'None', [], None))
                                        interview_status.mark_tentative_as_answered(user_dict)
                                    else:
                                        raise DAError("An embedded question can only be a code block or a regular question block.  The question type was " + getattr(the_question, 'question_type', 'unknown'))
                                else:
                                    interview_status.populate(question.ask(user_dict, old_user_dict, 'None', [], None))
                                if interview_status.question.question_type == 'continue':
                                    user_dict['_internal']['answered'].add(question.name)
                                else:
                                    raise MandatoryQuestion()
                except NameError as the_exception:
                    #logmessage("Error in NameError is " + str(the_exception))
                    docassemble.base.functions.reset_context()
                    if isinstance(the_exception, ForcedNameError):
                        #logmessage("assemble: got a ForcedNameError for " + the_exception.name)
                        follow_mc = False
                        if the_exception.next_action is not None:
                            interview_status.next_action.extend(the_exception.next_action)
                        missingVariable = the_exception.name
                    else:
                        follow_mc = True
                        missingVariable = extract_missing_name(the_exception)
                    variables_sought.add(missingVariable)
                    question_result = self.askfor(missingVariable, user_dict, old_user_dict, interview_status, seeking=interview_status.seeking, follow_mc=follow_mc)
                    if question_result['type'] == 'continue':
                        continue
                    elif question_result['type'] == 'refresh':
                        pass
                    else:
                        interview_status.populate(question_result)
                        break
                except UndefinedError as the_exception:
                    docassemble.base.functions.reset_context()
                    missingVariable = extract_missing_name(the_exception)
                    variables_sought.add(missingVariable)
                    question_result = self.askfor(missingVariable, user_dict, old_user_dict, interview_status, seeking=interview_status.seeking, follow_mc=True)
                    if question_result['type'] == 'continue':
                        continue
                    elif question_result['type'] == 'refresh':
                        pass
                    else:
                        interview_status.populate(question_result)
                        break
                except CommandError as qError:
                    docassemble.base.functions.reset_context()
                    question_data = dict(command=qError.return_type, url=qError.url)
                    new_interview_source = InterviewSourceString(content='')
                    new_interview = new_interview_source.get_interview()
                    reproduce_basics(self, new_interview)
                    new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                    new_question.name = "Question_Temp"
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None))
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
                        question_data['content type'] = 'application/json'
                        question_data['all_variables'] = True
                    if hasattr(qError, 'content_type') and qError.content_type:
                        question_data['content type'] = qError.content_type
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
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None))
                    break
                except BackgroundResponseError as qError:
                    docassemble.base.functions.reset_context()
                    #logmessage("Trapped BackgroundResponseError")
                    question_data = dict(extras=dict())
                    if hasattr(qError, 'backgroundresponse'):
                        question_data['backgroundresponse'] = qError.backgroundresponse
                    new_interview_source = InterviewSourceString(content='')
                    new_interview = new_interview_source.get_interview()
                    reproduce_basics(self, new_interview)
                    new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                    new_question.name = "Question_Temp"
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None))
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
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None))
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
                    docassemble.base.functions.reset_context()
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
                    # will this be a problem?  Maybe, since the question name can vary by thread.
                    #the_question = new_question.follow_multiple_choice(user_dict)
                    interview_status.populate(new_question.ask(user_dict, old_user_dict, 'None', [], None))
                    break
                except AttributeError as the_error:
                    docassemble.base.functions.reset_context()
                    #logmessage(str(the_error.args))
                    docassemble.base.functions.close_files()
                    raise DAError('Got error ' + str(the_error) + " " + traceback.format_exc(the_error) + "\nHistory was " + pprint.pformat(interview_status.seeking))
                except MandatoryQuestion:
                    docassemble.base.functions.reset_context()
                    break
                except CodeExecute as code_error:
                    docassemble.base.functions.reset_context()
                    #if debug:
                    #    interview_status.seeking.append({'question': question, 'reason': 'mandatory code'})
                    #logmessage("I am going to execute " + str(code_error.compute))
                    exec(code_error.compute, user_dict)
                except SyntaxException as qError:
                    docassemble.base.functions.reset_context()
                    the_question = None
                    try:
                        the_question = question
                    except:
                        pass
                    docassemble.base.functions.close_files()
                    if the_question is not None:
                        raise DAError(str(qError) + "\n\n" + str(self.idebug(self.data_for_debug)))
                    raise DAError("no question available: " + str(qError))
                else:
                    docassemble.base.functions.close_files()
                    raise DAErrorNoEndpoint('Docassemble has finished executing all code blocks marked as initial or mandatory, and finished asking all questions marked as mandatory (if any).  It is a best practice to end your interview with a question that says goodbye and offers an Exit button.')
        except Exception as the_error:
            if debug:
                the_error.interview = self
                the_error.interview_status = interview_status
                if not hasattr(the_error, 'traceback'):
                    the_error.traceback = traceback.format_exc()
            raise the_error
        if docassemble.base.functions.get_info('prevent_going_back'):
            interview_status.can_go_back = False
        docassemble.base.functions.close_files()
        if debug:
            interview_status.seeking.append({'done': True, 'time': time.time()})
        #return(pickleable_objects(user_dict))
    def askfor(self, missingVariable, user_dict, old_user_dict, interview_status, **kwargs):
        variable_stack = kwargs.get('variable_stack', set())
        questions_tried = kwargs.get('questions_tried', dict())
        recursion_depth = kwargs.get('recursion_depth', 0)
        recursion_depth += 1
        language = get_language()
        current_question = None
        follow_mc = kwargs.get('follow_mc', True)
        seeking = kwargs.get('seeking', list())
        if debug:
            seeking.append({'variable': missingVariable, 'time': time.time()})
        if recursion_depth > self.recursion_limit:
            raise DAError("There appears to be an infinite loop.  Variables in stack are " + ", ".join(variable_stack) + ".")
        # logmessage("askfor: I don't have " + str(missingVariable) + " for language " + str(language))
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
        #logmessage(repr(variants))
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
                    for cl in type(root_evaluated).__bases__:
                        classes_to_look_for.append(cl.__name__)
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
        while True:
            num_cycles += 1
            if num_cycles > self.loop_limit:
                raise DAError("Infinite loop detected while looking for " + missing_var)
            a_question_was_skipped = False
            docassemble.base.functions.reset_gathering_mode(origMissingVariable)
            # logmessage("Starting the while loop")
            try:
                for the_question, is_generic, the_x, iterators, missing_var, generic_object in questions_to_try:
                    # logmessage("In for loop with question " + the_question.name)
                    if missing_var in questions_tried and the_question in questions_tried[missing_var]:
                        a_question_was_skipped = True
                        # logmessage("Skipping question " + the_question.name)
                        continue
                    current_question = the_question
                    if follow_mc:
                        question = the_question.follow_multiple_choice(user_dict, interview_status)
                    else:
                        question = the_question
                    if debug:
                        seeking.append({'question': question, 'reason': 'considering', 'time': time.time()})
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
                    if debug:
                        seeking.append({'question': question, 'reason': 'asking', 'time': time.time()})
                    if question.question_type == "data":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_dataobject(question.fields[0].data, user_dict))
                        exec(string, user_dict)
                        docassemble.base.functions.pop_current_variable()
                        return({'type': 'continue', 'sought': missing_var})
                    if question.question_type == "data_from_code":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        string = from_safeid(question.fields[0].saveas) + ' = ' + repr(recursive_eval_data_from_code(question.fields[0].data, user_dict))
                        exec(string, user_dict)
                        docassemble.base.functions.pop_current_variable()
                        return({'type': 'continue', 'sought': missing_var})
                    if question.question_type == "objects":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        success = False
                        for keyvalue in question.objects:
                            # logmessage("In a for loop for keyvalue")
                            for variable, object_type_name in keyvalue.iteritems():
                                if variable != missing_var:
                                    continue
                                was_defined = False
                                try:
                                    exec("__oldvariable__ = " + str(missing_var), user_dict)
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
                        docassemble.base.functions.pop_current_variable()
                        # logmessage("Returning")
                        return({'type': 'continue', 'sought': missing_var})
                    if question.question_type == "template":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        if question.target is not None:
                            return({'type': 'template', 'question_text': question.content.text(user_dict).rstrip(), 'subquestion_text': None, 'under_text': None, 'continue_label': None, 'audiovideo': None, 'decorations': None, 'help_text': None, 'attachments': None, 'question': question, 'selectcompute': dict(), 'defaults': dict(), 'hints': dict(), 'helptexts': dict(), 'extras': dict(), 'labels': dict(), 'sought': missing_var})
                        string = "import docassemble.base.core"
                        exec(string, user_dict)
                        if question.decorations is None:
                            decoration_list = []
                        else:
                            decoration_list = question.decorations
                        string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.DATemplate(' + repr(from_safeid(question.fields[0].saveas)) + ", content=" + repr(question.content.text(user_dict).rstrip()) + ', subject=' + repr(question.subcontent.text(user_dict).rstrip()) + ', decorations=' + repr([dec['image'].text(user_dict).rstrip() for dec in decoration_list]) + ')'
                        #logmessage("Doing " + string)
                        exec(string, user_dict)
                        #question.mark_as_answered(user_dict)
                        docassemble.base.functions.pop_current_variable()
                        return({'type': 'continue', 'sought': missing_var})
                    if question.question_type == "table":
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        string = "import docassemble.base.core"
                        exec(string, user_dict)
                        table_content = "\n"
                        header = question.fields[0].extras['header']
                        row = question.fields[0].extras['row']
                        column = question.fields[0].extras['column']
                        indent = " " * (4 * int(question.fields[0].extras['indent']))
                        header_output = [table_safe(x.text(user_dict)) for x in header]
                        the_iterable = eval(row, user_dict)
                        if not hasattr(the_iterable, '__iter__'):
                            raise DAError("Error in processing table " + from_safeid(question.fields[0].saveas) + ": row value is not iterable")
                        if hasattr(the_iterable, 'instanceName') and hasattr(the_iterable, 'elements') and type(the_iterable.elements) in (list, dict) and docassemble.base.functions.get_gathering_mode(the_iterable.instanceName):
                            the_iterable = the_iterable._validated_elements()
                        indexno = 0
                        contents = list()
                        for item in the_iterable:
                            user_dict['row_item'] = item
                            user_dict['row_index'] = indexno
                            contents.append([table_safe(eval(x, user_dict)) for x in column])
                            indexno += 1
                        user_dict.pop('row_item', None)
                        user_dict.pop('row_index', None)
                        max_chars = [0 for x in header_output]
                        max_word = [0 for x in header_output]
                        for indexno in range(len(header_output)):
                            words = re.split(r'[ \n]', header_output[indexno])
                            if len(header_output[indexno]) > max_chars[indexno]:
                                max_chars[indexno] = len(header_output[indexno])
                            for content_line in contents:
                                words += re.split(r'[ \n]', content_line[indexno])
                                if len(content_line[indexno]) > max_chars[indexno]:
                                    max_chars[indexno] = len(content_line[indexno])
                            for text in words:
                                if len(text) > max_word[indexno]:
                                    max_word[indexno] = len(text)
                        max_chars_to_use = [min(x, self.table_width) for x in max_chars]
                        override_mode = False
                        while True:
                            new_sum = sum(max_chars_to_use)
                            old_sum = new_sum
                            if new_sum < self.table_width:
                                break
                            r = random.uniform(0, new_sum)
                            upto = 0
                            for indexno in range(len(max_chars_to_use)):
                                if upto + max_chars_to_use[indexno] >= r:
                                    if max_chars_to_use[indexno] > max_word[indexno] or override_mode:
                                        max_chars_to_use[indexno] -= 1
                                        break
                                upto += max_chars_to_use[indexno]
                            new_sum = sum(max_chars_to_use)
                            if new_sum == old_sum:
                                override_mode = True
                        table_content += indent + "|".join(header_output) + "\n"
                        table_content += indent + "|".join(['-' * x for x in max_chars_to_use]) + "\n"
                        for content_line in contents:
                            table_content += indent + "|".join(content_line) + "\n"
                        if len(contents) == 0 and question.fields[0].extras['empty_message'] is not True:
                            if question.fields[0].extras['empty_message'] in (False, None):
                                table_content = "\n"
                            else:
                                table_content = question.fields[0].extras['empty_message'].text(user_dict) + "\n"
                        table_content += "\n"
                        string = from_safeid(question.fields[0].saveas) + ' = docassemble.base.core.DATemplate(' + repr(from_safeid(question.fields[0].saveas)) + ", content=" + repr(table_content) + ")"
                        exec(string, user_dict)
                        docassemble.base.functions.pop_current_variable()
                        return({'type': 'continue', 'sought': missing_var})
                    if question.question_type == 'attachments':
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        attachment_text = question.processed_attachments(user_dict, seeking_var=origMissingVariable)
                        if missing_var in variable_stack:
                            variable_stack.remove(missing_var)
                        try:
                            eval(missing_var, user_dict)
                            question.mark_as_answered(user_dict)
                            docassemble.base.functions.pop_current_variable()
                            return({'type': 'continue', 'sought': missing_var})
                        except:
                            continue
                    if question.question_type in ["code", "event_code"]:
                        question.exec_setup(is_generic, the_x, iterators, user_dict)
                        was_defined = False
                        try:
                            exec("__oldvariable__ = " + str(missing_var), user_dict)
                            exec("del " + str(missing_var), user_dict)
                            was_defined = True
                        except:
                            pass
                        exec_with_trap(question, user_dict)
                        interview_status.mark_tentative_as_answered(user_dict)
                        if missing_var in variable_stack:
                            variable_stack.remove(missing_var)
                        if question.question_type == 'event_code':
                            docassemble.base.functions.pop_current_variable()
                            return({'type': 'continue', 'sought': missing_var})
                        try:
                            eval(missing_var, user_dict)
                            question.mark_as_answered(user_dict)
                            docassemble.base.functions.pop_current_variable()
                            return({'type': 'continue', 'sought': missing_var})
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
                        return question.ask(user_dict, old_user_dict, the_x, iterators, missing_var)
                if a_question_was_skipped:
                    raise DAError("Infinite loop: " + missingVariable + " already looked for, where stack is " + str(variable_stack))
                raise DAErrorMissingVariable("Interview has an error.  There was a reference to a variable '" + origMissingVariable + "' that could not be looked up in the question file or in any of the files incorporated by reference into the question file.", variable=origMissingVariable)
            except NameError as the_exception:
                # logmessage("NameError: " + str(the_exception))
                docassemble.base.functions.reset_context()
                if isinstance(the_exception, ForcedNameError):
                    #logmessage("askfor: got a ForcedNameError for " + the_exception.name)
                    follow_mc = False
                    newMissingVariable = the_exception.name
                    if the_exception.next_action is not None:
                        interview_status.next_action.extend(the_exception.next_action)
                else:
                    #logmessage("regular nameerror")
                    follow_mc = True
                    newMissingVariable = extract_missing_name(the_exception)
                #newMissingVariable = str(the_exception).split("'")[1]
                #if newMissingVariable in questions_tried and newMissingVariable in variable_stack:
                #    raise DAError("Infinite loop: " + missingVariable + " already looked for, where stack is " + str(variable_stack))
                if newMissingVariable not in questions_tried:
                    questions_tried[newMissingVariable] = set()
                else:
                    variable_stack.add(missingVariable)
                questions_tried[newMissingVariable].add(current_question)
                question_result = self.askfor(newMissingVariable, user_dict, old_user_dict, interview_status, variable_stack=variable_stack, questions_tried=questions_tried, seeking=seeking, follow_mc=follow_mc, recursion_depth=recursion_depth)
                if question_result['type'] == 'continue' and missing_var != newMissingVariable:
                    # logmessage("Continuing after asking for newMissingVariable " + str(newMissingVariable))
                    continue
                docassemble.base.functions.pop_current_variable()
                return(question_result)
            except UndefinedError as the_exception:
                # logmessage("UndefinedError: " + str(the_exception))
                docassemble.base.functions.reset_context()
                newMissingVariable = extract_missing_name(the_exception)
                if newMissingVariable not in questions_tried:
                    questions_tried[newMissingVariable] = set()
                else:
                    variable_stack.add(missingVariable)
                questions_tried[newMissingVariable].add(current_question)
                question_result = self.askfor(newMissingVariable, user_dict, old_user_dict, interview_status, variable_stack=variable_stack, questions_tried=questions_tried, seeking=seeking, follow_mc=True, recursion_depth=recursion_depth)
                if question_result['type'] == 'continue':
                    continue
                docassemble.base.functions.pop_current_variable()
                return(question_result)
            except CommandError as qError:
                # logmessage("CommandError: " + str(qError))
                docassemble.base.functions.reset_context()
                question_data = dict(command=qError.return_type, url=qError.url)
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var))
            except ResponseError as qError:
                # logmessage("ResponseError")
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
                    question_data['content type'] = 'application/json'
                    question_data['all_variables'] = True
                if hasattr(qError, 'content_type') and qError.content_type:
                    question_data['content type'] = qError.content_type
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                #the_question = new_question.follow_multiple_choice(user_dict)
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var))
            except BackgroundResponseError as qError:
                # logmessage("BackgroundResponseError")
                docassemble.base.functions.reset_context()
                #logmessage("Trapped BackgroundResponseError2")
                question_data = dict(extras=dict())
                if hasattr(qError, 'backgroundresponse'):
                    question_data['backgroundresponse'] = qError.backgroundresponse
                new_interview_source = InterviewSourceString(content='')
                new_interview = new_interview_source.get_interview()
                reproduce_basics(self, new_interview)
                new_question = Question(question_data, new_interview, source=new_interview_source, package=self.source.package)
                new_question.name = "Question_Temp"
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var))
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
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var))
            except QuestionError as qError:
                # logmessage("QuestionError")
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
                # will this be a problem? yup
                # the_question = new_question.follow_multiple_choice(user_dict)
                return(new_question.ask(user_dict, old_user_dict, 'None', [], missing_var))
            except CodeExecute as code_error:
                # logmessage("CodeExecute")
                docassemble.base.functions.reset_context()
                #if debug:
                #    interview_status.seeking.append({'question': question, 'reason': 'mandatory code'})
                #logmessage("Going to execute " + str(code_error.compute) + " where missing_var is " + str(missing_var))
                exec(code_error.compute, user_dict)
                try:
                    eval(missing_var, user_dict)
                    #logmessage(str(missing_var) + " was defined")
                    code_error.question.mark_as_answered(user_dict)
                    #logmessage("Got here 1")
                    #logmessage("returning from running code")
                    docassemble.base.functions.pop_current_variable()
                    #logmessage("Got here 2")
                    return({'type': 'continue', 'sought': missing_var})
                except:
                    #raise DAError("Problem setting that variable")
                    continue
            except SyntaxException as qError:
                # logmessage("SyntaxException")
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
            #     return(new_question.ask(user_dict, old_user_dict, 'None', [], None))
        raise DAErrorMissingVariable("Interview has an error.  There was a reference to a variable '" + origMissingVariable + "' that could not be found in the question file (for language '" + str(language) + "') or in any of the files incorporated by reference into the question file.", variable=origMissingVariable)

def reproduce_basics(interview, new_interview):
    new_interview.metadata = interview.metadata
    new_interview.external_files = interview.external_files

def unpack_list(item, target_list=None):
    if target_list is None:
        target_list = list()
    if type(item) not in [list, dict]:
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
    if type(data) is list or (hasattr(data, 'elements') and type(data.elements) is list):
        for entry in data:
            if type(entry) is dict or (hasattr(entry, 'elements') and type(entry.elements) is dict):
                the_item = dict()
                for key in entry:
                    if len(entry) > 1:
                        if key in ['default', 'help', 'image']:
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
                            elif entry['image'].__class__.__name__ == 'DAStaticFile':
                                the_item['image'] = dict(type='url', value=entry['image'].url_for())
                            else:
                                the_item['image'] = dict(type='decoration', value=entry['image'])
                    the_item['key'] = key
                    the_item['label'] = entry[key]
                    is_not_boolean = False
                    for val in entry.values():
                        if val not in (True, False):
                            is_not_boolean = True
                    if key not in to_exclude and (is_not_boolean or entry[key] is True):
                        result.append(the_item)
            if (type(entry) is list or (hasattr(entry, 'elements') and type(entry.elements) is list)) and len(entry) > 0:
                if entry[0] not in to_exclude:
                    if len(entry) >= 4:
                        result.append(dict(key=entry[0], label=entry[1], default=entry[2], help=entry[3]))
                    elif len(entry) == 3:
                        result.append(dict(key=entry[0], label=entry[1], default=entry[2]))
                    elif len(entry) == 1:
                        result.append(dict(key=entry[0], label=entry[0]))
                    else:
                        result.append(dict(key=entry[0], label=entry[1]))
            elif type(entry) in (str, unicode, bool, int, float):
                if entry not in to_exclude:
                    result.append(dict(key=entry, label=entry))
            elif hasattr(entry, 'instanceName'):
                if entry not in to_exclude:
                    result.append(dict(key=unicode(entry), label=unicode(entry)))
    elif type(data) is dict or (hasattr(data, 'elements') and type(data.elements) is dict):
        for key, value in sorted(data.items(), key=operator.itemgetter(1)):
            if key not in to_exclude:
                if type(value) in (str, unicode, bool, int, float):
                    result.append(dict(key=key, label=value))
                elif hasattr(value, 'instanceName'):
                    result.append(dict(key=key, label=unicode(value)))
    else:
        raise DAError("Unknown data type in choices selection: " + re.sub(r'[<>]', '', repr(data)))
    return(result)

def process_selections_manual(data):
    result = []
    if type(data) is list:
        for entry in data:
            if type(entry) is dict:
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
                            the_item['help'] = TextObject(entry['help'])
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
                            the_item['key'] = TextObject(entry['key'])
                            the_item['label'] = TextObject(entry['label'])
                            result.append(the_item)
                            continue
                    the_item['key'] = TextObject(entry[key])
                    the_item['label'] = TextObject(key)
                    result.append(the_item)
            if type(entry) is list:
                result.append(dict(key=TextObject(entry[0]), label=TextObject(entry[1])))
            elif type(entry) is str or type(entry) is unicode:
                result.append(dict(key=TextObject(entry), label=TextObject(entry)))
    elif type(data) is dict:
        for key, value in sorted(data.items(), key=operator.itemgetter(1)):
            result.append(dict(key=TextObject(value), label=TextObject(key)))
    else:
        raise DAError("Unknown data type in manual choices selection: " + re.sub(r'[<>]', '', repr(data)))
    return(result)

def extract_missing_name(the_error):
    #logmessage("extract_missing_name: string was " + str(string))
    m = nameerror_match.search(unicode(the_error))
    if m:
        return m.group(1)
    else:
        raise the_error
        #raise DAError("Unable to extract variable name from '" + unicode(the_error) + "'")

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
        return u'no label'
    return unicode(text)

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

def ensure_object_exists(saveas, datatype, user_dict, commands=None):
    # logmessage("ensure object exists: " + str(saveas))
    if commands is None:
        execute = True
        commands = list()
    else:
        execute = False
    already_there = False
    try:
        eval(saveas, user_dict)
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
                core_key = eval(parse_result['final_parts'][0], user_dict)
                if hasattr(core_key, 'instanceName'):
                    method = 'attribute'
            except:
                pass
        elif parse_result['final_parts'][1][0] == '[':
            try:
                core_key = eval(parse_result['final_parts'][0], user_dict)
                if hasattr(core_key, 'instanceName'):
                    method = 'index'
            except:
                pass
    if "import docassemble.base.core" not in commands:
        commands.append("import docassemble.base.core")
    if method == 'attribute':
        attribute_name = parse_result['final_parts'][1][1:]
        if datatype == 'checkboxes':
            commands.append(parse_result['final_parts'][0] + ".initializeAttribute(" + repr(attribute_name) + ", docassemble.base.core.DADict, auto_gather=False)")
        elif datatype == 'object_checkboxes':
            commands.append(parse_result['final_parts'][0] + ".initializeAttribute(" + repr(attribute_name) + ", docassemble.base.core.DAList, auto_gather=False)")
    elif method == 'index':
        index_name = parse_result['final_parts'][1][1:-1]
        if datatype == 'checkboxes':
            commands.append(parse_result['final_parts'][0] + ".initializeObject(" + repr(index_name) + ", docassemble.base.core.DADict, auto_gather=False)")
        elif datatype == 'object_checkboxes':
            commands.append(parse_result['final_parts'][0] + ".initializeObject(" + repr(index_name) + ", docassemble.base.core.DAList, auto_gather=False)")
    else:
        if datatype == 'checkboxes':
            commands.append(saveas + ' = docassemble.base.core.DADict(' + repr(saveas) + ', auto_gather=False)')
        elif datatype == 'object_checkboxes':
            commands.append(saveas + ' = docassemble.base.core.DAList(' + repr(saveas) + ', auto_gather=False)')
    if execute:
        for command in commands:
            # logmessage("Doing " + command)
            exec(command, user_dict)
    
def invalid_variable_name(varname):
    if type(varname) not in (str, unicode):
        return True
    if re.search(r'[\n\r\(\)\{\}\*\^\#]', varname):
        return True
    varname = re.sub(r'[\.\[].*', '', varname)
    if not valid_variable_match.match(varname):
        return True 
    return False

def exec_with_trap(the_question, the_dict):
    try:
        exec(the_question.compute, the_dict)
    except (NameError, UndefinedError, CommandError, ResponseError, BackgroundResponseError, BackgroundResponseActionError, QuestionError, AttributeError, MandatoryQuestion, CodeExecute, SyntaxException):
        raise
    except Exception as e:
        cl, exc, tb = sys.exc_info()
        if len(traceback.extract_tb(tb)) == 2:
            line_with_error = traceback.extract_tb(tb)[-1][1]
            if type(line_with_error) is int and line_with_error > 0 and hasattr(the_question, 'sourcecode'):
                exc.da_line_with_error = the_question.sourcecode.splitlines()[line_with_error - 1]
                exc.traceback = traceback.format_exc()
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
