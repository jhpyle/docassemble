import re
import os
import mimetypes
import codecs
import json
from io import BytesIO
import xml.etree.ElementTree as ET
import qrcode
import qrcode.image.svg
from pikepdf import Pdf
import PIL
from bs4 import BeautifulSoup
from ..functions import get_config
from ..hooks import (
    file_finder,
    get_default_thead_class,
    fg_make_png_for_pdf_path,
    url_finder,
    get_saved_file_class,
    get_default_table_class,
    fg_make_pdf_for_word_path,
)
from ..language.control import get_language
from ..language.words import word
from ..thread_context import this_thread
from .utils import convert_length, replace_fields, repeat_along

QPDF_PATH = 'qpdf'
NoneType = type(None)

term_start = re.compile(r'\[\[')
term_match = re.compile(r'\[\[([^\[\]\|]*)(\|[^\[\]]*)?\]\]', re.DOTALL)
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
# amp_match = re.compile(r'&(?!#?[0-9A-Za-z]+;)')
emoji_match = re.compile(r':([A-Za-z][A-Za-z0-9\_\-]+):')
extension_match = re.compile(r'\.[a-z]+$')
map_match = re.compile(r'\[MAP ([^\]]+)\]', flags=re.DOTALL)
code_match = re.compile(r'<code>')

# def blank_da_send_mail(*args, **kwargs):
#     logmessage("da_send_mail: no mail agent configured!")
#     return(None)

# da_send_mail = blank_da_send_mail

# def set_da_send_mail(func):
#     global da_send_mail
#     da_send_mail = func
#     return

# def blank_file_finder(*args, **kwargs):
#     return({'filename': "invalid"})

# file_finder = blank_file_finder

# def set_file_finder(func):
#     global file_finder
#     #logmessage("set the file finder to " + str(func))
#     file_finder = func
#     return

# def blank_url_finder(*args, **kwargs):
#     return('about:blank')

# url_finder = blank_url_finder

# def set_url_finder(func):
#     global url_finder
#     url_finder = func
#     return

# def blank_url_for(*args, **kwargs):
#     return('about:blank')

# url_for = blank_url_for

# def set_url_for(func):
#     global url_for
#     url_for = func
#     return



