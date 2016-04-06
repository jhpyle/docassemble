# -*- coding: utf-8 -*-
import types
import en
import re
import os
import mimetypes
import datetime
import locale
import pkg_resources
import titlecase
from docassemble.base.logger import logmessage
import babel.dates
import locale
import json
import threading
import urllib
import codecs
import base64
import json
locale.setlocale(locale.LC_ALL, '')

__all__ = ['ordinal', 'ordinal_number', 'comma_list', 'word', 'get_language', 'set_language', 'get_dialect', 'get_locale', 'set_locale', 'comma_and_list', 'need', 'nice_number', 'currency_symbol', 'verb_past', 'verb_present', 'noun_plural', 'indefinite_article', 'capitalize', 'space_to_underscore', 'force_ask', 'period_list', 'name_suffix', 'currency', 'static_image', 'title_case', 'url_of', 'process_action', 'url_action', 'get_info', 'set_info', 'get_config', 'prevent_going_back', 'qr_code', 'action_menu_item', 'from_b64_json']

debug = False
default_dialect = 'us'
default_language = 'en'
default_locale = 'US.utf8'
daconfig = dict()

class ThreadVariables(threading.local):
    language = default_language
    dialect = default_dialect
    locale = default_locale
    initialized = False
    def __init__(self, **kw):
        if self.initialized:
            raise SystemError('__init__ called too many times')
        self.initialized = True
        self.__dict__.update(kw)

this_thread = ThreadVariables()

def get_info(att):
    if hasattr(this_thread, att):
        return getattr(this_thread, att)

def set_info(**kwargs):
    for att, value in kwargs.iteritems():
        setattr(this_thread, att, value)
    
word_collection = {
    'es': {
        'Continue': 'Continuar',
        'Help': 'Ayuda',
        'Sign in': 'Registrarse',
        'Question': 'Interrogación',
        'save_as_multiple': 'The document is available in the following formats:',
        'save_as_singular': 'The document is available in the following format:',
        'pdf_message': 'for printing; requires Adobe Reader or similar application',
        'rtf_message': 'for editing; requires Microsoft Word, Wordpad, or similar application',
        'docx_message': 'for editing; requires Microsoft Word or compatible application',
        'tex_message': 'for debugging PDF output',
        'attachment_message_plural': 'The following documents have been created for you.',
        'attachment_message_singular': 'The following document has been created for you.'
        },
    'en': {
        'and': "and",
        'or': "or",
        'yes': "yes",
        'no': "no",
        'Document': "Document",
        'content': 'content',
        'Open as:': 'Open this document as:',
        'Open as:': 'Save this documents as:',
        'Question': 'Question',
        'Help': 'Help',
        'Download': 'Download',
        'Preview': 'Preview',
        'Markdown': 'Markdown',
        'Source': 'Source',
        'attachment_message_plural': 'The following documents have been created for you.',
        'attachment_message_singular': 'The following document has been created for you.',
        'save_as_multiple': 'The document is available in the following formats:',
        'save_as_singular': 'The document is available in the following format:',
        'pdf_message': 'for printing; requires Adobe Reader or similar application',
        'rtf_message': 'for editing; requires Microsoft Word, Wordpad, or similar application',
        'docx_message': 'for editing; requires Microsoft Word or compatible application',
        'tex_message': 'for debugging PDF output',
        'vs.': 'vs.',
        'v.': 'v.',
        'Case No.': 'Case No.',
        'In the': 'In the',
        'This field is required.': 'You need to fill this in.',
        "You need to enter a valid date.": "You need to enter a valid date.",
        "You need to enter a complete e-mail address.": "You need to enter a complete e-mail address.",
        "You need to enter a number.": "You need to enter a number.",
        "You need to select one.": "You need to select one.",
        "Country Code": 'Country Code (e.g., "us")',
        "First Subdivision": "State Abbreviation (e.g., 'NY')",
        "Second Subdivision": "County",
        "Third Subdivision": "Municipality",
        "Organization": "Organization",
    }
}

ordinal_numbers = {
    'en': {
        '0': 'zeroeth',
        '1': 'first',
        '2': 'second',
        '3': 'third',
        '4': 'fourth',
        '5': 'fifth',
        '6': 'sixth',
        '7': 'seventh',
        '8': 'eighth',
        '9': 'ninth',
        '10': 'tenth'
    }
}

