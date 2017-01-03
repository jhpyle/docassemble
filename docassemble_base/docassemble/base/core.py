#import string
#import random
from docassemble.base.logger import logmessage
from docassemble.base.generate_key import random_string
import re
import codecs
import redis
import sys
from docassemble.base.filter import file_finder
#from docassemble.base.error import DANameError
from docassemble.base.functions import possessify, possessify_long, a_preposition_b, a_in_the_b, its, their, the, underscore_to_space, nice_number, verb_past, verb_present, noun_plural, comma_and_list, ordinal, word, need, capitalize

__all__ = ['DAObject', 'DAList', 'DADict', 'DASet', 'DAFile', 'DAFileCollection', 'DAFileList', 'DATemplate']

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
        newname = random_string(12)
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
#     def __setstate__(self, state):
# #        sys.stderr.write("__setstate__\n")
#         self.__dict__ = state
#     def __getstate__(self):
# #        sys.stderr.write("__getstate__\n")
#         return self.__dict__
    # def __slots__(self):
    #     attrs = ['has_nonrandom_instance_name', 'instanceName', 'attrList']
    #     attrs.extend(self.attrList)
    #     return attrs
    def __init__(self, *args, **kwargs):
        if len(args):
            thename = args[0]
#            sys.stderr.write("__init__: " + thename + "\n")
            self.has_nonrandom_instance_name = True
        else:
            thename = get_unique_name()
#            sys.stderr.write("__init__: " + thename + "\n")
            self.has_nonrandom_instance_name = False
        self.instanceName = str(thename)
        self.attrList = list()
        self.init(**kwargs)
    def set_instance_name(self, thename):
        """Sets the instanceName attribute, if it is not already set."""
#        sys.stderr.write("set_instance_name\n")
        if not self.has_nonrandom_instance_name:
            self.instanceName = thename
            self.has_nonrandom_instance_name = True
        else:
            logmessage("Not resetting name of " + self.instanceName)
        return
    def _map_info(self):
        return None
    def __getattr__(self, thename):
        # sys.stderr.write("__getattr__: " + thename + "\n")
        # if hasattr(self, thename):# or thename == "__setstate__" or thename == "__getstate__" or thename == "__slots__":
        #     #sys.stderr.write("special __getattr__: " + thename + "\n")
        #     return(object.__getattribute__(self, thename))
        if thename.startswith('_'):
            return object.__getattribute__(self, thename)
        else:
            #var_name = object.__getattribute__(self, 'instanceName') + "." + thename
            var_name = object.__getattribute__(self, 'instanceName') + "." + thename
#            sys.stderr.write("__getattr__: " + thename + "\n")
            raise NameError("name '" + var_name + "' is not defined")
            #return var_name
    def object_name(self):
        """Returns the instanceName attribute, or, if the instanceName contains attributes, returns a
        phrase.  E.g., case.plaintiff becomes "plaintiff in the case." """
        return (reduce(a_in_the_b, map(object_name_convert, reversed(self.instanceName.split(".")))))
    def object_possessive(self, target):
        """Returns a possessive phrase based on the instanceName.  E.g., client.object_possessive('fish') returns
        "client's fish." """
        if len(self.instanceName.split(".")) > 1:
            return(possessify_long(self.object_name(), target))
        else:
            return(possessify(the(self.object_name()), target))
    def initializeAttribute(self, name, objectType, **kwargs):
        """Defines an attribute for the object, setting it to a newly initialized object.
        The first argument is the name of the attribute and the second argument is type
        of the new object that will be initialized.  E.g., 
        client.initializeAttribute('mother', Individual) initializes client.mother as an
        Individual with instanceName "client.mother"."""
        if name in self.__dict__:
            return
        else:
            object.__setattr__(self, name, objectType(self.instanceName + "." + name, **kwargs))
            self.attrList.append(name)
    def attribute_defined(self, name):
        """Returns True or False depending on whether the given attribute is defined."""
#        sys.stderr.write("attribute_defined\n")
        return hasattr(self, name)
    def attr(self, name):
        """Returns the value of the given attribute, or None if the attribute is not defined"""
#        sys.stderr.write("attr\n")
        return getattr(self, name, None)
    def __str__(self):
#        sys.stderr.write("__str__\n")
        if hasattr(self, 'name'):
            return self.name
        return self.object_name()
    def __unicode__(self):
