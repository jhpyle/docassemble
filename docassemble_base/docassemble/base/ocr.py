import tempfile
import subprocess
from PIL import Image, ImageEnhance
from docassemble.base.functions import get_config, get_language, ReturnValue
from docassemble.base.core import DAFile, DAFileList, DAFileCollection, DAStaticFile
import PyPDF2
from docassemble.base.logger import logmessage
from docassemble.base.error import DAError
import pycountry
import sys
import os
import shutil
import re

QPDF_PATH = 'qpdf'

def safe_pypdf_reader(filename):
    try:
        return PyPDF2.PdfFileReader(open(filename, 'rb'))
    except PyPDF2.utils.PdfReadError:
        new_filename = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".pdf", delete=False)
        qpdf_subprocess_arguments = [QPDF_PATH, filename, new_filename.name]
        try:
            result = subprocess.run(qpdf_subprocess_arguments, timeout=60).returncode
        except subprocess.TimeoutExpired:
            result = 1
        if result != 0:
            raise Exception("Call to qpdf failed for template " + str(filename) + " where arguments were " + " ".join(qpdf_subprocess_arguments))
        return PyPDF2.PdfFileReader(open(new_filename.name, 'rb'))

def ocr_finalize(*pargs, **kwargs):
    #sys.stderr.write("ocr_finalize started")
    if kwargs.get('pdf', False):
        target = kwargs['target']
        dafilelist = kwargs['dafilelist']
        filename = kwargs['filename']
        file_list = []
        input_number = target.number
        for parg in pargs:
            if type(parg) is list:
                for item in parg:
                    if type(item) is ReturnValue:
                        if isinstance(item.value, dict):
                            if 'page' in item.value:
                                file_list.append([item.value['indexno'], int(item.value['page']), item.value['doc']._pdf_page_path(int(item.value['page']))])
                            else:
                                file_list.append([item.value['indexno'], 0, item.value['doc'].path()])
            else:
                if type(parg) is ReturnValue:
                    if isinstance(item.value, dict):
                        if 'page' in item.value:
                            file_list.append([parg.value['indexno'], int(parg.value['page']), parg.value['doc']._pdf_page_path(int(parg.value['page']))])
                        else:
                            file_list.append([parg.value['indexno'], 0, parg.value['doc'].path()])
        from docassemble.base.pandoc import concatenate_files
        pdf_path = concatenate_files([y[2] for y in sorted(file_list, key=lambda x: x[0]*10000 + x[1])])
        target.initialize(filename=filename, extension='pdf', mimetype='application/pdf', reinitialize=True)
        shutil.copyfile(pdf_path, target.file_info['path'])
        del target.file_info
        target._make_pdf_thumbnail(1, both_formats=True)
        target.commit()
        target.retrieve()
        return (target, dafilelist)
    output = dict()
    #index = 0
    for parg in pargs:
        #sys.stderr.write("ocr_finalize: index " + str(index) + " is a " + str(type(parg)) + "\n")
        if type(parg) is list:
            for item in parg:
                #sys.stderr.write("ocr_finalize: sub item is a " + str(type(item)) + "\n")
                if type(item) is ReturnValue and isinstance(item.value, dict):
                    output[int(item.value['page'])] = item.value['text']
        else:
            if type(parg) is ReturnValue and isinstance(item.value, dict):
                output[int(parg.value['page'])] = parg.value['text']
        #index += 1
    #sys.stderr.write("ocr_finalize: assembling output\n")
    final_output = "\f".join([output[x] for x in sorted(output.keys())])
    #sys.stderr.write("ocr_finalize: final output has length " + str(len(final_output)) + "\n")
    return final_output

