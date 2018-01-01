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
import pypdftk
import string
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
    
def fill_template(template, data_strings=[], data_names=[], hidden=[], readonly=[], images=[], pdf_url=None, editable=True, pdfa=False, password=None):
    if pdf_url is None:
        pdf_url = ''
    fdf = fdfgen.forge_fdf(pdf_url, data_strings, data_names, hidden, readonly)
    fdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".fdf", delete=False)
    fdf_file.write(fdf)
    fdf_file.close()
    if False:
        fdf_dict = dict()
        for key, val in data_strings:
            fdf_dict[key] = val
        xfdf_temp_filename = pypdftk.gen_xfdf(fdf_dict)
        xfdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=\
".xfdf", delete=False)
        shutil.copyfile(xfdf_temp_filename, xfdf_file.name)
    pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    subprocess_arguments = [PDFTK_PATH, template, 'fill_form', fdf_file.name, 'output', pdf_file.name]
    #logmessage("Arguments are " + str(subprocess_arguments))
    if editable:
        subprocess_arguments.append('need_appearances')
    else:
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
            #logmessage("Need to put image on page " + str(fields[field]['pageno']))
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
    if editable:
        replicate_js_and_calculations(template, pdf_file.name, password)
    elif password:
        pdf_encrypt(pdf_file.name, password)
    return pdf_file.name

def concatenate_files(path_list, pdfa=False, password=None):
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
    #logmessage("Arguments are " + str(subprocess_arguments))
    result = call(subprocess_arguments)
    if result != 0:
        logmessage("Failed to concatenate PDF files")
        raise DAError("Call to pdftk failed for concatenation where arguments were " + " ".join(subprocess_arguments))
    if pdfa:
        pdf_to_pdfa(pdf_file.name)
    replicate_js_and_calculations(new_path_list[0], pdf_file.name, password)
    return pdf_file.name

def get_passwords(password):
    if password is None:
        return (None, None)
    if type(password) in (str, unicode, bool, int, float):
        owner_password = unicode(password).strip()
        user_password = unicode(password).strip()
    elif type(password) is list:
        owner_password = unicode(password[0]).strip()
        user_password = unicode(password[1]).strip()
    elif type(password) is dict:
        owner_password = unicode(password.get('owner', 'password')).strip()
        user_password = unicode(password.get('user', 'password')).strip()
    else:
        raise DAError("get_passwords: invalid password")
    return (owner_password, user_password)

