from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    SelectField,
    FileField,
)
from docassemble.base.language.words import LazyWord as word
from docassemble.webapp.services.validators import html_validator

class UpdatePackageForm(FlaskForm):
    giturl = StringField(word('GitHub URL'), validators=[html_validator])
    gitbranch = SelectField(word('GitHub Branch'), validators=[html_validator])
    zipfile = FileField(word('Zip File'))
    pippackage = StringField(word('Package on PyPI'), validators=[html_validator])
    submit = SubmitField(word('Update'))