#        sys.stderr.write("__unicode__\n")
        return unicode(self.__str__())
    def __dir__(self):
#        sys.stderr.write("__dir__\n")
        return self.attrList
    def pronoun_possessive(self, target, **kwargs):
        """Returns "its <target>." """
        output = its(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        return word('it', **kwargs)
    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)
    def pronoun_subjective(self, **kwargs):        
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

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
        self.auto_gather = True
        self.ask_number = False
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
    def is_gathered(self):
        if self.auto_gather:
            return self.gather()
        return self.gathered
    def clear(self):
        self.elements = list()
    def appendObject(self, *pargs, **kwargs):
        """Creates a new object and adds it to the list.
        Takes an optional argument, which is the type of object
        the new object should be.  If no object type is provided,
        the object type given by .objectFunction is used, and if 
        that is not set, DAObject is used."""
        if len(pargs) > 0:
            objectFunction = pargs[0]
        elif self.object_type is not None:
            objectFunction = self.object_type
        else:
            objectFunction = DAObject
        newobject = objectFunction(self.instanceName + '[' + str(len(self.elements)) + ']', **kwargs)
        self.elements.append(newobject)
        return newobject
    def append(self, *pargs):
        """Adds the arguments to the end of the list."""
        for parg in pargs:
            self.elements.append(parg)
    def remove(self, *pargs):
        """Removes the given arguments from the list, if they are in the list"""
        for value in pargs:
            if value in self.elements:
                self.elements.remove(value)
    def extend(self, the_list):
        """Adds each of the elements of the given list to the end of the list."""
        self.elements.extend(the_list)
    def first(self):
        """Returns the first element of the list"""
        return self.__getitem__(0)
    def last(self):
        """Returns the last element of the list"""
        if len(self.elements) == 0:
            return self.__getitem__(0)
        return self.__getitem__(len(self.elements)-1)
    def does_verb(self, the_verb, **kwargs):
        """Returns the appropriate conjugation of the given verb depending on whether
        there is only one element in the list or multiple elements.  E.g.,
        case.plaintiff.does_verb('sue') will return "sues" if there is one plaintiff
        and "sue" if there is more than one plaintiff."""
        if not self.gathering:
            self.is_gathered()
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if len(self.elements) > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense)
        else:
            if len(self.elements) > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        if not self.gathering:
            self.is_gathered()
        if len(self.elements) > 1:
            tense = 'ppl'
        else:
            tense = '3sgp'
        return verb_past(the_verb, tense)
    def as_singular_noun(self):
        """Returns a human-readable expression of the object based on its instanceName,
        without making it plural.  E.g., case.plaintiff.child.as_singular_noun() 
        returns "child" even if there are multiple children."""
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun
    def possessive(self, target):
        return possessify(self.as_noun(), target, plural=(len(self.elements) > 1))
    def as_noun(self, *pargs, **kwargs):
        """Returns a human-readable expression of the object based on its instanceName,
        using singular or plural depending on whether the list has one element or more
        than one element.  E.g., case.plaintiff.child.as_noun() returns "child" or
        "children," as appropriate.  If an argument is supplied, the argument is used
        instead of the instanceName."""
        the_noun = self.instanceName
        if not self.gathering:
            self.is_gathered()
            if len(pargs) > 0:
                the_noun = pargs[0]
        the_noun = re.sub(r'.*\.', '', the_noun)
        if len(self.elements) > 1 or len(self.elements) == 0:
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(noun_plural(the_noun))
            else:
                return noun_plural(the_noun)
        else:
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(the_noun)
            else:
                return the_noun
    def number(self):
        """Returns the number of elements in the list.  Forces the gathering of the
        elements if necessary."""
        self.is_gathered()
        return len(self.elements)
    def number_gathered(self):
        """Returns the number of elements in the list without forcing the gathering
        of the elements."""
        return len(self.elements)
    def number_as_word(self):
        """Returns the number of elements in the list, spelling out the number if ten 
        or below.  Forces the gathering of the elements if necessary."""
        return nice_number(self.number())
    def number_gathered_as_word(self):
        """Returns the number of elements in the list, spelling out the number if ten 
        or below.  Does not force the gathering of the elements."""
        return nice_number(self.number_gathered())
    def gather(self, number=None, item_object_type=None, minimum=1):
        """Causes the elements of the list to be gathered and named.  Returns True."""
        if hasattr(self, 'gathered') and self.gathered:
            return True
        if item_object_type is None and self.object_type is not None:
            item_object_type = self.object_type
        self.gathering = True
        if number is None and self.ask_number:
            number = self.target_number
        while len(self.elements) < minimum:
            logmessage("I am here and item_object_type is " + str(item_object_type))
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
        if self.auto_gather:
            self.gathered = True
        return True
    def comma_and_list(self, **kwargs):
        """Returns the elements of the list, separated by commas, with 
        "and" before the last element."""
        if not self.gathering:
            self.is_gathered()
        return comma_and_list(self.elements, **kwargs)
    def __contains__(self, item):
        return self.elements.__contains__(item)
    def __iter__(self):
        return self.elements.__iter__()
    def __len__(self):
        return self.elements.__len__()
    def __delitem__(self, index):
        return self.elements.__delitem__(index)
    def __reversed__(self):
        return self.elements.__reversed__()
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
                var_name = object.__getattribute__(self, 'instanceName') + '[' + str(index) + ']'
                raise NameError("name '" + var_name + "' is not defined")
            else:
                self._fill_up_to(index)
            return self.elements[index]
    def __str__(self):
        return self.comma_and_list()
    def __unicode__(self):
        return unicode(self.__str__())
    def union(other_set):
        return set(self.elements).union(setify(other_set))
    def intersection(other_set):
        return set(self.elements).intersection(setify(other_set))
    def difference(other_set):
        return set(self.elements).difference(setify(other_set))
    def isdisjoint(other_set):
        return set(self.elements).isdisjoint(setify(other_set))
    def issubset(other_set):
        return set(self.elements).issubset(setify(other_set))
    def issuperset(other_set):
        return set(self.elements).issuperset(setify(other_set))
    def pronoun_possessive(self, target, **kwargs):
        """Given a word like "fish," returns "her fish," "his fish," or "their fish," as appropriate."""
        if len(self.elements) == 1:
            return self.elements[0].pronoun_possessive(target, **kwargs)
        output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        """Returns a pronoun like "you," "her," or "him," "it", or "them," as appropriate."""
        if len(self.elements) == 1:
            return self.elements[0].pronoun(**kwargs)
        output = word('them', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)
    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)
    def pronoun_subjective(self, **kwargs):
        """Returns a pronoun like "you," "she," "he," or "they" as appropriate."""
        if len(self.elements) == 1:
            return self.elements[0].pronoun_subjective(**kwargs)
        output = word('they', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)

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
    def clear(self):
        self.elements = list()
    def initializeObject(self, *pargs, **kwargs):
        """Creates a new object and creates an entry in the dictionary for it.
        The first argument is the name of the dictionary key to set.
        Takes an optional second argument, which is the type of object
        the new object should be.  If no object type is provided,
        the object type given by .objectFunction is used, and if 
        that is not set, DAObject is used."""
        entry = pargs[0]
        if len(pargs) > 1:
            objectFunction = pargs[1]
        elif self.object_type is not None:
            objectFunction = self.object_type
        else:
            objectFunction = DAObject
        newobject = objectFunction(self.instanceName + '[' + repr(entry) + ']', **kwargs)
        self.elements[entry] = newobject
        return newobject
    def new(self, *pargs, **kwargs):
        """Initializes new dictionary entries.  Each entry is set to a
        new object.  For example, if the dictionary is called positions,
        calling positions.new('file clerk') will result in the creation of
        the object positions['file clerk'].  The type of object is given by
        the object_type attribute, or DAObject if object_type is not set."""
        for parg in pargs:
            if hasattr(parg, '__iter__'):
                for item in parg:
                    self.new(item, **kwargs)
            else:
                if hasattr(self, 'object_type'):
                    if parg not in self.elements:
                        self.initializeObject(parg, self.object_type, **kwargs)
    def does_verb(self, the_verb, **kwargs):
        """Returns the appropriate conjugation of the given verb depending on
        whether there is only one key in the dictionary or multiple
        keys.  E.g., player.does_verb('finish') will return "finishes" if there
        is one player and "finish" if there is more than one
        player."""
        if not self.gathering:
            self.gathered
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if len(self.elements) > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense)
        else:
            if len(self.elements) > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        if not self.gathering:
            self.gathered
        if len(self.elements) > 1:
            tense = 'ppl'
        else:
            tense = '3sgp'
        return verb_past(the_verb, tense)
    def as_singular_noun(self):
        """Returns a human-readable expression of the object based on its
        instanceName, without making it plural.  E.g.,
        player.as_singular_noun() returns "player" even if there are
        multiple players."""
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun        
    def as_noun(self, *pargs):
        """Returns a human-readable expression of the object based on its
        instanceName, using singular or plural depending on whether
        the dictionary has one key or more than one key.  E.g.,
        player.as_noun() returns "player" or "players," as
        appropriate.  If an argument is supplied, the argument is used
        as the noun instead of the instanceName."""
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
        """Returns the number of keys in the dictionary.  Forces the gathering of the
        dictionary items if necessary."""
        self.gathered
        return len(self.elements)
    def number_gathered(self):
        """Returns the number of keys in the dictionary without forcing the gathering
        of the dictionary items."""
        return len(self.elements)
    def number_gathered_as_word(self):
        """Returns the number of keys in the dictionary, spelling out the number if ten 
        or below.  Does not force the gathering of the dictionary items."""
        return nice_number(self.number_gathered())
    def number_as_word(self):
        """Returns the number of keys in the dictionary, spelling out the number if ten 
        or below.  Forces the gathering of the dictionary items if necessary."""
        return nice_number(self.number())
    def gather(self, item_object_type=None):
        """Causes the dictionary items to be gathered and named.  Returns True."""
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
    def comma_and_list(self, **kwargs):
        """Returns the keys of the list, separated by commas, with 
        "and" before the last key."""
        if not self.gathering:
            self.gathered
        return comma_and_list(sorted(self.elements.keys()), **kwargs)
    def __getitem__(self, index):
        if index not in self.elements:
            if self.object_type is None:
                var_name = object.__getattribute__(self, 'instanceName') + "[" + repr(index) + "]"
                raise NameError("name '" + var_name + "' is not defined")
            else:
                self.initializeObject(index, self.object_type)
            return self.elements[index]
        return self.elements[index]
    def __setitem__(self, key, value):
        self.elements[key] = value
        return
    def __contains__(self, item):
        return self.elements.__contains__(item)
    def keys(self):
        """Returns the keys of the dictionary as a Python list."""
        return self.elements.keys()
    def values(self):
        """Returns the values of the dictionary as a Python list."""
        return self.elements.values()
    def update(*pargs, **kwargs):
        """Updates the dictionary with the keys and values of another dictionary"""
        if len(pargs) > 0:
            other_dict = pargs[0]
            if isinstance(other_dict, DADict):
                return self.elements.update(other_dict.elements)
        self.elements.update(*pargs, **kwargs)
    def pop(self, *pargs):
        """Remove a given key from the dictionary and return its value"""
        return self.elements.pop(*pargs)
    def popitem(self):
        """Remove an arbitrary key from the dictionary and return its value"""
        return self.elements.popitem()
    def setdefault(self, *pargs):
        """Set a key to a default value if it does not already exist in the dictionary"""
        return self.elements.setdefault(*pargs)
    def get(*pargs):
        """Returns the value of a given key."""
        return self.elements.get(*pargs)
    def clear(self):
        """Removes all the items from the dictionary."""
        return self.elements.clear()
    def copy(self):
        """Returns a copy of the dictionary."""
        return self.elements.copy()
    def has_key(key):
        """Returns True if key is in the dictionary."""
        return self.elements.has_key(key)
    def items(self):
        """Returns a copy of the items of the dictionary."""
        return self.elements.items()
    def iteritems(self):
        """Iterates through the keys and values of the dictionary."""
        return self.elements.iteritems()
    def iterkeys(self):
        """Iterates through the keys of the dictionary."""
        return self.elements.iterkeys()
    def itervalues(self):
        """Iterates through the values of the dictionary."""
        return self.elements.itervalues()
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
    def __hash__(self, the_object):
        return self.elements.__hash__(the_object)
    def __str__(self):
        return self.comma_and_list()
    def __unicode__(self):
        return unicode(self.__str__())
    def union(other_set):
        return set(self.elements.values()).union(setify(other_set))
    def intersection(other_set):
        return set(self.elements.values()).intersection(setify(other_set))
    def difference(other_set):
        return set(self.elements.values()).difference(setify(other_set))
    def isdisjoint(other_set):
        return set(self.elements.values()).isdisjoint(setify(other_set))
    def issubset(other_set):
        return set(self.elements.values()).issubset(setify(other_set))
    def issuperset(other_set):
        return set(self.elements.values()).issuperset(setify(other_set))
    def pronoun_possessive(self, target, **kwargs):
        """Returns "their <target>." """
        output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        output = word('them', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)
    def pronoun_subjective(self, **kwargs):        
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

