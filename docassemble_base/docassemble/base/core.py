import string
import random
from docassemble.base.logger import logmessage
import re
import codecs
from docassemble.base.util import possessify, possessify_long, a_preposition_b, a_in_the_b, your, the, underscore_to_space, nice_number, verb_past, verb_present, noun_plural, comma_and_list, ordinal, word

__all__ = ['DAObject', 'DAList', 'DADict', 'DAFile', 'DAFileCollection', 'DAFileList']

unique_names = set()

match_inside_and_outside_brackets = re.compile('(.*)\[([^\]]+)\]$')
is_number = re.compile(r'[0-9]+')

def noquote(text):
    return re.sub(r'["\']', '', text)

def object_name_convert(text):
    match = match_inside_and_outside_brackets.search(text)
    if match:
        index = noquote(match.group(2))
        if is_number.match(index):
            prefix = ordinal(index) + ' '
        else:
            prefix = index + ' '
        return prefix + word(underscore_to_space(match.group(1)))
    return word(underscore_to_space(text))

def get_unique_name():
    while True:
        newname = ''.join(random.choice(string.ascii_letters) for i in range(12))
        if newname in unique_names:
            continue
        unique_names.add(newname)
        return newname

class DAObject(object):
    def init(self, **kwargs):
        for key, value in kwargs.iteritems():
            logmessage("Found key " + str(key) + " with value " + str(value))
            setattr(self, key, value)
        return
    def __init__(self, *args, **kwargs):
        if len(args):
            thename = args[0]
            self.has_nonrandom_instance_name = True
        else:
            thename = get_unique_name()
            self.has_nonrandom_instance_name = False
        self.instanceName = thename
        self.init(**kwargs)
    def set_instance_name(self, thename):
        if not self.has_nonrandom_instance_name:
            self.instanceName = thename
            self.has_nonrandom_instance_name = True
        else:
            logmessage("Not resetting name of " + self.instanceName)
        return
    def __getattr__(self, thename):
        if hasattr(self, thename) or thename == "__getstate__" or thename == "__slots__":
            return(object.__getattribute__(self, thename))
        else:
            raise NameError("name '" + object.__getattribute__(self, 'instanceName') + "." + thename + "' is not defined")
    def object_name(self):
        return (reduce(a_in_the_b, map(object_name_convert, reversed(self.instanceName.split(".")))))
    def object_possessive(self, target):
        if len(self.instanceName.split(".")) > 1:
            return(possessify_long(self.object_name(), target))
        else:
            return(possessify(the(self.object_name()), target))
    def initializeAttribute(self, name, objectType, **kwargs):
        if name in self.__dict__:
            return
        else:
            object.__setattr__(self, name, objectType(self.instanceName + "." + name, **kwargs))
    def __str__(self):
        return self.object_name()
            
class DAList(DAObject):
    def init(self, **kwargs):
        self.elements = list()
        self.gathering = False
        if 'elements' in kwargs:
            for element in kwargs['elements']:
                self.append(element)
            self.gathered = True
            del kwargs['elements']
        return super(DAList, self).init(**kwargs)
    def appendObject(self, objectFunction):
        newobject = objectFunction(self.instanceName + '[' + str(len(self.elements)) + ']')
        self.elements.append(newobject)
        return newobject
    def append(self, value):
        self.elements.append(value)
    def extend(self, the_list):
        self.elements.extend(the_list)
    def first(self):
        return self.elements[0]
    def last(self):
        return self.elements[-1]
    def does_verb(self, the_verb, **kwargs):
        if not self.gathering:
            self.gathered
        if len(self.elements) > 1:
            tense = 'plural'
        else:
            tense = 3
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            return verb_past(the_verb, person=tense)
        else:
            return verb_present(the_verb, person=tense)
    def did_verb(self, the_verb, **kwargs):
        if not self.gathering:
            self.gathered
        if len(self.elements) > 1:
            tense = 'plural'
        else:
            tense = 3
        return verb_past(the_verb, person=tense)
    def as_singular_noun(self):
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun        
    def as_noun(self, *pargs):
        if not self.gathering:
            self.gathered
            if len(pargs) > 0:
                the_noun = pargs[0]
        else:
            the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        if len(self.elements) > 1 or len(self.elements) == 0:
            return noun_plural(the_noun)
        else:
            return the_noun
    def number(self):
        self.gathered
        return len(self.elements)
    def number_gathered(self):
        return len(self.elements)
    def number_gathered_as_word(self):
        return nice_number(self.number_gathered())
    def number_as_word(self):
        return nice_number(self.number())
    def comma_and_list(self):
        if not self.gathering:
            self.gathered
        return comma_and_list(self.elements)        
    def __setitem__(self, index, value):
        return self.elements.__setitem__(index, value)
    def __getitem__(self, index):
        return self.elements[index]
    def __str__(self):
        return self.comma_and_list()
    def __unicode__(self):
        return self.comma_and_list()

