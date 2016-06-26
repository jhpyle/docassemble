from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField
from docassemble.base.util import word
from wtforms import validators, ValidationError, StringField, SubmitField, TextAreaField, SelectMultipleField
import re
import sys

def validate_name(form, field):
    if re.search('[^A-Za-z0-9\-]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9, hyphen'))

def validate_package_name(form, field):
    if re.search('[^A-Za-z0-9]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9'))

class CreatePackageForm(Form):
    name = StringField(word('Package name'), validators=[
        validators.Required(word('Package name is required')), validate_name])
    submit = SubmitField(word('Get template'))

class UpdatePackageForm(Form):
    giturl = StringField(word('Git URL'))
    zipfile = FileField(word('Zip File'))
    pippackage = StringField(word('Package on PyPI'))
    submit = SubmitField(word('Update'))

class ConfigForm(Form):
    config_content = TextAreaField(word('Configuration YAML'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))

class PlaygroundForm(Form):
    original_playground_name = StringField(word('Original Name'))
    playground_name = StringField(word('Name'), [validators.Length(min=1, max=255)])
    playground_content = TextAreaField(word('Playground YAML'))
    submit = SubmitField(word('Save'))
    run = SubmitField(word('Save and Run'))
    delete = SubmitField(word('Delete'))

class LogForm(Form):
    filter_string = StringField(word('Filter For'))
    file_name = StringField(word('File Name'))
    submit = SubmitField(word('Apply'))
    clear = SubmitField(word('Clear'))

class Utilities(Form):
    pdffile = FileField(word('PDF File'))
    scan = SubmitField(word('Scan'))
    
class PlaygroundFilesForm(Form):
    section = StringField(word('Section'))
    uploadfile = FileField(word('File to upload'))
    submit = SubmitField(word('Upload'))

class PlaygroundFilesEditForm(Form):
    section = StringField(word('Section'))
    original_file_name = StringField(word('Original Name'))
    file_name = StringField(word('Name'), [validators.Length(min=1, max=255)])
    file_content = TextAreaField(word('File Text'))
    submit = SubmitField(word('Save'))

class PlaygroundPackagesForm(Form):
    original_file_name = StringField(word('Original Name'))
    file_name = StringField(word('Package Name'), validators=[validators.Length(min=1, max=50),
        validators.Required(word('Package Name is required')), validate_package_name])
    license = StringField(word('License'), default='MIT', validators=[validators.Length(min=1, max=255)])
    description = TextAreaField(word('Description'), validators=[validators.Length(min=1, max=255)], default="A docassemble extension.")
    dependencies = SelectMultipleField(word('Dependencies'))
    interview_files = SelectMultipleField(word('Interview Files'))
    template_files = SelectMultipleField(word('Template Files'))
    module_files = SelectMultipleField(word('Module Files'))
    static_files = SelectMultipleField(word('Static Files'))
    submit = SubmitField(word('Save'))
