import re
from bs4 import BeautifulSoup
from docassemble.base.functions import word

__all__ = ['to_text']


def to_text(html_doc):
    # logmessage("Starting to_text")
    output = ''
    soup = BeautifulSoup(html_doc, 'html.parser')
    [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title', 'audio', 'video', 'pre', 'attribution'])]  # pylint: disable=expression-not-assigned
    [s.extract() for s in soup.find_all(hidden)]  # pylint: disable=expression-not-assigned
    [s.extract() for s in soup.find_all('div', {'class': 'dainvisible'})]  # pylint: disable=expression-not-assigned
    [s.extract() for s in soup.select('.sr-exclude')]  # pylint: disable=expression-not-assigned
    previous = ''
    for s in soup.find_all(do_show):
        if s.name in ['input', 'textarea', 'img'] and s.has_attr('alt'):
            words = s.attrs['alt']
            if s.has_attr('placeholder'):
                words += str(", ") + s.attrs['placeholder']
        else:
            words = s.get_text()
        words = re.sub(r'\n\s*', ' ', words, flags=re.DOTALL)
        if len(words) and re.search(r'\w *$', words, re.UNICODE):
            words = words + str('.')
        if words != previous:
            output += str(words) + "\n"
        previous = words
    terms = {}
    for s in soup.find_all('a'):
        if s.has_attr('class') and s.attrs['class'][0] == 'daterm' and s.has_attr('data-bs-content') and s.string is not None:
            terms[s.string] = s.attrs['data-bs-content']
    if len(terms):
        output += word("Terms used in this question:") + "\n"
        for term, definition in terms.items():
            output += str(term) + '.  ' + str(definition) + '\n'
    output = re.sub(r'&amp;gt;', '>', output)
    output = re.sub(r'&amp;lt;', '<', output)
    output = re.sub(r'&gt;', '>', output)
    output = re.sub(r'&lt;', '<', output)
    output = re.sub(r'<[^>]+>', '', output)
    return output


def hidden(element):
    if element.name == 'input':
        if element.has_attr('type'):
            if element.attrs['type'] == 'hidden':
                return True
    elif element.has_attr('aria-hidden') and element.attrs['aria-hidden'] != 'false':
        return True
    return False

bad_list = ['div', 'option']

good_list = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'button', 'textarea', 'note', 'label', 'li']


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
