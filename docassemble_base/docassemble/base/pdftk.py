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
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1, PDFObjRef
from pdfminer.pdfpage import PDFPage
from docassemble.base.error import DAError, DAException
from docassemble.base.pdfa import pdf_to_pdfa
from docassemble.base.language.words import word
from docassemble.base.logger import logmessage
from docassemble.base.config import daconfig

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


def _pdf_object_key(obj):
    """Return a stable key for an indirect PDF object."""
    try:
        if obj.objgen != (0, 0):
            return obj.objgen
    except Exception:
        pass
    return id(obj)


def _inherited_field_value(widget, key):
    """Resolve an inheritable field value from a widget and its ancestors."""
    current = widget
    seen = set()
    while current is not None:
        current_key = _pdf_object_key(current)
        if current_key in seen:
            break
        seen.add(current_key)
        value = current.get(key)
        if value is not None:
            return value
        current = current.get('/Parent')
    return None


def _display_state(widget):
    """Resolve /AS first, then the inherited field value as a fallback."""
    state = widget.get('/AS') or _inherited_field_value(widget, '/V')
    if state is None:
        return None
    state = str(state)
    try:
        return pikepdf.Name(state if state.startswith('/') else '/' + state)
    except ValueError:
        return None


def _selected_appearance(widget):
    """Return the normal appearance stream that the widget actually displays."""
    appearance = widget.get('/AP')
    if appearance is None:
        return None
    normal = appearance.get('/N')
    if isinstance(normal, pikepdf.Stream):
        return normal
    if not isinstance(normal, pikepdf.Dictionary):
        return None
    state = _display_state(widget)
    if state is not None and state in normal:
        selected = normal[state]
        return selected if isinstance(selected, pikepdf.Stream) else None
    return None


def _replace_selected_appearance(widget, appearance):
    normal = widget.AP.N
    if isinstance(normal, pikepdf.Stream):
        widget.AP.N = appearance
        return
    state = _display_state(widget)
    if state is None or state not in normal:
        raise ValueError("widget has no selected normal appearance")
    widget.AS = state
    normal[state] = appearance


def _ensure_selected_appearance(pdf, widget):
    """Supply an empty off appearance when the unselected box is page artwork."""
    appearance = _selected_appearance(widget)
    if appearance is not None or _inherited_field_value(widget, '/FT') != '/Btn':
        return appearance
    state = _display_state(widget)
    normal = widget.get('/AP') and widget.AP.get('/N')
    if str(state).lower() != '/off' or not isinstance(normal, pikepdf.Dictionary):
        return None
    reference = next((item for item in normal.values() if isinstance(item, pikepdf.Stream)), None)
    if reference is None:
        return None
    appearance = pdf.make_stream(
        b'',
        Type=pikepdf.Name('/XObject'),
        Subtype=pikepdf.Name('/Form'),
        FormType=1,
        BBox=reference.get('/BBox', pikepdf.Array([0, 0, 1, 1])),
        Resources=pikepdf.Dictionary(),
    )
    if reference.get('/Matrix') is not None:
        appearance.Matrix = reference.Matrix
    widget.AS = state
    normal[state] = appearance
    return appearance


def _iter_widgets(pdf):
    for page in pdf.pages:
        for annot in page.get('/Annots', []):
            if annot.get('/Subtype') == '/Widget':
                yield page, annot


def _parent_tree(pdf):
    """Return the structure tree's /ParentTree as a mutable number tree."""
    root = pdf.Root.get('/StructTreeRoot')
    if root is None or root.get('/ParentTree') is None:
        return None
    # NumberTree only wraps a dictionary the Pdf owns.
    root.ParentTree = pdf.make_indirect(root.ParentTree)
    return pikepdf.NumberTree(root.ParentTree)


def _find_widget_objr(item, widget):
    """Find an OBJR content item that points at widget."""
    if isinstance(item, pikepdf.Array):
        for child in item:
            result = _find_widget_objr(child, widget)
            if result is not None:
                return result
        return None
    if not isinstance(item, pikepdf.Dictionary):
        return None
    if item.get('/Type') == '/OBJR' and _pdf_object_key(item.get('/Obj')) == _pdf_object_key(widget):
        return item
    return None


def _form_structure_element(parent_tree, widget):
    """Return the existing Form element and OBJR that credibly own widget."""
    struct_parent = widget.get('/StructParent')
    if parent_tree is None or struct_parent is None or int(struct_parent) not in parent_tree:
        return None, None
    element = parent_tree[int(struct_parent)]
    if isinstance(element, pikepdf.Array):
        # Parent-tree arrays are for marked content. Annotation entries normally
        # point directly to one structure element, but tolerate a single entry.
        element = next((item for item in element if isinstance(item, pikepdf.Dictionary)), None)
    if not isinstance(element, pikepdf.Dictionary) or element.get('/S') != '/Form':
        return None, None
    objr = _find_widget_objr(element.get('/K'), widget)
    if objr is None:
        return None, None
    return element, objr


