from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
)
from docassemble.base.language.words import LazyWord as word


class ConfigForm(FlaskForm):
    config_content = TextAreaField(word('Configuration YAML'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))


class InterviewsListForm(FlaskForm):
    i = StringField()
    session = StringField()
    tags = StringField()
    delete = SubmitField()
    delete_all = SubmitField()
