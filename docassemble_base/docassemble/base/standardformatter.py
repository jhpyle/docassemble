from docassemble.base.util import word, currency_symbol
import docassemble.base.filter
from docassemble.base.filter import markdown_to_html
from docassemble.base.parse import Question, debug
import urllib
import sys
import os
import re
import mimetypes
import json
import random
import sys
import codecs

noquote_match = re.compile(r'"')

def tracker_tag(status):
    output = ''
    if status.question.name:
        output += '<input type="hidden" name="_questionname" value="' + status.question.name + '">'
    output += '<input type="hidden" name="_tracker" value="' + str(status.tracker) + '">'
    return output

def datatype_tag(datatypes):
    if len(datatypes):
        return('<input type="hidden" name="_datatypes" value=' + myb64quote(json.dumps(datatypes)) + '>')
    return ('')

# def question_name_tag(question):
#     if question.name:
#         return('<input type="hidden" name="_questionname" value="' + question.name + '">')
#     return('')

def icon_html(status, name, width_value=1.0, width_units='em'):
    the_image = status.question.interview.images.get(name, None)
    if the_image is None:
        return('')
    url = docassemble.base.filter.url_finder(str(the_image.package) + ':' + str(the_image.filename))
    sizing = 'width:' + str(width_value) + str(width_units) + ';'
    filename = docassemble.base.filter.file_finder(str(the_image.package) + ':' + str(the_image.filename))
    if 'extension' in filename and filename['extension'] == 'svg':
        if filename['width'] and filename['height']:
            sizing += 'height:' + str(width_value * (filename['height']/filename['width'])) + str(width_units) + ';'
    else:
        sizing += 'height:auto;'    
    return('<img src="' + url + '" style="image-orientation:from-image;' + sizing + '"> ')

def signature_html(status, debug, root):
    output = '<div id="page"><div class="header" id="header"><a id="new" class="navbtn nav-left">' + word('Clear') + '</a><a id="save" class="navbtn nav-right">' + word('Done') + '</a><div class="title">' + word('Sign Your Name') + '</div></div><div class="toppart" id="toppart">'
    if status.questionText:
        output += markdown_to_html(status.questionText, trim=True)
    output += '</div>'
    if status.subquestionText:
        output += '<div>' + markdown_to_html(status.subquestionText) + '</div>'
    output += '<div id="content"><p style="text-align:center;border-style:solid;border-width:1px">' + word('Loading.  Please wait . . . ') + '</p></div><div class="bottompart" id="bottompart">'
    if (status.underText):
        output += markdown_to_html(status.underText, trim=True)
    output += '</div></div><form action="' + root + '" id="daform" method="POST"><input type="hidden" name="_saveas" value="' + status.question.fields[0].saveas + '"><input type="hidden" id="_theImage" name="_theImage" value=""><input type="hidden" id="_success" name="_success" value="0">'
    #output += question_name_tag(status.question)
    output += tracker_tag(status)
    output += '</form>'
    return output