def html_filter(text, status=None, question=None, embedder=None, default_image_width=None, external=False):
    if question is None and status is not None:
        question = status.question
    text = text + "\n\n"
    text = re.sub(r'^[|] (.*)$', r'\1<br>', text, flags=re.MULTILINE)
    text = replace_fields(text, status=status, embedder=embedder)
    # if embedder is not None:
    #     text = re.sub(r'\[FIELD ([^\]]+)\]', lambda x: embedder(status, x.group(1)), text)
    # else:
    #     text = re.sub(r'\[FIELD ([^\]]+)\]', 'ERROR: FIELD cannot be used here', text)
    text = re.sub(r'\[TARGET ([^\]]+)\]', target_html, text)
    if this_thread.evaluation_context != 'docx':
        text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_url_string(x, emoji=True, question=question, external=external, status=status), text)
        text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', lambda x: image_url_string(x, question=question, external=external, status=status), text)
        text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_url_string(x, question=question, external=external, status=status), text)
        text = re.sub(r'\[FILE ([^,\]]+)\]', lambda x: image_url_string(x, question=question, default_image_width=default_image_width, external=external, status=status), text)
        text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', qr_url_string, text)
        text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+)\]', qr_url_string, text)
        text = re.sub(r'\[QR ([^,\]]+)\]', qr_url_string, text)
    if map_match.search(text):
        text = map_match.sub((lambda x: map_string(x.group(1), status)), text)
    # width="420" height="315"
    text = re.sub(r'\[YOUTUBE ([^\]]+)\]', r'<div class="davideo davideo169"><iframe src="https://www.youtube.com/embed/\1?rel=0" frameborder="0" allowfullscreen></iframe></div>', text)
    text = re.sub(r'\[YOUTUBE4:3 ([^\]]+)\]', r'<div class="davideo davideo43"><iframe src="https://www.youtube.com/embed/\1?rel=0" frameborder="0" allowfullscreen></iframe></div>', text)
    text = re.sub(r'\[YOUTUBE16:9 ([^\]]+)\]', r'<div class="davideo davideo169"><iframe src="https://www.youtube.com/embed/\1?rel=0" frameborder="0" allowfullscreen></iframe></div>', text)
    # width="500" height="281"
    text = re.sub(r'\[VIMEO ([^\]]+)\]', r'<div class="davideo davideo169"><iframe src="https://player.vimeo.com/video/\1?byline=0&portrait=0" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>', text)
    text = re.sub(r'\[VIMEO4:3 ([^\]]+)\]', r'<div class="davideo davideo43"><iframe src="https://player.vimeo.com/video/\1?byline=0&portrait=0" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>', text)
    text = re.sub(r'\[VIMEO16:9 ([^\]]+)\]', r'<div class="davideo davideo169"><iframe src="https://player.vimeo.com/video/\1?byline=0&portrait=0" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>', text)
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\[VERTICAL_LINE\]\s*(.+?)\[END_CAPTION\]', html_caption, text, flags=re.DOTALL)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\[BREAK\]\s*(.+?)\[END_TWOCOL\]', html_two_col, text, flags=re.DOTALL)
    text = re.sub(r'\[NBSP\]', r'&nbsp;', text)
    text = re.sub(r'\[REDACTION_SPACE\]', '&#9608;&#8203;', text)
    text = re.sub(r'\[REDACTION_WORD ([^\]]+)\]', lambda x: repeat_along('&#9608;', x), text)
    text = re.sub(r'\[ENDASH\]', r'&ndash;', text)
    text = re.sub(r'\[EMDASH\]', r'&mdash;', text)
    text = re.sub(r'\[HYPHEN\]', r'-', text)
    text = re.sub(r'\[CHECKBOX\]', r'<span style="text-decoration: underline">&nbsp;&nbsp;&nbsp;&nbsp;</span>', text)
    text = re.sub(r'\[BLANK\]', r'<span style="text-decoration: underline">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>', text)
    text = re.sub(r'\[BLANKFILL\]', r'<span style="text-decoration: underline">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>', text)
    text = re.sub(r'\[PAGEBREAK\] *', r'', text)
    text = re.sub(r'\[PAGENUM\] *', r'', text)
    text = re.sub(r'\[SECTIONNUM\] *', r'', text)
    text = re.sub(r'\[SKIPLINE\] *', r'<br />', text)
    text = re.sub(r'\[NEWLINE\] *', r'<br />', text)
    text = re.sub(r'\[NEWPAR\] *', r'<br /><br />', text)
    text = re.sub(r'\[BR\] *', r'<br />', text)
    text = re.sub(r'\[TAB\] *', '<span class="datab"></span>', text)
    text = re.sub(r' *\[END\] *', r'\n', text)
    lines = re.split(r'\n *\n', text)
    text = ''
    spacing_class = None
    doing_indentation = False
    for line in lines:
        classes = set()
        styles = {}
        if re.search(r'\[TIGHTSPACING\]', line):
            spacing_class = 'daspacingtight'
        if re.search(r'\[SINGLESPACING\]', line):
            spacing_class = 'daspacingsingle'
        if re.search(r'\[DOUBLESPACING\]', line):
            spacing_class = 'daspacingdouble'
        if re.search(r'\[ONEANDAHALFSPACING\]', line):
            spacing_class = 'daspacingoneandahalf'
        if re.search(r'\[TRIPLESPACING\]', line):
            spacing_class = 'daspacingtriple'
        if re.search(r'\[START_INDENTATION\]', line):
            doing_indentation = True
        if re.search(r'\[STOP_INDENTATION\]', line):
            doing_indentation = False
        if spacing_class:
            classes.add(spacing_class)
        if doing_indentation and not re.search(r'\[NOINDENT\]', line):
            styles['text-indent'] = '36px'
        if re.search(r'\[BORDER\]', line):
            classes.add('daborder')
        if re.search(r'\[FLUSHLEFT\]', line):
            classes.add('daflushleft')
        if re.search(r'\[FLUSHRIGHT\]', line):
            classes.add('daflushright')
        if re.search(r'\[CENTER\]', line):
            classes.add('dacenter')
        if re.search(r'\[BOLDCENTER\]', line):
            classes.add('dacenter')
            classes.add('dabold')
        m = re.search(r'\[INDENTBY *([0-9\.]+ *[A-Za-z]+)\]', line)
        if m:
            styles["padding-left"] = str(convert_length(m.group(1), 'px')) + 'px'
        m = re.search(r'\[INDENTBY *([0-9\.]+ *[A-Za-z]+) *([0-9]+ *[A-Za-z]+)\]', line)
        if m:
            styles["margin-left"] = str(convert_length(m.group(1), 'px')) + 'px'
            styles["margin-right"] = str(convert_length(m.group(2), 'px')) + 'px'
        orig_length = len(line)
        line = re.sub(r'\[(BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|BOLDCENTER|CENTER|TIGHTSPACING|SINGLESPACING|DOUBLESPACING|ONEANDAHALFSPACING|TRIPLESPACING|START_INDENTATION|STOP_INDENTATION)\] *', r'', line)
        line = re.sub(r'\[INDENTBY[^\]]*\] *', r'', line)
        if orig_length > 0 and len(line) == 0:
            continue
        if line.startswith('>'):
            line = re.sub(r'^> *', '', line)
            text += "> "
        if len(classes) > 0 or len(styles) > 0:
            text += '<i class="visually-hidden'
            if len(classes) > 0:
                text += '  ' + " ".join(classes) + '"'
            else:
                text += '"'
            if len(styles) > 0:
                text += ' style="' + "".join(map(lambda x: str(x[0]) + ":" + x[1] + ';', styles.items())) + '"'
            text += '></i>'
        text += line + '\n\n'
    text = re.sub(r'\n+$', r'', text)
    return text


def map_string(encoded_text, status):
    if status is None:
        return ''
    map_number = len(status.maps)
    status.maps.append(codecs.decode(bytearray(encoded_text, 'utf-8'), 'base64').decode())
    return '<div id="map' + str(map_number) + '" class="dagooglemap"></div>'


def target_html(match):
    target = match.group(1)
    target = re.sub(r'[^A-Za-z0-9\_]', r'', str(target))
    return '<span class="datarget' + target + '"></span>'


def html_caption(match):
    firstcol = match.group(1)
    secondcol = match.group(2)
    firstcol = re.sub(r'^\s+', '', firstcol)
    firstcol = re.sub(r'\s+$', '', firstcol)
    secondcol = re.sub(r'^\s+', '', secondcol)
    secondcol = re.sub(r'\s+$', '', secondcol)
    firstcol = markdown_to_html(firstcol)
    secondcol = markdown_to_html(secondcol)
    return '<table style="width: 100%"><tr><td style="width: 50%; border-style: solid; border-right-width: 1px; padding-right: 1em; border-left-width: 0px; border-top-width: 0px; border-bottom-width: 0px">' + firstcol + '</td><td style="padding-left: 1em; width: 50%;">' + secondcol + '</td></tr></table>'


