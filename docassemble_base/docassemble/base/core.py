from docassemble.base.logger import logmessage
from docassemble.base.generate_key import random_string
import re
import os
import codecs
#import redis
import sys
import shutil
import inspect
import yaml
import pycurl
import mimetypes
from docassemble.base.functions import possessify, possessify_long, a_preposition_b, a_in_the_b, its, their, the, this, these, underscore_to_space, nice_number, verb_past, verb_present, noun_plural, comma_and_list, ordinal, word, need, capitalize, server, nodoublequote, some, indefinite_article, force_gather, quantity_noun
import docassemble.base.functions
import docassemble.base.file_docx
from docassemble.webapp.files import SavedFile
from docxtpl import InlineImage, Subdoc
import tempfile
import time
import stat
import copy
import random

__all__ = ['DAObject', 'DAList', 'DADict', 'DASet', 'DAFile', 'DAFileCollection', 'DAFileList', 'DAStaticFile', 'DAEmail', 'DAEmailRecipient', 'DAEmailRecipientList', 'DATemplate', 'DAEmpty', 'DALink']

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

class DAEmpty(object):
    """An object that does nothing except avoid triggering errors about missing information."""
    def __getattr__(self, thename):
        if thename.startswith('_'):
            return object.__getattribute__(self, thename)
        else:
            return DAEmpty()
    def __str__(self):
        return ''
    def __unicode__(self):
        return unicode('')
    def __dir__(self):
        return list()
    def __contains__(self, item):
        return False
    def __iter__(self):
        the_list = list()
        return the_list.__iter__()
    def __len__(self):
        return 0
    def __reversed__(self):
        return list()
    def __getitem__(self, index):
        return DAEmpty()
    def __call__(self, *pargs, **kwargs):
        return DAEmpty()
    def __repr__(self):
        return repr('')
    def __add__(self, other):
        return other
    def __sub__(self, other):
        return other
    def __mul__(self, other):
        return other
    def __floordiv__(self, other):
        return other
    def __mod__(self, other):
        return other
    def __divmod__(self, other):
        return other
    def __pow__(self, other):
        return other
    def __lshift__(self, other):
        return other
    def __rshift__(self, other):
        return other
    def __and__(self, other):
        return other
    def __xor__(self, other):
        return other
    def __or__(self, other):
        return other
    def __div__(self, other):
        return other
    def __truediv__(self, other):
        return other
    def __radd__(self, other):
        return other
    def __rsub__(self, other):
        return other
    def __rmul__(self, other):
        return other
    def __rdiv__(self, other):
        return other
    def __rtruediv__(self, other):
        return other
    def __rfloordiv__(self, other):
        return other
    def __rmod__(self, other):
        return other
    def __rdivmod__(self, other):
        return other
    def __rpow__(self, other):
        return other
    def __rlshift__(self, other):
        return other
    def __rrshift__(self, other):
        return other
    def __rand__(self, other):
        return other
    def __ror__(self, other):
        return other
    def __neg__(self):
        return 0
    def __pos__(self):
        return 0
    def __abs__(self):
        return 0
    def __invert__(self):
        return 0
    def __complex__(self):
        return 0
    def __int__(self):
        return int(0)
    def __long__(self):
        return long(0)
    def __float__(self):
        return float(0)
    def __oct__(self):
        return oct(0)
    def __hex__(self):
        return hex(0)
    def __index__(self):
        return int(0)
        
class DAObjectPlusParameters(object):
    pass

