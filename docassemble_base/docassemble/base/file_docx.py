import re
import os
import codecs
import time
import stat
import mimetypes
import tempfile
import string
import subprocess
from collections import deque
from copy import deepcopy
from xml.sax.saxutils import escape as html_escape
from docxtpl import InlineImage, RichText, Document, DocxTemplate
from docx.shared import Mm, Inches, Pt, Cm, Twips
import docx.opc.constants
from docx.oxml.section import CT_SectPr # For figuring out if an element is a section or not
import docx
from docxcompose.composer import Composer # For fixing up images, etc when including docx files within templates
from docassemble.base.functions import server, this_thread, package_template_filename, get_config, roman
from docassemble.base.error import DAError
import docassemble.base.filter
import docassemble.base.pandoc
from docassemble.base.logger import logmessage
from bs4 import BeautifulSoup, NavigableString, Tag
import PyPDF2

zerowidth = '\u200B'

QPDF_PATH = 'qpdf'
NoneType = type(None)

DEFAULT_PAGE_WIDTH = '6.5in'

list_types = ['1', 'A', 'a', 'I', 'i']

def image_for_docx(fileref, question, tpl, width=None):
    if fileref.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DALocalFile', 'DAStaticFile'):
        file_info = dict(fullpath=fileref.path())
    else:
        file_info = server.file_finder(fileref, question=question)
    if 'path' in file_info and 'extension' in file_info:
        docassemble.base.filter.convert_svg_to_png(file_info)
    if 'fullpath' not in file_info:
        return '[FILE NOT FOUND]'
    if width is not None:
        m = re.search(r'^([0-9\.]+) *([A-Za-z]*)', str(width))
        if m:
            amount = float(m.group(1))
            units = m.group(2).lower()
            if units in ['in', 'inches', 'inch']:
                the_width = Inches(amount)
            elif units in ['pt', 'pts', 'point', 'points']:
                the_width = Pt(amount)
            elif units in ['mm', 'millimeter', 'millimeters']:
                the_width = Mm(amount)
            elif units in ['cm', 'centimeter', 'centimeters']:
                the_width = Cm(amount)
            elif units in ['twp', 'twip', 'twips']:
                the_width = Twips(amount)
            else:
                the_width = Pt(amount)
        else:
            the_width = Inches(2)
    else:
        the_width = Inches(2)
    return InlineImage(tpl, file_info['fullpath'], the_width)

def transform_for_docx(text):
    if type(text) in (int, float, bool, NoneType):
        return text
    text = str(text)
    return text

def create_hyperlink(url, anchor_text, tpl):
    return InlineHyperlink(tpl, url, sanitize_xml(anchor_text))

