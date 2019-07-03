# -*- coding: utf-8 -*-
from six import string_types, text_type, PY2
from docassemble.base.functions import word, currency_symbol, url_action, comma_and_list, server
from docassemble.base.util import format_date
from docassemble.base.filter import markdown_to_html, get_audio_urls, get_video_urls, audio_control, video_control, noquote, to_text, my_escape
from docassemble.base.parse import Question, debug
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig
if PY2:
    from urllib import quote as urllibquote
else:
    from urllib.parse import quote as urllibquote
import sys
import os
import re
import json
import random
import sys
import codecs
import datetime

DECORATION_SIZE = daconfig.get('decoration size', 2.0)
DECORATION_UNITS = daconfig.get('decoration units', 'em')
BUTTON_ICON_SIZE = daconfig.get('button icon size', 4.0)
BUTTON_ICON_UNITS = daconfig.get('button icon units', 'em')
if daconfig.get('button size', 'medium') == 'medium':
    BUTTON_CLASS = 'btn-da'
elif daconfig.get('button size', 'large') == 'large':
    BUTTON_CLASS = 'btn-lg btn-da'
else:
    BUTTON_CLASS = 'btn-da'

def tracker_tag(status):
    output = text_type()
    output += '                <input type="hidden" name="csrf_token" value=' + json.dumps(server.generate_csrf()) + '/>\n'
    #restore this, maybe
    #if len(status.next_action):
    #    output += '                <input type="hidden" name="_next_action" value=' + myb64doublequote(json.dumps(status.next_action)) + '/>\n'
    if status.orig_sought is not None:
        output += '                <input type="hidden" name="_event" value=' + myb64doublequote(json.dumps([status.orig_sought])) + ' />\n'
    if status.question.name:
        output += '                <input type="hidden" name="_question_name" value=' + json.dumps(status.question.name) + '/>\n'
    # if 'orig_action' in status.current_info:
    #     output += '                <input type="hidden" name="_action_context" value=' + myb64doublequote(json.dumps(dict(action=status.current_info['orig_action'], arguments=status.current_info['orig_arguments']))) + '/>\n'
    output += '                <input type="hidden" name="_tracker" value=' + json.dumps(str(status.tracker)) + '/>\n'
    if 'track_location' in status.extras and status.extras['track_location']:
        output += '                <input type="hidden" id="da_track_location" name="_track_location" value=""/>\n'
    return output

def datatype_tag(datatypes):
    if len(datatypes):
        return('                <input type="hidden" name="_datatypes" value=' + myb64doublequote(json.dumps(datatypes)) + '/>\n                <input type="hidden" name="_visible" value=""/>\n')
    return ('')

def varname_tag(varnames):
    if len(varnames):
        return('                <input type="hidden" name="_varnames" value=' + myb64doublequote(json.dumps(varnames)) + '/>\n')
    return ('')

def icon_html(status, name, width_value=1.0, width_units='em'):
    #logmessage("icon_html: name is " + repr(name))
    if isinstance(name, dict) and name['type'] == 'decoration':
        name = name['value']
    if not isinstance(name, dict):
        is_decoration = True
        the_image = status.question.interview.images.get(name, None)
        if the_image is None:
            if daconfig.get('default icons', None) == 'font awesome':
                return('<i class="' + daconfig.get('font awesome prefix', 'fas') + ' fa-' + str(name) + '"></i>')
            elif daconfig.get('default icons', None) == 'material icons':
                return('<i class="da-material-icons">' + str(name) + '</i>')
            return('')
        if the_image.attribution is not None:
            status.attributions.add(the_image.attribution)
        url = server.url_finder(str(the_image.package) + ':' + str(the_image.filename))
    else:
        is_decoration = False
        url = name['value']
    if url is None:
        raise Exception("Could not find filename " + str(the_image.filename) + " for image " + str(name) + " in package " + str(the_image.package))
    sizing = 'width:' + str(width_value) + str(width_units) + ';'
    if is_decoration:
        filename = server.file_finder(str(the_image.package) + ':' + str(the_image.filename))
        if 'extension' in filename and filename['extension'] == 'svg' and 'width' in filename and 'height' in filename:
            if filename['width'] and filename['height']:
                sizing += 'height:' + str(width_value * (filename['height']/filename['width'])) + str(width_units) + ';'
        else:
            sizing += 'height:auto;'    
    return('<img alt="" class="daicon" src="' + url + '" style="' + str(sizing) + '"/>')

# def signature_html(status, debug, root, validation_rules):
#     if (status.continueLabel):
#         continue_label = markdown_to_html(status.continueLabel, trim=True)
#     else:
#         continue_label = word('Done')
#     output = '    <div class="sigpage" id="dasigpage">\n      <div class="sigshowsmallblock sigheader" id="dasigheader">\n        <div class="siginnerheader">\n          <a id="danew" class="signavbtn signav-left">' + word('Clear') + '</a>\n          <a id="dasave" class="signavbtn signav-right">' + continue_label + '</a>\n          <div class="sigtitle">'
#     if status.questionText:
#         output += markdown_to_html(status.questionText, trim=True)
#     else:
#         output += word('Sign Your Name')
#     output += '</div>\n        </div>\n      </div>\n      <div class="dasigtoppart" id="dasigtoppart">\n        <div id="daerrormess" class="sigerrormessage signotshowing">' + word("You must sign your name to continue.") + '</div>\n        '
#     output += '\n      </div>'
#     if status.subquestionText:
#         output += '\n      <div class="sigmidpart">\n        ' + markdown_to_html(status.subquestionText) + '\n      </div>'
#     output += '\n      <div id="dasigcontent"><p style="text-align:center;border-style:solid;border-width:1px">' + word('Loading.  Please wait . . . ') + '</p></div>\n      <div class="sigbottompart" id="sigbottompart">\n        '
#     if 'underText'status.extras:
#         output += markdown_to_html(status.extras['underText'], trim=True)
#     output += "\n      </div>"
#     output += """
#       <div class="form-actions sighidesmall sigbuttons">
#         <a id="savetwo" class="btn btn-primary btn-lg">""" + continue_label + """</a>
#         <a id="savetwo" class="btn btn-warning btn-lg">""" + word('Clear') + """</a>
#       </div>
# """
#     output += '    </div>\n    <form action="' + root + '" id="dasigform" method="POST"><input type="hidden" name="_save_as" value="' + escape_id(status.question.fields[0].saveas) + '"/><input type="hidden" id="_the_image" name="_the_image" value=""/><input type="hidden" id="da_success" name="_success" value="0"/>'
#     output += tracker_tag(status)
#     output += '</form>\n'
#     add_validation(status.extra_scripts, validation_rules)
#     return output

def get_choices_with_abb(status, field, the_user_dict, terms=None, links=None):
    if terms is None:
        terms = dict()
    if links is None:
        links = list()
    choice_list = status.get_choices(field, the_user_dict)
    data = dict()
    while True:
        success = True
        data['keys'] = list()
        data['abb'] = dict()
        data['abblower'] = dict()
        data['label'] = list()
        for choice in choice_list:
            flabel = to_text(markdown_to_html(choice[0], trim=False, status=status, strip_newlines=True), terms, links, status).strip()
            success = try_to_abbreviate(choice[0], flabel, data, len(choice_list))
            if not success:
                break
        if success:
            break
    return data, choice_list
    
sms_bad_words = ['cancel', 'end', 'help', 'info', 'quit', 'stop', 'stopall', 'unsubscribe', 'back', 'question', 'exit']

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
            #data['size'] = 1
            endpoint = startpoint + data['size']
            continue
        if method == 'fromstart' and re.search(r'[^A-Za-z0-9]$', prospective_key):
            endpoint += 1
            continue
        if prospective_key.lower() in data['abblower'] or prospective_key.lower() in sms_bad_words:
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

def as_sms(status, the_user_dict, links=None, menu_items=None):
    if links is None:
        links = list()
    if menu_items is None:
        menu_items = list()    
    terms = dict()
    #logmessage("length of links is " + str(len(links)))
    links_len = 0
    menu_items_len = 0
    next_variable = None
    qoutput = text_type()
    if status.question.question_type == 'signature':
        qoutput += word('Sign Your Name') + "\n"
    #logmessage("The question is " + status.questionText)
    qoutput += to_text(markdown_to_html(status.questionText, trim=False, status=status, strip_newlines=True), terms, links, status)
    if status.subquestionText:
        qoutput += "\n" + to_text(markdown_to_html(status.subquestionText, status=status), terms, links, status)
        #logmessage("output is: " + repr(qoutput))
    qoutput += "XXXXMESSAGE_AREAXXXX"
    if len(status.question.fields):
        field = None
        next_field = None
        info_message = None
        field_list = status.get_field_list()
        for the_field in field_list:
            if is_empty_mc(status, the_field):
                logmessage("as_sms: skipping field because choice list is empty.")
                continue
            if hasattr(the_field, 'datatype'):
                if the_field.datatype in ['script', 'css']: # why did I ever comment this out?
                    continue
                if the_field.datatype in ['html', 'note'] and field is not None:
                    continue
                if the_field.datatype == 'note':
                    info_message = to_text(markdown_to_html(status.extras['note'][the_field.number], status=status), terms, links, status)
                    continue
                if the_field.datatype == 'html':
                    info_message = to_text(status.extras['html'][the_field.number].rstrip(), terms, links, status)
                    continue
            #logmessage("field number is " + str(the_field.number))
            if not hasattr(the_field, 'saveas'):
                logmessage("as_sms: field has no saveas")
                continue
            if the_field.number not in status.current_info['skip']:
                #logmessage("as_sms: field is not defined yet")
                if field is None:
                    field = the_field
                elif next_field is None:
                    next_field = the_field
                continue
            else:
                logmessage("as_sms: field " + str(the_field.number) + " skipped")
        if info_message is not None:
            qoutput += "\n" + info_message
        immediate_next_field = None
        if field is None:
            logmessage("as_sms: field seemed to be defined already?")
            field = status.question.fields[0]
            #return dict(question=qoutput, help=None, next=next_variable)
        else:
            reached_field = False
            for the_field in field_list:
                if the_field is field:
                    reached_field = True
                    continue
                if reached_field is False:
                    continue
                if the_field.datatype in ['script', 'css']:
                    continue
                immediate_next_field = the_field
                break
        label = None
        next_label = ''
        if next_field is not None:
            next_variable = myb64unquote(next_field.saveas)
            if immediate_next_field is not None:
                if hasattr(immediate_next_field, 'label') and status.labels[immediate_next_field.number] not in ["no label", ""]:
                    next_label = ' (' + word("Next will be") + ' ' + to_text(markdown_to_html(status.labels[immediate_next_field.number], trim=False, status=status, strip_newlines=True), terms, links, status) + ')'
                elif hasattr(immediate_next_field, 'datatype'):
                    if immediate_next_field.datatype in ['note']:
                        next_label = ' (' + word("Next will be") + ' ' + to_text(markdown_to_html(status.extras['note'][immediate_next_field.number], trim=False, status=status, strip_newlines=True), terms, links, status) + ')'
                    elif immediate_next_field.datatype in ['html']:
                        next_label = ' (' + word("Next will be") + ' ' + to_text(status.extras['html'][immediate_next_field.number].rstrip(), terms, links, status) + ')'
        if hasattr(field, 'label') and status.labels[field.number] != "no label":
            label = to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), terms, links, status)
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
            data, choice_list = get_choices_with_abb(status, field, the_user_dict, terms=terms, links=links)
            qoutput += "\n" + word("Choices:")
            if hasattr(field, 'shuffle') and field.shuffle:
                random.shuffle(data['label'])
            for the_label in data['label']:
                qoutput += "\n" + the_label
            if hasattr(field, 'datatype') and field.datatype in ['checkboxes', 'object_checkboxes']:
                if hasattr(field, 'nota') and status.extras['nota'][field.number] is not False:
                    qoutput += "\n" + word("Type your selection(s), separated by commas.")
                else:
                    qoutput += "\n" + word("Type your selection(s), separated by commas, or type none.")
            else:
                if status.extras['required'][field.number]:
                    if len(choice_list) == 1:
                        qoutput += "\n" + word("Type") + " " + data['keys'][0] + " " + word("to proceed.")
                    else:
                        qoutput += "\n" + word("Type your selection.")
                else:
                    qoutput += "\n" + word("Type your selection, or type skip to move on without selecting.")
        elif question.question_type == 'signature':
            if 'underText' in status.extras:
                qoutput += "\n__________________________\n" + to_text(markdown_to_html(status.extras['underText'], trim=False, status=status, strip_newlines=True), terms, links, status)
            qoutput += "\n" + word('Type x to sign your name electronically')
        elif hasattr(field, 'datatype') and field.datatype == 'range':
            max_string = str(float(status.extras['max'][field.number]))
            min_string = str(float(status.extras['min'][field.number]))
            if label:
                qoutput += "\n" + label + ":" + next_label
            qoutput += "\n" + word('Type a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string
        elif hasattr(field, 'datatype') and field.datatype in ['file', 'camera', 'user', 'environment']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
                if status.extras['required'][field.number]:
                    qoutput += "\n" + word('Please send an image or file.')
                else:
                    qoutput += "\n" + word('Please send an image or file, or type skip.')                    
        elif hasattr(field, 'datatype') and field.datatype in ['files']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Please send one or more images.')
            else:
                qoutput += "\n" + word('Please send one or more images, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['camcorder']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Please send a video.')
            else:
                qoutput += "\n" + word('Please send a video, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['microphone']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Please send an audio clip.')
            else:
                qoutput += "\n" + word('Please send an audio clip, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['number', 'float', 'integer']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Type a number.')
            else:
                qoutput += "\n" + word('Type a number, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['currency']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Type a currency value.')
            else:
                qoutput += "\n" + word('Type a currency value, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['date']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Type a date.')
            else:
                qoutput += "\n" + word('Type a date, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['time']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Type a time.')
            else:
                qoutput += "\n" + word('Type a time, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['datetime']:
            if label:
                qoutput += "\n" + label + ":" + next_label 
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Type a date and time.')
            else:
                qoutput += "\n" + word('Type a date and time, or type skip.')
        elif hasattr(field, 'datatype') and field.datatype in ['email']:
            if label:
                qoutput += "\n" + label + ":" + next_label
            if status.extras['required'][field.number]:
                qoutput += "\n" + word('Type an e-mail address.')
            else:
                qoutput += "\n" + word('Type an e-mail address, or type skip.')
        else:
            if label:
                if status.extras['required'][field.number]:
                    qoutput += "\n" + word("Type the") + " " + label + "." + next_label
                else:
                    qoutput += "\n" + word("Type the") + " " + label + " " + word("or type skip to leave blank.") + next_label
    if 'underText' in status.extras and question.question_type != 'signature':
        qoutput += "\n" + to_text(markdown_to_html(status.extras['underText'], status=status), terms, links, status)
    if 'menu_items' in status.extras and isinstance(status.extras['menu_items'], list):
        for menu_item in status.extras['menu_items']:
            if isinstance(menu_item, dict) and 'url' in menu_item and 'label' in menu_item:
                menu_items.append((menu_item['url'], menu_item['label']))
    if len(links):
        indexno = 1
        qoutput_add = "\n" + "== " + word("Links") + " =="
        seen = dict()
        for (href, label) in links:
            if label in seen and href in seen[label]:
                continue
            if label not in seen:
                seen[label] = set()
            seen[label].add(href)
            if re.search(r'action=', href):
                qoutput_add += "\n* " + label + ": [" + word('link') + str(indexno) + ']'
                indexno += 1
            else:
                qoutput_add += "\n* " + label + ": " + href
        if indexno == 2:
            qoutput_add += "\n" + word("You can type link1 to visit the link")
        else:
            qoutput_add += "\n" + word("You can type link1, etc. to visit a link")
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', qoutput_add + r'XXXXMESSAGE_AREAXXXX', qoutput)
        links_len = len(links)
        links_orig = list(links)
        while len(links):
            links.pop()
        for (href, label) in links_orig:
            if re.search(r'action=', href):
                links.append((href, label))
    if len(status.helpText) or len(terms) or len(menu_items):
        houtput = text_type()
        for help_section in status.helpText:
            if houtput != '':
                houtput += "\n"
            if help_section['heading'] is not None:
                houtput += '== ' + to_text(markdown_to_html(help_section['heading'], trim=False, status=status, strip_newlines=True), terms, links, status) + ' =='
            elif len(status.helpText) > 1:
                houtput += '== ' + word('Help with this question') + ' =='
            houtput += "\n" + to_text(markdown_to_html(help_section['content'], trim=False, status=status, strip_newlines=True), terms, links, status)
        if len(terms):
            if houtput != '':
                houtput += "\n"
            houtput += "== " + word("Terms used:") + " =="
            for term, definition in terms.items():
                houtput += "\n" + term + ': ' + definition
        if len(menu_items):
            indexno = 1
            if houtput != '':
                houtput += "\n"
            houtput += "== " + word("Menu:") + " =="
            for (href, label) in menu_items:
                if re.search(r'action=', href):
                    houtput += "\n* " + label + ": [" + word('menu') + str(indexno) + ']'
                    indexno += 1
                else:
                    houtput += "\n* " + label + ": " + href
            if indexno == 2:
                houtput += "\n" + word("You can type menu1 to select the menu item")
            else:
                houtput += "\n" + word("You can type menu1, etc. to select a menu item")
            menu_items_len = len(menu_items)
            menu_items_orig = list(menu_items)
            while len(menu_items):
                menu_items.pop()
            for (href, label) in menu_items_orig:
                if re.search(r'action=', href):
                    menu_items.append((href, label))
        #houtput += "\n" + word("You can type question to read the question again.")
    else:
        houtput = None
    if status.question.helptext is not None:
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + word("Type ? for additional assistance.") + 'XXXXMESSAGE_AREAXXXX', qoutput)
    elif len(terms) or menu_items_len:
        items = list()
        if len(terms):
            items.append(word("definitions of words"))
        if menu_items_len:
            items.append(word("menu items"))
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + word("Type ? to see") + " " + comma_and_list(items) + "." + 'XXXXMESSAGE_AREAXXXX', qoutput)
    # if status.question.question_type == 'deadend':
    #     return dict(question=qoutput, help=houtput)
    if len(status.attachments) > 0:
        if len(status.attachments) > 1:
            qoutput += "\n" + word("Your documents are attached.")
        else:
            qoutput += "\n" + word("Your document is attached.")
    return dict(question=qoutput, help=houtput, next=next_variable)

