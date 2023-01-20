# import sys
import re
import json
import random
import codecs
import datetime
import locale
from io import StringIO
from html.parser import HTMLParser
from docassemble.base.functions import word, get_currency_symbol, comma_and_list, server, custom_types, get_locale
from docassemble.base.util import format_date, format_datetime, format_time
# from docassemble.base.generate_key import random_string
from docassemble.base.filter import markdown_to_html, get_audio_urls, get_video_urls, audio_control, video_control, noquote, to_text, my_escape, process_target
from docassemble.base.parse import Question
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig
equals_byte = bytes('=', 'utf-8')

NoneType = type(None)
STRICT_MODE = daconfig.get('restrict input variables', False)
DECORATION_SIZE = daconfig.get('decoration size', 2.0)
DECORATION_UNITS = daconfig.get('decoration units', 'em')
BUTTON_ICON_SIZE = daconfig.get('button icon size', 4.0)
BUTTON_ICON_UNITS = daconfig.get('button icon units', 'em')
if daconfig.get('button size', 'medium') == 'medium':
    BUTTON_CLASS = 'btn-da'
elif daconfig['button size'] == 'large':
    BUTTON_CLASS = 'btn-lg btn-da'
elif daconfig['button size'] == 'small':
    BUTTON_CLASS = 'btn-sm btn-da'
else:
    BUTTON_CLASS = 'btn-da'

if daconfig.get('button style', 'normal') == 'normal':
    BUTTON_STYLE = 'btn-'
elif daconfig['button style'] == 'outline':
    BUTTON_STYLE = 'btn-outline-'
else:
    BUTTON_STYLE = 'btn-'

BUTTON_COLOR = daconfig['button colors'].get('continue', 'primary')
BUTTON_COLOR_YES = daconfig['button colors'].get('answer yes', 'primary')
BUTTON_COLOR_NO = daconfig['button colors'].get('answer no', 'secondary')
BUTTON_COLOR_MAYBE = daconfig['button colors'].get('answer maybe', 'warning')
BUTTON_COLOR_CLEAR = daconfig['button colors'].get('clear', 'warning')
BUTTON_COLOR_BACK = daconfig['button colors'].get('back', 'link')
BUTTON_COLOR_REGISTER = daconfig['button colors'].get('register', 'primary')
BUTTON_COLOR_NEW_SESSION = daconfig['button colors'].get('new session', 'primary')
BUTTON_COLOR_LEAVE = daconfig['button colors'].get('leave', 'warning')
BUTTON_COLOR_URL = daconfig['button colors'].get('url', 'link')
BUTTON_COLOR_RESTART = daconfig['button colors'].get('restart', 'warning')
BUTTON_COLOR_REFRESH = daconfig['button colors'].get('refresh', 'primary')
BUTTON_COLOR_SIGNIN = daconfig['button colors'].get('signin', 'info')
BUTTON_COLOR_EXIT = daconfig['button colors'].get('exit', 'danger')
BUTTON_COLOR_LOGOUT = daconfig['button colors'].get('logout', 'danger')
BUTTON_COLOR_SEND = daconfig['button colors'].get('send', 'primary')
BUTTON_COLOR_DOWNLOAD = daconfig['button colors'].get('download', 'primary')
BUTTON_COLOR_REVIEW = daconfig['button colors'].get('review', 'secondary')
BUTTON_COLOR_ADD = daconfig['button colors'].get('add', 'secondary')
BUTTON_COLOR_DELETE = daconfig['button colors'].get('delete', 'danger')
BUTTON_COLOR_UNDELETE = daconfig['button colors'].get('undelete', 'info')
BUTTON_COLOR_HELP = daconfig['button colors'].get('help', 'info')
BUTTON_COLOR_QUESTION_HELP = daconfig['button colors'].get('question help', 'info')
BUTTON_COLOR_BACK_TO_QUESTION = daconfig['button colors'].get('back to question', 'primary')
DEFAULT_LABELAUTY_COLOR = daconfig['button colors'].get('labelauty', 'primary')
DEFAULT_LABELAUTY_NOTA_COLOR = daconfig['button colors'].get('labelauty nota', DEFAULT_LABELAUTY_COLOR)


def process_help(help_section, status, full_page=True):
    output = ''
    if full_page:
        if help_section['heading'] is not None:
            output += '            <div class="da-page-header"><h1 class="h3">' + help_section['heading'].strip() + '</h1></div>\n'
        elif help_section['from'] == 'question':
            output += '            <div class="da-page-header"><h1 class="h3">' + word('Help with this question') + '</h1></div>\n'
    else:
        if help_section['heading'] is not None:
            output += '            <h2 class="h4">' + help_section['heading'].strip() + '</h2>\n'
    if help_section['audiovideo'] is not None:
        audio_urls = get_audio_urls(help_section['audiovideo'])
        if len(audio_urls) > 0:
            output += '            <div class="daaudiovideo-control">\n' + indent_by(audio_control(audio_urls), 14) + '            </div>\n'
        video_urls = get_video_urls(help_section['audiovideo'])
        if len(video_urls) > 0:
            output += '            <div class="daaudiovideo-control">\n' + indent_by(video_control(video_urls), 14) + '            </div>\n'
    output += markdown_to_html(help_section['content'], status=status)
    return output


def tracker_tag(status):
    output = str()
    output += '                <input type="hidden" name="csrf_token" value=' + json.dumps(server.generate_csrf()) + '/>\n'
    # restore this, maybe
    # if len(status.next_action):
    #    output += '                <input type="hidden" name="_next_action" value=' + myb64doublequote(json.dumps(status.next_action)) + '/>\n'
    if status.orig_sought is not None and not STRICT_MODE:
        output += '                <input type="hidden" name="_event" value=' + myb64doublequote(json.dumps([status.orig_sought])) + ' />\n'
    if status.question.name:
        output += '                <input type="hidden" name="_question_name" value=' + json.dumps(status.question.name, ensure_ascii=False) + '/>\n'
    # if 'orig_action' in status.current_info:
    #     output += '                <input type="hidden" name="_action_context" value=' + myb64doublequote(json.dumps(dict(action=status.current_info['orig_action'], arguments=status.current_info['orig_arguments']))) + '/>\n'
    output += '                <input type="hidden" name="_tracker" value=' + json.dumps(str(status.tracker)) + '/>\n'
    if 'track_location' in status.extras and status.extras['track_location']:
        output += '                <input type="hidden" id="da_track_location" name="_track_location" value=""/>\n'
    if hasattr(status.question, 'fields_saveas') and status.question.question_type != 'fields':
        output += '                <input type="hidden" name="' + escape_id(safeid(status.question.fields_saveas)) + '" value="True">\n'
    return output


def datatype_tag(datatypes):
    output = ''
    if len(datatypes) > 0 and not STRICT_MODE:
        output += '                <input type="hidden" name="_datatypes" value=' + myb64doublequote(json.dumps(datatypes)) + '/>\n'
    output += '                <input type="hidden" name="_visible" value=""/>\n'
    return output


def varname_tag(varnames):
    if len(varnames) > 0:
        return '                <input type="hidden" name="_varnames" value=' + myb64doublequote(json.dumps(varnames)) + '/>\n'
    return ''


def icon_html(status, name, width_value=1.0, width_units='em'):
    # logmessage("icon_html: name is " + repr(name))
    if isinstance(name, dict) and name['type'] == 'decoration':
        name = name['value']
    if not isinstance(name, dict):
        is_decoration = True
        the_image = status.question.interview.images.get(name, None)
        if the_image is None:
            if daconfig.get('default icons', None) == 'font awesome':
                return '<i class="' + daconfig.get('font awesome prefix', 'fas') + ' fa-' + str(name) + '"></i>'
            if daconfig.get('default icons', None) == 'material icons':
                return '<i class="da-material-icons">' + str(name) + '</i>'
            return ''
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
    return '<img alt="" class="daicon" src="' + url + '" style="' + str(sizing) + '"/>'

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
#     if 'underText' in status.extras:
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
        terms = {}
    if links is None:
        links = []
    choice_list = status.get_choices(field, the_user_dict)
    data = {}
    while True:
        success = True
        data['keys'] = []
        data['abb'] = {}
        data['abblower'] = {}
        data['label'] = []
        for choice in choice_list:
            flabel = to_text(markdown_to_html(choice[0], trim=False, status=status, strip_newlines=True), terms, links).strip()
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
        data['keys'] = []
    if 'abb' not in data:
        data['abb'] = {}
    if 'abblower' not in data:
        data['abblower'] = {}
    if 'label' not in data:
        data['label'] = []
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
            # data['size'] = 1
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
        links = []
    if menu_items is None:
        menu_items = []
    terms = {}
    # logmessage("length of links is " + str(len(links)))
    menu_items_len = 0
    next_variable = None
    qoutput = str()
    if status.question.question_type == 'signature':
        qoutput += word('Sign Your Name') + "\n"
    # logmessage("The question is " + status.questionText)
    qoutput += to_text(markdown_to_html(status.questionText, trim=False, status=status, strip_newlines=True), terms, links)
    if status.subquestionText:
        qoutput += "\n" + to_text(markdown_to_html(status.subquestionText, status=status), terms, links)
        # logmessage("output is: " + repr(qoutput))
    qoutput += "XXXXMESSAGE_AREAXXXX"
    if len(status.question.fields) > 0:
        field = None
        next_field = None
        info_message = None
        field_list = status.get_field_list()
        for the_field in field_list:
            if status.is_empty_mc(the_field):
                logmessage("as_sms: skipping field because choice list is empty.")
                continue
            if hasattr(the_field, 'datatype'):
                if the_field.datatype in ['script', 'css']:  # why did I ever comment this out?
                    continue
                if the_field.datatype in ['html', 'note'] and field is not None:
                    continue
                if the_field.datatype == 'note':
                    info_message = to_text(markdown_to_html(status.extras['note'][the_field.number], status=status), terms, links)
                    continue
                if the_field.datatype == 'html':
                    info_message = to_text(process_target(status.extras['html'][the_field.number].rstrip()), terms, links)
                    continue
            # logmessage("field number is " + str(the_field.number))
            if not hasattr(the_field, 'saveas'):
                logmessage("as_sms: field has no saveas")
                continue
            if the_field.number not in the_user_dict['_internal']['skip']:
                # logmessage("as_sms: field is not defined yet")
                if field is None:
                    field = the_field
                elif next_field is None:
                    next_field = the_field
                continue
            logmessage("as_sms: field " + str(the_field.number) + " skipped")
        if info_message is not None:
            qoutput += "\n" + info_message
        immediate_next_field = None
        if field is None:
            logmessage("as_sms: field seemed to be defined already?")
            field = status.question.fields[0]
            # return dict(question=qoutput, help=None, next=next_variable)
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
                    next_label = ' (' + word("Next will be") + ' ' + to_text(markdown_to_html(status.labels[immediate_next_field.number], trim=False, status=status, strip_newlines=True), terms, links) + ')'
                elif hasattr(immediate_next_field, 'datatype'):
                    if immediate_next_field.datatype in ['note']:
                        next_label = ' (' + word("Next will be") + ' ' + to_text(markdown_to_html(status.extras['note'][immediate_next_field.number], trim=False, status=status, strip_newlines=True), terms, links) + ')'
                    elif immediate_next_field.datatype in ['html']:
                        next_label = ' (' + word("Next will be") + ' ' + to_text(status.extras['html'][immediate_next_field.number].rstrip(), terms, links) + ')'
        if hasattr(field, 'label') and status.labels[field.number] != "no label":
            label = to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), terms, links)
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
        elif question.question_type == 'multiple_choice' or hasattr(field, 'choicetype') or (hasattr(field, 'datatype') and field.datatype in ['object', 'checkboxes', 'multiselect', 'object_checkboxes', 'object_multiselect']):
            if question.question_type == 'fields' and label:
                qoutput += "\n" + label + ":" + next_label
            data, choice_list = get_choices_with_abb(status, field, the_user_dict, terms=terms, links=links)
            qoutput += "\n" + word("Choices:")
            if hasattr(field, 'shuffle') and field.shuffle:
                random.shuffle(data['label'])
            for the_label in data['label']:
                qoutput += "\n" + the_label
            if hasattr(field, 'datatype') and field.datatype in ['multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes']:
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
                qoutput += "\n__________________________\n" + to_text(markdown_to_html(status.extras['underText'], trim=False, status=status, strip_newlines=True), terms, links)
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
        elif hasattr(field, 'datatype') and field.datatype in ['datetime', 'datetime-local']:
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
        qoutput += "\n" + to_text(markdown_to_html(status.extras['underText'], status=status), terms, links)
    if 'menu_items' in status.extras and isinstance(status.extras['menu_items'], list):
        for menu_item in status.extras['menu_items']:
            if isinstance(menu_item, dict) and 'url' in menu_item and 'label' in menu_item:
                menu_items.append((menu_item['url'], menu_item['label']))
    if len(links) > 0:
        indexno = 1
        qoutput_add = "\n" + "== " + word("Links") + " =="
        seen = {}
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
        links_orig = list(links)
        while len(links):
            links.pop()
        for (href, label) in links_orig:
            if re.search(r'action=', href):
                links.append((href, label))
    if len(status.helpText) > 0 or len(terms) > 0 or len(menu_items) > 0:
        houtput = str()
        for help_section in status.helpText:
            if houtput != '':
                houtput += "\n"
            if help_section['heading'] is not None:
                houtput += '== ' + to_text(markdown_to_html(help_section['heading'], trim=False, status=status, strip_newlines=True), terms, links) + ' =='
            elif len(status.helpText) > 1:
                houtput += '== ' + word('Help with this question') + ' =='
            houtput += "\n" + to_text(markdown_to_html(help_section['content'], trim=False, status=status, strip_newlines=True), terms, links)
        if len(terms) > 0:
            if houtput != '':
                houtput += "\n"
            houtput += "== " + word("Terms used:") + " =="
            for term, definition in terms.items():
                houtput += "\n" + term + ': ' + definition
        if len(menu_items) > 0:
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
        # houtput += "\n" + word("You can type question to read the question again.")
    else:
        houtput = None
    if status.question.helptext is not None:
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + word("Type ? for additional assistance.") + 'XXXXMESSAGE_AREAXXXX', qoutput)
    elif len(terms) > 0 or menu_items_len:
        items = []
        if len(terms) > 0:
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


def help_wrap(content, helptext, status):
    if helptext is None:
        return content
    help_wrapper = '<div class="dachoicewithhelp"><div><div>%s</div><div class="dachoicehelp text-' + (status.extras.get('help button color', None) or BUTTON_COLOR_HELP) + '"><a tabindex="0" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="left" data-bs-content=%s><i class="fas fa-question-circle"></i></a></div></div></div>'
    return help_wrapper % (content, noquote(markdown_to_html(helptext, trim=True, status=status, do_terms=False)))


