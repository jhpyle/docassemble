import re
import os
import tempfile
import time
import stat
import qrcode
import qrcode.image.svg
from pikepdf import Pdf
from pylatex.utils import escape_latex
import PIL
from cairosvg import svg2png
from ..logger import logmessage
from ..hooks import file_finder, fg_make_png_for_pdf_path, fg_make_pdf_for_word_path
from ..rtfng.object.picture import Image
from .utils import (
    convert_length,
    replace_fields,
    repeat_along,
    get_default_image_width,
    convert_pixels,
    pixels_in,
    convert_svg_to_eps,
)

DEFAULT_PAGE_WIDTH = '6.5in'

def set_default_page_width(width):
    global DEFAULT_PAGE_WIDTH
    DEFAULT_PAGE_WIDTH = str(width)


def get_default_page_width():
    return DEFAULT_PAGE_WIDTH

MAX_HEIGHT_POINTS = 10 * 72


def set_max_height_points(points):
    global MAX_HEIGHT_POINTS
    MAX_HEIGHT_POINTS = points


def get_max_height_points():
    return MAX_HEIGHT_POINTS

MAX_WIDTH_POINTS = 6.5 * 72.0


def set_max_width_points(points):
    global MAX_WIDTH_POINTS
    MAX_WIDTH_POINTS = points


def get_max_width_points():
    return MAX_WIDTH_POINTS


rtf_spacing = {'tight': r'\\sl0 ', 'single': r'\\sl0 ', 'oneandahalf': r'\\sl360\\slmult1 ', 'double': r'\\sl480\\slmult1 ', 'triple': r'\\sl720\\slmult1 '}

rtf_after_space = {'tight': 0, 'single': 1, 'oneandahalf': 0, 'double': 0, 'triplespacing': 0, 'triple': 0}


def rtf_prefilter(text):
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
    return text