def html_two_col(match):
    firstcol = markdown_to_html(match.group(1))
    secondcol = markdown_to_html(match.group(2))
    return '<table style="width: 100%"><tr><td style="width: 50%; vertical-align: top; border-style: none; padding-right: 1em;">' + firstcol + '</td><td style="padding-left: 1em; vertical-align: top; width: 50%;">' + secondcol + '</td></tr></table>'


def add_newlines(string):
    string = re.sub(r'\[(BR)\]', r'[NEWLINE]', string)
    string = re.sub(r' *\n', r'\n', string)
    string = re.sub(r'(?<!\[NEWLINE\])\n', r' [NEWLINE]\n', string)
    return string



def image_url_string(match, emoji=False, question=None, default_image_width=None, external=False, status=None):
    file_reference = match.group(1)
    try:
        width = match.group(2)
        assert width != 'None'
    except:
        if default_image_width is not None:
            width = default_image_width
        else:
            width = "300px"
    if width == "full":
        width = "300px"
    if match.lastindex == 3:
        if match.group(3) != 'None':
            alt_text = 'alt=' + json.dumps(match.group(3)) + ' '
        else:
            alt_text = ''
    else:
        alt_text = ''
    return image_url(file_reference, alt_text, width, emoji=emoji, question=question, external=external, status=status)


def image_url(file_reference, alt_text, width, emoji=False, question=None, external=False, status=None):
    if question and file_reference in question.interview.images:
        if status and question.interview.images[file_reference].attribution is not None:
            status.attributions.add(question.interview.images[file_reference].attribution)
        file_reference = question.interview.images[file_reference].get_reference()
    file_info = file_finder(file_reference, question=question)
    if 'mimetype' in file_info and file_info['mimetype']:
        if re.search(r'^audio', file_info['mimetype']):
            urls = get_audio_urls([{'text': "[FILE " + file_reference + "]", 'package': None, 'type': 'audio'}], question=question)
            if len(urls) > 0:
                return audio_control(urls)
            return ''
        if re.search(r'^video', file_info['mimetype']):
            urls = get_video_urls([{'text': "[FILE " + file_reference + "]", 'package': None, 'type': 'video'}], question=question)
            if len(urls) > 0:
                return video_control(urls)
            return ''
    if 'extension' in file_info and file_info['extension'] is not None:
        if re.match(r'.*%$', width):
            width_string = "width:" + width
            stack_width_string = width_string
        else:
            width_string = "max-width:" + width
            stack_width_string = "width:" + width
        if emoji:
            width_string += ';vertical-align: middle'
            alt_text = 'alt="" '
        the_url = url_finder(file_reference, _question=question, display_filename=file_info['filename'], _external=external)
        if the_url is None:
            return '[ERROR: File reference ' + str(file_reference) + ' cannot be displayed]'
        if width_string == 'width:100%':
            extra_class = ' dawideimage'
        else:
            extra_class = ''
        if file_info.get('extension', '') in ('png', 'jpg', 'gif', 'svg', 'jpe', 'jpeg'):
            try:
                if file_info.get('extension', '') == 'svg':
                    attributes = ET.parse(file_info['fullpath']).getroot().attrib
                    layout_width = attributes['width']
                    layout_height = attributes['height']
                else:
                    with PIL.Image.open(file_info['fullpath']) as im:
                        layout_width, layout_height = im.size
                return '<img ' + alt_text + 'class="daicon daimageref' + extra_class + '" width=' + str(layout_width) + ' height=' + str(layout_height) + ' style="' + width_string + '; height: auto;" src="' + the_url + '"/>'
            except:
                return '<img ' + alt_text + 'class="daicon daimageref' + extra_class + '" style="' + width_string + '; height: auto;" src="' + the_url + '"/>'
        if file_info['extension'] in ('pdf', 'docx', 'rtf', 'doc', 'odt'):
            if file_info['extension'] in ('docx', 'rtf', 'doc', 'odt') and not os.path.isfile(file_info['path'] + '.pdf'):
                fg_make_pdf_for_word_path(file_info['path'], file_info['extension'])
                fg_make_png_for_pdf_path(file_info['path'] + ".pdf", 'screen', page=1)
                if re.match(r'[0-9]+', str(file_reference)):
                    sf = get_saved_file_class()(int(file_reference), fix=True)
                    sf.finalize()
            if 'pages' not in file_info:
                try:
                    with Pdf.open(file_info['path'] + '.pdf') as reader:
                        file_info['pages'] = len(reader.pages)
                except:
                    file_info['pages'] = 1
            the_image_url = url_finder(file_reference, size="screen", page=1, _question=question, _external=external)
            if the_image_url is None:
                return '[ERROR: File reference ' + str(file_reference) + ' cannot be displayed]'
            if 'filename' in file_info:
                title = ' title="' + file_info['filename']
                if 'pages' in file_info and file_info['pages'] > 1:
                    title += " (" + str(file_info['pages']) + " " + word('pages') + ")"
                title += '"'
            else:
                if 'pages' in file_info and file_info['pages'] > 1:
                    title = ' title="' + str(file_info['pages']) + " " + word('pages') + '"'
                else:
                    title = ''
            if alt_text == '':
                the_alt_text = 'alt=' + json.dumps(word("Thumbnail image of document")) + ' '
            else:
                the_alt_text = alt_text
            try:
                with Pdf.open(file_info['path'] + '.pdf') as reader:
                    layout_width = reader.pages[0].mediabox[2] - reader.pages[0].mediabox[0]
                    layout_height = reader.pages[0].mediabox[3] - reader.pages[0].mediabox[1]
                    if width_string == 'width:100%':
                        output = '<a target="_blank"' + title + ' class="daimageref" href="' + the_url + '"><img ' + the_alt_text + 'class="daicon dapdfscreen' + extra_class + '" width=' + str(layout_width) + ' height=' + str(layout_height) + ' style="' + width_string + '; height: auto;" src="' + the_image_url + '"/></a>'
                    else:
                        if 'pages' in file_info and file_info['pages'] >= 1:
                            extra_pages = min(2, file_info['pages'] - 1)
                        else:
                            extra_pages = 2
                        aspect_ratio = 1.0*layout_width/layout_height
                        stack_width_string += "; height: auto; aspect-ratio: " + str(aspect_ratio) + ";"
                        output = '<div class="da-paper-stack" style="' + stack_width_string + '"><div class="da-paper"><a target="_blank"' + title + ' class="daimageref" href="' + the_url + '"><img ' + the_alt_text + 'class="daicon' + extra_class + '" width=' + str(layout_width) + ' height="' + str(layout_height) + '" style="width: 100%; height: auto" src="' + the_image_url + '"/></a></div>' + (('<div class="da-paper"></div>') * extra_pages) + '</div>'
            except:
                output = '<a target="_blank"' + title + ' class="daimageref" href="' + the_url + '"><img ' + the_alt_text + 'class="daicon dapdfscreen' + extra_class + '" style="' + width_string + '; height: auto;" src="' + the_image_url + '"/></a>'
            return output
        return '<a target="_blank" class="daimageref" href="' + the_url + '">' + file_info['filename'] + '</a>'
    return '[Invalid image reference; reference=' + str(file_reference) + ', width=' + str(width) + ', filename=' + file_info.get('filename', 'unknown') + ']'


