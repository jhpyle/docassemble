import sys
import re
import markdown
import docassemble.base.util
import docassemble.base.filter
from docassemble.base.pandoc import Pandoc
from mdx_smartypants import SmartypantsExt

from docassemble.base.logger import logmessage
from rtfng.object.picture import Image
import PIL

DEFAULT_PAGE_WIDTH = '6.5in'

term_start = re.compile(r'\[\[')
term_match = re.compile(r'\[\[([^\]]*)\]\]')
noquote_match = re.compile(r'"')
lt_match = re.compile(r'<')
gt_match = re.compile(r'>')
amp_match = re.compile(r'&')
emoji_match = re.compile(r':([^ ]+):')
extension_match = re.compile(r'\.[a-z]+$')

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

def blank_mail_variable(*args, **kwargs):
    return(None)

mail_variable = blank_mail_variable

def set_mail_variable(func):
    global mail_variable
    #logmessage("set the mail variable to " + str(func) + "\n")
    mail_variable = func
    return

def blank_file_finder(*args, **kwargs):
    return(dict(filename="invalid"))

file_finder = blank_file_finder

def set_file_finder(func):
    global file_finder
    #logmessage("set the file finder to " + str(func) + "\n")
    file_finder = func
    return

def blank_url_finder(*args, **kwargs):
    return('about:blank')

url_finder = blank_url_finder

def set_url_finder(func):
    global url_finder
    url_finder = func
    return

rtf_spacing = {'single': '', 'oneandahalf': '\\sl360\\slmult1', 'double': '\\sl480\\slmult1', 'triple': '\\sl720\\slmult1'}

rtf_after_space = {'single': 1, 'oneandahalf': 0, 'double': 0, 'triplespacing': 0}

