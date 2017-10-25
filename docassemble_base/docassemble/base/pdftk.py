import os
import os.path
import subprocess
import mimetypes
import docassemble.base.filter
import tempfile
import shutil
import fdfgen
import yaml
import re
import PyPDF2 as pypdf
from PIL import Image
from docassemble.base.error import DAError
from docassemble.base.pdfa import pdf_to_pdfa
from subprocess import call, check_output
from docassemble.base.logger import logmessage
from docassemble.base.functions import word
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.pdfpage import PDFPage

PDFTK_PATH = 'pdftk'

def set_pdftk_path(path):
    global PDFTK_PATH
    PDFTK_PATH = path

def read_fields(pdffile):
    import string
    printable = set(string.printable)
    outfields = list()
    fp = open(pdffile, 'rb')
    id_to_page = dict()
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    pageno = 1;
    for page in PDFPage.create_pages(doc):
        id_to_page[page.pageid] = pageno
        pageno += 1
    if 'AcroForm' not in doc.catalog:
        return None
    fields = resolve1(doc.catalog['AcroForm'])['Fields']
    recursively_add_fields(fields, id_to_page, outfields)
    return sorted(outfields, key=fieldsorter)

def fieldsorter(x):
    if x[3] and type(x[3]) is list:
        x_coord = x[3][0]
        y_coord = -1 * x[3][1]
    else:
        x_coord = 0
        y_coord = 0
    return (x[2], y_coord, x_coord)

def recursively_add_fields(fields, id_to_page, outfields):
    for i in fields:
        field = resolve1(i)
        name, value, rect, page, field_type = field.get('T'), field.get('V'), field.get('Rect'), field.get('P'), field.get('FT')
        if name is not None:
            name = str(name).decode('latin1')
        if value is not None:
            value = str(value).decode('latin1')
        #logmessage("name is " + str(name) + " and FT is |" + str(field_type) + "| and value is " + str(value))
        if page is not None:
            pageno = id_to_page[page.objid]
        else:
            pageno = 1
        if str(field_type) == '/Btn':
            if value == '/Yes':
                default = "Yes"
            else:
                default = "No"
        elif str(field_type) == '/Sig':
            default = '${ user.signature }'
        else:
            if value is not None:
                #for val in value:
                #    logmessage("Got a " + str(ord(val)))
                #logmessage(repr(value.decode('utf8')))
                #default = re.sub(r'^\xc3\xbe\xc3\xbf', '', value)
                #default = re.sub(r'^þÿ', '', value)
                default = value
                if not default:
                    default = word("something")
            else:
                default = word("something")
        kids = field.get('Kids')
        if kids:
            recursively_add_fields(kids, id_to_page, outfields)
        else:
            outfields.append((name, default, pageno, rect, field_type))

def read_fields_pdftk(pdffile):
    output = unicode(check_output([PDFTK_PATH, pdffile, 'dump_data_fields']).decode('utf8'))
    fields = list()
    if not len(output) > 0:
        return None
    for field in yaml.load_all(output):
        if 'FieldType' in field and field['FieldType'] == 'Button':
            default = "No"
        else:
            default = word("something")
        if 'FieldName' in field:
            fields.append((field['FieldName'], default))
    return fields
    
