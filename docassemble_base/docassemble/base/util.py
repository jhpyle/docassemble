# -*- coding: utf-8 -*-
import types
import en
import re
import os
import inspect
import mimetypes
import datetime
import locale
import pkg_resources
import titlecase
from docassemble.base.logger import logmessage
from docassemble.base.error import QuestionError
import babel.dates
import dateutil.parser
import locale
import json
import threading
import urllib
import codecs
import base64
import json
import ast
import astunparse
locale.setlocale(locale.LC_ALL, '')

__all__ = ['ordinal', 'ordinal_number', 'comma_list', 'word', 'get_language', 'set_language', 'get_dialect', 'get_locale', 'set_locale', 'comma_and_list', 'need', 'nice_number', 'currency_symbol', 'verb_past', 'verb_present', 'noun_plural', 'indefinite_article', 'capitalize', 'space_to_underscore', 'force_ask', 'period_list', 'name_suffix', 'currency', 'static_image', 'title_case', 'url_of', 'process_action', 'url_action', 'get_info', 'set_info', 'get_config', 'prevent_going_back', 'qr_code', 'action_menu_item', 'from_b64_json', 'defined', 'value', 'message', 'single_paragraph']

class lister(ast.NodeVisitor):
    def __init__(self):
        self.stack = []
    def visit_Name(self, node):
        self.stack.append(['name', node.id])
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Attribute(self, node):
        self.stack.append(['attr', node.attr])
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Subscript(self, node):
        self.stack.append(['index', re.sub(r'\n', '', astunparse.unparse(node.slice))])
        ast.NodeVisitor.generic_visit(self, node)

debug = False
default_dialect = 'us'
default_language = 'en'
default_locale = 'US.utf8'
daconfig = dict()
dot_split = re.compile(r'([^\.\[\]]+(?:\[.*?\])?)')
newlines = re.compile(r'[\r\n]+')

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
    """Used to retrieve the values of global variables set through set_info()."""
    if hasattr(this_thread, att):
        return getattr(this_thread, att)

def set_info(**kwargs):
    """Used to set the values of global variables you wish to retrieve through get_info()."""
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

def word(the_word, **kwargs):
    """Returns the word translated into the current language.  If a translation is not known,
    the input is returned."""
    # Currently, no kwargs are used, but in the future, this function could be
    # expanded to use kwargs.  For example, for languages with gendered words,
    # the gender could be passed as a keyword argument.
    if the_word is True:
        the_word = 'yes'
    elif the_word is False:
        the_word = 'no'
    elif the_word is None:
        the_word = "I don't know"
    try:
        return word_collection[this_thread.language][the_word].decode('utf-8')
    except:
        return unicode(the_word)

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
    """Returns a value from the docassemble configuration.  If not defined, returns None."""
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
    """Instructs docassemble to disable the user's back button, so that the user cannot
    go back and change any answers before this point in the interview."""
    this_thread.prevent_going_back = True
    return

def set_language(lang, dialect=None):
    """Sets the language to use for linguistic functions.
    E.g., set_language('es') to set the language to Spanish.
    Use the keyword argument "dialect" to set a dialect."""
    if dialect:
        this_thread.dialect = dialect
    elif lang != this_thread.language:
        this_thread.dialect = None
    this_thread.language = lang
    return

def get_language():
    """Returns the current language (e.g., "en")."""
    return this_thread.language

def get_dialect():
    """Returns the current dialect."""
    return this_thread.dialect

def set_default_locale(loc):
    global default_locale
    default_locale = loc
    return

def set_locale(loc):
    """Sets the current locale.  See also update_locale()."""
    this_thread.locale = loc
    return

def get_locale():
    """Returns the current locale setting."""
    return this_thread.locale

def update_locale():
    """Updates the system locale based on the value set by set_locale()."""
    #logmessage("Using " + str(language) + '_' + str(this_locale) + "\n")
    locale.setlocale(locale.LC_ALL, str(this_thread.language) + '_' + str(this_thread.locale))
    return