def _appearance_wrapper(pdf, appearance, actual_text=None, mcid=None):
    """Make a visually identical Form XObject that invokes appearance once.

    The marked content lives inside this wrapper rather than in the page content
    stream, so pdftk only has to paint the XObject during flattening and the
    tagging rides along untouched.  Inlining the BDC/EMC into the page would
    make the flatten discard it.
    """
    content = b'q\n/DocassembleAppearance Do\nQ\n'
    if mcid is not None:
        content = (
            b'/Span << /MCID '
            + str(int(mcid)).encode('ascii')
            + b' >> BDC\n'
            + content
            + b'EMC\n'
        )
    if actual_text is not None:
        # ActualText on a sequence containing only an invoked Form XObject is
        # ignored by some extractors.  Give it an invisible text-showing operation
        # to replace.  The dummy ASCII glyph is portable, ActualText carries Unicode,
        # and text rendering mode 3 cannot change the printed appearance.
        content += (
            b'/Span << /ActualText '
            + pikepdf.String(actual_text).unparse()
            + b' >> BDC\nBT\n/DocassembleFallback 1 Tf\n3 Tr\n0 0 Td\n(x) Tj\nET\nEMC\n'
        )
    # An appearance stream is allowed to omit /Subtype while it is only an
    # annotation appearance, but invoking it as an XObject resource requires one.
    if appearance.get('/Subtype') is None:
        appearance.Type = pikepdf.Name('/XObject')
        appearance.Subtype = pikepdf.Name('/Form')
    resources = pikepdf.Dictionary(XObject=pikepdf.Dictionary(DocassembleAppearance=appearance))
    if actual_text is not None:
        resources.Font = pikepdf.Dictionary(
            DocassembleFallback=pikepdf.Dictionary(
                Type=pikepdf.Name('/Font'),
                Subtype=pikepdf.Name('/Type1'),
                BaseFont=pikepdf.Name('/Helvetica'),
                Encoding=pikepdf.Name('/WinAnsiEncoding'),
            )
        )
    wrapper = pdf.make_stream(
        content,
        Type=pikepdf.Name('/XObject'),
        Subtype=pikepdf.Name('/Form'),
        FormType=1,
        BBox=appearance.get('/BBox', pikepdf.Array([0, 0, 1, 1])),
        Resources=resources,
    )
    if appearance.get('/Matrix') is not None:
        wrapper.Matrix = appearance.Matrix
    return wrapper


def _button_role_and_state(widget):
    flags = int(_inherited_field_value(widget, '/Ff') or 0)
    if flags & (1 << 16):
        return 'pb', None
    state = str(_display_state(widget) or '/Off').lower()
    checked = 'off' if state == '/off' else ('neutral' if state in ('/neutral', '/mixed') else 'on')
    return ('rb' if flags & (1 << 15) else 'cb'), checked


def _printfield_role_and_state(widget):
    field_type = _inherited_field_value(widget, '/FT')
    if field_type == '/Btn':
        return _button_role_and_state(widget)
    if field_type in ('/Tx', '/Ch'):
        return 'tv', None
    return None, None


def _add_printfield_attribute(element, role, checked, description):
    attribute = None
    current = element.get('/A')
    candidates = current if isinstance(current, pikepdf.Array) else [current]
    for candidate in candidates:
        if isinstance(candidate, pikepdf.Dictionary) and candidate.get('/O') == '/PrintField':
            attribute = candidate
            break
    if attribute is None:
        attribute = pikepdf.Dictionary(O=pikepdf.Name('/PrintField'))
        if current is None:
            element.A = attribute
        elif isinstance(current, pikepdf.Array):
            current.append(attribute)
        else:
            element.A = pikepdf.Array([current, attribute])
    attribute.Role = pikepdf.Name('/' + role)
    if checked is not None:
        attribute[pikepdf.Name('/checked')] = pikepdf.Name('/' + checked)
    elif '/checked' in attribute:
        del attribute[pikepdf.Name('/checked')]
    if description:
        attribute.Desc = pikepdf.String(str(description))


def _fallback_button_text(role, checked, checked_label, unchecked_label):
    if role == 'pb':
        return None
    if role == 'rb':
        return word("radio button, selected") if checked == 'on' else word("radio button, unselected")
    if checked == 'on':
        return checked_label if checked_label is not None else word("checkbox, checked")
    return unchecked_label if unchecked_label is not None else word("checkbox, unchecked")