def pdf_encrypt(filename, password):
    #logmessage("pdf_encrypt: running; password is " + repr(password))
    (owner_password, user_password) = get_passwords(password)
    outfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    if owner_password == user_password:
        commands = ['pdftk', filename, 'output', outfile.name, 'user_pw', user_password, 'allow', 'printing']
    else:
        commands = ['pdftk', filename, 'output', outfile.name, 'owner_pw', owner_password, 'user_pw', user_password, 'allow', 'printing']
    try:
        output = subprocess.check_output(commands, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        output = err.output
        raise DAError("pdf_encrypt: error running pdftk.  " + output)
    #logmessage(' '.join(commands))
    #logmessage(output)
    shutil.move(outfile.name, filename)

class DAPdfFileWriter(pypdf.PdfFileWriter):
    def DAGetFields(self, tree=None, results=None):
        if results is None:
            results = dict()
        if tree is None:
            tree = self._root_object['/AcroForm']
        if isinstance(tree, pypdf.generic.IndirectObject):
            the_tree = tree.getObject()
        else:
            the_tree = tree
        self.DABuildField(tree, results=results)
        if "/Fields" in the_tree:
            fields = the_tree["/Fields"]
            for f in fields:
                self.DABuildField(f, results)
        return results

    def DABuildField(self, f, results):
        if isinstance(f, pypdf.generic.IndirectObject):
            field = f.getObject()
        else:
            field = f
        self.DACheckKids(field, results=results)
        try:
            key = field["/TM"]
        except KeyError:
            try:
                key = field["/T"]
            except KeyError:
                return
        results[key] = f

    def DACheckKids(self, tree, results):
        if "/Kids" in tree:
            for kid in tree["/Kids"]:
                self.DAGetFields(tree=kid, results=results)

def remove_nonprintable(text):
    final = ''
    for char in text:
        if char in string.printable:
            final += char
    return final

def replicate_js_and_calculations(template_filename, original_filename, password):
    #logmessage("replicate_js_and_calculations where template_filename is " + template_filename + " and original_filename is " + original_filename + " and password is " + repr(password))
    template = pypdf.PdfFileReader(open(template_filename, 'rb'))
    co_field_names = list()
    if '/AcroForm' in template.trailer['/Root']:
        #logmessage("Found AcroForm")
        acroform = template.trailer['/Root']['/AcroForm'].getObject()
        if '/CO' in acroform:
            #logmessage("Found CO in AcroForm")
            for f in acroform['/CO']:
                field = f.getObject()
                if '/TM' in field:
                    name = field['/TM']
                elif '/T' in field:
                    name = field['/T']
                else:
                    continue
                #logmessage("Found CO name " + str(name))
                co_field_names.append(name)

    js_to_write = list()
    if '/Names' in template.trailer['/Root'] and '/JavaScript' in template.trailer['/Root']['/Names']:
        #logmessage("Found name in root and javascript in names")
        js_names = template.trailer['/Root']['/Names']['/JavaScript'].getObject()
        if '/Names' in js_names:
            #logmessage("Found names in javascript")
            js_list = js_names['/Names']
            while len(js_list):
                name = js_list.pop(0)
                obj = js_list.pop(0)
                js_obj = obj.getObject()
                if '/S' in js_obj and js_obj['/S'] == '/JavaScript' and '/JS' in js_obj:
                    if isinstance(js_obj['/JS'], pypdf.generic.ByteStringObject) or isinstance(js_obj['/JS'], pypdf.generic.TextStringObject):
                        js_to_write.append((name, remove_nonprintable(js_obj['/JS'])))
                    elif isinstance(js_obj['/JS'], pypdf.generic.EncodedStreamObject) or isinstance(js_obj['/JS'], pypdf.generic.DecodedStreamObject):
                        js_to_write.append((name, remove_nonprintable(js_obj['/JS'].getData())))

    if len(js_to_write) == 0 and len(co_field_names) == 0:
        #logmessage("Nothing to do here")
        if password:
            pdf_encrypt(original_filename, password)
        return
    original = pypdf.PdfFileReader(open(original_filename, 'rb'))
    #logmessage("Opening " + original_filename)
    writer = DAPdfFileWriter()
    writer.cloneReaderDocumentRoot(original)
    if len(co_field_names) > 0:
        #logmessage("Cloning CO")
        fields = writer.DAGetFields()
        co = []
        for field_name in co_field_names:
            if field_name in fields:
                co.append(fields[field_name])
        #writer._root_object['/AcroForm'][pypdf.generic.NameObject("/CO")] = pypdf.generic.ArrayObject(co)
        writer._root_object['/AcroForm'].update({
            pypdf.generic.NameObject("/CO"): pypdf.generic.ArrayObject(co)
        })
    if len(js_to_write) > 0:
        #logmessage("Cloning JS")
        name_array = []
        for js_string_name, js_text in js_to_write:
            js_object = pypdf.generic.DecodedStreamObject()
            js_object.setData(js_text)
            js = pypdf.generic.DictionaryObject()
            js.update({
                pypdf.generic.NameObject("/Type"): pypdf.generic.NameObject("/Action"),
                pypdf.generic.NameObject("/S"): pypdf.generic.NameObject("/JavaScript"),
                pypdf.generic.NameObject("/JS"): js_object
            })
            js_indirect_object = writer._addObject(js)
            name_array.append(pypdf.generic.createStringObject(js_string_name))
            name_array.append(js_indirect_object)

        js_name_tree = pypdf.generic.DictionaryObject()
        js_name_tree.update({
            pypdf.generic.NameObject("/JavaScript"): pypdf.generic.DictionaryObject({
                pypdf.generic.NameObject("/Names"): pypdf.generic.ArrayObject(name_array)
            })
        })
        writer._addObject(js_name_tree)
        writer._root_object.update({
            pypdf.generic.NameObject("/Names"): js_name_tree
        })
    if password is not None:
        (owner_password, user_password) = get_passwords(password)
        if owner_password == user_password:
            #logmessage("Password for encryption is " + str(user_password))
            writer.encrypt(str(user_password))
        else:
            #logmessage("Passwords for encryption are " + str(user_password) + " and " + str(owner_password))
            writer.encrypt(str(user_password), owner_pwd=str(owner_password))
    outfile = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    writer.write(outfile)
    outfile.flush()
    shutil.move(outfile.name, original_filename)
