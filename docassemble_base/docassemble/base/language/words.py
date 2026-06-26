from docassemble.base.thread_context import this_thread
from .capitalization import capitalize

word_collection = {
    'en': {
        'This field is required.': 'You need to fill this in.',
        "Country Code": 'Country Code (e.g., "us")',
        "First Subdivision": 'State Abbreviation (e.g., "NY")',
        "Second Subdivision": "County",
        "Third Subdivision": "Municipality",
    }
}


def words():
    return word_collection[this_thread.language]


class LazyWord:

    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            self.original = args[0] % kwargs
        else:
            self.original = args[0]

    def __mod__(self, other):
        return word(self.original) % other

    def __str__(self):
        return word(self.original)


def word(the_word, **kwargs):
    """Return the word translated into the current language.

    If no translation is found for the current language, the input is
    returned unchanged.  Used throughout docassemble to support
    multilingual interviews.

    Args:
        the_word (str): The word or phrase to translate.
        **kwargs: Optional keyword arguments.  Pass ``language`` to
            look up a translation for a specific language, or
            ``capitalize=True`` to capitalize the result.

    Returns:
        str: The translated (or original) word.
    """
    # Currently, no kwargs are used, but in the future, this function could be
    # expanded to use kwargs.  For example, for languages with gendered words,
    # the gender could be passed as a keyword argument.
    if the_word is True:
        the_word = 'yes'
    elif the_word is False:
        the_word = 'no'
    elif the_word is None:
        the_word = "I don't know"
    if isinstance(the_word, LazyWord):
        the_word = the_word.original
    try:
        the_word = word_collection[kwargs.get('language', this_thread.language)][the_word]
    except:
        the_word = str(the_word)
    if kwargs.get('capitalize', False):
        return capitalize(the_word)
    return the_word


def update_word_collection(lang, defs):
    if lang not in word_collection:
        word_collection[lang] = {}
    for the_word, translation in defs.items():
        if translation is not None:
            word_collection[lang][the_word] = translation
