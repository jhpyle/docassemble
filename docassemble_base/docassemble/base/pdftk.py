import subprocess
import tempfile
import shutil
import re
import os
import string
import codecs
import logging
from io import BytesIO
import packaging
from xfdfgen import Xfdf
import pikepdf
import img2pdf
from pikepdf import Pdf
from PIL import Image
from docassemble.base.error import DAError, DAException
from docassemble.base.pdfa import pdf_to_pdfa
from docassemble.base.logger import logmessage
from docassemble.base.functions import word
from docassemble.base.config import daconfig
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1, PDFObjRef
from pdfminer.pdfpage import PDFPage

logging.getLogger('pdfminer').setLevel(logging.ERROR)

PDFTK_PATH = 'pdftk'
QPDF_PATH = 'qpdf'

SYSTEM_VERSION = daconfig.get('system version', None)
REPLACEMENT_FONT_SUPPORTED = SYSTEM_VERSION is not None and packaging.version.parse(SYSTEM_VERSION) >= packaging.version.parse("1.4.73")
DEFAULT_RENDERING_FONT = daconfig.get('default rendering font', None)
if REPLACEMENT_FONT_SUPPORTED and DEFAULT_RENDERING_FONT and os.path.isfile(DEFAULT_RENDERING_FONT):
    DEFAULT_FONT_ARGUMENTS = ['replacement_font', DEFAULT_RENDERING_FONT]
else:
    DEFAULT_FONT_ARGUMENTS = []


def set_pdftk_path(path):
    global PDFTK_PATH
    PDFTK_PATH = path


def read_fields(pdffile):
    outfields = []
    fp = open(pdffile, 'rb')
    id_to_page = {}
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    pageno = 1
    for page in PDFPage.create_pages(doc):
        id_to_page[page.pageid] = pageno
        pageno += 1
    if 'AcroForm' not in doc.catalog:
        return []
    fields = resolve1(doc.catalog['AcroForm'])['Fields']
    recursively_add_fields(fields, id_to_page, outfields)
    return sorted(outfields, key=fieldsorter)


def fieldsorter(x):
    if x[3] and isinstance(x[3], list):
        x_coord = x[3][0]
        y_coord = -1 * x[3][1]
    else:
        x_coord = 0
        y_coord = 0
    return (x[2], y_coord, x_coord)


def recursively_add_fields(fields, id_to_page, outfields, prefix='', parent_ft=None):
    if isinstance(fields, PDFObjRef):
        fields = resolve1(fields)
    for i in fields:
        field = resolve1(i)
        if isinstance(field, PDFObjRef):
            field = resolve1(field)
        try:
            name, value, rect, page, field_type = field.get('T'), field.get('V'), field.get('Rect'), field.get('P'), field.get('FT')
            if field_type is None:
                widget_type = str(field.get("Type"))
                if widget_type in ("/'Annot'", "/Annot"):
                    field_type = parent_ft
        except:
            logmessage("Skipping field " + repr(field))
            continue
        if isinstance(rect, PDFObjRef):
            rect = resolve1(rect)
        if isinstance(rect, list):
            new_list = []
            for item in rect:
                if isinstance(item, PDFObjRef):
                    new_list.append(resolve1(item))
                else:
                    new_list.append(item)
            rect = new_list
        else:
            rect = []
        if name is not None:
            if not isinstance(name, bytes):
                name = bytes(str(name), encoding='utf-8')
            name = remove_nonprintable_bytes_limited(name)
        if value is not None:
            if not isinstance(value, bytes):
                value = bytes(str(value), encoding='utf-8')
            value = remove_nonprintable_bytes_limited(value)
        # logmessage("name is " + repr(name) + " and FT is |" + repr(str(field_type)) + "| and value is " + repr(value))
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
                    if key in ('Off', 'off'):  # , 'No', 'no'
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
                # for val in value:
                #    logmessage("Got a " + str(ord(val)))
                # logmessage(repr(value.decode('utf8')))
                # default = re.sub(r'^\xc3\xbe\xc3\xbf', '', value)
                default = value
                if not default:
                    default = word("something")
            else:
                default = word("something")
        kids = field.get('Kids')
        if kids:
            if name is None:
                recursively_add_fields(kids, id_to_page, outfields, prefix=prefix, parent_ft=field_type)
            else:
                if prefix == '':
                    recursively_add_fields(kids, id_to_page, outfields, prefix=name, parent_ft=field_type)
                else:
                    recursively_add_fields(kids, id_to_page, outfields, prefix=prefix + '.' + name, parent_ft=field_type)
        else:
            if prefix != '' and name is not None:
                outfields.append((prefix + '.' + name, default, pageno, rect, field_type, export_value))
            elif prefix == '':
                outfields.append((name, default, pageno, rect, field_type, export_value))
            else:
                outfields.append((prefix, default, pageno, rect, field_type, export_value))


