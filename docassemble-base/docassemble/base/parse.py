import re
import ast
import yaml
import os
import os.path
import sys
import subprocess
import shutil
import tempfile
import httplib2
import datetime
import operator
import pkg_resources
import docassemble.base.filter
from docassemble.base.error import DAError, MandatoryQuestion
from docassemble.base.util import pickleable_objects, word
from docassemble.base.logger import logmessage
from mako.template import Template

match_mako = re.compile(r'<%|\${|% if|% for|% while')

PANDOC_PATH = 'pandoc'

class InterviewSource(object):
    def __init__(self, **kwargs):
        pass
    def set_path(self, path):
        self.path = path
        return
    def set_directory(self, directory):
        self.directory = directory
        return
    def set_content(self, content):
        self.content = content
        return
    def update(self):
        return True
    def get_modtime(self):
        return self._modtime
    def get_interview(self):
        return Interview(source=self)
    def append(self, path):
        return None

class InterviewSourceString(InterviewSource):
    def __init__(self, **kwargs):
        self.set_path(kwargs.get('path', None))
        self.set_directory(kwargs.get('directory', None))
        self.set_content(kwargs.get('content', None))
        return super(InterviewSourceString, self).__init__(**kwargs)

class InterviewSourceFile(InterviewSource):
    def __init__(self, **kwargs):
        if 'filepath' in kwargs:
            self.set_filepath(kwargs['filepath'])
        else:
            self.filepath = None
        if 'path' in kwargs:
            self.set_path(kwargs['path'])
        return super(InterviewSourceFile, self).__init__(**kwargs)
    def set_path(self, path):
        self.path = path
        if self.filepath is None:
            self.set_filepath(interview_source_from_string(self.path))
        return
    def set_filepath(self, filepath):
        self.filepath = filepath
        if self.filepath is None:
            self.directory = None
        else:
            self.set_directory(os.path.dirname(self.filepath))
        return
    def update(self):
        try:
            with open(self.filepath) as the_file:
                self.set_content(the_file.read())
                return True
        except:
            pass
        return False
    def get_modtime(self):
        self._modtime = os.path.getmtime(self.filepath)
        return(self._modtime)
    def append(self, path):
        new_file = os.path.join(self.directory, path)
        if os.path.isfile(new_file) and os.access(new_file, os.R_OK):
            new_source = InterviewSourceFile()
            new_source.path = path
            new_source.filepath = new_file
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
                self._modtime = datetime.datetime.now()
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

def standard_template_filename(the_file):
    try:
        return(pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.base'), "docassemble/base/data/templates/" + str(the_file)))
    except:
        #logmessage("Error retrieving data file\n")
        return(None)

def standard_question_filename(the_file):
    #try:
    return(pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.base'), "docassemble/base/data/questions/" + str(the_file)))
    #except:
    #logmessage("Error retrieving question file\n")
    return(None)

def package_template_filename(the_file):
    parts = the_file.split(":")
    if len(parts) == 2:
        try:
            return(pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1]))
        except:
            return(None)
    return(None)

def package_question_filename(the_file):
    parts = the_file.split(":")
    if len(parts) == 2:
        try:
            return(pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1]))
        except:
            return(None)
    return(None)

def absolute_filename(the_file):
    if os.path.isfile(the_file) and os.access(the_file, os.R_OK):
        return(the_file)
    return(None)

def set_pandoc_path(path):
    global PANDOC_PATH
    PANDOC_PATH = path
#fontfamily: zi4, mathptmx, courier
#\ttfamily
#\renewcommand{\thesubsubsubsection}{\alph{subsubsubsection}.}
#\renewcommand{\thesubsubsubsubsection}{\roman{subsubsubsubsection}.}
#  - \newenvironment{allcaps}{\startallcaps}{}
#  - \def\startallcaps#1\end{\uppercase{#1}\end}

class InterviewStatus(object):
    def __init__(self):
        self.attachments = None
    def populate(self, question_result, interview_help):
        self.question = question_result['question']
        self.questionText = question_result['question_text']
        self.subquestionText = question_result['subquestion_text']
        self.helpText = question_result['help_text']
        #self.missingVariable = question_result['missing_variable']
        self.attachments = question_result['attachments']
        self.selectcompute = question_result['selectcompute']
        self.defaults = question_result['defaults']
        self.hints = question_result['hints']
        #self.genericVariables = {'x': question_result['variable_x'], 'i': question_result['variable_i']}
        if len(interview_help) > 0:
            self.helpText.extend(interview_help)
    pass

