import re
from flask_wtf import FlaskForm
from docassemble.base.functions import LazyWord as word
from wtforms import validators, ValidationError, StringField, SubmitField, TextAreaField, SelectMultipleField, SelectField, FileField, HiddenField, RadioField, BooleanField

class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass

def validate_project_name(form, field):
    if re.search('^[0-9]', field.data):
        raise ValidationError(word('Project name cannot begin with a number'))
    if re.search('[^A-Za-z0-9]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9'))

def validate_name(form, field):
    if re.search('[^A-Za-z0-9\-]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9, hyphen'))

def validate_package_name(form, field):
    if re.search('[^A-Za-z0-9]', field.data):
        raise ValidationError(word('Valid characters are: A-Z, a-z, 0-9'))

class CreatePackageForm(FlaskForm):
    name = StringField(word('Package name'), validators=[
        validators.DataRequired(word('Package name is required')), validate_name])
    submit = SubmitField(word('Get template'))

class CreatePlaygroundPackageForm(FlaskForm):
    name = SelectField(word('Package'), validators=[
        validators.DataRequired(word('Package name is required')), validate_name])
    submit = SubmitField(word('Get package'))

class UpdatePackageForm(FlaskForm):
    giturl = StringField(word('GitHub URL'))
    gitbranch = SelectField(word('GitHub Branch'))
    zipfile = FileField(word('Zip File'))
    pippackage = StringField(word('Package on PyPI'))
    submit = SubmitField(word('Update'))

class ConfigForm(FlaskForm):
    config_content = TextAreaField(word('Configuration YAML'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))

class PlaygroundForm(FlaskForm):
    status = StringField('Status')
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
    pdfdocxfile = FileField(word('PDF/DOCX File'))
    scan = SubmitField(word('Scan'))
    interview = StringField(word('Interview'))
    interview_submit = SubmitField(word('Download'))
    language = StringField(word('Language'))
    tr_language = StringField(word('Language'))
    systemfiletype = SelectField(word('Output Format'))
    filetype = SelectField(word('Output Format'))
    language_submit = SubmitField(word('Translate'))
    officeaddin_version = StringField(word('Version'), default='0.0.0.1')
    officeaddin_submit = SubmitField(word('Download'))

class PlaygroundFilesForm(FlaskForm):
    purpose = StringField('Purpose')
    section = StringField(word('Section'))
    uploadfile = FileField(word('File to upload'))
    submit = SubmitField(word('Upload'))

class PlaygroundFilesEditForm(FlaskForm):
    purpose = StringField('Purpose')
    section = StringField(word('Section'))
    original_file_name = StringField(word('Original Name'))
    file_name = StringField(word('Name'), [validators.Length(min=1, max=255)])
    search_term = StringField(word('Search'))
    file_content = TextAreaField(word('File Text'))
    active_file = StringField(word('Active File'))
    submit = SubmitField(word('Save'))
    delete = SubmitField(word('Delete'))

class RenameProject(FlaskForm):
    name = StringField(word('New Name'), validators=[
        validators.DataRequired(word('Project name is required')), validate_project_name])
    submit = SubmitField(word('Rename'))

class DeleteProject(FlaskForm):
    submit = SubmitField(word('Delete'))

class NewProject(FlaskForm):
    name = StringField(word('Name'), validators=[
        validators.DataRequired(word('Project name is required')), validate_project_name])
    submit = SubmitField(word('Save'))

class PullPlaygroundPackage(FlaskForm):
    github_url = StringField(word('GitHub URL'))
    github_branch = SelectField(word('GitHub Branch'))
    pypi = StringField(word('PyPI package'))
    pull = SubmitField(word('Pull'))
    cancel = SubmitField(word('Cancel'))

