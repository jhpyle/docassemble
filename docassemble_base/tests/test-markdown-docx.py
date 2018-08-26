import codecs
from docassemble.base.file_docx import markdown_to_docx
from docxtpl import DocxTemplate

markdown_texts = {
	'markdown1': "data/markdown1.md",
	'markdown2': "data/markdown2.md",
	'markdown3': "data/markdown3.md"
	}

for markdown_key, markdown_value in markdown_texts.items():
	markdown_file = codecs.open(markdown_value, mode="r", encoding="utf-8")
	markdown_texts[markdown_key] = markdown_file.read()

markdown_texts['inline'] = 'These examples are from the [Daring Fireball Syntax](https://daringfireball.net/projects/markdown/syntax) page.'

tpl = markdown_to_docx(markdown_texts,'data/templates/markdown_to_docx_template.docx')
tpl.save('data/markdown_to_docx_filled.docx')
