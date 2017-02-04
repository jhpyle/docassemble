from flask_wtf import FlaskForm
from docassemble.base.functions import word
from wtforms import validators, ValidationError, StringField, SubmitField, TextAreaField, SelectMultipleField, SelectField, FileField
import re
import sys

def validate_name(form, field):
    if re.search('[^A-Za-z0-9\-]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9, hyphen'))

def validate_package_name(form, field):
    if re.search('[^A-Za-z0-9]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9'))

class CreatePackageForm(FlaskForm):
    name = StringField(word('Package name'), validators=[
        validators.Required(word('Package name is required')), validate_name])
    submit = SubmitField(word('Get template'))

class CreatePlaygroundPackageForm(FlaskForm):
    name = SelectField(word('Package'), validators=[
        validators.Required(word('Package name is required')), validate_name])
    submit = SubmitField(word('Get package'))

class UpdatePackageForm(FlaskForm):
    giturl = StringField(word('GitHub URL'))
    zipfile = FileField(word('Zip File'))
    pippackage = StringField(word('Package on PyPI'))
    submit = SubmitField(word('Update'))

class ConfigForm(FlaskForm):
    config_content = TextAreaField(word('Configuration YAML'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))

class PlaygroundForm(FlaskForm):
    original_playground_name = StringField(word('Original Name'))
    playground_name = StringField(word('Name'), [validators.Length(min=1, max=255)])
    playground_content = TextAreaField(word('Playground YAML'))
    search_term = StringField(word('Search'))
    submit = SubmitField(word('Save'))
    run = SubmitField(word('Save and Run'))
    delete = SubmitField(word('Delete'))

class PlaygroundUploadForm(FlaskForm):
    uploadfile = FileField(word('File to upload'))

class LogForm(FlaskForm):
    filter_string = StringField(word('Filter For'))
    file_name = StringField(word('File Name'))
    submit = SubmitField(word('Apply'))
    clear = SubmitField(word('Clear'))

class Utilities(FlaskForm):
    pdffile = FileField(word('PDF File'))
    scan = SubmitField(word('Scan'))
    
class PlaygroundFilesForm(FlaskForm):
    section = StringField(word('Section'))
    uploadfile = FileField(word('File to upload'))
    submit = SubmitField(word('Upload'))

class PlaygroundFilesEditForm(FlaskForm):
    section = StringField(word('Section'))
    original_file_name = StringField(word('Original Name'))
    file_name = StringField(word('Name'), [validators.Length(min=1, max=255)])
    search_term = StringField(word('Search'))
    file_content = TextAreaField(word('File Text'))
    submit = SubmitField(word('Save'))
    delete = SubmitField(word('Delete'))

class PlaygroundPackagesForm(FlaskForm):
    original_file_name = StringField(word('Original Name'))
    file_name = StringField(word('Package Name'), validators=[validators.Length(min=1, max=50),
        validators.Required(word('Package Name is required')), validate_package_name])
    license = StringField(word('License'), default='The MIT License (MIT)', validators=[validators.Length(min=1, max=255)])
    description = TextAreaField(word('Description'), validators=[validators.Length(min=1, max=255)], default="A docassemble extension.")
    version = StringField(word('Version'), validators=[validators.Length(min=1, max=255)], default="0.1")
    url = StringField(word('URL'), validators=[validators.Length(min=1, max=255)], default="http://docassemble.org")
    dependencies = SelectMultipleField(word('Dependencies'))
    interview_files = SelectMultipleField(word('Interview files'))
    template_files = SelectMultipleField(word('Template files'))
    module_files = SelectMultipleField(word('Modules'))
    static_files = SelectMultipleField(word('Static files'))
    sources_files = SelectMultipleField(word('Source files'))
    readme = TextAreaField(word('README file'), default='')
    submit = SubmitField(word('Save'))
    download = SubmitField(word('Download'))
    install = SubmitField(word('Install'))
    delete = SubmitField(word('Delete'))
