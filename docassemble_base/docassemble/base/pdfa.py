import tempfile
import subprocess
import shutil
from docassemble.base.error import DAError
from docassemble.base.logger import logmessage

def pdf_to_pdfa(filename):
    logmessage("pdf_to_pdfa: running")
    outfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    directory = tempfile.mkdtemp()
    commands = ['gs', '-dPDFA', '-dBATCH', '-dNOPAUSE', '-sProcessColorModel=DeviceCMYK', '-sDEVICE=pdfwrite', '-sPDFACompatibilityPolicy=1', '-sOutputFile=' + outfile.name, filename]
    try:
        output = subprocess.check_output(commands, cwd=directory, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        output = err.output
        raise DAError("pdf_to_pdfa: error running ghostscript.  " + output)
    logmessage(output)
    shutil.move(outfile.name, filename)
