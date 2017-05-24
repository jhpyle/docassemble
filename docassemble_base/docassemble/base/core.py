#from docassemble.base.logger import logmessage
from docassemble.base.generate_key import random_string
import re
import os
import codecs
import redis
import sys
import shutil
import inspect
import yaml
import mimetypes
from docassemble.base.functions import possessify, possessify_long, a_preposition_b, a_in_the_b, its, their, the, this, these, underscore_to_space, nice_number, verb_past, verb_present, noun_plural, comma_and_list, ordinal, word, need, capitalize, server, nodoublequote, some, indefinite_article
import docassemble.base.functions
import docassemble.base.file_docx

__all__ = ['DAObject', 'DAList', 'DADict', 'DASet', 'DAFile', 'DAFileCollection', 'DAFileList', 'DAEmail', 'DAEmailRecipient', 'DAEmailRecipientList', 'DATemplate']

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
    def init(self, *pargs, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        return
    def __init__(self, *pargs, **kwargs):
        thename = None
        if len(pargs):
            pargs = [x for x in pargs]
            thename = pargs.pop(0)
        if thename is not None:
            self.has_nonrandom_instance_name = True
        else:
            frame = inspect.stack()[1][0]
            the_names = frame.f_code.co_names
            #sys.stderr.write("co_name is " + str(frame.f_code.co_names) + "\n")
            if len(the_names) == 2:
                thename = the_names[1]
                self.has_nonrandom_instance_name = True
            else:
                thename = get_unique_name()
                self.has_nonrandom_instance_name = False
            del frame
        self.instanceName = str(thename)
        self.attrList = list()
        self.init(*pargs, **kwargs)
    def _set_instance_name_for_method(self):
        method_name = inspect.stack()[1][3]
        #sys.stderr.write("_set_instance_name_for_method: method_name is " + str(method_name) + "\n");
        level = 1
        while level < 10:
            frame = inspect.stack()[level][0]
            the_names = frame.f_code.co_names
            #sys.stderr.write("_set_instance_name_for_method: level " + str(level) + "; co_name is " + str(frame.f_code.co_names) + "\n")
            if len(the_names) == 3 and the_names[1] == method_name:
                self.instanceName = the_names[2]
                self.has_nonrandom_instance_name = True
                del frame
                return self
            level += 1
            del frame
        self.instanceName = get_unique_name()
        self.has_nonrandom_instance_name = False
        return self
    def fix_instance_name(self, old_instance_name, new_instance_name):
        """Substitutes a different instance name for the object and its subobjects."""
        self.instanceName = re.sub(r'^' + old_instance_name, new_instance_name, self.instanceName)
        for aname in self.__dict__:
            if isinstance(getattr(self, aname), DAObject):
                getattr(self, aname).fix_instance_name(old_instance_name, new_instance_name)
        self.has_nonrandom_instance_name = True
    def set_instance_name(self, thename):
        """Sets the instanceName attribute, if it is not already set."""
        if not self.has_nonrandom_instance_name:
            self.instanceName = thename
            self.has_nonrandom_instance_name = True
        #else:
        #    logmessage("Not resetting name of " + self.instanceName)
        return
    def set_random_instance_name(self):
        """Sets the instanceName attribute to a random value."""
        self.instanceName = str(get_unique_name())
        self.has_nonrandom_instance_name = False
    def _set_instance_name_recursively(self, thename):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        #logmessage("Change " + str(self.instanceName) + " to " + str(thename))
        #if not self.has_nonrandom_instance_name:
        self.instanceName = thename
        self.has_nonrandom_instance_name = True
        for aname in self.__dict__:
            if hasattr(self, aname) and isinstance(getattr(self, aname), DAObject):
                #logmessage("ASDF Setting " + str(thename) + " for " + str(aname))
                getattr(self, aname)._set_instance_name_recursively(thename + '.' + aname)
        return
    def _mark_as_gathered_recursively(self):
        self.gathered = True
        for aname in self.__dict__:
            if hasattr(self, aname) and isinstance(getattr(self, aname), DAObject):
                getattr(self, aname)._mark_as_gathered_recursively()
    def _reset_gathered_recursively(self):
        for aname in self.__dict__:
            if hasattr(self, aname) and isinstance(getattr(self, aname), DAObject):
                getattr(self, aname)._reset_gathered_recursively()
    def _map_info(self):
        return None
    def __getattr__(self, thename):
        if thename.startswith('_'):
            return object.__getattribute__(self, thename)
        else:
            var_name = object.__getattribute__(self, 'instanceName') + "." + thename
            raise NameError("name '" + var_name + "' is not defined")
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
    def initializeAttribute(self, *pargs, **kwargs):
        """Defines an attribute for the object, setting it to a newly initialized object.
        The first argument is the name of the attribute and the second argument is type
        of the new object that will be initialized.  E.g., 
        client.initializeAttribute('mother', Individual) initializes client.mother as an
        Individual with instanceName "client.mother"."""
        pargs = [x for x in pargs]
        name = pargs.pop(0)
        objectType = pargs.pop(0)
        if name in self.__dict__:
            return
        else:
            object.__setattr__(self, name, objectType(self.instanceName + "." + name, *pargs, **kwargs))
            self.attrList.append(name)
    def attribute_defined(self, name):
        """Returns True or False depending on whether the given attribute is defined."""
        return hasattr(self, name)
    def attr(self, name):
        """Returns the value of the given attribute, or None if the attribute is not defined"""
        if hasattr(self, name):
            return getattr(self, name)
        return None
    def __str__(self):
        if hasattr(self, 'name'):
            return unicode(self.name)
        return self.object_name()
    def __unicode__(self):
        return unicode(self.__str__())
    def __dir__(self):
        return self.attrList
    def pronoun_possessive(self, target, **kwargs):
        """Returns "its <target>." """
        output = its(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        """Returns it."""
        return word('it', **kwargs)
    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)
    def pronoun_subjective(self, **kwargs):        
        """Same as pronoun()."""
        return self.pronoun(**kwargs)
    def __setattr__(self, key, value):
        if isinstance(value, DAObject) and not value.has_nonrandom_instance_name:
            value.has_nonrandom_instance_name = True
            value.instanceName = self.instanceName + '.' + str(key)
        return super(DAObject, self).__setattr__(key, value)

class DAList(DAObject):
    """The base class for lists of things."""
    def init(self, *pargs, **kwargs):
        self.elements = list()
        self.auto_gather = True
        self.ask_number = False
        self.minimum_number = None
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
        if 'complete_attribute' in kwargs:
            self.complete_attribute = kwargs['complete_attribute']
            del kwargs['complete_attribute']
        if not hasattr(self, 'complete_attribute'):
            self.complete_attribute = None
        return super(DAList, self).init(*pargs, **kwargs)
    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered
        return
    def reset_gathered(self, recursive=False):
        """Indicates that there is more to be gathered"""
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if recursive:
            self._reset_gathered_recursively()
    def clear(self):
        """Removes all the items from the list."""
        self.elements = list()
    def _set_instance_name_recursively(self, thename):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        indexno = 0
        for item in self.elements:
            if isinstance(item, DAObject):
                item._set_instance_name_recursively(thename + '[' + str(indexno) + ']')
            indexno += 1
        return super(DAList, self)._set_instance_name_recursively(thename)
    def _mark_as_gathered_recursively(self):
        for item in self.elements:
            if isinstance(item, DAObject):
                item._mark_as_gathered_recursively()
        return super(DAList, self)._mark_as_gathered_recursively()
    def _reset_gathered_recursively(self):
        self.reset_gathered()
        for item in self.elements:
            if isinstance(item, DAObject):
                item._reset_gathered_recursively()
        return super(DAList, self)._reset_gathered_recursively()
    def appendObject(self, *pargs, **kwargs):
        """Creates a new object and adds it to the list.
        Takes an optional argument, which is the type of object
        the new object should be.  If no object type is provided,
        the object type given by .objectFunction is used, and if 
        that is not set, DAObject is used."""
        objectFunction = None
        if len(pargs) > 0:
            pargs = [x for x in pargs]
            objectFunction = pargs.pop(0)
        if objectFunction is None:
            if self.object_type is not None:
                objectFunction = self.object_type
            else:
                objectFunction = DAObject
        newobject = objectFunction(self.instanceName + '[' + str(len(self.elements)) + ']', *pargs, **kwargs)
        self.elements.append(newobject)
        return newobject
    def append(self, *pargs):
        """Adds the arguments to the end of the list."""
        for parg in pargs:
            if isinstance(parg, DAObject) and not parg.has_nonrandom_instance_name:
                parg.fix_instance_name(parg.instanceName, self.instanceName + '[' + str(len(self.elements)) + ']')
                #parg.has_nonrandom_instance_name = True
                #parg.instanceName = self.instanceName + '[' + str(len(self.elements)) + ']'
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
        self._trigger_gather()
        return self.__getitem__(0)
    def last(self):
        """Returns the last element of the list"""
        self._trigger_gather()
        if len(self.elements) == 0:
            return self.__getitem__(0)
        return self.__getitem__(len(self.elements)-1)
    def does_verb(self, the_verb, **kwargs):
        """Returns the appropriate conjugation of the given verb depending on whether
        there is only one element in the list or multiple elements.  E.g.,
        case.plaintiff.does_verb('sue') will return "sues" if there is one plaintiff
        and "sue" if there is more than one plaintiff."""
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense)
        else:
            if self.number() > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        if self.number() > 1:
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
        """If the variable name is "plaintiff" and the target is "fish,"
        returns "plaintiff's fish" if there is one item in the list,
        and "plaintiffs' fish" if there is more than one item in the
        list.

        """
        return possessify(self.as_noun(), target, plural=(self.number() > 1))
    def as_noun(self, *pargs, **kwargs):
        """Returns a human-readable expression of the object based on its instanceName,
        using singular or plural depending on whether the list has one element or more
        than one element.  E.g., case.plaintiff.child.as_noun() returns "child" or
        "children," as appropriate.  If an argument is supplied, the argument is used
        instead of the instanceName."""
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        the_noun = re.sub(r'_', ' ', the_noun)
        if len(pargs) > 0:
            the_noun = pargs[0]
        if (self.number() > 1 or self.number() == 0 or ('plural' in kwargs and kwargs['plural'])) and not ('singular' in kwargs and kwargs['singular']):
            output = noun_plural(the_noun)
            if 'article' in kwargs and kwargs['article']:
                if 'some' in kwargs and kwargs['some']:
                    output = some(output)
            elif 'this' in kwargs and kwargs['this']:
                output = these(output)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
        else:
            output = the_noun
            if 'article' in kwargs and kwargs['article']:
                output = indefinite_article(output)
            elif 'this' in kwargs and kwargs['this']:
                output = this(output)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
    def number(self):
        """Returns the number of elements in the list.  Forces the gathering of the
        elements if necessary."""
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return len(self.elements)
    def number_as_word(self):
        """Returns the number of elements in the list, spelling out the number if ten 
        or below.  Forces the gathering of the elements if necessary."""
        return nice_number(self.number())
    def gather(self, number=None, item_object_type=None, minimum=None, complete_attribute=None):
        """Causes the elements of the list to be gathered and named.  Returns True."""
        if hasattr(self, 'gathered') and self.gathered:
            return True
        if item_object_type is None and self.object_type is not None:
            item_object_type = self.object_type
        if complete_attribute is None and self.complete_attribute is not None:
            complete_attribute = self.complete_attribute
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        if number is None and self.ask_number:
            number = self.target_number
        if minimum is None:
            minimum = self.minimum_number
        if number is None and minimum is None:
            if len(self.elements) == 0:
                if self.there_are_any:
                    minimum = 1
                else:
                    minimum = 0
        while len(self.elements) < minimum:
            the_length = len(self.elements)
            if item_object_type is not None:
                self.appendObject(item_object_type)
            str(self.__getitem__(the_length))
            if item_object_type is not None and complete_attribute is not None:
                getattr(self.__getitem__(the_length), complete_attribute)
        for elem in self.elements:
            str(elem)
            if item_object_type is not None and complete_attribute is not None:
                getattr(elem, complete_attribute)
        the_length = len(self.elements)
        if number is not None:
            while the_length < int(number):
                if item_object_type is not None:
                    self.appendObject(item_object_type)
                str(self.__getitem__(the_length))
                if item_object_type is not None and complete_attribute is not None:
                    getattr(self.__getitem__(the_length), complete_attribute)
        elif minimum != 0:
            while self.there_is_another:
                del self.there_is_another
                if item_object_type is not None:
                    self.appendObject(item_object_type)
                str(self.__getitem__(the_length))
                if item_object_type is not None and complete_attribute is not None:
                    getattr(self.__getitem__(the_length), complete_attribute)
        if self.auto_gather:
            self.gathered = True
        docassemble.base.functions.set_gathering_mode(False, self.instanceName)
        return True
    def comma_and_list(self, **kwargs):
        """Returns the elements of the list, separated by commas, with 
        "and" before the last element."""
        self._trigger_gather()
        return comma_and_list(self.elements, **kwargs)
    def __contains__(self, item):
        self._trigger_gather()
        return self.elements.__contains__(item)
    def __iter__(self):
        self._trigger_gather()
        return self.elements.__iter__()
    def _target_or_actual(self):
        if hasattr(self, 'gathered') and self.gathered:
            return len(self.elements)
        return self.target_number
    def __len__(self):
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return self.elements.__len__()
    def __delitem__(self, index):
        return self.elements.__delitem__(index)
    def __reversed__(self):
        self._trigger_gather()
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
        if isinstance(value, DAObject) and not value.has_nonrandom_instance_name:
            value.has_nonrandom_instance_name = True
            value.instanceName = self.instanceName + '[' + str(index) + ']'
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
        self._trigger_gather()
        return self.comma_and_list()
    def __unicode__(self):
        self._trigger_gather()
        return unicode(self.__str__())
    def union(self, other_set):
        """Returns a Python set consisting of the elements of current list,
        considered as a set, combined with the elements of the other_set.

        """
        self._trigger_gather()
        return DASet(elements=set(self.elements).union(setify(other_set)))
    def intersection(self, other_set):
        """Returns a Python set consisting of the elements of the current list,
        considered as a set, that also exist in the other_set.

        """
        self._trigger_gather()
        return DASet(elements=set(self.elements).intersection(setify(other_set)))
    def difference(self, other_set):
        """Returns a Python set consisting of the elements of the current list,
        considered as a set, that do not exist in the other_set.

        """
        self._trigger_gather()
        return DASet(elements=set(self.elements).difference(setify(other_set)))
    def isdisjoint(self, other_set):
        """Returns True if no elements overlap between the current list,
        considered as a set, and the other_set.  Otherwise, returns
        False.

        """
        self._trigger_gather()
        return set(self.elements).isdisjoint(setify(other_set))
    def issubset(self, other_set):
        """Returns True if the current list, considered as a set, is a subset
        of the other_set.  Otherwise, returns False.

        """
        self._trigger_gather()
        return set(self.elements).issubset(setify(other_set))
    def issuperset(self, other_set):
        """Returns True if the other_set is a subset of the current list,
        considered as a set.  Otherwise, returns False.

        """
        self._trigger_gather()
        return set(self.elements).issuperset(setify(other_set))
    def pronoun_possessive(self, target, **kwargs):
        """Given a word like "fish," returns "her fish," "his fish," or "their fish," as appropriate."""
        if self.number() == 1:
            self._trigger_gather()
            return self.elements[0].pronoun_possessive(target, **kwargs)
        output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        """Returns a pronoun like "you," "her," or "him," "it", or "them," as appropriate."""
        if self.number() == 1:
            self._trigger_gather()
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
        if self.number() == 1:
            self._trigger_gather()
            return self.elements[0].pronoun_subjective(**kwargs)
        output = word('they', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)

