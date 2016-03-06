from docassemble.base.util import word, currency_symbol
import docassemble.base.filter
from docassemble.base.filter import markdown_to_html, get_audio_urls, get_video_urls, audio_control, video_control, noquote
from docassemble.base.parse import Question, debug
from docassemble.base.logger import logmessage
import urllib
import sys
import os
import re
import json
import random
import sys
import codecs
import html2text

def tracker_tag(status):
    output = ''
    if status.question.name:
        output += '              <input type="hidden" name="_question_name" value="' + status.question.name + '"/>\n'
    output += '              <input type="hidden" name="_tracker" value="' + str(status.tracker) + '"/>\n'
    if 'track_location' in status.extras and status.extras['track_location']:
        output += '              <input type="hidden" id="_track_location" name="_track_location" value=""/>\n'
    return output

def datatype_tag(datatypes):
    if len(datatypes):
        return('              <input type="hidden" name="_datatypes" value=' + myb64doublequote(json.dumps(datatypes)) + '/>\n')
    return ('')

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
    return('<img class="daicon" src="' + url + '" style="' + sizing + '"/>')

def signature_html(status, debug, root):
    output = '<div id="page"><div class="header" id="header"><a id="new" class="navbtn nav-left">' + word('Clear') + '</a><a id="save" class="navbtn nav-right">' + word('Done') + '</a><div class="title">' + word('Sign Your Name') + '</div></div><div class="toppart" id="toppart">'
    if status.questionText:
        output += markdown_to_html(status.questionText, trim=True)
    output += '</div>'
    if status.subquestionText:
        output += '<div class="midpart">' + markdown_to_html(status.subquestionText) + '</div>'
    output += '<div id="content"><p style="text-align:center;border-style:solid;border-width:1px">' + word('Loading.  Please wait . . . ') + '</p></div><div class="bottompart" id="bottompart">'
    if (status.underText):
        output += markdown_to_html(status.underText, trim=True)
    output += '</div></div><form action="' + root + '" id="daform" method="POST"><input type="hidden" name="_save_as" value="' + status.question.fields[0].saveas + '"/><input type="hidden" id="_the_image" name="_the_image" value=""/><input type="hidden" id="_success" name="_success" value="0"/>'
    output += tracker_tag(status)
    output += '</form>\n'
    return output

