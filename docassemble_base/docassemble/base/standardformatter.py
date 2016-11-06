from docassemble.base.functions import word, currency_symbol, url_action
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
from bs4 import BeautifulSoup

def tracker_tag(status):
    output = ''
    if status.question.name:
        output += '                <input type="hidden" name="_question_name" value="' + status.question.name + '"/>\n'
    output += '                <input type="hidden" name="_tracker" value="' + str(status.tracker) + '"/>\n'
    if 'track_location' in status.extras and status.extras['track_location']:
        output += '                <input type="hidden" id="_track_location" name="_track_location" value=""/>\n'
    return output

def datatype_tag(datatypes):
    if len(datatypes):
        return('                <input type="hidden" name="_datatypes" value=' + myb64doublequote(json.dumps(datatypes)) + '/>\n')
    return ('')

def varname_tag(varnames):
    if len(varnames):
        return('                <input type="hidden" name="_varnames" value=' + myb64doublequote(json.dumps(varnames)) + '/>\n')
    return ('')

def icon_html(status, name, width_value=1.0, width_units='em'):
    the_image = status.question.interview.images.get(name, None)
    if the_image.attribution is not None:
        status.attributions.add(the_image.attribution)
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

def signature_html(status, debug, root, extra_scripts, validation_rules):
    if (status.continueLabel):
        continue_label = markdown_to_html(status.continueLabel, trim=True)
    else:
        continue_label = word('Done')
    output = '    <div class="sigpage" id="sigpage">\n      <div class="sigheader" id="sigheader">\n        <div class="siginnerheader">\n          <a id="new" class="signavbtn signav-left">' + word('Clear') + '</a>\n          <a id="save" class="signavbtn signav-right">' + continue_label + '</a>\n          <div class="sigtitle">' + word('Sign Your Name') + '</div>\n        </div>\n      </div>\n      <div class="sigtoppart" id="sigtoppart">\n        <div id="errormess" class="sigerrormessage signotshowing">' + word("You must sign your name to continue.") + '</div>\n        '
    if status.questionText:
        output += markdown_to_html(status.questionText, trim=True)
    output += '\n      </div>'
    if status.subquestionText:
        output += '\n      <div class="sigmidpart">\n        ' + markdown_to_html(status.subquestionText) + '\n      </div>'
    output += '\n      <div id="sigcontent"><p style="text-align:center;border-style:solid;border-width:1px">' + word('Loading.  Please wait . . . ') + '</p></div>\n      <div class="sigbottompart" id="sigbottompart">\n        '
    if (status.underText):
        output += markdown_to_html(status.underText, trim=True)
    output += '\n      </div>\n    </div>\n    <form action="' + root + '" id="daform" method="POST"><input type="hidden" name="_save_as" value="' + escape_id(status.question.fields[0].saveas) + '"/><input type="hidden" id="_the_image" name="_the_image" value=""/><input type="hidden" id="_success" name="_success" value="0"/>'
    output += tracker_tag(status)
    output += '</form>\n'
    add_validation(extra_scripts, validation_rules)
    return output

bad_list = ['div', 'option']

good_list = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'button', 'textarea', 'note']

def to_text(html_doc, terms):
    output = ""
    soup = BeautifulSoup(html_doc, 'html.parser')
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title', 'audio', 'video', 'pre', 'attribution'])]
    [s.extract() for s in soup.find_all(hidden)]
    [s.extract() for s in soup.find_all('div', {'class': 'invisible'})]
    for s in soup.find_all(do_show):
        if s.name in ['input', 'textarea', 'img'] and s.has_attr('alt'):
            words = s.attrs['alt']
            if s.has_attr('placeholder'):
                words += ", " + s.attrs['placeholder']
        else:
            words = s.get_text()
        words = re.sub(r'\n\s*', ' ', words, flags=re.DOTALL)
        output += words + "\n"
    for s in soup.find_all('a'):
        if s.has_attr('class') and s.attrs['class'][0] == 'daterm' and s.has_attr('data-content'):
            terms[s.string] = s.attrs['data-content']
    output = re.sub(ur'\u201c', '"', output)
    output = re.sub(ur'\u201d', '"', output)
    output = re.sub(ur'\u2018', "'", output)
    output = re.sub(ur'\u2019', "'", output)
    output = re.sub(ur'\u201b', "'", output)
    output = re.sub(r'&amp;gt;', '>', output)
    output = re.sub(r'&amp;lt;', '<', output)
    output = re.sub(r'&gt;', '>', output)
    output = re.sub(r'&lt;', '<', output)
    output = re.sub(r'<[^>]+>', '', output)
    output = re.sub(r'\n$', '', output)
    output = re.sub(r'  +', ' ', output)
    return output

def do_show(element):
    if re.match('<!--.*-->', str(element), re.DOTALL):
        return False
    if element.name in ['option'] and element.has_attr('selected'):
        return True    
    if element.name in bad_list:
        return False
    if element.name in ['img', 'input'] and element.has_attr('alt'):
        return True
    if element.name in good_list:
        return True
    if element.parent and element.parent.name in good_list:
        return False
    if element.string:
        return True
    if re.match(r'\s+', element.get_text()):
        return False
    return False

def hidden(element):
    if element.name == 'input':
        if element.has_attr('type'):
            if element.attrs['type'] == 'hidden':
                return True
    return False

def get_choices_with_abb(status, field, terms=dict()):
    choice_list = get_choices(status, field)
    data = dict()
    while True:
        success = True
        data['keys'] = list()
        data['abb'] = dict()
        data['abblower'] = dict()
        data['label'] = list()
        for choice in choice_list:
            flabel = to_text(markdown_to_html(choice[0], trim=False, status=status, strip_newlines=True), terms).strip()
            success = try_to_abbreviate(choice[0], flabel, data, len(choice_list))
            if not success:
                break
        if success:
            break        
    return data, choice_list
    