class DAObject(object):
    """The base class for all docassemble objects."""
    def init(self, *pargs, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    @classmethod
    def using(cls, **kwargs):
        object_plus = DAObjectPlusParameters()
        object_plus.object_type = cls
        object_plus.parameters = kwargs
        return object_plus
    # @classmethod
    # def using(cls, **kwargs):
    #     the_kwargs = dict()
    #     for key, val in kwargs.iteritems():
    #         the_kwargs[key] = val
    #     class constructor(cls):
    #         def init(self, *pargs, **kwargs):
    #             new_args = dict()
    #             for key, val in the_kwargs.iteritems():
    #                 new_args[key] = val
    #             for key, val in kwargs.iteritems():
    #                 new_args[key] = val
    #             return super(constructor, self).init(*pargs, **new_args)
    #     return constructor
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
        self.instanceName = unicode(thename)
        self.attrList = list()
        self.init(*pargs, **kwargs)
    def _set_instance_name_for_function(self):
        try:
            self.instanceName = inspect.stack()[2][0].f_code.co_names[3]
            self.has_nonrandom_instance_name = True
        except:
            self.instanceName = get_unique_name()
            self.has_nonrandom_instance_name = False
        return self
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
        self.instanceName = re.sub(r'^' + re.escape(old_instance_name), new_instance_name, self.instanceName)
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
        self.instanceName = unicode(get_unique_name())
        self.has_nonrandom_instance_name = False
    def copy_shallow(self, thename):
        """Returns a copy of the object, giving the new object the intrinsic name 'thename'; does not change intrinsic names of sub-objects"""
        new_object = copy.copy(self)
        new_object.instanceName = thename
        return new_object
    def copy_deep(self, thename):
        """Returns a copy of the object, giving the new object the intrinsic name 'thename'; also changes the intrinsic names of sub-objects"""
        new_object = copy.deepcopy(self)
        new_object._set_instance_name_recursively(thename)
        return new_object
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
        self.revisit = True
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
    def object_name(self, **kwargs):
        """Returns the instanceName attribute, or, if the instanceName contains attributes, returns a
        phrase.  E.g., case.plaintiff becomes "plaintiff in the case." """
        the_name = reduce(a_in_the_b, map(object_name_convert, reversed(self.instanceName.split("."))))
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(the_name)
        return the_name
    def as_serializable(self):
        """Returns a serializable representation of the object."""
        return docassemble.base.functions.safe_json(self)
    def object_possessive(self, target, **kwargs):
        """Returns a possessive phrase based on the instanceName.  E.g., client.object_possessive('fish') returns
        "client's fish." """
        language = kwargs.get('language', None)
        if len(self.instanceName.split(".")) > 1:
            return(possessify_long(self.object_name(), target, language=language))
        else:
            return(possessify(the(self.object_name(), language=language), target, language=language))
    def initializeAttribute(self, *pargs, **kwargs):
        """Defines an attribute for the object, setting it to a newly initialized object.
        The first argument is the name of the attribute and the second argument is type
        of the new object that will be initialized.  E.g., 
        client.initializeAttribute('mother', Individual) initializes client.mother as an
        Individual with instanceName "client.mother"."""
        pargs = [x for x in pargs]
        name = pargs.pop(0)
        objectType = pargs.pop(0)
        new_object_parameters = dict()
        if isinstance(objectType, DAObjectPlusParameters):
            for key, val in objectType.parameters.iteritems():
                new_object_parameters[key] = val
            objectType = objectType.object_type
        for key, val in kwargs.iteritems():
            new_object_parameters[key] = val
        if name in self.__dict__:
            return
        else:
            object.__setattr__(self, name, objectType(self.instanceName + "." + name, *pargs, **new_object_parameters))
            self.attrList.append(name)
    def reInitializeAttribute(self, *pargs, **kwargs):
        """Redefines an attribute for the object, setting it to a newly initialized object.
        The first argument is the name of the attribute and the second argument is type
        of the new object that will be initialized.  E.g., 
        client.initializeAttribute('mother', Individual) initializes client.mother as an
        Individual with instanceName "client.mother"."""
        pargs = [x for x in pargs]
        name = pargs.pop(0)
        objectType = pargs.pop(0)
        new_object_parameters = dict()
        if isinstance(objectType, DAObjectPlusParameters):
            for key, val in objectType.parameters.iteritems():
                new_object_parameters[key] = val
            objectType = objectType.object_type
        for key, val in kwargs.iteritems():
            new_object_parameters[key] = val
        object.__setattr__(self, name, objectType(self.instanceName + "." + name, *pargs, **new_object_parameters))
        if name in self.__dict__:
            return
        else:
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
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        if hasattr(self, 'name'):
            return unicode(self.name)
        return unicode(self.object_name())
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
    def alternative(self, *pargs, **kwargs):
        """Returns a particular value depending on the value of a given attribute"""
        if len(pargs) == 0:
            raise Exception("alternative: attribute must be provided")
        attribute = pargs[0]
        value = self.getattr(self, attribute)
        if value in kwargs:
            return kwargs[value]
        if '_default' in kwargs:
            return kwargs['_default']
        if 'default' in kwargs:
            return kwargs['default']
        return None
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
        if 'set_instance_name' in kwargs:
            set_instance_name = kwargs['set_instance_name']
            del kwargs['set_instance_name']
        else:
            set_instance_name = False
        if 'elements' in kwargs:
            for element in kwargs['elements']:
                self.append(element)
            self.gathered = True
            self.revisit = True
            del kwargs['elements']
            if set_instance_name:
                self._set_instance_name_recursively(self.instanceName)
        if 'object_type' in kwargs:
            if isinstance(kwargs['object_type'], DAObjectPlusParameters):
                self.object_type = kwargs['object_type'].object_type
                self.object_type_parameters = kwargs['object_type'].parameters
            else:
                self.object_type = kwargs['object_type']
                self.object_type_parameters = dict()
            del kwargs['object_type']
        if not hasattr(self, 'object_type'):
            self.object_type = None
        if not hasattr(self, 'object_type_parameters'):
            self.object_type_parameters = dict()
        if 'complete_attribute' in kwargs:
            self.complete_attribute = kwargs['complete_attribute']
            del kwargs['complete_attribute']
        if not hasattr(self, 'complete_attribute'):
            self.complete_attribute = None
        if 'ask_object_type' in kwargs:
            self.ask_object_type = True
        if not hasattr(self, 'ask_object_type'):
            self.ask_object_type = False
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
        #logmessage("reset_gathered on " + self.instanceName)
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if hasattr(self, 'revisit'):
            delattr(self, 'revisit')
        if hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        if recursive:
            self._reset_gathered_recursively()
    def has_been_gathered(self):
        """Returns whether the list has been gathered"""
        if hasattr(self, 'gathered'):
            return True
        return False
    def pop(self, *pargs):
        """Remove an item the list and return it."""
        self._trigger_gather()
        result = self.elements.pop(*pargs)
        self._reset_instance_names()
        return result
    def item(self, index):
        """Returns the value for the given index, or a blank value if the index does not exist."""
        self._trigger_gather()
        if index < len(self.elements):
            return self[index]
        return DAEmpty()
    def __add__(self, other):
        self._trigger_gather()
        if isinstance(other, DAList):
            other._trigger_gather()
            the_list = DAList(elements=self.elements + other.elements, gathered=True, auto_gather=False)
            the_list.set_random_instance_name()
            return the_list
        return self.elements + other
    def index(self, *pargs, **kwargs):
        """Returns the first index at which a given item may be found."""
        self._trigger_gather()
        return self.elements.index(*pargs, **kwargs)
    def clear(self):
        """Removes all the items from the list."""
        self.elements = list()
    # def populated(self):
    #     """Ensures that existing elements have been populated."""
    #     if self.object_type is not None:
    #         item_object_type = self.object_type
    #     else:
    #         item_object_type = None
    #     if self.complete_attribute is not None:
    #         complete_attribute = self.complete_attribute
    #     else:
    #         complete_attribute = None
    #     for elem in self.elements:
    #         str(elem)
    #         if item_object_type is not None and complete_attribute is not None:
    #             getattr(elem, complete_attribute)
    #     return True
    def fix_instance_name(self, old_instance_name, new_instance_name):
        """Substitutes a different instance name for the object and its subobjects."""
        for item in self.elements:
            if isinstance(item, DAObject):
                item.fix_instance_name(old_instance_name, new_instance_name)
        return super(DAList, self).fix_instance_name(old_instance_name, new_instance_name)
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
    def _reset_instance_names(self):
        indexno = 0
        for item in self.elements:
            if isinstance(item, DAObject) and item.instanceName.startswith(self.instanceName + '['):
                item._set_instance_name_recursively(self.instanceName + '[' + str(indexno) + ']')
            indexno += 1
    def appendObject(self, *pargs, **kwargs):
        """Creates a new object and adds it to the list.
        Takes an optional argument, which is the type of object
        the new object should be.  If no object type is provided,
        the object type given by .object_type is used, and if 
        that is not set, DAObject is used."""
        #sys.stderr.write("Called appendObject where len is " + str(len(self.elements)) + "\n")
        objectFunction = None
        if len(pargs) > 0:
            pargs = [x for x in pargs]
            objectFunction = pargs.pop(0)
        new_obj_parameters = dict()
        if objectFunction is None:
            if self.object_type is not None:
                objectFunction = self.object_type
                for key, val in self.object_type_parameters.iteritems():
                    new_obj_parameters[key] = val
            else:
                objectFunction = DAObject
        for key, val in kwargs.iteritems():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + str(len(self.elements)) + ']', *pargs, **new_obj_parameters)
        self.elements.append(newobject)
        if hasattr(self, 'there_are_any'):
            self.there_are_any = True
        return newobject
    def append(self, *pargs, **kwargs):
        """Adds the arguments to the end of the list."""
        something_added = False
        set_instance_name = kwargs.get('set_instance_name', False)
        for parg in pargs:
            if isinstance(parg, DAObject) and (set_instance_name or (not parg.has_nonrandom_instance_name)):
                parg.fix_instance_name(parg.instanceName, self.instanceName + '[' + str(len(self.elements)) + ']')
            self.elements.append(parg)
            something_added = True
        if something_added and len(self.elements) > 0 and hasattr(self, 'there_are_any'):
            self.there_are_any = True
    def remove(self, *pargs):
        """Removes the given arguments from the list, if they are in the list"""
        something_removed = False
        for value in pargs:
            if value in self.elements:
                self.elements.remove(value)
                something_removed = True
        self._reset_instance_names()
        if something_removed and len(self.elements) == 0 and hasattr(self, 'there_are_any'):
            self.there_are_any = False
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
        language = kwargs.get('language', None)
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
        else:
            if self.number() > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense, language=language)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        language = kwargs.get('language', None)
        if self.number() > 1:
            tense = 'ppl'
        else:
            tense = '3sgp'
        return verb_past(the_verb, tense, language=language)
    def as_singular_noun(self):
        """Returns a human-readable expression of the object based on its instanceName,
        without making it plural.  E.g., case.plaintiff.child.as_singular_noun() 
        returns "child" even if there are multiple children."""
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun
    def possessive(self, target, **kwargs):
        """If the variable name is "plaintiff" and the target is "fish,"
        returns "plaintiff's fish" if there is one item in the list,
        and "plaintiffs' fish" if there is more than one item in the
        list.

        """
        language = kwargs.get('language', None)
        return possessify(self.as_noun(**kwargs), target, plural=(self.number() > 1), language=language)
    def quantity_noun(self, *pargs, **kwargs):
        the_args = [self.number()] + list(pargs)
        return quantity_noun(*the_args, **kwargs)
    def as_noun(self, *pargs, **kwargs):
        """Returns a human-readable expression of the object based on its instanceName,
        using singular or plural depending on whether the list has one element or more
        than one element.  E.g., case.plaintiff.child.as_noun() returns "child" or
        "children," as appropriate.  If an argument is supplied, the argument is used
        instead of the instanceName."""
        language = kwargs.get('language', None)
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        the_noun = re.sub(r'_', ' ', the_noun)
        if len(pargs) > 0:
            the_noun = pargs[0]
        if (self.number() > 1 or self.number() == 0 or ('plural' in kwargs and kwargs['plural'])) and not ('singular' in kwargs and kwargs['singular']):
            output = noun_plural(the_noun, language=language)
            if 'article' in kwargs and kwargs['article']:
                if 'some' in kwargs and kwargs['some']:
                    output = some(output, language=language)
            elif 'this' in kwargs and kwargs['this']:
                output = these(output, language=language)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
        else:
            output = the_noun
            if 'article' in kwargs and kwargs['article']:
                output = indefinite_article(output, language=language)
            elif 'this' in kwargs and kwargs['this']:
                output = this(output, language=language)
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
    def number_gathered(self):
        """Returns the number of elements in the list that have been gathered so far."""
        return len(self.elements)
    def current_index(self):
        """Returns the index number of the last element added to the list, or 0 if no elements have been added."""
        if len(self.elements) == 0:
            return 0
        return len(self.elements) - 1
    def number_as_word(self, language=None):
        """Returns the number of elements in the list, spelling out the number if ten 
        or below.  Forces the gathering of the elements if necessary."""
        return nice_number(self.number(), language=language)
    def complete_elements(self, complete_attribute=None):
        """Returns a list of the elements that are complete."""
        if complete_attribute is None and hasattr(self, 'complete_attribute'):
            complete_attribute = self.complete_attribute
        items = list()
        for item in self.elements:
            if item is None:
                continue
            if complete_attribute is not None:
                if not hasattr(item, complete_attribute):
                    continue
            else:
                try:
                    unicode(item)
                except:
                    continue
            items.append(item)
        return items
    def _validate(self, item_object_type, complete_attribute):
        if self.ask_object_type:
            for indexno in range(len(self.elements)):
                if self.elements[indexno] is None:
                    if isinstance(self.new_object_type, DAObjectPlusParameters):
                        object_type_to_use = self.new_object_type.object_type
                        parameters_to_use = self.new_object_type.parameters
                    if type(self.new_object_type) is type:
                        object_type_to_use = self.new_object_type
                        parameters_to_use = dict()
                    else:
                        raise Exception("new_object_type must be an object type")
                    self.elements[indexno] = object_type_to_use(self.instanceName + '[' + str(indexno) + ']', **parameters_to_use)
                if complete_attribute is not None:
                    getattr(self.elements[indexno], complete_attribute)
                else:
                    unicode(self.elements[indexno])
            if hasattr(self, 'new_object_type'):
                delattr(self, 'new_object_type')
        for elem in self.elements:
            if item_object_type is not None and complete_attribute is not None:
                getattr(elem, complete_attribute)
            else:
                unicode(elem)
    def gather(self, number=None, item_object_type=None, minimum=None, complete_attribute=None):
        """Causes the elements of the list to be gathered and named.  Returns True."""
        #sys.stderr.write("Gather\n")
        if hasattr(self, 'gathered') and self.gathered:
            return True
        if item_object_type is None and self.object_type is not None:
            item_object_type = self.object_type
            item_object_parameters = self.object_type_parameters
        elif isinstance(item_object_type, DAObjectPlusParameters):
            item_object_parameters = item_object_type.parameters
            item_object_type = item_object_type.object_type
        else:
            item_object_parameters = dict()
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
        self._validate(item_object_type, complete_attribute)
        while len(self.elements) < minimum:
            the_length = len(self.elements)
            if item_object_type is not None:
                self.appendObject(item_object_type, **item_object_parameters)
            self.__getitem__(the_length)
            self._validate(item_object_type, complete_attribute)
            #str(self.__getitem__(the_length))
            # if item_object_type is not None and complete_attribute is not None:
            #     getattr(self.__getitem__(the_length), complete_attribute)
        # for elem in self.elements:
        #     str(elem)
        #     if item_object_type is not None and complete_attribute is not None:
        #         getattr(elem, complete_attribute)
        the_length = len(self.elements)
        if hasattr(self, '_necessary_length'):
            if self._necessary_length <= the_length:
                del self._necessary_length
            elif number is None or number < self._necessary_length:
                number = self._necessary_length
        if number is not None:
            while the_length < int(number):
                if item_object_type is not None:
                    self.appendObject(item_object_type, **item_object_parameters)
                self.__getitem__(the_length)
                self._validate(item_object_type, complete_attribute)
                #str(self.__getitem__(the_length))
                # if item_object_type is not None and complete_attribute is not None:
                #     getattr(self.__getitem__(the_length), complete_attribute)
            if hasattr(self, '_necessary_length'):
                del self._necessary_length
        elif minimum != 0:
            while self.there_is_another:
                #logmessage("gather " + self.instanceName + ": del on there_is_another")
                del self.there_is_another
                self._necessary_length = the_length + 1
                if item_object_type is not None:
                    self.appendObject(item_object_type, **item_object_parameters)
                self.__getitem__(the_length)
                self._validate(item_object_type, complete_attribute)
                #str(self.__getitem__(the_length))
                # if item_object_type is not None and complete_attribute is not None:
                #     getattr(self.__getitem__(the_length), complete_attribute)
        if hasattr(self, '_necessary_length'):
            del self._necessary_length
        if self.auto_gather:
            self.gathered = True
            self.revisit = True
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
        self[index]
        self.elements.__delitem__(index)
        self._reset_instance_names()
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
                    self.appendObject(self.object_type, **self.object_type_parameters)
        elif len(self.elements) <= index:
            num_to_add = 1 + index - len(self.elements)
            for i in range(0, num_to_add):
                if self.object_type is None:
                    self.elements.append(None)
                else:
                    self.appendObject(self.object_type, **self.object_type_parameters)
    def __setitem__(self, index, value):
        self._fill_up_to(index)
        if isinstance(value, DAObject) and not value.has_nonrandom_instance_name:
            value.has_nonrandom_instance_name = True
            value.instanceName = self.instanceName + '[' + str(index) + ']'
            #value._set_instance_name_recursively(self.instanceName + '[' + str(index) + ']')
        return self.elements.__setitem__(index, value)
    def __getitem__(self, index):
        try:
            return self.elements[index]
        except:
            if self.auto_gather and hasattr(self, 'gathered'):
                try:
                    logmessage("list index out of range on " + unicode(self.instanceName))
                except:
                    pass
                raise IndexError("list index out of range")
            elif self.object_type is None and not self.ask_object_type:
                var_name = object.__getattribute__(self, 'instanceName') + '[' + str(index) + ']'
                #force_gather(var_name)
                raise NameError("name '" + var_name + "' is not defined")
            else:
                #sys.stderr.write("Calling fill up to\n")
                self._fill_up_to(index)
            #sys.stderr.write("Assuming it is there!\n")
            return self.elements[index]
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        self._trigger_gather()
        return unicode(self.comma_and_list())
    def __repr__(self):
        self._trigger_gather()
        return repr(self.elements)
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
    def item_actions(self, *pargs):
        """Returns HTML for editing the items in a list"""
        the_args = list(pargs)
        item = the_args.pop(0)
        return '<a href="' + docassemble.base.functions.url_action('_da_list_edit', items=[item.instanceName + '.' + y for y in the_args]) + '" class="btn btn-sm btn-secondary btn-revisit"><i class="fas fa-pencil-alt"></i> ' + word('Edit') + '</a> <a href="' + docassemble.base.functions.url_action('_da_list_remove', list=self.instanceName, item=item.instanceName) + '" class="btn btn-sm btn-danger btn-revisit"><i class="fas fa-trash"></i> ' + word('Delete') + '</a>'
    def add_action(self, message=None):
        """Returns HTML for adding an item to a list"""
        if message is None:
            message = word("Add another")
        return '<a href="' + docassemble.base.functions.url_action('_da_list_add', list=self.instanceName) + '" class="btn btn-sm btn-success"><i class="fas fa-plus-circle"></i> ' + unicode(message) + '</a>'

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
            self.revisit = True
            del kwargs['elements']
        if 'object_type' in kwargs:
            if isinstance(kwargs['object_type'], DAObjectPlusParameters):
                self.object_type = kwargs['object_type'].object_type
                self.object_type_parameters = kwargs['object_type'].parameters
            else:
                self.object_type = kwargs['object_type']
                self.object_type_parameters = dict()
            del kwargs['object_type']
        if not hasattr(self, 'object_type'):
            self.object_type = None
        if not hasattr(self, 'object_type_parameters'):
            self.object_type_parameters = dict()
        if 'complete_attribute' in kwargs:
            self.complete_attribute = kwargs['complete_attribute']
            del kwargs['complete_attribute']
        if not hasattr(self, 'complete_attribute'):
            self.complete_attribute = None
        if 'ask_object_type' in kwargs:
            self.ask_object_type = True
        if not hasattr(self, 'ask_object_type'):
            self.ask_object_type = False
        if 'keys' in kwargs and hasattr(kwargs['keys'], '__iter__'):
            self.new(kwargs['keys'])
        return super(DADict, self).init(*pargs, **kwargs)
    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered
        return
    def fix_instance_name(self, old_instance_name, new_instance_name):
        """Substitutes a different instance name for the object and its subobjects."""
        for key, value in self.elements.iteritems():
            if isinstance(value, DAObject):
                value.fix_instance_name(old_instance_name, new_instance_name)
        return super(DADict, self).fix_instance_name(old_instance_name, new_instance_name)
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
    def all_false(self, *pargs, **kwargs):
        """Returns True if the values of all keys are False.  If one or more
        keys are provided as arguments, returns True if all of the
        values of those keys are False.  If the optional keyword
        argument 'exclusive' is True, returns True only if those keys
        are the only false values.

        """
        the_list = list()
        exclusive = kwargs.get('exclusive', False)
        for parg in pargs:
            if hasattr(parg, '__iter__'):
                the_list.extend([x for x in parg])
            else:
                the_list.append(parg)
        if len(the_list) == 0:
            for key, value in sorted(self.elements.iteritems()):
                if value is not False:
                    return False
            self._trigger_gather()
            return True
        for key in the_list:
            if key not in self.elements:
                return False
        for key, value in sorted(self.elements.iteritems()):
            if key in the_list:
                if value is not False:
                    return False
            else:
                if exclusive and value is False:
                    return False
        self._trigger_gather()
        return True
    def any_true(self, *pargs, **kwargs):
        """Returns the opposite of all_false()."""
        return not self.all_false(*pargs, **kwargs)
    def any_false(self, *pargs, **kwargs):
        """Returns the opposite of all_true()."""
        return not self.all_true(*pargs, **kwargs)
    def all_true(self, *pargs, **kwargs):
        """Returns True if the values of all keys are True.  If one or more
        keys are provided as arguments, returns True if all of the
        values of those keys are True.  If the optional keyword
        argument 'exclusive' is True, returns True only if those keys
        are the only true values.

        """
        the_list = list()
        exclusive = kwargs.get('exclusive', False)
        for parg in pargs:
            if hasattr(parg, '__iter__'):
                the_list.extend([x for x in parg])
            else:
                the_list.append(parg)
        if len(the_list) == 0:
            for key, value in sorted(self.elements.iteritems()):
                if value is not True:
                    return False
            self._trigger_gather()
            return True
        for key in the_list:
            if key not in self.elements:
                return False
        for key, value in sorted(self.elements.iteritems()):
            if key in the_list:
                if value is not True:
                    return False
            else:
                if exclusive and value is True:
                    return False
        self._trigger_gather()
        return True
    def true_values(self):
        """Returns the keys for which the corresponding value is True."""
        return DAList(elements=[key for key, value in sorted(self.iteritems()) if value is True])
    def false_values(self):
        """Returns the keys for which the corresponding value is False."""
        return DAList(elements=[key for key, value in sorted(self.iteritems()) if value is False])
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
        new_obj_parameters = dict()
        if isinstance(objectFunction, DAObjectPlusParameters):
            for key, val in objectFunction.parameters.iteritems():
                new_obj_parameters[key] = val
            objectFunction = objectFunction.object_type
        if objectFunction is None:
            if self.object_type is not None:
                objectFunction = self.object_type
                for key, val in self.object_type_parameters.iteritems():
                    new_obj_parameters[key] = val
            else:
                objectFunction = DAObject
                object_type_parameters = dict()
        for key, val in kwargs.iteritems():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + repr(entry) + ']', *pargs, **new_obj_parameters)
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
                new_obj_parameters = dict()
                if self.object_type is not None:
                    item_object_type = self.object_type
                    for key, val in self.object_type_parameters.iteritems():
                        new_obj_parameters[key] = val
                else:
                    item_object_type = DAObject
                for key, val in kwargs.iteritems():
                    new_obj_parameters[key] = val
                if parg not in self.elements:
                    self.initializeObject(parg, item_object_type, **new_obj_parameters)
    def reset_gathered(self, recursive=False):
        """Indicates that there is more to be gathered"""
        #logmessage("reset_gathered on " + self.instanceName)
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if hasattr(self, 'revisit'):
            delattr(self, 'revisit')
        if hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        if recursive:
            self._reset_gathered_recursively()
    def has_been_gathered(self):
        """Returns whether the dictionary has been gathered"""
        if hasattr(self, 'gathered'):
            return True
        return False
    def does_verb(self, the_verb, **kwargs):
        """Returns the appropriate conjugation of the given verb depending on
        whether there is only one key in the dictionary or multiple
        keys.  E.g., player.does_verb('finish') will return "finishes" if there
        is one player and "finish" if there is more than one
        player."""
        language = kwargs.get('language', None)
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
        else:
            if self.number() > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense, language=language)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        language = kwargs.get('language', None)
        if self.number() > 1:
            tense = 'ppl'
        else:
            tense = '3sgp'
        return verb_past(the_verb, tense, language=language)
    def as_singular_noun(self):
        """Returns a human-readable expression of the object based on its
        instanceName, without making it plural.  E.g.,
        player.as_singular_noun() returns "player" even if there are
        multiple players."""
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun        
    def quantity_noun(self, *pargs, **kwargs):
        the_args = [self.number()] + list(pargs)
        return quantity_noun(*the_args, **kwargs)
    def as_noun(self, *pargs, **kwargs):
        """Returns a human-readable expression of the object based on its
        instanceName, using singular or plural depending on whether
        the dictionary has one key or more than one key.  E.g.,
        player.as_noun() returns "player" or "players," as
        appropriate.  If an argument is supplied, the argument is used
        as the noun instead of the instanceName."""
        language = kwargs.get('language', None)        
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        the_noun = re.sub(r'_', ' ', the_noun)
        if len(pargs) > 0:
            the_noun = pargs[0]
        if (self.number() > 1 or self.number() == 0 or ('plural' in kwargs and kwargs['plural'])) and not ('singular' in kwargs and kwargs['singular']):
            output = noun_plural(the_noun, language=language)
            if 'article' in kwargs and kwargs['article']:
                if 'some' in kwargs and kwargs['some']:
                    output = some(output, language=language)
            elif 'this' in kwargs and kwargs['this']:
                output = these(output, language=language)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
        else:
            output = the_noun
            if 'article' in kwargs and kwargs['article']:
                output = indefinite_article(output, language=language)
            elif 'this' in kwargs and kwargs['this']:
                output = this(output, language=language)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
    def possessive(self, target, **kwargs):
        """If the variable name is "plaintiff" and the target is "fish,"
        returns "plaintiff's fish" if there is one item in the dictionary,
        and "plaintiffs' fish" if there is more than one item in the
        list.

        """
        language = kwargs.get('language', None)
        return possessify(self.as_noun(**kwargs), target, plural=(self.number() > 1), language=language)
    def number(self):
        """Returns the number of keys in the dictionary.  Forces the gathering of the
        dictionary items if necessary."""
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return len(self.elements)
    def number_gathered(self):
        """Returns the number of elements in the list that have been gathered so far."""
        return len(self.elements)
    def number_as_word(self, language=None):
        """Returns the number of keys in the dictionary, spelling out the number if ten 
        or below.  Forces the gathering of the dictionary items if necessary."""
        return nice_number(self.number(), language=language)
    def complete_elements(self, complete_attribute=None):
        """Returns a dictionary containing the key/value pairs that are complete."""
        if complete_attribute is None and hasattr(self, 'complete_attribute'):
            complete_attribute = self.complete_attribute
        items = list()
        for key, val in self.elements.iteritems():
            if val is None:
                continue
            if complete_attribute is not None:
                if not hasattr(val, complete_attribute):
                    continue
            else:
                try:
                    unicode(val)
                except:
                    continue
            items[key] = val
        return items
    def _validate(self, item_object_type, complete_attribute, keys=None):
        if keys is None:
            keys = sorted(self.elements.keys())
        else:
            keys = [key for key in keys if key in self.elements]
        if self.ask_object_type:
            for key in keys:
                elem = self.elements[key]
                if elem is None:
                    if isinstance(self.new_object_type, DAObjectPlusParameters):
                        object_type_to_use = self.new_object_type.object_type
                        parameters_to_use = self.new_object_type.parameters
                    elif type(self.new_object_type) is type:
                        object_type_to_use = self.new_object_type
                        parameters_to_use = dict()
                    else:
                        raise Exception("new_object_type must be an object type")
                    self.elements[key] = object_type_to_use(self.instanceName + '[' + repr(key) + ']', **parameters_to_use)
            if hasattr(self, 'new_object_type'):
                delattr(self, 'new_object_type')
        for key in keys:
            elem = self.elements[key]
            if item_object_type is not None and complete_attribute is not None:
                getattr(elem, complete_attribute)
            else:
                unicode(elem)
    def gather(self, item_object_type=None, number=None, minimum=None, complete_attribute=None, keys=None):
        """Causes the dictionary items to be gathered and named.  Returns True."""
        if hasattr(self, 'gathered') and self.gathered:
            return True
        if item_object_type is None and self.object_type is not None:
            item_object_type = self.object_type
            new_item_parameters = self.object_type_parameters
        elif isinstance(item_object_type, DAObjectPlusParameters):
            new_item_parameters = item_object_type.parameters
            item_object_type = item_object_type.object_type
        else:
            new_item_parameters = dict()
        if complete_attribute is None and self.complete_attribute is not None:
            complete_attribute = self.complete_attribute
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        self._validate(item_object_type, complete_attribute, keys=keys)
        # for elem in sorted(self.elements.values()):
        #     str(elem)
        #     if item_object_type is not None and complete_attribute is not None:
        #         getattr(elem, complete_attribute)
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
        if item_object_type is None and hasattr(self, 'new_item_name') and self.new_item_name in self.elements:
            delattr(self, 'new_item_name')
            if hasattr(self, 'there_is_another'):
                #logmessage("0gather " + self.instanceName + ": del on there_is_another")
                delattr(self, 'there_is_another')
        while (number is not None and len(self.elements) < int(number)) or (minimum is not None and len(self.elements) < int(minimum)) or (self.ask_number is False and minimum != 0 and self.there_is_another):
            if item_object_type is not None:
                self.initializeObject(self.new_item_name, item_object_type, **new_item_parameters)
                if hasattr(self, 'there_is_another'):
                    #logmessage("1gather " + self.instanceName + ": del on there_is_another")
                    delattr(self, 'there_is_another')
                self._new_item_init_callback()
                if hasattr(self, 'new_item_name'):
                    delattr(self, 'new_item_name')
            else:
                self.new_item_name
                if hasattr(self, 'new_item_value'):
                    self.elements[self.new_item_name] = self.new_item_value
                    delattr(self, 'new_item_value')
                    delattr(self, 'new_item_name')
                    if hasattr(self, 'there_is_another'):
                        #logmessage("2gather " + self.instanceName + ": del on there_is_another")
                        delattr(self, 'there_is_another')
                else:
                    the_name = self.new_item_name
                    self.__getitem__(the_name)
                    if hasattr(self, 'new_item_name'):
                        delattr(self, 'new_item_name')
                    if hasattr(self, 'there_is_another'):
                        #logmessage("3gather " + self.instanceName + ": del on there_is_another")
                        delattr(self, 'there_is_another')
            if hasattr(self, 'there_is_another'):
                #logmessage("4gather " + self.instanceName + ": del on there_is_another")
                delattr(self, 'there_is_another')
        self._validate(item_object_type, complete_attribute, keys=keys)
        if self.auto_gather:
            self.gathered = True
            self.revisit = True
        docassemble.base.functions.set_gathering_mode(False, self.instanceName)
        return True
    def _new_item_init_callback(self):
        if hasattr(self, 'new_item_name'):
            delattr(self, 'new_item_name')
        if hasattr(self, 'new_item_value'):
            delattr(self, 'new_item_value')
        for elem in sorted(self.elements.values()):
            if self.object_type is not None and self.complete_attribute is not None:
                getattr(elem, self.complete_attribute)
            else:
                unicode(elem)
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
                self.initializeObject(index, self.object_type, **self.object_type_parameters)
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
        return sorted(self.elements.keys())
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
    def item(self, key):
        """Returns the value for the given key, or a blank value if the key does not exist."""
        self._trigger_gather()
        if key in self.elements:
            return self[key]
        return DAEmpty()
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
        self[key]
        return self.elements.__delitem__(key)
    def __missing__(self, key):
        return self.elements.__missing__(key)
    def __hash__(self, the_object):
        self._trigger_gather()
        return self.elements.__hash__(the_object)
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return unicode(self.comma_and_list())
    def __repr__(self):
        self._trigger_gather()
        return repr(self.elements)
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
            self.revisit = True
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
        #logmessage("reset_gathered: " + self.instanceName + ": del on there_is_another")
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        if recursive:
            self._reset_gathered_recursively()
    def has_been_gathered(self):
        """Returns whether the set has been gathered"""
        if hasattr(self, 'gathered'):
            return True
        return False
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
        language = kwargs.get('language', None)
        if ('past' in kwargs and kwargs['past'] == True) or ('present' in kwargs and kwargs['present'] == False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
        else:
            if self.number() > 1:
                tense = 'pl'
            else:
                tense = '3sg'
            return verb_present(the_verb, tense, language=language)
    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except it returns the past tense of the verb."""        
        language = kwargs.get('language', None)
        if self.number() > 1:
            tense = 'ppl'
        else:
            tense = '3sgp'
        return verb_past(the_verb, tense, language=language)
    def as_singular_noun(self):
        """Returns a human-readable expression of the object based on its
        instanceName, without making it plural.  E.g.,
        player.as_singular_noun() returns "player" even if there are
        multiple players.

        """
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        return the_noun        
    def quantity_noun(self, *pargs, **kwargs):
        the_args = [self.number()] + list(pargs)
        return quantity_noun(*the_args, **kwargs)
    def as_noun(self, *pargs, **kwargs):
        """Returns a human-readable expression of the object based on its
        instanceName, using singular or plural depending on whether
        the set has one item in it or multiple items.  E.g.,
        player.as_noun() returns "player" or "players," as
        appropriate.  If an argument is supplied, the argument is used
        instead of the instanceName.

        """
        language = kwargs.get('language', None)
        the_noun = self.instanceName
        the_noun = re.sub(r'.*\.', '', the_noun)
        the_noun = re.sub(r'_', ' ', the_noun)
        if len(pargs) > 0:
            the_noun = pargs[0]
        if (self.number() > 1 or self.number() == 0 or ('plural' in kwargs and kwargs['plural'])) and not ('singular' in kwargs and kwargs['singular']):
            output = noun_plural(the_noun, language=language)
            if 'article' in kwargs and kwargs['article']:
                if 'some' in kwargs and kwargs['some']:
                    output = some(output, language=language)
            elif 'this' in kwargs and kwargs['this']:
                output = these(output, language=language)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output)
            else:
                return output
        else:
            output = the_noun
            if 'article' in kwargs and kwargs['article']:
                output = indefinite_article(output, language=language)
            elif 'this' in kwargs and kwargs['this']:
                output = this(output, language=language)
            if 'capitalize' in kwargs and kwargs['capitalize']:
                return capitalize(output, language=language)
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
    def number_gathered(self):
        """Returns the number of elements in the list that have been gathered so far."""
        return len(self.elements)
    def number_as_word(self, language=None):
        """Returns the number of items in the set, spelling out the number if
        ten or below.  Forces the gathering of the items if necessary.

        """
        return nice_number(self.number(), language=language)
    def gather(self, number=None, minimum=None):
        """Causes the items in the set to be gathered.  Returns True.

        """
        if hasattr(self, 'gathered') and self.gathered:
            return True
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        for elem in sorted(self.elements):
            unicode(elem)
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
            for elem in sorted(self.elements):
                unicode(elem)
            if hasattr(self, 'there_is_another'):
                #logmessage("gather: " + self.instanceName + ": del on there_is_another")
                del self.there_is_another
        if self.auto_gather:
            self.gathered = True
            self.revisit = True
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
    def __add__(self, other):
        if isinstance(other, DASet):
            return self.elements + other.elements
        return self.elements + other
    def __sub__(self, other):
        if isinstance(other, DASet):
            return self.elements - other.elements
        return self.elements - other
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        self._trigger_gather()
        return unicode(self.comma_and_list())
    def __repr__(self):
        self._trigger_gather()
        return repr(self.elements)
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
        if 'filename' in kwargs:
            self.filename = kwargs['filename']
            self.has_specific_filename = True
        else:
            self.has_specific_filename = False
        if 'mimetype' in kwargs:
            self.mimetype = kwargs['mimetype']
        if 'extension' in kwargs:
            self.extension = kwargs['extension']
        if 'content' in kwargs:
            self.content = kwargs['content']
        if 'markdown' in kwargs:
            self.markdown = kwargs['markdown']
        if 'number' in kwargs:
            self.number = kwargs['number']
            self.ok = True
        else:
            self.ok = False
        if hasattr(self, 'extension') and self.extension == 'pdf':
            if 'make_thumbnail' in kwargs and kwargs['make_thumbnail']:
                self._make_pdf_thumbnail(kwargs['make_thumbnail'])
            if 'make_pngs' in kwargs and kwargs['make_pngs']:
                self._make_pngs_for_pdf()
        return
    def set_mimetype(self, mimetype):
        """Sets the MIME type of the file"""
        self.mimetype = mimetype
        if mimetype == 'image/jpeg':
            self.extension = 'jpg'
        else:
            self.extension = re.sub(r'^\.', '', mimetypes.guess_extension(mimetype))
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return unicode(self.show())
    def initialize(self, **kwargs):
        """Creates the file on the system if it does not already exist, and ensures that the file is ready to be used."""
        #logmessage("initialize")
        if 'filename' in kwargs and kwargs['filename']:
            self.filename = kwargs['filename']
            self.has_specific_filename = True
        if 'mimetype' in kwargs:
            self.mimetype = kwargs['mimetype']
        if 'extension' in kwargs:
            self.extension = kwargs['extension']
        if 'content' in kwargs:
            self.content = kwargs['content']
        if 'markdown' in kwargs:
            self.markdown = kwargs['markdown']
        if 'number' in kwargs and kwargs['number'] is not None:
            self.number = kwargs['number']
            self.ok = True
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
            sf = SavedFile(self.number, extension=self.extension, fix=True)
            sf.save()
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
        self.extension = self.file_info.get('extension', None)
        self.mimetype = self.file_info.get('mimetype', None)
        self.persistent = self.file_info['persistent']
        self.private = self.file_info['private']
    def slurp(self, auto_decode=True):
        """Returns the contents of the file."""
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File " + str(the_path) + " does not exist yet.")
        with open(the_path, 'rU') as f:
            if auto_decode and hasattr(self, 'mimetype') and (self.mimetype.startswith('text') or self.mimetype in ('application/json', 'application/javascript')):
                return(f.read().decode('utf8'))
            else:
                return(f.read())
    def readlines(self):
        """Returns the contents of the file."""
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File does not exist yet.")
        with open(the_path, 'rU') as f:
            return(f.readlines())
    def write(self, content):
        """Writes the given content to the file, replacing existing contents."""
        self.retrieve()
        the_path = self.file_info['path']
        with open(the_path, 'w') as f:
            f.write(content)
    def copy_into(self, filename):
        """Makes the contents of the file the same as those of the given filename."""
        self.retrieve()
        shutil.copyfile(filename, self.file_info['path'])
    def from_url(self, url):
        """Makes the contents of the file the contents of the given URL."""
        self.retrieve()
        cookiefile = tempfile.NamedTemporaryFile(suffix='.txt')
        the_path = self.file_info['path']
        f = open(the_path, 'wb')
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.WRITEDATA, f)
        c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36')
        c.setopt(pycurl.COOKIEFILE, cookiefile.name)
        c.perform()
        c.close()
    def _make_pdf_thumbnail(self, page):
        """Creates a page image for the first page of a PDF file."""
        if not hasattr(self, 'file_info'):
            self.retrieve()
        max_pages = 1 + int(self.file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        the_path = self.file_info['path'] + 'screen-' + (formatter % int(page)) + '.png'
        if not os.path.isfile(the_path):
            server.fg_make_png_for_pdf(self, 'screen', page=page)
    def pngs_ready(self):
        """Creates page images for a PDF file."""
        self._make_pngs_for_pdf()
        if server.task_ready(self._taskscreen) and server.task_ready(self._taskpage):
            return True
        return False
    def _make_pngs_for_pdf(self):
        if not hasattr(self, '_taskscreen'):
            setattr(self, '_taskscreen', server.make_png_for_pdf(self, 'screen'))
        if not hasattr(self, '_taskpage'):
            setattr(self, '_taskpage', server.make_png_for_pdf(self, 'page'))
    def num_pages(self):
        """Returns the number of pages in the file, if a PDF file, and 1 otherwise"""
        if not hasattr(self, 'number'):
            raise Exception("Cannot get pages in file without a file number.")
        if not hasattr(self, 'file_info'):
            self.retrieve()
        if hasattr(self, 'mimetype'):
            if self.mimetype != 'application/pdf':
                return 1
            if 'pages' not in self.file_info:
                return 1
            return self.file_info['pages']
        else:
            return 1
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
        #logmessage("Test path is " + test_path)
        if wait and os.path.isfile(test_path):
            #logmessage("Test path exists")
            while (os.path.isfile(test_path) and time.time() - os.stat(test_path)[stat.ST_MTIME]) < 30:
                logmessage("Waiting for test path to go away")
                if not os.path.isfile(test_path):
                    break
                time.sleep(1)
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
    def cloud_path(self, filename=None):
        """Returns the path with which the file can be accessed using S3 or Azure Blob Storage, or None if cloud storage is not enabled."""
        if not hasattr(self, 'number'):
            raise Exception("Cannot get the cloud path of file without a file number.")
        return SavedFile(self.number, fix=False).cloud_path(filename)
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
        if hasattr(self, 'number'):
            #logmessage("Committed " + str(self.number))
            sf = SavedFile(self.number, fix=True)
            sf.finalize()
    def show(self, width=None, wait=True):
        """Inserts markup that displays the file as an image.  Takes an
        optional keyword argument width.

        """
        if not self.ok:
            return(u'')
        if hasattr(self, 'number') and hasattr(self, 'extension') and self.extension == 'pdf' and wait:
            self.page_path(1, 'page')
        if self.mimetype == 'text/markdown':
            the_template = DATemplate(content=self.slurp())
            return unicode(the_template)
        elif self.mimetype == 'text/plain':
            the_content = self.slurp()
            return the_content
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self)
            else:
                return docassemble.base.file_docx.image_for_docx(self.number, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.docx_template, width=width)
        else:
            if width is not None:
                return(u'[FILE ' + unicode(self.number) + u', ' + unicode(width) + u']')
            else:
                return(u'[FILE ' + unicode(self.number) + u']')
    def url_for(self, **kwargs):
        """Returns a URL to the file."""
        return server.url_finder(self, **kwargs)
    def set_attributes(self, **kwargs):
        """Sets attributes of the file stored on the server.  Takes optional keyword arguments private and persistent, which must be boolean values."""
        if 'private' in kwargs and kwargs['private'] in [True, False]:
            self.private = kwargs['private']
        if 'persistent' in kwargs and kwargs['persistent'] in [True, False]:
            self.persistent = kwargs['persistent']
        return server.file_set_attributes(self.number, **kwargs)

class DAFileCollection(DAObject):
    """Used internally by docassemble to refer to a collection of DAFile
    objects, usually representing the same document in different
    formats.  Attributes represent file types.  The attachments
    feature generates objects of this type.

    """
    def init(self, *pargs, **kwargs):
        self.info = dict()
    def _extension_list(self):
        if hasattr(self, 'info') and 'formats' in self.info:
            return self.info['formats']
        return ['pdf', 'docx', 'rtf']
    def num_pages(self):
        """If there is a PDF file, returns the number of pages in the file, otherwise returns 1."""
        if hasattr(self, 'pdf'):
            return self.pdf.num_pages()
        return result        
    def _first_file(self):
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext)
        return None
    def path(self):
        """Returns a path and filename at which one of the attachments in the
        collection can be accessed.

        """
        the_file = self._first_file()
        if the_file is None:
            return None
        return the_file.path()
    def url_for(self, **kwargs):
        """Returns a URL to one of the attachments in the collection."""
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext).url_for(**kwargs)
        raise Exception("Could not find a file within a DACollection.")
    def set_attributes(self, **kwargs):
        """Sets attributes of the file(s) stored on the server.  Takes optional keyword arguments private and persistent, which must be boolean values."""
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext).set_attributes(**kwargs)
    def show(self, **kwargs):
        """Inserts markup that displays each part of the file collection as an
        image or link.
        """
        the_files = [getattr(self, ext).show(**kwargs) for ext in self._extension_list() if hasattr(self, ext)]
        for the_file in the_files:
            if isinstance(the_file, InlineImage) or isinstance(the_file, Subdoc):
                return the_file
        return u' '.join(the_files)
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return unicode(self._first_file())

class DAFileList(DAList):
    """Used internally by docassemble to refer to a list of files, such as
    a list of files uploaded to a single variable.

    """
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return unicode(self.show())
    def num_pages(self):
        """Returns the total number of pages in the PDF documents, or one page per non-PDF file."""
        result = 0;
        for element in sorted(self.elements):
            if element.ok:
                result += element.num_pages()
        return result        
    def slurp(self, auto_decode=True):
        """Returns the contents of the first file."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].slurp()
    def show(self, width=None):
        """Inserts markup that displays each element in the list as an image.
        Takes an optional keyword argument width.

        """
        output = ''
        for element in sorted(self.elements):
            if element.ok:
                new_image = element.show(width=width)
                if isinstance(new_image, InlineImage) or isinstance(new_image, Subdoc):
                    return new_image
                output += new_image
        return output
    def path(self):
        """Returns a path and filename at which the first file in the
        list can be accessed.

        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].path()
    def url_for(self, **kwargs):
        """Returns a URL to the first file in the list."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].url_for(**kwargs)
    def set_attributes(self, **kwargs):
        """Sets attributes of the file(s) stored on the server.  Takes optional keyword arguments private and persistent, which must be boolean values."""
        for element in sorted(self.elements):
            if element.ok:
                element.set_attributes(**kwargs)

class DAStaticFile(DAObject):
    def init(self, *pargs, **kwargs):
        if 'filename' in kwargs and 'mimetype' not in kwargs and 'extension' not in kwargs:
            self.extension, self.mimetype = server.get_ext_and_mimetype(kwargs['filename'])
        return super(DAStaticFile, self).init(*pargs, **kwargs)
    def show(self, width=None):
        """Inserts markup that displays the file.  Takes an optional keyword
        argument width.

        """
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self)
            else:
                return docassemble.base.file_docx.image_for_docx(docassemble.base.functions.DALocalFile(self.path()), docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.docx_template, width=width)
        else:
            if width is not None:
                return('[FILE ' + str(self.filename) + ', ' + str(width) + ']')
            else:
                return('[FILE ' + str(self.filename) + ']')
    def slurp(self, auto_decode=True):
        """Returns the contents of the file."""
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File " + str(the_path) + " does not exist.")
        with open(the_path, 'rU') as f:
            if auto_decode and hasattr(self, 'mimetype') and (self.mimetype.startswith('text') or self.mimetype in ('application/json', 'application/javascript')):
                return(f.read().decode('utf8'))
            else:
                return(f.read())
    def path(self):
        """Returns a path and filename at which the file can be accessed.

        """
        file_info = server.file_finder(self.filename)
        return file_info.get('fullpath', None)
    def url_for(self, **kwargs):
        """Returns a URL to the static file."""
        the_args = dict()
        for key, val in kwargs.iteritems():
            the_args[key] = val
        the_args['_question'] = docassemble.base.functions.this_thread.current_question
        return server.url_finder(self.filename, **the_args)
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return unicode(self.show())
                