def as_html(status, extra_scripts, extra_css, url_for, debug, root):
    decorations = list()
    datatypes = dict()
    validation_rules = {'rules': {}, 'messages': {}, 'errorClass': 'help-inline'}
    if status.question.script is not None:
        extra_scripts.append(status.question.script)
    if status.decorations is not None:
        #sys.stderr.write("yoo1\n")
        for decoration in status.decorations:
            #sys.stderr.write("yoo2\n")
            if 'image' in decoration:
                #sys.stderr.write("yoo3\n")
                the_image = status.question.interview.images.get(decoration['image'], None)
                if the_image is not None:
                    #sys.stderr.write("yoo4\n")
                    url = docassemble.base.filter.url_finder(str(the_image.package) + ':' + str(the_image.filename))
                    width_value = 2.0
                    width_units = 'em'
                    sizing = 'width:' + str(width_value) + str(width_units) + ';'
                    filename = docassemble.base.filter.file_finder(str(the_image.package) + ':' + str(the_image.filename))
                    if 'extension' in filename and filename['extension'] == 'svg':
                        if filename['width'] and filename['height']:
                            sizing += 'height:' + str(width_value * (filename['height']/filename['width'])) + str(width_units) + ';'
                    else:
                        sizing += 'height:auto;'    
                    if url is not None:
                        #sys.stderr.write("yoo5\n")
                        if the_image.attribution is not None:
                            #sys.stderr.write("yoo6\n")
                            status.attributions.add(the_image.attribution)
                        decorations.append('<img style="image-orientation:from-image;float:right;' + sizing + '" src="' + url + '">')
    if len(decorations):
        decoration_text = decorations[0];
    else:
        decoration_text = ''
    output = ""
    output += '<section id="question" class="tab-pane active col-md-6">'
    if status.question.question_type == "yesno":
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += '<form action="' + root + '" id="daform" method="POST"><fieldset>'
        output += '<div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status) + '<div style="clear:both"></div></h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText, status=status) + '</div>'
        output += '<div class="btn-toolbar"><button class="btn btn-primary btn-lg " name="' + status.question.fields[0].saveas + '" type="submit" value="True">Yes</button> <button class="btn btn-lg btn-info" name="' + status.question.fields[0].saveas + '" type="submit" value="False">No</button></div>'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '</fieldset></form>'
    elif status.question.question_type == "noyes":
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += '<form action="' + root + '" id="daform" method="POST"><fieldset>'
        output += '<div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status) + '<div style="clear:both"></div></h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText, status=status) + '</div>'
        output += '<div class="btn-toolbar"><button class="btn btn-primary btn-lg" name="' + status.question.fields[0].saveas + '" type="submit" value="False">Yes</button> <button class="btn btn-lg btn-info" name="' + status.question.fields[0].saveas + '" type="submit" value="True">No</button></div>'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '</fieldset></form>'
    elif status.question.question_type == "fields":
        enctype_string = ""
        fieldlist = list()
        checkboxes = list()
        files = list()
        checkbox_validation = False
        for field in status.question.fields:
            if hasattr(field, 'extras'):
                if 'script' in field.extras and 'script' in status.extras:
                    extra_scripts.append(status.extras['script'][field.number])
                if 'css' in field.extras and 'css' in status.extras:
                    extra_css.append(status.extras['css'][field.number])
                #fieldlist.append("<div>datatype is " + str(field.datatype) + "</div>")
            if hasattr(field, 'datatype'):
                if field.datatype == 'html':
                    fieldlist.append('<div class="form-group"><div class="col-md-12">' + status.extras['html'][field.number] + '</div></div>')
                    continue
                elif field.datatype == 'note':
                    fieldlist.append('<div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status) + '</div></div>')
                    continue
                elif field.datatype in ['script', 'css']:
                    continue
                else:
                    datatypes[field.saveas] = field.datatype
            if field.number in status.helptexts:
                helptext_start = '<a style="cursor:pointer;color:#408E30" data-container="body" data-toggle="popover" data-placement="bottom" data-content="' + noquote(unicode(status.helptexts[field.number])) + '">' 
                helptext_end = '</a>'
            else:
                helptext_start = ''
                helptext_end = ''
            if field.required:
                #sys.stderr.write(field.datatype + "\n")
                validation_rules['rules'][field.saveas] = {'required': True}
                validation_rules['messages'][field.saveas] = {'required': word("This field is required.")}
            else:
                validation_rules['rules'][field.saveas] = {'required': False}
            if hasattr(field, 'datatype'):
                if field.datatype == 'date':
                    validation_rules['rules'][field.saveas]['date'] = True
                    validation_rules['messages'][field.saveas]['date'] = word("You need to enter a valid date.")
                if field.datatype == 'email':
                    validation_rules['rules'][field.saveas]['email'] = True
                    if field.required:
                        validation_rules['rules'][field.saveas]['notEmpty'] = True
                        validation_rules['messages'][field.saveas]['notEmpty'] = word("This field is required.")
                    validation_rules['messages'][field.saveas]['email'] = word("You need to enter a complete e-mail address.")
                if field.datatype in ['number', 'currency', 'float', 'integer']:
                    validation_rules['rules'][field.saveas]['number'] = True
                    validation_rules['messages'][field.saveas]['number'] = word("You need to enter a number.")
                if (field.datatype in ['files', 'file']):
                    enctype_string = ' enctype="multipart/form-data"'
                    files.append(field.saveas)
                if field.datatype in ['yesno', 'yesnowide']:
                    checkboxes.append(field.saveas)
                elif field.datatype == 'checkboxes':
                    if field.choicetype == 'compute':
                        pairlist = list(status.selectcompute[field.number])
                    elif field.choicetype == 'manual':
                        pairlist = list(field.selections)
                    else:
                        pairlist = list()
                    if hasattr(field, 'shuffle') and field.shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if pair[0] is not None:
                            checkboxes.append(field.saveas + "[" + myb64quote(pair[0]) + "]")
            if hasattr(field, 'label'):
                if field.label == 'no label':
                    fieldlist.append('<div class="form-group"><div class="col-md-12">' + input_for(status, field, wide=True) + '</div></div>')
                elif hasattr(field, 'datatype') and field.datatype == 'yesnowide':
                    fieldlist.append('<div class="row"><div class="col-md-12">' + input_for(status, field) + '</div></div>')
                elif hasattr(field, 'datatype') and field.datatype == 'yesno':
                    fieldlist.append('<div class="form-group"><div class="col-sm-offset-4 col-sm-8">' + input_for(status, field) + '</div></div>')
                else:
                    fieldlist.append('<div class="form-group"><label for="' + field.saveas + '" class="control-label col-sm-4">' + helptext_start + field.label + helptext_end + '</label><div class="col-sm-8">' + input_for(status, field) + '</div></div>')
        output += '<form action="' + root + '" id="daform" class="form-horizontal" method="POST"' + enctype_string + '><fieldset>'
        output += '<div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status) + '<div style="clear:both"></div></h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText, status=status) + '</div>'
        #output += '<div class="row">'
        if (len(fieldlist)):
            output += "".join(fieldlist)
        else:
            output += "<p>Error: no fields</p>"
        #output += '</div>'
        if len(checkboxes):
            output += '<input type="hidden" name="_checkboxes" value=' + myb64quote(json.dumps(checkboxes)) + '>'
        if len(files):
            output += '<input type="hidden" name="_files" value=' + myb64quote(json.dumps(files)) + '>'
            init_string = '<script>'
            for saveasname in files:
                init_string += '$("#' + saveasname + '").fileinput();' + "\n"
            init_string += '</script>'
            extra_scripts.append('<script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>' + init_string)
            #extra_css.append('<link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />')
        output += '<div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">' + word('Continue') + '</button></div>'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '</fieldset></form>'
    elif status.question.question_type == "settrue":
        datatypes[status.question.fields[0].saveas] = "boolean"
        output += '<form action="' + root + '" id="daform" method="POST"><fieldset>'
        output += '<div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status) + '<div style="clear:both"></div></h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText, status=status) + '</div>'
        output += '<div class="form-actions"><button type="submit" class="btn btn-lg btn-primary" name="' + status.question.fields[0].saveas + '" value="True"> ' + word('Continue') + '</button></div>'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '</fieldset></form>'
    elif status.question.question_type == "multiple_choice":
        if hasattr(status.question.fields[0], 'datatype'):
            datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += '<form action="' + root + '" id="daform" method="POST"><fieldset>'
        output += '<div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status) + '<div style="clear:both"></div></h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText, status=status) + '</div>'
        output += '<div id="errorcontainer" class="alert alert-danger" role="alert" style="display:none"></div>'
        validation_rules['errorElement'] = "span"
        validation_rules['errorLabelContainer'] = "#errorcontainer"
        if status.question.question_variety == "radio":
            if hasattr(status.question.fields[0], 'saveas'):
                if hasattr(status.question.fields[0], 'has_code') and status.question.fields[0].has_code:
                    id_index = 0
                    pairlist = list(status.selectcompute[status.question.fields[0].number])
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                        if pair[0] is not None:
                            output += '<div class="row"><div class="col-md-6"><input data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + str(status.question.fields[0].saveas) + '_' + str(id_index) + '" name="' + str(status.question.fields[0].saveas) + '" type="radio" value="' + unicode(pair[0]) + '"></div></div>'
                        else:
                            output += '<div class="form-group"><div class="col-md-12">' + markdown_to_html(pair[1], status=status) + '</div></div>'
                        id_index += 1
                else:
                    id_index = 0
                    choicelist = list(status.question.fields[0].choices)
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(choicelist)
                    for choice in choicelist:
                        if 'image' in choice:
                            the_icon = icon_html(status, choice['image'])
                        else:
                            the_icon = ''
                        for key in choice:
                            if key == 'image':
                                continue
                            formatted_key = markdown_to_html(key, status=status, trim=True, escape=True)
                            output += '<div class="row"><div class="col-md-6"><input data-labelauty="' + formatted_key + '|' + formatted_key + '" class="to-labelauty radio-icon" id="' + status.question.fields[0].saveas + '_' + str(id_index) + '" name="' + status.question.fields[0].saveas + '" type="radio" value="' + unicode(choice[key]) + '"></div></div>'
                        id_index += 1
                validation_rules['ignore'] = None
                validation_rules['rules'][status.question.fields[0].saveas] = {'required': True}
                validation_rules['messages'][status.question.fields[0].saveas] = {'required': word("You need to select one.")}
            else:
                indexno = 0
                for choice in status.question.fields[0].choices:
                    if 'image' in choice:
                        the_icon = icon_html(status, choice['image'])
                    else:
                        the_icon = ''
                    id_index = 0
                    for key in choice:
                        if key == 'image':
                            continue
                        formatted_key = markdown_to_html(key, status=status, trim=True, escape=True)
                        output += '<div class="row"><div class="col-md-6"><input data-labelauty="' + the_icon + formatted_key + '|' + the_icon + formatted_key + '" class="to-labelauty radio-icon" id="multiple_choice_' + str(indexno) + '_' + str(id_index) + '" name="_multiple_choice" type="radio" value="' + str(indexno) + '"></div></div>'
                        id_index += 1
                    indexno += 1
                    validation_rules['rules']['_multiple_choice'] = {'required': True}
                    validation_rules['messages']['_multiple_choice'] = {'required': word("You need to select one.")}
            output += '<br><button class="btn btn-lg btn-primary" type="submit">' + word('Continue') + '</button>'
        else:
            output += '<div class="btn-toolbar">'
            if hasattr(status.question.fields[0], 'saveas'):
                btn_class = ' btn-primary'
                if hasattr(status.question.fields[0], 'has_code') and status.question.fields[0].has_code:
                    pairlist = list(status.selectcompute[status.question.fields[0].number])
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if pair[0] is not None:
                            output += '<button type="submit" class="btn btn-lg' + btn_class + '" name="' + str(status.question.fields[0].saveas) + '" value="' + unicode(pair[0]) + '"> ' + markdown_to_html(pair[1], status=status, trim=True, do_terms=False) + '</button> '
                        else:
                            output += markdown_to_html(pair[1], status=status)
                else:
                    choicelist = list(status.question.fields[0].choices)
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(choicelist)
                    for choice in choicelist:
                        if 'image' in choice:
                            the_icon = icon_html(status, choice['image'])
                            btn_class = ' btn-default'
                        else:
                            the_icon = ''
                        for key in choice:
                            if key == 'image':
                                continue
                            output += '<button type="submit" class="btn btn-lg' + btn_class + '" name="' + status.question.fields[0].saveas + '" value="' + unicode(choice[key]) + '"> ' + the_icon + markdown_to_html(key, status=status, trim=True, do_terms=False) + '</button> '
            else:
                indexno = 0
                for choice in status.question.fields[0].choices:
                    btn_class = ' btn-primary'
                    if 'image' in choice:
                        the_icon = '<div>' + icon_html(status, choice['image'], width_value=4.0) + '</div>'
                        btn_class = ' btn-default btn-da-custom'
                    else:
                        the_icon = ''
                    for key in choice:
                        if key == 'image':
                            continue
                        if isinstance(choice[key], Question) and choice[key].question_type in ["exit", "continue", "restart", "refresh", "signin", "leave", "link"]:
                            if choice[key].question_type == "continue":
                                btn_class = ' btn-primary'
                            elif choice[key].question_type in ["leave", "link", "restart"]:
                                btn_class = ' btn-warning'
                            elif choice[key].question_type == "refresh":
                                btn_class = ' btn-success'
                            elif choice[key].question_type == "signin":
                                btn_class = ' btn-info'
                            elif choice[key].question_type == "exit":
                                btn_class = ' btn-danger'
                        output += '<button type="submit" class="btn btn-lg' + btn_class + '" name="_multiple_choice" value="' + str(indexno) + '"> ' + the_icon + markdown_to_html(key, status=status, trim=True, do_terms=False) + '</button> '
                    indexno += 1
            output += '</div>'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '</fieldset></form>'
    elif status.question.question_type == 'deadend':
        output += '<div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status) + '<div style="clear:both"></div></h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText, status=status) + '</div>'
    else:
        output += '<form action="' + root + '" id="daform" class="form-horizontal" method="POST"><fieldset>'
        output += '<div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status) + '<div style="clear:both"></div></h3></div>'
        if status.subquestionText:
            output += '<div>' + markdown_to_html(status.subquestionText, status=status) + '</div>'
            output += '<div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">' + word('Continue') + '</button></div>'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += '</fieldset></form>'
    if len(status.attachments) > 0:
        output += '<br>'
        if len(status.attachments) > 1:
            output += '<div class="alert alert-success" role="alert">' + word('attachment_message_plural') + '</div>'
        else:
            output += '<div class="alert alert-success" role="alert">' + word('attachment_message_singular') + '</div>'
        attachment_index = 0
        rtfs_included = False
        for attachment in status.attachments:
            if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                rtfs_included = True
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
            output += '<div><h3>' + markdown_to_html(attachment['name'], trim=True) + '</h3></div>'
            if attachment['description']:
                output += '<div><p><em>' + markdown_to_html(attachment['description'], status=status) + '</em></p></div>'
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
                output += '<blockquote>' + unicode(attachment['content']['html']) + '</blockquote>'
                output += '</div>'
            if show_markdown:
                output += '<div class="tab-pane" id="markdown' + str(attachment_index) + '">'
                output += '<pre>' + unicode(attachment['markdown']['html']) + '</pre>'
                output += '</div>'
            output += '</div></div>'
            attachment_index += 1
        if status.question.allow_emailing:
            if len(status.attachments) > 1:
                email_header = word("E-mail these documents to yourself")
            else:
                email_header = word("E-mail this document to yourself")
            output += """
<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
  <div class="panel panel-default">
    <div class="panel-heading" role="tab" id="headingOne">
      <h4 class="panel-title">
        <a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
          """ + email_header + """
        </a>
      </h4>
    </div>
    <div id="collapseOne" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingOne">
      <div class="panel-body">
        <form action=\"""" + root + """\" id="emailform" class="form-horizontal" method="POST">
          <fieldset>
            <div class="form-group"><label for="_attachment_email_address" class="control-label col-sm-4">""" + word('E-mail address') + """</label><div class="col-sm-8"><input class="form-control" type="email" name="_attachment_email_address" id="_attachment_email_address"></div></div>"""
            if rtfs_included:
                output += """
            <div class="form-group"><label for="_attachment_include_rtf" class="control-label col-sm-4">""" + '&nbsp;</label><div class="col-sm-8"><input type="checkbox" value="True" name="_attachment_include_rtf" id="_attachment_include_rtf"> ' + word('Include RTF files for editing') + '</div></div>'
            output += """
            <div class="form-actions"><button class="btn btn-primary" type="submit">""" + word('Send') + '</button></div><input type="hidden" name="_email_attachments" value="1"><input type="hidden" name="_question_number" value="' + str(status.question.number) + '">'
            output += """
          </fieldset>
        </form>
      </div>
    </div>
  </div>
</div>"""
            extra_scripts.append("""<script>$("#emailform").validate(""" + json.dumps({'rules': {'_attachment_email_address': {'notEmpty': True, 'required': True, 'email': True}}, 'messages': {'_attachment_email_address': {'required': word("An e-mail address is required."), 'email': word("You need to enter a complete e-mail address.")}}, 'errorClass': 'help-inline'}) + """);</script>""")
    if len(status.attributions):
        output += '<br><br><br><br><br><br><br>'
    for attribution in sorted(status.attributions):
        output += '<div><small>' + markdown_to_html(attribution) + '</small></div>'
    output += '</section>'
    output += '<section id="help" class="tab-pane col-md-6">'
    for help_section in status.helpText:
        if help_section['heading'] is not None:
            output += '<div class="page-header"><h3>' + help_section['heading'] + '</h3></div>'
        else:
            output += '<div class="page-header"><h3>' + word('Help with this question') + '</h3></div>'
        output += markdown_to_html(help_section['content'], status=status)
    if len(status.attributions):
        output += '<br><br><br><br><br><br><br>'
    for attribution in sorted(status.attributions):
        output += '<div><small>' + markdown_to_html(attribution) + '</small></div>'
    output += '</section>'
    extra_scripts.append('<script>$("#daform").validate(' + json.dumps(validation_rules) + ');</script>')
    return output

