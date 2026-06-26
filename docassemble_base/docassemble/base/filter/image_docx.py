import re
from docxtpl import InlineImage
from docx.shared import Mm, Inches, Pt, Cm, Twips
from docassemble.base.hooks import file_finder
from docassemble.base.filter.utils import convert_svg_to_png


def fix_double_quote(the_string):
    return '"' + re.sub('"', '&quot;', the_string) + '"'


class CustomInlineImage(InlineImage):
    alt_text = None

    def __init__(self, tpl, image_descriptor, width=None, height=None, anchor=None, alt_text=None):
        super().__init__(tpl, image_descriptor, width=width, height=height, anchor=anchor)
        self.alt_text = alt_text

    def _insert_image(self):
        output = super()._insert_image()
        if self.alt_text:
            return re.sub('<wp:docPr ', f'<wp:docPr descr={fix_double_quote(self.alt_text)} ', output)
        return output


def image_for_docx(fileref, question, tpl, width=None, alt_text=None):
    if fileref.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DALocalFile', 'DAStaticFile'):
        file_info = {'fullpath': fileref.path()}
    else:
        file_info = file_finder(fileref, question=question)
    if 'path' in file_info and 'extension' in file_info:
        convert_svg_to_png(file_info)
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
    return CustomInlineImage(tpl, file_info['fullpath'], width=the_width, alt_text=alt_text)