def rtf_filter(text, metadata=dict()):
    if 'fontsize' in metadata:
        text = re.sub(r'{\\pard', '\\fs' + str(convert_length(metadata['fontsize'], 'hp')) + ' {\\pard', text, count=1)
        after_space_multiplier = str(convert_length(metadata['fontsize'], 'twips'))
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
        default_spacing = 'single'
    elif 'OneAndAHalfSpacing' in metadata and metadata['OneAndAHalfSpacing']:
        default_spacing = 'oneandahalf'
    elif 'DoubleSpacing' in metadata and metadata['DoubleSpacing']:
        default_spacing = 'double'
    elif 'TripleSpacing' in metadata and metadata['TripleSpacing']:
        default_spacing = 'triple'
    else:
        default_spacing = 'double'
    after_space = after_space_multiplier * rtf_after_space[default_spacing]
    text = re.sub(r'{\\pard \\ql \\f0 \\sa180 \\li0 \\fi0 \[(BEGIN_TWOCOL|BREAK|END_TWOCOL|BEGIN_CAPTION|VERTICAL_LINE|END_CAPTION|SINGLESPACING|DOUBLESPACING|INDENTATION|NOINDENTATION|PAGEBREAK|SKIPLINE)\] *', r'[\1]{\\pard \\ql \\f0 \\sa180 \\li0 \\fi0 ', text)
    text = re.sub(r'{\\pard \\ql \\f0 \\sa180 \\li0 \\fi0 *\\par}', r'', text)
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\[BREAK\](.+?)\[END_TWOCOL\]', rtf_caption_table, text, flags=re.DOTALL)
    text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', image_as_rtf, text)
    text = re.sub(r'\[IMAGE ([^,\]]+), *([0-9A-Za-z.%]+)\]', image_as_rtf, text)
    text = re.sub(r'\[IMAGE ([^,\]]+)\]', image_as_rtf, text)
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\[VERTICAL_LINE\](.+?)\[END_CAPTION\]', rtf_caption_table, text)
    text = re.sub(r'\[NBSP\]', r'\\~ ', text)
    text = re.sub(r'\[ENDASH\]', r'{\\endash}', text)
    text = re.sub(r'\[EMDASH\]', r'{\\emdash}', text)
    text = re.sub(r'\[HYPHEN\]', r'-', text)
    text = re.sub(r'\[PAGEBREAK\] *', r'\\page ', text)
    text = re.sub(r'\[PAGENUM\]', r'{\\chpgn}', text)
    text = re.sub(r'\[SECTIONNUM\]', r'{\\sectnum}', text)
    text = re.sub(r'\[SKIPLINE\] *', r'\\line ', text)
    text = re.sub(r'\[NEWLINE\] *', r'\\line ', text)
    text = re.sub(r'\[BR\] *', r'\\line ', text)
    text = re.sub(r'\[TAB\] *', r'\\tab ', text)
    text = re.sub(r'\[FLUSHLEFT\] *', r'\\ql ', text)
    text = re.sub(r'\[CENTER\] *', r'\\qc ', text)
    text = re.sub(r'\[BOLDCENTER\] *', r'\\qc \\b ', text)
    text = re.sub(r'\\sa180', '\sa0', text)
    if re.search(r'\[(SINGLESPACING|DOUBLESPACING|TRIPLESPACING|ONEANDAHALFSPACING|INDENTATION|NOINDENTATION)\]', text):
        text = re.sub(r'[\n ]*\[(SINGLESPACING|DOUBLESPACING|TRIPLESPACING|ONEANDAHALFSPACING|INDENTATION|NOINDENTATION)\][\n ]*', r'\n[\1]\n', text)
        lines = text.split('\n')
        spacing_command = rtf_spacing[default_spacing]
        if default_indentation:
            indentation_command = '\\fi' + indentation_amount
        else:
            indentation_command = ''
        text = ''
        for line in lines:
            if re.search(r'\[SINGLESPACING\]', line):
                spacing_command = rtf_spacing['single']
                after_space = after_space_multiplier * rtf_after_space[default_spacing]
            elif re.search(r'\[ONEANDAHALFSPACING\]', line):
                spacing_command = rtf_spacing['oneandahalf']
                after_space = after_space_multiplier * rtf_after_space[default_spacing]
            elif re.search(r'\[DOUBLESPACING\]', line):
                spacing_command = rtf_spacing['double']
                after_space = after_space_multiplier * rtf_after_space[default_spacing]
            elif re.search(r'\[TRIPLESPACING\]', line):
                spacing_command = rtf_spacing['triple']
                after_space = after_space_multiplier * rtf_after_space[default_spacing]
            if re.search(r'\[INDENTATION\]', line):
                indentation_command = '\\fi' + indentation_amount
            elif re.search(r'\[NOINDENTATION\]', line):
                indentation_command = ''
            line = re.sub(r'\\pard ', '\\pard ' + spacing_command + indentation_command + ' ', line)
            if after_space > 0:
                line = re.sub(r'\\sa[0-9]+ ', '\\sa' + str(after_space) + ' ', line)
            text += line + '\n'
    return(text)