def get_choices(interview_status, field):
    question = interview_status.question
    choice_list = list()
    if hasattr(field, 'saveas') and field.saveas is not None:
        saveas = myb64unquote(field.saveas)
        if interview_status.question.question_type == "multiple_choice":
            if hasattr(field, 'has_code') and field.has_code:
                pairlist = list(interview_status.selectcompute[field.number])
                for pair in pairlist:
                    choice_list.append([pair[1], saveas, pair[0]])
            else:
                for choice in field.choices:
                    for key in choice:
                        if key == 'image':
                            continue
                        choice_list.append([key, saveas, choice[key]])
        elif hasattr(field, 'choicetype'):
            if field.choicetype == 'compute':
                pairlist = list(interview_status.selectcompute[field.number])
            elif field.datatype in ['checkboxes', 'object_checkboxes'] and field.choicetype != 'manual':
                pairlist = list()
            else:
                pairlist = list(field.selections)
            #if field.datatype in ['object', 'radio', 'object_radio', 'checkboxes', 'object_checkboxes']:
            if field.datatype in ['object_checkboxes']:
                for pair in pairlist:
                    choice_list.append([pair[1], saveas, from_safeid(pair[0])])
            elif field.datatype in ['object', 'object_radio']:
                for pair in pairlist:
                    choice_list.append([pair[1], saveas, from_safeid(pair[0])])
            elif field.datatype in ['checkboxes']:
                for pair in pairlist:
                    choice_list.append([pair[1], saveas + "[" + repr(pair[0]) + "]", True])
            else:
                for pair in pairlist:
                    choice_list.append([pair[1], saveas, pair[0]])
    else:
        indexno = 0
        for choice in field.choices:
            for key in choice:
                if key == 'image':
                    continue
                choice_list.append([key, '_internal["answers"][' + repr(question.name) + ']', indexno])
            indexno += 1
    return choice_list

def try_to_abbreviate(label, flabel, data, length):
    if 'size' not in data:
        data['size'] = 1
    if 'keys' not in data:
        data['keys'] = list()
    if 'abb' not in data:
        data['abb'] = dict()
    if 'abblower' not in data:
        data['abblower'] = dict()
    if 'label' not in data:
        data['label'] = list()
    if length > 8:
        method = 'fromstart'
    else:
        method = 'float'
    startpoint = 0
    endpoint = startpoint + data['size']
    prospective_key = flabel
    while endpoint <= len(flabel):
        prospective_key = flabel[startpoint:endpoint]
        if method == 'float' and re.search(r'[^A-Za-z0-9]', prospective_key):
            startpoint += 1
            endpoint = startpoint + data['size']
            continue
        if method == 'fromstart' and re.search(r'[^A-Za-z0-9]$', prospective_key):
            endpoint += 1
            continue
        if prospective_key.lower() in data['abblower']:
            if method == 'float':
                data['size'] += 1
                return False
            endpoint += 1
            continue
        break
    data['abb'][prospective_key] = label
    data['abblower'][prospective_key.lower()] = label
    data['keys'].append(prospective_key)
    data['label'].append(flabel[0:startpoint] + "[" + prospective_key + ']' + flabel[endpoint:])
    return True

def as_sms(status):
    terms = dict()
    next_variable = None
    qoutput = to_text(markdown_to_html(status.questionText, trim=False, status=status, strip_newlines=True), terms)
    if status.subquestionText:
        qoutput += "\n" + to_text(markdown_to_html(status.subquestionText, status=status), terms)
        #logmessage("output is: " + repr(qoutput))
    qoutput += "XXXXMESSAGE_AREAXXXX"
    if len(status.question.fields):
        field = None
        next_field = None
        for the_field in status.question.fields:
            if hasattr(the_field, 'datatype'):
                if the_field.datatype in ['script', 'css']:
                    continue
                if the_field.datatype in ['html', 'note'] and field is not None:
                    continue
                if the_field.datatype in ['note']:
                    qoutput += "\n" + to_text(markdown_to_html(status.extras['note'][the_field.number], status=status), terms)
                    continue
                if the_field.datatype in ['html']:
                    qoutput += "\n" + to_text(status.extras['html'][the_field.number].rstrip())
                    continue
            #logmessage("field number is " + str(the_field.number))
            if not hasattr(the_field, 'saveas'):
                logmessage("as_sms: field has no saveas")
                continue
            if the_field.number not in status.current_info['skip']:
                #logmessage("field is not defined yet")
                if field is None:
                    field = the_field
                elif next_field is None:
                    next_field = the_field
                continue
        if field is None:
            logmessage("as_sms: field seemed to be defined already?")
            field = status.question.fields[0]
            #return dict(question=qoutput, help=None, next=next_variable)
        label = None
        next_label = ''
        if next_field is not None:
            next_variable = myb64unquote(next_field.saveas)
            if hasattr(next_field, 'label') and status.labels[next_field.number] not in ["no label", ""]:
                next_label = ' (' + word("Next will be") + ' ' + to_text(markdown_to_html(status.labels[next_field.number], trim=False, status=status, strip_newlines=True), terms) + ')'
        if hasattr(field, 'label') and status.labels[field.number] != "no label":
            label = to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), terms)
        question = status.question
        # if hasattr(field, 'datatype'):
        #     logmessage("as_sms: data type is " + field.datatype)
        # else:
        #     logmessage("as_sms: data type is undefined")
        if question.question_type == "settrue":
            qoutput += "\n" + word("Type ok to continue.")
        elif question.question_type in ["yesno", "noyes"] or (hasattr(field, 'datatype') and (field.datatype in ['yesno', 'yesnowide', 'noyes', 'noyeswide'] or (field.datatype == 'boolean' and question.question_type == 'fields'))):
            if question.question_type == 'fields' and label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word("Type [y]es or [n]o.")
        elif question.question_type in ["yesnomaybe"] or (hasattr(field, 'datatype') and (field.datatype in ['yesnomaybe', 'yesnowidemaybe', 'noyesmaybe', 'noyesmaybe', 'noyeswidemaybe'] or (field.datatype == 'threestate' and question.question_type == 'fields'))):
            if question.question_type == 'fields' and label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word("Type [y]es, [n]o, or [d]on't know")
        elif question.question_type == 'multiple_choice' or hasattr(field, 'choicetype') or (hasattr(field, 'datatype') and field.datatype in ['object', 'checkboxes', 'object_checkboxes']):
            if question.question_type == 'fields' and label:
                qoutput += "\n" + label + ":" + next_label
            data, choice_list = get_choices_with_abb(status, field, terms=terms)
            qoutput += "\n" + word("Choices:")
            if hasattr(field, 'shuffle') and field.shuffle:
                random.shuffle(data['label'])
            for the_label in data['label']:
                qoutput += "\n" + the_label
            if hasattr(field, 'datatype') and field.datatype in ['checkboxes', 'object_checkboxes']:
                qoutput += "\n" + word("Type your selection(s), separated by commas, or type none.")
            else:
                if status.extras['required'][field.number]:
                    if len(choice_list) == 1:
                        qoutput += "\n" + word("Type") + " " + data['keys'][0] + " " + word("to proceed.")
                    else:
                        qoutput += "\n" + word("Type your selection.")
                else:
                    qoutput += "\n" + word("Type your selection, or type skip to move on without selecting.")
        elif hasattr(field, 'datatype') and field.datatype == 'range':
            max_string = str(int(status.extras['max'][field.number]))
            min_string = str(int(status.extras['min'][field.number]))
            if label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word('Type a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string
        elif hasattr(field, 'datatype') and field.datatype in ['file', 'files', 'camera']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            qoutput += "\n" + word('Please send an image or file.')
        elif hasattr(field, 'datatype') and field.datatype in ['camcorder']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word('Please send a video.')
        elif hasattr(field, 'datatype') and field.datatype in ['microphone']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            qoutput += "\n" + word('Please send an audio clip.')
        elif hasattr(field, 'datatype') and field.datatype in ['number', 'float', 'integer']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word('Type a number.')
        elif hasattr(field, 'datatype') and field.datatype in ['currency']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word('Type a currency value.')
        elif hasattr(field, 'datatype') and field.datatype in ['date']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            qoutput += "\n" + word('Type a date.')
        elif hasattr(field, 'datatype') and field.datatype in ['email']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word('Type an e-mail address.')
        else:
            if label:
                if status.extras['required'][field.number]:
                    qoutput += "\n" + word("Type the") + " " + label + "." + next_label
                else:
                    qoutput += "\n" + word("Type the") + " " + label + " " + word("or type skip to leave blank.") + next_label
    if len(status.helpText) or len(terms):
        houtput = ''
        for help_section in status.helpText:
            if houtput != '':
                houtput += "\n"
            if help_section['heading'] is not None:
                houtput += '== ' + to_text(markdown_to_html(help_section['heading'], trim=False, status=status, strip_newlines=True), terms) + ' =='
            else:
                houtput += '== ' + word('Help with this question') + ' =='
            houtput += "\n" + to_text(markdown_to_html(help_section['content'], trim=False, status=status, strip_newlines=True), terms)
        if len(terms):
            if houtput != '':
                houtput += "\n"
            houtput += word("== Terms used: ==")
            for term, definition in terms.iteritems():
                houtput += "\n" + term + ': ' + definition
        #houtput += "\n" + word("You can type question to read the question again.")
    else:
        houtput = None
    if status.question.helptext is not None:
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + word("Type help for additional assistance.") + 'XXXXMESSAGE_AREAXXXX', qoutput)
    elif len(terms):
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + word("Type help to see definitions of words.") + 'XXXXMESSAGE_AREAXXXX', qoutput)
    # if status.question.question_type == 'deadend':
    #     return dict(question=qoutput, help=houtput)
    return dict(question=qoutput, help=houtput, next=next_variable)

