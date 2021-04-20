import os
import os.path
import subprocess
import mimetypes
import tempfile
import shutil
#import fdfgen
from xfdfgen import Xfdf
import yaml
import re
import PyPDF2 as pypdf
import pypdftk
import string
import codecs
from PIL import Image
from docassemble.base.error import DAError
from docassemble.base.pdfa import pdf_to_pdfa
from docassemble.base.logger import logmessage
from docassemble.base.functions import word
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1, PDFObjRef
from pdfminer.pdfpage import PDFPage
import logging
logging.getLogger('pdfminer').setLevel(logging.ERROR)
import uuid
from docassemble.base.config import daconfig

PDFTK_PATH = 'pdftk'
QPDF_PATH = 'qpdf'

def set_pdftk_path(path):
    global PDFTK_PATH
    PDFTK_PATH = path

def set_qpdf_path(path):
    global QPDF_PATH
    QPDF_PATH = path

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

def recursively_add_fields(fields, id_to_page, outfields, prefix=''):
    if isinstance(fields, PDFObjRef):
        fields = resolve1(fields)
    for i in fields:
        field = resolve1(i)
        try:
            name, value, rect, page, field_type = field.get('T'), field.get('V'), field.get('Rect'), field.get('P'), field.get('FT')
        except:
            logmessage("Skipping field " + repr(field))
            continue
        if name is not None:
            if not isinstance(name, bytes):
                name = bytes(str(name), encoding='utf-8')
            name = remove_nonprintable_bytes_limited(name)
        if value is not None:
            if not isinstance(value, bytes):
                value = bytes(str(value), encoding='utf-8')
            value = remove_nonprintable_bytes_limited(value)
        #logmessage("name is " + repr(name) + " and FT is |" + repr(str(field_type)) + "| and value is " + repr(value))
        if page is not None and hasattr(page, 'objid'):
            try:
                pageno = id_to_page[page.objid]
            except:
                pageno = 1
        else:
            pageno = 1
        export_value = None
        if str(field_type) in ('/Btn', "/'Btn'"):
            export_value = 'Yes'
            try:
                for key in list(field['AP']['N'].keys()):
                    if key in ('Off', 'off', 'No', 'no'):
                        continue
                    export_value = key
                    break
            except:
                pass
            if value == '/Yes':
                default = export_value
            else:
                default = "No"
        elif str(field_type) in ('/Sig', "/'Sig'"):
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
            if name is None:
                recursively_add_fields(kids, id_to_page, outfields, prefix=prefix)
            else:
                if prefix == '':
                    recursively_add_fields(kids, id_to_page, outfields, prefix=name)
                else:
                    recursively_add_fields(kids, id_to_page, outfields, prefix=prefix + '.' + name)
        else:
            if prefix != '' and name is not None:
                outfields.append((prefix + '.' + name, default, pageno, rect, field_type, export_value))
            elif prefix == '':
                outfields.append((name, default, pageno, rect, field_type, export_value))
            else:
                outfields.append((prefix, default, pageno, rect, field_type, export_value))

def read_fields_pdftk(pdffile):
    output = subprocess.check_output([PDFTK_PATH, pdffile, 'dump_data_fields']).decode()
    fields = list()
    if not len(output) > 0:
        return None
    for field in yaml.load_all(output, Loader=yaml.FullLoader):
        if 'FieldType' in field and field['FieldType'] == 'Button':
            default = "No"
        else:
            default = word("something")
        if 'FieldName' in field:
            fields.append((field['FieldName'], default))
    return fields

pdf_parts = ['/AcroForm', '/Metadata', '/OCProperties', '/StructTreeRoot', '/OpenAction', '/AA', '/MarkInfo', '/Lang']

def recursive_get_pages(indirect_obj, result):
    obj = indirect_obj.getObject()
    if '/Type' in obj and obj['/Type'] == '/Page':
        result.append(indirect_obj)
    if '/Kids' in obj:
        for kid in obj['/Kids']:
            recursive_get_pages(kid, result)

