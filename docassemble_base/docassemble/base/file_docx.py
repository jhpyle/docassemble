import os
import time
import stat
import mimetypes
import tempfile
import shutil
import zipfile
from collections import deque
from xml.sax.saxutils import escape as html_escape
import docx.opc.constants
import docx
from docxcompose.composer import Composer  # For fixing up images, etc when including docx files within templates
from bs4 import NavigableString
from pikepdf import Pdf
from .error import DAError
from .filter.image_docx import image_for_docx
from .filter.utils import sanitize_xml
from .functions import DALocalFile
from .hooks import fg_make_pdf_for_word_path, fg_make_png_for_pdf_path
from .pandoc import convert_file
from .thread_context import this_thread

QPDF_PATH = 'qpdf'
NoneType = type(None)

DEFAULT_PAGE_WIDTH = '6.5in'


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


def pdf_pages(file_info, width):
    output = ''
    if width is None:
        width = DEFAULT_PAGE_WIDTH
    if not os.path.isfile(file_info['path'] + '.pdf'):
        if file_info['extension'] in ('rtf', 'doc', 'odt') and not os.path.isfile(file_info['path'] + '.pdf'):
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
            output += str(image_for_docx(DALocalFile(page_file['fullpath']), this_thread.current_question, this_thread.misc.get('docx_template', None), width=width))
        else:
            output += "[Error including page image]"
        output += ' '
    return output


def concatenate_files(path_list):
    new_path_list = []
    for path in path_list:
        mimetype, encoding = mimetypes.guess_type(path)  # pylint: disable=unused-variable
        if mimetype in ('application/rtf', 'application/msword', 'application/vnd.oasis.opendocument.text'):
            new_docx_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
            if mimetype == 'application/rtf':
                ext = 'rtf'
            elif mimetype == 'application/msword':
                ext = 'doc'
            else:
                ext = 'odt'
            convert_file(path, new_docx_file.name, ext, 'docx')
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


def fix_docx(path):
    seen = set()
    problem_present = False
    with tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx") as new_docx_file:
        with zipfile.ZipFile(path, mode='r') as doc:
            with zipfile.ZipFile(new_docx_file.name, compression=zipfile.ZIP_DEFLATED, mode='w') as zf:
                for item in doc.infolist():
                    if item.filename in seen:
                        problem_present = True
                        continue
                    seen.add(item.filename)
                    zf.writestr(item, doc.read(item))
        if problem_present:
            shutil.copyfile(new_docx_file.name, path)