def as_html(status, extra_scripts, extra_css, url_for, debug, root, validation_rules):
    decorations = list()
    uses_audio_video = False
    audio_text = ''
    video_text = ''
    datatypes = dict()
    varnames = dict()
    onchange = list()
    if status.continueLabel:
        continue_label = markdown_to_html(status.continueLabel, trim=True)
    else:
        continue_label = word('Continue')        
    if status.question.script is not None:
        extra_scripts.append(status.question.script)
    if status.audiovideo is not None:
        uses_audio_video = True
        audio_urls = get_audio_urls(status.audiovideo)
        if len(audio_urls):
            audio_text += '<div>\n' + audio_control(audio_urls) + '</div>\n'
        video_urls = get_video_urls(status.audiovideo)
        if len(video_urls):
            video_text += '<div>\n' + video_control(video_urls) + '</div>\n'
    if status.using_screen_reader and 'question' in status.screen_reader_links:
        audio_text += '<div>\n' + audio_control(status.screen_reader_links['question'], preload="none") + '</div>\n'
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
                    if 'extension' in filename and filename['extension'] == 'svg' and 'width' in filename:
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
    master_output += '          <section id="question" class="tab-pane active col-lg-6 col-md-8 col-sm-10">\n'
    output = ""
    if status.question.question_type in ["yesno", "yesnomaybe"]:
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += '                <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
        output += '                <div class="btn-toolbar">\n                  <button class="btn btn-primary btn-lg " name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True">' + status.question.yes() + '</button>\n                  <button class="btn btn-lg btn-info" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False">' + status.question.no() + '</button>'
        if status.question.question_type == 'yesnomaybe':
            output += '\n                  <button class="btn btn-lg btn-warning" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None">' + status.question.maybe() + '</button>'
        output += '\n                </div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += varname_tag(varnames)
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type in ["noyes", "noyesmaybe"]:
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += '                <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
        output += '                <div class="btn-toolbar">\n                  <button class="btn btn-primary btn-lg" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False">' + status.question.yes() + '</button>\n                  <button class="btn btn-lg btn-info" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True">' + status.question.no() + '</button>'
        if status.question.question_type == 'noyesmaybe':
            output += '\n                  <button class="btn btn-lg btn-warning" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None">' + status.question.maybe() + '</button>'
        output += '\n                </div>\n'
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += varname_tag(varnames)
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == "review":
        fieldlist = list()
        for field in status.question.fields:
            if not status.extras['ok'][field.number]:
                continue
            if hasattr(field, 'extras'):
                if 'script' in field.extras and 'script' in status.extras and field.number in status.extras['script']:
                    extra_scripts.append(status.extras['script'][field.number])
                if 'css' in field.extras and 'css' in status.extras and field.number in status.extras['css']:
                    extra_css.append(status.extras['css'][field.number])
            if hasattr(field, 'datatype'):
                if field.datatype == 'html' and 'html' in status.extras and field.number in status.extras['html']:
                    fieldlist.append('                <div class="form-group' + req_tag +'"><div class="col-md-12"><note>' + status.extras['html'][field.number].rstrip() + '</note></div></div>\n')
                    continue
                elif field.datatype == 'note' and 'note' in status.extras and field.number in status.extras['note']:
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status, strip_newlines=True) + '</div></div>\n')
                    continue
                elif field.datatype in ['script', 'css']:
                    continue
                elif field.datatype == 'button' and hasattr(field, 'label') and field.number in status.helptexts:
                    fieldlist.append('                <div class="row"><div class="col-md-12"><a class="label label-success review-action" href="' + url_action(field.action) + '">' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a>' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div></div>\n')
                    continue
            if hasattr(field, 'label'):
                fieldlist.append('                <div class="form-group"><div class="col-md-12"><a href="' + url_action(field.action) + '">' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a></div></div>\n')
                if field.number in status.helptexts:
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div></div>\n')
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" class="form-horizontal" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if (len(fieldlist)):
            output += "".join(fieldlist)
        if status.continueLabel:
            resume_button_label = markdown_to_html(status.continueLabel, trim=True)
        else:
            resume_button_label = word('Resume')
        output += '                <div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">' + resume_button_label + '</button></div>\n'
        output += tracker_tag(status)
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == "fields":
        enctype_string = ""
        fieldlist = list()
        checkboxes = list()
        files = list()
        checkbox_validation = False
        for field in status.question.fields:
            if not status.extras['ok'][field.number]:
                continue
            if status.extras['required'][field.number]:
                req_tag = ' required'
            else:
                req_tag = ''
            if hasattr(field, 'extras'):
                if 'script' in field.extras and 'script' in status.extras:
                    extra_scripts.append(status.extras['script'][field.number])
                if 'css' in field.extras and 'css' in status.extras:
                    extra_css.append(status.extras['css'][field.number])
                #fieldlist.append("<div>datatype is " + str(field.datatype) + "</div>")
                if 'show_if_var' in field.extras and 'show_if_val' in status.extras and hasattr(field, 'saveas'):
                    fieldlist.append('                <div class="showif" data-saveas="' + escape_id(field.saveas) + '" data-showif-sign="' + escape_id(field.extras['show_if_sign']) + '" data-showif-var="' + escape_id(field.extras['show_if_var']) + '" data-showif-val=' + noquote(unicode(status.extras['show_if_val'][field.number])) + '>\n')
            if hasattr(field, 'datatype'):
                if field.datatype == 'html':
                    fieldlist.append('                <div class="form-group' + req_tag +'"><div class="col-md-12"><note>' + status.extras['html'][field.number].rstrip() + '</note></div></div>\n')
                    continue
                elif field.datatype == 'note':
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status, strip_newlines=True) + '</div></div>\n')
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
            if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                onchange.append(field.saveas)
            if hasattr(field, 'saveas'):
                varnames[safeid('_field_' + str(field.number))] = field.saveas
                if hasattr(field, 'extras') and 'show_if_var' in field.extras and 'show_if_val' in status.extras:
                    the_saveas = safeid('_field_' + str(field.number))
                else:
                    the_saveas = field.saveas
                if status.extras['required'][field.number]:
                    #sys.stderr.write(field.datatype + "\n")
                    validation_rules['rules'][the_saveas] = {'required': True}
                    validation_rules['messages'][the_saveas] = {'required': word("This field is required.")}
                else:
                    validation_rules['rules'][the_saveas] = {'required': False}
                for key in ['minlength', 'maxlength']:
                    if hasattr(field, 'extras') and key in field.extras and key in status.extras:
                        #sys.stderr.write("Adding validation rule for " + str(key) + "\n")
                        validation_rules['rules'][the_saveas][key] = int(status.extras[key][field.number])
            if hasattr(field, 'datatype'):
                if field.datatype == 'date':
                    validation_rules['rules'][the_saveas]['date'] = True
                    validation_rules['messages'][the_saveas]['date'] = word("You need to enter a valid date.")
                if field.datatype == 'email':
                    validation_rules['rules'][the_saveas]['email'] = True
                    if status.extras['required'][field.number]:
                        validation_rules['rules'][the_saveas]['minlength'] = 1
                        validation_rules['messages'][the_saveas]['minlength'] = word("This field is required.")
                    validation_rules['messages'][the_saveas]['email'] = word("You need to enter a complete e-mail address.")
                if field.datatype in ['number', 'currency', 'float', 'integer']:
                    validation_rules['rules'][the_saveas]['number'] = True
                    validation_rules['messages'][the_saveas]['number'] = word("You need to enter a number.")
                    #sys.stderr.write("Considering adding validation rule\n")
                    for key in ['min', 'max']:
                        if hasattr(field, 'extras') and key in field.extras and key in status.extras:
                            #sys.stderr.write("Adding validation rule for " + str(key) + "\n")
                            validation_rules['rules'][the_saveas][key] = int(status.extras[key][field.number])
                if (field.datatype in ['files', 'file', 'camera', 'camcorder', 'microphone']):
                    enctype_string = ' enctype="multipart/form-data"'
                    files.append(field.saveas)
                if field.datatype in ['boolean', 'threestate']:
                    checkboxes.append(field.saveas)
                elif field.datatype in ['checkboxes', 'object_checkboxes']:
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
                            checkboxes.append(safeid(from_safeid(field.saveas) + "[" + myb64quote(pair[0]) + "]"))
            if hasattr(field, 'label'):
                if status.labels[field.number] == 'no label':
                    fieldlist.append('                <div class="form-group' + req_tag +'"><div class="col-md-12">' + input_for(status, field, extra_scripts, wide=True) + '</div></div>\n')
                elif hasattr(field, 'inputtype') and field.inputtype in ['yesnowide', 'noyeswide']:
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + input_for(status, field, extra_scripts) + '</div></div>\n')
                elif hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes']:
                    fieldlist.append('                <div class="form-group' + req_tag +'"><div class="col-sm-offset-4 col-sm-8">' + input_for(status, field, extra_scripts) + '</div></div>\n')
                else:
                    fieldlist.append('                <div class="form-group' + req_tag + '"><label for="' + escape_id(field.saveas) + '" class="control-label col-sm-4">' + helptext_start + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + helptext_end + '</label><div class="col-sm-8 fieldpart">' + input_for(status, field, extra_scripts) + '</div></div>\n')
            if hasattr(field, 'extras') and 'show_if_var' in field.extras and 'show_if_val' in status.extras and hasattr(field, 'saveas'):
                fieldlist.append('                </div>\n')
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" class="form-horizontal" method="POST"' + enctype_string + '>\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        #output += '<div class="row">'
        if video_text:
            output += indent_by(video_text, 12)
        if (len(fieldlist)):
            output += "".join(fieldlist)
        else:
            output += "                <p>Error: no fields</p>\n"
        #output += '</div>\n'
        if len(checkboxes):
            output += '                <input type="hidden" name="_checkboxes" value=' + myb64doublequote(json.dumps(checkboxes)) + '/>\n'
        if len(files):
            output += '                <input type="hidden" name="_files" value=' + myb64doublequote(json.dumps(files)) + '/>\n'
            init_string = '<script>'
            for saveasname in files:
                init_string += '$("#' + saveasname + '").fileinput();' + "\n"
            init_string += '</script>'
            #extra_scripts.append('<script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>' + init_string)
            extra_scripts.append(init_string)
            #extra_css.append('<link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />')
        output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '                <div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">' + continue_label + '</button></div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += varname_tag(varnames)
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == "settrue":
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = "boolean"
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '                <div class="form-actions"><button type="submit" class="btn btn-lg btn-primary" name="' + escape_id(status.question.fields[0].saveas) + '" value="True"> ' + continue_label + '</button></div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += varname_tag(varnames)
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == "multiple_choice":
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        if status.question.fields[0].number in status.defaults and type(status.defaults[status.question.fields[0].number]) in [str, unicode, int, float]:
            defaultvalue = unicode(status.defaults[status.question.fields[0].number])
        else:
            defaultvalue = None
        if hasattr(status.question.fields[0], 'datatype'):
            datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += '                <div id="errorcontainer" class="alert alert-danger" role="alert" style="display:none"></div>\n'
        output += '                <p class="sr-only">' + word('Your choices are:') + '</p>\n'
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
                        if defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        if pair[0] is not None:
                            output += '                <div class="row"><div class="col-md-6"><input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + escape_id(status.question.fields[0].saveas) + '_' + str(id_index) + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="radio" value="' + unicode(pair[0]) + '"' + ischecked + '/></div></div>\n'
                        else:
                            output += '                <div class="form-group"><div class="col-md-12">' + markdown_to_html(pair[1], status=status) + '</div></div>\n'
                        id_index += 1
                else:
                    id_index = 0
                    choicelist = list(status.question.fields[0].choices)
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(choicelist)
                    for choice in choicelist:
                        if 'image' in choice:
                            the_icon = icon_html(status, choice['image']) + ' '
                        else:
                            the_icon = ''
                        for key in choice:
                            if key == 'image':
                                continue
                            formatted_key = markdown_to_html(key, status=status, trim=True, escape=True)
                            if defaultvalue is not None and unicode(choice[key]) == unicode(defaultvalue):
                                ischecked = ' checked="checked"'
                            else:
                                ischecked = ''
                            output += '                <div class="row"><div class="col-md-6"><input alt="' + formatted_key + '" data-labelauty="' + docassemble.base.filter.my_escape(the_icon) + formatted_key + '|' + docassemble.base.filter.my_escape(the_icon) + formatted_key + '" class="to-labelauty radio-icon" id="' + escape_id(status.question.fields[0].saveas) + '_' + str(id_index) + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="radio" value="' + unicode(choice[key]) + '"' + ischecked + '/></div></div>\n'
                        id_index += 1
                validation_rules['ignore'] = None
                validation_rules['rules'][status.question.fields[0].saveas] = {'required': True}
                validation_rules['messages'][status.question.fields[0].saveas] = {'required': word("You need to select one.")}
            else:
                indexno = 0
                for choice in status.question.fields[0].choices:
                    if 'image' in choice:
                        the_icon = icon_html(status, choice['image']) + ' '
                    else:
                        the_icon = ''
                    id_index = 0
                    for key in choice:
                        if key == 'image':
                            continue
                        formatted_key = markdown_to_html(key, status=status, trim=True, escape=True)
                        output += '                <div class="row"><div class="col-md-6"><input alt="' + formatted_key + '" data-labelauty="' + docassemble.base.filter.my_escape(the_icon) + formatted_key + '|' + docassemble.base.filter.my_escape(the_icon) + formatted_key + '" class="to-labelauty radio-icon" id="multiple_choice_' + str(indexno) + '_' + str(id_index) + '" name="X211bHRpcGxlX2Nob2ljZQ==" type="radio" value="' + str(indexno) + '"/></div></div>\n'
                        id_index += 1
                    indexno += 1
                    validation_rules['rules']['X211bHRpcGxlX2Nob2ljZQ=='] = {'required': True}
                    validation_rules['messages']['X211bHRpcGxlX2Nob2ljZQ=='] = {'required': word("You need to select one.")}
            output += '                <br/>\n'
            output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
            output += '                <button class="btn btn-lg btn-primary" type="submit">' + continue_label + '</button>\n'
        else:
            #output += '                <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
            output += '                <div class="btn-toolbar">\n'
            if hasattr(status.question.fields[0], 'saveas'):
                btn_class = ' btn-primary'
                if hasattr(status.question.fields[0], 'has_code') and status.question.fields[0].has_code:
                    pairlist = list(status.selectcompute[status.question.fields[0].number])
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if pair[0] is not None:
                            output += '                  <button type="submit" class="btn btn-lg' + btn_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value="' + unicode(pair[0]) + '"> ' + markdown_to_html(pair[1], status=status, trim=True, do_terms=False) + '</button>\n'
                        else:
                            output += markdown_to_html(pair[1], status=status)
                else:
                    choicelist = list(status.question.fields[0].choices)
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(choicelist)
                    for choice in choicelist:
                        if 'image' in choice:
                            the_icon = '<div>' + icon_html(status, choice['image'], width_value=4.0) + '</div>';
                            btn_class = ' btn-default btn-da-custom'
                        else:
                            the_icon = ''
                        for key in choice:
                            if key == 'image':
                                continue
                            output += '                  <button type="submit" class="btn btn-lg' + btn_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value="' + unicode(choice[key]) + '"> ' + the_icon + markdown_to_html(key, status=status, trim=True, do_terms=False) + '</button>\n'
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
                        output += '                  <button type="submit" class="btn btn-lg' + btn_class + '" name="X211bHRpcGxlX2Nob2ljZQ==" value="' + str(indexno) + '">' + the_icon + markdown_to_html(key, status=status, trim=True, do_terms=False, strip_newlines=True) + '</button>\n'
                    indexno += 1
            output += '                </div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += varname_tag(varnames)
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == 'deadend':
        output += indent_by(audio_text, 12) + '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
    else:
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" class="form-horizontal" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '                <div class="form-actions"><button class="btn btn-lg btn-primary" type="submit">' + continue_label + '</button></div>\n'
        #output += question_name_tag(status.question)
        output += tracker_tag(status)
        output += '              </fieldset>\n            </form>\n'
    if len(status.attachments) > 0:
        output += '            <br/>\n'
        if len(status.attachments) > 1:
            output += '            <div class="alert alert-success" role="alert">' + word('attachment_message_plural') + '</div>\n'
        else:
            output += '            <div class="alert alert-success" role="alert">' + word('attachment_message_singular') + '</div>\n'
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
            output += '            <div><h3>' + markdown_to_html(attachment['name'], trim=True, status=status, strip_newlines=True) + '</h3></div>\n'
            if attachment['description']:
                output += '            <div>' + markdown_to_html(attachment['description'], status=status, strip_newlines=True) + '</div>\n'
            output += '            <div class="tabbable">\n'
            if True or show_preview or show_markdown:
                output += '              <ul class="nav nav-tabs">\n'
                if show_download:
                    output += '                <li class="active"><a href="#download' + str(attachment_index) + '" data-toggle="tab">' + word('Download') + '</a></li>\n'
                if show_preview:
                    output += '                <li><a href="#preview' + str(attachment_index) + '" data-toggle="tab">' + word('Preview') + '</a></li>\n'
                if show_markdown:
                    output += '                <li><a href="#markdown' + str(attachment_index) + '" data-toggle="tab">' + word('Markdown') + '</a></li>\n'
                output += '              </ul>\n'
            output += '              <div class="tab-content">\n'
            if show_download:
                output += '                <div class="tab-pane active" id="download' + str(attachment_index) + '">\n'
                if multiple_formats:
                    output += '                  <p>' + word('save_as_multiple') + '</p>\n'
                #else:
                    #output += '                  <p>' + word('save_as_singular') + '</p>\n'
                if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '                  <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=pdf"><i class="glyphicon glyphicon-print"></i> PDF</a> (' + word('pdf_message') + ')</p>\n'
                if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '                  <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=rtf"><i class="glyphicon glyphicon-pencil"></i> RTF</a> (' + word('rtf_message') + ')</p>\n'
                if 'docx' in attachment['valid_formats']:
                    output += '                  <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=docx"><i class="glyphicon glyphicon-pencil"></i> DOCX</a> (' + word('docx_message') + ')</p>\n'
                if debug and ('tex' in attachment['valid_formats'] or '*' in attachment['valid_formats']):
                    output += '                  <p><a href="?filename=' + urllib.quote(status.question.interview.source.path, '') + '&question=' + str(status.question.number) + '&index=' + str(attachment_index) + '&format=tex"><i class="glyphicon glyphicon-pencil"></i> LaTeX</a> (' + word('tex_message') + ')</p>\n'
                output += '                </div>\n'
            if show_preview:
                output += '                <div class="tab-pane" id="preview' + str(attachment_index) + '">\n'
                output += '                  <blockquote>' + unicode(attachment['content']['html']) + '</blockquote>\n'
                output += '                </div>\n'
            if show_markdown:
                if 'html' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    md_format = 'html'
                else:
                    for format_type in attachment['valid_formats']:
                        md_format = format_type
                        break
                output += '                <div class="tab-pane" id="markdown' + str(attachment_index) + '">\n'
                output += '                  <pre>' + unicode(attachment['markdown'][md_format]) + '</pre>\n'
                output += '                </div>\n'
            output += '              </div>\n            </div>\n'
            attachment_index += 1
        if status.question.allow_emailing:
            if len(status.attachments) > 1:
                email_header = word("E-mail these documents")
            else:
                email_header = word("E-mail this document")
            if status.current_info['user']['is_authenticated'] and status.current_info['user']['email']:
                default_email = status.current_info['user']['email']
            else:
                default_email = ''
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
                        <div class="form-group"><label for="_attachment_email_address" class="control-label col-sm-4">""" + word('E-mail address') + """</label><div class="col-sm-8"><input alt=""" + '"' + word ("Input box") + '"' + """ class="form-control" type="email" name="_attachment_email_address" id="_attachment_email_address" value=""" + '"' + str(default_email) + '"' + """/></div></div>"""
            if editable_included:
                output += """
                        <div class="form-group"><div class="col-sm-4"></div><div class="col-sm-8"><input alt="' + word ("Check box") + ", " + word('Include ' + editable_name + ' for editing') + '" type="checkbox" value="True" name="_attachment_include_editable" id="_attachment_include_editable"/>&nbsp;<label for="_attachment_include_editable" class="nobold">""" + word('Include ' + editable_name + ' for editing') + '</label></div></div>\n'
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
            extra_scripts.append("""<script>\n      $("#emailform").validate(""" + json.dumps({'rules': {'_attachment_email_address': {'minlength': 1, 'required': True, 'email': True}}, 'messages': {'_attachment_email_address': {'required': word("An e-mail address is required."), 'email': word("You need to enter a complete e-mail address.")}}, 'errorClass': 'help-inline'}) + """);\n    </script>""")
    if len(status.attributions):
        output += '            <br/><br/><br/><br/><br/><br/><br/>\n'
    for attribution in sorted(status.attributions):
        output += '            <div><attribution><small>' + markdown_to_html(attribution, strip_newlines=True) + '</small></attribution></div>\n'
    if status.using_screen_reader:
        status.screen_reader_text['question'] = unicode(output)
    master_output += output
    master_output += '          </section>\n'
    master_output += '          <section id="help" class="tab-pane col-lg-6 col-md-8 col-sm-10">\n'
    output = '<div><a id="backToQuestion" data-toggle="tab" href="#question" class="btn btn-info btn-md"><i class="glyphicon glyphicon-arrow-left"></i> ' + word("Back to question") + '</a></div>'
    output += """
