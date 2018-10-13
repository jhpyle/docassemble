# -*- coding: utf-8 -*-
import re
from docxtpl import DocxTemplate, R, InlineImage, RichText, Listing, Document, Subdoc
from docx.shared import Mm, Inches, Pt
import docx.opc.constants
from docassemble.base.functions import server, this_thread, package_template_filename
import docassemble.base.filter
from xml.sax.saxutils import escape as html_escape
from types import NoneType
from docassemble.base.logger import logmessage
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import deque

def image_for_docx(fileref, question, tpl, width=None):
    if fileref.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DALocalFile'):
        file_info = dict(fullpath=fileref.path())
    else:
        file_info = server.file_finder(fileref, convert={'svg': 'png'}, question=question)
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
            else:
                the_width = Pt(amount)
        else:
            the_width = Inches(2)
    else:
        the_width = Inches(2)
    return InlineImage(tpl, file_info['fullpath'], the_width)

def transform_for_docx(text, question, tpl, width=None):
    if type(text) in (int, float, bool, NoneType):
        return text
    text = unicode(text)
    m = re.search(r'\[FILE ([^,\]]+), *([0-9\.]) *([A-Za-z]+) *\]', text)
    if m:
        amount = m.group(2)
        units = m.group(3).lower()
        if units in ['in', 'inches', 'inch']:
            the_width = Inches(amount)
        elif units in ['pt', 'pts', 'point', 'points']:
            the_width = Pt(amount)
        elif units in ['mm', 'millimeter', 'millimeters']:
            the_width = Mm(amount)
        else:
            the_width = Pt(amount)
        file_info = server.file_finder(m.group(1), convert={'svg': 'png'}, question=question)
        if 'fullpath' not in file_info:
            return '[FILE NOT FOUND]'
        return InlineImage(tpl, file_info['fullpath'], the_width)
    m = re.search(r'\[FILE ([^,\]]+)\]', text)
    if m:
        file_info = server.file_finder(m.group(1), convert={'svg': 'png'}, question=question)
        if 'fullpath' not in file_info:
            return '[FILE NOT FOUND]'
        return InlineImage(tpl, file_info['fullpath'], Inches(2))
    return docassemble.base.filter.docx_template_filter(text)

def create_hyperlink(url, anchor_text, tpl):
    return InlineHyperlink(tpl, url, anchor_text)

