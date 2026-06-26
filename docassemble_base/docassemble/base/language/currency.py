import locale
from docassemble.base.hooks import get_configuration
from docassemble.base.thread_context import this_thread
from .control import get_locale
from .core import (
    language_function_constructor,
    ensure_definition,
    update_language_function,
    language_functions,
)

currency = language_function_constructor('currency')
currency_symbol = language_function_constructor('currency_symbol')

if currency.__doc__ is None:
    currency.__doc__ = """Format a number as a currency value using the current locale.

    Args:
        value: The numeric value to format.
        **kwargs: Optional keyword arguments including ``decimals`` (bool,
            default ``True``), ``symbol`` (str override for the currency
            symbol), and ``symbol_precedes`` (bool controlling symbol
            position).

    Returns:
        str: The formatted currency string (e.g. ``currency(45.2)`` returns
            ``'$45.20'`` for a US locale).
    """
if currency_symbol.__doc__ is None:
    currency_symbol.__doc__ = """Return the currency symbol for the current locale.

    Returns:
        str: The currency symbol (e.g. ``'$'`` for a US locale). Respects
            overrides set via :func:`set_locale` or the ``currency symbol``
            configuration setting.
    """

def currency_symbol_default(**kwargs):  # pylint: disable=unused-argument
    """Returns the currency symbol for the current locale."""
    return str(locale.localeconv()['currency_symbol'])


def currency_default(the_value, **kwargs):
    """Returns the value as a currency, according to the conventions of
    the current locale.  Use the optional keyword argument
    decimals=False if you do not want to see decimal places in the
    number, and the optional currency_symbol for a different symbol
    than the default.

    """
    decimals = kwargs.get('decimals', True)
    symbol = kwargs.get('symbol', None)
    symbol_precedes = kwargs.get('symbol_precedes', None)
    ensure_definition(the_value, decimals, symbol)
    obj_type = type(the_value).__name__
    if obj_type in ['FinancialList', 'PeriodicFinancialList']:
        the_value = the_value.total()
    elif obj_type in ['Value', 'PeriodicValue']:
        if the_value.exists:
            the_value = the_value.amount()
        else:
            the_value = 0
    elif obj_type == 'DACatchAll':
        the_value = float(the_value)
    try:
        float(the_value)
    except:
        return ''
    the_float_value = float(the_value)
    the_symbol = None
    if symbol is not None:
        the_symbol = symbol
    elif 'locale_overrides' in this_thread.misc and 'currency_symbol' in this_thread.misc['locale_overrides']:
        the_symbol = this_thread.misc['locale_overrides']['currency_symbol']
    elif language_functions['currency_symbol']['*'] is not currency_symbol_default:
        the_symbol = currency_symbol()
    the_symbol_precedes = None
    if symbol_precedes is not None:
        the_symbol_precedes = symbol_precedes
    elif 'locale_overrides' in this_thread.misc and the_float_value < 0 and 'n_cs_precedes' in this_thread.misc['locale_overrides']:
        the_symbol_precedes = bool(this_thread.misc['locale_overrides']['n_cs_precedes'])
    elif 'locale_overrides' in this_thread.misc and 'p_cs_precedes' in this_thread.misc['locale_overrides']:
        the_symbol_precedes = bool(this_thread.misc['locale_overrides']['p_cs_precedes'])
    if the_symbol is None and the_symbol_precedes is None and decimals:
        return str(locale.currency(the_float_value, symbol=True, grouping=True))
    if the_symbol is None:
        the_symbol = currency_symbol()
    if the_symbol_precedes is None:
        if the_float_value < 0:
            the_symbol_precedes = bool(get_locale('n_cs_precedes'))
        else:
            the_symbol_precedes = bool(get_locale('p_cs_precedes'))
    output = ''
    if the_symbol_precedes:
        output += the_symbol
        if the_float_value < 0:
            if get_locale('n_sep_by_space'):
                output += ' '
        elif get_locale('p_sep_by_space'):
            output += ' '
    if decimals:
        output += locale.format_string('%.' + str(get_configuration().get('currency decimal places', locale.localeconv()['frac_digits'])) + 'f', the_float_value, grouping=True, monetary=True)
    else:
        output += locale.format_string("%d", int(the_float_value), grouping=True, monetary=True)
    if not the_symbol_precedes:
        if the_float_value < 0:
            if get_locale('n_sep_by_space'):
                output += ' '
        elif get_locale('p_sep_by_space'):
            output += ' '
        output += the_symbol
    return output


def get_currency_symbol():
    """Returns the current setting for the currency symbol if there is
    one, and otherwise returns the default currency symbol.

    """
    if 'locale_overrides' in this_thread.misc and 'currency_symbol' in this_thread.misc['locale_overrides']:
        return this_thread.misc['locale_overrides']['currency_symbol']
    return currency_symbol()


update_language_function('*', 'currency_symbol', currency_symbol_default)
