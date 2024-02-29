from bs4 import BeautifulSoup
from wtforms import ValidationError
from docassemble.base.functions import LazyWord as word


def html_validator(form, field):  # pylint: disable=unused-argument
    """Field must not contain HTML"""
    if field.data is None:
        return
    text = BeautifulSoup(field.data, "html.parser").get_text('')
    if text != field.data:
        raise ValidationError(word('Field cannot contain HTML'))