def pdf_filter(text, metadata=dict()):
    text = text + "\n\n"
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', emoji_include_string, text)
    text = re.sub(r'\[IMAGE ([^,\]]+), *([0-9A-Za-z.%]+)\]', image_include_string, text)
    text = re.sub(r'\[IMAGE ([^,\]]+)\]', image_include_string, text)
    text = re.sub(r'\\clearpage *\\clearpage', r'\\clearpage', text)
    text = re.sub(r'\[INDENTATION\]', r'\\setlength{\\parindent}{0.5in}\\setlength{\\RaggedRightParindent}{\\parindent}', text)    
    text = re.sub(r'\[NOINDENTATION\]', r'\\setlength{\\parindent}{0in}\\setlength{\\RaggedRightParindent}{\\parindent}', text)    
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\[VERTICAL_LINE\](.+?)\[END_CAPTION\]', pdf_caption, text, flags=re.DOTALL)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\[BREAK\](.+?)\[END_TWOCOL\]', pdf_two_col, text, flags=re.DOTALL)
    text = re.sub(r'\[SINGLESPACING\] *', r'\\singlespacing\\setlength{\\parskip}{\\myfontsize} ', text)
    text = re.sub(r'\[DOUBLESPACING\] *', r'\\doublespacing\\setlength{\\parindent}{0.5in}\\setlength{\\RaggedRightParindent}{\\parindent} ', text)
    text = re.sub(r'\[NBSP\]', r'\\myshow{\\nonbreakingspace}', text)
    text = re.sub(r'\[ENDASH\]', r'\\myshow{\\myendash}', text)
    text = re.sub(r'\[EMDASH\]', r'\\myshow{\\myemdash}', text)
    text = re.sub(r'\[HYPHEN\]', r'\\myshow{\\myhyphen}', text)
    text = re.sub(r'\[PAGEBREAK\] *', r'\\clearpage ', text)
    text = re.sub(r'\[PAGENUM\] *', r'\\myshow{\\thepage} ', text)
    text = re.sub(r'\[SECTIONNUM\] *', r'\\myshow{\\thesection} ', text)
    text = re.sub(r'\[SKIPLINE\] *', r'\\par\\myskipline ', text)
    text = re.sub(r'\[VERTICALSPACE\] *', r'\\rule[-24pt]{0pt}{0pt}', text)
    text = re.sub(r'\[NEWLINE\] *', r'\\newline ', text)
    text = re.sub(r'\[BR\] *', r'\\manuallinebreak ', text)
    text = re.sub(r'\[TAB\] *', r'\\manualindent ', text)
    text = re.sub(r'\[FLUSHLEFT\] *(.+?)\n\n', flushleft_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[CENTER\] *(.+?)\n\n', center_pdf, text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BOLDCENTER\] *(.+?)\n\n', boldcenter_pdf, text, flags=re.MULTILINE | re.DOTALL)
    return(text)

def html_filter(text):
    text = text + "\n\n"
    text = re.sub(r'^[|] (.*)$', r'\1<br>', text, flags=re.MULTILINE)
    text = re.sub(r'\[EMOJI ([^,\]]+), *([0-9A-Za-z.%]+)\]', emoji_url_string, text)
    text = re.sub(r'\[IMAGE ([^,\]]+), *([0-9A-Za-z.%]+)\]', image_url_string, text)
    text = re.sub(r'\[IMAGE ([^,\]]+)\]', image_url_string, text)
    text = re.sub(r'\[BEGIN_CAPTION\](.+?)\[VERTICAL_LINE\](.+?)\[END_CAPTION\]', r'<table style="width: 100%"><tr><td style="width: 50%; border-style: solid; border-right-width: 1px; padding-right: 1em; border-left-width: 0px; border-top-width: 0px; border-bottom-width: 0px">\1</td><td style="padding-left: 1em; width: 50%;">\2</td></tr></table>', text)
    text = re.sub(r'\[BEGIN_TWOCOL\](.+?)\[BREAK\](.+?)\[END_TWOCOL\]', r'<table style="width: 100%"><tr><td style="width: 50%; vertical-align: top; border-style: none; padding-right: 1em;">\1</td><td style="padding-left: 1em; vertical-align: top; width: 50%;">\2</td></tr></table>', text, flags=re.DOTALL)
    text = re.sub(r'\[SINGLESPACING\] *', r'', text)
    text = re.sub(r'\[DOUBLESPACING\] *', r'', text)
    text = re.sub(r'\[INDENTATION\] *', r'', text)
    text = re.sub(r'\[NOINDENTATION\] *', r'', text)
    text = re.sub(r'\[NBSP\]', r'&nbsp;', text)
    text = re.sub(r'\[ENDASH\]', r'&ndash;', text)
    text = re.sub(r'\[EMDASH\]', r'&mdash;', text)
    text = re.sub(r'\[HYPHEN\]', r'-', text)
    text = re.sub(r'\[PAGEBREAK\] *', r'', text)
    text = re.sub(r'\[PAGENUM\] *', r'', text)
    text = re.sub(r'\[SECTIONNUM\] *', r'', text)
    text = re.sub(r'\[SKIPLINE\] *', r'<br />', text)
    text = re.sub(r'\[NEWLINE\] *', r'<br />', text)
    text = re.sub(r'\[BR\] *', r'<br />', text)
    text = re.sub('\[TAB\] *', '<span style="display: inline-block; width: 4em;"></span>', text)
    text = re.sub(r'\[FLUSHLEFT\] *(.+?)\n\n', r'<p style="text-align: left;">\1</p>\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[CENTER\] *(.+?)\n\n', r'<p style="text-align: center;">\1</p>\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\[BOLDCENTER\] *(.+?)\n\n', r'<p style="text-align: center; font-weight: bold">\1</p>\n\n', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'\\_', r'__', text)
    text = re.sub(r'\n+$', r'', text)
    return(text)

