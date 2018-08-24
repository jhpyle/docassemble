import re
from docxtpl import DocxTemplate, R, InlineImage, RichText, Listing, Document, Subdoc
from docx.shared import Mm, Inches, Pt
import docx.opc.constants
from docassemble.base.functions import server, this_thread, package_template_filename
import docassemble.base.filter
from xml.sax.saxutils import escape as html_escape
from types import NoneType
from docassemble.base.logger import logmessage
from bs4 import BeautifulSoup

def image_for_docx(number, question, tpl, width=None):
    file_info = server.file_finder(number, convert={'svg': 'png'}, question=question)
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
    if template_file.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection'):
        template_path = template_file.path()
    else:
        template_path = package_template_filename(template_file, package=this_thread.current_package)
    sd = this_thread.docx_template.new_subdoc()
    sd.subdocx = Document(template_path)
    sd.subdocx._part = sd.docx._part
    first_paragraph = sd.subdocx.paragraphs[0]
    for key, val in kwargs.iteritems():
        if hasattr(val, 'instanceName') and val.__class__.__name__.startswith('DA'):
            the_repr = val.instanceName
        else:
            the_repr = '"' + re.sub(r'\n', '', unicode(val).encode('utf-8').encode('base64')) + '".decode("base64").decode("utf-8")'
        first_paragraph.insert_paragraph_before(str("{%%p set %s = %s %%}" % (key, the_repr)))
    this_thread.docx_include_count += 1
    return sd

html_names =    {
    'p': None,
    'em': True,
    'strong': True,
    'u': True,
    'strike': True,
    'a': True,
    'code': True,
    'h1': 60,
    'h2': 40,
    'h3': 40,
    'h4': 20,
    'br': None,
    'ol': None,
    'ul': None,
    'li': None
}

def markdown_to_docx(text, tpl):
    # Credits: epompeii
    rt = RichText('')
    soup = BeautifulSoup('<html>' + docassemble.base.filter.markdown_to_html(text, do_terms=False) + '</html>', 'lxml')
    html_tag = soup.find("html")
    for html_element in html_tag.next_elements:
        if (html_element.name):
            for html_key, html_value in html_names.items():
                if(html_element.name == html_key):
                    if(html_element.name == 'p'):
                        rt.add('\a' + html_element.text + ' ')
                    elif(html_element.name == 'em'):
                        rt.add(html_element.text, italic=html_value)
                        rt.add(' ')
                    elif(html_element.name == 'strong'):
                        rt.add(html_element.text, bold=html_value)
                        rt.add(' ')
                    elif(html_element.name == 'u'):
                        rt.add(html_element.text, underline=html_value)
                        rt.add(' ')
                    elif(html_element.name == 'strike'):
                        rt.add(html_element.text, strike=html_value)
                        rt.add(' ')
                    elif(html_element.name == 'a'):
                        rt.add(html_element.text,
                               url_id=tpl.build_url_id(html_element['href']), underline=html_value)
                        rt.add(' ')
                    elif(html_element.name == 'code'):
                        rt.add(html_element.text, italic=html_value)
                        rt.add(' ')
                    elif(html_element.name == 'h1' or html_element.name == 'h2'
                        or html_element.name == 'h3' or html_element.name == 'h4'):
                        rt.add('\n')
                        rt.add(html_element.text, size=html_value)
                        rt.add('\n')
                    elif(html_key == 'br' or html_key == 'ol' or html_key == 'ul'):
                        rt.add('\n')
                    elif(html_key == 'li'):
                        rt.add('-' + html_element.text + '\n')
    logmessage(unicode(rt))
    return rt