nice_numbers = {
    'en': {
        '0': 'zero',
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four',
        '5': 'five',
        '6': 'six',
        '7': 'seven',
        '8': 'eight',
        '9': 'nine',
        '10': 'ten'
    }
}

def basic_url_of(text):
    return text

url_of = basic_url_of

def set_url_finder(func):
    global url_of
    url_of = func
    return

def default_ordinal_function(i):
    return unicode(i)

def ordinal_function_en(i):
    num = unicode(i)
    if 10 <= i % 100 <= 20:
        return num + 'th'
    elif i % 10 == 3:
        return num + 'rd'
    elif i % 10 == 1:
        return num + 'st'
    elif i % 10 == 2:
        return num + 'nd'
    else:
        return num + 'th'

ordinal_functions = {
    'en': ordinal_function_en
}

def words():
    return word_collection[this_thread.language]

def word(theword):
    try:
        return word_collection[this_thread.language][theword].decode('utf-8')
    except:
        return unicode(theword)

def update_language_function(lang, term, func):
    if term not in language_functions:
        language_functions[term] = dict()
    language_functions[term][lang] = func
    return

def update_nice_numbers(lang, defs):
    if lang not in nice_numbers:
        nice_numbers[lang] = dict()
    for number, word in defs.iteritems():
        nice_numbers[lang][unicode(number)] = word
    return

def update_ordinal_numbers(lang, defs):
    if lang not in ordinal_numbers:
        ordinal_numbers[lang] = dict()
    for number, word in defs.iteritems():
        ordinal_numbers[lang][unicode(number)] = word
    return

def update_ordinal_function(lang, func):
    ordinal_functions[lang] = func
    return

def update_word_collection(lang, defs):
    if lang not in word_collection:
        word_collection[lang] = dict()
    for word, translation in defs.iteritems():
        word_collection[lang][word] = translation
    return

def set_da_config(config):
    global daconfig
    daconfig = config

def get_config(key):
    return daconfig.get(key, None)
    
def set_default_language(lang):
    global default_language
    default_language = lang
    return

def set_default_dialect(dialect):
    global default_dialect
    default_dialect = dialect
    return

def reset_local_variables():
    this_thread.language = default_language
    this_thread.locale = default_locale
    this_thread.prevent_going_back = False
    return

def prevent_going_back():
    this_thread.prevent_going_back = True
    return

def set_language(lang, dialect=None):
    if dialect:
        this_thread.dialect = dialect
    elif lang != this_thread.language:
        this_thread.dialect = None
    this_thread.language = lang
    return

def get_language():
    return this_thread.language

def get_dialect():
    return this_thread.dialect

def set_default_locale(loc):
    global default_locale
    default_locale = loc
    return

def set_locale(loc):
    this_thread.locale = loc
    return

def get_locale():
    return this_thread.locale

def update_locale():
    #logmessage("Using " + str(language) + '_' + str(this_locale) + "\n")
    locale.setlocale(locale.LC_ALL, str(this_thread.language) + '_' + str(this_thread.locale))
    return

def comma_and_list_en(*pargs, **kargs):
    if 'oxford' in kargs and kargs['oxford'] == False:
        extracomma = ""
    else:
        extracomma = ","
    if 'and_string' in kargs:
        and_string = kargs['and_string']
    else:
        and_string = word('and')
    if 'comma_string' in kargs:
        comma_string = kargs['comma_string']
    else:
        comma_string = ", "
    if 'before_and' in kargs:
        before_and = kargs['before_and']
    else:
        before_and = " "
    if 'after_and' in kargs:
        after_and = kargs['after_and']
    else:
        after_and = " "
    if (len(pargs) == 0):
        return
    elif (len(pargs) == 1):
        if type(pargs[0]) == list:
            pargs = pargs[0]
    if (len(pargs) == 0):
        return
    elif (len(pargs) == 1):
        return(unicode(pargs[0]))
    elif (len(pargs) == 2):
        return(unicode(pargs[0]) + before_and + and_string + after_and + unicode(pargs[1]))
    else:
        return(comma_string.join(map(unicode, pargs[:-1])) + extracomma + before_and + and_string + after_and + unicode(pargs[-1]))

def need(*pargs):
    for argument in pargs:
        argument
    return True

