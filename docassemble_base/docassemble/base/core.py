import string
import random
from docassemble.base.logger import logmessage
import re
import codecs
from docassemble.base.util import possessify, possessify_long, a_preposition_b, a_in_the_b, your, the, underscore_to_space, nice_number, verb_past, verb_present, noun_plural, comma_and_list, ordinal, word, need

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
    """The base class for all docassemble objects."""
    def init(self, **kwargs):
        for key, value in kwargs.iteritems():
            #logmessage("Found key " + str(key) + " with value " + str(value))
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
        self.attrList = list()
        self.init(**kwargs)
    def set_instance_name(self, thename):
        if not self.has_nonrandom_instance_name:
            self.instanceName = thename
            self.has_nonrandom_instance_name = True
        else:
            logmessage("Not resetting name of " + self.instanceName)
        return
    def _map_info(self):
        return None
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
            self.attrList.append(name)
    def attribute_defined(self, name):
        return hasattr(self, name)
    def attr(self, name):
        return getattr(self, name, None)
    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        return self.object_name()
    def __dir__(self):
        return self.attrList
            
class DAList(DAObject):
    """The base class for lists of things.  A DAList object
    has the attributes "gathered" and "gathering."  The "gathering"
    attribute should be True while the interview is in the midst of 
    determining the items in the list.  When there are no more items
    to be gathered, "gathering" should be set to False and "gathered"
    should be set to True."""
    def init(self, **kwargs):
        self.elements = list()
        self.gathering = False
        if 'elements' in kwargs:
            for element in kwargs['elements']:
                self.append(element)
            self.gathered = True
            del kwargs['elements']
        if 'object_type' in kwargs:
            self.object_type = kwargs['object_type']
            del kwargs['object_type']
        if not hasattr(self, 'object_type'):
            self.object_type = None
        return super(DAList, self).init(**kwargs)
    def appendObject(self, *pargs, **kwargs):
        if len(pargs) > 0:
            objectFunction = pargs[0]
        elif self.object_type is not None:
            objectFunction = self.object_type
        else:
            objectFunction = DAObject
        newobject = objectFunction(self.instanceName + '[' + str(len(self.elements)) + ']', **kwargs)
        self.elements.append(newobject)
        return newobject
    def append(self, value):
        self.elements.append(value)
    def extend(self, the_list):
        self.elements.extend(the_list)
    def first(self):
        return self.__getitem__(0)
    def last(self):
        if len(self.elements) == 0:
            return self.__getitem__(0)
        return self.__getitem__(len(self.elements)-1)
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
        the_noun = self.instanceName
        if not self.gathering:
            self.gathered
            if len(pargs) > 0:
                the_noun = pargs[0]
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
    def gather(self, number=None, item_object_type=None, minimum=1):
        if item_object_type is None and self.object_type is not None:
            item_object_type = self.object_type
        self.gathering = True
        while len(self.elements) < minimum:
            the_length = len(self.elements)
            if item_object_type is not None:
                self.appendObject(item_object_type)
            str(self.__getitem__(the_length))
        for elem in self.elements:
            str(elem)
        the_length = len(self.elements)
        if number is not None:
            while the_length < int(number):
                if item_object_type is not None:
                    self.appendObject(item_object_type)
                str(self.__getitem__(the_length))
        else:
            while self.there_is_another:
                del self.there_is_another
                if item_object_type is not None:
                    self.appendObject(item_object_type)
                str(self.__getitem__(the_length))
        self.gathering = False
        return True
    def comma_and_list(self):
        if not self.gathering:
            self.gathered
        return comma_and_list(self.elements)        
    def __iter__(self):
        return self.elements.__iter__()
    def _fill_up_to(self, index):
        if index < 0 and len(self.elements) + index < 0:
            num_to_add = (-1 * index) - len(self.elements)
            for i in range(0, num_to_add):
                if self.object_type is None:
                    self.elements.append(None)
                else:
                    self.appendObject(self.object_type)
        elif len(self.elements) <= index:
            num_to_add = 1 + index - len(self.elements)
            for i in range(0, num_to_add):
                if self.object_type is None:
                    self.elements.append(None)
                else:
                    self.appendObject(self.object_type)        
    def __setitem__(self, index, value):
        self._fill_up_to(index)
        return self.elements.__setitem__(index, value)
    def __getitem__(self, index):
        try:
            return self.elements[index]
        except:
            if self.object_type is None:
                raise NameError("name '" + object.__getattribute__(self, 'instanceName') + '[' + str(index) + ']' + "' is not defined")
            else:
                self._fill_up_to(index)
            return self.elements[index]
    def __str__(self):
        return self.comma_and_list()
    def __unicode__(self):
        return self.comma_and_list()