<div id="daPhoneMessage" class="row invisible">
  <div class="col-md-12">
    <h3>""" + word("Telephone assistance") + """</h3>
    <p></p>
  </div>
</div>
<div id="daChatBox" class="invisible">
  <div class="row">
    <div class="col-md-12 dachatbutton">
      <a id="daChatOnButton" class="label label-success">""" + word("Activate chat") + """</a>
      <a id="daChatOffButton" class="label label-warning">""" + word("Turn off chat") + """</a>
      <h3>""" + word("Live chat") + """</h3>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <ul class="list-group dachatbox" id="daCorrespondence"></ul>
    </div>
  </div>
  <form id="dachat" autocomplete="off">
    <div class="row">
      <div class="col-md-12">
        <div class="input-group">
            <input type="text" class="form-control" id="daMessage" placeholder=""" + '"' + word("Type your message here.") + '"' + """>
            <span class="input-group-btn"><button class="btn btn-default" id="daSend" type="button">""" + word("Send") + """</button></span>
        </div>
      </div>
    </div>
  </form>
  <div class="row invisible">
    <div class="col-md-12">
      <p id="daPushResult"></p>
    </div>
  </div>
  <div class="row topspace">
    <div class="col-md-12">
      <p>
        <span class="peer-message" id="peerMessage"></span>
        <span class="peer-message" id="peerHelpMessage"></span>
      </p>
    </div>
  </div>