def pickleable_objects(input_dict):
    output_dict = dict()
    for key in input_dict:
        if type(input_dict[key]) in [types.ModuleType, types.FunctionType, types.TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType]:
            continue
        if key == "__builtins__":
            continue
        output_dict[key] = input_dict[key]
    return(output_dict)

def ordinal_number_default(i):
    num = unicode(i)
    if this_thread.language in ordinal_numbers and num in ordinal_numbers[this_thread.language]:
        return ordinal_numbers[this_thread.language][num]
    if this_thread.language in ordinal_functions:
        return ordinal_functions[this_thread.language](i)
    else:
        return default_ordinal_function(i)

def ordinal_default(j):
    return ordinal_number(int(j) + 1)

def nice_number_default(num):
    if this_thread.language in nice_numbers and unicode(num) in nice_numbers[this_thread.language]:
        return nice_numbers[this_thread.language][unicode(num)]
    return unicode(num)

def capitalize_default(a):
    if a and (type(a) is str or type(a) is unicode) and len(a) > 1:
        return(a[0].upper() + a[1:])
    else:
        return(unicode(a))

def currency_symbol_default():
    return locale.localeconv()['currency_symbol'].decode('utf8')

def currency_default(value, decimals=True):
    if decimals:
        return locale.currency(value, symbol=True, grouping=True).decode('utf8')
    else:
        return currency_symbol() + locale.format("%d", value, grouping=True)

def prefix_constructor(prefix):
    def func(word, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(prefix)) + unicode(word)
        else:
            return unicode(prefix) + unicode(word)
    return func

def double_prefix_constructor_reverse(prefix_one, prefix_two):
    def func(word_one, word_two, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(prefix_one)) + unicode(word_two) + unicode(prefix_two) + unicode(word_one)
        else:
            return unicode(prefix_one) + unicode(word_two) + unicode(prefix_two) + unicode(word_one)
    return func

def prefix_constructor_two_arguments(prefix, **kwargs):
    def func(word_one, word_two, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(prefix)) + unicode(word_one) + ' ' + unicode(word_two)
        else:
            return unicode(prefix) + unicode(word_one) + ' ' + unicode(word_two)
    return func