def fill_template(template, data_strings=[], data_names=[], hidden=[], readonly=[], images=[], pdf_url=None, editable=True, pdfa=False):
    if pdf_url is None:
        pdf_url = ''
    fdf = fdfgen.forge_fdf(pdf_url, data_strings, data_names, hidden, readonly)
    fdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".fdf", delete=False)
    fdf_file.write(fdf)
    fdf_file.close()
    pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    subprocess_arguments = [PDFTK_PATH, template, 'fill_form', fdf_file.name, 'output', pdf_file.name]
    logmessage("Arguments are " + str(subprocess_arguments))
    if not editable:
        subprocess_arguments.append('flatten')
    result = call(subprocess_arguments)
    if result != 0:
        logmessage("Failed to fill PDF form " + str(template))
        raise DAError("Call to pdftk failed for template " + str(template) + " where arguments were " + " ".join(subprocess_arguments))
    if len(images):
        fields = dict()
        for field, default, pageno, rect, field_type in read_fields(template):
            if str(field_type) == '/Sig':
                fields[field] = {'pageno': pageno, 'rect': rect}
        for field, file_info in images:
            if field not in fields:
                logmessage("field name " + str(field) + " not found in PDF file")
                continue
            logmessage("Need to put image on page " + str(fields[field]['pageno']))
            temp_png = tempfile.NamedTemporaryFile(mode="wb", suffix=".png")
            args = ["convert", file_info['fullpath'], "-trim", "+repage", temp_png.name]
            result = call(args)
            if result == 1:
                logmessage("failed to trim file: " + " ".join(args))
                continue
            im = Image.open(temp_png.name)
            width, height = im.size
            xone, yone, xtwo, ytwo = fields[field]['rect']
            dppx = width/(xtwo-xone)
            dppy = height/(ytwo-yone)
            if (dppx > dppy):
                dpp = dppx
            else:
                dpp = dppy
            extent_x, extent_y = xone*dpp+width, yone*dpp+height
            overlay_pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf")
            args = ["convert", temp_png.name, "-background", "none", "-density", str(int(dpp*72)), "-gravity", "NorthEast", "-extent", str(int(extent_x)) + 'x' + str(int(extent_y)), overlay_pdf_file.name]
            result = call(args)
            if result == 1:
                logmessage("failed to make overlay: " + " ".join(args))
                continue
            new_pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf")
            with open(pdf_file.name, "rb") as inFile, open(overlay_pdf_file.name, "rb") as overlay:
                original = pypdf.PdfFileReader(inFile)
                background = original.getPage(fields[field]['pageno']-1)
                foreground = pypdf.PdfFileReader(overlay).getPage(0)
                background.mergePage(foreground)
                writer = pypdf.PdfFileWriter()
                for i in range(original.getNumPages()):
                    page = original.getPage(i)
                    writer.addPage(page)
                with open(new_pdf_file.name, "wb") as outFile:
                    writer.write(outFile)
            shutil.copyfile(new_pdf_file.name, pdf_file.name)
    if pdfa:
        pdf_to_pdfa(pdf_file.name)
    return pdf_file.name

def concatenate_files(path_list, pdfa=False):
    pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    subprocess_arguments = [PDFTK_PATH]
    new_path_list = list()
    for path in path_list:
        mimetype, encoding = mimetypes.guess_type(path)
        if mimetype.startswith('image'):
            new_pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            args = ["convert", path, new_pdf_file.name]
            result = call(args)
            if result != 0:
                logmessage("failed to convert image to PDF: " + " ".join(args))
                continue
            new_path_list.append(new_pdf_file.name)
        elif mimetype in ('application/rtf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'application/vnd.oasis.opendocument.text'):
            new_pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            if mimetype == 'application/rtf':
                ext = 'rtf'
            elif mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                ext = 'docx'
            elif mimetype == 'application/msword':
                ext = 'doc'
            elif mimetype == 'application/vnd.oasis.opendocument.text':
                ext = 'odt'
            docassemble.base.pandoc.word_to_pdf(path, ext, new_pdf_file.name, pdfa=False)
            new_path_list.append(new_pdf_file.name)
        elif mimetype == 'application/pdf':
            new_path_list.append(path)
    if len(new_path_list) == 0:
        raise DAError("concatenate_files: no valid files to concatenate")
    subprocess_arguments.extend(new_path_list)
    subprocess_arguments.extend(['cat', 'output', pdf_file.name])
    logmessage("Arguments are " + str(subprocess_arguments))
    result = call(subprocess_arguments)
    if result != 0:
        logmessage("Failed to concatenate PDF files")
        raise DAError("Call to pdftk failed for concatenation where arguments were " + " ".join(subprocess_arguments))
    if pdfa:
        pdf_to_pdfa(pdf_file.name)
    return pdf_file.name
