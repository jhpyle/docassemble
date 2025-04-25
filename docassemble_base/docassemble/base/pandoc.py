import os
import os.path
import subprocess
import tempfile
import filecmp
import shutil
# import sys
import re
import time
import random
import mimetypes
import urllib.request
import convertapi
import requests
from pikepdf import Pdf
import docassemble.base.filter
import docassemble.base.functions
from docassemble.base.config import daconfig
from docassemble.base.logger import logmessage
from docassemble.base.pdfa import pdf_to_pdfa
from docassemble.base.pdftk import pdf_encrypt
from docassemble.base.error import DAError, DAException

style_find = re.compile(r'{\s*(\\s([1-9])[^\}]+)\\sbasedon[^\}]+heading ([0-9])', flags=re.DOTALL)
PANDOC_PATH = daconfig.get('pandoc', 'pandoc')


def copy_if_different(source, destination):
    if (not os.path.isfile(destination)) or filecmp.cmp(source, destination) is False:
        shutil.copyfile(source, destination)


def gotenberg_to_pdf(from_file, to_file, pdfa, password, owner_password):
    if pdfa:
        data = {'nativePdfFormat': 'PDF/A-1a'}
    else:
        data = {}
    r = requests.post(daconfig['gotenberg url'] + '/forms/libreoffice/convert', data=data, files={'files': open(from_file, 'rb')}, timeout=6000)
    if r.status_code != 200:
        logmessage("call to " + daconfig['gotenberg url'] + " returned status code " + str(r.status_code))
        logmessage(r.text)
        raise DAException("Call to gotenberg did not succeed")
    with open(to_file, 'wb') as fp:
        fp.write(r.content)
    if password or owner_password:
        pdf_encrypt(to_file, password, owner_password)


def cloudconvert_to_pdf(in_format, from_file, to_file, pdfa, password):
    headers = {"Authorization": "Bearer " + daconfig.get('cloudconvert secret').strip()}
    data = {
        "tasks": {
            "import-1": {
                "operation": "import/upload"
            },
            "task-1": {
                "operation": "convert",
                "input_format": in_format,
                "output_format": "pdf",
                "engine": "office",
                "input": [
                    "import-1"
                ],
                "optimize_print": True,
                "pdf_a": pdfa,
                "filename": "myoutput.docx"
            },
            "export-1": {
                "operation": "export/url",
                "input": [
                    "task-1"
                ],
                "inline": False,
                "archive_multiple_files": False
            }
        }
    }
    if password:
        data['tasks']['task-1']['password'] = password
    r = requests.post("https://api.cloudconvert.com/v2/jobs", json=data, headers=headers, timeout=6000)
    resp = r.json()
    if 'data' not in resp:
        logmessage("cloudconvert_to_pdf: create job returned " + repr(r.text))
        raise DAException("cloudconvert_to_pdf: failed to create job")
    uploaded = False
    for task in resp['data']['tasks']:
        if task['name'] == 'import-1':
            r = requests.post(task['result']['form']['url'], data=task['result']['form']['parameters'], files={'file': open(from_file, 'rb')}, timeout=6000)
            uploaded = True
    if not uploaded:
        raise DAException("cloudconvert_to_pdf: failed to upload")
    r = requests.get("https://sync.api.cloudconvert.com/v2/jobs/%s" % (resp['data']['id'],), headers=headers, timeout=60)
    wait_resp = r.json()
    if 'data' not in wait_resp:
        logmessage("cloudconvert_to_pdf: wait returned " + repr(r.text))
        raise DAException("Failed to wait on job")
    ok = False
    for task in wait_resp['data']['tasks']:
        if task['operation'] == "export/url":
            for file_result in task['result']['files']:
                urllib.request.urlretrieve(file_result['url'], to_file)
                ok = True
    if not ok:
        raise DAException("cloudconvert failed")


def convertapi_to_pdf(from_file, to_file):
    convertapi.api_credentials = daconfig.get('convertapi secret')
    result = convertapi.convert('pdf', {'File': from_file})
    result.file.save(to_file)