def as_html(status, extra_scripts, extra_css, url_for, debug, root):
    decorations = list()
    uses_audio_video = False
    audio_video_text = ''
    datatypes = dict()
    onchange = list()
    validation_rules = {'rules': {}, 'messages': {}, 'errorClass': 'help-inline'}
    if status.question.script is not None:
        extra_scripts.append(status.question.script)
    if status.audiovideo is not None:
        uses_audio_video = True
        audio_urls = get_audio_urls(status.audiovideo)
        if len(audio_urls):
            audio_video_text += '<div>\n' + audio_control(audio_urls) + '</div>\n'
        video_urls = get_video_urls(status.audiovideo)
        if len(video_urls):
            audio_video_text += '<div>\n' + video_control(video_urls) + '</div>\n'
    if status.using_screen_reader and 'question' in status.screen_reader_links:
        audio_video_text += '<div>\n' + audio_control(status.screen_reader_links['question'], preload="none") + '</div>\n'
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
                        decorations.append('<img class="daiconfloat" style="' + sizing + '" src="' + url + '"/>')
    if len(decorations):
        decoration_text = decorations[0];
    else:
        decoration_text = ''
    master_output = ""
    master_output += '        <section id="question" class="tab-pane active col-md-6">\n'
    output = ""
    if status.question.question_type == "yesno":
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += indent_by(audio_video_text, 10) + '          <form action="' + root + '" id="daform" method="POST">\n            <fieldset>\n'
        output += '              <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '              <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=16) + '              </div>\n'
        output += '              <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
        output += '              <div class="btn-toolbar">\n                <button class="btn btn-primary btn-lg " name="' + status.question.fields[0].saveas + '" type="submit" value="True">Yes</button>\n                <button class="btn btn-lg btn-info" name="' + status.question.fields[0].saveas + '" type="submit" value="False">No</button>\n              </div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '            </fieldset>\n          </form>\n'
    elif status.question.question_type == "noyes":
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += indent_by(audio_video_text, 10) + '          <form action="' + root + '" id="daform" method="POST">\n            <fieldset>\n'
        output += '              <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '              <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=16) + '              </div>\n'
        output += '              <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
        output += '              <div class="btn-toolbar">\n                <button class="btn btn-primary btn-lg" name="' + status.question.fields[0].saveas + '" type="submit" value="False">Yes</button>\n                <button class="btn btn-lg btn-info" name="' + status.question.fields[0].saveas + '" type="submit" value="True">No</button>\n              </div>\n'
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '            </fieldset>\n          </form>\n'
    elif status.question.question_type == "fields":
        enctype_string = ""
        fieldlist = list()
        checkboxes = list()
        files = list()
        checkbox_validation = False
        for field in status.question.fields:
            if field.required:
                req_tag = ' required'
            else:
                req_tag = ''
            if hasattr(field, 'extras'):
                if 'script' in field.extras and 'script' in status.extras:
                    extra_scripts.append(status.extras['script'][field.number])
                if 'css' in field.extras and 'css' in status.extras:
                    extra_css.append(status.extras['css'][field.number])
                #fieldlist.append("<div>datatype is " + str(field.datatype) + "</div>")
            if hasattr(field, 'datatype'):
                if field.datatype == 'html':
                    fieldlist.append('              <div class="form-group' + req_tag +'"><div class="col-md-12"><note>' + status.extras['html'][field.number].rstrip() + '</note></div></div>\n')
                    continue
                elif field.datatype == 'note':
                    fieldlist.append('              <div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status, strip_newlines=True) + '</div></div>\n')
                    continue
                elif field.datatype in ['script', 'css']:
                    continue
                else:
                    datatypes[field.saveas] = field.datatype
            if field.number in status.helptexts:
                helptext_start = '<a class="daterm" data-container="body" data-toggle="popover" data-placement="bottom" data-content=' + noquote(unicode(status.helptexts[field.number])) + '>' 
                helptext_end = '</a>'
            else:
                helptext_start = ''
                helptext_end = ''
            if hasattr(field, 'disableothers') and field.disableothers:
                onchange.append(field.saveas)
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
                if (field.datatype in ['files', 'file', 'camera', 'camcorder', 'microphone']):
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
                    fieldlist.append('              <div class="form-group' + req_tag +'"><div class="col-md-12">' + input_for(status, field, wide=True) + '</div></div>\n')
                elif hasattr(field, 'datatype') and field.datatype == 'yesnowide':
                    fieldlist.append('              <div class="row"><div class="col-md-12">' + input_for(status, field) + '</div></div>\n')
                elif hasattr(field, 'datatype') and field.datatype == 'yesno':
                    fieldlist.append('              <div class="form-group' + req_tag +'"><div class="col-sm-offset-4 col-sm-8">' + input_for(status, field) + '</div></div>\n')
                else:
                    fieldlist.append('              <div class="form-group' + req_tag +'"><label for="' + field.saveas + '" class="control-label col-sm-4">' + helptext_start + field.label + helptext_end + '</label><div class="col-sm-8">' + input_for(status, field) + '</div></div>\n')
        output += indent_by(audio_video_text, 10) + '          <form action="' + root + '" id="daform" class="form-horizontal" method="POST"' + enctype_string + '>\n            <fieldset>\n'
        output += '              <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '              <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=16) + '              </div>\n'
        #output += '<div class="row">'
        if (len(fieldlist)):
            output += "".join(fieldlist)
        else:
            output += "              <p>Error: no fields</p>\n"
        #output += '</div>\n'
        if len(checkboxes):
            output += '              <input type="hidden" name="_checkboxes" value=' + myb64doublequote(json.dumps(checkboxes)) + '/>\n'
        if len(files):
            output += '              <input type="hidden" name="_files" value=' + myb64doublequote(json.dumps(files)) + '/>\n'
            init_string = '<script>'
            for saveasname in files:
                init_string += '$("#' + saveasname + '").fileinput();' + "\n"
            init_string += '</script>'
            extra_scripts.append('<script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>' + init_string)
            #extra_css.append('<link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />')
        output += '              <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '              <div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">' + word('Continue') + '</button></div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '            </fieldset>\n          </form>\n'
    elif status.question.question_type == "settrue":
        datatypes[status.question.fields[0].saveas] = "boolean"
        output += indent_by(audio_video_text, 10) + '          <form action="' + root + '" id="daform" method="POST">\n            <fieldset>\n'
        output += '              <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '              <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=16) + '              </div>\n'
        output += '              <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '              <div class="form-actions"><button type="submit" class="btn btn-lg btn-primary" name="' + status.question.fields[0].saveas + '" value="True"> ' + word('Continue') + '</button></div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '            </fieldset>\n          </form>\n'
    elif status.question.question_type == "multiple_choice":
        if hasattr(status.question.fields[0], 'datatype'):
            datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += indent_by(audio_video_text, 10) + '          <form action="' + root + '" id="daform" method="POST">\n            <fieldset>\n'
        output += '              <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '              <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=16) + '              </div>\n'
        output += '              <div id="errorcontainer" class="alert alert-danger" role="alert" style="display:none"></div>\n'
        output += '              <p class="sr-only">' + word('Your choices are:') + '</p>\n'
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
                            output += '              <div class="row"><div class="col-md-6"><input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + str(status.question.fields[0].saveas) + '_' + str(id_index) + '" name="' + str(status.question.fields[0].saveas) + '" type="radio" value="' + unicode(pair[0]) + '"/></div></div>\n'
                        else:
                            output += '              <div class="form-group"><div class="col-md-12">' + markdown_to_html(pair[1], status=status) + '</div></div>\n'
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
                            output += '              <div class="row"><div class="col-md-6"><input alt="' + formatted_key + '" data-labelauty="' + formatted_key + '|' + formatted_key + '" class="to-labelauty radio-icon" id="' + status.question.fields[0].saveas + '_' + str(id_index) + '" name="' + status.question.fields[0].saveas + '" type="radio" value="' + unicode(choice[key]) + '"/></div></div>\n'
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
                        output += '              <div class="row"><div class="col-md-6"><input alt="' + formatted_key + '" data-labelauty="' + the_icon + formatted_key + '|' + the_icon + formatted_key + '" class="to-labelauty radio-icon" id="multiple_choice_' + str(indexno) + '_' + str(id_index) + '" name="_multiple_choice" type="radio" value="' + str(indexno) + '"/></div></div>\n'
                        id_index += 1
                    indexno += 1
                    validation_rules['rules']['_multiple_choice'] = {'required': True}
                    validation_rules['messages']['_multiple_choice'] = {'required': word("You need to select one.")}
            output += '              <br/>\n'
            output += '              <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
            output += '              <button class="btn btn-lg btn-primary" type="submit">' + word('Continue') + '</button>\n'
        else:
            #output += '              <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
            output += '              <div class="btn-toolbar">\n'
            if hasattr(status.question.fields[0], 'saveas'):
                btn_class = ' btn-primary'
                if hasattr(status.question.fields[0], 'has_code') and status.question.fields[0].has_code:
                    pairlist = list(status.selectcompute[status.question.fields[0].number])
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if pair[0] is not None:
                            output += '                <button type="submit" class="btn btn-lg' + btn_class + '" name="' + str(status.question.fields[0].saveas) + '" value="' + unicode(pair[0]) + '"> ' + markdown_to_html(pair[1], status=status, trim=True, do_terms=False) + '</button>\n'
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
                            output += '                <button type="submit" class="btn btn-lg' + btn_class + '" name="' + status.question.fields[0].saveas + '" value="' + unicode(choice[key]) + '"> ' + the_icon + markdown_to_html(key, status=status, trim=True, do_terms=False) + '</button>\n'
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
                        output += '                <button type="submit" class="btn btn-lg' + btn_class + '" name="_multiple_choice" value="' + str(indexno) + '">' + the_icon + markdown_to_html(key, status=status, trim=True, do_terms=False, strip_newlines=True) + '</button>\n'
                    indexno += 1
            output += '              </div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '            </fieldset>\n          </form>\n'
    elif status.question.question_type == 'deadend':
        output += indent_by(audio_video_text, 10) + '              <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '              <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=16) + '              </div>\n'
    else:
        output += indent_by(audio_video_text, 10) + '          <form action="' + root + '" id="daform" class="form-horizontal" method="POST">\n            <fieldset>\n'
        output += '              <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '              <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=16) + '              </div>\n'
        output += '              <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '              <div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">' + word('Continue') + '</button></div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += '            </fieldset>\n          </form>\n'
    if len(status.attachments) > 0:
        output += '          <br/>\n'
        if len(status.attachments) > 1:
            output += '          <div class="alert alert-success" role="alert">' + word('attachment_message_plural') + '</div>\n'
        else:
            output += '          <div class="alert alert-success" role="alert">' + word('attachment_message_singular') + '</div>\n'
        attachment_index = 0
        editable_included = False
        if len(status.attachments) > 1:
            file_word = 'files'
        else:
            file_word = 'file'
        editable_name = ''
        for attachment in status.attachments:
            if 'rtf' in attachment['valid_formats'] or 'docx' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    editable_included = True
                    if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                        if 'docx' in attachment['valid_formats']:
                            editable_name = 'RTF and DOCX files'
                        else:
                            editable_name = 'RTF ' + file_word
                    elif 'docx' in attachment['valid_formats']:
                        editable_name = 'DOCX ' + file_word
            if debug and len(attachment['markdown']):
                show_markdown = True
            else:
                show_markdown = False
            if 'pdf' in attachment['valid_formats'] or 'rtf' in attachment['valid_formats'] or 'docx' in attachment['valid_formats'] or (debug and 'tex' in attachment['valid_formats']) or '*' in attachment['valid_formats']:
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
            output += '          <div><h3>' + markdown_to_html(attachment['name'], trim=True, status=status, strip_newlines=True) + '</h3></div>\n'
            if attachment['description']:
                output += '          <div>' + markdown_to_html(attachment['description'], status=status, strip_newlines=True) + '</div>\n'
            output += '          <div class="tabbable">\n'
            if True or show_preview or show_markdown:
                output += '            <ul class="nav nav-tabs">\n'
                if show_download:
                    output += '              <li class="active"><a href="#download' + str(attachment_index) + '" data-toggle="tab">' + word('Download') + '</a></li>\n'
                if show_preview:
                    output += '              <li><a href="#preview' + str(attachment_index) + '" data-toggle="tab">' + word('Preview') + '</a></li>\n'
                if show_markdown:
                    output += '              <li><a href="#markdown' + str(attachment_index) + '" data-toggle="tab">' + word('Markdown') + '</a></li>\n'
                output += '            </ul>\n'
            output += '            <div class="tab-content">\n'
            if show_download:
                output += '              <div class="tab-pane active" id="download' + str(attachment_index) + '">\n'
                if multiple_formats:
                    output += '                <p>' + word('save_as_multiple') + '</p>\n'
                #else:
                    #output += '                <p>' + word('save_as_singular') + '</p>\n'
                if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '                <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=pdf"><i class="glyphicon glyphicon-print"></i> PDF</a> (' + word('pdf_message') + ')</p>\n'
                if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '                <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=rtf"><i class="glyphicon glyphicon-pencil"></i> RTF</a> (' + word('rtf_message') + ')</p>\n'
                if 'docx' in attachment['valid_formats']:
                    output += '                <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=docx"><i class="glyphicon glyphicon-pencil"></i> DOCX</a> (' + word('docx_message') + ')</p>\n'
                if debug and ('tex' in attachment['valid_formats'] or '*' in attachment['valid_formats']):
                    output += '                <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=tex"><i class="glyphicon glyphicon-pencil"></i> LaTeX</a> (' + word('tex_message') + ')</p>\n'
                output += '              </div>\n'
            if show_preview:
                output += '              <div class="tab-pane" id="preview' + str(attachment_index) + '">\n'
                output += '                <blockquote>' + unicode(attachment['content']['html']) + '</blockquote>\n'
                output += '              </div>\n'
            if show_markdown:
                if 'html' in attachment['valid_formats']:
                    md_format = 'html'
                else:
                    for format_type in attachment['valid_formats']:
                        md_format = format_type
                        break
                output += '              <div class="tab-pane" id="markdown' + str(attachment_index) + '">\n'
                output += '                <pre>' + unicode(attachment['markdown'][md_format]) + '</pre>\n'
                output += '              </div>\n'
            output += '            </div>\n          </div>\n'
            attachment_index += 1
        if status.question.allow_emailing:
            if len(status.attachments) > 1:
                email_header = word("E-mail these documents to yourself")
            else:
                email_header = word("E-mail this document to yourself")
            output += """\
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
                      <div class="form-group"><label for="_attachment_email_address" class="control-label col-sm-4">""" + word('E-mail address') + """</label><div class="col-sm-8"><input alt=""" + '"' + word ("Input box") + '"' + """ class="form-control" type="email" name="_attachment_email_address" id="_attachment_email_address"/></div></div>"""
            if editable_included:
                output += """
                      <div class="form-group"><label for="_attachment_include_editable" class="control-label col-sm-4">""" + '&nbsp;</label><div class="col-sm-8"><input alt="' + word ("Check box") + ", " + word('Include ' + editable_name + ' for editing') + '" type="checkbox" value="True" name="_attachment_include_editable" id="_attachment_include_editable"/> ' + word('Include ' + editable_name + ' for editing') + '</div></div>\n'
            output += """
                      <div class="form-actions"><button class="btn btn-primary" type="submit">""" + word('Send') + '</button></div><input type="hidden" name="_email_attachments" value="1"/><input type="hidden" name="_question_number" value="' + str(status.question.number) + '"/>'
            output += """
                    </fieldset>
                  </form>
                </div>
              </div>
            </div>
          </div>
"""
            extra_scripts.append("""<script>\n      $("#emailform").validate(""" + json.dumps({'rules': {'_attachment_email_address': {'notEmpty': True, 'required': True, 'email': True}}, 'messages': {'_attachment_email_address': {'required': word("An e-mail address is required."), 'email': word("You need to enter a complete e-mail address.")}}, 'errorClass': 'help-inline'}) + """);\n    </script>""")
    if len(status.attributions):
        output += '          <br/><br/><br/><br/><br/><br/><br/>\n'
    for attribution in sorted(status.attributions):
        output += '          <div><attribution><small>' + markdown_to_html(attribution, strip_newlines=True) + '</small></attribution></div>\n'
    if status.using_screen_reader:
        status.screen_reader_text['question'] = unicode(output)
    master_output += output
    master_output += '        </section>\n'
    master_output += '        <section id="help" class="tab-pane col-md-6">\n'
    output = '<div><a id="backToQuestion" data-toggle="tab" href="#question" class="btn btn-info btn-md"><i class="glyphicon glyphicon-arrow-left"></i> ' + word("Back to question") + '</a></div>'
    if status.using_screen_reader and 'help' in status.screen_reader_links:
        output += '          <div>\n' + indent_by(audio_control(status.screen_reader_links['help'], preload="none"), 12) + '          </div>\n'
    for help_section in status.helpText:
        if help_section['heading'] is not None:
            output += '          <div class="page-header"><h3>' + help_section['heading'] + '</h3></div>\n'
        else:
            output += '          <div class="page-header"><h3>' + word('Help with this question') + '</h3></div>\n'
        if help_section['audiovideo'] is not None:
            uses_audio_video = True
            audio_urls = get_audio_urls(help_section['audiovideo'])
            if len(audio_urls):
                output += '          <div>\n' + indent_by(audio_control(audio_urls), 12) + '          </div>\n'
            video_urls = get_video_urls(help_section['audiovideo'])
            if len(video_urls):
                output += '          <div>\n' + indent_by(video_control(video_urls), 12) + '          </div>\n'
        output += markdown_to_html(help_section['content'], status=status, indent=10)
    if len(status.attributions):
        output += '          <br/><br/><br/><br/><br/><br/><br/>\n'
    for attribution in sorted(status.attributions):
        output += '          <div><attribution><small>' + markdown_to_html(attribution, strip_newlines=True) + '</small></attribution></div>\n'
    if status.using_screen_reader:
        #status.screen_reader_text['help'] = html2text.html2text(output)
        status.screen_reader_text['help'] = unicode(output)
    master_output += output
    master_output += '        </section>\n'
    extra_scripts.append('<script>\n      $("#daform").validate(' + json.dumps(validation_rules) + ');\n    </script>')
    for element_id_unescaped in onchange:
        element_id = re.sub(r'(:|\.|\[|\]|,)', r'\\\\\1', element_id_unescaped)
        the_script = """\
    <script>
      $("#""" + element_id + """").change(function(){
        if ($( this ).val() == ""){
          $("#daform input:not(#""" + element_id + """):not(:hidden)").prop("disabled", false);
          $("#daform select:not(#""" + element_id + """):not(:hidden)").prop("disabled", false);
          $("#daform input:not(#""" + element_id + """):not(:hidden)").parent().parent().removeClass("greyedout");
          $("#daform select:not(#""" + element_id + """):not(:hidden)").parent().parent().removeClass("greyedout");
        }
        else{
          $("#daform input:not(#""" + element_id + """):not(:hidden)").prop("disabled", true);
          $("#daform select:not(#""" + element_id + """):not(:hidden)").prop("disabled", true);
          $("#daform input:not(#""" + element_id + """):not(:hidden)").parent().parent().addClass("greyedout");
          $("#daform select:not(#""" + element_id + """):not(:hidden)").parent().parent().addClass("greyedout");
        }
      });
    </script>
"""
        extra_scripts.append(the_script)
    if 'track_location' in status.extras and status.extras['track_location']:
        track_js = """\
    <script>
      function daSetPosition(position) {
        document.getElementById('_track_location').value = JSON.stringify({'latitude': position.coords.latitude, 'longitude': position.coords.longitude})
      }
      function daShowError(error) {
        switch(error.code) {
          case error.PERMISSION_DENIED:
            document.getElementById('_track_location').value = JSON.stringify({error: "User denied the request for Geolocation"});
            console.log("User denied the request for Geolocation.");
            break;
          case error.POSITION_UNAVAILABLE:
            document.getElementById('_track_location').value = JSON.stringify({error: "Location information is unavailable"});
            console.log("Location information is unavailable.");
            break;
          case error.TIMEOUT:
            document.getElementById('_track_location').value = JSON.stringify({error: "The request to get user location timed out"});
            console.log("The request to get user location timed out.");
            break;
          case error.UNKNOWN_ERROR:
            document.getElementById('_track_location').value = JSON.stringify({error: "An unknown error occurred"});
            console.log("An unknown error occurred.");
            break;
        }
      }
      $( document ).ready(function() {
        $(function () {
          if (navigator.geolocation) {
            document.getElementById('_track_location').value = JSON.stringify({error: "getCurrentPosition was still running"});
            navigator.geolocation.getCurrentPosition(daSetPosition, daShowError, {timeout: 1000, maximumAge: 3600000});
          }
          else{
            document.getElementById('_track_location').value = JSON.stringify({error: "navigator.geolocation not available in browser"});
          }
        });
      });
    </script>"""
        extra_scripts.append(track_js)
    if len(status.maps):
        map_js = """\
    <script>
      $(window).ready(daUpdateHeight);
      $(window).resize(daUpdateHeight);
      function daUpdateHeight(){
        $(".googleMap").each(function(){
          var size = $( this ).width();
          $( this ).css('height', size);
        });
      }
      function daAddMap(map_num, center_lat, center_lon){
        var map = new google.maps.Map(document.getElementById("map" + map_num), {
          zoom: 11,
          center: new google.maps.LatLng(center_lat, center_lon),
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });
        var infowindow = new google.maps.InfoWindow();
        return({map: map, infowindow: infowindow});
      }
      function daAddMarker(map, marker_info){
        var marker;
        if (marker_info.icon){
          if (marker_info.icon.path){
            marker_info.icon.path = google.maps.SymbolPath[marker_info.icon.path];
          }
        }
        else{
          marker_info.icon = null;
        }
        marker = new google.maps.Marker({
          position: new google.maps.LatLng(marker_info.latitude, marker_info.longitude),
          map: map.map,
          icon: marker_info.icon
        });
        if(marker_info.info){
          google.maps.event.addListener(marker, 'click', (function(marker, info) {
            return function() {
              map.infowindow.setContent(info);
              map.infowindow.open(map.map, marker);
            }
          })(marker, marker_info.info));
        }
        return marker;
      }
      function daInitMap(){
        maps = [];
        map_info = [""" + ", ".join(status.maps) + """];
        map_info_length = map_info.length;
        for (var i = 0; i < map_info_length; i++){
          the_map = map_info[i];
          var bounds = new google.maps.LatLngBounds();
          maps[i] = daAddMap(i, the_map.center.latitude, the_map.center.longitude);
          marker_length = the_map.markers.length;
          for (var j = 0; j < marker_length; j++){
            var new_marker = daAddMarker(maps[i], the_map.markers[j]);
            bounds.extend(new_marker.getPosition());
          }
          maps[i].map.fitBounds(bounds);
        }
      }
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?signed_in=true&callback=daInitMap"></script>
"""
        extra_scripts.append(map_js)
    return master_output