def noquote(string):
    return noquote_match.sub('\\\"', string)

def input_for(status, field, wide=False):
    output = ""
    if field.number in status.defaults:
        defaultvalue = unicode(status.defaults[field.number])
    else:
        defaultvalue = None
    if field.number in status.hints:
        placeholdertext = ' placeholder="' + unicode(status.hints[field.number]) + '"'
    else:
        placeholdertext = ''
    if hasattr(field, 'choicetype'):
        if field.choicetype == 'compute':
            pairlist = list(status.selectcompute[field.number])
        else:
            pairlist = list(field.selections)
        if hasattr(field, 'shuffle') and field.shuffle:
            random.shuffle(pairlist)
        if field.datatype == 'checkboxes':
            inner_fieldlist = list()
            id_index = 0
            for pair in pairlist:
                if pair[0] is not None:
                    inner_field = str(field.saveas) + "[" + myb64quote(pair[0]) + "]"
                    #sys.stderr.write("I've got a " + repr(pair[1]) + "\n")
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                    inner_fieldlist.append('<input data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty checkbox-icon" id="' + str(field.saveas) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True">')
                else:
                    inner_fieldlist.append('<div>' + markdown_to_html(pair[1], status=status) + '</div>')
                id_index += 1
            output += u''.join(inner_fieldlist)
        elif field.datatype == 'radio':
            inner_fieldlist = list()
            id_index = 0
            for pair in pairlist:
                if pair[0] is not None:
                    #sys.stderr.write(str(field.saveas) + "\n")
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                    inner_fieldlist.append('<input data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + str(field.saveas) + '_' + str(id_index) + '" name="' + str(field.saveas) + '" type="radio" value="' + unicode(pair[0]) + '">')
                else:
                    inner_fieldlist.append('<div>' + markdown_to_html(unicode(pair[1]), status=status) + '</div>')
                id_index += 1
            output += "".join(inner_fieldlist)
        else:
            output += '<select name="' + field.saveas + '" id="' + field.saveas + '" >'
            output += '<option name="' + field.saveas + '" id="' + field.saveas + '" value="">' + word('Select...') + '</option>'
            for pair in pairlist:
                if pair[0] is not None:
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, do_terms=False)
                    output += '<option value="' + unicode(pair[0]) + '"'
                    if defaultvalue is not None and unicode(pair[0]) == defaultvalue:
                        output += 'selected="selected"'
                    output += '>' + formatted_item + '</option>'
            output += '</select> '
    elif hasattr(field, 'datatype'):
        if field.datatype in ['yesno', 'yesnowide']:
            output += '<input class="to-labelauty checkbox-icon" type="checkbox" value="True" data-labelauty="' + field.label + '|' + field.label + '" name="' + field.saveas + '" id="' + field.saveas + '"'
            if defaultvalue:
                output += ' checked'
            output += '> '
        elif field.datatype in ['file', 'files']:
            if field.datatype == 'file':
                multipleflag = ''
            else:
                multipleflag = ' multiple'
            output += '<input type="file" class="file" data-show-upload="false" data-preview-file-type="text" name="' + field.saveas + '" id="' + field.saveas + '"' + multipleflag + '>'
            #output += '<div class="fileinput fileinput-new input-group" data-provides="fileinput"><div class="form-control" data-trigger="fileinput"><i class="glyphicon glyphicon-file fileinput-exists"></i><span class="fileinput-filename"></span></div><span class="input-group-addon btn btn-default btn-file"><span class="fileinput-new">' + word('Select file') + '</span><span class="fileinput-exists">' + word('Change') + '</span><input type="file" name="' + field.saveas + '" id="' + field.saveas + '"' + multipleflag + '></span><a href="#" class="input-group-addon btn btn-default fileinput-exists" data-dismiss="fileinput">' + word('Remove') + '</a></div>'
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
            if field.datatype in ['integer', 'float', 'currency']:
                input_type = 'number'
            if field.datatype == 'currency':
                output += '<div class="input-group"><span class="input-group-addon" id="addon-' + field.saveas + '">' + currency_symbol() + '</span>'
            output += '<input' + defaultstring + placeholdertext + ' class="form-control" type="' + input_type + '" name="' + field.saveas + '" id="' + field.saveas + '"'
            if field.datatype == 'currency':
                output += ' aria-describedby="addon-' + field.saveas + '"></div>'
            else:
                output += '>'
    return output

def myb64quote(text):
    return "'" + codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '') + "'"
