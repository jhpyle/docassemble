import sys
import re
import os
import markdown
import mimetypes
import codecs
import json
import qrcode
import qrcode.image.svg
from io import BytesIO
import tempfile
import types
import time
import stat
import PyPDF2
from docassemble.base.functions import server, word
import docassemble.base.functions
import docassemble.base.pandoc as pandoc
from bs4 import BeautifulSoup
import docassemble.base.file_docx
from pylatex.utils import escape_latex
from pathlib import Path
import subprocess

QPDF_PATH = 'qpdf'
NoneType = type(None)

from docassemble.base.logger import logmessage
from docassemble.base.rtfng.object.picture import Image
import PIL
zerowidth = '\u200B'

DEFAULT_PAGE_WIDTH = '6.5in'

term_start = re.compile(r'\[\[')
term_match = re.compile(r'\[\[([^\]\|]*)(\|[^\]]*)?\]\]', re.DOTALL)
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
#amp_match = re.compile(r'&(?!#?[0-9A-Za-z]+;)')
emoji_match = re.compile(r':([A-Za-z][A-Za-z0-9\_\-]+):')
extension_match = re.compile(r'\.[a-z]+$')
map_match = re.compile(r'\[MAP ([^\]]+)\]', flags=re.DOTALL)
code_match = re.compile(r'<code>')

def set_default_page_width(width):
    global DEFAULT_PAGE_WIDTH
    DEFAULT_PAGE_WIDTH = str(width)
    return

def get_default_page_width():
    return(DEFAULT_PAGE_WIDTH)

DEFAULT_IMAGE_WIDTH = '4in'

def set_default_image_width(width):
    global DEFAULT_IMAGE_WIDTH
    DEFAULT_IMAGE_WIDTH = str(width)
    return

def get_default_image_width():
    return(DEFAULT_IMAGE_WIDTH)

MAX_HEIGHT_POINTS = 10 * 72

def set_max_height_points(points):
    global MAX_HEIGHT_POINTS
    MAX_HEIGHT_POINTS = points
    return

def get_max_height_points():
    return(MAX_HEIGHT_POINTS)

MAX_WIDTH_POINTS = 6.5 * 72.0

def set_max_width_points(points):
    global MAX_WIDTH_POINTS
    MAX_WIDTH_POINTS = points
    return

def get_max_width_points():
    return(MAX_WIDTH_POINTS)

# def blank_da_send_mail(*args, **kwargs):
#     logmessage("da_send_mail: no mail agent configured!")
#     return(None)

# da_send_mail = blank_da_send_mail

# def set_da_send_mail(func):
#     global da_send_mail
#     da_send_mail = func
#     return

# def blank_file_finder(*args, **kwargs):
#     return(dict(filename="invalid"))

# file_finder = blank_file_finder

# def set_file_finder(func):
#     global file_finder
#     #sys.stderr.write("set the file finder to " + str(func) + "\n")
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

rtf_spacing = {'tight': r'\\sl0 ', 'single': r'\\sl0 ', 'oneandahalf': r'\\sl360\\slmult1 ', 'double': r'\\sl480\\slmult1 ', 'triple': r'\\sl720\\slmult1 '}

rtf_after_space = {'tight': 0, 'single': 1, 'oneandahalf': 0, 'double': 0, 'triplespacing': 0, 'triple': 0}

def rtf_prefilter(text, metadata=dict()):
    text = re.sub(r'^# ', '[HEADING1] ', text, flags=re.MULTILINE)
    text = re.sub(r'^## ', '[HEADING2] ', text, flags=re.MULTILINE)
    text = re.sub(r'^### ', '[HEADING3] ', text, flags=re.MULTILINE)
    text = re.sub(r'^#### ', '[HEADING4] ', text, flags=re.MULTILINE)
    text = re.sub(r'^##### ', '[HEADING5] ', text, flags=re.MULTILINE)
    text = re.sub(r'^###### ', '[HEADING6] ', text, flags=re.MULTILINE)
    text = re.sub(r'^####### ', '[HEADING7] ', text, flags=re.MULTILINE)
    text = re.sub(r'^######## ', '[HEADING8] ', text, flags=re.MULTILINE)
    text = re.sub(r'^######### ', '[HEADING9] ', text, flags=re.MULTILINE)
    text = re.sub(r'\s*\[VERTICAL_LINE\]\s*', '\n\n[VERTICAL_LINE]\n\n', text)
    text = re.sub(r'\s*\[BREAK\]\s*', '\n\n[BREAK]\n\n', text)
    text = re.sub(r'\s+\[END_TWOCOL\]', '\n\n[END_TWOCOL]', text)
    text = re.sub(r'\s+\[END_CAPTION\]', '\n\n[END_CAPTION]', text)
    text = re.sub(r'\[BEGIN_TWOCOL\]\s+', '[BEGIN_TWOCOL]\n\n', text)
    text = re.sub(r'\[BEGIN_CAPTION\]\s+', '[BEGIN_CAPTION]\n\n', text)
    return(text)

def repeat_along(chars, match):
    output = chars * len(match.group(1))
    #logmessage("Output is " + repr(output))
    return output    

