import titlecase
from .core import ensure_definition, language_function_constructor, language_functions
from .capitalization import capitalize
from .words import word
from .numbers import nice_number, nice_number_default
from .language_en import (
    verb_present_en,
    verb_past_en,
    possessify_en,
    indefinite_article_en,
    noun_singular_en,
    noun_plural_en,
    add_separators_en,
    comma_list_en,
    comma_and_list_en,
)
from .language_es import (
    verb_past_es,
    noun_plural_es,
    indefinite_article_es,
    noun_singular_es,
    verb_present_es,
    comma_and_list_es,
)
from .language_de import (
    indefinite_article_de,
    noun_singular_de,
    verb_past_de,
    verb_present_de,
    noun_plural_de,
    comma_and_list_de,
)
from .language_fr import verb_past_fr, noun_plural_fr, noun_singular_fr, verb_present_fr
from .language_it import (
    noun_singular_it,
    noun_plural_it,
    verb_past_it,
    indefinite_article_it,
    verb_present_it,
)
from .language_nl import verb_past_nl, verb_present_nl, noun_singular_nl, noun_plural_nl
from .currency import currency_default
from .capitalization import capitalize_default

def titlecasestr(text):
    return titlecase.titlecase(str(text))


def salutation_default(indiv, **kwargs):
    """Returns Mr., Ms., etc. for an individual."""
    with_name = kwargs.get('with_name', False)
    with_name_and_punctuation = kwargs.get('with_name_and_punctuation', False)
    ensure_definition(indiv, with_name, with_name_and_punctuation)
    used_gender = False
    gender = str(indiv.gender).casefold()
    if hasattr(indiv, 'salutation_to_use') and indiv.salutation_to_use is not None:
        salut = indiv.salutation_to_use
    elif hasattr(indiv, 'is_doctor') and indiv.is_doctor:
        salut = 'Dr.'
    elif hasattr(indiv, 'is_judge') and indiv.is_judge:
        salut = 'Judge'
    elif hasattr(indiv, 'name') and hasattr(indiv.name, 'suffix') and indiv.name.suffix in ('MD', 'PhD'):
        salut = 'Dr.'
    elif hasattr(indiv, 'name') and hasattr(indiv.name, 'suffix') and indiv.name.suffix == 'J':
        salut = 'Judge'
    elif gender == 'female':
        used_gender = True
        salut = 'Ms.'
    elif gender == 'male':
        used_gender = True
        salut = 'Mr.'
    else:
        used_gender = True
        salut = 'Mx.'
    if with_name_and_punctuation or with_name:
        if used_gender and gender not in ('male', 'female'):
            salut_and_name = indiv.name.full()
        else:
            salut_and_name = salut + ' ' + indiv.name.last
        if with_name_and_punctuation:
            if hasattr(indiv, 'is_friendly') and indiv.is_friendly:
                punct = ','
            else:
                punct = ':'
            return salut_and_name + punct
        if with_name:
            return salut_and_name
    return salut


def quantity_noun_default(the_number, noun, **kwargs):
    as_integer = kwargs.get('as_integer', True)
    capitalize_arg = kwargs.get('capitalize', False)
    language = kwargs.get('language', None)
    ensure_definition(the_number, noun, as_integer, capitalize_arg, language)
    if as_integer:
        the_number = int(round(the_number))
    result = nice_number(the_number, language=language) + " " + noun_plural(noun, the_number, language=language)
    if capitalize_arg:
        return capitalize(result)
    return result


def prefix_constructor(prefix):

    def func(the_word, **kwargs):
        ensure_definition(the_word, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(prefix)) + str(the_word)
        return str(prefix) + str(the_word)
    return func


def double_prefix_constructor_reverse(prefix_one, prefix_two):

    def func(word_one, word_two, **kwargs):
        ensure_definition(word_one, word_two, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(prefix_one)) + str(word_two) + str(prefix_two) + str(word_one)
        return str(prefix_one) + str(word_two) + str(prefix_two) + str(word_one)
    return func


