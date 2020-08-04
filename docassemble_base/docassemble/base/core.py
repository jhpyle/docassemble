from docassemble.base.logger import logmessage
from docassemble.base.generate_key import random_string
import collections.abc as abc
from collections import OrderedDict
from functools import reduce
import re
import os
import codecs
#import redis
import sys
import shutil
import inspect
import yaml
import pycurl
import json
import types
import mimetypes
import datetime
from docassemble.base.functions import possessify, possessify_long, a_preposition_b, a_in_the_b, its, their, the, this, these, underscore_to_space, nice_number, verb_past, verb_present, noun_singular, noun_plural, comma_and_list, ordinal, word, need, capitalize, server, nodoublequote, some, indefinite_article, force_gather, quantity_noun, invalidate
import docassemble.base.functions
import docassemble.base.filter
import docassemble.base.file_docx
from docassemble.base.error import LazyNameError, DAError, DAAttributeError, DAIndexError
from docxtpl import InlineImage, Subdoc
import tempfile
import time
import stat
import copy
import random
#import tablib
import pandas
from PIL import Image
NoneType = type(None)

__all__ = ['DAObject', 'DAList', 'DADict', 'DAOrderedDict', 'DASet', 'DAFile', 'DAFileCollection', 'DAFileList', 'DAStaticFile', 'DAEmail', 'DAEmailRecipient', 'DAEmailRecipientList', 'DATemplate', 'DAEmpty', 'DALink', 'RelationshipTree', 'DAContext']

#unique_names = set()

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
    return random_string(12)
    # while True:
    #     newname = random_string(12)
    #     if newname in unique_names:
    #         continue
    #     unique_names.add(newname)
    #     return newname

class DAEmpty:
    """An object that does nothing except avoid triggering errors about missing information."""
    def __init__(self, *pargs, **kwargs):
        self.str = str(kwargs.get('str', ''))
    def __getattr__(self, thename):
        if thename.startswith('_'):
            return object.__getattribute__(self, thename)
        else:
            return DAEmpty()
    def __str__(self):
        return self.str
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
    def __setitem__(self, index, val):
        return
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
    def __le__(self, other):
        return True
    def __ge__(self, other):
        return self is other or False
    def __gt__(self, other):
        return False
    def __lt__(self, other):
        return True
    def __eq__(self, other):
        return self is other
    def __ne__(self, other):
        return self is not other
    def __hash__(self):
        return hash(('',))

class DAObjectPlusParameters:
    pass

class DAObject:
    """The base class for all docassemble objects."""
    def init(self, *pargs, **kwargs):
        for key, value in kwargs.items():
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
    #     for key, val in kwargs.items():
    #         the_kwargs[key] = val
    #     class constructor(cls):
    #         def init(self, *pargs, **kwargs):
    #             new_args = dict()
    #             for key, val in the_kwargs.items():
    #                 new_args[key] = val
    #             for key, val in kwargs.items():
    #                 new_args[key] = val
    #             return super().init(*pargs, **new_args)
    #     return constructor
    def __init__(self, *pargs, **kwargs):
        thename = None
        if len(pargs):
            pargs = [x for x in pargs]
            thename = pargs.pop(0)
        if thename is not None:
            self.has_nonrandom_instance_name = True
        else:
            stack = inspect.stack()
            frame = stack[1][0]
            the_names = frame.f_code.co_names
            #logmessage("co_name is " + str(frame.f_code.co_names))
            if len(the_names) == 2:
                thename = the_names[1]
                self.has_nonrandom_instance_name = True
            elif len(the_names) == 1 and len(stack) > 2 and len(stack[2][0].f_code.co_names) == 2:
                thename = stack[2][0].f_code.co_names[1]
                self.has_nonrandom_instance_name = True
            else:
                thename = get_unique_name()
                self.has_nonrandom_instance_name = False
            del frame
        self.instanceName = str(thename)
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
    def attr_name(self, attr):
        """Returns a variable name for an attribute, suitable for use in force_ask() and other functions."""
        return self.instanceName + '.' + attr
    def delattr(self, *pargs):
        """Deletes attributes."""
        for attr in pargs:
            if hasattr(self, attr):
                delattr(self, attr)
    def invalidate_attr(self, *pargs):
        """Invalidate attributes."""
        for attr in pargs:
            if hasattr(self, attr):
                invalidate(self.instanceName + '.' + attr)
    def is_peer_relation(self, target, relationship_type, tree):
        for item in tree.query_peer(tree._and(involves=[self, target], relationship_type=relationship_type)):
            return True
        return False
    def is_relation(self, target, relationship_type, tree, self_is='either', filter_by=None):
        extra_queries = list()
        if filter_by is not None:
            if not isinstance(filter_by, dict):
                raise DAError("is_relation: filter_by must be a dictionary.")
            extra_queries = list()
            for key, val in filter_by.items():
                if self_is == 'either':
                    extra_queries.append(tree._or(lambda y: hasattr(self.child, key) and getattr(self.child, key) == val, lambda y: hasattr(y.parent, key) and getattr(y.parent, key) == val))
                elif self_is == 'parent':
                    extra_queries.append(lambda y: hasattr(y.child, key) and getattr(y.child, key) == val)
                elif self_is == 'child':
                    extra_queries.append(lambda y: hasattr(y.parent, key) and getattr(y.parent, key) == val)
                else:
                    raise DAError("is_relation: self_is must be parent, child, or other")
        if self_is == 'either':
            for item in tree.query_peer(tree._and(*extra_queries, involves=[self, target], relationship_type=relationship_type)):
                return True
        elif self_is == 'parent':
            for item in tree.query_peer(tree._and(*extra_queries, parent=self, child=target, relationship_type=relationship_type)):
                return True
        elif self_is == 'child':
            for item in tree.query_peer(tree._and(*extra_queries, child=self, parent=target, relationship_type=relationship_type)):
                return True
        else:
            raise DAError("is_relation: self_is must be parent, child, or other")
        return False
    def get_relation(self, relationship_type, tree, self_is='either', create=False, object_type=None, complete_attribute=None, rel_filter_by=None, filter_by=None, count=1):
        results = DAList(auto_gather=False, gathered=True)
        results.set_random_instance_name()
        if rel_filter_by is None:
            query_params = dict()
        elif isinstance(rel_filter_by, dict):
            query_params = copy.copy(rel_filter_by)
        else:
            raise DAError("get_peer_relation: rel_filter_by must be a dictionary.")
        if self_is == 'either':
            if create:
                raise DAError("get_relation: create can only be used if self_is is parent or child.")
            query_params.update(involves=self, relationship_type=relationship_type)
            for item in tree.query_dir(tree._and(**query_params)):
                if item.parent is not self:
                    results.append(item.parent)
                elif item.child is not self:
                    results.append(item.child)
        elif self_is == 'parent':
            query_params.update(parent=self, relationship_type=relationship_type)
            for item in tree.query_dir(tree._and(**query_params)):
                results.append(item.child)
        elif self_is == 'child':
            query_params.update(child=self, relationship_type=relationship_type)
            for item in tree.query_dir(tree._and(**query_params)):
                results.append(item.parent)
        else:
            raise DAError("get_relation: self_is must be parent, child, or either.")
        if filter_by is not None:
            results = results.filter(**filter_by)
        if create is False or len(results) >= count:
            if len(results) == 1:
                return results[0]
            if len(results) > 1:
                return results
        if create:
            if filter_by is None:
                filter_by = dict()
            if create == 'independent':
                if object_type is None:
                    new_item = tree.leaf.appendObject(self.__class__, **filter_by)
                else:
                    new_item = tree.leaf.appendObject(object_type, **filter_by)
                self.set_relationship(new_item, relationship_type, self_is, tree)
            else:
                if not hasattr(self, 'new_relation'):
                    self.initializeAttribute('new_relation', DADict)
                if relationship_type not in self.new_relation.elements:
                    if object_type is None:
                        object_type = self.__class__
                    self.new_relation.initializeObject(relationship_type, object_type, **filter_by)
                if complete_attribute:
                    getattr(self.new_relation[relationship_type], complete_attribute)
                else:
                    str(self.new_relation[relationship_type])
                new_item = self.new_relation[relationship_type]
                if new_item not in tree.leaf.elements:
                    tree.leaf.append(new_item, set_instance_name=True)
                self.set_peer_relationship(new_item, relationship_type, tree)
                del self.new_relation
            return new_item
        return None
    def get_peer_relation(self, relationship_type, tree, create=False, object_type=None, complete_attribute=None, rel_filter_by=None, filter_by=None, count=1):
        results = DAList(auto_gather=False, gathered=True)
        results.set_random_instance_name()
        if rel_filter_by is None:
            query_params = dict()
        elif isinstance(rel_filter_by, dict):
            query_params = copy.copy(rel_filter_by)
        else:
            raise DAError("get_peer_relation: rel_filter_by must be a dictionary.")
        query_params.update(dict(involves=self, relationship_type=relationship_type))
        for item in tree.query_peer(tree._and(*query_params)):
            for subitem in item.peers:
                if subitem is not self:
                    results.append(subitem)
        if filter_by is not None:
            results = results.filter(**filter_by)
        if count is False or len(results) >= count:
            if len(results) == 1:
                return results[0]
            if len(results) > 1:
                return results
        if create:
            if create == 'independent':
                if object_type is None:
                    new_item = tree.leaf.appendObject(self.__class__)
                else:
                    new_item = tree.leaf.appendObject(object_type)
                self.set_peer_relationship(new_item, relationship_type, tree)
            else:
                if not hasattr(self, 'new_peer_relation'):
                    self.initializeAttribute('new_peer_relation', DADict)
                if relationship_type not in self.new_peer_relation.elements:
                    if object_type is None:
                        object_type = self.__class__
                    self.new_peer_relation.initializeObject(relationship_type, object_type)
                if complete_attribute:
                    getattr(self.new_peer_relation[relationship_type], complete_attribute)
                else:
                    str(self.new_peer_relation[relationship_type])
                new_item = self.new_peer_relation[relationship_type]
                if new_item not in tree.leaf.elements:
                    tree.leaf.append(new_item, set_instance_name=True)
                self.set_peer_relationship(new_item, relationship_type, tree)
                del self.new_peer_relation
            return new_item
        return None
    def set_peer_relationship(self, target, relationship_type, tree, replace=False):
        if replace:
            to_delete = list()
            for item in tree.query_peer(tree._and(involves=self, relationship_type=relationship_type)):
                to_delete.append(item)
            if len(to_delete):
                tree.delete_peer(*to_delete)
        return tree.add_relationship_peer(self, target, relationship_type=relationship_type)
    def set_relationship(self, target, relationship_type, self_is, tree, replace=False):
        if self_is != 'parent' and self_is != 'child':
            raise DAError("set_relationship: self_is must be parent or child")
        if replace:
            to_delete = list()
            if self_is == 'parent':
                for item in tree.query_dir(tree._and(parent=self, relationship_type=relationship_type)):
                    to_delete.append(item)
            elif self_is == 'child':
                for item in tree.query_dir(tree._and(child=self, relationship_type=relationship_type)):
                    to_delete.append(item)
            if len(to_delete):
                tree.delete_dir(*to_delete)
        if self_is == 'parent':
            return tree.add_relationship_dir(parent=self, child=target, relationship_type=relationship_type)
        else:
            return tree.add_relationship_dir(child=self, parent=target, relationship_type=relationship_type)
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
        self.instanceName = str(get_unique_name())
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
    def _set_instance_name_recursively(self, thename, matching=None):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        #logmessage("Change " + str(self.instanceName) + " to " + str(thename))
        #if not self.has_nonrandom_instance_name:
        if matching is not None and not self.instanceName.startswith(matching):
            return
        self.instanceName = thename
        self.has_nonrandom_instance_name = True
        for aname in self.__dict__:
            if hasattr(self, aname) and isinstance(getattr(self, aname), DAObject):
                #logmessage("ASDF Setting " + str(thename) + " for " + str(aname))
                getattr(self, aname)._set_instance_name_recursively(thename + '.' + aname, matching=matching)
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
        if thename.startswith('_') or hasattr(self.__class__, thename):
            if 'pending_error' in docassemble.base.functions.this_thread.misc:
                raise docassemble.base.functions.this_thread.misc['pending_error']
            return object.__getattribute__(self, thename)
        else:
            var_name = object.__getattribute__(self, 'instanceName') + "." + thename
            docassemble.base.functions.this_thread.misc['pending_error'] = DAAttributeError("name '" + var_name + "' is not defined")
            raise docassemble.base.functions.this_thread.misc['pending_error']
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
        capitalize = kwargs.get('capitalize', False)
        if len(self.instanceName.split(".")) > 1:
            return(possessify_long(self.object_name(), target, language=language))
        else:
            return(possessify(the(self.object_name(), language=language), target, language=language, capitalize=capitalize))
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
            for key, val in objectType.parameters.items():
                new_object_parameters[key] = val
            objectType = objectType.object_type
        for key, val in kwargs.items():
            new_object_parameters[key] = val
        if name in self.__dict__:
            return getattr(self, name)
        else:
            object.__setattr__(self, name, objectType(self.instanceName + "." + name, *pargs, **new_object_parameters))
            self.attrList.append(name)
        return getattr(self, name)
    def reInitializeAttribute(self, *pargs, **kwargs):
        """Redefines an attribute for the object, setting it to a newly initialized object.
        The first argument is the name of the attribute and the second argument is type
        of the new object that will be initialized.  E.g.,
        client.reInitializeAttribute('mother', Individual) initializes client.mother as an
        Individual with instanceName "client.mother"."""
        pargs = [x for x in pargs]
        name = pargs.pop(0)
        objectType = pargs.pop(0)
        new_object_parameters = dict()
        if isinstance(objectType, DAObjectPlusParameters):
            for key, val in objectType.parameters.items():
                new_object_parameters[key] = val
            objectType = objectType.object_type
        for key, val in kwargs.items():
            new_object_parameters[key] = val
        object.__setattr__(self, name, objectType(self.instanceName + "." + name, *pargs, **new_object_parameters))
        if name in self.__dict__:
            return getattr(self, name)
        else:
            self.attrList.append(name)
        return getattr(self, name)
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
            return str(self.name)
        return str(self.object_name())
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
        value = getattr(self, attribute)
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
        return super().__setattr__(key, value)
    def __le__(self, other):
        return str(self) <= (str(other) if isinstance(other, DAObject) else other)
    def __ge__(self, other):
        return str(self) >= (str(other) if isinstance(other, DAObject) else other)
    def __gt__(self, other):
        return str(self) > (str(other) if isinstance(other, DAObject) else other)
    def __lt__(self, other):
        return str(self) < (str(other) if isinstance(other, DAObject) else other)
    def __eq__(self, other):
        return self is other
    def __ne__(self, other):
        return self is not other
    def __hash__(self):
        return hash((self.instanceName,))