def prepare_accessible_flatten(pdf, flattened_checkbox_label=None, flattened_checkbox_unselected_label=None):
    """Move tagged widget semantics to their selected appearance XObjects.

    Untagged checkbox and radio appearances instead receive an invisible ActualText
    fallback, leaving the pdftk-generated drawing unchanged while giving text-based
    accessibility tools a meaningful state to read.  A source PDF that was never
    tagged does not become PDF/UA conformant this way; only its field states
    become readable.
    """
    parent_tree = _parent_tree(pdf)
    for _page, widget in _iter_widgets(pdf):
        appearance = _ensure_selected_appearance(pdf, widget)
        if appearance is None:
            continue
        role, checked = _printfield_role_and_state(widget)
        element, objr = _form_structure_element(parent_tree, widget)
        if element is not None:
            # Annotation structure uses a singular /StructParent entry whose
            # parent-tree value points directly to the owning structure element.
            # A painted Form XObject instead needs /StructParents (plural), a
            # parent-tree array indexed by MCID, and an MCR content item.  Keeping
            # the annotation-shaped mapping on an XObject makes NVDA's Acrobat
            # virtual buffer loop indefinitely while loading the document.
            appearance = _appearance_wrapper(pdf, appearance, mcid=0)
            _replace_selected_appearance(widget, appearance)
            struct_parent = int(widget.StructParent)
            appearance.StructParents = struct_parent
            del widget.StructParent
            parent_tree[struct_parent] = pikepdf.Array([element])
            objr.Type = pikepdf.Name('/MCR')
            if '/Obj' in objr:
                del objr[pikepdf.Name('/Obj')]
            objr.Stm = appearance
            objr.MCID = 0
            if role is not None:
                description = _inherited_field_value(widget, '/TU') or _inherited_field_value(widget, '/T')
                _add_printfield_attribute(element, role, checked, description)
            continue
        if _inherited_field_value(widget, '/FT') != '/Btn':
            continue
        fallback = _fallback_button_text(
            role, checked, flattened_checkbox_label, flattened_checkbox_unselected_label
        )
        if fallback:
            appearance = _appearance_wrapper(pdf, appearance, actual_text=fallback)
            _replace_selected_appearance(widget, appearance)


def _flatten_widgets(filename, template):
    """Flatten the prepared widgets and drop the AcroForm they leave behind.

    qpdf can paint these same appearances but does not place every real-world
    BBox/Rect/Matrix combination exactly as pdftk does, so pdftk does the final
    placement to preserve legacy rendering and other annotations.
    """
    flatten_pdf(filename)
    with Pdf.open(filename, allow_overwriting_input=True) as pdf:
        acroform = pdf.Root.get('/AcroForm')
        fields = acroform.get('/Fields') if acroform is not None else None
        if any(_iter_widgets(pdf)) or (fields is not None and len(fields) > 0):
            raise DAError("Could not flatten every PDF form widget in template " + str(template))
        if acroform is not None:
            del pdf.Root.AcroForm
            pdf.save()


def fill_template(template, data_strings=None, data_names=None, hidden=None, readonly=None, images=None, pdf_url=None, editable=True, pdfa=False, password=None, owner_password=None, template_password=None, default_export_value=None, replacement_font=None, use_pdftk=False, flattened_checkbox_label=None, flattened_checkbox_unselected_label=None):
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
    flattening = pdfa or not editable
    if flattening or use_pdftk:
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
        # pdftk generates the normal appearances while filling.  In the flattened
        # path they must remain widgets for the accessibility rewrite below.
        if not flattening:
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
        if len(images) > 0 or flattening:
            temp_pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            shutil.copyfile(pdf_file.name, temp_pdf_file.name)
            pdf = Pdf.open(temp_pdf_file.name)
        if flattening and len(images) == 0:
            prepare_accessible_flatten(
                pdf,
                flattened_checkbox_label=flattened_checkbox_label,
                flattened_checkbox_unselected_label=flattened_checkbox_unselected_label,
            )
            pdf.save(pdf_file.name)
            pdf.close()
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
        try:
            pdf.generate_appearance_streams()
        except Exception as err:
            logmessage("fill_template: could not generate appearance streams: " + str(err))
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
            if width < 10 or height < 10:
                im.close()
                im = Image.open(file_info['fullpath'])
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
        if flattening:
            prepare_accessible_flatten(
                pdf,
                flattened_checkbox_label=flattened_checkbox_label,
                flattened_checkbox_unselected_label=flattened_checkbox_unselected_label,
            )
        pdf.save(pdf_file.name)
        pdf.close()
    if flattening:
        _flatten_widgets(pdf_file.name, template)
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
    first_page = min(first_page, len(main_pdf.pages))
    last_page = max(last_page, first_page)
    if logo_page is None or logo_page < 1:
        logo_page = 1
    logo_page = min(logo_page, len(logo_pdf.pages))
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
