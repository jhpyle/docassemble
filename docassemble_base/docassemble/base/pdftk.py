import os
import os.path
import subprocess
import docassemble.base.filter
import docassemble.base.util
import tempfile
import shutil
import fdfgen
import yaml
from docassemble.base.error import DAError
from subprocess import call, check_output
from docassemble.base.logger import logmessage
from docassemble.base.util import word

PDFTK_PATH = 'pdftk'

def set_pdftk_path(path):
    global PDFTK_PATH
    PDFTK_PATH = path

def read_fields(pdffile):
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
    
def fill_template(template, data_strings=[], data_names=[], hidden=[], readonly=[], pdf_url=''):
    fdf = fdfgen.forge_fdf(pdf_url, data_strings, data_names, hidden, readonly)
    fdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".fdf", delete=False)
    fdf_file.write(fdf)
    fdf_file.close()
    pdf_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False)
    subprocess_arguments = [PDFTK_PATH, template, 'fill_form', fdf_file.name,'output', pdf_file.name, 'flatten']
    result = call(subprocess_arguments)
    if result != 0:
        logmessage("Failed to fill PDF form " + str(template))
        raise DAError("Call to pdftk failed for template " + str(template) + " where arguments were " + " ".join(subprocess_arguments))
    return pdf_file.name