def prefix_constructor_two_arguments(prefix, **kwargs):  # pylint: disable=unused-argument

    def func(word_one, word_two, **kwargs):
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(prefix)) + str(word_one) + ' ' + str(word_two)
        return str(prefix) + str(word_one) + ' ' + str(word_two)
    return func


def middle_constructor(middle, **kwargs):  # pylint: disable=unused-argument

    def func(a, b, **kwargs):
        ensure_definition(a, b, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(str(a)) + str(middle) + str(b)
        return str(a) + str(middle) + str(b)
    return func


def a_preposition_b_default(a, b, **kwargs):
    ensure_definition(a, b, **kwargs)
    if hasattr(a, 'preposition'):
        preposition = word(a.preposition)
    else:
        preposition = word('in the')
    if 'capitalize' in kwargs and kwargs['capitalize']:
        return capitalize(str(a)) + str(' ' + preposition + ' ') + str(b)
    return str(a) + str(' ' + preposition + ' ') + str(b)



in_the = language_function_constructor('in_the')
a_preposition_b = language_function_constructor('a_preposition_b')
a_in_the_b = language_function_constructor('a_in_the_b')
i_subjective = language_function_constructor('i_subjective')
he_subjective = language_function_constructor('he_subjective')
she_subjective = language_function_constructor('she_subjective')
genderless_subjective = language_function_constructor('genderless_subjective')
myself = language_function_constructor('myself')
itself = language_function_constructor('itself')
herself = language_function_constructor('herself')
himself = language_function_constructor('himself')
themselves = language_function_constructor('themselves')
genderless_self = language_function_constructor('genderless_self')
yourself = language_function_constructor('yourself')
yourselves = language_function_constructor('yourselves')
ourselves = language_function_constructor('ourselves')
you_subjective = language_function_constructor('you_subjective')
you_subjective_plural = language_function_constructor('you_subjective_plural')
we_subjective = language_function_constructor('we_subjective')
they_subjective = language_function_constructor('they_subjective')
it_subjective = language_function_constructor('it_subjective')
it_objective = language_function_constructor('it_objective')
them_objective = language_function_constructor('them_objective')
genderless_objective = language_function_constructor('genderless_objective')
me_objective = language_function_constructor('me_objective')
him_objective = language_function_constructor('him_objective')
her_objective = language_function_constructor('her_objective')
our_objective = language_function_constructor('our_objective')
you_objective = language_function_constructor('you_objective')
you_objective_plural = language_function_constructor('you_objective_plural')
us_objective = language_function_constructor('us_objective')
are_we = language_function_constructor('are_we')
are_you = language_function_constructor('are_you')
are_you_plural = language_function_constructor('are_you_plural')
am_i = language_function_constructor('am_i')
her = language_function_constructor('her')
his = language_function_constructor('his')
are_word = language_function_constructor('are_word')
is_word = language_function_constructor('is_word')
their = language_function_constructor('their')
my_possessive = language_function_constructor('my_possessive')
our_possessive = language_function_constructor('our_possessive')
of_the = language_function_constructor('of_the')
your = language_function_constructor('your')
your_plural = language_function_constructor('your_plural')
some = language_function_constructor('some')
its = language_function_constructor('its')
the = language_function_constructor('the')
these = language_function_constructor('these')
this = language_function_constructor('this')
does_a_b = language_function_constructor('does_a_b')
do_a_b = language_function_constructor('do_a_b')
did_a_b = language_function_constructor('did_a_b')
did_a_b_plural = language_function_constructor('did_a_b_plural')
do_i = language_function_constructor('do_i')
do_we = language_function_constructor('do_we')
do_you = language_function_constructor('do_you')
do_you_plural = language_function_constructor('do_you_plural')
did_i = language_function_constructor('did_i')
did_we = language_function_constructor('did_we')
did_you = language_function_constructor('did_you')
did_you_plural = language_function_constructor('did_you_plural')
was_i = language_function_constructor('was_i')
were_we = language_function_constructor('were_we')
were_you = language_function_constructor('were_you')
were_you_plural = language_function_constructor('were_you_plural')
was_a_b = language_function_constructor('was_a_b')
were_a_b = language_function_constructor('were_a_b')
were_a_b_plural = language_function_constructor('were_a_b_plural')
have_i = language_function_constructor('have_i')
have_we = language_function_constructor('have_we')
have_you = language_function_constructor('have_you')
have_you_plural = language_function_constructor('have_you_plural')
has_a_b = language_function_constructor('has_a_b')
have_a_b = language_function_constructor('have_a_b')
verb_past = language_function_constructor('verb_past')
verb_present = language_function_constructor('verb_present')
noun_plural = language_function_constructor('noun_plural')
noun_singular = language_function_constructor('noun_singular')
indefinite_article = language_function_constructor('indefinite_article')
period_list = language_function_constructor('period_list')
name_suffix = language_function_constructor('name_suffix')
possessify = language_function_constructor('possessify')
possessify_long = language_function_constructor('possessify_long')
comma_list = language_function_constructor('comma_list')
comma_and_list = language_function_constructor('comma_and_list')
add_separators = language_function_constructor('add_separators')
quantity_noun = language_function_constructor('quantity_noun')
title_case = language_function_constructor('title_case')
salutation = language_function_constructor('salutation')

if verb_past.__doc__ is None:
    verb_past.__doc__ = """Return the past tense of a verb.

    Args:
        verb (str): The verb to conjugate.
        **kwargs: Optional conjugation parameters passed to the underlying
            language function (e.g. ``'3gp'`` for third-person past tense).

    Returns:
        str: The past-tense form of the verb (e.g. ``verb_past('help')``
            returns ``'helped'``).
    """
if verb_present.__doc__ is None:
    verb_present.__doc__ = """Return the present tense of a verb.

    Args:
        verb (str): The verb to conjugate (may be in any tense).
        **kwargs: Optional conjugation parameters passed to the underlying
            language function (e.g. ``'3sg'`` for third-person singular).

    Returns:
        str: The present-tense form of the verb (e.g.
            ``verb_present('helped', '3sg')`` returns ``'helps'``).
    """
if noun_plural.__doc__ is None:
    noun_plural.__doc__ = """Return the plural form of a noun.

    Args:
        noun (str): The noun to pluralize.
        *pargs: An optional quantity (number, list, dict, or set). When the
            quantity is exactly ``1`` the singular form is returned instead.
        **kwargs: Pass ``noun_is_singular=True`` to skip singularization
            before pluralizing.

    Returns:
        str: The plural form of the noun, or the singular form if the
            optional quantity equals ``1``.
    """
if noun_singular.__doc__ is None:
    noun_singular.__doc__ = """Return the singular form of a noun.

    Args:
        noun (str): The noun to singularize.
        *pargs: An optional quantity (number, list, dict, or set). When the
            quantity is not ``1`` the original noun is returned unchanged.

    Returns:
        str: The singular form of the noun, or the original noun when the
            optional quantity is not ``1``.
    """
if indefinite_article.__doc__ is None:
    indefinite_article.__doc__ = """Return a noun preceded by the appropriate indefinite article.

    Args:
        noun (str): The noun phrase to precede with an article.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: The noun prefixed with ``'a'`` or ``'an'`` as appropriate
            (e.g. ``indefinite_article('apple')`` returns ``'an apple'``).
    """
if capitalize.__doc__ is None:
    capitalize.__doc__ = """Return the input string with the first letter capitalized.

    Args:
        a (str): The string to capitalize.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: The input string with its first character converted to
            upper case.
    """
if period_list.__doc__ is None:
    period_list.__doc__ = """Return a list of per-year period options for use in multiple-choice fields.

    Returns:
        list: A list of ``[number, label]`` pairs representing common
            payment periods (e.g. ``[[12, 'Per Month'], [1, 'Per Year'],
            [52, 'Per Week'], ...]``).
    """
if name_suffix.__doc__ is None:
    name_suffix.__doc__ = """Return a list of common name suffixes for use in multiple-choice fields.

    Returns:
        list: A list of name suffix strings such as
            ``['Jr', 'Sr', 'II', 'III', 'IV', 'V', 'VI']``.
    """
if possessify.__doc__ is None:
    possessify.__doc__ = """Return the possessive phrase combining two arguments.

    Args:
        a: The possessor.
        b: The thing possessed.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: A possessive phrase such as ``"a's b"``.
    """
if possessify_long.__doc__ is None:
    possessify_long.__doc__ = """Return the long possessive phrase combining two arguments.

    Args:
        a: The possessor.
        b: The thing possessed.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: A possessive phrase of the form ``"the b of a"``.
    """
if comma_list.__doc__ is None:
    comma_list.__doc__ = """Return the items joined by commas.

    Args:
        *pargs: Items to join, or a single iterable as the first argument.
        **kwargs: Optional ``comma_string`` (default ``', '``) to customize
            the separator.

    Returns:
        str: The items separated by commas (e.g.
            ``comma_list('lions', 'tigers', 'bears')`` returns
            ``'lions, tigers, bears'``).
    """
if comma_and_list.__doc__ is None:
    comma_and_list.__doc__ = """Return the items joined by commas with "and" before the last item.

    Args:
        *pargs: Items to join, or a single iterable as the first argument.
        **kwargs: Optional keyword arguments including ``oxford`` (bool,
            default ``True``), ``and_string`` (default ``'and'``),
            ``comma_string``, ``before_and``, and ``after_and``.

    Returns:
        str: An English-language listing such as ``'lions, tigers, and
            bears'``.
    """
if add_separators.__doc__ is None:
    add_separators.__doc__ = """Return the list items as strings with separators appended.

    Appends ``;`` to all items except the penultimate, which gets
    ``'; and'``, and the last, which gets ``'.'``.

    Args:
        the_list: The list of items to process.
        separator (str, optional): Separator appended to middle items.
            Defaults to ``';'``.
        last_separator (str, optional): Separator appended to the
            penultimate item. Defaults to ``'; and'``.
        end_mark (str, optional): Mark appended to the final item.
            Defaults to ``'.'``.

    Returns:
        list: A list of strings with separators appended.
    """
if nice_number.__doc__ is None:
    nice_number.__doc__ = """Return a number expressed as a word for small values, or as a formatted numeral.

    Args:
        num: The number to convert.
        **kwargs: Optional keyword arguments including ``capitalize``
            (bool), ``language`` (str), and ``use_word`` (bool, default
            ``False``).

    Returns:
        str: The number as a word (e.g. ``nice_number(4)`` returns
            ``'four'``) or as a locale-formatted numeral for larger values.
    """
if quantity_noun.__doc__ is None:
    quantity_noun.__doc__ = """Return a number combined with a noun in the appropriate singular or plural form.

    Combines :func:`nice_number` and :func:`noun_plural`. Rounds the number
    to the nearest integer unless ``as_integer=False`` is passed.

    Args:
        num: The quantity.
        noun (str): The singular noun.
        **kwargs: Optional keyword arguments including ``as_integer``
            (bool, default ``True``) and other arguments accepted by
            :func:`nice_number`.

    Returns:
        str: The quantity and noun combined (e.g. ``quantity_noun(2,
            'apple')`` returns ``'two apples'``).
    """
if title_case.__doc__ is None:
    title_case.__doc__ = """Return the input string with the first letter of each word capitalized.

    Args:
        a (str): The string to convert to title case.
        **kwargs: Additional keyword arguments passed to the underlying
            language function.

    Returns:
        str: The title-cased string (e.g. ``title_case('the importance of
            being ernest')`` returns ``'The Importance of Being Ernest'``).
    """

language_functions.update({
    'in_the': {
        'en': prefix_constructor('in the ')
    },
    'a_preposition_b': {
        'en': a_preposition_b_default
    },
    'a_in_the_b': {
        'en': middle_constructor(' in the ')
    },
    'i_subjective': {
        'en': lambda *pargs, **kwargs: word('I', **kwargs)
    },
    'he_subjective': {
        'en': lambda *pargs, **kwargs: word('he', **kwargs)
    },
    'she_subjective': {
        'en': lambda *pargs, **kwargs: word('she', **kwargs)
    },
    'genderless_subjective': {
        'en': lambda *pargs, **kwargs: word('they', **kwargs)
    },
    'myself': {
        'en': lambda *pargs, **kwargs: word('myself', **kwargs)
    },
    'itself': {
        'en': lambda *pargs, **kwargs: word('itself', **kwargs)
    },
    'herself': {
        'en': lambda *pargs, **kwargs: word('herself', **kwargs)
    },
    'himself': {
        'en': lambda *pargs, **kwargs: word('himself', **kwargs)
    },
    'themselves': {
        'en': lambda *pargs, **kwargs: word('themselves', **kwargs)
    },
    'genderless_self': {
        'en': lambda *pargs, **kwargs: word('themself', **kwargs)
    },
    'yourself': {
        'en': lambda *pargs, **kwargs: word('yourself', **kwargs)
    },
    'yourselves': {
        'en': lambda *pargs, **kwargs: word('yourselves', **kwargs)
    },
    'ourselves': {
        'en': lambda *pargs, **kwargs: word('ourselves', **kwargs)
    },
    'you_subjective': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'you_subjective_plural': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'we_subjective': {
        'en': lambda *pargs, **kwargs: word('we', **kwargs)
    },
    'they_subjective': {
        'en': lambda *pargs, **kwargs: word('they', **kwargs)
    },
    'it_subjective': {
        'en': lambda *pargs, **kwargs: word('it', **kwargs)
    },
    'it_objective': {
        'en': lambda *pargs, **kwargs: word('it', **kwargs)
    },
    'them_objective': {
        'en': lambda *pargs, **kwargs: word('them', **kwargs)
    },
    'genderless_objective': {
        'en': lambda *pargs, **kwargs: word('them', **kwargs)
    },
    'me_objective': {
        'en': lambda *pargs, **kwargs: word('me', **kwargs)
    },
    'him_objective': {
        'en': lambda *pargs, **kwargs: word('him', **kwargs)
    },
    'her_objective': {
        'en': lambda *pargs, **kwargs: word('her', **kwargs)
    },
    'our_objective': {
        'en': lambda *pargs, **kwargs: word('our', **kwargs)
    },
    'you_objective': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'you_objective_plural': {
        'en': lambda *pargs, **kwargs: word('you', **kwargs)
    },
    'us_objective': {
        'en': lambda *pargs, **kwargs: word('us', **kwargs)
    },
    'are_we': {
        'en': lambda *pargs, **kwargs: word('are we', **kwargs)
    },
    'are_you': {
        'en': lambda *pargs, **kwargs: word('are you', **kwargs)
    },
    'are_you_plural': {
        'en': lambda *pargs, **kwargs: word('are you', **kwargs)
    },
    'am_i': {
        'en': lambda *pargs, **kwargs: word('am I', **kwargs)
    },
    'her': {
        'en': prefix_constructor('her ')
    },
    'his': {
        'en': prefix_constructor('his ')
    },
    'are_word': {
        'en': prefix_constructor('are ')
    },
    'is_word': {
        'en': prefix_constructor('is ')
    },
    'their': {
        'en': prefix_constructor('their ')
    },
    'my_possessive': {
        'en': prefix_constructor('my ')
    },
    'our_possessive': {
        'en': prefix_constructor('our ')
    },
    'of_the': {
        'en': prefix_constructor('of the ')
    },
    'your': {
        'en': prefix_constructor('your ')
    },
    'your_plural': {
        'en': prefix_constructor('your ')
    },
    'some': {
        'en': prefix_constructor('some ')
    },
    'its': {
        'en': prefix_constructor('its ')
    },
    'the': {
        'en': prefix_constructor('the ')
    },
    'these': {
        'en': prefix_constructor('these ')
    },
    'this': {
        'en': prefix_constructor('this ')
    },
    'does_a_b': {
        'en': prefix_constructor_two_arguments('does ')
    },
    'do_a_b': {
        'en': prefix_constructor_two_arguments('do ')
    },
    'did_a_b': {
        'en': prefix_constructor_two_arguments('did ')
    },
    'did_a_b_plural': {
        'en': prefix_constructor_two_arguments('did ')
    },
    'do_i': {
        'en': prefix_constructor('do I ')
    },
    'do_we': {
        'en': prefix_constructor('do we ')
    },
    'do_you': {
        'en': prefix_constructor('do you ')
    },
    'do_you_plural': {
        'en': prefix_constructor('do you ')
    },
    'did_i': {
        'en': prefix_constructor('did I ')
    },
    'did_we': {
        'en': prefix_constructor('did we ')
    },
    'did_you': {
        'en': prefix_constructor('did you ')
    },
    'did_you_plural': {
        'en': prefix_constructor('did you ')
    },
    'was_i': {
        'en': prefix_constructor('was I ')
    },
    'were_we': {
        'en': prefix_constructor('were we ')
    },
    'were_you': {
        'en': prefix_constructor('were you ')
    },
    'were_you_plural': {
        'en': prefix_constructor('were you ')
    },
    'was_a_b': {
        'en': prefix_constructor_two_arguments('was ')
    },
    'were_a_b': {
        'en': prefix_constructor_two_arguments('were ')
    },
    'were_a_b_plural': {
        'en': prefix_constructor_two_arguments('were ')
    },
    'have_i': {
        'en': prefix_constructor('have I ')
    },
    'have_we': {
        'en': prefix_constructor('have we ')
    },
    'have_you': {
        'en': prefix_constructor('have you ')
    },
    'have_you_plural': {
        'en': prefix_constructor('have you ')
    },
    'has_a_b': {
        'en': prefix_constructor_two_arguments('has ')
    },
    'have_a_b': {
        'en': prefix_constructor_two_arguments('have ')
    },
    'verb_past': {
        'en': verb_past_en,
        'es': verb_past_es,
        'de': verb_past_de,
        'fr': verb_past_fr,
        'it': verb_past_it,
        'nl': verb_past_nl
    },
    'verb_present': {
        'en': verb_present_en,
        'es': verb_present_es,
        'de': verb_present_de,
        'fr': verb_present_fr,
        'it': verb_present_it,
        'nl': verb_present_nl
    },
    'noun_plural': {
        'en': noun_plural_en,
        'es': noun_plural_es,
        'de': noun_plural_de,
        'fr': noun_plural_fr,
        'it': noun_plural_it,
        'nl': noun_plural_nl
    },
    'noun_singular': {
        'en': noun_singular_en,
        'es': noun_singular_es,
        'de': noun_singular_de,
        'fr': noun_singular_fr,
        'it': noun_singular_it,
        'nl': noun_singular_nl
    },
    'indefinite_article': {
        'en': indefinite_article_en,
        'es': indefinite_article_es,
        'de': indefinite_article_de,
        'it': indefinite_article_it
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
        'en': possessify_en
    },
    'possessify_long': {
        'en': double_prefix_constructor_reverse('the ', ' of the ')
    },
    'comma_and_list': {
        'en': comma_and_list_en,
        'es': comma_and_list_es,
        'de': comma_and_list_de
    },
    'comma_list': {
        'en': comma_list_en
    },
    'add_separators': {
        'en': add_separators_en
    },
    'nice_number': {
        '*': nice_number_default
    },
    'quantity_noun': {
        '*': quantity_noun_default
    },
    'capitalize': {
        '*': capitalize_default
    },
    'title_case': {
        '*': titlecasestr
    },
    'salutation': {
        '*': salutation_default
    }
})