def qr_url_string(match):
    string = match.group(1)
    try:
        width = match.group(2)
        assert width != 'None'
    except:
        width = "300px"
    if width == "full":
        width = "300px"
    if match.lastindex == 3:
        if match.group(3) != 'None':
            alt_text = str(match.group(3))
        else:
            alt_text = word(f"A QR code that goes to {string}")
    else:
        alt_text = word(f"A QR code that goes to {string}")
    width_string = "width:" + width
    im = qrcode.make(string, image_factory=qrcode.image.svg.SvgPathFillImage)
    output = BytesIO()
    im.save(output)
    the_image = output.getvalue().decode()
    the_image = re.sub(r"<\?xml version='1.0' encoding='UTF-8'\?>\n", '', the_image)
    the_image = re.sub(r'height="[0-9]+mm" ', '', the_image)
    the_image = re.sub(r'width="[0-9]+mm" ', '', the_image)
    m = re.search(r'(viewBox="[^"]+")', the_image)
    if m:
        viewbox = m.group(1)
    else:
        viewbox = ""
    return '<svg style="' + width_string + '" ' + viewbox + '><g transform="scale(1.0)">' + the_image + '</g><title>' + alt_text + '</title></svg>'


def get_icon_html(text):
    icons_setting = get_config('default icons', None)
    if icons_setting == 'font awesome':
        m = re.search(r'^(fa[a-z])-fa-(.*)', text)
        if m:
            the_prefix = m.group(1)
            text = m.group(2)
        else:
            the_prefix = get_config('font awesome prefix', 'fa-solid')
        if the_prefix == 'fab':
            the_prefix = 'fa-brands'
        elif the_prefix == 'far':
            the_prefix = 'fa-regular'
        elif the_prefix == 'fas':
            the_prefix = 'fa-solid'
        return '<i class="' + the_prefix + ' fa-' + str(text) + '"></i>'
    if icons_setting == 'material icons':
        return '<i class="da-material-icons">' + str(text) + '</i>'
    return None


def emoji_html(text, status=None, question=None, images=None):
    # logmessage("Got to emoji_html")
    if status is not None and question is None:
        question = status.question
    if images is None:
        images = question.interview.images
    if text in images:
        if status is not None and images[text].attribution is not None:
            status.attributions.add(images[text].attribution)
        return image_url(images[text].get_reference(), word('icon'), '1em', emoji=True, question=question)
    icon_html = get_icon_html(text)
    if icon_html:
        return icon_html
    return ":" + str(text) + ":"


def emoji_insert(text, status=None, images=None):
    if images is None:
        images = status.question.interview.images
    if text in images:
        if status is not None and images[text].attribution is not None:
            status.attributions.add(images[text].attribution)
        return "[EMOJI " + images[text].get_reference() + ', 1.2em]'
    return ":" + str(text) + ":"