class DACatchAll(DAObject):
    def data_type_guess(self):
        if not hasattr(self, 'context'):
            return 'str'
        if self.context == 'bool':
            return 'bool'
        if self.context in ('hex', 'rlshift', 'rrshift', 'rand', 'ror', 'int', 'oct', 'hex'):
            return 'int'
        if self.context in ('neg', 'pos', 'abs', 'invert', 'float'):
            return 'float'
        if self.context == 'complex':
            return 'complex'
        if self.context in ('add', 'radd', 'sub', 'rsub', 'mul', 'rmul', 'div', 'rdiv', 'truediv', 'rtruediv', 'floordiv', 'rfloordiv', 'mod', 'rmod', 'divmod', 'rdivmod', 'pow', 'rpow', 'lt', 'eq', 'gt', 'ne', 'ge', 'le'):
            if isinstance(self.operand, bool):
                return 'bool'
            if isinstance(self.operand, str):
                return 'str'
            if isinstance(self.operand, float):
                return 'float'
            if isinstance(self.operand, int):
                return 'int'
            if isinstance(self.operand, complex):
                return 'complex'
            return 'str'
        return 'str'
    def __str__(self):
        self.context = 'str'
        return str(self.value)
    def __dir__(self):
        self.context = 'dir'
        return dir(self.value)
    def __contains__(self, item):
        self.context = 'contains'
        self.operand = item
        return self.value.__contains__(item)
    def __iter__(self):
        self.context = 'iter'
        return self.value.__iter__()
    def __len__(self):
        self.context = 'len'
        return len(self.value)
    def __reversed__(self):
        self.context = 'reversed'
        return reversed(self.value)
    def __getitem__(self, index):
        self.context = 'getitem'
        self.operand = index
        return self.value.__getitem__(index)
    def __repr__(self):
        self.context = 'repr'
        return repr(self.value)
    def __add__(self, other):
        self.context = 'add'
        self.operand = other
        return self.value.__add__(other)
    def __sub__(self, other):
        self.context = 'sub'
        self.operand = other
        return self.value.__sub__(other)
    def __mul__(self, other):
        self.context = 'mul'
        self.operand = other
        return self.value.__mul__(other)
    def __floordiv__(self, other):
        self.context = 'floordiv'
        self.operand = other
        return self.value.__floordiv__(other)
    def __mod__(self, other):
        self.context = 'mod'
        self.operand = other
        return self.value.__mod__(other)
    def __divmod__(self, other):
        self.context = 'divmod'
        self.operand = other
        return self.value.__divmod__(other)
    def __pow__(self, other):
        self.context = 'pow'
        self.operand = other
        return self.value.__pow__(other)
    def __lshift__(self, other):
        self.context = 'lshift'
        self.operand = other
        return self.value.__lshift__(other)
    def __rshift__(self, other):
        self.context = 'rshift'
        self.operand = other
        return self.value.__rshift__(other)
    def __and__(self, other):
        self.context = 'and'
        self.operand = other
        return self.value.__and__(other)
    def __xor__(self, other):
        self.context = 'xor'
        self.operand = other
        return self.value.__xor__(other)
    def __or__(self, other):
        self.context = 'or'
        self.operand = other
        return self.value.__or__(other)
    def __div__(self, other):
        self.context = 'div'
        self.operand = other
        return self.value.__div__(other)
    def __truediv__(self, other):
        self.context = 'truediv'
        self.operand = other
        return self.value.__truediv__(other)
    def __radd__(self, other):
        self.context = 'radd'
        self.operand = other
        return self.value.__radd__(other)
    def __rsub__(self, other):
        self.context = 'rsub'
        self.operand = other
        return self.value.__rsub__(other)
    def __rmul__(self, other):
        self.context = 'rmul'
        self.operand = other
        return self.value.__rmul__(other)
    def __rdiv__(self, other):
        self.context = 'rdiv'
        self.operand = other
        return self.value.__rdiv__(other)
    def __rtruediv__(self, other):
        self.context = 'rtruediv'
        self.operand = other
        return self.value.__rtruediv__(other)
    def __rfloordiv__(self, other):
        self.context = 'rfloordiv'
        self.operand = other
        return self.value.__rfloordiv__(other)
    def __rmod__(self, other):
        self.context = 'rmod'
        self.operand = other
        return self.value.__rmod__(other)
    def __rdivmod__(self, other):
        self.context = 'rdivmod'
        self.operand = other
        return self.value.__rdivmod__(other)
    def __rpow__(self, other):
        self.context = 'rpow'
        self.operand = other
        return self.value.__rpow__(other)
    def __rlshift__(self, other):
        self.context = 'rlshift'
        self.operand = other
        return self.value.__rlshift__(other)
    def __rrshift__(self, other):
        self.context = 'rrshift'
        self.operand = other
        return self.value.__rrshift__(other)
    def __rand__(self, other):
        self.context = 'rand'
        self.operand = other
        return self.value.__rand__(other)
    def __ror__(self, other):
        self.context = 'ror'
        self.operand = other
        return self.value.__ror__(other)
    def __neg__(self):
        self.context = 'neg'
        return self.value.__neg__()
    def __pos__(self):
        self.context = 'pos'
        return self.value.__pos__()
    def __abs__(self):
        self.context = 'abs'
        return abs(self.value)
    def __invert__(self):
        self.context = 'invert'
        return self.value.__invert__()
    def __complex__(self):
        self.context = 'complex'
        return complex(self.value)
    def __int__(self):
        self.context = 'int'
        return int(self.value)
    def __long__(self):
        self.context = 'long'
        return long(self.value)
    def __float__(self):
        self.context = 'float'
        return float(self.value)
    def __oct__(self):
        self.context = 'oct'
        return self.octal_value
    def __hex__(self):
        self.context = 'hex'
        return hex(self.value)
    def __index__(self):
        self.context = 'index'
        return self.value.__index__()
    def __le__(self, other):
        self.context = 'le'
        self.operand = other
        return self.value.__le__(other)
    def __ge__(self, other):
        self.context = 'ge'
        self.operand = other
        return self.value.__ge__(other)
    def __gt__(self, other):
        self.context = 'gt'
        self.operand = other
        return self.value.__gt__(other)
    def __lt__(self, other):
        self.context = 'lt'
        self.operand = other
        return self.value.__lt__(other)
    def __eq__(self, other):
        self.context = 'eq'
        self.operand = other
        return self.value.__eq__(other)
    def __ne__(self, other):
        self.context = 'ne'
        self.operand = other
        return self.value.__ne__(other)
    def __hash__(self):
        self.context = 'hash'
        return hash(self.value)
    def __bool__(self):
        self.context = 'bool'
        return bool(self.value)

class RelationshipDir(DAObject):
    """A data structure representing a relationships among people."""
    def init(self, *pargs, **kwargs):
        return super().init(*pargs, **kwargs)
    def involves(self, target):
        #sys.stderr.write("RelationshipDir: involves " + repr(target) + "\n")
        if self.parent is target or self.child is target:
            return True
        return False

class RelationshipPeer(DAObject):
    """A data structure representing a relationships among people."""
    def init(self, *pargs, **kwargs):
        return super().init(*pargs, **kwargs)
    def involves(self, target):
        #sys.stderr.write("RelationshipPeer: involves " + repr(target) + "\n")
        if target in self.peers:
            return True
        return False

def generator_involves(the_item):
    return lambda y: y.involves(the_item)

def generator_is(the_key, the_val):
    return lambda y: getattr(y, the_key) is the_val

def generator_equals(the_key, the_val):
    return lambda y: getattr(y, the_key) == the_val