def embed_input(status, variable):
    variable = re.sub(r'^\[FIELD +(.*?) *\]$', r'\1', variable)
    for field in status.get_field_list():
        if hasattr(field, 'saveas') and variable == from_safeid(field.saveas):
            status.embedded.add(field.saveas)
            return input_for(status, field, embedded=True)
    return 'ERROR: field not found'

def is_empty_mc(status, field):
    if hasattr(field, 'choicetype'):
        if field.choicetype in ['compute', 'manual']:
            if field.number not in status.selectcompute:
                #logmessage("selectcompute had nothing for field " + str(field.number))
                return False
            #logmessage("Using selectcompute")
            pairlist = list(status.selectcompute[field.number])
        else:
            logmessage("is_empty_mc: unknown choicetype " + str(field.choicetype))
            return False
        #logmessage("Pairlist was " + str(pairlist))
        if len(pairlist) == 0:
            return True
    return False

def help_wrap(content, helptext, status):
    if helptext is None:
        return content
    else:
        return '<div class="dachoicewithhelp"><div><div>' + content + '</div><div class="dachoicehelp"><a tabindex="0" data-container="body" data-toggle="popover" data-placement="left" data-content=' + noquote(markdown_to_html(helptext, trim=True, status=status, do_terms=False)) + '><i class="fas fa-question-circle"></i></a></div></div></div>'