def get_page_hash(obj):
    page_list = list()
    recursive_get_pages(obj['/Root']['/Pages'], page_list)
    result = dict()
    indexno = 1
    for item in page_list:
        result[item.idnum] = indexno
        indexno += 1
    return result

def recursive_add_bookmark(reader, writer, outlines, parent=None):
    #logmessage("recursive_add_bookmark")
    cur_bm = None
    for destination in outlines:
        if type(destination) is list:
            #logmessage("Going into subbookmark")
            recursive_add_bookmark(reader, writer, destination, parent=cur_bm)
        else:
            #logmessage("page is " + str(destination.page))
            if isinstance(destination.page, pypdf.generic.NullObject):
                #logmessage("continue 1")
                continue
            if not isinstance(destination.page, pypdf.generic.IndirectObject):
                #logmessage("continue 2")
                continue
            if destination.page.idnum not in reader.idnum_to_page:
                #logmessage("continue 3")
                continue
            if reader.idnum_to_page[destination.page.idnum] > len(writer.page_list):
                #logmessage("continue 4")
                continue
            destination_page = writer.page_list[reader.idnum_to_page[destination.page.idnum] - 1]
            if destination.typ in ('/FitH', '/FitBH'):
                cur_bm = writer.addBookmark(destination.title, destination_page, parent, None, False, False, destination.typ, destination.top)
            elif destination.typ in ('/FitV', '/FitBV'):
                cur_bm = writer.addBookmark(destination.title, destination_page, parent, None, False, False, destination.typ, destination.left)
            elif destination.typ == '/FitR':
                cur_bm = writer.addBookmark(destination.title, destination_page, parent, None, False, False, destination.typ, destination.left, destination.bottom, destination.right, destination.top)
            elif destination.typ == '/XYZ':
                cur_bm = writer.addBookmark(destination.title, destination_page, parent, None, False, False, destination.typ, destination.left, destination.top, destination.zoom)
            else:
                cur_bm = writer.addBookmark(destination.title, destination_page, parent, None, False, False, destination.typ)
            #logmessage("Added bookmark " + destination.title)

def fill_template(template, data_strings=[], data_names=[], hidden=[], readonly=[], images=[], pdf_url=None, editable=True, pdfa=False, password=None, template_password=None, default_export_value=None):
    if pdf_url is None:
        pdf_url = 'file.pdf'
    if not pdf_url.endswith('.pdf'):
        pdf_url += '.pdf'
    the_fields = read_fields(template)
    export_values = dict()
    for field, default, pageno, rect, field_type, export_value in the_fields:
        field_type = re.sub(r'[^/A-Za-z]', '', str(field_type))
        if field_type in ('/Btn', "/'Btn'"):
            export_values[field] = export_value or default_export_value or 'Yes'
    if len(export_values):
        new_data_strings = list()
        for key, val in data_strings:
            if key in export_values:
                if str(val) in ('Yes', 'yes', 'True', 'true', 'On', 'on', export_values[key]):
                    val = export_values[key]
                else:
                    if export_values[key] == 'On':
                        val = 'Off'
                    elif export_values[key] == 'on':
                        val = 'off'
                    elif export_values[key] == 'yes':
                        val = 'no'
                    else:
                        val = 'No'
            new_data_strings.append((key, val))
        data_strings = new_data_strings
    data_dict = {}
    for key, val in data_strings:
        data_dict[key] = val
    fdf = Xfdf(pdf_url, data_dict)
    #fdf = fdfgen.forge_fdf(pdf_url, data_strings, data_names, hidden, readonly)
    fdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".xfdf", delete=False)
    #fdf_file.write(fdf)
    fdf_file.close()
    fdf.write_xfdf(fdf_file.name)
    if False:
        fdf_dict = dict()
        for key, val in data_strings:
            fdf_dict[key] = val
        xfdf_temp_filename = pypdftk.gen_xfdf(fdf_dict)
        xfdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=\