def fill_template(template, data_strings=None, data_names=None, hidden=None, readonly=None, images=None, pdf_url=None, editable=True, pdfa=False, password=None, owner_password=None, template_password=None, default_export_value=None, replacement_font=None, use_pdftk=False):
    if data_strings is None:
        data_strings = []
    if data_names is None:
        data_names = []
    if hidden is None:
        hidden = []
    if readonly is None:
        readonly = []
    if images is None:
        images = []
    if pdf_url is None:
        pdf_url = 'file.pdf'
    if not pdf_url.endswith('.pdf'):
        pdf_url += '.pdf'
    the_fields = read_fields(template)
    if len(the_fields) == 0:
        raise DAError("PDF template has no fields in it.")
    export_values = {}
    for field, default, pageno, rect, field_type, export_value in the_fields:  # pylint: disable=unused-variable
        field_type = re.sub(r'[^/A-Za-z]', '', str(field_type))
        if field_type in ('/Btn', "/'Btn'"):
            if field in export_values:
                export_values[field].append(export_value or default_export_value or 'Yes')
            else:
                export_values[field] = [export_value or default_export_value or 'Yes']
    if len(export_values) > 0:
        new_data_strings = []
        for key, val in data_strings:
            if key in export_values and len(export_values[key]) > 0:
                if len(export_values[key]) > 1:
                    # Implies a radio button, so val should stay the same. Check for yes vs True, since
                    # parse.py turns "true" into "yes".
                    # Just turn things off if it doesn't match any value
                    if 'True' in export_values[key] and val in ('Yes', 'yes'):
                        val = 'True'
                    if 'False' in export_values[key] and val in ('No', 'no'):
                        val = 'False'
                    if val not in export_values[key]:
                        val = 'Off'
                else:
                    export_val = export_values[key][0]
                    if str(val) in ('Yes', 'yes', 'True', 'true', 'On', 'on', export_val):
                        val = export_val
                    else:
                        if export_val == 'On':
                            val = 'Off'
                        elif export_val == 'on':
                            val = 'off'
                        elif export_val == 'yes':
                            val = 'no'
                        else:
                            val = 'No'
            new_data_strings.append((key, val))
        data_strings = new_data_strings
    data_dict = {}
    for key, val in data_strings:
        data_dict[key] = val
    pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    if pdfa or not editable or use_pdftk:
        fdf = Xfdf(pdf_url, data_dict)
        # fdf = fdfgen.forge_fdf(pdf_url, data_strings, data_names, hidden, readonly)
        fdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".xfdf", delete=False)
        # fdf_file.write(fdf)
        fdf_file.close()
        fdf.write_xfdf(fdf_file.name)
        if template_password is not None:
            template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            qpdf_subprocess_arguments = [QPDF_PATH, '--decrypt', '--password=' + template_password, template, template_file.name]
            try:
                result = subprocess.run(qpdf_subprocess_arguments, timeout=60, check=False).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("fill_template: call to qpdf took too long")
            if result != 0:
                logmessage("Failed to decrypt PDF template " + str(template))
                raise DAError("Call to qpdf failed for template " + str(template) + " where arguments were " + " ".join(qpdf_subprocess_arguments))
            template = template_file.name
        if replacement_font:
            if REPLACEMENT_FONT_SUPPORTED:
                font_arguments = ['replacement_font', replacement_font]
            else:
                logmessage("Warning: the rendering font feature requires system version 1.4.73 or later")
                font_arguments = []
        else:
            font_arguments = DEFAULT_FONT_ARGUMENTS
        subprocess_arguments = [PDFTK_PATH, template, 'fill_form', fdf_file.name, 'output', pdf_file.name] + font_arguments
        # logmessage("Arguments are " + str(subprocess_arguments))
        if len(images) > 0:
            subprocess_arguments.append('need_appearances')
        else:
            if pdfa or not editable:
                subprocess_arguments.append('flatten')
            else:
                subprocess_arguments.append('need_appearances')
        completed_process = None
        try:
            completed_process = subprocess.run(subprocess_arguments, timeout=600, check=False, capture_output=True)
            result = completed_process.returncode
        except subprocess.TimeoutExpired:
            result = 1
            logmessage("fill_template: call to pdftk fill_form took too long")
        if result != 0:
            logmessage("Failed to fill PDF form " + str(template))
            pdftk_error_msg = (f": {completed_process.stderr}") if completed_process else ""
            raise DAError("Call to pdftk failed for template " + str(template) + " where arguments were " + " ".join(subprocess_arguments) + pdftk_error_msg)
        if len(images) > 0:
            temp_pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            shutil.copyfile(pdf_file.name, temp_pdf_file.name)
            pdf = Pdf.open(temp_pdf_file.name)
    else:
        if template_password:
            pdf = Pdf.open(template, password=template_password)
        else:
            pdf = Pdf.open(template)
        for page in pdf.pages:
            if not hasattr(page, 'Annots'):
                continue
            for the_annot in page.Annots:
                annot = the_annot
                annot_kid = None
                while not (hasattr(annot, "FT") and hasattr(annot, "T")) and hasattr(annot, 'Parent'):
                    annot_kid = annot
                    annot = annot.Parent
                if not (hasattr(annot, "T") and hasattr(annot, "FT")):
                    continue
                for field, value in data_dict.items():
                    if field != str(annot.T):
                        continue
                    field_type = str(annot.FT)
                    if field_type == "/Tx":
                        the_string = pikepdf.String(value)
                        annot.V = the_string
                    elif field_type == "/Btn":
                        if hasattr(annot, "A"):
                            continue
                        the_name = pikepdf.Name('/' + value)
                        # Could be radio button: if it is, set the appearance stream of the
                        # correct child annot
                        if (annot_kid is not None and hasattr(annot_kid, "AP")
                                and hasattr(annot_kid.AP, "N")):
                            if the_name in annot_kid.AP.N.keys():
                                annot_kid.AS = the_name
                                annot.V = the_name
                            else:
                                for off in ["/Off", "/off"]:
                                    if off in annot_kid.AP.N.keys():
                                        annot_kid.AS = pikepdf.Name(off)
                                        break
                        elif (hasattr(annot, "AP") and hasattr(annot.AP, "N")):
                            if the_name in annot.AP.N.keys():
                                annot.AS = the_name
                                annot.V = the_name
                            elif hasattr(annot.AP, "D"):
                                for off in ["/Off", "/off"]:
                                    if off in annot.AP.D:
                                        annot.AS = pikepdf.Name(off)
                                        annot.V = pikepdf.Name(off)
                                        break
                            else:
                                annot.AS = pikepdf.Name("/Off")
                                annot.V = pikepdf.Name("/Off")
                    elif field_type == "/Ch":
                        opt_list = [str(item) for item in annot.Opt]
                        if value not in opt_list:
                            opt_list.append(value)
                            annot.Opt = pikepdf.Array(opt_list)
                        the_string = pikepdf.String(value)
                        annot.V = the_string
        pdf.Root.AcroForm.NeedAppearances = True
        pdf.generate_appearance_streams()
        pdf.Root.AcroForm.NeedAppearances = True
        if len(images) == 0:
            pdf.save(pdf_file.name)
            pdf.close()
    if len(images) > 0:
        fields = {}
        for field, default, pageno, rect, field_type, export_value in the_fields:
            if str(field_type) in ('/Sig', "/'Sig'"):
                fields[field] = {'pageno': pageno, 'rect': rect}
        image_todo = []
        for field, file_info in images:
            if field not in fields:
                logmessage("field name " + str(field) + " not found in PDF file")
                continue
            temp_png = tempfile.NamedTemporaryFile(mode="wb", suffix=".png")
            args = [daconfig.get('imagemagick', 'convert'), file_info['fullpath'], "-trim", "+repage", "+profile", '*', '-density', '0', temp_png.name]
            try:
                result = subprocess.run(args, timeout=60, check=False).returncode
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
            if dppx > dppy:
                dpp = dppx
                x_offset = 0
                y_offset = int(0.5 * ((ytwo - yone) * dpp - height))
            else:
                dpp = dppy
                x_offset = int(0.5 * ((xtwo - xone) * dpp - width))
                y_offset = 0
            new_im = Image.new('RGBA', (int((xtwo - xone) * dpp), int((ytwo - yone) * dpp)), (255, 0, 0, 0))
            new_im.paste(im, (x_offset, y_offset))
            overlay_pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            with BytesIO() as output:
                new_im.save(output, 'PNG')
                overlay_pdf_file.write(img2pdf.convert(output.getvalue()))
                overlay_pdf_file.close()
            image_todo.append({'overlay_file': overlay_pdf_file.name, 'pageno': fields[field]['pageno'], 'field': field})
        if len(image_todo) > 0:
            for item in image_todo:
                xone, yone, xtwo, ytwo = fields[item['field']]['rect']
                # logmessage("Trying to save to page " + repr(item['pageno'] - 1))
                with Pdf.open(item['overlay_file']) as overlay_file:
                    overlay_page = overlay_file.pages[0]
                    pdf.pages[item['pageno'] - 1].add_overlay(overlay_page, rect=pikepdf.Rectangle(xone, yone, xtwo, ytwo))
        pdf.save(pdf_file.name)
        pdf.close()
    if (pdfa or not editable) and len(images) > 0:
        flatten_pdf(pdf_file.name)
    if pdfa:
        pdf_to_pdfa(pdf_file.name)
    if password or owner_password:
        pdf_encrypt(pdf_file.name, password, owner_password)
    return pdf_file.name