def pdf_two_col(match, add_line=False):
    firstcol = match.group(1)
    secondcol = match.group(2)
    firstcol = re.sub(r'^[\n ]+', r'', firstcol)
    secondcol = re.sub(r'^[\n ]+', r'', secondcol)
    firstcol = re.sub(r'[\n ]+$', r'', firstcol)
    secondcol = re.sub(r'[\n ]+$', r'', secondcol)
    firstcol = re.sub(r' *\n *$', r'\n', firstcol)
    secondcol = re.sub(r' *\n *$', r'\n', secondcol)
    firstcol = re.sub(r'\n{2,}', r'[NEWLINE]', firstcol)
    secondcol = re.sub(r'\n{2,}', r'[NEWLINE]', secondcol)
    if add_line:
        return '\\noindent\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\mynoindent\\begin{tabular}{@{}m{0.49\\textwidth}|@{\\hspace{1em}}m{0.49\\textwidth}@{}}{' + firstcol + '} & {' + secondcol + '} \\\\ \\end{tabular}\\endgroup\\myskipline'
    else:
        return '\\noindent\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\mynoindent\\begin{tabular}{@{}p{0.49\\textwidth}@{\\hspace{1em}}p{0.49\\textwidth}@{}}{' + firstcol + '} & {' + secondcol + '} \\\\ \\end{tabular}\\endgroup\\myskipline'

def pdf_caption(match):
    return pdf_two_col(match, add_line=True)

def add_newlines(string):
    string = re.sub(r'\[(BR)\]', r'[NEWLINE]', string)
    string = re.sub(r' *\n', r'\n', string)
    string = re.sub(r'(?<!\[NEWLINE\])\n', r' [NEWLINE]\n', string)
    return string    

def flushleft_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return('\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\noindent ' + str(string) + '\\par\\endgroup' + "\n\n")

def center_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return('\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\Centering\\noindent ' + str(string) + '\\par\\endgroup' + "\n\n")

def boldcenter_pdf(match):
    string = match.group(1)
    string = re.sub(r'\[NEWLINE\] *', r'\\newline ', string)
    return('\\begingroup\\singlespacing\\setlength{\\parskip}{0pt}\\Centering\\bfseries\\noindent ' + str(string) + '\\par\\endgroup' + "\n\n")

def image_as_rtf(match):
    width_supplied = False
    try:
        width = match.group(2)
        width_supplied = True
    except:
        width = DEFAULT_IMAGE_WIDTH
    if width == 'full':
        width_supplied = False
    file_reference = match.group(1)
    file_info = file_finder(file_reference, convert={'svg': 'png'})
    if 'path' not in file_info:
        return ''
    if 'width' in file_info:
        return rtf_image(file_info, width, not width_supplied)
    elif file_info['extension'] == 'pdf':
        output = ''
        if not width_supplied:
            #logmessage("Adding page break\n")
            width = DEFAULT_PAGE_WIDTH
            output += '\\page '
        #logmessage("maxpage is " + str(int(file_info['pages'])) + "\n")
        for page in range(1, 1 + int(file_info['pages'])):
            #logmessage("Doing page " + str(page) + "\n")
            page_file = dict()
            page_file['extension'] = 'png'
            page_file['path'] = file_info['path'] + 'page-' + str(page)
            im = PIL.Image.open(page_file['path'] + ".png")
            page_file['width'], page_file['height'] = im.size
            output += rtf_image(page_file, width, False)
            if not width_supplied:
                #logmessage("Adding page break\n")
                output += '\\page '
            else:
                output += ' '
        #logmessage("Returning output\n")
        return(output)
    else:
        return('')

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
    return(content + image.Data)
    