def as_html(status, url_for, debug, root, validation_rules, field_error, the_progress_bar, steps):
    decorations = list()
    uses_audio_video = False
    audio_text = ''
    video_text = ''
    datatypes = dict()
    varnames = dict()
    onchange = list()
    autocomplete_id = False
    if status.using_navigation == 'vertical':
        grid_class = "col-xl-6 col-lg-6 col-md-9"
    else:
        if status.question.interview.flush_left:
            grid_class = "offset-xl-1 col-xl-5 col-lg-6 col-md-8"
        else:
            grid_class = "offset-xl-3 offset-lg-3 col-xl-6 col-lg-6 offset-md-2 col-md-8"
    if 'script' in status.extras and status.extras['script'] is not None:
        status.extra_scripts.append(status.extras['script'])
    if 'css' in status.extras and status.extras['css'] is not None:
        status.extra_css.append(status.extras['css'])
    if status.continueLabel:
        continue_label = markdown_to_html(status.continueLabel, trim=True, do_terms=False, status=status)
    else:
        continue_label = word('Continue')        
    # if status.question.script is not None:
    #     status.extra_scripts.append(status.question.script)
    back_button_val = status.extras.get('back_button', None)
    if (back_button_val or (back_button_val is None and status.question.interview.question_back_button)) and status.question.can_go_back and steps > 1:
        back_button = '\n                  <button type="button" class="btn btn-link ' + BUTTON_CLASS + ' daquestionbackbutton" title=' + json.dumps(word("Go back to the previous question")) + '><span><i class="fas fa-chevron-left"></i> '
        if status.extras['back button label text'] is not None:
            back_button += status.extras['back button label text']
        else:
            back_button += status.question.back()
        back_button += '</span></button>'
    else:
        back_button = ''
    if status.question.interview.question_help_button and len(status.helpText) and status.question.helptext is not None:
        if status.helpText[0]['label']:
            help_label = markdown_to_html(status.helpText[0]['label'], trim=True, do_terms=False, status=status)
        else:
            help_label = status.question.help()
        help_button = '\n                  <button type="button" class="btn btn-info ' + BUTTON_CLASS + ' " id="daquestionhelpbutton"><span>' + help_label + '</span></button>'
    else:
        help_button = ''
    if status.audiovideo is not None:
        uses_audio_video = True
        audio_urls = get_audio_urls(status.audiovideo)
        if len(audio_urls):
            audio_text += '<div class="daaudiovideo-control">\n' + audio_control(audio_urls) + '</div>\n'
        video_urls = get_video_urls(status.audiovideo)
        if len(video_urls):
            video_text += '<div class="daaudiovideo-control">\n' + video_control(video_urls) + '</div>\n'
    if status.using_screen_reader and 'question' in status.screen_reader_links:
        audio_text += '<div class="daaudiovideo-control">\n' + audio_control(status.screen_reader_links['question'], preload="none", title_text=word('Read this screen out loud')) + '</div>\n'
    if status.decorations is not None:
        #sys.stderr.write("yoo1\n")
        for decoration in status.decorations:
            #sys.stderr.write("yoo2\n")
            if 'image' in decoration:
                #sys.stderr.write("yoo3\n")
                the_image = status.question.interview.images.get(decoration['image'], None)
                if the_image is not None:
                    #sys.stderr.write("yoo4\n")
                    url = server.url_finder(str(the_image.package) + ':' + str(the_image.filename))
                    width_value = DECORATION_SIZE
                    width_units = DECORATION_UNITS
                    sizing = 'width:' + str(width_value) + str(width_units) + ';'
                    filename = server.file_finder(str(the_image.package) + ':' + str(the_image.filename))
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
                        decorations.append('<img alt="" class="daiconfloat" style="' + sizing + '" src="' + url + '"/>')
                elif daconfig.get('default icons', None) == 'font awesome':
                    decorations.append('<span style="font-size: ' + str(DECORATION_SIZE) + str(DECORATION_UNITS) + '" class="dadecoration"><i class="' + daconfig.get('font awesome prefix', 'fas') + ' fa-' + str(decoration['image']) + '"></i></span>')
                elif daconfig.get('default icons', None) == 'material icons':
                    decorations.append('<span style="font-size: ' + str(DECORATION_SIZE) + str(DECORATION_UNITS) + '" class="dadecoration"><i class="da-material-icons">' + str(decoration['image']) + '</i></span>')
    if len(decorations):
        decoration_text = decorations[0];
    else:
        decoration_text = ''
    master_output = text_type()
    master_output += '          <section id="daquestion" class="tab-pane active ' + grid_class + '">\n'
    output = text_type()
    if the_progress_bar:
        if status.question.question_type == "signature":
            the_progress_bar = re.sub(r'class="row"', 'class="d-none d-md-block"', the_progress_bar)
        output += the_progress_bar
    if status.question.question_type == "signature":
        if status.question.interview.question_back_button and status.question.can_go_back and steps > 1:
            back_clear_button = '<button type="button" class="btn btn-sm btn-link dasignav-left dasignavbutton daquestionbackbutton"><span>' + status.question.back() + '</span></button>'
        else:
            back_clear_button = '<a href="#" role="button" class="btn btn-sm btn-warning dasignav-left dasignavbutton dasigclear">' + word('Clear') + '</a>'
        output += '            <div class="dasigpage" id="dasigpage">\n              <div class="dasigshowsmallblock dasigheader d-block d-md-none" id="dasigheader">\n                <div class="dasiginnerheader">\n                  ' + back_clear_button + '\n                  <a href="#" role="button" class="btn btn-sm btn-primary dasignav-right dasignavbutton dasigsave">' + continue_label + '</a>\n                  <div id="dasigtitle" class="dasigtitle">'
        if status.questionText:
            output += markdown_to_html(status.questionText, trim=True, status=status)
        else:
            output += word('Sign Your Name')
        output += '</div>\n                </div>\n              </div>\n              <div class="dasigtoppart" id="dasigtoppart">\n                <div id="daerrormess" class="dasigerrormessage dasignotshowing">' + word("You must sign your name to continue.") + '</div>\n'
        if status.questionText:
            output += '                <div class="da-page-header d-none d-md-block"><h1 class="h3">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        output += '              </div>'
        if status.subquestionText:
            output += '                <div id="dasigmidpart" class="dasigmidpart">\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        else:
            output += '\n              <div id="dasigmidpart" class="dasigmidpart"></div>'
        output += '\n              <div id="dasigcontent"><p style="text-align:center;border-style:solid;border-width:1px">' + word('Loading.  Please wait . . . ') + '</p></div>\n              <div class="dasigbottompart" id="dasigbottompart">\n                '
        if 'underText' in status.extras:
            output += '                <div class="d-none d-md-block">' + markdown_to_html(status.extras['underText'], trim=False, status=status) + '</div>\n                <div class="d-block d-md-none">' + markdown_to_html(status.extras['underText'], trim=True, status=status) + '</div>'
        output += "\n              </div>"
        output += """
              <div class="form-actions d-none d-md-block dasigbuttons">""" + back_button + """
                <a href="#" role="button" class="btn btn-primary """ + BUTTON_CLASS + """ dasigsave">""" + continue_label + """</a>
                <a href="#" role="button" class="btn btn-warning """ + BUTTON_CLASS + """ dasigclear">""" + word('Clear') + """</a>
              </div>
"""
        output += '            </div>\n            <form aria-labelledBy="dasigtitle" action="' + root + '" id="dasigform" method="POST"><input type="hidden" name="_save_as" value="' + escape_id(status.question.fields[0].saveas) + '"/><input type="hidden" id="da_ajax" name="ajax" value="0"/><input type="hidden" id="da_the_image" name="_the_image" value=""/><input type="hidden" id="da_success" name="_success" value="0"/>'
        output += tracker_tag(status)
        output += '            </form>\n'
        output += '            <div class="d-block d-md-none"><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br></div>'
    elif status.question.question_type in ["yesno", "yesnomaybe"]:
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-field- ' + status.question.question_type + '"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
        output += '                <div>' + back_button + '\n                  <button class="btn btn-primary ' + BUTTON_CLASS + ' " name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True"><span>' + status.question.yes() + '</span></button>\n                  <button class="btn ' + BUTTON_CLASS + ' btn-secondary" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False"><span>' + status.question.no() + '</span></button>'
        if status.question.question_type == 'yesnomaybe':
            output += '\n                  <button class="btn ' + BUTTON_CLASS + ' btn-warning" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None"><span>' + markdown_to_html(status.question.maybe(), trim=True, do_terms=False, status=status) + '</span></button>'
        output += help_button
        output += '\n                </div></fieldset>\n'
        #output += question_name_tag(status.question)
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type in ["noyes", "noyesmaybe"]:
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-field- ' + status.question.question_type + '"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
        output += '                <div>' + back_button + '\n                  <button class="btn btn-primary ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False"><span>' + status.question.yes() + '</span></button>\n                  <button class="btn ' + BUTTON_CLASS + ' btn-secondary" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True"><span>' + status.question.no() + '</span></button>'
        if status.question.question_type == 'noyesmaybe':
            output += '\n                  <button class="btn ' + BUTTON_CLASS + ' btn-warning" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None"><span>' + status.question.maybe() + '</span></button>'
        output += help_button
        output += '\n                </div></fieldset>\n'
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type == "review":
        fieldlist = list()
        if hasattr(status.question, 'review_saveas'):
            datatypes[safeid(status.question.review_saveas)] = "boolean"
        for field in status.get_field_list():
            if 'html' in status.extras and field.number in status.extras['html']:
                side_note_content = status.extras['html'][field.number].rstrip()
            elif 'note' in status.extras and field.number in status.extras['note']:
                side_note_content = markdown_to_html(status.extras['note'][field.number], status=status, strip_newlines=True)
            else:
                side_note_content = None
            if side_note_content is not None:
                side_note = '<div class="col darlap">' + side_note_content + '</div>'
                side_note_parent = ' darlap-parent'
            else:
                side_note = ''
                side_note_parent = ''
            if not status.extras['ok'][field.number]:
                continue
            #if hasattr(field, 'extras'):
            #    if 'script' in field.extras and 'script' in status.extras and field.number in status.extras['script']:
            #        status.extra_scripts.append(status.extras['script'][field.number])
                # if 'css' in field.extras and 'css' in status.extras and field.number in status.extras['css']:
                #     status.extra_css.append(status.extras['css'][field.number])
            if hasattr(field, 'datatype'):
                if field.datatype == 'html' and 'html' in status.extras and field.number in status.extras['html']:
                    fieldlist.append('                <div class="form-group row da-field-container da-field-container-note"><div class="col-md-12"><div>' + side_note_content + '</div></div></div>\n')
                    continue
                elif field.datatype == 'note' and 'note' in status.extras and field.number in status.extras['note']:
                    fieldlist.append('                <div class="form-group row da-field-container da-field-container-note"><div class="col-md-12">' + side_note_content + '</div></div>\n')
                    continue
                # elif field.datatype in ['script', 'css']:
                #     continue
                elif field.datatype == 'button' and hasattr(field, 'label') and field.number in status.helptexts:
                    fieldlist.append('                <div class="row' + side_note_parent + '"><div class="col-md-12"><a href="#" role="button" class="btn btn-sm btn-success da-review-action da-review-action-button" data-action=' + myb64doublequote(json.dumps(field.action)) + '>' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a>' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div>' + side_note + '</div>\n')
                    continue
            if hasattr(field, 'label'):
                fieldlist.append('                <div class="form-group row' + side_note_parent + '"><div class="col-md-12"><a href="#" class="da-review-action" data-action=' + myb64doublequote(json.dumps(field.action)) + '>' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a></div>' + side_note + '</div>\n')
                if field.number in status.helptexts:
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div></div>\n')
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" class="form-horizontal" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        #fieldlist.append('                <input type="hidden" name="_event" value=' + myb64doublequote(json.dumps(list(status.question.fields_used))) + ' />\n')
        if (len(fieldlist)):
            output += "".join(fieldlist)
        if status.continueLabel:
            resume_button_label = markdown_to_html(status.continueLabel, trim=True, do_terms=False, status=status)
        else:
            resume_button_label = word('Resume')
        output += status.submit
        output += '                <fieldset class="da-field-buttons"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
        if hasattr(status.question, 'review_saveas'):
            output += '                <div class="form-actions">' + back_button + '\n                <button type="submit" class="btn ' + BUTTON_CLASS + ' btn-primary" name="' + escape_id(safeid(status.question.review_saveas)) + '" value="True"><span>' + continue_label + '</span></button>' + help_button + '</div></fieldset>\n'
        else:
            output += '                <div class="form-actions">' + back_button + '\n                <button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit"><span>' + resume_button_label + '</span></button>' + help_button + '</div></fieldset>\n'
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '            </form>\n'
    elif status.question.question_type == "fields":
        enctype_string = ""
        fieldlist = list()
        checkboxes = dict()
        files = list()
        hiddens = dict()
        ml_info = dict()
        note_fields = dict()
        checkbox_validation = False
        if status.subquestionText:
            sub_question_text = markdown_to_html(status.subquestionText, status=status, indent=18, embedder=embed_input)
        if hasattr(status.question, 'fields_saveas'):
            datatypes[safeid(status.question.fields_saveas)] = "boolean"
        field_list = status.get_field_list()
        status.saveas_to_use = dict()
        status.saveas_by_number = dict()
        for field in field_list:
            if 'html' in status.extras and field.number in status.extras['html']:
                note_fields[field.number] = status.extras['html'][field.number].rstrip()
            elif 'note' in status.extras and field.number in status.extras['note']:
                note_fields[field.number] = markdown_to_html(status.extras['note'][field.number], status=status, embedder=embed_input)
            if hasattr(field, 'address_autocomplete') and field.address_autocomplete and hasattr(field, 'saveas'):
                autocomplete_id = field.saveas
            if hasattr(field, 'saveas'):
                varnames[safeid('_field_' + str(field.number))] = field.saveas
                if (hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in status.extras) or 'show_if_js' in field.extras)) or (hasattr(field, 'disableothers') and field.disableothers):
                    the_saveas = safeid('_field_' + str(field.number))
                else:
                    the_saveas = field.saveas
                status.saveas_to_use[field.saveas] = the_saveas
                status.saveas_by_number[field.number] = the_saveas
                if the_saveas not in validation_rules['rules']:
                    validation_rules['rules'][the_saveas] = dict()
                if the_saveas not in validation_rules['messages']:
                    validation_rules['messages'][the_saveas] = dict()
        seen_extra_header = False
        for field in field_list:
            field_number = int(re.sub(r'.*_', '', text_type(field.number)))
            if hasattr(field, 'collect_type'):
                data_def = 'data-collectnum="' + str(field.collect_number) + '" data-collecttype="' + field.collect_type + '" '
                class_def = ' dacollect' + field.collect_type
                if field.collect_type in ('extra', 'extraheader', 'extrapostheader', 'extrafinalpostheader'):
                    if field.collect_type == 'extraheader' and not seen_extra_header:
                        seen_extra_header = True
                        style_def = ''
                    else:
                        style_def = 'style="display: none;" '
                else:
                    style_def = ''
            else:
                data_def = ''
                class_def = ''
                style_def = ''
            if field.number in note_fields:
                side_note = '<div class="col darlap">' + note_fields[field.number] + '</div>'
                side_note_parent = ' darlap-parent'
            else:
                side_note = ''
                side_note_parent = ''
            if hasattr(field, 'disableothers') and field.disableothers and isinstance(field.disableothers, list):
                if 'disableothers' not in status.extras:
                    status.extras['disableothers'] = dict()
                status.extras['disableothers'][field.number] = list()
                for orig_var in field.disableothers:
                    for the_field in field_list:
                        the_field_number = int(re.sub(r'.*_', '', text_type(the_field.number)))
                        if the_field is not field and hasattr(the_field, 'saveas') and from_safeid(the_field.saveas) == orig_var:
                            status.extras['disableothers'][field.number].append(status.saveas_by_number[the_field.number])
                            break
            if is_empty_mc(status, field):
                if hasattr(field, 'datatype'):
                    hiddens[field.saveas] = field.datatype
                else:
                    hiddens[field.saveas] = True
                if hasattr(field, 'datatype'):
                    datatypes[field.saveas] = field.datatype
                    if field.datatype == 'object_checkboxes':
                        datatypes[safeid(from_safeid(field.saveas) + ".gathered")] = 'boolean'
                continue
            if not status.extras['ok'][field.number]:
                continue
            if status.extras['required'][field.number]:
                req_tag = ' darequired'
            else:
                req_tag = ''
            if hasattr(field, 'extras'):
                # if 'script' in field.extras and 'script' in status.extras:
                #     status.extra_scripts.append(status.extras['script'][field.number])
                # if 'css' in field.extras and 'css' in status.extras:
                #     status.extra_css.append(status.extras['css'][field.number])
                #fieldlist.append("<div>datatype is " + str(field.datatype) + "</div>")
                if 'ml_group' in field.extras or 'ml_train' in field.extras:
                    ml_info[field.saveas] = dict()
                    if 'ml_group' in field.extras:
                        ml_info[field.saveas]['group_id'] = status.extras['ml_group'][field.number]
                    if 'ml_train' in field.extras:
                        ml_info[field.saveas]['train'] = status.extras['ml_train'][field.number]
                if 'show_if_var' in field.extras and 'show_if_val' in status.extras:
                    if hasattr(field, 'saveas'):
                        fieldlist.append('                <div class="dashowif" data-saveas="' + escape_id(field.saveas) + '" data-showif-sign="' + escape_id(field.extras['show_if_sign']) + '" data-showif-var="' + escape_id(field.extras['show_if_var']) + '" data-showif-val=' + noquote(text_type(status.extras['show_if_val'][field.number])) + '>\n')
                    else:
                        fieldlist.append('                <div class="dashowif" data-showif-sign="' + escape_id(field.extras['show_if_sign']) + '" data-showif-var="' + escape_id(field.extras['show_if_var']) + '" data-showif-val=' + noquote(text_type(status.extras['show_if_val'][field.number])) + '>\n')
                if 'show_if_js' in field.extras:
                    if hasattr(field, 'saveas'):
                        fieldlist.append('                <div class="dajsshowif" data-saveas="' + escape_id(field.saveas) + '" data-jsshowif=' + myb64doublequote(json.dumps(field.extras['show_if_js'])) + '>\n')
                    else:
                        fieldlist.append('                <div class="dajsshowif" data-jsshowif=' + myb64doublequote(json.dumps(field.extras['show_if_js'])) + '>\n')
            if hasattr(field, 'datatype'):
                field_class = ' da-field-container da-field-container-datatype-' + field.datatype
                if field.datatype == 'html':
                    if hasattr(field, 'collect_type'):
                        if 'list_minimum' in status.extras and field.collect_number < status.extras['list_minimum']:
                            hide_delete = True
                        else:
                            hide_delete = False
                        if status.extras['list_collect_allow_delete'] and not hide_delete:
                            da_remove_existing = '<button type="button" class="btn btn-sm btn-danger float-right dacollectremoveexisting"><i class="fas fa-trash"></i> ' + word("Delete") + '</button>'
                        else:
                            da_remove_existing = ''
                        if field.collect_type == 'extraheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + class_def + '"><div class="col-md-12"><hr><span class="dacollectnum dainvisible">' + status.extras['list_message'] + ' ' + str(field.collect_number + 1) + '.</span><span class="dacollectremoved text-danger dainvisible"> ' + word("(Deleted)") + '</span><button type="button" class="btn btn-sm btn-danger float-right dainvisible dacollectremove"><i class="fas fa-trash"></i> ' + word("Delete") + '</button><button type="button" class="btn btn-sm btn-info float-right dainvisible dacollectunremove"><i class="fas fa-trash-restore"></i> ' + word("Undelete") + '</button><button type="button" class="btn btn-sm btn-success dacollectadd"><i class="fas fa-plus-circle"></i> ' + word("Add another") + '</button></div></div>\n')
                        elif field.collect_type == 'postheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + class_def + '"><div class="col-md-12"></div></div>\n')
                        elif field.collect_type == 'extrapostheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + class_def + '"><div class="col-md-12"></div></div>\n')
                        elif field.collect_type == 'extrafinalpostheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + class_def + '"><div class="col-md-12"><button type="submit" name="_collect" value=' + myb64doublequote(json.dumps({'function': 'add', 'list': status.extras['list_collect'].instanceName})) + ' class="btn btn-sm btn-success"><i class="fas fa-plus-circle"></i> ' + word("Add another") + '</button></div></div>\n')
                        elif field.collect_type == 'firstheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + class_def + '"><div class="col-md-12"><span class="dacollectnum">' + status.extras['list_message'] + ' ' + str(field.collect_number + 1) + '.</span><span class="dacollectremoved text-danger dainvisible"> ' + word("(Deleted)") + '</span><button type="button" class="btn btn-sm btn-info float-right dainvisible dacollectunremove"><i class="fas fa-trash-restore"></i> ' + word("Undelete") + '</button>' + da_remove_existing + '</div></div>\n')
                        else:
                            fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + class_def + '"><div class="col-md-12"><hr><span class="dacollectnum">' + status.extras['list_message'] + ' ' + str(field.collect_number + 1) + '.</span><span class="dacollectremoved text-danger dainvisible"> ' + word("(Deleted)") + '</span><button type="button" class="btn btn-sm btn-info float-right dainvisible dacollectunremove"><i class="fas fa-trash-restore"></i> ' + word("Undelete") + '</button>' + da_remove_existing + '</div></div>\n')
                    else:
                        fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row da-field-container da-field-container-note' + class_def + '"><div class="col-md-12"><div>' + note_fields[field.number] + '</div></div></div>\n')
                    #continue
                elif field.datatype == 'note':
                    fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row da-field-container da-field-container-note' + class_def + '"><div class="col-md-12">' + note_fields[field.number] + '</div></div>\n')
                    #fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status, strip_newlines=True) + '</div></div>\n')
                    #continue
                # elif field.datatype in ['script', 'css']:
                #     continue
                else:
                    if hasattr(field, 'choicetype'):
                        vals = set([text_type(x['key']) for x in status.selectcompute[field.number]])
                        if len(vals) == 1 and ('True' in vals or 'False' in vals):
                            datatypes[field.saveas] = 'boolean'
                        elif len(vals) == 1 and 'None' in vals:
                            datatypes[field.saveas] = 'threestate'
                        elif len(vals) == 2 and ('True' in vals and 'False' in vals):
                            datatypes[field.saveas] = 'boolean'
                        elif len(vals) == 2 and (('True' in vals and 'None' in vals) or ('False' in vals and 'None' in vals)):
                            datatypes[field.saveas] = 'threestate'
                        elif len(vals) == 3 and ('True' in vals and 'False' in vals and 'None' in vals):
                            datatypes[field.saveas] = 'threestate'
                        else:
                            datatypes[field.saveas] = field.datatype
                    else:
                        datatypes[field.saveas] = field.datatype
                    if field.datatype == 'object_checkboxes':
                        datatypes[safeid(from_safeid(field.saveas) + ".gathered")] = 'boolean'
            else:
                field_class = ' da-field-container'
            if hasattr(field, 'inputtype'):
                field_class += ' da-field-container-inputtype-' + field.inputtype
            elif hasattr(field, 'choicetype'):
                if field.datatype in ['checkboxes', 'object_checkboxes']:
                    field_class += ' da-field-container-inputtype-checkboxes'
                elif field.datatype == 'object_radio':
                    field_class += ' da-field-container-inputtype-radio'
                else:
                    field_class += ' da-field-container-inputtype-dropdown'
            if field.number in status.helptexts:
                helptext_start = '<a tabindex="0" class="daterm" data-container="body" data-toggle="popover" data-placement="bottom" data-content=' + noquote(status.helptexts[field.number]) + '>' 
                helptext_end = '</a>'
            else:
                helptext_start = ''
                helptext_end = ''
            if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                onchange.append(safeid('_field_' + str(field.number)))
            if hasattr(field, 'saveas'):
                varnames[safeid('_field_' + str(field.number))] = field.saveas
                #the_saveas = status.saveas_to_use[field.saveas]
                the_saveas = status.saveas_by_number[field.number]
                if (hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in status.extras) or 'show_if_js' in field.extras)) or (hasattr(field, 'disableothers') and field.disableothers):
                    label_saveas = the_saveas
                else:
                    label_saveas = field.saveas                        
                if not (hasattr(field, 'datatype') and field.datatype in ['checkboxes', 'object_checkboxes']):
                    if hasattr(field, 'inputtype') and field.inputtype == 'combobox':
                        validation_rules['messages'][the_saveas]['required'] = field.validation_message('combobox required', status, word("You need to select one or type in a new value."))
                    elif hasattr(field, 'datatype') and (field.datatype == 'object_radio' or (hasattr(field, 'inputtype') and field.inputtype in ('yesnoradio', 'noyesradio', 'radio', 'dropdown'))):
                        validation_rules['messages'][the_saveas]['required'] = field.validation_message('multiple choice required', status, word("You need to select one."))
                    else:
                        validation_rules['messages'][the_saveas]['required'] = field.validation_message('required', status, word("This field is required."))
                    if status.extras['required'][field.number]:
                        #sys.stderr.write(field.datatype + "\n")
                        validation_rules['rules'][the_saveas]['required'] = True
                    else:
                        validation_rules['rules'][the_saveas]['required'] = False
                if hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes', 'yesnowide', 'noyeswide'] and hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                    if field.uncheckothers is True:
                        the_query = '.dauncheckable:checked, .dauncheckothers:checked'
                        uncheck_list = [status.saveas_to_use[y.saveas] for y in field_list if y is not field and hasattr(y, 'saveas') and hasattr(y, 'inputtype') and y.inputtype in ['yesno', 'noyes', 'yesnowide', 'noyeswide']]
                    else:
                        uncheck_list = [status.saveas_to_use[safeid(y)] for y in field.uncheckothers if safeid(y) in status.saveas_to_use]
                        the_query = ', '.join(['#' + do_escape_id(x) + ':checked' for x in uncheck_list + [the_saveas]])
                    for y in uncheck_list + [the_saveas]:
                        validation_rules['rules'][y]['checkone'] = [1, the_query]
                        validation_rules['messages'][y]['checkone'] = field.validation_message('checkboxes required', status, word(u"Check at least one option, or check “%s”"), parameters=tuple([status.labels[field.number]]))
                    if 'groups' not in validation_rules:
                        validation_rules['groups'] = dict()
                    validation_rules['groups'][the_saveas + '_group'] = ' '.join(uncheck_list + [the_saveas])
                    validation_rules['ignore'] = None
                if field.datatype not in ('checkboxes', 'object_checkboxes'):
                    for key in ('minlength', 'maxlength'):
                        if hasattr(field, 'extras') and key in field.extras and key in status.extras:
                            #sys.stderr.write("Adding validation rule for " + str(key) + "\n")
                            validation_rules['rules'][the_saveas][key] = int(status.extras[key][field.number])
                            if key == 'minlength':
                                validation_rules['messages'][the_saveas][key] = field.validation_message(key, status, word("You must type at least %s characters."), parameters=tuple([status.extras[key][field.number]]))
                            elif key == 'maxlength':
                                validation_rules['messages'][the_saveas][key] = field.validation_message(key, status, word("You cannot type more than %s characters."), parameters=tuple([status.extras[key][field.number]]))
            if hasattr(field, 'inputtype'):
                if field.inputtype in ['yesnoradio', 'noyesradio', 'radio']:
                    validation_rules['ignore'] = None
                elif field.inputtype == 'combobox':
                    validation_rules['ignore'] = list()
            if hasattr(field, 'datatype'):
                if field.datatype in ('checkboxes', 'object_checkboxes') and ((hasattr(field, 'nota') and status.extras['nota'][field.number] is not False) or (hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in status.extras) or ('maxlength' in field.extras and 'maxlength' in status.extras)))):
                    if hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in status.extras) or ('maxlength' in field.extras and 'maxlength' in status.extras)):
                        checkbox_rules = dict()
                        checkbox_messages = dict()
                        if 'minlength' in field.extras and 'minlength' in status.extras and 'maxlength' in field.extras and 'maxlength' in status.extras and status.extras['minlength'][field.number] == status.extras['maxlength'][field.number] and status.extras['minlength'][field.number] > 0:
                            if 'nota' not in status.extras:
                                status.extras['nota'] = dict()
                            status.extras['nota'][field.number] = False
                            checkbox_rules['checkexactly'] = [str(field.number), status.extras['maxlength'][field.number]]
                            checkbox_messages['checkexactly'] = field.validation_message('checkbox minmaxlength', status, word("Please select exactly %s."), parameters=tuple([status.extras['maxlength'][field.number]]))
                        else:
                            if 'minlength' in field.extras and 'minlength' in status.extras:
                                checkbox_rules['checkatleast'] = [str(field.number), status.extras['minlength'][field.number]]
                                if status.extras['minlength'][field.number] == 1:
                                    checkbox_messages['checkatleast'] = field.validation_message('checkbox minlength', status, word("Please select one."))
                                else:
                                    checkbox_messages['checkatleast'] = field.validation_message('checkbox minlength', status, word("Please select at least %s."), parameters=tuple([status.extras['minlength'][field.number]]))
                                if int(status.extras['minlength'][field.number]) > 0:
                                    if 'nota' not in status.extras:
                                        status.extras['nota'] = dict()
                                    status.extras['nota'][field.number] = False
                            if 'maxlength' in field.extras and 'maxlength' in status.extras:
                                checkbox_rules['checkatmost'] = [str(field.number), status.extras['maxlength'][field.number]]
                                checkbox_messages['checkatmost'] = field.validation_message('checkbox maxlength', status, word("Please select no more than %s."), parameters=tuple([status.extras['maxlength'][field.number]]))
                        validation_rules['rules']['_ignore' + str(field.number)] = checkbox_rules
                        validation_rules['messages']['_ignore' + str(field.number)] = checkbox_messages
                    if hasattr(field, 'nota') and status.extras['nota'][field.number] is not False:
                        if '_ignore' + str(field.number) not in validation_rules['rules']:
                            validation_rules['rules']['_ignore' + str(field.number)] = dict()
                        if 'checkatleast' not in validation_rules['rules']['_ignore' + str(field.number)]:
                            validation_rules['rules']['_ignore' + str(field.number)]['checkatleast'] = [str(field.number), 1]
                        if status.extras['nota'][field.number] is True:
                            formatted_item = word("None of the above")
                        else:
                            if hasattr(field, 'saveas') and field.saveas in status.embedded:
                                formatted_item = markdown_to_html(text_type(status.extras['nota'][field.number]), status=status, trim=True, escape=False, do_terms=False)
                            else:
                                formatted_item = markdown_to_html(text_type(status.extras['nota'][field.number]), status=status, trim=True, escape=True, do_terms=False)
                        validation_rules['messages']['_ignore' + str(field.number)] = dict(checkatleast=field.validation_message('checkboxes required', status, word(u"Check at least one option, or check “%s”"), parameters=tuple([formatted_item])))
                    validation_rules['ignore'] = None
                if field.datatype == 'object_radio':
                    validation_rules['ignore'] = None
                if field.datatype == 'date':
                    validation_rules['rules'][the_saveas]['date'] = True
                    validation_rules['messages'][the_saveas]['date'] = field.validation_message('date', status, word("You need to enter a valid date."))
                    if hasattr(field, 'extras') and 'min' in field.extras and 'min' in status.extras and 'max' in field.extras and 'max' in status.extras:
                        validation_rules['rules'][the_saveas]['minmaxdate'] = [format_date(status.extras['min'][field.number], format='yyyy-MM-dd'), format_date(status.extras['max'][field.number], format='yyyy-MM-dd')]
                        validation_rules['messages'][the_saveas]['minmaxdate'] = field.validation_message('date minmax', status, word("You need to enter a date between %s and %s."), parameters=(format_date(status.extras['min'][field.number], format='short'), format_date(status.extras['max'][field.number], format='short')))
                    else:
                        for key in ['min', 'max']:
                            if hasattr(field, 'extras') and key in field.extras and key in status.extras:
                                #sys.stderr.write("Adding validation rule for " + str(key) + "\n")
                                validation_rules['rules'][the_saveas][key + 'date'] = format_date(status.extras[key][field.number], format='yyyy-MM-dd')
                                if key == 'min':
                                    validation_rules['messages'][the_saveas]['mindate'] = field.validation_message('date min', status, word("You need to enter a date on or after %s."), parameters=tuple([format_date(status.extras[key][field.number], format='short')]))
                                elif key == 'max':
                                    validation_rules['messages'][the_saveas]['maxdate'] = field.validation_message('date max', status, word("You need to enter a date on or before %s."), parameters=tuple([format_date(status.extras[key][field.number], format='short')]))
                if field.datatype == 'time':
                    validation_rules['rules'][the_saveas]['time'] = True
                    validation_rules['messages'][the_saveas]['time'] = field.validation_message('time', status, word("You need to enter a valid time."))
                if field.datatype == 'datetime':
                    validation_rules['rules'][the_saveas]['datetime'] = True
                    validation_rules['messages'][the_saveas]['datetime'] = field.validation_message('datetime', status, word("You need to enter a valid date and time."))
                if field.datatype == 'email':
                    validation_rules['rules'][the_saveas]['email'] = True
                    if status.extras['required'][field.number]:
                        validation_rules['rules'][the_saveas]['minlength'] = 1
                        validation_rules['messages'][the_saveas]['minlength'] = field.validation_message('required', status, word("This field is required."))
                    validation_rules['messages'][the_saveas]['email'] = field.validation_message('email', status, word("You need to enter a complete e-mail address."))
                if field.datatype in ['number', 'currency', 'float', 'integer']:
                    validation_rules['rules'][the_saveas]['number'] = True
                    validation_rules['messages'][the_saveas]['number'] = field.validation_message('number', status, word("You need to enter a number."))
                    #sys.stderr.write("Considering adding validation rule\n")
                    for key in ['min', 'max']:
                        if hasattr(field, 'extras') and key in field.extras and key in status.extras:
                            #sys.stderr.write("Adding validation rule for " + str(key) + "\n")
                            validation_rules['rules'][the_saveas][key] = float(status.extras[key][field.number])
                            if key == 'min':
                                validation_rules['messages'][the_saveas][key] = field.validation_message('min', status, word("You need to enter a number that is at least %s."), parameters=tuple([status.extras[key][field.number]]))
                            elif key == 'max':
                                validation_rules['messages'][the_saveas][key] = field.validation_message('max', status, word("You need to enter a number that is at most %s."), parameters=tuple([status.extras[key][field.number]]))
                if (field.datatype in ['files', 'file', 'camera', 'user', 'environment', 'camcorder', 'microphone']):
                    enctype_string = ' enctype="multipart/form-data"'
                    files.append(the_saveas)
                    validation_rules['messages'][the_saveas]['required'] = field.validation_message('file required', status, word("You must provide a file."))
                    if 'accept' in status.extras and field.number in status.extras['accept']:
                        validation_rules['messages'][the_saveas]['accept'] = field.validation_message('accept', status, word("Please upload a file with a valid file format."))
                if field.datatype == 'boolean':
                    if field.sign > 0:
                        checkboxes[field.saveas] = 'False'
                    else:
                        checkboxes[field.saveas] = 'True'
                elif field.datatype == 'threestate':
                    checkboxes[field.saveas] = 'None'
                elif field.datatype in ['checkboxes', 'object_checkboxes']:
                    if field.choicetype in ['compute', 'manual']:
                        pairlist = list(status.selectcompute[field.number])
                    else:
                        pairlist = list()
                    if hasattr(field, 'shuffle') and field.shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if pair['key'] is not None:
                            checkboxes[safeid(from_safeid(field.saveas) + "[" + myb64quote(pair['key']) + "]")] = 'False'
                elif not status.extras['required'][field.number]:
                    if hasattr(field, 'saveas'):
                        checkboxes[field.saveas] = 'None'
            if hasattr(field, 'saveas') and field.saveas in status.embedded:
                continue
            if hasattr(field, 'label'):
                if status.labels[field.number] == 'no label':
                    fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + class_def + '' + side_note_parent + req_tag + field_class + ' da-field-container-nolabel"><label for="' + escape_id(label_saveas) + '" class="sr-only">' + word("Answer here") + '</label><div class="col dawidecol">' + input_for(status, field, wide=True) + '</div>' + side_note + '</div>\n')
                elif hasattr(field, 'inputtype') and field.inputtype in ['yesnowide', 'noyeswide']:
                    fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row dayesnospacing ' + side_note_parent + field_class + ' da-field-container-nolabel' + class_def + '"><label for="' + escape_id(label_saveas) + '" class="sr-only">' + word("Check if applicable") + '</label><div class="col dawidecol">' + input_for(status, field) + '</div>' + side_note + '</div>\n')
                elif hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes']:
                    fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row dayesnospacing' + side_note_parent + req_tag + field_class + ' da-field-container-emptylabel' + class_def + '"><label for="' + escape_id(label_saveas) + '" class="sr-only">' + word("Check if applicable") + '</label><div class="offset-md-4 col-md-8">' + input_for(status, field) + '</div>' + side_note + '</div>\n')
                elif status.labels[field.number] == '':
                    fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + side_note_parent + req_tag + field_class + ' da-field-container-emptylabel' + class_def + '"><label for="' + escape_id(label_saveas) + '" class="sr-only">' + word("Answer here") + '</label><div class="offset-md-4 col-md-8 dafieldpart danolabel">' + input_for(status, field) + '</div>' + side_note + '</div>\n')
                else:
                    fieldlist.append('                <div ' + style_def + data_def + 'class="form-group row' + side_note_parent + req_tag + field_class + class_def + '"><label for="' + escape_id(label_saveas) + '" class="col-md-4 col-form-label datext-right">' + helptext_start + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + helptext_end + '</label><div class="col-md-8 dafieldpart">' + input_for(status, field) + '</div>' + side_note + '</div>\n')
            if hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in status.extras) or 'show_if_js' in field.extras):
                fieldlist.append('                </div>\n')
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" class="form-horizontal" method="POST"' + enctype_string + '>\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + sub_question_text 
            output += '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if (len(fieldlist)):
            output += "".join(fieldlist)
        #else:
        #    output += "                <p>Error: no fields</p>\n"
        #output += '</div>\n'
        if status.extras.get('list_collect', False) is not False:
            output += '                <input type="hidden" name="_list_collect_list" value=' + myb64doublequote(json.dumps(status.extras['list_collect'].instanceName)) + '/>\n'
        if status.extras.get('list_collect_is_final', False) and status.extras['list_collect'].auto_gather:
            if status.extras['list_collect'].ask_number:
                output += '                <input type="hidden" name="' + escape_id(safeid(status.extras['list_collect'].instanceName + ".target_number"))  + '" value="0"/>\n'
            else:
                output += '                <input type="hidden" name="' + escape_id(safeid(status.extras['list_collect'].instanceName + ".there_is_another"))  + '" value="False"/>\n'
        if len(checkboxes):
            output += '                <input type="hidden" name="_checkboxes" value=' + myb64doublequote(json.dumps(checkboxes)) + '/>\n'
        if len(hiddens):
            output += '                <input type="hidden" name="_empties" value=' + myb64doublequote(json.dumps(hiddens)) + '/>\n'
        if len(ml_info):
            output += '                <input type="hidden" name="_ml_info" value=' + myb64doublequote(json.dumps(ml_info)) + '/>\n'
        if len(files):
            output += '                <input type="hidden" name="_files" value=' + myb64doublequote(json.dumps(files)) + '/>\n'
        output += status.submit
        output += '                <fieldset class="da-field-buttons"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
        if hasattr(status.question, 'fields_saveas'):
            output += '                <div class="form-actions">' + back_button + '\n                <button type="submit" class="btn ' + BUTTON_CLASS + ' btn-primary" name="' + escape_id(safeid(status.question.fields_saveas)) + '" value="True"><span>' + continue_label + '</span></button>' + help_button + '</div></fieldset>\n'
        else:
            output += '                <div class="form-actions">' + back_button + '\n                  <button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit"><span>' + continue_label + '</span></button>' + help_button + '</div></fieldset>\n'
        #output += question_name_tag(status.question)
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
        output += tracker_tag(status)
        if status.extras.get('list_collect_is_final', False):
            if status.extras['list_collect'].ask_number:
                datatypes[safeid(status.extras['list_collect'].instanceName + ".target_number")] = 'integer'
            else:
                datatypes[safeid(status.extras['list_collect'].instanceName + ".there_is_another")] = 'boolean'
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type == "settrue":
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = "boolean"
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-field-buttons"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
        output += '                <div class="form-actions">' + back_button + '\n                <button type="submit" class="btn ' + BUTTON_CLASS + ' btn-primary" name="' + escape_id(status.question.fields[0].saveas) + '" value="True"><span>' + continue_label + '</span></button>' + help_button + '</div></fieldset>\n'
        #output += question_name_tag(status.question)
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type == "multiple_choice":
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        if status.question.fields[0].number in status.defaults and isinstance(status.defaults[status.question.fields[0].number], (string_types, int, float)):
            defaultvalue = text_type(status.defaults[status.question.fields[0].number])
            #logmessage("Default value is " + str(defaultvalue))
        else:
            defaultvalue = None
        if hasattr(status.question.fields[0], 'datatype'):
            datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        validation_rules['errorElement'] = "span"
        validation_rules['errorLabelContainer'] = "#daerrorcontainer"
        if status.question.question_variety in ["radio", "dropdown", "combobox"]:
            if status.question.question_variety == "radio":
                verb = 'check'
                output += '                <fieldset class="da-field-' + status.question.question_variety +'"><legend class="sr-only">' + word("Choices:") + "</legend>\n"
            else:
                verb = 'select'
                if status.question.question_variety == "dropdown":
                    inner_fieldlist = ['<option value="">' + word('Select...') + '</option>']
                else:
                    inner_fieldlist = ['<option value="">' + word('Select one') + '</option>']
            if hasattr(status.question.fields[0], 'saveas'):
                id_index = 0
                pairlist = list(status.selectcompute[status.question.fields[0].number])
                if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                    random.shuffle(pairlist)
                for pair in pairlist:
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    helptext = pair.get('help', None)
                    ischecked = ''
                    if 'default' in pair and pair['default'] and defaultvalue is None:
                        ischecked = ' ' + verb + 'ed="' + verb + 'ed"'
                    formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=True, do_terms=False)
                    if defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == text_type(defaultvalue):
                        ischecked = ' ' + verb + 'ed="' + verb + 'ed"'
                    if status.question.question_variety == "radio":
                        if True or pair['key'] is not None: #not sure why this was added
                            output += '                <div class="row"><div class="col-md-12">' + help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty" id="' + escape_id(status.question.fields[0].saveas) + '_' + str(id_index) + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + '/>', helptext, status) + '</div></div>\n'
                        else:
                            output += '                <div class="form-group row"><div class="col-md-12">' + help_wrap(markdown_to_html(pair['label'], status=status), helptext, status) + '</div></div>\n'
                    else:
                        if True or pair['key'] is not None:
                            inner_fieldlist.append('<option value="' + text_type(pair['key']) + '"' + ischecked + '>' + formatted_item + '</option>')

                    id_index += 1
                if status.question.question_variety in ["dropdown", "combobox"]:
                    if status.question.question_variety == 'combobox':
                        combobox = ' combobox'
                        daspaceafter = ' daspaceafter'
                        field_container_class = ' da-field-container-combobox'
                    else:
                        combobox = ''
                        daspaceafter = ''
                        field_container_class = ' da-field-container-dropdown'
                    output += '                <div class="row' + field_container_class + '"><div class="col-md-12' + daspaceafter + '"><select class="form-control daspaceafter' + combobox + '" name="' + escape_id(status.question.fields[0].saveas) + '" id="' + escape_id(status.question.fields[0].saveas) + '">' + "".join(inner_fieldlist) + '</select></div></div>\n'
                if status.question.question_variety == 'combobox':
                    validation_rules['ignore'] = list()
                    validation_rules['messages'][status.question.fields[0].saveas] = {'required': status.question.fields[0].validation_message('combobox required', status, word("You need to select one or type in a new value."))}
                else:
                    validation_rules['ignore'] = None
                    validation_rules['messages'][status.question.fields[0].saveas] = {'required': status.question.fields[0].validation_message('multiple choice required', status, word("You need to select one."))}
                validation_rules['rules'][status.question.fields[0].saveas] = {'required': True}
            else:
                indexno = 0
                for choice in status.selectcompute[status.question.fields[0].number]:
                #for choice in status.question.fields[0].choices:
                    if 'image' in choice:
                        the_icon = icon_html(status, choice['image']) + ' '
                    else:
                        the_icon = ''
                    if 'help' in choice:
                        helptext = choice['help']
                    else:
                        helptext = None
                    if 'default' in choice:
                        is_a_default = choice['default']
                        ischecked = ' ' + verb + 'ed="' + verb + 'ed"'
                    else:
                        is_a_default = False
                        ischecked = ''
                    id_index = 0
                    formatted_key = markdown_to_html(choice['label'], status=status, trim=True, escape=True, do_terms=False)
                    if status.question.question_variety == "radio":
                        output += '                <div class="row"><div class="col-md-12">' + help_wrap('<input aria-label="' + formatted_key + '" alt="' + formatted_key + '" data-labelauty="' + my_escape(the_icon) + formatted_key + '|' + my_escape(the_icon) + formatted_key + '" class="da-to-labelauty" id="multiple_choice_' + str(indexno) + '_' + str(id_index) + '" name="X211bHRpcGxlX2Nob2ljZQ==" type="radio" value="' + str(indexno) + '"' + ischecked + '/>', helptext, status) + '</div></div>\n'
                    else:
                        inner_fieldlist.append('<option value="' + str(indexno) + '"' + ischecked + '>' + formatted_key + '</option>')
                    id_index += 1
                    indexno += 1
                if status.question.question_variety in ["dropdown", "combobox"]:
                    if status.question.question_variety == 'combobox':
                        combobox = ' combobox'
                        daspaceafter = ' daspaceafter'
                    else:
                        combobox = ' daspaceafter'
                        daspaceafter = ''
                    output += '                <div class="row"><div class="col-md-12' + daspaceafter + '"><select class="form-control ' + combobox + '" name="X211bHRpcGxlX2Nob2ljZQ==">' + "".join(inner_fieldlist) + '</select></div></div>\n'
                if status.question.question_variety == 'combobox':
                    validation_rules['ignore'] = list()
                    validation_rules['messages']['X211bHRpcGxlX2Nob2ljZQ=='] = {'required': status.question.fields[0].validation_message('combobox required', status, word("You need to select one or type in a new value."))}
                else:
                    validation_rules['ignore'] = None
                    validation_rules['messages']['X211bHRpcGxlX2Nob2ljZQ=='] = {'required': status.question.fields[0].validation_message('multiple choice required', status, word("You need to select one."))}
                validation_rules['rules']['X211bHRpcGxlX2Nob2ljZQ=='] = {'required': True}
            output += '                <div id="daerrorcontainer" style="display:none"></div>\n'
            if status.question.question_variety == "radio":
                output += "                </fieldset>\n"
            output += status.submit
            output += '                <fieldset class="da-field-buttons"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
            output += '                <div>' + back_button + '\n'
            output += '                  <button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit"><span>' + continue_label + '</span></button>' + help_button + '\n'
            output += '                </div></fieldset>\n'
        else:
            output += status.submit
            output += '                <fieldset class="da-field-buttons"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
            output += '                <div>' + back_button + '\n'
            if hasattr(status.question.fields[0], 'saveas'):
                btn_class = ' btn-primary'
                if hasattr(status.question.fields[0], 'has_code') and status.question.fields[0].has_code:
                    pairlist = list(status.selectcompute[status.question.fields[0].number])
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if 'image' in pair:
                            the_icon = '<span>' + icon_html(status, pair['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</span>';
                            btn_class = ' btn-light btn-da btn-da-custom'
                        else:
                            the_icon = ''
                        if True or pair['key'] is not None:
                            output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value="' + text_type(pair['key']) + '"><span>' + the_icon + markdown_to_html(pair['label'], status=status, trim=True, do_terms=False) + '</span></button>\n'
                        else:
                            output += markdown_to_html(pair['label'], status=status)
                else:
                    choicelist = status.selectcompute[status.question.fields[0].number]
                    #choicelist = list(status.question.fields[0].choices)
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(choicelist)
                    for choice in choicelist:
                        if 'image' in choice:
                            the_icon = '<span>' + icon_html(status, choice['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</span>';
                            btn_class = ' btn-light btn-da btn-da-custom'
                        else:
                            the_icon = ''
                        if 'help' in choice:
                            the_help = choice['help']
                        else:
                            the_help = ''
                        output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value="' + text_type(choice['key']) + '"><span>' + the_icon + markdown_to_html(choice['label'], status=status, trim=True, do_terms=False) + '</span></button>\n'
            else:
                indexno = 0
                for choice in status.selectcompute[status.question.fields[0].number]:
                #for choice in status.question.fields[0].choices:
                    btn_class = ' btn-primary'
                    if 'image' in choice:
                        the_icon = '<span>' + icon_html(status, choice['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</span>'
                        btn_class = ' btn-light btn-da btn-da-custom'
                    else:
                        the_icon = ''
                    if 'help' in choice:
                        the_help = choice['help']
                    else:
                        the_help = ''
                    if 'default' in choice:
                        is_default = choice['default']
                    else:
                        is_default = False
                    if isinstance(choice['key'], Question) and choice['key'].question_type in ("exit", "logout", "continue", "restart", "refresh", "signin", "register", "leave", "link"):
                        if choice['key'].question_type in ("continue", "register"):
                            btn_class = ' btn-primary'
                        elif choice['key'].question_type in ("leave", "link", "restart"):
                            btn_class = ' btn-warning'
                        elif choice['key'].question_type == "refresh":
                            btn_class = ' btn-success'
                        elif choice['key'].question_type == "signin":
                            btn_class = ' btn-info'
                        elif choice['key'].question_type in ("exit", "logout"):
                            btn_class = ' btn-danger'
                    #output += '                  <input type="hidden" name="_event" value=' + myb64doublequote(json.dumps(list(status.question.fields_used))) + ' />\n'
                    output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + '" name="X211bHRpcGxlX2Nob2ljZQ==" value="' + str(indexno) + '"><span>' + the_icon + markdown_to_html(choice['label'], status=status, trim=True, do_terms=False, strip_newlines=True) + '</span></button>\n'
                    indexno += 1
            output += help_button
            output += '                </div></fieldset>\n'
        #output += question_name_tag(status.question)
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type == 'deadend':
        output += status.pre
        output += indent_by(audio_text, 12) + '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if back_button != '' or help_button != '':
            output += status.submit
            output += '                <fieldset class="da-field-buttons"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
            output += '                <div class="form-actions">' + back_button + help_button + '</div></fieldset>\n'
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
    else:
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" class="form-horizontal" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-field-buttons"><legend class="sr-only">' + word('Press one of the following buttons:') + '</legend>\n'
        output += '                <div class="form-actions">' + back_button + '\n                <button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit"><span>' + continue_label + '</span></button>' + help_button + '</div></fieldset>\n'
        #output += question_name_tag(status.question)
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
        output += tracker_tag(status)
        output += '            </form>\n'
    if len(status.attachments) > 0:
        output += '            <br/>\n'
        if len(status.attachments) > 1:
            output += '            <h2 class="sr-only">' + word('Attachments') + "</h2>\n"
            output += '            <div class="alert alert-success" role="alert">' + word('attachment_message_plural') + '</div>\n'
        else:
            output += '            <h2 class="sr-only">' + word('Attachment') + "</h2>\n"
            output += '            <div class="alert alert-success" role="alert">' + word('attachment_message_singular') + '</div>\n'
        attachment_index = 0
        editable_included = False
        if len(status.attachments) > 1:
            file_word = 'files'
        else:
            file_word = 'file'
        editable_name = ''
        for attachment in status.attachments:
            if 'rtf' in attachment['valid_formats'] or 'rtf to docx' in attachment['valid_formats'] or 'docx' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    editable_included = True
                    if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                        if 'docx' in attachment['valid_formats'] or 'rtf to docx' in attachment['valid_formats']:
                            editable_name = 'RTF and DOCX files'
                        else:
                            editable_name = 'RTF ' + file_word
                    elif 'docx' in attachment['valid_formats'] or 'rtf to docx' in attachment['valid_formats']:
                        editable_name = 'DOCX ' + file_word
            if debug and len(attachment['markdown']):
                if 'html' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    md_format = 'html'
                else:
                    for format_type in attachment['valid_formats']:
                        md_format = format_type
                        break
                if md_format in attachment['markdown'] and attachment['markdown'][md_format] != '':
                    show_markdown = True
                else:
                    show_markdown = False
            else:
                show_markdown = False
            #logmessage("markdown is " + str(attachment['markdown']))
            if 'pdf' in attachment['valid_formats'] or 'rtf' in attachment['valid_formats'] or 'rtf to docx' in attachment['valid_formats'] or 'docx' in attachment['valid_formats'] or (debug and 'tex' in attachment['valid_formats']) or '*' in attachment['valid_formats']:
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
            output += '            <div>\n'
            if True or show_preview or show_markdown:
                output += '              <ul role="tablist" class="nav nav-tabs" role="tablist">\n'
                if show_download:
                    output += '                <li class="nav-item"><a class="nav-link active" id="dadownload-tab' + str(attachment_index) + '" href="#dadownload' + str(attachment_index) + '" data-toggle="tab" role="tab" aria-controls="dadownload' + str(attachment_index) + '" aria-selected="true">' + word('Download') + '</a></li>\n'
                if show_preview:
                    output += '                <li class="nav-item"><a class="nav-link" id="dapreview-tab' + str(attachment_index) + '" href="#dapreview' + str(attachment_index) + '" data-toggle="tab" role="tab" aria-controls="dapreview' + str(attachment_index) + '" aria-selected="false">' + word('Preview') + '</a></li>\n'
                if show_markdown:
                    output += '                <li class="nav-item"><a class="nav-link" id="damarkdown-tab' + str(attachment_index) + '" href="#damarkdown' + str(attachment_index) + '" data-toggle="tab" role="tab" aria-controls="damarkdown' + str(attachment_index) + '" aria-selected="false">' + word('Markdown') + '</a></li>\n'
                output += '              </ul>\n'
            output += '              <div class="tab-content" id="databcontent' + str(attachment_index) + '">\n'
            if show_download:
                output += '                <div class="tab-pane show active" id="dadownload' + str(attachment_index) + '" role="tabpanel" aria-labelledby="dadownload-tab' + str(attachment_index) + '">\n'
                if multiple_formats:
                    output += '                  <p>' + word('save_as_multiple') + '</p>\n'
                #else:
                    #output += '                  <p>' + word('save_as_singular') + '</p>\n'
                if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['pdf'], display_filename=attachment['filename'] + '.pdf') + '" target="_blank"><i class="fas fa-print fa-fw"></i> PDF</a> (' + word('pdf_message') + ')</p>\n'
                if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['rtf'], display_filename=attachment['filename'] + '.rtf') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> RTF</a> (' + word('rtf_message') + ')</p>\n'
                if 'docx' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['docx'], display_filename=attachment['filename'] + '.docx') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> DOCX</a> (' + word('docx_message') + ')</p>\n'
                if 'rtf to docx' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['rtf to docx'], display_filename=attachment['filename'] + '.docx') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> DOCX</a> (' + word('docx_message') + ')</p>\n'
                if 'tex' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['tex'], display_filename=attachment['filename'] + '.tex') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> LaTeX</a> (' + word('tex_message') + ')</p>\n'
                output += '                </div>\n'
            if show_preview:
                output += '                <div class="tab-pane" id="dapreview' + str(attachment_index) + '" role="tabpanel" aria-labelledby="dapreview-tab' + str(attachment_index) + '">\n'
                output += '                  <blockquote class="blockquote">' + text_type(attachment['content']['html']) + '</blockquote>\n'
                output += '                </div>\n'
            if show_markdown:
                output += '                <div class="tab-pane" id="damarkdown' + str(attachment_index) + '" role="tabpanel" aria-labelledby="damarkdown-tab' + str(attachment_index) + '">\n'
                output += '                  <pre class="mb-2 mt-2">' + safe_html(attachment['markdown'][md_format]) + '</pre>\n'
                output += '                </div>\n'
            output += '              </div>\n            </div>\n'
            attachment_index += 1
        if status.extras.get('allow_emailing', True) or status.extras.get('allow_downloading', False):
            if len(status.attachments) > 1:
                email_header = word("E-mail these documents")
                download_header = word("Download all documents as a ZIP file")
            else:
                email_header = word("E-mail this document")
                download_header = word("Download this document as a ZIP file")
            if status.extras.get('allow_emailing', True):
                if status.current_info['user']['is_authenticated'] and status.current_info['user']['email']:
                    default_email = status.current_info['user']['email']
                else:
                    default_email = ''
                output += """\
            <div id="daaccordionOne">
              <div class="card mb-2">
                <div class="card-header" id="daheadingOne">
                  <a role="button" data-toggle="collapse" data-parent="#daaccordionOne" href="#dacollapseOne" aria-expanded="true" aria-controls="dacollapseOne">""" + email_header + """</a>
                </div>
                <div id="dacollapseOne" class="collapse show" aria-labelledby="daheadingOne">
                  <div class="card-body">
                    <form aria-labelledby="daheadingOne" action=\"""" + root + """\" id="daemailform" class="form-horizontal" method="POST">
                      <div class="form-group row"><label for="da_attachment_email_address" class="col-md-4 col-form-label datext-right">""" + word('E-mail address') + """</label><div class="col-md-8"><input alt=""" + json.dumps(word("Input box")) + """ class="form-control" type="email" name="_attachment_email_address" id="da_attachment_email_address" value=""" + '"' + str(default_email) + '"' + """/></div></div>"""
                if editable_included:
                    output += """
                      <div class="form-group row"><div class="col-md-4 col-form-label datext-right"></div><div class="col-md-8"><input alt=""" + json.dumps(word("Check box") + ", " + word('Include ' + editable_name + ' for editing')) + """ type="checkbox" value="True" name="_attachment_include_editable" id="da_attachment_include_editable"/>&nbsp;<label for="da_attachment_include_editable" class="danobold">""" + word('Include ' + editable_name + ' for editing') + '</label></div></div>\n'
                output += """
                      <button class="btn btn-primary" type="submit"><span>""" + word('Send') + '</span></button>\n                      <input type="hidden" name="_email_attachments" value="1"/>'
                output += """
                      <input type="hidden" name="csrf_token" value=""" + json.dumps(server.generate_csrf()) + """/>
                    </form>
                  </div>
                </div>
              </div>
            </div>
"""
            if status.extras.get('allow_downloading', False):
                output += """
            <div id="daaccordionTwo">
              <div class="card">
                <div class="card-header" id="daheadingTwo">
                  <a role="button" data-toggle="collapse" data-parent="#daaccordionTwo" href="#dacollapseTwo" aria-expanded="true" aria-controls="dacollapseTwo">""" + download_header + """</a>
                </div>
                <div id="dacollapseTwo" class="collapse show" aria-labelledby="daheadingTwo">
                  <div class="card-body">
                    <form aria-labelledby="daheadingTwo" action=\"""" + root + """\" id="dadownloadform" class="form-horizontal" method="POST">"""
                if editable_included:
                    output += """
                      <div class="form-group row"><div class="col-md-12"><input alt=""" + json.dumps(word("Check box") + ", " + word('Include ' + editable_name + ' for editing')) + """ type="checkbox" value="True" name="_attachment_include_editable" id="da_attachment_include_editable"/>&nbsp;<label for="da_attachment_include_editable" class="danobold">""" + word('Include ' + editable_name + ' for editing') + '</label></div></div>\n'
                output += """
                      <button class="btn btn-primary" type="submit"><span>""" + word('Download All') + '</span></button>\n                      <input type="hidden" name="_download_attachments" value="1"/>'
                output += """
                      <input type="hidden" name="csrf_token" value=""" + json.dumps(server.generate_csrf()) + """/>
                    </form>
                  </div>
                </div>
              </div>
            </div>
"""
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, indent=18, divclass="daundertext")
    if status.question.question_type == "signature":
        output += '<div class="dasigpost">' + status.post + '</div>'
        # if len(status.attributions):
        #     output += '            <br/><br/><br/><br/><br/><br/><br/>\n'
        # for attribution in sorted(status.attributions):
        #     output += '            <div><cite><small>' + markdown_to_html(attribution, status=status, strip_newlines=True) + '</small></cite></div>\n'
    if debug or status.using_screen_reader:
        status.screen_reader_text['question'] = text_type(output)
    if 'rightText' in status.extras:
        if status.using_navigation == 'vertical':
            output += '            <div id="darightbottom" class="d-block d-lg-none daright">\n'
        else:
            if status.question.interview.flush_left:
                output += '            <div id="darightbottom" class="d-block d-lg-none daright">\n'
            else:
                output += '            <div id="darightbottom" class="d-block d-lg-none daright">\n'
        output += markdown_to_html(status.extras['rightText'], trim=False, status=status) + "\n"
        output += '            </div>\n'
    master_output += output
    master_output += '          </section>\n'
    master_output += '          <section id="dahelp" class="tab-pane ' + grid_class + '">\n'
    output = text_type() + '            <div class="mt-2 mb-2"><a href="#daquestion" role="button" id="dabackToQuestion" class="btn btn-info"><i class="fas fa-caret-left"></i> ' + word("Back to question") + '</a></div>'
    output += """
            <div id="daPhoneMessage" class="row dainvisible">
              <div class="col-md-12">
                <h1 class="h3">""" + word("Telephone assistance") + """</h1>
                <p></p>
              </div>
            </div>
            <div id="daChatBox" class="dainvisible">
              <div class="row">
                <div class="col-md-12 dachatbutton">
                  <a href="#" id="daChatOnButton" role="button" class="btn btn-success">""" + word("Activate chat") + """</a>
                  <a href="#" id="daChatOffButton" role="button" class="btn btn-warning">""" + word("Turn off chat") + """</a>
                  <h1 class="h3" id="dachatHeading">""" + word("Live chat") + """</h1>
                </div>
              </div>
              <div class="row">
                <div class="col-md-12">
                  <ul class="list-group dachatbox" id="daCorrespondence"></ul>
                </div>
              </div>
              <form aria-labelledby="dachatHeading" id="dachat" autocomplete="off">
                <div class="row">
                  <div class="col-md-12">
                    <div class="input-group">
                      <label for="daMessage" class="sr-only">""" + word("Chat message you want to send") + """</label>
                      <input type="text" class="form-control daChatMessage" id="daMessage" placeholder=""" + json.dumps(word("Type your message here.")) + """>
                      <button class="btn btn-secondary daChatButton" id="daSend" type="button">""" + word("Send") + """</button>
                    </div>
                  </div>
                </div>
              </form>
              <div class="row dainvisible">
                <div class="col-md-12">
                  <p id="daPushResult"></p>
                </div>
              </div>
              <div class="row datopspace">
                <div class="col-md-12">
                  <p>
                    <span class="da-peer-message" id="dapeerMessage"></span>
                    <span class="da-peer-message" id="dapeerHelpMessage"></span>
                  </p>
                </div>
              </div>
            </div>
"""
    if len(status.helpText):
        if status.using_screen_reader and 'help' in status.screen_reader_links:
            output += '            <div class="daaudiovideo-control">\n' + indent_by(audio_control(status.screen_reader_links['help'], preload="none", title_text=word('Read this screen out loud')), 14) + '            </div>\n'
        for help_section in status.helpText:
            if help_section['heading'] is not None:
                output += '            <div class="da-page-header"><h1 class="h3">' + help_section['heading'].strip() + '</h1></div>\n'
            elif len(status.helpText) > 1:
                output += '            <div class="da-page-header"><h1 class="h3">' + word('Help with this question') + '</h1></div>\n'
            if help_section['audiovideo'] is not None:
                uses_audio_video = True
                audio_urls = get_audio_urls(help_section['audiovideo'])
                if len(audio_urls):
                    output += '            <div class="daaudiovideo-control">\n' + indent_by(audio_control(audio_urls), 14) + '            </div>\n'
                video_urls = get_video_urls(help_section['audiovideo'])
                if len(video_urls):
                    output += '            <div class="daaudiovideo-control">\n' + indent_by(video_control(video_urls), 14) + '            </div>\n'
            output += markdown_to_html(help_section['content'], status=status, indent=12)
        # if len(status.attributions):
        #     output += '            <br/><br/><br/><br/><br/><br/><br/>\n'
        # for attribution in sorted(status.attributions):
        #     output += '            <div><cite><small>' + markdown_to_html(attribution, status=status, strip_newlines=True) + '</small></cite></div>\n'
        if debug or status.using_screen_reader:
            status.screen_reader_text['help'] = text_type(output)
    master_output += output
    master_output += '          </section>\n'
    # if status.question.question_type == "fields":
    #     status.extra_scripts.append("""\
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
    add_validation(status.extra_scripts, validation_rules, field_error)
    for element_id_unescaped in onchange:
        element_id = re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', element_id_unescaped)
        the_script = """\
    <script>
      $('[name=""" + '"' + element_id + '"' + """]').change(function(){
        if ($(this).attr('type') == "checkbox" || $(this).attr('type') == "radio"){
          theVal = $('[name=""" + '"' + element_id + '"' + """]:checked').val();
        }
        else{
          theVal = $( this ).val();
        }
        var n = 0;
        if ($(this).data('disableothers')){
          var id_list = JSON.parse(atob($(this).data('disableothers')));
          var n = id_list.length;
        }
        if (n){
          for(var i = 0; i < n; ++i){
            var the_element_id = id_list[i].replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
            if (theVal == null || theVal == ""){
              $("#daform [name='" + the_element_id + "']").prop("disabled", false);
              $("#daform [name='" + the_element_id + "']").parent().parent().removeClass("dagreyedout");
            }
            else{
              $("#daform [name='" + the_element_id + "']").prop("disabled", true);
              $("#daform [name='" + the_element_id + "']").parent().parent().addClass("dagreyedout");
            }
          }
        }
        else{
          if (theVal == null || theVal == ""){
            $("#daform input:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").prop("disabled", false);
            $("#daform select:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").prop("disabled", false);
            $("#daform textarea:not([name='"""  + element_id  + """']):not([type=hidden])").prop("disabled", false);
            $("#daform input:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").parent().parent().removeClass("dagreyedout");
            $("#daform select:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").parent().parent().removeClass("dagreyedout");
            $("#daform textarea:not([name='"""  + element_id  + """']):not([type=hidden])").parent().parent().removeClass("dagreyedout");
          }
          else{
            $("#daform input:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").prop("disabled", true);
            $("#daform select:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").prop("disabled", true);
            $("#daform textarea:not([name='"""  + element_id  + """']):not([type=hidden])").prop("disabled", true);
            $("#daform input:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").parent().parent().addClass("dagreyedout");
            $("#daform select:not([name='"""  + element_id  + """']):not([id^='"""  + element_id  + """']):not([type=hidden])").parent().parent().addClass("dagreyedout");
            $("#daform textarea:not([name='"""  + element_id  + """']):not([type=hidden])").parent().parent().addClass("dagreyedout");
          }
        }
      });
      $("[data-disableothers]").trigger('change');
    </script>
"""
        status.extra_scripts.append(the_script)
    if 'track_location' in status.extras and status.extras['track_location']:
        track_js = """\
    <script>
      function daSetPosition(position) {
        document.getElementById('da_track_location').value = JSON.stringify({'latitude': position.coords.latitude, 'longitude': position.coords.longitude})
      }
      function daShowError(error) {
        switch(error.code) {
          case error.PERMISSION_DENIED:
            document.getElementById('da_track_location').value = JSON.stringify({error: "User denied the request for Geolocation"});
            console.log("User denied the request for Geolocation.");
            break;
          case error.POSITION_UNAVAILABLE:
            document.getElementById('da_track_location').value = JSON.stringify({error: "Location information is unavailable"});
            console.log("Location information is unavailable.");
            break;
          case error.TIMEOUT:
            document.getElementById('da_track_location').value = JSON.stringify({error: "The request to get user location timed out"});
            console.log("The request to get user location timed out.");
            break;
          case error.UNKNOWN_ERROR:
            document.getElementById('da_track_location').value = JSON.stringify({error: "An unknown error occurred"});
            console.log("An unknown error occurred.");
            break;
        }
      }
      $( document ).ready(function() {
        $(function () {
          if (navigator.geolocation) {
            document.getElementById('da_track_location').value = JSON.stringify({error: "getCurrentPosition was still running"});
            navigator.geolocation.getCurrentPosition(daSetPosition, daShowError, {timeout: 1000, maximumAge: 3600000});
          }
          else{
            document.getElementById('da_track_location').value = JSON.stringify({error: "navigator.geolocation not available in browser"});
          }
        });
      });
    </script>"""
        status.extra_scripts.append(track_js)
    if autocomplete_id:
        status.extra_scripts.append("""
<script>
  daInitAutocomplete(""" + json.dumps(autocomplete_id) + """);
</script>
""")
    if len(status.maps):
        status.extra_scripts.append("""
<script>
  daInitMap([""" + ", ".join(status.maps) + """]);
</script>
""")
        # google_config = daconfig.get('google', dict())
        # if 'google maps api key' in google_config:
        #     api_key = google_config.get('google maps api key')
        # elif 'api key' in google_config:
        #     api_key = google_config.get('api key')
        # else:
        #     raise Exception('google API key not provided')
        #status.extra_scripts.append('<script async defer src="https://maps.googleapis.com/maps/api/js?key=' + urllibquote(api_key) + '&callback=daInitMap"></script>')
    return master_output