def get_ocr_language(language):
    langs = get_available_languages()
    if language is None:
        language = get_language()
    ocr_langs = get_config("ocr languages")
    if ocr_langs is None:
        ocr_langs = dict()
    if language in langs:
        lang = language
    else:
        if language in ocr_langs and ocr_langs[language] in langs:
            lang = ocr_langs[language]
        else:
            try:
                pc_lang = pycountry.languages.get(alpha_2=language)
                lang_three_letter = pc_lang.alpha_3
                if lang_three_letter in langs:
                    lang = lang_three_letter
                else:
                    if 'eng' in langs:
                        lang = 'eng'
                    else:
                        lang = langs[0]
                    raise Exception("could not get OCR language for language " + str(language) + "; using language " + str(lang))
            except Exception as the_error:
                if 'eng' in langs:
                    lang = 'eng'
                else:
                    lang = langs[0]
                raise Exception("could not get OCR language for language " + str(language) + "; using language " + str(lang) + "; error was " + str(the_error))
    return lang

def get_available_languages():
    try:
        output = subprocess.check_output(['tesseract', '--list-langs'], stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as err:
        raise Exception("get_available_languages: failed to list available languages: " + str(err))
    else:
        result = output.splitlines()
        result.pop(0)
        return result

def ocr_page_tasks(image_file, language=None, psm=6, x=None, y=None, W=None, H=None, user_code=None, user=None, pdf=False, preserve_color=False, **kwargs):
    #sys.stderr.write("ocr_page_tasks running\n")
    if isinstance(image_file, set):
        return []
    if not (isinstance(image_file, DAFile) or isinstance(image_file, DAFileList)):
        return word("(Not a DAFile or DAFileList object)")
    pdf_to_ppm = get_config("pdftoppm")
    if pdf_to_ppm is None:
        pdf_to_ppm = 'pdftoppm'
    ocr_resolution = get_config("ocr dpi")
    if ocr_resolution is None:
        ocr_resolution = '300'
    langs = get_available_languages()
    if language is None:
        language = get_language()
    if language in langs:
        lang = language
    else:
        ocr_langs = get_config("ocr languages")
        if ocr_langs is None:
            ocr_langs = dict()
        if language in ocr_langs and ocr_langs[language] in langs:
            lang = ocr_langs[language]
        else:
            try:
                pc_lang = pycountry.languages.get(alpha_2=language)
                lang_three_letter = pc_lang.alpha_3
                if lang_three_letter in langs:
                    lang = lang_three_letter
                else:
                    if 'eng' in langs:
                        lang = 'eng'
                    else:
                        lang = langs[0]
                    sys.stderr.write("ocr_file: could not get OCR language for language " + str(language) + "; using language " + str(lang) + "\n")
            except Exception as the_error:
                if 'eng' in langs:
                    lang = 'eng'
                else:
                    lang = langs[0]
                sys.stderr.write("ocr_file: could not get OCR language for language " + str(language) + "; using language " + str(lang) + "; error was " + str(the_error) + "\n")
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    todo = list()
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif', 'docx', 'doc', 'odt', 'rtf']:
                raise Exception("document with extension " + doc.extension + " is not a readable image file")
            if doc.extension == 'pdf':
                #doc.page_path(1, 'page')
                for i in range(safe_pypdf_reader(doc.path()).getNumPages()):
                    todo.append(dict(doc=doc, page=i+1, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code, user=user, pdf=pdf, preserve_color=preserve_color))
            elif doc.extension in ("docx", "doc", "odt", "rtf"):
                import docassemble.base.util
                doc_conv = docassemble.base.util.pdf_concatenate(doc)
                for i in range(safe_pypdf_reader(doc_conv.path()).getNumPages()):
                    todo.append(dict(doc=doc_conv, page=i+1, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code, user=user, pdf=pdf, preserve_color=preserve_color))
            else:
                todo.append(dict(doc=doc, page=None, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code, user=user, pdf=pdf, preserve_color=preserve_color))
    #sys.stderr.write("ocr_page_tasks finished\n")
    return todo

def make_png_for_pdf(doc, prefix, resolution, pdf_to_ppm, page=None):
    path = doc.path()
    make_png_for_pdf_path(path, prefix, resolution, pdf_to_ppm, page=page)
    doc.commit()

def make_png_for_pdf_path(path, prefix, resolution, pdf_to_ppm, page=None):
    basefile = os.path.splitext(path)[0]
    test_path = basefile + prefix + '-in-progress'
    with open(test_path, 'a'):
        os.utime(test_path, None)
    if page is None:
        try:
            result = subprocess.run([str(pdf_to_ppm), '-r', str(resolution), '-png', str(path), str(basefile + prefix)], timeout=3600).returncode
        except subprocess.TimeoutExpired:
            result = 1
    else:
        try:
            result = subprocess.run([str(pdf_to_ppm), '-f', str(page), '-l', str(page), '-r', str(resolution), '-png', str(path), str(basefile + prefix)], timeout=3600).returncode
        except subprocess.TimeoutExpired:
            result = 1
    if os.path.isfile(test_path):
        os.remove(test_path)
    if result > 0:
        raise Exception("Unable to extract images from PDF file")

def ocr_pdf(*pargs, target=None, filename=None, lang=None, psm=6, dafilelist=None, preserve_color=False):
    if preserve_color:
        device = 'tiff48nc'
    else:
        device = 'tiffgray'
    docs = []
    if not isinstance(target, DAFile):
        raise DAError("ocr_pdf: target must be a DAFile")
    for other_file in pargs:
        if isinstance(other_file, DAFileList):
            for other_file_sub in other_file.elements:
                docs.append(other_file_sub)
        elif isinstance(other_file, DAFileCollection):
            if hasattr(other_file, 'pdf'):
                docs.append(other_file.pdf)
            elif hasattr(other_file, 'docx'):
                docs.append(other_file.docx)
            else:
                raise DAError('ocr_pdf: DAFileCollection object did not have pdf or docx attribute.')
        elif isinstance(other_file, DAStaticFile):
            docs.append(other_file)
        elif isinstance(other_file, (str, DAFile)):
            docs.append(other_file)
    if len(docs) == 0:
        docs.append(target)
    if psm is None:
        psm = 6
    output = []
    for doc in docs:
        if not hasattr(doc, 'extension'):
            continue
        if doc._is_pdf() and hasattr(doc, 'has_ocr') and doc.has_ocr:
            output.append(doc.path())
            continue
        if doc.extension in ['png', 'jpg', 'gif']:
            import docassemble.base.util
            doc = docassemble.base.util.pdf_concatenate(doc)
        elif doc.extension in ['docx', 'doc', 'odt', 'rtf']:
            import docassemble.base.util
            output.append(docassemble.base.util.pdf_concatenate(doc).path())
            continue
        elif not doc._is_pdf():
            logmessage("ocr_pdf: not a readable image file")
            continue
        path = doc.path()
        pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
        pdf_file.close()
        if doc.extension == 'pdf':
            tiff_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".tiff", delete=False)
            params = ['gs', '-q', '-dNOPAUSE', '-sDEVICE=' + device, '-r600', '-sOutputFile=' + tiff_file.name, path, '-c', 'quit']
            try:
                result = subprocess.run(params, timeout=60*60).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("ocr_pdf: call to gs took too long")
            if result != 0:
                raise Exception("ocr_pdf: failed to run gs with command " + " ".join(params))
            params = ['tesseract', tiff_file.name, pdf_file.name, '-l', str(lang), '--psm', str(psm), '--dpi', '600', 'pdf']
            try:
                result = subprocess.run(params, timeout=60*60).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("ocr_pdf: call to tesseract took too long")
            if result != 0:
                raise Exception("ocr_pdf: failed to run tesseract with command " + " ".join(params))
        else:
            params = ['tesseract', path, pdf_file.name, '-l', str(lang), '--psm', str(psm), '--dpi', '300', 'pdf']
            try:
                result = subprocess.run(params, timeout=60*60).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("ocr_pdf: call to tesseract took too long")
            if result != 0:
                raise Exception("ocr_pdf: failed to run tesseract with command " + " ".join(params))
        output.append(pdf_file.name + '.pdf')
    if len(output) == 0:
        return None
    if len(output) == 1:
        the_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
        the_file.close()
        shutil.copyfile(output[0], the_file.name)
        source_file = the_file.name
    else:
        import docassemble.base.pandoc
        source_file = docassemble.base.pandoc.concatenate_files(output)
    if filename is None:
        filename = 'file.pdf'
    target.initialize(filename=filename, extension='pdf', mimetype='application/pdf', reinitialize=True)
    shutil.copyfile(source_file, target.file_info['path'])
    del target.file_info
    target._make_pdf_thumbnail(1, both_formats=True)
    target.commit()
    target.retrieve()
    return target

