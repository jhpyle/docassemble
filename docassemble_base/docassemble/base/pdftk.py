import os
import os.path
import subprocess
import docassemble.base.filter
import tempfile
import shutil
import fdfgen
import yaml
import PyPDF2 as pypdf
from PIL import Image
from docassemble.base.error import DAError
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
    for i in fields:
        field = resolve1(i)
        name, value, rect, page, field_type = field.get('T'), field.get('V'), field.get('Rect'), field.get('P'), field.get('FT')
        #logmessage("name is " + str(name) + " and FT is |" + str(field_type) + "|")
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
                default = value
            else:
                default = word("something")
        outfields.append((name, default, pageno, rect, field_type))
    return outfields

def read_fields_pdftk(pdffile):
    output = check_output([PDFTK_PATH, pdffile, 'dump_data_fields'])
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
    
def fill_template(template, data_strings=[], data_names=[], hidden=[], readonly=[], images=[], pdf_url=None, editable=True):
    if pdf_url is None:
        pdf_url = ''
    fdf = fdfgen.forge_fdf(pdf_url, data_strings, data_names, hidden, readonly)
    fdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".fdf", delete=False)
    fdf_file.write(fdf)
    fdf_file.close()
    pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False)
    subprocess_arguments = [PDFTK_PATH, template, 'fill_form', fdf_file.name, 'output', pdf_file.name]
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
    return pdf_file.name
