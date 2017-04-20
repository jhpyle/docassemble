import pyocr
import pyocr.builders
import tempfile
from subprocess import call
from PIL import Image, ImageEnhance
from docassemble.base.functions import get_config, get_language, ReturnValue
from docassemble.base.core import DAFile, DAFileList
from pyPdf import PdfFileReader
import sys
import os

def ocr_finalize(*pargs, **kwargs):
    #sys.stderr.write("ocr_finalize started")
    output = dict()
    index = 0
    for parg in pargs:
        #sys.stderr.write("ocr_finalize: index " + str(index) + " is a " + str(type(parg)) + "\n")
        if type(parg) is list:
            for item in parg:
                #sys.stderr.write("ocr_finalize: sub item is a " + str(type(item)) + "\n")
                if type(item) is ReturnValue:
                    output[int(item.value['page'])] = item.value['text']
        else:
            if type(parg) is ReturnValue:
                output[int(parg.value['page'])] = parg.value['text']
        index += 1
    #sys.stderr.write("ocr_finalize: assembling output\n")
    final_output = "\f".join([output[x] for x in sorted(output.keys())])
    #sys.stderr.write("ocr_finalize: final output has length " + str(len(final_output)) + "\n")
    return final_output

def ocr_page_tasks(image_file, language=None, psm=6, x=None, y=None, W=None, H=None, user_code=None, **kwargs):
    #sys.stderr.write("ocr_page_tasks running\n")
    if not (isinstance(image_file, DAFile) or isinstance(image_file, DAFileList)):
        return word("(Not a DAFile or DAFileList object)")
    pdf_to_ppm = get_config("pdftoppm")
    if pdf_to_ppm is None:
        pdf_to_ppm = 'pdftoppm'
    ocr_resolution = get_config("ocr dpi")
    if ocr_resolution is None:
        ocr_resolution = '300'
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        return word('(OCR engine not available)')
    tool = tools[0]
    langs = tool.get_available_languages()
    if language is None:
        language = get_language()
    ocr_langs = get_config("ocr languages")
    if ocr_langs is None:
        ocr_langs = dict()
    if language in ocr_langs and ocr_langs[language] in langs:
        lang = ocr_langs[language]
    else:
        lang = langs[0]
        logmessage("ocr_file: could not get OCR language for language " + str(language) + "; using language " + str(lang))
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    todo = list()
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
                raise Exception("document with extension " + doc.extension + " is not a readable image file")
            if doc.extension == 'pdf':
                #doc.page_path(1, 'page')
                for i in xrange(PdfFileReader(open(doc.path(), 'rb')).getNumPages()):
                    todo.append(dict(doc=doc, page=i+1, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code))
            else:
                todo.append(dict(doc=doc, page=None, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code))
    #sys.stderr.write("ocr_page_tasks finished\n")
    return todo

def make_png_for_pdf(doc, prefix, resolution, pdf_to_ppm):
    path = doc.path()
    basefile = os.path.splitext(path)[0]
    test_path = basefile + prefix + '-in-progress'
    with open(test_path, 'a'):
        os.utime(test_path, None)
    result = call([str(pdf_to_ppm), '-r', str(resolution), '-png', str(path), str(basefile + prefix)])
    os.remove(test_path)
    if result > 0:
        raise Exception("Unable to extract images from PDF file")
    doc.commit()
    return

def ocr_page(doc=None, lang=None, pdf_to_ppm='pdf_to_ppm', ocr_resolution=300, psm=6, page=None, x=None, y=None, W=None, H=None, user_code=None):
    """Runs optical character recognition on an image or a page of a PDF file and returns the recognized text."""
    if page is None:
        page = 1
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
            result = call(args)
            if result > 0:
                return word("(Unable to extract images from PDF file)")
            the_file = output_file.name + '.png'
    else:
        the_file = path
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        return word('(OCR engine not available)')
    tool = tools[0]
    image = Image.open(the_file)
    color = ImageEnhance.Color(image)
    bw = color.enhance(0.0)
    bright = ImageEnhance.Brightness(bw)
    brightened = bright.enhance(1.5)
    contrast = ImageEnhance.Contrast(brightened)
    final_image = contrast.enhance(2.0)
    text = tool.image_to_string(final_image, lang=lang, builder=pyocr.builders.TextBuilder(tesseract_layout=psm))
    sys.stderr.write("ocr_page finished with page " + str(page) + "\n")
    return dict(page=page, text=text)