def ocr_page(indexno, doc=None, lang=None, pdf_to_ppm='pdf_to_ppm', ocr_resolution=300, psm=6, page=None, x=None, y=None, W=None, H=None, user_code=None, user=None, pdf=False, preserve_color=False):
    """Runs optical character recognition on an image or a page of a PDF file and returns the recognized text."""
    if page is None:
        page = 1
    if psm is None:
        psm = 6
    sys.stderr.write("ocr_page running on page " + str(page) + "\n")
    the_file = None
    if not hasattr(doc, 'extension'):
        return None
    #sys.stderr.write("ocr_page running with extension " + str(doc.extension) + "\n")
    if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
        raise Exception("Not a readable image file")
    #sys.stderr.write("ocr_page calling doc.path()\n")
    path = doc.path()
    if doc.extension == 'pdf':
        the_file = None
        if x is None and y is None and W is None and H is None:
            the_file = doc.page_path(page, 'page', wait=False)
        if the_file is None:
            output_file = tempfile.NamedTemporaryFile()
            args = [str(pdf_to_ppm), '-r', str(ocr_resolution), '-f', str(page), '-l', str(page)]
            if x is not None:
                args.extend(['-x', str(x)])
            if y is not None:
                args.extend(['-y', str(y)])
            if W is not None:
                args.extend(['-W', str(W)])
            if H is not None:
                args.extend(['-H', str(H)])
            args.extend(['-singlefile', '-png', str(path), str(output_file.name)])
            try:
                result = subprocess.run(args, timeout=120).returncode
            except subprocess.TimeoutExpired:
                result = 1
            if result > 0:
                return word("(Unable to extract images from PDF file)")
            the_file = output_file.name + '.png'
    else:
        the_file = path
    file_to_read = tempfile.NamedTemporaryFile()
    if pdf and preserve_color:
        shutil.copyfile(the_file, file_to_read.name)
    else:
        image = Image.open(the_file)
        color = ImageEnhance.Color(image)
        bw = color.enhance(0.0)
        bright = ImageEnhance.Brightness(bw)
        brightened = bright.enhance(1.5)
        contrast = ImageEnhance.Contrast(brightened)
        final_image = contrast.enhance(2.0)
        file_to_read = tempfile.TemporaryFile()
        final_image.convert('RGBA').save(file_to_read, "PNG")
    file_to_read.seek(0)
    if pdf:
        outfile = doc._pdf_page_path(page)
        params = ['tesseract', 'stdin', re.sub(r'\.pdf$', '', outfile), '-l', str(lang), '--psm', str(psm), '--dpi', str(ocr_resolution), 'pdf']
        sys.stderr.write("ocr_page: piping to command " + " ".join(params) + "\n")
        try:
            text = subprocess.check_output(params, stdin=file_to_read).decode()
        except subprocess.CalledProcessError as err:
            raise Exception("ocr_page: failed to run tesseract with command " + " ".join(params) + ": " + str(err) + " " + str(err.output.decode()))
        sys.stderr.write("ocr_page finished with pdf page " + str(page) + "\n")
        doc.commit()
        return dict(indexno=indexno, page=page, doc=doc)
    params = ['tesseract', 'stdin', 'stdout', '-l', str(lang), '--psm', str(psm), '--dpi', str(ocr_resolution)]
    sys.stderr.write("ocr_page: piping to command " + " ".join(params) + "\n")
    try:
        text = subprocess.check_output(params, stdin=file_to_read).decode()
    except subprocess.CalledProcessError as err:
        raise Exception("ocr_page: failed to run tesseract with command " + " ".join(params) + ": " + str(err) + " " + str(err.output.decode()))
    sys.stderr.write("ocr_page finished with page " + str(page) + "\n")
    return dict(indexno=indexno, page=page, text=text)