class DADict(DAObject):
    """A base class for objects that behave like Python dictionaries."""
    def init(self, **kwargs):
        self.elements = dict()
        self.gathering = False
        if 'elements' in kwargs:
            self.elements.update(kwargs['elements'])
            self.gathered = True
            del kwargs['elements']
        if 'object_type' in kwargs:
            self.object_type = kwargs['object_type']
            del kwargs['object_type']
        if not hasattr(self, 'object_type'):
            self.object_type = None
        return super(DADict, self).init(**kwargs)
    def initializeObject(self, entry, objectFunction, **kwargs):
        newobject = objectFunction(self.instanceName + '[' + repr(entry) + ']', **kwargs)
        self.elements[entry] = newobject
        return newobject
    def new(self, *pargs, **kwargs):
        for parg in pargs:
            if type(parg) is list:
                for item in parg:
                    self.new(item, **kwargs)
            else:
                if hasattr(self, 'object_type'):
                    if parg not in self.elements:
                        self.initializeObject(parg, self.object_type, **kwargs)
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
        the_noun = self.instanceName
        if not self.gathering:
            self.gathered
            if len(pargs) > 0:
                the_noun = pargs[0]
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
    def gather(self, item_object_type=None):
        if item_object_type is None and self.object_type is not None:
            item_object_type = self.object_type
        self.gathering = True
        for elem in self.elements.values():
            str(elem)
        while self.there_is_another:
            if item_object_type is not None:
                self.initializeObject(self.new_item_name, item_object_type)
                self._new_item_init_callback()
            else:
                self.elements[self.new_item_name] = self.new_item_value
                del self.new_item_value
            del self.new_item_name
            del self.there_is_another
        self.gathering = False
        return True
    def _new_item_init_callback(self):
        return
    def comma_and_list(self):
        if not self.gathering:
            self.gathered
        return comma_and_list(sorted(self.elements.keys()))
    def __getitem__(self, index):
        if index not in self.elements:
            if self.object_type is None:
                raise NameError("name '" + object.__getattribute__(self, 'instanceName') + "[" + repr(index) + "] is not defined")
            else:
                self.initializeObject(index, self.object_type)
            return self.elements[index]
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
    """Used internally by docassemble to represent a file."""
    def init(self, **kwargs):
        if 'filename' in kwargs:
            self.filename = kwargs['filename']
        if 'mimetype' in kwargs:
            self.mimetype = kwargs['mimetype']
        if 'extension' in kwargs:
            self.extension = kwargs['extension']
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
            return('[FILE ' + str(self.number) + ', ' + str(width) + ']')
        else:
            return('[FILE ' + str(self.number) + ']')

class DAFileCollection(DAObject):
    """Used internally by docassemble to refer to a collection of
    DAFile objects, usually representing the same document in different
    formats.  Attributes represent file types.  The attachments feature
    generates objects of this type."""
    pass

class DAFileList(DAList):
    """Used internally by docassemble to refer to a list of files,
    such as a list of files uploaded to a single variable."""
    def __str__(self):
        return self.show()
    def __unicode__(self):
        return self.show()
    def show(self, width=None):
        output = ''
        for element in self.elements:
            if element.ok:
                output += element.show(width=width)
        return output

class DATemplate(DAObject):
    """The class used for Markdown templates.  A template block saves to
    an object of this type.  The two attributes are "subject" and 
    "content." """
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
    """Packs a list of objects in the appropriate format for including
    as code in a multiple-choice field."""
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