def as_html(status, debug, root, validation_rules, field_error, the_progress_bar, steps):
    decorations = []
    audio_text = ''
    video_text = ''
    datatypes = {}
    varnames = {}
    onchange = []
    autocomplete_info = []
    validation_rules['ignore'] = None
    showUnderText = 'underText' in status.extras and len(status.attachments) == 0
    if status.using_navigation == 'vertical':
        grid_class = daconfig['grid classes']['vertical navigation']['body']
    else:
        if status.flush_left():
            grid_class = daconfig['grid classes']['flush left']['body']
        else:
            grid_class = daconfig['grid classes']['centered']['body']
    if status.question.interview.options.get('suppress autofill', False):
        autofill = ' autocomplete="off"'
    else:
        autofill = ''
    labels_above = status.question.interview.options.get('labels above', False)
    floating_labels = status.question.interview.options.get('floating labels', False)
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
    if hasattr(status.question, 'fields_saveas'):
        datatypes[safeid(status.question.fields_saveas)] = "boolean"
    continue_button_color = status.extras.get('continuecolor', None) or BUTTON_COLOR
    back_button_val = status.extras.get('back_button', None)
    if (back_button_val or (back_button_val is None and status.question.interview.question_back_button)) and status.question.can_go_back and steps > 1:
        back_button = '\n                  <button type="button" class="btn ' + BUTTON_STYLE + (status.extras.get('back button color', None) or BUTTON_COLOR_BACK) + ' ' + BUTTON_CLASS + ' daquestionbackbutton danonsubmit" title=' + json.dumps(word("Go back to the previous question")) + '><i class="fas fa-chevron-left"></i> '
        back_button += status.back
        back_button += '</button>'
    else:
        back_button = ''
    if status.question.interview.question_help_button and len(status.helpText):
        if status.helpText[0]['label']:
            help_label = markdown_to_html(status.helpText[0]['label'], trim=True, do_terms=False, status=status)
        else:
            help_label = status.question.help()
        help_button = '\n                  <button type="button" class="btn ' + BUTTON_STYLE + (status.extras.get('help button color', None) or BUTTON_COLOR_QUESTION_HELP) + ' ' + BUTTON_CLASS + '  danonsubmit" data-bs-toggle="collapse" data-bs-target="#daquestionhelp" aria-expanded="false" aria-controls="daquestionhelp">' + help_label + '</button>'
        if status.question.question_type == "signature":
            help_button_area = '<div class="d-none d-sm-block"><div class="collapse daquestionhelp" id="daquestionhelp">'
        else:
            help_button_area = '<div class="collapse daquestionhelp" id="daquestionhelp">'
        for help_section in status.helpText:
            help_button_area += process_help(help_section, status, full_page=False)
        if status.question.question_type == "signature":
            help_button_area += '</div></div>'
        else:
            help_button_area += '</div>'
    else:
        help_button = ''
        help_button_area = ''
    if 'action_buttons' in status.extras:
        additional_buttons_before = ''
        additional_buttons_after = ''
        for item in status.extras['action_buttons']:
            if item['icon'] is not None:
                icon = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', item['icon'])
                if not re.search(r'^fa[a-z] fa-', icon):
                    icon = 'fas fa-' + icon
                icon = '<i class="' + icon + '"></i> '
            else:
                icon = ''
            if item['css_class'] is not None:
                button_css_class = ' ' + item['css_class'].strip()
            else:
                button_css_class = ''
            action_search = re.search(r'[\?\&]action=([^\&]+)', item['action'])
            if action_search and ('/interview' in item['action'] or '/run' in item['action'] or '/start' in item['action'] or item['action'].startswith('?')):
                action_data = 'data-embaction="' + action_search.group(1) + '" '
            else:
                action_data = ''
            if item['target'] is not None and action_data == '':
                target_string = 'target=' + json.dumps(item['target']) + ' '
            else:
                target_string = ''
            js_search = re.search(r'^javascript:(.*)', item['action'])
            if js_search:
                js_data = 'data-js="' + js_search.group(1) + '" '
            else:
                js_data = ''
            status.linkcounter += 1
            button_html = '\n                  <a ' + target_string + 'data-linknum="' + str(status.linkcounter) + '" ' + action_data + js_data + 'href="' + item['action'] + '" class="btn ' + BUTTON_STYLE + item['color'] + ' ' + BUTTON_CLASS + ' daquestionactionbutton danonsubmit' + button_css_class + '">' + icon + markdown_to_html(item['label'], trim=True, do_terms=False, status=status) + '</a>'
            if item['placement'] == 'before':
                additional_buttons_before += button_html
            else:
                additional_buttons_after += button_html
    else:
        additional_buttons_before = ''
        additional_buttons_after = ''
    if status.audiovideo is not None:
        audio_urls = get_audio_urls(status.audiovideo)
        if len(audio_urls) > 0:
            audio_text += '<div class="daaudiovideo-control">\n' + audio_control(audio_urls) + '</div>\n'
        video_urls = get_video_urls(status.audiovideo)
        if len(video_urls) > 0:
            video_text += '<div class="daaudiovideo-control">\n' + video_control(video_urls) + '</div>\n'
    if status.using_screen_reader and 'question' in status.screen_reader_links:
        audio_text += '<div class="daaudiovideo-control">\n' + audio_control(status.screen_reader_links['question'], preload="none", title_text=word('Read this screen out loud')) + '</div>\n'
    if status.decorations is not None:
        for decoration in status.decorations:
            if 'image' in decoration:
                the_image = status.question.interview.images.get(decoration['image'], None)
                if the_image is not None:
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
                        if the_image.attribution is not None:
                            status.attributions.add(the_image.attribution)
                        decorations.append('<img alt="" class="daiconfloat" style="' + sizing + '" src="' + url + '"/>')
                elif daconfig.get('default icons', None) == 'font awesome':
                    decorations.append('<span style="font-size: ' + str(DECORATION_SIZE) + str(DECORATION_UNITS) + '" class="dadecoration"><i class="' + daconfig.get('font awesome prefix', 'fas') + ' fa-' + str(decoration['image']) + '"></i></span>')
                elif daconfig.get('default icons', None) == 'material icons':
                    decorations.append('<span style="font-size: ' + str(DECORATION_SIZE) + str(DECORATION_UNITS) + '" class="dadecoration"><i class="da-material-icons">' + str(decoration['image']) + '</i></span>')
    if len(decorations) > 0:
        decoration_text = decorations[0]
    else:
        decoration_text = ''
    master_output = str()
    master_output += '          <div id="daquestion" aria-labelledby="dapagetitle" role="main" class="tab-pane fade show active ' + grid_class + '">\n'
    output = str()
    if the_progress_bar:
        if status.question.question_type == "signature":
            the_progress_bar = re.sub(r'class="row"', 'class="d-none d-sm-block"', the_progress_bar)
        output += the_progress_bar
    if status.question.question_type == "signature":
        if status.question.interview.question_back_button and status.question.can_go_back and steps > 1:
            back_clear_button = '<button type="button" class="btn btn-sm ' + BUTTON_STYLE + (status.extras.get('back button color', None) or BUTTON_COLOR_BACK) + ' dasignav-left dasignavbutton daquestionbackbutton danonsubmit">' + status.question.back() + '</button>'
        else:
            back_clear_button = '<a href="#" role="button" class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_CLEAR + ' dasignav-left dasignavbutton dasigclear">' + word('Clear') + '</a>'
        output += '            <div class="dasigpage" id="dasigpage">\n              <div class="dasigshowsmallblock dasigheader d-block d-sm-none" id="dasigheader">\n                <div class="dasiginnerheader">\n                  ' + back_clear_button + '\n                  <a href="#" role="button" class="btn btn-sm ' + BUTTON_STYLE + continue_button_color + ' dasignav-right dasignavbutton dasigsave">' + continue_label + '</a>\n                  <div id="dasigtitle" class="dasigtitle">'
        if status.questionText:
            output += markdown_to_html(status.questionText, trim=True, status=status)
        else:
            output += word('Sign Your Name')
        output += '</div>\n                </div>\n              </div>\n              <div class="dasigtoppart" id="dasigtoppart">\n                <div id="daerrormess" class="dasigerrormessage dasignotshowing">' + word("You must sign your name to continue.") + '</div>\n'
        if status.pre:
            output += '                <div class="d-none d-sm-block">' + markdown_to_html(status.pre, trim=False, status=status) + '</div>\n'
        if status.questionText:
            output += '                <div class="da-page-header d-none d-sm-block"><h1 class="h3">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        output += '              </div>'
        if status.subquestionText:
            output += '                <div id="dasigmidpart" class="dasigmidpart da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        else:
            output += '\n              <div id="dasigmidpart" class="dasigmidpart"></div>'
        output += '\n              <div id="dasigcontent"' + (' aria-required="true"' if status.extras['required'][0] else '') + '><p class="form-control" style="text-align:center;padding:0;">' + word('Loading.  Please wait . . . ') + '</p></div>\n              <div class="dasigbottompart" id="dasigbottompart">\n                '
        if showUnderText:
            output += '                <div class="d-none d-sm-block">' + markdown_to_html(status.extras['underText'], trim=False, status=status) + '</div>\n                <div class="d-block d-sm-none">' + markdown_to_html(status.extras['underText'], trim=True, status=status) + '</div>'
        output += "\n              </div>"
        if status.submit:
            output += '                <div class="d-none d-sm-block">' + markdown_to_html(status.submit, trim=False, status=status) + '</div>\n'
        output += """
              <fieldset class="da-button-set d-none d-sm-block da-signature">
                <legend class="visually-hidden">""" + word('Press one of the following buttons:') + """</legend>
                <div class="dasigbuttons mt-3">""" + back_button + additional_buttons_before + """
                  <a href="#" role="button" class="btn """ + BUTTON_STYLE + continue_button_color + ' ' + BUTTON_CLASS + """ dasigsave">""" + continue_label + """</a>
                  <a href="#" role="button" class="btn """ + BUTTON_STYLE + BUTTON_COLOR_CLEAR + ' ' + BUTTON_CLASS + """ dasigclear">""" + word('Clear') + """</a>""" + additional_buttons_after + help_button + """
                </div>
              </fieldset>
"""
        output += help_button_area
        if not STRICT_MODE:
            saveas_part = '<input type="hidden" name="_save_as" value="' + escape_id(status.question.fields[0].saveas) + '"/>'
        else:
            saveas_part = ''
        output += '            </div>\n            <form aria-labelledBy="dasigtitle" action="' + root + '" id="dasigform" method="POST">' + saveas_part + '<input type="hidden" id="da_sig_required" value="' + ('1' if status.extras['required'][0] else '0') + '"/><input type="hidden" id="da_ajax" name="ajax" value="0"/><input type="hidden" id="da_the_image" name="_the_image" value=""/><input type="hidden" id="da_success" name="_success" value="0"/>'
        output += tracker_tag(status)
        output += '            </form>\n'
        output += '            <div class="d-block d-md-none"><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br></div>'
    elif status.question.question_type in ["yesno", "yesnomaybe"]:
        # varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST" class="daformyesno">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div class="da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-button-set da-field-' + status.question.question_type + '">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
        output += back_button + additional_buttons_before + '\n                  <button class="btn ' + BUTTON_STYLE + BUTTON_COLOR_YES + ' ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True">' + status.question.yes() + '</button>\n                  <button class="btn ' + BUTTON_STYLE + BUTTON_COLOR_NO + ' ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False">' + status.question.no() + '</button>'
        if status.question.question_type == 'yesnomaybe':
            output += '\n                  <button class="btn ' + BUTTON_STYLE + BUTTON_COLOR_MAYBE + ' ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None">' + markdown_to_html(status.question.maybe(), trim=True, do_terms=False, status=status) + '</button>'
        output += additional_buttons_after
        output += help_button
        output += '\n                </fieldset>\n'
        # output += question_name_tag(status.question)
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type in ["noyes", "noyesmaybe"]:
        # varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST" class="daformnoyes">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div class="da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-button-set da-field-' + status.question.question_type + '">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
        output += back_button + additional_buttons_before + '\n                  <button class="btn ' + BUTTON_STYLE + BUTTON_COLOR_YES + ' ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="False">' + status.question.yes() + '</button>\n                  <button class="btn ' + BUTTON_STYLE + BUTTON_COLOR_NO + ' ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="True">' + status.question.no() + '</button>'
        if status.question.question_type == 'noyesmaybe':
            output += '\n                  <button class="btn ' + BUTTON_STYLE + BUTTON_COLOR_MAYBE + ' ' + BUTTON_CLASS + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="submit" value="None">' + status.question.maybe() + '</button>'
        output += additional_buttons_after
        output += help_button
        output += '\n                </fieldset>\n'
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type == "review":
        fieldlist = []
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
            # if hasattr(field, 'extras'):
            #    if 'script' in field.extras and 'script' in status.extras and field.number in status.extras['script']:
            #        status.extra_scripts.append(status.extras['script'][field.number])
                # if 'css' in field.extras and 'css' in status.extras and field.number in status.extras['css']:
                #     status.extra_css.append(status.extras['css'][field.number])
            if hasattr(field, 'datatype'):
                if field.datatype == 'html' and 'html' in status.extras and field.number in status.extras['html']:
                    if field.number in status.helptexts:
                        fieldlist.append('                <div class="da-form-group row da-field-container da-field-container-note da-review"><div class="col"><div>' + help_wrap(side_note_content, status.helptexts[field.number], status) + '</div></div></div>\n')
                    else:
                        fieldlist.append('                <div class="da-form-group row da-field-container da-field-container-note da-review"><div class="col"><div>' + side_note_content + '</div></div></div>\n')
                    continue
                if field.datatype == 'note' and 'note' in status.extras and field.number in status.extras['note']:
                    if field.number in status.helptexts:
                        fieldlist.append('                <div class="da-form-group row da-field-container da-field-container-note da-review"><div class="col">' + help_wrap(side_note_content, status.helptexts[field.number], status) + '</div></div>\n')
                    else:
                        fieldlist.append('                <div class="da-form-group row da-field-container da-field-container-note da-review"><div class="col">' + side_note_content + '</div></div>\n')
                    continue
                # elif field.datatype in ['script', 'css']:
                #     continue
                if field.datatype == 'button' and hasattr(field, 'label') and field.number in status.helptexts:
                    color = status.question.interview.options.get('review button color', BUTTON_COLOR_REVIEW)
                    if color not in ('link', 'danger', 'warning', 'info', 'primary', 'secondary', 'light', 'dark', 'success'):
                        color = BUTTON_COLOR_REVIEW
                    icon = status.question.interview.options.get('review button icon', 'fas fa-pencil-alt')
                    if isinstance(icon, str) and icon != '':
                        icon = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', icon)
                        if not re.search(r'^fa[a-z] fa-', icon):
                            icon = 'fas fa-' + icon
                        icon = '<i class="' + icon + '"></i> '
                    else:
                        icon = ''
                    fieldlist.append('                <div class="row' + side_note_parent + ' da-review da-review-button bg-light pt-2 my-2"><div class="col"><a href="#" role="button" class="btn btn-sm ' + BUTTON_STYLE + color + ' da-review-action da-review-action-button" data-action=' + myb64doublequote(status.extras['action'][field.number]) + '>' + icon + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a>' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div>' + side_note + '</div>\n')
                    continue
            if hasattr(field, 'label'):
                fieldlist.append('                <div class="da-form-group row' + side_note_parent + ' da-review da-review-label"><div class="col"><a href="#" class="da-review-action" data-action=' + myb64doublequote(status.extras['action'][field.number]) + '>' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + '</a></div>' + side_note + '</div>\n')
                if field.number in status.helptexts:
                    fieldlist.append('                <div class="row da-review da-review-help"><div class="col">' + markdown_to_html(status.helptexts[field.number], status=status, strip_newlines=True) + '</div></div>\n')
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" class="form-horizontal daformreview" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div class="da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        # fieldlist.append('                <input type="hidden" name="_event" value=' + myb64doublequote(json.dumps(list(status.question.fields_used))) + ' />\n')
        if len(fieldlist) > 0:
            output += "".join(fieldlist)
        if status.continueLabel:
            resume_button_label = markdown_to_html(status.continueLabel, trim=True, do_terms=False, status=status)
        else:
            resume_button_label = word('Resume')
        output += status.submit
        output += '                <fieldset class="da-button-set da-field-buttons">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
        if hasattr(status.question, 'review_saveas'):
            output += back_button + additional_buttons_before + '\n                <button type="submit" class="btn ' + BUTTON_STYLE + continue_button_color + ' ' + BUTTON_CLASS + '" name="' + escape_id(safeid(status.question.review_saveas)) + '" value="True">' + continue_label + '</button>' + additional_buttons_after + help_button + '\n                </fieldset>\n'
        else:
            output += back_button + additional_buttons_before + '\n                <button class="btn ' + BUTTON_STYLE + continue_button_color + ' ' + BUTTON_CLASS + '" type="submit">' + resume_button_label + '</button>' + additional_buttons_after + help_button + '\n                </fieldset>\n'
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        output += '            </form>\n'
    elif status.question.question_type == "fields":
        enctype_string = ""
        fieldlist = []
        checkboxes = {}
        files = []
        hiddens = {}
        ml_info = {}
        note_fields = {}
        if status.subquestionText:
            sub_question_text = markdown_to_html(status.subquestionText, status=status, embedder=embed_input)
        if hasattr(status.question, 'fields_saveas'):
            datatypes[safeid(status.question.fields_saveas)] = "boolean"
        field_list = status.get_field_list()
        status.saveas_to_use = {}
        status.saveas_by_number = {}
        seen_first = False
        null_question = True
        for field in field_list:
            if 'html' in status.extras and field.number in status.extras['html']:
                note_fields[field.number] = process_target(status.extras['html'][field.number].rstrip())
            elif 'note' in status.extras and field.number in status.extras['note']:
                note_fields[field.number] = markdown_to_html(status.extras['note'][field.number], status=status, embedder=embed_input)
            if hasattr(field, 'saveas'):
                varnames[safeid('_field_' + str(field.number))] = field.saveas
                if (hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in status.extras) or 'show_if_js' in field.extras)) or (hasattr(field, 'disableothers') and field.disableothers):
                    the_saveas = safeid('_field_' + str(field.number))
                else:
                    the_saveas = field.saveas
                status.saveas_to_use[field.saveas] = the_saveas
                status.saveas_by_number[field.number] = the_saveas
                if the_saveas not in validation_rules['rules']:
                    validation_rules['rules'][the_saveas] = {}
                if the_saveas not in validation_rules['messages']:
                    validation_rules['messages'][the_saveas] = {}
                if 'address_autocomplete' in status.extras and field.number in status.extras['address_autocomplete'] and status.extras['address_autocomplete'][field.number]:
                    if isinstance(status.extras['address_autocomplete'][field.number], bool):
                        autocomplete_info.append([the_saveas, {"types": ["address"], "fields": ["address_components"]}])
                    elif isinstance(status.extras['address_autocomplete'][field.number], dict):
                        autocomplete_info.append([the_saveas, status.extras['address_autocomplete'][field.number]])
                    else:
                        raise Exception("address autocomplete must refer to a boolean value or a dictionary of options")
        seen_extra_header = False
        for field in field_list:
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
                    status.extras['disableothers'] = {}
                status.extras['disableothers'][field.number] = []
                for orig_var in field.disableothers:
                    for the_field in field_list:
                        if the_field is not field and hasattr(the_field, 'saveas') and from_safeid(the_field.saveas) == orig_var:
                            status.extras['disableothers'][field.number].append(status.saveas_by_number[the_field.number])
                            break
            if status.is_empty_mc(field):
                if hasattr(field, 'datatype'):
                    hiddens[field.saveas] = field.datatype
                else:
                    hiddens[field.saveas] = True
                if hasattr(field, 'datatype'):
                    datatypes[field.saveas] = field.datatype
                    if field.datatype in ('object_multiselect', 'object_checkboxes'):
                        datatypes[safeid(from_safeid(field.saveas) + ".gathered")] = 'boolean'
                continue
            if not status.extras['ok'][field.number]:
                continue
            if hasattr(field, 'saveas'):
                null_question = False
            if status.extras['required'][field.number]:
                req_tag = ' darequired'
            else:
                req_tag = ''
            extra_container_class = ''
            if hasattr(field, 'extras'):
                # if 'script' in field.extras and 'script' in status.extras:
                #     status.extra_scripts.append(status.extras['script'][field.number])
                # if 'css' in field.extras and 'css' in status.extras:
                #     status.extra_css.append(status.extras['css'][field.number])
                # fieldlist.append("<div>datatype is " + str(field.datatype) + "</div>")
                if 'css class' in status.extras and field.number in status.extras['css class']:
                    extra_container_class = ' ' + clean_whitespace(status.extras['css class'][field.number]) + '-container'
                if 'ml_group' in field.extras or 'ml_train' in field.extras:
                    ml_info[field.saveas] = {}
                    if 'ml_group' in field.extras:
                        ml_info[field.saveas]['group_id'] = status.extras['ml_group'][field.number]
                    if 'ml_train' in field.extras:
                        ml_info[field.saveas]['train'] = status.extras['ml_train'][field.number]
                if 'show_if_var' in field.extras and 'show_if_val' in status.extras:
                    if field.extras['show_if_mode'] == 0:
                        display_style = 'style="display: none;" '
                    else:
                        display_style = ''
                    if hasattr(field, 'saveas'):
                        fieldlist.append('                <div ' + display_style + 'class="dashowif" data-saveas="' + escape_id(field.saveas) + '" data-showif-sign="' + escape_id(field.extras['show_if_sign']) + '" data-showif-mode="' + str(field.extras['show_if_mode']) + '" data-showif-var="' + escape_id(field.extras['show_if_var']) + '" data-showif-val=' + noquote(str(status.extras['show_if_val'][field.number])) + '>\n')
                    else:
                        fieldlist.append('                <div ' + display_style + 'class="dashowif" data-showif-sign="' + escape_id(field.extras['show_if_sign']) + '" data-showif-mode="' + str(field.extras['show_if_mode']) + '" data-showif-var="' + escape_id(field.extras['show_if_var']) + '" data-showif-val=' + noquote(str(status.extras['show_if_val'][field.number])) + '>\n')
                if 'show_if_js' in field.extras:
                    if status.extras['show_if_js'][field.number]['mode'] == 0:
                        display_style = 'style="display: none;" '
                    else:
                        display_style = ''
                    if hasattr(field, 'saveas'):
                        fieldlist.append('                <div ' + display_style + 'class="dajsshowif" data-saveas="' + escape_id(field.saveas) + '" data-jsshowif=' + myb64doublequote(json.dumps(status.extras['show_if_js'][field.number])) + '>\n')
                    else:
                        fieldlist.append('                <div ' + display_style + 'class="dajsshowif" data-jsshowif=' + myb64doublequote(json.dumps(status.extras['show_if_js'][field.number])) + '>\n')
            if hasattr(field, 'datatype'):
                if field.datatype in custom_types:
                    field_class = ' da-field-container ' + custom_types[field.datatype]['container_class']
                else:
                    field_class = ' da-field-container da-field-container-datatype-' + field.datatype
                if field.datatype == 'html':
                    if hasattr(field, 'collect_type'):
                        if not seen_first:
                            if status.extras['list_collect_length'] <= 1:
                                class_of_first = ' dainvisible da-first-delete'
                            else:
                                class_of_first = ''
                            seen_first = True
                        else:
                            class_of_first = ''
                    if hasattr(field, 'collect_type'):
                        hide_delete = bool('list_minimum' in status.extras and field.collect_number < status.extras['list_minimum'])
                        if status.extras['list_collect_allow_delete'] and not hide_delete:
                            da_remove_existing = '<button type="button" class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_DELETE + ' float-end dacollectremoveexisting' + class_of_first + '"><i class="fas fa-trash"></i> ' + word("Delete") + '</button>'
                        else:
                            da_remove_existing = ''
                        list_message = status.extras['list_message'][field.collect_number]
                        if list_message == '':
                            list_message = str(field.collect_number + 1) + '.'
                        else:
                            list_message = markdown_to_html(list_message, status=status, trim=True, escape=False, do_terms=True)
                        if status.extras['list_collect_add_another_label']:
                            add_another = status.extras['list_collect_add_another_label']
                        else:
                            add_another = word("Add another")
                        if field.collect_type == 'extraheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + class_def + '"><div class="col"><hr><span class="dacollectnum dainvisible">' + list_message + '</span><span class="dacollectremoved text-danger dainvisible"> ' + word("(Deleted)") + '</span><button type="button" class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_DELETE + ' float-end dainvisible dacollectremove"><i class="fas fa-trash"></i> ' + word("Delete") + '</button><button type="button" class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_UNDELETE + ' float-end dainvisible dacollectunremove"><i class="fas fa-trash-restore"></i> ' + word("Undelete") + '</button><button type="button" class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_ADD + ' dacollectadd"><i class="fas fa-plus-circle"></i> ' + add_another + '</button></div></div>\n')
                        elif field.collect_type == 'postheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + class_def + '"><div class="col"></div></div>\n')
                        elif field.collect_type == 'extrapostheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + class_def + '"><div class="col"></div></div>\n')
                        elif field.collect_type == 'extrafinalpostheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + class_def + '"><div class="col"><button type="button" id="da-extra-collect" value=' + myb64doublequote(json.dumps({'function': 'add', 'list': status.extras['list_collect'].instanceName})) + ' class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_ADD + '"><i class="fas fa-plus-circle"></i> ' + add_another + '</button></div></div>\n')
                        elif field.collect_type == 'firstheader':
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + class_def + '"><div class="col"><span class="dacollectnum">' + list_message + '</span><span class="dacollectremoved text-danger dainvisible"> ' + word("(Deleted)") + '</span><button type="button" class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_UNDELETE + ' float-end dainvisible dacollectunremove"><i class="fas fa-trash-restore"></i> ' + word("Undelete") + '</button>' + da_remove_existing + '</div></div>\n')
                        else:
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + class_def + '"><div class="col"><hr><span class="dacollectnum">' + list_message + '</span><span class="dacollectremoved text-danger dainvisible"> ' + word("(Deleted)") + '</span><button type="button" class="btn btn-sm ' + BUTTON_STYLE + BUTTON_COLOR_UNDELETE + ' float-end dainvisible dacollectunremove"><i class="fas fa-trash-restore"></i> ' + word("Undelete") + '</button>' + da_remove_existing + '</div></div>\n')
                    else:
                        if field.number in note_fields:
                            if field.number in status.helptexts:
                                fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row da-field-container da-field-container-note' + class_def + extra_container_class + '"><div class="col">' + help_wrap(note_fields[field.number], status.helptexts[field.number], status) + '</div></div>\n')
                            else:
                                fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row da-field-container da-field-container-note' + class_def + extra_container_class + '"><div class="col"><div>' + note_fields[field.number] + '</div></div></div>\n')
                    # continue
                elif field.datatype == 'note':
                    if field.number in note_fields:
                        if field.number in status.helptexts:
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row da-field-container da-field-container-note' + class_def + extra_container_class + '"><div class="col">' + help_wrap(note_fields[field.number], status.helptexts[field.number], status) + '</div></div>\n')
                        else:
                            fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row da-field-container da-field-container-note' + class_def + extra_container_class + '"><div class="col">' + note_fields[field.number] + '</div></div>\n')
                    # continue
                # elif field.datatype in ['script', 'css']:
                #     continue
                else:
                    if hasattr(field, 'choicetype'):
                        vals = set(str(x['key']) for x in status.selectcompute[field.number])
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
                    if field.datatype in ('object_multiselect', 'object_checkboxes'):
                        datatypes[safeid(from_safeid(field.saveas) + ".gathered")] = 'boolean'
            else:
                field_class = ' da-field-container'
            if hasattr(field, 'inputtype'):
                field_class += ' da-field-container-inputtype-' + field.inputtype
            elif hasattr(field, 'choicetype'):
                if field.datatype in ['checkboxes', 'object_checkboxes']:
                    field_class += ' da-field-container-inputtype-checkboxes'
                elif field.datatype in ['multiselect', 'object_multiselect']:
                    field_class += ' da-field-container-inputtype-multiselect'
                elif field.datatype == 'object_radio' or (field.datatype == 'object' and hasattr(field, 'inputtype') and field.inputtype == 'radio'):
                    field_class += ' da-field-container-inputtype-radio'
                else:
                    field_class += ' da-field-container-inputtype-dropdown'
            field_class += extra_container_class
            if field.number in status.helptexts:
                helptext_start = '<a tabindex="0" class="text-info ms-1 dapointer" data-bs-container="body" data-bs-toggle="popover" data-bs-placement="bottom" data-bs-content=' + noquote(markdown_to_html(status.helptexts[field.number], trim=True)) + '>'
                helptext_end = '<i class="fas fa-question-circle"></i></a>'
            else:
                helptext_start = ''
                helptext_end = ''
            if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                onchange.append(safeid('_field_' + str(field.number)))
            if hasattr(field, 'saveas'):
                varnames[safeid('_field_' + str(field.number))] = field.saveas
                # the_saveas = status.saveas_to_use[field.saveas]
                the_saveas = status.saveas_by_number[field.number]
                if (hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in status.extras) or 'show_if_js' in field.extras)) or (hasattr(field, 'disableothers') and field.disableothers):
                    label_saveas = the_saveas
                else:
                    label_saveas = field.saveas
                if not (hasattr(field, 'datatype') and field.datatype in ['multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes']):
                    if hasattr(field, 'inputtype') and field.inputtype == 'combobox':
                        validation_rules['messages'][the_saveas]['required'] = field.validation_message('combobox required', status, word("You need to select one or type in a new value."))
                    elif hasattr(field, 'inputtype') and field.inputtype == 'ajax':
                        validation_rules['messages'][the_saveas]['ajaxrequired'] = field.validation_message('combobox required', status, word("You need to select one."))
                    elif hasattr(field, 'datatype') and (field.datatype == 'object_radio' or (hasattr(field, 'inputtype') and field.inputtype in ('yesnoradio', 'noyesradio', 'radio', 'dropdown'))):
                        validation_rules['messages'][the_saveas]['required'] = field.validation_message('multiple choice required', status, word("You need to select one."))
                    else:
                        validation_rules['messages'][the_saveas]['required'] = field.validation_message('required', status, word("This field is required."))
                    if status.extras['required'][field.number]:
                        # logmessage(field.datatype)
                        if hasattr(field, 'inputtype') and field.inputtype == 'ajax':
                            validation_rules['rules'][the_saveas]['ajaxrequired'] = True
                            validation_rules['rules'][the_saveas]['required'] = False
                        else:
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
                        validation_rules['messages'][y]['checkone'] = field.validation_message('checkboxes required', status, word("Check at least one option, or check “%s”"), parameters=tuple([strip_tags(status.labels[field.number])]))
                    if 'groups' not in validation_rules:
                        validation_rules['groups'] = {}
                    validation_rules['groups'][the_saveas + '_group'] = ' '.join(uncheck_list + [the_saveas])
                if field.datatype not in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                    for key in ('minlength', 'maxlength'):
                        if hasattr(field, 'extras') and key in field.extras and key in status.extras:
                            # logmessage("Adding validation rule for " + str(key))
                            validation_rules['rules'][the_saveas][key] = int(float(status.extras[key][field.number]))
                            if key == 'minlength':
                                validation_rules['messages'][the_saveas][key] = field.validation_message(key, status, word("You must type at least %s characters."), parameters=tuple([status.extras[key][field.number]]))
                            elif key == 'maxlength':
                                validation_rules['messages'][the_saveas][key] = field.validation_message(key, status, word("You cannot type more than %s characters."), parameters=tuple([status.extras[key][field.number]]))
                if hasattr(field, 'inputtype') and field.inputtype == 'hidden':
                    validation_rules['rules'][the_saveas] = {'required': False}
            if hasattr(field, 'datatype'):
                if field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes') and ((hasattr(field, 'nota') and status.extras['nota'][field.number] is not False) or (hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in status.extras) or ('maxlength' in field.extras and 'maxlength' in status.extras)))):
                    if field.datatype.endswith('checkboxes'):
                        d_type = 'checkbox'
                    else:
                        d_type = 'multiselect'
                    if hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in status.extras) or ('maxlength' in field.extras and 'maxlength' in status.extras)):
                        checkbox_rules = {}
                        checkbox_messages = {}
                        if 'minlength' in field.extras and 'minlength' in status.extras and 'maxlength' in field.extras and 'maxlength' in status.extras and int(status.extras['minlength'][field.number]) == int(status.extras['maxlength'][field.number]) and int(status.extras['minlength'][field.number]) > 0:
                            if 'nota' not in status.extras:
                                status.extras['nota'] = {}
                            status.extras['nota'][field.number] = False
                            the_length = int(status.extras['maxlength'][field.number])
                            if d_type == 'checkbox':
                                checkbox_rules['checkexactly'] = [str(field.number), the_length]
                                checkbox_messages['checkexactly'] = field.validation_message(d_type + ' minmaxlength', status, word("Please select exactly %s."), parameters=tuple([the_length]))
                            else:
                                checkbox_rules['selectexactly'] = [the_length]
                                checkbox_messages['selectexactly'] = field.validation_message(d_type + ' minmaxlength', status, word("Please select exactly %s."), parameters=tuple([the_length]))
                        else:
                            if 'minlength' in field.extras and 'minlength' in status.extras:
                                if d_type == 'checkbox':
                                    checkbox_rules['checkatleast'] = [str(field.number), status.extras['minlength'][field.number]]
                                    if status.extras['minlength'][field.number] == 1:
                                        checkbox_messages['checkatleast'] = field.validation_message(d_type + ' minlength', status, word("Please select one."))
                                    else:
                                        checkbox_messages['checkatleast'] = field.validation_message(d_type + ' minlength', status, word("Please select at least %s."), parameters=tuple([status.extras['minlength'][field.number]]))
                                    if int(float(status.extras['minlength'][field.number])) > 0:
                                        if 'nota' not in status.extras:
                                            status.extras['nota'] = {}
                                        status.extras['nota'][field.number] = False
                                else:
                                    the_length = int(status.extras['minlength'][field.number])
                                    if the_length > 0:
                                        checkbox_rules['required'] = True
                                        checkbox_rules['minlength'] = the_length
                                        if status.extras['minlength'][field.number] == 1:
                                            checkbox_messages['minlength'] = field.validation_message(d_type + ' minlength', status, word("Please select one."))
                                            checkbox_messages['required'] = field.validation_message(d_type + ' minlength', status, word("Please select one."))
                                        else:
                                            checkbox_messages['minlength'] = field.validation_message('checkbox minlength', status, word("Please select at least %s."), parameters=tuple([status.extras['minlength'][field.number]]))
                                            checkbox_messages['required'] = field.validation_message('checkbox minlength', status, word("Please select at least %s."), parameters=tuple([status.extras['minlength'][field.number]]))
                            if 'maxlength' in field.extras and 'maxlength' in status.extras:
                                if d_type == 'checkbox':
                                    checkbox_rules['checkatmost'] = [str(field.number), status.extras['maxlength'][field.number]]
                                    checkbox_messages['checkatmost'] = field.validation_message(d_type + ' maxlength', status, word("Please select no more than %s."), parameters=tuple([status.extras['maxlength'][field.number]]))
                                else:
                                    checkbox_rules['maxlength'] = int(status.extras['maxlength'][field.number])
                                    checkbox_messages['maxlength'] = field.validation_message(d_type + ' maxlength', status, word("Please select no more than %s."), parameters=tuple([status.extras['maxlength'][field.number]]))
                        if d_type == 'checkbox':
                            validation_rules['rules']['_ignore' + str(field.number)] = checkbox_rules
                            validation_rules['messages']['_ignore' + str(field.number)] = checkbox_messages
                        else:
                            validation_rules['rules'][the_saveas] = checkbox_rules
                            validation_rules['messages'][the_saveas] = checkbox_messages
                    if d_type == 'checkbox' and hasattr(field, 'nota') and status.extras['nota'][field.number] is not False:
                        if '_ignore' + str(field.number) not in validation_rules['rules']:
                            validation_rules['rules']['_ignore' + str(field.number)] = {}
                        if 'checkatleast' not in validation_rules['rules']['_ignore' + str(field.number)]:
                            validation_rules['rules']['_ignore' + str(field.number)]['checkatleast'] = [str(field.number), 1]
                        if status.extras['nota'][field.number] is True:
                            formatted_item = word("None of the above")
                            unescaped_item = formatted_item
                        else:
                            if hasattr(field, 'saveas') and field.saveas in status.embedded:
                                formatted_item = markdown_to_html(str(status.extras['nota'][field.number]), status=status, trim=True, escape=False, do_terms=False)
                            else:
                                formatted_item = markdown_to_html(str(status.extras['nota'][field.number]), status=status, trim=True, escape=True, do_terms=False)
                            unescaped_item = markdown_to_html(str(status.extras['nota'][field.number]), status=status, trim=False, escape=False, do_terms=False)
                        if '_ignore' + str(field.number) not in validation_rules['messages']:
                            validation_rules['messages']['_ignore' + str(field.number)] = {}
                        validation_rules['messages']['_ignore' + str(field.number)]['checkatleast'] = field.validation_message('checkboxes required', status, word("Check at least one option, or check “%s”"), parameters=tuple([strip_tags(unescaped_item)]))
                if field.datatype == 'date':
                    validation_rules['rules'][the_saveas]['date'] = True
                    validation_rules['messages'][the_saveas]['date'] = field.validation_message('date', status, word("You need to enter a valid date."))
                    if hasattr(field, 'extras') and 'min' in field.extras and 'min' in status.extras and 'max' in field.extras and 'max' in status.extras and field.number in status.extras['min'] and field.number in status.extras['max']:
                        validation_rules['rules'][the_saveas]['minmaxdate'] = [format_date(status.extras['min'][field.number], format='yyyy-MM-dd'), format_date(status.extras['max'][field.number], format='yyyy-MM-dd')]
                        validation_rules['messages'][the_saveas]['minmaxdate'] = field.validation_message('date minmax', status, word("You need to enter a date between %s and %s."), parameters=(format_date(status.extras['min'][field.number], format='medium'), format_date(status.extras['max'][field.number], format='medium')))
                    else:
                        was_defined = {}
                        for key in ['min', 'max']:
                            if hasattr(field, 'extras') and key in field.extras and key in status.extras and field.number in status.extras[key]:
                                was_defined[key] = True
                                # logmessage("Adding validation rule for " + str(key))
                                validation_rules['rules'][the_saveas][key + 'date'] = format_date(status.extras[key][field.number], format='yyyy-MM-dd')
                                if key == 'min':
                                    validation_rules['messages'][the_saveas]['mindate'] = field.validation_message('date min', status, word("You need to enter a date on or after %s."), parameters=tuple([format_date(status.extras[key][field.number], format='medium')]))
                                elif key == 'max':
                                    validation_rules['messages'][the_saveas]['maxdate'] = field.validation_message('date max', status, word("You need to enter a date on or before %s."), parameters=tuple([format_date(status.extras[key][field.number], format='medium')]))
                        if len(was_defined) == 0 and 'default date min' in status.question.interview.options and 'default date max' in status.question.interview.options:
                            validation_rules['rules'][the_saveas]['minmaxdate'] = [format_date(status.question.interview.options['default date min'], format='yyyy-MM-dd'), format_date(status.question.interview.options['default date max'], format='yyyy-MM-dd')]
                            validation_rules['messages'][the_saveas]['minmaxdate'] = field.validation_message('date minmax', status, word("You need to enter a date between %s and %s."), parameters=(format_date(status.question.interview.options['default date min'], format='medium'), format_date(status.question.interview.options['default date max'], format='medium')))
                        elif 'max' not in was_defined and 'default date max' in status.question.interview.options:
                            validation_rules['rules'][the_saveas]['maxdate'] = format_date(status.question.interview.options['default date max'], format='yyyy-MM-dd')
                            validation_rules['messages'][the_saveas]['maxdate'] = field.validation_message('date max', status, word("You need to enter a date on or before %s."), parameters=tuple([format_date(status.question.interview.options['default date max'], format='medium')]))
                        elif 'min' not in was_defined and 'default date min' in status.question.interview.options:
                            validation_rules['rules'][the_saveas]['mindate'] = format_date(status.question.interview.options['default date min'], format='yyyy-MM-dd')
                            validation_rules['messages'][the_saveas]['mindate'] = field.validation_message('date min', status, word("You need to enter a date on or after %s."), parameters=tuple([format_date(status.question.interview.options['default date min'], format='medium')]))
                if field.datatype == 'time':
                    validation_rules['rules'][the_saveas]['time'] = True
                    validation_rules['messages'][the_saveas]['time'] = field.validation_message('time', status, word("You need to enter a valid time."))
                if field.datatype in ['datetime', 'datetime-local']:
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
                    if field.datatype == 'integer' and not ('step' in status.extras and field.number in status.extras['step']):
                        validation_rules['messages'][the_saveas]['step'] = field.validation_message('integer', status, word("Please enter a whole number."))
                    elif 'step' in status.extras and field.number in status.extras['step']:
                        validation_rules['messages'][the_saveas]['step'] = field.validation_message('step', status, word("Please enter a multiple of {0}."))
                    # logmessage("Considering adding validation rule")
                    for key in ['min', 'max']:
                        if hasattr(field, 'extras') and key in field.extras and key in status.extras and field.number in status.extras[key]:
                            # logmessage("Adding validation rule for " + str(key))
                            validation_rules['rules'][the_saveas][key] = float(status.extras[key][field.number])
                            if key == 'min':
                                validation_rules['messages'][the_saveas][key] = field.validation_message('min', status, word("You need to enter a number that is at least %s."), parameters=tuple([status.extras[key][field.number]]))
                            elif key == 'max':
                                validation_rules['messages'][the_saveas][key] = field.validation_message('max', status, word("You need to enter a number that is at most %s."), parameters=tuple([status.extras[key][field.number]]))
                if field.datatype in ['files', 'file', 'camera', 'user', 'environment', 'camcorder', 'microphone']:
                    enctype_string = ' enctype="multipart/form-data"'
                    files.append(the_saveas)
                    validation_rules['messages'][the_saveas]['required'] = field.validation_message('file required', status, word("You must provide a file."))
                    if 'accept' in status.extras and field.number in status.extras['accept']:
                        validation_rules['messages'][the_saveas]['accept'] = field.validation_message('accept', status, word("Please upload a file with a valid file format."))
                    if daconfig['maximum content length'] is not None:
                        validation_rules['rules'][the_saveas]['maxuploadsize'] = daconfig['maximum content length']
                        validation_rules['messages'][the_saveas]['maxuploadsize'] = field.validation_message('maxuploadsize', status, word("Your file upload is larger than the server can accept. Please reduce the size of your file upload."))
                if field.datatype in custom_types:
                    if custom_types[field.datatype]['jq_rule'] is not None:
                        if not isinstance(custom_types[field.datatype]['jq_rule'], list):
                            to_enable = [custom_types[field.datatype]['jq_rule']]
                        else:
                            to_enable = custom_types[field.datatype]['jq_rule']
                        for rule_name in to_enable:
                            validation_rules['rules'][the_saveas][rule_name] = True
                        if custom_types[field.datatype]['jq_message'] is not None:
                            if isinstance(custom_types[field.datatype]['jq_rule'], list):
                                if not isinstance(custom_types[field.datatype]['jq_message'], dict):
                                    raise Exception("jq_message must be a dictionary if jq_rule is list")
                                the_messages = custom_types[field.datatype]['jq_message']
                            else:
                                if isinstance(custom_types[field.datatype]['jq_message'], dict):
                                    the_messages = custom_types[field.datatype]['jq_message']
                                elif isinstance(custom_types[field.datatype]['jq_message'], str):
                                    the_messages = {custom_types[field.datatype]['jq_rule']: custom_types[field.datatype]['jq_message']}
                                else:
                                    raise Exception("jq_message must be a dictionary or a string")
                            for rule_name, the_message in the_messages.items():
                                validation_rules['messages'][the_saveas][rule_name] = field.validation_message(rule_name, status, word(the_message))
                        for rule_name in to_enable:
                            if rule_name != 'required' and rule_name not in validation_rules['messages'][the_saveas]:
                                validation_rules['messages'][the_saveas][rule_name] = field.validation_message(rule_name, status, word('You need to enter a valid value.'))
                if field.datatype == 'boolean':
                    if hasattr(field, 'inputtype') and field.inputtype in ('yesnoradio', 'noyesradio'):
                        checkboxes[field.saveas] = 'None'
                    elif field.sign > 0:
                        checkboxes[field.saveas] = 'False'
                    else:
                        checkboxes[field.saveas] = 'True'
                elif field.datatype == 'threestate':
                    checkboxes[field.saveas] = 'None'
                elif field.datatype in ['multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes']:
                    if field.choicetype in ['compute', 'manual']:
                        pairlist = list(status.selectcompute[field.number])
                    else:
                        pairlist = []
                    if hasattr(field, 'shuffle') and field.shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if isinstance(pair['key'], str):
                            checkboxes[safeid(from_safeid(field.saveas) + "[B" + myb64quote(pair['key']) + "]")] = 'False'
                        else:
                            checkboxes[safeid(from_safeid(field.saveas) + "[R" + myb64quote(repr(pair['key'])) + "]")] = 'False'
                elif not status.extras['required'][field.number]:
                    if hasattr(field, 'saveas'):
                        checkboxes[field.saveas] = 'None'
            if hasattr(field, 'inputtype') and field.inputtype == 'hidden':
                fieldlist.append('                ' + input_for(status, field) + '\n')
                continue
            if hasattr(field, 'saveas') and field.saveas in status.embedded:
                continue
            if hasattr(field, 'label'):
                if hasattr(field, 'datatype') and field.datatype not in ('checkboxes', 'object_checkboxes'):
                    label_for = ' for="' + escape_id(label_saveas) + '"'
                else:
                    label_for = ''
                if status.labels[field.number] == 'no label':
                    fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + class_def + '' + side_note_parent + req_tag + field_class + ' da-field-container-nolabel">\n                  <span class="visually-hidden">' + word("Answer here") + '</span>\n                  <div class="col dawidecol dafieldpart">' + input_for(status, field, wide=True) + '</div>' + side_note + '\n                </div>\n')
                elif hasattr(field, 'inputtype') and field.inputtype in ['yesnowide', 'noyeswide']:
                    fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row dayesnospacing ' + side_note_parent + field_class + ' da-field-container-nolabel' + class_def + '">\n                  <span class="visually-hidden">' + word("Check if applicable") + '</span>\n                  <div class="col dawidecol dafieldpart">' + input_for(status, field) + '</div>' + side_note + '\n                </div>\n')
                elif floating_labels or (hasattr(field, 'floating_label') and status.extras['floating_label'][field.number]):
                    if hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes']:
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group dayesnospacing' + side_note_parent + field_class + ' da-field-container-nolabel' + class_def + '">\n                  <span class="visually-hidden">' + word("Check if applicable") + '</span>\n                  <div class="dafieldpart">' + input_for(status, field) + side_note + '</div>\n                </div>\n')
                    elif status.labels[field.number] == '':
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group' + side_note_parent + req_tag + field_class + ' da-field-container-emptylabel' + class_def + '">\n                  <span class="visually-hidden">' + word("Answer here") + '</span>\n                  <div class="dafieldpart">' + input_for(status, field) + side_note + '</div>\n                </div>\n')
                    else:
                        floating_label = markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True)
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group-floating form-floating mb-3' + side_note_parent + req_tag + field_class + class_def + '">\n                  ' + input_for(status, field, floating_label=strip_quote(to_text(floating_label, {}, []).strip())) + side_note + '\n                  <label ' + label_for + '>' + floating_label + '</label>\n                </div>\n')
                elif labels_above or (hasattr(field, 'label_above_field') and status.extras['label_above_field'][field.number]):
                    if hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes']:
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group dayesnospacing' + side_note_parent + field_class + ' da-field-container-nolabel' + class_def + '">\n                  <span class="visually-hidden">' + word("Check if applicable") + '</span>\n                  <div class="dafieldpart">' + input_for(status, field) + side_note + '</div>\n                </div>\n')
                    elif status.labels[field.number] == '':
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group' + side_note_parent + req_tag + field_class + ' da-field-container-emptylabel' + class_def + '">\n                  <span class="visually-hidden">' + word("Answer here") + '</span>\n                  <div class="dafieldpart">' + input_for(status, field) + side_note + '</div>\n                </div>\n')
                    else:
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group' + side_note_parent + req_tag + field_class + class_def + '">\n                  <label class="form-label da-top-label"' + label_for + '>' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + helptext_start + helptext_end + '</label>\n                  <div class="dafieldpart">' + input_for(status, field) + side_note + '</div>\n                </div>\n')
                else:
                    if hasattr(field, 'inputtype') and field.inputtype in ['yesno', 'noyes']:
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row dayesnospacing' + side_note_parent + req_tag + field_class + ' da-field-container-emptylabel' + class_def + '"><span  class="visually-hidden">' + word("Check if applicable") + '</span><div class="offset-' + daconfig['grid classes']['label width'] + ' col-' + daconfig['grid classes']['field width'] + ' dafieldpart">' + input_for(status, field) + '</div>' + side_note + '</div>\n')
                    elif status.labels[field.number] == '':
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + side_note_parent + req_tag + field_class + ' da-field-container-emptylabel' + class_def + '"><span class="visually-hidden">' + word("Answer here") + '</span><div class="offset-' + daconfig['grid classes']['label width'] + ' col-' + daconfig['grid classes']['field width'] + ' dafieldpart danolabel">' + input_for(status, field) + '</div>' + side_note + '</div>\n')
                    else:
                        fieldlist.append('                <div ' + style_def + data_def + 'class="da-form-group row' + side_note_parent + req_tag + field_class + class_def + '"><label' + label_for + ' class="col-' + daconfig['grid classes']['label width'] + ' col-form-label da-form-label datext-right">' + markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True) + helptext_start + helptext_end + '</label><div class="col-' + daconfig['grid classes']['field width'] + ' dafieldpart">' + input_for(status, field) + '</div>' + side_note + '</div>\n')
            if hasattr(field, 'extras') and (('show_if_var' in field.extras and 'show_if_val' in status.extras) or 'show_if_js' in field.extras):
                fieldlist.append('                </div>\n')
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" class="form-horizontal daformfields" method="POST"' + enctype_string + autofill + '>\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div class="da-subquestion">\n' + sub_question_text
            output += '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if len(fieldlist) > 0:
            output += "".join(fieldlist)
        # else:
        #    output += "                <p>Error: no fields</p>\n"
        # output += '</div>\n'
        if status.extras.get('list_collect', False) is not False and not STRICT_MODE:
            output += '                <input type="hidden" name="_list_collect_list" value=' + myb64doublequote(json.dumps(status.extras['list_collect'].instanceName)) + '/>\n'
        if status.extras.get('list_collect_is_final', False) and status.extras['list_collect'].auto_gather:
            if status.extras['list_collect'].ask_number:
                output += '                <input type="hidden" name="' + escape_id(safeid(status.extras['list_collect'].instanceName + ".target_number")) + '" value="0"/>\n'
            else:
                output += '                <input type="hidden" name="' + escape_id(safeid(status.extras['list_collect'].instanceName + ".there_is_another")) + '" value="False"/>\n'
        if len(checkboxes) > 0:
            output += '                <input type="hidden" name="_checkboxes" value=' + myb64doublequote(json.dumps(checkboxes)) + '/>\n'
        if len(hiddens) > 0 and not STRICT_MODE:
            output += '                <input type="hidden" name="_empties" value=' + myb64doublequote(json.dumps(hiddens)) + '/>\n'
        if len(ml_info) > 0 and not STRICT_MODE:
            output += '                <input type="hidden" name="_ml_info" value=' + myb64doublequote(json.dumps(ml_info)) + '/>\n'
        if len(files) > 0:
            output += '                <input type="hidden" name="_files" value=' + myb64doublequote(json.dumps(files)) + '/>\n'
        if null_question:
            output += '                <input type="hidden" name="_null_question" value="1" />\n'
        output += status.submit
        output += '                <fieldset class="da-button-set da-field-buttons">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
        if hasattr(status.question, 'fields_saveas'):
            output += back_button + additional_buttons_before + '\n                <button type="submit" class="btn ' + BUTTON_CLASS + ' ' + BUTTON_STYLE + continue_button_color + '" name="' + escape_id(safeid(status.question.fields_saveas)) + '" value="True">' + continue_label + '</button>' + additional_buttons_after + help_button + '\n                </fieldset>\n'
        else:
            output += back_button + additional_buttons_before + '\n                  <button class="btn ' + BUTTON_CLASS + ' ' + BUTTON_STYLE + continue_button_color + '" type="submit">' + continue_label + '</button>' + additional_buttons_after + help_button + '\n                </fieldset>\n'
        # output += question_name_tag(status.question)
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
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
        # varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        datatypes[status.question.fields[0].saveas] = "boolean"
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST" class="daformcontinue">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div class="da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-button-set da-field-buttons">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
        output += back_button + additional_buttons_before + '\n                <button type="submit" class="btn ' + BUTTON_CLASS + ' ' + BUTTON_STYLE + continue_button_color + '" name="' + escape_id(status.question.fields[0].saveas) + '" value="True">' + continue_label + '</button>' + additional_buttons_after + help_button + '\n                </fieldset>\n'
        # output += question_name_tag(status.question)
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
        output += tracker_tag(status)
        output += datatype_tag(datatypes)
        status.datatypes = datatypes
        output += varname_tag(varnames)
        status.varnames = varnames
        output += '            </form>\n'
    elif status.question.question_type == "multiple_choice":
        # varnames[safeid('_field_' + str(status.question.fields[0].number))] = status.question.fields[0].saveas
        if status.question.fields[0].number in status.defaults and isinstance(status.defaults[status.question.fields[0].number], (str, int, float, bool, NoneType)):
            defaultvalue = str(status.defaults[status.question.fields[0].number])
            # logmessage("Default value is " + str(defaultvalue))
        else:
            defaultvalue = None
        if hasattr(status.question.fields[0], 'datatype'):
            datatypes[status.question.fields[0].saveas] = status.question.fields[0].datatype
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" method="POST" class="daformmultiplechoice">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div class="da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        validation_rules['errorElement'] = "span"
        validation_rules['errorLabelContainer'] = "#daerrorcontainer"
        if status.question.question_variety in ["radio", "dropdown", "combobox"]:
            if status.question.question_variety == "radio":
                verb = 'check'
                output += '                <fieldset class="da-field-' + status.question.question_variety + '">\n                  <legend class="visually-hidden">' + word("Choices (choose one):") + "</legend>\n"
            else:
                verb = 'select'
                if status.question.question_variety == "dropdown":
                    inner_fieldlist = ['<option value="">' + option_escape(word('Select...')) + '</option>']
                else:
                    inner_fieldlist = ['<option value="">' + option_escape(word('Select one')) + '</option>']
            if hasattr(status.question.fields[0], 'saveas'):
                id_index = 0
                pairlist = list(status.selectcompute[status.question.fields[0].number])
                using_opt_groups = all('group' in pair for pair in pairlist)
                using_shuffle = hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle
                if using_opt_groups:
                    group_order = list(range(len(pairlist)))
                    if using_shuffle:
                        random.shuffle(group_order)
                    groups = {}
                    for idx, p in zip(group_order, pairlist):
                        if not p.get('group') in groups:
                            groups[p.get('group')] = idx
                    if using_shuffle:
                        pairlist = sorted(pairlist, key=lambda p: groups[p.get('group')] * 1000 + random.randint(1, 1000))
                    else:
                        # stable sort: keep group items in the same relative order
                        pairlist = sorted(pairlist, key=lambda p: groups[p.get('group')])
                elif using_shuffle:
                    random.shuffle(pairlist)
                found_default = False
                last_group = None
                for pair in pairlist:
                    if using_opt_groups and pair.get('group') != last_group:
                        if last_group is not None:
                            inner_fieldlist.append('</optgroup>')
                        pair_group = pair.get('group')
                        inner_fieldlist.append(f'<optgroup label="{pair_group}">')
                        last_group = pair_group
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    if pair.get('css class', None):
                        css_class = ' ' + pair['css class'].strip()
                    else:
                        css_class = ''
                    if pair.get('color', None):
                        css_color = pair['color'].strip()
                    else:
                        css_color = DEFAULT_LABELAUTY_COLOR
                    helptext = pair.get('help', None)
                    ischecked = ''
                    if 'default' in pair and pair['default'] and defaultvalue is None:
                        ischecked = ' ' + verb + 'ed="' + verb + 'ed"'
                    formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=True, do_terms=False)
                    if defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue):
                        ischecked = ' ' + verb + 'ed="' + verb + 'ed"'
                        found_default = True
                    if status.question.question_variety == "radio":
                        output += '                <div class="row"><div class="col">' + help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + css_color + '" data-color="' + css_color + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + css_class + '" id="' + escape_id(status.question.fields[0].saveas) + '_' + str(id_index) + '" name="' + escape_id(status.question.fields[0].saveas) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + '/>', helptext, status) + '</div></div>\n'
                    else:
                        if css_class:
                            css_class = 'class="' + css_class.strip() + '"'
                        inner_fieldlist.append('<option value=' + fix_double_quote(str(pair['key'])) + ischecked + css_class + '>' + markdown_to_html(str(pair['label']), status=status, trim=True, escape='option', do_terms=False) + '</option>')
                    id_index += 1
                if status.question.question_variety != "radio" and found_default:
                    inner_fieldlist = inner_fieldlist[1:]
                if status.question.question_variety in ["dropdown", "combobox"]:
                    if status.question.question_variety == 'combobox':
                        combobox = ' form-control combobox'
                        daspaceafter = ' daspaceafter'
                        if defaultvalue:
                            datadefault = ' data-default=' + fix_double_quote(str(defaultvalue))
                        else:
                            datadefault = ''
                        field_container_class = ' da-field-container-combobox'
                    else:
                        combobox = ' form-select'
                        datadefault = ''
                        daspaceafter = ''
                        field_container_class = ' da-field-container-dropdown'
                    output += '                <div class="row' + field_container_class + '"><div class="col' + daspaceafter + '"><select aria-labelledby="daMainQuestion" class="daspaceafter' + combobox + '"' + datadefault + ' name="' + escape_id(status.question.fields[0].saveas) + '" id="' + escape_id(status.question.fields[0].saveas) + '" required >' + "".join(inner_fieldlist) + '</select></div></div>\n'
                if status.question.question_variety == 'combobox':
                    validation_rules['messages'][status.question.fields[0].saveas] = {'required': status.question.fields[0].validation_message('combobox required', status, word("You need to select one or type in a new value."))}
                else:
                    validation_rules['messages'][status.question.fields[0].saveas] = {'required': status.question.fields[0].validation_message('multiple choice required', status, word("You need to select one."))}
                validation_rules['rules'][status.question.fields[0].saveas] = {'required': True}
            else:
                indexno = 0
                found_default = False
                for choice in status.selectcompute[status.question.fields[0].number]:
                    if 'image' in choice:
                        the_icon = icon_html(status, choice['image']) + ' '
                    else:
                        the_icon = ''
                    if 'help' in choice:
                        helptext = choice['help']
                    else:
                        helptext = None
                    if 'default' in choice:
                        ischecked = ' ' + verb + 'ed="' + verb + 'ed"'
                        found_default = True
                    else:
                        ischecked = ''
                    if choice.get('css class', None):
                        css_class = ' ' + choice['css class'].strip()
                    else:
                        css_class = ''
                    if choice.get('color', None):
                        css_color = choice['color'].strip()
                    else:
                        css_color = DEFAULT_LABELAUTY_COLOR
                    id_index = 0
                    formatted_key = markdown_to_html(choice['label'], status=status, trim=True, escape=True, do_terms=False)
                    if status.question.question_variety == "radio":
                        output += '                <div class="row"><div class="col">' + help_wrap('<input aria-label="' + formatted_key + '" alt="' + formatted_key + '" data-color="' + css_color + '" data-labelauty="' + my_escape(the_icon) + formatted_key + '|' + my_escape(the_icon) + formatted_key + '" class="da-to-labelauty' + css_class + '" id="multiple_choice_' + str(indexno) + '_' + str(id_index) + '" name="X211bHRpcGxlX2Nob2ljZQ" type="radio" value="' + str(indexno) + '"' + ischecked + '/>', helptext, status) + '</div></div>\n'
                    else:
                        if css_class:
                            css_class = 'class="' + css_class.strip() + '"'
                        inner_fieldlist.append('<option value="' + str(indexno) + '"' + ischecked + css_class + '>' + markdown_to_html(choice['label'], status=status, trim=True, escape='option', do_terms=False) + '</option>')
                    id_index += 1
                    indexno += 1
                if status.question.question_variety != "radio" and found_default:
                    inner_fieldlist = inner_fieldlist[1:]
                if status.question.question_variety in ["dropdown", "combobox"]:
                    if status.question.question_variety == 'combobox':
                        combobox = 'form-control combobox'
                        daspaceafter = ' daspaceafter'
                    else:
                        combobox = 'form-select daspaceafter'
                        daspaceafter = ''
                    if defaultvalue:
                        datadefault = ' data-default=' + fix_double_quote(str(defaultvalue))
                    else:
                        datadefault = ''
                    output += '                <div class="row"><div class="col' + daspaceafter + '"><select class="' + combobox + '"' + datadefault + ' name="X211bHRpcGxlX2Nob2ljZQ" required >' + "".join(inner_fieldlist) + '</select></div></div>\n'
                if status.question.question_variety == 'combobox':
                    validation_rules['messages']['X211bHRpcGxlX2Nob2ljZQ'] = {'required': status.question.fields[0].validation_message('combobox required', status, word("You need to select one or type in a new value."))}
                else:
                    validation_rules['messages']['X211bHRpcGxlX2Nob2ljZQ'] = {'required': status.question.fields[0].validation_message('multiple choice required', status, word("You need to select one."))}
                validation_rules['rules']['X211bHRpcGxlX2Nob2ljZQ'] = {'required': True}
            output += '                <div id="daerrorcontainer" style="display:none"></div>\n'
            if status.question.question_variety == "radio":
                output += "                </fieldset>\n"
            output += status.submit
            output += '                <fieldset class="da-button-set da-field-buttons">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
            output += back_button + additional_buttons_before + '\n'
            output += '                  <button class="btn ' + BUTTON_CLASS + ' ' + BUTTON_STYLE + continue_button_color + '" type="submit">' + continue_label + '</button>' + additional_buttons_after + help_button + '\n'
            output += '                </fieldset>\n'
        else:
            output += status.submit
            output += '                <fieldset class="da-button-set da-field-buttons">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
            output += back_button + additional_buttons_before + '\n'
            if hasattr(status.question.fields[0], 'saveas'):
                if hasattr(status.question.fields[0], 'has_code') and status.question.fields[0].has_code:
                    pairlist = list(status.selectcompute[status.question.fields[0].number])
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(pairlist)
                    for pair in pairlist:
                        if 'image' in pair:
                            if pair.get('color', None):
                                css_color = pair['color'].strip()
                            else:
                                css_color = 'light'
                            the_icon = '<div>' + icon_html(status, pair['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</div>'
                            btn_class = ' ' + BUTTON_STYLE + css_color + ' btn-da btn-da-custom'
                        else:
                            the_icon = ''
                            if pair.get('color', None):
                                btn_class = ' ' + BUTTON_STYLE + ' btn-' + pair['color'].strip()
                            else:
                                btn_class = ' ' + BUTTON_STYLE + continue_button_color
                        if pair.get('css class', None):
                            css_class = ' ' + pair['css class'].strip()
                        else:
                            css_class = ''
                        output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + css_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value=' + fix_double_quote(str(pair['key'])) + '>' + the_icon + markdown_to_html(pair['label'], status=status, trim=True, do_terms=False) + '</button>\n'
                else:
                    choicelist = status.selectcompute[status.question.fields[0].number]
                    # choicelist = list(status.question.fields[0].choices)
                    if hasattr(status.question.fields[0], 'shuffle') and status.question.fields[0].shuffle:
                        random.shuffle(choicelist)
                    for choice in choicelist:
                        if 'image' in choice:
                            if choice.get('color', None):
                                css_color = choice['color'].strip()
                            else:
                                css_color = 'light'
                            the_icon = '<span>' + icon_html(status, choice['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</span>'
                            btn_class = ' ' + BUTTON_STYLE + css_color + ' btn-da btn-da-custom'
                        else:
                            the_icon = ''
                            if choice.get('color', None):
                                btn_class = ' ' + BUTTON_STYLE + ' btn-' + choice['color'].strip()
                            else:
                                btn_class = ' ' + BUTTON_STYLE + continue_button_color
                        if choice.get('css class', None):
                            css_class = ' ' + choice['css class'].strip()
                        else:
                            css_class = ''
                        output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + css_class + '" name="' + escape_id(status.question.fields[0].saveas) + '" value=' + fix_double_quote(str(choice['key'])) + '>' + the_icon + markdown_to_html(choice['label'], status=status, trim=True, do_terms=False) + '</button>\n'
            else:
                indexno = 0
                for choice in status.selectcompute[status.question.fields[0].number]:
                    auto_color = True
                    if choice.get('css class', None):
                        css_class = ' ' + choice['css class'].strip()
                    else:
                        css_class = ''
                    if choice.get('color', None):
                        btn_class = ' ' + BUTTON_STYLE + ' btn-' + choice['color'].strip()
                        auto_color = False
                    else:
                        btn_class = ' ' + BUTTON_STYLE + continue_button_color
                    if 'image' in choice:
                        if choice.get('color', None):
                            css_color = choice['color'].strip()
                        else:
                            css_color = 'light'
                        the_icon = '<span>' + icon_html(status, choice['image'], width_value=BUTTON_ICON_SIZE, width_units=BUTTON_ICON_UNITS) + '</span>'
                        btn_class = ' ' + BUTTON_STYLE + css_color + ' btn-da btn-da-custom'
                    else:
                        the_icon = ''
                    if auto_color and isinstance(choice['key'], Question) and choice['key'].question_type in ("exit", "logout", "continue", "restart", "refresh", "signin", "register", "leave", "link", "new_session"):
                        if choice['key'].question_type == "continue":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR
                        elif choice['key'].question_type == "register":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_REGISTER
                        elif choice['key'].question_type == "new_session":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_NEW_SESSION
                        elif choice['key'].question_type == "leave":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_LEAVE
                        elif choice['key'].question_type == "link":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_URL
                        elif choice['key'].question_type == "restart":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_RESTART
                        elif choice['key'].question_type == "refresh":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_REFRESH
                        elif choice['key'].question_type == "signin":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_SIGNIN
                        elif choice['key'].question_type == "exit":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_EXIT
                        elif choice['key'].question_type == "logout":
                            btn_class = ' ' + BUTTON_STYLE + BUTTON_COLOR_LOGOUT
                    # output += '                  <input type="hidden" name="_event" value=' + myb64doublequote(json.dumps(list(status.question.fields_used))) + ' />\n'
                    output += '                  <button type="submit" class="btn ' + BUTTON_CLASS + btn_class + css_class + '" name="X211bHRpcGxlX2Nob2ljZQ" value="' + str(indexno) + '">' + the_icon + markdown_to_html(choice['label'], status=status, trim=True, do_terms=False, strip_newlines=True) + '</button>\n'
                    indexno += 1
            output += additional_buttons_after
            output += help_button
            output += '                </fieldset>\n'
        # output += question_name_tag(status.question)
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
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
            output += '                <div class="da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        if back_button != '' or help_button != '' or additional_buttons_after != '' or additional_buttons_before != '':
            output += status.submit
            output += '                <fieldset class="da-button-set da-field-buttons">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
            output += back_button + additional_buttons_before + additional_buttons_after + help_button + '</fieldset>\n'
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
    else:
        output += status.pre
        output += indent_by(audio_text, 12) + '            <form aria-labelledby="daMainQuestion" action="' + root + '" id="daform" class="form-horizontal daformcontinueother" method="POST">\n'
        output += '                <div class="da-page-header"><h1 class="h3" id="daMainQuestion">' + decoration_text + markdown_to_html(status.questionText, trim=True, status=status, strip_newlines=True) + '</h1><div class="daclear"></div></div>\n'
        if status.subquestionText:
            output += '                <div class="da-subquestion">\n' + markdown_to_html(status.subquestionText, status=status) + '                </div>\n'
        if video_text:
            output += indent_by(video_text, 12)
        output += status.submit
        output += '                <fieldset class="da-button-set da-field-buttons">\n                  <legend class="visually-hidden">' + word('Press one of the following buttons:') + '</legend>'
        output += back_button + additional_buttons_before + '\n                <button class="btn ' + BUTTON_CLASS + ' ' + BUTTON_STYLE + continue_button_color + '" type="submit">' + continue_label + '</button>' + additional_buttons_after + help_button + '\n                </fieldset>\n'
        # output += question_name_tag(status.question)
        output += help_button_area
        if showUnderText:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
        output += tracker_tag(status)
        output += '            </form>\n'
    if len(status.attachments) > 0:
        if not status.extras.get('manual_attachment_list', False):
            output += '            <br/>\n'
            if len(status.attachments) > 1:
                output += '            <h2 class="visually-hidden">' + word('Attachments') + "</h2>\n"
                if status.extras.get('attachment_notice', True):
                    output += '            <div class="da-attachment-alert da-attachment-alert-multiple alert alert-success" role="alert">' + word('The following documents have been created for you.') + '</div>\n'
            else:
                output += '            <h2 class="visually-hidden">' + word('Attachment') + "</h2>\n"
                if status.extras.get('attachment_notice', True):
                    output += '            <div class="da-attachment-alert da-attachment-alert-single alert alert-success" role="alert">' + word('The following document has been created for you.') + '</div>\n'
        attachment_index = 0
        editable_included = False
        automatically_include_editable = bool(status.extras.get('always_include_editable_files', False))
        editable_options = set()
        total_editable = 0
        for attachment in status.attachments:
            if 'rtf' in attachment['valid_formats'] or 'rtf to docx' in attachment['valid_formats'] or 'docx' in attachment['valid_formats'] or 'md' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    editable_included = True
                if 'md' in attachment['valid_formats']:
                    total_editable += 1
                    editable_options.add('MD')
                if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    total_editable += 1
                    editable_options.add('RTF')
                elif 'docx' in attachment['valid_formats'] or 'rtf to docx' in attachment['valid_formats']:
                    total_editable += 1
                    editable_options.add('DOCX')
            if status.extras.get('manual_attachment_list', False):
                continue
            if debug and len(attachment['markdown']):
                if 'html' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                    md_format = 'html'
                else:
                    for format_type in attachment['valid_formats']:
                        md_format = format_type
                        break
                show_markdown = bool(md_format in attachment['markdown'] and attachment['markdown'][md_format] != '')
            else:
                show_markdown = False
            # logmessage("markdown is " + str(attachment['markdown']))
            show_download = bool('pdf' in attachment['valid_formats'] or 'rtf' in attachment['valid_formats'] or 'rtf to docx' in attachment['valid_formats'] or 'docx' in attachment['valid_formats'] or 'md' in attachment['valid_formats'] or (debug and 'tex' in attachment['valid_formats']) or '*' in attachment['valid_formats'])
            show_preview = bool('html' in attachment['valid_formats'] or '*' in attachment['valid_formats'])
            multiple_formats = bool(len(attachment['valid_formats']) > 1 or '*' in attachment['valid_formats'])
            if attachment.get('raw', False):
                show_preview = False
                show_markdown = False
                show_download = True
                multiple_formats = False
            if not status.extras.get('download_tab', True):
                show_preview = False
                show_markdown = False
            output += '            <div class="da-attachment-title-wrapper"><h3>' + markdown_to_html(attachment['name'], trim=True, status=status, strip_newlines=True) + '</h3></div>\n'
            if attachment['description']:
                output += '            <div class="da-attachment-title-description">' + markdown_to_html(attachment['description'], status=status, strip_newlines=True) + '</div>\n'
            output += '            <div class="da-attachment-download-wrapper">\n'
            if status.extras.get('download_tab', True) or show_preview or show_markdown:
                output += '              <ul role="tablist" class="nav nav-tabs da-attachment-tablist">\n'
                if show_download:
                    output += '                <li class="nav-item da-attachment-tab-download-header"><a class="nav-link active" id="dadownload-tab' + str(attachment_index) + '" href="#dadownload' + str(attachment_index) + '" data-bs-toggle="tab" role="tab" aria-controls="dadownload' + str(attachment_index) + '" aria-selected="true">' + word('Download') + '</a></li>\n'
                if show_preview:
                    output += '                <li class="nav-item da-attachment-tab-preview-header"><a class="nav-link" id="dapreview-tab' + str(attachment_index) + '" href="#dapreview' + str(attachment_index) + '" data-bs-toggle="tab" role="tab" aria-controls="dapreview' + str(attachment_index) + '" aria-selected="false">' + word('Preview') + '</a></li>\n'
                if show_markdown:
                    output += '                <li class="nav-item da-attachment-tab-markdown-header"><a class="nav-link" id="damarkdown-tab' + str(attachment_index) + '" href="#damarkdown' + str(attachment_index) + '" data-bs-toggle="tab" role="tab" aria-controls="damarkdown' + str(attachment_index) + '" aria-selected="false">' + word('Markdown') + '</a></li>\n'
                output += '              </ul>\n'
            output += '              <div class="tab-content" id="databcontent' + str(attachment_index) + '">\n'
            if show_download:
                if status.extras.get('download_tab', True) or show_preview or show_markdown:
                    output += '                <div class="tab-pane show active da-attachment-tab-download" id="dadownload' + str(attachment_index) + '" role="tabpanel" aria-labelledby="dadownload-tab' + str(attachment_index) + '">\n'
                else:
                    output += '                <div>\n'
                if multiple_formats:
                    output += '                  <p class="da-attachment-tab-download-intro">' + word('The document is available in the following formats:') + '</p>\n'
                if attachment.get('raw', False):
                    output += '                  <p class="da-attachment-tab-download-raw"><a href="' + server.url_finder(attachment['file']['raw'], display_filename=attachment['filename'] + attachment['raw']) + '" target="_blank"><i class="fas fa-code fa-fw"></i> ' + attachment['filename'] + attachment['raw'] + '</a> (' + word('for downloading') + ')</p>\n'
                else:
                    if 'pdf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                        output += '                  <p class="da-attachment-tab-download-pdf"><a href="' + server.url_finder(attachment['file']['pdf'], display_filename=attachment['filename'] + '.pdf') + '" target="_blank"><i class="fas fa-print fa-fw"></i> PDF</a> (' + word('for printing; requires Adobe Reader or similar application') + ')</p>\n'
                    if 'rtf' in attachment['valid_formats'] or '*' in attachment['valid_formats']:
                        output += '                  <p class="da-attachment-tab-download-rtf"><a href="' + server.url_finder(attachment['file']['rtf'], display_filename=attachment['filename'] + '.rtf') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> RTF</a> (' + word('for editing; requires Microsoft Word, Wordpad, or similar application') + ')</p>\n'
                    if 'docx' in attachment['valid_formats']:
                        output += '                  <p class="da-attachment-tab-download-docx"><a href="' + server.url_finder(attachment['file']['docx'], display_filename=attachment['filename'] + '.docx') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> DOCX</a> (' + word('for editing; requires Microsoft Word or compatible application') + ')</p>\n'
                    if 'rtf to docx' in attachment['valid_formats']:
                        output += '                  <p class="da-attachment-tab-download-docx"><a href="' + server.url_finder(attachment['file']['rtf to docx'], display_filename=attachment['filename'] + '.docx') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> DOCX</a> (' + word('for editing; requires Microsoft Word or compatible application') + ')</p>\n'
                    if 'tex' in attachment['valid_formats']:
                        output += '                  <p class="da-attachment-tab-download-tex"><a href="' + server.url_finder(attachment['file']['tex'], display_filename=attachment['filename'] + '.tex') + '" target="_blank"><i class="fas fa-pencil-alt fa-fw"></i> LaTeX</a> (' + word('for debugging PDF output') + ')</p>\n'
                    if 'md' in attachment['valid_formats']:
                        output += '                  <p class="da-attachment-tab-download-md"><a href="' + server.url_finder(attachment['file']['md'], display_filename=attachment['filename'] + '.md') + '" target="_blank"><i class="fab fa-markdown fa-fw"></i> Markdown</a></p>\n'
                output += '                </div>\n'
            if show_preview:
                output += '                <div class="tab-pane da-attachment-tab-preview" id="dapreview' + str(attachment_index) + '" role="tabpanel" aria-labelledby="dapreview-tab' + str(attachment_index) + '">\n'
                output += '                  <blockquote class="blockquote">' + str(attachment['content']['html']) + '</blockquote>\n'
                output += '                </div>\n'
            if show_markdown:
                output += '                <div class="tab-pane da-attachment-tab-markdown" id="damarkdown' + str(attachment_index) + '" role="tabpanel" aria-labelledby="damarkdown-tab' + str(attachment_index) + '">\n'
                output += '                  <pre class="mb-2 mt-2">' + safe_html(attachment['markdown'][md_format]) + '</pre>\n'
                output += '                </div>\n'
            output += '              </div>\n            </div>\n'
            attachment_index += 1
        if editable_included:
            if 'RTF' in editable_options and 'DOCX' in editable_options:
                editable_name = word('Include RTF and DOCX files for editing')
            elif 'RTF' in editable_options and 'MD' in editable_options:
                editable_name = word('Include RTF and Markdown files for editing')
            elif 'DOCX' in editable_options and 'MD' in editable_options:
                editable_name = word('Include DOCX and Markdown files for editing')
            elif 'RTF' in editable_options:
                if total_editable > 1:
                    editable_name = word('Include RTF files for editing')
                else:
                    editable_name = word('Include RTF file for editing')
            elif 'DOCX' in editable_options:
                if total_editable > 1:
                    editable_name = word('Include DOCX files for editing')
                else:
                    editable_name = word('Include DOCX file for editing')
            elif 'MD' in editable_options:
                if total_editable > 1:
                    editable_name = word('Include Markdown files for editing')
                else:
                    editable_name = word('Include Markdown file for editing')
            else:
                editable_name = ''
        if status.extras.get('allow_emailing', True) or status.extras.get('allow_downloading', False):
            if len(status.attachments) > 1:
                email_header = word("E-mail these documents")
                download_header = word("Download all documents as a ZIP file")
            else:
                email_header = word("E-mail this document")
                download_header = word("Download this document as a ZIP file")
            if status.extras.get('allow_emailing', True):
                if status.extras.get('email_default', None):
                    default_email = status.extras['email_default']
                elif status.current_info['user']['is_authenticated'] and status.current_info['user']['email']:
                    default_email = status.current_info['user']['email']
                else:
                    default_email = ''
                output += """\
            <div class="da-attachment-email-all">
              <div class="card mb-2">
                <div class="card-header" id="daheadingOne">
                  <span>""" + email_header + """</span>
                </div>
                <div aria-labelledby="daheadingOne">
                  <div class="card-body">
                    <form aria-labelledby="daheadingOne" action=\"""" + root + """\" id="daemailform" class="form-horizontal" method="POST">
                      <input type="hidden" name="_question_name" value=""" + json.dumps(status.question.name, ensure_ascii=False) + """/>
                      <div class="da-form-group row"><label for="da_attachment_email_address" class="col-""" + daconfig['grid classes']['label width'] + """ col-form-label da-form-label datext-right">""" + word('E-mail address') + """</label><div class="col-""" + daconfig['grid classes']['field width'] + """"><input alt=""" + fix_double_quote(word("Input box")) + """ class="form-control" type="email" name="_attachment_email_address" id="da_attachment_email_address" value=""" + fix_double_quote(str(default_email)) + """/></div></div>"""
                if editable_included:
                    if automatically_include_editable:
                        output += """
                      <input type="hidden" value="True" name="_attachment_include_editable" id="da_attachment_include_editable"/>"""
                    else:
                        output += """
                      <div class="row da-form-group"><div class="offset-""" + daconfig['grid classes']['label width'] + """ col-""" + daconfig['grid classes']['field width'] + """"><div class="form-check"><input class="form-check-input" alt=""" + fix_double_quote(word("Check box") + ", " + editable_name) + """ type="checkbox" value="True" name="_attachment_include_editable" id="da_attachment_include_editable"/><label for="da_attachment_include_editable" class="danobold form-check-label">""" + editable_name + '</label></div></div></div>\n'
                output += """
                      <button class="btn """ + BUTTON_STYLE + BUTTON_COLOR_SEND + """" type="submit">""" + word('Send') + '</button>\n                      <input type="hidden" name="_email_attachments" value="1"/>'
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
            <div class="da-attachment-download-all">
              <div class="card">
                <div class="card-header" id="daheadingTwo">
                  <span>""" + download_header + """</span>
                </div>
                <div aria-labelledby="daheadingTwo">
                  <div class="card-body">
                    <form aria-labelledby="daheadingTwo" action=\"""" + root + """\" id="dadownloadform" class="form-horizontal" method="POST">
                      <input type="hidden" name="_question_name" value=""" + json.dumps(status.question.name, ensure_ascii=False) + """/>"""
                if editable_included:
                    if automatically_include_editable:
                        output += """
                      <input type="hidden" value="True" name="_attachment_include_editable" id="da_attachment_include_editable"/>"""
                    else:
                        output += """
                      <div class="da-form-group row"><div class="col"><input alt=""" + fix_double_quote(word("Check box") + ", " + editable_name) + """ type="checkbox" value="True" name="_attachment_include_editable" id="da_attachment_include_editable"/>&nbsp;<label for="da_attachment_include_editable" class="danobold form-label">""" + editable_name + '</label></div></div>\n'
                output += """
                      <button class="btn """ + BUTTON_STYLE + BUTTON_COLOR_DOWNLOAD + """" type="submit">""" + word('Download All') + '</button>\n                      <input type="hidden" name="_download_attachments" value="1"/>'
                output += """
                      <input type="hidden" name="csrf_token" value=""" + json.dumps(server.generate_csrf()) + """/>
                    </form>
                  </div>
                </div>
              </div>
            </div>
"""
        output += help_button_area
        if 'underText' in status.extras:
            output += markdown_to_html(status.extras['underText'], status=status, divclass="daundertext")
    if status.question.question_type == "signature":
        output += '<div class="dasigpost">' + status.post + '</div>'
        # if len(status.attributions):
        #     output += '            <br/><br/><br/><br/><br/><br/><br/>\n'
        # for attribution in sorted(status.attributions):
        #     output += '            <div><cite><small>' + markdown_to_html(attribution, status=status, strip_newlines=True) + '</small></cite></div>\n'
    if debug or status.using_screen_reader:
        status.screen_reader_text['question'] = str(output)
    if 'rightText' in status.extras:
        if status.using_navigation == 'vertical':
            output += '            <div id="darightbottom" class="' + daconfig['grid classes']['vertical navigation']['right small screen'] + ' daright">\n'
        else:
            if status.flush_left():
                output += '            <div id="darightbottom" class="' + daconfig['grid classes']['flush left']['right small screen'] + ' daright">\n'
            else:
                output += '            <div id="darightbottom" class="' + daconfig['grid classes']['centered']['right small screen'] + ' daright">\n'
        output += markdown_to_html(status.extras['rightText'], trim=False, status=status) + "\n"
        output += '            </div>\n'
    master_output += output
    master_output += '          </div>\n'
    master_output += '          <div id="dahelp" role="tabpanel" aria-labelledby="dahelptoggle" class="tab-pane fade ' + grid_class + '">\n'
    output = str() + '            <div class="mt-2 mb-2"><button id="dabackToQuestion" class="btn ' + BUTTON_STYLE + BUTTON_COLOR_BACK_TO_QUESTION + '"><i class="fas fa-chevron-left"></i> ' + word("Back to question") + '</button></div>'
    output += """
            <div id="daPhoneMessage" class="row dainvisible">
              <div class="col">
                <h1 class="h3">""" + word("Telephone assistance") + """</h1>
                <p></p>
              </div>
            </div>
            <div id="daChatBox" class="dainvisible">
              <div class="row">
                <div class="col dachatbutton">
                  <a href="#" id="daChatOnButton" role="button" class="btn """ + BUTTON_STYLE + """success">""" + word("Activate chat") + """</a>
                  <a href="#" id="daChatOffButton" role="button" class="btn """ + BUTTON_STYLE + """warning">""" + word("Turn off chat") + """</a>
                  <h1 class="h3" id="dachatHeading">""" + word("Live chat") + """</h1>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <ul class="list-group dachatbox" id="daCorrespondence"></ul>
                </div>
              </div>
              <form aria-labelledby="dachatHeading" id="dachat" autocomplete="off">
                <div class="row">
                  <div class="col">
                    <div class="input-group">
                      <label for="daMessage" class="visually-hidden">""" + word("Chat message you want to send") + """</label>
                      <input type="text" class="form-control daChatMessage" id="daMessage" placeholder=""" + fix_double_quote(word("Type your message here.")) + """>
                      <button class="btn """ + BUTTON_STYLE + """secondary daChatButton" id="daSend" type="button">""" + word("Send") + """</button>
                    </div>
                  </div>
                </div>
              </form>
              <div class="row dainvisible">
                <div class="col">
                  <p id="daPushResult"></p>
                </div>
              </div>
              <div class="row datopspace">
                <div class="col">
                  <p>
                    <span class="da-peer-message" id="dapeerMessage"></span>
                    <span class="da-peer-message" id="dapeerHelpMessage"></span>
                  </p>
                </div>
              </div>
            </div>
"""
    if len(status.interviewHelpText) > 0 or (len(status.helpText) > 0 and not status.question.interview.question_help_button):
        if status.using_screen_reader and 'help' in status.screen_reader_links:
            output += '            <div class="daaudiovideo-control">\n' + indent_by(audio_control(status.screen_reader_links['help'], preload="none", title_text=word('Read this screen out loud')), 14) + '            </div>\n'
        if status.question.interview.question_help_button:
            help_parts = status.interviewHelpText
        else:
            help_parts = status.helpText + status.interviewHelpText
        for help_section in help_parts:
            output += process_help(help_section, status)
        # if len(status.attributions):
        #     output += '            <br/><br/><br/><br/><br/><br/><br/>\n'
        # for attribution in sorted(status.attributions):
        #     output += '            <div><cite><small>' + markdown_to_html(attribution, status=status, strip_newlines=True) + '</small></cite></div>\n'
        if debug or status.using_screen_reader:
            status.screen_reader_text['help'] = str(output)
    master_output += output
    master_output += '          </div>\n'
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
          var id_list = JSON.parse(decodeURIComponent(escape(atob($(this).data('disableothers')))));
          n = id_list.length;
        }
        if (n){
          for(var i = 0; i < n; ++i){
            var the_element_id = id_list[i].replace(/(:|\.|\[|\]|,|=)/g, "\\\\$1");
            if (theVal == null || theVal == ""){
              daDisableIfNotHidden("#daform [name='" + the_element_id + "']:not([type=hidden])", false);
              $("#daform [name='" + the_element_id + "']:not([type=hidden])").parents(".da-form-group").removeClass("dagreyedout");
            }
            else{
              daDisableIfNotHidden("#daform [name='" + the_element_id + "']:not([type=hidden])", true);
              $("#daform [name='" + the_element_id + "']:not([type=hidden])").parents(".da-form-group").addClass("dagreyedout");
            }
          }
        }
        else{
          if (theVal == null || theVal == ""){
            daDisableIfNotHidden("#daform input:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])", false);
            daDisableIfNotHidden("#daform select:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])", false);
            daDisableIfNotHidden("#daform textarea:not([name='""" + element_id + """']):not([type=hidden])", false);
            $("#daform input:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])").parents(".da-form-group").removeClass("dagreyedout");
            $("#daform select:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])").parents(".da-form-group").removeClass("dagreyedout");
            $("#daform textarea:not([name='""" + element_id + """']):not([type=hidden])").parents(".da-form-group").removeClass("dagreyedout");
          }
          else{
            $("#daform input:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])").prop("disabled", true);
            $("#daform select:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])").prop("disabled", true);
            $("#daform textarea:not([name='""" + element_id + """']):not([type=hidden])").prop("disabled", true);
            $("#daform input:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])").parents(".da-form-group").addClass("dagreyedout");
            $("#daform select:not([name='""" + element_id + """']):not([id^='""" + element_id + """']):not([type=hidden])").parents(".da-form-group").addClass("dagreyedout");
            $("#daform textarea:not([name='""" + element_id + """']):not([type=hidden])").parents(".da-form-group").addClass("dagreyedout");
          }
        }
      });
      $("[data-disableothers]").trigger('change');
    </script>
"""  # noqa: W605
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
    if len(autocomplete_info) > 0:
        status.extra_scripts.append("""
<script>
  daInitAutocomplete(""" + json.dumps(autocomplete_info) + """);
</script>
""")
    if len(status.maps) > 0:
        status.extra_scripts.append("""
<script>
  daInitMap([""" + ", ".join(status.maps) + """]);
</script>
""")
        # google_config = daconfig.get('google', {})
        # if 'google maps api key' in google_config:
        #     api_key = google_config.get('google maps api key')
        # elif 'api key' in google_config:
        #     api_key = google_config.get('api key')
        # else:
        #     raise Exception('google API key not provided')
        # status.extra_scripts.append('<script async defer src="https://maps.googleapis.com/maps/api/js?key=' + urllibquote(api_key) + '&callback=daInitMap"></script>')
    return master_output


def add_validation(extra_scripts, validation_rules, field_error):
    if field_error is None:
        error_show = ''
    else:
        error_mess = {}
        for key, val in field_error.items():
            error_mess[key] = val
        error_show = "\n    daValidator.showErrors(" + json.dumps(error_mess) + ");"
    extra_scripts.append("""<script>
  var daValidationRules = """ + json.dumps(validation_rules) + """;
  daValidationRules.submitHandler = daValidationHandler;
  daValidationRules.invalidHandler = daInvalidHandler;
  daValidationRules.onfocusout = daInjectTrim($.validator.defaults.onfocusout);
  if ($("#daform").length > 0){
    var daValidator = $("#daform").validate(daValidationRules);""" + error_show + """
  }
</script>""")


def locale_format_string(the_value):
    return re.sub(r'[^0-9]$', '', locale.format_string('%.10f', float(the_value), grouping=False).rstrip('0'))


def double_to_single_newline(text):
    text = re.sub(r'\n\n', 'XXXNEWLINEXXX', text)
    text = text.replace('\n', ' ')
    text = text.replace('XXXNEWLINEXXX', '\n')
    return text


def input_for(status, field, wide=False, embedded=False, floating_label=None):
    output = str()
    if field.number in status.defaults:
        defaultvalue_set = True
        if hasattr(field, 'datatype') and field.datatype in custom_types:
            try:
                defaultvalue = custom_types[field.datatype]['class'].default_for(status.defaults[field.number])
            except:
                defaultvalue_set = False
                defaultvalue = None
        elif isinstance(status.defaults[field.number], (str, int, float)):
            defaultvalue = str(status.defaults[field.number])
        elif isinstance(status.defaults[field.number], list):
            defaultvalue = []
            for item in status.defaults[field.number]:
                if hasattr(item, 'instanceName'):
                    defaultvalue.append(safeid(item.instanceName))
                else:
                    defaultvalue.append(item)
        else:
            defaultvalue = status.defaults[field.number]
        if not isinstance(defaultvalue, (list, NoneType, datetime.datetime, datetime.date, datetime.time, int, float)) and (defaultvalue.__class__.__name__ == 'DAEmpty' or (not hasattr(defaultvalue, 'instanceName') and str(defaultvalue).strip() == '')):
            defaultvalue_set = False
            defaultvalue = None
    else:
        defaultvalue_set = False
        defaultvalue = None
    if field.number in status.hints:
        if hasattr(field, 'inputtype') and field.inputtype == 'area':
            placeholdertext = ' placeholder=' + fix_double_quote(double_to_single_newline(status.hints[field.number]))
        else:
            placeholdertext = ' placeholder=' + fix_double_quote(status.hints[field.number].replace('\n', ' '))
    elif floating_label is not None:
        placeholdertext = ' placeholder=' + fix_double_quote(floating_label.replace('\n', ' '))
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
    if status.extras['required'][field.number]:
        req_attr = ' required'
        req_aria = ' aria-required="true"'
    else:
        req_attr = ''
        req_aria = ''
    if embedded:
        extra_class = ' dainput-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'date':
            extra_class += ' dadate-embedded'
        if hasattr(field, 'datatype') and field.datatype == 'time':
            extra_class += ' datime-embedded'
        if hasattr(field, 'datatype') and field.datatype in ['datetime', 'datetime-local']:
            extra_class += ' dadate-embedded'
        if inline_width is not None:
            extra_style = ' style="min-width: ' + str(inline_width) + '"'
        else:
            extra_style = ''
        extra_checkbox = ' dacheckbox-embedded'
        extra_radio = 'daradio-embedded'
        if field.number in status.labels:
            label_text = strip_quote(to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), {}, []).strip())
        else:
            label_text = 'no label'
        if label_text != 'no label':
            title_text = ' title=' + fix_double_quote(str(label_text))
        else:
            title_text = ''
        if hasattr(field, 'datatype') and field.datatype == 'object':
            extra_class += ' daobject'
    else:
        extra_style = ''
        if hasattr(field, 'datatype') and field.datatype == 'object':
            extra_class = ' daobject'
        else:
            extra_class = ''
        extra_checkbox = ''
        extra_radio = ''
        title_text = ''
    if field.datatype == 'password':
        autocomplete_off = ' autocomplete="new-password"'
    else:
        autocomplete_off = ''
    if 'css class' in status.extras and field.number in status.extras['css class']:
        extra_class += ' ' + clean_whitespace(status.extras['css class'][field.number])
    is_hidden = hasattr(field, 'inputtype') and field.inputtype == 'hidden'
    if hasattr(field, 'choicetype') and not is_hidden:
        if field.choicetype in ['compute', 'manual']:
            pairlist = list(status.selectcompute[field.number])
        else:
            raise Exception("Unknown choicetype " + field.choicetype)
        using_opt_groups = all('group' in pair for pair in pairlist)
        using_shuffle = hasattr(field, 'shuffle') and field.shuffle
        # Using optgroups, each option has an associated group
        if using_opt_groups:
            # Keep groups and group items in same relative order they're added in interview
            # or shuffle the groups, and items w/in groups, but keep items in same groups together
            group_order = list(range(len(pairlist)))
            if using_shuffle:
                random.shuffle(group_order)
            groups = {}
            for idx, p in zip(group_order, pairlist):
                if not p.get('group') in groups:
                    groups[p.get('group')] = idx

            if using_shuffle:
                pairlist = sorted(pairlist, key=lambda p: (groups[p.get('group')], random.random()))
            else:
                pairlist = sorted(pairlist, key=lambda p: groups[p.get('group')])
        elif using_shuffle:
            random.shuffle(pairlist)

        if field.datatype in ['multiselect', 'object_multiselect']:
            if field.datatype == 'object_multiselect':
                daobject = ' damultiselect daobject'
            else:
                daobject = ' damultiselect'
            if embedded:
                emb_text = 'class="dainput-embedded' + daobject + '" '
                if inline_width is not None:
                    emb_text += 'style="min-width: ' + str(inline_width) + '" '
                label_text = strip_quote(to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), {}, []).strip())
                if label_text != 'no label':
                    emb_text += 'title=' + fix_double_quote(str(label_text)) + ' '
            else:
                output += '<p class="visually-hidden">' + word('Multiselect box') + '</p>'
                emb_text = 'class="form-control' + daobject + '" '
            if 'rows' in status.extras and field.number in status.extras['rows']:
                emb_text += 'size=' + noquote(str(status.extras['rows'][field.number])) + ' '
            emb_text += 'data-varname=' + myb64doublequote(from_safeid(field.saveas)) + ' '
            if embedded:
                output += '<span class="da-inline-error-wrapper">'
            output += '<select ' + emb_text + 'name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + disable_others_data + req_attr + ' multiple>'
            the_options = ''
            last_group = None
            for pair in pairlist:
                if using_opt_groups and pair.get('group') != last_group:
                    if last_group is not None:
                        the_options += '</optgroup>'
                    pair_group = pair.get('group')
                    the_options += f'<optgroup label="{pair_group}">'
                    last_group = pair_group
                if isinstance(pair['key'], str):
                    inner_field = safeid(from_safeid(saveas_string) + "[B" + myb64quote(pair['key']) + "]")
                    key_data = ' data-valname=' + myb64doublequote(pair['key'])
                else:
                    inner_field = safeid(from_safeid(saveas_string) + "[R" + myb64quote(repr(pair['key'])) + "]")
                    key_data = ' data-valname=' + myb64doublequote(repr(pair['key']))
                def_key = from_safeid(saveas_string) + "[" + repr(pair['key']) + "]"
                if def_key in status.other_defaults and status.other_defaults[def_key]:
                    isselected = ' selected="selected"'
                elif 'default' in pair and pair['default']:
                    isselected = ' selected="selected"'
                elif defaultvalue is None:
                    isselected = ''
                elif isinstance(defaultvalue, (list, set)) and str(pair['key']) in defaultvalue:
                    isselected = ' selected="selected"'
                elif isinstance(defaultvalue, dict) and str(pair['key']) in defaultvalue and defaultvalue[str(pair['key'])]:
                    isselected = ' selected="selected"'
                elif (hasattr(defaultvalue, 'elements') and isinstance(defaultvalue.elements, dict)) and str(pair['key']) in defaultvalue.elements and defaultvalue.elements[str(pair['key'])]:
                    isselected = ' selected="selected"'
                elif pair['key'] is defaultvalue:
                    isselected = ' selected="selected"'
                elif isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue):
                    isselected = ' selected="selected"'
                else:
                    isselected = ''
                if pair.get('css class', None):
                    css_class = ' class="' + pair['css class'].strip() + '"'
                else:
                    css_class = ''
                the_options += '<option value=' + fix_double_quote(inner_field) + key_data + isselected + css_class + '>' + markdown_to_html(str(pair['label']), status=status, escape='option', trim=True, do_terms=False) + '</option>'
            if using_opt_groups:
                the_options += '</optgroup>'
            output += the_options
            if embedded:
                output += '</select></span> '
            else:
                output += '</select> '
            if field.datatype in ['object_multiselect']:
                output += '<input type="hidden" name="' + safeid(from_safeid(field.saveas) + ".gathered") + '" value="True"' + disable_others_data + '/>'
        elif field.datatype in ['checkboxes', 'object_checkboxes']:
            # if len(pairlist) == 0:
            #    return '<input type="hidden" name="' + safeid(from_safeid(saveas_string))+ '" value="None"/>'
            inner_fieldlist = []
            id_index = 0
            if embedded:
                output += '<span class="da-embed-checkbox-wrapper">'
            else:
                if req_aria:
                    legend_text = 'Checkboxes (select at least one):'
                else:
                    legend_text = 'Checkboxes:'
                output += '<fieldset class="da-field-checkboxes" role="group"><legend class="visually-hidden">' + word(legend_text) + '</legend>'
            for pair in pairlist:
                if 'image' in pair:
                    the_icon = icon_html(status, pair['image']) + ' '
                else:
                    the_icon = ''
                if pair.get('css class', None):
                    css_class = ' ' + pair['css class'].strip()
                else:
                    css_class = ''
                if pair.get('color', None):
                    css_color = pair['color'].strip()
                else:
                    css_color = DEFAULT_LABELAUTY_COLOR
                helptext = pair.get('help', None)
                if isinstance(pair['key'], str):
                    inner_field = safeid(from_safeid(saveas_string) + "[B" + myb64quote(pair['key']) + "]")
                else:
                    inner_field = safeid(from_safeid(saveas_string) + "[R" + myb64quote(repr(pair['key'])) + "]")
                # logmessage("I've got a " + repr(pair['label']))
                formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                def_key = from_safeid(saveas_string) + "[" + repr(pair['key']) + "]"
                if def_key in status.other_defaults and status.other_defaults[def_key]:
                    ischecked = ' checked'
                elif 'default' in pair and pair['default']:
                    ischecked = ' checked'
                elif defaultvalue is None:
                    ischecked = ''
                elif isinstance(defaultvalue, (list, set)) and str(pair['key']) in defaultvalue:
                    ischecked = ' checked'
                elif isinstance(defaultvalue, dict) and str(pair['key']) in defaultvalue and defaultvalue[str(pair['key'])]:
                    ischecked = ' checked'
                elif (hasattr(defaultvalue, 'elements') and isinstance(defaultvalue.elements, dict)) and str(pair['key']) in defaultvalue.elements and defaultvalue.elements[str(pair['key'])]:
                    ischecked = ' checked'
                elif pair['key'] is defaultvalue:
                    ischecked = ' checked'
                elif isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue):
                    ischecked = ' checked'
                else:
                    ischecked = ''
                if embedded:
                    inner_fieldlist.append('<input aria-label="' + formatted_item + '" class="dacheckbox-embedded dafield' + str(field.number) + ' danon-nota-checkbox' + css_class + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"' + ischecked + disable_others_data + '/>&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '_' + str(id_index) + '" />' + the_icon + formatted_item + '</label>')
                else:
                    inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + css_color + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="' + 'dafield' + str(field.number) + ' danon-nota-checkbox da-to-labelauty checkbox-icon' + extra_checkbox + css_class + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + inner_field + '" type="checkbox" value="True"' + ischecked + disable_others_data + ' />', helptext, status))
                id_index += 1
            if 'nota' in status.extras and field.number in status.extras['nota'] and status.extras['nota'][field.number] is not False:
                if defaultvalue_set and defaultvalue is None:
                    ischecked = ' checked'
                else:
                    ischecked = ''
                if status.extras['nota'][field.number] is True:
                    formatted_item = word("None of the above")
                else:
                    formatted_item = markdown_to_html(str(status.extras['nota'][field.number]), status=status, trim=True, escape=(not embedded), do_terms=False)
                if embedded:
                    inner_fieldlist.append('<input class="dafield' + str(field.number) + ' dacheckbox-embedded danota-checkbox" id="_ignore' + str(field.number) + '" type="checkbox" name="_ignore' + str(field.number) + '"' + disable_others_data + '/>&nbsp;<label class="form-label" for="_ignore' + str(field.number) + '">' + formatted_item + '</label>')
                else:
                    inner_fieldlist.append('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + DEFAULT_LABELAUTY_NOTA_COLOR + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="' + 'dafield' + str(field.number) + ' danota-checkbox da-to-labelauty checkbox-icon' + extra_checkbox + '"' + title_text + ' type="checkbox" name="_ignore' + str(field.number) + '" ' + ischecked + disable_others_data + '/>')
            elif hasattr(field, 'extras') and (('minlength' in field.extras and 'minlength' in status.extras and field.number in status.extras['minlength']) or ('maxlength' in field.extras and 'maxlength' in status.extras and field.number in status.extras['maxlength'])):
                inner_fieldlist.append('<input value="" type="hidden" name="_ignore' + str(field.number) + '"/>')
            if embedded:
                output += ' '.join(inner_fieldlist) + '</span>'
            else:
                output += ''.join(inner_fieldlist)
            output += '</fieldset>'
            if field.datatype in ['object_checkboxes']:
                output += '<input type="hidden" name="' + safeid(from_safeid(field.saveas) + ".gathered") + '" value="True"' + disable_others_data + '/>'
        elif field.datatype == 'object_radio' or (hasattr(field, 'inputtype') and field.inputtype == 'radio'):
            if field.datatype in ('object_radio', 'object'):
                daobject = ' daobject'
            else:
                daobject = ''
            inner_fieldlist = []
            id_index = 0
            try:
                defaultvalue_printable = str(defaultvalue)
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
                    if pair.get('css class', None):
                        css_class = ' ' + pair['css class'].strip()
                    else:
                        css_class = ''
                    formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and defaultvalue_printable and str(pair['label']) == defaultvalue_printable) or (hasattr(field, 'datatype') and field.datatype in ('object_radio', 'object') and defaultvalue is not None and hasattr(defaultvalue, 'instanceName') and safeid(defaultvalue.instanceName) == pair['key']) or (defaultvalue_set and defaultvalue is None and str(pair['key']) == 'None'):
                        ischecked = ' checked="checked"'
                        default_selected = True
                    else:
                        ischecked = ''
                    inner_fieldlist.append('<input class="daradio-embedded' + css_class + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                    id_index += 1
                if 'nota' in status.extras and field.number in status.extras['nota'] and status.extras['nota'][field.number] is not False:
                    if status.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = markdown_to_html(str(status.extras['nota'][field.number]), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if not default_selected:
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    the_icon = ''
                    inner_fieldlist.append('<input class="daradio-embedded' + daobject + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value="" checked="checked"' + disable_others_data + ' />&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + the_icon + formatted_item + '</label>')
                output += '<span class="da-embed-radio-wrapper">'
                output += " ".join(inner_fieldlist)
                output += '</span>'
            else:
                default_selected = False
                output += '<fieldset class="da-field-radio" role="radiogroup"' + req_aria + '><legend class="visually-hidden">' + word('Choices:') + '</legend>'
                for pair in pairlist:
                    if 'image' in pair:
                        the_icon = icon_html(status, pair['image']) + ' '
                    else:
                        the_icon = ''
                    if pair.get('css class', None):
                        css_class = ' ' + pair['css class'].strip()
                    else:
                        css_class = ''
                    if pair.get('color', None):
                        css_color = pair['color'].strip()
                    else:
                        css_color = DEFAULT_LABELAUTY_COLOR
                    helptext = pair.get('help', None)
                    # logmessage(str(saveas_string))
                    formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == defaultvalue_printable) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and defaultvalue_is_printable and str(pair['label']) == defaultvalue_printable) or (hasattr(field, 'datatype') and field.datatype in ('object_radio', 'object') and defaultvalue is not None and hasattr(defaultvalue, 'instanceName') and safeid(defaultvalue.instanceName) == pair['key']) or (defaultvalue_set and defaultvalue is None and str(pair['key']) == 'None'):
                        ischecked = ' checked="checked"'
                        default_selected = True
                    else:
                        ischecked = ''
                    inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + css_color + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + daobject + extra_radio + css_class + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />', helptext, status))
                    id_index += 1
                if 'nota' in status.extras and field.number in status.extras['nota'] and status.extras['nota'][field.number] is not False:
                    if status.extras['nota'][field.number] is True:
                        formatted_item = word("None of the above")
                    else:
                        formatted_item = markdown_to_html(str(status.extras['nota'][field.number]), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if not default_selected:
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    the_icon = ''
                    helptext = None
                    inner_fieldlist.append(help_wrap('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + DEFAULT_LABELAUTY_NOTA_COLOR + '" data-labelauty="' + my_escape(the_icon) + formatted_item + '|' + my_escape(the_icon) + formatted_item + '" class="da-to-labelauty' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=""' + ischecked + disable_others_data + ' />', helptext, status))
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
            if hasattr(field, 'inputtype') and field.inputtype == 'combobox' and defaultvalue:
                datadefault = ' data-default=' + fix_double_quote(str(defaultvalue))
            else:
                datadefault = ''
            if embedded:
                emb_text = 'class="dainput-embedded' + daobject + '" '
                if inline_width is not None:
                    emb_text += 'style="min-width: ' + str(inline_width) + '" '
                label_text = strip_quote(to_text(markdown_to_html(status.labels[field.number], trim=False, status=status, strip_newlines=True), {}, []).strip())
                if label_text != 'no label':
                    emb_text += 'title=' + fix_double_quote(str(label_text)) + ' '
            else:
                output += '<p class="visually-hidden">' + word('Select box') + '</p>'
                if hasattr(field, 'inputtype') and field.inputtype == 'combobox':
                    emb_text = 'class="form-control dasingleselect combobox' + daobject + '" '
                else:
                    emb_text = 'class="form-select dasingleselect' + daobject + '" '
            if embedded:
                output += '<span class="da-inline-error-wrapper">'
            output += '<select ' + emb_text + 'name="' + escape_id(saveas_string) + '"' + datadefault + ' id="' + escape_id(saveas_string) + '" ' + disable_others_data + req_attr + '>'
            first_option = ''
            if hasattr(field, 'inputtype') and field.inputtype == 'combobox' and not embedded:
                if placeholdertext == '':
                    first_option += '<option value="">' + option_escape(word('Select one')) + '</option>'
                else:
                    first_option += '<option value="">' + option_escape(str(status.hints[field.number].replace('\n', ' '))) + '</option>'
            else:
                if placeholdertext == '':
                    first_option += '<option value="">' + option_escape(word('Select...')) + '</option>'
                else:
                    first_option += '<option value="">' + option_escape(str(status.hints[field.number].replace('\n', ' '))) + '</option>'
            try:
                defaultvalue_printable = str(defaultvalue)
                defaultvalue_is_printable = True
            except:
                defaultvalue_printable = None
                defaultvalue_is_printable = False
            # logmessage("defaultvalue is " + repr(defaultvalue))
            # logmessage("defaultvalue_printable is " + repr(defaultvalue_printable))
            # logmessage("defaultvalue_is_printable is " + repr(defaultvalue_is_printable))
            found_default = False
            other_options = ''
            last_group = None
            for pair in pairlist:
                if using_opt_groups and pair.get('group') != last_group:
                    if last_group is not None:
                        other_options += '</optgroup>'
                    pair_group = pair.get('group')
                    other_options += f'<optgroup label="{pair_group}">'
                    last_group = pair_group
                if pair.get('css class', None):
                    css_class = ' class="' + pair['css class'].strip() + '"'
                else:
                    css_class = ''
                if pair.get('color', None):
                    css_color = pair['color'].strip()
                else:
                    css_color = DEFAULT_LABELAUTY_COLOR
                other_options += '<option value=' + fix_double_quote(str(pair['key']))
                if ('default' in pair and pair['default']) or \
                   (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == defaultvalue_printable) or \
                   (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and defaultvalue_is_printable and str(pair['label']) == defaultvalue_printable) or \
                   (hasattr(field, 'datatype') and field.datatype == 'object' and defaultvalue is not None and hasattr(defaultvalue, 'instanceName') and safeid(defaultvalue.instanceName) == pair['key']) or \
                   (defaultvalue_set and defaultvalue is None and str(pair['key']) == 'None'):
                    other_options += ' selected="selected"'
                    found_default = True
                other_options += css_class + '>' + markdown_to_html(str(pair['label']), status=status, escape='option', trim=True, do_terms=False) + '</option>'
            if using_opt_groups:
                other_options += '</optgroup>'
            if (not status.extras['required'][field.number]) or (not found_default):
                output += first_option
            output += other_options
            if embedded:
                output += '</select></span> '
            else:
                output += '</select> '
    elif hasattr(field, 'datatype'):
        if field.datatype == 'boolean' and not is_hidden:
            label_text = markdown_to_html(status.labels[field.number], trim=True, status=status, strip_newlines=True, escape=(not embedded), do_terms=False)
            if hasattr(field, 'inputtype') and field.inputtype in ['yesnoradio', 'noyesradio']:
                inner_fieldlist = []
                id_index = 0
                if embedded:
                    output += '<span class="da-embed-radio-wrapper">'
                else:
                    output += '<fieldset class="da-field-radio" role="radiogroup"' + req_aria + '><legend class="visually-hidden">' + word('Choices:') + '</legend>'
                if field.sign > 0:
                    for pair in [dict(key='True', label=status.question.yes()), dict(key='False', label=status.question.no())]:
                        formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        if embedded:
                            inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + formatted_item + '</label>')
                        else:
                            inner_fieldlist.append('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + DEFAULT_LABELAUTY_COLOR + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="da-to-labelauty' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />')
                        id_index += 1
                else:
                    for pair in [dict(key='False', label=status.question.yes()), dict(key='True', label=status.question.no())]:
                        formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                        if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                            ischecked = ' checked="checked"'
                        else:
                            ischecked = ''
                        if embedded:
                            inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + formatted_item + '</label>')
                        else:
                            inner_fieldlist.append('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + DEFAULT_LABELAUTY_COLOR + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="da-to-labelauty' + extra_radio + '" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />')
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
                    output += '<fieldset class="da-field-checkbox"><legend class="visually-hidden">' + word('Choices:') + '</legend>'
                if field.number in status.helptexts:
                    helptext = status.helptexts[field.number]
                else:
                    helptext = None
                if field.sign > 0:
                    if embedded:
                        output += '<input class="dacheckbox-embedded' + uncheck + '"' + uncheckdata + ' type="checkbox" value="True" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + '/>&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '" />' + label_text + '</label>'
                    else:
                        output += help_wrap('<input aria-label="' + label_text + '" alt="' + label_text + '" class="da-to-labelauty checkbox-icon' + extra_checkbox + uncheck + '"' + title_text + uncheckdata + ' type="checkbox" value="True" data-color="' + DEFAULT_LABELAUTY_COLOR + '" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + ' />', helptext, status) + ' '
                else:
                    if embedded:
                        output += '<input class="dacheckbox-embedded' + uncheck + '"' + uncheckdata + ' type="checkbox" value="False" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + '/>&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '" />' + label_text + '</label>'
                    else:
                        output += help_wrap('<input aria-label="' + label_text + '" alt="' + label_text + '" class="da-to-labelauty checkbox-icon' + extra_checkbox + uncheck + '"' + title_text + uncheckdata + ' type="checkbox" value="False" data-color="' + DEFAULT_LABELAUTY_COLOR + '" data-labelauty="' + label_text + '|' + label_text + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + docheck + disable_others_data + ' />', helptext, status) + ' '
                if embedded:
                    output += '</span>'
                else:
                    output += '</fieldset>'
        elif field.datatype == 'threestate' and not is_hidden:
            inner_fieldlist = []
            id_index = 0
            if embedded:
                output += '<span class="da-embed-threestate-wrapper">'
            else:
                output += '<fieldset class="field-radio" role="radiogroup"' + req_aria + '><legend class="visually-hidden">' + word('Choices:') + '</legend>'
            if field.sign > 0:
                for pair in [dict(key='True', label=status.question.yes()), dict(key='False', label=status.question.no()), dict(key='None', label=status.question.maybe())]:
                    formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ' />&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + formatted_item + ischecked + disable_others_data + '</label>')
                    else:
                        inner_fieldlist.append('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + DEFAULT_LABELAUTY_COLOR + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="da-to-labelauty' + extra_radio + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />')
                    id_index += 1
            else:
                for pair in [dict(key='False', label=status.question.yes()), dict(key='True', label=status.question.no()), dict(key='None', label=status.question.maybe())]:
                    formatted_item = markdown_to_html(str(pair['label']), status=status, trim=True, escape=(not embedded), do_terms=False)
                    if ('default' in pair and pair['default']) or (defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)) and str(pair['key']) == str(defaultvalue)):
                        ischecked = ' checked="checked"'
                    else:
                        ischecked = ''
                    if embedded:
                        inner_fieldlist.append('<input class="daradio-embedded" id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />&nbsp;<label class="form-label" for="' + escape_id(saveas_string) + '_' + str(id_index) + '">' + formatted_item + '</label>')
                    else:
                        inner_fieldlist.append('<input aria-label="' + formatted_item + '" alt="' + formatted_item + '" data-color="' + DEFAULT_LABELAUTY_COLOR + '" data-labelauty="' + formatted_item + '|' + formatted_item + '" class="da-to-labelauty' + extra_radio + '"' + title_text + ' id="' + escape_id(saveas_string) + '_' + str(id_index) + '" name="' + escape_id(saveas_string) + '" type="radio" value=' + fix_double_quote(str(pair['key'])) + ischecked + disable_others_data + ' />')
                    id_index += 1
            if embedded:
                output += " ".join(inner_fieldlist) + '</span>'
            else:
                output += "".join(inner_fieldlist) + '</fieldset>'
        elif field.datatype in ['file', 'files', 'camera', 'user', 'environment', 'camcorder', 'microphone'] and not is_hidden:
            if field.datatype == 'files':
                multipleflag = ' multiple'
            else:
                multipleflag = ''
            if field.datatype == 'camera':
                accept = ' accept="image/*"'
                # capture = ' capture="camera"'
            elif field.datatype == 'user':
                accept = ' accept="image/*" capture="user"'
            elif field.datatype == 'environment':
                accept = ' accept="image/*" capture="environment"'
            elif field.datatype == 'camcorder':
                accept = ' accept="video/*"'
                # capture = '  capture="camcorder"'
            elif field.datatype == 'microphone':
                accept = ' accept="audio/*"'
                # capture = ' capture="microphone"'
            else:
                accept = ''
                # capture = ''
            if 'accept' in status.extras and field.number in status.extras['accept']:
                accept = ' accept="' + status.extras['accept'][field.number] + '"'
            maximagesize = ''
            if 'max_image_size' in status.extras:
                if status.extras['max_image_size']:
                    maximagesize = 'data-maximagesize="' + str(int(float(status.extras['max_image_size']))) + '" '
            elif status.question.interview.max_image_size:
                maximagesize = 'data-maximagesize="' + str(int(float(status.question.interview.max_image_size))) + '" '
            imagetype = ''
            if 'image_type' in status.extras:
                if status.extras['image_type']:
                    imagetype = 'data-imagetype="' + str(status.extras['image_type']) + '" '
            elif status.question.interview.image_type:
                imagetype = 'data-imagetype="' + str(status.question.interview.image_type) + '" '
            if embedded:
                output += '<span class="da-inline-error-wrapper"><input alt="' + word("You can upload a file here") + '" type="file" class="dafile-embedded" name="' + escape_id(saveas_string) + '"' + title_text + ' id="' + escape_id(saveas_string) + '"' + multipleflag + accept + disable_others_data + req_attr + '/></span>'
            else:
                output += '<input aria-describedby="' + escape_id(saveas_string) + '-error" alt=' + fix_double_quote(word("You can upload a file here")) + ' type="file" tabindex="-1" class="dafile" data-show-upload="false" ' + maximagesize + imagetype + ' data-preview-file-type="text" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + accept + disable_others_data + req_attr + ' /><div class="da-has-error invalid-feedback" style="display: none;" id="' + escape_id(saveas_string) + '-error"></div>'
            # output += '<div class="fileinput fileinput-new input-group" data-provides="fileinput"><div class="form-control" data-trigger="fileinput"><i class="fas fa-file fileinput-exists"></i><span class="fileinput-filename"></span></div><span class="input-group-addon btn btn-secondary btn-file"><span class="fileinput-new">' + word('Select file') + '</span><span class="fileinput-exists">' + word('Change') + '</span><input type="file" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + multipleflag + '></span><a href="#" class="input-group-addon btn btn-secondary fileinput-exists" data-dismiss="fileinput">' + word('Remove') + '</a></div>\n'
        elif field.datatype == 'range' and not is_hidden:
            ok = True
            for key in ['min', 'max']:
                if not (hasattr(field, 'extras') and key in field.extras and key in status.extras and field.number in status.extras[key]):
                    ok = False
            if ok:
                if defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)):
                    the_default = ' data-slider-value="' + str(defaultvalue) + '"'
                else:
                    the_default = ' data-slider-value="' + str(int((float(status.extras['max'][field.number]) + float(status.extras['min'][field.number]))/2)) + '"'
                if 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step']:
                    the_step = ' data-slider-step="' + str(status.extras['step'][field.number]) + '"'
                else:
                    the_step = ''
                if 'scale' in field.extras and 'scale' in status.extras and field.number in status.extras['scale']:
                    the_step += ' data-slider-scale="' + str(status.extras['scale'][field.number]) + '"'
                max_string = str(float(status.extras['max'][field.number]))
                min_string = str(float(status.extras['min'][field.number]))
                if embedded:
                    output += '<span class="daslider-embedded"' + title_text + '><input alt="' + word('Select a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + the_default + ' data-slider-max="' + max_string + '" data-slider-min="' + min_string + '"' + the_step + disable_others_data + ' data-slider-id="' + escape_id(saveas_string) + '_slider"></span><br>'
                else:
                    output += '<input alt="' + word('Select a value between') + ' ' + min_string + ' ' + word('and') + ' ' + max_string + '" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + the_default + ' data-slider-max="' + max_string + '" data-slider-min="' + min_string + '"' + the_step + disable_others_data + ' data-slider-id="' + escape_id(saveas_string) + '_slider">'
                status.extra_scripts.append('<script>$("#' + escape_for_jquery(saveas_string) + '").slider({tooltip: "always"});</script>\n')
        elif hasattr(field, 'inputtype') and field.inputtype == 'area':
            if embedded:
                output += '<span class="da-embed-area-wrapper">'
            if 'rows' in status.extras and field.number in status.extras['rows']:
                rows = noquote(str(status.extras['rows'][field.number]))
            else:
                rows = '"4"'
            output += '<textarea alt=' + fix_double_quote(word("Input box")) + ' class="form-control datextarea' + extra_class + '"' + title_text + ' rows=' + rows + ' name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + placeholdertext + disable_others_data + req_attr + '>'
            if defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)):
                output += defaultvalue
            output += '</textarea>'
            if embedded:
                output += '</span>'
        elif hasattr(field, 'inputtype') and field.inputtype == 'ajax':
            if defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)):
                if field.datatype in ('currency', 'number'):
                    if hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step'] and int(float(status.extras['step'][field.number])) == float(status.extras['step'][field.number]):
                        defaultvalue = int(float(defaultvalue))
                    else:
                        defaultvalue = locale_format_string(defaultvalue)
                elif field.datatype == 'integer':
                    defaultvalue = int(float(defaultvalue))
                defaultstring = ' value=' + fix_double_quote(str(defaultvalue))
                default_val = defaultvalue
            elif isinstance(defaultvalue, datetime.time):
                defaultstring = ' value="' + format_time(defaultvalue, format='HH:mm') + '"'
                default_val = format_time(defaultvalue, format='HH:mm')
            elif isinstance(defaultvalue, datetime.datetime):
                if field.datatype == 'datetime':
                    defaultstring = ' value="' + format_datetime(defaultvalue, format='yyyy-MM-ddTHH:mm') + '"'
                    default_val = format_date(defaultvalue, format='yyyy-MM-dd HH:mm')
                elif field.datatype == 'datetime-local':
                    defaultstring = ' value="' + format_datetime(defaultvalue, format='yyyy-MM-ddTHH:mm') + '"'
                    default_val = format_date(defaultvalue, format='yyyy-MM-dd HH:mm')
                else:
                    defaultstring = ' value="' + format_date(defaultvalue, format='yyyy-MM-dd') + '"'
                    default_val = format_date(defaultvalue, format='yyyy-MM-dd')
            else:
                defaultstring = ''
                default_val = ''
            if embedded:
                output += '<span class="da-inline-error-wrapper">'
            output += '<select data-action=' + fix_double_quote(field.combobox_action['action']) + ' data-trig="' + str(field.combobox_action['trig']) + '" alt="' + word("Input box") + '" class="form-control da-ajax-combobox' + extra_class + '"' + extra_style + title_text + ' name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"' + req_attr + '><option' + defaultstring + ' selected="selected">' + option_escape(default_val) + '</option></select>'
            if embedded:
                if field.datatype == 'currency':
                    output += '</span></span>'
                else:
                    output += '</span>'
        else:
            if defaultvalue is not None and isinstance(defaultvalue, (str, int, bool, float)):
                if field.datatype == 'date':
                    the_date = format_date(defaultvalue, format='yyyy-MM-dd')
                    if the_date != word("Bad date"):
                        defaultvalue = the_date
                elif field.datatype == 'time':
                    the_time = format_time(defaultvalue, format='HH:mm')
                    if the_time != word("Bad date"):
                        defaultvalue = the_time
                elif field.datatype == 'datetime':
                    the_date = format_datetime(defaultvalue, format='yyyy-MM-ddTHH:mm')
                    if the_date != word("Bad date"):
                        defaultvalue = the_date
                elif field.datatype == 'datetime-local':
                    the_date = format_datetime(defaultvalue, format='yyyy-MM-ddTHH:mm')
                    if the_date != word("Bad date"):
                        defaultvalue = the_date
                elif field.datatype in ('currency', 'number'):
                    if hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step'] and int(float(status.extras['step'][field.number])) == float(status.extras['step'][field.number]):
                        defaultvalue = int(float(defaultvalue))
                    else:
                        defaultvalue = locale_format_string(defaultvalue)
                elif field.datatype == 'integer':
                    defaultvalue = int(float(defaultvalue))
                defaultstring = ' value=' + fix_double_quote(str(defaultvalue))
            elif isinstance(defaultvalue, datetime.time):
                defaultstring = ' value="' + format_time(defaultvalue, format='HH:mm') + '"'
            elif isinstance(defaultvalue, datetime.datetime):
                if field.datatype == 'datetime':
                    defaultstring = ' value="' + format_datetime(defaultvalue, format='yyyy-MM-ddTHH:mm') + '"'
                elif field.datatype == 'datetime-local':
                    defaultstring = ' value="' + format_datetime(defaultvalue, format='yyyy-MM-ddTHH:mm') + '"'
                else:
                    defaultstring = ' value="' + format_date(defaultvalue, format='yyyy-MM-dd') + '"'
            else:
                defaultstring = ''
            if is_hidden:
                return '<input' + defaultstring + ' type="hidden" name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '" />'
            input_type = field.datatype
            if field.datatype == 'datetime':
                input_type = 'datetime-local'
            step_string = ''
            if field.datatype in ['integer', 'float', 'currency', 'number']:
                input_type = 'text" inputmode="numeric" pattern="[\-\d.,]*'  # noqa: W605
                if hasattr(field, 'extras') and 'step' in field.extras and 'step' in status.extras and field.number in status.extras['step']:
                    step_string = ' step="' + str(status.extras['step'][field.number]) + '"'
                else:
                    if field.datatype == 'integer':
                        step_string = ' step="1"'
                    if field.datatype in ('float', 'number'):
                        step_string = ''
                    # if field.datatype == 'currency':
                    #    step_string = ' step="' + str(1.0/pow(10, daconfig.get('currency decimal places', 2))) + '"'
                if field.datatype == 'currency':
                    extra_class += ' dacurrency'
                    if embedded:
                        output += '<span class="da-embed-currency-wrapper">'
                        currency_symbol = '<span class="da-embed-currency-symbol">' + the_currency_symbol(status, field) + '</span>'
                    else:
                        output += '<div class="input-group">'
                        currency_symbol = '<span class="input-group-text">' + the_currency_symbol(status, field) + '</span>'
                    currency_symbol_before = bool(get_locale('p_cs_precedes'))
                    if currency_symbol_before:
                        output += currency_symbol
            if field.datatype in ('ml', 'raw'):
                input_type = 'text'
            if embedded:
                output += '<span class="da-inline-error-wrapper">'
            data_part = ''
            if field.datatype in custom_types:
                input_type = custom_types[field.datatype]['input_type']
                extra_class += ' ' + custom_types[field.datatype]['input_class']
                custom_parameters = {}
                if hasattr(field, 'extras') and 'custom_parameters' in field.extras:
                    for parameter, parameter_value in field.extras['custom_parameters'].items():
                        custom_parameters[parameter] = parameter_value
                for param_type in ('custom_parameters_code', 'custom_parameters_mako'):
                    if param_type in status.extras and field.number in status.extras[param_type]:
                        for parameter, parameter_value in status.extras[param_type][field.number].items():
                            custom_parameters[parameter] = parameter_value
                if len(custom_parameters) > 0:
                    for param_name, param_val in custom_parameters.items():
                        data_part += ' data-' + re.sub(r'[^A-Za-z0-9\-]', '-', param_name).strip('-') + '=' + fix_double_quote(str(param_val))
            output += '<input' + defaultstring + placeholdertext + ' alt="' + word("Input box") + '" class="form-control' + extra_class + '"' + extra_style + title_text + data_part + ' type="' + input_type + '"' + step_string + ' name="' + escape_id(saveas_string) + '" id="' + escape_id(saveas_string) + '"'
            if not embedded and field.datatype == 'currency':
                output += ' aria-describedby="' + escape_id(saveas_string) + '-error"' + disable_others_data + autocomplete_off + req_attr + ' />'
                if not currency_symbol_before:
                    output += currency_symbol
                output += '</div><div class="da-has-error invalid-feedback" style="display: none;" id="' + escape_id(saveas_string) + '-error"></div>'
            else:
                output += disable_others_data + autocomplete_off + req_attr + ' />'
            if embedded:
                if field.datatype == 'currency':
                    output += '</span>'
                    if not currency_symbol_before:
                        output += currency_symbol
                    output += '</span>'
                else:
                    output += '</span>'
    return output


