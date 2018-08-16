from bs4 import BeautifulSoup
from docassemble.base.functions import word
import re

__all__ = ['to_text']

def to_text(html_doc):
    #logmessage("Starting to_text")
    output = ""
    soup = BeautifulSoup(html_doc, 'html.parser')
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title', 'audio', 'video', 'pre', 'attribution'])]
    [s.extract() for s in soup.find_all(hidden)]
    [s.extract() for s in soup.find_all('div', {'class': 'invisible'})]
    previous = ""
    for s in soup.find_all(do_show):
        if s.name in ['input', 'textarea', 'img'] and s.has_attr('alt'):
            words = s.attrs['alt']
            if s.has_attr('placeholder'):
                words += ", " + s.attrs['placeholder']
        else:
            words = s.get_text()
        words = re.sub(r'\n\s*', ' ', words, flags=re.DOTALL)
        if len(words) and re.search(r'\w *$', words, re.UNICODE):
            words = words + '.'
        if words != previous:
            output += words + "\n"
        previous = words
    terms = dict()
    for s in soup.find_all('a'):
        if s.has_attr('class') and s.attrs['class'][0] == 'daterm' and s.has_attr('data-content') and s.string is not None:
            terms[s.string] = s.attrs['data-content']
    if len(terms):
        output += word("Terms used in this question:") + "\n"
        for term, definition in terms.iteritems():
            output += term + '.  ' + definition + '\n'
    output = re.sub(r'&amp;gt;', '>', output)
    output = re.sub(r'&amp;lt;', '<', output)
    output = re.sub(r'&gt;', '>', output)
    output = re.sub(r'&lt;', '<', output)
    output = re.sub(r'<[^>]+>', '', output)
    #foo = unicode(output).encode('utf8')
    #logmessage("ending to_text")
    return output

def hidden(element):
    if element.name == 'input':
        if element.has_attr('type'):
            if element.attrs['type'] == 'hidden':
                return True
    return False

bad_list = ['div', 'option']

good_list = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'button', 'textarea', 'note']

def do_show(element):
    if re.match('<!--.*-->', str(element), re.DOTALL):
        return False
    if element.name in ['option'] and element.has_attr('selected'):
        return True    
    if element.name in bad_list:
        return False
    if element.name in ['img', 'input'] and element.has_attr('alt'):
        return True
    if element.name in good_list:
        return True
    if element.parent and element.parent.name in good_list:
        return False
    if element.string:
        return True
    if re.match(r'\s+', element.get_text()):
        return False
    return False

