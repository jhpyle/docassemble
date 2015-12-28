import os
import os.path
import subprocess
import docassemble.base.filter
import docassemble.base.util
import tempfile
import shutil
from docassemble.base.logger import logmessage

PANDOC_PATH = 'pandoc'

def set_pandoc_path(path):
    global PANDOC_PATH
    PANDOC_PATH = path
#fontfamily: zi4, mathptmx, courier
#\ttfamily
#\renewcommand{\thesubsubsubsection}{\alph{subsubsubsection}.}
#\renewcommand{\thesubsubsubsubsection}{\roman{subsubsubsubsection}.}
#  - \newenvironment{allcaps}{\startallcaps}{}
#  - \def\startallcaps#1\end{\uppercase{#1}\end}

class Pandoc(object):
    def __init__(self):
        self.input_content = None
        self.output_content = None
        self.input_format = 'markdown'
        self.output_format = 'rtf'
        self.output_filename = None
        self.template_file = None
        self.metadata = list()
        self.initial_yaml = list()
        self.additional_yaml = list()
        self.arguments = []
    def convert_to_file(self):
        metadata_as_dict = dict()
        for data in self.metadata:
            if type(data) is dict:
                for key in data:
                    metadata_as_dict[key] = data[key]
        if self.output_format == 'rtf' and self.template_file is None:
            self.template_file = docassemble.base.util.standard_template_filename('Legal-Template.rtf')
        if (self.output_format == 'pdf' or self.output_format == 'tex') and self.template_file is None:
            self.template_file = docassemble.base.util.standard_template_filename('Legal-Template.tex')
        yaml_to_use = list()
        if self.output_format == 'pdf' or self.output_format == 'tex':
            if len(self.initial_yaml) == 0:
                standard_file = docassemble.base.util.standard_template_filename('Legal-Template.yml')
                if standard_file is not None:
                    self.initial_yaml.append(standard_file)
            for yaml_file in self.initial_yaml:
                if yaml_file is not None:
                    yaml_to_use.append(yaml_file)
            for yaml_file in self.additional_yaml:
                if yaml_file is not None:
                    yaml_to_use.append(yaml_file)
            #print "Before: " + repr(self.input_content)
            self.input_content = docassemble.base.filter.pdf_filter(self.input_content, metadata=metadata_as_dict)
            logmessage("After: " + repr(self.input_content))
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        temp_file.write(self.input_content.encode('UTF-8'))
        temp_file.close()
        temp_outfile = tempfile.NamedTemporaryFile(mode="w", suffix="." + str(self.output_format), delete=False)
        temp_outfile.close()
        subprocess_arguments = [PANDOC_PATH]
        if len(yaml_to_use) > 0:
            subprocess_arguments.extend(yaml_to_use)
        subprocess_arguments.extend([temp_file.name])
        if self.template_file is not None:
            subprocess_arguments.extend(['--template=%s' % self.template_file])
        subprocess_arguments.extend(['-s -o %s' % temp_outfile.name])
        subprocess_arguments.extend(self.arguments)
        #for argum in subprocess_arguments:
        #    logmessage(str(argum) + "\n")
        cmd = " ".join(subprocess_arguments)
        fin = os.popen(cmd)
        msg = fin.read()
        fin.close()
        if msg:
            self.pandoc_message = msg
        os.remove(temp_file.name)
        if os.path.exists(temp_outfile.name):
            if self.output_format == 'rtf':
                with open(temp_outfile.name) as the_file: file_contents = the_file.read()
                file_contents = docassemble.base.filter.rtf_filter(file_contents, metadata=metadata_as_dict)
                with open(temp_outfile.name, "w") as the_file: the_file.write(file_contents)
            if self.output_filename is not None:
                shutil.copyfile(temp_outfile.name, self.output_filename)
            else:
                self.output_filename = temp_outfile.name
            self.output_content = None
        else:
            raise IOError("Failed creating file: %s" % output_filename)
        return
    def convert(self):
        if (self.output_format == "pdf" or self.output_format == "tex" or self.output_format == "rtf" or self.output_format == "epub"):
            self.convert_to_file()
        else:
            subprocess_arguments = [PANDOC_PATH, '--from=%s' % self.input_format, '--to=%s' % self.output_format]
            subprocess_arguments.extend(self.arguments)
            p = subprocess.Popen(
                subprocess_arguments,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            self.output_filename = None
            
            self.output_content = p.communicate(self.input_content.encode('utf-8'))[0]
        return