def middle_constructor(middle, **kwargs):
    def func(a, b, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(unicode(a)) + unicode(middle) + unicode(b)
        else:
            return unicode(a) + unicode(middle) + unicode(b)
    return func

def a_preposition_b_default(a, b, **kwargs):
    logmessage("Got here")
    if hasattr(a, 'preposition'):
        logmessage("Has preposition")
        preposition = a.preposition
    else:
        preposition = word('in the')
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(unicode(a)) + unicode(' ' + preposition + ' ') + unicode(b)
    else:
        return unicode(a) + unicode(' ' + preposition + ' ') + unicode(b)

language_functions = {
    'in_the': {
        'en': prefix_constructor('in the ')
    },
    'a_preposition_b': {
        'en': a_preposition_b_default
    },
    'a_in_the_b': {
        'en': middle_constructor(' in the ')
    },
    'her': {
        'en': prefix_constructor('her ')
    },
    'his': {
        'en': prefix_constructor('his ')
    },
    'of_the': {
        'en': prefix_constructor('of the ')
    },
    'your': {
        'en': prefix_constructor('your ')
    },
    'the': {
        'en': prefix_constructor('the ')
    },
    'does_a_b': {
        'en': prefix_constructor_two_arguments('does ')
    },
    'do_you': {
        'en': prefix_constructor('do you ')
    },
    'verb_past': {
        'en': lambda x, **kwargs: en.verb.past(x, **kwargs)
    },
    'verb_present': {
        'en': lambda x, **kwargs: en.verb.present(x, **kwargs)
    },
    'noun_plural': {
        'en': lambda x, **kwargs: en.noun.plural(x, **kwargs)
    },
    'indefinite_article': {
        'en': lambda x, **kwargs: en.noun.article(x, **kwargs)
    },
    'currency_symbol': {
        '*': currency_symbol_default
    },
    'today': {
        '*': lambda: babel.dates.format_date(datetime.date.today(), format='long', locale=this_thread.language)
    },
    'period_list': {
        '*': lambda: [[12, word("Per Month")], [1, word("Per Year")], [52, word("Per Week")], [24, word("Twice Per Month")], [26, word("Every Two Weeks")]]
    },
    'name_suffix': {
        '*': lambda: ['Jr', 'Sr', 'II', 'III', 'IV', 'V', 'VI']
    },
    'currency': {
        '*': currency_default
    },
    'possessify': {
        'en': middle_constructor("'s ")
    },
    'possessify_long': {
        'en': double_prefix_constructor_reverse('the ', ' of the ')
    },
    'comma_and_list': {
        'en': comma_and_list_en
    },
    'comma_list': {
        'en': lambda *argv: ", ".join(map(str, argv))
    },
    'nice_number': {
        '*': nice_number_default
    },
    'ordinal_number': {
        '*': ordinal_number_default
    },
    'ordinal': {
        '*': ordinal_default
    },
    'capitalize': {
        '*': capitalize_default
    },
    'title_case': {
        '*': titlecase.titlecase
    }
}

def language_function_constructor(term):
    if term not in language_functions:
        raise SystemError("term " + str(term) + " not in language_functions")
    def func(*args, **kwargs):
        if this_thread.language in language_functions[term]:
            return language_functions[term][this_thread.language](*args, **kwargs)
        if '*' in language_functions[term]:
            return language_functions[term]['*'](*args, **kwargs)
        if 'en' in language_functions[term]:
            logmessage("Term " + str(term) + " is not defined for language " + str(this_thread.language))
            return language_functions[term]['en'](*args, **kwargs)
        raise SystemError("term " + str(term) + " not defined in language_functions for English or *")
    return func
    
in_the = language_function_constructor('in_the')
a_preposition_b = language_function_constructor('a_preposition_b')
a_in_the_b = language_function_constructor('a_in_the_b')
her = language_function_constructor('her')
his = language_function_constructor('his')
your  = language_function_constructor('your')
of_the = language_function_constructor('of_the')
the = language_function_constructor('the')
do_you = language_function_constructor('do_you')
does_a_b = language_function_constructor('does_a_b')
verb_past = language_function_constructor('verb_past')
verb_present = language_function_constructor('verb_present')
noun_plural = language_function_constructor('noun_plural')
indefinite_article = language_function_constructor('indefinite_article')
today = language_function_constructor('today')
period_list = language_function_constructor('period_list')
name_suffix = language_function_constructor('name_suffix')
currency = language_function_constructor('currency')
currency_symbol = language_function_constructor('currency_symbol')
possessify = language_function_constructor('possessify')
possessify_long = language_function_constructor('possessify_long')
comma_list = language_function_constructor('comma_list')
comma_and_list = language_function_constructor('comma_and_list')
nice_number = language_function_constructor('nice_number')
capitalize = language_function_constructor('capitalize')
title_case = language_function_constructor('title_case')
ordinal_number = language_function_constructor('ordinal_number')
ordinal = language_function_constructor('ordinal')

def underscore_to_space(a):
    return(re.sub('_', ' ', unicode(a)))

def space_to_underscore(a):
    return(re.sub(' +', '_', unicode(a).encode('ascii', errors='ignore')))

def remove(variable_name):
    logmessage("Calling remove in util")
    try:
        exec('del ' + variable_name)
    except:
        pass

def force_ask(variable_name):
    raise NameError("name '" + variable_name + "' is not defined")

def static_filename_path(filereference):
    result = package_data_filename(static_filename(filereference))
    #if result is None or not os.path.isfile(result):
    #    result = absolute_filename("/playgroundstatic/" + re.sub(r'[^A-Za-z0-9\-\_\.]', '', filereference)).path
    return(result)

def static_filename(filereference):
    if re.search(r',', filereference):
        return(None)
    #filereference = re.sub(r'^None:data/static/', '', filereference)
    #filereference = re.sub(r'^None:', '', filereference)
    parts = filereference.split(':')
    if len(parts) < 2:
        parts = ['docassemble.base', filereference]
    if re.search(r'\.\./', parts[1]):
        return(None)
    if not re.match(r'(data|static)/.*', parts[1]):
        parts[1] = 'data/static/' + parts[1]
    return(parts[0] + ':' + parts[1])

def static_image(filereference, **kwargs):
    filename = static_filename(filereference)
    if filename is None:
        return('ERROR: invalid image reference')
    width = kwargs.get('width', None)
    if width is None:
        return('[FILE ' + filename + ']')
    else:
        return('[FILE ' + filename + ', ' + width + ']')

def qr_code(string, **kwargs):
    width = kwargs.get('width', None)
    if width is None:
        return('[QR ' + string + ']')
    else:
        return('[QR ' + string + ', ' + width + ']')

def standard_template_filename(the_file):
    try:
        return(pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.base'), "docassemble/base/data/templates/" + str(the_file)))
    except:
        #logmessage("Error retrieving data file\n")
        return(None)

def package_template_filename(the_file, **kwargs):
    parts = the_file.split(":")
    if len(parts) == 1:
        package = kwargs.get('package', None)
        #logmessage("my package is " + str(package))
        if package is not None:
            parts = [package, the_file]
            #logmessage("my package is " + str(package))
        #else:
            #parts = ['docassemble.base', the_file]
            #logmessage("my package is docassemble.base and the_file is " + str(the_file))
        #else:
        #    retval = absolute_filename('/playgroundtemplate/' + the_file).path
        #    logmessage("package_template_filename: retval is " + str(retval))
        #    return(retval)
    if len(parts) == 2:
        m = re.search(r'^playground\.([0-9]+)$', parts[0])
        if m:
            parts[1] = re.sub(r'^data/templates/', '', parts[1])
            return(absolute_filename("/playgroundtemplate/" + m.group(1) + '/' + re.sub(r'[^A-Za-z0-9\-\_\.]', '', parts[1])).path)
        if not re.match(r'data/.*', parts[1]):
            parts[1] = 'data/templates/' + parts[1]
        try:
            #logmessage("Trying with " + str(parts[0]) + " and " + str(parts[1]))
            return(pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1]))
        except:
            return(None)
    return(None)

