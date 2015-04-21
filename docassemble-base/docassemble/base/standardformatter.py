from docassemble.base.util import word, currency_symbol
from docassemble.base.filter import markdown_to_html
from docassemble.base.parse import Question
import urllib
def question_name_tag(question):
    if question.name:
        return('<input type="hidden" name="questionname" value="' + question.name + '"></input>')
    return('')
def as_html(status, validation_rules, debug):
    output = ""
    output += '<section id="question" class="tab-pane active col-md-6">'
    if status.question.question_type == "yesno":
        output += '<form id="daform" method="POST"><fieldset>'
        output += question_name_tag(status.question)
        output += '<div class="page-header"><h3>' + markdown_to_html(status.questionText, trim=True) + '</h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText) + '</div>'
        output += '<div class="btn-toolbar"><button class="btn btn-primary btn-lg " name="' + status.question.fields[0].saveas + '" type="submit" value="True">Yes</button> <button class="btn btn-lg btn-info" name="' + status.question.fields[0].saveas + '" type="submit" value="False">No</button></div>'
        output += '</fieldset></form>'
    elif status.question.question_type == "noyes":
        output += '<form id="daform" method="POST"><fieldset>'
        output += question_name_tag(status.question)
        output += '<div class="page-header"><h3>' + markdown_to_html(status.questionText, trim=True) + '</h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText) + '</div>'
        output += '<div class="btn-toolbar"><button class="btn btn-primary btn-lg" name="' + status.question.fields[0].saveas + '" type="submit" value="False">Yes</button> <button class="btn btn-lg btn-info" name="' + status.question.fields[0].saveas + '" type="submit" value="True">No</button></div>'
        output += '</fieldset></form>'
    elif status.question.question_type == "fields":
        enctype_string = ""
        fieldlist = list()
        checkboxes = list()
        files = list()
        for field in status.question.fields:
            if field.required:
                validation_rules['rules'][field.saveas] = {'required': True}
                validation_rules['messages'][field.saveas] = {'required': word("This field is required.")}
            else:
                validation_rules['rules'][field.saveas] = {'required': False}
            if field.datatype == 'date':
                validation_rules['rules'][field.saveas]['date'] = True
                validation_rules['messages'][field.saveas]['date'] = word("You need to enter a valid date.")
            if field.datatype == 'email':
                validation_rules['rules'][field.saveas]['email'] = True
                validation_rules['messages'][field.saveas]['email'] = word("You need to enter a complete e-mail address.")
            if field.datatype == 'number' or field.datatype == 'currency':
                validation_rules['rules'][field.saveas]['number'] = True
                validation_rules['messages'][field.saveas]['number'] = word("You need to enter a number.")
            if field.datatype == 'file':
                enctype_string = ' enctype="multipart/form-data"'
                files.append(field.saveas)
            if field.datatype == 'yesno':
                checkboxes.append(field.saveas)
                fieldlist.append('<div class="form-group"><div class="col-sm-12"><div class="checkbox"><label>' + input_for(status, field) + '</label></div></div></div>')
            else:
                fieldlist.append('<div class="form-group"><label for="' + field.saveas + '" class="control-label col-sm-4">' + field.label + '</label><div class="col-sm-8">' + input_for(status, field) + '</div></div>')
        output += '<form id="daform" class="form-horizontal" method="POST"' + enctype_string + '><fieldset>'
        output += question_name_tag(status.question)
        output += '<div class="page-header"><h3>' + markdown_to_html(status.questionText, trim=True) + '</h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText) + '</div>'
        if (len(fieldlist)):
            output += "".join(fieldlist)
        else:
            output += "<p>Error: no fields</p>"
        if len(checkboxes):
            output += '<input type="hidden" name="checkboxes" value="' + ",".join(checkboxes) + '"></input>'
        if len(files):
            output += '<input type="hidden" name="files" value="' + ",".join(files) + '"></input>'
        output += '<div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">Continue</button></div>'
        output += '</fieldset></form>'
    elif status.question.question_type == "multiple_choice":
        output += '<form id="daform" method="POST"><fieldset>'
        output += question_name_tag(status.question)
        output += '<div class="page-header"><h3>' + markdown_to_html(status.questionText, trim=True) + '</h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText) + '</div>'
        output += '<div id="errorcontainer" style="display:none"></div>'
        validation_rules['errorClass'] = "alert alert-error"
        validation_rules['errorLabelContainer'] = "#errorcontainer"
        if status.question.question_variety == "radio":
            if hasattr(status.question.fields[0], 'saveas'):
                for choice in status.question.fields[0].choices:
                    for key in choice:
                        output += '<div class="radio"><label><input name="' + status.question.fields[0].saveas + '" type="radio" value="' + choice[key] + '"> ' + key + '</label></div>'
                validation_rules['rules'][status.question.fields[0].saveas] = {'required': True}
                validation_rules['messages'][status.question.fields[0].saveas] = {'required': word("You need to select one.")}
            else:
                indexno = 0
                for choice in status.question.fields[0].choices:
                    for key in choice:
                        output += '<div class="radio"><label><input name="multiple_choice" type="radio" value="' + str(indexno) + '"> ' + key + '</label></div>'
                    indexno += 1
                    validation_rules['rules']['multiple_choice'] = {'required': True}
                    validation_rules['messages']['multiple_choice'] = {'required': word("You need to select one.")}
            output += '<br><button class="btn btn-lg btn-primary" type="submit">Continue</button>'
        else:
            output += '<div class="btn-toolbar">'
            if hasattr(status.question.fields[0], 'saveas'):
                for choice in status.question.fields[0].choices:
                    for key in choice:
                        output += '<button type="submit" class="btn btn-lg' + btn_class + '" name="' + status.question.fields[0].saveas + '" value="' + choice[key] + '"> ' + key + '</button> '
            else:
                indexno = 0
                for choice in status.question.fields[0].choices:
                    for key in choice:
                        btn_class = ''
                        if isinstance(choice[key], Question) and choice[key].question_type in ["exit", "continue", "restart"]:
                            if choice[key].question_type == "continue":
                                btn_class = ' btn-primary'
                            elif choice[key].question_type == "restart":
                                btn_class = ' btn-warning'
                            elif choice[key].question_type == "exit":
                                btn_class = ' btn-danger'
                        output += '<button type="submit" class="btn btn-lg' + btn_class + '" name="multiple_choice" value="' + str(indexno) + '"> ' + key + '</button> '
                    indexno += 1
            output += '</div>'
        output += '</fieldset></form>'
    else:
        output += '<form id="daform" class="form-horizontal" method="POST"><fieldset>'
        output += question_name_tag(status.question)
        output += '<div class="page-header"><h3>' + markdown_to_html(status.questionText, trim=True) + '</h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText) + '</div>'
        output += '<div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">Continue</button></div>'
        output += '</fieldset></form>'
    if len(status.attachments) > 0:
        output += '<br>'
        if len(status.attachments) > 1:
            output += '<div class="alert alert-success" role="alert">' + word('attachment_message_plural') + '</div>'
        else:
            output += '<div class="alert alert-success" role="alert">' + word('attachment_message_singular') + '</div>'
        attachment_index = 0
        for attachment in status.attachments:
            if debug:
                show_markdown = True
            else:
                show_markdown = False
            if 'pdf' in attachment['valid_formats'] or 'rtf' in attachment['valid_formats'] or (debug and 'tex' in attachment['valid_formats']) or '*' in attachment['valid_formats']:
                show_download = True
            else:
                show_download = False                
            if 'html' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                show_preview = True
            else:
                show_preview = False
            if len(attachment['valid_formats']) > 1 or '*' in attachment['valid_formats']:
                multiple_formats = True
            else:
                multiple_formats = False
            output += '<div><h3>' + attachment['name'] + '</h3></div>'
            output += '<div class="tabbable"><ul class="nav nav-tabs">'
            if show_download:
                output += '<li class="active"><a href="#download' + str(attachment_index) + '" data-toggle="tab">' + word('Download') + '</a></li>'
            if show_preview:
                output += '<li><a href="#preview' + str(attachment_index) + '" data-toggle="tab">' + word('Preview') + '</a></li>'
            if show_markdown:
                output += '<li><a href="#markdown' + str(attachment_index) + '" data-toggle="tab">' + word('Markdown') + '</a></li>'
            output += '</ul><div class="tab-content">'
            if show_download:
                output += '<div class="tab-pane active" id="download' + str(attachment_index) + '">'
                if multiple_formats:
                    output += '<p>' + word('save_as_multiple') + '</p>'
                else:
                    output += '<p>' + word('save_as_singular') + '</p>'
                if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '<p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=pdf"><i class="glyphicon glyphicon-print"></i> PDF</a> (' + word('pdf_message') + ')</p>'
                if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '<p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=rtf"><i class="glyphicon glyphicon-pencil"></i> RTF</a> (' + word('rtf_message') + ')</p>'
                if debug and ('tex' in attachment['valid_formats'] or '*' in attachment['valid_formats']):
                    output += '<p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=tex"><i class="glyphicon glyphicon-pencil"></i> LaTeX</a> (' + word('tex_message') + ')</p>'
                output += '</div>'
            if show_preview:
                output += '<div class="tab-pane" id="preview' + str(attachment_index) + '">'
                output += '<blockquote>' + str(attachment['content']['html']) + '</blockquote>'
                output += '</div>'
            if show_markdown:
                output += '<div class="tab-pane" id="markdown' + str(attachment_index) + '">'
                output += '<pre>' + str(attachment['markdown']['html']) + '</pre>'
                output += '</div>'
            output += '</div></div>'
            attachment_index += 1
    output += '</section>'
    output += '<section id="help" class="tab-pane">'
    for help_section in status.helpText:
        if help_section['heading'] is not None:
            output += '<div class="page-header"><h3>' + help_section['heading'] + '</h3></div>'
        output += markdown_to_html(help_section['content'])
    output += '</section>'
    return output