class PlaygroundPackagesForm(FlaskForm):
    original_file_name = StringField(word('Original Name'))
    file_name = StringField(word('Package Name'), validators=[validators.Length(min=1, max=50),
        validators.DataRequired(word('Package Name is required')), validate_package_name])
    license = StringField(word('License'), default='The MIT License (MIT)', validators=[validators.Length(min=0, max=255)])
    author_name = StringField(word('Author Name'), validators=[validators.Length(min=0, max=255)])
    author_email = StringField(word('Author E-mail'), validators=[validators.Length(min=0, max=255)])
    description = StringField(word('Description'), validators=[validators.Length(min=0, max=255)], default="A docassemble extension.")
    version = StringField(word('Version'), validators=[validators.Length(min=0, max=255)], default="0.0.1")
    url = StringField(word('URL'), validators=[validators.Length(min=0, max=255)], default="")
    dependencies = SelectMultipleField(word('Dependencies'))
    interview_files = SelectMultipleField(word('Interview files'))
    template_files = SelectMultipleField(word('Template files'))
    module_files = SelectMultipleField(word('Modules'))
    static_files = SelectMultipleField(word('Static files'))
    sources_files = SelectMultipleField(word('Source files'))
    readme = TextAreaField(word('README file'), default='')
    github_branch = NonValidatingSelectField(word('Branch'))
    github_branch_new = StringField(word('Name of new branch'))
    commit_message = StringField(word('Commit message'), default="")
    pypi_also = BooleanField(word('Publish on PyPI also'))
    install_also = BooleanField(word('Install package on this server also'))
    submit = SubmitField(word('Save'))
    download = SubmitField(word('Download'))
    install = SubmitField(word('Install'))
    pypi = SubmitField(word('PyPI'))
    github = SubmitField(word('GitHub'))
    cancel = SubmitField(word('Cancel'))
    delete = SubmitField(word('Delete'))

class GoogleDriveForm(FlaskForm):
    folder = SelectField(word('Folder'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))

class OneDriveForm(FlaskForm):
    folder = SelectField(word('Folder'))
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))

class GitHubForm(FlaskForm):
    shared = BooleanField(word('Access shared repositories'))
    orgs = BooleanField(word('Access organizational repositories'))
    save = SubmitField(word('Save changes'))
    configure = SubmitField(word('Configure'))
    unconfigure = SubmitField(word('Disable'))
    cancel = SubmitField(word('Back to profile'))

class TrainingForm(FlaskForm):
    the_package = HiddenField()
    the_file = HiddenField()
    the_group_id = HiddenField()
    show_all = HiddenField()
    submit = SubmitField(word('Save'))
    cancel = SubmitField(word('Cancel'))

class TrainingUploadForm(FlaskForm):
    usepackage = RadioField(word('Use Package'))
    jsonfile = FileField(word('JSON file'))
    importtype = RadioField(word('Import method'))
    submit = SubmitField(word('Import'))

class AddinUploadForm(FlaskForm):
    content = HiddenField()
    filename = HiddenField()

class FunctionFileForm(FlaskForm):
    pass

class APIKey(FlaskForm):
    action = HiddenField()
    key = HiddenField()
    security = HiddenField()
    name = StringField(word('Name'), validators=[validators.Length(min=1, max=255)])
    method = SelectField(word('Security Method'))
    permissions = SelectMultipleField(word('Limited Permissions'))
    submit = SubmitField(word('Create'))
    delete = SubmitField(word('Delete'))
    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators=extra_validators)
        if not rv:
            return False
        if self.action.data not in ('edit', 'new'):
            return False
        has_error = False
        if self.action.data in ('edit', 'new'):
            if (not isinstance(self.name.data, str)) or not re.search(r'[A-Za-z0-9]', self.name.data):
                self.name.errors.append(word("The name must be filled in."))
                has_error = True
            if (not isinstance(self.method.data, str)) or self.method.data not in ('referer', 'ip', 'none'):
                self.name.errors.append(word("You must select an option."))
                has_error = True
        if has_error:
            return False
        return True