class RelationshipTree(DAObject):
    """A data structure that maps the relationships among people."""
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.initializeAttribute('leaf', DAList)
        self.leaf.auto_gather = False
        self.leaf.gathered = True
        self.leaf.object_type = DAObject
        self.leaf.initializeAttribute('existing', DAList)
        self.initializeAttribute('relationships_dir', DAList)
        self.relationships_dir.auto_gather = False
        self.relationships_dir.gathered = True
        self.relationships_dir.object_type = RelationshipDir
        self.initializeAttribute('relationships_peer', DAList)
        self.relationships_peer.auto_gather = False
        self.relationships_peer.gathered = True
        self.relationships_peer.object_type = RelationshipPeer
    def new(self, *pargs, **kwargs):
        return self.leaf.appendObject(*pargs, **kwargs)
    def _func_list(self, *pargs, **kwargs):
        filters = list()
        for item in pargs:
            if isinstance(item, types.FunctionType):
                filters.append(item)
        for key, val in kwargs.items():
            if key == 'involves':
                #sys.stderr.write("_func_list: key is involves\n")
                if isinstance(val, (list, set, DAList, DASet)):
                    #sys.stderr.write("_func_list: involves in a list\n")
                    subfilters = list()
                    for item in val:
                        #sys.stderr.write("_func_list: adding a subfilter\n")
                        subfilters.append(generator_involves(item))
                    filters.append(self._and(*subfilters))
                else:
                    #sys.stderr.write("_func_list: involves without a list\n")
                    filters.append(generator_involves(val))
            elif isinstance(val, DAObject):
                #sys.stderr.write("_func_list: a DAObject\n")
                filters.append(generator_is(key, val))
            else:
                #sys.stderr.write("_func_list: key is " + repr(key) + " and val is " + repr(val) + "\n")
                filters.append(generator_equals(key, val))
        return filters
    def _and(self, *pargs, **kwargs):
        #sys.stderr.write("_and\n")
        filters = self._func_list(*pargs, **kwargs)
        def func(y):
            #sys.stderr.write("in _and func\n")
            for subfunc in filters:
                #sys.stderr.write("evaluating _and func\n")
                result = subfunc(y)
                #sys.stderr.write("result is " + repr(result) + "\n")
                if not result:
                    return False
            return True
        return func
    def _or(self, *pargs, **kwargs):
        #sys.stderr.write("_or\n")
        filters = self._func_list(*pargs, **kwargs)
        def func(y):
            #sys.stderr.write("in _or func\n")
            for subfunc in filters:
                #sys.stderr.write("evaluating _or func\n")
                if subfunc(y):
                    return True
            return False
        return func
    def query_peer(self, *pargs, **kwargs):
        #sys.stderr.write("query_peer\n")
        if len(pargs) == 0 and len(kwargs) == 1:
            func = self._func_list(*pargs, **kwargs)[0]
        elif len(pargs) == 1:
            func = pargs[0]
        else:
            func = None
        if not isinstance(func, types.FunctionType):
            raise DAError("Invalid RelationshipTree query")
        return (y for y in self.relationships_peer if func(y))
    def query_dir(self, *pargs, **kwargs):
        #sys.stderr.write("query_dir\n")
        if len(pargs) == 0 and len(kwargs) == 1:
            func = self._func_list(*pargs, **kwargs)[0]
        elif len(pargs) == 1:
            func = pargs[0]
        else:
            func = None
        if not isinstance(func, types.FunctionType):
            raise DAError("Invalid RelationshipTree query")
        return (y for y in self.relationships_dir if func(y))
    def add_relationship_dir(self, parent=None, child=None, relationship_type=None):
        """Creates a relationship between the person and another object."""
        for item in self.relationships_dir:
            if item.relationship_type == relationship_type and (hasattr(item, 'parent') and item.parent is parent) and (hasattr(item, 'child') and item.child is child):
                return item
        args = dict()
        if parent is not None:
            args['parent'] = parent
        if child is not None:
            args['child'] = child
        if relationship_type is not None:
            args['relationship_type'] = relationship_type
        return self.relationships_dir.appendObject(**args)
    def delete_dir(self, *pargs):
        """Deletes the given relationship(s)"""
        self.relationships_dir.remove(*pargs)
    def add_relationship_peer(self, *pargs, **kwargs):
        """Creates a relationship between the person and another object."""
        relationship_type = kwargs.get('relationship_type', None)
        the_set = set(pargs)
        for item in self.relationships_peer:
            if item.relationship_type == relationship_type and item.peers == the_set:
                return item
        #sys.stderr.write("Setting relationship involving " + repr(the_set) + " and reltype " + relationship_type + "\n")
        return self.relationships_peer.appendObject(peers=the_set, relationship_type=relationship_type)
    def delete_peer(self, *pargs):
        """Deletes the given peer relationship(s)"""
        self.relationships_peer.remove(*pargs)
    def delete_dir(self, *pargs):
        """Deletes the given relationship(s)"""
        self.relationships_dir.remove(*pargs)

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
            if len(self.elements) > 0:
                self.there_are_any = True
            else:
                self.there_are_any = False
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
        return super().init(*pargs, **kwargs)
    def initializeObject(self, *pargs, **kwargs):
        """Creates a new object and creates an entry in the list for it.
        The first argument is the index to set.
        Takes an optional second argument, which is the type of object
        the new object should be.  If no object type is provided, the
        object type given by .object_type is used, and if that is not
        set, DAObject is used.

        """
        objectFunction = None
        pargs = [x for x in pargs]
        index = pargs.pop(0)
        if len(pargs) > 0:
            objectFunction = pargs.pop(0)
        new_obj_parameters = dict()
        if isinstance(objectFunction, DAObjectPlusParameters):
            for key, val in objectFunction.parameters.items():
                new_obj_parameters[key] = val
            objectFunction = objectFunction.object_type
        if objectFunction is None:
            if self.object_type is not None:
                objectFunction = self.object_type
                for key, val in self.object_type_parameters.items():
                    new_obj_parameters[key] = val
            else:
                objectFunction = DAObject
                object_type_parameters = dict()
        for key, val in kwargs.items():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + repr(index) + ']', *pargs, **new_obj_parameters)
        for pre_index in range(index):
            self.elements.append(None)
        self[index] = newobject
        self.there_are_any = True
        return newobject
    def gathered_and_complete(self):
        """Ensures all items in the list are complete and then returns True."""
        if not hasattr(self, 'doing_gathered_and_complete'):
            self.doing_gathered_and_complete = True
            if hasattr(self, 'complete_attribute') and self.complete_attribute == 'complete':
                for item in self.elements:
                    if hasattr(item, self.complete_attribute):
                        delattr(item, self.complete_attribute)
            if hasattr(self, 'gathered'):
                del self.gathered
        if self.auto_gather:
            self.gather()
        else:
            self.hook_on_gather()
            self.gathered
            self.hook_after_gather()
        if hasattr(self, 'doing_gathered_and_complete'):
            del self.doing_gathered_and_complete
        return True
    def copy(self):
        """Returns a copy of the list."""
        return self.elements.copy()
    def filter(self, *pargs, **kwargs):
        """Returns a filtered version of the list containing only items with particular values of attributes."""
        self._trigger_gather()
        new_elements = list()
        for item in self.elements:
            include = True
            for key, val in kwargs.items():
                if getattr(item, key) != val:
                    include = False
                    break
            if include:
                new_elements.append(item)
        if len(pargs):
            new_instance_name = pargs[0]
        else:
            new_instance_name = self.instanceName
        new_list = self.copy_shallow(new_instance_name)
        new_list.elements = new_elements
        new_list.gathered = True
        if len(new_list.elements) == 0:
            new_list.there_are_any = False
        return new_list

    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered
        return
    def reset_gathered(self, recursive=False, only_if_empty=False, mark_incomplete=False):
        """Indicates that there is more to be gathered"""
        #logmessage("reset_gathered on " + self.instanceName)
        if only_if_empty and len(self.elements) > 0:
            return
        if len(self.elements) == 0 and hasattr(self, 'there_are_any'):
            delattr(self, 'there_are_any')
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'there_is_one_other'):
            delattr(self, 'there_is_one_other')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if hasattr(self, 'revisit'):
            delattr(self, 'revisit')
        if hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        if mark_incomplete and self.complete_attribute is not None:
            for item in self.elements:
                if hasattr(item, self.complete_attribute):
                    delattr(item, self.complete_attribute)
        if recursive:
            self._reset_gathered_recursively()
    def has_been_gathered(self):
        """Returns whether the list has been gathered"""
        if hasattr(self, 'gathered'):
            return True
        if hasattr(self, 'was_gathered') and self.was_gathered:
            return True
        return False
    def pop(self, *pargs):
        """Remove an item the list and return it."""
        #self._trigger_gather()
        if len(pargs) == 1:
            self.hook_on_remove(self.elements[pargs[0]])
        elif len(self.elements) > 0:
            self.hook_on_remove(self.elements[-1])
        result = self.elements.pop(*pargs)
        self._reset_instance_names()
        if len(self.elements) == 0:
            self.there_are_any = False
        return result
    def item(self, index):
        """Returns the value for the given index, or a blank value if the index does not exist."""
        self._trigger_gather()
        if index < len(self.elements):
            return self[index]
        return DAEmpty()
    def __add__(self, other):
        self._trigger_gather()
        if isinstance(other, DAEmpty):
            return self
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
        return super().fix_instance_name(old_instance_name, new_instance_name)
    def _set_instance_name_recursively(self, thename, matching=None):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        indexno = 0
        for item in self.elements:
            if isinstance(item, DAObject):
                item._set_instance_name_recursively(thename + '[' + str(indexno) + ']', matching=matching)
            indexno += 1
        return super()._set_instance_name_recursively(thename, matching=matching)
    def _mark_as_gathered_recursively(self):
        for item in self.elements:
            if isinstance(item, DAObject):
                item._mark_as_gathered_recursively()
        return super()._mark_as_gathered_recursively()
    def _reset_gathered_recursively(self):
        self.reset_gathered()
        for item in self.elements:
            if isinstance(item, DAObject):
                item._reset_gathered_recursively()
        return super()._reset_gathered_recursively()
    def _reset_instance_names(self):
        indexno = 0
        for item in self.elements:
            if isinstance(item, DAObject) and item.instanceName.startswith(self.instanceName + '['):
                item._set_instance_name_recursively(self.instanceName + '[' + str(indexno) + ']', matching=self.instanceName + '[')
            indexno += 1
    def sort(self, *pargs, **kwargs):
        """Reorders the elements of the list and returns the object."""
        self._trigger_gather()
        self.elements = sorted(self.elements, **kwargs)
        self._reset_instance_names()
        return self
    def sort_elements(self, *pargs, **kwargs):
        """Reorders the elements of the list and returns the object, without
        triggering the gathering process.

        """
        self.elements = sorted(self.elements, **kwargs)
        self._reset_instance_names()
        return self
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
                for key, val in self.object_type_parameters.items():
                    new_obj_parameters[key] = val
            else:
                objectFunction = DAObject
        for key, val in kwargs.items():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + str(len(self.elements)) + ']', *pargs, **new_obj_parameters)
        self.elements.append(newobject)
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
        if something_added and len(self.elements) > 0:
            self.there_are_any = True
    def remove(self, *pargs):
        """Removes the given arguments from the list, if they are in the list"""
        something_removed = False
        for value in pargs:
            if value in self.elements:
                self.hook_on_remove(value)
                self.elements.remove(value)
                something_removed = True
        self._reset_instance_names()
        if something_removed and len(self.elements) == 0:
            self.there_are_any = False
    def _remove_items_by_number(self, *pargs):
        """Removes items from the list, by index number"""
        new_list = list()
        list_truncated = False
        for indexno in range(len(self.elements)):
            if indexno not in pargs:
                new_list.append(self.elements[indexno])
            else:
                list_truncated = True
        self.elements = new_list
        self._reset_instance_names()
        if list_truncated and hasattr(self, '_necessary_length'):
            del self._necessary_length
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
            output = noun_singular(the_noun)
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
    def gathering_started(self):
        """Returns True if the gathering process has started or the number of elements is non-zero."""
        if hasattr(self, 'gathered') or hasattr(self, 'there_are_any') or len(self.elements) > 0:
            return True
        return False
    def number_gathered(self, if_started=False):
        """Returns the number of elements in the list that have been gathered so far."""
        if if_started and not self.gathering_started():
            self._trigger_gather()
        return len(self.elements)
    def current_index(self):
        """Returns the index number of the last element added to the list, or 0 if no elements have been added."""
        if len(self.elements) == 0:
            return 0
        return len(self.elements) - 1
    def number_as_word(self, language=None, capitalize=False):
        """Returns the number of elements in the list, spelling out the number if ten
        or below.  Forces the gathering of the elements if necessary."""
        return nice_number(self.number(), language=language, capitalize=capitalize)
    def complete_elements(self, complete_attribute=None):
        """Returns a list of the elements that are complete."""
        if complete_attribute is None and hasattr(self, 'complete_attribute'):
            complete_attribute = self.complete_attribute
        items = DAList(self.instanceName)
        for item in self.elements:
            if item is None:
                continue
            if complete_attribute is not None:
                if not hasattr(item, complete_attribute):
                    continue
            else:
                try:
                    str(item)
                except:
                    continue
            items.append(item)
        items.gathered = True
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
                    str(self.elements[indexno])
            if hasattr(self, 'new_object_type'):
                delattr(self, 'new_object_type')
        for elem in self.elements:
            if item_object_type is not None and complete_attribute is not None:
                getattr(elem, complete_attribute)
            else:
                str(elem)
    def _allow_appending(self):
        self._appending_allowed = True
    def _disallow_appending(self):
        if hasattr(self, '_appending_allowed'):
            del self._appending_allowed
    def gather(self, number=None, item_object_type=None, minimum=None, complete_attribute=None):
        """Causes the elements of the list to be gathered and named.  Returns True."""
        #sys.stderr.write("Gather\n")
        if hasattr(self, 'gathered') and self.gathered:
            if self.auto_gather and len(self.elements) == 0 and hasattr(self, 'there_are_any') and self.there_are_any:
                del self.gathered
            else:
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
            if hasattr(self, 'there_are_any') and not self.there_are_any:
                number = 0
            else:
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
        if minimum is not None:
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
                the_length = len(self.elements)
            if hasattr(self, '_necessary_length'):
                del self._necessary_length
        elif minimum != 0:
            while self.there_is_another or (hasattr(self, 'there_is_one_other') and self.there_is_one_other):
                #logmessage("gather " + self.instanceName + ": del on there_is_another")
                if hasattr(self, 'there_is_one_other'):
                    del self.there_is_one_other
                elif hasattr(self, 'there_is_another'):
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
        self.hook_on_gather()
        if self.auto_gather:
            self.gathered = True
            self.revisit = True
        #if hasattr(self, 'doing_gathered_and_complete'):
        #    del self.doing_gathered_and_complete
        if hasattr(self, 'was_gathered'):
            del self.was_gathered
        docassemble.base.functions.set_gathering_mode(False, self.instanceName)
        self.hook_after_gather()
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
        if hasattr(self, 'there_are_any') and not self.there_are_any:
            return 0
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
        if isinstance(index, str):
            raise Exception("Attempt to fill up " + self.instanceName + " with index " + index)
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
            if self.auto_gather and hasattr(self, 'gathered') and not (hasattr(self, '_appending_allowed') and self._appending_allowed):
                try:
                    logmessage("list index " + str(index) + " out of range on " + str(self.instanceName))
                except:
                    pass
                raise IndexError("list index out of range")
            elif self.object_type is None and not self.ask_object_type:
                var_name = object.__getattribute__(self, 'instanceName') + '[' + str(index) + ']'
                #force_gather(var_name)
                raise DAIndexError("name '" + var_name + "' is not defined")
            else:
                #sys.stderr.write("Calling fill up to\n")
                self._fill_up_to(index)
            #sys.stderr.write("Assuming it is there!\n")
            return self.elements[index]
    def __str__(self):
        self._trigger_gather()
        return str(self.comma_and_list())
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
    def _reorder(self, *pargs):
        old_elements = self.elements
        self.elements = copy.copy(self.elements)
        maximum = len(self.elements)
        for item in pargs:
            if item[0] < maximum and item[1] < maximum:
                self.elements[item[1]] = old_elements[item[0]]
    def item_actions(self, *pargs, **kwargs):
        """Returns HTML for editing the items in a list"""
        the_args = list(pargs)
        item = the_args.pop(0)
        index = the_args.pop(0)
        output = ''
        if kwargs.get('reorder', False):
            output += '<a href="#" role="button" class="btn btn-sm ' + docassemble.base.functions.server.button_class_prefix + 'info btn-darevisit datableup" data-tablename="' + myb64quote(self.instanceName) + '" data-tableitem="' + str(index) + '" title=' + json.dumps(word("Reorder by moving up")) + '><i class="fas fa-arrow-up"></i><span class="sr-only">' + word("Move down") + '</span></a> <a href="#" role="button" class="btn btn-sm ' + docassemble.base.functions.server.button_class_prefix + 'info btn-darevisit databledown"><i class="fas fa-arrow-down" title=' + json.dumps(word("Reorder by moving down")) + '></i><span class="sr-only">' + word("Move down") + '</span></a> '
        if self.minimum_number is not None and len(self.elements) <= self.minimum_number:
            can_delete = False
        else:
            can_delete = True
        use_edit = kwargs.get('edit', True)
        use_delete = kwargs.get('delete', True)
        ensure_complete = kwargs.get('ensure_complete', True)
        if 'read_only_attribute' in kwargs:
            val = getattr(item, kwargs['read_only_attribute'])
            if isinstance(val, bool):
                if val:
                    use_edit = False
                    use_delete = False
            elif hasattr(val, 'items') and hasattr(val, 'get'):
                use_edit = val.get('edit', True)
                use_delete = val.get('delete', True)
        if use_edit:
            items = []
            #if self.complete_attribute == 'complete':
            #    items += [dict(action='_da_undefine', arguments=dict(variables=[item.instanceName + '.' + self.complete_attribute]))]
            if len(the_args):
                items += [{'follow up': [item.instanceName + ('' if y.startswith('[') else '.') + y for y in the_args]}]
            else:
                items += [{'follow up': [self.instanceName + '[' + repr(index) + ']']}]
            if self.complete_attribute is not None and self.complete_attribute != 'complete':
                items += [dict(action='_da_define', arguments=dict(variables=[item.instanceName + '.' + self.complete_attribute]))]
            if ensure_complete:
                items += [dict(action='_da_list_ensure_complete', arguments=dict(group=self.instanceName))]
            output += '<a href="' + docassemble.base.functions.url_action('_da_list_edit', items=items) + '" role="button" class="btn btn-sm ' + docassemble.base.functions.server.button_class_prefix + 'secondary btn-darevisit"><i class="fas fa-pencil-alt"></i> ' + word('Edit') + '</a> '
        if use_delete and can_delete:
            if kwargs.get('confirm', False):
                areyousure = ' daremovebutton'
            else:
                areyousure = ''
            output += '<a href="' + docassemble.base.functions.url_action('_da_list_remove', list=self.instanceName, item=repr(index)) + '" role="button" class="btn btn-sm ' + docassemble.base.functions.server.button_class_prefix + 'danger btn-darevisit' + areyousure +'"><i class="fas fa-trash"></i> ' + word('Delete') + '</a>'
        if kwargs.get('edit_url_only', False):
            return docassemble.base.functions.url_action('_da_list_edit', items=items)
        if kwargs.get('delete_url_only', False):
            return docassemble.base.functions.url_action('_da_list_remove', dict=self.instanceName, item=repr(index))
        return output
    def add_action(self, label=None, message=None, url_only=False, icon='plus-circle', color='success', size='sm', block=None, classname=None):
        """Returns HTML for adding an item to a list"""
        if color not in ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'):
            color = 'success'
        if size not in ('sm', 'md', 'lg'):
            size = 'sm'
        if size == 'md':
            size = ''
        else:
            size = " btn-" + size
        if block:
            block = ' btn-block'
        else:
            block = ''
        if isinstance(icon, str):
            icon = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', icon)
            if not re.search(r'^fa[a-z] fa-', icon):
                icon = 'fas fa-' + icon
            icon = '<i class="' + icon + '"></i> '
        else:
            icon = ''
        if classname is None:
            classname = ''
        else:
            classname = ' ' + str(classname)
        if message is not None:
            logmessage("add_action: note that the 'message' parameter has been renamed to 'label'.")
        if message is None and label is not None:
            message = label
        if message is None:
            if len(self.elements) > 0:
                message = word("Add another")
            else:
                message = word("Add an item")
        else:
            message = word(str(message))
        if url_only:
            return docassemble.base.functions.url_action('_da_list_add', list=self.instanceName)
        return '<a href="' + docassemble.base.functions.url_action('_da_list_add', list=self.instanceName) + '" class="btn' + size + block + ' ' + docassemble.base.functions.server.button_class_prefix + color + classname + '">' + icon + str(message) + '</a>'
    def hook_on_gather(self):
        pass
    def hook_after_gather(self):
        pass
    def hook_on_item_complete(self, item):
        pass
    def hook_on_remove(self, item):
        pass
    def __eq__(self, other):
        self._trigger_gather()
        return self.elements == other
    def __hash__(self):
        return hash((self.instanceName,))

