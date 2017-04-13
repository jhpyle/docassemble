import pyocr
import pyocr.builders
import tempfile
from subprocess import call
from PIL import Image, ImageEnhance
from docassemble.base.functions import get_config
from docassemble.base.core import DAFile, DAFileList
from pyPdf import PdfFileReader

def ocr_page_tasks(image_file, language=None, psm=6, x=None, y=None, W=None, H=None):
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
                return word("(Not a readable image file)")
            if doc.extension == 'pdf':
                for i in xrange(PdfFileReader(open(path, 'rb')).getNumPages()):
                    todo.append(dict(doc=doc, page=i+1, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm))
            else:
                todo.append(dict(doc=doc, page=None, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm))
    return todo

def ocr_page(doc=None, lang=None, pdf_to_ppm='pdf_to_ppm', ocr_resolution=300, psm=6, page=None, x=None, y=None, W=None, H=None):
    """Runs optical character recognition on an image or a page of a PDF file and returns the recognized text."""
    if page is None:
        page = 1
    temp_directory_list = list()
    file_list = list()
    if hasattr(doc, 'extension'):
        if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
            raise Exception("Not a readable image file")
        path = doc.path()
        if doc.extension == 'pdf':
            output_file = tempfile.NamedTemporaryFile()
            args = [pdf_to_ppm, '-r', str(ocr_resolution), '-f', str(page), '-l', str(page)]
            if x is not None:
                args.extend(['-x', str(x)])
            if y is not None:
                args.extend(['-y', str(y)])
            if W is not None:
                args.extend(['-W', str(W)])
            if H is not None:
                args.extend(['-H', str(H)])
            args.extend(['-singlefile', '-png', path, prefix])
            result = call(args)
            if result > 0:
                return word("(Unable to extract images from PDF file)")
            file_list.extend(sorted([os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]))
            continue
        file_list.append(path)
    page_text = list()
    for page in file_list:
        image = Image.open(page)
        color = ImageEnhance.Color(image)
        bw = color.enhance(0.0)
        bright = ImageEnhance.Brightness(bw)
        brightened = bright.enhance(1.5)
        contrast = ImageEnhance.Contrast(brightened)
        final_image = contrast.enhance(2.0)
        text = tool.image_to_string(final_image, lang=lang, builder=pyocr.builders.TextBuilder(tesseract_layout=psm))
        page_text.append(text)
    for directory in temp_directory_list:
        shutil.rmtree(directory)
    return "\f".join(page_text)

