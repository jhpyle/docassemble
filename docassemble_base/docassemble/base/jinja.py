import re
import os
from collections import abc, namedtuple
from itertools import groupby, chain
from docxtpl import RichText, DocxTemplate
from jinja2 import ChainableUndefined
from jinja2 import meta as jinja2meta
from jinja2.environment import Environment
from jinja2.ext import Extension
from jinja2.lexer import Token
from jinja2.runtime import StrictUndefined, UndefinedError
from jinja2.utils import internalcode, missing, object_type_repr
from .error import DAError, DASourceError, DAAttributeError, DAIndexError
from .filter.docx import inline_markdown_to_docx, markdown_to_docx
from .filter.utils import sanitize_xml
from .functions import (
    redact,
    phone_number_in_e164,
    manual_line_breaks,
    bold,
    single_to_double_newlines,
    single_paragraph,
    alpha,
    qr_code,
    country_name,
    phone_number_formatted,
    verbatim,
    roman,
    italic,
)
from .helpers import extract_missing_name, fix_quotes
from .language.capitalization import capitalize
from .language.currency import currency
from .language.language import (
    salutation,
    add_separators,
    comma_and_list,
    title_case,
    comma_list,
)
from .language.numbers import ordinal_number, nice_number, ordinal
from .language.utils import fix_punctuation
from .language.words import word
from .thread_context import this_thread
from .dates import (
    month_of,
    format_date,
    day_of,
    format_time,
    format_datetime,
    year_of,
    dow_of,
)

NoneType = type(None)

class DAExtension(Extension):

    def parse(self, parser):
        raise NotImplementedError()

    def filter_stream(self, stream):
        # in_var = False
        met_pipe = False
        for token in stream:
            if token.type == 'variable_begin':
                # in_var = True
                met_pipe = False
            if token.type == 'variable_end':
                # in_var = False
                if not met_pipe:
                    yield Token(token.lineno, 'pipe', None)
                    yield Token(token.lineno, 'name', 'ampersand_filter')
            # if in_var and token.type == 'pipe':
            #     met_pipe = True
            yield token


def ampersand_filter(value):
    if value.__class__.__name__ in ('DAFile', 'DALink', 'DAStaticFile', 'DAFileCollection', 'DAFileList'):
        return value
    if value.__class__.__name__ in ('CustomInlineImage', 'InlineImage', 'RichText', 'Listing', 'Document', 'Subdoc', 'DALazyTemplate', 'Markup'):
        return str(value)
    if isinstance(value, (int, bool, float, NoneType)):
        return value
    if not isinstance(value, str):
        value = str(value)
    value = sanitize_xml(value)
    if '<w:r>' in value or '</w:t>' in value:
        return re.sub(r'&(?!#?[0-9A-Za-z]+;)', '&amp;', value)
    for auto_filter in this_thread.misc.get('auto jinja filter', []):
        value = auto_filter(value)
    return re.sub(r'>', '&gt;', re.sub(r'<', '&lt;', re.sub(r'&(?!#?[0-9A-Za-z]+;)', '&amp;', value)))


class DAStrictUndefined(StrictUndefined):
    __slots__ = ('_undefined_type',)

    def __init__(self, hint=None, obj=missing, name=None, exc=UndefinedError, accesstype=None):  # pylint: disable=super-init-not-called
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
        raise self._undefined_exception(hint)
    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
        __lt__ = __le__ = __gt__ = __ge__ = __int__ = \
        __float__ = __complex__ = __pow__ = __rpow__ = __sub__ = \
        __rsub__ = __iter__ = __str__ = __len__ = __nonzero__ = __eq__ = \
        __ne__ = __bool__ = __hash__ = _fail_with_undefined_error


class DASkipUndefined(ChainableUndefined):
    """Undefined handler for Jinja2 exceptions that allows rendering most
    templates that have undefined variables. It will not fix all broken
    templates. For example, if the missing variable is used in a complex
    mathematical expression it may still break (but expressions with only two
    elements should render as '').
    """

    def __init__(self, *pargs, **kwargs):  # pylint: disable=super-init-not-called
        # Handle the way Docassemble DAEnvironment triggers attribute errors
        pass

    def __str__(self) -> str:
        return ''

    def __call__(self, *pargs, **kwargs) -> "DASkipUndefined":
        return self

    __getitem__ = __getattr__ = __call__

    def __eq__(self, *pargs) -> bool:
        return False

    # need to return a bool type
    __bool__ = __ne__ = __le__ = __lt__ = __gt__ = __ge__ = __nonzero__ = __eq__

    # let undefined variables work in for loops

    def __iter__(self, *pargs) -> "DASkipUndefined":
        return self

    def __next__(self, *pargs) -> None:
        raise StopIteration

    # need to return an int type

    def __int__(self, *pargs) -> int:
        return 0

    __len__ = __int__

    # need to return a float type

    def __float__(self, *pargs) -> float:
        return 0.0

    # need to return complex type

    def __complex__(self, *pargs) -> complex:
        return 0j

    def __add__(self, *pargs, **kwargs) -> str:
        return self.__str__()

    # type can be anything. we want it to work with `str()` function though
    # and we do not want to silently give wrong math results.
    # note that this means 1 + (undefined) or (undefined) + 1 will work but not 1 + (undefined) + 1
    __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __pow__ = __rpow__ = \
        __sub__ = __rsub__ = __hash__ = __add__


