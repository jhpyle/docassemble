import os
# import sys
import tempfile
import re
import subprocess

from os.path import expanduser
from docassemble.base.functions import get_config
from docassemble.base.util import DAFile
from docassemble.base.logger import logmessage

__all__ = ['mmdc']


def mmdc(input_text, file_format='svg', flags=None):
    if flags is None:
        flags = {}
    if not isinstance(flags, dict):
        raise Exception("mmdc: flags not a dictionary")
    if not isinstance(file_format, str) or re.search(r'[^a-z]', file_format) or len(file_format) == 0:
        raise Exception("mmdc: invalid file format")
    if not isinstance(input_text, str):
        input_text = str(input_text)
    logmessage("Writing:\n" + input_text)
    input_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="w", suffix=".mmd", delete=False)
    input_file.write(input_text)
    input_file.close()
    output_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="w", suffix="." + file_format, delete=False)
    output_file.close()
    commands = [get_config('mmdc path', 'mmdc'), '-p', os.path.join(expanduser("~"), 'puppeteer-config.json'), '-i', input_file.name, '-o', output_file.name]
    for key, val in flags.items():
        commands.append('-' + str(key))
        commands.append(repr(str(val)))
    logmessage("Commands are: " + " ".join(commands))
    try:
        output = subprocess.check_output(commands, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as err:
        output = err.output.decode()
        raise Exception("mmdc: there was an error.  " + output)
    if os.path.getsize(output_file.name) == 0:
        raise Exception("mmdc: the command did not produce any output.  " + output)
    obj = DAFile()
    obj.set_random_instance_name()
    obj.initialize(extension=file_format)
    obj.copy_into(output_file.name)
    obj.commit()
    return obj
