import re

nameerror_match = re.compile(r'\'(.*)\' (is not defined|referenced before assignment|is undefined|where it is not)')

def extract_missing_name(the_error):
    # logmessage("extract_missing_name: string was " + str(string))
    m = nameerror_match.search(str(the_error))
    if m:
        return m.group(1)
    raise the_error


def fix_quotes(match):
    instring = match.group(1)
    n = len(instring)
    output = ''
    i = 0
    while i < n:
        if instring[i] == '\u201c' or instring[i] == '\u201d':
            output += '"'
        elif instring[i] == '\u2018' or instring[i] == '\u2019':
            output += "'"
        elif instring[i] == '&' and i + 4 < n and instring[i:i+5] == '&amp;':
            output += '&'
            i += 4
        else:
            output += instring[i]
        i += 1
    return output