class DAEnvironment(Environment):

    def from_string(self, source, **kwargs):  # pylint: disable=arguments-differ
        source = re.sub(r'({[\%\{].*?[\%\}]})', fix_quotes, source)
        return super().from_string(source, **kwargs)

    def getitem(self, obj, argument):
        try:
            return obj[argument]
        except (DAAttributeError, DAIndexError) as err:
            varname = extract_missing_name(err)
            if 'pending_error' in this_thread.misc:
                del this_thread.misc['pending_error']
            return self.undefined(obj=missing, name=varname)
        except (AttributeError, TypeError, LookupError):
            if 'pending_error' in this_thread.misc:
                del this_thread.misc['pending_error']
            return self.undefined(obj=obj, name=argument, accesstype='item')

    def getattr(self, obj, attribute):
        try:
            return getattr(obj, attribute)
        except DAAttributeError as err:
            if 'pending_error' in this_thread.misc:
                del this_thread.misc['pending_error']
            varname = extract_missing_name(err)
            return self.undefined(obj=missing, name=varname)
        except AttributeError:
            if 'pending_error' in this_thread.misc:
                del this_thread.misc['pending_error']
        return self.undefined(obj=obj, name=attribute, accesstype='attribute')


def mygetattr(y, attr, default=None):
    for attribute in attr.split('.'):
        y = getattr(y, attribute, default)
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
    return sorted(dictionary.items(), key=lambda y: str_or_original(y[0], case_sensitive), reverse=reverse)


def sort_filter(the_array, reverse=False, case_sensitive=False, attribute=None):
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
    return sorted(the_array, key=key_func, reverse=reverse)

_GroupTuple = namedtuple('_GroupTuple', ['grouper', 'list'])
_GroupTuple.__repr__ = tuple.__repr__
_GroupTuple.__str__ = tuple.__str__


def groupby_filter(the_array, attr_name):

    def func(y):
        return mygetattr(y, attr_name)
    return [_GroupTuple(key, list(values)) for key, values in groupby(sorted(the_array, key=func), func)]


def max_filter(the_array, case_sensitive=False, attribute=None):
    it = iter(the_array)
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


def min_filter(the_array, case_sensitive=False, attribute=None):
    it = iter(the_array)
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


def sum_filter(the_array, attribute=None, start=0):
    if attribute is not None:
        the_array = [mygetattr(y, attribute) for y in the_array]
    return sum(the_array, start)


def unique_filter(the_array, case_sensitive=False, attribute=None):
    seen = set()
    if attribute is None:
        for item in the_array:
            new_item = str_or_original(item, case_sensitive)
            if new_item not in seen:
                seen.add(new_item)
                yield item
    else:
        for item in the_array:
            new_item = str_or_original(mygetattr(item, attribute), case_sensitive)
            if new_item not in seen:
                seen.add(new_item)
                yield mygetattr(item, attribute)


def join_filter(the_array, d="", attribute=None):
    if attribute is not None:
        return d.join([str(mygetattr(y, attribute)) for y in the_array])
    return d.join([str(y) for y in the_array])


def attr_filter(var, attr_name):
    return mygetattr(var, attr_name)


def selectattr_filter(*pargs, **kwargs):
    if len(pargs) > 2:
        the_array = pargs[0]
        attr_name = pargs[1]
        func_name = pargs[2]
        env = custom_jinja_env()
        def func(item):
            return env.call_test(func_name, item, pargs[3:], kwargs)
        for item in the_array:
            if func(mygetattr(item, attr_name)):
                yield item
    else:
        for item in pargs[0]:
            if mygetattr(item, pargs[1]):
                yield item


def rejectattr_filter(*pargs, **kwargs):
    if len(pargs) > 2:
        the_array = pargs[0]
        attr_name = pargs[1]
        func_name = pargs[2]
        env = custom_jinja_env()
        def func(item):
            return env.call_test(func_name, item, pargs[3:], kwargs)
        for item in the_array:
            if not func(mygetattr(item, attr_name)):
                yield item
    else:
        for item in pargs[0]:
            if not mygetattr(item, pargs[1]):
                yield item