</div>
"""
    if len(status.helpText):
        if status.using_screen_reader and 'help' in status.screen_reader_links:
            output += '            <div>\n' + indent_by(audio_control(status.screen_reader_links['help'], preload="none"), 14) + '            </div>\n'
        for help_section in status.helpText:
            if help_section['heading'] is not None:
                output += '            <div class="page-header"><h3>' + help_section['heading'] + '</h3></div>\n'
            else:
                output += '            <div class="page-header"><h3>' + word('Help with this question') + '</h3></div>\n'
            if help_section['audiovideo'] is not None:
                uses_audio_video = True
                audio_urls = get_audio_urls(help_section['audiovideo'])
                if len(audio_urls):
                    output += '            <div>\n' + indent_by(audio_control(audio_urls), 14) + '            </div>\n'
                video_urls = get_video_urls(help_section['audiovideo'])
                if len(video_urls):
                    output += '            <div>\n' + indent_by(video_control(video_urls), 14) + '            </div>\n'
            output += markdown_to_html(help_section['content'], status=status, indent=12)
        if len(status.attributions):
            output += '            <br/><br/><br/><br/><br/><br/><br/>\n'
        for attribution in sorted(status.attributions):
            output += '            <div><attribution><small>' + markdown_to_html(attribution, strip_newlines=True) + '</small></attribution></div>\n'
        if status.using_screen_reader:
            status.screen_reader_text['help'] = unicode(output)
    master_output += output
    master_output += '          </section>\n'
    # if status.question.question_type == "fields":
    #     extra_scripts.append("""\
    # <script>
    #   $("#daform").find('button[type="submit"]').prop("disabled", true);
    #   daform = $("#daform");
    #   $("#daform input, #daform select, #daform textarea").on('change input propertychange paste', function(){
    #     if (daform.valid()){
    #       $("#daform").find('button[type="submit"]').prop("disabled", false);
    #     }
    #     else{
    #       $("#daform").find('button[type="submit"]').prop("disabled", true);
    #     }
    #   });
    # </script>""")
    add_validation(extra_scripts, validation_rules)
    for element_id_unescaped in onchange:
        element_id = re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', element_id_unescaped)
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
      function daAddMarker(map, marker_info, show_marker){
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
        if(show_marker){
          map.infowindow.setContent(marker_info.info);
          map.infowindow.open(map.map, marker);
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
          if (marker_length == 1){
            show_marker = true
          }
          else{
            show_marker = false
          }
          for (var j = 0; j < marker_length; j++){
            var new_marker = daAddMarker(maps[i], the_map.markers[j], show_marker);
            bounds.extend(new_marker.getPosition());
          }
          if (marker_length > 1){
            maps[i].map.fitBounds(bounds);
          }
        }
      }
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?signed_in=true&callback=daInitMap"></script>
"""
        extra_scripts.append(map_js)
    return master_output

def add_validation(extra_scripts, validation_rules):
    extra_scripts.append("""<script>
      var validation_rules = """ + json.dumps(validation_rules) + """;
      validation_rules.submitHandler = function(form){
        //form.submit();
        dadisable = setTimeout(function(){
          $("#daform").find('input[type="submit"]').prop("disabled", true);
          $("#daform").find('button[type="submit"]').prop("disabled", true);
        }, 1);
        if ($('#daform input[name="_files"]').length){
          $("#uploadiframe").remove();
          var iframe = $('<iframe name="uploadiframe" id="uploadiframe" style="display: none"></iframe>');
          $("body").append(iframe);
          $(form).attr("target", "uploadiframe");
          $('<input>').attr({
              type: 'hidden',
              name: 'ajax',
              value: '1'
          }).appendTo($(form));
          iframe.load(function(){
            setTimeout(function(){
              daProcessAjax($.parseJSON($("#uploadiframe").contents().text()), form);
            }, 0);
          });
          form.submit();
        }
        else{
          if (daSubmitter != null){
            var input = $("<input>")
              .attr("type", "hidden")
              .attr("name", daSubmitter.name).val(daSubmitter.value);
            $("#daform").append($(input));
          }
          var informed = '';
          if (daInformedChanged){
            informed = '&informed=' + Object.keys(daInformed).join(',');
          }
          $.ajax({
            type: "POST",
            url: $("#daform").attr('action'),
            data: $("#daform").serialize() + '&ajax=1' + informed, 
            success: function(data){
              setTimeout(function(){
                daProcessAjax(data, form);
              }, 0);
            },
            error: function(xhr, status, error){
              setTimeout(function(){
                daProcessAjaxError(xhr, status, error);
              }, 0);
            }
          });
        }
        daSpinnerTimeout = setTimeout(showSpinner, 1000);
        return(false);
      };
      $("#daform").validate(validation_rules);
      $("#backbutton").submit(function(event){
        var informed = '';
        if (daInformedChanged){
          informed = '&informed=' + Object.keys(daInformed).join(',');
        }
        $.ajax({
          type: "POST",
          url: $("#backbutton").attr('action'),
          data: $("#backbutton").serialize() + '&ajax=1' + informed, 
          success: function(data){
            setTimeout(function(){
              daProcessAjax(data, document.getElementById('backbutton'));
            }, 0);
          },
          error: function(xhr, status, error){
            setTimeout(function(){
              daProcessAjaxError(xhr, status, error);
            }, 0);
          }
        });
        event.preventDefault();
      });
    </script>""")

def input_for(status, field, extra_scripts, wide=False):
    output = ""
    if field.number in status.defaults and type(status.defaults[field.number]) in [str, unicode, int, float]:
        defaultvalue = unicode(status.defaults[field.number])
    else:
        defaultvalue = None
    if field.number in status.hints:
        placeholdertext = ' placeholder=' + json.dumps(unicode(status.hints[field.number].replace('\n', ' ')))
    else:
        placeholdertext = ''
    if hasattr(field, 'extras') and 'show_if_var' in field.extras and 'show_if_val' in status.extras and hasattr(field, 'saveas'):
        saveas_string = safeid('_field_' + str(field.number))
    else:
        saveas_string = field.saveas
    if hasattr(field, 'choicetype'):
        if field.choicetype == 'compute':
            pairlist = list(status.selectcompute[field.number])
        else:
            pairlist = list(field.selections)
        if hasattr(field, 'shuffle') and field.shuffle:
            random.shuffle(pairlist)
        if field.datatype in ['checkboxes', 'object_checkboxes']:
            inner_fieldlist = list()
            id_index = 0
            output += '<p class="sr-only">' + word('Checkboxes:') + '</p>'
            for pair in pairlist:
                if pair[0] is not None:
                    inner_field = safeid(from_safeid(saveas_string) + "[" + myb64quote(pair[0]) + "]")
                    #sys.stderr.write("I've got a " + repr(pair[1]) + "\n")
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                    if (len(pair) > 2 and pair[2]) or (defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue)):
                        ischecked = ' checked'
                    else:
                        ischecked = ''
                    inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty checkbox-icon" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"' + ischecked + '/>')
                else:
                    inner_fieldlist.append('<div>' + markdown_to_html(pair[1], status=status) + '</div>')
                id_index += 1
            output += u''.join(inner_fieldlist)
            if field.datatype in ['object_checkboxes']:
                output += '<input type="hidden" name="' + safeid(from_safeid(saveas_string) + ".gathered")+ '" value="True"/>'
        elif field.datatype in ['radio', 'object_radio']:
            inner_fieldlist = list()
            id_index = 0
            output += '<p class="sr-only">' + word('Choices:') + '</p>'
            for pair in pairlist:
                if pair[0] is not None:
                    #sys.stderr.write(str(saveas_string) + "\n")
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                    if (len(pair) > 2 and pair[2]) or (defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair[0]) + '"' + ischecked + '/>')
                else:
                    inner_fieldlist.append('<div>' + markdown_to_html(unicode(pair[1]), status=status) + '</div>')
                id_index += 1
            output += "".join(inner_fieldlist)
        else:
            output += '<p class="sr-only">' + word('Select box') + '</p>'
            output += '<select name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '" >'
            output += '<option value="">' + word('Select...') + '</option>'
            for pair in pairlist:
                if pair[0] is not None:
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, do_terms=False)
                    output += '<option value="' + unicode(pair[0]) + '"'
                    if (len(pair) > 2 and pair[2]) or (defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue)):
                        output += ' selected="selected"'
                    output += '>' + formatted_item + '</option>'
            output += '</select> '
    elif hasattr(field, 'datatype'):
        if field.datatype == 'boolean':
            label_text = markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True, escape=True)
            if hasattr(field, 'inputtype') and field.inputtype in ['yesnoradio', 'noyesradio']:
                output += '<p class="sr-only">' + word('Choices:') + '</p>'
                inner_fieldlist = list()
                id_index = 0
                if field.sign > 0:
                    for pair in [['True', status.question.yes()], ['False', status.question.no()]]:
                        formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                        if (len(pair) > 2 and pair[2]) or (defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair[0]) + '"' + ischecked + '/>')
                        id_index += 1
                else:
                    for pair in [['False', status.question.yes()], ['True', status.question.no()]]:
                        formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                        if (len(pair) > 2 and pair[2]) or (defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair[0]) + '"' + ischecked + '/>')
                        id_index += 1
                output += "".join(inner_fieldlist)
            else:
                if field.sign > 0:
                    output += '<input alt="' + label_text + '" class="to-labelauty checkbox-icon" type="checkbox" value="True" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"'
                else:
                    output += '<input alt="' + label_text + '" class="to-labelauty checkbox-icon" type="checkbox" value="False" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"'
                if defaultvalue:
                    output += ' checked'
                output += '/> '
        elif field.datatype == 'threestate':
            inner_fieldlist = list()
            id_index = 0
            output += '<p class="sr-only">' + word('Choices:') + '</p>'
            if field.sign > 0:
                for pair in [['True', status.question.yes()], ['False', status.question.no()], ['None', status.question.maybe()]]:
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                    if (len(pair) > 2 and pair[2]) or (defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair[0]) + '"' + ischecked + '/>')
                    id_index += 1
            else:
                for pair in [['False', status.question.yes()], ['True', status.question.no()], ['None', status.question.maybe()]]:
                    formatted_item = markdown_to_html(unicode(pair[1]), status=status, trim=True, escape=True)
                    if (len(pair) > 2 and pair[2]) or (defaultvalue is not None and unicode(pair[0]) == unicode(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="to-labelauty radio-icon" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair[0]) + '"' + ischecked + '/>')
                    id_index += 1
            output += "".join(inner_fieldlist)
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
            output += '<input alt="' + word("You can upload a file here") + '" type="file" class="file" data-show-upload="false" data-preview-file-type="text" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + accept + '/>'
            #output += '<div class="fileinput fileinput-new input-group" data-provides="fileinput"><div class="form-control" data-trigger="fileinput"><i class="glyphicon glyphicon-file fileinput-exists"></i><span class="fileinput-filename"></span></div><span class="input-group-addon btn btn-default btn-file"><span class="fileinput-new">' + word('Select file') + '</span><span class="fileinput-exists">' + word('Change') + '</span><input type="file" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + '></span><a href="#" class="input-group-addon btn btn-default fileinput-exists" data-dismiss="fileinput">' + word('Remove') + '</a></div>\n'
        elif field.datatype == 'range':
            ok = True
            for key in ['min', 'max']:
                if not (hasattr(field, 'extras') and key in field.extras and key in status.extras and field.number in status.extras[key]):
                    ok = False
            if ok:
                if defaultvalue is not None:
                    the_default = ' data-slider-value="' + str(defaultvalue) + '"'
                else:
                    the_default = ''
                if 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step']:
                    the_step = ' data-slider-step="' + str(status.extras['step'][field.number]) + '"'
                else:
                    the_step = ''
                max_string = str(int(status.extras['max'][field.number]))
                min_string = str(int(status.extras['min'][field.number]))
                output += '<input alt="' + word('Select a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + the_default + ' data-slider-max="' + max_string + '" data-slider-min="' + min_string + '"' + the_step + '></input>'
                extra_scripts.append('<script>$("#' + escape_for_jquery(saveas_string) + '").slider({tooltip: "always"});</script>\n')
        elif field.datatype == 'area':
            output += '<textarea alt="' + word("Input box") + '" class="form-control" rows="4" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + placeholdertext + '>'
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
            if field.datatype in ['integer', 'float', 'currency', 'number']:
                input_type = 'number'
                if field.datatype == 'integer':
                    step_string = ' step="1"'
                if field.datatype == 'float' or field.datatype == 'number':
                    step_string = ' step="0.01"'
                if field.datatype == 'currency':
                    step_string = ' step="0.01"'
                    output += '<div class="input-group"><span class="input-group-addon" id="addon-' + do_escape_id(saveas_string) + '">' + currency_symbol() + '</span>'
            output += '<input' + defaultstring + placeholdertext + ' alt="' + word("Input box") + '" class="form-control" type="' + input_type + '"' + step_string + ' name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"'
            if field.datatype == 'currency':
                output += ' aria-describedby="addon-' + do_escape_id(saveas_string) + '"/></div><label style="display: none;" for="' + escape_id(saveas_string) + '" class="help-inline" id="' + escape_id(saveas_string) + '-error"></label>'
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

def safeid(text):
    return codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '')

def from_safeid(text):
    return(codecs.decode(text, 'base64').decode('utf-8'))

def escape_id(text):
    return str(text)
    #return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)

def do_escape_id(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\1', text)

def escape_for_jquery(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)

def myb64unquote(the_string):
    return(codecs.decode(the_string, 'base64').decode('utf-8'))