class DASet(DAObject):
    """A base class for objects that behave like Python sets."""
    def init(self, **kwargs):
        self.elements = set()
        self.gathering = False
        if 'elements' in kwargs:
            self.add(kwargs['elements'])
            self.gathered = True
            del kwargs['elements']
        return super(DASet, self).init(**kwargs)
    def copy(self):
        """Returns a copy of the set."""
        return self.elements.copy()
    def clear(self):
        """Removes all the items from the set."""
        self.elements = set()
    def remove(self, elem):
        """Removes an element from the set."""
        self.elements.remove(elem)
    def discard(self, elem):
        """Removes an element from the set if it exists."""
        self.elements.discard(elem)
    def pop(self, *pargs):
        """Remove and return an arbitrary element from the set"""
        return self.elements.pop(*pargs)
    def add(self, *pargs):
        """Adds the arguments to the set, unpacking each argument if it is a
        group of some sort (i.e. it is iterable)."""
        for parg in pargs:
            if hasattr(parg, '__iter__'):
                for item in parg:
                    self.add(item)
            else:
                self.elements.add(parg)
    def does_verb(self, the_verb, **kwargs):
        """Returns the appropriate conjugation of the given verb depending on
        whether there is only one element in the set or multiple
        items.  E.g., player.does_verb('finish') will return
        "finishes" if there is one player and "finish" if there is
        more than one player.

        """
        if not self.gathering:
            self.gathered
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if len(self.elements) > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense)
        else:
            if len(self.elements) > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        if not self.gathering:
            self.gathered
        if len(self.elements) > 1:
            tense = 'ppl'
        else:
            tense = '3sgp'
        return verb_past(the_verb, tense)
    def as_singular_noun(self):
        """Returns a human-readable expression of the object based on its
        instanceName, without making it plural.  E.g.,
        player.as_singular_noun() returns "player" even if there are
        multiple players.

        """
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun        
    def as_noun(self, *pargs):
        """Returns a human-readable expression of the object based on its
        instanceName, using singular or plural depending on whether
        the set has one item in it or multiple items.  E.g.,
        player.as_noun() returns "player" or "players," as
        appropriate.  If an argument is supplied, the argument is used
        instead of the instanceName.

        """
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
        """Returns the number of items in the set.  Forces the gathering of
        the items if necessary.

        """
        self.gathered
        return len(self.elements)
    def number_gathered(self):
        """Returns the number of items in the set without forcing the
        gathering of the items.

        """
        return len(self.elements)
    def number_gathered_as_word(self):
        """Returns the number of items in the set, spelling out the number if
        ten or below.  Does not force the gathering of the items.

        """
        return nice_number(self.number_gathered())
    def number_as_word(self):
        """Returns the number of items in the set, spelling out the number if
        ten or below.  Forces the gathering of the items if necessary.

        """
        return nice_number(self.number())
    def gather(self, item_object_type=None):
        """Causes the items in the set to be gathered and named.  Returns
        True.

        """
        self.gathering = True
        for elem in self.elements.values():
            str(elem)
        while self.there_is_another:
            self.add(self.new_item)
            del self.new_item
            del self.there_is_another
        self.gathering = False
        return True
    def comma_and_list(self, **kwargs):
        """Returns the items in the set, separated by commas, with 
        "and" before the last item."""
        if not self.gathering:
            self.gathered
        return comma_and_list(sorted(map(str, self.elements)), **kwargs)
    def __contains__(self, item):
        return self.elements.__contains__(item)
    def __iter__(self):
        return self.elements.__iter__()
    def __len__(self):
        return self.elements.__len__()
    def __reversed__(self):
        return self.elements.__reversed__()
    def __and__(self, operand):
        return self.elements.__and__(operand)
    def __or__(self, operand):
        return self.elements.__or__(operand)
    def __rand__(self, operand):
        return self.elements.__rand__(operand)
    def __ror__(self, operand):
        return self.elements.__ror__(operand)
    def __hash__(self, the_object):
        return self.elements.__hash__(the_object)
    def __str__(self):
        return self.comma_and_list()
    def __unicode__(self):
        return unicode(self.__str__())
    def union(other_set):
        """Returns a Python set consisting of the elements of current set
        combined with the elements of the other_set.

        """
        return self.elements.union(setify(other_set))
    def intersection(other_set):
        """Returns a Python set consisting of the elements of the current set
        that also exist in the other_set.

        """
        return self.elements.intersection(setify(other_set))
    def difference(other_set):
        """Returns a Python set consisting of the elements of the current set
        that do not exist in the other_set.

        """
        return self.elements.difference(setify(other_set))
    def isdisjoint(other_set):
        """Returns True if no elements overlap between the current set and the
        other_set.  Otherwise, returns False."""
        return self.elements.isdisjoint(setify(other_set))
    def issubset(other_set):
        """Returns True if the current set is a subset of the other_set.
        Otherwise, returns False.

        """
        return self.elements.issubset(setify(other_set))
    def issuperset(other_set):
        """Returns True if the other_set is a subset of the current set.
        Otherwise, returns False.

        """
        return self.elements.issuperset(setify(other_set))
    def pronoun_possessive(self, target, **kwargs):
        """Returns "their <target>." """
        output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        output = word('them', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)
    def pronoun_subjective(self, **kwargs):        
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

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
        return unicode(self.__str__())
    def retrieve(self):
        self.file_info = file_finder(self.number)
    def path(self):
        """Returns a filename at which the file can be accessed"""
        if not hasattr(self, 'file_info'):
            self.retrieve()
        if 'fullpath' not in self.file_info:
            #logmessage("file_info is " + str(self.file_info))
            raise Exception("fullpath not found")
        return self.file_info['fullpath']
    def commit(self):
        """Ensures that changes to the file are saved and available in the 
        future
        """
        if hasattr(self, 'file_info') and 'savedfile' in self.file_info:
            self.file_info['savedfile'].finalize()
    def show(self, width=None):
        """Inserts markup that displays the file as an image.  Takes an
        optional keyword argument width.

        """
        if not self.ok:
            return('')
        if width is not None:
            return('[FILE ' + str(self.number) + ', ' + str(width) + ']')
        else:
            return('[FILE ' + str(self.number) + ']')