def link_rewriter(m, status):
    the_path = None
    if m.group(1).startswith('#'):
        return '<a href="javascript:daGoToAnchor(' + re.sub(r'"', '&quot;', json.dumps(m.group(1))) + ');"'
    if m.group(1).startswith('/'):
        the_path = m.group(1)
    elif 'url_root' in this_thread.current_info and m.group(1).startswith(this_thread.current_info['url_root']):
        the_path = '/' + m.group(1)[len(this_thread.current_info['url_root']):]
    if the_path:
        if re.search(r'^/(packagestatic|storedfile|tempfile|uploadedfile|uploadedpage|playgroundstatic|playgrounddownload)', the_path):
            target = 'target="_blank" '
        else:
            target = ''
    else:
        target = 'target="_blank" '
    if the_path or m.group(1).startswith('?'):
        action_search = re.search(r'[\?\&]action=([^\&]+)', m.group(1))
        if action_search:
            action_data = 'data-embaction="' + action_search.group(1) + '" '
            target = ''
        else:
            action_data = ''
    else:
        action_data = ''
    if m.group(1).startswith('?'):
        target = ''
    js_search = re.search(r'^javascript:(.*)', m.group(1))
    if js_search:
        js_data = 'data-js="' + js_search.group(1) + '" '
        target = ''
    else:
        js_data = ''
    if status is None:
        return '<a ' + action_data + target + js_data + 'href="' + m.group(1) + '"'
    status.linkcounter += 1
    return '<a data-linknum="' + str(status.linkcounter) + '" ' + action_data + target + js_data + 'href="' + m.group(1) + '"'


def sub_term(m):
    if m.group(2):
        return '[[' + m.group(1) + m.group(2) + ']]'
    return '[[' + m.group(1) + ']]'