unit_multipliers = {'twips':1440, 'hp': 144, 'in':72, 'pt':1, 'px':1, 'em':12, 'cm':28.346472}

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

def image_url_string(match, emoji=False):
    file_reference = match.group(1)
    try:
        width = match.group(2)
    except:
        width = "300px"
    if width == "full":
        width = "300px"    
    file_info = file_finder(file_reference)
    if 'extension' in file_info:
        if re.match(r'.*%$', width):
            width_string = "width:" + width
        else:
            width_string = "max-width:" + width
        if emoji:
            width_string += ';vertical-align: middle'
        if file_info['extension'] in ['png', 'jpg', 'gif', 'svg']:
            return('<img style="image-orientation:from-image;' + width_string + '" src="' + url_finder(file_reference) + '">')
        elif file_info['extension'] == 'pdf':
            output = '<img style="image-orientation:from-image;' + width_string + '" src="' + url_finder(file_reference, size="screen", page=1) + '">'
            if 'pages' in file_info and file_info['pages'] > 1:
                output += " (" + str(file_info['pages']) + " " + docassemble.base.util.word('pages') + ")"
            return(output)
        else:
            return('<a href="' + url_finder(file_reference) + '">' + file_info['filename'] + '</a>')
    else:
        return('[Invalid image reference; reference=' + str(file_reference) + ', width=' + str(width) + ', filename=' + file_info.get('filename', 'unknown') + ']')

def emoji_url_string(match):
    return(image_url_string(match, emoji=True))
    
def convert_pixels(match):
    pixels = match.group(1)
    return (str(int(pixels)/72.0) + "in")

def image_include_string(match, emoji=False):
    file_reference = match.group(1)
    try:
        width = match.group(2)
        width = re.sub(r'^(.*)px', convert_pixels, width)
        if width == "full":
            width = '\\textwidth'
    except:
        width = DEFAULT_IMAGE_WIDTH
    file_info = file_finder(file_reference, convert={'svg': 'eps'})
    if 'path' in file_info:
        if 'extension' in file_info:
            if file_info['extension'] in ['png', 'jpg', 'gif', 'pdf', 'eps']:
                if file_info['extension'] == 'pdf':
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

def emoji_include_string(match):
    return image_include_string(match, emoji=True)

def rtf_caption_table(match):
    table_text = """\\trowd \\irow0\\irowband0\\lastrow \\ltrrow\\ts24\\trgaph108\\trleft0\\trbrdrt\\brdrs\\brdrw10 \\trbrdrl\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrh\\brdrs\\brdrw10 \\trbrdrv\\brdrs\\brdrw10 
\\trftsWidth1\\trftsWidthB3\\trftsWidthA3\\trautofit1\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddft3\\trpaddfb3\\trpaddfr3\\trcbpat1\\trcfpat1\\tblrsid1508006\\tbllkhdrrows\\tbllkhdrcols\\tbllknocolband\\tblind0\\tblindtype3 \\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone 
\\clbrdrb\\brdrnone \\clbrdrr\\brdrs\\brdrw10 \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx4680\\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrs\\brdrw10 \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx9468\\pard\\plain \\ltrpar
\\ql \\li0\\ri0\\widctlpar\\intbl\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0\\pararsid1508006\\yts24 \\rtlch\\fcs1 \\af0\\afs22\\alang1025 \\ltrch\\fcs0 \\fs22\\lang1033\\langfe1033\\cgrid\\langnp1033\\langfenp1033 {\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid2427490 """ + match.group(1) + """}{\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid10753242\\charrsid2427490 \\cell }\\pard \\ltrpar
\\ql \\li162\\ri0\\widctlpar\\intbl\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin162\\pararsid15432102\\yts24 {\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\li240 \\insrsid2427490 """ + match.group(2) + """}{\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid10753242\\charrsid2427490 \\cell }\\pard\\plain \\ltrpar
\\ql \\li0\\ri0\\sa200\\sl276\\slmult1\\widctlpar\\intbl\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0 \\rtlch\\fcs1 \\af0\\afs22\\alang1025 \\ltrch\\fcs0 \\fs24\\lang1033\\langfe1033\\cgrid\\langnp1033\\langfenp1033 {\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\insrsid10753242 
\\trowd \\irow0\\irowband0\\lastrow \\ltrrow\\ts24\\trgaph108\\trleft0\\trbrdrt\\brdrs\\brdrw10 \\trbrdrl\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrh\\brdrs\\brdrw10 \\trbrdrv\\brdrs\\brdrw10 
\\trftsWidth1\\trftsWidthB3\\trftsWidthA3\\trautofit1\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddft3\\trpaddfb3\\trpaddfr3\\trcbpat1\\trcfpat1\\tblrsid1508006\\tbllkhdrrows\\tbllkhdrcols\\tbllknocolband\\tblind0\\tblindtype3 \\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrnone 
\\clbrdrb\\brdrnone \\clbrdrr\\brdrs\\brdrw10 \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx4680\\clvertalc\\clbrdrt\\brdrnone \\clbrdrl\\brdrs\\brdrw10 \\clbrdrb\\brdrnone \\clbrdrr\\brdrnone \\cltxlrtb\\clftsWidth3\\clwWidth4732 \\cellx9468\\row }"""
    table_text += """\\pard \\ltrpar
\\qc \\li0\\ri0\\sb0\\sl240\\slmult1\\widctlpar\\wrapdefault\\aspalpha\\aspnum\\faauto\\adjustright\\rin0\\lin0\\itap0\\pararsid10753242"""
    table_text = re.sub(r'\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0', r'\\rtlch\\fcs1 \\af0 \\ltrch\\fcs0 \\sl240 \\slmult1', table_text)
    return table_text