def standard_question_filename(the_file):
    return(pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.base'), "docassemble/base/data/questions/" + str(the_file)))
    return(None)

def package_data_filename(the_file):
    #logmessage("package_data_filename with: " + str(the_file))
    if the_file is None:
        return(None)
    #the_file = re.sub(r'^None:data/static/', '', the_file)
    #the_file = re.sub(r'^None:', '', the_file)
    parts = the_file.split(":")
    result = None
    #if len(parts) == 1:
    #    parts = ['docassemble.base', the_file]
    if len(parts) == 2:
        m = re.search(r'^playground\.([0-9]+)$', parts[0])
        if m:
            parts[1] = re.sub(r'^data/static/', '', parts[1])
            return(absolute_filename("/playgroundstatic/" + m.group(1) + '/' + re.sub(r'[^A-Za-z0-9\-\_\.]', '', parts[1])).path)
        try:
            result = pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1])
        except:
            result = None
    #if result is None or not os.path.isfile(result):
    #    result = absolute_filename("/playgroundstatic/" + re.sub(r'[^A-Za-z0-9\-\_\.]', '', the_file)).path
    return(result)

def package_question_filename(the_file):
    parts = the_file.split(":")
    #if len(parts) == 1:
    #    parts = ['docassemble.base', the_file]
    if len(parts) == 2:
        if not re.match(r'data/.*', parts[1]):
            parts[1] = 'data/question/' + parts[1]
        try:
            return(pkg_resources.resource_filename(pkg_resources.Requirement.parse(parts[0]), re.sub(r'\.', r'/', parts[0]) + '/' + parts[1]))
        except:
            return(None)
    return(None)

def default_absolute_filename(the_file):
    return the_file

absolute_filename = default_absolute_filename

def set_absolute_filename(func):
    #logmessage("Running set_absolute_filename in util")
    global absolute_filename
    absolute_filename = func
    return

def nodoublequote(text):
    return re.sub(r'"', '', unicode(text))

def process_action(current_info):
    if 'action' not in current_info:
        return
    the_action = current_info['action']
    del current_info['action']
    force_ask(the_action)

def url_action(action, **kwargs):
    return '?action=' + urllib.quote(myb64quote(json.dumps({'action': action, 'arguments': kwargs})))

def myb64quote(text):
    return codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '')

def set_debug_status(new_value):
    global debug
    debug = new_value

def debug_status():
    return debug
# grep -E -R -o -h "word\(['\"][^\)]+\)" * | sed "s/^[^'\"]+['\"]//g"

def action_menu_item(label, action):
    return dict(label=label, url=url_action(action))

def from_b64_json(string):
    if string is None:
        return None
    return json.loads(base64.b64decode(string))