def input_for(status, field):
    output = ""
    if field.saveas in status.defaults:
        defaultvalue = unicode(status.defaults[field.saveas])
    else:
        defaultvalue = None
    if field.saveas in status.hints:
        placeholdertext = ' placeholder="' + unicode(status.hints[field.saveas]) + '"'
    else:
        placeholdertext = ''
    if field.datatype == 'selectcompute':
        output += '<select name="' + field.saveas + '" id="' + field.saveas + '" >'
        output += '<option name="' + field.saveas + '" id="' + field.saveas + '" value="">' + word('Select...') + '</option>'
        for pair in status.selectcompute[field.saveas]:
            output += '<option value="' + unicode(pair[0]) + '"'
            if defaultvalue is not None and unicode(pair[0]) == defaultvalue:
                output += 'selected="selected"'
            output += '>' + unicode(pair[1]) + '</option>'
        output += '</select> '
    elif field.datatype == 'selectmanual':
        output += '<select name="' + field.saveas + '" id="' + field.saveas + '" >'
        output += '<option value="">' + word('Select...') + '</option>'
        for pair in field.selections:
            output += '<option value="' + unicode(pair[0]) + '"'
            if defaultvalue is not None and unicode(pair[0]) == defaultvalue:
                output += 'selected="selected"'
            output += '>' + unicode(pair[1]) + '</option>'
        output += '</select> '
    elif field.datatype == 'yesno':
        output += '<input type="checkbox" value="True" name="' + field.saveas + '" id="' + field.saveas + '"'
        if defaultvalue:
            output += ' checked'
        output += '> ' + field.label
    elif field.datatype == 'file':
        output += '<div class="fileinput fileinput-new input-group" data-provides="fileinput"><div class="form-control" data-trigger="fileinput"><i class="glyphicon glyphicon-file fileinput-exists"></i><span class="fileinput-filename"></span></div><span class="input-group-addon btn btn-default btn-file"><span class="fileinput-new">' + word('Select file') + '</span><span class="fileinput-exists">' + word('Change') + '</span><input type="file" name="' + field.saveas + '" id="' + field.saveas + '"></span><a href="#" class="input-group-addon btn btn-default fileinput-exists" data-dismiss="fileinput">' + word('Remove') + '</a></div>'
    elif field.datatype == 'area':
        output += '<textarea class="form-control" rows="4" name="' + field.saveas + '" id="' + field.saveas + '"' + placeholdertext + '>'
        if defaultvalue is not None:
            output += defaultvalue
        output += '</textarea>'
    else:
        if defaultvalue is not None:
            defaultstring = ' value="' + defaultvalue + '"'
        else:
            defaultstring = ''
        input_type = field.datatype
        if field.datatype == 'currency':
            input_type = 'number'
            output += '<div class="input-group"><span class="input-group-addon" id="addon-' + field.saveas + '">' + currency_symbol() + '</span>'
        output += '<input' + defaultstring + placeholdertext + ' class="form-control" type="' + input_type + '" name="' + field.saveas + '" id="' + field.saveas + '"'
        if field.datatype == 'currency':
            output += ' aria-describedby="addon-' + field.saveas + '"></input></div>'
        else:
            output += '></input>'
    return output
