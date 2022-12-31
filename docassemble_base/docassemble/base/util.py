from collections import OrderedDict, abc
from decimal import Decimal
from functools import reduce
from itertools import chain
import codecs
import copy
import datetime
import inspect
import io
import json
import mimetypes
import os
import pickle
import random
import re
import shutil
import stat
import subprocess
# import sys
import tempfile
import time
import types
import zipfile
import pycurl  # pylint: disable=import-error
import requests
import yaml
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from requests.exceptions import RequestException
import httplib2
import oauth2client.client
import apiclient
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from PIL import Image, ImageEnhance
from twilio.rest import Client as TwilioRestClient
import pycountry
from jinja2.runtime import UndefinedError
from jinja2.exceptions import TemplateError
from docassemble.base.error import DAError, DAValidationError, DAIndexError, DAWebError, LazyNameError, DAAttributeError
from docassemble.base.file_docx import include_docx_template
from docassemble.base.filter import markdown_to_html
from docassemble.base.functions import alpha, roman, item_label, comma_and_list, get_language, set_language, get_dialect, get_voice, set_country, get_country, word, comma_list, ordinal, ordinal_number, need, nice_number, quantity_noun, possessify, verb_past, verb_present, noun_plural, noun_singular, space_to_underscore, force_ask, force_gather, period_list, name_suffix, currency_symbol, currency, indefinite_article, nodoublequote, capitalize, title_case, url_of, do_you, did_you, does_a_b, did_a_b, were_you, was_a_b, have_you, has_a_b, your, her, his, their, is_word, get_locale, set_locale, process_action, url_action, get_info, set_info, get_config, prevent_going_back, qr_code, action_menu_item, from_b64_json, defined, define, value, message, response, json_response, command, single_paragraph, quote_paragraphs, location_returned, location_known, user_lat_lon, interview_url, interview_url_action, interview_url_as_qr, interview_url_action_as_qr, interview_email, get_emails, this_thread, static_image, action_arguments, action_argument, language_functions, language_function_constructor, get_default_timezone, user_logged_in, interface, user_privileges, user_has_privilege, user_info, background_action, background_response, background_response_action, background_error_action, us, set_live_help_status, chat_partners_available, phone_number_in_e164, phone_number_formatted, phone_number_is_valid, countries_list, country_name, write_record, read_records, delete_record, variables_as_json, all_variables, server, language_from_browser, device, plain, bold, italic, states_list, state_name, subdivision_type, indent, raw, fix_punctuation, set_progress, get_progress, referring_url, undefine, invalidate, dispatch, yesno, noyes, split, showif, showifdef, phone_number_part, set_parts, log, encode_name, decode_name, interview_list, interview_menu, server_capabilities, session_tags, get_chat_log, get_user_list, get_user_info, set_user_info, get_user_secret, create_user, create_session, get_session_variables, set_session_variables, get_question_data, go_back_in_session, manage_privileges, salutation, redact, ensure_definition, forget_result_of, re_run_logic, reconsider, set_title, set_save_status, single_to_double_newlines, CustomDataType, verbatim, add_separators, update_ordinal_numbers, update_ordinal_function, update_language_function, update_nice_numbers, update_word_collection, store_variables_snapshot, get_uid, update_terms, possessify_long, a_in_the_b, its, the, this, these, underscore_to_space, some, ReturnValue, set_variables, language_name, run_action_in_session  # noqa: F401 # pylint: disable=unused-import
from docassemble.base.generate_key import random_alphanumeric, random_string
from docassemble.base.logger import logmessage
from docassemble.base.pandoc import word_to_markdown, concatenate_files
import docassemble.base.file_docx
import docassemble.base.filter
import docassemble.base.functions
import docassemble.base.geocode
import docassemble.base.pandoc
import docassemble.base.parse
import docassemble.base.pdftk
from docassemble.base import DA
import dateutil
import dateutil.parser
import babel.dates
# import redis
import phonenumbers
from bs4 import BeautifulSoup
import i18naddress
from flask_mail import Message
from pyzbar.pyzbar import decode
from docxtpl import InlineImage, Subdoc, DocxTemplate
# import tablib
import pandas
from docx import Document
from pikepdf import Pdf
import google.cloud

capitalize_func = capitalize
NoneType = type(None)

valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')
match_inside_and_outside_brackets = re.compile(r'(.*)\[([^\]]+)\]$')
is_number = re.compile(r'^[0-9]+$')

QPDF_PATH = 'qpdf'

__all__ = [
    'alpha',
    'roman',
    'item_label',
    'ordinal',
    'ordinal_number',
    'comma_list',
    'word',
    'get_language',
    'set_language',
    'get_dialect',
    'get_voice',
    'set_country',
    'get_country',
    'get_locale',
    'set_locale',
    'comma_and_list',
    'need',
    'nice_number',
    'quantity_noun',
    'currency_symbol',
    'verb_past',
    'verb_present',
    'noun_plural',
    'noun_singular',
    'indefinite_article',
    'capitalize',
    'space_to_underscore',
    'force_ask',
    'force_gather',
    'period_list',
    'name_suffix',
    'currency',
    'static_image',
    'title_case',
    'url_of',
    'process_action',
    'url_action',
    'get_info',
    'set_info',
    'get_config',
    'prevent_going_back',
    'qr_code',
    'action_menu_item',
    'from_b64_json',
    'defined',
    'define',
    'value',
    'message',
    'response',
    'json_response',
    'command',
    'single_paragraph',
    'quote_paragraphs',
    'location_returned',
    'location_known',
    'user_lat_lon',
    'interview_url',
    'interview_url_action',
    'interview_url_as_qr',
    'interview_url_action_as_qr',
    'LatitudeLongitude',
    'RoleChangeTracker',
    'Name',
    'IndividualName',
    'Address',
    'City',
    'Event',
    'Person',
    'Thing',
    'Individual',
    'ChildList',
    'FinancialList',
    'PeriodicFinancialList',
    'Income',
    'Asset',
    'Expense',
    'Value',
    'PeriodicValue',
    'OfficeList',
    'Organization',
    'objects_from_file',
    'send_email',
    'send_sms',
    'send_fax',
    'map_of',
    'selections',
    'DAObject',
    'DAList',
    'DADict',
    'DAOrderedDict',
    'DASet',
    'DAFile',
    'DAFileCollection',
    'DAFileList',
    'DAStaticFile',
    'DAEmail',
    'DAEmailRecipient',
    'DAEmailRecipientList',
    'DATemplate',
    'DAEmpty',
    'DALink',
    'last_access_time',
    'last_access_delta',
    'last_access_days',
    'last_access_hours',
    'last_access_minutes',
    'returning_user',
    'action_arguments',
    'action_argument',
    'timezone_list',
    'as_datetime',
    'current_datetime',
    'date_difference',
    'date_interval',
    'year_of',
    'month_of',
    'day_of',
    'dow_of',
    'format_date',
    'format_datetime',
    'format_time',
    'today',
    'get_default_timezone',
    'user_logged_in',
    'interface',
    'user_privileges',
    'user_has_privilege',
    'user_info',
    'task_performed',
    'task_not_yet_performed',
    'mark_task_as_performed',
    'times_task_performed',
    'set_task_counter',
    'background_action',
    'background_response',
    'background_response_action',
    'background_error_action',
    'us',
    'DARedis',
    'DACloudStorage',
    'DAGoogleAPI',
    'MachineLearningEntry',
    'SimpleTextMachineLearner',
    'SVMMachineLearner',
    'RandomForestMachineLearner',
    'set_live_help_status',
    'chat_partners_available',
    'phone_number_in_e164',
    'phone_number_formatted',
    'phone_number_is_valid',
    'countries_list',
    'country_name',
    'write_record',
    'read_records',
    'delete_record',
    'variables_as_json',
    'all_variables',
    'ocr_file',
    'ocr_file_in_background',
    'read_qr',
    'get_sms_session',
    'initiate_sms_session',
    'terminate_sms_session',
    'language_from_browser',
    'device',
    'interview_email',
    'get_emails',
    'plain',
    'bold',
    'italic',
    'path_and_mimetype',
    'states_list',
    'state_name',
    'subdivision_type',
    'indent',
    'raw',
    'fix_punctuation',
    'set_progress',
    'get_progress',
    'referring_url',
    'run_python_module',
    'undefine',
    'invalidate',
    'dispatch',
    'yesno',
    'noyes',
    'split',
    'showif',
    'showifdef',
    'phone_number_part',
    'pdf_concatenate',
    'set_parts',
    'log',
    'encode_name',
    'decode_name',
    'interview_list',
    'interview_menu',
    'server_capabilities',
    'session_tags',
    'include_docx_template',
    'get_chat_log',
    'get_user_list',
    'get_user_info',
    'set_user_info',
    'get_user_secret',
    'create_user',
    'create_session',
    'get_session_variables',
    'set_session_variables',
    'go_back_in_session',
    'manage_privileges',
    'start_time',
    'zip_file',
    'validation_error',
    'DAValidationError',
    'redact',
    'forget_result_of',
    're_run_logic',
    'reconsider',
    'action_button_html',
    'url_ask',
    'overlay_pdf',
    'get_question_data',
    'set_title',
    'set_save_status',
    'single_to_double_newlines',
    'RelationshipTree',
    'DAContext',
    'DAOAuth',
    'DAStore',
    'explain',
    'clear_explanations',
    'logic_explanation',
    'set_status',
    'get_status',
    'verbatim',
    'add_separators',
    'DAWeb',
    'DAWebError',
    'json',
    're',
    'iso_country',
    'assemble_docx',
    'docx_concatenate',
    'store_variables_snapshot',
    'stash_data',
    'retrieve_stashed_data',
    'update_terms',
    'chain',
    'DABreadCrumbs',
    'set_variables',
    'language_name',
    'DA',
    'DAGlobal',
    'run_action_in_session',
    'transform_json_variables'
]

# knn_machine_learner = DummyObject

# def TheSimpleTextMachineLearner(*pargs, **kwargs):
#     return knn_machine_learner(*pargs, **kwargs)


def fix_word_processing(filename, extension):
    result = word_to_markdown(filename, extension)
    assert result is not None


def fix_docx(filename):
    Document(filename)


def fix_jpg(filename):
    image = Image.open(filename)
    assert image.format == 'JPEG'
    image.close()


def fix_png(filename):
    image = Image.open(filename)
    assert image.format == 'PNG'
    image.close()


