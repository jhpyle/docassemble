from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, HiddenField, RadioField
from docassemble.base.language.words import LazyWord as word

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