class DAEmailRecipientList(DAList):
    """Represents a list of DAEmailRecipient objects."""
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
    """An object type used within DAEmail objects to represent a single
    e-mail address and the name associated with that e-mail address.

    """
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
        return(unicode(self.address))
    def exists(self):
        return hasattr(self, 'address')
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        if hasattr(self, 'name'):
            name = unicode(self.name)
        else:
            name = u''
        if hasattr(self, 'empty') and self.empty:
            return u''
        if self.address == '' and name == '':
            return u'EMAIL NOT DEFINED'
        if self.address == '' and name != '':
            return name
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return unicode(self.address)
        if name == '' and self.address != '':
            return '[' + unicode(self.address) + '](mailto:' + unicode(self.address) + ')' 
        return '[' + unicode(name) + '](mailto:' + unicode(self.address) + ')'

class DAEmail(DAObject):
    """An object type used to represent an e-mail that has been received
    through the e-mail receiving feature.

    """
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return(u'This is an e-mail')

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
    def show(self, **kwargs):
        """Displays the contents of the template."""
        return unicode(self)
    def __unicode__(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            #return unicode(self.content)
            #return unicode(docassemble.base.filter.docx_template_filter(self.content))
            return unicode(docassemble.base.file_docx.markdown_to_docx(self.content, docassemble.base.functions.this_thread.docx_template))
        return(unicode(self.content))
    def __str__(self):
        return unicode(self).encode('utf-8')

def table_safe(text):
    text = unicode(text)
    text = re.sub(r'[\n\r\|]', ' ', text)
    if re.match(r'[\-:]+', text):
        text = '  ' + text + '  '
    return text

def text_of_table(table_info, user_dict):
    table_content = "\n"
    header_output = [table_safe(x.text(user_dict)) for x in table_info.header]
    the_iterable = eval(table_info.row, user_dict)
    if not hasattr(the_iterable, '__iter__'):
        raise DAError("Error in processing table " + table_info.saveas + ": row value is not iterable")
    if hasattr(the_iterable, 'instanceName') and hasattr(the_iterable, 'elements') and type(the_iterable.elements) in (list, dict) and docassemble.base.functions.get_gathering_mode(the_iterable.instanceName):
        the_iterable = the_iterable.complete_elements()
    indexno = 0
    contents = list()
    for item in the_iterable:
        user_dict['row_item'] = item
        user_dict['row_index'] = indexno
        contents.append([table_safe(eval(x, user_dict)) for x in table_info.column])
        indexno += 1
    user_dict.pop('row_item', None)
    user_dict.pop('row_index', None)
    max_chars = [0 for x in header_output]
    max_word = [0 for x in header_output]
    for indexno in range(len(header_output)):
        words = re.split(r'[ \n]', header_output[indexno])
        if len(header_output[indexno]) > max_chars[indexno]:
            max_chars[indexno] = len(header_output[indexno])
        for content_line in contents:
            words += re.split(r'[ \n]', content_line[indexno])
            if len(content_line[indexno]) > max_chars[indexno]:
                max_chars[indexno] = len(content_line[indexno])
        for text in words:
            if len(text) > max_word[indexno]:
                max_word[indexno] = len(text)
    max_chars_to_use = [min(x, table_info.table_width) for x in max_chars]
    override_mode = False
    while True:
        new_sum = sum(max_chars_to_use)
        old_sum = new_sum
        if new_sum < table_info.table_width:
            break
        r = random.uniform(0, new_sum)
        upto = 0
        for indexno in range(len(max_chars_to_use)):
            if upto + max_chars_to_use[indexno] >= r:
                if max_chars_to_use[indexno] > max_word[indexno] or override_mode:
                    max_chars_to_use[indexno] -= 1
                    break
            upto += max_chars_to_use[indexno]
        new_sum = sum(max_chars_to_use)
        if new_sum == old_sum:
            override_mode = True
    table_content += table_info.indent + "|".join(header_output) + "\n"
    table_content += table_info.indent + "|".join(['-' * x for x in max_chars_to_use]) + "\n"
    for content_line in contents:
        table_content += table_info.indent + "|".join(content_line) + "\n"
    if len(contents) == 0 and table_info.empty_message is not True:
        if table_info.empty_message in (False, None):
            table_content = "\n"
        else:
            table_content = table_info.empty_message.text(user_dict) + "\n"
    table_content += "\n"
    return table_content

class DALazyTemplate(DAObject):
    """The class used for Markdown templates.  A template block saves to
    an object of this type.  The two attributes are "subject" and 
    "content." """
    @property
    def subject(self):
        return self.source_subject.text(self.user_dict).rstrip()
    @property
    def content(self):
        if hasattr(self, 'table_info'):
            return text_of_table(self.table_info, self.user_dict)
        return self.source_content.text(self.user_dict).rstrip()
    @property
    def decorations(self):
        return [dec.text(self.user_dict).rstrip for dec in self.source_decorations]
    def show(self, **kwargs):
        """Displays the contents of the template."""
        return unicode(self)
    def __unicode__(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            #return unicode(self.content)
            #return unicode(docassemble.base.filter.docx_template_filter(self.content))
            return unicode(docassemble.base.file_docx.markdown_to_docx(self.content, docassemble.base.functions.this_thread.docx_template))
        return(unicode(self.content))
    def __str__(self):
        return unicode(self).encode('utf-8')

def selections(*pargs, **kwargs):
    """Packs a list of objects in the appropriate format for including
    as code in a multiple-choice field."""
    to_exclude = set()
    if 'exclude' in kwargs:
        setify(kwargs['exclude'], to_exclude)
    defaults = set()
    if 'default' in kwargs:
        setify(kwargs['default'], defaults)
        defaults.discard(None)
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
                output.append({myb64quote(subarg.instanceName): unicode(subarg), 'default': default_value})
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
    #from docassemble.base.core import DAObject, DAList, DADict, DASet
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
    objects.revisit = True
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

class DALink(DAObject):
    """An object type Represents a hyperlink to a URL."""
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return unicode(self.show())
    def show(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return docassemble.base.file_docx.create_hyperlink(self.url, self.anchor_text, docassemble.base.functions.this_thread.docx_template)
        else:
            return '[%s](%s)' % (self.anchor_text, self.url)
