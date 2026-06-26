import re
from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    validators,
)
from docassemble.base.language.words import LazyWord as word
from docassemble.webapp.services.validators import html_validator

class APIKey(FlaskForm):
    action = HiddenField()
    key = HiddenField()
    security = HiddenField()
    name = StringField(word('Name'), validators=[validators.Length(min=1, max=255), html_validator])
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