class DADict(DAObject):
    """A base class for objects that behave like Python dictionaries."""
    def init(self, *pargs, **kwargs):
        self.elements = self._new_elements()
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
            if kwargs['ask_object_type']:
                self.ask_object_type = True
            del kwargs['ask_object_type']
        if not hasattr(self, 'ask_object_type'):
            self.ask_object_type = False
        if 'keys' in kwargs:
            if isinstance(kwargs['keys'], (DAList, DASet, abc.Iterable)) and not isinstance(kwargs['keys'], str):
                self.new(kwargs['keys'])
            del kwargs['keys']
        return super().init(*pargs, **kwargs)
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
        for key, value in self.elements.items():
            if isinstance(value, DAObject):
                value.fix_instance_name(old_instance_name, new_instance_name)
        return super().fix_instance_name(old_instance_name, new_instance_name)
    def _set_instance_name_recursively(self, thename, matching=None):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        for key, value in self.elements.items():
            if isinstance(value, DAObject):
                value._set_instance_name_recursively(thename + '[' + repr(key) + ']', matching=matching)
        return super()._set_instance_name_recursively(thename, matching=matching)
    def _mark_as_gathered_recursively(self):
        for key, value in self.elements.items():
            if isinstance(value, DAObject):
                value._mark_as_gathered_recursively()
        return super()._mark_as_gathered_recursively()
    def _reset_gathered_recursively(self):
        self.reset_gathered()
        for key, value in self.elements.items():
            if isinstance(value, DAObject):
                value._reset_gathered_recursively()
        return super()._reset_gathered_recursively()
    def all_false(self, *pargs, **kwargs):
        """Returns True if the values of all keys are false.  If one or more
        keys are provided as arguments, returns True if all of the
        values of those keys are false.  If the optional keyword
        argument 'exclusive' is True, returns True only if those keys
        are the only false values.

        """
        the_list = list()
        exclusive = kwargs.get('exclusive', False)
        for parg in pargs:
            if isinstance(parg, (DAList, DASet, abc.Iterable)) and not isinstance(parg, str):
                the_list.extend([x for x in parg])
            else:
                the_list.append(parg)
        if len(the_list) == 0:
            for key, value in self._sorted_elements_items():
                if value:
                    return False
            self._trigger_gather()
            return True
        for key in the_list:
            if key not in self.elements:
                return False
        for key, value in self._sorted_elements_items():
            if key in the_list:
                if value:
                    return False
            else:
                if exclusive and not value:
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
        """Returns True if the values of all keys are true.  If one or more
        keys are provided as arguments, returns True if all of the
        values of those keys are true.  If the optional keyword
        argument 'exclusive' is True, returns True only if those keys
        are the only true values.

        """
        the_list = list()
        exclusive = kwargs.get('exclusive', False)
        for parg in pargs:
            if isinstance(parg, (DAList, DASet, abc.Iterable)) and not isinstance(parg, str):
                the_list.extend([x for x in parg])
            else:
                the_list.append(parg)
        if len(the_list) == 0:
            for key, value in self._sorted_elements_items():
                if not value:
                    return False
            self._trigger_gather()
            return True
        for key in the_list:
            if key not in self.elements:
                return False
        for key, value in self._sorted_elements_items():
            if key in the_list:
                if not value:
                    return False
            else:
                if exclusive and value:
                    return False
        self._trigger_gather()
        return True
    def true_values(self):
        """Returns the keys for which the corresponding value is true."""
        return DAList(elements=[key for key, value in self._sorted_items() if value])
    def false_values(self):
        """Returns the keys for which the corresponding value is false."""
        return DAList(elements=[key for key, value in self._sorted_items() if not value])
    def _sorted_items(self):
        return sorted(self.items())
    def _sorted_elements_items(self):
        return sorted(self.elements.items())
    def _sorted_iteritems(self):
        return sorted(self.items())
    def _sorted_elements_iteritems(self):
        return sorted(self.elements.items())
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
            for key, val in objectFunction.parameters.items():
                new_obj_parameters[key] = val
            objectFunction = objectFunction.object_type
        if objectFunction is None:
            if self.object_type is not None:
                objectFunction = self.object_type
                for key, val in self.object_type_parameters.items():
                    new_obj_parameters[key] = val
            else:
                objectFunction = DAObject
                object_type_parameters = dict()
        for key, val in kwargs.items():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + repr(entry) + ']', *pargs, **new_obj_parameters)
        self.elements[entry] = newobject
        self.there_are_any = True
        return newobject
    def new(self, *pargs, **kwargs):
        """Initializes new dictionary entries.  Each entry is set to a
        new object.  For example, if the dictionary is called positions,
        calling positions.new('file clerk') will result in the creation of
        the object positions['file clerk'].  The type of object is given by
        the object_type attribute, or DAObject if object_type is not set."""
        for parg in pargs:
            if isinstance(parg, (DAList, DASet, abc.Iterable)) and not isinstance(parg, str):
                for item in parg:
                    self.new(item, **kwargs)
            else:
                new_obj_parameters = dict()
                if self.object_type is not None:
                    item_object_type = self.object_type
                    for key, val in self.object_type_parameters.items():
                        new_obj_parameters[key] = val
                else:
                    item_object_type = DAObject
                for key, val in kwargs.items():
                    new_obj_parameters[key] = val
                if parg not in self.elements:
                    self.initializeObject(parg, item_object_type, **new_obj_parameters)
    def reset_gathered(self, recursive=False, only_if_empty=False, mark_incomplete=False):
        """Indicates that there is more to be gathered"""
        #logmessage("reset_gathered on " + self.instanceName)
        if only_if_empty and len(self.elements) > 0:
            return
        if len(self.elements) == 0 and hasattr(self, 'there_are_any'):
            delattr(self, 'there_are_any')
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'there_is_one_other'):
            delattr(self, 'there_is_one_other')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if hasattr(self, 'revisit'):
            delattr(self, 'revisit')
        if hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        if mark_incomplete and self.complete_attribute is not None:
            for item in list(self.elements.values()):
                if hasattr(item, self.complete_attribute):
                    delattr(item, self.complete_attribute)
        if recursive:
            self._reset_gathered_recursively()
    def slice(self, *pargs):
        """Returns a shallow copy of the dictionary containing only the keys provided in the parameters."""
        new_dict = copy.copy(self)
        if len(pargs) == 1 and type(pargs[0]) is types.FunctionType:
            the_func = pargs[0]
            new_dict.elements = {key: self.elements[key] for key in self.elements if the_func(self.elements[key])}
        else:
            new_dict.elements = {key: self.elements[key] for key in pargs if key in self.elements}
        new_dict.gathered = True
        if len(new_dict.elements) == 0:
            new_dict.there_are_any = False
        return new_dict
    def has_been_gathered(self):
        """Returns whether the dictionary has been gathered"""
        if hasattr(self, 'gathered'):
            return True
        if hasattr(self, 'was_gathered') and self.was_gathered:
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
            output = noun_singular(the_noun)
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
    def gathering_started(self):
        """Returns True if the gathering process has started or the number of elements is non-zero."""
        if hasattr(self, 'gathered') or hasattr(self, 'there_are_any') or len(self.elements) > 0:
            return True
        return False
    def number_gathered(self, if_started=False):
        """Returns the number of elements in the list that have been gathered so far."""
        if if_started and not self.gathering_started():
            self._trigger_gather()
        return len(self.elements)
    def number_as_word(self, language=None):
        """Returns the number of keys in the dictionary, spelling out the number if ten
        or below.  Forces the gathering of the dictionary items if necessary."""
        return nice_number(self.number(), language=language)
    def complete_elements(self, complete_attribute=None):
        """Returns a dictionary containing the key/value pairs that are complete."""
        if complete_attribute is None and hasattr(self, 'complete_attribute'):
            complete_attribute = self.complete_attribute
        items = dict()
        for key, val in self.elements.items():
            if val is None:
                continue
            if complete_attribute is not None:
                if not hasattr(val, complete_attribute):
                    continue
            else:
                try:
                    str(val)
                except:
                    continue
            items[key] = val
        return items
    def _sorted_keys(self):
        return sorted(self.keys())
    def _sorted_elements_keys(self):
        return sorted(self.elements.keys())
    def _validate(self, item_object_type, complete_attribute, keys=None):
        if keys is None:
            try:
                keys = self._sorted_elements_keys()
            except TypeError:
                keys = list(self.elements.keys())
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
                str(elem)
    def gathered_and_complete(self):
        """Ensures all items in the dictionary are complete and then returns True."""
        if not hasattr(self, 'doing_gathered_and_complete'):
            self.doing_gathered_and_complete = True
            if self.complete_attribute == 'complete':
                for item in list(self.elements.values()):
                    if hasattr(item, self.complete_attribute):
                        delattr(item, self.complete_attribute)
            if hasattr(self, 'gathered'):
                del self.gathered
        if self.auto_gather:
            self.gather()
        else:
            self.hook_on_gather()
            self.gathered
            self.hook_after_gather()
        if hasattr(self, 'doing_gathered_and_complete'):
            del self.doing_gathered_and_complete
        return True
    def gather(self, item_object_type=None, number=None, minimum=None, complete_attribute=None, keys=None):
        """Causes the dictionary items to be gathered and named.  Returns True."""
        if hasattr(self, 'gathered') and self.gathered:
            if self.auto_gather and len(self.elements) == 0 and hasattr(self, 'there_are_any') and self.there_are_any:
                del self.gathered
            else:
                return True
        if not self.auto_gather:
            return self.gathered
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
        if number is None and self.ask_number:
            if hasattr(self, 'there_are_any') and not self.there_are_any:
                number = 0
            else:
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
            if hasattr(self, 'there_is_one_other'):
                delattr(self, 'there_is_one_other')
            elif hasattr(self, 'there_is_another'):
                #logmessage("0gather " + self.instanceName + ": del on there_is_another")
                delattr(self, 'there_is_another')
        while (number is not None and len(self.elements) < int(number)) or (minimum is not None and len(self.elements) < int(minimum)) or (self.ask_number is False and minimum != 0 and (self.there_is_another or (hasattr(self, 'there_is_one_other') and self.there_is_one_other))):
            if item_object_type is not None:
                self.initializeObject(self.new_item_name, item_object_type, **new_item_parameters)
                if hasattr(self, 'there_is_one_other'):
                    delattr(self, 'there_is_one_other')
                elif hasattr(self, 'there_is_another'):
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
                    if hasattr(self, 'there_is_one_other'):
                        delattr(self, 'there_is_one_other')
                    elif hasattr(self, 'there_is_another'):
                        #logmessage("2gather " + self.instanceName + ": del on there_is_another")
                        delattr(self, 'there_is_another')
                else:
                    the_name = self.new_item_name
                    self.__getitem__(the_name)
                    if hasattr(self, 'new_item_name'):
                        delattr(self, 'new_item_name')
                    if hasattr(self, 'there_is_one_other'):
                        delattr(self, 'there_is_one_other')
                    elif hasattr(self, 'there_is_another'):
                        #logmessage("3gather " + self.instanceName + ": del on there_is_another")
                        delattr(self, 'there_is_another')
            if hasattr(self, 'there_is_one_other'):
                delattr(self, 'there_is_one_other')
            elif hasattr(self, 'there_is_another'):
                #logmessage("4gather " + self.instanceName + ": del on there_is_another")
                delattr(self, 'there_is_another')
        self._validate(item_object_type, complete_attribute, keys=keys)
        self.hook_on_gather()
        if self.auto_gather:
            self.gathered = True
            self.revisit = True
        docassemble.base.functions.set_gathering_mode(False, self.instanceName)
        self.hook_after_gather()
        return True
    def _sorted_elements_values(self):
        return sorted(self.elements.values())
    def _sorted_values(self):
        return sorted(self.values())
    def _new_item_init_callback(self):
        if hasattr(self, 'new_item_name'):
            delattr(self, 'new_item_name')
        if hasattr(self, 'new_item_value'):
            delattr(self, 'new_item_value')
        for elem in self._sorted_elements_values():
            if self.object_type is not None and self.complete_attribute is not None:
                getattr(elem, self.complete_attribute)
            else:
                str(elem)
        return
    def comma_and_list(self, **kwargs):
        """Returns the keys of the list, separated by commas, with
        "and" before the last key."""
        self._trigger_gather()
        try:
            return comma_and_list(self._sorted_elements_keys(), **kwargs)
        except TypeError:
            return comma_and_list(self.elements.keys(), **kwargs)
    def __getitem__(self, index):
        if index not in self.elements:
            if self.object_type is None:
                var_name = object.__getattribute__(self, 'instanceName') + "[" + repr(index) + "]"
                raise DAIndexError("name '" + var_name + "' is not defined")
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
        try:
            return self._sorted_elements_keys()
        except TypeError:
            return list(self.elements.keys())
    def values(self):
        """Returns the values of the dictionary as a Python list."""
        self._trigger_gather()
        return self.elements.values()
    def update(self, *pargs, **kwargs):
        """Updates the dictionary with the keys and values of another dictionary"""
        if len(pargs) > 0:
            other_dict = pargs[0]
            if isinstance(other_dict, DADict):
                return self.elements.update(other_dict.elements)
        self.elements.update(*pargs, **kwargs)
    def pop(self, *pargs):
        """Remove a given key from the dictionary and return its value"""
        if pargs[0] in self.elements:
            self.hook_on_remove(self.elements[pargs[0]])
        if len(self.elements) == 1:
            self.there_are_any = False
        return self.elements.pop(*pargs)
    def popitem(self):
        """Remove an arbitrary key from the dictionary and return its value"""
        if len(self.elements) == 1:
            self.there_are_any = False
        return self.elements.popitem()
    def setdefault(self, *pargs):
        """Set a key to a default value if it does not already exist in the dictionary"""
        return self.elements.setdefault(*pargs)
    def get(self, *pargs):
        """Returns the value of a given key."""
        if len(pargs) == 1:
            return self[pargs[0]]
        return self.elements.get(*pargs)
    def clear(self):
        """Removes all the items from the dictionary."""
        return self.elements.clear()
    def copy(self):
        """Returns a copy of the dictionary."""
        return self.elements.copy()
    def has_key(self, key):
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
        return self.elements.items()
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
        if hasattr(self, 'there_are_any') and not self.there_are_any:
            return 0
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
    #def __hash__(self):
    #    self._trigger_gather()
    #    return self.elements.__hash__()
    def __str__(self):
        return str(self.comma_and_list())
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
    def item_actions(self, *pargs, **kwargs):
        """Returns HTML for editing the items in a dictionary"""
        the_args = list(pargs)
        item = the_args.pop(0)
        index = the_args.pop(0)
        output = ''
        if self.minimum_number is not None and len(self.elements) <= self.minimum_number:
            can_delete = False
        else:
            can_delete = True
        use_edit = kwargs.get('edit', True)
        use_delete = kwargs.get('delete', True)
        ensure_complete = kwargs.get('ensure_complete', True)
        if 'read_only_attribute' in kwargs:
            val = getattr(item, kwargs['read_only_attribute'])
            if isinstance(val, bool):
                if val:
                    use_edit = False
                    use_delete = False
            elif hasattr(val, 'items') and hasattr(val, 'get'):
                use_edit = val.get('edit', True)
                use_delete = val.get('delete', True)
        if use_edit:
            items = []
            if self.complete_attribute == 'complete':
                items += [dict(action='_da_undefine', arguments=dict(variables=[item.instanceName + '.' + self.complete_attribute]))]
            if len(the_args):
                items += [{'follow up': [item.instanceName + ('' if y.startswith('[') else '.') + y for y in the_args]}]
            else:
                items += [{'follow up': [self.instanceName + '[' + repr(index) + ']']}]
            if self.complete_attribute is not None and self.complete_attribute != 'complete':
                items += [dict(action='_da_define', arguments=dict(variables=[item.instanceName + '.' + self.complete_attribute]))]
            if ensure_complete:
                items += [dict(action='_da_dict_ensure_complete', arguments=dict(group=self.instanceName))]
            output += '<a href="' + docassemble.base.functions.url_action('_da_dict_edit', items=items) + '" role="button" class="btn btn-sm ' + docassemble.base.functions.server.button_class_prefix + 'secondary btn-darevisit"><i class="fas fa-pencil-alt"></i> ' + word('Edit') + '</a> '
        if use_delete and can_delete:
            if kwargs.get('confirm', False):
                areyousure = ' daremovebutton'
            else:
                areyousure = ''
            output += '<a href="' + docassemble.base.functions.url_action('_da_dict_remove', dict=self.instanceName, item=repr(index)) + '" role="button" class="btn btn-sm ' + docassemble.base.functions.server.button_class_prefix + 'danger btn-darevisit' + areyousure + '"><i class="fas fa-trash"></i> ' + word('Delete') + '</a>'
        if kwargs.get('edit_url_only', False):
            return docassemble.base.functions.url_action('_da_dict_edit', items=items)
        if kwargs.get('delete_url_only', False):
            return docassemble.base.functions.url_action('_da_dict_remove', dict=self.instanceName, item=repr(index))
        return output
    def add_action(self, label=None, message=None, url_only=False, icon='plus-circle', color='success', size='sm', block=None, classname=None):
        """Returns HTML for adding an item to a dict"""
        if color not in ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'):
            color = 'success'
        if size not in ('sm', 'md', 'lg'):
            size = 'sm'
        if size == 'md':
            size = ''
        else:
            size = " btn-" + size
        if block:
            block = ' btn-block'
        else:
            block = ''
        if isinstance(icon, str):
            icon = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', icon)
            if not re.search(r'^fa[a-z] fa-', icon):
                icon = 'fas fa-' + icon
            icon = '<i class="' + icon + '"></i> '
        else:
            icon = ''
        if classname is None:
            classname = ''
        else:
            classname = ' ' + str(classname)
        if message is not None:
            logmessage("add_action: note that the 'message' parameter has been renamed to 'label'.")
        if message is None and label is not None:
            message = label
        if message is None:
            if len(self.elements) > 0:
                message = word("Add another")
            else:
                message = word("Add an item")
        else:
            message = word(str(message))
        if url_only:
            return docassemble.base.functions.url_action('_da_dict_add', list=self.instanceName)
        return '<a href="' + docassemble.base.functions.url_action('_da_dict_add', dict=self.instanceName) + '" class="btn' + size + block + ' ' + docassemble.base.functions.server.button_class_prefix + color + classname + '">' + icon + str(message) + '</a>'
    def _new_elements(self):
        return dict()
    def hook_on_gather(self):
        pass
    def hook_after_gather(self):
        pass
    def hook_on_item_complete(self, item):
        pass
    def hook_on_remove(self, item):
        pass
    def __eq__(self, other):
        self._trigger_gather()
        return self.elements == other
    def __hash__(self):
        return hash((self.instanceName,))

