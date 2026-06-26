import decimal
import locale
from typing import Callable
import num2words
from docassemble.base.thread_context import this_thread
from .capitalization import capitalize
from .control import get_language
from .core import (
    language_function_constructor,
    ensure_definition,
    update_language_function,
)

ordinal_functions: dict[str, Callable] = {}

ordinal_numbers: dict[str, dict[str, str]] = {}

nice_numbers: dict[str, dict[str, str]] = {}

ordinal_number = language_function_constructor('ordinal_number')
ordinal = language_function_constructor('ordinal')
nice_number = language_function_constructor('nice_number')

if ordinal_number.__doc__ is None:
    ordinal_number.__doc__ = """Return the ordinal form of a cardinal number.

    Args:
        num: The cardinal number (1-based).
        **kwargs: Optional keyword arguments including ``capitalize``
            (bool) and ``use_word`` (bool, default depends on the value).

    Returns:
        str: The ordinal form (e.g. ``ordinal_number(8)`` returns
            ``'eighth'``; ``ordinal_number(8, use_word=False)`` returns
            ``'8th'``).
    """
if ordinal.__doc__ is None:
    ordinal.__doc__ = """Return the ordinal form of a zero-based index.

    Equivalent to ``ordinal_number(num + 1)``. This is useful when working
    with zero-based list indexes.

    Args:
        num: The zero-based index.
        **kwargs: Optional keyword arguments passed to :func:`ordinal_number`.

    Returns:
        str: The ordinal form (e.g. ``ordinal(0)`` returns ``'first'``;
            ``ordinal(22)`` returns ``'23rd'``).
    """

def string_to_number(number):
    try:
        float_number = float(number)
        int_number = int(number)
        if float_number == int_number:
            return int_number
        return float_number
    except:
        return number


def number_to_word(number, **kwargs):
    language = kwargs.get('language', None)
    capitalize_arg = kwargs.get('capitalize', False)
    function = kwargs.get('function', None)
    raise_on_error = kwargs.get('raise_on_error', False)
    if function not in ('ordinal', 'ordinal_num'):
        function = 'cardinal'
    if language is None:
        language = get_language()
    for lang, loc in (('en', 'en_GB'), ('en', 'en_IN'), ('es', 'es_CO'), ('es', 'es_VE'), ('fr', 'fr_CH'), ('fr', 'fr_BE'), ('fr', 'fr_DZ'), ('pt', 'pt_BR')):
        if language == lang and this_thread.locale.startswith(loc):
            language = loc
            break
    number = string_to_number(number)
    if raise_on_error:
        the_word = num2words.num2words(number, lang=language, to=function)
    else:
        try:
            the_word = num2words.num2words(number, lang=language, to=function)
        except NotImplementedError:
            the_word = str(number)
    if capitalize_arg:
        return capitalize(the_word)
    return the_word


def ordinal_default(the_number, **kwargs):
    """Returns the "first," "second," "third," etc. for a given number, which is expected to
    be an index starting with zero.  ordinal(0) returns "first."  For a more literal ordinal
    number function, see ordinal_number()."""
    result = ordinal_number(int(float(the_number)) + 1, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(result)
    return result


def nice_number_default(the_number, **kwargs):
    """Returns the number as a word in the current language."""
    capitalize_arg = kwargs.get('capitalize', False)
    language = kwargs.get('language', None)
    use_word = kwargs.get('use_word', None)
    ensure_definition(the_number, capitalize_arg, language)
    if language is None:
        language = this_thread.language
    if language in nice_numbers:
        language_to_use = language
    elif '*' in nice_numbers:
        language_to_use = '*'
    else:
        language_to_use = 'en'
    if isinstance(the_number, float):
        the_number = float(decimal.Context(prec=8).create_decimal_from_float(the_number))
    if int(float(the_number)) == float(the_number):
        the_number = int(float(the_number))
        is_integer = True
    else:
        is_integer = False
    if language_to_use in nice_numbers and str(the_number) in nice_numbers[language_to_use]:
        the_word = nice_numbers[language_to_use][str(the_number)]
        if capitalize_arg:
            return capitalize(the_word)
        return the_word
    if use_word or (is_integer and 0 <= the_number < 11 and use_word is not False):
        try:
            return number_to_word(the_number, **kwargs)
        except:
            pass
    if isinstance(the_number, int):
        return str(locale.format_string("%d", the_number, grouping=True))
    return str(locale.format_string("%.2f", float(the_number), grouping=True)).rstrip('0')


def ordinal_function_en(i, **kwargs):
    try:
        i = int(i)
    except:
        i = 0
    use_word = kwargs.get('use_word', None)
    if use_word is True:
        kwargs['function'] = 'ordinal'
    elif use_word is False:
        kwargs['function'] = 'ordinal_num'
    else:
        if i < 11:
            kwargs['function'] = 'ordinal'
        else:
            kwargs['function'] = 'ordinal_num'
    return number_to_word(i, **kwargs)


def ordinal_number_default(the_number, **kwargs):
    """Returns the "first," "second," "third," etc. for a given number.
    ordinal_number(1) returns "first."  For a function that can be used
    on index numbers that start with zero, see ordinal()."""
    num = str(the_number)
    if kwargs.get('use_word', True):
        if this_thread.language in ordinal_numbers and num in ordinal_numbers[this_thread.language]:
            return ordinal_numbers[this_thread.language][num]
        if '*' in ordinal_numbers and num in ordinal_numbers['*']:
            return ordinal_numbers['*'][num]
    if this_thread.language in ordinal_functions:
        language_to_use = this_thread.language
    elif '*' in ordinal_functions:
        language_to_use = '*'
    else:
        language_to_use = 'en'
    return ordinal_functions[language_to_use](the_number, **kwargs)


def update_nice_numbers(lang, defs):
    if lang not in nice_numbers:
        nice_numbers[lang] = {}
    for number, the_word in defs.items():
        nice_numbers[lang][str(number)] = the_word


def update_ordinal_numbers(lang, defs):
    if lang not in ordinal_numbers:
        ordinal_numbers[lang] = {}
    for number, the_word in defs.items():
        ordinal_numbers[lang][str(number)] = the_word


def update_ordinal_function(lang, func):
    ordinal_functions[lang] = func


def number_or_length(target):
    if isinstance(target, (int, float)):
        return target
    if isinstance(target, (list, dict, set, tuple)) or (hasattr(target, 'elements') and isinstance(target.elements, (list, dict, set))):
        return len(target)
    if target:
        return 2
    return 1


update_ordinal_function('en', ordinal_function_en)
update_ordinal_function('*', ordinal_function_en)
update_language_function('*', 'ordinal_number', ordinal_number_default)
update_language_function('*', 'ordinal', ordinal_default)
