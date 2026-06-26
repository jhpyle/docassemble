import re
import tempfile
import PIL
from cairosvg import svg2png, svg2eps
from ..logger import logmessage

zerowidth = '\u200B'  # pylint: disable=invalid-name

list_types = ['1', 'A', 'a', 'I', 'i']

DEFAULT_IMAGE_WIDTH = '4in'


def set_default_image_width(width):
    global DEFAULT_IMAGE_WIDTH
    DEFAULT_IMAGE_WIDTH = str(width)


def get_default_image_width():
    return DEFAULT_IMAGE_WIDTH

unit_multipliers = {'twips': 0.0500, 'hp': 0.5, 'in': 72, 'pt': 1, 'px': 1, 'em': 12, 'cm': 28.346472}


def pixels_in(length):
    m = re.search(r"([0-9.]+) *([a-z]+)", str(length).lower())
    if m:
        value = float(m.group(1))
        unit = m.group(2)
        # logmessage("value is " + str(value) + " and unit is " + unit)
        if unit in unit_multipliers:
            size = float(unit_multipliers[unit]) * value
            # logmessage("size is " + str(size))
            return int(size)
    logmessage("Could not read " + str(length))
    return 300


def convert_length(length, unit):
    value = pixels_in(length)
    if unit in unit_multipliers:
        size = float(value)/float(unit_multipliers[unit])
        return int(size)
    logmessage("Unit " + str(unit) + " is not a valid unit")
    return 300


def replace_fields(string, status=None, embedder=None):
    if not re.search(r'\[FIELD ', string):
        return string
    matches = []
    in_match = False
    start_match = None
    depth = 0
    i = 0
    while i < len(string):
        if string[i:i+7] == '[FIELD ':
            in_match = True
            start_match = i
            i += 7
            continue
        if in_match:
            if string[i] == '[':
                depth += 1
            elif string[i] == ']':
                if depth == 0:
                    i += 1
                    matches.append((start_match, i))
                    in_match = False
                    continue
                depth -= 1
        i += 1

    field_strings = []
    for (start, end) in matches:
        field_strings.append(string[start:end])
    # logmessage(repr(field_strings))
    for field_string in field_strings:
        if embedder is None:
            string = string.replace(field_string, 'ERROR: FIELD cannot be used here')
        else:
            string = string.replace(field_string, embedder(status, field_string))
    return string


def repeat_along(chars, match):
    output = chars * len(match.group(1))
    # logmessage("Output is " + repr(output))
    return output


def convert_pixels(match):
    pixels = match.group(1)
    return str(int(pixels)/72.0) + "in"


def convert_svg_to_eps(file_info):
    try:
        if file_info['extension'] == 'svg':
            with tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".eps", delete=False) as eps_file:
                with open(file_info['fullpath'], 'rb') as fp:
                    svg2eps(file_obj=fp, write_to=eps_file)
                file_info['path'] = eps_file.name
                file_info['fullpath'] = eps_file.name
                file_info['extension'] = 'eps'
                file_info['mimetype'] = 'application/postscript'
                eps_file.close()
    except BaseException as err:
        logmessage("Failure to convert SVG to EPS: " + err.__class__.__name__ + ": " + str(err))


def convert_svg_to_png(file_info):
    try:
        if file_info['extension'] == 'svg':
            with tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".png", delete=False) as png_file:
                with open(file_info['fullpath'], 'rb') as fp:
                    svg2png(file_obj=fp, write_to=png_file, dpi=300)
                png_file.flush()
                with PIL.Image.open(png_file.name) as im:
                    file_info['width'], file_info['height'] = im.size
                file_info['path'] = png_file.name
                file_info['fullpath'] = png_file.name
                file_info['extension'] = 'png'
                file_info['mimetype'] = 'image/png'
                png_file.close()
    except BaseException as err:
        logmessage("Failure to convert SVG to PNG: " + err.__class__.__name__ + ": " + str(err))


def sanitize_xml(text):
    return re.sub(r'{([{%#])', '{' + zerowidth + r'\1', re.sub(r'([}%#])}', r'\1' + zerowidth + '}', text))