class DAOrderedDict(DADict):
    """A base class for objects that behave like Python OrderedDicts."""
    def _new_elements(self):
        return OrderedDict()
    def _sorted_items(self):
        return self.items()
    def _sorted_elements_items(self):
        return self.elements.items()
    def _sorted_iteritems(self):
        return self.items()
    def _sorted_elements_iteritems(self):
        return self.elements.items()
    def _sorted_keys(self):
        return self.keys()
    def _sorted_elements_keys(self):
        return self.elements.keys()
    def _sorted_values(self):
        return self.elements.values()
    def _sorted_elements_values(self):
        return self.elements.values()

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
        return super().init(*pargs, **kwargs)
    def gathered_and_complete(self):
        """Ensures all items in the set are complete and then returns True."""
        if not hasattr(self, 'doing_gathered_and_complete'):
            self.doing_gathered_and_complete = True
            if hasattr(self, 'complete_attribute') and self.complete_attribute == 'complete':
                for item in self.elements:
                    if hasattr(item, self.complete_attribute):
                        delattr(item, self.complete_attribute)
            if hasattr(self, 'gathered'):
                del self.gathered
        if self.auto_gather:
            self.gather()
        else:
            self.hook_on_gather()
            self.gathered
        if hasattr(self, 'doing_gathered_and_complete'):
            del self.doing_gathered_and_complete
        self.hook_after_gather()
        return True
    def complete_elements(self, complete_attribute=None):
        """Returns a subset with the elements that are complete."""
        if complete_attribute is None and hasattr(self, 'complete_attribute'):
            complete_attribute = self.complete_attribute
        items = set()
        for item in self.elements:
            if item is None:
                continue
            if complete_attribute is not None:
                if not hasattr(item, complete_attribute):
                    continue
            else:
                try:
                    str(item)
                except:
                    continue
            items.add(item)
        return items
    def filter(self, *pargs, **kwargs):
        """Returns a filtered version of the set containing only items with particular values of attributes."""
        self._trigger_gather()
        new_elements = set()
        for item in self.elements:
            include = True
            for key, val in kwargs.items():
                if getattr(item, key) != val:
                    include = False
                    break
            if include:
                new_elements.add(item)
        if len(pargs):
            new_instance_name = pargs[0]
        else:
            new_instance_name = self.instanceName
        new_set = self.copy_shallow(new_instance_name)
        new_set.elements = new_elements
        new_list.gathered = True
        if len(new_list.elements) == 0:
            new_list.there_are_any = False
        return new_set
    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered
        return
    def reset_gathered(self, recursive=False, only_if_empty=False, mark_incomplete=False):
        """Indicates that there is more to be gathered"""
        #logmessage("reset_gathered: " + self.instanceName + ": del on there_is_another")
        if only_if_empty and len(self.elements) > 0:
            return
        if len(self.elements) == 0 and hasattr(self, 'there_are_any'):
            delattr(self, 'there_are_any')
        if hasattr(self, 'there_is_another'):
            delattr(self, 'there_is_another')
        if hasattr(self, 'there_is_one_other'):
            delattr(self, 'there_is_one_other')
        if hasattr(self, 'gathered'):
            delattr(self, 'gathered')
        if hasattr(self, 'new_object_type'):
            delattr(self, 'new_object_type')
        if mark_incomplete and self.complete_attribute is not None:
            for item in list(self.elements):
                if hasattr(item, self.complete_attribute):
                    delattr(item, self.complete_attribute)
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
        if elem in self.elements:
            self.hook_on_remove(elem)
        self.elements.remove(elem)
        if len(self.elements) == 0:
            self.there_are_any = False
    def discard(self, elem):
        """Removes an element from the set if it exists."""
        if elem in self.elements:
            self.hook_on_remove(elem)
        self.elements.discard(elem)
        if len(self.elements) == 0:
            self.there_are_any = False
    def pop(self):
        """Remove and return an arbitrary element from the set"""
        if len(self.elements) == 1:
            self.there_are_any = False
        return self.elements.pop()
    def add(self, *pargs):
        """Adds the arguments to the set, unpacking each argument if it is a
        group of some sort (i.e. it is iterable)."""
        something_added = False
        for parg in pargs:
            if isinstance(parg, (DAList, DASet, abc.Iterable)) and not isinstance(parg, str):
                for item in parg:
                    self.add(item)
                    something_added = True
            else:
                self.elements.add(parg)
                something_added = True
        if something_added:
            self.there_are_any = True
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
            output = noun_singular(the_noun)
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
    def gathering_started(self):
        """Returns True if the gathering process has started or the number of elements is non-zero."""
        if hasattr(self, 'gathered') or hasattr(self, 'there_are_any') or len(self.elements) > 0:
            return True
        return False
    def number_gathered(self, if_started=False):
        """Returns the number of elements in the list that have been gathered so far."""
        if if_started and not self.gathering_started():
            self._trigger_gather()
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
            if self.auto_gather and len(self.elements) == 0 and hasattr(self, 'there_are_any') and self.there_are_any:
                del self.gathered
            else:
                return True
        if not self.auto_gather:
            return self.gathered
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        for elem in sorted(self.elements):
            str(elem)
        if number is None and self.ask_number:
            if hasattr(self, 'there_are_any') and not self.there_are_any:
                number = 0
            else:
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
        while (number is not None and len(self.elements) < int(number)) or (minimum is not None and len(self.elements) < int(minimum)) or (self.ask_number is False and minimum != 0 and (self.there_is_another or (hasattr(self, 'there_is_one_other') and self.there_is_one_other))):
            self.add(self.new_item)
            del self.new_item
            for elem in sorted(self.elements):
                str(elem)
            if hasattr(self, 'there_is_one_other'):
                del self.there_is_one_other
            elif hasattr(self, 'there_is_another'):
                #logmessage("gather: " + self.instanceName + ": del on there_is_another")
                del self.there_is_another
        self.hook_on_gather()
        if self.auto_gather:
            self.gathered = True
            self.revisit = True
        docassemble.base.functions.set_gathering_mode(False, self.instanceName)
        self.hook_after_gather()
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
        if hasattr(self, 'there_are_any') and not self.there_are_any:
            return 0
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
    def __hash__(self):
        self._trigger_gather()
        return self.elements.__hash__()
    def __add__(self, other):
        if isinstance(other, DAEmpty):
            return self
        if isinstance(other, DASet):
            return self.elements + other.elements
        return self.elements + other
    def __sub__(self, other):
        if isinstance(other, DASet):
            return self.elements - other.elements
        return self.elements - other
    def __str__(self):
        self._trigger_gather()
        return str(self.comma_and_list())
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
    def hook_on_gather(self):
        pass
    def hook_after_gather(self):
        pass
    def hook_on_item_complete(self, item):
        pass
    def hook_on_remove(self, item):
        pass
    def __eq__(self, other):
        self._trigger_gather()
        return self.elements == other
    def __hash__(self):
        return hash((self.instanceName,))

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
        if 'alt_text' in kwargs:
            self.alt_text = kwargs['alt_text']
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
    def convert_to(self, output_extension):
        self.retrieve()
        if hasattr(self, 'extension'):
            input_extension = self.extension
        elif hasattr(self, 'filename'):
            input_extension, input_mimetype = server.get_ext_and_mimetype(self.filename)
        else:
            raise Exception("DAFile.convert: could not identify file type")
        output_extension = output_extension.strip().lower()
        if output_extension == input_extension:
            return
        if hasattr(self, 'filename'):
            output_filename = re.sub(r'\.[^\.]+$', '.' + output_extension, self.filename)
        else:
            output_filename = 'file.' + output_extension
        input_path = self.path()
        input_number = self.number
        del self.number
        self.ok = False
        if hasattr(self, 'mimetype'):
            del self.mimetype
        self.initialize(extension=output_extension, filename=output_filename)
        if input_extension in ("docx", "doc", "odt", "rtf") and output_extension in ("docx", "doc", "odt", "rtf"):
            import docassemble.base.pandoc
            docassemble.base.pandoc.convert_file(input_path, self.path(), input_extension, output_extension)
        elif input_extension in ("docx", "doc", "odt", "rtf") and output_extension == 'md':
            import docassemble.base.pandoc
            result = docassemble.base.pandoc.word_to_markdown(input_path, input_extension)
            if result is None:
                raise DAError("Could not convert file")
            shutil.copyfile(result.name, self.path())
        elif input_extension in ("png", "jpg", "tif") and output_extension in ("png", "jpg", "tif"):
            the_image = Image.open(input_path)
            if input_extension == 'png':
                rgb_image = the_image.convert('RGB')
                rgb_image.save(self.path())
            else:
                the_image.save(self.path())
        else:
            raise Exception("DAFile.convert: could not identify file type")
        server.SavedFile(input_number).delete
        self.commit()
        self.retrieve()
    def set_alt_text(self, alt_text):
        """Sets the alt text for the file."""
        self.alt_text = alt_text
    def get_alt_text(self):
        """Returns the alt text for the file.  If no alt text is defined, None is returned."""
        if hasattr(self, 'alt_text'):
            return str(self.alt_text)
        return None
    def set_mimetype(self, mimetype):
        """Sets the MIME type of the file"""
        self.mimetype = mimetype
        if mimetype == 'image/jpeg':
            self.extension = 'jpg'
        else:
            self.extension = re.sub(r'^\.', '', mimetypes.guess_extension(mimetype))
    def __str__(self):
        return str(self.show())
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
        if 'alt_text' in kwargs:
            self.alt_text = kwargs['alt_text']
        if 'number' in kwargs and kwargs['number'] is not None:
            self.number = kwargs['number']
            self.ok = True
        if not hasattr(self, 'filename'):
            if hasattr(self, 'extension'):
                self.filename = kwargs.get('filename', 'file.' + self.extension)
            else:
                self.filename = kwargs.get('filename', 'file.txt')
        docassemble.base.filter.ensure_valid_filename(self.filename)
        if not hasattr(self, 'number'):
            yaml_filename = None
            uid = None
            if hasattr(docassemble.base.functions.this_thread, 'current_info'):
                yaml_filename = docassemble.base.functions.this_thread.current_info.get('yaml_filename', None)
            uid = docassemble.base.functions.get_uid()
            self.number = server.get_new_file_number(uid, self.filename, yaml_file_name=yaml_filename)
            self.ok = True
            self.extension, self.mimetype = server.get_ext_and_mimetype(self.filename)
        self.retrieve()
        the_path = self.path()
        if not (os.path.isfile(the_path) or os.path.islink(the_path)):
            sf = server.SavedFile(self.number, extension=self.extension, fix=True)
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
        if 'path' not in self.file_info:
            raise Exception("Could not retrieve file")
        self.extension = self.file_info.get('extension', None)
        self.mimetype = self.file_info.get('mimetype', None)
        self.persistent = self.file_info['persistent']
        self.private = self.file_info['private']
    def size_in_bytes(self):
        """Returns the number of bytes in the file."""
        self.retrieve()
        the_path = self.path()
        return os.path.getsize(the_path)
    def slurp(self, auto_decode=True):
        """Returns the contents of the file."""
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File " + str(the_path) + " does not exist yet.")
        if auto_decode and hasattr(self, 'mimetype') and (self.mimetype.startswith('text') or self.mimetype in ('application/json', 'application/javascript')):
            with open(the_path, 'rU', encoding='utf-8') as f:
                return(f.read())
        else:
            with open(the_path, 'rb') as f:
                return(f.read())
    def readlines(self):
        """Returns the contents of the file."""
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File does not exist yet.")
        with open(the_path, 'rU', encoding='utf-8') as f:
            return(f.readlines())
    def write(self, content, binary=False):
        """Writes the given content to the file, replacing existing contents."""
        self.retrieve()
        the_path = self.file_info['path']
        if binary:
            with open(the_path, 'wb') as f:
                f.write(content)
        else:
            with open(the_path, 'w', encoding='utf-8') as f:
                f.write(content)
        self.retrieve()
    def copy_into(self, other_file):
        """Makes the contents of the file the same as those of another file."""
        if isinstance(other_file, DAFile) or isinstance(other_file, DAFileList) or isinstance(other_file, DAFileCollection) or isinstance(other_file, DAStaticFile):
            filepath = other_file.path()
        else:
            filepath = other_file
        self.retrieve()
        shutil.copyfile(filepath, self.file_info['path'])
        self.retrieve()
    def get_docx_variables(self):
        """Returns a list of variables used by the Jinja2 templating of a DOCX template file."""
        import docassemble.base.parse
        return docassemble.base.parse.get_docx_variables(self.path())
    def get_pdf_fields(self):
        """Returns a list of fields that exist in the PDF document"""
        results = list()
        import docassemble.base.pdftk
        for item in docassemble.base.pdftk.read_fields(self.path()):
            the_type = re.sub(r'[^/A-Za-z]', '', str(item[4]))
            if the_type == 'None':
                the_type = None
            result = (item[0], '' if item[1] == 'something' else item[1], item[2], item[3], the_type, item[5])
            results.append(result)
        return results
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
        c.setopt(pycurl.USERAGENT, docassemble.base.functions.server.daconfig.get('user agent', 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36'))
        c.setopt(pycurl.COOKIEFILE, cookiefile.name)
        c.perform()
        c.close()
        self.retrieve()
    def is_encrypted(self):
        """Returns True if the file is a PDF file and it is encrypted, otherwise returns False."""
        if not hasattr(self, 'file_info'):
            self.retrieve()
        return self.file_info.get('encrypted', False)
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
            if wait and server.wait_for_task(getattr(self, '_task' + prefix)):
                self.retrieve()
                the_path = self.file_info['path'] + prefix + '-' + str(int(page)) + '.png'
                if os.path.isfile(the_path):
                    return the_path
        return None
    def cloud_path(self, filename=None):
        """Returns the path with which the file can be accessed using S3 or Azure Blob Storage, or None if cloud storage is not enabled."""
        if not hasattr(self, 'number'):
            raise Exception("Cannot get the cloud path of file without a file number.")
        return server.SavedFile(self.number, fix=False).cloud_path(filename)
    def path(self):
        """Returns a path and filename at which the file can be accessed."""
        #logmessage("path")
        if not hasattr(self, 'number'):
            raise Exception("Cannot get path of file without a file number.")
        #if not hasattr(self, 'file_info'):
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
            sf = server.SavedFile(self.number, fix=True)
            sf.finalize()
    def show(self, width=None, wait=True, alt_text=None):
        """Inserts markup that displays the file as an image.  Takes
        optional keyword arguments width and alt_text.

        """
        if not self.ok:
            return('')
        if hasattr(self, 'number') and hasattr(self, 'extension') and self.extension == 'pdf' and wait:
            self.page_path(1, 'page')
        if self.mimetype == 'text/markdown':
            the_template = DATemplate(content=self.slurp())
            return str(the_template)
        elif self.mimetype == 'text/plain':
            the_content = self.slurp()
            return the_content
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self)
            else:
                if self.mimetype in ('application/pdf', 'application/rtf', 'application/vnd.oasis.opendocument.text', 'application/msword'):
                    return self._pdf_pages(width)
                return docassemble.base.file_docx.image_for_docx(self.number, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width)
        else:
            if width is not None:
                the_width = str(width)
            else:
                the_width = 'None'
            if alt_text is None:
                alt_text = self.get_alt_text()
            if alt_text is not None:
                the_alt_text = re.sub(r'\]', '', str(alt_text))
            else:
                the_alt_text = 'None'
            return('[FILE ' + str(self.number) + ', ' + the_width + ', ' + the_alt_text + ']')
    def _pdf_pages(self, width):
        file_info = server.file_finder(self.number, question=docassemble.base.functions.this_thread.current_question)
        if 'path' not in file_info:
            return ''
        return docassemble.base.file_docx.pdf_pages(file_info, width)
    def url_for(self, **kwargs):
        """Returns a URL to the file."""
        if kwargs.get('temporary', False) and 'external' not in kwargs:
            kwargs['_external'] = True
        if kwargs.get('external', False):
            kwargs['_external'] = True
            del kwargs['external']
        if kwargs.get('attachment', False):
            kwargs['_attachment'] = True
            del kwargs['attachment']
        return server.url_finder(self, **kwargs)
    def set_attributes(self, **kwargs):
        """Sets attributes of the file stored on the server.  Takes optional keyword arguments private and persistent, which must be boolean values."""
        if 'private' in kwargs and kwargs['private'] in [True, False]:
            self.private = kwargs['private']
        if 'persistent' in kwargs and kwargs['persistent'] in [True, False]:
            self.persistent = kwargs['persistent']
        return server.file_set_attributes(self.number, **kwargs)
    def user_access(self, *pargs, **kwargs):
        """Allows or disallows access to the file for a given user."""
        allow_user_id = list()
        allow_email = list()
        disallow_user_id = list()
        disallow_email = list()
        disallow_all = False
        for item in pargs:
            if isinstance(item, str):
                m = re.search('^[0-9]+$', item)
                if m:
                    item = int(item)
            if isinstance(item, int):
                allow_user_id.append(item)
            elif isinstance(item, str):
                allow_email.append(item)
        if 'disallow' in kwargs:
            disallow = kwargs['disallow']
            if disallow == 'all':
                allow_user_id = list()
                allow_email = list()
                disallow_all = True
            else:
                if isinstance(disallow, (int, str)):
                    disallow = [disallow]
                if isinstance(disallow, list) or isinstance(disallow, DAList):
                    for item in disallow:
                        if isinstance(item, str):
                            m = re.search('^[0-9]+$', item)
                            if m:
                                item = int(item)
                        if isinstance(item, int):
                            disallow_user_id.append(item)
                        elif isinstance(item, str):
                            disallow_email.append(item)
        return server.file_user_access(self.number, allow_user_id=allow_user_id, allow_email=allow_email, disallow_user_id=disallow_user_id, disallow_email=disallow_email, disallow_all=disallow_all)
    def privilege_access(self, *pargs, **kwargs):
        """Allows or disallows access to the file for a given privilege."""
        allow = list()
        disallow = list()
        disallow_all = False
        for item in pargs:
            if isinstance(item, str):
                allow.append(item)
        if 'disallow' in kwargs:
            disallow_arg = kwargs['disallow']
            if disallow_arg == 'all':
                allow = list()
                disallow_all = True
            else:
                if isinstance(disallow_arg, str):
                    disallow_arg = [disallow_arg]
                if isinstance(disallow_arg, list) or isinstance(disallow_arg, DAList):
                    for item in disallow_arg:
                        if isinstance(item, str):
                            disallow.append(item)
        return server.file_privilege_access(self.number, allow=allow, disallow=disallow, disallow_all=disallow_all)

class DAFileCollection(DAObject):
    """Used internally by docassemble to refer to a collection of DAFile
    objects, usually representing the same document in different
    formats.  Attributes represent file types.  The attachments
    feature generates objects of this type.

    """
    def init(self, *pargs, **kwargs):
        self.info = dict()
        super().init(*pargs, **kwargs)
    def _extension_list(self):
        if hasattr(self, 'info') and 'formats' in self.info:
            return self.info['formats']
        return ['pdf', 'docx', 'rtf']
    def set_alt_text(self, alt_text):
        """Sets the alt text of each of the files in the collection."""
        for ext in self._extension_list():
            if hasattr(self, ext):
                getattr(self, ext).alt_text = alt_text
    def get_alt_text(self):
        """Returns the alt text for the first file in the collection.  If no
        alt text is defined, None is returned.

        """
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext).get_alt_text()
        return None
    def is_encrypted(self):
        """Returns True if there is a PDF file and it is encrypted, otherwise returns False."""
        if hasattr(self, 'pdf'):
            return self.pdf.is_encrypted()
        return False
    def num_pages(self):
        """If there is a PDF file, returns the number of pages in the file, otherwise returns 1."""
        if hasattr(self, 'pdf'):
            return self.pdf.num_pages()
        return 1
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
    def get_docx_variables(self):
        """Returns a list of variables used by the Jinja2 templating of a DOCX template file."""
        return the_file.docx.get_docx_fields()
    def get_pdf_fields(self):
        """Returns a list of fields that exist in the PDF document"""
        return the_file.pdf.get_pdf_fields()
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
    def user_access(self, *pargs, **kwargs):
        """Allows or disallows access to the file(s) for a given user."""
        for ext in self._extension_list():
            if hasattr(self, ext):
                if getattr(self, ext).ok:
                    getattr(self, ext).user_access(*pargs, **kwargs)
    def privilege_access(self, *pargs, **kwargs):
        """Allows or disallows access to the file(s) for a given privilege."""
        for ext in self._extension_list():
            if hasattr(self, ext):
                if getattr(self, ext).ok:
                    getattr(self, ext).privilege_access(*pargs, **kwargs)
    def show(self, **kwargs):
        """Inserts markup that displays each part of the file collection as an
        image or link.
        """
        the_files = [getattr(self, ext).show(**kwargs) for ext in self._extension_list() if hasattr(self, ext)]
        for the_file in the_files:
            if isinstance(the_file, InlineImage) or isinstance(the_file, Subdoc):
                return the_file
        return ' '.join(the_files)
    def __str__(self):
        return str(self._first_file())

