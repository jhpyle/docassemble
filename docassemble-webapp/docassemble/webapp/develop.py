from flask.ext.wtf import Form
from docassemble.base.util import word
from wtforms import validators, ValidationError, StringField, SubmitField
import re

def validate_name(form, field):
    if re.search('[^A-Za-z0-9\-]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9, hyphen'))

class CreatePackageForm(Form):
    name = StringField(word('Package name'), validators=[
        validators.Required(word('Package name is required')), validate_name])
    submit = SubmitField(word('Get template'))

class UpdatePackageForm(Form):
    packagename = StringField(word('Package name'), validators=[
        validators.Required(word('Package name is required'))])
    giturl = StringField(word('Git URL'), validators=[
        validators.Required(word('Git URL is required'))])
    submit = SubmitField(word('Update'))
