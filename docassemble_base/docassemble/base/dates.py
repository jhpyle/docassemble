try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore[no-redef]
import datetime
import dateutil
import dateutil.parser
import babel.dates
from .empty import DAEmpty
from .hooks import get_configuration, get_default_timezone
from .language.capitalization import capitalize
from .language.control import get_language
from .language.core import ensure_definition
from .language.language import noun_plural, comma_and_list
from .language.numbers import nice_number
from .language.words import word
from .thread_context import this_thread

def interview_default(the_part, default_value, language):
    if the_part in this_thread.internal and this_thread.internal[the_part] is not None:
        return this_thread.internal[the_part]
    for lang in (language, get_language(), '*'):
        if lang is not None and this_thread.interview is not None and lang in this_thread.interview.default_title and the_part in this_thread.interview.default_title[lang]:
            return this_thread.interview.default_title[lang][the_part]
    return default_value

def today(timezone=None, format=None):  # pylint: disable=redefined-builtin
    """Return today's date at midnight as a DADateTime object.

    Args:
        timezone (str or None): IANA timezone name. If None, the interview's
            default timezone is used.
        format (str or None): If provided, return the date formatted as a
            string using this Babel date-format pattern instead of a
            DADateTime.

    Returns:
        DADateTime or str: Midnight today in the given timezone, or a
            formatted date string if ``format`` is specified.
    """
    ensure_definition(timezone, format)
    if timezone is None:
        timezone = get_default_timezone()
    val = datetime.datetime.now(datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone))
    if format is not None:
        return dd(val.replace(hour=0, minute=0, second=0, microsecond=0)).format_date(format)
    return dd(val.replace(hour=0, minute=0, second=0, microsecond=0))


def babel_language(language):
    if 'babel dates map' not in get_configuration():
        return language
    return get_configuration()['babel dates map'].get(language, language)


def month_of(the_date, as_word=False, language=None):
    """Return the month component of a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            extract the month from.
        as_word (bool): If True, return the full month name (e.g.
            ``'January'``); otherwise return the month as an integer.
        language (str or None): Language code for localizing the month name.
            Defaults to the current interview language.

    Returns:
        int or str: Month number (1–12) or localized month name.
    """
    ensure_definition(the_date, as_word, language)
    if language is None:
        language = get_language()
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        if as_word:
            return babel.dates.format_date(date, format='MMMM', locale=babel_language(language))
        return int(date.strftime('%m'))
    except:
        return word("Bad date")