class InlineHyperlink(object):
    def __init__(self, tpl, url, anchor_text):
        self.tpl = tpl
        self.url = url
        self.anchor_text = anchor_text
    def _insert_link(self):
        ref = self.tpl.docx._part.relate_to(self.url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
        return '</w:t></w:r><w:hyperlink r:id="%s"><w:r><w:rPr><w:rStyle w:val="InternetLink"/></w:rPr><w:t>%s</w:t></w:r></w:hyperlink><w:r><w:rPr></w:rPr><w:t xml:space="preserve">' % (ref, html_escape(self.anchor_text))
    def __unicode__(self):
        return self._insert_link()
    def __str__(self):
        return self._insert_link()

def include_docx_template(template_file, **kwargs):
    """Include the contents of one docx file inside another docx file."""
    if this_thread.evaluation_context is None:
        return 'ERROR: not in a docx file'
    if template_file.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DALocalFile'):
        template_path = template_file.path()
    else:
        template_path = package_template_filename(template_file, package=this_thread.current_package)
    sd = this_thread.misc['docx_template'].new_subdoc()
    sd.subdocx = Document(template_path)
    sd.subdocx._part = sd.docx._part
    first_paragraph = sd.subdocx.paragraphs[0]
    for key, val in kwargs.iteritems():
        if hasattr(val, 'instanceName'):
            the_repr = val.instanceName
        else:
            the_repr = '"' + re.sub(r'\n', '', unicode(val).encode('utf-8').encode('base64')) + '".decode("base64").decode("utf-8")'
        first_paragraph.insert_paragraph_before(str("{%%p set %s = %s %%}" % (key, the_repr)))
    if 'docx_include_count' not in this_thread.misc:
        this_thread.misc['docx_include_count'] = 0
    this_thread.misc['docx_include_count'] += 1
    return sd

def add_to_rt(tpl, rt, parsed):
    list_tab = False
    block_tab = False
    while (len(list(parsed)) > 0):
        html_names =    {
            'em': False,
            'code': False,
            'strong': False,
            'h1': False,
            'h2': False,
            'h3': False,
            'h4': False,
            'u': False,
            'a': False,
            'strike': False,
            'ol': False,
            'ul': False,
            'li': False,
            'blockquote': False
        }
        href = ''
        html_out = parsed.popleft()
        for parent in html_out.parents:
            for html_key, html_value in html_names.items():
                if (parent.name ==  html_key):
                    html_names[html_key] = True
                    if (html_key == 'a'):
                        href = parent.get('href')
        rtf_pretext = ''
        if (html_names['code']):
            html_names['em'] = True
        if (html_names['ol'] or html_names['ul']):
            if (html_out == '\n'):
                list_tab = True
            elif (list_tab == True):
                rt.add('\t- ')
                list_tab = False
        else:
            list_tab = False
        if (html_names['blockquote']):
            if (html_out == '\n'):
                block_tab = True
            elif (block_tab == True):
                rt.add('\t')
                block_tab = False
        else:
            block_tab = False
        if (html_names['a']):
            rt.add(rtf_pretext + html_out, italic=html_names['em'],
                bold=html_names['strong'], underline=True, strike=html_names['strike'],
                url_id=tpl.build_url_id(href))
        elif (html_names['h1']):
            if (html_names['a']):
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=True, strike=html_names['strike'],
                    url_id=tpl.build_url_id(href), size=60)
            else:
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=html_names['u'], strike=html_names['strike'], size=60)
        elif (html_names['h2']):
            if (html_names['a']):
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=True, strike=html_names['strike'],
                    url_id=tpl.build_url_id(href), size=40)
            else:
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=html_names['u'], strike=html_names['strike'], size=40)
        elif (html_names['h3']):
            if (html_names['a']):
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=True, strike=html_names['strike'],
                    url_id=tpl.build_url_id(href), size=30)
            else:
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=html_names['u'], strike=html_names['strike'], size=30)
        elif (html_names['h4']):
            if (html_names['a']):
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=True, strike=html_names['strike'],
                    url_id=tpl.build_url_id(href), size=20)
            else:
                rt.add(rtf_pretext + html_out, italic=html_names['em'],
                    bold=True, underline=html_names['u'], strike=html_names['strike'], size=20)
        else:
            rt.add(rtf_pretext + html_out, italic=html_names['em'],
                bold=html_names['strong'], underline=html_names['u'], strike=html_names['strike'])
    return rt

def get_children(descendants, parsed):
    subelement = False
    descendants_buff = deque()
    if descendants is None:
        return descendants_buff
    if (isinstance(descendants, NavigableString)):
        parsed.append(descendants)
    else:
        for child in descendants.children:
            if (child.name == None):
                if (subelement == False):
                    parsed.append(child)
                else:
                    descendants_buff.append(child)
            else:
                if (subelement == False):
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
    while (len(list(descendants)) > 0):
        child = descendants.popleft()
        from_children = get_children(child, parsed)
        descendants.extendleft(from_children)
    return parsed

def markdown_to_docx(text, tpl):
    source_code = docassemble.base.filter.markdown_to_html(text, do_terms=False)
    source_code = re.sub(r'(?<!\>)\n', ' ', source_code)
    #source_code = re.sub("\n", ' ', source_code)
    #source_code = re.sub(">\s+<", '><', source_code)
    rt = RichText('')
    soup = BeautifulSoup(source_code, 'lxml')
    html_parsed = deque()
    html_parsed = html_linear_parse(soup)
    rt = add_to_rt(tpl, rt, html_parsed)
    return rt