def emoji_html(text, status=None, images=None):
    if images is None:
        images = status.question.interview.images
    if text in images:
        if status is not None and images[text].attribution is not None:
            status.attributions.add(images[text].attribution)
        return("[EMOJI " + images[text].get_reference() + ', 1em]')
    else:
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

def markdown_to_html(a, trim=False, pclass=None, status=None, use_pandoc=False, escape=False, do_terms=True):
    if do_terms and status is not None:
        if len(status.question.interview.terms) > 0:
            for term in status.question.interview.terms:
                #logmessage("Searching for term " + term + "\n")
                a = status.question.interview.terms[term]['re'].sub(r'[[\1]]', a)
                #logmessage("string is now " + str(a) + "\n")
        if len(status.question.interview.images) > 0:
            a = emoji_match.sub((lambda x: emoji_html(x.group(1), status=status)), a)
    a = docassemble.base.filter.html_filter(unicode(a))
    if use_pandoc:
        converter = Pandoc()
        converter.output_format = 'html'
        converter.input_content = a
        converter.convert()
        result = converter.output_content
    else:
        result = markdown.markdown(a, extensions=[SmartypantsExt(configs=dict())], output_format='html5')
    result = re.sub('<a href', '<a target="_blank" href', result)
    if do_terms and status is not None and len(status.question.interview.terms) > 0 is not None and term_start.search(result):
        #logmessage("Found a term\n")
        result = term_match.sub((lambda x: add_terms(x.group(1), status.question.interview.terms)), result)
    if trim:
        result = result[3:-4]
    elif pclass:
        result = re.sub('<p>', '<p class="' + pclass + '">', result)
    if escape:
        result = noquote_match.sub('&quot;', result)
        result = lt_match.sub('&lt;', result)
        result = gt_match.sub('&gt;', result)
        result = amp_match.sub('&amp;', result)
    return(result)

def add_terms(termname, terms):
    #logmessage("add terms with " + termname + "\n")
    lower_termname = termname.lower()
    if lower_termname in terms:
        # title="' + noquote(termname) + '"
        return('<a style="cursor:pointer;color:#408E30" data-toggle="popover" data-placement="bottom" data-content="' + noquote(terms[lower_termname]['definition']) + '">' + str(termname) + '</a>')
    else:
        #logmessage(lower_termname + " is not in terms dictionary\n")
        return termname

def noquote(string):
    return noquote_match.sub('\\\"', string)
