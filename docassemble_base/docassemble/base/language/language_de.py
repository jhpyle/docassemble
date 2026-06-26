from docassemble.base.pattern import pattern_de
from .core import ensure_definition
from .capitalization import capitalize
from .numbers import number_or_length
from .language_en import comma_and_list_en

def comma_and_list_de(*pargs, **kwargs):
    if 'and_string' not in kwargs:
        kwargs['and_string'] = 'und'
    if 'oxford' not in kwargs:
        kwargs['oxford'] = False
    return comma_and_list_en(*pargs, **kwargs)


def verb_present_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    if new_args[1] == 'pl':
        new_args[1] = '3pl'
    output = pattern_de.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    if new_args[1] == 'ppl':
        new_args[1] = '3ppl'
    output = pattern_de.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_plural_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_de(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_de.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_de.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_de(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_de.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output