def input_for(status, field, wide=False):
    output = ""
    if field.number in status.defaults and type(status.defaults[field.number]) in [str, unicode, int, float]:
        defaultvalue = unicode(status.defaults[field.number])
    else:
        defaultvalue = None
    if field.number in status.hints:
        placeholdertext = ' placeholder=' + json.dumps(unicode(status.hints[field.number].replace('\n', ' ')))
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
                    inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty checkbox-icon" id="' + str(field.saveas) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"/>')
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
                    inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + str(field.saveas) + '_' + str(id_index) + '" name="' + str(field.saveas) + '" type="radio" value="' + unicode(pair[0]) + '"/>')
                else:
                    inner_fieldlist.append('<div>' + markdown_to_html(unicode(pair[1]), status=status) + '</div>')
                id_index += 1
            output += "".join(inner_fieldlist)
        else:
            output += '<p class="sr-only">' + word('Select box') + '</p>'
            output += '<select class="daselect" name="' + field.saveas + '" id="' + field.saveas + '" >'
            output += '<option name="' + field.saveas + '" id="' + field.saveas + '" value="">' + word('Select...') + '</option>'
            for pair in pairlist:
                if pair[0] is not None:
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, do_terms=False)
                    output += '<option value="' + unicode(pair[0]) + '"'
                    if defaultvalue is not None and unicode(pair[0]) == defaultvalue:
                        output += ' selected="selected"'
                    output += '>' + formatted_item + '</option>'
            output += '</select> '
    elif hasattr(field, 'datatype'):
        if field.datatype in ['yesno', 'yesnowide']:
            output += '<input alt="' + field.label + '" class="to-labelauty checkbox-icon" type="checkbox" value="True" data-labelauty="' + field.label + '|' + field.label + '" name="' + field.saveas + '" id="' + field.saveas + '"'
            if defaultvalue:
                output += ' checked'
            output += '/> '
        elif field.datatype in ['file', 'files', 'camera', 'camcorder', 'microphone']:
            if field.datatype == 'files':
                multipleflag = ' multiple'
            else:
                multipleflag = ''
            if field.datatype == 'camera':
                accept = ' accept="image/*;capture=camera"'
            elif field.datatype == 'camcorder':
                accept = ' accept="video/*;capture=camcorder"'
            elif field.datatype == 'microphone':
                accept = ' accept="audio/*;capture=microphone"'
            else:
                accept = ''
            output += '<input alt="' + word("You can upload a file here") + '" type="file" class="file" data-show-upload="false" data-preview-file-type="text" name="' + field.saveas + '" id="' + field.saveas + '"' + multipleflag + accept + '/>'
            #output += '<div class="fileinput fileinput-new input-group" data-provides="fileinput"><div class="form-control" data-trigger="fileinput"><i class="glyphicon glyphicon-file fileinput-exists"></i><span class="fileinput-filename"></span></div><span class="input-group-addon btn btn-default btn-file"><span class="fileinput-new">' + word('Select file') + '</span><span class="fileinput-exists">' + word('Change') + '</span><input type="file" name="' + field.saveas + '" id="' + field.saveas + '"' + multipleflag + '></span><a href="#" class="input-group-addon btn btn-default fileinput-exists" data-dismiss="fileinput">' + word('Remove') + '</a></div>\n'
        elif field.datatype == 'area':
            output += '<textarea alt="' + word("Input box") + '" class="form-control" rows="4" name="' + field.saveas + '" id="' + field.saveas + '"' + placeholdertext + '>'
            if defaultvalue is not None:
                output += defaultvalue
            output += '</textarea>'
        else:
            if defaultvalue is not None:
                defaultstring = ' value="' + defaultvalue + '"'
            else:
                defaultstring = ''
            input_type = field.datatype
            step_string = ''
            if field.datatype in ['integer', 'float', 'currency']:
                input_type = 'number'
                if field.datatype == 'integer':
                    step_string = ' step="1"'
                if field.datatype == 'float':
                    step_string = ' step="0.01"'
                if field.datatype == 'currency':
                    step_string = ' step="0.01"'
                output += '<div class="input-group"><span class="input-group-addon" id="addon-' + field.saveas + '">' + currency_symbol() + '</span>'
            output += '<input' + defaultstring + placeholdertext + ' alt="' + word("Input box") + '" class="form-control" type="' + input_type + '"' + step_string + ' name="' + field.saveas + '" id="' + field.saveas + '"'
            if field.datatype == 'currency':
                output += ' aria-describedby="addon-' + field.saveas + '"/></div>'
            else:
                output += '/>'
    return output

def myb64doublequote(text):
    return '"' + codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '') + '"'

def myb64quote(text):
    return "'" + codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '') + "'"

def indent_by(text, num):
    if not text:
        return ""
    return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"
    