class DAFileList(DAList):
    """Used internally by docassemble to refer to a list of files, such as
    a list of files uploaded to a single variable.

    """
    def __str__(self):
        return str(self.show())
    def set_alt_text(self, alt_text):
        """Sets the alt text of each of the files in the list."""
        for item in self:
            item.alt_text = alt_text
    def get_alt_text(self):
        """Returns the alt text for the first file in the list.  If no alt
        text is defined, None is returned.

        """
        if len(self.elements) == 0:
            return None
        return self.elements[0].get_alt_text()
    def num_pages(self):
        """Returns the total number of pages in the PDF documents, or one page per non-PDF file."""
        result = 0;
        for element in sorted(self.elements):
            if element.ok:
                result += element.num_pages()
        return result
    def is_encrypted(self):
        """Returns True if the first file is a PDF file and it is encrypted, otherwise returns False."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].is_encrypted()
    def convert_to(self, output_extension):
        for element in self.elements:
            element.convert_to(output_extension)
    def size_in_bytes(self):
        """Returns the number of bytes in the first file."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].size_in_bytes()
    def slurp(self, auto_decode=True):
        """Returns the contents of the first file."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].slurp()
    def show(self, width=None, alt_text=None):
        """Inserts markup that displays each element in the list as an image.
        Takes optional keyword arguments width and alt_text.

        """
        output = ''
        for element in sorted(self.elements):
            if element.ok:
                new_image = element.show(width=width, alt_text=alt_text)
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
    def get_docx_variables(self):
        """Returns a list of variables used by the Jinja2 templating of a DOCX template file."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].get_docx_variables()
    def get_pdf_fields(self):
        """Returns a list of fields that exist in the PDF document"""
        if len(self.elements) == 0:
            return None
        return self.elements[0].get_pdf_fields()
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
    def user_access(self, *pargs, **kwargs):
        """Allows or disallows access to the file(s) for a given user."""
        for element in sorted(self.elements):
            if element.ok:
                element.user_access(*pargs, **kwargs)
    def privilege_access(self, *pargs, **kwargs):
        """Allows or disallows access to the file(s) for a given privilege."""
        for element in sorted(self.elements):
            if element.ok:
                element.privilege_access(*pargs, **kwargs)