def add_validation(extra_scripts, validation_rules, field_error):
    if field_error is None:
        error_show = ''
    else:
        error_mess = dict()
        for key, val in field_error.items():
            error_mess[key] = val
        error_show = "\n  daValidator.showErrors(" + json.dumps(error_mess) + ");"
    extra_scripts.append("""<script>
  var daValidationRules = """ + json.dumps(validation_rules) + """;
  daValidationRules.submitHandler = daValidationHandler;
  daValidationRules.onfocusout = daInjectTrim($.validator.defaults.onfocusout);
  if ($("#daform").length > 0){
    //console.log("Running validator")
    var daValidator = $("#daform").validate(daValidationRules);""" + error_show + """
  }
</script>""")

def input_for(status, field, wide=False, embedded=False):
    output = text_type()
    if field.number in status.defaults:
        defaultvalue_set = True
        if isinstance(status.defaults[field.number], (string_types, int, float)):
            defaultvalue = text_type(status.defaults[field.number])
        else:
            defaultvalue = status.defaults[field.number]
    else:
        defaultvalue_set = False
        defaultvalue = None
    if field.number in status.hints:
        placeholdertext = ' placeholder=' + json.dumps(text_type(status.hints[field.number].replace('\n', ' ')))
    else:
        placeholdertext = ''
    if (hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in status.extras) or ('show_if_js' in field.extras)) and hasattr(field, 'saveas')) or (hasattr(field, 'disableothers') and field.disableothers):
        saveas_string = safeid('_field_' + str(field.number))
    else:
        saveas_string = field.saveas
    if hasattr(field, 'disableothers') and field.disableothers:
        if 'disableothers' in status.extras and field.number in status.extras['disableothers']:
            disable_others_data = ' data-disableothers=' + myb64doublequote(json.dumps(status.extras['disableothers'][field.number]))
        else:
            disable_others_data = ' data-disableothers=' + myb64doublequote(json.dumps(True))
    else:
        disable_others_data = ''
    if 'inline width' in status.extras and field.number in status.extras['inline width']:
        inline_width = status.extras['inline width'][field.number]
    else:
        inline_width = None
    if embedded:
        extra_class = ' dainput-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'date':
            extra_class += ' dadate-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'time':
            extra_class += ' datime-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'datetime':
            extra_class += ' dadate-embedded'
        if inline_width is not None:
            extra_style = ' style="min-width: ' + text_type(inline_width) + '"'
        else:
            extra_style = ''
        extra_checkbox = ' dacheckbox-embedded'
        extra_radio = 'daradio-embedded'
        if field.number in status.labels:
            label_text = strip_quote(to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), dict(), list(), status).strip())
        else:
            label_text = 'no label'
        if label_text != 'no label':
            title_text = ' title=' + json.dumps(label_text)
        else:
            title_text = ''
        if hasattr(field, 'datatype') and field.datatype == 'object':
            extra_class += ' daobject'
    else:
        extra_style = ''
        if hasattr(field, 'datatype') and field.datatype == 'object':
            extra_class = 'daobject'
        else:
            extra_class = ''
        extra_checkbox = ''
        extra_radio = ''
        title_text = ''
    if hasattr(field, 'choicetype'):
        # logmessage("In a choicetype where field datatype is " + field.datatype)
        # if hasattr(field, 'inputtype'):
        #     logmessage("inputtype is" + field.inputtype)
        # else:
        #     logmessage("No inputtype")
        if field.choicetype in ['compute', 'manual']:
            pairlist = list(status.selectcompute[field.number])
        else:
            raise Exception("Unknown choicetype " + field.choicetype)
        if hasattr(field, 'shuffle') and field.shuffle:
            random.shuffle(pairlist)
        if field.datatype in ['checkboxes', 'object_checkboxes']:
            #if len(pairlist) == 0:
            #    return '<input type="hidden" name="' + safeid(from_safeid(saveas_string))+ '" value="None"/>'
            inner_fieldlist = list()
            id_index = 0
            if embedded:
                output += '<span class="da-embed-checkbox-wrapper">'
            else:
                output += '<fieldset class="da-field-checkboxes"><legend class="sr-only">' + word('Checkboxes:') + '</legend>'
            for pair in pairlist:
                if 'image' in pair:
                    the_icon = icon_html(status, pair['image']) + ' '
                else:
                    the_icon = ''
                helptext = pair.get('help', None)
                if True or pair['key'] is not None:
                    inner_field = safeid(from_safeid(saveas_string) + "[" + myb64quote(pair['key']) + "]")
                    #sys.stderr.write("I've got a " + repr(pair['label']) + "\n")
                    formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if 'default' in pair and pair['default']:
                        ischecked = ' checked'
                    elif defaultvalue is None:
                        ischecked = ''
                    elif isinstance(defaultvalue, (list, set)) and text_type(pair['key']) in defaultvalue:
                        ischecked = ' checked'
                    elif isinstance(defaultvalue, dict) and text_type(pair['key']) in defaultvalue and defaultvalue[text_type(pair['key'])]:
                        ischecked = ' checked'
                    elif (hasattr(defaultvalue, 'elements') and isinstance(defaultvalue.elements, dict)) and text_type(pair['key']) in defaultvalue.elements and defaultvalue.elements[text_type(pair['key'])]:
                        ischecked = ' checked'
                    elif pair['key'] is defaultvalue:
                        ischecked = ' checked'
                    elif isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == text_type(defaultvalue):
                        ischecked = ' checked'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input aria-label="' + formatted_item + '" class="dacheckbox-embedded dafield' + str(field.number) + ' danon-nota-checkbox" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"' + ischecked + disable_others_data + '/>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    else:
                        inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="' + 'dafield' + str(field.number) + ' danon-nota-checkbox da-to-labelauty checkbox-icon' + extra_checkbox + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"' + ischecked + disable_others_data + '/>', helptext, status))
                else:
                    inner_fieldlist.append(help_wrap('<div>' + markdown_to_html(pair['label'], status=status) + '</div>', helptext, status))
                id_index += 1
            if 'nota' in status.extras and field.number in status.extras['nota'] and status.extras['nota'][field.number] is not False:
                if defaultvalue_set and defaultvalue is None:
                    ischecked = ' checked'
                else:
                    ischecked = ''
                if status.extras['nota'][field.number] is True:
                    formatted_item = word("None of the above")
                else:
                    formatted_item = markdown_to_html(text_type(status.extras['nota'][field.number]), status=status, trim=True, escape=(not embedded), do_terms=False)
                if embedded:
                    inner_fieldlist.append('<input class="dafield' + str(field.number) + ' dacheckbox-embedded danota-checkbox" id="_ignore' + str(field.number) + '" type="checkbox" name="_ignore' + str(field.number) + '"' + disable_others_data + '/>&nbsp;<label for="_ignore' + str(field.number) + '">' + formatted_item + '</label>')
                else:
                    inner_fieldlist.append('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="' + 'dafield' + str(field.number) + ' danota-checkbox da-to-labelauty checkbox-icon' + extra_checkbox + '"' + title_text + ' type="checkbox" name="_ignore' + str(field.number) + '" ' + ischecked + disable_others_data + '/>')
            elif (hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in status.extras) or ('maxlength' in field.extras and 'maxlength' in status.extras))):
                inner_fieldlist.append('<input value="" type="hidden" name="_ignore' + str(field.number) + '"/>')
            if embedded:
                output += u' '.join(inner_fieldlist) + '</span>'
            else:
                output += u''.join(inner_fieldlist)
            output += '</fieldset>'
            if field.datatype in ['object_checkboxes']:                
                output += '<input type="hidden" name="' + safeid(from_safeid(saveas_string) + ".gathered") + '" value="True"' + disable_others_data + '/>'
        elif field.datatype == 'object_radio' or (hasattr(field, 'inputtype') and field.inputtype == 'radio'):
            if field.datatype == 'object':
                daobject = ' daobject'
            else:
                daobject = ''
            inner_fieldlist = list()
            id_index = 0
            try:
                defaultvalue_printable = text_type(defaultvalue)
                defaultvalue_is_printable = True
            except:
                defaultvalue_printable = None
                defaultvalue_is_printable = False
            if embedded:
                default_selected = False
                for pair in pairlist:
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and defaultvalue_printable and text_type(pair['label']) == defaultvalue_printable):
                        ischecked = ' checked="checked"'
                        default_selected = True
                    else:
                        ischecked = ''
                    inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    id_index += 1
                if 'nota' in status.extras and field.number in status.extras['nota'] and status.extras['nota'][field.number] is not False:
                    if status.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = markdown_to_html(text_type(status.extras['nota'][field.number]), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if not default_selected:
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    the_icon = ''
                    inner_fieldlist.append('<input class="daradio-embedded' + daobject + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="" checked="checked"' + disable_others_data + '>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                output += '<span class="da-embed-radio-wrapper">'
                output += " ".join(inner_fieldlist)
                output += '</span>'
            else:
                default_selected = False
                output += '<fieldset class="da-field-radio"><legend class="sr-only">' + word('Choices:') + '</legend>'
                for pair in pairlist:
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    helptext = pair.get('help', None)
                    if True or pair['key'] is not None:
                        #sys.stderr.write(str(saveas_string) + "\n")
                        formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and defaultvalue_is_printable and text_type(pair['label']) == defaultvalue_printable):
                            ischecked = ' checked="checked"'
                            default_selected = True
                        else:
                            ischecked = ''
                        inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + daobject + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '/>', helptext, status))
                    else:
                        inner_fieldlist.append(help_wrap('<div>' + the_icon + markdown_to_html(text_type(pair['label']), status=status) + '</div>', helptext, status))
                    id_index += 1
                if 'nota' in status.extras and field.number in status.extras['nota'] and status.extras['nota'][field.number] is not False:
                    if status.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = markdown_to_html(text_type(status.extras['nota'][field.number]), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if not default_selected:
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    the_icon = ''
                    inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=""' + ischecked + disable_others_data + '/>', helptext, status))
                if embedded:
                    output += '<span class="da-embed-radio-wrapper">' + " ".join(inner_fieldlist) + '</span>'
                else:
                    output += "".join(inner_fieldlist)
                output += "</fieldset>"
        else:
            if hasattr(field, 'datatype') and field.datatype == 'object':
                daobject = ' daobject'
            else:
                daobject = ''
            if embedded:
                emb_text = 'class="dainput-embedded' + daobject + '" '
                if inline_width is not None:
                    emb_text += 'style="min-width: ' + text_type(inline_width) + '" '
                label_text = strip_quote(to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), dict(), list(), status).strip())
                if label_text != 'no label':
                    emb_text += 'title=' + json.dumps(label_text) + ' '
            else:
                output += '<p class="sr-only">' + word('Select box') + '</p>'
                if hasattr(field, 'inputtype') and field.inputtype == 'combobox':
                    emb_text = 'class="form-control combobox' + daobject + '" '
                else:
                    emb_text = 'class="form-control' + daobject + '" '
            if embedded:
                output += '<span class="da-inline-error-wrapper">'
            output += '<select ' + emb_text + 'name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '" ' + disable_others_data + '>'
            if hasattr(field, 'inputtype') and field.inputtype == 'combobox' and not embedded:
                if placeholdertext == '':
                    output += '<option value="">' + word('Select one') + '</option>'
                else:
                    output += '<option value="">' + text_type(status.hints[field.number].replace('\n', ' ')) + '</option>'
            else:
                if placeholdertext == '':
                    output += '<option value="">' + word('Select...') + '</option>'
                else:
                    output += '<option value="">' + text_type(status.hints[field.number].replace('\n', ' ')) + '</option>'
            try:
                defaultvalue_printable = text_type(defaultvalue)
                defaultvalue_is_printable = True
            except:
                defaultvalue_printable = None
                defaultvalue_is_printable = False
            #logmessage("defaultvalue is " + repr(defaultvalue))
            #logmessage("defaultvalue_printable is " + repr(defaultvalue_printable))
            #logmessage("defaultvalue_is_printable is " + repr(defaultvalue_is_printable))
            for pair in pairlist:
                if True or pair['key'] is not None:
                    formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, do_terms=False)
                    #logmessage("Considering " + repr(pair['key']) + " and " + repr(pair['label']))
                    output += '<option value="' + text_type(pair['key']) + '"'
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and defaultvalue_is_printable and text_type(pair['label']) == defaultvalue_printable):
                        output += ' selected="selected"'
                    output += '>' + formatted_item + '</option>'
            if embedded:
                output += '</select></span> '
            else:
                output += '</select> '
    elif hasattr(field, 'datatype'):
        if field.datatype == 'boolean':
            label_text = markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True, escape=(not embedded), do_terms=False)
            if hasattr(field, 'inputtype') and field.inputtype in ['yesnoradio', 'noyesradio']:
                inner_fieldlist = list()
                id_index = 0
                if embedded:
                    output += '<span class="da-embed-radio-wrapper">'
                else:
                    output += '<fieldset class="da-field-radio"><legend class="sr-only">' + word('Choices:') + '</legend>'
                if field.sign > 0:
                    for pair in [dict(key='True', label=status.question.yes()), dict(key='False', label=status.question.no())]:
                        formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if 'image' in pair:
                            the_icon = icon_html(status, pair['image']) + ' '
                        else:
                            the_icon = ''
                        helptext = pair.get('help', None)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == text_type(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        if embedded:
                            inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                        else:
                            inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '/>', helptext, status))
                        id_index += 1
                else:
                    for pair in [dict(key='False', label=status.question.yes()), dict(key='True', label=status.question.no())]:
                        formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if 'image' in pair:
                            the_icon = icon_html(status, pair['image']) + ' '
                        else:
                            the_icon = ''
                        helptext = pair.get('help', None)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == text_type(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        if embedded:
                            inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                        else:
                            inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '/>', helptext, status))
                        id_index += 1
                if embedded:
                    output += " ".join(inner_fieldlist) + '</span>'
                else:
                    output += "".join(inner_fieldlist) + '</fieldset>'
            else:
                if hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                    if isinstance(field.uncheckothers, list):
                        uncheck = ' dauncheckspecificothers'
                        uncheck_list = [status.saveas_to_use[safeid(y)] for y in field.uncheckothers if safeid(y) in status.saveas_to_use]
                        uncheckdata = ' data-unchecklist=' + myb64doublequote(json.dumps(uncheck_list))
                    else:
                        uncheck = ' dauncheckothers'
                        uncheckdata = ''
                else:
                    uncheck = ' dauncheckable'
                    uncheckdata = ''
                if defaultvalue in ('False', 'false', 'FALSE', 'no', 'No', 'NO', 'Off', 'off', 'OFF', 'Null', 'null', 'NULL'):
                    defaultvalue = False
                if (defaultvalue and field.sign > 0) or (defaultvalue is False and field.sign < 0):
                    docheck = ' checked'
                else:
                    docheck = ''
                if embedded:
                    output += '<span class="da-embed-yesno-wrapper">'
                else:
                    output += '<fieldset class="da-field-checkbox"><legend class="sr-only">' + word('Choices:') + '</legend>'
                if field.sign > 0:
                    if embedded:
                        output += '<input class="dacheckbox-embedded' + uncheck + '"' + uncheckdata + ' type="checkbox" value="True" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + '/>&nbsp;<label for="' + escape_id(saveas_string) + '">' + label_text + '</label>'
                    else:
                        output += '<input aria-label="' + label_text + '" alt="' + label_text + '" class="da-to-labelauty checkbox-icon' + extra_checkbox + uncheck + '"' + title_text + uncheckdata + ' type="checkbox" value="True" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + '/> '
                else:
                    if embedded:
                        output += '<input class="dacheckbox-embedded' + uncheck + '"' + uncheckdata + ' type="checkbox" value="False" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + '/>&nbsp;<label for="' + escape_id(saveas_string) + '">' + label_text + '</label>'
                    else:
                        output += '<input aria-label="' + label_text + '" alt="' + label_text + '" class="da-to-labelauty checkbox-icon' + extra_checkbox + uncheck + '"' + title_text + uncheckdata + ' type="checkbox" value="False" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + '/> '
                if embedded:
                    output += '</span>'
                else:
                    output += '</fieldset>'
        elif field.datatype == 'threestate':
            inner_fieldlist = list()
            id_index = 0
            if embedded:
                output += '<span class="da-embed-threestate-wrapper">'
            else:
                output += '<fieldset class="field-radio"><legend class="sr-only">' + word('Choices:') + '</legend>'
            if field.sign > 0:
                for pair in [dict(key='True', label=status.question.yes()), dict(key='False', label=status.question.no()), dict(key='None', label=status.question.maybe())]:
                    formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    helptext = pair.get('help', None)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == text_type(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + '/>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + disable_others_data + '</label>')
                    else:
                        inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + extra_radio + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '/>', helptext, status))
                    id_index += 1
            else:
                for pair in [dict(key='False', label=status.question.yes()), dict(key='True', label=status.question.no()), dict(key='None', label=status.question.maybe())]:
                    formatted_item = markdown_to_html(text_type(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    helptext = pair.get('help', None)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)) and text_type(pair['key']) == text_type(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '/>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    else:
                        inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + extra_radio + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + text_type(pair['key']) + '"' + ischecked + disable_others_data + '/>', helptext, status))
                    id_index += 1
            if embedded:
                output += " ".join(inner_fieldlist) + '</span>'
            else:
                output += "".join(inner_fieldlist) + '</fieldset>'
        elif field.datatype in ['file', 'files', 'camera', 'user', 'environment', 'camcorder', 'microphone']:
            if field.datatype == 'files':
                multipleflag = ' multiple'
            else:
                multipleflag = ''
            if field.datatype == 'camera':
                accept = ' accept="image/*"'
                capture = ' capture="camera"'
            elif field.datatype == 'user':
                accept = ' accept="image/*" capture="user"'
                capture = ' capture="environment"'
            elif field.datatype == 'environment':
                accept = ' accept="image/*"'
                capture = ' capture="environment"'
            elif field.datatype == 'camcorder':
                accept = ' accept="video/*"'
                capture = '  capture="camcorder"'
            elif field.datatype == 'microphone':
                accept = ' accept="audio/*"'
                capture = ' capture="microphone"'
            else:
                accept = ''
                capture = ''
            if 'accept' in status.extras and field.number in status.extras['accept']:
                accept = ' accept="' + status.extras['accept'][field.number] + '"'
            maximagesize = ''
            if 'max_image_size' in status.extras:
                if status.extras['max_image_size']:
                    maximagesize = 'data-maximagesize="' + str(int(status.extras['max_image_size'])) + '" '
            elif status.question.interview.max_image_size:
                maximagesize = 'data-maximagesize="' + str(int(status.question.interview.max_image_size)) + '" '
            imagetype = ''
            if 'image_type' in status.extras:
                if status.extras['image_type']:
                    imagetype = 'data-imagetype="' + str(status.extras['image_type']) + '" '
            elif status.question.interview.image_type:
                imagetype = 'data-imagetype="' + str(status.question.interview.image_type) + '" '
            if embedded:
                output += '<span class="da-inline-error-wrapper"><input alt="' + word("You can upload a file here") + '" type="file" class="dafile-embedded" name="' + escape_id(saveas_string) + '"' + title_text + ' id="' + escape_id(saveas_string) + '"' + multipleflag + accept + disable_others_data + '/></span>'
            else:
                output += '<input aria-describedby="' + escape_id(saveas_string) + '-error" alt=' + json.dumps(word("You can upload a file here")) + ' type="file" tabindex="-1" class="dafile" data-show-upload="false" ' + maximagesize + imagetype + ' data-preview-file-type="text" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + accept + disable_others_data + '/><label style="display: none;" for="' + escape_id(saveas_string) + '" class="da-has-error text-danger" id="' + escape_id(saveas_string) + '-error"></label>'
            #output += '<div class="fileinput fileinput-new input-group" data-provides="fileinput"><div class="form-control" data-trigger="fileinput"><i class="fas fa-file fileinput-exists"></i><span class="fileinput-filename"></span></div><span class="input-group-addon btn btn-secondary btn-file"><span class="fileinput-new">' + word('Select file') + '</span><span class="fileinput-exists">' + word('Change') + '</span><input type="file" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + '></span><a href="#" class="input-group-addon btn btn-secondary fileinput-exists" data-dismiss="fileinput">' + word('Remove') + '</a></div>\n'
        elif field.datatype == 'range':
            ok = True
            for key in ['min', 'max']:
                if not (hasattr(field, 'extras') and key in field.extras and key in status.extras and field.number in status.extras[key]):
                    ok = False
            if ok:
                if defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)):
                    the_default = ' data-slider-value="' + str(defaultvalue) + '"'
                else:
                    the_default = ' data-slider-value="' + str(int((float(status.extras['max'][field.number]) + float(status.extras['min'][field.number]))/2)) + '"'
                if 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step']:
                    the_step = ' data-slider-step="' + str(status.extras['step'][field.number]) + '"'
                else:
                    the_step = ''
                if 'scale' in field.extras and 'scale' in status.extras and field.number in status.extras['scale']:
                    the_step = ' data-slider-scale="' + str(status.extras['scale'][field.number]) + '"'
                else:
                    the_step = ''
                max_string = str(float(status.extras['max'][field.number]))
                min_string = str(float(status.extras['min'][field.number]))
                if embedded:
                    output += '<span class="form-group daslider-embedded"' + title_text + '><input alt="' + word('Select a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + the_default + ' data-slider-max="' + max_string + '" data-slider-min="' + min_string + '"' + the_step + disable_others_data + ' data-slider-id="' + escape_id(saveas_string) + '_slider"></span><br>'
                else:
                    output += '<input alt="' + word('Select a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + the_default + ' data-slider-max="' + max_string + '" data-slider-min="' + min_string + '"' + the_step + disable_others_data + ' data-slider-id="' + escape_id(saveas_string) + '_slider">'
                status.extra_scripts.append('<script>$("#' + escape_for_jquery(saveas_string) + '").slider({tooltip: "always"});</script>\n')
        elif field.datatype in ['area', 'mlarea']:
            if embedded:
                output += '<span class="da-embed-area-wrapper">'
            if 'rows' in status.extras and field.number in status.extras['rows']:
                rows = noquote(text_type(status.extras['rows'][field.number]))
            else:
                rows = '"4"'
            output += '<textarea alt=' + json.dumps(word("Input box")) + ' class="form-control' + extra_class + '"' + title_text + ' rows=' + rows + ' name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + placeholdertext + disable_others_data + '>'
            if defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)):
                output += defaultvalue
            output += '</textarea>'
            if embedded:
                output += '</span>'
        else:
            if defaultvalue is not None and isinstance(defaultvalue, (string_types, int, bool, float)):
                defaultstring = ' value="' + defaultvalue + '"'
            elif isinstance(defaultvalue, datetime.datetime):
                defaultstring = ' value="' + format_date(defaultvalue, format='yyyy-MM-dd') + '"'
            else:
                defaultstring = ''
            input_type = field.datatype
            if field.datatype == 'datetime':
                input_type = 'datetime-local'
            step_string = ''
            if field.datatype in ['integer', 'float', 'currency', 'number']:
                input_type = 'number'
                if hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step']:
                    step_string = ' step="' + text_type(status.extras['step'][field.number]) + '"'
                else:
                    if field.datatype == 'integer':
                        step_string = ' step="1"'
                    if field.datatype == 'float' or field.datatype == 'number':
                        step_string = ''
                    if field.datatype == 'currency':
                        step_string = ' step="0.01"'
                if field.datatype == 'currency':
                    extra_class += ' dacurrency'
                    if embedded:
                        output += '<span class="da-embed-currency-wrapper"><span class="da-embed-currency-symbol">' + currency_symbol() + '</span>'
                    else:
                        output += '<div class="input-group mb-2"><div class="input-group-prepend" id="addon-' + do_escape_id(saveas_string) + '"><div class="input-group-text">' + currency_symbol() + '</div></div>'
            if field.datatype == 'ml':
                input_type = 'text'
            if embedded:
                output += '<span class="da-inline-error-wrapper">'
            output += '<input' + defaultstring + placeholdertext + ' alt="' + word("Input box") + '" class="form-control' + extra_class + '"' + extra_style + title_text + ' type="' + input_type + '"' + step_string + ' name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"'
            if not embedded and field.datatype == 'currency':
                output += ' aria-describedby="addon-' + do_escape_id(saveas_string) + '"' + disable_others_data + '/></div><label style="display: none;" for="' + escape_id(saveas_string) + '" class="da-has-error text-danger" id="' + escape_id(saveas_string) + '-error"></label>'
            else:
                output += '/>'
            if embedded:
                if field.datatype == 'currency':
                    output += '</span></span>'
                else:
                    output += '</span>'
    return output

def get_ischecked(pair, defaultvalue):
    return ischecked
                
def myb64doublequote(text):
    return '"' + codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '') + '"'

def myb64quote(text):
    return "'" + codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '') + "'"

def indent_by(text, num):
    if not text:
        return ""
    return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"

def safeid(text):
    return codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '')

def from_safeid(text):
    return(codecs.decode(bytearray(text, encoding='utf-8'), 'base64').decode('utf8'))

def escape_id(text):
    return str(text)
    #return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)

def do_escape_id(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\1', text)

def escape_for_jquery(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)

def myb64unquote(the_string):
    return(codecs.decode(bytearray(the_string, encoding='utf-8'), 'base64').decode('utf8'))

def strip_quote(the_string):
    return re.sub(r'"', r'', the_string)

def safe_html(the_string):
    the_string = re.sub(r'\&', '&amp;', the_string)
    the_string = re.sub(r'\<', '&lt;', the_string)
    the_string = re.sub(r'\>', '&gt;', the_string)
    return the_string