class DAFileCollection(DAObject):
    """Used internally by docassemble to refer to a collection of DAFile
    objects, usually representing the same document in different
    formats.  Attributes represent file types.  The attachments
    feature generates objects of this type.

    """
    def init(self, **kwargs):
        self.info = dict()
    pass

class DAFileList(DAList):
    """Used internally by docassemble to refer to a list of files, such as
    a list of files uploaded to a single variable.

    """
    def __str__(self):
        return self.show()
    def __unicode__(self):
        return unicode(self.__str__())
    def show(self, width=None):
        """Inserts markup that displays each element in the list as an image.
        Takes an optional keyword argument width.

        """
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
        self.decorations = list()
        if 'decorations' in kwargs:
            for decoration in kwargs['decorations']:
                if decoration and decoration != '':
                    self.decorations.append(decoration)
    def __str__(self):
        return(self.content)
    def __unicode__(self):
        return unicode(self.__str__())
#    def __repr__(self):
#        return(self.content)

def selections(*pargs, **kwargs):
    """Packs a list of objects in the appropriate format for including
    as code in a multiple-choice field."""
    to_exclude = set()
    if 'exclude' in kwargs:
        setify(kwargs['exclude'], to_exclude)
    defaults = set()
    if 'default' in kwargs:
        setify(kwargs['default'], defaults)
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
                if subarg in defaults:
                    default_value = True
                else:
                    default_value = False
                output.append({myb64quote(subarg.instanceName): str(subarg), 'default': default_value})
                seen.add(subarg)
    return output

def myb64quote(text):
    return codecs.encode(text.encode('utf-8'), 'base64').decode().replace('\n', '')

def setify(item, output=set()):
    if isinstance(item, DAObject) and hasattr(item, 'elements'):
        setify(item.elements, output)
    elif hasattr(item, '__iter__'):
        for subitem in item:
            setify(subitem, output)
    else:
        output.add(item)
    return output