def rtf_filter(text, metadata=None, styles=None, question=None):
    if metadata is None:
        metadata = {}
    if styles is None:
        styles = {}
    # logmessage(text)
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
        default_indentation = bool(metadata['Indentation'])
    else:
        default_indentation = True
    if 'SingleSpacing' in metadata and metadata['SingleSpacing']:
        # logmessage("Gi there!")
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
    formatting_stack = []
    for line in lines:
        if re.search(r'\[SAVE\]', line):
            formatting_stack.append({'spacing_command': spacing_command, 'after_space': after_space, 'default_indentation': default_indentation, 'indentation_command': indentation_command})
        elif re.search(r'\[RESTORE\]', line):
            if len(formatting_stack) > 0:
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
    return text


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
        metadata = {}
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
    text = re.sub(r'\[PAGENUM\]', r'\\myshow{\\thepage\\myxspace}', text)
    text = re.sub(r'\[TOTALPAGES\]', r'\\myshow{\\pageref*{LastPage}\\myxspace}', text)
    text = re.sub(r'\[SECTIONNUM\]', r'\\myshow{\\thesection\\myxspace}', text)
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
    text = re.sub(r'\[INDENTBY *([0-9\.]+ *[A-Za-z]+)\] *(.+?)\n *\n', indentby_left_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[INDENTBY *([0-9\.]+ *[A-Za-z]+) *([0-9]+ *[A-Za-z]+)\] *(.+?)\n *\n', indentby_both_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BORDER\] *(.+?)\n *\n', border_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\s*\[SKIPLINE\]\s*', r'\\par\\myskipline ', text)
    return text


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
    return string


def pdf_two_col(match, add_line=False):
    firstcol = clean_markdown_to_latex(match.group(1))
    secondcol = clean_markdown_to_latex(match.group(2))
    if add_line:
        return '\\noindent\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\mynoindent\\begin{tabular}{@{}m{0.49\\textwidth}|@{\\hspace{1em}}m{0.49\\textwidth}@{}}{' + firstcol + '} & {' + secondcol + '} \\\\ \\end{tabular}\\endgroup\\myskipline'
    return '\\noindent\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\mynoindent\\begin{tabular}{@{}m{0.49\\textwidth}@{\\hspace{1em}}m{0.49\\textwidth}@{}}{' + firstcol + '} & {' + secondcol + '} \\\\ \\end{tabular}\\endgroup\\myskipline'


def pdf_caption(match):
    return pdf_two_col(match, add_line=False)


def border_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return '\\mdframed\\setlength{\\parindent}{0pt} ' + str(string) + '\n\n\\endmdframed' + "\n\n"


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
    return '\\mdframed ' + str(string) + '\\endmdframed'


def image_as_rtf(match, question=None):
    width_supplied = False
    try:
        width = match.group(2)
        assert width != 'None'
        width_supplied = True
    except:
        width = get_default_image_width()
    if width == 'full':
        width_supplied = False
    file_reference = match.group(1)
    if question and file_reference in question.interview.images:
        file_reference = question.interview.images[file_reference].get_reference()
    file_info = file_finder(file_reference, question=question)
    if 'path' not in file_info:
        return '[invalid graphics reference]'
    # logmessage('image_as_rtf: path is ' + file_info['path'])
    if 'mimetype' in file_info and file_info['mimetype']:
        if re.search(r'^(audio|video)', file_info['mimetype']):
            return '[reference to file type that cannot be displayed]'
    if file_info['extension'] == 'svg':
        try:
            with tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".png", delete=False) as png_file:
                with open(file_info['fullpath'], 'rb') as fp:
                    svg2png(file_obj=fp, write_to=png_file, dpi=300)
                png_file.close()
                with PIL.Image.open(png_file.name) as im:
                    orig_width, orig_height = im.size
                return rtf_image({"width": orig_width, "height": orig_height, "fullpath": png_file.name}, width, False)
        except BaseException as err:
            logmessage("Could not insert SVG into RTF file: " + err.__class__.__name__ + ": " + str(err))
            return '[graphic could not be inserted]'
    if 'width' in file_info:
        if file_info['extension'] in ('gif', 'jpg', 'jpeg'):
            try:
                with tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".png", delete=False) as png_file:
                    with PIL.Image.open(file_info['fullpath']) as im:
                        im.save(png_file.name)
                    png_file.close()
                    return rtf_image({"width": file_info["width"], "height": file_info["height"], "fullpath": png_file.name}, width, False)
            except BaseException as err:
                logmessage("Could not insert image into RTF file: " + err.__class__.__name__ + ": " + str(err))
                return '[graphic could not be inserted]'
        try:
            return rtf_image(file_info, width, False)
        except BaseException as err:
            logmessage("Could not insert graphic into RTF file: " + err.__class__.__name__ + ": " + str(err))
            return '[graphic could not be inserted]'
    elif file_info['extension'] in ('pdf', 'docx', 'rtf', 'doc', 'odt'):
        output = ''
        if not width_supplied:
            # logmessage("image_as_rtf: Adding page break")
            width = DEFAULT_PAGE_WIDTH
            # output += '\\page '
        # logmessage("image_as_rtf: maxpage is " + str(int(file_info['pages'])))
        if not os.path.isfile(file_info['path'] + '.pdf'):
            if file_info['extension'] in ('docx', 'rtf', 'doc', 'odt') and not os.path.isfile(file_info['path'] + '.pdf'):
                fg_make_pdf_for_word_path(file_info['path'], file_info['extension'])
        if 'pages' not in file_info:
            try:
                with Pdf.open(file_info['path'] + '.pdf') as reader:
                    file_info['pages'] = len(reader.pages)
            except:
                file_info['pages'] = 1
        max_pages = 1 + int(file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        for page in range(1, max_pages):
            page_file = {}
            test_path = file_info['path'] + 'page-in-progress'
            if os.path.isfile(test_path):
                while (os.path.isfile(test_path) and time.time() - os.stat(test_path)[stat.ST_MTIME]) < 30:
                    if not os.path.isfile(test_path):
                        break
                    time.sleep(1)
            page_file['extension'] = 'png'
            page_file['path'] = file_info['path'] + 'page-' + formatter % page
            page_file['fullpath'] = page_file['path'] + '.png'
            if not os.path.isfile(page_file['fullpath']):
                fg_make_png_for_pdf_path(file_info['path'] + '.pdf', 'page')
            if os.path.isfile(page_file['fullpath']):
                try:
                    with PIL.Image.open(page_file['fullpath']) as im:
                        page_file['width'], page_file['height'] = im.size
                    output += rtf_image(page_file, width, False)
                except BaseException as err:
                    logmessage("Could not insert graphic into RTF file: " + err.__class__.__name__ + ": " + str(err))
                    return '[page image could not be inserted]'
            else:
                output += "[Error including page image]"
            output += ' '
        return output
    return '[graphic could not be inserted]'


def qr_as_rtf(match):
    width_supplied = False
    try:
        width = match.group(2)
        assert width != 'None'
        width_supplied = True
    except:
        width = get_default_image_width()
    if width == 'full':
        width_supplied = False
    string = match.group(1)
    output = ''
    if not width_supplied:
        # logmessage("Adding page break")
        width = DEFAULT_PAGE_WIDTH
        output += '\\page '
    try:
        im = qrcode.make(string)
        with tempfile.NamedTemporaryFile(suffix=".png") as the_image:
            im.save(the_image.name)
            page_file = {}
            page_file['extension'] = 'png'
            page_file['fullpath'] = the_image.name
            page_file['width'], page_file['height'] = im.size
            output += rtf_image(page_file, width, False)
    except BaseException as err:
        logmessage("Could not insert QR code into RTF file: " + err.__class__.__name__ + ": " + str(err))
        return '[QR code could not be inserted]'
    if not width_supplied:
        # logmessage("Adding page break")
        output += '\\page '
    else:
        output += ' '
    # logmessage("Returning output")
    return output


def rtf_image(file_info, width, insert_page_breaks):
    pixels = pixels_in(width)
    if pixels > 0 and file_info['width'] > 0:
        scale = float(pixels)/float(file_info['width'])
        # logmessage("scale is " + str(scale))
        if scale*float(file_info['height']) > float(MAX_HEIGHT_POINTS):
            scale = float(MAX_HEIGHT_POINTS)/float(file_info['height'])
        # logmessage("scale is " + str(scale))
        if scale*float(file_info['width']) > float(MAX_WIDTH_POINTS):
            scale = float(MAX_WIDTH_POINTS)/float(file_info['width'])
        # logmessage("scale is " + str(scale))
        # scale *= 100.0
        # logmessage("scale is " + str(scale))
        # scale = int(scale)
        # logmessage("scale is " + str(scale))
        wtwips = int(scale*float(file_info['width'])*20.0)
        htwips = int(scale*float(file_info['height'])*20.0)
        image = Image(file_info['fullpath'])
        image.Data = re.sub(r'\\picwgoal([0-9]+)', r'\\picwgoal' + str(wtwips), image.Data)
        image.Data = re.sub(r'\\pichgoal([0-9]+)', r'\\pichgoal' + str(htwips), image.Data)
    else:
        image = Image(file_info['fullpath'])
    if insert_page_breaks:
        content = '\\page '
    else:
        content = ''
    # logmessage(content + image.Data)
    return content + image.Data


def convert_percent(match):
    percentage = match.group(1)
    return str(float(percentage)/100.0) + '\\textwidth'


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
        width = get_default_image_width()
    if match.lastindex == 3:
        alt_text = match.group(3)
    else:
        alt_text = None
    file_info = file_finder(file_reference, question=question)
    if 'path' in file_info and 'extension' in file_info:
        convert_svg_to_eps(file_info)
        if file_info['extension'] == 'gif':
            with tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".png", delete=False) as png_file:
                try:
                    with PIL.Image.open(file_info['fullpath']) as im:
                        im.save(png_file.name)
                    png_file.close()
                    file_info['path'] = png_file.name
                    file_info['fullpath'] = png_file.name
                    file_info['extension'] = 'png'
                    file_info['mimetype'] = 'image/png'
                except BaseException as err:
                    logmessage("Could not convert GIF to PNG: " + err.__class__.__name__ + ": " + str(err))
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
                        fg_make_pdf_for_word_path(file_info['path'], file_info['extension'])
                    output = '\\includepdf[pages={-}]{' + file_info['path'] + '.pdf}'
                else:
                    if alt_text:
                        alt_text_string = ', alt={' + re.sub(r'[{}]', '', alt_text) + '}'
                    else:
                        alt_text_string = ''
                    if emoji:
                        output = '\\raisebox{-.6\\dp\\strutbox}{\\mbox{\\includegraphics[width=' + width + alt_text_string + ']{' + file_info['path'] + '}}}'
                    else:
                        output = '\\mbox{\\includegraphics[width=' + width + alt_text_string + ']{' + file_info['path'] + '}}'
                    if width == '\\textwidth':
                        output = '\\clearpage ' + output + '\\clearpage '
                return output
    return '[invalid graphics reference]'


def qr_include_string(match):
    string = match.group(1)
    try:
        width = match.group(2)
        assert width != 'None'
        width = re.sub(r'^(.*)px', convert_pixels, width)
        if width == "full":
            width = '\\textwidth'
    except:
        width = get_default_image_width()
    if match.lastindex == 3:
        alt_text = match.group(3)
    else:
        alt_text = None
    im = qrcode.make(string)
    with tempfile.NamedTemporaryFile(prefix="datemp", suffix=".png", delete=False) as the_image:
        # this_thread.temporary_resources.add(the_image.name)
        im.save(the_image.name)
        if alt_text:
            alt_text_string = ', alt={' + re.sub(r'[{}]', '', alt_text) + '}'
        else:
            alt_text_string = ''
        output = '\\mbox{\\includegraphics[width=' + width + alt_text_string + ']{' + the_image.name + '}}'
    if width == '\\textwidth':
        output = '\\clearpage ' + output + '\\clearpage '
    # logmessage("Output is " + output)
    return output


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