def day_of(the_date, language=None):
    """Return the day-of-month component of a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            extract the day from.
        language (str or None): Unused; retained for API consistency.

    Returns:
        int: Day of the month (1–31).
    """
    ensure_definition(the_date, language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return int(date.strftime('%d'))
    except:
        return word("Bad date")


def dow_of(the_date, as_word=False, language=None):
    """Return the day of the week for a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            inspect.
        as_word (bool): If True, return the full weekday name (e.g.
            ``'Monday'``); otherwise return an integer from 1 (Monday) to
            7 (Sunday) per ISO 8601.
        language (str or None): Language code for localizing the weekday
            name. Defaults to the current interview language.

    Returns:
        int or str: Day-of-week number or localized weekday name.
    """
    ensure_definition(the_date, as_word, language)
    if language is None:
        language = get_language()
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        if as_word:
            return babel.dates.format_date(date, format='EEEE', locale=babel_language(language))
        return int(date.strftime('%u'))
    except:
        return word("Bad date")


def year_of(the_date, language=None):
    """Return the year component of a date.

    Args:
        the_date (datetime.date, datetime.datetime, or str): The date to
            extract the year from.
        language (str or None): Unused; retained for API consistency.

    Returns:
        int: Four-digit year.
    """
    ensure_definition(the_date, language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return int(date.strftime('%Y'))
    except:
        return word("Bad date")


def format_date(the_date, format=None, language=None):  # pylint: disable=redefined-builtin
    """Return a date formatted as a localized string.

    Args:
        the_date (datetime.date, datetime.datetime, or str): Date to format.
        format (str or None): Babel date-format pattern (e.g. ``'long'``,
            ``'short'``, ``'MM/dd/yyyy'``). Defaults to the interview's
            configured date format or ``'long'``.
        language (str or None): Language/locale code. Defaults to the current
            interview language.

    Returns:
        str: Formatted date string, or ``''`` for an empty date.
    """
    ensure_definition(the_date, format, language)
    if isinstance(the_date, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('date format', 'long', language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_date(date, format=format, locale=babel_language(language))
    except:
        return word("Bad date")


def format_datetime(the_date, format=None, language=None):  # pylint: disable=redefined-builtin
    """Return a date and time formatted as a localized string.

    Args:
        the_date (datetime.datetime or str): Date/time to format.
        format (str or None): Babel datetime-format pattern. Defaults to the
            interview's configured datetime format or ``'long'``.
        language (str or None): Language/locale code. Defaults to the current
            interview language.

    Returns:
        str: Formatted datetime string, or ``''`` for an empty date.
    """
    ensure_definition(the_date, format, language)
    if isinstance(the_date, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('datetime format', 'long', language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_datetime(date, format=format, locale=babel_language(language))
    except:
        return word("Bad date")


def format_time(the_time, format=None, language=None):  # pylint: disable=redefined-builtin
    """Return a time formatted as a localized string.

    Args:
        the_time (datetime.time, datetime.datetime, or str): Time to format.
        format (str or None): Babel time-format pattern. Defaults to the
            interview's configured time format or ``'short'``.
        language (str or None): Language/locale code. Defaults to the current
            interview language.

    Returns:
        str: Formatted time string, or ``''`` for an empty time.
    """
    ensure_definition(the_time, format, language)
    if isinstance(the_time, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('time format', 'short', language)
    try:
        if isinstance(the_time, (datetime.datetime, datetime.date, datetime.time)):
            this_time = the_time
        else:
            this_time = dateutil.parser.parse(the_time)
        return babel.dates.format_time(this_time, format=format, locale=babel_language(language))
    except BaseException as errmess:
        return word("Bad date: " + str(errmess))


class DateTimeDelta:

    def __str__(self):
        return str(self.describe())

    def describe(self, **kwargs):
        specificity = kwargs.get('specificity', None)
        output = []
        diff = dateutil.relativedelta.relativedelta(self.end, self.start)
        if diff.years != 0:
            output.append((abs(diff.years), noun_plural(word('year'), abs(diff.years), noun_is_singular=True)))
        if diff.months != 0 and specificity != 'year':
            output.append((abs(diff.months), noun_plural(word('month'), abs(diff.months), noun_is_singular=True)))
        if diff.days != 0 and specificity not in ('year', 'month'):
            output.append((abs(diff.days), noun_plural(word('day'), abs(diff.days), noun_is_singular=True)))
        if len(output) == 0 or specificity in ('hour', 'minute', 'second'):
            if diff.hours != 0 and specificity not in ('year', 'month', 'day'):
                output.append((abs(diff.hours), noun_plural(word('hour'), abs(diff.hours), noun_is_singular=True)))
            if (abs(diff.hours) < 2 or specificity in ('minute', 'second')) and diff.minutes != 0 and specificity not in ('year', 'month', 'day', 'hour'):
                output.append((abs(diff.minutes), noun_plural(word('minute'), abs(diff.minutes), noun_is_singular=True)))
        if len(output) == 0 or specificity == 'second':
            if diff.seconds != 0 and specificity not in ('year', 'month', 'day', 'hour', 'minute'):
                output.append((abs(diff.seconds), noun_plural(word('second'), abs(diff.seconds), noun_is_singular=True)))
        if len(output) == 0:
            if specificity is None:
                output.append((0, noun_plural(word('second'), 0, noun_is_singular=True)))
            else:
                output.append((0, noun_plural(word(specificity), 0, noun_is_singular=True)))
        if kwargs.get('nice', True):
            return_value = comma_and_list(["%s %s" % (nice_number(y[0]), y[1]) for y in output])
            if kwargs.get('capitalize', False):
                return capitalize(return_value)
            return return_value
        return comma_and_list(["%d %s" % y for y in output])


class DADateTime(datetime.datetime):
    """A timezone-aware datetime subclass with docassemble-specific formatting and arithmetic.

    Inherits all ``datetime.datetime`` behavior and adds convenience methods
    for formatting, date arithmetic, and accessing ISO calendar properties.

    Attributes:
        dow (int): Day of the week (1 = Monday … 7 = Sunday, ISO 8601).
        week (int): ISO week number of the year.
        nanosecond (int): Always 0; provided for compatibility.
    """

    def format(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_date(self, format=format, language=language)

    def format_date(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_date(self, format=format, language=language)

    def format_datetime(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_datetime(self, format=format, language=language)

    def format_time(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_time(self, format=format, language=language)

    def replace_time(self, the_time):
        return self.replace(hour=the_time.hour, minute=the_time.minute, second=the_time.second, microsecond=the_time.microsecond)

    @property
    def nanosecond(self):
        return 0

    @property
    def dow(self):
        return self.isocalendar()[2]

    @property
    def week(self):
        return self.isocalendar()[1]

    def plus(self, **kwargs):
        return dd(dt(self) + date_interval(**kwargs))

    def minus(self, **kwargs):
        return dd(dt(self) - date_interval(**kwargs))

    def __str__(self):
        return str(format_date(self))

    def __add__(self, other):
        if isinstance(other, str):
            return str(self) + other
        val = dt(self) + other
        if isinstance(val, datetime.date):
            return dd(val)
        return val

    def __radd__(self, other):
        if isinstance(other, str):
            return other + str(self)
        return dd(dt(self) + other)

    def __sub__(self, other):
        val = dt(self) - other
        if isinstance(val, datetime.date):
            return dd(val)
        return val

    def __rsub__(self, other):
        val = other - dt(self)
        if isinstance(val, datetime.date):
            return dd(val)
        return val


def current_datetime(timezone=None):
    """Return the current date and time as a DADateTime object.

    Args:
        timezone (str or None): IANA timezone name. If None, the interview's
            default timezone is used.

    Returns:
        DADateTime: Current date and time in the specified timezone.
    """
    ensure_definition(timezone)
    if timezone is None:
        timezone = get_default_timezone()
    return dd(datetime.datetime.now(datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)))


def as_datetime(the_date, timezone=None):
    """Convert a date or date string to a timezone-aware DADateTime object.

    Args:
        the_date (datetime.date, datetime.datetime, or str): Date or
            date/time value to convert. String values are parsed with
            ``dateutil``.
        timezone (str or None): IANA timezone name to attach. If the value
            already carries timezone information it is converted to this
            zone; otherwise the timezone is applied as-is. Defaults to
            the interview's default timezone.

    Returns:
        DADateTime: Timezone-aware datetime.
    """
    ensure_definition(the_date, timezone)
    if timezone is None:
        timezone = get_default_timezone()
    if isinstance(the_date, datetime.date) and not isinstance(the_date, datetime.datetime):
        the_date = datetime.datetime.combine(the_date, datetime.datetime.min.time())
    if isinstance(the_date, datetime.datetime):
        new_datetime = the_date
    else:
        new_datetime = dateutil.parser.parse(the_date)
    if new_datetime.tzinfo:
        new_datetime = new_datetime.astimezone(zoneinfo.ZoneInfo(timezone))
    else:
        new_datetime = new_datetime.replace(tzinfo=zoneinfo.ZoneInfo(timezone))
    return dd(new_datetime)


def dd(obj):
    if isinstance(obj, DADateTime):
        return obj
    return DADateTime(obj.year, month=obj.month, day=obj.day, hour=obj.hour, minute=obj.minute, second=obj.second, microsecond=obj.microsecond, tzinfo=obj.tzinfo)


def dt(obj):
    return datetime.datetime(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond, obj.tzinfo)


def date_interval(**kwargs):
    """Return a relative date/time interval.

    All keyword arguments are forwarded to
    ``dateutil.relativedelta.relativedelta``. Common arguments include
    ``years``, ``months``, ``weeks``, ``days``, ``hours``, ``minutes``,
    and ``seconds``.

    Returns:
        dateutil.relativedelta.relativedelta: Interval that can be added to
            or subtracted from a ``DADateTime`` or ``datetime`` object.
    """
    ensure_definition(**kwargs)
    return dateutil.relativedelta.relativedelta(**kwargs)


def date_difference(starting=None, ending=None, timezone=None):
    """Return the difference between two dates.

    Args:
        starting (datetime.date, datetime.datetime, str, or None): Start of
            the interval. Defaults to the current datetime.
        ending (datetime.date, datetime.datetime, str, or None): End of the
            interval. Defaults to the current datetime.
        timezone (str or None): IANA timezone name used when localizing
            naive datetimes. Defaults to the interview's default timezone.

    Returns:
        DateTimeDelta: Object with ``weeks``, ``days``, ``hours``,
            ``minutes``, ``seconds``, ``years``, and ``delta`` attributes
            expressing the difference, and ``start``/``end`` attributes
            holding the resolved datetime objects.
    """
    ensure_definition(starting, ending, timezone)
    if starting is None:
        starting = current_datetime()
    if ending is None:
        ending = current_datetime()
    if timezone is None:
        timezone = get_default_timezone()
    if isinstance(starting, datetime.date) and not isinstance(starting, datetime.datetime):
        starting = datetime.datetime.combine(starting, datetime.datetime.min.time())
    if isinstance(ending, datetime.date) and not isinstance(ending, datetime.datetime):
        ending = datetime.datetime.combine(ending, datetime.datetime.min.time())
    if not isinstance(starting, datetime.datetime):
        starting = dateutil.parser.parse(starting)
    if not isinstance(ending, datetime.datetime):
        ending = dateutil.parser.parse(ending)
    if starting.tzinfo:
        starting = starting.astimezone(zoneinfo.ZoneInfo(timezone))
    else:
        starting = starting.replace(tzinfo=zoneinfo.ZoneInfo(timezone))
    if ending.tzinfo:
        ending = ending.astimezone(zoneinfo.ZoneInfo(timezone))
    else:
        ending = ending.replace(tzinfo=zoneinfo.ZoneInfo(timezone))
    delta = ending - starting
    output = DateTimeDelta()
    output.start = starting
    output.end = ending
    output.weeks = (delta.days / 7.0) + (delta.seconds / 604800.0)
    output.days = delta.days + (delta.seconds / 86400.0)
    output.hours = (delta.days * 24.0) + (delta.seconds / 3600.0)
    output.minutes = (delta.days * 1440.0) + (delta.seconds / 60.0)
    output.seconds = (delta.days * 86400) + delta.seconds
    output.years = (delta.days + delta.seconds / 86400.0) / 365.2425
    output.delta = delta
    return output
