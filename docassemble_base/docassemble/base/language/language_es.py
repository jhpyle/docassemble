from docassemble.base.pattern import pattern_es
from .core import ensure_definition
from .capitalization import capitalize
from .numbers import number_or_length
from .language_en import comma_and_list_en

def comma_and_list_es(*pargs, **kwargs):
    if 'and_string' not in kwargs:
        kwargs['and_string'] = 'y'
    return comma_and_list_en(*pargs, **kwargs)


def verb_present_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(str(arg))
    if len(new_args) < 2:
        new_args.append('3sg')
    if new_args[1] == 'pl':
        new_args[1] = '3pl'
    output = pattern_es.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def verb_past_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    new_args = []
    for arg in pargs:
        new_args.append(arg)
    if len(new_args) < 2:
        new_args.append('3sgp')
    if new_args[1] == 'ppl':
        new_args[1] = '3ppl'
    output = pattern_es.conjugate(*new_args, **kwargs)
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_plural_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if kwargs.get('noun_is_singular', False):
        noun = pargs[0]
    else:
        noun = noun_singular_es(pargs[0])
    if len(pargs) >= 2 and number_or_length(pargs[1]) == 1:
        return str(noun)
    output = pattern_es.pluralize(str(noun))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def noun_singular_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    if len(pargs) >= 2 and number_or_length(pargs[1]) != 1:
        return pargs[0]
    output = pattern_es.singularize(str(pargs[0]))
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output


def indefinite_article_es(*pargs, **kwargs):
    ensure_definition(*pargs, **kwargs)
    output = pattern_es.article(str(pargs[0]).lower()) + " " + str(pargs[0])
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(output)
    return output
