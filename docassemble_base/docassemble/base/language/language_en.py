from collections.abc import Iterable
from docassemble.base.pattern import pattern_en
from docassemble.base.thread_context import this_thread
from docassemble.base.language.utils import fix_punctuation
from .core import ensure_definition
from .capitalization import capitalize
from .numbers import number_or_length
from .words import word

def noun_plural_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_en(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_en.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_en.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_en.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output

def verb_present_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    output = pattern_en.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_en(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    output = pattern_en.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def possessify_en(a, b, **kwargs):
    ensure_definition(a, b, **kwargs)
    if this_thread.evaluation_context == 'docx':
        apostrophe = "’"
    else:
        apostrophe = "'"
    if 'plural' in kwargs and kwargs['plural']:
        middle = apostrophe + " "
    else:
        middle = apostrophe + "s "
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(str(a)) + str(middle) + str(b)
    return str(a) + str(middle) + str(b)


def comma_list_en(*pargs, **kwargs):
    """Returns the arguments separated by commas.  If the first argument is a list,
    that list is used.  Otherwise, the arguments are treated as individual items.
    See also comma_and_list()."""
    ensure_definition(*pargs, **kwargs)
    comma_string = kwargs.get('comma_string', ', ')
    the_list = []
    for parg in pargs:
        if isinstance(parg, str):
            the_list.append(parg)
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            for sub_parg in parg:
                the_list.append(str(sub_parg))
        else:
            the_list.append(str(parg))
    return comma_string.join(the_list)


def comma_and_list_en(*pargs, **kwargs):
    """Returns an English-language listing of the arguments.  If the first argument is a list,
    that list is used.  Otherwise, the arguments are treated as individual items in the list.
    Use the optional argument oxford=False if you do not want a comma before the "and."
    See also comma_list()."""
    ensure_definition(*pargs, **kwargs)
    and_string = kwargs.get('and_string', word('and'))
    comma_string = kwargs.get('comma_string', ', ')
    if 'oxford' in kwargs and kwargs['oxford'] is False:
        extracomma = ""
    else:
        extracomma = comma_string.strip()
    before_and = kwargs.get('before_and', ' ')
    after_and = kwargs.get('after_and', ' ')
    the_list = []
    for parg in pargs:
        if isinstance(parg, str):
            the_list.append(parg)
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            for sub_parg in parg:
                the_list.append(str(sub_parg))
        else:
            the_list.append(str(parg))
    if len(the_list) == 0:
        return str('')
    if len(the_list) == 1:
        return the_list[0]
    if len(the_list) == 2:
        return the_list[0] + before_and + and_string + after_and + the_list[1]
    return comma_string.join(the_list[:-1]) + extracomma + before_and + and_string + after_and + the_list[-1]


def add_separators_en(*pargs, **kwargs):
    """Accepts a list and returns a list, with semicolons after each item,
    except "and" after the penultimate item and a period after the
    last.

    """
    ensure_definition(*pargs, **kwargs)
    separator = kwargs.get('separator', ';')
    last_separator = kwargs.get('last_separator', '; ' + word("and"))
    end_mark = kwargs.get('end_mark', '.')
    the_list = []
    for parg in pargs:
        if isinstance(parg, str):
            the_list.append(parg.rstrip())
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')) or isinstance(parg, Iterable):
            for sub_parg in parg:
                the_list.append(str(sub_parg).rstrip())
        else:
            the_list.append(str(parg).rstrip())
    if len(the_list) == 0:
        return the_list
    if len(the_list) == 1:
        return [fix_punctuation(the_list[0], mark=end_mark)]
    for indexno in range(len(the_list) - 2):  # for 4: 0, 1; for 3: 0; for 2: []
        the_list[indexno] = the_list[indexno].rstrip(',')
        the_list[indexno] = fix_punctuation(the_list[indexno], mark=separator)
    if not the_list[-2].endswith(last_separator):
        the_list[-2] = the_list[-2].rstrip(last_separator[0])
        the_list[-2] += last_separator
    the_list[-1] = fix_punctuation(the_list[-1], mark=end_mark)
    return the_list
