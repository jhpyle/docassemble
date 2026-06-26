import locale
from docassemble.base.thread_context import this_thread
from docassemble.base.logger import logmessage

def get_language():
    """Return the current language code.

    Returns:
        str: The current language code (e.g., ``'en'``, ``'es'``).
    """
    return this_thread.language


def set_language(lang, dialect=None, voice=None):
    """Set the language used for linguistic functions and the web application.

    Does not change the Python locale; call ``update_locale()`` for that.
    Should be called in an ``initial`` code block so it takes effect on every
    page load.

    Args:
        lang (str): A lowercase ISO-639-1 or ISO-639-3 language code
            (e.g., ``'en'``, ``'es'``, ``'fr'``).
        dialect (str, optional): A dialect code for the text-to-speech engine.
            Defaults to None.
        voice (str, optional): A voice name for the text-to-speech engine.
            Defaults to None.
    """
    try:
        if dialect:
            this_thread.dialect = dialect
        elif lang != this_thread.language:
            this_thread.dialect = None
    except:
        pass
    try:
        if voice:
            this_thread.voice = voice
        elif lang != this_thread.language:
            this_thread.voice = None
    except:
        pass
    this_thread.language = lang


def set_country(country):
    """Set the current country used for phone number formatting and other locale features.

    Args:
        country (str): A two-letter uppercase ISO 3166-1 alpha-2 country code
            (e.g., ``'US'``, ``'GB'``, ``'DE'``).
    """
    this_thread.country = country


def get_country():
    """Return the current country code.

    Returns:
        str: A two-letter uppercase ISO 3166-1 alpha-2 country code
            (e.g., ``'US'``). Defaults to ``'US'`` unless configured otherwise.
    """
    return this_thread.country


def get_dialect():
    """Return the current dialect.

    Returns:
        str: The dialect code set by the ``dialect`` keyword argument to
            :func:`set_language`, or ``None`` if no dialect has been set.
    """
    return this_thread.dialect


def get_voice():
    """Return the current voice.

    Returns:
        str: The voice name set by the ``voice`` keyword argument to
            :func:`set_language`, or ``None`` if no voice has been set.
    """
    return this_thread.voice


def set_locale(*pargs, **kwargs):
    """Set the current locale string and/or locale convention overrides.

    Calling ``set_locale('FR.utf8')`` stores the locale string so that
    :func:`get_locale` returns it.  The actual Python locale does not change
    until :func:`update_locale` is called.  Keyword arguments such as
    ``currency_symbol`` override individual locale conventions used by
    functions like :func:`currency` and :func:`currency_symbol`.

    Args:
        *pargs: An optional locale string (e.g. ``'FR.utf8'``).
        **kwargs: Locale convention overrides (e.g. ``currency_symbol='€'``).
    """
    if len(pargs) == 1:
        this_thread.locale = pargs[0]
    if len(kwargs):
        this_thread.misc['locale_overrides'] = kwargs


def get_locale(*pargs):
    """Return the current locale setting or a specific locale convention.

    With no arguments, returns the locale string previously set with
    :func:`set_locale`.  With one argument, returns the value of the named
    locale convention (e.g. ``'currency_symbol'``), taking into account any
    overrides set with :func:`set_locale`.

    Args:
        *pargs: An optional locale convention name (e.g.
            ``'currency_symbol'``).

    Returns:
        str or None: The locale string when called with no arguments, or the
            value of the requested locale convention (``None`` if not found).
    """
    if len(pargs) == 1:
        if 'locale_overrides' in this_thread.misc and pargs[0] in this_thread.misc['locale_overrides']:
            return this_thread.misc['locale_overrides'][pargs[0]]
        return locale.localeconv().get(pargs[0], None)
    return this_thread.locale


def update_locale():
    """Update the Python locale based on the current language and locale settings.

    Applies the locale string previously set with :func:`set_locale` (combined
    with the current language from :func:`get_language` when necessary) so that
    Python's ``locale`` module reflects the desired locale.  This is required
    for functions like :func:`currency` and :func:`currency_symbol` to produce
    locale-appropriate formatting.
    """
    if '_' in this_thread.locale:
        the_locale = str(this_thread.locale)
    else:
        the_locale = str(this_thread.language) + '_' + str(this_thread.locale)
    try:
        locale.setlocale(locale.LC_ALL, the_locale)
    except BaseException as err:
        logmessage("update_locale error: unable to set the locale to " + the_locale)
        logmessage(err.__class__.__name__ + ": " + str(err))
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
