from docassemble.base.functions import word, currency_symbol, url_action, comma_and_list, server
from docassemble.base.filter import markdown_to_html, get_audio_urls, get_video_urls, audio_control, video_control, noquote, to_text, my_escape
from docassemble.base.parse import Question, debug
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig
import urllib
import sys
import os
import re
import json
import random
import sys
import codecs

DECORATION_SIZE = daconfig.get('decoration size', 2.0)
DECORATION_UNITS = daconfig.get('decoration units', 'em')
BUTTON_ICON_SIZE = daconfig.get('button icon size', 4.0)
BUTTON_ICON_UNITS = daconfig.get('button icon units', 'em')
if daconfig.get('button size', 'large') == 'large':
    BUTTON_CLASS = 'btn-lg btn-da'
else:
    BUTTON_CLASS = 'btn-da'

def tracker_tag(status):
    output = ''
    output += '                <input type="hidden" name="csrf_token" value="' + server.generate_csrf() + '"/>\n'
    if len(status.next_action):
        output += '                <input type="hidden" name="_next_action" value=' + myb64doublequote(json.dumps(status.next_action)) + '/>\n'
    if status.question.name:
        output += '                <input type="hidden" name="_question_name" value="' + status.question.name + '"/>\n'
    # if 'orig_action' in status.current_info:
    #     output += '                <input type="hidden" name="_action_context" value=' + myb64doublequote(json.dumps(dict(action=status.current_info['orig_action'], arguments=status.current_info['orig_arguments']))) + '/>\n'
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
    logmessage("icon_html: name is " + repr(name))
    if type(name) is dict and name['type'] == 'decoration':
        name = name['value']
    if type(name) is not dict:
        is_decoration = True
        the_image = status.question.interview.images.get(name, None)
        if the_image is None:
            if daconfig.get('default icons', None) == 'font awesome':
                return('<i class="' + daconfig.get('font awesome prefix', 'fas') + ' fa-' + str(name) + '"></i>')
            elif daconfig.get('default icons', None) == 'material icons':
                return('<i class="material-icons">' + str(name) + '</i>')
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
    return('<img class="daicon" src="' + url + '" style="' + str(sizing) + '"/>')

# def signature_html(status, debug, root, validation_rules):
#     if (status.continueLabel):
#         continue_label = markdown_to_html(status.continueLabel, trim=True)
#     else:
#         continue_label = word('Done')
#     output = '    <div class="sigpage" id="sigpage">\n      <div class="sigshowsmallblock sigheader" id="sigheader">\n        <div class="siginnerheader">\n          <a id="new" class="signavbtn signav-left">' + word('Clear') + '</a>\n          <a id="save" class="signavbtn signav-right">' + continue_label + '</a>\n          <div class="sigtitle">'
#     if status.questionText:
#         output += markdown_to_html(status.questionText, trim=True)
#     else:
#         output += word('Sign Your Name')
#     output += '</div>\n        </div>\n      </div>\n      <div class="sigtoppart" id="sigtoppart">\n        <div id="errormess" class="sigerrormessage signotshowing">' + word("You must sign your name to continue.") + '</div>\n        '
#     output += '\n      </div>'
#     if status.subquestionText:
#         output += '\n      <div class="sigmidpart">\n        ' + markdown_to_html(status.subquestionText) + '\n      </div>'
#     output += '\n      <div id="sigcontent"><p style="text-align:center;border-style:solid;border-width:1px">' + word('Loading.  Please wait . . . ') + '</p></div>\n      <div class="sigbottompart" id="sigbottompart">\n        '
#     if (status.underText):
#         output += markdown_to_html(status.underText, trim=True)
#     output += "\n      </div>"
#     output += """
#       <div class="form-actions sighidesmall sigbuttons">
#         <a id="savetwo" class="btn btn-primary btn-lg">""" + continue_label + """</a>
#         <a id="savetwo" class="btn btn-warning btn-lg">""" + word('Clear') + """</a>
#       </div>
# """
#     output += '    </div>\n    <form action="' + root + '" id="dasigform" method="POST"><input type="hidden" name="_save_as" value="' + escape_id(status.question.fields[0].saveas) + '"/><input type="hidden" id="_the_image" name="_the_image" value=""/><input type="hidden" id="_success" name="_success" value="0"/>'
#     output += tracker_tag(status)
#     output += '</form>\n'
#     add_validation(status.extra_scripts, validation_rules)
#     return output

def get_choices_with_abb(status, field, terms=None, links=None):
    if terms is None:
        terms = dict()
    if links is None:
        links = list()
    choice_list = status.get_choices(field)
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

def as_sms(status, links=None, menu_items=None):
    if links is None:
        links = list()
    if menu_items is None:
        menu_items = list()    
    terms = dict()
    #logmessage("length of links is " + str(len(links)))
    links_len = 0
    menu_items_len = 0
    next_variable = None
    qoutput = ''
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
                if the_field.datatype in ['note']:
                    info_message = to_text(markdown_to_html(status.extras['note'][the_field.number], status=status), terms, links, status)
                    continue
                if the_field.datatype in ['html']:
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
            data, choice_list = get_choices_with_abb(status, field, terms=terms, links=links)
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
            if status.underText:
                qoutput += "\n__________________________\n" + to_text(markdown_to_html(status.underText, trim=False, status=status, strip_newlines=True), terms, links, status)
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
    if status.underText and question.question_type != 'signature':
        qoutput += "\n" + to_text(markdown_to_html(status.underText, status=status), terms, links, status)
    if 'menu_items' in status.extras and type(status.extras['menu_items']) is list:
        for menu_item in status.extras['menu_items']:
            if type(menu_item) is dict and 'url' in menu_item and 'label' in menu_item:
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
        houtput = ''
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
            for term, definition in terms.iteritems():
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
        return '<div class="choicewithhelp"><div><div>' + content + '</div><div class="choicehelp"><a data-container="body" data-toggle="popover" data-placement="left" data-content=' + noquote(markdown_to_html(helptext, trim=True, status=status, do_terms=False)) + '><i class="glyphicon glyphicon-question-sign"></i></a></div></div></div>'

