import re
import yaml
import os
import pprint
fix_tabs = re.compile(r'\t')

with open("/home/jpyle/da/docassemble_base/docassemble/base/data/questions/documentation.yml", 'rU') as fp:
    content = fp.read().decode('utf8')
    content = fix_tabs.sub('  ', content)
    documentation = yaml.load(content)

function_sections = set()
for key, value in documentation.iteritems():
    function_sections.add(value)

illustrated = set()
with open("/home/jpyle/da/docassemble_base/docassemble/base/data/questions/example-list.yml", 'rU') as fp:
    content = fp.read().decode('utf8')
    content = fix_tabs.sub('  ', content)
    categories = yaml.load(content)
    for item in categories:
        for key, value in item.iteritems():
            for examp in value:
                illustrated.add(examp)

directory = '/home/jpyle/da/docassemble_base/docassemble/base/data/questions/examples'
existing_examples = set([re.sub(r'\.yml', r'', f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

doc_sections_with_examples = set()
examples_without_documentation = set()

for example_yml in existing_examples:
    with open(os.path.join(directory, example_yml) + '.yml', 'rU') as fp:
        content = fp.read().decode('utf8')
        content = fix_tabs.sub('  ', content)
        blocks = yaml.load_all(content)
        found = False
        for block in blocks:
            if block is not None and 'metadata' in block:
                if 'documentation' in block['metadata']:
                    doc_sections_with_examples.add(block['metadata']['documentation'])
                    found = True
                    break
        if not found:
            examples_without_documentation.add(example_yml)

docs_directory = '/home/jpyle/gh-pages-da/_docs'
doc_md_files = [f for f in os.listdir(docs_directory) if f != 'functions-errors.md' and os.path.isfile(os.path.join(docs_directory, f))]

examples_referenced = set()
possible_documentation_strings = set()
name_extract = re.compile(r'name="([^"]+)">')
example_ref = re.compile(r'demo="([^"]+)" \%\}')
for doc_md in doc_md_files:
    doc_html = re.sub(r'\.md', r'.html', doc_md)
    possible_documentation_strings.add(str("https://docassemble.org/docs/" + doc_html))
    with open(os.path.join(docs_directory, doc_md), 'rU') as fp:
        content = fp.read().decode('utf8')
        for name in re.findall(name_extract, content):
            possible_documentation_strings.add(str("https://docassemble.org/docs/" + doc_html + '#' + name))
        for name in re.findall(example_ref, content):
            examples_referenced.add(name)

print "non-existent documentation "
pprint.pprint(sorted([doc_sections_with_examples - possible_documentation_strings]))
print "doc sections without examples"
pprint.pprint(sorted([possible_documentation_strings - doc_sections_with_examples]))
print ""
print "illustrations without documentation"
pprint.pprint(sorted([examples_without_documentation & illustrated]))
print ""
print "examples_without_documentation"
pprint.pprint(sorted([examples_without_documentation]))
print ""
print "examples not referenced in documentation"
pprint.pprint(sorted([existing_examples - examples_referenced]))
print ""
print "examples not referenced in playground"
pprint.pprint(sorted([existing_examples - illustrated]))
print ""
print "examples referenced in documentation but not playground"
pprint.pprint(sorted([examples_referenced - illustrated]))
print ""
print "sections not referenced in documentation.yml"
pprint.pprint(sorted([possible_documentation_strings - function_sections]))
print ""
print "sections referenced in documentation.yml that do not exist"
pprint.pprint(sorted([function_sections - possible_documentation_strings]))