class DADict(DAObject):
    """A base class for objects that behave like Python dictionaries."""
    def init(self, *pargs, **kwargs):
        self.elements = dict()
        self.auto_gather = True
        self.ask_number = False
        self.minimum_number = None
        if 'elements' in kwargs:
            self.elements.update(kwargs['elements'])
            self.gathered = True
            del kwargs['elements']
        if 'object_type' in kwargs:
            self.object_type = kwargs['object_type']
            del kwargs['object_type']
        if not hasattr(self, 'object_type'):
            self.object_type = None
        if 'complete_attribute' in kwargs:
            self.complete_attribute = kwargs['complete_attribute']
            del kwargs['complete_attribute']
        if not hasattr(self, 'complete_attribute'):
            self.complete_attribute = None
        return super(DADict, self).init(*pargs, **kwargs)
    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered
        return
    def _set_instance_name_recursively(self, thename):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        #logmessage("DICT instance name recursive for " + str(self.instanceName) + " to " + str(thename))
        for key, value in self.elements.iteritems():
            #logmessage("QWER Setting " + str(thename) + " for " + str(key))
            if isinstance(value, DAObject):
                value._set_instance_name_recursively(thename + '[' + repr(key) + ']')
        #logmessage("Change " + str(self.instanceName) + " to " + str(thename))
        return super(DADict, self)._set_instance_name_recursively(thename)
    def _mark_as_gathered_recursively(self):
        for key, value in self.elements.iteritems():
            if isinstance(value, DAObject):
                value._mark_as_gathered_recursively()
        return super(DADict, self)._mark_as_gathered_recursively()
    def _reset_gathered_recursively(self):
        self.reset_gathered()
        for key, value in self.elements.iteritems():
            if isinstance(value, DAObject):
                value._reset_gathered_recursively()
        return super(DADict, self)._reset_gathered_recursively()
    def initializeObject(self, *pargs, **kwargs):
        """Creates a new object and creates an entry in the dictionary for it.
        The first argument is the name of the dictionary key to set.
        Takes an optional second argument, which is the type of object
        the new object should be.  If no object type is provided, the
        object type given by .object_type is used, and if that is not
        set, DAObject is used.

        """
        objectFunction = None
        pargs = [x for x in pargs]
        entry = pargs.pop(0)
        if len(pargs) > 0:
            objectFunction = pargs.pop(0)
        if objectFunction is None:
            if self.object_type is not None:
                objectFunction = self.object_type
            else:
                objectFunction = DAObject
        newobject = objectFunction(self.instanceName + '[' + repr(entry) + ']', *pargs, **kwargs)
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
    def reset_gathered(self, recursive=False):
        """Indicates that there is more to be gathered"""
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if recursive:
            self._reset_gathered_recursively()
    def does_verb(self, the_verb, **kwargs):
        """Returns the appropriate conjugation of the given verb depending on
        whether there is only one key in the dictionary or multiple
        keys.  E.g., player.does_verb('finish') will return "finishes" if there
        is one player and "finish" if there is more than one
        player."""
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense)
        else:
            if self.number() > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        if self.number() > 1:
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
    def as_noun(self, *pargs, **kwargs):
        """Returns a human-readable expression of the object based on its
        instanceName, using singular or plural depending on whether
        the dictionary has one key or more than one key.  E.g.,
        player.as_noun() returns "player" or "players," as
        appropriate.  If an argument is supplied, the argument is used
        as the noun instead of the instanceName."""
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        the_noun = re.sub(r'_', ' ', the_noun)
        if len(pargs) > 0:
            the_noun = pargs[0]
        if (self.number() > 1 or self.number() == 0 or ('plural' in kwargs and kwargs['plural'])) and not ('singular' in kwargs and kwargs['singular']):
            output = noun_plural(the_noun)
            if 'article' in kwargs and kwargs['article']:
                if 'some' in kwargs and kwargs['some']:
                    output = some(output)
            elif 'this' in kwargs and kwargs['this']:
                output = these(output)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
        else:
            output = the_noun
            if 'article' in kwargs and kwargs['article']:
                output = indefinite_article(output)
            elif 'this' in kwargs and kwargs['this']:
                output = this(output)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
    def possessive(self, target):
        """If the variable name is "plaintiff" and the target is "fish,"
        returns "plaintiff's fish" if there is one item in the dictionary,
        and "plaintiffs' fish" if there is more than one item in the
        list.

        """
        return possessify(self.as_noun(), target, plural=(self.number() > 1))
    def number(self):
        """Returns the number of keys in the dictionary.  Forces the gathering of the
        dictionary items if necessary."""
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return len(self.elements)
    def number_as_word(self):
        """Returns the number of keys in the dictionary, spelling out the number if ten 
        or below.  Forces the gathering of the dictionary items if necessary."""
        return nice_number(self.number())
    def gather(self, item_object_type=None, number=None, minimum=None, complete_attribute=None):
        """Causes the dictionary items to be gathered and named.  Returns True."""
        if hasattr(self, 'gathered') and self.gathered:
            return True
        if item_object_type is None and self.object_type is not None:
            item_object_type = self.object_type
        if complete_attribute is None and self.complete_attribute is not None:
            complete_attribute = self.complete_attribute
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        for elem in sorted(self.elements.values()):
            str(elem)
            if item_object_type is not None and complete_attribute is not None:
                getattr(elem, complete_attribute)
        if number is None and self.ask_number:
            number = self.target_number
        if minimum is None:
            minimum = self.minimum_number
        if number is None and minimum is None:
            if len(self.elements) == 0:
                if self.there_are_any:
                    minimum = 1
                else:
                    minimum = 0
            else:
                minimum = 1
        #logmessage("foo foo call there_is_another")
        while (number is not None and len(self.elements) < int(number)) or (minimum is not None and len(self.elements) < int(minimum)) or (self.ask_number is False and minimum != 0 and self.there_is_another):
            #logmessage("foo foo done there_is_another")
            if item_object_type is not None:
                self.initializeObject(self.new_item_name, item_object_type)
                delattr(self, 'new_item_name')
                self._new_item_init_callback()
            else:
                self.new_item_name
                if hasattr(self, 'new_item_value'):
                    self.elements[self.new_item_name] = self.new_item_value
                    delattr(self, 'new_item_value')
                    delattr(self, 'new_item_name')
                    if hasattr(self, 'there_is_another'):
                        delattr(self, 'there_is_another')
                else:
                    the_name = self.new_item_name
                    delattr(self, 'new_item_name')
                    if hasattr(self, 'there_is_another'):
                        delattr(self, 'there_is_another')
                    self.__getitem__(the_name)
            if hasattr(self, 'there_is_another'):
                delattr(self, 'there_is_another')
        if self.auto_gather:
            self.gathered = True
        docassemble.base.functions.set_gathering_mode(False, self.instanceName)
        #logmessage("foo foo done")
        return True
    def _new_item_init_callback(self):
        for elem in sorted(self.elements.values()):
            str(elem)
            if self.object_type is not None and self.complete_attribute is not None:
                getattr(elem, self.complete_attribute)
        return
    def comma_and_list(self, **kwargs):
        """Returns the keys of the list, separated by commas, with 
        "and" before the last key."""
        self._trigger_gather()
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
        self._trigger_gather()
        return self.elements.__contains__(item)
    def keys(self):
        """Returns the keys of the dictionary as a Python list."""
        self._trigger_gather()
        return self.elements.keys()
    def values(self):
        """Returns the values of the dictionary as a Python list."""
        self._trigger_gather()
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
        self._trigger_gather()
        return self.elements.items()
    def iteritems(self):
        """Iterates through the keys and values of the dictionary."""
        self._trigger_gather()
        return self.elements.iteritems()
    def iterkeys(self):
        """Iterates through the keys of the dictionary."""
        self._trigger_gather()
        return self.elements.iterkeys()
    def itervalues(self):
        """Iterates through the values of the dictionary."""
        self._trigger_gather()
        return self.elements.itervalues()
    def __iter__(self):
        self._trigger_gather()
        return self.elements.__iter__()
    def _target_or_actual(self):
        if hasattr(self, 'gathered') and self.gathered:
            return len(self.elements)
        return self.target_number
    def __len__(self):
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return self.elements.__len__()
    def __reversed__(self):
        self._trigger_gather()
        return self.elements.__reversed__()
    def __delitem__(self, key):
        return self.elements.__delitem__(key)
    def __missing__(self, key):
        return self.elements.__missing__(key)
    def __hash__(self, the_object):
        self._trigger_gather()
        return self.elements.__hash__(the_object)
    def __str__(self):
        self._trigger_gather()
        return self.comma_and_list()
    def __unicode__(self):
        self._trigger_gather()
        return unicode(self.__str__())
    def union(self, other_set):
        """Returns a Python set consisting of the keys of the current dict,
        considered as a set, combined with the elements of the other_set.

        """
        self._trigger_gather()
        return DASet(elements=set(self.elements.values()).union(setify(other_set)))
    def intersection(self, other_set):
        """Returns a Python set consisting of the keys of the current dict,
        considered as a set, that also exist in the other_set.

        """
        self._trigger_gather()
        return DASet(elements=set(self.elements.values()).intersection(setify(other_set)))
    def difference(self, other_set):
        """Returns a Python set consisting of the keys of the current dict,
        considered as a set, that do not exist in the other_set.

        """
        self._trigger_gather()
        return DASet(elements=set(self.elements.values()).difference(setify(other_set)))
    def isdisjoint(self, other_set):
        """Returns True if no elements overlap between the keys of the current
        dict, considered as a set, and the other_set.  Otherwise,
        returns False.

        """
        self._trigger_gather()
        return set(self.elements.values()).isdisjoint(setify(other_set))
    def issubset(self, other_set):
        """Returns True if the keys of the current dict, considered as a set,
        is a subset of the other_set.  Otherwise, returns False.

        """
        self._trigger_gather()
        return set(self.elements.values()).issubset(setify(other_set))
    def issuperset(self, other_set):
        """Returns True if the other_set is a subset of the keys of the
        current dict, considered as a set.  Otherwise, returns False.

        """
        self._trigger_gather()
        return set(self.elements.values()).issuperset(setify(other_set))
    def pronoun_possessive(self, target, **kwargs):
        """Returns "their <target>." """
        output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        """Returns them, or the pronoun for the only element."""
        if self.number() == 1:
            self._trigger_gather()
            return list(self.elements.values())[0].pronoun(**kwargs)
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
    def init(self, *pargs, **kwargs):
        self.elements = set()
        self.auto_gather = True
        self.ask_number = False
        self.minimum_number = None
        if 'elements' in kwargs:
            self.add(kwargs['elements'])
            self.gathered = True
            del kwargs['elements']
        return super(DASet, self).init(*pargs, **kwargs)
    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered
        return
    def reset_gathered(self, recursive=False):
        """Indicates that there is more to be gathered"""
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if recursive:
            self._reset_gathered_recursively()
    def _reset_gathered_recursively(self):
        self.reset_gathered()
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
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense)
        else:
            if self.number() > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        if self.number() > 1:
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
    def as_noun(self, *pargs, **kwargs):
        """Returns a human-readable expression of the object based on its
        instanceName, using singular or plural depending on whether
        the set has one item in it or multiple items.  E.g.,
        player.as_noun() returns "player" or "players," as
        appropriate.  If an argument is supplied, the argument is used
        instead of the instanceName.

        """
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        the_noun = re.sub(r'_', ' ', the_noun)
        if len(pargs) > 0:
            the_noun = pargs[0]
        if (self.number() > 1 or self.number() == 0 or ('plural' in kwargs and kwargs['plural'])) and not ('singular' in kwargs and kwargs['singular']):
            output = noun_plural(the_noun)
            if 'article' in kwargs and kwargs['article']:
                if 'some' in kwargs and kwargs['some']:
                    output = some(output)
            elif 'this' in kwargs and kwargs['this']:
                output = these(output)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
        else:
            output = the_noun
            if 'article' in kwargs and kwargs['article']:
                output = indefinite_article(output)
            elif 'this' in kwargs and kwargs['this']:
                output = this(output)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
    def number(self):
        """Returns the number of items in the set.  Forces the gathering of
        the items if necessary.

        """
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return len(self.elements)
    def number_as_word(self):
        """Returns the number of items in the set, spelling out the number if
        ten or below.  Forces the gathering of the items if necessary.

        """
        return nice_number(self.number())
    def gather(self, number=None, minimum=None):
        """Causes the items in the set to be gathered.  Returns True.

        """
        if hasattr(self, 'gathered') and self.gathered:
            return True
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        for elem in self.elements:
            str(elem)
        if number is None and self.ask_number:
            number = self.target_number
        if minimum is None:
            minimum = self.minimum_number
        if number is None and minimum is None:
            if len(self.elements) == 0:
                if self.there_are_any:
                    minimum = 1
                else:
                    minimum = 0
            else:
                minimum = 1
        while (number is not None and len(self.elements) < int(number)) or (minimum is not None and len(self.elements) < int(minimum)) or (self.ask_number is False and minimum != 0 and self.there_is_another):
            self.add(self.new_item)
            del self.new_item
            for elem in self.elements:
                str(elem)
            if hasattr(self, 'there_is_another'):
                del self.there_is_another
        if self.auto_gather:
            self.gathered = True
        docassemble.base.functions.set_gathering_mode(False, self.instanceName)
        return True
    def comma_and_list(self, **kwargs):
        """Returns the items in the set, separated by commas, with 
        "and" before the last item."""
        self._trigger_gather()
        return comma_and_list(sorted(map(str, self.elements)), **kwargs)
    def __contains__(self, item):
        self._trigger_gather()
        return self.elements.__contains__(item)
    def __iter__(self):
        self._trigger_gather()
        return self.elements.__iter__()
    def _target_or_actual(self):
        if hasattr(self, 'gathered') and self.gathered:
            return len(self.elements)
        return self.target_number
    def __len__(self):
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return self.elements.__len__()
    def __reversed__(self):
        self._trigger_gather()
        return self.elements.__reversed__()
    def __and__(self, operand):
        self._trigger_gather()
        return self.elements.__and__(operand)
    def __or__(self, operand):
        self._trigger_gather()
        return self.elements.__or__(operand)
    def __iand__(self, operand):
        self._trigger_gather()
        return self.elements.__iand__(operand)
    def __ior__(self, operand):
        self._trigger_gather()
        return self.elements.__ior__(operand)
    def __isub__(self, operand):
        self._trigger_gather()
        return self.elements.__isub__(operand)
    def __ixor__(self, operand):
        self._trigger_gather()
        return self.elements.__ixor__(operand)
    def __rand__(self, operand):
        self._trigger_gather()
        return self.elements.__rand__(operand)
    def __ror__(self, operand):
        self._trigger_gather()
        return self.elements.__ror__(operand)
    def __hash__(self, the_object):
        self._trigger_gather()
        return self.elements.__hash__(the_object)
    def __str__(self):
        self._trigger_gather()
        return self.comma_and_list()
    def __unicode__(self):
        self._trigger_gather()
        return unicode(self.__str__())
    def union(self, other_set):
        """Returns a Python set consisting of the elements of current set
        combined with the elements of the other_set.

        """
        self._trigger_gather()
        return DASet(elements=self.elements.union(setify(other_set)))
    def intersection(self, other_set):
        """Returns a Python set consisting of the elements of the current set
        that also exist in the other_set.

        """
        self._trigger_gather()
        return DASet(elements=self.elements.intersection(setify(other_set)))
    def difference(self, other_set):
        """Returns a Python set consisting of the elements of the current set
        that do not exist in the other_set.

        """
        self._trigger_gather()
        return DASet(elements=self.elements.difference(setify(other_set)))
    def isdisjoint(self, other_set):
        """Returns True if no elements overlap between the current set and the
        other_set.  Otherwise, returns False."""
        self._trigger_gather()
        return self.elements.isdisjoint(setify(other_set))
    def issubset(self, other_set):
        """Returns True if the current set is a subset of the other_set.
        Otherwise, returns False.

        """
        self._trigger_gather()
        return self.elements.issubset(setify(other_set))
    def issuperset(self, other_set):
        """Returns True if the other_set is a subset of the current set.
        Otherwise, returns False.

        """
        self._trigger_gather()
        return self.elements.issuperset(setify(other_set))
    def pronoun_possessive(self, target, **kwargs):
        """Returns "their <target>." """
        output = their(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return(capitalize(output))
        else:
            return(output)            
    def pronoun(self, **kwargs):
        """Returns them, or the pronoun for the one element."""
        if self.number() == 1:
            self._trigger_gather()
            return list(self.elements)[0].pronoun(**kwargs)
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
    def init(self, *pargs, **kwargs):
        #logmessage("init")
        if 'filename' in kwargs:
            self.filename = kwargs['filename']
            self.has_specific_filename = True
        else:
            self.has_specific_filename = False
        if 'mimetype' in kwargs:
            self.mimetype = kwargs['mimetype']
        if 'extension' in kwargs:
            self.extension = kwargs['extension']
        if 'number' in kwargs:
            self.number = kwargs['number']
            self.ok = True
        else:
            self.ok = False
        if hasattr(self, 'extension') and self.extension == 'pdf' and 'make_pngs' in kwargs and kwargs['make_pngs']:
            self._make_pngs_for_pdf()
        return
    def set_mimetype(self, mimetype):
        """Sets the MIME type of the file"""
        self.mimetype = mimetype
        #if mimetype == 'image/jpeg':
        #    self.extension = 'jpg'
        #else:
        self.extension = re.sub(r'^\.', '', mimetypes.guess_extension(mimetype))
    def __str__(self):
        return self.show()
    def __unicode__(self):
        return unicode(self.__str__())
    def initialize(self, **kwargs):
        """Creates the file on the system if it does not already exist, and ensures that the file is ready to be used."""
        #logmessage("initialize")
        if not hasattr(self, 'filename'):
            if hasattr(self, 'extension'):
                self.filename = kwargs.get('filename', 'file.' + self.extension)
            else:
                self.filename = kwargs.get('filename', 'file.txt')
        if not hasattr(self, 'number'):
            yaml_filename = None
            uid = None
            if hasattr(docassemble.base.functions.this_thread, 'current_info'):
                yaml_filename = docassemble.base.functions.this_thread.current_info.get('yaml_filename', None)
                uid = docassemble.base.functions.this_thread.current_info.get('session', None)
                #logmessage("yaml_filename is " + str(yaml_filename) + " and uid is " + str(uid))
            self.number = server.get_new_file_number(uid, self.filename, yaml_file_name=yaml_filename)
            self.ok = True
            self.extension, self.mimetype = server.get_ext_and_mimetype(self.filename)
        self.retrieve()
        the_path = self.path()
        if not (os.path.isfile(the_path) or os.path.islink(the_path)):
            self.file_info['savedfile'].save()
    def retrieve(self):
        """Ensures that the file is ready to be used."""
        if not self.ok:
            self.initialize()
        if not hasattr(self, 'number'):
            raise Exception("Cannot retrieve a file without a file number.")
        docassemble.base.functions.this_thread.open_files.add(self)
        #logmessage("Retrieve: calling file finder")
        if self.has_specific_filename:
            self.file_info = server.file_number_finder(self.number, filename=self.filename)
        else:
            self.file_info = server.file_number_finder(self.number)
    def slurp(self):
        """Returns the contents of the file."""
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File " + str(the_path) + " does not exist yet.")
        with open(the_path, 'rU') as f:
            return(f.read())
    def readlines(self):
        """Returns the contents of the file."""
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File does not exist yet.")
        with open(path, 'rU') as f:
            return(f.readlines())
    def write(self, content):
        """Writes the given content to the file, replacing existing contents."""
        self.retrieve()
        the_path = self.path()
        with open(path, 'w') as f:
            f.write(content)
    def copy_into(self, filename):
        """Makes the contents of the file the same as those of the given filename."""
        self.retrieve()
        shutil.copyfile(filename, self.path())
    def _make_pngs_for_pdf(self):
        if not hasattr(self, '_taskscreen'):
            setattr(self, '_taskscreen', server.make_png_for_pdf(self, 'screen'))
        if not hasattr(self, '_taskpage'):
            setattr(self, '_taskpage', server.make_png_for_pdf(self, 'page'))
    def page_path(self, page, prefix, wait=True):
        """Returns a path and filename at which a PDF page image can be accessed."""
        if not hasattr(self, 'number'):
            raise Exception("Cannot get path of file without a file number.")
        if not hasattr(self, 'file_info'):
            self.retrieve()
        if 'fullpath' not in self.file_info:
            raise Exception("fullpath not found.")
        if 'pages' not in self.file_info:
            raise Exception("number of pages not found.")
        test_path = self.file_info['path'] + prefix + '-in-progress'
        if os.path.isfile(test_path) and hasattr(self, '_task' + prefix):
            if wait:
                server.wait_for_task(getattr(self, '_task' + prefix))
            else:
                return None
        max_pages = 1 + int(self.file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        the_path = self.file_info['path'] + prefix + '-' + (formatter % int(page)) + '.png'
        if os.path.isfile(the_path):
            return the_path
        if hasattr(self, '_task' + prefix):
            if server.wait_for_task(getattr(self, '_task' + prefix)):
                self.retrieve()
                the_path = self.file_info['path'] + prefix + '-' + str(int(page)) + '.png'
                if os.path.isfile(the_path):
                    return the_path
        return None
    def path(self):
        """Returns a path and filename at which the file can be accessed."""
        #logmessage("path")
        if not hasattr(self, 'number'):
            raise Exception("Cannot get path of file without a file number.")
        if not hasattr(self, 'file_info'):
            self.retrieve()
        if 'fullpath' not in self.file_info:
            raise Exception("fullpath not found.")
        return self.file_info['fullpath']
    def commit(self):
        """Ensures that changes to the file are saved and will be available in
        the future.

        """
        #logmessage("commit")
        if hasattr(self, 'file_info') and 'savedfile' in self.file_info:
            #logmessage("Committed " + str(self.number))
            self.file_info['savedfile'].finalize()
    def show(self, width=None):
        """Inserts markup that displays the file as an image.  Takes an
        optional keyword argument width.

        """
        #logmessage("show")
        if not self.ok:
            return('')
        if hasattr(self, 'number') and hasattr(self, 'extension') and self.extension == 'pdf':
            self.page_path(1, 'page')
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return docassemble.base.file_docx.image_for_docx(self.number, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.docx_template, width=width)
        else:
            if width is not None:
                return('[FILE ' + str(self.number) + ', ' + str(width) + ']')
            else:
                return('[FILE ' + str(self.number) + ']')
    def url_for(self):
        """Returns a URL to the file."""
        return server.url_finder(self)

class DAFileCollection(DAObject):
    """Used internally by docassemble to refer to a collection of DAFile
    objects, usually representing the same document in different
    formats.  Attributes represent file types.  The attachments
    feature generates objects of this type.

    """
    def init(self, *pargs, **kwargs):
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

class DAEmailRecipientList(DAList):
    def init(self, *pargs, **kwargs):
        #logmessage("DAEmailRecipientList: pargs is " + str(pargs) + " and kwargs is " + str(kwargs))
        self.object_type = DAEmailRecipient
        super(DAEmailRecipientList, self).init(**kwargs)
        for parg in pargs:
            if type(parg) is list:
                #logmessage("DAEmailRecipientList: parg type is list")
                for item in parg:
                    self.appendObject(DAEmailRecipient, **item)
            elif type(parg) is dict:
                #logmessage("DAEmailRecipientList: parg type is dict")
                self.appendObject(DAEmailRecipient, **parg)
    
class DAEmailRecipient(DAObject):
    def init(self, *pargs, **kwargs):
        #logmessage("DAEmailRecipient: pargs is " + str(pargs) + " and kwargs is " + str(kwargs))
        if 'address' in kwargs:
            self.address = kwargs['address']
            del kwargs['address']
        if 'name' in kwargs:
            self.name = kwargs['name']
            del kwargs['name']
        return super(DAEmailRecipient, self).init(*pargs, **kwargs)
    def email_address(self, include_name=None):
        """Returns a properly formatted e-mail address for the recipient."""
        if hasattr(self, 'empty') and self.empty:
            return ''
        if include_name is True or (include_name is not False and self.name is not None and self.name != ''):
            return('"' + nodoublequote(self.name) + '" <' + str(self.address) + '>')
        return(str(self.address))
    def exists(self):
        return hasattr(self, 'address')
    def __str__(self):
        if hasattr(self, 'name'):
            name = self.name
        else:
            name = ''
        if hasattr(self, 'empty') and self.empty:
            return ''
        if self.address == '' and name == '':
            return 'EMAIL NOT DEFINED'
        if self.address == '' and name != '':
            return name
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return unicode(self.address)
        if name == '' and self.address != '':
            return '[' + unicode(self.address) + '](mailto:' + unicode(self.address) + ')' 
        return '[' + unicode(name) + '](mailto:' + unicode(self.address) + ')'

class DAEmail(DAObject):
    def __str__(self):
        return("This is an e-mail")

class DATemplate(DAObject):
    """The class used for Markdown templates.  A template block saves to
    an object of this type.  The two attributes are "subject" and 
    "content." """
    def init(self, *pargs, **kwargs):
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

# class DATable(DAObject):
#     """The class used for tables.  A table block saves to
#     an object of this type."""
#     def render(self):
#         return(self.content)
#     def __str__(self):
#         return(self.render())

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
            arg._trigger_gather()
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
    return codecs.encode(text.encode('utf8'), 'base64').decode().replace('\n', '')

def setify(item, output=set()):
    if isinstance(item, DAObject) and hasattr(item, 'elements'):
        setify(item.elements, output)
    elif hasattr(item, '__iter__'):
        for subitem in item:
            setify(subitem, output)
    else:
        output.add(item)
    return output

def objects_from_file(file_ref, recursive=True, gathered=True, name=None):
    """A utility function for initializing a group of objects from a YAML file written in a certain format."""
    from docassemble.base.core import DAObject, DAList, DADict, DASet
    if name is None:
        frame = inspect.stack()[1][0]
        #logmessage("co_name is " + str(frame.f_code.co_names))
        the_names = frame.f_code.co_names
        if len(the_names) == 2:
            thename = the_names[1]
        else:
            thename = None
        del frame
    else:
        thename = name
    #logmessage("objects_from_file: thename is " + str(thename))
    file_info = server.file_finder(file_ref, folder='sources')
    if 'path' not in file_info:
        raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' not found')
    if thename is None:
        objects = DAList()
    else:
        objects = DAList(thename)
    objects.gathered = True
    is_singular = True
    with open(file_info['fullpath'], 'rU') as fp:
        for document in yaml.load_all(fp):
            new_objects = recurse_obj(document, recursive=recursive)
            if type(new_objects) is list:
                is_singular = False
                for obj in new_objects:
                    objects.append(obj)
            else:
                objects.append(new_objects)
    if is_singular and len(objects.elements) == 1:
        objects = objects.elements[0]
    #logmessage("Returning for a " + str(thename))
    if thename is not None and isinstance(objects, DAObject):
        objects._set_instance_name_recursively(thename)
    if (isinstance(objects, DAList) or isinstance(objects, DADict) or isinstance(objects, DASet)) and not gathered:
        objects._reset_gathered_recursively()
    #logmessage("Returning a " + str(objects.instanceName))
    return objects

def recurse_obj(the_object, recursive=True):
    constructor = None
    if type(the_object) in [str, unicode, bool, int, float]:
        return the_object
    if type(the_object) is list:
        if recursive:
            return [recurse_obj(x) for x in the_object]
        else:
            return the_object
    if type(the_object) is set:
        if recursive:
            new_set = set()
            for sub_object in the_object:
                new_set.add(recurse_obj(sub_object, recursive=recursive))
            return new_list
        else:
            return the_object
    if type(the_object) is dict:
        if 'object' in the_object and ('item' in the_object or 'items' in the_object):
            if the_object['object'] in globals() and inspect.isclass(globals()[the_object['object']]):
                constructor = globals()[the_object['object']]
            elif the_object['object'] in locals() and inspect.isclass(locals()[the_object['object']]):
                constructor = locals()[the_object['object']]
            if not constructor:
                if 'module' in the_object:
                    if the_object['module'].startswith('.'):
                        module_name = docassemble.base.functions.this_thread.current_package + the_object['module']
                    else:
                        module_name = the_object['module']
                    new_module = __import__(module_name, globals(), locals(), [the_object['object']], -1)
                    constructor = getattr(new_module, the_object['object'], None)
            if not constructor:
                raise SystemError('recurse_obj: found an object for which the object declaration, ' + str(the_object['object']) + ' could not be found')
            if 'items' in the_object:
                objects = list()
                for item in the_object['items']:
                    if type(item) is not dict:
                        raise SystemError('recurse_obj: found an item, ' + str(item) + ' that was not expressed as a dictionary')
                    if recursive:
                        transformed_item = recurse_obj(item)
                    else:
                        transformed_item = item
                    #new_obj = constructor(**transformed_item)
                    #if isinstance(new_obj, DAList) or isinstance(new_obj, DADict) or isinstance(new_obj, DASet):
                    #    new_obj.gathered = True
                    objects.append(constructor(**transformed_item))
                return objects
            if 'item' in the_object:
                item = the_object['item']
                if type(item) is not dict:
                    raise SystemError('recurse_obj: found an item, ' + str(item) + ' that was not expressed as a dictionary')
                if recursive:
                    transformed_item = recurse_obj(item)
                else:
                    transformed_item = item
                #new_obj = constructor(**transformed_item)
                #if isinstance(new_obj, DAList) or isinstance(new_obj, DADict) or isinstance(new_obj, DASet):
                #    new_obj.gathered = True
                return constructor(**transformed_item)
        else:
            if recursive:
                new_dict = dict()
                for key, value in the_object.iteritems():
                    new_dict[key] = recurse_obj(value)
                return new_dict
            else:
                return the_object
    return the_object