".xfdf", delete=False)
        shutil.copyfile(xfdf_temp_filename, xfdf_file.name)
    pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    if template_password is not None:
        template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
        qpdf_subprocess_arguments = [QPDF_PATH, '--decrypt', '--password=' + template_password, template, template_file.name]
        try:
            result = subprocess.run(qpdf_subprocess_arguments, timeout=60).returncode
        except subprocess.TimeoutExpired:
            result = 1
            logmessage("fill_template: call to qpdf took too long")
        if result != 0:
            logmessage("Failed to decrypt PDF template " + str(template))
            raise DAError("Call to qpdf failed for template " + str(template) + " where arguments were " + " ".join(qpdf_subprocess_arguments))
        template = template_file.name
    subprocess_arguments = [PDFTK_PATH, template, 'fill_form', fdf_file.name, 'output', pdf_file.name]
    #logmessage("Arguments are " + str(subprocess_arguments))
    if editable or len(images):
        subprocess_arguments.append('need_appearances')
    else:
        subprocess_arguments.append('flatten')
    try:
        result = subprocess.run(subprocess_arguments, timeout=600).returncode
    except subprocess.TimeoutExpired:
        result = 1
        logmessage("fill_template: call to pdftk fill_form took too long")
    if result != 0:
        logmessage("Failed to fill PDF form " + str(template))
        raise DAError("Call to pdftk failed for template " + str(template) + " where arguments were " + " ".join(subprocess_arguments))
    if len(images):
        fields = dict()
        for field, default, pageno, rect, field_type, export_value in the_fields:
            if str(field_type) in ('/Sig', "/'Sig'"):
                fields[field] = {'pageno': pageno, 'rect': rect}
        image_todo = list()
        for field, file_info in images:
            if field not in fields:
                logmessage("field name " + str(field) + " not found in PDF file")
                continue
            #logmessage("Need to put image on page " + str(fields[field]['pageno']))
            temp_png = tempfile.NamedTemporaryFile(mode="wb", suffix=".png")
            args = [daconfig.get('imagemagick', 'convert'), file_info['fullpath'], "-trim", "+repage", "+profile", '*', '-density', '0', temp_png.name]
            try:
                result = subprocess.run(args, timeout=60).returncode
            except subprocess.TimeoutExpired:
                logmessage("fill_template: convert took too long")
                result = 1
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
            overlay_pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            args = [daconfig.get('imagemagick', 'convert'), temp_png.name, "-background", "none", "-density", str(int(dpp*72)), "-gravity", "NorthEast", "-extent", str(int(extent_x)) + 'x' + str(int(extent_y)), overlay_pdf_file.name]
            try:
                result = subprocess.run(args, timeout=60).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("fill_template: call to convert took too long")
            if result == 1:
                logmessage("failed to make overlay: " + " ".join(args))
                continue
            image_todo.append({'overlay_stream': open(overlay_pdf_file.name, "rb"), 'pageno': fields[field]['pageno']})
        if len(image_todo):
            new_pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf")
            with open(pdf_file.name, "rb") as inFile:
                original = pypdf.PdfFileReader(inFile)
                original.idnum_to_page = get_page_hash(original.trailer)
                catalog = original.trailer["/Root"]
                writer = DAPdfFileWriter()
                tree = dict()
                for part in pdf_parts:
                    if part in catalog:
                        tree[part] = catalog[part]
                for i in range(original.getNumPages()):
                    for item in image_todo:
                        if (item['pageno'] - 1) == i:
                            page = original.getPage(i)
                            foreground_file = pypdf.PdfFileReader(item['overlay_stream'])
                            foreground_page = foreground_file.getPage(0)
                            page.mergePage(foreground_page)
                for i in range(original.getNumPages()):
                    newpage = original.getPage(i)
                    writer.addPage(newpage)
                for key, val in tree.items():
                    writer._root_object.update({pypdf.generic.NameObject(key): val})
                writer.page_list = list()
                recursive_get_pages(writer._root_object['/Pages'], writer.page_list)
                recursive_add_bookmark(original, writer, original.getOutlines())
                with open(new_pdf_file.name, "wb") as outFile:
                    writer.write(outFile)
            shutil.copyfile(new_pdf_file.name, pdf_file.name)
            for item in image_todo:
                item['overlay_stream'].close()
    if (not editable) and len(images):
        flatten_pdf(pdf_file.name)
    if pdfa:
        pdf_to_pdfa(pdf_file.name)
    if editable:
        replicate_js_and_calculations(template, pdf_file.name, password)
    elif password:
        pdf_encrypt(pdf_file.name, password)
    return pdf_file.name