def markdown_to_html(a, trim=False, pclass=None, status=None, question=None, use_pandoc=False, escape=False, do_terms=True, strip_newlines=None, divclass=None, embedder=None, default_image_width=None, external=False, verbatim=False):
    if verbatim:
        return a
    a = str(a)
    if question is None and status is not None:
        question = status.question
    if question is not None:
        if do_terms:
            terms_done = set()
            if status is not None:
                if len(question.terms) > 0:
                    lang = get_language()
                    for term in question.terms:
                        terms_done.add(term.lower())
                        # logmessage("Searching for term " + term + " in " + a)
                        if lang in question.terms[term]['re']:
                            a = question.terms[term]['re'][lang].sub(sub_term, a)
                        else:
                            a = question.terms[term]['re'][question.language].sub(sub_term, a)
                        # logmessage("string is now " + str(a))
                if len(question.autoterms) > 0:
                    lang = get_language()
                    for term in question.autoterms:
                        if term.lower() in terms_done:
                            continue
                        terms_done.add(term.lower())
                        # logmessage("Searching for term " + term + " in " + a)
                        if lang in question.autoterms[term]['re']:
                            a = question.autoterms[term]['re'][lang].sub(r'[[\1]]', a)
                        else:
                            a = question.autoterms[term]['re'][question.language].sub(r'[[\1]]', a)
                        # logmessage("string is now " + str(a))
                if 'interview_terms' in status.extras:
                    interview_terms = status.extras['interview_terms']
                else:
                    interview_terms = question.interview.terms
                if 'interview_autoterms' in status.extras:
                    interview_autoterms = status.extras['interview_autoterms']
                else:
                    interview_autoterms = question.interview.autoterms
            else:
                interview_terms = question.interview.terms
                interview_autoterms = question.interview.autoterms
            if len(interview_terms) > 0:
                lang = get_language()
                if lang in interview_terms and len(interview_terms[lang]) > 0:
                    for term in interview_terms[lang]:
                        if term.lower() in terms_done:
                            continue
                        terms_done.add(term.lower())
                        # logmessage("Searching for term " + term + " in " + a)
                        a = interview_terms[lang][term]['re'].sub(sub_term, a)
                        # logmessage("string is now " + str(a))
                elif question.language in interview_terms and len(interview_terms[question.language]) > 0:
                    for term in interview_terms[question.language]:
                        if term.lower() in terms_done:
                            continue
                        terms_done.add(term.lower())
                        # logmessage("Searching for term " + term + " in " + a)
                        a = interview_terms[question.language][term]['re'].sub(sub_term, a)
                        # logmessage("string is now " + str(a))
            if len(interview_autoterms) > 0:
                lang = get_language()
                if lang in interview_autoterms and len(interview_autoterms[lang]) > 0:
                    for term in interview_autoterms[lang]:
                        if term.lower() in terms_done:
                            continue
                        terms_done.add(term.lower())
                        # logmessage("Searching for term " + term + " in " + a)
                        a = interview_autoterms[lang][term]['re'].sub(r'[[\1]]', a)
                        # logmessage("string is now " + str(a))
                elif question.language in interview_autoterms and len(interview_autoterms[question.language]) > 0:
                    for term in interview_autoterms[question.language]:
                        if term.lower() in terms_done:
                            continue
                        terms_done.add(term.lower())
                        # logmessage("Searching for term " + term + " in " + a)
                        a = interview_autoterms[question.language][term]['re'].sub(r'[[\1]]', a)
                        # logmessage("string is now " + str(a))
    a = html_filter(str(a), status=status, question=question, embedder=embedder, default_image_width=default_image_width, external=external)
    # logmessage("before: " + a)
    if status and status.extras.get('tableCssClass', None):
        classes = status.extras['tableCssClass'].split(',')
        table_class = json.dumps(classes[0].strip())
        if len(classes) > 1:
            thead_class = json.dumps(classes[1].strip())
        else:
            thead_class = None
    else:
        table_class = get_default_table_class()
        thead_class = get_default_thead_class()
    a = re.sub(r'<(/?)table', r'<\1TABLE', a)
    a = re.sub(r'<thead>', r'<THEAD>', a)
    if use_pandoc:
        from docassemble.base import pandoc
        converter = pandoc.MyPandoc()
        converter.output_format = 'html'
        converter.input_content = a
        converter.convert(question)
        result = converter.output_content
    else:
        try:
            result = this_thread.markdown.reset().convert(a)
        except:
            # Try again because sometimes it fails randomly and maybe trying again will work.
            result = this_thread.markdown.reset().convert(a)
    result = re.sub(r'<table>', r'<div class="table-responsive"><table class=' + table_class + '>', result)
    if thead_class != '':
        result = re.sub(r'<thead>', r'<thead class=' + thead_class + '>', result)
    result = re.sub(r'</table>', r'</table></div>', result)
    result = re.sub(r'<(/?)TABLE', r'<\1table', result)
    result = re.sub(r'<THEAD>', r'<thead>', result)
    result = re.sub(r'<(t[dh]) align="(right|left|center)">', r'<\1 class="text-\2">', result)
    result = re.sub(r'<blockquote>', r'<blockquote class="blockquote">', result)
    result = re.sub(r'<a href="(.*?)"', lambda x: link_rewriter(x, status), result)
    if do_terms and question is not None and term_start.search(result):
        lang = get_language()
        if status is not None:
            if len(question.terms) > 0 and 'terms' in status.extras:
                result = term_match.sub((lambda x: add_terms(x.group(1), status.extras['terms'], label=x.group(2), status=status, question=question)), result)
            if len(question.autoterms) > 0 and 'autoterms' in status.extras:
                result = term_match.sub((lambda x: add_terms(x.group(1), status.extras['autoterms'], label=x.group(2), status=status, question=question)), result)
            if 'interview_terms' in status.extras:
                interview_terms = status.extras['interview_terms']
            else:
                interview_terms = question.interview.terms
            if 'interview_autoterms' in status.extras:
                interview_autoterms = status.extras['interview_autoterms']
            else:
                interview_autoterms = question.interview.autoterms
        else:
            interview_terms = question.interview.terms
            interview_autoterms = question.interview.autoterms
        if lang in interview_terms and len(interview_terms[lang]):
            result = term_match.sub((lambda x: add_terms(x.group(1), interview_terms[lang], label=x.group(2), status=status, question=question)), result)
        elif question.language in interview_terms and len(interview_terms[question.language]):
            result = term_match.sub((lambda x: add_terms(x.group(1), interview_terms[question.language], label=x.group(2), status=status, question=question)), result)
        if lang in interview_autoterms and len(interview_autoterms[lang]):
            result = term_match.sub((lambda x: add_terms(x.group(1), interview_autoterms[lang], label=x.group(2), status=status, question=question)), result)
        elif question.language in interview_autoterms and len(interview_autoterms[question.language]):
            result = term_match.sub((lambda x: add_terms(x.group(1), interview_autoterms[question.language], label=x.group(2), status=status, question=question)), result)
    do_not_scan_for_emojis = bool(re.search(r'\[NO_EMOJIS\]', result))
    if do_not_scan_for_emojis:
        result = re.sub(r'\[NO_EMOJIS\]\s*', r'', result)
    if status is not None and question.interview.scan_for_emojis and not do_not_scan_for_emojis:
        result = emoji_match.sub((lambda x: emoji_html(x.group(1), status=status, question=question)), result)
    result = re.sub(r'<p><i class="visually-hidden *([^>]*)></i>', r'<p class="\1>', result)
    if trim:
        if result.startswith('<p>') and result.endswith('</p>'):
            result = re.sub(r'</p>\s*<p>', ' ', result[3:-4])
    elif pclass:
        result = re.sub('<p>', '<p class="' + pclass + '">', result)
    if escape:
        if escape is True:
            result = noquote_match.sub('&quot;', result)
        if escape == 'option':
            result = re.sub(r'\n\r', ' ', BeautifulSoup(result, 'html.parser').get_text()).strip()
        result = lt_match.sub('&lt;', result)
        result = gt_match.sub('&gt;', result)
        if escape is True:
            result = amp_match.sub('&amp;', result)
    # logmessage("after: " + result)
    # result = result.replace('\n', ' ')
    if result:
        if strip_newlines:
            result = result.replace('\n', ' ')
        if divclass is not None:
            result = '<div class="' + str(divclass) + '">' + result + '</div>'
        # if indent and not code_match.search(result):
        #     return (" " * indent) + re.sub(r'\n', "\n" + (" " * indent), result).rstrip() + "\n"
    return result


def my_escape(result):
    result = noquote_match.sub('&quot;', result)
    result = lt_match.sub('&lt;', result)
    result = gt_match.sub('&gt;', result)
    result = amp_match.sub('&amp;', result)
    return result


def noquote(string):
    # return json.dumps(string.replace('\n', ' ').rstrip())
    return '"' + string.replace('\n', ' ').replace('"', '&quot;').rstrip() + '"'


def add_terms_mako(termname, terms, status=None, question=None):
    lower_termname = re.sub(r'\s+', ' ', str(termname).lower(), re.DOTALL)
    if lower_termname in terms:
        term_as_text = to_text(markdown_to_html(str(termname), trim=False, do_terms=False, status=status, question=question), None, None)
        return '<a tabindex="0" class="daterm" aria-label=' + noquote(term_as_text + ' ' + word("(term definition)")) +\
            ' data-bs-toggle="popover" data-bs-container="body" data-bs-placement="bottom" data-bs-content=' +\
            noquote(markdown_to_html(terms[lower_termname]['definition'].text({}),
                                     trim=True,
                                     default_image_width='100%',
                                     do_terms=False,
                                     status=status,
                                     question=question
                                     )) + '>' + str(termname) + '</a>'
    # logmessage(lower_termname + " is not in terms dictionary")
    return '[[' + termname + ']]'


