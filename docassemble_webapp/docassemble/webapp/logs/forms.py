from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
)
from docassemble.base.language.words import LazyWord as word

class LogForm(FlaskForm):
    filter_string = StringField(word('Filter For'))
    file_name = StringField(word('File Name'))
    submit = SubmitField(word('Apply'))
    clear = SubmitField(word('Clear'))