class Pandoc(object):
    def __init__(self):
        self.input_content = None
        self.output_content = None
        self.input_format = 'markdown'
        self.output_format = 'rtf'
        self.output_filename = None
        self.template_file = None
        self.initial_yaml = list()
        self.additional_yaml = list()
        self.arguments = []
    def convert_to_file(self):
        if self.output_format == 'rtf' and self.template_file is None:
            self.template_file = standard_template_filename('Legal-Template.rtf')
        if (self.output_format == 'pdf' or self.output_format == 'tex') and self.template_file is None:
            self.template_file = standard_template_filename('Legal-Template.tex')
        yaml_to_use = []
        if self.output_format == 'pdf' or self.output_format == 'tex':
            print "Before: " + str(self.input_content)
            self.input_content = docassemble.base.filter.pdf_filter(self.input_content)
            print "After: " + str(self.input_content)
            if len(self.initial_yaml) == 0:
                standard_file = standard_template_filename('Legal-Template.yml')
                if standard_file is not None:
                    self.initial_yaml.append(standard_file)
            yaml_to_use.extend(self.initial_yaml)
            if len(self.additional_yaml) > 0:
                yaml_to_use.extend(self.additional_yaml)
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        temp_file.write(self.input_content)
        temp_file.close()
        temp_outfile = tempfile.NamedTemporaryFile(mode="w", suffix="." + str(self.output_format), delete=False)
        temp_outfile.close()
        subprocess_arguments = [PANDOC_PATH]
        subprocess_arguments.extend(yaml_to_use)
        subprocess_arguments.extend([temp_file.name])
        if self.template_file is not None:
            subprocess_arguments.extend(['--template=%s' % self.template_file])
        subprocess_arguments.extend(['-s -o %s' % temp_outfile.name])
        subprocess_arguments.extend(self.arguments)
        for argum in subprocess_arguments:
            logmessage(str(argum) + "\n")
        cmd = " ".join(subprocess_arguments)
        fin = os.popen(cmd)
        msg = fin.read()
        fin.close()
        if msg:
            self.pandoc_message = msg
        os.remove(temp_file.name)
        if os.path.exists(temp_outfile.name):
            if self.output_format == 'rtf':
                with open(temp_outfile.name) as the_file: file_contents = the_file.read()
                file_contents = docassemble.base.filter.rtf_filter(file_contents)
                with open(temp_outfile.name, "w") as the_file: the_file.write(file_contents)
            if self.output_filename is not None:
                shutil.copyfile(temp_outfile.name, self.output_filename)
            else:
                self.output_filename = temp_outfile.name
            self.output_content = None
        else:
            raise IOError("Failed creating file: %s" % output_filename)
        return
    def convert(self):
        if (self.output_format == "pdf" or self.output_format == "tex" or self.output_format == "rtf" or self.output_format == "epub"):
            self.convert_to_file()
        else:
            subprocess_arguments = [PANDOC_PATH, '--from=%s' % self.input_format, '--to=%s' % self.output_format]
            subprocess_arguments.extend(self.arguments)
            p = subprocess.Popen(
                subprocess_arguments,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            self.output_filename = None
            self.output_content = p.communicate(self.input_content)[0]

# def new_counter(initial_value=0):
#     d = {'counter': initial_value}
#     def f():
#         return_value = d['counter']
#         d['counter'] += 1
#         return(return_value)
#     return f

# increment_question_counter = new_counter()

# class Content(object):
#     def __init__(self, **kwargs):
#         self.compute = False
#         if 'code' in kwargs:
#             self.compute = True
#             self.code = compile(kwargs['code'], '', 'eval')
#         else:
#             self.compute = False
#         if 'content' in kwargs:
#             self.content = kwargs['content']
#     def text(self, user_dict):
#         if self.compute:
#             return eval(self.code, user_dict)
#         else:
#             return self.content

class TextObject(object):
    def __init__(self, x):
        self.original_text = x
        if match_mako.search(x):
            self.template = Template(x, strict_undefined=True)
            self.uses_mako = True
        else:
            self.uses_mako = False
    def text(self, user_dict, **kwargs):
        if self.uses_mako:
            #if ('the_x' in kwargs or 'the_i' in kwargs) and (kwargs['the_x'] != 'None' or kwargs['the_i'] != 'None'):
            #    exec("x = " + kwargs['the_x'] + "\ni = " + kwargs['the_i'], user_dict)
            return(self.template.render(**user_dict))
        else:
            return(self.original_text)
            
class Field:
    def __init__(self, data):
        if 'saveas' in data:
            self.saveas = data['saveas']
        if 'label' in data:
            self.label = data['label']
        if 'type' in data:
            self.datatype = data['type']
        if 'default' in data:
            self.default = data['default']
        if 'hint' in data:
            self.hint = data['hint']
        if 'selections' in data:
            self.selections = data['selections']
        if 'boolean' in data:
            self.datatype = 'boolean'
            self.sign = data['boolean']
        if 'choices' in data:
            self.fieldtype = 'multiple_choice'
            self.choices = data['choices']
        if 'required' in data:
            self.required = data['required']
        else:
            self.required = True

class Question:
    def __init__(self, data, caller, **kwargs):
        should_append = True
        if 'register_target' in kwargs:
            register_target = kwargs['register_target']
            main_list = False
        else:
            register_target = self
            main_list = True
        self.from_path = kwargs.get('path', None)
        self.interview = caller
        self.fields = []
        self.attachments = []
        self.name = None
        self.need = None
        self.helptext = None
        self.subcontent = None
        self.progress = None
        self.fields_used = set()
        self.names_used  = set()
        self.role = set()
        if 'mandatory' in data and data['mandatory']:
            self.is_mandatory = True
        else:
            self.is_mandatory = False
        if 'command' in data and data['command'] in ['exit', 'continue', 'restart']:
            self.question_type = data['command']
            self.content = TextObject("")
            return
        if 'objects' in data:
            if type(data['objects']) is not list:
                raise DAError("Unknown data type in objects")
            self.question_type = 'objects'
            self.objects = data['objects']
            for item in data['objects']:
                if type(item) is dict:
                    for key in item:
                        self.fields.append(Field({'saveas': key, 'type': 'object', 'objecttype': item[key]}))
                        self.fields_used.add(key)
                elif type(item) is str:
                    self.fields.append(Field({'saveas': item, 'type': 'object', 'objecttype': data['objects'][key]}))
                    self.fields_used.add(item)
                else:
                    raise DAError("Unknown data type within objects")
        if 'id' in data:
            self.id = data['id']
        if 'interview help' in data:
            should_append = False
            if type(data['interview help']) is not dict:
                raise DAError("Unknown data type within help")
            if 'heading' in data['interview help']:
                if type(data['interview help']['heading']) not in [dict, list]:
                    help_heading = data['interview help']['heading']
                else:
                    raise DAError("Unknown data type within help heading")
            else:
                help_heading = None
            if 'content' in data['interview help']:
                if type(data['interview help']['content']) not in [dict, list]:
                    help_content = data['interview help']['content']
                else:
                    raise DAError("Unknown data type within help content")
            else:
                raise DAError("No content within help")
            self.interview.helptext.append({'content': help_content, 'heading': help_heading})
        if 'generic object' in data:
            self.is_generic = True
            self.is_generic_list = False
            self.generic_object = data['generic object']
        elif 'generic list object' in data:
            self.is_generic = True
            self.is_generic_list = True
            self.generic_object = data['generic list object']
        else:
            self.is_generic = False
        if 'metadata' in data:
            should_append = False
            if (type(data['metadata']) == dict):
                data['metadata']['origin_path'] = self.from_path
                self.interview.metadata.append(data['metadata'])
            else:
                raise DAError("Unknown data type in metadata")
        if 'modules' in data:
            if type(data['modules']) is list:
                self.question_type = 'modules'
                self.module_list = data['modules']
            else:
                raise DAError("Unknown data type in modules")
        if 'imports' in data:
            if type(data['imports']) is list:
                self.question_type = 'imports'
                self.module_list = data['imports']
            else:
                raise DAError("Unknown data type in imports")
        if 'include' in data:
            should_append = False
            if type(data['include']) is list:
                for questionPath in data['include']:
                    self.interview.read_from(interview_source_from_string(questionPath, context_interview=self.interview))
            else:
                raise DAError("Unknown data type in include")
        if 'if' in data:
            if type(data['if']) == str:
                self.condition = [data['if']]
            elif type(data['if']) == list:
                self.condition = data['if']
            else:
                raise DAError("Unknown data type in if statement")
        else:
            self.condition = []
        if 'require' in data:
            if type(data['require']) is list:
                self.question_type = 'require'
                try:
                    self.require_list = list(map((lambda x: compile(x, '', 'eval')), data['require']))
                except:
                    logmessage("Compile error in require:\n" + str(data['require']) + "\n" + str(sys.exc_info()[0]) + "\n")
                    raise
                if 'orelse' in data:
                    if type(data['orelse']) is dict:
                        self.or_else_question = Question(data['orelse'], self.interview, register_target=register_target, path=self.from_path)
                    else:
                        raise DAError("Unknown data type in orelse")
                else:
                    raise DAError("Require question lacks an orelse")
            else:
                raise DAError("Unknown data type in require")
        if 'attachment' in data:
            self.attachments = process_attachment_list(data['attachment'])
        elif 'attachments' in data:
            self.attachments = process_attachment_list(data['attachments'])
        if 'role' in data:
            if type(data['role']) is list:
                for rolename in data['role']:
                    self.role.add(rolename)
            elif type(data['role']) is str:
                self.role.add(data['role'])
            else:
                raise DAError("Unknown data type in role")
        if 'language' in data:
            self.language = data['language']
        if 'progress' in data:
            self.progress = data['progress']
        if 'question' in data:
            self.content = TextObject(data['question'])
        if 'subquestion' in data:
            self.subcontent = TextObject(data['subquestion'])
        if 'help' in data:
            self.helptext = TextObject(data['help'])
        if 'yesno' in data:
            self.fields.append(Field({'saveas': data['yesno'], 'boolean': 1}))
            self.fields_used.add(data['yesno'])
            self.question_type = 'yesno'
        if 'noyes' in data:
            self.fields.append(Field({'saveas': data['noyes'], 'boolean': -1}))
            self.fields_used.add(data['yesno'])
            self.question_type = 'noyes'
        if 'sets' in data:
            if type(data['sets']) is str:
                self.fields_used.add(data['sets'])
            elif type(data['sets']) is list:
                for key in data['sets']:
                    self.fields_used.add(key)
            else:
                raise DAError("Unknown data type in sets: " + str(data))
        if 'choices' in data or 'buttons' in data:
            if 'field' in data:
                uses_field = True
            else:
                uses_field = False
            if 'choices' in data:
                field_data = {'choices': self.parse_fields(data['choices'], register_target, uses_field)}
                self.question_variety = 'radio'
            elif 'buttons' in data:
                field_data = {'choices': self.parse_fields(data['buttons'], register_target, uses_field)}
                self.question_variety = 'buttons'
            if uses_field:
                self.fields_used.add(data['field'])
                field_data['saveas'] = data['field']
                if 'type' in data:
                    field_data['type'] = data['type']
            self.fields.append(Field(field_data))
            self.question_type = 'multiple_choice'
        if 'need' in data:
            if type(data['need']) == str:
                need_list = [data['need']]
            elif type(data['need']) == list:
                need_list = data['need']
            else:
                raise DAError("Unknown data type in need code: " + str(data))
            try:
                self.need = list(map((lambda x: compile(x, '', 'exec')), need_list))
            except:
                logmessage("Compile error in need code:\n" + str(data['need']) + "\n" + str(sys.exc_info()[0]) + "\n")
                raise
        if 'code' in data:
            self.question_type = 'code'
            if type(data['code']) == str:
                try:
                    self.compute = compile(data['code'], '', 'exec')
                    self.sourcecode = data['code']
                except:
                    logmessage("Compile error in code:\n" + str(data['code']) + "\n" + str(sys.exc_info()[0]) + "\n")
                    raise
                find_fields_in(data['code'], self.fields_used, self.names_used)
            else:
                raise DAError("Unknown data type in code: " + str(data))
        if 'fields' in data:
            self.question_type = 'fields'
            if type(data['fields']) is not list:
                raise DAError("Unknown data type in fields:" + str(type(data['fields'])) + "\n" + str(data['fields']))
            else:
                for field in data['fields']:
                    if type(field) is dict:
                        field_info = {'type': 'text'}
                        for key in field:
                            if key == 'required':
                                field_info['required'] = field[key]
                            elif key == 'default' or key == 'hint':
                                if type(field[key]) is not dict and type(field[key]) is not list:
                                    field_info[key] = TextObject(unicode(field[key]))
                            elif key == 'datatype':
                                field_info['type'] = field[key]
                                if field[key] == 'yesno' and 'required' not in field_info:
                                    field_info['required'] = False
                            elif key == 'code':
                                field_info['type'] = 'selectcompute'
                                field_info['selections'] = {'compute': compile(field[key], '', 'eval'), 'sourcecode': field[key]}
                            elif key == 'choices':
                                field_info['type'] = 'selectmanual'
                                field_info['selections'] = process_selections(field[key])
                            else:
                                field_info['label'] = key
                                field_info['saveas'] = field[key]
                        if 'saveas' in field_info:
                            self.fields.append(Field(field_info))
                            self.fields_used.add(field_info['saveas'])
                        else:
                            raise DAError("fields without value for saving:\n" + str(data))
                    else:
                        raise DAError("Unknown data type within fields")
        if should_append:
            if not hasattr(self, 'question_type'):
                raise DAError("Question has no question_type: " + str(data))
            if main_list:
                self.interview.questions_list.append(self)
            self.number = len(self.interview.questions_list) - 1
            self.name = "__Question_" + str(self.number)
        if hasattr(self, 'id'):
            try:
                self.interview.questions_by_id[self.id].append(self)
            except:
                self.interview.questions_by_id[self.id] = [self]
        for field_name in self.fields_used:
            try:
                self.interview.questions[field_name].append(register_target)
            except:
                self.interview.questions[field_name] = [register_target]
            if self.is_generic:
                if self.generic_object not in self.interview.generic_questions:
                    self.interview.generic_questions[self.generic_object] = dict()
                if field_name not in self.interview.generic_questions[self.generic_object]:
                    self.interview.generic_questions[self.generic_object][field_name] = list()
                self.interview.generic_questions[self.generic_object][field_name].append(register_target)

    def ask(self, user_dict, the_x, the_i):
        if the_x != 'None':
            exec("x = " + the_x, user_dict)
            logmessage("x is " + the_x + "\n")
        if the_i != 'None':
            exec("i = " + the_i, user_dict)
            logmessage("i is " + the_i + "\n")
        if self.helptext is not None:
            help_text_list = [{'heading': None, 'content': self.helptext.text(user_dict, the_x=the_x, the_i=the_i)}]
        else:
            help_text_list = list()
        if self.subcontent is not None:
            subquestion = self.subcontent.text(user_dict, the_x=the_x, the_i=the_i)
        else:
            subquestion = None
        if self.need is not None:
            for need_entry in self.need:
                exec(need_entry, user_dict)
        selectcompute = dict()
        defaults = dict()
        hints = dict()
        for field in self.fields:
            if hasattr(field, 'datatype') and field.datatype == 'selectcompute':
                selectcompute[field.saveas] = process_selections(eval(field.selections['compute'], user_dict))
            if hasattr(field, 'saveas'):
                try:
                    defaults[field.saveas] = eval(field.saveas, user_dict)
                except:
                    if hasattr(field, 'default'):
                        defaults[field.saveas] = field.default.text(user_dict, the_x=the_x, the_i=the_i)
                if hasattr(field, 'hint'):
                    hints[field.saveas] = field.hint.text(user_dict, the_x=the_x, the_i=the_i)
        return({'type': 'question', 'question_text': self.content.text(user_dict, the_x=the_x, the_i=the_i), 'subquestion_text': subquestion, 'help_text': help_text_list, 'attachments': self.processed_attachments(user_dict, the_x=the_x, the_i=the_i), 'question': self, 'variable_x': the_x, 'variable_i': the_i, 'selectcompute': selectcompute, 'defaults': defaults, 'hints': hints})

    def processed_attachments(self, user_dict, **kwargs):
        return(list(map((lambda x: make_attachment(x, user_dict, **kwargs)), self.attachments)))
    def parse_fields(self, the_list, register_target, uses_field):
        result_list = list()
        if type(the_list) is not list:
            raise DAError("Unknown data type for the_list in parse_fields")
        for the_dict in the_list:
            if type(the_dict) is str:
                the_dict = {the_dict: the_dict}
            elif type(the_dict) is not dict:
                raise DAError("Unknown data type for the_dict in parse_fields")
            for key in the_dict:
                value = the_dict[key]
                if uses_field:
                    result_list.append({key: value})
                elif type(value) == dict:
                    result_list.append({key: Question(value, self.interview, register_target=register_target, path=self.from_path)})
                elif type(value) == str:
                    if value in ["continue", "exit", "restart"]:
                        result_list.append({key: Question({'command': value}, self.interview, register_target=register_target, path=self.from_path)})
                    else:
                        result_list.append({key: value})
                elif type(value) == bool:
                    result_list.append({key: value})
                else:
                    raise DAError("Unknown data type in parse_fields:" + str(type(value)))
        return result_list
    def follow_multiple_choice(self, user_dict):
        #if self.name:
            #logmessage("question is " + self.name + "\n")
        #else:
            #logmessage("question has no name\n")
        if self.name and self.name in user_dict['answers']:
            #logmessage("question in answers\n")
            user_dict['answered'].add(self.name)
            the_choice = self.fields[0].choices[int(user_dict['answers'][self.name])]
            for key in the_choice:
                #logmessage("Setting target\n")
                target = the_choice[key]
                break
            if target:
                #logmessage("Target defined\n")
                if type(target) is str:
                    pass
                elif isinstance(target, Question):
                    logmessage("Reassigning question\n")
                    return(target.follow_multiple_choice(user_dict))
        return(self)

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
    sys.stderr.write("Trying to find it")
    for the_filename in [package_question_filename(path), standard_question_filename(path), absolute_filename(path)]:
        sys.stderr.write("Trying " + str(the_filename))
        if the_filename is not None:
            new_source = InterviewSourceFile(filepath=the_filename, path=path)
            if new_source.update():
                return(new_source)
    raise DAError("YAML file " + str(path) + " not found")

class Interview:
    def __init__(self, **kwargs):
        #questionFilepath = kwargs.get('questionFilepath', None)
        #self.questionPath = None
        #self.rootDirectory = None
        self.source = None
        self.questions = dict()
        self.generic_questions = dict()
        self.questions_by_id = dict()
        self.questions_list = list()
        self.metadata = list()
        self.helptext = list()
        if 'source' in kwargs:
            self.read_from(kwargs['source'])
    def read_from(self, source):
        if self.source is None:
            self.source = source
            #self.firstPath = source.path
            #self.rootDirectory = source.directory
        for document in yaml.load_all(source.content):
            question = Question(document, self, path=source.path)
    # def read_yaml_string(self, questionString, **kwargs):
    #     path = kwargs.get('path', None)
    #     if self.firstFile is None:
    #         self.firstFile = path
    #         self.rootDirectory = kwargs.get('directory', None)
    #     for document in yaml.load(questionString):
    #         question = Question(document, self, path=path)
    # def read_yaml_file(self, questionFilepath):
    #     if not os.path.isfile(questionFilepath):
    #         raise DAError("File " + questionFilepath + " does not exist")
    #     if not os.access(questionFilepath, os.R_OK):
    #         raise DAError("File " + questionFilepath + " is not readable")
    #     if self.firstFile is None:
    #         self.firstFile = questionFilepath
    #         self.rootDirectory = os.path.dirname(questionFilepath)
    #     stream = file(questionFilepath, 'r')
    #     for document in yaml.load_all(stream):
    #         question = Question(document, self, path=questionFilepath)
    def assemble(self, user_dict, *args):
        if len(args):
            interview_status = args[0]
        else:
            interview_status = InterviewStatus()
        if 'answered' not in user_dict:
            user_dict['answered'] = set()
        if 'answers' not in user_dict:
            user_dict['answers'] = dict()
        if 'x_stack' not in user_dict:
            user_dict['x_stack'] = list()
        if 'i_stack' not in user_dict:
            user_dict['i_stack'] = list()
        for question in self.questions_list:
            if question.question_type == 'imports':
                #logmessage("Found imports\n")
                for module_name in question.module_list:
                    #logmessage("Imported a module " + module_name + "\n")
                    exec('import ' + module_name, user_dict)
            if question.question_type == 'modules':
                for module_name in question.module_list:
                    #logmessage("Imported from module " + module_name + "\n")
                    exec('from ' + module_name + ' import *', user_dict)
        while True:
            try:
                for question in self.questions_list:
                    if question.name and question.name in user_dict['answered']:
                        continue
                    if question.question_type == 'objects':
                        logmessage("Running objects\n")
                        for keyvalue in question.objects:
                            for variable in keyvalue:
                                object_type = keyvalue[variable]
                                if re.search(r"\.", variable):
                                    m = re.search(r"(.*)\.(.*)", variable)
                                    variable = m.group(1)
                                    attribute = m.group(2)
                                    command = variable + ".initializeAttribute(name='" + attribute + "', objectType=" + object_type + ")"
                                    logmessage("Running " + command + "\n")
                                    exec(command, user_dict)
                                else:
                                    command = variable + ' = ' + object_type + '("' + variable + '")'
                                    exec(command, user_dict)
                                    #user_dict[variable] = user_dict[object_type](variable)
                        if question.name:
                            user_dict['answered'].add(question.name)
                    if question.question_type == 'code' and question.is_mandatory:
                        #logmessage("Running some code:\n\n" + question.sourcecode + "\n")
                        exec(question.compute, user_dict)
                        if question.name:
                            user_dict['answered'].add(question.name)
                    if hasattr(question, 'content') and question.name and question.is_mandatory:
                        sys.stderr.write("Asking mandatory question\n")
                        interview_status.populate(question.ask(user_dict, 'None', 'None'), self.helptext)
                        sys.stderr.write("Asked mandatory question\n")
                        raise MandatoryQuestion()
            except NameError as errMess:
                missingVariable = str(errMess).split("'")[1]
                #logmessage(str(errMess) + "\n")
                question_result = self.askfor(missingVariable, user_dict)
                if question_result['type'] == 'continue':
                    continue
                else:
                    logmessage("Need to ask:\n  " + question_result['question_text'] + "\n")
                    interview_status.populate(question_result, self.helptext)
                    break
            except AttributeError as errMess:
                logmessage(str(errMess.args) + "\n")
                raise DAError('Got error ' + str(errMess))
                #break
            except MandatoryQuestion:
                break
            else:
                raise DAError('All was defined')
                #break
        return(pickleable_objects(user_dict))
    def askfor(self, missingVariable, user_dict, **kwargs):
        variable_stack = kwargs.get('variable_stack', set())
        the_i = 'None'
        the_x = 'None'
        logmessage("I don't have " + missingVariable + "\n")
        if missingVariable in variable_stack:
            raise DAError("Infinite loop:" + missingVariable + " already looked for")
        variable_stack.add(missingVariable)
        is_generic = False
        is_iterator = False
        realMissingVariable = missingVariable
        totry = [{'real': missingVariable, 'vari': missingVariable}]
        #logmessage("moo1" + "\n")
        match_brackets_at_end = re.compile(r'^(.*)(\[[^\[]+\])$')
        match_inside_brackets = re.compile(r'\[([^\]+])\]')
        m = match_inside_brackets.search(missingVariable)
        if m:
            newMissingVariable = re.sub('\[[^\]+]\]', '[i]', missingVariable)
            totry.insert(0, {'real': missingVariable, 'vari': newMissingVariable})
        #logmessage("Length of totry is" + str(len(totry)) + "\n")
        for mv in totry:
            realMissingVariable = mv['real']
            missingVariable = mv['vari']
            logmessage("Trying missingVariable " + missingVariable + "\n")
            if missingVariable not in self.questions:
                components = missingVariable.split(".")
                realComponents = realMissingVariable.split(".")
                logmessage("Vari Components are " + str(components) + "\n")
                logmessage("Real Components are " + str(realComponents) + "\n")
                n = len(components)
                if n == 1:
                    logmessage("There is no question for " + missingVariable + "\n")
                    continue
                found_x = 0;
                for i in range(1, n):
                    if found_x:
                        break;
                    sub_totry = [{'var': "x." + ".".join(components[i:n]), 'realvar': "x." + ".".join(realComponents[i:n]), 'root': ".".join(realComponents[0:i]), 'root_for_object': ".".join(realComponents[0:i])}]
                    m = match_brackets_at_end.search(sub_totry[0]['root'])
                    if m:
                        before_brackets = m.group(1)
                        brackets_part = m.group(2)
                        sub_totry.insert(0, {'var': "x[i]." + ".".join(components[i:n]), 'realvar': "x" + brackets_part + "." + ".".join(realComponents[i:n]), 'root': before_brackets, 'root_for_object': before_brackets + brackets_part})
                    for d in sub_totry:
                        if found_x:
                            break;
                        var = d['var']
                        realVar = d['realvar']
                        mm = match_inside_brackets.findall(realVar)
                        if (mm):
                            if len(mm) > 1:
                                logmessage("Variable " + var + " is no good because it has more than one iterator\n")
                                continue;
                            the_i = mm[0];
                        root = d['root']
                        root_for_object = d['root_for_object']
                        logmessage("testing variable " + var + " and root " + root + " and root for object " + root_for_object + "\n")
                        try:
                            logmessage("Looking for " + root_for_object + "\n")
                            root_evaluated = eval(root_for_object, user_dict)
                            logmessage("Looking for type of root evaluated\n")
                            generic_object = type(root_evaluated).__name__
                            logmessage("ok -4\n")
                            logmessage("Generic object is " + generic_object + "\n")
                            if generic_object in self.generic_questions:
                                logmessage("ok1\n")
                                if var in self.questions:
                                    logmessage("ok2\n")
                                    if var in self.generic_questions[generic_object]:
                                        logmessage("ok3\n")
                            if generic_object in self.generic_questions and var in self.questions and var in self.generic_questions[generic_object]:
                                logmessage("Got a hit, setting var " + var + " and realMissingVariable " + realMissingVariable + "\n")
                                realMissingVariable = missingVariable
                                missingVariable = var
                                is_generic = True
                                the_x = root
                                found_x = 1
                                break
                            logmessage("I should be looping around now\n")
                        except:
                            logmessage("variable did not exist in user_dict: " + str(sys.exc_info()[0]) + "\n")
                if not (is_generic or is_iterator):
                    logmessage("There is no question for " + missingVariable + "\n")
                    continue
            while True:
                try:
                    for the_question in self.questions[missingVariable]:
                        question = the_question.follow_multiple_choice(user_dict)
                        if is_generic:
                            if question.is_generic:
                                if question.generic_object != generic_object:
                                    continue
                                logmessage("ok" + "\n")
                            else:
                                continue
                        if question.question_type == "code":
                            logmessage("Running some code:\n\n" + question.sourcecode + "\n")
                            exec(question.compute, user_dict)
                            #logmessage("the missing variable is " + str(missingVariable) + "\n")
                            if missingVariable in variable_stack:
                                variable_stack.remove(missingVariable)
                            try:
                                eval(missingVariable, user_dict)
                                return({'type': 'continue'})
                            except:
                                logmessage("Try another method of setting the variable" + "\n")
                                continue
                        else:
                            #logmessage("Question type is " + question.question_type + "\n")
                            #logmessage("Ask:\n  " + question.content.original_text + "\n")
                            return question.ask(user_dict, the_x, the_i)
                    raise DAError("Failed to set " + missingVariable)
                except NameError as errMess:
                    newMissingVariable = str(errMess).split("'")[1]
                    logmessage(str(errMess) + "\n")
                    question_result = self.askfor(newMissingVariable, user_dict, variable_stack=variable_stack)
                    if question_result['type'] == 'continue':
                        continue
                    return(question_result)
        raise DAError("Exiting")
        
class myextract(ast.NodeVisitor):
    def __init__(self):
        self.stack = []
    def visit_Name(self, node):
        self.stack.append(node.id)
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Attribute(self, node):
        self.stack.append(node.attr)
        ast.NodeVisitor.generic_visit(self, node)

class myvisitnode(ast.NodeVisitor):
    def __init__(self):
        self.names = {}
        self.targets = {}
        self.depth = 0;
    def generic_visit(self, node):
        #logmessage(' ' * self.depth + type(node).__name__ + "\n")
        self.depth += 1
        ast.NodeVisitor.generic_visit(self, node)
        self.depth -= 1
    def visit_Assign(self, node):
        for key, val in ast.iter_fields(node):
            if key == 'targets':
                for subnode in val:
                    crawler = myextract()
                    crawler.visit(subnode)
                    self.targets[".".join(reversed(crawler.stack))] = 1
        self.depth += 1
        ast.NodeVisitor.generic_visit(self, node)
        self.depth -= 1
    def visit_Name(self, node):
        self.names[node.id] = 1
        ast.NodeVisitor.generic_visit(self, node)

def find_fields_in(code, fields_used, names_used):
    myvisitor = myvisitnode()
    t = ast.parse(code)
    myvisitor.visit(t)
    predefines = set(globals().keys()) | set(locals().keys())
    for item in myvisitor.targets.keys():
        if item not in predefines:
            fields_used.add(item)
    definables = set(predefines) | set(myvisitor.targets.keys())
    for item in myvisitor.names.keys():
        if item not in definables:
            names_used.add(item)

def process_attachment(target):
    metadata = dict()
    if type(target) is dict:
        if 'filename' not in target:
            target['filename'] = word("Document")
        if 'name' not in target:
            target['name'] = word("Document")
        if 'valid_formats' in target:
            if type(target['valid_formats']) is str:
                target['valid_formats'] = [target['valid_formats']]
            elif type(target['valid_formats']) is not list:
                raise DAError('Unknown data type in attachment valid_formats')
        else:
            target['valid_formats'] = ['*']
        if 'metadata' in target:
            if type(target['metadata']) is not dict:
                raise DAError('Unknown data type in attachment metadata')
            for key in target['metadata']:
                data = target['metadata'][key]
                if data is list:
                    for sub_data in data:
                        if sub_data is not str:
                            raise DAError('Unknown data type in list in attachment metadata')
                    newdata = list(map((lambda x: TextObject(x)), data))
                    metadata[key] = newdata
                elif type(data) is str:
                    metadata[key] = TextObject(data)
                else:
                    raise DAError('Unknown data type ' + str(type(data)) + ' in key in attachment metadata')
        if 'content' not in target:
            raise DAError("No content provided in attachment")
        return({'name': TextObject(target['name']), 'filename': TextObject(target['filename']), 'content': TextObject(target['content']), 'valid_formats': target['valid_formats'], 'metadata': metadata})
    elif type(target) is str:
        return({'name': TextObject('Document'), 'filename': TextObject('document'), 'content': TextObject(target), 'valid_formats': ['*'], 'metadata': metadata})
    else:
        raise DAError("Unknown data type in process_attachment")

def process_attachment_list(target):
    if type(target) is list:
        return(list(map((lambda x: process_attachment(x)), target)))
    else:
        return([process_attachment(target)])
    
        
def make_attachment(attachment, user_dict, **kwargs):
    result = {'name': attachment['name'].text(user_dict, **kwargs), 'filename': attachment['filename'].text(user_dict, **kwargs), 'valid_formats': attachment['valid_formats']}
    result['markdown'] = dict();
    result['content'] = dict();
    result['file'] = dict();
    if '*' in attachment['valid_formats']:
        formats_to_use = ['html', 'rtf', 'pdf', 'tex']
    else:
        formats_to_use = attachment['valid_formats']
    for doc_format in formats_to_use:
        if doc_format in ['pdf', 'rtf', 'tex']:
            the_markdown = ""
            if len(attachment['metadata']) > 0:
                metadata = dict()
                for key in attachment['metadata']:
                    data = attachment['metadata'][key]
                    if type(data) is list:
                        metadata[key] = list(map((lambda x: x.text(user_dict, doc_format=doc_format, **kwargs)), data))
                    else:
                        metadata[key] = data.text(user_dict, doc_format=doc_format, **kwargs)
                the_markdown += "---\n" + yaml.dump(metadata) + "\n...\n"
            the_markdown += attachment['content'].text(user_dict, doc_format=doc_format, **kwargs)
            result['markdown'][doc_format] = the_markdown
            converter = Pandoc()
            converter.output_format = doc_format
            converter.input_content = the_markdown
            converter.convert()
            result['file'][doc_format] = converter.output_filename
            result['content'][doc_format] = result['markdown'][doc_format]
        elif doc_format in ['html']:
            result['markdown'][doc_format] = attachment['content'].text(user_dict, doc_format=doc_format, **kwargs)
            result['content'][doc_format] = docassemble.base.filter.markdown_to_html(result['markdown'][doc_format])
    return(result)
            
def process_selections(data):
    result = []
    if type(data) is list:
        for entry in data:
            if type(entry) is dict:
                for key in entry:
                    result.append([key, entry[key]])
            if type(entry) is list:
                result.append([entry[0], entry[1]])
            elif type(entry) is str or type(entry) is unicode:
                result.append([entry, entry])
    elif type(data) is dict:
        for key, value in sorted(data.items(), key=operator.itemgetter(1)):
            result.append([key, value])
    else:
        raise DAError("Unknown data type in choices selection")
    return(result)

def set_url_finder(func):
    docassemble.base.filter.set_url_finder(func)

def set_file_finder(func):
    docassemble.base.filter.set_file_finder(func)