def as_html(status, url_for, debug, root, validation_rules, field_error, the_progress_bar, steps):
    decorations = list()
    uses_audio_video = False
    audio_text = ''
    video_text = ''
    datatypes = dict()
    varnames = dict()
    onchange = list()
    autocomplete_id = False
    if status.question.interview.use_navigation:
        grid_class = "col-lg-6 col-md-9 col-sm-9"
    else:
        grid_class = "col-lg-offset-3 col-lg-6 col-md-offset-2 col-md-8 col-sm-offset-1 col-sm-10"
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
    if status.question.interview.question_back_button and status.question.can_go_back and steps > 1:
        back_button = '\n                  <button class="btn btn-default ' + BUTTON_CLASS + ' " id="questionbackbutton" title="' + word("Go back to the previous question") + '"><i class="glyphicon glyphicon-chevron-left dalarge"></i>' + status.question.back() + '</button>'
    else:
        back_button = ''
    if status.question.interview.question_help_button and len(status.helpText) and status.question.helptext is not None:
        if status.helpText[0]['label']:
            help_label = markdown_to_html(status.helpText[0]['label'], trim=True, do_terms=False, status=status)
        else:
            help_label = status.question.help()
        help_button = '\n                  <button class="btn btn-default ' + BUTTON_CLASS + ' " id="questionhelpbutton">' + help_label + '</button>'
    else:
        help_button = ''
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
                        decorations.append('<img class="daiconfloat" style="' + sizing + '" src="' + url + '"/>')
                elif daconfig.get('default icons', None) == 'font awesome':
                    decorations.append('<span style="font-size: ' + str(DECORATION_SIZE) + str(DECORATION_UNITS) + '" class="dadecoration"><i class="' + daconfig.get('font awesome prefix', 'fas') + ' fa-' + str(decoration['image']) + '"></i></span>')
                elif daconfig.get('default icons', None) == 'material icons':
                    decorations.append('<span style="font-size: ' + str(DECORATION_SIZE) + str(DECORATION_UNITS) + '" class="dadecoration"><i class="material-icons">' + str(decoration['image']) + '</i></span>')
    if len(decorations):
        decoration_text = decorations[0];
    else:
        decoration_text = ''
    master_output = ""
    master_output += '          <section role="tabpanel" id="question" class="tab-pane active ' + grid_class + '">\n'
    output = ""
    if the_progress_bar:
        if status.question.question_type == "signature":
            the_progress_bar = re.sub(r'class="row"', 'class="hidden-xs"', the_progress_bar)
        output += the_progress_bar
    if status.question.question_type == "signature":
        output += '            <div class="sigpage" id="sigpage">\n              <div class="sigshowsmallblock sigheader" id="sigheader">\n                <div class="siginnerheader">\n                  <a class="btn btn-sm btn-warning signav-left signavbutton sigclear">' + word('Clear') + '</a>\n                  <a class="btn btn-sm btn-primary signav-right signavbutton sigsave">' + continue_label + '</a>\n                  <div class="sigtitle">'
        if status.questionText:
            output += markdown_to_html(status.questionText, trim=True, status=status)
        else:
            output += word('Sign Your Name')
        output += '</div>\n                </div>\n              </div>\n              <div class="sigtoppart" id="sigtoppart">\n                <div id="errormess" class="sigerrormessage signotshowing">' + word("You must sign your name to continue.") + '</div>\n'
        if status.questionText:
            output += '                <div class="sighidesmall">' + markdown_to_html(status.questionText, trim=True, status=status) + '</div>\n'
        output += '              </div>'
        if status.subquestionText:
            output += '\n              <div class="sigmidpart">\n                ' + markdown_to_html(status.subquestionText, status=status) + '\n              </div>'
        else:
            output += '\n              <div class="sigmidpart"></div>'
        output += '\n              <div id="sigcontent"><p style="text-align:center;border-style:solid;border-width:1px">' + word('Loading.  Please wait . . . ') + '</p></div>\n              <div class="sigbottompart" id="sigbottompart">\n                '
        if (status.underText):
            output += markdown_to_html(status.underText, trim=True, status=status)
        output += "\n              </div>"
        output += """
              <div class="form-actions sighidesmall sigbuttons">
                <a class="btn btn-primary """ + BUTTON_CLASS + """ sigsave">""" + continue_label + """</a>
                <a class="btn btn-warning """ + BUTTON_CLASS + """ sigclear">""" + word('Clear') + """</a>
              </div>
"""
        output += '            </div>\n            <form action="' + root + '" id="dasigform" method="POST"><input type="hidden" name="_save_as" value="' + escape_id(status.question.fields[0].saveas) + '"/><input type="hidden" id="_the_image" name="_the_image" value=""/><input type="hidden" id="_success" name="_success" value="0"/>'
        output += tracker_tag(status)
        output += '            </form>\n'
        output += '            <div class="sigshowsmallblock"><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br></div>'
    elif status.question.question_type in ["yesno", "yesnomaybe"]:
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
        output += '                <div class="btn-toolbar">' + back_button + '\n                  <button class="btn btn-primary ' + BUTTON_CLASS + ' " name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True">' + status.question.yes() + '</button>\n                  <button class="btn ' + BUTTON_CLASS + ' btn-info" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False">' + status.question.no() + '</button>'
        if status.question.question_type == 'yesnomaybe':
            output += '\n                  <button class="btn ' + BUTTON_CLASS + ' btn-warning" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None">' + markdown_to_html(status.question.maybe(), trim=True, do_terms=False, status=status) + '</button>'
        output += help_button
        output += '\n                </div>\n'
        #output += question_name_tag(status.question)
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type in ["noyes", "noyesmaybe"]:
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
        output += '                <div class="btn-toolbar">' + back_button + '\n                  <button class="btn btn-primary ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False">' + status.question.yes() + '</button>\n                  <button class="btn ' + BUTTON_CLASS + ' btn-info" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True">' + status.question.no() + '</button>'
        if status.question.question_type == 'noyesmaybe':
            output += '\n                  <button class="btn ' + BUTTON_CLASS + ' btn-warning" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None">' + status.question.maybe() + '</button>'
        output += help_button
        output += '\n                </div>\n'
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == "review":
        fieldlist = list()
        for field in status.get_field_list():
            if not status.extras['ok'][field.number]:
                continue
            if hasattr(field, 'extras'):
                if 'script' in field.extras and 'script' in status.extras and field.number in status.extras['script']:
                    status.extra_scripts.append(status.extras['script'][field.number])
                # if 'css' in field.extras and 'css' in status.extras and field.number in status.extras['css']:
                #     status.extra_css.append(status.extras['css'][field.number])
            if hasattr(field, 'datatype'):
                if field.datatype == 'html' and 'html' in status.extras and field.number in status.extras['html']:
                    fieldlist.append('                <div class="form-group' + req_tag +'"><div class="col-md-12"><note>' + status.extras['html'][field.number].rstrip() + '</note></div></div>\n')
                    continue
                elif field.datatype == 'note' and 'note' in status.extras and field.number in status.extras['note']:
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status, strip_newlines=True) + '</div></div>\n')
                    continue
                # elif field.datatype in ['script', 'css']:
                #     continue
                elif field.datatype == 'button' and hasattr(field, 'label') and field.number in status.helptexts:
                    fieldlist.append('                <div class="row"><div class="col-md-12"><a class="label label-success review-action review-action-button" data-action="' + str(field.action) + '">' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a>' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div></div>\n')
                    continue
            if hasattr(field, 'label'):
                fieldlist.append('                <div class="form-group"><div class="col-md-12"><a class="review-action" data-action="' + str(field.action) + '">' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a></div></div>\n')
                if field.number in status.helptexts:
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div></div>\n')
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" class="form-horizontal" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if (len(fieldlist)):
            output += "".join(fieldlist)
        if status.continueLabel:
            resume_button_label = markdown_to_html(status.continueLabel, trim=True, do_terms=False, status=status)
        else:
            resume_button_label = word('Resume')
        output += status.submit
        output += '                <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
        output += '                <div class="form-actions"><div class="btn-toolbar">' + back_button + '<button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit">' + resume_button_label + '</button>' + help_button + '</div></div>\n'
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
        output += tracker_tag(status)
        output += '              </fieldset>\n            </form>\n'
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
        field_list = status.get_field_list()
        saveas_to_use = dict()
        for field in field_list:
            if hasattr(field, 'address_autocomplete') and field.address_autocomplete and hasattr(field, 'saveas'):
                autocomplete_id = field.saveas
            if hasattr(field, 'datatype') and field.datatype == 'note':
                note_fields[field.number] = '                <div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status, embedder=embed_input) + '</div></div>\n'
            if hasattr(field, 'saveas'):
                varnames[safeid('_field_' + str(field.number))] = field.saveas
                if (hasattr(field, 'extras') and 'show_if_var' in field.extras and 'show_if_val' in status.extras) or (hasattr(field, 'disableothers') and field.disableothers):
                    the_saveas = safeid('_field_' + str(field.number))
                else:
                    the_saveas = field.saveas
                saveas_to_use[field.saveas] = the_saveas
                if the_saveas not in validation_rules['rules']:
                    validation_rules['rules'][the_saveas] = dict()
                if the_saveas not in validation_rules['messages']:
                    validation_rules['messages'][the_saveas] = dict()
        for field in field_list:
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
                req_tag = ' required'
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
                        fieldlist.append('                <div class="showif" data-saveas="' + escape_id(field.saveas) + '" data-showif-sign="' + escape_id(field.extras['show_if_sign']) + '" data-showif-var="' + escape_id(field.extras['show_if_var']) + '" data-showif-val=' + noquote(unicode(status.extras['show_if_val'][field.number])) + '>\n')
                    else:
                        fieldlist.append('                <div class="showif" data-showif-sign="' + escape_id(field.extras['show_if_sign']) + '" data-showif-var="' + escape_id(field.extras['show_if_var']) + '" data-showif-val=' + noquote(unicode(status.extras['show_if_val'][field.number])) + '>\n')
            if hasattr(field, 'datatype'):
                if field.datatype == 'html':
                    fieldlist.append('                <div class="form-group' + req_tag +'"><div class="col-md-12"><note>' + status.extras['html'][field.number].rstrip() + '</note></div></div>\n')
                    #continue
                elif field.datatype == 'note':
                    fieldlist.append(note_fields[field.number])
                    #fieldlist.append('                <div class="row"><div class="col-md-12">' + markdown_to_html(status.extras['note'][field.number], status=status, strip_newlines=True) + '</div></div>\n')
                    #continue
                # elif field.datatype in ['script', 'css']:
                #     continue
                else:
                    if hasattr(field, 'choicetype'):
                        vals = set([unicode(x['key']) for x in status.selectcompute[field.number]])
                        if len(vals) == 1 and ('True' in vals or 'False' in vals):
                            datatypes[field.saveas] = 'yesno'
                        elif len(vals) == 1 and 'None' in vals:
                            datatypes[field.saveas] = 'yesnomaybe'
                        elif len(vals) == 2 and ('True' in vals and 'False' in vals):
                            datatypes[field.saveas] = 'yesno'
                        elif len(vals) == 2 and (('True' in vals and 'None' in vals) or ('False' in vals and 'None' in vals)):
                            datatypes[field.saveas] = 'yesnomaybe'
                        elif len(vals) == 3 and ('True' in vals and 'False' in vals and 'None' in vals):
                            datatypes[field.saveas] = 'yesnomaybe'
                        else:
                            datatypes[field.saveas] = field.datatype
                    else:
                        datatypes[field.saveas] = field.datatype
                    if field.datatype == 'object_checkboxes':
                        datatypes[safeid(from_safeid(field.saveas) + ".gathered")] = 'boolean'
            if field.number in status.helptexts:
                helptext_start = '<a class="daterm" data-container="body" data-toggle="popover" data-placement="bottom" data-content=' + noquote(status.helptexts[field.number]) + '>' 
                helptext_end = '</a>'
            else:
                helptext_start = ''
                helptext_end = ''
            if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                onchange.append(safeid('_field_' + str(field.number)))
            if hasattr(field, 'saveas'):
                varnames[safeid('_field_' + str(field.number))] = field.saveas
                the_saveas = saveas_to_use[field.saveas]
                if (hasattr(field, 'extras') and 'show_if_var' in field.extras and 'show_if_val' in status.extras) or (hasattr(field, 'disableothers') and field.disableothers):
                    label_saveas = the_saveas
                else:
                    label_saveas = field.saveas                        
                if not (hasattr(field, 'datatype') and field.datatype in ['checkboxes', 'object_checkboxes']):
                #     validation_rules['messages'][the_saveas] = dict()
                #     validation_rules['rules'][the_saveas] = dict()
                # else:
                    validation_rules['messages'][the_saveas]['required'] = word("This field is required.")
                    if status.extras['required'][field.number]:
                        #sys.stderr.write(field.datatype + "\n")
                        validation_rules['rules'][the_saveas]['required'] = True
                    else:
                        validation_rules['rules'][the_saveas]['required'] = False
                if hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes', 'yesnowide', 'noyeswide'] and hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                    if field.uncheckothers is True:
                        the_query = '.uncheckable:checked, .uncheckothers:checked'
                        uncheck_list = [saveas_to_use[y.saveas] for y in field_list if y is not field and hasattr(y, 'saveas') and hasattr(y, 'inputtype') and y.inputtype in ['yesno', 'noyes', 'yesnowide', 'noyeswide']]
                    else:
                        uncheck_list = [saveas_to_use[safeid(y)] for y in field.uncheckothers if safeid(y) in saveas_to_use]
                        the_query = ', '.join(['#' + do_escape_id(x) + ':checked' for x in uncheck_list + [the_saveas]])
                        the_js = """\
<script>
  $( document ).ready(function() {
    $(""" + '"' + ', '.join(['#' + escape_for_jquery(x) for x in uncheck_list]) + '"' + """).on("change", function(){
      if ($(this).is(":checked")){
        $('#""" + escape_for_jquery(the_saveas) + """').prop("checked", false);
      }
    });
    $('#""" + escape_for_jquery(the_saveas) + """').on("change", function(){
      if ($(this).is(":checked")){
        $(""" + '"' + ', '.join(['#' + escape_for_jquery(x) for x in uncheck_list]) + '"' + """).prop("checked", false);
      }
    });
  });
</script>
"""
                        status.extra_scripts.append(the_js)
                    for y in uncheck_list + [the_saveas]:
                        validation_rules['rules'][y]['checkone'] = [1, the_query]
                        validation_rules['messages'][y]['checkone'] = word("Check at least one option, or check") + " " + '"' + status.labels[field.number] + '"'
                    if 'groups' not in validation_rules:
                        validation_rules['groups'] = dict()
                    validation_rules['groups'][the_saveas + '_group'] = ' '.join(uncheck_list + [the_saveas])
                    validation_rules['ignore'] = None
                    
                for key in ('minlength', 'maxlength'):
                    if hasattr(field, 'extras') and key in field.extras and key in status.extras:
                        #sys.stderr.write("Adding validation rule for " + str(key) + "\n")
                        validation_rules['rules'][the_saveas][key] = int(status.extras[key][field.number])
                        if key == 'minlength':
                            validation_rules['messages'][the_saveas][key] = word("You must type at least") + " " + str(status.extras[key][field.number]) + " " + word("characters")
                        elif key == 'maxlength':
                            validation_rules['messages'][the_saveas][key] = word("You cannot type more than") + " " + str(status.extras[key][field.number]) + " " + word("characters")
            if hasattr(field, 'datatype'):
                if field.datatype in ('checkboxes', 'object_checkboxes') and hasattr(field, 'nota') and status.extras['nota'][field.number] is not False:
                    validation_rules['rules']['_ignore' + str(field.number)] = dict(checkbox=[str(field.number)])
                    #validation_rules['messages']['_ignore' + str(field.number)] = dict(checkbox=word("Please select one."))
                    validation_rules['ignore'] = None
                # if field.datatype in ('checkboxes', 'object_checkboxes') and hasattr(field, 'nota') and status.extras['nota'][field.number] is not False:
                #     #validation_rules['rules'][the_saveas]['checkboxgroup'] = dict(name=the_saveas, foobar=2)
                #     #validation_rules['messages'][the_saveas]['checkboxgroup'] = word("You need to select one.")
                #     if 'groups' not in validation_rules:
                #         validation_rules['groups'] = dict()
                #     if field.choicetype in ['compute', 'manual']:
                #         pairlist = list(status.selectcompute[field.number])
                #     else:
                #         raise Exception("Unknown choicetype " + field.choicetype)
                #     name_list = [safeid(from_safeid(the_saveas) + "[" + myb64quote(pairlist[indexno]['key']) + "]") for indexno in range(len(pairlist))]
                #     for the_name in name_list:
                #         validation_rules['rules'][the_name] = dict(require_from_group=[1, '.dafield' + str(field.number)])
                #         validation_rules['messages'][the_name] = dict(require_from_group=word("Please select one."))
                #     validation_rules['rules']['_ignore' + str(field.number)] = dict(require_from_group=[1, '.dafield' + str(field.number)])
                #     validation_rules['messages']['_ignore' + str(field.number)] = dict(require_from_group=word("Please select one."))
                #     validation_rules['groups'][the_saveas] = " ".join(name_list + ['_ignore' + str(field.number)])
                #     validation_rules['ignore'] = None
                if hasattr(field, 'inputtype') and field.inputtype in ['yesnoradio', 'noyesradio']:
                    validation_rules['ignore'] = None
                if field.datatype in ['radio', 'object_radio']:
                    validation_rules['ignore'] = None
                if field.datatype == 'date':
                    validation_rules['rules'][the_saveas]['date'] = True
                    validation_rules['messages'][the_saveas]['date'] = word("You need to enter a valid date.")
                if field.datatype == 'time':
                    validation_rules['rules'][the_saveas]['time'] = True
                    validation_rules['messages'][the_saveas]['time'] = word("You need to enter a valid time.")
                if field.datatype == 'datetime':
                    validation_rules['rules'][the_saveas]['datetime'] = True
                    validation_rules['messages'][the_saveas]['datetime'] = word("You need to enter a valid date and time.")
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
                            validation_rules['rules'][the_saveas][key] = float(status.extras[key][field.number])
                            if key == 'min':
                                validation_rules['messages'][the_saveas][key] = word("You need to enter a number that is at least") + " " + str(status.extras[key][field.number])
                            elif key == 'max':
                                validation_rules['messages'][the_saveas][key] = word("You need to enter a number that is at most") + " " + str(status.extras[key][field.number])
                if (field.datatype in ['files', 'file', 'camera', 'user', 'environment', 'camcorder', 'microphone']):
                    enctype_string = ' enctype="multipart/form-data"'
                    files.append(field.saveas)
                    validation_rules['messages'][field.saveas]['required'] = word("You must provide a file.")
                if field.datatype == 'combobox':
                    validation_rules['ignore'] = list()
                if field.datatype in ['boolean', 'threestate']:
                    if field.sign > 0:
                        checkboxes[field.saveas] = 'False'
                    else:
                        checkboxes[field.saveas] = 'True'
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
            if hasattr(field, 'saveas') and field.saveas in status.embedded:
                continue
            if hasattr(field, 'label'):
                if status.labels[field.number] == 'no label':
                    fieldlist.append('                <div class="form-group' + req_tag + '"><div class="col-md-12">' + input_for(status, field, wide=True) + '</div></div>\n')
                elif hasattr(field, 'inputtype') and field.inputtype in ['yesnowide', 'noyeswide']:
                    fieldlist.append('                <div class="row"><div class="col-md-12">' + input_for(status, field) + '</div></div>\n')
                elif hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes']:
                    fieldlist.append('                <div class="form-group yesnospacing' + req_tag +'"><div class="col-sm-offset-4 col-sm-8">' + input_for(status, field) + '</div></div>\n')
                else:
                    fieldlist.append('                <div class="form-group' + req_tag + '"><label for="' + escape_id(label_saveas) + '" class="control-label col-sm-4">' + helptext_start + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + helptext_end + '</label><div class="col-sm-8 fieldpart">' + input_for(status, field) + '</div></div>\n')
            if hasattr(field, 'extras') and 'show_if_var' in field.extras and 'show_if_val' in status.extras:
                fieldlist.append('                </div>\n')
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" class="form-horizontal" method="POST"' + enctype_string + '>\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + sub_question_text 
            #for saveas_string in status.embedded:
            #    output += '<label style="display: none;" for="' + escape_id(saveas_string) + '" class="da-has-error" id="' + escape_id(saveas_string) + '-error"></label> '
            output += '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if (len(fieldlist)):
            output += "".join(fieldlist)
        #else:
        #    output += "                <p>Error: no fields</p>\n"
        #output += '</div>\n'
        if len(checkboxes):
            output += '                <input type="hidden" name="_checkboxes" value=' + myb64doublequote(json.dumps(checkboxes)) + '/>\n'
        if len(hiddens):
            output += '                <input type="hidden" name="_empties" value=' + myb64doublequote(json.dumps(hiddens)) + '/>\n'
        if len(ml_info):
            output += '                <input type="hidden" name="_ml_info" value=' + myb64doublequote(json.dumps(ml_info)) + '/>\n'
        if len(files):
            output += '                <input type="hidden" name="_files" value=' + myb64doublequote(json.dumps(files)) + '/>\n'
            #init_string = '<script>'
            #for saveasname in files:
            #    init_string += '$("#' + escape_for_jquery(saveasname) + '").fileinput();' + "\n"
            #init_string += '</script>'
            #status.extra_scripts.append('<script src="' + url_for('static', filename='bootstrap-fileinput/js/fileinput.min.js') + '"></script>' + init_string)
            #status.extra_scripts.append(init_string)
            #status.extra_css.append('<link href="' + url_for('static', filename='bootstrap-fileinput/css/fileinput.min.css') + '" media="all" rel="stylesheet" type="text/css" />')
        output += status.submit
        output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '                <div class="form-actions"><div class="btn-toolbar">' + back_button + '<button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit">' + continue_label + '</button>' + help_button + '</div></div>\n'
        #output += question_name_tag(status.question)
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == "settrue":
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = "boolean"
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '                <div class="form-actions"><div class="btn-toolbar">' + back_button + '<button type="submit" class="btn ' + BUTTON_CLASS + ' btn-primary" name="' + escape_id(status.question.fields[0].saveas) + '" value="True">' + continue_label + '</button>' + help_button + '</div></div>\n'
        #output += question_name_tag(status.question)
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == "multiple_choice":
        #varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        if status.question.fields[0].number in status.defaults and type(status.defaults[status.question.fields[0].number]) in [str, unicode, int, float]:
            defaultvalue = unicode(status.defaults[status.question.fields[0].number])
            #logmessage("Default value is " + str(defaultvalue))
        else:
            defaultvalue = None
        if hasattr(status.question.fields[0], 'datatype'):
            datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += '                <p class="sr-only">' + word('Your choices are:') + '</p>\n'
        validation_rules['errorElement'] = "span"
        validation_rules['errorLabelContainer'] = "#errorcontainer"
        if status.question.question_variety in ["radio", "dropdown", "combobox"]:
            if status.question.question_variety == "radio":
                verb = 'check'
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
                    formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=True, do_terms=False)
                    if defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == unicode(defaultvalue):
                        ischecked = ' ' + verb + 'ed="' + verb + 'ed"'
                    if status.question.question_variety == "radio":
                        if True or pair['key'] is not None: #not sure why this was added
                            output += '                <div class="row"><div class="col-md-12">' + help_wrap('<input alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="to-labelauty radio-icon" id="' + escape_id(status.question.fields[0].saveas) + '_' + str(id_index) + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>', helptext, status) + '</div></div>\n'
                        else:
                            output += '                <div class="form-group"><div class="col-md-12">' + help_wrap(markdown_to_html(pair['label'], status=status), helptext, status) + '</div></div>\n'
                    else:
                        if True or pair['key'] is not None:
                            inner_fieldlist.append('<option value="' + unicode(pair['key']) + '"' + ischecked + '>' + formatted_item + '</option>')

                    id_index += 1
                if status.question.question_variety in ["dropdown", "combobox"]:
                    if status.question.question_variety == 'combobox':
                        combobox = ' combobox'
                        daspaceafter = ' daspaceafter'
                    else:
                        combobox = ''
                        daspaceafter = ''
                    output += '                <div class="row"><div class="col-md-12' + daspaceafter + '"><select class="form-control daspaceafter' + combobox + '" name="' + escape_id(status.question.fields[0].saveas) + '" id="' + escape_id(status.question.fields[0].saveas) + '">' + "".join(inner_fieldlist) + '</select></div></div>\n'
                if status.question.question_variety == 'combobox':
                    validation_rules['ignore'] = list()
                else:
                    validation_rules['ignore'] = None
                validation_rules['rules'][status.question.fields[0].saveas] = {'required': True}
                validation_rules['messages'][status.question.fields[0].saveas] = {'required': word("You need to select one.")}
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
                        output += '                <div class="row"><div class="col-md-12">' + help_wrap('<input alt="' + formatted_key + '" data-labelauty="' + my_escape(the_icon) + formatted_key + '|' + my_escape(the_icon) + formatted_key + '" class="to-labelauty radio-icon" id="multiple_choice_' + str(indexno) + '_' + str(id_index) + '" name="X211bHRpcGxlX2Nob2ljZQ==" type="radio" value="' + str(indexno) + '"' + ischecked + '/>', helptext, status) + '</div></div>\n'
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
                else:
                    validation_rules['ignore'] = None
                validation_rules['rules']['X211bHRpcGxlX2Nob2ljZQ=='] = {'required': True}
                validation_rules['messages']['X211bHRpcGxlX2Nob2ljZQ=='] = {'required': word("You need to select one.")}
            output += '                <div id="errorcontainer" style="display:none"></div>\n'
            output += status.submit
            output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
            output += '                <div class="btn-toolbar">' + back_button + '\n'
            output += '                  <button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit">' + continue_label + '</button>\n'
            output += '                </div>\n'
        else:
            output += status.submit
            #output += '                <p class="sr-only">' + word('Press one of the following buttons:') + '</p>\n'
            output += '                <div class="btn-toolbar">' + back_button + '\n'
            if hasattr(status.question.fields[0], 'saveas'):
                btn_class = ' btn-primary'
                if hasattr(status.question.fields[0], 'has_code') and status.question.fields[0].has_code:
                    pairlist = list(status.selectcompute[status.question.fields[0].number])
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if 'image' in pair:
                            the_icon = '<div>' + icon_html(status, pair['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</div>';
                            btn_class = ' btn-default btn-da-custom'
                        else:
                            the_icon = ''
                        if True or pair['key'] is not None:
                            output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value="' + unicode(pair['key']) + '">' + the_icon + markdown_to_html(pair['label'], status=status, trim=True, do_terms=False) + '</button>\n'
                        else:
                            output += markdown_to_html(pair['label'], status=status)
                else:
                    choicelist = status.selectcompute[status.question.fields[0].number]
                    #choicelist = list(status.question.fields[0].choices)
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(choicelist)
                    for choice in choicelist:
                        if 'image' in choice:
                            the_icon = '<div>' + icon_html(status, choice['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</div>';
                            btn_class = ' btn-default btn-da-custom'
                        else:
                            the_icon = ''
                        if 'help' in choice:
                            the_help = choice['help']
                        else:
                            the_help = ''
                        output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value="' + unicode(choice['key']) + '">' + the_icon + markdown_to_html(choice['label'], status=status, trim=True, do_terms=False) + '</button>\n'
            else:
                indexno = 0
                for choice in status.selectcompute[status.question.fields[0].number]:
                #for choice in status.question.fields[0].choices:
                    btn_class = ' btn-primary'
                    if 'image' in choice:
                        the_icon = '<div>' + icon_html(status, choice['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</div>'
                        btn_class = ' btn-default btn-da-custom'
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
                    output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + '" name="X211bHRpcGxlX2Nob2ljZQ==" value="' + str(indexno) + '">' + the_icon + markdown_to_html(choice['label'], status=status, trim=True, do_terms=False, strip_newlines=True) + '</button>\n'
                    indexno += 1
            output += help_button
            output += '                </div>\n'
        #output += question_name_tag(status.question)
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '              </fieldset>\n            </form>\n'
    elif status.question.question_type == 'deadend':
        output += status.pre
        output += indent_by(audio_text, 12) + '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if back_button != '' or help_button != '':
            output += status.submit
            output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
            output += '                <div class="form-actions"><div class="btn-toolbar">' + back_button + help_button + '</div></div>\n'
    else:
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form action="' + root + '" id="daform" class="form-horizontal" method="POST">\n              <fieldset>\n'
        output += '                <div class="page-header"><h3>' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '<div class="daclear"></div></h3></div>\n'
        if status.subquestionText:
            output += '                <div>\n' + markdown_to_html(status.subquestionText, status=status, indent=18) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <p class="sr-only">' + word('You can press the following button:') + '</p>\n'
        output += '                <div class="form-actions"><div class="btn-toolbar">' + back_button + '<button class="btn ' + BUTTON_CLASS + ' btn-primary" type="submit">' + continue_label + '</button>' + help_button + '</div></div>\n'
        #output += question_name_tag(status.question)
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
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
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['pdf'], display_filename=attachment['filename'] + '.pdf') + '" target="_blank"><i class="glyphicon glyphicon-print"></i> PDF</a> (' + word('pdf_message') + ')</p>\n'
                if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['rtf'], display_filename=attachment['filename'] + '.rtf') + '" target="_blank"><i class="glyphicon glyphicon-pencil"></i> RTF</a> (' + word('rtf_message') + ')</p>\n'
                if 'docx' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['docx'], display_filename=attachment['filename'] + '.docx') + '" target="_blank"><i class="glyphicon glyphicon-pencil"></i> DOCX</a> (' + word('docx_message') + ')</p>\n'
                if 'rtf to docx' in attachment['valid_formats']:
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['rtf to docx'], display_filename=attachment['filename'] + '.docx') + '" target="_blank"><i class="glyphicon glyphicon-pencil"></i> DOCX</a> (' + word('docx_message') + ')</p>\n'
                if debug and ('tex' in attachment['valid_formats']):
                    output += '                  <p><a href="' + server.url_finder(attachment['file']['tex'], display_filename=attachment['filename'] + '.tex') + '" target="_blank"><i class="glyphicon glyphicon-pencil"></i> LaTeX</a> (' + word('tex_message') + ')</p>\n'
                output += '                </div>\n'
            if show_preview:
                output += '                <div class="tab-pane" id="preview' + str(attachment_index) + '">\n'
                output += '                  <blockquote>' + unicode(attachment['content']['html']) + '</blockquote>\n'
                output += '                </div>\n'
            if show_markdown:
                output += '                <div class="tab-pane" id="markdown' + str(attachment_index) + '">\n'
                output += '                  <pre>' + safe_html(attachment['markdown'][md_format]) + '</pre>\n'
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
                        <div class="form-actions"><button class="btn btn-primary" type="submit">""" + word('Send') + '</button></div><input type="hidden" name="_email_attachments" value="1"/>'#<input type="hidden" name="_question_number" value="' + str(status.question.number) + '"/>'
            output += """
                      </fieldset>
                      <input type="hidden" name="csrf_token" value=""" + '"' + server.generate_csrf() + '"' + """/>
                    </form>
                  </div>
                </div>
              </div>
            </div>
"""
#            status.extra_scripts.append("""<script>
#      $("#emailform").validate({'submitHandler': daValidationHandler, 'rules': {'_attachment_email_address': {'minlength': 1, 'required': true, 'email': true}}, 'messages': {'_attachment_email_address': {'required': """ + repr(str(word("An e-mail address is required."))) + """, 'email': """ + repr(str(word("You need to enter a complete e-mail address."))) + """}}, 'errorClass': 'da-has-error'});
#    </script>""")
        if (status.underText):
            output += markdown_to_html(status.underText, status=status, indent=18, divclass="undertext")
    if status.question.question_type != "signature":
        output += status.post
        if len(status.attributions):
            output += '            <br/><br/><br/><br/><br/><br/><br/>\n'
        for attribution in sorted(status.attributions):
            output += '            <div><attribution><small>' + markdown_to_html(attribution, status=status, strip_newlines=True) + '</small></attribution></div>\n'
    if debug or status.using_screen_reader:
        status.screen_reader_text['question'] = unicode(output)
    master_output += output
    master_output += '          </section>\n'
    master_output += '          <section role="tabpanel" id="help" class="tab-pane ' + grid_class + '">\n'
    output = '<div><a id="backToQuestion" data-toggle="tab" data-target="#question" href="#question" class="btn btn-info btn-md"><i class="glyphicon glyphicon-arrow-left"></i> ' + word("Back to question") + '</a></div>'
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
            elif len(status.helpText) > 1:
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
            output += '            <div><attribution><small>' + markdown_to_html(attribution, status=status, strip_newlines=True) + '</small></attribution></div>\n'
        if debug or status.using_screen_reader:
            status.screen_reader_text['help'] = unicode(output)
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
        status.extra_scripts.append(the_script)
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
        status.extra_scripts.append(track_js)
    if autocomplete_id:
        status.extra_scripts.append("""
<script>
  initAutocomplete(""" + repr(str(autocomplete_id)) + """);
</script>
""")
    if len(status.maps):
        map_js = """\
    <script>
      map_info = [""" + ", ".join(status.maps) + """];
    </script>
"""
        status.extra_scripts.append(map_js)
        google_config = daconfig.get('google', dict())
        if 'google maps api key' in google_config:
            api_key = google_config.get('google maps api key')
        elif 'api key' in google_config:
            api_key = google_config.get('api key')
        else:
            raise Exception('google API key not provided')
        status.extra_scripts.append('<script async defer src="https://maps.googleapis.com/maps/api/js?key=' + urllib.quote(api_key) + '&callback=daInitMap"></script>')
    return master_output

def add_validation(extra_scripts, validation_rules, field_error):
    if field_error is None:
        error_show = ''
    else:
        error_mess = dict()
        for key, val in field_error.iteritems():
            error_mess[key] = val
        error_show = "\n  validator.showErrors(" + json.dumps(error_mess) + ");"
    extra_scripts.append("""<script>
  var validation_rules = """ + json.dumps(validation_rules) + """;
  $.validator.setDefaults({
    highlight: function(element) {
        $(element).closest('.form-group').addClass('has-error');
    },
    unhighlight: function(element) {
        $(element).closest('.form-group').removeClass('has-error');
    },
    errorElement: 'span',
    errorClass: 'help-block',
    errorPlacement: function(error, element) {
        var elementName = $(element).attr("name");
        var lastInGroup = $.map(validation_rules['groups'], function(thefields, thename){
          var fieldsArr;
          if (thefields.indexOf(elementName) >= 0) {
            fieldsArr = thefields.split(" ");
            return fieldsArr[fieldsArr.length - 1];
          }
          else {
            return null;
          }
        })[0];
        if (element.hasClass('input-embedded')){
          error.insertAfter(element);
        }
        else if (element.hasClass('file-embedded')){
          error.insertAfter(element);
        }
        else if (element.hasClass('radio-embedded')){
          element.parent().append(error);
        }
        else if (element.hasClass('checkbox-embedded')){
          element.parent().append(error);
        }
        else if (element.hasClass('uncheckable') && lastInGroup){
          $("input[name='" + lastInGroup + "']").parent().append(error);
        }
        else if (element.parent().hasClass('combobox-container')){
          error.insertAfter(element.parent());
        }
        else if (element.hasClass('dafile')){
          var fileContainer = $(element).parents(".file-input").first();
          if (fileContainer.length > 0){
            $(fileContainer).append(error);
          }
          else{
            error.insertAfter(element.parent());
          }
        }
        else if (element.parent('.input-group').length) {
          error.insertAfter(element.parent());
        }
        else if (element.hasClass('labelauty')){
          var choice_with_help = $(element).parents(".choicewithhelp").first();
          if (choice_with_help.length > 0){
            $(choice_with_help).parent().append(error);
          }
          else{
            element.parent().append(error);
          }
        }
        else if (element.hasClass('non-nota-checkbox')){
          element.parent().append(error);
        }
        else {
          error.insertAfter(element);
        }
    }
  });
  $.validator.addMethod('checkone', function(value, element, params){
    var number_needed = params[0];
    var css_query = params[1];
    if ($(css_query).length >= number_needed){
      return true;
    }
    else{
      return false;
    }
  }, """ + json.dumps(word("Please check at least one.")) + """);
  $.validator.addMethod('checkbox', function(value, element, params){
    if ($(element).attr('name') != '_ignore' + params[0]){
      return true;
    }
    if ($('.dafield' + params[0] + ':checked').length > 0){
      return true;
    }
    else{
      return false;
    }
  }, """ + json.dumps(word("Please select one.")) + """);
  validation_rules.submitHandler = daValidationHandler;
  if ($("#daform").length > 0){
    //console.log("Running validator")
    var validator = $("#daform").validate(validation_rules);""" + error_show + """
  }
</script>""")

def input_for(status, field, wide=False, embedded=False):
    output = ""
    if field.number in status.defaults:
        defaultvalue_set = True
        if type(status.defaults[field.number]) in [str, unicode, int, float]:
            defaultvalue = unicode(status.defaults[field.number])
        else:
            defaultvalue = status.defaults[field.number]
    else:
        defaultvalue_set = False
        defaultvalue = None
    if field.number in status.hints:
        placeholdertext = ' placeholder=' + json.dumps(unicode(status.hints[field.number].replace('\n', ' ')))
    else:
        placeholdertext = ''
    if (hasattr(field, 'extras') and 'show_if_var' in field.extras and 'show_if_val' in status.extras and hasattr(field, 'saveas')) or (hasattr(field, 'disableothers') and field.disableothers):
        saveas_string = safeid('_field_' + str(field.number))
    else:
        saveas_string = field.saveas
    if 'inline width' in status.extras and field.number in status.extras['inline width']:
        inline_width = status.extras['inline width'][field.number]
    else:
        inline_width = None
    if embedded:
        extra_class = ' input-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'date':
            extra_class += ' date-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'time':
            extra_class += ' time-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'datetime':
            extra_class += ' date-embedded'
        if inline_width is not None:
            extra_style = ' style="min-width: ' + unicode(inline_width) + '"'
        else:
            extra_style = ''
        extra_checkbox = ' checkbox-embedded'
        extra_radio = 'radio-embedded'
        if field.number in status.labels:
            label_text = strip_quote(to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), dict(), list(), status).strip())
        else:
            label_text = 'no label'
        if label_text != 'no label':
            title_text = ' title="' + label_text + '"'
        else:
            title_text = ''
    else:
        extra_style = ''
        extra_class = ''
        extra_checkbox = ''
        extra_radio = ''
        title_text = ''
    if hasattr(field, 'choicetype'):
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
                output += '<span class="embed-checkbox-wrapper">'
            else:
                output += '<p class="sr-only">' + word('Checkboxes:') + '</p>'
            for pair in pairlist:
                if 'image' in pair:
                    the_icon = icon_html(status, pair['image']) + ' '
                else:
                    the_icon = ''
                helptext = pair.get('help', None)
                if True or pair['key'] is not None:
                    inner_field = safeid(from_safeid(saveas_string) + "[" + myb64quote(pair['key']) + "]")
                    #sys.stderr.write("I've got a " + repr(pair['label']) + "\n")
                    formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if 'default' in pair and pair['default']:
                        ischecked = ' checked'
                    elif defaultvalue is None:
                        ischecked = ''
                    elif type(defaultvalue) in (list, set) and unicode(pair['key']) in defaultvalue:
                        ischecked = ' checked'
                    elif type(defaultvalue) is dict and unicode(pair['key']) in defaultvalue and defaultvalue[unicode(pair['key'])]:
                        ischecked = ' checked'
                    elif (hasattr(defaultvalue, 'elements') and type(defaultvalue.elements) is dict) and unicode(pair['key']) in defaultvalue.elements and defaultvalue.elements[unicode(pair['key'])]:
                        ischecked = ' checked'
                    elif pair['key'] is defaultvalue:
                        ischecked = ' checked'
                    elif type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == unicode(defaultvalue):
                        ischecked = ' checked'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input class="checkbox-embedded dafield' + str(field.number) + ' non-nota-checkbox" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"' + ischecked + '/>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    else:
                        inner_fieldlist.append(help_wrap('<input alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="' + 'dafield' + str(field.number) + ' non-nota-checkbox to-labelauty checkbox-icon' + extra_checkbox + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"' + ischecked + '/>', helptext, status))
                else:
                    inner_fieldlist.append(help_wrap('<div>' + markdown_to_html(pair['label'], status=status) + '</div>', helptext, status))
                id_index += 1
            if hasattr(field, 'nota') and 'nota' in status.extras and status.extras['nota'][field.number] is not False:
                if defaultvalue_set and defaultvalue is None:
                    ischecked = ' checked'
                else:
                    ischecked = ''
                if status.extras['nota'][field.number] is True:
                    formatted_item = word("None of the above")
                else:
                    formatted_item = markdown_to_html(unicode(status.extras['nota'][field.number]), status=status, trim=True, escape=(not embedded), do_terms=False)
                if embedded:
                    inner_fieldlist.append('<input class="dafield' + str(field.number) + ' checkbox-embedded nota-checkbox" id="_ignore' + str(field.number) + '" type="checkbox" name="_ignore' + str(field.number) + '"/>&nbsp;<label for="_ignore' + str(field.number) + '">' + formatted_item + '</label>')
                else:
                    inner_fieldlist.append('<input alt="' + formatted_item + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="' + 'dafield' + str(field.number) + ' nota-checkbox to-labelauty checkbox-icon' + extra_checkbox + '"' + title_text + ' type="checkbox" name="_ignore' + str(field.number) + '" ' + ischecked + '/>')
            if embedded:
                output += u' '.join(inner_fieldlist) + '</span>'
            else:
                output += u''.join(inner_fieldlist)
            if field.datatype in ['object_checkboxes']:                
                output += '<input type="hidden" name="' + safeid(from_safeid(saveas_string) + ".gathered") + '" value="True"/>'
        elif field.datatype in ['radio', 'object_radio']:
            inner_fieldlist = list()
            id_index = 0
            try:
                defaultvalue_printable = unicode(defaultvalue)
                defaultvalue_is_printable = True
            except:
                defaultvalue_printable = None
                defaultvalue_is_printable = False
            if embedded:
                for pair in pairlist:
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and type(defaultvalue) not in [str, unicode, int, bool, float] and defaultvalue_printable and unicode(pair['label']) == defaultvalue_printable):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    inner_fieldlist.append('<input class="radio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    id_index += 1
                output += '<span class="embed-radio-wrapper">'
                output += " ".join(inner_fieldlist)
                output += '</span>'
            else:
                output += '<p class="sr-only">' + word('Choices:') + '</p>'
                for pair in pairlist:
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    helptext = pair.get('help', None)
                    if True or pair['key'] is not None:
                        #sys.stderr.write(str(saveas_string) + "\n")
                        formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and type(defaultvalue) not in [str, unicode, int, bool, float] and defaultvalue_is_printable and unicode(pair['label']) == defaultvalue_printable):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        inner_fieldlist.append(help_wrap('<input alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="to-labelauty radio-icon' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>', helptext, status))
                    else:
                        inner_fieldlist.append(help_wrap('<div>' + the_icon + markdown_to_html(unicode(pair['label']), status=status) + '</div>', helptext, status))
                    id_index += 1
                if embedded:
                    output += '<span class="embed-radio-wrapper">' + " ".join(inner_fieldlist) + '</span>'
                else:
                    output += "".join(inner_fieldlist)
        else:
            if embedded:
                emb_text = 'class="input-embedded" '
                if inline_width is not None:
                    emb_text += 'style="min-width: ' + unicode(inline_width) + '" '
                label_text = strip_quote(to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), dict(), list(), status).strip())
                if label_text != 'no label':
                    emb_text += 'title="' + label_text + '" '
            else:
                output += '<p class="sr-only">' + word('Select box') + '</p>'
                if hasattr(field, 'datatype') and field.datatype == 'combobox':
                    emb_text = 'class="form-control combobox" '
                else:
                    emb_text = 'class="form-control" '
            if embedded:
                output += '<span class="inline-error-wrapper">'
            output += '<select ' + emb_text + 'name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '" >'
            if hasattr(field, 'datatype') and field.datatype == 'combobox' and not embedded:
                if placeholdertext == '':
                    output += '<option value="">' + word('Select one') + '</option>'
                else:
                    output += '<option value="">' + unicode(status.hints[field.number].replace('\n', ' ')) + '</option>'
            else:
                if placeholdertext == '':
                    output += '<option value="">' + word('Select...') + '</option>'
                else:
                    output += '<option value="">' + unicode(status.hints[field.number].replace('\n', ' ')) + '</option>'
            try:
                defaultvalue_printable = unicode(defaultvalue)
                defaultvalue_is_printable = True
            except:
                defaultvalue_printable = None
                defaultvalue_is_printable = False
            for pair in pairlist:
                if True or pair['key'] is not None:
                    formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, do_terms=False)
                    output += '<option value="' + unicode(pair['key']) + '"'
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and type(defaultvalue) not in [str, unicode, int, bool, float] and defaultvalue_is_printable and unicode(pair['label']) == defaultvalue_printable):
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
                    output += '<span class="embed-radio-wrapper">'
                else:
                    output += '<p class="sr-only">' + word('Choices:') + '</p>'
                if field.sign > 0:
                    for pair in [dict(key='True', label=status.question.yes()), dict(key='False', label=status.question.no())]:
                        formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if 'image' in pair:
                            the_icon = icon_html(status, pair['image']) + ' '
                        else:
                            the_icon = ''
                        helptext = pair.get('help', None)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == unicode(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        if embedded:
                            inner_fieldlist.append('<input class="radio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                        else:
                            inner_fieldlist.append(help_wrap('<input alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="to-labelauty radio-icon' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>', helptext, status))
                        id_index += 1
                else:
                    for pair in [dict(key='False', label=status.question.yes()), dict(key='True', label=status.question.no())]:
                        formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if 'image' in pair:
                            the_icon = icon_html(status, pair['image']) + ' '
                        else:
                            the_icon = ''
                        helptext = pair.get('help', None)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == unicode(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        if embedded:
                            inner_fieldlist.append('<input class="radio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                        else:
                            inner_fieldlist.append(help_wrap('<input alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="to-labelauty radio-icon' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>', helptext, status))
                        id_index += 1
                if embedded:
                    output += " ".join(inner_fieldlist) + '</span>'
                else:
                    output += "".join(inner_fieldlist)
            else:
                if hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                    if type(field.uncheckothers) is list:
                        uncheck = ''
                    else:
                        uncheck = ' uncheckothers'
                else:
                    uncheck = ' uncheckable'
                if defaultvalue in ('False', 'false', 'FALSE', 'no', 'No', 'NO', 'Off', 'off', 'OFF', 'Null', 'null', 'NULL'):
                    defaultvalue = False
                if (defaultvalue and field.sign > 0) or (defaultvalue is False and field.sign < 0):
                    docheck = ' checked'
                else:
                    docheck = ''
                if embedded:
                    output += '<span class="embed-yesno-wrapper">'
                if field.sign > 0:
                    if embedded:
                        output += '<input class="checkbox-embedded' + uncheck + '" type="checkbox" value="True" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + '/>&nbsp;<label for="' + escape_id(saveas_string) + '">' + label_text + '</label>'
                    else:
                        output += '<input alt="' + label_text + '" class="to-labelauty checkbox-icon' + extra_checkbox + uncheck + '"' + title_text + ' type="checkbox" value="True" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + '/> '
                else:
                    if embedded:
                        output += '<input class="checkbox-embedded' + uncheck + '" type="checkbox" value="False" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + '/>&nbsp;<label for="' + escape_id(saveas_string) + '">' + label_text + '</label>'
                    else:
                        output += '<input alt="' + label_text + '" class="to-labelauty checkbox-icon' + extra_checkbox + uncheck + '"' + title_text + ' type="checkbox" value="False" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + '/> '
                if embedded:
                    output += '</span>'
        elif field.datatype == 'threestate':
            inner_fieldlist = list()
            id_index = 0
            if embedded:
                output += '<span class="embed-threestate-wrapper">'
            else:
                output += '<p class="sr-only">' + word('Choices:') + '</p>'
            if field.sign > 0:
                for pair in [dict(key='True', label=status.question.yes()), dict(key='False', label=status.question.no()), dict(key='None', label=status.question.maybe())]:
                    formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    helptext = pair.get('help', None)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == unicode(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input class="radio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    else:
                        inner_fieldlist.append(help_wrap('<input alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="to-labelauty radio-icon' + extra_radio + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>', helptext, status))
                    id_index += 1
            else:
                for pair in [dict(key='False', label=status.question.yes()), dict(key='True', label=status.question.no()), dict(key='None', label=status.question.maybe())]:
                    formatted_item = markdown_to_html(unicode(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    helptext = pair.get('help', None)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float] and unicode(pair['key']) == unicode(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input class="radio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>&nbsp;<label for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    else:
                        inner_fieldlist.append(help_wrap('<input alt="' + formatted_item + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="to-labelauty radio-icon' + extra_radio + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="' + unicode(pair['key']) + '"' + ischecked + '/>', helptext, status))
                    id_index += 1
            if embedded:
                output += " ".join(inner_fieldlist) + '</span>'
            else:
                output += "".join(inner_fieldlist)
        elif field.datatype in ['file', 'files', 'camera', 'user', 'environment', 'camcorder', 'microphone']:
            if field.datatype == 'files':
                multipleflag = ' multiple'
            else:
                multipleflag = ''
            if field.datatype == 'camera':
                accept = ' accept="image/*" capture="camera"'
            elif field.datatype == 'user':
                accept = ' accept="image/*" capture="user"'
            elif field.datatype == 'environment':
                accept = ' accept="image/*" capture="environment"'
            elif field.datatype == 'camcorder':
                accept = ' accept="video/*" capture="camcorder"'
            elif field.datatype == 'microphone':
                accept = ' accept="audio/*" capture="microphone"'
            else:
                accept = ''
            maximagesize = ''
            if 'max_image_size' in status.extras:
                if status.extras['max_image_size']:
                    maximagesize = 'data-maximagesize="' + str(int(status.extras['max_image_size'])) + '" '
            elif status.question.interview.max_image_size:
                maximagesize = 'data-maximagesize="' + str(int(status.question.interview.max_image_size)) + '" '
            if embedded:
                output += '<span class="inline-error-wrapper"><input alt="' + word("You can upload a file here") + '" type="file" class="file-embedded" name="' + escape_id(saveas_string) + '"' + title_text + ' id="' + escape_id(saveas_string) + '"' + multipleflag + accept + '/></span>'
            else:
                output += '<input alt="' + word("You can upload a file here") + '" type="file" class="dafile" data-show-upload="false" ' + maximagesize + ' data-preview-file-type="text" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + accept + '/><label style="display: none;" for="' + escape_id(saveas_string) + '" class="da-has-error" id="' + escape_id(saveas_string) + '-error"></label>'
            #output += '<div class="fileinput fileinput-new input-group" data-provides="fileinput"><div class="form-control" data-trigger="fileinput"><i class="glyphicon glyphicon-file fileinput-exists"></i><span class="fileinput-filename"></span></div><span class="input-group-addon btn btn-default btn-file"><span class="fileinput-new">' + word('Select file') + '</span><span class="fileinput-exists">' + word('Change') + '</span><input type="file" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + '></span><a href="#" class="input-group-addon btn btn-default fileinput-exists" data-dismiss="fileinput">' + word('Remove') + '</a></div>\n'
        elif field.datatype == 'range':
            ok = True
            for key in ['min', 'max']:
                if not (hasattr(field, 'extras') and key in field.extras and key in status.extras and field.number in status.extras[key]):
                    ok = False
            if ok:
                if defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float]:
                    the_default = ' data-slider-value="' + str(defaultvalue) + '"'
                else:
                    the_default = ' data-slider-value="' + str(int((float(status.extras['max'][field.number]) + float(status.extras['min'][field.number]))/2)) + '"'
                if 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step']:
                    the_step = ' data-slider-step="' + str(status.extras['step'][field.number]) + '"'
                else:
                    the_step = ''
                max_string = str(float(status.extras['max'][field.number]))
                min_string = str(float(status.extras['min'][field.number]))
                if embedded:
                    output += '<span class="form-group slider-embedded"' + title_text + '><input alt="' + word('Select a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + the_default + ' data-slider-max="' + max_string + '" data-slider-min="' + min_string + '"' + the_step + '></span><br>'
                else:
                    output += '<input alt="' + word('Select a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + the_default + ' data-slider-max="' + max_string + '" data-slider-min="' + min_string + '"' + the_step + '>'
                status.extra_scripts.append('<script>$("#' + escape_for_jquery(saveas_string) + '").slider({tooltip: "always"});</script>\n')
        elif field.datatype in ['area', 'mlarea']:
            if embedded:
                output += '<span class="embed-area-wrapper">'
            output += '<textarea alt="' + word("Input box") + '" class="form-control' + extra_class + '"' + title_text + ' rows="4" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + placeholdertext + '>'
            if defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float]:
                output += defaultvalue
            output += '</textarea>'
            if embedded:
                output += '</span>'
        else:
            if defaultvalue is not None and type(defaultvalue) in [str, unicode, int, bool, float]:
                defaultstring = ' value="' + defaultvalue + '"'
            else:
                defaultstring = ''
            input_type = field.datatype
            if field.datatype == 'datetime':
                input_type = 'datetime-local'
            step_string = ''
            if field.datatype in ['integer', 'float', 'currency', 'number']:
                input_type = 'number'
                if field.datatype == 'integer':
                    step_string = ' step="1"'
                if field.datatype == 'float' or field.datatype == 'number':
                    step_string = ' step="0.01"'
                if field.datatype == 'currency':
                    step_string = ' step="0.01"'
                    if embedded:
                        output += '<span class="embed-currency-wrapper"><span class="embed-currency-symbol">' + currency_symbol() + '</span>'
                    else:
                        output += '<div class="input-group"><span class="input-group-addon" id="addon-' + do_escape_id(saveas_string) + '">' + currency_symbol() + '</span>'
            if field.datatype == 'ml':
                input_type = 'text'
            if embedded:
                output += '<span class="inline-error-wrapper">'
                # output += '<span class="inline-error-wrapper"><label for="' + escape_id(saveas_string) + '" class="da-has-error inline-error-position inline-error" style="display: none" id="' + escape_id(saveas_string) + '-error"></label>'
            output += '<input' + defaultstring + placeholdertext + ' alt="' + word("Input box") + '" class="form-control' + extra_class + '"' + extra_style + title_text + ' type="' + input_type + '"' + step_string + ' name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"'
            if not embedded and field.datatype in ('currency', 'file', 'files', 'camera', 'user', 'environment', 'camcorder', 'microphone'):
                output += ' aria-describedby="addon-' + do_escape_id(saveas_string) + '"/></div><label style="display: none;" for="' + escape_id(saveas_string) + '" class="da-has-error" id="' + escape_id(saveas_string) + '-error"></label>'
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
    return(codecs.decode(text, 'base64').decode('utf8'))

def escape_id(text):
    return str(text)
    #return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)

def do_escape_id(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\1', text)

def escape_for_jquery(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)

def myb64unquote(the_string):
    return(codecs.decode(the_string, 'base64').decode('utf8'))

def strip_quote(the_string):
    return re.sub(r'"', r'', the_string)

def safe_html(the_string):
    the_string = re.sub(r'\&', '&amp;', the_string)
    the_string = re.sub(r'\<', '&lt;', the_string)
    the_string = re.sub(r'\>', '&gt;', the_string)
    return the_string
