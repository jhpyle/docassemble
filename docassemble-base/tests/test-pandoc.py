from docassemble.parse import Pandoc

mycontent = """\
1. Howdy howdy
1. Yo dude
1. You suck"""

pandoc = Pandoc()
pandoc.input_content = mycontent
pandoc.output_format = 'pdf'
pandoc.convert()
print pandoc.output_filename