def get_passwords(password):
    if password is None:
        return (None, None)
    if type(password) in (str, bool, int, float):
        owner_password = str(password).strip()
        user_password = str(password).strip()
    elif type(password) is list:
        owner_password = str(password[0]).strip()
        user_password = str(password[1]).strip()
    elif type(password) is dict:
        owner_password = str(password.get('owner', 'password')).strip()
        user_password = str(password.get('user', 'password')).strip()
    else:
        raise DAError("get_passwords: invalid password")
    return (owner_password, user_password)

def pdf_encrypt(filename, password):
    #logmessage("pdf_encrypt: running; password is " + repr(password))
    (owner_password, user_password) = get_passwords(password)
    outfile = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
    if owner_password == user_password:
        commands = ['pdftk', filename, 'output', outfile.name, 'user_pw', user_password, 'allow', 'printing']
    else:
        commands = ['pdftk', filename, 'output', outfile.name, 'owner_pw', owner_password, 'user_pw', user_password, 'allow', 'printing']
    try:
        output = subprocess.check_output(commands, stderr=subprocess.STDOUT).decode()
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
            if '/AcroForm' not in self._root_object:
                self._root_object.update({pypdf.generic.NameObject('/AcroForm'): pypdf.generic.DictionaryObject()})
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

    def addBookmark(self, title, page, parent=None, color=None, bold=False, italic=False, fit='/Fit', *args):
        """
        Add a bookmark to this PDF file.

        :param str title: Title to use for this bookmark.
        :param int pagenum: Page number this bookmark will point to.
        :param parent: A reference to a parent bookmark to create nested
            bookmarks.
        :param tuple color: Color of the bookmark as a red, green, blue tuple
            from 0.0 to 1.0
        :param bool bold: Bookmark is bold
        :param bool italic: Bookmark is italic
        :param str fit: The fit of the destination page. See
            :meth:`addLink()<addLink>` for details.
        """
        action = pypdf.generic.DictionaryObject()
        zoomArgs = []
        for a in args:
            if a is not None and a.__class__.__name__ != 'NullObject':
                zoomArgs.append(pypdf.generic.NumberObject(a))
            else:
                zoomArgs.append(pypdf.generic.NullObject())
        dest = pypdf.generic.Destination(pypdf.generic.NameObject("/"+str(uuid.uuid4())), page, pypdf.generic.NameObject(fit), *zoomArgs)
        destArray = dest.getDestArray()
        action.update({
            pypdf.generic.NameObject('/D') : destArray,
            pypdf.generic.NameObject('/S') : pypdf.generic.NameObject('/GoTo')
        })
        actionRef = self._addObject(action)

        outlineRef = self.getOutlineRoot()

        if parent == None:
            parent = outlineRef

        bookmark = pypdf.generic.TreeObject()

        bookmark.update({
            pypdf.generic.NameObject('/A'): actionRef,
            pypdf.generic.NameObject('/Title'): pypdf.generic.createStringObject(title),
        })

        if color is not None:
            bookmark.update({pypdf.generic.NameObject('/C'): pypdf.generic.ArrayObject([pypdf.generic.FloatObject(c) for c in color])})

        format = 0
        if italic:
            format += 1
        if bold:
            format += 2
        if format:
            bookmark.update({pypdf.generic.NameObject('/F'): pypdf.generic.NumberObject(format)})

        bookmarkRef = self._addObject(bookmark)

        parent = parent.getObject()
        parent.addChild(bookmarkRef, self)

        return bookmarkRef

