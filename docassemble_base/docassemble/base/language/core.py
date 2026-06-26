from typing import Callable
from jinja2.runtime import Undefined
from docassemble.base.logger import logmessage
from docassemble.base.thread_context import this_thread

language_functions: dict[str, dict[str, Callable]] = {}

def update_language_function(lang, term, func):
    if term not in language_functions:
        language_functions[term] = {}
    language_functions[term][lang] = func


def ensure_definition(*pargs, **kwargs):
    for val in pargs:
        if isinstance(val, Undefined):
            str(val)
    for val in kwargs.values():
        if isinstance(val, Undefined):
            str(val)


def language_function_constructor(term):

    def func(*args, **kwargs):
        ensure_definition(*args, **kwargs)
        language = kwargs.get('language', None)
        if language is None:
            language = this_thread.language
        if language in language_functions[term]:
            return language_functions[term][language](*args, **kwargs)
        if '*' in language_functions[term]:
            return language_functions[term]['*'](*args, **kwargs)
        if 'en' in language_functions[term]:
            logmessage("Term " + str(term) + " is not defined for language " + str(language))
            return language_functions[term]['en'](*args, **kwargs)
        raise SystemError("term " + str(term) + " not defined in language_functions for English or *")
    return func