def get_pandoc_version():
    p = subprocess.Popen(
        [PANDOC_PATH, '--version'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    version_content = p.communicate()[0].decode('utf-8')
    version_content = re.sub(r'\n.*', '', version_content)
    version_content = re.sub(r'^pandoc ', '', version_content)
    return version_content

PANDOC_INITIALIZED = False
PANDOC_OLD = False
PANDOC_ENGINE = '--pdf-engine=' + daconfig.get('pandoc engine', 'pdflatex')


def initialize_pandoc():
    global PANDOC_OLD
    global PANDOC_ENGINE
    global PANDOC_INITIALIZED
    if PANDOC_INITIALIZED:
        return
    PANDOC_VERSION = get_pandoc_version()
    if PANDOC_VERSION.startswith('1'):
        PANDOC_OLD = True
        PANDOC_ENGINE = '--latex-engine=' + daconfig.get('pandoc engine', 'pdflatex')
    else:
        PANDOC_OLD = False
        try:
            subprocess.check_output(['lualatex', '--help'], stderr=subprocess.STDOUT)
            assert os.path.isfile('/usr/share/texlive/texmf-dist/tex/luatex/luatexbase/luatexbase.sty')
            lualatex_supported = True
        except:
            lualatex_supported = False
        if lualatex_supported:
            PANDOC_ENGINE = '--pdf-engine=' + daconfig.get('pandoc engine', 'lualatex')
        else:
            PANDOC_ENGINE = '--pdf-engine=' + daconfig.get('pandoc engine', 'pdflatex')
    PANDOC_INITIALIZED = True

UNOCONV_PATH = daconfig.get('unoconv path', '/usr/bin/daunoconv')
UNOCONV_AVAILABLE = bool('enable unoconv' in daconfig and daconfig['enable unoconv'] is True and os.path.isfile(UNOCONV_PATH) and os.access(UNOCONV_PATH, os.X_OK))
UNOCONV_FILTERS = {'pdfa': ['-e', 'SelectPdfVersion=1', '-e', 'UseTaggedPDF=true'], 'tagged': ['-e', 'UseTaggedPDF=true'], 'default': []}
LIBREOFFICE_PATH = daconfig.get('libreoffice', 'libreoffice')
LIBREOFFICE_MACRO_PATH = daconfig.get('libreoffice macro file', '/var/www/.config/libreoffice/4/user/basic/Standard/Module1.xba')
LIBREOFFICE_INITIALIZED = False

convertible_mimetypes = {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx", "application/vnd.oasis.opendocument.text": "odt"}
convertible_extensions = {"docx": "docx", "odt": "odt"}
if daconfig.get('libreoffice', 'libreoffice') is not None:
    convertible_mimetypes.update({"application/msword": "doc", "application/rtf": "rtf"})
    convertible_extensions.update({"doc": "doc", "rtf": "rtf"})

# fontfamily: zi4, mathptmx, courier
# \ttfamily
# \renewcommand{\thesubsubsubsection}{\alph{subsubsubsection}.}
# \renewcommand{\thesubsubsubsubsection}{\roman{subsubsubsubsection}.}
#  - \newenvironment{allcaps}{\startallcaps}{}
#  - \def\startallcaps#1\end{\uppercase{#1}\end}


class MyPandoc:

    def __init__(self, **kwargs):
        initialize_pandoc()
        if 'pdfa' in kwargs and kwargs['pdfa']:
            self.pdfa = True
        else:
            self.pdfa = False
        self.password = kwargs.get('password', None)
        self.owner_password = kwargs.get('owner_password', None)
        self.input_content = None
        self.output_content = None
        self.input_format = 'markdown'
        self.output_format = 'rtf'
        self.output_extension = 'rtf'
        self.output_filename = None
        self.template_file = None
        self.reference_file = None
        self.metadata = {}
        self.initial_yaml = []
        self.additional_yaml = []
        self.arguments = []

    def convert_to_file(self, question):
        metadata_as_dict = {}
        if isinstance(self.metadata, dict):
            metadata_as_dict = self.metadata
        elif isinstance(self.metadata, list):
            for data in self.metadata:
                if isinstance(data, dict):
                    for key in data:
                        metadata_as_dict[key] = data[key]
        if self.output_format == 'rtf to docx':
            self.output_extension = 'rtf'
        else:
            self.output_extension = self.output_format
        if self.output_format in ('rtf', 'rtf to docx') and self.template_file is None:
            self.template_file = docassemble.base.functions.standard_template_filename('Legal-Template.rtf')
        if self.output_format == 'docx' and self.reference_file is None:
            self.reference_file = docassemble.base.functions.standard_template_filename('Legal-Template.docx')
        if self.output_format in ('pdf', 'tex') and self.template_file is None:
            self.template_file = docassemble.base.functions.standard_template_filename('Legal-Template.tex')
        yaml_to_use = []
        if self.output_format in ('rtf', 'rtf to docx'):
            # logmessage("pre input content is " + str(self.input_content))
            self.input_content = docassemble.base.filter.rtf_prefilter(self.input_content)
            # logmessage("post input content is " + str(self.input_content))
        if self.output_format == 'docx':
            self.input_content = docassemble.base.filter.docx_filter(self.input_content, metadata=metadata_as_dict, question=question)
        if self.output_format in ('pdf', 'tex'):
            if len(self.initial_yaml) == 0:
                standard_file = docassemble.base.functions.standard_template_filename('Legal-Template.yml')
                if standard_file is not None:
                    self.initial_yaml.append(standard_file)
            for yaml_file in self.initial_yaml:
                if yaml_file is not None:
                    yaml_to_use.append(yaml_file)
            for yaml_file in self.additional_yaml:
                if yaml_file is not None:
                    yaml_to_use.append(yaml_file)
            # logmessage("Before: " + repr(self.input_content))
            self.input_content = docassemble.base.filter.pdf_filter(self.input_content, metadata=metadata_as_dict, question=question)
            # logmessage("After: " + repr(self.input_content))
        if not re.search(r'[^\s]', self.input_content):
            self.input_content = "\\textbf{}\n"
        temp_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="w", suffix=".md", delete=False, encoding='utf-8')
        temp_file.write(self.input_content)
        temp_file.close()
        temp_outfile = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix="." + str(self.output_extension), delete=False)
        temp_outfile.close()
        latex_conversion_directory = os.path.join(tempfile.gettempdir(), 'conv')
        if not os.path.isdir(latex_conversion_directory):
            os.makedirs(latex_conversion_directory, exist_ok=True)
        if not os.path.isdir(latex_conversion_directory):
            raise DAException("Could not create latex conversion directory")
        icc_profile_in_temp = os.path.join(tempfile.gettempdir(), 'sRGB_IEC61966-2-1_black_scaled.icc')
        if not os.path.isfile(icc_profile_in_temp):
            shutil.copyfile(docassemble.base.functions.standard_template_filename('sRGB_IEC61966-2-1_black_scaled.icc'), icc_profile_in_temp)
        subprocess_arguments = [PANDOC_PATH, PANDOC_ENGINE]
        if PANDOC_OLD:
            subprocess_arguments.append("--smart")
        subprocess_arguments.extend(['-M', 'latextmpdir=' + os.path.join('.', 'conv'), '-M', 'pdfa=' + ('true' if self.pdfa else 'false')])
        if len(yaml_to_use) > 0:
            subprocess_arguments.extend(yaml_to_use)
        if self.template_file is not None:
            subprocess_arguments.extend(['--template=%s' % self.template_file])
        if self.reference_file is not None:
            if PANDOC_OLD:
                subprocess_arguments.extend(['--reference-docx=%s' % self.reference_file])
            else:
                subprocess_arguments.extend(['--reference-doc=%s' % self.reference_file])
        if self.output_format in ('pdf', 'tex'):
            subprocess_arguments.extend(['--from=markdown+raw_tex-latex_macros'])
        subprocess_arguments.extend(['-s', '-o', temp_outfile.name])
        subprocess_arguments.extend([temp_file.name])
        subprocess_arguments.extend(self.arguments)
        # logmessage("Arguments are " + str(subprocess_arguments) + " and directory is " + tempfile.gettempdir())
        try:
            msg = subprocess.check_output(subprocess_arguments, cwd=tempfile.gettempdir(), stderr=subprocess.STDOUT).decode('utf-8', 'ignore')
        except subprocess.CalledProcessError as err:
            raise DAException("Failed to assemble file: " + err.output.decode())
        if msg:
            self.pandoc_message = msg
        os.remove(temp_file.name)
        if os.path.exists(temp_outfile.name):
            if self.output_format in ('rtf', 'rtf to docx'):
                with open(temp_outfile.name, encoding='utf-8') as the_file:
                    file_contents = the_file.read()
                # with open('/tmp/asdf.rtf', 'w') as deb_file:
                #     deb_file.write(file_contents)
                file_contents = docassemble.base.filter.rtf_filter(file_contents, metadata=metadata_as_dict, styles=get_rtf_styles(self.template_file), question=question)
                with open(temp_outfile.name, "wb") as the_file:
                    the_file.write(bytearray(file_contents, encoding='utf-8'))
                if self.output_format == 'rtf to docx':
                    docx_outfile = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
                    success = rtf_to_docx(temp_outfile.name, docx_outfile.name)
                    if not success:
                        raise DAException("Could not convert RTF to DOCX.")
                    temp_outfile = docx_outfile
            if self.output_filename is not None:
                shutil.copyfile(temp_outfile.name, self.output_filename)
            else:
                self.output_filename = temp_outfile.name
            self.output_content = None
            if self.output_format == 'pdf' and (self.password or self.owner_password):
                pdf_encrypt(self.output_filename, self.password, self.owner_password)
        else:
            raise IOError("Failed creating file: %s" % temp_outfile.name)

    def convert(self, question):
        latex_conversion_directory = os.path.join(tempfile.gettempdir(), 'conv')
        if not os.path.isdir(latex_conversion_directory):
            try:
                os.makedirs(latex_conversion_directory, exist_ok=True)
            except:
                pass
        if not os.path.isdir(latex_conversion_directory):
            raise DAException("Could not create latex conversion directory")
        if self.output_format in ("pdf", "tex", "rtf", "rtf to docx", "epub", "docx"):
            self.convert_to_file(question)
        else:
            subprocess_arguments = [PANDOC_PATH, PANDOC_ENGINE]
            if PANDOC_OLD:
                input_format = self.input_format
                subprocess_arguments.append("--smart")
            else:
                if self.input_format == 'markdown':
                    input_format = "markdown+smart"
                if self.output_format in ('pdf', 'tex'):
                    input_format += '+raw_tex-latex_macros'
            subprocess_arguments.extend(['-M', 'latextmpdir=' + os.path.join('.', 'conv'), '--from=%s' % input_format, '--to=%s' % self.output_format])
            if self.output_format == 'html':
                subprocess_arguments.append('--ascii')
            subprocess_arguments.extend(self.arguments)
            # logmessage("Arguments are " + str(subprocess_arguments))
            p = subprocess.Popen(
                subprocess_arguments,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                cwd=tempfile.gettempdir()
            )
            self.output_filename = None
            # logmessage("input content is a " + self.input_content.__class__.__name__)
            # with open('/tmp/moocow1', 'wb') as fp:
            #    fp.write(bytearray(self.input_content, encoding='utf-8'))
            self.output_content = p.communicate(bytearray(self.input_content, encoding='utf-8'))[0]
            # with open('/tmp/moocow2', 'wb') as fp:
            #    fp.write(self.output_content)
            self.output_content = self.output_content.decode()


def word_to_pdf(in_file, in_format, out_file, pdfa=False, password=None, owner_password=None, update_refs=False, tagged=False, filename=None, retry=True):
    if filename is None:
        filename = 'file'
    filename = docassemble.base.functions.secure_filename(filename)
    tempdir = tempfile.mkdtemp(prefix='SavedFile')
    from_file = os.path.join(tempdir, "file." + in_format)
    to_file = os.path.join(tempdir, "file.pdf")
    shutil.copyfile(in_file, from_file)
    tries = 0
    if pdfa:
        method = 'pdfa'
    elif tagged:
        method = 'tagged'
    else:
        method = 'default'
    if retry:
        num_tries = 5
    else:
        num_tries = 1
    while tries < num_tries:
        completed_process = None
        use_libreoffice = True
        if update_refs:
            if daconfig.get('gotenberg url', None) is not None:
                update_references(from_file)
                try:
                    gotenberg_to_pdf(from_file, to_file, pdfa, password, owner_password)
                    result = 0
                except BaseException as err:
                    logmessage("Call to gotenberg failed")
                    logmessage(err.__class__.__name__ + ": " + str(err))
                    result = 1
                use_libreoffice = False
                password = False
                owner_password = False
            elif daconfig.get('convertapi secret', None) is not None:
                update_references(from_file)
                try:
                    convertapi_to_pdf(from_file, to_file)
                    result = 0
                except BaseException as err:
                    logmessage("Call to convertapi failed")
                    logmessage(err.__class__.__name__ + ": " + str(err))
                    result = 1
                use_libreoffice = False
            elif daconfig.get('cloudconvert secret', None) is not None:
                update_references(from_file)
                try:
                    cloudconvert_to_pdf(in_format, from_file, to_file, pdfa, password)
                    result = 0
                except BaseException as err:
                    logmessage("Call to cloudconvert failed")
                    logmessage(err.__class__.__name__ + ": " + str(err))
                    result = 1
                use_libreoffice = False
                password = False
                owner_password = False
            else:
                if UNOCONV_AVAILABLE:
                    subprocess_arguments = [UNOCONV_PATH, '-f', 'pdf'] + UNOCONV_FILTERS[method] + ['-e', 'PDFViewSelection=2', '-o', to_file, from_file]
                else:
                    subprocess_arguments = [LIBREOFFICE_PATH, '--headless', '--invisible', 'macro:///Standard.Module1.ConvertToPdf(' + from_file + ',' + to_file + ',True,' + method + ')']
        elif daconfig.get('gotenberg url', None) is not None:
            try:
                gotenberg_to_pdf(from_file, to_file, pdfa, password, owner_password)
                result = 0
            except BaseException as err:
                logmessage("Call to gotenberg failed")
                logmessage(err.__class__.__name__ + ": " + str(err))
                result = 1
            use_libreoffice = False
            password = False
            owner_password = False
        elif daconfig.get('convertapi secret', None) is not None:
            try:
                convertapi_to_pdf(from_file, to_file)
                result = 0
            except:
                logmessage("Call to convertapi failed")
                result = 1
            use_libreoffice = False
        elif daconfig.get('cloudconvert secret', None) is not None:
            try:
                cloudconvert_to_pdf(in_format, from_file, to_file, pdfa, password)
                result = 0
            except BaseException as err:
                logmessage("Call to cloudconvert failed")
                logmessage(err.__class__.__name__ + ": " + str(err))
                result = 1
            use_libreoffice = False
            password = False
            owner_password = False
        else:
            if method == 'default':
                if UNOCONV_AVAILABLE:
                    subprocess_arguments = [UNOCONV_PATH, '-f', 'pdf'] + UNOCONV_FILTERS[method] + ['-e', 'PDFViewSelection=2', '-o', to_file, from_file]
                else:
                    subprocess_arguments = [LIBREOFFICE_PATH, '--headless', '--invisible', 'macro:///Standard.Module1.ConvertToPdf(' + from_file + ',' + to_file + ',False,' + method + ')']
            else:
                if UNOCONV_AVAILABLE:
                    subprocess_arguments = [UNOCONV_PATH, '-f', 'pdf'] + UNOCONV_FILTERS[method] + ['-e', 'PDFViewSelection=2', '-o', to_file, from_file]
                else:
                    subprocess_arguments = [LIBREOFFICE_PATH, '--headless', '--invisible', 'macro:///Standard.Module1.ConvertToPdf(' + from_file + ',' + to_file + ',False,' + method + ')']
        if use_libreoffice:
            start_time = time.time()
            if UNOCONV_AVAILABLE:
                docassemble.base.functions.server.applock('obtain', 'unoconv', maxtime=6)
                logmessage("Trying unoconv with " + repr(subprocess_arguments))
                try:
                    completed_process = subprocess.run(subprocess_arguments, cwd=tempdir, timeout=120, check=False, capture_output=True)
                    result = completed_process.returncode
                except subprocess.TimeoutExpired:
                    logmessage("word_to_pdf: unoconv took too long")
                    result = 1
                    tries = 5
                docassemble.base.functions.server.applock('release', 'unoconv', maxtime=6)
                logmessage("Finished unoconv after {:.4f} seconds.".format(time.time() - start_time))
            else:
                initialize_libreoffice()
                logmessage("Trying libreoffice with " + repr(subprocess_arguments))
                docassemble.base.functions.server.applock('obtain', 'libreoffice')
                logmessage("Obtained libreoffice lock after {:.4f} seconds.".format(time.time() - start_time))
                try:
                    completed_process = subprocess.run(subprocess_arguments, cwd=tempdir, timeout=120, check=False, capture_output=True)
                    result = completed_process.returncode
                except subprocess.TimeoutExpired:
                    logmessage("word_to_pdf: libreoffice took too long")
                    result = 1
                    tries = 5
                logmessage("Finished libreoffice after {:.4f} seconds.".format(time.time() - start_time))
                docassemble.base.functions.server.applock('release', 'libreoffice')
        if result == 0:
            time.sleep(0.1)
            if os.path.isfile(to_file) and os.path.getsize(to_file) > 0:
                break
            time.sleep(0.1)
            if os.path.isfile(to_file) and os.path.getsize(to_file) > 0:
                break
            time.sleep(0.1)
            if os.path.isfile(to_file) and os.path.getsize(to_file) > 0:
                break
            time.sleep(0.1)
            if os.path.isfile(to_file) and os.path.getsize(to_file) > 0:
                break
            time.sleep(0.1)
            if os.path.isfile(to_file) and os.path.getsize(to_file) > 0:
                break
            result = 1
        tries += 1
        if tries < num_tries:
            if use_libreoffice:
                error_msg = (f": {completed_process.stderr}") if completed_process else ""
                if UNOCONV_AVAILABLE:
                    logmessage(f"Didn't get file ({error_msg}), Retrying unoconv with " + repr(subprocess_arguments))
                else:
                    logmessage(f"Didn't get file ({error_msg}), Retrying libreoffice with " + repr(subprocess_arguments))
            elif daconfig.get('gotenberg url', None) is not None:
                logmessage("Retrying gotenberg")
            elif daconfig.get('convertapi secret', None) is not None:
                logmessage("Retrying convertapi")
            else:
                logmessage("Retrying cloudconvert")
            time.sleep(tries*random.random())
    if os.path.isfile(to_file) and os.path.getsize(to_file) == 0:
        result = 1
    if result == 0:
        if password:
            pdf_encrypt(to_file, password, owner_password)
        shutil.copyfile(to_file, out_file)
    if tempdir is not None:
        shutil.rmtree(tempdir)
    if result != 0:
        return False
    return True


def rtf_to_docx(in_file, out_file):
    tempdir = tempfile.mkdtemp(prefix='SavedFile')
    from_file = os.path.join(tempdir, "file.rtf")
    to_file = os.path.join(tempdir, "file.docx")
    shutil.copyfile(in_file, from_file)
    if UNOCONV_AVAILABLE:
        subprocess_arguments = [UNOCONV_PATH, '-f', 'docx', '-o', to_file, from_file]
    else:
        initialize_libreoffice()
        subprocess_arguments = [LIBREOFFICE_PATH, '--headless', '--invisible', '--convert-to', 'docx', from_file, '--outdir', tempdir]
    # logmessage("rtf_to_docx: creating " + to_file + " by doing " + " ".join(subprocess_arguments))
    tries = 0
    while tries < 5:
        if UNOCONV_AVAILABLE:
            try:
                result = subprocess.run(subprocess_arguments, cwd=tempdir, timeout=120, check=False).returncode
            except subprocess.TimeoutExpired:
                logmessage("rtf_to_docx: call to unoconv took too long")
                result = 1
                tries = 5
            if result != 0:
                logmessage("rtf_to_docx: call to unoconv returned non-zero response")
        else:
            docassemble.base.functions.server.applock('obtain', 'libreoffice')
            try:
                result = subprocess.run(subprocess_arguments, cwd=tempdir, timeout=120, check=False).returncode
            except subprocess.TimeoutExpired:
                logmessage("rtf_to_docx: call to LibreOffice took too long")
                result = 1
                tries = 5
            docassemble.base.functions.server.applock('release', 'libreoffice')
            if result != 0:
                logmessage("rtf_to_docx: call to LibreOffice returned non-zero response")
        if result == 0 and os.path.isfile(to_file):
            break
        result = 1
        tries += 1
        if tries < 5:
            if UNOCONV_AVAILABLE:
                logmessage("rtf_to_docx: retrying unoconv")
            else:
                logmessage("rtf_to_docx: retrying LibreOffice")
            time.sleep(0.5 + tries*random.random())
    if result == 0:
        shutil.copyfile(to_file, out_file)
    if tempdir is not None:
        shutil.rmtree(tempdir)
    if result != 0:
        return False
    return True


def convert_file(in_file, out_file, input_extension, output_extension):
    if not UNOCONV_AVAILABLE:
        initialize_libreoffice()
    tempdir1 = tempfile.mkdtemp(prefix='SavedFile')
    tempdir2 = tempfile.mkdtemp(prefix='SavedFile')
    from_file = os.path.join(tempdir1, "file." + input_extension)
    to_file = os.path.join(tempdir2, "file." + output_extension)
    shutil.copyfile(in_file, from_file)
    if UNOCONV_AVAILABLE:
        subprocess_arguments = [UNOCONV_PATH, '-f', output_extension, '-o', to_file, from_file]
    else:
        subprocess_arguments = [LIBREOFFICE_PATH, '--headless', '--invisible', '--convert-to', output_extension, from_file, '--outdir', tempdir2]
    # logmessage("convert_to: creating " + to_file + " by doing " + " ".join(subprocess_arguments))
    tries = 0
    while tries < 5:
        if UNOCONV_AVAILABLE:
            try:
                result = subprocess.run(subprocess_arguments, cwd=tempdir1, timeout=120, check=False).returncode
            except subprocess.TimeoutExpired:
                logmessage("convert_file: unoconv took too long")
                result = 1
                tries = 5
            if result != 0:
                logmessage("convert_file: call to unoconv returned non-zero response")
        else:
            docassemble.base.functions.server.applock('obtain', 'libreoffice')
            try:
                result = subprocess.run(subprocess_arguments, cwd=tempdir1, timeout=120, check=False).returncode
            except subprocess.TimeoutExpired:
                logmessage("convert_file: libreoffice took too long")
                result = 1
                tries = 5
            docassemble.base.functions.server.applock('release', 'libreoffice')
            if result != 0:
                logmessage("convert_file: call to LibreOffice returned non-zero response")
        if result == 0 and os.path.isfile(to_file):
            break
        result = 1
        tries += 1
        if tries < 5:
            if UNOCONV_AVAILABLE:
                logmessage("convert_file: retrying unoconv")
            else:
                logmessage("convert_file: retrying libreoffice")
            time.sleep(0.5 + tries*random.random())
    if result == 0:
        shutil.copyfile(to_file, out_file)
    if tempdir1 is not None:
        shutil.rmtree(tempdir1)
    if tempdir2 is not None:
        shutil.rmtree(tempdir2)
    if result != 0:
        return False
    return True


def word_to_markdown(in_file, in_format):
    if not UNOCONV_AVAILABLE:
        initialize_libreoffice()
    temp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".md")
    if in_format not in ['docx', 'odt']:
        tempdir = tempfile.mkdtemp(prefix='SavedFile')
        from_file = os.path.join(tempdir, "file." + in_format)
        to_file = os.path.join(tempdir, "file.docx")
        shutil.copyfile(in_file, from_file)
        if UNOCONV_AVAILABLE:
            subprocess_arguments = [UNOCONV_PATH, '-f', 'docx', '-o', to_file, from_file]
        else:
            subprocess_arguments = [LIBREOFFICE_PATH, '--headless', '--invisible', '--convert-to', 'docx', from_file, '--outdir', tempdir]
        tries = 0
        while tries < 5:
            if UNOCONV_AVAILABLE:
                if tries > 0:
                    logmessage("word_to_markdown: retrying unoconv")
                try:
                    result = subprocess.run(subprocess_arguments, cwd=tempdir, timeout=120, check=False).returncode
                except subprocess.TimeoutExpired:
                    logmessage("word_to_markdown: unoconv took too long")
                    result = 1
                    tries = 5
                if result != 0:
                    logmessage("word_to_markdown: call to unoconv returned non-zero response")
            else:
                docassemble.base.functions.server.applock('obtain', 'libreoffice')
                try:
                    result = subprocess.run(subprocess_arguments, cwd=tempdir, timeout=120, check=False).returncode
                except subprocess.TimeoutExpired:
                    logmessage("word_to_markdown: libreoffice took too long")
                    result = 1
                    tries = 5
                docassemble.base.functions.server.applock('release', 'libreoffice')
                if result != 0:
                    logmessage("word_to_markdown: call to LibreOffice returned non-zero response")
            if result == 0 and os.path.isfile(to_file):
                break
            result = 1
            tries += 1
            if tries < 5:
                if UNOCONV_AVAILABLE:
                    logmessage("word_to_markdown: retrying unoconv")
                else:
                    logmessage("word_to_markdown: retrying LibreOffice")
                time.sleep(0.5 + tries*random.random())
        if result != 0:
            return None
        in_file_to_use = to_file
        in_format_to_use = 'docx'
    else:
        in_file_to_use = in_file
        in_format_to_use = in_format
        tempdir = None
    subprocess_arguments = [PANDOC_PATH, PANDOC_ENGINE]
    if PANDOC_OLD:
        subprocess_arguments.append("--smart")
    else:
        if in_format_to_use == 'markdown':
            in_format_to_use = "markdown+smart"
    subprocess_arguments.extend(['--from=%s' % str(in_format_to_use), '--to=markdown_phpextra', str(in_file_to_use), '-o', str(temp_file.name)])
    try:
        result = subprocess.run(subprocess_arguments, timeout=60, check=False).returncode
    except subprocess.TimeoutExpired:
        result = 1
    if tempdir is not None:
        shutil.rmtree(tempdir)
    if result == 0:
        final_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".md")
        with open(temp_file.name, 'r', encoding='utf-8') as the_file:
            file_contents = the_file.read()
        file_contents = re.sub(r'\\([\$\[\]])', lambda x: x.group(1), file_contents)
        with open(final_file.name, "w", encoding='utf-8') as the_file:
            the_file.write(file_contents)
        return final_file
    return None