def add_terms(termname, terms, label=None, status=None, question=None):
    if label is None:
        label = str(termname)
    else:
        label = re.sub(r'^\|', '', label)
    lower_termname = re.sub(r'\s+', ' ', termname.lower(), re.DOTALL)
    if lower_termname in terms:
        term_as_text = to_text(markdown_to_html(label, trim=False, do_terms=False, status=status, question=question), None, None)
        return '<a tabindex="0" class="daterm" aria-label=' + noquote(term_as_text + ' ' + word("(term definition)")) +\
            ' data-bs-toggle="popover" data-bs-container="body" data-bs-placement="bottom" data-bs-content=' +\
            noquote(markdown_to_html(terms[lower_termname]['definition'],
                                     trim=True,
                                     default_image_width='100%',
                                     do_terms=False,
                                     status=status,
                                     question=question
                                     )) + '>' + label + '</a>'
    return '[[' + termname + ']]'


def audio_control(files, preload="metadata", title_text=None):
    for d in files:
        if isinstance(d, str):
            return d
    if title_text is None:
        title_text = ''
    else:
        title_text = " title=" + json.dumps(title_text)
    output = '<audio' + title_text + ' class="daaudio-control" controls="controls" preload="' + preload + '">' + "\n"
    for d in files:
        if isinstance(d, list):
            output += '  <source src="' + d[0] + '"'
            if d[1] is not None:
                output += ' type="' + d[1] + '"/>'
            output += "\n"
    output += '  <a target="_blank" href="' + files[-1][0] + '">' + word('Listen') + '</a>\n'
    output += "</audio>\n"
    return output


def video_control(files):
    for d in files:
        if isinstance(d, (str, NoneType)):
            return str(d)
    output = '<video class="dawidevideo" controls="controls">' + "\n"
    for d in files:
        if isinstance(d, list):
            if d[0] is None:
                continue
            output += '  <source src="' + d[0] + '"'
            if d[1] is not None:
                output += ' type="' + d[1] + '"/>'
            output += "\n"
    output += '  <a target="_blank" href="' + files[-1][0] + '">' + word('Listen') + '</a>\n'
    output += "</video>\n"
    return output


def get_audio_urls(the_audio, question=None):
    output = []
    the_list = []
    to_try = {}
    for audio_item in the_audio:
        if audio_item['type'] != 'audio':
            continue
        found_upload = False
        pattern = re.compile(r'^\[FILE ([^,\]]+)')
        for file_ref in re.findall(pattern, audio_item['text']):
            found_upload = True
            m = re.match(r'[0-9]+', file_ref)
            if m:
                file_info = file_finder(file_ref, question=question)
                if 'path' in file_info:
                    if file_info['mimetype'] == 'audio/ogg':
                        output.append([url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.ogg'):
                        output.append([url_finder(file_ref, ext='ogg', _question=question), 'audio/ogg'])
                    if file_info['mimetype'] == 'audio/mpeg':
                        output.append([url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.mp3'):
                        output.append([url_finder(file_ref, ext='mp3', _question=question), 'audio/mpeg'])
                    if file_info['mimetype'] not in ['audio/mpeg', 'audio/ogg']:
                        output.append([url_finder(file_ref, _question=question), file_info['mimetype']])
            else:
                the_list.append({'text': file_ref, 'package': audio_item['package']})
        if not found_upload:
            the_list.append(audio_item)
    for audio_item in the_list:
        mimetype, encoding = mimetypes.guess_type(audio_item['text'])  # pylint: disable=unused-variable
        if re.search(r'^http', audio_item['text']):
            output.append([audio_item['text'], mimetype])
            continue
        basename = os.path.splitext(audio_item['text'])[0]
        ext = os.path.splitext(audio_item['text'])[1]
        if mimetype not in to_try:
            to_try[mimetype] = []
        to_try[mimetype].append({'basename': basename, 'filename': audio_item['text'], 'ext': ext, 'package': audio_item['package']})
    if 'audio/mpeg' in to_try and 'audio/ogg' not in to_try:
        to_try['audio/ogg'] = []
        for attempt in to_try['audio/mpeg']:
            if attempt['ext'] == '.MP3':
                to_try['audio/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.OGG', 'ext': '.OGG', 'package': attempt['package']})
            else:
                to_try['audio/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.ogg', 'ext': '.ogg', 'package': attempt['package']})
    if 'audio/ogg' in to_try and 'audio/mpeg' not in to_try:
        to_try['audio/mpeg'] = []
        for attempt in to_try['audio/ogg']:
            if attempt['ext'] == '.OGG':
                to_try['audio/mpeg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.MP3', 'ext': '.MP3', 'package': attempt['package']})
            else:
                to_try['audio/mpeg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.mp3', 'ext': '.mp3', 'package': attempt['package']})
    for mimetype in reversed(sorted(to_try.keys())):
        for attempt in to_try[mimetype]:
            parts = attempt['filename'].split(':')
            if len(parts) < 2:
                parts = [attempt['package'], attempt['filename']]
            if parts[0] is None:
                parts[0] = 'None'
            parts[1] = re.sub(r'^data/static/', '', parts[1])
            full_file = parts[0] + ':data/static/' + parts[1]
            file_info = file_finder(full_file, question=question)
            if 'fullpath' in file_info:
                url = url_finder(full_file, _question=question)
                output.append([url, mimetype])
    return [item for item in output if item[0] is not None]