def rtf_filter(text, metadata=None, styles=None, question=None):
    if metadata is None:
        metadata = dict()
    if styles is None:
        styles = dict()
    #sys.stderr.write(text + "\n")
    if 'fontsize' in metadata:
        text = re.sub(r'{\\pard', r'\\fs' + str(convert_length(metadata['fontsize'], 'hp')) + r' {\\pard', text, count=1)
        after_space_multiplier = convert_length(metadata['fontsize'], 'twips')
    else:
        after_space_multiplier = 240
    if 'IndentationAmount' in metadata:
        indentation_amount = str(convert_length(metadata['IndentationAmount'], 'twips'))
    else:
        indentation_amount = '720'
    if 'Indentation' in metadata:
        if metadata['Indentation']:
            default_indentation = True
        else:
            default_indentation = False            
    else:
        default_indentation = True
    if 'SingleSpacing' in metadata and metadata['SingleSpacing']:
        #logmessage("Gi there!")
        default_spacing = 'single'
        if 'Indentation' not in metadata:
            default_indentation = False
    elif 'OneAndAHalfSpacing' in metadata and metadata['OneAndAHalfSpacing']:
        default_spacing = 'oneandahalf'
    elif 'DoubleSpacing' in metadata and metadata['DoubleSpacing']:
        default_spacing = 'double'
    elif 'TripleSpacing' in metadata and metadata['TripleSpacing']:
        default_spacing = 'triple'
    else:
        default_spacing = 'double'
    after_space = after_space_multiplier * rtf_after_space[default_spacing]
    text = re.sub(r'{\\pard \\ql \\f0 \\sa180 \\li0 \\fi0 \[HEADING([0-9]+)\] *', (lambda x: '{\\pard ' + styles.get(x.group(1), '\\ql \\f0 \\sa180 \\li0 \\fi0 ')), text)
    text = re.sub(r'{\\pard \\ql \\f0 \\sa180 \\li0 \\fi0 \[(BEGIN_TWOCOL|BREAK|END_TWOCOL|BEGIN_CAPTION|VERTICAL_LINE|END_CAPTION|TIGHTSPACING|SINGLESPACING|DOUBLESPACING|START_INDENTATION|STOP_INDENTATION|PAGEBREAK|SKIPLINE|NOINDENT|FLUSHLEFT|FLUSHRIGHT|CENTER|BOLDCENTER|INDENTBY[^\]]*)\] *', r'[\1]{\\pard \\ql \\f0 \\sa180 \\li0 \\fi0 ', text)
    text = re.sub(r'{\\pard \\ql \\f0 \\sa180 \\li0 \\fi0 *\\par}', r'', text)
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    # with open('/tmp/asdf.rtf', 'w') as deb_file:
    #     deb_file.write(text)
    text = re.sub(r'\\par}\s*\[(END_TWOCOL|END_CAPTION|BREAK|VERTICAL_LINE)\]', r'}[\1]', text, flags=re.DOTALL)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\s*\[BREAK\]\s*(.+?)\[END_TWOCOL\]', rtf_two_col, text, flags=re.DOTALL)
    text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_as_rtf(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', lambda x: image_as_rtf(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_as_rtf(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+)\]', lambda x: image_as_rtf(x, question=question), text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', qr_as_rtf, text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+)\]', qr_as_rtf, text)
    text = re.sub(r'\[QR ([^\]]+)\]', qr_as_rtf, text)
    text = re.sub(r'\[MAP ([^\]]+)\]', '', text)
    text = replace_fields(text)
    # text = re.sub(r'\[FIELD ([^\]]+)\]', '', text)
    text = re.sub(r'\[TARGET ([^\]]+)\]', '', text)
    text = re.sub(r'\[YOUTUBE[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\[VIMEO[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\s*\[VERTICAL_LINE\]\s*(.+?)\[END_CAPTION\]', rtf_caption_table, text, flags=re.DOTALL)
    text = re.sub(r'\[NBSP\]', r'\\~ ', text)
    text = re.sub(r'\[REDACTION_SPACE\]', r'\\u9608\\zwbo', text)
    text = re.sub(r'\[REDACTION_WORD ([^\]]+)\]', lambda x: repeat_along('\\u9608', x), text)
    text = re.sub(r'\[ENDASH\]', r'{\\endash}', text)
    text = re.sub(r'\[EMDASH\]', r'{\\emdash}', text)
    text = re.sub(r'\[HYPHEN\]', r'-', text)
    text = re.sub(r'\[CHECKBOX\]', r'____', text)
    text = re.sub(r'\[BLANK\]', r'________________', text)
    text = re.sub(r'\[BLANKFILL\]', r'________________', text)
    text = re.sub(r'\[PAGEBREAK\] *', r'\\page ', text)
    text = re.sub(r'\[PAGENUM\]', r'{\\chpgn}', text)
    text = re.sub(r'\[TOTALPAGES\]', r'{\\field{\\*\\fldinst NUMPAGES } {\\fldrslt 1}}', text)
    text = re.sub(r'\[SECTIONNUM\]', r'{\\sectnum}', text)
    text = re.sub(r' *\[SKIPLINE\] *', r'\\line ', text)
    text = re.sub(r' *\[NEWLINE\] *', r'\\line ', text)
    text = re.sub(r' *\[NEWPAR\] *', r'\\par ', text)
    text = re.sub(r' *\[BR\] *', r'\\line ', text)
    text = re.sub(r' *\[TAB\] *', r'\\tab ', text)
    text = re.sub(r' *\[END\] *', r'\n', text)
    text = re.sub(r'\\sa180\\sa180\\par', r'\\par', text)
    text = re.sub(r'\\sa180', r'\\sa0', text)
    text = re.sub(r'(\\trowd \\trgaph[0-9]+)', r'\1\\trqc', text)
    text = re.sub(r'\\intbl\\row}\s*{\\pard', r'\\intbl\\row}\n\\line\n{\\pard', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\s*\[(SAVE|RESTORE|TIGHTSPACING|SINGLESPACING|DOUBLESPACING|TRIPLESPACING|ONEANDAHALFSPACING|START_INDENTATION|STOP_INDENTATION)\]\s*', r'\n[\1]\n', text)
    lines = text.split('\n')
    spacing_command = rtf_spacing[default_spacing]
    if default_indentation:
        indentation_command = r'\\fi' + str(indentation_amount) + " "
    else:
        indentation_command = r'\\fi0 '
    text = ''
    formatting_stack = list()
    for line in lines:
        if re.search(r'\[SAVE\]', line):
            formatting_stack.append(dict(spacing_command=spacing_command, after_space=after_space, default_indentation=default_indentation, indentation_command=indentation_command))
        elif re.search(r'\[RESTORE\]', line):
            if len(formatting_stack):
                prior_values = formatting_stack.pop()
                spacing_command = prior_values['spacing_command']
                after_space = prior_values['after_space']
                default_indentation = prior_values['default_indentation']
                indentation_command = prior_values['indentation_command']
        elif re.search(r'\[TIGHTSPACING\]', line):
            spacing_command = rtf_spacing['tight']
            default_spacing = 'tight'
            after_space = after_space_multiplier * rtf_after_space[default_spacing]
            default_indentation = False
        elif re.search(r'\[SINGLESPACING\]', line):
            spacing_command = rtf_spacing['single']
            default_spacing = 'single'
            after_space = after_space_multiplier * rtf_after_space[default_spacing]
            default_indentation = False
        elif re.search(r'\[ONEANDAHALFSPACING\]', line):
            spacing_command = rtf_spacing['oneandahalf']
            default_spacing = 'oneandahalf'
            after_space = after_space_multiplier * rtf_after_space[default_spacing]
        elif re.search(r'\[DOUBLESPACING\]', line):
            spacing_command = rtf_spacing['double']
            default_spacing = 'double'
            after_space = after_space_multiplier * rtf_after_space[default_spacing]
        elif re.search(r'\[TRIPLESPACING\]', line):
            spacing_command = rtf_spacing['triple']
            default_spacing = 'triple'
            after_space = after_space_multiplier * rtf_after_space[default_spacing]
        elif re.search(r'\[START_INDENTATION\]', line):
            indentation_command = r'\\fi' + str(indentation_amount) + " "
        elif re.search(r'\[STOP_INDENTATION\]', line):
            indentation_command = r'\\fi0 '
        elif line != '':
            special_after_space = None
            special_spacing = None
            if re.search(r'\[BORDER\]', line):
                line = re.sub(r' *\[BORDER\] *', r'', line)
                border_text = r'\\box \\brdrhair \\brdrw1 \\brdrcf1 \\brsp29 '
            else:
                border_text = r''
            line = re.sub(r'{(\\pard\\intbl \\q[lrc] \\f[0-9]+ \\sa[0-9]+ \\li[0-9]+ \\fi[0-9]+.*?)\\par}', r'\1', line)
            if re.search(r'\[NOPAR\]', line):
                line = re.sub(r'{\\pard \\ql \\f[0-9]+ \\sa[0-9]+ \\li[0-9]+ \\fi-?[0-9]* *(.*?)\\par}', r'\1', line)
                line = re.sub(r' *\[NOPAR\] *', r'', line)
            n = re.search(r'\[INDENTBY *([0-9\.]+ *[A-Za-z]+) *([0-9\.]+ *[A-Za-z]+)\]', line)
            m = re.search(r'\[INDENTBY *([0-9\.]+ *[A-Za-z]+)\]', line)
            if n:
                line = re.sub(r'\\fi-?[0-9]+ ', r'\\fi0 ', line)
                line = re.sub(r'\\ri-?[0-9]+ ', r'', line)
                line = re.sub(r'\\li-?[0-9]+ ', r'\\li' + str(convert_length(n.group(1), 'twips')) + r' \\ri' + str(convert_length(n.group(2), 'twips')) + ' ', line)
                line = re.sub(r'\[INDENTBY[^\]]*\]', '', line)
            elif m:
                line = re.sub(r'\\fi-?[0-9]+ ', r'\\fi0 ', line)
                line = re.sub(r'\\li-?[0-9]+ ', r'\\li' + str(convert_length(m.group(1), 'twips')) + ' ', line)
                line = re.sub(r' *\[INDENTBY[^\]]*\] *', '', line)
            elif re.search(r'\[NOINDENT\]', line):
                line = re.sub(r'\\fi-?[0-9]+ ', r'\\fi0 ', line)
                line = re.sub(r' *\[NOINDENT\] *', '', line)
            elif re.search(r'\[FLUSHLEFT\]', line):
                line = re.sub(r'\\fi-?[0-9]+ ', r'\\fi0 ', line)
                line = re.sub(r' *\[FLUSHLEFT\] *', '', line)
                special_after_space = after_space_multiplier * 1
                special_spacing = rtf_spacing['single']
            elif re.search(r'\[FLUSHRIGHT\]', line):
                line = re.sub(r'\\fi-?[0-9]+ ', r'\\fi0 ', line)
                line = re.sub(r'\\ql', r'\\qr', line)
                line = re.sub(r' *\[FLUSHRIGHT\] *', '', line)
                special_after_space = after_space_multiplier * 1
                special_spacing = rtf_spacing['single']
            elif re.search(r'\[CENTER\]', line):
                line = re.sub(r'\\fi-?[0-9]+ ', r'\\fi0 ', line)
                line = re.sub(r'\\ql', r'\\qc', line)
                line = re.sub(r' *\[CENTER\] *', '', line)
            elif re.search(r'\[BOLDCENTER\]', line):
                line = re.sub(r'\\fi-?[0-9]+ ', r'\\fi0 ', line)
                line = re.sub(r'\\ql', r'\\qc \\b', line)
                line = re.sub(r' *\[BOLDCENTER\] *', '', line)
            elif indentation_command != '' and not re.search(r'\\widctlpar', line):
                line = re.sub(r'\\fi-?[0-9]+ ', indentation_command, line)
            if not re.search(r'\\s[0-9]', line):
                if special_spacing:
                    spacing_command_to_use = special_spacing
                else:
                    spacing_command_to_use = spacing_command
                line = re.sub(r'\\pard ', r'\\pard ' + str(spacing_command_to_use) + str(border_text), line)
                line = re.sub(r'\\pard\\intbl ', r'\\pard\\intbl ' + str(spacing_command_to_use) + str(border_text), line)
            if not (re.search(r'\\fi0\\(endash|bullet)', line) or re.search(r'\\s[0-9]', line) or re.search(r'\\intbl', line)):
                if special_after_space:
                    after_space_to_use = special_after_space
                else:
                    after_space_to_use = after_space
                if after_space_to_use > 0:
                    line = re.sub(r'\\sa[0-9]+ ', r'\\sa' + str(after_space_to_use) + ' ', line)
                else:
                    line = re.sub(r'\\sa[0-9]+ ', r'\\sa0 ', line)
            text += line + '\n'
    text = re.sub(r'{\\pard \\sl[0-9]+\\slmult[0-9]+ \\ql \\f[0-9]+ \\sa[0-9]+ \\li[0-9]+ \\fi-?[0-9]*\s*\\par}', r'', text)
    text = re.sub(r'\[MANUALSKIP\]', r'{\\pard \\sl0 \\ql \\f0 \\sa0 \\li0 \\fi0 \\par}', text)
    return(text)

def docx_filter(text, metadata=None, question=None):
    if metadata is None:
        metadata = dict()
    text = text + "\n\n"
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_include_docx(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', lambda x: image_include_docx(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_include_docx(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+)\]', lambda x: image_include_docx(x, question=question), text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', qr_include_docx, text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+)\]', qr_include_docx, text)
    text = re.sub(r'\[QR ([^\]]+)\]', qr_include_docx, text)
    text = re.sub(r'\[MAP ([^\]]+)\]', '', text)
    text = replace_fields(text)
    # text = re.sub(r'\[FIELD ([^\]]+)\]', '', text)
    text = re.sub(r'\[TARGET ([^\]]+)\]', '', text)
    text = re.sub(r'\[YOUTUBE[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\[VIMEO[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\\clearpage *\\clearpage', '', text)
    text = re.sub(r'\[START_INDENTATION\]', '', text)
    text = re.sub(r'\[STOP_INDENTATION\]', '', text)    
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\[VERTICAL_LINE\]\s*(.+?)\[END_CAPTION\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\[BREAK\]\s*(.+?)\[END_TWOCOL\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[TIGHTSPACING\] *', '', text)
    text = re.sub(r'\[SINGLESPACING\] *', '', text)
    text = re.sub(r'\[DOUBLESPACING\] *', '', text)
    text = re.sub(r'\[ONEANDAHALFSPACING\] *', '', text)
    text = re.sub(r'\[TRIPLESPACING\] *', '', text)
    text = re.sub(r'\[NBSP\]', ' ', text)
    text = re.sub(r'\[REDACTION_SPACE\]', '█​', text)
    text = re.sub(r'\[REDACTION_WORD ([^\]]+)\]', lambda x: repeat_along('█', x), text)
    text = re.sub(r'\[ENDASH\]', '--', text)
    text = re.sub(r'\[EMDASH\]', '---', text)
    text = re.sub(r'\[HYPHEN\]', '-', text)
    text = re.sub(r'\[CHECKBOX\]', '____', text)
    text = re.sub(r'\[BLANK\]', r'__________________', text)
    text = re.sub(r'\[BLANKFILL\]', r'__________________', text)
    text = re.sub(r'\[PAGEBREAK\] *', '', text)
    text = re.sub(r'\[PAGENUM\] *', '', text)
    text = re.sub(r'\[TOTALPAGES\] *', '', text)
    text = re.sub(r'\[SECTIONNUM\] *', '', text)
    text = re.sub(r'\[SKIPLINE\] *', '\n\n', text)
    text = re.sub(r'\[VERTICALSPACE\] *', '\n\n', text)
    text = re.sub(r'\[NEWLINE\] *', '\n\n', text)
    text = re.sub(r'\[NEWPAR\] *', '\n\n', text)
    text = re.sub(r'\[BR\] *', '\n\n', text)
    text = re.sub(r'\[TAB\] *', '', text)
    text = re.sub(r' *\[END\] *', r'\n', text)
    text = re.sub(r'\[BORDER\] *(.+?)\n *\n', r'\1\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[NOINDENT\] *(.+?)\n *\n', r'\1\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[FLUSHLEFT\] *(.+?)\n *\n', r'\1\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[FLUSHRIGHT\] *(.+?)\n *\n', r'\1\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[CENTER\] *(.+?)\n *\n', r'\1\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BOLDCENTER\] *(.+?)\n *\n', r'**\1**\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[INDENTBY *([0-9]+ *[A-Za-z]+)\] *(.+?)\n *\n', r'\2', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[INDENTBY *([0-9]+ *[A-Za-z]+) *([0-9]+ *[A-Za-z]+)\] *(.+?)\n *\n', r'\3', text, flags=re.MULTILINE | re.DOTALL)
    return(text)

def docx_template_filter(text, question=None):
    #logmessage('docx_template_filter')
    if text == 'True':
        return True
    elif text == 'False':
        return False
    elif text == 'None':
        return None
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_include_docx_template(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', lambda x: image_include_docx_template(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_include_docx_template(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+)\]', lambda x: image_include_docx_template(x, question=question), text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', qr_include_docx_template, text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+)\]', qr_include_docx_template, text)
    text = re.sub(r'\[QR ([^\]]+)\]', qr_include_docx_template, text)
    text = re.sub(r'\[MAP ([^\]]+)\]', '', text)
    text = replace_fields(text)
    # text = re.sub(r'\[FIELD ([^\]]+)\]', '', text)
    text = re.sub(r'\[TARGET ([^\]]+)\]', '', text)
    text = re.sub(r'\[YOUTUBE[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\[VIMEO[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\\clearpage *\\clearpage', '', text)
    text = re.sub(r'\[START_INDENTATION\]', '', text)
    text = re.sub(r'\[STOP_INDENTATION\]', '', text)    
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\[VERTICAL_LINE\]\s*(.+?)\[END_CAPTION\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\[BREAK\]\s*(.+?)\[END_TWOCOL\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[TIGHTSPACING\] *', '', text)
    text = re.sub(r'\[SINGLESPACING\] *', '', text)
    text = re.sub(r'\[DOUBLESPACING\] *', '', text)
    text = re.sub(r'\[ONEANDAHALFSPACING\] *', '', text)
    text = re.sub(r'\[TRIPLESPACING\] *', '', text)
    text = re.sub(r'\[NBSP\]', ' ', text)
    text = re.sub(r'\[REDACTION_SPACE\]', r'█​', text)
    #text = re.sub(r'\[REDACTION_SPACE\]', r'', text)
    text = re.sub(r'\[REDACTION_WORD ([^\]]+)\]', lambda x: repeat_along('█', x), text)
    #text = re.sub(r'\[REDACTION_WORD ([^\]]+)\]', lambda x: repeat_along('X', x), text)
    text = re.sub(r'\[ENDASH\]', '--', text)
    text = re.sub(r'\[EMDASH\]', '---', text)
    text = re.sub(r'\[HYPHEN\]', '-', text)
    text = re.sub(r'\\', '', text)
    text = re.sub(r'\[CHECKBOX\]', '____', text)
    text = re.sub(r'\[BLANK\]', r'__________________', text)
    text = re.sub(r'\[BLANKFILL\]', r'__________________', text)
    text = re.sub(r'\[PAGEBREAK\] *', '', text)
    text = re.sub(r'\[PAGENUM\] *', '', text)
    text = re.sub(r'\[TOTALPAGES\] *', '', text)
    text = re.sub(r'\[SECTIONNUM\] *', '', text)
    text = re.sub(r'\[SKIPLINE\] *', '</w:t><w:br/><w:t xml:space="preserve">', text)
    text = re.sub(r'\[VERTICALSPACE\] *', '</w:t><w:br/><w:br/><w:t xml:space="preserve">', text)
    text = re.sub(r'\[NEWLINE\] *', '</w:t><w:br/><w:t xml:space="preserve">', text)
    #text = re.sub(r'\n *\n', '[NEWPAR]', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\[NEWPAR\] *', '</w:t><w:br/><w:br/><w:t xml:space="preserve">', text)
    text = re.sub(r'\[TAB\] *', '\t', text)
    text = re.sub(r'\[NEWPAR\]', '</w:t><w:br/><w:br/><w:t xml:space="preserve">', text)
    text = re.sub(r' *\[END\] *', r'</w:t><w:br/><w:t xml:space="preserve">', text)
    text = re.sub(r'\[BORDER\] *', r'', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[NOINDENT\] *', r'', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[FLUSHLEFT\] *', r'', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[FLUSHRIGHT\] *', r'', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[CENTER\] *', r'', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BOLDCENTER\] *', r'', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[INDENTBY *([0-9]+ *[A-Za-z]+)\] *(.+?)\n *\n', r'\2', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[INDENTBY *([0-9]+ *[A-Za-z]+) *([0-9]+ *[A-Za-z]+)\] *(.+?)\n *\n', r'\3', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BR\]', '</w:t><w:br/><w:t xml:space="preserve">', text)
    text = re.sub(r'\[SKIPLINE\]', '</w:t><w:br/><w:t xml:space="preserve">', text)
    text = re.sub(r'{([{%#])', '{' + zerowidth + r'\1', re.sub(r'([}%#])}', r'\1' + zerowidth + '}', text))
    return(text)

def metadata_filter(text, doc_format):
    if doc_format == 'pdf':
        text = re.sub(r'\*\*([^\*]+?)\*\*', r'\\begingroup\\bfseries \1\\endgroup {}', text, flags=re.MULTILINE | re.DOTALL)
        text = re.sub(r'\*([^\*]+?)\*', r'\\begingroup\\itshape \1\\endgroup {}', text, flags=re.MULTILINE | re.DOTALL)
        text = re.sub(r'\_\_([^\_]+?)\_\_', r'\\begingroup\\bfseries \1\\endgroup {}', text, flags=re.MULTILINE | re.DOTALL)
        text = re.sub(r'\_([^\_]+?)\_*', r'\\begingroup\\itshape \1\\endgroup {}', text, flags=re.MULTILINE | re.DOTALL)
    return text

def redact_latex(match):
    return '\\redactword{' + str(escape_latex(match.group(1))) + '}'

def pdf_filter(text, metadata=None, question=None):
    if metadata is None:
        metadata = dict()
    #if len(metadata):
    #    text = yaml.dump(metadata) + "\n---\n" + text
    text = text + "\n\n"
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_include_string(x, emoji=True, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', lambda x: image_include_string(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+), *([0-9A-Za-z.%]+)\]', lambda x: image_include_string(x, question=question), text)
    text = re.sub(r'\[FILE ([^,\]]+)\]', lambda x: image_include_string(x, question=question), text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+), *([^\]]*)\]', qr_include_string, text)
    text = re.sub(r'\[QR ([^,\]]+), *([0-9A-Za-z.%]+)\]', qr_include_string, text)
    text = re.sub(r'\[QR ([^\]]+)\]', qr_include_string, text)
    text = re.sub(r'\[MAP ([^\]]+)\]', '', text)
    text = replace_fields(text)
    # text = re.sub(r'\[FIELD ([^\]]+)\]', '', text)
    text = re.sub(r'\[TARGET ([^\]]+)\]', '', text)
    text = re.sub(r'\[YOUTUBE[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\[VIMEO[^ ]* ([^\]]+)\]', '', text)
    text = re.sub(r'\$\$+', '$', text)
    text = re.sub(r'\\clearpage *\\clearpage', r'\\clearpage', text)
    text = re.sub(r'\[BORDER\]\s*\[(BEGIN_TWOCOL|BEGIN_CAPTION|TIGHTSPACING|SINGLESPACING|DOUBLESPACING|START_INDENTATION|STOP_INDENTATION|NOINDENT|FLUSHLEFT|FLUSHRIGHT|CENTER|BOLDCENTER|INDENTBY[^\]]*)\]', r'[\1] [BORDER]', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[START_INDENTATION\]', r'\\setlength{\\parindent}{\\myindentamount}\\setlength{\\RaggedRightParindent}{\\parindent}', text)    
    text = re.sub(r'\[STOP_INDENTATION\]', r'\\setlength{\\parindent}{0in}\\setlength{\\RaggedRightParindent}{\\parindent}', text)    
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\[VERTICAL_LINE\]\s*(.+?)\[END_CAPTION\]', pdf_caption, text, flags=re.DOTALL)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\[BREAK\]\s*(.+?)\[END_TWOCOL\]', pdf_two_col, text, flags=re.DOTALL)
    text = re.sub(r'\[TIGHTSPACING\]\s*', r'\\singlespacing\\setlength{\\parskip}{0pt}\\setlength{\\parindent}{0pt}\\setlength{\\RaggedRightParindent}{\\parindent}', text)
    text = re.sub(r'\[SINGLESPACING\]\s*', r'\\singlespacing\\setlength{\\parskip}{\\myfontsize}\\setlength{\\parindent}{0pt}\\setlength{\\RaggedRightParindent}{\\parindent}', text)
    text = re.sub(r'\[DOUBLESPACING\]\s*', r'\\doublespacing\\setlength{\\parindent}{\\myindentamount}\\setlength{\\RaggedRightParindent}{\\parindent}', text)
    text = re.sub(r'\[ONEANDAHALFSPACING\]\s*', r'\\onehalfspacing\\setlength{\\parindent}{\\myindentamount}\\setlength{\\RaggedRightParindent}{\\parindent}', text)
    text = re.sub(r'\[TRIPLESPACING\]\s*', r'\\setlength{\\parindent}{\\myindentamount}\\setlength{\\RaggedRightParindent}{\\parindent}', text)
    text = re.sub(r'\[NBSP\]', r'\\myshow{\\nonbreakingspace}', text)
    text = re.sub(r'\[REDACTION_SPACE\]', r'\\redactword{~}\\hspace{0pt}', text)
    text = re.sub(r'\[REDACTION_WORD ([^\]]+)\]', redact_latex, text)
    text = re.sub(r'\[ENDASH\]', r'\\myshow{\\myendash}', text)
    text = re.sub(r'\[EMDASH\]', r'\\myshow{\\myemdash}', text)
    text = re.sub(r'\[HYPHEN\]', r'\\myshow{\\myhyphen}', text)
    text = re.sub(r'\[CHECKBOX\]', r'{\\rule{0.3in}{0.4pt}}', text)
    text = re.sub(r'\[BLANK\]', r'\\leavevmode{\\xrfill[-2pt]{0.4pt}}', text)
    text = re.sub(r'\[BLANKFILL\]', r'\\leavevmode{\\xrfill[-2pt]{0.4pt}}', text)
    text = re.sub(r'\[PAGEBREAK\]\s*', r'\\clearpage ', text)
    text = re.sub(r'\[PAGENUM\]', r'\\myshow{\\thepage\\xspace}', text)
    text = re.sub(r'\[TOTALPAGES\]', r'\\myshow{\\pageref*{LastPage}\\xspace}', text)
    text = re.sub(r'\[SECTIONNUM\]', r'\\myshow{\\thesection\\xspace}', text)
    text = re.sub(r'\s*\[SKIPLINE\]\s*', r'\\par\\myskipline ', text)
    text = re.sub(r'\[VERTICALSPACE\] *', r'\\rule[-24pt]{0pt}{0pt}', text)
    text = re.sub(r'\[NEWLINE\] *', r'\\newline ', text)
    text = re.sub(r'\[NEWPAR\] *', r'\\par ', text)
    text = re.sub(r'\[BR\] *', r'\\manuallinebreak ', text)
    text = re.sub(r'\[TAB\] *', r'\\manualindent ', text)
    text = re.sub(r' *\[END\] *', r'\n', text)
    text = re.sub(r'\[NOINDENT\] *', r'\\noindent ', text)
    text = re.sub(r'\[FLUSHLEFT\] *(.+?)\n *\n', flushleft_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[FLUSHRIGHT\] *(.+?)\n *\n', flushright_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[CENTER\] *(.+?)\n *\n', center_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BOLDCENTER\] *(.+?)\n *\n', boldcenter_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[INDENTBY *([0-9]+ *[A-Za-z]+)\] *(.+?)\n *\n', indentby_left_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[INDENTBY *([0-9]+ *[A-Za-z]+) *([0-9]+ *[A-Za-z]+)\] *(.+?)\n *\n', indentby_both_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BORDER\] *(.+?)\n *\n', border_pdf, text, flags=re.MULTILINE | re.DOTALL)
    return(text)

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
    if docassemble.base.functions.this_thread.evaluation_context != 'docx':
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
    text = re.sub(r'\[TIGHTSPACING\] *', r'', text)
    text = re.sub(r'\[SINGLESPACING\] *', r'', text)
    text = re.sub(r'\[DOUBLESPACING\] *', r'', text)
    text = re.sub(r'\[ONEANDAHALFSPACING\] *', '', text)
    text = re.sub(r'\[TRIPLESPACING\] *', '', text)
    text = re.sub(r'\[START_INDENTATION\] *', r'', text)
    text = re.sub(r'\[STOP_INDENTATION\] *', r'', text)
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
    for line in lines:
        classes = set()
        styles = dict()
        if re.search(r'\[BORDER\]', line):
            classes.add('daborder')
        if re.search(r'\[NOINDENT\]', line):
            classes.add('daflushleft')
        if re.search(r'\[FLUSHLEFT\]', line):
            classes.add('daflushleft')
        if re.search(r'\[FLUSHRIGHT\]', line):
            classes.add('daflushright')
        if re.search(r'\[CENTER\]', line):
            classes.add('dacenter')
        if re.search(r'\[BOLDCENTER\]', line):
            classes.add('dacenter')
            classes.add('dabold')
        m = re.search(r'\[INDENTBY *([0-9]+ *[A-Za-z]+)\]', line)
        if m:
            styles["padding-left"] = str(convert_length(m.group(1), 'px')) + 'px'
        m = re.search(r'\[INDENTBY *([0-9]+ *[A-Za-z]+) *([0-9]+ *[A-Za-z]+)\]', line)
        if m:
            styles["margin-left"] = str(convert_length(m.group(1), 'px')) + 'px'
            styles["margin-right"] = str(convert_length(m.group(2), 'px')) + 'px'
        line = re.sub(r'\[(BORDER|NOINDENT|FLUSHLEFT|FLUSHRIGHT|BOLDCENTER|CENTER)\] *', r'', line)
        line = re.sub(r'\[INDENTBY[^\]]*\]', r'', line)
        if len(classes) or len(styles):
            text += "<p"
            if len(classes):
                text += ' class="' + " ".join(classes) + '"'
            if len(styles):
                text += ' style="' + "".join(map(lambda x: str(x) + ":" + styles[x] + ';', styles.keys())) + '"'
            text += ">" + line + '</p>\n\n'
        else:
            text += line + '\n\n'
    text = re.sub(r'\\_', r'__', text)
    text = re.sub(r'\n+$', r'', text)
    return(text)

def clean_markdown_to_latex(string):
    string = re.sub(r'\s*\[SKIPLINE\]\s*', r'\\par\\myskipline ', string)
    string = re.sub(r'^[\n ]+', '', string)
    string = re.sub(r'[\n ]+$', '', string)
    string = re.sub(r' *\n *$', '\n', string)
    string = re.sub(r'\n{2,}', '[NEWLINE]', string)
    string = re.sub(r'\[BR\]', '[NEWLINE]', string)
    string = re.sub(r'\[(NOINDENT|FLUSHLEFT|FLUSHRIGHT|CENTER|BOLDCENTER|TIGHTSPACING|SINGLESPACING|DOUBLESPACING|START_INDENTATION|STOP_INDENTATION|PAGEBREAK)\]\s*', '', string)
    string = re.sub(r'\*\*([^\*]+?)\*\*', r'\\textbf{\1}', string)
    string = re.sub(r'\*([^\*]+?)\*', r'\\emph{\1}', string)
    string = re.sub(r'(?<!\\)_([^_]+?)_', r'\\emph{\1}', string)
    string = re.sub(r'\[([^\]]+?)\]\(([^\)]+?)\)', r'\\href{\2}{\1}', string)
    return string;

def map_string(encoded_text, status):
    if status is None:
        return ''
    map_number = len(status.maps)
    status.maps.append(codecs.decode(bytearray(encoded_text, 'utf-8'), 'base64').decode())
    return '<div id="map' + str(map_number) + '" class="dagoogleMap"></div>'

def target_html(match):
    target = match.group(1)
    target = re.sub(r'[^A-Za-z0-9\_]', r'', str(target))
    return '<span class="datarget' + target + '"></span>'

def pdf_two_col(match, add_line=False):
    firstcol = clean_markdown_to_latex(match.group(1))
    secondcol = clean_markdown_to_latex(match.group(2))
    if add_line:
        return '\\noindent\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\mynoindent\\begin{tabular}{@{}m{0.49\\textwidth}|@{\\hspace{1em}}m{0.49\\textwidth}@{}}{' + firstcol + '} & {' + secondcol + '} \\\\ \\end{tabular}\\endgroup\\myskipline'
    else:
        return '\\noindent\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\mynoindent\\begin{tabular}{@{}m{0.49\\textwidth}@{\\hspace{1em}}m{0.49\\textwidth}@{}}{' + firstcol + '} & {' + secondcol + '} \\\\ \\end{tabular}\\endgroup\\myskipline'

def html_caption(match):
    firstcol = match.group(1)
    secondcol = match.group(2)
    firstcol = re.sub(r'^\s+', '', firstcol)
    firstcol = re.sub(r'\s+$', '', firstcol)
    secondcol = re.sub(r'^\s+', '', secondcol)
    secondcol = re.sub(r'\s+$', '', secondcol)
    firstcol = re.sub(r'\n{2,}', '<br>', firstcol)
    secondcol = re.sub(r'\n{2,}', '<br>', secondcol)
    return '<table style="width: 100%"><tr><td style="width: 50%; border-style: solid; border-right-width: 1px; padding-right: 1em; border-left-width: 0px; border-top-width: 0px; border-bottom-width: 0px">' + firstcol + '</td><td style="padding-left: 1em; width: 50%;">' + secondcol + '</td></tr></table>'

def html_two_col(match):
    firstcol = markdown_to_html(match.group(1))
    secondcol = markdown_to_html(match.group(2))
    return '<table style="width: 100%"><tr><td style="width: 50%; vertical-align: top; border-style: none; padding-right: 1em;">' + firstcol + '</td><td style="padding-left: 1em; vertical-align: top; width: 50%;">' + secondcol + '</td></tr></table>'

def pdf_caption(match):
    return pdf_two_col(match, add_line=False)

def add_newlines(string):
    string = re.sub(r'\[(BR)\]', r'[NEWLINE]', string)
    string = re.sub(r' *\n', r'\n', string)
    string = re.sub(r'(?<!\[NEWLINE\])\n', r' [NEWLINE]\n', string)
    return string    

def border_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return('\\mdframed\\setlength{\\parindent}{0pt} ' + str(string) + '\n\n\\endmdframed' + "\n\n")

def flushleft_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return borderify('\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\setlength{\\parindent}{0pt}\\noindent ' + str(string) + '\\par\\endgroup') + "\n\n"

def flushright_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return borderify('\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\setlength{\\parindent}{0pt}\\RaggedLeft ' + str(string) + '\\par\\endgroup') + "\n\n"

def center_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return borderify('\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\Centering\\noindent ' + str(string) + '\\par\\endgroup') + "\n\n"

def boldcenter_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return borderify('\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\Centering\\bfseries\\noindent ' + str(string) + '\\par\\endgroup') + "\n\n"

def indentby_left_pdf(match):
    string = match.group(2)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    if re.search(r'\[BORDER\]', string):
        string = re.sub(r' *\[BORDER\] *', r'', string)
        return '\\mdframed[leftmargin=' + str(convert_length(match.group(1), 'pt')) + 'pt]\n\\noindent ' + str(string) + '\n\n\\endmdframed' + "\n\n"
    return '\\begingroup\\setlength{\\leftskip}{' + str(convert_length(match.group(1), 'pt')) + 'pt}\\noindent ' + str(string) + '\\par\\endgroup' + "\n\n"

def indentby_both_pdf(match):
    string = match.group(3)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    if re.search(r'\[BORDER\]', string):
        string = re.sub(r' *\[BORDER\] *', r'', string)
        return '\\mdframed[leftmargin=' + str(convert_length(match.group(1), 'pt')) + 'pt,rightmargin=' + str(convert_length(match.group(2), 'pt')) + 'pt]\n\\noindent ' + str(string) + '\n\n\\endmdframed' + "\n\n"
    return '\\begingroup\\setlength{\\leftskip}{' + str(convert_length(match.group(1), 'pt')) + 'pt}\\setlength{\\rightskip}{' + str(convert_length(match.group(2), 'pt')) + 'pt}\\noindent ' + str(string) + '\\par\\endgroup' + "\n\n"

def borderify(string):
    if not re.search(r'\[BORDER\]', string):
        return string
    string = re.sub(r'\[BORDER\] *', r'', string)
    return('\\mdframed ' + str(string) + '\\endmdframed')

def safe_pypdf_reader(filename):
    try:
        return PyPDF2.PdfFileReader(open(filename, 'rb'))
    except PyPDF2.utils.PdfReadError:
        new_filename = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
        qpdf_subprocess_arguments = [QPDF_PATH, filename, new_filename.name]
        try:
            result = subprocess.run(qpdf_subprocess_arguments, timeout=60).returncode
        except subprocess.TimeoutExpired:
            result = 1
        if result != 0:
            raise Exception("Call to qpdf failed for template " + str(filename) + " where arguments were " + " ".join(qpdf_subprocess_arguments))
        return PyPDF2.PdfFileReader(open(new_filename.name, 'rb'))

def image_as_rtf(match, question=None):
    width_supplied = False
    try:
        width = match.group(2)
        assert width != 'None'
        width_supplied = True
    except:
        width = DEFAULT_IMAGE_WIDTH
    if width == 'full':
        width_supplied = False
    file_reference = match.group(1)
    if question and file_reference in question.interview.images:
        file_reference = question.interview.images[file_reference].get_reference()
    file_info = server.file_finder(file_reference, convert={'svg': 'png', 'gif': 'png'}, question=question)
    if 'path' not in file_info:
        return ''
    #logmessage('image_as_rtf: path is ' + file_info['path'])
    if 'mimetype' in file_info and file_info['mimetype']:
        if re.search(r'^(audio|video)', file_info['mimetype']):
            return '[reference to file type that cannot be displayed]'
    if 'width' in file_info:
        try:
            return rtf_image(file_info, width, False)
        except:
            return '[graphic could not be inserted]'
    elif file_info['extension'] in ('pdf', 'docx', 'rtf', 'doc', 'odt'):
        output = ''
        if not width_supplied:
            #logmessage("image_as_rtf: Adding page break\n")
            width = DEFAULT_PAGE_WIDTH
            #output += '\\page '
        #logmessage("image_as_rtf: maxpage is " + str(int(file_info['pages'])) + "\n")
        if not os.path.isfile(file_info['path'] + '.pdf'):
            if file_info['extension'] in ('docx', 'rtf', 'doc', 'odt') and not os.path.isfile(file_info['path'] + '.pdf'):
                server.fg_make_pdf_for_word_path(file_info['path'], file_info['extension'])
        if 'pages' not in file_info:
            try:
                reader = safe_pypdf_reader(file_info['path'] + '.pdf')
                file_info['pages'] = reader.getNumPages()
            except:
                file_info['pages'] = 1
        max_pages = 1 + int(file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        for page in range(1, max_pages):
            #logmessage("image_as_rtf: doing page " + str(page) + "\n")
            page_file = dict()
            test_path = file_info['path'] + 'page-in-progress'
            #logmessage("Test path is " + test_path)
            if os.path.isfile(test_path):
                #logmessage("image_as_rtf: test path " + test_path + " exists")
                while (os.path.isfile(test_path) and time.time() - os.stat(test_path)[stat.ST_MTIME]) < 30:
                    #logmessage("Waiting for test path to go away")
                    if not os.path.isfile(test_path):
                        break
                    time.sleep(1)
            page_file['extension'] = 'png'
            page_file['path'] = file_info['path'] + 'page-' + formatter % page
            page_file['fullpath'] = page_file['path'] + '.png'
            if not os.path.isfile(page_file['fullpath']):
                server.fg_make_png_for_pdf_path(file_info['path'] + '.pdf', 'page')
            if os.path.isfile(page_file['fullpath']):
                im = PIL.Image.open(page_file['fullpath'])
                page_file['width'], page_file['height'] = im.size
                output += rtf_image(page_file, width, False)
            else:
                output += "[Error including page image]"
            # if not width_supplied:
            #     #logmessage("Adding page break\n")
            #     output += '\\page '
            # else:
            output += ' '
        #logmessage("Returning output\n")
        return(output)
    else:
        return('')

def qr_as_rtf(match):
    width_supplied = False
    try:
        width = match.group(2)
        assert width != 'None'
        width_supplied = True
    except:
        width = DEFAULT_IMAGE_WIDTH
    if width == 'full':
        width_supplied = False
    string = match.group(1)
    output = ''
    if not width_supplied:
        #logmessage("Adding page break\n")
        width = DEFAULT_PAGE_WIDTH
        output += '\\page '
    im = qrcode.make(string)
    the_image = tempfile.NamedTemporaryFile(suffix=".png")
    im.save(the_image.name)
    page_file = dict()
    page_file['extension'] = 'png'
    page_file['fullpath'] = the_image.name    
    page_file['width'], page_file['height'] = im.size
    output += rtf_image(page_file, width, False)
    if not width_supplied:
        #logmessage("Adding page break\n")
        output += '\\page '
    else:
        output += ' '
    #logmessage("Returning output\n")
    return(output)

def rtf_image(file_info, width, insert_page_breaks):
    pixels = pixels_in(width)
    if pixels > 0 and file_info['width'] > 0:
        scale = float(pixels)/float(file_info['width'])
        #logmessage("scale is " + str(scale) + "\n")
        if scale*float(file_info['height']) > float(MAX_HEIGHT_POINTS):
            scale = float(MAX_HEIGHT_POINTS)/float(file_info['height'])
        #logmessage("scale is " + str(scale) + "\n")
        if scale*float(file_info['width']) > float(MAX_WIDTH_POINTS):
            scale = float(MAX_WIDTH_POINTS)/float(file_info['width'])
        #logmessage("scale is " + str(scale) + "\n")
        #scale *= 100.0
        #logmessage("scale is " + str(scale) + "\n")
        #scale = int(scale)
        #logmessage("scale is " + str(scale) + "\n")
        wtwips = int(scale*float(file_info['width'])*20.0)
        htwips = int(scale*float(file_info['height'])*20.0)
        image = Image( file_info['fullpath'] )
        image.Data = re.sub(r'\\picwgoal([0-9]+)', r'\\picwgoal' + str(wtwips), image.Data)
        image.Data = re.sub(r'\\pichgoal([0-9]+)', r'\\pichgoal' + str(htwips), image.Data)
    else:
        image = Image( file_info['fullpath'] )
    if insert_page_breaks:
        content = '\\page '
    else:
        content = ''
    #logmessage(content + image.Data)
    return(content + image.Data)

unit_multipliers = {'twips': 0.0500, 'hp': 0.5, 'in': 72, 'pt': 1, 'px': 1, 'em': 12, 'cm': 28.346472}

def convert_length(length, unit):
    value = pixels_in(length)
    if unit in unit_multipliers:
        size = float(value)/float(unit_multipliers[unit])
        return(int(size))
    else:
        logmessage("Unit " + str(unit) + " is not a valid unit\n")
    return(300)
    
def pixels_in(length):
    m = re.search(r"([0-9.]+) *([a-z]+)", str(length).lower())
    if m:
        value = float(m.group(1))
        unit = m.group(2)
        #logmessage("value is " + str(value) + " and unit is " + unit + "\n")
        if unit in unit_multipliers:
            size = float(unit_multipliers[unit]) * value
            #logmessage("size is " + str(size) + "\n")
            return(int(size))
    logmessage("Could not read " + str(length) + "\n")
    return(300)

def image_url_string(match, emoji=False, question=None, playground=False, default_image_width=None, external=False, status=None):
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
    return image_url(file_reference, alt_text, width, emoji=emoji, question=question, playground=playground, external=external, status=status)

def image_url(file_reference, alt_text, width, emoji=False, question=None, playground=False, external=False, status=None):
    if question and file_reference in question.interview.images:
        if status and question.interview.images[file_reference].attribution is not None:
            status.attributions.add(question.interview.images[file_reference].attribution)
        file_reference = question.interview.images[file_reference].get_reference()
    file_info = server.file_finder(file_reference, question=question)
    if 'mimetype' in file_info and file_info['mimetype']:
        if re.search(r'^audio', file_info['mimetype']):
            urls = get_audio_urls([{'text': "[FILE " + file_reference + "]", 'package': None, 'type': 'audio'}], question=question)
            if len(urls):
                return audio_control(urls)
            return ''
        if re.search(r'^video', file_info['mimetype']):
            urls = get_video_urls([{'text': "[FILE " + file_reference + "]", 'package': None, 'type': 'video'}], question=question)
            if len(urls):
                return video_control(urls)
            return ''
    if 'extension' in file_info and file_info['extension'] is not None:
        if re.match(r'.*%$', width):
            width_string = "width:" + width
        else:
            width_string = "max-width:" + width
        if emoji:
            width_string += ';vertical-align: middle'
            alt_text = 'alt="" '
        the_url = server.url_finder(file_reference, _question=question, display_filename=file_info['filename'], _external=external)
        if the_url is None:
            return ('[ERROR: File reference ' + str(file_reference) + ' cannot be displayed]')
        if width_string == 'width:100%':
            extra_class = ' dawideimage'
        else:
            extra_class = ''
        if file_info.get('extension', '') in ['png', 'jpg', 'gif', 'svg', 'jpe', 'jpeg']:
            return('<img ' + alt_text + 'class="daicon daimageref' + extra_class + '" style="' + width_string + '" src="' + the_url + '"/>')
        elif file_info['extension'] in ('pdf', 'docx', 'rtf', 'doc', 'odt'):
            if file_info['extension'] in ('docx', 'rtf', 'doc', 'odt') and not os.path.isfile(file_info['path'] + '.pdf'):
                server.fg_make_pdf_for_word_path(file_info['path'], file_info['extension'])
                server.fg_make_png_for_pdf_path(file_info['path'] + ".pdf", 'screen', page=1)
                if re.match(r'[0-9]+', str(file_reference)):
                    sf = server.SavedFile(int(file_reference), fix=True)
                    sf.finalize()
            if 'pages' not in file_info:
                try:
                    reader = safe_pypdf_reader(file_info['path'] + '.pdf')
                    file_info['pages'] = reader.getNumPages()
                except:
                    file_info['pages'] = 1
            image_url = server.url_finder(file_reference, size="screen", page=1, _question=question, _external=external)
            if image_url is None:
                return ('[ERROR: File reference ' + str(file_reference) + ' cannot be displayed]')
            if 'filename' in file_info:
                title = ' title="' + file_info['filename'] + '"'
            else:
                title = ''
            if alt_text == '':
                the_alt_text = 'alt=' + json.dumps(word("Thumbnail image of document")) + ' '
            else:
                the_alt_text = alt_text
            output = '<a target="_blank"' + title + ' class="daimageref" href="' + the_url + '"><img ' + the_alt_text + 'class="daicon dapdfscreen' + extra_class + '" style="' + width_string + '" src="' + image_url + '"/></a>'
            if 'pages' in file_info and file_info['pages'] > 1:
                output += " (" + str(file_info['pages']) + " " + word('pages') + ")"
            return(output)
        else:
            return('<a target="_blank" class="daimageref" href="' + the_url + '">' + file_info['filename'] + '</a>')
    else:
        return('[Invalid image reference; reference=' + str(file_reference) + ', width=' + str(width) + ', filename=' + file_info.get('filename', 'unknown') + ']')

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
            alt_text = word("A QR code")
    else:
        alt_text = word("A QR code")
    width_string = "width:" + width
    im = qrcode.make(string, image_factory=qrcode.image.svg.SvgPathImage)
    output = BytesIO()
    im.save(output)
    the_image = output.getvalue().decode()
    the_image = re.sub("<\?xml version='1.0' encoding='UTF-8'\?>\n", '', the_image)
    the_image = re.sub(r'height="[0-9]+mm" ', '', the_image)
    the_image = re.sub(r'width="[0-9]+mm" ', '', the_image)
    m = re.search(r'(viewBox="[^"]+")', the_image)
    if m:
        viewbox = m.group(1)
    else:
        viewbox = ""
    return('<svg style="' + width_string + '" ' + viewbox + '><g transform="scale(1.0)">' + the_image + '</g><title>' + alt_text + '</title></svg>')

def convert_pixels(match):
    pixels = match.group(1)
    return (str(int(pixels)/72.0) + "in")

def convert_percent(match):
    percentage = match.group(1)
    return (str(float(percentage)/100.0) + '\\textwidth')

def image_include_string(match, emoji=False, question=None):
    file_reference = match.group(1)
    if question and file_reference in question.interview.images:
        file_reference = question.interview.images[file_reference].get_reference()
    try:
        width = match.group(2)
        assert width != 'None'
        width = re.sub(r'^(.*)px', convert_pixels, width)
        width = re.sub(r'^(.*)%', convert_percent, width)
        if width == "full":
            width = '\\textwidth'
    except:
        width = DEFAULT_IMAGE_WIDTH
    file_info = server.file_finder(file_reference, convert={'svg': 'eps', 'gif': 'png'}, question=question)
    if 'mimetype' in file_info and file_info['mimetype']:
        if re.search(r'^(audio|video)', file_info['mimetype']):
            return '[reference to file type that cannot be displayed]'
    if 'path' in file_info:
        if 'extension' in file_info:
            if file_info['extension'] in ['png', 'jpg', 'pdf', 'eps', 'jpe', 'jpeg', 'docx', 'rtf', 'doc', 'odt']:
                if file_info['extension'] == 'pdf':
                    output = '\\includepdf[pages={-}]{' + file_info['path'] + '.pdf}'
                elif file_info['extension'] in ('docx', 'rtf', 'doc', 'odt'):
                    if not os.path.isfile(file_info['path'] + '.pdf'):
                        server.fg_make_pdf_for_word_path(file_info['path'], file_info['extension'])
                    output = '\\includepdf[pages={-}]{' + file_info['path'] + '.pdf}'
                else:
                    if emoji:
                        output = '\\raisebox{-.6\\dp\\strutbox}{\\mbox{\\includegraphics[width=' + width + ']{' + file_info['path'] + '}}}'
                    else:
                        output = '\\mbox{\\includegraphics[width=' + width + ']{' + file_info['path'] + '}}'
                    if width == '\\textwidth':
                        output = '\\clearpage ' + output + '\\clearpage '
                return(output)
    return('[invalid graphics reference]')

def image_include_docx(match, question=None):
    file_reference = match.group(1)
    if question and file_reference in question.interview.images:
        file_reference = question.interview.images[file_reference].get_reference()
    try:
        width = match.group(2)
        assert width != 'None'
        width = re.sub(r'^(.*)px', convert_pixels, width)
        if width == "full":
            width = '100%'
    except:
        width = DEFAULT_IMAGE_WIDTH
    file_info = server.file_finder(file_reference, convert={'svg': 'eps'}, question=question)
    if 'mimetype' in file_info and file_info['mimetype']:
        if re.search(r'^(audio|video)', file_info['mimetype']):
            return '[reference to file type that cannot be displayed]'
    if 'path' in file_info:
        if 'extension' in file_info:
            if file_info['extension'] in ('docx', 'rtf', 'doc', 'odt'):
                if not os.path.isfile(file_info['path'] + '.pdf'):
                    server.fg_make_pdf_for_word_path(file_info['path'], file_info['extension'])
                output = '![](' + file_info['path'] + '.pdf){width=' + width + '}'
                return(output)
            if file_info['extension'] in ['png', 'jpg', 'gif', 'pdf', 'eps', 'jpe', 'jpeg']:
                output = '![](' + file_info['path'] + '){width=' + width + '}'
                return(output)
    return('[invalid graphics reference]')

def qr_include_string(match):
    string = match.group(1)
    try:
        width = match.group(2)
        assert width != 'None'
        width = re.sub(r'^(.*)px', convert_pixels, width)
        if width == "full":
            width = '\\textwidth'
    except:
        width = DEFAULT_IMAGE_WIDTH
    im = qrcode.make(string)
    the_image = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".png", delete=False)
    #docassemble.base.functions.this_thread.temporary_resources.add(the_image.name)
    im.save(the_image.name)
    output = '\\mbox{\\includegraphics[width=' + width + ']{' + the_image.name + '}}'
    if width == '\\textwidth':
        output = '\\clearpage ' + output + '\\clearpage '
    #logmessage("Output is " + output)
    return(output)

def qr_include_docx(match):
    string = match.group(1)
    try:
        width = match.group(2)
        assert width != 'None'
        width = re.sub(r'^(.*)px', convert_pixels, width)
        if width == "full":
            width = '100%'
    except:
        width = DEFAULT_IMAGE_WIDTH
    im = qrcode.make(string)
    the_image = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".png", delete=False)
    #docassemble.base.functions.this_thread.temporary_resources.add(the_image.name)
    im.save(the_image.name)
    output = '![](' + the_image.name + '){width=' + width + '}'
    return(output)

def rtf_caption_table(match):
    table_text = """\\trowd \\irow0\\irowband0\\lastrow \\ltrrow\\ts24\\trgaph108\\trleft0\\trbrdrt\\brdrs\\brdrw10 \\trbrdrl\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrh\\brdrs\\brdrw10 \\trbrdrv\\brdrs\\brdrw10 
\\trftsWidth1\\trftsWidthB3\\trftsWidthA3\\trautofit1\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddft3\\trpaddfb3\\trpaddfr3\\trcbpat1\\trcfpat1\\tblrsid1508006\\tbllkhdrrows\\tbllkhdrcols\\tbllknocolband\\tblind0\\tblindtype3 \\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone 
\\clbrdrb\\brdrnone \\clbrdrr\\clshdng0\\brdrs\\brdrw10 \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx4680\\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrs\\brdrw10 \\clbrdrb\\brdrnone \\clbrdrr\\clshdng0\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx9468\\pard\\plain \\ltrpar
\\ql \\li0\\ri0\\widctlpar\\intbl\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0\\pararsid1508006\\yts24 \\rtlch\\fcs1 \\af0\\afs22\\alang1025 \\ltrch\\fcs0 \\fs22\\lang1033\\langfe1033\\cgrid\\langnp1033\\langfenp1033 { [SAVE][TIGHTSPACING][STOP_INDENTATION]""" + match.group(1) + """}{\\cell}{""" + match.group(2) + """[RESTORE]}{\\cell}\\pard\\plain \\ltrpar
\\ql \\li0\\ri0\\sa200\\sl276\\slmult1\\widctlpar\\intbl\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0 \\rtlch\\fcs1 \\af0\\afs22\\alang1025 \\ltrch\\fcs0 \\fs24\\lang1033\\langfe1033\\cgrid\\langnp1033\\langfenp1033 {\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid10753242 
\\trowd \\irow0\\irowband0\\lastrow \\ltrrow\\ts24\\trgaph108\\trleft0\\trbrdrt\\brdrs\\brdrw10 \\trbrdrl\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrh\\brdrs\\brdrw10 \\trbrdrv\\brdrs\\brdrw10 
\\trftsWidth1\\trftsWidthB3\\trftsWidthA3\\trautofit1\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddft3\\trpaddfb3\\trpaddfr3\\trcbpat1\\trcfpat1\\tblrsid1508006\\tbllkhdrrows\\tbllkhdrcols\\tbllknocolband\\tblind0\\tblindtype3 \\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone 
\\clbrdrb\\brdrnone \\clbrdrr\\clshdng0\\brdrs\\brdrw10 \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx4680\\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrs\\brdrw10 \\clbrdrb\\brdrnone \\clbrdrr\\clshdng0\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx9468\\row }"""
    table_text += """\\pard \\ltrpar
\\qc \\li0\\ri0\\sb0\\sl240\\slmult1\\widctlpar\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0\\itap0\\pararsid10753242"""
    table_text = re.sub(r'\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0', r'\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\sl240 \\slmult1', table_text)
    return table_text + '[MANUALSKIP]'

def rtf_two_col(match):
    table_text = """\\trowd \\irow0\\irowband0\\lastrow \\ltrrow\\ts24\\trgaph108\\trleft0\\trbrdrt\\brdrs\\brdrw10 \\trbrdrl\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrh\\brdrs\\brdrw10 \\trbrdrv\\brdrs\\brdrw10 
\\trftsWidth1\\trftsWidthB3\\trftsWidthA3\\trautofit1\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddft3\\trpaddfb3\\trpaddfr3\\trcbpat1\\trcfpat1\\tblrsid1508006\\tbllkhdrrows\\tbllkhdrcols\\tbllknocolband\\tblind0\\tblindtype3 \\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone 
\\clbrdrb\\brdrnone \\clbrdrr\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx4680\\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\clshdng0\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx9468\\pard\\plain \\ltrpar
\\ql \\li0\\ri0\\widctlpar\\intbl\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0\\pararsid1508006\\yts24 \\rtlch\\fcs1 \\af0\\afs22\\alang1025 \\ltrch\\fcs0 \\fs22\\lang1033\\langfe1033\\cgrid\\langnp1033\\langfenp1033 {\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid2427490 [SAVE][TIGHTSPACING][STOP_INDENTATION]""" + match.group(1) + """}{\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid10753242\\charrsid2427490 \\cell}{""" + match.group(2) + """[RESTORE]}{\\cell}\\pard\\plain \\ltrpar
\\ql \\li0\\ri0\\sa200\\sl276\\slmult1\\widctlpar\\intbl\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0 \\rtlch\\fcs1 \\af0\\afs22\\alang1025 \\ltrch\\fcs0 \\fs24\\lang1033\\langfe1033\\cgrid\\langnp1033\\langfenp1033 {\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid10753242 
\\trowd \\irow0\\irowband0\\lastrow \\ltrrow\\ts24\\trgaph108\\trleft0\\trbrdrt\\brdrs\\brdrw10 \\trbrdrl\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrh\\brdrs\\brdrw10 \\trbrdrv\\brdrs\\brdrw10 
\\trftsWidth1\\trftsWidthB3\\trftsWidthA3\\trautofit1\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddft3\\trpaddfb3\\trpaddfr3\\trcbpat1\\trcfpat1\\tblrsid1508006\\tbllkhdrrows\\tbllkhdrcols\\tbllknocolband\\tblind0\\tblindtype3 \\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone 
\\clbrdrb\\brdrnone \\clbrdrr\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx4680\\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone \\clbrdrb\\brdrnone \\clbrdrr\\clshdng0\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx9468\\row }"""
    table_text += """\\pard \\ltrpar
\\qc \\li0\\ri0\\sb0\\sl240\\slmult1\\widctlpar\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0\\itap0\\pararsid10753242"""
    table_text = re.sub(r'\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0', r'\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\sl240 \\slmult1', table_text)
    return table_text + '[MANUALSKIP]'

def emoji_html(text, status=None, question=None, images=None):
    #logmessage("Got to emoji_html")
    if status is not None and question is None:
        question = status.question
    if images is None:
        images = question.interview.images
    if text in images:
        if status is not None and images[text].attribution is not None:
            status.attributions.add(images[text].attribution)
        return image_url(images[text].get_reference(), word('icon'), '1em', emoji=True, question=question)
    icons_setting = docassemble.base.functions.get_config('default icons', None)
    if icons_setting == 'font awesome':
        m = re.search(r'^(fa[a-z])-fa-(.*)', text)
        if m:
            the_prefix = m.group(1)
            text = m.group(2)
        else:
            the_prefix = docassemble.base.functions.get_config('font awesome prefix', 'fas')
        return('<i class="' + the_prefix + ' fa-' + str(text) + '"></i>')
    elif icons_setting == 'material icons':
        return('<i class="da-material-icons">' + str(text) + '</i>')
    return(":" + str(text) + ":")

def emoji_insert(text, status=None, images=None):
    if images is None:
        images = status.question.interview.images
    if text in images:
        if status is not None and images[text].attribution is not None:
            status.attributions.add(images[text].attribution)
        return("[EMOJI " + images[text].get_reference() + ', 1.2em]')
    else:
        return(":" + str(text) + ":")

def link_rewriter(m, status):
    the_path = None
    if m.group(1).startswith('#'):
        return '<a href="javascript:daGoToAnchor(' + re.sub(r'"', '&quot;', json.dumps(m.group(1))) + ');"'
    if m.group(1).startswith('/'):
        the_path = m.group(1)
    elif 'url_root' in docassemble.base.functions.this_thread.current_info and m.group(1).startswith(docassemble.base.functions.this_thread.current_info['url_root']):
        the_path = '/' + m.group(1)[len(docassemble.base.functions.this_thread.current_info['url_root']):]
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

def markdown_to_html(a, trim=False, pclass=None, status=None, question=None, use_pandoc=False, escape=False, do_terms=True, indent=None, strip_newlines=None, divclass=None, embedder=None, default_image_width=None, external=False, verbatim=False):
    if verbatim:
        return a
    a = str(a)
    if question is None and status is not None:
        question = status.question
    if question is not None:
        if do_terms:
            if status is not None:
                if len(question.terms):
                    lang = docassemble.base.functions.get_language()
                    for term in question.terms:
                        if lang in question.terms[term]['re']:
                            a = question.terms[term]['re'][lang].sub(sub_term, a)
                        else:
                            a = question.terms[term]['re'][question.language].sub(sub_term, a)
                if len(question.autoterms):
                    lang = docassemble.base.functions.get_language()
                    for term in question.autoterms:
                        if lang in question.autoterms[term]['re']:
                            a = question.autoterms[term]['re'][lang].sub(r'[[\1]]', a)
                        else:
                            a = question.autoterms[term]['re'][question.language].sub(r'[[\1]]', a)
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
            if len(interview_terms):
                lang = docassemble.base.functions.get_language()
                if lang in interview_terms and len(interview_terms[lang]) > 0:
                    for term in interview_terms[lang]:
                        #logmessage("Searching for term " + term + " in " + a + "\n")
                        a = interview_terms[lang][term]['re'].sub(sub_term, a)
                        #logmessage("string is now " + str(a) + "\n")
                elif question.language in interview_terms and len(interview_terms[question.language]) > 0:
                    for term in interview_terms[question.language]:
                        #logmessage("Searching for term " + term + " in " + a + "\n")
                        a = interview_terms[question.language][term]['re'].sub(sub_term, a)
                        #logmessage("string is now " + str(a) + "\n")
            if len(interview_autoterms):
                lang = docassemble.base.functions.get_language()
                if lang in interview_autoterms and len(interview_autoterms[lang]) > 0:
                    for term in interview_autoterms[lang]:
                        #logmessage("Searching for term " + term + " in " + a + "\n")
                        a = interview_autoterms[lang][term]['re'].sub(r'[[\1]]', a)
                        #logmessage("string is now " + str(a) + "\n")
                elif question.language in interview_autoterms and len(interview_autoterms[question.language]) > 0:
                    for term in interview_autoterms[question.language]:
                        #logmessage("Searching for term " + term + " in " + a + "\n")
                        a = interview_autoterms[question.language][term]['re'].sub(r'[[\1]]', a)
                        #logmessage("string is now " + str(a) + "\n")
    a = html_filter(str(a), status=status, question=question, embedder=embedder, default_image_width=default_image_width, external=external)
    #logmessage("before: " + a)
    if status and status.extras.get('tableCssClass', None):
        classes = status.extras['tableCssClass'].split(',')
        table_class = json.dumps(classes[0].strip())
        if len(classes) > 1:
            thead_class = json.dumps(classes[1].strip())
        else:
            thead_class = None
    else:
        table_class = server.default_table_class
        thead_class = server.default_thead_class
    a = re.sub(r'<(/?)table', r'<\1TABLE', a)
    a = re.sub(r'<thead>', r'<THEAD>', a)
    if use_pandoc:
        converter = pandoc.MyPandoc()
        converter.output_format = 'html'
        converter.input_content = a
        converter.convert(question)
        result = converter.output_content
    else:
        try:
            result = docassemble.base.functions.this_thread.markdown.reset().convert(a)
        except:
            # Try again because sometimes it fails randomly and maybe trying again will work.
            result = docassemble.base.functions.this_thread.markdown.reset().convert(a)
    result = re.sub(r'<table>', r'<div class="table-responsive"><table class=' + table_class + '>', result)
    if thead_class:
        result = re.sub(r'<thead>', r'<thead class=' + thead_class + '>', result)
    result = re.sub(r'</table>', r'</table></div>', result)
    result = re.sub(r'<(/?)TABLE', r'<\1table', result)
    result = re.sub(r'<THEAD>', r'<thead>', result)
    result = re.sub(r'<(t[dh]) align="(right|left|center)">', r'<\1 class="text-\2">', result)
    result = re.sub(r'<blockquote>', r'<blockquote class="blockquote">', result)
    result = re.sub(r'<a href="(.*?)"', lambda x: link_rewriter(x, status), result)
    if do_terms and question is not None and term_start.search(result):
        lang = docassemble.base.functions.get_language()
        if status is not None:
            if len(question.terms):
                result = term_match.sub((lambda x: add_terms(x.group(1), status.extras['terms'], label=x.group(2), status=status, question=question)), result)
            if len(question.autoterms):
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
    if status is not None and question.interview.scan_for_emojis:
        result = emoji_match.sub((lambda x: emoji_html(x.group(1), status=status, question=question)), result)
    if trim:
        if result.startswith('<p>') and result.endswith('</p>'):
            result = re.sub(r'</p>\s*<p>', ' ', result[3:-4])
    elif pclass:
        result = re.sub('<p>', '<p class="' + pclass + '">', result)
    if escape:
        if escape is True:
            result = noquote_match.sub('&quot;', result)
        result = lt_match.sub('&lt;', result)
        result = gt_match.sub('&gt;', result)
        if escape is True:
            result = amp_match.sub('&amp;', result)
    #logmessage("after: " + result)
    #result = result.replace('\n', ' ')
    if result:
        if strip_newlines:
            result = result.replace('\n', ' ')
        if divclass is not None:
            result = '<div class="' + str(divclass) + '">' + result + '</div>'
        # if indent and not code_match.search(result):
        #     return (" " * indent) + re.sub(r'\n', "\n" + (" " * indent), result).rstrip() + "\n"
    return(result)

def my_escape(result):
    result = noquote_match.sub('&quot;', result)
    result = lt_match.sub('&lt;', result)
    result = gt_match.sub('&gt;', result)
    result = amp_match.sub('&amp;', result)
    return(result)

def noquote(string):
    #return json.dumps(string.replace('\n', ' ').rstrip())
    return '"' + string.replace('\n', ' ').replace('"', '&quot;').rstrip() + '"'

def add_terms_mako(termname, terms, status=None, question=None):
    lower_termname = re.sub(r'\s+', ' ', termname.lower(), re.DOTALL)
    if lower_termname in terms:
        return('<a tabindex="0" class="daterm" data-toggle="popover" data-container="body" data-placement="bottom" data-content=' + noquote(markdown_to_html(terms[lower_termname]['definition'].text(dict()), trim=True, default_image_width='100%', do_terms=False, status=status, question=question)) + '>' + str(termname) + '</a>')
    #logmessage(lower_termname + " is not in terms dictionary\n")
    return '[[' + termname + ']]'

def add_terms(termname, terms, label=None, status=None, question=None):
    if label is None:
        label = str(termname)
    else:
        label = re.sub(r'^\|', '', label)
    lower_termname = re.sub(r'\s+', ' ', termname.lower(), re.DOTALL)
    if lower_termname in terms:
        return('<a tabindex="0" class="daterm" data-toggle="popover" data-container="body" data-placement="bottom" data-content=' + noquote(markdown_to_html(terms[lower_termname]['definition'], trim=True, default_image_width='100%', do_terms=False, status=status, question=question)) + '>' + label + '</a>')
    #logmessage(lower_termname + " is not in terms dictionary\n")
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
    output += '  <a target="_blank" href="' + files[-1][0] +  '">' + word('Listen') + '</a>\n'
    output += "</audio>\n"
    return output

def video_control(files):
    for d in files:
        if isinstance(d, (str, NoneType)):
            return str(d)
    output = '<video class="dawidevideo" controls="controls">' + "\n"
    for d in files:
        if type(d) is list:
            if d[0] is None:
                continue
            output += '  <source src="' + d[0] + '"'
            if d[1] is not None:
                output += ' type="' + d[1] + '"/>'
            output += "\n"
    output += '  <a target="_blank" href="' + files[-1][0] +  '">' + word('Listen') + '</a>\n'
    output += "</video>\n"
    return output

def get_audio_urls(the_audio, question=None):
    output = list()
    the_list = list()
    to_try = dict()
    for audio_item in the_audio:
        if audio_item['type'] != 'audio':
            continue
        found_upload = False
        pattern = re.compile(r'^\[FILE ([^,\]]+)')
        for (file_ref) in re.findall(pattern, audio_item['text']):
            found_upload = True
            m = re.match(r'[0-9]+', file_ref)
            if m:
                file_info = server.file_finder(file_ref, question=question)
                if 'path' in file_info:
                    if file_info['mimetype'] == 'audio/ogg':
                        output.append([server.url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.ogg'):
                        output.append([server.url_finder(file_ref, ext='ogg', _question=question), 'audio/ogg'])
                    if file_info['mimetype'] == 'audio/mpeg':
                        output.append([server.url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.mp3'):
                        output.append([server.url_finder(file_ref, ext='mp3', _question=question), 'audio/mpeg'])
                    if file_info['mimetype'] not in ['audio/mpeg', 'audio/ogg']:
                        output.append([server.url_finder(file_ref, _question=question), file_info['mimetype']])
            else:
                the_list.append({'text': file_ref, 'package': audio_item['package']})
        if not found_upload:
            the_list.append(audio_item)
    for audio_item in the_list:
        mimetype, encoding = mimetypes.guess_type(audio_item['text'])
        if re.search(r'^http', audio_item['text']):
            output.append([audio_item['text'], mimetype])
            continue
        basename = os.path.splitext(audio_item['text'])[0]
        ext = os.path.splitext(audio_item['text'])[1]
        if not mimetype in to_try:
            to_try[mimetype] = list();
        to_try[mimetype].append({'basename': basename, 'filename': audio_item['text'], 'ext': ext, 'package': audio_item['package']})
    if 'audio/mpeg' in to_try and 'audio/ogg' not in to_try:
        to_try['audio/ogg'] = list()
        for attempt in to_try['audio/mpeg']:
            if attempt['ext'] == '.MP3':
                to_try['audio/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.OGG', 'ext': '.OGG', 'package': attempt['package']})
            else:
                to_try['audio/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.ogg', 'ext': '.ogg', 'package': attempt['package']})
    if 'audio/ogg' in to_try and 'audio/mpeg' not in to_try:
        to_try['audio/mpeg'] = list()
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
            file_info = server.file_finder(full_file, question=question)
            if 'fullpath' in file_info:
                url = server.url_finder(full_file, _question=question)
                output.append([url, mimetype])
    return [item for item in output if item[0] is not None]

def get_video_urls(the_video, question=None):
    output = list()
    the_list = list()
    to_try = dict()
    for video_item in the_video:
        if video_item['type'] != 'video':
            continue
        found_upload = False
        if re.search(r'^\[(YOUTUBE|VIMEO)[0-9\:]* ', video_item['text']):
            output.append(html_filter(video_item['text']))
            continue
        pattern = re.compile(r'^\[FILE ([^,\]]+)')
        for (file_ref) in re.findall(pattern, video_item['text']):
            found_upload = True
            m = re.match(r'[0-9]+', file_ref)
            if m:
                file_info = server.file_finder(file_ref, question=question)
                if 'path' in file_info:
                    if file_info['mimetype'] == 'video/ogg':
                        output.append([server.url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.ogv'):
                        output.append([server.url_finder(file_ref, ext='ogv', _question=question), 'video/ogg'])
                    if file_info['mimetype'] == 'video/mp4':
                        output.append([server.url_finder(file_ref, _question=question), file_info['mimetype']])
                    elif os.path.isfile(file_info['path'] + '.mp4'):
                        output.append([server.url_finder(file_ref, ext='mp4', _question=question), 'video/mp4'])
                    if file_info['mimetype'] not in ['video/mp4', 'video/ogg']:
                        output.append([server.url_finder(file_ref, _question=question), file_info['mimetype']])
            else:
                the_list.append({'text': file_ref, 'package': video_item['package']})
        if not found_upload:
            the_list.append(video_item)
    for video_item in the_list:
        mimetype, encoding = mimetypes.guess_type(video_item['text'])
        if re.search(r'^http', video_item['text']):
            output.append([video_item['text'], mimetype])
            continue
        basename = os.path.splitext(video_item['text'])[0]
        ext = os.path.splitext(video_item['text'])[1]
        if not mimetype in to_try:
            to_try[mimetype] = list();
        to_try[mimetype].append({'basename': basename, 'filename': video_item['text'], 'ext': ext, 'package': video_item['package']})
    if 'video/mp4' in to_try and 'video/ogg' not in to_try:
        to_try['video/ogg'] = list()
        for attempt in to_try['video/mp4']:
            if attempt['ext'] == '.MP4':
                to_try['video/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.OGV', 'ext': '.OGV', 'package': attempt['package']})
            else:
                to_try['video/ogg'].append({'basename': attempt['basename'], 'filename': attempt['basename'] + '.ogv', 'ext': '.ogv', 'package': attempt['package']})
    if 'video/ogg' in to_try and 'video/mp4' not in to_try:
        to_try['video/mp4'] = list()
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
            if parts[0] is None:
                parts[0] = 'None'
            parts[1] = re.sub(r'^data/static/', '', parts[1])
            full_file = parts[0] + ':data/static/' + parts[1]
            file_info = server.file_finder(full_file, question=question)
            if 'fullpath' in file_info:
                url = server.url_finder(full_file, _question=question)
                if url is not None:
                    output.append([url, mimetype])
    return output

def to_text(html_doc, terms, links, status):
    output = ""
    #logmessage("to_text: html doc is " + str(html_doc))
    soup = BeautifulSoup(html_doc, 'html.parser')
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title', 'audio', 'video', 'pre', 'attribution'])]
    [s.extract() for s in soup.find_all(hidden)]
    [s.extract() for s in soup.find_all('div', {'class': 'dainvisible'})]
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
        elif s.has_attr('href'):# and (s.attrs['href'].startswith(url) or s.attrs['href'].startswith('?')):
            #logmessage("Adding a link: " + s.attrs['href'])
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

def replace_fields(string, status=None, embedder=None):
    if not re.search(r'\[FIELD ', string):
        return string
    matches = list()
    in_match = False
    start_match = None
    depth = 0
    i = 0
    while i < len(string):
        if string[i:i+7] == '[FIELD ':
            in_match = True
            start_match = i
            i += 7
            continue
        if in_match:
            if string[i] == '[':
                depth += 1
            elif string[i] == ']':
                if depth == 0:
                    i += 1
                    matches.append((start_match, i))
                    in_match = False
                    continue
                else:
                    depth -= 1
        i += 1

    field_strings = list()
    for (start, end) in matches:
        field_strings.append(string[start:end])
    #logmessage(repr(field_strings))
    for field_string in field_strings:
        if embedder is None:
            string = string.replace(field_string, 'ERROR: FIELD cannot be used here')
        else:
            string = string.replace(field_string, embedder(status, field_string))
    return string

def image_include_docx_template(match, question=None):
    file_reference = match.group(1)
    if question and file_reference in question.interview.images:
        file_reference = question.interview.images[file_reference].get_reference()
    try:
        width = match.group(2)
        assert width != 'None'
        width = re.sub(r'^(.*)px', convert_pixels, width)
        if width == "full":
            width = '100%'
    except:
        width = DEFAULT_IMAGE_WIDTH
    file_info = server.file_finder(file_reference, convert={'svg': 'eps'}, question=question)
    if 'mimetype' in file_info and file_info['mimetype']:
        if re.search(r'^(audio|video)', file_info['mimetype']):
            return '[reference to file type that cannot be displayed]'
    if 'path' in file_info:
        if 'mimetype' in file_info and file_info['mimetype']:
            if file_info['mimetype'] in ('text/markdown', 'text/plain'):
                with open(file_info['fullpath'], 'r', encoding='utf-8') as f:
                    contents = f.read()
                if file_info['mimetype'] == 'text/plain':
                    return contents
                else:
                    return docassemble.base.file_docx.markdown_to_docx(contents, question, docassemble.base.functions.this_thread.misc.get('docx_template', None))
            if file_info['mimetype'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return str(docassemble.base.file_docx.include_docx_template(docassemble.base.functions.DALocalFile(file_info['fullpath'])))
            else:
                return str(docassemble.base.file_docx.image_for_docx(file_reference, question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width))
    return '[reference to file that could not be found]'

def qr_include_docx_template(match):
    string = match.group(1)
    try:
        width = match.group(2)
        assert width != 'None'
        width = re.sub(r'^(.*)px', convert_pixels, width)
        if width == "full":
            width = '100%'
    except:
        width = DEFAULT_IMAGE_WIDTH
    im = qrcode.make(string)
    the_image = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".png", delete=False)
    im.save(the_image.name)
    return str(docassemble.base.file_docx.image_for_docx(docassemble.base.functions.DALocalFile(the_image.name), None, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width))

def ensure_valid_filename(filename):
    m = re.search(r'[\\/\&\`:;,~\'\"\*\?\<\>\|]', filename)
    if m:
        raise Exception("Filename contained invalid character " + repr(m.group(1)))
    for char in filename:
        if ord(char) < 32 or ord(char) >= 127:
            raise Exception("Filename contained invalid character " + repr(char))
    return True