def fix_gif(filename):
    image = Image.open(filename)
    assert image.format == 'GIF'
    if image.is_animated:
        new_filename = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".gif")
        image.seek(0)
        image.save(new_filename.name)
        image.close()
        shutil.copyfile(new_filename.name, filename)
    else:
        image.close()


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

    def __init__(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        self.str = str(kwargs.get('str', ''))

    def __getattr__(self, thename):
        if thename.startswith('__') or thename == 'str':
            return object.__getattribute__(self, thename)
        return DAEmpty()

    def __str__(self):
        try:
            return object.__getattribute__(self, 'str')
        except:
            return ''

    def __dir__(self):
        return []

    def __contains__(self, item):
        return False

    def __iter__(self):
        the_list = []
        return the_list.__iter__()

    def __len__(self):
        return 0

    def __reversed__(self):
        return []

    def __getitem__(self, index):
        return DAEmpty()

    def __setitem__(self, index, val):
        pass

    def __delitem__(self, index):
        pass

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

    def init(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        for key, the_value in kwargs.items():
            setattr(self, key, the_value)

    @classmethod
    def using(cls, **kwargs):
        object_plus = DAObjectPlusParameters()
        object_plus.object_type = cls
        object_plus.parameters = kwargs
        return object_plus

    # @classmethod
    # def using(cls, **kwargs):
    #     the_kwargs = {}
    #     for key, val in kwargs.items():
    #         the_kwargs[key] = val
    #     class constructor(cls):
    #         def init(self, *pargs, **kwargs):
    #             new_args = {}
    #             for key, val in the_kwargs.items():
    #                 new_args[key] = val
    #             for key, val in kwargs.items():
    #                 new_args[key] = val
    #             super().init(*pargs, **new_args)
    #     return constructor

    def __init__(self, *pargs, **kwargs):
        thename = None
        if len(pargs) > 0:
            pargs = list(pargs)
            thename = pargs.pop(0)
        if thename is not None:
            self.has_nonrandom_instance_name = True
        else:
            stack = inspect.stack()
            frame = stack[1][0]
            the_names = frame.f_code.co_names
            # logmessage("co_name is " + str(frame.f_code.co_names))
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
        self.attrList = []
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
        # logmessage("_set_instance_name_for_method: method_name is " + str(method_name));
        level = 1
        while level < 10:
            frame = inspect.stack()[level][0]
            the_names = frame.f_code.co_names
            # logmessage("_set_instance_name_for_method: level " + str(level) + "; co_name is " + str(frame.f_code.co_names))
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

    def getattr_fresh(self, attr):
        """Compute a fresh value of the given attr and return it."""
        if hasattr(self, attr):
            docassemble.base.functions.reconsider(self.instanceName + '.' + attr)
        return getattr(self, attr)

    def is_peer_relation(self, target, relationship_type, tree):
        for item in tree.query_peer(tree._and(involves=[self, target], relationship_type=relationship_type)):  # pylint: disable=unused-variable
            return True
        return False

    def is_relation(self, target, relationship_type, tree, self_is='either', filter_by=None):
        extra_queries = []
        if filter_by is not None:
            if not isinstance(filter_by, dict):
                raise DAError("is_relation: filter_by must be a dictionary.")
            extra_queries = []
            for key, val in filter_by.items():
                if self_is == 'either':
                    extra_queries.append(tree._or(lambda y, the_key=key, the_val=val: hasattr(self.child, the_key) and getattr(self.child, the_key) == the_val, lambda y, the_key=key, the_val=val: hasattr(y.parent, the_key) and getattr(y.parent, the_key) == the_val))
                elif self_is == 'parent':
                    extra_queries.append(lambda y, the_key=key, the_val=val: hasattr(y.child, the_key) and getattr(y.child, the_key) == the_val)
                elif self_is == 'child':
                    extra_queries.append(lambda y, the_key=key, the_val=val: hasattr(y.parent, the_key) and getattr(y.parent, the_key) == the_val)
                else:
                    raise DAError("is_relation: self_is must be parent, child, or other")
        if self_is == 'either':
            for item in tree.query_peer(tree._and(*extra_queries, involves=[self, target], relationship_type=relationship_type)):  # pylint: disable=unused-variable
                return True
        elif self_is == 'parent':
            for item in tree.query_peer(tree._and(*extra_queries, parent=self, child=target, relationship_type=relationship_type)):  # pylint: disable=unused-variable
                return True
        elif self_is == 'child':
            for item in tree.query_peer(tree._and(*extra_queries, child=self, parent=target, relationship_type=relationship_type)):  # pylint: disable=unused-variable
                return True
        else:
            raise DAError("is_relation: self_is must be parent, child, or other")
        return False

    def get_relation(self, relationship_type, tree, self_is='either', create=False, object_type=None, complete_attribute=None, rel_filter_by=None, filter_by=None, count=1):
        results = DAList(auto_gather=False, gathered=True)
        results.set_random_instance_name()
        if rel_filter_by is None:
            query_params = {}
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
                filter_by = {}
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
                    for attrib in self._complete_attributes(complete_attribute):
                        complex_getattr(self.new_relation[relationship_type], attrib)
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
            query_params = {}
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
                    for attrib in self._complete_attributes(complete_attribute):
                        complex_getattr(self.new_peer_relation[relationship_type], attrib)
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
            to_delete = []
            for item in tree.query_peer(tree._and(involves=self, relationship_type=relationship_type)):
                to_delete.append(item)
            if len(to_delete) > 0:
                tree.delete_peer(*to_delete)
        return tree.add_relationship_peer(self, target, relationship_type=relationship_type)

    def set_relationship(self, target, relationship_type, self_is, tree, replace=False):
        if self_is not in ('parent', 'child'):
            raise DAError("set_relationship: self_is must be parent or child")
        if replace:
            to_delete = []
            if self_is == 'parent':
                for item in tree.query_dir(tree._and(parent=self, relationship_type=relationship_type)):
                    to_delete.append(item)
            elif self_is == 'child':
                for item in tree.query_dir(tree._and(child=self, relationship_type=relationship_type)):
                    to_delete.append(item)
            if len(to_delete) > 0:
                tree.delete_dir(*to_delete)
        if self_is == 'parent':
            return tree.add_relationship_dir(parent=self, child=target, relationship_type=relationship_type)
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
        # else:
        #     logmessage("Not resetting name of " + self.instanceName)

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
        # logmessage("Change " + str(self.instanceName) + " to " + str(thename))
        # if not self.has_nonrandom_instance_name:
        if matching is not None and not self.instanceName.startswith(matching):
            return
        self.instanceName = thename
        self.has_nonrandom_instance_name = True
        for aname in self.__dict__:
            if hasattr(self, aname) and isinstance(getattr(self, aname), DAObject):
                # logmessage("ASDF Setting " + str(thename) + " for " + str(aname))
                getattr(self, aname)._set_instance_name_recursively(thename + '.' + aname, matching=matching)

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
        if thename.startswith('__') or hasattr(self.__class__, thename):
            if 'pending_error' in docassemble.base.functions.this_thread.misc:
                pending_error = docassemble.base.functions.this_thread.misc['pending_error']
                del docassemble.base.functions.this_thread.misc['pending_error']
                raise pending_error
            return object.__getattribute__(self, thename)
        var_name = object.__getattribute__(self, 'instanceName') + "." + thename
        docassemble.base.functions.this_thread.misc['pending_error'] = DAAttributeError("name '" + var_name + "' is not defined")
        raise docassemble.base.functions.this_thread.misc['pending_error']

    def object_name(self, **kwargs):
        """Returns the instanceName attribute, or, if the instanceName contains attributes, returns a
        phrase.  E.g., case.plaintiff becomes "plaintiff in the case." """
        the_name = reduce(a_in_the_b, map(object_name_convert, reversed(self.instanceName.split("."))))
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(the_name)
        return the_name

    def as_serializable(self):
        """Returns a serializable representation of the object."""
        return docassemble.base.functions.safe_json(self)

    def object_possessive(self, target, **kwargs):
        """Returns a possessive phrase based on the instanceName.  E.g., client.object_possessive('fish') returns
        "client's fish." """
        language = kwargs.get('language', None)
        if len(self.instanceName.split(".")) > 1:
            return possessify_long(self.object_name(), target, language=language)
        return possessify(the(self.object_name(), language=language), target, language=language, capitalize=kwargs.get('capitalize', False))

    def initializeAttribute(self, *pargs, **kwargs):
        """Defines an attribute for the object, setting it to a newly initialized object.
        The first argument is the name of the attribute and the second argument is type
        of the new object that will be initialized.  E.g.,
        client.initializeAttribute('mother', Individual) initializes client.mother as an
        Individual with instanceName "client.mother"."""
        pargs = list(pargs)
        if len(pargs) < 2:
            raise Exception("initializeAttribute requires an attribute name and an object type")
        name = pargs.pop(0)
        object_type = pargs.pop(0)
        new_object_parameters = {}
        if isinstance(object_type, DAObjectPlusParameters):
            for key, val in object_type.parameters.items():
                new_object_parameters[key] = val
            object_type = object_type.object_type
        for key, val in kwargs.items():
            new_object_parameters[key] = val
        if name in self.__dict__:
            return getattr(self, name)
        object.__setattr__(self, name, object_type(self.instanceName + "." + name, *pargs, **new_object_parameters))
        self.attrList.append(name)
        return getattr(self, name)

    def reInitializeAttribute(self, *pargs, **kwargs):
        """Redefines an attribute for the object, setting it to a newly initialized object.
        The first argument is the name of the attribute and the second argument is type
        of the new object that will be initialized.  E.g.,
        client.reInitializeAttribute('mother', Individual) initializes client.mother as an
        Individual with instanceName "client.mother"."""
        pargs = list(pargs)
        name = pargs.pop(0)
        object_type = pargs.pop(0)
        new_object_parameters = {}
        if isinstance(object_type, DAObjectPlusParameters):
            for key, val in object_type.parameters.items():
                new_object_parameters[key] = val
            object_type = object_type.object_type
        for key, val in kwargs.items():
            new_object_parameters[key] = val
        object.__setattr__(self, name, object_type(self.instanceName + "." + name, *pargs, **new_object_parameters))
        if name in self.__dict__:
            return getattr(self, name)
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
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Returns it."""
        return word('it', **kwargs)

    def alternative(self, *pargs, **kwargs):
        """Returns a particular value depending on the value of a given attribute"""
        if len(pargs) == 0:
            raise Exception("alternative: attribute must be provided")
        attribute = pargs[0]
        the_value = getattr(self, attribute)
        if the_value in kwargs:
            return kwargs[the_value]
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

    def __setattr__(self, key, the_value):
        if isinstance(the_value, DAObject) and not the_value.has_nonrandom_instance_name:
            the_value.has_nonrandom_instance_name = True
            the_value.instanceName = self.instanceName + '.' + str(key)
        super().__setattr__(key, the_value)

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
        if self.context == 'callable':
            return 'callable'
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

    def __call__(self, *args, **kwargs):
        self.context = 'callable'
        return self.value(*args, **kwargs)


class RelationshipDir(DAObject):
    """A data structure representing a relationships among people."""

    def involves(self, target):
        # logmessage("RelationshipDir: involves " + repr(target))
        if self.parent is target or self.child is target:
            return True
        return False


class RelationshipPeer(DAObject):
    """A data structure representing a relationships among people."""

    def involves(self, target):
        # logmessage("RelationshipPeer: involves " + repr(target))
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
        filters = []
        for item in pargs:
            if isinstance(item, types.FunctionType):
                filters.append(item)
        for key, val in kwargs.items():
            if key == 'involves':
                # logmessage("_func_list: key is involves")
                if isinstance(val, (list, set, DAList, DASet)):
                    # logmessage("_func_list: involves in a list")
                    subfilters = []
                    for item in val:
                        # logmessage("_func_list: adding a subfilter")
                        subfilters.append(generator_involves(item))
                    filters.append(self._and(*subfilters))
                else:
                    # logmessage("_func_list: involves without a list")
                    filters.append(generator_involves(val))
            elif isinstance(val, DAObject):
                # logmessage("_func_list: a DAObject")
                filters.append(generator_is(key, val))
            else:
                # logmessage("_func_list: key is " + repr(key) + " and val is " + repr(val) + "")
                filters.append(generator_equals(key, val))
        return filters

    def _and(self, *pargs, **kwargs):
        # logmessage("_and")
        filters = self._func_list(*pargs, **kwargs)
        def func(y):
            # logmessage("in _and func")
            for subfunc in filters:
                # logmessage("evaluating _and func")
                result = subfunc(y)
                # logmessage("result is " + repr(result))
                if not result:
                    return False
            return True
        return func

    def _or(self, *pargs, **kwargs):
        # logmessage("_or")
        filters = self._func_list(*pargs, **kwargs)
        def func(y):
            # logmessage("in _or func")
            for subfunc in filters:
                # logmessage("evaluating _or func")
                if subfunc(y):
                    return True
            return False
        return func

    def query_peer(self, *pargs, **kwargs):
        # logmessage("query_peer")
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
        # logmessage("query_dir")
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
        args = {}
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
        # logmessage("Setting relationship involving " + repr(the_set) + " and reltype " + relationship_type)
        return self.relationships_peer.appendObject(peers=the_set, relationship_type=relationship_type)

    def delete_peer(self, *pargs):
        """Deletes the given peer relationship(s)"""
        self.relationships_peer.remove(*pargs)


class DAList(DAObject):
    """The base class for lists of things."""

    def init(self, *pargs, **kwargs):
        self.elements = []
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
                self.object_type_parameters = {}
            del kwargs['object_type']
        if not hasattr(self, 'object_type'):
            self.object_type = None
        if not hasattr(self, 'object_type_parameters'):
            self.object_type_parameters = {}
        if 'complete_attribute' in kwargs:
            self.complete_attribute = kwargs['complete_attribute']
            del kwargs['complete_attribute']
        if not hasattr(self, 'complete_attribute'):
            self.complete_attribute = None
        if 'ask_object_type' in kwargs:
            self.ask_object_type = True
        if not hasattr(self, 'ask_object_type'):
            self.ask_object_type = False
        super().init(*pargs, **kwargs)

    def initializeObject(self, *pargs, **kwargs):
        """Creates a new object and creates an entry in the list for it.
        The first argument is the index to set.
        Takes an optional second argument, which is the type of object
        the new object should be.  If no object type is provided, the
        object type given by .object_type is used, and if that is not
        set, DAObject is used.

        """
        objectFunction = None
        pargs = list(pargs)
        index = pargs.pop(0)
        if len(pargs) > 0:
            objectFunction = pargs.pop(0)
        new_obj_parameters = {}
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
        for key, val in kwargs.items():
            new_obj_parameters[key] = val
        newobject = objectFunction(self.instanceName + '[' + repr(index) + ']', *pargs, **new_obj_parameters)
        for pre_index in range(index):  # pylint: disable=unused-variable
            self.elements.append(None)
        self[index] = newobject
        self.there_are_any = True
        return newobject

    def set_object_type(self, object_type):
        """Sets the object_type of the DAList"""
        if isinstance(object_type, DAObjectPlusParameters):
            self.object_type = object_type.object_type
            self.object_type_parameters = object_type.parameters
        else:
            self.object_type = object_type
            self.object_type_parameters = {}

    def gathered_and_complete(self):
        """Ensures all items in the list are complete and then returns True."""
        if not hasattr(self, 'doing_gathered_and_complete'):
            self.doing_gathered_and_complete = True
            if hasattr(self, 'complete_attribute') and self.complete_attribute == 'complete':
                for item in self.elements:
                    if hasattr(item, 'complete'):
                        try:
                            delattr(item, 'complete')
                        except:
                            pass
            if hasattr(self, 'gathered'):
                del self.gathered
        if self.auto_gather:
            self.gather()
        else:
            self.hook_on_gather()
            self.gathered  # pylint: disable=pointless-statement
            self.hook_after_gather()
        if hasattr(self, 'doing_gathered_and_complete'):
            del self.doing_gathered_and_complete
        return True

    def item_name(self, item):
        """Returns a variable name for an item, suitable for use in force_ask() and other functions."""
        return self.instanceName + '[' + repr(item) + ']'

    def delitem(self, *pargs):
        """Deletes items."""
        for item in reversed([item for item in pargs if item < len(self.elements)]):
            self.elements.__delitem__(item)  # pylint: disable=unnecessary-dunder-call
        self._reset_instance_names()

    def copy(self):
        """Returns a copy of the list."""
        return self.elements.copy()

    def filter(self, *pargs, **kwargs):
        """Returns a filtered version of the list containing only items with particular values of attributes."""
        self._trigger_gather()
        new_elements = []
        for item in self.elements:
            include = True
            for key, val in kwargs.items():
                if getattr(item, key) != val:
                    include = False
                    break
            if include:
                new_elements.append(item)
        if len(pargs) > 0:
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
                self.gathered  # pylint: disable=pointless-statement

    def reset_gathered(self, recursive=False, only_if_empty=False, mark_incomplete=False):
        """Indicates that there is more to be gathered"""
        # logmessage("reset_gathered on " + self.instanceName)
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
            for attrib in self._complete_attributes():
                for item in self.elements:
                    if complex_hasattr(item, attrib):
                        try:
                            complex_delattr(item, attrib)
                        except:
                            pass
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
        # self._trigger_gather()
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
            the_list = self.__class__(elements=self.elements + other.elements, gathered=True, auto_gather=False)
            the_list.set_random_instance_name()
            return the_list
        return self.elements + other

    def __radd__(self, other):
        self._trigger_gather()
        if isinstance(other, DAEmpty):
            return self
        if isinstance(other, DAList):
            other._trigger_gather()
            the_list = self.__class__(elements=other.elements + self.elements, gathered=True, auto_gather=False)
            the_list.set_random_instance_name()
            return the_list
        return other + self.elements

    def index(self, *pargs, **kwargs):
        """Returns the first index at which a given item may be found."""
        self._trigger_gather()
        return self.elements.index(*pargs, **kwargs)

    def clear(self):
        """Removes all the items from the list."""
        self.elements = []
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
        super().fix_instance_name(old_instance_name, new_instance_name)

    def _set_instance_name_recursively(self, thename, matching=None):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        indexno = 0
        for item in self.elements:
            if isinstance(item, DAObject):
                item._set_instance_name_recursively(thename + '[' + str(indexno) + ']', matching=matching)
            indexno += 1
        super()._set_instance_name_recursively(thename, matching=matching)

    def _mark_as_gathered_recursively(self):
        for item in self.elements:
            if isinstance(item, DAObject):
                item._mark_as_gathered_recursively()
        super()._mark_as_gathered_recursively()

    def _reset_gathered_recursively(self):
        self.reset_gathered()
        for item in self.elements:
            if isinstance(item, DAObject):
                item._reset_gathered_recursively()
        super()._reset_gathered_recursively()

    def _reset_instance_names(self):
        indexno = 0
        for item in self.elements:
            if isinstance(item, DAObject) and item.instanceName.startswith(self.instanceName + '['):
                item._set_instance_name_recursively(self.instanceName + '[' + str(indexno) + ']', matching=self.instanceName + '[')
            indexno += 1

    def sort(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        """Reorders the elements of the list in place and returns the object."""
        self._trigger_gather()
        self.elements = sorted(self.elements, **kwargs)
        self._reset_instance_names()
        self.hook_after_gather()
        return self

    def reverse(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        """Reverse the order of the elements of the list in place and returns the object."""
        self._trigger_gather()
        self.elements.reverse()
        self._reset_instance_names()
        self.hook_after_gather()
        return self

    def sort_elements(self, *pargs, **kwargs):  # pylint: disable=unused-argument
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
        # logmessage("Called appendObject where len is " + str(len(self.elements)))
        objectFunction = None
        if len(pargs) > 0:
            pargs = list(pargs)
            objectFunction = pargs.pop(0)
        new_obj_parameters = {}
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
        for the_value in pargs:
            if the_value in self.elements:
                self.hook_on_remove(the_value)
                self.elements.remove(the_value)
                something_removed = True
        self._reset_instance_names()
        if something_removed and len(self.elements) == 0:
            self.there_are_any = False

    def _remove_items_by_number(self, *pargs):
        """Removes items from the list, by index number"""
        new_list = []
        list_truncated = False
        for indexno, item in enumerate(self.elements):
            if indexno not in pargs:
                new_list.append(item)
            else:
                list_truncated = True
        self.elements = new_list
        self._reset_instance_names()
        if list_truncated and hasattr(self, '_necessary_length'):
            del self._necessary_length

    def insert(self, *pargs):
        """Inserts an item at the given position."""
        self.elements.insert(*pargs)
        self._reset_instance_names()
        self.there_are_any = True

    def count(self, item):
        """Returns the number of times item appears in the list."""
        self._trigger_gather()
        return self.elements.count(item)

    def extend(self, the_list):
        """Adds each of the elements of the given list to the end of the list."""
        self.elements.extend(the_list)

    def first(self):
        """Returns the first element of the list"""
        self._trigger_gather()
        return self.__getitem__(0)  # pylint: disable=unnecessary-dunder-call

    def last(self):
        """Returns the last element of the list"""
        self._trigger_gather()
        if len(self.elements) == 0:
            return self.__getitem__(0)  # pylint: disable=unnecessary-dunder-call
        return self.__getitem__(len(self.elements)-1)  # pylint: disable=unnecessary-dunder-call

    def does_verb(self, the_verb, **kwargs):
        """Returns the appropriate conjugation of the given verb depending on whether
        there is only one element in the list or multiple elements.  E.g.,
        case.plaintiff.does_verb('sue') will return "sues" if there is one plaintiff
        and "sue" if there is more than one plaintiff."""
        language = kwargs.get('language', None)
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
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
        """Returns the output of the quantity_noun() function using the number
        of elements in the list as the quantity."""
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
                return capitalize_func(output)
            return output
        output = noun_singular(the_noun)
        if 'article' in kwargs and kwargs['article']:
            output = indefinite_article(output, language=language)
        elif 'this' in kwargs and kwargs['this']:
            output = this(output, language=language)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
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

    def number_as_word(self, language=None, capitalize=False):  # pylint: disable=redefined-outer-name
        """Returns the number of elements in the list, spelling out the number if ten
        or below.  Forces the gathering of the elements if necessary."""
        return nice_number(self.number(), language=language, capitalize=capitalize)

    def complete_elements(self, complete_attribute=None):
        """Returns a list of the elements that are complete."""
        if complete_attribute is None and hasattr(self, 'complete_attribute'):
            complete_attribute = self.complete_attribute
        items = self.__class__(self.instanceName)
        for item in self.elements:
            if item is None:
                continue
            if complete_attribute is not None:
                should_skip = False
                for attrib in self._complete_attributes(complete_attribute):
                    if not complex_hasattr(item, attrib):
                        should_skip = True
                        break
                if should_skip:
                    continue
            else:
                try:
                    str(item)
                except:
                    continue
            items.append(item)
        items.gathered = True
        return items

    def _complete_attributes(self, complete_attribute=None):
        if complete_attribute is None:
            complete_attribute = self.complete_attribute
        if isinstance(complete_attribute, str):
            return [complete_attribute]
        if isinstance(complete_attribute, list):
            return complete_attribute
        if isinstance(complete_attribute, DAList):
            return complete_attribute.elements
        return []

    def _validate(self, item_object_type, complete_attribute):
        if self.ask_object_type:
            for indexno, the_element in enumerate(self.elements):
                if the_element is None:
                    if isinstance(self.new_object_type, DAObjectPlusParameters):
                        object_type_to_use = self.new_object_type.object_type
                        parameters_to_use = self.new_object_type.parameters
                    if isinstance(self.new_object_type, type):
                        object_type_to_use = self.new_object_type
                        parameters_to_use = {}
                    else:
                        raise Exception("new_object_type must be an object type")
                    self.elements[indexno] = object_type_to_use(self.instanceName + '[' + str(indexno) + ']', **parameters_to_use)
                if complete_attribute is not None:
                    for attrib in self._complete_attributes(complete_attribute):
                        complex_getattr(self.elements[indexno], attrib)
                else:
                    str(self.elements[indexno])
            if hasattr(self, 'new_object_type'):
                delattr(self, 'new_object_type')
        for elem in self.elements:
            if item_object_type is not None and complete_attribute is not None:
                for attrib in self._complete_attributes(complete_attribute):
                    complex_getattr(elem, attrib)
            else:
                str(elem)

    def _allow_appending(self):
        self._appending_allowed = True

    def _disallow_appending(self):
        if hasattr(self, '_appending_allowed'):
            del self._appending_allowed

    def gather(self, number=None, item_object_type=None, minimum=None, complete_attribute=None):
        """Causes the elements of the list to be gathered and named.  Returns True."""
        # logmessage("Gather")
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
            item_object_parameters = {}
        if complete_attribute is None and self.complete_attribute is not None:
            complete_attribute = self.complete_attribute
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        if number is None and self.ask_number:
            if hasattr(self, 'there_are_any') and not self.there_are_any:
                number = 0
            else:
                number = int(self.target_number)
        if minimum is None:
            minimum = self.minimum_number
        if number is None and (minimum is None or minimum == 0):
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
                self.__getitem__(the_length)  # pylint: disable=unnecessary-dunder-call
                self._validate(item_object_type, complete_attribute)
                # str(self.__getitem__(the_length))  # pylint: disable=unnecessary-dunder-call
                # if item_object_type is not None and complete_attribute is not None:
                #     getattr(self.__getitem__(the_length), complete_attribute)  # pylint: disable=unnecessary-dunder-call
        # for elem in self.elements:
        #     str(elem)
        #     if item_object_type is not None and complete_attribute is not None:
        #         getattr(elem, complete_attribute)
        the_length = len(self.elements)
        if hasattr(self, '_necessary_length'):
            if self._necessary_length <= the_length:  # pylint: disable=access-member-before-definition
                del self._necessary_length
            elif number is None or number < self._necessary_length:  # pylint: disable=access-member-before-definition
                number = self._necessary_length  # pylint: disable=access-member-before-definition
        if number is not None:
            while the_length < int(number):
                if item_object_type is not None:
                    self.appendObject(item_object_type, **item_object_parameters)
                self.__getitem__(the_length)  # pylint: disable=unnecessary-dunder-call
                self._validate(item_object_type, complete_attribute)
                # str(self.__getitem__(the_length))  # pylint: disable=unnecessary-dunder-call
                # if item_object_type is not None and complete_attribute is not None:
                #     getattr(self.__getitem__(the_length), complete_attribute)  # pylint: disable=unnecessary-dunder-call
                the_length = len(self.elements)
            if hasattr(self, '_necessary_length'):
                del self._necessary_length
        elif minimum != 0:
            while self.there_is_another or (hasattr(self, 'there_is_one_other') and self.there_is_one_other):
                # logmessage("gather " + self.instanceName + ": del on there_is_another")
                if hasattr(self, 'there_is_one_other'):
                    del self.there_is_one_other
                elif hasattr(self, 'there_is_another'):
                    del self.there_is_another
                self._necessary_length = the_length + 1
                if item_object_type is not None:
                    self.appendObject(item_object_type, **item_object_parameters)
                self.__getitem__(the_length)  # pylint: disable=unnecessary-dunder-call
                self._validate(item_object_type, complete_attribute)
                # str(self.__getitem__(the_length))  # pylint: disable=unnecessary-dunder-call
                # if item_object_type is not None and complete_attribute is not None:
                #     getattr(self.__getitem__(the_length), complete_attribute)  # pylint: disable=unnecessary-dunder-call
        if hasattr(self, '_necessary_length'):
            del self._necessary_length
        self.hook_on_gather()
        if self.auto_gather:
            self.gathered = True
            self.revisit = True
        # if hasattr(self, 'doing_gathered_and_complete'):
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
        return int(self.target_number)

    def __len__(self):
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return self.elements.__len__()

    def __delitem__(self, index):
        self[index]  # pylint: disable=pointless-statement
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
            if num_to_add > 10:
                raise Exception("Attempt to fill up more than 10 items")
            for i in range(0, num_to_add):  # pylint: disable=unused-variable
                if self.object_type is None:
                    self.elements.append(None)
                else:
                    self.appendObject(self.object_type, **self.object_type_parameters)
        elif len(self.elements) <= index:
            num_to_add = 1 + index - len(self.elements)
            if num_to_add > 10:
                raise Exception("Attempt to fill up more than 10 items")
            for i in range(0, num_to_add):
                if self.object_type is None:
                    self.elements.append(None)
                else:
                    self.appendObject(self.object_type, **self.object_type_parameters)

    def __setitem__(self, index, the_value):
        self._fill_up_to(index)
        if isinstance(the_value, DAObject) and not the_value.has_nonrandom_instance_name:
            the_value.has_nonrandom_instance_name = True
            the_value.instanceName = self.instanceName + '[' + str(index) + ']'
            # the_value._set_instance_name_recursively(self.instanceName + '[' + str(index) + ']')
        return self.elements.__setitem__(index, the_value)

    def __getitem__(self, index):
        try:
            return self.elements[index]
        except:
            if (self.auto_gather and hasattr(self, 'gathered') and not (hasattr(self, '_appending_allowed') and self._appending_allowed)) or docassemble.base.functions.this_thread.probing:
                try:
                    logmessage("list index " + str(index) + " out of range on " + str(self.instanceName))
                except:
                    pass
                raise IndexError("list index out of range")
            if self.object_type is None and not self.ask_object_type:
                var_name = object.__getattribute__(self, 'instanceName') + '[' + str(index) + ']'
                # force_gather(var_name)
                raise DAIndexError("name '" + var_name + "' is not defined")
            # logmessage("Calling fill up to")
            self._fill_up_to(index)
            # logmessage("Assuming it is there!")
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
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Returns a pronoun like "you," "her," or "him," "it", or "them," as appropriate."""
        if self.number() == 1:
            self._trigger_gather()
            return self.elements[0].pronoun(**kwargs)
        output = word('them', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

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
            return capitalize_func(output)
        return output

    def _reorder(self, *pargs):
        old_elements = self.elements
        self.elements = copy.copy(self.elements)
        maximum = len(self.elements)
        for item in pargs:
            if item[0] < maximum and item[1] < maximum:
                self.elements[item[1]] = old_elements[item[0]]
        self._reset_instance_names()
        if hasattr(self, 'gathered') and self.gathered:
            self.hook_after_gather()

    def item_actions(self, *pargs, **kwargs):
        """Returns HTML for editing the items in a list"""
        the_args = list(pargs)
        item = the_args.pop(0)
        index = the_args.pop(0)
        output = ''
        if kwargs.get('reorder', False):
            output += '<span class="text-nowrap"><a href="#" role="button" class="btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('reorder', 'info') + ' btn-darevisit datableup" data-tablename="' + myb64quote(self.instanceName) + '" data-tableitem="' + str(index) + '" title=' + json.dumps(word("Reorder by moving up")) + '><i class="fas fa-arrow-up"></i><span class="visually-hidden">' + word("Move down") + '</span></a> <a href="#" role="button" class="btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('reorder', 'info') + ' btn-darevisit databledown"><i class="fas fa-arrow-down" title=' + json.dumps(word("Reorder by moving down")) + '></i><span class="visually-hidden">' + word("Move down") + '</span></a></span> '
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
            # if self.complete_attribute == 'complete':
            #    items += [dict(action='_da_undefine', arguments=dict(variables=[item.instanceName + '.' + self.complete_attribute]))]
            if len(the_args) > 0:
                items += [{'follow up': [item.instanceName + ('' if y.startswith('[') else '.') + y for y in the_args]}]
            else:
                items += [{'follow up': [self.instanceName + '[' + repr(index) + ']']}]
            if self.complete_attribute is not None and self.complete_attribute != 'complete':
                items += [dict(action='_da_define', arguments=dict(variables=[item.instanceName + '.' + attrib for attrib in self._complete_attributes()]))]
            if ensure_complete:
                items += [dict(action='_da_list_ensure_complete', arguments=dict(group=self.instanceName))]
            output += '<a href="' + docassemble.base.functions.url_action('_da_list_edit', items=items) + '" role="button" class="btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('edit', 'secondary') + ' btn-darevisit"><span class="text-nowrap"><i class="fas fa-pencil-alt"></i> ' + word('Edit') + '</span></a> '
        if use_delete and can_delete:
            if kwargs.get('confirm', False):
                areyousure = ' daremovebutton'
            else:
                areyousure = ''
            output += '<a href="' + docassemble.base.functions.url_action('_da_list_remove', list=self.instanceName, item=repr(index)) + '" role="button" class="btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('delete', 'danger') + ' btn-darevisit' + areyousure + '"><span class="text-nowrap"><i class="fas fa-trash"></i> ' + word('Delete') + '</span></a>'
        if kwargs.get('edit_url_only', False):
            return docassemble.base.functions.url_action('_da_list_edit', items=items)
        if kwargs.get('delete_url_only', False):
            return docassemble.base.functions.url_action('_da_list_remove', dict=self.instanceName, item=repr(index))
        return output

    def add_action(self, label=None, message=None, url_only=False, icon='plus-circle', color=None, size='sm', block=None, classname=None):  # pylint: disable=redefined-outer-name
        """Returns HTML for adding an item to a list"""
        if color is None:
            color = server.daconfig['button colors'].get('add', 'secondary')
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
        return '<a href="' + docassemble.base.functions.url_action('_da_list_add', list=self.instanceName) + '" class="btn' + size + block + ' ' + server.button_class_prefix + color + classname + '">' + icon + str(message) + '</a>'

    def hook_on_gather(self, *pargs, **kwargs):
        """Code that runs just before a list is marked as gathered."""

    def hook_after_gather(self, *pargs, **kwargs):
        """Code that runs just after a list is marked as gathered."""

    def hook_on_item_complete(self, item, *pargs, **kwargs):
        """Code that runs when an item is marked as complete."""

    def hook_on_remove(self, item, *pargs, **kwargs):
        """Code that runs when an item is removed from the list."""

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
                self.object_type_parameters = {}
            del kwargs['object_type']
        if not hasattr(self, 'object_type'):
            self.object_type = None
        if not hasattr(self, 'object_type_parameters'):
            self.object_type_parameters = {}
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
        super().init(*pargs, **kwargs)

    def set_object_type(self, object_type):
        """Sets the object_type of the DADict"""
        if isinstance(object_type, DAObjectPlusParameters):
            self.object_type = object_type.object_type
            self.object_type_parameters = object_type.parameters
        else:
            self.object_type = object_type
            self.object_type_parameters = {}

    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered  # pylint: disable=pointless-statement

    def fix_instance_name(self, old_instance_name, new_instance_name):
        """Substitutes a different instance name for the object and its subobjects."""
        for key, the_value in self.elements.items():  # pylint: disable=unused-variable
            if isinstance(the_value, DAObject):
                the_value.fix_instance_name(old_instance_name, new_instance_name)
        super().fix_instance_name(old_instance_name, new_instance_name)

    def _set_instance_name_recursively(self, thename, matching=None):
        """Sets the instanceName attribute, if it is not already set, and that of subobjects."""
        for key, the_value in self.elements.items():
            if isinstance(the_value, DAObject):
                the_value._set_instance_name_recursively(thename + '[' + repr(key) + ']', matching=matching)
        super()._set_instance_name_recursively(thename, matching=matching)

    def _mark_as_gathered_recursively(self):
        for key, the_value in self.elements.items():  # pylint: disable=unused-variable
            if isinstance(the_value, DAObject):
                the_value._mark_as_gathered_recursively()
        super()._mark_as_gathered_recursively()

    def _reset_gathered_recursively(self):
        self.reset_gathered()
        for key, the_value in self.elements.items():  # pylint: disable=unused-variable
            if isinstance(the_value, DAObject):
                the_value._reset_gathered_recursively()
        super()._reset_gathered_recursively()

    def item_name(self, item):
        """Returns a variable name for an item, suitable for use in force_ask() and other functions."""
        return self.instanceName + '[' + repr(item) + ']'

    def delitem(self, *pargs):
        """Deletes items."""
        for item in pargs:
            if item in self.elements:
                del self[item]

    def invalidate_item(self, *pargs):
        """Invalidate items."""
        for item in pargs:
            if item in self.elements.keys():
                invalidate(self.item_name(item))

    def getitem_fresh(self, item):
        """Compute a fresh value of the given item and return it."""
        if item in self.elements:
            docassemble.base.functions.reconsider(self.item_name(item))
        return self[item]

    def all_false(self, *pargs, **kwargs):
        """Returns True if the values of all keys are false.  If one or more
        keys are provided as arguments, returns True if all of the
        values of those keys are false.  If the optional keyword
        argument 'exclusive' is True, returns True only if those keys
        are the only false values.

        """
        the_list = []
        exclusive = kwargs.get('exclusive', False)
        for parg in pargs:
            if isinstance(parg, (DAList, DASet, abc.Iterable)) and not isinstance(parg, str):
                the_list.extend(list(parg))
            else:
                the_list.append(parg)
        if len(the_list) == 0:
            for key, the_value in self._sorted_elements_items():
                if the_value:
                    return False
            self._trigger_gather()
            return True
        for key in the_list:
            if key not in self.elements:
                return False
        for key, the_value in self._sorted_elements_items():
            if key in the_list:
                if the_value:
                    return False
            else:
                if exclusive and not the_value:
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
        the_list = []
        exclusive = kwargs.get('exclusive', False)
        for parg in pargs:
            if isinstance(parg, (DAList, DASet, abc.Iterable)) and not isinstance(parg, str):
                the_list.extend(list(parg))
            else:
                the_list.append(parg)
        if len(the_list) == 0:
            for key, the_value in self._sorted_elements_items():
                if not the_value:
                    return False
            self._trigger_gather()
            return True
        for key in the_list:
            if key not in self.elements:
                return False
        for key, the_value in self._sorted_elements_items():
            if key in the_list:
                if not the_value:
                    return False
            else:
                if exclusive and the_value:
                    return False
        self._trigger_gather()
        return True

    def true_values(self, insertion_order=False):
        """Returns the keys for which the corresponding value is true."""
        if insertion_order:
            return DAList(elements=[key for key, value in self.items() if value])
        return DAList(elements=[key for key, value in self._sorted_items() if value])

    def false_values(self, insertion_order=False):
        """Returns the keys for which the corresponding value is false."""
        if insertion_order:
            return DAList(elements=[key for key, value in self.items() if not value])
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
        pargs = list(pargs)
        entry = pargs.pop(0)
        if len(pargs) > 0:
            objectFunction = pargs.pop(0)
        new_obj_parameters = {}
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
                new_obj_parameters = {}
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
        # logmessage("reset_gathered on " + self.instanceName)
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
            for attrib in self._complete_attributes():
                for item in list(self.elements.values()):
                    if complex_hasattr(item, attrib):
                        try:
                            complex_delattr(item, attrib)
                        except:
                            pass
        if recursive:
            self._reset_gathered_recursively()

    def slice(self, *pargs):
        """Returns a shallow copy of the dictionary containing only the keys provided in the parameters."""
        new_dict = copy.copy(self)
        if len(pargs) == 1 and isinstance(pargs[0], types.FunctionType):
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
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
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
        """Returns the output of the quantity_noun() function using the number
        of elements in the dictionary as the quantity."""
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
                return capitalize_func(output)
            return output
        output = noun_singular(the_noun)
        if 'article' in kwargs and kwargs['article']:
            output = indefinite_article(output, language=language)
        elif 'this' in kwargs and kwargs['this']:
            output = this(output, language=language)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
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
        items = {}
        for key, val in self.elements.items():
            if val is None:
                continue
            if complete_attribute is not None:
                should_skip = False
                for attrib in self._complete_attributes(complete_attribute):
                    if not complex_hasattr(val, attrib):
                        should_skip = True
                        break
                if should_skip:
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

    def _complete_attributes(self, complete_attribute=None):
        if complete_attribute is None:
            complete_attribute = self.complete_attribute
        if isinstance(complete_attribute, str):
            return [complete_attribute]
        if isinstance(complete_attribute, list):
            return complete_attribute
        if isinstance(complete_attribute, DAList):
            return complete_attribute.elements
        return []

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
                    elif isinstance(self.new_object_type, type):
                        object_type_to_use = self.new_object_type
                        parameters_to_use = {}
                    else:
                        raise Exception("new_object_type must be an object type")
                    self.elements[key] = object_type_to_use(self.instanceName + '[' + repr(key) + ']', **parameters_to_use)
            if hasattr(self, 'new_object_type'):
                delattr(self, 'new_object_type')
        for key in keys:
            elem = self.elements[key]
            if item_object_type is not None and complete_attribute is not None:
                for attrib in self._complete_attributes(complete_attribute):
                    complex_getattr(elem, attrib)
            else:
                str(elem)

    def gathered_and_complete(self):
        """Ensures all items in the dictionary are complete and then returns True."""
        if not hasattr(self, 'doing_gathered_and_complete'):
            self.doing_gathered_and_complete = True
            if self.complete_attribute == 'complete':
                for item in list(self.elements.values()):
                    if hasattr(item, 'complete'):
                        try:
                            delattr(item, 'complete')
                        except:
                            pass
            if hasattr(self, 'gathered'):
                del self.gathered
        if self.auto_gather:
            self.gather()
        else:
            self.hook_on_gather()
            self.gathered  # pylint: disable=pointless-statement
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
            new_item_parameters = {}
        if complete_attribute is None and self.complete_attribute is not None:
            complete_attribute = self.complete_attribute
        docassemble.base.functions.set_gathering_mode(True, self.instanceName)
        self._validate(item_object_type, complete_attribute, keys=keys)
        if number is None and self.ask_number:
            if hasattr(self, 'there_are_any') and not self.there_are_any:
                number = 0
            else:
                number = int(self.target_number)
        if minimum is None:
            minimum = self.minimum_number
        if number is None and (minimum is None or minimum == 0):
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
                # logmessage("0gather " + self.instanceName + ": del on there_is_another")
                delattr(self, 'there_is_another')
        while (number is not None and len(self.elements) < int(number)) or (minimum is not None and len(self.elements) < int(minimum)) or (self.ask_number is False and minimum != 0 and (self.there_is_another or (hasattr(self, 'there_is_one_other') and self.there_is_one_other))):
            if item_object_type is not None:
                self.initializeObject(self.new_item_name, item_object_type, **new_item_parameters)
                if hasattr(self, 'there_is_one_other'):
                    delattr(self, 'there_is_one_other')
                elif hasattr(self, 'there_is_another'):
                    # logmessage("1gather " + self.instanceName + ": del on there_is_another")
                    delattr(self, 'there_is_another')
                self._new_item_init_callback()
                if hasattr(self, 'new_item_name'):
                    delattr(self, 'new_item_name')
            else:
                self.new_item_name  # pylint: disable=pointless-statement
                if hasattr(self, 'new_item_value'):
                    self.elements[self.new_item_name] = self.new_item_value
                    delattr(self, 'new_item_value')
                    delattr(self, 'new_item_name')
                    if hasattr(self, 'there_is_one_other'):
                        delattr(self, 'there_is_one_other')
                    elif hasattr(self, 'there_is_another'):
                        # logmessage("2gather " + self.instanceName + ": del on there_is_another")
                        delattr(self, 'there_is_another')
                else:
                    the_name = self.new_item_name
                    self.__getitem__(the_name)  # pylint: disable=unnecessary-dunder-call
                    if hasattr(self, 'new_item_name'):
                        delattr(self, 'new_item_name')
                    if hasattr(self, 'there_is_one_other'):
                        delattr(self, 'there_is_one_other')
                    elif hasattr(self, 'there_is_another'):
                        # logmessage("3gather " + self.instanceName + ": del on there_is_another")
                        delattr(self, 'there_is_another')
            if hasattr(self, 'there_is_one_other'):
                delattr(self, 'there_is_one_other')
            elif hasattr(self, 'there_is_another'):
                # logmessage("4gather " + self.instanceName + ": del on there_is_another")
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
                for attrib in self._complete_attributes():
                    complex_getattr(elem, attrib)
            else:
                str(elem)

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
            if self.object_type is None or docassemble.base.functions.this_thread.probing:
                var_name = object.__getattribute__(self, 'instanceName') + "[" + repr(index) + "]"
                raise DAIndexError("name '" + var_name + "' is not defined")
            self.initializeObject(index, self.object_type, **self.object_type_parameters)
            return self.elements[index]
        return self.elements[index]

    def __setitem__(self, key, the_value):
        self.elements[key] = the_value

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
                self.elements.update(other_dict.elements)
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
        return key in self.elements

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
        return int(self.target_number)

    def __len__(self):
        if self.ask_number:
            return self._target_or_actual()
        self._trigger_gather()
        return self.elements.__len__()

    def __reversed__(self):
        self._trigger_gather()
        return self.elements.__reversed__()

    def __delitem__(self, key):
        self[key]  # pylint: disable=pointless-statement
        return self.elements.__delitem__(key)

    def __missing__(self, key):
        return self.elements.__missing__(key)
    # def __hash__(self):
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
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Returns them, or the pronoun for the only element."""
        if self.number() == 1:
            self._trigger_gather()
            return list(self.elements.values())[0].pronoun(**kwargs)
        output = word('them', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

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
                items += [dict(action='_da_undefine', arguments=dict(variables=[item.instanceName + '.complete']))]
            if len(the_args) > 0:
                items += [{'follow up': [item.instanceName + ('' if y.startswith('[') else '.') + y for y in the_args]}]
            else:
                items += [{'follow up': [self.instanceName + '[' + repr(index) + ']']}]
            if self.complete_attribute is not None and self.complete_attribute != 'complete':
                items += [dict(action='_da_define', arguments=dict(variables=[item.instanceName + '.' + attrib for attrib in self._complete_attributes()]))]
            if ensure_complete:
                items += [dict(action='_da_dict_ensure_complete', arguments=dict(group=self.instanceName))]
            output += '<a href="' + docassemble.base.functions.url_action('_da_dict_edit', items=items) + '" role="button" class="btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('edit', 'secondary') + ' btn-darevisit"><i class="fas fa-pencil-alt"></i> ' + word('Edit') + '</a> '
        if use_delete and can_delete:
            if kwargs.get('confirm', False):
                areyousure = ' daremovebutton'
            else:
                areyousure = ''
            output += '<a href="' + docassemble.base.functions.url_action('_da_dict_remove', dict=self.instanceName, item=repr(index)) + '" role="button" class="btn btn-sm ' + server.button_class_prefix + server.daconfig['button colors'].get('delete', 'danger') + ' btn-darevisit' + areyousure + '"><i class="fas fa-trash"></i> ' + word('Delete') + '</a>'
        if kwargs.get('edit_url_only', False):
            return docassemble.base.functions.url_action('_da_dict_edit', items=items)
        if kwargs.get('delete_url_only', False):
            return docassemble.base.functions.url_action('_da_dict_remove', dict=self.instanceName, item=repr(index))
        return output

    def add_action(self, label=None, message=None, url_only=False, icon='plus-circle', color=None, size='sm', block=None, classname=None):  # pylint: disable=redefined-outer-name
        """Returns HTML for adding an item to a dict"""
        if color is None:
            color = server.daconfig['button colors'].get('add', 'secondary')
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
        return '<a href="' + docassemble.base.functions.url_action('_da_dict_add', dict=self.instanceName) + '" class="btn' + size + block + ' ' + server.button_class_prefix + color + classname + '">' + icon + str(message) + '</a>'

    def _new_elements(self):
        return {}

    def hook_on_gather(self, *pargs, **kwargs):
        """Code that runs just before a dictionary is marked as gathered."""

    def hook_after_gather(self, *pargs, **kwargs):
        """Code that runs just after a dictionary is marked as gathered."""

    def hook_on_item_complete(self, item, *pargs, **kwargs):
        """Code that runs when an item is marked as complete."""

    def hook_on_remove(self, item, *pargs, **kwargs):
        """Code that runs when an item is removed from the dictionary."""

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
        super().init(*pargs, **kwargs)

    def gathered_and_complete(self):
        """Ensures all items in the set are complete and then returns True."""
        if not hasattr(self, 'doing_gathered_and_complete'):
            self.doing_gathered_and_complete = True
            if hasattr(self, 'complete_attribute') and self.complete_attribute == 'complete':
                for item in self.elements:
                    if hasattr(item, 'complete'):
                        try:
                            delattr(item, 'complete')
                        except:
                            pass
            if hasattr(self, 'gathered'):
                del self.gathered
        if self.auto_gather:
            self.gather()
        else:
            self.hook_on_gather()
            self.gathered  # pylint: disable=pointless-statement
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
                should_skip = False
                for attrib in self._complete_attributes(complete_attribute):
                    if not complex_hasattr(item, attrib):
                        should_skip = True
                        break
                if should_skip:
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
        if len(pargs) > 0:
            new_instance_name = pargs[0]
        else:
            new_instance_name = self.instanceName
        new_set = self.copy_shallow(new_instance_name)
        new_set.elements = new_elements
        new_set.gathered = True
        if len(new_set.elements) == 0:
            new_set.there_are_any = False
        return new_set

    def _trigger_gather(self):
        """Triggers the gathering process."""
        if docassemble.base.functions.get_gathering_mode(self.instanceName) is False:
            if self.auto_gather:
                self.gather()
            else:
                self.gathered  # pylint: disable=pointless-statement

    def reset_gathered(self, recursive=False, only_if_empty=False, mark_incomplete=False):
        """Indicates that there is more to be gathered"""
        # logmessage("reset_gathered: " + self.instanceName + ": del on there_is_another")
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
            for attrib in self._complete_attributes():
                for item in list(self.elements):
                    if complex_hasattr(item, attrib):
                        try:
                            complex_delattr(item, attrib)
                        except:
                            pass
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
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            if self.number() > 1:
                tense = 'ppl'
            else:
                tense = '3sgp'
            return verb_past(the_verb, tense, language=language)
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
        """Returns the output of the quantity_noun() function using the number
        of elements in the set as the quantity."""
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
                return capitalize_func(output)
            return output
        output = noun_singular(the_noun)
        if 'article' in kwargs and kwargs['article']:
            output = indefinite_article(output, language=language)
        elif 'this' in kwargs and kwargs['this']:
            output = this(output, language=language)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output, language=language)
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
                number = int(self.target_number)
        if minimum is None:
            minimum = self.minimum_number
        if number is None and (minimum is None or minimum == 0):
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
                # logmessage("gather: " + self.instanceName + ": del on there_is_another")
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
        return int(self.target_number)

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
        return hash((self.instanceName,))

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
        return self.__class__(elements=self.elements.union(setify(other_set)))

    def intersection(self, other_set):
        """Returns a Python set consisting of the elements of the current set
        that also exist in the other_set.

        """
        self._trigger_gather()
        return self.__class__(elements=self.elements.intersection(setify(other_set)))

    def difference(self, other_set):
        """Returns a Python set consisting of the elements of the current set
        that do not exist in the other_set.

        """
        self._trigger_gather()
        return self.__class__(elements=self.elements.difference(setify(other_set)))

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
            return capitalize_func(output)
        return output

    def pronoun(self, **kwargs):
        """Returns them, or the pronoun for the one element."""
        if self.number() == 1:
            self._trigger_gather()
            return list(self.elements)[0].pronoun(**kwargs)
        output = word('them', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize_func(output)
        return output

    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

    def pronoun_subjective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

    def hook_on_gather(self, *pargs, **kwargs):
        """Code that runs just before a set is marked as gathered."""

    def hook_after_gather(self, *pargs, **kwargs):
        """Code that runs just after a set is marked as gathered."""

    def hook_on_item_complete(self, item, *pargs, **kwargs):
        """Code that runs when an item is marked as complete."""

    def hook_on_remove(self, item, *pargs, **kwargs):
        """Code that runs when an item is removed from the set."""

    def __eq__(self, other):
        self._trigger_gather()
        return self.elements == other


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
            self.initialized = True
        else:
            self.ok = False
        if hasattr(self, 'extension') and self.extension == 'pdf':
            if 'make_thumbnail' in kwargs and kwargs['make_thumbnail']:
                self._make_pdf_thumbnail(kwargs['make_thumbnail'])
            if 'make_pngs' in kwargs and kwargs['make_pngs']:
                self._make_pngs_for_pdf()

    def convert_to(self, output_extension, output_to=None):
        """Converts the file in-place to a different file extension."""
        if output_to is None:
            output_to = self
        elif isinstance(output_to, DAFileList):
            output_to = output_to.elements[0]
        if not isinstance(output_to, DAFile):
            raise Exception("convert_to: output_to must be a DAFile")
        self.retrieve()
        if hasattr(self, 'extension'):
            input_extension = self.extension
        elif hasattr(self, 'filename'):
            input_extension, input_mimetype = server.get_ext_and_mimetype(self.filename)  # pylint: disable=assignment-from-none,unpacking-non-sequence,unused-variable
        else:
            raise Exception("DAFile.convert: could not identify file type")
        output_extension = output_extension.strip().lower()
        if output_to is self and output_extension == input_extension:
            return
        if hasattr(self, 'filename'):
            output_filename = re.sub(r'\.[^\.]+$', '.' + output_extension, self.filename)
        else:
            output_filename = 'file.' + output_extension
        input_path = self.path()
        if output_to is self:
            temp_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=input_extension, delete=False)
            shutil.copyfile(input_path, temp_file.name)
            input_path = temp_file.name
        output_to.initialize(extension=output_extension, filename=output_filename, reinitialize=output_to.ok)
        if input_extension == output_extension:
            shutil.copyfile(input_path, output_to.path())
        elif input_extension in ("docx", "doc", "odt", "rtf", "png", "jpg", "tif") and output_extension == "pdf":
            shutil.copyfile(docassemble.base.pandoc.concatenate_files([input_path]), output_to.path())
        elif input_extension in ("docx", "doc", "odt", "rtf") and output_extension in ("docx", "doc", "odt", "rtf"):
            if not docassemble.base.pandoc.convert_file(input_path, output_to.path(), input_extension, output_extension):
                raise DAError("Could not convert file")
        elif input_extension in ("docx", "doc", "odt", "rtf") and output_extension == 'md':
            result = docassemble.base.pandoc.word_to_markdown(input_path, input_extension)
            if result is None:
                raise DAError("Could not convert file")
            shutil.copyfile(result.name, output_to.path())
        elif input_extension in ("png", "jpg", "tif") and output_extension in ("png", "jpg", "tif"):
            the_image = Image.open(input_path)
            if input_extension == 'png':
                rgb_image = the_image.convert('RGB')
                rgb_image.save(output_to.path())
            else:
                the_image.save(output_to.path())
        else:
            raise Exception("DAFile.convert: could not identify file type")
        output_to.commit()
        output_to.retrieve()

    def fix_up(self):
        """Makes corrections to the file and changes it in-place if necessary.
        Raises an exception if the file is corrupt and cannot be fixed."""
        if not self.ok and not hasattr(self, 'content'):
            self.initialized  # pylint: disable=pointless-statement
        if hasattr(self, 'extension'):
            if self.extension == 'pdf':
                docassemble.base.pdftk.apply_qpdf(self.path())
            elif self.extension == 'gif':
                fix_gif(self.path())
            elif self.extension == 'png':
                fix_png(self.path())
            elif self.extension == 'jpg':
                fix_jpg(self.path())
            elif self.extension == 'docx':
                fix_docx(self.path())
            elif self.extension in ('odt', 'doc', 'rtf'):
                fix_word_processing(self.path(), self.extension)

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
        # logmessage("initialize")
        to_delete = []
        for key, val in kwargs.items():
            if val is None:
                to_delete.append(key)
        for key in to_delete:
            del kwargs[key]
        if kwargs.get('reinitialize', False):
            if hasattr(self, 'mimetype'):
                del self.mimetype
            if hasattr(self, 'extension'):
                del self.extension
            if hasattr(self, 'filename'):
                del self.filename
            if hasattr(self, 'number'):
                server.SavedFile(self.number).delete()
                del self.number
            self.ok = False
            if hasattr(self, 'initialized'):
                del self.initialized
            self.has_specific_filename = False
            if hasattr(self, 'file_info'):
                del self.file_info
            for prefix in ('page', 'screen'):
                if hasattr(self, '_task' + prefix):
                    delattr(self, '_task' + prefix)
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
        if 'number' in kwargs:
            self.number = kwargs['number']
            self.ok = True
        if not hasattr(self, 'filename'):
            if hasattr(self, 'extension'):
                self.filename = kwargs.get('filename', 'file.' + self.extension)
            else:
                self.filename = kwargs.get('filename', 'file.txt')
        docassemble.base.filter.ensure_valid_filename(self.filename)
        if hasattr(self, 'number'):
            should_not_exist = False
        else:
            yaml_filename = None
            uid = None
            if hasattr(docassemble.base.functions.this_thread, 'current_info'):
                yaml_filename = docassemble.base.functions.this_thread.current_info.get('yaml_filename', None)
            uid = docassemble.base.functions.get_uid()
            self.number = server.get_new_file_number(uid, self.filename, yaml_file_name=yaml_filename)  # pylint: disable=assignment-from-none
            self.ok = True
            self.extension, self.mimetype = server.get_ext_and_mimetype(self.filename)  # pylint: disable=assignment-from-none,unpacking-non-sequence
            should_not_exist = True
        self.retrieve()
        the_path = self.path()
        if not (os.path.isfile(the_path) or os.path.islink(the_path)):
            sf = server.SavedFile(self.number, extension=self.extension, fix=True, should_not_exist=should_not_exist)
            sf.save()
        self.initialized = True

    def retrieve(self):
        """Ensures that the file is ready to be used."""
        if not self.ok:
            self.initialize()
        if not hasattr(self, 'number'):
            raise Exception("Cannot retrieve a file without a file number.")
        docassemble.base.functions.this_thread.open_files.add(self)
        # logmessage("Retrieve: calling file finder")
        if self.has_specific_filename:
            self.file_info = server.file_number_finder(self.number, filename=self.filename)
        else:
            self.file_info = server.file_number_finder(self.number)
        if self.file_info is None:
            raise Exception("Could not retrieve file " + str(self.number))
        if 'path' not in self.file_info:
            raise Exception("Could not retrieve file: " + repr(self.file_info))
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
            with open(the_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            with open(the_path, 'rb') as f:
                return f.read()

    def readlines(self):
        """Returns the contents of the file."""
        self.retrieve()
        the_path = self.path()
        if not os.path.isfile(the_path):
            raise Exception("File does not exist yet.")
        with open(the_path, 'r', encoding='utf-8') as f:
            return f.readlines()

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
        if isinstance(other_file, (DAFile, DAFileList, DAFileCollection, DAStaticFile)):
            filepath = other_file.path()
        else:
            filepath = other_file
        self.retrieve()
        shutil.copyfile(filepath, self.file_info['path'])
        self.retrieve()

    def extract_pages(self, first=None, last=None, output_to=None):
        if first is None:
            first = 1
        elif not isinstance(first, int):
            raise Exception("extract_pages: first must be an integer")
        if first < 1:
            raise Exception("extract_pages: first must be 1 or greater")
        if last is None:
            last = ''
        elif not isinstance(last, int):
            raise Exception("extract_pages: last must be an integer")
        elif last < first:
            raise Exception("extract_pages: last must greater than or equal to first")
        self.retrieve()
        if output_to is None:
            output_to = DAFile()
            output_to.set_random_instance_name()
        elif isinstance(output_to, DAFileList):
            output_to = output_to.elements[0]
        else:
            raise Exception("extract_pages: output_to must be a DAFile")
        input_filename = self.filename
        input_path = self.path()
        if output_to is self:
            temp_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
            shutil.copyfile(input_path, temp_file.name)
            input_path = temp_file.name
        output_to.initialize(extension='pdf', filename=input_filename, reinitialize=output_to.ok)
        try:
            docassemble.base.pdftk.extract_pages(input_path, output_to.path(), first, last)
        except Exception as err:
            raise Exception("extract_pages: " + str(err))
        output_to.retrieve()
        output_to.commit()
        return output_to

    def bates_number(self, *pargs, **kwargs):
        """Makes the contents of the file a Bates-numbered of the file or, if provided, another file."""
        docs = []
        all_pdf = True
        for other_file in pargs:
            if isinstance(other_file, DAFileList):
                for other_file_sub in other_file.elements:
                    if not other_file._is_pdf():
                        all_pdf = False
                    docs.append(other_file_sub)
            elif isinstance(other_file, DAFileCollection):
                if not hasattr(other_file, 'pdf'):
                    raise DAError('bates_number: DAFileCollection object did not have pdf attribute.')
                docs.append(other_file.pdf)
            elif isinstance(other_file, DAStaticFile):
                if not other_file._is_pdf():
                    all_pdf = False
                docs.append(other_file)
            else:
                all_pdf = False
                docs.append(other_file)
        if len(docs) == 0:
            if not self._is_pdf():
                all_pdf = False
            docs.append(self)
        if not all_pdf:
            docs = [pdf_concatenate(docs).path()]
        filename = kwargs.get('filename', None)
        prefix = kwargs.get('prefix', 'TEST')
        digits = kwargs.get('digits', 5)
        start = kwargs.get('start', 1)
        area = kwargs.get('area', None)
        if area is None:
            area = 'BOTTOM_RIGHT'
        if area not in ('TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_RIGHT', 'BOTTOM_LEFT'):
            raise DAError("bates_number: area must be one of TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, or BOTTOM_LEFT")
        if filename is None:
            filename = 'file.pdf'
        args = [os.path.join(server.daconfig['modules'], 'bin', 'python'), '-m', 'docassemble.base.bates', '--prefix', str(prefix), '--digits', str(digits), '--start', str(start), '--area', area]
        for doc in docs:
            if isinstance(doc, str):
                args.append(doc)
            else:
                args.append(doc.path())
        the_dir = tempfile.mkdtemp(prefix='SavedFile')
        try:
            result = subprocess.run(args, cwd=the_dir, timeout=300, check=False).returncode
        except subprocess.TimeoutExpired:
            logmessage("bates_number: took too long")
            result = 1
        if result != 0:
            raise DAError("bates_number: failure during processing; return value " + str(result) + " after " + ' '.join(args))
        outfiles = [os.path.join(the_dir, f) for f in os.listdir(the_dir) if f.endswith('.pdf')]
        if len(outfiles) == 0:
            raise DAError("bates_number: no files found in " + the_dir)
        self.initialize(filename=filename, extension='pdf', mimetype='application/pdf', reinitialize=True)
        if len(outfiles) > 1:
            shutil.copyfile(pdf_concatenate(sorted(outfiles)).path(), self.file_info['path'])
        else:
            shutil.copyfile(outfiles[0], self.file_info['path'])
        del self.file_info
        self._make_pdf_thumbnail(1)
        self.commit()
        self.retrieve()

    def make_ocr_pdf(self, *pargs, **kwargs):
        """Makes the contents of the file an OCRed PDF of the file or, if provided, another file."""
        lang = get_ocr_language(kwargs.get('language', None))
        ocr_pdf(*pargs, target=self, filename=kwargs.get('filename', None), lang=lang, psm=kwargs.get('psm', None), preserve_color=kwargs.get('preserve_color', False))

    def make_ocr_pdf_in_background(self, *pargs, **kwargs):
        """In the background, makes the contents of the file an OCRed PDF of the file or, if provided, another file."""
        lang = get_ocr_language(kwargs.get('language', None))
        args = dict(yaml_filename=docassemble.base.functions.this_thread.current_info['yaml_filename'], user=docassemble.base.functions.this_thread.current_info['user'], user_code=docassemble.base.functions.this_thread.current_info['session'], secret=docassemble.base.functions.this_thread.current_info['secret'], url=docassemble.base.functions.this_thread.current_info['url'], url_root=docassemble.base.functions.this_thread.current_info['url_root'], language=lang, psm=kwargs.get('psm', None), x=None, y=None, W=None, H=None, extra=None, message=None, pdf=True, preserve_color=kwargs.get('preserve_color', False), target=self, dafilelist=kwargs.get('dafilelist', None), filename=kwargs.get('filename', None))
        collector = server.ocr_finalize.s(**args)
        docs = []
        for parg in pargs:
            if isinstance(parg, DAFileList):
                docs.extend(parg.elements)
            elif isinstance(parg, list):
                docs.extend(parg)
            else:
                docs.append(parg)
        todo = []
        indexno = 0
        for image_file in docs:
            if hasattr(image_file, 'extension') and image_file.extension in ('docx', 'doc', 'odt', 'rtf'):
                todo.append(server.ocr_dummy.s(image_file, indexno, **args))
                indexno += 1
            elif hasattr(image_file, 'extension') and image_file._is_pdf() and hasattr(image_file, 'has_ocr') and image_file.has_ocr:
                todo.append(server.ocr_dummy.s(image_file, indexno, **args))
                indexno += 1
            else:
                for item in ocr_page_tasks(image_file, **args):
                    todo.append(server.ocr_page.s(indexno, **item))
                    indexno += 1
        if len(todo) == 0:
            if hasattr(self, 'extension') and self.extension in ('docx', 'doc', 'odt', 'rtf'):
                todo.append(server.ocr_dummy.s(self, indexno, **args))
                indexno += 1
            elif self._is_pdf() and hasattr(self, 'has_ocr') and self.has_ocr:
                todo.append(server.ocr_dummy.s(self, indexno, **args))
                indexno += 1
            else:
                for item in ocr_page_tasks(self, **args):
                    todo.append(server.ocr_page.s(indexno, **item))
                    indexno += 1
        the_chord = server.chord(todo)(collector)  # pylint: disable=assignment-from-none
        return the_chord

    def _is_pdf(self):
        if hasattr(self, 'extension') and self.extension.lower() == 'pdf':
            return True
        if hasattr(self, 'mimetype') and self.mimetype == 'application/pdf':
            return True
        return False

    def get_docx_variables(self):
        """Returns a list of variables used by the Jinja2 templating of a DOCX template file."""
        return docassemble.base.parse.get_docx_variables(self.path())

    def get_pdf_fields(self):
        """Returns a list of fields that exist in the PDF document"""
        results = []
        all_items = docassemble.base.pdftk.read_fields(self.path())
        if all_items is not None:
            for item in all_items:
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
        with open(the_path, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.FOLLOWLOCATION, True)
            c.setopt(c.WRITEDATA, f)
            c.setopt(pycurl.USERAGENT, server.daconfig.get('user agent', 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36'))
            c.setopt(pycurl.COOKIEFILE, cookiefile.name)
            c.perform()
            status_code = c.getinfo(pycurl.HTTP_CODE)
            c.close()
        if status_code >= 400:
            raise Exception("from_url: Error %s" % (status_code,))
        self.retrieve()

    def uses_acroform(self):
        """Returns True if the file uses AcroForm, otherwise returns False."""
        if not hasattr(self, 'file_info'):
            self.retrieve()
        return self.file_info.get('acroform', False)

    def is_encrypted(self):
        """Returns True if the file is a PDF file and it is encrypted, otherwise returns False."""
        if not hasattr(self, 'file_info'):
            self.retrieve()
        return self.file_info.get('encrypted', False)

    def _make_pdf_thumbnail(self, page, both_formats=False):
        """Creates a page image for the first page of a PDF file."""
        if not hasattr(self, 'file_info'):
            self.retrieve()
        max_pages = 1 + int(self.file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        the_path = self.file_info['path'] + 'screen-' + (formatter % int(page)) + '.png'
        if not os.path.isfile(the_path):
            server.fg_make_png_for_pdf(self, 'screen', page=page)
        if both_formats:
            the_path = self.file_info['path'] + 'page-' + (formatter % int(page)) + '.png'
            if not os.path.isfile(the_path):
                server.fg_make_png_for_pdf(self, 'page', page=page)

    def pngs_ready(self):
        """Returns True if the PNGs have been generated."""
        self._make_pngs_for_pdf()
        if server.task_ready(self._taskscreen) and server.task_ready(self._taskpage):
            return True
        return False

    def _delete_pngs(self):
        self.retrieve()
        did_something = False
        for prefix in ('page', 'screen'):
            test_path = self.file_info['path'] + prefix + '-in-progress'
            if os.path.isfile(test_path):
                while (os.path.isfile(test_path) and time.time() - os.stat(test_path)[stat.ST_MTIME]) < 10:
                    logmessage("Waiting for test path to go away")
                    if not os.path.isfile(test_path):
                        break
                    time.sleep(1)
                    self.commit()
                    self.retrieve()
            if os.path.isfile(test_path) and hasattr(self, '_task' + prefix):
                server.wait_for_task(getattr(self, '_task' + prefix), timeout=10)
                self.commit()
                self.retrieve()
            if os.path.isfile(test_path):
                did_something = True
                os.remove(test_path)
            if hasattr(self, '_task' + prefix):
                delattr(self, '_task' + prefix)
            the_dir = os.path.dirname(self.file_info['path'])
            to_remove = []
            for f in os.listdir(the_dir):
                the_path = os.path.join(the_dir, f)
                if the_path.endswith('.png') and the_path.startswith(self.file_info['path'] + prefix + '-'):
                    to_remove.append(the_path)
            for file_to_remove in to_remove:
                try:
                    os.remove(file_to_remove)
                    did_something = True
                except:
                    logmessage("Unable to remove png file " + file_to_remove)
        if did_something:
            self.commit()
            self.retrieve()

    def _make_pngs_for_pdf(self):
        if not hasattr(self, '_taskscreen'):
            setattr(self, '_taskscreen', server.make_png_for_pdf(self, 'screen'))
        if not hasattr(self, '_taskpage'):
            setattr(self, '_taskpage', server.make_png_for_pdf(self, 'page'))

    def num_pages(self):
        """Returns the number of pages in the file, if a PDF file, and 1 otherwise"""
        if not self.ok:
            self.initialized  # pylint: disable=pointless-statement
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
        return 1

    def _pdf_page_path(self, page):
        if not self.ok:
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise Exception("Cannot get path of file without a file number.")
        self.retrieve()
        if 'fullpath' not in self.file_info:
            raise Exception("fullpath not found.")
        return self.file_info['path'] + 'page' + str(page) + '.pdf'

    def _path_ready(self, the_path):
        if os.path.isfile(the_path):
            if time.time() - os.stat(the_path)[stat.ST_MTIME] < 3:
                time.sleep(1)
            return True
        return False

    def page_path(self, page, prefix, wait=True):
        """Returns a file path at which a PDF page image can be accessed."""
        if not self.ok:
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise Exception("Cannot get path of file without a file number.")
        self.retrieve()
        if 'fullpath' not in self.file_info:
            raise Exception("fullpath not found.")
        if 'pages' not in self.file_info:
            raise Exception("number of pages not found. " + repr(self.file_info))
        max_pages = 1 + int(self.file_info['pages'])
        formatter = '%0' + str(len(str(max_pages))) + 'd'
        the_path = self.file_info['path'] + prefix + '-' + (formatter % int(page)) + '.png'
        if self._path_ready(the_path):
            return the_path
        test_path = self.file_info['path'] + prefix + '-in-progress'
        # logmessage("Test path is " + test_path)
        if wait and os.path.isfile(test_path):
            while (os.path.isfile(test_path) and time.time() - os.stat(test_path)[stat.ST_MTIME]) < 10:
                if not os.path.isfile(test_path):
                    break
                time.sleep(3)
                self.commit()
                self.retrieve()
                if self._path_ready(the_path):
                    return the_path
        if self._path_ready(the_path):
            return the_path
        if os.path.isfile(test_path) and hasattr(self, '_task' + prefix):
            if wait:
                tries = 4
                while tries > 0:
                    server.wait_for_task(getattr(self, '_task' + prefix))
                    self.commit()
                    self.retrieve()
                    if self._path_ready(the_path):
                        return the_path
                    tries -= 1
            else:
                return None
        if self._path_ready(the_path):
            return the_path
        if hasattr(self, '_task' + prefix):
            if wait:
                tries = 4
                while tries > 0:
                    server.wait_for_task(getattr(self, '_task' + prefix))
                    self.commit()
                    self.retrieve()
                    if self._path_ready(the_path):
                        return the_path
                    tries -= 1
        if wait:
            server.fg_make_png_for_pdf(self, prefix, page=page)
        if os.path.isfile(the_path):
            return the_path
        return None

    def cloud_path(self, filename=None):
        """Returns the path with which the file can be accessed using S3 or Azure Blob Storage, or None if cloud storage is not enabled."""
        if not self.ok and not hasattr(self, 'content'):
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise Exception("Cannot get the cloud path of file without a file number.")
        return server.SavedFile(self.number, fix=False).cloud_path(filename)

    def path(self):
        """Returns a path and filename at which the file can be accessed."""
        # logmessage("path")
        if not self.ok and not hasattr(self, 'content'):
            self.initialized  # pylint: disable=pointless-statement
        if not hasattr(self, 'number'):
            raise Exception("Cannot get path of file without a file number.")
        # if not hasattr(self, 'file_info'):
        self.retrieve()
        if 'fullpath' not in self.file_info:
            raise Exception("fullpath not found.")
        return self.file_info['fullpath']

    def commit(self):
        """Ensures that changes to the file are saved and will be available in
        the future.

        """
        if hasattr(self, 'number'):
            sf = server.SavedFile(self.number, fix=True)
            sf.finalize()

    def show(self, width=None, wait=True, alt_text=None):
        """Inserts markup that displays the file as an image.  Takes
        optional keyword arguments width and alt_text.

        """
        if not self.ok:
            if hasattr(self, 'content'):
                return ''
            self.initialized  # pylint: disable=pointless-statement
        if hasattr(self, 'number') and hasattr(self, 'extension') and self.extension == 'pdf' and wait:
            self.page_path(1, 'page')
        if self.mimetype == 'text/markdown':
            the_template = DATemplate(content=self.slurp())
            return str(the_template)
        if self.mimetype == 'text/plain':
            the_content = self.slurp()
            return the_content
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self, _use_jinja2=False)
            if self.mimetype in ('application/pdf', 'application/rtf', 'application/vnd.oasis.opendocument.text', 'application/msword'):
                return self._pdf_pages(width)
            return docassemble.base.file_docx.image_for_docx(self.number, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width)
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
        return '[FILE ' + str(self.number) + ', ' + the_width + ', ' + the_alt_text + ']'

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
        """Sets attributes of the file stored on the server.  Takes optional keyword arguments private and persistent, which must be boolean values.  Also takes the optional keyword argument filename."""
        if 'private' in kwargs and kwargs['private'] in [True, False]:
            self.private = kwargs['private']
        if 'persistent' in kwargs and kwargs['persistent'] in [True, False]:
            self.persistent = kwargs['persistent']
        if 'filename' in kwargs:
            kwargs['filename'] = server.secure_filename_spaces_ok(kwargs['filename'])
            self.filename = kwargs['filename']
        if 'session' in kwargs:
            del kwargs['session']
        return server.file_set_attributes(self.number, **kwargs)

    def user_access(self, *pargs, **kwargs):
        """Allows or disallows access to the file for a given user."""
        allow_user_id = []
        allow_email = []
        disallow_user_id = []
        disallow_email = []
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
                allow_user_id = []
                allow_email = []
                disallow_all = True
            else:
                if isinstance(disallow, (int, str)):
                    disallow = [disallow]
                if isinstance(disallow, (list, DAList)):
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
        allow = []
        disallow = []
        disallow_all = False
        for item in pargs:
            if isinstance(item, str):
                allow.append(item)
        if 'disallow' in kwargs:
            disallow_arg = kwargs['disallow']
            if disallow_arg == 'all':
                allow = []
                disallow_all = True
            else:
                if isinstance(disallow_arg, str):
                    disallow_arg = [disallow_arg]
                if isinstance(disallow_arg, (list, DAList)):
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
        self.info = {}
        super().init(*pargs, **kwargs)

    def _extension_list(self):
        if hasattr(self, 'info') and 'formats' in self.info:
            return [item for item in self.info['formats'] if item != 'html']
        return ['pdf', 'docx', 'rtf']

    def fix_up(self):
        """Makes corrections to the files and changes them in-place if necessary.
        Raises an exception if a file is corrupt and cannot be fixed."""
        for ext in self._extension_list():
            if hasattr(self, ext):
                getattr(self, ext).fix_up()

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

    def uses_acroform(self):
        """Returns True if there is a PDF file and it uses AcroForm, otherwise returns False."""
        if hasattr(self, 'pdf'):
            return self.pdf.uses_acroform()
        return False

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
        if hasattr(self, 'docx'):
            return self.docx.get_docx_variables()
        return None

    def get_pdf_fields(self):
        """Returns a list of fields that exist in the PDF document"""
        if hasattr(self, 'pdf'):
            return self.pdf.get_pdf_fields()
        return None

    def url_for(self, **kwargs):
        """Returns a URL to one of the attachments in the collection."""
        for ext in self._extension_list():
            if hasattr(self, ext):
                return getattr(self, ext).url_for(**kwargs)
        raise Exception("Could not find a file within a DACollection.")

    def set_attributes(self, **kwargs):
        """Sets attributes of the file(s) stored on the server.  Takes optional keyword arguments private and persistent, which must be boolean values."""
        if 'filename' in kwargs:
            del kwargs['filename']
        for ext in self._extension_list():
            if hasattr(self, ext):
                getattr(self, ext).set_attributes(**kwargs)

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
            if isinstance(the_file, (InlineImage, Subdoc)):
                return the_file
        return ' '.join(the_files)

    def extract_pages(self, first=None, last=None):
        """Extracts a page range from a PDF file and returns a new PDF file"""
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call extract_pages() on a DAFileCollection object without a pdf attribute.")
        return self.pdf.extract_pages(first=first, last=last)

    def bates_number(self, **kwargs):
        """Makes the contents of the pdf file a Bates-numbered PDF."""
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call bates_number() on a DAFileCollection object without a pdf attribute.")
        self.pdf.bates_number(**kwargs)

    def make_ocr_pdf(self, **kwargs):
        """Makes the contents of the pdf file an OCRed PDF."""
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call make_ocr_pdf() on a DAFileCollection object without a pdf attribute.")
        self.pdf.make_ocr_pdf(**kwargs)

    def make_ocr_pdf_in_background(self, **kwargs):
        """In the background, makes the contents of the pdf file an OCRed PDF."""
        if not hasattr(self, 'pdf'):
            raise DAError("Cannot call make_ocr_pdf_in_background() on a DAFileCollection object without a pdf attribute.")
        return self.pdf.make_ocr_pdf_in_background(**kwargs)

    def __str__(self):
        return str(self._first_file())


class DAFileList(DAList):
    """Used internally by docassemble to refer to a list of files, such as
    a list of files uploaded to a single variable.

    """

    def __str__(self):
        return str(self.show())

    def fix_up(self):
        """Makes corrections to the files and changes them in-place if necessary.
        Raises an exception if a file is corrupt and cannot be fixed."""
        for item in self.elements:
            item.fix_up()

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
        result = 0
        for element in sorted(self.elements):
            if element.ok:
                result += element.num_pages()
        return result

    def uses_acroform(self):
        """Returns True if the first file is a PDF file and it uses AcroForm, otherwise returns False."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].uses_acroform()

    def is_encrypted(self):
        """Returns True if the first file is a PDF file and it is encrypted, otherwise returns False."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].is_encrypted()

    def convert_to(self, output_extension, output_to=None):
        """Converts each file in-place to a different file extension."""
        for element in self.elements:
            element.convert_to(output_extension, output_to=output_to)

    def size_in_bytes(self):
        """Returns the number of bytes in the first file."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].size_in_bytes()

    def slurp(self, auto_decode=True):
        """Returns the contents of the first file."""
        if len(self.elements) == 0:
            return None
        return self.elements[0].slurp(auto_decode=auto_decode)

    def show(self, width=None, alt_text=None):
        """Inserts markup that displays each element in the list as an image.
        Takes optional keyword arguments width and alt_text.

        """
        output = ''
        for element in sorted(self.elements):
            if element.ok:
                new_image = element.show(width=width, alt_text=alt_text)
                if isinstance(new_image, (InlineImage, Subdoc)):
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
        if 'filename' in kwargs:
            del kwargs['filename']
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

    def extract_pages(self, first=None, last=None):
        """Extracts a page range from a PDF file and returns a new PDF file"""
        return self.elements[0].extract_pages(first=first, last=last)

    def bates_number(self, **kwargs):
        """Makes the contents of the first file a Bates-numbered PDF of the list of files."""
        if len(self.elements) == 0:
            return
        if len(self.elements) > 1:
            self.elements[0].bates_number(self, **kwargs)
            self.elements = [self.elements[0]]
        else:
            self.elements[0].bates_number(self.elements[0], **kwargs)
        return

    def make_ocr_pdf(self, **kwargs):
        """Makes the contents of the first file an OCRed PDF of the list of files."""
        if len(self.elements) == 0:
            return
        if len(self.elements) > 1:
            self.elements[0].make_ocr_pdf(self, **kwargs)
            self.elements = [self.elements[0]]
        else:
            self.elements[0].make_ocr_pdf(**kwargs)

    def make_ocr_pdf_in_background(self, **kwargs):
        """Makes the contents of the first file an OCRed PDF of the list of files."""
        if len(self.elements) == 0:
            return None
        if len(self.elements) > 1:
            kwargs['dafilelist'] = self
            return self.elements[0].make_ocr_pdf_in_background(self, **kwargs)
        return self.elements[0].make_ocr_pdf_in_background(**kwargs)


class DAStaticFile(DAObject):

    def init(self, *pargs, **kwargs):
        if 'filename' in kwargs and 'mimetype' not in kwargs and 'extension' not in kwargs:
            self.extension, self.mimetype = server.get_ext_and_mimetype(kwargs['filename'])  # pylint: disable=assignment-from-none,unpacking-non-sequence
        self.package = docassemble.base.functions.this_thread.current_question.package
        super().init(*pargs, **kwargs)

    def _populate(self):
        if not hasattr(self, 'extension') or not hasattr(self, 'mimetype'):
            self.extension, self.mimetype = server.get_ext_and_mimetype(self.filename)  # pylint: disable=assignment-from-none,unpacking-non-sequence

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

    def _get_unqualified_reference(self):
        self._populate()
        if ':' not in self.filename and hasattr(self, 'package'):
            file_reference = self.package + ':'
            if '/' not in str(self.filename):
                file_reference += 'data/static/'
            file_reference += str(self.filename)
            return file_reference
        return str(self.filename)

    def show(self, width=None, alt_text=None):
        """Inserts markup that displays the file.  Takes optional keyword
        arguments width and alt_text.

        """
        self._populate()
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            if self.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return docassemble.base.file_docx.include_docx_template(self)
            if self.mimetype in ('application/pdf', 'application/rtf', 'application/vnd.oasis.opendocument.text', 'application/msword'):
                return self._pdf_pages(width)
            the_text = docassemble.base.file_docx.image_for_docx(docassemble.base.functions.DALocalFile(self.path()), docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None), width=width)
            return the_text
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
        return '[FILE ' + self._get_unqualified_reference() + ', ' + the_width + ', ' + the_alt_text + ']'

    def _pdf_pages(self, width):
        file_info = {}
        pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".pdf", delete=False)
        file_info['fullpath'] = pdf_file.name
        file_info['extension'] = 'pdf'
        file_info['path'] = os.path.splitext(pdf_file.name)[0]
        shutil.copyfile(self.path(), pdf_file.name)
        return docassemble.base.file_docx.pdf_pages(file_info, width)

    def uses_acroform(self):
        """Returns True if the file is a PDF file and it uses AcroForm, otherwise returns False."""
        file_info = server.file_finder(self._get_unqualified_reference())
        return file_info.get('acroform', False)

    def is_encrypted(self):
        """Returns True if the file is a PDF file and it is encrypted, otherwise returns False."""
        file_info = server.file_finder(self._get_unqualified_reference())
        return file_info.get('encrypted', False)

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
            with open(the_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            with open(the_path, 'rb') as f:
                return f.read()

    def path(self):
        """Returns a path and filename at which the file can be accessed.

        """
        file_info = server.file_finder(self._get_unqualified_reference())
        return file_info.get('fullpath', None)

    def get_docx_variables(self):
        """Returns a list of variables used by the Jinja2 templating of a DOCX template file."""
        return docassemble.base.parse.get_docx_variables(self.path())

    def get_pdf_fields(self):
        """Returns a list of fields that exist in the PDF document"""
        results = []
        all_items = docassemble.base.pdftk.read_fields(self.path())
        if all_items is not None:
            for item in all_items:
                the_type = re.sub(r'[^/A-Za-z]', '', str(item[4]))
                if the_type == 'None':
                    the_type = None
                result = (item[0], '' if item[1] == 'something' else item[1], item[2], item[3], the_type, item[5])
                results.append(result)
        return results

    def url_for(self, **kwargs):
        """Returns a URL to the static file."""
        the_args = {}
        for key, val in kwargs.items():
            the_args[key] = val
        if 'external' in kwargs:
            the_args['_external'] = kwargs['external']
            del the_args['external']
        if 'attachment' in kwargs:
            the_args['_attachment'] = kwargs['attachment']
            del the_args['attachment']
        the_args['question'] = docassemble.base.functions.this_thread.current_question
        return server.url_finder(self._get_unqualified_reference(), **the_args)

    def _is_pdf(self):
        if hasattr(self, 'extension') and self.extension.lower() == 'pdf':
            return True
        if hasattr(self, 'mimetype') and self.mimetype == 'application/pdf':
            return True
        return False

    def __str__(self):
        return str(self.show())


class DAEmailRecipientList(DAList):
    """Represents a list of DAEmailRecipient objects."""

    def init(self, *pargs, **kwargs):
        # logmessage("DAEmailRecipientList: pargs is " + str(pargs) + " and kwargs is " + str(kwargs))
        self.object_type = DAEmailRecipient
        super().init(**kwargs)
        for parg in pargs:
            if isinstance(parg, list):
                # logmessage("DAEmailRecipientList: parg type is list")
                for item in parg:
                    self.appendObject(DAEmailRecipient, **item)
            elif isinstance(parg, dict):
                # logmessage("DAEmailRecipientList: parg type is dict")
                self.appendObject(DAEmailRecipient, **parg)


class DAEmailRecipient(DAObject):
    """An object type used within DAEmail objects to represent a single
    e-mail address and the name associated with that e-mail address.

    """

    def init(self, *pargs, **kwargs):
        # logmessage("DAEmailRecipient: pargs is " + str(pargs) + " and kwargs is " + str(kwargs))
        if 'address' in kwargs:
            self.address = kwargs['address']
            del kwargs['address']
        if 'name' in kwargs:
            self.name = kwargs['name']
            del kwargs['name']
        super().init(*pargs, **kwargs)

    def email_address(self, include_name=None):
        """Returns a properly formatted e-mail address for the recipient."""
        if hasattr(self, 'empty') and self.empty:
            return ''
        if include_name is True or (include_name is not False and self.name is not None and self.name != ''):
            return '"' + nodoublequote(self.name) + '" <' + str(self.address) + '>'
        return str(self.address)

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
        return 'This is an e-mail'


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
        self.decorations = []
        if 'decorations' in kwargs:
            for decoration in kwargs['decorations']:
                if decoration and decoration != '':
                    self.decorations.append(decoration)

    def show(self, **kwargs):  # pylint: disable=unused-argument
        """Displays the contents of the template."""
        return str(self)

    def show_as_markdown(self, **kwargs):  # pylint: disable=unused-argument
        """Displays the contents of the template."""
        return str(self.content)

    def __str__(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            content = self.content
            content = re.sub(r'\\_', r'\\\\_', content)
            return str(docassemble.base.file_docx.markdown_to_docx(content, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None)))
        return str(self.content)


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
    # logmessage("i is " + str(user_dict_copy['i']))
    header_output = [table_safe(x.text(user_dict_copy)) for x in table_info.header]
    if table_info.is_editable and not editable:
        header_output.pop()
    the_iterable = eval(table_info.row, user_dict_copy)
    if (not isinstance(the_iterable, (DAList, DADict, abc.Iterable))) or isinstance(the_iterable, str):
        raise DAError("Error in processing table " + table_info.saveas + ": row value is not iterable")
    if hasattr(the_iterable, 'instanceName') and hasattr(the_iterable, 'elements') and isinstance(the_iterable.elements, (list, dict)):
        if not table_info.require_gathered:
            the_iterable = the_iterable.complete_elements()
        elif table_info.show_incomplete and the_iterable.gathering_started():
            the_iterable = the_iterable.elements
        elif docassemble.base.functions.get_gathering_mode(the_iterable.instanceName):
            the_iterable = the_iterable.complete_elements()
    contents = []
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
    for indexno, the_header in enumerate(header_output):
        words = re.split(r'[ \n]', the_header)
        if len(the_header) > max_chars[indexno]:
            max_chars[indexno] = len(the_header)
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
        for indexno, num_max_chars in enumerate(max_chars_to_use):
            if upto + num_max_chars >= r:
                if num_max_chars > max_word[indexno] or override_mode:
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
        return_val = {}
        if hasattr(self, 'instanceName'):
            return_val['instanceName'] = self.instanceName
        return return_val

    def subject_as_html(self, **kwargs):
        the_args = {}
        for key, val in kwargs.items():
            the_args[key] = val
        the_args['status'] = docassemble.base.functions.this_thread.interview_status
        the_args['question'] = docassemble.base.functions.this_thread.current_question
        return docassemble.base.filter.markdown_to_html(self.subject, **the_args)

    def content_as_html(self, **kwargs):
        the_args = {}
        for key, val in kwargs.items():
            the_args[key] = val
        the_args['status'] = docassemble.base.functions.this_thread.interview_status
        the_args['question'] = docassemble.base.functions.this_thread.current_question
        return docassemble.base.filter.markdown_to_html(self.content, **the_args)

    @property
    def subject(self, **kwargs):
        if not hasattr(self, 'source_subject'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        user_dict_copy.update(kwargs)
        return self.source_subject.text(user_dict_copy).rstrip()

    @property
    def content(self, **kwargs):
        if not hasattr(self, 'source_content'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        user_dict_copy.update(kwargs)
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
        if docassemble.base.functions.this_thread.evaluation_context == 'docx' and server.daconfig.get('new template markdown behavior', False):
            content = re.sub(r'\\_', r'\\\\_', content)
            return str(docassemble.base.file_docx.markdown_to_docx(content, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None)))
        return content

    def show_as_markdown(self, **kwargs):
        """Displays the contents of the template as Markdown, even in the DOCX context."""
        if not hasattr(self, 'source_content'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        user_dict_copy.update(kwargs)
        return self.source_content.text(user_dict_copy).rstrip()

    def __str__(self):
        if docassemble.base.functions.this_thread.evaluation_context == 'docx' and server.daconfig.get('new template markdown behavior', False):
            content = self.content
            content = re.sub(r'\\_', r'\\\\_', content)
            return str(docassemble.base.file_docx.markdown_to_docx(content, docassemble.base.functions.this_thread.current_question, docassemble.base.functions.this_thread.misc.get('docx_template', None)))
        return str(self.content)


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
    def content(self, **kwargs):
        if not hasattr(self, 'table_info'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        return text_of_table(self.table_info, self.userdict, self.tempvars)

    def export(self, filename=None, file_format=None, title=None, freeze_panes=True, output_to=None):
        if file_format is None:
            if filename is not None:
                base_filename, file_format = os.path.splitext(filename)  # pylint: disable=unused-variable
                file_format = re.sub(r'^\.', '', file_format)
            else:
                file_format = 'xlsx'
        if file_format not in ('json', 'xlsx', 'csv'):
            raise Exception("export: unsupported file format")
        header_output, contents = self.header_and_contents()
        df = pandas.DataFrame.from_records(contents, columns=header_output)
        if output_to is None:
            output_to = DAFile()
            output_to.set_random_instance_name()
        elif isinstance(output_to, DAFileList):
            output_to = output_to.elements[0]
        if not isinstance(output_to, DAFile):
            raise Exception("export: output_to must be a DAFile")
        if filename is not None:
            output_to.initialize(filename=filename, extension=file_format, reinitialize=output_to.ok)
        else:
            output_to.initialize(extension=file_format, reinitialize=output_to.ok)
        if file_format == 'xlsx':
            if freeze_panes:
                freeze_panes = (1, 0)
            else:
                freeze_panes = None
            writer = pandas.ExcelWriter(output_to.path(),  # pylint: disable=abstract-class-instantiated
                                        engine='xlsxwriter',
                                        options={'remove_timezone': True})
            df.to_excel(writer, sheet_name=title, index=False, freeze_panes=freeze_panes)
            writer.save()
        elif file_format == 'csv':
            df.to_csv(output_to.path(), index=False)
        elif file_format == 'json':
            df.to_json(output_to.path(), orient='records')
        output_to.commit()
        output_to.retrieve()
        return output_to

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
        if not hasattr(self, 'table_info'):
            raise LazyNameError("name '" + str(self.instanceName) + "' is not defined")
        user_dict_copy = copy.copy(self.userdict)
        user_dict_copy.update(self.tempvars)
        header_output = [export_safe(x.text(user_dict_copy)) for x in self.table_info.header]
        if self.table_info.is_editable:
            header_output.pop()
        the_iterable = eval(self.table_info.row, user_dict_copy)
        if (not isinstance(the_iterable, (DAList, DADict, abc.Iterable))) or isinstance(the_iterable, str):
            raise DAError("Error in processing table " + self.table_info.saveas + ": row value is not iterable")
        if hasattr(the_iterable, 'instanceName') and hasattr(the_iterable, 'elements') and isinstance(the_iterable.elements, (list, dict)):
            if not self.table_info.require_gathered:
                the_iterable = the_iterable.complete_elements()
            elif self.table_info.show_incomplete and the_iterable.gathering_started():
                the_iterable = the_iterable.elements
            elif docassemble.base.functions.get_gathering_mode(the_iterable.instanceName):
                the_iterable = the_iterable.complete_elements()
        contents = []
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
        def object_labeler(x):
            return str(kwargs['object_labeler'](x))
    else:
        object_labeler = str
    if 'help_generator' in kwargs:
        def help_generator(x):
            return str(kwargs['help_generator'](x))
    else:
        help_generator = None
    if 'image_generator' in kwargs:
        def image_generator(x):
            return str(kwargs['image_generator'](x))
    else:
        image_generator = None
    to_exclude = set()
    if 'exclude' in kwargs:
        setify(kwargs['exclude'], to_exclude)

    defaults = set()
    if 'default' in kwargs:
        setify(kwargs['default'], defaults)
        defaults.discard(None)
    output = []
    seen = set()
    for arg in pargs:
        if isinstance(arg, DAList):
            arg._trigger_gather()
            the_list = arg.elements
        elif isinstance(arg, DASet):
            arg._trigger_gather()
            the_list = list(arg.elements)
        elif isinstance(arg, list):
            the_list = arg
        elif isinstance(arg, set):
            the_list = list(arg)
        elif isinstance(arg, abc.Iterable) and not isinstance(arg, str):
            the_list = list(arg)
        else:
            the_list = [arg]
        for subarg in the_list:
            if isinstance(subarg, DAObject) and subarg not in to_exclude and subarg not in seen:
                default_value = bool(subarg in defaults)
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


def setify(item, output=None):
    if output is None:
        output = set()
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
        # logmessage("co_name is " + str(frame.f_code.co_names))
        the_names = frame.f_code.co_names
        if len(the_names) == 2:
            thename = the_names[1]
        else:
            thename = None
        del frame
    else:
        thename = name
    # logmessage("objects_from_file: thename is " + str(thename))
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
    with open(file_info['fullpath'], 'r', encoding='utf-8') as fp:
        if 'mimetype' in file_info and file_info['mimetype'] == 'application/json':
            document = json.load(fp)
            new_objects = recurse_obj(document, recursive=recursive, use_objects=use_objects)
            if isinstance(new_objects, list):
                is_singular = False
                for obj in new_objects:
                    objects.append(obj)
            else:
                objects.append(new_objects)
        else:
            for document in yaml.load_all(fp, Loader=yaml.FullLoader):
                new_objects = recurse_obj(document, recursive=recursive, use_objects=use_objects)
                if isinstance(new_objects, list):
                    is_singular = False
                    for obj in new_objects:
                        objects.append(obj)
                else:
                    objects.append(new_objects)
    if is_singular and len(objects.elements) == 1:
        objects = objects.elements[0]
    # logmessage("Returning for a " + str(thename))
    if thename is not None and isinstance(objects, DAObject):
        objects._set_instance_name_recursively(thename)
    if isinstance(objects, (DAList, DADict, DASet)) and not gathered:
        objects._reset_gathered_recursively()
    # logmessage("Returning a " + str(objects.instanceName))
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
        if use_objects:
            return_object = DAList('return_object', elements=the_object)
            return_object.set_random_instance_name()
            return return_object
        return the_object
    if isinstance(the_object, set):
        if recursive:
            new_set = set()
            for sub_object in the_object:
                new_set.add(recurse_obj(sub_object, recursive=recursive, use_objects=use_objects))
            if use_objects:
                return_object = DASet('return_object', elements=new_set)
                return_object.set_random_instance_name()
                return return_object
            return new_set
        return the_object
    if isinstance(the_object, dict):
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
                objects = []
                for item in the_object['items']:
                    if not isinstance(item, dict):
                        raise SystemError('recurse_obj: found an item, ' + str(item) + ' that was not expressed as a dictionary')
                    if recursive:
                        transformed_item = recurse_obj(item, recursive=True, use_objects=use_objects)
                    else:
                        transformed_item = item
                    # new_obj = constructor(**transformed_item)
                    # if isinstance(new_obj, DAList) or isinstance(new_obj, DADict) or isinstance(new_obj, DASet):
                    #    new_obj.gathered = True
                    objects.append(constructor(**transformed_item))
                return objects
            if 'item' in the_object:
                item = the_object['item']
                if not isinstance(item, dict):
                    raise SystemError('recurse_obj: found an item, ' + str(item) + ' that was not expressed as a dictionary')
                if recursive:
                    transformed_item = recurse_obj(item, recursive=True, use_objects=use_objects)
                else:
                    transformed_item = item
                # new_obj = constructor(**transformed_item)
                # if isinstance(new_obj, DAList) or isinstance(new_obj, DADict) or isinstance(new_obj, DASet):
                #    new_obj.gathered = True
                return constructor(**transformed_item)
        else:
            if recursive:
                new_dict = {}
                for key, the_value in the_object.items():
                    new_dict[key] = recurse_obj(the_value, recursive=True, use_objects=use_objects)
                if use_objects:
                    return_object = DADict('return_object', elements=new_dict)
                    return_object.set_random_instance_name()
                    return return_object
                return new_dict
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
        """In the DOCX context, returns a DOCX hyperlink. Otherwise, returns a Markdown hyperlink."""
        if docassemble.base.functions.this_thread.evaluation_context == 'docx':
            return docassemble.base.file_docx.create_hyperlink(self.url, self.anchor_text, docassemble.base.functions.this_thread.misc.get('docx_template', None))
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
        return str(self.elements['question'])

    def __repr__(self):
        output = str('DAContext(' + repr(self.instanceName) + ', ')
        if len(self.elements) > 0:
            output += ', '.join(key + '=' + repr(val) for key, val in self.elements.items())
        output += str(')')
        return output

    def __hash__(self):
        return hash((self.instanceName,))


da_context_keys = set(['question', 'document', 'docx', 'pdf', 'pandoc'])


def objects_from_structure(target, root=None):
    if isinstance(target, dict):
        target_keys = set(target.keys())
        if len(target_keys) > 0 and len(target_keys.intersection(da_context_keys)) >= 2 and len(target_keys.difference(da_context_keys)) == 0:
            new_context = DAContext('abc_context', **target)
            if root:
                new_context._set_instance_name_recursively(root)
            new_context.gathered = True
            return new_context
        new_dict = DADict('abc_dict')
        for key, val in target.items():
            new_dict[key] = objects_from_structure(val)
        new_dict.gathered = True
        if root:
            new_dict._set_instance_name_recursively(root)
        return new_dict
    if isinstance(target, list):
        new_list = DAList('abc_list')
        for val in target.__iter__():  # pylint: disable=unnecessary-dunder-call
            new_list.append(objects_from_structure(val))
        new_list.gathered = True
        if root:
            new_list._set_instance_name_recursively(root)
        return new_list
    if isinstance(target, (bool, float, int, NoneType, str)):
        return target
    raise DAError("objects_from_structure: expected a standard type, but found a " + str(type(target)))


class DASessionLocal(DAObject):

    def __init__(self, *pargs, **kwargs):
        super().__init__('session_local')


class DADeviceLocal(DAObject):

    def __init__(self, *pargs, **kwargs):
        super().__init__('device_local')


class DAUserLocal(DAObject):

    def __init__(self, *pargs, **kwargs):
        super().__init__('user_local')


class DAGlobal(DAObject):
    """A class for objects that are stored in an unencrypted global area outside of the interview answers."""

    @classmethod
    def keys(cls, base):
        if base == 'interview':
            globalbase = 'da:daglobal:i:' + str(this_thread.current_info.get('yaml_filename', ''))
        elif base == 'global':
            globalbase = 'da:daglobal:global'
        else:
            globalbase = 'da:daglobal:userid:' + str(this_thread.current_info['user']['the_user_id'])
        return server.server_sql_keys(globalbase + ':')

    @classmethod
    def defined(cls, base, key):
        """Returns True if the key exists in the data store, otherwise returns False."""
        if base == 'interview':
            globalkey = 'da:daglobal:i:' + str(this_thread.current_info.get('yaml_filename', '')) + ':' + str(key)
        elif base == 'global':
            globalkey = 'da:daglobal:global:' + str(key)
        else:
            globalkey = 'da:daglobal:userid:' + str(this_thread.current_info['user']['the_user_id']) + ':' + str(key)
        return server.server_sql_defined(globalkey)

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        if 'base' not in kwargs:
            self.base = 'user'
        if 'key' not in kwargs:
            self.key = random_alphanumeric(32)
        if self.base == 'interview':
            globalkey = 'da:daglobal:i:' + str(this_thread.current_info.get('yaml_filename', '')) + ':' + str(self.key)
        elif self.base == 'global':
            globalkey = 'da:daglobal:global:' + str(self.key)
        else:
            globalkey = 'da:daglobal:userid:' + str(this_thread.current_info['user']['the_user_id']) + ':' + str(self.key)
        saved_dict = server.server_sql_get(globalkey)  # pylint: disable=assignment-from-none
        if isinstance(saved_dict, dict):
            for key, val in saved_dict.items():
                setattr(self, key, val)

    def __getstate__(self):
        if hasattr(self, 'base') and hasattr(self, 'key'):
            if self.base == 'interview':
                globalkey = 'da:daglobal:i:' + str(this_thread.current_info.get('yaml_filename', '')) + ':' + str(self.key)
            elif self.base == 'global':
                globalkey = 'da:daglobal:global:' + str(self.key)
            else:
                globalkey = 'da:daglobal:userid:' + str(this_thread.current_info['user']['the_user_id']) + ':' + str(self.key)
            dict_to_save = copy.copy(self.__dict__)
            dict_to_return = {'attrList': []}
            if 'instanceName' in dict_to_save:
                dict_to_return['instanceName'] = dict_to_save['instanceName']
                del dict_to_save['instanceName']
            if 'has_nonrandom_instance_name' in dict_to_save:
                dict_to_return['has_nonrandom_instance_name'] = dict_to_save['has_nonrandom_instance_name']
                del dict_to_save['has_nonrandom_instance_name']
            if 'base' in dict_to_save:
                dict_to_return['base'] = dict_to_save['base']
                del dict_to_save['base']
            if 'key' in dict_to_save:
                dict_to_return['key'] = dict_to_save['key']
                del dict_to_save['key']
            server.server_sql_set(globalkey, dict_to_save, encrypted=False)
            return dict_to_return
        dict_to_return = copy.copy(self.__dict__)
        return dict_to_return

    def __setstate__(self, pickle_dict):
        self.__dict__ = pickle_dict
        if 'base' in pickle_dict and 'key' in pickle_dict:
            if pickle_dict['base'] == 'interview':
                globalkey = 'da:daglobal:i:' + str(this_thread.current_info.get('yaml_filename', '')) + ':' + str(pickle_dict['key'])
            elif pickle_dict['base'] == 'global':
                globalkey = 'da:daglobal:global:' + str(pickle_dict['key'])
            else:
                globalkey = 'da:daglobal:userid:' + str(this_thread.current_info['user']['the_user_id']) + ':' + str(pickle_dict['key'])

            saved_dict = server.server_sql_get(globalkey)  # pylint: disable=assignment-from-none
            if isinstance(saved_dict, dict):
                for key, val in saved_dict.items():
                    setattr(self, key, val)

    def delete(self):
        """Deletes the data in the global storage area and undefines all attributes."""
        if self.base == 'interview':
            globalkey = 'da:daglobal:i:' + this_thread.current_info.get('yaml_filename', '') + ':' + self.key
        elif self.base == 'global':
            globalkey = 'da:daglobal:global:' + self.key
        else:
            globalkey = 'da:daglobal:userid:' + str(this_thread.current_info['user']['the_user_id']) + ':' + self.key
        server.server_sql_delete(globalkey)
        self.__dict__ = dict(instanceName=self.instanceName, attrList=[], has_nonrandom_instance_name=self.has_nonrandom_instance_name)


class DAStore(DAObject):
    """A class used to save objects to SQL."""

    def is_encrypted(self):
        """Returns True if the storage object is using encryption, otherwise returns False."""
        if hasattr(self, 'encrypted'):
            return self.encrypted
        if hasattr(self, 'base'):
            if self.base == 'interview':
                return False
            if self.base == 'user':
                return True
            if self.base == 'session':
                return True
            if self.base == 'global':
                return False
            return False
        return True

    def _get_base_key(self):
        if hasattr(self, 'base'):
            if self.base == 'interview':
                return 'da:i:' + this_thread.current_info.get('yaml_filename', '')
            if self.base == 'user':
                return 'da:userid:' + str(this_thread.current_info['user']['the_user_id'])
            if self.base == 'session':
                return 'da:uid:' + get_uid() + ':i:' + this_thread.current_info.get('yaml_filename', '')
            if self.base == 'global':
                return 'da:global'
            return str(self.base)
        return 'da:userid:' + str(this_thread.current_info['user']['the_user_id'])

    def defined(self, key):
        """Returns True if the key exists in the data store, otherwise returns False."""
        the_key = self._get_base_key() + ':' + key
        return server.server_sql_defined(the_key)

    def get(self, key):
        """Reads an object from the data store for the given key."""
        the_key = self._get_base_key() + ':' + key
        return server.server_sql_get(the_key, secret=this_thread.current_info.get('secret', None))

    def set(self, key, the_value):
        """Writes an object to the data store under the given key."""
        the_key = self._get_base_key() + ':' + key
        server.server_sql_set(the_key, the_value, encrypted=self.is_encrypted(), secret=this_thread.current_info.get('secret', None), the_user_id=this_thread.current_info['user']['the_user_id'])

    def delete(self, key):
        """Deletes an object from the data store"""
        the_key = self._get_base_key() + ':' + key
        server.server_sql_delete(the_key)

    def keys(self):
        """Returns a list of keys in use."""
        return server.server_sql_keys(self._get_base_key() + ':')


class DAWeb(DAObject):
    """A class used to call external APIs"""

    def _get_base_url(self):
        if hasattr(self, 'base_url'):
            base_url = self.base_url
            if not isinstance(self.base_url, str):
                raise Exception("DAWeb.call: the base url must be a string")
            if not base_url.endswith('/'):
                base_url += '/'
            return base_url
        return self.base_url

    def _get_on_failure(self, on_failure):
        if on_failure is None and hasattr(self, 'on_failure'):
            on_failure = self.on_failure
        return on_failure

    def _get_success_code(self, success_code):
        if success_code is None and hasattr(self, 'success_code'):
            success_code = self.success_code
        return success_code

    def _get_on_success(self, on_success):
        if on_success is None and hasattr(self, 'on_success'):
            on_success = self.on_success
        return on_success

    def _get_task(self, task):
        if task is None and hasattr(self, 'task'):
            task = self.task
        if task is None:
            return None
        if not isinstance(task, str):
            raise Exception("DAWeb.call: task must be a string")
        return task

    def _get_task_persistent(self, task_persistent):
        if task_persistent is None and hasattr(self, 'task_persistent'):
            task_persistent = self.task_persistent
        if task_persistent is None:
            return False
        if not isinstance(task_persistent, (bool, str)):
            raise Exception("DAWeb.call: task_persistent must be boolean or string")
        return task_persistent

    def _get_auth(self, auth):
        if auth is None and hasattr(self, 'auth'):
            auth = self.auth
        if isinstance(auth, (dict, DADict)):
            if auth.get('type', 'basic') == 'basic':
                return HTTPBasicAuth(auth['username'], auth['password'])
            if auth['type'] == 'digest':
                return HTTPDigestAuth(auth['username'], auth['password'])
        return auth

    def _get_headers(self, new_headers):
        if hasattr(self, 'headers'):
            headers = self.headers
            if isinstance(headers, DADict):
                headers = headers.elements
            if not isinstance(headers, dict):
                raise Exception("DAWeb.call: the headers must be a dictionary")
            headers.update(new_headers)
            return headers
        return new_headers

    def _get_cookies(self, new_cookies):
        if hasattr(self, 'cookies'):
            cookies = self.cookies
            if isinstance(cookies, DADict):
                cookies = cookies.elements
            if not isinstance(cookies, dict):
                raise Exception("DAWeb.call: the cookies must be a dictionary")
            cookies.update(new_cookies)
            return cookies
        return new_cookies

    def _get_json_body(self, json_body):
        if json_body is not None:
            return bool(json_body)
        if hasattr(self, 'json_body'):
            return bool(self.json_body)
        return True

    def _call(self, url, method=None, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, task=None, task_persistent=None, files=None, cookies=None, success_code=None):
        task = self._get_task(task)
        task_persistent = self._get_task_persistent(task_persistent)
        auth = self._get_auth(auth)
        json_body = self._get_json_body(json_body)
        on_failure = self._get_on_failure(on_failure)
        on_success = self._get_on_success(on_success)
        success_code = self._get_success_code(success_code)
        if isinstance(success_code, str):
            success_code = [int(success_code.strip())]
        elif isinstance(success_code, (DASet, DAList)) or (isinstance(success_code, abc.Iterable) and not isinstance(success_code, str)):
            new_success_code = []
            for code in success_code:
                if not isinstance(code, int):
                    raise Exception("DAWeb.call: success codes must be integers")
                new_success_code.append(code)
            success_code = new_success_code
        elif isinstance(success_code, int):
            success_code = [success_code]
        elif success_code is not None:
            raise Exception("DAWeb.call: success_code must be an integer or a list of integers")
        if method is None:
            method = 'GET'
        if not isinstance(method, str):
            raise Exception("DAWeb.call: the method must be a string")
        method = method.upper().strip()
        if method not in ('POST', 'GET', 'PATCH', 'PUT', 'HEAD', 'DELETE', 'OPTIONS'):
            raise Exception("DAWeb.call: invalid method")
        if not isinstance(url, str):
            raise Exception("DAWeb.call: the url must be a string")
        if not re.search(r'^https?://', url):
            url = self._get_base_url() + re.sub(r'^/*', '', url)
        if data is None:
            data = {}
        if isinstance(data, DADict):
            data = data.elements
        if json_body is False and not isinstance(data, dict):
            raise Exception("DAWeb.call: data must be a dictionary")
        if params is None:
            params = {}
        if isinstance(params, DADict):
            params = params.elements
        if not isinstance(params, dict):
            raise Exception("DAWeb.call: params must be a dictionary")
        if headers is None:
            headers = {}
        if isinstance(headers, DADict):
            headers = headers.elements
        if not isinstance(headers, dict):
            raise Exception("DAWeb.call: the headers must be a dictionary")
        headers = self._get_headers(headers)
        if len(headers) == 0:
            headers = None
        if cookies is None:
            cookies = {}
        if isinstance(cookies, DADict):
            cookies = cookies.elements
        if not isinstance(cookies, dict):
            raise Exception("DAWeb.call: the cookies must be a dictionary")
        cookies = self._get_cookies(cookies)
        if len(cookies) == 0:
            cookies = None
        if isinstance(data, dict) and len(data) == 0:
            data = None
        if files is not None:
            if not isinstance(files, dict):
                raise Exception("DAWeb.call: files must be a dictionary")
            new_files = {}
            for key, val in files.items():
                if not isinstance(key, str):
                    raise Exception("DAWeb.call: files must be a dictionary of string keys")
                try:
                    path = server.path_from_reference(val)
                    logmessage("path is " + str(path))
                    assert path is not None
                except:
                    raise Exception("DAWeb.call: could not load the file")
                new_files[key] = open(path, 'rb')
            files = new_files
            if len(files):
                json_body = False
        try:
            if method == 'POST':
                if json_body:
                    r = requests.post(url, json=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files)
                else:
                    r = requests.post(url, data=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files)
            elif method == 'PUT':
                if json_body:
                    r = requests.put(url, json=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files)
                else:
                    r = requests.put(url, data=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files)
            elif method == 'PATCH':
                if json_body:
                    r = requests.patch(url, json=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files)
                else:
                    r = requests.patch(url, data=data, params=params, headers=headers, auth=auth, cookies=cookies, files=files)
            elif method == 'GET':
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.get(url, params=params, headers=headers, auth=auth, cookies=cookies)
            elif method == 'DELETE':
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.delete(url, params=params, headers=headers, auth=auth, cookies=cookies)
            elif method == 'OPTIONS':
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.options(url, params=params, headers=headers, auth=auth, cookies=cookies)
            elif method == 'HEAD':
                if len(params) == 0:
                    params = data
                    data = None
                r = requests.head(url, params=params, headers=headers, auth=auth, cookies=cookies)
        except RequestException as err:
            if on_failure == 'raise':
                raise DAWebError(url=url, method=method, params=params, headers=headers, data=data, task=task, task_persistent=task_persistent, status_code=-1, response_text='', response_json=None, response_headers={}, exception_type=err.__class__.__name__, exception_text=str(err), cookies_before=cookies, cookies_after=None)
            return on_failure
        if success_code is None:
            success = bool(r.status_code >= 200 and r.status_code < 300)
        else:
            success = bool(r.status_code in success_code)
        if hasattr(self, 'cookies'):
            self.cookies = dict(r.cookies)
        try:
            the_json_response = r.json()
        except:
            the_json_response = None
        if success and task is not None:
            mark_task_as_performed(task, persistent=task_persistent)
        if not success:
            if on_failure == 'content':
                return r.content
            if on_failure == 'text':
                return r.text
            if on_failure == 'status_code':
                return r.status_code
            if on_failure == 'raise':
                raise DAWebError(url=url, method=method, params=params, headers=headers, data=data, task=task, task_persistent=task_persistent, status_code=r.status_code, response_text=r.text, response_json=the_json_response, response_headers=r.headers, exception_type=None, exception_text=None, cookies_before=cookies, cookies_after=dict(r.cookies), success=success)
            return on_failure
        if success and on_success is not None:
            if on_success == 'content':
                return r.content
            if on_success == 'text':
                return r.text
            if on_success == 'status_code':
                return r.status_code
            if on_success == 'raise':
                raise DAWebError(url=url, method=method, params=params, headers=headers, data=data, task=task, task_persistent=task_persistent, status_code=r.status_code, response_text=r.text, response_json=the_json_response, response_headers=r.headers, exception_type=None, exception_text=None, cookies_before=cookies, cookies_after=dict(r.cookies), success=success)
            return on_success
        return the_json_response if the_json_response is not None else r.text

    def get(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None):
        """Makes a GET request"""
        return self._call(url, method='GET', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)

    def post(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None, files=None):
        """Makes a POST request"""
        return self._call(url, method='POST', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent, files=files)

    def put(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None, files=None):
        """Makes a PUT request"""
        return self._call(url, method='PUT', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent, files=files)

    def patch(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None, files=None):
        """Makes a PATCH request"""
        return self._call(url, method='PATCH', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent, files=files)

    def delete(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None):
        """Makes a DELETE request"""
        return self._call(url, method='DELETE', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)

    def options(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None):
        """Makes an OPTIONS request"""
        return self._call(url, method='OPTIONS', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)

    def head(self, url, data=None, params=None, headers=None, json_body=None, on_failure=None, on_success=None, auth=None, cookies=None, task=None, task_persistent=None):
        """Makes a HEAD request"""
        return self._call(url, method='HEAD', data=data, params=params, headers=headers, json_body=json_body, on_failure=on_failure, on_success=on_success, auth=auth, cookies=cookies, task=task, task_persistent=task_persistent)


class DARedis(DAObject):
    """A class used to interact with the redis server."""

    def key(self, keyname):
        """Returns a key that combines the interview name with the keyname."""
        return this_thread.current_info.get('yaml_filename', '') + ':' + str(keyname)

    def get_data(self, key):
        """Returns data from Redis and unpickles it."""
        result = server.server_redis_user.get(key)
        if result is None:
            return None
        try:
            result = server.fix_pickle_obj(result)
        except:
            logmessage("get_data: could not unpickle contents of " + str(key))
            result = None
        return result

    def set_data(self, key, data, expire=None):
        """Saves data in Redis after pickling it."""
        pickled_data = pickle.dumps(data)
        if expire is not None:
            if not isinstance(expire, int):
                raise DAError("set_data: expire time must be an integer")
            pipe = server.server_redis_user.pipeline()
            pipe.set(key, pickled_data)
            pipe.expire(key, expire)
            pipe.execute()
        else:
            server.server_redis_user.set(key, pickled_data)

    def __getattr__(self, funcname):
        return getattr(server.server_redis_user, funcname)


class DACloudStorage(DAObject):
    """Returns an object that can be used to interface with S3 or Azure."""

    def init(self, *pargs, **kwargs):
        if 'provider' in kwargs and 'config' in kwargs:
            self.custom = True
            self.provider = kwargs['provider']
            self.config = kwargs['config']
            del kwargs['provider']
            del kwargs['config']
            server.cloud_custom(self.provider, self.config)
        else:
            self.custom = False
        super().init(*pargs, **kwargs)

    @property
    def conn(self):
        """This property returns a boto3.resource('s3') or BlockBlobService() object."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).conn
        return server.cloud.conn

    @property
    def client(self):
        """This property returns a boto3.client('s3') object."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).client
        return server.cloud.client

    @property
    def bucket(self):
        """This property returns a boto3 Bucket() object."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).bucket
        return server.cloud.bucket

    @property
    def bucket_name(self):
        """This property returns the name of the Amazon S3 bucket."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).bucket_name
        return server.cloud.bucket_name

    @property
    def container_name(self):
        """This property returns the name of the Azure Blob Storage container."""
        if self.custom:
            return server.cloud_custom(self.provider, self.config).container
        return server.cloud.container


class DAGoogleAPI(DAObject):

    def api_credentials(self, scope):
        """Returns an OAuth2 credentials object for the given scope."""
        return server.google_api.google_api_credentials(scope)

    def http(self, scope):
        """Returns a credentialized http object for the given scope."""
        return self.api_credentials(scope).authorize(httplib2.Http())

    def drive_service(self):
        """Returns a Google Drive service object using google-api-python-client."""
        return apiclient.discovery.build('drive', 'v3', http=self.http('https://www.googleapis.com/auth/drive'))

    def cloud_credentials(self, scope):
        """Returns a google.oauth2.service_account credentials object for the given scope."""
        return server.google_api.google_cloud_credentials(scope)

    def project_id(self):
        """Returns the ID of the project referenced in the google service account credentials in the Configuration."""
        return server.google_api.project_id()

    def google_cloud_storage_client(self):
        """Returns a google.cloud.storage.Client object."""
        return server.google_api.google_cloud_storage_client()

    def google_cloud_vision_client(self):
        """Returns an google.cloud.vision.ImageAnnotatorClient object."""
        return server.google_api.google_cloud_vision_client()


def run_python_module(module, arguments=None):
    """Runs a python module, as though from the command line, and returns the output."""
    if re.search(r'\.py$', module):
        module = this_thread.current_package + '.' + re.sub(r'\.py$', '', module)
    elif re.search(r'^\.', module):
        module = this_thread.current_package + module
    commands = [re.sub(r'/lib/python.*', '/bin/python3', docassemble.base.pandoc.__file__), '-m', module]
    if arguments:
        if not isinstance(arguments, list):
            raise DAError("run_python_module: the arguments parameter must be in the form of a list")
        commands.extend(arguments)
    output = ''
    try:
        output = subprocess.check_output(commands, stderr=subprocess.STDOUT).decode()
        return_code = 0
    except subprocess.CalledProcessError as err:
        output = err.output.decode()
        return_code = err.returncode
    return output, return_code


def today(timezone=None, format=None):  # pylint: disable=redefined-builtin
    """Returns today's date at midnight as a DADateTime object."""
    ensure_definition(timezone, format)
    if timezone is None:
        timezone = get_default_timezone()
    val = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone))
    if format is not None:
        return dd(val.replace(hour=0, minute=0, second=0, microsecond=0)).format_date(format)
    return dd(val.replace(hour=0, minute=0, second=0, microsecond=0))


def babel_language(language):
    if 'babel dates map' not in server.daconfig:
        return language
    return server.daconfig['babel dates map'].get(language, language)


def month_of(the_date, as_word=False, language=None):
    """Interprets the_date as a date and returns the month.
    Set as_word to True if you want the month as a word."""
    ensure_definition(the_date, as_word, language)
    if language is None:
        language = get_language()
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        if as_word:
            return babel.dates.format_date(date, format='MMMM', locale=babel_language(language))
        return int(date.strftime('%m'))
    except:
        return word("Bad date")


def day_of(the_date, language=None):
    """Interprets the_date as a date and returns the day of month."""
    ensure_definition(the_date, language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return int(date.strftime('%d'))
    except:
        return word("Bad date")


def dow_of(the_date, as_word=False, language=None):
    """Interprets the_date as a date and returns the day of week as a number from 1 to 7 for Sunday through Saturday.  Set as_word to True if you want the day of week as a word."""
    ensure_definition(the_date, as_word, language)
    if language is None:
        language = get_language()
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        if as_word:
            return babel.dates.format_date(date, format='EEEE', locale=babel_language(language))
        return int(date.strftime('%u'))
    except:
        return word("Bad date")


def year_of(the_date, language=None):
    """Interprets the_date as a date and returns the year."""
    ensure_definition(the_date, language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return int(date.strftime('%Y'))
    except:
        return word("Bad date")


def interview_default(the_part, default_value, language):
    if the_part in this_thread.internal and this_thread.internal[the_part] is not None:
        return this_thread.internal[the_part]
    for lang in (language, get_language(), '*'):
        if lang is not None:
            if lang in this_thread.interview.default_title:
                if the_part in this_thread.interview.default_title[lang]:
                    return this_thread.interview.default_title[lang][the_part]
    return default_value


def format_date(the_date, format=None, language=None):  # pylint: disable=redefined-builtin
    """Interprets the_date as a date and returns the date formatted for the current locale."""
    ensure_definition(the_date, format, language)
    if isinstance(the_date, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('date format', 'long', language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_date(date, format=format, locale=babel_language(language))
    except:
        return word("Bad date")


def format_datetime(the_date, format=None, language=None):  # pylint: disable=redefined-builtin
    """Interprets the_date as a date/time and returns the date/time formatted for the current locale."""
    ensure_definition(the_date, format, language)
    if isinstance(the_date, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('datetime format', 'long', language)
    try:
        if isinstance(the_date, (datetime.datetime, datetime.date)):
            date = the_date
        else:
            date = dateutil.parser.parse(the_date)
        return babel.dates.format_datetime(date, format=format, locale=babel_language(language))
    except:
        return word("Bad date")


def format_time(the_time, format=None, language=None):  # pylint: disable=redefined-builtin
    """Interprets the_time as a date/time and returns the time formatted for the current locale."""
    ensure_definition(the_time, format, language)
    if isinstance(the_time, DAEmpty):
        return ""
    if language is None:
        language = get_language()
    if format is None:
        format = interview_default('time format', 'short', language)
    try:
        if isinstance(the_time, (datetime.datetime, datetime.date, datetime.time)):
            this_time = the_time
        else:
            this_time = dateutil.parser.parse(the_time)
        return babel.dates.format_time(this_time, format=format, locale=babel_language(language))
    except Exception as errmess:
        return word("Bad date: " + str(errmess))


class DateTimeDelta:

    def __str__(self):
        return str(self.describe())

    def describe(self, **kwargs):
        specificity = kwargs.get('specificity', None)
        output = []
        diff = dateutil.relativedelta.relativedelta(self.end, self.start)
        if diff.years != 0:
            output.append((abs(diff.years), noun_plural(word('year'), abs(diff.years))))
        if diff.months != 0 and specificity != 'year':
            output.append((abs(diff.months), noun_plural(word('month'), abs(diff.months))))
        if diff.days != 0 and specificity not in ('year', 'month'):
            output.append((abs(diff.days), noun_plural(word('day'), abs(diff.days))))
        if kwargs.get('nice', True):
            return_value = comma_and_list(["%s %s" % (nice_number(y[0]), y[1]) for y in output])
            if kwargs.get('capitalize', False):
                return capitalize(return_value)
            return return_value
        return comma_and_list(["%d %s" % y for y in output])


class DADateTime(datetime.datetime):

    def format(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_date(self, format=format, language=language)

    def format_date(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_date(self, format=format, language=language)

    def format_datetime(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_datetime(self, format=format, language=language)

    def format_time(self, format=None, language=None):  # pylint: disable=redefined-builtin
        return format_time(self, format=format, language=language)

    def replace_time(self, the_time):
        return self.replace(hour=the_time.hour, minute=the_time.minute, second=the_time.second, microsecond=the_time.microsecond)

    @property
    def nanosecond(self):
        return 0

    @property
    def dow(self):
        return self.isocalendar()[2]

    @property
    def week(self):
        return self.isocalendar()[1]

    def plus(self, **kwargs):
        return dd(dt(self) + date_interval(**kwargs))

    def minus(self, **kwargs):
        return dd(dt(self) - date_interval(**kwargs))

    def __str__(self):
        return str(format_date(self))

    def __add__(self, other):
        if isinstance(other, str):
            return str(self) + other
        val = dt(self) + other
        if isinstance(val, datetime.date):
            return dd(val)
        return val

    def __radd__(self, other):
        if isinstance(other, str):
            return other + str(self)
        return dd(dt(self) + other)

    def __sub__(self, other):
        val = dt(self) - other
        if isinstance(val, datetime.date):
            return dd(val)
        return val

    def __rsub__(self, other):
        val = other - dt(self)
        if isinstance(val, datetime.date):
            return dd(val)
        return val


def current_datetime(timezone=None):
    """Returns the current time.  Uses the default timezone unless another
    timezone is explicitly provided.

    """
    ensure_definition(timezone)
    if timezone is None:
        timezone = get_default_timezone()
    return dd(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)))


def as_datetime(the_date, timezone=None):
    """Converts the_date to a DADateTime object with a timezone.  Uses the

    default timezone unless another timezone is explicitly provided."""
    ensure_definition(the_date, timezone)
    if timezone is None:
        timezone = get_default_timezone()
    if isinstance(the_date, datetime.date) and not isinstance(the_date, datetime.datetime):
        the_date = datetime.datetime.combine(the_date, datetime.datetime.min.time())
    if isinstance(the_date, datetime.datetime):
        new_datetime = the_date
    else:
        new_datetime = dateutil.parser.parse(the_date)
    if new_datetime.tzinfo:
        new_datetime = new_datetime.astimezone(zoneinfo.ZoneInfo(timezone))
    else:
        new_datetime = new_datetime.replace(tzinfo=zoneinfo.ZoneInfo(timezone))
    return dd(new_datetime)


def dd(obj):
    if isinstance(obj, DADateTime):
        return obj
    return DADateTime(obj.year, month=obj.month, day=obj.day, hour=obj.hour, minute=obj.minute, second=obj.second, microsecond=obj.microsecond, tzinfo=obj.tzinfo)


def dt(obj):
    return datetime.datetime(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond, obj.tzinfo)


def date_interval(**kwargs):
    """Expresses a date and time interval.  Passes through all arguments
    to dateutil.relativedelta.relativedelta."""
    ensure_definition(**kwargs)
    return dateutil.relativedelta.relativedelta(**kwargs)


def date_difference(starting=None, ending=None, timezone=None):
    """Calculates the difference between the date indicated by "starting"
    and the date indicated by "ending."  Returns an object with attributes weeks,
    days, hours, minutes, seconds, and delta."""
    ensure_definition(starting, ending, timezone)
    if starting is None:
        starting = current_datetime()
    if ending is None:
        ending = current_datetime()
    if timezone is None:
        timezone = get_default_timezone()
    if isinstance(starting, datetime.date) and not isinstance(starting, datetime.datetime):
        starting = datetime.datetime.combine(starting, datetime.datetime.min.time())
    if isinstance(ending, datetime.date) and not isinstance(ending, datetime.datetime):
        ending = datetime.datetime.combine(ending, datetime.datetime.min.time())
    if not isinstance(starting, datetime.datetime):
        starting = dateutil.parser.parse(starting)
    if not isinstance(ending, datetime.datetime):
        ending = dateutil.parser.parse(ending)
    if starting.tzinfo:
        starting = starting.astimezone(zoneinfo.ZoneInfo(timezone))
    else:
        starting = starting.replace(tzinfo=zoneinfo.ZoneInfo(timezone))
    if ending.tzinfo:
        ending = ending.astimezone(zoneinfo.ZoneInfo(timezone))
    else:
        ending = ending.replace(tzinfo=zoneinfo.ZoneInfo(timezone))
    delta = ending - starting
    output = DateTimeDelta()
    output.start = starting
    output.end = ending
    output.weeks = (delta.days / 7.0) + (delta.seconds / 604800.0)
    output.days = delta.days + (delta.seconds / 86400.0)
    output.hours = (delta.days * 24.0) + (delta.seconds / 3600.0)
    output.minutes = (delta.days * 1440.0) + (delta.seconds / 60.0)
    output.seconds = (delta.days * 86400) + delta.seconds
    output.years = (delta.days + delta.seconds / 86400.0) / 365.2425
    output.delta = delta
    return output


def fax_string(person, country=None):
    if person is None:
        return None
    fax_number = None
    if isinstance(person, Person):
        fax_number = person.facsimile_number(country=country)
    elif isinstance(person, phonenumbers.PhoneNumber):
        fax_number = phonenumbers.format_number(person, phonenumbers.PhoneNumberFormat.E164)
    else:
        fax_number = phone_number_in_e164(person, country=country)
    return fax_number


def phone_string(person, country=None):
    if person is None:
        return None
    phone_number = None
    if isinstance(person, Person):
        phone_number = person.sms_number()
    elif isinstance(person, phonenumbers.PhoneNumber):
        phone_number = phonenumbers.format_number(person, phonenumbers.PhoneNumberFormat.E164)
    else:
        phone_number = phone_number_in_e164(person, country=country)
    return phone_number


def email_string(persons, include_name=None, first=False):
    if persons is None:
        return None
    if not (isinstance(persons, (DAList, DASet, abc.Iterable)) and not isinstance(persons, str)):
        persons = [persons]
    result = []
    for person in persons:
        if isinstance(person, (Person, DAEmailRecipient)):
            result.append(person.email_address(include_name=include_name))
        else:
            result.append(str(person))
    result = [x for x in result if x is not None and x != '']
    if first:
        if len(result):
            return result[0]
        return None
    return result


def email_stringer(variable, first=False, include_name=False):
    return email_string(variable, include_name=include_name, first=first)


def valid_datetime(the_datetime):
    """Returns True if the provided text represents a valid date or time."""
    ensure_definition(the_datetime)
    if isinstance(the_datetime, (datetime.date, datetime.time)):
        return True
    try:
        dateutil.parser.parse(the_datetime)
        return True
    except:
        return False


def timezone_list():
    """Returns a list of timezone choices, expressed as text."""
    return sorted(list(zoneinfo.available_timezones()))


def returning_user(minutes=None, hours=None, days=None):
    """Returns True if the user is returning to the interview after six
    hours of inactivity, or other time indicated by the optional
    keyword arguments minutes, hours, or days.

    """
    if this_thread.current_info['method'] != 'GET':
        return False
    if minutes is not None and last_access_minutes() > minutes:
        return True
    if hours is not None and last_access_hours() > hours:
        return True
    if days is not None and last_access_days() > days:
        return True
    if last_access_hours() > 6.0:
        return True
    return False


def last_access_delta(*pargs, **kwargs):
    """Returns a datetime.timedelta object expressing the length of
    time that has passed since the last time the interview was accessed."""
    last_time = last_access_time(*pargs, **kwargs)
    if last_time is None:
        return datetime.timedelta(0)
    return current_datetime() - last_time


def last_access_days(*pargs, **kwargs):
    """Returns the number of days since the last time the interview
    was accessed."""
    delta = last_access_delta(*pargs, **kwargs)
    return delta.days + (delta.seconds / 86400.0)


def last_access_hours(*pargs, **kwargs):
    """Returns the number of hours since the last time the interview
    was accessed."""
    delta = last_access_delta(*pargs, **kwargs)
    return (delta.days * 24.0) + (delta.seconds / 3600.0)


def last_access_minutes(*pargs, **kwargs):
    """Returns the number of minutes since the last time the interview
    was accessed."""
    delta = last_access_delta(*pargs, **kwargs)
    return (delta.days * 1440.0) + (delta.seconds / 60.0)


def last_access_time(include_privileges=None, exclude_privileges=None, include_cron=False, timezone=None):
    """Returns the last time the interview was accessed, as a DADateTime object."""
    max_time = None
    if include_privileges is not None:
        if not isinstance(include_privileges, (list, tuple, dict)):
            if isinstance(include_privileges, DAObject) and hasattr(include_privileges, 'elements'):
                include_privileges = include_privileges.elements
            else:
                include_privileges = [include_privileges]
        if 'cron' in include_privileges:
            include_cron = True
    if exclude_privileges is not None:
        if not isinstance(exclude_privileges, (list, tuple, dict)):
            if isinstance(exclude_privileges, DAObject) and hasattr(exclude_privileges, 'elements'):
                exclude_privileges = exclude_privileges.elements
            else:
                exclude_privileges = [exclude_privileges]
    else:
        exclude_privileges = []
    for user_id, access_time in this_thread.internal['accesstime'].items():
        if user_id == -1:
            if 'anonymous' in exclude_privileges:
                continue
            if include_privileges is None or 'anonymous' in include_privileges:
                if max_time is None or max_time < access_time:
                    max_time = access_time
                    break
        else:
            user_object = server.get_user_object(user_id)
            if user_object is not None and hasattr(user_object, 'roles'):
                if len(user_object.roles) == 0:
                    if 'user' in exclude_privileges:
                        continue
                    if include_privileges is None or 'user' in include_privileges:
                        if max_time is None or max_time < access_time:
                            max_time = access_time
                            break
                else:
                    for role in user_object.roles:
                        if (include_cron is False and role.name == 'cron') or role.name in exclude_privileges:
                            continue
                        if include_privileges is None or role.name in include_privileges:
                            if max_time is None or max_time < access_time:
                                max_time = access_time
                                break
    if max_time is None:
        return None
    if timezone is not None:
        return dd(max_time.replace(tzinfo=datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)))
    return dd(max_time.replace(tzinfo=datetime.timezone.utc))


def start_time(timezone=None):
    """Returns the time the interview was started, as a DADateTime object."""
    if timezone is not None:
        return dd(this_thread.internal['starttime'].replace(tzinfo=datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)))
    return dd(this_thread.internal['starttime'].replace(tzinfo=datetime.timezone.utc))


class LatitudeLongitude(DAObject):
    """Represents a GPS location."""

    def init(self, *pargs, **kwargs):
        self.gathered = False
        self.known = False
        # self.description = ""
        super().init(*pargs, **kwargs)

    def status(self):
        """Returns True or False depending on whether an attempt has yet been made
        to gather the latitude and longitude."""
        # logmessage("got to status")
        if self.gathered:
            # logmessage("gathered is true")
            return False
        if location_returned():
            # logmessage("returned is true")
            self._set_to_current()
            return False
        return True

    def _set_to_current(self):
        # logmessage("set to current")
        if 'user' in this_thread.current_info and 'location' in this_thread.current_info['user'] and isinstance(this_thread.current_info['user']['location'], dict):
            if 'latitude' in this_thread.current_info['user']['location'] and 'longitude' in this_thread.current_info['user']['location']:
                self.latitude = this_thread.current_info['user']['location']['latitude']
                self.longitude = this_thread.current_info['user']['location']['longitude']
                self.known = True
                # logmessage("known is true")
            elif 'error' in this_thread.current_info['user']['location']:
                self.error = this_thread.current_info['user']['location']['error']
                self.known = False
                # logmessage("known is false")
            self.gathered = True
            self.description = str(self)

    def __str__(self):
        if hasattr(self, 'latitude') and hasattr(self, 'longitude'):
            return str(self.latitude) + ', ' + str(self.longitude)
        if hasattr(self, 'error'):
            return str(self.error)
        return 'Unknown'


class RoleChangeTracker(DAObject):
    """Used within an interview to facilitate changes in the active role
    required for filling in interview information.  Ensures that participants
    do not receive multiple e-mails needlessly."""

    def init(self, *pargs, **kwargs):
        self.last_role = None
    # def should_send_email(self):
    #     """Returns True or False depending on whether an e-mail will be sent on
    #     role change"""
    #     return True

    def _update(self, target_role):
        """When a notification is delivered about a necessary change in the
        active role of the interviewee, this function is called with
        the name of the new role.  This prevents the send_email()
        function from sending duplicative notifications."""
        self.last_role = target_role

    def send_email(self, roles_needed, **kwargs):
        """Sends a notification e-mail if necessary because of a change in the
        active of the interviewee.  Returns True if an e-mail was
        successfully sent.  Otherwise, returns False.  False could
        mean that it was not necessary to send an e-mail."""
        # logmessage("Current role is " + str(this_thread.global_vars.role))
        for key, val in kwargs.items():  # pylint: disable=unused-variable
            if 'to' in val:
                need(val['to'].email)
        for role_needed in roles_needed:
            # logmessage("One role needed is " + str(role_needed))
            if role_needed == self.last_role:
                # logmessage("Already notified new role " + str(role_needed))
                return False
            if role_needed in kwargs:
                # logmessage("I have info on " + str(role_needed))
                email_info = kwargs[role_needed]
                if 'to' in email_info and 'email' in email_info:
                    # logmessage("I have email info on " + str(role_needed))
                    try:
                        result = send_email(to=email_info['to'], html=email_info['email'].content, subject=email_info['email'].subject)
                    except DAError:
                        result = False
                    if result:
                        self._update(role_needed)
                    return result
        return False


class Name(DAObject):
    """Base class for an object's name."""

    def full(self, **kwargs):  # pylint: disable=unused-argument
        """Returns the full name."""
        return self.text

    def familiar(self):
        """Returns the familiar name."""
        return self.text

    def firstlast(self):
        """This method is included for compatibility with other types of names."""
        return self.text

    def lastfirst(self):
        """This method is included for compatibility with other types of names."""
        return self.text

    def middle_initial(self, with_period=True):  # pylint: disable=unused-argument
        """This method is included for compatibility with other types of names."""
        return ''

    def defined(self):
        """Returns True if the name has been defined.  Otherwise, returns False."""
        return hasattr(self, 'text')

    def __str__(self):
        return str(self.full())
#    def __repr__(self):
#        return repr(self.full())


class IndividualName(Name):
    """The name of an Individual."""

    def init(self, *pargs, **kwargs):
        if 'uses_parts' not in kwargs:
            self.uses_parts = True
        super().init(*pargs, **kwargs)

    def defined(self):
        """Returns True if the name has been defined.  Otherwise, returns False."""
        if not self.uses_parts:
            return super().defined()
        return hasattr(self, 'first')

    def familiar(self):
        """Returns the familiar name."""
        if not self.uses_parts:
            return self.full()
        return self.first

    def full(self, middle='initial', use_suffix=True):  # pylint: disable=arguments-differ
        """Returns the full name.  Has optional keyword arguments middle
        and use_suffix."""
        if not self.uses_parts:
            return super().full()
        names = [self.first.strip()]
        if hasattr(self, 'middle'):
            if middle is False or middle is None:
                pass
            elif middle == 'initial':
                initial = self.middle_initial()
                if initial:
                    names.append(initial)
            elif len(self.middle.strip()):
                names.append(self.middle.strip())
        if hasattr(self, 'last') and len(self.last.strip()):
            names.append(self.last.strip())
        else:
            if hasattr(self, 'paternal_surname') and len(self.paternal_surname.strip()):
                names.append(self.paternal_surname.strip())
            if hasattr(self, 'maternal_surname') and len(self.maternal_surname.strip()):
                names.append(self.maternal_surname.strip())
        if hasattr(self, 'suffix') and use_suffix and len(self.suffix.strip()):
            names.append(self.suffix.strip())
        return " ".join(names)

    def firstlast(self):
        """Returns the first name followed by the last name."""
        if not self.uses_parts:
            return super().firstlast()
        return self.first + " " + self.last

    def lastfirst(self):
        """Returns the last name followed by a comma, followed by the
        last name, followed by the suffix (if a suffix exists)."""
        if not self.uses_parts:
            return super().lastfirst()
        output = self.last
        if hasattr(self, 'suffix') and self.suffix and len(self.suffix.strip()):
            output += " " + self.suffix
        output += ", " + self.first
        if hasattr(self, 'middle'):
            initial = self.middle_initial()
            if initial:
                output += " " + initial
        return output

    def middle_initial(self, with_period=True):
        """Returns the middle initial, or the empty string if the name does not have a middle component."""
        if len(self.middle.strip()) == 0:
            return ''
        if with_period:
            return self.middle[0].strip() + '.'
        return self.middle[0].strip()


class Address(DAObject):
    """A geographic address."""
    LatitudeLongitudeClass = LatitudeLongitude

    def init(self, *pargs, **kwargs):
        if 'location' not in kwargs:
            self.initializeAttribute('location', self.LatitudeLongitudeClass)
        if 'geolocated' in kwargs:
            kwargs['_geocoded'] = kwargs['geolocated']
        if '_geocoded' not in kwargs:
            self._geocoded = False
        if 'geolocated' not in kwargs:
            self.geolocated = False
        if not hasattr(self, 'city_only'):
            self.city_only = False
        super().init(*pargs, **kwargs)

    def __str__(self):
        return str(self.block())

    def on_one_line(self, include_unit=True, omit_default_country=True, language=None, show_country=None):
        """Returns a one-line address.  Primarily used internally for geocoding."""
        output = ""
        if self.city_only is False:
            if (not hasattr(self, 'address')) and hasattr(self, 'street_number') and hasattr(self, 'street'):
                output += str(self.street_number) + " " + str(self.street)
            else:
                output += str(self.address)
            if include_unit:
                the_unit = self.formatted_unit(language=language)
                if the_unit != '':
                    output += ", " + the_unit
            output += ", "
        # if hasattr(self, 'sublocality') and self.sublocality:
        #    output += str(self.sublocality) + ", "
        if hasattr(self, 'sublocality_level_1') and self.sublocality_level_1:
            if not (hasattr(self, 'street_number') and self.street_number == self.sublocality_level_1):
                output += str(self.sublocality_level_1) + ", "
        output += str(self.city)
        if hasattr(self, 'state') and self.state:
            output += ", " + str(self.state)
        if hasattr(self, 'zip') and self.zip:
            output += " " + str(self.zip)
        elif hasattr(self, 'postal_code') and self.postal_code:
            output += " " + str(self.postal_code)
        if show_country is None and hasattr(self, 'country') and self.country and ((not omit_default_country) or get_country() != self.country):
            show_country = True
        if show_country:
            output += ", " + country_name(self._get_country())
        return output

    def _map_info(self):
        if (self.location.gathered and self.location.known) or self.geocode():
            if hasattr(self.location, 'description'):
                the_info = self.location.description
            else:
                the_info = ''
            result = {'latitude': self.location.latitude, 'longitude': self.location.longitude, 'info': the_info}
            if hasattr(self, 'icon'):
                result['icon'] = self.icon
            return [result]
        return None

    def was_geocoded(self):
        """Returns True or False depending on whether the geocoding process has been performed."""
        if hasattr(self, '_geocoded'):
            return self._geocoded
        return self.geolocated

    def was_geocoded_successfully(self):
        """Returns True or False depending on whether the geocoding process has been performed and has been performed successfully."""
        if hasattr(self, '_geocoded'):
            if not self._geocoded:
                return False
        elif not self.geolocated:
            return False
        if hasattr(self, '_geocode_success'):
            return self._geocode_success
        if hasattr(self, '_geocode_response') and len(self._geocode_response):
            return True
        if hasattr(self, 'geolocate_response') and len(self.geolocate_response):
            return True
        return self.geolocate_success

    def get_geocode_response(self):
        """Returns the raw data that the geocoding service returned."""
        if hasattr(self, '_geocode_response'):
            return self._geocode_response
        if hasattr(self, 'geolocate_response'):
            return self.geolocate_response
        if hasattr(self, 'norm'):
            if hasattr(self.norm, '_geocode_response'):
                return self.norm._geocode_response
            if hasattr(self.norm, 'geolocate_response'):
                return self.norm.geolocate_response
        return []

    def geolocate(self, address=None, reset=False):
        """This exists for backward compatibility only. Use .geocode()."""
        return self.geocode(address=address, reset=reset)

    def geocode(self, address=None, reset=False):
        """Determines the latitude and longitude of the location from its components.  If an address is supplied, the address fields that are not already populated will be populated with the result of the geocoding of the selected address."""
        if reset:
            self.reset_geocoding()
        if address is None:
            if hasattr(self, '_geocoded'):
                if self.geolocated != self._geocoded:
                    self._geocoded = self.geolocated
                if self._geocoded:
                    return self._geocode_success  # pylint: disable=access-member-before-definition
            elif self.geolocated:
                return self.geolocate_success  # pylint: disable=access-member-before-definition
            the_address = self.on_one_line(omit_default_country=False)
        else:
            the_address = address
        # logmessage("geocode: trying to geocode " + str(the_address))
        geocoder_service = server.daconfig.get('geocoder service', 'google maps')
        if geocoder_service == 'google maps':
            geocoder = docassemble.base.geocode.GoogleV3GeoCoder(server=server)
        elif geocoder_service == 'azure maps':
            geocoder = docassemble.base.geocode.AzureMapsGeoCoder(server=server)
        else:
            self._geocoded = True
            self.geolocated = True
            self._geocode_success = False
            self.geolocate_success = False
            return False
        if not geocoder.config_ok():
            self._geocoded = True
            self.geolocated = True
            self._geocode_success = False
            self.geolocate_success = False
            return False
        geocoder.initialize()
        try_number = 0
        success = False
        while not success and try_number < 2:
            try:
                success = geocoder.geocode(the_address, language=get_language())
                assert hasattr(geocoder.data, 'longitude')
                assert success
            except Exception as the_err:
                logmessage(the_err.__class__.__name__ + ": " + str(the_err))
                try_number += 1
                time.sleep(try_number)
                success = False
        self._geocoded = True
        self.geolocated = True
        if success:
            self._geocode_success = True
            self.geolocate_success = True
            self.location.gathered = True
            self.location.known = True
            self.location.latitude = geocoder.data.latitude
            self.location.longitude = geocoder.data.longitude
            self._geocode_response = geocoder.data.raw
            self.geolocate_response = self._geocode_response
            if hasattr(self, 'norm'):
                delattr(self, 'norm')
            if hasattr(self, 'norm_long'):
                delattr(self, 'norm_long')
            self.initializeAttribute('norm', self.__class__)
            self.initializeAttribute('norm_long', self.__class__)
            geocoder.populate_address(self)
            self.norm._geocoded = True
            self.norm.geolocated = True
            self.norm.location.gathered = True
            self.norm.location.known = True
            self.norm.location.latitude = geocoder.data.latitude
            self.norm.location.longitude = geocoder.data.longitude
            try:
                self.norm.location.description = self.norm.block()
            except Exception as err:
                logmessage("Normalized address was incomplete: " + str(err))
                self._geocode_success = False
                self.geolocate_success = False
            self.norm._geocode_response = geocoder.data.raw
            self.norm.geolocate_response = self.norm._geocode_response
            self.norm_long._geocoded = True
            self.norm_long.geolocated = True
            self.norm_long.location.gathered = True
            self.norm_long.location.known = True
            self.norm_long.location.latitude = geocoder.data.latitude
            self.norm_long.location.longitude = geocoder.data.longitude
            try:
                self.norm_long.location.description = self.norm_long.block()
            except:
                logmessage("Normalized address was incomplete")
                self._geocode_success = False
                self.geolocate_success = False
            self.norm_long._geocode_response = geocoder.data.raw
            self.norm_long.geolocate_response = self.norm_long._geocode_response
            if address is not None:
                self.normalize()
            try:
                self.location.description = self.block()
            except:
                self.location.description = ''
        else:
            logmessage("geocode: Valid not ok.")
            self._geocode_success = False
            self.geolocate_success = False
        # logmessage(str(self.__dict__))
        return self._geocode_success

    def normalize(self, long_format=False):
        if not self.geocode():
            return False
        the_instance_name = self.instanceName
        the_norm = self.norm  # pylint: disable=access-member-before-definition
        the_norm_long = self.norm_long  # pylint: disable=access-member-before-definition
        if long_format:
            target = copy.deepcopy(the_norm_long)
        else:
            target = copy.deepcopy(the_norm)
        for name in target.__dict__:
            setattr(self, name, getattr(target, name))
        self._set_instance_name_recursively(the_instance_name)
        self.norm = the_norm
        self.norm_long = the_norm_long
        return True

    def reset_geolocation(self):
        """This exists for backward compatibility only. Use .reset_geocoding()."""
        return self.reset_geocoding()

    def reset_geocoding(self):
        """Resets the geocoding information"""
        self.delattr('norm', 'geolocate_success', 'geolocate_response', '_geocode_success', '_geocode_response', 'norm_long', 'one_line')
        self._geocoded = False
        self.geolocated = False
        self.location.delattr('gathered', 'known', 'latitude', 'longitude', 'description')

    def block(self, language=None, international=False, show_country=None):
        """Returns the address formatted as a block, as in a mailing."""
        if this_thread.evaluation_context == 'docx':
            line_breaker = '</w:t><w:br/><w:t xml:space="preserve">'
        else:
            line_breaker = " [NEWLINE] "
        if international:
            i18n_address = {}
            if (not hasattr(self, 'address')) and hasattr(self, 'street_number') and hasattr(self, 'street'):
                i18n_address['street_address'] = str(self.street_number) + " " + str(self.street)
            else:
                i18n_address['street_address'] = str(self.address)
            the_unit = self.formatted_unit(language=language)
            if the_unit != '':
                i18n_address['street_address'] += '\n' + the_unit
            if hasattr(self, 'sublocality_level_1') and self.sublocality_level_1:
                i18n_address['city_area'] = str(self.sublocality_level_1)
            i18n_address['city'] = str(self.city)
            if hasattr(self, 'state') and self.state:
                i18n_address['country_area'] = str(self.state)
            if hasattr(self, 'zip') and self.zip:
                i18n_address['postal_code'] = str(self.zip)
            elif hasattr(self, 'postal_code') and self.postal_code:
                i18n_address['postal_code'] = str(self.postal_code)
            i18n_address['country_code'] = self._get_country()
            return i18naddress.format_address(i18n_address).replace('\n', line_breaker)
        output = ""
        if self.city_only is False:
            if (not hasattr(self, 'address')) and hasattr(self, 'street_number') and hasattr(self, 'street'):
                output += str(self.street_number) + " " + str(self.street) + line_breaker
            else:
                output += str(self.address) + line_breaker
            the_unit = self.formatted_unit(language=language)
            if the_unit != '':
                output += the_unit + line_breaker
        if hasattr(self, 'sublocality_level_1') and self.sublocality_level_1:
            output += str(self.sublocality_level_1) + line_breaker
        output += str(self.city)
        if hasattr(self, 'state') and self.state:
            output += ", " + str(self.state)
        if hasattr(self, 'zip') and self.zip:
            output += " " + str(self.zip)
        elif hasattr(self, 'postal_code') and self.postal_code:
            output += " " + str(self.postal_code)
        if show_country is None and hasattr(self, 'country') and self.country and get_country() != self.country:
            show_country = True
        if show_country:
            output += line_breaker + country_name(self._get_country())
        return output

    def _get_country(self):
        if hasattr(self, 'country') and isinstance(self.country, str):
            country = self.country
        else:
            country = None
        if not country:
            country = get_country()
        if not country:
            country = 'US'
        try:
            country = iso_country(country)
        except:
            logmessage("Invalid country code " + repr(country))
            country = 'US'
        return country

    def formatted_unit(self, language=None, require=False):
        """Returns the unit, formatted appropriately"""
        if not hasattr(self, 'unit') and not hasattr(self, 'floor') and not hasattr(self, 'room'):
            if require:
                self.unit  # pylint: disable=pointless-statement
            else:
                return ''
        if hasattr(self, 'unit') and self.unit != '' and self.unit is not None:
            if not re.search(r'unit|floor|suite|apt|apartment|room|ste|fl', str(self.unit), flags=re.IGNORECASE):
                return word("Unit", language=language) + " " + str(self.unit)
            return str(self.unit)
        if hasattr(self, 'floor') and self.floor != '' and self.floor is not None:
            return word("Floor", language=language) + " " + str(self.floor)
        if hasattr(self, 'room') and self.room != '' and self.room is not None:
            return word("Room", language=language) + " " + str(self.room)
        return ''

    def line_one(self, language=None):
        """Returns the first line of the address, including the unit
        number if there is one."""
        if self.city_only:
            return ''
        if (not hasattr(self, 'address')) and hasattr(self, 'street_number') and hasattr(self, 'street'):
            output = str(self.street_number) + " " + str(self.street)
        else:
            output = str(self.address)
        the_unit = self.formatted_unit(language=language)
        if the_unit != '':
            output += ", " + the_unit
        return output

    def line_two(self, language=None):  # pylint: disable=unused-argument
        """Returns the second line of the address, including the city,
        state and zip code."""
        output = ""
        # if hasattr(self, 'sublocality') and self.sublocality:
        #    output += str(self.sublocality) + ", "
        if hasattr(self, 'sublocality_level_1') and self.sublocality_level_1:
            output += str(self.sublocality_level_1) + ", "
        output += str(self.city)
        if hasattr(self, 'state') and self.state:
            output += ", " + str(self.state)
        if hasattr(self, 'zip') and self.zip:
            output += " " + str(self.zip)
        elif hasattr(self, 'postal_code') and self.postal_code:
            output += " " + str(self.postal_code)
        return output


def iso_country(country, part='alpha_2'):
    """Returns a best-guess ISO 3166-1 country information given a country
    name.  The optional keyword parameter "part" can be alpha_2,
    alpha_3, name, or official_name.  The default "part" is alpha_2.

    """
    try:
        guess = pycountry.countries.search_fuzzy(country)
        assert len(guess) > 0
    except:
        raise DAError("Invalid country: " + str(country))
    if part == 'alpha_2':
        return guess[0].alpha_2
    if part == 'alpha_3':
        return guess[0].alpha_3
    if part == 'name':
        return guess[0].name
    if part == 'numeric':
        return guess[0].numeric
    if part == 'official_name':
        return guess[0].official_name
    raise DAError('iso_country: unknown part')


class City(Address):
    """A geographic address specific only to a city."""

    def init(self, *pargs, **kwargs):
        self.city_only = True
        super().init(*pargs, **kwargs)


class Thing(DAObject):
    """Represents something with a name."""
    NameClass = Name

    def init(self, *pargs, **kwargs):
        if not hasattr(self, 'name') and 'name' not in kwargs:
            self.initializeAttribute('name', self.NameClass)
        if 'name' in kwargs and isinstance(kwargs['name'], str):
            if not hasattr(self, 'name'):
                self.initializeAttribute('name', self.NameClass)
            self.name.text = kwargs['name']
            del kwargs['name']
        super().init(*pargs, **kwargs)

    def __setattr__(self, attrname, the_value):
        if attrname == 'name' and isinstance(the_value, str):
            self.name.text = the_value
        else:
            super().__setattr__(attrname, the_value)

    def __str__(self):
        return str(self.name.full())


class Event(DAObject):
    """A DAObject with pre-set attributes address, which is a City, and
    location, which is a LatitudeLongitude.

    """
    CityClass = City
    LatitudeLongitudeClass = LatitudeLongitude

    def init(self, *pargs, **kwargs):
        if 'address' not in kwargs:
            self.initializeAttribute('address', self.CityClass)
        if 'location' not in kwargs:
            self.initializeAttribute('location', self.LatitudeLongitudeClass)
        super().init(*pargs, **kwargs)

    def __str__(self):
        return str(self.address)


class Person(DAObject):
    """Represents a legal or natural person."""
    NameClass = Name
    AddressClass = Address
    LatitudeLongitudeClass = LatitudeLongitude

    def init(self, *pargs, **kwargs):
        if not hasattr(self, 'name') and 'name' not in kwargs:
            self.initializeAttribute('name', self.NameClass)
        if 'address' not in kwargs:
            self.initializeAttribute('address', self.AddressClass)
        if 'location' not in kwargs:
            self.initializeAttribute('location', self.LatitudeLongitudeClass)
        if 'name' in kwargs and isinstance(kwargs['name'], str):
            if not hasattr(self, 'name'):
                self.initializeAttribute('name', self.NameClass)
            self.name.text = kwargs['name']
            del kwargs['name']
        # if 'roles' not in kwargs:
        #     self.roles = set()
        super().init(*pargs, **kwargs)

    def _map_info(self):
        if not self.location.known:  # pylint: disable=access-member-before-definition
            if (self.address.location.gathered and self.address.location.known) or self.address.geocode():
                self.location = self.address.location
        if self.location.gathered and self.location.known:
            if self.name.defined():
                the_info = self.name.full()
            else:
                the_info = capitalize(self.object_name())
            if hasattr(self.location, 'description') and self.location.description != '':
                the_info += " [NEWLINE] " + self.location.description
            result = {'latitude': self.location.latitude, 'longitude': self.location.longitude, 'info': the_info}
            if hasattr(self, 'icon'):
                result['icon'] = self.icon
            elif self is this_thread.global_vars.user:
                result['icon'] = {'path': 'CIRCLE', 'scale': 5, 'strokeColor': 'blue'}
            return [result]
        return None

    def identified(self):
        """Returns True if the person's name has been set.  Otherwise, returns False."""
        if hasattr(self.name, 'text'):
            return True
        return False

    def __setattr__(self, attrname, the_value):
        if attrname == 'name' and isinstance(the_value, str):
            self.name.text = the_value
        else:
            super().__setattr__(attrname, the_value)

    def __str__(self):
        return str(self.name.full())

    def pronoun_objective(self, **kwargs):
        """Returns "it" or "It" depending on the value of the optional
        keyword argument "capitalize." """
        output = word('it', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def possessive(self, target, **kwargs):
        """Given a word like "fish," returns "your fish" or
        "John Smith's fish," depending on whether the person is the user."""
        if self is this_thread.global_vars.user:
            return your(target, **kwargs)
        return possessify(self, target, **kwargs)

    def object_possessive(self, target, **kwargs):
        """Given a word, returns a phrase indicating possession, but
        uses the variable name rather than the object's actual name."""
        if self is this_thread.global_vars.user:
            return your(target, **kwargs)
        return super().object_possessive(target, **kwargs)

    def is_are_you(self, **kwargs):
        """Returns "are you" if the object is the user, otherwise returns
        "is" followed by the object name."""
        if self is this_thread.global_vars.user:
            output = word('are you', **kwargs)
        else:
            output = is_word(str(self), **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def is_user(self):
        """Returns True if the person is the user, otherwise False."""
        return self is this_thread.global_vars.user

    def address_block(self, language=None, international=False, show_country=False):
        """Returns the person name address as a block, for use in mailings."""
        if this_thread.evaluation_context == 'docx':
            return self.name.full() + '</w:t><w:br/><w:t xml:space="preserve">' + self.address.block(language=language, international=international, show_country=show_country)
        return "[FLUSHLEFT] " + self.name.full() + " [NEWLINE] " + self.address.block(language=language, international=international, show_country=show_country)

    def sms_number(self, country=None):
        """Returns the person's mobile_number, if defined, otherwise the phone_number."""
        if hasattr(self, 'mobile_number'):
            the_number = self.mobile_number
            if hasattr(self, 'uses_whatsapp'):
                the_number = 'whatsapp:' + str(self.mobile_number)
        else:
            the_number = self.phone_number
        if country is None:
            if hasattr(self, 'country'):
                country = self.country
            elif hasattr(self, 'address') and hasattr(self.address, 'country'):
                country = self.address.country
            else:
                country = get_country()
        return phone_number_in_e164(the_number, country=country)

    def facsimile_number(self, country=None):
        """Returns the person's fax_number, formatted appropriately."""
        the_number = self.fax_number
        if country is not None:
            the_country = country
        elif hasattr(self, 'country'):
            the_country = self.country
        elif hasattr(self, 'address') and hasattr(self.address, 'country'):
            the_country = self.address.country
        else:
            the_country = get_country()
        return phone_number_in_e164(the_number, country=the_country)

    def email_address(self, include_name=None):
        """Returns an e-mail address for the person."""
        if include_name is True or (include_name is not False and self.name.defined()):
            return '"' + nodoublequote(self.name) + '" <' + str(self.email) + '>'
        return str(self.email)
    # def age(self):
    #     if (hasattr(self, 'age_in_years')):
    #         return self.age_in_years
    #     today = date.today()
    #     born = self.birthdate
    #     try:
    #         birthday = born.replace(year=today.year)
    #     except ValueError:
    #         birthday = born.replace(year=today.year, month=born.month+1, day=1)
    #     if birthday > today:
    #         return today.year - born.year - 1
    #     else:
    #         return today.year - born.year

    def do_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "do you eat" or "does John Smith eat,"
        depending on whether the person is the user."""
        if self == this_thread.global_vars.user:
            return do_you(the_verb, **kwargs)
        return does_a_b(self, the_verb, **kwargs)

    def did_question(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "did you eat" or "did John Smith eat,"
        depending on whether the person is the user."""
        if self == this_thread.global_vars.user:
            return did_you(the_verb, **kwargs)
        return did_a_b(self, the_verb, **kwargs)

    def were_question(self, the_target, **kwargs):
        """Given a target like "married", returns "were you married" or "was
        John Smith married," depending on whether the person is the
        user."""
        if self == this_thread.global_vars.user:
            return were_you(the_target, **kwargs)
        return was_a_b(self, the_target, **kwargs)

    def have_question(self, the_target, **kwargs):
        """Given a target like "", returns "have you married" or "has
        John Smith married," depending on whether the person is the
        user."""
        if self == this_thread.global_vars.user:
            return have_you(the_target, **kwargs)
        return has_a_b(self, the_target, **kwargs)

    def does_verb(self, the_verb, **kwargs):
        """Given a verb like "eat," returns "eat" or "eats"
        depending on whether the person is the user."""
        if self == this_thread.global_vars.user:
            tense = '2sg'
        else:
            tense = '3sg'
        if ('past' in kwargs and kwargs['past'] is True) or ('present' in kwargs and kwargs['present'] is False):
            return verb_past(the_verb, tense, **kwargs)
        return verb_present(the_verb, tense, **kwargs)

    def did_verb(self, the_verb, **kwargs):
        """Like does_verb(), except uses the past tense of the verb."""
        if self == this_thread.global_vars.user:
            tense = "2sgp"
        else:
            tense = "3sgp"
        # logmessage(the_verb + " " + tense)
        return verb_past(the_verb, tense, **kwargs)

    def subject(self, **kwargs):
        """Returns "you" or the person's name, depending on whether the
        person is the user."""
        if self == this_thread.global_vars.user:
            output = word('you', **kwargs)
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output


class Individual(Person):
    """Represents a natural person."""
    NameClass = IndividualName

    def init(self, *pargs, **kwargs):
        if 'name' not in kwargs and not hasattr(self, 'name'):
            self.initializeAttribute('name', self.NameClass)
        # if 'child' not in kwargs and not hasattr(self, 'child'):
        #     self.child = ChildList()
        # if 'income' not in kwargs and not hasattr(self, 'income'):
        #     self.income = Income()
        # if 'asset' not in kwargs and not hasattr(self, 'asset'):
        #     self.asset = Asset()
        # if 'expense' not in kwargs and not hasattr(self, 'expense'):
        #     self.expense = Expense()
        if (not hasattr(self, 'name')) and 'name' in kwargs and isinstance(kwargs['name'], str):
            self.initializeAttribute('name', self.NameClass)
            self.name.uses_parts = False
            self.name.text = kwargs['name']
        super().init(*pargs, **kwargs)

    def familiar(self):
        """Returns the individual's familiar name."""
        return self.name.familiar()
    # def get_parents(self, tree, create=False):
    #     return self.get_relation('child', tree, create=create)
    # def get_spouse(self, tree, create=False):
    #     return self.get_peer_relation('spouse', tree, create=create)
    # def set_spouse(self, target, tree):
    #     return self.set_peer_relationship(self, target, "spouse", tree, replace=True)
    # def is_spouse_of(self, target, tree):
    #     return self.is_peer_relation(target, 'spouse', tree)

    def gather_family(self, tree, up=1, down=1):
        pass

    def identified(self):
        """Returns True if the individual's name has been set.  Otherwise, returns False."""
        if hasattr(self.name, 'first'):
            return True
        return False

    def age_in_years(self, decimals=False, as_of=None):
        """Returns the individual's age in years, based on self.birthdate."""
        if hasattr(self, 'age'):
            if decimals:
                return float(self.age)
            return int(self.age)
        if as_of is None:
            comparator = current_datetime()
        else:
            comparator = as_datetime(as_of)
        birth_date = as_datetime(self.birthdate)
        rd = dateutil.relativedelta.relativedelta(comparator, birth_date)
        if decimals:
            return float(rd.years)
        return int(rd.years)

    def first_name_hint(self):
        """If the individual is the user and the user is logged in and
        the user has set up a name in the user profile, this returns
        the user's first name.  Otherwise, returns a blank string."""
        if self is this_thread.global_vars.user and this_thread.current_info['user']['is_authenticated'] and 'firstname' in this_thread.current_info['user'] and this_thread.current_info['user']['firstname']:
            return this_thread.current_info['user']['firstname']
        return ''

    def last_name_hint(self):
        """If the individual is the user and the user is logged in and
        the user has set up a name in the user profile, this returns
        the user's last name.  Otherwise, returns a blank string."""
        if self is this_thread.global_vars.user and this_thread.current_info['user']['is_authenticated'] and 'lastname' in this_thread.current_info['user'] and this_thread.current_info['user']['lastname']:
            return this_thread.current_info['user']['lastname']
        return ''

    def salutation(self, **kwargs):
        """Returns "Mr.", "Ms.", etc."""
        return salutation(self, **kwargs)

    def pronoun_possessive(self, target, **kwargs):
        """Given a word like "fish," returns "her fish" or "his fish," as appropriate."""
        if self == this_thread.global_vars.user and ('thirdperson' not in kwargs or not kwargs['thirdperson']):
            output = your(target, **kwargs)
        elif self.gender == 'female':
            output = her(target, **kwargs)
        elif self.gender == 'other':
            output = their(target, **kwargs)
        else:
            output = his(target, **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def pronoun(self, **kwargs):
        """Returns a pronoun like "you," "her," or "him," as appropriate."""
        if self == this_thread.global_vars.user:
            output = word('you', **kwargs)
        if self.gender == 'female':
            output = word('her', **kwargs)
        elif self.gender == 'other':
            output = word('them', **kwargs)
        else:
            output = word('him', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def pronoun_objective(self, **kwargs):
        """Same as pronoun()."""
        return self.pronoun(**kwargs)

    def pronoun_subjective(self, **kwargs):
        """Returns a pronoun like "you," "she," or "he," as appropriate."""
        if self == this_thread.global_vars.user and ('thirdperson' not in kwargs or not kwargs['thirdperson']):
            output = word('you', **kwargs)
        elif self.gender == 'female':
            output = word('she', **kwargs)
        elif self.gender == 'other':
            output = word('they', **kwargs)
        else:
            output = word('he', **kwargs)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def yourself_or_name(self, **kwargs):
        """Returns a "yourself" if the individual is the user, otherwise
        returns the individual's name."""
        if self == this_thread.global_vars.user:
            output = word('yourself', **kwargs)
        else:
            output = str(self)
        if 'capitalize' in kwargs and kwargs['capitalize']:
            return capitalize(output)
        return output

    def __setattr__(self, attrname, the_value):
        if attrname == 'name' and isinstance(the_value, str):
            if isinstance(self.name, IndividualName):
                self.name.uses_parts = False
            self.name.text = the_value
        else:
            super().__setattr__(attrname, the_value)

    def __str__(self):
        if hasattr(self, 'use_familiar') and self.use_familiar and isinstance(self.name, IndividualName) and self.name.uses_parts:
            return str(self.name.first)
        return super().__str__()


class ChildList(DAList):
    """Represents a list of children."""
    ChildClass = Individual

    def init(self, *pargs, **kwargs):
        self.object_type = self.ChildClass
        super().init(*pargs, **kwargs)


class Value(DAObject):
    """Represents a value in a FinancialList."""

    def amount(self):
        """Returns the value's amount, or 0 if the value does not exist."""
        if not self.exists:
            return 0
        return Decimal(self.value)

    def __str__(self):
        return str(self.amount())

    def __float__(self):
        return float(self.amount())

    def __int__(self):
        return int(self.__float__())

    def __le__(self, other):
        return self.value <= (other.value if isinstance(other, Value) else other)

    def __ge__(self, other):
        return self.value >= (other.value if isinstance(other, Value) else other)

    def __gt__(self, other):
        return self.value > (other.value if isinstance(other, Value) else other)

    def __lt__(self, other):
        return self.value < (other.value if isinstance(other, Value) else other)

    def __eq__(self, other):
        return self.value == (other.value if isinstance(other, Value) else other)

    def __ne__(self, other):
        return self.value != (other.value if isinstance(other, Value) else other)

    def __hash__(self):
        return hash((self.instanceName,))


class PeriodicValue(Value):
    """Represents a value in a PeriodicFinancialList."""

    def amount(self, period_to_use=1):
        """Returns the periodic value's amount for a full period,
        or 0 if the value does not exist."""
        if not self.exists:
            return 0
        ensure_definition(period_to_use)
        return (Decimal(self.value) * Decimal(self.period)) / Decimal(period_to_use)


class FinancialList(DADict):
    """Represents a set of currency amounts."""
    ValueClass = Value

    def init(self, *pargs, **kwargs):
        self.object_type = self.ValueClass
        super().init(*pargs, **kwargs)

    def total(self):
        """Returns the total value in the list, gathering the list items if necessary."""
        self._trigger_gather()
        result = 0
        for item in sorted(self.elements.keys()):
            if self[item].exists:
                result += Decimal(self[item].value)
        return result

    def existing_items(self):
        """Returns a list of types of amounts that exist within the financial list."""
        self._trigger_gather()
        return [key for key in sorted(self.elements.keys()) if self[key].exists]

    def _new_item_init_callback(self):
        self.elements[self.new_item_name].exists = True
        if hasattr(self, 'new_item_value'):
            self.elements[self.new_item_name].value = self.new_item_value
            del self.new_item_value
        return super()._new_item_init_callback()

    def __str__(self):
        return str(self.total())


class PeriodicFinancialList(FinancialList):
    """Represents a set of currency items, each of which has an associated period."""
    PeriodicValueClass = PeriodicValue

    def init(self, *pargs, **kwargs):
        self.object_type = self.PeriodicValueClass
        super().init(*pargs, **kwargs)

    def total(self, period_to_use=1):
        """Returns the total periodic value in the list, gathering the list items if necessary."""
        self._trigger_gather()
        result = 0
        if period_to_use == 0:
            return result
        for item in sorted(self.elements.keys()):
            if self.elements[item].exists:
                result += Decimal(self.elements[item].value) * Decimal(self.elements[item].period)
        return result/Decimal(period_to_use)

    def _new_item_init_callback(self):
        if hasattr(self, 'new_item_period'):
            self.elements[self.new_item_name].period = self.new_item_period
            del self.new_item_period
        return super()._new_item_init_callback()


class Income(PeriodicFinancialList):
    """A PeriodicFinancialList representing a person's income."""


class Asset(FinancialList):
    """A FinancialList representing a person's assets."""


class Expense(PeriodicFinancialList):
    """A PeriodicFinancialList representing a person's expenses."""


class OfficeList(DAList):
    """Represents a list of offices of a company or organization."""
    AddressClass = Address

    def init(self, *pargs, **kwargs):
        self.object_type = self.AddressClass
        super().init(*pargs, **kwargs)


class Organization(Person):
    """Represents a company or organization."""
    OfficeListClass = OfficeList

    def init(self, *pargs, **kwargs):
        if 'offices' in kwargs:
            self.initializeAttribute('office', self.OfficeListClass)
            if isinstance(kwargs['offices'], list):
                for office in kwargs['offices']:
                    if isinstance(office, dict):
                        new_office = self.office.appendObject(**office)
                        new_office.geocode()
            del kwargs['offices']
        super().init(*pargs, **kwargs)

    def will_handle(self, problem=None, county=None):
        """Returns True or False depending on whether the organization
        serves the given county and/or handles the given problem."""
        ensure_definition(problem, county)
        if problem:
            if not (hasattr(self, 'handles') and problem in self.handles):
                return False
        if county:
            if not (hasattr(self, 'serves') and county in self.serves):
                return False
        return True

    def _map_info(self):
        the_response = []
        if hasattr(self.office):
            for office in self.office:
                if (office.location.gathered and office.location.known) or office.geocode():
                    if self.name.defined():
                        the_info = self.name.full()
                    else:
                        the_info = capitalize(self.object_name())
                    if hasattr(office.location, 'description') and office.location.description != '':
                        the_info += " [NEWLINE] " + office.location.description
                    this_response = {'latitude': office.location.latitude, 'longitude': office.location.longitude, 'info': the_info}
                    if hasattr(office, 'icon'):
                        this_response['icon'] = office.icon
                    elif hasattr(self, 'icon'):
                        this_response['icon'] = self.icon
                    the_response.append(this_response)
        if len(the_response) > 0:
            return the_response
        return None

# twilio_config = None

# def set_twilio_config(the_config):
#     global twilio_config
#     twilio_config = the_config


def get_sms_session(phone_number, config='default'):
    """Returns the SMS session information for a phone number, or None if no session exists."""
    result = server.get_sms_session(phone_number, config=config)
    for key in ['number', 'tempuser', 'user_id']:
        if key in result:
            del result[key]
    return result


def initiate_sms_session(phone_number, yaml_filename=None, email=None, new=False, send=True, config='default'):
    """Initiates a new SMS session for a phone number, overwriting any that is currently active."""
    server.initiate_sms_session(phone_number, yaml_filename=yaml_filename, email=email, new=new, config=config)
    if send:
        send_sms_invite(to=phone_number, config=config)
    return True


def terminate_sms_session(phone_number, config='default'):
    """Terminates an SMS session for a phone number, whether the session exists or not."""
    return server.terminate_sms_session(phone_number, config=config)


def send_sms_invite(to=None, body='question', config='default'):
    """Sends an SMS message to a phone number, where the message is the
    current interview question the recipient would see if he or she
    texted 'question' to the system.
    """
    if to is None:
        raise DAError("send_sms_invite: no phone number provided")
    phone_number = docassemble.base.functions.phone_number_in_e164(to)
    if phone_number is None:
        raise DAError("send_sms_invite: phone number is invalid")
    the_message = server.sms_body(phone_number, body=body, config=config)
    # logmessage("Sending message " + str(message) + " to " + str(phone_number))
    send_sms(to=phone_number, body=the_message, config=config)


def send_sms(to=None, body=None, template=None, task=None, task_persistent=False, attachments=None, config='default', dry_run=False):
    """Sends a text message and returns whether sending the text was successful."""
    if server.twilio_config is None:
        logmessage("send_sms: ignoring because Twilio not enabled")
        return False
    if config not in server.twilio_config['name']:
        logmessage("send_sms: ignoring because requested configuration does not exist")
        return False
    tconfig = server.twilio_config['name'][config]
    if 'sms' not in tconfig or tconfig['sms'] in [False, None]:
        logmessage("send_sms: ignoring because SMS not enabled")
        return False
    if attachments is None:
        attachments = []
    elif attachments is not list:
        attachments = [attachments]
    if not isinstance(to, (list, DAList)):
        to = [to]
    if len(to) == 0:
        logmessage("send_sms: no recipients identified")
        return False
    if template is not None and body is None:
        body_html = '<html><body>'
        if template.subject is not None:
            body_html += markdown_to_html(template.subject, external=True)
        body_html += markdown_to_html(template.content, external=True) + '</body></html>'
        body_html = re.sub(r'\n', ' ', body_html)
        body = BeautifulSoup(body_html, "html.parser").get_text('\n')
    if body is None:
        body = word("blank message")
    success = True
    media = []
    for attachment in attachments:
        attachment_list = []
        if isinstance(attachment, DAFileCollection):
            subattachment = getattr(attachment, 'pdf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'docx', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'rtf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'tex', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'raw', None)
            if subattachment is not None:
                attachment_list.append(subattachment)
            else:
                logmessage("send_sms: could not find file to attach in DAFileCollection.")
                success = False
        elif isinstance(attachment, DAFile):
            attachment_list.append(attachment)
        elif isinstance(attachment, DAStaticFile):
            attachment_list.append(attachment)
        elif isinstance(attachment, DAFileList):
            attachment_list.extend(attachment.elements)
        elif isinstance(attachment, str) and re.search(r'^https?://', attachment):
            attachment_list.append(attachment)
        else:
            logmessage("send_sms: attachment " + repr(attachment) + " is not valid.")
            success = False
        if success:
            for the_attachment in attachment_list:
                if isinstance(the_attachment, DAFile) and the_attachment.ok:
                    # url = url_start + server.url_for('serve_stored_file', uid=this_thread.current_info['session'], number=the_attachment.number, filename=the_attachment.filename, extension=the_attachment.extension)
                    media.append(the_attachment.url_for(_external=True))
                if isinstance(the_attachment, DAStaticFile):
                    media.append(the_attachment.url_for(_external=True))
                elif isinstance(the_attachment, str):
                    media.append(the_attachment)
    if len(media) > 10:
        logmessage("send_sms: more than 10 attachments were provided; not sending message")
        success = False
    if dry_run:
        success = False
    if success:
        twilio_client = TwilioRestClient(tconfig['account sid'], tconfig['auth token'])
        for recipient in to:
            phone_number = phone_string(recipient)
            if phone_number is not None:
                if phone_number.startswith('whatsapp:'):
                    from_number = 'whatsapp:' + tconfig.get('whatsapp number', tconfig['number'])
                else:
                    from_number = tconfig['number']
                try:
                    if len(media) > 0:
                        twilio_client.messages.create(to=phone_number, from_=from_number, body=body, media_url=media)
                    else:
                        twilio_client.messages.create(to=phone_number, from_=from_number, body=body)
                except Exception as errstr:
                    logmessage("send_sms: failed to send message from " + from_number + " to " + phone_number + ": " + str(errstr))
                    return False
    if success and task is not None:
        mark_task_as_performed(task, persistent=task_persistent)
    return True


class FaxStatus:

    def __init__(self, sid):
        self.sid = sid

    def status(self):
        if self.sid is None:
            return 'not-configured'
        the_json = server.server_redis.get('da:faxcallback:sid:' + self.sid)
        if the_json is None:
            return 'no-information'
        info = json.loads(the_json)
        if 'FaxStatus' in info:
            return info['FaxStatus']
        if 'status_text' in info:
            return info['status_text'] or 'no-information'
        if 'status' in info:
            return info['status'] or 'no-information'
        return 'no-information'

    def pages(self):
        if self.sid is None:
            return 0
        the_json = server.server_redis.get('da:faxcallback:sid:' + self.sid)
        if the_json is None:
            return 0
        info = json.loads(the_json)
        if 'NumPages' in info:
            return info['NumPages']
        if 'message_pages' in info:
            return info['message_pages'] or 0
        if 'page_count' in info:
            return info['page_count'] or 0
        return 0

    def info(self):
        if self.sid is None:
            return dict(FaxStatus='not-configured')
        the_json = server.server_redis.get('da:faxcallback:sid:' + self.sid)
        if the_json is None:
            return dict(FaxStatus='no-information')
        info_dict = json.loads(the_json)
        return info_dict

    def received(self):
        the_status = self.status()
        if the_status in ('no-information', 'not-configured'):
            return None
        if the_status in ('received', 'delivered', 'Fax successfully sent'):
            return True
        return False


def send_fax(fax_number, file_object, config='default', country=None):
    if isinstance(file_object, DAFileCollection):
        file_object = file_object._first_file()
    if isinstance(file_object, DAFileList):
        if len(file_object.elements) == 0:
            raise Exception("send_fax: if passing a DAFileList, the DAFileList must have at least one element")
        if len(file_object.elements) == 1:
            file_object = file_object.elements[0]
        else:
            file_object = pdf_concatenate(file_object)
    return FaxStatus(server.send_fax(fax_string(fax_number, country=country), file_object, config, country=country))


def send_email(to=None, sender=None, reply_to=None, cc=None, bcc=None, body=None, html=None, subject="", template=None, task=None, task_persistent=False, attachments=None, mailgun_variables=None, dry_run=False):
    """Sends an e-mail and returns whether sending the e-mail was successful."""
    if attachments is None:
        attachments = []
    if (not isinstance(attachments, (DAList, DASet, abc.Iterable))) or isinstance(attachments, str):
        attachments = [attachments]
    if not isinstance(to, (list, DAList)):
        to = [to]
    if len(to) == 0:
        return False
    if template is not None:
        if subject is None or subject == '':
            subject = template.subject
        body_html = '<html><body>' + template.content_as_html(external=True) + '</body></html>'
        if body is None:
            body = BeautifulSoup(body_html, "html.parser").get_text('\n')
        if html is None:
            html = body_html
    if body is None and html is None:
        body = ""
    if html is None:
        html = '<html><body>' + body + '</body></html>'
    subject = re.sub(r'[\n\r]+', ' ', subject)
    sender_string = email_stringer(sender, first=True, include_name=True)
    reply_to_string = email_stringer(reply_to, first=True, include_name=True)
    to_string = email_stringer(to, include_name=None)
    cc_string = email_stringer(cc, include_name=None)
    bcc_string = email_stringer(bcc, include_name=None)
    # logmessage("Sending mail to: " + repr(dict(subject=subject, recipients=to_string, sender=sender_string, cc=cc_string, bcc=bcc_string, body=body, html=html)))
    msg = Message(subject, sender=sender_string, reply_to=reply_to_string, recipients=to_string, cc=cc_string, bcc=bcc_string, body=body, html=html)
    if mailgun_variables is not None:
        if isinstance(mailgun_variables, dict):
            msg.mailgun_variables = mailgun_variables
        else:
            logmessage("send_email: mailgun_variables must be a dict")
    filenames_used = set()
    success = True
    for attachment in attachments:
        attachment_list = []
        if isinstance(attachment, DAFileCollection):
            subattachment = getattr(attachment, 'pdf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'docx', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'rtf', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'tex', None)
            if subattachment is None:
                subattachment = getattr(attachment, 'raw', None)
            if subattachment is not None:
                attachment_list.append(subattachment)
            else:
                success = False
        elif isinstance(attachment, DAFile):
            attachment_list.append(attachment)
        elif isinstance(attachment, DAStaticFile):
            attachment_list.append(attachment)
        elif isinstance(attachment, DAFileList):
            attachment_list.extend(attachment.elements)
        elif isinstance(attachment, str):
            file_info = server.file_finder(attachment)
            if 'fullpath' in file_info and file_info['fullpath'] is not None:
                failed = True
                with open(file_info['fullpath'], 'rb') as fp:
                    msg.attach(attachment_name(file_info['filename'], filenames_used), file_info['mimetype'], fp.read())
                    failed = False
                if failed:
                    success = False
            else:
                success = False
            continue
        else:
            success = False
        if success:
            for the_attachment in attachment_list:
                if isinstance(the_attachment, DAStaticFile):
                    the_path = the_attachment.path()
                    with open(the_path, 'rb') as fp:
                        the_basename = os.path.basename(the_path)
                        extension, mimetype = server.get_ext_and_mimetype(the_basename)  # pylint: disable=assignment-from-none,unpacking-non-sequence,unused-variable
                        msg.attach(attachment_name(the_basename, filenames_used), mimetype, fp.read())
                    continue
                if the_attachment.ok:
                    if the_attachment.has_specific_filename:
                        file_info = server.file_finder(str(the_attachment.number), filename=the_attachment.filename)
                    else:
                        file_info = server.file_finder(str(the_attachment.number))
                    if 'fullpath' in file_info and file_info['fullpath'] is not None:
                        failed = True
                        with open(file_info['fullpath'], 'rb') as fp:
                            msg.attach(attachment_name(the_attachment.filename, filenames_used), file_info['mimetype'], fp.read())
                            failed = False
                        if failed:
                            success = False
                    else:
                        success = False
    if dry_run:
        success = False
    if success:
        try:
            logmessage("send_email: starting to send")
            server.send_mail(msg)
            logmessage("send_email: finished sending")
        except Exception as errmess:
            logmessage("send_email: sending mail failed with error of " + " type " + str(errmess.__class__.__name__) + ": " + str(errmess))
            success = False
    if success and task is not None:
        mark_task_as_performed(task, persistent=task_persistent)
    return success


def attachment_name(filename, filenames):
    if filename not in filenames:
        filenames.add(filename)
        return filename
    indexno = 1
    parts = os.path.splitext(filename)
    while True:
        new_filename = '%s_%03d%s' % (parts[0], indexno, parts[1])
        if new_filename not in filenames:
            filenames.add(new_filename)
            return new_filename
        indexno += 1


def map_of(*pargs, **kwargs):
    """Inserts into markup a Google Map representing the objects passed as arguments."""
    the_map = {'markers': []}
    all_args = []
    for arg in pargs:
        if isinstance(arg, list):
            all_args.extend(arg)
        else:
            all_args.append(arg)
    for arg in all_args:
        if isinstance(arg, DAObject):
            markers = arg._map_info()
            if markers:
                for marker in markers:
                    if 'icon' in marker and not isinstance(marker['icon'], dict):
                        marker['icon'] = {'url': server.url_finder(marker['icon'])}
                    if 'info' in marker and marker['info']:
                        marker['info'] = markdown_to_html(marker['info'], trim=True, external=True)
                    the_map['markers'].append(marker)
    if 'center' in kwargs:
        the_center = kwargs['center']
        if callable(getattr(the_center, '_map_info', None)):
            markers = the_center._map_info()
            if markers:
                the_map['center'] = markers[0]
    if 'center' not in the_map and len(the_map['markers']) > 0:
        the_map['center'] = the_map['markers'][0]
    if len(the_map['markers']) > 0 or 'center' in the_map:
        return '[MAP ' + re.sub(r'\n', '', codecs.encode(json.dumps(the_map).encode('utf-8'), 'base64').decode()) + ']'
    return word('(Unable to display map)')


def int_or_none(number):
    if number is None:
        return number
    try:
        return int(number)
    except:
        logmessage("Non-number passed to x, y, W, or H")
    return None


def ocr_file_in_background(*pargs, **kwargs):
    """Starts optical character recognition on one or more image files or PDF
    files and returns an object representing the background task created."""
    image_file = pargs[0]
    if len(pargs) > 1:
        ui_notification = pargs[1]
    else:
        ui_notification = None
    if kwargs.get('use_google', False):
        the_task = server.ocr_google_in_background(image_file, kwargs.get('raw_result', False), docassemble.base.functions.this_thread.current_info['session'])  # pylint: disable=assignment-from-none
    else:
        language = kwargs.get('language', None)
        arg_f = int_or_none(kwargs.get('f', None))
        arg_l = int_or_none(kwargs.get('l', None))
        arg_psm = kwargs.get('psm', 6)
        arg_x = int_or_none(kwargs.get('x', None))
        arg_y = int_or_none(kwargs.get('y', None))
        arg_W = int_or_none(kwargs.get('W', None))
        arg_H = int_or_none(kwargs.get('H', None))
        the_message = kwargs.get('message', None)
        args = dict(yaml_filename=this_thread.current_info['yaml_filename'], user=this_thread.current_info['user'], user_code=this_thread.current_info['session'], secret=this_thread.current_info['secret'], url=this_thread.current_info['url'], url_root=this_thread.current_info['url_root'], language=language, f=arg_f, l=arg_l, psm=arg_psm, x=arg_x, y=arg_y, W=arg_W, H=arg_H, extra=ui_notification, message=the_message, pdf=False, preserve_color=False)
        collector = server.ocr_finalize.s(**args)
        todo = []
        indexno = 0
        for item in ocr_page_tasks(image_file, **args):
            todo.append(server.ocr_page.s(indexno, **item))
            indexno += 1
        the_task = server.chord(todo)(collector)  # pylint: disable=assignment-from-none
    if ui_notification is not None:
        worker_key = 'da:worker:uid:' + str(this_thread.current_info['session']) + ':i:' + str(this_thread.current_info['yaml_filename']) + ':userid:' + str(this_thread.current_info['user']['the_user_id'])
        # logmessage("worker_caller: id is " + str(result.obj.id) + " and key is " + worker_key)
        server.server_redis.rpush(worker_key, the_task.id)
    # logmessage("ocr_file_in_background finished")
    return the_task

# def ocr_file_in_background(image_file, ui_notification=None, language=None, psm=6, x=None, y=None, W=None, H=None):
#     """Starts optical character recognition on one or more image files or PDF
#     files and returns an object representing the background task created."""
#     logmessage("ocr_file_in_background: started")
#     return server.async_ocr(image_file, ui_notification=ui_notification, language=language, psm=psm, x=x, y=y, W=W, H=H, user_code=this_thread.current_info.get('session', None))


def get_work_bucket():
    bucket_name = server.daconfig['google'].get('work bucket', None)
    if bucket_name is None:
        raise Exception("Cannot use Google Storage unless there is a work bucket configured in the google configuration")
    api = DAGoogleAPI()
    client = api.google_cloud_storage_client()
    try:
        bucket = client.get_bucket(bucket_name)
    except:
        try:
            bucket = client.create_bucket(bucket_name)
        except Exception as err:
            raise Exception("failed to create bucket named " + bucket_name + ": " + str(err))
    return bucket


def google_ocr_file(image_file, raw_result=False):
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    api = docassemble.base.util.DAGoogleAPI()
    client = api.google_cloud_vision_client()
    if raw_result:
        output = []
    else:
        output = ''
    bucket = None
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
                return word("(Not a readable image file)")
            path = doc.path()
            if doc.extension == 'pdf':
                if bucket is None:
                    bucket = get_work_bucket()
                if isinstance(doc, DAFile):
                    input_prefix = 'ocr/ocr_input_' + str(doc.number).zfill(12) + '.pdf'
                    output_prefix = 'ocr/ocr_result_' + str(doc.number).zfill(12)
                else:
                    suffix = random_alphanumeric(12) + '_' + space_to_underscore(os.path.basename(path))
                    input_prefix = 'ocr/ocr_input_' + suffix
                    output_prefix = 'ocr/ocr_result_' + suffix
                blob = bucket.blob(input_prefix)
                blob.upload_from_filename(path)
                gcs_source_uri = 'gs://' + bucket.name + '/' + input_prefix
                gcs_destination_uri = 'gs://' + bucket.name + '/' + output_prefix
                batch_size = 2
                mime_type = 'application/pdf'

                feature = google.cloud.vision.Feature(
                    type_=google.cloud.vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

                gcs_source = google.cloud.vision.GcsSource(uri=gcs_source_uri)
                input_config = google.cloud.vision.InputConfig(
                    gcs_source=gcs_source, mime_type=mime_type)

                gcs_destination = google.cloud.vision.GcsDestination(uri=gcs_destination_uri)
                output_config = google.cloud.vision.OutputConfig(
                    gcs_destination=gcs_destination, batch_size=batch_size)

                async_request = google.cloud.vision.AsyncAnnotateFileRequest(
                    features=[feature], input_config=input_config,
                    output_config=output_config)

                operation = client.async_batch_annotate_files(
                    requests=[async_request])

                operation.result(timeout=420)
                blob.delete()
                blob_list = [blob for blob in list(bucket.list_blobs(prefix=output_prefix)) if not blob.name.endswith('/')]
                for blob in blob_list:
                    json_string = blob.download_as_string()
                    the_response = json.loads(json_string)
                    if raw_result:
                        output.append(the_response)
                    else:
                        for item in the_response['responses']:
                            output += item['fullTextAnnotation']['text'] + "\n"
                for blob in blob_list:
                    blob.delete()
            else:
                image = google.cloud.vision.Image()
                with io.open(path, 'rb') as the_image_file:
                    content = the_image_file.read()
                image = google.cloud.vision.Image(content=content)
                the_response = client.text_detection(image=image)
                if the_response.error.message:
                    raise Exception("Failed to OCR file with Google Cloud Vision: " + the_response.error.message)
                if raw_result:
                    output.append(json.loads(google.cloud.vision.AnnotateImageResponse.to_json(the_response)))
                else:
                    for text in the_response.text_annotations:
                        output += text.description + "\n"
    return output


def ocr_file(image_file, language=None, psm=6, f=None, l=None, x=None, y=None, W=None, H=None, use_google=False, raw_result=False):  # noqa: E741
    """Runs optical character recognition on one or more image files or PDF
    files and returns the recognized text."""
    if not isinstance(image_file, (DAFile, DAFileList)):
        return word("(Not a DAFile or DAFileList object)")
    if use_google:
        return google_ocr_file(image_file, raw_result=raw_result)
    x = int_or_none(x)
    y = int_or_none(y)
    W = int_or_none(W)
    H = int_or_none(H)
    pdf_to_ppm = get_config("pdftoppm")
    if pdf_to_ppm is None:
        pdf_to_ppm = 'pdftoppm'
    ocr_resolution = get_config("ocr dpi")
    if ocr_resolution is None:
        ocr_resolution = '300'
    lang = get_ocr_language(language)
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    temp_directory_list = []
    file_list = []
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
                return word("(Not a readable image file)")
            path = doc.path()
            if doc.extension == 'pdf':
                directory = tempfile.mkdtemp(prefix='SavedFile')
                temp_directory_list.append(directory)
                prefix = os.path.join(directory, 'page')
                args = [pdf_to_ppm, '-r', str(ocr_resolution)]
                if f is not None:
                    args.extend(['-f', str(f)])
                if l is not None:
                    args.extend(['-l', str(l)])
                if x is not None:
                    args.extend(['-x', str(x)])
                if y is not None:
                    args.extend(['-y', str(y)])
                if W is not None:
                    args.extend(['-W', str(W)])
                if H is not None:
                    args.extend(['-H', str(H)])
                args.extend(['-png', path, prefix])
                try:
                    result = subprocess.run(args, timeout=3600, check=False).returncode
                except subprocess.TimeoutExpired:
                    result = 1
                    logmessage("ocr_file: call to pdftoppm took too long")
                if result > 0:
                    return word("(Unable to extract images from PDF file)")
                file_list.extend(sorted([os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]))
                continue
            file_list.append(path)
    page_text = []
    for page in file_list:
        image = Image.open(page)
        color = ImageEnhance.Color(image)
        bw = color.enhance(0.0)
        bright = ImageEnhance.Brightness(bw)
        brightened = bright.enhance(1.5)
        contrast = ImageEnhance.Contrast(brightened)
        final_image = contrast.enhance(2.0)
        file_to_read = tempfile.TemporaryFile()
        final_image.save(file_to_read, "PNG")
        file_to_read.seek(0)
        try:
            text = subprocess.check_output(['tesseract', 'stdin', 'stdout', '-l', str(lang), '--psm', str(psm)], stdin=file_to_read).decode('utf-8', 'ignore')
        except subprocess.CalledProcessError as err:
            raise Exception("ocr_file: failed to list available languages: " + str(err) + " " + str(err.output.decode()))
        page_text.append(text)
    for directory in temp_directory_list:
        shutil.rmtree(directory)
    return "\f".join(page_text)


def read_qr(image_file, f=None, l=None, x=None, y=None, W=None, H=None):  # noqa: E741
    """Reads QR codes from a file or files and returns a list of codes found."""
    if not isinstance(image_file, (DAFile, DAFileList)):
        return word("(Not a DAFile or DAFileList object)")
    x = int_or_none(x)
    y = int_or_none(y)
    W = int_or_none(W)
    H = int_or_none(H)
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    pdf_to_ppm = get_config("pdftoppm")
    if pdf_to_ppm is None:
        pdf_to_ppm = 'pdftoppm'
    ocr_resolution = get_config("ocr dpi")
    if ocr_resolution is None:
        ocr_resolution = '300'
    file_list = []
    temp_directory_list = []
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
                return word("(Not a readable image file)")
            path = doc.path()
            if doc.extension == 'pdf':
                directory = tempfile.mkdtemp(prefix='SavedFile')
                temp_directory_list.append(directory)
                prefix = os.path.join(directory, 'page')
                args = [pdf_to_ppm, '-r', str(ocr_resolution)]
                if f is not None:
                    args.extend(['-f', str(f)])
                if l is not None:
                    args.extend(['-l', str(l)])
                if x is not None:
                    args.extend(['-x', str(x)])
                if y is not None:
                    args.extend(['-y', str(y)])
                if W is not None:
                    args.extend(['-W', str(W)])
                if H is not None:
                    args.extend(['-H', str(H)])
                args.extend(['-png', path, prefix])
                try:
                    result = subprocess.run(args, timeout=3600, check=False).returncode
                except subprocess.TimeoutExpired:
                    result = 1
                    logmessage("read_qr: call to pdftoppm took too long")
                if result > 0:
                    return word("(Unable to extract images from PDF file)")
                file_list.extend(sorted([os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]))
                continue
            file_list.append(path)
    codes = []
    for page in file_list:
        for result in decode(Image.open(page)):
            codes.append(result.data.decode())
    return codes


def path_and_mimetype(file_ref):
    """Returns a path and the MIME type of a file"""
    if isinstance(file_ref, DAFileList) and len(file_ref.elements) > 0:
        file_ref = file_ref.elements[0]
    elif isinstance(file_ref, DAFileCollection):
        file_ref = file_ref._first_file()
    elif isinstance(file_ref, DAStaticFile):
        path = file_ref.path()
        extension, mimetype = server.get_ext_and_mimetype(file_ref.filename)  # pylint: disable=unpacking-non-sequence,unused-variable,assignment-from-none
        return path, mimetype
    if isinstance(file_ref, DAFile):
        if hasattr(file_ref, 'mimetype'):
            mime_type = file_ref.mimetype
        else:
            mime_type = None
        return file_ref.path(), mime_type
    file_info = server.file_finder(file_ref)
    return file_info.get('fullpath', None), file_info.get('mimetype', None)


class DummyObject:

    def __init__(self, *pargs, **kwargs):
        pass

SimpleTextMachineLearner = DummyObject


def set_knn_machine_learner(target):
    global SimpleTextMachineLearner
    SimpleTextMachineLearner = target

SVMMachineLearner = DummyObject


def set_svm_machine_learner(target):
    global SVMMachineLearner
    SVMMachineLearner = target

RandomForestMachineLearner = DummyObject


def set_random_forest_machine_learner(target):
    global RandomForestMachineLearner
    RandomForestMachineLearner = target

MachineLearningEntry = DummyObject


def set_machine_learning_entry(target):
    global MachineLearningEntry
    MachineLearningEntry = target


class DAModel(DAObject):
    """Applies natural language processing to user input and returns a prediction."""

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        if 'store' in kwargs:
            self.store = kwargs['store']
        else:
            self.store = '_global'
        if 'group_id' in kwargs:
            self.group_id = kwargs['group_id']
            parts = self.group_id.split(':')
            if len(parts) == 3 and parts[0].startswith('docassemble.') and re.match(r'data/sources/.*\.json', parts[1]):
                self.store = parts[0] + ':' + parts[1]
                self.group_id = parts[2]
            elif len(parts) == 2 and parts[0] == 'global':
                self.store = '_global'
                self.group_id = parts[1]
            elif len(parts) == 2 and (re.match(r'data/sources/.*\.json', parts[0]) or re.match(r'[^/]+\.json', parts[0])):
                self.store = re.sub(r':.*', ':data/sources/' + re.sub(r'^data/sources/', '', parts[0]), self.store)
                self.group_id = parts[1]
            elif len(parts) != 1:
                self.store = '_global'
        else:
            self.group_id = self.instanceName
        if self.store != '_global':
            self.group_id = self.store + ':' + self.group_id
        self.key = kwargs.get('key', None)
        self.use_for_training = kwargs.get('use_for_training', True)
        self.learner = SimpleTextMachineLearner(group_id=self.group_id)
        if 'text' in kwargs:
            self.text = kwargs['text']
            self.predict()

    def __str__(self):
        return str(self.prediction)

    def predict(self):
        if self.use_for_training:
            self.entry_id = self.learner.save_for_classification(self.text, key=self.key)
        self.predictions = self.learner.predict(self.text, probabilities=True)
        if len(self.predictions) > 0:
            self.prediction = self.predictions[0][0]
            self.probability = self.predictions[0][1]
        else:
            self.prediction = None
            self.probability = 1.0


def docx_concatenate(*pargs, **kwargs):
    """Concatenates DOCX files together and returns a DAFile representing
    the new DOCX file.

    """
    paths = []
    get_docx_paths(list(pargs), paths)
    if len(paths) == 0:
        raise DAError("docx_concatenate: no valid files to concatenate")
    docx_path = docassemble.base.file_docx.concatenate_files(paths)
    docx_file = kwargs.get('output_to', None)
    if docx_file is None:
        docx_file = DAFile()
        docx_file.set_random_instance_name()
    elif isinstance(docx_file, DAFileList):
        docx_file = docx_file.elements[0]
    if not isinstance(docx_file, DAFile):
        raise Exception("docx_concatenate: output_to must be a DAFile")
    docx_file.initialize(filename=kwargs.get('filename', 'file.docx'), reinitialize=docx_file.ok)
    docx_file.copy_into(docx_path)
    docx_file.retrieve()
    docx_file.commit()
    return docx_file


def get_docx_paths(target, paths):
    if isinstance(target, DAFileCollection) and hasattr(target, 'docx'):
        paths.append(target.docx.path())
    elif isinstance(target, (DAFileList, DAList)) or (isinstance(target, abc.Iterable) and not isinstance(target, str)):
        for the_file in target:
            get_docx_paths(the_file, paths)
    elif isinstance(target, (DAFile, DAStaticFile)):
        paths.append(target.path())
    elif isinstance(target, str) and os.path.isfile(target):
        paths.append(target)


def pdf_concatenate(*pargs, **kwargs):
    """Concatenates PDF files together and returns a DAFile representing
    the new PDF.

    """
    paths = []
    get_pdf_paths(list(pargs), paths)
    if len(paths) == 0:
        raise DAError("pdf_concatenate: no valid files to concatenate")
    pdf_path = docassemble.base.pandoc.concatenate_files(paths, pdfa=kwargs.get('pdfa', False), password=kwargs.get('password', None))
    pdf_file = kwargs.get('output_to', None)
    if pdf_file is None:
        pdf_file = DAFile()
        pdf_file.set_random_instance_name()
    elif isinstance(pdf_file, DAFileList):
        pdf_file = pdf_file.elements[0]
    if not isinstance(pdf_file, DAFile):
        raise Exception("pdf_concatenate: output_to must be a DAFile")
    pdf_file.initialize(filename=kwargs.get('filename', 'file.pdf'), reinitialize=pdf_file.ok)
    pdf_file.copy_into(pdf_path)
    pdf_file.retrieve()
    pdf_file.commit()
    return pdf_file


def get_pdf_paths(target, paths):
    if isinstance(target, DAFileCollection) and hasattr(target, 'pdf'):
        paths.append(target.pdf.path())
    elif isinstance(target, (DAFileList, DAList)) or (isinstance(target, abc.Iterable) and not isinstance(target, str)):
        for the_file in target:
            get_pdf_paths(the_file, paths)
    elif isinstance(target, (DAFile, DAStaticFile)):
        paths.append(target.path())
    elif isinstance(target, str) and os.path.isfile(target):
        paths.append(target)


def recurse_zip_params(param, root, files):
    if isinstance(param, dict):
        for key, val in param.items():
            recurse_zip_params(val, root + key + '/', files=files)
    elif isinstance(param, (list, tuple, DAFileList)):
        for val in param:
            recurse_zip_params(val, root, files=files)
    elif isinstance(param, DAFileCollection):
        the_file = getattr(param, 'pdf', None)
        if the_file is None:
            the_file = getattr(param, 'docx', None)
            if the_file is None:
                the_file = getattr(param, 'rtf', None)
            if the_file is None:
                the_file = getattr(param, 'tex', None)
        if the_file is not None:
            recurse_zip_params(the_file, root, files=files)
    elif isinstance(param, (DAStaticFile, DAFile)):
        files.append((root + param.filename, param.path()))
    else:
        file_info = server.file_finder(param)
        files.append((root + file_info['filename'], file_info['fullpath']))
    return files


def zip_file(*pargs, **kwargs):
    """Returns a ZIP file as a DAFile containing the files provided as arguments."""
    files = []
    timezone = get_default_timezone()
    recurse_zip_params(pargs, '', files)
    the_zip_file = kwargs.get('output_to', None)
    if the_zip_file is None:
        the_zip_file = DAFile()
        the_zip_file.set_random_instance_name()
    elif isinstance(the_zip_file, DAFileList):
        the_zip_file = the_zip_file.elements[0]
    if not isinstance(the_zip_file, DAFile):
        raise Exception("zip_file: output_to must be a DAFile")
    the_zip_file.initialize(filename=kwargs.get('filename', 'file.zip'), reinitialize=the_zip_file.ok)
    zf = zipfile.ZipFile(the_zip_file.path(), mode='w')
    seen = {}
    for zip_path, path in files:
        if zip_path not in seen:
            seen[zip_path] = 0
        seen[zip_path] += 1
    revised_files = []
    count = {}
    for zip_path, path in files:
        if seen[zip_path] > 1:
            if zip_path not in count:
                count[zip_path] = 0
            while True:
                count[zip_path] += 1
                suffix = ('%0' + str(len(str(seen[zip_path]))) + 'd') % count[zip_path]
                new_zip_path = re.sub(r'(\.[^\.]+)$', r'_' + suffix + r'\1', zip_path)
                if new_zip_path == zip_path:
                    new_zip_path = zip_path + '_' + suffix
                if new_zip_path not in seen:
                    seen[new_zip_path] = 1
                    break
            revised_files.append((new_zip_path, path))
        else:
            revised_files.append((zip_path, path))
    for zip_path, path in revised_files:
        info = zipfile.ZipInfo(zip_path)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        info.date_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(path)).replace(tzinfo=datetime.timezone.utc).astimezone(zoneinfo.ZoneInfo(timezone)).timetuple()
        with open(path, 'rb') as fp:
            zf.writestr(info, fp.read())
    zf.close()
    the_zip_file.retrieve()
    the_zip_file.commit()
    return the_zip_file


def validation_error(the_message, field=None):
    """Raises a validation error with a given message, optionally
    associated with a field.

    """
    raise DAValidationError(the_message, field=field)


def invalid_variable_name(varname):
    if not isinstance(varname, str):
        return True
    if re.search(r'[\n\r\(\)\{\}\*\^\#]', varname):
        return True
    varname = re.sub(r'[\.\[].*', '', varname)
    if not valid_variable_match.match(varname):
        return True
    return False

contains_volatile = re.compile(r'^(x\.|x\[|.*\[[ijklmn]\])')


def url_ask(data):
    """Like url_action, but accepts a data structure containing a sequence of variables to be sought."""
    if not isinstance(data, list):
        data = [data]
    variables = []
    for the_saveas in data:
        if isinstance(the_saveas, dict) and len(the_saveas) == 1 and ('undefine' in the_saveas or 'invalidate' in the_saveas or 'recompute' in the_saveas or 'set' in the_saveas or 'follow up' in the_saveas):
            if 'set' in the_saveas:
                if not isinstance(the_saveas['set'], list):
                    raise DAError("url_ask: the set statement must refer to a list.  " + repr(data))
                clean_list = []
                for the_dict in the_saveas['set']:
                    if not isinstance(the_dict, dict):
                        raise DAError("url_ask: a set command must refer to a list of dicts.  " + repr(data))
                    for the_var, the_val in the_dict.items():
                        if not isinstance(the_var, str):
                            raise DAError("url_ask: a set command must refer to a list of dicts with keys as variable names.  " + repr(data))
                        the_var_stripped = the_var.strip()
                        if invalid_variable_name(the_var_stripped):
                            raise DAError("url_ask: missing or invalid variable name " + repr(the_var) + " .  " + repr(data))
                        if contains_volatile.search(the_var_stripped):
                            raise DAError("url_ask cannot be used with a generic object or a variable iterator")
                        clean_list.append([the_var_stripped, the_val])
                variables.append(dict(action='_da_set', arguments=dict(variables=clean_list)))
            if 'follow up' in the_saveas:
                if not isinstance(the_saveas['follow up'], list):
                    raise DAError("url_ask: the follow up statement must refer to a list.  " + repr(data))
                for var in the_saveas['follow up']:
                    if not isinstance(var, str):
                        raise DAError("url_ask: invalid variable name in follow up " + command + ".  " + repr(data))
                    var_saveas = var.strip()
                    if invalid_variable_name(var_saveas):
                        raise DAError("url_ask: missing or invalid variable name " + repr(var_saveas) + " .  " + repr(data))
                    if contains_volatile.search(var):
                        raise DAError("url_ask cannot be used with a generic object or a variable iterator")
                    variables.append(dict(action=var, arguments={}))
            for the_command in ('undefine', 'invalidate', 'recompute'):
                if the_command not in the_saveas:
                    continue
                if not isinstance(the_saveas[the_command], list):
                    raise DAError("url_ask: the " + the_command + " statement must refer to a list.  " + repr(data))
                clean_list = []
                for undef_var in the_saveas[the_command]:
                    if not isinstance(undef_var, str):
                        raise DAError("url_ask: invalid variable name " + repr(undef_var) + " in " + the_command + ".  " + repr(data))
                    undef_saveas = undef_var.strip()
                    if invalid_variable_name(undef_saveas):
                        raise DAError("url_ask: missing or invalid variable name " + repr(undef_saveas) + " .  " + repr(data))
                    if contains_volatile.search(undef_saveas):
                        raise DAError("url_ask cannot be used with a generic object or a variable iterator")
                    clean_list.append(undef_saveas)
                if the_command == 'invalidate':
                    variables.append(dict(action='_da_invalidate', arguments=dict(variables=clean_list)))
                else:
                    variables.append(dict(action='_da_undefine', arguments=dict(variables=clean_list)))
                if the_command == 'recompute':
                    variables.append(dict(action='_da_compute', arguments=dict(variables=clean_list)))
            continue
        if isinstance(the_saveas, dict) and len(the_saveas) == 2 and 'action' in the_saveas and 'arguments' in the_saveas:
            if not isinstance(the_saveas['arguments'], dict):
                raise DAError("url_ask: an arguments directive must refer to a dictionary.  " + repr(data))
            if contains_volatile.search(the_saveas['action']):
                raise DAError("url_ask cannot be used with a generic object or a variable iterator")
            variables.append(dict(action=the_saveas['action'], arguments=the_saveas['arguments']))
            continue
        if not isinstance(the_saveas, str):
            raise DAError("url_ask: invalid variable name " + repr(the_saveas) + ".  " + repr(data))
        the_saveas = the_saveas.strip()
        if invalid_variable_name(the_saveas):
            raise DAError("url_ask: missing or invalid variable name " + repr(the_saveas) + " .  " + repr(data))
        if the_saveas not in variables:
            variables.append(the_saveas)
        if contains_volatile.search(the_saveas):
            raise DAError("url_ask cannot be used with a generic object or a variable iterator")
    return url_action('_da_force_ask', variables=variables)


def action_button_html(url, icon=None, color='success', size='sm', block=False, label='Edit', classname=None, new_window=None, id_tag=None):
    """Returns HTML for a button that visits a particular URL."""
    if not isinstance(label, str):
        label = 'Edit'
    if color not in ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark', 'link'):
        color = 'dark'
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
    if classname is None:
        classname = ''
    else:
        classname = ' ' + str(classname)
    if isinstance(icon, str):
        icon = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', icon)
        if not re.search(r'^fa[a-z] fa-', icon):
            icon = 'fas fa-' + icon
        icon = '<i class="' + icon + '"></i> '
    else:
        icon = ''
    if new_window is True:
        target = 'target="_blank" '
    elif new_window is False:
        target = 'target="_self" '
    elif new_window:
        target = 'target="' + str(new_window) + '" '
    else:
        target = ''
    if id_tag is None:
        id_tag = ''
    else:
        id_tag = ' id=' + json.dumps(id_tag)
    return '<a ' + target + 'href="' + url + '"' + id_tag + ' class="btn' + size + block + ' ' + server.button_class_prefix + color + ' btn-darevisit' + classname + '">' + icon + word(label) + '</a> '


def overlay_pdf(main_pdf, logo_pdf, first_page=None, last_page=None, logo_page=None, only=None, multi=False, output_to=None, filename=None):
    """Overlays one or more pages from a PDF file on top of the pages of another PDF file."""
    if isinstance(main_pdf, DAFileCollection):
        main_file = main_pdf.pdf.path()
    elif isinstance(main_pdf, (DAFile, DAStaticFile, DAFileList)):
        main_file = main_pdf.path()
    elif isinstance(main_pdf, str):
        main_file = main_pdf
    else:
        raise Exception("overlay_pdf: bad main filename")
    if isinstance(logo_pdf, DAFileCollection):
        logo_file = logo_pdf.pdf.path()
    elif isinstance(logo_pdf, (DAFile, DAStaticFile, DAFileList)):
        logo_file = logo_pdf.path()
    elif isinstance(logo_pdf, str):
        logo_file = logo_pdf
    else:
        raise Exception("overlay_pdf: bad logo filename")
    outfile = output_to
    if outfile is None:
        outfile = DAFile()
        outfile.set_random_instance_name()
    elif isinstance(outfile, DAFileList):
        outfile = outfile.elements[0]
    if not isinstance(outfile, DAFile):
        raise Exception("overlay_pdf: output_to must be a DAFile")
    if filename is None:
        filename = 'file.pdf'
    outfile.initialize(extension='pdf', filename=filename, reinitialize=outfile.ok)
    if multi:
        docassemble.base.pdftk.overlay_pdf_multi(main_file, logo_file, outfile.path())
    else:
        docassemble.base.pdftk.overlay_pdf(main_file, logo_file, outfile.path(), first_page=first_page, last_page=last_page, logo_page=logo_page, only=only)
    outfile.commit()
    outfile.retrieve()
    return outfile


def explain(the_explanation, category='default'):
    """Add a line to the explanations history."""
    if 'explanations' not in this_thread.internal:
        this_thread.internal['explanations'] = {}
    if category not in this_thread.internal['explanations']:
        this_thread.internal['explanations'][category] = []
    if the_explanation not in this_thread.internal['explanations'][category]:
        this_thread.internal['explanations'][category].append(the_explanation)


def clear_explanations(category='default'):
    """Erases the history of explanations."""
    if 'explanations' not in this_thread.internal:
        return
    if category == 'all':
        this_thread.internal['explanations'] = {}
    if category not in this_thread.internal['explanations']:
        return
    this_thread.internal['explanations'][category] = []


def logic_explanation(category='default'):
    """Returns the list of explanations."""
    if 'explanations' not in this_thread.internal:
        return []
    return this_thread.internal['explanations'].get(category, [])


def set_status(**kwargs):
    """Sets various settings in the interview session."""
    if 'misc' not in this_thread.internal:
        this_thread.internal['misc'] = {}
    for key, val in kwargs.items():
        this_thread.internal['misc'][key] = val


def get_status(setting):
    """Retrieves a setting of the interview session."""
    if 'misc' not in this_thread.internal:
        return None
    return this_thread.internal['misc'].get(setting, None)


def prevent_dependency_satisfaction(f):

    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (NameError, AttributeError, DAIndexError, UndefinedError):
            raise Exception("Reference to undefined variable in context where dependency satisfaction not allowed")
        # Python 3 version:
        # try:
        #     return f(*args, **kwargs)
        # except (NameError, AttributeError, DAIndexError, UndefinedError) as err:
        #     raise Exception("Reference to undefined variable in context where dependency satisfaction not allowed") from err
    return wrapper


def assemble_docx(input_file, fields=None, output_path=None, output_format='docx', return_content=False, pdf_options=None, filename=None):
    input_file = path_and_mimetype(input_file)[0]
    if not (isinstance(input_file, str) and os.path.isfile(input_file)):
        raise DAError("assemble_docx: input file did not exist")
    if output_format not in ('docx', 'pdf', 'md'):
        raise DAError("assemble_docx: invalid output format")
    if output_path is None:
        using_temporary_file = True
        output_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.' + output_format, delete=False)
        output_path = output_file.name
    else:
        using_temporary_file = False
    the_fields = copy.copy(docassemble.base.functions.get_user_dict())
    if isinstance(fields, dict):
        the_fields.update(fields)
    try:
        docx_template = DocxTemplate(input_file)
        docx_template.render_init()
        docassemble.base.functions.set_context('docx', template=docx_template)
        the_env = docassemble.base.parse.custom_jinja_env()
        the_xml = docx_template.get_xml()
        the_xml = re.sub(r'<w:p([ >])', r'\n<w:p\1', the_xml)
        the_xml = re.sub(r'({[\%\{].*?[\%\}]})', docassemble.base.parse.fix_quotes, the_xml)
        the_xml = docx_template.patch_xml(the_xml)
        the_env.parse(the_xml)
        while True:
            old_count = docassemble.base.functions.this_thread.misc.get('docx_include_count', 0)
            docx_template.render(the_fields, jinja_env=docassemble.base.parse.custom_jinja_env())
            if docassemble.base.functions.this_thread.misc.get('docx_include_count', 0) > old_count and old_count < 10:
                new_template_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".docx", delete=False)
                docx_template.save(new_template_file.name)
                docx_template = DocxTemplate(new_template_file.name)
                docx_template.render_init()
                docassemble.base.functions.this_thread.misc['docx_template'] = docx_template
            else:
                break
        subdocs = docassemble.base.functions.this_thread.misc.get('docx_subdocs', [])
        the_template_docx = docx_template.docx
        for subdoc in subdocs:
            docassemble.base.file_docx.fix_subdoc(the_template_docx, subdoc)
    except TemplateError as the_error:
        if (not hasattr(the_error, 'filename')) or the_error.filename is None:
            the_error.filename = os.path.basename(input_file)
            raise the_error
    docassemble.base.functions.reset_context()
    if output_format == 'docx':
        docx_template.save(output_path)
    elif output_format == 'pdf':
        temp_file = tempfile.NamedTemporaryFile()
        docx_template.save(temp_file.name)
        if not isinstance(pdf_options, dict):
            pdf_options = {}
        result = docassemble.base.pandoc.word_to_pdf(temp_file.name, 'docx', output_path, pdfa=pdf_options.get('pdfa', False), password=pdf_options.get('password', None), update_refs=pdf_options.get('update_refs', False), tagged=pdf_options.get('tagged', False), filename=filename)
        if not result:
            raise DAError("Error converting to PDF")
    elif output_format == 'md':
        temp_file = tempfile.NamedTemporaryFile()
        docx_template.save(temp_file.name)
        result = docassemble.base.pandoc.word_to_markdown(temp_file.name, 'docx')
        if not result:
            raise DAError("Unable to convert docx to Markdown")
        shutil.copyfile(result.name, output_path)
    if return_content:
        if output_format == 'md':
            with open(output_path, 'r', encoding='utf-8') as fp:
                output = fp.read()
        else:
            with open(output_path, 'rb') as fp:
                output = fp.read()
        if using_temporary_file:
            try:
                output_file.close()
                os.unlink(output_file.name)
            except:
                logmessage("assemble_docx: could not delete temporary file")
        return output
    if using_temporary_file:
        return output_path
    return None


def register_jinja_filter(filter_name, func):
    """Add a custom Jinja2 filter.

    This function can only be called from a module file that contains
    the line "# pre-load" so that the module will run when the server
    starts.  The register_jinja_filter() function must run when the module
    loads.  For example:

    # pre-load
    from docassemble.base.util import register_jinja_filter


    def omg_filter(text):
        return "OMG! " + text + " OMG!"

    register_jinja_filter('omg', omg_filter)
    """
    return docassemble.base.parse.register_jinja_filter(filter_name, func)


def variables_snapshot_connection():
    return server.variables_snapshot_connection()


def get_persistent_task_store(persistent):
    if persistent is True:
        base = 'session'
    else:
        base = persistent
    if base == 'session':
        encrypted = this_thread.current_info.get('encrypted', True)
        store = DAStore('store', base=base, encrypted=encrypted)
    else:
        store = DAStore('store', base=base)
    if not store.defined('tasks'):
        store.set('tasks', {})
    return store


def task_performed(task, persistent=False):
    """Returns True if the task has been performed at least once, otherwise False."""
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if task in tasks and tasks[task]:  # pylint: disable=unsubscriptable-object,unsupported-membership-test
            return True
        return False
    if task in this_thread.internal['tasks'] and this_thread.internal['tasks'][task]:
        return True
    return False


def task_not_yet_performed(task, persistent=False):
    """Returns True if the task has never been performed, otherwise False."""
    ensure_definition(task)
    if task_performed(task, persistent=persistent):
        return False
    return True


def mark_task_as_performed(task, persistent=False):
    """Increases by 1 the number of times the task has been performed."""
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if task not in tasks:  # pylint: disable=unsupported-membership-test
            tasks[task] = 0  # pylint: disable=unsupported-assignment-operation
        tasks[task] += 1  # pylint: disable=unsupported-assignment-operation
        store.set('tasks', tasks)
        return tasks[task]  # pylint: disable=unsubscriptable-object
    if task not in this_thread.internal['tasks']:
        this_thread.internal['tasks'][task] = 0
    this_thread.internal['tasks'][task] += 1
    return this_thread.internal['tasks'][task]


def times_task_performed(task, persistent=False):
    """Returns the number of times the task has been performed."""
    ensure_definition(task)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        if task not in tasks:  # pylint: disable=unsupported-membership-test
            return 0
        return tasks[task]  # pylint: disable=unsubscriptable-object
    if task not in this_thread.internal['tasks']:
        return 0
    return this_thread.internal['tasks'][task]


def set_task_counter(task, times, persistent=False):
    """Allows you to manually set the number of times the task has been performed."""
    ensure_definition(task, times)
    if persistent:
        store = get_persistent_task_store(persistent)
        tasks = store.get('tasks')
        tasks[task] = times  # pylint: disable=unsupported-assignment-operation
        store.set('tasks', tasks)
        return
    this_thread.internal['tasks'][task] = times


def stash_data(data, expire=None):
    """Stores data in an encrypted form and returns a key and a decryption secret."""
    if expire is None:
        expire = 60*60*24*90
    try:
        expire = int(expire)
        assert expire > 0
    except:
        raise DAError("Invalid expire value")
    return server.stash_data(data, expire)


def retrieve_stashed_data(stash_key, secret, delete=False, refresh=False):
    """Retrieves data stored with stash_data()."""
    if refresh and not (isinstance(refresh, int) and refresh > 0):
        refresh = 60*60*24*90
    return server.retrieve_stashed_data(stash_key, secret, delete=delete, refresh=refresh)


class DABreadCrumbs(DAObject):

    def get_crumbs(self):
        """Returns a list of breadcrumb names of the "parent" questions, followed by the current question."""
        return docassemble.base.functions.get_action_stack()

    def show(self):
        """Displays the breadcrumbs."""
        crumbs = self.get_crumbs()
        if len(crumbs) < 2:
            return ''
        last_indexno = len(crumbs) - 1
        return self.container(self.inner(item['breadcrumb'], indexno == last_indexno) for indexno, item in enumerate(crumbs))

    def container(self, items):
        """Returns the HTML of the container element. This is called from .show()."""
        return '<nav class="da-breadcrumb mt-2" aria-label="' + word('breadcrumb') + '"><ol class="breadcrumb">' + ''.join(items) + '</ol></nav>\n'

    def inner(self, label, active):
        """Returns the HTML for an individual breadcrumb. This is called from .show()."""
        if active:
            return '<li class="da-breadcrumb-item breadcrumb-item">' + label + '</li>'
        return '<li class="da-breadcrumb-item breadcrumb-item active" aria-current="page">' + label + '</li>'


def safeid(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())


class DAOAuth(DAObject):
    """A base class for performing OAuth2 authorization in an interview"""

    def init(self, *pargs, **kwargs):
        if 'url_args' not in kwargs:
            raise Exception("DAOAuth: you must pass the url_args as a keyword parameter")
        self.url_args = kwargs['url_args']
        del kwargs['url_args']
        super().init(*pargs, **kwargs)

    def _get_flow(self):
        app_credentials = get_config('oauth', {}).get(self.appname, {})
        client_id = app_credentials.get('id', None)
        client_secret = app_credentials.get('secret', None)
        if client_id is None or client_secret is None:
            raise Exception('The application ' + self.appname + " is not configured in the Configuration")
        flow = oauth2client.client.OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope=self.scope,
            redirect_uri=re.sub(r'\?.*', '', interview_url()),
            auth_uri=self.auth_uri,
            token_uri=self.token_uri,
            access_type='offline',
            prompt='consent')
        return flow

    def _setup(self):
        if hasattr(self, 'use_random_unique_id') and self.use_random_unique_id and not hasattr(self, 'unique_id'):
            self.unique_id = self._get_random_unique_id()
        if not hasattr(self, 'expires'):
            if hasattr(self, 'unique_id'):
                self.expires = 86400
            else:
                self.expires = 15724800
        try:
            if not isinstance(self.expires, int):
                self.expires = int(self.expires)
            assert self.expires > 0
        except:
            self.expires = None

    def _get_redis_key(self):
        if hasattr(self, 'unique_id'):
            return 'da:' + self.appname + ':status:uniqueid:' + str(self.unique_id)
        return 'da:' + self.appname + ':status:user:' + user_info().email

    def _get_redis_cred_storage(self):
        if hasattr(self, 'unique_id'):
            key = 'da:' + self.appname + ':uniqueid:' + str(self.unique_id)
            lock = 'da:' + self.appname + ':lock:uniqueid:' + str(self.unique_id)
        else:
            key = 'da:' + self.appname + ':user:' + user_info().email
            lock = 'da:' + self.appname + ':lock:user:' + user_info().email
        return RedisCredStorage(key, lock, self.expires)

    def _get_random_unique_id(self):
        r = DARedis()
        tries = 10
        while tries > 0:
            key = random_alphanumeric(32)
            if r.setnx('da:' + self.appname + ':status:uniqueid:' + key, 'None'):
                r.expire('da:' + self.appname + ':status:uniqueid:' + key, 300)
                return key
            tries -= 1
        raise Exception("DAOAuth: unable to set a random unique id")

    def get_credentials(self):
        """Returns the stored credentials."""
        self._setup()
        r = DARedis()
        r_key = self._get_redis_key()
        stored_state = r.get(r_key)
        if stored_state is not None and stored_state.decode() == 'None':
            stored_state = None
        if stored_state is not None:
            if 'code' in self.url_args and 'state' in self.url_args:
                r.delete(r_key)
                if self.url_args['state'] != stored_state.decode():
                    raise Exception("State did not match.  " + repr(self.url_args['state']) + " vs " + repr(stored_state.decode()) + " where r_key is " + repr(r_key))
                flow = self._get_flow()
                credentials = flow.step2_exchange(self.url_args['code'])
                storage = self._get_redis_cred_storage()
                storage.put(credentials)
                del self.url_args['code']
                del self.url_args['state']
            else:
                message("Please wait.", "You are in the process of authenticating.", dead_end=True)
        storage = self._get_redis_cred_storage()
        credentials = storage.get()
        if not credentials or credentials.invalid:
            state_string = safeid(user_info().filename + '^' + random_string(8))
            pipe = r.pipeline()
            pipe.set(r_key, state_string)
            pipe.expire(r_key, 300)
            pipe.execute()
            flow = self._get_flow()
            uri = flow.step1_get_authorize_url(state=state_string)
            if 'state' in self.url_args:
                del self.url_args['state']
            if 'code' in self.url_args:
                del self.url_args['code']
            response(url=uri)
        return credentials

    def delete_credentials(self):
        """Deletes the stored credentials."""
        self._setup()
        r = DARedis()
        r.delete(self._get_redis_key())
        storage = self._get_redis_cred_storage()
        storage.locked_delete()

    def get_http(self):
        """Returns an http object that can be used to communicate with the OAuth-enabled API."""
        return self.get_credentials().authorize(httplib2.Http())

    def authorize(self, web):
        """Adds the appropriate headers to a DAWeb object"""
        headers = {}
        self.get_credentials().apply(headers)
        if hasattr(web, 'headers'):
            web.headers.update(headers)
        else:
            web.headers = headers

    def ensure_authorized(self):
        """If the credentials are not valid, starts the authorization process."""
        self.get_http()

    def active(self):
        """Returns True if user has stored credentials, whether they are valid or not.  Otherwise returns False."""
        self._setup()
        storage = self._get_redis_cred_storage()
        credentials = storage.get()
        if not credentials:
            return False
        return True

    def is_authorized(self):
        """Returns True if user has stored credentials and the credentials are valid."""
        self._setup()
        storage = self._get_redis_cred_storage()
        credentials = storage.get()
        if not credentials or credentials.invalid:
            return False
        return True


class RedisCredStorage(oauth2client.client.Storage):

    def __init__(self, key, lock, expires):
        self.r = DARedis()
        self.key = key
        self.lockkey = lock
        self.expires = expires
        super().__init__()

    def acquire_lock(self):
        pipe = self.r.pipeline()
        pipe.set(self.lockkey, 1)
        pipe.expire(self.lockkey, 5)
        pipe.execute()

    def release_lock(self):
        self.r.delete(self.lockkey)

    def locked_get(self):
        json_creds = self.r.get(self.key)
        creds = None
        if json_creds is not None:
            self.r.expire(self.key, self.expires)
            json_creds = json_creds.decode()
            try:
                creds = oauth2client.client.Credentials.new_from_json(json_creds)
            except:
                log("RedisCredStorage: could not read credentials from " + str(json_creds))
        return creds

    def locked_put(self, credentials):
        if self.expires:
            pipe = self.r.pipeline()
            pipe.set(self.key, credentials.to_json())
            pipe.expire(self.key, self.expires)
            pipe.execute()
        else:
            self.r.set(self.key, credentials.to_json())

    def locked_delete(self):
        self.r.delete(self.key)


def ocr_finalize(*pargs, **kwargs):
    # logmessage("ocr_finalize started")
    if kwargs.get('pdf', False):
        target = kwargs['target']
        dafilelist = kwargs['dafilelist']
        filename = kwargs['filename']
        file_list = []
        for parg in pargs:
            if isinstance(parg, list):
                for item in parg:
                    if isinstance(item, ReturnValue):
                        if isinstance(item.value, dict):
                            if 'page' in item.value:
                                file_list.append([item.value['indexno'], int(item.value['page']), item.value['doc']._pdf_page_path(int(item.value['page']))])
                            else:
                                file_list.append([item.value['indexno'], 0, item.value['doc'].path()])
            else:
                if isinstance(parg, ReturnValue):
                    if isinstance(item.value, dict):
                        if 'page' in item.value:
                            file_list.append([parg.value['indexno'], int(parg.value['page']), parg.value['doc']._pdf_page_path(int(parg.value['page']))])
                        else:
                            file_list.append([parg.value['indexno'], 0, parg.value['doc'].path()])
        pdf_path = concatenate_files([y[2] for y in sorted(file_list, key=lambda x: x[0]*10000 + x[1])])
        target.initialize(filename=filename, extension='pdf', mimetype='application/pdf', reinitialize=True)
        shutil.copyfile(pdf_path, target.file_info['path'])
        del target.file_info
        target._make_pdf_thumbnail(1, both_formats=True)
        target.commit()
        target.retrieve()
        return (target, dafilelist)
    output = {}
    # index = 0
    for parg in pargs:
        # logmessage("ocr_finalize: index " + str(index) + " is a " + str(type(parg)))
        if isinstance(parg, list):
            for item in parg:
                # logmessage("ocr_finalize: sub item is a " + str(type(item)))
                if isinstance(item, ReturnValue) and isinstance(item.value, dict):
                    output[int(item.value['page'])] = item.value['text']
        else:
            if isinstance(parg, ReturnValue) and isinstance(parg.value, dict):
                output[int(parg.value['page'])] = parg.value['text']
        # index += 1
    # logmessage("ocr_finalize: assembling output")
    final_output = "\f".join([output[x] for x in sorted(output.keys())])
    # logmessage("ocr_finalize: final output has length " + str(len(final_output)))
    return final_output


def get_ocr_language(language):
    langs = get_available_languages()
    if language is None:
        language = get_language()
    ocr_langs = get_config("ocr languages")
    if ocr_langs is None:
        ocr_langs = {}
    if language in langs:
        lang = language
    else:
        if language in ocr_langs and ocr_langs[language] in langs:
            lang = ocr_langs[language]
        else:
            try:
                pc_lang = pycountry.languages.get(alpha_2=language)
                lang_three_letter = pc_lang.alpha_3
                if lang_three_letter in langs:
                    lang = lang_three_letter
                else:
                    if 'eng' in langs:
                        lang = 'eng'
                    else:
                        lang = langs[0]
                    raise Exception("could not get OCR language for language " + str(language) + "; using language " + str(lang))
            except Exception as the_error:
                if 'eng' in langs:
                    lang = 'eng'
                else:
                    lang = langs[0]
                raise Exception("could not get OCR language for language " + str(language) + "; using language " + str(lang) + "; error was " + str(the_error))
    return lang


def get_available_languages():
    try:
        output = subprocess.check_output(['tesseract', '--list-langs'], stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as err:
        raise Exception("get_available_languages: failed to list available languages: " + str(err))
    else:
        result = output.splitlines()
        result.pop(0)
        return result


def ocr_page_tasks(image_file, language=None, psm=6, f=None, l=None, x=None, y=None, W=None, H=None, user_code=None, user=None, pdf=False, preserve_color=False, **kwargs):  # noqa: E741 # pylint: disable=unused-argument
    # logmessage("ocr_page_tasks running")
    if isinstance(image_file, set):
        return []
    if not isinstance(image_file, (DAFile, DAFileList, list)):
        return word("(Not a DAFile, DAFileList, or list object)")
    pdf_to_ppm = get_config("pdftoppm")
    if pdf_to_ppm is None:
        pdf_to_ppm = 'pdftoppm'
    ocr_resolution = get_config("ocr dpi")
    if ocr_resolution is None:
        ocr_resolution = '300'
    langs = get_available_languages()
    if language is None:
        language = get_language()
    if language in langs:
        lang = language
    else:
        ocr_langs = get_config("ocr languages")
        if ocr_langs is None:
            ocr_langs = {}
        if language in ocr_langs and ocr_langs[language] in langs:
            lang = ocr_langs[language]
        else:
            try:
                pc_lang = pycountry.languages.get(alpha_2=language)
                lang_three_letter = pc_lang.alpha_3
                if lang_three_letter in langs:
                    lang = lang_three_letter
                else:
                    if 'eng' in langs:
                        lang = 'eng'
                    else:
                        lang = langs[0]
                    logmessage("ocr_file: could not get OCR language for language " + str(language) + "; using language " + str(lang))
            except Exception as the_error:
                if 'eng' in langs:
                    lang = 'eng'
                else:
                    lang = langs[0]
                logmessage("ocr_file: could not get OCR language for language " + str(language) + "; using language " + str(lang) + "; error was " + str(the_error))
    if isinstance(image_file, DAFile):
        image_file = [image_file]
    todo = []
    for doc in image_file:
        if hasattr(doc, 'extension'):
            if doc.extension not in ['pdf', 'png', 'jpg', 'gif', 'docx', 'doc', 'odt', 'rtf']:
                raise Exception("document with extension " + doc.extension + " is not a readable image file")
            if doc.extension == 'pdf':
                # doc.page_path(1, 'page')
                for i in range(len(Pdf.open(doc.path()).pages)):
                    if f is not None and i + 1 < f:
                        continue
                    if l is not None and i + 1 > l:
                        continue
                    todo.append(dict(doc=doc, page=i+1, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code, user=user, pdf=pdf, preserve_color=preserve_color))
            elif doc.extension in ("docx", "doc", "odt", "rtf"):
                doc_conv = pdf_concatenate(doc)
                for i in range(len(Pdf.open(doc_conv.path()).pages)):
                    if f is not None and i + 1 < f:
                        continue
                    if l is not None and i + 1 > l:
                        continue
                    todo.append(dict(doc=doc_conv, page=i+1, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code, user=user, pdf=pdf, preserve_color=preserve_color))
            else:
                todo.append(dict(doc=doc, page=None, lang=lang, ocr_resolution=ocr_resolution, psm=psm, x=x, y=y, W=W, H=H, pdf_to_ppm=pdf_to_ppm, user_code=user_code, user=user, pdf=pdf, preserve_color=preserve_color))
    # logmessage("ocr_page_tasks finished")
    return todo


def make_png_for_pdf(doc, prefix, resolution, pdf_to_ppm, page=None):
    path = doc.path()
    make_png_for_pdf_path(path, prefix, resolution, pdf_to_ppm, page=page)
    doc.commit()


def make_png_for_pdf_path(path, prefix, resolution, pdf_to_ppm, page=None):
    basefile = os.path.splitext(path)[0]
    test_path = basefile + prefix + '-in-progress'
    with open(test_path, 'a', encoding='utf-8'):
        os.utime(test_path, None)
    if page is None:
        try:
            result = subprocess.run([str(pdf_to_ppm), '-r', str(resolution), '-png', str(path), str(basefile + prefix)], timeout=3600, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
    else:
        try:
            result = subprocess.run([str(pdf_to_ppm), '-f', str(page), '-l', str(page), '-r', str(resolution), '-png', str(path), str(basefile + prefix)], timeout=3600, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 1
    if os.path.isfile(test_path):
        os.remove(test_path)
    if result > 0:
        raise Exception("Unable to extract images from PDF file")


def ocr_pdf(*pargs, target=None, filename=None, lang=None, psm=6, dafilelist=None, preserve_color=False):  # pylint: disable=unused-argument
    if preserve_color:
        the_device = 'tiff48nc'
    else:
        the_device = 'tiffgray'
    docs = []
    if not isinstance(target, DAFile):
        raise DAError("ocr_pdf: target must be a DAFile")
    for other_file in pargs:
        if isinstance(other_file, DAFileList):
            for other_file_sub in other_file.elements:
                docs.append(other_file_sub)
        elif isinstance(other_file, list):
            for other_file_sub in other_file:
                docs.append(other_file_sub)
        elif isinstance(other_file, DAFileCollection):
            if hasattr(other_file, 'pdf'):
                docs.append(other_file.pdf)
            elif hasattr(other_file, 'docx'):
                docs.append(other_file.docx)
            else:
                raise DAError('ocr_pdf: DAFileCollection object did not have pdf or docx attribute.')
        elif isinstance(other_file, DAStaticFile):
            docs.append(other_file)
        elif isinstance(other_file, (str, DAFile)):
            docs.append(other_file)
    if len(docs) == 0:
        docs.append(target)
    if psm is None:
        psm = 6
    output = []
    for doc in docs:
        if not hasattr(doc, 'extension'):
            continue
        if doc._is_pdf() and hasattr(doc, 'has_ocr') and doc.has_ocr:
            output.append(doc.path())
            continue
        if doc.extension in ['png', 'jpg', 'gif']:
            doc = pdf_concatenate(doc)
        elif doc.extension in ['docx', 'doc', 'odt', 'rtf']:
            output.append(pdf_concatenate(doc).path())
            continue
        elif not doc._is_pdf():
            logmessage("ocr_pdf: not a readable image file")
            continue
        path = doc.path()
        pdf_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
        pdf_file.close()
        if doc.extension == 'pdf':
            tiff_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", suffix=".tiff", delete=False)
            params = ['gs', '-q', '-dNOPAUSE', '-sDEVICE=' + the_device, '-r600', '-sOutputFile=' + tiff_file.name, path, '-c', 'quit']
            try:
                result = subprocess.run(params, timeout=60*60, check=False).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("ocr_pdf: call to gs took too long")
            if result != 0:
                raise Exception("ocr_pdf: failed to run gs with command " + " ".join(params))
            params = ['tesseract', tiff_file.name, pdf_file.name, '-l', str(lang), '--psm', str(psm), '--dpi', '600', 'pdf']
            try:
                result = subprocess.run(params, timeout=60*60, check=False).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("ocr_pdf: call to tesseract took too long")
            if result != 0:
                raise Exception("ocr_pdf: failed to run tesseract with command " + " ".join(params))
        else:
            params = ['tesseract', path, pdf_file.name, '-l', str(lang), '--psm', str(psm), '--dpi', '300', 'pdf']
            try:
                result = subprocess.run(params, timeout=60*60, check=False).returncode
            except subprocess.TimeoutExpired:
                result = 1
                logmessage("ocr_pdf: call to tesseract took too long")
            if result != 0:
                raise Exception("ocr_pdf: failed to run tesseract with command " + " ".join(params))
        output.append(pdf_file.name + '.pdf')
    if len(output) == 0:
        return None
    if len(output) == 1:
        the_file = tempfile.NamedTemporaryFile(prefix="datemp", mode="wb", delete=False)
        the_file.close()
        shutil.copyfile(output[0], the_file.name)
        source_file = the_file.name
    else:
        source_file = docassemble.base.pandoc.concatenate_files(output)
    if filename is None:
        filename = 'file.pdf'
    target.initialize(filename=filename, extension='pdf', mimetype='application/pdf', reinitialize=True)
    shutil.copyfile(source_file, target.file_info['path'])
    del target.file_info
    target._make_pdf_thumbnail(1, both_formats=True)
    target.commit()
    target.retrieve()
    return target


def ocr_page(indexno, doc=None, lang=None, pdf_to_ppm='pdf_to_ppm', ocr_resolution=300, psm=6, page=None, x=None, y=None, W=None, H=None, user_code=None, user=None, pdf=False, preserve_color=False):  # pylint: disable=unused-argument
    """Runs optical character recognition on an image or a page of a PDF file and returns the recognized text."""
    if page is None:
        page = 1
    if psm is None:
        psm = 6
    logmessage("ocr_page running on page " + str(page))
    the_file = None
    if not hasattr(doc, 'extension'):
        return None
    # logmessage("ocr_page running with extension " + str(doc.extension))
    if doc.extension not in ['pdf', 'png', 'jpg', 'gif']:
        raise Exception("Not a readable image file")
    # logmessage("ocr_page calling doc.path()")
    path = doc.path()
    if doc.extension == 'pdf':
        the_file = None
        if x is None and y is None and W is None and H is None:
            the_file = doc.page_path(page, 'page', wait=False)
        if the_file is None:
            output_file = tempfile.NamedTemporaryFile()
            args = [str(pdf_to_ppm), '-r', str(ocr_resolution), '-f', str(page), '-l', str(page)]
            if x is not None:
                args.extend(['-x', str(x)])
            if y is not None:
                args.extend(['-y', str(y)])
            if W is not None:
                args.extend(['-W', str(W)])
            if H is not None:
                args.extend(['-H', str(H)])
            args.extend(['-singlefile', '-png', str(path), str(output_file.name)])
            try:
                result = subprocess.run(args, timeout=120, check=False).returncode
            except subprocess.TimeoutExpired:
                result = 1
            if result > 0:
                return word("(Unable to extract images from PDF file)")
            the_file = output_file.name + '.png'
    else:
        the_file = path
    file_to_read = tempfile.NamedTemporaryFile()
    if pdf and preserve_color:
        shutil.copyfile(the_file, file_to_read.name)
    else:
        image = Image.open(the_file)
        color = ImageEnhance.Color(image)
        bw = color.enhance(0.0)
        bright = ImageEnhance.Brightness(bw)
        brightened = bright.enhance(1.5)
        contrast = ImageEnhance.Contrast(brightened)
        final_image = contrast.enhance(2.0)
        file_to_read = tempfile.TemporaryFile()
        final_image.convert('RGBA').save(file_to_read, "PNG")
    file_to_read.seek(0)
    if pdf:
        outfile = doc._pdf_page_path(page)
        params = ['tesseract', 'stdin', re.sub(r'\.pdf$', '', outfile), '-l', str(lang), '--psm', str(psm), '--dpi', str(ocr_resolution), 'pdf']
        logmessage("ocr_page: piping to command " + " ".join(params))
        try:
            text = subprocess.check_output(params, stdin=file_to_read).decode()
        except subprocess.CalledProcessError as err:
            raise Exception("ocr_page: failed to run tesseract with command " + " ".join(params) + ": " + str(err) + " " + str(err.output.decode()))
        logmessage("ocr_page finished with pdf page " + str(page))
        doc.commit()
        return dict(indexno=indexno, page=page, doc=doc)
    params = ['tesseract', 'stdin', 'stdout', '-l', str(lang), '--psm', str(psm), '--dpi', str(ocr_resolution)]
    logmessage("ocr_page: piping to command " + " ".join(params))
    try:
        text = subprocess.check_output(params, stdin=file_to_read).decode()
    except subprocess.CalledProcessError as err:
        raise Exception("ocr_page: failed to run tesseract with command " + " ".join(params) + ": " + str(err) + " " + str(err.output.decode()))
    logmessage("ocr_page finished with page " + str(page))
    return dict(indexno=indexno, page=page, text=text)


def complex_getattr(obj, attr):
    parts = attr.split('.')
    while len(parts) > 1:
        pre_attr = parts.pop(0)
        obj = getattr(obj, pre_attr)
    return getattr(obj, parts[0])


def complex_hasattr(obj, attr):
    parts = attr.split('.')
    while len(parts) > 1:
        pre_attr = parts.pop(0)
        if not hasattr(obj, pre_attr):
            return False
        obj = getattr(obj, pre_attr)
    return hasattr(obj, parts[0])


def complex_delattr(obj, attr):
    parts = attr.split('.')
    while len(parts) > 1:
        pre_attr = parts.pop(0)
        obj = getattr(obj, pre_attr)
    delattr(obj, parts[0])


def transform_json_variables(obj):
    return server.transform_json_variables(obj)