def chain_filter(*pargs, **kwargs):  # pylint: disable=unused-argument
    the_list = []
    for parg in pargs:
        if isinstance(parg, str):
            the_list.append(parg)
        elif (hasattr(parg, 'instanceName') and hasattr(parg, 'elements')):
            if isinstance(parg.elements, dict):
                for sub_parg in parg.values():
                    the_list.append(sub_parg)
            else:
                for sub_parg in parg:
                    the_list.append(sub_parg)
        elif isinstance(parg, abc.Iterable):
            for sub_parg in parg:
                the_list.append(sub_parg)
        else:
            the_list.append(parg)
    return chain(*the_list)


def map_filter(*pargs, **kwargs):
    if len(pargs) >= 2:
        the_array = pargs[0]
        the_filter = pargs[1]
        env = custom_jinja_env()
        if the_filter not in env.filters:
            raise DAError('filter passed to map() does not exist')
        for item in the_array:
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
            the_kwargs = kwargs.get('kwargs', {})
            the_pargs = kwargs.get('pargs', [])
            if not isinstance(the_kwargs, dict):
                raise DAError('kwargs passed to map() must be a dictionary')
            if not isinstance(the_pargs, list):
                raise DAError('pargs passed to map() must be a list')
            for item in pargs[0]:
                yield kwargs['function'](item, *the_pargs, **the_kwargs)
        else:
            raise DAError('map() must refer to a function, index, attribute, or filter')


def markdown_filter(text):
    return markdown_to_docx(text, this_thread.current_question, this_thread.misc.get('docx_template', None))


def inline_markdown_filter(text):
    return inline_markdown_to_docx(text, this_thread.current_question, this_thread.misc.get('docx_template', None))


def get_builtin_jinja_filters():
    return {
        'ampersand_filter': ampersand_filter,
        'markdown': markdown_filter,
        'add_separators': add_separators,
        'inline_markdown': inline_markdown_filter,
        'paragraphs': single_to_double_newlines,
        'manual_line_breaks': manual_line_breaks,
        'RichText': RichText,
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
        'format_date': format_date,
        'format_datetime': format_datetime,
        'format_time': format_time,
        'month_of': month_of,
        'year_of': year_of,
        'day_of': day_of,
        'dow_of': dow_of,
        'qr_code': qr_code,
        'nice_number': nice_number,
        'ordinal': ordinal,
        'ordinal_number': ordinal_number,
        'currency': currency,
        'comma_list': comma_list,
        'comma_and_list': comma_and_list,
        'capitalize': capitalize,
        'salutation': salutation,
        'alpha': alpha,
        'roman': roman,
        'word': word,
        'bold': bold,
        'italic': italic,
        'title_case': title_case,
        'single_paragraph': single_paragraph,
        'phone_number_formatted': phone_number_formatted,
        'phone_number_in_e164': phone_number_in_e164,
        'country_name': country_name,
        'fix_punctuation': fix_punctuation,
        'redact': redact,
        'verbatim': verbatim,
        'map': map_filter,
        'chain': chain_filter,
        'any': any,
        'all': all
    }


registered_jinja_filters = {}


def custom_jinja_env(skip_undefined=False):
    if skip_undefined:
        env = DAEnvironment(undefined=DASkipUndefined, extensions=[DAExtension])
    else:
        env = DAEnvironment(undefined=DAStrictUndefined, extensions=[DAExtension])
    env.filters.update(registered_jinja_filters)
    env.filters.update(get_builtin_jinja_filters())
    return env


def register_jinja_filter(filter_name, func):
    if filter_name in get_builtin_jinja_filters():
        raise DAError("Cannot register filter with same name as built-in filter %s" % filter_name)
    registered_jinja_filters[filter_name] = func


def get_docx_variables(the_path):
    names = set()
    if not os.path.isfile(the_path):
        raise DASourceError("Missing docx template file " + os.path.basename(the_path))
    try:
        docx_template = DocxTemplate(the_path)
        docx_template.render_init()
        the_env = custom_jinja_env()
        the_xml = docx_template.get_xml()
        the_xml = re.sub(r'<w:p([ >])', r'\n<w:p\1', the_xml)
        the_xml = re.sub(r'({[\%\{].*?[\%\}]})', fix_quotes, the_xml)
        the_xml = docx_template.patch_xml(the_xml)
        parsed_content = the_env.parse(the_xml)
    except BaseException as the_err:
        raise DASourceError("There was an error parsing the docx file: " + the_err.__class__.__name__ + " " + str(the_err))
    for key in jinja2meta.find_undeclared_variables(parsed_content):
        if not key.startswith('__'):
            names.add(key)
    from docassemble.base.legal import __all__ as legal_all  # pylint: disable=import-outside-toplevel
    for name in legal_all:
        if name in names:
            names.remove(name)
    return sorted(list(names))