class DAStaticFile(DAObject):
    def init(self, *pargs, **kwargs):
        if 'filename' in kwargs and 'mimetype' not in kwargs and 'extension' not in kwargs:
            self.extension, self.mimetype = server.get_ext_and_mimetype(kwargs['filename'])
        return super().init(*pargs, **kwargs)
    def get_alt_text(self):
        """Returns the alt text for the file.  If no alt text is defined, None
        is returned.

        """
        if hasattr(self, 'alt_text'):
            return str(self.alt_text)
        return None
    def set_alt_text(self, alt_text):
        """Sets the alt text for the file."""
        self.alt_text = alt_text
    def show(self, width=None, alt_text=None):
        """Inserts markup that displays the file.  Takes optional keyword
        arguments width and alt_text.

        """
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self)
            else:
                if self.mimetype in ('application/pdf', 'application/rtf', 'application/vnd.oasis.opendocument.text', 'application/msword'):
                    return self._pdf_pages(width)
                the_text = docassemble.base.file_docx.image_for_docx(docassemble.base.functions.DALocalFile(self.path()), docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width)
                return the_text
        else:
            if width is not None:
                the_width = str(width)
            else:
                the_width = 'None'
            if alt_text is None:
                alt_text = self.get_alt_text()
            if alt_text is not None:
                the_alt_text = the_alt_text = re.sub(r'\]', '', str(alt_text))
            else:
                the_alt_text = 'None'
            return('[FILE ' + str(self.filename) + ', ' + the_width + ', ' + the_alt_text + ']')
    def _pdf_pages(self, width):
        file_info = dict()
        pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
        file_info['fullpath'] = pdf_file.name
        file_info['extension'] = 'pdf'
        file_info['path'] = os.path.splitext(pdf_file.name)[0]
        shutil.copyfile(self.path(), pdf_file.name)
        return docassemble.base.file_docx.pdf_pages(file_info, width)
    def is_encrypted(self):
        """Returns True if the file is a PDF file and it is encrypted, otherwise returns False."""
        file_info = server.file_finder(self.filename)
        return the_file.get('encrypted', False)
    def size_in_bytes(self):
        """Returns the number of bytes in the file."""
        the_path = self.path()
        return os.path.getsize(the_path)
    def slurp(self, auto_decode=True):
        """Returns the contents of the file."""
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File " + str(the_path) + " does not exist.")
        if auto_decode and hasattr(self, 'mimetype') and (self.mimetype.startswith('text') or self.mimetype in ('application/json', 'application/javascript')):
            with open(the_path, 'rU', encoding='utf-8') as f:
                return(f.read())
        else:
            with open(the_path, 'rU') as f:
                return(f.read())
    def path(self):
        """Returns a path and filename at which the file can be accessed.

        """
        file_info = server.file_finder(self.filename)
        return file_info.get('fullpath', None)
    def get_docx_variables(self):
        """Returns a list of variables used by the Jinja2 templating of a DOCX template file."""
        import docassemble.base.parse
        return docassemble.base.parse.get_docx_variables(self.path())
    def get_pdf_fields(self):
        """Returns a list of fields that exist in the PDF document"""
        results = list()
        import docassemble.base.pdftk
        for item in docassemble.base.pdftk.read_fields(self.path()):
            the_type = re.sub(r'[^/A-Za-z]', '', str(item[4]))
            if the_type == 'None':
                the_type = None
            result = (item[0], '' if item[1] == 'something' else item[1], item[2], item[3], the_type, item[5])
            results.append(result)
        return results
    def url_for(self, **kwargs):
        """Returns a URL to the static file."""
        the_args = dict()
        for key, val in kwargs.items():
            the_args[key] = val
        if 'external' in kwargs:
            the_args['_external'] = kwargs['external']
            del the_args['external']
        if 'attachment' in kwargs:
            the_args['_attachment'] = kwargs['attachment']
            del the_args['attachment']
        the_args['_question'] = docassemble.base.functions.this_thread.current_question
        return server.url_finder(self.filename, **the_args)
    def __str__(self):
        return str(self.show())

class DAEmailRecipientList(DAList):
    """Represents a list of DAEmailRecipient objects."""
    def init(self, *pargs, **kwargs):
        #logmessage("DAEmailRecipientList: pargs is " + str(pargs) + " and kwargs is " + str(kwargs))
        self.object_type = DAEmailRecipient
        super().init(**kwargs)
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
        return super().init(*pargs, **kwargs)
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
            name = str(self.name)
        else:
            name = ''
        if hasattr(self, 'empty') and self.empty:
            return ''
        if self.address == '' and name == '':
            return 'EMAIL NOT DEFINED'
        if self.address == '' and name != '':
            return name
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return str(self.address)
        if name == '' and self.address != '':
            return '[' + str(self.address) + '](mailto:' + str(self.address) + ')'
        return '[' + str(name) + '](mailto:' + str(self.address) + ')'