def comma_list_en(*pargs, **kargs):
    """Returns the arguments separated by commas.  If the first argument is a list, 
    that list is used.  Otherwise, the arguments are treated as individual items.
    See also comma_and_list()."""
    if 'comma_string' in kargs:
        comma_string = kargs['comma_string']
    else:
        comma_string = ", "
    if (len(pargs) == 0):
        return unicode('')
    elif (len(pargs) == 1):
        if type(pargs[0]) == list:
            pargs = pargs[0]
    if (len(pargs) == 0):
        return unicode('')
    elif (len(pargs) == 1):
        return(unicode(pargs[0]))
    else:
        return(comma_string.join(pargs))

def comma_and_list_en(*pargs, **kargs):
    """Returns an English-language listing of the arguments.  If the first argument is a list, 
    that list is used.  Otherwise, the arguments are treated as individual items in the list.
    Use the optional argument oxford=False if you do not want a comma before the "and."
    See also comma_list()."""
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
        return unicode('')
    elif (len(pargs) == 1):
        if type(pargs[0]) == list:
            pargs = pargs[0]
    if (len(pargs) == 0):
        return unicode('')
    elif (len(pargs) == 1):
        return(unicode(pargs[0]))
    elif (len(pargs) == 2):
        return(unicode(pargs[0]) + before_and + and_string + after_and + unicode(pargs[1]))
    else:
        return(comma_string.join(map(unicode, pargs[:-1])) + extracomma + before_and + and_string + after_and + unicode(pargs[-1]))

def need(*pargs):
    """Given one or more variables, this function instructs docassemble 
    to do what is necessary to define the variables."""
    for argument in pargs:
        argument
    return True

def pickleable_objects(input_dict):
    output_dict = dict()
    for key in input_dict:
        if type(input_dict[key]) in [types.ModuleType, types.FunctionType, types.TypeType, types.BuiltinFunctionType, types.BuiltinMethodType, types.MethodType, types.ClassType]:
            continue
        if key == "__builtins__":
            continue
        output_dict[key] = input_dict[key]
    return(output_dict)

def ordinal_number_default(i):
    """Returns the "first," "second," "third," etc. for a given number.
    ordinal_number(1) returns "first."  For a function that can be used
    on index numbers that start with zero, see ordinal()."""
    num = unicode(i)
    if this_thread.language in ordinal_numbers and num in ordinal_numbers[this_thread.language]:
        return ordinal_numbers[this_thread.language][num]
    if this_thread.language in ordinal_functions:
        return ordinal_functions[this_thread.language](i)
    else:
        return default_ordinal_function(i)

def ordinal_default(j):
    """Returns the "first," "second," "third," etc. for a given number, which is expected to
    be an index starting with zero.  ordinal(0) returns "first."  For a more literal ordinal 
    number function, see ordinal_number()."""
    return ordinal_number(int(j) + 1)

def nice_number_default(num):
    """Returns the number as a word in the current language."""
    if this_thread.language in nice_numbers and unicode(num) in nice_numbers[this_thread.language]:
        return nice_numbers[this_thread.language][unicode(num)]
    return unicode(num)

def capitalize_default(a):
    if a and (type(a) is str or type(a) is unicode) and len(a) > 1:
        return(a[0].upper() + a[1:])
    else:
        return(unicode(a))

def today_default(format='long'):
    return babel.dates.format_date(datetime.date.today(), format=format, locale=this_thread.language)

def currency_symbol_default():
    """Returns the currency symbol for the current locale."""
    return locale.localeconv()['currency_symbol'].decode('utf8')

