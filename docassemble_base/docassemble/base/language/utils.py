from docassemble.base.language.core import ensure_definition

def fix_punctuation(text, mark=None, other_marks=None):
    """Ensure the text ends with a punctuation mark, adding one if necessary.

    Args:
        text (str): The text to check.
        mark (str, optional): The punctuation mark to append if none is
            present. Defaults to ``'.'``.
        other_marks (list, optional): A list of punctuation marks that are
            considered acceptable endings. Defaults to ``['.', '?', '!']``.

    Returns:
        str: The text, possibly with a punctuation mark appended.
    """
    ensure_definition(text, mark, other_marks)
    if other_marks is None:
        other_marks = ['.', '?', '!']
    if not isinstance(other_marks, list):
        other_marks = list(other_marks)
    if mark is None:
        mark = '.'
    text = text.rstrip()
    if mark == '':
        return text
    for end_mark in set([mark] + other_marks):
        if text.endswith(end_mark):
            return text
    return text + mark