class DAEmail(DAObject):
    """An object type used to represent an e-mail that has been received
    through the e-mail receiving feature.

    """
    def __str__(self):
        return('This is an e-mail')

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
        return str(self)
    def __str__(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            #return str(self.content)
            #return str(docassemble.base.filter.docx_template_filter(self.content))
            return str(docassemble.base.file_docx.markdown_to_docx(self.content, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc('docx_template', None)))
        return(str(self.content))

def table_safe(text):
    text = str(text)
    text = re.sub(r'[\n\r\|]', ' ', text)
    if re.match(r'[\-:]+', text):
        text = '  ' + text + '  '
    return text

def export_safe(text):
    if isinstance(text, DAObject):
        text = str(text)
    if isinstance(text, DAEmpty):
        text = None
    if isinstance(text, datetime.datetime):
        text = text.replace(tzinfo=None)
    return text

def table_safe_eval(x, user_dict_copy, table_info):
    try:
        return table_safe(eval(x, user_dict_copy))
    except:
        return table_safe(word(table_info.not_available_label))

def text_of_table(table_info, orig_user_dict, temp_vars, editable=True):
    table_content = "\n"
    user_dict_copy = copy.copy(orig_user_dict)
    user_dict_copy.update(temp_vars)
    #logmessage("i is " + str(user_dict_copy['i']))
    header_output = [table_safe(x.text(user_dict_copy)) for x in table_info.header]
    if table_info.is_editable and not editable:
        header_output.pop()
    the_iterable = eval(table_info.row, user_dict_copy)
    if not isinstance(the_iterable, (list, dict, DAList, DADict)):
        raise DAError("Error in processing table " + table_info.saveas + ": row value is not iterable")
    if hasattr(the_iterable, 'instanceName') and hasattr(the_iterable, 'elements') and isinstance(the_iterable.elements, (list, dict)):
        if not table_info.require_gathered:
            the_iterable = the_iterable.complete_elements()
        elif table_info.show_incomplete and the_iterable.gathering_started():
            the_iterable = the_iterable.elements
        elif docassemble.base.functions.get_gathering_mode(the_iterable.instanceName):
            the_iterable = the_iterable.complete_elements()
    contents = list()
    if hasattr(the_iterable, 'items') and callable(the_iterable.items):
        if isinstance(the_iterable, (OrderedDict, DAOrderedDict)):
            for key in the_iterable:
                user_dict_copy['row_item'] = the_iterable[key]
                user_dict_copy['row_index'] = key
                if table_info.show_incomplete:
                    contents.append([table_safe_eval(x, user_dict_copy, table_info) for x in table_info.column])
                else:
                    contents.append([table_safe(eval(x, user_dict_copy)) for x in table_info.column])
        else:
            for key in sorted(the_iterable):
                user_dict_copy['row_item'] = the_iterable[key]
                user_dict_copy['row_index'] = key
                if table_info.show_incomplete:
                    contents.append([table_safe_eval(x, user_dict_copy, table_info) for x in table_info.column])
                else:
                    contents.append([table_safe(eval(x, user_dict_copy)) for x in table_info.column])
    else:
        indexno = 0
        for item in the_iterable:
            user_dict_copy['row_item'] = item
            user_dict_copy['row_index'] = indexno
            if table_info.show_incomplete:
                contents.append([table_safe_eval(x, user_dict_copy, table_info) for x in table_info.column])
            else:
                contents.append([table_safe(eval(x, user_dict_copy)) for x in table_info.column])
            indexno += 1
    if table_info.is_editable and not editable:
        for cols in contents:
            cols.pop()
    user_dict_copy.pop('row_item', None)
    user_dict_copy.pop('row_index', None)
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
    table_content += table_info.indent + '|' + "|".join(header_output) + "|\n"
    table_content += table_info.indent + '|' + "|".join(['-' * x for x in max_chars_to_use]) + "|\n"
    for content_line in contents:
        table_content += table_info.indent + '|' + "|".join(content_line) + "|\n"
    if len(contents) == 0 and table_info.empty_message is not True:
        if table_info.empty_message in (False, None):
            table_content = "\n"
        else:
            table_content = table_info.empty_message.text(user_dict_copy) + "\n"
    table_content += "\n"
    return table_content

class DALazyTemplate(DAObject):
    """The class used for Markdown templates.  A template block saves to
    an object of this type.  The two attributes are "subject" and
    "content." """
    def __getstate__(self):
        if hasattr(self, 'instanceName'):
            return dict(instanceName=self.instanceName)
        else:
            return dict()
    def subject_as_html(self, **kwargs):
        the_args = dict()
        for key, val in kwargs.items():
            the_args[key] = val
        the_args['status'] = docassemble.base.functions.this_thread.interview_status
        the_args['question'] = docassemble.base.functions.this_thread.current_question
        return docassemble.base.filter.markdown_to_html(self.subject, **the_args)
    def content_as_html(self, **kwargs):
        the_args = dict()
        for key, val in kwargs.items():
            the_args[key] = val
        the_args['status'] = docassemble.base.functions.this_thread.interview_status
        the_args['question'] = docassemble.base.functions.this_thread.current_question
        return docassemble.base.filter.markdown_to_html(self.content, **the_args)
    @property
    def subject(self):
        if not hasattr(self, 'source_subject'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        return self.source_subject.text(user_dict_copy).rstrip()
    @property
    def content(self):
        if not hasattr(self, 'source_content'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        return self.source_content.text(user_dict_copy).rstrip()
    @property
    def decorations(self):
        if not hasattr(self, 'source_decorations'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        return [dec.text(user_dict_copy).rstrip for dec in self.source_decorations]
    def show(self, **kwargs):
        """Displays the contents of the template."""
        if not hasattr(self, 'source_content'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        user_dict_copy.update(kwargs)
        content = self.source_content.text(user_dict_copy).rstrip()
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            content = re.sub(r'\\_', r'\\\\_', content)
            return str(docassemble.base.file_docx.markdown_to_docx(content, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None)))
        return content
    def __str__(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            content = self.content
            content = re.sub(r'\\_', r'\\\\_', content)
            #return str(self.content)
            #return str(docassemble.base.filter.docx_template_filter(self.content))
            return str(docassemble.base.file_docx.markdown_to_docx(content, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None)))
        return(str(self.content))

class DALazyTableTemplate(DALazyTemplate):
    """The class used for tables."""
    def show(self, **kwargs):
        """Displays the contents of the table."""
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return word("ERROR: you cannot insert a table into a .docx document")
        if kwargs.get('editable', True):
            return str(self.content)
        if not hasattr(self, 'table_info'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        return text_of_table(self.table_info, self.userdict, self.tempvars, editable=False)
    @property
    def content(self):
        if not hasattr(self, 'table_info'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        return text_of_table(self.table_info, self.userdict, self.tempvars)
    def export(self, filename=None, file_format=None, title=None, freeze_panes=True):
        if file_format is None:
            if filename is not None:
                base_filename, file_format = os.path.splitext(filename)
                file_format = re.sub(r'^\.', '', file_format)
            else:
                file_format = 'xlsx'
        if file_format not in ('json', 'xlsx', 'csv'):
            raise Exception("export: unsupported file format")
        header_output, contents = self.header_and_contents()
        df = pandas.DataFrame.from_records(contents, columns=header_output)
        outfile = DAFile()
        outfile.set_random_instance_name()
        if filename is not None:
            outfile.initialize(filename=filename, extension=file_format)
        else:
            outfile.initialize(extension=file_format)
        if file_format == 'xlsx':
            if freeze_panes:
                freeze_panes = (1, 0)
            else:
                freeze_panes = None
            writer = pandas.ExcelWriter(outfile.path(),
                                        engine='xlsxwriter',
                                        options={'remove_timezone': True})
            df.to_excel(writer, sheet_name=title, index=False, freeze_panes=freeze_panes)
            writer.save()
        elif file_format == 'csv':
            df.to_csv(outfile.path(), index=False)
        elif file_format == 'json':
            df.to_json(outfile.path(), orient='records')
        outfile.commit()
        outfile.retrieve()
        return outfile
    def as_df(self):
        """Returns the table as a pandas data frame"""
        header_output, contents = self.header_and_contents()
        return pandas.DataFrame.from_records(contents, columns=header_output)
    def export_safe_eval(self, x, user_dict_copy):
        try:
            return table_safe(eval(x, user_dict_copy))
        except:
            return table_safe(word(self.table_info.not_available_label))
    def header_and_contents(self):
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        header_output = [export_safe(x.text(user_dict_copy)) for x in self.table_info.header]
        if self.table_info.is_editable:
            header_output.pop()
        the_iterable = eval(self.table_info.row, user_dict_copy)
        if not isinstance(the_iterable, (list, dict, DAList, DADict)):
            raise DAError("Error in processing table " + self.table_info.saveas + ": row value is not iterable")
        if hasattr(the_iterable, 'instanceName') and hasattr(the_iterable, 'elements') and isinstance(the_iterable.elements, (list, dict)):
            if not self.table_info.require_gathered:
                the_iterable = the_iterable.complete_elements()
            elif self.table_info.show_incomplete and the_iterable.gathering_started():
                the_iterable = the_iterable.elements
            elif docassemble.base.functions.get_gathering_mode(the_iterable.instanceName):
                the_iterable = the_iterable.complete_elements()
        contents = list()
        if hasattr(the_iterable, 'items') and callable(the_iterable.items):
            for key in sorted(the_iterable):
                user_dict_copy['row_item'] = the_iterable[key]
                user_dict_copy['row_index'] = key
                if self.table_info.show_incomplete:
                    contents.append([self.export_safe_eval(x, user_dict_copy) for x in self.table_info.column])
                else:
                    contents.append([export_safe(eval(x, user_dict_copy)) for x in self.table_info.column])
        else:
            indexno = 0
            for item in the_iterable:
                user_dict_copy['row_item'] = item
                user_dict_copy['row_index'] = indexno
                if self.table_info.show_incomplete:
                    contents.append([export_safe(eval(x, user_dict_copy)) for x in self.table_info.column])
                else:
                    contents.append([self.export_safe_eval(x, user_dict_copy) for x in self.table_info.column])
                indexno += 1
        if self.table_info.is_editable:
            for cols in contents:
                cols.pop()
        user_dict_copy.pop('row_item', None)
        user_dict_copy.pop('row_index', None)
        return header_output, contents

def selections(*pargs, **kwargs):
    """Packs a list of objects in the appropriate format for including
    as code in a multiple-choice field."""
    if 'object_labeler' in kwargs:
        object_labeler = lambda x: str(kwargs['object_labeler'](x))
    else:
        object_labeler = str
    if 'help_generator' in kwargs:
        help_generator = lambda x: str(kwargs['help_generator'](x))
    else:
        help_generator = None
    if 'image_generator' in kwargs:
        image_generator = lambda x: str(kwargs['image_generator'](x))
    else:
        image_generator = None
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
                output_dict = {myb64quote(subarg.instanceName): object_labeler(subarg), 'default': default_value}
                if help_generator is not None:
                    the_help = help_generator(subarg)
                    if the_help is not None:
                        output_dict['help'] = the_help
                if image_generator is not None:
                    the_image = image_generator(subarg)
                    if the_image is not None:
                        output_dict['image'] = the_image
                output.append(output_dict)
                seen.add(subarg)
    return output

def myb64quote(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode())

def setify(item, output=set()):
    if isinstance(item, DAObject) and hasattr(item, 'elements'):
        setify(item.elements, output)
    elif isinstance(item, abc.Iterable) and not isinstance(item, str):
        for subitem in item:
            setify(subitem, output)
    else:
        output.add(item)
    return output

def objects_from_file(file_ref, recursive=True, gathered=True, name=None, use_objects=False, package=None):
    """A utility function for initializing a group of objects from a YAML file written in a certain format."""
    #from docassemble.base.core import DAObject, DAList, DADict, DASet
    if isinstance(file_ref, DAFileCollection):
        file_ref = file_ref._first_file()
    if isinstance(file_ref, DAFileList) and len(file_ref.elements):
        file_ref = file_ref.elements[0]
    if file_ref is None:
        raise Exception("objects_from_file: no file referenced")
    if isinstance(file_ref, DAFile):
        file_ref = file_ref.number
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
    if package is None and docassemble.base.functions.this_thread.current_question is not None:
        package = docassemble.base.functions.this_thread.current_question.package
    file_info = server.file_finder(file_ref, folder='sources', package=package)
    if file_info is None or 'path' not in file_info:
        raise SystemError('objects_from_file: file reference ' + str(file_ref) + ' not found')
    if thename is None:
        objects = DAList()
    else:
        objects = DAList(thename)
    objects.gathered = True
    objects.revisit = True
    is_singular = True
    with open(file_info['fullpath'], 'rU', encoding='utf-8') as fp:
        if 'mimetype' in file_info and file_info['mimetype'] == 'application/json':
            document = json.load(fp)
            new_objects = recurse_obj(document, recursive=recursive, use_objects=use_objects)
            if type(new_objects) is list:
                is_singular = False
                for obj in new_objects:
                    objects.append(obj)
            else:
                objects.append(new_objects)
        else:
            for document in yaml.load_all(fp, Loader=yaml.FullLoader):
                new_objects = recurse_obj(document, recursive=recursive, use_objects=use_objects)
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

def recurse_obj(the_object, recursive=True, use_objects=False):
    constructor = None
    if isinstance(the_object, (str, bool, int, float)):
        return the_object
    if isinstance(the_object, list):
        if recursive:
            if use_objects:
                return_object = DAList('return_object', elements=[recurse_obj(x, use_objects=use_objects) for x in the_object])
                return_object.set_random_instance_name()
                return return_object
            return [recurse_obj(x, use_objects=use_objects) for x in the_object]
        else:
            if use_objects:
                return_object = DAList('return_object', elements=the_object)
                return_object.set_random_instance_name()
                return return_object
            return the_object
    if type(the_object) is set:
        if recursive:
            new_set = set()
            for sub_object in the_object:
                new_set.add(recurse_obj(sub_object, recursive=recursive, use_objects=use_objects))
            if use_objects:
                return_object = DASet('return_object', elements=new_set)
                return_object.set_random_instance_name()
                return return_object
            return new_set
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
                    new_module = __import__(module_name, globals(), locals(), [the_object['object']], 0)
                    constructor = getattr(new_module, the_object['object'], None)
            if not constructor:
                raise SystemError('recurse_obj: found an object for which the object declaration, ' + str(the_object['object']) + ' could not be found')
            if 'items' in the_object:
                objects = list()
                for item in the_object['items']:
                    if type(item) is not dict:
                        raise SystemError('recurse_obj: found an item, ' + str(item) + ' that was not expressed as a dictionary')
                    if recursive:
                        transformed_item = recurse_obj(item, recursive=True, use_objects=use_objects)
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
                    transformed_item = recurse_obj(item, recursive=True, use_objects=use_objects)
                else:
                    transformed_item = item
                #new_obj = constructor(**transformed_item)
                #if isinstance(new_obj, DAList) or isinstance(new_obj, DADict) or isinstance(new_obj, DASet):
                #    new_obj.gathered = True
                return constructor(**transformed_item)
        else:
            if recursive:
                new_dict = dict()
                for key, value in the_object.items():
                    new_dict[key] = recurse_obj(value, recursive=True, use_objects=use_objects)
                if use_objects:
                    return_object = DADict('return_object', elements=new_dict)
                    return_object.set_random_instance_name()
                    return return_object
                return new_dict
            else:
                if use_objects:
                    return_object = DADict('return_object', elements=the_object)
                    return_object.set_random_instance_name()
                    return return_object
                return the_object
    return the_object

class DALink(DAObject):
    """An object type Represents a hyperlink to a URL."""
    def __str__(self):
        return str(self.show())
    def show(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return docassemble.base.file_docx.create_hyperlink(self.url, self.anchor_text, docassemble.base.functions.this_thread.misc.get('docx_template', None))
        else:
            return '[%s](%s)' % (self.anchor_text, self.url)

class DAContext(DADict):
    def init(self, *pargs, **kwargs):
        super().init()
        self.pargs = pargs
        self.kwargs = kwargs
        if len(pargs) == 1:
            self.elements['question'] = pargs[0]
            self.elements['document'] = pargs[0]
        if len(pargs) >= 2:
            self.elements['question'] = pargs[0]
            self.elements['document'] = pargs[1]
        for key, val in kwargs.items():
            self.elements[key] = val
    def __str__(self):
        if docassemble.base.functions.this_thread.evaluation_context in ('docx', 'pdf', 'pandoc'):
            if docassemble.base.functions.this_thread.evaluation_context in self.elements:
                return str(self.elements[docassemble.base.functions.this_thread.evaluation_context])
            return str(self.elements['document'])
        else:
            return str(self.elements['question'])
    def __repr__(self):
        output = str('DAContext(' + repr(self.instanceName) + ', ')
        if len(self.elements):
            output += ', '.join(key + '=' + repr(val) for key, val in self.elements.items())
        output += str(')')
    def __hash__(self):
        return hash((self.instanceName,))

def objects_from_structure(target, root=None):
    if isinstance(target, dict):
        if len(target.keys()) > 0 and len(set(target.keys()).difference(set(['question', 'document', 'docx', 'pdf', 'pandoc']))) == 0:
            new_context = DAContext('abc_context', **target)
            if root:
                new_context._set_instance_name_recursively(root)
            new_context.gathered = True
            return new_context
        else:
            new_dict = DADict('abc_dict')
            for key, val in target.items():
                new_dict[key] = objects_from_structure(val)
            new_dict.gathered = True
            if root:
                new_dict._set_instance_name_recursively(root)
            return new_dict
    if isinstance(target, list):
        new_list = DAList('abc_list')
        for val in target.__iter__():
            new_list.append(objects_from_structure(val))
        new_list.gathered = True
        if root:
            new_list._set_instance_name_recursively(root)
        return new_list
    if isinstance(target, (bool, float, int, NoneType, str)):
        return target
    else:
        raise DAError("objects_from_structure: expected a standard type, but found a " + str(type(target)))