def get_video_urls(the_video, question=None):
    output = []
    the_list = []
    to_try = {}
    for video_item in the_video:
        if video_item['type'] != 'video':
            continue
        found_upload = False
        if re.search(r'^\[(YOUTUBE|VIMEO)[0-9\:]* ', video_item['text']):
            output.append(html_filter(video_item['text']))
            continue
        pattern = re.compile(r'^\[FILE ([^,\]]+)')
        for file_ref in re.findall(pattern, video_item['text']):
            found_upload = True
            m = re.match(r'[0-9]+', file_ref)
            if m:
                file_info = file_finder(file_ref, question=question)
                if 'path' in file_info:
                    if file_info['mimetype'] == 'video/ogg':
                        output.append([url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.ogv'):
                        output.append([url_finder(file_ref, ext='ogv', _question=question), 'video/ogg'])
                    if file_info['mimetype'] == 'video/mp4':
                        output.append([url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.mp4'):
                        output.append([url_finder(file_ref, ext='mp4', _question=question), 'video/mp4'])
                    if file_info['mimetype'] not in ['video/mp4', 'video/ogg']:
                        output.append([url_finder(file_ref, _question=question), file_info['mimetype']])
            else:
                the_list.append({'text': file_ref, 'package': video_item['package']})
        if not found_upload:
            the_list.append(video_item)
    for video_item in the_list:
        mimetype, encoding = mimetypes.guess_type(video_item['text'])  # pylint: disable=unused-variable
        if re.search(r'^http', video_item['text']):
            output.append([video_item['text'], mimetype])
            continue
        basename = os.path.splitext(video_item['text'])[0]
        ext = os.path.splitext(video_item['text'])[1]
        if mimetype not in to_try:
            to_try[mimetype] = []
        to_try[mimetype].append({'basename': basename, 'filename': video_item['text'], 'ext': ext, 'package': video_item['package']})
    if 'video/mp4' in to_try and 'video/ogg' not in to_try:
        to_try['video/ogg'] = []
        for attempt in to_try['video/mp4']:
            if attempt['ext'] == '.MP4':
                to_try['video/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.OGV', 'ext': '.OGV', 'package': attempt['package']})
            else:
                to_try['video/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.ogv', 'ext': '.ogv', 'package': attempt['package']})
    if 'video/ogg' in to_try and 'video/mp4' not in to_try:
        to_try['video/mp4'] = []
        for attempt in to_try['video/ogg']:
            if attempt['ext'] == '.OGV':
                to_try['video/mp4'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.MP4', 'ext': '.MP4', 'package': attempt['package']})
            else:
                to_try['audio/mpeg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.mp4', 'ext': '.mp4', 'package': attempt['package']})
    for mimetype in reversed(sorted(to_try.keys())):
        for attempt in to_try[mimetype]:
            parts = attempt['filename'].split(':')
            if len(parts) < 2:
                parts = [attempt['package'], attempt['filename']]
            parts[1] = re.sub(r'^data/static/', '', parts[1])
            if parts[0] is None:
                full_file = 'data/static/' + parts[1]
            else:
                full_file = parts[0] + ':data/static/' + parts[1]
            file_info = file_finder(full_file, question=question)
            if 'fullpath' in file_info:
                url = url_finder(full_file, _question=question)
                if url is not None:
                    output.append([url, mimetype])
    return output


def process_target(text):
    return re.sub(r'\[TARGET ([^\]]+)\]', target_html, text)


def to_text(html_doc, terms, links):
    output = ""
    # logmessage("to_text: html doc is " + str(html_doc))
    if not html_doc.startswith('<'):
        html_doc = "<span>" + html_doc + "</span>"
    soup = BeautifulSoup(html_doc, 'html.parser')
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title', 'audio', 'video', 'pre', 'attribution'])]  # pylint: disable=expression-not-assigned
    [s.extract() for s in soup.find_all(hidden)]  # pylint: disable=expression-not-assigned
    [s.extract() for s in soup.find_all('div', {'class': 'dainvisible'})]  # pylint: disable=expression-not-assigned
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
        if s.has_attr('class') and s.attrs['class'][0] == 'daterm' and s.has_attr('data-bs-content'):
            terms[s.string] = s.attrs['data-bs-content']
        elif s.has_attr('href'):  # and (s.attrs['href'].startswith(url) or s.attrs['href'].startswith('?')):
            # logmessage("Adding a link: " + s.attrs['href'])
            links.append((s.attrs['href'], s.get_text()))
    output = re.sub(br'\u201c'.decode('raw_unicode_escape'), '"', output)
    output = re.sub(br'\u201d'.decode('raw_unicode_escape'), '"', output)
    output = re.sub(br'\u2018'.decode('raw_unicode_escape'), "'", output)
    output = re.sub(br'\u2019'.decode('raw_unicode_escape'), "'", output)
    output = re.sub(br'\u201b'.decode('raw_unicode_escape'), "'", output)
    output = re.sub(r'&amp;gt;', '>', output)
    output = re.sub(r'&amp;lt;', '<', output)
    output = re.sub(r'&gt;', '>', output)
    output = re.sub(r'&lt;', '<', output)
    output = re.sub(r'<[^>]+>', '', output)
    output = re.sub(r'\n$', '', output)
    output = re.sub(r'  +', ' ', output)
    return output

bad_list = ['div', 'option']

good_list = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'button', 'textarea', 'note']


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