def pdf_encrypt(filename, user_password, owner_password):
    # logmessage("pdf_encrypt: running; password is " + repr(password))
    outfile = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
    if owner_password is None:
        commands = ['pdftk', filename, 'output', outfile.name, 'user_pw', user_password, 'allow', 'printing']
    elif user_password is None:
        commands = ['pdftk', filename, 'output', outfile.name, 'owner_pw', owner_password, 'allow', 'printing']
    else:
        commands = ['pdftk', filename, 'output', outfile.name, 'owner_pw', owner_password, 'user_pw', user_password, 'allow', 'printing']
    try:
        output = subprocess.check_output(commands, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as err:
        output = err.output
        raise DAError("pdf_encrypt: error running pdftk.  " + output)
    # logmessage(' '.join(commands))
    # logmessage(output)
    shutil.move(outfile.name, filename)


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


def flatten_pdf(filename):
    # logmessage("flatten_pdf: running")
    outfile = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
    subprocess_arguments = [PDFTK_PATH, filename, 'output', outfile.name, 'flatten']
    # logmessage("Arguments are " + str(subprocess_arguments))
    completed_process = None
    try:
        completed_process = subprocess.run(subprocess_arguments, timeout=60, check=False, capture_output=True)
        result = completed_process.returncode
    except subprocess.TimeoutExpired:
        result = 1
        logmessage("flatten_pdf: call to pdftk took too long")
    if result != 0:
        logmessage("Failed to flatten PDF form")
        pdftk_error_msg = (f": {completed_process.stderr}") if completed_process else ""
        raise DAError("Call to pdftk failed for template where arguments were " + " ".join(subprocess_arguments) + pdftk_error_msg)
    shutil.move(outfile.name, filename)


def overlay_pdf_multi(main_file, logo_file, out_file):
    subprocess_arguments = [PDFTK_PATH, main_file, 'multistamp', logo_file, 'output', out_file]
    try:
        result = subprocess.run(subprocess_arguments, timeout=60, check=False).returncode
    except subprocess.TimeoutExpired:
        result = 1
        logmessage("overlay_pdf_multi: call to pdftk took too long")
    if result != 0:
        logmessage("Failed to overlay PDF")
        raise DAError("Call to pdftk failed for overlay where arguments were " + " ".join(subprocess_arguments))


def overlay_pdf(main_file, logo_file, out_file, first_page=None, last_page=None, logo_page=None, only=None):
    main_pdf = Pdf.open(main_file)
    logo_pdf = Pdf.open(logo_file)
    if first_page is None or first_page < 1:
        first_page = 1
    if last_page is None or last_page < 1:
        last_page = len(main_pdf.pages)
    if first_page > len(main_pdf.pages):
        first_page = len(main_pdf.pages)
    last_page = max(last_page, first_page)
    if logo_page is None or logo_page < 1:
        logo_page = 1
    if logo_page > len(logo_pdf.pages):
        logo_page = len(logo_pdf.pages)
    for page_no in range(first_page - 1, last_page):
        if only == 'even':
            if page_no % 2 == 0:
                continue
        elif only == 'odd':
            if page_no % 2 != 0:
                continue
        main_pdf.pages[page_no].add_overlay(logo_pdf.pages[logo_page - 1])
    main_pdf.save(out_file)
    logo_pdf.close()
    main_pdf.close()


def apply_qpdf(filename):
    new_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    try:
        pikepdf.Job(['pikepdf', filename, new_file.name]).run()
    except BaseException as err:
        raise DAError("Could not fix PDF: " + err.__class__.__name__ + ": " + str(err))
    shutil.copyfile(new_file.name, filename)
    os.remove(new_file.name)


def extract_pages(input_path, output_path, first, last):
    subprocess_arguments = [PDFTK_PATH, input_path, 'cat', str(first) + '-' + str(last), 'output', output_path]
    try:
        result = subprocess.run(subprocess_arguments, timeout=60, check=False).returncode
    except subprocess.TimeoutExpired:
        raise DAException("call to pdftk took too long where arguments were " + " ".join(subprocess_arguments))
    if result != 0:
        raise DAException("call to pdftk failed where arguments were " + " ".join(subprocess_arguments))