def remove_nonprintable(text):
    final = str()
    for char in text:
        if char in string.printable:
            final += char
    return final

def remove_nonprintable_bytes(byte_list):
    if isinstance(byte_list, str):
        return bytearray(remove_nonprintable(byte_list), 'utf-8')
    final = str()
    for the_int in byte_list:
        if chr(the_int) in string.printable:
            final += chr(the_int)
    return bytearray(final, 'utf-8')

def remove_nonprintable_bytes_limited(byte_list):
    final = bytes()
    if len(byte_list) >= 2 and byte_list[0] == 254 and byte_list[1] == 255:
        byte_list = byte_list[2:]
    for the_int in byte_list:
        if the_int > 0:
            final += bytes([the_int])
    return codecs.decode(final, 'latin1')

def remove_nonprintable_limited(text):
    text = re.sub(r'^\xfe\xff', '', text)
    text = re.sub(r'\x00', '', text)
    return codecs.decode(text, 'latin1')

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
                        js_to_write.append((name, remove_nonprintable_bytes(js_obj['/JS'])))
                    elif isinstance(js_obj['/JS'], pypdf.generic.EncodedStreamObject) or isinstance(js_obj['/JS'], pypdf.generic.DecodedStreamObject):
                        js_to_write.append((name, remove_nonprintable_bytes(js_obj['/JS'].getData())))

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
        if '/AcroForm' not in writer._root_object:
            writer._root_object.update({pypdf.generic.NameObject('/AcroForm'): pypdf.generic.DictionaryObject()})
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
    with open(outfile.name, 'wb') as fp:
        writer.write(fp)
    shutil.move(outfile.name, original_filename)

def flatten_pdf(filename):
    #logmessage("flatten_pdf: running")
    outfile = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
    subprocess_arguments = [PDFTK_PATH, filename, 'output', outfile.name, 'flatten']
    #logmessage("Arguments are " + str(subprocess_arguments))
    try:
        result = subprocess.run(subprocess_arguments, timeout=60).returncode
    except subprocess.TimeoutExpired:
        result = 1
        logmessage("flatten_pdf: call to pdftk took too long")
    if result != 0:
        logmessage("Failed to flatten PDF form " + str(template))
        raise DAError("Call to pdftk failed for template " + str(template) + " where arguments were " + " ".join(subprocess_arguments))
    commands = []
    shutil.move(outfile.name, filename)

def overlay_pdf(main_file, logo_file, out_file, first_page=None, last_page=None, logo_page=None, only=None):
    main_pdf = pypdf.PdfFileReader(main_file)
    logo_pdf = pypdf.PdfFileReader(logo_file)
    output_pdf = pypdf.PdfFileWriter()
    if first_page is None or first_page < 1:
        first_page = 1
    if last_page is None or last_page < 1:
        last_page = main_pdf.getNumPages()
    if first_page > main_pdf.getNumPages():
        first_page = main_pdf.getNumPages()
    if last_page < first_page:
        last_page = first_page
    if logo_page is None or logo_page < 1:
        logo_page = 1
    if logo_page > logo_pdf.getNumPages():
        logo_page = logo_pdf.getNumPages()
    for page_no in range(first_page - 1, last_page):
        if only == 'even':
            if page_no % 2 == 0:
                continue
        elif only == 'odd':
            if page_no % 2 != 0:
                continue
        page = main_pdf.getPage(page_no)
        page.mergePage(logo_pdf.getPage(logo_page - 1))
    for page_no in range(main_pdf.getNumPages()):
        page = main_pdf.getPage(page_no)
        output_pdf.addPage(page)
    with open(out_file, 'wb') as fp:
        output_pdf.write(fp)
