from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField
from docassemble.base.util import word
from wtforms import validators, ValidationError, StringField, SubmitField, TextAreaField
import re
import sys

def validate_name(form, field):
    if re.search('[^A-Za-z0-9\_]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9, underscore'))

class CreatePackageForm(Form):
    name = StringField(word('Package name'), validators=[
        validators.Required(word('Package name is required')), validate_name])
    submit = SubmitField(word('Get template'))

class UpdatePackageForm(Form):
    #packagename = StringField(word('Package name'), validators=[
    #    validators.Required(word('Package name is required'))])
    giturl = StringField(word('Git URL'))
    zipfile = FileField(word('Zip File'))
    submit = SubmitField(word('Update'))

class ConfigForm(Form):
    config_content = TextAreaField(word('Configuration YAML'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))

class SandboxForm(Form):
    sandbox_content = TextAreaField(word('Sandbox YAML'))
    submit = SubmitField(word('Save'))
    run = SubmitField(word('Save and Run'))
