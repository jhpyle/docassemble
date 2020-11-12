#! /usr/bin/env python3

import sys
import os
import codecs
import re
import yaml

document_match = re.compile(r'^--- *$', flags=re.MULTILINE)
fix_tabs = re.compile(r'\t')
fix_initial = re.compile(r'^---\n')

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: get_yaml_from_example.py some_file.yml")
    dirname = sys.argv[1]
    output = dict()
    if not os.path.isdir(dirname):
        sys.exit("Directory " + str(dirname) + " not found")
    for filename in os.listdir(dirname):
        if not re.search(r'.ya*ml$', filename, flags=re.IGNORECASE):
            continue
        if re.search(r'\#', filename):
            continue    
        example_name = os.path.splitext(filename)[0]
        result = read_file(os.path.join(dirname, filename))
        if result is None:
            continue
        output[example_name] = result
    print(yaml.safe_dump(output, default_flow_style=False, default_style = '|'))

def read_file(filename):
    start_block = 1
    end_block = 2
    if not os.path.isfile(filename):
        sys.exit("File " + str(filename) + " not found")
    with open(filename, 'r', encoding='utf-8') as fp:
        content = fp.read()
        content = fix_tabs.sub('  ', content)
        content = fix_initial.sub('', content)
        blocks = list(map(lambda x: x.strip(), document_match.split(content)))
        if not len(blocks):
            sys.stderr.write("File " + str(filename) + " could not be read\n")
            return None
        metadata = dict()
        for the_block in blocks:
            if re.search(r'metadata:', the_block):
                block_info = yaml.load(the_block) #, Loader=yaml.FullLoader
                if 'metadata' in block_info:
                    metadata.update(block_info['metadata'])
        start_block = int(metadata.get('example start', 1))
        end_block = int(metadata.get('example end', start_block)) + 1
        result = "\n---\n".join(blocks[start_block:end_block])
    return(result)

if __name__ == "__main__":
    main()
    sys.exit(None)
