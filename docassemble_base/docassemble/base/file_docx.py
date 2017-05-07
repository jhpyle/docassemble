import re
from docxtpl import DocxTemplate, R, InlineImage, RichText, Listing
from docx.shared import Mm, Inches, Pt
from docassemble.base.functions import server
import docassemble.base.filter
from types import NoneType

def transform_for_docx(text, question, tpl):
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