def currency_default(value, decimals=True):
    """Returns the value as a currency, according to the conventions of the current locale.
    Use the optional keyword argument decimals=False if you do not want to see decimal places
    in the number."""
    obj_type = type(value).__name__
    if obj_type in ['FinancialList', 'PeriodicFinancialList']:
        value = value.total()
    elif obj_type in ['Value', 'PeriodicValue']:
        if value.exists:
            value = value.amount()
        else:
            value = 0
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
    'is_word': {
        'en': prefix_constructor('is ')
    },
    'their': {
        'en': prefix_constructor('their ')
    },
    'of_the': {
        'en': prefix_constructor('of the ')
    },
    'your': {
        'en': prefix_constructor('your ')
    },
    'its': {
        'en': prefix_constructor('its ')
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
        '*': today_default
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
        'en': comma_list_en
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
is_word = language_function_constructor('is_word')
their = language_function_constructor('their')
your = language_function_constructor('your')
its = language_function_constructor('its')
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

if verb_past.__doc__ is None:
    verb_past.__doc__ = """Given a verb, returns the past tense of the verb."""
if verb_present.__doc__ is None:
    verb_present.__doc__ = """Given a verb, returns the present tense of the verb."""
if noun_plural.__doc__ is None:
    noun_plural.__doc__ = """Given a noun, returns the plural version of the noun."""
if indefinite_article.__doc__ is None:
    indefinite_article.__doc__ = """Given a noun, returns the noun with an indefinite article attached
                                 (e.g., indefinite_article("fish") returns "a fish")."""
if capitalize.__doc__ is None:
    capitalize.__doc__ = """Capitalizes the first letter of the word or phrase."""
if period_list.__doc__ is None:
    period_list.__doc__ = """Returns an array of arrays where the first element of each array is a number, 
                          and the second element is a word expressing what that numbers means as a per-year
                          period.  This is meant to be used in code for a multiple-choice field."""
if name_suffix.__doc__ is None:
    name_suffix.__doc__ = """Returns an array of choices for the suffix of a name.
                          This is meant to be used in code for a multiple-choice field."""
if today.__doc__ is None:
    today.__doc__ = """Returns today's date in long form according to the current locale."""    
if period_list.__doc__ is None:
    period_list.__doc__ = """Returns a list of periods of a year, for inclusion in dropdown items."""
if name_suffix.__doc__ is None:
    name_suffix.__doc__ = """Returns a list of name suffixes, for inclusion in dropdown items."""
if currency.__doc__ is None:
    currency.__doc__ = """Formats the argument as a currency value, according to language and locale."""
if currency_symbol.__doc__ is None:
    currency_symbol.__doc__ = """Returns the symbol for currency, according to the locale."""
if possessify.__doc__ is None:
    possessify.__doc__ = """Given two arguments, a and b, returns "a's b." """
if possessify_long.__doc__ is None:
    possessify_long.__doc__ = """Given two arguments, a and b, returns "the b of a." """
if comma_list.__doc__ is None:
    comma_list.__doc__ = """Returns the arguments separated by commas."""
if comma_and_list.__doc__ is None:
    comma_and_list.__doc__ = """Returns the arguments separated by commas with "and" before the last one."""
if nice_number.__doc__ is None:
    nice_number.__doc__ = """Takes a number as an argument and returns the number as a word if ten or below."""
if capitalize.__doc__ is None:
    capitalize.__doc__ = """Returns the argument with the first letter capitalized."""
if title_case.__doc__ is None:
    title_case.__doc__ = """Returns the argument with the first letter of each word capitalized, as in a title."""
if ordinal_number.__doc__ is None:
    ordinal_number.__doc__ = """Given a number, returns "first" or "23rd" for 1 or 23, respectively."""
if ordinal.__doc__ is None:
    ordinal.__doc__ = """Given a number that is expected to be an index, returns "first" or "23rd" for 0 or 22, respectively."""
if url_of.__doc__ is None:
    url_of.__doc__ = """Returns a URL to a file within a docassemble package."""

def month_of(the_date, as_word=False):
    """Interprets the_date as a date and returns the month.  
    Set as_word to True if you want the month as a word."""
    try:
        date = dateutil.parser.parse(the_date)
        if as_word:
            return(date.strftime('%B'))
        return(date.strftime('%m'))
    except:
        return word("Bad date")

def day_of(the_date):
    """Interprets the_date as a date and returns the day of month."""
    try:
        date = dateutil.parser.parse(the_date)
        return(date.strftime('%d'))
    except:
        return word("Bad date")

def year_of(the_date):
    """Interprets the_date as a date and returns the year."""
    try:
        date = dateutil.parser.parse(the_date)
        return(date.strftime('%Y'))
    except:
        return word("Bad date")

def format_date(the_date, format='long'):
    """Interprets the_date as a date and returns the date formatted in long form."""
    try:
        return(babel.dates.format_date(dateutil.parser.parse(the_date), format=format, locale=get_language()))
    except:
        return word("Bad date")

def underscore_to_space(a):
    return(re.sub('_', ' ', unicode(a)))

def space_to_underscore(a):
    """Converts spaces in the input to underscores in the output.  Useful for making filenames without spaces."""
    return(re.sub(' +', '_', unicode(a).encode('ascii', errors='ignore')))

def message(*pargs, **kwargs):
    """Presents a screen to the user with the given message"""
    raise QuestionError(*pargs, **kwargs)
    
def force_ask(variable_name):
    """Given a variable, instructs docassemble to do what is necessary to define the variable,
    even if the variable has already been defined."""
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
    """Inserts appropriate markup to include a static image.  If you know
    the image path, you can just use the "[FILE ...]" markup.  This function is
    useful when you want to assemble the image path programmatically.
    Takes an optional keyword argument "width"
    (e.g., static_image('docassemble.demo:crawling.png', width='2in'))."""
    filename = static_filename(filereference)
    if filename is None:
        return('ERROR: invalid image reference')
    width = kwargs.get('width', None)
    if width is None:
        return('[FILE ' + filename + ']')
    else:
        return('[FILE ' + filename + ', ' + width + ']')

def qr_code(string, **kwargs):
    """Inserts appropriate markup to include a QR code image.  If you know
    the string you want to encode, you can just use the "[QR ...]" markup.  
    This function is useful when you want to assemble the string programmatically.
    Takes an optional keyword argument "width"
    (e.g., qr_code('http://google.com', width='2in'))."""
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
        m = re.search(r'^docassemble.playground([0-9]+)$', parts[0])
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
        m = re.search(r'^docassemble.playground([0-9]+)$', parts[0])
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
            parts[1] = 'data/questions/' + parts[1]
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
    """If an action is waiting to be processed, it processes the action."""
    if 'action' not in current_info:
        return
    the_action = current_info['action']
    del current_info['action']
    force_ask(the_action)

def url_action(action, **kwargs):
    """Returns a URL to run an action in the interview."""
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
    """Takes two arguments: a label and an action.
    The label is what the user will see and the action is the action that will be
    performed when the user clicks on the item in the menu.  This is only used 
    when setting the special variable menu_items.
    E.g., menu_items = [ action_menu_item('Ask for my favorite food', 'favorite_food') ]"""
    return dict(label=label, url=url_action(action))

def from_b64_json(string):
    """Converts the string from base-64, then parses the string as JSON, and returns the object.
    This is an advanced function that is used by software developers to integrate other systems 
    with docassemble."""
    if string is None:
        return None
    return json.loads(base64.b64decode(string))

def components_of(full_variable):
    node = ast.parse(full_variable, mode='eval')
    crawler = lister()
    crawler.visit(node)
    return list(reversed(crawler.stack))

def defined(var):
    """Returns true if the variable has already been defined.  Otherwise, returns false."""
    if type(var) not in [str, unicode]:
        raise Exception("defined() must be given a string")
    frame = inspect.stack()[1][0]
    components = components_of(var)
    variable = components[0][1]
    the_user_dict = frame.f_locals
    while variable not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            return False
        if 'user_dict' in frame.f_locals:
            the_user_dict = eval('user_dict', frame.f_locals)
            if variable in the_user_dict:
                break
            else:
                return False
        else:
            the_user_dict = frame.f_locals
    if variable not in the_user_dict:
        return False
    if len(components) == 1:
        return True
    cum_variable = ''
    for elem in components:
        if elem[0] == 'name':
            cum_variable += elem[1]
            continue
        elif elem[0] == 'attr':
            to_eval = "hasattr(" + cum_variable + ", " + repr(elem[1]) + ")"
            cum_variable += '.' + elem[1]
        elif elem[0] == 'index':
            try:
                the_index = eval(elem[1], the_user_dict)
            except:
                return False
            if type(the_index) == int:
                to_eval = 'len(' + cum_variable + ') > ' + str(the_index)
            else:
                to_eval = elem[1] + " in " + cum_variable
            cum_variable += '[' + elem[1] + ']'
        try:
            result = eval(to_eval, the_user_dict)
        except:
            return False
        if result:
            continue
        return False
    return True

def value(var):
    """Returns the value of the variable given by the string 'var'."""
    if type(var) not in [str, unicode]:
        raise Exception("value() must be given a string")
    frame = inspect.stack()[1][0]
    components = components_of(var)
    variable = components[0][1]
    the_user_dict = frame.f_locals
    while variable not in the_user_dict:
        frame = frame.f_back
        if frame is None:
            force_ask(var)
        if 'user_dict' in frame.f_locals:
            the_user_dict = eval('user_dict', frame.f_locals)
            if variable in the_user_dict:
                break
            else:
                force_ask(var)
        else:
            the_user_dict = frame.f_locals
    if variable not in the_user_dict:
        force_ask(var)
    if len(components) == 1:
        return eval(variable, the_user_dict)
    cum_variable = ''
    for elem in components:
        if elem[0] == 'name':
            cum_variable += elem[1]
            continue
        elif elem[0] == 'attr':
            to_eval = "hasattr(" + cum_variable + ", " + repr(elem[1]) + ")"
            cum_variable += '.' + elem[1]
        elif elem[0] == 'index':
            try:
                the_index = eval(elem[1], the_user_dict)
            except:
                force_ask(var)
            if type(the_index) == int:
                to_eval = 'len(' + cum_variable + ') > ' + str(the_index)
            else:
                to_eval = elem[1] + " in " + cum_variable
            cum_variable += '[' + elem[1] + ']'
        try:
            result = eval(to_eval, the_user_dict)
        except:
            force_ask(var)
        if result:
            continue
        force_ask(var)
    return eval(cum_variable, the_user_dict)

# def _undefine(*pargs):
#     logmessage("called _undefine")
#     for var in pargs:
#         _undefine(var)

# def undefine(var):
#     """Makes the given variable undefined."""
#     logmessage("called undefine")
#     if type(var) not in [str, unicode]:
#         raise Exception("undefine() must be given one or more strings")
#     components = components_of(var)
#     variable = components[0][1]
#     frame = inspect.stack()[1][0]
#     the_user_dict = frame.f_locals
#     while variable not in the_user_dict:
#         frame = frame.f_back
#         if frame is None:
#             return
#         if 'user_dict' in frame.f_locals:
#             the_user_dict = eval('user_dict', frame.f_locals)
#             if variable in the_user_dict:
#                 break
#             else:
#                 return
#         else:
#             the_user_dict = frame.f_locals
#     try:
#         exec("del " + var, the_user_dict)
#     except:
#         logmessage("Failed to delete " + var)
#         pass
#     return

def single_paragraph(text):
    """Reduces the text to a single paragraph.  Useful when using Markdown 
    to indent user-supplied text."""
    return newlines.sub(' ', text)