class DADict(DAObject):
    def init(self, **kwargs):
        self.elements = dict()
        return super(DADict, self).init(**kwargs)
    def initializeObject(self, entry, objectFunction, **kwargs):
        newobject = objectFunction(self.instanceName + '[' + repr(entry) + ']', **kwargs)
        self.elements[entry] = newobject
        return newobject
    def __getitem__(self, index):
        return self.elements[index]
    def __setitem__(self, key, value):
        self.elements[key] = value
        return
    def __contains__(self, index):
        return self.elements.__contains__(index)
    def keys(self):
        return self.elements.keys()
    def values(self):
        return self.elements.values()
    def __iter__(self):
        return self.elements.__iter__()
    def __len__(self):
        return self.elements.__len__()
    def __reversed__(self):
        return self.elements.__reversed__()
    def __delitem__(self, key):
        return self.elements.__delitem__(key)
    def __missing__(self, key):
        return self.elements.__missing__(key)

class DAFile(DAObject):
    def init(self, **kwargs):
        if 'filename' in kwargs:
            self.filename = kwargs['filename']
        if 'mimetype' in kwargs:
            self.filename = kwargs['mimetype']
        if 'extension' in kwargs:
            self.filename = kwargs['extension']
        if 'number' in kwargs:
            self.number = kwargs['number']
            self.ok = True
        else:
            self.ok = False
        return
    def __str__(self):
        return self.show()
    def __unicode__(self):
        return self.show()
    def show(self, width=None):
        if not self.ok:
            return('')
        if width is not None:
            return('[IMAGE ' + str(self.number) + ', ' + str(width) + ']')
        else:
            return('[IMAGE ' + str(self.number) + ']')

class DAFileCollection(DAObject):
    pass

class DAFileList(DAList):
    def __str__(self):
        return self.show()
    def __unicode__(self):
        return self.show()
    def show(self, width=None):
        output = ''
        for element in self.elements:
            if element.ok:
                if width is not None:
                    output += '[IMAGE ' + str(element.number) + ', ' + str(width) + ']' + "\n"
                else:
                    output += '[IMAGE ' + str(element.number) + ']' + "\n"
        return output

class DATemplate(DAObject):
    def init(self, **kwargs):
        if 'content' in kwargs:
            self.content = kwargs['content']
        else:
            self.content = ""
        if 'subject' in kwargs:
            self.subject = kwargs['subject']
        else:
            self.subject = ""
    def __str__(self):
        return(self.content)
    def __repr__(self):
        return(self.content)

def selections(*pargs, **kwargs):
    to_exclude = set()
    if 'exclude' in kwargs:
        setify(kwargs['exclude'], to_exclude)
    output = list()
    seen = set()
    for arg in pargs:
        if isinstance(arg, DAList):
            arg.gathered
            the_list = arg.elements
        elif type(arg) is list:
            the_list = arg
        else:
            the_list = [arg]
        for subarg in the_list:
            if isinstance(subarg, DAObject) and subarg not in to_exclude and subarg not in seen:
                output.append({myb64quote(subarg.instanceName): str(subarg)})
                seen.add(subarg)
    return output

def myb64quote(text):
    return codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '')

def setify(item, output=set()):
    if isinstance(item, DAList):
        setify(item.elements, output)
    elif type(item) is list:
        for subitem in item:
            setify(subitem, output)
    else:
        output.add(item)
    return output