def myb64doublequote(text):
    return '"' + re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode()) + '"'


def myb64quote(text):
    return "'" + re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode()) + "'"


def repad(text):
    return text + (equals_byte * ((4 - len(text) % 4) % 4))


def indent_by(text, num):
    if not text:
        return ""
    return (" " * num) + re.sub(r'\n', "\n" + (" " * num), text).rstrip() + "\n"


def safeid(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode())


def from_safeid(text):
    return codecs.decode(repad(bytearray(text, encoding='utf-8')), 'base64').decode('utf8')


def escape_id(text):
    return str(text)
    # return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)


def do_escape_id(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\1', text)


def escape_for_jquery(text):
    return re.sub(r'(:|\.|\[|\]|,|=)', r'\\\\\1', text)


def myb64unquote(the_string):
    return codecs.decode(repad(bytearray(the_string, encoding='utf-8')), 'base64').decode('utf8')


def strip_quote(the_string):
    return re.sub(r'"', r'', the_string)


def safe_html(the_string):
    the_string = re.sub(r'\&', '&amp;', the_string)
    the_string = re.sub(r'\<', '&lt;', the_string)
    the_string = re.sub(r'\>', '&gt;', the_string)
    return the_string


def the_currency_symbol(status, field):
    if hasattr(field, 'extras') and 'currency symbol' in field.extras and 'currency symbol' in status.extras and field.number in status.extras['currency symbol']:
        return status.extras['currency symbol'][field.number]
    return get_currency_symbol()


def fix_double_quote(the_string):
    return '"' + re.sub('"', '&quot;', the_string) + '"'


def option_escape(the_string):
    the_string = re.sub(r'\<', '&lt;', the_string)
    the_string = re.sub(r'\>', '&gt;', the_string)
    return the_string


class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, data):
        self.text.write(data)

    def get_data(self):
        return self.text.getvalue()

    def error(self, message):
        self.text.write(message)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def clean_whitespace(text):
    return re.sub(r'\s+', ' ', str(text)).strip()
