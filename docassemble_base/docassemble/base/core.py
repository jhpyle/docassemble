import string
import random
import re
from docassemble.base.util import possessify, possessify_long, a_in_the_b, your, the, underscore_to_space, nice_number, verb_past, verb_present, noun_plural, comma_and_list

unique_names = set()

def get_unique_name():
    while True:
        newname = ''.join(random.choice(string.ascii_letters) for i in range(12))
        if newname in unique_names:
            continue
        unique_names.add(newname)
        return newname

class DAObject(object):
    def init(self):
        return
    def __init__(self, *args, **kwargs):
        if len(args):
            thename = args[0]
        else:
            thename = get_unique_name()
        self.instanceName = thename
        self.init(**kwargs)
    def __getattr__(self, thename):
        if hasattr(self, thename) or thename == "__getstate__" or thename == "__slots__":
            return(object.__getattribute__(self, thename))
        else:
            raise NameError("Undefined name '" + object.__getattribute__(self, 'instanceName') + "." + thename + "'")
    def object_name(self):
        return(reduce(a_in_the_b, map(underscore_to_space, reversed(self.instanceName.split(".")))))
    def object_possessive(self, target):
        if len(self.instanceName.split(".")) > 1:
            return(possessify_long(self.object_name(), target))
        else:
            return(possessify(the(self.object_name()), target))
    def initializeAttribute(self, name, objectType):
        if name in self.__dict__:
            return
        else:
            object.__setattr__(self, name, objectType(self.instanceName + "." + name))

class DAList(DAObject):
    def init(self, **kwargs):
        self.elements = list()
        self.gathering = False
        if 'elements' in kwargs:
            for element in kwargs['elements']:
                self.add(element)
            self.gathered = True
        return super(DAList, self).init()
    def add(self, element):
        self.elements.append(element)
    def addObject(self, objectFunction):
        newobject = objectFunction(self.instanceName + '[' + str(len(self.elements)) + ']')
        self.elements.append(newobject)
        return newobject
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
    def as_singular_noun(self, *pargs):
        if not self.gathering:
            self.gathered
        if len(pargs) > 0:
            the_noun = pargs[0]
        else:
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
    def __getitem__(self, index):
        return self.elements[index]
    def __str__(self):
        return self.comma_and_list()

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
    def show(self, width=None):
        output = ''
        for element in self.elements:
            if element.ok:
                if width is not None:
                    output += '[IMAGE ' + str(element.number) + ', ' + str(width) + ']' + "\n"
                else:
                    output += '[IMAGE ' + str(element.number) + ']' + "\n"
        return output