def get_rtf_styles(filename):
    file_contents = ''
    styles = {}
    with open(filename, 'r', encoding='utf-8') as the_file:
        file_contents = the_file.read()
        for (style_string, style_number, heading_number) in re.findall(style_find, file_contents):  # pylint: disable=unused-variable
            style_string = re.sub(r'\s+', ' ', style_string, flags=re.DOTALL)
            # logmessage("heading " + str(heading_number) + " is style " + str(style_number))
            styles[heading_number] = style_string
    return styles


def update_references(filename):
    if UNOCONV_AVAILABLE:
        with tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False) as temp_file:
            logmessage("update_references: converting docx to docx")
            result = convert_file(filename, temp_file.name, 'docx', 'docx')
            if result:
                shutil.copyfile(temp_file.name, filename)
        return result
    initialize_libreoffice()
    subprocess_arguments = [LIBREOFFICE_PATH, '--headless', '--invisible', 'macro:///Standard.Module1.PysIndexer(' + filename + ')']
    tries = 0
    while tries < 5:
        docassemble.base.functions.server.applock('obtain', 'libreoffice')
        try:
            result = subprocess.run(subprocess_arguments, cwd=tempfile.gettempdir(), timeout=120, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
            tries = 5
        docassemble.base.functions.server.applock('release', 'libreoffice')
        if result == 0:
            break
        logmessage("update_references: call to LibreOffice returned non-zero response")
        tries += 1
        if tries < 5:
            logmessage("update_references: retrying LibreOffice")
            time.sleep(0.5 + tries*random.random())
    if result != 0:
        return False
    return True


def initialize_libreoffice():
    global LIBREOFFICE_INITIALIZED
    if LIBREOFFICE_INITIALIZED:
        return
    LIBREOFFICE_INITIALIZED = True
    if not os.path.isfile(LIBREOFFICE_MACRO_PATH):
        logmessage("No LibreOffice macro path exists")
        temp_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf")
        word_file = docassemble.base.functions.package_template_filename('docassemble.demo:data/templates/template_test.docx')
        word_to_pdf(word_file, 'docx', temp_file.name, pdfa=False, password=None, owner_password=None, retry=False)
        del temp_file
        del word_file
    orig_path = docassemble.base.functions.package_template_filename('docassemble.base:data/macros/Module1.xba')
    try:
        assert os.path.isdir(os.path.dirname(LIBREOFFICE_MACRO_PATH))
        # logmessage("Copying LibreOffice macro from " + orig_path)
        copy_if_different(orig_path, LIBREOFFICE_MACRO_PATH)
    except:
        logmessage("Could not copy LibreOffice macro into place")


def concatenate_files(path_list, pdfa=False, password=None, owner_password=None):
    pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
    new_path_list = []
    for path in path_list:
        mimetype, encoding = mimetypes.guess_type(path)  # pylint: disable=unused-variable
        if mimetype.startswith('image'):
            new_pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
            args = [daconfig.get('imagemagick', 'convert')]
            if mimetype == 'image/tiff':
                args += ['-compress', 'LZW']
            args += [path, new_pdf_file.name]
            try:
                result = subprocess.run(args, timeout=60, check=False).returncode
            except subprocess.TimeoutExpired:
                logmessage("concatenate_files: convert took too long")
                result = 1
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
            if not word_to_pdf(path, ext, new_pdf_file.name, pdfa=False):
                raise DAException('Failure to convert DOCX to PDF')
            new_path_list.append(new_pdf_file.name)
        elif mimetype == 'application/pdf':
            new_path_list.append(path)
    if len(new_path_list) == 0:
        raise DAError("concatenate_files: no valid files to concatenate")

    if len(new_path_list) == 1:
        shutil.copyfile(new_path_list[0], pdf_file.name)
    else:
        with Pdf.open(new_path_list[0]) as original:
            need_appearances = False
            try:
                if original.Root.AcroForm.NeedAppearances:
                    need_appearances = True
            except:
                pass
            for additional_file in new_path_list[1:]:
                with Pdf.open(additional_file) as additional_pdf:
                    if need_appearances is False:
                        try:
                            if additional_pdf.Root.AcroForm.NeedAppearances:
                                need_appearances = True
                        except:
                            pass
                    original.pages.extend(additional_pdf.pages)
            if need_appearances:
                try:
                    original.Root.AcroForm.NeedAppearances = True
                except:
                    logmessage("concatenate_files: an additional file had an AcroForm with NeedAppearances but setting NeedAppearances on the final document resulted in an error")
            original.save(pdf_file.name)
    if pdfa:
        pdf_to_pdfa(pdf_file.name)
    if password or owner_password:
        pdf_encrypt(pdf_file.name, password, owner_password)
    return pdf_file.name