class InlineHyperlink:
    def __init__(self, tpl, url, anchor_text):
        self.tpl = tpl
        self.url = url
        self.anchor_text = anchor_text
    def _insert_link(self):
        ref = self.tpl.docx._part.relate_to(self.url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
        return '</w:t></w:r><w:hyperlink r:id="%s"><w:r><w:rPr><w:rStyle w:val="InternetLink"/></w:rPr><w:t>%s</w:t></w:r></w:hyperlink><w:r><w:rPr></w:rPr><w:t xml:space="preserve">' % (ref, html_escape(self.anchor_text))
    def __str__(self):
        return self._insert_link()

def fix_subdoc(masterdoc, subdoc_info):
    """Fix the images, styles, references, shapes, etc of a subdoc"""
    subdoc = subdoc_info['subdoc']
    change_numbering = subdoc_info['change_numbering']
    composer = Composer(masterdoc) # Using docxcompose
    composer.reset_reference_mapping()

    # This is the same as the docxcompose function, except it doesn't copy the elements over.
    # Copying the elements over is done by returning the subdoc XML in this function.
    # Both sd.subdocx and the master template file are changed with these functions.
    composer._create_style_id_mapping(subdoc)
    for element in subdoc.element.body:
        if isinstance(element, CT_SectPr):
            continue
        composer.add_referenced_parts(subdoc.part, masterdoc.part, element)
        composer.add_styles(subdoc, element)
        if change_numbering:
            try:
                composer.add_numberings(subdoc, element)
                composer.restart_first_numbering(subdoc, element)
            except:
                pass
        composer.add_images(subdoc, element)
        composer.add_shapes(subdoc, element)
        composer.add_footnotes(subdoc, element)
        composer.remove_header_and_footer_references(subdoc, element)

    composer.add_styles_from_other_parts(subdoc)
    composer.renumber_bookmarks()
    composer.renumber_docpr_ids()
    composer.fix_section_types(subdoc)

def include_docx_template(template_file, **kwargs):
    """Include the contents of one docx file inside another docx file."""
    use_jinja = kwargs.get('_use_jinja2', True)
    if this_thread.evaluation_context is None:
        return 'ERROR: not in a docx file'
    if template_file.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DALocalFile', 'DAStaticFile'):
        template_path = template_file.path()
    else:
        template_path = package_template_filename(template_file, package=this_thread.current_package)
    sd = this_thread.misc['docx_template'].new_subdoc()
    sd.subdocx = Document(template_path)
    if not use_jinja:
        return sanitize_xml(str(sd))
    if '_inline' in kwargs:
        single_paragraph = True
        del kwargs['_inline']
    else:
        single_paragraph = False
    if 'change_numbering' in kwargs:
        change_numbering = bool(kwargs['change_numbering'])
        del kwargs['change_numbering']
    else:
        change_numbering = True

    # We need to keep a copy of the subdocs so we can fix up the master template in the end (in parse.py)
    # Given we're half way through processing the template, we can't fix the master template here
    # we have to do it in post
    if 'docx_subdocs' not in this_thread.misc:
        this_thread.misc['docx_subdocs'] = []
    this_thread.misc['docx_subdocs'].append({'subdoc': deepcopy(sd.subdocx), 'change_numbering': change_numbering})

    # Fix the subdocs before they are included in the template
    fix_subdoc(this_thread.misc['docx_template'], {'subdoc': sd.subdocx, 'change_numbering': change_numbering})

    first_paragraph = sd.subdocx.paragraphs[0]
    for key, val in kwargs.items():
        if hasattr(val, 'instanceName'):
            the_repr = val.instanceName
        else:
            the_repr = '_codecs.decode(_array.array("b", "' + re.sub(r'\n', '', codecs.encode(bytearray(val, encoding='utf-8'), 'base64').decode()) + '".encode()), "base64").decode()'
        first_paragraph.insert_paragraph_before(str("{%%p set %s = %s %%}" % (key, the_repr)))
    if 'docx_include_count' not in this_thread.misc:
        this_thread.misc['docx_include_count'] = 0
    this_thread.misc['docx_include_count'] += 1
    if single_paragraph:
        return re.sub(r'<w:p[^>]*>\s*(.*)</w:p>\s*', r'\1', str(first_paragraph._p.xml), flags=re.DOTALL)
    return sd

def get_children(descendants, parsed):
    subelement = False
    descendants_buff = deque()
    if descendants is None:
        return descendants_buff
    if isinstance(descendants, NavigableString):
        parsed.append(descendants)
    else:
        for child in descendants.children:
            if child.name is None:
                if subelement is False:
                    parsed.append(child)
                else:
                    descendants_buff.append(child)
            else:
                if subelement is False:
                    subelement = True
                    descendants_buff.append(child)
                else:
                    descendants_buff.append(child)
    descendants_buff.reverse()
    return descendants_buff

def html_linear_parse(soup):
    html_tag = soup.html
    descendants = deque()
    descendants.appendleft(html_tag)
    parsed = deque()
    while len(list(descendants)) > 0:
        child = descendants.popleft()
        from_children = get_children(child, parsed)
        descendants.extendleft(from_children)
    return parsed

def Alpha(number):
    multiplier = int((number - 1) / 26)
    indexno = (number - 1) % 26
    return string.ascii_uppercase[indexno] * (multiplier + 1)

def alpha(number):
    multiplier = int((number - 1) / 26)
    indexno = (number - 1) % 26
    return string.ascii_lowercase[indexno] * (multiplier + 1)

def Roman_Numeral(number):
    return roman((number - 1) % 4000, case='upper')

def roman_numeral(number):
    return roman((number - 1) % 4000, case='lower')

class SoupParser:
    def __init__(self, tpl):
        self.paragraphs = [dict(params=dict(style='p', indentation=0, list_number=1), runs=[RichText('')])]
        self.current_paragraph = self.paragraphs[-1]
        self.run = self.current_paragraph['runs'][-1]
        self.bold = False
        self.center = False
        self.list_number = 1
        self.list_type = list_types[-1]
        self.italic = False
        self.underline = False
        self.strike = False
        self.indentation = 0
        self.style = 'p'
        self.still_new = True
        self.size = None
        self.charstyle = None
        self.color = None
        self.tpl = tpl
    def new_paragraph(self, classes, styles):
        if self.still_new:
            # logmessage("new_paragraph is still new and style is " + self.style + " and indentation is " + str(self.indentation))
            self.current_paragraph['params']['style'] = self.style
            self.current_paragraph['params']['indentation'] = self.indentation
            self.set_attribs(classes, styles)
            self.list_number += 1
            return
        # logmessage("new_paragraph where style is " + self.style + " and indentation is " + str(self.indentation))
        self.current_paragraph = dict(params=dict(style=self.style, indentation=self.indentation, list_number=self.list_number), runs=[RichText('')])
        self.set_attribs(classes, styles)
        self.list_number += 1
        self.paragraphs.append(self.current_paragraph)
        self.run = self.current_paragraph['runs'][-1]
        self.still_new = True
    def set_attribs(self, classes, styles):
        if 'dacenter' in classes:
            self.current_paragraph['params']['align'] = 'center'
        elif 'daflushright' in classes:
            self.current_paragraph['params']['align'] = 'end'
        else:
            self.current_paragraph['params']['align'] = 'start'
        if len(classes):
            if 'daspacingtight' in classes:
                self.current_paragraph['params']['spacing'] = 240
                self.current_paragraph['params']['after'] = 0
            elif 'daspacingsingle' in classes:
                self.current_paragraph['params']['spacing'] = 240
                self.current_paragraph['params']['after'] = 240
            elif 'daspacingdouble' in classes:
                self.current_paragraph['params']['spacing'] = 480
                self.current_paragraph['params']['after'] = 0
            elif 'daspacingoneandahalf' in classes:
                self.current_paragraph['params']['spacing'] = 260
                self.current_paragraph['params']['after'] = 0
            elif 'daspacingtriple' in classes:
                self.current_paragraph['params']['spacing'] = 700
                self.current_paragraph['params']['after'] = 0
        if styles:
            m = re.search(r'margin-left:([0-9\.]+)px', styles)
            if m:
                self.current_paragraph['params']['leftindent'] = 20 * int(m.group(1))
            m = re.search(r'margin-right:([0-9\.]+)px', styles)
            if m:
                self.current_paragraph['params']['rightindent'] = 20 * int(m.group(1))
            m = re.search(r'text-indent:([0-9\.]+)px', styles)
            if m:
                self.current_paragraph['params']['firstline'] = 20 * int(m.group(1))
    def __str__(self):
        output = ''
        for para in self.paragraphs:
            # logmessage("Got a paragraph where style is " + para['params']['style'] + " and indentation is " + str(para['params']['indentation']))
            output += '<w:p><w:pPr><w:pStyle w:val="Normal"/>'
            if para['params']['align'] == 'center':
                output += '<w:jc w:val="center"/>'
            elif para['params']['align'] == 'end':
                output += '<w:jc w:val="end"/>'
            if 'spacing' in para['params']:
                output += '<w:spacing w:before="0" w:after="' + str(para['params']['after']) + '" w:line="' + str(para['params']['spacing']) + '" w:lineRule="auto" w:beforeAutospacing="0" w:afterAutospacing="0"/>'
            if para['params']['style'] == 'ul' or para['params']['style'].startswith('ol'):
                if 'leftindent' in para['params']:
                    left_indent = para['params']['leftindent']
                else:
                    left_indent = 36*para['params']['indentation']
                if 'rightindent' in para['params']:
                    right_indent = para['params']['rightindent']
                else:
                    right_indent = 0
                output += '<w:ind w:left="' + str(left_indent) + '" w:right="' + str(right_indent) + '" w:hanging="0"/>'
            elif para['params']['style'] == 'blockquote':
                if 'spacing' not in para['params']:
                    output += '<w:spacing w:before="0" w:after="240" w:line="240" w:lineRule="auto" w:beforeAutospacing="0" w:afterAutospacing="0"/>'
                output += '<w:ind w:left="' + str(36*para['params']['indentation']) + '" w:right="' + str(36*para['params']['indentation']) + '" w:hanging="0"/>'
            elif 'leftindent' in para['params'] or 'rightindent' in para['params'] or 'firstline' in para['params']:
                if 'leftindent' in para['params']:
                    left_indent = para['params']['leftindent']
                else:
                    left_indent = 0
                if 'rightindent' in para['params']:
                    right_indent = para['params']['rightindent']
                else:
                    right_indent = 0
                if 'firstline' in para['params']:
                    first_line = para['params']['firstline']
                else:
                    first_line = 0
                output += '<w:ind w:left="' + str(left_indent) + '" w:right="' + str(right_indent) + '" w:hanging="0" w:firstLine="' + str(first_line) + '"/>'
            output += '<w:rPr></w:rPr></w:pPr>'
            if para['params']['style'] == 'ul':
                output += str(RichText("•\t"))
            if para['params']['style'] == 'ol1':
                output += str(RichText(str(para['params']['list_number']) + ".\t"))
            elif para['params']['style'] == 'olA':
                output += str(RichText(Alpha(para['params']['list_number']) + ".\t"))
            elif para['params']['style'] == 'ola':
                output += str(RichText(alpha(para['params']['list_number']) + ".\t"))
            elif para['params']['style'] == 'olI':
                output += str(RichText(Roman_Numeral(para['params']['list_number']) + ".\t"))
            elif para['params']['style'] == 'oli':
                output += str(RichText(roman_numeral(para['params']['list_number']) + ".\t"))
            for run in para['runs']:
                output += str(run)
            output += '</w:p>'
        return output
    def start_link(self, url):
        ref = self.tpl.docx._part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
        self.current_paragraph['runs'].append('<w:hyperlink r:id="%s">' % (ref, ))
        self.new_run()
        self.still_new = False
    def end_link(self):
        self.current_paragraph['runs'].append('</w:hyperlink>')
        self.new_run()
        self.still_new = False
    def new_run(self):
        self.current_paragraph['runs'].append(RichText(''))
        self.run = self.current_paragraph['runs'][-1]
    def traverse(self, elem):
        for part in elem.contents:
            if isinstance(part, NavigableString):
                self.run.add(str(part), italic=self.italic, bold=self.bold, underline=self.underline, strike=self.strike, size=self.size, style=self.charstyle, color=self.color)
                self.still_new = False
            elif isinstance(part, Tag):
                # logmessage("Part name is " + str(part.name))
                if part.name == 'p':
                    if 'class' in part.attrs:
                        classes = part.attrs['class']
                    else:
                        classes = []
                    if 'style' in part.attrs:
                        styles = part.attrs['style']
                    else:
                        styles = ""
                    self.new_paragraph(classes, styles)
                    if 'dabold' in classes:
                        self.bold = True
                    self.traverse(part)
                    if 'dabold' in classes:
                        self.bold = False
                elif part.name == 'li':
                    if 'class' in part.attrs:
                        classes = part.attrs['class']
                    else:
                        classes = []
                    if 'style' in part.attrs:
                        styles = part.attrs['style']
                    else:
                        styles = ""
                    self.new_paragraph(classes, styles)
                    self.traverse(part)
                elif part.name == 'ul':
                    # logmessage("Entering a UL")
                    oldstyle = self.style
                    self.style = 'ul'
                    self.indentation += 10
                    self.traverse(part)
                    self.indentation -= 10
                    self.style = oldstyle
                    # logmessage("Leaving a UL")
                elif part.name == 'ol':
                    # logmessage("Entering a OL")
                    oldstyle = self.style
                    oldlistnumber = self.list_number
                    oldlisttype = self.list_type
                    if part.get('type', None) in list_types:
                        self.list_type = part['type']
                    else:
                        self.list_type = list_types[(list_types.index(self.list_type) + 1) % 5]
                    try:
                        self.list_number = int(part.get('start', 1))
                    except:
                        self.list_number = 1
                    self.style = 'ol' + self.list_type
                    self.indentation += 10
                    self.traverse(part)
                    self.indentation -= 10
                    self.list_type = oldlisttype
                    self.list_number = oldlistnumber
                    self.style = oldstyle
                    # logmessage("Leaving a OL")
                elif part.name == 'strong':
                    self.bold = True
                    self.traverse(part)
                    self.bold = False
                elif part.name == 'em':
                    self.italic = True
                    self.traverse(part)
                    self.italic = False
                elif part.name == 'strike':
                    self.strike = True
                    self.traverse(part)
                    self.strike = False
                elif part.name == 'u':
                    self.underline = True
                    self.traverse(part)
                    self.underline = False
                elif part.name == 'blockquote':
                    oldstyle = self.style
                    self.style = 'blockquote'
                    self.indentation += 20
                    self.traverse(part)
                    self.indentation -= 20
                    self.style = oldstyle
                elif re.match(r'h[1-6]', part.name):
                    oldsize = self.size
                    self.size = 60 - ((int(part.name[1]) - 1) * 10)
                    if 'class' in part.attrs:
                        classes = part.attrs['class']
                    else:
                        classes = []
                    if 'style' in part.attrs:
                        styles = part.attrs['style']
                    else:
                        styles = ""
                    self.new_paragraph(classes, styles)
                    self.bold = True
                    self.traverse(part)
                    self.bold = False
                    self.size = oldsize
                elif part.name == 'a':
                    self.start_link(part['href'])
                    if self.tpl.da_hyperlink_style:
                        self.charstyle = self.tpl.da_hyperlink_style
                    else:
                        self.underline = True
                        self.color = '#0000ff'
                    self.traverse(part)
                    if self.tpl.da_hyperlink_style:
                        self.charstyle = None
                    else:
                        self.underline = False
                        self.color = None
                    self.end_link()
                elif part.name == 'br':
                    self.run.add("\n", italic=self.italic, bold=self.bold, underline=self.underline, strike=self.strike, size=self.size, style=self.charstyle, color=self.color)
                    self.still_new = False
            else:
                logmessage("Encountered a " + part.__class__.__name__)

class InlineSoupParser:
    def __init__(self, tpl):
        self.runs = [RichText('')]
        self.run = self.runs[-1]
        self.bold = False
        self.italic = False
        self.underline = False
        self.indentation = 0
        self.style = 'p'
        self.strike = False
        self.size = None
        self.charstyle = None
        self.color = None
        self.tpl = tpl
        self.at_start = True
        self.list_number = 1
        self.list_type = list_types[-1]
    def new_paragraph(self):
        if self.at_start:
            self.at_start = False
        else:
            self.run.add("\n", italic=self.italic, bold=self.bold, underline=self.underline, strike=self.strike, size=self.size, style=self.charstyle, color=self.color)
        if self.indentation:
            self.run.add("\t" * self.indentation)
        if self.style == 'ul':
            self.run.add("•\t")
        if self.style == 'ol1':
            self.run.add(str(self.list_number) + ".\t")
            self.list_number += 1
        elif self.style == 'olA':
            self.run.add(Alpha(self.list_number) + ".\t")
            self.list_number += 1
        elif self.style == 'ola':
            self.run.add(alpha(self.list_number) + ".\t")
            self.list_number += 1
        elif self.style == 'olI':
            self.run.add(Roman_Numeral(self.list_number) + ".\t")
            self.list_number += 1
        elif self.style == 'oli':
            self.run.add(roman_numeral(self.list_number) + ".\t")
            self.list_number += 1
        # else:
        #     self.list_number = 1
    def __str__(self):
        output = ''
        for run in self.runs:
            output += str(run)
        return output
    def start_link(self, url):
        ref = self.tpl.docx._part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
        self.runs.append('<w:hyperlink r:id="%s">' % (ref, ))
        self.new_run()
    def end_link(self):
        self.runs.append('</w:hyperlink>')
        self.new_run()
    def new_run(self):
        self.runs.append(RichText(''))
        self.run = self.runs[-1]
    def traverse(self, elem):
        for part in elem.contents:
            if isinstance(part, NavigableString):
                self.run.add(str(part), italic=self.italic, bold=self.bold, underline=self.underline, strike=self.strike, size=self.size, style=self.charstyle, color=self.color)
            elif isinstance(part, Tag):
                if part.name in ('p', 'blockquote'):
                    self.new_paragraph()
                    self.traverse(part)
                elif part.name == 'li':
                    self.new_paragraph()
                    self.traverse(part)
                elif part.name == 'ul':
                    oldstyle = self.style
                    self.style = 'ul'
                    self.indentation += 1
                    self.traverse(part)
                    self.indentation -= 1
                    self.style = oldstyle
                elif part.name == 'ol':
                    oldstyle = self.style
                    oldlistnumber = self.list_number
                    oldlisttype = self.list_type
                    if part.get('type', None) in list_types:
                        self.list_type = part['type']
                    else:
                        self.list_type = list_types[(list_types.index(self.list_type) + 1) % 5]
                    try:
                        self.list_number = int(part.get('start', 1))
                    except:
                        self.list_number = 1
                    self.style = 'ol' + self.list_type
                    self.indentation += 1
                    self.traverse(part)
                    self.indentation -= 1
                    self.list_type = oldlisttype
                    self.list_number = oldlistnumber
                    self.style = oldstyle
                elif part.name == 'strong':
                    self.bold = True
                    self.traverse(part)
                    self.bold = False
                elif part.name == 'em':
                    self.italic = True
                    self.traverse(part)
                    self.italic = False
                elif part.name == 'strike':
                    self.strike = True
                    self.traverse(part)
                    self.strike = False
                elif part.name == 'u':
                    self.underline = True
                    self.traverse(part)
                    self.underline = False
                elif re.match(r'h[1-6]', part.name):
                    oldsize = self.size
                    self.size = 60 - ((int(part.name[1]) - 1) * 10)
                    self.bold = True
                    self.traverse(part)
                    self.bold = False
                    self.size = oldsize
                elif part.name == 'a':
                    self.start_link(part['href'])
                    if self.tpl.da_hyperlink_style:
                        self.charstyle = self.tpl.da_hyperlink_style
                    else:
                        self.underline = True
                        self.color = '#0000ff'
                    self.traverse(part)
                    if self.tpl.da_hyperlink_style:
                        self.charstyle = None
                    else:
                        self.underline = False
                        self.color = None
                    self.end_link()
                elif part.name == 'br':
                    self.run.add("\n", italic=self.italic, bold=self.bold, underline=self.underline, strike=self.strike, size=self.size, style=self.charstyle, color=self.color)
            else:
                logmessage("Encountered a " + part.__class__.__name__)

def inline_markdown_to_docx(text, question, tpl):
    old_context = docassemble.base.functions.this_thread.evaluation_context
    docassemble.base.functions.this_thread.evaluation_context = None
    try:
        text = str(text)
    except:
        docassemble.base.functions.this_thread.evaluation_context = old_context
        raise
    docassemble.base.functions.this_thread.evaluation_context = old_context
    source_code = docassemble.base.filter.markdown_to_html(text, do_terms=False)
    source_code = re.sub("\n", ' ', source_code)
    source_code = re.sub(">\s+<", '><', source_code)
    soup = BeautifulSoup('<html>' + source_code + '</html>', 'html.parser')
    parser = InlineSoupParser(tpl)
    for elem in soup.find_all(recursive=False):
        parser.traverse(elem)
    output = str(parser)
    return docassemble.base.filter.docx_template_filter(output, question=question, replace_newlines=False)

def markdown_to_docx(text, question, tpl):
    old_context = docassemble.base.functions.this_thread.evaluation_context
    docassemble.base.functions.this_thread.evaluation_context = None
    try:
        text = str(text)
    except:
        docassemble.base.functions.this_thread.evaluation_context = old_context
        raise
    docassemble.base.functions.this_thread.evaluation_context = old_context
    if get_config('new markdown to docx', False):
        source_code = docassemble.base.filter.markdown_to_html(text, do_terms=False)
        source_code = re.sub("\n", ' ', source_code)
        source_code = re.sub(">\s+<", '><', source_code)
        soup = BeautifulSoup('<html>' + source_code + '</html>', 'html.parser')
        parser = SoupParser(tpl)
        for elem in soup.find_all(recursive=False):
            parser.traverse(elem)
        output = str(parser)
        # logmessage(output)
        return docassemble.base.filter.docx_template_filter(output, question=question)
    return inline_markdown_to_docx(text, question, tpl)

def safe_pypdf_reader(filename):
    try:
        return PyPDF2.PdfFileReader(open(filename, 'rb'), overwriteWarnings=False)
    except PyPDF2.utils.PdfReadError:
        new_filename = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
        qpdf_subprocess_arguments = [QPDF_PATH, filename, new_filename.name]
        try:
            result = subprocess.run(qpdf_subprocess_arguments, timeout=60, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
        if result != 0:
            raise Exception("Call to qpdf failed for template " + str(filename) + " where arguments were " + " ".join(qpdf_subprocess_arguments))
        return PyPDF2.PdfFileReader(open(new_filename.name, 'rb'), overwriteWarnings=False)

def pdf_pages(file_info, width):
    output = ''
    if width is None:
        width = DEFAULT_PAGE_WIDTH
    if not os.path.isfile(file_info['path'] + '.pdf'):
        if file_info['extension'] in ('rtf', 'doc', 'odt') and not os.path.isfile(file_info['path'] + '.pdf'):
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
            server.fg_make_png_for_pdf_path(file_info['path'] + '.pdf', 'page')
        if os.path.isfile(page_file['fullpath']):
            output += str(image_for_docx(docassemble.base.functions.DALocalFile(page_file['fullpath']), docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width))
        else:
            output += "[Error including page image]"
        output += ' '
    return output

def concatenate_files(path_list):
    new_path_list = []
    for path in path_list:
        mimetype, encoding = mimetypes.guess_type(path)
        if mimetype in ('application/rtf', 'application/msword', 'application/vnd.oasis.opendocument.text'):
            new_docx_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
            if mimetype == 'application/rtf':
                ext = 'rtf'
            elif mimetype == 'application/msword':
                ext = 'doc'
            elif mimetype == 'application/vnd.oasis.opendocument.text':
                ext = 'odt'
            docassemble.base.pandoc.convert_file(path, new_docx_file.name, ext, 'docx')
            new_path_list.append(new_docx_file.name)
        elif mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            new_path_list.append(path)
    if len(new_path_list) == 0:
        raise DAError("concatenate_files: no valid files to concatenate")
    if len(new_path_list) == 1:
        return new_path_list[0]
    composer = Composer(docx.Document(new_path_list[0]))
    for indexno in range(1, len(new_path_list)):
        composer.append(docx.Document(new_path_list[indexno]))
    docx_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
    composer.save(docx_file.name)
    return docx_file.name

def sanitize_xml(text):
    return re.sub(r'{([{%#])', '{' + zerowidth + r'\1', re.sub(r'([}%#])}', r'\1' + zerowidth + '}', text))
